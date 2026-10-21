"""UNDP's Human Development Report: Australia's series (hdr-australia-series.xlsx) and the 2025 statistical annex
(hdr-2025-statistical-annex-tables-1-7.xlsx), a table per index with one row per country.

The annex tables have two- to four-row headers with merged cells, so their columns are named here, one by one, rather
than guessed: `ANNEX` lists every column read (sheet, column index, code, name, unit, year). A row is a country when
its name maps to an ISO3 code; the human development groups, regions and the world are left out.

Each index's components are linked to it (`parts_of`), so the explorer can say when a correlation is part with whole:
the HDI is built from life expectancy, schooling and income, so it correlates with them by construction.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

import pandas as pd

from ..countries import Countries
from ..lenses import Lenses
from ..model import BuildError, EconVar, TimeVar, clean, number

# The composite each code feeds (UNDP's own codes from hdr-australia-series.xlsx; annex-only codes are ours).
PARTS = {
    "hdi": ["le", "eys", "mys", "gnipc"],
    "gdi": ["hdi_f", "hdi_m", "le_f", "le_m", "eys_f", "eys_m", "mys_f", "mys_m", "gni_pc_f", "gni_pc_m"],
    "hdi_f": ["le_f", "eys_f", "mys_f", "gni_pc_f"],
    "hdi_m": ["le_m", "eys_m", "mys_m", "gni_pc_m"],
    "gii": ["mmr", "abr", "pr_f", "pr_m", "se_f", "se_m", "lfpr_f", "lfpr_m"],
    "ihdi": ["hdi", "coef_ineq", "ineq_le", "ineq_edu", "ineq_inc", "loss"],
    "coef_ineq": ["ineq_le", "ineq_edu", "ineq_inc"],
    "loss": ["hdi", "ihdi"],
    "phdi": ["hdi", "co2_prod", "mf", "co2_index", "mf_index", "adj_factor", "diff_hdi_phdi"],
    "adj_factor": ["co2_index", "mf_index"],
    "co2_index": ["co2_prod"],
    "mf_index": ["mf"],
}


def _parts_of(code: str, prefix: str) -> list[str]:
    return sorted(f"{prefix}:{whole}" for whole, parts in PARTS.items() if code in parts)


# (sheet, column, code, name, unit). The year is read from the header cell above the data where there is one.
ANNEX = [
    ("Table 1. HDI", 2, "hdi", "Human Development Index (HDI)", "index, 0-1"),
    ("Table 1. HDI", 4, "le", "Life expectancy at birth", "years"),
    ("Table 1. HDI", 6, "eys", "Expected years of schooling", "years"),
    ("Table 1. HDI", 8, "mys", "Mean years of schooling", "years"),
    ("Table 1. HDI", 10, "gnipc", "Gross national income (GNI) per capita", "2021 PPP $"),
    ("Table 1. HDI", 12, "gni_minus_hdi_rank", "GNI per capita rank minus HDI rank", "ranks"),
    ("Table 2. HDI trends", 24, "hdi_growth_2010_2023", "Average annual HDI growth, 2010-2023", "%"),
    ("Table 2. HDI trends", 26, "hdi_growth_1990_2023", "Average annual HDI growth, 1990-2023", "%"),
    ("Table 3. IHDI", 4, "ihdi", "Inequality-adjusted HDI (IHDI)", "index, 0-1"),
    ("Table 3. IHDI", 6, "loss", "IHDI: overall loss from inequality", "%"),
    ("Table 3. IHDI", 10, "coef_ineq", "Coefficient of human inequality", "%"),
    ("Table 3. IHDI", 12, "ineq_le", "Inequality in life expectancy", "%"),
    ("Table 3. IHDI", 16, "ineq_edu", "Inequality in education", "%"),
    ("Table 3. IHDI", 20, "ineq_inc", "Inequality in income", "%"),
    ("Table 3. IHDI", 24, "share_poorest40", "Income share held by the poorest 40%", "%"),
    ("Table 3. IHDI", 26, "share_richest10", "Income share held by the richest 10%", "%"),
    ("Table 3. IHDI", 28, "share_richest1", "Income share held by the richest 1%", "%"),
    ("Table 3. IHDI", 30, "gini", "Gini coefficient", "0-100"),
    ("Table 4. GDI", 2, "gdi", "Gender Development Index (GDI)", "female HDI / male HDI"),
    ("Table 4. GDI", 6, "hdi_f", "HDI, female", "index, 0-1"),
    ("Table 4. GDI", 8, "hdi_m", "HDI, male", "index, 0-1"),
    ("Table 4. GDI", 10, "le_f", "Life expectancy at birth, female", "years"),
    ("Table 4. GDI", 12, "le_m", "Life expectancy at birth, male", "years"),
    ("Table 4. GDI", 14, "eys_f", "Expected years of schooling, female", "years"),
    ("Table 4. GDI", 16, "eys_m", "Expected years of schooling, male", "years"),
    ("Table 4. GDI", 18, "mys_f", "Mean years of schooling, female", "years"),
    ("Table 4. GDI", 20, "mys_m", "Mean years of schooling, male", "years"),
    ("Table 4. GDI", 22, "gni_pc_f", "Estimated GNI per capita, female", "2021 PPP $"),
    ("Table 4. GDI", 24, "gni_pc_m", "Estimated GNI per capita, male", "2021 PPP $"),
    ("Table 5. GII", 2, "gii", "Gender Inequality Index", "index, 0-1 (higher is more unequal)"),
    ("Table 5. GII", 6, "mmr", "Maternal mortality ratio", "deaths per 100,000 live births"),
    ("Table 5. GII", 8, "abr", "Adolescent birth rate", "births per 1,000 women ages 15-19"),
    ("Table 5. GII", 10, "pr_f", "Share of seats in parliament held by women", "%"),
    ("Table 5. GII", 12, "se_f", "Population with at least some secondary education, female", "% ages 25 and older"),
    ("Table 5. GII", 14, "se_m", "Population with at least some secondary education, male", "% ages 25 and older"),
    ("Table 5. GII", 16, "lfpr_f", "Labour force participation rate, female", "% ages 15 and older"),
    ("Table 5. GII", 18, "lfpr_m", "Labour force participation rate, male", "% ages 15 and older"),
    ("Table 7. PHDI", 4, "phdi", "Planetary pressures-adjusted HDI (PHDI)", "index, 0-1"),
    ("Table 7. PHDI", 6, "diff_hdi_phdi", "PHDI: difference from HDI value", "%"),
    ("Table 7. PHDI", 10, "adj_factor", "Adjustment factor for planetary pressures", "index, 0-1"),
    ("Table 7. PHDI", 12, "co2_prod", "Carbon dioxide emissions per capita (production)", "tonnes"),
    ("Table 7. PHDI", 14, "co2_index", "Carbon dioxide emissions (production) index", "index, 0-1"),
    ("Table 7. PHDI", 16, "mf", "Material footprint per capita", "tonnes"),
    ("Table 7. PHDI", 18, "mf_index", "Material footprint index", "index, 0-1"),
]
TOPIC = {
    "Table 1": "Human development",
    "Table 2": "Human development",
    "Table 3": "Inequality",
    "Table 4": "Gender",
    "Table 5": "Gender",
    "Table 7": "Planetary pressures",
}


def read_annex(path: Path, countries: Countries, lenses: Lenses) -> tuple[list[EconVar], dict]:
    try:
        sheets = pd.read_excel(path, sheet_name=None, engine="calamine", header=None)
    except Exception as e:  # noqa: BLE001
        raise BuildError(f"hdr_annex: cannot read {path} ({e})") from e
    out, unmatched = [], Counter()
    for sheet, col, code, name, unit in ANNEX:
        if sheet not in sheets:
            raise BuildError(f"hdr_annex: no sheet {sheet!r} in {path}; the annex's layout changed")
        t = sheets[sheet]
        first = _first_country_row(t, sheet)
        year = _header_year(t, col, first)
        values = {}
        for i in range(first, len(t)):
            label = t.iat[i, 1]
            if not isinstance(label, str) or (v := number(t.iat[i, col])) is None:
                continue
            iso = countries.iso3(label)
            if iso is None:
                unmatched[label.strip()] += 1
                continue
            values[iso] = v
        if len(values) < 100:
            raise BuildError(f"hdr_annex: {sheet} column {col} ({name}) has only {len(values)} countries; check ANNEX")
        out.append(
            EconVar(
                id=f"hdr:{code}",
                name=f"{name} (HDR)",
                source="hdr_annex",
                topic=TOPIC[sheet[:7]],
                lens=lenses.of("hdr", code),
                unit=unit,
                year=year,
                values=values,
                description=f"UNDP Human Development Report 2025, statistical annex, {sheet.split('. ')[0].lower()}.",
                parts_of=_parts_of(code, "hdr"),
                kind="index" if "index" in (unit or "") else "value",
            )
        )
    # every unmatched label is an aggregate or a note (the manifest lists them to keep that checkable)
    return out, {"variables": len(out), "unmatched_labels": sorted(n for n in unmatched if len(n) < 60)}


def _first_country_row(t: pd.DataFrame, sheet: str) -> int:
    for i in range(min(15, len(t))):
        if number(t.iat[i, 0]) == 1 and isinstance(t.iat[i, 1], str):
            return i
    raise BuildError(f"hdr_annex: {sheet} has no row ranked 1 in its first 15 rows")


def _header_year(t: pd.DataFrame, col: int, first: int) -> str | None:
    for i in range(first - 1, -1, -1):
        v = t.iat[i, col]
        if isinstance(v, int | float) and not pd.isna(v) and 1990 <= v <= 2030:
            return str(int(v))
        if isinstance(v, str) and v.strip()[:4].isdigit():
            return v.strip()
    return None


def read_series(path: Path, lenses: Lenses) -> tuple[list[TimeVar], dict]:
    try:
        d = pd.read_excel(path, engine="calamine", dtype=str)
    except Exception as e:  # noqa: BLE001
        raise BuildError(f"hdr_series: cannot read {path} ({e})") from e
    if set(d["countryIsoCode"].dropna()) != {"AUS"}:
        raise BuildError(f"hdr_series: {path} holds countries other than Australia")
    out, single = [], 0
    for (index_code, code, name), g in d.groupby(["indexCode", "indicatorCode", "indicator"], sort=True):
        values = {int(y): v for y, x in zip(g["year"], g["value"], strict=True) if (v := number(x)) is not None}
        if len(values) < 5:
            single += 1  # ranks and groups for one year
            continue
        name = clean(name).replace("eduation", "education")
        out.append(
            TimeVar(
                id=f"hdr:{code}",
                name=f"{name} (HDR)",
                source="hdr_series",
                topic={
                    "HDI": "Human development",
                    "GDI": "Gender",
                    "GII": "Gender",
                    "IHDI": "Inequality",
                    "PHDI": "Planetary pressures",
                }.get(index_code, "Human development"),
                lens=lenses.of("hdr", code),
                unit=None,
                values=values,
                description=f"UNDP Human Development Report data, part of the {index_code} family.",
                parts_of=_parts_of(code, "hdr"),
                kind="index" if "Index" in name or code == "phdi" else "value",
            )
        )
    return out, {"variables": len(out), "one_year_only": single}
