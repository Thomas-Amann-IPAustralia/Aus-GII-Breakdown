# 0011: Corpus repairs: every published value kept, one row per key, amendments in order, and reprocessing

**Date:** 2026-10-25. **Whose:** Claude's, in the last check before Stage 1 (the owner asked for an in-depth review of
the repository, with every gap that can be easily filled filled, and every transformation made explainable and
defensible); the owner can overturn any of it. It carries out the review's B2, B7, B10, B11 and B12, the corpus half
of A1, and F02, and fixes problems this check found. The lens changes are in ADR 0010.

**Context.** The independent review (`docs/Aus-GII-Independent-Review-and-Action-Plan.md`) checked the lenses and the
loaders behind them. This check went further:
- it scanned all 160 corpus tables for exact duplicate rows, which the profile never checked ("Not yet checked" in
  `analysis/README.md`). Seventeen tables had some. In three (CABEE, PHIDU and the ABS R&D cubes), the duplicates were
  the visible part of a parser that dropped a dimension, so different values shared one label;
- it checked, for every SDMX flow (24 OECD and every ABS flow), that each non-empty source value survives;
- it re-read the AusTender releases and bulk file, and checked every policy date against the Federal Register.

**Decision.**
1. **Reprocessing.** `corpus reprocess <source>` (or `<source>:<table>,...`) rebuilds a source's tables from the raw
   files the manifest already records, fetching nothing, and merges the manifest entry: it keeps the entry's other
   files, its notes and its `run` date (when the data was fetched), and adds `reprocessed`. A parser fix then changes
   a table without changing the data's vintage. Seven sources have it: `austender`, `cer`, `phidu`, `abs_cabee`,
   `abs_rd_vc`, `oecd` and `policy_events`.
2. **AusTender (`austender`): each notice in order (A1).**
   - Each notice keeps its own id: CN123 for a contract's first notice, CN123-A2 for its second amendment, in both
     parts. `parent_cn_id` and `amendment` are new. The API gives an amendment's number in the release's
     `contracts[0].amendments` (171,126 of 171,127 well formed), but the loader kept only the contract's id, so a
     contract's notices shared one id. They could not be put in order by date: 97,135 contracts had several notices
     on their last day (a batch of releases on 27 April 2023 shares one timestamp), and how those ties were broken
     moved the total over all contracts between $904 billion and $1,154 billion.
   - In the bulk file, an amendment's `Publish Date` repeats its parent's; its own date is `Applicable Publish Date`
     (true of all 105,679 amendments), which `published` now uses.
   - An amendment carries the contract's new total, not the change. In the bulk file each amendment's `Value` is the
     parent's plus every `Amendments Value` so far; in the API 91% of later notices raise the value and none is
     negative. So a contract's value is its latest notice's, and summing notices counts it once per amendment.
   - Asking the API by the date published returns amendments only for contracts published from July 2019 (it held 187
     amendments to older ones), so the bulk file's contracts lacked every amendment made after the file closed. The API
     is now also asked, by id, for each contract in the bulk file still running on its last day (a latest end date on or
     after 30 August 2019): 44,461 contracts, of which 33,661 were first published before July 2019 (worth $260.7
     billion at their latest notice in the bulk file) and 10,800 in July and August 2019, which the other query holds
     too. The answer is each contract's whole history. It adds 28,698 amendments to 10,494 of the older contracts, and
     their value at the latest notice goes from $179.5 billion to $303.7 billion (all 33,661: from $260.7 billion to
     $385.0 billion). Of the 10,494, 9,747 rise, 186 stay the same and 561 fall (by $2.5 billion in all): the Hunter
     class frigates' design and build went from $2.3 billion to $15.7 billion over 20 amendments.
   - The API re-released many notices in batches and dates them by the batch (all ten of one 2018 contract's amendments
     carry 22 September 2025). So `published` is the earliest date any part gives a notice, and `published_batch` marks
     the 137,147 notices whose date is still a batch's (39,454 on 27 April 2023); the amendment number, not the date,
     orders a contract's notices. A notice that comes back from both queries, or twice, is kept once, with its latest
     version's values.
   - Asking by the date last modified, as first planned, was dropped: that record begins in May 2023, and each weekly
     window from July 2023 pages back through thousands of older contracts and all their releases (in two hours, four
     workers finished none of them).
   - Still missing: amendments made after August 2019 to contracts that had ended by then. In a random sample of 150
     that ended in the year before, 16 had later amendments, adding $2.4 million in all; of 150 that ended earlier, 5
     did ($1.5 million), and the API held nothing for 82. Scaled up, that is roughly $1 billion and $7 billion, but
     samples this small are only a guide for values this skewed. Asking for all 780,613 would take about a day.
   - Quirks of the sources, each handled: eight API releases are contracts under an amendment's id (CN444842-A3),
     which had each counted as a contract of its own ($72 million in all) and are now read as that amendment; four
     notice ids appear twice in the bulk file with different values (CN1689431-A1: $165,000 in May 2015 and $185,000
     in June 2016), and each is kept once, at its later version; four bulk notices have malformed ids
     (CN221277-A1-A) and no parent notice, so their `amendment` is empty.
   - Values keyed in the wrong units: 70 notices are at least 100 times their contract's previous notice and $100
     million or more ($59.0 billion in all). Most are corrected by the next notice; 8 are a contract's latest ($11.6
     billion), such as a data-capture service whose amendments run from $0.7 million to $6.6 million, then $9,626
     million. `value_jump` flags them; values are left as published, since a few may be real (a pilot become a
     programme), and the flag lets an analysis set them aside.
   - Result: 1,577,643 notices for 1,272,234 contracts. One row per contract at its latest notice gives $1,258.5
     billion; summing every notice gives $7,585.9 billion, six times as much.
