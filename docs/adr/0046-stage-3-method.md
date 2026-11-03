# 0046: Stage 3's method: each signal with its third factors held together, the review's methods first, the website frozen

**Date:** 2026-11-03. **Whose:** the owner asked for Stage 3 to begin and for the website to be frozen, so that all
effort goes to processing the data (A32); Stage 3 begins with the methods the final review listed (A29) and includes
the name match (A30, ADR 0045). How it is done is Claude's, and the owner can overturn any of it.

**Context.** Stage 2 carried sixteen signals to Stage 3, each with candidate third factors (notebook 2, section 8;
`docs/stage-2-summary.md`, section 4), and the final review listed methods it did not use (`docs/review-stages-1-and-2.md`):
block resampling for §5's changes, 1,000 or more resamples for quoted intervals, B42 and B60 through the crosswalk with
services, fixed-age citation windows (B44 to B46), research spend as an exposure for B62, the window-free order for
B25, the party-aligned filer for B30, heatmap legends, and models that hold the named third factors together. The
skeleton of `03_multivariate.ipynb` (23 October 2026) predates Stage 2 and two of the seven lenses. The plan says Stage
3 is finished with a table of early signals and a table of data gaps (`docs/eda-plan.md`).

**Decision.**

1. **The website is frozen for Stage 3 (A32).** Nothing in `evidence/` or `analysis/atlas/` changes, and
   `python -m atlas.charts` is not rerun. Notebooks 1 and 2 stay as reviewed, since the atlas quotes them. Where
   Stage 3 changes the reading of an earlier observation, its M observation says so ("revisits B42"), and the earlier
   observation is listed in the handover under "Waiting for the atlas", to carry over when the freeze lifts. The rule
   that an observation's page changes in the same commit (ADR 0023) is suspended for Stage 3's observations, which
   have no pages yet.
2. **The notebook follows Stage 2's order.** Section 0 sets out the shared method; sections 1 to 7 take the lenses in
   Stage 2's order (`rights`, `firms`, `regions`, `national`, `timeline`, `industries`, `institutions`); section 8
   holds the two tables the plan asks for. Observations are numbered M1 on. Each lens section has up to three parts:
   **structure** (how its variables group, where it has many numeric ones), **signals with third factors held
   together**, and the **review's methods** for that lens (A29).
3. **Each signal is tested with its third factors held together, in a model suited to its outcome**, and reported
   beside the raw figure, so the reader sees how much of it the factors account for:
   - a yes or no for each right or firm (granted, still in force, has a filing linked): a logistic regression with
     the third factors as categories, reported as the **average marginal effect** (the difference in percentage points,
     with the other factors kept as they are), with standard errors **clustered** by the filer where one filer has
     many rows;
   - counts with an exposure (an area's filing per resident, citations per patent): a negative binomial model, as in
     B29, reported as rate ratios;
   - the small lenses (36 OECD members, 19 divisions, about 110 institutions): partial rank correlations, with
     intervals from 1,000 resamples of the units; leads at most, as in Stage 2;
   - lifetimes (a share still in force): a proportional hazards (Cox) model with delayed entry at grant, as Stage 2's
     survival curves count each right (ADR 0041), reported as hazard ratios; a yes or no "in force at 10 years"
     among granted rights was tried first and rejected, since it treats patents granted at different ages unequally,
     and a landmark at five years kept too few of the older cohorts' patents;
   - money (contract value, licence income): a gamma model, or a Tweedie model where there are zeros;
   - the timeline: trend and season removed first (STL), then the review's block resampling; policy breaks as
     interrupted time series with a trend and the month of the year held and Newey-West intervals.
4. **Verdict words, in each sample** (ratios compared on a log scale). A signal **holds** if its adjusted effect has the raw effect's direction, its
   95% interval excludes zero and at least half of the raw size remains; it is **weakened** if the direction and
   interval hold but less than half remains; **not detected once held** if the interval includes zero; **reversed** if
   it changes direction with an interval that excludes zero. Where the raw association was not itself detected (its
   interval includes zero), it **appears once held** if the adjusted interval excludes zero, and is **not detected
   either way** if not. A signal goes to the early signals table as holding only
   if it holds in both samples. A factor that is a consequence of the signal (whether examination was requested, for
   representation and grant) is not held fixed in the main model; it is shown as a separate reading, as in B6.
5. **Samples as in Stage 2 (ADR 0030, 0041).** Rights: found in FY2010 to FY2019, checked in FY2000 to FY2009, within
   each type of right, except where a measure is reliable only from FY2010 (family reach and citations, B55), when
   the samples are the two halves of FY2010 to FY2019 by `bi.half_sql`; firms and places: the halves of `bi.half_sql`; countries, divisions and institutions: their
   two periods, read as stability checks (ADR 0043); the timeline: its two periods.
6. **Structure before drivers.** Where a lens has many related characteristics (places, countries, divisions,
   institutions), they are reduced first: variance inflation shows how far they repeat each other, and principal
   components summarise them; the components then stand as third factors, so that a gradient of advantage is held
   as one or two measures rather than twenty collinear ones. No single indicator inside a component is read as a
   driver.
7. **Segments only where they are real.** Clusters (k-means on standardised components) are reported with their
   silhouette score; below 0.25 the notebook says there are no clear segments and does not read the clusters as
   kinds of place or country.
8. **Intervals.** From the model (clustered where rows share a filer), or from 1,000 or more resamples of the
   independent unit (A29). For quarterly changes, resamples of blocks of consecutive quarters (a moving-block
   bootstrap), with the effective sample size beside the raw one.
9. **Heatmap legends.** Every correlation map says what its colours and numbers mean, the measure and the rows used,
   in its title and a note (`multi.corr_heatmap`).
10. **The name match (ADR 0045)** is part of the firms section; its matched links stay in their own columns.

**Rejected.**
- **Prediction models (gradient boosting, random forests) with importance scores:** better at predicting, but the
  question is whether a named association survives named factors, which a coefficient with an interval answers more
  plainly; importance scores invite a causal reading.
- **Matching and propensity scores as the main tool:** designs for estimating effects, which the EDA does not claim;
  kept for after Stage 3.
- **Random-effects models for every lens:** heavier to fit and explain; clustered errors give an honest interval for
  this purpose.
- **Applying the review's methods inside notebook 2:** the atlas quotes it and is frozen; Stage 3 records the revisits.

**Consequences.** `03_multivariate.ipynb` is rebuilt from its skeleton. `multivariate.py` gains the helpers above, with
tests. Each later change to an earlier observation is listed for the atlas, not made on it, until the owner lifts the
freeze.
