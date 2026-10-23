# 0003: Aggregate in DuckDB; commit notebooks with their outputs; rebuild the lens tables rather than commit them

**Date:** 2026-10-23. **Whose:** Claude's.

**Context.** The largest corpus tables have 49 million rows (IP RAPID events) and 20.6 million (ABR). The machine has
about 15 GB of memory and 4 cores. The owner asked that large volumes of data be kept out of Claude's context window.
The repo is shared with readers who will read the notebooks on GitHub rather than run them.

**Decision.**
- **Aggregate in DuckDB.** All reading goes through `eda.sql`, which filters and aggregates in DuckDB. It refuses
  results over 250,000 rows (`TooManyRows`) unless they are asked for deliberately.
- **Keep outputs small.** Helpers return summaries and figures, never raw rows. pandas shows at most 40 rows.
- **Lens tables are rebuilt, not committed.** They are built in about 10 seconds into `analysis/eda/data/`
  (gitignored), and the notebooks build them on first use. They are derived and reproducible, and committing them
  would duplicate about 55 MB of data already in the corpus.
- **Notebooks are committed with their outputs** (charts and tables), so they can be read on GitHub without running
  anything. Images are PNG at 100 dpi to keep files small; Stage 1's skeleton is 0.9 MB.
- **Dependencies.** The analysis has its own dependency group (`uv sync --group analysis`): Jupyter's kernel and
  nbconvert, matplotlib, seaborn, scipy, statsmodels and scikit-learn. All are free.
- **CI** installs the analysis group, lints `analysis/`, and runs `tests/test_eda.py` on synthetic data (no network).

**Consequences.** A reader who wants to re-run a notebook needs the R2 credentials (see `README.md`). Reading one
needs nothing.
