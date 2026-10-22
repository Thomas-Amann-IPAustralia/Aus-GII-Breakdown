"""Places: ASGS 2021 geography, SEIFA 2021 and Data by Region, to put IP users and businesses in context.

Raw: the ASGS allocation files (mesh block to every structure, postal areas and remoteness) and the 2021 Census mesh
block counts (R2); SEIFA and Data by Region from the ABS Data API (repo, gzipped, or R2 when large). Processed:

- `mesh_blocks`: every 2021 mesh block with its SA1 to SA4, GCCSA, state, postal area (POA), remoteness area, and
  usual resident persons and dwellings (2021 Census).
- `poa_sa2`: postal area to SA2, with each pair's share of the postal area's persons (for apportioning postcode data).
- `poa`: one row per postal area: persons, its main SA2, SA3, SA4 and state (most persons), and remoteness (most
  persons; and the share in major cities).
- `seifa_poa`, `seifa_sa2`: SEIFA 2021 indexes (scores, ranks, deciles), tidy.
- `region_asgs`, `region_remoteness`, `region_lga`: Data by Region 2011 to 2025 (population, economy and industry,
  income, education, health and more), tidy.

IPGOD and IPLORD give postcodes; map a postcode to a POA by its four digits (POA codes are postcodes, with a few
postcodes that have no POA, such as PO boxes; those cannot be placed).
"""

from __future__ import annotations

import pandas as pd

from ..core import Ctx
from ._abs import fetch_flow

ALLOC = (
    "https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs/"
    "edition-3-july-2021-june-2026/access-and-downloads/allocation-files/"
)
MB_COUNTS = (
    "https://www.abs.gov.au/census/guide-census-data/mesh-block-counts/2021/Mesh%20Block%20Counts%2C%202021.xlsx"
)
FLOWS = {
    "seifa_poa": ("ABS_SEIFA2021_POA", "repo"),
    "seifa_sa2": ("ABS_SEIFA2021_SA2", "repo"),
    "region_asgs": ("ABS_REGIONAL_ASGS2021", "r2"),
    "region_remoteness": ("ABS_REGIONAL_REMOTENESS_ASGS2021", "auto"),
    "region_lga": ("ABS_REGIONAL_LGA2021", "r2"),
}


def _xlsx(path, code_col: str) -> pd.DataFrame:
    """The first sheet of an ASGS allocation file whose header names `code_col`, as strings."""
    for _, df in pd.read_excel(path, sheet_name=None, engine="calamine", dtype=str, header=None).items():
        hits = [i for i in range(min(10, len(df))) if code_col in set(df.iloc[i].astype(str))]
        if hits:
            df.columns = df.iloc[hits[0]].astype(str)
            return df.iloc[hits[0] + 1 :].dropna(subset=[code_col])
    raise ValueError(f"no sheet names {code_col} in {path}")


def run(ctx: Ctx) -> None:
    mb = _xlsx(ctx.fetch(ALLOC + "MB_2021_AUST.xlsx", "MB_2021_AUST.xlsx", keep="r2"), "MB_CODE_2021")
    poa = _xlsx(ctx.fetch(ALLOC + "POA_2021_AUST.xlsx", "POA_2021_AUST.xlsx", keep="r2"), "MB_CODE_2021")
    ra = _xlsx(ctx.fetch(ALLOC + "RA_2021_AUST.xlsx", "RA_2021_AUST.xlsx", keep="r2"), "SA1_CODE_2021")
    counts_raw = pd.read_excel(
        ctx.fetch(MB_COUNTS, "mesh-block-counts-2021.xlsx", keep="r2"),
        sheet_name=None,
        engine="calamine",
        dtype=str,
        header=None,
    )
    counts = []
    for _, df in counts_raw.items():
        hit = [i for i in range(min(10, len(df))) if "MB_CODE_2021" in set(df.iloc[i].astype(str))]
        if hit:
            df.columns = df.iloc[hit[0]].astype(str)
            counts.append(df.iloc[hit[0] + 1 :][["MB_CODE_2021", "Dwelling", "Person"]])
    counts = pd.concat(counts).dropna(subset=["MB_CODE_2021"])
    keep = [
        "MB_CODE_2021",
        "MB_CATEGORY_2021",
        "SA1_CODE_2021",
        "SA2_CODE_2021",
        "SA2_NAME_2021",
        "SA3_CODE_2021",
        "SA3_NAME_2021",
        "SA4_CODE_2021",
        "SA4_NAME_2021",
        "GCCSA_CODE_2021",
        "GCCSA_NAME_2021",
        "STATE_CODE_2021",
        "STATE_NAME_2021",
        "AREA_ALBERS_SQKM",
    ]
    m = (
        mb[[c for c in keep if c in mb.columns]]
        .merge(poa[["MB_CODE_2021", "POA_CODE_2021"]], on="MB_CODE_2021", how="left")
        .merge(ra[["SA1_CODE_2021", "RA_CODE_2021", "RA_NAME_2021"]], on="SA1_CODE_2021", how="left")
    )
    m = m.merge(counts, on="MB_CODE_2021", how="left")
    m["persons"] = pd.to_numeric(m.pop("Person"), errors="coerce").fillna(0).astype(int)
    m["dwellings"] = pd.to_numeric(m.pop("Dwelling"), errors="coerce").fillna(0).astype(int)
    m.columns = [c.lower().removesuffix("_2021") for c in m.columns]
    ctx.table(m, "mesh_blocks", describe="2021 mesh blocks with every ASGS structure, POA, remoteness and counts")

    pairs = m.dropna(subset=["poa_code"]).groupby(["poa_code", "sa2_code", "sa2_name"], as_index=False)["persons"].sum()
    tot = pairs.groupby("poa_code")["persons"].transform("sum")
    pairs["share"] = (pairs["persons"] / tot.where(tot > 0)).fillna(
        1 / pairs.groupby("poa_code")["sa2_code"].transform("count")
    )
    ctx.table(pairs, "poa_sa2", describe="Postal area to SA2, with shares of persons")

    def main_of(col_code: str, col_name: str | None = None) -> pd.DataFrame:
        cols = [col_code] + ([col_name] if col_name else [])
        g = m.dropna(subset=["poa_code"]).groupby(["poa_code"] + cols, as_index=False)["persons"].sum()
        g = g.sort_values(["poa_code", "persons"], ascending=[True, False]).drop_duplicates("poa_code")
        return g[["poa_code"] + cols]

    p = m.dropna(subset=["poa_code"]).groupby("poa_code", as_index=False).agg(persons=("persons", "sum"))
    for code, name in (
        ("sa2_code", "sa2_name"),
        ("sa3_code", "sa3_name"),
        ("sa4_code", "sa4_name"),
        ("state_code", "state_name"),
        ("ra_code", "ra_name"),
    ):
        p = p.merge(main_of(code, name), on="poa_code", how="left")
    major = m[m.ra_name.str.startswith("Major Cities", na=False)].groupby("poa_code")["persons"].sum()
    p["share_major_cities"] = (major.reindex(p.poa_code).fillna(0).values / p.persons.where(p.persons > 0)).round(4)
    ctx.table(p, "poa", describe="One row per postal area: persons, main SA2 to state, remoteness")

    for name, (flow, keep_raw) in FLOWS.items():
        df = fetch_flow(ctx, flow, keep="r2" if keep_raw == "r2" else "repo")
        ctx.table(df, name, describe=flow)
