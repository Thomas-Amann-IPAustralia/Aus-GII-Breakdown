# EDA plan: getting to know the data before answering the questions

**Status (2026-10-26):** the groundwork is built, an independent review of the data has been done
(`docs/Aus-GII-Independent-Review-and-Action-Plan.md`, whose finding IDs are used below), and the last check before
Stage 1 has repaired the lenses (ADR 0010) and the corpus (ADR 0011). The owner has decided that every dataset goes
through all three stages (ADR 0007). Stage 1 has begun: every core variable of the `rights` lens is profiled
(observations U1 to U16), after five more repairs found on the way (ADR 0012), and so is its first attachment, the
parties (U17 to U21, ADR 0013), and its second, the events: each right's milestones and lifetime (U31 to U40, ADR
0015). Every column of the `timeline` lens is profiled too (U22 to U30), after one more repair (ADR 0014), and every
column of the `firms` lens (U41 to U47), after it switched to counting applications by the filer (ADR 0016), and
every column of the `regions` lens (U48 to U54), after it switched to the filer's postcode and set rules for small
areas (ADR 0017), with its attachments: every value of the Census, Data by Region, CABEE, PHIDU and the Clean Energy
Regulator in a long companion table, `region_indicators`, and AusTender beside the core (U55 to U62, ADR 0018). Every
column of the `national` lens is profiled too (U63 to U72), after it kept WIPO's former states and unknown origins, with
its attachments: every value of the GII 2026, the 24 OECD flows, WIPO's other tables, Measuring What Matters and
Closing the Gap in a long companion table, `national_indicators` (ADR 0019). The `industries` lens is built and
profiled (U73 to U79, ADR 0020): IP by ANZSIC division through the ALP crosswalks, beside CABEE, BERD, the WPI and
BCARR, with every industry table in `industry_indicators`. The `institutions` lens, the last planned, is built and
profiled (U80 to U87, ADR 0021): 130 research institutions by ROR and year, linked to IP RAPID, the ARC and AusTender
through a reviewed list of names and ABNs, with OpenAlex, patent citations, NHMRC grants and patent families, and
the detail in `institution_rights`. The last three `rights` attachments, the links, Google Patents and the
inventors, are built and profiled (U88 to U98, ADR 0022). **Stage 1 is complete:** every lens and attachment has its
profile, summarised in `docs/stage-1-summary.md` (and section 9 of the notebook). This plan says what the exploratory
data analysis (EDA) covers, where each dataset fits, what each part needs before it starts, and which gaps are worth
filling. Decisions are in `docs/adr/` (0002 to 0022); terms are in `GLOSSARY.md`.

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
| `rights` | IP right | Built: 4,368,006 rows, 74 columns | Q1, Q2 |
| `firms` | ABN in any IP, R&D, procurement or tax source | Built: 398,450 rows, 40 columns | Q2, Q3, Q4 |
| `regions` | Postal area | Built: 2,641 rows, 42 columns; its attachments in `region_indicators` (postal area, source, indicator and period: 22,511,923 rows) | Q2, Q4 |
| `national` | Country, year and indicator | Built: 135,597 rows, 11 columns; its attachments in `national_indicators` (place, source, indicator and period: 41,218,170 rows) | Q1, Q4 (context) |
| `timeline` | Month, for Australia (Jan 1904 to Sep 2026) | Built: 1,473 | Q1, Q4, Q5 |
| `industries` | ANZSIC division and financial year | Built: 703 rows (FY1990 to FY2026), 17 columns; its attachments in `industry_indicators` (division, source, indicator and period: 1,409,875 rows) | Q2, Q3, Q4 |
| `institutions` | Australian research institution (ROR) and calendar year | Built: 4,810 rows (130 institutions, 1990 to 2026), 30 columns; its IP in `institution_rights` (right and institution: 31,528 rows) | Q1, Q2, Q3 |

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
| `iprapid` `*_rights`, `application` | rights | The base: one row per right | Done (ADR 0009): A2 (origin), A4 (patent types), raw applicant location; (ADR 0012) attorney use, technology area, placeholder dates, the state. Stage 1 profile done (U1 to U16) |
| `ipa_api` `trade_marks`, `designs`, `patents`, `owners`, `numbers` | rights | IP Australia's live register (its APIs), joined by right and number: a check of IP RAPID (completeness, every field compared on a random sample) and fills for its gaps: trade mark ABNs and ACNs (OQ7), design applicants' countries (OQ14), the register's own expedite events (OQ6) | Done as an audit (ADR 0028, `docs/audit-ipa-api.md`). The fills come from `ipa_register` (below) |
| `ipa_register` `trade_marks`, `designs`, `owners` | rights, firms | Every trade mark and design in IP Australia's register: owners' ABNs and ACNs, owners' countries, the register's expedite events | Done (ADR 0029): filled columns beside IP RAPID's, firms credited by `filer_abn`, the spine takes its ABNs, design shells dropped; U99 to U104 |
| `ipa_provisionals` `provisionals`, `inventors`, `applicants`, `gap_probe` | rights | Every provisional in the register, with its inventors and their estimated gender | Done (ADR 0029): four `register_inventors*` columns in `rights`; U105 to U107 |
| `iprapid/events` | rights, timeline | **Per right:** the dates of the examination request, acceptance, grant, opposition, assignments, licences and extension of term, and of the lapse, cessation or expiry, giving each right's lifetime. **Per month:** counts (already built). | Done (ADR 0010): A3 (coverage starts and ends), events labelled as events and counted once (F38), trade mark registrations by the date entered; (ADR 0014) starts past partial and batch-dated records. Timeline profile done (U22 to U30). Done for `rights` (ADR 0015, U31 to U40): B5, milestones and lifetimes, with rights still in force counted as unfinished |
| `iprapid/party` | rights, firms | Applicants by country, all of them rather than only the first; founding filer against current holder; the attorney firm. Individuals are pseudonymised codes in IP RAPID, so their gender cannot be estimated. | Done for `rights` (ADR 0013, U17 to U21): founding applicant, holder changed (not before FY2003 for patents), agent, representation. `firms` (ADR 0016) and `regions` (ADR 0017) count by the filer |
| `iprapid/links` | rights | The route into Australia: foreign priority claimed, PCT entry, divisional | Done (ADR 0022, U88 to U91): `filing_route` and 7 more; a patent priority's office read from its number (PCT numbers are labelled `au`); the PCT route checked against WIPO |
| `iprapid/classification`, `concordances` | rights, industries | Technology fields and the green-technology flag per right; industry shares for `industries` | Done (ADR 0020): B6 (26 IPC predecessors; unknown subclass marks 0.48% to 0.003%); Nice classes padded; ISIC to ANZSIC no longer split over partial links (a corpus repair). Profiled (U74, U75) |
| `iprapid/applicant_year`, `iplord` | firms | Filing histories per ABN. IPLORD is used only to check `applicant_year` before 2020, never added to it. | Checked (U41, ADR 0016): IPLORD's counts differ (81.02% of shared ABNs agree); `in_iplord` flags the 50,790 ABNs only it links to IP |
| `iprapid/description` | text | Titles and goods and services descriptions; variables derived only if wanted | — |
| `linkage/abn_spine`, `abr`, `asic` | firms, regions | Firm attributes; business counts by postal area and entity type | Done (ADR 0010, 0011): A6 (age basis and truncation); B2 (every applicant's ABN) |
| `rdti` | firms, regions | R&D claims per ABN and year | Done: A5 (latest report, amended); ABNs from ACNs (ADR 0011). In `regions` as claimants per postal area (U54) |
| `ato_ctt` | firms | Income and tax of large entities | Done: latest report per year |
| `austender` | firms, regions, timeline | Contracts and their value per ABN (one row per contract), per supplier postal area, per month | Done (ADR 0011): A1, with amendments in order. Limit: amendments from September 2019 to April 2023 to contracts published before July 2019 are missing. In `regions` (ADR 0018, U62): suppliers, contracts and value FY2017 to FY2026 by the supplier's postcode |
| `abs_census` (14 tables) | regions | Every table, as shares of its total: education, occupation, industry, labour force, health, care, volunteering, mobility | Done (ADR 0018, U57): every cell of the 14 tables in `region_indicators`, by postal area; perturbed, so parts do not add exactly to totals. Shares are made in Stage 2, against each table's own universe |
| `abs_regions` (Data by Region, SEIFA, geography) | regions | Regional indicators through SA2-to-postal-area population weights; SEIFA (built); geography as reference | Done (ADR 0018, U58): every SA2 item, 2011 to 2025, split to postal areas by 2021 residents (mesh blocks) in `region_indicators`; SEIFA and geography in `regions` (ADR 0017: SA3 for pooling) |
| `abs_cabee` | regions, industries, national | Businesses by employment and turnover size; entries, exits and survival | Survival rates by size repaired (ADR 0011). SA2 tables in `region_indicators` (ADR 0018, U59), split by residents; the other cubes and the national tables by division in `industries` and `industry_indicators`, its other national tables in `national_indicators` (ADR 0020, U77, U79) |
| `phidu` | regions | Health and social indicators through a concordance from PHIDU's areas (PHAs) to SA2s and postal areas | Done (ADR 0011): B12 (`phidu/pha_sa2`), sub-indicators and area types. In `region_indicators` (ADR 0018, U60), without its confidence limits |
| `cer` | regions, timeline | Solar, battery and other small-scale installations per postal area, and nationally per month | Done (ADR 0011): B11 (one format, one row per key). In `region_indicators` by year (ADR 0018, U61); the monthly national series waits for the `timeline` |
| `abs_bcs` | industries | Innovation, barriers, finance and IP methods by industry and firm size (aggregate) | Done (ADR 0020, U79): every table in `industry_indicators`, with the ABS's flags (36.2% flagged, 25% withheld) |
| `abs_rd_vc` | industries, national | Business R&D by industry; R&D by sector; venture capital to 2019 | Done (ADR 0011): B10 (every cell, units, sheet rows). BERD by division in `industries`, by subdivision in `industry_indicators`, the rest in `national_indicators` (ADR 0020, U78) |
| `bcarr_creative` | industries, national | Cultural and creative activity by industry and domain | Done (ADR 0020, U78, U79): value added by division in `industries` (newer release), both releases by industry in `industry_indicators` and by domain in `national_indicators`, never spliced |
| `abs_labour` (added 2026-10-25) | timeline, national | The Labour Force Survey: employment, unemployment and participation by sex and state, monthly from 1978; owner-managers and employees by sex, monthly from 1991 (the denominator for who runs businesses) | — |
| `abs_prices` (added 2026-10-25) | timeline, industries | CPI (quarterly from 1948), living costs by household type, wages (also by industry) and property prices: background, and the deflator for every money series (fees, R&D, contracts, medicine costs) | Quarterly CPI attached to the timeline (ADR 0010); the WPI by industry in `industries` and `industry_indicators` (ADR 0020) |
| `wdi`, `wipo_ipstats`, `gii`, `oecd`, `mwm`, `ctg` | national | Country-year indicators: every OECD flow (one indicator per named breakdown); GII 2026; WIPO's filings at IP Australia by origin country, 1980–2024 (an independent view of which nations use the system); Australian annual series (Measuring What Matters, Closing the Gap) | Done (ADR 0010, 0011): F02 and F15 (A8: trade marks, OECD R&D); F01 (B10: IP tax regimes' values). Done (ADR 0019, U63 to U72): former states and unknown origins kept; every value of the GII, the OECD flows, WIPO's other tables, Measuring What Matters and Closing the Gap in `national_indicators`; Closing the Gap's "Aus Gov" and Measuring What Matters' stacked tables repaired. Compare WIPO by country from 1995 (U64) |
| `pbs` | timeline; medicines | Prescriptions, and government and patient costs, per month. Items are linked to ingredients for the medicine strand. | B9 (Section 100) |
| `tga` | own unit | ARTG entries; sponsors per ingredient (competition); joins PBS and extension-of-term patents by ingredient | — |
| `fedcourt` | timeline; text | IP judgments per month by right; variables derived from the text later | — |
| `google_patents`, `google_patents_inventors` | rights, firms, institutions | Per Australian application: family size, offices, US grant, forward citations (with a follow-up flag); inventors by country and their estimated gender (expected counts, from `wgnd`) | B4. In `institutions` (ADR 0021, U85): the families of the institutions' Australian applications. Done for `rights` (ADR 0022, U92 to U98): family reach, US grant and citations (five-year count only where complete); inventors' countries and expected women and men, the gender estimates checked against WIPO's shares (levels for inventors in Australia only). Left: F07 |
| `openalex`, `openalex_works`, `reliance_on_science` | institutions, rights | Output, citations and patent-cited works per institution; science cited by Australian-linked patent families | Done for `institutions` (ADR 0021, U82, U85): works and citations from 2010, US patent citations by publication year. F37 test still to do |
| `arc_grants`, `nhmrc_grants` | institutions, timeline | Grants and funding per institution and year (ARC names matched to ROR) | Done (ADR 0021, U83): ARC by the year funding starts, NHMRC by round (F41), names matched to ROR; industry-partner schemes apart |
| `ror` (added 2026-10-26) | institutions | Every Australian ROR record, with names, aliases and relationships: the lens's key | Done (ADR 0021): from ROR's data dump |
| `policy_events` | timeline | Policy changes per month; the policy register is reference | Done (ADR 0011): B7 (every date checked against the Federal Register); (ADR 0014) the 1995 term change added: 17 events. Profiled one at a time (U28) |
| `ipa_fees` | timeline, rights | The fee in force each month, and fees per right, once the fee history exists | R3 |
| `wgnd` | reference | The name-gender dictionary behind `google_patents_inventors` | — |
| `evidence`, `wine_gi` | reference | The literature register; the GI list (for certification marks) | — |

