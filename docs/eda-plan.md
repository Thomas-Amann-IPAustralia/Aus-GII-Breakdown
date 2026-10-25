# EDA plan: getting to know the data before answering the questions

**Status (2026-10-25):** the groundwork is built, and an independent review of the data has been done
(`docs/Aus-GII-Independent-Review-and-Action-Plan.md`, whose finding IDs are used below). The owner has decided that
every dataset goes through all three stages (ADR 0007). This plan says what the exploratory data analysis (EDA) covers,
where each dataset fits, what each part needs before it starts, and which gaps are worth filling. Decisions are in
`docs/adr/` (0002 to 0007); terms are in `GLOSSARY.md`.

## Why an EDA first

The research goal (`docs/research-goal.md`) asks what public value the IP system creates, for whom, what makes it work,
and where intervention would add most. Answering those well depends on knowing what the data can and cannot say: how
complete each measure is, how it is distributed, what its quirks are, and which relationships are strong enough to be
worth a proper test. The EDA builds that understanding in three stages. It ends with a list of early signals and data
gaps. Only then are the questions themselves tackled.

## The approach: every dataset, every stage

- **Every datapoint goes through all three stages.** Only the approach changes: a variable on its own (Stage 1),
  against one other (Stage 2), against several (Stage 3). This is a discovery phase, so the EDA goes broad.
- **Comparisons need a shared unit.** Two variables can only be compared if they describe the same thing: a right, a
  firm, a place, an industry, a research institution, a country in a year, or a month. So every table in the corpus is
  attached to at least one **lens**, an analysis-ready table with one row per unit. The map is below.
- **Broad, but clean:**
  - one row per key in every lens, checked by a test;
  - where two sources measure the same thing, one is the main measure and the other a labelled comparison; they are
    never added together;
  - totals are not screened against their own parts;
  - known errors are repaired before a table's Stage 1 section.
- **Detail stays reachable.** Where a lens summarises, the detail stays reachable by key, for example every applicant's
  raw postcode and country, overseas ones included, for drilling down later.

## The units of analysis: seven lenses

All lenses are built by `uv run python -m eda.build`, and every column is described in `analysis/eda/variables.yaml`.

| Lens | One row per | Status | Main questions |
|---|---|---|---|
| `rights` | IP right | Built: 4,368,006 rows | Q1, Q2 |
| `firms` | ABN in any IP, R&D, procurement or tax source | Built: 391,983 | Q2, Q3, Q4 |
| `regions` | Postal area | Built: 2,641 | Q2, Q4 |
| `national` | Country, year and indicator | Built: 127,309 | Q1, Q4 (context) |
| `timeline` | Month, for Australia (Jan 1904 to Sep 2026) | Built: 1,473 | Q1, Q4, Q5 |
| `industries` | ANZSIC division and financial year | Planned (ADR 0007; confirmed by the owner) | Q2, Q3, Q4 |
| `institutions` | Australian research institution (ROR) and year | Planned (ADR 0007; confirmed by the owner) | Q1, Q2, Q3 |

**Rules for time.**
- Monthly and quarterly series join the `timeline`. Quarterly series are compared at quarterly resolution, never spread
  across months.
- Annual Australian series join `national`, beside the other countries.
- Comparisons over time use changes, or the months around events, not levels. Series that trend together over decades
  correlate whatever their link (ADR 0006).

## Where every table goes

Each table's variables are brought to the lens's unit by a stated join or aggregation. The column "First" names what it
needs before its Stage 1 section; codes are the review's IDs (A1–A8, B1–B12, Fnn, Nnn, Rn).

