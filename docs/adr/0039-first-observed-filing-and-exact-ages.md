# 0039: First observed filing is not entry; ages from dates; undated firms have no age; reproducible sums

**Date:** 2026-11-02. **Whose:** the owner asked for the next audit theme, looked at deeply and widely (A20); Claude
chose how. The findings acted on, and the check of each, are in `analysis/GPT-audit/261030/AMENDMENTS.md` (pass 4).

**Context.** The audits' theme "first observed filing treated as true entry" (S1 L0-L1 R31, S1 L2 R50, S2 L2 R17) and
the four findings on the same computation (S2 L2 R15, R16; S1 L2 R54; S8-S9 R15) were checked against the code, the
lenses and both notebooks. They hold, except one part of R31, and the check found more than they did:
1. **Entry.** U101 headed "Firms' entry did not fall" from the first application credited to an ABN. Of each year's
   first observed linked trade mark filers, 4.32% to 9.1% were already linked to IP another way, and filers without an
   ABN are missed, so the counts are neither upper nor lower bounds on new filers.
2. **The age sample.** B25 and B26 said "firms first seen in 2001 or later" but filtered on `NOT age_truncated`, which
   keeps every company dated by ASIC registration, however old (51,712 first seen before 2001). B26's ten-plus band in
   FY2003 to FY2011 held 4,341 patents; restricted to firms first seen from 2001 it holds 2.
3. **The date arithmetic.** Financial years are named by their end, so `fy - 0.5` is a year's start, not its middle;
   B25 dropped filings more than a year before registration and counted the rest as "within the first year"; B26 used
   calendar years. With dates: 17.07% to 19.57% of first filings are dated before the firm's first public
   registration, so a recorded age is not a lower bound on age at filing for about one firm in five.
4. **Undated firms read as old.** `age_truncated` was false, not empty, for the 32,600 firms with no registration date,
   and notebook 2's `AGE` grouping sent a missing age to its last branch, "20 years or more". B22 and B23 did not move
   (every undated firm is inactive or not in the ABR, and those tables use active ABNs), but the firms screen did.
5. **Builds that differ from run to run.** Sums of fractions done in parallel (the regions' split values, the
   industries' expected counts, contract values) differed in their last digits between two builds of the same corpus:
   383,271 values of `region_indicators`, 696 of 703 `industries` rows. A pair on a threshold flipped: B28's leads
   moved between 24,947 and 24,948 from build to build, so pass 2's move of one lead cannot be credited to ADR 0037.
6. **Not confirmed:** R31's claim that IP RAPID's known-origin design shares could be biased either way. IP
   Australia's own counts (`docs/audit-ip-australia.md`, D1) show the unknowns are mostly Australian, so those shares
   are lower bounds, as U102 said.

**Decision.**
1. **"First observed linked filing"**, never "entry" or "first-time filer" without that qualifier (GLOSSARY). U101
   shows, in each year, how many first observed filers were already linked to IP.
2. **Ages from dates.** The firms lens gains `patent_first_date_filled`, `trade_mark_first_date_filled` and
   `design_first_date_filled` (the dates of the filings behind `*_first_fy_filled`); an age at filing is days from
   `first_seen` to the application date over 365.25. A filing before the first registration is reported apart.
3. **Name the sample.** "Not truncated" (ASIC-dated companies in any year, other firms first seen from 2001) is the
   main sample; "first seen from 2001" is shown as a sensitivity check. Which right comes first is compared within
   firms that have both (B25: the trade mark first for 72.86% of 4,550 firms).
4. **Undated is unknown.** `age_truncated` is empty where `first_seen` is; any age grouping gives undated firms their
   own group first.
5. **Exact sums.** `build._exact_sum` adds each term as a decimal fixed to 18 places, so the result is the same in
   any order. Two full builds now give identical tables in all eleven lenses. (An ordered aggregate, tried first, was
   also reproducible but nearly tripled memory and killed the notebook's kernel.)

**Consequences.** B26's lead weakens: the youngest firms' patents moved overseas more in FY2003 to FY2011 (5.79%) but
not clearly in FY2012 to FY2021 (2.89%, its interval overlapping the others'); patents filed before the firm's first
registration move most in both (7.01%, 7.77%). B25's medians lengthen (trade marks 2.61 years, patents 5.22, designs
5.24) and its ordering now rests on a within-firm comparison. U101's rise in first observed filers stands, with its
overstatement measured. Region and industry builds are slightly slower (seconds) and reproducible.
