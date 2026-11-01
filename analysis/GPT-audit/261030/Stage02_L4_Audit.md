# Stage 2 notebook audit: Lens 4 reviewed in depth

**Reviewed:** 2 November 2026. **Source:** [02_bivariate.ipynb](https://github.com/Thomas-Amann-IPAustralia/Aus-GII-Breakdown/blob/1581223dc2fbb2ce1a1c26fab77a14f459eb023a/analysis/notebooks/02_bivariate.ipynb), retrieved from `main` for this review.

**Provenance:** Follows `analysis/GPT-audit/261030/Stage01_L0-L1_Audit.md`: prioritised, numbered issue/action entries grouped by subject, followed by review boundaries. R01–R24 are local to this report. Earlier audit references use their lens prefix, for example **L4 R27**.

**Scope of this pass:** Only §4, including §§4.0–4.5 and B32–B35/B61: all 16 cells, comprising five code cells, their saved outputs, 11 Markdown cells and both embedded figures. The Stage 1 audit series was consulted for relevant carry-forward concerns, with detailed checks against its Lens 4 and §§8–9 reports and the cited Stage 1 notebook evidence. Stage 2's introductory rules were consulted. The GitHub Pages website was not checked. No underlying datasets, imported helper implementations or external source publications were audited; the notebook was not re-executed.

**Overall finding:** Most quoted numbers match the saved outputs. The main weaknesses are incompatible measures and comparison populations, over-interpretation of correlations, incomplete supporting displays, and B61's incorrect restatement of B34. The visible calculations remain pairwise; the principal drift beyond bivariate scope occurs in explanations that imply a common underlying factor or a tested third-variable mechanism.

**Priority:** **High** = affects interpretation, validity or downstream use; **Medium** = correct before relying on or circulating the findings. Validation requests do not establish defects in uninspected data or helpers. Apply corrections to the corresponding §4.5 summary row as well as the original observation.

**Read first:** R07, R12–R15, R17–R18 and R21–R23. B34's weak change correlation does not establish an ineffective R&D intervention, and B61 does not replicate B34's model.

## Scope, populations and measurement

### R01 — High | B32 / B35: pairwise results become a single-factor explanation

**Issue:** “One development gradient” and “Nothing about IP is unrelated to development” imply more than the pairwise screen establishes. No common-factor model or adjustment for development is shown. Likewise, “trade marks follow commerce, patents follow research” generalises selected associations into a broad explanatory distinction. These are interpretive steps towards multivariate analysis, not demonstrated multivariate results.

**Action:** Describe the specific positive associations and label a shared development factor as a hypothesis for Stage 3. Retain the heatmap, separate pairwise regressions and period comparisons in Stage 2: multiple displayed variables or separate periods do not themselves constitute a multivariable model. Evidence: `f6a82fbe`, `4e8a6b09`, `6fccbbc5`.

### R02 — High | §§4.0–4.2 / §4.4: the country population changes without consistent labelling

**Issue:** The core restricts countries to a mean population of at least one million, including its OECD rankings and regressions. B33 therefore does not rank Australia against all reporting OECD members. B61 uses the OECD flag without that population restriction and includes up to 38 members. Core membership is derived through `bool_or(oecd)` across records, not an explicit historically dated membership rule. Pairwise missingness further changes the countries used.

**Action:** Label every population and show included/excluded countries, pair-specific counts and the membership convention. Use a common-country sensitivity comparison before comparing rankings, coefficients or periods. Replace the summary's blanket “36 OECD members” with analysis-specific denominators. Evidence: `56ed2b2a`, `6be88b85`, `a2d420b8`, `9702b2e1`, `6fccbbc5`; Stage 1 L4 R08/R10.

### R03 — High | `national_wide`: period means can represent different observed years

**Issue:** Each indicator is averaged over its available non-null years, then scaled using population averaged separately. No minimum number of years or alignment with denominator years is imposed. A single observation can therefore represent a nominal five-year period. Stage 1 explicitly shows sparse research series and high-technology exports starting in 2007, so not all 2006–2010 means cover five years. Ratios of separately averaged values are also not necessarily means of annual ratios.

**Action:** Show observed-year counts and actual spans by country/indicator. Define the intended ratio, align numerator and denominator years, and apply an explicit coverage rule with sensitivity checks. Do not describe all values as comparable full-period averages. Evidence: `56ed2b2a`, `9fae40b0`; Stage 1 `0e50e75d`, `be1b0abc`, L4 R02/R08.

### R04 — Medium | Input preparation: eligibility and uniqueness are not demonstrated

**Issue:** The core query excludes null values but does not expose duplicate-key or status checks. Attachment averaging excludes status text containing “projection”, but does not show treatment of other flags or recording breaks. B61 drops source years/status metadata and selects supplementary rows without an explicit latest-year rule. These are unverified safeguards, not evidence that projections or duplicate observations actually entered the results.

**Action:** Add compact checks for unique usable country–indicator–year observations, finite values, flag treatment and supplement selection. State which safeguards occur upstream and display their outcomes. Preserve observed, estimated, projected and missing distinctions carried from Stage 1. Evidence: `56ed2b2a`, `9fae40b0`, `9702b2e1`; Stage 1 L4 R03/R15/R22.

### R05 — High | B32 / B34: ratios do not automatically remove scale effects

**Issue:** Several pairs share population denominators, such as patents and articles per million people; other pairs combine patents per population with R&D per GDP. Shared denominators and variation in GDP per person can contribute to their associations. The screen does not separate those effects from relationships between the underlying numerators. GDP-adjusted patenting in B61 introduces another denominator specification.

**Action:** Identify shared or linked denominators beside the principal leads. Describe results as associations between the stated rates, without treating normalisation as proof that size is controlled. Carry numerator/denominator and alternative-scaling checks into Stage 3. Evidence: `56ed2b2a`, `a2d420b8`, `9702b2e1`.

### R06 — Medium | B32–B33 displays: source labels conceal transformed units

**Issue:** `nlab` reuses and truncates original indicator names after transformation. The table still labels articles and new businesses as counts and high-technology exports as current-US-dollar totals, although their values have been divided by population. Trade-mark labels retain “by count” despite Stage 1's class-count finding. The advanced-education denominator is truncated, risking the same participation-versus-educational-composition confusion identified in Stage 1.

**Action:** Generate labels from the actual transformations and retain full denominators: per million people, current US dollars per person, application classes, or the exact participation rate. Specify that nominal dollar comparisons are not real growth or total returns on Australian IP. Evidence: `56ed2b2a`, `6be88b85`, `4a741ad9`; Stage 1 L4 R06/R09/R13.

## Core screen and Australia's relative position

### R07 — High | B32: the R&D coverage explanation is false and the coefficient comparison is unmatched

**Issue:** B32 says business R&D is measured “for OECD members only”. Stage 1's coverage table reports the OECD BERD series for **47 countries**, exceeding its 38-member reference panel; the Stage 2 screen imposes no OECD-only filter. B32 also compares trade-mark correlations with commerce and R&D across potentially different reporting subsets. The claimed reason that 0.292 fails correction is not evidenced by displayed pair-specific sample sizes or adjusted p-values.

**Action:** Replace “OECD members only” with the verified source coverage. Display both sample sizes and adjusted p-values, and compare commerce/R&D associations on matched countries before claiming a systematic contrast. Treat low power as a possible explanation, not the demonstrated reason. Evidence: `f6a82fbe`, `56ed2b2a`; Stage 1 `0e50e75d`.

### R08 — Medium | B32 / B35: the saved evidence does not support the promised inspection of every lead

**Issue:** The 134-row IP lead table is truncated because its display limit is 120; most rows and third-factor lists are hidden. The focus table has coefficients and verdicts but no pair-specific sample sizes or intervals. B35 prints only selected extremes, omitting the other leads, replication counts, adjusted p-values and intervals. This falls short of the notebook's promise that findings lead with a size and interval.

**Action:** Save readable, complete lead tables or compact grouped displays with full labels, both sample sizes, signed coefficients, intervals, adjusted p-values and eligibility decisions. Expose the imported screen's relevant decision rules rather than relying on prose alone. Evidence: `56ed2b2a`, `9fae40b0`, introductory cell `0a9fee61`.

### R09 — Medium | §4.0 heatmap: saturation and unexplained symbols obscure the result

**Issue:** The colour scale ends at **0.6**, while displayed correlations reach **0.966**, so markedly different strong associations share the darkest colour. The figure has orange crosses and hatched cells without an on-chart key. Truncated labels omit units and parts of definitions. The colour scale is unsigned strength, so it cannot establish direction by itself.

**Action:** Use the full strength range or explicitly label saturation; explain every symbol and distinguish strength from sign. Wrap meaningful labels and preserve transformed units. Keep numerical coefficients available beside the figure. Evidence: saved figure in `56ed2b2a`.

### R10 — Medium | B33: the headline overstates ranks and overlooks an important contrast

**Issue:** “Top for business entry, trade marks and research articles” can imply first place, but the later ranks are **4th of 35**, **6th of 32** and **4th of 36**. “Near the bottom for … exports” blurs total exports/GDP, high-tech exports/person and high-tech exports/manufactured exports. The last measure is **9th of 36**, improving from 20th, despite high-tech exports/person being 30th.

**Action:** Use “among the higher-ranked reporting countries” with exact measures and denominators. Add the high-tech value/share contrast and its different economic meanings. Describe rank changes alongside Australia's values and the changing comparison sample. Evidence: `6be88b85`, `4a741ad9`; Stage 1 L4 R30 and S8–S9 R20.

### R11 — Medium | B33–B34 / §4.5: historical findings are presented as current

**Issue:** The core analysis ends in 2020, but §4.5 says Australia is near its prediction “now”. Stage 1 already contains later patent, R&D and other observations, and B61 adds more recent supplementary research measures. B33's absent Australian researchers/technicians values in the later window also receive no explanation or forward reference. Historical windows remain legitimate; unqualified currency does not.

**Action:** Replace “now” with “in 2016–2020”. Explain why the historical windows were retained, distinguish unavailable core-series values from later supplements, and link B61 without treating it as an equivalent update. Add a newer comparable window only after checking coverage. Evidence: `6be88b85`, `6fccbbc5`, `06b4368b`; Stage 1 L4 R10/R28.

## Patenting against business R&D

### R12 — High | §4.2 / B34: the outcome is narrower than invention or total resident patenting

**Issue:** “Invention against R&D” uses `IP.PAT.RESD`, resident applications at the home office, rather than the separately available worldwide resident-application series. Office routes and filing practices can affect cross-country comparisons. Even worldwide applications would count application events, not distinct inventions, and the R&D measure is business R&D while resident applications include other applicant types. “23 members' residents filed less” also refers to rates per person, not necessarily lower filing totals.

**Action:** Name the exact office-based outcome and applicant coverage throughout. Test the worldwide series as a clearly distinguished sensitivity measure, without calling it an invention count. Say patent applications **per person** fell in 23 members. Evidence: `ee18f43f`, `a2d420b8`, `c510ff8c`; Stage 1 L4 R09/R18.

### R13 — High | B34: weak change correlation becomes a causal and timing conclusion

**Issue:** A Spearman correlation of **0.165** across 34 countries does not establish that R&D and patenting “do not move together”, or that “raising R&D would not … raise patenting quickly”. The code compares two period averages, not intervention effects or response lags. It also correlates a patent **log change** with an **absolute percentage-point** R&D change, unlike the level model's log–log specification. No interval for the change correlation is displayed.

**Action:** Report a weak observed association under this specific change definition, with uncertainty. Remove the intervention/timing conclusion. Show a change scatterplot and assess matched change scales; defer causal and lag claims to a suitable design. Translate Australia's −0.083 log10 change to approximately **17.4% lower applications per person**. Evidence: `a2d420b8`, `c510ff8c`.

### R14 — High | B34: the explanation for Australia's changed relative position is incomplete

**Issue:** “Its change in position came from falling R&D” ignores changes in the fitted line and comparison sample. The regressions use **34 versus 36** countries and are fitted separately. Using the displayed earlier prediction, slope and R&D values, holding the earlier relationship fixed would predict approximately **160** patents per million at the later R&D share, not the later model's **98.46**. Falling R&D alone therefore does not reproduce the reported prediction change.

**Action:** Describe the observed moves without assigning the whole relative-position change to R&D. If explaining it, use a common country panel and separate movement along a fixed line from changes in intercept/slope and composition. The approximate calculation uses rounded saved values and is a diagnostic, not a model rerun. Evidence: `6be88b85`, `a2d420b8`, `c510ff8c`.

### R15 — High | B34: fitted benchmarks and prediction intervals need narrower interpretation

**Issue:** Australia contributes to the fitted line used to assess itself. Exponentiating the fitted log mean gives a geometric-mean-type benchmark, not an arithmetic expected patent count without retransformation assumptions. The **17–580** and **41–1,262** prediction intervals are model-based intervals for an observation, not observed member ranges or confidence intervals for Australia's gap. Slope uncertainty, residual diagnostics and influence sensitivity are absent; the plotted countries visibly depart substantially from the line.

**Action:** Label the benchmark and intervals precisely, show slope uncertainty and model checks, and use an Australia-excluded fit for a peer prediction. Plot the prediction bands. Retain the valid fitted interpretation that doubling the R&D share corresponds to roughly **2.22×/2.15×** the patent rate; avoid claiming a precise law or proven underperformance. Evidence: `a2d420b8`, `c510ff8c`.

## Attachment screen

### R16 — Medium | §4.3 / B35: “every cross-country indicator” overstates coverage

**Issue:** The query selects only four OECD datasets plus GII values. Stage 1's inventory also includes cross-country well-being, poverty, hunger, climate and other datasets outside that whitelist. Some exclusions may be justified, but no complete eligibility register is shown. The **485** total is indicators retained with a valid discovery correlation and at least 15 observations, not every ingested indicator or necessarily every attempted test.

**Action:** Rename this a screen of selected eligible attachments. Show counts from available to attempted to retained indicators, with reasons for dataset exclusions, insufficient coverage, constant values and missing replication. Reconcile later additions or explicitly mark their scope elsewhere. Evidence: `c0ecdc77`, `9fae40b0`; Stage 1 `7e0751c8`, L4 R14/R29, S8–S9 R01.

### R17 — High | B35: attachment totals are not scaled as the section's rule requires

**Issue:** OECD attachment values are averaged and correlated directly with patents **per million people**. Unlike `national_wide`, this query applies no population or GDP normalisation. Displayed leads include total business R&D in PPP dollars and total venture-capital investment in US dollars. Their associations mix expenditure scale with patenting intensity, despite §4's rule that cross-country counts become ratios. Dollar and GDP-share versions are then discussed together.

**Action:** Classify each attachment's units and normalise appropriate totals using aligned denominators, preserving already normalised measures. Rerun the affected screen and report sensitivity to scale choice. Until then, label these as total-expenditure versus patent-rate associations. Evidence: `839057c7`, `9fae40b0`, `4e8a6b09`.

### R18 — High | GII part of B35: edition date and outcome period are mismatched

**Issue:** GII 2026 values, whose underlying observation years vary, are paired with patent rates averaged over **2016–2020**. The query discards those years. Splitting economies by hash checks whether an association recurs across two country groups; it does not resolve timing mismatch or demonstrate stability over time. Some proposed explanatory measurements may postdate the patent outcome.

**Action:** Display underlying indicator years and align them with a justified patent period or lag. Otherwise label the results as mixed-date cross-country associations. Preserve the existing warning that the GII split is a weaker test, and identify its country counts and membership. Evidence: `c0ecdc77`, `9fae40b0`, `4e8a6b09`; Stage 1 L4 R27.

### R19 — Medium | B35: exclusion and lead-count rules are inconsistent with the narrative

**Issue:** Eight patent-labelled indicators are described as “not screened”, but their correlations and p-values enter discovery correction and potentially the replication correction before exclusion. A substring search for `atent` also treats all such measures as equivalent without inspecting their definitions. The **225** retained indicator-level results are not deduplicated like B32's distinct leads; examples include total/sex-specific life expectancy and multiple unit versions of R&D or venture capital.

**Action:** Define exclusions and measurement families explicitly before correction, or accurately state that tests were computed but excluded from the final lead count. Report raw tests and distinct substantive leads separately, with the correction family documented. Do not imply 225 independent findings. Evidence: `9fae40b0`, `4e8a6b09`.

### R20 — High | B35: the explanation for the negative women's-share association is untested

**Issue:** The displayed negative correlations concern women's share of researchers and higher education's share of researchers. B35 then asserts that business research employs fewer women and calls the result a third-factor pattern. The displayed analysis does not test that proposed chain or establish that sector composition explains the women's-share association. Country-level relationships cannot identify individual researchers' patenting behaviour.

**Action:** Retain the negative country-level associations with their populations. Present sector composition as one hypothesis requiring direct measurement and adjustment in Stage 3. Remove the asserted mechanism and preserve the warning against a gender-effect interpretation. Evidence: `4e8a6b09`, `9fae40b0`.

## Supplementary comparison and reconciliation

### R21 — High | B61: Stage 1's supplement limitations disappear from precise rankings

**Issue:** B61 reports exact Australian ranks but omits the supplementary values, survey periods and caveats. Stage 1 identifies mixed sector years, researcher person-years and the exclusion of joint business–government funds. The query also discards peer years. “GERD financed by business” lacks its denominator: GII 5.1.5 is the **business-financed share of GERD**, unlike B34's business-performed R&D **as a share of GDP**.

**Action:** Restore values, full definitions, actual periods and comparability caveats beside each result. Label computed placements as indicative, author-calculated peer ranks, not published GII ranks. Preserve the distinction between financing, performance and denominators. Replace `int(average_rank)` with an explicit tie convention if ranks are retained. Evidence: `9702b2e1`, `06b4368b`; Stage 1 `35e0960f`, `ef086a65`, L4 R27–R28.

### R22 — High | B61 → B34: the later finding contradicts and does not replicate the earlier one

**Issue:** B61 says “B34's gap (Australia patents less than its business R&D suggests) holds”. B34 actually reports **104.9% of its fitted value in 2016–2020**, with the earlier 55.22% estimate inside a very wide prediction interval. B61 changes the R&D concept, patent denominator, dates and country set. Being **17th on financing and 28th on patenting** is a difference in marginal ranks, not a measured shortfall conditional on financing; no expected rank or residual is fitted.

**Action:** Remove the claimed confirmation. State separately what each analysis measures, and describe B61's rank contrast without calling it a replicated gap. Establish a comparable conditional benchmark and uncertainty before claiming under-patenting. Keep the low business-researcher share as a candidate explanation only. Evidence: `c510ff8c`, `06b4368b`, `6fccbbc5`.

### R23 — Medium | B61 / §4.5: an interval is not replication

**Issue:** B61 estimates three correlations on **36 or 37 peers excluding Australia** and supplies bootstrap strength intervals. It does not use a second period or held-out country group. Yet its summary places “interval” under “Holds in the other period?”, which obscures that replication was not conducted. Australia's ranks then include Australia and use denominators of 37 or 38, a separate population.

**Action:** Mark replication “not tested; single mixed-date comparison”. Explain signed rho versus unsigned strength intervals and distinguish the correlation sample from the ranking sample. Treat this as a supplementary exploratory result, not a lead that has met the notebook's full replication rule. Evidence: `9702b2e1`, `06b4368b`, `6fccbbc5`.

### R24 — Medium | §4.5: the summary strengthens claims and does not resolve the later addition

**Issue:** The summary retains “one development gradient”, “manufacturing last” and “Australia near its prediction now” without their population, measure or period restrictions. It labels candidate third factors as those “named most often”, including research history, without a displayed frequency tally or measured research-history variable. B61's contradictory interpretation of B34 remains unreconciled.

**Action:** Regenerate the summary from corrected B32–B35/B61 observations, carrying forward dates, exact units, eligible populations and replication status. Separate measured candidate covariates from proposed explanations and remove unsupported frequency wording. Explicitly cross-reference B34 and B61 as different analyses. Evidence: `6fccbbc5`; compare Stage 1 S8–S9 R19–R20 on preserving national-summary qualifications.

## Review boundary and reproducibility

This report contains **24 issue/action entries**. All five Lens 4 code cells have saved outputs, sequential execution counts **45–49**, and no saved error outputs. Both figures were visually inspected. Numerical checks used those outputs and simple arithmetic; no data rebuild, model fitting or notebook execution was performed. Saved outputs establish what was displayed, not reproducibility against current helpers or data.

The review distinguishes demonstrated contradictions and code/display mismatches from checks needed before stronger conclusions. It does not certify imported screen routines, source metadata, OECD membership history or GII construction. No notebook or repository files were changed.

**Earlier audit references:** Reports in `analysis/GPT-audit/261030/`, especially `Stage01_L4_Audit.md` and `Stage01_S8-S9_Audit.md`. Their relevant concerns were checked against the current notebooks rather than assumed to remain applicable. Stage 1's notebook SHA-256 remains `1d5e51a699b82091788c75fdaff6d2706a24ba6a91df21877799677a8a357cdb`, matching the audited version. Right-holder attribution and family-coverage issues were not mechanically transferred to these separately sourced national-series calculations.

**Evidence locators:** B/U-numbers and section headings are searchable. Cell identifiers are stable notebook JSON `id` values, not execution counts. Unqualified cell IDs refer to Stage 2; Stage 1 IDs are explicitly identified.

Repository commit: `1581223dc2fbb2ce1a1c26fab77a14f459eb023a`.

Reviewed Stage 2 notebook SHA-256: `441679240f0e884486b681493f87604fa327223a9ae369fcdd263fd84218ede2`.
