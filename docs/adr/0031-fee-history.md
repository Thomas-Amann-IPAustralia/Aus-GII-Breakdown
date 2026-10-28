# 0031: The history of official fees, from every version of the fee regulations

**Date:** 2026-10-28. **Whose:** the owner asked for the data gaps to be filled, the fee history first (A15,
`docs/data-gaps-brief.md`, gap A1; R3 and OQ2); Claude chose the source and the method.

**Context.** Fees are IP Australia's most direct lever, and Stage 2 could not relate filing or renewal to them (B37,
U28). `ipa_fees` holds only today's fees (IP Australia's website); the Wayback Machine is blocked here. The fees are
set by regulation, and the Federal Register of Legislation holds every version of each regulation, with a public API
(`https://api.prod.legislation.gov.au/v1`): versions (start, end and the instruments that made each) and documents
(EPUB, Word, PDF). It holds the text of most versions from 1999 (compilations) and the regulations as made, but not the
compilations of the 1980s and 1990s, and of the trade mark regulations under the 1955 Act only the 1958 text.

**Decision.**

1. **One corpus source, `frl_fees`, reads six sets of regulations**: the Patents Regulations 1991 (Schedule 7), the
   Trade Marks Regulations under the 1955 Act (Schedule 2, from July 1989) and of 1995 (Schedule 9), the Designs
   Regulations 1982 (Schedule 2) and 2004 (Schedule 4), and the Plant Breeder's Rights Regulations 1994. Each starts
   when its Act began to apply (the Register's first version is the making date, which can come earlier) and ends when
   it was superseded. Raw: the versions (repo), the EPUBs (R2, zipped by title, and the amending instruments).
2. **Every compilation's fee schedule is read from its EPUB tables** (`schedule_rows`): each row's item, its matter
   with the item's words and the paragraph labels above it, the fee as written and its first dollar amount. Cells that
   hold several sub-items and their fees in one paragraph are split; "(i)" after "(h)" is read as a letter where the
   schedule's layout says so.
3. **Key fees are picked by rules, not by item number** (items are renumbered over the years): a pattern on the matter
   for each fee, the base fee only (surcharges for extra claims, pages, classes, sequences and late payment left out),
   paid the cheapest way offered (preferred, approved or electronic means; the trade mark pick list; not TM
   Headstart). Patent renewals are kept by anniversary. 23 fees, 49 series.
4. **Versions without text come from the amending instruments**, read by hand into `gaps.yaml`: where an instrument
   replaces the whole schedule, its tables are read by the same rules; otherwise each "omit ..., substitute ..." that
   touches a key fee is entered with its provision; every instrument behind a version without text is listed, with
   those that change no key fee under `checked`. The chain was checked against the next compilation: the first check
   found the 3rd and 4th anniversary renewals omitted by SR 1998 No. 264 (no dollar amount in that provision), now
   entered. Compilation 39 of the Patents Regulations (from 1 March 2001) already shows the innovation patent fees
   that began on 24 May 2001, so it is not read.
5. **The output is spells** (`key_fees`: one row per fee and period at one amount, with the version or instrument that
   set it) and the dates of change (`fee_changes`). A test checks that the latest spells give the amounts on IP
   Australia's website for every fee listed in the same terms (standard patent renewals at every anniversary to the
   19th; filing, examination and renewal of each right).
6. **Attached to two places.** The `timeline` lens holds each key fee in force on the first day of the month (26
   columns: single fees, the costs of obtaining and keeping a right, six of them also in dollars of the latest CPI
   quarter) and `fee_changes`, the rights whose fees changed that month. `policy_events/events` gains each change as
   an event (lever "fees"); the timeline's `policy_events` column leaves them out, so the Stage 1 and 2 analyses of the
   17 policy changes are unchanged.
7. **A fee no longer charged counts 0 inside a right's history** (the trade mark registration fee after 10 October
   2016; no sealing or acceptance fee from November 1998 to August 2002), and the columns are empty before it.

**Rejected.**
- Reading only the fees IP Australia announces: its pages go back a few years, and the regulations are the law.
- PDF text of the old instruments: the EPUBs carry the same text as tables.
- Hand-entering every fee: the rules read 160 compilations alike; only the gaps are entered by hand, and checked
  against the compilation that follows them.
- Adding the fee changes to the timeline's `policy_events` column: Stage 1's charts mark every event in it.

**Consequences.** Stage 1 profiles the history (U108 to U111) and Stage 2 sets filing and lapsing around each change
against placebo dates (B47 to B49). Not here: the fees before 1989 for trade marks and 1991 for patents (other Acts),
attorneys' charges, the fees of the PCT and Madrid systems, and the extra fees for claims, classes and pages (they are
in `schedule_rows`). Fees are as published; the first of the month is used, so a change on the 10th shows the next
month.
