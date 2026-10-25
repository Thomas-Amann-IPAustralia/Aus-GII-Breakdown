# Analysis workspace

Code and outputs for the analysis sessions. The corpus itself is described in `docs/catalogue.md`; this folder holds
what is learned by using it.

## Exploratory data analysis (EDA)

Three notebooks, one per stage, each organised by *lenses*: analysis-ready tables with one row per right, firm, postal
area, country-year or month for Australia, with industries and research institutions planned. Every dataset is attached
to a lens and goes through all three stages (ADR 0007). The plan is `docs/eda-plan.md`; the status is
`docs/handover-eda.md`.

```sh
uv sync --group dev --group analysis
uv run python -m eda.build          # the lens tables, into analysis/eda/data/ (gitignored; under a minute)
uv run jupyter nbconvert --to notebook --execute --inplace analysis/notebooks/01_univariate.ipynb
```

| Path | What it holds |
|---|---|
| `notebooks/01_univariate.ipynb`, `02_bivariate.ipynb`, `03_multivariate.ipynb` | The three stages, committed with their outputs so they read on GitHub |
| `eda/build.py` | How each lens is built from the corpus (every derived column is defined here) |
| `eda/variables.yaml` | Every lens column in plain English: label, kind, unit, notes |
| `eda/data.py` | `sql()`: DuckDB over the corpus (`{source/table}`) and the lenses (`{lens/name}`), refusing un-aggregated results |
| `eda/style.py` | One look for every chart (colour-blind-safe palette), labels, source captions |
| `eda/univariate.py`, `bivariate.py`, `multivariate.py` | The tools of each stage |

## Profiling the corpus

```sh
uv run python analysis/profile_corpus.py            # every stage: about 10 minutes once R2 tables are cached
uv run python analysis/profile_corpus.py --stage report   # rebuild PROFILE.md from the CSVs
```

| Output (`analysis/output/`) | What it holds |
|---|---|
| `tables.csv` | One row per processed table: opens, rows against the manifest, columns against the manifest, open time |
| `columns.csv` | One row per column: type, null rate, empty strings, approximate distinct count, min and max, an example |
| `keys.csv` | How well each join key links to its authoritative list (ABN to the ABR, postcode to ABS POAs and so on), and the most common key value |
| `PROFILE.md` | The above as a readable report |

Everything is read with DuckDB straight off the Parquet files, so the 49-million-row `iprapid/events` and 20-million-row
`abr/abns` are never loaded whole into memory. Do the same in analysis code: filter and aggregate in DuckDB, and bring
only the result into pandas. The machine has about 15 GB of memory and 4 cores.

## What the profile found (corpus as of the 2026-10-22 builds)

- **Access.** All 152 processed tables (130 in the repo, 22 in R2) open; every row count and column list matches
  `data/manifest.json`. 314.7 million rows and 8,067 columns in all.
- **ABNs join cleanly.** Every ABN in IP RAPID, IPLORD, AusTender, the RDTI, the ATO tax-transparency data and the
  linkage spine is in the ABR (99.7 to 100% of rows). Counts of distinct entities are therefore safe to compare.
- **ASIC's `abn` is `'0'` for 40.6% of companies** (1.63 million of 4.02 million) that have no ABN. Treat `'0'` as
  missing before joining or counting. The remaining ASIC ABNs link to the ABR. Because of this, only 59% of ASIC
  `acn` values are found in the ABR's `acn`; that is companies without an ABN, not a gap in the ABR.
- **Postcodes need cleaning before they join to ABS geography.** Many postcodes are foreign or free text (for example
  `250-0123`). By rows, 99.6% of ABR, 98.9% of linkage-spine and 88.2% of trade-mark applicant postcodes match an ABS
  POA, but only 44.7% of patent applicants do (most patent applicants are overseas). Count distinct postcodes with
  care: ABR has 15,276 distinct postcodes against about 2,600 real ones.
- **Google Patents joins to IP RAPID only for modern filings.** IP RAPID uses a 10-digit year-first application
  number for every patent. Google Patents keeps the original schemes before the 2000s (`AU-PP379798-A`,
  `AU-4782101-A`, `AU-198303605-F`). After stripping the `AU-` prefix and suffix the match is 100% for filings from
  2010 on, about 65% for the 2000s and 0% before 2000. Pre-2000 matching needs a number map the corpus does not hold.
- **Trade marks, SA2s and IPC link fully.** TM-Link, IP RAPID and the Nice-class tables share application numbers
  (TM-Link's `tm_link` table covers 93.9%). SA2 codes agree across ABS Census, SEIFA, CABEE and the region tables.
  IP RAPID's IPC classifications match the IPC-to-industry concordance for 93.9% of distinct subclasses.
- **Empty and placeholder columns.** 88 columns are entirely null (40 in OECD, 22 in IPLORD, 13 in ABS BCS, 8 in
  ABS regions, 4 in IP RAPID, 1 in the ATO data) and 481 are constant. IP RAPID `pbr_rights` has no ABNs at all, and
  `patent_rights.enforceable_from_date` is empty. `google_patents/members` stores empty strings, not nulls, in
  `entity_status` (97.6%), `au_assignee_names` (87.5%) and `inventor_countries` (83.7%).
- **Dates.** `1800-01-01` is the earliest value in IP RAPID `events`, `links` and `party`; it looks like a
  placeholder, not a real date, so exclude it from any timeline. IP RAPID `events.event_effective_date` runs to
  2033 and `deemed_retired_date` to 2029, which are scheduled dates; ABR status dates also run into 2027.

## Not yet checked

- Duplicate rows and whether each table's natural key is unique.
- Whether values mean the same thing across sources (for example, what counts as a "state" or an entity type).
- The raw files in R2 (not needed for analysis; large).
- The `google_patents` rebuild credentials: only reading is verified, not re-running the BigQuery query.
