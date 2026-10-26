# Analysis workspace

Code and outputs for the analysis sessions. The corpus itself is described in `docs/catalogue.md`; this folder holds
what is learned by using it.

## Exploratory data analysis (EDA)

Three notebooks, one per stage, each organised by *lenses*: analysis-ready tables with one row per right, firm, postal
area, country-year, industry-year, research institution-year or month for Australia. Every dataset is attached
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
| `eda/institutions/` | The reviewed link for the `institutions` lens: its institutions (by ROR), their other names and their ABNs (ADR 0021) |
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

## Found in the timeline's Stage 1 profile (2026-10-25, ADR 0014)

From section 5 of `01_univariate.ipynb`. The timeline lens is repaired; the corpus tables are as published.
- **Old records are survivors.** IP RAPID holds only the trade marks filed before 1983, designs filed before 1986 and
  provisional applications filed before September 1985 that were still on the register when its records were
  computerised: 2% to 5% of trade marks filed in 1981 were never registered, against 51% to 59% from 1983. Counts of
  those rights by year of filing understate filings; the rows themselves are real.
- **Patent outcomes start with patents filed in 1979.** 68.5% of standard patents filed in 1979 have a grant date,
  against 1.0% to 1.9% of those filed in 1976 to 1978.
- **Some events are dated in batches.** In `iprapid/events`, patent cessations are dated on 0 to 3 days a month to
  March 1995 (29.8% of months from September 1986 empty), expiries to December 1994, patent lapses to 1988 and design
  lapses to 1993. Weekly or daily since.
- **Pauses and backlogs inside complete records:** trade mark registrations (0 in January 1996, 4,021 in March, when
  the Trade Marks Act 1995 commenced), patent grants (113 in June 1991; 248 then 3,373 in October and November 1998)
  and patent cessations (82 in December 2006; 7 in February 2020, 2,468 in March).
- **The 1995 term change shows in the expiries:** almost none from July 1995 to June 1999, when the standard patent
  term rose from 16 to 20 years for patents still in force. The policy register now holds it.
- **The CPI's base** is the month of September 2025 (= 100); the quarterly index averages its three months, so the
  September quarter 2025 is 99.73.

## Found in the events attachment (2026-10-25, ADR 0015)

From section 1.8.2 of `01_univariate.ipynb`. The `rights` lens gains each right's milestones and lifetime; the
corpus tables are as published.
- **`is_standing` marks events later reversed.** 4.76% of patent lapse events are not standing, and most of those
  patents went on to be granted. Take a right's milestones from standing events.
- **Patent assignments are published twice,** as `published_assignments_*` and as `published_ip_right_assignment`
  (99.78% of assigned patents have both). Count one.
- **A trade mark's term runs from its earliest filing date,** which for a Madrid mark is the international
  registration's, not the application date IP RAPID gives.
- **A patent's cessation is dated at the end of its grace period,** 6 to 7 months after an anniversary of its date
  of patent (84.59% of those ceased since 1996).
- **Milestones are recorded from different dates:** patents' examination requests from the early 1980s' filings,
  trade marks' acceptances from the mid-1980s', designs' examination requests from 2013. Petty patents filed FY1986
  to FY1988 mostly lack an acceptance.
- **Trade mark requests for expedited examination fall** from about 1,400 a month to about 230 in November 2018, when
  the trade mark records moved between systems: recording or practice, not yet known.
- **171 events are dated before the right's earliest filing,** including 26 trade mark oppositions dated 1909.
- **Placeholders** (1 January 1800, 1900, 1970): 3,162 of 49.35 million events, 34 links and 105 party start dates.

## Found in the firms lens's Stage 1 profile (2026-10-25, ADR 0016)

From section 2 of `01_univariate.ipynb`.
- **IPLORD links ABNs that IP RAPID does not.** 52,949 of the spine's ABNs are linked to trade marks, designs or plant
  breeder's rights by IPLORD (to FY2020) but are on no IP RAPID right; 50,790 are in the spine for that reason alone.
- **IPLORD's counts differ from IP RAPID's applicant panel,** built to the same design: for ABNs with trade marks in
  both, 81.02% agree, but the largest filers run up to 7 times higher in IPLORD (total 1.84 times), while IPLORD's
  weighted total is 0.42 times IP RAPID's. Do not add or splice them.
- **IPLORD has no patents:** its columns cover trade marks, designs and plant breeder's rights only.
- **The ABR leaves `state` blank** (an empty string) for 3,977 of the spine's ABNs.
- **Recent filers are less often linked to an ABN:** Australian organisations' trade marks with a filer's ABN fall from
  84.1% (FY2024) to 59.9% (FY2026).
- **The tax transparency reports' first years** (2013-14 to 2015-16) hold 29 rows under $100 million, and the
  2013-14 December sheet lists two ABNs twice.

