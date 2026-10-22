"""AusTender contract notices: Australian Government contracts by supplier (with ABN), value, category and agency.

Two parts, because the OCDS API pages 100 notices at a time (about three seconds a page): the Department of Finance's
cumulative file of notices published to 30 August 2019 (from July 2007), and the API for notices published from
1 July 2019 (weekly windows, fetched four at a time and cached as each finishes, so a rerun resumes). Raw: the bulk
file and the API's responses as gzipped JSON lines (R2). Processed: `contracts`, one row per notice (parent or
amendment) with: `cn_id`, `published`, `signed`, `start`, `end`, `value` (AUD), `description`, `unspsc`, `agency`,
`supplier_name`, `supplier_abn`, `supplier_postcode`, `supplier_state`, `supplier_country`, `procurement_method`,
`source` (bulk or api). Where both parts hold a notice, the API's row is kept. `supplier_name` is blank where
the ABR records the supplier's ABN as an individual (a sole trader).
"""

from __future__ import annotations

import datetime as dt
import gzip
import json
import re
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import requests

from ..core import CorpusError, Ctx, http_get, individual_abns

API = "https://api.tenders.gov.au/ocds/findByDates/contractPublished"
PACKAGE = "https://data.gov.au/data/api/3/action/package_show?id=historical-australian-government-contract-data"
BULK_NAME = "AusTender CNs published up to 30 August 2019"
API_FROM = dt.date(2019, 7, 1)


def _window(args) -> str:
    ctx_cache, start, end = args
    out = ctx_cache / "api" / f"{start}.jsonl.gz"
    if out.exists():
        return str(out)
    url = f"{API}/{start}T00:00:00Z/{end}T00:00:00Z"
    rows = []
    while url:
        try:
            d = http_get(url, timeout=180).json()
        except CorpusError as e:  # an empty window answers 400 with errorCode 100, "No Records found"
            if "answered 400" in str(e) and requests.get(url, timeout=180).json().get("errorCode") == 100:
                break
            raise
        rows += d.get("releases", [])
        nxt = (d.get("links") or {}).get("next")
        url = nxt if nxt and d.get("releases") else None
    tmp = out.with_suffix(".part")
    out.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(tmp, "wt", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    tmp.replace(out)
    return str(out)


def _flatten(r: dict) -> dict:
    parties = r.get("parties") or []
    sup = next((p for p in parties if "supplier" in (p.get("roles") or [])), {})
    agency = next((p for p in parties if "procuringEntity" in (p.get("roles") or [])), {})
    abn = next((i["id"] for i in sup.get("additionalIdentifiers") or [] if i.get("scheme") == "AU-ABN"), None)
    c = (r.get("contracts") or [{}])[0]
    item = (c.get("items") or [{}])[0]
    addr = sup.get("address") or {}
    period = c.get("period") or {}
    return {
        "cn_id": c.get("id"),
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

    out = pd.DataFrame(
        {
            "cn_id": pick("cn_id", "contract_notice_id", "cnid"),
            "published": pick("publish_date", "published_date"),
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
        out[c] = pd.to_datetime(out[c], errors="coerce", dayfirst=True).dt.strftime("%Y-%m-%d")
    out["supplier_abn"] = out["supplier_abn"].str.replace(r"\D", "", regex=True).replace("", None)
    return out


def run(ctx: Ctx) -> None:
    today = dt.date.today()
    starts = []
    d = API_FROM
    while d < today:
        starts.append((ctx.cache, d.isoformat(), min(d + dt.timedelta(days=7), today).isoformat()))
        d += dt.timedelta(days=7)
    with ThreadPoolExecutor(max_workers=4) as ex:
        files = list(ex.map(_window, starts))
    ctx.log(f"API: {len(files)} weekly windows")
    rows = []
    for f in files:
        with gzip.open(f, "rt", encoding="utf-8") as fh:
            rows += [_flatten(json.loads(line)) for line in fh]
    api = pd.DataFrame(rows).assign(source="api")
    raw = ctx.cache / "austender-api-releases.jsonl.gz"
    with gzip.open(raw, "wb") as out:
        for f in files:
            with open(f, "rb") as fh:
                out.write(gzip.decompress(fh.read()))
    ctx.keep_raw(raw, keep="r2", url=API)
    res = http_get(PACKAGE).json()["result"]["resources"]
    bulk_url = next((r["url"] for r in res if r.get("name", "").strip() == BULK_NAME), None)
    if not bulk_url:
        raise CorpusError(f"austender: no resource named '{BULK_NAME}' on data.gov.au")
    bulk = _bulk(ctx.fetch(bulk_url, "cn-parent-and-amendments-30092019.xlsx", keep="r2")).assign(source="bulk")
    both = pd.concat([api, bulk[~bulk.cn_id.isin(api.cn_id)]], ignore_index=True)
    both["value"] = pd.to_numeric(both["value"].astype(str).str.replace(r"[,$]", "", regex=True), errors="coerce")
    both = both.sort_values(["published", "cn_id"], na_position="last").reset_index(drop=True)
    both.loc[both.supplier_abn.isin(individual_abns()), "supplier_name"] = None  # sole traders' names stay out
    ctx.table(both, "contracts", describe="Contract notices 2007 onward, one row per notice, with supplier ABN")
