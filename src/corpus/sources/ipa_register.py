"""IP Australia's register, whole: every trade mark and design record, read through the register APIs
(`corpus.ipa_api`; ADR 0029).

`ipa_api` checked IP RAPID against the register from a sample and a few targets (ADR 0028). This source takes every
trade mark and design, so the gaps the register fills (owners' ABNs and ACNs, design owners' countries, the
register's expedite events) are filled for every year alike. Provisional patent applications, with their inventors,
are `ipa_provisionals`.

Every record a date search finds (by lodgement and filing date) is taken a page of 100 at a time, the range split
until each part is under the 10,000-record cap; and, by number, the records the searches cannot find (IP RAPID's
numbers with no date in the register). About 2.6 million records; under three hours.

Raw responses are not kept (2.3 million trade mark records are about 25 GB): each slice is flattened as it arrives
(`ipa_api.flat`, the same fields the audit uses) and kept in the cache, so an interrupted run carries on where it
stopped, on any later day, and `IPA_BUDGET_MINUTES` stops a run cleanly after that long (for runs in parts).

Processed:
- `trade_marks`, `designs` (no names): one row per record: status, dates, classes, the first current owner's ABN, ACN,
  country, state and postcode, any owner's ABN, and (trade marks) the register's expedite events.
- `owners` (R2, names as the register gives them): every current owner of every trade mark and design.
"""

from __future__ import annotations

import datetime as dt
import os
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import duckdb
import pandas as pd

from .. import ipa_api
from ..core import CorpusError, Ctx, path
from .ipa_api import flat, owners

SEARCH = {"trade_mark": ("LODGEMENT_DATE", "trademarks", "number"), "design": ("FILED", "designs", "designNumber")}
FIRST = dt.date(1900, 1, 1)
CAP = 10_000


class Budget:
    """Stops new work after `IPA_BUDGET_MINUTES` (unset: no limit)."""

    def __init__(self):
        m = os.environ.get("IPA_BUDGET_MINUTES")
        self.until = time.monotonic() + float(m) * 60 if m else None

    def over(self) -> bool:
        return self.until is not None and time.monotonic() > self.until


