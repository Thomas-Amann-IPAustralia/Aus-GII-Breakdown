"""Shared by sources that read ABS data cubes (formatted xlsx tables): every table sheet, long.

ABS cubes put a title in the first few rows, one or two header rows, then data rows whose first cell is the row's
label (sometimes with section rows that have a label and no numbers). This reads each sheet best-effort into
`sheet`, `title` (the sheet's last title line), `section` (the most recent label-only row), `row`, `column` (the
header rows joined with " | "), `unit` (where a data row gives its own unit in a cell, such as "$'000"), `value` and
`value_text`, with `sheet_row` (the row in the sheet, counting from 1 as Excel does), so every value can be found in
the raw cube. Section rows can nest (indentation, which the cells do not record), so two blocks can share a section
name; `sheet_row` tells them apart. Check against the raw cube before relying on an unusual table.

No published cell is lost: a number with a footnote ("0 (b)") is read as the number, and a cell that is not a number
("np", not published; "-", nil or rounded to zero) is kept with an empty `value`; both keep the cell in `value_text`.
"""

from __future__ import annotations

import math
import re

import pandas as pd

UNIT = re.compile(r"^(\$'?000|\$m|\$b|\$|%|no\.|'000|number|person[- ]years?( of effort)?|pye|years?|fte)$", re.I)
NOTE = re.compile(r"^(-?[\d,]*\.?\d+)\s*(\([a-z]{1,2}\)\s*)+$")  # a number followed by footnote letters: "0 (b)"


def _num(x) -> float | None:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return None
    s = str(x).replace(",", "").strip()
    m = NOTE.match(s)
    try:
        v = float(m.group(1) if m else s)
    except ValueError:
        return None
    return v if math.isfinite(v) else None


def _text(x) -> str:
    return "" if x is None or (isinstance(x, float) and math.isnan(x)) else str(x).strip()


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
        body = i + 1  # the rows below the headers, so section rows above the first data row are read too
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
        for r in range(body, len(df)):
            label = df.iat[r, 0]
            cells = [_text(x) for x in df.iloc[r, 1:]]
            vals = [_num(c) for c in cells]
            if pd.isna(label):
                continue
            if all(not c or UNIT.match(c) for c in cells):  # a label and nothing else: a section row
                section = str(label).strip()
                continue
            unit = next((c for c in cells if UNIT.match(c)), None)  # a row that states its own unit
            for j, (c, v) in enumerate(zip(cells, vals, strict=True), start=1):
                if not c or UNIT.match(c):
                    continue
                text = c if v is None or NOTE.match(c.replace(",", "")) else None  # anything but a plain number
                out.append((sheet.strip(), title, section, str(label).strip(), cols[j], unit, v, text, r + 1))
    return pd.DataFrame(
        out, columns=["sheet", "title", "section", "row", "column", "unit", "value", "value_text", "sheet_row"]
    )
