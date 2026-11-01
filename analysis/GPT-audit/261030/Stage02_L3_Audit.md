# Stage 2 notebook audit: Lens 3, Places

**Reviewed:** 2 November 2026. **Source:** [02_bivariate.ipynb](https://github.com/Thomas-Amann-IPAustralia/Aus-GII-Breakdown/blob/1581223dc2fbb2ce1a1c26fab77a14f459eb023a/analysis/notebooks/02_bivariate.ipynb), retrieved from `main` and checked against the pinned commit.

**Format:** Numbered, prioritised findings with an **Issue** and **Action**, following the earlier univariate audits. R01–R33 are local to this report.

**Scope:** Only §3, from its introduction through §3.7: 24 cells, including all nine code cells, their saved outputs and both embedded charts. The notebook introduction and the Places row in §8 were consulted to check methodological promises and repeated claims. The univariate Places audit and Stage 1 §§8–9 audit informed the review, together with relevant findings in the Firms, Industries and completed L0–L1 audits. Relevant Stage 1 notebook passages were checked directly. The GitHub Pages website, underlying datasets, imported helper implementations, ADRs and external summary document were not assessed. Neither notebook was re-executed or changed.

**Overall finding:** Most quoted coefficients match the saved tables. The major problems concern interpretation and comparability: a joint model exceeds strictly bivariate scope; hash splits are not consistently evidenced; geographic and denominator qualifications are lost; and the income, manufacturing and change-over-time headlines claim more than their analyses establish. The later ATO and Census additions add useful comparisons but do not resolve the earlier validity concerns.

**Priority:** **High** affects interpretation, validity or downstream use. **Medium** should be corrected before relying on or circulating the findings. Requested implementation checks are not findings that unseen code or data are wrong.

**Read first:** R01–R03, R05, R13–R14, R21, R23–R29. Apply each correction to the corresponding §3.7 row and any repetition of the Places finding in §8.

## Scope, samples and measurement

### R01 — High | §3.2 / B29: the joint model is multivariable

**Issue:** The formula `count ~ z_irsad + C(remoteness, ...)` estimates advantage and remoteness together, in addition to the population exposure. It therefore exceeds a strict two-variable analysis. Statements that the relationships persist at the same advantage, or that each accounts for part of the other, describe adjusted associations. The single-predictor models, pairwise correlations, comparisons of halves and largest-filer sensitivity check do not automatically become multivariable merely because many results are presented.

**Action:** Move the joint models and adjusted conclusions to Stage 3, or explicitly identify them as a permitted Stage 2 multivariable sensitivity analysis. Keep the unadjusted and adjusted estimates clearly separated. Listing candidate third factors or proposing PCA is not itself a completed multivariate analysis. Evidence: `f80eb1ec`, `8175d81b`.

### R02 — High | §§3.0, 3.2, 3.5–3.6: the claimed common halves are inconsistent

**Issue:** The core screen reports **1,377 discovery and 1,264 replication areas**. B58 reports **1,266 replication areas** for one ATO pair, although that query selects a subset of the same postal-area lens. Its patent pair also has **438 discovery areas**, against B27's **431**. Those cannot simply be subsets of the stated fixed halves. The notebook uses `bi.screen_sample`, explicit SQL hashing with a `stage2` suffix, and `bi.split_half`; it does not show that their membership or Boolean labels agree.

**Action:** Establish one canonical postcode-to-half mapping and join it into every Places analysis. Show membership agreement, unique-area counts and exclusions for each section; reconcile the saved counts before calling B58/B59 the lens's same halves. The notebook establishes an inconsistency, but not which helper or labelling convention caused it. Evidence: `1cb83215`, `f80eb1ec`, `ecc34934`, `b7179e5a`.

### R03 — High | Throughout: random postal-area halves do not establish independent geographic replication

**Issue:** Hashing postcode rows separates records, but nearby areas can share economic conditions, filers and allocated source-area measurements. SA2/PHA-derived values can contribute to both halves. Similar results therefore show internal split stability, not independence from spatial dependence, allocation choices or shared measurement errors. Ordinary correlation p-values, area-level bootstrap intervals and model intervals do not visibly account for these dependencies.

**Action:** Describe the second half as an internal robustness check. Add spatial/source-area blocking or leave-region-out sensitivity and uncertainty that respects the relevant clustering before claiming geographic generalisability. Show residual spatial checks for the models. This does not prove the reported associations disappear; it limits what replication and the intervals establish. Evidence: `1ca091d5`, `0a576241`, `f80eb1ec`; Stage 1 Places R18–R19/R29.

### R04 — High | §3 rules / B27–B31 / B58: rates combine different dates and populations

**Issue:** FY2017–FY2026 applications are annualised against a fixed 2021 resident population or a snapshot of active GST-registered ABNs. Organisation applicants need not belong to that active GST population. ATO comparisons add a 2023–24 tax-return population; CABEE uses June 2025. These are contextual application intensities, not matched-population filing probabilities or evidence that the same people/businesses filed more. Population offsets do not repair these mismatches.

**Action:** State each numerator's period, attribution rule and denominator's date and population. Use wording such as average annual recorded applications relative to the stated population stock. Where practical, compare aligned periods and annual exposures; otherwise retain the mismatch beside the conclusions. Distinguish filing-address counts from current ABR-address counts of firms. Evidence: `1ca091d5`, `f80eb1ec`, `c3c0b719`, `ecc34934`; Stage 1 Places R07, Firms R61.

### R05 — High | Throughout / B29: geographic sensitivity remains unresolved

**Issue:** The analysis covers matched filing postcodes, not all Australian applications or their operating locations. Stage 1 already identified unmatched university-associated postcodes and explicitly left their effect on regional results for Stage 2. No such remapping/exclusion sensitivity is displayed here. Pooling available postal areas does not recover omitted applications. Whole-area remoteness labels and `sa3_code` also do not establish exact physical locations of residents, firms or filings.

**Action:** Carry forward unmatched/missing-postcode coverage and party-attribution qualifications. Add the promised sensitivity for institutional and other unmatched filings before treating the gradient as geographically comprehensive. Label SA3 results as pools of postal areas assigned to SA3s, with allocation rules and exclusions; retain the distinction between registered/filing addresses and where work occurs. Evidence: `1ca091d5`, `f80eb1ec`; Stage 1 U49, U87 and Places R04/R06/R08/R14.

### R06 — High | B27 / heatmap: absent linked filings are still called never filing

**Issue:** B27 and the heatmap describe R&D claimants with no recorded linked filings as having never filed IP. The earlier audits identify incomplete linkage, historical IP evidence without counts and uncertainty about propagation of register-filled ABNs. These can alter the area's non-filer share and its correlations. Calling recorded use a lower bound does not make the complementary non-use share a lower bound.

**Action:** Use no filing linked under the current attribution rules, with the eligible claimant population and observation window. Reconcile historical source membership and filled ABNs before interpreting the share as non-use. Keep acquisition and unmeasured forms of IP outside the claim. Evidence: `bd7702fc`, chart in `1cb83215`; Stage 1 Places R15, Firms R48 and Stage 1 summary R17.

### R07 — High | B27–B28: shared denominators and overlapping populations can contribute to correlations

**Issue:** The strongest pair, IP-filing firms and R&D claimants per business (**0.884; 0.909**), shares the GST-business denominator and can overlap in its numerators. Patent, trade mark and design rates share residents; attached count-based indicators also divide by residents. These relationships may be substantively informative, but ranking rates does not remove mathematical coupling or dependence on denominator variation. Excluding only explicitly configured by-construction pairs does not establish that the remaining leads are independent signals.

**Action:** Identify common denominators and numerator overlap. Add sensitivity using counts with suitable exposures, denominator strata or other justified specifications, and distinguish these checks from the primary pairwise description. Do not infer distinct mechanisms merely from strong rate correlations. Evidence: `1cb83215`, `0a576241`, `bd7702fc`.

### R08 — Medium | §3 rules / B27 / later additions: sample restrictions are not universal

**Issue:** The blanket ten-expected-applications rule describes prebuilt application-rate fields, not every later statistic. B29 models counts in **2,528** areas with at least 100 residents and a known IRSAD score; B58's new individual-filing ratio only requires a positive business-income count; B59 requires at least 1,000 residents at both dates. The strongest patent and trade mark attachment results also use very different samples, commonly **431 versus 1,074 discovery areas**. Cross-outcome differences can therefore reflect composition as well as association.

**Action:** Give eligibility and exclusions per analysis, including pairwise non-null counts and denominator sizes. State that count modelling deliberately includes areas whose displayed rates were suppressed; this is not inherently an error. Compare associations on a common-area subset before ranking their relative strength. Define the threshold as a reporting choice, not proof of validity. Evidence: `bd7702fc`, `0a576241`, `f80eb1ec`, `ecc34934`, `b7179e5a`; Stage 1 Places R13.

## Core and attachment screens

### R09 — Medium | B27 / §3.7: overall strength agreement becomes a universal replication claim

**Issue:** The **0.961** is a rank correlation between measured pair strengths across the two halves, excluding configured by-construction pairs. It is not the correlation for any particular economic relationship, a replication success rate, or agreement in every direction. The screen separately reports **269 lead versions, 16 not replicated, and 124 distinct leads**. The summary's blanket yes obscures those differences. Collapsing to the strongest version also makes its interval conditional on selection.

**Action:** Label 0.961 precisely and retain the verdict counts. Distinguish pair versions, distinct leads and the 75 distinct IP/R&D leads. Show sample size and direction for each reported lead; avoid treating a selected strongest version's interval as selection-adjusted evidence. Evidence: `1cb83215`, `bd7702fc`, `a9f5687a`.

### R10 — Medium | §3.1 / B28: the attachment inventory is an earlier subset

**Issue:** The text says the companion table holds **6,406 indicators from five sources**, but the query explicitly excludes `ato_postcode` and `census_tsp`, which appear in §§3.5–3.6. The five-source figure is valid for the chosen screen, not the current table's full inventory. Selected pairs in the additions do not establish that every indicator in those sources was screened.

**Action:** Call this the original five-source screen and show its exclusions. Update the inventory to distinguish full source coverage, indicators screened and deliberately selected later pairs. Preserve the original screen's multiple-testing family rather than silently presenting its counts as current all-source totals. Evidence: `5cc45503`, `0a576241`, `f5adf89a`, `08716ea5`; Stage 1 Places R02 and Stage 1 summary R03.

### R11 — High | §3.1 / B28: dividing every additive value by residents does not create comparable shares

**Issue:** The code transforms every `additive` value into units per 1,000 total residents. That is not necessarily a share of an eligible whole group, as the introduction claims: businesses, installations, male graduates, dwellings and other counts have different relevant populations. It mixes prevalence, demographic composition and business density. Non-additive values transferred by resident-weighted averaging remain proxies, not necessarily the actual postal-area median, percentage or standardised rate.

**Action:** Define units and appropriate denominators by indicator family. Label contextual per-resident quantities honestly, retain the allocation method and source geography, and use numerator/eligible-denominator aggregation where valid. Explain whether the land-area result uses hectares or hectares per resident under the transformation rule. Do not treat the Stage 1 allocation checks as validation of every transferred measure. Evidence: `5cc45503`, `0a576241`, `47c98879`; Stage 1 Places R18–R21.

### R12 — Medium | §3.1: period selection counts rows and orders labels, not verified usable coverage and chronology

**Issue:** `BEST` chooses the period using `count(*)` and a lexical `ORDER BY period`. Row presence can include null values, so it does not necessarily maximise usable area coverage. Text periods across these sources need not sort chronologically. The resulting comparisons mix years and windows, with examples spanning 2021, 2022, 2024 and June 2025 against a ten-year filing average.

**Action:** Select on distinct areas with usable values, parse dates/windows explicitly and display the chosen period with each result. Give a time-aligned sensitivity or retain an explicit mixed-period limitation. Do not call this the latest period unless the chronology test establishes it. Evidence: `0a576241`, `b259f002`; Stage 1 Places R17/R22.

### R13 — High | B28: pairwise screening does not establish one underlying dimension

**Issue:** The **24,792 leads out of 38,217 measured pairs (64.9%)** are indicator–rate combinations, not 24,792 independent discoveries. The top table visibly repeats the same professional-services total across CABEE employment/turnover tables and Data by Region. Correlations of many indicators with filing do not demonstrate that they form one latent dimension or that no separate signal exists. PCA is proposed for Stage 3, not shown here.

**Action:** Report replicated indicator–rate combinations and quantify duplicate/overlapping measures. Do not turn the percentage of pairs into a percentage of distinct indicators without the corresponding calculation. Describe a possible shared socioeconomic pattern as a hypothesis. Defer dimensionality claims until a justified component/factor analysis and sensitivity checks are displayed; preserve the possibility of multiple dimensions. A proposed PCA step is not evidence that one dimension already explains the findings. Evidence: `0a576241`, `b259f002`, `47c98879`.

## Advantage, remoteness and concentration

### R14 — High | B29: the headline claims an SA3 check that was not fitted

**Issue:** B29 says advantage and remoteness both hold together and when pooled into SA3s. The SA3 loop fits **IRSAD only**. There is no displayed SA3 remoteness or joint model. The postal-area remoteness estimates also do not form a uniformly declining sequence: for standard patents in discovery, the unadjusted ratios are **0.259 inner regional, 0.289 outer regional and 0.338 remote**, before **0.173 very remote**. The evidence supports differences from major-city-classified areas, not a monotonic decline with every remoteness step.

**Action:** Say that the IRSAD association remains positive in the pooled-area analysis, and that all displayed non-major-city categories have lower modelled rates than major cities. Restrict the adjusted conclusion to postal-area models. Show category counts and intervals; do not imply an unperformed joint geographic replication. Evidence: `f80eb1ec`, `8175d81b`.

### R15 — High | §3.2: negative-binomial convergence is not a model adequacy check

**Issue:** All fits report convergence, but warnings are suppressed and no residual, influence, zero-count, functional-form or spatial-dependence diagnostics are shown. The model uses a single linear IRSAD term on the log-rate scale, whereas the prose emphasises a concentration at high deciles. Large estimated dispersion supports allowing extra-Poisson variation; it does not establish that this specification captures the data or makes its ratio the steadier reading.

**Action:** Separate optimisation success from model adequacy. Surface consequential warnings and add targeted diagnostics, nonlinear/decile sensitivity and influential-area checks. State that reported intervals are conditional on the model and exposure assumptions. Replace claims about spread beyond chance with spread relative to the specified Poisson benchmark. Evidence: `c4fc1b7a`, `f80eb1ec`, `8175d81b`; Stage 1 Places R12 and Stage 1 summary R16.

### R16 — Medium | B29 / decile chart: the shape and proposed explanation are overstated

**Issue:** The description emphasises a steep gradient in the most advantaged fifth and a steadier trade mark rise, but does not quantify the top-fifth contribution or establish that IRSAD deciles divide the retained areas into equal fifths. Trade marks fall from **31.60 to 29.24** in discovery deciles 9–10; designs fall from **1.54 to 1.21**, while both rise sharply in replication. The claimed city-centre cause of the split difference is not checked in this section. The fitted log-linear model and the resident-weighted decile totals also summarise different aspects of the data.

**Action:** Describe the visible reversals and quantify any claim about where most of the gradient lies. Use IRSAD deciles 9–10 unless the relevant area shares are shown. Treat the city-centre explanation as a candidate, with per-area contributions or leave-out estimates, rather than an established cause. Do not infer a tested nonlinear relationship solely from the pooled display. Evidence: `9ea0a1c6`, `8175d81b`.

### R17 — High | §3.2 chart: Poisson error bars conflict with the overdispersion discussion

**Issue:** The chart pools counts by decile and half, then applies `uni.poisson_interval`. Its narrow bars do not capture between-area heterogeneity, spatial dependence or denominator/allocation uncertainty, even though those concerns motivate the negative-binomial models. The figure does not identify the interval type. Readers can therefore mistake the bars for uncertainty about the broader area gradient.

**Action:** Label the bars as conditional Poisson count intervals and state their limitations, or show uncertainty consistent with the intended area-level inference, such as a justified clustered bootstrap or model-based prediction. Keep the difference between resident-weighted pooled rates and the fitted area-level model explicit. Evidence: `9ea0a1c6`, `f80eb1ec`; Stage 1 Places R12–R14.

### R18 — High | §3.3 / B30: the removal result is narrower than the conclusion

**Issue:** Removing each area's largest identified filer leaves positive IRSAD ratios (**1.897; 1.961**), but cannot establish that large filers merely add noise. Missing-ABN applications are deliberately treated as separate filers; an unidentified dominant filer can remain, and removing one ABN does not remove a corporate group or all concentration. **29.2%** is the combined share removed across areas, not the largest filer's share in every area. Applications are described as held even though the query counts filing attribution.

**Action:** Report the specific removal sensitivity and pooled share: the association persists under this identification rule. Use applications attributed to the largest identified ABN and show missing-ABN coverage and concentration distributions. Do not interpret the increase in point estimates as an established difference without a paired uncertainty comparison. Retire the rule that concentration has been excluded as an explanation. Evidence: `a2d6c7e2`, `348901fd`, `8f0bb876`; Stage 1 Places R10.

## Business mix

### R19 — High | §3.4 / B31: CABEE composition and the ABR exposure are different populations

**Issue:** Industry shares divide allocated CABEE counts by their CABEE total, while application rates divide organisation filings by active GST-registered ABNs. Stage 1 found that the business universes and dates differ; CABEE is not established as a decomposition of the ABR stock. The 100-business filter applies to the summed CABEE divisions, while application-rate eligibility comes from a separate prebuilt field.

**Action:** Name both denominators, dates, geographic allocation and eligibility rules. Describe the result as CABEE area composition against filing relative to ABR business stock. Test an aligned-denominator specification if feasible; do not describe the ratios as filing propensity among the same businesses. Evidence: `93daf5a9`, `c3c0b719`; Stage 1 Places R20 and summary R18.

### R20 — High | B31: the headline generalises patent-only patterns to filing overall

**Issue:** The negative construction/transport pattern applies to standard patents. Their trade mark correlations are **0.025/0.051** and **−0.015/−0.070**, respectively. Manufacturing's patent correlations **0.119/−0.021** show weak, inconsistent association, not that manufacturing makes no difference. The clearer negative trade mark association is agriculture (**−0.622/−0.655**), and positive associations include health care and education.

**Action:** Separate patent and trade mark findings in the headline and summary. Replace no difference with no consistent monotonic association in these samples. Retain the different industry patterns without converting weak estimates into evidence of no relationship. Evidence: `c3c0b719`, `c3a6cba9`, `a9f5687a`.

### R21 — High | B31: the manufacturing and head-office explanation is unsupported

**Issue:** The assertion that manufacturers file the patents relies on U75, which allocates patent technology classes through a crosswalk; it does not observe each applicant's industry. A weak correlation with an area's manufacturing share does not show that patenting places are not manufacturing places, nor establish that manufacturers' head offices sit among city-centre services. The later services crosswalk changes the allocation and further limits reliance on the older shorthand. B31 also treats filing postcode and ABR registered address as interchangeable without a displayed reconciliation.

**Action:** Remove the explanation from the finding. Present it as a hypothesis requiring linked applicant industry, relevant address dates and operating-location evidence. Distinguish technology-to-industry allocation from firms' actual industries, and acknowledge the updated crosswalk sensitivity. Evidence: `c3a6cba9`; Stage 1 Industries R03–R04/R10, Firms R61 and completed L0–L1 R39.

### R22 — Medium | §3.4: industry shares are compositional, not isolated industry effects

**Issue:** The 19 shares sum to one within an area, so an increase in one necessarily changes the relative shares of others. Separate correlations cannot show the independent contribution of any industry, or establish that business mix explains B29. The code also drops division `X` before forming its denominator without quantifying that exclusion locally.

**Action:** State that these are marginal relationships with relative composition. Show excluded/unknown-industry shares and retained-area counts. Keep any independent-effect or explanatory decomposition for a suitable Stage 3 model; do not include all shares with an intercept without a reference or other compositional treatment. Evidence: `c3c0b719`, `c3a6cba9`.

## ATO income and individual-filing addition

### R23 — High | §3.5 / B58: business-income tax records are not a matched population of filers

**Issue:** The denominator counts individual tax records reporting total business income in 2023–24. It does not establish everyone who runs or owns a business, or that the individual applicants counted over FY2017–FY2026 belong to that group. Taxable income divided by individual tax-lodger counts is also not income per resident. The earlier audit explicitly questioned using this denominator as a filing rate; the Stage 2 comparison does not resolve that issue.

**Action:** Label the measure as annualised applications relative to individual tax lodgers reporting business income, with both periods. Use taxable income per individual tax lodger and business-income reporting share. Treat these as contextual area ratios unless membership and timing are aligned; do not call them filing rates among business owners. Evidence: `f5adf89a`, `ecc34934`, `539d13ec`; Stage 1 Places R26–R27.

### R24 — High | B58: subtracting organisation applications does not prove individual applications

**Issue:** The numerator is total standard patents, trade marks and designs minus their organisation counts. That equals individual counts only if every other record is a correctly identified individual, with consistent party selection. Unknown or other types would enter the remainder. Stage 1's individual shares explicitly depend on known applicant type; the notebook does not reconcile the subtraction to direct individual classification here.

**Action:** Count positively identified individual applicants, report unknown/other types and verify that type and postcode describe the same selected party. Show the reconciliation to the existing remainder before retaining the individual-filing label. This is a validation requirement, not evidence that every remainder record is misclassified. Evidence: `ecc34934`; Stage 1 Places R04, completed L0–L1 R39.

### R25 — Medium | B58: pooled rights and small tax denominators obscure what drives the result

**Issue:** The new ratio adds three distinct application types with equal weight, omits provisionals and uses only `business > 0` as its tax-denominator filter. It is not the previously suppressed type-specific rate and can be unstable where few tax lodgers report business income. No type-specific breakdown or denominator distribution shows whether trade marks dominate the gradient. Median ratios within deciles are unweighted medians of area ratios, not pooled filing rates for the decile's people.

**Action:** Describe the composite exactly, show its type contributions, and repeat it by right type. Report denominator quantiles and a justified sensitivity to small denominators. Label the **3.84 to 11.03** comparison as medians across eligible areas, with counts by decile; do not interpret it as an individual-level propensity difference. Evidence: `ecc34934`, `539d13ec`.

### R26 — High | B58: the analysis does not rule out business composition as an explanation

**Issue:** Comparing pairwise correlations with a business-income share, or dividing applications by a business-income count, does not hold business participation or other factors constant. The headline and Stage 3 handover nevertheless conclude that the advantage gradient is not explained by business owners. The share itself has positive correlations with patents (**0.191/0.181**) and trade marks (**0.194/0.211**); the statement that income and advantage, not people in business, go with filing is too exclusive.

**Action:** State that income has the larger observed rank correlation in these particular comparisons and that the contextual ratio remains positively associated with IRSAD. Keep the explanation unresolved. If adjustment is needed, define an appropriate model and population in Stage 3, after repairing the numerator/denominator issues. Evidence: `ecc34934`, `539d13ec`.

## Census change addition

### R27 — High | B59: weak change correlations become claims of no gains and no effect

**Issue:** Small negative correlations do not establish that areas gaining graduates or income did not gain filings, or that increased education/income cannot lift filing. The table does not count which areas gained both. Graduate-share change and trade mark change are consistently weakly negative (**−0.124; −0.115**), above the notebook's 0.1 size threshold in magnitude, rather than simply absent. The headline's standing-difference interpretation and the Stage 3 levels-not-changes rule exceed this two-window comparison.

**Action:** Say that this selected-area, two-window analysis finds weak negative monotonic associations and no positive association in the reported pairs. Add joint-direction counts or change scatterplots if statements about which areas gained are needed. Do not infer causation, equivalence or an absence of lagged/nonlinear relationships. Evidence: `b7179e5a`, `926d52ec`, `a9f5687a`.

### R28 — High | B59: historical allocated proxies are treated as directly observed area change

**Issue:** U118 documents historical SA2 values transferred using 2021 resident weights. That does not reconstruct historical within-SA2 distributions. Allocated income medians are weighted source-area proxies, not necessarily true postal-area medians. Separately, historical filing postcode strings are joined to the fixed lens geography without a displayed postcode-vintage reconciliation. These differences can affect measured local change even when national population totals reconcile.

**Action:** Label Census changes as changes in estimates allocated to fixed geography; retain the unvalidated historical allocation and income-proxy limitations. Check historical postcode correspondence, unmatched filing coverage and source-area sensitivity. Where feasible, analyse at the original comparable geography. Do not treat the Stage 1 national count check as validation of local change. Evidence: `08716ea5`, `b7179e5a`; Stage 1 U118 and Places R18/R28–R29.

### R29 — High | B59: the pseudocount can create apparent filing change where neither period has filings

**Issue:** The response is the difference in logs of `(count + 1) / population`, not the log change in the actual filing rate. For an area with zero filings in both periods, it equals **−log(population2021/population2011)**: population growth alone creates a negative value. The 1,000-resident threshold does not ensure adequate filing counts. `fillna(0)` also converts an unmatched filing row to zero without displaying whether absence is an observed zero or a coverage issue.

**Action:** State the exact smoothed measure, count zero–zero and low-count areas, and test sensitivity to pseudocounts and zero handling. Keep missing/unmatched observations distinct unless their zero meaning is established. Consider count/exposure modelling or a separately labelled positive-count comparison. Do not describe the median **−0.145** as an unqualified fall in actual patent rates. Evidence: `b7179e5a`, `926d52ec`.

### R30 — Medium | B59: the median-change prose implies a single median area

**Issue:** The four reported medians are calculated separately across areas. There need not be one area whose education, income, patent and trade mark changes all equal those medians. The filing windows are FY2007–FY2011 and FY2017–FY2021, while Census characteristics are endpoint snapshots. The income change is explicitly nominal, which is appropriate, but it is not a measure of real local income growth.

**Action:** Say median change across eligible areas separately for each variable. Keep both filing windows and Census dates beside the result, label income as nominal and distinguish the smoothed filing measure. If describing joint trajectories, display the corresponding joint evidence. Evidence: `b7179e5a`, `926d52ec`.

## Evidence, presentation and reconciliation

### R31 — High | B31, B58, B59 and attachment leaders: uncertainty is missing where conclusions are strongest

**Issue:** The introduction promises effect sizes and intervals for every finding. B31 supplies correlations without sample sizes or intervals; B58/B59 show counts but no intervals, and the displayed attachment leaders omit intervals and replication sample sizes. B31 examines 38 industry–outcome pairs, while the additions examine seven and six pairs respectively, without a displayed multiplicity policy. Repeated signs alone are not equivalent to passing the screen's significance and replication criteria. Small estimates do not establish no association.

**Action:** Show pairwise sample sizes and justified uncertainty, with the dependence caveat in R03. State which results are descriptive exploratory comparisons and which meet a declared screening rule; disclose the tested family and any correction. Use uncertainty/equivalence reasoning before no-difference claims and distinguish internal stability from a formal replicated lead. Evidence: `0a9fee61`, `b259f002`, `c3c0b719`, `ecc34934`, `b7179e5a`.

### R32 — Medium | B28 / charts / tables: labels and presentation conceal important distinctions

**Issue:** Several smaller issues obstruct checking the findings:

- B28 omits the top displayed standard-patent correlation, finance/insurance businesses with turnover $200,000 to less than $2 million (**0.595; 0.621**), while introducing selected examples as the most positive. Its professional-services turnover label is truncated in the saved table, so the prose's $2 million-or-more category cannot be verified from that output.
- The PHIDU Parenting Payment row is a percentage with its own eligible population, not simply a count of single mothers. The broader healthier-area interpretation combines selected proxies and is not a general health finding.
- The CER percentage table uses measured eligible pairs. Zero trade mark leads does not show that all 11 inventoried indicators received a usable test; indicator-by-rate eligibility counts are absent.
- The heatmap ends its colour scale at **0.6**, although several values exceed it, and lacks a visible key for hatching, orange crosses and black borders. Its strength-only colours omit direction and combine different association metrics; the common 0–1 range alone does not establish equivalent effect-size meaning.
- Long decile-chart x-axis labels collide, while many screen-table pair names and indicator labels are truncated. Several acronyms and internal Q/U/ADR references require context outside the section.

**Action:** Preserve full identifiers, units, source populations, category boundaries and eligible test counts in a readable supporting table. Use among the strongest selected examples where appropriate. Add a chart key, state any colour saturation and the metric/direction, shorten labels, and define the main terms locally: postal area, SA3, IRSAD/IEO, ABR, CABEE, exposure, rho and rate ratio. Evidence: `1cb83215`, `0a576241`, `b259f002`, `47c98879`, `9ea0a1c6`.

### R33 — High | §3.7 / Places row in §8: summaries preserve overstatement and do not reconcile later additions

**Issue:** The summary repeats the single-dimension claim, the unperformed joint SA3 check, the concentration exclusion, manufacturing's supposed lack of relevance and the business-owner denominator. B29's **1.7–1.9** shorthand applies approximately to the unadjusted standard-patent ratios, not all right types or adjusted estimates. B59's yes column conflates matching signs with the stronger screen criteria. The §8 Places row still covers B27–B31 only, omitting B58/B59 while preserving a broad gradient story and unsupported explanation.

**Action:** Regenerate the Places summaries from corrected observations, identifying each measure, eligible population, model and uncertainty. Explicitly reconcile B29's cross-sectional level associations with B59's weak changes: they answer different questions and are not a demonstrated contradiction. Add the later ATO/Census results and unresolved limitations. Move superseded wording into a dated change note and replace blanket yes/rules with the particular robustness check actually performed. Evidence: `a9f5687a`, Places row in `de334709`.

## Audit trail and limits

The report contains **33 issue/action entries**. Confirmed discrepancies include the incompatible half counts, the absence of a joint/remoteness SA3 fit, patent-only industry patterns generalised to trade marks, and the exact pseudocount transformation. Checks concerning attribution, missing classifications, source mapping and spatial sensitivity remain conditional because their implementations and underlying data were not inspected.

All nine Places code cells have saved outputs, sequential execution counts **36–44**, and no saved error outputs. This establishes a coherent saved execution sequence, not reproducibility against current helpers or data. Both charts were visually inspected. Numerical checks used saved values and direct examination of notebook code; no statistical models were rerun.

**Earlier audit linkage:**

| Earlier report | Findings materially carried into this review |
|---|---|
| `Stage01_L3_Audit.md` | R04/R06–R08/R10/R12–R15/R17–R21/R26–R29/R32: attribution, denominators, missing geography, suppression, model limits, linkage and historical allocation |
| `Stage01_S8-S9_Audit.md` | R03/R15–R18/R21/R24: stale handover, firms, places, source comparability, industry allocation and institutional postcode limits |
| `Stage01_L2_Audit.md` | R48/R51/R61: zero versus unlinked use, party/ABN definitions and dated registered addresses |
| `Stage01_L6_Audit.md` | R03–R04/R10: services-crosswalk update, allocation concentration and applicant-industry mismatch |
| `Stage01_L0-L1_Audit_Completed.md` | R39: country, type, postcode and ABN must refer to a consistently selected party |

These reports were used as leads and context, not as proof of defects in uninspected helpers. The current Stage 1 notebook matches the SHA-256 recorded in those audits. A generic Stage 1 warning was not counted as a new defect unless it affected a Places measure or interpretation here. For example, B59's SQL does not explicitly filter `founding_australian`, but Stage 1 defines `founder_postcode` as an Australian founding-applicant field; omission of the redundant-looking filter alone was therefore not labelled a confirmed foreign-postcode contamination bug.

**Evidence locators:** B-numbers and headings are searchable. Eight-character cell IDs are stable notebook JSON IDs, not execution counts. The reviewed section runs from `1ca091d5` through `a9f5687a`. The external summary document and website remain outside this review.

Repository commit: `1581223dc2fbb2ce1a1c26fab77a14f459eb023a`.

Stage 2 notebook SHA-256: `441679240f0e884486b681493f87604fa327223a9ae369fcdd263fd84218ede2`.

Stage 1 notebook SHA-256: `1d5e51a699b82091788c75fdaff6d2706a24ba6a91df21877799677a8a357cdb`.
