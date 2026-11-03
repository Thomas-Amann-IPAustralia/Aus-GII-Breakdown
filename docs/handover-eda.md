# Handover: exploratory data analysis

For the next Claude Code session. Read `CLAUDE.md` first, then `docs/eda-plan.md`.

**Status (2026-11-03, latest): the Stage 3 web pass** (A34, ADR 0049). The owner's instruction: "The website freeze
is officially lifted! I would like you to now update the website with everything new that's been found in stage 3.
Make sure to make the headings very clear and the logical processes explicit. Again, graphs/visuals are preferred over
just plain text. Updating the website to correctly and accurately reflect the 3 EDA notebooks is the top priority. A
second, more minor task is to improve the UX of the atlas." **The freeze is lifted**; `CLAUDE.md` says so. Done:
- **Every observation of the three notebooks has a page (229):** M1 to M38 (`analysis/atlas/content/observations/
  stage3/`, one file per lens), and the review's additions U124 to U127 and B63. No earlier observation's text had
  changed since the atlas was built (checked against the committed `atlas.json`), so no earlier page needed rewriting.
- **The logic is on every page.** A Stage 3 entry has `revisits` (the earlier observation, the signal in a few words,
  the outcome, one sentence on what changed), `held` and `verdicts` (each comparison's raw and held figures and its
  outcome); the numbers rule covers the last two. A Stage 3 page opens with a chain (what Stage 2 found → what was held
  together → what is left), then the observation, a chart and a "signal by signal" table. The build copies each
  revisit onto the earlier page (`later`): 53 earlier pages show Stage 3's outcome under their observation, with a
  link, among them every reading the "Waiting for the atlas" lists below named (so both lists are done).
- **Charts:** a new `effect` chart (a forest plot: raw in grey beside held in blue, each with its interval, a dashed
  line of no difference) for most Stage 3 pages, bars for the rest; all 38 quoted from the observation's own numbers
  and checked; 221 of 229 pages have a chart.
