# Stage 1 summary: every variable on its own

**What this is.** A self-contained account of Stage 1 (the univariate stage) of the exploratory data analysis (EDA):
why it was done, how, what it found, what was decided because of it, and what it hands to Stage 2. It is written for
readers who have not followed the work day by day and are not data scientists.

**Date:** 26 October 2026. **Evidence:** every number below is quoted from an observation in
[`analysis/notebooks/01_univariate.ipynb`](../analysis/notebooks/01_univariate.ipynb), named by its number (U0 to
U98), where the output it rests on is on the page. Every observation in Stage 1 is **descriptive**: it says what the
data show, not why, and nothing here is a cause or a conclusion. Terms are explained in [`GLOSSARY.md`](../GLOSSARY.md).

**Status.** Stage 1 is complete: every lens and every planned attachment has its profile. The last three attachments
to the `rights` lens (how each right came to Australia, each patent's worldwide family, and its inventors) were added
on 26 October (U88 to U98, ADR 0022). Nothing here answers the five research questions: that waits until Stage 3 is
done and the owner says so.

---

## 1. In brief

**What Stage 1 did.** It took a corpus of 162 tables from 41 sources (317.8 million rows, U0), organised it into seven
analysis-ready tables called *lenses* (one row per IP right, firm, postal area, country-year, industry-year, research
institution-year and month) with four long companion tables, and described every column on its own: how complete it
is, its shape, its outliers and its quirks. That produced 99 numbered observations, a series of repairs to the data
before they could be trusted (recorded in ADR 0008 to 0022), and a set of rules for how each variable may be used in
Stages 2 and 3. The groundwork was laid from 21 to 24 October 2026; Stage 1 itself ran on 25 and 26 October, lens by
lens, with the owner setting the order.

**The ten things most worth knowing.**

1. **Australia's patent system is mostly used from overseas; its trade mark system mostly from home.** About nine in
   ten standard patents are filed from overseas (91.3% in FY2017 to FY2026; the United States alone 43.5%), against
   59.0% of trade marks filed by Australians (U13). China now files as many patent applications at IP Australia as
   Australians do (8.3% each in 2024, from 0.3% in 2004), and three-quarters of Australians' own applications are made
   abroad (76.1%, U70). Overseas applicants arrive through the PCT (81.0% of their standard patents in FY2010), mostly
   with inventions first filed in the United States (53.42%), and their patents reach a median 6 offices against
   Australians' 2 (U90, U91, U93).
2. **Almost everything is concentrated.** The top 1% of filing firms filed 55.3% of standard patents (U44); the tenth
   of postal areas with the most patents filed 72.5% of them with 29.2% of the people (U52); five attorney firms
   handle 63.96% of standard patents (U21); the Group of Eight hold two-thirds of ARC and NHMRC funding (U83); and one
   firm can be most of a postcode's patents (Aristocrat 76.3% of 2113's, U52).
3. **Places differ far more than chance would make them.** 68.2% to 72.5% of areas file below what chance allows
   around the national rate, and 6.7% to 15.5% above it, at postal areas and SA3s alike (U53). Stage 2 must model this
   spread rather than assume it away.
4. **Australians, above all individuals, often file without an attorney.** Overseas filers use one for 99.0% of
   standard patents; Australian filers for 85.4%; Australian individuals file 62.4% of their trade marks alone (U20).
   Individuals file about a fifth of the standard patents and two-fifths of the provisional applications filed from
   Australia (U48).
5. **Provisional applications doubled in FY2026** (10,069, against 4,143 to 5,047 a year in FY2022 to FY2025), driven
   by individuals without ABNs, both broadly and through a few heavy filers (U8). It is real, not a recording artefact
   (N01, settled with the owner). Why is a question for IP Australia (OQ5).
6. **Policy changes leave clear marks.** Two rushes to file before a rule changed (Raising the Bar, 4.39 times
   Australians' usual month; the innovation patent's closure, 4.31 times, then 95.9% fewer), four steps and two
   pauses, and several changes with nothing visible (U28). These are the raw material for the natural experiments
   the later questions need.
7. **Owners keep patents longer than they used to; about half of trade marks are renewed at ten years.** Standard
   patents' median years in force rose from 10.7 (1980s) to 13.5 (2000s and 2010s); 46.9% to 56.4% of trade marks
   were still in force after ten years (U36). The owner adopted years in force as a working measure for Stage 2,
   alongside other signals.
8. **Australia's research is used, but mostly abroad.** 93.6% of US patent citations to Australian research
   institutions' work come from inventions with no Australian applicant or inventor (U85). Nationally, research
   intensity peaked in 2008 (gross R&D 2.24% of GDP) and has fallen to 1.68% (2023), below the OECD median of 1.85%;
   business R&D is 26th of 35 OECD members (U65, U66). Of the patents filed in Australia from overseas, 0.85% have an
   inventor here (U96).
9. **The register's history shapes what it can say.** Early years hold only the rights that survived until records
   were computerised; some events were dated in batches; patent ownership history starts in FY2003; trade mark
   expedite requests fall sharply when records moved between systems in November 2018 (U23, U17, U34). Each is now
   handled, but each limits what can be compared over time.
