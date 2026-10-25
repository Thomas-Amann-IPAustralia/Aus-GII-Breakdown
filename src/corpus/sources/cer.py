"""Small-scale renewable installations by postcode (Clean Energy Regulator): solar panels, solar water heaters, heat
pumps, batteries, wind and hydro, monthly from 2001, as installations, capacity and (for batteries) certificates.

For the environmental pathway (section 2 of docs/data-plan.md): how fast green technologies spread, by place, beside
green patenting. Raw: each published file (repo; CSV files, and Excel workbooks that repeat them). Processed:

- `installations`, long, one row per technology, series, postcode and month: `technology` (solar_pv, wind, hydro,
  battery, solar_water_heater, heat_pump_water_heater), `series` (installations, capacity_kw, usable_capacity_kwh or
  stcs, the certificates created), `postcode` (as published), `month` (YYYY-MM), `measure` (the column as published,
  such as "SGU Rated Output In kW") and `value`, with the `dataset` (file) it came from.
- `battery_states`: the CER's historical voluntary count of battery installations by state and year, 2014 to
  2025 (the file's total over states is left out).

Each series is read from its CSV file only: every workbook sheet repeats a CSV exactly, so reading both counted every
value twice (ADR 0011). The files' total columns ("Historic Total ... (2001 - 2010)" and "Total ...") are left out:
they are sums of the monthly values (checked to the unit for solar, wind and water heaters), and keeping them beside
the months would invite adding a total to its parts.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from ..core import CorpusError, Ctx, http_get, raw_path, read_manifest

PAGE = "https://cer.gov.au/markets/reports-and-data/small-scale-installation-postcode-data"
MONTHS = {
    m: i for i, m in enumerate(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)
}
TECHNOLOGY = {  # file-name prefix -> technology
    "sgu-solar": "solar_pv",
    "sgu-wind": "wind",
    "sgu-hydro": "hydro",
    "sgu-battery": "battery",
    "swh-solar": "solar_water_heater",
    "swh-air-source": "heat_pump_water_heater",
    "sres-postcode-data-small-scale-technology-certificates": "battery",  # certificates for batteries, from July 2025
}
SERIES = {  # the measure in a monthly column -> series
    "installation quantity": "installations",
    "installations quantity": "installations",
    "sgu rated output in kw": "capacity_kw",
    "rated power output in kw": "capacity_kw",
    "usable capacity in kwh": "usable_capacity_kwh",
    "validated stcs": "stcs",
}
STATE_FILE = "historical-voluntary-state-data-battery-installation-small-scale-systems"


def _number(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s.astype(str).str.replace(",", "").str.strip(), errors="coerce")


def series_file(path: Path) -> pd.DataFrame:
    """One CSV series, long: a postcode column, then 'Mon YYYY - measure' columns (total columns are left out)."""
    name = path.stem
    tech = next((t for prefix, t in TECHNOLOGY.items() if name.startswith(prefix)), None)
    if tech is None:
        raise CorpusError(f"cer: {path.name} is not a known technology; add it to TECHNOLOGY")
    df = pd.read_csv(path, dtype=str, encoding="utf-8-sig")
    df.columns = [re.sub(r"\s+", " ", c).strip() for c in df.columns]  # some headers hold non-breaking spaces
    pc = df.columns[0]
    cols = {}
    for c in df.columns[1:]:
        m = re.fullmatch(r"([A-Z][a-z]{2}) (\d{4}) - (.+)", c)
        if m:
            cols[c] = (f"{m.group(2)}-{MONTHS[m.group(1)]:02d}", m.group(3).strip())
        elif not c.lower().startswith(("total", "historic total")):
            raise CorpusError(f"cer: {path.name} has an unexpected column '{c}'")
    long = df.melt(id_vars=[pc], value_vars=list(cols), var_name="column", value_name="value")
    long["month"] = long["column"].map(lambda c: cols[c][0])
    long["measure"] = long["column"].map(lambda c: cols[c][1])
    unknown = set(long["measure"].str.lower()) - set(SERIES)
    if unknown:
        raise CorpusError(f"cer: {path.name} has measures {sorted(unknown)}; add them to SERIES")
    long["series"] = long["measure"].str.lower().map(SERIES)
    long["value"] = _number(long["value"])
    long = long.dropna(subset=["value"]).rename(columns={pc: "postcode"})
    long["postcode"] = long["postcode"].str.strip()
    long.insert(0, "dataset", name)
    long.insert(1, "technology", tech)
    return long[["dataset", "technology", "series", "postcode", "month", "measure", "value"]]


def battery_states(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str, encoding="utf-8-sig")
    year = df.columns[0]
    long = df.melt(id_vars=[year], var_name="state", value_name="installations").rename(columns={year: "year"})
    long["installations"] = _number(long["installations"])
    long["year"] = pd.to_numeric(long["year"], errors="coerce").astype("Int64")
    long = long[long["state"].str.strip().str.lower() != "total"]  # the sum of the states, recomputable
    return long.dropna(subset=["year", "installations"]).reset_index(drop=True)


def _build(ctx: Ctx, files: list[Path]) -> None:
    csvs = sorted(f for f in files if f.suffix == ".csv")
    states = [f for f in csvs if f.stem == STATE_FILE]
    frames = [series_file(f) for f in csvs if f.stem != STATE_FILE]
    df = pd.concat(frames, ignore_index=True).sort_values(["technology", "series", "postcode", "month"])
    dupes = df.duplicated(["technology", "series", "postcode", "month"]).sum()
    if dupes:
        raise CorpusError(f"cer: {dupes} rows repeat a technology, series, postcode and month")
    ctx.table(df.reset_index(drop=True), "installations", describe="Small-scale installations by postcode and month")
    if states:
        ctx.table(battery_states(states[0]), "battery_states", describe="Battery installations by state and year")


def run(ctx: Ctx) -> None:
    docs = sorted(set(re.findall(r'href="(/document/[^"]+)"', http_get(PAGE).text)))
    if not docs:
        raise CorpusError("cer: no documents on the postcode data page")
    files = []
    for d in docs:
        name = d.rsplit("/", 1)[1]
        r = http_get("https://cer.gov.au" + d, timeout=300)
        is_xlsx = r.content[:2] == b"PK"  # some documents are Excel workbooks, which repeat the CSV files
        f = ctx.raw / f"{name}.{'xlsx' if is_xlsx else 'csv'}"
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(r.content)
        ctx.keep_raw(f, url="https://cer.gov.au" + d)
        files.append(f)
    _build(ctx, files)


def reprocess(ctx: Ctx, tables: list[str] | None = None) -> None:
    """The tables again from the raw files the manifest records (in the repo), fetching nothing."""
    files = read_manifest()["sources"]["cer"]["files"]
    _build(ctx, [raw_path("cer", k.split("/", 1)[1]) for k in files if k.startswith("raw/")])
