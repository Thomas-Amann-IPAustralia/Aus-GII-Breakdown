# Handover: exploratory data analysis

For the next Claude Code session. Read `CLAUDE.md` first, then `docs/eda-plan.md`.

**Status (2026-10-25):** Stage 1 has not started beyond its data overviews. Since the last handover:
- the corpus has had an independent review, `docs/Aus-GII-Independent-Review-and-Action-Plan.md`. Its evidence and IDs
  (A1–A8, B1–B12, F01–F42, N01–N07) are used throughout the plan;
- the owner has decided that every dataset goes through all three stages (ADR 0007);
- prices, wages and living costs have been added (`abs_prices`).

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
- **The ChatGPT audit** (`docs/Aus-GII-Consolidated-Review-and-Action-Plan.md`) is background. The plan, and the review
  as re-sequenced by it, is the action list.
- **Corrected this session:**
  - the glossary had "lapse" and "ceased" the wrong way round. Lapsed rights were never granted, ceased ones were;
  - the data plan's IPLORD, WDI and PBS rows.
- **Tests:** 31 pass; lint is clean.

## Next, in order

1. **The `rights` lens's repairs:**
   - A2: a third "origin unknown" category;
   - A4: patents split into standard, provisional and second-tier;
   - keep every applicant's raw postcode, state and country.

   Record them, together with the other lens repairs, in one ADR (0008), then start the `rights` section of Stage 1.
   Add its attachments (events per right, parties, links, Google Patents, gender) as sub-sections as each is built.
2. **The `timeline` lens's repairs:**
   - A3: coverage starts for each series;
   - B7: verify the four policy dates flagged `verify = true`;
   - attach `abs_prices` at quarterly resolution.
3. **`firms` (A1, A5, A6), `regions` (N03 rules, Census, CABEE), then `national` (A8):** in the order the plan gives.
4. **The "data worth adding" list in the plan:** the RBA rates, ABS labour force and national accounts, and ATO
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
1. ABS TableBuilder (free registration) for Census owner-managers.
2. A decision on whether to reopen BLADE.

## Conventions to keep

- Commit the code, run the notebook, then commit the notebook with its outputs.
- Never print raw rows. Aggregate in DuckDB.
- Next free ADR: 0008.
