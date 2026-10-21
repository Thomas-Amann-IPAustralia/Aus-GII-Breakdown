// Checks assets/js/stats.js against scipy and numpy (tests/js/expected.json, from make_expected.py).
// Run: node --test tests/js/*.test.mjs
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import * as S from "../../assets/js/stats.js";

const E = JSON.parse(readFileSync(new URL("./expected.json", import.meta.url)));
const close = (a, b, tol, what) => assert.ok(Math.abs(a - b) <= tol, `${what}: ${a} vs ${b} (tolerance ${tol})`);

test("Pearson's r, its p-value and Fisher interval match scipy", () => {
  const t = S.pearson(E.x, E.y);
  close(t.r, E.pearson.r, 1e-12, "r");
  close(t.p, E.pearson.p, 1e-9, "p");
  close(t.lo, E.pearson.lo, 1e-6, "lo");
  close(t.hi, E.pearson.hi, 1e-6, "hi");
});

test("Spearman's rho with ties matches scipy", () => {
  const t = S.spearman(E.tx, E.ty);
  close(t.r, E.spearman_ties.r, 1e-12, "rho");
  close(t.p, E.spearman_ties.p, 1e-9, "p");
});

test("Kendall's tau-b and its asymptotic p match scipy, with and without ties", () => {
  const a = S.kendall(E.tx, E.ty);
  close(a.tau, E.kendall_ties.tau, 1e-12, "tau ties");
  close(a.p, E.kendall_ties.p, 1e-6, "p ties");
  const b = S.kendall(E.x, E.y);
  close(b.tau, E.kendall.tau, 1e-12, "tau");
  close(b.p, E.kendall.p, 1e-6, "p");
});

test("Student's t tail and quantile match scipy", () => {
  for (const c of E.t) close(S.tP(c.t, c.df), c.p, 1e-9, `t=${c.t} df=${c.df}`);
  for (const c of E.tcrit) close(S.tCrit(0.95, c.df), c.q, 1e-6, `df=${c.df}`);
});

test("OLS coefficients, standard errors, p-values, R² and betas match numpy", () => {
  const f = S.ols(E.w, [E.y, E.z]);
  f.coef.forEach((c, j) => {
    close(c.b, E.ols.b[j], 1e-10, `b${j}`);
    close(c.se, E.ols.se[j], 1e-10, `se${j}`);
    close(c.p, E.ols.p[j], 1e-8, `p${j}`);
    if (j) close(c.std, E.ols.std[j], 1e-10, `beta${j}`);
  });
  close(f.r2, E.ols.r2, 1e-12, "r2");
  close(f.adjR2, E.ols.adj_r2, 1e-12, "adj r2");
});

test("partial correlation matches residual-on-residual correlation", () => {
  const t = S.partial(E.x, E.w, [E.z]);
  close(t.r, E.partial.r, 1e-10, "r");
  close(t.p, E.partial.p, 1e-8, "p");
});

test("VIF and condition number match numpy", () => {
  const c = S.collinearity([E.y, E.z, E.w]);
  c.vif.forEach((v, i) => close(v, E.vif[i], 1e-9, `vif${i}`));
  close(c.condition, E.condition, 1e-8, "condition");
});

test("lag-1 autocorrelation, Cook's distance and skewness match", () => {
  close(S.acf1(E.trend), E.acf1, 1e-12, "acf1");
  S.cooks(E.x, E.y).forEach((d, i) => close(d, E.cooks[i], 1e-10, `cook${i}`));
  close(S.skew(E.trend), E.skew, 1e-10, "skew");
});

test("Benjamini-Hochberg and Holm match scipy and the definition", () => {
  S.bh(E.p_many).forEach((q, i) => close(q, E.bh[i], 1e-12, `q${i}`));
  S.holm(E.p_many).forEach((q, i) => close(q, E.holm[i], 1e-12, `holm${i}`));
});

test("missing values are dropped pairwise, and transforms behave", () => {
  const t = S.pearson([1, 2, null, 4, 5, NaN], [2, 4, 6, 8, 11, 3]);
  assert.equal(t.n, 4);
  const s = new Map([[2000, 10], [2001, 12], [2003, 15], [2004, 18], [2009, 30]]);
  assert.deepEqual([...S.transform(s, "diff")], [[2001, 2], [2003, 1.5], [2004, 3]]); // a gap of 2 is a per-year rate; 5 is too long
  assert.deepEqual([...S.transform(s, "pct")].map(([y, v]) => [y, +v.toFixed(6)]), [[2001, 20], [2003, 11.803399], [2004, 20]]);
  assert.equal(S.effectiveN(30, 0.9, 0.9) < 4, true);
  assert.equal(S.effectiveN(30, 0.5, -0.5), 30);
  assert.deepEqual(S.ranks([3, 1, 3, 2]), [3.5, 1, 3.5, 2]);
});
