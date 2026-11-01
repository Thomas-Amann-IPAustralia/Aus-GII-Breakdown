# Stage 1 notebook audit: Sources outside the lenses and Stage 1 summary

**Reviewed:** 1 November 2026. **Source:** [01_univariate.ipynb](https://github.com/Thomas-Amann-IPAustralia/Aus-GII-Breakdown/blob/7513aac9c68a345c5c1dd684c31fab6c633c763e/analysis/notebooks/01_univariate.ipynb), retrieved from `main` on the review date.

**Format:** Follows `analysis/GPT-audit/261030/Stage01_L0-L1_Audit.md`: prioritised, numbered findings with an explicit **Issue** and **Action**. R01–R25 are local to this report. References such as “L4 R11” identify findings in the earlier lens audits, not additional findings here.

**Scope of this pass:** Only §8 and §9, comprising two Markdown cells and one code cell with its saved output. Relevant earlier notebook code, tables and observations were consulted to check the summary. All seven earlier audit reports covering L0–L1 and L2–L7 were considered. The repository copies of L0–L6 match their supplied report versions; L7 was obtained from the supplied report. The notebook also matches the SHA-256 recorded by those audits. The GitHub Pages website, underlying datasets, imported helpers, ADRs and external summary document were not assessed. The notebook was not re-executed.

**Overall finding:** §8 does not demonstrate the advertised profiling coverage and retains an unreconciled policy-event profile. §9 carries forward numerical errors, stronger interpretations than the evidence supports, and decisions superseded by later notebook additions. The main task is to regenerate the summary from corrected observations, preserving their populations, periods and limitations.

**Priority:** **High** = affects interpretation, validity or downstream use; **Medium** = correct before relying on or circulating the findings. Checks requested below are not claims that unseen data or implementations are wrong.

**Read first:** R02–R05, R12, R16–R17, R19 and R21–R25. Prospective Stage 2 questions are appropriately placed in a handover; the scope problem is presenting relationships or model-dependent conclusions as completed univariate findings.

## Scope, source coverage and freshness

### R01 — Medium | §8: the coverage claim exceeds the evidence shown

**Issue:** The section says these sources are profiled, but displays only the policy-events column profile. “One call away” and a catalogue link do not show completion of the promised size/time-span and coverage checks for, for example, `tga`, `wine_gi`, `fedcourt` and `evidence`. Conversely, many listed sources are already attached to lenses, so the heading obscures what actually remains outside them. Existing audits also distinguish inventories from substantive variable profiles.

**Action:** Replace the planning table with a current coverage register: source/table, lens or outside-lens status, available profile date, evidence location, completed work and deliberately deferred work. Show compact counts, time coverage and relevant missingness for retained outside-lens sources, or mark them unassessed. Do not imply every variable was explored merely because metadata exists. Evidence: `c65816b4`, `fd966a12`; L0–L1 R41, L2 R67, L4 R29, L6 R20, L7 R04.

### R02 — High | §8: the policy-event profile is not reconciled with later use

**Issue:** The saved profile reports approximately **16 distinct IDs/dates**, whereas §5.4 evaluates **17 named events** and U108 says fee changes were added to `policy_events`. An approximate distinct count is not an exact row count, so the discrepancy does not prove an event is missing; it does require reconciliation. The Boolean `verify` field shows one approximate distinct value, with example `false`, but its meaning is unexplained. That cannot establish either verification or non-verification of every event.

**Action:** Show a dated, exact inventory with row/unique-ID counts, duplicates, event categories, date types and a reconciliation to the 17 timeline events and added fees. Explain `verify`, show its actual distribution and distinguish a source URL from a completed date check. Retain the original profile only as a labelled historical snapshot if applicable. Evidence: `fd966a12`, `280d6566`, `525a6bb3`; L5 R02.

### R03 — Medium | §§8–9: navigation and the handover have not caught up with additions

**Issue:** §9 points to six obsolete lens-summary sections. The current sequence is **1.9, 2.7, 3.8, 4.7, 5.11, 6.7 and 7.9**. It twice treats fee history as missing despite U108–U111. §8 omits the historical fee source `frl_fees`. The selected summary also provides no current handover for material additions such as WGEA, RBA/national accounts, ATO/Census time series, newer business surveys, GII supplements, NSRC and the expanded PBS series.

**Action:** Correct the pointers and fee-history status; add a brief “later additions and remaining limits” row or note with links to the relevant observations. Update the source register accordingly. A selective summary need not repeat all results, but its stated gaps and analysis options must reflect the available notebook. Evidence: `2f712bb5`, U108–U123; L5 R02, L6 R03/R15, L7 R21.

### R04 — High | §9 opening and Strength column: descriptive is not synonymous with univariate

**Issue:** Every row is labelled descriptive, and the opening extends that label to every notebook observation. Yet the summary includes origin–citation comparisons, geography–filing comparisons, a Spearman correlation and model-based claims about chance. U121 also extrapolates from a sample. “Because”, “rushes” and “made here” introduce explanations or interpretations beyond simple recorded distributions.

**Action:** Retain genuine marginal descriptions and coverage diagnostics. Move substantive relationships to Stage 2, or explicitly label permitted descriptive comparisons and estimation exceptions. Distinguish observed statistics, hypotheses, model-dependent inference and practical decisions. Keep the prospective Stage 2 list, while avoiding the implication that its relationships have already been established. Evidence: `83e76483`, `257435cc`, `2f712bb5`; scope findings in all seven earlier audits.

## Rights, parties and proxy measures

### R05 — High | §9 U7/U13 and origin-based comparisons: holder and filer remain conflated

**Issue:** The **91.3% overseas** and **59.0% Australian** findings use applicant fields that §1.8.1 defines as current-holder information. They cannot silently become historical filing-origin claims. The same distinction affects route, reach and inventor comparisons. The design decision also fails to identify the register-filled result in U102: **32.31% Australian among known origins, 0.007% unknown**, for FY2017–FY2026.

**Action:** Use validated founding-origin fields for filing claims, or label results as current-holder classifications. Identify the selected party and known-origin denominator. Carry U102's revised coverage into the decision without treating filled holder information as verified origin at filing. Evidence: `7e248d05`, `748d4a39`, `93e8da39`; L0–L1 R04/R12/R39, L4 R12.

### R06 — Medium | §9 U8: the provisional increase is attributed too narrowly

**Issue:** “Doubled … from individuals” implies that the whole rise came from individuals. U8 reports **10,069 total applications**, **5,399 with an individual first applicant**, and applications with an ABN rising from **2,329 to 2,619**. A broadly flat number of distinct ABNs is a different measure and does not establish unchanged business filing activity.

**Action:** Report the total rise and the individual-first-applicant rise separately, with an explicit comparison year. Describe the ABN count as a linkage-based distinct-entity count, not evidence that businesses did not contribute. Retain the cause as an open question. Evidence: `bd230f5c`; L0–L1 R07.

### R07 — High | §9 U17/U35 and Stage 2 item 3: recorded changes are not a complete ownership history

**Issue:** The **64.68%–74.66%** assignment agreement for observed holder changes is carried into a decision to use `assignment_count` before FY2003. It does not establish historical recovery at the same rate. Party-ID differences can include name/identity changes; endpoint country changes do not show inventions or economic value physically moving overseas. U17 also warns that older founding fields may describe a later holder.

**Action:** Separate recorded holder differences, assignment events and endpoint country classifications. Treat pre-FY2003 assignments as an incomplete indicator with unestablished sensitivity. Preserve the founding-field limitation and phrase the proposed overseas analysis in terms of recorded ownership/origin transitions. Evidence: `47b1aa0c`, `513423e3`; L0–L1 R16.

### R08 — High | §9 U20/U21 and Stage 2 item 2: representation is an unvalidated proxy

**Issue:** The summary treats an agent serving at least five applicants as an attorney, threshold sensitivity as “bounds”, and the **63.96%** top-five share as applying to standard patents generally. Its denominator is applications classified as attorney-represented under the proxy. “Alone” denotes a recorded representation category, not independently verified absence of legal assistance.

**Action:** State the client-count rule and conditional denominator; call alternative thresholds sensitivity scenarios. Validate representation before interpreting waiting-time differences as access-to-attorney differences. Align agent-ID/name grouping for concentration figures. Evidence: `47b1aa0c`, `5c5b3281`; L0–L1 R15.

### R09 — High | §9 U34/U103: expedite events are still described as requests

**Issue:** The headline calls the November 2018 decline a fall in requests, then supports continuity with **97.82%/99.55%** either-source rates for priority-claiming marks. U103 distinguishes those marks, non-priority IP RAPID events and additional register events whose meaning remains unresolved. Combining them recreates the ambiguity that the later observation tried to resolve.

**Action:** Summarise the three series separately. Describe the priority-mark recording change as an event-source change; restrict request comparisons to the explicitly defined request series. Keep OQ6 attached to the additional register events and avoid declaring all expedites comparable across 2018. Evidence: `93e8da39`; L0–L1 R32.

### R10 — High | §9 U36 and Stage 2 item 3: survival is presented as renewal and value

**Issue:** The **46.9%–56.4%** figures are estimated survival at ten years in selected recorded cohorts, not directly observed renewal rates. The median lifetime comparison also depends on cohort eligibility, historical recording and censoring. Stage 2's “private value” framing is stronger than U36's explicit distinction between register lifetimes and value.

**Action:** Use “estimated survival of eligible recorded rights”, with cohort dates, exclusions and censoring cutoff. Treat lifetime as a candidate proxy requiring validation; retain regime and recording limitations before interpreting renewal behaviour or economic value. Evidence: `c7c3060d`, `93d19271`; L0–L1 R20–R22.

### R11 — High | §9 U93/U94: family and citation measures lose their units and limits

**Issue:** The **6 versus 2 offices** and **6 versus 1 citing families** summaries omit FY2010–FY2019 and the repetition of family attributes across applications. U92 reports **23.14%** sharing a family with another Australian application. The citation window concerns citing families first filed within five years of the target family's first priority, not necessarily citations received within five years. U115 later raises coverage/matching concerns that the summary does not carry forward.

**Action:** State the period, right-weighted unit, exact citation-window definition and snapshot limitations. Deduplicate for family-level questions and retain coverage sensitivity. Describe reach/citations as candidate indicators, not established measures of private value or research use. Evidence: `88373402`, `ff656ac6`, `34710b37`; L0–L1 R25–R26, L4 R24/R26.

### R12 — High | §9 U89/U90: “exactly” contradicts the evidence in the same row

**Issue:** The claimed exact PCT match is accompanied by ratios **0.981–1.007**: approximately **1.9% below to 0.7% above** WIPO. Aggregate agreement does not validate every link. The route account also omits that categories are assigned by precedence, so “direct” means no higher-priority route was identified, not verified absence of priority claims.

**Action:** Say “close aggregate agreement over 1995–2024”, retaining the measured range and exceptions. Define route precedence and treat the FY2026 direct-category increase as a recording/behaviour question pending validation. Evidence: `bfd682c6`, `5dfc510b`; L0–L1 R23–R24.

### R13 — High | §9 U95/U96 and Stage 2 item 8: inventor address becomes place of invention

**Issue:** “Made here” upgrades a recorded inventor-country flag into a location-of-invention claim. **94.47% versus 0.85%** applies to the eligible known-country subset in FY2017–FY2026, while **56.98%** coverage describes Australian-holder-selected patents in the 2010s. Those periods and denominators differ. Missing country information is selective, particularly for Australia-only records.

**Action:** Say “has a recorded family inventor with an Australian address”, and state the selected publication, period and known-country denominator. Separate known Australian, fully known overseas and unresolved cases. Frame Stage 2 around inventor/holder addresses unless actual invention locations can be established. Evidence: `fa3bcc91`; L0–L1 R27–R28.

### R14 — High | §9 U97/U105–U107: benchmark agreement does not validate gender estimates

**Issue:** “Match … for Australia only” overlooks several other countries within two percentage points and Australia's **2.8-point** difference in 2023. The comparison uses different periods/weighting. The provisional percentages **21.24%/15.57%** concern inventor entries with usable name estimates, not observed gender or all unique inventors; recent missing inventor names are material.

**Action:** Describe approximate benchmark agreement with unresolved comparability. Retain name-estimation and naming-coverage caveats beside every percentage, including repeated entries and the applicant-country proxy for provisionals. Make the gender-analysis decision conditional on coverage/validation, rather than treating aggregate agreement as approval. Evidence: `fa3bcc91`, `1bd5af15`; L0–L1 R29–R30.

## Firms and places

### R15 — High | §9 U41/U45/U100/U101 and U44: firm populations and bounds are overstated

**Issue:** **50,790** is the IPLORD-only category, not all IPLORD-linked ABNs absent from IP RAPID; the earlier audit's sum across combinations is **52,949**. **19,730** represents first observed linked trade mark filings, not verified first-ever filing. Linkage percentages count eligible applications, not distinct firms, and filled coverage still falls from **92.3% to 90.9%**. The **55.3%** concentration result is limited to attributed standard applications in the selected lens.

**Action:** State those populations explicitly and replace guaranteed “lower bounds” with recorded counts under stated linkage rules unless the required assumptions are verified. Harmonise the filer definition across analyses before downstream comparisons; missing older links can misclassify repeat filers as entrants. Evidence: `7466d4dd`, `ca4d2541`, `02e6ebb8`, `93e8da39`; L2 R46–R51/R55.

### R16 — High | §9 U52/U53: a model-specific departure is called “far more than chance”

**Issue:** The funnel result depends on a common-rate Poisson benchmark, geographic matching and population denominators. It cannot exclude all chance or allocation effects. The **68.2%–72.5%** range combines postal areas and postal-area pools labelled by SA3. Neither the departure nor persistence after pooling establishes that negative-binomial modelling is sufficient.

**Action:** Name the benchmark and report each geography separately. Retain the concentration statistic as descriptive, but present model choice as a Stage 2 assessment with denominator, clustering and geographic-allocation checks. Describe the pools as approximations rather than exact SA3 totals. Evidence: `d942b235`, `199a0496`; L3 R12–R14/R32.

### R17 — High | §9 U54 and Stage 2 item 4: “never filed IP” is unsupported

**Issue:** **50.7%** concerns **17,627 active R&D claimant ABNs matched to postal areas** without counted founding-applicant filings. Missing links, historical coverage and inconsistent propagation of register-filled ABNs can produce apparent non-filers. The measure also excludes acquired rights and IP activity outside the counted application types.

**Action:** Say “50.7% had no filing linked under the current attribution rules”, preserving the active/matched denominator. Reconcile filled ABNs and historical source membership before constructing a non-filer group. Replace “missing filers” with a neutral candidate group whose recording coverage still needs checking. Evidence: `3db9f6bc`; L3 R15, L2 R47–R50.

### R18 — Medium | §9 U56/U57 and Stage 2 item 5: source and geographic caveats are too compressed

**Issue:** **0.742** is a national CABEE/ABR ratio; **0.988** is an area-rank correlation. Neither makes the different business populations interchangeable. Choosing ABR totals beside a CABEE business mix needs justification. The **10.9%** exact Census reconciliation statistic does not by itself establish every discrepancy's cause or guarantee that shares of grouped cells are reliable. Later historical Census values are allocated estimates, not direct observations in each postal area.

**Action:** Label each statistic's unit, reference date and population. Keep business universes separate unless reconciled; retain allocation, small-cell and perturbation qualifications for the proposed area analysis. Do not imply that aggregation into shares alone resolves measurement limitations. Evidence: U56–U57/U118; L3 R18–R21/R29.

## National, industry and institution summaries

### R19 — High | §9 U64/U67: reconciliation errors become a blanket reliability claim

**Issue:** “Within 1.5%” conflicts with the resident-patent ratio **0.907 in 2008**, a **9.3% shortfall**. The correct displayed range is **0.907–1.015**. WDI/WIPO exact agreement concerns their combined applicant total; it is not independent validation of each origin split. A chosen post-1995 comparison window does not establish that every WIPO country series is reliable from that date.

**Action:** Correct the range, retain the 2008 discrepancy as an unresolved lead, and state which series/period each reconciliation supports. Treat 1995 as an analytical restriction supported by the displayed coverage diagnostics, not a universal quality guarantee. Evidence: `ef6e0a23`, `7d095977`, `be1b0abc`; L4 R04–R05/R11–R12.

### R20 — Medium | §9 U65/U66/U70: endpoints, ranks and rounded shares need dates and units

**Issue:** “Fallen since 2008” suggests an uninterrupted decline rather than a lower later R&D intensity. The rankings omit indicator years and reporting-country qualifications, while “exports” blurs total exports and high-technology measures. China's and Australia's **8.3%** shares establish rounded parity, not exact equality. **76.1% abroad** counts application events across offices, not the proportion of Australian inventions taken overseas.

**Action:** Attach measure, year and reporting denominator to each rank and endpoint. Say “lower than its 2008 peak” and “both approximately 8.3% in 2024”. Define the overseas application-event denominator; keep country comparisons distinct from invention- or applicant-level conclusions. Evidence: `1b5570dd`, `2ad2808d`, `2bd602eb`; L4 R08/R10/R18/R30.

### R21 — High | §9 U75 and Stage 2 item 7: the crosswalk decision is both overstated and stale

**Issue:** “Divisions near certain” mistakes concentrated allocation weights for classification accuracy. The services crosswalk is no longer merely a future choice: U114 already compares it, with manufacturing **90.63% versus 79.67%** for FY2016–FY2025. The older **90.78%** uses FY2017–FY2026. IP per business would also combine technology-based allocations, including overseas applications, with Australian business counts classified by business activity.

**Action:** Retain the chosen no-services specification explicitly and link the completed sensitivity analysis, using matched periods for comparisons. Replace certainty with conditional allocation concentration. Define any later ratio as allocated IP relative to a stated business stock, not patenting propensity of firms in that industry. Distinguish the innovation measures updated in U119. Evidence: `a2da31f2`, `84a55ef1`, `7dcf4714`; L6 R03–R04/R10/R16.

### R22 — Medium | §9 U81 and Stage 2 item 9: company involvement is not exclusive filing through companies

**Issue:** UNSW's **96.5%** measures applications involving a listed company among founding parties; the university can also be named. It does not quantify how many applications would be lost by excluding companies. The summary also drops the selected, historically consolidated institutional roster and the distinction between co-filing and an independent industry partnership.

**Action:** Use “company involved” and separate university-only, company-only and joint records before quantifying incremental recovery. Specify institutional roster and periods. For grant/co-filing comparisons, distinguish related entities from independent partners and align their counting units and time bases. Evidence: `4a2fb2a5`, `6003c09f`, `c5190cd9`; L7 R02/R08/R12.

### R23 — High | §9 U85 and Stage 2 item 9: US patent citations become evidence of foreign invention

**Issue:** **93.6%** is the complement of citations with a defined Australian applicant/inventor flag, within summed institution-attributed US patent citations. It is not a worldwide share of research use or proof that every remaining invention lacks an Australian connection. U121 later identifies omitted/unresolved-ID works, without demonstrating that shares or institutional rankings remain unchanged.

**Action:** Report the positive **6.40% recorded Australian-link share**, define unknown-country treatment and overlapping institutional credits, and retain US-only scope. Add U121's coverage limitation and require sensitivity checks before interpreting research-to-invention pathways or rankings. Evidence: `28a93a93`, `0632bf39`, `bae467f5`; L7 R05/R13/R19–R21.

### R24 — High | §9 U87: postcode percentages change units and omit an unmatched category

**Issue:** **71.58%** is calculated from application/category rows, not distinct postcodes, with possible cross-institution-type duplication. **50.34%** is only the unmatched delivery-range category: adding nine other unmatched university applications gives **751/1,474 = 50.95%**, among applications with a known founder postcode. That selected founder's postcode need not be the institution's address.

**Action:** Deduplicate the overall institutional share by application; label each category and denominator correctly. Report total unmatched and missing-postcode counts separately. Before reallocating through institutional locations, establish whose address is being replaced and use an explicit, dated allocation rule. Evidence: `5689b0df`, `7995cabf`; L7 R16–R18.

## Policy interpretation and downstream use

### R25 — High | §9 U23/U28 and Stage 2 item 1: policy timing is stronger than the design supports

**Issue:** “Rushes”, “steps” and “pauses” classify raw event-centred patterns as responses. The **−98.4%** expiry change uses only January–June 1995 before July commencement, despite the supporting table's “12 months before” label. “Series start where complete” likewise upgrades chosen recording windows to verified completeness. Placebo dates alone do not establish a natural experiment or isolate policy effects from trends, anticipation, seasonality and recording changes.

**Action:** Describe the observed changes around dated events, and correct the expiry baseline to six observed months or omit that comparison. State source-specific eligibility and window coverage. Treat causal analysis as conditional on a defensible design; align the now-available fee history, event dates, affected populations and measures before testing. Evidence: `b86d1582`, `280d6566`, `4191f6dd`, `525a6bb3`; L5 R04/R14–R16/R23–R24.

## Review boundary and reproducibility

This report contains **25 issue/action entries**. It assesses the summary's fidelity to the notebook, informed by the earlier audits; it does not certify every assertion in those audits or establish defects in uninspected builders or sources. The one §8 code cell has execution count **168**, one saved table output and no saved error. Neither target section contains a chart. Numerical corrections above use saved tables or arithmetic on displayed values; no model training, data rebuild or notebook execution was performed. No notebook or repository changes were made.

**Earlier audit references:** L0–L1 = `Stage01_L0-L1_Audit.md` (the completed R01–R44 report); L2–L6 = the corresponding `Stage01_L2_Audit.md` through `Stage01_L6_Audit.md` in `analysis/GPT-audit/261030/`; L7 = `Stage01_L7_Audit.md`, the supplied 31 October report. Lens-qualified references avoid ambiguity from reused R-numbers.

**Evidence locators:** §8 is cell `c65816b4`; its profiling code/output is `fd966a12`; all §9 findings and its handover are in `2f712bb5`. Additional cell IDs identify supporting notebook evidence, not execution counts. U-numbers and section headings are searchable. Internal Q/OQ/ADR identifiers should be given short descriptions or working links when the summary is revised, so the handover can be read without reconstructing project history.

Repository commit: `7513aac9c68a345c5c1dd684c31fab6c633c763e`.

Downloaded notebook SHA-256: `1d5e51a699b82091788c75fdaff6d2706a24ba6a91df21877799677a8a357cdb`.
