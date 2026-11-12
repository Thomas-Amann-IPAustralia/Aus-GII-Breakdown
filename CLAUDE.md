# CLAUDE.md

Research for IPAVentures (IP Australia): how Australia's IP system creates public value, and where IP Australia's
interventions could add the most. The goal and its five questions are in `docs/research-goal.md`. This repo holds the
data corpus (`src/corpus/`, `data/`) and the analysis of it (`analysis/`).

**Current phase: exploratory data analysis (EDA), Stage 3 of 3 under way** (univariate and bivariate done, reviewed in
full and on the website; Stage 3, multivariate, begun on 3 November 2026 with the methods the final review listed: A29,
A32, ADR 0046; a review of all three stages on the same day filled the gaps it found, A33, ADR 0048). The plan is
`docs/eda-plan.md`; status and open items are in `docs/handover-eda.md`. Don't start
answering the five questions until Stage 3 is done and the owner says so.

**The website freeze is lifted (A34, ADR 0049).** The atlas shows all three stages again: a change to any observation
changes its page in the same commit, and a Stage 3 observation names what it revisits (`revisits`), what it held
(`held`) and its outcome, which the build copies onto the earlier page. Keep notebooks 1 and 2 as reviewed, changing
them only by additions and dated corrections where a gap is found (as the review of 3 November 2026 did, A33), run
cell by cell, never in full.

## Working agreement

- **Get on with it.** Make the analytical and engineering choices yourself. Record the non-obvious ones as an ADR in
  `docs/adr/`.
- **Ask the owner only about:**
  - direction (what to do next);
  - money (any paid API, compute or data; free or very cheap is preferred);
  - adopting a finding as a conclusion;
  - anything outward-facing or irreversible (publishing, sharing data, rewriting history);
  - sourcing new data that needs an account or a request.
- **Flag once:** what you found, the evidence, why it matters, the options, your recommendation, and what you need. Then
  carry on with whatever the flag doesn't affect.
- **Correct your own mistakes** in the turn you find them, in the reply and in the record.
- **Replies:** the outcome first, then the numbers, your recommendation, and the owner's items numbered.

## Evidence rules

- Number every observation. Quote the numbers from the output cell above it, and label its strength: descriptive,
  observational, causal or projected. If a number isn't on the page, it isn't a finding.
- Write in plain English for readers who aren't data scientists. Put each term in `GLOSSARY.md`. Prefer charts to
  tables, and have every chart name its source (`style.source`).
- An association is not a cause. With large samples, lead with effect sizes and intervals, not p-values.

## Keeping every observation current (ADR 0058)

- **Every observation on the atlas must be current.** When you add or change an observation, re-run a cell above one,
  or change data under one, run the currency check in the same turn (`/currency-check`, or `uv run python -m
  atlas.currency check --stale` from `analysis/`): judge each candidate pair and record each relation in
  `analysis/atlas/content/relations.yaml`. The strict atlas build fails until you do.
- **New data, a new source or a change to the lens code** (ADR 0059): after `eda.build`, run `python -m
  eda.fingerprint` (it rewrites `analysis/eda/fingerprints.json`; every observation reading a changed lens table then
  waits). Then, from `analysis/`, `python -m atlas.refresh run`, `report` and `confirm`: the notebooks are run **in a
  copy**, `docs/refresh-report.md` says which quoted numbers moved, and observations whose numbers all came out as
  quoted are cleared with that as the reason. For the rest, re-run their cells in place (cell by cell), amend with a
  dated correction and check. If one cannot be affected, `atlas.currency confirm <id> "why"`. Checking again does not
  clear a wait.
- **Disagreement that settles nothing is kept**, as *contests* with what would settle it: an area for further
  exploration, not a problem to remove.
- **Retire only when nothing true is left that the replacement does not say.** If one claim in an observation is
  outmoded and the rest stands, correct the wording in place with a dated note that quotes what it said, and record
  *refines* (as B13 was, ADR 0058 addendum).
- **The atlas shows only the current reading** (A42). Dated corrections are saved in the notebooks and may be made
  without asking; a page shows them only in "Follow the evidence" (the notebook's own words, the steps and the
  preparation). A headline, reading, figure, relation, limit or section title never says what it used to say; the
  build refuses it.
- **Never remove, hide or renumber an observation without the owner's explicit approval.** An outmoded or disproven
  one is proposed for retirement (an owner question, `asked`), and its page says so at once; only an approved entry
  in `analysis/atlas/content/ledger.yaml`, with the owner's words, retires it.
- `uv run python -m atlas.currency status` shows what is stale, proposed and open; `impact <id>` what leans on one.

## Working with the data

- Keep context small. Never print raw rows or whole tables: aggregate in DuckDB with `eda.sql`, which refuses results
  over 250,000 rows. Read `analysis/output/columns.csv` with filters, not whole.
