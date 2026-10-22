# Data plan: from a correlation explorer to a research corpus

Status: proposal for review (2026-10-22). Nothing has been deleted or ingested yet.

This note assesses the data now in the repository against the five core questions in `docs/research-goal.md`, flags
what adds little or nothing, and proposes the datasets to ingest instead. Availability was checked from this
environment on 2026-10-22: "programmatic" means a script here reached the source and can fetch it unattended.

## The short version

- **The current corpus is national and cross-country; the questions are about businesses, people and places.** Of
  the 2,663 measures in the repo, perhaps 30 bear on the IP system at all, and none can say who benefits, what
  determines value or what an intervention would add. The data can support one thing well: a benchmarking chapter
  ("Australia in context") built from the GII and a short, targeted cross-country panel.
- **The correlation explorer amplifies the problem.** Testing 2,442 Australian time series (most of them trending
  together over the same 15 to 60 years) against each other is a search for spurious correlations, however carefully
  the statistics are corrected. It has no route to the research goal's principles of additionality and distribution.
- **The data that can answer the questions is mostly public, ABN-linked and fetchable.** IP Australia's own IPGOD and
  IPLORD (application-level and applicant-level IP data with ABNs and postcodes) joined to the public business
  registers (ABR, ASIC), the ATO's R&D Tax Incentive transparency data, ABS business innovation and business counts,
  and SEIFA give a firm- and region-level spine for questions 1 to 4.
- **Question 5, and any causal claim, needs data that cannot sit in a repo.** ABS BLADE (via DataLab), and
  IP Australia's internal examination records, are the only routes to credible estimates of additionality. They need
  an institutional request, not a download; the plan below sets up the public spine so that a request is specific.

## 1. What the current data can and cannot do

| Question | What the current data supports | What it cannot do |
|---|---|---|
| Q1 Public value | National IP activity over time (WDI patent, trade mark and design filings; IP royalty receipts and payments: in the latest year Australia paid about US$12.4 billion for the use of IP and received about US$7.4 billion); the GII's IP indicators across 139 economies | Any link from rights to outcomes; costs of obtaining, maintaining or enforcing rights; costs to consumers or follow-on innovators |
| Q2 Who benefits | Nothing on IP users. Closing the Gap, HDR and the gender gap profile describe population outcomes, not use of the IP system | Businesses, industries, regions, firm size or age, gender or First Nations participation in the IP system |
| Q3 What determines value | Nothing at the level needed (firms) | Complementary capabilities, finance, procurement, alternatives to registration |
| Q4 Opportunities | The GII's strengths and weaknesses give national-level gaps (for example knowledge diffusion and research commercialisation) as hypotheses to test | Barriers, or which of them IP Australia could influence |
| Q5 Outcomes of interventions | Nothing | Magnitudes, additionality, costs, sensitivity |

### Dataset by dataset

| Dataset (in `data/raw/`) | Verdict | Why |
|---|---|---|
| WIPO GII 2026 data file and Appendix III | **Keep, as context** | The best single benchmark of Australia's position, and a source of hypotheses (Q4). One year only, and a composite, so it supports description, not inference |
| World Bank WDI, Australia only (1,002 indicators) | **Replace** | About 25 indicators matter (IP filings, royalties, R&D, researchers, high-tech exports, firm entry). Australia alone gives one short series per indicator. Replace with those indicators for a comparator panel (OECD members) from the WDI API |
| UNDP HDR (annex, series, country file) | **Drop** | National human development changes slowly and has no identifiable pathway from the IP system at this resolution. The country file duplicates the series |
| OECD How's Life? (15 series, Australia) | **Drop** | As above; 15 national wellbeing series cannot be tied to IP policy |
| World Happiness Report (`.xlsx` and the loose `.csv`) | **Drop** | Life evaluation across countries is dominated by income and social support; no link to IP can be identified. The CSV duplicates the xlsx |
| Productivity Commission Closing the Gap (17 files, 1,381 national series) | **Drop from the corpus** (keep a pointer) | The outcomes are health, justice, housing and education. First Nations participation in the IP system needs First Nations business and IP-use data (Tier 3 below), not these |
| WJP Rule of Law Index 2026 | **Drop** (or keep two factors as context) | Australia is stable and near the top; only the civil-justice factors touch enforcement costs, and only at national level |
| Yale EPI 2026 | **Drop** | No pathway to the IP system. Environmental public value is better measured through green patenting (IPC Green Inventory, below) |
| SDR 2026 and Global Gender Gap 2026 profiles (PDFs) | **Drop** | One-year narrative profiles; nothing to analyse |
| `docs/Data-Analysis-DEMO.html` | **Delete** | Empty (2 bytes) |
| The explorer, its 2,442-series build and `config/lenses.yaml` | **Retire** | See above. The engineering principles (source register, SHA-256 manifest, deterministic build that fails loudly) are worth keeping for the new corpus |

