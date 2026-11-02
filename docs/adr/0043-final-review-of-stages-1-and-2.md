# 0043: A final review of Stages 1 and 2: every observation against its outputs, and the audit's open findings

**Date:** 2026-11-02. **Whose:** the owner asked for an in-depth review of both stages before the website is updated:
correct any observation that is not a reasonable and objective description of the facts, make the two notebooks
agree where later datasets overtook earlier readings, and assess the stages' quality. Claude chose how. The record,
finding by finding, is pass 8 in `analysis/GPT-audit/261030/AMENDMENTS.md`; the assessment is
`docs/review-stages-1-and-2.md`.

**Context.** Seven audit passes had each taken one theme. Nothing had yet read every observation of both notebooks
against the outputs above it, re-run both notebooks from a fresh build, or checked the summary documents number by
number. What this review found:
1. **Both notebooks reproduce.** A fresh build of the eleven lenses and a re-run of both notebooks gave the same text
   outputs (notebook 2 identical; notebook 1 identical except two tables whose rows came in another order).
2. **The numbers are mostly right; some readings are not.** Of 186 observations, 68 are restated (31 of Stage 1's
   124, 37 of Stage 2's 62): 26 quoted a figure the output does not give (a stale count, a misread table, a rounded
   display taken as exact, a range across a break), 39 read further than the output allows (an absence from a weak
   correlation, a mechanism from a correlation, a cause from an association, a heading broader than its bullets,
   "file" for counts a crosswalk allocates), and 3 share one selection error (point 3).
3. **One selection effect moved a reading.** The firms lens holds an ABN only if it is in an IP, R&D, procurement or
   tax source, so the WGEA employers in none of them (2,616 of 9,742) were missing from U112's, B50's and B51's
   denominators. Over every employer the share with a filing linked is 48.6% to 72.9% by size, not 70.4% to 82.5%,
   and the gap by size doubles.
4. **The full Stage 2 audit's remaining findings hold.** Its open themes (what a count measures, US citations read as
   use, same-unit samples read as replications, weak associations written as absences, B38's break, B39's
   contradiction) were each checked against the notebook first; all hold.
5. **The summary documents lagged the notebooks** by more than the notebooks lagged their outputs (stale figures from
   before passes 2 and 6 in `docs/stage-1-summary.md`; over-strong lines in `docs/stage-2-summary.md`).

**Decision.**
1. **Every correction is a dated restatement where it is made** ("Restated (2 November 2026, pass 8; ADR 0043)"),
   with the earlier wording, as passes 1 to 7 did; summary rows and documents follow their observations.
2. **A figure quoted must be printed in full on the page.** Where a reading needed a number the page did not print
   (a year, an exact count behind a rounded display, an organisation's name), the cell now prints it; no new
   analysis beyond that, except where an output was wrong for its purpose (WGEA, below).
3. **Shares of WGEA employers are taken over every employer**, those outside the lens counted as having no filing
   linked; the lens's own shares stay beside them.
4. **Wording rules, applied in both notebooks and the summaries:** "no association detected" (with the interval where
   there is one) for a weak or uncorrected association, never an absence; "stability check" for a second sample of
   the same units; "allocated" for counts by division, keeping "file" for observed filers; a mechanism or a cause
   offered as a hypothesis. Both terms are in `GLOSSARY.md`.
5. **Not done here:** new methods the audit proposes (block bootstraps for serially dependent changes, 1,000
   resamples for quoted intervals, B42 and B60 through the crosswalk with services, heatmap legends, fixed-age
   citation windows, expenditure as an exposure for B62). They are listed for Stage 3 in the assessment.

**Consequences.** No lens changes. Notebook 1 gains printed figures in thirteen cells and a stable row order in two;
notebook 2 gains every-employer WGEA rates, full CABEE labels and B29's halves. Both re-executed. Readings that change
in substance: U8 (organisations' provisionals rose too), U112, B50 and B51 (the selection), B31 (patents are not shown
to be filed by manufacturers), B37 (seven of eight breaks), B38 (FY2022 to FY2024 the base), B39 (annual trade marks
move together), B46 and U85 (citations are not use), B62 (a shared denominator). The website's plain English
(`analysis/atlas/content/`) quotes several of these and is updated in the web pass.
