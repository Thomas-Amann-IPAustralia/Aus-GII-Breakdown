# Stage 1 notebook audit: Lens 3 reviewed in depth

**Reviewed:** 31 October 2026. **Source:** [01_univariate.ipynb](https://github.com/Thomas-Amann-IPAustralia/Aus-GII-Breakdown/blob/main/analysis/notebooks/01_univariate.ipynb), downloaded from `main` on the review date.

**Format:** Follows `analysis/GPT-audit/261030/Stage01_L0-L1_Audit.md`: numbered findings, priority, issue and action. R01–R32 are local to this Lens 3 report.

**Scope of this pass:** Only §3, including its overview, §§3.1–3.7 and §3.8 summary: all 45 cells, including 24 code cells, their saved outputs and all nine embedded charts. The notebook's introductory rules and relevant observations elsewhere were consulted only to trace qualifications, amendments and repetitions of Places claims. No GitHub Pages website, underlying datasets, imported helper implementations, ADRs or other analytical repository files were assessed. The supplied audit was read for format. The notebook was not re-executed.

**Overall finding:** Most quoted figures match the saved outputs. The principal weaknesses are relationship analysis labelled univariate, unqualified claims about missing filing histories, overconfident geographic allocation and funnel interpretations, and confusion between area summaries and statistics about people or distinct firms. Later additions are not consistently reflected in earlier descriptions.

**Priority:** **High** = affects interpretation, validity or downstream use; **Medium** = correct before relying on or circulating the findings. Implementation-dependent concerns are explicitly framed as checks. Apply corrections to the corresponding §3.8 row and any repetition of the Places finding in §9.

**Read first:** R07, R12–R15, R18–R19, R25 and R28–R30 concern denominators, validity or consequential interpretation. An observation can be descriptive while still being bivariate.

## Scope, freshness and definitions

### R01 — High | Throughout: substantive comparisons exceed the stated univariate scope

**Issue:** Remoteness × population/business counts (U51), IP concentration against population (U52), rates against population and a common-rate model (U53), filing status × remoteness (U54), and procurement shares against business shares (U62) examine relationships. U56 explicitly calculates Spearman correlations. National time/technology, size and income summaries also change the unit from one postal area. These exceed the introduction's promise to examine variables separately before testing relationships.

**Action:** Retain marginal distributions and clearly labelled data-quality checks. Move substantive comparisons and model-based inference to Stage 2, or explicitly broaden Stage 1 to allow specified descriptive comparisons. Separate source-agreement checks from evidence about economic relationships; two chart axes alone do not make a frequency plot bivariate.

### R02 — Medium | §3 introduction / §3.5 / U55: the attachment inventory has not caught up

**Issue:** The overview describes five sources and U55 calls 22,511,923 rows the attachments' total. Its query deliberately excludes the subsequently added ATO and Census time-series sources, while the accompanying chart includes all seven. The notebook introduction gives 28,960,234 companion rows. These are different scopes, not a demonstrated contradiction in the underlying data. The overview's “every value they publish” also exceeds the selected tables and successfully matched areas shown.

**Action:** Give one current seven-source inventory and label the five-source subtotal explicitly. Reconcile the total to the introductory inventory; align the chart, table and source caption. Say “the ingested indicators mapped to this lens”, and update §9's Places-summary pointer from §3.6 to §3.8.

### R03 — High | §3 introduction / U49: unmatched postcodes are over-classified

**Issue:** The introduction says postcodes with no residents are not postal areas, but U50 finds two postal areas with no residents. The postcode check infers “real codes with no residents” from a delivery-range code appearing in the ABR but not the lens. That establishes neither current validity nor absence of residents; boundary vintage or address errors remain possible. “Held by no one” is stronger than absence from this ABR extract.

**Action:** Describe ABS postal areas and unmatched postal codes separately. Label the categories by the actual tests: “delivery-range code present in ABR, unmatched to a lens postal area”, etc. Reserve validity, occupancy and university/GPO classifications for independently supported matches; do not treat non-matching as proof of no population.

### R04 — High | U48–U49: postcode and applicant-type percentages need their eligible populations

**Issue:** U49's 94.45% is 25,180 of **26,661 standard applications with a founder postcode**, not all standard patents. U48's individual shares also require a founder postcode, and SQL `avg` silently excludes unknown founder types. Its headline “one right in fifteen” is not a displayed pooled estimate and omits provisionals' much lower 1.77% postcode difference. The queries rely on imported founder-field definitions to identify an Australian party.

**Action:** State the filing window, selected founder, known-postcode/type denominators and exclusions. Display missing-postcode and unknown-type counts. Use type-specific difference percentages or calculate a pooled result. Confirm postcode, type and ABN describe the same selected Australian founder before interpreting their combination.

### R05 — Medium | U48 / overview: filled cells are not complete capture

**Issue:** “Every count is complete” means 100% non-null, although U49 immediately identifies omitted applications. The attribution of all 34 missing rent medians to “no renters” is not demonstrated. `austender_value` is only 76.3% filled, whereas contract counts are complete; the notebook does not show whether every missing value means no contracts rather than an unknown amount.

**Action:** Say “all count fields are populated”. Separate observed zero, geographic non-match, unavailable value and deliberate rate suppression. Show the joint contract-count/value missingness check and evidence for the rent explanation, or label its cause unverified. Do not replace unknown money values with zero without establishing their meaning.

### R06 — Medium | U49 → U87: a later quantification has not replaced the earlier provisional account

**Issue:** U49 says the institutions lens “will count” university applications and leaves a postcode lookup pending. Later §7.6/U87 reports 742 of 1,474 university-linked standard applications at unmatched delivery-range postcodes (50.34%), with nine more in the other unmatched category, and proposes institution-based placement. U49's “mostly missing” remains less precise; its summary says six universities while its prose lists seven university-associated codes.

**Action:** Replace the prospective wording with a cross-reference to the later recorded result, preserving its population and linkage limitations. Distinguish shares of applications from shares of codes, and update the pending action and six/seven discrepancy. Do not imply that institution-based remapping has already occurred.

## Core places profile and IP rates

### R07 — High | §§3.1–3.4 / U48, U50, U53–U54: rates mix dates and non-equivalent populations

**Issue:** Ten years of applications are divided by a fixed 2021 population or 2026 active GST-registered ABNs. Organisation applications need not come from those currently active, GST-registered entities. The claim that the business denominator “holds no individuals” is not established by an ABN/GST filter. R&D counts concern claimants observed in a limited reporting window, not necessarily firms claiming at the snapshot. These rates are not filing probabilities or matched-cohort incidence.

**Action:** Label them ten-year average application intensities against a dated denominator. State the R&D reporting years and meaning of “active”. Show denominator eligibility, geographic matching and zero-denominator treatment; do not equate organisation status with GST eligibility. Use aligned annual exposures or sensitivity checks before interpreting differences as behaviour.

### R08 — Medium | U51 / §3.2: whole-area classifications are described as exact locations

**Issue:** The remoteness table assigns every person and business to the postal area's single `remoteness` category, although `share_major_cities` has 138 distinct values. Thus “72.8% of people … inside” cities is a total for areas classified as major-city areas, not demonstrated point-level location. The same issue affects businesses and claimant comparisons.

**Action:** Say “in postal areas classified as …” and state the assignment rule. For actual city-population shares, use the available fractional population measure where appropriate. Do not allocate businesses using resident fractions without labelling that approximation. Explain state assignment for any postal areas crossing boundaries.

### R09 — Medium | U51 / SEIFA and Census summaries: the statistical unit needs clearer wording

**Issue:** The chart calls 1,000 “the average Australian area”, but the displayed postal-area means are 983.8, 995.0, 999.6 and 982.6; the standardisation population is not supplied. The four indexes are also compressed into one notion of “most disadvantaged”. Personal income $754 and age 43 are medians **of area medians**, not national medians of people. Long SEIFA panel titles visibly overlap.

**Action:** Explain the documented reference scale without claiming the displayed areas average 1,000. Describe each index's direction and construct separately. Label all summaries as unweighted distributions across eligible postal areas, with missing areas excluded, and shorten or wrap panel titles.

### R10 — High | U52: selected high-volume areas do not establish how often one filer dominates

**Issue:** The one-filer table covers only the ten areas with the most standard applications. Three show a single identified ABN above 50%; it does not establish that an area's patents are “often one firm's” across 2,641 areas. In several city centres, missing founder ABNs exceed the largest identified filer's share, so that ABN is not necessarily the largest actual filer.

**Action:** Restrict the statement to the displayed examples and say “largest identified ABN”. If a general prevalence claim is needed, summarise the dominant-filer share across all patent-filing areas, with identification coverage. Describe counts as applications attributed to a selected founder, not necessarily distinct inventions or economic activity occurring there.

### R11 — Medium | §3.3 concentration chart: its curves do not rank the same places

**Issue:** Each application series and the population series are independently sorted. The dashed population curve therefore does not show the population living in the areas ranked highest for patents or trade marks. The adjacent table correctly uses the latter calculation, but the chart's “most first” label does not explain the distinction.

**Action:** State “each series ranked separately” and use the plot only to compare marginal concentration. To illustrate U52's 72.5% versus 29.2%, add a population curve using the same patent-ranked areas, or rely on the existing clearly labelled table.

### R12 — High | U53 / funnel plots: a particular null model is presented as chance itself

**Issue:** “Far more than chance”, “not small-area noise” and the prescribed negative-binomial model exceed a descriptive result. A common-rate Poisson benchmark assumes a particular count process; repeat filings, firm concentration, denominator mismatch and geographic allocation can violate it. Exactly 2.5% in each tail is not guaranteed for discrete counts. The imported `uni.funnel` implementation is not shown, so the notebook does not establish whether its limits are predictive count limits or confidence intervals for a rate.

**Action:** Describe departures from the specified benchmark. Expose or document the limit calculation and verify low-count/zero handling before interpreting the outlier percentages. Do not substitute confidence limits around an expected count for count prediction limits. Treat overdispersion and candidate models as Stage 2 questions, not settled findings or proof that noise is excluded.

### R13 — High | U53 / rate suppression: presentation and interpretation mix different subsets

**Issue:** The repair says rates below ten expected applications are empty, but the funnels plot raw counts against population, including points left of the threshold. U53's maximum of 61.8 standard applications per 10,000 people is the highest **retained** rate; the patent funnel visibly contains much larger raw rates. Its medians also exclude suppressed areas. An expected-count threshold alone does not prove a rate “means something” or that smaller rates are “mostly chance”.

**Action:** Label diagnostic raw rates separately from publication-eligible rates. Qualify every median and maximum by the retained subset and report excluded areas and population. Identify zeros placed at a plotting floor. Present ten expected applications as a reporting rule, with sensitivity, rather than a universal validity boundary; business-address concentrations can distort per-resident rates even above it.

### R14 — High | U53 / pooled SA3 analysis: whole-postcode pooling is an approximation

**Issue:** Cell `d942b235` allocates each postal area's entire population and filing count to the SA3 containing most of its people. These are postal-area pools labelled by SA3, not demonstrated counts inside actual SA3 boundaries. Pooling does not recover unmatched university postcodes or resolve business-address/resident mismatches. Its “national” benchmark also covers matched areas rather than all Australian filings.

**Action:** Label the pooled geography and benchmark population explicitly. Quantify cross-boundary allocation and unmatched applications before using the result geographically. Use a suitable crosswalk or point-level allocation if true SA3 estimates are required; do not infer from persistence after pooling that small-area or allocation effects are absent.

### R15 — High | U54: “never filed IP” is not established by an absent linked filing

**Issue:** The 8,939 of 17,627 claimants without counted filings are described as having “never filed IP”. U41 already acknowledges incomplete ABN linkage and historical IP-only links. A lower bound on recorded use implies potentially overstated non-use, not a lower bound on non-use. Later register-filled ABNs are documented elsewhere, but §3 does not show whether its prebuilt claimant and filer counts incorporate them.

**Action:** Say “no filing linked under the lens's ABN and applicant rules”. Verify propagation of register-filled ABNs and reconcile any historical IP evidence before treating firms as non-filers. State that acquired rights and other forms of IP are outside this filing measure; preserve the active, geographically matched claimant denominator in headlines and summaries.

### R16 — Medium | U54: the remoteness conclusion omits a visible exception

**Issue:** “Claimants outside the cities have more often never filed IP” overlooks very remote areas: 36.4% (4 of 11), below cities' 50.4%. Inner regional, outer regional and remote areas have 51.4%, 59.6% and 58.7%. The claimants-per-business gradient is a different statistic and does decline across the displayed remoteness categories.

**Action:** Separate the two findings. Give the exception and small denominator, or calculate and explicitly label a pooled non-city comparison. Retain “no linked filing” rather than “never filed” throughout.

## Attachments and geographic allocation

### R17 — High | U55 / attachment coverage: row presence is mistaken for a usable value

**Issue:** “Median areas with a value” and the coverage histogram use `count(*)`, including null-valued rows. “% empty” excludes absent rows altogether. A high median does not establish nearly every indicator reaches nearly every area: CER has 285,382 rows across 164 indicator-periods, averaging about **1,740 areas (65.9%)**, despite a median of 2,559. The histogram also shows low-coverage indicators in other sources.

**Action:** Count distinct areas with non-null values separately from row presence. Show minimum/lower-quantile coverage, absent and null values, and applicable indicator-period universes. Distinguish sparse reporting from measured zero. Replace “nearly every one” with the coverage actually demonstrated; explain missingness causes only where supported.

### R18 — High | §3.5 / U56, U60: transferred levels are estimates, not observed postal-area statistics

**Issue:** Population-weighted averages of source-area medians, percentages and standardised ratios are not generally the corresponding statistics for a target postal area. Counts allocated by resident shares also assume the measured population or activity follows residents. Calling these the values for postal areas obscures substantial assumptions, particularly for businesses and health measures with different eligible populations.

**Action:** Label outputs as allocated estimates or weighted source-area proxies. Use appropriate numerators and denominators for aggregable rates; do not average medians into a target median or imply that averaged standardised ratios retain their original interpretation. Retain geography, method, period and eligibility metadata; leave unsupported target measures unavailable.

### R19 — High | U56: aggregate agreement does not validate the allocation method

**Issue:** Close population totals and rank correlation do not establish that the residents-weighted split is “sound”. Shared population weights can produce agreement partly by construction, while national totals can be conserved despite local misallocation. The attribution of the 4,317-person Census difference solely to perturbation and the ERP difference solely to missed Census residents is not demonstrated by the displayed comparison.

**Action:** Describe agreement and residuals without claiming validation or a proven cause. Explain shared inputs; show area-level errors, especially tails and small areas. Validate against independent direct geography where available, and state which measures remain unvalidated. Keep source-definition explanations distinct from empirical findings.

### R20 — High | U56: CABEE is not established as a breakdown of the ABR total

**Issue:** After acknowledging different business universes, U56 calls CABEE “its split by size and industry”, implying a decomposition of ABR registrations. The comparison also mixes June 2025 CABEE with 2026 ABR. The median ratio 0.749 and 2.96% within 10% concern only areas with at least **1,000 ABR GST registrations**. Employment and turnover totals are close, not identical: 2,713,177 versus 2,714,218, a difference of 1,041.

**Action:** Keep CABEE distributions and ABR counts as separate measures unless a reconciliation supports combination. State dates and the selected-area denominator. Replace “same total” with the measured small difference. Replace “never compared” with “not treated as interchangeable”, since this section explicitly compares them.

### R21 — Medium | U57 / U59: national smallness does not guarantee local reliability

**Issue:** The 0.05% of CABEE businesses in zero-resident SA2s establishes a small national contribution, not that the mesh-block fallback “matters little” for affected places. Similarly, aggregating perturbed Census cells into shares does not by itself ensure reliable estimates when the resulting numerator or denominator is small.

**Action:** Qualify the fallback statement as national and report its maximum/local contribution. Apply minimum group sizes and uncertainty rules to Census shares. Check totals with a justified tolerance rather than abandoning reconciliation, and retain perturbation-related discrepancies instead of forcing exact equality.

### R22 — Medium | U60 / U55: the PHIDU percentage uses the wrong stated unit

**Issue:** The 54.14% “of its indicators” is the complement of an average over **indicator-periods** in cell `acae54e37e7d407bbb7b55eff062a284`. The topic table instead shows 1,297 non-additive indicators out of 2,368, or approximately **54.77%**. The same weighting distinction affects Data by Region's 57.43% counts. PHIDU's free-text periods also cannot be read chronologically from lexical `min`/`max` alone.

**Action:** Label percentages by their actual denominator, or recompute distinct-indicator shares after checking uniqueness. Explain SR, percentage and other level units separately. Parse period boundaries or display the period labels without claiming lexical first/last values are earliest/latest.

### R23 — High | U61: changes in recorded technologies do not establish a transition to batteries

**Issue:** “Moved from … to batteries” implies substitution or a sustained technology transition. The evidence combines long-running series with batteries recorded only from July 2025 and a partial 2026. In full-year 2025, solar PV remains higher: 272,395 versus 207,305 battery installations. The annual table alone does not demonstrate the July/September recording boundaries stated in the prose.

**Action:** Describe each series' recorded counts and recording window separately. Treat missing pre-coverage battery observations as unavailable, not established zeros. Show metadata supporting partial-year boundaries; do not infer substitution or compare unmatched periods as equivalent annual totals.

### R24 — Medium | §3.5 energy chart: the battery result is invisible

**Issue:** The chart excludes 2026 and draws lines without markers. Batteries therefore have only one retained non-null point, in 2025, and no visible segment, despite appearing in the legend and dominating the headline. The table's `fillna(0)` further hides the difference between no observation and a recorded zero.

**Action:** Add markers or bars for single-year observations and explicitly label partial recording periods. Preserve missing values in the table. Keep the explanatory observation aligned with what the figure actually displays.

### R25 — High | U62: summed supplier counts are not distinct suppliers

**Issue:** The table explicitly labels 54,798 as distinct ABNs **within each area**, noting one can occur in several areas. U62 drops that qualification and calls them 54,798 suppliers. Its 2,015-area statement applies to contracts/value; identified suppliers occur in 1,961 areas. “Above all the ACT” is also ambiguous: NSW leads absolute contract/value shares at 32.6%/26.4%, versus ACT 27.0%/20.5%.

**Action:** Say “54,798 supplier–area occurrences” or calculate a national distinct-ABN total. Separate the area coverages. Describe the ACT as disproportionate to its 1.3% share of GST registrations, not the largest absolute recipient. Keep contract-address and lifetime nominal-value qualifications; “often head office” requires evidence beyond an address field.

## Later additions and completeness

### R26 — Medium | U117: tax-return statistics are described as population statistics

**Issue:** The rising business-income share is among recorded individual tax lodgers, not all people. The 99.98% coverage is the share of **2021 Census residents living in areas with any 2023–24 ATO row**, not coverage of taxpayers or every indicator. The code counts indicator/unit combinations, whereas “138 to 160 items (each a count and an amount)” can imply twice as many measures. Suppression is asserted as the cause of omitted areas without a displayed check.

**Action:** State the tax-lodger denominator, dated geographic coverage and indicator/unit counting convention. Describe taxable-income totals as sums over matched postal areas. Report item-specific non-null coverage and distinguish suppression from unmatched or absent records before attributing omissions.

### R27 — High | U117 decision: the proposed denominator for individuals' filings is not established

**Issue:** The decision to use individuals with business income as the denominator for individuals' own filing is not justified by these marginal totals. Individual filers need not report business income, and the available tax years end in 2023–24 while core filing counts cover FY2017–FY2026. A ratio of these groups is not a filing rate among business-income recipients.

**Action:** Define the intended population and align years, geography and eligibility before adopting this denominator. Without person-level membership or a defensible matching assumption, label it an aggregate contextual ratio and test alternatives in Stage 2. Do not present denominator selection as an established descriptive finding.

### R28 — High | U118: an average of area medians is labelled a national median

**Issue:** Cell `9a77936f` computes `sum(i.value * p.value) / sum(p.value)` and names it `median_personal_income_weekly`. This is a population-weighted mean of allocated area income medians, not the median income of Australians. The parenthetical explanation does not make the headline statistic a median. Total-person weights also differ from the income measure's eligible population, and a missing income value would leave its weight in the SQL denominator.

**Action:** Relabel $609.4, $692.6 and $840.5 as the defined proxy, or obtain a genuine national median. Align weights and exclude missing-value weights consistently. Preserve the nominal-dollar qualification; do not read changes as real income growth.

### R29 — High | U118: national count agreement does not validate historical postal-area change

**Issue:** Historical SA2 counts are distributed using **2021 residents**. This does not reconstruct where people lived within each SA2 in 2011 or 2016. A national 2021 difference of only 66 people verifies an aggregate reconciliation, not local allocation accuracy. “Reaches every postal area” measures row presence, not historical direct observations or complete usable values.

**Action:** Describe the time series as estimates on fixed 2021 geography using fixed allocation weights. Validate 2021 at area level where direct values exist and disclose the untested historical within-SA2 allocation. Qualify local change analysis accordingly, or keep it at the source geography; report usable coverage separately.

### R30 — Medium | Overview / checked-off profiles: important marginal distributions remain unexplored

**Issue:** Despite the “every column” claim, `active_abns` and `share_major_cities` receive only an overview; organisation-only filing counts lack substantive distribution summaries. Several claimed source profiles describe coverage or national totals rather than their distributions across postal areas. Visible but under-discussed features include 1,334 areas with no designs (50.5%), provisional applications' lower top-decile concentration (63.6% versus 72.5% for standard patents), and non-null contract-value coverage of only 76.3%.

**Action:** Add compact summaries of analytically important unprofiled columns: missing/zero shares, median, upper quantiles and extreme-area checks. Separate observations about the postal-area distribution from national aggregates. Mark remaining work explicitly rather than claiming every attached indicator has been explored; do not add bivariate analysis merely to fill the gap.

### R31 — Medium | U50 / U53 / figures: small wording and presentation errors accumulate

**Issue:** U50's “a third” is 818/2,641, or **31.0%**. “Per-person rates … meaningless” is categorical: the displayed ratios show a business-address/resident mismatch, not absence of any descriptive meaning. The population/business histograms omit zeros without stating this in their captions. The Places completeness chart credits no AusTender source despite including procurement columns.

**Action:** Use “31%” or “about three in ten”. Say per-resident ratios are unsuitable as measures of residents' filing propensity in such areas. Label positive-only histograms and excluded zero counts; complete source captions. Explain FY, POA, SA3, SEIFA and SR locally, and replace unsupported certainty with the measured qualification.

### R32 — Medium | §3.8 / §9: summaries lose qualifications and preserve outdated decisions

**Issue:** Summaries repeat “never filed”, “far more than chance”, universal attachment coverage and the technology-transition headline. §3.8's U56 omits the 1,000-person eligibility threshold behind its ERP agreement statistic; U49 retains the earlier lookup action after U87. U53's summary range also mixes postal-area and pooled-SA3 results without naming them.

**Action:** Regenerate the summaries from corrected observations, preserving population, period, geography, coverage and model qualifications. Maintain one current finding and decision; move superseded wording to a dated change note. Keep external explanations or unshown checks labelled as assumptions or validation tasks rather than notebook-established facts.

## Review boundary and reproducibility

These findings establish inconsistencies in the notebook and identify checks needed before stronger claims are used. They do not establish whether imported builders, geographic concordances or statistical helpers are implemented correctly. Recommendations to check those components are follow-up actions, not claims that they were inspected. Later notebook statements were consulted for reconciliation, not independently certified.

All 24 Places code cells have saved outputs, sequential execution counts 91–114 and no saved error outputs. This does not establish that current data or imported code would reproduce them. No notebook or repository changes were made.

**Evidence locators:** Section headings and U-numbers are searchable in the notebook. Code identifiers quoted above are stable JSON `id` values, not execution counts. The reviewed Places cells run from `7b85ddd0` (§3 introduction) through `0b44b918` (§3.8 summary). There are **32 issue/action entries**.

Downloaded notebook SHA-256: `1d5e51a699b82091788c75fdaff6d2706a24ba6a91df21877799677a8a357cdb`.