10. **Links between datasets are the weakest point.** Firms' IP counts are lower bounds (U41); fewer recent filers
    are linked to an ABN (84.1% of Australian organisations' trade marks in FY2024, 59.9% in FY2026, U45); no firm has
    an industry, so patents reach industries only through a crosswalk that leaves out services (U75); half the
    universities' patents carry a postcode that is not a postal area (U87).

---

## 2. Why Stage 1, and what it asks

### The research it serves

The research (for IPAVentures, IP Australia) asks how Australia's IP system creates public value and where IP
Australia's interventions could add the most ([`research-goal.md`](research-goal.md)). It has five questions:

| # | Question | In short |
|---|---|---|
| Q1 | What public value does the IP system create? | Outcomes, costs and net contribution |
| Q2 | Who benefits, and who is underserved? | Firms, industries, regions and groups |
| Q3 | What determines whether IP protection produces value? | Capabilities, finance, alternatives to registration |
| Q4 | Where are the greatest opportunities for intervention? | Barriers IP Australia can influence |
| Q5 | What outcomes could interventions produce? | Size, timing, additionality and cost |

Its principles matter for the EDA: public value over activity counts, additionality over attribution, distribution
over averages, openness to disconfirming evidence, and evidence proportionate to the claim (descriptive,
observational, causal and projected kept apart).

### Where Stage 1 sits

Answering those questions well depends on knowing what the data can and cannot say. So the questions wait, and the EDA
comes first, in three stages ([`eda-plan.md`](eda-plan.md)):

| Stage | Asks | Ends with |
|---|---|---|
| **1. Univariate** (this one) | What does each variable look like on its own: completeness, shape, outliers, quirks? | Every variable of every lens profiled; exclusions and transformations decided |
| 2. Bivariate | Which pairs move together, how strongly, for whom? | Leads with sizes and intervals that survive correction and a second sample |
| 3. Multivariate | Do the signals survive other factors? What structure exists? | A table of early signals and a table of data gaps |

Stage 1 deliberately does not relate one variable to another, test anything, or answer any question. Its job is to
make the later stages safe: to find the errors, gaps and artefacts that would otherwise be mistaken for findings.

---

## 3. How it was done

### 3.1 The corpus

The corpus holds 162 tables from 41 sources, 317,792,796 rows in all; three sources hold 69.73% of the rows (IP RAPID
31.57%, TM-Link 24.86% and the OECD panels 13.3%, U0; corrected on 27 October 2026 from the first profile's 152
tables, 38 sources and 70.4%, which U0's text had kept). The profile dates from 25 October, so `ror` and the WIPO tables
added on 26 October are not in it. Row counts measure how much a source records, not how much it
matters, so the work is organised by unit of analysis, not by source. The sources run from IP Australia's own
registers (IP RAPID, IPLORD, TM-Link) through business registers (ABR, ASIC), R&D and procurement (the R&D Tax
Incentive, AusTender), the ABS (Census, business counts, prices, labour, surveys), international panels (World Bank,
WIPO, OECD, GII) to research (OpenAlex, ROR, ARC and NHMRC grants, Google Patents). [`catalogue.md`](catalogue.md)
describes them all.

### 3.2 Lenses: a shared unit for every comparison

Two variables can only be compared if they describe the same thing. So every table in the corpus is attached to at
least one **lens**: an analysis-ready table with one row per unit (ADR 0002, 0007). Wide sources are held in long
**companion tables** (one row per unit, source, indicator and period) so that every published value is kept without
making the lens unreadable.

| Lens | One row per | Rows | Mainly informs |
|---|---|---|---|
| `rights` | IP right (patent, trade mark, design, plant breeder's right), 1904 to 2026 | 4,368,006 (74 columns) | Q1, Q2 |
| `firms` | ABN in any IP, R&D, procurement or tax source | 398,450 | Q2, Q3, Q4 |
| `regions` (+ `region_indicators`) | Postal area | 2,641 (+ 22,511,923) | Q2, Q4 |
| `national` (+ `national_indicators`) | Country, year and indicator | 135,597 (+ 41,218,170) | Q1, Q4 |
| `timeline` | Month, for Australia, January 1904 to September 2026 | 1,473 | Q1, Q4, Q5 |
| `industries` (+ `industry_indicators`) | ANZSIC division and financial year, FY1990 to FY2026 | 703 (+ 1,409,875) | Q2, Q3, Q4 |
| `institutions` (+ `institution_rights`) | Research institution (ROR) and calendar year, 1990 to 2026 | 4,810 (+ 31,528) | Q1, Q2, Q3 |

All are rebuilt from the corpus in about two minutes by `analysis/eda/build.py`, and every column is described in
`analysis/eda/variables.yaml`.

### 3.3 The rules the work followed

- **Every dataset goes through every stage** (the owner's decision, ADR 0007). This is a discovery phase, so the EDA
  goes broad; only the approach changes from stage to stage.
- **Clean before broad:** one row per key in every lens (checked by a test); where two sources measure the same thing,
  one is the main measure and the other a labelled comparison, never added together; known errors repaired before a
  table's Stage 1 section; detail kept reachable by key.
- **Evidence** (ADR 0004): observations are numbered, quote the numbers in the output above them, and carry a strength
  label. Plain English, a chart for each variable with its source named underneath, and every term in the glossary.
- **Small outputs** (ADR 0003): everything is aggregated in DuckDB, which refuses results over 250,000 rows; raw rows
  are never printed. The notebook is committed with its outputs so it can be read on GitHub without running anything.
- **Money in real terms**, deflated by the quarterly CPI (U30) and shown as recorded beside it.

### 3.4 The order of work

| When | Step | Record |
|---|---|---|
| 21 to 23 October | Corpus built; three-stage EDA and lenses agreed; evidence conventions; the timeline added as a fifth lens | ADR 0001 to 0006 |
| 25 October | An independent review of an earlier data audit (42 findings, F01 to F42, and new ones of its own, N01 to N07) set the repairs; the owner decided every dataset goes through every stage, with two new lenses | Review; ADR 0007 |
| 25 October | The last check before Stage 1: repairs to the lenses and the corpus | ADR 0008 to 0011 |
| 25 October | `rights`: core variables (U1 to U16), then its parties (U17 to U21) | ADR 0012, 0013 |
| 25 October | `timeline` (U22 to U30) | ADR 0014 |
| 25 October | `rights`: its events, milestones and lifetimes (U31 to U40) | ADR 0015 |
| 25 October | `firms` (U41 to U47) | ADR 0016 |
| 25 October | `regions` and its attachments (U48 to U62) | ADR 0017, 0018 |
| 26 October | `national` and its attachments (U63 to U72) | ADR 0019 |
| 26 October | `industries` and its attachments (U73 to U79) | ADR 0020 |
| 26 October | `institutions` (U80 to U87), the last planned lens | ADR 0021 |
| 26 October | `rights`: its links, Google Patents families and inventors (U88 to U98) | ADR 0022 |

The owner set the order at each step (the answered questions A1 to A6 in `owner-questions.md`); Claude made the
analytical and engineering choices and recorded the non-obvious ones as ADRs.

### 3.5 Profile, find, repair, record

Each lens went through the same loop: profile every column; when a profile showed something that could not be true
(a placeholder date, a column measuring the wrong thing, a series starting before its records were complete), trace
it back to the source, repair the lens or the corpus, keep the evidence on the page (read from the source's own
tables, so it survives the repair), and record the repair in an ADR. The main repairs:

| Lens or source | What was wrong | Repair | ADR |
|---|---|---|---|
| `rights` | "No country recorded" counted as overseas (517,145 patents) | Origin has three values: Australian, overseas, unknown | 0009 |
| `rights` | Patents mixed standard, provisional and second-tier | Counted apart everywhere; headlines use standard patents | 0009 |
| `rights` | A 1970 placeholder end date (1,282 rights); trade marks before 1986 "registered" on their filing day; a "technology area" that repeated the class for trade marks and designs; the applicant counted as its own attorney; a state missing for 34.96% of recent Australian patents | Each emptied, restricted or rebuilt (U2, U16) | 0012 |
| `rights` | The current holder used where the filer was meant | Founding applicant columns beside the holder's; `representation` (attorney, other agent, self) | 0013 |
| `timeline` | 15 series started on survivors, partial records or batch dates; the 1995 patent term change missing from the policy register | Series start where records are complete; the term change is the 17th policy event | 0014 |
| `firms`, `regions` | Applications credited to the current holder | Counted by the filer's ABN and postcode | 0016, 0017 |
| `regions` | Rates in areas too small to mean anything | A rate only where 10 or more applications would be expected; SA3s for pooling | 0017 |
| AusTender | Contract values summed over every amendment ($7,585.9 billion) | One row per contract at its latest notice ($1,258.5 billion) | 0010, 0011 |
| `national` | WIPO's former states and unknown origins dropped (9.65% of patent applications by origin) | Kept, with an `entity` column | 0019 |
| `concordances` | Each ISIC class split over partial ANZSIC links (textiles had 8.9% of patents) | Weight to full links first (textiles 2.3%) | 0020 |
| `rights` build | Two ties broken arbitrarily, so a few figures changed from build to build | Ties fixed; two builds agree row for row; five quoted figures corrected | 0019 |
| `rights` links | IP RAPID labels every PCT number, and many other offices' priority numbers, `au` | A patent priority's office read from its number | 0022 |

Each repair has a test, and the suite passes (86 tests at the end of the stage).

### 3.6 Corrections made on the way

The record corrects its own mistakes in the turn they are found. Stage 1's corrections include: the policy register's
note that the Patents Act 1990 brought in 20-year patents (it was 16 years until 1 July 1995, U23); charts of trade
marks before 1983 and designs before 1986 that showed survivors without saying so (U5, U10); the World Bank's trade
mark series, described as applications but counting classes (U67); five figures that differed between builds
(U48, U49, U52, U53); and, found when the notebook was re-run with the last attachments, three more that depended on
how ties were broken: the share of people in the top tenth of areas (29.0% became 29.2% for standard patents, 32.9%
became 32.8% for trade marks, U52), and the universities' postcodes outside the postal areas, which counted joint
filings twice and named an arbitrary institution (UNSW's 216 became 210, U87). On 27 October, building the evidence
pages found that U0's text still gave the first corpus profile (152 tables, 38 sources) when the output above it gave
the later one (162 tables, 41 sources); the text now follows the output. Each is noted where it applies and in the
handover.

---

## 4. What each lens shows

### 4.1 IP rights (`rights`, U1 to U21 and U31 to U40, U88 to U98)

Every patent, trade mark, design and plant breeder's right in IP RAPID, 1904 to October 2026.

- **What is in it.** 4,368,006 rights with no repeats; origin known for 86.37% (U1). Trade marks are 53.5% of rights,
  patents 40.12%, designs 6.153%, plant breeder's rights 0.2686%; of patents, 82.17% are standard, 15.07% provisional
  and 2.77% second-tier (U4). Recent years are complete (U6).
- **Who applies.** About nine in ten standard patents come from overseas (Australian share 7.9% to 12.4% since FY1990,
  U7). The first applicant's country for FY2017 to FY2026: the United States 43.5%, Australia 8.6%, China 6.8%, Japan
  5.3% (U13). Australians file 59.0% of trade marks and 94.45% of provisional applications. 12% to 22% of Australian
  organisations' rights carry no ABN (U13).
- **The provisional rise.** 10,069 in FY2026, from individuals (5,399 against 1,365 to 1,926), with distinct ABNs flat
  at 1,361; single-filing individuals rose from 1,538 to 2,507 and 54 individuals filed 10 or more (one filed 375). It
  began in early 2025, peaked in March and April 2026 and eased by September 2026 (U8).
- **How rights end.** "Lapsed" (an application abandoned) and "ceased" (a registered right let go) are different
  (U9). 408,957 old patents (filed FY1904 to FY1999) have an "unknown" status, and only 68.9% of expired patents have
  a grant date, so old grants are under-recorded. The standard patent grant rate fell from 75.5% (FY2000) to 54.4%
  (FY2008) and recovered to 65.4% (FY2019, U10).
- **How long it takes.** A median 980 days to grant a standard patent and 223 days to register a trade mark (filed
  FY2010 to FY2019, U11), with a sharp trade mark peak at 222 days that WIPO's figures show is the office's usual path
  (U70). Patent examination from request to acceptance lengthened to 755 days (FY2006) and has been 422 to 516 since
  FY2014 (U33).
- **What is protected.** Medical technology, pharmaceuticals and biotechnology are 32.0% of standard patents;
  advertising and business services (class 35) 11.7% of trade marks (U14).
- **Where.** New South Wales 38.2% and Victoria 23.7% of Australian standard patents; usable postcodes for 99.3% of
  Australian applicants (U15, U16).
- **Filers, holders and representation (the parties).** The holder is not the filer for 22.0% of standard patents
  filed in the 2000s, but for patents filed before FY2003 the history cannot be seen (U17). More Australian-filed rights
  moved overseas than came the other way (standard patents 2,036 against 804, U18). Overseas filers almost always use
  an attorney; Australian individuals often file alone (U20). Five patent attorney firms handle 63.96% of standard
  patents; trade mark representation is spread (top five 17.51%, U21).
- **Milestones and lifetimes (the events).** Each milestone is recorded from a different date, so shares compare only
  within those years (U32). Expedited patent examination rose from 1.87% (FY2005) to 10.31% (FY2026); trade mark
  expedite requests fell from about 1,400 to about 230 a month in November 2018, when the records moved between
  systems (U34). About one standard patent in seven and one trade mark in five is assigned (U35). Owners keep patents
  longer than they did and renew about half of trade marks at ten years (U36). Extensions of term are rare (1,450,
  U37). Two timeline puzzles were resolved: the 2002 trade mark trough (the gap between two Acts' first terms and the
  2000 filing peak, U38) and April design lapses (how lapses were dated, U39).
- **How rights came to Australia (the links).** IP RAPID labels 93.88% of PCT numbers as Australian, so a priority's
  office is read from its number (U88). The PCT route then matches WIPO's count of national phase entries at IP
  Australia, a median 1.001 of it from 1995 to 2024 (U89). Overseas applicants' standard patents came through the PCT
  for 81.0% in FY2010 and 69.3% in FY2026, with divisionals rising to 19.9%; Australians' moved from claiming a
  provisional (81.2% in FY1985, 11.4% in FY2026) to the PCT, divisionals and, lately, direct filing (28.3% in FY2026, a
  lead) (U90). Overseas inventions were first filed in the United States for 53.42%; 91.24% of Australians' PCT
  applications were filed at IP Australia (U91).
- **Families, reach and citations (Google Patents).** 94.81% to 99.23% of standard patents filed in each decade since
  the 1980s find their family (U92). Overseas applicants' patents reach a median 6 offices and 66.66% are granted in
  the United States; Australians' reach 2, and 45.53% are filed only here (U93). Within five years, overseas
  applicants' families are cited by a median 6 others and Australians' by 1 (43.99% never) (U94).
- **Inventors.** Inventors' countries are missing for most patents filed only in Australia, because Google's
  Australian publications give none (U95). Where known, 94.47% of patents filed from Australia have an inventor here,
  against 0.85% of those filed from overseas (U96). Gender estimated from names matches WIPO's published share for
  Australia (14.6% against 13.8%) but runs a median 4.5 points high elsewhere, 11.2 for China and 21.3 for Korea, so it
  is read for inventors in Australia only (U97): about one in seven is estimated to be a woman (U98).

### 4.2 Australia over time (`timeline`, U22 to U30)

IP Australia's register month by month, January 1904 to September 2026, with the CPI and 17 policy changes.

- **Repairs.** 15 series started too early (on survivors, partial records or batch dates) and now start where their
  records are complete; the 1995 rise of the patent term from 16 to 20 years was added (patent expiries fell 98.4%
  when it took effect, U23, U28).
- **Growth.** Standard patents grew 3.9% a year in the 1990s and 0.4% a year from 2019 to 2025, set by overseas
  applicants; trade marks 4.3% and designs 5.5% a year since 2019, designs almost all from overseas; falls in 2009
  (U25).
- **Seasons.** Australians file 25% to 34% less in January, overseas applicants 5% to 10% less, and the lull is
  deepening for Australian patents (January at 80% of an ordinary month in the 1990s, 73% since 2020). The office's
  output follows its own calendar (U26).
- **Outcomes.** Patent grants peaked in 2016 (25,687); trade mark cessations rose to 35,484 (2025) (U27).
- **Policy.** Two rushes, four steps, two pauses at commencement, and nothing visible for PCT accession, plain
  packaging, the 2018 and 2019 Productivity Commission responses or the designs grace period (U28).
- **Artefacts.** 42 months still stand out after the repairs; each is explained (pauses and backlogs, the register's
  start-up before June 1904, a portfolio transfer in July 2015) and none is removed (U29).
- **Prices.** The CPI is complete and quarterly from 1948 (312 quarters), and deflates every money series (U30).

### 4.3 Firms (`firms`, U41 to U47)

Every ABN that appears in IP Australia's data, the R&D Tax Incentive, AusTender or the ATO's tax transparency reports.

- **Who is in it.** 398,450 ABNs: the firms that used one of five schemes, not all businesses. 63.68% are in IP RAPID
  alone and 12.75% linked to IP by IPLORD alone (with zero IP counts), so firms' IP counts are lower bounds (U41).
- **What they are.** Private companies are 74.7% of firms and 94.5% of R&D claimants (U42); a median 13.6 years old on
  the record, with a spike at the ABN's start in 1999 (U43).
- **IP use.** The median filing firm filed one application; the top 1% filed 55.3% of standard patents and 25.9% of
  trade marks; 116,240 firms hold 430,305 rights in force (U44).
- **A linking problem.** First-time trade mark filers fell from 11,318 (FY2024) to 7,384 (FY2026), but so did the share
  of Australian organisations' trade marks with a filer's ABN (84.1% to 59.9%): at least part of the fall is in
  linking, not filing (U45, OQ7).
- **Money and place.** The median latest R&D claim is $307,490; the top 1% of government suppliers hold 83.1% of
  contract value (U46). IP filers and R&D claimants are more metropolitan and more advantaged than firms in general
  (U47).

### 4.4 Places (`regions`, U48 to U62)

Every postal area, with its people, businesses, socio-economic indexes, the IP filed from it (FY2017 to FY2026), R&D
claimants and contracts, and every value of five area sources in `region_indicators`.

- **Coverage.** 2,641 postal areas and 25,365,506 people; the filer's postcode differs from the holder's for 6.05% of
  standard patents (U48).
- **Postcodes that are not places.** 94.45% of standard patents' filer postcodes are postal areas; 4.14% are real
  codes with no residents, led by universities' (U49). Half the universities' standard patents carry such a code
  (U87).
- **Very different areas.** 818 areas have fewer than 1,000 people; 18 have more businesses than residents (U50).
  Major cities hold 37.7% of areas and 72.8% of people; SEIFA deciles rank areas, not people (U51).
- **Concentration and chance.** The top tenth of areas file 72.5% of standard patents with 29.2% of people, and an
  area's patents are often one firm's (U52). Areas differ far more than chance would make them, so Stage 2 uses
  negative binomial models and pooling (U53).
- **'Missing filers'.** 50.7% of R&D claimants have never filed IP; claimants are 5.6 per 1,000 businesses in major
  cities and 0.6 in very remote areas (U54).
- **The attachments.** 22.5 million values (U55). Values split from SA2s track direct counts (Data by Region's
  population is within 10% of the direct count for 99.34% of areas of 1,000 people or more); CABEE counts 0.742 of the
  ABR's businesses in the same order, so business counts come from the ABR (U56). Census cells are small and perturbed
  (U57); Data by Region repeats the Census (U58); most businesses employ no one (U59); PHIDU's periods differ (U60);
  installations moved from solar water heaters to panels to batteries (U61); the ACT holds 27.0% of government
  contracts with 1.3% of businesses (U62).

### 4.5 Australia and other countries (`national`, U63 to U72)

30 indicators for 229 places, 1960 to 2025, and 41.2 million attached values (the GII 2026, 24 OECD flows, WIPO's
other tables, Measuring What Matters and Closing the Gap).

- **Coverage.** Australia's researchers series ends in 2010 and technicians in 2008 (U63). Before 1995 WIPO cannot say
  where most applicants come from (29% to 34% unknown), so WIPO's series by country are compared from 1995 (U64).
- **Australia over time.** Gross R&D 1.26% of GDP (1990), 2.24% (2008), 1.68% (2023); business R&D 0.91% against an
  OECD median of 1.18%; manufacturing 13.7% to 5.32% of GDP (down 61%, the median member 30%); IP payments exceed
  receipts in every year (U65).
- **Against the OECD.** Near the top for non-resident patents (5th of 38), new businesses (2nd of 30) and new business
  density (4th); near the bottom for exports (34th of 35), manufacturing (31st of 32) and business R&D (26th of 35)
  (U66).
- **Three routes agree.** IP RAPID's standard patents are within 1.5% (Australian) and 2.2% (overseas) of the World
  Bank's, 1989 to 2024; the World Bank's trade mark series count classes, not applications (U67).
- **The attachments.** Australia is absent from the OECD's business demography, innovation and IP methods and IP tax
  regimes tables (U68). The GII 2026 ranks Australia 20th of 139 (inputs 13th, outputs 24th), strong in education and
  universities, weak in outputs and trade (U69). The United States files 41.9% of patent applications at IP Australia
  (2024) (U70); 7.0% of Australian inventions were US-owned in 2020 (U71). Most of Measuring What Matters is monthly
  copies of ABS series, and Closing the Gap mixes in projections, now marked (U72).

### 4.6 Industries (`industries`, U73 to U79)

The 19 ANZSIC divisions, FY1990 to FY2026, with IP assigned through probabilistic crosswalks, business counts, R&D,
wages and creative value added, and 1.4 million attached values.

- **Coverage.** Only IP covers every division and year; business counts cover FY2023 to FY2026 and business R&D one
  year, so Stage 2 compares patterns across 19 divisions, not models (U73).
- **The crosswalks.** They carry 98.42% to 99.73% of standard patents; a patent's division is nearly certain (median
  largest share 0.996), its subdivision less so (0.727) (U74).
- **IP by industry.** Manufacturing receives 90.78% of standard patents because the corpus's crosswalk leaves out
  services; trade marks spread (manufacturing 55.65%, professional services 11.05%), with a break in January 2002 when
  the Nice classes were split (U75). Australians file 7.87% to 17.29% of a division's patents, about half of goods
  divisions' trade marks and two-thirds to four-fifths of services' (U76).
- **Businesses, R&D and wages.** Construction (17.0%), professional services (13.0%) and property (11.4%) hold two in
  five businesses; manufacturing 3.2% (U77). Business R&D was $24.41 billion in 2023-24, 37.6% in professional
  services and 20.7% in manufacturing; wages rose 44.5% to 56.8% by division from FY2010 to FY2025 (U78).
- **The attachments.** 21.7% of businesses introduced a new good or service in 2023 (9.9% in agriculture to 31.9% in
  information media); 61.9% of businesses survived June 2022 to June 2026; the business survey flags 36.2% of its
  values for sampling error (U79).

### 4.7 Research institutions (`institutions`, U80 to U87)

130 institutions (44 universities, 11 public research agencies, 46 medical research institutes and other grant
holders) by ROR and calendar year, 1990 to 2026, linked through a reviewed list of names and ABNs.

- **Coverage.** Research output from 2010 (OpenAlex), ARC grants from 2001, NHMRC from 2013; IP in every year (U80).
- **The link.** 31,528 institution-rights, almost all matched by name and ABN together. Universities patent through
  commercialisation companies to very different degrees: UNSW 96.5% through NewSouth Innovations, Queensland 2.1%
  through UniQuest, Sydney and Monash under 1% (U81). Whether the list is complete is OQ11.
- **Research and grants.** Universities produce 86.8% of the institutions' works and the Group of Eight 45.35% (U82);
  the Group of Eight hold 66.3% of ARC and 63.5% of NHMRC funding, and industry-partner schemes take 9.7% to 29.2% of
  ARC funding a year (U83).
- **IP.** The institutions file a small, slowly rising share of standard patents filed from Australia (4.80% in 1990 to
  1994, 8.96% in 2020 to 2024); CSIRO files the most (481 in 2017 to 2026), and a quarter to a third are filed with
  others (U84).
- **Science and patents.** US patents cite the institutions' research, but 93.6% of the citations come from inventions
  with no Australian applicant or inventor; medical research institutes' works are cited most per work (107.7 per
  1,000 works, against universities' 43.26) (U85).
- **Contracts and place.** Universities hold 77.9% of the institutions' contract value (U86); 50.34% of the
  universities' standard patents carry a postcode with no residents, which closes the U49 question (U87).

---

## 5. Themes across the lenses

Read together, the profiles point to eight patterns. Each is descriptive: a shape in the data worth testing, not an
explanation.

1. **Two systems in one.** Patents are an overseas filers' system in Australia (U7, U13, U70, U66: 5th of 38 OECD
   members for non-resident patents), while trade marks, provisionals and second-tier patents are mostly Australians'
   (U7, U13). Overseas applicants come through the PCT and file widely (U90, U93); Australians themselves file mostly
   abroad (U70), yet nearly half of their own standard patents are filed only here (U93). Who benefits from each right
   (Q2) may differ sharply.
2. **Concentration at every level.** Firms (U44), places (U52), attorneys (U21), grants (U83), contracts (U46, U62)
   and institutions' patents (U84) are all dominated by a few. Averages will mislead; Stage 2 uses medians, logs,
   ranks and shares.
3. **Uneven access.** Individuals and regional areas stand out: individuals file alone (U20), file a fifth of the
   standard patents filed from Australia (U48), drove the provisional rise (U8) and file more of their patents only
   here (U93); R&D claimants are rarer outside the cities and more often have never filed IP there (U54); filers are
   more advantaged than firms in general (U47). About one inventor in seven in Australia is estimated to be a woman
   (U98). This bears directly on Q2 and Q4.
4. **Research without local invention.** Strong research inputs (GII inputs 13th, U69; universities 86.8% of works,
   U82) sit beside weak outputs (24th), falling business R&D (U65) and research cited mostly by foreign inventions
   (U85). Few foreign-filed inventions are made here (0.85%, U96), and Australians' patents are cited less (U94). The
   gap between research and Australian invention is a lead for Q1 and Q4.
5. **Policy leaves fingerprints.** Rushes, steps and pauses around rule changes (U28, U3, U33) offer before-and-after
   comparisons, the starting point for the natural experiments Q5 needs. Fees, the lever IP Australia holds most
   directly, are not yet in the data (R3).
6. **Signs of a right's value.** Lifetimes have lengthened for patents and shortened for trade marks (U36), and
   ownership changes are common (U17, U35). How widely a patent is filed and how often it is cited (U93, U94) add two
   more signs of private value (Q1), to read beside years in force, which is now a working measure.
7. **The record has a history.** System migrations, Acts and classifications change what is recorded: survivors and
   batch dates (U23), ownership history from FY2003 (U17), November 2018 (U34), the Nice 8th edition (U75), WIPO's
   unknown origins before 1995 (U64). Every comparison over time now has a stated safe window.
8. **Linkage is the binding limit.** Firms only through schemes and ABNs (U41, U45), industries only through
   crosswalks (U75), places only through postcodes (U49, U87), institutions through a reviewed list (U81), inventors'
   countries only for patents also filed abroad (U95), gender only as an estimate that holds for Australia (U97), and
   no firm-level outcomes for small firms (BLADE ruled out). These limits shape how far Q3 and Q5 can be answered.

---

## 6. Rules carried into Stages 2 and 3

The decisions Stage 1 made about how each variable may be used.

**Counting rights**
- Totals are always given by type of right; patent headlines use standard patents, with provisionals and second-tier
  patents apart (U4).
- Australian shares are compared from FY1990, and a design share is always shown with its unknown share (U7).
- Trade marks before 1983, designs before 1986 and provisionals before September 1985 are survivors, not filings (U23).
- Grant rates and times only for decided years: to FY2021 for standard patents, FY2024 for trade marks (U10, U12).
- "Where and who files" uses the founding applicant; "who holds" the current applicant (U19).
- Representation uses agents of five or more applicants, with bounds for trade marks (U20).
- For patents filed before FY2003, `assignment_count` stands in for a change of owner (U35).
- Lifetimes come from survival curves with unfinished rights kept; trade marks and designs are observed to 31 March
  2026 (U31, U36).
- Trade mark expedite shares are compared only on one side of November 2018 (U34).
- A patent priority's office is read from its number, not IP RAPID's label (U88); `filing_route` names the first route
  that applies (U90).
- A family's reach and citations are the whole family's, so they repeat across divisionals (U92); citations are
  compared as ranks or logs within cohorts, and the five-year count only where its window is complete (U92, U94).
- "Invented in Australia" is read among patents whose inventors' countries are known, which leaves out most patents
  filed only here (U95).
- Gender estimates are read as levels for inventors in Australia only; for other countries only within one country
  over time; for China and Korea not at all (U97).
- Comparisons with IP Australia's published figures use calendar years and `founding_australian` for residency; a
  design share among known origin is a lower bound; trade marks filed in 2018 are flagged (2.5% short in IP RAPID, in
  Madrid applications); second-tier counts include conversions from standard patents (ADR 0024).

**Over time**
- Changes, or months around events, not levels; months against the same month a year earlier, or 12-month totals
  (ADR 0006, U26).
- Series with a median under 10 a month are compared by quarter or year (U24).
- Pauses are pooled with their backlogs; rushes are studied, not removed; months before June 1904 are left out (U29).
- Money is deflated by the quarterly CPI, with the base stated (U30).

**Firms and places**
- Firms' IP counts are lower bounds; firm filing by year is compared only to FY2024 until the ABN linking question is
  answered (U41, U45).
- Firm counts use medians, logs or ranks, never means alone (U44); age is used with `age_truncated` (U43).
- Area rates are shown only where 10 or more applications would be expected; area counts are modelled with negative
  binomial models, pooled to SA3s and read beside the firms behind them (U52, U53).
- Business counts by area come from the ABR; CABEE gives size and industry, never compared with the ABR (U56).
- Census values are used as shares of whole groups, never single small cells (U57); Data by Region is never added to
  the Census (U58); PHIDU one period at a time (U60).
- An address is where a business is registered, not where it works (U47, U62).

**Countries, industries and institutions**
- WIPO by country from 1995; former states never added to their successors (U64).
- Counts across countries become ratios to people or GDP (U66); trade marks are compared as class counts (U67).
- Projections are filtered out by `status` (U72); a GII rank is context, its indicators the evidence (U69).
- Industry IP counts are expected counts: divisions near certain, subdivisions spread; trade marks by industry from
  FY2003 (U74, U75). `TOTAL` is never added to the divisions.
- Institutions' works and citations are never added across institutions, nor a child's to its parent's; a university's
  IP includes its companies; patent citations are compared by cohorts of the same age (U81, U82, U85).

---

## 7. What Stage 2 will test

The pairs worth testing, from the leads Stage 1 found. Each will need its effect size and interval, a correction for
the number of pairs tested, and a second period or sample before it counts as a lead.

| Lead | From | Question it serves |
|---|---|---|
| The provisional rise against policy and fee events, and IP Australia's own figures | U8 | Q4 |
| Before and after each policy change (two rushes, four steps, two pauses), with placebo dates | U28 | Q4, Q5 |
| Filing alone, and time to grant, by origin, applicant type and representation | U11, U20, U33 | Q2, Q4 |
| Years in force, family reach and citations by origin, applicant and technology, within cohorts | U36, U93, U94 | Q1 |
| The route into Australia by origin and applicant, and where inventions are made against who files them | U90, U96 | Q1, Q2 |
| Women's estimated share among inventors in Australia, by field and filer | U98 | Q2 |
| Rights moving overseas by technology, firm and age | U18 | Q1, Q2 |
| Firms' IP against their R&D, contracts, age and entity group | U41 to U46 | Q2, Q3 |
| R&D claimants who have never filed IP ('missing filers'), by place and industry | U54 | Q4 |
| Area filing rates against advantage, remoteness, the Census and business mix | U51, U53 | Q2 |
| Australia against OECD members, as ratios to people and GDP | U65, U66 | Q1, Q4 |
| IP per business by industry, beside the crosswalk's limits; innovation (BCS) against IP | U75, U77, U79 | Q2, Q3 |
| Research output against IP by institution (2010 to 2024); industry-partner grants against joint filing | U82 to U84 | Q1, Q3 |
| Expedited examination against years in force, as IP Australia's commissioned study found (ADR 0024) | U34, U36 | Q1, Q4 |
| Australian research cited by patents against Australian inventions that cite it | U85 | Q1, Q4 |

**Unexplained leads, kept in view:** Australians' direct filing of standard patents, 28.3% in FY2026 (U90; IP
Australia reads it as a real change among domestic innovators); the November 2018 fall in trade mark expedite requests
(U34, OQ6); ABN linking since FY2025 (U45, OQ7: a fall in linking, not filing, ADR 0024); the step in the World Bank's
advanced education share around 2010 (U65); rising holder changes for plant breeder's rights (U17); petty patents of
FY1986 to FY1988 without acceptances (U32). Closed by the audit: IP RAPID's innovation patents in 2016 (U67), a real
rise IP Australia reported.

---

## 8. Open items and data gaps

**For the owner** (`owner-questions.md`):
1. **What next:** Stage 1 is complete, so Stage 2 can begin when you say (the three `rights` attachments, OQ1, are
   done).
2. **A sector check of the institutions link** (OQ11): a half-hour review by someone who knows the sector, best done
   before Stage 2 compares institutions.
3. **The fee history and the PBS report** (OQ2): fees are IP Australia's most direct lever and are not yet in the
   data; recommended before Stage 2.
4. AusTender's missing amendments (OQ3, small) and TableBuilder (OQ4, on hold).

**For IP Australia** (the owner is asking): what evidence supports its reading that digital tools, including AI, drove
the provisional rise, and whether the few heavy filers are part of it (OQ5); why trade mark expedite requests fell in
November 2018 (OQ6); and whether ABNs are added to records later, or no longer collected or checked, since mid-2024
(OQ7). OQ5 and OQ7 were reworded after the audit against IP Australia's reports (section 10), which also added three
more (OQ12 to OQ14).

**Data worth adding, all free:** the RBA's cash and exchange rates and the ABS national accounts (timeline); the ATO's
statistics by postcode (regions); IP Australia's published statistics as a benchmark; ALP's crosswalk that includes
services (industries); WIPO's patent families by origin, to size the Australian inventions filed only abroad that
Google's selection misses (the review's F07). BLADE, the only route to small firms' outcomes, stays ruled out, and that
limit is stated wherever it bears on a finding.

---

## 9. What Stage 1 cannot tell you

- **Why.** Every observation is descriptive. Stage 1 shows when, how much and who, not what caused it. Associations
  come in Stage 2, and causal claims need designs (natural experiments) after Stage 3.
- **Value.** Counts of rights, lifetimes and citations are activity and use, not public value. The research goal
  treats them as indicators, not success.
- **Everyone.** The `firms` lens holds firms that used a scheme, not all businesses; individuals in IP RAPID are
  pseudonymised, so their gender cannot be estimated (only inventors' is, from Google Patents, and reliably only for
  inventors in Australia, U97).
- **Small firms' outcomes.** Without BLADE, firm-level growth and survival for small businesses are out of reach.

---

## 10. Checked against IP Australia's published evidence (27 October 2026)

After Stage 1 closed, its observations were audited against what IP Australia has published: the twelve Australian IP
Reports (2015 to 2026), its economic research papers and notes, as the Econ repository holds them
([`audit-ip-australia.md`](audit-ip-australia.md), ADR 0024). In short:

- **The counts are corroborated.** 195 figures IP Australia published were recomputed from the lenses on its own
  definitions (calendar years; a resident has a founding applicant in Australia); 155 agree within 2% (or 1 point).
  Standard patent applications agree in all 12 years from 2014 to 2025, within 0.34%; provisionals, grants, trade
  mark registrations, Madrid trade marks and the PCT route as closely.
- **Verdicts:** of the 99 observations, 23 are corroborated, 9 consistent, 1 disputed in part and 66 not testable from
  IP Australia's publications; none is contradicted.
- **Three readings change:** design shares among known origin are lower bounds, because IP Australia counts about three
  in four of IP RAPID's "origin unknown" designs as Australian (U7, U13); trade marks filed in 2018 are 2.5% short in
  IP RAPID, in Madrid applications (U5, U25); and U27's 2016 grant peak counts second-tier patents too.
- **Leads:** U67's 2016 innovation patents were a real rise IP Australia reported (closed); U45's fall in first-time
  filers is a fall in ABN linking (narrowed); U28 gains a response (Australians' standard patents brought forward in
  2021 by the innovation closure); U8 and U90 have IP Australia's published readings (digital tools; direct filing by
  domestic innovators).
