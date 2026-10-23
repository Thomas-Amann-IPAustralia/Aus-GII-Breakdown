# 0006: Add a fifth lens: Australia over time, one row per month

**Date:** 2026-10-23. **Whose:** the owner decided to add the lens; Claude chose its contents. This extends ADR 0002
(four lenses become five) and ADR 0005 (lens definitions).

**Context.** The owner asked whether "years" should be a lens. Time was already a column in every lens: filing year in
`rights`, year of first filing in `firms`, and year in `national`. Nothing, though, gave Australia's own story over time
with many measures side by side. That view is needed for three things:
- seasonal patterns;
- what happened around each IP policy change (the groundwork for the natural experiments that Q5 relies on);
- any later forecasting.

**Decision.** `timeline` has one row per month, from January 1904 to September 2026 (1,473 rows). It covers IP
Australia's whole register, Australian and overseas applicants alike. It is defined in `analysis/eda/build.py`
(`TIMELINE_*`) and described in `analysis/eda/variables.yaml`.

- **Why months rather than years.** 1,473 data points against 123. Monthly data also shows seasonal patterns and the
  rushes before a rule changes.
- **Applications** are counted by application date, from the `rights` lens:
  - standard patents, Australian and overseas;
  - provisional patents;
  - second-tier patents (petty, then innovation);
  - trade marks and designs, Australian and overseas;
  - plant breeder's rights.
- **Outcomes** are counted by effective date, from IP RAPID's events:
  - grants and registrations;
  - lapses, cessations and expiries;
  - oppositions (patents published from 2003; trade marks, including non-use removal);
  - pharmaceutical extensions of term granted;
  - ownership transfers (assignments) of patents and trade marks.
- **Policy changes.** `policy_events` holds the ids of the 13 changes that took effect in each month.
- **Before its records begin, a series is blank, not 0**, so that "not yet recorded" is not read as "none happened".
- **Left out:**
  - renewals, whose records stop in 2016 (designs) and 2018 (trade marks), so a monthly series would show a false
    collapse;
  - events IP RAPID marks `_historical`, which are dated on the day records moved between systems (670,560 trade mark
    registrations are dated 10 November 2018);
  - fees over time, because the corpus holds only today's schedule. This is a gap for the end of Stage 3.

**Checked.**
- The totals match the sources: 1,388,191 standard patent and 2,330,275 trade mark applications over the same months.
- All 13 policy changes are placed.
- The register matches the built table (`tests/test_eda.py`).

**Consequences.**
- Each notebook has a timeline section:
  - Stage 1, section 5: its overview has been run;
  - Stage 2, section 6: before-and-after comparisons, using changes rather than levels;
  - Stage 3, section 5: trend and season separated, and interrupted time series at each policy change, with placebo
    dates.
- **A caution carried into Stages 2 and 3.** Series that trend together over decades correlate whatever their
  connection. Comparisons over time therefore use changes, or the months around specific events, not levels.
