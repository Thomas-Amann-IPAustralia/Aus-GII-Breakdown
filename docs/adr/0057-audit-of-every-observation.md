# 0057: Every observation audited against its output, 22 corrected with dated notes, and the atlas brought into step

**Date:** 2026-11-10. **Whose:** the owner's (the ask: review every observation in the three notebooks for errors of
logic or synthesis, "if the observation is out of step with what the data is showing", correct them, then update the
front end); Claude's (the method, each correction's wording, and the two choices under "Choices"), which the owner
can overturn.

**Context.** The notebooks hold 231 numbered observations (128 in Stage 1, 63 in Stage 2, 40 in Stage 3). Earlier
reviews checked them by section or by theme (the twelve external audits, pass 8 of 2 November, the review of 3
November). None read every observation against the output cell above it in one pass.

**Method.**

1. Each observation's markdown was set beside the outputs between it and the observation before (a dump per cell).
   Every quoted number was matched to the output; derived figures (sums, ratios, ranges) were recomputed; the heading
   and the plain-English reading were read against the bullets and the tables.
2. A screen listed, for each observation, the numbers in its text that are not in its evidence; each was explained (a
   cross-reference checked in the other observation, a derived figure, or an error).
3. Figures the page shows only in a chart were recomputed from the lens tables (U14's plant breeder's rights by genus,
   U26's seasonal profile), and one attribution was tested on the lens (M39: GDP's negative lead on trade marks after
   2008 is the pandemic years'; over 2008Q3 to 2019Q4 it is -1.531, interval -4.479 to 1.418).
4. Corrections follow the notebooks' own convention: the text is put right in place and a dated bullet says what it
   said. They were made as edits to the cell's source inside the notebook's JSON, so every other byte, outputs
   included, is as it was; no cell was re-run.

**What was found.** 22 observations needed a correction (9 in Stage 1, 8 in Stage 2, 5 in Stage 3). None reverses a
finding or changes a Stage 3 verdict; 209 are in step with their output as written.

| Observation | What it said | What the output shows | Kind |
|---|---|---|---|
| M18 | "B33's 'IP follows R&D and income'" (also 4.2's heading, 4.4's table, and the atlas link) | That is B32's finding; B33 is Australia's ranks among OECD members | Synthesis (wrong page) |
| M35 | The fall is "in new and heavy filers"; filers seen before "followed up about as often as before" | A fall at every filing volume (12.92% to 7.98%, 10.82% to 3.39%, 22.38% to 5.46%); filers in both periods 7.11% to 4.34%, not detected either way (-7.27 to 1.73, which includes the whole fall); new filers are not separated | Synthesis |
| U45 | "The cause is publication" | The register shows where the missing ABNs are, not why IP RAPID lacks them (U100, OQ7) | Synthesis |
| B32 | Trade marks go "much less with R&D ... trade marks follow commerce, patents follow research" | True of business R&D among OECD members (0.373 against 0.844); across all countries trade marks go with R&D spending at 0.643 and researchers 0.701 (patents 0.793 and 0.837) | Synthesis (degree) |
| U64 | "Before 1995 WIPO cannot say where most applicants come from" | 27.91% to 34.35% of applications have no origin to 1993, about a third (9.0% in 1994) | Heading |
| U120 | "more than almost any OECD member's" | 16.7% of 36 members are lower (about six) | Heading |
| U63 | "complete except for R&D people and spending" | Tertiary enrolment starts in 2015 (40% of years) | Heading |
| U124 | Employment's largest months "May 2020 and June 2020"; unusual months "in 2020" | October 2021 (-334.77) is second; the PBS's unusual months are 2023 and 2025 | Reading of a list |
| B1 | 221 leads, "most of them holding in a second decade" | A lead holds in both decades by definition; "most" is of first-decade passes (1,586 of 1,940) | Heading |
| M23 | "each research measure goes with more patents per work on its own" | Citations per work alone is 1.151 (0.849 to 1.562) in 2017 to 2023 | Heading |
| M12 | "U45's later fall in first patent filers is about half a matter of linking" | The 660 to 542 series is first linked standard patents; U45 counts a first patent of any kind (1,165 to 685) | Scope |
| U26 | Plant breeder's rights granted peak in "September 170, March 91" | March is below an ordinary month; June 115 and August 113 are the next busiest | Number |
| B13 | Overseas organisations, FY2010 to FY2016: "intervals overlapping" | 66.8% to 69.0% and 66.1% to 66.7%: 0.1 points apart | Number |
| B29 | The top decile's five heaviest filing areas fall in the second half | Four do; 2015 (365 patents) is in the first | Number |
| B49 | "the 33.33% rise of November 2016" | The fee changed on 10 October 2016; the renewal tables label the first month that opens at the new fee | Date |
| U38 | Later renewals "held steady at 3,242 to 3,786 a year" (no years) | 3,037 to 3,786 over 1998 to 2005; 8,272 in 2006 | Clarity |
| U14 | "the other 559 values ... hold 55.4%" after three genera | The 559 are outside the chart's 15 largest | Clarity |
| U22 | The lens has 79 columns | 86 since U124 (U22's overview was not re-run) | Stale |
| B21, B27, B40, M39 | "0.316 in both halves"; "0.196"; "0.465 in both years"; "about a third of a point" | 0.314; 0.197; 0.467; 0.38 | Rounding |

**The atlas.** Each page carries the notebook's corrected words (its "original" and its reading). The plain-English
layer changed where it repeated a corrected claim: U22, U63, U64 (headline, and the national lens's limits), U124,
B29, B32, B40 (and its chart's FY2025 value), B49, M12, M18, M23 and M35 (headline, statement, its revisit of B38 and
its question), with the fifteenth early signal and the audit page's two passages on M35. The other ten pages' own
wording did not carry the error. The strict build, the passages and the tests pass.

**Choices.**

1. **M18's outcome moves from B33's page to B32's** (`revisits`), where it sits beside M17's. Section 4.1 of notebook
   3 names B33 as revisited, so M17 now links to B33 as "refined" (Australia's ranks as distances from the members'
   mean: manufacturing -1.57, exports -1.06, new business density +1.75, journal articles +0.96, business R&D -0.35);
   otherwise B33's page would show no Stage 3 outcome. The owner can drop that link without affecting anything else.
2. **M35's reading is amended**, the one plain-English reading that carried an error ("concentrated among new and
   frequent filers"), with a dated note under it as ADR 0055 and 0056 did. IP Australia's own figure (new filers 63%
   of provisional applicants in 2025) still fits M35; M35 does not test it. A direct split of the fall by whether the
   filer had filed before would settle it (OQ35).

**Not changed.** No output, chart, verdict or number of leads; no observation removed or renumbered; `screens.yaml`,
the lens tables and the glossary. Cross-notebook differences that each match their own table were left (for example
B49's 15 anniversaries against M28's 14).

**Consequence for the chat.** "Ask the atlas" is served by the Econ repository from passages ingested at an earlier
commit. Until it is re-ingested at the merged commit (the handover's open issue), its quotes will not match the 22
corrected pages.
