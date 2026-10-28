# Brief: filling the data gaps (after Stage 2)

**For a fresh Claude Code session.** The owner asked on 2026-10-28 for the data gaps to be filled in a new session
(A15, `docs/owner-questions.md`). Read `CLAUDE.md`, then `docs/handover-eda.md` (its latest status block),
`docs/stage-2-summary.md` and ADR 0030 before starting. This brief lists every open gap, why it matters, where the
data is, and what "done" means. All sources are free unless marked; anything marked **owner** needs the owner first.

## Ground rules (from `CLAUDE.md` and ADR 0007)

- **Each new source is a corpus source** in `src/corpus/sources/` (follow an existing one of the same kind: `ipa_fees`
  for scraped tables, `abs_prices` for the ABS API, `_abs_cube.py` for ABS data cubes, `wipo_ipstats` for WIPO), with
  its entry in `docs/catalogue.md` and a test. Large tables go to R2, as the others do.
- **Every dataset goes through all three stages.** So each gap filled is attached to a lens in `analysis/eda/build.py`
  (with its columns in `variables.yaml` and `screens.yaml`, which tests check), profiled in `01_univariate.ipynb`
  (new observations from **U108**), and its pairs added to `02_bivariate.ipynb` (new observations from **B47**), under
  the evidence rules: every number on the page, each observation labelled.
- **Never add two sources for one measure**: one is the main measure, the other a labelled comparison (for example
  the crosswalk with services beside the one without).
- **The website is not updated** (`evidence/`, `analysis/atlas/`) until the owner answers OQ19.
- Record the non-obvious choices in ADRs (next free number: **0031**), keep the handover current, commit and push to
  the session's branch, one gap per commit.
- Running the notebooks: `uv run jupyter nbconvert --to notebook --execute --inplace analysis/notebooks/02_bivariate.ipynb`
  (about nine minutes). Edit its cells directly; Stage 2's helpers are in `analysis/eda/bivariate.py`. Keep its runs
  reproducible: order any SQL whose rows feed a bootstrap (ADR 0030, item 10).

## The gaps, in order of value

### A. Found to matter by Stage 2 (do these first)

| # | Gap | Why (observations) | Source | Attach to | Done when |
|---|---|---|---|---|---|
| A1 | **The history of official fees** (R3, OQ2) | IP Australia's most direct lever, and the one missing from every policy comparison (B37, U28); renewal behaviour (B8, B10) cannot be related to fees without it | The Federal Register of Legislation: every compilation of the Patents Regulations 1991 (Schedule 7), Trade Marks Regulations 1995 (Schedule 9), Designs Regulations 2004 (Schedule 4) and Plant Breeder's Rights Regulations, with their start dates; the current fees are already in `ipa_fees` | `timeline` (each fee's level by month, nominal and in real terms with the CPI) and `policy_events` (each fee change as an event) | Fee series for filing, examination and renewal of each right from at least 1990; fee changes tested as in B37, against placebo dates; filing and renewal around them in `02_bivariate` |
| A2 | **ALP's crosswalk that includes services** (B41, U75) | Patents reach only 8 of 19 divisions because the crosswalk used excludes services, so the industries lens can say little about R&D and patenting | Lybbert and Zolas's ALP concordances (the IPC-to-ISIC version with services), the same site as `concordances`' current files | `industries` (a labelled comparison beside the current counts) | Patents by division with services; B40 and B41 redone with both crosswalks |
| A3 | **Firms' size and industry** (B21 to B24) | The third factors most firm leads need; BLADE stays ruled out | Investigate free sources first: the R&D Tax Incentive and ATO transparency releases (industry fields, if any), ASIC, the ABR's public extract (no ANZSIC), AusTender's suppliers (UNSPSC, not ANZSIC). If none is free and firm-level, write up the options and costs for the owner (**owner**: money or an account, for example ABS DataLab) | `firms` | Either the columns are in the lens with their coverage profiled, or an owner question with the options |
| A4 | **Google Patents' coverage of Australian-only families, and Australian inventions filed only abroad** (B11, F07, item 14 of the plan) | Australian organisations' patents filed only in Australia fell from 73.02% to 40.71% between decades (B11): practice, or older families held less fully? And how many Australian inventions does IP RAPID never see? | WIPO's patent families by origin (IP statistics indicator 6a: the `wipo_ipstats` loader takes another indicator in minutes, ADR 0022); IP RAPID's own priority and PCT links for a check of family size | `national` (families by origin) and a check in `rights` | The coverage check written up (an observation), and families by origin compared with Australia's patent counts |

### B. In the plan, not yet done (free)

| # | Gap | Source | Attach to |
|---|---|---|---|
| B1 | RBA cash rate and exchange rates (monthly) | RBA statistical tables (F1, F11) | `timeline` |
| B2 | ABS national accounts (GDP and state final demand, quarterly) | ABS API, as `abs_prices` | `timeline`, `national` |
| B3 | ATO taxation statistics by postcode (annual, from 2012-13), including counts with business income | data.gov.au (ATO taxation statistics, individuals table 6 or 8 by postcode) | `regions` (over time, and a denominator for individual applicants) |
| B4 | ABS Business Characteristics Survey 2023-24 and 2024-25 (the API stops at 2023) | ABS data cubes (`_abs_cube.py`) | `industries` (`industry_indicators`) |
| B5 | Court judgments after 10 March 2025 | Check the Open Australian Legal Corpus for a newer collection, then the Federal Court's own listings | `rights` (via `fedcourt`) |
| B6 | Census 2011, 2016 and 2021 time-series tables by area | ABS Census DataPacks (time series profile) | `regions` (`region_indicators`) |
| B7 | GII supplementary observations for the six indicators blank for Australia (F17) | The GII's sources for those indicators | `national_indicators`, labelled "supplementary" |
| B8 | OpenAlex: does the "cited at least once" filter drop works that patents cite (F37)? Re-harvest if it matters | OpenAlex API | `institutions` |
| B9 | Research commercialisation: NSRC unit records, 2000 to 2015 | DISR. If they need a request, it is **owner** | `institutions` |
| B10 | The missing AusTender amendments (OQ3: amendments after August 2019 to contracts that had ended by then; under 1% of value) | `austender._harvest_by_id`, which exists | `firms`, `regions` |
| B11 | PBS monthly report with Section 100 (B9 of Stage 1, OQ2) | The raw file is already in R2 | The PBS source; it matters for a medicine case study (OQ8), so it can come last |

### Not for this session

- **OQ18** (whether IP RAPID records priority claims late, B38) and the other questions to IP Australia: the owner
  sends them.
- **TableBuilder** (OQ4): on hold, needs the owner's account.
- **OQ11** (a sector review of the institutions link) and **OQ19** (the atlas, Stage 3): the owner's call.

## Suggested opening prompt for the new session

> Read `CLAUDE.md`, `docs/handover-eda.md` and `docs/data-gaps-brief.md`. Fill the data gaps in the brief, in its order
> (A1 to A4, then B1 to B11), each as a corpus source attached to a lens and carried through Stages 1 and 2 as the
> brief says. Do not update the website. Ask me only about the items the brief marks "owner".
