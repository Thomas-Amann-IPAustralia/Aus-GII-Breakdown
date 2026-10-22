# Data catalogue

Every source in the corpus and every table it holds. Written by `uv run corpus catalogue` from `config/sources.yaml`
and `data/manifest.json`; edit those (or a source's module docstring), not this file. What each source is for, and
what is still missing, is in `docs/data-plan.md`; how to use the corpus is in `README.md`.

**Where a table lives.** *repo* tables are in `data/processed/<source>/<table>.parquet`. *R2* tables are in the
`ipholmes` bucket at `processed/<source>/<table>.parquet`; `corpus.load` and `corpus.path` fetch them once into
`~/.cache/ipholmes` (R2 credentials in `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID` and `R2_SECRET_ACCESS_KEY`).

**Join keys.** `abn` (11 digits, as text) joins IPGOD, IPLORD, the ABR, ASIC (through `acn`), the R&D Tax Incentive,
AusTender and the corporate tax reports; `linkage/abn_spine` already does it. Postcodes join to ABS geography through
`abs_regions/poa` and `poa_sa2` (a postcode is a postal area code, as text). IPC subclasses join to industries and
technology fields through `concordances`. ISO3 codes join the cross-country sources (`gii`, `oecd`, `wdi`).

## Intellectual Property Government Open Data (IPGOD) 2022 (`ipgod`)

IP Australia. Tier 1; questions 1, 2, 3, 4. Licence: CC BY 2.5 AU. Source: https://data.gov.au/data/dataset/ipgod2022

IPGOD 2022: every Australian patent, trade mark, design and plant breeder's right application to early 2022.

Raw: the release's zip (R2) and its data dictionary (repo). Processed, one Parquet table per IPGOD table (R2), typed:
dates as dates, ABNs as 11-digit strings, flags as booleans. Then one summary per right type, a row per application
with its applicants and attorneys reduced to a few columns (repo where it fits):

- `<right>_application`, `_classification`, `_description`, `_events`, `_links`, `_party`: the IPGOD tables as published
  (right is patent, trade_mark, design or pbr).
- `<right>_rights`: one row per application: status and key dates; the number of current applicants; the first current
  applicant's party id, name, type, country, state, postcode and ABN; whether any applicant is in Australia; whether an
  attorney or agent acts; the main classification (patents: the first current IPC mark's four-character class;
  trade marks: the Nice classes, as a count and a list; designs: the Locarno class; PBR: the genus). Individuals'
  names are left out of these (repo) tables; the `_party` tables (R2) have them as IP Australia publishes them.
- `applicant_year`: applicant (ABN where IPGOD has one, else party id) by right by financial year: applications filed
  and rights that became enforceable, counted and weighted as IPLORD does. Unlike IPLORD 2020, it covers patents, and
  runs to early 2022.

IPGOD's public party data has no inventors, only applicants, owners, agents and other parties.

| Table | Rows | Where | Columns |
|---|---:|---|---|
| `applicant_year` | 2,678,084 | repo (12.6 MB) | `applicant_id`, `applicant_id_type`, `party_type`, `country_code`, `state_code`, `post_code`, `ip_right_type`, `financial_year`, `filed`, `filed_weighted`, `became_enforceable`, `became_enforceable_weighted` |
| `design_application` | 224,211 | R2 (2.9 MB) | `ip_right_type`, `application_number`, `ip_right_sub_type`, `status`, `earliest_filed_date`, `priority_date`, `gained_registration_status_date`, `gained_enforceable_status_date`, `enforceable_from_date`, `deemed_retired_date` |
| `design_classification` | 233,855 | R2 (1.6 MB) | `ip_right_type`, `application_number`, `classification_system`, `classification`, `classification_importance`, `classification_inventiveness`, `classification_source`, `classifying_country_code`, `classification_date`, `classification_removal_date`, `classification_system_version`, `is_current` |
| `design_description` | 210,420 | R2 (2.5 MB) | `ip_right_type`, `application_number`, `description_type`, `description_value` |
| `design_events` | 1,769,404 | R2 (8.5 MB) | `application_number`, `ip_right_type`, `event_type`, `event_category`, `event_effective_date`, `event_declared_date`, `is_standing` |
| `design_links` | 97,748 | R2 (1.2 MB) | `ip_right_type`, `application_number`, `link_type`, `linked_application_number`, `link_date`, `linked_application_country` |
| `design_party` | 509,951 | R2 (7.9 MB) | `ip_right_type`, `application_number`, `party_id`, `party_role_category`, `party_role`, `party_type`, `party_name`, `state_code`, `post_code`, `country_code`, `effective_from_date`, `effective_to_date`, `is_current`, `abn` … |
| `design_rights` | 224,211 | repo (3.5 MB) | `application_number`, `ip_right_sub_type`, `status`, `earliest_filed_date`, `priority_date`, `gained_registration_status_date`, `gained_enforceable_status_date`, `enforceable_from_date`, `deemed_retired_date`, `applicant_count`, `applicant_party_id`, `applicant_name`, `applicant_type`, `applicant_country` … |
| `patent_application` | 1,576,221 | R2 (20.3 MB) | `ip_right_type`, `application_number`, `ip_right_sub_type`, `status`, `earliest_filed_date`, `priority_date`, `gained_registration_status_date`, `gained_enforceable_status_date`, `enforceable_from_date`, `deemed_retired_date` |
| `patent_classification` | 8,281,276 | R2 (51.7 MB) | `ip_right_type`, `application_number`, `classification_system`, `classification`, `classification_importance`, `classification_inventiveness`, `classification_source`, `classifying_country_code`, `classification_date`, `classification_removal_date`, `classification_system_version`, `is_current` |
| `patent_description` | 1,576,221 | R2 (36.1 MB) | `ip_right_type`, `application_number`, `description_type`, `description_value` |
| `patent_events` | 11,703,884 | R2 (52.7 MB) | `application_number`, `ip_right_type`, `event_type`, `event_category`, `event_effective_date`, `event_declared_date`, `is_standing` |
| `patent_links` | 1,887,935 | R2 (25.1 MB) | `ip_right_type`, `application_number`, `link_type`, `linked_application_number`, `link_date`, `linked_application_country` |
| `patent_party` | 3,458,445 | R2 (56.3 MB) | `ip_right_type`, `application_number`, `party_id`, `party_role_category`, `party_role`, `party_type`, `party_name`, `state_code`, `post_code`, `country_code`, `effective_from_date`, `effective_to_date`, `is_current`, `abn` … |
| `patent_rights` | 1,576,221 | repo (30.3 MB) | `application_number`, `ip_right_sub_type`, `status`, `earliest_filed_date`, `priority_date`, `gained_registration_status_date`, `gained_enforceable_status_date`, `enforceable_from_date`, `deemed_retired_date`, `applicant_count`, `applicant_party_id`, `applicant_name`, `applicant_type`, `applicant_country` … |
| `pbr_application` | 10,368 | R2 (0.1 MB) | `ip_right_type`, `application_number`, `ip_right_sub_type`, `status`, `earliest_filed_date`, `priority_date`, `gained_registration_status_date`, `gained_enforceable_status_date`, `enforceable_from_date`, `deemed_retired_date` |
| `pbr_classification` | 30,825 | R2 (0.1 MB) | `ip_right_type`, `application_number`, `classification_system`, `classification`, `classification_importance`, `classification_inventiveness`, `classification_source`, `classifying_country_code`, `classification_date`, `classification_removal_date`, `classification_system_version`, `is_current` |
| `pbr_description` | 10,368 | R2 (0.1 MB) | `ip_right_type`, `application_number`, `description_type`, `description_value` |
| `pbr_events` | 55,099 | R2 (0.2 MB) | `application_number`, `ip_right_type`, `event_type`, `event_category`, `event_effective_date`, `event_declared_date`, `is_standing` |
| `pbr_links` | 0 | R2 (0.0 MB) | `ip_right_type`, `application_number`, `link_type`, `linked_application_number`, `link_date`, `linked_application_country` |
| `pbr_party` | 11,890 | R2 (0.1 MB) | `ip_right_type`, `application_number`, `party_id`, `party_role_category`, `party_role`, `party_type`, `party_name`, `state_code`, `post_code`, `country_code`, `effective_from_date`, `effective_to_date`, `is_current`, `abn` … |
| `pbr_rights` | 10,368 | repo (0.2 MB) | `application_number`, `ip_right_sub_type`, `status`, `earliest_filed_date`, `priority_date`, `gained_registration_status_date`, `gained_enforceable_status_date`, `enforceable_from_date`, `deemed_retired_date`, `applicant_count`, `applicant_party_id`, `applicant_name`, `applicant_type`, `applicant_country` … |
| `trade_mark_application` | 1,910,924 | R2 (30.6 MB) | `ip_right_type`, `application_number`, `ip_right_sub_type`, `status`, `earliest_filed_date`, `priority_date`, `gained_registration_status_date`, `gained_enforceable_status_date`, `enforceable_from_date`, `deemed_retired_date` |
| `trade_mark_classification` | 3,028,595 | R2 (17.8 MB) | `ip_right_type`, `application_number`, `classification_system`, `classification`, `classification_importance`, `classification_inventiveness`, `classification_source`, `classifying_country_code`, `classification_date`, `classification_removal_date`, `classification_system_version`, `is_current` |
| `trade_mark_description` | 4,432,633 | R2 (42.5 MB) | `ip_right_type`, `application_number`, `description_type`, `description_value` |
| `trade_mark_events` | 26,968,088 | R2 (130.4 MB) | `application_number`, `ip_right_type`, `event_type`, `event_category`, `event_effective_date`, `event_declared_date`, `is_standing` |
| `trade_mark_links` | 1,263,346 | R2 (13.2 MB) | `ip_right_type`, `application_number`, `link_type`, `linked_application_number`, `link_date`, `linked_application_country` |
| `trade_mark_party` | 5,764,299 | R2 (103.0 MB) | `ip_right_type`, `application_number`, `party_id`, `party_role_category`, `party_role`, `party_type`, `party_name`, `state_code`, `post_code`, `country_code`, `effective_from_date`, `effective_to_date`, `is_current`, `abn` … |
| `trade_mark_rights` | 1,910,924 | repo (41.6 MB) | `application_number`, `ip_right_sub_type`, `status`, `earliest_filed_date`, `priority_date`, `gained_registration_status_date`, `gained_enforceable_status_date`, `enforceable_from_date`, `deemed_retired_date`, `applicant_count`, `applicant_party_id`, `applicant_name`, `applicant_type`, `applicant_country` … |

## Intellectual Property Longitudinal Research Data (IPLORD) 2020 (`iplord`)

IP Australia. Tier 1; questions 2, 3. Licence: CC BY 4.0. Source: https://data.gov.au/data/dataset/intellectual-property-longitudinal-research-data-2020

IPLORD 2020: IP Australia's applicant by financial year panel, 1904 to 2020, with the ABN where known.

The public 2020 release covers designs (`d_`), plant breeder's rights (`pbr_`) and trade marks (`tm_`, with
`tm_services_` for service classes); it has no patent columns, although its dictionary describes them. For patents,
and for years after 2020, use `ipgod/applicant_year`, built the same way from IPGOD 2022.

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
- `patent_fields`: each IPGOD patent application's technology fields, from its current IPC marks, with `weight`
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
| `patent_fields` | 1,699,357 | repo (5.2 MB) | `application_number`, `field_no`, `weight`, `field`, `sector` |

