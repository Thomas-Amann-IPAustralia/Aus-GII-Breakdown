"""ABN Bulk Extract: every ABN, current and cancelled, from the Australian Business Register's weekly public extract.

Raw: the two zips (R2), the schema and readme (repo). Processed: `abns`, one row per ABN (R2): status and the date it
took effect, entity type, the main name for non-individuals, state and postcode of the main business location, ACN,
GST status and date, and whether it is a deductible gift recipient. Individuals' (sole traders') names are not kept:
the ABN is the link key, and the corpus does not need personal names. Linked subsets come from `linkage`.

From these: firm age (`abn_status_from` of the first activation is not published, so age is measured from the earliest
of ABN status date, GST date and ASIC registration; see docs/catalogue.md), survival (`abn_status` = CAN and its date),
entity type, and GST registration as a rough marker of turnover of $75,000 or more.
"""

from __future__ import annotations

import subprocess
import xml.etree.ElementTree as ET
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from ..core import CorpusError, Ctx, http_get, unzip_names

PACKAGE = "https://data.gov.au/data/api/3/action/package_show?id=abn-bulk-extract"
FIELDS = [
    "abn",
    "abn_status",
    "abn_status_from",
    "record_last_updated",
    "replaced",
    "entity_type",
    "entity_type_text",
    "name",
    "state",
    "postcode",
    "acn",
    "gst_status",
    "gst_status_from",
    "dgr",
    "other_name_count",
]


def _date(s: str | None) -> str | None:
    if not s or s == "19000101" or len(s) != 8:
        return None
    return f"{s[:4]}-{s[4:6]}-{s[6:]}"


def _record(line: str) -> dict | None:
    e = ET.fromstring(line)
    abn = e.find("ABN")
    if abn is None:
        return None
    et = e.find("EntityType")
    main = e.find("MainEntity")
    ind = e.find("LegalEntity")
    holder = main if main is not None else ind
    addr = holder.find("BusinessAddress/AddressDetails") if holder is not None else None
    name = main.findtext("NonIndividualName/NonIndividualNameText") if main is not None else None
    asic = e.find("ASICNumber")
    gst = e.find("GST")
    return {
        "abn": abn.text,
        "abn_status": abn.get("status"),
        "abn_status_from": _date(abn.get("ABNStatusFromDate")),
        "record_last_updated": _date(e.get("recordLastUpdatedDate")),
        "replaced": e.get("replaced") == "Y",
        "entity_type": et.findtext("EntityTypeInd") if et is not None else None,
        "entity_type_text": et.findtext("EntityTypeText") if et is not None else None,
        "name": name,
        "state": addr.findtext("State") if addr is not None else None,
        "postcode": addr.findtext("Postcode") if addr is not None else None,
        "acn": asic.text if asic is not None and asic.text else None,
        "gst_status": gst.get("status") if gst is not None else None,
        "gst_status_from": _date(gst.get("GSTStatusFromDate")) if gst is not None else None,
        "dgr": e.find("DGR") is not None,
        "other_name_count": len(e.findall("OtherEntity")),
    }


SCHEMA = pa.schema(
    [
        ("abn", pa.string()),
        ("abn_status", pa.string()),
        ("abn_status_from", pa.date32()),
        ("record_last_updated", pa.date32()),
        ("replaced", pa.bool_()),
        ("entity_type", pa.string()),
        ("entity_type_text", pa.string()),
        ("name", pa.string()),
        ("state", pa.string()),
        ("postcode", pa.string()),
        ("acn", pa.string()),
        ("gst_status", pa.string()),
        ("gst_status_from", pa.date32()),
        ("dgr", pa.bool_()),
        ("other_name_count", pa.int16()),
    ]
)


def _batch(rows: list[dict]) -> pa.RecordBatch:
    cols = {f: [r[f] for r in rows] for f in FIELDS}
    for f in ("abn_status_from", "record_last_updated", "gst_status_from"):
        cols[f] = pa.array(cols[f], pa.string()).cast(pa.date32())
    return pa.RecordBatch.from_pydict(cols, schema=SCHEMA)


def _member(args: tuple[str, str, str]) -> tuple[str, int, int]:
    """Parse one XML member of a zip into a Parquet file; returns (path, rows, unparsed lines)."""
    zpath, member, out = args
    proc = subprocess.Popen(["unzip", "-p", zpath, member], stdout=subprocess.PIPE, text=True, encoding="utf-8")
    writer = pq.ParquetWriter(out, SCHEMA, compression="zstd")
    rows, bad, buf = 0, 0, []
    for line in proc.stdout:
        line = line.strip()
        if not line.startswith("<ABR "):
            continue
        try:
            r = _record(line)
        except ET.ParseError:
            bad += 1
            continue
        if r:
            buf.append(r)
        if len(buf) >= 200_000:
            writer.write_batch(_batch(buf))
            rows += len(buf)
            buf = []
    if buf:
        writer.write_batch(_batch(buf))
        rows += len(buf)
    writer.close()
    if proc.wait() != 0:
        raise CorpusError(f"abr: unzip failed on {member}")
    return out, rows, bad


def run(ctx: Ctx) -> None:
    res = http_get(PACKAGE).json()["result"]["resources"]
    zips = [r for r in res if r.get("format", "").upper() == "ZIP"]
    if len(zips) < 2:
        raise CorpusError(f"abr: expected two ZIP parts on data.gov.au, found {len(zips)}")
    for r in res:
        fname = r["url"].rsplit("/", 1)[1]
        if fname.endswith((".xsd", ".pdf")):
            ctx.fetch(r["url"], fname, keep="repo")
    parts = []
    for r in zips:
        z = ctx.fetch(r["url"], r["url"].rsplit("/", 1)[1], keep="r2")
        parts += [(str(z), m) for m in unzip_names(z) if m.endswith(".xml")]
    tmp = ctx.cache / "parts"
    tmp.mkdir(parents=True, exist_ok=True)
    jobs = [(z, m, str(tmp / (Path(m).stem + ".parquet"))) for z, m in parts]
    total, bad = 0, 0
    with ProcessPoolExecutor(max_workers=4) as ex:
        for out, rows, b in ex.map(_member, jobs):
            total += rows
            bad += b
            ctx.log(f"{Path(out).name}: {rows:,} records")
    if bad:
        ctx.note(f"abr: {bad} records could not be parsed and were left out")
    import duckdb

    out = ctx.cache / "processed/abns.parquet"
    out.parent.mkdir(parents=True, exist_ok=True)
    duckdb.connect().execute(
        f"COPY (SELECT * FROM '{tmp}/*.parquet' ORDER BY abn) TO '{out}' (FORMAT parquet, COMPRESSION zstd, "
        "COMPRESSION_LEVEL 9)"
    )
    ctx.keep_table(out, "abns", total, FIELDS, keep="r2", describe="One row per ABN; no individuals' names")
    for f in tmp.glob("*.parquet"):
        f.unlink()