## Found in the national lens's Stage 1 profile (2026-10-26, ADR 0019)

From section 4 of `01_univariate.ipynb`.
- **WIPO's origins are mostly unknown before 1995.** 29% to 34% of WIPO's patent applications by origin had an
  unknown origin to 1993 (1.12% in 2024), and 87% to 90% of those at IP Australia; Australians' applications abroad,
  and WIPO's grants and designs to Australian residents, are near zero until 1994. Compare WIPO by country from 1995.
- **WIPO lists former states as origins** (the Soviet Union, East Germany, Czechoslovakia, Yugoslavia, Zaire, the
  Netherlands Antilles), some with values long after they ceased (East Germany to 2023). The lens keeps them under
  ISO 3166-3 codes; they were silently dropped before.
- **The World Bank's trade mark and design series "by count" count classes and designs,** not applications: they equal
  WIPO's class and design counts at the office.
- **The OECD publishes suppressed business demography values as 0** (536,269 of them, flagged "missing value;
  suppressed"); the lens empties them.
- **In the OECD's cross-border patent tables the "World" partner is the country's total,** not a cross-border count, and
  "WXD" is the rest of the world.
- **The OECD's business demography, innovation and IP methods and IP tax regime flows hold no Australian values;**
  its venture capital ends for Australia in 2019.
- **Closing the Gap's target 15 has an "Aus Gov" jurisdiction** (land and sea held by the Australian Government), which
  the parser had left unmelted; and its tables mix observations with trajectories to 2031 (`description7`).
- **Two Measuring What Matters pages stack males and females under one header** (feeling safe, health-adjusted life
  expectancy), so a row and column held two values; the parser now names each block.
- **IP RAPID's innovation patents filed in 2016 exceed WIPO's utility model count by a third** (2,469 against 1,855);
  other years are 0.958 to 1.072 of it.

## Found in the industries lens's Stage 1 profile (2026-10-26, ADR 0020)

From section 6 of `01_univariate.ipynb`.
- **The corpus's ALP patent crosswalk excludes services,** so 90.8% of standard patents fall in manufacturing and no
  service division receives more than 0.23%.
- **IP RAPID stores Nice classes 1 to 9 without a leading zero;** the ALP crosswalk writes them '01' to '09'.
- **The ISIC-to-ANZSIC step split weight over partial links** (pharmaceuticals sent half their weight to textile
  finishing and inorganic chemicals); repaired in `concordances`, which now has a `reprocess`.
- **ALP maps G21B (nuclear fusion) wholly to ISIC 1392 (made-up textiles).** Its own quirk, left as published; G21B
  has few patents.
- **Trade mark classes break in January 2002** (the Nice 8th edition: class 42 split into 42 to 45): classes 43 to 45
  have 1 mark filed in FY2000 and 1,185 in FY2002.
- **ABS cube headings can nest three deep** (the venture capital tables), but the cube reader records two, so 469
  values share a section and row label; the lenses key ABS cube rows by their row on the sheet as well.
- **BCARR's two releases overlap** (FY2016 to FY2023) and differ by up to 1.2%; the BCS flags 36.2% of its values and
  withholds 25%.

## Found in the institutions lens's Stage 1 profile (2026-10-26, ADR 0021)

From section 7 of `01_univariate.ipynb`.
- **ROR's API pages are not in a stable order:** paging through a query for Australian records returned 2,052 rows for
  1,518 records. The `ror` source reads ROR's data dump instead.
- **IP RAPID gives plant breeder's rights' applicants as codes** (UUIDs), organisations included, with no ABNs, so no
  plant breeder's right can be linked to a filer by name or ABN.
- **Universities file through companies, under many names:** UNSW as NewSouth Innovations and before that Unisearch
  (one company, ACN 000 263 025); CSIRO under eight spellings. IP RAPID gives UQ's own filings no ABN (96% of them).
- **OpenAlex's counts by year** run from 2010 and include a few works dated 2027 to 10000 (placeholders), which the
  lens leaves out.
- **The NHMRC's workbooks give the administering institution's ROR only from the 2025 round;** the ARC gives names, and
  its current administering organisation for older grants can be a successor (Adelaide University), so the lens uses
  the organisation at announcement.
- **The ARC's "Linkage" program holds the Centres of Excellence and infrastructure grants** as well as research with
  industry.
- **Half the universities' standard patents carry a postcode that is not a postal area** (2052, 3800, 4072, 3010,
  2006): the institutions hold 71.58% of such real codes with no residents (U87).

## Not yet checked

- Whether values mean the same thing across sources (for example, what counts as a "state" or an entity type).
- The raw files in R2 (not needed for analysis; large).
- The `google_patents` rebuild credentials: only reading is verified, not re-running the BigQuery query.