- Note: concordances: nice_anzsic: 0.0% of ALP weight is on ISIC classes the ABS table lacks

## World Gender-Name Dictionary 2.0 (`wgnd`)

WIPO (Harvard Dataverse). Tier 1; questions 2. Licence: CC0 1.0. Source: https://doi.org/10.7910/DVN/MSEGSJ

World Gender-Name Dictionary 2.0 (WIPO, 2021): first names with the gender they are given to, by country.

For estimating the gender of individual applicants in IPGOD from first names, the method WIPO and IP Australia have
used. IPGOD's public party data has no inventors, so this covers individual applicants (and owners) only.
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

*Not ingested yet: see the status in `docs/data-plan.md`.*

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

NHMRC grant outcomes.

Health and medical research funding by institution, scheme and field (Q2 research institutions; Q3 public funding).
This environment cannot fetch it: put the files in data/raw/nhmrc_grants/ and run `corpus run nhmrc_grants`. To get
them: From https://www.nhmrc.gov.au/funding/data-research/outcomes, the summary of results and grant outcomes
workbooks (xlsx). The NHMRC site refuses this environment.

Processed: one table per file (and per sheet of a workbook), all columns as text; see `_manual.read_dropped`.

*Not ingested yet: see the status in `docs/data-plan.md`.*

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

