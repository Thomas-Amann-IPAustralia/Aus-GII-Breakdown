"""WIPO IP statistics: filings, grants and rights in force by office and applicant's origin, every country, 1980 on.

Q3: which countries' applicants file where (Australians abroad, foreigners in Australia), including trade marks and
designs, which the World Bank no longer publishes; office workloads (examiners, pendency) for comparison. Read from
the public API behind the WIPO IP Statistics Data Center (https://www3.wipo.int/ipstats/), which serves the same CSV
exports as the site. Each export asks for every office and origin the indicator has. Raw: each export (gzipped CSV;
repo, or R2 when large). Source: WIPO statistics database; cite WIPO.

Processed:
- `office_origin`: one row per indicator, filing office, applicant's origin, breakdown (field of technology or class,
  where the indicator has one) and year. Resident filings are those where office and origin are the same; an
  origin's total is the sum over offices.
- `office`: indicators reported by office only (rights in force, examiners, pendency, oppositions).
- `pmh`: PCT applications by origin, Madrid applications by country of holder and Hague applications by origin.
"""

from __future__ import annotations

import csv
import gzip
import io
import re

import pandas as pd

from ..core import Ctx, http_get

API = "https://api.ipstatsdc.deda.prd.web1.wipo.int/api/v1/public"
HEADERS = {"Accept-Language": "en"}  # the API answers 400 without it

# (tab, indicator, report type): 15 is by office and origin, 11 by office only
IPS = [
    ("patent", 10, 15),  # total applications
    ("patent", 23, 15),  # total grants
    ("patent", 15, 15),  # in force
    ("patent", 21, 15),  # foreign-oriented patent families by origin and destination office
    ("patent", 17, 15),  # publications by field of technology
    ("patent", 25, 15),  # publications relating to renewable energy
    ("patent", 26, 15),  # publications for AI-related technology
    ("patent", 111, 11),  # examiners
    ("patent", 112, 11),  # pendency to first office action
    ("patent", 120, 11),  # post-grant oppositions
    ("utility", 70, 15),  # utility model applications
    ("trademark", 48, 15),  # class count in applications
    ("trademark", 49, 15),  # class count in registrations
    ("trademark", 90, 15),  # applications by Nice class
    ("trademark", 43, 11),  # in force
    ("trademark", 114, 11),  # pendency
    ("trademark", 117, 11),  # examiners
    ("industrial", 68, 15),  # design count in applications
    ("industrial", 69, 15),  # design count in registrations
    ("industrial", 92, 15),  # applications by Locarno class
    ("industrial", 63, 11),  # registrations in force
]
# (tab, indicator, the list of codes to ask for): PCT by origin, Madrid by holder, Hague by origin
PMH = [("pct", 1001, "ori"), ("madrid", 2002, "ori"), ("hague", 3001, "ori")]


def _get(path: str, **params):
    return http_get(f"{API}/{path}", params=params, headers=HEADERS, timeout=600)


def _labels(family: str, tab: str) -> dict[int, str]:
    d = _get(f"{family}-search/formcontrols", selectedTab=tab).json()
    items = d.get("ipsIndicatorMap") or d.get("pmhIndicatorMap") or []
    return {int(i.get("indicatorId") or i.get("value")): i["label"].strip() for i in items}


def _read(text: str) -> tuple[str, pd.DataFrame]:
    """An export: a preamble (right, indicator, source), then a CSV whose year columns follow the dimensions."""
    lines = text.splitlines()
    updated = next((m.group(1) for line in lines if (m := re.search(r"Last updated: (.+)$", line))), "")
    start = next(i for i, line in enumerate(lines) if re.search(r",\s*\"?(19|20)\d\d\"?,", line))
    rows = list(csv.reader(io.StringIO("\n".join(lines[start:]))))
    head = [h.strip() for h in rows[0]]
    years = [i for i, h in enumerate(head) if re.fullmatch(r"(19|20)\d\d", h)]
    dims = head[: years[0]]
    out = []
    for r in rows[1:]:
        if len(r) < len(head) - 1:
            continue
        key = r[: years[0]]
        for i in years:
            v = r[i].replace(",", "").strip() if i < len(r) else ""
            if v:
                out.append((*key, int(head[i]), float(v)))
    return updated, pd.DataFrame(out, columns=[*dims, "year", "value"])


def _keep(ctx: Ctx, name: str, text: str, url: str) -> None:
    p = ctx.cache / f"{name}.csv.gz"
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", mtime=0, filename="") as f:
        f.write(text.encode())
    if p.stat().st_size > 45 << 20:
        ctx.keep_raw(p, keep="r2", url=url)
    else:
        ctx.raw.mkdir(parents=True, exist_ok=True)
        p.replace(ctx.raw / p.name)
        ctx.keep_raw(ctx.raw / p.name, url=url)


