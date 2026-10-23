# EDA plan: getting to know the data before answering the questions

**Status (2026-10-23):** the groundwork is built and verified; Stage 1 is ready to start. This plan says what the
exploratory data analysis (EDA) covers, how it is done, and when each stage is finished. Decisions behind it are in
`docs/adr/` (0002 to 0005); terms are in `GLOSSARY.md`.

## Why an EDA first

The research goal (`docs/research-goal.md`) asks what public value the IP system creates, for whom, what makes it
work, and where intervention would add most. Answering those well depends on knowing what the data can and cannot
say: how complete each measure is, how it is distributed, what its quirks are, and which relationships are strong
enough to be worth a proper test. The EDA builds that understanding in three stages and ends with a short list of
early signals and data gaps. Only then are the questions themselves tackled.

## The units of analysis: five lenses

The corpus has 152 tables at many levels of detail. The EDA works on five analysis-ready tables (lenses), each with
one clear meaning per row. They are built in seconds by `uv run python -m eda.build`.

| Lens | One row per | Rows | Main questions | What it holds |
|---|---|---|---|---|
| `rights` | IP right | 4,368,006 | Q1, Q2 | Type, status, dates, time to registration, applicant origin and type, attorney use, class |
| `firms` | ABN in any IP, R&D, procurement or tax source | 391,983 | Q2, Q3, Q4 | Entity type, age, place, IP applications, R&D claims, income, government contracts |
| `regions` | Postal area | 2,641 | Q2, Q4 | Population, remoteness, SEIFA, Census medians, businesses, IP applications and rates, R&D claimants |
| `national` | Country, year and indicator | 127,309 | Q1, Q4 (context) | 22 World Bank indicators and WIPO filings by residents, for every country |
| `timeline` | Month, for Australia (Jan 1904 to Sep 2026) | 1,473 | Q1, Q4, Q5 | Applications by type and origin; grants, lapses, expiries, oppositions, assignments, extensions of term; the 13 IP policy changes |

Time is a column in every lens; the `timeline` lens adds Australia's own month-by-month view, for seasonal patterns,
what happened around each policy change, and any later forecasting (ADR 0006). Comparisons over time use changes or
the months around events, not levels, because series that trend together over decades correlate whatever their link.

Everything else in the corpus (citations, grants, PBS, court judgments, wellbeing data) is profiled in Stage 1 and
brought in when a question needs it.

## The three stages

| Stage | Notebook | Asks | Main tools (`analysis/eda/`) | Finished when |
|---|---|---|---|---|
| 1. Univariate | `analysis/notebooks/01_univariate.ipynb` | What does each variable look like on its own: completeness, shape, outliers, quirks? | `univariate`: `overview`, `describe`, `distribution`, `bin_check`, `counts`, `missing`, `over_time`, `monthly` | Every lens variable has a section with evidenced observations; exclusions and transformations are decided and recorded; the pairs to test are listed |
| 2. Bivariate | `02_bivariate.ipynb` | Which pairs move together, in what shape, how strongly, for whom? | `bivariate`: `screen_pairs`, `pair_stats`, `scatter_trend`, `binned_summary`, `compare_groups`, `rate_by`, `rate_chart` | The planned pairs are tested; each signal has its size and interval; candidate third factors are listed |
| 3. Multivariate | `03_multivariate.ipynb` | Do the signals survive other factors? What structure and segments exist? | `multivariate`: `corr_heatmap`, `pca`, `scree`, `vif`, `partial_corr`, `clusters`, `assign` | A table of early signals (evidence, strength, question, next step) and a table of data gaps (why, possible source, cost) |

Each notebook already has a section per lens with the planned analyses listed, the research question each informs,
and the helper that does it. Stage 1 also has its data overviews run.

## How the work is done

- **Evidence.** Observations are numbered (U1, B1, M1, ...), quote the numbers above them and are labelled descriptive,
  observational, causal or projected (ADR 0004). Observation U0 in Stage 1 is the worked example.
- **Visual first.** A chart for each variable or pair, with plain-English labels from `analysis/eda/variables.yaml` and
  its source underneath.
- **Small outputs.** Aggregate in DuckDB; never print raw rows (ADR 0003).
- **Rhythm.** One lens section at a time: run, read the outputs, write the observations, commit. A stage ends with its
  summary, an update to `docs/handover-eda.md` and, for anything that changes a lens, an ADR.
- **Reviewing.** Each stage's notebook is committed with its outputs so that it can be read on GitHub without running
  anything.

## Leads already found (to confirm in Stage 1)

Found while building the lenses; not yet findings.

- 264,024 patent rows are provisional applications, which are never granted; they need separating from standard patents.
- Registration dates as early as 1901-01-01, and 1,497 rights (1,493 of them trade marks) registered before they were
  applied for: likely placeholder dates.
- Patent applications per year show no drop-off in the latest years (FY2025: 35,065; FY2026: 41,257), so IP RAPID
  appears to list applications before publication.
- About 80% of patent rights have no Australian postcode (their applicants are overseas).
- Some postal areas have no residents (population, median age and income of 0).
- Australia's World Bank series for researchers in R&D ends in 2010, and R&D spending (% of GDP) in 2021.
- Rushes before rule changes: the busiest month for standard patent applications is April 2013 (1,018 from Australian
  applicants, 5,407 from overseas), when the Raising the Bar reforms took effect; second-tier patent applications peak
  at 2,789 in August 2021, the month innovation patents closed.
- Designs registered begin in January 1970, which looks like a placeholder date.

## After Stage 3

1. Review the early signals and data gaps with the owner.
2. Source additional data for the gaps worth filling (free first; costs proposed with estimates).
3. Only then, design the analyses that answer the five questions: descriptive where that suffices, and natural
   experiments or other designs where additionality is claimed. Heavier tools (for example, time-series foundation
   models) are considered at that point, on evidence that they beat simpler methods on this data.