*Not ingested yet: see the status in `docs/data-plan.md`.*

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

WIPO IP statistics, filings by origin and office.

Q3: which countries' applicants file where, including trade marks, which the World Bank no longer publishes. This
environment cannot fetch it: put the files in data/raw/wipo_ipstats/ and run `corpus run wipo_ipstats`. To get them:
From the WIPO IP Statistics Data Center (https://www3.wipo.int/ipstats/), export as CSV, for all origins and all
available years: trade mark applications (class count) by origin; patent applications by origin; industrial design
applications (design count) by origin; PCT applications by origin; Madrid applications by origin. Its API is
undocumented, so this source reads the exports.

Processed: one table per file (and per sheet of a workbook), all columns as text; see `_manual.read_dropped`.

*Not ingested yet: see the status in `docs/data-plan.md`.*

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
medicines, which can be followed through patent expiry and IPGOD's pharmaceutical extensions of term.

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

*Not ingested yet: see the status in `docs/data-plan.md`.*

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

Cultural and creative activity in Australia.

The size of the creative industries, where copyright and design protection operate (section 2 of docs/data-plan.md).
This environment cannot fetch it: put the files in data/raw/bcarr_creative/ and run `corpus run bcarr_creative`. To
get them: From the Bureau of Communications, Arts and Regional Research (infrastructure.gov.au), the cultural and
creative activity data tables (xlsx). The site refuses this environment.

Processed: one table per file (and per sheet of a workbook), all columns as text; see `_manual.read_dropped`.

*Not ingested yet: see the status in `docs/data-plan.md`.*

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

## Small-area synthetic estimates of life satisfaction and generalised trust (SA2) (`natsem`)

NATSEM, University of Canberra. Tier 2; questions 1, 2. Licence: CC BY-NC 4.0. Source: https://data.gov.au/ (AURIN)

NATSEM small-area synthetic estimates of life satisfaction and generalised trust (SA2).

Wellbeing and social cohesion by place, beside regional IP use (context, not effect). CC BY-NC 4.0. This environment
cannot fetch it: put the files in data/raw/natsem/ and run `corpus run natsem`. To get them: From data.gov.au, the
AURIN download manager links on 'NATSEM - Life Satisfaction Indicators - Synthetic Estimates SA2 2016', 'NATSEM -
Trust Indicators - Synthetic Estimates SA2 2016' and 'SA2 OECD Indicators: Estimates of Generalised Trust (Synthetic
Data) 2011', as CSV. AURIN's servers refuse this environment.

Processed: one table per file (and per sheet of a workbook), all columns as text; see `_manual.read_dropped`.

*Not ingested yet: see the status in `docs/data-plan.md`.*

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
marks in IPGOD are the other side of it. Raw: the register page's HTML and its PDFs (the EU GI register, traditional
expressions, additional terms and quality wine terms; repo). Processed: `australian_gis`, one row per register line
with the state or zone, region and subregion as published (footnote markers kept).

