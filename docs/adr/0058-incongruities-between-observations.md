# 0058: Observations read against each other: nine incongruities corrected, and B40's Stage 3 outcome changed to "holds"

**Date:** 2026-11-14. **Whose:** the owner's (the ask: analyse the observations in the notebooks or the atlas for any
incongruity; then "make all corrections", and add the question on agents to the request to IP Australia, A42);
Claude's (the method, each correction's wording, and the choices below), which the owner can overturn.

**Context.** ADR 0057 read each of the 231 observations against the output above it. It did not read them against
each other. This pass does: each observation's notebook text (dated correction notes left out) with its atlas headline
and revisit lines, compared for figures or claims that disagree across pages. The plain-English readings were read
only for the pages flagged. Candidates were then checked on the rebuilt lens tables or traced to their output cells.

**What was found, and what was done.** Nine incongruities; none reverses a Stage 1 or Stage 2 finding, and one changes
a Stage 3 outcome (item 4).

| # | Observations | The incongruity | The correction |
|---|---|---|---|
| 1 | U20, B5 | U20: Australian individuals filed 37.2% of their standard patents alone (FY2017 to FY2026). B5: 26.11% (FY2010 to FY2019). Neither says why they differ | A table by year, run alone, above U20: 22.4% to 30.3% in FY2015 to FY2022, then 35.7%, 43.7%, 50.4% and 66.5% (FY2023 to FY2026); Australian organisations 2.9% to 4.5%, then to 23.8%; overseas organisations 0.12% to 0.90%, then 4.91% in FY2026; trade marks no rise. Dated notes on U20 and B5: a lead, since FY2026's jump shows for overseas organisations too (agents recorded late?), and OQ36 for IP Australia |
| 2 | M33 | Atlas headline: "a quarter of the international measures still go with patenting". A quarter is of the leads (56 of 224); of the 477 measures it is about one in eight | Headline now "56 of 477 international measures"; a note in the notebook |
| 3 | M35, U8 | The outcome copied onto U8's page: "the heavy filers behind the surge follow up much less". M35's heavy filers are FY2025's (183 provisionals, 9 individuals); the surge's are mostly FY2026's (54 individuals, 1,528 provisionals), whose 12 months have not run | The outcome and a note in M35 say so |
| 4 | M22, B40, B41 | M22 tested Australians' trade marks against business R&D (0.609, B41's pair) and gave its verdict, "not detected once held", to B40, whose lead is every applicant's trade marks (0.709; 0.682) | B40's own pair tested in a second table, run alone: 0.514 (0.061 to 0.827) and 0.487 (0.098 to 0.803) with value added held, 72% and 71% of the raw size: **holds**. B40's outcome is now "holds"; "not detected once held" moves to B41. M22's heading, bullets, reading, section summary and page follow |
| 5 | B5 to B7, B11, B12, B15 to B17; M1, M26, M27 | U17: patents filed before FY2003 have one set of applicants, who may be a later holder. Only B8 repeated it, though FY2000 to FY2009, the earlier decade of each, holds three such years | A note under B5 and a pointer on each of the others |
| 6 | U9, U3 | U9: all 408,957 unknown-status patents "were filed between FY1904 and FY1999". 49,737 of them have no application date (U3) | Text put right (the 359,220 with a date), with a dated note; U9's page |
| 7 | U78, B41 | Business R&D per business for FY2024 differs: U78 divides by businesses at June 2024, B41 by those at the start of the year, which swaps manufacturing and utilities | A note on each naming the denominator; within 3%, the order of the two not a finding |
| 8 | B37 and B47; B35 and M33; B57 and M22 | Small figures that differ between pages: 0.338 and 0.334 (the Designs Act's step); 225 and 224 leads (64 and 63 from the GII); 0.481 and 0.491 (value added is FY2024's in both of M22's years, FY2025's in B57) | A note in B47, M33 and M22. Each matches its own table |
| 9 | U75, U114, B41 | U75 and U114 say the main crosswalk sends nothing to services; B41 says it places patents in three service divisions | Notes on U75 and U114: "none" is of ISIC's service divisions; in ANZSIC divisions three service divisions receive 0.03% to 0.23% (U75's own table) |

**Choices.**

1. **B40's outcome changes, under ADR 0046's rules.** The interval is clear of zero and more than half of the raw size
   remains, so the word is "holds". The lower ends (0.061 and 0.098) are only just clear of zero, on 19 divisions and
   one year of R&D, and the page says so. The ninth early signal now reads "patents and trade marks allocated per
   business follow business R&D" and lists B40. The owner can ask for it to be left as "not detected" pending a second
   year of R&D; nothing else depends on it.
2. **Two cells were added and run alone** (the notebook's setup cell, then the new cell, in a fresh kernel), as the
   review of 3 November did: `e891a43a` in notebook 1 (1.8.1, above U17 to U21's observations) and `622-berd-all` in
   notebook 3 (6.2). No other cell was run; every other output is byte for byte as it was.
3. **The rise in filing alone is recorded as a lead, not a finding.** It is not given its own observation number: it
   qualifies U20 and B5, and what it is waits on OQ36. The two decades B5, B6 and M1 compare end in FY2019, before it.
4. **Notes are dated 14 November 2026**, the day the incongruities were found.

**Not changed.** Differences that each match their own table and change no reading were left, as ADR 0057 left them:
B6's 23.6 points and M1's 23.7 (organisations' trade marks; M1 is a sample of 200,000), B10's 34.4% and M2's 34.5%
(a survival estimate against a share in the model's sample), B46's 82 institutions and M38's 84. Checked and found
consistent: patent oppositions "recorded from April 2003" (U32) against a series from December 2003 (U22: three
events before the series starts); B20's and B27's halves both agreeing at 0.962; real GDP's fall of 5.85% (U116)
against 5.83% in current prices (U124); B53's "both were 0.465".

**Consequence for the chat.** As after ADR 0057, "Ask the atlas" quotes passages ingested at an earlier commit; the
Econ refresh in the handover now also covers these pages.
