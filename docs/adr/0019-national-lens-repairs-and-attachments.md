# 0019: The national lens keeps former states and unknown origins, and holds its attachments in one long table

**Date:** 2026-10-26. **Whose:** Claude's (the owner asked for the `national` lens next, 2026-10-25 and 2026-10-26); the
owner can overturn any of it. It repairs the core lens and attaches the tables the plan maps to `national` (ADR 0007):
the GII, the OECD flows, WIPO's other tables, Measuring What Matters and Closing the Gap. The evidence is in
`analysis/notebooks/01_univariate.ipynb`, section 4 (observations U63 to U72).

**Context.** The core lens (ADR 0010) holds 30 indicators: the World Bank's 24, WIPO's filings by residents of each
country summed over every office (4), and the OECD's R&D intensity (2). It joined WIPO's origins to current ISO codes,
so filings by residents of former states (the Soviet Union, East Germany, Czechoslovakia, Yugoslavia, Zaire, the
Netherlands Antilles) and of unknown origin fell out: 9.65% of WIPO's patent applications by origin over 1980 to 2024,
and 56.94% of 1980's. The other national sources had not been attached: the GII 2026 (15,290 values), 24 OECD flows (42 million rows,
most of them dense grids of partner countries, industries and sizes), WIPO's filings at each office by origin, its
office table and its PCT, Madrid and Hague counts, Measuring What Matters (scraped tables) and Closing the Gap (three
targets).

**Decision.**
1. **Former states and unknown origins kept (core and attachments).** Former states keep their ISO 3166-3 codes (SUN,
   DDR, CSK, YUG, ZAR, ANT; the OECD's "former Yugoslavia" is YUG), and WIPO's unknown origin (`**`) is `ZZZ`. A new
   column, `entity`, says whether a place is a country, a former state or the unknown origin. A former state is
   never added to its successors. WIPO's applications by residents now sum to the source's total. Aggregates (regions,
   income groups, the OECD, the EU, the world, the rest of the world) stay out.
2. **One long table, `national_indicators`,** built with the lenses (`national_indicators_sql`): one row per place,
   source, indicator and period, with the value, its text where it is not a number, its unit and the publisher's flag.
   41,196,081 rows, 146,102 indicators, 264 MB. Its columns are in the variable register; each indicator keeps the
   publisher's labels. It is queried with filters, never loaded whole. Like `region_indicators` (ADR 0018).
3. **What goes in, by source.**
   - **The OECD:** every flow, one indicator per combination of its dimensions (`OECD.<FLOW>.<codes>`), country rows
     only. The regional patent table keeps its country rows (its regions are within countries). The two MSTI series in
     the core lens are not repeated. The OECD's "normal value" carries no flag; a suppressed value ("missing value;
     suppressed"), which it publishes as 0, is emptied and keeps its flag (536,278 values: 536,269 in business
     demography, 9 in innovation and IP methods).
   - **WIPO:** filings by origin summed over every office for every indicator and breakdown not in the core
     (`WIPO.ORIGIN.*`), except foreign-oriented patent families, which are counted at each office they reach, so a sum
     over offices would count a family more than once; filings at IP Australia by origin (`WIPO.AU.*`), for every
     indicator; the office table by the office's country (`WIPO.OFFICE.*`; regional offices such as the EPO are not
     countries and are left out); and the PCT, Madrid and Hague counts by origin (`WIPO.PMH.*`).
   - **The GII 2026:** each node's score, rank and screened value, and WIPO's strength and weakness flags
     (`GII.<node>.*`); each economy's population, GDP, income group and region (`GII.ECONOMY.*`). An indicator's year
     is its data year; a composite's is the edition's (2026). WIPO's "outdated" and "data minimum coverage" flags go to
     `status`. Nodes with no value (1,200 indicator rows) have no row.
   - **Measuring What Matters and Closing the Gap:** Australia's only. A Measuring What Matters table's first column
     is its period where it is one, otherwise the series' year if its name holds one. Closing the Gap's jurisdictions
     are breakdowns of Australia; its trajectories are marked "projected", its regression estimates "modelled" and its
     assessments as such, in `status`.
