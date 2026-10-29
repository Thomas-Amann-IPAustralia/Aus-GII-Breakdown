"""AusTender contract notices: Australian Government contracts by supplier (with ABN), value, category and agency.

Three parts. The Department of Finance's cumulative file of notices published to 30 August 2019 (from July 2007). The
OCDS API's notices by the date they were published, from 1 July 2019 (weekly windows of 100-notice pages, about three
seconds a page, fetched four at a time and cached as each finishes, so a rerun resumes). And, because that query returns
amendments only for contracts published from July 2019, every release the API holds for each contract in the bulk file
still running on its last day (its latest end date on or after 30 August 2019), asked by id: their later amendments are
nowhere else. That is 44,461 contracts, of which 10,800 were published in July and August 2019 and so come from the
other query too. And (gap B10) the same for every contract that ended in the four years before then (from September
2015): 234,313, of which a sample found 5% to 8% with amendments published later; older contracts' late amendments (1.6%
in the sample) are left out. Raw: the bulk file and the API's responses as gzipped JSON lines, one file per query (R2).
Processed: `contracts`, one row per notice (parent or amendment) with: `cn_id` (the notice's own id: the contract's,
such as CN123, or an amendment's, such as CN123-A2), `parent_cn_id`, `amendment` (0 for the contract's first notice, n
for its nth amendment), `published`, `published_batch`, `signed`, `start`, `end`, `value` (AUD), `value_jump`,
`description`, `unspsc`, `agency`, `supplier_name`, `supplier_abn`, `supplier_postcode`, `supplier_state`,
`supplier_country`, `procurement_method`, `source` (bulk or api). Where both parts hold a notice, the API's row is kept;
a release the API returned twice is kept once. `supplier_name` is blank where the ABR records the supplier's ABN as an
individual (a sole trader).

An amendment's `value` is the contract's new total, not the change (in the bulk file each amendment's value is the
parent's plus every change so far). So a contract's value is that of its latest notice (the highest `amendment`), and
summing every notice counts a contract once per amendment (about six times the true total; ADR 0011). The API gives
the amendment number in each release's `contracts[0].amendments`; releases share timestamps, so the number, not the
date, orders them.

`published` is the earliest date any part gives the notice. In the bulk file that is the notice's own date (an
amendment's `Publish Date` repeats its parent's; its own is `Applicable Publish Date`). The API dates a release when it
was released, and it re-released many notices in batches (every amendment of one 2018 contract carries 22 September
2025), so an amendment only the API holds can be dated later than it was made; the order is still its number.
`published_batch` marks those dates: the notice's first release shared its second with another notice of the same
contract.

`value_jump` flags a value at least 100 times the contract's previous notice's and of $100 million or more: most
likely keyed in the wrong units (a data-capture service whose amendments run from $0.7 million to $6.6 million, then
$9,626 million). Values are left as published; the flag lets an analysis set them aside.

Quirks of the sources: eight API releases are contracts under an amendment's id (CN123-A3), and are read as that
amendment; four notice ids appear twice in the bulk file with different values, and each is kept once, at its later
version; four bulk notices have malformed ids (CN221277-A1-A) and no parent notice, so their `amendment` is empty.
"""

from __future__ import annotations

import datetime as dt
import gzip
import json
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd
import requests

from ..core import CorpusError, Ctx, http_get, individual_abns, raw_path, read_manifest

API = "https://api.tenders.gov.au/ocds"
PACKAGE = "https://data.gov.au/data/api/3/action/package_show?id=historical-australian-government-contract-data"
BULK_NAME = "AusTender CNs published up to 30 August 2019"
BULK_FILE = "cn-parent-and-amendments-30092019.xlsx"
BULK_TO = "2019-08-30"  # the bulk file's last publish date
API_FROM = dt.date(2019, 7, 1)
RAW_PUBLISHED = "austender-api-releases.jsonl.gz"  # findByDates/contractPublished, weekly windows from API_FROM
RAW_BY_ID = "austender-api-by-id-releases.jsonl.gz"  # findById, for the bulk file's contracts running at BULK_TO
RAW_ENDED = "austender-api-by-id-ended-releases.jsonl.gz"  # findById, those that ended from ENDED_FROM to BULK_TO
ENDED_FROM = "2015-09-01"  # four years back: later amendments to older contracts are rare (gap B10, OQ3)
# Not used: findByDates/contractLastModified. Its record begins in May 2023, and each window from July 2023 pages back
# through thousands of older contracts and their releases: in two hours, four workers finished none of them.


