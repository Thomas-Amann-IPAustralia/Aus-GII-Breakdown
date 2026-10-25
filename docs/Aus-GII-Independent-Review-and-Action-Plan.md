# Independent review of the consolidated data audit, and action plan

**Reviewed:** 25 October 2026, by Claude Code, on branch `claude/pensive-pascal-bdaj89` at commit
`e52d9250bb53a04a5fefb58ba5e5b45a37cd70ed` (also `origin/main`). That commit differs from the one the ChatGPT audit
reviewed (`38b5ddd`) only by adding the audit file itself, so the code and data are the same.

**Subject:** `docs/Aus-GII-Consolidated-Review-and-Action-Plan.md` (the "ChatGPT audit"): 42 findings (F01–F42) and
seven proposed workstreams (R1–R7). Scope and relevance are judged against `docs/research-goal.md`.

**Status:** this is a review only. No code, data or other documents were changed. This file is the only change to the
repository. Its recommendations are proposals until the owner sets the direction (section 5).

## 1. Overall assessment

**Bottom line.** The ChatGPT audit's facts are mostly right. Every count I re-ran matched, to the row. Its remedies,
though, are out of proportion to what the project needs: most would build infrastructure for problems that do not touch
the analysis tables, or that the data cannot fix. Only about a dozen of its 42 findings affect the five lenses that
Stage 1 describes. Those, and three problems the audit missed (N01–N03), call for about a day of small fixes to
`analysis/eda/build.py` before the affected Stage 1 sections are written (checklist A). Everything else can wait until
a later analysis needs it, or can be dropped.

**Verdicts.** Of the 42 findings, I agree with 35 and partly agree with 6. I could not verify 1 (F20). I disagree with
none. Five that the audit left open are now settled, because this session could read the R2 tables the audit could not:
- F08 and F09: the gaps are in IPLORD's own release.
- F10: IP RAPID publishes no ABNs for plant breeder's rights.
- F25: IP RAPID has no renewal events of any kind for patents.
- F28: the gap is inside the TM-Link release.

On the remedies, I recommend:
- adopting the audit's remedy as written for 6 findings;
- a simpler or narrower version for 19;
- a different remedy for 2;
- deferring 7 until an analysis needs them;
- rejecting 8.

Of the workstreams, R3 (historical fees) is the most valuable. R4 (BLADE) is the owner's call. R1 (the affordability
layer) should be dropped.

**Fitness for the research programme.**

| Question | What the corpus can support now | Ceiling without new data |
|---|---|---|
| Q1 Public value | Descriptive histories of every right since 1904. Proxies for value: forward citations and family size (after F06/F38), and how long rights are kept up (from cease and expiry dates, F25). Official fees today only. | No estimate of net welfare. Costs to consumers only in a medicine case study (R7). |
| Q2 Who benefits | Postal area, remoteness, SEIFA, entity type, Australian or overseas applicant (from 1990, F04), and gender from first names (an estimate). | No firm size or industry for most firms (N04). No First Nations, disability or age identifiers. Area measures describe places, not applicants. |
| Q3 Conditions for value | Associations among IP use, R&D claims (three years only), government contracts and large-company income, all within the firm spine. | No outcome panel for small firms (F24). Observational only. |
| Q4 Opportunities | Descriptive gaps, such as places, or R&D-claiming firms, with little IP use; innovation barriers by industry and firm size (survey tables, aggregate only). | The gaps sit within selected populations (N04). They are leads, not proof of unmet need. |
| Q5 Outcomes of interventions | Quasi-experiments on the national monthly series around policy changes (the timeline lens). | Firm-level additionality needs linked outcomes (R4). Fee effects need a fee history (R3). |

**Immediate blockers.** Nothing stops Stage 1 from starting. But six lens variables are wrong or misleading as built,
and describing them first would waste the work (checklist A1–A6):
- AusTender contract values are overstated about four times (F33).
- "Overseas" includes "unknown" (F04).
- The timeline fills decades of missing records with zeros (F38).
- Patent counts mix provisional and complete applications (N01).
- The R&D claims ignore amendments (F32).
- "Age" is not an age (F35).

Most fixes take an hour or two; the timeline one (A3) may take half a day.

**Limitations to accept and state, not fix.**
- Applicant country is unknown for almost all patents filed before 1980 (F04).
- IP RAPID records no renewal events for patents. Its renewal records stop in 2016 for designs and 2018 for trade marks
  (F25).
- IPLORD 2020 has no patent columns, and its trade mark modal classes are blank (F08, F09).
- IP RAPID publishes no ABNs for plant breeder's rights (F10).
- Survey suppression (F14).
- Venture capital stops in 2019 (F22).
- The six blank GII indicators for Australia (F17).
- The public registers show only current status, so business histories are truncated and exits lose their start dates
  (F35).
- No small-firm outcomes, because BLADE was ruled out on 2026-10-22 (F24).
- R&D claims cover 2021-22 to 2023-24 only.
- Court judgments stop at 10 March 2025 (F26).
- The ARTG is a snapshot of the current register (F19).

**How to treat the ChatGPT audit from here.** Keep it as the evidence record that it is. Its "Fix" paragraphs and
section 8 are not the agreed action list; this document's checklist (section 4) is. In particular, do not build what it
proposes in R1, the international postal references, a full model of AusTender releases, or the ten-point engineering
standard before the analyses that need them.

## 2. How this review was done

- **Code.** I read the loaders, linkage, lens build and profile code behind each claim. The register cites them by
  `file:line`.
