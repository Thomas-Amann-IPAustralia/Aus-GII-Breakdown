# 0040: Ownership is read at two endpoints, not as a history of transfers

**Date:** 2026-11-02. **Whose:** the owner asked for the next audit theme (A21); Claude chose how. The findings acted on,
and the check of each, are in `analysis/GPT-audit/261030/AMENDMENTS.md` (pass 5).

**Context.** The audits' theme "recorded ownership changes read as complete ownership histories" (S1 L0-L1 R16, S8-S9
R07, S2 L1 R25, R26, S2 L2 R19) and two findings on the same analysis, B26 (S2 L2 R18, R20), were checked against the
lens definitions and both notebooks. All seven hold. What the data hold:
1. **Origin at two endpoints.** `founding_australian` (a founding applicant in Australia) and `australian_applicant`
   (a current applicant in Australia) are two snapshots. "Australian-founded, now held only overseas" says nothing of
   the holders in between, of a return to Australia, of where an invention is used or of where its returns go.
2. **Holder changes are differences in recorded parties.** `holder_changed` compares party ids; a sale, a merger, a new
   legal entity and some changes of name all count, and the date is not known. A different postcode can be a new
   address of the same party.
3. **Assignments before FY2003 have unknown coverage.** From FY2003, 64.68% to 74.66% of recorded holder changes have an
   assignment; for earlier patents the holder history cannot be seen, so that share cannot be checked there. The
   assigned share running on smoothly across FY2003 shows consistent recording, not coverage.
4. **Rates are not composition.** B19's overseas-held rate is highest among wide patents (14.52%, FY2003 to FY2011),
   but 44.22% of that period's overseas-held patents are single-office ones. Reach and grant are seen today, not before
   the holder changed.
5. **The unit in B26 is the patent.** Firm-level counts change the reading: the youngest firms 4.34% against 3.63%
   (FY2003 to FY2011) and 2.96% against 3.33% (FY2012 to FY2021); one firm holds 44.26% of one band's overseas-held
   patents. Reach unknown was counted in denominators without being shown; marginal reach shares do not rule it out.

**Decision.**
1. **Endpoint language.** "Australian-founded, now held only overseas" (or "no Australian holder now"), never
   "moved", "left" or "exported"; "recorded holder differs from the filer", not "transferred". Value, use and returns
   are questions for Q1, not observations.
2. **Assignments before FY2003** are an incomplete indicator of a change of owner, with unknown coverage, not a
   measure calibrated at two-thirds.
3. **Show both readings** of a grouped rate: the rate within each group and the composition of the outcome across
   groups, with unknowns counted apart.
4. **Firm-level outcomes beside patent-level ones** where patents cluster in firms, with each band's concentration
   in its largest firm; patent-level Wilson intervals are labelled as treating patents as independent.
5. **Name the join.** B26 joins by `filer_abn`, the first founding applicant with an ABN; for a jointly founded patent
   (4.56% of B26's) it need not be the Australian party.

**Consequences.** No lens changes. U17 to U19, U35, B19, B26 and B46 are restated, with the summaries; B19 and B26 gain
a composition table and firm-level counts. B26's lead is weaker again: by firm, the youngest firms show no clear
difference in either period. The analysis of "value created here and realised abroad" stays a Stage 3 and Q1
question, with ownership, use and returns to be measured separately if the data allow.
