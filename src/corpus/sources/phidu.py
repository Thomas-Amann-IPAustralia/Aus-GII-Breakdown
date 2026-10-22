"""PHIDU Social Health Atlas of Australia, by Population Health Area (optional; replaces the NATSEM estimates).

Modelled small-area estimates of health and wellbeing (such as psychological distress and self-assessed health) and
social indicators, beside regional IP use (context, not effect; section 2 of docs/data-plan.md). CC BY-NC-SA 3.0 AU
(non-commercial use only). The site's pages answer this environment but its files do not, so the workbook is put in
data/raw/phidu/ by hand and read with `corpus run phidu`: from https://phidu.torrens.edu.au/social-health-atlases/data,
'Social Health Atlas of Australia: Population Health Areas', the Australia workbook (phidu_data_pha_aust.xlsx).
Population Health Areas are SA2s or groups of SA2s; PHIDU publishes the concordance.

Processed: one table per file and sheet, all columns as text; see `_manual.read_dropped`.
"""

from __future__ import annotations

from ..core import Ctx
from ._manual import read_dropped

HOW = (
    "From https://phidu.torrens.edu.au/social-health-atlases/data, 'Social Health Atlas of Australia: Population "
    "Health Areas', the Australia workbook (phidu_data_pha_aust.xlsx)."
)


def run(ctx: Ctx) -> None:
    read_dropped(ctx, HOW)
