"""Writes tests/js/expected.json: reference values from scipy and numpy for tests/js/stats.test.mjs.

Run after changing the inputs: `uv run python tests/js/make_expected.py`. The inputs are fixed pseudo-random draws,
with ties and a trend, so the JavaScript is checked on the cases the explorer meets.
"""

import json
from pathlib import Path

import numpy as np
from scipy import stats

rng = np.random.default_rng(20261021)
n = 30
x = rng.normal(size=n).round(3)
y = (0.6 * x + rng.normal(scale=0.8, size=n)).round(3)
z = (0.5 * x + rng.normal(size=n)).round(3)
w = (0.3 * y - 0.4 * z + rng.normal(size=n)).round(3)
tx = np.round(rng.integers(0, 6, size=n), 0).astype(float)  # many ties
ty = np.round(tx + rng.integers(-2, 3, size=n), 0).astype(float)
trend = (np.arange(n) * 0.5 + rng.normal(scale=0.7, size=n).cumsum()).round(6)

out = {
    "x": x.tolist(),
    "y": y.tolist(),
    "z": z.tolist(),
    "w": w.tolist(),
    "tx": tx.tolist(),
    "ty": ty.tolist(),
    "trend": trend.round(6).tolist(),
}

pr = stats.pearsonr(x, y)
ci = pr.confidence_interval(0.95)
out["pearson"] = {"r": pr.statistic, "p": pr.pvalue, "lo": ci.low, "hi": ci.high}
sr = stats.spearmanr(tx, ty)
out["spearman_ties"] = {"r": sr.statistic, "p": sr.pvalue}
kt = stats.kendalltau(tx, ty, method="asymptotic")
out["kendall_ties"] = {"tau": kt.statistic, "p": kt.pvalue}
kt2 = stats.kendalltau(x, y, method="asymptotic")
out["kendall"] = {"tau": kt2.statistic, "p": kt2.pvalue}
out["t"] = [
    {"t": t, "df": df, "p": 2 * stats.t.sf(abs(t), df)}
    for t, df in [(2.1, 5), (0.3, 28), (4.5, 3), (1.96, 1000), (2.5, 1.7)]
]
out["tcrit"] = [{"df": df, "q": stats.t.ppf(0.975, df)} for df in (3, 10, 28)]

# OLS of w on y and z, with standard errors, as statsmodels would give
X = np.column_stack([np.ones(n), y, z])
beta, *_ = np.linalg.lstsq(X, w, rcond=None)
resid = w - X @ beta
df = n - 3
s2 = resid @ resid / df
cov = s2 * np.linalg.inv(X.T @ X)
se = np.sqrt(np.diag(cov))
r2 = 1 - (resid @ resid) / ((w - w.mean()) @ (w - w.mean()))
out["ols"] = {
    "b": beta.tolist(),
    "se": se.tolist(),
    "p": (2 * stats.t.sf(np.abs(beta / se), df)).tolist(),
    "r2": r2,
    "adj_r2": 1 - (1 - r2) * (n - 1) / df,
    "std": [None, beta[1] * y.std(ddof=1) / w.std(ddof=1), beta[2] * z.std(ddof=1) / w.std(ddof=1)],
}


# partial correlation of x and w controlling for z
def res(a, b):
    B = np.column_stack([np.ones(n), b])
    return a - B @ np.linalg.lstsq(B, a, rcond=None)[0]


rp = np.corrcoef(res(x, z), res(w, z))[0, 1]
tp = rp * np.sqrt((n - 3) / (1 - rp**2))
out["partial"] = {"r": rp, "p": 2 * stats.t.sf(abs(tp), n - 3)}

# VIF and condition number of y, z, w
R = np.corrcoef(np.vstack([y, z, w]))
out["vif"] = np.diag(np.linalg.inv(R)).tolist()
ev = np.linalg.eigvalsh(R)
out["condition"] = float(np.sqrt(ev.max() / ev.min()))

# lag-1 autocorrelation (statsmodels' acf definition) and Cook's distance of y on x
d = trend - trend.mean()
out["acf1"] = float((d[:-1] @ d[1:]) / (d @ d))
B = np.column_stack([np.ones(n), x])
h = np.diag(B @ np.linalg.inv(B.T @ B) @ B.T)
e = y - B @ np.linalg.lstsq(B, y, rcond=None)[0]
s2c = e @ e / (n - 2)
out["cooks"] = (e**2 / (2 * s2c) * h / (1 - h) ** 2).tolist()
out["skew"] = float(stats.skew(trend, bias=False))

# multiple testing
p = np.array([0.001, 0.008, 0.039, 0.041, 0.042, 0.06, 0.074, 0.205, 0.212, 0.216])
out["p_many"] = p.tolist()
out["bh"] = stats.false_discovery_control(p, method="bh").tolist()
m = len(p)
holm = np.empty(m)
run = 0
for r, i in enumerate(np.argsort(p)):
    run = max(run, min(1, (m - r) * p[i]))
    holm[i] = run
out["holm"] = holm.tolist()

Path(__file__).with_name("expected.json").write_text(json.dumps(out, indent=1) + "\n")
