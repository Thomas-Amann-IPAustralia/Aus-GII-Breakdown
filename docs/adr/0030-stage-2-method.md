# 0030: Stage 2's method: a screen of every pair on one scale, found in one sample and held in another, then the planned pairs

**Date:** 2026-10-28. **Whose:** the owner asked for Stage 2 to begin (A14); Claude chose the method.

**Context.** The plan (`docs/eda-plan.md`) says Stage 2 is finished when "every pair within each lens has been
screened; each lead has its size and interval, survives a correction for the number of pairs tested, and holds in a
second period or sample; candidate third factors are listed". The `bivariate` helpers built before Stage 1 measured
pairs of numbers only (r and rho), while most of the lenses' columns are categories or yes/no flags, many are versions
of the same measure, and the samples are large enough that every pair is "significant". Stage 1 also named fifteen
pairs worth a proper look (`docs/stage-1-summary.md`, section 7).

**Decision.**

1. **Each lens section has two parts: the screen, then the planned pairs.** The screen is systematic and the same for
   every lens; the planned pairs are worked in the units that mean something (a difference in grant rates in
   percentage points, years in force from survival curves), with intervals, in two periods, with third factors named.
2. **One scale for every pair, whatever its kinds** (`bi.association`): |Spearman's rho| for two numbers; the rank
   correlation ratio (the square root of Kruskal-Wallis's epsilon squared) for a number and a category; Cramér's V
   with Bergsma's bias correction for two categories. For a yes/no variable the three coincide with |rho|, so the
   scale is shared. Categories keep their 20 most common values (each held by 30 or more rows), the rest pooled as
   "other". Rank-based measures need no logs and are not moved by extreme values. A pair is measured on the rows where
   both are present, if there are at least 100.
3. **A lead passes four tests** (`bi.replicate`): strength at least 0.1 (conventionally small) in the discovery
   sample; a Benjamini-Hochberg false discovery rate below 5% across the lens's pairs; strength at least 0.1 again,
   in the same direction, and a q-value below 5% (over the pairs taken forward) in a replication sample; and not
   related by construction. The size threshold does most of the work: with 200,000 rows a strength of 0.01 is
   "significant".
4. **The replication sample is a second period where the lens has time, a random half where it does not.** For
   `rights`: discovery FY2010 to FY2019, replication FY2000 to FY2009 (both decided; a pair must hold across a decade
   of change in practice and records). Each type of right is screened apart (pooling types mostly shows that patents
   differ from trade marks), up to 200,000 rights per sample, chosen by a hash of the key so the same rows return on
   every run. Lenses without time (`firms`, `regions`) use the halves of a hash of the key.
5. **The screen's design is a file, `analysis/eda/screens.yaml`, that names every column of the lens** as a number, a
   category, or skipped with its reason (identifiers; dates whose content is in another column, such as the
   examination request date in the years from application to the request). It adds derived columns in SQL (a
   milestone's presence, the gap between two dates, a share) and lists **groups** of variables that are one measure
   or made from each other: the origin of the filer and of the holder, a total and its parts, a status and the flags
   made from it, and age-bound pairs (the filing year against years in force or citations, whose ranges are cut short
   for recent rights). Pairs inside a group are screened but marked "by construction". A test checks that the file
   names every column of `variables.yaml`.
6. **Leads are reported once per pair of families** (`bi.distinct_leads`): where several versions of one measure give
   the same lead, the strongest is kept and the number of versions shown.
7. **Each lead carries** a 95% bootstrap interval for its strength (100 resamples of the full discovery sample: a
   subsample shifts corrected Cramér's V for rare categories), its direction in words (`bi.describe_pair`), and its
   candidate third factors: the variables tied to both members by at least 0.1 in the screen (`bi.third_factors`).
8. **Leads are sorted by judgement in the observations**, not by the code: mechanics of the IP system (Australian
   applicants file PCT applications at IP Australia), quirks of the records, and substantive signals for the
   questions. Only the last are carried to Stage 3 as signals; the others are recorded.
9. **New helpers for the planned pairs:** `rate_difference` (Newcombe's interval), `median_difference` and
   `ratio_by` (bootstrap, resampling whole units such as patents), `rate_ratio`, `survival_with_interval` (a
   survival curve's value at a year with Greenwood's interval) and `dot_chart`.
10. **The notebook is generated, then executed whole.** Its sections are run top to bottom by `nbconvert`, as Stage 1's
    were, and committed with outputs. The rights section takes about seven minutes.

**Rejected.**
- Pearson's r with dummy-coded categories: one coefficient per category, on scales that do not compare.
- Mutual information: one scale, but unbounded and hard to explain to readers who are not data scientists.
- A p-value threshold alone, or Bonferroni's correction alone: with these sample sizes both pass trivial pairs.
- Random halves for `rights`: two halves of one decade agree almost by definition; a second decade is a real test.
- Screening every indicator of the long companion tables (`region_indicators`, `national_indicators`,
  `industry_indicators`) against every other: millions of pairs, nearly all between two Census shares or two OECD
  series, which serve none of the five questions. Their indicators are screened against the lens's IP measures
  instead, and pairs among them only where a planned pair asks (decided when each lens is reached).

**Consequences.** Stage 2's observations are numbered B1 on, each quoting the outputs above it. The website (the
evidence atlas) is not updated during Stage 2, at the owner's instruction: it is updated once Stage 2 is finished.