| Source (tables) | Lens | What it adds | First |
|---|---|---|---|
| `iprapid` `*_rights`, `application` | rights | The base: one row per right | A2 (origin); keep every applicant's raw postcode, state and country |
| `iprapid/events` | rights, timeline | **Per right:** the dates of the examination request, acceptance, grant, opposition, assignments, licences and extension of term, and of the lapse, cessation or expiry, giving each right's lifetime. **Per month:** counts (already built). | A3 (coverage starts); label events as events (F38); B5 (lifetimes) |
| `iprapid/party` | rights, firms | Applicants by country, all of them rather than only the first; founding filer against current holder; the attorney firm. Individuals are pseudonymised codes in IP RAPID, so their gender cannot be estimated. | B1 |
| `iprapid/links` | rights | The route into Australia: foreign priority claimed, PCT entry, divisional | — |
| `iprapid/classification`, `concordances` | rights, industries | Technology fields and the green-technology flag per right; industry shares for `industries` | B6 (new IPC subclasses) |
| `iprapid/applicant_year`, `iplord` | firms | Filing histories per ABN. IPLORD is used only to check `applicant_year` before 2020, never added to it. | — |
| `iprapid/description` | text | Titles and goods and services descriptions; variables derived only if wanted | — |
| `linkage/abn_spine`, `abr`, `asic` | firms, regions | Firm attributes; business counts by postal area and entity type | A6 (age); B2 (missing ABNs) |
| `rdti` | firms, regions | R&D claims per ABN and year | A5 |
| `ato_ctt` | firms | Income and tax of large entities | — |
| `austender` | firms, regions, timeline | Contracts and their value per ABN (one row per contract), per supplier postal area, per month | A1 |
| `abs_census` (14 tables) | regions | Every table, as shares of its total: education, occupation, industry, labour force, health, care, volunteering, mobility | Totals or parts, not both |
| `abs_regions` (Data by Region, SEIFA, geography) | regions | Regional indicators through SA2-to-postal-area population weights; SEIFA (built); geography as reference | — |
| `abs_cabee` | regions, industries, national | Businesses by employment and turnover size; entries, exits and survival | Weights from `poa_sa2` |
| `phidu` | regions | Health and social indicators through a concordance from PHIDU's areas (PHAs) to SA2s and postal areas | B12 |
| `cer` | regions, timeline | Solar, battery and other small-scale installations per postal area, and nationally per month | B11 |
| `abs_bcs` | industries | Innovation, barriers, finance and IP methods by industry and firm size (aggregate) | Status flags (S5) |
| `abs_rd_vc` | industries, national | Business R&D by industry; R&D by sector; venture capital to 2019 | B10 (workbook parser) |
| `bcarr_creative` | industries, national | Cultural and creative activity by industry and domain | — |
| `abs_labour` (added 2026-10-25) | timeline, national | The Labour Force Survey: employment, unemployment and participation by sex and state, monthly from 1978; owner-managers and employees by sex, monthly from 1991 (the denominator for who runs businesses) | — |
| `abs_prices` (added 2026-10-25) | timeline, industries | CPI (quarterly from 1948), living costs by household type, wages (also by industry) and property prices: background, and the deflator for every money series (fees, R&D, contracts, medicine costs) | — |
| `wdi`, `wipo_ipstats`, `gii`, `oecd`, `mwm`, `ctg` | national | Country-year indicators: every OECD flow (one indicator per named breakdown); GII 2026; WIPO's filings at IP Australia by origin country, 1980–2024 (an independent view of which nations use the system); Australian annual series (Measuring What Matters, Closing the Gap) | F02 and F15 (A8); F01 (B10) |
| `pbs` | timeline; medicines | Prescriptions, and government and patient costs, per month. Items are linked to ingredients for the medicine strand. | B9 (Section 100) |
| `tga` | own unit | ARTG entries; sponsors per ingredient (competition); joins PBS and extension-of-term patents by ingredient | — |
| `fedcourt` | timeline; text | IP judgments per month by right; variables derived from the text later | — |
| `google_patents`, `google_patents_inventors` | rights, firms, institutions | Per Australian application: family size, offices, US grant, forward citations (with a follow-up flag); inventors by country and their estimated gender (expected counts, from `wgnd`) | B4 |
| `openalex`, `openalex_works`, `reliance_on_science` | institutions, rights | Output, citations and patent-cited works per institution; science cited by Australian-linked patent families | F37 test |
| `arc_grants`, `nhmrc_grants` | institutions, timeline | Grants and funding per institution and year (ARC names matched to ROR) | Label round years (F41) |
| `policy_events` | timeline | Policy changes per month; the policy register is reference | B7 |
| `ipa_fees` | timeline, rights | The fee in force each month, and fees per right, once the fee history exists | R3 |
| `wgnd` | reference | The name-gender dictionary behind `google_patents_inventors` | — |
| `evidence`, `wine_gi` | reference | The literature register; the GI list (for certification marks) | — |

