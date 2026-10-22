"""Classification concordances: patents and trade marks to technologies, industries and green technologies.

Raw (repo): `ipc-technology-35.csv`, WIPO's 35 technology fields (Schmoch 2008) as IP Australia reproduces them in
the IPLORD 2020 dictionary (Annex A), transcribed here, with G01B to G01M restored to Measurement as in WIPO's
table;
the ALP crosswalks (Lybbert and Zolas, version 2209 for IPC excluding services, and the Nice crosswalk version 2305);
the ABS correspondence ISIC Rev. 4 to ANZSIC 2006; and the WIPO IPC Green Inventory, taken from the tree embedded in
its web app. Processed:

- `ipc_technology`: the 35 fields' IPC rules (prefix; groups it is limited to; groups or subclass it excludes; and
  `unless_also`, a subclass whose presence on the same patent moves it out of the field, as in WIPO's method).
- `patent_fields`: each IPGOD patent application's technology fields, from its current IPC marks, with `weight`
  (1/n over its n distinct fields, so each application sums to 1).
- `alp_ipc4_isic4`, `alp_nice_isic4`: the probability-weighted links from IPC subclass, and from Nice class, to ISIC
  Rev. 4 four-digit classes.
- `isic4_anzsic`: ISIC Rev. 4 class to ANZSIC 2006 class (`partial` where the ABS marks the link as partial).
- `ipc4_anzsic`, `nice_anzsic`: the ALP weights carried through to ANZSIC 2006 classes (a weight split equally where
  one ISIC class maps to several ANZSIC classes), with the ANZSIC division.
- `ipc_green_inventory`: the Green Inventory's topics, each with its IPC references, one row per reference.
"""

from __future__ import annotations

import json
import re

import duckdb
import pandas as pd

from ..core import CorpusError, Ctx, http_get, path, unzip_member, unzip_names

ALP_IPC = "https://drive.google.com/uc?export=download&id=1wsIflv45zCyLNvB1mcSWGS6vhfNC_qxv"
ALP_NICE = "https://drive.google.com/uc?export=download&id=1P1NQ4tfggVOu_CtLxTXCKTr9yzoyeniP"
ISIC_ANZSIC = (
    "https://www.abs.gov.au/statistics/classifications/australian-and-new-zealand-standard-industrial-classification-"
    "anzsic/2006-revision-2-0/correspondences/isic-rev-4-anzsic-2006"
)
GREEN = "https://www.wipo.int/classifications/ipc/green-inventory/"


def _groups(spec: str) -> list[int]:
    out = []
    for part in str(spec).split(";"):
        if "-" in part:
            a, b = part.split("-")
            out += list(range(int(a), int(b) + 1))
        elif part.strip():
            out.append(int(part))
    return out


def _green_tree(js: str) -> list:
    start = js.find('[{"expanded"')
    if start < 0:
        raise CorpusError("concordances: the Green Inventory tree is no longer in the app's script")
    depth, i, in_str, esc = 0, start, False, False
    while True:
        c = js[i]
        if in_str:
            esc = (c == "\\") and not esc
            if c == '"' and not esc:
                in_str = False
        elif c == '"':
            in_str = True
        elif c in "[{":
            depth += 1
        elif c in "]}":
            depth -= 1
            if depth == 0:
                break
        i += 1
    text = js[start : i + 1]
    text = re.sub(r"\\x([0-9a-fA-F]{2})", r"\\u00\1", text).replace("\\'", "'")
    return json.loads(text)


def _green_rows(nodes: list, trail: list[str]) -> list[dict]:
    rows = []
    for n in nodes:
        here = trail + [n.get("title", "").strip()]
        ipc = (n.get("data") or {}).get("IPC")
        if ipc:
            for ref in _ipc_refs(ipc):
                rows.append(
                    {"level": len(here), "topic": " > ".join(here), "title": here[-1], "ipc_raw": ipc, "ipc": ref}
                )
        rows += _green_rows(n.get("children") or [], here)
    return rows


def _ipc_refs(s: str) -> list[str]:
    """'F03D 1/04, 9/00, 13/20. F03G 6/00' -> ['F03D 1/04', 'F03D 9/00', 'F03D 13/20', 'F03G 6/00']."""
    out = []
    for chunk in re.split(r"\.\s+|\.$|;\s*", s.strip()):
        chunk = chunk.strip().rstrip(".")
        m = re.match(r"([A-H]\d\d[A-Z])\s*(.*)", chunk)
        if not m:
            continue
        sub, rest = m.groups()
        if not rest.strip():
            out.append(sub)
            continue
        for g in re.split(r",\s*", rest):
            g = g.strip()
            if g:
                out.append(f"{sub} {g}")
    return out