- **Disputed:** IP Australia's "55.6% of resident applications were filed by individuals" (2022) cannot be reproduced
  (the lens: 20.65%); U13 and U48 stand meanwhile (OQ12).
- **In the atlas:** the review has its own page, "Checked against IP Australia" (ADR 0025); the observation pages and
  the notebook are unchanged until the owner decides to revise them.

---

## 11. Where to find things

| What | Where |
|---|---|
| Every observation, with its chart and the output it quotes | `analysis/notebooks/01_univariate.ipynb` (section summaries 1.9, 2.6, 3.6, 4.5, 5.7, 6.5, 7.7; section 9) |
| The plan, and where every table goes | `docs/eda-plan.md` |
| Status, leads and conventions for the next session | `docs/handover-eda.md` |
| Every decision and repair | `docs/adr/` (0001 to 0025) |
| The audit against IP Australia's published evidence | `docs/audit-ip-australia.md`; the benchmark in `analysis/audit/` |
| Questions for the owner and IP Australia | `docs/owner-questions.md` |
| Terms | `GLOSSARY.md` |
| How each lens is built, and its columns | `analysis/eda/build.py`, `analysis/eda/variables.yaml` |
| Known data quirks | `analysis/output/PROFILE.md`, `analysis/README.md` |

---

## Appendix: index of observations

