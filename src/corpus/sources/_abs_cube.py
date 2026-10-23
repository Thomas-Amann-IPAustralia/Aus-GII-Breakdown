"""Shared by sources that read ABS data cubes (formatted xlsx tables): every table sheet, long.

ABS cubes put a title in the first few rows, one or two header rows, then data rows whose first cell is the row's
label (sometimes with section rows that have a label and no numbers). This reads each sheet best-effort into
`sheet`, `title` (the sheet's last title line), `section` (the most recent label-only row), `row`, `column` (the
header rows joined with " | ") and `value`; check against the raw cube before relying on an unusual table.
"""

from __future__ import annotations

import math
import re

import pandas as pd


def _num(x) -> float | None:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return None
    try:
        v = float(str(x).replace(",", "").strip())
    except ValueError:
        return None
    return v if math.isfinite(v) else None


def read_cube(path, skip_sheets=("Contents", "Explanatory Notes", "Further information", "Disclaimer")) -> pd.DataFrame:
    out = []
    for sheet, df in pd.read_excel(path, sheet_name=None, engine="calamine", header=None, dtype=str).items():
        if sheet.strip() in skip_sheets or df.empty:
            continue
        numeric = df.apply(lambda r: sum(_num(x) is not None for x in r.iloc[1:]), axis=1)
        first_data = next((i for i in range(len(df)) if numeric.iat[i] >= 1 and pd.notna(df.iat[i, 0])), None)
        if first_data is None:
            continue
        # header rows: walking up from the first data row, skip section rows (a label and nothing else), then take
        # the contiguous rows that have something beyond the label column
        heads, i = [], first_data - 1
        while i >= 0 and df.iloc[i, 1:].isna().all():
            i -= 1
        while i >= 0 and len(heads) < 3 and df.iloc[i, 1:].notna().any():
            heads.insert(0, df.iloc[i].ffill())
            i -= 1
        titles = [str(df.iat[k, 0]) for k in range(min(8, len(df))) if re.match(r"\s*Table\s*\d", str(df.iat[k, 0]))]
        title = titles[0].strip() if titles else sheet
        cols = []
        for j in range(df.shape[1]):
            parts = [str(h.iat[j]).strip() for h in heads if pd.notna(h.iat[j]) and str(h.iat[j]).strip() != "nan"]
            cols.append(" | ".join(dict.fromkeys(parts)) if parts else f"col{j}")
        section = None
        for r in range(first_data, len(df)):
            label = df.iat[r, 0]
            vals = [_num(x) for x in df.iloc[r, 1:]]
            if pd.isna(label):
                continue
            if all(v is None for v in vals):
                section = str(label).strip()
                continue
            for j, v in enumerate(vals, start=1):
                if v is not None:
                    out.append((sheet.strip(), title, section, str(label).strip(), cols[j], v))
    return pd.DataFrame(out, columns=["sheet", "title", "section", "row", "column", "value"])