def run(ctx: Ctx) -> None:
    tech = pd.read_csv(ctx.raw / "ipc-technology-35.csv", dtype=str)
    ctx.keep_raw(ctx.raw / "ipc-technology-35.csv")
    ctx.table(tech, "ipc_technology", describe="WIPO's 35 technology fields, IPC rules")

    # Each patent's fields, from its current IPC marks
    rules = []
    for r in tech.itertuples():
        inc = _groups(r.groups) if isinstance(r.groups, str) else None
        exc = _groups(r.except_groups) if isinstance(r.except_groups, str) else []
        rules.append(
            (
                int(r.field_no),
                r.ipc_prefix,
                inc,
                exc,
                r.except_prefix if isinstance(r.except_prefix, str) else None,
                r.unless_also if isinstance(r.unless_also, str) else None,
            )
        )
    con = duckdb.connect()
    cls = path("ipgod", "patent_classification")
    marks = con.execute(f"""
        SELECT DISTINCT application_number, upper(replace(left(classification, 4), ' ', '')) AS subclass,
               try_cast(regexp_extract(classification, '^\\S+\\s*(\\d+)/', 1) AS INTEGER) AS grp
        FROM '{cls}' WHERE classification_system = 'ipc_mark' AND is_current""").df()
    subs = marks.groupby("application_number")["subclass"].agg(set)
    hits = []
    for field, prefix, inc, exc, exc_prefix, unless in rules:
        m = marks[marks.subclass.str.startswith(prefix)]
        if exc_prefix:
            m = m[~m.subclass.str.startswith(exc_prefix)]
        if inc is not None:
            m = m[m.grp.isin(inc)]
        if exc:
            m = m[~m.grp.isin(exc)]
        apps = m.application_number.unique()
        if unless:
            apps = [a for a in apps if not any(s.startswith(unless) for s in subs[a])]
        hits.append(pd.DataFrame({"application_number": apps, "field_no": field}))
    pf = pd.concat(hits).drop_duplicates()
    pf["weight"] = 1 / pf.groupby("application_number")["field_no"].transform("count")
    names = tech.drop_duplicates("field_no").assign(field_no=lambda d: d.field_no.astype(int))
    pf = pf.merge(names[["field_no", "field", "sector"]], on="field_no").sort_values(["application_number", "field_no"])
    ctx.table(pf, "patent_fields", describe="IPGOD patents to WIPO technology fields, weighted")

    # ALP crosswalks
    zi = ctx.fetch(ALP_IPC, "alp-ipc-excl-service-v2209.zip", keep="repo")
    zn = ctx.fetch(ALP_NICE, "alp-trademark-v2305.zip", keep="repo")
    work = ctx.cache / "work"
    member = next((m for m in unzip_names(zi) if m.endswith("ipc4_to_isic_rev4_4_excl_service.txt")), None)
    nmember = next((m for m in unzip_names(zn) if re.search(r"nice_to_ISIC_Rev4_4\.txt$", m)), None)
    if not member or not nmember:
        raise CorpusError("concordances: the ALP zips no longer hold the IPC4 or Nice to ISIC Rev. 4 files")
    alp = pd.read_csv(unzip_member(zi, member, work), dtype={"ipc4": str, "isic_rev4_4": str})
    alp.columns = ["ipc4", "isic4", "weight"]
    nice = pd.read_csv(unzip_member(zn, nmember, work), dtype=str)
    nice.columns = ["nice", "isic4", "weight"]
    nice["weight"] = nice["weight"].astype(float)
    ctx.table(alp, "alp_ipc4_isic4", describe="ALP: IPC subclass to ISIC Rev. 4 class, probability weights")
    ctx.table(nice, "alp_nice_isic4", describe="ALP: Nice class to ISIC Rev. 4 class, probability weights")

    # ISIC Rev. 4 to ANZSIC 2006
    html = http_get(ISIC_ANZSIC).text
    ctx.raw_text("isic-rev-4-anzsic-2006.html", html)
    from io import StringIO

    t = pd.concat(pd.read_html(StringIO(html)), ignore_index=True)
    t.columns = ["isic_top", "isic_class", "isic_title", "anzsic", "anzsic_title"]
    t["isic4"] = t["isic_class"].where(t["isic_class"].astype(str).str.fullmatch(r"\d{4}")).ffill()
    t = t.dropna(subset=["anzsic"])
    t["partial"] = t["anzsic"].astype(str).str.endswith("p")
    t["anzsic"] = t["anzsic"].astype(str).str.rstrip("p")
    t = t[t["anzsic"].str.fullmatch(r"\d{4}")]
    ia = t[["isic4", "anzsic", "anzsic_title", "partial"]].drop_duplicates().reset_index(drop=True)
    ctx.table(ia, "isic4_anzsic", describe="ISIC Rev. 4 class to ANZSIC 2006 class (ABS)")

    split = ia.assign(share=1 / ia.groupby("isic4")["anzsic"].transform("count"))
    for name, df, key in (("ipc4_anzsic", alp, "ipc4"), ("nice_anzsic", nice, "nice")):
        x = df.merge(split, on="isic4", how="left")
        x["weight"] = x["weight"] * x["share"].fillna(1)
        x = x.groupby([key, "anzsic", "anzsic_title"], dropna=False, as_index=False)["weight"].sum()
        unmatched = df[~df.isic4.isin(ia.isic4)]["weight"].sum() / df["weight"].sum()
        if unmatched > 0:
            ctx.note(f"concordances: {name}: {unmatched:.1%} of ALP weight is on ISIC classes the ABS table lacks")
        ctx.table(x, name, describe=f"{key} to ANZSIC 2006 class, ALP weights carried through ISIC Rev. 4")

    # IPC Green Inventory
    page = http_get(GREEN + "home").text
    js_name = re.search(r'src="[^"]*?(main\.[0-9a-f]+\.js)"', page)
    if not js_name:
        raise CorpusError("concordances: the Green Inventory page no longer names its main script")
    js = http_get(GREEN + js_name.group(1)).text
    rows = _green_rows(_green_tree(js), [])
    ctx.raw_text("ipc-green-inventory.json", json.dumps(_green_tree(js), ensure_ascii=False, indent=1))
    ctx.table(pd.DataFrame(rows), "ipc_green_inventory", describe="WIPO IPC Green Inventory topics and IPC references")