- **Data.** About 70 aggregate DuckDB queries, none printing raw rows:
  - on the tables in the repository;
  - on 14 R2 tables, cached outside the repository (in `~/.cache/ipholmes`). Unlike the ChatGPT audit, this session
    could read R2.
- **Raw files checked:**
  - the raw IPLORD zip (all seven CSVs);
  - the raw OECD, ABS and CER files.
- **Lenses.** I rebuilt them (`analysis/eda/data/`, which git ignores). `pytest`: 31 tests pass.
- **Live sources:**
  - **Reached:** the World Bank API, the ABS Data API, one day of AusTender's API, the PBS statistics page, the
    Federal Register of Legislation, two ABS pages, and web search results for data.gov.au.
  - **Not reachable from this environment:** the TGA (503), the ABF (403), and the industry.gov.au and
    education.gov.au pages (503). Claims resting on them are marked as unverified.
- **Evidence strength.** Every number here is descriptive: a count from this snapshot. Statements about why a pattern
  exists are marked as inferred.
- **Remedy codes:**
  - **Adopt:** take the audit's remedy as written.
  - **Modify:** keep its aim, with a simpler or narrower fix.
  - **Replace:** a different remedy.
  - **Defer:** do it only when a named analysis needs it.
  - **Reject:** not worth doing.
- **Tiers:**
  - **A:** before Stage 1.
  - **S:** a check to run within Stage 1.
  - **B:** before a named later analysis.
  - **C:** optional, deferred or dropped.

  Effort: S is under 2 hours; M is half a day to a day; L is several days.

## 3. Findings register

IDs F01–F42 and R1–R7 are the ChatGPT audit's. N01–N07 are new. Where findings overlap, the row names every ID it
covers.

### 3.1 Findings that change a lens (decide Stage 1)