## The order of work

Stage 1 goes lens by lens. A lens's section can start with its core variables; each attachment adds a sub-section when
it is built. Each lens's repairs come first.

1. **`rights`** (about half a day before it starts): A2, A4, and keeping the raw applicant location. Then come the
   attachments: events per right, the parties' countries and founding applicants (B1), links, Google Patents (B4) and
   the inventors (with their estimated gender).
2. **`timeline`**: A2 and A3, the policy dates (B7), and quarterly prices and wages (now in the corpus). Later: PBS (B9),
   CER (B11), judgments, contracts, and fees once the fee history exists (R3).
3. **`firms`**: A1, A5 and A6, then B1 and B2.
4. **`regions`**: A4; the rules for small areas (N03: a minimum denominator or pooling, intervals, a per-person rate);
   the postcode check (S6). Then the Census, CABEE, PHIDU (B12) and CER (B11) attachments.
5. **`national`**: A8 (World Bank trade marks, OECD R&D), GII, the OECD flows (B10 for tax regimes), and WIPO by origin.
6. **`industries`**: built new. Needs the IPC map (B6) and the workbook parser (B10).
7. **`institutions`**: built new. Needs a reviewed link from research institutions to ROR identifiers and ABNs, for
   about 60 universities, CSIRO and the medical research institutes.

Record each change to a lens in an ADR, and the repairs to the existing lenses together in one ADR, as the review
proposes.

## Data worth adding

Re-checked on 2026-10-25 with the owner's steer to go broad. Every source here is free.

**Done:**
- Prices, wages and living costs (`abs_prices`): 352,576 CPI values, 18,900 living-cost, 45,936 wage and 6,372 property
  values. Every non-empty source value is kept.
- The Labour Force Survey (`abs_labour`): 434,496 headline values (1978 to September 2026) and 27,027 values of
  employment by status (1991 to September 2026). Every non-empty source value is kept; one row per key. Owner-managers
  numbered 2.14 million in August 2026 (34.8% women), against 1.45 million in August 1991 (31.0% women).

**High value, little work. Add with the lens builds:**
1. **RBA cash rate and exchange rates (monthly), for the timeline.** About 91% of standard patents filed in FY2017–2026
   came from overseas applicants, and the cost to them of filing here moves with the Australian dollar. The cash rate
   gives financing conditions.
2. **ABS national accounts (GDP and state final demand, quarterly), for the timeline and national lenses.** Macro
   background, through the same ABS service as `abs_prices`. (The Labour Force half of this item is done:
   `abs_labour`, including the owner-manager counts that stand in for TableBuilder.)
3. **ATO taxation statistics by postcode (annual, from 2012-13), for the regions lens.** Incomes that change over time
   (the lens now has only the 2021 Census), and a denominator for individual applicants, who make up 34% of Australian
   patent records. First check which table holds counts of business income.
4. **IP Australia's published statistics (the Australian IP Report), as a benchmark for every release.** The lens
   already matches the 2025 figures:
   - standard patents: 30,448 against 30,348 reported;
   - trade marks: up 13.3%, as reported;
   - designs: up 7.1%, as reported.

   It would also confirm the provisional-application puzzle (N01).

