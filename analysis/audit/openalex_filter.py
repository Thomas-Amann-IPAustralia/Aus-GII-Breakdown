"""Does the OpenAlex harvest's "cited at least once" filter drop Australian works that US patents cite (F37, gap B8)?

    uv run python -m audit.openalex_filter     # about 200 OpenAlex calls (US$0.02, inside the free daily allowance)

`openalex_works` keeps works with an Australian institution and `cited_by_count:>0`, then joins them to Reliance on
Science's US patent citations. A work cited by a patent but never by another paper is lost before the join. This draws
a random sample of the patent-cited works outside the harvest (Reliance on Science's citations file, from R2), asks
OpenAlex which of them have an Australian institution today, and writes to `analysis/audit/output/openalex/`:

- `summary.csv`: the counts (patent-cited works; those in the harvest; those outside it; the sample; Australian works
  found in it, with no scholarly citation and with one; those OpenAlex returned under another id, a merged work), the
  scaled estimates with Poisson 95% intervals, and the patent citations involved;
- `found.csv`: the Australian works found: id asked, id returned, year, type, scholarly citations, patent citations.

Needs `OPENALEX_API_KEY`. The sample is fixed (the works with the lowest hash of their id), so a rerun asks the same
works; the answers can change as OpenAlex updates.
"""

from __future__ import annotations

import os
from pathlib import Path

import duckdb
import pandas as pd
from scipy import stats

from corpus.core import http_get, path, raw_path

OUT = Path(__file__).resolve().parent / "output" / "openalex"
SAMPLE = 20_000
API = "https://api.openalex.org/works"


def _poisson(k: int) -> tuple[float, float]:
    """An exact 95% interval for a Poisson count."""
    lo = stats.chi2.ppf(0.025, 2 * k) / 2 if k else 0.0
    return lo, stats.chi2.ppf(0.975, 2 * k + 2) / 2


def main() -> None:
    con = duckdb.connect()
    cites = raw_path("reliance_on_science", "pcs_oa_uspto.csv")
    con.sql(f"CREATE TABLE c AS SELECT oaid, count(*) AS n FROM read_csv_auto('{cites}', sample_size=20000) GROUP BY 1")
    au = path("openalex_works", "au_works")
    con.sql(f"CREATE TABLE au AS SELECT DISTINCT CAST(replace(work_id, 'W', '') AS BIGINT) AS oaid FROM '{au}'")
    con.sql("CREATE TABLE r AS SELECT * FROM c ANTI JOIN au USING (oaid)")
    totals = (
        con.sql("""
        SELECT (SELECT count(*) FROM c) AS cited_works, (SELECT sum(n) FROM c) AS citations,
               (SELECT count(*) FROM c SEMI JOIN au USING (oaid)) AS in_harvest,
               (SELECT sum(n) FROM c SEMI JOIN au USING (oaid)) AS in_harvest_citations,
               (SELECT count(*) FROM r) AS outside, (SELECT sum(n) FROM r) AS outside_citations
    """)
        .df()
        .iloc[0]
    )
    sample = con.sql(f"SELECT oaid, n FROM r ORDER BY hash(oaid), oaid LIMIT {SAMPLE}").df()
    ids, n = sample.oaid.astype(str).tolist(), dict(zip(sample.oaid.astype(str), sample.n, strict=True))
    found = []
    for i in range(0, len(ids), 100):
        batch = ids[i : i + 100]
        params = {
            "filter": "ids.openalex:" + "|".join("W" + x for x in batch) + ",institutions.country_code:au",
            "select": "id,ids,cited_by_count,publication_year,type",
            "per-page": 100,
            "api_key": os.environ["OPENALEX_API_KEY"],
        }
        for w in http_get(API, params=params, timeout=120).json().get("results", []):
            returned = w["id"].rsplit("W", 1)[-1]
            asked = returned if returned in n else None  # a merged work comes back under its new id
            found.append(
                {
                    "asked": asked,
                    "returned": returned,
                    "year": w.get("publication_year"),
                    "type": w.get("type"),
                    "scholarly_citations": w.get("cited_by_count"),
                    "patent_citations": n.get(returned),
                }
            )
    f = pd.DataFrame(found)
    uncited = int((f.scholarly_citations == 0).sum())
    merged = int(f.asked.isna().sum())
    scale = totals.outside / SAMPLE
    rows = {
        "patent-cited works (Reliance on Science)": totals.cited_works,
        "US patent citations to them": totals.citations,
        "in the harvest (Australian, cited at least once)": totals.in_harvest,
        "US patent citations to works in the harvest": totals.in_harvest_citations,
        "outside the harvest": totals.outside,
        "sampled from outside": SAMPLE,
        "Australian in the sample": len(f),
        "of which no scholarly citation": uncited,
        "of which returned under another id (merged)": merged,
        "patent citations of the sample": int(sample.n.sum()),
        "patent citations of the Australian works found (asked ids)": int(f.patent_citations.fillna(0).sum()),
    }
    for label, k in (("Australian", len(f)), ("no scholarly citation", uncited), ("merged", merged)):
        lo, hi = _poisson(k)
        rows[f"estimated patent-cited works outside the harvest: {label}"] = k * scale
        rows[f"  95% interval, low: {label}"] = lo * scale
        rows[f"  95% interval, high: {label}"] = hi * scale
    OUT.mkdir(parents=True, exist_ok=True)
    pd.Series(rows, name="value").rename_axis("measure").to_csv(OUT / "summary.csv")
    f.to_csv(OUT / "found.csv", index=False)
    print(pd.Series(rows).round(1).to_string())


if __name__ == "__main__":
    main()
