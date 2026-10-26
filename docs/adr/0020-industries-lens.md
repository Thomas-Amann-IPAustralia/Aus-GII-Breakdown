# 0020: The industries lens: IP by division through probabilistic crosswalks, beside the ABS's industry tables

**Date:** 2026-10-26. **Whose:** Claude's (the owner asked for the `industries` lens next, 2026-10-26); the owner can
overturn any of it. It builds the lens ADR 0007 planned, carries out the review's B6 and repairs the corpus's
crosswalk to ANZSIC. The evidence is in `analysis/notebooks/01_univariate.ipynb`, section 6 (observations U73 to U79).

**Context.** ADR 0007 set the unit: an ANZSIC division and financial year, holding business counts, entries, exits and
survival, innovation and barriers by firm size, business R&D, wages by industry, and IP rights assigned to industries
through the IPC and Nice crosswalks. No firm in the corpus has an industry (the ABR extract holds none, the review's
N04), so IP can reach industries only through what it protects. The corpus holds ALP's crosswalks (Lybbert and Zolas:
IPC subclass to ISIC Rev. 4, *excluding services*, version 2209; Nice class to ISIC Rev. 4, version 2305) and the
ABS's ISIC to ANZSIC correspondence. The ABS's industry tables are CABEE (national release by division, FY2023 to
FY2026, and cubes by state, class, subdivision and local government area), the BCS (13 tables, 2018 to 2023), BERD
(2023-24, by subdivision), the WPI (quarterly by division) and BCARR's cultural and creative accounts (two releases).

**Decision.**
1. **The core lens, `industries`:** one row per division (A to S) and financial year, FY1990 to FY2026 (703 rows).
   FY1990 because IP RAPID records few overseas applicants' countries before 1989 (U67). Columns: expected standard
   patent, second-tier patent and trade mark applications (all, and by Australian applicants); CABEE's businesses at
   the start and end of the year, entries, exits and their rates; BERD (FY2024); the WPI (total hourly rates excluding
   bonuses, all sectors, the financial year's average of four quarters); and creative value added (BCARR's newer
   release).
2. **IP by expected counts.** A right's current classes share it equally (1/n), each class's ALP weight is split over
   ANZSIC classes, and the shares are summed by division, so each right sums to 1. A right with no known class is left
   out (98.42% to 99.73% of standard patents and 99.8% of trade marks are carried, U74). Australian applicants are
   those of the current applicant's country, the residents' definition the World Bank and WIPO use, which the lens
   matches (U67).
3. **B6: IPC predecessors.** 26 subclasses the crosswalk does not know (new ones from 2018 to 2026, obsolete B29F to
   B29J, C08D, F21M to F21Q) are mapped to the subclass they came from or merged into (`IPC_PREDECESSORS`). Unknown
   subclass marks fall from 12,143 to 71 of 2,518,546; patents with none known from 3,853 to 20.
4. **Nice classes as two digits.** IP RAPID stores classes 1 to 9 without a leading zero; the crosswalk has '01' to
   '09'. They are padded.
5. **A corpus repair: ISIC to ANZSIC.** `concordances` split each ISIC class's weight equally over every ANZSIC class
   it links to, full or partial. A partial link carries only part of an ANZSIC class, so pharmaceuticals (ISIC 2100;
   full links to human and veterinary pharmaceuticals, partial to textile finishing and inorganic chemicals) sent half
   their weight to the partial ones, and textiles received 8.9% of all standard patents. An ISIC class's weight now goes
   equally to its full links, and only where it has none to its partial links (264 of the 415 ISIC classes have only
   partial links, 96 have both). Textiles fall to 2.3% of patents and chemicals rise to 30.2%. `concordances` has a
   `reprocess` that rebuilds the crosswalks from the raw files in the repo.
6. **One long table, `industry_indicators`** (1,409,875 rows): one row per division, source, indicator and period,
   for every value the ABS and BCARR publish by industry (CABEE's cubes, except the SA2 ones in `region_indicators`,
   and its national tables 1 to 3; the 13 BCS tables; BERD by subdivision; BCARR's industry tables in both releases;
   the WPI, quarterly), and the core lens's IP counts by subdivision (source `ip`). All industries is `TOTAL`, an
   industry the ABS could not code `X`. The core lens's own values are not repeated. Divisions are found from codes
   (a subdivision's two digits fall in one division's range) or from names (the divisions' and CABEE's subdivision
   names).
7. **The Australia-wide tables of the same releases go to `national_indicators`** (as ADR 0019 promised): CABEE's
   national tables 4 to 16, the ABS's R&D for government, private non-profits and higher education, BERD's summaries,
   venture capital to 2018-19, and BCARR's creative domains. ABS cube rows are keyed by their row on the sheet as well,
   because the cube reader records two levels of heading and the venture capital tables have three, so 469 values
   shared a section and row label.
8. **BCARR's two releases are never spliced.** They overlap for FY2016 to FY2023 and agree to within 1.2% (U79); each
   is its own indicator, and the core lens uses the newer one only.

**Use.**
- A division's IP count is an estimate of what its rights protect, with patents limited to goods-producing industries:
  manufacturing receives 90.8% of standard patents (U75). Read patents by subdivision within manufacturing
  (`industry_indicators`, source `ip`), and remember that a subdivision count is a spread estimate (U74).
- Trade marks by industry break in January 2002, when the Nice classification's 8th edition split class 42 into 42 to
  45 (U75): compare from FY2003, or across the break with that caveat.
- Never add `TOTAL` to the divisions. CABEE's divisions plus `X` equal its total (a test checks).
- The BCS flags 36.2% of its values for sampling error and withholds 25%; compare divisions with care.

**Rejected.**
- **Assigning firms to industries by their name or their main patent class.** It would make an industry for each IP
  filer, but an untested one; the crosswalks are published and probabilistic, and say so.
- **Weighting partial links by business counts** (CABEE's classes). It would favour industries with many small firms
  (textile finishing has 742 businesses against human pharmaceutical manufacturing's 596, June 2025), the opposite of where the technology is.
- **A crosswalk that includes services.** ALP publishes one, free; it would change the patent counts' meaning rather
  than repair them, and is a decision for Stage 2 (a lead, in the handover).
- **Splicing BCARR's releases** or keeping only the newer: the older one runs back to FY2009.

**Checked.**
- `tests/test_eda.py`: one row per key in both tables; the division of a class or subdivision code; each right's
  shares sum to one, so the divisions hold between 98% and 100% of the year's standard patents and 99.5% to 100% of its
  trade marks (FY2000 to FY2024); CABEE's divisions and its unknown industry sum to its total; business R&D's divisions
  sum to the ABS's total to within its rounding.
- The lenses as built: `industries` 703 rows and 17 columns; `industry_indicators` 1,409,875 rows and 12 columns;
  `national_indicators` 41,203,167 rows (7,086 more).
