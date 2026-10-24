# Aus-GII-Breakdown: Consolidated Data Audit and Research Gap-Closure Plan

**Consolidated:** 24 October 2026  
**Underlying audits:** 23 October 2026  
**Repository reviewed:** `Thomas-Amann-IPAustralia/Aus-GII-Breakdown`, `main`, commit [`38b5ddd9d5d764b683ae076c308d9285ee459357`](https://github.com/Thomas-Amann-IPAustralia/Aus-GII-Breakdown/tree/38b5ddd9d5d764b683ae076c308d9285ee459357)

**Purpose:** Provide one evidence and action document for correcting data problems, resolving remaining gaps and building research that helps IP Australia identify interventions likely to create additional public value.

This document consolidates the three supplied reviews. The earlier audit is reproduced in full within the expanded audit, apart from its added update notice and second-pass findings. That duplicated material appears only once here. All **42 audit findings** and all **seven research workstreams** are retained, grouped by topic. Original finding numbers remain identifiable as **F01–F42**; the closure plan’s priorities remain **R1–R7**. Recommendations that overlap are connected to their supporting findings, and the delivery sequence reconciles data repairs with the proposed research programme.

**Status:** Findings and counts retain the evidence strength, dates and limitations of the original reviews. This consolidation is not a new repository audit or a fresh verification of external sources. References to “current”, “latest” or live-source availability in the inherited evidence refer to the original review, unless explicitly dated otherwise. Research workstreams remain proposals: they have not been implemented or shown to produce causal findings. Source availability, licences, coverage, linkage permissions and comparability still require implementation checks.

**Contents**

- [1. Overall assessment, evidence and delivery sequence](#1-overall-assessment-evidence-and-delivery-sequence)
- [2. Ingestion, revisions and data integrity](#2-ingestion-revisions-and-data-integrity)
- [3. Applicants, firms, identifiers and geography](#3-applicants-firms-identifiers-and-geography)
- [4. Innovation indicators and economic context](#4-innovation-indicators-and-economic-context)
- [5. Participation, business outcomes and public research](#5-participation-business-outcomes-and-public-research)
- [6. Dates, official fees, medicines and public outcomes](#6-dates-official-fees-medicines-and-public-outcomes)
- [7. Policy evaluation and intervention decisions](#7-policy-evaluation-and-intervention-decisions)
- [8. Shared implementation requirements and completion criteria](#8-shared-implementation-requirements-and-completion-criteria)
- [9. Read-only reproduction queries](#9-read-only-reproduction-queries)
- [10. Repository locations and traceability](#10-repository-locations-and-traceability)

## 1. Overall assessment, evidence and delivery sequence

The corpus contains a mixture of genuine source gaps, recoverable omissions, deliberate exclusions, misclassification and misleading completeness measures. Treating these all as “missing data” obscures both the remedy and the limits of the evidence.

The clearest value-loss example is the OECD IP tax-regime table: **2,639 non-empty source values become 2,639 null values**. The expanded audit also identifies CER schema errors and duplicate formats, omitted PBS coverage, ignored RDTI amendments, conflated AusTender releases and contracts, omitted firms, and lost ABS annotations and units. These need correction before affected measures support research conclusions.

Some improvements need no new data source: use the existing patent-number conversion in join profiling, expose OECD R&D observations already held, preserve unknown applicant countries, and repair party attribution. Other public sources can add current-code World Bank trade mark series, international postal references, ARTG registration dates, historical official fees, partial border-seizure statistics, business-owner denominators and public-research commercialisation evidence.

These improvements cannot automatically supply absent applicant addresses, unpublished or suppressed observations, representative small-firm financial panels, or the counterfactual required for causal claims.

### Evidence base and limits

The original audits inspected repository documentation, source modules, analysis construction, notebooks, manifest and committed profiles; queried relevant local Parquet tables; compared selected processed data with raw CSV/XLSX inputs; tested World Bank APIs; downloaded six GeoNames postal files for an actual join trial; and researched publisher documentation and alternative sources. The second pass used a fresh clone of the same pinned commit and examined source selection, workbook layouts, duplicate keys, amendments, joins, units, dates and refresh behaviour.

**Access limitation:** The repository’s **22 R2-only processed tables** and relevant large raw extracts could not be independently reopened because R2 credentials were unavailable. This affects full IP RAPID party/events data, Google Patents members, full IPLORD, ASIC and TM-Link. Their committed profiling results describe an earlier run, rather than a new source-level verification. The IPLORD publisher endpoint also returned HTTP 403. Code-level mechanisms are distinguished from measured downstream effects throughout the findings. No repository code or hosted data was changed by the audits or this consolidation.

Unless explicitly identified as a live API result or the postal trial, counts describe the pinned snapshot. They are descriptive findings, not economic-effect estimates. A proposed repair is not evidence that it has succeeded.

The second pass also reported useful positive checks:

| Check | Reported result | What it establishes |
|---|---|---|
| SHA-256 against manifest | All 586 manifest-listed repository files matched | Agreement with the saved manifest, not publisher completeness or transformation correctness. |
| Local Parquet row counts | All 130 local tables matched their manifest counts | Saved table/count consistency, not retention of values or correct semantics. |
| Mesh-block keys | 368,286 rows and 368,286 distinct keys | Key uniqueness in the checked table. |
| POA-to-SA2 population weights | Sum to one within floating-point tolerance | Internal weight consistency, not suitability for every variable or geography vintage. |
| OpenAlex work IDs | 2,456,961 stored IDs are unique | Stored-key uniqueness, not complete research coverage. |
| NHMRC keys | 12,224 application/round keys are unique | Key uniqueness, not complete grant dates. |
| PBS cost components | Patient plus government cost reconciles within two cents for every local item-month row | Arithmetic consistency within the selected coverage, not completeness of PBS supply. |

The second pass found material issues missed by the first. An unqualified claim that nothing else is wrong or missing is therefore not supported.

### One delivery sequence for repairs and research

The audits prioritise correctness; the closure plan prioritises additional research value. Both can be retained by treating repairs as prerequisites for affected analyses while beginning research design and access enquiries alongside them. The ordering below is an editorial synthesis of the supplied recommendations, not a new estimate of effort or impact. R1–R7 retain the closure plan’s original research-priority order.

| Stage | Work | Principal output and decision gate |
|---|---|---|
| A. Correct demonstrated loss, misclassification and aggregation | OECD mixed values (F01); unknown-country handling (F04); CER schemas and duplicates (F29–F30); PBS selection (F31); RDTI revisions (F32); AusTender release identity (F33); firm membership/party attribution (F34); ABS cells and units (F36). | Rebuilt affected tables, before/after counts and reconciliation at the correct observation unit. Do not use affected measures as validated evidence until these checks pass. |
| B. Repair coverage, joins and interpretation | Patent profiling on `au_application` (F06); business-age proxy (F35); research-to-patent selection (F37); citation/timeline windows (F25/F38); refresh behaviour (F39); PHIDU/PBR lens coverage (F40). | Raw/normalised identifiers, explicit coverage intervals, correct labels, link bridges and source vintages. |
| C. Resolve access-limited uncertainties | Raw IPLORD headers and modal classes (F08–F09); PBR parties (F10); ASIC/ABR links (F11); renewal events (F25); Google and TM-Link joins (F06–F07/F28). | Right/role/decade completeness profiles, conversion/collision checks, multi-party validation and like-for-like comparison with official totals. Keep unresolved cases visible. |
| D. Recover targeted public evidence | World Bank trade mark codes (F02); separate OECD R&D series (F15–F16); postal references (F03/F05); supplementary GII observations (F17); fees/ARTG (F18–F19); bounded ABF, NATSEM and demographic additions (F20–F23); later judgments (F26); NSRC/HERDC and suitable public SCOPR aggregates (F42). | Versioned, traceable additions with definitions, licence, coverage and match rates. No substitution of unlike measures or silent alteration of official GII data. |
| E. Deliver the research programme | R1 affordability/economic context; R2 business innovation/barriers; R3 fees/lifecycle costs; R4 BLADE feasibility; R5 participation/denominators; R6 evaluation framework and two retrospective pilots; R7 medicine lifecycle case study. | The workstream-specific outputs and acceptance criteria below. Begin the BLADE enquiry early; its result determines which linked-outcome designs are feasible. |

Feasibility work for R1–R5 and evaluation design for R6 need not wait for unrelated repairs. Outcome testing does depend on the relevant data and definition checks. Preserve irreducible limits: suppressed observations, stale national researcher totals, absent addresses, incomplete international attribution, restricted business outcomes and causal identification.

### Research standard

The goal is not to collect as many indicators as possible or to maximise the number of correlations. The goal is to build credible evidence for decisions about **where to intervene, for whom, through what mechanism, at what cost, and with what additional public benefit**.

Use three complementary evidence levels:

1. **Descriptive:** where IP use, innovation, barriers and costs occur, and how they change.
2. **Observational:** which factors are associated with outcomes, including how relationships vary by business, industry, region and population group.
3. **Causal evaluation:** whether a policy or intervention improved outcomes relative to a credible counterfactual.

Do not present descriptive or observational findings as causal effects. Prefer defined hypotheses and decision questions over indiscriminate correlation searches.

## 2. Ingestion, revisions and data integrity

These findings concern whether the stored values, units, observation identities and source vintages are suitable for analysis. F14’s demonstrated source blanks and F36’s demonstrated parser loss are distinct findings; one does not cancel the other.

### F01 — OECD IP tax regimes: confirmed ingestion failure — repair first

**Location:** `analysis/output/columns.csv`; `src/corpus/sources/_abs.py::tidy_file`; `src/corpus/sources/oecd.py`.

**Evidence:** `data/raw/oecd/ip_tax_regimes.csv.gz` contains 2,639 rows, all with non-empty `OBS_VALUE`. The corresponding Parquet has 2,639 rows and zero non-null `value` entries. Source values include `0.00%`, `4.44%`, regime names, qualifying asset descriptions and explanatory text. Exactly 839 observations are simple numeric percentages; others include ranges, multiple rates or text. `tidy_file` applies `try_cast(OBS_VALUE AS DOUBLE)` to every observation. This is a directly demonstrated data-loss mechanism.

The OECD describes this dataset as containing regime names, qualifying assets, rates and review status, consistent with the raw file's mixed types. [OECD explanation](https://www.oecd.org/en/publications/corporate-tax-statistics-2026_73af6222-en/full-report/beps-actions_cfce0342.html).

**Fix:** preserve `value_raw` as text for every SDMX flow; give `ip_tax_regimes` a mixed-type parser with `value_text`, optional `value_numeric`, and `value_unit`. Convert simple percentages only when the measure calls for them; retain compound rates verbatim. Rebuild this table from its existing raw file. Check that all 2,639 non-empty inputs remain represented and that no non-empty value disappears without an explicit parse flag.

### F13 — Most all-null columns are optional metadata, not lost observations

**Location:** `analysis/output/columns.csv`; `_abs.py::tidy_file`.

Of the **88 all-null column entries**, **60** are optional labels, observation comments, status or multiplier metadata in ABS/OECD tables: 13 ABS BCS, 8 ABS regions and 39 OECD. `tidy_file` creates `_label` columns even for dimensions without label strings. These should not be counted as missing substantive measurements.

The other 28 comprise the OECD value failure, ATO ACN, 22 IPLORD column entries and four IP RAPID entries covered elsewhere in this report.

**Fix:** define required/optional/applicable columns by table. Report missingness separately for observations, identifiers, optional metadata and deliberately withheld personal names. A table whose row count matches its own manifest can still have lost every value during parsing, as F01 demonstrates.

### F14 — ABS BCS and SEIFA missing observations: substantial evidence of source suppression/availability limits

**Location:** `analysis/output/columns.csv`; first EDA notebook.

For `ABS_IT_FINANCE`, the raw CSV already has **2,589 blank observations out of 5,576**. Of those, **1,869** explicitly carry the publisher's 'not available for publication' status; 720 have no status explaining the blank. Its processed 46.43% missing rate therefore agrees with the raw values. This sample does not support a parsing-loss claim.

The repository's SEIFA POA table has 2,643 IRSAD-score rows, of which 2,624 contain a score. The lens's denominator differs after geography filtering, explaining why its percentage need not equal the whole source table's. ABS documents exclusions for reliability and confidentiality and cautions about small-area correspondence. [SEIFA construction](https://www.abs.gov.au/statistics/detailed-methodology-information/concepts-sources-methods/socio-economic-indexes-areas-seifa-technical-paper/2021/construction-indexes).

**Fix:** preserve observation statuses. Prefer a published coarser geography/category where appropriate; do not turn suppressed observations into zero. Check other tables individually rather than extrapolating this sample. `_abs_cube.py` currently emits numeric cells only, so a richer importer should also retain source tokens such as suppressed/not-applicable values and cell coordinates.

### F36 — ABS workbook parsing drops annotated zeroes and loses units — confirmed

**Location:** `src/corpus/sources/_abs_cube.py`; `abs_rd_vc/cubes`.

The generic numeric parser accepts only float-convertible strings. The raw HERD workbooks contain **seven `0 (b)` cells**: one in `HERDDC02.xlsx`, six in `HERDDC03.xlsx`. These are omitted entirely by `_num`, rather than retained as zero with a footnote. This is additional to the suppression-token loss discussed in F14.

In `HERDDC01.xlsx`, Table 1 has row-specific units in its second column and values in its third. The **34 retained values** all receive the generic header `col2`; their units are discarded. Raw units are **30 monetary values in $'000 and four PYE values** (person-years of effort). The processed schema has no separate unit field. Values survived, but are not safely comparable without reopening the workbook.

**Fix:** use an explicit layout for these tables; retain unit, raw cell, annotation and observation status. Parse numeric-plus-footnote cells with the footnote stored separately. Retain suppression and not-applicable observations without inventing values. Initialise section hierarchy from pre-data rows, preserve row/column coordinates, and validate representative output cells against the workbook. The [ABS release and methodology](https://www.abs.gov.au/methodologies/research-and-experimental-development-higher-education-organisations-australia-methodology/2024) provide context; workbook cells are the direct evidence here.

### F29 — CER: years are ingested as postcodes, and historic totals have broken labels — confirmed

**Location:** `src/corpus/sources/cer.py::run`, `_period`; `cer/installations`.

The loader assumes the first column of every CSV is a postcode. But `historical-voluntary-state-data-battery-installation-small-scale-systems.csv` starts with **Installation year**, followed by ACT, NSW, NT, QLD, SA, TAS, VIC, WA and Total. Consequently all **108 observations** are mislabelled: `postcode` contains **2014–2025**, while `period` contains state abbreviations or `Total`. A four-digit format check would incorrectly accept these years as postcodes.

Separately, `_period` splits every remaining header at its last ` - `. For the solar installation header `Historic Total Installation Quantity (2001 - 2010)`, it produces a truncated period and a measure of `2010)`. There are **23,548 observations across 16 dataset labels** with that malformed measure in the processed table.

**Fix:** dispatch on validated source schemas. Give the state battery file `geography_type=state`, `state`, `year`, `measure=installations`, `value`; parse its Total separately. Parse monthly columns with a strict month/year pattern and historic totals with a separate explicit rule. Add `period_type` and start/end dates so totals cannot enter a monthly series. Reject unexpected first-column names instead of treating any four digits as geography.

The [CER publisher page](https://cer.gov.au/markets/reports-and-data/small-scale-installation-postcode-data) separately identifies postcode datasets and historical voluntary state battery data. This is a loader problem, not missing postcode information in the state file.

### F30 — CER: equivalent CSV and Excel tables are both loaded — confirmed duplication risk

**Location:** `cer.py::run`; `cer/installations`.

The loader follows both CSV and workbook links and appends their contents. The second-pass audit compared the modern solar-installation CSV with the `SGU-Solar` worksheet in the installation workbook: after postcode padding, **all 536,901 observations match exactly on postcode, period, measure and value**. Both sets remain in the processed table under different `dataset` strings. This is confirmed duplicated representation, although a consumer that explicitly selects one dataset avoids double counting.

**Fix:** retain both raw formats for provenance if useful, but choose one canonical processed representation per technology/measure/geography/period. Assert uniqueness at that key. Store `technology`, `unit`, `geography_type` and `period_type` explicitly rather than requiring analysts to infer them from filenames. Do not combine monthly records with the historic and grand-total columns.

**Genuine coverage limit:** CER says this is certificate-creation data; pending/failed registrations are excluded and recent figures rise during the 12-month certificate-creation window. Keep a completeness flag or lag window. Solar capacity is kW, whereas battery capacity is usable kWh; these must remain distinct units. [Publisher definitions](https://cer.gov.au/markets/reports-and-data/small-scale-installation-postcode-data).

### F32 — R&D Tax Incentive: amendments and report revisions are ignored by the firm lens — confirmed

**Location:** `src/corpus/sources/_ato.py::read_reports`, `rdti.py`; `analysis/eda/build.py::firms_sql`.

The processed RDTI data preserves amendments, but the firm lens computes `max(rd_expenditure)` per ABN/year and never uses `rd_expenditure_amended`. There are **944 rows with amended expenditure**, involving **813 distinct non-null ABNs**; all 944 differ from the original amount. Across these source rows, amended amounts total $2,131,898,609 versus $2,290,664,772 originally. That **$158,766,163 difference is a diagnostic over source rows, not a deduplicated national revision estimate**.

There are also **188 ABN/year groups with multiple rows**, accounting for **190 extra rows**. `_ato.py` drops exact repeats, but does not select the latest report, despite `rdti.py` describing that rule. Taking the maximum is not a substitute for applying a later, potentially downward revision. [ATO guidance](https://www.ato.gov.au/businesses-and-organisations/income-deductions-and-concessions/incentives-and-concessions/research-and-development-tax-incentive/r-d-tax-transparency-reports) confirms that original and amended claims are both published.

**Fix:** preserve the report history; rank reports by actual release/revision date; resolve one authoritative row per ABN and income year; derive `effective_rd_expenditure = coalesce(rd_expenditure_amended, rd_expenditure)`. Retain a genuine amended zero. Compute latest-year and mean measures from this resolved table. For unresolved same-release conflicts, flag the record rather than silently choosing the maximum. Do not label claimed RDTI expenditure as an ABS R&D measure without reconciling definitions.

### F33 — AusTender: releases are flattened into contract IDs, then summed — confirmed structural problem

**Location:** `src/corpus/sources/austender.py::_flatten`, `_window`, `run`; `linkage.py`.

The processed table has **1,548,989 rows**, but **96,277 contract IDs repeat**, with **171,076 rows above one per ID**. The API portion contains 629,050 rows for 457,978 IDs; **525 API rows are exact duplicates across all retained columns**. Most repeated IDs have different values, so indiscriminately dropping duplicates by ID would also destroy legitimate amendment history.

The mechanism is visible: `_flatten` saves `contracts[0].id` as `cn_id`, but omits the release `id`, `ocid`, release tags and amendment links. `linkage.py` then counts every row and sums every `value` by supplier. A live API check for 1–2 October 2026 returned **93 releases, 92 contract IDs**, including a `contractAmendment` release. This confirms that a release and a contract are different units. It does not quantify the correct national monetary adjustment.

The [Department of Finance](https://www.finance.gov.au/government/procurement/statistics-australian-government-procurement-contracts-) states that AusTender values describe maximum contract value over the contract's life, not annual spending. The [Open Contracting Partnership's Australian registry](https://data.open-contracting.org/en/publication/19) also documents amendment/supplier issues; its detailed quality review is dated September 2019, so those caveats are not proof that every issue persists today.

**Fix:** keep a release table keyed by `release_id`, retain `ocid`, tags, amendment IDs, status and full contract/party/item relationships; deduplicate downloads by release ID. Build a separate current-contract table using the amendment chain and valid cancellations. Aggregate either resolved contract commitments or correctly interpreted amendment deltas, never a mixture. Review negative revisions. Replace first-supplier/first-item selection with linked child tables where arrays have multiple entries.

**Additional ingestion risk:** `_window` caches files by start date only. An unfinished current week is later reused even when its end date extends. Re-fetch incomplete windows, use start/end in the cache key, and reconcile boundary releases. An open alternative for reconciliation is the [OCP bulk dataset](https://data.open-contracting.org/en/publication/19), available in JSON/CSV under CC BY 3.0 AU; it shares upstream limitations and is not independent evidence of ground truth.

### F39 — Re-running a source does not consistently refresh it — confirmed code-level risk

**Location:** `core.py::download`, `r2_get`, `Ctx.save`; `oecd.py::run`; `openalex_works.py`; `austender.py::_window`.

`download` skips any non-empty existing file unless `force=True`. OECD tests only file existence, despite a comment saying a file fetched “today” is reused. `r2_get` trusts an existing local path without comparing the current manifest hash. Completed OpenAlex years are never refreshed, although citations and affiliations change. `Ctx.save` nevertheless records today's run date. AusTender's incomplete-week problem is described in F33.

This demonstrates routes to stale or incomplete re-runs, not that every table is currently stale. IP RAPID explicitly uses `force=True` for its weekly ZIP and is an exception.

**Fix:** separate `retrieved_at`, publisher release date, source coverage end and `processed_at`. Use versioned filenames or conditional requests, verify cached bytes against the manifest, re-fetch mutable recent windows and periodically refresh older mutable data. Record publisher resource IDs/URLs as well as local names. Add a run-level coverage report and fail when required flows disappear; OECD currently raises only if every flow fails.

## 3. Applicants, firms, identifiers and geography

Preserve original identifiers, party roles and location precision. Missing business links, unknown country, an unmatched postal reference and a missing application are different conditions.

### F03 — Overseas postcodes: present in the corpus, deliberately removed from the Australian lens

**Location:** `docs/eda-plan.md`; ADR 0005; `analysis/eda/build.py::rights_sql`; postcode join tests in `analysis/profile_corpus.py`.

The rights lens keeps a postcode only where the first applicant's country is `au`. The profile then tests postal strings against Australian ABS Postal Areas. That measures Australian statistical-geography coverage, not worldwide postcode validity.

Direct counts from `iprapid/patent_rights`:

| Category | Records |
|---|---:|
| All patents | 1,752,428 |
| First applicant recorded as Australian | 354,055 |
| Those Australian records with a postcode | 352,020 |
| Known foreign first-applicant country | 880,799 |
| Known foreign country and non-null postcode | 410,112 |
| First-applicant country missing | 517,574 |

**Fix:** retain `applicant_postcode_raw` and `applicant_country_raw`, alongside the existing Australian analysis field. Add a separate international postal lookup keyed by **country + normalised postcode**, with source, vintage and match precision. A country-aware reference can locate many existing foreign codes. It cannot fill a genuinely blank postcode without additional address evidence.

### F04 — Unknown country is treated as non-Australian: confirmed transformation problem

**Location:** `src/corpus/sources/iprapid.py::_rights`; `analysis/eda/build.py::TIMELINE_APPLICATIONS`.

`coalesce(a.any_applicant_in_australia, false)` converts a missing answer into `false`. Of the **517,574 patent records with missing first-applicant country, 517,375 have this flag set to false**. The timeline uses `NOT australian_applicant` for overseas standard patents and some other rights. Only 76,441 of the 517,574 records have zero selected applicants, so this is not merely a handful of rows without parties.

This demonstrates a classification problem; it does **not** establish how many unknown cases are actually Australian. The explanation that roughly 80% have no Australian postcode *because they are overseas* is unsupported. About 29.5% of all patent records lack the first-applicant country.

**Fix:** use `domestic`, `foreign`, `mixed` and `unknown` categories derived from all relevant parties, preserving incomplete country information. Distinguish founding applicants from current owners. Profile the full party table by right, role, current/founding flag and filing decade to determine which countries can be recovered before seeking a new dataset. Do not infer nationality from a postal string alone.

### F05 — Australian postcodes not matching ABS POAs: partly a reference mismatch

**Location:** `analysis/README.md`; `docs/catalogue.md`; `src/corpus/sources/abs_regions.py`.

Among 352,020 Australian first-applicant patent records with a postcode, 337,454 match the repository's POAs after four-digit normalisation. **14,566 do not**. Yet a trial against GeoNames finds 350,522 matches among the same 352,020 records. These are different reference universes, not proof that GeoNames supplies correct business locations for every additional match.

ABS explicitly says POAs approximate postcodes and exclude PO boxes, large-volume receivers and other non-street-delivery codes. Some valid delivery codes also have no corresponding POA. The repository's description of roughly 2,600 'real' postcodes should therefore be changed to roughly 2,600 *ABS Postal Areas*. [ABS POA definition](https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs/edition-3-july-2021-june-2026/non-abs-structures/postal-areas).

**Fix:** classify failures as missing, malformed, foreign, non-residential postal code, unmatched historical code, or unrecognised. Use G-NAF where a physical address is actually available; otherwise retain postal-location precision. Never attach a firm's SEIFA or remoteness to a PO-box centroid as if it were its operating location. Keep 2021 geography for comparability with the 2021 Census and SEIFA; use explicit correspondences for other vintages.

### F06 — Old Australian patent-number joins: the profile ignores a conversion already implemented

**Location:** `analysis/README.md`; `analysis/profile_corpus.py::KEYS`; `src/corpus/sources/google_patents.py::_au_application`.

The profile says pre-2000 matching requires a map the corpus does not hold. Its join test extracts the digits with `regexp_extract(application_number, '^AU-(\\d+)-', 1)`. But current ingestion already creates **`au_application`**, including conversion of numeric legacy identifiers; the committed manifest lists this column. The code example converts `AU-6508386-A` to `1986065083`.

**Verdict:** confirmed mismatch between the diagnostic and current ingestion. The true improved match rate remains unverified because the members table is R2-only. The function's two-digit-year pivot and handling of short/letter identifiers still need validation; its docstring's broad mapping claim is not proof of complete coverage.

**Fix:** profile and join on `au_application`; compare old/new matches by filing decade and application kind, and inspect collisions. Retain the original identifier. Use IP Australia's [ST.37 Authority File](https://data.gov.au/data/dataset/authority-file-for-ip-australia-patents-collection) to check publication coverage and identifiers; inspect its actual schema before assuming it is a complete legacy-number crosswalk. Use the public patent search for unresolved examples. Do not re-query all of BigQuery just to update this join test.

### F07 — Google Patents blank fields: mixed semantics, plus a genuinely incomplete selection frame

**Location:** `analysis/README.md`; `src/corpus/sources/google_patents.py::FAM`, `MEMBERS`.

The committed profile reports empty strings in `entity_status` (97.6%), `au_assignee_names` (87.5%) and `inventor_countries` (83.7%). Their interpretations differ:

- `au_assignee_names` deliberately includes only assignees with harmonised country `AU`; its blank rate is not a measure of missing assignee names worldwide.
- `entity_status` is not a universal legal-status field. Do not interpret blank as 'inactive' or automatically as a failed import.
- Missing harmonised inventor/assignee countries can cause Australian-connected foreign-only families to be omitted by the `FAM` query. Enriching only the already-selected families will not recover families excluded at selection time.
- `members` downloads Australian publications plus members of families with identified Australian people/assignees. It is not all worldwide members of every Australian-publication family. Family summaries and members consequently have different coverage.

**Fix:** retain raw and harmonised names/countries separately, normalise empty arrays/strings explicitly, and label why a field is empty. Add candidates using independently identified Australian inventors/assignees, then rebuild the family selection. [USPTO PatentsView](https://www.uspto.gov/ip-policy/economic-research/patentsview) provides inventor/assignee/location links for US documents; it cannot solve all jurisdictions. For institutional applicants, ROR can help resolve organisations, with historical-location and name-match checks. A non-PCT application legitimately has no PCT number.

### F08 — IPLORD patent columns: probable source-release issue, not independently resolved

**Location:** `docs/catalogue.md`; `src/corpus/sources/iplord.py`; `docs/data-plan.md` section 8.

The committed IPLORD schema contains designs, PBR and trade mark fields but no patent columns. Importantly, `iplord.py` dynamically selects **every column in the source header**; it does not use a whitelist that drops patent columns. That supports the repository's source-release explanation. However, The audit could not independently inspect the large original ZIP, and the public dictionary/catalogue advertises broader IP coverage. Metadata is not proof that the actual CSV contains those fields.

**Fix:** inspect the ZIP member list and first CSV header against the downloaded release; check split files as well as `iplord_1901_2020_full_data_set.csv`. If patents are absent, retain that limitation and use `iprapid/applicant_year`, which already exists. Update the stale `docs/data-plan.md` reference to `ipgod/applicant_year` ending in 2022. Do not call the newer table identical to IPLORD without checking its stock/flow definitions, financial-year basis and founding-party attribution.

Source: [publisher catalogue metadata](https://researchdata.edu.au/intellectual-property-longitudinal-data-iplord/3802327).

### F09 — IPLORD modal-class blanks and PBR blanks in the ABN subset

**Location:** `analysis/output/columns.csv`; `iplord.py`; `iprapid.py`.

The 22 all-null IPLORD column entries include repeated trade mark modal-class columns in both the full and ABN-only tables, and PBR fields empty in the ABN-only subset. These are not 22 distinct missing datasets. The loader preserves modal-class text, so there is no demonstrated numeric-cast explanation for these blanks.

**Fix:** compare those exact raw CSV columns before declaring a source error. Trade mark class summaries can be reconstructed from IP RAPID classifications using an explicitly chosen definition and tie-breaking rule. Preserve the published IPLORD fields and label reconstructed measures separately. PBR emptiness in an ABN-filtered subset must be investigated together with missing PBR ABN linkage, rather than interpreted as no PBR activity.

### F10 — PBR ABNs: missing links, not missing applications

**Location:** `analysis/README.md`; `analysis/output/PROFILE.md`.

The committed PBR table has **11,732 applications, zero ABNs, 5,357 records with Australian first-applicant country, and 9,007 non-null applicant names**. This establishes the missing link but does not prove whether raw parties have no ABNs or whether the current-party selection loses them.

**Fix:** check raw PBR parties across current, former and founding roles first. Where no authoritative ABN is recorded, build a separate candidate-link table using organisation name, state and other corroborating evidence against ABR/ASIC. Review ambiguous matches and record confidence and provenance. Foreign and individual applicants may legitimately have no ABN. Do not interpret an unlinked record as a non-business or fabricate a universal match rate. PBR `main_area` being null is also not evidence the application is absent: inspect its genus/species classification rather than demanding a patent-style technology area.

### F11 — ASIC zero ABNs and ATO empty ACNs: clean placeholders and reuse existing links

**Location:** `analysis/README.md`; `analysis/output/PROFILE.md`; `src/corpus/sources/asic.py`, `_ato.py`.

The profile reports ASIC ABN `'0'` in 40.6% of company rows and an entirely null ATO corporate-transparency ACN column. These do not establish a missing ABR dataset. An absent ACN in a tax report can often be enriched from the ABR using the report's ABN. Conversely, an ASIC company may genuinely lack a corresponding ABN, or it may require ACN-based matching.

**Fix:** convert empty/zero/invalid ABNs to null, validate length and checksum, then perform an exact ACN↔ABN lookup against the existing ABR extract. Separate 'no ABN recorded in ASIC' from 'no match anywhere'. Preserve many-to-one or historical anomalies for review; do not assume the relationship is always unique. The full ASIC/ABR join could not be rerun during the audit. [ASIC open-data information](https://www.asic.gov.au/online-services/search-asic-registers/datagovau).

### F28 — TM-Link joins and omitted text: distinguish linkage coverage from deliberate scope

**Location:** `analysis/output/PROFILE.md`; `src/corpus/sources/tmlink.py`.

The committed profile gives 100% joins from the Australian application and owner tables to IP RAPID, but only 93.9% for the Australian `tm_link` identifiers. That selective discrepancy warrants an anti-join investigation; it could not be explained conclusively in the audit because the tables are R2-only. TM-Link is also a historical multi-office release, not a current worldwide register. The code deliberately excludes `description` and `image-text`; their absence is not failed ingestion. [TM-Link catalogue](https://researchdata.edu.au/tm-link/3805843).

**Fix:** anti-join `tm_link` to its own application table first, then to IP RAPID; inspect office codes, whitespace, prefixes and identifier definitions before changing keys. Separate genuine unmatched IDs from release-window differences and probabilistic international links. If text becomes useful, add the two omitted source resources explicitly. Similarly, personal names blanked in IP RAPID summaries, ABR and NHMRC are documented privacy/scope choices, not evidence that the upstream source lacks names.

### F34 — The firm spine omits some ABNs used by the rights lens — confirmed

**Location:** `linkage.py`; `iprapid.py::_rights`, `_applicant_year`; `analysis/eda/build.py::firms_sql`.

The spine constructs its IP population from `applicant_year`, which uses founding applicants. The rights lens instead carries a selected ABN from current applicants/owners. An anti-join shows **1,179 patent rights representing 812 distinct ABNs**, and **329 design rights representing 119 distinct ABNs**, whose selected ABN is absent from the spine. These ABN counts overlap across right types and must not be added as a unique-business total. Trade marks could not be checked afresh because their summary is R2-only.

`firms_sql` starts from the spine, so these selected owners cannot enter the firm table, even though their rights are present. Separately, `any_applicant_abn` selects only one ABN per right; it is not a complete co-applicant linkage. Current-owner locations attached to historical filing years also do not establish where the original filing occurred.

**Fix:** build an application-party bridge retaining role, founding/current flags and effective dates. Construct the firm universe from the union of relevant ABNs, then calculate separate founding-filer and current-owner measures. Choose and document full or fractional co-applicant counting. Assert that every ABN selected for the firm analysis appears in the spine, and measure ownership/location changes instead of silently applying today's owner to the filing year.

### F35 — Business age is a registration/status proxy, not a verified founding date

**Location:** `linkage.py::first_seen`; `analysis/eda/build.py::age_years`; `variables.yaml`.

`first_seen` is the earliest available current active ABN-status date, GST-status date and ASIC registration date. The firm lens calls the derived interval `Age`. In the spine, **26,998 ABNs have no first_seen**, **47 have a date before 1900**, and **16,208 have first_seen after 30 June of their first patent-filing financial year**. The last comparison is a warning about chronology/attribution, not proof that every registration date is wrong: assignments and changes of legal entity can also produce it. Pre-1900 dates can be genuine and must not all be deleted.

The [ABN bulk extract description](https://abr.business.gov.au/Tools/BulkExtract) distinguishes ABN status dates and GST registration dates. They do not collectively establish a universal business birth date. The module's phrase “lower bound on the business's start” is also misleading: a later first-observed date ordinarily gives a lower bound on elapsed age, not an earlier bound on the true start date.

**Fix:** rename this `years_since_first_observed_registration`, retain component dates and provenance, and create an explicit age-quality flag. Use incorporation dates for incorporated-entity age where appropriate, but do not equate incorporation with operational founding for every entity. Do not infer survival or historical activity merely from today's ABN status.

### F40 — Some collected data lacks the linkage or lens columns needed for the stated analysis

**PHIDU:** `phidu.py` explicitly skips the `PHAs` worksheet, even though it contains the geographic correspondence described in its own docstring. The processed indicators retain PHA codes, but there is no processed PHA-to-SA2 concordance. The official [2021 SA2-to-PHA concordance](https://phidu.torrens.edu.au/help-and-information/help-guides-and-faq/geographical-structures/pha-list-2021) is publicly downloadable. Ingest that or the workbook correspondence, preserving the geography vintage. Then aggregate IP counts from SA2 to PHA, or use explicitly weighted POA-to-SA2-to-PHA correspondences. Do not treat a PHA code as an SA2 code or redistribute rates by simple addition. PHIDU's non-commercial/share-alike terms remain applicable.

**PBR:** the rights and timeline lenses include PBR, but `firms_sql` and `regions_sql` omit PBR measures; the firm lens also drops the spine's `in_iprapid_pbr` flag. There are **1,014 PBR rights with an Australian first applicant and a non-null postcode within FY2017–FY2026**, before checking POA matchability. Missing PBR ABNs do not prevent geographic analysis of all these records. Add PBR counts/flags and explicit linkage coverage, or document its exclusion from each lens. Missing ABNs must remain unknown business links, not zero activity.

These are additions to the analysis layer; they are not evidence that PHIDU indicators or PBR applications themselves failed to download.

### Postal and organisation reference sources

These are specific sources with clear joins, rather than a generic list of datasets. 'Open' does not mean complete or appropriate for every use.

| Source | Useful fields and join | Access/licence | Limitations and ingestion instruction |
|---|---|---|---|
| [GeoNames postal downloads](https://download.geonames.org/export/zip/) | Country, postcode, place, administrative areas, coordinates, accuracy | Bulk ZIP/TSV; current download README says CC BY 4.0 | Best first international reference. Read the current country coverage notes. Store country + postcode as text and preserve one-to-many place matches. Coordinates can be estimated. |
| [ONS Postcode Directory / NSPL](https://www.ons.gov.uk/methodology/geography/geographicalproducts/postcodeproducts) | Full UK postcode, geography codes; current/terminated postcode coverage depends on product | Downloadable; [ONS licensing](https://www.ons.gov.uk/methodology/geography/licences) specifies OGL and separate Northern Ireland conditions | Prefer official full codes for GB. Keep introduction/termination information where provided; do not apply a current location blindly to historical records. |
| [US Census Gazetteer](https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.html) and [ZCTAs](https://www.census.gov/programs-surveys/geography/guidance/geo-areas/zctas.html) | ZIP-like statistical areas, centroids/boundaries and Census joins | Free official downloads | ZCTAs do not represent all valid USPS ZIP codes, including many special/PO-box codes. Use ZIP5 for area matching while preserving ZIP+4 raw values. |
| [Japan Post UTF-8 postal files](https://www.post.japanpost.jp/service/search/zipcode/download/utf-zip.html) | Seven-digit postcode to prefecture, municipality and locality | CSV/ZIP; [publisher permits free distribution and does not claim copyright over the postcode data](https://www.post.japanpost.jp/service/search/zipcode/download/utf-readme.html) | Preserve leading zeros; remove hyphen only in normalised key. Address lookup is not necessarily a coordinate source. Special business codes may need separate files. |
| [La Poste official postal-code base](https://www.data.gouv.fr/datasets/base-officielle-des-codes-postaux) | French postcode ↔ INSEE commune | Download/API; Licence Ouverte 2.0 | One postal code can cover multiple communes; boundaries are not included in this dataset. |
| [G-NAF](https://www.industry.gov.au/publications/geocoded-national-address-file-g-naf-and-administrative-boundaries-ab-data) | Australian physical addresses and coordinates | Open government download under G-NAF-specific end-user licence | Useful only when there is enough physical-address information. Does not turn a PO box into an operating address. Retain the applicable EULA and vintage. |
| [USPTO PatentsView](https://www.uspto.gov/ip-policy/economic-research/patentsview) | US patent/publication identifiers, inventors, assignees and locations | Official downloadable research datasets; now hosted on USPTO ODP | Use to add Australian-connected US records that Google's country filter missed. It is US-specific, and any inferred location needs a source/date. Check current ODP access requirements before building a scheduled loader. |
| [ROR data dump](https://ror.readme.io/docs/data-dump) | Organisation identifiers, names and institutional locations | Bulk JSON; core metadata CC0; location data carries GeoNames attribution | Helps research-institution matching, not comprehensive business addresses or historical inventor residence. Avoid a name-only automatic match for ambiguous organisations. |
| [IP Australia Authority File](https://data.gov.au/data/dataset/authority-file-for-ip-australia-patents-collection) | Patent publication identifiers, publication availability | Public monthly TXT/CSV release; check release licence | Useful to audit publication coverage. Verify fields before claiming it provides every old-to-new application-number mapping. |

GeoNames' [current README](https://download.geonames.org/export/zip/readme.txt) describes separate full-code files for Canada, the Netherlands and the UK; the ordinary all-country/country files contain only their first code part. It also describes partial coverage for China, Ireland, Malta, Chile, Argentina and Brazil. These restrictions must be represented in a coverage table rather than interpreting every unmatched code as invalid.

### Postal matching trial reported in the audit

The audit downloaded the then-current GeoNames AU/US/JP/DE/GB/CN country ZIPs and matched against the committed patent table. Normalisation trimmed/capitalised text, preserved digits as text, reduced US ZIP+4 to ZIP5, removed the Japanese hyphen and padded Australian three-digit codes. No fuzzy matching or name-based guessing was used. UK outward-code matching was measured separately because `GB.zip` is a district-level file.

| Country | Patent records with country and postcode | Reference matches | Match rate | Precision |
|---|---:|---:|---:|---|
| Australia | 352,020 | 350,522 | 99.6% | Postal lookup; not necessarily a residential POA |
| United States | 266,566 | 264,723 | 99.3% | ZIP5 |
| Japan | 32,878 | 29,601 | 90.0% | Normalised postal code |
| Germany | 4,196 | 3,363 | 80.1% | Postal code |
| United Kingdom | 25,595 | 24,868 | 97.2% | Outward district only; full-code equality matches just 17 records against this truncated reference |
| China | 21,910 | 3,910 | 17.8% | Codes present in the limited reference |

The counts establish a practical lookup opportunity, not verified coordinate accuracy or unique physical addresses. They are counts of patent records, not distinct applicants or distinct postcodes. UK and China illustrate why a low exact match rate can reflect a limited reference file. A historical postcode can also be valid at filing time but absent from today's file.

## 4. Innovation indicators and economic context

### F02 — World Bank trade marks: obsolete requested codes, not the disappearance of trade mark statistics

**Location:** `docs/data-plan.md` section 8; `data/manifest.json` WDI notes; `src/corpus/sources/wdi.py::INDICATORS`.

The code requests `IP.TMK.RESD`, `IP.TMK.NRES` and `IP.TMK.TOTL`. The audit confirmed that the resident-code API returns an archived/deleted-indicator error. However, the current official indicators are [resident, by count: `IP.TMK.RSCT`](https://data.worldbank.org/indicator/IP.TMK.RSCT) and [nonresident, by count: `IP.TMK.NRCT`](https://data.worldbank.org/indicator/IP.TMK.NRCT). Both live Australian API requests returned 21 observations, covering 2004–2024. For 2024 they return **84,859 resident** and **67,644 nonresident** counts.

**Fix:** add these current indicators to `wdi.py`, retain their definitions and units, and rerun WDI and the national lens. Do not silently rename them to the old series: establish comparability first. If a total is required, derive resident + nonresident only for matching country, year and counting definitions. The existing WIPO tables offer another route, but the national lens's origin-based worldwide filings are not interchangeable with domestic-office resident/nonresident totals.

Reproduction endpoints:

```text
https://api.worldbank.org/v2/country/AUS/indicator/IP.TMK.RSCT?format=json&per_page=100
https://api.worldbank.org/v2/country/AUS/indicator/IP.TMK.NRCT?format=json&per_page=100
```

### F15 — Australia's R&D expenditure: some data are already present but unused

**Location:** `docs/handover-eda.md`; first EDA notebook; `analysis/eda/build.py::national_sql`.

The national lens includes WDI and WIPO, **not OECD MSTI**. In the committed WDI panel, Australian R&D/GDP ends in 2021; OECD MSTI already supplies 2023. The observed series also differ where they overlap: WDI 2021 is **1.85783%**, while OECD is **1.658221012%**. OECD 2023 is **1.682148487%**. Treating OECD as simple blank-filling would hide a material source/vintage difference.

**Fix:** expose a separately labelled OECD GERD/GDP series using `reference_area='AUS'`, `measure='G'`, `unit_of_measure='PT_B1GQ'`, with all remaining dimension checks and observation flags. Reconcile vintages before selecting a preferred series. Do not interpolate biennial survey years and call them observations: ABS explicitly runs relevant R&D collections biennially. [MSTI](https://www.oecd.org/en/data/datasets/main-science-and-technology-indicators.html); [ABS collection methodology](https://www.abs.gov.au/methodologies/research-and-experimental-development-government-and-private-non-profit-organisations-australia-methodology/2024-25).

### F16 — Researchers and technicians: the missing totals are not fixed by adding sector figures indiscriminately

**Location:** first EDA notebook; WDI and MSTI tables.

Live WDI requests reproduce the repository's cut-offs: researchers per million end in **2010**, technicians per million in **2008**. The committed OECD total-researcher series ends in **2008**. OECD does have newer sectoral researchers: business to 2023 and government/higher education to 2022. Total GERD financed by business also ends in 2008 in the committed MSTI data.

**Fix:** retain the missing national totals as such. Add newer sector measures for questions they can answer, labelled by sector and year. A national reconstruction needs compatible sector coverage, dates, definitions, units and any private non-profit component; it cannot simply sum the latest row from each sector. ABS sector R&D publications are the appropriate public starting point. Do not substitute all R&D personnel for researchers.

### F17 — Six missing Australian GII indicators: present as blanks in the supplied source

**Location:** raw `gii-2026-data.xlsx`; `gii/data`; `src/corpus/sources/gii.py`.

The audit compared the raw workbook and processed table. The raw file already has **1,224 blank scores** across economies and nodes. The six Australian blanks below are genuine blanks in the supplied GII source, not values destroyed by this loader. Blank `value_screen` on aggregate index nodes can also be structurally appropriate: an index score does not necessarily have a single raw input observation.

| Indicator | What can realistically fill the analytical gap |
|---|---|
| 2.1.5 Secondary pupil–teacher ratio | ABS Schools publishes secondary student/teacher ratios: **11.7 in 2025** and **11.7 in 2024**. Download Table 51a. Reconcile FTE and school-level definitions against UIS/GII before using as a substitute. WDI's Australian secondary-ratio endpoint returned no observations in this check. |
| 2.3.1 Researchers, FTE per million | National total is genuinely stale in the checked international series; see F16. Newer sector figures are useful but are not the missing total. |
| 4.1.3 Microfinance loans/GDP | The WIPO Australia profile also shows n/a. No complete, compatible Australian numerator was verified. Program-level lending reports would be partial coverage, not an automatic replacement. |
| 5.1.5 GERD financed by business, % | Checked OECD total funding series ends in 2008. ABS sector funding tables could support a separately labelled reconstruction after harmonising reference periods and sector coverage. BERD performed by business is a different quantity. |
| 5.3.6 Research talent in businesses, % | Requires business researchers and a compatible national researcher total. A newer numerator does not repair the old/missing denominator. |
| 6.1.3 Utility models by origin/PPP GDP | Check WIPO origin-based counts and the exact GII reference year. Australia's innovation-patent phase-out does not prove Australian residents filed zero utility models overseas. Leave missing unless a compatible numerator is established. |

Sources: [ABS Schools 2025](https://www.abs.gov.au/statistics/people/education/schools/latest-release), [WIPO Australia 2026 profile](https://www.wipo.int/edocs/gii-ranking/2026/au.pdf), [GII definitions](https://www.wipo.int/web-publications/global-innovation-index-2026/en/appendix-iii-sources-and-definitions.html).

**Fix:** preserve the official GII release exactly. Put supplementary observations in a separate table with source, observation year, definition difference and quality status. Do not silently recalculate an 'official' rank after replacing inputs. WIPO's statistical audit explicitly examines the consequences of missing-data treatment.

### F22 — Venture capital after 2018–19: real discontinuation; existing OECD data do not solve Australia's gap

**Location:** `src/corpus/sources/abs_rd_vc.py`; data plan.

The [ABS publication explicitly says it has ceased](https://www.abs.gov.au/statistics/economy/finance/venture-capital-and-later-stage-private-equity-australia), with 2018–19 the latest release. The repository's OECD venture-capital table has Australian observations only through **2019**. Therefore simply switching to the existing OECD table does not establish a newer Australian series.

**Fix:** retain the discontinuity. Public industry reports may supply separately defined aggregates, but no like-for-like open deal-level replacement was verified in the original audit. Do not splice different reports into a continuous ABS series without a definitions bridge. Historical ABS releases remain usable for backfilling earlier years.

### F27 — IPC-to-industry gaps: incomplete crosswalk coverage, not missing patents

**Location:** `analysis/README.md`, `analysis/output/PROFILE.md`, `src/corpus/sources/concordances.py`.

The profile reports 93.9% coverage of distinct IP RAPID IPC subclasses by the ALP industry crosswalk, but 99.7% coverage of classification rows. Those are different denominators. A direct query of the committed patent summaries finds unmatched main classes including G16H (1,884 patents), B29H (1,090), G06V (828), G16B (708) and F24S (629). This demonstrates reference coverage gaps; it does not establish that these patents lack valid classification.

The importer uses ALP IPC version 2209, explicitly excluding services. The [ALP author's download page](https://sites.google.com/site/nikolaszolas/PatentCrosswalk) still identifies that version. Separately, the technology-field mapping is transcribed from the IPLORD dictionary, whereas [WIPO publishes a regularly updated technology concordance](https://www.wipo.int/en/web/ip-statistics). Technology fields and probabilistic industry mappings are not interchangeable.

**Fix:** list unmatched subclasses and their filing/classification vintages; compare against official IPC validity and revision-concordance files. Rebuild technology fields from the current WIPO table, while preserving versioned historical mappings. For ALP industry weights, use a justified revision bridge or explicitly leave an unmapped category; do not assign industries from similar-looking codes or assume an updated WIPO technology table supplies missing industry probabilities. Check the effect of the services exclusion on the research population.

### R1 — Add a public affordability and economic-conditions layer

**Delivery link:** This retains Priority 1 of the closure plan. The audit repairs in section 2 are prerequisites for analyses that use the affected tables; feasibility and source-design work can proceed alongside them.

**Why:** The current corpus contains regional socioeconomic and wellbeing measures, but does not appear to have a dedicated, recurring household-affordability series. Household and business cost pressures may affect business formation, R&D investment, access to talent and commercialisation. These relationships should be tested rather than assumed.

#### Data sources to investigate

| Source | Measures to extract | Main use | Important caveat |
|---|---|---|---|
| [ABS Selected Living Cost Indexes](https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/selected-living-cost-indexes-australia) | Index levels, percentage changes, household type and available expenditure groups | National quarterly context for different household groups | Limited geographic detail; not interchangeable with CPI. |
| [ABS Consumer Price Index](https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/consumer-price-index-australia) | CPI index and changes by available expenditure class, including housing, food, transport, utilities and health | Separate general inflation from specific expense pressures | CPI is not a direct measure of household financial stress. |
| [ABS Census housing-affordability guidance and data](https://www.abs.gov.au/statistics/detailed-methodology-information/information-papers/guide-housing-affordability-statistics) | Rent and mortgage costs relative to household income; geographic identifiers and reference year | Regional affordability and distributional comparisons | Census snapshots are periodic rather than continuous; geography and definitions must be checked. |
| [Rental Affordability Index](https://www.housingdata.gov.au/visualisations/rental-market/rental-affordability-index) | Published scores, geography, period and methodology metadata, if reproducible export is available | Compare rents with household incomes | Confirm licensing and reproducible data access. Postcode-level rent observations may be combined with broader income estimates. |
| [ABS Wage Price Index](https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/wage-price-index-australia) | Quarterly wage index by available industry/state dimensions | Labour-cost context | Wage growth is not itself a measure of affordability or productivity. |
| [ABS Producer Price Indexes](https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/producer-price-indexes-australia) | Relevant input/output price series | Business input-cost context | Select a small number of relevant series; avoid an unstructured indicator dump. |
| [Reserve Bank of Australia — cash rate](https://www.rba.gov.au/statistics/cash-rate/) | Cash-rate target and date | Broad financing-conditions context | The cash rate is not the borrowing rate faced by every business. |

#### Repository implementation

Proposed modules (adapt names to match existing conventions):

- `src/corpus/sources/abs_slci.py`
- `src/corpus/sources/abs_cpi.py`
- `src/corpus/sources/abs_housing.py`
- Optional: `src/corpus/sources/sgs_rental_affordability.py`
- Optional: `src/corpus/sources/abs_wpi.py`, `src/corpus/sources/abs_ppi.py`, and `src/corpus/sources/rba_cash_rate.py`

Register each source in the repository's source configuration, retain original inputs where permitted, and add processed outputs to the manifest/catalogue and data-quality checks.

Create a contextual table, likely `economic_context`, with fields such as:

- `period`
- `geography_level`
- `geography_code`
- `indicator`
- `dimension` (for example household type or expenditure group)
- `value`
- `unit`
- `source_id`
- `release_date`
- `reference_period`
- `methodology_version`
- `quality_note`

Keep national, state and small-area observations distinct. Do not imply that a national measure explains SA2-level differences. Record whether each statistic is a stock, flow, index, rate or percentage and whether it is seasonally adjusted.

#### Initial analyses

1. Test whether housing affordability and selected cost pressures are associated with business entries/exits, R&D participation and IP use over time or across comparable regions.
2. Examine lags (for example, whether affordability changes precede rather than coincide with changes in outcomes).
3. Control, where data permit, for industry composition, population growth, unemployment, financing conditions, socioeconomic disadvantage and research-institution presence.
4. Report sensitivity to alternative periods and definitions. Treat results as hypotheses unless the design supports stronger inference.

**Decision question:** Are there places or business groups with innovation potential but lower participation in IP activity, where affordability or other economic pressures may be one of several relevant barriers?

**Acceptance criteria:** Reproducible ingestion; sources and reference periods documented; values and units validated; missingness and geographic coverage reported; no unsupported geographic interpolation; at least three pre-specified analyses documented.

### R2 — Refresh ABS business innovation and barriers data

**Delivery link:** Retains Priority 2. Apply the observation-status and annotated-cell repairs in F14 and F36 to any refreshed business-survey tables; a newer release does not by itself resolve suppression or comparability limits.

**Why:** Business survey data provide direct information on innovation activity and reported barriers, including finance, skills and development costs. They can contextualise administrative IP records and help identify barriers that IP Australia may or may not be able to influence.

**Source:** [ABS — Characteristics of Australian Business](https://www.abs.gov.au/statistics/industry/technology-and-innovation/characteristics-australian-business).

#### Actions

1. Inspect the latest release and determine whether existing source-module/API flow identifiers still resolve to the current survey outputs.
2. Ingest the latest relevant tables even if the redesigned release requires a new ingestion path.
3. Retain the source's definitions, survey reference period, release date, units, industry/business-size dimensions and uncertainty/suppression flags where published.
4. Preserve historical data but explicitly flag survey redesigns and breaks in comparability. Do not splice series across methodological changes without a defensible bridge.
5. Update the source catalogue and the EDA plan to identify which tables can be linked only at aggregate level and which, if any, are record-level.

#### Initial analyses

- Innovation barriers by industry and business size.
- Reported finance, skills and innovation-development-cost barriers.
- Reported innovation benefits, where available.
- Differences between industry-level barriers and industry-level use of IP protection.
- Whether sectors with relatively high innovation activity show different patterns of formal IP use or reported barriers.

**Important linkage limit:** Published aggregate survey tables are not automatically linkable to individual ABNs. Use them as industry/size-level context unless an approved microdata/linkage route exists.

**Decision question:** Which barriers appear material in potentially underserved groups, and which fall within IP Australia's remit versus requiring cross-agency action?

**Acceptance criteria:** Latest release ingested or source limitation logged; survey breaks documented; classifications reconciled; no claims of firm-level linkage from aggregate tables; analyses use denominator-consistent rates.

## 5. Participation, business outcomes and public research

Use public aggregates for the questions their units and coverage support. Stronger linked-outcome research requires a separate feasibility and permissions decision; richer descriptive data alone do not establish additional public value caused by IP.

### F23 — First Nations and business-owner demographics: some public denominators can be added now

**Location:** data plan Tier 3 G/H; Q2 distributional coverage.

The [ABS business-owner article](https://www.abs.gov.au/articles/aboriginal-and-torres-strait-islander-people-who-managed-their-own-business-2021) includes downloadable tables by sex, age and state/territory, so not all useful denominator work requires a new TableBuilder session. [NIAA publishes Indigenous Procurement Policy outcomes](https://www.niaa.gov.au/our-work/employment-and-economic-development/indigenous-procurement-policy-ipp).

**Fix:** ingest the public ABS tables and NIAA aggregates as contextual denominators/outcomes. Bespoke combinations of industry, region and other characteristics may still require TableBuilder. These data do not identify which IP applicants are First Nations, disabled or a given age. Do not infer sensitive characteristics from names, postcodes or aggregate population composition. WGND name-based gender estimates also remain estimates, not self-reported identity.

### R5 — Improve participation and underserved-group measures

**Delivery link:** Retains Priority 5. F23 identifies existing public ABS tables that can be ingested before requesting bespoke TableBuilder outputs. Procurement aggregates and population denominators do not identify individual IP applicants’ sensitive characteristics.

**Why:** Aggregate rates can conceal groups that face disproportionate barriers. Existing regional and name-inference measures should be supplemented with appropriate denominators and direct evidence where possible.

#### A. Owner-manager and population denominators

Start with the published ABS owner-manager tables in F23. Investigate Census/TableBuilder for additional combinations of sex, Indigenous status, industry and region, subject to availability and access conditions. Use the appropriate published categories and time periods.

Possible measures include IP applications per relevant business/owner-manager population, subject to definitional alignment. Clearly distinguish persons, businesses, applicants, inventors and owners; these are not interchangeable units.

For name-based gender inference, report match coverage, uncertainty and unclassified records. Do not describe inferred gender as directly observed gender identity.

#### B. First Nations business participation

Source to investigate: [National Indigenous Australians Agency — Indigenous Procurement Policy](https://www.niaa.gov.au/our-work/employment-and-economic-development/indigenous-procurement-policy-ipp).

Actions:

1. Obtain detailed published procurement outcomes and the accompanying definitions/reference periods.
2. Determine whether supplier identifiers are available and whether a permitted ABN linkage can be made.
3. If linkage is not available, use the published aggregates as context and record the limitation.
4. Consider a suitable partnership/research approach for questions that cannot be answered from public data.

Never infer Indigenous identity from a business name, postcode or other indirect proxy. Procurement suppliers are not representative of all First Nations businesses; describe the selection limitation clearly and consult appropriate stakeholders on governance and interpretation.

#### C. Direct evidence of user barriers

For groups not identifiable in administrative data (for example, people with disability or younger entrepreneurs), conduct a proportionate, voluntary, accessible research programme with relevant business associations and support organisations. Recruit non-users as well as current customers.

Ask about awareness, costs, usability, alternative protection, commercialisation and unmet needs. Make sensitive demographic questions optional, collect only what is needed and predefine safe publication thresholds.

**Decision question:** Which groups have unmet needs, how do their barriers differ, and which intervention can plausibly change those barriers?

**Acceptance criteria:** Valid denominators and unit definitions; direct versus inferred measures distinguished; privacy/consent plan for new research; no identity inference from geographic or name proxies.

### F24 — Small-firm turnover, employment, productivity and causal outcomes: genuine public-linkage limitation

**Location:** data plan Tier 3 B–D and research-goal coverage.

ABR/ASIC registers are not comprehensive firm-level financial panels; ATO corporate-transparency reports cover a selected population. [BLADE's description](https://www.industry.gov.au/publications/business-longitudinal-analysis-data-environment-blade) confirms that it supports linked turnover, employment and labour-productivity analysis, but the repository deliberately excludes this access route.

**Fix:** keep the limitation explicit. Use open ABS industry/region aggregates for context and public annual reports for selected entities, without presenting them as a representative linked SME panel. Missing examiner assignment, internal customer research and counterfactual outcomes are not repaired by additional postal data. Copyright/creative-industry aggregates similarly do not provide a register of all copyright users or isolate copyright's causal value.

### R4 — Revisit access to ABS BLADE for linked business outcomes

**Delivery link:** Retains Priority 4. F24 describes the public-data limitation and the repository’s earlier exclusion of BLADE. This workstream proposes revisiting that decision; it does not assert that access or any linkage has been approved. Begin feasibility work early because its outcome shapes the available research designs.

**Why:** Public data provide incomplete measures of smaller firms' turnover, employment and productivity. A linked business-data environment may make it possible to compare IP users with similar non-users over time.

**Source:** [ABS — Business Longitudinal Analysis Data Environment (BLADE)](https://www.abs.gov.au/statistics/microdata-tablebuilder/available-microdata-tablebuilder/business-longitudinal-analysis-data-environment-blade) and [ABS — Accessing integrated data](https://www.abs.gov.au/statistics/data-integration/accessing-integrated-data).

The closure plan reports that ABS BLADE documentation lists IPRAPID among its data products. This is a reason to reopen the earlier decision not to pursue integrated data, not proof that all requested linkages are available. Confirm available identifiers, data items, linkage permissions, costs and approvals with the ABS and relevant data custodians.

#### Concrete actions

Send a scoped research enquiry to the ABS asking:

1. Whether IP RAPID/IPRAPID data can be linked to business outcomes through identifiers available in BLADE.
2. Which business measures are available for suitable periods: turnover, employment, productivity, exports, R&D activity/expenditure, survival and insolvency (subject to the data product and permissions).
3. Which approvals and data-custodian permissions are required.
4. Whether TableBuilder is adequate or the study would require DataLab or a custom linkage.
5. Likely costs, timing requirements, output-clearance rules and permitted publication forms.

If feasible, prepare a research proposal and a privacy-preserving analysis plan. Keep confidential microdata in the authorised secure environment. Do not commit confidential records or derived identifiable data to the public GitHub repository; publish only outputs approved for release.

#### Proposed design

Compare first-time IP filers with similar non-filing firms, using pre-filing characteristics and outcome histories. Examine differences in turnover, employment, productivity, export activity, survival/exit and R&D where available. Stratify by industry, firm age/size and type of IP right when sample size and disclosure requirements permit.

The primary analysis remains observational unless a credible causal design can be justified. Consider selection into filing, business maturity, financing, industry and prior performance.

**Decision question:** Under what conditions is IP use associated with improved business outcomes, and what additional evidence is needed to claim that IP or an IP Australia intervention caused those outcomes?

**Fallback:** If linkage is unavailable or infeasible, document the decision and continue with public proxies; do not imply that public data provide equivalent outcome coverage.

**Acceptance criteria:** Written data-access decision; feasibility/permissions matrix; documented variables and periods; secure-environment plan; pre-analysis plan before outcome testing.

### F37 — OpenAlex research-to-patent coverage excludes scholarly-uncited works before the patent join

**Location:** `src/corpus/sources/openalex_works.py::FILTER`, `run`, `_institutions`.

The filter is `institutions.country_code:au,cited_by_count:>0`. OpenAlex's [citation documentation](https://help.openalex.org/data/works/citations/) defines this count through citations from other indexed works. A work can be cited by a patent without having such a scholarly citation. Therefore this filter cannot substantiate the catalogue's claim of **every** USPTO citation to Australian research. The selection mechanism is confirmed; the number of omitted patent-cited works was not measurable without the complete Reliance on Science raw file and a broader OpenAlex lookup.

There are also **39 distinct works** in the local patent-citation table with no corresponding institutional row. Because the institutional output is exploded from returned AU affiliations, missing/changed affiliations or absent API results can disappear without an explicit resolution-status record.

**Fix:** remove the scholarly-citation threshold, or start from distinct patent-cited OpenAlex IDs and resolve their Australian affiliations directly. Handle merged/redirected IDs and retain a work-level lookup-status table even when no institution is returned. Compare requested IDs, returned IDs, works with AU affiliations and exploded institutional rows. Preserve confidence scores and counting units. Re-querying OpenAlex may require the existing key and budget; no paid harvest was run for the original review.

### F42 — Additional public sources worth adding for the research questions

The initial audit missed useful direct measures of public-research commercialisation and institution-level research income. These should supplement patent and citation proxies.

| Source | What it adds | Ingestion approach and limitation |
|---|---|---|
| [National Survey of Research Commercialisation, DISR](https://www.industry.gov.au/publications/national-survey-research-commercialisation-data) | Publicly downloadable **2000–2016 unit-record XLSX**, patent/PBR holdings, controlled-entity patent activity and historical commercialisation measures | Read the survey's codebook and unit-record workbook; normalise institution and year, preserve non-response and controlled-entity relationships. Join through a reviewed institution/ROR/ABN bridge. The survey has ceased; do not extrapolate it to current years. The older 2000–2015 catalogue record carries CC BY 2.5 AU; retain the actual selected release's licence rather than assuming all releases have identical terms. |
| [HERDC research-income time series, Department of Education](https://www.education.gov.au/research-block-grants/resources/research-income-time-series) | Downloadable **1992–2024** institutional research-income series, improving the denominator for university IP and research comparisons | Ingest XLSX by institution/year/income category and retain definition changes. Link institutions through a reviewed bridge; income is not expenditure or commercialisation revenue. Departmental material defaults to [CC BY 4.0 with stated exceptions](https://www.education.gov.au/using-site/copyright); check workbook-specific notices. |
| [SCOPR, Knowledge Commercialisation Australasia](https://www.techtransfer.org.au/scopr/) | Recent public reports/dashboard on commercialisation income, deals, industry contracts and new companies | Add public aggregate metrics and survey coverage to the evidence register or an aggregate table. **Do not describe its respondent-level spreadsheet as open data:** KCA says it is supplied to respondents. Participation is voluntary and self-reported, and respondent composition changes. The public report's reuse terms must be checked separately. |
| [PHIDU SA2–PHA 2021 concordance](https://phidu.torrens.edu.au/help-and-information/help-guides-and-faq/geographical-structures/pha-list-2021) | Makes already-collected health/context indicators geographically linkable | Ingest the published crosswalk with ASGS vintage; respect PHIDU's CC BY-NC-SA terms. This is geographically different from the postal references in the first audit. |
| [OCP Australian procurement bulk data](https://data.open-contracting.org/en/publication/19) | Downloadable compiled contracting processes and linked objects, useful for cross-checking the repository's release handling | Use JSON or linked CSV tables, CC BY 3.0 AU. Retain known upstream quality caveats; it is a second delivery route for AusTender data, not an independent procurement census. |

These candidates were verified at their publisher/download-catalogue pages; a complete row-level ingestion and linkage trial was not performed. SCOPR is deliberately distinguished from openly licensed unit-record datasets. Neither these additions nor better linkage provides a causal counterfactual on its own.

## 6. Dates, official fees, medicines and public outcomes

### F12 — Patent enforceability dates: distinguish two different dates

**Location:** `analysis/README.md`; IP RAPID dictionary; `iprapid/patent_rights`.

`enforceable_from_date` is empty for all 1,752,428 patents. But **620,825 have `gained_enforceable_status_date`**, and **658,871 have `gained_registration_status_date`**. The dictionary distinguishes the date a right gained enforceable status from the earlier date from which protection may operate. These are not interchangeable fields.

**Fix:** use `gained_enforceable_status_date` for analyses of when enforceable status was obtained; retain the other field as unavailable pending a raw-source check. Do not fill it mechanically from priority or grant dates. Provisional patents and uncertified innovation patents also require different treatment. Source: repository `data/raw/iprapid/ip-rapid-data-dictionary.pdf`, application-table definitions.

### F25 — Renewal-event cut-offs and historical dates: unresolved source/selection issue, not proven absence of renewals

**Location:** timeline ADR 0006 and `analysis/eda/build.py`.

The repository says renewal records stop in 2016 for designs and 2018 for trade marks, and excludes `_historical` categories because of migration-date concentrations. The underlying R2 events were unavailable for the original audit. The local dictionary includes renewal-publication categories, so counting only one category may miss another representation; this is a hypothesis to test, not a confirmed repair.

**Fix:** count events by right, exact event type, category, year, standing flag and both effective/declared dates. Check publication-of-renewal, intent-to-renew and renewal-due events separately. Compare totals with public reports and selected register histories. Do not treat all historical categories as unusable without category-specific checks, or all empty months after a first event as zero. Keep raw dates and explicit validity flags for suspicious 1800/1970 dates; some future dates can be scheduled events.

### F38 — “Five-year citations” and timeline zeroes need explicit observation windows

**Location:** `google_patents.py::FAMILIES`, `CITATIONS`; `analysis/eda/build.py::timeline_sql`.

`citing_families_5y` compares the citing publication's **priority date** with the cited family's first priority date plus five years. It does not measure when the citation was made or published; it has no lower-bound condition and no flag indicating whether the cited family has had five years of follow-up. Furthermore, its “citing family priority” is the minimum among publications that carry the citation, not necessarily the minimum over every member of that family. This is a confirmed metric-definition issue; no corrected family counts were calculated because the relevant family/member tables are R2-only.

**Fix:** decide whether the intended measure is a priority-cohort linkage or citations observed within a follow-up window. Name the former accordingly. For the latter retain the earliest relevant citing-publication/citation observation date, specify the anchor, validate chronology, and flag incomplete follow-up using the dataset snapshot. If a true family-priority measure is intended, join to a complete family-date table.

The timeline masks dates before the first observed event, then fills subsequent missing monthly groups with zero indefinitely. First observation does not establish continuous reporting, and this cannot distinguish a source outage or series end from genuine zero activity. Add series-specific coverage intervals and completeness states; apply zero only inside verified coverage. Event-row counts also need a check against distinct applications/events before they are called numbers of rights granted or opposed.

### F18 — Historical IP fees: public primary sources exist outside the Wayback Machine

**Location:** `src/corpus/sources/ipa_fees.py`; data plan; timeline ADR.

The failure to reach the Wayback Machine is an access-route limitation, not proof historical fees are unavailable. The Federal Register publishes historical compilations and amending instruments, including the **2020 fee amendments (`F2020L00997`)** and **2024 fee amendments (`F2024L01093`)**. The [Patents Regulations version history](https://www.legislation.gov.au/Series/F1996B02697) identifies applicable historical compilations; the [Designs Regulations history](https://www.legislation.gov.au/F2004B00136/latest/versions) does the same.

**Fix:** extract dated fee schedules from the relevant patent, trade mark, design and PBR regulations; use amendments and commencement/transitional provisions to construct validity periods. Store right type, service, fee basis, payment channel, amount, start/end dates and source. Validate against published IP Australia schedules. These are official fees, not total attorney or litigation costs.

### R3 — Reconstruct historical IP fee schedules and estimate lifecycle costs

**Delivery link:** Retains Priority 3 and extends F18 from recovering official schedules to lifecycle-cost analysis and direct research on broader costs. Use the identified 2020 and 2024 instruments as starting points; validate each right and commencement provision.

**Why:** Extend the existing current-fee source with validated historical schedules to analyse access costs and policy changes. Official fees remain only one component of total protection costs.

#### Sources

- Historical instruments and version histories identified in F18.
- [IP Australia — Fee review 2023–24](https://www.ipaustralia.gov.au/about-us/accountability-and-reporting/fee-review-2023-24)
- Applicable historical regulations and fee instruments for trade marks, designs and plant breeder's rights; confirm each instrument and commencement date from the Federal Register.

#### Repository implementation

Create `src/corpus/sources/ipa_fees_history.py` or an equivalent module consistent with current conventions.

For each fee schedule item, capture:

- IP right and activity (application, examination, renewal, opposition, extension, etc.).
- Fee amount and currency.
- Applicability conditions (for example, claim count, classes, filing route, entity concession or renewal year), where relevant.
- Effective start and end dates.
- Source instrument, provision/table and URL.
- Source publication/registration date separately from commencement/effective date.
- Confidence/validation status and notes for ambiguous cases.
- Inflation-adjusted amount in a declared base year, where the applicable deflator is defensible.

Validate schedule transitions around known fee changes against official fee-review documents. Do not derive a historical fee solely from the date a webpage or instrument was published.

#### Analyses

1. Estimate official-fee pathways for realistic application-to-renewal scenarios.
2. Compare fee changes against application volume, renewals, lapse/abandonment and applicant characteristics.
3. Examine whether effects differ by right type, business size, first-time filer status and self-filing/representative use where data allow.
4. Use comparison groups and test pre-trends; treat simple before/after comparisons as descriptive.

#### Measure the costs missing from official fee schedules

Design a targeted, voluntary survey of SMEs and IP professionals. Ask about cost ranges for attorney/agent fees, internal staff time, prosecution, renewals, enforcement and disputes, as well as reasons for not filing or abandoning a right and alternative protection methods.

Stratify and report by IP type, business size, industry and filing approach. Report response rates, uncertainty and non-response limitations. Do not extrapolate a small convenience sample to all Australian firms without a defensible weighting strategy.

**Decision question:** Are official fees or broader protection costs plausible barriers for particular groups, and which fee or assistance options deserve further evaluation?

**Acceptance criteria:** Historical values traceable to primary legal/official sources; effective dates validated; fee scenarios tested; current and historical fee schedules distinguish official fees from estimated total protection cost.

### F19 — TGA registration dates: missing from the selected export, available in public records

**Location:** `src/corpus/sources/tga.py`; data plan section 8.

The raw spreadsheet really has only the five columns selected by the loader; dates were not accidentally dropped from that workbook. However, public ARTG detail pages include **ARTG Date**. For example, [ARTG 465220](https://www.tga.gov.au/resources/artg/465220) gives **22 October 2024**. Public assessment reports can also distinguish a registration decision date from entry in the register.

**Fix:** enrich entries by `artg_id` from public detail pages/public summaries, using cached, rate-limited retrieval; add `artg_date`, source URL and retrieval date. Cancellation history needs separate sources and validation. A current-register snapshot may omit cancelled products. Registration is permission to supply, not proof of first commercial sale: use PBS supply/listing information for a separately labelled market-access measure.

### F31 — PBS: the processed data omits the broader monthly report and Section 100 coverage — confirmed selection omission

**Location:** `src/corpus/sources/pbs.py`; `pbs/item_month`; manifest PBS raw files.

The loader processes only filenames matching `dos-jul-YYYY-to-jun-YYYY-phrmcy-type.csv`. These are **supplementary pharmacy-type reports**. The [publisher explicitly says](https://www.pbs.gov.au/statistics/dos-and-dop/dos-and-dop) they exclude Section 100 special arrangements, whereas the monthly XLSX includes broader Section 100 supply. The repository already records `dos-jul-2022-to-jul-2026.xlsx` as an R2 raw file (98,706,319 bytes), but does not process it.

The local `item_month` table contains **279,371 item-month observations**, ending **June 2026**. The raw workbook's filename extends to July; at the audit date, the live publisher page offered the monthly workbook through **August 2026**. These are two distinct issues: a deliberately unprocessed, broader source and an available newer release. The audit did not re-open the R2 workbook or quantify omitted Section 100 prescriptions.

**Fix:** ingest the monthly workbook into a separate canonical item-month series with a report/source-vintage field. Keep the supplementary table for pharmacy-type analysis. Reconcile overlapping Section 85/RPBS totals and revisions; do not append overlapping reports and sum them. Preserve older supplementary-only history with a coverage flag. The publisher says historical supplementary files are frozen, while the monthly report is revised, so identical totals should not be assumed.

**Related join gap:** two codes fail the item-to-drug map for all 72 months: `99999Z` (4,380,574 prescriptions) and `00000B` (144,477). The official [explanatory notes, page 3](https://www.pbs.gov.au/statistics/dos-and-dop/files/dos-and-dop-explanatory-notes.pdf) define `99999Z` as the aggregate for unlisted RPBS-only items. Give it an explicit category; it cannot be assigned to a single drug. The audit did not verify the meaning of `00000B`; preserve it as unresolved. Use a left join so these prescriptions are not silently dropped. Patient plus government costs reconcile within two cents for every local item-month row; no arithmetic error was found in that check.

### R7 — Strengthen the pharmaceutical IP and medicine-cost case study

**Delivery link:** Retains Priority 7. F19 supplies a verified public route for ARTG registration dates, while F31 identifies the broader PBS report and revision handling required before expenditure analysis. Registration dates, PBS listing/supply and first commercial sale remain different events.

**Why:** This is a focused way to examine a potential public-cost pathway for which the repository already contains useful starting sources. It is more tractable than attempting to infer all consumer costs of IP from national inflation.

The reviewed corpus includes pharmaceutical patent/extension information, PBS data beginning in July 2020, TGA data and court judgments. F19 establishes that the selected TGA export lacks dates but public ARTG records provide registration dates. F31 establishes that the processed PBS selection omits broader Section 100 coverage.

#### Actions

1. Enrich TGA registration dates using the ARTG route in F19, validate historical and cancellation coverage, and separately establish authoritative market-entry dates. Repair the PBS report selection, coverage and revisions in F31 before using the expenditure series.
2. Confirm workable identifiers across patents, active ingredients, products, PBS listings and generic/biosimilar products. Record match confidence and unmatched records.
3. Build a medicine-lifecycle table with relevant patent filing/grant/extension dates, product registration dates, PBS listing/supply/expenditure, and generic/biosimilar entry dates where available.
4. Separate government subsidy expenditure from patient co-payments and other costs wherever the data permit.
5. Develop case-level and aggregated analyses of market entry and expenditure changes, with comparators and caveats.

Do not interpret PBS expenditure alone as the full consumer cost of medicine or as a direct measure of the net social cost of pharmaceutical IP. Changes in utilisation, negotiated prices, clinical mix and policy settings also matter.

**Decision question:** In which well-defined cases might patent-related arrangements alter timing of competition, expenditure or access, and what evidence is needed to assess the size of that effect?

**Acceptance criteria:** Identifier/data lineage documented; unmatched rates reported; dates validated; expenditure categories distinguished; comparison approach specified before testing.

### F26 — Court decisions after March 2025 and patent-to-paper coverage: snapshot and jurisdiction limits

**Location:** `src/corpus/sources/fedcourt.py`, `reliance_on_science.py`, `openalex_works.py`.

The [Open Australian Legal Corpus documentation](https://huggingface.co/datasets/isaacus/open-australian-legal-corpus) confirms its Federal Court collection cut-off of 10 March 2025. The [Federal Court publishes newer judgments](https://www.fedcourt.gov.au/digital-law-library/judgments/latest). The date gap is recoverable through a fresh court collection, but the repository's text-based IP filter can also omit cases and should be tested against practice-area listings. Published decisions never represent all disputes or settlements.

[Reliance on Science's current documentation](https://relianceonscience.org/patent-to-paper-citations/) confirms USPTO coverage through 2025; earlier international-citation files remain available at [Zenodo 11461587](https://zenodo.org/records/11461587). Those older files are an extension of jurisdictional coverage, not a fully current worldwide equivalent. The current release restores previously absent 2021–22 in-text citations; do not assume that older defect remains in this repository's newer release.

**Fix:** increment court collection from its cut-off with stable citations/version identifiers. For science links, retain jurisdiction, release date, confidence threshold and coverage window; explore the older international files separately. Check the identifier system before joining to OpenAlex and deduplicate front-page/in-text references.

### F41 — NHMRC: date gaps are real in the selected exports; keep them distinct from parsing errors

**Location:** `nhmrc_grants.py`; the 14 raw grant-round workbooks; `nhmrc_grants/grants`.

The processed table contains **6,663 missing start years** and **7,917 missing end years** across 12,224 grants. Inspection of the grant-sheet headers found no start/end fields in the selected **2014 and 2018–2024** exports. The 2013 export has start year but no end year. In 2016, one raw start/end pair is `TBC`; the remaining available start/end fields in 2015–2017 and 2025–2026 parse successfully. Thus the whole-round blanks checked in the audit are **source-layout omissions**, not demonstrated alias or date-parser failures.

**Fix:** record per-round field availability; preserve `TBC` as an observation status; never infer grant dates from application round or announcement date. Check grant-level official records for date enrichment keyed by application/grant ID and retain the enrichment source. The [outcomes page](https://www.nhmrc.gov.au/funding/data-research/outcomes) and [funding statistics page](https://www.nhmrc.gov.au/funding/outcomes-and-data-research/research-funding-statistics-and-data) offer related data, but the original review did **not** verify an open bulk file that fills all these dates. Treat that enrichment route as unresolved.

### F20 — Border seizures: some separately reported IP statistics exist

**Location:** data plan sections 2 and 8, which drop border enforcement because annual reports do not separate IP seizures.

The narrow annual-report observation may be correct, but the broader implication that no separate public statistics exist is not. An [ABF release dated 22 September 2023](https://www.abf.gov.au/newsroom-subsite/Pages/ABF-not-playing-around-with-counterfeit-toys.aspx) reports over **112,000 individual items** seized in the 2023 financial year, estimated at almost **$40 million**.

**Fix:** create a small cited annual-statistics table from ABF releases and published parliamentary answers; retain exact period, measure, qualifications and valuation basis. Individual incidents must not be summed with annual totals. This establishes a partial public route, not a verified complete annual series or shipment-level dataset.

### F21 — NATSEM life satisfaction/trust: dataset existence verified; access still unresolved

**Location:** data plan section 2 and source-selection table.

The [NATSEM 2016 SA2 life-satisfaction catalogue record](https://researchdata.edu.au/natsem-life-satisfaction-sa2-2016/2737908) remains published, describes open access via the AURIN Download Manager and specifies **CC BY-NC 4.0**. These are synthetic modelled estimates, not direct observations of every SA2. The audit verified the metadata and download route, not successful retrieval of the dataset bytes.

**Fix:** change 'no public source' to 'known public dataset; automated retrieval not verified'. Try the publisher-linked Download Manager and, if accessible under its stated conditions, retain the 2016 SA2 geography and model provenance. Crosswalk to 2021 only with appropriate weights. Trust is a separate indicator/dataset and requires its own retrieval. Census volunteering and PHIDU health are contextual alternatives, not equivalent measurements of life satisfaction or trust.

## 7. Policy evaluation and intervention decisions

### R6 — Establish a policy-event evaluation framework

**Delivery link:** Retains Priority 6. Resolve event definitions and coverage (F12, F25 and F38), fees (F18/R3), ownership attribution (F34–F35) and relevant outcome-table defects before estimating effects. Evaluation questions and designs should be specified before outcome testing.

**Why:** The repository already has a policy-event history. It should be used to frame evaluable questions, not merely add vertical markers to time-series charts.

#### Repository deliverables

- `docs/evaluation-plan.md`
- `analysis/notebooks/04_policy_events.ipynb` (adapt path to repository conventions)
- An evaluation register linked to existing policy-event, rights, firms and timeline sources.
- A reusable intervention evidence-card template.

Each proposed evaluation should record:

- Policy/intervention and verified effective date.
- Target/affected population and plausible mechanism.
- Primary outcome and secondary/distributional outcomes.
- Comparison group or counterfactual strategy.
- Pre/post windows and plausible lag.
- Confounders, assumptions and data limitations.
- Pre-trend and placebo tests, alternative specifications and sensitivity analysis.
- Costs and the decision the findings could change.
- Analysis status, review and confidence rating.

Verify policy dates from primary sources before analysis. Do not interpret co-occurrence with a policy date as evidence of impact.

#### Three initial evaluation candidates

**A. IP fee changes effective 1 October 2024**

Use the official fee review and historical schedule. Compare activity types with different fee changes where a defensible comparison exists. Outcomes may include applications, renewals, lapse/abandonment, applicant type and filing method. Two years of post-change data is limited for long-run outcomes; make that constraint explicit. Policy changes are not randomly assigned, so check pre-trends and concurrent changes.

**B. Innovation-patent phase-out**

Investigate whether affected businesses/technology areas substituted into standard patents or other protection methods, changed filing patterns or showed different subsequent outcomes. Define affected and comparison groups carefully and account for self-selection and the changing policy environment.

**C. Prospective evaluation of a future SME-support intervention**

Before launch, agree target population, intervention mechanism, outcomes, costs and counterfactual. Where fair and feasible, randomise outreach timing/intensity among otherwise eligible groups while preserving ordinary services. Otherwise use a defensible quasi-experimental design. Measure more than registrations: include appropriate-use decisions, reduced barriers, commercialisation and other intended public outcomes.

Use the [Commonwealth Evaluation Policy and Toolkit](https://www.finance.gov.au/about-us/news/2021/commonwealth-evaluation-policy-and-toolkit) as a methodological reference, alongside current applicable Finance guidance.

#### Evidence-card output

For each evaluation, publish a concise record of: question; intervention; comparison; results; robustness; who benefited or lost; cost; limitations; confidence; and the decision recommended. Separate the observed result from the policy implication.

**Decision question:** What should IP Australia continue, modify, scale or stop—and on what evidence?

**Acceptance criteria:** Pre-specified question and outcome; primary-source event date; comparison strategy justified; pre-trend/placebo/robustness checks where appropriate; limitations and distributional outcomes reported.

## 8. Shared implementation requirements and completion criteria

### Data engineering requirements

Every new source should:

1. Preserve its originating publisher, exact URL, retrieval date, reference period, licence/terms and any access restrictions.
2. Record the raw data's hash where feasible and retain raw inputs when licensing permits.
3. Declare unit of observation, geographic level, time frequency, units, denominator and classification versions.
4. Validate row counts, expected columns, data types, key uniqueness where applicable, missing values and known totals.
5. Document every transformation, join key, match rate and many-to-many join risk.
6. Track revisions to published data and distinguish publication date from reference period.
7. Avoid treating absent observations as zero; distinguish zero, not applicable, suppressed, missing and not collected.
8. Keep restricted data outside the public repository and publish only outputs cleared for release.
9. Link the source to the relevant `rights`, `firms`, `regions`, `national` or `timeline` analytical view only when units and definitions align.
10. Maintain a record of research hypotheses and decisions so that the analysis does not silently become a search for favourable correlations.

In addition to these source-level requirements, each repair must retain the original source value, transformation and unresolved-null reason, and report before/after records and non-null values. Separate source completeness, analytical selection, linkage success and final analytical coverage. Postal and other one-to-many reference joins must not silently multiply rights; event rows must not be labelled as distinct rights without checking the counting unit. Validate revisions and reporting windows before converting missing periods to zero.

After rebuilding, run the repository checks and reconcile source modules, manifest, catalogue, data plan and analytical definitions. Existing row-count and schema checks remain useful, but the OECD loss shows they cannot establish value retention or semantic correctness. Compare restricted/R2 raw and processed data when authorised access becomes available before asserting completeness; retain observed, suppressed, not applicable, missing, not collected and deliberately withheld states separately.

### Questions to answer before adding an indicator

For each proposed variable, document:

- What decision could this variable change?
- What mechanism connects it to the outcome of interest?
- Is the measure an input, activity, output, outcome, cost or contextual factor?
- What is the correct unit of analysis and denominator?
- Are the geography, time coverage and definitions compatible with other data?
- Is the variable independently useful, or does it duplicate an existing indicator?
- Could observed association be caused by reverse causality, selection or a common trend?
- Can the analysis distinguish the effect of IP protection from other advantages of the businesses that choose to use it?
- What evidence would be sufficient to change a policy decision?

Do not add variables solely because they are available or correlate with a headline innovation measure.

### Programme outputs

The programme should produce:

1. A versioned public-data corpus with source metadata and quality checks.
2. A documented affordability/economic-context layer.
3. A refreshed innovation-barriers dataset with comparability notes.
4. A traceable historical schedule of official IP fees and a separate evidence base for broader protection costs.
5. A written decision on the feasibility of approved linked business-data access.
6. Better-documented participation measures for underserved groups.
7. A policy evaluation register, reusable analysis methods and concise evidence cards.
8. A medicine lifecycle case study with explicit linkage and causal limitations.
9. A prioritised intervention portfolio that describes target group, barrier, mechanism, likely benefit, implementation cost, risks, evidence strength and evaluation plan.

The intended result is a decision-support evidence base that can indicate **which intervention is likely to improve which outcome for which group, what it may cost, how uncertain the estimate is, and how success will be evaluated**. Additional indicators should serve those decisions. The audits’ corrective backlog is part of making that evidence credible.

## 9. Read-only reproduction queries

The following queries are retained from the audits. Run them with DuckDB from the root of the **pinned repository**, where the referenced files exist. They are diagnostic checks, not ingestion or repair commands, and were not rerun during this consolidation. Results may change after a repair or refresh. The second block returns aggregates rather than personal records.

### Initial-audit checks

```sql
-- Confirms the OECD loss without an external request.
SELECT count(*) AS rows,
       count(*) FILTER (WHERE trim(OBS_VALUE) <> '') AS nonempty_source_values
FROM read_csv('data/raw/oecd/ip_tax_regimes.csv.gz', all_varchar=true);

SELECT count(*) AS rows, count(value) AS retained_numeric_values
FROM 'data/processed/oecd/ip_tax_regimes.parquet';

-- Separates unknown country from recorded overseas country.
SELECT count(*) AS patents,
       count(*) FILTER (WHERE applicant_country IS NULL) AS unknown_country,
       count(*) FILTER (WHERE applicant_country IS NULL
                         AND NOT any_applicant_in_australia) AS unknown_with_false_au_flag,
       count(*) FILTER (WHERE applicant_country <> 'au'
                         AND applicant_postcode IS NOT NULL) AS foreign_with_postcode
FROM 'data/processed/iprapid/patent_rights.parquet';

-- Identify the existing OECD GERD/GDP series before adding it to the national lens.
SELECT time_period, value, observation_status, observation_status_label
FROM 'data/processed/oecd/msti.parquet'
WHERE reference_area = 'AUS' AND measure = 'G' AND unit_of_measure = 'PT_B1GQ'
ORDER BY time_period;
```

### Second-pass checks

```sql
-- CER: years erroneously stored as postcodes.
SELECT count(*) AS rows, min(postcode), max(postcode)
FROM 'data/processed/cer/installations.parquet'
WHERE dataset = 'historical-voluntary-state-data-battery-installation-small-scale-systems';

-- CER: exact duplicate representation of one solar-installation series.
WITH a AS (
  SELECT lpad(postcode,4,'0') AS pc, period, measure, value
  FROM 'data/processed/cer/installations.parquet'
  WHERE dataset='sgu-solar-installations-2011-to-present-and-totals'
), b AS (
  SELECT lpad(postcode,4,'0') AS pc, period, measure, value
  FROM 'data/processed/cer/installations.parquet'
  WHERE dataset='sres-postcode-data-installations-2011-to-present-and-totals:SGU-Solar'
)
SELECT count(*) AS joined, count(*) FILTER (a.value=b.value) AS identical
FROM a JOIN b USING (pc,period,measure);

-- Amendments available but not used by firms_sql.
SELECT count(*) AS amended_rows, count(DISTINCT abn) AS abns,
       sum(rd_expenditure) AS original, sum(rd_expenditure_amended) AS amended
FROM 'data/processed/rdti/entities.parquet'
WHERE rd_expenditure_amended IS NOT NULL;

-- Repeated contract IDs: revisions are not all duplicate downloads.
SELECT count(*) AS repeated_ids, sum(n-1) AS extra_rows
FROM (
  SELECT cn_id, count(*) AS n
  FROM 'data/processed/austender/contracts.parquet'
  GROUP BY 1 HAVING count(*) > 1
);

-- Selected patent-owner ABNs absent from the analysis spine.
SELECT count(*) AS rights, count(DISTINCT any_applicant_abn) AS abns
FROM 'data/processed/iprapid/patent_rights.parquet'
WHERE any_applicant_abn IS NOT NULL
  AND any_applicant_abn NOT IN (
    SELECT abn FROM 'data/processed/linkage/abn_spine.parquet'
  );

-- PBS coverage and unmapped codes.
SELECT min(month), max(month), count(*)
FROM 'data/processed/pbs/item_month.parquet';
SELECT item_code, count(*) AS months, sum(prescriptions) AS prescriptions
FROM 'data/processed/pbs/item_month.parquet'
WHERE item_code NOT IN (
  SELECT item_code FROM 'data/processed/pbs/item_drug_map.parquet'
)
GROUP BY 1;
```

## 10. Repository locations and traceability

### Where the original missing-data claims occur

Paths below are relative to the pinned repository. [Browse the reviewed source tree](https://github.com/Thomas-Amann-IPAustralia/Aus-GII-Breakdown/tree/38b5ddd9d5d764b683ae076c308d9285ee459357).

| Location | Missing or incomplete data discussed |
|---|---|
| `analysis/README.md`, `analysis/output/PROFILE.md`, `analysis/output/columns.csv` | Null and blank columns, postcodes, ABNs, patent-number joins, placeholder dates |
| `docs/data-plan.md`, especially sections 2, 4 and 8 | Historical fees, TGA dates, IPLORD patents, WDI trade marks, VC, border enforcement, wellbeing, demographics, firm outcomes |
| `docs/catalogue.md` | Repeats source-specific limitations and describes coverage |
| `docs/eda-plan.md`, `docs/adr/0005-lens-definitions-v1.md` | Claim that roughly 80% of patent rights lack Australian postcodes because applicants are overseas |
| `docs/handover-eda.md`, `analysis/notebooks/01_univariate.ipynb` | R&D expenditure, researchers and technicians series; SEIFA gaps |
| `docs/adr/0006-timeline-lens.md`, `analysis/eda/build.py` | Renewal cut-offs, historical-event exclusions, fee history, leading blanks in monthly series |
| `src/corpus/sources/google_patents.py` | Missing harmonised countries, international filing undercount, limited downloaded family members |
| `data/processed/gii/data.parquet`, raw GII workbook | Missing scores and underlying observations, including six Australian indicators |
| `src/corpus/sources/fedcourt.py`, `reliance_on_science.py` | Court collection date and patent-to-paper coverage limits |

### Repository reference pages

- [Aus-GII-Breakdown README](https://github.com/Thomas-Amann-IPAustralia/Aus-GII-Breakdown/blob/main/README.md)
- [Data plan](https://github.com/Thomas-Amann-IPAustralia/Aus-GII-Breakdown/blob/main/docs/data-plan.md)
- [Data catalogue](https://github.com/Thomas-Amann-IPAustralia/Aus-GII-Breakdown/blob/main/docs/catalogue.md)
- [EDA plan](https://github.com/Thomas-Amann-IPAustralia/Aus-GII-Breakdown/blob/main/docs/eda-plan.md)

These `main` links are navigation aids; the audit’s evidence is tied to the pinned commit stated at the start. External source links are retained beside the relevant findings, source tables and research workstreams rather than repeated in a separate bibliography.

### Source-document mapping

| Supplied document | Content retained | Consolidation treatment |
|---|---|---|
| `Aus-GII-data-gap-audit (2).md` | Original findings 1–28, scope and limitations, postal source table and trial, initial repair order and SQL. | All substantive content retained once; it is also present in the expanded audit. |
| `Aus-GII-data-gap-audit (1).md` | The same initial audit plus the second-pass update, findings 29–42, additional validation results, repair priorities and SQL. | F01–F42 grouped by theme; common scope and sequencing combined in section 1; both SQL blocks retained in section 9. |
| `Aus-GII-Breakdown-Gap-Closure-Plan(1).md` | Seven proposed priorities, detailed actions and analyses, source links, decision questions, acceptance criteria, engineering requirements and intended outputs. | R1–R7 placed beside related findings; shared implementation sequence and requirements consolidated in sections 1 and 8. |

The principal reconciliations are explicit: confirmed audit repairs precede use of affected measures; the existing public business-owner tables are the starting point for R5; ARTG registration-date recovery and PBS coverage repairs feed R7; BLADE remains a proposed reopening of an earlier access decision; and the direct-versus-inferred, descriptive-versus-causal and source-gap-versus-processing-error distinctions remain intact.

### Finding index

| ID | Finding | Section |
|---|---|---|
| [F01](#f01--oecd-ip-tax-regimes-confirmed-ingestion-failure--repair-first) | OECD IP tax regimes: confirmed ingestion failure — repair first | 2 |
| [F02](#f02--world-bank-trade-marks-obsolete-requested-codes-not-the-disappearance-of-trade-mark-statistics) | World Bank trade marks: obsolete requested codes, not the disappearance of trade mark statistics | 4 |
| [F03](#f03--overseas-postcodes-present-in-the-corpus-deliberately-removed-from-the-australian-lens) | Overseas postcodes: present in the corpus, deliberately removed from the Australian lens | 3 |
| [F04](#f04--unknown-country-is-treated-as-non-australian-confirmed-transformation-problem) | Unknown country is treated as non-Australian: confirmed transformation problem | 3 |
| [F05](#f05--australian-postcodes-not-matching-abs-poas-partly-a-reference-mismatch) | Australian postcodes not matching ABS POAs: partly a reference mismatch | 3 |
| [F06](#f06--old-australian-patent-number-joins-the-profile-ignores-a-conversion-already-implemented) | Old Australian patent-number joins: the profile ignores a conversion already implemented | 3 |
| [F07](#f07--google-patents-blank-fields-mixed-semantics-plus-a-genuinely-incomplete-selection-frame) | Google Patents blank fields: mixed semantics, plus a genuinely incomplete selection frame | 3 |
| [F08](#f08--iplord-patent-columns-probable-source-release-issue-not-independently-resolved) | IPLORD patent columns: probable source-release issue, not independently resolved | 3 |
| [F09](#f09--iplord-modal-class-blanks-and-pbr-blanks-in-the-abn-subset) | IPLORD modal-class blanks and PBR blanks in the ABN subset | 3 |
| [F10](#f10--pbr-abns-missing-links-not-missing-applications) | PBR ABNs: missing links, not missing applications | 3 |
| [F11](#f11--asic-zero-abns-and-ato-empty-acns-clean-placeholders-and-reuse-existing-links) | ASIC zero ABNs and ATO empty ACNs: clean placeholders and reuse existing links | 3 |
| [F12](#f12--patent-enforceability-dates-distinguish-two-different-dates) | Patent enforceability dates: distinguish two different dates | 6 |
| [F13](#f13--most-all-null-columns-are-optional-metadata-not-lost-observations) | Most all-null columns are optional metadata, not lost observations | 2 |
| [F14](#f14--abs-bcs-and-seifa-missing-observations-substantial-evidence-of-source-suppressionavailability-limits) | ABS BCS and SEIFA missing observations: substantial evidence of source suppression/availability limits | 2 |
| [F15](#f15--australias-rd-expenditure-some-data-are-already-present-but-unused) | Australia's R&D expenditure: some data are already present but unused | 4 |
| [F16](#f16--researchers-and-technicians-the-missing-totals-are-not-fixed-by-adding-sector-figures-indiscriminately) | Researchers and technicians: the missing totals are not fixed by adding sector figures indiscriminately | 4 |
| [F17](#f17--six-missing-australian-gii-indicators-present-as-blanks-in-the-supplied-source) | Six missing Australian GII indicators: present as blanks in the supplied source | 4 |
| [F18](#f18--historical-ip-fees-public-primary-sources-exist-outside-the-wayback-machine) | Historical IP fees: public primary sources exist outside the Wayback Machine | 6 |
| [F19](#f19--tga-registration-dates-missing-from-the-selected-export-available-in-public-records) | TGA registration dates: missing from the selected export, available in public records | 6 |
| [F20](#f20--border-seizures-some-separately-reported-ip-statistics-exist) | Border seizures: some separately reported IP statistics exist | 6 |
| [F21](#f21--natsem-life-satisfactiontrust-dataset-existence-verified-access-still-unresolved) | NATSEM life satisfaction/trust: dataset existence verified; access still unresolved | 6 |
| [F22](#f22--venture-capital-after-201819-real-discontinuation-existing-oecd-data-do-not-solve-australias-gap) | Venture capital after 2018–19: real discontinuation; existing OECD data do not solve Australia's gap | 4 |
| [F23](#f23--first-nations-and-business-owner-demographics-some-public-denominators-can-be-added-now) | First Nations and business-owner demographics: some public denominators can be added now | 5 |
| [F24](#f24--small-firm-turnover-employment-productivity-and-causal-outcomes-genuine-public-linkage-limitation) | Small-firm turnover, employment, productivity and causal outcomes: genuine public-linkage limitation | 5 |
| [F25](#f25--renewal-event-cut-offs-and-historical-dates-unresolved-sourceselection-issue-not-proven-absence-of-renewals) | Renewal-event cut-offs and historical dates: unresolved source/selection issue, not proven absence of renewals | 6 |
| [F26](#f26--court-decisions-after-march-2025-and-patent-to-paper-coverage-snapshot-and-jurisdiction-limits) | Court decisions after March 2025 and patent-to-paper coverage: snapshot and jurisdiction limits | 6 |
| [F27](#f27--ipc-to-industry-gaps-incomplete-crosswalk-coverage-not-missing-patents) | IPC-to-industry gaps: incomplete crosswalk coverage, not missing patents | 4 |
| [F28](#f28--tm-link-joins-and-omitted-text-distinguish-linkage-coverage-from-deliberate-scope) | TM-Link joins and omitted text: distinguish linkage coverage from deliberate scope | 3 |
| [F29](#f29--cer-years-are-ingested-as-postcodes-and-historic-totals-have-broken-labels--confirmed) | CER: years are ingested as postcodes, and historic totals have broken labels — confirmed | 2 |
| [F30](#f30--cer-equivalent-csv-and-excel-tables-are-both-loaded--confirmed-duplication-risk) | CER: equivalent CSV and Excel tables are both loaded — confirmed duplication risk | 2 |
| [F31](#f31--pbs-the-processed-data-omits-the-broader-monthly-report-and-section-100-coverage--confirmed-selection-omission) | PBS: the processed data omits the broader monthly report and Section 100 coverage — confirmed selection omission | 6 |
| [F32](#f32--rd-tax-incentive-amendments-and-report-revisions-are-ignored-by-the-firm-lens--confirmed) | R&D Tax Incentive: amendments and report revisions are ignored by the firm lens — confirmed | 2 |
| [F33](#f33--austender-releases-are-flattened-into-contract-ids-then-summed--confirmed-structural-problem) | AusTender: releases are flattened into contract IDs, then summed — confirmed structural problem | 2 |
| [F34](#f34--the-firm-spine-omits-some-abns-used-by-the-rights-lens--confirmed) | The firm spine omits some ABNs used by the rights lens — confirmed | 3 |
| [F35](#f35--business-age-is-a-registrationstatus-proxy-not-a-verified-founding-date) | Business age is a registration/status proxy, not a verified founding date | 3 |
| [F36](#f36--abs-workbook-parsing-drops-annotated-zeroes-and-loses-units--confirmed) | ABS workbook parsing drops annotated zeroes and loses units — confirmed | 2 |
| [F37](#f37--openalex-research-to-patent-coverage-excludes-scholarly-uncited-works-before-the-patent-join) | OpenAlex research-to-patent coverage excludes scholarly-uncited works before the patent join | 5 |
| [F38](#f38--five-year-citations-and-timeline-zeroes-need-explicit-observation-windows) | “Five-year citations” and timeline zeroes need explicit observation windows | 6 |
| [F39](#f39--re-running-a-source-does-not-consistently-refresh-it--confirmed-code-level-risk) | Re-running a source does not consistently refresh it — confirmed code-level risk | 2 |
| [F40](#f40--some-collected-data-lacks-the-linkage-or-lens-columns-needed-for-the-stated-analysis) | Some collected data lacks the linkage or lens columns needed for the stated analysis | 3 |
| [F41](#f41--nhmrc-date-gaps-are-real-in-the-selected-exports-keep-them-distinct-from-parsing-errors) | NHMRC: date gaps are real in the selected exports; keep them distinct from parsing errors | 6 |
| [F42](#f42--additional-public-sources-worth-adding-for-the-research-questions) | Additional public sources worth adding for the research questions | 5 |

### Research-workstream index

| Original priority / ID | Workstream | Section |
|---|---|---|
| [R1](#r1--add-a-public-affordability-and-economic-conditions-layer) | Add a public affordability and economic-conditions layer | 4 |
| [R2](#r2--refresh-abs-business-innovation-and-barriers-data) | Refresh ABS business innovation and barriers data | 4 |
| [R3](#r3--reconstruct-historical-ip-fee-schedules-and-estimate-lifecycle-costs) | Reconstruct historical IP fee schedules and estimate lifecycle costs | 6 |
| [R4](#r4--revisit-access-to-abs-blade-for-linked-business-outcomes) | Revisit access to ABS BLADE for linked business outcomes | 5 |
| [R5](#r5--improve-participation-and-underserved-group-measures) | Improve participation and underserved-group measures | 5 |
| [R6](#r6--establish-a-policy-event-evaluation-framework) | Establish a policy-event evaluation framework | 7 |
| [R7](#r7--strengthen-the-pharmaceutical-ip-and-medicine-cost-case-study) | Strengthen the pharmaceutical IP and medicine-cost case study | 6 |
