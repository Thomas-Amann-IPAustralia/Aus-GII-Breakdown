# Handover: exploratory data analysis

For the next Claude Code session. Read `CLAUDE.md` first, then `docs/eda-plan.md`. Do Stage 1 next; start Stage 2
only when Stage 1's summary is written.

**Status (2026-10-23):** the groundwork is done (ADRs 0001 to 0005), on branch `claude/compassionate-curie-kqjoys`.
Stage 1 has not started beyond its data overviews.

## Where things stand

- **The lenses** (`analysis/eda/build.py`) build in about 10 seconds:
  - `rights`: 4,368,006 rows;
  - `firms`: 391,983;
  - `regions`: 2,641;
  - `national`: 127,309.

  The row counts match their sources, and each table has one row per key.
- **`variables.yaml`** describes every lens column. A test fails if it drifts from the built tables.
- **The helpers** (`analysis/eda/`):
  - `data.sql`: DuckDB, with a 250,000-row guard;
  - `data.load_lens`: typed from the register;
  - `style`: the house style, labels and source captions;
  - `univariate`, `bivariate`, `multivariate`: one module per stage.

  15 tests in `tests/test_eda.py` run on synthetic data. The full suite passes (30 tests).
- **The notebooks** (`analysis/notebooks/`):
  - all three are skeletons with planned sections;
  - Stage 1's corpus overview and its four lens overviews have been run;
  - observation U0 is the worked example of the format.

## Open items

1. Stage 1, lens by lens. Each lens section lists the checks it plans, and "Leads to check" lists the quirks already
   seen.
2. Decide in Stage 1 how provisional and innovation patents are treated, and what to do with placeholder dates. If a
   lens changes, record the change in a new ADR.
3. For the national lens: the gaps in Australia's R&D series may be fillable from `oecd/msti`.

## For the owner

Nothing blocks Stage 1. See the reply on this session for optional items.

## Conventions to keep

- Commit the code, run the notebook, then commit the notebook with its outputs.
- Never print raw rows. Aggregate in DuckDB.
- Next free ADR: 0006.