- **Lenses** are the units of analysis: `rights`, `firms`, `regions`, `national`, `industries` (ANZSIC division and
  financial year), `institutions` (research institution by ROR and calendar year; its IP in `institution_rights`, and
  its reviewed link to names and ABNs in `analysis/eda/institutions/`) and `timeline` (monthly). `regions` has a long companion, `region_indicators` (its attachments: one
  row per postal area, source, indicator and period), and so do `national`, `national_indicators` (one row per
  place, source, indicator and period: 41 million rows), and `industries`, `industry_indicators`; query them with
  filters, never whole.
  - Every dataset goes through all three stages, so every table is attached to at least one lens (ADR 0007; the map is
    in `docs/eda-plan.md`). Keep one row per key, never add two sources for the same measure together, and repair a
    table before its Stage 1 section (`docs/Aus-GII-Independent-Review-and-Action-Plan.md` has the evidence).
  - They are built by `analysis/eda/build.py` into `analysis/eda/data/`, which is gitignored.
  - Each column is described in `analysis/eda/variables.yaml`. Keep it in step with `build.py`; a test checks.
- Corpus reference:
  - `README.md` and `docs/catalogue.md`;
  - the known data quirks: `analysis/output/PROFILE.md` and `analysis/README.md`.
- Large tables come from the R2 bucket. Its credentials are in the environment.

## Commands

```sh
uv sync --group dev --group analysis
uv run python -m eda.build                     # the lens tables (about two minutes; one lens at a time if memory is short)
uv run python -m eda.fingerprint               # the lens tables' fingerprints, committed (ADR 0059)
uv run python -m atlas.refresh run             # from analysis/: the notebooks re-run in a copy; then `report`
uv run python -m audit.benchmark               # IP Australia's published figures against the lenses (ADR 0024)
uv run jupyter nbconvert --to notebook --execute --inplace analysis/notebooks/01_univariate.ipynb
uv run ruff check src tests analysis && uv run ruff format --check src tests analysis
uv run pytest -q
```

## Sessions

- **At the start:** read this file, `docs/handover-eda.md` and the latest ADRs, then check `git log`.
- **Questions for the owner** go in `docs/owner-questions.md`, and answers move to its "Answered" table.
- **External notebook audits** (twelve so far, one per notebook section) are indexed in
  `analysis/GPT-audit/261030/INDEX.md`: which audit covers which observations, how to cite a finding, recurring themes and
  a freshness check. Read the index, not the audits whole; check a finding against the notebook before acting on it, and
  act on them only at the owner's direction. What has been acted on, finding by finding, is in `AMENDMENTS.md` there. They are distinct from `analysis/audit/` (the check against IP Australia).
- **Both stages were reviewed in full** on 2 November 2026 (pass 8, ADR 0043): the assessment is
  `docs/review-stages-1-and-2.md`, with the methods still to adopt in Stage 3.
- **The evidence atlas** (`evidence/`, built by `analysis/atlas/`) matches all three notebooks (ADR 0044, 0049): a
  change to an observation changes its page in the same commit, `uv run python -m atlas.build` must pass (the numbers
  rule), and drawn charts are redrawn with `python -m atlas.charts` after `eda.build`. Stage 3's plain English is in
  `analysis/atlas/content/observations/stage3/`. Each observation also has a plain-English reading just above it in its notebook
  (`##### Observation U12 in plain English`, ADR 0055): the pages lead with it, the build checks its numbers, and a new
  observation needs one. The rest of each page is plain English too (ADR 0056: "allowing for", "likely range",
  "2025–26"), and the numbers rule checks every visible field. After `atlas.build`, run `node analysis/atlas/passages.mjs`: the
  chat's evidence (`evidence/data/passages.jsonl`, ADR 0054) must match the pages, and a test checks. The chat
  ("Ask the atlas", `#/ask`, `evidence/js/chat.js`) is served by the Econ repository's API; to make a change reach it,
  in Econ run `econ atlas-ingest --ref <this commit>`, set the sha in its `config/atlas.yaml`, then
  `econ index --kb atlas`, and commit (Econ's `docs/deploy.md`). `node analysis/atlas/chat_check.mjs` checks the page.
- **For Stage 2, use the full audit** in `analysis/claude-audit/261102/INDEX.md` (a Claude Code session, 2 November
  2026; the working list for Stage 2, A24; every finding acted on by pass 8): it rechecks the four Stage 2 audits above against the amended notebook, keeping their finding numbers, audits
  §5 to §8, and gathers the survival theme's findings in one table. Same rules: check, then act at the owner's direction.
- **At the end:** update the handover, commit, and push to the session's branch.

The working agreement is adapted from `docs/sop-agent-construction-v2 (2).md`, which describes a different project; take
its method, not its content.