def _get(url: str) -> dict:
    """One API answer; {} for an empty one (the API answers 400 with errorCode 100, "No Records found")."""
    try:
        return http_get(url, timeout=180).json()
    except CorpusError as e:
        if "answered 400" in str(e) and requests.get(url, timeout=180).json().get("errorCode") == 100:
            return {}
        raise


def _write(out: Path, rows: list[dict]) -> str:
    tmp = out.with_suffix(".part")
    out.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(tmp, "wt", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    tmp.replace(out)
    return str(out)


def _window(args) -> str:
    """One weekly window of notices by the date published, every page, cached."""
    cache, start, end = args
    out = cache / "api" / f"{start}.jsonl.gz"
    if out.exists():
        return str(out)
    url = f"{API}/findByDates/contractPublished/{start}T00:00:00Z/{end}T00:00:00Z"
    rows, seen = [], set()
    while url:
        d = _get(url)
        page = [r for r in d.get("releases", []) if r.get("id") not in seen]
        if not page:  # nothing new: the end, or a cursor that has started to repeat itself
            break
        seen.update(r.get("id") for r in page)
        rows += page
        url = (d.get("links") or {}).get("next")
    return _write(out, rows)


def _contracts(args) -> str:
    """Every release the API holds for each of a batch of contracts (by id), cached."""
    cache, ids = args
    out = cache / "by_id" / f"{ids[0]}.jsonl.gz"
    if out.exists():
        return str(out)
    return _write(out, [r for cn in ids for r in _get(f"{API}/findById/{cn}").get("releases", [])])


def _running(bulk: pd.DataFrame) -> list[str]:
    """The bulk file's contracts still running on its last day (latest end date on or after BULK_TO): the ones that
    can have amendments published after it."""
    end = bulk.groupby("parent_cn_id")["end"].max()
    return sorted(end[end >= BULK_TO].index)


def _ended(bulk: pd.DataFrame) -> list[str]:
    """The bulk file's contracts that ended in the four years before its last day (latest end date from ENDED_FROM,
    before BULK_TO): amendments published after it to these are in neither the bulk file nor the query by date (gap
    B10). A sample found them for 5% to 8% of these contracts and 1.6% of those that ended earlier
    (`analysis/audit/austender_amendments.py`)."""
    end = bulk.groupby("parent_cn_id")["end"].max()
    return sorted(end[(end >= ENDED_FROM) & (end < BULK_TO)].index)


def _amendment(r: dict) -> int | None:
    """0 for a contract's own release; n for an amendment release whose amendment id is `CNxxx-An`."""
    if "contractAmendment" not in (r.get("tag") or []):
        return 0
    c = (r.get("contracts") or [{}])[0]
    m = re.search(r"-A(\d+)$", ((c.get("amendments") or [{}])[-1]).get("id") or "")
    return int(m.group(1)) if m else None


def _flatten(r: dict) -> dict:
    parties = r.get("parties") or []
    sup = next((p for p in parties if "supplier" in (p.get("roles") or [])), {})
    agency = next((p for p in parties if "procuringEntity" in (p.get("roles") or [])), {})
    abn = next((i["id"] for i in sup.get("additionalIdentifiers") or [] if i.get("scheme") == "AU-ABN"), None)
    c = (r.get("contracts") or [{}])[0]
    item = (c.get("items") or [{}])[0]
    addr = sup.get("address") or {}
    period = c.get("period") or {}
    n, cid = _amendment(r), c.get("id")
    m = re.match(r"^(CN\d+)-A(\d+)$", cid or "")
    if m and n == 0:  # released as a contract under an amendment's id (CN123-A3): that amendment
        cid, n = m.group(1), int(m.group(2))
    if n is None:  # an amendment whose id has no number keeps that id, so it cannot stand in for its contract's notice
        cn_id = ((c.get("amendments") or [{}])[-1]).get("id") or f"{cid}-A"
    else:
        cn_id = f"{cid}-A{n}" if n else cid
    return {
        "cn_id": cn_id,
        "parent_cn_id": cid,
        "amendment": n,
        "released_at": r.get("date"),
        "published": (r.get("date") or "")[:10] or None,
        "signed": (c.get("dateSigned") or "")[:10] or None,
        "start": (period.get("startDate") or "")[:10] or None,
        "end": (period.get("endDate") or "")[:10] or None,
        "value": (c.get("value") or {}).get("amount"),
        "description": c.get("description"),
        "unspsc": (item.get("classification") or {}).get("id"),
        "agency": agency.get("name"),
        "supplier_name": sup.get("name"),
        "supplier_abn": re.sub(r"\D", "", abn) if abn else None,
        "supplier_postcode": addr.get("postalCode"),
        "supplier_state": addr.get("region"),
        "supplier_country": addr.get("countryName"),
        "procurement_method": (r.get("tender") or {}).get("procurementMethodDetails")
        or (r.get("tender") or {}).get("procurementMethod"),
    }


def _bulk(path) -> pd.DataFrame:
    df = pd.read_excel(path, engine="calamine", dtype=str)
    cols = {c: re.sub(r"[^a-z0-9]+", "_", c.lower()).strip("_") for c in df.columns}
    df = df.rename(columns=cols)

    def pick(*names):
        for n in names:
            if n in df:
                return df[n]
        return pd.Series([None] * len(df))

    cn_id = pick("contract_id", "cn_id", "contract_notice_id")
    suffix = cn_id.str.extract(r"-A(\d+)$", expand=False)
    is_amendment = pick("contract_notice_type").fillna("").str.lower().eq("amendment") | suffix.notna()
    out = pd.DataFrame(
        {
            "cn_id": cn_id,
            "parent_cn_id": pick("parent_contract_id").fillna(cn_id.str.replace(r"-A\d+$", "", regex=True)),
            "amendment": pd.to_numeric(suffix, errors="coerce").where(is_amendment, 0).astype("Int64"),
            # an amendment's "Publish Date" repeats its parent's; "Applicable Publish Date" is the notice's own
            "published": pick("applicable_publish_date", "publish_date", "published_date"),
            "signed": pick("contract_signed_date", "agreement_date", "date_signed"),
            "start": pick("start_date", "contract_start_date"),
            "end": pick("end_date", "contract_end_date"),
            "value": pick("value", "contract_value", "value_aud"),
            "description": pick("description", "title"),
            "unspsc": pick("unspsc_code", "category_code", "unspsc"),
            "agency": pick("agency", "agency_name"),
            "supplier_name": pick("supplier_name"),
            "supplier_abn": pick("supplier_abn", "abn"),
            "supplier_postcode": pick("supplier_postcode", "postcode"),
            "supplier_state": pick("supplier_state", "state"),
            "supplier_country": pick("supplier_country", "country"),
            "procurement_method": pick("procurement_method"),
        }
    )
    for c in ("published", "signed", "start", "end"):
        out[c] = pd.to_datetime(out[c].str[:10], errors="coerce", format="%Y-%m-%d").dt.strftime("%Y-%m-%d")
    out["supplier_abn"] = out["supplier_abn"].str.replace(r"\D", "", regex=True).replace("", None)
    # a notice id the file gives twice (four do, with different values) is kept once, at its later version
    return out.sort_values("published", kind="stable").drop_duplicates("cn_id", keep="last").reset_index(drop=True)


def _api(paths) -> pd.DataFrame:
    """Every API release (JSON lines files), flattened. A notice can come back from both queries, or more than once
    (adjacent windows, re-publication): each notice is kept once, as its latest release has it, dated by its first.
    `published_batch` marks a notice whose first release shares its second with another notice of the same contract:
    a batch re-release, so the date can be later than the notice was made."""
    rows = []
    for p in paths:
        with gzip.open(p, "rt", encoding="utf-8") as fh:
            rows += [_flatten(json.loads(line)) for line in fh]
    rows = pd.DataFrame(rows).sort_values("released_at", kind="stable")
    rows["published_batch"] = rows.groupby(["parent_cn_id", "released_at"])["cn_id"].transform("nunique").gt(1)
    first = rows.drop_duplicates("cn_id").set_index("cn_id")
    rows = rows.drop_duplicates("cn_id", keep="last")
    for c in ("published", "published_batch"):
        rows[c] = rows["cn_id"].map(first[c])
    rows["amendment"] = rows["amendment"].astype("Int64")
    return rows.drop(columns="released_at").assign(source="api")


def _combine(api: pd.DataFrame, bulk: pd.DataFrame) -> pd.DataFrame:
    """One row per notice: the API's where both parts hold it, dated by the earlier of the two (the API re-released
    notices in batches). `published_batch` stays true only where the date is still the API's batch release."""
    both = pd.concat([api, bulk[~bulk.cn_id.isin(api.cn_id)]], ignore_index=True)
    both["published"] = both.cn_id.map(pd.concat([api, bulk]).groupby("cn_id")["published"].min())
    own = both.cn_id.map(bulk.groupby("cn_id")["published"].min())
    both["published_batch"] = both["published_batch"].eq(True) & own.ne(both["published"])
    both["value"] = pd.to_numeric(both["value"].astype(str).str.replace(r"[,$]", "", regex=True), errors="coerce")
    # a value at least 100 times its contract's previous notice's, and $100 million or more: most likely keyed in the
    # wrong units at source. Flagged, not changed
    order = both.sort_values(["parent_cn_id", "amendment", "published"], na_position="first")
    prev = order.groupby("parent_cn_id")["value"].shift()
    both["value_jump"] = (prev > 0) & (order["value"] >= 100 * prev) & (order["value"] >= 1e8)
    cols = [c for c in both.columns if c not in ("published_batch", "value_jump")]
    cols.insert(cols.index("published") + 1, "published_batch")
    cols.insert(cols.index("value") + 1, "value_jump")
    return both[cols].sort_values(["published", "cn_id"], na_position="last").reset_index(drop=True)


def _build(ctx: Ctx, api: pd.DataFrame, bulk: pd.DataFrame) -> None:
    both = _combine(api, bulk)
    both.loc[both.supplier_abn.isin(individual_abns()), "supplier_name"] = None  # sole traders' names stay out
    ctx.table(both, "contracts", describe="Contract notices 2007 onward, one row per notice, with supplier ABN")


def _keep(ctx: Ctx, files: list[str], name: str, url: str) -> Path:
    """The cached answers as one raw file (byte for byte the same for the same answers), kept in R2."""
    raw = ctx.cache / name
    with open(raw, "wb") as f, gzip.GzipFile(fileobj=f, mode="wb", mtime=0, filename="") as out:
        for w in files:
            with open(w, "rb") as fh:
                out.write(gzip.decompress(fh.read()))
    return ctx.keep_raw(raw, keep="r2", url=url)


def _harvest(ctx: Ctx, until: dt.date | None = None) -> Path:
    """Every weekly window of notices by the date published, from July 2019 to `until` (today)."""
    today = until or dt.date.today()
    starts, d = [], API_FROM
    while d < today:
        starts.append((ctx.cache, d.isoformat(), min(d + dt.timedelta(days=7), today).isoformat()))
        d += dt.timedelta(days=7)
    with ThreadPoolExecutor(max_workers=4) as ex:
        files = list(ex.map(_window, starts))
    ctx.log(f"API by date published: {len(files)} weekly windows")
    return _keep(ctx, files, RAW_PUBLISHED, f"{API}/findByDates/contractPublished")


def _harvest_by_id(ctx: Ctx, ids: list[str], batch: int = 500, name: str = RAW_BY_ID) -> Path:
    """Every release of each contract in `ids`, asked by id, in cached batches (eight at a time)."""
    batches = [(ctx.cache, ids[i : i + batch]) for i in range(0, len(ids), batch)]
    with ThreadPoolExecutor(max_workers=8) as ex:
        files = list(ex.map(_contracts, batches))
    ctx.log(f"API by id: {len(ids)} contracts")
    return _keep(ctx, files, name, f"{API}/findById")


def run(ctx: Ctx) -> None:
    res = http_get(PACKAGE).json()["result"]["resources"]
    bulk_url = next((r["url"] for r in res if r.get("name", "").strip() == BULK_NAME), None)
    if not bulk_url:
        raise CorpusError(f"austender: no resource named '{BULK_NAME}' on data.gov.au")
    bulk = _bulk(ctx.fetch(bulk_url, BULK_FILE, keep="r2")).assign(source="bulk")
    by_id = [_harvest_by_id(ctx, _running(bulk)), _harvest_by_id(ctx, _ended(bulk), name=RAW_ENDED)]
    _build(ctx, _api([_harvest(ctx), *by_id]), bulk)


def reprocess(ctx: Ctx, tables: list[str] | None = None) -> None:
    """`contracts` again from the stored raw files (the API's releases from both queries and the bulk file, in R2)."""
    files = read_manifest()["sources"]["austender"]["files"]
    api = _api([raw_path("austender", n) for n in (RAW_PUBLISHED, RAW_BY_ID, RAW_ENDED) if f"raw/{n}" in files])
    bulk = _bulk(raw_path("austender", BULK_FILE)).assign(source="bulk")
    _build(ctx, api, bulk)
