# Questions for the owner

Questions only the owner can answer: direction, money, adopting a finding, anything outward-facing, and new data that
needs an account or a request (`CLAUDE.md`). Each says why it matters, what Claude recommends, and what the answer
changes. **Nothing here blocks Stage 1**; the work carries on around each one.

When a question is answered, move it to **Answered** with the date and the answer, and record it where it applies (an
ADR, the handover or the plan). Number new questions from the next free one: **OQ18**.

## Open: for you to answer

| # | Question | Why it matters | Recommendation | What the answer changes |
|---|---|---|---|---|
| OQ2 | Should the two biggest data gaps be filled before Stage 2: the history of official fees (R3, B8) and the PBS monthly report with Section 100 (B9)? Both are free, from the Federal Register and the PBS website | Fees are IP Australia's most direct lever (Q4, Q5); Section 100 holds high-cost medicines, central to a medicine case study | Build the fee history before Stage 2 (a few days); leave the PBS report until a medicine case study is chosen (OQ8) | Whether Stage 2 can relate filing and renewal to fees |
| OQ3 | Should the missing AusTender amendments be fetched? Amendments after August 2019 to contracts that had ended by then are not in the corpus | A sample suggests under 1% of contract value; the harvester exists (`austender._harvest_by_id`); it takes about a day of running, at no cost | Not now: the effect is small. Fetch it if Stage 2 leans on contract values | The completeness of `austender_value` |
| OQ4 | TableBuilder: only if a question needs owner-managers by sex or Indigenous status for each postal area, would you register as a private user? | It needs an account in your name; the free Basic version may not have the variables (`docs/tablebuilder-owner-managers.md`) | Hold until the `regions` profile shows a need | One more `regions` attachment |
| OQ11 | The `institutions` lens is built (ADR 0021) on a reviewed link: 130 institutions, 116 extra names (former names, predecessors, commercialisation companies, misspellings) and 146 ABNs, in `analysis/eda/institutions/`. Should someone who knows the sector (IPAVentures, or IP Australia's own research team) check it? | It decides which IP counts as a university's: UNSW files 96.5% of its patents through NewSouth Innovations, Newcastle 72.8% through Newcastle Innovation (U81). A missed company or merger moves an institution's counts | A half-hour check of the three CSV files by someone in the sector, before Stage 2 compares institutions; in particular each university's companies, and which medical research institutes and health services belong | Corrections to the link; the lens rebuilds in seconds |

## Open: for IP Australia (you are asking)

The data show when and who, not why. Each answer would turn a lead into an explanation. OQ12 to OQ14 came from the
audit against IP Australia's published figures and were added to the same request by the owner on 27 October 2026
(A8).

| # | Question | Evidence | Meanwhile |
|---|---|---|---|
| OQ5 | Your IP Report 2026 links the 2025 rise in provisional applications to digital tools, including AI. What evidence supports that? And are the few very heavy filers part of the same pattern (54 individuals filed 10 or more provisionals each in FY2026, one filed 375), or something different? **Reworded (2026-10-27, A10)**, because IP Australia had already published its reading: the rise is "consistent with reduced entry costs and faster drafting and search enabled by digital tools, including artificial intelligence" (new filers 63%, self-filers 52%, ipr-2026 p21; ADR 0024). Was: why did provisional applications from individuals double in FY2026 (10,069 against 5,047): a new filing channel, a fee change, or drafting tools? | U8: individuals without ABNs; 54 individuals filed 10 or more, one 375; monthly filings peaked in March and April 2026. The lens reproduces IP Australia's 2025 count (6,874 against 6,867, ADR 0024) | Counts are kept as recorded; Stage 2 tests them against policy and fee events |
| OQ6 | IP Australia's register records "Examination expedited" in the history of every trade mark claiming convention priority filed since November 2018, and of about a quarter of the others, but IP RAPID publishes only the expedites applicants ask for ("Expedite Work Initiated"). What does "Examination expedited" mean where no one asked (a fast track IP Australia applies to priority claims?), and could IP RAPID publish it? **Reworded (2026-10-27, OQ16, the register check, ADR 0028 V14).** Was (recheck, ADR 0027): before November 2018, about 97% of trade marks claiming convention priority carried an expedited-examination event, and almost none have since; did the old system record those marks' handling under that event, rather than applicants' requests? Earlier: why did requests for expedited examination of trade marks fall from about 1,400 a month to about 230 in November 2018? | V14: in a random sample, the register shows "Examination expedited" on 130 of 130 priority-claiming marks filed FY2020 to FY2026 and IP RAPID none; on 162 of 644 other marks, against IP RAPID's 34 (all among the 162). Before: U34, R1 to R5 (1,417 requests in October 2018, 604 in November, 240 in December) | U34 restated from the register's own events (ADR 0029); IP RAPID's series kept beside it |
| OQ7 | IP Australia's register holds an ABN, or an ACN that the ABR links to one, for 84% of the Australian organisations' trade marks filed since July 2024 that have no ABN in IP RAPID (and for 60% of such marks in FY2023). Why does IP RAPID leave them out, above all for customers new since July 2024, and could it publish them, with ACNs? **Reworded (2026-10-27, OQ16, the register check, ADR 0028 V12).** Was (recheck, ADR 0027): did something change in July 2024 in how new customers are set up, or in what IP RAPID publishes? Is the ABN collected but not published? Earlier (A10): is the ABN added to the record later, or no longer collected or checked? | V12: of 34,635 such marks, the register gives an ABN for 19,215 (55.5%) and an ACN linked to one for 9,826 more: 29,041 (83.8%). Before: U45, R11 to R15 (85.1% with an ABN in FY2024, 59.8% in FY2026) | ABNs filled from the register in the lenses (ADR 0029); U45 restated; IP RAPID's own ABN kept beside it |
| OQ12 | What does IP Australia's "In 2022, 55.6% of resident applications were filed by individuals rather than organisations" (ipr-2023 p12) count? | The lens gives 20.65% of 2022's resident standard applications with an individual as first founding applicant, and 26.76% of their applicants (U13, U48); no base reproduces 55.6% (the audit, D3) | U13 and U48 stand on the lens's evidence, recorded as disputed |
| OQ13 | IP Australia's register counts 78,643 trade marks lodged in 2018 (77,726 by filing date), IP RAPID 77,496 and WIPO 15,943 Madrid designations against IP RAPID's 15,836; the IP Report 2019 counted 79,490. What did the report's 2018 count include, and does IP Australia still stand by it? **Reworded (2026-10-27, OQ16, the register check, ADR 0028 V10, V11):** the question about trade mark numbers 1,978,060 to 1,980,352 is dropped, as the register shows they were not used (1 of 2,292 exists). Was (recheck and WIPO, ADR 0027): what did the 2018 count in the IP Report 2019 include, and were those numbers ever used? Earlier: why does IP RAPID hold about 2,000 fewer trade marks filed in 2018 than the IP Report 2019 counted? | V11: neither of the register's dates gives 79,490 (lodgement date 847 short). Every other year from 2015 to 2025 agrees with IP Australia within 0.05% (D2); WIPO: R9 | 2018 is flagged in trade mark series |
| OQ14 | IP Australia's register holds the owner's country for 61% of the designs IP RAPID leaves without one, and for nearly all filed since 1990. Could IP RAPID publish it? **Reworded (2026-10-27, OQ16, the register check, ADR 0028 V13).** Was: could IP RAPID publish the applicant origin IP Australia holds for designs it now leaves unknown? | V13: the register gives a country for 25,018 of 40,748, Australia for 20,870; for 2021, 2023 and 2025 the lens plus the register's Australians (2,601, 2,660, 3,078) matches IP Australia's resident counts (2,595, 2,652, 3,078). The rest have no owner on record anywhere (V17) | Design origin filled from the register in the lenses (ADR 0029); the empty 1973 to 1982 shells dropped |
| OQ17 | Your register names the inventors of 98.5% to 100% of provisional applications filed FY2003 to FY2023, but of only 78.79% (FY2024), 76.38% (FY2025) and 84.69% (FY2026). Are inventors added to a provisional later, or no longer recorded for some (for example those filed through a particular channel)? **Added (2026-10-28, A14)** | U106: 181,469 inventors in the register's records of 264,250 provisionals (ADR 0029) | The gender analysis shows each year's inventor coverage beside its figure |

**The register check (2026-10-27, ADR 0028, `docs/audit-ipa-api.md`)** found what IP Australia holds for OQ6, OQ7,
OQ13 and OQ14; at the owner's word (A13) those four now ask why IP RAPID leaves it out and whether it could publish
it, which IP Australia can answer from its own systems.

These could go in the same request, if it is easy to add: why plant breeder's rights change hands more often in recent
years (11.2% of those filed in the 2020s, U17). Two earlier add-ons are answered from IP Australia's own reports
(ADR 0024, `docs/audit-ip-australia.md`): its published counts now benchmark the lenses (155 of 195 figures agree);
and IP RAPID's innovation patents filed in 2016 (2,469, 1.331 of WIPO's utility models) were a real rise that IP
Australia reported itself (2,322, from non-residents), so the gap is between IP Australia's count and WIPO's (U67).

