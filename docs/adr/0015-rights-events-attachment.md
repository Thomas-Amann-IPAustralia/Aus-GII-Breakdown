# 0015: The events attachment: each right's milestones, and its lifetime with unfinished rights kept

**Date:** 2026-10-25. **Whose:** Claude's (the owner agreed to the events attachment next, 2026-10-25); the owner can
overturn any of it. It carries out the review's B5, which replaces the renewal records that stop (F25). The evidence
is in `analysis/notebooks/01_univariate.ipynb`, section 1.8.2 (observations U31 to U40).

**Context.** The `rights` lens said whether a right was granted and when it ended (`registered_date`, `retired_date`,
`status`), but not what happened in between or how long owners kept paying for it. IP RAPID's renewal publications
stop in 2016 (designs) and 2018 (trade marks), and patents have none, so the review proposed measuring how long rights
are kept from their end dates, counting rights still in force as unfinished (survival analysis). The timeline already
counts the same events by month (ADR 0010, 0014).

**Decision.** Eleven columns join the `rights` lens from `iprapid/events` (`RIGHT_EVENTS` in `analysis/eda/build.py`):
1. **Milestones,** each the first event of its kind:
   - `date_of_patent`: the date a patent's term runs from;
   - `exam_requested_date` (patents and designs, re-examination left out) and `exam_expedited` (true or false for
     every trade mark, and for every patent or design with a request);
   - `accepted_date` (patents, trade marks, plant breeder's rights), `certified_date` (innovation patents, designs);
   - `opposed_date`: an opposition to the grant or registration (patents from April 2003; a trade mark's application
     for removal for non-use is not one);
   - `assignment_count` and `first_assigned_date`: recorded transfers of ownership, each counted once a day;
   - `term_extended_date`: an extension of a standard patent's term granted.
2. **Which events count:** only those the register holds as *standing* (4.76% of patent lapse events are not, and
   60.47% of the patents with one are now granted, expired or ceased: the lapse was reversed); dated from 1904 to the
   corpus date (22 October 2026); not on 1 January 1970 (3,154 events, a placeholder); and, except the date of patent,
   not before the right's earliest filing (171 events, including 26 trade mark oppositions dated 1909).
3. **The lifetime:** `years_in_force` runs from the date the term runs from to `retired_date`, for rights that were
   granted or registered. The term runs from the date of patent; from a trade mark's or design's *earliest* filing date
   (for a Madrid mark, the international registration's: 92.19% of ceased marks whose two dates differ end a whole
   number of years after it, 1.65% after the application date); and from a plant breeder's right's grant. A right not
   ended by `OBSERVED_UNTIL` is unfinished (`in_force` true) and its years run to that date: 31 March 2026 for trade
   marks and designs, whose ends are recorded only after a six-month grace period (trade marks' recorded ends fall
   from 3,213 in March 2026 to 0 from May, as `TIMELINE_LAG` found), and 22 October 2026 for the rest.
4. **No lifetime** (both columns empty) where it cannot be measured: never granted; a status that ended the right with
   no end date (6,621 rights); or an end dated before the term began (26 rights).

**Owner's decision (2026-10-25):** years in force (U36) is adopted as a working measure for Stage 2, on condition that
it is used alongside other signals, never alone as a measure of value.

**Use.** Lifetimes are compared with survival curves (`uni.kaplan_meier`, from counts aggregated in SQL), within
cohorts that start where the register is complete (ADR 0014): patents by the year of their date of patent from 1980,
trade marks by earliest filing from 1983, designs from 1986. Milestone shares are compared only within the years each
is recorded (U32): patents' examination requests from the early 1980s' filings, trade marks' acceptances from the
mid-1980s, designs' examination requests from 2013. Trade mark `exam_expedited` is compared only on one side of
November 2018 (U34). For patents filed before FY2003, a change of owner is measured by `assignment_count` (U35), since
`holder_changed` is empty for them (ADR 0013).

**Rejected.**
- **A grant date from the events.** The grant event falls on `registered_date` for 99.99% of granted patents; a second
  column would repeat it.
- **Counting both publications of a patent assignment.** 99.78% of assigned patents have it published as an
  assignment and as a party change; the first is used, as the timeline does.
- **An end date from the events.** `retired_date` already agrees with the end event's date (checked while building: on the
  same day for 95.6% to 100% of each type and status), and is filled where IP RAPID has no end event.
- **Treating rights still in force as ended at the corpus date, or dropping them.** Either biases lifetimes down,
  most for recent cohorts.
- **Censoring every type at the corpus date.** Trade marks and designs that ceased from April 2026 are not yet
  recorded as ceased; counting them in force to October would overstate their survival.
- **Emptying lifetimes longer than a type's longest term** (104 rights, such as second-tier patents with a date of
  patent before their application). They are kept as recorded and named in `variables.yaml`.

**Checked.**
- `tests/test_eda.py`: no milestone outside 1904 to the corpus date, on 1 January 1970, or before the earliest filing;
  each column only on the types it describes; an assignment count exactly where a first assignment date is; a
  lifetime only for rights granted or registered, never negative, and with an end date wherever the right is not in
  force; and the survival helper against a hand count.
- The lens as built: 4,368,006 rows and 52 columns (29 core, 12 from the parties, 11 from the events). The other
  lenses are unchanged.
