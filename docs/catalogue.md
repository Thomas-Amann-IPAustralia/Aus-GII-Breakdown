# Data catalogue

Every source in the corpus and every table it holds. Written by `uv run corpus catalogue` from `config/sources.yaml`
and `data/manifest.json`; edit those (or a source's module docstring), not this file. What each source is for, and
what is still missing, is in `docs/data-plan.md`; how to use the corpus is in `README.md`.

**Where a table lives.** *repo* tables are in `data/processed/<source>/<table>.parquet`. *R2* tables are in the
`ipholmes` bucket at `processed/<source>/<table>.parquet`; `corpus.load` and `corpus.path` fetch them once into
`~/.cache/ipholmes` (R2 credentials in `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID` and `R2_SECRET_ACCESS_KEY`).

**Join keys.** `abn` (11 digits, as text) joins IP RAPID, IPLORD, the ABR, ASIC (through `acn`), the R&D Tax Incentive,
AusTender and the corporate tax reports; `linkage/abn_spine` already does it. Postcodes join to ABS geography through
`abs_regions/poa` and `poa_sa2` (a postcode is a postal area code, as text). IPC subclasses join to industries and
technology fields through `concordances`. ISO3 codes join the cross-country sources (`gii`, `oecd`, `wdi`).

## IP RAPID (IP Australia's open IP data, updated weekly; the successor to IPGOD) (`iprapid`)

IP Australia. Tier 1; questions 1, 2, 3, 4. Licence: CC BY 4.0. Source: https://data.gov.au/data/dataset/iprapid

IP RAPID: every Australian patent, trade mark, design and plant breeder's right application, updated weekly.

IP Australia's open data product, the successor to IPGOD (same tables and columns, all four rights in each table, plus
an application date and, for classifications, IP Australia's own technology area). The run takes the current weekly
release, so a rerun brings the corpus up to date.

Raw: the release's zip (R2) and its data dictionary (repo). Processed, typed (dates as dates, ABNs as 11-digit
strings, flags as booleans):

- `application`, `classification`, `description`, `events`, `links`, `party`: the IP RAPID tables as published, every
  right in each, with `ip_right_type` (patent, trade_mark, design, pbr) (R2).
- `<right>_rights`: one row per application of that right: status and key dates; the number of current applicants;
  the first current applicant's party id, name, type, country, state, postcode and ABN; whether any applicant is in
  Australia; whether an attorney or agent acts; the main classification (patents: the first current IPC mark's
  subclass, and IP Australia's technology area; trade marks: the Nice classes, as a count and a list; designs: the
  Locarno class; PBR: the genus). Individuals' names are left out of these (repo) tables; `party` (R2) has them as IP
  Australia publishes them.
- `applicant_year`: applicant (ABN where IP RAPID has one, else party id) by right by financial year: applications
  filed and rights that became enforceable, counted and weighted as IPLORD does (repo).

Useful event types (in `events`): extensions of term for pharmaceutical patents, lapses (renewals not paid),
assignments, registered licences, oppositions and their outcomes, examination requests. The public party data has
no inventors, only applicants, owners, agents and other parties.

| Table | Rows | Where | Columns |
|---|---:|---|---|
| `applicant_year` | 3,184,671 | repo (15.2 MB) | `applicant_id`, `applicant_id_type`, `party_type`, `country_code`, `state_code`, `post_code`, `ip_right_type`, `financial_year`, `filed`, `filed_weighted`, `became_enforceable`, `became_enforceable_weighted` |
| `application` | 4,368,006 | R2 (75.4 MB) | `ip_right_type`, `application_number`, `ip_right_sub_type`, `status`, `application_date`, `earliest_filed_date`, `priority_date`, `gained_registration_status_date`, `gained_enforceable_status_date`, `enforceable_from_date`, `deemed_retired_date` |
| `classification` | 15,209,518 | R2 (164.4 MB) | `ip_right_type`, `application_number`, `classification_system`, `classification`, `classification_importance`, `classification_inventiveness`, `classification_source`, `classifying_country_code`, `classification_date`, `classification_removal_date`, `classification_system_version`, `is_current`, `classification_area`, `coarse_classification_area` |
| `description` | 7,457,402 | R2 (96.8 MB) | `ip_right_type`, `application_number`, `description_type`, `description_value` |
| `design_rights` | 268,782 | repo (4.4 MB) | `application_number`, `ip_right_sub_type`, `status`, `application_date`, `earliest_filed_date`, `priority_date`, `gained_registration_status_date`, `gained_enforceable_status_date`, `enforceable_from_date`, `deemed_retired_date`, `applicant_count`, `applicant_party_id`, `applicant_name`, `applicant_type` … |
| `events` | 49,352,557 | R2 (361.5 MB) | `application_number`, `ip_right_type`, `event_type`, `event_category`, `event_effective_date`, `event_declared_date`, `is_standing` |
| `links` | 3,867,277 | R2 (47.3 MB) | `ip_right_type`, `application_number`, `link_type`, `linked_application_number`, `link_date`, `linked_application_country` |
| `party` | 12,517,064 | R2 (275.2 MB) | `ip_right_type`, `application_number`, `party_id`, `abn`, `party_role_category`, `party_role`, `party_type`, `party_name`, `state_code`, `post_code`, `country_code`, `effective_from_date`, `effective_to_date`, `is_current` … |
| `patent_rights` | 1,752,428 | repo (35.9 MB) | `application_number`, `ip_right_sub_type`, `status`, `application_date`, `earliest_filed_date`, `priority_date`, `gained_registration_status_date`, `gained_enforceable_status_date`, `enforceable_from_date`, `deemed_retired_date`, `applicant_count`, `applicant_party_id`, `applicant_name`, `applicant_type` … |
| `pbr_rights` | 11,732 | repo (0.3 MB) | `application_number`, `ip_right_sub_type`, `status`, `application_date`, `earliest_filed_date`, `priority_date`, `gained_registration_status_date`, `gained_enforceable_status_date`, `enforceable_from_date`, `deemed_retired_date`, `applicant_count`, `applicant_party_id`, `applicant_name`, `applicant_type` … |
| `trade_mark_rights` | 2,335,064 | R2 (53.6 MB) | `application_number`, `ip_right_sub_type`, `status`, `application_date`, `earliest_filed_date`, `priority_date`, `gained_registration_status_date`, `gained_enforceable_status_date`, `enforceable_from_date`, `deemed_retired_date`, `applicant_count`, `applicant_party_id`, `applicant_name`, `applicant_type` … |

- Note: iprapid: release of 2026-10-19T00:32:40.599789

## Intellectual Property Longitudinal Research Data (IPLORD) 2020 (`iplord`)

IP Australia. Tier 1; questions 2, 3. Licence: CC BY 4.0. Source: https://data.gov.au/data/dataset/intellectual-property-longitudinal-research-data-2020

IPLORD 2020: IP Australia's applicant by financial year panel, 1904 to 2020, with the ABN where known.

The public 2020 release covers designs (`d_`), plant breeder's rights (`pbr_`) and trade marks (`tm_`, with
`tm_services_` for service classes); it has no patent columns, although its dictionary describes them. For patents,
and for years after 2020, use `iprapid/applicant_year`, built the same way from IP RAPID.

Raw: the release's zip (R2) and dictionary (repo). Processed: `iplord` (the full data set, typed: ids as text, years
and counts as integers, weighted counts as doubles), in R2; `iplord_abn`, the rows identified by an ABN (repo if it
fits), with `party_name` blank where the ABR records the ABN as an individual (a sole trader).

| Table | Rows | Where | Columns |
|---|---:|---|---|
| `iplord` | 7,303,207 | R2 (58.9 MB) | `lord_party_id`, `lord_party_id_type`, `party_name`, `country_code`, `state_code`, `post_code`, `d_first_earliest_filed_financial_year`, `pbr_first_earliest_filed_financial_year`, `tm_first_earliest_filed_financial_year`, `d_first_gained_enforceable_status_financial_year`, `pbr_first_gained_enforceable_status_financial_year`, `tm_first_gained_enforceable_status_financial_year`, `financial_year`, `d_filed_count` … |
| `iplord_abn` | 2,089,555 | repo (15.0 MB) | `lord_party_id`, `lord_party_id_type`, `party_name`, `country_code`, `state_code`, `post_code`, `d_first_earliest_filed_financial_year`, `pbr_first_earliest_filed_financial_year`, `tm_first_earliest_filed_financial_year`, `d_first_gained_enforceable_status_financial_year`, `pbr_first_gained_enforceable_status_financial_year`, `tm_first_gained_enforceable_status_financial_year`, `financial_year`, `d_filed_count` … |

## ABN Bulk Extract (`abr`)

Australian Business Register. Tier 1; questions 2, 3. Licence: CC BY 3.0 AU. Source: https://data.gov.au/data/dataset/abn-bulk-extract

ABN Bulk Extract: every ABN, current and cancelled, from the Australian Business Register's weekly public extract.

Raw: the two zips (R2), the schema and readme (repo). Processed: `abns`, one row per ABN (R2): status and the date it
took effect, entity type, the main name for non-individuals, state and postcode of the main business location, ACN,
GST status and date, and whether it is a deductible gift recipient. Individuals' (sole traders') names are not kept:
the ABN is the link key, and the corpus does not need personal names. Linked subsets come from `linkage`.

From these: firm age (`abn_status_from` of the first activation is not published, so age is measured from the earliest
of ABN status date, GST date and ASIC registration; see docs/catalogue.md), survival (`abn_status` = CAN and its date),
entity type, and GST registration as a rough marker of turnover of $75,000 or more.

| Table | Rows | Where | Columns |
|---|---:|---|---|
| `abns` | 20,612,369 | R2 (374.7 MB) | `abn`, `abn_status`, `abn_status_from`, `record_last_updated`, `replaced`, `entity_type`, `entity_type_text`, `name`, `state`, `postcode`, `acn`, `gst_status`, `gst_status_from`, `dgr` … |

## ASIC Company Dataset (`asic`)

Australian Securities and Investments Commission. Tier 1; questions 2, 3. Licence: CC BY 3.0 AU. Source: https://data.gov.au/data/dataset/asic-companies

ASIC Company Dataset: every company registered in Australia, current and deregistered, as at the extract.

ASIC publishes one row per company name (current and former). Raw: the zip (R2) and help file (repo). Processed:
`company_names` (every row) and `companies` (one row per ACN: its current name, type, class, status, registration
and deregistration dates, ABN), typed and with snake_case columns.

| Table | Rows | Where | Columns |
|---|---:|---|---|
| `companies` | 4,018,291 | R2 (59.0 MB) | `acn`, `abn`, `name`, `type`, `class`, `sub_class`, `status`, `registered`, `deregistered`, `name_rows` |
| `company_names` | 4,452,194 | R2 (80.8 MB) | `company_name`, `acn`, `type`, `class`, `sub_class`, `status`, `registered`, `deregistered`, `previous_state`, `state_registration_number`, `modified_since_last_report`, `current_name_indicator`, `abn`, `current_name` … |

## Research and Development Tax Incentive, report of entity data (`rdti`)

Australian Taxation Office. Tier 1; questions 3, 4. Licence: CC BY 3.0 AU. Source: https://data.gov.au/data/dataset/research-and-development-tax-incentive

R&D Tax Incentive transparency reports: every company's R&D expenditure as claimed, by income year (ATO).

