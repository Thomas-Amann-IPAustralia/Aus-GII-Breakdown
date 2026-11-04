# 0053: Two tests from IP Australia's research added to Stage 3 (M39, M40)

**Date:** 2026-11-04. **Whose:** the owner's (what: OQ27, answered A36, "lets add (a) and (b) to stage 3"); Claude's
(how), which the owner can overturn.

**Context.** The audit against IP Australia's published evidence (ADR 0052, section 11 of
`docs/audit-ip-australia.md`) left six observations "qualified" because IP Australia's findings measured something
they did not: its analytical note's lead of trade marks on real GDP (C13; B56, B63, M36 compared the same quarter), and
its commissioned study's "speeding up" of examination, which includes requests made early and unprompted (C3; M5
tested only expedited requests).

**Decision.**

1. **M40, notebook 3 section 1.11 (the study's measure).** A request is unprompted if IP RAPID's first request for
   examination is dated before any direction to request examination (its `exam_direction_to_request_exam` events).
   Granted standard patents, divisionals left out as the study left them, cohorts by the date of patent as M5; the
   same hazard model as M5, to 10 years from the date of patent, each patent entering at its grant, with the filer,
   field, route, cohort, co-filers, classes and expedited examination held, and within each filer group. The measure
   is checked against the study's share and joins the benchmark (`std_unprompted_exam_share`: 41.39% against 41.9%).
2. **M39, notebook 3 section 5.8 (the note's lead).** Quarterly trade mark applications and real GDP from the
   timeline, from 1983Q1 (the timeline's trade marks start then; earlier records are survivors, ADR 0014). In levels,
   as the note: log trade marks seasonally adjusted (STL), scaled by 1.11 from 1996 as the note does, Engle-Granger
   tests and GDP on two lags. In changes, as M36: year-on-year changes, GDP's growth on trade marks' growth one and two
   quarters before with GDP's own growth held, and the reverse, with Newey-West intervals, over 1983 to 2023 and
   the two periods of section 5.6.
3. **Only the new cells were run** (with the setup they need); every reviewed cell and output is unchanged.
4. **Results.** M40: the measure is reproduced, but those patents are more likely to end, held together (hazard ratios
   1.276 in FY2010 to FY2016, 1.383 in FY2003 to FY2009): the audit marks it **disputed in part** (the study's model is
   not published). M39: the shared path is found (p 0.018) and in levels the lead is the note's direction (3.069% and
   3.296% per 10%, against 1.8% and 2.7% over a longer window), but in changes, with GDP's own growth held, it is small
   (0.038) and not detected after 2008: **consistent; the size differs**.
5. **Carried to the atlas** (two Stage 3 pages, B13's and B56's pages showing them, "What Stage 3 found", the audit page
   and two glossary terms) and to the audit's record (section 11.8): 132 later observations, 231 in all.
6. **Not carried as signals.** M39 is recorded with B56. M40 joins M5 under the third early signal (what applicants
   ask for speed for); adding it to section 8's table is left to the owner's review of that table.

**Consequences.** IP Australia's commissioned study and the open data now disagree in direction on the study's own
measure; OQ28 proposes asking IP Australia how the study measured the renewal lifetime and what it held. The note's
lead is confirmed as a long-run relation, but adds little to GDP's own past as a predictor.
