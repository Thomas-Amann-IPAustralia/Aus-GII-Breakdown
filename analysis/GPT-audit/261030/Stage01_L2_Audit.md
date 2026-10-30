# Stage 1 notebook audit: Lens 2 reviewed in depth

**Reviewed:** 31 October 2026. **Source:** [01_univariate.ipynb](https://github.com/Thomas-Amann-IPAustralia/Aus-GII-Breakdown/blob/main/analysis/notebooks/01_univariate.ipynb), downloaded from `main` for this review.

**Provenance:** Follows the layout, priorities and Issue/Action format of [Stage01_L0-L1_Audit.md](https://github.com/Thomas-Amann-IPAustralia/Aus-GII-Breakdown/blob/main/analysis/GPT-audit/261030/Stage01_L0-L1_Audit.md). Identifiers continue from that chapter's R44. This is a separate, self-contained review of Lens 2.

**Scope of this pass:** Only §2, including §§2.0–2.7, observations U41–U47 and U112. Reviewed all 30 cells: 14 code cells, their saved outputs, all seven embedded figures, and the commentary. The introduction/setup were consulted for the notebook's stated rules and dependencies. Apart from the preceding audit as a format reference, no other repository files, underlying datasets, external factual sources or GitHub Pages website were assessed. The notebook was not re-executed; imported helpers and referenced ADRs were not independently verified.

**Overall finding:** Most quoted descriptive statistics match the saved outputs. The principal weakness is inconsistent incorporation of the register update: different analyses now use different definitions of an IP filer. Several headlines also generalise beyond the selected ABNs, conflate recorded activity with real-world behaviour, or contradict their supporting tables.

**Priority:** **High** = affects interpretation, validity or downstream use; **Medium** = correct before relying on or circulating the findings. Implementation-dependent concerns are framed as checks. Apply corrections to §2.7 as well as the original observations.

**Read first:** R47–R51 address inconsistent populations, linkage and first-filing claims; R58 addresses incompatible monetary periods; R60 and R62–R65 address geographic and WGEA interpretation. Descriptive analysis can still be bivariate.

## Scope, freshness and definitions

### R45 — High | Throughout: comparisons exceed the stated univariate scope

**Issue:** Entity group × source and status × entity group (§2.1), age × dating source (§2.2), ABN linkage × year × right/type (§2.3), geography × source (§2.5), and filing share × employer size (§2.6) analyse relationships between variables. U112's rising filing share across size bands is explicitly an association. Labelling these “descriptive” does not make them univariate.

**Action:** Move substantive comparisons to Stage 2, retaining marginal distributions and necessary coverage diagnostics. Alternatively, explicitly permit stratified descriptive analysis and mark those exceptions. A frequency distribution of first-observed years or a log-scaled histogram is not automatically bivariate merely because it has two axes. Evidence: `386b9d6a`, `e8cb8e76`, `3caa1fdb`, `f0b7821c`, `25eb740f`, `9439498d`.

### R46 — High | U41: source categories are mistaken for complete source membership

**Issue:** The membership query suppresses IPLORD/register flags when an earlier IP category applies. “IP RAPID alone” therefore means no R&D, procurement or tax flag within this hierarchy, not necessarily absence from IPLORD/register. Summing the displayed combinations gives **66,324** ABNs linked to IP through the register but neither earlier IP source, and **52,949** through IPLORD but not IP RAPID; **64,829** and **50,790** are their single-category rows. Likewise, 91.91% active describes the R&D-only row, not all claimants.

**Action:** Label the hierarchy explicitly and distinguish category-only counts from totals across combinations. Use original membership flags if actual source intersections are intended. Keep “ABNs in this selected lens” as the population: an ABN is not necessarily one operating firm or corporate group. Evidence: `7466d4dd`, `27378427`.

### R47 — High | U42 / U44 / U47 / U112: “IP filers” changes meaning within the lens

**Issue:** U44 reports **301,249 trade mark filers**, but only **265,615** ABNs with any `ip_filed_total`. U112 instead identifies **323,604** filers using the sum of the per-type counts. Entity and geography profiles still select `ip_filed_total > 0`, a population **57,989 smaller in net terms**. The notebook explains that per-type trade mark/design counts use register-filled ABNs, whereas the aggregate credits every founding applicant. These measures cannot be treated as interchangeable; the per-type total is **1,379,824**, versus **1,253,998** aggregate filing credits.

**Action:** Reconcile ABNs and filing credits by linkage version and attribution rule. Define one current filer population for cross-section comparisons, then regenerate U42/U47 and their charts. Retain alternative measures only with explicit labels; co-applicant counting alone cannot explain an “any IP” population smaller than trade mark filers. Evidence: `386b9d6a`, `ca4d2541`, `f0b7821c`, `25eb740f`.

### R48 — High | U41 / overview: zero-filled counts are not complete observations of non-use

**Issue:** U41 explicitly says IPLORD-linked entities can have zero IP counts despite known IP use. Nevertheless, the completeness chart shows these count columns as 100% filled. The “lower bounds” headline also needs qualification: the notebook does not verify every attribution, distinguish unique applications from co-applicant credits, or expose the counting helpers. Source disagreement demonstrates non-equivalence, not which count is correct.

**Action:** Distinguish recorded zero, known activity without attributable counts, and inapplicable/missing information. Describe amounts as recorded counts under stated attribution rules, rather than verified lower bounds on every firm's true activity. Report coverage among eligible records alongside non-nullness. Preserve the decision not to merge incompatible IPLORD counts without asserting that the discrepancy's cause has been established. Evidence: `556e91be`, `cf3b96d9`, `7900af1e`, `27378427`.

## Entity status, age and IP use

### R49 — High | U45 / §2.7: the revised result leaves the superseded chart in place

**Issue:** The first-filing chart and table still use unfilled `*_first_fy`, showing trade mark counts falling to **7,384** in FY2026. U45 later gives the filled result of **19,730**, but no corresponding local chart/table. The summary says filers are no longer less often linked, although its own filled figures fall from **92.3% to 90.9%**. Also, `patent_first_fy` covers patents generally, while the overview labels `patent_first_fy_filled` as **standard patents**: substituting fields would change scope.

**Action:** Make the updated series the primary evidence and identify the old series as a diagnostic comparison. Preserve a consistent patent subtype definition. Say the sharp linkage decline is substantially reduced, not eliminated; retire the superseded decision to stop at FY2024. Evidence: `556e91be`, `ce3fe734`, `02e6ebb8`, `2da9aa3b`.

### R50 — High | U45: first observed filing does not establish true entry

**Issue:** “Firms filing their first application” means the earliest application linked to an ABN in the available records. Missing older links can assign a repeat filer to a later entry cohort. Consequently, the restatement that earlier cohort counts are “lower bounds” is not assured: a cohort can both lose unlinked genuine entrants and gain misclassified repeat filers. The register's additional ABNs demonstrate a source discrepancy, not by themselves the precise publication mechanism causing it.

**Action:** Use “first observed ABN-linked application”, define the historical observation window and show sensitivity to linkage changes. Do not equate the filled increase with new-business entry or unrestricted year-to-year comparability. Describe publication differences as supported by the reconciliation, with the precise mechanism requiring evidence. Evidence: `ce3fe734`, `02e6ebb8`.

### R51 — High | U41 / U45: linkage percentages concern selected rights, not distinct firms

**Issue:** U45's linkage query averages application-level ABN presence; it does not measure the share of distinct filers linked. It also combines `founding_australian` with one `founder_type` without showing that country and type refer to the same party. In U41, the **6.04%–7.25%** no-filer-ABN range omits provisional applications at **1.70%**; the 7.11% trade mark filer/holder difference is conditional on both ABNs being known. These checks use unfilled fields despite the subsequent count update.

**Action:** State right-level denominators, eligible subtypes, party selection and linkage version. Include the provisional exception and retain the both-known qualification in the summary. Check party alignment and show filled versus unfilled diagnostics before carrying these figures into firm-level conclusions. Evidence: `b8bbb04a`, `3caa1fdb`, `27378427`.

### R52 — High | U41: inactive ABNs are interpreted as closed businesses

**Issue:** “Many firms that once filed for IP have since closed” is stronger than the snapshot of `abn_active`. The table establishes neither closure dates nor continuity of the underlying business under another entity/ABN. IP membership also includes owners and historical links, not only verified original filers. Activity percentages exclude null statuses through `avg`, rather than treating every ABN as observed.

**Action:** Say that a stated share of ABNs with known status is inactive at the source snapshot. Do not infer business closure, timing or survival from this flag alone. Show unknown-status counts and retain the distinction between applicants and owners. Evidence: `7466d4dd`, `27378427`.

### R53 — Medium | U42: the entity headline and contextual explanations overreach

**Issue:** “Private companies dominate every source but AusTender” conflicts with their **55.3% majority** among suppliers. Only selected groups are compared, not every source. Rounded 0.0% cells do not prove no trusts/sole traders/partnerships occur among R&D claimants. The claimed increase in sole traders after adding the register has no before/after table. GST status is also presented as a rough turnover classification without evidence here.

**Action:** Say private companies are the largest group in all displayed populations, with a smaller share among suppliers. Show unrounded counts before asserting absence, a before/after comparison for the register effect, and treat eligibility rules as sourced context. Report GST registration as status, not an observed turnover band. Evidence: `386b9d6a`, `5212ff36`.

### R54 — High | U43: recorded age and its truncation flag need narrower interpretation

**Issue:** Age statistics concern the **430,679 dated ABNs**, including inactive entities; they are not ages of all operating businesses. The overview supplies no age reference date. All **32,600 undated** entities have `age_truncated = False`, which must not be read as reliable age. Starting after 2001 avoids the ABN-introduction spike but does not establish that a registration date is business inception. The 1817 extreme is recorded, not independently validated here.

**Action:** State “elapsed years since earliest available registration”, the as-of date and known-date population. Define what the truncation flag detects and use an explicit unknown category for undated records. Qualify any lower-bound interpretation by entity continuity and date validity; do not treat the post-2001 subset as free of age measurement limitations. Evidence: `556e91be`, `e8cb8e76`, `d79fbe22`.

### R55 — Medium | U44: the headline loses its positive-count and standard-patent qualifications

**Issue:** “Most firms file once or twice” is not established for all 463,279 ABNs: the aggregate has **42.7% recorded zeros**, and a median of two among positives does not give the exact share filing one or two. “A few file most of the patents” is supported for **standard** patents, whose top 1% account for 55.3%; corresponding shares are 32.0% for provisionals and 12.2% for second-tier patents.

**Action:** Report conditional medians and compute the explicit one-or-two share if that headline is retained. Restrict the majority claim to standard patent applications attributed in this lens, not all Australian patents. Rename the table's “% filed” column for `n_held` and `n_held_in_force` to “share of the total”: holdings are not filings. Evidence: `ca4d2541`, `02e6ebb8`.

### R56 — Medium | U44: log-binned chart shape is overstated

**Issue:** The charts use raw counts in geometrically widening bins, with both axes logged. Their apparent straightness depends on binning; gaps near one application can be empty integer bins, not absent behaviours. A long right tail is supported by the medians, upper percentiles and maxima, but “close to a straight line” is not a checked distributional result.

**Action:** Describe the observed skew and concentration without implying a particular distribution. Label the vertical scale as firms per log-spaced bin, and use integer-frequency plots or a complementary cumulative distribution if shape matters. State that zero-count ABNs are excluded; account for those zeros before applying logs downstream. Evidence: `ca4d2541`, `02e6ebb8`.

## R&D, income and government contracts

### R57 — High | U46: expenditure, tax benefits and concentration groups are conflated

**Issue:** The field is labelled R&D expenditure claimed, but “median latest claim” and “top 1% claim” can be read as the tax benefit received. “R&D claims are spread” understates the displayed top-1% share of **28.1%** without a criterion. For AusTender, **83.1% of value** and **55.9% of contracts** come from independently ranking suppliers on each variable; the code does not show that the same suppliers hold both shares.

**Action:** Name the measure as reported R&D expenditure, unless a tax-offset amount is actually available. Report concentration numerically. Say “the top 1% by value” and “the top 1% by contract count” separately, or calculate both quantities for one explicitly defined supplier group. Evidence: `83193d44`, `0ee1258a`.

### R58 — High | U46: the monetary distributions mix reporting periods and exposure lengths

**Issue:** R&D and tax income use each ABN's latest available year, which need not be the same year. Contract value is an accumulated supplier total, unlike annual income/expenditure; contract counts and values also reflect different lengths of observed participation. No contract accumulation window is stated. A later CPI adjustment alone cannot align reporting periods or correct unequal exposure.

**Action:** Show the latest-year distribution and source windows, and label cross-year snapshots explicitly. Describe contract values as recorded contract values, not actual payments or annual revenue. For comparable annual distributions, rebuild from a defined period and deflate dated amounts before aggregation; otherwise retain the narrower mixed-period description. Evidence: `1355e8cc`, `83193d44`, `0ee1258a`.

### R59 — Medium | U46: zero and low-income explanations exceed the actual queries

**Issue:** The query counts **195 R&D values below $1**, not necessarily 195 exact zeros. The 15 low-income entities are identified only by income; the accompanying query shows six appeared in one year, not that all 15 come from the reports' first years. The blanket $100-million coverage statement is external eligibility context, not established by this output. Chart statistics exclude sub-dollar values while table statistics include them, although the caption usefully discloses this.

**Action:** Separate exact zeros, positive sub-dollar values and negatives. Tabulate the 15 entities' reporting years before attributing their values to early releases, and qualify the coverage threshold by applicable year/category if retained. State chart sample sizes beside table counts. Evidence: `83193d44`, `0ee1258a`.

## Geography and WGEA attachment

### R60 — High | U47: the headline contradicts the advantage table and generalises beyond the lens

**Issue:** “Government suppliers less so” implies they are less advantaged as well as less metropolitan. Yet **35.3%** are in decile 10, above **33.4%** for the whole lens; their top-three-decile share is **66.3%**, versus **65.5%** using displayed values. Lower metropolitan share does not establish lower advantage. “Firms in general” also generalises from a selected corpus, and area advantage is not the firm's own prosperity.

**Action:** Separate the two dimensions: suppliers have a lower major-city share (**78.9% versus 85.3%**), but the displayed advantage distribution does not support the blanket “less advantaged” claim. Refer to ABR addresses in more advantaged areas among lens ABNs. Retain the existing warning that addresses are not operating locations. Evidence: `f0b7821c`, `f9253fee`.

### R61 — Medium | U47: geographic percentages conceal changing known-case denominators

**Issue:** `share()` drops missing values separately for each variable and group, while the axis says “% of the group's firms”. State, remoteness and IRSAD therefore have different denominators. “Most advantaged tenth of postcodes” assumes a particular ranking universe and mapping that the notebook does not expose. Present-day ABR addresses also cannot locate historical filing activity without temporal linkage.

**Action:** Show eligible, known and missing counts per group/variable and label percentages “among ABNs with known [field]”. State the ABS geography, vintage, decile construction and postcode mapping; until demonstrated, call this “IRSAD decile 10”. Keep historical activity and snapshot address distinct. Evidence: `556e91be`, `f0b7821c`, `f9253fee`.

### R62 — High | U112: “employers of 100 or more” is not the demonstrated coverage boundary

**Issue:** The overview shows WGEA employee counts as low as **one**, while the section says every private employer with 100 or more reports and its headline implies size/industry are known for that population. Only **6,009 of 8,240** latest-year employer rows match the lens (**72.9%**); 7,126 is the count across latest available reports from multiple years. The threshold does not explain which sub-100 ABNs have data, and reporting eligibility is not evidence of complete coverage.

**Action:** Describe matched reporting entities and their actual employee-count range. Explain the reporting unit and any below-threshold records before making population-wide claims. Separate source coverage, lens matching and latest-year coverage, including the **2,231** latest-year rows outside the lens. Evidence: `556e91be`, `25eb740f`, `22e96477`.

### R63 — High | §2.6: employer and workforce aggregation need a visible unit check

**Issue:** Annual “employers” are calculated with `count(*)` and employees with `sum(employees)`. Lens ABN uniqueness is demonstrated, but the notebook does not show uniqueness of the source's employer-year rows or whether workforce counts refer to individual ABNs or reporting groups. This is an unverified aggregation assumption, not a demonstrated duplication error.

**Action:** Add a compact source check of row count, distinct reporting units/ABNs per year, duplicate keys and the scope of employee totals. Document how group reports, if present, attach to ABNs and ensure workforce totals are not repeated. Qualify national-looking totals until those checks are evidenced. Evidence: `25eb740f`.

### R64 — High | U112: latest employer attributes are attached to historical IP totals

**Issue:** WGEA size/industry are taken from each firm's latest report, while `n_*` counts have no filing-period restriction. The increase in recorded filing share from **70.1% to 82.5%** is therefore not a contemporaneous size–filing comparison. **1,117** matched firms have older reports. The 18.41% patent and 12.29% trade mark shares concern the lens's attributed applications, not all IP or current portfolios.

**Action:** State the report-year mix, historical filing window and application denominator. Describe the association as latest recorded size versus any observed historical filing, or align filings and employer attributes to a common period in Stage 2. Keep the lens-only qualification in the headline and summary. Evidence: `25eb740f`, `22e96477`.

### R65 — High | U112: the industry benchmark mixes selected and differently dated populations

**Issue:** The comparison uses WGEA-matched lens ABNs with their latest reports against `businesses_start` from CABEE's FY2024 row. It is not all large employers versus all other firms at a common date. Lens inclusion, reporting scope, business unit and period can each affect the composition. The displayed industry differences are valid for the two tabulations, but cannot be attributed to employer size alone.

**Action:** Name both populations and the CABEE opening-stock reference date. Either align units, periods and eligibility or label this as a non-equivalent contextual comparison. Replace “large employers are a different mix” with “the WGEA-matched lens subset has a different recorded industry composition”. Evidence: `9439498d`, `22e96477`.

### R66 — Medium | U112: the source-search conclusion is unsupported and too absolute

**Issue:** “Firms under 100 employees still have no size or industry” is inconsistent with the sub-100 WGEA values in the overview. “No free firm-level source holds them” is a universal availability claim supported only by an unseen ADR. The notebook establishes sparse attached coverage, not the absence of every possible source.

**Action:** Say size/industry are populated for matched WGEA records and remain unpopulated for other lens ABNs under the current construction. If retaining the search conclusion, describe it as a documented search finding with date, scope and limitations, rather than proof that no source exists. Evidence: `556e91be`, `22e96477`.

## Overlooked observations, evidence and amendments

### R67 — Medium | §§2.1–2.6: important columns lack the promised univariate profiles

**Issue:** The overview does not fulfil the introduction's promise to assess each variable's typical values, spread and outliers. `ip_filed_weighted` has no distribution; `wgea_women_share` receives only min/max/mode despite spanning 0–1. The size table leaves out the **six unknown-band records** from U112's prose. Entity type/ASIC type receive no frequency profile, and §2.1 does not show status and GST rates for each source as its checklist promises.

**Action:** Add compact, relevant marginal summaries with denominators and missingness, or narrow the completion claim/checklist. Prioritise weighted filing counts, WGEA workforce share/employee-count tails and unknown size bands. Do not introduce additional relationship analysis merely to fill the gaps. Evidence: `556e91be`, `80b644ce`, `25eb740f`.

### R68 — Medium | U43 / U44 / U46: visible anomalies and limits need short descriptive notes

**Issue:** U43 discusses the ABN-start spike but overlooks repeated GST dates: **954** entities on 1 July 2023, **918** on 1 July 2016, **915** on 1 July 2022 and **862** on 30 June 2013. The 5,506 ABN-start records do not alone establish the cause of the entire histogram hump. Concentration findings also depend on extreme records, including **25,373 contracts** and **$23.28 billion** for a supplier, without an on-page aggregation check.

**Action:** Flag date clustering and extremes for validation, not as established errors. Check date conventions, contract identity/amendment aggregation and the leading observations' contribution. Describe accumulated activity over its stated window; do not infer filing intensity or business performance from lifetime totals alone. Evidence: `e8cb8e76`, `ca4d2541`, `83193d44`.

### R69 — Medium | Introduction / repairs / figures: stale metadata obscures the current snapshot

**Issue:** The introductory firms count is **398,450**, versus **463,279** in the executed overview. The overview comment says 44 columns, but there are **50**; the entity code says 63 missing ABR entities, but the overview gives **252**. The historical state repair gives 3,977 blanks and 165 fills without reconciling the current **4,145** missing states. The missingness chart omits register/WGEA sources; the IP histogram credits IP RAPID alone although U44 identifies register-filled trade marks/designs.

**Action:** Update metadata from the current execution, date historical repair counts, and name all contributing sources in captions. Show snapshot dates for ABR/ASIC, IP, monetary and WGEA data rather than implying a single simultaneous observation. Evidence: `257435cc`, `556e91be`, `ba553e93`, `386b9d6a`, `cf3b96d9`, `ca4d2541`.

### R70 — Medium | §2.7: maintain one authoritative observation and preserve its qualifications

**Issue:** The summary repeats the problematic U42, U44, U45, U46 and U47 headlines and drops important population qualifications. U45 retains an old lead, an obsolete decision and a revised decision beside the old chart. Several explanations rely on ADRs or other observations rather than the on-page outputs promised by the notebook; imported transformations cannot be verified here. Lens 2 also depends on `TYPES`, `TYPE_COLOURS` and `np` defined earlier, so it is not independently executable after setup.

**Action:** Regenerate the summary after the corrections, retaining population, period, attribution and missingness qualifications. Move superseded conclusions into a dated change note. Bring decisive evidence into the section or clearly label externally documented assumptions. State execution prerequisites or centralise shared definitions; expand ABN, ABR, GST, IRSAD and WGEA locally for non-technical readers.

## Review boundary and reproducibility

The audit establishes discrepancies in the notebook and identifies checks needed before stronger interpretations are used. It does not establish defects in underlying datasets or imported build/helper code. All 14 Lens 2 code cells have saved outputs, with sequential execution counts 77–90 and no saved error outputs; this does not establish reproducibility against current source data. No notebook or repository changes were made.

**Evidence locators:** Section headings and U-numbers are searchable. Backticked eight-character identifiers are stable notebook JSON cell IDs, not execution counts. Calculations added by this audit use displayed counts; the geographic top-three shares sum rounded table values. The register contains **26 issue/action entries, R45–R70**.

Downloaded notebook SHA-256: `1d5e51a699b82091788c75fdaff6d2706a24ba6a91df21877799677a8a357cdb`.