**High value, more work:**
5. **Historical official fees (R3).** IP Australia's own lever. With the CPI now held, fees can be compared in real
   terms.
6. **PBS monthly report with Section 100 (B9).** The raw file is already in R2.
7. **ABS business characteristics releases for 2023-24 and 2024-25,** from the data cubes. The API stops at 2023.
8. **Inventors, from Google Patents (approved 2026-10-25; loaded 2026-10-25, one publication per family, ADR
   0008).** IP RAPID records no inventors, and gives individual applicants as pseudonymised
   codes, so this is the only route to inventors' countries and to gender. It shows where inventions are made against
   who owns them, and the expected numbers of women and men among inventors (with WGND).
9. **Research commercialisation:** NSRC unit records, 2000–2015 (licences, spin-outs, patents and income by
   institution), plus research income or R&D spending by university. For the institutions lens.
10. **Court judgments after 10 March 2025.** The Open Australian Legal Corpus page was updated in March 2026, so check
    for a newer collection first, then the Federal Court's own listings.
11. **Census 2011, 2016 and 2021 time-series tables by area,** for change over time in the regions lens.

**Small:**
12. **Supplementary observations for the six GII indicators that are blank for Australia (F17).** Labelled
    "supplementary", beside the official release.
13. **OpenAlex.** Test whether the "cited at least once" filter drops works that patents cite (F37); re-harvest if it
    matters.
14. **Google Patents.** Size how many Australian families filed only abroad are missed, against WIPO's counts by origin
    (F07).

**Needs the owner (an account or a request):**
15. **ABS TableBuilder (on hold; if it is needed, the owner registers as a private user):** Census owner-managers by
    sex, Indigenous status, industry, age and postal area, the denominator for who runs businesses. The tables and
    the clicks are in `docs/tablebuilder-owner-managers.md`. Meanwhile, `abs_labour` (owner-managers nationally), CABEE (businesses by size, per area) and item 3 (individuals with business income, per postcode)
    stand in. What only TableBuilder gives is owner-managers by sex and Indigenous status for each postal area.

**Closed:** BLADE (linked small-firm outcomes) stays ruled out; the owner confirmed this on 2026-10-25. Firm-level
outcomes for small businesses are a limit of this research, stated wherever it bears on a finding.

**Still not worth it, and why:**
- **Mapping overseas postcodes to places:** the raw codes are kept, so this can be done later if a question needs it.
- **Matching names for plant breeder's rights:** IP RAPID publishes no ABNs for them.
- **Rebuilding IPLORD's trade mark classes:** they are blank at source.
- **Changing TM-Link's keys:** the gap is inside the release.
- **Border seizures:** there is no series.
- **NATSEM:** modelled for 2016; PHIDU and the OECD cover wellbeing.
- **A full model of AusTender's releases:** one row per contract gives the same answer.

## The three stages

| Stage | Notebook | Asks | Main tools (`analysis/eda/`) | Finished when |
|---|---|---|---|---|
| 1. Univariate | `analysis/notebooks/01_univariate.ipynb` | What does each variable look like on its own: completeness, shape, outliers, quirks? | `univariate`: `overview`, `describe`, `distribution`, `bin_check`, `counts`, `missing`, `over_time`, `monthly` | Every variable of every lens, and of every attachment, has its profile. The notable ones have numbered observations. Exclusions and transformations are decided and recorded. |
| 2. Bivariate | `02_bivariate.ipynb` | Which pairs move together, in what shape, how strongly, for whom? | `bivariate`: `screen_pairs`, `pair_stats`, `scatter_trend`, `binned_summary`, `compare_groups`, `rate_by`, `rate_chart` | Every pair within each lens has been screened. Each lead has its size and interval, survives a correction for the number of pairs tested, and holds in a second period or sample. Candidate third factors are listed. |
| 3. Multivariate | `03_multivariate.ipynb` | Do the signals survive other factors? What structure and segments exist? | `multivariate`: `corr_heatmap`, `pca`, `scree`, `vif`, `partial_corr`, `clusters`, `assign` | A table of early signals (evidence, strength, question, next step) and a table of data gaps (why, possible source, cost). |

