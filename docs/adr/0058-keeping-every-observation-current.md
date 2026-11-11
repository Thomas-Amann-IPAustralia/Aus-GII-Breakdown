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
