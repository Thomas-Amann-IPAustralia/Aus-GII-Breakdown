"""Every provisional patent application in IP Australia's register, with its inventors, read through the patent API
(`corpus.ipa_api`; ADR 0029).

Provisional applications are never published, so Google Patents (the corpus's other source of inventors) holds almost
none; the register names their inventors from about 2000 (ADR 0028, V15). The patent search cannot list patents, so
each is fetched by number:

- every provisional IP RAPID holds;
- numbers past each of the last two years' highest, until 300 in a row are not found (filed after the release);
- a probe of 300 numbers missing inside IP RAPID's yearly sequences (they run YYYY90NNNN): on 27 October 2026 a probe
  of 360 found none in the register, so the gaps are numbers never used, and only a probe is kept, as evidence.

Production's patent API fails about half its calls at random, but those calls are not counted toward the limit
(ADR 0028), so with 24 threads the run takes about 540 records a minute: about eight hours for 264,000. Batches are
kept in the cache, so an interrupted run carries on, on any later day; `IPA_BUDGET_MINUTES` stops it cleanly.

Processed:
- `provisionals` (no names): one row per number asked: whether the register has it, its status and status events,
  dates, title, first IPC mark, numbers of applicants and representatives, its inventors and their expected women and
  men, and whether IP RAPID has it (`in_iprapid`).
- `inventors` (R2, names as the register gives them): one row per provisional and inventor, with the given name used
  and the estimated chance that the inventor is a woman, by the World Gender-Name Dictionary as
  `google_patents_inventors` does (ADR 0022). The register gives no inventor's country, so the first applicant's
  country in IP RAPID stands in for it (`country_basis` = `applicant`); with none, the name alone decides.
- `applicants` (R2, names): each provisional's applicants as the register names them.
- `gap_probe`: the probed numbers and whether the register has them.
"""

from __future__ import annotations

import datetime as dt
import random

import duckdb
import pandas as pd

from .. import ipa_api
from ..core import CorpusError, Ctx, path
from .google_patents_inventors import estimate_sql
from .ipa_register import Budget, _concat, by_number

PROBE_MISSES = 300  # numbers in a row not found before a year's sequence is taken to have ended
GAP_PROBE = 300
SEED = 2026


def numbers(ctx: Ctx, client) -> tuple[list[str], pd.DataFrame]:
    """IP RAPID's provisionals and the numbers past the last two years' highest; and the probe of the gaps."""
    have = sorted(
        duckdb.connect()
        .execute(f"""SELECT application_number FROM '{path("iprapid", "patent_rights")}'
                     WHERE ip_right_sub_type = 'provisional'""")
        .df()
        .application_number
    )
    seq = pd.Series([int(n) for n in have if n.isdigit()])
    series = seq // 10_000  # YYYY90 or YYYY95: one year's sequence
    gaps = []
    for _, s in seq.groupby(series):
        gaps += sorted(set(range(s.min(), s.max() + 1)) - set(s))
    probe = random.Random(SEED).sample(gaps, min(GAP_PROBE, len(gaps)))
    got = dict(client.get_many("patent", [str(n) for n in probe], workers=24))
    if any(ipa_api.failed(r) for r in got.values()):
        raise CorpusError("ipa_provisionals: the gap probe had calls the register would not answer; run it again")
    probe = pd.DataFrame({"application_number": list(got), "in_register": [r is not None for r in got.values()]})
    ctx.log(
        f"provisionals: {len(have):,} in IP RAPID; {len(gaps):,} numbers missing inside their years' sequences, "
        f"of which {probe.in_register.sum()} of {len(probe)} probed are in the register"
    )
    beyond = []
    this = dt.date.today().year
    for y in (this - 1, this):
        top = seq[series == y * 100 + 90].max()
        n, misses = int(top) + 1, 0
        while misses < PROBE_MISSES:
            batch = [str(n + k) for k in range(50)]
            got = dict(client.get_many("patent", batch, workers=24))
            for k in batch:
                if got[k] is None or ipa_api.failed(got[k]):
                    misses += 1
                else:
                    misses = 0
                    beyond.append(k)
            n += 50
        ctx.log(f"provisionals: {sum(b.startswith(str(y)) for b in beyond):,} past IP RAPID's last number for {y}")
    return have + beyond, probe


