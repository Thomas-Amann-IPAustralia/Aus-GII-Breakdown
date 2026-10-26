# Handover: exploratory data analysis

For the next Claude Code session. Read `CLAUDE.md` first, then `docs/eda-plan.md`.

**The owner's decisions (2026-10-26):** complete the `institutions` lens (done: core, its IP detail and every source
mapped to it); before that, go on to the `industries` lens (done: core and attachments); before that, commence the
`national` lens (done). **(2026-10-25):**
after the `firms` lens, the owner asked for the `regions` lens to be
completed (done: core and attachments). Before that, after the events attachment, the owner adopted years in force (U36, with
unfinished rights kept) as a working measure for Stage 2, on condition that it is used alongside other signals, and
asked for the `firms` lens next. They will try to find out from IP Australia why provisionals rose (U8) and why trade
mark expedite requests fell in November 2018 (U34). Earlier: the events attachment (B5) before `firms`; N01 and N06
settled (ADR 0010).

**Status (2026-10-26, latest):** Stage 1 has its summary: `docs/stage-1-summary.md` gives the full account (the
goals, the process, each lens's findings, eight themes across the lenses, the rules carried forward, the pairs for
Stage 2, the open items and the limits, with an index of U0 to U87), and section 9 of `01_univariate.ipynb` holds the
short version (the key observations and the pairs carried into Stage 2). The notebook's status line is brought up to
date. Only markdown cells changed, so the notebook was not re-run. **Next is the owner's call: the remaining `rights`
attachments (OQ1) or Stage 2; OQ11 is best answered before Stage 2 compares institutions.**

Before that, on 2026-10-26: the `institutions` lens, the last planned, is built and complete for Stage 1, so
**every lens now has its Stage 1 profile**. Section 7 of `01_univariate.ipynb` profiles every column (U80 to U87),
ADR 0021. One row per research institution (its ROR identifier) and calendar year, 1990 to 2026 (4,810 rows): 44
universities, 11 public research agencies, 46 medical research institutes and 29 other grant holders. A new corpus
source, `ror` (every Australian ROR record, from ROR's data dump: its API pages unstably), keys it. The link from
institutions to IP RAPID, the ARC and AusTender is a reviewed list in `analysis/eda/institutions/` (130 institutions,
116 extra names, 146 ABNs), with the universities' commercialisation companies: UNSW files 96.5% of its patents
through NewSouth Innovations. The IP detail is a companion table, `institution_rights` (31,528 rows, joinable to
`rights`). The lens holds OpenAlex's works and citations (2010 on), US patents' citations to the institutions' works,
ARC grants (2001 on, industry-partner schemes apart) and NHMRC grants (2013 on), IP by type, the patents' families
(Google Patents) and AusTender contracts. Plant breeder's rights cannot be linked (their applicants are codes). The
profile also answers U49: half the universities' standard patents carry a postcode that is not a postal area. **Next is
the owner's call (Stage 1's summary, then Stage 2, or the remaining `rights` attachments); OQ11 asks whether someone
in the sector should check the link.**

Before that, on 2026-10-26: the `industries` lens is built and complete for Stage 1: section 6 of
`01_univariate.ipynb` profiles every column (U73 to U78) and every attachment (6.4, U79), ADR 0020. One row per ANZSIC
division and financial year, FY1990 to FY2026 (703 rows): IP applications as expected counts through the ALP
crosswalks (each right split over industries by probabilities), CABEE's businesses, entries and exits (FY2023 to
FY2026), BERD (2023-24), the WPI and BCARR's creative value added. Every value the ABS and BCARR publish by industry is
in a new long table, `industry_indicators` (1.4 million rows), and their Australia-wide tables went to
`national_indicators`. B6 is done (26 IPC predecessors), and a corpus repair: `concordances` split each ISIC class over
partial ANZSIC links, sending half of pharmaceuticals' weight to textiles and inorganic chemicals. Patents reach only
goods-producing industries (the crosswalk excludes services: manufacturing 90.8%), a lead for Stage 2. **Next is
`institutions`, the last planned lens, unless the owner says otherwise.**

Before that, on 2026-10-26: the `national` lens is complete for Stage 1: section 4 of `01_univariate.ipynb`
profiles every column (U63 to U67) after the repairs of ADR 0019, and every attachment (4.4, U68 to U72). WIPO's filings
by residents of former states (the Soviet Union, East Germany and four more) and of unknown origin are kept (they were
9.65% of patent applications by origin, and silently dropped), with a new column, `entity`. The attachments are a new
long table, `national_indicators` (41.2 million rows: every value of the GII 2026, the 24 OECD flows, WIPO's filings at
IP Australia by origin, its office table and PCT, Madrid and Hague counts, Measuring What Matters and Closing the Gap).
Two corpus repairs, by reprocessing: Closing the Gap's "Aus Gov" jurisdiction (85 values) and Measuring What Matters'
stacked tables (45 cells shared a key). Re-running the notebook also showed that the `rights` build broke two ties
arbitrarily (a founder's two same-day postcodes, an agent's several names), so a few figures in sections 1 and 3
changed from build to build; the ties are now fixed (ADR 0019, decision 6), two builds agree row for row, and five
quoted figures are corrected (U48, U49, U52, U53). **Next is `industries`, then `institutions` (the plan's order),
unless the owner says otherwise.** (Done: `industries`, above.)

Before that, on 2026-10-25: the `regions` lens is complete for Stage 1: section 3 of `01_univariate.ipynb`
profiles every column (U48 to U54) after the repairs of ADR 0017, and every attachment (3.5, U55 to U62, ADR 0018).
Applications are now counted at the filer's postcode; rates are a year, per 10,000 people and (organisations only) per
1,000 GST-registered businesses, and are empty where fewer than 10 applications would be expected at the national
rate; `sa3_code` allows pooling; and the filers' postcodes that are not postal areas are classed (S6): 5.55% of
standard patents, mostly universities' postcodes. The attachments are a new long table, `region_indicators` (22.5
million rows: every value of the Census, Data by Region, CABEE, PHIDU and the Clean Energy Regulator by postal area,
SA2 and PHA values split by 2021 residents), and three AusTender columns in `regions`.

