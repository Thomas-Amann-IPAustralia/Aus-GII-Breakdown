# Australia in the GII, and a correlation explorer

Early visual analysis for IP Australia's research programme (`docs/research-goal.md`): how Australia fares in the
Global Innovation Index 2026, and an interactive tool for looking for patterns and correlations between the datasets
behind the research goal. Two static pages, published with GitHub Pages:

- **The GII breakdown** (`index.html`): Australia's score, rank, pillars, strengths and weaknesses, and all 79
  indicators, with WIPO's definitions and a way into the explorer from each.
- **The correlation explorer** (`explorer/`): compare any two measures over time for Australia (2,442 series) or
  across economies (221 measures, 197 economies); a correlation matrix with multicollinearity checks and a
  descriptive regression; a scan for the measures that correlate with a target, corrected for multiple testing.
  Every statistical term (Spearman, p-value, multicollinearity, effective n and others) has a hover call-out, and
  every comparison comes with the checks that keep a correlation from being over-read.

Everything shown is exploratory association, the first of the research goal's levels of evidence. Methods:
`docs/methods.md`.

## Opening it

Once GitHub Pages is switched on (below), the pages are at
**https://thomas-amann-ipaustralia.github.io/Aus-GII-Breakdown/**, and the explorer at `…/explorer/`.

To run it on your own computer: `python3 -m http.server 8000` in the repository, then open http://localhost:8000/.
(Opening `index.html` straight from disk doesn't work: browsers block a page from reading its own data files that way.)

### Switching on GitHub Pages (once)

1. On GitHub, open the repository, then **Settings**, then **Pages**.
2. Under **Build and deployment**, set **Source** to **Deploy from a branch**.
3. Choose the branch **main** and the folder **/ (root)**, and **Save**. The `.nojekyll` file tells GitHub to serve
   the files as they are.

To preview a branch before it is merged, choose that branch in step 3 instead.

## The repository

| Path | What it is |
|---|---|
| `index.html`, `explorer/index.html` | The two pages |
| `assets/` | Styles, scripts (`js/stats.js` holds the statistics), Apache ECharts 5.6.1 (Apache-2.0, vendored), the icon |
| `data/raw/<publisher>/` | The source files as uploaded, renamed by publisher (`config/sources.yaml` maps each to its original name, URL and licence) |
| `data/processed/` | What the pages load, built from `data/raw` by `uv run breakdown build` |
| `config/sources.yaml` | The source register: every raw file's publisher, original name, URL, licence and use |
| `config/lenses.yaml` | The research goal's framework concepts as a lens on every measure (a suggestion; edit freely) |
| `src/breakdown/` | The build: one module per source |
| `tests/` | The build's rules and a rebuild check (pytest); the statistics against scipy (`node --test tests/js/*.test.mjs`) |
| `docs/` | The research goal and the methods |

## Rebuilding the data

After adding or replacing a file in `data/raw` (and its entry in `config/sources.yaml`):

```sh
uv sync --group dev
uv run breakdown build          # writes data/processed/
uv run pytest -q                # includes `breakdown build --check`
node --test tests/js/*.test.mjs # the statistics against scipy
```

A source whose layout changed stops the build with one line naming the file.

## Sources and licences

WIPO Global Innovation Index 2026 (CC BY 4.0); World Bank World Development Indicators (CC BY 4.0); UNDP Human
Development Reports; OECD How's Life? (CC BY 4.0); World Happiness Report 2026; Productivity Commission, Closing the Gap
Annual Data Compilation Report 2026; UN SDSN Sustainable Development Report 2026 and World Economic Forum Global Gender
Gap Report 2026 (context only). Each one's terms are in `config/sources.yaml` and on the explorer's Sources page; where
we were not sure of a licence, the register says so.

## Reused from IP Australia's other repositories

- From **Moria** (its dashboard): the hover-explainer popover, the safe DOM and formatting helpers, the ECharts theming
  and chart cards, the normal distribution, Holm and Benjamini-Hochberg code, the vendored ECharts, and the
  no-third-party content security policy.
- From **Econ**: the reading of the GII data file (`econ.ingest.gii`: the tree, scores against values by profile), and
  the working principles: deterministic stages that fail loudly, hashes for every input and output, a source register.
