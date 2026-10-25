# 0010: Lens definitions, version 2: the last repairs before Stage 1

**Date:** 2026-10-25. **Whose:** Claude's, in the last check before Stage 1 (the owner asked for an in-depth review,
with every gap that can be easily filled filled, and every transformation made explainable and defensible); the owner
can overturn any of it. It carries out the review's A1, A3, A5, A6, A7 and A8 and the lens half of B2, settles N01 and
N06, and fixes problems this check found. It changes ADR 0005 (lens definitions), ADR 0006 (the timeline) and
ADR 0009 (the rights repairs). The corpus repairs behind it are in ADR 0011.

**Context.** ADR 0009 repaired the `rights` lens. The other lenses' repairs from the review were still open, and this
check, which read every lens definition against the corpus, found more: trade mark registrations counted at the wrong
date, series that end on a cliff because the register records them late, a firm measure whose documentation
described a different measure, and attorney use recorded as "no" where IP RAPID publishes nothing.

**Settled (descriptive; N01 and N06 confirmed by the owner, 2026-10-25).**
- **N01, refuted.** The review's hypothesis was that the register drops a provisional application once a complete
  application supersedes it. It does not: of the provisionals that standard patents claim as priority (Australian
  provisional numbers, YYYY9NNNNN), 99.9% to 100% are in the register in every financial year from 2000 to 2026. The
  jump in FY2026 (10,069 provisionals against 4,143 to 5,047 a year in FY2022 to FY2025) is real and broad: 5,165
  distinct applicants against 3,361 in FY2025, and 5,399 provisionals by individuals against 1,926. Its cause is
  outside the data (a lead for Stage 1).
- **N06, answered.** For a PCT application, IP RAPID's `application_date` is the date it entered Australia's national
  phase (614,950 of 614,951 PCT-route standard patents have it equal to the national-phase entry event), a median 909
  days after the priority date. Its `earliest_filed_date` is the international filing date (a median 364 days after
  priority). That is why recent years show no drop-off: the counts are of filings in Australia, by date of entry.
- **Second-tier patents after the closure.** 768 innovation patents have application dates from 26 August 2021, when
  new filings closed: the divisionals and conversions of earlier applications that the transitional rules allow. They
  are real, not errors.

**Decision.**
1. **`rights`.**
   - `earliest_filed_date` is added beside `application_date` (above). `application_date` and `filing_fy` are
     unchanged; their notes now say what the date means for PCT filings.
   - `has_agent` is empty (unknown) for provisional applications, because IP RAPID publishes no agents for them: no
     provisional has an agent row in the party table, while 71% of standard patents do. Before, all 264,024 read
     "filed without an attorney".
2. **`firms`.**
   - Contracts (A1): from the repaired spine, each contract counted once, at its latest notice, for the supplier that
     notice names (ADR 0011). Relabelled "Contract value at latest amendment": each contract's total over its whole
     life as last amended (an amendment can lower it), not spending in a year.
   - R&D claims (A5): each ABN-year's value is the latest report's, amended where it was, instead of the largest of the
     reports. This changes 936 of 38,290 ABN-years and the total by -$153 million (-0.34%). The tax transparency
     income likewise takes the latest report's value (2 ABN-years were restated).
   - Age (A6): `age_years` is relabelled "years since earliest public registration". `age_basis` says which register
     set `first_seen` (ASIC, the ABN status date or GST registration), and `age_truncated` flags a business first seen
     through its ABN or GST date before 2001: ABNs and GST began in 1999-2000, so such a business may be much older.
   - `ip_filed_total` was documented as splitting shared rights (ADR 0005, `variables.yaml`), but it counts each
     application once for each founding applicant (28,329 firms differ). Its label now says so, and the split version
     is added as `ip_filed_weighted`, which sums over firms to the number of rights.
   - Membership (B2): the spine now holds every IP RAPID applicant's ABN (ADR 0011), so every right with an ABN has its
     firm.
   - `entity_group`: APRA-regulated funds are super funds (31 firms had been "Other").
3. **`regions`.** The Census gives 0 for a median that describes no one (no renters, no residents): 34 postal areas'
   median rent, 6 household incomes, 4 household sizes and 1 median age and personal income. These are now empty, so a
   distribution does not mistake them for very poor areas.
