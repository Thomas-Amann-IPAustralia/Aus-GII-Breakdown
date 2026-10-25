# 0017: The regions lens counts applications where the filer was, and shows a rate only where it is more than chance

**Date:** 2026-10-25. **Whose:** Claude's (the owner asked for the `regions` lens next, 2026-10-25); the owner can
overturn any of it. It carries out the switch that ADR 0013 set for this lens, the review's rules for small areas (N03,
B3) and its postcode check (S6, F05). The evidence is in `analysis/notebooks/01_univariate.ipynb`, section 3
(observations U48 onwards).

**Context.** The lens counted each right at the *current* holder's postcode, so a right sold to a firm elsewhere moved
with it. Its three rates divided ten years of filings, by individuals as well as organisations, by one count of
GST-registered businesses, in every postal area however small: 295 of the 2,641 areas have fewer than 50 such
businesses, and the highest rate was 4,917 per 1,000 (N03). And 4.1% of Australian postcodes in IP RAPID are not ABS
postal areas, with no account of which or why (F05).

**Decision.**
1. **Applications by the filer.** `patents_standard` to `designs` count the rights whose first founding applicant in
   Australia had this postcode (`founder_postcode`, ADR 0013), over FY2017 to FY2026. Where both postcodes are known,
   the filer's differs from the holder's for 6.03% of standard patents, 7.6% of trade marks and 6.81% of designs. The
   lens's standard patents rise from 24,841 to 25,180 (filers' postcodes are filled slightly more often), trade marks
   from 473,055 to 474,339, designs from 23,231 to 23,565.
2. **Organisations' counts beside them** (`patents_standard_by_organisations`, `trade_marks_by_organisations`,
   `designs_by_organisations`): individuals file 21.53% of standard patents, 24.97% of trade marks and 20.71% of
   designs, and the business denominator holds no individuals, so a rate per business uses organisations' filings only.
3. **Rates per year, per person and per business,** with a minimum (B3). Each rate is applications a year (the
   ten-year count divided by 10): per 10,000 people (every filing; the 2021 Census, near the middle of the window) and
   per 1,000 GST-registered businesses (organisations' filings; the ABR of October 2026). A rate is empty where fewer
   than 10 applications of its type would be expected at the national rate (`MIN_EXPECTED`): a Poisson count of 10
   has a 95% interval of about 4.8 to 18.4, so a smaller area's rate is mostly chance. For standard patents that means
   about 10,000 people; for trade marks about 530. Standard patents per person are shown for 850 areas (82.73% of
   people), trade marks for 2,094 (99.46%), designs for 812 (81.16%); per business, 650, 2,048 and 608.
4. **Pooling.** `sa3_code` and `sa3_name` give the SA3 holding most of each area's people (for 89% of areas, 90% or
   more of them), so Stage 2 can sum small areas into 335 SA3s; 324 of them expect 10 or more standard patents (99.8%
   of people). Stage 2 shows intervals (`uni.poisson_interval`) and, for maps, shrinks small areas' rates toward their
   SA3's or the nation's.
5. **The postcode check (S6).** A filer's postcode that is not a postal area is classed by Australia Post's ranges
   (`postcode_range` in `build.py`): post office box and large-volume ranges (1.39% of standard patents, 1.86% of trade
   marks); codes in a delivery range that the ABR also holds, which are real codes with no residents (4.14% of
   standard patents, 1.7% of trade marks), led by six universities' postcodes; and codes in no range or held by no one
   (0.02% or less). They are left out of the postal-area counts, and kept in the state totals of the `rights` lens
   (`founder_state`). No lookup assigns them to a place: the review's GeoNames trial waits for Stage 2 to show whether
   regional results are sensitive to them.

**Use.** Compare postal areas by their rates only where the rate is filled; for the rest, and for standard patents and
designs anywhere, use SA3s or shrunk rates. The variation between areas is far more than chance (two-thirds of areas
fall below the funnel's 95% limits for trade marks and standard patents, U52), so Stage 2 models counts with room for
that (negative binomial, not Poisson). Rates per person are highest in business districts with few residents (Sydney's
2000: 712 trade marks a year per 10,000 people, against a median of 8.48), and rates per business much less so (26.4
per 1,000, against 4.35); read both. A university's patents
are mostly outside the postal-area counts; the `institutions` lens counts them directly.

**Rejected.**
- **One minimum population or business count for every rate.** Patents are 20 times rarer than trade marks, so a
  minimum that steadies trade marks leaves patent rates as noise, and one that steadies patents hides most areas' trade
  marks. The minimum expected count adapts to each type.
- **Keeping rates for every area and flagging the small ones.** The review asks that no rate be shown without its
  denominator and interval; an empty rate cannot be mapped by mistake.
- **Dividing by the ABR's ABNs at the filing date.** The ABR extract holds only current statuses, so past business
  counts cannot be rebuilt from it.

**Checked.**
- `tests/test_eda.py`: the postal-area counts equal the window's rights with a filer's postcode in the lens; no
  organisations' count exceeds its total; no rate is shown below the minimum or hidden above it; the Poisson interval
  against known values; the postcode ranges.
- The lens as built: 2,641 rows and 39 columns (31 before, plus the two SA3 columns, the three organisations' counts
  and the three rates per person).
