// The statistics behind the explorer. The normal distribution, Holm, Benjamini-Hochberg and the log-gamma come from
// Moria's dashboard (Moria/dashboard/assets/js/stats.js, itself a port of Moria's stats.py); the rest is new here.
// tests/js/stats.test.mjs checks every function against scipy and numpy on fixed inputs (tests/js/expected.json).
//
// Conventions: inputs are plain arrays; null, undefined and non-finite values are missing and dropped pairwise.
// Every p-value is two-sided.

// ------------------------------------------------------------------------------------------- distributions

/** The standard normal upper tail, P(Z > z). */
export function normSf(z) {
  return 0.5 * erfc(z / Math.SQRT2);
}
function erfc(x) {
  const z = Math.abs(x);
  const t = 1 / (1 + 0.5 * z);
  const r = t * Math.exp(-z * z - 1.26551223 + t * (1.00002368 + t * (0.37409196 + t * (0.09678418 + t * (-0.18628806 +
    t * (0.27886807 + t * (-1.13520398 + t * (1.48851587 + t * (-0.82215223 + t * 0.17087277)))))))));
  return x >= 0 ? r : 2 - r;
}
/** The standard normal quantile (Acklam's rational approximation). */
export function normPpf(p) {
  const a = [-39.69683028665376, 220.9460984245205, -275.9285104469687, 138.357751867269, -30.66479806614716, 2.506628277459239];
  const b = [-54.47609879822406, 161.5858368580409, -155.6989798598866, 66.80131188771972, -13.28068155288572];
  const c = [-0.007784894002430293, -0.3223964580411365, -2.400758277161838, -2.549732539343734, 4.374664141464968, 2.938163982698783];
  const d = [0.007784695709041462, 0.3224671290700398, 2.445134137142996, 3.754408661907416];
  const pl = 0.02425;
  if (p < pl) {
    const q = Math.sqrt(-2 * Math.log(p));
    return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1);
  }
  if (p > 1 - pl) return -normPpf(1 - p);
  const q = p - 0.5, r = q * q;
  return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1);
}

export function lgamma(z) {
  // Lanczos approximation
  const g = 7;
  const c = [0.99999999999980993, 676.5203681218851, -1259.1392167224028, 771.32342877765313, -176.61502916214059,
    12.507343278686905, -0.13857109526572012, 9.9843695780195716e-6, 1.5056327351493116e-7];
  if (z < 0.5) return Math.log(Math.PI / Math.sin(Math.PI * z)) - lgamma(1 - z);
  z -= 1;
  let x = c[0];
  for (let i = 1; i < g + 2; i++) x += c[i] / (z + i);
  const t = z + g + 0.5;
  return 0.5 * Math.log(2 * Math.PI) + (z + 0.5) * Math.log(t) - t + Math.log(x);
}

/** The regularised incomplete beta function I_x(a, b) (continued fraction, as in Numerical Recipes). */
export function ibeta(x, a, b) {
  if (x <= 0) return 0;
  if (x >= 1) return 1;
  const bt = Math.exp(lgamma(a + b) - lgamma(a) - lgamma(b) + a * Math.log(x) + b * Math.log(1 - x));
  return x < (a + 1) / (a + b + 2) ? (bt * betacf(x, a, b)) / a : 1 - (bt * betacf(1 - x, b, a)) / b;
}
function betacf(x, a, b) {
  const TINY = 1e-300;
  let c = 1, d = 1 - ((a + b) * x) / (a + 1);
  if (Math.abs(d) < TINY) d = TINY;
  d = 1 / d;
  let h = d;
  for (let m = 1; m <= 300; m++) {
    const m2 = 2 * m;
    let aa = (m * (b - m) * x) / ((a + m2 - 1) * (a + m2));
    d = 1 + aa * d; if (Math.abs(d) < TINY) d = TINY;
    c = 1 + aa / c; if (Math.abs(c) < TINY) c = TINY;
    d = 1 / d; h *= d * c;
    aa = (-(a + m) * (a + b + m) * x) / ((a + m2) * (a + m2 + 1));
    d = 1 + aa * d; if (Math.abs(d) < TINY) d = TINY;
    c = 1 + aa / c; if (Math.abs(c) < TINY) c = TINY;
    d = 1 / d;
    const del = d * c;
    h *= del;
    if (Math.abs(del - 1) < 3e-16) break;
  }
  return h;
}

