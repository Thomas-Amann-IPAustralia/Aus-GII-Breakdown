# 0032: Firms' size and industry from WGEA, for employers of 100 or more; nothing free for smaller firms

**Date:** 2026-10-28. **Whose:** the owner asked for the data gaps to be filled (A15, `docs/data-gaps-brief.md`, gap
A3: firms' size and industry, the third factors most firm leads need, B21 to B24); Claude searched and chose.

**Context.** The firms lens has no industry and no size beyond income for the largest taxpayers (`ato_ctt`) and R&D
spend for claimants (`rdti`). The ABS's BLADE is ruled out (it needs DataLab, an account and a fee). The brief asked
for free firm-level sources to be tried first.

**What was searched, and what each holds by ABN:**

| Source | Size | Industry | Coverage | Verdict |
|---|---|---|---|---|
| ABR public extract (`abr`) | no | no (no ANZSIC) | every ABN | already in the corpus; no help |
| ASIC company register (`asic`) | no (company type only) | no | companies | already in the corpus; no help |
| R&D Tax Incentive transparency (`rdti`) | R&D spend | no | every claimant | already in the corpus |
| ATO corporate tax transparency (`ato_ctt`) | total income | no | income of $100m or more (private) | already in the corpus |
| AusTender (`austender`) | no | UNSPSC of what is bought, not ANZSIC of the seller | suppliers | not an industry |
| **WGEA public data** (data.gov.au, CC BY 3.0 AU) | **headcount and size band** | **ANZSIC class** | **every private employer of 100 or more (8,240 in 2024-25)** | **taken** |
| ACNC charity register (data.gov.au) | revenue band (small, medium, large) | charitable purposes, not ANZSIC | charities | not taken: a revenue band and purposes, not an industry; worth adding if a charity or university question needs it |

**Decision.**

1. **A corpus source, `wgea`, reads WGEA's public data files for 2022-23, 2023-24 and 2024-25** (the workforce
   composition, one row per ABN, occupation, status and gender) into `employers`: one row per year and ABN, with the
   size band, the ANZSIC class and division, headcount, women and managers. In 2022-23 a submission group reports under
   its primary ABN only, with the group's size band; from 2023-24 each employer reports under its own ABN.
2. **The firms lens takes each firm's latest report** (`wgea_year`, `wgea_employees`, `wgea_size_band`,
   `wgea_division`, `wgea_anzsic_class`, `wgea_women_share`). 7,126 firms in the lens have one. They are left out of
   the lens's screen (whose pairs Stage 2 has reported) and read among the firms they cover, in their own section
   (U112; B50 and B51).
3. **Small firms stay without size or industry.** No free source gives either for firms under 100 employees by ABN.
   The options for the owner, if the questions need them, are those the brief names: ABS DataLab (BLADE; an account,
   a project approval and a fee), or a classification of firms from their names, websites or IP classes (free, but an
   estimate, not a record). Neither is started.

**Consequences.** Industry and size are third factors for large employers only, who file 18.41% of the lens's
standard patents but are 1.59% of its IP filers (U112). Any finding about size from WGEA is about firms of 100 or
more.
