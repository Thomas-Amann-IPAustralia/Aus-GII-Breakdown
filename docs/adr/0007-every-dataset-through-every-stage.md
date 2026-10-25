# 0007: Every dataset goes through all three stages

**Date:** 2026-10-25. **Whose:** the owner decided the principle. Claude chose how to apply it, which the owner can
overturn. This supersedes ADR 0002's rule that sources outside the lenses are "profiled in Stage 1, not explored
variable by variable". It extends ADR 0005 (lens definitions) and ADR 0006 (the timeline).

**Context.** The plan put five lenses through univariate, bivariate and multivariate analysis, and left the other
tables to be brought in "when a question needs it". The owner's intent is different: every datapoint goes through every
stage, and only the approach changes from stage to stage (a variable on its own, against one other, against several).
For a discovery phase that is the better design, because a narrow first cut can hide the signals the EDA exists to
find. The independent review (`docs/Aus-GII-Independent-Review-and-Action-Plan.md`) had tied each repair to when a
table would first be used. Under this decision, a table's repairs come before its Stage 1 section instead.

**Decision.**
- **Every table has a home.** Each table in the corpus is attached to at least one lens. Its variables are brought to
  that lens's unit (a right, a firm, a place, an industry, a research institution, a country-year, a month) by a stated
  join or aggregation. The map, and what each table needs first, is in `docs/eda-plan.md`.
- **Two new lenses**, for data whose unit no current lens shares:
  - `industries`: one row per ANZSIC division and financial year. It holds business counts, entries, exits and survival;
    innovation and barriers by firm size; business R&D; wages by industry; and IP rights assigned to industries
    through the IPC and Nice concordances, which give probabilities, not certainties.
  - `institutions`: one row per Australian research institution and year (identified by ROR). It holds research output
    and citations, citations from patents, ARC and NHMRC grants, and the IP rights the institution files.
- **Frequency.** Monthly and quarterly series join the `timeline`; quarterly ones are compared at quarterly resolution,
  never spread across months. Annual Australian series join the `national` lens, beside the other countries.
- **Tables without a shared unit** go through the three stages within themselves:
  - the ARTG (medicine entries and their sponsors);
  - text (judgments, IP RAPID descriptions), once variables have been derived from it.

  Reference tables (concordances, the evidence and policy registers, the wine GI list) label or build the lenses, and
  are profiled in Stage 1.
- **No duplicates, no errors.** Each lens keeps one row per key, and a test checks it. Where two sources measure the
  same thing, the lens keeps one as the main measure and the other only as a separately labelled comparison. It never
  adds them together, and never counts the same event twice. Examples: WDI and WIPO filings, WDI and OECD R&D, CER's CSV
  and Excel copies, the PBS reports, IPLORD and `applicant_year`, quarterly and monthly CPI. Totals that are sums of
  their parts (persons as the sum of males and females) are not screened against those parts.
- **Detail is kept for drilling down.** Where a lens summarises, the detail stays reachable by key, for example the raw
  postcode, state and country of every applicant, including those overseas.
- **Repairs come before a table's Stage 1 section**, not before Stage 1 as a whole. Stage 1 proceeds lens by lens, and a
  lens starts when its own repairs and attachments are done.
- **Scale.** Every variable gets the systematic Stage 1 profile (completeness, distribution, outliers, quirks), and the
  notable ones get written observations. Stage 2 screens every pair within a lens, as hypothesis generation, with three
  guards: effect sizes with intervals; a correction for the number of pairs tested; and a check that a signal holds in
  a second period or sample before it is reported as a lead. Stage 3 works on the whole set, using PCA, clustering and
  partial correlations.

**Consequences.**
- There is more work before the later lenses' Stage 1 sections. The rights and timeline lenses can start after about a
  day of fixes; the others need their attachments built first (see the plan).
- `analysis/eda/variables.yaml` grows to describe every attached variable, and its test continues to apply.
- The notebooks may need splitting by lens sooner (the 25 MB rule in ADR 0002 still applies).
- The review's tiers (A, B, C) are re-sequenced in the plan by lens; its evidence and finding IDs still apply.
