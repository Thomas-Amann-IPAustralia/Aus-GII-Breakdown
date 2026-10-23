# Data plan: from a correlation explorer to a research corpus

Status: approved 2026-10-22 (Tiers 1 and 2), and ingested the same day; see section 8 for what is in the corpus,
what could not be fetched, and what needs your help. Decisions: public data only (no ABS integrated data assets such as
BLADE, no internal IP Australia data); keep the GII page (to be rebuilt) and `docs/Data-Analysis-DEMO.html`; large files in the R2 bucket `ipholmes`.

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
- **Public value is not only financial.** Health, environment, culture, consumer trust, knowledge, opportunity and
  wellbeing are in scope (section 2). National wellbeing series cannot show the IP system's contribution on their own,
  so the plan traces each non-financial benefit through the pathway by which IP could plausibly affect it, and keeps
  a small, curated set of wellbeing measures (led by the Australian Government's Measuring What Matters framework) as
  the outcome layer and for valuation, rather than as variables to correlate.
- **Question 5, and any causal claim, needs designs the public data only partly support.** The corpus uses public data
  only, so the routes to credible additionality are natural experiments in IP Australia's own levers
  (`policy_events`, with IP RAPID's full application histories), comparisons across the thresholds those changes
  created, and priors from the evidence register. Firm outcomes come from the public registers only: survival (ABR, ASIC), a size marker (GST),
  R&D (the R&D Tax Incentive), procurement (AusTender) and large firms' income (corporate tax transparency).

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
| UNDP HDR (annex, series, country file) | **Drop** | Its domains (health, education, living standards) are covered for Australia, in more detail and with an official status, by Measuring What Matters (section 2). The country file duplicates the series |
| OECD How's Life? (15 series, Australia) | **Replace, as part of the outcome layer** | Keep the wellbeing domains, but re-pull How's Life? for comparator countries (OECD API) beside Measuring What Matters for Australia. Used to frame and value outcomes (section 2), not to correlate with IP measures |
| World Happiness Report (`.xlsx` and the loose `.csv`) | **Drop** | Life evaluation matters, but cross-country differences are driven mostly by income, health and social support, and the IP system's share cannot be identified from them. Life satisfaction enters instead through wellbeing valuation (section 2). The CSV duplicates the xlsx |
| Productivity Commission Closing the Gap (17 files, 1,381 national series) | **Keep three targets as context** (8 economic participation, 15 land and waters, 16 cultures and languages); drop the rest | These are the targets a First Nations workstream on Indigenous Knowledge and cultural and intellectual property would sit against. They describe the context, not the IP system's effect; First Nations participation in the IP system itself needs Tier 3 data |
| WJP Rule of Law Index 2026 | **Drop** (or keep two factors as context) | Australia is stable and near the top; only the civil-justice factors touch enforcement costs, and only at national level |
| Yale EPI 2026 | **Drop** | No pathway to the IP system. Environmental public value is better measured through green patenting (IPC Green Inventory, below) |
| SDR 2026 and Global Gender Gap 2026 profiles (PDFs) | **Drop** | One-year narrative profiles; nothing to analyse |
| `docs/Data-Analysis-DEMO.html` | **Delete** | Empty (2 bytes) |
| The explorer, its 2,442-series build and `config/lenses.yaml` | **Retire** | See above. The engineering principles (source register, SHA-256 manifest, deterministic build that fails loudly) are worth keeping for the new corpus |

## 2. Public value beyond financial returns

The research goal defines public value as "net effects on economic prosperity, social progress, opportunity,
environmental sustainability, competition and public welfare", and Q1 asks about "economic, social, technological and
environmental outcomes". The first version of this plan leaned towards financial and economic measures. This section
corrects that.

**Why the wellbeing datasets still cannot be the main evidence.** A national happiness or social cohesion series moves
with income, housing, health, migration and many other forces. The IP system is a small, indirect influence on it, so a
correlation between the two (over 15 years for one country, or across countries that differ in everything) cannot
separate the IP system's contribution from everything else. That is a problem of attribution, not a judgement that
non-financial value matters less.

**What the plan does instead.** It traces each non-financial benefit (and cost) through the specific pathway by which
the IP system could affect it, measuring at the level where that pathway is visible, and then links the pathway to
wellbeing using established evidence:

| Domain (Measuring What Matters theme) | How the IP system could add or subtract value | Measurable with |
|---|---|---|
| Health (healthy) | Incentives to develop and bring medicines and devices to Australia; against that, higher prices and delayed generic entry during patent terms and extensions | IP RAPID pharmaceutical extensions of term; PBS spending; TGA's register of therapeutic goods (sponsors per active ingredient, a snapshot without dates) |
| Environment (sustainable) | Green technology invention, disclosure and diffusion; whether patents speed or slow uptake | Green patents (IPC Green Inventory, IPGOD); Clean Energy Regulator postcode data on small-scale solar and batteries (diffusion) |
| Culture, identity and social cohesion (cohesive) | Protection of Indigenous Knowledge and cultural expression; regional identity (geographical indications, certification marks); creative industries; against that, misappropriation | IPGOD trade marks (certification marks, Indigenous words, objections); Wine Australia's GI register; cultural and creative activity estimates (Bureau of Communications, Arts and Regional Research); Closing the Gap targets 15 and 16 as context |
| Consumer trust and safety (secure) | Trade marks lower search costs and signal quality; enforcement against counterfeits, some of which are unsafe | Trade mark oppositions and non-use removals (IP RAPID); IP judgments, including counterfeiting and passing off (`fedcourt`). Border seizures of counterfeits are not published separately (the Home Affairs annual reports fold them into "other goods") |
| Knowledge and opportunity (prosperous, cohesive) | Disclosure of inventions; rights lapsing into the public domain; who can take part in the system | Forward citations and families (Google Patents); patents' citations to science (Reliance on Science); early lapse rates (IP RAPID); the distribution analyses under Q2 |
| Wellbeing in places (cohesive, healthy) | Whether regions with more innovation and IP activity also do better on life satisfaction and trust, as context for distribution (not as proof of effect) | 2021 Census by SA2 and postcode: volunteering, unpaid care, long-term and mental health conditions, residential stability (`abs_census`); PHIDU's modelled health and wellbeing estimates by Population Health Area (`phidu`). No public source gives small-area life satisfaction or trust now that NATSEM's AURIN files cannot be reached |
| Wellbeing overall | The final layer: converting health, environmental and social outcomes into comparable terms for Q5 | Measuring What Matters (ABS, about 50 indicators); OECD How's Life? for comparators; wellbeing valuation evidence (WELLBY values, Office of Impact Analysis guidance on valuing non-market outcomes); HILDA if individual-level wellbeing is needed (Tier 3) |

Gaps that remain: disability and age are not observable for IP users in any open data; copyright is not registered,
so its public value can only be approached through the creative industries' figures and the literature.

## 3. Coverage of every sub-question

Each bullet in `docs/research-goal.md` §3, with how the proposed corpus covers it. "Full" means the data can answer it
descriptively or observationally; causal answers still need Tier 3 C. Since BLADE (B) is ruled out, where a row
names B the public registers are the best proxy (survival from the ABR and ASIC, GST as a size marker, R&D
expenditure, procurement, large firms' income), and turnover, employment and productivity for small firms are not
observable.

| Sub-question | Coverage | Data (numbers refer to section 4) |
|---|---|---|
| **Q1.1** Economic, social, technological and environmental outcomes of each form of IP | Partial | Economic: renewals, firm survival (1 to 4), BLADE (B). Technological: citations (1, F). Environmental: green patents and diffusion (9, 27). Social: through the pathways in section 2 (24 to 30). Trade marks and designs, not only patents, have renewal data |
| **Q1.2** When patents, trade marks and designs support innovation, commercialisation, investment, competition, diffusion | Partial | BCS (6); co-applicants and assignments (1); VC (I). Competition needs BLADE (B) |
| **Q1.3** Costs of obtaining, maintaining, licensing and enforcing | Partial | Fees (18) and attorney use (1). Licensing: only national royalty flows (15) and assignments recorded in IPGOD (1). Enforcement: IP judgments of the Federal Court, High Court and Copyright Tribunal (31), with hearing and judgment dates and the firms acting |
| **Q1.4** Costs to consumers, competitors, follow-on innovators and the public | Partial | Consumers: PBS case (19). Competitors: oppositions and re-examinations (1). Follow-on innovators: citations and patent thickets (1, E). Public: section 2 |
| **Q1.5** What existing evidence says about net contribution | Full | Evidence register (22) |
| **Q2.1** Who benefits most (businesses, industries, regions, groups) | Partial | Use is measurable (1 to 8); benefit needs outcomes (B). Analyses will say "uses" and "benefits" carefully |
| **Q2.2** Who faces barriers to understanding, accessing or using the system | Partial | BCS barriers (6); self-filer abandonment (1); IP Australia customer research (D) |
| **Q2.3** Underserved groups with unrealised potential | Full (descriptive) | "Missing filers": R&D performers (5), grant recipients (12), suppliers (11) and regions (7, 8) with potential but little use |
| **Q2.4** Startups, SMEs, established firms, research institutions, large enterprises | Partial | ABN age, entity type, GST (3, 4); large firms (13); research institutions by name (1, 12). Exact size needs BLADE (B) |
| **Q2.5** Gender, geography, socio-economic circumstances, other | Partial | Gender (10); geography and area-based SEIFA (8, 25), which describes places, not people; First Nations (G, H); disability and age not available |
| **Q3.1** Conditions that let holders benefit | Partial | BCS (6), BLADE (B) |
| **Q3.2** Complementary capabilities (finance, skills, management, markets, collaboration) | Partial | BCS (6); regional skills (8); collaboration via co-applicants and ARC Linkage grants (1, 12); management only in BLADE (B) |
| **Q3.3** Does registration change access to investment, licensing, procurement, partnerships, international markets | Partial | Procurement (11); partnerships (1, 12); international markets (16, 17); investment (I); licensing has no firm-level open data |
| **Q3.4** When trade secrets, open licensing, collaborative research or public funding do better | Partial | Informal protection (6); public funding and collaborative research (5, 12). Open licensing: no good data; evidence register (22) |
| **Q3.5** What distinguishes successful registration from little benefit | Partial | Renewal against lapse, survival (1 to 4); outcomes (B) |
| **Q4.1** Barriers that stop valuable innovation reaching the market | Partial | BCS barriers (6); customer research (D) |
| **Q4.2** Which barriers IP Australia could influence | Partial | Natural experiments in IP Australia's own levers (32): the innovation patent's closure to new filings (August 2021; the last expire in 2029), Raising the Bar (2013), fee changes |
| **Q4.3** Where funding, services, regulation, partnerships or expertise could add value | Partial | Q2.3 and Q4.2 analyses; evidence register of other offices' programmes (22) |
| **Q4.4** Market failures and institutional gaps others do not address | Partial | Evidence register (22); the GII's national gaps as hypotheses |
| **Q4.5** Where to act directly, collaborate or advocate | Not data | A remit and lever map: a qualitative exercise built on the findings above |
| **Q5.1** Magnitude, distribution and timing of benefits | Partial | Scenario modelling on the Q2 to Q4 populations, with priors from the evidence register (22) |
| **Q5.2** Additionality | Needs B or C | Natural experiments (32) give partial, observational evidence meanwhile |
| **Q5.3** Financial, administrative and opportunity costs | Partial | IP Australia's annual reports and portfolio budget statements; internal programme costs (D) |
| **Q5.4** Sensitivity to assumptions | Full (method) | A modelling choice, not a dataset |
| **Q5.5** Evidence needed to scale, modify or stop | Not data | An evaluation framework, written once the above is known |

## 4. Proposed additions

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
| 16 | **WIPO IP Statistics**: filings, grants and rights in force by office and origin, every country; PCT, Madrid and Hague by origin | WIPO | Do Australian firms take rights to international markets, and how does that compare with peers? | Q3 |
| 17 | **TM-Link** | IP Australia | Trade marks linked across offices: which Australian owners file abroad and where | Q3 |
| 18 | **IP Australia fee schedules**, current and historical | IP Australia | Direct costs of obtaining and maintaining rights, to set against revealed value from renewals | Q1, Q5 |
| 19 | **PBS expenditure and prescriptions** with IPGOD extensions of term | Department of Health, Disability and Ageing | A concrete consumer-cost case: spending on medicines under extended patent terms | Q1 |
| 20 | **ABS R&D surveys** (business, higher education, government) and **venture capital** (5678.0) | ABS | National and industry R&D and VC context | Q3, Q4 |
| 21 | **OpenAlex** (Australian institutions' research output) | OurResearch | Research capacity by institution and field, to compare with patenting (commercialisation gap) | Q2, Q4 |
| 22 | **An evidence register** of key literature and evaluations (PC Intellectual Property Arrangements 2016; IP Australia economic research papers; OECD; UK IPO, EUIPO SME Fund and other IP-support evaluations) | various | Q1's "what can existing evidence establish", and priors for Q5 where Australian data cannot give magnitudes | Q1, Q5 |
| 23 | **Bureau of Communications, Arts and Regional Research: cultural and creative activity** | Department of Infrastructure | The size of creative industries, where copyright and design protection operate | Q1 |
| 24 | **Measuring What Matters** (about 50 indicators, five themes) | Treasury and ABS | The Australian Government's own definition of wellbeing: the outcome layer and vocabulary for public value | Q1, Q5 |
| 25 | ~~NATSEM small-area estimates of life satisfaction and trust~~, replaced by the **2021 Census** (volunteering, unpaid care, health conditions, residential stability, workforce; SA2 and postcode) and optionally **PHIDU's Social Health Atlas** | ABS; PHIDU | Wellbeing and social cohesion by place, beside regional IP use (context, not effect) | Q1, Q2 |
| 26 | **OECD How's Life?** for comparator countries | OECD | Replaces the Australia-only file | Q1 |
| 27 | **Clean Energy Regulator small-scale installations by postcode** | CER, data.gov.au | Diffusion of green technologies by place | Q1 |
| 28 | **Wine Australia register of geographical indications** | Wine Australia | Regional identity protection (small scrape) | Q1 |
| 29 | ~~Australian Border Force notices of objection and seizures~~ | ABF annual reports | **Dropped:** the annual reports do not report IP seizures separately | Q1 |
| 30 | **Closing the Gap targets 8, 15 and 16** (already held) | Productivity Commission | Context for a First Nations workstream | Q1, Q2 |
| 31 | **IP judgments** (Federal Court, Full Federal Court, High Court, Copyright Tribunal) | The courts, via the Open Australian Legal Corpus | Enforcement costs and outcomes | Q1 |
| 32 | **Policy-change dates and terms** (innovation patent phase-out, Raising the Bar, fee schedules) | Federal Register of Legislation, IP Australia | Turns IPGOD into natural experiments on IP Australia's own levers | Q4, Q5 |

### Tier 3: needs your help or an institutional request

Listed in order of value. Items marked "you" are the limited fetches you offered; the rest are requests to others.

| # | Dataset | Why it matters | How |
|---|---|---|---|
| A | ~~A current IPGOD and IPLORD extract~~ | **Done with public data:** IP RAPID, IP Australia's weekly open data release, covers every application to the current week (`iprapid`) | Ingested |
| B | ~~ABS BLADE with IP Australia's linked IP data~~ | **Ruled out (2026-10-22): no ABS integrated data assets.** It was the only source of small firms' turnover, employment and productivity | Not pursued |
| C | ~~Examination records with examiner assignment~~ | **Ruled out (2026-10-22): public data only.** It would have allowed the examiner leniency design | Not pursued |
| D | ~~IP Australia customer and SME research microdata~~ | **Ruled out: public data only.** Published reports can go in the evidence register | Not pursued |
| E | **Global patent data**: Google Patents Public Data (BigQuery) | Forward citations and patent families as value measures; Australian inventors abroad | **Ingested** (`google_patents`) |
| F | ~~The Lens API~~, replaced by **Reliance on Science** (Marx and Fuegi; CC BY-NC 4.0) | Patent to scholarly-literature links: knowledge diffusion from research | **Ingested** (`reliance_on_science`); the Lens API is paid beyond a trial |
| G | **ABS TableBuilder: Census 2021 owner-managers** by sex, Indigenous status, industry and region | Who runs businesses, the denominator for gender and First Nations participation | You, a free registration and a few tables |
| H | **First Nations business data** (Indigenous Business Sector Snapshot; Indigenous Procurement Policy outcomes) | Q2 for First Nations businesses, replacing Closing the Gap | Mixed: some public reports, some by request |
| I | ~~Venture capital deal data~~ | **Ruled out: paid, not public** | Not pursued |
| J | **TGA's Australian Register of Therapeutic Goods** | Generic competition for the health case (section 2) | **Ingested** (`tga`) from your export; it has no dates, so time to market needs another route |
| K | ~~HILDA~~ | **Ruled out: access needs an application** | Not pursued |

## 5. What the corpus would let later sessions answer

Each line is a descriptive or observational analysis that the Tier 1 and 2 data support; the evidence level is noted
as the research goal requires.

- **Q1 Value.** Revealed private value of patents and designs from renewal and lapse decisions, by applicant type,
  technology and origin (observational, an established method). Share of Australian rights, renewals and royalty
  flows held by foreign versus domestic owners (descriptive). Direct costs against revealed value (descriptive).
  Pharmaceutical extension-of-term spending (descriptive case study). Non-financial pathways from section 2: green
  patenting and its diffusion, Indigenous Knowledge and geographical indications, counterfeit enforcement, disclosure
  and the public domain (descriptive), framed against Measuring What Matters.
- **Q2 Distribution.** IP use per business by industry, firm age, entity type, size proxy, remoteness and SEIFA
  decile; gender of inventors and individual applicants; self-filers against attorney filers (descriptive).
- **Q3 Conditions.** Survival and growth proxies (ABR, ASIC, GST status) for first-time filers against matched
  non-filers; R&D performers that do and do not register; IP holders' share of government contracts; international
  filing by firm type; formal against informal protection from BCS (observational).
- **Q4 Opportunities.** "Missing filers" (R&D performers, grant recipients and procurement suppliers that never use
  the system); regions with high innovation potential and low use; abandonment and opposition outcomes for
  self-filers; barriers by firm size from BCS (descriptive, hypothesis-generating).
- **Q5 Interventions.** Needs Tier 3 C, or the natural experiments in `policy_events`, for credible additionality.
  Until then: evidence register priors and scenario ranges built from the Q2 to Q4 populations (projection, clearly
  labelled).

## 6. Storage (as built)

GitHub refuses files over 100 MB and slows beyond a few GB, so:

- **R2 (bucket `ipholmes`) holds the large files**: raw files under `raw/<source>/` (IP RAPID, IPLORD, the ABR, ASIC,
  TM-Link, AusTender, PBS, the ASGS allocation files) and large Parquet tables under `processed/<source>/`.
- **The repo holds small raw files and every table under 50 MB**, including analysis-ready summaries of the large
  sources (`ipgod/*_rights`, `ipgod/applicant_year`, `iplord/iplord_abn`, `linkage/abn_spine`).
- `data/manifest.json` records every file's SHA-256, size, rows, columns and location; `corpus verify --r2` checks it.

## 7. Repository

As planned, with the details in `README.md`; `docs/catalogue.md` lists every table.

## 8. What was ingested (2026-10-22)

Every approved source has a module in `src/corpus/sources/` (updated after your downloads and the BigQuery key, the same day); `docs/catalogue.md` lists every table with its rows and
columns. In short:

| # | Source (`id`) | Status | What is there |
|---|---|---|---|
| 1 | IP RAPID (`iprapid`), replacing IPGOD 2022 | Ingested | All six tables, every right, to the current week (R2); a summary per right type and an applicant by financial year panel (repo). Its events include extensions of term (1,450 patents granted one), lapses (300,270 patents), assignments (110,600 patents), registered licences (1,700) and oppositions (1,831 lodged); current to the week of 19 October 2026 |
| 2 | IPLORD 2020 (`iplord`) | Ingested | The full panel (R2) and its ABN rows (repo). The public release has no patent columns; `ipgod/applicant_year` covers patents to 2022 |
| 3 | ABN Bulk Extract (`abr`) | Ingested | 20.6 million ABNs, current and cancelled (R2), without individuals' names |
| 4 | ASIC companies (`asic`) | Ingested | 4.0 million companies (R2) |
| 5 | R&D Tax Incentive (`rdti`) | Ingested | 38,512 claims, 2021-22 to 2023-24 |
| 6 | ABS business characteristics (`abs_bcs`) | Ingested | 13 flows, including licensing of IP and "inability to protect IP" as a limit on commercialisation |
| 7 | Counts of businesses (`abs_cabee`) | Ingested | National tables to June 2026; state, industry, survival, SA2 and LGA cubes to June 2025 |
| 8 | Places (`abs_regions`) | Ingested | ASGS 2021 mesh blocks, postal area to SA2 and remoteness, SEIFA 2021, Data by Region |
| 9 | Concordances (`concordances`) | Ingested | WIPO's 35 technology fields (and each IP RAPID patent's fields), ALP IPC and Nice to ISIC and ANZSIC, the IPC Green Inventory |
| 10 | Gender-name dictionary (`wgnd`) | Ingested | WGND 2.0 (CC0, not CC BY as first listed) |
| — | Linkage (`linkage`) | Built | `abn_spine`: 391,983 ABNs (all found in the ABR) with ABR and ASIC attributes, source flags and first and last filing years |
| — | GII 2026 (`gii`), Closing the Gap (`ctg`) | Ingested | Kept from the earlier corpus as context |
| 11 | AusTender (`austender`) | Ingested | 1.55 million contract notices, July 2007 to October 2026, 94.5% with a supplier ABN |
| 12 | ARC grants (`arc_grants`) | Ingested | 34,977 grants |
| 12 | NHMRC grants (`nhmrc_grants`) | Ingested (your download) | 12,224 grants, application rounds 2013 to 2026, harmonised into one table; investigators' names left out |
| 13 | Corporate tax transparency (`ato_ctt`) | Ingested | 2013-14 to 2024-25 |
| 14, 26 | OECD panel (`oecd`) | Ingested | 24 flows: MSTI, methods used to protect IP, patents (WIPO fields, environment, ownership, co-invention, regions), business demography, venture capital, IP tax regimes, How's Life? (current and future well-being, including trust in government, others and the police; by sex, age and education; child well-being), and distance to the Sustainable Development Goals 1, 2, 9 and 13 |
| 15 | WDI panel (`wdi`) | Ingested | 22 indicators, every country; the World Bank has archived its trade mark series |
| 16 | WIPO IP statistics (`wipo_ipstats`) | Ingested | From the public API behind WIPO's data centre: every office by every origin, 1980 to 2024 (4.9 million values: patents, utility models, trade marks, designs; applications, grants, in force, by field or class), office workloads, and PCT, Madrid and Hague by origin |
| 17 | TM-Link (`tmlink`) | Ingested | Links, applications, owners, classes, Madrid and property tables (R2); free-text tables left out |
| 18 | IP Australia fees (`ipa_fees`) | Ingested (current only) | Application, examination, renewal, opposition fees; historical schedules need the Wayback Machine, which this environment cannot reach |
| 19 | PBS (`pbs`) | Ingested | Date-of-supply data from July 2020 by item and month, and the item to drug map |
| 20 | ABS R&D and venture capital (`abs_rd_vc`) | Ingested | BERD 2023-24, GOVERD 2024-25, HERD 2024, venture capital to 2018-19 (discontinued) |
| 21 | OpenAlex (`openalex`) | Ingested | 1,910 Australian institutions (243 companies), works by field and year from 2000 |
| 22 | Evidence register (`evidence`) | Ingested | 20 items, journal items checked against Crossref (one flagged: its only Crossref record is a later SSRN version) |
| 23 | Cultural and creative activity (`bcarr_creative`) | Ingested (your download) | Both releases (2008-09 to 2022-23, 2015-16 to 2024-25) as one long table |
| 24 | Measuring What Matters (`mwm`) | Ingested | 50 indicator pages and their data |
| 25 | 2021 Census (`abs_census`), in place of NATSEM | Ingested | 14 General Community Profile tables by SA2 and postal area: volunteering, unpaid care, health conditions, mobility, labour force, qualifications, industry, occupation; and PHIDU's Social Health Atlas (`phidu`, your download, in R2): 4.95 million values by Population Health Area and socioeconomic quintile, including modelled estimates of psychological distress, self-assessed health and risk factors (non-commercial licence) |
| 27 | Small-scale renewables (`cer`) | Ingested | Every postcode file, 2001 to 2026 |
| 28 | Wine GIs (`wine_gi`) | Ingested | The Australian GI register and the other registers' PDFs |
| 29 | Border enforcement | Dropped | The Home Affairs annual reports (2016-17 to 2024-25) do not report IP seizures separately |
| 30 | Closing the Gap 8, 15, 16 (`ctg`) | Ingested | |
| 31 | IP judgments (`fedcourt`) | Ingested | 2,666 decisions (Federal Court 2,097, Full Court 326, High Court 146, Copyright Tribunal 80) to 10 March 2025, from the Open Australian Legal Corpus: cover-page fields (practice area and sub-area, catchwords, legislation, hearing and judgment dates, solicitors), rights and Acts cited, full texts (R2) |
| J | TGA register (`tga`) | Ingested (your download) | 98,147 ARTG entries (35,113 medicines, 62,647 devices) and their active ingredients; no dates |
| E | Google Patents (`google_patents`) | Ingested | 1.75 million families with an Australian publication, applicant or inventor (offices, grants, forward citations, titles); 3.2 million publications, with Australian application numbers that join to IP RAPID; 1.85 million citation pairs |
| F | Reliance on Science (`reliance_on_science`) | Ingested | 620,364 citations to 175,607 papers (OpenAlex ids) by US patents in 18,254 families with Australian applicants or inventors; 59,202 patent-paper pairs |
| F | Australian research cited by patents (`openalex_works`) | Ingested | 2.46 million cited works with an Australian institution (OpenAlex); 103,644 of them are cited by 287,416 US patents (614,148 citations, 6% from patent families with Australian applicants or inventors), with their Australian institutions. Most cited: Melbourne, CSIRO, Sydney, Monash, Queensland |
| 32 | Policy events (`policy_events`) | Ingested | 13 dated changes (four marked to verify) and IP Australia's policy register (155 proposals and their status) |

### What needs you

Nothing is blocking. Optional:

1. **BigQuery**: `GCP_PROJECT_ID` should be a project id or left unset (the key's own project is used); giving the
   service account the BigQuery Read Session User role makes `google_patents` download much faster.

Lens was not pursued (its API is paid beyond a trial); Google Patents and Reliance on Science cover its uses.

### A first look, to show the corpus works

Not a finding: of the 18,487 companies in the R&D Tax Incentive reports (2021-22 to 2023-24), 49% appear in IP
RAPID as an applicant for any right, and 18.5% for a patent (with IPGOD 2022, which stopped in early 2022, it was
36% and 14%). Whether the rest are "missing filers" with protectable inventions, or firms for which registration has
little value, is exactly the kind of question Q3 and Q4 ask.

### Repository size

The repo holds about 690 MB of data (the largest parts: OECD panels, IP RAPID summaries, ABS regional data), every file
under 50 MB. If it grows past about 1 GB, move the OECD raw files to R2 (`keep="r2"` in `oecd.py`).