Raw: each year's xlsx (repo). Processed: `entities`, one row per company per report: name, ABN (or ACN where the
report gives one), total R&D expenditure, any amended total, income year, and the report it came from. A report can
restate earlier years (late lodgements and amendments); keep the latest report's row for a company and year.

| Table | Rows | Where | Columns |
|---|---:|---|---|
| `entities` | 38,512 | repo (0.6 MB) | `rd_expenditure`, `rd_expenditure_amended`, `income_year`, `report`, `sheet`, `name`, `abn`, `acn` |

## Business Characteristics Survey and characteristics of Australian business (innovation, barriers, finance) (`abs_bcs`)

Australian Bureau of Statistics. Tier 1; questions 1, 3, 4. Licence: CC BY 4.0. Source: https://data.api.abs.gov.au/

ABS Business Characteristics Survey and the characteristics of Australian business series, from the ABS Data API.

Innovation activity and status, methods and collaboration, finance, barriers to innovation and to business activity,
markets and competition, performance, IT use, by employment size, industry (ANZSIC 2006) and region where published.
Raw: each flow's CSV (repo, gzipped). Processed: one tidy table per flow, named after the flow in lower case.

| Table | Rows | Where | Columns |
|---|---:|---|---|
| `abs_it_barrier` | 17,550 | repo (0.1 MB) | `flow`, `measure`, `measure_label`, `employment_size`, `employment_size_label`, `industry`, `industry_label`, `innovation_status`, `innovation_status_label`, `region`, `region_label`, `frequency`, `frequency_label`, `time_period` … |
| `abs_it_bus_struc` | 8,460 | repo (0.0 MB) | `flow`, `measure`, `measure_label`, `employment_size`, `employment_size_label`, `industry`, `industry_label`, `innovation_status`, `innovation_status_label`, `region`, `region_label`, `frequency`, `frequency_label`, `time_period` … |
| `abs_it_finance` | 5,576 | repo (0.0 MB) | `flow`, `measure`, `measure_label`, `employment_size`, `employment_size_label`, `industry`, `industry_label`, `region`, `region_label`, `frequency`, `frequency_label`, `time_period`, `unit_of_measure`, `unit_of_measure_label` … |
| `abs_it_innovation` | 3,420 | repo (0.0 MB) | `flow`, `measure`, `measure_label`, `employment_size`, `employment_size_label`, `industry`, `industry_label`, `region`, `region_label`, `frequency`, `frequency_label`, `time_period`, `unit_of_measure`, `unit_of_measure_label` … |
| `abs_it_mktcomp` | 15,300 | repo (0.1 MB) | `flow`, `measure`, `measure_label`, `employment_size`, `employment_size_label`, `industry`, `industry_label`, `innovation_status`, `innovation_status_label`, `region`, `region_label`, `frequency`, `frequency_label`, `time_period` … |
| `abs_it_perf` | 18,900 | repo (0.1 MB) | `flow`, `measure`, `measure_label`, `employment_size`, `employment_size_label`, `industry`, `industry_label`, `innovation_status`, `innovation_status_label`, `region`, `region_label`, `frequency`, `frequency_label`, `time_period` … |
| `abs_it_support` | 630 | repo (0.0 MB) | `flow`, `measure`, `measure_label`, `employment_size`, `employment_size_label`, `industry`, `industry_label`, `region`, `region_label`, `frequency`, `frequency_label`, `time_period`, `unit_of_measure`, `unit_of_measure_label` … |
| `bcs_busgvtsk` | 2,202 | repo (0.0 MB) | `flow`, `measure`, `measure_label`, `employment_size`, `employment_size_label`, `industry`, `industry_label`, `region_class`, `region_class_label`, `innovation_status`, `innovation_status_label`, `region`, `region_label`, `frequency` … |
| `bcs_businf` | 15,132 | repo (0.1 MB) | `flow`, `measure`, `measure_label`, `employment_size`, `employment_size_label`, `industry`, `industry_label`, `region_class`, `region_class_label`, `innovation_status`, `innovation_status_label`, `region`, `region_label`, `frequency` … |
| `bcs_businf2` | 4,077 | repo (0.0 MB) | `flow`, `measure`, `measure_label`, `employment_size`, `employment_size_label`, `industry`, `industry_label`, `region_class`, `region_class_label`, `innovation_status`, `innovation_status_label`, `region`, `region_label`, `frequency` … |
| `bcs_inn` | 10,796 | repo (0.1 MB) | `flow`, `measure`, `measure_label`, `employment_size`, `employment_size_label`, `industry`, `industry_label`, `region_class`, `region_class_label`, `innovation_status`, `innovation_status_label`, `region`, `region_label`, `frequency` … |
| `bcs_innact` | 11,287 | repo (0.1 MB) | `flow`, `measure`, `measure_label`, `employment_size`, `employment_size_label`, `industry`, `industry_label`, `region_class`, `region_class_label`, `innovation_status`, `innovation_status_label`, `region`, `region_label`, `frequency` … |
| `bcs_innsig` | 2,351 | repo (0.0 MB) | `flow`, `measure`, `measure_label`, `employment_size`, `employment_size_label`, `industry`, `industry_label`, `region_class`, `region_class_label`, `innovation_status`, `innovation_status_label`, `region`, `region_label`, `frequency` … |

## Counts of Australian Businesses, including Entries and Exits (`abs_cabee`)

Australian Bureau of Statistics. Tier 1; questions 2, 4. Licence: CC BY 4.0. Source: https://www.abs.gov.au/statistics/economy/business-indicators/counts-australian-businesses-including-entries-and-exits

Counts of Australian Businesses, including Entries and Exits (ABS 8165.0): the denominators for IP use.

Data cube 1 (national tables) from the latest release; cubes 2 to 11 (by state and industry class, survival by
subdivision, and by SA2 and LGA, each by employment and turnover size) from the latest release that has them, as the
ABS publishes those in December. Raw: the xlsx cubes (repo). Processed, long tables (one value per row):

- `national`: cube 1, every table: `table`, `table_title`, `period`, `row` (the row's label), `column`, `value`.
- `cubes`: cubes 2 to 11: `cube`, `table`, `table_title`, the cube's own id columns (state, industry code and label,
  SA2 or LGA code and label), `measure` (for example "Operating at start of financial year"), `size` (the employment
  or turnover range) and `value`.

| Table | Rows | Where | Columns |
|---|---:|---|---|
| `cubes` | 3,169,744 | repo (4.2 MB) | `cube`, `table`, `table_title`, `state_name`, `anzsic_industry_code`, `anzsic_industry_label`, `measure`, `size`, `unit`, `value`, `release`, `state_label`, `anzsic_subdivision_code`, `anzsic_subdivision_label` … |
| `national` | 3,339 | repo (0.0 MB) | `table`, `table_title`, `period`, `row`, `column`, `value`, `release` |

## SEIFA 2021, Data by Region and ASGS correspondences (`abs_regions`)

Australian Bureau of Statistics. Tier 1; questions 2, 4. Licence: CC BY 4.0. Source: https://data.api.abs.gov.au/

Places: ASGS 2021 geography, SEIFA 2021 and Data by Region, to put IP users and businesses in context.

Raw: the ASGS allocation files (mesh block to every structure, postal areas and remoteness) and the 2021 Census mesh
block counts (R2); SEIFA and Data by Region from the ABS Data API (repo, gzipped, or R2 when large). Processed:

- `mesh_blocks`: every 2021 mesh block with its SA1 to SA4, GCCSA, state, postal area (POA), remoteness area, and
  usual resident persons and dwellings (2021 Census).
- `poa_sa2`: postal area to SA2, with each pair's share of the postal area's persons (for apportioning postcode data).
- `poa`: one row per postal area: persons, its main SA2, SA3, SA4 and state (most persons), and remoteness (most
  persons; and the share in major cities).
- `seifa_poa`, `seifa_sa2`: SEIFA 2021 indexes (scores, ranks, deciles), tidy.
- `region_asgs`, `region_remoteness`, `region_lga`: Data by Region 2011 to 2025 (population, economy and industry,
  income, education, health and more), tidy.

IPGOD and IPLORD give postcodes; map a postcode to a POA by its four digits (POA codes are postcodes, with a few
postcodes that have no POA, such as PO boxes; those cannot be placed).

| Table | Rows | Where | Columns |
|---|---:|---|---|
| `mesh_blocks` | 368,286 | repo (3.8 MB) | `mb_code`, `mb_category`, `sa1_code`, `sa2_code`, `sa2_name`, `sa3_code`, `sa3_name`, `sa4_code`, `sa4_name`, `gccsa_code`, `gccsa_name`, `state_code`, `state_name`, `area_albers_sqkm` … |
| `poa` | 2,644 | repo (0.1 MB) | `poa_code`, `persons`, `sa2_code`, `sa2_name`, `sa3_code`, `sa3_name`, `sa4_code`, `sa4_name`, `state_code`, `state_name`, `ra_code`, `ra_name`, `share_major_cities` |
| `poa_sa2` | 5,904 | repo (0.1 MB) | `poa_code`, `sa2_code`, `sa2_name`, `persons`, `share` |
| `region_asgs` | 6,484,615 | repo (42.4 MB) | `flow`, `data_item`, `data_item_label`, `region_type`, `region_type_label`, `region`, `region_label`, `frequency`, `frequency_label`, `time_period`, `unit_of_measure`, `unit_of_measure_label`, `unit_of_multiplier`, `unit_of_multiplier_label` … |
| `region_lga` | 1,180,960 | repo (7.0 MB) | `flow`, `data_item`, `data_item_label`, `region_type`, `region_type_label`, `region`, `region_label`, `frequency`, `frequency_label`, `time_period`, `unit_of_measure`, `unit_of_measure_label`, `unit_of_multiplier`, `unit_of_multiplier_label` … |
| `region_remoteness` | 30,477 | repo (0.1 MB) | `flow`, `data_item`, `data_item_label`, `region_type`, `region_type_label`, `region`, `region_label`, `frequency`, `frequency_label`, `time_period`, `unit_of_measure`, `unit_of_measure_label`, `unit_of_multiplier`, `observation_status` … |
| `seifa_poa` | 116,292 | repo (0.8 MB) | `flow`, `postal_area_code`, `postal_area_code_label`, `index_type`, `index_type_label`, `measure`, `measure_label`, `time_period`, `unit_of_measure`, `unit_of_measure_label`, `observation_status`, `observation_status_label`, `observation_comment`, `value` |
| `seifa_sa2` | 108,768 | repo (0.8 MB) | `flow`, `statistical_area_level_2_sa2`, `statistical_area_level_2_sa2_label`, `index_type`, `index_type_label`, `measure`, `measure_label`, `time_period`, `unit_of_measure`, `unit_of_measure_label`, `observation_status`, `observation_status_label`, `observation_comment`, `value` |

## Classification concordances (IPC to technology fields and industries; Nice classes; IPC Green Inventory) (`concordances`)

WIPO and others. Tier 1; questions 1, 2. Licence: see each file's entry in data/raw/concordances/README.md. Source: https://www.wipo.int/

Classification concordances: patents and trade marks to technologies, industries and green technologies.

Raw (repo): `ipc-technology-35.csv`, WIPO's 35 technology fields (Schmoch 2008) as IP Australia reproduces them in
the IPLORD 2020 dictionary (Annex A), transcribed here, with G01B to G01M restored to Measurement as in WIPO's
table;
the ALP crosswalks (Lybbert and Zolas, version 2209 for IPC excluding services, and the Nice crosswalk version 2305);
the ABS correspondence ISIC Rev. 4 to ANZSIC 2006; and the WIPO IPC Green Inventory, taken from the tree embedded in
its web app. Processed:

