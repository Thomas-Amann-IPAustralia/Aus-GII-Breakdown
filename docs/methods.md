# Methods

How the data behind the two pages are built, and how the explorer computes what it shows. The explorer is for early,
exploratory analysis: every number it gives is an association, the first and weakest of the research goal's levels of
evidence ("Evidence proportionate to the claim", `docs/research-goal.md` §2.2).

## The data

`uv run breakdown build` reads every file in `data/raw/` and writes `data/processed/`:

| Output | What it holds | From |
|---|---|---|
| `australia.json` | 2,442 Australian series by year | World Bank WDI (1,002 indicators with 5+ years), UNDP HDR (36), OECD How's Life? (15), World Happiness Report (8), Closing the Gap (1,381 national series with 4+ years) |
| `economies.json` | 221 measures across 197 economies | GII 2026 (169: every node's score, each indicator's value where WIPO's profile shows one, and population and GDP), the HDR 2025 annex (44), the WHR's 2025 values (8) |
| `gii-australia.json` | Australia's GII breakdown | GII 2026 data file and Appendix III |
| `manifest.json` | Each raw file's SHA-256, what was read and left out, each output's SHA-256 | |

The build is deterministic (canonical JSON, no timestamps): `uv run breakdown build --check` exits 2 if the committed
outputs differ from a rebuild, and CI runs it. A source whose layout changes stops the build with one line naming the
file. Values are kept to six significant figures.

### Source by source

- **GII 2026** (`sources/gii.py`). The Index Structure, Economies and Data sheets of WIPO's data file, read as Econ's
  `econ.ingest.gii` reads them. Every node gets a score (0-100); an indicator gets a value too when its PROFILE is
  "Value", as in the printed profiles. Each node's score is linked to its parent's (`parts_of`), so the explorer knows
  the tree. Appendix III marks the five indicators where higher is worse and the two at half weight.
- **World Bank WDI** (`sources/wdi.py`). Australia's download; topics from the code's first part, lenses from
  `config/lenses.yaml`.
- **UNDP HDR** (`sources/hdr.py`). Australia's series from the long-format file. The annex tables have merged,
  multi-row headers, so the 44 columns read are named one by one in `ANNEX` rather than guessed; rows are countries
  when their names match an ISO3 code exactly (groups and regions are listed in the manifest as left out). Each
  index is linked to its components (`PARTS`).
- **OECD How's Life?** (`sources/oecd.py`). A Data Explorer export, read by its row labels.
- **World Happiness Report** (`sources/whr.py`). Australia's years, and every country's latest year. The six
  "explained by" columns split the life evaluation itself, so they are linked to it.
- **Closing the Gap** (`sources/ctg.py`). National figures (`Aust`) of actual values: trajectories, estimates,
  assessments and confidence intervals are left out. A financial year is placed at the year it ends; a period of three
  to five years at its middle year (rounded down); changes over a period and longer periods are left out. A series
  is named from its description fields and breakdowns, leaving out defaults (all people, all ages, all areas).

Country names are matched exactly (`countries.py`): the GII's own names, then ISO 3166 through pycountry, then a short
list of the sources' own spellings. A fuzzy match could turn "Arab States" into a country, so there is none.

### Framework lenses

Every measure carries one of the research goal's five concepts (innovation potential, innovation activity, IP
protection and use, private and organisational outcomes, public value), or "conditions and context", or "composite".
The rules are prefixes in `config/lenses.yaml`, longest first. The tag helps find and pair measures; it is a
suggestion, and changing it is a one-line edit.

## The statistics

All in `assets/js/stats.js`, checked against scipy and numpy by `tests/js/stats.test.mjs`.

- **Correlations.** Pearson's r with a two-sided p from Student's t (n − 2 df) and a 95% interval from Fisher's z;
  Spearman's ρ (Pearson's r of average ranks) with the t approximation; Kendall's τ-b with the asymptotic test allowing
  for ties. Missing values are dropped pairwise.
- **Over time.** The transforms: levels, year-on-year change, % change, detrended (residuals from each series' own
  straight-line trend), log. Year-on-year change bridges a gap of up to 3 years as a per-year rate (some WDI series are
  published every second year). Every comparison also computes the correlation of year-on-year changes, and flags a
  probable shared trend when the levels correlate strongly and the changes do not. The lag-1 autocorrelations of both
  series give an **effective n**, n(1 − r₁ₓr₁ᵧ)/(1 + r₁ₓr₁ᵧ) (Bretherton and others, 1999), and the adjusted p uses it.
  The lag chart shows r at each lag from −6 to +6 against a band of ±1.96/√(effective n).
- **Across economies.** Log scales for skewed measures; a group filter (GII economies, income groups); a control,
  giving the partial correlation (the correlation of the residuals of X and Y on the control, df = n − 3) and an
  added-variable plot; Australia's percentiles, its residual from the fitted line, and its residual rank.
- **Checks** (`assets/js/explorer/common.js`): few pairs; one measure built from the other (the GII tree, the HDR
  indices, the WHR split); Pearson and Spearman disagreeing; the most influential point by Cook's distance and r
  without it; skewness above 1.5 (suggesting a log scale); near-identical measures; ranks; "higher is worse"
  indicators; mixed data years; subgroups; missing data; income as a likely confounder.
- **Correlation matrix.** Pairwise or complete cases; each variable's VIF (the diagonal of the inverse correlation
  matrix) and the set's condition number (√(largest/smallest eigenvalue), Jacobi rotations); a descriptive OLS of one
  measure on the others with standardised coefficients, 95% intervals and p-values.
- **Find correlates.** Every measure with enough overlap against a target, with Benjamini-Hochberg q-values and the
  count expected at p < 0.05 by chance alone. Measures built from or into the target are left out by default.

### What the explorer cannot do

It finds associations. It cannot estimate additionality, separate cause from effect, or say anything about firms or
people inside an economy. The research goal's causal questions need designs (natural experiments, difference-in-
differences, matched firm-level data) and data this repository does not hold.
