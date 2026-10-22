"""OECD comparator panel: R&D, patents, protection methods, business demography, venture capital, IP tax regimes and
How's Life? well-being, from the OECD Data Explorer's SDMX API, for every country the OECD publishes.

Raw: each flow's CSV with labels (gzipped; repo when small, R2 when large). Processed: one tidy table per flow (named
below), with a code and a `_label` column for every dimension, then `value`. The flows are the OECD's own; check each
table's `_label` columns for units and breakdowns before comparing.
"""

from __future__ import annotations

import gzip

from ..core import REPO_LIMIT, CorpusError, Ctx, http_get
from ._abs import tidy_file

API = "https://sdmx.oecd.org/public/rest/data"
FLOWS = {
    "msti": "OECD.STI.STP,DSD_MSTI@DF_MSTI",  # Main Science and Technology Indicators
    "innovation_ip_methods": "OECD.STI.STP,DSD_INNOSTAT@DF_INNOIP",  # methods used to protect IP
    "patents_wipo_fields": "OECD.STI.PIE,DSD_PATENTS@DF_PATENTS_WIPO",
    "patents_environment": "OECD.STI.PIE,DSD_PATENTS@DF_PATENTS_ENVIROMENT",
    "patents_foreign_ownership": "OECD.STI.PIE,DSD_PATENTS@DF_PATENTS_FOREIGN",
    "patents_domestic_ownership_abroad": "OECD.STI.PIE,DSD_PATENTS@DF_PATENTS_DOMESTIC",
    "patents_coinventors": "OECD.STI.PIE,DSD_PATENTS@DF_PATENTS_COINVENTOR",
    "patents_regions": "OECD.CFE.EDS,DSD_REG_INNOV@DF_PAT",
    "business_births_deaths": "OECD.SDD.TPS,DSD_SDBSBD_ISIC4@DF_BD_EMP_B_D",
    "business_high_growth": "OECD.SDD.TPS,DSD_SDBSBD_ISIC4@DF_BD_EMP_HG",
    "business_survival": "OECD.SDD.TPS,DSD_SDBSBD_ISIC4@DF_BD_EMP_S",
    "venture_capital": "OECD.SDD.TPS,DSD_VC@DF_VC_INV",
    "ip_tax_regimes": "OECD.CTP.TPS,DSD_QDD_IPR@DF_QDD_IPR",
    "wellbeing_current": "OECD.WISE.WDP,DSD_HSL@DF_HSL_CWB",
    "wellbeing_by_sex": "OECD.WISE.WDP,DSD_HSL@DF_HSL_CWB_SEX",
    "wellbeing_inequality": "OECD.WISE.WDP,DSD_HSL@DF_HSL_CWB_INEQ",
    "wellbeing_future": "OECD.WISE.WDP,DSD_HSL@DF_HSL_FWB",
}


def run(ctx: Ctx) -> None:
    failed = []
    for name, flow in FLOWS.items():
        url = f"{API}/{flow}/all"
        try:
            r = http_get(
                url,
                params={"dimensionAtObservation": "AllDimensions"},
                headers={"Accept": "application/vnd.sdmx.data+csv;labels=both"},
                timeout=900,
            )
        except CorpusError as e:
            failed.append(name)
            ctx.note(f"oecd: {name} ({flow}) could not be fetched: {e}")
            continue
        gz = ctx.cache / f"{name}.csv.gz"
        gz.parent.mkdir(parents=True, exist_ok=True)
        with open(gz, "wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", mtime=0, filename="") as f:
            f.write(r.content)
        if gz.stat().st_size <= REPO_LIMIT:
            ctx.raw.mkdir(parents=True, exist_ok=True)
            gz = gz.replace(ctx.raw / gz.name)
            ctx.keep_raw(gz, url=url)
        else:
            ctx.keep_raw(gz, keep="r2", url=url)
        out = ctx.cache / "processed" / f"{name}.parquet"
        out.parent.mkdir(parents=True, exist_ok=True)
        rows, cols = tidy_file(gz, out, flow)
        ctx.keep_table(out, name, rows, cols, describe=flow)
    if len(failed) == len(FLOWS):
        raise CorpusError("oecd: no flow could be fetched")
