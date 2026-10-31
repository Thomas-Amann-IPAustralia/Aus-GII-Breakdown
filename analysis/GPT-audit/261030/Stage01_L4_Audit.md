# Stage 1 notebook audit: Lens 4 reviewed in depth

**Reviewed:** 31 October 2026. **Source:** [01\_univariate.ipynb](https://github.com/Thomas-Amann-IPAustralia/Aus-GII-Breakdown/blob/main/analysis/notebooks/01_univariate.ipynb), downloaded from `main` on the review date.

**Provenance:** Follows the layout of `analysis/GPT-audit/261030/Stage01_L0-L1_Audit.md`: prioritised issue/action entries, grouped by subject, followed by review boundaries. R01–R30 are local to this Lens 4 report.

**Scope of this pass:** Only §4, including §§4.0–4.7, U63–U72, U115 and U120. Reviewed all 32 cells: 14 code cells and their saved outputs, 18 Markdown cells, and all six embedded figures (including the 30-panel indicator figure). Consulted the notebook's introductory rules, its applicant-field definition and U11 only to assess claims made in Lens 4. Apart from the supplied format reference, no other repository files, underlying datasets, external factual sources or GitHub Pages website were assessed. The notebook was not re-executed.

**Overall finding:** Most quoted values match the saved tables. The material weaknesses are an incorrect indicator interpretation, overstated source agreement, inconsistent historical-coverage rules, comparisons with changing or incompatible populations, and family-coverage conclusions that the displayed evidence does not establish. Later supplements are not fully reflected in the earlier overview.

**Priority:** **High** = affects interpretation, validity or downstream use; **Medium** = correct before relying on or circulating the findings. Implementation-dependent concerns are framed as checks. Apply corrections to the corresponding §4.7 summary row as well as the original observation.

**Read first:** R04, R06, R11, R12, R20 and R23–R27 address misleading claims or invalid comparisons. R14 and R28 address freshness. “Descriptive” does not automatically mean “univariate”, and a plausible explanation is not a demonstrated finding.

## Scope, coverage and definitions

### R01 — High | §4 rules: several analyses exceed strict univariate scope

**Issue:** Origin × year in U70, ownership/co-inventorship × partner × year in U71, and family coverage/reach × cohort × origin/PCT route in U115 describe joint or conditional patterns. U65 compares country-specific trajectories with an evolving comparator. These go beyond the introduction's promise to understand variables before relating them. U66 additionally supplies an explanation involving population and GDP.

**Action:** Move substantive relationship analyses to Stage 2, or explicitly permit and label stratified descriptive exceptions. Keep source-reconciliation and coverage diagnostics here as quality checks. A distribution of one indicator across countries, a rank within that distribution, or a simple time profile need not be removed merely because it uses two chart axes. Evidence: cells `4f7033c8`, `d036e415`, `48724bc5`, `2f6022da`, `06f696f3`–`ba0f0180`.

### R02 — Medium | U63: completeness is overstated and reporting frequency is not separated from missingness

**Issue:** “30 indicators for every country” and “Australia's series are complete except for R&D people and spending” overstate coverage. Indicator coverage ranges from 47 to 217 countries. Australia's tertiary enrolment covers only 40% of 2000–2024; advanced-education labour-force data cover 96%; other series start after 2000. The annual grid also treats years before a series starts, and potentially years outside its reporting schedule, as gaps.

**Action:** Describe a partially populated country–year–indicator table. Separate start/end coverage, expected reporting frequency, absent expected observations and source non-coverage. State that the fixed `38 × 25` OECD denominator is a reference panel, not demonstrated historical membership. Evidence: `0e50e75d`, `be1b0abc`.

### R03 — Medium | §4.0 / §4.2: row counts are assumed to represent distinct reported values

**Issue:** Coverage uses `count(*)`; ranking uses `len(o)` and Australia's first row in the latest year. Lens 4 shows no explicit uniqueness, non-null-value or flag check establishing that each counted row is one usable country–year observation. Duplicate rows would inflate coverage and ranks; nulls could also distort comparison denominators, depending on the column dtype. This is a validation gap, not proof that those defects exist.

**Action:** Display compact key-uniqueness, numeric-null and eligibility checks. Select the latest eligible non-null value, count distinct reporting countries, and state treatment of estimates and breaks. Preserve the published figures unless those checks identify an actual discrepancy. Evidence: `0e50e75d`, `2ad2808d`.

### R04 — High | U64: unknown origin is confused with former-state origin

**Issue:** “Before 1995 WIPO cannot say where most applicants come from” is unsupported for the worldwide series. Unknown origin is 34.35% in 1980, 29.02% in 1990 and 32.24% in 1993, not a majority. Former-state origins are known historical origins. The much higher unknown share at IP Australia is a different population. These are shares of applications, not distinct applicants.

**Action:** Describe substantial historical unknown-origin shares separately from former-state shares and the Australian-office gap. Present country totals as incomplete recorded counts; call them mathematical lower bounds only if counting and misclassification assumptions are established. Correct §4.7 too. Evidence: `54e27fd4`, `be1b0abc`, `48724bc5`.

### R05 — High | U64 / §§4.1, 4.4–4.5: the historical comparison rule is not applied consistently

**Issue:** U64 says WIPO country series are compared from 1995 only. The indicator and overseas-application charts still draw pre-1995 values as ordinary trends. The origin chart fills absent country-years with zero, creating apparent pre-1995 zero filing followed by abrupt increases. U115 also compares pre-1995 family series without explaining whether the earlier restriction applies to that different dataset.

**Action:** Mask or visibly distinguish unreliable periods, retain missing values unless zero is established, and mark recording breaks. Define dataset-specific eligibility rather than applying or ignoring a blanket WIPO cutoff. Diagnostic historical values can remain if clearly labelled. Evidence: `d036e415`, `48724bc5`, `06f696f3`.

## Core indicators and international comparisons

### R06 — High | U65: the advanced-education indicator has the wrong denominator

**Issue:** U65 calls `SL.TLF.ADVN.ZS` the “share of the labour force with advanced education”. The saved chart's full title instead gives labour force with advanced education **as a percentage of the working-age population with advanced education**. That is participation within an education group, not the educational composition of the labour force. The interpretation of the 86.33% value is therefore wrong.

**Action:** Use “labour-force participation among working-age people with advanced education”. Preserve the published denominator in labels and summaries. Also explain that the tertiary-enrolment indicator is a gross ratio, so its 108.4% is not a percentage of all people attending tertiary education. Evidence: figure in `d036e415`, U65 in `1b5570dd`, table in `2ad2808d`.

### R07 — High | U65: unusual values are declared to be series breaks

**Issue:** A negative FDI value in 2005 and the advanced-education step are called “two series breaks to read past”. Neither the table nor code tests a methodological break or displays supporting source flags. A negative net flow can be a valid observation; an unusual step alone does not establish a recording error.

**Action:** Call these an unusual value and a possible discontinuity pending validation. Show relevant metadata/flags before excluding, adjusting or disregarding them. Retain the advanced-education pattern as an unresolved lead, consistent with §4.7. Evidence: `d036e415`, `1b5570dd`, `99501afa`.

### R08 — High | U65: changing reporting panels are described as one median member's trajectory

**Issue:** Annual OECD medians use whichever members report, with as few as ten in the chart. Their change need not be the change experienced by a typical fixed member. “Manufacturing fell twice as fast” refers to relative endpoint declines of 61% versus 30%; the percentage-point falls are 8.38 versus 5.50. “Has fallen since” also obscures intervening variation in R&D intensity.

**Action:** Say “the median of reporting members in each year”; show annual sample sizes and a fixed-panel sensitivity comparison before interpreting relative trajectories. Specify relative percentage change in manufacturing's GDP share, not manufacturing output or an annual speed. Describe R&D as lower in 2023 than its 2008 peak. Evidence: `d036e415`, `1b5570dd`.

### R09 — High | U65–U66: explanations and economic meanings exceed the evidence

**Issue:** Australia's filing, article and royalty counts are said to occupy their positions because of size “for that reason alone”. No size-adjusted analysis establishes this. The European Patent Office explanation for falling national-office medians is also untested here. Royalty payments and receipts are described as returns on “others' IP” versus “its own”, although the displayed indicators measure cross-border charges, not the ownership or total economic return of Australian-created IP.

**Action:** Remove the exclusive size explanation; retain scale as a consideration for Stage 2. Label the European-office explanation as a hypothesis requiring evidence. Describe recorded IP-charge payments and receipts in current US dollars without implying a national IP-value balance or real growth. Evidence: `1b5570dd`, `d4801615`.

### R10 — Medium | U66 / §4.2: ranks mix years, reporting subsets and an imprecise median marker

**Issue:** The ranking ranges from technicians in **2008** to economic indicators in **2025**, with 22–38 reporting members. It is not a common-date OECD assessment. Some chart labels truncate the year. Gross R&D at 21st of 35 is below the median but not convincingly “near the bottom”. The strict share below Australia includes Australia in the denominator; `50 = the median member` is not exact for odd samples or ties.

**Action:** Show each year and reporting denominator prominently; flag stale series and avoid a single current-performance interpretation. Use “below the reporting-member median” where appropriate. Keep “percentage strictly below Australia” or adopt a stated percentile convention. U65 should also acknowledge available 2024 patent figures: 2,542 resident and 27,945 non-resident applications, rather than stopping its patent account in 2023. Evidence: `2ad2808d`, `d4801615`, `1b5570dd`.

### R11 — High | U67: the stated reconciliation tolerance is numerically false

**Issue:** “Within 1.5%” for resident standard patents contradicts the minimum ratio **0.907**, a **9.3% shortfall** in 2008. Trade-mark class counts differ by up to **6.2%** and utility models by **33.1%**. “The lenses agree” conceals these exceptions. Exact WDI/WIPO agreement is shown for combined resident and non-resident totals, not independently for each split or as independent confirmation from three unrelated sources.

**Action:** Report the full resident range, **0.907–1.015**, and retain 2008 as an unresolved discrepancy. Qualify agreement by series, years and tolerance; distinguish total reconciliation from origin reconciliation. Explain potential source dependence before treating agreement as corroboration. Correct §4.7's repeated 1.5% claim. Evidence: `ef6e0a23`, `7d095977`.

### R12 — High | U67 / U115: current-holder origin is used for historical filer claims

**Issue:** The notebook's §1.8.1 explicitly defines applicant fields as current-holder information. Lens 4 nevertheless uses `australian_applicant` to reconcile historical resident filings and to select Australian patent families/PCT applications. These selections need not represent Australian applicants at filing, and cannot establish family-level Australian origin across all family members.

**Action:** Use validated founding-origin fields for filing comparisons, with historical limitations stated. Define family origin explicitly and reconcile it with WIPO's definition; a qualifying Australian-office record alone is insufficient. Otherwise relabel results as current-holder-selected records. Evidence: definition in `7e248d05`; Lens 4 queries `ef6e0a23`, `06f696f3`, `ba0f0180`.

### R13 — Medium | §§4.1–4.3: charts hide exceptions or retain superseded labels

**Issue:** The source-ratio chart fixes its y-axis to **0.4–1.15**, clipping the 0.072 historical ratio and the 1.331 utility-model discrepancy it should help investigate. The 30-panel figure's overall title overlaps its top-row titles. Trade-mark chart labels still say “applications, by count” after U67 identifies class counts, and the ranking chart truncates important units and dates.

**Action:** Show the full ratio range or clearly labelled insets and out-of-range annotations. Repair title spacing and wrap labels without losing years/units. Use “application classes” in reader-facing trade-mark labels while retaining source codes for traceability. Evidence: figures in `d036e415`, `2ad2808d`, `ef6e0a23`.

## Attachments, GII and office statistics

### R14 — Medium | U68 / §4 introduction: attachment totals exclude later additions without saying so

**Issue:** U68 reports **41,218,170** attached values as the inventory. Its query deliberately excludes WIPO origin-family indicators, GII supplements and Schools. The notebook's introduction lists **41,230,072** `national_indicators` rows, **11,902 more**. “Every value they publish” also exceeds what an inventory of ingested rows can establish; some rows are text or null, not numerical measurements.

**Action:** Regenerate a complete current inventory, or label U68's total as a subtotal with the exclusions and reconciliation shown. Use “rows/records” and qualify completeness as coverage of the ingested tables. Update §4.7 and the attachment source description. Evidence: `257435cc`, `4f7033c8`, `7e0751c8`, `66dc23fc`.

### R15 — Medium | U68: generic flag/null counts are assigned specific meanings

**Issue:** The inventory measures non-null `status` and null `value`. U68 interprets those as particular estimate/break categories and suppression without displaying a status breakdown. Null values can also carry text or other unavailable-value markers. For Measuring What Matters, the inventory averages page-level percentages equally, which is not a row-weighted source percentage; currently displayed zeros conceal that distinction.

**Action:** Tabulate actual status/text categories and distinguish suppressed, missing, textual, projected and estimated records. Compute source percentages from counts or row weights. Do not infer the meaning of every null from one documented repair. Evidence: `7e0751c8`, `66dc23fc`.

### R16 — Medium | U68 / U120: data absence is treated as evidence of wider absence

**Issue:** Five OECD flows have no Australian rows, but this does not establish why. “Australia has no patent box” is a substantive policy assertion not demonstrated by the displayed inventory. The code shows absence from the ingested flow, not whether Australia lacks an underlying activity, regime or source publication. U120 similarly asserts that there is no Australian microfinance series without showing the search or coverage evidence.

**Action:** State “no Australian records in the ingested flow”. Remove the policy explanation or separately validate and date it before retaining it. For microfinance, say no suitable series is supplied here unless the broader absence claim is separately substantiated. Keep source absence distinct from a measured zero. Evidence: `66dc23fc`, `2f6022da`, `ef086a65`.

### R17 — Medium | U69: broad strength/weakness labels blur the displayed categories

**Issue:** The numerical GII ranks agree with the output, but “strengths are education and universities” omits listed regulatory/tariff strengths and includes cluster development under an ill-fitting heading. “Weaknesses are outputs and trade” includes education, demographics and energy. The table distinguishes overall from income-group flags, which a broad summary can obscure.

**Action:** Use “selected WIPO-flagged strengths/weaknesses include…” and group them accurately. Retain the distinction between overall and high-income comparisons, and distinguish ranks from the publisher's strength/weakness labels. Keep the useful warning that the composite reflects indicator and weight choices. Evidence: `ae9dd1f0`, `2d828dc2`.

### R18 — Medium | U70: rounded equality and selected years become broader claims

**Issue:** China's and Australia's displayed shares both round to **8.3%**, which establishes approximate parity, not exact equality. “Before 1995, 87.3% to 88.6%” quotes just the 1990 and 1994 examples; the chart shows substantially higher earlier unknown shares. “Three-quarters … abroad” is an application-event share, not the share of Australian inventions or applicants that seek overseas protection.

**Action:** Say “both approximately 8.3% in 2024”, provide counts if asserting equality, and label historical examples by year. State the overseas denominator explicitly, noting that an invention may generate applications at several offices. Evidence: `48724bc5`, `2bd602eb`, `99501afa`.

### R19 — High | U70: office benchmarks silently mix reporting years

**Issue:** The office query selects each office's latest year independently before calculating medians. U70 labels the comparison “(2024)”, although only Australia's year is displayed; peers may report older values. The table itself includes Australia's 2016 registration-time figure. Office counts and procedural durations also describe different quantities, not a common measure of office performance.

**Action:** Compare the same indicator in a common year, or show the full distribution of peer reporting years and label the benchmark as mixed-year. Retain reporting-office counts and define each duration's start/end events. Avoid efficiency conclusions without comparable workloads and procedures. Evidence: `48724bc5`, `2bd602eb`.

### R20 — High | U70: a mean of 222 days does not confirm a 222-day mode

**Issue:** U70 treats WIPO's **2016 average** of 222 days as confirmation that the **modal peak** in U11's broader filing cohort is the usual registration path and “not an artefact”. A mean and a mode can coincide numerically without identifying the same population, mechanism or recording convention. U11 correctly leaves the explanation unresolved.

**Action:** Retain this as a numerical correspondence, not resolution of the lead. Align populations, periods and duration definitions, then check the distribution and procedural explanation before ruling out an artefact. Evidence: `48724bc5`, `2bd602eb`; referenced U11 in `45073a0d`.

### R21 — Medium | U71: the code comment contradicts the output and the prose broadens the unit

**Issue:** The query comment says all three “World” totals agree; the output and U71 correctly distinguish **2,117 invented in Australia** from **1,762 owned in Australia** in 2015. Later prose refers generally to “inventions”, while the selection is PCT applications by priority date. The 2022 decline is reported without showing whether recent priority cohorts have comparable reporting maturity.

**Action:** Correct the comment and carry the PCT/priority-date restriction into all claims and captions. Define each partner percentage's denominator and whether multi-partner counts overlap. Qualify the latest decline until cohort maturity is checked; do not treat it as a decline in all Australian invention. Evidence: `2f6022da`, `fd212c1a`.

### R22 — Medium | U72: some claims are not evidenced by the displayed checks

**Issue:** Period counts establish **3,767 monthly records**, but not that all are employment/wages or exact copies of the named ABS series. Similarly, counting `modelled%` statuses does not establish that all 443 estimates use linear regression. The prose's period enumeration omits **112** Measuring What Matters records classified as “other”. Projection/model/assessment categories are counted, not demonstrated as mutually exclusive conceptual groups.

**Action:** Include the omitted category. Show labels, source mappings or method metadata for the duplication and modelling claims, or qualify them as unverified descriptions. Keep the explicit rule excluding projections from observed-data analyses. Evidence: `5f74ab65`, `50009d5b`.

## Later additions: patent families and GII supplements

### R23 — High | U115: unmatched aggregate family counts do not measure families bypassing Australia

**Issue:** Google Patents families selected through IP RAPID are **84.04%** of WIPO's 2015–2019 total. The complement is called “about one … in six … never reaches IP Australia”, even though the notebook acknowledges different family definitions and incomplete matching. Two aggregate counts do not establish a subset relationship. Calling the complement an “upper bound” is also unjustified without that relationship.

**Action:** Report the ratio as a discrepancy between differently constructed inventories. Remove the bypass estimate/bound until definitions, origin, dates and matching are harmonised or a family-level overlap is established. Do not interpret missing corpus matches as proof of no Australian filing. Evidence: `06f696f3`, `34710b37`.

### R24 — High | U115: coverage diagnostics do not establish their asserted mechanisms

**Issue:** The priority-office test assumes every non-Australian/non-US priority must have a published foreign filing; that premise is not demonstrated. PCT entry likewise does not by itself prove entry into several national offices. Differences in family scope, publication, matching, cohort mix and actual filing behaviour remain alternatives. The headline attributes incompleteness to Google Patents, while the final paragraph admits the corpus's matching may be responsible.

**Action:** Describe the results as evidence of possible coverage/matching problems. Verify expected publications on a sample, define whether international/regional records count as offices, and distinguish a foreign-only family from a multi-office family. Reconcile WIPO's foreign-oriented definition before treating it as identical to `family_offices > 1`. Keep attribution unresolved. Evidence: `1038afaa`, `ba0f0180`, `34710b37`.

### R25 — Medium | U115: the final five-year group is mislabelled and an important level change is overlooked

**Issue:** `fam.loc[1980:2022]` produces a final **2020–2022** group labelled **2020 to 2024**. It is not a full five-year total. The emphasis on a roughly stable foreign-oriented share also obscures a **20.5% decline** in WIPO family counts between the complete 2000–2004 and 2015–2019 groups: 21,047 to 16,726.

**Action:** Label actual group boundaries and completeness; do not compare partial totals as full periods. Add the observed count decline alongside the share, without inferring a cause or assuming constant source coverage. Describe 61.73%–66.37% as the observed grouped range, not proof of statistical stability. Evidence: `06f696f3`, `34710b37`.

### R26 — High | U115: denominators and the FY2010 rule are insufficiently supported

**Issue:** The foreign-priority diagnostic includes all standard patents, but supports a decision about Australian applicants. PCT counts include records without families, while its percentages exclude them; null office/grant fields could narrow denominators further. The displayed checks concern offices and US grants, yet the decision extends to citations. Post-FY2010 improvement does not establish complete coverage. The latest US-grant share is **42.54%**, below 53.05% in FY2015–FY2019, which the “double at the same break” account omits.

**Action:** Display eligible denominators and separate Australian-origin results. Label FY2010 as a provisional reporting cutoff, not validation of completeness; evaluate citation coverage separately. Include the latest cohort with a maturity caveat and avoid treating its grant percentage as a completed-cohort outcome. Evidence: `1038afaa`, `ba0f0180`, `34710b37`.

### R27 — High | U120: non-equivalent supplementary measures are used for precise international positions

**Issue:** The saved caveats identify FTE versus headcount differences for pupils, mixed survey years for R&D/researchers, and excluded joint business–government funding. Peers use their latest available GII data years, which are not displayed. Nevertheless U120 reports exact shares below Australia and says researchers sit outside business “more than almost any” member's. **16.7% of 36**, or six reporting peers, have a lower business share; Australia is also excluded from this comparison denominator.

**Action:** Present these as approximate contextual comparisons, with definitions and Australian/peer periods beside each row. Suppress rank-like precision where measures are not comparable, or label it explicitly as indicative. Say “below most reporting peers” and refer to researcher effort rather than unqualified headcounts. Keep the rule against recalculating GII scores or ranks. Evidence: `35e0960f`, `ef086a65`.

### R28 — Medium | U63 / U69 / U120: later supplementary coverage is not propagated backwards

**Issue:** U120 adds approximate contemporary researchers-per-million and business-funding measures, but U63 and its summary still leave readers with historical R&D endpoints alone. U69's six blanks remain correct **for the published GII**, yet it does not direct readers to the four supplementary measures. U120 also quotes **11.8 in 2023**, although its preceding query retains only the latest pupil–teacher value, **11.7 in 2025**.

**Action:** Add explicit forward references distinguishing published-source gaps from supplementary coverage; do not silently replace or backfill the GII/WDI series. Display the 2023 observation if retained, or remove that unevidenced comparison. Preserve source-specific definitions and dates. Evidence: `be1b0abc`, `2d828dc2`, `35e0960f`, `ef086a65`, `99501afa`.

## Completeness of the descriptive account

### R29 — Medium | §4.2 / §4.4: the promised univariate profiling is only partially delivered

**Issue:** The cross-country section gives Australia's position and the median, but no latest-year distribution, tails or named extremes for most core indicators. Attachment profiling is mainly an inventory plus selected examples; it does not support the introduction's claim that every attachment variable has been explored. Important distinctions such as counts versus rates, mixed units and repeated breakdowns remain largely implicit.

**Action:** Add compact per-indicator summaries: usable country count, missingness, median, quartiles, range and flagged extremes, with clearly selected plots. Prioritise indicators used downstream; explicitly mark other attachments as inventoried only. Do not summarise unlike indicators into one numerical distribution or add relationship analysis just to complete the checklist. Evidence: `2ad2808d`, `7e0751c8`, notebook introduction `83e76483`.

### R30 — Medium | §§4.1–4.2: contrasting indicator results deserve explicit descriptive treatment

**Issue:** The output contains useful contrasts not discussed: high-technology exports are **24th of 38 in current-dollar value** but **8th of 38 as a share of manufactured exports**. These measure different things and should not be collapsed into a broad exports verdict. The scientific-article chart also shows a recent fall after its peak that receives no observation or coverage qualification.

**Action:** Briefly state the high-tech value/share distinction with units and years, without claiming an explanatory relationship. Flag the article endpoint as an observed decline requiring a reporting/comparability check before interpretation; tabulate the relevant annual values if discussing it. Evidence: `d036e415`, `2ad2808d`, `d4801615`.

## Review boundary and reproducibility

These findings establish inconsistencies in the notebook or identify validation required before stronger claims are used. They do not establish whether referenced ADRs, external metadata, imported helpers, source pipelines or earlier/later analysis stages are correct. All 14 Lens 4 code cells have saved outputs, sequential execution counts **115–128**, and no saved error outputs. This does not establish reproducibility against current data or code. No notebook or repository changes were made.

**Evidence locators:** U-numbers and section headings are searchable. Cell identifiers are the notebook JSON's stable `id` values, not execution counts; a range denotes consecutive cells. This report contains **30 issue/action entries**. The downloaded notebook's SHA-256 matches the version recorded in the supplied Lens 0–1 audit.

Downloaded notebook SHA-256: `1d5e51a699b82091788c75fdaff6d2706a24ba6a91df21877799677a8a357cdb`.
