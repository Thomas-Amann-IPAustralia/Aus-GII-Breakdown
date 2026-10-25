# Handover: exploratory data analysis

For the next Claude Code session. Read `CLAUDE.md` first, then `docs/eda-plan.md`.

**Status (2026-10-25, later):** Stage 1 has begun. The `rights` section of `01_univariate.ipynb` profiles every
core variable of the lens, with observations U1 to U16 and a summary table (1.9). Profiling found five more problems,
repaired in the lens before the profiles (ADR 0012): IP RAPID's "agent" is the address for service, often the
applicant itself, so attorney use was overstated (Australian trade marks 57.02%, not 100%); `main_area` repeated the
Nice or Locarno class for trade marks and designs; a 1 January 1970 retirement placeholder (1,282 rights) and a
registration before 1904; trade marks registered before 1986 are dated at filing, so their time to registration
measured nothing; and IP RAPID left out the state for about a third of Australian standard patents filed from FY2024,
now taken from the postcode.

Earlier the same day: the last check before Stage 1 (ADR 0010, the lenses; ADR 0011, the corpus), after the
independent review (`docs/Aus-GII-Independent-Review-and-Action-Plan.md`, whose IDs A1–A8, B1–B12, F01–F42 and
N01–N07 are used throughout), the owner's decision that every dataset goes through all three stages (ADR 0007),
`abs_prices` and `abs_labour`, the inventors (ADR 0008) and the `rights` repairs (ADR 0009). TableBuilder is on hold,
and BLADE stays ruled out.

## Where things stand

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
- **Five lenses are built** (`analysis/eda/build.py`), in under a minute:
  - `rights`: 4,368,006 rows, 29 columns;
  - `firms`: 398,450 rows, 37 columns;
  - `regions`: 2,641 rows, 31 columns;
  - `national`: 135,140 rows, 10 columns;
  - `timeline`: 1,473 months, 35 columns.

  Two more, `industries` and `institutions`, are planned (ADR 0007). Every table has a lens to attach to; the map is
  in `docs/eda-plan.md`.
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
- **Settled (descriptive, ADR 0010):** the register does not drop provisional applications once a full application
  claims them (N01, refuted), so FY2026's jump to 10,069 provisionals is real; `application_date` for a PCT filing is
  the date it entered Australia's national phase (N06).
- **Corrected this session** (each in the record as well):
  - the plan to ask AusTender's API for notices by the date last modified: its windows from July 2023 page back
    through every older contract, so it was replaced by asking for the running contracts by id. The draft of ADR 0011
    had said the 2019 to 2023 amendments could not be recovered; asking by id recovers them;
  - the draft of ADR 0010 said repeated events were at most 0.2% of any series: design lapses lose 1.9%;
  - "Contract value at latest amendment" was described as the most a contract was worth; an amendment can lower it;
  - the trade mark registration series' months before 1986 counted filings, with a false hole in 1983 to 1985.
- **Tests:** 57 pass (the lens tests skip unless the lenses are built); lint is clean.

## Next, in order

1. **The `rights` attachments, as sub-sections of 1.8,** each built into the lens first: the events per right
   (lifetimes, B5), the parties (every applicant's country, founding against current holder, the attorney firm: B1),
   the links (with the PCT country check), Google Patents (B4) and the inventors (gender estimates checked country by
   country against WIPO's published shares, above all China and Korea).
2. **The `timeline` section:** each series from the first month the lens gives it; the CPI at quarterly resolution;
   the 16 policy events one at a time (descriptive only: Stage 2 compares before and after). The rushes before
   Raising the Bar (1,856 applications on 12 April 2013) and the innovation patent's closure belong here.
3. **`firms`, then `regions` (the B3 rules for small areas first: a minimum denominator or pooling, intervals, a
   per-person rate), then `national`,** in the order the plan gives.
4. **The plan's "high value, little work" additions, with the lens each serves:** the RBA's cash rate and exchange
   rates and the ABS national accounts (timeline), the ATO's statistics by postcode (regions), and IP Australia's own
   published figures as a benchmark (which would also test the provisional rise, U8).

## Open items

1. Check in Stage 1:
   - the 1800-01-01 placeholder in IP RAPID's events, links and parties (the 1901 and 1970 dates in `rights` are
     repaired, ADR 0012);
   - IP RAPID's `links.linked_application_country`, which labels every PCT number `au` (`analysis/README.md`), with
     the links attachment;
   - the 222-day peak in trade mark registration times (U11), against IP Australia's published process times.
2. The attorney flag (ADR 0012) may still count some agents who are not attorneys: counting only agents of five or
   more applicants gives 49.52% for Australian trade marks against 57.02%. The parties attachment (B1) can name the
   attorney firms and settle it.
3. AusTender: amendments after August 2019 to bulk-file contracts that had ended by then are not in the corpus. A
   sample suggests they are under 1% of the contracts' value; `austender._harvest_by_id` can fetch them in about a day.
4. Fee history (R3) and the PBS monthly report with Section 100 (B9) are the biggest data gaps for the later stages.
5. The `coalesce` in `iprapid.py` that caused the origin problem (ADR 0009) is left until IP RAPID is next rebuilt; no
   lens reads that column.

## For the owner

Nothing blocks the rest of Stage 1. Only you can do these:
1. **Confirm N01 and N06 as settled** (ADR 0010): both are descriptive facts about the register, not research
   findings, but they close two of the review's open questions.
2. **The provisional rise (U8), if you can ask IP Australia:** whether a change in filing (a new channel, a fee, or
   drafting tools) explains individuals' provisionals doubling in FY2026. The data show when and who, not why.
3. **TableBuilder, only if a question needs owner-managers by sex or Indigenous status for each postal area:** register
   as a private user, and check that the free Basic version has the variables (`docs/tablebuilder-owner-managers.md`).

## Conventions to keep

- Commit the code, run the notebook, then commit the notebook with its outputs.
- Never print raw rows. Aggregate in DuckDB.
- After a parser fix, `corpus reprocess <source>` rebuilds its tables from the raw files it holds, keeping the data's
  vintage (ADR 0011).
- The `rights` section's cells are long; keep each new sub-section to a few cells, and the notebook under about
  25 MB (it is 4.0 MB now; ADR 0002 says when to split it).
- Next free ADR: 0013.