/** Two-sided p-value of Student's t with df degrees of freedom: P(|T| > |t|). */
export function tP(t, df) {
  if (!(df > 0) || !Number.isFinite(t)) return Number.isFinite(t) ? NaN : 0;
  return ibeta(df / (df + t * t), df / 2, 0.5);
}
/** Student's t quantile for a two-sided level (e.g. 0.95 gives the 97.5th percentile), by bisection. */
export function tCrit(level, df) {
  const target = 1 - level;
  let lo = 0, hi = 1000;
  for (let i = 0; i < 200; i++) {
    const mid = (lo + hi) / 2;
    if (tP(mid, df) > target) lo = mid; else hi = mid;
  }
  return (lo + hi) / 2;
}

// ------------------------------------------------------------------------------------------- basics

const ok = (v) => v != null && Number.isFinite(v);

/** The pairs where both values are present. */
export function pairs(x, y) {
  const a = [], b = [], idx = [];
  for (let i = 0; i < x.length; i++) if (ok(x[i]) && ok(y[i])) { a.push(x[i]); b.push(y[i]); idx.push(i); }
  return { x: a, y: b, idx };
}
export function mean(a) {
  let s = 0;
  for (const v of a) s += v;
  return s / a.length;
}
export function sd(a) {
  const m = mean(a);
  let s = 0;
  for (const v of a) s += (v - m) ** 2;
  return Math.sqrt(s / (a.length - 1));
}
export function median(a) {
  const s = a.filter(ok).sort((p, q) => p - q);
  if (!s.length) return NaN;
  const m = s.length >> 1;
  return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
}
/** Sample skewness (the adjusted Fisher-Pearson coefficient, as pandas' skew). */
export function skew(a) {
  const n = a.length;
  if (n < 3) return NaN;
  const m = mean(a);
  let m2 = 0, m3 = 0;
  for (const v of a) { m2 += (v - m) ** 2; m3 += (v - m) ** 3; }
  m2 /= n; m3 /= n;
  if (m2 === 0) return 0;
  return (Math.sqrt(n * (n - 1)) / (n - 2)) * (m3 / m2 ** 1.5);
}
/** Ranks, with ties given their average rank (1-based). */
export function ranks(a) {
  const idx = a.map((v, i) => i).sort((i, j) => a[i] - a[j]);
  const r = new Array(a.length);
  for (let s = 0; s < idx.length;) {
    let e = s;
    while (e + 1 < idx.length && a[idx[e + 1]] === a[idx[s]]) e++;
    const avg = (s + e) / 2 + 1;
    for (let k = s; k <= e; k++) r[idx[k]] = avg;
    s = e + 1;
  }
  return r;
}
export function zscores(a) {
  const v = a.filter(ok);
  const m = mean(v), s = sd(v);
  return a.map((x) => (ok(x) && s > 0 ? (x - m) / s : null));
}

// ------------------------------------------------------------------------------------------- correlation

/** Pearson's r of complete pairs (inputs already paired). */
export function pearsonR(x, y) {
  const n = x.length;
  if (n < 3) return NaN;
  const mx = mean(x), my = mean(y);
  let sxy = 0, sxx = 0, syy = 0;
  for (let i = 0; i < n; i++) {
    const dx = x[i] - mx, dy = y[i] - my;
    sxy += dx * dy; sxx += dx * dx; syy += dy * dy;
  }
  if (sxx === 0 || syy === 0) return NaN;
  return Math.max(-1, Math.min(1, sxy / Math.sqrt(sxx * syy)));
}

