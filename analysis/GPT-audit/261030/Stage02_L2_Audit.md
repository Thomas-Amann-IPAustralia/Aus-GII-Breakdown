# Stage 2 notebook audit: Lens 2 reviewed in depth

**Reviewed:** 2 November 2026. **Source:** [02_bivariate.ipynb](https://github.com/Thomas-Amann-IPAustralia/Aus-GII-Breakdown/blob/1581223dc2fbb2ce1a1c26fab77a14f459eb023a/analysis/notebooks/02_bivariate.ipynb), downloaded from `main` for this review.

**Provenance:** Follows the thematic sections, priorities and **Issue / Action** format of the Stage 1 audits in `analysis/GPT-audit/261030/`. This is a separate, self-contained review; R-numbers are local to this report. Earlier findings are cited with their lens to avoid ambiguity.

**Scope of this pass:** Only §2, including §§2.0–2.7 and B20–B26/B50–B51: all **27 cells**, including **12 code cells**, their saved tables and **three embedded figures**. The introduction/setup and qualifications elsewhere relevant to these claims were consulted. All eight Stage 1 audit reports were screened for relevant findings, with particular attention to Firms, Places, IP rights and the Stage 1 summary. The GitHub Pages website was not assessed. The notebook was not re-executed; underlying datasets, imported helpers and ADR implementations were not independently audited.

**Overall finding:** Most quoted numbers agree with the saved outputs, but several conclusions do not match what was calculated. The most consequential issues are inconsistent filing definitions, an incorrect IPLORD denominator, age filters and date arithmetic that do not implement the stated population, accumulated contract values described as contract sizes, and unsupported claims that size or reach have been ruled out as explanations. The later WGEA addition has not been fully incorporated into earlier statements.

**Priority:** **High** = affects interpretation, validity or downstream use; **Medium** = correct before relying on or circulating findings. Implementation-dependent concerns are identified as checks, not established defects. Apply corrections to §2.7 as well as the original observations.

**Read first:** R04 and R08–R10 concern apparent non-filers; R12–R13 concern contracts; R15–R20 concern age and ownership; R21–R26 concern the WGEA update.

## Scope, screening and definitions

### R01 — High | §§2.3/2.6: conditional comparisons extend beyond two-variable analysis

**Issue:** B24 compares filing status × contract value within entity groups; B51 compares R&D expenditure × patent counts within size bands. These involve a third variable. B26 also compares age × ownership status across periods and invokes reach to dismiss an explanation. The within-band results do not establish independent effects. Separate pairwise tables or a list of candidate third factors are not, by themselves, a fitted multivariable analysis.

**Action:** Identify these as stratified checks that extend the strict bivariate scope, or move adjustment claims to Stage 3. Retain descriptive conditional associations without claiming that entity type, size or reach has been controlled adequately. Evidence: `162ee072`, `18df0008`, `6880dc9f`, `efb8d829`.

### R02 — High | Screening rules applied to Lens 2: association measures are not interchangeable

**Issue:** The introduction presents Spearman's rho, rank correlation ratio and corrected Cramér's V as one equivalent strength scale, including an exact binary-variable equivalence. Their definitions and corrections differ; common 0–1 ranges do not make 0.1 comparable in every case. Spearman describes monotonic association, not association “in any shape”. B24 additionally applies negligible/lead language to rank-biserial correlations, another scale.

**Action:** Describe each measure and use measure-specific, justified decision rules. Keep signs where meaningful, distinguish screening conventions from substantive importance, and do not rank unlike measures as equivalent effects. Evidence: `0a9fee61`, `c0c3cee3`, `e82d4b3e`.

### R03 — Medium | B20: rank agreement is not near-identical effect sizes or external replication

**Issue:** The 0.962 compares the ordering of pair strengths, not their numerical agreement. The leading expenditure–income association is 0.485 in discovery versus 0.346 in replication. Both halves share source selection and measurement limitations; related ABNs may also span halves. Pair-specific usable counts are absent from the lead table, although the nominal screen samples are much larger than some source intersections.

**Action:** Call this internal split-sample consistency, retain the notebook's existing weaker-test caveat, and report absolute strength differences and usable counts. Explain sampling, missingness and any group dependence; retain all verdict categories, including eight pairs with too few rows. Evidence: `44597b98`, `c0c3cee3`, `2acf090e`.

### R04 — High | B22–B24/B50: “filed IP” changes definition within the lens

**Issue:** B22/B24 use the union of positive `ip_filed_total` and positive per-type counts. B23 uses only `ip_filed_total == 0` for non-filers; B50 uses only positive per-type counts. These are not demonstrated complements or equivalent populations. Stage 1 already identified attribution/linkage differences. The opening “lower bounds” rule also overstates verification, and its 50,790 is the IPLORD-only category, not all ABNs linked by IPLORD but absent from IP RAPID.

**Action:** Define one intended recorded-filing flag and reconcile all three alternatives by ABN. Regenerate affected tables, figures and summaries; retain separate measures only with explicit attribution labels. Distinguish zeros from unresolved historical links and use recorded counts rather than guaranteed bounds. Evidence: `44597b98`, `dff03f5c`, `c9f6c794`, `d25160cd`, `9f01d1f9`; Stage 1 L2 R46–R50, S8–S9 R15/R17.

### R05 — Medium | B21: interpretations exceed the screen's measures

**Issue:** “Firms that hold patents also hold designs” refers to flags labelled applicant **or** owner. “Government suppliers cluster in the ACT” is based on median contracts per lens ABN, not a geographic distribution of suppliers. “Larger firms” is not the variable in the expenditure–income pair, and register mechanics/source selection are plausible explanations, not decomposed causes. Several “followed up below” pairs receive no dedicated follow-up.

**Action:** Name the measured flags and selected population. Describe the ACT result as a difference in recorded contract counts per lens ABN; label size and selection mechanisms as hypotheses. Either supply the promised follow-ups or identify them as screen-only leads. Evidence: `c0c3cee3`, `2acf090e`.

## Filing profiles and apparent non-filers

### R06 — High | B22/B23: the age grouping can classify missing ages as oldest

**Issue:** The shared `AGE` expression ends with `ELSE '20 years or more'`. Any record with unknown `age_years` and no true truncation flag reaches that category. Stage 1 found undated ABNs with `age_truncated = False`; the current section does not show whether eligible claimants/suppliers include them. The “20 years or more” group also mixes a different dating basis from the separately flagged older-registration group.

**Action:** Handle missing dates/ages explicitly before numeric bands, show affected counts within each population, and describe the truncation flag's actual meaning. Recalculate age gradients if any unknown ages were assigned to the oldest band. Evidence: `dff03f5c`, `c9f6c794`; Stage 1 L2 R54.

### R07 — Medium | B22: geographic wording is stronger than the tabulations

**Issue:** Suppliers' filing share does not rise “steadily”: discovery falls from 23.1% in IRSAD decile 2 to 19.4% in decile 4. The 0.806/0.782 correlations use ten decile-level percentages, not individual ABNs. “Once a firm does R&D, where it is registered does not go with filing” generalises from claimants and IRSAD, despite displayed remoteness differences. The claim that companies, older firms and city firms are larger is not tested here.

**Action:** Say the supplier share shows an overall positive decile gradient, not a monotonic rise. Label the ten-group correlation and report ABN-level contrasts separately. Limit the claimant finding to no consistent IRSAD gradient; retain remoteness, known-geography denominators and registered-address qualifications. Treat size as a candidate explanation. Evidence: `dff03f5c`, `d31b91bb`, `1d5add86`; Stage 1 L2 R60–R61.

### R08 — High | B23: the IPLORD percentage uses the wrong stated denominator

**Issue:** `iplord` sums IPLORD membership across **all** claimants in each group, then divides by all group members. The column “of whom IPLORD links to IP (%)” and prose instead describe the share of missing filers linked by IPLORD. Thus 54.3%/56.2% are not established percentages of the oldest missing filers. The query does not establish the intersection of IPLORD membership and zero founding-applicant filings.

**Action:** Calculate `in_iplord AND ip_filed_total == 0`, divide by the corresponding missing-filer count, and display both numerator and denominator. Reconcile register-filled evidence before using that intersection to interpret non-filing. Replace every affected percentage and conclusion. Evidence: `5db69f06`, `472585cd`.

### R09 — High | B23: “never filed” and “close to exact” are unsupported

**Issue:** Zero attributed applications does not establish lifetime non-filing or absence of other IP activity. The introductory caveat does not repair the repeated “never” labels in the chart and headline. IPLORD's coverage ends at FY2020: no IPLORD links among recently registered entities cannot validate their zero counts. Neither unobserved filing histories nor attribution errors are measured, so exactness and an unconditional upper-bound claim are not demonstrated.

**Action:** Use “no application linked under the stated rules”, distinguishing unresolved links, acquired rights and unmeasured IP. Check recent and historical linkage coverage directly; remove the young-firm exactness claim. Keep source-window limitations beside the figure. Evidence: `c8c7251c`, `c9f6c794`, `472585cd`; Stage 1 L3 R15, S8–S9 R17.

### R10 — High | B23: marginal rates do not establish a joint target group or intervention benefit

**Issue:** Separate age and entity tables do not show that apparent non-filers are jointly “mostly young private companies”. High within-group prevalence is not the group's share of all non-filers: the under-three groups contain only 283 claimants, versus 8,470 aged three to ten. “Where an intervention could add most” requires evidence about unmet need, suitable protection and likely benefit, none of which is measured. “Wherever they are” also obscures the regional differences reported immediately above.

**Action:** After correcting filing status, show the joint composition and counts if a target-group description is needed. Define “young”. Present this as a group for further investigation, not demonstrated missed protection or an intervention opportunity. Evidence: `5db69f06`, `472585cd`.

## Expenditure, contracts and income

### R11 — High | B21/B23/B24: monetary and filing measures have unequal observation windows

**Issue:** Average R&D expenditure across observed claimant years, latest tax income, accumulated contract values and historical application counts are compared without aligned periods. Participation duration and differing report years can contribute to the associations. B23's “recorded spend” sample actually requires a **positive mean** and contains 17,514 claimants, compared with B22's 17,643 active claimants; the 129 exclusions are not explained locally.

**Action:** State each source window, report-year distribution, averaging denominator and exclusion count. Describe reported R&D expenditure, not tax benefits. For stronger comparisons, align annual activity and exposure periods; otherwise retain the mixed-period qualification and investigate sensitivity. Evidence: `c0c3cee3`, `c9f6c794`, `d25160cd`; Stage 1 L2 R57–R59.

### R12 — High | B24: total supplier value is described as individual contract size

**Issue:** `austender_value` is an accumulated supplier value at latest amendments. Its median of $273,400 versus $113,800 is not the median size of individual contracts. More contracts can itself produce a larger total, so “win more and larger contracts” states two conclusions when only counts and accumulated values are shown. Recorded contract values are not actual payments or procurement success rates.

**Action:** Say suppliers with linked filings have higher recorded contract counts and higher accumulated contract value over the stated window. Analyse contract-level values separately if individual size is intended, with amendment handling and exposure documented. Keep the existing non-causal qualification. Evidence: `d25160cd`, `e82d4b3e`, `67eaba22`; Stage 1 L2 R58/R68.

### R13 — High | B24: “within every kind of entity” is not supported

**Issue:** The stratified code examines **value only**, not contract counts. It retains five entity groups with at least 50 records in each filing-status group per half; sole traders, partnerships and super funds are absent. Trusts have only 0.044/0.065 rank-biserial associations, explicitly called negligible in the body. The headline and summary nevertheless generalise both outcomes across entity groups.

**Action:** Restrict the statement to higher median accumulated value in the five displayed groups, noting the small trust association. Show excluded groups/counts and uncertainty for within-group contrasts. Test stratified contract counts separately before claiming that pattern also persists. Evidence: `162ee072`, `e82d4b3e`, `67eaba22`.

### R14 — Medium | B24 / §2.7: the income result is qualified correctly only in part

**Issue:** The discovery income difference is $27.82m with an entirely positive interval ($13.38m–$45.04m); the replication difference is $3.75m with an interval spanning zero. Small rank associations and this instability justify caution, but do not demonstrate no income relationship. The lens summary omits the income comparison despite it being a planned pair.

**Action:** Report a small, inconsistent association across the halves and preserve both intervals. Add the income result and its limited inference to §2.7 without turning failure to meet a screening rule into evidence of equivalence. Evidence: `d25160cd`, `e82d4b3e`, `67eaba22`.

## First filing, age and recorded ownership

### R15 — High | B25/B26: the code does not apply the stated post-2000 restriction

**Issue:** Both analyses use `NOT age_truncated`, not `year(first_seen) >= 2001`. These conditions are not demonstrated equivalent. B26 makes the mismatch conclusive: **4,341 of 7,166** earlier-period records (60.6%) are in the ten-plus-year band. With first registration from 2001 and filing no later than FY2011, its formula cannot produce age ten. B25's visible pooled 25-year tail likewise conflicts with the stated range under its formula.

**Action:** Decide whether the intended sample is all records with an unflagged date or only registrations from 2001. Implement that exact filter, show date ranges and exclusions, then regenerate both analyses and captions. Do not describe an unflagged registration age as “real” business age. Evidence: `3e0e89d9`, `3f4b06bf`, `f0884744`, `18df0008`; Stage 1 L2 R54.

### R16 — High | B25/B26: date arithmetic and negative ages distort the age bands

**Issue:** Under end-year financial-year labels, `fy - 0.5` represents approximately the **start**, not the middle, of the July–June year. B25 retains ages between −1 and zero and counts them in “within the first year”. B26 uses only the calendar year of registration, unlike B25's day-based date, and permits registration in the filing FY's calendar year without checking event order. These approximations can move observations across the under-two and other boundaries.

**Action:** Prefer actual filing and registration dates. If only FY is available, construct the correct midpoint or an age interval and disclose approximation uncertainty. Report negative/inconsistent dates separately, make the two calculations consistent, and rerun threshold-sensitive results. Label B25's vertical axis as probability density, not a direct share per bin. Evidence: `3f4b06bf`, `18df0008`.

### R17 — High | B25: first observed filing is not true entry or a guaranteed age bound

**Issue:** Missing earlier links can make first observed filing later than true first filing, while registration dates and FY approximations introduce other errors. The resulting ages are not guaranteed lower bounds. The analysis also conditions on an observed first filing in FY2010–FY2026 and excludes firms without one. The three right-type groups differ, so their median ordering does not show that an individual firm typically files a trade mark before a patent/design.

**Action:** Describe elapsed time from recorded registration to first observed linked filing among each eligible right-type group. State coverage, exclusions and cohort selection. Use matched firms for within-firm sequencing and an appropriate time-to-event design including non-filers if studying entry timing. Evidence: `3e0e89d9`, `3f4b06bf`, `8926adb5`; Stage 1 L2 R49–R50/R54.

### R18 — High | B26: the unit switches from ABNs to patent applications

**Issue:** The rights-to-firms join counts rights with `count(*)`. Prolific ABNs contribute repeatedly; linked family records may also repeat. The reported percentages therefore concern selected patent applications, not the share of young firms whose IP changes ownership. Ordinary Wilson intervals do not account for dependence within firms/families. Different filing years also have unequal time to reach the current ownership endpoint.

**Action:** Label the application-weighted unit and show distinct ABNs/families per band. Use a firm-level outcome if that is the research question; otherwise assess clustered uncertainty and concentration sensitivity. Compare a common follow-up window for event-based claims. Evidence: `18df0008`, `ec3ec3a0`; Stage 1 L0–L1 R25.

### R19 — High | B26: ownership endpoints and selected ABN links are over-interpreted

**Issue:** `founding_australian` plus `NOT australian_applicant` identifies origin classifications at two endpoints, not a verified transfer, acquisition, founder emigration or loss of economic returns. The join uses `r.filer_abn`, whereas the section's general description promises register-filled attribution; it does not show linkage coverage or ensure that the linked ABN is the Australian founding party in a multi-party record.

**Action:** Use “Australian-founding applications with no recorded current Australian holder” and state the snapshot and missing-holder exclusions. Reconcile the ABN field and party alignment with the filled attribution used elsewhere. Keep overseas acquisition and founder relocation as untested hypotheses, not observed mechanisms. Evidence: `44597b98`, `18df0008`, `ec3ec3a0`; Stage 1 L0–L1 R16, L2 R51, S8–S9 R07.

### R20 — High | B26: reach has not been ruled out as an explanation

**Issue:** Marginal five-plus-office shares do not test ownership differences within reach groups, so “reach does not explain the gap” is unsupported. The later youngest group is also **20.62%** wide, slightly above the oldest group's **20.16%**, contrary to a blanket youngest-versus-older ordering. Missing reach is included in the denominator without a separate unknown category. B55's warning about older Australian family coverage is not carried into this FY2003–FY2011 comparison.

**Action:** Report the actual marginal shares and unknown reach counts. Withdraw the explanatory exclusion; assess reach on comparable records with suitable stratification/adjustment in Stage 3. Carry the historical coverage caveat into B26 without treating B55's proposed cutoff as validated. Compare age-band differences directly before claiming the youngest group is distinctly higher than every other group. Evidence: `18df0008`, `ec3ec3a0`, `b3ed6e03`; Stage 1 L4 R24–R26.

## WGEA addition, replication and amendments

### R21 — High | B50/B51: “employers of 100 or more” is not the verified population

**Issue:** The query selects `wgea_year IS NOT NULL`, not headcount of at least 100. Stage 1 identified employee counts as low as one, incomplete source-to-lens matching, and an unresolved reporting-group versus ABN unit. Thus these are matched WGEA-report ABNs in a selected lens, not a demonstrated representative census of all large employers. Group-level headcount attached to individual ABNs could also change the meaning of size–filing comparisons.

**Action:** Use the actual matched-record population, explain below-threshold records, and verify report/ABN/group relationships before describing employer size. Show matching exclusions and coverage; reserve generalisation to all eligible employers for evidence that supports it. Evidence: `00f6b33d`, `9f01d1f9`, `efb8d829`; Stage 1 L2 R62–R63/R66.

### R22 — High | B50/B51: latest employer attributes are paired with historical filing

**Issue:** Latest available headcount/industry is compared with any historical application or cumulative counts. Stage 1 identified 1,117 matched ABNs with older reports. “Filing rises with size” can therefore be read as current filing propensity, although the analysis does not align employer size, industry and filing dates or measure changes within employers.

**Action:** State the reporting-year mix and historical filing window. Describe the association as latest recorded employer attributes versus recorded historical filing; align periods and exposure before interpreting contemporary propensity or changes. Evidence: `9f01d1f9`, `ae9897e6`, `6880dc9f`, `efb8d829`; Stage 1 L2 R64.

### R23 — High | B51: “industry sorts patenting far more than size” lacks a comparable measure

**Issue:** The claim compares division-specific filing shares with size-band shares/headcount correlations. Differences between selected extremes are not like-for-like measures of explanatory importance, and size and industry may be associated. The notebook calculates neither a common association measure nor their separate contributions on an identical sample.

**Action:** Describe the displayed industry variation without ranking its importance against size. If the comparison matters, use comparable summaries on the same eligible ABNs, with uncertainty; assess independent contributions in Stage 3. Evidence: `ae9897e6`, `efb8d829`.

### R24 — High | B51: the size check changes B23's population and expenditure measure

**Issue:** B23 uses active claimants with positive **mean** R&D expenditure. B51 uses WGEA-matched claimants with non-null **latest** expenditure, without the same active/positive filters. Its pooled rho of 0.172 is therefore not a like-for-like recheck of 0.120/0.128. Within-band rhos range 0.105–0.253, exceed the pooled value in two bands, and have no intervals; the largest band has only 11 records and no estimate. Broad bands leave residual size variation.

**Action:** First reproduce B23's definition on the WGEA overlap; change measure and eligibility one at a time. Report uncertainty and omitted-band limits. Replace “size does not explain” with the observed within-band associations; do not rule out size or selection from this check. Evidence: `c9f6c794`, `6880dc9f`, `efb8d829`.

### R25 — Medium | B50/B51 / §2.7: replication labels and denominators need correction

**Issue:** B50's headcount correlations are below 0.1 in both halves, so they fail the stated screen rule despite positive full-sample extreme-band differences. B51's division rates and within-size correlations are calculated on the full WGEA subset: “within bands” in the replication column is not replication. B50 names 7,126 ABNs, but the five size bands total **7,120**; six unknown-band records are omitted without a local note.

**Action:** Distinguish exploratory/planned-pair findings from screen-qualified leads. Mark the division and within-band results as not split-sample replicated unless that check is added. Report the six exclusions and pair-specific eligible counts; give intervals for the correlations where they inform a conclusion. Evidence: `9f01d1f9`, `ae9897e6`, `6880dc9f`, `67eaba22`; Stage 1 L2 R67.

### R26 — Medium | B24 → B50/B51 → §2.7: later data has not replaced stale availability claims

**Issue:** B24 and the closing data-gap paragraph still say size/industry are not in the lens, although §2.6 adds them for matched WGEA records. The screen figure shows neither WGEA size nor industry, while “every pair” and the completion language are unqualified. B51's statement that small firms still lack the fields is also too absolute given the sub-100 records identified in Stage 1.

**Action:** State which fields are available for which ABNs and years, and which remain missing. Refresh or explicitly date the original screen and describe the supplement's coverage rather than implying a comprehensive updated screen. Rebuild §2.7 from the corrected findings, preserving exceptions and unresolved checks. Evidence: `c0c3cee3`, `e82d4b3e`, `efb8d829`, `67eaba22`; Stage 1 L2 R62/R66/R69–R70.

## Evidence and presentation

### R27 — Medium | Tables and figures: key qualifications are absent when outputs stand alone

**Issue:** Lead directions and third factors are truncated to 90 characters; the heatmap has no nearby key for outlines, crosses and hatching. B23's figure omits the register from its source caption and labels counted zeros as never filing. B25's prominent final histogram spike pools the upper tail and is not a mode at age 25. Several planned-pair correlations and subgroup differences lack the intervals promised in the introduction.

**Action:** Display complete lead details and a symbol key. Put sample, attribution, period, missingness and source qualifications in captions; distinguish pooled overflow from an ordinary histogram bin. Add the relevant intervals or narrow the methodological promise. Expand internal acronyms/references briefly so the section remains intelligible on its own. Evidence: `7455cfd8`, `c0c3cee3`, `c9f6c794`, `3f4b06bf`, `6880dc9f`.

## Review boundary and reproducibility

This report contains **27 issue/action entries**. Findings are based on displayed notebook code, saved tables/figures and commentary, informed by the earlier audits. Proposed recalculations are actions, not results claimed to have been run. All 12 Lens 2 code cells have saved outputs, sequential execution counts **24–35**, and no saved error output; that does not establish reproducibility against current data and dependencies. No notebook, source-code or website changes were made.

**Earlier audit references:** L0–L1 = `Stage01_L0-L1_Audit.md`; L2–L7 = `Stage01_L2_Audit.md` through `Stage01_L7_Audit.md`; S8–S9 = `Stage01_S8-S9_Audit.md`, all in `analysis/GPT-audit/261030/`. Prior findings were treated as context and checked against the present section where possible, not assumed to prove unseen implementation defects.

**Evidence locators:** B-numbers and headings are searchable. Eight-character identifiers refer to stable notebook JSON cell IDs, not execution counts. Numerical examples use saved outputs or direct arithmetic on displayed counts. Matters outside Lens 2 were consulted only to identify definitions or qualifications affecting this lens.

Repository commit: `1581223dc2fbb2ce1a1c26fab77a14f459eb023a`.

Downloaded notebook SHA-256: `441679240f0e884486b681493f87604fa327223a9ae369fcdd263fd84218ede2`.
