# Handover: exploratory data analysis

For the next Claude Code session. Read `CLAUDE.md` first, then `docs/eda-plan.md`.

**Status (2026-10-25):** Stage 1 has not started beyond its data overviews. Since the last handover:
- the corpus has had an independent review, `docs/Aus-GII-Independent-Review-and-Action-Plan.md`. Its evidence and IDs
  (A1–A8, B1–B12, F01–F42, N01–N07) are used throughout the plan;
- the owner has decided that every dataset goes through all three stages (ADR 0007), and confirmed the two new lenses;
- prices, wages and living costs have been added (`abs_prices`), and the Labour Force Survey (`abs_labour`), including
  owner-managers by sex, monthly from 1991;
- the inventors are loaded (`google_patents_inventors`), now that BigQuery access works. The first run nearly doubled
  the inventors, so each family's are now taken from one publication (ADR 0008);
- TableBuilder is on hold until a question needs postal-area detail. The owner pursues this exploration in a personal
  capacity and would register as a private user (`docs/tablebuilder-owner-managers.md`);
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
- **`google_patents_inventors` is loaded** (BigQuery, 12.1 GB scanned per run, inside the free monthly 1 TB):
  - `inventors` (R2, names): 4,131,009 rows, one per family and inventor, with country, `country_basis` and
    `p_female`, the estimated probability that the inventor is a woman, from WGND;
  - `family_inventors` (repo, no names): 1,548,276 families, 88.3% of `google_patents`' 1,753,104.

  Each family's inventors come from one representative publication (ADR 0008): counting every harmonised name across
  the family gave 5.13 inventors per family against 2.67 on the largest single publication. Countries are borrowed
  from the rest of the family, so only 13.2% are unknown (25.4% before). Given name: the second word (it matches WGND
  for 28.2% of distinct words, against 14.2% for the first). 85.1% of inventors have a gender estimate; the average
  probability of being a woman is 0.135 overall and 0.121 in Australia. China (0.336, 31.9% ambiguous) and Korea
  (0.321, only 52.2% estimated) look unreliable; check them before use.
- **The ChatGPT audit** (`docs/Aus-GII-Consolidated-Review-and-Action-Plan.md`) is background. The plan, and the review
  as re-sequenced by it, is the action list.
- **Corrected this session:**
  - the glossary had "lapse" and "ceased" the wrong way round. Lapsed rights were never granted, ceased ones were;
  - the data plan's IPLORD, WDI and PBS rows;
  - the plan, data plan, README and review, which said gender could be estimated from IP RAPID's names;
  - the inventor loader, whose first run counted each inventor about twice (ADR 0008).
- **Tests:** 27 pass and 5 skip; lint is clean.

## Next, in order

1. **The `rights` lens's repairs:**
   - A2: a third "origin unknown" category;
   - A4: patents split into standard, provisional and second-tier;
   - keep every applicant's raw postcode, state and country.

   Record them, together with the other lens repairs, in one ADR (0009), then start the `rights` section of Stage 1.
   Add its attachments (events per right, parties, links, Google Patents, inventors) as sub-sections as each is built.
2. **The `timeline` lens's repairs:**
   - A3: coverage starts for each series;
   - B7: verify the four policy dates flagged `verify = true`;
   - attach `abs_prices` at quarterly resolution.
3. **`firms` (A1, A5, A6), `regions` (N03 rules, Census, CABEE), then `national` (A8):** in the order the plan gives.
4. **The inventors, when `google_patents` attaches to `rights` (B4):** attach `family_inventors` with it. In its
   Stage 1 sub-section, check the gender estimates country by country against an outside benchmark (WIPO publishes
   women's share of inventors by country), above all China and Korea; for Korea, try joining the second and third words
   as the given name.
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
1. **TableBuilder, only if a question needs owner-managers by sex or Indigenous status for each postal area:** register
   as a private user, and check that the free Basic version has the variables (`docs/tablebuilder-owner-managers.md`).

## Conventions to keep

- Commit the code, run the notebook, then commit the notebook with its outputs.
- Never print raw rows. Aggregate in DuckDB.
- Next free ADR: 0009.