def run(ctx: Ctx) -> None:
    client = ipa_api.Client("prod")
    budget = Budget()
    ctx.note(f"ipa_provisionals: production register as at {dt.date.today()}")
    plan, probe_file = ctx.cache / "provisional_numbers.parquet", ctx.cache / "gap_probe.parquet"
    if not plan.exists():
        nums, probe = numbers(ctx, client)
        plan.parent.mkdir(parents=True, exist_ok=True)
        probe.to_parquet(probe_file)
        pd.DataFrame({"application_number": nums}).to_parquet(plan)
    nums = pd.read_parquet(plan).application_number.tolist()
    d = by_number(ctx, client, "patent", nums, "provisional", budget, 24)
    if d is None:
        raise CorpusError("ipa_provisionals: stopped before every record was in (IPA_BUDGET_MINUTES); run it again")

    files = sorted(d.glob("*.parquet"))
    con = duckdb.connect()
    p = _concat([f for f in files if not f.name.endswith((".owners.parquet", ".inventors.parquet"))]).to_pandas()
    inv = _concat([f for f in files if f.name.endswith(".inventors.parquet")]).to_pandas()
    own = _concat([f for f in files if f.name.endswith(".owners.parquet")])
    country = con.execute(f"""
        SELECT application_number, upper(applicant_country) AS country_code
        FROM '{path("iprapid", "patent_rights")}' WHERE ip_right_sub_type = 'provisional'""").df()
    con.register("inv0", inv.merge(country, on="application_number", how="left"))
    con.execute(
        "CREATE TABLE inv1 AS SELECT *, CASE WHEN country_code IS NOT NULL THEN 'applicant' END AS "
        "country_basis FROM inv0"
    )
    # the register writes inventors 'Surname, Given': the given name follows the comma (position 1 is the fallback)
    est = con.execute(
        estimate_sql("inv1", f"'{path('wgnd', 'name_gender_code')}'", f"'{path('wgnd', 'name_gender')}'", 1)
        + " ORDER BY application_number, seq"
    ).df()
    ctx.table(est, "inventors", keep="r2", describe="Provisionals' inventors as the register names them, with gender")
    ctx.table(own, "applicants", keep="r2", describe="Provisionals' applicants as the register names them")
    per = (
        est.groupby("application_number")
        .agg(
            inventors=("seq", "size"),
            women_expected=("p_female", "sum"),
            men_expected=("p_female", lambda s: (1 - s).sum()),
            gender_unknown=("p_female", lambda s: s.isna().sum()),
        )
        .reset_index()
    )
    keep = [
        c
        for c in p.columns
        if c not in ("error", "reasons", "inventor_count")
        and not c.startswith("owner_")
        and c not in ("any_owner_abn", "any_owner_in_australia")
    ]
    p = p[keep].merge(per, on="application_number", how="left")
    p["inventors"] = p["inventors"].fillna(0).astype(int)
    p["gender_unknown"] = p["gender_unknown"].fillna(0).astype(int)
    p["in_iprapid"] = p.application_number.isin(set(country.application_number))
    if p.found.isna().any():
        raise CorpusError(f"ipa_provisionals: {p.found.isna().sum():,} records the register would not serve")
    ctx.table(
        p.sort_values("application_number"),
        "provisionals",
        describe="Every provisional the register holds, with its inventors' count and expected gender",
    )
    ctx.table(
        pd.read_parquet(probe_file),
        "gap_probe",
        describe="Numbers missing inside IP RAPID's provisional sequences, probed: whether the register has them",
    )
    ctx.note(f"ipa_provisionals: {client.calls:,} calls, {client.retries:,} retried")
    ctx.save()
