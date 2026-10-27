# 0027: OQ6, OQ7 and OQ13 rechecked on a fresh release; the questions for IP Australia are sharpened

**Date:** 2026-10-27. **Whose:** the owner asked for the recheck; Claude decided how to do it and drafted the
rewording. Adopting any of it as a conclusion is the owner's decision.

**Context.** Before taking OQ6, OQ7 and OQ13 to IP Australia, the owner asked for a check on a fresh IP RAPID release
that each one is not a misclassification.

**Decision.**

1. **The recheck is independent of the corpus.** `analysis/audit/recheck.py` downloads the current release from
   data.gov.au (26 October 2026) and reads its CSVs as published, with no typing, repairs or lens logic. It writes
   each check to `analysis/audit/output/recheck/`, and `docs/recheck-oq6-oq7-oq13.md` gives the observations (R1 to
   R15). It reproduces the Stage 1 and audit figures (U34, U45, D2).
2. **OQ6 is mostly a recording change, as far as the data can show.** From FY2009 to FY2018, 95.97% to 97.81% of
   trade marks claiming convention priority carried an expedite event, and 0.06% to 0.16% have since FY2020. For
   marks without a priority claim, the share was 4.81% to 6.11% and is now 3.60% to 4.87%, with no break. The
   question now asks whether the old system recorded those marks' handling under the expedite code.
3. **OQ13: WIPO sides with IP RAPID** (added the same day, when the owner asked for a WIPO search). WIPO's count of
   designations of Australia in 2018 is 15,943, and IP RAPID holds 15,836 Madrid marks (0.9933). Every year from 2014
   to 2024 is within 1.2%, apart from 2023. The IP Report 2019 implies about 17,830 (1.118 of WIPO's count). So the
   2018 count in that report is probably the odd one out, not IP RAPID. Trade mark numbers 1,978,060 to 1,980,352
   (2,292 numbers, issued around New Year 2019) are missing from every IP RAPID table, but WIPO's count weighs against
   their being the missing marks. The question now asks what the IP Report 2019's 2018 count included. WIPO's
   register (Madrid Monitor) is not searched mark by mark: its terms forbid automated queries and bulk downloads.
4. **OQ7 is not a misclassification.** The ABN goes missing from July 2024, mostly for applicants new to IP Australia.
   For trade marks from companies under a year old, the share with an ABN fell from 89.0% to 90.2% (FY2022 to FY2024)
   to 10.1% (FY2026). 80.0% of FY2026's no-ABN company filers match an ASIC company that has an ABN. Marks filed in
   July 2024 have not gained ABNs since. The question now asks what changed in July 2024 for new customers.
5. **No observation is revised.** U34, U45 and D2 stand, and so do their meanwhile rules, until the owner decides
   (ADR 0026). If the owner adopts R5, U34 could compare trade mark expedite shares across 2018 among marks without a
   priority claim.

**Consequences.** The questions in `docs/owner-questions.md` and the atlas's "What comes next" page carry the sharper
wording. The old wording is kept in each row. If IP Australia confirms R5 or R10, U34 and D2 can be closed. The
recheck reruns in minutes against any later release.
