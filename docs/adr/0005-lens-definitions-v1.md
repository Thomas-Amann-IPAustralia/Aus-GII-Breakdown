# 0005: How the four lenses are defined (version 1), and their known limits

**Date:** 2026-10-23. **Whose:** Claude's; Stage 1 may revise them through a new ADR.

**Decision.** The definitions are in `analysis/eda/build.py`, and every column is described in
`analysis/eda/variables.yaml`. The choices that shape later results:

- **`rights` (4,368,006 rows).**
  - The four `iprapid/*_rights` tables stacked, with the type of right added. The count matches the sources exactly,
    with no repeated rights.
  - Postcodes are kept for Australian applicants only, cleaned to four digits.
  - The ABN is IP RAPID's `any_applicant_abn` (the first applicant with an ABN).
  - The financial year runs July to June.
- **`firms` (391,983 rows).**
  - The corpus's ABN spine. It holds the ABNs that appear in IP RAPID, IPLORD, the R&D Tax Incentive, AusTender or
    the tax transparency reports: *not all Australian businesses*. A rate computed on it is a rate among these ABNs.
  - A right is credited to one ABN, the first applicant with an ABN. `ip_filed_total` (IP RAPID's own panel, which
    splits shared rights) is kept beside the counts.
  - R&D is the average and the latest year of 2021-22 to 2023-24. Income is the latest year in the tax reports.
  - The place is the remoteness area and IRSAD decile of the firm's postcode.
- **`regions` (2,641 postal areas).**
  - Based on the ABS postal areas, less the four non-geographic codes.
  - IP applications are by Australian applicants in the ten latest complete financial years, FY2017 to FY2026.
  - The business denominator is active, GST-registered ABNs.
- **`national` (127,309 rows).**
  - 22 World Bank indicators for every country (regional aggregates left out).
  - WIPO's applications and grants by residents of each country, summed over every office, so they include filings
    abroad.
  - Flags mark OECD members and Australia.

**Known limits, to test in Stage 1.**
- The first applicant stands in for the whole right.
- About 80% of patent rights have no Australian postcode, because their applicants are overseas.
- Postal areas with no residents produce zero or undefined rates.
- WIPO counts (filings by residents at every office) and WDI counts (filings at the national office) measure
  different things.

**Checked.**
- Row counts match their sources, with one row per key.
- 98.9% of firms have a remoteness area and 98.6% an IRSAD decile.
- Census medians cover all 2,641 postal areas, and SEIFA 99.4%.
- The populations sum to 25,365,506.
