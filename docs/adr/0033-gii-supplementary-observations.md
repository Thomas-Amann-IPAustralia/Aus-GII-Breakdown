# 0033: Supplementary observations for the GII indicators blank for Australia, beside the official release

**Date:** 2026-10-29. **Whose:** the owner asked for the data gaps to be filled (A15, `docs/data-gaps-brief.md`, gap
B7; F17); Claude chose the sources and the method.

**Context.** GII 2026 leaves six indicators blank for Australia (U69): 2.1.5 pupil-teacher ratio, secondary; 2.3.1
researchers, FTE per million people; 4.1.3 loans from microfinance institutions; 5.1.5 GERD financed by business;
5.3.6 research talent in businesses; 6.1.3 utility models by origin per billion PPP$ GDP. The blanks are in WIPO's own
file, not lost by the loader (F17). The review's advice: keep the official release exactly as published, and put any
substitute in separate rows with its source, year, definition difference and status.

**Decision.**

1. **The GII's own rows are not touched.** Supplementary values go to `national_indicators` as the source
   `gii_supplementary` (dataset `gii_2026`, indicators `GIISUP.<GII code>`), each with a `status` beginning
   "supplementary (not in the GII)" and saying how it differs. No rank or score is recalculated.
2. **Four are filled from Australia's own statistics:**
   - **2.1.5** from a new source, `abs_schools` (ABS Schools, Table 53a): full-time equivalent students per full-time
     equivalent teaching staff in secondary schools, all affiliations, every year from 2006 (11.7 in 2025). UNESCO,
     the GII's source, counts heads, so the levels are close but not the same measure.
   - **2.3.1, 5.1.5 and 5.3.6** from the ABS's four R&D surveys already in the corpus (`abs_rd_vc`): business
     (2023-24), higher education (2024), government and private non-profit (2024-25). Their sum stands in for GERD,
     each sector in its own survey year, as the ABS itself publishes no newer all-sector total. Researchers are
     person-years of effort; in higher education, academic staff and postgraduate students (the OECD's definition).
     GERD financed by business counts business funds in every sector and leaves out government R&D's "joint
     business-government" funds. Population for 2.3.1 is the World Bank's for 2024 (`wdi`).
3. **Two stay blank.** 4.1.3: no Australian series of microfinance lending exists; program reports would be partial.
   6.1.3: WIPO's counts of utility models by origin are in the corpus (128 Australian in 2024), but the GII's
   counts could not be reproduced: WIPO's utility models over its patent applications by origin, times the GII's own
   patents by origin per billion PPP$ GDP (6.1.1), misses the GII's published 6.1.3 by a median 31% to 46%
   (whichever of four data years is assumed) for the 64 to 66 countries with both, so an Australian value would not
   be comparable.

**Consequences.** The supplementary values let Australia's R&D and schooling be read beside other countries on the
GII's definitions, approximately. They are context for Q1 and Q4, not inputs to any GII rank, and Stage 3 cites them
as "supplementary".
