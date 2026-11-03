# 0049: Stage 3 in the evidence atlas, with its logic on every page, and easier navigation

**Date:** 2026-11-03. **Whose:** the owner lifted the website freeze (A34) and asked for the atlas to show everything
Stage 3 found, "correctly and accurately", with very clear headings, the logical process explicit and charts in
preference to text; and, as a second task, for the atlas to be easier to navigate now that it holds this many
observations. Claude chose how. Publishing (merging to the branch GitHub Pages serves) stays the owner's call.

**Context.** The atlas (`evidence/`, ADR 0023, 0035, 0044) held Stages 1 and 2 (186 observations) and was frozen while
Stage 3 ran (A32). Since then notebook 3 added M1 to M38, the review of 3 November 2026 (ADR 0048) added U124 to U127
and B63 to notebooks 1 and 2, and the handover listed 29 Stage 2 readings that Stage 3 revises ("Waiting for the
atlas"). No earlier observation's text had changed (checked against the committed `atlas.json`), so no existing page
needed rewriting for numbers. The observations page listed every observation as a card, grouped only by lens: 229
cards on one page.

**Decision.**

1. **Stage 3 is a third stage of the same atlas.** `atlas.notebook` reads `03_multivariate.ipynb` (ids `M`); Stage 3's
   plain English is in `content/observations/stage3/`, one file per lens; references are written `{M3}`. The numbers
   rule is unchanged and covers two new fields (below); it no longer reads a stage's name ("Stage 2") or a quoted
   chart's styling (a colour's place in the palette, an axis's range) as figures, and the chart-shape check covers a
   chart's views as well as the chart.
2. **The logic is data, so every page can show it.** A Stage 3 entry names the earlier observations it tests
   (`revisits`: the id, the signal in a few words, the outcome and one sentence on what changed), what was held
   together (`held`) and each comparison's raw and held figures with its outcome (`verdicts`). The build copies each
   revisit onto the earlier page (`later`), so the logic reads in both directions:
   - a Stage 3 page opens with a three-step chain (what Stage 2 found → what Stage 3 held together → what is left),
     then the observation, a chart of the raw and held figures, and a "signal by signal" table;
   - an earlier page that Stage 3 tested shows, under its observation, a box with Stage 3's outcome and a link to the
     test, and its "What happens next" says the test is done. 53 earlier pages carry one (the 29 Stage 2 readings the
     handover listed, the other signals Stage 3 tested and found holding, and U8, U28, U44 and U45).
3. **Outcomes are ADR 0046's words, plus three.** holds, weakened, not detected once held, reversed, appears once held,
   not detected either way; and, for the atlas, "does not replicate" (seen in one sample, not the second), "mixed" (a
   page whose groups or periods differ; its sentence says which) and "refined" (a description that sharpens an earlier
   one). Each is always written, never a colour alone; its meaning is in the glossary and on the Stage 3 page.
4. **A chart for every Stage 3 page, drawn from its own numbers.** A new chart type, `effect` (a forest plot: a dot for
   each estimate and a line for its interval, the raw figure in grey beside the held one in blue, a dashed line where
   there is no difference), shows what holding the factors did; bars show counts and shares. All 38 are quoted charts,
   checked by the numbers rule; the notebook's own 11 charts are under "For analysts". The five review additions have
   charts too (229 pages, 221 with a chart).
5. **A page for Stage 3 as a whole.** "What Stage 3 found" (`#/stage3`, in the menu) explains the test in five steps,
   walks through one example (M1), defines the outcomes with their counts, and lists every check, lens by lens, from
   the earlier finding to the outcome to the page that made it, filterable by outcome; then the structure findings
   (components, groups, the name match). The overview leads with a bar of outcomes and eleven findings; "What comes
   next" gives section 8's two tables (15 early signals, 13 data gaps) in place of Stage 2's list of leads, and the
   question pages show the signals that bear on each.
6. **Navigation.** The observations page shows a compact list by default (id, headline, Stage 3 outcome or "→ M…"),
   grouped by lens and the notebook's sections, which open and close; a large list opens as an outline. It can group
   by stage, switch to cards (remembered in the browser), filter by Stage 3 outcome or by "tested again in Stage 3",
   and jump between groups from a bar that stays in view. The search box suggests observations as you type (an id, or
   headline words first), with the arrow keys and Enter; `/` focuses it. On an observation page the arrow keys (or j
   and k) move to the previous or next observation, and the side rail lists the other observations in the same
   section. Lens pages list their observations by stage and section in the same compact, collapsible form.

**Corrections made on the way.** None to the notebooks. The framing pages had said "Stage 2 of 3 complete"; the
corrections list now records the review of 3 November 2026 and the freeze. Redrawing the drawn charts after the lenses
were rebuilt changed only U22 and U24, which gain the IP judgments series added to the timeline; U22's subtitle had
hard-coded "28 series" (it drew 30, now 33) and now counts them.

**Consequences.** The atlas and the three notebooks agree: the strict build passes for all 229 pages, the committed
`atlas.json` is the build's, and the atlas's tests (now covering the links back, the two tables and the outcomes'
meanings) pass. Each later change to an observation again needs its page changed in the same commit (ADR 0023), and
a new Stage 3 observation needs its `revisits`, `held` and chart. `atlas.json` grew from 920 kB to 1,238 kB.
