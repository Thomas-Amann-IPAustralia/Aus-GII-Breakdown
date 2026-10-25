# ABS TableBuilder: owner-managers from the 2021 Census

> **On hold (2026-10-25).** The owner doubts that the project meets the ABS's conditions of use. Do not download until
> the owner has settled two things:
> - the registration route, which for IP Australia work should be through IP Australia's ABS organisation;
> - whether IP Australia's own rules allow ABS tables to be kept in this repository and the R2 bucket and analysed with
>   an AI assistant.
>
> The ABS's strict rules (undertakings, secure storage, no disclosure) are for unit-record microdata. TableBuilder gives
> only aggregated, confidentialised tables, which the ABS says may be published with attribution. Open sources cover
> the national picture meanwhile: see "Data worth adding" in `docs/eda-plan.md`.

**What this is for.** People who run their own business ("owner-managers"), counted by postal area, industry, sex,
Indigenous status and age. They are the denominators for questions such as how many of a place's, an industry's, or a
group's business owners use the IP system. They feed the `regions` and `industries` lenses and the national view
(ADR 0007). TableBuilder is free, but it needs an account in the owner's name, so the owner downloads the tables.

**What to get.** Six tables (the sixth is optional). Each counts **persons by Status in Employment (SIEMP)**, which
splits employed people aged 15 and over into employees; owner-managers of incorporated and of unincorporated
enterprises, each with or without employees; contributing family workers; and not stated or not applicable. Keep every
category and the totals.

| File name | Rows | Columns | Wafer | Size |
|---|---|---|---|---|
| `owner_managers_poa_sex.csv` | Postal Areas (POA) | Status in Employment (SIEMP) | Sex (SEXP) | about 90,000 cells |
| `owner_managers_poa_indigenous.csv` | Postal Areas (POA) | SIEMP | Indigenous Status (INGP) | about 170,000 cells |
| `owner_managers_industry_sex.csv` | Industry of Employment (INDP), 1-digit level | SIEMP | Sex | small |
| `owner_managers_industry_indigenous.csv` | INDP, 1-digit level | SIEMP | Indigenous Status | small |
| `owner_managers_age_sex.csv` | Age in Ten Year Groups (AGE10P) | SIEMP | Sex | small |
| `owner_managers_poa_industry.csv` (optional) | Postal Areas (POA) | SIEMP | INDP, 1-digit level | about 700,000 cells; it may be queued |

A *wafer* is TableBuilder's third dimension: one layer of the table for each category, such as one for males, one for
females and one for the total. Download every table as CSV: TableBuilder's Excel format stops at 100,000 cells.

## Click by click

**Register and log in (once)**
1. Go to <https://www.abs.gov.au/statistics/microdata-tablebuilder/tablebuilder>.
2. Click **Log in to TableBuilder**. Without an account yet, follow **Register**: fill in the form, accept the
   conditions of use, and confirm from the email the ABS sends.
3. Log in.

**Open the dataset**
4. On the TableBuilder home page, click the triangle beside the Census folder to show its datasets.
5. Select **2021 Census - employment, income and education** and click **New table** (or double-click it).
   - If that dataset has no *Status in Employment*, go back and open **2021 Census - counting persons, place of usual
     residence** instead.
   - The count should be persons by place of usual residence, TableBuilder's default for these datasets.

**Build the first table (postal area by status in employment by sex)**
6. In the left panel, open the geography folder for usual residence (*Geographical Areas (Usual Residence)*), then
   **Postal Areas (POA)**.
7. Tick the box beside the variable name to select every postal area, then click **Add to Row** at the top of the panel.
8. Find **SIEMP Status in Employment**, in a folder for employment or the labour force (or use the search box above the
   list, if there is one).
9. Tick the box beside the variable name to select all its categories, then click **Add to Column**.
10. Find **SEXP Sex**, in *Selected Person Characteristics* or similar. Select all its categories and click
    **Add to Wafer**.
11. Click **Retrieve data**. If TableBuilder says the table is too big to show, accept its offer to queue it, and open
    it later from **Saved and large tables** (click **View**).
12. Download it from the top right. Choose **Comma Separated Value (.csv)** as the format, then click
    **Download table** (or **Go**). Save it as `owner_managers_poa_sex.csv`.
13. Optional: click **Save table** to keep the layout for next time.

**The other tables.** Click **New table**, or remove a variable by dragging it out of the table, then:

14. `owner_managers_poa_indigenous.csv`:
    - Rows: Postal Areas.
    - Columns: SIEMP.
    - Wafer: **INGP Indigenous Status**, all categories.
15. `owner_managers_industry_sex.csv`:
    - Rows: **INDP Industry of Employment** at the 1-digit level. Click the small arrow at the end of the variable name,
      choose the 1-digit (division) level, then **Add to Row**.
    - Columns: SIEMP.
    - Wafer: Sex.
16. `owner_managers_industry_indigenous.csv`: as step 15, with Indigenous Status as the wafer.
17. `owner_managers_age_sex.csv`:
    - Rows: **AGE10P Age in Ten Year Groups**.
    - Columns: SIEMP.
    - Wafer: Sex.
18. Optional, `owner_managers_poa_industry.csv`:
    - Rows: Postal Areas.
    - Columns: SIEMP.
    - Wafer: INDP at the 1-digit level.

    This one is likely to queue; collect it from **Saved and large tables**.

**Hand the files over**
19. Upload the CSV files to the GitHub repository, anywhere: **Add file**, then **Upload files**, as with earlier
    uploads. Then tell Claude. Claude moves them into `data/raw/abs_owner_managers/`, writes the loader, and checks the
    totals against the Census figures already in the corpus.

## Notes

- **Small cells are unreliable.** The ABS adjusts small cells slightly at random to protect privacy, so small counts
  (under about 10) are unreliable and rows may not add exactly to their totals. The analysis uses counts, not tiny
  shares, and pools small areas.
- **Licence.** CC BY 4.0. The source line is "ABS, Census of Population and Housing 2021, TableBuilder". The conditions
  of use forbid trying to identify anyone.
- **What owner-managers are.** They are people, not businesses. A business with two owners counts twice, and a person
  is counted once, by their main job. The analysis keeps people and businesses apart.
