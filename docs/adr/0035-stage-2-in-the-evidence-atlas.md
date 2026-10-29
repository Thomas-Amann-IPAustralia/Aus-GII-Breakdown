# 0035: Stage 2 in the evidence atlas

**Date:** 2026-10-29. **Whose:** the owner asked for the website to show all of Stage 2's findings and changes (A16,
answering OQ19's first part); Claude chose how.

**Context.** The evidence atlas (`evidence/`, ADR 0023) held Stage 1's observations as they stood on 27 October
(U0 to U107). Since then Stage 2 added B1 to B62 (`analysis/notebooks/02_bivariate.ipynb`, ADR 0030), and filling the
data gaps added sixteen Stage 1 observations (U108 to U123) and new sources. The owner had asked that the website wait
until Stage 2 was finished (A14); the test of the atlas skipped while the notebooks were ahead of it.

**Decision.**

1. **One atlas, two stages.** `atlas.notebook` reads both notebooks (`read_all`), and every observation carries its
   stage. Stage 2's plain English is in `analysis/atlas/content/observations/stage2/`, one file per lens, with the
   same fields as Stage 1's; the build refuses a Stage 1 observation in that folder or a Stage 2 one outside it.
   References to Stage 2 observations are written `{B6}`, as Stage 1's are `{U44}`.
2. **The numbers rule is unchanged.** Every number in a Stage 2 page's headline, statement, figures, points and quoted
   chart is on that observation's page of the Stage 2 notebook (its text or the outputs above it). Writing the pages
   found nothing in the notebooks to correct.
3. **Charts are quoted, not redrawn.** Stage 2's observations are pairs, intervals and model ratios that the notebook
   computes on samples; redrawing them from the lens tables would repeat the notebook's work. So 30 of the 62 have a
   small chart of numbers the observation quotes (checked by the numbers rule), and the 31 with charts in the
   notebook show them under "For analysts" as Stage 1's do. Of the sixteen new Stage 1 observations, 11 have quoted
   charts and 4 the notebook's.
4. **The pages show the stage.** A stage filter on the observations page, a stage chip on every card, the stage and
   the right wording for its strength on each observation page, lens pages grouped by stage, question pages listing
   Stage 2's evidence first, and "What comes next" giving Stage 3's tests (from `docs/stage-2-summary.md`, section 4)
   in place of Stage 2's.
5. **The framing pages say what Stage 2 adds.** The overview has a "What Stage 2 found" section of ten signals; the
   limits page adds what pairs cannot show (causes, people from places, small units); the lenses list the sources
   added while filling the gaps; the review against IP Australia's evidence notes that its pair for Stage 2 (C3) is
   done ({B13}).

**Corrections made on the way.**

- The published "What comes next" page did not render: one question to IP Australia (OQ13) held a colon, so YAML read
  it as a mapping and the page stopped with an error. It is quoted now, and a test checks that those lists hold only
  text.
- U23's figure "17th" policy change was no longer on its notebook page, whose outputs now count the fee changes too;
  the figure now gives the change itself (the patent term, 16 to 20 years).
- The rights lens's page gave 4,368,006 rights, the count before the 11,098 empty design records were dropped
  (ADR 0029); it now gives U1's 4,356,908, and 86 columns rather than 74.

**Consequences.** The atlas is a plain-English record of both stages, and the test of it runs again (no observation is
waiting). Each later addition to either notebook needs its page before the tests pass. The pages go live only when this
branch reaches the branch GitHub Pages serves: publishing is the owner's call.
