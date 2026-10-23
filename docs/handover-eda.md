# Handover: exploratory data analysis

For the next Claude Code session. Read `CLAUDE.md` first, then `docs/eda-plan.md`. Do Stage 1 next; start Stage 2
only when Stage 1's summary is written.

**Status (2026-10-23):** the groundwork is done (ADRs 0001 to 0006), on branch `claude/compassionate-curie-kqjoys`.
Stage 1 has not started beyond its data overviews.

## Where things stand

- **Five lenses** (`analysis/eda/build.py`) build in under a minute (8 to 36 seconds measured):
  - `rights`: 4,368,006 rows;
  - `firms`: 391,983;
  - `regions`: 2,641;
  - `national`: 127,309;
  - `timeline`: 1,473 months, added on the owner's request (ADR 0006).

  The row counts match their sources, and each table has one row per key.
- **`variables.yaml`** describes every lens column. A test fails if it drifts from the built tables.
- **The helpers** (`analysis/eda/`):
  - `data.sql`: DuckDB, with a 250,000-row guard;
  - `data.load_lens`: typed from the register;
  - `style`: the house style, labels, source captions, and `mark_events` for policy changes;
  - `univariate` (including `monthly` for the timeline), `bivariate`, `multivariate`: one module per stage.

  16 tests in `tests/test_eda.py`; the full suite passes (31 tests).
- **The notebooks** (`analysis/notebooks/`):
  - all three are skeletons with planned sections;
  - each has a timeline section (Stage 1 §5, Stage 2 §6, Stage 3 §5);
  - Stage 1's corpus overview and its five lens overviews have been run;
  - observation U0 is the worked example of the format.

## Open items

1. Stage 1, lens by lens. Each lens section lists the checks it plans, and "Leads to check" lists the quirks already
   seen.
2. Decide in Stage 1 how provisional and innovation patents are treated, and what to do with placeholder dates. If a
   lens changes, record the change in a new ADR.
3. For the national lens: the gaps in Australia's R&D series may be fillable from `oecd/msti`.
4. For the timeline:
   - what IP RAPID's "ceased" means, against "lapsed";
   - which months are artefacts (for example, January 1970 for designs);
   - historical fee schedules, which are a data gap for Stage 3's list.

## For the owner

Nothing blocks Stage 1.

## Conventions to keep

- Commit the code, run the notebook, then commit the notebook with its outputs.
- Never print raw rows. Aggregate in DuckDB.
- Next free ADR: 0007.
