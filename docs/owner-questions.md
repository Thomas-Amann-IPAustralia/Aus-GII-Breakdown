# Questions for the owner

Questions only the owner can answer: direction, money, adopting a finding, anything outward-facing, and new data that
needs an account or a request (`CLAUDE.md`). Each says why it matters, what Claude recommends, and what the answer
changes. **Nothing here blocks Stage 1**; the work carries on around each one.

When a question is answered, move it to **Answered** with the date and the answer, and record it where it applies (an
ADR, the handover or the plan). Number new questions from the next free one: **OQ12**.

## Open: for you to answer

| # | Question | Why it matters | Recommendation | What the answer changes |
|---|---|---|---|---|
| OQ1 | When should the other `rights` attachments be done: the links (the route into Australia), Google Patents (family size, citations, B4) and the inventors (with estimated gender)? | They add who invents and how inventions reach Australia (Q1, Q2); they are not needed for the other lenses' Stage 1 | After `regions` and `national`, so that every lens has its Stage 1 core before more attachments | The order of work in the handover |
| OQ2 | Should the two biggest data gaps be filled before Stage 2: the history of official fees (R3, B8) and the PBS monthly report with Section 100 (B9)? Both are free, from the Federal Register and the PBS website | Fees are IP Australia's most direct lever (Q4, Q5); Section 100 holds high-cost medicines, central to a medicine case study | Build the fee history before Stage 2 (a few days); leave the PBS report until a medicine case study is chosen (OQ8) | Whether Stage 2 can relate filing and renewal to fees |
| OQ3 | Should the missing AusTender amendments be fetched? Amendments after August 2019 to contracts that had ended by then are not in the corpus | A sample suggests under 1% of contract value; the harvester exists (`austender._harvest_by_id`); it takes about a day of running, at no cost | Not now: the effect is small. Fetch it if Stage 2 leans on contract values | The completeness of `austender_value` |
| OQ4 | TableBuilder: only if a question needs owner-managers by sex or Indigenous status for each postal area, would you register as a private user? | It needs an account in your name; the free Basic version may not have the variables (`docs/tablebuilder-owner-managers.md`) | Hold until the `regions` profile shows a need | One more `regions` attachment |

## Open: for IP Australia (you are asking)

The data show when and who, not why. Each answer would turn a lead into an explanation.

| # | Question | Evidence | Meanwhile |
|---|---|---|---|
| OQ5 | Why did provisional applications from individuals double in FY2026 (10,069 against 5,047)? A new filing channel, a fee change, or drafting tools? | U8: individuals without ABNs; 54 individuals filed 10 or more, one 375; monthly filings peaked in March and April 2026 | Counts are kept as recorded; Stage 2 tests them against policy and fee events |
| OQ6 | Why did requests for expedited examination of trade marks fall from about 1,400 a month to about 230 in November 2018? A change in practice, or in how requests were recorded when the trade mark records moved to a new system? | U34: 1,417 in October 2018, 604 in November, 240 in December; 16.67% to 19.69% of marks to FY2018, 3.08% to 3.97% since FY2020 | Trade mark expedite shares compared only on one side of November 2018 |
| OQ7 | Since FY2025, are ABNs attached to applications late, or collected less often? | U45: Australian organisations' trade marks with the filer's ABN 84.1% (FY2024), 71.4% (FY2025), 59.9% (FY2026); designs 88.4% to 76.3% | Firm-level filing by year compared only to FY2024 |

These could go in the same request, if it is easy to add: why plant breeder's rights change hands more often in recent
years (11.2% of those filed in the 2020s, U17); IP Australia's own published counts, to benchmark the lenses; and why
IP RAPID holds a third more innovation patents filed in 2016 than WIPO's count of Australia's utility models (2,469
against 1,855; other years 0.958 to 1.072 of it, U67).

## Deferred: not needed for the EDA

| # | Question | Status |
|---|---|---|
| OQ8 | Rank the medicine case study (R7) against the other case studies | Ask when Stage 3 ends |
| OQ9 | Reopen BLADE (F24, R4), the only route to small-firm outcomes and firm-level additionality (Q3, Q5)? A scoping enquiry to the ABS is free to send but outward-facing and may lead to fees | Ruled out by the owner (2026-10-22); revisit before answering Q3 and Q5 |
| OQ10 | Outward-facing research: R3's survey of what IP costs small firms, R5's user research, and First Nations data governance (F23) | Not recommended now; the owner's call if and when |
| OQ11 | Should the `institutions` lens's link from research institutions to ROR identifiers and ABNs (about 60 universities, CSIRO and the medical research institutes) be reviewed by someone who knows the sector? | Ask when that lens is built |

## Answered

| # | Question | Answer | Date | Recorded in |
|---|---|---|---|---|
| A1 | Adopt years in force (U36), with unfinished rights kept, as a working measure of how long owners keep their rights? | Yes, as long as it is used alongside other signals | 2026-10-25 | ADR 0015; handover |
| A2 | Order of work after the timeline | The events attachment (B5), then `firms` | 2026-10-25 | Handover; plan |
| A3 | Are N01 (provisionals not dropped once claimed) and N06 (a PCT application's date is its national phase entry) settled? | Yes | 2026-10-25 | ADR 0010 |
| A4 | Every dataset goes through all three stages, with two new lenses (`industries`, `institutions`) | Yes | 2026-10-25 | ADR 0007 |
| A5 | BLADE | Ruled out | 2026-10-22 | `docs/data-plan.md`; OQ9 |
