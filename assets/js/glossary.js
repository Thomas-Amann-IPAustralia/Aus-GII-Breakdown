// The explainers behind every dotted term and every "?" on both pages. The popover is Moria's
// (Moria/dashboard/assets/js/glossary.js): hover or focus a term to see it, Escape to close. Each entry has a title,
// a plain-language definition, how this tool uses it, what to watch out for, and, for numbers, a reading of the
// value being hovered.

import { el, esc, fmt, pval, r2d } from "./util.js";

export const GROUPS = {
  corr: "Correlation",
  test: "Testing and uncertainty",
  time: "Comparing over time",
  model: "Regression and multicollinearity",
  traps: "Traps in reading a correlation",
  data: "Data and measurement",
  frame: "The research goal's framework",
  gii: "The Global Innovation Index",
};

const strength = (r) => {
  const a = Math.abs(r);
  return a >= 0.9 ? "very strong" : a >= 0.7 ? "strong" : a >= 0.5 ? "moderate" : a >= 0.3 ? "weak" : a >= 0.1 ? "very weak" : "next to none";
};

export const TERMS = {
  // ------------------------------------------------------------------------------------------- correlation
  correlation: {
    title: "Correlation", group: "corr",
    short: "How closely two measures move together, from −1 (one always rises as the other falls) through 0 (no straight-line pattern) to +1 (they rise and fall together).",
    tool: "Every comparison reports three correlations: Pearson's r, Spearman's ρ and Kendall's τ. They answer slightly different questions; when they disagree, the chart usually shows why.",
    watch: "A correlation is a pattern in the data, not a cause. It says nothing about which way an influence runs, or whether a third thing drives both.",
  },
  pearson: {
    title: "Pearson's r", group: "corr",
    short: "The correlation of the values themselves: how well a straight line fits the points. r² is the share of one measure's variation the line accounts for.",
    tool: "The headline number in each comparison, with its 95% confidence interval and p-value.",
    watch: "Sensitive to outliers (one extreme economy or year can make or break it) and blind to curved patterns. Check it against Spearman's ρ.",
    interpret: (v) => `${r2d(v)}: a ${strength(v)} ${v >= 0 ? "positive" : "negative"} straight-line association. A line through the points accounts for ${Math.round(v * v * 100)}% of the variation (r²).`,
  },
  spearman: {
    title: "Spearman's ρ (rho)", group: "corr",
    short: "The correlation of the ranks instead of the values: does a higher X tend to come with a higher Y, whether or not in a straight line?",
    tool: "Shown beside Pearson's r. Prefer it when a measure is skewed, has outliers, or is itself a rank or a score.",
    watch: "If ρ is much stronger than r, the pattern is consistent but curved (or an outlier drags r down); if r is much stronger than ρ, a few extreme points may be making it.",
    interpret: (v) => `${r2d(v)}: a ${strength(v)} ${v >= 0 ? "positive" : "negative"} association in rank order (monotonic, not necessarily straight).`,
  },
  kendall: {
    title: "Kendall's τ (tau)", group: "corr",
    short: "Another rank correlation: of every pair of points, the share that are in the same order on both measures minus the share in opposite order.",
    tool: "Tau-b, which allows for ties. Its values run smaller than ρ for the same data (a τ of 0.5 is roughly a ρ of 0.7), so compare it with itself, not with r.",
    interpret: (v) => `${r2d(v)}: of all pairs, ${Math.round(((1 + v) / 2) * 100)}% are ordered the same way on both measures (ignoring ties).`,
  },
  r2: {
    title: "R² (R-squared)", group: "corr",
    short: "The share of the variation in Y that a fitted line (or model) accounts for, from 0 to 1. With one predictor it is r².",
    watch: "A high R² means the line fits, not that X explains Y in any causal sense. Two series that both rise over time give a high R² whatever they measure.",
    interpret: (v) => `${fmt(v, 2)}: the fit accounts for about ${Math.round(v * 100)}% of the variation.`,
  },
  slope: {
    title: "Slope", group: "corr",
    short: "How much Y changes, on average, for one unit more of X along the fitted straight line, in Y's units per X unit.",
    watch: "Depends on the units and the transform: a slope on logs reads as percentages; a slope on year-on-year changes is about changes, not levels.",
  },
  monotonic: {
    title: "Monotonic", group: "corr",
    short: "Always moving the same way: as X rises, Y rises (or always falls), though not necessarily at a steady rate. Rank correlations measure this.",
  },
  scatter: {
    title: "Scatter plot", group: "corr",
    short: "Each point is one observation (a year, or an economy) placed by its X and Y values. The fitted line is the straight line closest to the points.",
    tool: "Always look at the scatter before trusting a number: clusters, curves and outliers are obvious in the chart and invisible in r.",
  },

  // ------------------------------------------------------------------------------------------- testing
  p_value: {
    title: "p-value", group: "test",
    short: "If there were truly no association, how often would chance alone give a correlation at least this strong from this many points? Small p: chance is an unlikely explanation on its own.",
    tool: "Two-sided. For comparisons over time, an adjusted p-value allows for the fact that consecutive years are not independent.",
    watch: "p is not the probability the association is real, nor a measure of its size or importance. With many points tiny effects get tiny p; with few points large effects can miss 0.05. Testing many pairs guarantees some small p's by chance (see multiple comparisons).",
    interpret: (v) => `${pval(v)}: with no real association, a correlation at least this strong would turn up by chance ${v >= 0.5 ? "more often than not" : `roughly 1 time in ${fmt(Math.max(2, Math.round(1 / Math.max(v, 1e-9))))}`}. ${v < 0.01 ? "Chance alone is an unlikely explanation." : v < 0.05 ? "Conventionally 'significant', but only just." : v < 0.1 ? "Weak evidence against chance." : "Chance is a perfectly good explanation."}`,
  },
  significance: {
    title: "Statistical significance", group: "test",
    short: "A label for p below a chosen threshold (usually 0.05). It means 'hard to explain by chance alone', not 'important' or 'causal'.",
    watch: "The 0.05 line is a convention. Report the interval and the size of the effect, not only whether it crossed the line.",
  },
  ci: {
    title: "Confidence interval (95%)", group: "test",
    short: "The range of correlations consistent with the data: if we could repeat the sampling many times, intervals built this way would contain the true value 95% of the time.",
    tool: "For Pearson's r, from Fisher's z transformation. A wide interval means the data cannot pin the association down; an interval spanning 0 means it could be nothing.",
    watch: "For a handful of years or economies the interval is wide whatever r is. Width is honesty about how little the data can say.",
  },
  n: {
    title: "n (number of pairs)", group: "test",
    short: "How many observations have both measures: overlapping years, or economies with both values. Missing either value drops the point.",
    watch: "Below about 10 pairs, correlations swing wildly from one point to the next. Below 30, treat them as a hint at most.",
    interpret: (v) => `${fmt(v)} pairs: ${v < 8 ? "far too few to say much; one point can change everything." : v < 15 ? "few; the interval will be wide." : v < 30 ? "a modest number; treat the result as a hint." : "enough to estimate a correlation reasonably, if the points are independent."}`,
  },
  power: {
    title: "Statistical power", group: "test",
    short: "The chance a test detects a real association of a given size. With few points, power is low: a real but moderate correlation will often come out 'not significant'.",
    watch: "'Not significant' with low power is absence of evidence, not evidence of absence.",
  },
  multiple_comparisons: {
    title: "Multiple comparisons", group: "test",
    short: "Test enough pairs and some will look strong by pure chance: at p < 0.05, about 1 test in 20 when nothing is going on.",
    tool: "Find correlates tests a target against hundreds or thousands of measures, then corrects with Benjamini-Hochberg and says how many would be expected by chance.",
    watch: "A correlation found by searching is a hypothesis to test on new data, not a finding. This is the 'garden of forking paths': every choice of transform, lag and period is another test.",
  },
  fdr: {
    title: "False discovery rate (Benjamini-Hochberg)", group: "test",
    short: "A correction for testing many pairs: it controls the expected share of false leads among the results you flag, rather than the chance of any false lead at all.",
    tool: "Gives each result a q-value. Flag the results with q < 0.05 and, on average, no more than 5% of them should be flukes, if the tests are roughly independent.",
    watch: "Many measures here move together (they share trends, sources or components), so the tests are not independent and the correction is only approximate.",
  },
  q_value: {
    title: "q-value", group: "test",
    short: "A p-value adjusted for the number of tests (Benjamini-Hochberg): the smallest false discovery rate at which this result would be flagged.",
    interpret: (v) => `${pval(v)}: ${v < 0.05 ? "survives the correction for searching many pairs." : v < 0.2 ? "does not survive the correction at 0.05; a weak lead." : "does not survive the correction: consistent with a fluke of searching."}`,
  },
  holm: {
    title: "Holm correction", group: "test",
    short: "A stricter correction for many tests that controls the chance of even one false lead. Moria uses it for its detectors; the explorer uses Benjamini-Hochberg, which suits exploring.",
  },

  // ------------------------------------------------------------------------------------------- time
  time_series: {
    title: "Time series", group: "time",
    short: "One measure tracked over successive years. Here: Australia's series from the World Bank, UNDP, the OECD, the World Happiness Report and Closing the Gap.",
    watch: "Years are not independent draws: this year looks like last year. That breaks the usual tests unless you allow for it.",
  },
  spurious: {
    title: "Spurious correlation (shared trend)", group: "time",
    short: "Two series that both trend over time will correlate strongly even if they have nothing to do with each other: GDP, population, patent filings and life expectancy all rose for decades.",
    tool: "Every comparison over time also reports the correlation of year-on-year changes. If the levels correlate but the changes don't, the shared trend is probably doing the work.",
    watch: "This is the most common way a time-series correlation misleads. Treat any correlation of trending levels as close to meaningless on its own.",
  },
  trend: {
    title: "Trend", group: "time",
    short: "A steady rise or fall over the years. Most economic and social series trend; their correlation in levels mostly measures that both have a trend.",
  },
  diff: {
    title: "Year-on-year change (first difference)", group: "time",
    short: "Each year's value minus the year before. Comparing changes asks: in years when X rose more than usual, did Y also rise more than usual?",
    tool: "The default cure for a shared trend. Where a series skips years (some are published every second year), the change since the previous value is spread evenly over the gap, up to 3 years; longer gaps leave the year out.",
    watch: "Differences are noisier than levels and lose slow, long-run relationships. A real effect that takes years to appear can vanish in year-on-year changes (try a lag).",
  },
  pct: {
    title: "Percentage change", group: "time",
    short: "Each year's change as a percentage of the year before (across a gap of up to 3 years, the average yearly growth). Like the first difference, but comparable across measures of different size.",
    watch: "Explodes when the earlier value is near zero; unreliable for measures that can be negative.",
  },
  detrend: {
    title: "Detrended (residuals from a linear trend)", group: "time",
    short: "Each series minus its own straight-line trend over its years. Compares the swings around the trends rather than the trends themselves.",
    watch: "Only removes a straight-line trend. A curved trend leaves a pattern in the residuals that can still correlate spuriously.",
  },
  log: {
    title: "Logarithm (log scale)", group: "data",
    short: "Takes the log of each value, so equal ratios become equal steps: 1,000 to 10,000 is the same distance as 10,000 to 100,000.",
    tool: "Use it for skewed measures such as GDP, population, patents or money, where a few large values otherwise dominate. Only positive values have a log; others are dropped.",
  },
  autocorrelation: {
    title: "Autocorrelation (lag-1)", group: "time",
    short: "How strongly a series correlates with itself one year earlier. Near 1 for smooth trending series; near 0 for series that jump around.",
    tool: "When both series are autocorrelated the years are not independent, so the tool lowers n to an effective n before testing.",
    interpret: (v) => `${r2d(v)}: ${v > 0.8 ? "very smooth; each year is mostly last year plus a little." : v > 0.5 ? "fairly smooth; consecutive years are far from independent." : v > 0.2 ? "some persistence." : "little persistence from year to year."}`,
  },
  effective_n: {
    title: "Effective n", group: "time",
    short: "The number of independent observations the years are worth once their autocorrelation is allowed for: n × (1 − r₁ₓr₁ᵧ) / (1 + r₁ₓr₁ᵧ) (Bretherton and others, 1999).",
    tool: "The adjusted p-value uses it. Two smooth trending series of 40 years can be worth only 3 or 4 independent points.",
    watch: "An approximation. It still assumes the relationship is the same throughout the period.",
    interpret: (v) => `${fmt(v, 2)}: the years carry about as much independent information as ${fmt(Math.round(v))} unrelated observations.`,
  },
  adjusted_p: {
    title: "Adjusted p-value (for autocorrelation)", group: "time",
    short: "The p-value recomputed with the effective n instead of the number of years, so smooth trending series don't look more certain than they are.",
    interpret: (v) => TERMS.p_value.interpret(v),
  },
  lag: {
    title: "Lag", group: "time",
    short: "Shifting one series in time: a lag of +2 pairs X in each year with Y two years later. Asks whether X leads Y (or Y leads X, for a negative lag).",
    tool: "The lag chart shows the correlation at each shift (a cross-correlation). The band marks roughly where chance alone would land.",
    watch: "A peak at a lag is suggestive of timing, never proof of cause. Trying many lags is itself multiple testing.",
  },
  cross_correlation: {
    title: "Cross-correlation", group: "time",
    short: "The correlation between X and Y at each lag. A peak away from zero hints that one moves ahead of the other.",
  },
  indexed: {
    title: "Standardised (z-scores)", group: "data",
    short: "Each value as the number of standard deviations above or below its own average. Puts two measures on one scale so their shapes can be compared on a single axis.",
    tool: "Used to draw two series on one chart without a second axis, which would invent a match by choosing the scales.",
  },

  // ------------------------------------------------------------------------------------------- model
  regression: {
    title: "Regression (OLS)", group: "model",
    short: "Fitting the line (or, with several predictors, the plane) that minimises the squared distances to the points: ordinary least squares.",
    tool: "One predictor: the line on each scatter. Several predictors: the model in the correlation matrix, which estimates each one's association holding the others fixed.",
    watch: "Descriptive here. A coefficient is an association conditional on the other variables in the model, not an effect of changing that variable.",
  },
  residual: {
    title: "Residual", group: "model",
    short: "How far a point sits above (+) or below (−) the fitted line: the part of Y the line does not account for.",
    tool: "Australia's residual says whether it sits higher or lower on Y than economies with similar X. A starting point for 'gaps' and 'opportunities', never the end of the argument.",
  },
  partial: {
    title: "Partial correlation (controlling for)", group: "model",
    short: "The correlation between X and Y after removing what a third measure (the control) predicts in each. Asks: among economies with similar control values, do X and Y still go together?",
    tool: "Pick a control in a cross-economy comparison (GDP per capita is the usual first one). The chart can show the residuals, an added-variable plot.",
    watch: "Controls only for what you include, measured as you measured it. Controlling for something caused by X or Y can create or hide an association (a 'bad control').",
  },
  confounder: {
    title: "Confounder", group: "traps",
    short: "A third factor that drives both X and Y, making them correlate without one affecting the other. National income is the great confounder across economies: richer economies score higher on nearly everything.",
    tool: "Partial correlation can take out a confounder you have measured; nothing can take out one you haven't.",
  },
  multicollinearity: {
    title: "Multicollinearity", group: "model",
    short: "When predictors in a model are strongly correlated with each other, the model cannot tell their separate contributions apart: coefficients become unstable, wide and sometimes the 'wrong' sign.",
    tool: "The correlation matrix reports each variable's VIF and the set's condition number, and warns before you fit a model.",
    watch: "It does not bias the overall fit, only the split between predictors. GII pillars and sub-pillars are built to move together, so they are highly collinear.",
  },
  vif: {
    title: "VIF (variance inflation factor)", group: "model",
    short: "How much the uncertainty of a variable's coefficient is inflated by its correlation with the other predictors: 1 / (1 − R²) of it regressed on the rest.",
    tool: "Above 5 deserves a look; above 10 the variable is largely a copy of the others.",
    interpret: (v) => `${fmt(v, 3)}: ${v < 2 ? "little overlap with the others." : v < 5 ? "moderate overlap." : v < 10 ? "high: the others predict it well (R² ≈ " + fmt(1 - 1 / v, 2) + ")." : "very high: the others predict it almost entirely (R² ≈ " + fmt(1 - 1 / v, 2) + "); its coefficient is not separately identifiable."}`,
  },
  condition_number: {
    title: "Condition number", group: "model",
    short: "One number for the whole set's collinearity: the square root of the largest over the smallest eigenvalue of the correlation matrix.",
    interpret: (v) => `${fmt(v, 3)}: ${v < 10 ? "little collinearity." : v < 30 ? "moderate collinearity." : "strong collinearity: some combination of these variables is nearly constant."}`,
  },
  std_coef: {
    title: "Standardised coefficient (beta)", group: "model",
    short: "A regression coefficient in standard deviations: how many SDs Y moves per SD of X, holding the other predictors fixed. Lets predictors in different units be compared.",
  },
  adj_r2: {
    title: "Adjusted R²", group: "model",
    short: "R² penalised for the number of predictors, so adding a useless predictor doesn't make the model look better.",
  },
  overfitting: {
    title: "Overfitting", group: "model",
    short: "A model with many predictors relative to observations fits the noise in this sample and predicts new data badly. A rough rule: at least 10 to 20 observations per predictor.",
  },
  pairwise: {
    title: "Pairwise or complete cases", group: "data",
    short: "Pairwise: each correlation uses every observation that has both of its two measures. Complete cases (listwise): only observations with every measure in the set.",
    tool: "Pairwise keeps more data but each cell can rest on a different sample; complete cases make cells comparable. Models and VIFs always use complete cases.",
  },
  missing: {
    title: "Missing data", group: "data",
    short: "Values a source doesn't have. Here a missing value drops that year or economy from a comparison.",
    watch: "Data are rarely missing at random: smaller and poorer economies, and early years, are missing more often, which can bias a correlation.",
  },

  // ------------------------------------------------------------------------------------------- traps
  causation: {
    title: "Correlation is not causation", group: "traps",
    short: "A correlation can come from X affecting Y, Y affecting X, a third factor affecting both, how the sample was chosen, or chance. The data alone cannot tell these apart.",
    tool: "The research goal asks for evidence proportionate to the claim. Everything here is exploratory association: a reason to look closer, not a finding.",
  },
  reverse_causality: {
    title: "Reverse causality", group: "traps",
    short: "Y may drive X rather than the other way round: richer economies can afford more R&D, as well as R&D making economies richer.",
  },
  ecological_fallacy: {
    title: "Ecological fallacy", group: "traps",
    short: "A pattern across economies (or years) need not hold for the firms or people inside them. Economies with more patents being richer does not show that patenting firms are richer.",
    tool: "Every cross-economy comparison is at the level of economies. The research goal's questions about businesses and groups need firm- and person-level data.",
  },
  simpsons: {
    title: "Simpson's paradox", group: "traps",
    short: "A correlation that holds overall can reverse inside every subgroup, or the other way round, when the groups differ on a third factor. Colour by income group to check.",
  },
  outlier: {
    title: "Outlier and influential point", group: "traps",
    short: "A point far from the rest. An influential one is a point the fitted line depends on: without it, r or the slope changes a lot.",
    tool: "The checks name the most influential point (by Cook's distance) and say what r becomes without it.",
  },
  cooks: {
    title: "Cook's distance", group: "traps",
    short: "How far the fitted line moves when one point is left out, combining how unusual the point's X is (leverage) and how far it sits from the line.",
    interpret: (v) => `${fmt(v, 2)}: ${v > 1 ? "very influential: the line depends on this point." : v > 0.5 ? "influential." : "not especially influential."}`,
  },
  part_whole: {
    title: "Part and whole", group: "traps",
    short: "When one measure is built from the other (an index and one of its components), they correlate by construction. The HDI contains life expectancy; the GII score contains its pillars.",
    tool: "The tool knows the GII's tree, the HDR's indices and the WHR's breakdown, and flags such pairs.",
  },
  restricted_range: {
    title: "Restricted range", group: "traps",
    short: "Looking at only part of the range (only high-income economies, only recent years) usually weakens a correlation, because there is less variation to correlate.",
  },
  skewness: {
    title: "Skewness", group: "data",
    short: "How lopsided a distribution is. Strong right skew (a few very large values: GDP, patents, money) lets those few dominate Pearson's r.",
    tool: "The checks suggest a log scale when a positive measure is strongly skewed.",
    interpret: (v) => `${fmt(v, 2)}: ${Math.abs(v) < 0.5 ? "roughly symmetric." : Math.abs(v) < 1 ? "moderately skewed." : "strongly skewed; consider a log scale."}`,
  },

  // ------------------------------------------------------------------------------------------- data
  cross_section: {
    title: "Cross-section (economies compared)", group: "data",
    short: "Many economies at one point in time. Here: the GII 2026's 139 economies, the HDR's 193 countries and the WHR's 147.",
    watch: "Each source has its own data year, and the GII mixes years by economy. Economies are not independent experiments either: neighbours and trading partners share a lot.",
  },
  data_year: {
    title: "Data year", group: "data",
    short: "The year a value refers to, which is often earlier than the edition it appears in. The GII 2026 uses each economy's most recent value between 2016 and 2026.",
  },
  ppp: {
    title: "PPP (purchasing power parity)", group: "data",
    short: "Money converted at rates that equalise what a basket of goods costs in each economy, so incomes can be compared in real terms.",
  },
  composite_index: {
    title: "Composite index", group: "data",
    short: "A single number built by combining several indicators, each scaled and weighted (the GII, the HDI). Useful for ranking; hard to interpret in a correlation, because it blends many things.",
  },
  normalised_score: {
    title: "Normalised score (0-100)", group: "gii",
    short: "The GII rescales each indicator so economies sit between 0 and 100 (after treating outliers), then averages scores up the tree. A score is relative to the other economies, not an absolute level.",
  },
  rank: {
    title: "Rank", group: "data",
    short: "A position in an ordering (1st, 2nd…). Ranks are ordinal: the gap between 1st and 2nd need not equal the gap between 50th and 51st. Use Spearman's ρ with ranks.",
  },
  percentile: {
    title: "Percentile", group: "data",
    short: "The share of economies (with a value) that sit below this one. The 90th percentile is higher than 90% of them.",
    interpret: (v) => `${fmt(v, 2)}: higher than about ${Math.round(v)}% of the economies with a value.`,
  },

  // ------------------------------------------------------------------------------------------- framework
  lens: {
    title: "Framework lens", group: "frame",
    short: "Each measure is tagged with one of the research goal's five concepts (plus 'conditions and context' and 'composite'), to help you find and pair them. The tag is a suggestion, editable in config/lenses.yaml.",
    watch: "The research goal treats the links between the concepts as empirical questions, not assumed causal chains. A correlation between two lenses is a starting point for that question.",
  },
  potential: { title: "Innovation potential", group: "frame", short: "The capabilities, ideas, research, skills and opportunities from which innovation may emerge: education, researchers, R&D spending." },
  activity: { title: "Innovation activity", group: "frame", short: "Developing, adopting, diffusing and applying new or significantly improved products, processes and other solutions: publications, high-tech production and trade, creative output." },
  ip: { title: "IP protection and use", group: "frame", short: "Acquiring, managing, licensing, enforcing and strategically using registered rights: patent, trade mark and design filings, IP receipts and payments." },
  outcomes: { title: "Private and organisational outcomes", group: "frame", short: "Commercialisation, productivity, revenue, employment, investment and resilience for innovators and organisations: national accounts, labour, business entry." },
  public_value: { title: "Public value", group: "frame", short: "Net effects on prosperity, social progress, opportunity, sustainability, competition and public welfare: human development, health, well-being, inequality, Closing the Gap." },
  context: { title: "Conditions and context", group: "frame", short: "The settings the framework's questions turn on (research question 3): institutions, finance, markets, infrastructure, population." },
  composite: { title: "Composite index", group: "frame", short: "A headline index blending several of the concepts (the GII itself and its two sub-indices)." },
  additionality: {
    title: "Additionality", group: "frame",
    short: "The benefit that happens because a right, policy or service exists, compared with what would have happened anyway. The research goal's central question, and one a correlation cannot answer.",
  },
  causal_inference: {
    title: "Causal inference", group: "frame",
    short: "Methods that estimate what an intervention actually changes: experiments, natural experiments, difference-in-differences, regression discontinuity, instrumental variables. They need designs and data well beyond these aggregate series.",
  },
  evidence_levels: {
    title: "Evidence proportionate to the claim", group: "frame",
    short: "The research goal's sixth principle: exploratory correlations, observational estimates, causal effects and projections are kept distinct. Everything this tool shows is the first kind.",
  },

  // ------------------------------------------------------------------------------------------- gii
  gii: {
    title: "Global Innovation Index (GII)", group: "gii",
    short: "WIPO's annual ranking of economies' innovation: the simple average of an input sub-index (five pillars) and an output sub-index (two pillars), built from 79 indicators.",
  },
  pillar: {
    title: "Pillar and sub-pillar", group: "gii",
    short: "The GII's tree: 7 pillars (5 input, 2 output), each split into 3 sub-pillars, each averaging 2 to 6 indicators.",
  },
  inputs_outputs: {
    title: "Inputs and outputs", group: "gii",
    short: "Inputs (institutions, human capital and research, infrastructure, market and business sophistication) capture what enables innovation; outputs (knowledge and technology, creative outputs) capture its results.",
    watch: "Comparing outputs with inputs is a rough 'efficiency' view. It is not a production function: outputs are partly the same kinds of thing as inputs, measured differently.",
  },
  strength: {
    title: "Strength and weakness", group: "gii",
    short: "WIPO marks an economy's top-ranked indicators as strengths and bottom-ranked as weaknesses, overall and within its income group.",
  },
  outdated: {
    title: "Outdated", group: "gii",
    short: "The economy's latest data year for this indicator is older than the year most economies report.",
  },
  dmc: {
    title: "Data minimum coverage (DMC)", group: "gii",
    short: "The economy did not have enough indicators in this sub-pillar or pillar to meet WIPO's coverage rule; its score rests on fewer data.",
  },
  bad: {
    title: "Higher is worse (a 'bad')", group: "gii",
    short: "An indicator where a higher value is a poorer outcome (a tariff rate, a risk index, a dwell time). The GII's score turns it round; its value does not.",
  },
};