/**
 * The test of a correlation r from n pairs: t with df = n - 2 - k (k controls), its p-value, and a 95% interval
 * from Fisher's z (se = 1 / sqrt(n - 3 - k)). `nEff` replaces n where pairs are not independent.
 */
export function corrTest(r, n, { k = 0, nEff = null, level = 0.95 } = {}) {
  const m = nEff ?? n;
  const df = m - 2 - k;
  if (!Number.isFinite(r) || df < 1) return { r, n, df, t: NaN, p: NaN, lo: NaN, hi: NaN };
  const t = Math.abs(r) >= 1 ? Math.sign(r) * Infinity : r * Math.sqrt(df / (1 - r * r));
  const p = tP(t, df);
  let lo = NaN, hi = NaN;
  if (m - 3 - k > 0) {
    const z = Math.atanh(Math.max(-0.999999, Math.min(0.999999, r)));
    const h = -normPpf((1 - level) / 2) / Math.sqrt(m - 3 - k);
    lo = Math.tanh(z - h);
    hi = Math.tanh(z + h);
  }
  return { r, n, df, t, p, lo, hi };
}

export function pearson(x, y, opts) {
  const p = pairs(x, y);
  return corrTest(pearsonR(p.x, p.y), p.x.length, opts);
}

/** Spearman's rho: Pearson's r of the ranks; p from the t approximation, as scipy.stats.spearmanr. */
export function spearman(x, y, opts) {
  const p = pairs(x, y);
  const res = corrTest(pearsonR(ranks(p.x), ranks(p.y)), p.x.length, opts);
  return { ...res, lo: NaN, hi: NaN }; // Fisher's interval is for Pearson's r; not shown for rho
}

/** Kendall's tau-b with the asymptotic test allowing for ties, as scipy.stats.kendalltau(method="asymptotic"). */
export function kendall(x, y) {
  const p = pairs(x, y);
  const n = p.x.length;
  if (n < 3) return { tau: NaN, z: NaN, p: NaN, n };
  let s = 0;
  for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) s += Math.sign(p.x[j] - p.x[i]) * Math.sign(p.y[j] - p.y[i]);
  const ties = (a) => {
    const c = new Map();
    for (const v of a) c.set(v, (c.get(v) || 0) + 1);
    let t1 = 0, t2 = 0, t3 = 0;
    for (const t of c.values()) { t1 += t * (t - 1); t2 += t * (t - 1) * (t - 2); t3 += t * (t - 1) * (2 * t + 5); }
    return { t1, t2, t3 };
  };
  const tx = ties(p.x), ty = ties(p.y);
  const n0 = (n * (n - 1)) / 2;
  const denom = Math.sqrt((n0 - tx.t1 / 2) * (n0 - ty.t1 / 2));
  const tau = denom > 0 ? s / denom : NaN;
  const v = (n * (n - 1) * (2 * n + 5) - tx.t3 - ty.t3) / 18 + (tx.t1 * ty.t1) / (2 * n * (n - 1)) +
    (tx.t2 * ty.t2) / (9 * n * (n - 1) * (n - 2));
  const z = v > 0 ? s / Math.sqrt(v) : NaN;
  return { tau, z, p: Number.isFinite(z) ? 2 * normSf(Math.abs(z)) : NaN, n };
}

// ------------------------------------------------------------------------------------------- regression

/** Ordinary least squares of y on x (one predictor): slope, intercept, their standard errors, R², residuals. */
export function linFit(x, y) {
  const n = x.length;
  const mx = mean(x), my = mean(y);
  let sxy = 0, sxx = 0;
  for (let i = 0; i < n; i++) { sxy += (x[i] - mx) * (y[i] - my); sxx += (x[i] - mx) ** 2; }
  const slope = sxy / sxx, intercept = my - slope * mx;
  const resid = y.map((v, i) => v - (intercept + slope * x[i]));
  let sse = 0, sst = 0;
  for (let i = 0; i < n; i++) { sse += resid[i] ** 2; sst += (y[i] - my) ** 2; }
  const s2 = sse / (n - 2);
  return { slope, intercept, seSlope: Math.sqrt(s2 / sxx), r2: sst > 0 ? 1 - sse / sst : NaN, resid, s2, sxx, mx, n };
}