3. **The ABN spine (`linkage`): every IP applicant, and each contract once (B2, A1).**
   - Every ABN of an applicant or owner of any right in IP RAPID's party table (founding or current) is now in the
     spine, not just founding applicants with filings: 6,466 more ABNs, 398,450 in all. Every ABN the `rights`
     lens credits a right to is now in the spine; before, 11,525 rights (1,179 patents, 10,017 trade marks and 329
     designs) were credited to 5,903 ABNs outside it, so they fell out of the `firms` lens.
   - `in_iprapid_patent` and the like now mean "an applicant or owner of that right, founding or current".
   - `austender_contracts` and `austender_value` count each contract once, at its latest notice, for the supplier that
     notice names (2,224 contracts changed supplier, usually by novation): 1,199,500 contracts with a supplier ABN,
     $1,077.3 billion, for 72,042 suppliers.
4. **R&D Tax Incentive (`rdti`): ABNs from ACNs.** 521 of the 551 rows without an ABN take it from the ABR, where
   exactly one ABN holds the row's ACN (471 of 478 ACNs): $228 million of R&D that would otherwise drop out of every
   join on ABN. `abn_from` records which. 30 rows ($16 million) have no usable identifier. Two of the 521 repeat an
   ABN's own row for the same year (a later report's restatement, at the same value), which the lens's latest-report
   rule handles.
5. **SDMX flows (`_abs.py`, `oecd`): every value kept (B10, F01).** `value_text` keeps any cell that is not a plain
   number, in the flows that have one; a percentage written as "12.5%" is read as 12.5. The OECD's IP tax regimes
   had lost all 2,639 values; now 839 rates are numbers and the rest (the FHTP's verdict on each regime, its name, the
   assets that qualify, comments) are text. No other flow had a non-numeric value.
6. **World Bank (`wdi`): trade marks (F02).** `IP.TMK.RSCT` and `IP.TMK.NRCT` (resident and non-resident applications,
   by count) replace three codes the World Bank withdrew: 5,181 values (4,677 for countries, the rest for regional
   groups), 2004 to 2024. The other 22 indicators came back byte for byte.
7. **CER (`cer`): each value once (B11; F29, F30).** Each series is read from its CSV only: every workbook sheet
   repeated a CSV exactly, so 7,051,130 rows become 3,494,496, one per technology, series, postcode and month. The
   files' total columns are left out as sums of the months (checked to the unit for solar, wind and water heaters),
   which also removes the broken `2010)` labels. New columns `technology`, `series` and `month`. The state battery
   file, which had been read as postcodes, is its own table, `battery_states`.
