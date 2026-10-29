"""How much do the AusTender amendments the corpus lacks matter (OQ3, gap B10)?

    uv run python -m audit.austender_amendments     # about 2,000 API calls (free), ten minutes

`austender` asks the API by id for every contract in the bulk file still running on its last day (30 August 2019);
amendments published later to contracts that had ended by then are in neither part. Asking all 740,000 or so ended
contracts would take days, so this asks a random sample of them, by the year their latest end date falls in, and
writes to `analysis/audit/output/austender/`:

- `summary.csv`: by end-year band, the contracts asked, those with amendments numbered beyond the bulk file's last
  (the API also re-released old notices with later dates, which are not counted), and the value those amendments add
  (the latest one's value less the bulk file's; a jump of 100 times to $100 million or more, a value keyed in the
  wrong units as `value_jump` flags, is set aside), scaled to every ended contract in the band, and its share of the
  band's value in the corpus;
- `found.csv`: those contracts: id, band, new amendments, the first one's publication date, value before and after.

The sample is fixed (the contracts with the lowest hash of their id in each band).
"""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import duckdb
import pandas as pd

from corpus import path
from corpus.sources.austender import API, BULK_TO, _flatten, _get

OUT = Path(__file__).resolve().parent / "output" / "austender"
CACHE = Path.home() / ".cache" / "ipholmes" / "audit_austender"  # the API's answers, so a rerun resumes
PER_BAND = 500
BANDS = {"ended Aug 2018 to Aug 2019": (2018.67, 2019.67), "ended 2017-18": (2017.67, 2018.67),
         "ended 2015 to 2017": (2015.67, 2017.67), "ended before Sep 2015": (0, 2015.67)}  # fmt: skip


def _ask(cn: str) -> list[dict]:
    f = CACHE / f"{cn}.json"
    if f.exists():
        return json.loads(f.read_text())
    rel = _get(f"{API}/findById/{cn}").get("releases", [])
    f.write_text(json.dumps(rel))
    return rel


def main() -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    contracts = path("austender", "contracts")
    con.sql(f"""
        CREATE TABLE ended AS
        SELECT parent_cn_id, max(TRY_CAST("end" AS DATE)) AS last_end,
               arg_max(value, coalesce(amendment, 0)) AS value, max(coalesce(amendment, 0)) AS last_amendment
        FROM '{contracts}' WHERE parent_cn_id IS NOT NULL
        GROUP BY 1 HAVING bool_and(source = 'bulk') AND max(TRY_CAST("end" AS DATE)) < DATE '{BULK_TO}'
    """)
    rows, found = [], []
    for band, (lo, hi) in BANDS.items():
        t = "year(last_end) + (month(last_end) - 1) / 12"
        where = f"{t} >= {lo} AND {t} < {hi}"
        pop = con.sql(f"SELECT count(*), sum(value) FROM ended WHERE {where}").fetchall()[0]
        sample = con.sql(
            f"SELECT parent_cn_id, value, last_amendment FROM ended WHERE {where} "
            f"ORDER BY hash(parent_cn_id), parent_cn_id LIMIT {PER_BAND}"
        ).df()
        with ThreadPoolExecutor(max_workers=8) as ex:
            answers = list(ex.map(_ask, sample.parent_cn_id))
        added, hits, amendments, jumps = 0.0, 0, 0, 0
        for (cn, before, known), rel in zip(sample.itertuples(index=False), answers, strict=True):
            # amendments the bulk file does not hold: numbered beyond its last (a re-release of an old notice is not)
            new = [a for a in map(_flatten, rel) if (a["amendment"] or 0) > known]
            if not new:
                continue
            hits += 1
            amendments += len(new)
            latest = max(new, key=lambda r: r["amendment"])
            after = float(latest["value"]) if latest["value"] is not None else before  # the API gives text
            jump = before and after >= 100 * before and after >= 1e8  # keyed in the wrong units (`value_jump`)
            jumps += bool(jump)
            added += 0 if jump else (after or 0) - (before or 0)
            first = min(a["published"] or "" for a in new)
            found.append(
                {"cn": cn, "band": band, "new_amendments": len(new), "first_new_published": first,
                 "value_before": before, "value_after": after, "value_jump": bool(jump)}
            )  # fmt: skip
        scale = pop[0] / len(sample)
        rows.append(
            {
                "band": band,
                "ended contracts": pop[0],
                "their value (AUD)": pop[1],
                "asked": len(sample),
                "with amendments the bulk file lacks": hits,
                "those amendments": amendments,
                "set aside as a value jump": jumps,
                "value added in the sample (AUD)": added,
                "value added, scaled to the band (AUD)": added * scale,
                "as % of the band's value": 100 * added * scale / pop[1] if pop[1] else None,
            }
        )
    OUT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT / "summary.csv", index=False)
    pd.DataFrame(found).to_csv(OUT / "found.csv", index=False)
    print(pd.DataFrame(rows).to_string())


if __name__ == "__main__":
    main()