Every variable gets the systematic profile. Written observations are kept for what is notable, so that breadth does not
bury the findings. If a notebook passes about 25 MB, it is split by lens (ADR 0002).

## How the work is done

- **Evidence.** Observations are numbered (U1, B1, M1, ...), quote the numbers above them, and are labelled
  descriptive, observational, causal or projected (ADR 0004). Observation U0 in Stage 1 is the worked example.
- **Visual first.** A chart for each variable or pair, with plain-English labels from `analysis/eda/variables.yaml` and
  its source underneath.
- **Small outputs.** Aggregate in DuckDB; never print raw rows (ADR 0003).
- **Money in real terms.** Money series are shown both as recorded and deflated by the CPI (`abs_prices`), with the base
  stated.
- **Rhythm.** One lens section at a time: run, read the outputs, write the observations, commit. A stage ends with its
  summary, an update to `docs/handover-eda.md` and, for anything that changes a lens, an ADR.
- **Reviewing.** Each stage's notebook is committed with its outputs, so that it can be read on GitHub without running
  anything.

## Leads already found (to confirm in Stage 1)

Found while building the lenses or in the review; not yet findings.

- 264,024 patent rows are provisional applications, which are never granted. They make up 60% of the Australian patent
  records in the regional counts (FY2017–26). FY2026 has 10,069 of them, against 4,143–5,388 a year before. The register
  seems to drop a provisional once a full application supersedes it (N01).
- 79.9% of patent rights have no Australian postcode:
  - 50.3% have an overseas first applicant;
  - 29.5% have no recorded country, almost all filed before 1990;
  - 0.1% are Australian without a postcode.

  Before 1980, "overseas" in the timeline wrongly includes those unknowns (F04).
- "Lapsed" and "ceased" are different. Lapsed rights were never granted or registered: 0.0% of lapsed patents, trade
  marks and designs. Ceased rights were: 99.9% of patents, 100% of trade marks and 92.1% of designs. A lapse is an
  application abandoned; a cessation is a granted right let go.
- Registration dates as early as 1901-01-01, and 1,497 rights (1,493 of them trade marks) registered before they were
  applied for: likely placeholder dates.
- Patent applications per year show no drop-off in the latest years (FY2025: 35,065; FY2026: 41,257), and the counts
  match IP Australia's published 2025 figures. What `application_date` means for PCT filings is still to confirm (N06).
- Several timeline series show decades of zeros between a stray early record and the start of continuous records. For
  example, trade mark oppositions are zero for 777 months, to October 1973 (F38).
- AusTender contract values are added up over every amendment. Summing every notice gives $3.85 trillion, against $0.92
  trillion with one row per contract at its latest value (F33).
- Some postal areas have no residents (population, median age and income of 0), and 295 have fewer than 50 active
  businesses (N03).
- Australia's R&D spending as a share of GDP: the World Bank series ends in 2021 (1.86%); the OECD series, already in
  the corpus, runs to 2023 (1.68%) and differs where they overlap. Researchers end in 2010 (F15, F16).
- Rushes before rule changes:
  - the busiest month for standard patent applications is April 2013 (1,018 from Australian applicants, 5,407 from
    overseas), when the Raising the Bar reforms took effect;
  - second-tier patent applications peak at 2,789 in August 2021, the month innovation patents closed.
- Designs registered begin in January 1970, which looks like a placeholder date.

## After Stage 3

1. Review the early signals and data gaps with the owner.
2. Source additional data for the gaps worth filling (free first; costs proposed with estimates).
3. Only then, design the analyses that answer the five questions: descriptive where that suffices, and natural
   experiments or other designs where additionality is claimed. Heavier tools (for example, time-series foundation
   models) are considered at that point, on evidence that they beat simpler methods on this data.
