# 0018: The regions lens's attachments: every value of five area sources in one long table, and AusTender beside the core

**Date:** 2026-10-25. **Whose:** Claude's (the owner asked for the `regions` lens to be completed, 2026-10-25); the
owner can overturn any of it. It attaches the tables the plan maps to `regions` (ADR 0007): the Census, Data by Region,
CABEE, PHIDU, the Clean Energy Regulator and AusTender. The evidence is in `analysis/notebooks/01_univariate.ipynb`,
section 3.5 (observations U55 to U62).

**Context.** Every table must reach a lens and go through all three stages (ADR 0007). Five of the `regions` lens's
sources are wide: the 14 Census tables have 2,993 cells, Data by Region 774 items over 12 years, PHIDU 2,368
indicators, CABEE 260 business counts over three years and the Clean Energy Regulator 11 series over 26 years. As
columns of `regions` they would be about 8,900 columns, each needing a line in the variable register. Three of them are
published for areas other than postal areas: SA2s (Data by Region, CABEE) and PHIDU's Population Health Areas (PHAs,
one SA2 or a group of them).

**Decision.**
1. **One long table, `region_indicators`,** built with the lenses (`region_indicators_sql` in `build.py`): one row per
   postal area, source, indicator and period, with the value, its unit, whether it is a count (`additive`) and how it
   reached the postal area (`method`). It holds every value of the five sources for the lens's 2,641 postal areas:
   22,511,923 rows, 8,874 indicator-periods. Its columns, not its indicators, are in the variable register; each
   indicator keeps the publisher's own label. It is like the `national` lens (country, year, indicator), and is always
   queried with filters, never loaded whole.
2. **Counts and levels.** A count (people, businesses, installations, events) can be split and summed; a level (a
   median, mean, rate, ratio, percentage or index) cannot. The Census's medians and averages (G02) and its percentages
   (G43) are levels; Data by Region's by their unit (percent, decile, quartile, years, rate, density) or a label
   saying median, mean or average; PHIDU's by its measure (standardised ratios, age-standardised rates, percentages,
   rates, medians, averages). 99.43% of Census cells are counts, 57.43% of Data by Region's items and 45.86% of
   PHIDU's indicators.
3. **From SA2s and PHAs to postal areas,** through the 2021 residents of each mesh block (the ASGS file, which places
   every mesh block in one SA2 and one postal area): a count is split by the share of the area's residents in each
   postal area; a level is the average of the areas overlapping a postal area, weighted by the residents they share.
   An area with no residents is split by its mesh blocks instead (40 SA2s, holding 0.05% of CABEE's businesses). The
   Census and the Clean Energy Regulator are published by postal area or postcode, so they are used directly
   (`method` = direct).
4. **Left out:** PHIDU's confidence limits (an average of interval ends is not an interval), and CABEE's tables by
   state or local government area (DC02 to DC07, DC10 and DC11), which cover the same businesses as its SA2 tables and
   belong to the `industries` and `national` lenses. The Census's medians of 0 are empty, as in the core (ADR 0010).
   The Clean Energy Regulator's months are summed to calendar years; 2026 runs to September.
5. **AusTender, three columns of `regions`:** `austender_suppliers`, `austender_contracts` and `austender_value`, for
   contracts first published in FY2017 to FY2026 (the window of the IP counts), each once at its latest notice, by the
   supplier's postcode on the contract. 54,798 suppliers, 521,968 contracts, $590.4 billion (nominal, whole-life).

**Use.**
- Compare values within one indicator and period only. Never sum a level, never add a total to its parts (Census
  parts do not add exactly to totals: the ABS perturbs small cells, and males plus females equal persons in only 10.9%
  of postal areas), and never add one source's measure to another's (Data by Region repeats Census items, such as industry of employment
  and labour force status, for 2011, 2016 and 2021).
- Values from SA2s or PHAs are estimates for the postal area. They track the direct counts closely where both exist
  (Data by Region's 2021 resident population against the ASGS count: within 10% for 99.34% of postal areas of 1,000
  people or more), but CABEE's businesses are split by residents, not by where businesses are, so a business district
  inside a residential SA2 is understated. For counts of businesses by postal area use the ABR (`active_gst_abns`);
  CABEE's value is its size and industry split.
- CABEE counts about a quarter fewer businesses than the ABR has active GST-registered ABNs (ratio 0.742), with the
  same ranking (Spearman 0.988): two definitions, not an error. Never compare a CABEE count with an ABR count.

**Rejected.**
- **Columns in `regions` for every indicator** (about 8,900): unreadable, and the register would be generated rather
  than described.
- **A chosen few indicators in `regions`.** Choosing which matter is Stage 2's job; Stage 1 carries every value.
- **Splitting by the ABS's own correspondence file** (`poa_sa2`): it holds residents' shares only, with no fallback
  for SA2s without residents. The mesh-block weights give the same shares where there are residents (to
  within 0.001 for 5,901 of its 5,904 pairs).
- **Splitting CABEE by the ABR's businesses.** The ABR extract has postcodes, not SA2s, so it cannot weight within an
  SA2.

**Checked.**
- `tests/test_eda.py`: one row per postal area, source, indicator and period; CABEE's businesses split among postal
  areas sum to the SA2s' published total; no level is marked as a count; the Census's people match the lens's
  population to within 0.1% (25,369,823 against 25,365,506: perturbation).
- The lens as built: `regions` 2,641 rows and 42 columns (39 before, plus the three AusTender columns);
  `region_indicators` 22,511,923 rows and 10 columns, 173 MB, built in about 30 seconds.