## Deferred: not needed for the EDA

| # | Question | Status |
|---|---|---|
| OQ8 | Rank the medicine case study (R7) against the other case studies | Ask when Stage 3 ends |
| OQ9 | Reopen BLADE (F24, R4), the only route to small-firm outcomes and firm-level additionality (Q3, Q5)? A scoping enquiry to the ABS is free to send but outward-facing and may lead to fees | Ruled out by the owner (2026-10-22); revisit before answering Q3 and Q5 |
| OQ10 | Outward-facing research: R3's survey of what IP costs small firms, R5's user research, and First Nations data governance (F23) | Not recommended now; the owner's call if and when |

## Answered

| # | Question | Answer | Date | Recorded in |
|---|---|---|---|---|
| A14 | Go ahead with Stage 2 and the gender analysis (provisionals from FY2003, each year's coverage shown); add the provisional-inventor lead to the request (OQ17; the unrequested "Examination expedited" is already OQ6); open a pull request so the branch, and the atlas with it, can be published | Agreed to all | 2026-10-28 | This page (OQ17); handover |
| A13 | OQ16: reword the request to IP Australia to ask why IP RAPID leaves out what its register holds (the expedite event since November 2018, ABNs and ACNs, design applicants' countries), and drop the number-gap half of OQ13? | Yes | 2026-10-27 | This page (OQ6, OQ7, OQ13, OQ14); ADR 0029; the atlas |
| A12 | OQ15: attach the gaps the register fills to the lenses? | Yes, as suggested: new columns beside IP RAPID's, never replacing them, and U45, the design shares (U7, U13) and U34 restated. Also: harvest every provisional with its inventors (gender analysis to come), drop the design records with no information (recorded), and make no guesses about the remaining designs' origin | 2026-10-27 | ADR 0029; the notebook; handover |
| A11 | Does "do not alter the atlas" (A9) cover its framing pages? | No: update the atlas with the changed wording; only the substantive analyses stay unchanged for now | 2026-10-27 | ADR 0026; handover |
| A10 | Reword OQ5 and OQ7 to ask about what IP Australia's reports leave open? | Yes: OQ5 now asks for the evidence behind IP Australia's digital-tools reading and about the heavy filers; OQ7 asks only about the ABN data | 2026-10-27 | This page; handover |
| A9 | How should the audit against IP Australia be shown? | Pushed to the repository and shown in the evidence atlas; at this stage neither the notebook nor the atlas's existing pages are altered | 2026-10-27 | ADR 0025; handover |
| A8 | Add OQ12 to OQ14 (the audit's questions) to the request to IP Australia? | Yes | 2026-10-27 | This page; ADR 0024 |
| A7 | When should the other `rights` attachments be done (OQ1): the links, Google Patents and the inventors? | Now: done (U88 to U98) | 2026-10-26 | ADR 0022; handover |
| A6 | Go on to the `industries` lens after `national`? | Yes | 2026-10-26 | Handover; ADR 0020 |
| A1 | Adopt years in force (U36), with unfinished rights kept, as a working measure of how long owners keep their rights? | Yes, as long as it is used alongside other signals | 2026-10-25 | ADR 0015; handover |
| A2 | Order of work after the timeline | The events attachment (B5), then `firms` | 2026-10-25 | Handover; plan |
| A3 | Are N01 (provisionals not dropped once claimed) and N06 (a PCT application's date is its national phase entry) settled? | Yes | 2026-10-25 | ADR 0010 |
| A4 | Every dataset goes through all three stages, with two new lenses (`industries`, `institutions`) | Yes | 2026-10-25 | ADR 0007 |
| A5 | BLADE | Ruled out | 2026-10-22 | `docs/data-plan.md`; OQ9 |