// --------------------------------------------------------------------------------------------- the popover

let pop, hideTimer, current;

function place(target) {
  const r = target.getBoundingClientRect();
  const p = pop.getBoundingClientRect();
  let top = r.bottom + 8;
  if (top + p.height > window.innerHeight - 10) top = Math.max(10, r.top - p.height - 8);
  const left = Math.min(Math.max(10, r.left + r.width / 2 - p.width / 2), window.innerWidth - p.width - 12);
  pop.style.top = `${top}px`;
  pop.style.left = `${left}px`;
}

function show(target) {
  clearTimeout(hideTimer);
  const key = target.dataset.term;
  const t = TERMS[key];
  if (!t) return;
  current = target;
  const value = target.dataset.value != null && target.dataset.value !== "" ? Number(target.dataset.value) : null;
  let html = `<h4>${esc(t.title)}</h4><p>${esc(t.short)}</p>`;
  if (value != null && !Number.isNaN(value) && t.interpret) html += `<p class="p-value"><strong>This value:</strong> ${esc(t.interpret(value))}</p>`;
  if (t.tool) html += `<p class="p-tool"><strong>Here:</strong> ${esc(t.tool)}</p>`;
  if (t.watch) html += `<p class="p-watch"><strong>Watch out:</strong> ${esc(t.watch)}</p>`;
  if (glossaryHref) html += `<p class="p-more"><a href="${esc(glossaryHref)}${esc(key)}">More in the glossary</a></p>`;
  pop.innerHTML = html; // every piece of text above is escaped
  pop.hidden = false;
  place(target);
}