- **New and changed pages:** "What Stage 3 found" (`#/stage3`: the test in five steps, the M1 example, the outcomes
  with counts, every check lens by lens, filterable, and the structure findings); the overview (a bar of outcomes,
  eleven findings, M1 featured, the stages' status); "What comes next" (section 8's 15 early signals and 13 data gaps,
  in place of Stage 2's leads); question pages (early signals and Stage 3 first); lens pages (the timeline's seven new
  columns and sources, the name-match columns); limits (what "not detected" means; Stage 3's rule as an assumption)
  and corrections (the review of 3 November 2026, the helper fault, the freeze); 23 glossary terms.
- **Navigation:** a compact, collapsible list grouped by lens and section (or by stage), cards on request
  (remembered), filters by Stage 3 outcome and "tested again in Stage 3", a sticky jump bar; type-ahead search (ids,
  then headline words); `/` to search, arrow keys (or j and k) between observations; "In this section" in the rail.
- **Rule changes in the build:** a stage's name ("Stage 2") and a quoted chart's styling keys are not read as
  figures; the chart-shape check covers views; tests cover the links back, the two tables and the outcomes' meanings.

**Checks:** the strict build passes for all 229 pages; ruff is clean; the tests pass (the atlas's 8 included). Pages
checked in Chromium at 1,366 and 390 pixels: no console errors, no horizontal overflow; search, keys and filters
exercised. The lenses were rebuilt from R2 and every drawn chart redrawn (`atlas.charts`, all assertions pass):
only U22 and U24 change, gaining the IP judgments series the review added to the timeline; U22's subtitle now counts
its series (33; it had said 28 when it drew 30). U53 redrew the same points in another order and was left as
committed. With the lenses built, the full suite passes (137, none skipped).

**Next, in order:** the owner's review of section 8's two tables (on the website now, "What comes next") and OQ26
(the name match); the owner's pull request and publishing (merging to the branch GitHub Pages serves); then, at the
owner's word, the plan's "After Stage 3".

**Status (2026-11-03): a review of all three stages** (A33, ADR 0048). The owner's instruction: "Please
review the all stages of the EDA. Please look for any gaps or omissions and correct them. You must focus only on the
notebooks, not the GitHub webpage." What the review found and did:
- **Stage 3 (notebook 3):** every M observation of the first pass was checked against its output (all match but two
  slips, corrected where they are: M1 said "not detected once held" for a result the table calls "not detected either
  way"; M16 gave the lowest silhouette as 0.231, 0.2316 on the page). Section 0's table said every Stage 2 signal
  carried to Stage 3 was taken up; eighteen were not, nor B49's own request (renewal at each anniversary). Each now has
  a section, marked "added": 1.7 divisionals (M26), 1.8 made here and filed from overseas (M27), 1.9 renewal at each
  anniversary after a fee change (M28), 2.6 suppliers and large taxpayers (M29), 2.7 the firm's age and patents held
  overseas (M30), 3.5 business mix, incomes and change (M31), 3.6 every regional attachment beyond the components
  (M32), 4.3 the cross-country attachments with income and size held (M33), 5.4 fee breaks with trend and season (M34),
  5.5 the FY2025 provisionals (M35), 5.6 the cycle, labour and courts with block resampling (M36), 6.3 the
  division-level indicators (M37), 7.3 every kind of institution (M38). The lens summaries (now 1.10, 2.8, 3.7, 4.4,
  5.7, 6.4, 7.4) and section 8's tables carry them (15 signals, 13 gaps).
- **A helper fault:** `multi.adjusted_effect` returned a meaningless clustered interval, silently, when two held
  factors picked out the same rows (a patent with no field has no class count either). It now refits on the
  independent columns (a test covers it). Notebook 3 was re-run in full before and after the new sections: every
  earlier output is identical. A last full run found one new cell (352-mix, M31's change between Censuses) whose
  resampled intervals moved in the third decimal between runs (row order and the parallel sums' last digits); its
  rows are now sorted and rounded to 10 decimals, three runs agree, and M31 quotes the result (-0.204, not -0.203).
- **Two sources in no lens:** the Labour Force Survey (`abs_labour`) and the IP judgments (`fedcourt`), planned for the
  timeline, were never attached, so they had no profile, pair or model. Now in the timeline (86 columns): `employed`,
  `unemployment_rate`, `participation_rate`, `owner_managers`, `ip_judgments` (and on patents, on trade marks, January
  1995 to February 2025); `variables.yaml` and `screens.yaml` describe them (not screened: selected pairs).
- **Stage 1 (notebook 1), by additions only:** U124 (the new timeline columns, and the shape of the series added after
  Stage 2, which 5.11's summary said was not profiled; new section 5.11, summary now 5.12), U125 (every fee column, in
  5.7), U126 (the name-match columns, new 2.7, summary now 2.8), U127 (`shared_with_institution`, in 7.3); section 8's
  sources table, section 9 and the title's status note them.
- **Stage 2 (notebook 2), by addition only:** B63 (the labour market and the judgments, new 5.7, summary now 5.8);
  the title and section 8 note it.
- Notebooks 1 and 2 were run cell by cell for the new cells only (with their setup cell), so every reviewed output is
  as it was; the record of method is ADR 0048; `CLAUDE.md` now allows additions and dated corrections to notebooks 1
  and 2 where a gap is found.
- What the new sections found, in short: no renewal response to fee changes at each right's anniversary (patents
  within about 1.4 points, M28); divisionals doubled within the same filers (M26); manufacturing's share of an area's
  businesses goes with more filing per business beyond the advantage gradient, where B31 saw none (M31); most regional
  and cross-country attachments are their gradients (M32, M33); FY2025's provisional follow-up fall is new and heavy
  individual filers' (M35); the cycle shows only before 2008 (M36).

**Waiting for the atlas, added by the review (done in the Stage 3 web pass, ADR 0049):** the readings revised by M26 to M38 (B15, B16, B22, B24, B26, B28,
B31, B35, B38, B43, B44, B46, B47, B49, B52, B56, B58, B59); the additions to notebooks 1 and 2 (U124 to U127, B63,
and the renumbered summaries 2.8, 5.12 and 5.8); the timeline's seven new columns in the lens pages.

**Checks:** ruff is clean; the tests pass (131) except the atlas's five (`tests/test_atlas.py`), which fail by
design while the website is frozen: they require a page for every observation of notebooks 1 and 2, and U124 to
U127 and B63 have none yet (writing them is the atlas work the owner deferred, A32, A33). They pass again once the
freeze lifts and those pages are written.

**Left, and why:** the CER's national installations and AusTender by month, planned for the timeline, are not built
(both sources are in other lenses, so ADR 0007 is met; listed in section 8's gaps); the TGA and the PBS beyond Stage 1
wait for OQ8 (the medicine strand); court judgments after March 2025 wait for OQ22.

**Next, in order:** the owner's review of section 8's tables (now 15 signals and 13 gaps) and OQ26; then, at the
owner's word, the plan's "After Stage 3" and lifting the freeze to carry both lists to the atlas.

**Status (2026-11-03): Stage 3's first pass** (A32, ADR 0046, 0047). The owner's instruction: "Please
commence the multivariate analysis. For now, we can freeze the Github webpage. I want to make sure all efforts are
focused towards the processing of data and information." **The website is frozen**: nothing in `evidence/` or
`analysis/atlas/` changes during Stage 3, and notebooks 1 and 2 stay as reviewed. `03_multivariate.ipynb` is rebuilt
from its 23 October skeleton, with every lens: section 0 (the method), 1 (`rights`, M1 to M7), 2 (`firms`, M8 to M12,
with the name match), 3 (`regions`, M13 to M16), 4 (`national`, M17, M18), 5 (`timeline`, M19, M20), 6 (`industries`,
M21, M22), 7 (`institutions`, M23, M24), each with a summary, B37's breaks with trend and season held (M25, in
section 5.3), and 8, the two tables the plan asks for (11 early signals, 9 data gaps), drafted for the owner's review.
`docs/stage-3-summary.md` summarises the first pass. Each Stage 2 signal is modelled with its third factors held
together and given a verdict (holds, weakened, not detected once held, reversed; appears once held or not detected
either way where the raw figure was not detected). New helpers in `multivariate.py`, with tests: `adjusted_effect`
(logistic average marginal effects, clustered by the filer's party, rare or uniform levels merged), `adjusted_hazard`
(Cox models with delayed entry at grant, as Stage 2's curves; `cox_cluster_cov`, because statsmodels' clustered errors
fail when censored rows tie with the last event), `nb_rate_ratios`, `partial_corr_interval` (1,000 resamples),
`effective_n` and `block_bootstrap_corr`, `effects_chart`, `verdict`, `silhouette_word`, and a legend on
`corr_heatmap`. The filer's party id follows `filer_group`'s rule (type agrees for all 3,769,615 rights with a filer).
**The name match** (ADR 0045, 0047) is in the build: `name_matched_abn` in `rights`, four `*_name_matched` counts in
`firms`, kept apart; tested, 1.1% to 4.8% of matches name another ABN; the postcode rule was dropped (it halved the
matches for no gain in accuracy). What Stage 3 found (all observational or descriptive):
- **holds:** filing alone and grant for Australian individuals (about 31 points, M1); no agent before the first
  renewal (M2); Australian organisations' patents less likely to end within the same reach (hazard ratios 0.65 to 0.81,
  M3) and reaching fewer offices (M4); granted Australian-founded patents more often held only overseas (M6);
  provisionals' women inventors (M7); age, spend and public form for standard patents among R&D claimants (M8);
  suppliers' contracts and value (M9); the size gap among large employers, wider within industry (M11); B30 with the
  filer's party (M15); B36's quarterly lead with block resampling (M19); patents following business R&D across
  countries (M18) and divisions (M22); Raising the Bar's rush and Australians' lower level after it, with trend and
  season held (M25);
- **weakened:** citations at the same reach (M4); wide patents held overseas (M6); the places' advantage gradient once
  business density, degrees and R&D claimants and remoteness are held (M14);
- **not detected or reversed:** expedited examination's longer life (M5); organisations' women inventors once the
  field is held (M7); the claimants' city gap (M8); income for patents across countries (M18); innovation shares
  against IP, even with the crosswalk with services (M21); trade marks against business R&D across divisions (M22); no
  single university measure in both periods (M23); licences and licence income per patent at the same research spend
  (M24); the Designs Act's overseas step, which a control matches (M25);
- **structure:** one advantage component carries half of places' variation (M13), weak segments among places, one
  group of 288 city areas holding 56% of placed patents (M16); several dimensions among countries, Australia nearest
  Norway, New Zealand and Sweden (M17); trends dominate the monthly series (M20); the name match closes most of the
  recent fall in standard patents linked to an ABN and changes no firm finding (M12).

**Waiting for the atlas** (Stage 3 changes to earlier readings; done in the Stage 3 web pass, ADR 0049): B13 (M5);
B17 (M7); B25 (the cohort order, M10); B29 (M14); B33 (M18); B37 (M25); B40, and B42 and B60 (M21, M22); B45 (M23);
B62 (M24);
and the framing pages' "What comes next" (Stage 3 under way).

**Next, in order:** the owner's review of section 8's tables and OQ26 (adopt the name-matched links?); then, at the
owner's word, the plan's "After Stage 3" (review the signals and gaps, source the gaps worth filling) and lifting
the freeze to carry the revisions above to the atlas. The notebook is the source. Its
cell ids are three-digit sort keys with a name (`111-rep`, `131-reach`): this session split the cells into files, ran a
section's cells with the setup cells (`031-setup`, `101-rights`, `201-firms`, `301-places`, `401-countries`) in one
Python process (about a minute), and reassembled the notebook by sorting on the ids; a full run takes about ten
minutes. New cells should keep the three-digit ids in order.

**The owner's decisions (2026-11-02, A22 to A24):** the full Stage 2 audit (`analysis/claude-audit/261102/`) is the
working list for Stage 2, in place of ChatGPT's four Stage 2 audits (A24); the survival pass comes next, with the fix to
the halves (S2 S8 R07), in a fresh session with a fresh context window (A23); and B8 stays a Stage 3 signal only as a
comparison within reach bands, worded as the share still in force and read beside B11 and B12 (A22, answering OQ24).

**The owner's decisions (2026-11-02, A25 to A27):** pass 6's restated readings adopted as they stand (A25); OQ25 added
to the request to IP Australia (A26); next, later additions not carried back in §5 to §8, with policy and fees (A27,
done as pass 7).

**The owner's decisions (2026-11-02, A28 and A29):** correct the website now, in plain English with graphs where
possible, with "Follow the evidence" precise enough for people in the IP ecosystem and nothing overstated (A28, done as
the web pass below); and Stage 3 begins, after a break, by taking up the methods the final review listed (A29). The
owner expects to open a pull request; publishing the pages (OQ19) waits on it.

**Wording (2026-11-03, A31):** Stage 2's paired figures are labelled. "How to read this notebook" and each lens's
"The two samples" say what the halves are (a random split by a hash of the key; leads found in the first half, checked
in the second) and how a pair is written (first half, then second; "interval" marks a 95% interval); B21 to B31, B35,
B50, B58 and B59 name the half where a pair could be misread; "halves" is in `GLOSSARY.md` and the atlas glossary, and
the atlas's "other half" reads "second half". No number changed.

**The owner's decision (2026-11-03, A30, ADR 0045):** Stage 3 adds a check of firms' IP counts: Australian
organisations' rights with no filer's ABN are matched by name to the ABR and ASIC, the match tested on rights with a
known ABN, kept in separate columns and never added to the counts; U44, U45 and the firm-count leads are rerun with it
(`docs/eda-plan.md`, the three stages). OQ7 (asking IP Australia) is still to send, the owner's call.

**Status (2026-11-03, latest): the web pass** (A28, ADR 0044). The evidence atlas matches the reviewed notebooks again.
131 of 186 pages had changed since the atlas was built (29 October 2026); each was rewritten from its current notebook
text (headline, statement, figures, points, chart, questions, preparation, steps, assumptions, limits), and the other 55
were swept for withdrawn readings ("never filed", "renewed", "moved overseas", "no link") and jargon. Plain English in
the main view; the precise definitions in "Follow the evidence" (the filer's origin and type, representation before
the renewal, shares over every employer). 40 more pages have a chart (178 of 186, quoted charts checked by the numbers
rule); a `share` chart format shows the notebooks' proportions as percentages; the build now checks each quoted chart's
shape (`build.chart_shape`, after U74's labels split at a comma). The drawn-from-data charts use `founding_australian`,
`founder_type`, `founder_country`, `ip_record` and U36's survival method (ADR 0041), and assert current figures. The
framing pages (overview, the ten Stage 1 findings, "What Stage 2 found", limits, corrections, "What comes next", the
lenses, the questions and the review against IP Australia) follow the notebooks. Checks: the strict build passes for all
186 pages; the tests pass in full; ruff is clean; the pages render in Chromium at desktop and phone width with no console
errors. **Next:** the owner's pull request and OQ19; then Stage 3, starting with the methods (A29).

**Status (2026-11-02): pass 8, a final review of Stages 1 and 2** (the owner's request: an in-depth review
before the website is updated; ADR 0043; the assessment is `docs/review-stages-1-and-2.md`; the record, finding by
finding, is pass 8 in `analysis/GPT-audit/261030/AMENDMENTS.md`). All 186 observations were read against the outputs
above them; both notebooks were re-run from a fresh build first (notebook 2 identical; notebook 1 identical but for two
tables' row order, now sorted); both summary documents were checked number by number; and the full Stage 2 audit's
open findings (S2 L5 R08 to R12, R14; S2 L6 R02 to R05, R07 to R09; S2 L7 R01 to R06; S2 S8 R03, R05, R08 to R10,
R12; S2 L1 R09, R37; S2 L2 R29, R30; S2 L3 R34; S2 L4 R25) were checked and, all holding, acted on in wording. 68
observations are restated with a dated "pass 8" line (31 of Stage 1's, 37 of Stage 2's): 26 for a figure the output
does not give, 39 for reading further than it allows, 3 for one selection error. Substantive: **U112, B50, B51**, the
share of WGEA employers that file is now over every employer (48.6% to 72.9% by size, not the lens's 70.4% to 82.5%;
the size gap for any filing 24.3 points); **U8**, organisations' provisionals rose too (3,060 to 4,558); **B31**,
manufacturers are not shown to file the patents; **B37**, seven of eight breaks; **B38**, FY2022 to FY2024 the base
after the innovation patent's closure; **B39**, Australians' and overseas applicants' trade marks move together year
to year; **U85, B46**, US patents' citations are not where research is used; **B62**, six ratios on one denominator.
New on the page: U40's batch date (`agent_first_date` is 12 May 2018 for 362,485 patents, so it is not used for
patents), exact values where rounded displays were read, B28's labels in full. `docs/stage-1-summary.md` (18 edits,
stale figures from before passes 2 and 6) and `docs/stage-2-summary.md` (20) brought into line; `GLOSSARY.md` gains
"Stability check" and "No association detected". No lens changes. **Not done:** the website (its plain English quotes
several restated observations; the atlas's numbers rule lists 61 observations out of step with the notebooks, most from
passes 1 to 7, which the web pass must carry over: `build.build(strict=True, write=False)` prints them); the new methods the audit proposes (listed for Stage 3 in the
assessment). **Next, the owner's call:** the web pass, OQ19 (Stage 3), and whether Stage 3 takes up those methods first.

**Status (2026-11-02): audit pass 7, later additions in §5 to §8, and policy and fees** (A27, ADR 0042,
`analysis/GPT-audit/261030/AMENDMENTS.md`). Eleven findings of the full Stage 2 audit (S2 L5 R01, R02, R03, R07, R13;
S2 L6 R01, R06; S2 S8 R01, R02, R04, R06), each checked first; all hold. **B37** now classifies each policy break
(mechanical, administrative, behavioural), sets it beside two control series and shows its window's months: the
behavioural breaks are Raising the Bar's rush (controls quiet) and perhaps the Designs Act's overseas step; at the
innovation patent's closure and the Patents Act 1990 a control moved too; all four candidate steps, not three, are
beyond every placebo in some series; the 20-year term's window is incomplete. **B47** names each of the five fee
breaks with its direction: one points the way a price would (Australians' designs after July 1988, which B47 had left
out), and the 1998 rush read as price-like is not. **B48's** interval resamples changes (-0.638 to 0.049). **B43**
states its scope and periods (FY2018 to FY2023 against FY2024 filing) and gains two passes through the crosswalk with
services. Later additions carried back: B37's fee sentence, B36 and B39 (B52, B56), §6's rules, B41 and §6.7 (the
crosswalk with services), §8's opening (what was screened, what was not, the PBS deferred to OQ8), B15 and B62 added
to §8's signals, firm size "known for WGEA reporters only", the summary's status line and WIPO's endpoints;
`screens.yaml`'s section numbers. No lens changes; notebook 2 re-executed; tests pass except the atlas's five, as
before. **Next, the owner's call:** the next theme on the audit's list ("Read first" item 5, what a count measures:
S2 L6 R02, S2 L7 R01, S2 L6 R04, S2 L7 R02; then §5's dependence and absence findings, S2 L5 R08 to R12), the web
pass, OQ19 (Stage 3).

**Status (2026-11-02): audit pass 6, the survival pass, done** (A23, ADR 0041,
`analysis/GPT-audit/261030/AMENDMENTS.md`). The 16 survival findings of the full Stage 2 audit, Stage 1's three on the
same theme and the fix to the halves (S2 S8 R07) were checked against the code, the lenses and both notebooks first:
all hold (S2 L1 R15 in part; R14's "Simpson's paradox" proved wrong). Fixed at the source: `kaplan_meier` takes
delayed entry (each right counted from its grant or registration, with three guards: entries clamped to the end, the
629 rights recorded as ending before their grant left out, curves starting once 30 are at risk); cohorts by the
financial year the term began; the rights lens gains `agent_first_date` (89 columns); `years_in_force` leaves the
screen (221 distinct leads, from 223); `bivariate.half_sql` is the one rule for every half, and `split_half` computes
it in DuckDB (a test checks); `GLOSSARY.md` restated and extended. Readings that change: **B8** is carried only within
reach bands (A22): within the same reach Australian organisations' patents are more often in force at 10 years (two
to four offices 71.8% against 65.1%; five or more 75.6% against 66.5%), but not among Australia-only patents, and the
three signals (B8, B11, B12) disagree; **B10's** representation gap, read before the first renewal, is 19.1 points
(23.4 "at any time": marks whose agent arrives after 9.5 years are 89.5% in force); **B13** has no composition effect
and a small link in both periods (3.7 and 1.0 points), with work-sharing requests (the Global PPH, 2014) mixed in;
**B49** has one change that survives every check (trade marks, July 1993), and September 2002's patent step is within
the ordinary against the trend; **U36's** patent shares are 1 to 4 points lower (2000s 67.5% in force at 10 years) and
its design and second-tier cohorts follow the Acts. The halves' rerun (B35, B50, B58, B59) changes no reading; B58's
halves are now §3's. §1.9, §5.7, §8, both summaries, U36's rows and the owner questions (OQ25 proposed, for IP
Australia: PPH requests and the 2011 and 2012 rise) updated. Two faults of this pass were found and fixed before
committing (delayed entry without guards took trade mark curves towards 0%; a first start threshold of 100 dropped
small groups). Tests: 122 pass; the atlas's five fail as before; the benchmark is unchanged. **Next, the owner's
call:** the next audit theme (the index's "Read first" list: later additions in §5 to §8, S2 L5 R01, S2 L6 R01, S2 S8
R01, R06; policy and fees, S2 L5 R02, R03; what a count measures), the web pass, OQ19 (Stage 3), and whether to add
OQ25 to the request to IP Australia.

**Brief for this pass (done above): the survival pass (A23).** Work from the table "The survival theme in one place" in
`analysis/claude-audit/261102/INDEX.md` (16 findings: S2 L1 R11 to R15, R30, R32 to R36; S2 L5 R04 to R06; S2 S8 R03 and
R05), with Stage 1's findings on the same theme (S1 L0-L1 R20, R21 and S8-S9 R10, in `analysis/GPT-audit/261030/`, which
the audit did not recheck), and the fix to the halves (S2 S8 R07: one hash function for every half; then B35's GII
split, B50, B58 and B59 again). As in passes 1 to 5: check each finding against the code, the lenses and both notebooks
before changing anything; correct at the source (`build.py`, `bivariate.py`, `screens.yaml`, `GLOSSARY.md`) so that one
fix carries everywhere; re-execute the notebooks; restate each observation with a dated line; carry the changes into
§1.9, §5.7, §8, both stage summaries and U36. For B8, follow A22. Record it as pass 6 in
`analysis/GPT-audit/261030/AMENDMENTS.md`, so one log holds every pass, citing findings as the audit does (the earlier
numbers are shared), with an ADR (0041). The website stays a separate pass.

**The owner's decision (2026-10-29, A16):** update the website with all of Stage 2's findings and changes (done, ADR
0035). **(2026-10-28):** begin Stage 2 (A14); update the website only once all of Stage 2 is finished.
**The owner's decisions (2026-10-26):** address the three remaining `rights` attachments (done: the links, Google
Patents and the inventors); before that, complete the `institutions` lens (done: core, its IP detail and every source
mapped to it); before that, go on to the `industries` lens (done: core and attachments); before that, commence the
`national` lens (done). **(2026-10-25):**
after the `firms` lens, the owner asked for the `regions` lens to be
completed (done: core and attachments). Before that, after the events attachment, the owner adopted years in force (U36, with
unfinished rights kept) as a working measure for Stage 2, on condition that it is used alongside other signals, and
asked for the `firms` lens next. They will try to find out from IP Australia why provisionals rose (U8) and why trade
mark expedite requests fell in November 2018 (U34). Earlier: the events attachment (B5) before `firms`; N01 and N06
settled (ADR 0010).

**Status (2026-10-29, latest): Stage 2 is in the evidence atlas** (ADR 0035, A16). `analysis/atlas` now reads both
notebooks (`notebook.read_all`; each observation carries `stage`), and Stage 2's plain English is in
`analysis/atlas/content/observations/stage2/<lens>.yaml` under the same numbers rule; the sixteen Stage 1 observations
added while filling the gaps (U108 to U123) are in the Stage 1 files. 186 pages (124 Stage 1, 62 Stage 2); 30 of
Stage 2's have quoted charts, 31 the notebook's own. The site shows the stage everywhere (a filter, chips, lens pages
grouped by stage, Stage 2's evidence first on question pages), the overview has "What Stage 2 found", and the
limits, lenses and "What comes next" pages follow `docs/stage-2-summary.md` (Stage 3's tests, OQ18 and OQ20 to OQ22,
the gaps filled and those left). Corrections found on the way: the published "What comes next" page did not render
(OQ13's item read as a YAML mapping; quoted, and a test checks those lists); U23's "17th" figure was no longer on its
notebook page (reworded); the rights lens page still gave the count before the design shells were dropped (now
4,356,908 rights, 86 columns). Every page was loaded in a headless browser (no console errors, no horizontal scroll
at phone width). Tests: `tests/test_atlas.py` runs again (6 tests). **Next, the owner's call:** publish (merge to the
branch Pages serves) and Stage 3 (OQ19); B10's harvest is still to finish.

**Status (2026-11-02): Stage 2 audited in full** (`analysis/claude-audit/261102/INDEX.md`). The owner asked for
a new audit of all of Stage 2: review ChatGPT's Stage 2 audits, written before passes 1 to 5, and continue to the end,
in the same format, leaving the website for another pass. Eight files, one per notebook section, and an index. Of
ChatGPT's 115 Stage 2 findings (§1 to §4), the passes resolved 20, 19 hold in part and 76 hold; none was wrong. The
audit read the helpers and definitions as well as the notebook (nothing re-run) and adds 52 findings (26 High): §5 (14),
§6 (9), §7 (6), §8 with the method and `docs/stage-2-summary.md` (12), and 11 across §1 to §4. The main ones: "the
halves" are drawn by two different hash functions (DuckDB's in the screens, pandas' in `split_half`), the cause of the
places lens's unreconciled halves (S2 S8 R07); later additions not carried back in sections no earlier audit covered
(B37 says the fee history is not in the data; §6 says the crosswalk with services is still to come; §8 says every
companion table was screened); breaks the law makes certain counted as natural experiments, and B47's counts mixing
falls with rises (S2 L5 R02, R03); B49's heading contradicting its bullet (three renewal changes beyond every placebo,
not one); B39's own table contradicting it (overseas applicants' trade marks move with Australians', 0.785); B38's
follow-up measure breaking in August 2021, when innovation patents closed; counts allocated by the crosswalk read as
divisions' filing; B62's six ratios on one denominator; and the summary document's "Value made here is often owned or
used elsewhere", which its own body contradicts. For the survival theme, next on the list, the index gathers 16 findings
in one table: the screen treats unfinished lifetimes as finished (B4), "in force after N years" means different things
for patents and trade marks, survival is read as renewal and value against U36 and A1, and B10 compares renewal by a
representation measure that renewal itself can create. OQ24 asked whether B8 stays a Stage 3 signal (A1's "alongside
other signals"); the owner answered the same day (A22, below). Pointers added in `CLAUDE.md`, `README.md` and the
earlier batch's `INDEX.md`. No notebook, code or website changes. **The owner's decisions (2026-11-02, A22 to A24):**
yes to all three: B8 stays a signal only within reach bands; the survival pass next, with the hash fix, in a fresh
session; this audit is the working list for Stage 2. **Next:** the survival pass, from the brief at the top; then the
web pass and OQ19 (Stage 3), the owner's call.

**Status (2026-11-02): audit pass 5, recorded ownership read at two endpoints** (A21, ADR 0040,
`analysis/GPT-audit/261030/AMENDMENTS.md`). The theme "recorded ownership changes read as complete ownership
histories" (S1 L0-L1 R16, S8-S9 R07, S2 L1 R25, R26, S2 L2 R19) was taken with S2 L2 R18 and R20 (B26's unit and
reach): seven findings, all holding. Ownership is now read at two endpoints (an Australian founding applicant, no
Australian holder now), never as moves, transfers or exported value (U17 to U19, U35, B19, B26, B46, §1.7, §2.5, both
summaries). Pre-FY2003 assignments are an incomplete indicator of unknown coverage, not two-thirds. B19 shows the
composition of overseas-held patents beside the rates (44.22% single-office in FY2003 to FY2011), with unknown reach
counted; B26 shows firm-level counts (the youngest firms 4.34% against 3.63%, then 2.96% against 3.33%), each band's
largest firm (up to 44.26% of a band) and the ABN join's party alignment (4.56% jointly founded). B26's lead weakens to
no clear difference by firm. U19's ABN range (provisionals 1.739% left out) and state figures were stale; fixed. No
lens changes; notebook 2 re-executed. **Next, the owner's call:** the next theme (survival read as renewal or value:
S1 L0-L1 R20, R21, S8-S9 R10, S2 L1 R11, R12), the web pass, OQ19 (Stage 3).

**Status (2026-11-02): audit pass 4, first observed filing, firms' age and reproducible builds** (A20, ADR
0039, `analysis/GPT-audit/261030/AMENDMENTS.md`). The owner asked for the next audit theme, looked at deeply and
widely. The theme (first observed filing read as entry) was taken with the four findings on the same age computation:
seven findings, five holding in full and two in part. One part is not confirmed: IP RAPID's known-origin design
shares are lower bounds, as IP Australia's own counts show (D1). Fixed in the back end: the firms lens gains
`*_first_date_filled` (54 columns), and `age_truncated` is empty for the 32,600 undated firms (it read "not truncated").
Notebooks: U101 shows that 4.32% to 9.1% of each year's first observed trade mark filers were already linked to IP, so
"first observed linked", never "entry"; B25 is rebuilt from dates (17% to 20% of first filings are dated before the
firm's first registration, so recorded ages are not lower bounds for one firm in five; medians 2.61, 5.22 and 5.24
years; within firms the trade mark comes first for 72.86%); B26's young-firm lead now holds for FY2003 to FY2011
only. The wider check found two defects the audits did not: notebook 2's `AGE` grouping put undated firms in "20
years or more" (no table moved, since they are all inactive or outside the ABR), and the build was not reproducible.
Parallel sums of fractions differed in their last digits between builds (383,271 values of `region_indicators`, most
rows of `industries`), flipping one of B28's leads from run to run. `build._exact_sum` now adds them exactly, and two
full builds agree in all eleven lenses. U119's cube labels, §1.9's U99 row and the Stage 1 summary's FY2024 rule were
also stale. Both notebooks re-executed; tests pass except the atlas's five, as before; the benchmark is unchanged.
**Next, the owner's call:** the next theme (recorded ownership read as complete: S1 L0-L1 R16, S8-S9 R07, S2 L1 R25,
R26, S2 L2 R19, with S2 L2 R18 and R20 on B26's "moved overseas"), the web pass, OQ19 (Stage 3).

**Status (2026-11-02): audit pass 3, later additions carried back** (A19, ADR 0038,
`analysis/GPT-audit/261030/AMENDMENTS.md`). The owner asked for the audit work to continue, correcting what holds.
Pass 3 is the sweep passes 1 and 2 proposed: the 25 findings, across all twelve audits, that material added later
(the data gaps filled after Stage 2, the register's fills, passes 1 and 2) was not carried back. All were checked
against both notebooks, the rebuilt lenses and both stage summaries: none is false, 19 hold in full and 6 in part.
Corrected: three attachment inventories that called a subset the total (`region_indicators` 28,960,234 rows, not
22,511,923; `national_indicators` 41,230,072; `industry_indicators` 1,425,157), now printing the reconciliation; leads
and decisions left standing after they were settled (U34 by U103, U27 and U29 by U38 and U39, U45 by U100 and U101,
U49 by U87, U75 by U114, the fee history, B11 and B12 by B55, B61's "B34's gap holds"); stale counts and pointers (U0's
lens table, U22's 79 columns, U23's 18 series, §9's section numbers, §3.7's B28 count); and qualifications dropped in
summaries (U53, B29, "divisions near certain", "named most often"). A false caption fixed (designs' origin is unknown
for 4.0% to 25.1% a year, not "recorded for few"). Three small outputs put existing claims on the page: gross value
added's profile (U73: 19 divisions, FY1990 to FY2026; manufacturing 14.2% of the divisions' sum to 6.0%), 683 WGEA
reporters under 100 employees (U112) and U120's 2023 value. `docs/stage-1-summary.md` was further behind than the
audits saw (its firms section predated the register's ABNs: 398,450 ABNs and five schemes, now 463,279 and six) and is
restated, as are `docs/stage-2-summary.md` and `docs/eda-plan.md`'s lens table. No conclusion carried to Stage 3
reverses; three narrow (B11 and B12 from FY2010; B61 no longer evidence of under-patenting; value added reopens a
longer industry comparison). Notebook 1 re-executed whole; notebook 2's changes are text only. **Not done:** the
website (its tests stop at the numbers rule, as after passes 1 and 2); the other open themes in `INDEX.md`. **Next,
the owner's call:** another audit theme (the largest left: first observed filing as entry, survival read as value,
recorded ownership as complete, geographic allocation), the web pass, OQ19 (Stage 3).

**Status (2026-11-02): audit pass 2, origin is the filer's, is corrected in the back end** (A18, ADR 0037,
`analysis/GPT-audit/261030/AMENDMENTS.md`). ADR 0013's rule (who files uses the founding applicants) and ADR 0024's
finding (a founding applicant in Australia is IP Australia's resident) now hold everywhere: the `timeline` lens's
origin series (`ORIGINS`) and the `industries` lens's Australian counts use `founding_australian`, not the current
holder's `australian_applicant`. `rights` gains `filer_group` (origin and type from one party: the first founding
applicant in Australia, else the first with a known country; empty when origin is unknown) and
`founding_australian_filled` (the register's fill only while a right has not changed hands); 88 columns. `regions`
counts organisations' filings by the party that gives the postcode. Notebook 1's filer claims (U7, U8, U13, U15,
U16, U20, U67, U90 to U94, U98 to U102, U105 to U107, U115, the timeline's U22 to U29 and the industries' U76, U114)
and notebook 2's (`FILER` from `filer_group`: B5 to B19, B55; places B27, B28, B31, B58; timeline B36 to B39, B47 to
B49, B52, B56; industries B40, B41) re-executed and restated, each with the earlier figure where a reader might have
used it. The changes are small (standard patents' Australian share by up to 0.7 points a year), but two conclusions
moved: B47's fee changes show 3 rushes and 2 steps beyond placebos (not 4 and 3; the Designs Act's overseas rush is
now ordinary), and U7 no longer gives trade marks' FY1995 share. U67 now shows both IP Australia's definition (median
1.011 of the World Bank's residents) and the first founding applicant's (1.001, nearer WIPO's first-named applicant).
The benchmark against IP Australia is unchanged. **Not done:** the website (its tests stop at the numbers rule, as
after pass 1); `founder_abn` keeps its own selection rule (ADR 0016). **Next, the owner's call:** the sweep of later
additions not carried back, the web pass, OQ19 (Stage 3).

**Status (2026-11-01): audit pass 1, the firm filing population, is corrected in the back end** (A17, ADR
0036, `analysis/GPT-audit/261030/AMENDMENTS.md`). The owner asked for the most urgent cross-cutting issue in the
audits, verified before acting. Of the recurring themes, the one that held and moved numbers was "has filed IP": the
`firms` lens had three definitions, and the `regions` lens counted firms from IP RAPID's own applicant panel, which
predates the register's ABNs (ADR 0029), so 60,021 firms whose filings only the register links were invisible to it.
Now `firms.ip_record` is the one flag (filed by either rule; another link to IP; none), and `regions` counts by it:
active IP-filing firms 207,537 (162,359 before); `rdti_firms_no_ip` became `rdti_firms_no_filing` (48.3% of
claimants, against 50.7% "never filed") with `rdti_firms_no_ip_link` beside it (44.7%). Both notebooks re-executed
whole; restated: U41, U42, U44, U47, U54, U112, B23, B27, B28, B50, the summaries and both stage summaries. Two
conclusions changed: IP filers are no more advantaged than firms in general (U47), and another link to IP explains
little of B23's group (10.9% of the oldest, not the 54.3% first given, which had the wrong denominator). "No filing
linked", never "never filed" or "missing filers" (GLOSSARY). Checked: the holder-versus-filer origin theme is real but
small (shares move by at most 1.02 points; `timeline` and `industries` still take origin from the current holder):
proposed as pass 2 (OQ23). **Not done here: the website.** The atlas still quotes the old figures, and
the five tests in `tests/test_atlas.py` stop at its numbers rule until it is rebuilt (pages for U47, U54, B23, B27
and B50 quote figures no longer in the notebooks); every other test passes (119). **Next, the owner's call:** OQ23 (pass 2), the web pass, OQ19 (Stage 3).

**Status (2026-11-01): the external notebook audits are indexed.** Twelve audits of the notebooks (Stage 1 §§1 to 9;
Stage 2 §§1 to 4) arrived in `analysis/GPT-audit/261030/` as uploads: 348 findings, 215 High and 133 Medium. Nothing
in them has been acted on. `analysis/GPT-audit/261030/INDEX.md` maps each audit to its notebook section and
observations, gives each one's section map and "read first" findings, the themes that recur across audits, how to cite
a finding (R-numbers are local to each file) and a freshness check (both notebooks still match the SHA-256 the audits
read). Not yet audited: Stage 2 §§5 to 8 and Stage 3. Pointers in `README.md` and `CLAUDE.md`. **Next, the owner's
call:** whether and in what order to work through the audits' actions.

**Status (2026-10-29, earlier): filling the data gaps** (A15, `docs/data-gaps-brief.md`), in its order. Done so far:
- **A1, the fee history** (ADR 0031): `frl_fees` reads every version of the fee regulations from the Federal
  Register's API (EPUB tables of 160 compilations; `gaps.yaml` holds the 1980s and 1990s from the amending
  instruments, every one listed and checked); `key_fees` (23 fees, 49 series, 285 spells), `fee_changes` (39). A test
  checks today's against `ipa_fees`. Attached: the timeline's `fee_*` columns (nominal; six costs also real, June 2026
  dollars) and `fee_changes`; `policy_events/events` gains each change (lever "fees"), kept out of the timeline's
  `policy_events` column so Stage 1's 17 changes are unchanged. Notebook 1, 5.7 (U108 to U111); notebook 2, 5.4 (B47
  to B49): fee changes rarely moved filing or lapsing beyond placebo months; the exception is patent cessations after
  the September 2002 renewal rise.