Before that, the same day: the `firms` section (2) of `01_univariate.ipynb` profiles every column of that lens
(U41 to U47), after four repairs (ADR 0016): applications are counted by the filer's ABN (`founder_abn`), not the
current holder's; two new columns say what each firm holds (`n_held`, `n_held_in_force`); `in_iplord` flags the 50,790
ABNs that only IPLORD links to IP (their IP counts are 0, so firms' IP counts are lower bounds); and blank ABR states
are emptied (165 filled from the postcode). The profile found that recent filers are less often linked to an ABN
(Australian organisations' trade marks 84.1% in FY2024, 59.9% in FY2026): firm filing by year is compared to FY2024
for now.

Before that, the same day: the events attachment (B5) is built and profiled, as section 1.8.2 of
`01_univariate.ipynb` (U31 to U40, ADR 0015). Eleven columns join `rights` from `iprapid/events`: the date of patent,
the examination request (and whether expedited), acceptance, certification, first opposition, assignments (count and
first date), extension of term, and each right's lifetime (`in_force`, `years_in_force`), with rights still in force
counted as unfinished and compared by survival curves (`uni.kaplan_meier`). Trade marks and designs are observed to
31 March 2026, because their ends are recorded only after the six-month grace period. The profile also resolved two
timeline leads (U27, U29) and the placeholder-date check. **Next is `firms` (the owner's order).**

Before that, the same day: the `timeline` section (5) of `01_univariate.ipynb` now
profiles every column of that lens (U22 to U30), after one more repair (ADR 0014): 15 monthly series started too
early, on records where IP RAPID holds only the rights that survived until it was computerised (trade marks before
1983, designs before 1986, provisionals before September 1985), outcomes for some rights only, or events dated in
batches. Those months are now empty. The profile also found a policy change missing from the register, the rise of
the standard patent term from 16 to 20 years on 1 July 1995 (patent expiries all but stop for four years), now the
17th event, and corrected the register's note on the Patents Act 1990 (its term was 16 years).

Before that, the same day: the `rights` section profiled every core variable of its lens (U1 to U16, after five
repairs, ADR 0012) and its first attachment, the parties (1.8.1, U17 to U21, ADR 0013). The lens now has 41 columns:
12 describe who filed each right (the founding applicant), whether the holder has changed, the main agent and who
represents the filer (attorney, other agent or self). Profiling the parties found that IP RAPID keeps one set of
applicants for patents filed before FY2003, entered when records moved between systems, so a change of holder before
then cannot be seen; `holder_changed` is empty for them.

Earlier the same day: the last check before Stage 1 (ADR 0010, the lenses; ADR 0011, the corpus), after the
independent review (`docs/Aus-GII-Independent-Review-and-Action-Plan.md`, whose IDs A1–A8, B1–B12, F01–F42 and
N01–N07 are used throughout), the owner's decision that every dataset goes through all three stages (ADR 0007),
`abs_prices` and `abs_labour`, the inventors (ADR 0008) and the `rights` repairs (ADR 0009). TableBuilder is on hold,
and BLADE stays ruled out.

## Where things stand

- **Stage 1, `institutions` (section 7, every column).** What it found (all descriptive):
  - coverage (U80): 130 institutions, 1990 to 2026; works from 2010, ARC from 2001, NHMRC from the 2013 round,
    contracts in earnest from 2007; 84 institutions filed a standard patent, 112 a trade mark;
  - the link (U81): 31,528 institution-rights, almost all matched by name and ABN together; UNSW files 96.5% of its
    patent applications through NewSouth Innovations, Newcastle 72.8%, Adelaide 43.9%, Queensland 2.1%, Sydney and
    Monash under 1%; the few grants left unmatched are councils, foundations and networks outside the lens;
  - research (U82): universities 86.8% of works (2015 to 2024), the Group of Eight 45.35%, Melbourne 7.97%;
  - grants (U83): the Go8 hold 66.3% of ARC and 63.5% of NHMRC funding; industry-partner schemes 9.7% to 29.2% of
    ARC funding a year; medical research institutes 20.8% of NHMRC's;
  - IP (U84): the institutions file 4.80% (1990 to 1994) to 8.96% (2020 to 2024) of standard patents filed from
    Australia; CSIRO 481 in 2017 to 2026, the top five 47.4%; a quarter to a third filed with others;
  - science and patents (U85): medical research institutes' works are cited by US patents most (107.7 per 1,000
    works, 2010 to 2014; universities 43.26), but 93.6% of the citations come from inventions with no Australian
    applicant or inventor; 97.0% of the institutions' standard applications are found in Google Patents;
  - contracts (U86): universities 77.9% of the institutions' contract value, public research agencies 19.0%;
  - postcodes (U87): 50.34% of the universities' standard patents (FY2017 to FY2026) carry a real postcode with no
    residents; the institutions hold 71.58% of such codes.
- **Stage 1, `industries` (section 6, every column and attachment).** What it found (all descriptive):
  - coverage (U73): 19 divisions, FY1990 to FY2026; IP in every year, CABEE FY2023 to FY2026, BERD FY2024, the WPI
    from FY1998 (no agriculture), creative value added FY2016 to FY2025 (10 divisions);
  - the crosswalks (U74): 98.42% to 99.73% of standard patents carried and 99.8% of trade marks; B6 cuts unknown
    subclass marks from 12,143 to 71; a patent's division is clear (median largest share 0.996), its subdivision less
    so (0.727); a trade mark's division less clear (0.792);
  - IP by industry (U75): manufacturing 90.78% of standard patents (machinery 31.18%, chemicals 30.17%), no service
    division above 0.23%; trade marks manufacturing 55.65%, professional services 11.05%; trade marks break in
    January 2002 (Nice 8th edition, classes 43 to 45);
  - Australians (U76): 7.87% to 17.29% of a division's patents; 47% to 58% of goods divisions' trade marks, 67% to
    80% of services';
  - businesses (U77): construction 17.0%, professional services 13.0%, property 11.4%, manufacturing 3.2% (June
    2026); health care +30.7% since FY2023, agriculture −2.9%;
  - R&D and wages (U78): BERD $24.41 billion (2023-24), professional services 37.6%, manufacturing 20.7%; $142,100 per
    mining business; wages +44.5% (property) to +56.8% (utilities) FY2010 to FY2025;
  - attachments (U79): 1,409,875 values; 21.7% of businesses introduced a new good or service in 2023 (9.9%
    agriculture to 31.9% information media); 61.9% of businesses survived June 2022 to June 2026; BCARR's releases
    agree within 1.2%.
- **Stage 1, `national` (section 4, every column and attachment).** What it found (all descriptive):
  - coverage (U63): 30 indicators, 229 places, 1960 to 2025; Australia's researchers end in 2010, technicians 2008,
    the World Bank's R&D spending 2021 (the OECD's 2023); tertiary enrolment starts in 2015;
  - WIPO before 1995 (U64): 29% to 34% of patent applications by origin had an unknown origin to 1993 (1.12% in
    2024), 87% to 90% at IP Australia; Australians' filings abroad, and WIPO's grants and designs to them, near zero
    until 1994. WIPO by country is compared from 1995;
  - Australia over time (U65): GERD 1.26% (1990), 2.24% (2008), 1.68% (2023), against an OECD median of 1.85%; BERD
    0.91% (median 1.18%); manufacturing 13.7% to 5.32% of GDP (−61%, the median member −30%); IP payments exceed
    receipts in every year; two series breaks (advanced education 2009 to 2011, FDI 2005);
  - against OECD members (U66): near the top for non-resident patents (5th of 38), new businesses (2nd of 30) and
    new business density (4th); near the bottom for exports (34th of 35), manufacturing (31st of 32) and BERD (26th
    of 35);
  - three routes (U67): IP RAPID's standard patents are within 1.5% (Australian) and 2.2% (overseas) of the World
    Bank's, 1989 to 2024, and the World Bank's are WIPO's exactly; the World Bank's trade marks count classes
    (IP RAPID's classes 0.938 to 0.998 of it, its applications 0.545 to 0.659); innovation patents in 2016 1.331 times
    WIPO's utility models, a lead;
  - the attachments (U68): 41,203,167 values, 148,731 indicators (with the ABS's and BCARR's national tables, added
    with `industries`); no Australian values in the OECD's business
    demography, innovation and IP methods or IP tax regimes; venture capital ends for Australia in 2019;
  - the GII 2026 (U69): 20th of 139 (inputs 13th, outputs 24th); strengths in education and universities, weaknesses
    in outputs and trade; 6 indicators missing and 8 outdated for Australia (the median economy: 6 and 9);
  - WIPO (U70): the United States files 41.9% of patent applications at IP Australia (2024), Australia 8.3%, China
    8.3% (0.3% in 2004); 76.1% of Australians' applications are abroad; IP Australia's average trade mark time to
    registration was 222 days (2016), the U11 peak;
  - the OECD's cross-border patents (U71): the "World" partner is the country's total (2,117 PCT applications
    invented in Australia, 2015); 7.0% of Australian inventions were US-owned in 2020;
  - Measuring What Matters and Closing the Gap (U72): 3,767 of 5,159 MWM values are monthly copies of ABS series; 353
    Closing the Gap values are projections and 443 model estimates, marked in `status`.
- **Stage 1, `regions` (section 3, every column and attachment).** What it found (all descriptive):
  - coverage (U48): 2,641 postal areas, 25,365,506 people; the filer's postcode differs from the holder's for 6.05% of
    standard patents and 7.6% of trade marks (FY2017 to FY2026); individuals file 21.53% and 24.97%;
  - the postcode check (U49): 94.45% of standard patents' filer postcodes are postal areas; 4.14% are real codes with
    no residents, led by universities' (2052 UNSW's NewSouth Innovations, 3800 Monash, 2006 Sydney, 3010 Melbourne,
    2109 Macquarie, 5005 Adelaide, 4072 Queensland); 1.39% post office box ranges. They stay in state totals;
  - people and businesses (U50): median 3,508 people; 818 areas under 1,000 people (1.33% of people); 18 areas have
    more businesses than residents (industrial estates, business districts);
  - remoteness and SEIFA (U51): major cities 37.7% of areas, 72.8% of people; SEIFA deciles are tenths of areas;
  - concentration (U52): the top tenth of areas file 72.5% of standard patents with 29.0% of people; one firm files
    76.3% of 2113's (Aristocrat), 88.1% of 2601's (CSIRO), 64.1% of 2153's (ResMed);
  - rates against chance (U53): 68.2% to 72.5% of areas fall below the funnel's 95% limits and 6.7% to 15.5% above,
    for postal areas and for SA3s alike: far more spread than chance, so Stage 2 uses negative binomial models;
  - R&D claimants (U54): 50.7% have never filed IP; 5.6 claimants per 1,000 businesses in major cities, 0.6 in very
    remote areas;
  - the attachments (U55, U56): 8,874 indicator-periods, nearly every one for nearly every area; split values track
    direct ones (Data by Region's 2021 population within 10% of the ASGS count for 99.34% of areas); CABEE counts
    0.742 of the ABR's businesses, in the same order (Spearman 0.988), so business counts come from the ABR;
  - the Census (U57): small cells (51.1% of industry-by-age cells are 0) and perturbation (males plus females equal
    persons in 10.9% of areas); Data by Region (U58) repeats Census items; CABEE (U59) non-employing businesses 61.3%
    to 63.6% (June 2023 to 2025); PHIDU (U60) 54.14% levels, periods differ; the CER (U61) solar water heaters to
    panels to batteries (from July 2025); AusTender (U62): the ACT holds 27.0% of contracts, 1.3% of businesses.
- **Stage 1, `firms` (section 2, every column).** What it found (all descriptive):
  - who is in it (U41): 398,450 ABNs, 63.68% in IP RAPID alone, 13.69% AusTender alone, 12.75% linked to IP by IPLORD
    alone; active ABNs from 47.02% (IPLORD-only) to 95.35% (IP and R&D); IPLORD's own counts differ from IP RAPID's
    (81.02% agree; 99th percentile 7 times), so they are not used;
  - entity types (U42): private companies are 74.7% of firms, 82.2% of IP filers, 94.5% of R&D claimants and 55.3% of
    government suppliers;
  - age (U43): median 13.6 years on the record; 5,279 firms first seen on 1 November 1999, the ABN's start;
  - IP use (U44): medians of 1 application; the top 1% of filing firms filed 55.3% of standard patents and 25.9% of
    trade marks; 116,240 firms hold 430,305 rights in force;
  - ABN linking (U45): first-time trade mark filers fell from 11,318 (FY2024) to 7,384 (FY2026), but the share of
    Australian organisations' trade marks with a filer's ABN fell from 84.1% to 59.9%: a lead, and a question for IP
    Australia;
  - money (U46): R&D claims median $307,490 (top 1%: 28.1%); contract value concentrated (top 1% of suppliers: 83.1%);
  - place (U47): IP filers and R&D claimants more metropolitan (87.1%, 89.9% against 85.2%) and advantaged (decile 10:
    39.3% of R&D claimants against 34.0% of firms); the ACT has 9.7% of government suppliers.
- **Stage 1, `rights`, events (1.8.2).** What it found (all descriptive):
  - the checks (U31): the grant event is `registered_date` (99.99%); patent assignments are published twice (99.78%),
    counted once; 4.76% of patent lapse events were later reversed (not standing); a trade mark's term runs from its
    earliest filing date (92.19% of ceased Madrid-type marks end on a whole year from it); a patent's cessation falls
    6 to 7 months after an anniversary (84.59%), so its years in force include the grace period; 3,154 placeholder
    and 171 pre-filing events left out;
  - each milestone is recorded from a different date (U32): patents' examination requests from the early 1980s'
    filings, trade marks' acceptances from the mid-1980s' (30.88% of the 1980s', 75.88% to 79.05% since 2000), designs'
    examination requests only from 2013;
  - times (U33): a standard patent's examination request to acceptance took up to 755 days (FY2006), 422 to 516 since
    FY2014; FY2013's applicants asked for examination 44 days after filing (Raising the Bar); trade marks are accepted
    52 to 184 days after filing (FY2005 to FY2021);
  - expedited examination (U34): standard patents 1.87% (FY2005) to 10.31% (FY2026); trade marks 16.67% to 19.69% to
    FY2018, then 3.08% to 3.97%, the fall in November 2018 (about 1,400 requests a month to about 230), when the trade
    mark records moved between systems: a lead. Oppositions: 1.98% to 2.93% of accepted trade marks; 0.14% to 0.38%
    of standard patents since FY2015;
  - assignments (U35): 15.1% of standard patents and 18.1% of trade marks filed in the 2000s; from FY2003, 64.68% to
    74.66% of patents whose holder changed have one, and the assigned share runs on smoothly across FY2003 (15.4%,
    16.41%), so `assignment_count` measures a change of owner for patents filed before then;
  - lifetimes (U36): standard patents' median years in force rose from 10.7 (1980s) to 13.5 (2000s and 2010s); 21.3%
    of the 2000s' were kept to their 20-year end. 46.9% to 56.4% of trade marks were in force after 10 years (1990s to
    2010s), against 67.3% of the 1983 to 1989 marks (a 7-year first term). Designs renewed at 5 years: 64.8% (2000s),
    58.0% (2010s). Innovation patents: median 3.5 years;
  - extensions of term (U37): 1,450 standard patents (0.24% of those granted), 108 and 114 in 1999 and 2000;
  - the 2002 trade mark lead (U38): cessations at 7 years (the 1955 Act's first term) stop in 2002 (14) before those
    at 10 years (the 1995 Act's) build up (1,167 in 2003); 10,247 of 2002's lapses are of marks filed in 2000, the
    filing peak (42,907);
  - the April design lapses (U39): 101 lapses on 32 days in April against 365 to 671 on 56 to 91 days in other months,
    with filings and lapse shares (18.1% to 21.6% per filing month) even: how lapses were dated;
  - placeholders (U40): 3,162 of 49.35 million events, 34 links, 105 party start dates. Closed.
- **Stage 1, `timeline` (section 5, every column).** What it found (all descriptive):
  - the repair (U23): never registered, 2.0% of trade marks filed in early 1981 against 52.0% from 1983; patent
    cessations dated in batches to April 1995 (29.8% of months empty); grants recorded only for patents filed from
    1979 (68.5% against 1.0% to 1.9%). The rights lens is unchanged; counts by year of filing before those dates are
    survivors, and section 1's U5 and U10 now say so;
  - growth (U25): standard patents 3.9% a year in the 1990s, 1.3%, 2.0% and 0.4% (2019 to 2025), set by overseas
    applicants; trade marks 4.3% and designs 5.5% a year since 2019, designs almost all from overseas; falls in 2009;
  - seasons (U26): Australians file 25% to 34% less in January (2010 to 2019); overseas applicants 5% to 10% less. The
    lull is deepening for Australian standard patents (80 in the 1990s to 73 since 2020) and provisionals (73 to 63).
    Registrations and grants follow the office's calendar;
  - outcomes (U27): patent grants peaked in 2016 (25,687); trade mark cessations rose to 35,484 (2025); a lead in
    2002 (trade mark cessations 3,773, lapses 16,718);
  - policy changes (U28): two rushes (Raising the Bar, 4.39 times for Australians; the innovation closure, 4.31 times,
    then −95.9%), four steps (the term change −98.4% for expiries; the 1999 extension regime; the innovation patent's
    introduction +71.5%; the Designs Act 2003, overseas +34.1%), two pauses at commencement (the Patents Act 1990, the
    Trade Marks Act 1995), and nothing visible for PCT accession, plain packaging, the 2018 and 2019 PC responses, or
    the designs grace period;
  - artefacts (U29): 42 months stand out after the repair; none is removed. Pauses and backlogs (patent cessations 7
    in February 2020, 2,468 in March), the register's start-up before June 1904, a portfolio transfer in July 2015;
  - the CPI (U30): 312 quarters from 1948, none missing; base the month of September 2025.
- **Stage 1, `rights`, parties (1.8.1).** What it found (all descriptive):
  - the holder is not the filer for 22.0% of standard patents filed in the 2000s (from FY2003), 17.1% of the 2010s'
    and 7.0% of the 2020s'; trade marks 20.8%, 15.7% and 10.4%;
  - more Australian-filed rights moved overseas than came the other way: standard patents 2,036 against 804, trade
    marks 15,391 against 4,840;
  - the filer's postcode differs from the holder's for 10.1% of standard patents and 11.13% of trade marks (FY2003 to
    FY2026), almost always within a state;
  - overseas filers use an attorney for 99.0% of standard patents; Australian filers for 85.4%, and Australian
    individuals file 62.4% of their trade marks alone. The attorney share of trade marks depends on the threshold
    (Australian: 57.08% at one applicant, 49.67% at five, 42.59% at 100);
  - patent attorneys are concentrated (top 5 handle 63.96% of standard patents; 4 handle half), trade mark
    representation is not (top 5: 17.51%).
- **Stage 1, `rights` (done for its core variables).** What it found (all descriptive):
  - about nine in ten standard patents come from overseas (91.3% in FY2017 to FY2026; 7.9% to 12.4% Australian in
    the years shown since FY1990); the United States alone files 43.5%;
  - provisional applications doubled in FY2026 (10,069), from individuals without ABNs: distinct ABNs stayed flat at
    1,361, single-filing individuals rose from 1,538 to 2,507, and 54 individuals filed 10 or more each (one filed
    375). Monthly filings peaked in March and April 2026 and eased by September 2026;
  - Australians file without an attorney far more often than overseas applicants (trade marks 57.02% with one,
    against 96.27%); 12% to 22% of Australian organisations' rights carry no ABN;
  - registration takes a median 980 days for standard patents and 223 for trade marks (filed FY2010 to FY2019), with
    a sharp peak at about 222 days for trade marks: a lead;
  - the standard patent grant rate fell from 75.5% (FY2000) to 54.4% (FY2008) and recovered to 65% to 69%;
  - "unknown" status is 408,957 old patents (FY1904 to FY1999) whose outcome was never recorded; only 68.9% of
    expired patents have a grant date;
  - design origin is often unrecorded (4.0% to 6.3% unknown since FY2018, and rising), so design shares need care.
- **Seven lenses and four companion tables are built** (`analysis/eda/build.py`), in about two minutes:
  - `rights`: 4,368,006 rows, 52 columns (29 core, 12 from the parties, 11 from the events);
  - `firms`: 398,450 rows, 40 columns (ADR 0016: `n_held`, `n_held_in_force`, `in_iplord`);
  - `regions`: 2,641 rows, 42 columns (ADR 0017, 0018);
  - `region_indicators`: 22,511,923 rows, 10 columns, 173 MB (the `regions` lens's attachments, long; ADR 0018);
  - `national`: 135,597 rows, 11 columns (ADR 0019: `entity`);
  - `national_indicators`: 41,203,167 rows, 15 columns, 264 MB (the `national` lens's attachments, long; ADR 0019,
    0020);
  - `industries`: 703 rows, 17 columns (ADR 0020);
  - `industry_indicators`: 1,409,875 rows, 12 columns, 8 MB (the `industries` lens's attachments, long; ADR 0020);
  - `institutions`: 4,810 rows, 30 columns (ADR 0021);
  - `institution_rights`: 31,528 rows, 7 columns (the `institutions` lens's IP, one row per right and institution);
  - `timeline`: 1,473 months, 35 columns.

  Every planned lens is built (ADR 0007). Every table has a lens to attach to; the map is in `docs/eda-plan.md`.
- **The lenses' repairs (ADR 0010):**
  - `rights`: `earliest_filed_date` (for a PCT filing, `application_date` is the date it entered the national phase);
    attorney use is unknown, not "no", for provisionals, for which IP RAPID publishes no agents;
  - `firms`: contracts counted once each, at their latest notice; R&D from the latest report, amended where it was
    (−$153 million, −0.34%); `age_basis` and `age_truncated`; `ip_filed_weighted` beside `ip_filed_total`, whose
    label now says it counts an application once per founding applicant; super funds named;
  - `regions`: Census medians of 0 (no one to describe) are empty;
  - `national`: trade marks by residents and non-residents (the World Bank's current codes), the OECD's R&D intensity
    beside the World Bank's (never spliced), one name per country, and the OECD's flag on each value (`status`);
  - `timeline`: every series empty, not 0, before its records become continuous and in the months the register is
    still recording; trade mark registrations by the date entered, from January 1986 (they were counted at filing);
    each event once; the quarterly CPI; 16 policy events, every date checked against the Federal Register.
- **The corpus's repairs (ADR 0011):**
  - AusTender: each notice keeps its own id and amendment number, and the bulk file's contracts still running when
    it closed were asked for by id: 28,698 later amendments to 10,494 of them, whose value at the latest notice
    rises from $179.5 billion to $303.7 billion. Summing every notice gives $7,585.9 billion, against $1,258.5 billion
    with each contract once at its latest notice. `value_jump` flags 70 values that look keyed in the wrong units (8
    of them a contract's latest), and `published_batch` the dates that are a batch re-release's;
  - the ABN spine holds every IP applicant's or owner's ABN (6,466 more), so 11,525 rights no longer fall out of
    `firms`;
  - RDTI: 521 rows ($228 million) take their ABN from their ACN;
  - every value kept: the OECD's IP tax regimes (2,639 values, mostly text), the ABS cubes' footnoted and unpublished
    cells, and 5,181 World Bank trade mark values under the current codes;
  - one row per key: CER (7.05 million rows were 3.49 million values, each read twice), PHIDU (sub-indicators and
    area types restored, and a PHA-to-SA2 table), CABEE's survival rates by size, the ARTG.
- **Settled (descriptive, ADR 0010; confirmed by the owner, 2026-10-25):** the register does not drop provisional applications once a full application
  claims them (N01, refuted), so FY2026's jump to 10,069 provisionals is real; `application_date` for a PCT filing is
  the date it entered Australia's national phase (N06).
- **Corrected on 2026-10-26** (ADR 0020): the corpus's ISIC-to-ANZSIC step, which split each ISIC class over its
  partial links (textiles had 8.9% of patents, now 2.3%).
- **Corrected on 2026-10-26** (ADR 0019): the `rights` build's arbitrary ties (founders' same-day postcodes, agents'
  names), which made five quoted figures in U48, U49, U52 and U53 differ from a fresh build; and the World Bank's
  trade mark series, which the register described as applications but which count classes (U67).
- **Corrected on 2026-10-25** (each in the record as well):
  - the plan to ask AusTender's API for notices by the date last modified: its windows from July 2023 page back
    through every older contract, so it was replaced by asking for the running contracts by id. The draft of ADR 0011
    had said the 2019 to 2023 amendments could not be recovered; asking by id recovers them;
  - the draft of ADR 0010 said repeated events were at most 0.2% of any series: design lapses lose 1.9%;
  - "Contract value at latest amendment" was described as the most a contract was worth; an amendment can lower it;
  - the trade mark registration series' months before 1986 counted filings, with a false hole in 1983 to 1985.
- **Corrected this session (the timeline):** the policy register's note that the Patents Act 1990 brought in 20-year
  patents (it was 16 years until 1 July 1995); and section 1's U5 and U10, whose charts showed survivors' counts and
  registration rates for the years before 1983 (trade marks) and 1986 (designs) without saying so.
- **Tests (institutions):** 86 pass; new: one row per key in both tables, the reviewed link's integrity (every
  institution, name and ABN a ROR record, each ABN one institution, no name key two institutions), the name key
  across spellings, and the lens carrying its grants (all but 14 of the ARC's and 15 of the NHMRC's) and its IP links.
- **Tests (industries):** 79 pass; new: one row per key in both tables, the division of a class or subdivision code,
  each right's shares summing to one, CABEE's divisions summing to its total, BERD's divisions to its total.
- **Tests (national):** 73 pass; new: WIPO's applications by residents sum to the source's total, no aggregate is a
  place, the OECD's R&D intensity is held once, WIPO's filings at IP Australia sum to the office's total, Australia's
  GII rank is the source's, Closing the Gap keeps the Australian Government's values; one row per key in
  `national_indicators`.
- **Tests (regions):** 69 pass; new: the postal-area counts equal the window's rights with a filer's postcode, no
  rate shown below the minimum or hidden above it, the Poisson interval, the postcode ranges, one row per key in
  `region_indicators`, CABEE's split businesses sum to the published total, no level marked as a count.
- **Tests (firms):** 63 pass; new: the filing counts sum to the rights with a filer's ABN, holdings, states.
- **Tests (events attachment):** 62 pass; new: the events columns' dates, types and lifetimes, and the survival
  helper against a hand count.
- **Tests (before):** 60 pass (the lens tests skip unless the lenses are built); lint is clean. New: each hand-set timeline
  start, no batch gaps inside a series, and the new policy event's date.

## Next, in order

1. **The owner's call:** every lens has its Stage 1 profile, and the stage's summary is written
   (`docs/stage-1-summary.md`, section 9 of the notebook). What remains of Stage 1 is the `rights` attachments below;
   then Stage 2. OQ11 (a sector check of the institutions link) is best
   answered before Stage 2 compares institutions.
2. **Done:** the `national` section (U63 to U72, ADR 0019), the `industries` section (U73 to U79, ADR 0020) and the
   `institutions` section (U80 to U87, ADR 0021), each with its attachments.
3. **The rest of the `rights` attachments, as sub-sections of 1.8, when the owner says:** the links (with the PCT
   country check), Google Patents (B4), and the inventors (gender estimates checked country by country against WIPO's
   published shares, above all China and Korea).
4. **Done:** the `timeline` section (U22 to U30, ADR 0014), the events attachment (U31 to U40, ADR 0015), the `firms`
   section (U41 to U47, ADR 0016) and the `regions` section with its attachments (U48 to U62, ADR 0017, 0018). The
   `firms` lens's later attachments (filing histories by year from `applicant_year`; its rights' lifetimes and
   assignments) become sub-sections of section 2 as each is built.
5. **The plan's "high value, little work" additions, with the lens each serves:** the RBA's cash rate and exchange
   rates and the ABS national accounts (timeline), the ATO's statistics by postcode (regions), and IP Australia's own
   published figures as a benchmark (which would also test the provisional rise, U8, and the trade mark expedite fall,
   U34).

## Open items

1. Leads for Stage 2:
   - fewer recent filers are linked to an ABN (U45): Australian organisations' trade marks 84.1% (FY2024) to 59.9%
     (FY2026). Late linking, or ABNs collected less? Firm filing by year is compared to FY2024 until known;
   - trade mark requests for expedited examination fell from about 1,400 a month to about 230 in November 2018, when
     the trade mark records moved between systems (U34): recording or practice? IP Australia's published figures
     could tell;
   - petty patents filed FY1986 to FY1988 mostly lack an acceptance, though many were registered (U32);
   - resolved (U38, U39): the 2002 trade mark trough (the change from 7-year to 10-year first terms, and the 2000 filing
     peak) and the April design lapses (how lapses were dated);
   - trade mark oppositions rise from 0 to 16 a month (1983 to 1987) to 20 to 40 (1988): left as recorded (ADR 0014);
   - the months before June 1904 are a start-up (applications lodged before the Patents Act 1903 took effect).
   - the regional spread of filing is far more than chance, at postal areas and SA3s (U53), and a few areas' patents
     are one firm's (U52): Stage 2 reads area counts beside their firms, with negative binomial models;
   - universities' postcodes are not postal areas (U49): their filings are missing from postal-area counts. A lookup
     that places these postcodes (GeoNames, free) only if Stage 2's regional results prove sensitive;
   - the ACT holds 27.0% of government contracts against 1.3% of businesses (U62), and South Australia 12.2% of their
     value against 6.1%: where contracts are addressed, to read beside the firms behind them.
   - IP RAPID's innovation patents filed in 2016 are 1.331 times WIPO's utility models (2,469 against 1,855; other
     years 0.958 to 1.072, U67): how WIPO counted divisionals or conversions that year?
   - the World Bank's share of the labour force with advanced education steps up to 86.33% in 2010 for Australia
     (80.42% in 2008, 82.09% in 2015), a break the OECD median does not show (U65): use with care.
   - Australia ranks near the bottom of the OECD on business R&D, exports and manufacturing, and near the top on
     filings from abroad and new businesses (U66): Stage 2 compares them as ratios to people and GDP.
   - patents reach only goods-producing industries because the corpus's ALP crosswalk excludes services (U75): ALP
     publishes a version that includes services (free); whether to use it, beside or instead, is a Stage 2 choice;
   - trade marks by industry break in January 2002 (the Nice 8th edition, U75): compare from FY2003;
   - the BCS flags 36.2% of its values for sampling error and withholds 25% (U79): division comparisons need care.
   - US patents cite Australian institutions' research, but 93.6% of the citations come from inventions with no
     Australian applicant or inventor (U85): the research-to-invention link runs mostly abroad (Q1);
   - medical research institutes' works are cited by patents two and a half times as often per work as universities'
     (U85), and the institutions' joint filing (a quarter to a third of standard patents, U84) is a measure of
     collaboration to set beside the ARC's industry-partner grants (U83);
   - the universities' patents outside the postal areas (U87) can be placed through `institution_rights` and ROR's
     locations, replacing the GeoNames lookup in the item above, if Stage 2's regional results prove sensitive.
2. Check in Stage 1 (the placeholder dates are done, U40):
   - IP RAPID's `links.linked_application_country`, which labels every PCT number `au` (`analysis/README.md`), with
     the links attachment;
   - the 222-day peak in trade mark registration times (U11): WIPO gives IP Australia's average time from filing to
     registration as 222 days in 2016 (U70), so the peak is the office's usual path. IP Australia's own process
     times would confirm it for other years.
3. Settled by the parties attachment (ADR 0013): `representation` separates attorneys (agents of five or more
   applicants) from other agents. For trade marks the share still depends on the threshold, so Stage 2 gives bounds.
   Attorney firms' corporate groups are not recorded, so concentration by firm name is a lower bound.
4. Plant breeder's rights: their holder changes rise in recent years (11.2% of those filed in the 2020s, more than in
   any earlier decade), against every other type. Unexplained.
5. AusTender: amendments after August 2019 to bulk-file contracts that had ended by then are not in the corpus. A
   sample suggests they are under 1% of the contracts' value; `austender._harvest_by_id` can fetch them in about a day.
6. Fee history (R3) and the PBS monthly report with Section 100 (B9) are the biggest data gaps for the later stages.
7. The `coalesce` in `iprapid.py` that caused the origin problem (ADR 0009) is left until IP RAPID is next rebuilt; no
   lens reads that column.
8. The corpus profile (`analysis/output/`, `analysis/profile_corpus.py`) predates the `ror` source, so
   `data.corpus_columns("ror", ...)` finds nothing until the profile is next run in full (its `--only` replaces the
   CSVs rather than adding to them).

## For the owner

The owner's questions are kept in **`docs/owner-questions.md`**: open ones (OQ1 to OQ4), those the owner is asking IP
Australia (OQ5 to OQ7: the provisional rise, the trade mark expedite fall, ABN linking since FY2025), deferred ones,
and every answer with its date. Nothing there blocks Stage 1. Add new questions there, and move answers to its
"Answered" table.

## Conventions to keep

- Commit the code, run the notebook, then commit the notebook with its outputs.
- Never print raw rows. Aggregate in DuckDB.
- After a parser fix, `corpus reprocess <source>` rebuilds its tables from the raw files it holds, keeping the data's
  vintage (ADR 0011).
- The `rights` section's cells are long; keep each new sub-section to a few cells, and the notebook under about
  25 MB (ADR 0002 says when to split it).
- `region_indicators` is 22.5 million rows: always filter by `source` and `indicator` in SQL, never load it whole.
- `national_indicators` is 41 million rows: always filter by `source`, `dataset` and `indicator` in SQL.
- Compare WIPO's series by country from 1995 only (U64), and filter `entity = 'country'` for comparisons between
  countries.
- `industry_indicators`: filter by `source` and `indicator`; never add `TOTAL` to the divisions.
- `institutions`: never add works or citations across institutions as if distinct, or a child's (Data61's) to its
  parent's; count a university's IP with its companies (the link does); compare patent citations by cohorts of the
  same age.
- Corrections to the institutions link go in `analysis/eda/institutions/*.csv`; `uv run python -m eda.build
  institution_rights institutions` rebuilds both in seconds, and the tests check the link.
- Next free ADR: 0022.