/** Cook's distance of each point in a one-predictor fit (how much the fitted line moves without it). */
export function cooks(x, y) {
  const f = linFit(x, y);
  return x.map((xi, i) => {
    const h = 1 / f.n + (xi - f.mx) ** 2 / f.sxx;
    return (f.resid[i] ** 2 / (2 * f.s2)) * (h / (1 - h) ** 2);
  });
}

/** Solve A x = b and invert A together (Gauss-Jordan with partial pivoting). Throws on a singular matrix. */
export function invert(A) {
  const n = A.length;
  const M = A.map((row, i) => [...row, ...Array.from({ length: n }, (_, j) => (i === j ? 1 : 0))]);
  for (let c = 0; c < n; c++) {
    let piv = c;
    for (let r = c + 1; r < n; r++) if (Math.abs(M[r][c]) > Math.abs(M[piv][c])) piv = r;
    if (Math.abs(M[piv][c]) < 1e-12) throw new Error("singular");
    [M[c], M[piv]] = [M[piv], M[c]];
    const d = M[c][c];
    for (let j = 0; j < 2 * n; j++) M[c][j] /= d;
    for (let r = 0; r < n; r++) {
      if (r === c) continue;
      const f = M[r][c];
      if (f) for (let j = 0; j < 2 * n; j++) M[r][j] -= f * M[c][j];
    }
  }
  return M.map((row) => row.slice(n));
}

/**
 * OLS of y on several predictors (columns of X, complete cases only; an intercept is added). Returns coefficients
 * with standard errors, t, p and 95% intervals, R², adjusted R², and standardised coefficients (betas).
 */
export function ols(y, X) {
  const n = y.length, k = X.length;
  const rows = y.map((_, i) => [1, ...X.map((c) => c[i])]);
  const XtX = Array.from({ length: k + 1 }, (_, a) => Array.from({ length: k + 1 }, (_, b) => rows.reduce((s, r) => s + r[a] * r[b], 0)));
  const Xty = Array.from({ length: k + 1 }, (_, a) => rows.reduce((s, r, i) => s + r[a] * y[i], 0));
  const inv = invert(XtX);
  const beta = inv.map((row) => row.reduce((s, v, j) => s + v * Xty[j], 0));
  const fitted = rows.map((r) => r.reduce((s, v, j) => s + v * beta[j], 0));
  const resid = y.map((v, i) => v - fitted[i]);
  const my = mean(y);
  const sse = resid.reduce((s, e) => s + e * e, 0), sst = y.reduce((s, v) => s + (v - my) ** 2, 0);
  const df = n - k - 1;
  const s2 = sse / df;
  const tc = tCrit(0.95, df);
  const sy = sd(y);
  const coef = beta.map((b, j) => {
    const se = Math.sqrt(s2 * inv[j][j]);
    const t = b / se;
    const sx = j === 0 ? NaN : sd(X[j - 1]);
    return { b, se, t, p: tP(t, df), lo: b - tc * se, hi: b + tc * se, std: j === 0 ? NaN : (b * sx) / sy, stdLo: j === 0 ? NaN : ((b - tc * se) * sx) / sy, stdHi: j === 0 ? NaN : ((b + tc * se) * sx) / sy };
  });
  const r2 = 1 - sse / sst;
  return { coef, r2, adjR2: 1 - ((1 - r2) * (n - 1)) / df, n, k, df, resid, s2 };
}

/** Residuals of each of `cols` after regressing it on `controls` (with an intercept); complete cases only. */
export function residualise(cols, controls) {
  if (!controls.length) return cols;
  return cols.map((c) => ols(c, controls).resid);
}

/**
 * Partial correlation of x and y controlling for the columns in Z: the correlation of what is left of each after
 * removing what Z predicts, tested with df = n - 2 - k.
 */