- **A2, ALP's crosswalk with services**: `concordances` adds `alp_ipc4_isic4_services` and `ipc4_anzsic_services`;
  `industries` adds `patents_standard_with_services` and `patents_standard_au_with_services` beside the main counts.
  U114 (6.5); B53, B54 (6.4): patents reach all 19 divisions and follow business R&D per business (0.739).
- **A3, firms' size and industry** (ADR 0032): `wgea` (WGEA's public data, employers of 100 or more, by ABN, with
  ANZSIC class and size); `firms` adds `wgea_*` (7,126 firms). U112 (2.6); B50, B51 (2.6). Nothing free covers small
  firms: OQ20 asks the owner whether to pursue it.
- **B1, the RBA's cash rate and exchange rates**: `rba`; the timeline adds four columns. U113 (5.8); B52 (5.5).
- **A4, families by origin and Google Patents' coverage**: `wipo_ipstats` adds indicators 20 and 22 (families by
  origin, all and foreign-oriented). U115 (4.5); B55 (1.8): older Australian families' filings abroad are linked
  incompletely (PCT route "Australia only" 63.43% in FY2000 to FY2009, 11.53% after), so family measures for
  Australian applicants are read from FY2010 on. OQ21 asks whether to repair the older links (EPO OPS needs an
  account).
