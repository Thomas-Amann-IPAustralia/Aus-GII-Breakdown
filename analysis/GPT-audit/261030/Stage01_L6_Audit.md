# Stage 1 notebook audit: Lens 6 reviewed in depth

**Reviewed:** 31 October 2026. **Source:** [01\_univariate.ipynb](https://github.com/Thomas-Amann-IPAustralia/Aus-GII-Breakdown/blob/main/analysis/notebooks/01_univariate.ipynb), downloaded from `main` on the review date.

**Format:** Follows `analysis/GPT-audit/261030/Stage01_L0-L1_Audit.md`: prioritised, numbered findings with an explicit **Issue** and **Action**. R01–R20 are local to this Lens 6 report.

**Scope of this pass:** Only §6, including its overview, repairs, §§6.1–6.6 and §6.7 summary. Reviewed all 23 cells: 10 code cells, their saved text/HTML outputs, four embedded figures containing seven panels, and all nine observations (U73–U79, U114 and U119). The notebook’s introductory rules were consulted. The supplied first audit was read only to reproduce its format. No other repository files, underlying datasets, external factual sources or GitHub Pages website were assessed. The notebook was not re-executed; imported helpers and referenced ADRs or Stage 2 analyses were not independently verified.

**Overall finding:** Most quoted figures match the saved tables. The principal weaknesses are crosswalk concentration presented as certainty, substantive comparisons labelled univariate, incomplete denominator qualifications, and earlier claims left unchanged after additional data and crosswalks were added. Several narrower prose, scope and chart discrepancies are directly demonstrable.

**Priority:** **High** = affects interpretation, validity or downstream use; **Medium** = correct before relying on or circulating the findings. Validation requests are distinguished from proven errors. Apply each correction to the corresponding §6.7 summary row as well as the original observation.

**Read first:** R02–R06, R10 and R16–R17 address coverage, interpretation and comparability. R03 and R15 identify updates that have not been carried back. Descriptive analysis can still be bivariate; concentrated model weights are not evidence of classification accuracy.

## Scope, freshness and definitions

### R01 — High | Throughout: comparisons exceed the stated univariate scope

**Issue:** The entry-versus-exit scatterplot explicitly relates two rates, with business count as a third variable (§6.2). Australian share by industry (U76), industry composition over time (U75), industry growth comparisons (U77–U78), innovation by industry and year (U119), and BERD per business also go beyond profiling one variable on its own. Labelling them “descriptive” does not make them univariate. The notebook introduction says relationships and several-variable analysis belong in later stages.

**Action:** Move substantive relationships to Stage 2, retaining individual distributions and data-quality checks here; alternatively, explicitly permit and label stratified descriptive exceptions. Do not remove a category-frequency chart or source-reconciliation table merely because it has two axes or columns. The entry/exit/bubble-size plot is an unambiguous scope exception. Evidence: `dcfc5580`, `229d05bf`, `da791075`, `41a922ed`, `903ab6c0`.

### R02 — High | U73 / §6.7: the coverage conclusion omits the added GVA series

**Issue:** “Only IP” covering all 37 years is contradicted by the immediately preceding overview: `gva_cvm` is **100% filled across 19 divisions, FY1990–FY2026**. The opening source description and U73 omit it. “The ABS’s series cover one to four recent years, except wages” is therefore false for the displayed lens. GVA receives no substantive profile beyond coverage and extrema, despite the notebook’s claim to profile every column.

**Action:** Add gross value added, its chain-volume definition, units and coverage to the overview, observation and summary, with a compact descriptive profile. Revisit the downstream scope decision in light of this longer series. Four business-count years and one BERD year remain real limits, but do not establish that all industry analysis must be “patterns, not models”. Evidence: `fca5b908`, `e08f442a`, `d5c5fdc5`.

### R03 — High | U75 → U114 / §6.7: the services update is not carried back

**Issue:** U75 still says the corpus holds the crosswalk excluding services; the final lead treats obtaining a services crosswalk as future work. Yet §6.5 already uses it, reaches all 19 divisions and changes manufacturing’s allocation from **90.63% to 79.67%**. U75’s **90.78%** uses FY2017–FY2026; U114 uses FY2016–FY2025. These are different windows, not inconsistent calculations. U114 also says totals “agree”, although its rounded totals differ by two expected applications (301,515 versus 301,513).

**Action:** Keep the no-services result explicitly as the chosen main specification, but link its headline and decision to the completed sensitivity analysis. Retire the completed lead. Use a common window for direct comparisons, or explain the different windows. Say totals are approximately equal and report/check the small allocation difference. Evidence: `a2da31f2`, `952539ed`, `4dccb359`, `84a55ef1`, `d5c5fdc5`.

## Crosswalks, coverage and industry shares

### R04 — High | U74: concentrated allocations are mistaken for certainty

**Issue:** A median largest division share of **0.996** and 77.9% of mapped standard patents allocating at least 90% to one division show concentration within the chosen crosswalk. They do not establish that “division counts for patents are close to certain”. The exclusion of services constrains the available destinations; U114 demonstrates substantial sensitivity to that choice. The decisiveness query includes rights appearing in the mapping, not all eligible rights. “Says what the rights protect” also overstates what a probabilistic class-to-industry mapping directly establishes.

**Action:** Describe “concentration of modelled allocation among mapped applications”, conditional on crosswalk, class weighting and correspondence rules. Retain the mapped denominators (301,163 standard patents; 831,780 trade marks), separate mapping uncertainty from concentration, and replace certainty language with the measured allocation shares. Evidence: `0f3f27d9`, `9758714f`, `e08f442a`, `84a55ef1`.

### R05 — High | U74: the coverage measure and its explanations need qualification

**Issue:** “Share of rights carried” is calculated as **summed expected counts divided by raw application counts**, not a distinct-right match rate. Their equivalence depends on each mapped right contributing exactly one unit, which this notebook does not demonstrate. The stated 98.42%–99.73% range is evidenced only for selected years. FY2026 falls to **92.71%**, and early second-tier coverage is as low as **52.69%**, weakening the broad “nearly every right” headline. Attribution to not-yet-classified or unclassified patents is not decomposed in the displayed checks.

**Action:** Label the existing statistic as retained allocation mass. Separately report distinct-right matching, per-right weight sums and unmapped/partly mapped cases. Calculate ranges over all years, or say “among selected years”. Present classification lag as an explanation requiring a missing-class versus failed-mapping check; qualify FY2026 and historical second-tier comparisons. Evidence: `9758714f`, `e08f442a`.

### R06 — High | U76 / §6.7: the headline and summary omit an eligible division and obscure denominators

**Issue:** The summary gives Australian patent shares of **7.87%–17.29%**, but the table includes **28.04% for public administration and safety**. “Every industry” also includes divisions with no allocated patents and undefined shares. Industry composition percentages divide by total **allocated** counts; Australian shares divide allocated Australian counts by all allocated counts, without showing unknown-origin treatment. U114’s `au_with (%)` is a different measure: the distribution of Australian applications across industries, not the Australian share within an industry.

**Action:** Correct the range and restrict conclusions to divisions with a reported denominator. State the FY2017–FY2026 window, expected-count threshold of 50, allocated-count denominator and Australian-origin definition, including missing-origin handling. Label the two kinds of Australian percentage distinctly. Replace “Australians file few patents” with a statement about their recorded share; a share alone is not a count. Evidence: `229d05bf`, `a2da31f2`, `4dccb359`, `d5c5fdc5`.

### R07 — Medium | Repairs / U75 / U114: mapping choices and source claims are not fully evidenced

**Issue:** The repairs introduction promises the predecessors map, but the following cell displays aggregate before/after counts, not the 26 mappings. It does not show the Nice-padding or full-versus-partial ISIC correspondence checks. “Only goods-producing industries” is too absolute at the final ANZSIC level: the no-services result reaches eight divisions, including professional services, public administration and other services. U114’s author-recommendation claim is not substantiated on the page; its 5.15% service weight is a crosswalk-wide statistic, not the application-weighted service share.

**Action:** Distinguish ISIC crosswalk exclusions from final ANZSIC allocations. Show compact evidence for each claimed repair and the basis for the preferred specification, or label those as externally documented assumptions. Define 5.15% explicitly as a proportion of crosswalk weight and avoid interpreting it as the proportion of patents allocated to services. Evidence: `54f2c868`, `9758714f`, `a2da31f2`, `4dccb359`, `84a55ef1`.

### R08 — Medium | U75: the 2002 break is over-interpreted and imprecisely described

**Issue:** “Accommodation and food services have no trade marks to FY2001” describes zero crosswalk allocation, not the absence of trade marks in that industry. “1.67% from FY2003” reads as a continuing level; the table gives **1.65% in FY2004** and **1.82% in FY2005**. The class-revision explanation is plausible, but the displayed division shares do not isolate its contribution from other changes. The mapping uses current classes, complicating a direct historical classification interpretation.

**Action:** Say “zero expected allocation through FY2001; 1.67% in FY2003”. Separate the observed discontinuity from the proposed classification explanation. Show class-level allocation before/after the boundary if attributing the change to the revision, and explain how current classifications are applied to historical filings. Mark the break on the chart. Evidence: `9758714f`, `da791075`, `a2da31f2`.

### R09 — Medium | U75: selected-year prose misses the early-2000s rebound

**Issue:** Manufacturing’s trade mark share is said to have fallen to 56.51% in FY2000 and “stayed near 55%”. The full saved chart shows a rebound to roughly **61% in the early 2000s**, before returning to the mid-50s. The selected-year table skips that interval. The later figure of 54.91% does not establish a flat path between endpoints.

**Action:** Describe the initial decline, temporary rebound and later mid-50s range separately. Add the rebound years and exact values to the supporting table rather than extracting precise values from the image. Use “among the selected years” wherever a range relies on a sparse display. Evidence: `da791075`, `a2da31f2`.

## Businesses, R&D and value added

### R10 — High | U77: IP per business would combine different industry concepts

**Issue:** Contrasting manufacturing’s patent allocation with its 3.2% business share invites an inference about manufacturers’ patenting. The section explicitly says firms have no observed industry and patents are allocated through technology classes. The numerator also includes overseas applications, while CABEE counts Australian businesses. A crosswalk caveat alone does not make this a measure of firms’ IP use or propensity to patent.

**Action:** Keep the two distributions separate. If carrying the ratio forward, label it as expected IP allocation relative to Australian business stock, with matched years and explicit origin coverage. Do not describe it as patents filed by, or average patenting of, businesses in that division. Distinguish modelling sensitivity from the separate mismatch between numerator and denominator populations. Evidence: `0f3f27d9`, `5ee84dfd`, `d5c5fdc5`.

### R11 — Medium | U77: the growth period and business-share denominator are ambiguous

**Issue:** “Growth FY2023 to FY2026” divides the FY2026 end stock by the **FY2023 start stock**: June 2022 to June 2026, four years, rather than June 2023 to June 2026. Business shares use the sum of the 19 coded divisions. The attachment later shows an `X` unknown-industry category, but the earlier shares are simply labelled “% of businesses”, without noting its exclusion.

**Action:** Label the growth interval “June 2022 to June 2026”, or change the base if June 2023 is intended. Describe shares as percentages of businesses assigned to the 19 divisions; reconcile against the published total and show unknown-industry counts for the same date. State the base used for entry and exit rates. Evidence: `dcfc5580`, `5ee84dfd`, `072ed5bf`.

### R12 — Medium | U78: BERD per business needs a precise population definition

**Issue:** The ratio divides annual industry BERD by **all CABEE businesses at June 2024**, not by R&D-performing businesses and not by an average annual business population. It is not a typical firm’s expenditure. Compatibility between the two sources’ business units and scope is not demonstrated. The visible table shows only the ten largest divisions by total BERD, while the headline makes an all-division claim about the largest per-business value.

**Action:** Label the ratio “industry BERD per CABEE business at June 2024” and explain the population/snapshot limitation. Show all 19 ratios or an explicit maximum check before the all-division ranking claim. Select FY2024 explicitly instead of taking each division’s maximum BERD across years, which would silently mix years if the corpus expands. Evidence: `41a922ed`, `daf34ae7`.

### R13 — Medium | U78: the wage comparison stops a year before the chart and available data

**Issue:** The overview and chart reach **FY2026**, but the growth ranking and prose end in **FY2025**. The title “slowest and fastest growth since FY2010” omits that endpoint, although the selected lines continue beyond it. The chart plots original index levels, not growth rebased at FY2010; the FY2010 starting levels differ. Broad “wages grew” wording can also be read as average earnings or purchasing-power growth, rather than the displayed Wage Price Index.

**Action:** State why FY2025 is the cutoff, or update the comparison to the latest eligible year after checking completeness. Align chart, ranking and prose periods. Rebase to FY2010 = 100 if the chart is intended to compare growth since that year, and describe changes in the WPI with its basis and units. Evidence: `fca5b908`, `41a922ed`, `daf34ae7`.

### R14 — Medium | U79: aggregate revision agreement is generalised to two releases

**Issue:** The BCARR comparison first sums the matched divisions by year. Its maximum displayed revision of about **1.2%** therefore describes annual aggregates, not agreement for every division, indicator or value in the two releases. Offsetting division-level revisions could cancel. The introduction’s “10 divisions with such activity” similarly infers an absence of activity in the other nine from absent values.

**Action:** Say “summed GVA across matched divisions differs by up to about 1.2%”. Show division-level revisions and matched coverage before claiming broader agreement. Refer to ten divisions with published/non-null values unless the omitted divisions are explicitly known to have no activity. Preserve the existing nominal-value qualification in U78. Evidence: `fca5b908`, `e08f442a`, `072ed5bf`, `8ea65e94`.

## Attachments, innovation and overlooked observations

### R15 — Medium | U79 → U119: the attachment total excludes the added cubes

**Issue:** U79 says the attachments hold **1,409,875 values**, but its query explicitly excludes `bcs_cubes`. The later cube inventory adds **15,282 rows**, giving **1,425,157**, consistent with the introductory lens inventory. Moreover, rows are not synonymous with available numerical values: U79’s own table reports **25% empty BCS values** and **1.4% empty WPI values**. “Every value … publish” is a completeness claim that the inventory alone cannot establish.

**Action:** Update the current total, or clearly label the older subtotal “excluding the 2024–25 cubes”. Use “rows” and report available numeric values separately. Describe the selected sources/releases rather than asserting exhaustive publication coverage without reconciliation. Update the U79 summary while preserving separate sources instead of summing overlapping indicators. Evidence: `072ed5bf`, `8ea65e94`, `903ab6c0`, `d5c5fdc5`.

### R16 — High | U79 / U119: distinct innovation measures and cross-source comparability need checking

**Issue:** U79 reports businesses that introduced a **new good or service** (22.0%, 21.7%). U119 reports **any innovation activity** (51.9%, 45.7%, 45.6%). These are different measures, not a revision of the same estimate, yet “innovation” and “innovating businesses” blur that distinction in the headlines/summary. For U119, the code asserts “the same question” while joining an API indicator named `P_D_INNOVATOR_GV` to a cube indicator containing `innovation_active_businesses`; it does not display definitions, reference periods or eligible populations to establish equivalence.

**Action:** Use each measure’s exact definition consistently. Show the two source labels, scope, reference periods and units before treating U119 as one series; verify whether completed versus ongoing/abandoned activity is treated identically. Do not declare the series invalid from identifier names alone. Keep the measures separate, and add the new-good/service result for 2024–25 only if a comparable field exists. Evidence: `072ed5bf`, `8ea65e94`, `903ab6c0`, `7dcf4714`.

### R17 — High | U79 / U119: uncertainty claims are stronger than the displayed checks

**Issue:** The inventory measures non-null `status` and null `value`, but U79 translates these directly into “flagged for sampling error” and “not available for publication” without showing status codes or null reasons. The innovation tables omit status and precision fields. U119 then declares differences of “a few points” unreliable, which cannot be determined from a universal point threshold. “Has not recovered” presents a population trend more firmly than the displayed sample point estimates alone support.

**Action:** Tabulate status meanings and missing-value reasons; carry relevant flags and available uncertainty measures into the selected estimates. Say the reported total is 6.3 percentage points below 2020–21 and 0.1 point below 2022–23, conditional on comparability. State that significance is unassessed without appropriate uncertainty estimates; do not assume either reliability or unreliability from point differences alone. Evidence: `072ed5bf`, `8ea65e94`, `903ab6c0`, `7dcf4714`.

### R18 — Medium | U119: the national headline overlooks differing industry patterns

**Issue:** “Has not recovered its 2020–21 level” is not explicitly restricted to the national total. The table shows **accommodation/food services at 55.5% versus 53.8%** and **mining at 37.3% versus 34.8%**. It also shows seven divisions’ point estimates rising from 2022–23 to 2024–25 despite the almost unchanged total. The largest 2020–21 to 2024–25 decline is rental/hiring/real estate (**−17.5 points**), marginally larger than administrative services (−17.2), but is omitted.

**Action:** Restrict the headline to the total and briefly note the exceptions and largest displayed decline, without declaring statistical significance. Replace value-laden “recovered” with “remained below” for point estimates. Keep division-by-year comparisons in Stage 2 if strict univariate scope is retained. Evidence: `903ab6c0`, `7dcf4714`.

### R19 — Medium | Figures and tables: qualifications are lost when outputs are read alone

**Issue:** The industry-share charts label the denominator as applications rather than allocated expected applications and do not identify the no-services patent specification. “The six largest divisions” means the six with the highest **mean annual share during FY2017–FY2026**, not necessarily the largest in every plotted year. The entry/exit plot uses letter labels with no on-chart industry key or quantitative bubble-size legend. Subdivision labels and several units are truncated in saved tables.

**Action:** Put allocation basis, crosswalk, period and selection rule in captions. Add classification-break and low-coverage markers where relevant. If retained outside strict Stage 1, give the bubble plot a readable key and size reference. Display full subdivision labels and explicit units; do not require later prose to reconstruct a chart’s meaning. Evidence: `229d05bf`, `da791075`, `dcfc5580`, `41a922ed`.

### R20 — Medium | Completion claims: several variables and material patterns remain unprofiled

**Issue:** Second-tier expected patent counts and absolute business entries/exits receive only an overview or coverage check, rather than a distribution or short substantive profile. The creative-value-added table shows wholesale falling from **$1,631 million to $1,540 million** between FY2016 and FY2025 and education rising from **$552 million to $1,240 million**, neither noted in U78. Inventories of thousands of attachment indicators are useful coverage summaries but do not establish that every variable has been explored. The stated absence of a 2023–24 BCS release is also not proven by its absence from the displayed table.

**Action:** Add compact profiles for analytically important omitted columns, using comparable periods and retaining structural-zero/missing distinctions. Add the creative-sector exceptions if relevant to the section’s summary, explicitly in nominal terms. Mark attachments as inventoried versus substantively profiled, and label unverified publication-history statements as source documentation requiring confirmation. Do not expand the review into arbitrary comparisons simply to tick every field. Evidence: `fca5b908`, `41a922ed`, `daf34ae7`, `072ed5bf`, `903ab6c0`, `7dcf4714`.

## Review boundary and reproducibility

These findings establish inconsistencies and limitations visible in the notebook; they do not establish that the underlying source data, mappings or imported helpers are incorrect. In particular, source-scope equivalence, statistical precision and the implementation of repairs need checks beyond this notebook-only review. No website, notebook or repository changes were made.

All ten Lens 6 code cells have saved outputs, sequential execution counts **148–157**, and no saved error outputs. This does not establish that the current data or imported code would reproduce the results. Arithmetic checks used displayed values; approximate readings of charts are identified as such.

**Evidence locators:** U-numbers and section headings are searchable. The eight-character identifiers are stable notebook JSON cell `id` values, not execution counts. This report contains **20 issue/action entries**. Existing no-services estimates are not treated as inherently invalid merely because an alternative crosswalk was added; the issues concern interpretation, sensitivity and obsolete wording.

Downloaded notebook SHA-256: `1d5e51a699b82091788c75fdaff6d2706a24ba6a91df21877799677a8a357cdb`.