| ID | Claim | Verdict | Evidence (this review) | Remedy assessment | Tier |
|---|---|---|---|---|---|
| F33 | AusTender releases are flattened into contract IDs and summed | **Agree; the impact is larger than the audit says** | 1,548,989 notices, 1,377,913 IDs, 96,277 repeated IDs with 171,076 extra rows. In the bulk file, an amendment (`CNxxx-An`) carries the new total: the latest amendment exceeds the parent for 59,097 of 59,664 amended contracts, none is negative, and the median ratio is 1.61. The live API for 1–2 Oct 2026 gave 93 releases for 92 contract IDs, including one `contractAmendment` carrying the amended value. Summing every notice gives $3.85 trillion; one row per parent contract at its latest value gives $0.92 trillion (about 4.2 times less). `linkage.py:60` sums every row. In the firm lens, 17,976 of 72,159 supplier ABNs (24.9%) are overstated by more than 1% (99th percentile: 6.8 times), and 1.46 million notices are counted as 1.20 million contracts. | **Replace:** collapse to one row per parent contract (strip `-A\d+`, keep the latest published value) before summing, and count contracts rather than notices. Defer the release tables, amendment chains and child tables. Label the value as the maximum over the contract's life, not annual spending. | A1 |
| F04 (with F03) | Unknown country is treated as non-Australian | **Agree; the impact is concentrated before 1990** | `iprapid.py:162` coalesces to false. 517,574 patents have no country; 517,375 of them are flagged false, and 76,441 have no applicant at all. Share unknown among standard patents: 96.7–100% for the 1900s–1970s, 52.0% for the 1980s, 0.3% or less from the 1990s. As a result, the timeline's Australian share of standard patents is 0.0–0.7% in each decade before 1980, against 8.5–11.5% since 1990, an artefact. Re-profiling the parties recovers an applicant's country for only 478 of the 517,574; 80,487 have a country only through their attorney. | **Modify:** make `australian_applicant` three-valued (unknown stays NULL). In the timeline, keep unknowns out of the Australian and overseas series and add an "origin unknown" series. **Reject** the party re-profiling and the domestic/foreign/mixed scheme: they would recover almost nothing. Never use the attorney's country as a stand-in. | A2 |
| F38 | "Five-year" citations and timeline zeros need observation windows | **Agree** | (a) `citing_families_5y` compares the citing priority date with the first priority plus 5 years, and has no flag for incomplete follow-up (`google_patents.py`, FAMILIES). (b) `build.py:325` fills zeros from a series' first event onward, which creates decades-long zero runs: trade mark oppositions (first 1909, zero for 777 months to Oct 1973), patents lapsed (544 months to 1961), Australian standard patents (316 months to 1964), patents expired (221 to 1979), ceased (187 to 1975), assignments (124 to 1990), grants (115 to 1967). (c) Event rows are within 1% of distinct rights for grants and cessations; the gap is 2% for patent lapses and 5% for trade mark oppositions. | (b) **Modify:** start each series where continuous records begin (A3). (a) **Modify:** flag families with less than five years of follow-up and rename the measure (B4). (c) Label the series as event counts. | A3, B4 |
| N01 | *New:* provisional applications dominate the patent counts, and their numbers are not comparable across years | **New finding** | In the regions lens window (FY2017–26), 49,364 of 82,411 Australian-postcode patent records (60%) are provisional applications. Both `firms.n_patents` and `regions.patents` (`build.py:138`, `:239`) count every patent sub-type together, so a provisional followed by a complete application counts twice. FY2026 has 10,069 provisionals (7,919 still "filed"), against 4,143–5,388 a year in FY2016–FY2025. In FY2023–FY2025, almost all of them are lapsed or withdrawn (no more than 10 a year "converted"). *Inferred, to confirm in Stage 1 (S1):* the register appears to drop a provisional once a complete application supersedes it, so older years keep mainly the abandoned ones. | Split patents into standard (complete), provisional and second-tier counts, and use standard patents for headline rates. This settles open item 2 in the handover. | A4 |
| F32 | R&D Tax Incentive amendments and revisions are ignored | **Agree; the impact is small** | 944 amended rows (813 ABNs), all different from the original. 188 ABN-year groups have 190 extra rows (`build.py:143-144` takes the maximum). Taking the latest report's row, with its amended value where there is one, changes 922 of 37,771 ABN-years; the total over ABN-years moves from $44.467 billion to $44.321 billion (−$146 million, −0.33%). | **Modify:** in the firm lens, take the row from the latest report and `coalesce(amended, original)`. The processed table already keeps `report`, so no model of report history is needed. | A5 |
| F35 | "Business age" is a registration proxy | **Agree, and the problem is wider** | 26,998 ABNs have no `first_seen` and 47 have dates before 1900. For 16,208 of 39,017 patent filers (41.5%), `first_seen` comes after their first patent year. Of those, 7,900 first filed before FY2001, and ABNs began in 2000 (`first_seen` peaks in 1999 and 2000, at 9,315 and 14,967); 12,934 have no ASIC date. Of 103,008 company ABNs not found in the ASIC extract, 102,644 are cancelled: firms that have exited lack start dates. | **Modify:** relabel the column "years since earliest public registration". Add `age_basis` (ASIC, ABN or GST date) and a flag for truncation (first seen by 2000 with no ASIC date). Prefer the ASIC date for companies. | A6 |
| F34 (with N02) | The firm spine omits ABNs that the rights lens uses | **Agree; the gap is small** | Patents: 1,179 rights and 812 ABNs (0.41% of 287,562 ABN-linked rights). Designs: 329 and 119. Trade marks (not checked by the audit): 10,017 rights and 4,972 ABNs (1.1% of 898,687). Cause: the spine takes founding applicants from `applicant_year` (`linkage.py`), but the lens takes current applicants and owners. | **Modify:** add the `*_rights` ABNs to the spine's IDs at the next rebuild, and document the gap in the meantime. Defer the full party bridge. | A7 (document), B2 |
| N02 | *New:* the lens "applicant" is the current holder, not the filer | **New finding** | `iprapid.py:130` keeps current parties only. For rights filed 2000–2026, the lens applicant's postcode differs from every founding applicant's for about 7% of patents and 11% of trade marks. Names differ for about 11% and 17%, an upper bound because it includes changes in how names are written. | Use the founding applicant to answer "where and who files", and the current one for "who holds". Add the founding applicant's postcode and ABN to the rights lens before Stage 2 (B1). Report the gap in Stage 1 (S7). | S7, B1 |
| N03 | *New:* regional rates are unstable and their parts do not match | **New finding** | 295 of 2,641 postal areas have fewer than 50 active, GST-registered ABNs. The highest `patents_per_1k_businesses` is 4,917. In the window, 34% of Australian patent records (25% of trade marks) are by individuals, while the denominator counts businesses; ten years of filings are divided by a 2026 snapshot. | Set a minimum denominator, or pool small areas into larger ones (SA3). Show intervals, add a per-person rate, and shrink extreme rates for maps. Area associations describe places, not applicants. | B3 |
| F05 (with F03) | Australian postcodes that miss the ABS postal areas | **Agree; the GeoNames trial was not re-run** | 337,454 of 352,020 match and 14,566 (4.1%) do not. For filings from 2016, 85,128 of 90,037 match (94.5%). The misses cluster in PO-box and large-volume ranges (2,159 in 1xxx). | **Modify:** in Stage 1, classify the misses (non-geographic codes against malformed ones). Try a GeoNames Australia lookup only if Stage 2 regional results prove sensitive. No G-NAF. Fix the "about 2,600 real postcodes" wording (A7). | S6, A7 |
| F40 | Plant breeder's rights left out of the firm and regional lenses; PHIDU without its concordance | **Agree** | 1,014 of 3,112 plant breeder's rights in FY2017–26 have an Australian postcode. `phidu.py:27` skips the `PHAs` sheet. | Plant breeder's rights: **Modify:** document the exclusion; adding a count is optional. PHIDU: **Defer:** parse the `PHAs` sheet when PHIDU is used (B12). | A7, B12 |
| F02 | World Bank trade mark series use obsolete codes | **Agree** | `wdi.py:22-24` asks for `IP.TMK.RESD/NRES/TOTL`. The live API answers "indicator not found" for RESD. `IP.TMK.RSCT` and `IP.TMK.NRCT` each give 21 observations for 2004–2024 (2024: 84,859 and 67,644). The panel holds no `IP.TMK` rows. | **Adopt:** switch to RSCT and NRCT, keep the definitions, and do not add them up into a total unless the definitions match. | A8 (optional) |
| F15 | OECD R&D series already held but unused | **Agree** | MSTI's Australian GERD/GDP runs to 2023 (1.682, flagged as an estimate); its 2021 value (1.658) differs from WDI's (1.858). The national lens uses WDI and WIPO only (`build.py`, `national_sql`). | **Adopt:** add MSTI GERD/GDP (and BERD/GDP) labelled with their source. No interpolation. | A8 (optional) |

### 3.2 Ingestion and integrity (tables outside the lenses)

