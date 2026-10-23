# 0004: Numbered, evidenced observations with a strength label; plain English; accessible charts

**Date:** 2026-10-23. **Whose:** the owner set the principles; Claude chose the format.

**Context.** The owner asked that every observation or suggestion be "clearly and explicitly evidenced", that graphs
be used generously, and that jargon be avoided for readers who are not data scientists. The research goal asks that
evidence be proportionate to the claim, with descriptive, observational, causal and projected findings kept apart.

**Decision.**
- **Observations are numbered by stage:** U1, U2, ... (univariate), B1, ... (bivariate), M1, ... (multivariate).
  Each one:
  - quotes the numbers from the output cell above it;
  - carries one strength label: descriptive, observational, causal or projected.

  Observation U0 in `01_univariate.ipynb` is the worked example.
- **Each lens section ends with a summary table** (observation, evidence, strength, what it carries forward). Each
  stage ends with a summary of what passes to the next stage.
- **Charts:**
  - every chart names its source (`style.source`);
  - axis labels come from `variables.yaml`;
  - colours are the Okabe-Ito palette, which stays readable with colour-blindness.
- **Plain English.**
  - A term is explained where it first appears and in `GLOSSARY.md`.
  - Statistics lead with sizes (differences, rates with 95% intervals, r and rho) and give p-values second, because
    with large samples almost everything is "significant".
- **Leads are not observations.** A quirk noticed while building is recorded as a "lead to check", and becomes an
  observation only once the stage has shown the evidence for it.
