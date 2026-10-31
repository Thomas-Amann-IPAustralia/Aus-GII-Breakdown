# Stage 1 notebook audit: Lens 5 reviewed in depth

**Reviewed:** 31 October 2026. **Source:** [01_univariate.ipynb](https://github.com/Thomas-Amann-IPAustralia/Aus-GII-Breakdown/blob/main/analysis/notebooks/01_univariate.ipynb), downloaded from `main` for this review.

**Format:** Follows `analysis/GPT-audit/261030/Stage01_L0-L1_Audit.md`: prioritised findings, each with an **Issue** and **Action**. R01–R32 are local to this Lens 5 report.

**Scope of this pass:** Only §5, including §§5.0–5.11, observations U22–U30, U108–U111, U113, U116 and U123. Reviewed all 43 cells: 19 code cells, their saved outputs, 11 embedded charts and 24 Markdown cells. Introductory rules and directly relevant corrections elsewhere in the same notebook were consulted solely to assess Lens 5. The earlier audit supplied the format, not the findings. No underlying datasets, imported helper implementations, external factual sources or GitHub Pages website were assessed. The notebook was not re-executed.

**Overall finding:** Most quoted values match the saved outputs. The strongest concerns are a six-month baseline labelled as twelve months, policy-response language exceeding descriptive evidence, insufficiently defined origin/event measures, historical fee comparisons that need a consistent basket, and corrections not propagated into the observations and summary.

**Priority:** **High** = affects interpretation, validity or downstream use; **Medium** = correct before relying on or circulating the findings. Implementation-dependent concerns are explicitly framed as checks. Apply corrections to §5.11 as well as the original observation.

**Read first:** R03, R06, R12, R14, R15, R23 and R29 concern definitions or analytical validity. R02 and R13 identify stale or superseded claims. A descriptive comparison can still be bivariate; a time axis alone does not make a single-series profile inappropriate.

## Scope, freshness and definitions

### R01 — High | §5 rules / §§5.1–5.4 / U111: comparisons exceed the declared scope

**Issue:** §5 reserves before-and-after comparisons for Stage 2, yet §5.4 calculates them and classifies policy responses. Origin-specific growth comparisons in U25, changes in seasonality by origin and era in U26, and renewal-fee shape by anniversary and date in U111 also compare variables. Calling these “descriptive” does not make them univariate. U116 additionally profiles industry-year records within a nominally monthly national lens.

**Action:** Retain individual series profiles, seasonality and coverage checks. Move substantive relationships and policy comparisons to Stage 2, or explicitly broaden Stage 1 to include labelled stratified descriptions. Keep quarterly/annual attachments clearly identified and place industry composition in the industries lens.

### R02 — Medium | Overview / U22–U23 / U28: inventory and outstanding-work claims are stale

**Issue:** U22 describes 35 columns, updated to 61 after fees; the overview now reports **79**. The introduction omits the RBA, national accounts and PBS additions. U23 says **15** starts were repaired, but its supporting table contains **18** series. U28 says fee changes are still missing, although U108–U111 add them. The overall notebook status still ends at U104. Evidence: cells `f231ce79`, `f49cd405`, `08d668cd`, `591b7224`, `4191f6dd`, `525a6bb3`.

**Action:** Generate the current inventory and repaired-series count from the displayed results. Mark the earlier counts as historical if retained. Replace the missing-fees statement with a reference to §5.7, distinguishing the expanded policy-event table from the timeline column that intentionally retains the original 17 events.

### R03 — High | U22 / U25–U26 / U28: “Australian filers” needs an explicit origin definition

**Issue:** Lens 5 loads pre-built origin series without exposing their construction. Elsewhere, §1.8.1 says `applicant_*` describes current holders, while founding fields describe filers; U18 demonstrates changes of country. U99/U102 also fill missing design origins, but Lens 5 does not state whether its series uses those additions. Its FY2017–FY2026 profile still contains substantial unknown design counts. That is a reconciliation concern, not proof of the unseen builder's implementation.

**Action:** Show which party, date and filled/unfilled field defines each origin series. Reconcile the design series with U102 on an identical population and period. Use filing-origin fields for filer claims, or label current-holder classifications accurately. Recalculate affected trends, seasonal profiles and policy windows if the definition changes.

### R04 — High | Introduction / U22: continuity is presented as completeness

**Issue:** A regular monthly grid and a non-null value do not establish complete recording. The “9 of the next 12” rule tests positive counts, not source completeness; the notebook itself subsequently overrides it. The first/last/total table does not demonstrate U22's “none has a gap” claim, distinguish genuine zeros from filled zeros, or prove that recent blanks arise *only* from reporting delay. Two cessation profiles have 117 observations, not the 120 implied by “ten complete financial years”.

**Action:** State that these are chosen analytical coverage windows. Display expected/observed months, internal missingness, zero treatment and cutoff reasons per series. Qualify completeness to the checks actually shown, and label each profile's effective period and observation count.

### R05 — High | Repairs / U23: missing grant dates and recording patterns are over-interpreted

**Issue:** The query labels `registered_date IS NULL` as “never registered”. It establishes absence of a recorded date, not absence of registration. The chart's universal “only the rights that survived” caption also overlooks design quarters around 1980 with over 60% lacking such dates. “Grants only for patents filed from 1979” conflicts with the stated 1.0%–1.9% recorded before 1979. Monthly plots cannot establish the separate assertion that events became weekly or daily. Evidence: `b5bcd354`, `08d668cd`, U23.

**Action:** Use “no registration date recorded”. Describe the historical patterns as evidence of uneven recording, distinguishing demonstrated discontinuities from explanations based on external documentation. Replace “only” with a measured coverage statement. Display the calculated distinct-event-day checks if retaining claims about daily/weekly recording.

## Applications, seasonality and outcomes

### R06 — High | §5.1 / U25: historical standard-patent totals can omit an origin component

**Issue:** Annual components require 12 observed months, but their standard-patent total uses `sum(axis=1, min_count=1)`. It therefore accepts any one complete origin component as the whole total. The published 1970 total is **13,160**, while the Australian component is unavailable: that series starts in July 1971. This is an incomplete-component sum unless independently reconciled. Trade marks and designs correctly require all three components. Evidence: `b86d1582`, `3c93e7e1`.

**Action:** Build all-origin totals directly from eligible dated rights, separately from origin-coverage masks, or require complete components. Show the reconciliation for historical years before describing these as total applications or calculating growth across coverage breaks.

### R07 — Medium | U24: dispersion is confused with month-to-month movement

**Issue:** The boxplot and standard-deviation/mean ratio describe the spread of monthly levels over a decade, not successive monthly changes. Trends and the second-tier closure contribute to that spread. “Most variable: second-tier patents (1.82)” silently excludes unknown-origin series with ratios **5.58** and **2.27**. The log plot also cannot display the zero PBR-grant observation. “Origin unknown” is not uniformly mostly zero: designs have **0% zero**, and trade marks **45.83%**.

**Action:** Label the result “dispersion of monthly counts over the period”; state any exclusions from rankings and retain a zero-count note. Describe unknown-origin series separately. Do not infer volatility, recording quality or the reason for an outlier from the dispersion statistic alone.

### R08 — Medium | U25 / U27: selected-year values are presented as full-period ranges or peaks

**Issue:** U25's PBR range of **264–374** follows a selected-year table, while its rolling chart rises above 400. U27 says extensions have run at **14–76** annually since 2000, but only selected years are printed. Calendar-year peaks are also easy to confuse with rolling 12-month peaks: trade mark registrations are labelled a 2021 peak, while the chart reaches a higher rolling level near its end. The underlying statistics need not conflict, but the wording does. U27 also calls 2000 the first full year of the extensions regime, although the notebook dates its start to January 1999.

**Action:** Qualify selected-year ranges explicitly, or print full-period minima/maxima and dates. Distinguish calendar-year records from rolling peaks and identify incomplete endpoints. State which growth periods are being compared rather than implying a continuous acceleration or slowdown. Reconcile the extensions regime’s start date and “first full year” wording.

### R09 — Medium | U26: pooled applications are described as Australian-origin applications

**Issue:** The January statement about “Australian filers” includes provisional applications and PBR applications, although those two series are not split by origin. Their values, **70%** and **71%**, describe all recorded applications in those series. “January's share” also suggests a share of annual filings, whereas the measure is a ratio to a centred monthly average. Evidence: `bb1c22bf`, `6fdd7a11`.

**Action:** Separate Australian-origin standard patents, trade marks and designs from the pooled series. Define 75% as “25% below the surrounding monthly average”, not 75% of annual activity. Avoid treating nationality or residence as established for an unsplit series.

### R10 — High | U26: office-working-pattern explanations are not demonstrated

**Issue:** “These follow the office's working days and processing, not demand” attributes seasonal output to mechanisms not tested here. The heatmap shows recorded event seasonality; it includes no working-day adjustment, demand lag or processing analysis. Counts also mix months of different lengths. The more recent January estimates cover six years, versus ten in earlier periods, without sample counts or spread.

**Action:** Describe the observed seasonal differences and label possible explanations as hypotheses. Show usable observations and dispersion for each monthly/era estimate. State that these are unadjusted counts; use a separate, explicitly defined working-day or processing analysis before attributing causes.

### R11 — Medium | §§5.2–5.3 / U26–U27: small-series rules and omitted observations need reconciliation

**Issue:** §5.2 promises series of at least 50 per month, but includes PBR applications and grants. U26 then mandates quarterly treatment of PBR grants by reference to U24's rule for medians below 10, although their displayed median is **13.5**. Calling March's **91%** PBR-grant value a clustering month overlooks larger June (**115%**) and August (**113%**) values. U27 omits the clearly displayed design-registration record of **9,809 in 2025**.

**Action:** State and consistently apply the aggregation criterion, with any reasoned exception. Describe the September PBR-grant peak and the actual low/high months. Add the design-registration finding, retaining the distinction between registrations and certification/examination.

### R12 — High | §5.3 / U27–U28: event labels overstate what the series measures

**Issue:** The charts label the trade mark series “oppositions and non-use removal requests”, but U27 and U28 call it simply oppositions, including the **2,309** total. Assignments are published events, not necessarily distinct transactions on their actual transaction dates. “Lapsed (ended before grant)” and “ceased (let go after grant)” impose stage and behaviour interpretations; U31 elsewhere acknowledges reversed lapse events. Lens 5 does not display its standing-event filter or complete date-selection rule.

**Action:** Preserve the full event definitions in tables, prose and summary, or separate event categories. Expose deduplication, standing-status and effective/publication-date rules. Say “recorded lapse/cessation events” unless milestone evidence supports the stronger classification. Do not interpret event volumes as failure or renewal rates without eligible denominators.

### R13 — Medium | U27 / U29: leads already revisited elsewhere remain unresolved here

**Issue:** U27 leaves the 2002 trade mark cessation/lapse pattern for the events attachment. That attachment already addresses it in **U38**, using age-at-cessation and filing cohorts. U29 treats April design lapses in 1996–2002 as a small open lead; **U39** supplies a dating-pattern explanation and pooling decision. Conversely, §5.11 upgrades U29's tentative portfolio explanation to “a portfolio transfer”.

**Action:** Link U27 to U38 and U29 to U39, stating what the notebook has established and which limitations remain. Retire obsolete forward-work instructions. Keep the portfolio interpretation tentative in the summary. These are consistency corrections, not independent validation of U38/U39's conclusions.

## Policy windows and anomalous months

### R14 — High | §5.4 / U28: the 1995 expiry comparison has only six baseline months

**Issue:** The expiry series starts **January 1995**, and the term-change event is **July 1995**. The table nevertheless labels **289.5** as the average of “12 months before”; at most January–June supplies six non-null months. The reported **−98.39%** therefore compares unequal coverage, contrary to U28's description. Its graph likewise cannot show the advertised 24 months before the event. Evidence: `b86d1582`, `280d6566`.

**Action:** Display observed versus required months for every event window and suppress a 12-month statistic unless all 12 are available. Label this as a six-month descriptive baseline if retained. Do not restore excluded historical batches merely to complete the window; explain why the advertised comparison cannot be made on the accepted series.

### R15 — High | U28–U29: coincidence and anticipation are called policy responses

**Issue:** “Rushes to file”, “anticipation shows”, “four kinds of response” and “they are the policy responses” exceed what unadjusted event-centred counts establish. A commencement-month total also combines filings before and after the exact commencement date. The 12 months after the April 2012 enactment include April 2013 commencement, so the **45.3%** increase does not isolate anticipation. Grant peaks three years later are not linked to those application cohorts.

**Action:** Use “spikes/changes around the recorded policy dates” and distinguish timing from attribution. Show exact date and window membership; separate enactment and commencement effects in later analysis. Do not infer motive, processing lag or causal response from these plots alone.

### R16 — High | U28: “none visible” confuses inadequate measurement with no response

**Issue:** All-trade-mark counts do not measure tobacco-mark use; a short filing-date window may not capture PCT entry; and missing origin dominates the early patent series. These are limitations of the selected measures. The 2018 extensions window rises **44.44%** but is grouped under “none visible” without stating why. PBR applications are dismissed as “too few to read” despite a displayed **22%** difference and no explicit precision criterion.

**Action:** Distinguish “no obvious discontinuity in this measure” from “not assessable with this measure/window”. Explain target choice, coverage and noise for each policy. Retain descriptive counts without calling them evidence of either an effect or its absence. Select later analyses on relevance and measurability as well as visible spikes; placebo dates alone do not resolve these issues.

### R17 — Medium | §5.5 / U29: the anomaly screen is not exhaustive

**Issue:** The output contains **42 series-month observations**, not necessarily 42 distinct calendar months. Screening requires a local median of at least 50 and uses a centred **25-observation** window, including the target month, with as few as 13 observations at the edges. `dropna()` can bridge missing periods. A rise sustained long enough to move the median may not be flagged; absence from this list does not establish normality.

**Action:** Report both series-month and distinct-month counts. State threshold, window and edge handling precisely; preserve calendar spacing. Separate this screen from U24's IQR outliers and explain why its flags are leads, not a complete classification of anomalies or causes.

### R18 — High | U29: origin changes and backlogs are asserted from insufficient evidence

**Issue:** Unflagged Australian/overseas counts do not establish that the unknown-origin dip reflects recoding: the threshold may miss offsetting changes. “Pauses and their backlogs” requires evidence linking low and later high counts, especially before pooling them. The asserted pause in “every kind of patent” is not demonstrated by the aggregate cessation table. “Too small to matter elsewhere” is an unsupported dismissal of recurring design-lapse troughs.

**Action:** Show all-origin totals and component movements for the origin claim. Show neighbouring months and, where available, event-level reconciliation before labelling or pooling a backlog. Otherwise retain these as unexplained recorded troughs/spikes. Resolve the design-lapse lead through U39 rather than dismissing it.

### R19 — Medium | U29: the July 2015 assignment check does not reconcile

**Issue:** The five published-day counts sum to **1,602** (395 + 646 + 325 + 163 + 73), while the monthly series reports **1,603**. The diagnostic query deduplicates application/day and inner-joins rights, potentially differing from the timeline's event definition. Current holding countries on 2 July cannot establish the parties to a transaction in 2015 or prove one portfolio transfer.

**Action:** Reconcile the one-record difference and document the counting unit. Retain “consistent with a bulk transfer” only as a hypothesis, separating current country from historical parties. Require transaction/party evidence before reporting a single portfolio transfer as established.

### R20 — Medium | U29: some precise claims are not supported by the displayed selection

**Issue:** U29 says January–May 1904 counts range from **0 to 35**, but March is absent from the flagged-month table: absence gives no value. U24 similarly assigns all its IQR outliers to particular episodes without displaying the flagged dates. “No further months are removed” is immediately qualified by excluding months before June 1904, without showing whether this changes the lens or only future analyses.

**Action:** Print the five early-month values and the IQR-outlier dates needed for those statements. Distinguish stored-data exclusions from later analytical exclusions. Replace exact or exhaustive claims with the evidence actually displayed until those checks are added.

## Fees, prices and later additions

### R21 — Medium | U108: coverage is overstated as “every version”

**Issue:** The table reports **281 versions**, **163 with text**, and **160 compilations read**. Amendment-derived spells help bridge gaps, but these totals do not prove that every version or interval has been reconstructed. Only one of the three text-bearing versions not read is explained in prose. Agreement with eight current fee examples validates those comparisons, not the complete historical series. Evidence: `94ca1db0`, `525a6bb3`.

**Action:** Say “selected fee histories reconstructed from compilations and amendments”. Reconcile all unread versions, and display each series' first/last dates, gaps, overlaps and amendment-derived intervals. Keep the current eight-fee validation explicitly scoped.

### R22 — Medium | U109: official fee baskets are presented as the cost of obtaining or keeping rights

**Issue:** The measures use selected minimum scheduled fees, excluding surcharges and other costs. Nevertheless, U109 and §5.11 say “obtaining a trade mark costs…” and “keeping a patent costs the same”. The latter compares **16,140** with **16,550** in June 2026 dollars: approximately **2.5% higher**, reasonably similar but not equal. The plotted series also has intervening rises and falls.

**Action:** Say “the selected minimum official fee basket”, preserving class/design/payment assumptions. Describe renewals as about 2.5% higher between the two selected dates, with a lower intervening level. Do not generalise to applicants' total costs or a continuously unchanged real cost.

### R23 — High | U109–U111: renewal comparisons need consistent term and cohort definitions

**Issue:** The renewal-profile code sums through the **19th anniversary** even for January 1992, while U23 says the ordinary term then was **16 years**. U109 compares “full term” baskets in January 1995 and 2026 without establishing which ordinary/extended-term anniversaries are comparable. A sum of one date's fee schedule is also not what a filing cohort pays over its later life as fees change. Evidence: `86d2dda0`, `d73937b3`, `525a6bb3`.

**Action:** Define the basket as a snapshot schedule and identify the applicable ordinary or extended term. Show a fixed, common-anniversary comparison separately from the full applicable-term total. Recalculate late-year shares and totals if the historical basket includes inapplicable anniversaries. Use dated payment paths only if making actual cohort-cost claims.

### R24 — High | §5.7 / U30 / U109: monthly real fees lack an explicit quarterly-price rule

**Issue:** The section promises that quarterly CPI is never spread across months, but monthly fee charts and January fee levels have real-valued counterparts. No visible code explains whether CPI is interpolated, carried forward, matched to the current quarter or otherwise assigned. Nominal fees are sampled on each month's first day, so a mid-month change will appear in a later monthly observation. These choices matter to event timing and real-fee comparisons.

**Action:** State the deflation formula, reference index and monthly-to-quarter matching rule. Distinguish an explicitly assumed monthly deflator from observed quarterly CPI, including treatment beyond the last observed quarter. Preserve exact effective dates for fee-change analysis and label monthly fee levels as first-day snapshots.

### R25 — Medium | U110: direction counts and “dates” need clearer denominators

**Issue:** The direction code assigns every non-increase to “cut”, without explicitly excluding unchanged amounts. This is a potential classification error unless upstream spells guarantee changes. The **39** total counts right/date combinations, not unique calendar dates. The “six dates” on which all changed fees fell contain **five distinct dates**, because November 1998 appears for both patents and trade marks. Patent renewal anniversaries also receive separate weight in the 209-rise/26-cut count.

**Action:** Exclude unchanged amounts explicitly or demonstrate that none occur. Report unique dates, right/date combinations and fee-component changes separately. Define “all” as all *changed, observed components*, not all scheduled fees. Keep “nearly always upwards” tied to its component-weighted denominator.

### R26 — Medium | U110–U111: precise fee-history statements lack displayed support

**Issue:** U110 names abolished sealing/registration fees, examination changing from $350 to $290, and a $120-to-$250 filing change. U111 gives exact switches in first payable anniversary in November 1998 and July 2012. The printed outputs contain aggregate direction counts and four snapshots, not the corresponding before/after rows. These details cannot be checked on the page as promised by the notebook's evidence rule.

**Action:** Display a compact table with effective date, component, old amount/anniversary and new amount/anniversary for each claim. Otherwise identify the statements as externally documented context rather than findings established by the shown tables.

### R27 — Medium | U113: monthly averages read as point-in-time rates

**Issue:** “The cash rate target was … 4.36% (September 2026)” can be read as the target set at a particular date. The decision only later clarifies that cash rates are monthly averages, while exchange rates are month-end values. Their juxtaposition also leaves the three exchange-rate dates implicit. The coverage checks are useful, but six selected months do not assess typical levels, spread, extrema or outliers.

**Action:** Label the measures and units in the table and headline: monthly-average target/interbank rates, month-end USD per AUD, and the trade-weighted index with its base. Attach dates to every quoted value and add compact single-series distribution/extrema summaries.

### R28 — Medium | U116: complete annual industry coverage is not demonstrated

**Issue:** The industry query reports first/last non-null financial years, not intervening counts or missing years. It cannot establish “every financial year”, or that FY2026 is a complete four-quarter annual value. The summary calls GDP, state demand and value added “complete, quarterly”, although the displayed industry measure is annual. GDP medians are calculated from overlapping four-quarter growth rates, not one growth observation per year. Evidence: `8332c66d`, `e273066d`.

**Action:** Display expected/observed years and quarter counts behind each annual total, flagging partial years. Separate quarterly GDP/state demand from annual industry value added. Describe the medians as medians of year-on-year quarterly growth rates, with their observation windows.

### R29 — High | U116: normalised chain-volume measures are presented as economic contribution shares

**Issue:** The code calculates each division's percentage as `gva_cvm / sum(gva_cvm)`. Thus “mining added the most value (12.59%)” is a normalised share of the displayed chain-volume estimates, not a demonstrated current-price share of Australian value added or GDP. The notebook does not establish additivity for the reference period or the treatment of components outside the 19 divisions; the table omits monetary units and price basis.

**Action:** Use current-price GVA with an explicit denominator for economic composition. If retaining chain-volume comparisons, state their reference period and establish whether summing components is valid for that year; label the resulting quantity precisely. Show units and distinguish industry GVA from GDP. Do not claim the printed percentages are numerically wrong without that reconciliation.

### R30 — Medium | U123: nominal expenditure and coverage qualifications need to stay with the headline

**Issue:** PBS costs are reported only in nominal dollars despite U30's commitment to show money series deflated alongside recorded values. The headline's **1.4%** prescription share applies to FY2026, not the full period, which starts at **1.06%**. The final decision says “48 months” although the attachment contains **49**, including July 2026. Fiscal-year totals demonstrate coverage only for the non-null prescription series selected by the code, not all four columns independently.

**Action:** Label expenditure as nominal and add a clearly specified real comparison or explain the exception. Date the 1.41% share and identify prescription totals as endpoint comparisons rather than a range (the intervening years reach 339.6 million and 335.1 million); distinguish 48 months in complete FY2023–FY2026 from all 49 available months. Show first/last periods, missingness and complete-year counts for all four PBS measures.

### R31 — Medium | U123: the CSV reconciliation is close but not demonstrated as exact

**Issue:** “The difference is Section 100” is asserted from rounded totals. For FY2024 the displayed figures give **18.11 − 12.61 = 5.50**, against Section 100's **5.49**; FY2025 similarly gives **5.96** against **5.95**. Rounding may fully explain this, but the outputs do not establish it. Medicine names are truncated, and the therapeutic classifications in prose are not shown as fields.

**Action:** Display unrounded annual residuals for workbook total minus Section 100 minus CSV total, with aligned periods and a justified tolerance. Do not treat rounding differences as proven data errors. Show full medicine names and identify the source of therapeutic labels, or keep the observation at medicine-name level.

### R32 — Medium | Throughout / §5.11: summaries and checked-off coverage omit material qualifications

**Issue:** §5.11 says trade mark cessations “keep rising” despite falls from **29,802 (2019)** to **28,283 (2021)**, and calls a possible portfolio transfer established. It omits unequal coverage and origin/fee-basket limitations. The 79-column overview is truncated; state demand, nominal GDP and several added series receive coverage checks but little assessment of shape or unusual values, despite the introduction's all-column profiling claim. U30's correctly distinguished monthly CPI base and quarterly observations should be preserved, not simplified into a quarterly base of 100.

**Action:** Regenerate the summary from corrected observations, retaining periods, units, uncertainty and denominator qualifications. Use “higher in 2025 than 1996” rather than uninterrupted growth. Display a compact complete variable inventory and the missing single-series summaries, or mark their profiling as incomplete. Explain internal codes only where they are needed to follow an action.

## Review boundary and reproducibility

These findings establish inconsistencies in the notebook and identify checks needed before stronger claims are used. They do not establish that an unseen builder, helper, source or legislative interpretation is wrong. In particular, origin construction, event filtering, monthly deflation, fee reconstruction and annual-account aggregation require the explicit checks identified above.

All 19 Lens 5 code cells have saved outputs, sequential execution counts **129–147**, and no saved error outputs. This does not establish that current source data or imported code would reproduce those outputs. No notebook or repository changes were made.

**Evidence locators:** Section headings and U-numbers are searchable in the notebook. Backticked cell identifiers are the notebook JSON's stable `id` values, not execution counts. All 32 entries concern Lens 5; references to other notebook sections are limited to definitions and amendments affecting its claims.

Downloaded notebook SHA-256: `1d5e51a699b82091788c75fdaff6d2706a24ba6a91df21877799677a8a357cdb`.
