# 0026: The atlas's framing pages follow the audit; its analyses wait for the owner

**Date:** 2026-10-27. **Whose:** the owner's (a clarification of ADR 0025), Claude's (the edits). Supersedes item 5 of
ADR 0025.

**Context.** ADR 0025 read the owner's "do not alter the atlas at this stage" as covering every existing page, so the
"What comes next" page kept the old wording of OQ5 and OQ7 and left out OQ12 to OQ14. The owner has since clarified:
the atlas may be updated with the changed wording; what is to stay unchanged for now is the substantive analyses.

**Decision.**

1. **Unchanged until the owner decides:** the observations (their plain English, figures, charts, trails, limits and
   the notebook they quote). The observations in `evidence/data/atlas.json` stay byte for byte as they were.
2. **Updated now:** the framing on the "What comes next" page (`analysis/atlas/content/site.yaml`, `next`):
   - the questions for IP Australia carry OQ5 and OQ7 as reworded (A10) and add OQ12 to OQ14 (A8);
   - the puzzles drop IP RAPID's innovation patents in 2016 (U67), closed by the audit, and say so; U45's puzzle says
     filing itself did not fall;
   - the leads gain the audit's pair (expedited examination against years in force, U34 and U36), and the provisional
     lead names IP Australia's reading rather than its figures, which the audit has benchmarked;
   - "IP Australia's own published statistics" leave the list of data worth adding, with a pointer to the audit page.
3. **Still waiting:** a pointer from each observation page to its verdict. It would sit on the analyses' pages, so it
   waits for the owner, with the revision of the observations themselves.

**Consequences.** The atlas's framing agrees with the record (`docs/owner-questions.md`, the audit) while the
analyses stay as Stage 1 left them. When the owner decides to revise observations, the notebook, their content, the
verdict pointers and the site change together (ADR 0023).
