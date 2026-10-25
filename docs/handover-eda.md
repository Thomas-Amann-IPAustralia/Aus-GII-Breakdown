# Handover: exploratory data analysis

For the next Claude Code session. Read `CLAUDE.md` first, then `docs/eda-plan.md`.

**Status (2026-10-25):** Stage 1 has not started beyond its data overviews. Since the last handover:
- the corpus has had an independent review, `docs/Aus-GII-Independent-Review-and-Action-Plan.md`. Its evidence and IDs
  (A1–A8, B1–B12, F01–F42, N01–N07) are used throughout the plan;
- the owner has decided that every dataset goes through all three stages (ADR 0007), and confirmed the two new lenses;
- prices, wages and living costs have been added (`abs_prices`);
- the inventor loader (`google_patents_inventors`) is written and tested, and waits on BigQuery access (below);
- TableBuilder is on hold: the owner is checking whether the project meets the ABS's conditions of use
  (`docs/tablebuilder-owner-managers.md`). The open stand-ins are in the plan;
- BLADE stays ruled out (the owner confirmed it). Small-firm outcomes are a stated limit of the research.

## Where things stand

- **Five lenses are built** (`analysis/eda/build.py`), in under a minute:
  - `rights`: 4,368,006 rows;
  - `firms`: 391,983;
  - `regions`: 2,641;
  - `national`: 127,309;
  - `timeline`: 1,473 months.

  Two more, `industries` and `institutions`, are planned (ADR 0007).
- **Every table now has a lens** to attach to; the map is in `docs/eda-plan.md`.
- **New source `abs_prices`:**
  - CPI, quarterly from 1948 and monthly from 2017, on one base (September 2025 = 100);
  - Selected Living Cost Indexes from 1998;
  - Wage Price Index from 1997;
  - Residential Property Price Index, 2002 to 2021.

  Every non-empty source value is kept, and each table has one row per key. It is not yet attached to a lens.
- **IP RAPID's individual names are pseudonymised codes.** In every role and right, no individual's name reads as words
  (867,756 individual parties checked). Gender can only be estimated for inventors, from Google Patents.
- **`google_patents_inventors`:**
  - one row per family and inventor (names in R2), with country and `p_female`, the estimated probability that the
    inventor is a woman, from WGND;
  - `family_inventors`: counts per family, no names (repo).

  A free dry run checks the query's size first, and the run stops above 250 GB. It has not run yet: the only key in
  this environment (`GCP_SA_KEY_B64`) belongs to a project with the BigQuery API switched off.
  `core.gcp_credentials()` now accepts that variable name as well as `GCP_SERVICE_ACCOUNT_JSON`.
- **The ChatGPT audit** (`docs/Aus-GII-Consolidated-Review-and-Action-Plan.md`) is background. The plan, and the review
  as re-sequenced by it, is the action list.
- **Corrected this session:**
  - the glossary had "lapse" and "ceased" the wrong way round. Lapsed rights were never granted, ceased ones were;
  - the data plan's IPLORD, WDI and PBS rows;
  - the plan, data plan, README and review, which said gender could be estimated from IP RAPID's names.
- **Tests:** 32 pass; lint is clean.

## Next, in order

1. **The `rights` lens's repairs:**
   - A2: a third "origin unknown" category;
   - A4: patents split into standard, provisional and second-tier;
   - keep every applicant's raw postcode, state and country.

   Record them, together with the other lens repairs, in one ADR (0008), then start the `rights` section of Stage 1.
   Add its attachments (events per right, parties, links, Google Patents, inventors) as sub-sections as each is built.
2. **The `timeline` lens's repairs:**
   - A3: coverage starts for each series;
   - B7: verify the four policy dates flagged `verify = true`;
   - attach `abs_prices` at quarterly resolution.
3. **`firms` (A1, A5, A6), `regions` (N03 rules, Census, CABEE), then `national` (A8):** in the order the plan gives.
4. **When BigQuery access works:** `uv run corpus run google_patents_inventors`. Check the logged given-name word and
   its match rate, then the estimates country by country, before attaching it to `rights`.
5. **If TableBuilder goes ahead and the files arrive:** move them to `data/raw/abs_owner_managers/`, write the loader (TableBuilder
   CSVs have title lines and a block per wafer), and check the totals against `abs_census`.
6. **The "data worth adding" list in the plan:** the RBA rates, ABS labour force and national accounts, and ATO
   postcode statistics are cheap, and fit the lens builds.

## Open items

1. Check in Stage 1:
   - whether the register drops provisional applications once a full application supersedes them (N01);
   - what `application_date` means for PCT filings (N06);
   - placeholder dates (1800, 1901 and 1970).
2. For the national lens, Australia's R&D series: use the OECD's (to 2023) beside the World Bank's, labelled; never
   splice them.
3. Fee history (R3) is the biggest data gap for Stage 3.

## For the owner

Nothing blocks Stage 1. Only you can do these:
1. **BigQuery access, for the inventors.** Either add the service-account key used for the earlier `google_patents` runs
   as `GCP_SERVICE_ACCOUNT_JSON` in the environment's settings, or switch on the BigQuery API in the Google Cloud
   project of the current key and give its service account the BigQuery Job User role. A new session picks up either.
2. **TableBuilder (on hold):** settle the registration route (IP Australia's ABS organisation) and whether IP
   Australia's rules allow ABS tables in this repository and R2. Then the six tables in
   `docs/tablebuilder-owner-managers.md` can be downloaded.

## Conventions to keep

- Commit the code, run the notebook, then commit the notebook with its outputs.
- Never print raw rows. Aggregate in DuckDB.
- Next free ADR: 0008.
