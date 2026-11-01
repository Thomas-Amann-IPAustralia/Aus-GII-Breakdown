# Stage 1 notebook audit: Lens 7 reviewed in depth

**Reviewed:** 31 October 2026. **Source:** [01\_univariate.ipynb](https://github.com/Thomas-Amann-IPAustralia/Aus-GII-Breakdown/blob/main/analysis/notebooks/01_univariate.ipynb), downloaded from `main` on the review date.

**Format:** Follows `analysis/GPT-audit/261030/Stage01_L0-L1_Audit.md`: numbered findings, priority, location, **Issue** and **Action**. R01–R24 are local to this Lens 7 report; cite them as “Lens 7 Rxx” across the series.

**Scope of this pass:** Only §7, including §§7.0–7.9, observations U80–U87 and U121–U122, all 30 cells, all 10 code cells and their saved outputs, and all four embedded figures. The notebook's introductory rules were consulted. The earlier audit was read only to reproduce its format. No GitHub Pages website, underlying datasets, imported helper implementations, external factual sources or other analytical lenses were assessed. The notebook was not re-executed.

**Overall finding:** Most quoted values agree with the saved outputs. The principal weaknesses are overlapping institution counts presented as shares of research, analyses extending beyond one variable, incomplete population and time definitions, and stronger conclusions than the displayed checks support. Later additions reveal limitations that have not been carried back into the earlier observations or their summary. Several numerical and wording errors are directly demonstrable.

**Priority:** **High** = affects interpretation, validity or downstream use; **Medium** = correct before relying on or circulating the findings. Implementation-dependent concerns below are checks, not confirmed defects in unseen code. Apply corrections to §7.9 as well as the original observations.

**Read first:** R05, R12–R13, R16–R20 and R22 concern counting units, coverage or validity. “Descriptive” does not necessarily mean “univariate”. A recorded zero, an unmatched record and an observed absence are different things.

## Scope, coverage and definitions

### R01 — High | Throughout: substantive comparisons exceed the stated univariate scope

**Issue:** The introduction promises “one variable at a time” before relating variables. Lens 7 instead compares citations per work by institution/type (U82, U85), funding and filing by type and time (U83–U84), postcode coverage by institution type (U87), and commercialisation measures across types and years (U122). U121 also extrapolates from a sample with uncertainty intervals. These can be useful analyses, but labelling everything descriptive does not make them univariate.

**Action:** Move substantive relationships and comparisons to Stage 2, or explicitly broaden Stage 1 to include named descriptive-comparison and sampling exceptions. Retain individual distributions, coverage diagnostics and necessary reconciliation checks. Do not classify a simple frequency chart as bivariate merely because it has two axes.

### R02 — High | §7 introduction / U80–U81: the population is a selected, historically consolidated roster

**Issue:** “Australia's research institutions” and “every” university/grant administrator imply demonstrated completeness. The notebook instead describes a reviewed list of 130 ROR identities, leaves completeness open in OQ11 and displays 29 unmatched grants. It also folds predecessors and companies into institutional identities. The 4,810 rows equal 130 × 37 years despite establishment dates reaching 2024 and some inactive ROR records. These are not necessarily 130 separate, operating institutions in every year.

**Action:** Describe the population as the 130 institutions in the reviewed roster. State inclusion rules, snapshot date and treatment of predecessors, mergers, companies and historical classifications. Report unresolved coverage without asserting exhaustiveness. Distinguish a retrospective institutional lineage from the legal organisation operating in a particular year. Evidence: cells `7509bd84`, `f85d7eca`, `43978137`, `4a2fb2a5`.

### R03 — High | §7.0 / U80: populated years do not establish observed coverage

**Issue:** The coverage table finds first/last years using `notna()`. IP and patent-citation fields are 100% populated across the full rectangular panel, so “IP and patent families for every year” can simply describe zero-filled rows. It does not establish source completeness, eligibility before establishment or absence of activity. Conversely, positive counts for 129 institutions do not mean the remaining institution lacks source coverage.

**Action:** Separate eligible years, observed source coverage, matched records, measured zero and missing/unknown values. Display the eligible denominator and source cutoff for each measure. Base Stage 2 windows on those checks, not merely non-null dates. Do not assign substantive zeros to structurally inapplicable years without explanation. Evidence: `f85d7eca`, `6003c09f`.

### R04 — Medium | §7.0 and section checklists: the promised univariate profiles remain incomplete

**Issue:** The overview provides filling rates, distinct values, extrema and the most common value, but little about typical institution-years, spread or tails. Rankings and group totals dominate the subsequent analysis. Commercialisation staffing receives no substantive profile; second-tier patents/designs receive only totals. The “overlap” check displays separate Data61 and CSIRO counts without measuring their intersection. Neither independence nor overlap size follows from those marginals.

**Action:** Add compact distributions for important eligible institution-year measures: zero/missing shares, median, upper quantiles and extreme-record checks. Include staffing and explain which variables are intentionally deferred. Show a work-ID intersection if claiming measured parent–child overlap. Mark checklist items complete only to the extent demonstrated. Evidence: `f85d7eca`, `63f0fe1e`, `2b856046`, `577473a0`.

## Research output, linkage and grants

### R05 — High | U82 / §§7.1, 7.3–7.4: summed institutional credits are presented as distinct output

**Issue:** The section warns against adding works and citations across institutions as though distinct, but §7.1 does exactly that to form totals and percentage denominators. Thus 86.8%, 45.35% and the annual “works, all institutions” are shares/counts of institution-attributed works, with co-authored and parent–child overlaps retained. Similar summation underlies U84's concentration/joint-filing figures and U85's citation/family aggregates. The national filing-share query, by contrast, explicitly deduplicates rights. Adjacent figures therefore use different counting units.

**Action:** Either deduplicate works, citations, rights and families for collective totals, or label the existing results consistently as institutional credits/links. Explain that an item can contribute more than once and that collaboration affects weights. Preserve each institution's own full counts, but distinguish those from collective output. The five leading universities account for about **35.0% of work credits**, rather than an exact third of distinct works. Evidence: `2b856046`, `b357571b`, `28a93a93`.

### R06 — Medium | U80 / U82: harvest limits and citation exposure need clearer wording

**Issue:** “Research output, which OpenAlex gives only from 2010” assigns a limitation of the lens/harvest to the source itself; the displayed check only establishes the lens's coverage. U82's citations-per-work figures pool publication cohorts with different time to accumulate citations, without a citation cutoff or cohort/field qualification. U121 later identifies a scholarly-citation filter in the works harvest, but Lens 7 does not establish whether that filtered harvest also supplies U82's aggregate work counts.

**Action:** Say “the lens contains OpenAlex works from 2010”. State exactly which harvest/filter supplies each measure and whether counts exclude uncited works. Label citation averages with publication years and the observation cutoff; do not imply comparable impact across institutions from unadjusted averages. Treat apparent output growth as growth in recorded work credits until coverage is assessed. Evidence: `6003c09f`, `2b856046`, `3dacd3e3`, `7533ff67`.

### R07 — Medium | U81: linkage validation and unmatched counts are over-generalised

**Issue:** Name-and-ABN matches account for **84.73%** of the 31,528 links, making “almost all” imprecise. The table establishes missing country for 21.19% of name-only patent links, but not the claim that they are “old filings”. The ten displayed ABN-only names cannot validate all ABN-only matches. The unmatched-grant query also uses `NOT IN`, which does not count a null organisation name as unmatched; the stated 29 is not a demonstrated total of all unlinked grants.

**Action:** Report 84.73% explicitly and keep links distinct from unique rights. Show filing-year evidence before calling missing-country records old. Present the names as examples, with complete match-validation results separately. Count null names, unknown identities and unsuccessful links explicitly before giving a total unmatched figure. Evidence: `4a2fb2a5`, `6003c09f`.

### R08 — High | U81: company involvement does not establish the loss if companies were omitted

**Issue:** The company flag is true when **any** founding party matches a listed commercialisation company. A right can also name the university directly. Therefore UNSW's 96.5% company involvement does not establish that excluding companies would leave only 3.5% of its applications. The query includes all patent types and has no explicit filing-period filter, but the prose gives a broad present-tense conclusion about university patenting.

**Action:** Split applications into university-only, company-only and both, and calculate the actual incremental recovery from companies. State the period, patent types and whether company names identify the same legal entity or related entities. Keep the 96.5% as “company involved” unless exclusivity is shown. Evidence: `4a2fb2a5`, `6003c09f`.

### R09 — Medium | U83: “a fifth” and the scheme explanation lack displayed support

**Issue:** The headline gives one overall ARC industry-funding share, but the code reports annual percentages and does not print a pooled percentage or a defined mean. The 9.7% figure for 2017 is not in the displayed selected-year table. “Both move year to year with large schemes” attributes movements without a scheme-level breakdown. The percentages for universities and the Group of Eight concern linked lens funding, not demonstrably every national award.

**Action:** Print the ratio of summed industry funding to summed ARC funding for a specified period, or label a mean of annual shares as such. Display the claimed extrema with their period. Describe variation without assigning it to schemes unless decomposed. Qualify all shares as shares of recorded funding linked to the roster. Evidence: `78eca0d7`, `c23ebe19`.

### R10 — Medium | §7.2 / U83: grant values and latest years need explicit interpretation

**Issue:** The chart correctly distinguishes ARC start year from NHMRC round year, but prose can still read as annual expenditure or currently held funding. The notebook does not explain whether amounts are total multi-year awards, annual allocations or disbursements. The chart includes 2026 values of approximately $1,369 million ARC and $566.7 million NHMRC, while the observation stops at 2025 and provides no coverage status for those endpoints.

**Action:** Define the monetary measure and time assignment next to the table and observation; retain the current-dollar qualification. Identify release/round completeness before interpreting 2026 or comparing its movements. Explain the deliberate exclusion of provisional endpoints, if appropriate, instead of silently omitting them. Evidence: `78eca0d7`, `c23ebe19`.

## Patent applications, citations and contracts

### R11 — Medium | U84: the provisional ratio and trend description need correction

**Issue:** “Universities file 1.8 to 2.7 provisionals per standard application” conflicts with the displayed RMIT **1.58**, Griffith **1.29**, South Australia **1.47** and Western Australia **1.71**. No displayed university reaches 2.7. “Slowly rising” omits the standard share's fall from 7.33% to 6.86%, and the latest fall from 8.96% to 8.59%. The explanation invoking individuals' doubled filing is imported from U8, not demonstrated in Lens 7.

**Action:** State the range for an explicitly defined displayed subset, or calculate it across all eligible universities. Describe a higher long-run share with intervening declines; include the latest partial-period result with a caveat. Present the provisional-share fall as observed, and label its proposed explanation as requiring separate evidence. Ratios of period totals do not establish conversion from provisionals to standard applications. Evidence: `b357571b`, `c5190cd9`.

### R12 — High | §7.3 / U84: period labels, origin and collaboration definitions differ

**Issue:** The last filing-share point is placed at **2027** by `period + 2`, although it covers only 2025–2026. The ranking uses calendar 2017–2026, whereas §7.6 uses FY2017–FY2026. The national share requires a recorded Australian founder, while institutional counts can also include a founder of unknown country. Joint filings show another founding applicant, which need not mean an independent research partner; related companies and institutional co-founders may qualify.

**Action:** Label periods explicitly, marking 2025–2026 as partial and 2026 as observed to the snapshot. Distinguish calendar-year and financial-year windows. Reconcile origin restrictions before comparing the tables. Call the joint-filing variable “another recorded founding applicant” until related entities and partner types are separated; retain collaboration as a proposed proxy, not an established measure. Evidence: `43978137`, `b357571b`, `c5190cd9`, `5689b0df`.

### R13 — High | U85: US citation evidence is overextended to foreign inventions and research use

**Issue:** “Often”, “rarely”, “build on” and “the research-to-invention link runs mostly through foreign patents” go beyond the measured citation counts. The dataset here covers US patents, not all inventions or worldwide research use. The 6.40% is a share of summed institution-attributed patent citations with an Australian applicant/inventor flag; its complement is not proof of no Australian connection. The type comparison measures the proportion of works cited at least once, not the number of citations per work.

**Action:** State: “6.40% of recorded institution-attributed US patent citations have the defined Australian applicant/inventor link.” Define missing-country treatment and avoid identifying the complement as definitively foreign. Replace “build on” with “cite” and “cited most per work” with “highest recorded share of works cited at least once”. Specify that individual rankings apply to institutions above the 2,000-work threshold. Evidence: `28a93a93`, `0632bf39`.

### R14 — High | §7.4 / U85: family coverage and outcomes need denominator checks

**Issue:** The 97.0% linkage query begins with `institution_rights`, so a shared application can appear once per institution. It then joins distinct application–family pairs without demonstrating one family per application. Its row counts therefore do not establish a unique-application coverage rate. The family outcome table sums institutional counts and does not expose deduplication across institutions/years, the definition of “first filed”, or whether five-year citations count distinct citing families. These definitions are needed for the prose's stronger claims.

**Action:** Calculate coverage from distinct application keys, checking join multiplicity. Define family cohorts, attribution and citing-family deduplication; distinguish a family having at least one US grant from an application grant rate. Show eligibility for a complete five-year observation window and explain the chosen 2005–2019 cutoff. Treat the recent fall to 29 recorded families in 2024 as a coverage/maturity check, not a decline in inventive activity. Evidence: `28a93a93`, `0632bf39`.

### R15 — Medium | U86: the annual range is wrong and large-contract causation is untested

**Issue:** “1,000 to 1,835 a year from 2008” excludes **979 in 2014**. The 2019 total of $1,637 million does not itself show that single large contracts caused the spike. Annual totals are grouped by first-publication year, so they are not necessarily expenditure or contract delivery in that year. “Start in earnest” also blurs a change in recorded coverage with a change in activity.

**Action:** Correct the range to **979–1,835** for the displayed 2008–2026 years, marking the latest year as partial where applicable. Describe 2019 as a recorded value peak; show largest-contract contributions before attributing it. State that amounts are recorded contract values assigned to first-publication year, in current dollars, and define treatment of amendments and repeated notices. Evidence: `9fd731b1`, `24d6bac3`.

## Postcode coverage

### R16 — High | §7.6 / U87: deduplication remains incomplete for the overall postcode share

**Issue:** The first query deduplicates `(right, kind)`, not rights alone. A university–medical-institute co-application can therefore contribute to two rows. Summing those rows to calculate 71.58% can double-count institutional applications. The second, postcode-ranking query now counts distinct applications, but that does not repair the first query. The dated correction can be read as if all duplicate counting were resolved.

**Action:** Calculate the overall institutional/non-institutional share using one row per application and an “any institution” flag. Keep type-specific membership counts separately labelled as overlapping, or define exclusive categories. Quantify cross-type overlap and update 71.58% only after deduplication. Specify exactly which query the earlier correction fixed. Evidence: `5689b0df`, `7995cabf`.

### R17 — High | §7.6 / U87: postcode classification does not establish residence or institutional location

**Issue:** “Real code, no residents” means a postcode is absent from the postal-area table and falls in a delivery range. That test does not demonstrate validity, absence of residents or the reason no postal area matches. The code also uses one `founder_postcode` from the right while identifying any institutional founder; it does not show that the postcode belongs to that institution. Assigning such filings to a present-day ROR location could replace the recorded applicant location with another location.

**Action:** Relabel the class “delivery-range postcode not matched to a postal area” pending validation. Identify the party supplying the postcode and test its agreement with the institutional founder. Require a documented geographic allocation rule before moving records to institutional locations. Treat “stay in the state totals” as requiring a displayed reconciliation. Evidence: `5689b0df`, `7995cabf`.

### R18 — Medium | U87: application shares are described as shares of codes, and exclusions are obscured

**Issue:** The 71.58% statistic counts application rows, not distinct postcodes; “hold 71.58% of all the real codes” changes the unit. The university 50.34% is 742/1,474 in one unmatched category; including nine box/other-range records gives **751/1,474 = 50.95%** outside postal areas. Both exclude applications with no founder postcode. In the final table, an institution name identifies the leading institution at a postcode, but its adjacent count is all distinct institutional applications there, not necessarily that institution's count.

**Action:** State the counted unit and known-postcode denominator in the headline and summary. Distinguish the 50.34% category from the 50.95% total unmatched share and report missing-postcode exclusions. Relabel the final columns “leading institution” and “all institutional applications at postcode”, or show that institution's own count separately. Evidence: `5689b0df`, `7995cabf`.

## Later additions and updated conclusions

### R19 — High | §7.7 / U121: extrapolated losses require a visible sampling method

**Issue:** The cell reads estimates and “95% intervals” from an external CSV; it does not show random selection, response coverage, sampling seed or interval construction. The Australian estimate rests on only **23** sampled records, including **10** with no scholarly citation. Percentages are relative to the 103,644 already found, not the estimated total population. “Descriptive” does not distinguish direct counts from sampling estimates.

**Action:** Retain the sample counts but label extrapolations explicitly as estimates. Include a compact method/response audit and define the interval and population. State “additional works relative to those found”; if reporting a missing share of the estimated total, calculate that separately. Do not treat the two subgroup estimates as a proven exhaustive, disjoint partition without a cross-tabulation. Evidence: `2a97f2a1`, `bae467f5`.

### R20 — High | U121: unchanged rankings, recovered works and a lower bound are not established

**Issue:** The decision says losses are “spread over the institutions” and cannot change their order or B45/B46. No institutional allocation or sensitivity analysis is shown. Twelve merged identifiers may identify works already present under their replacement IDs; absence of an old ID is not necessarily absence of the underlying work. The sample's 24 Australian-work citations do not demonstrate the effect on every citation metric. A low aggregate missing share cannot establish negligible subgroup impact.

**Action:** Resolve sampled old/new IDs and test whether the underlying works are already represented. Report institution-level missingness and ranking sensitivity, or withdraw the invariance claim. Present “no re-harvest” as a practical decision with unresolved uncertainty. Restrict “lower bound” to validated non-duplicated counts under an omission-only assumption; shares and rankings are not automatically lower bounds. Evidence: `2a97f2a1`, `bae467f5`.

### R21 — High | U85 → U121 / U80 → U122 / §7.9: later qualifications are not propagated

**Issue:** U121 reveals omitted and unresolved-ID patent-cited works, but U85 and its summary retain unqualified citation shares and rankings. U80's overview now contains NSRC columns, yet its narrative and proposed windows still describe the older source mix. U122 adds commercialisation evidence only for 2000–2015; this does not extend the later filing period. §7.9 repeats headline claims while shedding several population, period and uncertainty qualifications.

**Action:** Add a current coverage/filter note directly to U85 and its figure; link the unresolved sensitivity result rather than presenting rankings as unaffected. Update U80's source coverage to include NSRC and its historical window. Regenerate §7.9 from corrected observations, retaining counting units and caveats. Keep dated changes in a short amendment note rather than leaving older conclusions authoritative. Evidence: `6003c09f`, `0632bf39`, `bae467f5`, `a0a400a7`, `cefd26ae`.

### R22 — High | §7.8 / U122: changing participation and item missingness constrain trends

**Issue:** Annual totals combine **48–72** institutions, and membership can change. `ns` includes a row when any NSRC field is present, so its institutional count is not the response count for each measure. Ordinary sums can present an all-missing measure as zero. The 98.9% and 99.9% coverage figures describe shares of source-reported disclosures/income captured in the lens, not representativeness of all Australian institutions or completeness of every measure.

**Action:** Display per-measure reporting counts, zero/missing distinctions and respondent continuity. Use `sum(min_count=1)` consistently. Describe the series as totals among that year's reporting linked institutions; use a stable-respondent comparison before claiming an institutional trend. Qualify coverage as capture of recorded NSRC totals. Evidence: `f85d7eca`, `577473a0`, `a0a400a7`.

### R23 — Medium | U122: terminology, ranges and cross-measure implications need tightening

**Issue:** “Licence income ran from $97.3 million … to $354.1 million” can read as a range, although the minimum shown is **$66.3 million in 2004**. The licences narrative stops at 728 in 2014 and omits **630 in 2015**. “Licences” abbreviates a measure described as licences, options and assignments. “43.2% of the income from 8.6% of the disclosures” suggests those disclosures generated that income, but no linked cohorts are shown. “Earned” may overstate what is established by reported income.

**Action:** Distinguish endpoints from extrema, include the 2015 value and use the complete measure name or define the shorthand. Say agencies account for the two separate shares; do not imply a return per disclosure. Describe income as reported, nominal income. State that start-up totals were lower in 2008–2015 than in 2000–2002, with a rebound to 42 in 2015, subject to R22. Evidence: `577473a0`, `a0a400a7`.

### R24 — Medium | U82 / U122: visible patterns are omitted from the narrative

**Issue:** U82's growth account omits the displayed fall from **252,456 in 2024 to 250,441 in 2025**, and the public-agency chart's conspicuous 2023 peak. U122 omits the research-expenditure fall from **$8.7 billion in 2010 to $6.3 billion in 2011**, followed by $10.0 billion in 2012. These could reflect coverage, membership or recording changes; no explanation is demonstrated.

**Action:** Add short descriptive notes and targeted coverage checks, without assigning causes. Note the high concentration already supported by U122: the three leading institutions account for about **65.0%** of recorded licence income. Keep concentration separate from commercialisation effectiveness or returns on research expenditure. Evidence: `2b856046`, `3dacd3e3`, `577473a0`, `a0a400a7`.

## Review boundary and reproducibility

This report contains **24 issue/action entries**. It establishes inconsistencies in the notebook and identifies checks needed before stronger claims are used. It does not establish whether external audits, referenced decisions, source data or imported functions are correct. The four saved figures were visually inspected; the numerical findings were checked against saved tables and visible calculations. All ten Lens 7 code cells have saved outputs, sequential execution counts 158–167 and no saved error outputs; that does not establish reproducibility against current data.

**Evidence locators:** U-numbers and section headings are searchable. Cell identifiers are the notebook JSON's stable `id` values, not execution counts. Cross-references to other lenses and Stages 2–3 were assessed only as claims made within Lens 7, not independently validated. No notebook or repository changes were made.

Downloaded notebook SHA-256: `1d5e51a699b82091788c75fdaff6d2706a24ba6a91df21877799677a8a357cdb`.