def _write(rows: list[dict], own: list[dict], dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(".tmp")
    pd.DataFrame(rows).to_parquet(tmp)
    pd.DataFrame(own).to_parquet(tmp.with_suffix(".own.tmp"))
    tmp.with_suffix(".own.tmp").replace(dest.with_name(dest.stem + ".owners.parquet"))
    tmp.replace(dest)  # last: a slice counts as done only when its rows file is in place


# -- trade marks and designs, by date ---------------------------------------------------------------------------------


def _count(client, right, a, b) -> int:
    body = {"rows": [{"query": {"date": {"type": SEARCH[right][0], "from": str(a), "to": str(b)}}}]}
    return client.page(right, body, 0, 1)["count"]


def slices(client, right, a: dt.date, b: dt.date) -> list[tuple[dt.date, dt.date, int]]:
    """Date ranges from `a` to `b`, each with at most CAP records, by halving."""
    n = _count(client, right, a, b)
    if n == 0:
        return []
    if n <= CAP:
        return [(a, b, n)]
    if a == b:
        raise CorpusError(f"ipa_register: {n} {right}s dated {a}, over the {CAP:,} cap of one search")
    mid = a + (b - a) // 2
    return slices(client, right, a, mid) + slices(client, right, mid + dt.timedelta(days=1), b)


def harvest_slice(client, right, a, b, n, dest: Path) -> int:
    date_type, key, num = SEARCH[right]
    body = {"rows": [{"query": {"date": {"type": date_type, "from": str(a), "to": str(b)}}}]}
    rows, own, seen = [], [], set()
    with ThreadPoolExecutor(3) as pool:
        pages = pool.map(lambda p: client.page(right, body, p, 100), range(-(-n // 100)))
        for out in pages:
            for rec in out.get(key) or []:
                number = str(rec[num])
                if number in seen:
                    continue
                seen.add(number)
                rows.append(flat(right, number, rec))
                own += owners(right, number, rec)
    if len(seen) < n:
        raise CorpusError(f"ipa_register: {right}s {a} to {b}: {len(seen):,} of {n:,} records came back")
    _write(rows, own, dest)
    return len(rows)


def by_date(ctx: Ctx, client, right: str, budget: Budget) -> bool:
    """Every record of `right` a date search finds, slice by slice into the cache. True once all are in."""
    d = ctx.cache / "register" / right
    plan = d / "slices.parquet"
    if plan.exists():
        todo = pd.read_parquet(plan)
    else:
        years = range(FIRST.year, dt.date.today().year + 1)
        with ThreadPoolExecutor(3) as pool:
            parts = pool.map(lambda y: slices(client, right, dt.date(y, 1, 1), dt.date(y, 12, 31)), years)
            todo = pd.DataFrame([s for p in parts for s in p], columns=["a", "b", "n"])
        d.mkdir(parents=True, exist_ok=True)
        todo.to_parquet(plan)
    ctx.log(f"{right}: {len(todo):,} slices, {todo.n.sum():,} records")

    def one(s):
        dest = d / f"{s.a}_{s.b}.parquet"
        if dest.exists() or budget.over():
            return 0
        return harvest_slice(client, right, s.a, s.b, s.n, dest)

    done = 0
    with ThreadPoolExecutor(2) as pool:
        for i, k in enumerate(pool.map(one, todo.itertuples())):
            done += k
            if i % 100 == 0:
                ctx.log(f"{right}: slice {i:,} of {len(todo):,}; {done:,} records this run")
    return all((d / f"{s.a}_{s.b}.parquet").exists() for s in todo.itertuples())


# -- records by number -------------------------------------------------------------------------------------------------


def by_number(ctx: Ctx, client, right: str, numbers: list[str], name: str, budget: Budget, workers: int) -> Path | None:
    """Records fetched one by one, a batch at a time into the cache; the batches' paths, once all are in."""
    d = ctx.cache / "register" / name
    d.mkdir(parents=True, exist_ok=True)
    batch, complete = 2_000, True
    for i in range(0, len(numbers), batch):
        dest = d / f"{i:08d}.parquet"
        if dest.exists():
            continue
        if budget.over():
            return None
        got = list(client.get_many(right, numbers[i : i + batch], workers=workers))
        if any(ipa_api.failed(r) for _, r in got):  # a batch with failures is fetched again next run
            ctx.log(f"{name}: batch {i:,} had records the register would not serve; skipped for now")
            complete = False
            continue
        rows = [flat(right, n, r) | _extra(right, r) for n, r in got]
        own = [o for n, r in got for o in owners(right, n, r)]
        inv = [
            {"application_number": n, "seq": k, "name": x.get("legalEntityName")}
            for n, r in got
            if r and right == "patent"
            for k, x in enumerate(r.get("inventors") or [])
        ]
        _write(rows, own, dest)
        if right == "patent":
            pd.DataFrame(inv, columns=["application_number", "seq", "name"]).to_parquet(
                dest.with_name(dest.stem + ".inventors.parquet")
            )
        ctx.log(f"{name}: {min(i + batch, len(numbers)):,} of {len(numbers):,} ({client.retries:,} retries so far)")
    return d if complete else None


def _extra(right: str, rec: dict | None) -> dict:
    """Fields the audit's flattening leaves out that the full register keeps: a patent's title and status events."""
    if right != "patent" or not rec or ipa_api.failed(rec):
        return {}
    b = rec.get("bibliographicData") or {}
    events = rec.get("ipRightStatusEvent") or []
    return {
        "title": next((t.get("title") for t in b.get("inventionTitle") or []), None),
        "status_events": ";".join(f"{e.get('ipRightStatusCode')}:{e.get('ipRightStatusDate')}" for e in events) or None,
    }


# -- assembly ----------------------------------------------------------------------------------------------------------


def _concat(files: list[Path]):
    """The cached parts as one Arrow table (columns matched by name: a part may lack an all-empty column)."""
    if not files:
        raise CorpusError("ipa_register: nothing in the cache to assemble")
    names = ", ".join(f"'{f}'" for f in files)
    return duckdb.connect().execute(f"SELECT * FROM read_parquet([{names}], union_by_name = true)").arrow()


def run(ctx: Ctx) -> None:
    client = ipa_api.Client("prod")
    budget = Budget()
    ctx.note(f"ipa_register: production register as at {dt.date.today()}")
    nums = pd.read_parquet(path("ipa_api", "numbers"))
    app = (
        duckdb.connect()
        .execute(f"""
        SELECT ip_right_type, application_number FROM '{path("iprapid", "application")}'
        WHERE ip_right_type IN ('trade_mark', 'design')""")
        .df()
    )
    undated = app.merge(nums, how="left", indicator=True).query("_merge == 'left_only'")

    # the two APIs have their own limits, so the two parts run side by side
    with ThreadPoolExecutor(2) as pool:
        jobs = {
            right: pool.submit(
                lambda r=right: (
                    by_date(ctx, client, r, budget)
                    and by_number(
                        ctx,
                        client,
                        r,
                        sorted(undated[undated.ip_right_type == r].application_number),
                        f"{r}_undated",
                        budget,
                        8,
                    )
                )
            )
            for right in SEARCH
        }
        done = {k: f.result() for k, f in jobs.items()}
    if not all(done.values()):
        raise CorpusError("ipa_register: stopped before every record was in (IPA_BUDGET_MINUTES); run it again")

    reg = ctx.cache / "register"
    con = duckdb.connect()
    for right, name in (("trade_mark", "trade_marks"), ("design", "designs")):
        files = sorted((reg / right).glob("*_*.parquet")) + sorted((reg / f"{right}_undated").glob("*.parquet"))
        rows = [f for f in files if not f.name.endswith((".owners.parquet", ".inventors.parquet"))]
        con.register("t", _concat(rows))
        cols = [c for c in con.execute("DESCRIBE t").df().column_name if c not in ("error", "reasons")]
        df = con.execute(
            f"SELECT {', '.join(cols)} FROM t QUALIFY row_number() OVER (PARTITION BY application_number "
            "ORDER BY found DESC NULLS LAST) = 1 ORDER BY application_number"
        ).arrow()
        missing = con.execute("SELECT count(*) FROM t WHERE found IS NULL").fetchone()[0]
        if missing:
            raise CorpusError(f"ipa_register: {missing:,} {right} records the register would not serve")
        ctx.table(df, name, describe=f"Every {right} in the register")
    own = []
    for sub in ("trade_mark", "design", "trade_mark_undated", "design_undated"):
        own += sorted((reg / sub).glob("*.owners.parquet"))
    con.register("o", _concat(own))
    ctx.table(
        con.execute("SELECT DISTINCT * FROM o ORDER BY ip_right_type, application_number, seq").arrow(),
        "owners",
        keep="r2",
        describe="Current owners of every trade mark and design, named",
    )

    ctx.note(f"ipa_register: {client.calls:,} calls, {client.retries:,} retried")
    ctx.save()
