# Stage 2 notebook audit: Lens 1 — IP rights

**Reviewed:** 1 November 2026. **Source:** [02_bivariate.ipynb](https://github.com/Thomas-Amann-IPAustralia/Aus-GII-Breakdown/blob/1581223dc2fbb2ce1a1c26fab77a14f459eb023a/analysis/notebooks/02_bivariate.ipynb), downloaded from `main` on the review date.

**Scope of this pass:** Only §1, including §§1.0–1.9, B1–B19 and B55: all 42 cells, comprising 22 code cells and their saved outputs, 20 Markdown cells, and all 11 embedded figures. The introduction/setup were consulted for the stated method. The eight Stage 1 audits in `analysis/GPT-audit/261030/` were considered for relevant prior findings and report format, especially L0–L1, L4 and §§8–9. No GitHub Pages website was inspected. Underlying datasets, imported helper implementations and referenced ADRs were not independently assessed; the notebook was not re-executed.

**Overall finding:** Most quoted numbers match the saved results, and the notebook usefully distinguishes associations from causes in several places. However, some selected populations are presented as all applications, recorded proxies become claims about behaviour or value, and B55's later coverage warning has not been propagated through earlier conclusions. Several analyses already condition on multiple variables despite the “two variables at a time” framing.

**Priority:** **High** = affects interpretation, validity or downstream use; **Medium** = correct before relying on or circulating the findings. Implementation-dependent concerns are explicitly checks, not established defects in unseen code. Apply corrections to the corresponding §1.9 row as well as the original observation. R-numbers are local to this report.

**Read first:** R06–R09, R16–R18 and R25–R29 concern populations, outcome definitions and consequential interpretation. A stratified comparison can be useful without establishing an independently adjusted relationship.

## Scope, screening and inference

### R01 — High | §§1.1–1.8: several analyses exceed a strictly bivariate scope

**Issue:** B6 compares representation and grant within origin/type groups and examination-request subsets; B8 adds technology; B12 ranks citations within field/year and then compares filer groups within reach; B13 conditions expedite–survival comparisons on filer. These are conditional analyses involving more than two underlying variables. B55 additionally changes the unit to families and annual national shares. Merely naming possible third factors, or displaying separate pairs, is not itself multivariate analysis.

**Action:** Label these as stratified exploratory comparisons and state the conditioning variables and unit. Either explicitly permit this scope in Stage 2 or move adjusted/compositional conclusions to Stage 3. Do not call stratification proof that other factors have been controlled. Evidence: `1f1747cd`, `3658ea02`, `7a25fb76`, `fd83230a`, `b38c4ca4`.

### R02 — High | Screening method / B1–B4: the shared “strength” scale is overstated

**Issue:** A common 0–1 range does not make absolute Spearman correlation, rank correlation ratio and corrected Cramér's V interchangeable. Spearman measures monotonic association, not relationships “in any shape”; zero does not establish no relationship. The blanket claim that the measures give identical values for binary cases also needs qualification, particularly with finite-sample correction. Universal small/moderate/strong labels can conceal different category structures.

**Action:** Retain each statistic's name and meaning; call 0.1 a screening convention rather than a common substantive effect. Correct the monotonicity explanation and demonstrate any asserted equivalence under the actual implementation. Define replication for categorical pairs using corresponding category patterns, not just two unsigned association magnitudes. Evidence: `0a9fee61`, `474fc7fd`.

### R03 — High | Throughout: intervals and replication need their independence assumptions

**Issue:** Distinct application rows can share a family, applicant or inventor. B12 repeats family citation attributes; B17 joins family inventors to applications and bootstraps patents. Separate filing decades need not contain independent families or filers. Wilson intervals, row-based standard errors and patent resampling do not automatically capture this dependence, linkage error or name-estimation uncertainty. Thus “not an accident of one decade” is too conclusive.

**Action:** Describe the result as consistency across two cohorts. Report application and distinct-family counts, overlap between periods, resampling unit and pair-specific complete-case sizes. Assess family/applicant clustering where relevant, and distinguish model-based intervals from coverage/measurement uncertainty. Treat intervals on the strongest selected screen versions as exploratory. Evidence: `d97bc865`, `474fc7fd`, `197b90a4`, `7a25fb76`, `f243256f`; Stage 1 L0–L1 R25/R30.

### R04 — High | §1 rules / B4: screening does not visibly enforce all eligibility rules

**Issue:** The screen includes overseas gender estimates despite the Australia-only rule, lifetime medians without a visible censoring explanation, and PBR grant-time comparisons for FY2010–FY2019 despite Stage 1's substantial unfinished cohorts. The FY2000–FY2009 second-tier sample spans different patent regimes. Pre-FY2003 founder limitations are acknowledged in §1.2 but also affect earlier-decade comparisons elsewhere.

**Action:** Show a compact eligibility register by variable/right type: valid years, subtype, missingness, censoring and historical-party limitations. Exclude unsupported comparisons or mark them as diagnostics; verify how the screen prepares censored lifetimes. Do not treat the 223 leads as equally interpretable substantive findings. Evidence: `d97bc865`, `09d32113`, `474fc7fd`, `2c348216`; Stage 1 L0–L1 R10/R16/R20–R22/R29.

### R05 — Medium | B1: the replication denominator and headline are inconsistent

**Issue:** The printed 5,207 counts rows with a replication strength, whereas the 0.859 correlation uses rows with both strengths and then excludes “by construction” pairs. B1 assigns that correlation to all 5,207. Its headline says “most” of the 223 leads replicate, although replication is a prerequisite for being a lead. The 369 non-replicated pairs are a separate category; 264/1,649 lead pairs also change strength by more than 0.1.

**Action:** Print the exact correlation sample size from the filtered frame and distinguish measured pairs, lead pairs and grouped leads. Say all retained leads pass the stated replication rule, while retaining the substantial effect-size variation. Avoid implying that the displayed zero “not significant” verdicts explains every screening exclusion without documenting verdict precedence. Evidence: `9878ed51`, `2c348216`.

## Parties, representation and grant outcomes

### R06 — High | Shared `FILER` / B5–B18: subgroup identities need reconciliation

**Issue:** `FILER` combines an any-founder Australian flag with one `founder_type`; the notebook does not establish that country and type describe the same party. In B12, unlike most other queries, a null `founding_australian` reaches the `ELSE 'overseas '` branch; checking only the resulting `filer IS NOT NULL` does not remove it when type is known. Some screen findings also use current-applicant fields while prose says filer.

**Action:** Define country/type using the same selected party, or explicitly label the mixed-party classification. Preserve unknown origin as a separate category and count affected rows before rerunning B12. Identify founder versus current-holder fields beside each result. Evidence: `ea1827ce`, `7a25fb76`, `474fc7fd`; Stage 1 L0–L1 R04/R39, L2 R51.

### R07 — High | B2/B4–B6/B10: recorded representation is not verified help at filing

**Issue:** Serving five applicants is an attorney proxy, not verified professional status. B6 acknowledges that representation can be recorded at any time, yet headings and B5 say applications were “filed alone”. No agent on the record does not establish absence of legal help. The 1,148 in B6 are application rows, not 1,148 organisations; the suggestion of in-house patent staff is unsupported.

**Action:** Use “applications classified as self-represented under the recorded-agent rule”, state its timing and validate the proxy before interpreting access to assistance. Replace the staffing explanation with a hypothesis. Keep percentages application-weighted and explain that they do not describe proportions of distinct filers. Evidence: `ea1827ce`, `20488ed2`, `fb8284f8`; Stage 1 L0–L1 R15/R43, S8–S9 R08.

### R08 — High | B6/B13/B19: missing grant dates and examination requests become completed outcomes

**Issue:** `registered_date IS NOT NULL` measures recorded dates; its complement is called “never granted” in B19. B6's “among examined” denominator is examination requested, not examination completed. Its conditional grant calculation uses all recorded grants as numerator, rather than explicitly counting grants whose examination request is recorded. Legal event ordering does not guarantee both dates are present in the data.

**Action:** Label date presence accurately; reconcile grants/status/events and show unresolved cases. Count the numerator and denominator from the same request-recorded subset. Say “examination requested” throughout, and show remaining pending/outcome-unknown shares before calling years decided. Evidence: `ea1827ce`, `1f1747cd`, `d1239afb`, `5ef8906d`; Stage 1 L0–L1 R05/R09/R18.

### R09 — High | B3 → B6: the near-universal design registration claim uses a selected population

**Issue:** B3 identifies 100% unknown raw origin among lapsed/withdrawn designs, alongside non-zero missingness among ceased/registered designs. B6 nevertheless concludes designs register 99.4%–100% “whoever files”, using records with known founder origin, type and representation, without showing recovery of unsuccessful applications. B3's instruction to use filled origin is not demonstrated in this founder-based query. Registration without examination does not explain near-universal registration among all applications.

**Action:** Withdraw the general registration conclusion. Reconcile all designs against the analytical subset by status and exclusion reason; verify whether register filling reaches the required founder fields. Recalculate on a defensible population or label the result as conditional on selected records. Narrow B3's claim that unknown-origin designs are exclusively never-registered cases. Evidence: `5c0b8418`, `ea1827ce`, `1f1747cd`, `20488ed2`; Stage 1 L0–L1 R12/R42.

### R10 — Medium | B2/B7: timing labels and denominators exceed the visible checks

**Issue:** B7 says the earlier origin gap did not occur, although the difference is 0.077 years with interval 0.044–0.126: it is small, not absent. The table uses `size` for request-to-grant durations, which includes rows missing a request date, and only filters non-negative application-to-grant time. B2's correlation partly compares a total with a component; “the applicant … sets the pace” and “the part the office controls more” add untested explanations.

**Action:** Say the earlier difference is much smaller and below the chosen lead criterion. Show valid counts for each duration and check request/grant chronology separately. Identify the shared time component, define each route's clock, and present responsibility for delay as a hypothesis. Evidence: `2c348216`, `1468d831`, `20488ed2`.

## Survival, renewal and expedited examination

### R11 — High | §§1.2/1.4: survival eligibility and anniversary calculations need explicit checks

**Issue:** `lifetimes()` explicitly filters non-negative duration and known `in_force`, but does not explicitly filter grant/registration; that eligibility may be embedded upstream and is not shown. It rounds durations to 0.1 years before estimating survival, potentially moving events across renewal anniversaries. Cohorts use `filing_fy`, while patent survival uses the date of patent. Source-specific censoring dates and excluded counts are absent here.

**Action:** Show whether the duration field guarantees the stated granted/registered population, and expose entry, endpoint, censoring and exclusion rules. Check anniversary estimates with exact durations and specify before/after-anniversary evaluation. Reconcile cohort dates with the survival time origin and report at-risk support through plotted tails. Evidence: `ce1d1389`, `287a3efb`, `fd83230a`; Stage 1 L0–L1 R21–R22.

### R12 — High | B8–B10/B14: survival is described as renewal behaviour and expected value

**Issue:** The outputs estimate survival of eligible recorded rights, not directly observed renewal transactions. B10/B14 and §1.9 call them renewal rates; §1.2 frames duration as owners' expected value. Selection on eventual grant also includes elapsed time before grant in the patent clock. Censoring adjustment does not remove selection, historical omissions or distinguish reasons for an end event.

**Action:** Use “estimated share still in force at the stated anniversary”, retaining cohort and eligibility qualifications. Present renewal behaviour and private value as possible interpretations requiring separate evidence. Avoid attributing a right's full lifetime to its founding owner where ownership may change. Evidence: `2823d69c`, `fb8284f8`, `321301d0`, `12ee8be5`; Stage 1 L0–L1 R21, S8–S9 R10.

### R13 — Medium | B8/B9: within-field persistence and candidate explanations are overstated

**Issue:** The within-field origin comparison is shown only for FY2005–FY2009: Australian organisations are higher in 23 of 32 eligible fields, lower in nine, with gaps −15.8 to +28.6 points. This does not establish a universal independent origin relationship or replication of the within-field result. B8 cites B6 for Australians being granted less often than overseas applicants, but B6 displays Australian representation comparisons, not that origin comparison.

**Action:** Separate the replicated pooled association from the single-period within-field check. Show field-specific differences and intervals, exclusions and a second-period check before strengthening the claim. Remove the unsupported grant-origin premise or add its evidence. Correct the family-reach reference from B10 to B11 and retain selection/firm size as hypotheses. Evidence: `3658ea02`, `fb8284f8`, `1f1747cd`.

### R14 — High | B13: “Simpson's paradox” and a composition-only explanation are not demonstrated

**Issue:** The pooled expedite gap changes from −2.6 to +8.1 points, but subgroup gaps also change: Australian organisations go from −9.2 to +3.2 points; overseas organisations remain positive. Showing a changed filer mix does not quantify how much of the pooled change it explains, and the subgroup directions do not display a uniform reversal against the pooled result. “Holds only” also obscures the persistent negative association for Australian individuals.

**Action:** Describe heterogeneous associations and a changing composition. Reserve “Simpson's paradox” or “composition effect” for a demonstrated decomposition/standardisation using comparable populations. Say the positive association repeats for overseas organisations, while the negative individual association also merits reporting. State the ten-year endpoint; five-year results differ. Evidence: `d1239afb`, `fd83230a`, `321301d0`.

### R15 — High | B14: expedite meaning and the dismissal threshold are insufficiently established

**Issue:** The analysis assumes non-priority trade mark expedite flags represent applicants' requests. Stage 1 explicitly left the meaning of additional register events unresolved. Restricting filing years to before November 2018 does not itself restrict the dates of later examination events, and `coalesce(priority_claims, 0)` treats missing as no claim. Separately, a 1–4-point gap cannot be compared directly with the screen's dimensionless 0.1 threshold.

**Action:** Identify the flag's source, event date and interpretation; separate unknown priority status and verify the relevant event window. Calculate an appropriate association or declare a substantive percentage-point criterion before deciding “not a lead”. Report the uncertainty of the differences rather than dismissing them by units that do not match. Evidence: `6b3d1c4e`, `d1239afb`, `fd83230a`, `321301d0`; Stage 1 L0–L1 R32.

## Family reach, citations, routes and inventor location

### R16 — High | B11: offices, countries, Australia-only families and overseas selection are conflated

**Issue:** B11's headline says countries, but the measure counts offices. `family_offices = 1` alone does not verify that the one linked office is Australia; that depends on matching and family construction. The comparison includes only linked Australian-office applications, so overseas families are already selected for reaching Australia. It cannot establish how Australian and overseas inventors generally internationalise.

**Action:** Label recorded family office counts and the linked-application denominator. Verify the single office's identity and matching, distinguish applications from unique families, and qualify “Australia only”. Restrict the origin comparison to the selected Australian application corpus rather than general international filing behaviour. Evidence: `197b90a4`, `7bb3ecee`; Stage 1 L0–L1 R25, L4 R23–R24.

### R17 — High | B12: the five-year citation window remains misdescribed

**Issue:** The Stage 1 audit identified `family_citations_5y` as citing families first filed within five years of the target family's first priority, not necessarily citations received within five years. B12 and its chart retain the latter wording. Ranking within Australian filing year and main field does not automatically align family priority age, publication exposure or citation coverage.

**Action:** Use the exact citing-family filing-window definition and observation snapshot. State the ranking population, ties and chosen year basis; assess family-priority-age and coverage sensitivity. Describe recorded citation ranks rather than validated influence or value. Evidence: `01cdcbf3`, `7a25fb76`, `7bb3ecee`; Stage 1 L0–L1 R25–R26, S8–S9 R11.

### R18 — High | B12: reach does not establish the principal explanation for citation differences

**Issue:** Stratified comparisons show attenuation/reversal, but do not quantify a share “explained” by reach or establish it as the main third factor. The later two-to-four-office gap is still 10.8 percentile points; the five-plus gap grows from 0.6 to 7.1 points across periods. “Same reach” means broad bins. The SQL's final `ELSE` also puts null office counts into “5 or more offices” if any occur.

**Action:** Label the bins and explicitly exclude/report missing reach. Present the conditional differences without claiming a dominant mechanism; test composition and coverage on consistent cohorts before attribution. Remove the claim that reach and citations are two readings of the same expected value. Carry B55's historical warning into this analysis. Evidence: `7a25fb76`, `7bb3ecee`, `b3ed6e03`.

### R19 — Medium | B15: route shares and the cited effect size describe different classifications

**Issue:** The route table uses founder origin/type, but the quoted 0.243/0.290 screen statistic uses `applicant_type`, which Stage 1 identifies as current-holder information. “Divisionals doubled” describes shares for organisations, not a demonstrated doubling in counts or every filer group. Exclusive route categories also hide precedence: direct is a residual category, not verified absence of priority links.

**Action:** Use the matching founder-based statistic, explain route precedence and identify both numerator and denominator. Say divisional shares rose from 11.6% to 22.4% for Australian organisations and 7.1% to 15.6% overseas. Treat longer pendency as a question for analysis, not an observed consequence of this table. Evidence: `c32476f3`, `46f31d3d`; Stage 1 L0–L1 R23–R24.

### R20 — High | B2/B16: inventor addresses become locations of invention

**Issue:** “Made here” and “inventions made in Australia” overstate a recorded inventor-country flag, drawn from family-linked information. The 14.51% is conditional on available founder/inventor classifications; selective missing countries can change it. A false Australian-inventor flag does not necessarily mean every inventor is known to be overseas. The acknowledged exclusion of inventions filed only abroad does not resolve these issues.

**Action:** Say “applications linked to a family with a recorded inventor address in Australia”, and retain the exact denominator. Separate known Australian, all-known-overseas and unresolved cases; report coverage by origin, reach and period. Remove location-of-invention wording from headings, outputs and §1.9. Evidence: `2c348216`, `b30fd8d7`, `46f31d3d`; Stage 1 L0–L1 R27–R28, S8–S9 R13.

## Name-based gender estimates

### R21 — High | §1.6/B17–B18: benchmarking is treated as validation

**Issue:** The introduction says WIPO confirms Australia as the one reliable country, although Stage 1 found unresolved differences in populations, periods and weighting. The 93.38% coverage is among inventor entries already selected as Australian, not all inventors/applications. Patent bootstrapping does not include uncertainty or systematic error in the name probabilities, and repeated family/person entries are not unique inventors.

**Action:** Call WIPO a benchmark comparison, not confirmation. Keep the denominator as inventor entries with usable estimates; show naming, country and estimation coverage separately by group/period. Explain the limited uncertainty captured by intervals and use neutral “name-based estimated share” labels throughout. Evidence: `ec39ffe6`, `f243256f`, `a9201297`; Stage 1 L0–L1 R29–R30.

### R22 — High | B18: applicant country/state is substituted for inventor geography

**Issue:** Provisionals use applicant country for name estimation and `founder_state` for state comparisons. These are not observed inventor locations. Overseas provisional estimates remain in the table and prose despite the Australia-only restriction, while the headline “organisations … more” omits the opposite later overseas ordering: individuals 16.60%, organisations 6.66%. “Western Australia and New South Wales lowest” also omits the NT's 13.92%, unless restricted to the seven eligible jurisdictions.

**Action:** Label provisional estimates by applicant classification and founder state, explicitly stating the geographic proxy. Restrict the organisational headline to Australian-classified applications; remove unsupported overseas comparisons or clearly separate them as unvalidated diagnostics. Apply the ≥500-entry eligibility qualification to state rankings and distinguish states from territories. Evidence: `4e794326`, `a9201297`; Stage 1 L0–L1 R30/R35.

### R23 — Medium | B17: interval overlap and ranges do not establish relative importance

**Issue:** Overlapping separate 95% intervals are not a direct test of the difference. “Field matters more than filer” compares a range across selected fields with grouped filer estimates, not like-for-like effects. B17's specific claim that organisations favour biotechnology/pharmaceuticals and individuals transport/civil engineering is not tabulated in this follow-up; B4's generic association is insufficient support.

**Action:** Estimate the organisation–individual contrast and its interval in each period. Say the displayed field estimates vary more widely, limited to the 12 eligible fields, without implying independent explanatory importance. Show the claimed field-by-filer composition or keep it as a hypothesis for Stage 3. Evidence: `f243256f`, `a9201297`, `2c348216`.

### R24 — Medium | B17/B18: stable ranks obscure substantial changes in levels

**Issue:** Textile/paper machinery falls from 39.7% to 15.9% in the field chart, despite the emphasis on rank consistency. For provisionals, the plotted estimates fall sharply from FY2012 to FY2014 for both Australian groups: organisations 27.07%→18.47%, individuals 23.54%→15.39%, while naming coverage remains near complete. The later FY2024 coverage issue does not explain that earlier pattern.

**Action:** Add short descriptive notes for both changes and test cohort composition, source and estimation consistency before interpretation. Do not infer a recording break or a real population change from the plot alone. Say ranks are correlated, not that every field/state keeps its position. Evidence: `f243256f`, `4e794326`, `a9201297`.

## Recorded ownership endpoints and the later coverage amendment

### R25 — High | B19: ownership endpoints are interpreted as the export of the most valuable rights

**Issue:** The query selects an Australian founder and no recorded current Australian applicant. This is an endpoint classification, not a verified transfer history, location of invention or location of economic returns. The conclusion that these are the rights owners “valued most” is not measured by grant and reach. It also omits joint ownership, possible intermediate overseas ownership and later returns to Australian ownership.

**Action:** Describe applications with an Australian founding-party flag and an exclusively overseas current-holder classification. Treat transfer histories, valuations and value captured abroad as separate research questions. Preserve missing-party and historical founder limitations; avoid “rights that leave” as a factual economic conclusion. Evidence: `8691ee1b`, `5ef8906d`, `7546a9f3`; Stage 1 L0–L1 R16, S8–S9 R07.

### R26 — High | B19: conditional rates, event ordering and follow-up need separation

**Issue:** The table estimates the overseas-held share within reach/grant groups, not the composition of patents that moved. In the older cohort, 539 of 1,219 overseas-held records are in the one-office category, versus 421 in five-plus offices, despite “the rights that leave are … wide”. Reach and grant are observed at the snapshot, not necessarily before ownership changed. Acknowledging unequal decades does not adjust differing exposure within groups.

**Action:** Say overseas-only current holding is more frequent among the observed wider/grant-recorded groups. Distinguish that probability from the composition of overseas-held records. For predictive or transfer interpretations, establish event order and compare common follow-up windows; retain descriptive endpoint comparisons if histories cannot support this. Evidence: `5ef8906d`, `7546a9f3`.

### R27 — High | B55: the purported B11 recheck changes population, route and unit

**Issue:** B11 uses founding origin/type and non-null office counts. B55 instead uses current `australian_applicant`/`applicant_type` and non-null family IDs. Its “direct” category means no recorded PCT number, potentially including convention, Australian-priority and divisional records. The WIPO comparison then deduplicates families, combines standard and second-tier patents and uses calendar priority years; B11 is standard-application-weighted by financial filing decade.

**Action:** Repeat B11 on the identical founder-defined population and denominator, then show any holder-based sensitivity separately. Rename the binary route “recorded PCT link / no recorded PCT link”. Reconcile family definitions, origin, years and WIPO's foreign-oriented measure before treating the annual comparison as validation of B11. Evidence: `197b90a4`, `8ff5a116`, `b38c4ca4`; Stage 1 L4 R12/R23–R26.

### R28 — High | B55: coverage concerns become an unquantified cause and an unsupported safe cutoff

**Issue:** A PCT link does not itself demonstrate entry into several national offices, so calling Australia-only records “not a believable practice” is not a validation test. The checks do not quantify how much of B11's fall is missing data, distinguish source coverage from corpus matching, or establish that FY2010 onward “stands”. Different endpoints do not show WIPO was flat throughout, and correlations based on 15/17 annual changes lack uncertainty or serial-dependence checks.

**Action:** Report evidence of possible coverage/matching problems without allocating “most” of the change to them. Verify a sample's expected publications and links; validate citations separately from office counts. Label FY2010 as a provisional restriction with unresolved coverage, retain annual variation and avoid claiming replication/validation from endpoint agreement. Evidence: `8ff5a116`, `b38c4ca4`, `b3ed6e03`; Stage 1 L4 R24–R26.

### R29 — High | B11/B12/B55 / §1.9: later amendments have not replaced earlier conclusions

**Issue:** B55 restricts older Australian family comparisons, yet B11's headline still says the gap narrowed, §1.9 calls B11/B12 replicated, and both remain unconditional Stage 3 leads. B55 itself is marked “yes” under replication despite its incomparable samples and contrasting time-series results. Its reference to “B8's reach” is also inaccurate: B8 reports survival and merely names reach as a possible factor. The opening completion inventory omits B55.

**Action:** Maintain one qualified current account: mark older family comparisons provisional, reassess affected screen leads and B19's reach comparison, and distinguish B8's survival evidence from its reach hypothesis. Rewrite §1.9 from corrected findings, including B55's own limitations, and update the status/contents. Do not simply substitute B55's stronger explanation for B11's earlier uncertainty. Evidence: `b29e8754`, `7bb3ecee`, `fb8284f8`, `b3ed6e03`, `12ee8be5`.

## Remaining accuracy and presentation checks

### R30 — Medium | B2/B4/B10/B11: smaller absolute claims exceed their supporting outputs

**Issue:** B2's “individuals have no ABN” and B4's “attorney markets are local” turn associations into universal/explanatory statements. B10 says every interval is within about one point, but overseas individuals' trade mark intervals span 36.5%–39.5%, and Australian individuals' earlier design interval spans 25.6%–28.6%. B11's Australian-individual later Australia-only interval is 58.6%–61.2%, wider than “within about a point”.

**Action:** Use “less often has a recorded ABN” and “a regional association in recorded agents”, with exact populations. Remove blanket precision claims or quote the relevant intervals. Keep these smaller qualifications in chart captions and the summary. Evidence: `2c348216`, `287a3efb`, `fb8284f8`, `197b90a4`, `7bb3ecee`.

### R31 — Medium | Screen tables and charts: important evidence is truncated or lacks standalone qualifications

**Issue:** The lead tables truncate directions and candidate third factors to 90 characters, limiting verification of the promised evidence. The heatmaps use outlines, dots and hatching without a nearby explanatory key in the notebook text. Several figures say filer, renewal or Australia-only without the selection/proxy limitations discussed elsewhere; field-chart captions say a threshold is met “in a period” although plotted comparisons require both periods.

**Action:** Provide untruncated lead details, pair-specific counts and a short symbol key. Keep population, source, period, threshold and proxy definitions in each figure/table caption. Explain internal Q/ADR/OQ references briefly and link them without requiring the reader to reconstruct project history. Evidence: `7455cfd8`, `474fc7fd`, `876656ad`, `f243256f`, `5ef8906d`.

## Review boundary and reproducibility

This report contains **31 issue/action entries**. It reviews the notebook's displayed code, saved tables/figures and commentary; it does not certify underlying records or the implementation of imported helpers. All 22 Lens 1 code cells have saved outputs, sequential execution counts **2–23**, and no saved error output. This does not establish that the current data and dependencies would reproduce those outputs. No notebook, source-code or website changes were made.

**Earlier audit references:** L0–L1 = `Stage01_L0-L1_Audit.md`; L2–L7 = `Stage01_L2_Audit.md` through `Stage01_L7_Audit.md`; S8–S9 = `Stage01_S8-S9_Audit.md`, all in `analysis/GPT-audit/261030/`. Relevant findings were used as context, not assumed to prove an unseen implementation defect. Lens-qualified R-numbers prevent confusion between audit files.

**Evidence locators:** B-numbers and section headings are searchable. Eight-character identifiers refer to the notebook JSON's stable cell IDs, not execution counts. Numerical examples use saved outputs or direct arithmetic on their counts. The report follows the existing series' scope, priority, thematic sections and **Issue / Action** layout.

Repository commit: `1581223dc2fbb2ce1a1c26fab77a14f459eb023a`.

Downloaded notebook SHA-256: `441679240f0e884486b681493f87604fa327223a9ae369fcdd263fd84218ede2`.