export function partial(x, y, Z, opts = {}) {
  const keep = [];
  for (let i = 0; i < x.length; i++) if (ok(x[i]) && ok(y[i]) && Z.every((z) => ok(z[i]))) keep.push(i);
  const pick = (a) => keep.map((i) => a[i]);
  const zs = Z.map(pick);
  if (keep.length < Z.length + 4) return { ...corrTest(NaN, keep.length, { k: Z.length }), idx: keep };
  let rx, ry;
  try {
    [rx, ry] = residualise([pick(x), pick(y)], zs);
  } catch {
    return { ...corrTest(NaN, keep.length, { k: Z.length }), idx: keep, singular: true };
  }
  return { ...corrTest(pearsonR(rx, ry), keep.length, { ...opts, k: Z.length }), idx: keep, rx, ry };
}

// ------------------------------------------------------------------------------------------- matrices

/** The correlation matrix of complete cases (listwise), or of each pair's own overlap (pairwise). */
export function corrMatrix(cols, { method = "pearson", listwise = false } = {}) {
  const k = cols.length;
  let use = cols;
  if (listwise) {
    const keep = [];
    for (let i = 0; i < cols[0].length; i++) if (cols.every((c) => ok(c[i]))) keep.push(i);
    use = cols.map((c) => keep.map((i) => c[i]));
  }
  const R = [], N = [], P = [];
  for (let a = 0; a < k; a++) {
    R.push([]); N.push([]); P.push([]);
    for (let b = 0; b < k; b++) {
      const t = a === b ? { r: 1, n: use[a].filter(ok).length, p: 0 } : method === "spearman" ? spearman(use[a], use[b]) : pearson(use[a], use[b]);
      R[a].push(t.r); N[a].push(t.n); P[a].push(t.p);
    }
  }
  return { R, N, P };
}

/** Eigenvalues of a symmetric matrix (cyclic Jacobi rotations), largest first. */
export function eigSym(A) {
  const n = A.length;
  const a = A.map((r) => r.slice());
  for (let sweep = 0; sweep < 100; sweep++) {
    let off = 0;
    for (let p = 0; p < n; p++) for (let q = p + 1; q < n; q++) off += a[p][q] ** 2;
    if (off < 1e-22) break;
    for (let p = 0; p < n; p++) {
      for (let q = p + 1; q < n; q++) {
        if (Math.abs(a[p][q]) < 1e-15) continue;
        const theta = (a[q][q] - a[p][p]) / (2 * a[p][q]);
        const t = Math.sign(theta || 1) / (Math.abs(theta) + Math.sqrt(theta * theta + 1));
        const c = 1 / Math.sqrt(t * t + 1), s = t * c;
        for (let k = 0; k < n; k++) {
          const akp = a[k][p], akq = a[k][q];
          a[k][p] = c * akp - s * akq;
          a[k][q] = s * akp + c * akq;
        }
        for (let k = 0; k < n; k++) {
          const apk = a[p][k], aqk = a[q][k];
          a[p][k] = c * apk - s * aqk;
          a[q][k] = s * apk + c * aqk;
        }
      }
    }
  }
  return a.map((r, i) => r[i]).sort((p, q) => q - p);
}

/**
 * Multicollinearity of a set of variables over their complete cases: each one's variance inflation factor (the
 * diagonal of the inverse correlation matrix, 1 / (1 - R²) of it on the others) and the condition number (the square
 * root of the largest over the smallest eigenvalue of the correlation matrix).
 */
export function collinearity(cols) {
  const keep = [];
  for (let i = 0; i < cols[0].length; i++) if (cols.every((c) => ok(c[i]))) keep.push(i);
  const use = cols.map((c) => keep.map((i) => c[i]));
  const n = keep.length, k = cols.length;
  if (n < k + 2) return { n, k, vif: cols.map(() => NaN), condition: NaN, tooFew: true };
  const { R } = corrMatrix(use);
  if (R.some((row) => row.some((v) => !Number.isFinite(v)))) return { n, k, vif: cols.map(() => NaN), condition: NaN, constant: true };
  let vif;
  try {
    vif = invert(R).map((row, i) => row[i]);
  } catch {
    vif = cols.map(() => Infinity);
  }
  const ev = eigSym(R);
  const min = ev[ev.length - 1];
  return { n, k, vif, condition: min > 1e-12 ? Math.sqrt(ev[0] / min) : Infinity, eigen: ev, idx: keep };
}