- `ipc_technology`: the 35 fields' IPC rules (prefix; groups it is limited to; groups or subclass it excludes; and
  `unless_also`, a subclass whose presence on the same patent moves it out of the field, as in WIPO's method).
- `patent_fields`: each IP RAPID patent application's technology fields, from its current IPC marks, with `weight`
  (1/n over its n distinct fields, so each application sums to 1).
- `alp_ipc4_isic4`, `alp_nice_isic4`: the probability-weighted links from IPC subclass, and from Nice class, to ISIC
  Rev. 4 four-digit classes.
- `isic4_anzsic`: ISIC Rev. 4 class to ANZSIC 2006 class (`partial` where the ABS marks the link as partial).
- `ipc4_anzsic`, `nice_anzsic`: the ALP weights carried through to ANZSIC 2006 classes (a weight split equally where
  one ISIC class maps to several ANZSIC classes), with the ANZSIC division.
- `ipc_green_inventory`: the Green Inventory's topics, each with its IPC references, one row per reference.

| Table | Rows | Where | Columns |
|---|---:|---|---|
| `alp_ipc4_isic4` | 3,098 | repo (0.0 MB) | `ipc4`, `isic4`, `weight` |
| `alp_nice_isic4` | 453 | repo (0.0 MB) | `nice`, `isic4`, `weight` |
| `ipc4_anzsic` | 8,384 | repo (0.1 MB) | `ipc4`, `anzsic`, `anzsic_title`, `weight` |
| `ipc_green_inventory` | 346 | repo (0.0 MB) | `level`, `topic`, `title`, `ipc_raw`, `ipc` |
| `ipc_technology` | 369 | repo (0.0 MB) | `field_no`, `field`, `sector`, `ipc_prefix`, `groups`, `except_groups`, `except_prefix`, `unless_also` |
| `isic4_anzsic` | 1,138 | repo (0.0 MB) | `isic4`, `anzsic`, `anzsic_title`, `partial` |
| `nice_anzsic` | 826 | repo (0.0 MB) | `nice`, `anzsic`, `anzsic_title`, `weight` |
| `patent_fields` | 1,909,193 | repo (5.8 MB) | `application_number`, `field_no`, `weight`, `field`, `sector` |

- Note: concordances: nice_anzsic: 0.0% of ALP weight is on ISIC classes the ABS table lacks

## World Gender-Name Dictionary 2.0 (`wgnd`)

WIPO (Harvard Dataverse). Tier 1; questions 2. Licence: CC0 1.0. Source: https://doi.org/10.7910/DVN/MSEGSJ

World Gender-Name Dictionary 2.0 (WIPO, 2021): first names with the gender they are given to, by country.

For estimating the gender of individual applicants in IP RAPID from first names, the method WIPO and IP Australia have
used. IP RAPID's public party data has no inventors, so this covers individual applicants (and owners) only.
Raw: the two Dataverse tables (R2). Processed: `name_gender_code` (name, ISO country code, gender F/M/?, and
`wgt`, the share of the name's bearers of that gender where known) and `name_gender` (the same without country).
Names are as WGND gives them (lower case, accents kept).

| Table | Rows | Where | Columns |
|---|---:|---|---|
| `name_gender` | 3,491,141 | repo (13.2 MB) | `name`, `gender` |
| `name_gender_code` | 4,970,296 | repo (17.7 MB) | `name`, `code`, `gender`, `wgt` |

## Global Innovation Index 2026, data file and Appendix III (`gii`)

WIPO. Tier context; questions 4. Licence: CC BY 4.0. Source: https://www.wipo.int/global_innovation_index/en/

Global Innovation Index 2026 (WIPO): every economy's score, rank and value on every node of the index.

Context for the research (Q4: where Australia stands, and hypotheses about where to look). Raw: WIPO's data file and
Appendix III (repo, as uploaded). Processed: `structure` (the index tree: number, name, level, type, profile,
description, source), `economies` (income group, region, population, GDP), and `data` (one row per economy and node:
the screened value and its data year, the 0-100 score, the rank, and WIPO's strength and weakness flags).
The page in `index.html` reads a frozen summary in `assets/data/gii-australia.json`.

| Table | Rows | Where | Columns |
|---|---:|---|---|
| `data` | 15,290 | repo (0.2 MB) | `iso3`, `economy_name`, `num`, `name`, `datayr`, `value_screen`, `score`, `rank`, `sw_overall`, `sw_incgrp`, `outdated`, `dmc` |
| `economies` | 139 | repo (0.0 MB) | `iso3`, `economy_name`, `income_grp`, `income_grp_code`, `subreg_un`, `subreg_un_code`, `pop`, `pppgdp`, `ppppc` |
| `structure` | 110 | repo (0.0 MB) | `num`, `name`, `level_type`, `type`, `profile`, `description`, `source`, `website` |

## Closing the Gap Annual Data Compilation Report 2026, targets 8, 15 and 16 (`ctg`)

Productivity Commission. Tier 2; questions 1, 2. Licence: see the publisher's terms (the Productivity Commission usually publishes under CC BY 4.0). Source: https://www.pc.gov.au/closing-the-gap-data/annual-data-report

Closing the Gap Annual Data Compilation Report 2026, targets 8, 15 and 16 (Productivity Commission).

Context for a First Nations workstream (economic participation; land and waters; cultures and languages): they
describe the setting, not the IP system's effect. Raw: the three targets' CSVs (repo, as uploaded). Processed: `data`,
long, one value per row: the descriptive columns as published, `jurisdiction` (NSW to NT, Total, Aust) and `value`
(numeric where the cell is a number; `value_text` keeps the cell, for '..', 'np' and the like).

| Table | Rows | Where | Columns |
|---|---:|---|---|
| `data` | 11,264 | repo (0.1 MB) | `target`, `table_number`, `year`, `measure`, `age`, `sex`, `indigenous_status`, `remoteness`, `seifa_irsd`, `description1`, `description2`, `description3`, `description4`, `description6` … |

## AusTender contract notices (`austender`)

Department of Finance. Tier 2; questions 3. Licence: CC BY 3.0 AU. Source: https://api.tenders.gov.au/

AusTender contract notices: Australian Government contracts by supplier (with ABN), value, category and agency.

Two parts, because the OCDS API pages 100 notices at a time (about three seconds a page): the Department of Finance's
cumulative file of notices published to 30 August 2019 (from July 2007), and the API for notices published from
1 July 2019 (weekly windows, fetched four at a time and cached as each finishes, so a rerun resumes). Raw: the bulk
file and the API's responses as gzipped JSON lines (R2). Processed: `contracts`, one row per notice (parent or
amendment) with: `cn_id`, `published`, `signed`, `start`, `end`, `value` (AUD), `description`, `unspsc`, `agency`,
`supplier_name`, `supplier_abn`, `supplier_postcode`, `supplier_state`, `supplier_country`, `procurement_method`,
`source` (bulk or api). Where both parts hold a notice, the API's row is kept. `supplier_name` is blank where
the ABR records the supplier's ABN as an individual (a sole trader).

| Table | Rows | Where | Columns |
|---|---:|---|---|
| `contracts` | 1,548,989 | repo (42.5 MB) | `cn_id`, `published`, `signed`, `start`, `end`, `value`, `description`, `unspsc`, `agency`, `supplier_name`, `supplier_abn`, `supplier_postcode`, `supplier_state`, `supplier_country` … |

## ARC National Competitive Grants Program, grants (`arc_grants`)

Australian Research Council. Tier 2; questions 2, 3. Licence: CC BY 4.0. Source: https://dataportal.arc.gov.au/NCGP/Web/Grant/Grants

ARC National Competitive Grants Program: every grant the Australian Research Council has announced since 2001.

Public research funding by scheme (Discovery, Linkage and others), administering organisation, field of research and
year; Linkage grants are research done with industry and other partners. Raw: the API's pages (repo, gzipped JSON).
Processed: `grants`, one row per grant with every attribute the API gives (nested scheme fields flattened; lists as
'; '-joined text).

| Table | Rows | Where | Columns |
|---|---:|---|---|
| `grants` | 34,977 | repo (11.4 MB) | `id`, `code`, `scheme_name`, `funding_commencement_year`, `scheme_information_schemeCode`, `scheme_information_program`, `scheme_information_submissionYear`, `scheme_information_roundNumber`, `scheme_information_schemeRound`, `current_admin_organisation`, `announcement_admin_organisation`, `grant_summary`, `lead_investigator`, `current_funding_amount` … |

## NHMRC grant outcomes (`nhmrc_grants`)

National Health and Medical Research Council. Tier 2; questions 2, 3. Licence: CC BY 4.0. Source: https://www.nhmrc.gov.au/funding/data-research/outcomes

NHMRC grant outcomes: every grant in the NHMRC's summary of results workbooks, application rounds 2013 to 2026.

Health and medical research funding by institution, scheme, sector and field (Q2 research institutions; Q3 public
funding). The NHMRC site refuses this environment, so the workbooks were downloaded by hand from
https://www.nhmrc.gov.au/funding/data-research/outcomes into data/raw/nhmrc_grants/ (repo); to add a round, put its
workbook there and run `corpus run nhmrc_grants`.

Processed: `grants`, one row per grant from each workbook's grants sheet, with the columns harmonised across the
rounds' layouts (amounts in dollars; keywords '; '-joined). Chief investigators' names and ORCIDs are left out.

| Table | Rows | Where | Columns |
|---|---:|---|---|
| `grants` | 12,224 | repo (2.1 MB) | `application_id`, `round`, `date_announced`, `scheme`, `sub_type`, `grant_opportunity`, `title`, `admin_institution`, `admin_institution_ror`, `state`, `sector`, `participating_institutions`, `international_collaboration`, `collaborating_countries` … |

## Corporate Tax Transparency, report of entity tax information (`ato_ctt`)

Australian Taxation Office. Tier 2; questions 1, 2. Licence: CC BY 3.0 AU. Source: https://data.gov.au/data/dataset/corporate-transparency

Corporate Tax Transparency: total income, taxable income and tax payable of large corporate entities (ATO).

Covers entities with total income of $100 million or more (and, for private Australian-owned companies, $200 million
before 2022-23). Raw: each year's xlsx (repo). Processed: `entities`, one row per entity per income year.

| Table | Rows | Where | Columns |
|---|---:|---|---|
| `entities` | 33,098 | repo (0.7 MB) | `name`, `abn`, `total_income`, `taxable_income`, `tax_payable`, `income_year`, `report`, `sheet`, `acn` |

## OECD comparator panel (R&D, patents, business demography, IP trade, How's Life?) (`oecd`)

OECD. Tier 2; questions 1, 4. Licence: CC BY 4.0. Source: https://sdmx.oecd.org/public/rest/

OECD comparator panel: R&D, patents, protection methods, business demography, venture capital, IP tax regimes and
How's Life? well-being, from the OECD Data Explorer's SDMX API, for every country the OECD publishes.

Raw: each flow's CSV with labels (gzipped; repo when small, R2 when large). Processed: one tidy table per flow (named
below), with a code and a `_label` column for every dimension, then `value`. The flows are the OECD's own; check each
table's `_label` columns for units and breakdowns before comparing.

