# 0041: Survival is the share still in force, counted from grant; one rule for the halves

**Date:** 2026-11-02. **Whose:** the owner asked for the survival pass, with the fix to the halves (A23), and decided
how B8 is carried (A22); Claude chose how. The findings acted on, and the check of each, are in
`analysis/GPT-audit/261030/AMENDMENTS.md` (pass 6).

**Context.** The survival theme of the full Stage 2 audit (`analysis/claude-audit/261102/INDEX.md`: S2 L1 R11 to R15,
R30, R32 to R36; S2 L5 R04 to R06; S2 S8 R03, R05) and Stage 1's findings on it (S1 L0-L1 R20, R21; S8-S9 R10) were
checked against `build.py`, the lenses and both notebooks before anything changed. What the checks showed:
1. **What a curve's reading means differs by right.** 97% of patents' recorded ends fall 0.5 to 0.7 of a year past an
   anniversary (the end of the grace period); 95% of trade marks' fall on the anniversary itself. So "in force after
   10 years" is renewal through the ninth anniversary for a patent and renewal at the tenth for a trade mark.
2. **Cohorts and clock disagreed.** Curves ran from the date of patent, but cohorts were years of application, which
   for a PCT patent is national phase entry: the date of patent precedes it by a median 1.5 years for overseas filers
   (0.38 to 1.26 for Australian individuals), and 48% to 89% of a group's patents fall in a different financial year
   by the two dates.
3. **Immortal time.** A patent cannot cease before it is granted, yet each was counted from its date of patent: 62.8%
   of non-expedited patents of FY2003 to FY2009 were granted more than five years in, against 19.0% of expedited
   ones. This, with point 2, made B13's pattern: once corrected, expedited patents are slightly ahead in both
   periods, and neither "does not replicate" nor "Simpson's paradox" holds.
4. **Representation "at any time" includes the renewal.** IP RAPID's party records carry a start date (for trade
   marks, usually the registration date). Australian trade marks whose agent first appears more than 9.5 years after
   filing are 87.4% in force at 10 years: renewed through the agent who joined for it.
5. **The screen took unfinished lifetimes as finished** (`years_in_force` as a number), so B4's lifetime medians were
   not survival medians.
6. **U36's cohorts mixed regimes:** second-tier patents were split into petty and innovation by year (116 innovation
   patents of 1997 to 2000 counted as petty, 96 petty patents of 2001 as innovation), and designs of 2000 to June
   2004 (the Designs Act 1906) sat in a "2000s" cohort described under the 2003 Act.
7. **The halves were drawn two ways** (S2 S8 R07): DuckDB's hash in the screens and the notebook's SQL, pandas' in
   `split_half` and B35's GII split.

**Decision.**
1. **Survival is "the share still in force at N years"** (of granted or registered rights), with each right's dating
   convention stated beside it. Renewal decisions and value are interpretations needing other evidence (A1), never
   the reading itself. `GLOSSARY.md`'s "Lifetime" and "Ceased" are restated; "Share still in force at N years",
   "Immortal time", "Delayed entry" and "Patent Prosecution Highway" are added.
2. **The clock and the cohorts agree:** both run from the date the term runs from (a patent's date of patent; a trade
   mark's or design's earliest filing), as U36 did.
3. **Delayed entry:** each right joins a curve's count at its grant or registration (`univariate.kaplan_meier`'s
   `entered`), in both notebooks, with three guards: an entry is clamped to the right's own end or censoring (trade
   marks registered after the record of ends closes); the 629 rights recorded as ending before their own grant or
   registration (616 trade marks) are left out; and a curve starts once 30 are at risk (`start_at_risk`), so a few
   odd ends in an almost empty first month cannot move it (3 trade marks of the 2010s took a cohort to 85% before
   this). `kaplan_meier` refuses counts with more ended than at risk.
4. **Representation before the first renewal:** the rights lens gains `agent_first_date` (when an agent who is not an
   applicant or owner first appears); B10 reads representation before the renewal fell due beside the "any time"
   measure.
5. **The screen leaves out `years_in_force`** (kept `in_force`); B4's lifetime leads are read from curves by cohort.
6. **B8 is carried only within reach bands** (A22), date-of-patent cohorts FY2010 to FY2016 (reach reliable, B55),
   read beside B11 and B12.
7. **U36's cohorts by regime:** second-tier patents by recorded subtype; designs before 17 June 2004 apart.
8. **B49 is read with its checks:** a window by how each series is dated (months 1 to 12 for trade marks and designs)
   and a trend baseline beside the flat one; the anniversaries each patent change moved are named; "no response
   beyond placebo variation, at this design's power", never "a weak lever"; cessations, not lapses.
9. **One rule for the halves:** `bivariate.half_sql` (DuckDB's hash of the key as text, salted), used by the screens,
   the notebook's SQL and `split_half`, which now computes it in DuckDB; a test checks they agree.

**Consequences.** One lens column added (`agent_first_date`; the rights lens has 89 columns). Every survival figure
in both notebooks moves and is restated with a dated line. The readings that change: B8 is carried only within reach
bands, where Australian organisations' patents are more often in force among the wider ones and not among
Australia-only ones, so the gap is not the narrow patent's single set of fees, and the three signals disagree; B10's
representation gap is smaller read before the renewal (19.1 points, not 23.4); B13 has no composition effect and a
small link in both periods, with work-sharing requests mixed in since 2014; B49 has one change that survives every
check (trade marks, July 1993), not "only patents after September 2002"; U36's patent shares are 1 to 4 points lower.
The screen has 221 distinct leads (223). The halves' rerun changes no reading.
