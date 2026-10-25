# 0009: Repairs to the `rights` lens: three-valued origin, patent types, and raw applicant location

**Date:** 2026-10-25. **Whose:** Claude's, carrying out repairs A2 and A4 of the independent review
(`docs/Aus-GII-Independent-Review-and-Action-Plan.md`) and the plan's "keep every applicant's raw location"; the owner
asked for the repairs and can overturn the details. This changes ADR 0005 (lens definitions) and ADR 0006 (timeline
contents). The other lenses' repairs (A1, A3, A5, A6, A8, N03) will get their own ADRs as each lens's turn comes.

**Context.** The review found three problems that would distort the `rights` section of Stage 1 and the lenses built on
`rights`:
- IP RAPID's `any_applicant_in_australia` turns "no applicant country recorded" into "not Australian". 517,145 patents
  have no applicant country, almost all filed before 1990, so the timeline's "overseas" standard patents included
  decades of rights of unknown origin (F04).
- `firms` and `regions` added every patent sub-type together. A provisional application is usually followed by a
  standard application for the same invention, so one invention counted twice, and provisionals are 60% of the
  regional patent records (N01).
- The lens kept an applicant's postcode only when the first applicant was Australian, and only cleaned to four digits,
  so overseas postcodes and every applicant after the first could not be reached (F03).

**Decision.**
1. **Origin has three values (A2).** `australian_applicant` is computed in `build.py` from every current applicant in
   `iprapid/party` (the same applicants IP RAPID's `*_rights` tables use): true if any is in Australia; false if at
   least one has a known country and none is in Australia; empty (origin unknown) if no applicant has a country. The
   review's shorter proxy (looking only at the first applicant's country) was not needed. The timeline adds
   `patents_standard_origin_unknown`, `trade_marks_origin_unknown` and `designs_origin_unknown`, and its overseas series
   now count only known overseas applicants.
2. **Patents are typed (A4).** `rights.patent_type` is `standard` (IP RAPID's `standard_complete`), `provisional` or
   `second_tier` (innovation and petty). `firms.n_patents` becomes `n_patents_standard`, `n_patents_provisional` and
   `n_patents_second_tier`; `regions.patents` likewise, and the regional rate becomes
   `patents_standard_per_1k_businesses`. The three are never added together.
3. **Raw applicant location.** `rights` keeps the first applicant's postcode as recorded, in any country
   (`applicant_postcode_raw`), beside the cleaned Australian `applicant_postcode`. It adds every current applicant's
   country (`applicant_countries`) and the numbers of applicants in Australia, overseas and of unknown country. Each
   applicant's full address stays in `iprapid/party`, reached by application number; the lens keeps one row per right.

**Not done, and why.**
- Re-profiling past and founding applicants to recover countries (the review rejected it, and the data agrees): taking
  every applicant ever recorded, not just current ones, leaves 517,096 patents with no country instead of 517,145.
- The attorney's country is never used as a stand-in for the applicant's.
- The `coalesce` in `iprapid.py` that creates the problem is left until IP RAPID is next rebuilt, so the code matches
  the committed data. The lens no longer reads that column.
- Locating overseas postcodes (an international postcode lookup) waits until a question needs it.

**Checked (descriptive).**
- `rights` still has 4,368,006 rows, one per application number. For every right, applicants in Australia, overseas and
  of unknown country add up to `applicant_count`, and `australian_applicant` follows the rule above (a test checks
  both).
- Origin before and after: no right changed from true to false or back. The only change is false to unknown: 517,145
  patents, 40,726 designs, 37,656 trade marks and 40 plant breeder's rights.
- Standard patents of unknown origin, by decade of application: 99.7% to 100% from the 1900s to the 1960s, 96.6% in the
  1970s, 51.9% in the 1980s, 0.3% in the 1990s and 0.1% or less since 2000. Australian applicants' share of standard
  patents with a known origin is 11.5% in the 1990s and 8.5% in the 2020s. Before 1980 the known-origin counts are too
  small (2 to 3,297 a decade) to give a share.
- The timeline's totals are unchanged: Australian, overseas and unknown standard patents add up to the 1,388,191 that
  Australian and overseas did before; likewise for trade marks (2,330,275) and designs (257,259).
- Firms: 286,383 patent applications split into 185,802 standard, 89,961 provisional and 10,620 second-tier.
- Regions (FY2017–FY2026): 77,911 patent applications split into 24,841 standard, 46,390 provisional and 6,680
  second-tier. The median postal area's patent rate falls from 8.29 to 1.34 per 1,000 GST-registered businesses.
  Provisionals in FY2026 number 9,542, against 3,794 to 5,124 a year in FY2017–FY2025 (N01).
- Raw postcodes: 596,510 of the 1,912,138 rights whose first applicant is overseas now keep a postcode (31.2%).
