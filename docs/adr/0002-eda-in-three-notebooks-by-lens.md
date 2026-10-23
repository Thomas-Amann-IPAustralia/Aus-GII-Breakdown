# 0002: The EDA is three notebooks, one per stage, each organised by four lenses

**Date:** 2026-10-23. **Whose:** the owner chose the three stages and one notebook per stage; Claude chose the lenses.

**Context.** The owner asked for an in-depth EDA in three stages before any attempt at the five research questions:
univariate, bivariate, then multivariate. It was modelled on a worked notebook about Boston house prices
(`docs/Learners_Notebook_...ipynb`), whose single table had one row per tract.

The corpus is very different: 152 tables from 38 sources, 314.7 million rows, at many grains (an event, a right, an
applicant-year, a business, a postcode, a country-year). Describing "each variable" only makes sense once each row's
meaning (the unit of analysis) is fixed.

**Decision.**
- There is one notebook per stage: `analysis/notebooks/01_univariate.ipynb`, `02_bivariate.ipynb` and
  `03_multivariate.ipynb`.
- Each notebook is organised by the same four **lenses**, each an analysis-ready table built from the corpus
  (`analysis/eda/build.py`):
  - `rights` (one row per IP right);
  - `firms` (one row per ABN);
  - `regions` (one row per postal area);
  - `national` (one row per country, year and indicator).
- These four cover the units the research questions are about: rights (Q1), businesses and places (Q2 to Q4), and
  Australia against other countries (context for Q1 and Q4).
- **Other sources** are profiled in Stage 1, not explored variable by variable. They join the lenses when a question
  needs them: for example, the IP RAPID events (renewals, lapses, oppositions), grants, PBS and TGA.
- **Notebook length.** If a notebook grows past about 25 MB or becomes hard to read, it is split by lens
  (`01a_univariate_rights.ipynb`, and so on). That split is recorded in a new ADR.

**Rejected.**
- One notebook per source: about 40 notebooks, most describing tables no question needs.
- Profiling all 8,067 columns by hand: the automatic profile already does that (`analysis/output/PROFILE.md`).