All descriptive.

| # | Lens | Observation |
|---|---|---|
| U0 | Corpus | 162 tables, 41 sources, 317.8 million rows; three sources hold 69.73% |
| U1 | rights | One row per right (4,368,006), complete where it should be; origin known for 86.37% |
| U2 | rights | Five repairs: a 1970 placeholder, a pre-1904 registration, trade marks registered at filing, a class as a technology area, attorney use |
| U3 | rights | Rushes to file before two rule changes; 61,854 rights cannot be placed in time |
| U4 | rights | Trade marks are 53.5% of rights; standard patents 82.17% of patents |
| U5 | rights | Annual counts by type; second-tier patents end after FY2021 |
| U6 | rights | The latest years are complete |
| U7 | rights | About nine in ten standard patents from overseas; design origin often unrecorded |
| U8 | rights | Provisional applications doubled in FY2026, from individuals |
| U9 | rights | Lapsed is not ceased; 408,957 old patents of unknown status |
| U10 | rights | Grant rates by year: standard patents 54.4% to 75.5% |
| U11 | rights | Median 980 days to grant (standard patents), 223 to register (trade marks); a 222-day peak |
| U12 | rights | The typical time by year of application |
| U13 | rights | Who applied, FY2017 to FY2026: the United States 43.5% of standard patents |
| U14 | rights | Health fields lead patents (32.0%); class 35 leads trade marks |
| U15 | rights | New South Wales 38.2%, Victoria 23.7% of Australian standard patents |
| U16 | rights | The state repair; postcodes usable for 99.3% |
| U17 | rights | The holder is often not the filer; patents' history only from FY2003 |
| U18 | rights | More Australian-filed rights moved overseas than came the other way |
| U19 | rights | The filer's postcode differs from the holder's for about a tenth of rights |
| U20 | rights | Overseas filers almost always use an attorney; Australian individuals often file alone |
| U21 | rights | Patent attorneys concentrated (top five 63.96%); trade mark representation not |
| U22 | timeline | One row per month (1,473), each series where it can be read |
| U23 | timeline | 15 series started too early; the 1995 term change added |
| U24 | timeline | Steady large series, noisy small ones |
| U25 | timeline | Standard patents' growth slowed; trade marks and designs faster |
| U26 | timeline | Australians file less in January, increasingly for patents |
| U27 | timeline | Grants peaked in 2016; trade mark cessations keep rising |
| U28 | timeline | Two rushes, four steps, two pauses; several changes with nothing visible |
| U29 | timeline | 42 months stand out; explained and kept |
| U30 | timeline | The CPI is complete and quarterly from 1948 |
| U31 | rights (events) | The events columns rest on five checks |
| U32 | rights (events) | Each milestone is recorded from a different date |
| U33 | rights (events) | Patent examination lengthened to FY2006 and shortened since |
| U34 | rights (events) | More patent applicants ask for speed; trade mark requests fell in November 2018 |
| U35 | rights (events) | One standard patent in seven and one trade mark in five is assigned |
| U36 | rights (events) | Patents kept longer; about half of trade marks renewed at ten years |
| U37 | rights (events) | Extensions of term are rare: 1,450 |
| U38 | rights (events) | The 2002 trade mark trough explained |
| U39 | rights (events) | April design lapses explained |
| U40 | rights (events) | Placeholder dates are few and handled |
| U41 | firms | 398,450 ABNs that used one of five schemes; IP counts are lower bounds |
| U42 | firms | Private companies dominate every source but AusTender |
| U43 | firms | A median 13.6 years old on the record |
| U44 | firms | The top 1% of filing firms file 55.3% of standard patents |
| U45 | firms | Recent filers are less often linked to an ABN |
| U46 | firms | R&D claims spread; contract value concentrated |
| U47 | firms | Filers and R&D claimants more metropolitan and advantaged |
| U48 | regions | 2,641 postal areas, 25.4 million people; filer and holder differ for one right in fifteen |
| U49 | regions | One standard patent in eighteen from a postcode that is not a postal area |
| U50 | regions | Areas from no residents to 129,883 |
| U51 | regions | Most areas outside the cities, most people inside; SEIFA deciles are tenths of areas |
| U52 | regions | Top tenth of areas file 72.5% of standard patents; often one firm's |
| U53 | regions | Areas differ far more than chance |
| U54 | regions | Half of R&D claimants have never filed IP |
| U55 | regions | 22.5 million attached values |
| U56 | regions | Split values track direct ones; business counts from the ABR |
| U57 | regions | Census cells small and perturbed |
| U58 | regions | Data by Region varies by year and repeats the Census |
| U59 | regions | Most businesses employ no one, and the share is rising |
| U60 | regions | PHIDU's indicators are mostly rates for different periods |
| U61 | regions | Solar water heaters to panels to batteries |
| U62 | regions | Government contracts concentrated where suppliers have offices, above all the ACT |
| U63 | national | 30 indicators, 229 places; Australia's R&D people series end early |
| U64 | national | Before 1995 WIPO cannot say where most applicants come from |
| U65 | national | R&D intensity peaked in 2008; manufacturing fell twice as fast as the OECD's |
| U66 | national | Near the top for filings from abroad, near the bottom for exports and business R&D |
| U67 | national | Three routes agree on patents; the World Bank's trade marks count classes |
| U68 | national | 41.2 million attached values; Australia absent from five OECD flows |
| U69 | national | GII 2026: 20th of 139 |
| U70 | national | The United States files 41.9% at IP Australia; three-quarters of Australians' applications are abroad |
| U71 | national | The OECD's cross-border tables: the United States is Australia's main partner |
| U72 | national | Measuring What Matters mostly copies; Closing the Gap includes projections |
| U73 | industries | 19 divisions over 37 years; only IP covers all |
| U74 | industries | The crosswalks carry nearly every right; divisions clear, subdivisions less so |
| U75 | industries | Nine in ten patents in manufacturing (services left out); trade marks break in 2002 |
| U76 | industries | Australians file few patents in any industry |
| U77 | industries | Construction, professional services and property hold two in five businesses |
| U78 | industries | Business R&D $24.41 billion, concentrated in professional services and manufacturing |
| U79 | industries | 1.4 million attached values; innovation from 9.9% to 31.9% of businesses |
| U80 | institutions | 130 institutions; research output only from 2010 |
| U81 | institutions | The link by name and ABN; universities patent through companies to very different degrees |
| U82 | institutions | Universities produce 86.8% of works |
| U83 | institutions | The Group of Eight hold two-thirds of grant funding |
| U84 | institutions | The institutions file 4.80% to 8.96% of Australian-filed standard patents |
| U85 | institutions | US patents cite the institutions' research, 93.6% from inventions with no Australian link |
| U86 | institutions | Universities hold 77.9% of the institutions' contract value |
| U87 | institutions | Half the universities' standard patents carry a postcode that is not a postal area |
| U88 | rights (links) | Eight columns from the links; IP RAPID's PCT country label read past |
| U89 | rights (links) | The PCT route agrees with WIPO's count of national phase entries, year by year |
| U90 | rights (links) | Overseas applicants come through the PCT; Australians moved from provisionals to the PCT, divisionals and direct filing |
| U91 | rights (links) | Most overseas inventions first filed in the United States; Australians' PCT applications filed at home; marks taken abroad |
| U92 | rights (Google Patents) | The family of nearly every standard patent since the 1980s is found |
| U93 | rights (Google Patents) | Overseas applicants' patents belong to wide families; Australians' are mostly narrow |
| U94 | rights (Google Patents) | Citations are a long tail, and Australians' patents are cited less |
| U95 | rights (inventors) | Inventors are named, but their countries are missing for patents filed only in Australia |
| U96 | rights (inventors) | Inventions filed from Australia are made here; few filed from overseas are |
| U97 | rights (inventors) | Gender estimates match WIPO's for Australia, run high elsewhere, far too high for China and Korea |
| U98 | rights (inventors) | About one inventor in seven in Australia is estimated to be a woman |