| ID | Verdict | Evidence | Remedy assessment | Tier |
|---|---|---|---|---|
| F01 OECD IP tax regimes lose every value | **Agree** | Raw: 2,639 rows, all non-empty; processed: 0 of 2,639 non-null. 839 are simple percentages. `_abs.py:87` casts every value to a number. Not used in any lens. | **Modify:** keep the raw value as `value_text` for every SDMX flow (one line); parse in the analysis. Skip the mixed-type parser and unit model. | B10 |
| F13 Most all-null columns are optional metadata | **Agree** | 88 columns are all null: 40 OECD (39 metadata, plus the F01 value), 22 IPLORD, 13 ABS BCS `observation_comment`, 8 ABS regions, 4 IP RAPID, 1 ATO. | **Modify:** the profile could label these columns; no loader change. | C |
| F14 ABS survey and SEIFA blanks are source suppression | **Agree** | `ABS_IT_FINANCE`: 2,589 of 5,576 values blank (1,869 marked "n", 720 unmarked). The SDMX loader already keeps the status (3,231 rows carry one). 345 "w" and 20 "z" values are numbers the ABS calls too unreliable. SEIFA IRSAD: 2,624 of 2,643 postal areas have a score. | **Modify:** nothing to build. Analysis rule: drop "n", and exclude or flag "w" and "z". | S5 |
| F36 ABS workbook parser drops annotated zeros and units | **Agree** | 7 `0 (b)` cells (1 in HERDDC02, 6 in HERDDC03), plus 17 `np` and 4 `-` cells, are dropped. HERDDC01's 34 values sit under `col2` with their units ($'000 or person-years) lost. `abs_rd_vc` is in no lens. | **Modify:** in `read_cube`, keep the raw cell text and the unit column, and split a number from its footnote. No layout engine. | B10 |
| F29 CER: years read as postcodes; broken total labels | **Agree** | The state battery file: 108 rows with "postcodes" 2014–2025. 23,548 rows in 16 datasets have the measure `2010)`. | **Modify:** parse the state file and the historic-total headers with their own simple rules; no general schema dispatcher. | B11 |
| F30 CER: CSV and Excel copies both loaded | **Agree, and widespread** | Every CSV series has a workbook sheet with the same row count; for solar installations, all 536,901 rows match exactly. | **Modify:** load one format only, and assert one row per (technology, postcode, period, measure). | B11 |
| F39 Re-running a source does not always refresh it | **Agree** (risk in the code; nothing shown to be stale now) | `core.py:64-66` skips existing files. `oecd.py:50-51` reuses cached flows. `austender.py:34-36` caches by start date only. | **Modify:** before the next corpus refresh, key AusTender's cache by start and end dates and re-fetch the last two windows. Defer the rest. | C |

### 3.3 Identifiers, linkage and geography (outside the lenses)

| ID | Verdict | Evidence | Remedy assessment | Tier |
|---|---|---|---|---|
| F03, the postal reference table and the postal trial | **Agree on the counts** (all six reproduced). Trial not re-run. | The lens keeps Australian postcodes by design. | **Reject the international postal lookups.** Locations of overseas applicants below country level do not serve questions about Australia's system, and the country is already held. | C |
| F06 The patent-number join ignores `au_application` | **Agree; now measured** | The profile uses a digits regex (`profile_corpus.py:255`); `google_patents.py:140` already converts numbers. Match rates against IP RAPID, by filing period, before and after: pre-1990 0% → 79.9%; 1990s 0% → 41.9%; 2000s 37.6% → 44.0%; 2010 on 84.9%, including 57,769 design numbers (kind S), which are not patents. The rest is P-series provisionals (10.1% of 1990s numbers, already documented) and many unmatched 7-digit numbers from the 1990s and 2000s. | **Modify:** profile on `au_application`, leave out kind S, and report rates by decade. Investigate the 7-digit misses with a sample before reaching for the ST.37 file. | B4 |
| F07 Google Patents blanks; incomplete selection of families | **Partly agree** | The meanings are as stated. The undercount of Australian families filed only abroad is already documented (`google_patents.py` docstring); its size is unknown. | **Defer** the PatentsView and ROR enrichment. First size the undercount against WIPO's counts by origin (S). | B4 |
| F08 IPLORD has no patent columns | **Agree; resolved** | All seven CSVs in the raw `iplord_2020.zip` have the same 77 columns, none for patents. This is the source; `iplord.py` already says so. | **Adopt** only the documentation fix: `data-plan.md:237` still names `ipgod/applicant_year` ("to 2022"); it should be `iprapid/applicant_year`. | A7 |
| F09 IPLORD modal-class blanks | **Agree; resolved** | In the raw full CSV (7,303,207 rows), all 8 trade mark modal-class columns are empty. The plant breeder's rights classes are filled in the full file (4,239 filed) and empty only in the ABN subset (see F10). | **Reject** rebuilding them unless a question needs them; IP RAPID's classifications hold the classes. | C |
| F10 Plant breeder's rights have no ABNs | **Agree; resolved** | IP RAPID's party table has 44,503 plant breeder's rights rows and 0 ABNs, in every role, current or founding. | **Reject** name matching for 11,732 rights: high effort and risk for little value. Document it. | C |
| F11 ASIC's zero ABNs and ATO's empty ACNs | **Agree** (not a gap) | ASIC's `abn` is "0" for 1,631,507 of 4,018,291 rows, but the spine joins ASIC by ACN. The ATO `acn` is empty by construction: 32,818 of 33,098 rows give an ABN and the rest give no usable identifier. | **Reject** the ACN enrichment. Set "0" to null at the next ASIC rebuild (trivial). | C |
| F28 TM-Link identifiers join at 93.9% | **Partly agree; cause found** | Of 1,437,110 Australian IDs in `tm_link`, 88,017 are missing from TM-Link's own application table as well as from IP RAPID: the gap is inside the release. | **Reject** changing the keys. Document it. | C |

