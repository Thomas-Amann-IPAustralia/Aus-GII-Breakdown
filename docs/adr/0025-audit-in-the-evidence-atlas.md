# 0025: The audit against IP Australia, shown in the evidence atlas beside the observations

**Date:** 2026-10-27. **Whose:** the owner's (show the review in the atlas; do not, at this stage, alter the notebook
or the atlas's existing pages), Claude's (how); the owner can overturn the how.

**Context.** ADR 0024 audited Stage 1's observations against IP Australia's published evidence and recorded the
verdicts in `docs/audit-ip-australia.md`. The owner asked for the review to be pushed to the repository and shown in
the evidence atlas (ADR 0023), without altering the notebook or the atlas at this stage. Read together: the review
appears in the atlas, and nothing already there changes.

**Decision.**

1. **A page of its own.** The atlas gains one page, "Checked against IP Australia" (`#/audit`), and one link to it in
   the navigation, under Honesty. No observation page, lens page, question page, the overview, the glossary or the
   notebook changes: the observations in `evidence/data/atlas.json` are byte for byte as they were (checked when it
   was built), and the review sits under a new key, `audit`.
2. **Built from the record, not copied.** `analysis/atlas/audit.py`, called by `python -m atlas.build`, reads:
   - each observation's verdict from the record's tables (`docs/audit-ip-australia.md`, sections 5.1 and 5.2), so
     the page cannot drift from the record;
   - the benchmark's outputs (`analysis/audit/output/`), for the table of measures and four charts (the verdicts,
     every published count against Stage 1's, Australians' designs, trade marks by year);
   - plain English in `analysis/atlas/content/audit.yaml`: a note for each observation the review could test, the
     four discrepancies, IP Australia's conclusions, what changes and the limits.
3. **The numbers rule, again.** Every number in the plain English must appear in the record or in the benchmark's
   outputs, or the page is not built; every observation the record tests needs a note; every observation has exactly
   one verdict (tested in `tests/test_audit.py`, with the charts kept in step).
4. **The page says what it is not.** Its banner says the observations are unchanged and that revising one is the
   owner's decision; IP Australia's conclusions are shown with the strength IP Australia gives them, none adopted.
5. **Known gaps left as they are, by instruction:** the "What comes next" page still lists OQ5 to OQ7 only for IP
   Australia (OQ12 to OQ14 are on the new page), and observation pages carry no pointer to their verdict.

**Consequences.** Readers of the atlas can see how each observation stands against IP Australia's evidence, follow it
to the observation, and see IP Australia's evidence as the record gives it. When the owner decides to revise
observations in the light of the review, the notebook, the content and the site change together, as ADR 0023 requires,
and the "What comes next" page and per-observation pointers can follow then. The page goes live only when the branch
reaches the one Pages serves (the owner's call).