## The order of work

Stage 1 goes lens by lens. A lens's section can start with its core variables; each attachment adds a sub-section when
it is built. Each lens's repairs come first.

1. **`rights`** (repairs done, ADR 0009, 0010 and 0012: A2, A4, the raw applicant location, the earliest filing date,
   attorney use unknown for provisionals and excluding the applicant itself, the technology area for patents only,
   placeholder dates, the state from the postcode). **Core variables profiled (U1 to U16); the parties attached and
   profiled (B1, ADR 0013, U17 to U21); the events attached and profiled (B5, ADR 0015, U31 to U40); the links,
   Google Patents (B4) and the inventors attached and profiled (ADR 0022, U88 to U98).** Every attachment is done.
2. **`timeline`** (repairs done, ADR 0010: A3 at both ends, events counted once, trade mark registrations by the date
   entered, the policy dates (B7), the quarterly CPI; ADR 0014: 15 series start where their records are complete, and
   the 1995 term change). **Every column profiled (U22 to U30).** Later attachments, each a sub-section of section 5:
   wages and the Labour Force Survey, PBS (B9), CER, judgments, contracts, and fees once the fee history exists (R3).
3. **`firms`** (repairs done, ADR 0010 and 0011: A1, A5, A6, B2; ADR 0016: applications by the filer's ABN, holdings,
   the IPLORD flag, blank states). **Every column profiled (U41 to U47).** Its attachments (filing histories by year
   from `applicant_year`, firms' rights' lifetimes) come as sub-sections when built.