// ------------------------------------------------------------------------------------------- time series

/** Lag-1 autocorrelation of a yearly series given as an array with gaps (consecutive years only). */
export function acf1(a) {
  const v = a.filter(ok);
  if (v.length < 4) return NaN;
  const m = mean(v);
  let num = 0, den = 0;
  for (let i = 0; i < a.length; i++) {
    if (!ok(a[i])) continue;
    den += (a[i] - m) ** 2;
    if (i + 1 < a.length && ok(a[i + 1])) num += (a[i] - m) * (a[i + 1] - m);
  }
  return den > 0 ? num / den : NaN;
}

/**
 * The effective number of independent pairs when both series are autocorrelated (Bretherton and others, 1999):
 * n (1 - r1x r1y) / (1 + r1x r1y). Only ever lowers n, and never below 3.
 */
export function effectiveN(n, r1x, r1y) {
  const rho = r1x * r1y;
  if (!Number.isFinite(rho) || rho <= 0) return n;
  return Math.max(3, Math.min(n, (n * (1 - rho)) / (1 + rho)));
}

export const MAX_GAP = 3;

/** Transform a yearly series (a Map of year to value). */
export function transform(series, how) {
  const out = new Map();
  const years = [...series.keys()].sort((a, b) => a - b);
  if (how === "level") return new Map(years.map((y) => [y, series.get(y)]));
  if (how === "log") {
    for (const y of years) if (series.get(y) > 0) out.set(y, Math.log(series.get(y)));
    return out;
  }
  if (how === "diff" || how === "pct") {
    // Against the previous observation: consecutive years, or across a gap of up to MAX_GAP years as a per-year
    // rate (a series published every second year still has changes). Longer gaps leave the year out.
    for (let i = 1; i < years.length; i++) {
      const gap = years[i] - years[i - 1];
      if (gap > MAX_GAP) continue;
      const a = series.get(years[i - 1]), b = series.get(years[i]);
      if (how === "diff") out.set(years[i], (b - a) / gap);
      else if (a > 0 && b > 0) out.set(years[i], ((b / a) ** (1 / gap) - 1) * 100);
      else if (a !== 0 && gap === 1) out.set(years[i], ((b - a) / Math.abs(a)) * 100);
    }
    return out;
  }
  if (how === "detrend") {
    if (years.length < 3) return out;
    const f = linFit(years, years.map((y) => series.get(y)));
    years.forEach((y, i) => out.set(y, f.resid[i]));
    return out;
  }
  throw new Error(`unknown transform ${how}`);
}

// ------------------------------------------------------------------------------------------- many tests

/** Holm-adjusted p-values in one family. */
export function holm(p) {
  const idx = p.map((v, i) => i).filter((i) => Number.isFinite(p[i])).sort((a, b) => p[a] - p[b] || a - b);
  const m = idx.length;
  const out = p.map(() => NaN);
  let run = 0;
  idx.forEach((i, r) => {
    run = Math.max(run, Math.min(1, (m - r) * p[i]));
    out[i] = run;
  });
  return out;
}

/** Benjamini-Hochberg q-values in one family. */
export function bh(p) {
  const idx = p.map((v, i) => i).filter((i) => Number.isFinite(p[i])).sort((a, b) => p[a] - p[b] || a - b);
  const m = idx.length;
  const out = p.map(() => NaN);
  let run = 1;
  for (let r = m - 1; r >= 0; r--) {
    run = Math.min(run, (p[idx[r]] * m) / (r + 1));
    out[idx[r]] = Math.min(1, run);
  }
  return out;
}
