# 0055: Each observation has a plain-English reading beside it, and the atlas leads with it

**Date:** 2026-11-06. **Whose:** the owner's (what); Claude's (the review of each reading, how the pages show it),
which the owner can overturn.

**Context.** The owner wrote a plain-English version of every observation into copies of the three notebooks
(`analysis/GPT-Rephrase/`), and asked for them to be copied into the notebooks beside the originals, which must not be
edited or removed ("for the sake of provenance"), and for the website to use them, with the technical version removed
from the pages except in the step-by-step provenance. Claude could reject a reading only if it harmfully
oversimplifies or misinterprets the observation.

The copies differ from the notebooks only by added lines in 169 markdown cells: a sentence under each notebook's
title, and for each of the 231 observations a heading `##### Observation U12 in plain English` and a block quote just
above the observation. No original line is changed and no code cell or output differs.

**Decision.**

1. **The readings join the notebooks as written, with seven phrases corrected.** Claude read every reading against
   its observation and checked its numbers against the page. 224 are kept word for word. In seven a phrase changed the
   meaning, so that phrase is corrected and the rest kept; each carries a dated note under its block quote saying what
   the supplied wording was and why it changed:

   | Observation | Supplied | Why it was changed |
   |---|---|---|
   | U4 | "About 82% are standard patent applications, while 15% are provisional" | Reads as a share of all IP records; it is a share of patents |
   | U5 | "annual Australian standard patent applications stayed between 28,798 and 32,960" | Reads as Australians' applications; nine in ten are from overseas (U7) |
   | U10 | "Of Australian standard patent applications filed in ... 2008, 54.4% went on to grant" | The same: the grant rates are every applicant's |
   | U28 | "Other policy dates showed little visible change" | The observation finds four steps and two pauses besides the two rushes |
   | U127 | Distinct patents count "how many applications they shared between them" | Not what that count measures |
   | B23 | "Higher spending made patenting more common" | A cause; the observation finds a weak association (rho 0.120) |
   | M12 | "usually assigning a different number in 1.1% to 4.8% of matches" | Reads as the match usually being wrong |

   None was rejected whole. The copies in `analysis/GPT-Rephrase/` are left as the owner supplied them. Re-reading
   the notebooks shows every one of the 231 observations' own words, sections, evidence and charts unchanged.
2. **The reader.** `atlas.notebook` reads each block quote as the observation's `plain` reading (a hyphenated word
   wrapped across two lines is rejoined). An observation's own text still runs to the next heading, which is now the
   next reading's, so it is exactly what it was.
3. **The numbers rule covers the readings, allowing for plain English's rounding.** A number in a reading must be on
   the notebook's page, or round to one there (82% for 82.17%), or be a share on the page written as a percentage
   (34.6% for 0.346), or a count in millions or billions (29 million for 28,960,234), or the end of a year range
   written short ("1990–93"). Four numbers are worked out by arithmetic, and each is listed in `build.DERIVED` with its
   sum (U26's 33% above an ordinary month from 133%; B21's $297,000 from $0.297m; M3's 35% from a hazard ratio of
   0.648; M14's 93% from a rate ratio of 1.932). The build fails on any other number, and on an observation with no
   reading.
4. **The pages lead with the reading.** The observation box shows the reading, and so do the observation cards and
   the "Copy as Markdown" copy. The atlas's own `statement` and `points` stay in the YAML, still checked, but are no
   longer sent to the pages. The observation in the notebook's own words now closes step 4 of "Follow the evidence"
   ("Which gives observation U12, in the notebook's own words"), the only place it appears; step 4 starts closed like
   the other three. The "For analysts" box keeps only the notebook's own charts and the link to the notebook. Search
   reads the reading and the notebook's words.
5. **What is not changed.** Headlines, key figures, the Stage 3 chain and signal table, the questions, the reasoning
   steps, assumptions and limits are the atlas's own wording, as before: the owner supplied readings of the
   observations only. Whether to rewrite those in the same style, and how to settle "Australian ... applications"
   (every applicant's in Australia in some readings, Australians' own in others), is OQ32.

**Consequences.** The notebooks grow by 1,803 lines and change nothing else; they were not re-run. `atlas.json` is
built from them (231 pages) and the chat's passages follow the pages (4,521, from 4,611: the atlas's statement and
points are gone, and the notebook's words are now in step 4). The chat answers from the new passages only once Econ is
refreshed (`econ atlas-ingest`, `econ index --kb atlas`; OQ33). The atlas's corrections log records the change, and its
date moves to 6 November 2026. Tests cover the reading on every page and in every Markdown copy, and the looser
numbers rule both ways.