| Table | Rows | Where | Columns |
|---|---:|---|---|
| `business_births_deaths` | 5,571,658 | repo (30.2 MB) | `flow`, `frequency_of_observation`, `frequency_of_observation_label`, `reference_area`, `reference_area_label`, `measure`, `measure_label`, `economic_activity`, `economic_activity_label`, `size_class`, `size_class_label`, `enterprise_age`, `enterprise_age_label`, `enterprise_type` … |
| `business_high_growth` | 1,070,680 | repo (4.6 MB) | `flow`, `frequency_of_observation`, `frequency_of_observation_label`, `reference_area`, `reference_area_label`, `measure`, `measure_label`, `economic_activity`, `economic_activity_label`, `size_class`, `size_class_label`, `enterprise_age`, `enterprise_age_label`, `enterprise_type` … |
| `business_survival` | 7,546,335 | repo (42.9 MB) | `flow`, `frequency_of_observation`, `frequency_of_observation_label`, `reference_area`, `reference_area_label`, `measure`, `measure_label`, `economic_activity`, `economic_activity_label`, `size_class`, `size_class_label`, `enterprise_age`, `enterprise_age_label`, `enterprise_type` … |
| `innovation_ip_methods` | 1,564 | repo (0.0 MB) | `flow`, `reference_area`, `reference_area_label`, `measure`, `measure_label`, `unit_of_measure`, `unit_of_measure_label`, `economic_activity`, `economic_activity_label`, `enterprise_size_class`, `enterprise_size_class_label`, `r_d_active_status`, `r_d_active_status_label`, `type_of_innovation` … |
| `ip_tax_regimes` | 2,639 | repo (0.0 MB) | `flow`, `reference_area`, `reference_area_label`, `frequency_of_observation`, `frequency_of_observation_label`, `measure`, `measure_label`, `regime`, `regime_label`, `time_period`, `time_period_label`, `value` |
| `msti` | 210,477 | repo (1.6 MB) | `flow`, `reference_area`, `reference_area_label`, `frequency_of_observation`, `frequency_of_observation_label`, `measure`, `measure_label`, `unit_of_measure`, `unit_of_measure_label`, `price_base`, `price_base_label`, `transformation`, `transformation_label`, `time_period` … |
| `patents_coinventors` | 6,824,320 | repo (20.0 MB) | `flow`, `patent_authorities`, `patent_authorities_label`, `frequency_of_observation`, `frequency_of_observation_label`, `measure`, `measure_label`, `unit_of_measure`, `unit_of_measure_label`, `reference_date_type`, `reference_date_type_label`, `reference_area`, `reference_area_label`, `counterpart_area` … |
| `patents_domestic_ownership_abroad` | 6,824,320 | repo (22.3 MB) | `flow`, `patent_authorities`, `patent_authorities_label`, `frequency_of_observation`, `frequency_of_observation_label`, `measure`, `measure_label`, `unit_of_measure`, `unit_of_measure_label`, `reference_date_type`, `reference_date_type_label`, `reference_area`, `reference_area_label`, `counterpart_area` … |
| `patents_environment` | 1,751,776 | repo (5.3 MB) | `flow`, `patent_authorities`, `patent_authorities_label`, `frequency_of_observation`, `frequency_of_observation_label`, `measure`, `measure_label`, `unit_of_measure`, `unit_of_measure_label`, `reference_date_type`, `reference_date_type_label`, `reference_area`, `reference_area_label`, `counterpart_area` … |
| `patents_foreign_ownership` | 6,824,320 | repo (20.6 MB) | `flow`, `patent_authorities`, `patent_authorities_label`, `frequency_of_observation`, `frequency_of_observation_label`, `measure`, `measure_label`, `unit_of_measure`, `unit_of_measure_label`, `reference_date_type`, `reference_date_type_label`, `reference_area`, `reference_area_label`, `counterpart_area` … |
| `patents_regions` | 796,814 | repo (4.8 MB) | `flow`, `frequency_of_observation`, `frequency_of_observation_label`, `territorial_level`, `territorial_level_label`, `reference_area`, `reference_area_label`, `territorial_typology`, `territorial_typology_label`, `patent_authorities`, `patent_authorities_label`, `reference_date_type`, `reference_date_type_label`, `measure` … |
| `patents_wipo_fields` | 4,504,032 | repo (21.9 MB) | `flow`, `patent_authorities`, `patent_authorities_label`, `frequency_of_observation`, `frequency_of_observation_label`, `measure`, `measure_label`, `unit_of_measure`, `unit_of_measure_label`, `reference_date_type`, `reference_date_type_label`, `reference_area`, `reference_area_label`, `counterpart_area` … |
| `venture_capital` | 5,032 | repo (0.0 MB) | `flow`, `reference_area`, `reference_area_label`, `measure`, `measure_label`, `business_development_stage`, `business_development_stage_label`, `unit_of_measure`, `unit_of_measure_label`, `frequency_of_observation`, `frequency_of_observation_label`, `time_period`, `time_period_label`, `observation_status` … |
| `wellbeing_by_sex` | 30,262 | repo (0.1 MB) | `flow`, `reference_area`, `reference_area_label`, `measure`, `measure_label`, `unit_of_measure`, `unit_of_measure_label`, `age`, `age_label`, `sex`, `sex_label`, `education_level`, `education_level_label`, `domain` … |
| `wellbeing_current` | 111,266 | repo (0.5 MB) | `flow`, `reference_area`, `reference_area_label`, `measure`, `measure_label`, `unit_of_measure`, `unit_of_measure_label`, `age`, `age_label`, `sex`, `sex_label`, `education_level`, `education_level_label`, `domain` … |
| `wellbeing_future` | 37,858 | repo (0.2 MB) | `flow`, `reference_area`, `reference_area_label`, `measure`, `measure_label`, `unit_of_measure`, `unit_of_measure_label`, `age`, `age_label`, `sex`, `sex_label`, `education_level`, `education_level_label`, `domain` … |
| `wellbeing_inequality` | 2,055 | repo (0.0 MB) | `flow`, `reference_area`, `reference_area_label`, `measure`, `measure_label`, `unit_of_measure`, `unit_of_measure_label`, `age`, `age_label`, `sex`, `sex_label`, `education_level`, `education_level_label`, `domain` … |

## World Development Indicators, comparator panel (`wdi`)

World Bank. Tier 2; questions 1. Licence: CC BY 4.0. Source: https://api.worldbank.org/v2/

World Development Indicators comparator panel (World Bank): the indicators that bear on the IP system, for every
country and year, from the World Bank's API.

Raw: each indicator's API response (repo, gzipped JSON). Processed: `panel` (country ISO3 and name, indicator code
and name, year, value) and `countries` (ISO3, region, income group, and whether it is an aggregate rather than a
country).

| Table | Rows | Where | Columns |
|---|---:|---|---|
| `countries` | 296 | repo (0.0 MB) | `iso3`, `name`, `region`, `income`, `aggregate` |
| `panel` | 136,371 | repo (1.1 MB) | `iso3`, `country`, `indicator`, `indicator_name`, `year`, `value` |

- Note: wdi: IP.TMK.RESD is no longer in the API (The indicator was not found. It may have been deleted or archived.)
- Note: wdi: IP.TMK.NRES is no longer in the API (The indicator was not found. It may have been deleted or archived.)
- Note: wdi: IP.TMK.TOTL is no longer in the API (The indicator was not found. It may have been deleted or archived.)

## WIPO IP statistics, filings by origin and office (`wipo_ipstats`)

WIPO. Tier 2; questions 3. Licence: CC BY 4.0. Source: https://www3.wipo.int/ipstats/

WIPO IP statistics: filings, grants and rights in force by office and applicant's origin, every country, 1980 on.

Q3: which countries' applicants file where (Australians abroad, foreigners in Australia), including trade marks and
designs, which the World Bank no longer publishes; office workloads (examiners, pendency) for comparison. Read from
the public API behind the WIPO IP Statistics Data Center (https://www3.wipo.int/ipstats/), which serves the same CSV
exports as the site. Each export asks for every office and origin the indicator has. Raw: each export (gzipped CSV;
repo, or R2 when large). Source: WIPO statistics database; cite WIPO.

Processed:
- `office_origin`: one row per indicator, filing office, applicant's origin, breakdown (field of technology or class,
  where the indicator has one) and year. Resident filings are those where office and origin are the same; an
  origin's total is the sum over offices.
- `office`: indicators reported by office only (rights in force, examiners, pendency, oppositions).
- `pmh`: PCT applications by origin, Madrid applications by country of holder and Hague applications by origin.

| Table | Rows | Where | Columns |
|---|---:|---|---|
| `office` | 8,401 | repo (0.0 MB) | `right`, `indicator_id`, `indicator`, `office_code`, `office`, `breakdown`, `year`, `value`, `last_updated` |
| `office_origin` | 4,939,588 | repo (7.2 MB) | `right`, `indicator_id`, `indicator`, `office_code`, `office`, `origin`, `origin_code`, `breakdown`, `year`, `value`, `last_updated` |
| `pmh` | 8,440 | repo (0.0 MB) | `system`, `indicator_id`, `indicator`, `origin_code`, `origin`, `year`, `value`, `last_updated` |

## TM-Link, trade marks linked across offices (`tmlink`)

IP Australia. Tier 2; questions 3. Licence: CC BY 4.0. Source: https://data.gov.au/data/dataset/tm-link

TM-Link (IP Australia and Swinburne University, 2020 release): trade marks from several offices under one schema,
with links between similar marks in different offices (international trade mark families).

For Q3: which Australian owners take their brands abroad, where, and when. Raw: each table's CSV (R2). Processed,
one Parquet table per TM-Link table, all columns as text as published (R2): `tm_link` (the links), `application`,
`owner`, `classification`, `madrid`, `property`. Left out: `description` (goods and services text) and `image-text`
(text read from logos), 1.5 GB of free text the research questions do not need. The dictionary the release cites
(minchulkim87.github.io/tmlink2020) is offline; the columns are as published.

| Table | Rows | Where | Columns |
|---|---:|---|---|
| `application` | 17,366,599 | R2 (56.5 MB) | `ip_office`, `application_number`, `trade_mark_type`, `status`, `application_date`, `priority_date`, `registration_date` |
| `classification` | 14,829,000 | R2 (39.0 MB) | `ip_office`, `application_number`, `nice_class_1`, `nice_class_2`, `nice_class_3`, `nice_class_4`, `nice_class_5`, `nice_class_6`, `nice_class_7`, `nice_class_8`, `nice_class_9`, `nice_class_10`, `nice_class_11`, `nice_class_12` … |
| `madrid` | 690,919 | R2 (2.7 MB) | `ip_office`, `application_number`, `link_type`, `ir_number` |
| `owner` | 18,698,857 | R2 (170.2 MB) | `ip_office`, `application_number`, `owner_type`, `ip_office_owner_identifier`, `owner_country_code`, `owner_name` |
| `property` | 16,767,243 | R2 (31.2 MB) | `ip_office`, `application_number`, `property_type` |
| `tm_link` | 10,651,467 | R2 (72.8 MB) | `ip_office`, `application_number`, `uid_trademark`, `uid_trademark_similar_owners` |

- Note: tmlink: description and image-text tables left out (free text, not needed)

## IP Australia fees, current and historical (`ipa_fees`)

IP Australia. Tier 2; questions 1, 5. Licence: CC BY 4.0. Source: https://www.ipaustralia.gov.au/about-us/fees

IP Australia's current fees, as its website lists them, for the direct cost of obtaining and keeping each right.

