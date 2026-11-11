# 0058: Keeping every observation current: a relation graph, a check at the moment of change, and a ledger

**Date:** 2026-11-11. **Whose:** the owner's (the policy: every observation on the atlas current and valid; nothing
shown once disproven or outmoded by a clearer observation; nothing removed without their explicit approval; a ledger of
what was removed and what replaced it; disagreements that do not clearly settle anything kept as areas for further
exploration; the aim that currency be maintained as observations are made, not by post-hoc audits); Claude's (how,
and every judgement in the first review), which the owner can overturn.

**Context.** Each new dataset or stage meant re-auditing every finding by hand: the twelve external audits, pass 8, the
review of 3 November and the audit of 10 November (ADR 0057) each read observations against their own outputs, by
section or theme. None compared every observation with the others across stages, and nothing in the build noticed
when a change to one observation, its outputs or its data bore on another. Stage 3's `revisits` (ADR 0049) were the
only cross-stage links, and only from Stage 3 back.

## Decision

1. **Relations are data.** `analysis/atlas/content/relations.yaml` holds the judged relations between observations:
   *supports*, *refines*, *contests*, *outmodes*, *disproves*, each with a plain sentence (`why`, under the numbers
   rule: any number must be on one of the two pages, with the plain readings' allowance). A contest says what would
   settle it (`settle`); an outmode or disproof names the owner question that asks to retire it (`asked`). Stage 3's
   revisits whose verdict is holds, weakened or refined become relations on their own; every other verdict (mixed,
   reversed, not detected, does not replicate, appears once held) needs a judged one.
2. **Status is derived, never typed.** *Retired* (in `content/ledger.yaml` with the owner's date and words), *proposed
   for retirement* (outmoded or disproved, awaiting the owner), *open for further exploration* (contested), *current*.
3. **The check happens at the moment of change, and the build enforces it.** Each observation has a review record,
   `analysis/atlas/reviews/<id>.yaml`: its candidates, each pair's judgement and note, and a fingerprint of what it
   rests on: its own words and reading, the outputs above it, the processed data files of its sources
   (`data/manifest.json`), and the words and standing of every observation it names. The strict `atlas.build` (and so
   the tests and CI) fails while any review is missing or stale, any pair is unjudged, a judged pair's other side has
   changed since, a judgement has no matching relation, a proposal has not been put to the owner, a retirement lacks
   the owner's words or its notebook note, or atlas content cites a retired observation. So adding data, re-running a
   cell or rewording an observation makes its check stale immediately; the next build says which and why.
4. **Finding the candidates: a hybrid search** (`atlas.currency`): keyword ranking (BM25 over headline, reading and the
   notebook's words), meaning (model2vec's potion-retrieval-32M, a small static embedding model run locally, free;
   a latent semantic index from scikit-learn if it is missing) and structure (snake-case columns named in the
   observation and its evidence, sources, glossary terms, lens), fused by reciprocal rank. The top 8, plus every
   observation it names or that names it, are judged. A knowledge graph alone would miss observations no one thought
   to link; a search alone would miss the explicit links; the graph records the judgements the search prompts.
5. **The judge is Claude, in the session**, following `.claude/skills/currency-check/SKILL.md` (`/currency-check`). No
   paid API. Judgements are kept, and mirrored to the pair's other side while neither text changes, so a re-check
   only judges what is new.
6. **Nothing leaves without approval.** An outmoded or disproved observation is marked at once (a banner at the top of
   its page, a tag in every list, a filter, the Markdown copy and so the chat's evidence) and listed on a new page,
   "Keeping the atlas current" (`#/currency`), with the owner question. Only an approved ledger entry retires it: it
   then leaves the lists, search, lens pages and passages, its address shows the ledger entry and what to read
   instead (following a chain of replacements), and its notebook keeps it with a dated "Retired" note.
7. **Where the bar sits.** *Outmodes* needs the earlier headline claim to fail a like-for-like comparison or to be an
   artefact of how the data were built, with the later observation stating everything still true in it. *Disproves*
   needs a clear reversal or a data error. Anything pointing against a claim without settling it (a range that
   includes no difference, one period, a different sample or measure) is *contests*. When a part changes and the
   headline stands, *refines*, and the earlier page shows the change in a box under its reading.

## The first cross-stage review (the baseline)

All 231 observations were checked: 1,380 distinct pairs (2,199 candidate entries), 510 of them across stages, of
which 476 were read pair by pair (the other 34 are settled by a Stage 3 verdict of holds, weakened or refined). Basis: every plain-English reading read lens by lens, every cross-stage pair
read by headline with the readings in view, and the notebook's own words for every pair that touched (B13, M5, B40,
M22, B58, B62, M24, U92, M23, M38 and the 27 revisits needing a judgement). Result, 69 relations:

| Kind | Count | Which |
|---|---|---|
| Outmodes (proposed for retirement) | 2 | M24 outmodes B62 (its links were a shared denominator; OQ36); M5 outmodes B13 (its pooled advantage reverses like for like; OQ37) |
| Contests (open for further exploration) | 3 | M22 and B40 (trade marks and R&D, once value added is held); M36 and B56 (GDP and overseas patents, once neighbouring quarters are allowed for); M38 and M23 (research cited by patents, within universities in 2017 to 2023) |
| Refines | 38 | 20 judged (17 Stage 3 revisits, among them M31 reading B58's "richer" areas as more advantaged ones; B55 on U92, B33 on U66, M7 on U98), 18 from revisits' verdicts |
| Supports | 26 | 9 judged, 17 from revisits' verdicts |

No observation was found disproven. Nothing was retired.

**A correction the review found.** U92's atlas headline and plain-English reading said Google Patents finds each
patent's *overseas* family; the notebook's own words say only "family", and U93 (45.12% of Australian applicants'
families filed only here) and B55 show the overseas members are often missing for older patents. The reading is
corrected in notebook 1 with a dated note (the cell's source edited in the JSON; no cell re-run, outputs byte for
byte as before), and the headline in `rights.yaml`. The overview's "What Stage 2 found" no longer presents B62's
licence-income link as a finding.

## Consequences

- Adding data or an observation now carries its own audit: a new observation is judged against its nearest
  neighbours in the turn it is made, and anything it outmodes is marked at once. Post-hoc audits become checks of the
  judging, not re-reading everything.
- `relations.yaml` and the reviews grow with the atlas; a re-check judges only changed pairs. `uv run python -m
  atlas.currency status` gives the state; `search` explores; `impact <id>` lists what leans on an observation.
- The chat's evidence carries each page's standing ("Where this stands" in the Markdown copy, and a passage for the
  new page); Econ needs its usual refresh to serve it.
- The judge is a model reading text. The review records say what each judgement rests on, so a later audit can sample
  them; a cheap one would re-judge a random 5% of "none" pairs.
- `model2vec` joins the analysis group (about 30 MB of model, downloaded once from Hugging Face). CI never needs it:
  the gate checks records, not searches.

## Addendum: review of the same day (11 November 2026)

The owner asked for a review of what was done, the process included, before deciding on the two proposed
retirements. Five tests, what each found, and what changed.

1. **Does the search find what is related?** Measured on the known relations (the Stage 3 revisits and the judged
   relations), searching from the later observation alone: the other is in its top 8 for 91% and its top 12 for 99%.
   Keywords alone reach 90% and 92%; the embedding model alone 83% and 92%; a latent semantic index alone 94% and 99%;
   keywords, both readings of meaning and columns together 96% and 99% (69 and 71 of 72). The differences among the
   combinations are one to three pairs, so they rank loosely, but a hybrid beats keywords. **Changed:** the search now
   uses both readings of meaning (the latent semantic index always, the embedding model when installed), and a new or
   reworded observation takes its top 12, not 8.
2. **Was the judging sound?** A random 70 of the 1,311 pairs judged "none" (seed 20261111) were read in full. None
   hides a contest, an outmoding or a disproof (0 of 70; a true rate up to about 4% cannot be ruled out on a sample
   this size). Two clear weaker links had been missed, B53 refines B40 and B46 supports U85, and three borderline
   supports were left as "none" (B3 with U99, B51 with M8, M12 with M8). **Changed:** both relations recorded; the
   procedure now says to read both readings in full, since headlines miss the weaker links.
3. **Are the relations taken from Stage 3's verdicts right?** The 18 revisits with a verdict of weakened or refined
   were read against the earlier headline: each leaves it standing, so "refines" holds for all.
4. **Does a retirement work?** It was rehearsed on B62 and reverted. It did not: the gate counted the retired
   observation's own entry, and its replacement's `revisits`, as content citing a retired observation, so no
   retirement could have passed the build; pairs judged against it were asked for again; and the replacement's page
   lost its "Stage 2 found" step. **Changed:** only other observations' entries and the site's own pages must be
   re-pointed; the replacement names what it replaced, shown as "since retired"; judged pairs with a retired
   observation are left. Rehearsed again: 230 pages build, no console errors at 1,366 or 390 pixels.
5. **Does new data force a second look?** It did not: a refreshed source made the checks stale, but running the check
   again restored the fingerprint with every judgement kept and nothing re-run. **Changed:** when the data under an
   observation change and its outputs are as before, the build asks for its cells to be re-run or for a recorded
   reason it is unaffected (`atlas.currency confirm`); checking again does not clear it. Scale: 173 of the 231
   observations rest on IP RAPID, 33 on the ABR, 31 on the ABS regional data.

**The bar for retirement, sharpened.** Decision 7 said an outmoding needs the later observation to state everything
still true in the earlier one. The B13 proposal did not meet it: M5 does not carry who asks for expedited
examination and for what (the 2011 and 2012 rise and the 2014 Patent Prosecution Highway step, which OQ25 rests on),
nor that expedited applications are granted more often. Claude withdrew the proposal. B13 is corrected in place: its
notebook heading no longer says "not a composition effect" (true of the filer mix only; a dated note quotes it), its
atlas headline reads "On raw figures ... but not among similar patents", and M5 *refines* it. The rule, now in
`CLAUDE.md` and the skill: **retire only when nothing true is left that the replacement does not say; otherwise
correct the outmoded wording in place with a dated note, and record *refines*.** B62 still meets the bar: M24 quotes
its four main correlations and reads them correctly; only "patents per disclosure fell from 0.161 to 0.134" is
B62's alone, and the notebook and ledger keep it.

**After the review:** 72 relations (1 outmodes, 3 contests, 41 refines, 27 supports); 224 observations current, 6
open, 1 proposed for retirement (B62, OQ36), none retired. B13's rewording made its own check and six neighbours'
stale; they were re-checked, 18 pairs read in full, and one relation added (B13 refines U34).

**What the process still cannot do.**
- It notices that data changed; it does not re-run the notebooks. A tool that re-runs the cells above each affected
  observation and compares the numbers with those quoted would turn a refresh of IP RAPID from 173 manual
  confirmations into a list of the observations whose numbers moved. Recommended next.
- A change to the lens-building code (`analysis/eda/build.py`) changes the tables without changing the corpus, and
  the fingerprint does not see it.
- The gate checks that every pair has a judgement, not that the judgement is right. The sample in test 2 is the
  control; repeat it after any large batch.

## Second addendum: the atlas shows only the current reading (11 November 2026, A42)

The owner, on dated corrections made in place: "I'm happy for the dated corrections to be saved but I only want the
atlas to show the current and accurate information. The 'Follow the evidence' portion may reflect the amendments and
their dates." So Claude may make a dated correction without asking, and:

- **The trail is where history shows.** `build.TRAIL` names the fields that make up "Follow the evidence": the
  notebook's own words (`original`), the reasoning steps, the preparation, the sources and the notebook's own section
  heading. Every other field of a page is checked by `build.history`: a dated note ("Corrected (10 November ..."), "was
  corrected", "the earlier text", "this said", "added after Stage 2", a gap or pass number. The strict build fails on
  any.
- **Found on the first run, all fixed:** the relation between B55 and U92 said "U92's reading was corrected to say
  so" (Claude's own, from the first review); U28's limits said fees "were added after Stage 2"; and 27 section titles,
  on 34 pages' headers, carried notes such as "(added after Stage 2, gap B3)". Section titles are now shown without
  such notes (`build.current_title`: "(WGEA; added after Stage 2, gap A3)" becomes "(WGEA)"); the notebook's heading is
  unchanged and still quoted in the trail.
- **Not changed, and asked of the owner:** two pages keep a log of changes by design, the "Corrections" list on
  "Limits and assumptions" and "What the review changed" on "Checked against IP Australia". Neither is an observation
  page. The ledger on "Keeping the atlas current" is the record the owner asked for.
- OQ36 and OQ37 are deferred by the owner; B62 stays marked "proposed for retirement" and B13 stays as corrected.