4. **`national` (A8).**
   - Trade mark applications by residents and non-residents (`IP.TMK.RSCT`, `IP.TMK.NRCT`, 2004 to 2024), from the
     World Bank's current codes (ADR 0011).
   - The OECD's R&D intensity (`OECD.MSTI.G`, gross; `OECD.MSTI.B`, business; % of GDP, to 2025 for some countries and
     2023 for Australia), with `source = 'OECD'`, beside the World Bank's (to 2021 for Australia). They differ where
     they overlap (Australia 2021: 1.66% OECD, 1.86% World Bank), so they are compared, never spliced. The OECD
     flags 32.5% of these values (estimated, provisional, definition differs, time series break), and a new `status`
     column keeps the flag: every Australian GERD value from 2010 is an estimate.
   - One name per country (the World Bank's): 31 countries had two (the World Bank's and WIPO's).
5. **`timeline`.**
   - **Trade mark registrations by the date entered.** A trade mark is registered "as from" its filing date, so IP
     RAPID's effective date for a registration is the filing (priority) date (for 85% of them); the date the
     registration was entered is the declared date (92.5% have one). Counted by effective date, the series was the
     number of each month's filings later registered, and it fell from about 5,700 a month to 0 by September 2026, as
     recent filings await examination. It now counts registrations by the date entered (the declared date, else the
     effective date): about 6,300 a month over the last year (the median), with 5,944 in September 2026. It matches
     the register's own date of registration status (`gained_registration_status_date`) to within 0.1% in every year
     from 2010 to 2026.
   - **Trade mark registrations start in January 1986**, set by hand (`TIMELINE_START_OVERRIDE`). IP RAPID has the date
     entered for every registration from 1986 and for under 2% before 1984; an older registration has only its effective
     date, which is its filing date for 99% of them. Counted at that date, the series showed a false hole: 122
     registrations in 1984 and 100 in 1985, against 5,300 to 7,900 a year in 1981-82 and 1986-87, because registrations
     entered in 1983-85 were dated at filing (earlier) and marks filed then were entered after 1985 (later). The 123,019
     registrations before 1986 are left out of the series; the trade mark application series cover those years.
   - **Each event once.** An event IP RAPID records twice for a right, with the same type and date, counts once:
     1,273 repeats in all (0.02% of the events), of which 413 are design registrations (0.2% of that series) and 402
     design lapses (1.9%); no other series loses more than 0.07%. The repeated design records differ in the date each
     was entered, so some may be separate designs filed in one application; either way each application counts once,
     as in the application series. Events on different days are kept: a right can lapse, be restored and lapse again,
     and a trade mark can be opposed several times. The series are labelled as event counts.
   - **Starts (A3).** A series starts at the first month from which at least 9 of the next 12 have a record, instead of
     at its first record; earlier months are empty. Before, trade mark oppositions read 0 for 777 months, patents lapsed
     for 544, Australian standard patents for 316. Now Australian standard patents start in July 1971 and overseas ones
     in October 1969, provisional applications in February 1975, patent grants in January 1975, patent lapses in
     December 1979, trade mark oppositions in May 1983 and patent oppositions in December 2003 (the rule's choice for
     every series is in the notebook's timeline section). The three "origin unknown" series are the exception the rule
     allows: their zeros since are real, as applicants' countries came to be recorded.
   - **Ends.** Five series leave their last months empty, because the register records them late: trade mark and
     design cessations (six months: a right ceases on the record only once its six-month grace period for renewal has
     passed; trade mark cessations were 0 from May 2026, with a median 198 days from effective date to record), and the
     three design origin series (three months: recent designs' applicant countries are filled in weeks after filing,
     so 843 of September 2026's designs were "origin unknown", against about 50 a month before).
   - **The CPI**, quarterly, all groups, Australia, original (index, the month of September 2025 = 100, the ABS's
     reference), in each quarter's last month and empty in the other two, so it is compared at quarterly resolution and
     never spread across months (ADR 0007). It deflates the money series.
   - **Policy events**: 16, every date checked against the Federal Register (ADR 0011).
6. **The record (A7).** The corrections the review listed are made: `docs/data-plan.md` names `iprapid` where it named
   `ipgod`; `analysis/README.md` says "about 2,640 ABS postal areas" and describes the Google Patents join as measured;
   ADR 0005's "about 80% of patent rights have no Australian postcode, because their applicants are overseas" is
   superseded by ADR 0009's split (50.3% overseas, 29.5% unknown, mostly before 1990).

**Not done, and why.**
- Rules for regional rates (B3: minimum denominators, intervals, a per-person rate): part of Stage 2's regional work.
- Founding applicants in `rights` (B1), Google Patents and the inventors (B4), the survival measure (B5): the `rights`
  lens's planned attachments, built in its Stage 1 section.
- A design total in the timeline (to keep the last three months while the origin split is being filled in): not
  needed; the three origin series are the record.

**Checked.**
- Every lens has one row per key, and `variables.yaml` lists every column in order (tests).
- The timeline: within each series' coverage there is no run of zeros longer than 12 months except in the "origin
  unknown" series; the months still being recorded are empty; and no series ends on a cliff (`tests/test_eda.py`).
- These figures were measured again on the final build: the R&D rule (936 of 38,290 ABN-years), the filings
  measure (28,329 firms), the super funds (31), the Census zeros (34, 6, 4, 1 and 1 postal areas), the innovation
  patents after the closure (768), the repeated events (1,273) and trade mark registrations against the register's
  status date (within 0.1% in every year from 2010 to 2026).
- The lenses as built: `rights` 4,368,006 rows (29 columns), `firms` 398,450 (37), `regions` 2,641 (31), `national`
  135,140 (10) and `timeline` 1,473 months (35).