| Table | Rows | Where | Columns |
|---|---:|---|---|
| `australian_gis` | 89 | repo (0.0 MB) | `state_zone`, `region`, `subregion` |

## Border enforcement of IP (notices of objection and seizures) (`abf`)

Australian Border Force. Tier 2; questions 1. Licence: see the publisher's terms. Source: https://www.abf.gov.au/

Border enforcement of IP.

Enforcement against counterfeits, and consumer safety (section 2 of docs/data-plan.md). This environment cannot fetch
it: put the files in data/raw/abf/ and run `corpus run abf`. To get them: The Australian Border Force's figures on
notices of objection and seizures of counterfeit and pirated goods, from the Department of Home Affairs annual reports
(performance tables), entered as a CSV with columns year, measure, value, source. Not published as data.

Processed: one table per file (and per sheet of a workbook), all columns as text; see `_manual.read_dropped`.

*Not ingested yet: see the status in `docs/data-plan.md`.*

## Federal Court IP judgments (`fedcourt`)

Federal Court of Australia. Tier 2; questions 1. Licence: see the publisher's terms. Source: https://www.judgments.fedcourt.gov.au/

Federal Court IP judgments.

Enforcement costs and outcomes (Q1.3). This environment cannot fetch it: put the files in data/raw/fedcourt/ and run
`corpus run fedcourt`. To get them: A CSV of IP judgments (patents, trade marks, designs, copyright) with columns
citation, date, parties, right, outcome, url, from the Federal Court's judgments search or a licensed database. The
Federal Court site and AustLII refuse this environment, and AustLII's terms do not allow bulk downloading.

Processed: one table per file (and per sheet of a workbook), all columns as text; see `_manual.read_dropped`.

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

built here from abr, asic, ipgod, iplord, rdti, austender and ato_ctt. Tier 1; questions 2, 3, 4. Licence: as its sources (CC BY 3.0 AU and CC BY 4.0). Source: src/corpus/sources/linkage.py

The ABN spine: one row per ABN that appears anywhere in the corpus, with what the business registers say about it.

Built from the other sources (run it after them). Processed: `abn_spine` (repo), one row per ABN seen in IPGOD's
parties, IPLORD, the R&D Tax Incentive reports, AusTender suppliers or the corporate tax transparency reports, with:

- from the ABR: entity type, ABN status and the date it took effect, GST status and date, state, postcode, ACN, and
  whether the business is a deductible gift recipient;
- from ASIC (through the ACN): company registration and deregistration dates, type, class and status;
- `first_seen`, the earliest of the ABN status date (for an active ABN), GST registration and ASIC registration: a
  lower bound on the business's start, since the public ABR gives only the date of the current status;
- flags for each source it appears in (`in_ipgod_patent` and so on, `in_rdti`, `in_austender`, `in_ato_ctt`), and its
  first and last filing financial years by right type from `ipgod/applicant_year`.

`abn_spine` is how the analysis joins IP use to R&D, procurement, size and survival. ABNs in IPGOD cover Australian
applicants that IP Australia matched to the ABR; foreign applicants and many individuals have none.

*Not ingested yet: see the status in `docs/data-plan.md`.*