8. **PHIDU (`phidu`): indicators told apart, and placed (B12).**
   - Each sheet's columns sit under up to three label rows. The loader read only the first, so the sub-indicator (the
     cancer type, the developmental domain) was lost and 62,893 keys on the health sheets held several values. Now
     `indicator`, `sub_indicator` and, where the top row is a caveat, `note`. Where two column groups carry the same
     labels (the quintiles' two migrant sheets), each takes its first measure as its sub-indicator.
   - `area_type` (`pha`, `sa3`, `sa4`, `total` or `quintile`): each sheet lists the PHAs, then named totals, then SA4s
     and SA3s, and SA3 codes have five digits like PHA codes, so a join on `area_code` alone could match an SA3 to a
     PHA.
   - `pha_sa2`, from the `PHAs` sheet: 2,450 SA2s in 1,165 PHAs, each SA2 in one PHA. With `abs_regions/poa_sa2` it
     places the indicators in postal areas.
   - 185 spacer rows (zeros, with no area) are dropped. Every row's key is now unique (the build checks it).
9. **CABEE (`abs_cabee`): survival rates by size.** In cubes 4 to 7, each survival rate sits beside the count of its
   size range, but every rate was labelled "Survival rate", so the rates of different size ranges could not be told
   apart (12,682 rows were exact duplicates). The national tables had the same fault, and Table 14's periods
   ("change in size category from June 2022 to June 2023") were lost. Both tables now have one row per key (the build
   checks it).
10. **ABS data cubes (`_abs_cube.py`, used by `abs_rd_vc`): every cell kept (B10, F36).** A number with a footnote
    ("0 (b)") is read as the number; a cell that is not a number ("np", not published; "-") is kept with an empty
    `value`; both keep the cell in `value_text`. A row that states its own unit (HERDDC01's $'000 and person-years) has
    it in `unit`. `sheet_row` gives each value's row in the sheet, because section rows nest by indentation, which the
    cells do not record (the venture capital tables' "Residents" sits under both "New commitments" and "Capital
    called").
11. **ARTG (`tga`).** The export's exact repeats (20 rows) are dropped. An entry can list several products (429 do),
    so `artg` is one row per entry and product, as its description now says.
12. **Policy events (`policy_events`): every date checked (B7, N05).** All 13 dates were checked against the
    Register's legislation histories (the endnotes of each Act's latest compilation) and the 2018 Act's commencement
    table:
    - the Patents Act 1990 commenced on 30 April 1991 (s 2(2)), not 1 May;
    - the Productivity Commission response Part 1 commenced in two steps: parallel importation (Schedule 1 Part 1) on
      25 August 2018, and the trade mark non-use period, plant breeder's rights in essentially derived varieties and
      most procedural changes on 24 February 2019. The event had put parallel importation in 2019. It is now two
      events;
    - the four flagged dates (the PBR Act, pharmaceutical extensions of term, the 2019 commencement, the designs grace
      period) are right;
    - two enactment dates are added, for modelling anticipation: Raising the Bar's Royal Assent (15 April 2012) and the
      innovation patent phase-out's (26 February 2020).

    Sixteen events, none left to verify; each `source` names the Act checked.

**Left as published, and why.** Exact duplicate rows remain where the source has them: IP RAPID's party (27,487),
description (1,464), links (383) and classification (103) tables, TM-Link (15,732), ASIC's company names (59), the
tax transparency reports (1) and the wine GI register (1). Every lens that reads these counts distinct rights, parties
or applicants, so they change no figure, and keeping the source's rows keeps the tables checkable against it.

**Not done, and why.**
- IPC subclasses missing from the ALP industry concordance (B6): 3,853 patents (0.29% of classified ones) have no
  matched subclass and 7,743 more have some unmatched; mostly new subclasses (G16H, G06V, F24S, G16B, H10F) and old
  ones (B29F to B29J). A map to their predecessors belongs with the `industries` lens, which is built later.
- Historical fees (R3, B8) and the PBS monthly report with Section 100 (B9): more than an easy fix; still the plan's
  largest gaps for later stages.
- Amendments made after August 2019 to the bulk file's contracts that had ended by then (item 2): about a day of
  asking by id, for what a sample suggests is under 1% of the contracts' value. `austender._harvest_by_id` can do it
  outside a session.

**Checked.**
- Tests on small inputs for each repaired parser (SDMX values, cube cells, CABEE survival rates, PHIDU labels and
  area types, AusTender amendment numbers and dates, RDTI's ACN rule, CER's months), and on the committed tables: one
  row per key for every repaired table, every IP tax regime value kept, each contract counted once in the spine, and
  every policy event checked (`tests/test_corpus.py`).
- The duplicate scan, re-run after the repairs, finds exact duplicates only in the tables listed above.