- **B2, the national accounts**: `abs_national_accounts` (key aggregates, state final demand, value added by
  industry). The timeline adds `gdp_cvm`, `gdp_current`, `sfd_<state>`; industries adds `gva_cvm`. U116 (5.9); B56
  (5.6), B57 (6.5).
- **B3, ATO individuals by postcode**: `ato_postcode` (Table 6, 2012-13 to 2023-24; a unit-less "Number of
  individuals" in some years is read as a count). In `region_indicators` as `ato_postcode`. U117 (3.6); B58 (3.5).
- **B4, business characteristics 2024-25**: `abs_bcs_cubes` (every cube; the ABS published no 2023-24 release). In
  `industry_indicators` as `bcs_cubes`; tables by innovation status keep their block in the indicator. U119 (6.6);
  B60 (6.6).
- **B5, court judgments after 10 March 2025: not filled.** The legal corpus has no newer release, the Federal Court's
  pages refuse this environment (403; AustLII too), and its RSS feed holds only titles and catchwords from January
  2026. OQ22 asks the owner.
- **B6, the Census time series**: `abs_census_tsp` (T01, T02, T29, T34, T35 for SA2s, 2011, 2016, 2021), apportioned
  to postal areas in `region_indicators` as `census_tsp`. U118 (3.7); B59 (3.6).
- **B7, supplementary GII values** (ADR 0033): `abs_schools` (Table 53a) and the ABS's four R&D surveys give four of
  the six indicators the GII leaves blank for Australia, as `gii_supplementary` rows in `national_indicators`, never
  in the GII's own rows. U120 (4.6); B61 (4.4). Microfinance (4.1.3) and utility models (6.1.3) stay blank.
- **B8, OpenAlex's "cited at least once" filter**: `audit.openalex_filter` samples 20,000 patent-cited works outside
  the harvest (about 200 OpenAlex calls, free). About 5.6% more patent-cited Australian works exist (3.5% to 8.3%),
  2.4% lost to the filter and 2.9% to merged ids. Not worth a re-harvest. U121 (7.7).
- **B9, the NSRC**: `nsrc` (unit records 2000 to 2015, free on data.gov.au; no request needed), joined by name to the
  institutions lens (`nsrc_*`; six aliases in `names.csv`, source nsrc). U122 (7.8); B62 (7.3).
- **B10, the missing AusTender amendments: measured and coded, not yet harvested.** `audit.austender_amendments`
  sampled 500 contracts in each end-date band: 7.6% of those that ended in the year before 30 August 2019 have
  amendments the corpus lacks (7.2%, 5.4% and 1.6% in earlier bands), and their value is heavy-tailed (one contract
  adds $88 million), so OQ3's "under 1% of value" does not hold for recent contracts (ADR 0034). `austender` now also
  asks by id for every contract that ended in the four years before then (`_ended`, 234,313; raw `RAW_ENDED`), but
  the harvest takes about nine hours at 7 to 8 a second and a cloud session's container does not keep it running
  while the session is idle: the first attempt stopped after 8,000. To finish: run it where it can go uninterrupted
  (`uv run corpus run austender`, or only this part with `austender._harvest_by_id(ctx, austender._ended(bulk),
  name=austender.RAW_ENDED)`, saving the context, then `uv run corpus reprocess austender`); it caches by batch, so a
  rerun on the same machine resumes. Then `uv run corpus run linkage`, rebuild `firms`, `regions` and
  `institutions`, re-run the notebooks, and check the observations that quote AusTender numbers.
- **B11, the PBS with Section 100**: `pbs/monthly` (the monthly workbook, July 2022 on, every section); the timeline
  gains `pbs_*`. Section 100 is about 30% of the government's cost. U123 (5.10). No Stage 2 pair (waits for OQ8).
- **Notebooks:** re-run whole after each addition; no earlier output changed except row order in two unordered
  tables of notebook 1 (sections 1.8.4 and 7.4) and a float tie (industries overview, 700 or 699 distinct; the
  regions overview's 1.0% or 0.9%), none quoted. Stage 1's overviews of the attachments (3.5, 4.4, 6.4) and Stage
  2's B28 and B39 screens leave out the sources added after Stage 2, so their outputs and the observations quoting them stand;
  the new sources have their own sections. Sections after an addition are renumbered (summaries move down one). The
  A4 and A2 sections of notebook 1 were moved before their lens's summary (each summary had shared a cell with the
  last observations), and three summary tables of notebook 2 whose new rows had been appended after their closing
  text were repaired.
- **Next:** finish B10 (above: a nine-hour harvest that needs an uninterrupted run); then the gaps are done except
  B5 (OQ22). The owner's items: OQ20, OQ21, OQ22.

**Status (2026-10-28): Stage 2 is complete** (A14; B1 to B46, `docs/stage-2-summary.md`), in `analysis/notebooks/02_bivariate.ipynb`, with the method
of ADR 0030. **The website (evidence atlas) is not to be updated until all of Stage 2 is finished** (the owner's
instruction, 2026-10-28): leave `evidence/` and `analysis/atlas/` alone until then.
- **Method:** each lens section screens every pair of its variables on one 0-to-1 scale (|Spearman rho|, the rank
  correlation ratio, bias-corrected Cramér's V), set column by column in `analysis/eda/screens.yaml` (a test checks
  it names every column of `variables.yaml`); a lead must be at least 0.1, pass a Benjamini-Hochberg false discovery
  rate of 5%, hold again in a replication sample (a second decade for `rights`, the other hash half of the key for
  `firms` and `regions`) and not be "by construction" (the yaml's `groups`). Then the planned pairs of
  `docs/stage-1-summary.md` section 7, each with intervals, in two periods or halves, third factors named. Helpers in
  `analysis/eda/bivariate.py` (`run_screen`, `replicate`, `distinct_leads`, `leads_table`, `rate_difference`,
  `ratio_by`, `survival_with_interval`, `dot_chart`); terms in `GLOSSARY.md`.
- **How the notebook is made:** I generated it from section files (cells as text) and executed it whole with
  `nbconvert` (about 7 minutes for sections 1 and 2; the screens are seconds, the full-sample bootstrap intervals
  minutes). A later session can edit the notebook's cells directly; keep each observation's numbers on the page.
- **Section 1, `rights` (B1 to B19):** 223 distinct leads over six types, the decades agreeing (rho 0.859). Mechanics
  and quirks recorded (B2, B3: IP RAPID gives no origin for designs never registered; the register fills it). Signals:
  standard patents filed alone are granted about 36 points less often (Australian individuals, both decades, also among
  those examined; B6) and trade marks about 23 to 24 points (B6); Australian organisations keep granted patents longer
  than overseas ones, within fields too (B8); lone filers and Australian individuals renew trade marks and designs
  least (B10); Australians' lower citations are mostly narrower reach (B12); expedited patents last longer only for
  overseas organisations, the pooled link being Simpson's paradox (B13); one patent in seven made in Australia is
  filed from overseas (B16); women among inventors vary by field (4.2% to 26.9%, order stable; B17) and, on
  provisionals, organisations' inventors include about 5 points more women than individuals' (B18); the patents that
  move overseas are the wider and granted ones (B19). Not replicated: the origin gap in time to grant (B7), organisations'
  lone-filing gap (B6).
- **Section 2, `firms` (B20 to B26):** looked within groups that entered the lens through another door (R&D
  claimants, government suppliers, large taxpayers), because the lens's own make-up drives several screen leads (B21).
  Filing IP goes with company form, age and cities, and with advantaged postcodes for suppliers only (B22); R&D spend
  goes only weakly with patenting (rho 0.12), and missing filers are mostly young private companies (B23); suppliers
  with IP win more and larger contracts within each entity group (B24); firms file a first trade mark at about 2
  years, a first patent at about 4.6 (B25); the youngest firms' patents move overseas most (B26, small numbers).
- **Section 3, `regions` (B27 to B31):** the lens's own pairs (IP measures move together, and with the education and
  occupation index IEO most, B27); every one of 6,406 attached indicators screened against six IP and R&D rates
  (24,792 of 38,217 pairs are leads, along one gradient of advantage, education and business density, B28); negative
  binomial models (started from a Poisson fit, which they need to converge): 1.7 to 1.9 times the standard patent
  rate per standard deviation of IRSAD, remote areas far lower, both holding together and in SA3s (B29), and without
  each area's largest filer (B30); business mix: finance, property and professional services up, construction and
  transport down, manufacturing flat (B31, read with U47).
- **Section 4, `national` (B32 to B35):** indicators screened across countries (2016-2020 against 2006-2010, counts
  per million people; `screens.yaml` names each indicator's ratio): IP moves with R&D, research and income as one
  development gradient, trade marks with commerce (B32); Australia's rank among OECD members (B33: patents middling,
  trade marks and business entry near the top, business R&D 13th to 20th, manufacturing last); residents' patenting
  rises about one for one with business R&D across members, Australia near its prediction in 2016-2020, but changes
  in R&D barely go with changes in patenting (rho 0.165, B34); the cross-country attachments (GII values, OECD MSTI,
  venture capital, well-being, SDG 9) screened against residents' patenting (B35). Australia-only sources (ABS,
  BCARR, MWM, Closing the Gap) have no other country to pair with; they go to section 5 as annual changes. The OECD's
  patent tables (counts of patents) and business demography cells are not screened (recorded in 4.3).
- **Section 5, `timeline` (B36 to B39):** series compared as quarterly year-on-year log changes (1991Q3-2008Q2
  against 2008Q3 on): one lead only (trade mark registrations × oppositions), no common cycle (B36); the eight policy
  candidates of U28 against placebo months five years either side: both rushes, three steps and the 1995 pauses are
  outside every placebo, Australians' designs after the 2003 Act and the 1991 commencement month are not (B37); FY2025
  provisionals followed by an Australian complete application within 12 months fell (individuals 6.66%, against 12% to
  19%), but Australian filers' priority claims are thinning in the latest years too, so late recording is possible
  (B38, proposed OQ18); Australia-only annual series give context, not signals (B39).
- **Data gaps found:** firms' industry and size (the third factors most firm leads need; BLADE stays ruled out);
  whether Google Patents holds older Australian-only families fully (B11).
- **Section 6, `industries` (B40 to B43):** 19 divisions, FY2024 against FY2025: trade marks per business follow
  business R&D per business (0.709; 0.682) and fall where a division has many small businesses; patents reach 8
  divisions only (the crosswalk excludes services), so R&D and patenting go together only loosely (0.465, interval
  wide); the business survey's innovation-active share does not consistently go with filing; one of 2,157 division
  indicators passes the correction.
- **Section 7, `institutions` (B44 to B46):** 2017-23 against 2010-16, as rates per 1,000 works: the kind of
  institution sorts most measures; universities' patents per work follow size (0.743; 0.732), patent-cited research
  and ARC success, not industry-partnered grants; 3% to 5% of US patent citations to Australian research come from
  patents with Australian links. The IP detail (`institution_rights`) is screened in halves.
- **Section 8 and `docs/stage-2-summary.md`:** the signals carried to Stage 3, what is recorded but not carried, third
  factors and data gaps.
- **Next (the owner's decision, 2026-10-28, A15): fill the data gaps, in a fresh session,** from
  `docs/data-gaps-brief.md` (every gap, its source, its lens and what done means; A1 the fee history first). Still the
  owner's call: (1) whether and when to update the evidence atlas with Stage 2 (the owner asked that
  the website wait until Stage 2 was finished; it is now, and the atlas would need Stage 2 pages built the way Stage
  1's were, ADR 0023); (2) Stage 3; (3) whether to add OQ18 to the request to IP Australia.

**Status (2026-10-27):** **The register's fills are in the lenses** (ADR 0029), at the owner's decisions (A12:
use the fills; A13: reword the request). `ipa_register` read every trade mark and design (2,338,036 and 269,048) and
`ipa_provisionals` is reading every provisional with its inventors (about nine hours, in runs of under two hours:
`IPA_BUDGET_MINUTES=112 uv run corpus run ipa_provisionals`, repeated until it saves; the cache is in
`~/.cache/ipholmes/ipa_provisionals`). The rights lens has the filled columns beside IP RAPID's (`filer_abn`,
`australian_applicant_filled`, `register_expedited` and others); firms are credited by `filer_abn` and the spine has
463,279 ABNs; 11,098 empty design records are dropped (`analysis/eda/dropped/design_shells.csv`). Notebook 1.8.6
(U99 to U104) restates U45 (ABN linking 92.3% to 90.9%, FY2024 to FY2026; first-time trade mark filers 19,730 in
FY2026), U7 and U13 (designs 32.31% Australian, 0.007% unknown) and U34 (priority-claiming marks expedited every year);
figures moved by the drop are corrected and the atlas follows (105 observations). OQ6, OQ7, OQ13 and OQ14 are
reworded. The provisional harvest is done too (`ipa_provisionals`: 264,260 numbers, 181,469 inventors; five runs, one
container restart, resumed from the cache): `rights` has `register_inventors` and its expected women and men, profiled
in 1.8.7 (U105 to U107; atlas 108 observations). **The owner agreed (2026-10-28, A14):** Stage 2 and the gender analysis go ahead (provisionals from FY2003, each
year's coverage shown); OQ17 (provisionals' missing inventors since FY2024) joins the request to IP Australia; the
branch goes to a pull request, and the atlas is published when it merges. **Next:** Stage 2.