## 2. Proposed additions

Tier 1 is the spine: all public, all programmatic, and between them they answer most of Q1 to Q4 descriptively.
Tier 2 adds complements, outcomes and comparators. Tier 3 needs your help or an institutional request.

### Tier 1: the spine (programmatic, open licence)

| # | Dataset | Publisher | What it adds | Questions | Size | Licence |
|---|---|---|---|---|---|---|
| 1 | **IPGOD 2022** (patents, trade marks, designs, PBR: applications, parties, classifications, events, citations, attorneys, oppositions, pharmaceutical extensions of term) | IP Australia, data.gov.au | Every Australian IP right since 1904 with its life history: filing, examination, grant, renewal, lapse, opposition. Renewals and lapses reveal the private value holders place on rights; attorney fields show who self-files; extensions of term are the pharmaceutical cost case | Q1, Q2, Q3, Q4 | ~2.5 GB raw (843 MB zip) | CC BY 2.5 AU |
| 2 | **IPLORD 2020** | IP Australia | Applicant by financial year panel, with **ABN** where available, postcode, state, first-filing year by right type, portfolio counts, technology and Nice class areas. The join key to everything else | Q2, Q3 | 1.7 GB | CC BY 4.0 |
| 3 | **ABN Bulk Extract** | Australian Business Register | Every ABN: entity type (company, sole trader, trust, partnership, government, charity), ABN start and cancellation dates, GST registration (a turnover of $75,000+ proxy), location. Gives firm age at first filing, survival, entity type and a size proxy for IP users and non-users alike | Q2, Q3 | ~1 GB zipped | CC BY 3.0 AU |
| 4 | **ASIC Company Dataset** | ASIC | Company registration and deregistration dates, type and class; cross-checks ABR survival and identifies public companies | Q2, Q3 | 400 MB | CC BY 3.0 AU |
| 5 | **R&D Tax Incentive transparency reports** (2021-22 to 2023-24) | ATO | Name, ABN and R&D expenditure for every R&DTI claimant. Joined to IPLORD: firms that invest in R&D but never use the IP system, and the reverse (Q3 alternatives, Q4 "missing filers") | Q3, Q4 | ~2 MB | CC BY 3.0 AU |
| 6 | **ABS Business Characteristics Survey: innovation, barriers, commercialisation** (`BCS_INN`, `BCS_INNACT`, `BCS_INNSIG`, `ABS_IT_BARRIER`, `ABS_IT_INNOVATION`, `ABS_IT_FINANCE`) | ABS Data API | Innovation activity, methods of protection (formal and informal), barriers to innovation, finance, collaboration, by firm size and industry. The only national measure of innovation that is not IP | Q1, Q3, Q4 | small | CC BY 4.0 |
| 7 | **Counts of Australian Businesses** (entries, exits, by industry, size and SA2) | ABS | Denominators: IP users per 1,000 businesses by industry, size and region, and the comparison population for non-users | Q2, Q4 | ~50 MB | CC BY 4.0 |
| 8 | **SEIFA 2021 by postal area and SA2**, **Data by Region** (ASGS 2021 and remoteness), **ASGS postcode and SA2 correspondences** | ABS Data API | Places IP users in socio-economic and remoteness context; regional innovation potential (education, occupation, industry mix) | Q2, Q4 | ~100 MB | CC BY 4.0 |
| 9 | **Concordances**: WIPO IPC to 35 technology fields; IPC to industry (Algorithmic Links with Probabilities, ISIC and ANZSIC); Nice class to industry; WIPO IPC Green Inventory | WIPO, academic (Lybbert and Zolas), ABS | Turn patent and trade mark classes into industries and green technologies (environmental public value) | Q1, Q2 | < 10 MB | open |
| 10 | **World Gender-Name Dictionary 2.0** | WIPO, Harvard Dataverse | Infers inventor and individual applicant gender from names, the established method (WIPO, IP Australia's own past reports) | Q2 | ~50 MB | CC BY 4.0 |

### Tier 2: complements, outcomes and comparators (programmatic)

| # | Dataset | Publisher | What it adds | Questions |
|---|---|---|---|---|
| 11 | **AusTender contract notices** (OCDS API, supplier ABN) | Department of Finance | Does holding registered IP change access to government procurement? | Q3 |
| 12 | **ARC grants** (NCGP API) and **NHMRC grant outcomes** | ARC, NHMRC | Public research funding by institution and field; links research investment to later institutional patenting (Q3 "public funding" alternative) | Q2, Q3 |
| 13 | **ATO Corporate Tax Transparency** (2017-18 to 2024-25) | ATO | Total income and tax for entities with $100 million+ income, by ABN: outcomes for large IP holders | Q1, Q2 |
| 14 | **OECD**: MSTI (R&D), patents by technology and co-invention, business demography, IP royalty trade (SDMX API) | OECD | A focused comparator panel replacing the WDI dump | Q1, Q4 |
| 15 | **WDI comparator panel** (about 25 indicators, OECD members, API) | World Bank | As above | Q1 |
| 16 | **WIPO IP Statistics**: filings abroad by origin (PCT, Madrid, Hague) | WIPO | Do Australian firms take rights to international markets, and how does that compare with peers? | Q3 |
| 17 | **TM-Link** | IP Australia | Trade marks linked across offices: which Australian owners file abroad and where | Q3 |
| 18 | **IP Australia fee schedules**, current and historical | IP Australia | Direct costs of obtaining and maintaining rights, to set against revealed value from renewals | Q1, Q5 |
| 19 | **PBS expenditure and prescriptions** with IPGOD extensions of term | Department of Health, Disability and Ageing | A concrete consumer-cost case: spending on medicines under extended patent terms | Q1 |
| 20 | **ABS R&D surveys** (business, higher education, government) and **venture capital** (5678.0) | ABS | National and industry R&D and VC context | Q3, Q4 |
| 21 | **OpenAlex** (Australian institutions' research output) | OurResearch | Research capacity by institution and field, to compare with patenting (commercialisation gap) | Q2, Q4 |
| 22 | **An evidence register** of key literature and evaluations (PC Intellectual Property Arrangements 2016; IP Australia economic research papers; OECD; UK IPO, EUIPO SME Fund and other IP-support evaluations) | various | Q1's "what can existing evidence establish", and priors for Q5 where Australian data cannot give magnitudes | Q1, Q5 |

### Tier 3: needs your help or an institutional request

Listed in order of value. Items marked "you" are the limited fetches you offered; the rest are requests to others.

| # | Dataset | Why it matters | How |
|---|---|---|---|
| A | **A current IPGOD and IPLORD extract (2021 to 2025)** | The public releases stop at 2021 (IPGOD 2022) and 2020 (IPLORD). Four to five missing years cover COVID, the end of the innovation patent and the current period | You, internally (IP Australia's data team). The single most valuable fetch |
| B | **ABS BLADE with IP Australia's linked IP data** (DataLab) | The only source of firm outcomes (turnover, employment, wages, productivity, exports, survival) for IP users and matched non-users. Needed for any Q1, Q3 or Q5 claim beyond description | Institutional project application; analysis happens inside DataLab, so nothing is stored here except cleared outputs |
| C | **Examination records with examiner assignment** (internal) | Enables the strongest causal design in the literature (examiner leniency as an instrument for grant, as in Farre-Mensa, Hegde and Ljungqvist 2020): what a granted patent adds for a startup, compared with a rejected one | Internal request; analysis likely inside IP Australia or DataLab |
| D | **IP Australia customer and SME research** (surveys of users and non-users, awareness, barriers) | Q2 and Q4 barriers from the users' side | You, internally, if the reports and microdata can be shared |
| E | **Global patent data**: Google Patents Public Data (BigQuery) or PatentsView | Forward citations and patent families as value measures; Australian inventors abroad | BigQuery needs a GCP project (the `bq` CLI here has no credentials); PatentsView is blocked by this environment's network policy and needs an allowlist change |
| F | **The Lens API token** (free for research) | Patent to scholarly-literature links: knowledge diffusion from research | You, a free registration |
| G | **ABS TableBuilder: Census 2021 owner-managers** by sex, Indigenous status, industry and region | Who runs businesses, the denominator for gender and First Nations participation | You, a free registration and a few tables |
| H | **First Nations business data** (Indigenous Business Sector Snapshot; Indigenous Procurement Policy outcomes) | Q2 for First Nations businesses, replacing Closing the Gap | Mixed: some public reports, some by request |
| I | **Venture capital deal data** (Dealroom, Cut Through Venture, Crunchbase) | Does registration change access to investment (Q3)? | Paid; only if IP Australia already subscribes |

## 3. What the corpus would let later sessions answer

Each line is a descriptive or observational analysis that the Tier 1 and 2 data support; the evidence level is noted
as the research goal requires.

- **Q1 Value.** Revealed private value of patents and designs from renewal and lapse decisions, by applicant type,
  technology and origin (observational, an established method). Share of Australian rights, renewals and royalty
  flows held by foreign versus domestic owners (descriptive). Direct costs against revealed value (descriptive).
  Pharmaceutical extension-of-term spending (descriptive case study). Green patenting share (descriptive).
- **Q2 Distribution.** IP use per business by industry, firm age, entity type, size proxy, remoteness and SEIFA
  decile; gender of inventors and individual applicants; self-filers against attorney filers (descriptive).
- **Q3 Conditions.** Survival and growth proxies (ABR, ASIC, GST status) for first-time filers against matched
  non-filers; R&D performers that do and do not register; IP holders' share of government contracts; international
  filing by firm type; formal against informal protection from BCS (observational).
- **Q4 Opportunities.** "Missing filers" (R&D performers, grant recipients and procurement suppliers that never use
  the system); regions with high innovation potential and low use; abandonment and opposition outcomes for
  self-filers; barriers by firm size from BCS (descriptive, hypothesis-generating).
- **Q5 Interventions.** Needs Tier 3 B or C for credible additionality. Until then: evidence register priors and
  scenario ranges built from the Q2 to Q4 populations (projection, clearly labelled).

## 4. Storage

GitHub refuses files over 100 MB and slows badly beyond a few GB, so:

- **R2 holds the large raw files** (IPGOD, IPLORD, ABR, ASIC, TM-Link: roughly 8 to 15 GB uncompressed), each
  recorded in the source register with its URL, retrieval date, SHA-256 and R2 key, with a script to re-fetch from
  the publisher or from R2.
- **The repo holds small raw files** (ABS, ATO, concordances, fees) and **analysis-ready Parquet extracts** of the large
  ones (for example Australian applicants only, with the columns the questions need), each under 50 MB.
- R2 credentials are present in this environment (`R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`); the
  bucket name is still needed.

## 5. Proposed repository shape

```
docs/            research-goal.md, data-plan.md, a question map (question to dataset to analysis), the evidence register
config/          sources.yaml (the source register, extended with R2 keys and retrieval dates)
data/raw/        small raw files, by publisher
data/processed/  Parquet extracts and the join tables (ABN, postcode to SA2, class to industry)
data/manifest    SHA-256 of every raw and processed file, local or in R2
src/corpus/      one ingest module per source, plus the shared linkage (ABN, geography, classification)
tests/           schema and row-count checks per source; a rebuild check
```

The current pages, explorer and their build would be removed from `main` (they stay in the git history).
