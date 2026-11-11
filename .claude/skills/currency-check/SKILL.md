---
name: currency-check
description: Check new or changed observations against the rest of the atlas and record each judgement (ADR 0058). Use whenever an observation is added, reworded or corrected, a notebook cell above one is re-run, a dataset under one is refreshed, or the atlas build says a check is stale.
---

# The currency check

Every observation the atlas shows must be current (ADR 0058). This is the procedure; the strict atlas build enforces
it, so a session cannot skip it.

## When

In the same turn as any of these, before `atlas.build`:

- a new observation (any stage), or a change to one's words or plain-English reading;
- a re-run cell above an observation (its outputs changed);
- a refreshed or new dataset under an observation (`data/manifest.json` changed);
- a proposal or retirement that changes what another observation cites.

`uv run python -m atlas.currency status` lists everything stale.

## Steps

1. **Find the candidates.** From `analysis/`:

   ```bash
   uv run python -m atlas.currency check M41
   ```

   or `check --stale` for everything stale. It writes `analysis/atlas/reviews/<id>.yaml` with the nearest observations
   (hybrid search: keywords, meaning, columns; the top 12 for a new or reworded observation, plus every observation
   it names or that names it) and a reading list, `analysis/atlas/reviews/BRIEF.md`. Judged pairs that still stand
   are kept; the rest are `judgement: null`.

   **If the data under it changed** and its outputs are as before, the build asks for more than a check: re-run its
   cells on the new data (cell by cell, never the whole notebook), then `check` again. If the outputs came out the
   same, or the change cannot reach it (a table it does not read), record that:
   `uv run python -m atlas.currency confirm U55 "cells re-run on the refreshed table; outputs identical"`.

2. **Judge each pair.** Read both readings in full for every pair, and the notebook's own words (`atlas.notebook`)
   wherever they touch. Do not judge from headlines: the review of 11 November 2026 found the weaker links
   (*supports*, *refines*) are the ones a quick read misses. For each candidate, set `judgement` and a one-line `note`
   that says why, in terms of these two observations:

   | Judgement | When |
   |---|---|
   | `none` | They do not bear on each other's claim, or agree without adding weight |
   | `supports` | It agrees and adds weight (another sample, period, method or source) |
   | `refines` | The other's headline claim still stands; a part narrows, sharpens or changes. Its page shows how |
   | `contests` | They point different ways and neither clearly settles it (wide ranges, one period, different samples or measures). **An area for further exploration, kept on purpose** |
   | `outmodes` | The other's headline claim does not survive a like-for-like comparison or was an artefact of how the data were built, **and nothing true is left in it that this one does not say** |
   | `disproves` | The other's claim is shown to be wrong (a clear reversal, or a data error) |

   Direction matters: the relation reads `from <type> to`. When in doubt between `contests` and `outmodes`/`disproves`,
   choose `contests`: retirement needs the evidence to be clear.

   **One claim outmoded, the rest standing: correct in place, do not retire.** List what the earlier observation says
   that the later one does not. If anything true is on that list (B13's "who asks for faster examination" was), put
   the outmoded wording right where it stands, add a dated note under it that quotes what it said
   (`- **Restated (11 November 2026; ADR 0058):** the heading said "..."`), fix its atlas headline if that carried the
   claim, and record `refines`. Rewording makes its own check stale: run it.

3. **Record each relation** other than `none` in `analysis/atlas/content/relations.yaml`: `from`, `to`, `type`, `why`
   (one plain-English sentence; any number must be on one of the two pages), `found` (today), plus `settle` for a
   contest (what would settle it) and `asked` for an outmode or disproof.

4. **Outmodes or disproves: ask, never remove.** Add an open question to `docs/owner-questions.md` (next free OQ number)
   asking to retire the observation, with the evidence and your recommendation, and set `asked` to it. The page shows
   "Proposed for retirement" at once. Then run `uv run python -m atlas.currency impact <id>` and bring everything that
   leans on it up to date in the same turn (summaries in `site.yaml`, early signals, other observations' entries).

5. **Only on the owner's explicit approval, retire.** (Rehearsed end to end on B62, 11 November 2026, and reverted.)
   - Add the entry to `analysis/atlas/content/ledger.yaml` (replacing the empty `[]`) with the owner's date and words
     and the A-number.
   - Add a dated bullet as the last line of the observation's own block in its notebook, an addition only, edited in
     the notebook's JSON so no output changes:
     `- **Retired (12 November 2026, ADR 0058, A42):** outmoded by M24; see the ledger.`
   - `uv run python -m atlas.currency status` now lists what still leans on it: other observations' entries and the
     site's summaries and signals. Point each at the replacement. Its own entry stays (the ledger shows its headline
     and reading), and the observation that replaced it keeps its `revisits` of it, shown as "since retired".
   - `check --stale`: the observations that cited it are checked again; only new pairs need judging.
   - Move the question to "Answered". If the owner declines, change the relation's type (usually to `refines`) and
     record the answer.

6. **Check the dependants.** `check --stale` again: observations that cite one just proposed or changed become stale
   and keep their other judgements; judge what is new.

7. **Build and finish.** `uv run python -m atlas.build` (strict: fails on any stale or unjudged check), then
   `node analysis/atlas/passages.mjs`, `uv run pytest -q tests/test_currency.py tests/test_atlas.py`, and say in the
   reply what the check found: relations added, anything proposed for retirement, anything newly open.

## What the atlas shows

Only the current reading (the owner, 11 November 2026). A dated correction lives in the notebook, under the
observation or its reading, and reaches a page only through "Follow the evidence", where the notebook's own words
are quoted. Write every other field (headline, relation `why` and `settle`, limits, figures) as things now stand:
"B13's raw advantage does not survive a like-for-like comparison", never "B13 was corrected to say". The build fails
on amendment history outside the trail.

## Never

- Remove, hide or renumber an observation without the owner's recorded approval.
- Mark a pair `none` without reading both; the review records that you did.
- Edit an observation's own words to make a conflict go away. Correct a genuine error with a dated note, as the
  notebooks already do, and record the relation that found it.
