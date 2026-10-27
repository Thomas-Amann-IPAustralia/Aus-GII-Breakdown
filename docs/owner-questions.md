# Questions for the owner

Questions only the owner can answer: direction, money, adopting a finding, anything outward-facing, and new data that
needs an account or a request (`CLAUDE.md`). Each says why it matters, what Claude recommends, and what the answer
changes. **Nothing here blocks Stage 1**; the work carries on around each one.

When a question is answered, move it to **Answered** with the date and the answer, and record it where it applies (an
ADR, the handover or the plan). Number new questions from the next free one: **OQ15**.

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
| OQ6 | Before November 2018, about 97% of trade marks claiming convention priority carried an expedited-examination event, and almost none have since. Did the old system record those marks' handling (for example a fast queue IP Australia ran itself) under that event, rather than applicants' requests? **Reworded (2026-10-27, recheck)** on a fresh release: the fall is almost all in those marks, so it looks like recording, not demand (ADR 0027, R1 to R5). Was: why did requests for expedited examination of trade marks fall from about 1,400 a month to about 230 in November 2018? A change in practice, or in how requests were recorded when the trade mark records moved to a new system? | U34, reproduced on the 26 October 2026 release: 1,417 requests in October 2018, 604 in November, 240 in December. With a priority claim: 95.97% to 97.81% of marks (FY2009 to FY2018), 0.06% to 0.16% since FY2020; without one: 4.81% to 6.11%, then 3.60% to 4.87%, no break. The old system's last trade mark examination event is on 9 November 2018 and the new one's first on 13 November; the ordinary examination request is not recorded for trade marks after that. IP Australia's reports do not mention it (ADR 0024) | Trade mark expedite shares compared only on one side of November 2018 |
| OQ7 | From July 2024, applicants new to IP Australia mostly have no ABN in IP RAPID: trade marks from companies registered less than a year before filing carried one about 90% of the time in FY2022 to FY2024, and 10% in FY2026, though ASIC's register shows the companies have ABNs. Did something change in July 2024 in how new customers are set up, or in what IP RAPID publishes? Is the ABN collected but not published? **Reworded (2026-10-27, recheck)**: the fresh release shows the ABNs are not added later (marks filed in July 2024 are still at 79.2%), so the question asks what changed (ADR 0027, R11 to R15). Was (A10): since mid-2024, is the ABN added to the record later, or is it no longer collected or checked? If later, how long does it usually take? Filing itself did not fall: IP Australia reports record resident trade marks in 2025 (55,913, +15.1%), and counted by applicant first-time resident trade mark filers rose from 22,838 (2024) to 28,626 (2025) (ADR 0024) | U45, reproduced: Australian organisations' trade marks with an ABN 85.1% (FY2024), 71.7% (FY2025), 59.8% (FY2026); by month 82.2% to 87.1% until June 2024, 79.2% in July, 51.8% in October 2026. New applicants 82.4% (FY2024) to 42.5% (FY2026); applicants seen before 87.4% to 77.7%. 80.0% of FY2026's no-ABN company filers match an ASIC company with an ABN, 75.2% of them registered since July 2024 | Firm-level filing by year compared only to FY2024; entry counted by applicant beside it |
| OQ12 | What does IP Australia's "In 2022, 55.6% of resident applications were filed by individuals rather than organisations" (ipr-2023 p12) count? | The lens gives 20.65% of 2022's resident standard applications with an individual as first founding applicant, and 26.76% of their applicants (U13, U48); no base reproduces 55.6% (the audit, D3) | U13 and U48 stand on the lens's evidence, recorded as disputed |
| OQ13 | WIPO records 15,943 designations of Australia through the Madrid system in 2018, and IP RAPID holds 15,836 Madrid trade marks, but the IP Report 2019 implies about 17,830 (+13%; 79,490 trade marks in all, against IP RAPID's 77,496). What did the 2018 count in the IP Report 2019 include, and does IP Australia still stand by 79,490? And were trade mark numbers 1,978,060 to 1,980,352, issued around New Year 2019, ever used? **Reworded (2026-10-27, recheck and WIPO)**: WIPO's own count agrees with IP RAPID, so the gap is probably in the report's count, not missing records (ADR 0027, R6 to R10). Was: why does IP RAPID hold about 2,000 fewer trade marks filed in 2018 than the IP Report 2019 counted, all of them Madrid applications? | Every other year from 2015 to 2025 agrees with IP Australia within 0.05% (the audit, D2). IP RAPID's Madrid marks are 0.9884 to 1.0121 of WIPO's designations of Australia in every year from 2014 to 2024 but 2023 (1.0662); 2018: 0.9933. TM-Link (IP Australia, 2020) has the same 2018 count as IP RAPID. The 2,292 numbers in the gap are all missing but one, about 2,100 to 2,200 beyond the usual rate | 2018 is flagged in trade mark series |
| OQ14 | Could IP RAPID publish the applicant origin IP Australia holds for designs it now leaves unknown? | IP Australia counts 264 to 425 more resident designs a year than the lens (2021 to 2025), about three in four of the designs with no country in IP RAPID (the audit, D1) | Design shares among known origin are lower bounds |

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
