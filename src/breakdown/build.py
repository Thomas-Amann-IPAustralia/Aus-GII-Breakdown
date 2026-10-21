"""`breakdown build`: read every raw file in data/raw and write the data the two pages load (data/processed/).

Outputs (canonical JSON, deterministic: the same raw files always give the same bytes, and no timestamps):
- australia.json: every Australian series by year (WDI, HDR, OECD How's Life, WHR, Closing the Gap);
- economies.json: every economy's values (GII 2026, the HDR annex, the WHR's latest year), aligned to one list;
- gii-australia.json: Australia's GII 2026 breakdown, for the landing page;
- manifest.json: each raw file's SHA-256, what was read and left out, each output's SHA-256.

`breakdown build --check` rebuilds in memory and exits 2 if any output differs from what is committed.
Fails loudly: a source whose layout changed stops the build (exit 2) with one line naming the file.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

from .countries import Countries
from .lenses import Lenses
from .model import BuildError, EconVar, TimeVar, canonical, sha256, sig, write_atomic
from .sources import ctg, gii, hdr, oecd, wdi, whr

ROOT = Path(__file__).resolve().parents[2]
OUT = Path("data/processed")


def _time(v: TimeVar) -> dict:
    years = sorted(v.values)
    start, end = years[0], years[-1]
    d = {
        "id": v.id,
        "name": v.name,
        "source": v.source,
        "topic": v.topic,
        "lens": v.lens,
        "unit": v.unit,
        "kind": v.kind,
        "start": start,
        "values": [sig(v.values[y]) if y in v.values else None for y in range(start, end + 1)],
    }
    for k in ("description", "note"):
        if getattr(v, k):
            d[k] = getattr(v, k)
    if v.parts_of:
        d["parts_of"] = sorted(v.parts_of)
    if v.labels:
        d["labels"] = {str(y): s for y, s in sorted(v.labels.items())}
    return d


def _econ(v: EconVar, order: list[str]) -> dict:
    d = {
        "id": v.id,
        "name": v.name,
        "source": v.source,
        "topic": v.topic,
        "lens": v.lens,
        "unit": v.unit,
        "kind": v.kind,
        "year": v.year,
        "values": [sig(v.values[i]) if i in v.values else None for i in order],
    }
    for k in ("description", "note"):
        if getattr(v, k):
            d[k] = getattr(v, k)
    if v.parts_of:
        d["parts_of"] = sorted(v.parts_of)
    if v.years and len(set(v.years.values())) > 1:
        d["years"] = [v.years.get(i) for i in order]
    return d


def build(root: Path) -> dict[str, str]:
    """Every output's path (relative to root) and its text."""
    raw = root / "data/raw"
    register = yaml.safe_load((root / "config/sources.yaml").read_text(encoding="utf-8"))["sources"]
    lenses = Lenses(root / "config/lenses.yaml")
    counts: dict[str, dict] = {}

    economies, gii_vars, page, counts["gii"] = gii.read(
        raw / "wipo-gii/gii-2026-data.xlsx", raw / "wipo-gii/gii-2026-appendix-3-sources-and-definitions.md", lenses
    )
    countries = Countries({iso: e["name"] for iso, e in economies.items()})

    time_vars: list[TimeVar] = []
    for name, (vs, c) in {
        "wdi": wdi.read(raw / "world-bank/wdi-australia.xls", lenses),
        "hdr_series": hdr.read_series(raw / "undp-hdr/hdr-australia-series.xlsx", lenses),
        "oecd_wise": oecd.read(raw / "oecd/oecd-hows-life-current-wellbeing-australia.xlsx", lenses),
        "whr_series": whr.read_series(raw / "whr/whr-2026-figure-2-1.xlsx", lenses),
        "ctg": ctg.read(raw / "closing-the-gap", lenses),
    }.items():
        time_vars += vs
        counts[name] = c

    econ_vars: list[EconVar] = list(gii_vars)
    for name, (vs, c) in {
        "hdr_annex": hdr.read_annex(raw / "undp-hdr/hdr-2025-statistical-annex-tables-1-7.xlsx", countries, lenses),
        "whr_latest": whr.read_latest(raw / "whr/whr-2026-figure-2-1.xlsx", countries, lenses),
    }.items():
        econ_vars += vs
        counts[name] = c

    for kind, vs in (("time", time_vars), ("economy", econ_vars)):
        ids = [v.id for v in vs]
        if len(ids) != len(set(ids)):
            dup = sorted({i for i in ids if ids.count(i) > 1})[:3]
            raise BuildError(f"build: duplicate {kind} variable ids {dup}; two sources or breakdowns collide")
        known = set(ids)
        for v in vs:
            for p in v.parts_of:
                if p not in known:
                    v.parts_of = [q for q in v.parts_of if q in known]  # a composite this file does not carry

    isos = sorted({i for v in econ_vars for i in v.values})
    economy_rows = []
    for iso in isos:
        e = economies.get(iso, {})
        economy_rows.append(
            {
                "iso3": iso,
                "name": countries.name(iso),
                "income": e.get("income"),
                "income_code": e.get("income_code"),
                "region": e.get("region"),
                "in_gii": iso in economies,
            }
        )

    outputs = {
        "australia.json": {"mode": "time", "variables": [_time(v) for v in sorted(time_vars, key=lambda v: v.id)]},
        "economies.json": {
            "mode": "economy",
            "economies": economy_rows,
            "variables": [_econ(v, isos) for v in sorted(econ_vars, key=lambda v: v.id)],
        },
        "gii-australia.json": _round(page),
    }
    texts = {f"{OUT}/{k}": canonical(v) + "\n" for k, v in outputs.items()}

    sources = []
    for s in register:
        p = root / s["file"]
        files = sorted(p.glob("*")) if p.is_dir() else [p]
        for f in files:
            if not f.exists():
                raise BuildError(f"config/sources.yaml: {s['id']} names {s['file']}, which is missing")
        sources.append(
            {
                **s,
                "files": [
                    {"path": str(f.relative_to(root)), "sha256": sha256(f), "bytes": f.stat().st_size} for f in files
                ],
            }
        )
    manifest = {
        "lenses": lenses.lenses,
        "sources": sources,
        "read": counts,
        "totals": {"time_variables": len(time_vars), "economy_variables": len(econ_vars), "economies": len(isos)},
        "outputs": {k: _text_sha(t) for k, t in sorted(texts.items())},
    }
    texts[f"{OUT}/manifest.json"] = canonical(manifest) + "\n"
    return texts