def _download(params: dict, offices: list[str], breakdown: bool) -> str:
    """One export, or for indicators with a breakdown (classes, fields), one per 20 offices, joined."""
    if not breakdown:
        return _get("ips-search/downloadCsv", **params).content.decode("utf-8-sig")
    parts = []
    for i in range(0, len(offices), 20):
        text = _get("ips-search/downloadCsv", **{**params, "ipsOffSelValues": ",".join(offices[i : i + 20])})
        lines = text.content.decode("utf-8-sig").splitlines()
        start = next((j for j, line in enumerate(lines) if re.search(r",\s*\"?(19|20)\d\d\"?,", line)), None)
        if start is None:
            continue
        parts.append(lines if not parts else lines[start + 1 :])
    return "\n".join(line for part in parts for line in part)


def _ips(ctx: Ctx) -> tuple[pd.DataFrame, pd.DataFrame]:
    labels: dict[str, dict[int, str]] = {}
    both, office_only = [], []
    for tab, ind, rp in IPS:
        labels.setdefault(tab, _labels("ips", tab))
        lists = _get("ips-search/loadOffOrgTechList", indicator=ind, rpType=rp).json()
        offices, origins = lists.get("ipsOffList") or {}, lists.get("ipsOriginList") or {}
        params = {"type": "IPS", "selectedTab": tab, "indicator": ind, "reportType": rp, "fromYear": 1980}
        params["toYear"] = _get("ips-search/to-year").json()
        params["ipsOffSelValues"] = ",".join(offices)
        if rp == 15:
            params["ipsOriSelValues"] = ",".join(origins)
        if lists.get("ipsTechList"):
            params["ipsTechSelValues"] = ",".join(lists["ipsTechList"])
        name = f"{tab}_{ind}_{rp}"
        cached = ctx.raw / f"{name}.csv.gz"
        if cached.exists():  # delete data/raw/wipo_ipstats/ to fetch afresh
            text = gzip.decompress(cached.read_bytes()).decode()
        else:
            text = _download(params, list(offices), bool(lists.get("ipsTechList")))
        _keep(ctx, name, text, f"{API}/ips-search/downloadCsv ({tab} {ind} {rp})")
        updated, df = _read(text)
        ctx.log(f"{tab} {ind}: {len(df):,} values")
        dims = [c for c in df.columns if c not in ("year", "value")]
        out = pd.DataFrame(
            {
                "right": tab,
                "indicator_id": ind,
                "indicator": labels[tab].get(ind, str(ind)),
                "office_code": df["Office (Code)"] if "Office (Code)" in df else None,
                "office": df["Office"] if "Office" in df else None,
            }
        )
        if rp == 15:
            by_name = {v: k for k, v in origins.items()}
            out["origin"] = df["Origin"]
            out["origin_code"] = df["Origin"].map(by_name)
        extra = [c for c in dims if c not in ("Office", "Office (Code)", "Origin", "Origin (Code)")]
        out["breakdown"] = df[extra].astype(str).agg("; ".join, axis=1) if extra else None
        out["year"], out["value"], out["last_updated"] = df["year"], df["value"], updated
        (both if rp == 15 else office_only).append(out)
    return pd.concat(both, ignore_index=True), pd.concat(office_only, ignore_index=True)


def _pmh(ctx: Ctx) -> pd.DataFrame:
    out = []
    for tab, ind, _ in PMH:
        label = _labels("pmh", tab).get(ind, str(ind))
        lists = _get("pmh-search/loadOffOrgClassList", indicator=ind).json()
        origins = [c for c in (lists.get("pmhOriginList") or {}) if c != "ZZ"]
        params = {"type": "PMH", "selectedTab": tab, "indicator": ind, "reportType": 4001, "fromYear": 1995}
        params["toYear"] = max(int(y["value"] if isinstance(y, dict) else y) for y in _pmh_years(tab))
        params["pmhOriSelValues"] = ",".join(origins)
        if tab == "pct":
            params["pmhOffSelValues"] = "ZZ"  # every receiving office
        r = _get("pmh-search/downloadCsv", **params)
        text = r.content.decode("utf-8-sig")
        _keep(ctx, f"{tab}_{ind}", text, f"{API}/pmh-search/downloadCsv ({tab} {ind})")
        updated, df = _read(text)
        code = next(c for c in df.columns if c.endswith("(Code)") and not c.startswith("Receiving"))
        name = code.replace("(Code)", "").strip()
        out.append(
            pd.DataFrame(
                {
                    "system": tab,
                    "indicator_id": ind,
                    "indicator": label,
                    "origin_code": df[code],
                    "origin": df[name],
                    "year": df["year"],
                    "value": df["value"],
                    "last_updated": updated,
                }
            )
        )
        ctx.log(f"{tab} {ind}: {len(df):,} values")
    return pd.concat(out, ignore_index=True)


def _pmh_years(tab: str) -> list:
    return _get("pmh-search/formcontrols", selectedTab=tab).json()["pmhToYearList"]


def run(ctx: Ctx) -> None:
    both, office_only = _ips(ctx)
    ctx.table(both, "office_origin", describe="WIPO indicators by filing office and applicant's origin, long")
    ctx.table(office_only, "office", describe="WIPO indicators by office only, long")
    ctx.table(_pmh(ctx), "pmh", describe="PCT, Madrid and Hague applications by origin or holder, long")