function hideSoon() {
  clearTimeout(hideTimer);
  hideTimer = setTimeout(() => {
    pop.hidden = true;
    current = null;
  }, 180);
}

let glossaryHref = "#/glossary/";

/** Wire the popover once per page. `href` + a term's key is where "More in the glossary" points (null: no link). */
export function initPopover(href = "#/glossary/") {
  glossaryHref = href;
  pop = document.getElementById("popover");
  const find = (e) => e.target.closest?.("[data-term]");
  document.addEventListener("pointerover", (e) => {
    const t = find(e);
    if (t) show(t);
    else if (e.target.closest?.("#popover")) clearTimeout(hideTimer);
  });
  document.addEventListener("pointerout", (e) => {
    if (find(e) || e.target.closest?.("#popover")) hideSoon();
  });
  document.addEventListener("focusin", (e) => {
    const t = find(e);
    if (t) show(t);
  });
  document.addEventListener("focusout", (e) => {
    if (find(e)) hideSoon();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !pop.hidden) pop.hidden = true;
  });
  window.addEventListener("scroll", () => current && !pop.hidden && place(current), { passive: true, capture: true });
}

/** A term in running text: dotted underline, explainer on hover and focus. */
export function term(key, text, value) {
  return el("span.term", { tabindex: 0, "data-term": key, "data-value": value ?? "", role: "button", "aria-label": `${text ?? TERMS[key]?.title}: what is this?` }, text ?? TERMS[key]?.title ?? key);
}

/** A small "?" after a heading or label. */
export function tip(key) {
  return el("button.tipdot", { type: "button", "data-term": key, "aria-label": `What is ${TERMS[key]?.title ?? key}?` }, "?");
}

/** A number with its explainer: the value's own reading appears in the popover. */
export function num(key, value, text) {
  return term(key, text ?? fmt(value), value);
}