def _round(obj):
    if isinstance(obj, float):
        return sig(obj)
    if isinstance(obj, dict):
        return {k: _round(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_round(v) for v in obj]
    return obj


def _text_sha(text: str) -> str:
    import hashlib

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="breakdown", description=__doc__.split("\n\n")[0])
    ap.add_argument("command", choices=["build"])
    ap.add_argument("--check", action="store_true", help="exit 2 if the committed outputs differ from a rebuild")
    ap.add_argument("--root", type=Path, default=ROOT)
    a = ap.parse_args(argv)
    try:
        texts = build(a.root)
    except BuildError as e:
        print(f"breakdown build failed: {e}", file=sys.stderr)
        return 2
    if a.check:
        stale = [p for p, t in texts.items() if not (a.root / p).exists() or (a.root / p).read_text("utf-8") != t]
        if stale:
            print(
                f"breakdown build --check: out of date: {', '.join(stale)} (run `uv run breakdown build`)",
                file=sys.stderr,
            )
            return 2
        print("breakdown build --check: outputs match the raw files")
        return 0
    for p, t in texts.items():
        write_atomic(a.root / p, t)
    m = canonical  # keep the summary short: counts only
    print(
        f"wrote {len(texts)} files to {OUT}/: "
        + m({k: v for k, v in yaml.safe_load(texts[f"{OUT}/manifest.json"])["totals"].items()})
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