Before that, the same day: **IP RAPID checked against IP Australia's live register** (ADR 0028,
`docs/audit-ipa-api.md`), after the owner obtained API access (credentials in the environment: `IPA_API_*_DEV` is
production, `IPA_API_*_TEST` the test host). The client is `src/corpus/ipa_api.py` (`python -m corpus.ipa_api get
trade_mark 1000000`; guide in `docs/ip-reg-api/README.md`); the harvest is a corpus source, `ipa_api` (about two
hours); the comparison is `python -m audit.api_check --live` (seconds, plus the live yearly counts). Findings (V1 to
V14): IP RAPID is complete to within the week since its release and its fields agree with the register's in 99.7% to
100% of a random sample of every right; Madrid marks are dated by IP Australia's notification and PCT patents by
national phase entry, by definition. Its gaps are in what it publishes: the register holds an ABN or ACN for 83.8% of
the OQ7 marks, a country for 61.4% of the OQ14 designs (which reproduces IP Australia's resident design counts, D1),
and "Examination expedited" on every priority-claiming mark since FY2020 (OQ6: U34's break is publication). Trade mark
numbers 1,978,060 to 1,980,352 were never used. No lens or observation is changed. **Next is the owner's call:** OQ15
(attach the fills to `rights`) and OQ16 (reword the request to IP Australia); then Stage 2. Production's patent API
fails about half its calls at random; the client retries. Added after the owner's questions (V15 to V17): the
register names inventors where Google Patents has none (standard patents before 1970, provisionals since 2000;
about 350,000 rights, projected, days of fetching); the undated designs are 1973 to 1982 shells; and of the designs
still without a country, 15,154 of 15,730 have no owner on record anywhere.

Before that, the same day: **OQ6, OQ7 and OQ13 rechecked on a fresh IP RAPID release** (ADR 0027,
`docs/recheck-oq6-oq7-oq13.md`), at the owner's request before taking them to IP Australia. `analysis/audit/recheck.py`
reads the 26 October 2026 release raw from data.gov.au, without the corpus or lenses, and reproduces U34, U45 and D2.
None is a misclassification in how we read the data, but two are now explained further:
- **OQ6:** the expedite fall is almost all in marks claiming convention priority: 95.97% to 97.81% of them carried
  the event to FY2018, against 0.06% to 0.16% since FY2020. Other marks: 4.81% to 6.11%, then 3.60% to 4.87%, no
  break. This looks like recording.
- **OQ7:** the ABN goes missing from July 2024 for applicants new to IP Australia. Companies under a year old: 89% to
  90% with an ABN, then 10.1% (FY2026). ASIC shows they have ABNs, and the ABNs are not added later.
- **OQ13:** WIPO's own count of designations of Australia in 2018 (15,943) agrees with IP RAPID's Madrid marks
  (15,836, 0.9933), not with the IP Report 2019 (about 17,830 implied). So the report's 2018 count is probably the odd
  one out. Trade mark numbers 1,978,060 to 1,980,352 are missing from every table, but probably were never used.
  WIPO's Madrid Monitor was not searched mark by mark: its terms forbid automated queries and bulk downloads.

The three questions and the atlas's "What comes next" page are reworded (old wording kept); the observations are not
revised (ADR 0026). **Next is the owner's call:** send the reworded questions; whether to adopt R5 (U34 compared across
2018 among marks without a priority claim); Stage 2. The corpus's IP RAPID is a week behind (19 October); `corpus run
iprapid` refreshes it.

Before that, the same day: **The atlas's framing follows the audit** (ADR 0026). The owner clarified that only
the substantive analyses (the observations) stay unchanged for now, so the "What comes next" page now carries OQ5 and
OQ7 as reworded (A10) and OQ12 to OQ14 (A8), drops U67's puzzle (closed by the audit), adds the audit's Stage 2 pair
(expedited examination against years in force) and moves IP Australia's statistics out of the data worth adding. The
observations in `atlas.json` are still byte for byte as Stage 1 left them; a pointer from each observation page to its
verdict waits for the owner with the revision of the observations.

Before that, the same day: **The audit is in the evidence atlas** (ADR 0025), as the owner asked: a page of its
own, "Checked against IP Australia" (`#/audit`), built by `python -m atlas.build` from the audit's record
(`docs/audit-ip-australia.md`, whose tables give each observation's verdict), the benchmark's outputs and plain English
in `analysis/atlas/content/audit.yaml`, under the numbers rule. The notebook and every existing atlas page are
unchanged (the observations in `atlas.json` are byte for byte as before), by the owner's instruction "at this stage".
The owner also sent OQ12 to OQ14 to IP Australia (A8) and had OQ5 and OQ7 reworded to ask what IP Australia's reports
leave open (A10). Tests: 95 pass (2 new). **Next is the owner's call:** whether
and when to revise observations in the light of the audit (then the notebook, the atlas content, the "What comes
next" page and per-observation pointers change together), Stage 2, and publishing the atlas.

Before that, the same day: **Stage 1 is audited against IP Australia's published evidence**
(`docs/audit-ip-australia.md`, ADR 0024), at the owner's request: the twelve Australian IP Reports (2015 to 2026),
IP Australia's research papers and notes, as the Econ repository holds them page by page. A tested benchmark
(`analysis/audit/`, `python -m audit.benchmark`) recomputes 195 figures IP Australia published from the lenses on its
definitions (calendar years; a resident has a founding applicant in Australia); 155 agree within 2% (or 1 point), the
rest explained by definition or found to be four real discrepancies. Of the 99 observations, 23 are corroborated, 9
consistent, 1 disputed in part and 66 not testable from IP Australia's publications; none is contradicted. What
changes: design shares among known origin are lower bounds (IP Australia counts about three in four "origin unknown"
designs as Australian); trade marks filed in 2018 are flagged (IP RAPID 1,994 short, in Madrid applications); U67's
2016 lead is closed (a real rise IP Australia reported); U45's fall in first-time filers is a fall in ABN linking
(by applicant, first-time resident trade mark filers rose from 22,838 to 28,626 in 2025); U28 gains Australians'
standard patents brought forward by the innovation closure in 2021 (+24.8%). IP Australia's "55.6% of resident
applications filed by individuals" (2022) cannot be reproduced (OQ12). The notebook is not rewritten; the verdicts
live in the audit, ADR 0024 and `docs/stage-1-summary.md` (section 10). **Next is still the owner's call:** Stage 2,
publishing the atlas, and whether to add OQ12 to OQ14 to the request to IP Australia.

Before that, on 2026-10-27: **Stage 1 has a plain-English website, the evidence atlas** (`evidence/`, ADR 0023),
asked for by the owner for readers who are not data scientists. Every observation (U0 to U98) has a page: what was
found, under which lens, how it serves the five questions, and a trail from the original source through storage and
preparation to the reasoning, with its assumptions and limits; plus pages on the questions, the lenses, the data's
journey, Stage 1's limits, what Stages 2 and 3 will add, and a glossary. `analysis/atlas` builds it from the notebook
and the plain English in `analysis/atlas/content/`, refusing any number the notebook does not show; 69 charts are
redrawn from the lens tables and checked against the quoted numbers. Building it found that U0 had kept the first
corpus profile's figures (152 tables, 38 sources, 314,742,745 rows); corrected to the profile its output reads (162,
41, 317,792,796; Parquet 69.73%) in the notebook's markdown, `docs/stage-1-summary.md` and the site. **The site is live
only once this branch reaches the branch Pages serves: the owner's call.**

Before that, on 2026-10-26: **Stage 1 is complete.** The last three `rights` attachments are built and profiled
(sections 1.8.3 to 1.8.5 of `01_univariate.ipynb`, U88 to U98, ADR 0022): how each right came to Australia (8 columns
from `iprapid/links`, with a patent priority's office read from its number because IP RAPID labels PCT numbers `au`),
each patent's Google Patents family (6 columns: offices, US grant, citations, with the five-year count only where its
window is complete) and its inventors (8 columns: countries and expected women and men). `rights` has 74 columns. The
PCT route matches WIPO's PCT national phase entries at IP Australia (median ratio 1.001, 1995 to 2024). Gender
estimates match WIPO's published share for Australia (14.6% against 13.8%) but run high elsewhere (median +4.5
points, China +11.2, Korea +21.3), so they are read as levels for inventors in Australia only. Two WIPO indicators
joined the corpus for the checks (`wipo_ipstats`: direct and PCT national phase applications; women's share of PCT
inventors), every earlier value unchanged; `national_indicators` now has 41,218,170 rows. Re-running the whole notebook
found four cells whose answers depended on how ties fell (row order, `any_value`); all are fixed, and three quoted
figures are corrected (U52: 29.2% and 32.8% of people, not 29.0% and 32.9%; U87: UNSW's 210, Monash's 151 and so on,
not 216 and 178; U68's totals). `docs/stage-1-summary.md` and section 9 are updated. **Next is the owner's call:
Stage 2. OQ11 (the institutions link) and OQ2 (the fee history) are best answered before it.**

Before that, on 2026-10-26: Stage 1 has its summary: `docs/stage-1-summary.md` gives the full account (the
goals, the process, each lens's findings, eight themes across the lenses, the rules carried forward, the pairs for
Stage 2, the open items and the limits, with an index of U0 to U87), and section 9 of `01_univariate.ipynb` holds the
short version (the key observations and the pairs carried into Stage 2). The notebook's status line is brought up to
date. Only markdown cells changed, so the notebook was not re-run. **Next is the owner's call: the remaining `rights`
attachments (OQ1) or Stage 2; OQ11 is best answered before Stage 2 compares institutions.**

Before that, on 2026-10-26: the `institutions` lens, the last planned, is built and complete for Stage 1, so
**every lens now has its Stage 1 profile**. Section 7 of `01_univariate.ipynb` profiles every column (U80 to U87),
ADR 0021. One row per research institution (its ROR identifier) and calendar year, 1990 to 2026 (4,810 rows): 44
universities, 11 public research agencies, 46 medical research institutes and 29 other grant holders. A new corpus
source, `ror` (every Australian ROR record, from ROR's data dump: its API pages unstably), keys it. The link from
institutions to IP RAPID, the ARC and AusTender is a reviewed list in `analysis/eda/institutions/` (130 institutions,
116 extra names, 146 ABNs), with the universities' commercialisation companies: UNSW files 96.5% of its patents
through NewSouth Innovations. The IP detail is a companion table, `institution_rights` (31,528 rows, joinable to
`rights`). The lens holds OpenAlex's works and citations (2010 on), US patents' citations to the institutions' works,
ARC grants (2001 on, industry-partner schemes apart) and NHMRC grants (2013 on), IP by type, the patents' families
(Google Patents) and AusTender contracts. Plant breeder's rights cannot be linked (their applicants are codes). The
profile also answers U49: half the universities' standard patents carry a postcode that is not a postal area. **Next is
the owner's call (Stage 1's summary, then Stage 2, or the remaining `rights` attachments); OQ11 asks whether someone
in the sector should check the link.**

Before that, on 2026-10-26: the `industries` lens is built and complete for Stage 1: section 6 of
`01_univariate.ipynb` profiles every column (U73 to U78) and every attachment (6.4, U79), ADR 0020. One row per ANZSIC
division and financial year, FY1990 to FY2026 (703 rows): IP applications as expected counts through the ALP
crosswalks (each right split over industries by probabilities), CABEE's businesses, entries and exits (FY2023 to
FY2026), BERD (2023-24), the WPI and BCARR's creative value added. Every value the ABS and BCARR publish by industry is
in a new long table, `industry_indicators` (1.4 million rows), and their Australia-wide tables went to
`national_indicators`. B6 is done (26 IPC predecessors), and a corpus repair: `concordances` split each ISIC class over
partial ANZSIC links, sending half of pharmaceuticals' weight to textiles and inorganic chemicals. Patents reach only
goods-producing industries (the crosswalk excludes services: manufacturing 90.8%), a lead for Stage 2. **Next is
`institutions`, the last planned lens, unless the owner says otherwise.**

Before that, on 2026-10-26: the `national` lens is complete for Stage 1: section 4 of `01_univariate.ipynb`
profiles every column (U63 to U67) after the repairs of ADR 0019, and every attachment (4.4, U68 to U72). WIPO's filings
by residents of former states (the Soviet Union, East Germany and four more) and of unknown origin are kept (they were
9.65% of patent applications by origin, and silently dropped), with a new column, `entity`. The attachments are a new
long table, `national_indicators` (41.2 million rows: every value of the GII 2026, the 24 OECD flows, WIPO's filings at
IP Australia by origin, its office table and PCT, Madrid and Hague counts, Measuring What Matters and Closing the Gap).
Two corpus repairs, by reprocessing: Closing the Gap's "Aus Gov" jurisdiction (85 values) and Measuring What Matters'
stacked tables (45 cells shared a key). Re-running the notebook also showed that the `rights` build broke two ties
arbitrarily (a founder's two same-day postcodes, an agent's several names), so a few figures in sections 1 and 3
changed from build to build; the ties are now fixed (ADR 0019, decision 6), two builds agree row for row, and five
quoted figures are corrected (U48, U49, U52, U53). **Next is `industries`, then `institutions` (the plan's order),
unless the owner says otherwise.** (Done: `industries`, above.)

Before that, on 2026-10-25: the `regions` lens is complete for Stage 1: section 3 of `01_univariate.ipynb`
profiles every column (U48 to U54) after the repairs of ADR 0017, and every attachment (3.5, U55 to U62, ADR 0018).
Applications are now counted at the filer's postcode; rates are a year, per 10,000 people and (organisations only) per
1,000 GST-registered businesses, and are empty where fewer than 10 applications would be expected at the national
rate; `sa3_code` allows pooling; and the filers' postcodes that are not postal areas are classed (S6): 5.55% of
standard patents, mostly universities' postcodes. The attachments are a new long table, `region_indicators` (22.5
million rows: every value of the Census, Data by Region, CABEE, PHIDU and the Clean Energy Regulator by postal area,
SA2 and PHA values split by 2021 residents), and three AusTender columns in `regions`.

Before that, the same day: the `firms` section (2) of `01_univariate.ipynb` profiles every column of that lens
(U41 to U47), after four repairs (ADR 0016): applications are counted by the filer's ABN (`founder_abn`), not the
current holder's; two new columns say what each firm holds (`n_held`, `n_held_in_force`); `in_iplord` flags the 50,790
ABNs that only IPLORD links to IP (their IP counts are 0, so firms' IP counts are lower bounds); and blank ABR states
are emptied (165 filled from the postcode). The profile found that recent filers are less often linked to an ABN
(Australian organisations' trade marks 84.1% in FY2024, 59.9% in FY2026): firm filing by year is compared to FY2024
for now.

Before that, the same day: the events attachment (B5) is built and profiled, as section 1.8.2 of
`01_univariate.ipynb` (U31 to U40, ADR 0015). Eleven columns join `rights` from `iprapid/events`: the date of patent,
the examination request (and whether expedited), acceptance, certification, first opposition, assignments (count and
first date), extension of term, and each right's lifetime (`in_force`, `years_in_force`), with rights still in force
counted as unfinished and compared by survival curves (`uni.kaplan_meier`). Trade marks and designs are observed to
31 March 2026, because their ends are recorded only after the six-month grace period. The profile also resolved two
timeline leads (U27, U29) and the placeholder-date check. **Next is `firms` (the owner's order).**

Before that, the same day: the `timeline` section (5) of `01_univariate.ipynb` now
profiles every column of that lens (U22 to U30), after one more repair (ADR 0014): 15 monthly series started too
early, on records where IP RAPID holds only the rights that survived until it was computerised (trade marks before
1983, designs before 1986, provisionals before September 1985), outcomes for some rights only, or events dated in
batches. Those months are now empty. The profile also found a policy change missing from the register, the rise of
the standard patent term from 16 to 20 years on 1 July 1995 (patent expiries all but stop for four years), now the
17th event, and corrected the register's note on the Patents Act 1990 (its term was 16 years).

Before that, the same day: the `rights` section profiled every core variable of its lens (U1 to U16, after five
repairs, ADR 0012) and its first attachment, the parties (1.8.1, U17 to U21, ADR 0013). The lens now has 41 columns:
12 describe who filed each right (the founding applicant), whether the holder has changed, the main agent and who
represents the filer (attorney, other agent or self). Profiling the parties found that IP RAPID keeps one set of
applicants for patents filed before FY2003, entered when records moved between systems, so a change of holder before
then cannot be seen; `holder_changed` is empty for them.

Earlier the same day: the last check before Stage 1 (ADR 0010, the lenses; ADR 0011, the corpus), after the
independent review (`docs/Aus-GII-Independent-Review-and-Action-Plan.md`, whose IDs A1–A8, B1–B12, F01–F42 and
N01–N07 are used throughout), the owner's decision that every dataset goes through all three stages (ADR 0007),
`abs_prices` and `abs_labour`, the inventors (ADR 0008) and the `rights` repairs (ADR 0009). TableBuilder is on hold,
and BLADE stays ruled out.

## Where things stand

- **The audit against IP Australia (ADR 0024).** `analysis/audit/published.csv` (195 figures, each with its Econ
  document and page), `benchmark.py` and `output/` (the comparison, a summary, the states' shares and the lens-only
  figures the audit quotes). Rerun `cd analysis && uv run python -m audit.benchmark` after rebuilding the lenses and
  commit the output; `tests/test_audit.py` fails if it is out of step (93 tests pass, 2 new). What it found (all
  descriptive):
  - counts: standard patents 12 of 12 years within 0.34%, provisionals 11 of 11 within 0.25%, trade marks 10 of 11
    within 0.05%, standard grants 10 of 10 within 0.03%, the PCT route within 0.35%, Madrid within 0.1%, states'
    shares within 0.2 points;
  - D1: resident designs 0.8619 to 0.8983 of IP Australia's, because about three in four "origin unknown" designs are
    Australian on its count; D2: trade marks 2018 0.9749 (Madrid); D3: IP Australia's 55.6% of residents'
    applications by individuals (2022) against the lens's 20.65%; D4: trade marks in force in 2005 0.9384 (context);
  - IP Australia's readings of the leads, with their strength: digital tools behind the provisional rise (U8), real
    direct filing among domestic innovators (U90), the closure behind 2021's resident patents (U28), fast-tracked
    patents renewed more (a Stage 2 pair, U34 with U36).
- **The evidence atlas (ADR 0023).** `evidence/` (index.html, css, js, data, img) is static; `evidence/data/atlas.json`
  and `evidence/data/charts/*.json` are generated and committed. To change it: edit the notebook or
  `analysis/atlas/content/`, then `cd analysis && uv run python -m atlas.charts` (needs the lens tables) and
  `uv run python -m atlas.build` (`--draft` lists problems without failing). Preview with
  `python3 -m http.server` from the repository root and open `/evidence/`. Tests: 91 pass (4 new in
  `tests/test_atlas.py`: every observation has a page, the committed JSON is in step, every observation names a lens
  and a question, and the numbers rule).
- **Stage 1, `rights`, links, Google Patents and inventors (1.8.3 to 1.8.5).** What it found (all descriptive):
  - the links (U88): IP RAPID labels 93.88% of PCT numbers and 15,568 other offices' priority numbers `au`; read from
    the number, 0.7% of standard patents' priority offices are unknown;
  - against WIPO (U89): the PCT route is 0.981 to 1.007 of WIPO's PCT national phase entries (1995 to 2024), other
    standard patents 0.989 to 1.019 of its direct applications;
  - routes (U90): overseas standard patents through the PCT 81.0% (FY2010), 69.3% (FY2026), divisionals 19.9%;
    Australians claiming only a provisional 81.2% (FY1985) to 11.4% (FY2026), direct filing 28.3% in FY2026 (a lead);
    overseas trade marks through Madrid 57.2% (FY2020);
  - offices (U91): overseas priorities first filed in the US 53.42%; Australians' PCT at IP Australia 91.24%; Madrid
    basis marks 268 (2001) to 2,258 (2020), beside WIPO's 2,064 (2015) and 2,151 (2020);
  - families (U92): found for 94.81% to 99.23% of standard patents per decade since the 1980s; 734 numbers in two
    families; 23.14% of standard patents FY2010 to FY2019 share a family, 88.29% through a divisional;
  - reach (U93): overseas median 6 offices, US grant 66.66%; Australian median 2, 45.53% only in Australia
    (individuals 59.91%);
  - citations (U94): median citing families in five years 6 (overseas) against 1 (Australian), never cited 13.29%
    against 43.99%;
  - inventors (U95, U96): Australian filers' inventor countries known for 56.98% (2010s), the rest almost all filed
    only here (Google's Australian publications give none); where known, 94.47% of Australian-filed patents have an
    inventor here, 0.85% of overseas-filed ones;
  - gender (U97, U98): Australia 14.6% against WIPO's 13.8%; median country +4.5 points; China +11.2, Korea +21.3;
    about one inventor in seven in Australia an estimated woman (14.34% on Australian organisations' patents).
- **Stage 1, `institutions` (section 7, every column).** What it found (all descriptive):
  - coverage (U80): 130 institutions, 1990 to 2026; works from 2010, ARC from 2001, NHMRC from the 2013 round,
    contracts in earnest from 2007; 84 institutions filed a standard patent, 112 a trade mark;
  - the link (U81): 31,528 institution-rights, almost all matched by name and ABN together; UNSW files 96.5% of its
    patent applications through NewSouth Innovations, Newcastle 72.8%, Adelaide 43.9%, Queensland 2.1%, Sydney and
    Monash under 1%; the few grants left unmatched are councils, foundations and networks outside the lens;
  - research (U82): universities 86.8% of works (2015 to 2024), the Group of Eight 45.35%, Melbourne 7.97%;
  - grants (U83): the Go8 hold 66.3% of ARC and 63.5% of NHMRC funding; industry-partner schemes 9.7% to 29.2% of
    ARC funding a year; medical research institutes 20.8% of NHMRC's;
  - IP (U84): the institutions file 4.80% (1990 to 1994) to 8.96% (2020 to 2024) of standard patents filed from
    Australia; CSIRO 481 in 2017 to 2026, the top five 47.4%; a quarter to a third filed with others;
  - science and patents (U85): medical research institutes' works are cited by US patents most (107.7 per 1,000
    works, 2010 to 2014; universities 43.26), but 93.6% of the citations come from inventions with no Australian
    applicant or inventor; 97.0% of the institutions' standard applications are found in Google Patents;
  - contracts (U86): universities 77.9% of the institutions' contract value, public research agencies 19.0%;
  - postcodes (U87): 50.34% of the universities' standard patents (FY2017 to FY2026) carry a real postcode with no
    residents; the institutions hold 71.58% of such codes.
- **Stage 1, `industries` (section 6, every column and attachment).** What it found (all descriptive):
  - coverage (U73): 19 divisions, FY1990 to FY2026; IP in every year, CABEE FY2023 to FY2026, BERD FY2024, the WPI
    from FY1998 (no agriculture), creative value added FY2016 to FY2025 (10 divisions);
  - the crosswalks (U74): 98.42% to 99.73% of standard patents carried and 99.8% of trade marks; B6 cuts unknown
    subclass marks from 12,143 to 71; a patent's division is clear (median largest share 0.996), its subdivision less
    so (0.727); a trade mark's division less clear (0.792);
  - IP by industry (U75): manufacturing 90.78% of standard patents (machinery 31.18%, chemicals 30.17%), no service
    division above 0.23%; trade marks manufacturing 55.65%, professional services 11.05%; trade marks break in
    January 2002 (Nice 8th edition, classes 43 to 45);
  - Australians (U76): 7.87% to 17.29% of a division's patents; 47% to 58% of goods divisions' trade marks, 67% to
    80% of services';
  - businesses (U77): construction 17.0%, professional services 13.0%, property 11.4%, manufacturing 3.2% (June
    2026); health care +30.7% since FY2023, agriculture −2.9%;
  - R&D and wages (U78): BERD $24.41 billion (2023-24), professional services 37.6%, manufacturing 20.7%; $142,100 per
    mining business; wages +44.5% (property) to +56.8% (utilities) FY2010 to FY2025;
  - attachments (U79): 1,409,875 values; 21.7% of businesses introduced a new good or service in 2023 (9.9%
    agriculture to 31.9% information media); 61.9% of businesses survived June 2022 to June 2026; BCARR's releases
    agree within 1.2%.
- **Stage 1, `national` (section 4, every column and attachment).** What it found (all descriptive):
  - coverage (U63): 30 indicators, 229 places, 1960 to 2025; Australia's researchers end in 2010, technicians 2008,
    the World Bank's R&D spending 2021 (the OECD's 2023); tertiary enrolment starts in 2015;
  - WIPO before 1995 (U64): 29% to 34% of patent applications by origin had an unknown origin to 1993 (1.12% in
    2024), 87% to 90% at IP Australia; Australians' filings abroad, and WIPO's grants and designs to them, near zero
    until 1994. WIPO by country is compared from 1995;
  - Australia over time (U65): GERD 1.26% (1990), 2.24% (2008), 1.68% (2023), against an OECD median of 1.85%; BERD
    0.91% (median 1.18%); manufacturing 13.7% to 5.32% of GDP (−61%, the median member −30%); IP payments exceed
    receipts in every year; two series breaks (advanced education 2009 to 2011, FDI 2005);
  - against OECD members (U66): near the top for non-resident patents (5th of 38), new businesses (2nd of 30) and
    new business density (4th); near the bottom for exports (34th of 35), manufacturing (31st of 32) and BERD (26th
    of 35);
  - three routes (U67): IP RAPID's standard patents are within 1.5% (Australian) and 2.2% (overseas) of the World
    Bank's, 1989 to 2024, and the World Bank's are WIPO's exactly; the World Bank's trade marks count classes
    (IP RAPID's classes 0.938 to 0.998 of it, its applications 0.545 to 0.659); innovation patents in 2016 1.331 times
    WIPO's utility models, a lead;
  - the attachments (U68): 41,203,167 values, 148,731 indicators (with the ABS's and BCARR's national tables, added
    with `industries`); no Australian values in the OECD's business
    demography, innovation and IP methods or IP tax regimes; venture capital ends for Australia in 2019;
  - the GII 2026 (U69): 20th of 139 (inputs 13th, outputs 24th); strengths in education and universities, weaknesses
    in outputs and trade; 6 indicators missing and 8 outdated for Australia (the median economy: 6 and 9);
  - WIPO (U70): the United States files 41.9% of patent applications at IP Australia (2024), Australia 8.3%, China
    8.3% (0.3% in 2004); 76.1% of Australians' applications are abroad; IP Australia's average trade mark time to
    registration was 222 days (2016), the U11 peak;
  - the OECD's cross-border patents (U71): the "World" partner is the country's total (2,117 PCT applications
    invented in Australia, 2015); 7.0% of Australian inventions were US-owned in 2020;
  - Measuring What Matters and Closing the Gap (U72): 3,767 of 5,159 MWM values are monthly copies of ABS series; 353
    Closing the Gap values are projections and 443 model estimates, marked in `status`.
- **Stage 1, `regions` (section 3, every column and attachment).** What it found (all descriptive):
  - coverage (U48): 2,641 postal areas, 25,365,506 people; the filer's postcode differs from the holder's for 6.05% of
    standard patents and 7.6% of trade marks (FY2017 to FY2026); individuals file 21.53% and 24.97%;
  - the postcode check (U49): 94.45% of standard patents' filer postcodes are postal areas; 4.14% are real codes with
    no residents, led by universities' (2052 UNSW's NewSouth Innovations, 3800 Monash, 2006 Sydney, 3010 Melbourne,
    2109 Macquarie, 5005 Adelaide, 4072 Queensland); 1.39% post office box ranges. They stay in state totals;
  - people and businesses (U50): median 3,508 people; 818 areas under 1,000 people (1.33% of people); 18 areas have
    more businesses than residents (industrial estates, business districts);
  - remoteness and SEIFA (U51): major cities 37.7% of areas, 72.8% of people; SEIFA deciles are tenths of areas;
  - concentration (U52): the top tenth of areas file 72.5% of standard patents with 29.0% of people; one firm files
    76.3% of 2113's (Aristocrat), 88.1% of 2601's (CSIRO), 64.1% of 2153's (ResMed);
  - rates against chance (U53): 68.2% to 72.5% of areas fall below the funnel's 95% limits and 6.7% to 15.5% above,
    for postal areas and for SA3s alike: far more spread than chance, so Stage 2 uses negative binomial models;
  - R&D claimants (U54): 50.7% have never filed IP; 5.6 claimants per 1,000 businesses in major cities, 0.6 in very
    remote areas;
  - the attachments (U55, U56): 8,874 indicator-periods, nearly every one for nearly every area; split values track
    direct ones (Data by Region's 2021 population within 10% of the ASGS count for 99.34% of areas); CABEE counts
    0.742 of the ABR's businesses, in the same order (Spearman 0.988), so business counts come from the ABR;
  - the Census (U57): small cells (51.1% of industry-by-age cells are 0) and perturbation (males plus females equal
    persons in 10.9% of areas); Data by Region (U58) repeats Census items; CABEE (U59) non-employing businesses 61.3%
    to 63.6% (June 2023 to 2025); PHIDU (U60) 54.14% levels, periods differ; the CER (U61) solar water heaters to
    panels to batteries (from July 2025); AusTender (U62): the ACT holds 27.0% of contracts, 1.3% of businesses.
- **Stage 1, `firms` (section 2, every column).** What it found (all descriptive):
  - who is in it (U41): 398,450 ABNs, 63.68% in IP RAPID alone, 13.69% AusTender alone, 12.75% linked to IP by IPLORD
    alone; active ABNs from 47.02% (IPLORD-only) to 95.35% (IP and R&D); IPLORD's own counts differ from IP RAPID's
    (81.02% agree; 99th percentile 7 times), so they are not used;
  - entity types (U42): private companies are 74.7% of firms, 82.2% of IP filers, 94.5% of R&D claimants and 55.3% of
    government suppliers;
  - age (U43): median 13.6 years on the record; 5,279 firms first seen on 1 November 1999, the ABN's start;
  - IP use (U44): medians of 1 application; the top 1% of filing firms filed 55.3% of standard patents and 25.9% of
    trade marks; 116,240 firms hold 430,305 rights in force;
  - ABN linking (U45): first-time trade mark filers fell from 11,318 (FY2024) to 7,384 (FY2026), but the share of
    Australian organisations' trade marks with a filer's ABN fell from 84.1% to 59.9%: a lead, and a question for IP
    Australia;
  - money (U46): R&D claims median $307,490 (top 1%: 28.1%); contract value concentrated (top 1% of suppliers: 83.1%);
  - place (U47): IP filers and R&D claimants more metropolitan (87.1%, 89.9% against 85.2%) and advantaged (decile 10:
    39.3% of R&D claimants against 34.0% of firms); the ACT has 9.7% of government suppliers.
- **Stage 1, `rights`, events (1.8.2).** What it found (all descriptive):
  - the checks (U31): the grant event is `registered_date` (99.99%); patent assignments are published twice (99.78%),
    counted once; 4.76% of patent lapse events were later reversed (not standing); a trade mark's term runs from its
    earliest filing date (92.19% of ceased Madrid-type marks end on a whole year from it); a patent's cessation falls
    6 to 7 months after an anniversary (84.59%), so its years in force include the grace period; 3,154 placeholder
    and 171 pre-filing events left out;
  - each milestone is recorded from a different date (U32): patents' examination requests from the early 1980s'
    filings, trade marks' acceptances from the mid-1980s' (30.88% of the 1980s', 75.88% to 79.05% since 2000), designs'
    examination requests only from 2013;
  - times (U33): a standard patent's examination request to acceptance took up to 755 days (FY2006), 422 to 516 since
    FY2014; FY2013's applicants asked for examination 44 days after filing (Raising the Bar); trade marks are accepted
    52 to 184 days after filing (FY2005 to FY2021);
  - expedited examination (U34): standard patents 1.87% (FY2005) to 10.31% (FY2026); trade marks 16.67% to 19.69% to
    FY2018, then 3.08% to 3.97%, the fall in November 2018 (about 1,400 requests a month to about 230), when the trade
    mark records moved between systems: a lead. Oppositions: 1.98% to 2.93% of accepted trade marks; 0.14% to 0.38%
    of standard patents since FY2015;
  - assignments (U35): 15.1% of standard patents and 18.1% of trade marks filed in the 2000s; from FY2003, 64.68% to
    74.66% of patents whose holder changed have one, and the assigned share runs on smoothly across FY2003 (15.4%,
    16.41%), so `assignment_count` measures a change of owner for patents filed before then;
  - lifetimes (U36): standard patents' median years in force rose from 10.7 (1980s) to 13.5 (2000s and 2010s); 21.3%
    of the 2000s' were kept to their 20-year end. 46.9% to 56.4% of trade marks were in force after 10 years (1990s to
    2010s), against 67.3% of the 1983 to 1989 marks (a 7-year first term). Designs renewed at 5 years: 64.8% (2000s),
    58.0% (2010s). Innovation patents: median 3.5 years;
  - extensions of term (U37): 1,450 standard patents (0.24% of those granted), 108 and 114 in 1999 and 2000;
  - the 2002 trade mark lead (U38): cessations at 7 years (the 1955 Act's first term) stop in 2002 (14) before those
    at 10 years (the 1995 Act's) build up (1,167 in 2003); 10,247 of 2002's lapses are of marks filed in 2000, the
    filing peak (42,907);
  - the April design lapses (U39): 101 lapses on 32 days in April against 365 to 671 on 56 to 91 days in other months,
    with filings and lapse shares (18.1% to 21.6% per filing month) even: how lapses were dated;
  - placeholders (U40): 3,162 of 49.35 million events, 34 links, 105 party start dates. Closed.
- **Stage 1, `timeline` (section 5, every column).** What it found (all descriptive):
  - the repair (U23): never registered, 2.0% of trade marks filed in early 1981 against 52.0% from 1983; patent
    cessations dated in batches to April 1995 (29.8% of months empty); grants recorded only for patents filed from
    1979 (68.5% against 1.0% to 1.9%). The rights lens is unchanged; counts by year of filing before those dates are
    survivors, and section 1's U5 and U10 now say so;
  - growth (U25): standard patents 3.9% a year in the 1990s, 1.3%, 2.0% and 0.4% (2019 to 2025), set by overseas
    applicants; trade marks 4.3% and designs 5.5% a year since 2019, designs almost all from overseas; falls in 2009;
  - seasons (U26): Australians file 25% to 34% less in January (2010 to 2019); overseas applicants 5% to 10% less. The
    lull is deepening for Australian standard patents (80 in the 1990s to 73 since 2020) and provisionals (73 to 63).
    Registrations and grants follow the office's calendar;
  - outcomes (U27): patent grants peaked in 2016 (25,687); trade mark cessations rose to 35,484 (2025); a lead in
    2002 (trade mark cessations 3,773, lapses 16,718);
  - policy changes (U28): two rushes (Raising the Bar, 4.39 times for Australians; the innovation closure, 4.31 times,
    then −95.9%), four steps (the term change −98.4% for expiries; the 1999 extension regime; the innovation patent's
    introduction +71.5%; the Designs Act 2003, overseas +34.1%), two pauses at commencement (the Patents Act 1990, the
    Trade Marks Act 1995), and nothing visible for PCT accession, plain packaging, the 2018 and 2019 PC responses, or
    the designs grace period;
  - artefacts (U29): 42 months stand out after the repair; none is removed. Pauses and backlogs (patent cessations 7
    in February 2020, 2,468 in March), the register's start-up before June 1904, a portfolio transfer in July 2015;
  - the CPI (U30): 312 quarters from 1948, none missing; base the month of September 2025.
- **Stage 1, `rights`, parties (1.8.1).** What it found (all descriptive):
  - the holder is not the filer for 22.0% of standard patents filed in the 2000s (from FY2003), 17.1% of the 2010s'
    and 7.0% of the 2020s'; trade marks 20.8%, 15.7% and 10.4%;
  - more Australian-filed rights moved overseas than came the other way: standard patents 2,036 against 804, trade
    marks 15,391 against 4,840;
  - the filer's postcode differs from the holder's for 10.1% of standard patents and 11.13% of trade marks (FY2003 to
    FY2026), almost always within a state;
  - overseas filers use an attorney for 99.0% of standard patents; Australian filers for 85.4%, and Australian
    individuals file 62.4% of their trade marks alone. The attorney share of trade marks depends on the threshold
    (Australian: 57.08% at one applicant, 49.67% at five, 42.59% at 100);
  - patent attorneys are concentrated (top 5 handle 63.96% of standard patents; 4 handle half), trade mark
    representation is not (top 5: 17.51%).
- **Stage 1, `rights` (done for its core variables).** What it found (all descriptive):
  - about nine in ten standard patents come from overseas (91.3% in FY2017 to FY2026; 7.9% to 12.4% Australian in
    the years shown since FY1990); the United States alone files 43.5%;
  - provisional applications doubled in FY2026 (10,069), from individuals without ABNs: distinct ABNs stayed flat at
    1,361, single-filing individuals rose from 1,538 to 2,507, and 54 individuals filed 10 or more each (one filed
    375). Monthly filings peaked in March and April 2026 and eased by September 2026;
  - Australians file without an attorney far more often than overseas applicants (trade marks 57.02% with one,
    against 96.27%); 12% to 22% of Australian organisations' rights carry no ABN;
  - registration takes a median 980 days for standard patents and 223 for trade marks (filed FY2010 to FY2019), with
    a sharp peak at about 222 days for trade marks: a lead;
  - the standard patent grant rate fell from 75.5% (FY2000) to 54.4% (FY2008) and recovered to 65% to 69%;
  - "unknown" status is 408,957 old patents (FY1904 to FY1999) whose outcome was never recorded; only 68.9% of
    expired patents have a grant date;
  - design origin is often unrecorded (4.0% to 6.3% unknown since FY2018, and rising), so design shares need care.
- **Seven lenses and four companion tables are built** (`analysis/eda/build.py`), in about two minutes:
  - `rights`: 4,368,006 rows, 74 columns (29 core, 12 from the parties, 11 from the events, 8 from the links, 6 from
    Google Patents, 8 from the inventors);
  - `firms`: 398,450 rows, 50 columns (ADR 0016: `n_held`, `n_held_in_force`, `in_iplord`; ADR 0032: `wgea_*`);
  - `regions`: 2,641 rows, 42 columns (ADR 0017, 0018);
  - `region_indicators`: 28,960,234 rows, 10 columns, 206 MB (the `regions` lens's attachments, long; ADR 0018;
    the ATO and the Census time series added for gaps B3 and B6);
  - `national`: 135,597 rows, 11 columns (ADR 0019: `entity`);
  - `national_indicators`: 41,229,749 rows, 15 columns, 264 MB (the `national` lens's attachments, long; ADR 0019,
    0020, 0022);
  - `industries`: 703 rows, 20 columns (ADR 0020; the crosswalk with services and value added, gaps A2 and B2);
  - `industry_indicators`: 1,425,157 rows, 12 columns, 8 MB (the `industries` lens's attachments, long; ADR 0020;
    the 2024-25 business characteristics cubes added for gap B4);
  - `institutions`: 4,810 rows, 30 columns (ADR 0021);
  - `institution_rights`: 31,528 rows, 7 columns (the `institutions` lens's IP, one row per right and institution);
  - `timeline`: 1,473 months, 75 columns (fees, the RBA and the national accounts added for gaps A1, B1 and B2).

  Every planned lens is built (ADR 0007). Every table has a lens to attach to; the map is in `docs/eda-plan.md`.
- **The lenses' repairs (ADR 0010):**
  - `rights`: `earliest_filed_date` (for a PCT filing, `application_date` is the date it entered the national phase);
    attorney use is unknown, not "no", for provisionals, for which IP RAPID publishes no agents;
  - `firms`: contracts counted once each, at their latest notice; R&D from the latest report, amended where it was
    (−$153 million, −0.34%); `age_basis` and `age_truncated`; `ip_filed_weighted` beside `ip_filed_total`, whose
    label now says it counts an application once per founding applicant; super funds named;
  - `regions`: Census medians of 0 (no one to describe) are empty;
  - `national`: trade marks by residents and non-residents (the World Bank's current codes), the OECD's R&D intensity
    beside the World Bank's (never spliced), one name per country, and the OECD's flag on each value (`status`);
  - `timeline`: every series empty, not 0, before its records become continuous and in the months the register is
    still recording; trade mark registrations by the date entered, from January 1986 (they were counted at filing);
    each event once; the quarterly CPI; 16 policy events, every date checked against the Federal Register.
- **The corpus's repairs (ADR 0011):**
  - AusTender: each notice keeps its own id and amendment number, and the bulk file's contracts still running when
    it closed were asked for by id: 28,698 later amendments to 10,494 of them, whose value at the latest notice
    rises from $179.5 billion to $303.7 billion. Summing every notice gives $7,585.9 billion, against $1,258.5 billion
    with each contract once at its latest notice. `value_jump` flags 70 values that look keyed in the wrong units (8
    of them a contract's latest), and `published_batch` the dates that are a batch re-release's;
  - the ABN spine holds every IP applicant's or owner's ABN (6,466 more), so 11,525 rights no longer fall out of
    `firms`;
  - RDTI: 521 rows ($228 million) take their ABN from their ACN;
  - every value kept: the OECD's IP tax regimes (2,639 values, mostly text), the ABS cubes' footnoted and unpublished
    cells, and 5,181 World Bank trade mark values under the current codes;
  - one row per key: CER (7.05 million rows were 3.49 million values, each read twice), PHIDU (sub-indicators and
    area types restored, and a PHA-to-SA2 table), CABEE's survival rates by size, the ARTG.
- **Settled (descriptive, ADR 0010; confirmed by the owner, 2026-10-25):** the register does not drop provisional applications once a full application
  claims them (N01, refuted), so FY2026's jump to 10,069 provisionals is real; `application_date` for a PCT filing is
  the date it entered Australia's national phase (N06).
- **Corrected on 2026-10-26** (ADR 0022 and the notebook): three figures whose answers depended on how ties fell, found
  by re-running the whole notebook: U52's share of people in the top tenth of areas (29.0% and 32.9% became 29.2% and
  32.8%), U87's postcode table (it counted joint filings twice and named an arbitrary institution: 216 became 210 for
  UNSW, 178 became 151 for Monash), and two displays (cells naming the largest filer and the names matched by ABN);
  U68's totals change with the new WIPO indicators.
- **Corrected on 2026-10-26** (ADR 0020): the corpus's ISIC-to-ANZSIC step, which split each ISIC class over its
  partial links (textiles had 8.9% of patents, now 2.3%).
- **Corrected on 2026-10-26** (ADR 0019): the `rights` build's arbitrary ties (founders' same-day postcodes, agents'
  names), which made five quoted figures in U48, U49, U52 and U53 differ from a fresh build; and the World Bank's
  trade mark series, which the register described as applications but which count classes (U67).
- **Corrected on 2026-10-25** (each in the record as well):
  - the plan to ask AusTender's API for notices by the date last modified: its windows from July 2023 page back
    through every older contract, so it was replaced by asking for the running contracts by id. The draft of ADR 0011
    had said the 2019 to 2023 amendments could not be recovered; asking by id recovers them;
  - the draft of ADR 0010 said repeated events were at most 0.2% of any series: design lapses lose 1.9%;
  - "Contract value at latest amendment" was described as the most a contract was worth; an amendment can lower it;
  - the trade mark registration series' months before 1986 counted filings, with a false hole in 1983 to 1985.
- **Corrected this session (the timeline):** the policy register's note that the Patents Act 1990 brought in 20-year
  patents (it was 16 years until 1 July 1995); and section 1's U5 and U10, whose charts showed survivors' counts and
  registration rates for the years before 1983 (trade marks) and 1986 (designs) without saying so.
- **Tests (the last rights attachments):** 87 pass; new: the links, family and inventor columns are consistent (routes
  by type, PCT numbers, priority offices, the citation window, inventor and gender sums).
- **Tests (institutions):** 86 pass; new: one row per key in both tables, the reviewed link's integrity (every
  institution, name and ABN a ROR record, each ABN one institution, no name key two institutions), the name key
  across spellings, and the lens carrying its grants (all but 14 of the ARC's and 15 of the NHMRC's) and its IP links.
- **Tests (industries):** 79 pass; new: one row per key in both tables, the division of a class or subdivision code,
  each right's shares summing to one, CABEE's divisions summing to its total, BERD's divisions to its total.
- **Tests (national):** 73 pass; new: WIPO's applications by residents sum to the source's total, no aggregate is a
  place, the OECD's R&D intensity is held once, WIPO's filings at IP Australia sum to the office's total, Australia's
  GII rank is the source's, Closing the Gap keeps the Australian Government's values; one row per key in
  `national_indicators`.
- **Tests (regions):** 69 pass; new: the postal-area counts equal the window's rights with a filer's postcode, no
  rate shown below the minimum or hidden above it, the Poisson interval, the postcode ranges, one row per key in
  `region_indicators`, CABEE's split businesses sum to the published total, no level marked as a count.
- **Tests (firms):** 63 pass; new: the filing counts sum to the rights with a filer's ABN, holdings, states.
- **Tests (events attachment):** 62 pass; new: the events columns' dates, types and lifetimes, and the survival
  helper against a hand count.
- **Tests (before):** 60 pass (the lens tests skip unless the lenses are built); lint is clean. New: each hand-set timeline
  start, no batch gaps inside a series, and the new policy event's date.

## Next, in order

1. **The owner's call:** publish the evidence atlas (merge to the branch Pages serves) and review its plain English;
   Stage 1 is complete (every lens and attachment profiled, U0 to U98; summary in
   `docs/stage-1-summary.md` and section 9). Stage 2 begins when the owner says. OQ11 (a sector check of the
   institutions link) is best answered before Stage 2 compares institutions.
2. **Done:** the `national` section (U63 to U72, ADR 0019), the `industries` section (U73 to U79, ADR 0020) and the
   `institutions` section (U80 to U87, ADR 0021), each with its attachments.
3. **Done:** the last `rights` attachments (1.8.3 to 1.8.5, U88 to U98, ADR 0022): the links (with the PCT country
   check), Google Patents (B4) and the inventors (gender checked against WIPO's shares). Left from B4: sizing the
   Australian families filed only abroad that Google misses (F07, needs WIPO's patent families by origin), and the
   1990s and 2000s numbers that do not match (1% to 5% of standard patents in those decades).
4. **Done:** the `timeline` section (U22 to U30, ADR 0014), the events attachment (U31 to U40, ADR 0015), the `firms`
   section (U41 to U47, ADR 0016) and the `regions` section with its attachments (U48 to U62, ADR 0017, 0018). The
   `firms` lens's later attachments (filing histories by year from `applicant_year`; its rights' lifetimes and
   assignments) become sub-sections of section 2 as each is built.
5. **The plan's "high value, little work" additions, with the lens each serves:** the RBA's cash rate and exchange
   rates and the ABS national accounts (timeline) and the ATO's statistics by postcode (regions). Done: IP Australia's
   own published figures as a benchmark (ADR 0024: the provisional rise, U8, is corroborated; the trade mark expedite
   fall, U34, is not mentioned in IP Australia's reports).

## Open items

1. Leads for Stage 2:
   - fewer recent filers are linked to an ABN (U45): Australian organisations' trade marks 84.1% (FY2024) to 59.9%
     (FY2026). Late linking, or ABNs collected less? Filing itself did not fall (ADR 0024). Firm filing by year is
     compared to FY2024 until known;
   - trade mark requests for expedited examination fell from about 1,400 a month to about 230 in November 2018, when
     the trade mark records moved between systems (U34): recording or practice? IP Australia's published figures
     could tell;
   - petty patents filed FY1986 to FY1988 mostly lack an acceptance, though many were registered (U32);
   - resolved (U38, U39): the 2002 trade mark trough (the change from 7-year to 10-year first terms, and the 2000 filing
     peak) and the April design lapses (how lapses were dated);
   - trade mark oppositions rise from 0 to 16 a month (1983 to 1987) to 20 to 40 (1988): left as recorded (ADR 0014);
   - the months before June 1904 are a start-up (applications lodged before the Patents Act 1903 took effect).
   - the regional spread of filing is far more than chance, at postal areas and SA3s (U53), and a few areas' patents
     are one firm's (U52): Stage 2 reads area counts beside their firms, with negative binomial models;
   - universities' postcodes are not postal areas (U49): their filings are missing from postal-area counts. A lookup
     that places these postcodes (GeoNames, free) only if Stage 2's regional results prove sensitive;
   - the ACT holds 27.0% of government contracts against 1.3% of businesses (U62), and South Australia 12.2% of their
     value against 6.1%: where contracts are addressed, to read beside the firms behind them.
   - closed (ADR 0024): IP RAPID's innovation patents filed in 2016 (1.331 times WIPO's utility models, U67) were a
     real rise from non-residents that IP Australia reported (2,322); the gap is between IP Australia's count and
     WIPO's;
   - trade marks filed in 2018 are 2.5% short in IP RAPID, in Madrid applications (ADR 0024, OQ13): flag 2018 in trade
     mark series;
   - design shares among known origin are lower bounds: IP Australia counts most "origin unknown" designs as
     Australian (ADR 0024, OQ14);
   - IP Australia's 55.6% of residents' patent applications by individuals (2022) cannot be reproduced (20.65% in the
     lens; ADR 0024, OQ12): U13 and U48 stand meanwhile;
   - the innovation closure pulled forward Australians' standard patents in 2021 (+24.8%, U28 and ADR 0024): include
     them in the closure's Stage 2 window;
   - first-time filers from FY2025: count by applicant (party id) beside the ABN count (U45, ADR 0024).
   - the World Bank's share of the labour force with advanced education steps up to 86.33% in 2010 for Australia
     (80.42% in 2008, 82.09% in 2015), a break the OECD median does not show (U65): use with care.
   - Australia ranks near the bottom of the OECD on business R&D, exports and manufacturing, and near the top on
     filings from abroad and new businesses (U66): Stage 2 compares them as ratios to people and GDP.
   - patents reach only goods-producing industries because the corpus's ALP crosswalk excludes services (U75): ALP
     publishes a version that includes services (free); whether to use it, beside or instead, is a Stage 2 choice;
   - trade marks by industry break in January 2002 (the Nice 8th edition, U75): compare from FY2003;
   - the BCS flags 36.2% of its values for sampling error and withholds 25% (U79): division comparisons need care.
   - US patents cite Australian institutions' research, but 93.6% of the citations come from inventions with no
     Australian applicant or inventor (U85): the research-to-invention link runs mostly abroad (Q1);
   - medical research institutes' works are cited by patents two and a half times as often per work as universities'
     (U85), and the institutions' joint filing (a quarter to a third of standard patents, U84) is a measure of
     collaboration to set beside the ARC's industry-partner grants (U83);
   - Australians' standard patents filed directly, claiming nothing, rose to 28.3% in FY2026 (11.3% in FY2020, U90): a
     change in practice, or priority claims recorded late?
   - family reach and citations (U93, U94) are value measures to read beside years in force (U36), within cohorts;
   - gender estimates are levels for inventors in Australia only (U97, ADR 0022);
   - the universities' patents outside the postal areas (U87) can be placed through `institution_rights` and ROR's
     locations, replacing the GeoNames lookup in the item above, if Stage 2's regional results prove sensitive.
2. Check in Stage 1 (the placeholder dates are done, U40):
   - the 222-day peak in trade mark registration times (U11): WIPO gives IP Australia's average time from filing to
     registration as 222 days in 2016 (U70), so the peak is the office's usual path. IP Australia's reports give no
     trade mark process times (ADR 0024); its median patent time from examination request to acceptance, 1.3 years
     for 2020, matches the lens's 1.23 (U33).
3. Settled by the parties attachment (ADR 0013): `representation` separates attorneys (agents of five or more
   applicants) from other agents. For trade marks the share still depends on the threshold, so Stage 2 gives bounds.
   Attorney firms' corporate groups are not recorded, so concentration by firm name is a lower bound.
4. Plant breeder's rights: their holder changes rise in recent years (11.2% of those filed in the 2020s, more than in
   any earlier decade), against every other type. Unexplained.
5. AusTender: amendments after August 2019 to bulk-file contracts that had ended by then are not in the corpus. A
   sample suggests they are under 1% of the contracts' value; `austender._harvest_by_id` can fetch them in about a day.
6. Fee history (R3) and the PBS monthly report with Section 100 (B9) are the biggest data gaps for the later stages.
7. The `coalesce` in `iprapid.py` that caused the origin problem (ADR 0009) is left until IP RAPID is next rebuilt; no
   lens reads that column.
8. The corpus profile (`analysis/output/`, `analysis/profile_corpus.py`) predates the `ror` source, so
   `data.corpus_columns("ror", ...)` finds nothing until the profile is next run in full (its `--only` replaces the
   CSVs rather than adding to them).

## For the owner

The owner's questions are kept in **`docs/owner-questions.md`**: open ones (OQ2 to OQ4 and OQ11), those the owner is asking IP
Australia (OQ5 to OQ7: the evidence behind IP Australia's digital-tools reading of the provisional rise and the heavy
filers, the trade mark expedite fall, whether ABNs are added later or no longer collected; OQ5 and OQ7 reworded after
the audit, A10) and three the audit added to the same request (OQ12 to OQ14: the 55.6% individuals' base, the 2018
Madrid gap, design origins; A8), deferred ones,
and every answer with its date. Nothing there blocks Stage 1. Add new questions there, and move answers to its
"Answered" table.

## Conventions to keep

- Commit the code, run the notebook, then commit the notebook with its outputs.
- Never print raw rows. Aggregate in DuckDB.
- After a parser fix, `corpus reprocess <source>` rebuilds its tables from the raw files it holds, keeping the data's
  vintage (ADR 0011).
- The `rights` section's cells are long; keep each new sub-section to a few cells, and the notebook under about
  25 MB (ADR 0002 says when to split it).
- `region_indicators` is 22.5 million rows: always filter by `source` and `indicator` in SQL, never load it whole.
- `national_indicators` is 41 million rows: always filter by `source`, `dataset` and `indicator` in SQL.
- When an observation changes, change its plain English in `analysis/atlas/content/` too and rebuild the atlas; the
  tests fail until `evidence/data/atlas.json` is in step. Stage 2's pages are in `analysis/atlas/content/observations/stage2/`
  (ADR 0035): a new B observation needs its entry there before the tests pass.
- Compare WIPO's series by country from 1995 only (U64), and filter `entity = 'country'` for comparisons between
  countries.
- `industry_indicators`: filter by `source` and `indicator`; never add `TOTAL` to the divisions.
- `institutions`: never add works or citations across institutions as if distinct, or a child's (Data61's) to its
  parent's; count a university's IP with its companies (the link does); compare patent citations by cohorts of the
  same age.
- Corrections to the institutions link go in `analysis/eda/institutions/*.csv`; `uv run python -m eda.build
  institution_rights institutions` rebuilds both in seconds, and the tests check the link.
- Next free ADR: 0048.
- The atlas's audit page reads the record's tables (sections 5.1 and 5.2 of `docs/audit-ip-australia.md`): keep their
  layout, and after changing the record, the benchmark or `analysis/atlas/content/audit.yaml`, rerun
  `python -m atlas.build` and commit `evidence/data/` (ADR 0025).
- After `python -m eda.build`, rerun `python -m audit.benchmark` and commit `analysis/audit/output/`; compare with IP
  Australia on calendar years and `founding_australian` (ADR 0024).
- The `rights` lens's gender columns: levels for inventors in Australia only; never for China or Korea (ADR 0022).
- Tie-breaks: any query that picks a top row or a name must order ties explicitly (the lens files' row order is not
  fixed between builds).
