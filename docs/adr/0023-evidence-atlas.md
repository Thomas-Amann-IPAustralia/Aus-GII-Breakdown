# 0023: The evidence atlas, Stage 1 for readers who are not data scientists

**Date:** 2026-10-27. **Whose:** Claude's (the owner asked for an interface, served from the repository's GitHub Pages,
that lets non-technical readers read the observations and click through to where each one's data came from, how they
are stored and prepared, and the reasoning that leads to it); the owner can overturn any of it. A design prototype
(`assets/evidence-atlas.html`) set the tone, not the build.

**Context.** Stage 1's 99 observations (U0 to U98) live in `analysis/notebooks/01_univariate.ipynb`, written for the
analysis: code, column names and output cells. The owner wants readers who will never open a notebook to see what was
found, under which lens, how it moves the five questions forward, what Stage 1 cannot say, and what Stages 2 and 3
will add. Nothing in the page may ask them to read code, and any method beyond high school is explained.

**Decision.**

1. **Where.** A separate static site in `evidence/` (one page, hash routing, no build step in the browser), linked
   from the GII breakdown page's navigation. Pages serves the branch root, so it appears at `…/evidence/` once on the
   published branch. The site's policy allows only its own scripts, so ECharts is the copy already vendored in
   `assets/vendor/`; nothing loads from a CDN.
2. **What it is built from.** `analysis/atlas` (run `python -m atlas.charts`, then `python -m atlas.build`) joins
   three inputs into `evidence/data/atlas.json`:
   - the notebook, read cell by cell: each observation's own text, its strength label, the heading it sits under, and
     the outputs and charts of the code cells above it (the notebook's own charts are copied as WebP, 70 images);
   - hand-written plain English in `analysis/atlas/content/` (one YAML file per lens, plus the site's framing pages,
     the lenses, the questions and a glossary of 100 terms). Each observation has a headline, a statement, its
     figures, the reasoning as numbered steps ending in the observation, what was kept and how it was prepared, its
     assumptions, its limits, and how it serves each research question it touches;
   - the source register and the manifest, for where each source comes from and how it is stored (42 sources).
3. **The numbers rule.** Every number in an observation's headline, statement, figures, points and any hand-quoted
   chart must appear in that observation's notebook text or in the outputs above it, or the build fails. Rounded or
   restated numbers ("about 4.4 million") are therefore written as the notebook writes them. This keeps the plain
   English from drifting from the evidence, and is tested (`tests/test_atlas.py`).
4. **Charts.** 69 observations have an interactive chart redrawn from the lens tables with the notebook's own query.
   Each chart function asserts that its data reproduce the numbers the observation quotes; if they do not, the chart is
   not written. 25 more are small charts of numbers quoted in the content, checked by the numbers rule; 5 have none.
   Every chart names its source, has a legend and a table view, and uses the validated palette in both themes.
5. **The question mapping is editorial.** Which research questions an observation serves, and how, is a judgement
   written in the content, not something the data decide. The pages say so, and say that Stage 1 answers none of the
   questions.
6. **In step.** The committed `atlas.json` must equal what the build produces from the notebook and content (a test
   checks), so a change to either needs a rebuild. The chart files need the lens tables, so they are rebuilt by hand
   after `python -m eda.build`, not in the tests.

**Consequences.** The site is a second, plain-English record of Stage 1 that cannot quote a number the notebook does
not show. Correcting an observation now means correcting the notebook, the content and the rebuilt site together;
building the site found one such error (U0 had kept the first corpus profile's figures; corrected in the notebook,
`docs/stage-1-summary.md` and the site's corrections list). Publishing is outward-facing: the pages go live only when
the branch reaches the one Pages serves, which is the owner's call. Stages 2 and 3 can add their observations to the
same structure (a strength other than descriptive, and pairs rather than single variables), which the page design
already allows for.
