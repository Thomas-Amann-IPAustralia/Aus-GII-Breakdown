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

## What the profile found (corpus as of 2026-10-25)

- **Access.** All 162 processed tables (139 in the repo, 23 in R2) open; every row count and column list matches
  `data/manifest.json`. 317.8 million rows and 8,227 columns in all.
- **ABNs join cleanly.** Every ABN in IP RAPID, IPLORD, AusTender, the RDTI, the ATO tax-transparency data and the
  linkage spine is in the ABR (99.7 to 100% of rows). Counts of distinct entities are therefore safe to compare.
- **ASIC's `abn` is `'0'` for 40.6% of companies** (1.63 million of 4.02 million) that have no ABN. Treat `'0'` as
  missing before joining or counting. The remaining ASIC ABNs link to the ABR. Because of this, only 59% of ASIC
  `acn` values are found in the ABR's `acn`; that is companies without an ABN, not a gap in the ABR.
- **Postcodes need cleaning before they join to ABS geography.** Many postcodes are foreign or free text (for example
  `250-0123`). By rows, 99.6% of ABR, 98.9% of linkage-spine and 88.2% of trade-mark applicant postcodes match an ABS
  POA, but only 44.7% of patent applicants do (most patent applicants are overseas). Count distinct postcodes with
  care: ABR has 15,276 distinct postcodes against about 2,640 ABS postal areas.
- **Google Patents joins to IP RAPID through `au_application`.** IP RAPID uses a 10-digit year-first application
  number for every patent; Google Patents keeps the original schemes before the 2000s (`AU-PP379798-A`,
  `AU-4782101-A`, `AU-198303605-F`). The profile's join (by digits only) understates the match: the review measured it
  on `google_patents/members.au_application`, which converts the old numbers, at 79.9% before 1990, 41.9% in the 1990s,
  44.0% in the 2000s and 84.9% from 2010 (the latter including 57,769 design numbers, kind S, which are not patents).
  The rest are mostly the 1990s' letter-series provisionals and unmatched 7-digit numbers (review item B4).
- **Trade marks, SA2s and IPC link fully.** TM-Link, IP RAPID and the Nice-class tables share application numbers
  (TM-Link's `tm_link` table covers 93.9%). SA2 codes agree across ABS Census, SEIFA, CABEE and the region tables.
  IP RAPID's IPC classifications match the IPC-to-industry concordance for 93.9% of distinct subclasses.
- **Empty and placeholder columns.** 94 columns are entirely null (39 in OECD, 22 in IPLORD, 13 in ABS BCS, 8 in
  ABS regions, 6 in ABS prices, 4 in IP RAPID, and 1 each in ABS labour and the ATO data) and 522 are constant. IP RAPID `pbr_rights` has no ABNs at all, and
  `patent_rights.enforceable_from_date` is empty. `google_patents/members` stores empty strings, not nulls, in
  `entity_status` (97.6%), `au_assignee_names` (87.5%) and `inventor_countries` (83.7%).
- **Dates.** `1800-01-01` is the earliest value in IP RAPID `events`, `links` and `party`; it looks like a
  placeholder, not a real date, so exclude it from any timeline. IP RAPID `events.event_effective_date` runs to
  2033 and `deemed_retired_date` to 2029, which are scheduled dates; ABR status dates also run into 2027.

## Checked since (2026-10-25, ADR 0010 and 0011)

- **Duplicate rows.** Every table was scanned for exact duplicates. Those that came from parsers (CABEE, PHIDU, CER,
  the ABS R&D cubes, the ARTG, AusTender) are repaired, and each repaired table is tested for one row per key. Those in
  the source files remain (IP RAPID's party, description, links and classification tables, TM-Link, ASIC's names):
  every lens counts distinct rights or parties, so they change no figure.
- **Values kept.** Every non-empty value in every SDMX flow (OECD and ABS) survives into its table; the OECD's IP tax
  regimes, which are mostly text, keep it in `value_text`.
- **IP RAPID's event dates.** A trade mark's registration has its filing date as its effective date (85%); the date it
  was entered is the declared date, recorded from 1986 (ADR 0010). Every other event the timeline counts has its own
  effective date. `event_category` is empty for 25,819 patent `new` events and one PBR event; no lens uses them.
- **IP RAPID's link countries.** For patents, `links.linked_application_country` is not the linked application's
  office: all 577,317 PCT application numbers are labelled `au` (37,656 more `wo`), and of the 85,067 convention
  priorities labelled `au`, 5,603 are PCT numbers and 9,965 have other offices' formats (mostly 11 to 15 digits).
  Tell an Australian priority by its number (year first, ten digits), as the N01 check did. No lens reads the column.

## Found in Stage 1 (2026-10-25, ADR 0012)

From the `rights` section of `01_univariate.ipynb`. The lens is repaired; the corpus tables are as published.
- **IP RAPID's "agent" is the address for service.** `party_role_category = 'applicant_agent'` names an agent for every
  trade mark, but for Australian applicants it is often the applicant itself (same party id or name). Count an agent
  as an attorney only if it is not one of the right's applicants.
- **`main_area` repeats the class.** For trade marks and designs it equals `main_class` (Nice or Locarno), not a WIPO
  technology field.
- **`deemed_retired_date` of 1 January 1970** is a placeholder (1,282 rights, all filed from 2013).
- **Trade mark registration dates before 1986 are filing dates** (98.6% on the day filed), as the events' effective
  dates are (ADR 0010).
- **`applicant_state` is left out** for about a third of Australian standard patents filed from FY2024, though the
  postcode is there; for overseas applicants it holds their own states ("wa" can be Washington).
- **Patents filed before FY2003 have one set of applicants** in `iprapid/party`, first recorded about 16 to 20 years
  after filing (when records moved between systems), so a change of holder before then is not kept (ADR 0013).
- **A party keeps its id through changes of address**, with a new row for each: compare founding and current
  applicants by party id, not by row (most founding trade mark rows are no longer current, though the holder
  changed for 15.3%).
- **Times to registration** cluster sharply at about 222 days for trade marks filed since FY2020: a lead, perhaps the
  shortest path through examination and opposition.

## Not yet checked

- Whether values mean the same thing across sources (for example, what counts as a "state" or an entity type).
- The raw files in R2 (not needed for analysis; large).
- The `google_patents` rebuild credentials: only reading is verified, not re-running the BigQuery query.
