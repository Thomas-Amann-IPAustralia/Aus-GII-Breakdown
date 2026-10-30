# Stage 1 notebook audit: Lens 0 retained, Lens 1 reviewed in depth

**Reviewed:** 30 October 2026. **Source:** [01\_univariate.ipynb](https://github.com/Thomas-Amann-IPAustralia/Aus-GII-Breakdown/blob/main/analysis/notebooks/01_univariate.ipynb), downloaded from `main` on the review date.

**Provenance:** Duplicated `analysis/GPT-audit/261030/Stage01_L0-L1_Audit.md` and developed this replacement from that copy. R01–R36 retain the original issue identifiers, with Lens 1 findings checked and refined; R37–R44 add findings. The Lens 0 finding (R02) is retained from the original audit, not a new Lens 0 review. This document includes the complete issue/action register and does not depend on keeping the original audit.

**Scope of this pass:** Only §1, including its overview, §§1.1–1.7, all seven attachments and §1.9. Reviewed all 110 Lens 1 cells, including 73 code cells, their saved outputs, all 38 embedded charts, and the observations. Introductory rules were consulted to assess Lens 1's compliance. Apart from the supplied audit, no other repository files, underlying datasets, external factual sources or GitHub Pages website were assessed. The notebook was not re-executed; references to ADRs, other audits and other lenses were not independently verified. The downloaded notebook's SHA-256 matches the version identified in the original audit.

**Overall finding:** Many quoted figures agree with the saved outputs, and the notebook usefully exposes missingness and historical recording changes. The main weaknesses are comparisons labelled univariate, current-holder information described as filing information, conclusions stronger than their evidence, and older observations left standing beside corrections. Several numerical and denominator errors are directly demonstrable.

**Priority:** **High** = affects interpretation, validity or downstream use; **Medium** = correct before relying on or circulating the findings. Implementation-dependent concerns are explicitly framed as checks. Apply each correction to the corresponding row in §1.9 as well as the original observation.

**Read first:** R04, R05, R10, R17, R21, R27, R31, R33 and R39 address populations, denominators or validity; R12, R32 and R36 address outdated or conflicting conclusions. An observation can be descriptive while still being bivariate. “Recorded”, “known” and “estimated” qualifications are substantive, not merely wording preferences.

## Scope, freshness and definitions

### R01 — High | Comparisons exceed the stated univariate scope

**Issue:** “Descriptive” does not mean “univariate”. Origin × year (U7), representation × origin × applicant type (U20), ownership transitions (U18–U19), lifetime × cohort (U36), route × origin × year (U90), reach/citations × origin (U93–U94), and inventor location/gender × filer (U96–U98, U107) describe relationships between variables. The WIPO scatterplot in §1.8.5 is explicitly bivariate. §1.8.6 also analyses firm-level entry despite the section’s right-level unit.

**Action:** Move substantive comparisons to Stage 2, retaining individual distributions and coverage checks here. Alternatively, explicitly broaden Stage 1 to include stratified descriptive analysis and identify those exceptions. Simple counts of filing dates and source-agreement checks need not be removed merely because they have two chart axes.

### R02 — Medium | §0 / U0: historical inventory presented as the current corpus

**Issue:** U0 acknowledges that its 162-table, 41-source profile excludes subsequently added sources. Later attachments use further data, including the register and provisionals. The chart cites 22 October, while U0 identifies the displayed profile as the 25 October rerun. The section still says “five lenses”, whereas the introduction says seven.

**Action:** Regenerate the inventory from the intended snapshot, or label it explicitly as a historical inventory with exclusions. Generate its date, totals and lens count from one source of metadata.

### R03 — Medium | Introduction / U1 / §1.8: inconsistent completion and row counts

**Issue:** The introductory lens table still gives 4,368,006 rights; the executed overview gives 4,356,908 after 11,098 design shells were removed. Status text ends at U104 and describes six attachments, whereas §1 includes U105–U107 and seven attachments. The attachment contents list stops at 1.8.5.

**Action:** Update the introduction and contents to the executed notebook. Use a generated row count rather than maintaining duplicate totals manually.

### R04 — High | U5–U8, U13, U15, U90–U94: holders described as filers

**Issue:** §1.8.1 explicitly says `applicant\_\*` describes the current holder. Earlier origin, applicant-type and location analyses nevertheless describe who applied and where they were at filing using those fields. Later route and family analyses also group by `australian\_applicant`. U17–U19 demonstrate that holder and founder can differ materially.

**Action:** Use founding fields for filing claims, subject to U17’s historical limitations, and rerun affected outputs. Otherwise relabel results as current-holder characteristics of applications filed in the stated years. Do not silently mix current-holder and founder definitions across adjacent tables.

### R05 — High | U1 / U9: missing values treated as proof of non-occurrence

**Issue:** U1 says the registration date is empty when a right was never registered, but U9 reports grant dates for only 68.9% of expired patents. “Complete where it should be” and “empty by design” also conflate inapplicable fields with unrecorded information. A populated status of `unknown` is not a known outcome.

**Action:** Say “registration/grant date recorded”, not “ever registered”, unless supported by additional evidence. Separate applicable, recorded, unknown and inapplicable cases; report coverage within eligible right types. In U13, the 0% ABN figure for plant breeder's rights means the source supplies no ABNs, not that applicants have none. In U106, distinguish zero inventors on a retrieved record from the ten register records not found (U105): `register_inventors` is nevertheless 100% filled. Describe the lens as application/right records, not exclusively granted or enforceable rights.

## Core rights profile

### R06 — High | U6: annual volume does not establish completeness

**Issue:** U6 concludes FY2025–FY2026 are complete because counts are not lower. This is both insufficient evidence and factually inconsistent: plant breeder’s rights fall to 258 and 255, below every FY2017–FY2024 value; second-tier patents also fall. Recording applications at filing does not itself demonstrate zero publication or ingestion lag.

**Action:** Replace the completeness claim with a description of recorded volumes. Identify completeness as requiring source reconciliation and release-lag evidence. Separate the observable growth in trade marks/designs, decline in plant breeder’s rights, and second-tier transition.

### R07 — High | U8 / U107: the provisional increase is over-interpreted

**Issue:** “Not from businesses” is not established by flat distinct ABNs: missing ABNs do not establish non-business activity, and rights with an ABN increase. The summary infers “individuals without ABNs” from separate marginal counts, without a joint count. U107 says individual filing doubled, but 5,399 versus 1,926 is **2.80 times**; total provisionals approximately doubled.

**Action:** Report those measured changes separately. Remove the business conclusion and joint inference unless directly tabulated. Keep the founder-level heavy-filer counts separate from right-level counts, since co-applications count for multiple founders. Qualify “real” as an increase in recorded applications. Compare September with earlier Septembers, or show a same-month change series, before treating September 2026 versus March 2024 as evidence of a sustained doubling; the current comparison mixes seasons.

### R08 — Medium | U3 / U9: undated records are omitted and assigned an unsupported age

**Issue:** The missing-date table totals **50,763**, not 50,756: U3 omits six plant breeder’s rights and one trade mark. U9 says all 408,957 unknown-status patents were filed in FY1904–FY1999, although U3 identifies 49,737 standard patents with both unknown status and no application date. SQL date minima/maxima exclude those missing dates.

**Action:** Correct the total and say “among records with a known filing year”. Treat the age of undated records as unestablished. Replace “cannot be placed in time” with “cannot be assigned a filing year from the application date”, because some have other dates.

### R09 — High | U9 / §1.3: status categories and percentages need correction

**Issue:** Designs are **25.55% in force** and **64.14% ended after grant** in the displayed table, not 24% and 66%; the old figures are consistent with retaining the removed shells. Separately, stage labels assert before/after grant solely from status: 24.95% of refused patents have a registration date. “A lapse is an application abandoned” adds a behavioural explanation not established by status.

**Action:** Recalculate design percentages. Label the grouping as a status-based approximation or classify using reconciled event evidence, retaining conflicts explicitly. Describe provisional applications separately from failed attempts at grant. Use recorded status, rather than inferred motivation, in the prose.

### R10 — High | §1.4 / U11–U12: plant breeder’s rights remain substantially unfinished

**Issue:** The checklist claims at most 0.1% of FY2010–FY2019 applications remain pending. U10 instead shows plant breeder’s rights at 2.6% pending in FY2010, 8.2% in FY2015 and 30.1% in FY2019. The duration table includes them, and the annual chart extends to FY2021 despite U10’s proposed cutoff around FY2010.

**Action:** Apply type-specific maturity rules. Describe durations as conditional on registration observed by the snapshot; report excluded/pending shares. Do not present recent plant breeder’s rights medians as complete-cohort processing times. State that U11’s percentiles concern observed successful applications, not all applications.

### R11 — High | U3, U11, U40: anomalous dates are acknowledged but not consistently contained

**Issue:** Negative registration durations remain in summary statistics, while the trade mark log chart excludes 40 zero/negative values and displays a different mean. Fourteen future end dates are dismissed as too few to matter without assessing affected subgroups. `years\_in\_force` reaches 119.75 years; `register\_expedite\_date` reaches back to 1909. U40 closes the placeholder issue, but §1.8.3 explicitly excludes only 1800/1900 dates, leaving its treatment of 26 links dated 1970 unclear.

**Action:** Retain raw values but flag and consistently exclude invalid analytical durations; align chart/table populations. Show a short anomaly-impact check and explain the extreme lifetimes and 1909 events. Explicitly document treatment of all identified placeholder dates before closing the issue.

### R12 — High | U13 / U99–U102: ABN and origin updates are not propagated

**Issue:** U13 still concludes that 12%–22% of Australian organisations’ rights cannot reach the firms lens, although U99 adds filer ABNs to 134,995 trade marks and 3,097 designs. U7/U13 retain older design-origin results beside corrections; associated charts and §1.8.3 still use the unfilled origin field. The route-chart caption incorrectly says origin was recorded for “few Australian designs” before FY2018; the earlier tables show missing minorities, not that most records lacked origin.

**Action:** Make the updated analysis the primary account, with original-source results labelled as a comparison. Recompute relevant cohorts using the appropriate filled/founder fields. Replace the outdated ABN-linkage conclusion and route caption; retain earlier claims only in a clearly marked change log.

### R13 — Medium | U14 / §1.9: main-class counts overstate what is protected

**Issue:** These charts count one main class or mapped main technology field per application, not all claimed classes, protected subject matter or granted rights. The summary’s “services lead trade marks” is not established by one service class being the largest individual class. The plant-genus “other 559 values” is the remainder after the chart’s top **15**, not after the three genera named in the prose.

**Action:** Describe “applications by recorded main class/field”. Either aggregate all relevant service classes before claiming a services lead or remove that statement. Clarify the top-15 remainder and keep missing classes distinguishable from other observed classes. U14's decision to use technology fields from the 1970s also needs coverage of `main_area`, not just `main_class`: a recorded class does not establish a successful technology-field mapping.

### R14 — Medium | U16: a non-null postcode is not a validated geographic link

**Issue:** The 99.3% “usable postcode” measure tests only `IS NOT NULL`; it does not join to a postal area. The notebook itself lists 3,535 distinct applicant postcodes and 2,641 postal areas, so these are not interchangeable inventories. The 3,857 non-first Australian applicants are also not the same population as U19’s 4,085 non-first Australian founders.

**Action:** Report postcode presence separately from successful postal-area matching, including unmatched values. Avoid saying U19 fills the earlier gap without a right-level overlap check. Keep geographic claims restricted to the explicitly selected first applicant/founder population.

## Parties, events and lifetimes

### R15 — High | U2, U13, U20–U21: attorney status and concentration are proxies

**Issue:** An agent serving at least five applicants is not verified as an attorney; fewer clients do not establish the opposite. Threshold sensitivity is not a statistical bound on true attorney use. U21’s concentration table groups by `agent\_id`, its chart groups by `agent\_name`, and missing names become “an individual attorney” without evidence. “Trade mark representation is not concentrated” lacks a stated criterion.

**Action:** Use “agent meeting the client-count threshold” until validated; describe thresholds as sensitivity scenarios. Align the grouping unit, label missing names as unknown, and report measured top-five/top-ten shares without an absolute concentration verdict or an unverified lower-bound claim.

### R16 — High | U17–U19 / U35: recorded differences do not reconstruct ownership histories

**Issue:** Party-ID or postcode differences can reflect identity/address changes; they do not by themselves prove a transfer or relocation. U35 acknowledges name changes. Origin transitions concern whether any recorded holder is Australian, not movements of inventions or economic value. Post-2003 agreement between assignment and holder flags does not establish that assignment records recover the same fraction of pre-2003 changes.

**Action:** Describe recorded holder/address differences and endpoint origin classifications. Reserve transfer/movement language for validated events. Present pre-2003 assignments as an incomplete indicator whose historical coverage is unknown, rather than a calibrated two-thirds recovery rate.

### R17 — High | U32: annual averages are described as shares of a decade’s rights

**Issue:** The milestone table uses `groupby(...).mean()` on annual percentages. Its 54.21%, 85.5%, etc. therefore give equal weight to each filing year, not each application. U32 describes these as percentages of all patents or rights filed in the decade. The 1970s and 2020s are partial periods.

**Action:** Aggregate milestone counts and eligible denominators across each period before dividing, or explicitly label the existing figures “unweighted mean of annual shares”. State partial-period boundaries and distinguish recording coverage from time available to reach a milestone.

### R18 — Medium | U31 / U34: validation claims exceed the displayed checks

**Issue:** The 99.99% grant-date agreement is conditional on a matching grant event and non-null registration date, not all granted patents. The 99.78% assignment check tests whether both event types occur somewhere on a right, not whether individual assignments are duplicates. U34’s expedited percentage averages a nullable flag without displaying its eligibility denominator, yet labels it “of those examined”.

**Action:** State the tested populations precisely. Show unmatched grant counts, event-level deduplication checks and the denominator for expedited rates. Distinguish an expedite event, a request and completed examination; avoid inferring greater demand for speed from the flag alone.

### R19 — High | U3, U33, U38–U39: explanations are presented as established findings

**Issue:** Filing spikes near policy dates are called rushes caused by rule changes; U38 concludes the 2002 pattern was “not from processing”; U39 says April lapses were dated in other months. Timing, cohort composition and similar annual lapse shares support hypotheses, but do not establish those explanations or rule out alternatives. The event queries for U38/U39 also lack the `is\_standing` filter promised in §1.8.2.

**Action:** Separate observed patterns from plausible explanations and remove categorical causal/exclusion wording. Identify what would resolve each lead. Either use standing events consistently or explain why reversed events belong in these historical event counts; do not mark the leads resolved on the present evidence.

### R20 — High | U36: survival cohorts mix different right regimes

**Issue:** The “2000s” design cohort includes years before and after the Designs Act 2003, but its 64.8% survival at five years is described entirely under the later regime. Second-tier cohorts are assigned as petty/innovation using the year of `date\_of\_patent`, rather than the recorded subtype; the notebook already shows innovation applications with pre-2001 filing years.

**Action:** Define regime cohorts using verified applicability rules and actual subtype, showing boundary cases. Recalculate before making renewal comparisons. Treat date-based approximations as such rather than substituting them for legal categories.

### R21 — High | U36: survival is not a directly observed renewal rate

**Issue:** The notebook says renewals are inconsistently recorded, yet describes survival at anniversaries as renewal percentages. Cohort curves are conditional on `in\_force` being known; U9 establishes incomplete old grant records. For patents, the term starts before grant, so the selected registered population also includes pre-grant elapsed time. Censoring adjustment alone does not repair selection or historical omissions.

**Action:** Label results as estimated survival of eligible recorded rights, define entry and exclusion rules, and qualify renewal/owner-behaviour interpretations. Show eligible denominators and a small at-risk table; apply the chart’s minimum-risk rule to reported tail estimates too. Check how cohort conclusions change under comparable recording coverage. The code rounds durations down to months (`floor(years_in_force * 12) / 12`); verify anniversary estimates against exact dates, and state whether the estimate is immediately before or after renewal is due. For the March censoring cutoff, verify that later ends are censored at March and records starting after March are excluded; the notebook does not expose that construction.

### R22 — Medium | U31, U37 / §1.8.6: inconsistent observation cutoffs

**Issue:** Trade mark ends become zero after April 2026; design ends decrease but continue. That supports a conservative cutoff, not proof that both are complete through March or patents/PBR through October. The term-extension chart includes partial calendar 2026 without marking it. §1.8.6 tables include partial FY2027 without the label used in §1.2. The provisional monthly chart also includes July–September 2026 despite §1's blanket rule excluding FY2027 from charts; complete months may be useful, but the exception is unstated.

**Action:** Distinguish chosen censoring dates from verified completeness dates. Record source-specific snapshots and release lags, assess cutoff sensitivity, and mark all partial years. Avoid treating a single October date as the observation date for every attachment.

## Links, families and inventors

### R23 — High | U90: exclusive route labels do not show abandonment of provisionals

**Issue:** `filing\_route` selects the first applicable category. PCT and divisional applications can also claim Australian priority, so a smaller Australian-priority route category does not establish that applicants moved away from provisional applications. “Direct” means no higher-priority link was identified, not necessarily that nothing was claimed.

**Action:** Publish the route precedence and label it as a classification. Reword the observation around category shares; use separate, non-exclusive priority/link flags to assess use of provisionals. Apply the same change to §1.9.

### R24 — High | U89–U91: aggregate agreement and Madrid counts are over-interpreted

**Issue:** Agreement with WIPO totals supports aggregate consistency, not completeness/correctness of every patent link. For Madrid, `madrid\_basis` counts all qualifying trade marks, while the Australian denominator/share is explicitly filtered by `australian\_applicant`; U91 treats them as one Australian population. The comparison also counts domestic base marks by filing year versus international applications by receipt year.

**Action:** Limit U89 to the demonstrated aggregate reconciliation. Align the Madrid numerator’s origin filter and label both counting units/time bases; avoid treating similar magnitudes as validation. Restrict §1.9’s “most inventions first filed in the US” to the observed overseas-origin standard-patent subset with recorded priority claims.

### R25 — High | U92–U94: family measures repeat across rights and ambiguous matches remain

**Issue:** U92 identifies repeated family measures on 23.14% of FY2010–FY2019 standard patents, but later prose can read as describing unique inventions/families. Its “88.29% ... through a divisional” check establishes only that the shared family contains at least one divisional, not the relationship between every repeated pair. Taking the lower family ID for 734 ambiguous application numbers is an arbitrary selection, not demonstrated resolution. Filing in an office also does not establish protection there, and citations do not directly show later inventions building on an invention.

**Action:** Label results as right-weighted family attributes; use one row per family when describing families/inventions. Flag ambiguous matches and show exclusion sensitivity. Replace protection/value/knowledge-flow claims with the measured filing, grant and citation properties; leave their substantive interpretation to later analysis.

### R26 — High | U92 / U94: the five-year citation measure is misdescribed

**Issue:** The chart source defines the measure as citing families **first filed within five years of the target family’s first priority**. That is not the same as citations received within five years. A completed priority-date window does not prove that every eventual citation or publication in that window has already been observed. U94 also asserts that larger families are more often cited without presenting that relationship here.

**Action:** Use the precise filing-window definition throughout; state the citation snapshot and publication lag limitations. If citation timing is intended, calculate from the relevant citation/publication dates. Treat the family-size relationship as a hypothesis or contextual rationale, not an established finding of this section.

### R27 — High | U95: inventor coverage calculation excludes missing cases

**Issue:** In the coverage query, `avg((inventors > 0)::int)` ignores null `inventors`; the overview shows this field contains positive counts or nulls. The resulting 100% values therefore do not measure coverage among all eligible patents. The three-inventor median is also explicitly conditional on `inventors > 0`.

**Action:** Calculate named-inventor coverage with a non-null denominator, for example `avg(CASE WHEN inventors > 0 THEN 1 ELSE 0 END)`, and separately report coverage among linked families. Recalculate the table and narrow U95’s headline to the supported population.

### R28 — High | U95–U96: inventor addresses are not proven locations of invention

**Issue:** Inventors come from one selected publication per family, not necessarily the Australian application. Country coverage is strongly selective: only 56.98% of Australian filers’ standard patents in the 2010s have a known inventor country. “Made here” overstates what an address establishes; excluding wholly unknown countries does not necessarily justify “no inventor in Australia” where some countries remain unknown.

**Action:** Say “a recorded family inventor has an Australian address”, conditional on available country data. Distinguish any known Australian inventor, all countries known overseas, and unresolved cases. Keep the selection caveat in the headline and summary; do not generalise to all inventions or Australian innovation. U95's percentage of no-country records filed only in Australia does not establish the reverse percentage: tabulate country coverage among Australia-only families before claiming that most of that group is omitted.

### R29 — High | U97: agreement with WIPO is not validation of gender estimates

**Issue:** The comparison pools inventor observations but takes an unweighted mean of WIPO’s annual shares, shifts priority years by one, and joins inventor country to WIPO origin without establishing identical definitions/populations. Australia’s aggregate agreement masks a 2.8-point difference in 2023. Agreement cannot establish accuracy, nor demonstrate that other countries’ within-country trends are reliable.

**Action:** Present this as a benchmark comparison with unresolved comparability, not confirmation. Align definitions, populations, years and weighting before validation claims. Report unmatched-name coverage by year and country; do not authorise levels or trends solely because aggregate values are close.

### R30 — High | U98 / U106–U107: gender headlines obscure selection and weighting

**Issue:** U98 averages only inventor entries with an estimate, while its headline covers inventors in Australia generally. Entries can repeat across rights/families. U107’s 2.97% missing-estimate figure concerns named inventor records and excludes provisionals with no named inventors: 21.21%, 23.62% and 15.31% in FY2024–FY2026. Its model uses applicant country as an inventor-country proxy; overseas subgroup results remain despite U97’s restrictions.

**Action:** State the denominator as inventor entries with usable estimates, not unique people or all inventors. Display naming coverage, name-estimation coverage and weighting alongside each result; qualify recent changes and limit unsupported overseas comparisons. In U106, label 1.18–1.58 as the mean among provisionals naming at least one inventor, and remove “as many are filed by one person”: an applicant is not necessarily an inventor. Replace the unconditional conclusion that the data are ready for gender analysis with these explicit conditions.

## Register updates, inconsistencies and overlooked observations

### R31 — High | U100–U102: corrected linkage does not establish true entry or unbiased origin

**Issue:** U100 says ABN linking “does not fall”, but filled trade mark coverage falls from 92.3% to 90.9%, and design coverage from 92.3% to 89.3%. U101’s “firms’ entry did not fall” concerns first **observed ABN-linked** filings: incomplete older linkage can misclassify repeat filers as new. U102 calls origin shares lower bounds before filling; a share among known-origin cases can be biased in either direction.

**Action:** Say the sharp linkage decline is substantially reduced, quantify the remaining decrease, and describe first observed filings rather than true entry. Assess historical linkage sensitivity. Report missing-origin shares without calling the known-case estimate a bound; distinguish near-complete recording from verified origin at filing.

### R32 — High | U34 → U103: the revised expedite interpretation is not fully carried back

**Issue:** U34 retains an unresolved November 2018 lead and a decision to compare only within either side of the break, then appends U103’s revision. U103 explicitly limits “no break” to IP RAPID's non-priority series; that wording should not be treated as a claim about its combined series. However, U34's broad restatement (“the fall is in where the event is recorded”) and the summary obscure the distinction: the **either-source** rate for non-priority marks rises from 4.94% in FY2018 to 14.97% in FY2019 and 24.11% in FY2020. The scope and meaning of the measure changed as well as its source.

**Action:** Replace U34’s primary interpretation and decision with the current qualified account. Clearly distinguish IP RAPID events, register events and their union. Keep the meaning of the additional register events unresolved; do not equate them with applicant requests without supporting evidence.

### R33 — High | U105: the register does not contain every provisional in the displayed reconciliation

**Issue:** IP RAPID contains 264,024 provisionals; only 264,014 are shown in both sources, leaving **ten unmatched**. The headline says every provisional is present. Finding none of 300 probed gap numbers cannot establish that all numbering gaps were never used or that IP RAPID is universally complete. “Register only, filed since release” is an output label, without a date verification shown here.

**Action:** Report the ten exceptions and the limited probe result. Show their reconciliation, verify dates for the 236 register-only records, and replace the completeness conclusion with the actual coverage demonstrated.

### R34 — Medium | U7, U12, U19, U38, U106: remaining prose/output discrepancies

**Issue:** Several smaller statements exceed or misquote their supporting output.

**Action:** Make the following targeted corrections:

|Location|Issue|Required correction|
|-|-|-|
|U7|The PBR range “37.8% to 52.3% since FY1995” comes from selected years; the full chart goes outside that range.|Calculate extrema over all relevant years or say “among the selected years shown”. Apply this rule to other selected-year ranges, including U12.|
|U19|ABNs said to differ for 5.912%–7.202% of “each type”, but provisionals are 1.739%. State differences are quoted as 1.585%/0.4425% instead of 1.589%/0.4418%.|Include the provisional exception and copy values from the current output.|
|U38|Filings “peaked in 2000” at 42,907, but 2003 is 44,634 in the same table. “Later renewals held steady” omits 8,272 in 2006.|Call 2000 a local peak and explicitly bound the stable interval; flag the later rise.|
|U106|“None filed before FY2003” contradicts the immediately noted 0.04% in FY2002.|Say “almost none before FY2003”, with the exception.|
|§1.9, U5/U6|“Second-tier patents ended in FY2021” conflicts with continuing recorded filings and the transition discussed in U4.|Describe the closure of the innovation-patent pathway and subsequent recorded filings without declaring the whole category ended.|

### R35 — Medium | U34, U92, U107: visible signals are overlooked

**Issue:** The expedite chart shows a substantial standard-patent spike around FY2013 that the rising-demand narrative skips. U92 does not examine the unusual 11.06% Google-family linkage for 2000s provisionals against 0% in adjacent decades, despite numbering ambiguities. U107 highlights lower estimated female representation among Australian individual filers but omits the reversed ordering overseas: 21.76% for individuals versus 9.52% for organisations.

**Action:** Add short descriptive notes for the FY2013 spike and provisional-linkage anomaly, with checks rather than explanations. Restrict U107’s organisational comparison to Australian filers, or explicitly acknowledge the opposite recorded pattern and its estimation limitations. U37 also calls extensions a “steady flow since” 1999–2000 despite a visible rise from 24 in 2013 to 74 in 2014 and 43–76 annually in 2015–2025; describe these periods separately without assigning a cause.

### R36 — Medium | Throughout / §1.9: evidence and amendments need one authoritative version

**Issue:** The notebook promises every observation is evidenced on the page, yet U99’s sample-validation/completeness claims, U31’s 171 excluded events and several repair explanations rely on uninspected external documents. Later corrections are appended without consistently retiring earlier claims: U0’s inventory, U7/U13→U102, U34→U103, U1/U4/U9→U104, and U17’s history limitation→U35’s assignment proxy. Summary headlines sometimes shed the original qualifications.

**Action:** Add compact supporting outputs where a claim depends on an unseen check, or label it as an externally documented assumption. Maintain one current observation and decision, moving superseded wording to a dated change log. Regenerate the summary from the corrected findings, retaining population, period, proxy and uncertainty qualifications. Define FY, ABN, PCT, cohort and censoring locally, and avoid unexplained references to “the lead”, “the review” and internal issue codes.

## Additional findings from the Lens 1 review

### R37 — High | U5 / U7 / §1.9: the innovation-patent closure is assigned to the wrong financial year

**Issue:** U5 calls FY2021 “the year innovation patents closed”, while U3 gives the closure date as **26 August 2021**. Under the notebook's end-year convention (FY2027 begins July 2026), that date falls in **FY2022**. The 7,150 peak in FY2021 is real in the saved table; its coincidence with the closure year is not. U7's closure explanation and §1.9 repeat or depend on this timing confusion. Evidence: cells `b9d7be67`, `1224a992`, `bd230f5c` and `a586b256`.

**Action:** Correct the closure to FY2022, distinguish the FY2021 peak from the FY2022 total of 4,073, and leave the reason for their timing as a question. Reconcile the date used for `filing_fy` with earliest filing, conversion and divisional dates before attributing either year's volume to the closure.

### R38 — Medium | §1.8.3 / U88: the PCT introduction contradicts its own check

**Issue:** The introduction and attachment contents say IP RAPID labels **every** PCT number `au`; the actual check reports **93.88%** of 614,973 PCT links. U88 uses the latter figure correctly. Evidence: cells `7e248d05`, `92c45e44`, `1b5e1a00` and `5dfc510b`.

**Action:** Replace “every” with the measured proportion throughout. Distinguish the number of link rows from the number of distinct PCT application numbers before calling all 614,973 rows “numbers”; the check uses `count(*)`. Keep the raw label, inferred office and unresolved cases separately identifiable.

### R39 — High | U13 / U20 / U93 / U98 / U100 / U107: origin and type may refer to different parties

**Issue:** U13 combines an **any-applicant** Australian flag with the **first applicant's** type. Those attributes need not belong to the same person or organisation. Later queries similarly combine `founding_australian` with a single `founder_type`, without demonstrating that its type belongs to an Australian founder. The founder-field construction needs checking; the notebook does not expose it. U19 demonstrates mixed-party records exist: 4,085 rights have an Australian founder who is not the first. This concern remains even after correcting current-holder versus founder fields (R04). Evidence: cells `748d4a39`, `b742978b`, `82ff7ad5`, `88373402`, `90027966`, `ae577e36` and `d633a03d`.

**Action:** Define each subgroup using country and type from the same party, or explicitly label it “rights with an Australian founder and an organisational first founder”. Count affected mixed-party records in each analysed cohort before deciding the discrepancy is immaterial. State which party supplies the ABN and postcode too.

### R40 — High | U34: opposition comparisons mix unequal follow-up and a restricted “all years” total

**Issue:** The opposition rate divides rights with a recorded opposition by rights with a recorded acceptance, including FY2026. Recent acceptances have had less time to attract an opposition, so the fall to 0.14% for standard patents does not establish a comparable decline in opposition propensity. The printed “Opposed, all years” totals of 44,744 trade marks and 1,802 standard patents actually cover **filing FY1985–FY2026**, excluding undated records and other years. Evidence: cell `79abaab2`, U34 in `898f554b`.

**Action:** Label the totals with their actual filing window. Compare opposition rates only after a stated follow-up period measured from acceptance; show eligibility counts and recording coverage. Treat recent rates as observed-to-date shares. Grant-cohort maturity alone does not establish that an opposition window is complete.

### R41 — Medium | §1.6 / attachment overviews: checked-off profiles leave important variables unexplored

**Issue:** §1.6 ticks “WIPO technology fields and IPC subclasses”, but displays WIPO fields, Nice/Locarno classes and genera without an IPC-subclass frequency profile. Several attachment counts receive only an overview: for example, `priority_claims` ranges to **167**, `founder_count` to **38**, and `assignment_count` to **9**, without a distribution or check of their upper tails. A min/max/most-common value does not fulfil the introduction's stated assessment of typical values, spread and outliers. Evidence: cells `42a1a3b4`, `6491eaa5`–`be3b2aef`, `f2ddc18c`, `8a2561f6` and `1b5e1a00`.

**Action:** Add the promised main-IPC-subclass counts and compact eligible-population summaries for analytically important counts: missing/zero shares, median, upper quantiles and extreme-record counts. Treat unusual maxima as checks, not errors already established. Mark uncompleted checklist items honestly; avoid adding relationship analysis just to fill the gap.

### R42 — Medium | §1 rules / U13 / U90: the origin-missingness rule is applied inconsistently

**Issue:** §1 says Australian shares are shown only for years with **less than 5%** unknown origin. The U7 chart applies that rule; U13 pools FY2017–FY2026 designs despite **5.062%** unknown overall and includes years above the threshold. U90's route-by-origin table also retains high-missingness design years, including FY1990–FY2000. Its conditional route shares are a different measure, but face the same selection concern. Displaying a known-case share does not make it representative of omitted records. Evidence: cells `cede563d`, `8522116c`, `748d4a39` and `5d808e57`.

**Action:** Apply the declared per-year eligibility rule consistently, or state an explicit exception and show excluded counts and sensitivity. Prefer the appropriate register-filled origin measure where justified, with the definition/period clearly stated. A missingness threshold is a reporting rule, not proof that the remaining sample is unbiased.

### R43 — Medium | U20 / U34 / U100: shares of rights are described as shares of filers

**Issue:** The representation and ABN queries count or average **rights**, not distinct applicants. U100 nevertheless calls its result “the share of filers linked to an ABN”, and “overseas filers almost always use an attorney” in U20 can be read as a person/firm-level result. A high-volume filer contributes many times, so these are different quantities. This is separate from identifying the correct party (R39). Evidence: cells `82ff7ad5`, `79abaab2` and `ae577e36`.

**Action:** Use “share of applications/rights with…” throughout this lens. If a statement about distinct filers is required, define an applicant-level denominator and place that analysis in the appropriate lens. Do not infer a change in the number of applicants from a change in a right-weighted percentage.

### R44 — Medium | Figures in §§1.0–1.3, 1.8.2 and 1.8.7: chart qualifications are incomplete

**Issue:** Several charts can mislead when read without later prose. The long-run application and grant-rate charts draw survivor-only historical periods as ordinary series. The opposition chart draws pre-recording patent zeros, although U32 says oppositions are recorded only from April 2003. The origin-share chart's end labels omit their year, although designs end earlier than other types. The 86-column missingness chart credits IP RAPID alone despite including Google Patents, register and name-estimation fields. Evidence: cells `9e32e6ad`, `9afe748e`, `8522116c`, `bc8c0472` and `79abaab2`.

**Action:** Mark known coverage breaks directly on the affected series, distinguish “not recorded” from measured zero, date endpoint labels, and name all contributing sources. Include cohort/known-case qualifications in chart captions as well as observations. For the provisional gender chart (`d633a03d`), show the FY2024 coverage break alongside the estimates rather than leaving it solely in the table below.

## Review boundary and reproducibility

These findings establish inconsistencies in the supplied notebook and identify validation needed before stronger claims are used. They do not establish whether referenced repairs, external audits or imported helper functions were implemented correctly. All 73 Lens 1 code cells have saved outputs with sequential execution counts and no saved error outputs; this does not establish that the current data or imported code would reproduce them. No notebook or repository changes were made.

**Evidence locators:** U-numbers and section headings are searchable in the notebook. Cell identifiers above are the notebook JSON's stable `id` values, not execution counts; the notation `6491eaa5`–`be3b2aef` means the consecutive cells between those identifiers. The audit preserves R01–R36 and adds eight issues, for **44 issue/action entries**. R02 remains the inherited Lens 0 finding; the other entries concern Lens 1 or shared introductory rules.

Downloaded notebook SHA-256: `1d5e51a699b82091788c75fdaff6d2706a24ba6a91df21877799677a8a357cdb`.
