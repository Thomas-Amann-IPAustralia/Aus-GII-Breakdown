"""Counts of Australian Businesses, including Entries and Exits (ABS 8165.0): the denominators for IP use.

Data cube 1 (national tables) from the latest release; cubes 2 to 11 (by state and industry class, survival by
subdivision, and by SA2 and LGA, each by employment and turnover size) from the latest release that has them, as the
ABS publishes those in December. Raw: the xlsx cubes (repo). Processed, long tables (one value per row):

- `national`: cube 1, every table: `table`, `table_title`, `period`, `row` (the row's label), `column`, `value`.
- `cubes`: cubes 2 to 11: `cube`, `table`, `table_title`, the cube's own id columns (state, industry code and label,
  SA2 or LGA code and label), `measure` (for example "Operating at start of financial year"), `size` (the employment
  or turnover range) and `value`.
"""

from __future__ import annotations

import re

import pandas as pd

from ..core import CorpusError, Ctx, http_get

BASE = "https://www.abs.gov.au/statistics/economy/business-indicators/counts-australian-businesses-including-entries-and-exits"


def _cube_links(release: str) -> list[str]:
    html = http_get(f"{BASE}/{release}").text
    return sorted(set(re.findall(r'/statistics/[^"]+?/(8165DC\d\d)\.xlsx', html)))


def _releases() -> list[str]:
    """The latest release and the one before it (cubes 2 to 11 come out later in the year)."""
    html = http_get(f"{BASE}/latest-release").text
    found = re.findall(r"jul(\d{4})-jun(\d{4})", html)
    if not found:
        raise CorpusError("abs_cabee: no release found on the latest-release page")
    latest = max(found, key=lambda x: int(x[1]))
    prev = (str(int(latest[0]) - 1), str(int(latest[1]) - 1))
    return [f"jul{latest[0]}-jun{latest[1]}", f"jul{prev[0]}-jun{prev[1]}"]


def _num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s.astype(str).str.replace(",", "").str.strip(), errors="coerce")


def parse_cube(df: pd.DataFrame, cube: str, table: str) -> pd.DataFrame | None:
    units = next((i for i in range(min(15, len(df))) if (df.iloc[i] == "no.").sum() >= 2), None)
    if units is None:
        return None
    ti = next((i for i in range(units) if re.match(r"(Businesses|Survival|Number) ", str(df.iat[i, 0]))), None)
    title = str(df.iat[ti, 0]) if ti is not None else ""
    head = df.iloc[units - 1].astype(str)
    has_group = units >= 2 and (ti is None or units - 2 > ti)
    group = df.iloc[units - 2].ffill() if has_group else pd.Series([None] * df.shape[1])
    id_cols, val_cols = [], []
    for j in range(df.shape[1]):
        u = str(df.iat[units, j])
        if u in ("Code", "Label", "Name"):
            id_cols.append((j, re.sub(r"[^a-z0-9]+", "_", f"{head.iat[j]} {u}".lower()).strip("_")))
        elif u == "no." or u == "%":
            g = group.iat[j]
            g = None if pd.isna(g) or str(g) == "nan" else str(g).strip().replace("Suriving", "Surviving")  # ABS typo
            val_cols.append((j, g, head.iat[j].strip(), u))
    body = df.iloc[units + 1 :]
    body = body[body.iloc[:, id_cols[0][0]].notna()] if id_cols else body
    frames = []
    for j, measure, size, unit in val_cols:
        f = pd.DataFrame({name: body.iloc[:, k].astype(str).str.strip() for k, name in id_cols})
        f["measure"], f["size"], f["unit"], f["value"] = measure, size, unit, _num(body.iloc[:, j]).values
        frames.append(f)
    if not frames:
        return None
    out = pd.concat(frames, ignore_index=True).dropna(subset=["value"])
    out.insert(0, "table_title", title.strip())
    out.insert(0, "table", table.strip())
    out.insert(0, "cube", cube)
    return out


def parse_national(df: pd.DataFrame, table: str) -> pd.DataFrame | None:
    units = next((i for i in range(min(15, len(df))) if (df.iloc[i] == "no.").sum() >= 1), None)
    if units is None:
        return None
    title = next((str(df.iat[i, 0]) for i in range(units) if str(df.iat[i, 0]).startswith("Table")), table)
    cols = df.iloc[units - 1].astype(str).str.replace(r"\s+", " ", regex=True).str.strip()
    rows, period = [], None
    for i in range(units + 1, len(df)):
        label = df.iat[i, 0]
        vals = _num(df.iloc[i, 1:])
        if pd.isna(label):
            continue
        if vals.isna().all():
            if re.fullmatch(r"\d{4}-\d{2}", str(label).strip()):
                period = str(label).strip()
            continue
        for j, v in vals.items():
            if pd.notna(v):
                rows.append((table, title, period, str(label).strip(), cols.iat[j], v))
    return pd.DataFrame(rows, columns=["table", "table_title", "period", "row", "column", "value"])


def run(ctx: Ctx) -> None:
    latest, prev = _releases()
    national, cubes = [], []
    for release in (latest, prev):
        names = _cube_links(release)
        want = ["8165DC01"] if release == latest else [n for n in names if n != "8165DC01"]
        if release == prev and not want:
            raise CorpusError(f"abs_cabee: {prev} has no cubes 2 to 11")
        for n in want:
            if n not in names:
                continue
            f = ctx.fetch(f"{BASE}/{release}/{n}.xlsx", f"{release}-{n}.xlsx", keep="repo")
            for sheet, df in pd.read_excel(f, sheet_name=None, engine="calamine", header=None, dtype=str).items():
                if not sheet.strip().startswith("Table"):
                    continue
                if n == "8165DC01":
                    t = parse_national(df, sheet)
                    if t is not None:
                        national.append(t.assign(release=release))
                else:
                    t = parse_cube(df, n, sheet)
                    if t is not None:
                        cubes.append(t.assign(release=release))
    ctx.table(pd.concat(national, ignore_index=True), "national", describe="Cube 1: national tables, long")
    ctx.table(pd.concat(cubes, ignore_index=True), "cubes", describe="Cubes 2 to 11, long")
