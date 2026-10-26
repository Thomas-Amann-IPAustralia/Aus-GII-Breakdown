# CLAUDE.md

Research for IPAVentures (IP Australia): how Australia's IP system creates public value, and where IP Australia's
interventions could add the most. The goal and its five questions are in `docs/research-goal.md`. This repo holds the
data corpus (`src/corpus/`, `data/`) and the analysis of it (`analysis/`).

**Current phase: exploratory data analysis (EDA), Stage 1 of 3** (univariate, then bivariate, then multivariate). The
plan is `docs/eda-plan.md`; status and open items are in `docs/handover-eda.md`. Don't start answering the five questions
until Stage 3 is done and the owner says so.

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

## Working with the data

- Keep context small. Never print raw rows or whole tables: aggregate in DuckDB with `eda.sql`, which refuses results
  over 250,000 rows. Read `analysis/output/columns.csv` with filters, not whole.
- **Lenses** are the units of analysis: `rights`, `firms`, `regions`, `national` and `timeline` (monthly), with
  `industries` and `institutions` planned. `regions` has a long companion, `region_indicators` (its attachments: one
  row per postal area, source, indicator and period), and so does `national`, `national_indicators` (one row per
  place, source, indicator and period: 41 million rows); query them with filters, never whole.
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
uv run python -m eda.build                     # the lens tables (seconds)
uv run jupyter nbconvert --to notebook --execute --inplace analysis/notebooks/01_univariate.ipynb
uv run ruff check src tests analysis && uv run ruff format --check src tests analysis
uv run pytest -q
```

## Sessions

- **At the start:** read this file, `docs/handover-eda.md` and the latest ADRs, then check `git log`.
- **Questions for the owner** go in `docs/owner-questions.md`, and answers move to its "Answered" table.
- **At the end:** update the handover, commit, and push to the session's branch.

The working agreement is adapted from `docs/sop-agent-construction-v2 (2).md`, which describes a different project; take
its method, not its content.