4. **`regions`** (ADR 0017: applications by the filer's postcode, organisations' counts, rates a year per person and
   per business shown only where 10 or more applications would be expected, SA3s for pooling, the postcode check S6).
   **Every column profiled (U48 to U54); every attachment built and profiled (ADR 0018, U55 to U62):** the Census,
   Data by Region, CABEE, PHIDU and the CER in `region_indicators`, AusTender in `regions`. Left for later: the ATO's
   statistics by postcode (an addition), and a lookup that places the postcodes that are not postal areas, if Stage 2
   proves sensitive to them (U49).
5. **`national`** (A8 done, ADR 0010; ADR 0019: former states and unknown origins kept, `entity`). **Every column
   profiled (U63 to U67); every attachment built and profiled (U68 to U72):** the GII 2026, the 24 OECD flows (the
   tax regimes' values kept, suppressed values emptied), WIPO's other tables, Measuring What Matters and Closing the
   Gap in `national_indicators`. The national tables of `abs_rd_vc`, `bcarr_creative` and CABEE join with `industries`.
6. **`industries`** (ADR 0020: B6, Nice padding, the ISIC-to-ANZSIC repair). **Every column profiled (U73 to U78);
   every attachment built and profiled (U79):** CABEE, the BCS, BERD, BCARR, the WPI and IP by subdivision in
   `industry_indicators`; the same releases' Australia-wide tables in `national_indicators`. Patents reach only
   goods-producing industries (the crosswalk excludes services, U75).
7. **`institutions`** (ADR 0021: the `ror` source; a reviewed link of 130 institutions, 116 names and 146 ABNs in
   `analysis/eda/institutions/`; IP by the filer, with commercialisation companies). **Every column profiled (U80 to
   U87)**, with `institution_rights` and the follow-up to U49 (half the universities' patents carry a postcode that
   is not a postal area). Whether someone who knows the sector should review the link is OQ11.

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

   It would also check the provisional rise (U8); N01 itself is settled.

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
    "supplementary", beside the official release. U69 confirms six: the pupil-teacher ratio, researchers per million
    people, microfinance loans, GERD financed by business, research talent in businesses and utility models by origin.
13. **OpenAlex.** Test whether the "cited at least once" filter drops works that patents cite (F37); re-harvest if it
    matters.
14. **Google Patents.** Size how many Australian families filed only abroad are missed, against WIPO's counts by origin
    (F07). WIPO's patent families by origin (indicator 6a) would do it; the loader takes another indicator in minutes
    (ADR 0022 added three).

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

Found while building the lenses or in the review. Those confirmed in Stage 1 name their observation in
`01_univariate.ipynb`.

- 264,024 patent rows are provisional applications, which are never granted. They make up 60% of the Australian patent
  records in the regional counts (FY2017–26). FY2026 has 10,069 of them, against 4,143–5,047 a year in FY2022–FY2025.
  The register does not drop a provisional once a full application claims it (N01, refuted in ADR 0010 and confirmed by the owner: 99.9% to 100%
  of claimed provisionals are present in every year from 2000); the jump is real, from more applicants (5,165 against
  3,361) and above all individuals (5,399 provisionals against 1,926). Why is the lead. **Confirmed in Stage 1 (U8):**
  it starts in early 2025, peaks in March and April 2026 and eases by September 2026; distinct ABNs are flat, and it
  is both broad (single-filing individuals 1,538 to 2,507) and concentrated (54 individuals filed 10 or more each).
- 79.9% of patent rights have no Australian postcode:
  - 50.3% have an overseas first applicant;
  - 29.5% have no recorded country, almost all filed before 1990;
  - 0.1% are Australian without a postcode.

  Fixed (ADR 0009): the unknowns are now "origin unknown" in every lens, not overseas (F04).
- 50,711 patents and 11,143 designs have no application date, so the timeline cannot place them. Almost all are of
  unknown origin (50,444 and 11,126), and only 203 and 15 were ever registered. **Confirmed (U3).**
- "Lapsed" and "ceased" are different. Lapsed rights were never granted or registered: 0.0% of lapsed patents, trade
  marks and designs. Ceased rights were: 99.9% of patents, 100% of trade marks and 92.1% of designs. A lapse is an
  application abandoned; a cessation is a granted right let go. **Confirmed (U9).**
- Registration dates as early as 1901-01-01, and 1,497 rights (1,493 of them trade marks) registered before they were
  applied for: likely placeholder dates. **Fixed (ADR 0012, U2 and U11):** the 1901 date is emptied; most of the 1,497
  were trade marks registered before 1986, whose registration date is their filing date, and 57 negative times
  remain.
- Patent applications per year show no drop-off in the latest years (FY2025: 35,065; FY2026: 41,257), and the counts
  match IP Australia's published 2025 figures. That is because, for a PCT filing, `application_date` is the date it
  entered Australia's national phase, about 30 months after priority (N06, answered in ADR 0010 and confirmed by the owner);
  `earliest_filed_date` is the international filing date. **Confirmed (U6)** for every type of right.
- Fixed (ADR 0010): several timeline series showed decades of zeros between a stray early record and the start of
  continuous records (trade mark oppositions read 0 for 777 months, to October 1973; F38), and some ended on a cliff
  because the register records them late (trade mark cessations, 0 from May 2026). Trade mark registrations were
  counted at their filing date, which is their legal registration date; they are now counted by the date each was
  entered, from January 1986, when IP RAPID starts recording it.
- Fixed (ADR 0011): AusTender contract values were added up over every amendment. Summing every notice gives $7.59
  trillion, against $1.26 trillion with one row per contract at its latest value (F33). The bulk file's contracts
  still running when it closed now have their later amendments (asked for by id), and 70 values that look keyed in
  the wrong units are flagged (`value_jump`).
- Some postal areas have no residents (population, median age and income of 0), and 295 have fewer than 50 active
  businesses (N03). **Confirmed in Stage 1 (U50, U53):** 818 areas have fewer than 1,000 people (1.33% of people);
  rates are now shown only where 10 or more applications would be expected (ADR 0017), and areas differ far more than
  chance would make them (68.2% to 72.5% fall below the funnel's 95% limits), so Stage 2 needs models with room for
  that spread.
- Australia's R&D spending as a share of GDP: the World Bank series ends in 2021 (1.86%); the OECD series, now in the
  national lens beside it, runs to 2023 (1.68%) and differs where they overlap (2021: 1.66%). Researchers end in 2010
  (F15, F16). **Confirmed in Stage 1 (U63, U65):** technicians end in 2008; GERD peaked at 2.24% in 2008, and business
  R&D (0.91% in 2023) is 26th of 35 OECD members.
- Rushes before rule changes:
  - the busiest month for standard patent applications is April 2013 (1,018 from Australian applicants, 5,407 from
    overseas), when the Raising the Bar reforms took effect;
  - second-tier patent applications peak at 2,789 in August 2021, the month innovation patents closed.

  **Confirmed in Stage 1 (U28):** 4.39 and 2.66 times the year before's average month, and 4.31 times; with steps (the
  1995 term change, the 1999 extension regime, the innovation patent's introduction, the Designs Act 2003) and pauses
  at commencement (the Patents Act 1990 and the Trade Marks Act 1995) as the other candidates for Stage 2.
- Three design registrations are dated 1 January 1970, a placeholder date. The series now starts in June 1973, where
  its records become continuous (ADR 0010). **Superseded (ADR 0014, U23):** design registrations start in January
  1988, and trade mark, design and provisional applications where IP RAPID stops holding only survivors.

## After Stage 3

1. Review the early signals and data gaps with the owner.
2. Source additional data for the gaps worth filling (free first; costs proposed with estimates).
3. Only then, design the analyses that answer the five questions: descriptive where that suffices, and natural
   experiments or other designs where additionality is claimed. Heavier tools (for example, time-series foundation
   models) are considered at that point, on evidence that they beat simpler methods on this data.
