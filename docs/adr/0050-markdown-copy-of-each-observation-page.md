# 0050: A Markdown copy of each observation page, with the chart's numbers as a table

**Date:** 2026-11-03. **Whose:** the owner asked that every observation page can be copied or downloaded as Markdown,
that a page with a chart always carries its table, and that the copy keeps the stepwise logic, explainers and data
provenance. Claude chose how.

**Context.** An observation page (`evidence/`, ADR 0023, 0044, 0049) is drawn in the browser from `atlas.json` and,
for a chart, `data/charts/<id>.json`. The page's chart already has a table view (its accessible twin), built in
`charts.js` from the same spec. 221 of the 229 pages have a chart; some have several views (U28 has 17), and a few
scatter charts' tables are long (U53's three views hold about 4,100 rows).

**Decision.**

1. **Two buttons under each page's headline:** "Copy as Markdown" (the clipboard, with a fallback for browsers that
   refuse it) and "Download .md" (`<id>.md`). Both write the same text.
2. **The Markdown is written in the browser from the data the page reads**, by `evidence/js/markdown.js`, not built
   into 229 files: nothing to keep in step, no new build step, and the copy is always the page. The module touches no
   document, so a test runs it under Node.
3. **The chart's table comes from one function.** `evidence/js/tables.js` holds how a value is written (`fmt`) and the
   chart's table (`chartTable`); `charts.js` draws its table view from it and `markdown.js` writes it, so the copy and
   the page cannot disagree. A chart with views carries a table for **every** view, in full, however long: a copy
   cannot carry the chart, so the table is its whole evidence.
4. **The copy follows the page's order and leaves nothing out:** the head (lens, unit, stage, section, strength and
   what it means, the page's address); for Stage 3, the chain (what the earlier stage found, what was held, what is
   left); the statement and points; what Stage 3 found (on earlier pages it tested); the key figures; the chart's
   title, subtitle, table(s), source and how its numbers were made; the signal-by-signal table; how it bears on the
   questions; the four steps of the trail (each source's publisher, link, coverage, licence and date copied; every
   processed table with rows, where kept, size and fingerprint; the observation's preparation and the lens's repairs,
   each with its reason; the reasoning steps ending in the observation); assumptions and limits; what happens next;
   related observations; the notebook's own words (quoted) with links to its charts; and an explainer for every
   glossary term the page uses.
5. **The site's markup becomes Markdown:** `[[term|words]]` reads as its words (the term is explained at the end),
   `{U44}` becomes a link to that page, and `**bold**` and `` `code` `` are kept.

**Consequences.** `tests/test_atlas.py` writes every page's copy (`analysis/atlas/markdown_check.mjs`) and checks
that it has the trail's headings, its sources, no unconverted markup, and, for a chart page, a table row for every
category of every view; it skips if Node is not installed. The largest copy is U53's (164 kB).