### 3.4 Innovation indicators and context

| ID | Verdict | Evidence | Remedy assessment | Tier |
|---|---|---|---|---|
| F16 Researcher totals stale; do not add sectors up | **Agree** | WDI's researchers series ends in 2010 and technicians in 2008. MSTI: total researchers 2008; business researchers (FTE) 2023; government and higher education 2022; GERD financed by business 2008. | **Defer:** keep the totals as missing and never add sectors up; add sector series only when a question needs them. | C |
| F17 Six Australian GII blanks are blank at source | **Partly agree** | The six blanks and the 1,224 blank scores are confirmed. On indicator 6.1.3, the corpus's WIPO data already holds utility-model applications of Australian origin (128 in 2024). | **Reject** the supplementary table. Australia's GII rank is not one of the research questions; keep the official release as published. | C |
| F22 Venture capital stops after 2018-19 | **Agree** | OECD's Australian series ends in 2019; its US, UK, Canadian and New Zealand series run to 2025. | **Adopt:** keep the break and do not splice other series onto it; leave industry reports aside. | C |
| F27 Gaps in the IPC-to-industry crosswalk | **Agree; small** | Unmatched classes cover 0.51% of classified patents (1.36% of those since 2016): G16H 1,884; B29H 1,090; G06V 828; G16B 708; F24S 629; H10F 394. They are new subclasses (2018–23) and obsolete ones (B29H/F/J). Separately, 410,610 patents (23%) have no class: all 264,024 provisionals, plus about a fifth of standard patents filed before 1970 (almost all before 1920). | **Modify:** a map of about 10 rows from each new subclass to its predecessor (for example G06V to G06K), flagged as mapped. **Reject** rebuilding from WIPO's concordance for now. | B6 |
| R1 An affordability and economic-conditions layer | **Disagree** (on its priority) | The research goal names socioeconomic circumstances (Q2), and the regions lens already has Census incomes and rents and SEIFA. The proposed links (affordability to IP use) are speculative and heavily confounded, and need seven new loaders. | **Reject** as a workstream. Add an ABS CPI deflator only when money series are compared over time (with R3). | C |
| R2 Refresh the ABS business innovation and barriers data | **Partly agree** | The corpus holds BCS 2021–2023 (IT tables 2018–2020). The ABS Data API has no BCS observations from 2024 ("NoRecordsFound"), but the ABS site lists a 2024-25 release, so a refresh needs a new loader for the data cubes. The tables are aggregate only. | **Defer** until Stage 2 needs barriers by industry and size; then load the latest cube only. | C |

### 3.5 Dates, fees, medicines, research and other sources

