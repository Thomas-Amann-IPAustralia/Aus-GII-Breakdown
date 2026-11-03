# 0044: The evidence atlas brought into line with the final review, in plain English, with more charts

**Date:** 2026-11-03. **Whose:** the owner asked for the website to be corrected now (A28): to communicate clearly
with little or no jargon, with graphs where possible, since for most readers the website is as deep as they will go;
to have "Follow the evidence" hold up to scrutiny from people in the IP ecosystem; and to describe the facts without
overstating them. Claude chose how. Publishing (merging to the branch GitHub Pages serves) stays the owner's call
(OQ19); the owner expects to open a pull request.

**Context.** The atlas (`evidence/`, ADR 0023, 0035) was last built on 29 October 2026. Since then audit passes 1 to 7
(ADR 0036 to 0042) and the final review (ADR 0043) restated many observations. Comparing each page's quoted notebook
text with the notebook as it now stands, 131 of the 186 observations had changed; the numbers rule failed for 61, and
the test of the atlas errored. The numbers rule cannot see readings: a page could quote current numbers and still say
"never filed", "renewed", "moved overseas", "no link" or "drives", which the passes had withdrawn. Five drawn-from-data
charts still asserted figures the notebooks no longer give, and two (U36's survival curves and U47's IP filers) used
the old method or definition while their assertions passed against figures kept only in restatement notes. The
overview's "What Stage 2 found", "Ten things Stage 1 found", the featured page (B6), the corrections, limits and "What
comes next" pages quoted readings that are no longer the notebooks'. 138 of 186 pages had a chart.

**Decision.**

1. **Every changed page is rewritten from its notebook text, not patched for numbers.** Each of the 131 was read
   beside the current observation, and its headline, statement, figures, points, chart, questions, steps, preparation,
   assumptions and limits brought into line. The 55 unchanged pages were swept for withdrawn readings and jargon.
2. **The main view is plain English; the trail is precise.** Headlines and statements describe what the data show,
   in the notebooks' restated terms: "no filing linked", not "never filed"; "still in force", not "renewed"; "now held
   only overseas" (two endpoints), not "moved"; "first observed filing", not entry; "allocated" for industry counts;
   "no association detected", not "no link"; a mechanism only as a hypothesis. Statistical terms in the main view are
   either replaced ("rank correlation", "comparison months") or linked to the glossary; method names (Wilson and
   Newcombe intervals, delayed entry, block resampling) sit in "Follow the evidence", with the definition an IP
   professional would check: the filer's origin and type (a founding applicant, IP Australia's resident definition,
   ADR 0037), representation before the renewal (ADR 0041), shares of large employers over every employer (ADR 0043).
3. **A chart wherever the page has the numbers for one.** 40 more pages have a chart (178 of 186): quoted charts of
   numbers on the notebook's page, checked by the numbers rule as before. A new chart format, `share`, shows a
   proportion the notebook prints (0.486) as a percentage (48.6%), so a chart can use the page's own figures. The eight
   pages without a chart are data checks or have no figures to chart; the notebook's own chart is under "For analysts".
4. **The drawn-from-data charts use the notebooks' current definitions.** Origin is the filer's (`founding_australian`,
   `founder_type`, `founder_country`), IP filers are `ip_record = 'filed'` (ADR 0036), U36's survival curves count each
   right from its grant or registration with cohorts by Act and subtype (ADR 0041), and every assertion quotes the
   current figure. A new check found no assertion that survives only in a restatement note.
5. **The framing pages follow the notebooks**, with a dated entry for each pass in the corrections list, and "What
   comes next" records the owner's decision that Stage 3 begins, after a break, with the methods the final review
   listed (A29).

**Corrections made on the way.**

- U74's chart split each label at its comma ("Standard patent, division" became two categories), so its three bars
  sat under six labels; the labels are quoted now, and the build checks that every quoted chart's series has one
  value per category (`build.chart_shape`).
- The review against IP Australia's evidence said Stage 2 found expedited patents' link "holds for overseas
  organisations only; pooled, it is a change in who asks", and quoted 67.3% for 1983 to 1989 trade marks; both follow
  B13 and U36 as restated (slightly more often in force, pooled, in both periods; 67.0%).
- A glossary link without display text prints the term's full title, which doubled words ("expedited examination
  examination", "placebo date months"); those links now carry their own words.

**Consequences.** The atlas and the notebooks agree again: the build passes the numbers rule for all 186 pages, the
committed `atlas.json` is the build's, and the test suite passes in full (127). Each later change to an observation
still needs its page changed in the same commit (ADR 0023). The pages go live only when this branch reaches the one
GitHub Pages serves (OQ19).