Raw: each fees page's HTML (repo, as fetched). Processed: `fees`, every table on those pages, long: `right`, `page`,
`table` (its position on the page), `heading` (the nearest heading above it), `row` (the row's first cell), `column`
and `value` (the cell as published, for example "$250"), with `amount_aud` parsed where the cell is a single dollar
amount. Historical schedules are not here: the Wayback Machine is blocked from this environment, and the dates of
major fee changes are in `policy_events`.

| Table | Rows | Where | Columns |
|---|---:|---|---|
| `fees` | 173 | repo (0.0 MB) | `right`, `page`, `table`, `heading`, `row`, `column`, `value`, `amount_aud` |

- Note: ipa_fees: no tables on https://www.ipaustralia.gov.au/about-us/accountability-and-reporting/fee-review-2023-24

## PBS expenditure and prescriptions (`pbs`)

Department of Health, Disability and Ageing. Tier 2; questions 1. Licence: CC BY 4.0. Source: https://www.pbs.gov.au/info/statistics

PBS date-of-supply data: prescriptions and costs for every PBS item by month (Department of Health, Disability
and Ageing), for the health pathway of public value (section 2 of docs/data-plan.md): what the public pays for
medicines, which can be followed through patent expiry and IP RAPID's pharmaceutical extensions of term.

Raw: every file on the date-of-supply page (R2). Processed: `supply` (every row of the yearly CSVs, July 2020 on:
month, item, drug type, patient category, pharmacy type, script type, prescriptions and the patient, government and
total cost; R2), `item_month` (prescriptions and costs by item and month, summed over the breakdowns; repo) and
`item_drug_map` (item code to drug name, form and strength, and ATC code; repo). The xlsx summary (from July 2022)
and the older date-of-processing zip (to January 2018) are kept raw only.

| Table | Rows | Where | Columns |
|---|---:|---|---|
| `item_drug_map` | 12,187 | repo (0.2 MB) | `item_code`, `drug_name`, `form_strength`, `atc5_code` |
| `item_month` | 279,371 | repo (5.3 MB) | `month`, `item_code`, `prescriptions`, `patient_contribution`, `government_contribution`, `total_cost` |
| `supply` | 2,146,679 | R2 (38.8 MB) | `MONTH_OF_SUPPLY`, `ITEM_CODE`, `DRUG_TYPE`, `PATIENT_CAT`, `PHRMCY_TYPE`, `SCRIPT_TYPE`, `PRESCRIPTIONS`, `PATIENT_CONTRIB`, `GOVT_CONTRIB`, `TOTAL_COST`, `RETAIL_MARKUP`, `PATIENT_NET_CONTRIB` |

## Australian Register of Therapeutic Goods (ARTG) (`tga`)

Therapeutic Goods Administration. Tier 2; questions 1. Licence: CC BY 4.0 (TGA copyright notice; check before republishing). Source: https://www.tga.gov.au/resources/artg

TGA's Australian Register of Therapeutic Goods (ARTG): every medicine and medical device on the register.

The health pathway (section 2 of docs/data-plan.md): how many sponsors supply each active ingredient (generic
competition), and which medicines and devices reach Australia. The TGA site does not respond to this environment, so
the ARTG search export was downloaded by hand (https://www.tga.gov.au/resources/artg, all entries, exported to xlsx)
into data/raw/tga/ (repo). The export is a snapshot of the current register: it has no start or cancellation dates.

Processed: `artg`, one row per ARTG entry (`kind` is medicine where there are active ingredients, device where there
is a device manufacturer); `artg_ingredients`, one row per entry and active ingredient (name in lower case, without
quantities), to join to PBS drugs and to patents' extension of term records by ingredient name.

| Table | Rows | Where | Columns |
|---|---:|---|---|
| `artg` | 98,147 | repo (2.4 MB) | `artg_id`, `product_name`, `sponsor_name`, `device_manufacturer`, `active_ingredients`, `kind` |
| `artg_ingredients` | 99,864 | repo (0.3 MB) | `artg_id`, `ingredient` |

## ABS research and experimental development, and venture capital (`abs_rd_vc`)

Australian Bureau of Statistics. Tier 2; questions 3, 4. Licence: CC BY 4.0. Source: https://www.abs.gov.au/

ABS research and experimental development (businesses, 8104.0; government and private non-profit, 8109.0;
higher education, 8111.0) and venture capital and later stage private equity (5678.0, discontinued after 2018-19).

Who does R&D in Australia, in which industries and fields, and how much, beside who uses the IP system. Raw: each
release's data cubes (repo). Processed: `cubes`, every table long (see `_abs_cube.read_cube`), with `release` and
`cube`.

| Table | Rows | Where | Columns |
|---|---:|---|---|
| `cubes` | 6,564 | repo (0.0 MB) | `sheet`, `title`, `section`, `row`, `column`, `value`, `release`, `cube`, `period` |

## OpenAlex, research output of Australian institutions (`openalex`)

OurResearch. Tier 2; questions 2, 4. Licence: CC0. Source: https://openalex.org/

OpenAlex: the research output of Australian institutions (universities, companies, government, health and others).

Innovation potential by institution and field, to set beside patenting (Q2 research institutions; Q4 the
commercialisation gap). Needs a free OpenAlex API key in `OPENALEX_API_KEY` (OpenAlex no longer serves keyless
requests from shared networks). Raw: the API responses (repo, gzipped JSON). Processed: `institutions` (every
Australian institution: OpenAlex id, ROR, name, type, city, works and citations to date) and `institution_year` (works
and citations by institution and year, as OpenAlex counts them, for the last ten years), and `field_year` (works with
an Australian institution, by primary field and publication year, 2000 on).

| Table | Rows | Where | Columns |
|---|---:|---|---|
| `field_year` | 702 | repo (0.0 MB) | `year`, `field_id`, `field`, `works` |
| `institution_year` | 18,532 | repo (0.1 MB) | `id`, `year`, `works_count`, `cited_by_count` |
| `institutions` | 1,910 | repo (0.1 MB) | `id`, `ror`, `name`, `type`, `city`, `region`, `works_count`, `cited_by_count` |

## Evidence register (key literature and evaluations) (`evidence`)

various. Tier 2; questions 1, 3, 4, 5. Licence: each item's own. Source: docs/evidence-register.md

The evidence register: the literature and evaluations behind the research questions, checked against Crossref.

Raw: `register.yaml` (repo; compiled by hand, add to it freely). For each journal item (with a `venue`) the module asks
Crossref for the closest match to its title and first author, and records the DOI, the title Crossref has and a
similarity score; `match` is false below 0.85, so a reference that does not check out is flagged rather than trusted.
Processed: `register` (one row per item). Also writes docs/evidence-register.md, the register as a readable list.

| Table | Rows | Where | Columns |
|---|---:|---|---|
| `register` | 20 | repo (0.0 MB) | `id`, `kind`, `authors`, `year`, `title`, `venue`, `url`, `why`, `questions`, `doi`, `crossref_title`, `crossref_year`, `crossref_venue`, `similarity` … |

- Note: evidence: ouellette-2012 did not match Crossref well (0.67)

## Cultural and creative activity in Australia (`bcarr_creative`)

Bureau of Communications, Arts and Regional Research. Tier 2; questions 1. Licence: CC BY 4.0. Source: https://www.infrastructure.gov.au/

Cultural and creative activity in Australia (BCARR satellite accounts).

The size of the creative industries, where copyright and design protection operate (section 2 of docs/data-plan.md):
output, gross value added and GDP for each cultural and creative domain, by industry division, and as a share of the
economy, by financial year. The site refuses this environment, so the workbooks were downloaded by hand from the
Bureau of Communications, Arts and Regional Research (infrastructure.gov.au) into data/raw/bcarr_creative/ (repo):
the 2015-16 to 2024-25 release and the 2008-09 to 2022-23 release (both on the refreshed methodology). To add a
release, put its workbook there and run `corpus run bcarr_creative`.

Processed: `activity`, one row per release, table, series and financial year (long; `table_title` names the domain
or breakdown, without its years; `unit` is $m or %). The two
summary tables comparing the first and last years are left out (their figures are in the yearly tables). Use the
newer release where they overlap; the older one runs back to 2008-09.

| Table | Rows | Where | Columns |
|---|---:|---|---|
| `activity` | 3,209 | repo (0.0 MB) | `release`, `table`, `table_title`, `series`, `unit`, `fy_end`, `financial_year`, `value` |

## Measuring What Matters (`mwm`)

Treasury and Australian Bureau of Statistics. Tier 2; questions 1, 5. Licence: CC BY 4.0. Source: https://www.abs.gov.au/statistics/measuring-what-matters

Measuring What Matters (Treasury and ABS): the Australian Government's wellbeing framework, five themes (healthy,
secure, sustainable, cohesive, prosperous) and about 50 indicators, plus overall life satisfaction.

The outcome layer and vocabulary for public value (section 2 of docs/data-plan.md): used to frame and value outcomes,
not to correlate with IP measures. The ABS publishes each indicator as a web page whose charts carry their data as
HTML tables. Raw: each page's HTML (repo, gzipped). Processed: `indicators` (theme, indicator, title, URL) and `data`,
long: `theme`, `indicator`, `table` (its position on the page), `caption`, `row` (the table's first column, usually
the period or group), `column` (the series) and `value` (numeric where the cell is a number; `value_text` keeps it).

| Table | Rows | Where | Columns |
|---|---:|---|---|
| `data` | 5,343 | repo (0.0 MB) | `theme`, `indicator`, `table`, `caption`, `row`, `column`, `value_text`, `value` |
| `indicators` | 50 | repo (0.0 MB) | `theme`, `indicator`, `url`, `title` |

- Note: mwm: no tables on air-quality

## 2021 Census General Community Profile (SA2 and postal areas) (`abs_census`)

Australian Bureau of Statistics. Tier 2; questions 1, 2. Licence: CC BY 4.0. Source: https://www.abs.gov.au/census/find-census-data/datapacks

2021 Census General Community Profile (GCP) for SA2s and postal areas: social capital, health and the workforce.

Stands in for the NATSEM small-area wellbeing and trust estimates, which cannot be fetched: the Census has no life
satisfaction or trust questions, but its small-area measures of social capital (volunteering, unpaid care for others,
residential stability), health (long-term conditions, including mental health conditions, and need for assistance)
and the local workforce (industry, occupation, fields of qualification) let wellbeing and cohesion sit beside regional
IP use (context, not effect; section 2 of docs/data-plan.md). Raw: the ABS DataPacks (short headers; R2). CC BY 4.0.

Processed, for `sa2` and `poa` (postal areas, which join to IP Australia's postcodes):
- `<geo>_g01` and so on: the selected GCP tables as published (one row per area, one column per cell; codes in the
  first column), joined across a table's parts (G19A, G19B and so on).
- `cells`: every cell's short name, long name and table, from the DataPack metadata, to read the columns.

Tables: G01 selected person characteristics; G02 medians and averages; G18 need for assistance; G19 and G20
long-term health conditions; G23 volunteering; G25 unpaid assistance to a person with a disability, health condition
or old age; G43 labour force, education and migration; G44 and G45 address one and five years ago; G46 labour force
status; G50 field of study; G54 industry of employment; G60 occupation.

| Table | Rows | Where | Columns |
|---|---:|---|---|
| `cells` | 16,984 | repo (0.2 MB) | `sequential`, `short`, `long`, `datapackfile`, `profiletable`, `columnheadingdescriptioninprofile` |
| `poa_g01` | 2,643 | repo (0.7 MB) | `POA_CODE_2021`, `Tot_P_M`, `Tot_P_F`, `Tot_P_P`, `Age_0_4_yr_M`, `Age_0_4_yr_F`, `Age_0_4_yr_P`, `Age_5_14_yr_M`, `Age_5_14_yr_F`, `Age_5_14_yr_P`, `Age_15_19_yr_M`, `Age_15_19_yr_F`, `Age_15_19_yr_P`, `Age_20_24_yr_M` … |
| `poa_g02` | 2,643 | repo (0.0 MB) | `POA_CODE_2021`, `Median_age_persons`, `Median_mortgage_repay_monthly`, `Median_tot_prsnl_inc_weekly`, `Median_rent_weekly`, `Median_tot_fam_inc_weekly`, `Average_num_psns_per_bedroom`, `Median_tot_hhd_inc_weekly`, `Average_household_size` |
| `poa_g18` | 2,643 | repo (0.7 MB) | `POA_CODE_2021`, `M_0_4_yrs_Need_for_assistance`, `M_0_4_No_need_for_assistance`, `M_0_4_Need_for_assistance_ns`, `M_0_4_yrs_Tot`, `M_5_14_Need_for_assistance`, `M_5_14_No_need_for_assistance`, `M_5_14_Need_for_assistance_ns`, `M_5_14_yrs_Tot`, `M_15_19_Need_for_assistance`, `M_15_19_No_need_for_assistnce`, `M_15_19_Need_for_assistnce_ns`, `M_15_19_yrs_Tot`, `M_20_24_Need_for_assistance` … |
| `poa_g19` | 2,643 | repo (1.5 MB) | `POA_CODE_2021`, `M_Arthritis_0_14`, `M_Arthritis_15_24`, `M_Arthritis_25_34`, `M_Arthritis_35_44`, `M_Arthritis_45_54`, `M_Arthritis_55_64`, `M_Arthritis_65_74`, `M_Arthritis_75_84`, `M_Arthritis_85_over`, `M_Arthritis_Tot`, `M_Asthma_0_14`, `M_Asthma_15_24`, `M_Asthma_25_34` … |
| `poa_g20` | 2,643 | repo (1.0 MB) | `POA_CODE_2021`, `M_0_cond_0_14`, `M_0_cond_15_24`, `M_0_cond_25_34`, `M_0_cond_35_44`, `M_0_cond_45_54`, `M_0_cond_55_64`, `M_0_cond_65_74`, `M_0_cond_75_84`, `M_0_cond_85_over`, `M_0_cond_Tot`, `M_1_cond_0_14`, `M_1_cond_15_24`, `M_1_cond_25_34` … |
| `poa_g23` | 2,643 | repo (0.6 MB) | `POA_CODE_2021`, `M_15_19_yr_Volunteer`, `M_15_19_yr_N_a_volunteer`, `M_15_19_yr_Voluntary_work_ns`, `M_15_19_yr_Tot`, `M_20_24_yr_Volunteer`, `M_20_24_yr_N_a_volunteer`, `M_20_24_yr_Voluntary_work_ns`, `M_20_24_yr_Tot`, `M_25_34_yr_Volunteer`, `M_25_34_yr_N_a_volunteer`, `M_25_34_yr_Voluntary_work_ns`, `M_25_34_yr_Tot`, `M_35_44_yr_Volunteer` … |
| `poa_g25` | 2,643 | repo (0.6 MB) | `POA_CODE_2021`, `M_15_19_Prvided_unpaid_assist`, `M_15_19_No_unpad_asst_prvided`, `M_15_19_Unpaid_assist_ns`, `M_15_19_Tot`, `M_20_24_Prvided_unpaid_assist`, `M_20_24_No_unpad_asst_prvided`, `M_20_24_Unpaid_assist_ns`, `M_20_24_Tot`, `M_25_34_Prvided_unpaid_assist`, `M_25_34_No_unpad_asst_prvided`, `M_25_34_Unpaid_assist_ns`, `M_25_34_Tot`, `M_35_44_Prvided_unpaid_assist` … |
| `poa_g43` | 2,643 | repo (0.4 MB) | `POA_CODE_2021`, `P_15_yrs_over_M`, `P_15_yrs_over_F`, `P_15_yrs_over_P`, `lfs_Emplyed_wrked_full_time_M`, `lfs_Emplyed_wrked_full_time_F`, `lfs_Emplyed_wrked_full_time_P`, `lfs_Emplyed_wrked_part_time_M`, `lfs_Emplyed_wrked_part_time_F`, `lfs_Emplyed_wrked_part_time_P`, `lfs_Employed_away_from_work_M`, `lfs_Employed_away_from_work_F`, `lfs_Employed_away_from_work_P`, `lfs_Unmplyed_lookng_for_wrk_M` … |
| `poa_g44` | 2,643 | repo (0.2 MB) | `POA_CODE_2021`, `Sme_Usl_ad_1_yr_ago_as_2021_M`, `Sme_Usl_ad_1_yr_ago_as_2021_F`, `Sme_Usl_ad_1_yr_ago_as_2021_P`, `Dif_Usl_ad_1_yr_ago_Sme_SA2_M`, `Dif_Usl_ad_1_yr_ago_Sme_SA2_F`, `Dif_Usl_ad_1_yr_ago_Sme_SA2_P`, `Dif_Us_ad_1_ago_Dif_SA2_NSW_M`, `Dif_Us_ad_1_ago_Dif_SA2_NSW_F`, `Dif_Us_ad_1_ago_Dif_SA2_NSW_P`, `Dif_Us_ad_1_ago_Dif_SA2_Vic_M`, `Dif_Us_ad_1_ago_Dif_SA2_Vic_F`, `Dif_Us_ad_1_ago_Dif_SA2_Vic_P`, `Dif_Us_ad_1_ago_Dif_SA2_Qld_M` … |
| `poa_g45` | 2,643 | repo (0.3 MB) | `POA_CODE_2021`, `Sme_Usl_ad_5_yr_ago_as_2021_M`, `Sme_Usl_ad_5_yr_ago_as_2021_F`, `Sme_Usl_ad_5_yr_ago_as_2021_P`, `Dif_Usl_ad_5_yr_ago_Sme_SA2_M`, `Dif_Usl_ad_5_yr_ago_Sme_SA2_F`, `Dif_Usl_ad_5_yr_ago_Sme_SA2_P`, `Dif_Us_ad_5_ago_Dif_SA2_NSW_M`, `Dif_Us_ad_5_ago_Dif_SA2_NSW_F`, `Dif_Us_ad_5_ago_Dif_SA2_NSW_P`, `Dif_Us_ad_5_ago_Dif_SA2_Vic_M`, `Dif_Us_ad_5_ago_Dif_SA2_Vic_F`, `Dif_Us_ad_5_ago_Dif_SA2_Vic_P`, `Dif_Us_ad_5_ago_Dif_SA2_Qld_M` … |
| `poa_g46` | 2,643 | repo (1.4 MB) | `POA_CODE_2021`, `M_Emp_FullT_15_19`, `M_Emp_FullT_20_24`, `M_Emp_FullT_25_34`, `M_Emp_FullT_35_44`, `M_Emp_FullT_45_54`, `M_Emp_FullT_55_64`, `M_Emp_FullT_65_74`, `M_Emp_FullT_75_84`, `M_Emp_FullT_85ov`, `M_Emp_FullT_Tot`, `M_Emp_PartT_15_19`, `M_Emp_PartT_20_24`, `M_Emp_PartT_25_34` … |
| `poa_g50` | 2,643 | repo (1.3 MB) | `POA_CODE_2021`, `M_NatPhyl_Scn_15_24`, `M_NatPhyl_Scn_25_34`, `M_NatPhyl_Scn_35_44`, `M_NatPhyl_Scn_45_54`, `M_NatPhyl_Scn_55_64`, `M_NatPhyl_Scn_65_74`, `M_NatPhyl_Scn_75_84`, `M_NatPhyl_Scn_85ov`, `M_NatPhyl_Scn_Tot`, `M_InfoTech_15_24`, `M_InfoTech_25_34`, `M_InfoTech_35_44`, `M_InfoTech_45_54` … |
| `poa_g54` | 2,643 | repo (1.6 MB) | `POA_CODE_2021`, `M_Ag_For_Fshg_15_19`, `M_Ag_For_Fshg_20_24`, `M_Ag_For_Fshg_25_34`, `M_Ag_For_Fshg_35_44`, `M_Ag_For_Fshg_45_54`, `M_Ag_For_Fshg_55_64`, `M_Ag_For_Fshg_65_74`, `M_Ag_For_Fshg_75_84`, `M_Ag_For_Fshg_85ov`, `M_Ag_For_Fshg_Tot`, `M_Mining_15_19`, `M_Mining_20_24`, `M_Mining_25_34` … |
| `poa_g60` | 2,643 | repo (1.0 MB) | `POA_CODE_2021`, `M15_19_Managers`, `M15_19_Professionals`, `M15_19_TechnicTrades_Wrs`, `M15_19_CommunPersnlSvc_W`, `M15_19_ClericalAdminis_W`, `M15_19_Sales_W`, `M15_19_Mach_oper_drivers`, `M15_19_Labourers`, `M15_19_Occu_ID_NS`, `M15_19_Tot`, `M20_24_Managers`, `M20_24_Professionals`, `M20_24_TechnicTrades_W` … |
| `sa2_g01` | 2,472 | repo (0.7 MB) | `SA2_CODE_2021`, `Tot_P_M`, `Tot_P_F`, `Tot_P_P`, `Age_0_4_yr_M`, `Age_0_4_yr_F`, `Age_0_4_yr_P`, `Age_5_14_yr_M`, `Age_5_14_yr_F`, `Age_5_14_yr_P`, `Age_15_19_yr_M`, `Age_15_19_yr_F`, `Age_15_19_yr_P`, `Age_20_24_yr_M` … |
| `sa2_g02` | 2,472 | repo (0.0 MB) | `SA2_CODE_2021`, `Median_age_persons`, `Median_mortgage_repay_monthly`, `Median_tot_prsnl_inc_weekly`, `Median_rent_weekly`, `Median_tot_fam_inc_weekly`, `Average_num_psns_per_bedroom`, `Median_tot_hhd_inc_weekly`, `Average_household_size` |
| `sa2_g18` | 2,472 | repo (0.7 MB) | `SA2_CODE_2021`, `M_0_4_yrs_Need_for_assistance`, `M_0_4_No_need_for_assistance`, `M_0_4_Need_for_assistance_ns`, `M_0_4_yrs_Tot`, `M_5_14_Need_for_assistance`, `M_5_14_No_need_for_assistance`, `M_5_14_Need_for_assistance_ns`, `M_5_14_yrs_Tot`, `M_15_19_Need_for_assistance`, `M_15_19_No_need_for_assistnce`, `M_15_19_Need_for_assistnce_ns`, `M_15_19_yrs_Tot`, `M_20_24_Need_for_assistance` … |
| `sa2_g19` | 2,472 | repo (1.4 MB) | `SA2_CODE_2021`, `M_Arthritis_0_14`, `M_Arthritis_15_24`, `M_Arthritis_25_34`, `M_Arthritis_35_44`, `M_Arthritis_45_54`, `M_Arthritis_55_64`, `M_Arthritis_65_74`, `M_Arthritis_75_84`, `M_Arthritis_85_over`, `M_Arthritis_Tot`, `M_Asthma_0_14`, `M_Asthma_15_24`, `M_Asthma_25_34` … |
| `sa2_g20` | 2,472 | repo (0.9 MB) | `SA2_CODE_2021`, `M_0_cond_0_14`, `M_0_cond_15_24`, `M_0_cond_25_34`, `M_0_cond_35_44`, `M_0_cond_45_54`, `M_0_cond_55_64`, `M_0_cond_65_74`, `M_0_cond_75_84`, `M_0_cond_85_over`, `M_0_cond_Tot`, `M_1_cond_0_14`, `M_1_cond_15_24`, `M_1_cond_25_34` … |
| `sa2_g23` | 2,472 | repo (0.6 MB) | `SA2_CODE_2021`, `M_15_19_yr_Volunteer`, `M_15_19_yr_N_a_volunteer`, `M_15_19_yr_Voluntary_work_ns`, `M_15_19_yr_Tot`, `M_20_24_yr_Volunteer`, `M_20_24_yr_N_a_volunteer`, `M_20_24_yr_Voluntary_work_ns`, `M_20_24_yr_Tot`, `M_25_34_yr_Volunteer`, `M_25_34_yr_N_a_volunteer`, `M_25_34_yr_Voluntary_work_ns`, `M_25_34_yr_Tot`, `M_35_44_yr_Volunteer` … |
| `sa2_g25` | 2,472 | repo (0.6 MB) | `SA2_CODE_2021`, `M_15_19_Prvided_unpaid_assist`, `M_15_19_No_unpad_asst_prvided`, `M_15_19_Unpaid_assist_ns`, `M_15_19_Tot`, `M_20_24_Prvided_unpaid_assist`, `M_20_24_No_unpad_asst_prvided`, `M_20_24_Unpaid_assist_ns`, `M_20_24_Tot`, `M_25_34_Prvided_unpaid_assist`, `M_25_34_No_unpad_asst_prvided`, `M_25_34_Unpaid_assist_ns`, `M_25_34_Tot`, `M_35_44_Prvided_unpaid_assist` … |
| `sa2_g43` | 2,472 | repo (0.4 MB) | `SA2_CODE_2021`, `P_15_yrs_over_M`, `P_15_yrs_over_F`, `P_15_yrs_over_P`, `lfs_Emplyed_wrked_full_time_M`, `lfs_Emplyed_wrked_full_time_F`, `lfs_Emplyed_wrked_full_time_P`, `lfs_Emplyed_wrked_part_time_M`, `lfs_Emplyed_wrked_part_time_F`, `lfs_Emplyed_wrked_part_time_P`, `lfs_Employed_away_from_work_M`, `lfs_Employed_away_from_work_F`, `lfs_Employed_away_from_work_P`, `lfs_Unmplyed_lookng_for_wrk_M` … |
| `sa2_g44` | 2,472 | repo (0.2 MB) | `SA2_CODE_2021`, `Sme_Usl_ad_1_yr_ago_as_2021_M`, `Sme_Usl_ad_1_yr_ago_as_2021_F`, `Sme_Usl_ad_1_yr_ago_as_2021_P`, `Dif_Usl_ad_1_yr_ago_Sme_SA2_M`, `Dif_Usl_ad_1_yr_ago_Sme_SA2_F`, `Dif_Usl_ad_1_yr_ago_Sme_SA2_P`, `Dif_Us_ad_1_ago_Dif_SA2_NSW_M`, `Dif_Us_ad_1_ago_Dif_SA2_NSW_F`, `Dif_Us_ad_1_ago_Dif_SA2_NSW_P`, `Dif_Us_ad_1_ago_Dif_SA2_Vic_M`, `Dif_Us_ad_1_ago_Dif_SA2_Vic_F`, `Dif_Us_ad_1_ago_Dif_SA2_Vic_P`, `Dif_Us_ad_1_ago_Dif_SA2_Qld_M` … |
| `sa2_g45` | 2,472 | repo (0.3 MB) | `SA2_CODE_2021`, `Sme_Usl_ad_5_yr_ago_as_2021_M`, `Sme_Usl_ad_5_yr_ago_as_2021_F`, `Sme_Usl_ad_5_yr_ago_as_2021_P`, `Dif_Usl_ad_5_yr_ago_Sme_SA2_M`, `Dif_Usl_ad_5_yr_ago_Sme_SA2_F`, `Dif_Usl_ad_5_yr_ago_Sme_SA2_P`, `Dif_Us_ad_5_ago_Dif_SA2_NSW_M`, `Dif_Us_ad_5_ago_Dif_SA2_NSW_F`, `Dif_Us_ad_5_ago_Dif_SA2_NSW_P`, `Dif_Us_ad_5_ago_Dif_SA2_Vic_M`, `Dif_Us_ad_5_ago_Dif_SA2_Vic_F`, `Dif_Us_ad_5_ago_Dif_SA2_Vic_P`, `Dif_Us_ad_5_ago_Dif_SA2_Qld_M` … |
| `sa2_g46` | 2,472 | repo (1.3 MB) | `SA2_CODE_2021`, `M_Emp_FullT_15_19`, `M_Emp_FullT_20_24`, `M_Emp_FullT_25_34`, `M_Emp_FullT_35_44`, `M_Emp_FullT_45_54`, `M_Emp_FullT_55_64`, `M_Emp_FullT_65_74`, `M_Emp_FullT_75_84`, `M_Emp_FullT_85ov`, `M_Emp_FullT_Tot`, `M_Emp_PartT_15_19`, `M_Emp_PartT_20_24`, `M_Emp_PartT_25_34` … |
| `sa2_g50` | 2,472 | repo (1.2 MB) | `SA2_CODE_2021`, `M_NatPhyl_Scn_15_24`, `M_NatPhyl_Scn_25_34`, `M_NatPhyl_Scn_35_44`, `M_NatPhyl_Scn_45_54`, `M_NatPhyl_Scn_55_64`, `M_NatPhyl_Scn_65_74`, `M_NatPhyl_Scn_75_84`, `M_NatPhyl_Scn_85ov`, `M_NatPhyl_Scn_Tot`, `M_InfoTech_15_24`, `M_InfoTech_25_34`, `M_InfoTech_35_44`, `M_InfoTech_45_54` … |
| `sa2_g54` | 2,472 | repo (1.6 MB) | `SA2_CODE_2021`, `M_Ag_For_Fshg_15_19`, `M_Ag_For_Fshg_20_24`, `M_Ag_For_Fshg_25_34`, `M_Ag_For_Fshg_35_44`, `M_Ag_For_Fshg_45_54`, `M_Ag_For_Fshg_55_64`, `M_Ag_For_Fshg_65_74`, `M_Ag_For_Fshg_75_84`, `M_Ag_For_Fshg_85ov`, `M_Ag_For_Fshg_Tot`, `M_Mining_15_19`, `M_Mining_20_24`, `M_Mining_25_34` … |
| `sa2_g60` | 2,472 | repo (0.9 MB) | `SA2_CODE_2021`, `M15_19_Managers`, `M15_19_Professionals`, `M15_19_TechnicTrades_Wrs`, `M15_19_CommunPersnlSvc_W`, `M15_19_ClericalAdminis_W`, `M15_19_Sales_W`, `M15_19_Mach_oper_drivers`, `M15_19_Labourers`, `M15_19_Occu_ID_NS`, `M15_19_Tot`, `M20_24_Managers`, `M20_24_Professionals`, `M20_24_TechnicTrades_W` … |

## Social Health Atlas of Australia, by Population Health Area and socioeconomic quintile (`phidu`)

PHIDU, Torrens University Australia. Tier 2; questions 1, 2. Licence: CC BY-NC-SA 3.0 AU. Source: https://phidu.torrens.edu.au/social-health-atlases/data

PHIDU Social Health Atlas of Australia: health, wellbeing and social indicators by Population Health Area.

Modelled small-area estimates of mental health (psychological distress), self-assessed health and risk factors, with
Census health conditions, mortality, use of health services and social indicators (volunteering, education,
income support and more), beside regional IP use (context, not effect; section 2 of docs/data-plan.md). Replaces the
NATSEM wellbeing and trust estimates, which cannot be reached. CC BY-NC-SA 3.0 AU (non-commercial use only). The
site's files do not answer this environment, so the September 2026 workbooks were downloaded by hand from
https://phidu.torrens.edu.au/social-health-atlases/data and put in R2 under `raw/phidu/` (too big for GitHub's web
upload): Population Health Areas (demographic and social; health status; use and provision of health services) and
the socioeconomic quintiles. To update, replace them there and run `corpus run phidu`.

Population Health Areas are SA2s or groups of SA2s (2021 ASGS); each workbook's `PHAs` sheet lists them.

Processed: `indicators`, one row per workbook, sheet, area, indicator, period and measure (long). `area_code` is the
PHA code (empty for state and national totals, whose names are in `area_name`); for the quintiles workbook,
`area_name` is the area type (capital cities, rest of state) and `quintile` the socioeconomic quintile.

| Table | Rows | Where | Columns |
|---|---:|---|---|
| `indicators` | 4,951,275 | repo (34.0 MB) | `workbook`, `sheet`, `area_code`, `area_name`, `quintile`, `indicator`, `period`, `measure`, `value` |

## Small-scale renewable installations by postcode (`cer`)

Clean Energy Regulator. Tier 2; questions 1. Licence: CC BY 4.0. Source: https://cer.gov.au/markets/reports-and-data/small-scale-installation-postcode-data

Small-scale renewable installations by postcode (Clean Energy Regulator): solar panels, solar water heaters, heat
pumps, batteries, wind and hydro, monthly from 2011 (with 2001 to 2010 totals), as installations and capacity.

For the environmental pathway (section 2 of docs/data-plan.md): how fast green technologies spread, by place, beside
green patenting. Raw: each published file (repo; most are CSV, a few are Excel workbooks). Processed:
`installations`, long: `dataset` (the file's name, and the sheet's for a workbook),
`postcode`, `period` (YYYY-MM, or the historic total's label), `measure` (the column's measure, for example
"Installation Quantity" or "Rated Output In kW") and `value`.

| Table | Rows | Where | Columns |
|---|---:|---|---|
| `installations` | 7,051,130 | repo (7.7 MB) | `dataset`, `postcode`, `value`, `period`, `measure` |

## Register of protected geographical indications and other terms (`wine_gi`)

Wine Australia. Tier 2; questions 1. Licence: see the publisher's terms. Source: https://www.wineaustralia.com/labelling/register-of-protected-gis-and-other-terms

Australian wine geographical indications (Wine Australia's register of protected GIs and other terms).

For the cultural and regional identity pathway (section 2 of docs/data-plan.md); certification and collective trade
marks in IP RAPID are the other side of it. Raw: the register page's HTML and its PDFs (the EU GI register, traditional
expressions, additional terms and quality wine terms; repo). Processed: `australian_gis`, one row per register line
with the state or zone, region and subregion as published (footnote markers kept).

| Table | Rows | Where | Columns |
|---|---:|---|---|
| `australian_gis` | 89 | repo (0.0 MB) | `state_zone`, `region`, `subregion` |

## IP judgments (Federal Court, Full Federal Court, High Court, Copyright Tribunal) (`fedcourt`)

The courts, via the Open Australian Legal Corpus (Isaacus). Tier 2; questions 1. Licence: CC BY 4.0 (the collection); judgments reproducible unaltered with acknowledgement of the court and source. Source: https://huggingface.co/datasets/isaacus/open-australian-legal-corpus

IP judgments of the Federal Court, the Full Federal Court, the High Court and the Copyright Tribunal.

Enforcement costs and outcomes (Q1.3): which rights are litigated, by whom, in which technologies and industries, how
long cases take from hearing to judgment, and which firms act. From the Open Australian Legal Corpus (Isaacus,
https://huggingface.co/datasets/isaacus/open-australian-legal-corpus; the collection is CC BY 4.0; the courts permit
judgments to be reproduced unaltered with acknowledgement of the court and the source), which holds every decision of
those courts to its last collection (10 March 2025 for this release). The corpus is streamed (9.4 GB) and only IP
decisions are kept: those the Federal Court files under the Intellectual Property practice area, or whose catchwords
or legislation name an IP Act, or (older judgments, without a cover page) whose opening cites one; every Copyright
Tribunal decision; High Court decisions whose opening cites an IP Act. Raw: those decisions (R2, gzipped JSON lines).

Processed (both in R2, because case names include individuals' names):
- `judgments`: one row per decision, with the fields of the Federal Court's cover page (court, judges, dates of
  hearing and judgment, catchwords, legislation, cases cited, practice area and sub-area, registry, number of
  paragraphs, solicitors' firms; counsel's names are left out; dates as written, and `*_last` as the last day
  they name, so a hearing over several days gives its last day), the rights involved (`rights`, from catchwords,
  legislation and sub-area) and the IP Acts cited in the text with counts.
- `judgment_text`: the full text of each decision, by `version_id`, for text analysis (outcomes, damages, costs).

| Table | Rows | Where | Columns |
|---|---:|---|---|
| `judgment_text` | 2,666 | R2 (47.1 MB) | `version_id`, `text` |
| `judgments` | 2,666 | R2 (0.8 MB) | `version_id`, `citation`, `court`, `date`, `url`, `file_number`, `judges`, `date_of_judgment`, `date_of_hearing`, `date_of_last_submissions`, `catchwords`, `legislation`, `cases_cited`, `registry` … |

- Note: 2,666 IP decisions; corpus collected to 2025-03-10

## Google Patents Public Data, the worldwide patent families touching Australia (`google_patents`)

Google (BigQuery public dataset patents-public-data). Tier 3; questions 1, 3. Licence: CC BY 4.0. Source: https://console.cloud.google.com/marketplace/product/google_patents_public_datasets/google-patents-public-data

Google Patents Public Data (BigQuery): the worldwide patent families that touch Australia.

Q1 and Q3: patent families as value measures (how many offices an invention is filed in, forward citations), where
Australian applicants and inventors file abroad, and which foreign families come to Australia. The families are those
with a publication in Australia or an Australian applicant or inventor (by Google's harmonised country codes, which
some offices leave blank, so foreign filings by Australians are undercounted): 1.75 million families and 17 million
publications in the October 2026 release. Queried in BigQuery (`patents-public-data.patents.publications`, CC BY 4.0;
about 140 GB of query per run, within BigQuery's free terabyte a month, billed to `GCP_PROJECT_ID`); the families are
summarised in BigQuery and only the summaries and the Australian publications are downloaded. No raw files.

Processed (R2 unless small):
- `families`: one row per family: first priority, filing and grant dates, offices filed in (`offices`; `n_offices`
  counts national and regional offices other than WO and EP), PCT and EP filings, whether filed and granted in
  Australia and granted in the United States, Australian applicant or inventor, publications, the earliest
  publication's first IPC code, an English title, and forward citations (distinct citing families, in all and within
  five years of the family's first priority).
- `members`: one row per publication that is Australian or in a family with an Australian applicant or inventor:
  numbers, office, kind, dates, applicant and inventor countries and counts, first IPC and CPC codes and IPC
  subclasses, patent and non-patent citations made, the names of Australian applicants (organisations and
  individuals, as published), and `au_application` (the 10-digit Australian application number, to join to
  `iprapid`; every standard patent and innovation patent application from the 1960s on maps, but not provisional
  applications in the letter series of the 1990s, such as PO4687/97, nor designs, which Google also holds).
- `citations`: family-level citation pairs (citing family, cited family, citing family's first priority date) where
  the cited family has an Australian applicant or inventor.

| Table | Rows | Where | Columns |
|---|---:|---|---|
| `citations` | 1,854,268 | repo (18.5 MB) | `citing_family`, `cited_family`, `citing_priority_date` |
| `families` | 1,753,104 | R2 (53.7 MB) | `family_id`, `first_priority_date`, `first_filing_date`, `first_grant_date`, `publications`, `offices`, `n_offices`, `pct`, `ep`, `filed_au`, `granted_au`, `granted_us`, `au_applicant`, `au_inventor` … |
| `members` | 3,223,057 | R2 (117.7 MB) | `publication_number`, `application_number`, `pct_number`, `country_code`, `kind_code`, `application_kind`, `family_id`, `publication_date`, `filing_date`, `grant_date`, `priority_date`, `entity_status`, `assignee_countries`, `inventor_countries` … |

## Reliance on Science, US patents' citations to scientific papers (OpenAlex) (`reliance_on_science`)

Matt Marx and Aaron Fuegi. Tier 3; questions 1, 2. Licence: CC BY-NC 4.0. Source: https://zenodo.org/records/22967630

Reliance on Science (Marx and Fuegi): US patents' citations to scientific papers, matched to OpenAlex works.

Q1 and Q2: knowledge flows from research to invention, in place of the Lens (whose API is paid). Every citation from
a USPTO patent to a scholarly work, through 2025, with whether the applicant or examiner made it, a confidence score
(1 to 10) and whether it is on the front page, in the body text or both; and the patent-paper pairs (USPTO, through
2021). From https://zenodo.org/records/22967630, CC BY-NC 4.0 (non-commercial use; cite Marx and Fuegi 2020, Strategic
Management Journal 41(9), and 2022, Journal of Economics and Management Strategy). Raw: the citations file (R2,
1.4 GB) and the pairs file (repo).

Processed:
- `citations_au`: the citations made by US publications in patent families with an Australian applicant or inventor
  (from `google_patents/members`), with the family, so the science behind Australian inventions can be traced.
  `oaid` is the OpenAlex work id without its 'W'.
- `ppp`: patent-paper pairs, as published.

Which citing patents rely on Australian research needs the OpenAlex works with an Australian institution (about 2.4
million cited works); the full citations file is kept in R2 for that join.

| Table | Rows | Where | Columns |
|---|---:|---|---|
| `citations_au` | 620,364 | repo (2.3 MB) | `patent`, `family_id`, `oaid`, `reftype`, `confscore`, `wherefound` |
| `ppp` | 59,202 | repo (0.7 MB) | `magid`, `patent_id`, `confidence_level` |

## OpenAlex works with an Australian institution, and US patents' citations to them (`openalex_works`)

OurResearch (OpenAlex), with Reliance on Science. Tier 3; questions 2, 4. Licence: CC0 (OpenAlex); CC BY-NC 4.0 (the citations). Source: https://openalex.org/

OpenAlex: every cited work with an Australian institution, and the patents that cite Australian research.

Q2 and Q4: which Australian research, and which institutions' research, US patents build on (knowledge diffusion
from public research, and the commercialisation gap). Joins Reliance on Science (`reliance_on_science`, every USPTO
patent's citations to OpenAlex works) to the OpenAlex works with at least one Australian institution. Needs
`OPENALEX_API_KEY`. OpenAlex charges about US$0.0001 a call and gives each key US$1 (10,000 calls) a day free; the
full harvest takes about 13,000 calls, so a run stops before the day's allowance is spent and the next run (after
OpenAlex's daily reset) carries on where it stopped.

Two steps:
1. Every work with an Australian institution that has been cited at least once (about 2.4 million), by publication
   year: id, year, type and primary topic's field and subfield (light pages, 200 works a call). Raw: one gzipped CSV
   per year (repo), kept as each year completes.
2. For the works among those that USPTO patents cite, their Australian institutions (100 works a call; authors' names
   are not kept). Raw: the results (repo, gzipped JSON lines).

Processed:
- `au_works`: every cited work with an Australian institution (step 1).
- `cited_au_works`: the works patents cite, with the OpenAlex ids, names and types of their Australian institutions.
- `patent_citations`: every USPTO patent citation to Australian research (patent, work, reference type, confidence,
  where found), with whether the citing patent's family has an Australian applicant or inventor (`google_patents`).

*Not ingested yet: see the status in `docs/data-plan.md`.*

## IP policy changes (dates and terms) for natural experiments (`policy_events`)

compiled here from the Federal Register of Legislation and IP Australia. Tier 2; questions 4, 5. Licence: CC BY 4.0 (compiled here). Source: https://www.legislation.gov.au/

Changes to the IP system, for natural experiments on IP Australia's levers (Q4, Q5), and IP Australia's IP policy
register, an inventory of the levers already proposed and where each stands.

Raw: `events.yaml` (repo; compiled here, with `verify` marking details to confirm) and each policy register page's
HTML (repo, gzipped). Processed: `events` (date, rights, lever, event, source, verify) and `policy_register` (policy
id, title, status, priority, tags, issue summary, comments and URL, as IP Australia publishes them).

| Table | Rows | Where | Columns |
|---|---:|---|---|
| `events` | 13 | repo (0.0 MB) | `id`, `date`, `rights`, `lever`, `event`, `source`, `verify` |
| `policy_register` | 155 | repo (0.1 MB) | `policy_id`, `title`, `status`, `priority`, `tags`, `issue_summary`, `comments`, `url` |

## The ABN spine (every ABN in the corpus, with ABR and ASIC attributes and source flags) (`linkage`)

built here from abr, asic, iprapid, iplord, rdti, austender and ato_ctt. Tier 1; questions 2, 3, 4. Licence: as its sources (CC BY 3.0 AU and CC BY 4.0). Source: src/corpus/sources/linkage.py

The ABN spine: one row per ABN that appears anywhere in the corpus, with what the business registers say about it.

Built from the other sources (run it after them). Processed: `abn_spine` (repo), one row per ABN seen in IP RAPID's
parties, IPLORD, the R&D Tax Incentive reports, AusTender suppliers or the corporate tax transparency reports, with:

- from the ABR: entity type, ABN status and the date it took effect, GST status and date, state, postcode, ACN, and
  whether the business is a deductible gift recipient;
- from ASIC (through the ACN): company registration and deregistration dates, type, class and status;
- `first_seen`, the earliest of the ABN status date (for an active ABN), GST registration and ASIC registration: a
  lower bound on the business's start, since the public ABR gives only the date of the current status;
- flags for each source it appears in (`in_iprapid_patent` and so on, `in_rdti`, `in_austender`, `in_ato_ctt`), and its
  first and last filing financial years by right type from `iprapid/applicant_year`.

`abn_spine` is how the analysis joins IP use to R&D, procurement, size and survival. ABNs in IP RAPID cover Australian
applicants that IP Australia matched to the ABR; foreign applicants and many individuals have none.

| Table | Rows | Where | Columns |
|---|---:|---|---|
| `abn_spine` | 391,983 | repo (12.7 MB) | `abn`, `entity_type`, `entity_type_text`, `abn_status`, `abn_status_from`, `gst_status`, `gst_status_from`, `state`, `postcode`, `acn`, `dgr`, `name`, `asic_registered`, `asic_deregistered` … |