| ID | Verdict | Evidence | Remedy assessment | Tier |
|---|---|---|---|---|
| F12 Two different enforceability dates | **Agree** (no action now) | `enforceable_from_date` is empty for every patent in the source application table, while it is filled for 1.63 million trade marks. 620,825 patents have `gained_enforceable_status_date`. The lens uses the registration date. | **Defer:** use the enforceable-status date when an analysis turns on enforceability; never fill the empty field. | C |
| F25 Renewal records stop; the cause was unresolved | **Agree; resolved** | Renewal publications: designs 160,273 (1987–2016); trade marks 492,717 (1987–2018), plus 132,783 "renewal due" (1986–1996). Patents have no renewal or continuation-fee events of any kind. ADR 0006 was right to leave renewals out. | **Replace:** measure how long rights are kept from cease, expiry and lapse dates, treating rights still alive as unfinished (survival analysis), instead of hunting for other event types. | B5 |
| F18 Historical fees exist outside the Wayback Machine | **Agree** | F2024L01093 exists on the Federal Register and amends the Patents, Trade Marks, Designs and Plant Breeder's Rights Regulations (fee amounts). | See R3. | B8 |
| R3 Rebuild historical fees and lifecycle costs | **Agree on value; narrow the scope** | Fees are IP Australia's most direct lever, and fee history is a recorded data gap for Stage 3 (ADR 0006). | **Modify:** take the key official fees (filing, examination, acceptance or registration, renewal by year, trade marks per class) for patents, trade marks and designs, about 2000–2026, from the Federal Register compilations, with effective dates; deflate by CPI. **Defer** plant breeder's rights. The SME cost survey is outward-facing: the owner's call. | B8 |
| F19 TGA registration dates | **Partly agree; the route is unverified here** | The export lacks dates (as `tga.py` says). The TGA site answered 503 from this environment, so the detail-page route could not be checked. Scraping all 98,147 entries would be out of proportion. | **Modify:** enrich only the entries a medicine case study needs (tens to hundreds), by hand or from a machine that can reach the TGA. | C (R7) |
| F31 PBS processed data omits the monthly report and Section 100 | **Agree** (the exclusion is intentional and documented, but it matters: Section 100 includes high-cost specialised medicines, central to the pharmaceutical case) | `pbs.py:34` loads only the pharmacy-type CSVs; its docstring says the xlsx is kept raw. The publisher's page confirms the CSVs leave out Section 100 supply and no longer change, while the monthly xlsx covers sections 85 and 100 and the RPBS to August 2026. `item_month`: 279,371 rows, July 2020 to June 2026. Unmapped codes: `99999Z` (4,380,574 prescriptions) and `00000B` (144,477). | **Adopt** (scoped): load the monthly xlsx as the main series for medicine costs, keep the CSVs for pharmacy type, and give `99999Z` a category of its own. | B9 |
| R7 Pharmaceutical IP and medicine-cost case study | **Agree on relevance** (Q1's costs to consumers) | Needs F31, a targeted F19 and the extension-of-term link. | **Defer** until after Stage 3, or until the owner ranks it. | C |
| F26 Court data stops in March 2025 | **Agree** | Documented in `fedcourt.py` (cut-off 10 March 2025). | **Defer** a refresh until enforcement is analysed. | C |
| F41 NHMRC date gaps are real | **Partly agree** | 6,663 grants lack a start year and 7,917 an end year; the 2014 and 2018–2024 rounds have neither field. Every grant has its round and announcement date. | **Modify:** use the round or announcement year, labelled as such; the audit's "never infer" is too strict. No enrichment. | C |
| F37 OpenAlex leaves out works no paper has cited | **Agree on the mechanism; the size is not measured** | `openalex_works.py:38` filters on `cited_by_count:>0`. Only 39 of 103,644 patent-cited works lack an institution row (0.04%). | **Defer.** A cheap test: look up a sample of patent-cited works missing from `au_works` (two API calls, within the free allowance). | C |
| F42 More public sources | **Partly agree; partly verified** | NSRC: data.gov.au holds unit-record CSVs for 2000–2015 (CC BY 2.5 AU); the "2000–2016 XLSX" could not be confirmed. HERDC income: page unreachable (503); a related series of higher-education R&D spending by provider (1992–2022) exists. SCOPR: not checked. | **Defer.** NSRC is the most useful, for a later strand on research commercialisation (Q1 diffusion, Q3 alternatives). | C |
| F20 Border seizures | **Unable to verify** (the ABF answered 403) | Even if right, it is one category (toys) in one year, not a series. | **Reject** the table. | C |
| F21 NATSEM life satisfaction | **Agree** | The data plan already says NATSEM is unreachable. The estimates are modelled, for 2016. | **Reject:** low value. | C |
| F23 First Nations owner-manager denominators | **Agree** (the source exists: 17,907 owner-managers in 2021, with an XLSX download) | IP data cannot identify First Nations applicants, so there is no numerator. | **Defer** until a numerator and governance exist (the owner's call). | C |
| F24, R4 No small-firm outcomes; reconsider BLADE | **Agree** | The owner ruled BLADE out on 2026-10-22 (`data-plan.md:181`). BLADE is the strongest route to firm-level evidence for Q3 and Q5. | F24: **Adopt:** keep the limitation explicit and use public aggregates as context only. R4: for the owner to decide (section 5); not a prerequisite. | Owner |
| R5 Participation and underserved groups | **Partly agree** (the rules on units and not inferring identity are right) | Within the corpus, the feasible step is gender estimated from names (WGND), reported with its coverage. | **Defer.** Surveys are outward-facing: the owner's call. | C |
| R6 A policy-evaluation framework | **Agree in principle** | 4 of the 13 policy-event dates are still flagged `verify = true` (N05). The strongest candidate is the innovation patent's closure (second-tier applications peaked at 2,789 in August 2021). The October 2024 fee change has only about two years of data after it. | **Modify:** no new notebook or register now. At the start of Stage 3, write a one-page analysis plan for each event. | B7 |
| §8 The ten-point engineering standard | **Partly agree** | Row counts matched while F01 lost every value. | **Modify:** adopt one rule now: each loader asserts that non-empty source values stay non-null or carry a parse flag, and that natural keys are unique. Defer the rest until a refresh. | B10 |

### 3.6 New findings not covered elsewhere

| ID | Finding | Evidence | Recommendation | Tier |
|---|---|---|---|---|
| N04 | The firm lens has no industry and, for most firms, no size, and its membership is selected | The ABR extract has no ANZSIC field. Size is visible only through tax-report income (large companies) and R&D claims. The spine is the union of IP filers, R&D claimants, AusTender suppliers and large taxpayers (`linkage.py`), so "IP user against non-user" within it compares selected groups. ADR 0005 notes the rate caveat but not the limit it puts on Q2 and Q3 claims. | Accept it, and state it in Stage 1. Take propensity denominators from the ABR or CABEE (as the regions lens does), not the spine. Industry comes only from technology for IP filers (probabilistic) or from aggregate tables. | S7 |
| N05 | The policy-event list needs verifying and completing before any event analysis | `policy_events/events` flags 4 of its 13 dates `verify = true` (Plant Breeder's Rights Act 1994, pharmaceutical extension of term 1999, the Productivity Commission response Part 1 in 2019, and the designs grace period in 2022). It has no fee-change events, and no announcement or legislation dates for the innovation patent's phase-out (needed to model anticipation). | Verify the four dates against the Federal Register, and add fee changes (from R3) and announcement dates. | B7 |
| N06 | What `application_date` means for PCT national-phase filings is unconfirmed | Standard patents by overseas applicants show no drop in FY2025 and FY2026 (27,365 and 28,245), although national-phase entries arrive up to about 31 months after priority. Either IP RAPID lists PCT applications before they enter, or the date is not the international filing date. Unresolved: an investigation task. | Settle it in Stage 1 from the IP RAPID dictionary and a sample of PCT-route patents, before any recent-year trend or time-to-grant analysis. | S2 |
| N07 | Stage 2 screening has no intervals and no control for testing many pairs | `bivariate.screen_pairs` ranks every pair by \|r\| or \|rho\|. With large samples, nearly every pair looks "significant". | Keep to the pairs pre-listed at the end of Stage 1; report effect sizes with intervals; check that a signal holds in a second time window. | Stage 2 |

## 4. Prioritised checklist

### A. Before Stage 1 (about a day in all; one ADR)

Do A1–A6 in `analysis/eda/build.py` and `analysis/eda/variables.yaml`. Then rebuild the lenses
(`uv run python -m eda.build`), run the tests, re-run the Stage 1 overview cells, and record the changes in ADR 0007
("lens definitions, version 2", superseding parts of 0005 and 0006). The items are independent of one another; A7
comes last.

| # | Do this | Files | Benefit | Effort | Acceptance |
|---|---|---|---|---|---|
| A1 | Give the firm lens contract counts and values from one row per parent contract. In `firms_sql`, add a CTE over `{austender/contracts}`: `parent = regexp_replace(cn_id, '-A\d+$', '')`; `v = arg_max(value, published)` per `(supplier_abn, parent)`; then `count(*)` and `sum(v)` per ABN. Use these instead of `s.austender_contracts` and `s.austender_value`. Relabel: "Government contracts" and "Contract value at latest amendment (maximum over the contract's life, AUD)". Fix `linkage.py:60` the same way at the next spine rebuild. | `build.py`, `variables.yaml` (`linkage.py` later) | Removes an overstatement of about 4.2 times in total (99th percentile: 6.8 times per firm). (F33) | S | A test asserts no parent contract is counted twice for an ABN. The ADR records the totals before and after ($3.85 trillion against about $0.92 trillion over all notices). |
| A2 | Make applicant origin three-valued. In `rights_sql`: `CASE WHEN applicant_country IS NULL AND NOT any_applicant_in_australia THEN NULL ELSE any_applicant_in_australia END AS australian_applicant`. In `TIMELINE_APPLICATIONS`, use `australian_applicant` and `australian_applicant = false`, and add `patents_standard_origin_unknown`. Remove the coalesce in `iprapid.py:162` at the next IP RAPID rebuild. | `build.py`, `variables.yaml`, `tests/test_eda.py` | Removes the fake pre-1990 "overseas" history of patents. (F04) | S | For each decade, Australian + overseas + unknown = all standard patents. The unknown share by decade is reported in Stage 1. |
| A3 | Start each timeline series where continuous records begin, not at its first event. Compute a start for each series (for example, the first month from which at least 9 of the next 12 months are non-zero), allow overrides in a `TIMELINE_COVERAGE` dict, and set months before the start to NULL. Document real structural zeros, such as second-tier patents after August 2021. | `build.py`, ADR 0007 | The timeline stops showing decades of false zeros. (F38) | S–M | No zero run longer than 12 months after a series' start, except documented structural zeros. The ADR lists each start and why. |
| A4 | Split patent counts by sub-type. In the firm and region `ip` CTEs, replace `n_patents` and `patents` with `*_standard` (`standard_complete`), `*_provisional` and `*_second_tier`, and base the `per_1k` rates on standard patents. | `build.py`, `variables.yaml` | Ends double counting and the FY2026 provisional bulge in the rates. (N01; settles open item 2 of the handover) | S | `variables.yaml` passes its test. Stage 1 shows each sub-type's share. |
| A5 | Resolve R&D claims to one row per ABN-year. `rd_year`: `arg_max(coalesce(rd_expenditure_amended, rd_expenditure), report)` grouped by ABN and income year. | `build.py` | Correct values for 922 ABN-years. (F32) | S | One row per ABN-year. The ADR records 922 of 37,771 ABN-years changed and −$146 million (−0.33%). |
| A6 | Label age honestly. Relabel `age_years` "years since earliest public registration". Add `age_basis` (`asic`, `abn` or `gst`: whichever date set `first_seen`) and `age_truncated` (`first_seen` before 2001-01-01 and no ASIC date). | `build.py`, `variables.yaml` | Prevents age being read as founding age, which matters for Q2's startups. (F35) | S | Stage 1 shows age by `age_basis`. |
| A7 | Correct the record, in one ADR and small doc edits: the ADR 0005 and EDA-plan line "about 80% … because their applicants are overseas" (the true split: 50.3% recorded overseas, 29.5% unknown and mostly before 1990); "about 2,600 real postcodes" becomes "about 2,600 ABS postal areas" (`analysis/README.md`); the profile's statement on the Google Patents join (F06); `data-plan.md:237` (F08); document the gaps from F34, F40 and N04. In the handover, name this document as the action list and the ChatGPT audit as background. | `docs/adr/0007-…`, `docs/eda-plan.md`, `analysis/README.md`, `docs/data-plan.md`, `docs/handover-eda.md`, `GLOSSARY.md` | A record that does not mislead the next session. | S | No document repeats a claim corrected here. |
| A8 (optional, same batch) | Fill the national lens. Switch `wdi.py:22-24` to `IP.TMK.RSCT` and `IP.TMK.NRCT`, then run `corpus run wdi`. Add MSTI GERD/GDP and BERD/GDP to `national_sql` with `source = 'OECD'`. | `wdi.py`, `build.py`, `variables.yaml`; `data/processed/wdi`, manifest | National trade mark counts (2004–2024) and R&D to 2023. (F02, F15) | S | The national lens has both series, labelled with their source; WDI and OECD R&D are kept apart. |

### S. Checks to run within Stage 1 (part of Stage 1, not prerequisites)

1. **S1 (N01):** confirm that the register drops provisionals once they are superseded. Compare provisional counts per
   year with IP Australia's published figures, and look at the status mix by year.
2. **S2 (N06):** find out what `application_date` means for PCT national-phase filings (the IP RAPID dictionary, and the
   `filing` event against the application date for a sample of PCT-route patents).
3. **S3:** what "ceased" means against "lapsed" (an existing open item); placeholder dates (1800, 1901, 1970, existing
   leads).
4. **S4:** state the limitations in section 1 in each lens's text.
5. **S5 (F14):** when ABS survey tables are profiled, drop "n" and flag "w" and "z".
6. **S6 (F05):** classify the postcodes that miss the ABS postal areas.
7. **S7 (N02, N04):** report current-holder against founding-applicant differences, and the spine's selection by
   source, as limits of the firm and rights lenses.

### B. Before later analyses

| # | Do this | Needed before | Files | Benefit | Effort | Acceptance |
|---|---|---|---|---|---|---|
| B1 | Add founding-applicant postcode, ABN and country to the rights lens (from `iprapid/party` where `is_founding`). | Stage 2 regional and firm comparisons | `iprapid.py` or `build.py` | "Where and who files", as against who holds now (N02) | M | Both versions in the lens; the gap reported |
| B2 | Add every `*_rights` ABN to the spine's `ids`. | The next spine rebuild | `linkage.py` | Firms complete (F34) | S | Every lens ABN is in the spine |
| B3 | Rules for regional rates: a minimum denominator or pooling to SA3, Poisson or Wilson intervals, a per-person rate as well, and shrinkage for maps. | Stage 2 regions | `bivariate.py`, notebook | Rates that do not swing on small numbers (N03) | S–M | No rate shown without its denominator and interval |
| B4 | Profile the patent join on `au_application` without kind S, and investigate the 7-digit misses. Flag citation follow-up under 5 years. Size the foreign-only undercount against WIPO counts by origin. | Analyses of patent value (citations, families) | `profile_corpus.py`, `google_patents.py`, `build.py` | Usable value proxies (F06, F07, F38a) | S–M | Match rates by decade; flag present |
| B5 | Build a maintenance (survival) measure from cease, expiry and lapse dates, treating live rights as unfinished. | Q1 private value of rights | New `build.py` lens column or notebook helper | Replaces the missing renewal records (F25) | M | Survival curves by right and cohort, with censoring stated |
| B6 | Map the new IPC subclasses to their predecessors (about 10 rows, flagged). | Industry or technology analyses | `concordances.py` | Covers 1.36% of recent patents (F27) | S | Unmatched share under 0.1% |
| B7 | Verify the four flagged policy dates; add fee-change and announcement events. | Stage 3 timeline §5 | `policy_events.py` | Valid event dates (N05, R6) | S | No `verify = true` left; every date sourced |
| B8 | A scoped history of official fees (R3), with a CPI deflator. | Stage 3 fee analysis | New `ipa_fees_history.py` | Q4 and Q5 on IP Australia's own lever (F18, R3) | M–L | Each fee traceable to an instrument and its commencement date |
| B9 | Load the PBS monthly xlsx (sections 85 and 100, RPBS); categorise `99999Z`. | Medicine-cost work (R7) | `pbs.py` | Covers Section 100 (F31) | M | Monthly totals match the publisher's |
| B10 | A loader test that values are retained (non-empty in, non-null out, or flagged); `value_text` for SDMX; raw text and units for ABS cubes. | Any use of `oecd/ip_tax_regimes` or `abs_rd_vc` | `_abs.py`, `_abs_cube.py`, `tests/` | Catches F01 and F36 problems | S each | The test fails on today's F01 table and passes after the fix |
| B11 | CER: one format only; parse the state file and the historic totals separately. | Green-diffusion analysis | `cer.py` | No duplicated or mislabelled rows (F29, F30) | S | One row per key; no `2010)` measure |
| B12 | PHIDU: parse the `PHAs` sheet into a PHA-to-SA2 concordance (2021). | Any use of PHIDU | `phidu.py` | Makes PHIDU linkable (F40) | S | Every PHA code resolves |

### C. Optional, deferred or dropped

- **Deferred until named:**
  - R2: refresh the BCS from the ABS cubes, for Stage 2 barriers.
  - R5: gender from WGND, in Stage 2.
  - R7: the medicine case study, with a targeted F19.
  - F07: PatentsView and ROR enrichment.
  - F16: sector researcher series.
  - F22: industry VC reports.
  - F26: court refresh.
  - F37: the cheap sample test.
  - F39: refresh hygiene, before the next corpus refresh.
  - F42: NSRC for a research-commercialisation strand.
  - F41: label the round year.
  - F11: ASIC "0" to null.
  - F13: column labels in the profile.
- **Dropped:**
  - R1: the affordability layer (keep only the CPI deflator in B8).
  - F03: the international postal references and the GeoNames trial.
  - F10: name matching for plant breeder's rights.
  - F09: rebuilding the modal classes.
  - F17: supplementary GII data.
  - F20: ABF seizures.
  - F21: NATSEM.
  - F28: changing TM-Link keys.
  - The full AusTender release model, and the rest of section 8's standard until a refresh.

## 5. For the owner

1. **Direction:** confirm that this checklist, not the ChatGPT audit's plan, is the action list, and that tier A
   (about a day) is done before the affected Stage 1 sections. Nothing here needs money.
2. **BLADE (F24, R4):** you ruled it out on 2026-10-22. It remains the only route to small-firm outcomes, and so to
   firm-level additionality for Q3 and Q5. A scoping enquiry to the ABS costs nothing to send, but it is outward-facing
   and may lead to fees. Do you want to reopen it? It is not needed for the EDA.
3. **Outward-facing research (R3's cost survey, R5's user research, First Nations data governance under F23):** not
   recommended now. Your call if and when.
4. **R7 (the medicine case study):** a strong candidate for after the EDA. Please rank it against the other case
   studies when Stage 3 ends.