4. **Two corpus repairs, by reprocessing.**
   - **Closing the Gap:** target 15's "Aus Gov" column (land and sea held by the Australian Government) was not
     melted with the other jurisdictions, so it rode along as a side column on every row. It is now a jurisdiction (85
     values; 11,264 rows became 11,349), and the parser stops if a CSV has a column it does not know.
   - **Measuring What Matters:** two pages (feeling safe, health-adjusted life expectancy) stack males and females in
     one table under one header, so 45 cells shared a key, 9 of them with different values. Each block is now named by
     the prefix its series share (`block`), empty cells are no longer rows (184), and years read as decimals (2021.0)
     are written as years. 5,343 rows became 5,159, one per cell. A `reprocess` function rebuilds both from the raw
     files in the repo.
5. **The register's note on trade marks.** The World Bank's "trade mark applications, by count" count classes, as
   WIPO's class counts do (IP RAPID's Australian classes are 0.938 to 0.998 of the World Bank's count; its applications
   0.545 to 0.659, U67).

6. **Every build gives the same lenses (found while profiling).** Re-running the notebook on a fresh build changed
   a few figures in sections 1 and 3, because the `rights` build broke two ties arbitrarily: 1,686 founding applicants
   have two postcodes recorded on their first day (176 in different states), and 12,214 agents have more than one
   name (some are pseudonymised codes). A founder's tie now goes to the lowest postcode, and an agent's name is the one
   it is recorded under most often. The overview's "most common" value takes the smallest of tied values, and the
   notebook's queries that cut a ranked list break ties by name. Two builds now give the same `rights`, `firms`,
   `national`, `national_indicators` and `timeline`, row for row; `regions` and `region_indicators` differ only in the
   15th significant figure of sums of decimals (relative difference under 2e-14).

**Use.**
- Compare WIPO's series by country from 1995 only. Before then most offices did not report applicants' origins:
  29% to 34% of applications are of unknown origin to 1993, and 87% at IP Australia (U64), so a country's count is a
  floor.
- Filter `entity = 'country'` when comparing countries.
- In the OECD's cross-border patent tables, the "World" partner is the country's total, not a cross-border count
  (U71).
- Never read a Closing the Gap value with a `status` beginning "projected" as an observation. Measuring What Matters'
  monthly labour series copy the ABS's (`abs_labour`, `abs_prices`), which stay the main measures; its patent and
  trade mark counts copy WIPO's.
- `abs_rd_vc`, `bcarr_creative` and CABEE's national tables are mapped to `industries` and `national`; they join when
  `industries` is built, so that each is parsed once for both.

**Rejected.**
- **Columns for each attached indicator, or a chosen few.** As in ADR 0018: 146,102 indicators cannot be columns, and
  choosing among them is Stage 2's job.
- **Dropping the OECD's zeros.** 87% to 89% of the cross-border patent values are 0 (no patents with that partner that
  year); a 0 is a value, and a sparse table would read a missing pair as 0 anyway.
- **Mapping former states to their successors** (the Soviet Union to Russia). The successors did not exist as such,
  and the split of a former state's filings among them is unknown.
- **Summing WIPO's filings at every office by origin into the core for every indicator.** The core keeps its four
  totals; the rest are attachments, where their breakdowns live.

**Corrected.** The fixed tie-breaks move these figures, now corrected in the notebook (they were quoted from one
arbitrary build): filer and holder postcodes differ for 6.05% of standard patents and 6.82% of designs (U48: 6.03%,
6.81%); trade marks in postal areas 474,329 and 96.43% (U49: 474,339, 96.44%); the top tenth of areas file 60.8% of
trade marks (U52: 60.7%); trade marks per 10,000 people, 90th percentile 32.61 and Sydney's 2000 712.6 (U53: 32.66,
712.1); 72.5% of SA3s below the funnel for standard patents (U53: 72.8%). ADR 0017 keeps the figures of its date.

**Checked.**
- `tests/test_eda.py`: one row per key in both tables; WIPO's patent applications by residents in the core sum to the
  source's total; no aggregate is a place; the OECD's R&D intensity is not repeated; WIPO's filings at IP Australia
  sum to the office's total; Australia's GII rank is the source's; Closing the Gap keeps the Australian Government's
  values.
- The lenses as built: `national` 135,597 rows and 11 columns (135,140 and 10 before: 301 former-state and 156
  unknown-origin values, and `entity`); `national_indicators` 41,196,081 rows and 15 columns, built in about 15
  seconds.