## 11. IP Australia's register (added 2026-10-27, ADR 0028 and 0029)

IP RAPID was checked against IP Australia's live register, read through its APIs (`docs/audit-ipa-api.md`): it is
complete to within a week and its fields agree with the register's for nearly every record of a random sample. Its
gaps are in what it publishes, and the register fills them beside IP RAPID's own values (notebook 1.8.6, U99 to U104):

- **U45 restated (U100, U101):** with the register's business numbers, 92.3% of Australian organisations' trade marks
  have a filer's ABN in FY2024, 91.4% in FY2025 and 90.9% in FY2026 (IP RAPID: 84.1%, 71.4%, 59.9%); firms filing
  their first trade mark number 14,728, 15,818 and 19,730. Firm-level filing by year is now compared to FY2026.
- **U7 and U13 restated (U102):** designs filed FY2017 to FY2026 are 32.31% Australian with 0.007% of unknown origin
  (IP RAPID: 30.05% with 5.062%).
- **U34 restated (U103):** trade marks claiming convention priority carry an expedite event in every year, in IP RAPID
  to FY2018 and in the register from FY2019 (97.82% in FY2018 and 99.55% in FY2020 in either record).
- **U104:** 11,098 empty design records, numbered 1973 to 1982, are dropped and listed.

Every provisional application is being read from the register with its inventors, for a gender analysis; its profile
will be section 1.8.7.
