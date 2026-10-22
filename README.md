# The research corpus for IP Australia's research programme

The data behind IP Australia's research programme (`docs/research-goal.md`): where, how and for whom IP Australia's
interventions could generate the greatest additional public value. This repository holds the corpus, the code that
builds it, and the plan that chose it. The analysis is done elsewhere, by sessions that read the corpus.

- **`docs/research-goal.md`**: the five core questions.
- **`docs/data-plan.md`**: which data serve which question, what was dropped and why, how non-financial public value is
  handled, and what is still missing.
- **`docs/catalogue.md`**: every source and table, with rows, columns and where each lives (generated).
- **`docs/evidence-register.md`**: the literature and evaluations the questions lean on (generated, checked against
  Crossref).

## Using the corpus

```sh
uv sync                       # Python 3.11+; installs pandas, pyarrow, duckdb and the rest
```

```python
import corpus

rights = corpus.load("iprapid", "patent_rights")           # a pandas DataFrame
spine = corpus.load("linkage", "abn_spine", columns=["abn", "entity_type", "in_rdti", "patent_first_fy"])

import duckdb                                              # for the big tables, query the Parquet file directly
events = corpus.path("iprapid", "events")                  # downloads from R2 once, into ~/.cache/ipholmes
duckdb.sql(f"SELECT event_type, count(*) FROM '{events}' WHERE ip_right_type = 'patent' GROUP BY 1 ORDER BY 2 DESC").df()
```

Small and analysis-ready tables are in the repo (`data/processed/<source>/<table>.parquet`). Large ones are in the
Cloudflare R2 bucket `ipholmes`; reading them needs `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID` and `R2_SECRET_ACCESS_KEY`
in the environment. `docs/catalogue.md` says which is where.

**Join keys.** ABNs (11 digits, as text) join IP Australia's data to the business registers, the R&D Tax Incentive,
AusTender and the corporate tax reports; `linkage/abn_spine` does that join once. Postcodes join to ABS geography
through `abs_regions/poa`; IPC classes join to technology fields and industries through `concordances`.

**Evidence levels.** As the research goal requires, findings should say whether they are descriptive, observational,
causal or projected. Almost everything here supports descriptive and observational work; the natural experiments in
`policy_events` support quasi-experimental designs; credible additionality needs data this corpus does not hold
(see the data plan's Tier 3).

## Building and checking it

```sh
uv sync --group dev
uv run corpus list                  # the sources and what the manifest holds for each
uv run corpus run rdti abs_bcs      # fetch and process sources (writes data/, uploads to R2, updates the manifest)
uv run corpus run all               # everything (hours: IP RAPID, the ABR and AusTender are large)
uv run corpus verify --r2           # repo files against the manifest, and R2 holding the rest
uv run corpus catalogue             # regenerate docs/catalogue.md
uv run pytest -q                    # the rules, and the committed data against the manifest
```

Each source is one module in `src/corpus/sources/`, named by its id in `config/sources.yaml` (the source register:
publisher, URL, licence, tier, questions). A run records every raw and processed file's SHA-256, size and location
in `data/manifest.json`, and fails loudly with one line naming the source when a publisher changes its layout. Large
raw files pass through a cache outside the repo (`$IPHOLMES_CACHE`, default `~/.cache/ipholmes`).

## The repository

| Path | What it is |
|---|---|
| `config/sources.yaml` | The source register |
| `src/corpus/` | The corpus: `core.py` (downloads, R2, Parquet, manifest), `cli.py`, one module per source |
| `data/raw/<source>/` | Raw files small enough for the repo, as published (large ones are in R2 under `raw/`) |
| `data/processed/<source>/` | Parquet tables small enough for the repo (large ones are in R2 under `processed/`) |
| `data/manifest.json` | Every file's SHA-256, size, rows, columns and location |
| `docs/` | The research goal, the data plan, the catalogue, the evidence register |
| `tests/` | The rules, and the committed data against the manifest |
| `index.html`, `assets/` | The GII breakdown page (Australia in the Global Innovation Index 2026), kept from the earlier site; it reads a frozen summary in `assets/data/`, and will be rebuilt on the corpus |

## Credentials

Keys and tokens go in the cloud environment's settings (the environment menu in the session's title bar, then
Edit, then Network secrets or Environment variables), never in the repo. A new session picks them up.

| Variable | For | Value |
|---|---|---|
| `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY` | The `ipholmes` R2 bucket | From Cloudflare |
| `OPENALEX_API_KEY` | `openalex` | A free OpenAlex key |
| `GCP_SERVICE_ACCOUNT_JSON` | Google Patents Public Data in BigQuery | The whole contents of the service account's JSON key file (or the same, base64-encoded); `corpus.core.gcp_credentials()` writes it to a private file outside the repo at run time |
| `GCP_PROJECT_ID` | BigQuery billing project | The project the service account belongs to (queries are billed to it; the public patent tables are free to read, the queries are not beyond the free monthly allowance) |
| `LENS_API_TOKEN` | The Lens (scholarly works and patents) | A Lens API token |

## Privacy

The corpus holds published data only. Individuals' names (sole traders, individual applicants) are left out of the
tables in the repo: the ABN Bulk Extract is read without them, and the IP RAPID summaries blank them. IP RAPID's party
tables in R2 keep names as IP Australia publishes them, for analyses (such as gender estimation from first names)
that need them; summaries built from them should not republish names.

## Sources and licences

Each source's licence is in `config/sources.yaml` and `docs/catalogue.md`. Most are CC BY (IP Australia, the ABS, the
ATO, ASIC, the ABR, the OECD, the World Bank, WIPO); the NATSEM small-area estimates (not yet ingested) are CC BY-NC.
Where a licence was unclear, the register says so: check before republishing outside this repository.
