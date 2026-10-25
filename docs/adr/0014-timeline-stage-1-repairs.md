# 0014: The timeline's series start where their records are complete, and the 1995 patent term change is an event

**Date:** 2026-10-25. **Whose:** Claude's, while profiling the `timeline` lens in Stage 1 (the owner asked for the
univariate analysis of the next lens to begin); the owner can overturn any of it. It changes ADR 0010's rule for where
a timeline series starts, and adds an event to the policy register checked in ADR 0011. The evidence is in
`analysis/notebooks/01_univariate.ipynb`, section 5.0 (observations U22 and U23), read from IP RAPID's own tables so
that it stays on the page after the repair.

**Context.** ADR 0010 starts each monthly series at the first month from which 9 of the next 12 have a record, so that
decades of scattered early records are not read as zeros. Profiling every series found that the rule starts 15 of
them too early. Before the dates below, IP RAPID holds one of three things, none of them a count of what happened in
the month:
- **Survivors.** IP RAPID holds only the rights still on the register when its records were computerised, not the
  applications that failed before then. By quarter of filing, 2.0% to 5.0% of trade marks filed in 1981 were never
  registered, rising through 1982 to 52.0% in the first quarter of 1983 (51% to 59% to 1988). Of designs filed in
  late 1985, 0.4% to 0.7%, against 26.3% in the first quarter of 1986. Provisional applications run at about 300 a
  quarter to mid-1985 and 1,372 in its last quarter. The 9-in-12 rule had started trade marks in April 1906.
- **Partial records.** Outcomes recorded for only some rights: grants for patents filed from 1979 (68.5% of them have a
  grant date, against 1.0% to 1.9% of those filed in 1976 to 1978); design registrations before designs filed from
  1986 are mostly registered; trade mark lapses (0 to 18 a month to September 1985, then 522) and cessations (to 1986);
  design cessations (rising through 1988, then a backlog in May and June 1990).
- **Batches.** Events dated on a few days a year, with empty months between backlogs. Patent cessations: 29.8% of the
  104 months from September 1986 to April 1995 are empty, and April 1995 holds 3,511; weekly from then. Patent expiries
  to December 1994 (29.4% of the series), then daily. Patent lapses to 1988, design lapses to 1993, and the first
  months of ownership transfers (patents to January 1992, trade marks to December 1986).

The same profile found that patent expiries fall from 289.5 a month to 4.67 in the year after July 1995 and resume in
July 1999. On 1 July 1995 the Patents (World Trade Organization Amendments) Act 1994 raised the standard patent term
from 16 to 20 years, for patents granted from then and for 16-year patents not yet expired (ss 2, 4 and 7), so
patents filed from July 1979 expired four years later. The policy register had no such event, and its note on the
Patents Act 1990 said that Act brought in 20-year patents; the 1990 Act's term was 16 years.

**Decision.**
1. **Fifteen hand-set starts** in `TIMELINE_START_OVERRIDE` (`analysis/eda/build.py`), each with its reason; earlier
   months are empty:

   | Series | Start | Why |
   |---|---|---|
   | `trade_marks_au`, `_overseas`, `_origin_unknown` | January 1983 | Survivors |
   | `designs_au`, `_overseas`, `_origin_unknown` | January 1986 | Survivors |
   | `patents_provisional` | September 1985 | Survivors |
   | `patents_granted` | January 1985 | Partial: grants of patents filed from 1979 only (99.4% of grants come within six years of filing) |
   | `designs_registered` | January 1988 | Partial: 90% of designs filed from 1986 are registered within 715 days |
   | `trade_marks_lapsed` | October 1985 | Partial |
   | `trade_marks_ceased` | January 1987 | Partial, then irregular in 1986 |
   | `designs_ceased` | July 1990 | Partial, then a backlog |
   | `patents_ceased` | May 1995 | Batches; April 1995 is the backlog |
   | `patents_expired` | January 1995 | Batches |
   | `patents_lapsed` | January 1989 | Batches |
   | `designs_lapsed` | January 1994 | Batches |
   | `patent_assignments` | February 1992 | Empty October to December 1991, then a backlog |
   | `trade_mark_assignments` | January 1987 | Empty October to December 1986 |

   Standard patents keep their starts: for the numbers issued in 1970 to 1972 and 1975 to 1979, IP RAPID holds about
   one standard patent for every number in each year's range, so it lost no failed applications; what it lacks is
   their outcomes before 1979 (U9).
2. **A 17th policy event,** `patent-term-20-years` (1 July 1995, lever "term"), checked against the 1994 Act as made
   (Federal Register C2004A04827), and the note on `patents-act-1990` corrected to "16-year standard patents, 20 years
   from 1 July 1995". `corpus reprocess policy_events` rebuilt the table.
3. **The rights lens is unchanged.** Its rows are real rights; only counts by year of filing are affected.
   `variables.yaml` says so on `filing_fy`, and section 1's U5 and U10 carry a correction.

**Rejected.**
- **A generic rule in place of hand-set starts** (for example, a level that a series must reach, or a minimum number
  of days a month with events). Each fails somewhere: a level test cannot tell partial records from real growth, and a
  days test empties small series whose quiet months are real. Hand-set starts, each with its evidence, are easier to
  check.
- **Keeping the early months with a flag.** A flag would be ignored by anyone summing a column; empty is what ADR 0010
  chose for "not recorded".
- **Emptying the months after July 1995 for patent expiries.** Their fall is real (the term change).
- **Emptying later pauses and backlogs** (trade mark registrations in January and March 1996, patent grants in June
  1991, patent cessations in February and March 2020). They sit inside complete records and two follow a change of
  law; Stage 2 pools each pause with its backlog (U29).
- **Starting trade mark oppositions later.** They rise from 0 to 16 a month (1983 to 1987) to 20 to 40 (1988), with no
  sign of how they were recorded; the rise may be real.

**Checked.**
- `tests/test_eda.py`: each hand-set start is where its series begins; inside a series' span no month falls below a
  twentieth of the two years around it (where those run at 100 or more a month), except two named pauses.
- `tests/test_corpus.py`: the new event's date.
- The lens as built: 1,473 rows and 35 columns (unchanged in shape).
