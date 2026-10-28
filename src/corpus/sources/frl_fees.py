"""The history of IP Australia's official fees, from every version of the fee regulations on the Federal Register of
Legislation: the Patents Regulations 1991 (Schedule 7), the Trade Marks Regulations under the 1955 Act (Schedule 2)
and the Trade Marks Regulations 1995 (Schedule 9), the Designs Regulations 1982 (Schedule 2) and 2004 (Schedule 4),
and the Plant Breeder's Rights Regulations 1994 (the Schedule). ADR 0031.

Read from the Register's public API (https://api.prod.legislation.gov.au/v1): each title's versions (start and end
dates, the amending instruments behind each), and each compilation's text as EPUB (XHTML). The Register holds no text
for some versions, mostly before 1999 (it holds the regulations as made and compilations from 1999 on); for those, the
key fees come from the amending instruments, read by hand into `gaps.yaml` (repo) and, where an instrument replaces a
whole fee schedule, from its tables by the same rules as a compilation. The current fees (`ipa_fees`) are IP
Australia's own list; a test checks the latest version here against it.

Raw: `versions.json` (every version of each title, repo), `gaps.yaml` (repo, compiled here) and the EPUBs, one zip
per title and one of the amending instruments (R2). Processed:
- `versions`: one row per version of each title: start, end, the compilation's register id, whether the Register
  holds its text, and the instruments that made it.
- `schedule_rows`: every row of the fee schedule of every compilation with text, as published: item, the matter
  (with the item's words before each paragraph), the fee as written and `amount_aud` (its first dollar amount).
- `key_fees`: the fees that matter for the questions, one row per fee and spell at one amount: right, fee,
  anniversary (patent renewals), start and end (exclusive), `amount_aud`, the version or instrument that set it, and
  `basis` (`compilation` or `amendment`). Each is the base fee for one right, one class or one design, paid the
  cheapest way the schedule offers ("preferred", "approved" or electronic means, the goods and services pick list),
  without surcharges for extra claims, pages, classes or late payment.
- `fee_changes`: one row per right and date on which any key fee changed, listing the changes.
"""

from __future__ import annotations

import io
import json
import re
import zipfile

import pandas as pd
import yaml

from ..core import CorpusError, Ctx, http_get

API = "https://api.prod.legislation.gov.au/v1"

# Each title: its right, its name, its fee schedule's number, when it began to apply (its Act's commencement, which
# the Register's first version can precede: regulations are made before they start), when it was superseded, and
# whether its compilations are read (the 1955 Act's regulations are read from their 1989 fee schedule on, in
# gaps.yaml: the brief needs fees from 1990, and the Register holds only their 1958 text).
TITLES = {
    "F1996B02697": dict(right="patent", name="Patents Regulations 1991", schedule="7", start="1991-04-30"),
    "C1958L00048": dict(
        right="trade_mark",
        name="Trade Marks Regulations (Trade Marks Act 1955)",
        schedule="2",
        start="1989-07-01",
        until="1996-01-01",
        compilations=False,
    ),
    "F1996B00084": dict(right="trade_mark", name="Trade Marks Regulations 1995", schedule="9", start="1996-01-01"),
    "F1996B00970": dict(
        right="design", name="Designs Regulations 1982", schedule="2", start="1982-03-11", until="2004-06-17"
    ),
    "F2004B00136": dict(right="design", name="Designs Regulations 2004", schedule="4", start="2004-06-17"),
    "F1996B02512": dict(right="pbr", name="Plant Breeder's Rights Regulations 1994", schedule="1?", start="1994-11-10"),
}


# Reading a schedule ----------------------------------------------------------------------------------------------

ROMAN = re.compile(r"^\((?:i|ii|iii|iv|v|vi|vii|viii|ix|x|xi|xii|xiii|xiv|xv|xvi|xvii|xviii|xix|xx)\)\s")
ALPHA = re.compile(r"^\([a-z]{1,2}\)\s")
HEADER = re.compile(r"^(item( no\.?)?|column \d.*|matter|fees?|amount.*|\$|fee \(\$\)|act, service.*)$", re.I)


def _clean(x: str) -> str:
    return re.sub(r"[ \t\r\f\v\xa0]+", " ", x).strip()


def money(s: str) -> float | None:
    """The first dollar amount in a cell ("$1 000 less ..." is 1000), or a bare number (old schedules)."""
    m = re.search(r"\$\s?(\d{1,3}(?:[,   ]\d{3})+(?!\d)|\d+)(\.\d+)?", s) or re.fullmatch(
        r"\s*(\d{1,3}(?:[, ]\d{3})+|\d+)(\.\d+)?\s*", s
    )
    return float(re.sub(r"\D", "", m.group(1)) + (m.group(2) or "")) if m else None


def _paras(el) -> list[str]:
    """A table cell's text as paragraphs: its <p>s, split again where a blank line (<br><br>) separates runs."""
    for br in el.iter("br"):
        br.tail = "\n" + (br.tail or "")
    out = []
    for p in el.findall(".//p") or [el]:
        for chunk in re.split(r"\n\s*\n", p.text_content()):
            if c := _clean(chunk.replace("\n", " ")):
                out.append(c)
    return out


def blocks(epub: bytes) -> list[tuple[str, object]]:
    """Paragraphs ('p', text) and table rows ('tr', [cell paragraphs]) in document order, over the EPUB's parts."""
    from lxml import html

    z = zipfile.ZipFile(io.BytesIO(epub))
    names = sorted(
        (n for n in z.namelist() if n.endswith(".html")),
        key=lambda n: [int(x) if x.isdigit() else x for x in re.split(r"(\d+)", n)],
    )
    out = []
    for n in names:
        root = html.fromstring(z.read(n))
        for el in root.iter("p", "tr", "h1", "h2", "h3", "h4"):
            if el.tag == "tr":
                out.append(("tr", [_paras(c) for c in el if c.tag in ("td", "th")]))
            elif not any(a.tag in ("td", "th") for a in el.iterancestors()):
                out.append(("p", _clean(el.text_content())))
    return out


def section(blks: list, num: str) -> list:
    """The fee schedule: blocks from its heading to the next schedule's or the notes (the longest such run, so that
    a contents page is skipped). `num` is a regex for the schedule's number ('1?' also matches an unnumbered one)."""
    head = re.compile(rf"^SCHEDULE\s*{num}(?![\dA-Z])", re.I)
    other = re.compile(r"^SCHEDULE\b", re.I)
    segs, cur = [], None
    for k, v in blks:
        if k == "p" and other.match(v) and not re.search(r"continued|has effect|applies|to the ", v, re.I):
            if cur is not None:
                segs.append(cur)
            cur = [] if head.match(v) else None
            continue
        if k == "p" and re.match(r"^(Notes to the|Endnotes?\b|NOTES?$)", v):
            if cur is not None:
                segs.append(cur)
            cur = None
        if cur is not None:
            cur.append((k, v))
    if cur is not None:
        segs.append(cur)
    return max(segs, key=lambda s: sum(k == "tr" for k, _ in s), default=[])


def flatten(blks: list) -> list[dict]:
    """A schedule's rows, one per fee: the item, the matter with the item's words and the paragraph labels above it
    ("Filing a request ...: / (a) by preferred means"), the fee as written and its amount. A cell holding several
    paragraphs (sub-items and their fees in one row) is split and the fees matched to the last paragraphs."""
    rows, item, itemtext, a, r_, part = [], None, "", "", "", ""

    def emit(line: str, fee: str) -> None:
        nonlocal a, r_
        if line:
            # "(i)" after "(h)" is the next letter, unless "(h)" ends with a colon (it heads numbered paragraphs) and
            # none of them has come yet
            sibling = line[:3] in ("(i)", "(v)", "(x)") and a[:3] in ("(h)", "(u)", "(w)")
            sibling = sibling and (not a.endswith(":") or bool(r_))
            if ROMAN.match(line) and not sibling:
                r_ = line
            elif ALPHA.match(line):
                a, r_ = line, ""
            else:
                r_ = line
        ctx = " / ".join(x for x in (itemtext, a, r_) if x) if (a or r_) else itemtext
        if fee and money(fee) is not None:
            rows.append({"part": part, "item": item, "matter": ctx, "fee_text": fee, "amount_aud": money(fee)})

    for k, v in blks:
        if k == "p":
            if re.match(r"^PART\b|^Part\s+\d", v):
                part = v
            continue
        while len(v) > 3 and not v[-1]:
            v = v[:-1]
        cells = [" ".join(c) for c in v]
        unlabelled = [re.sub(r"^Column \d\s*", "", c, flags=re.I) for c in cells]
        if len(v) < 2 or all(not c or HEADER.match(c) for c in unlabelled):
            continue
        first = cells[0]
        mp = [p for c in v[1:-1] for p in c] if len(v) > 2 else []
        fp = v[-1]
        if re.fullmatch(r"\d{1,3}[A-Z]{0,2}\.?", first):
            item, a, r_ = first.rstrip("."), "", ""
            if len(fp) > 1 and len(mp) >= len(fp):
                itemtext = " ".join(mp[: len(mp) - len(fp)]) or mp[0]
                for m, f in zip(mp[len(mp) - len(fp) :], fp, strict=True):
                    emit(m, f)
            else:
                itemtext = " ".join(mp)
                emit("", " ".join(fp))
        else:
            if not mp and first and not re.fullmatch(r"\d", first):
                mp = v[0]
            if len(fp) > 1 and len(mp) == len(fp):
                for m, f in zip(mp, fp, strict=True):
                    emit(m, f)
            else:
                emit(" ".join(mp), " ".join(fp))
    return rows


# The key fees ----------------------------------------------------------------------------------------------------

WORDS = {
    w: i
    for i, w in enumerate(
        "first second third fourth fifth sixth seventh eighth ninth tenth eleventh twelfth thirteenth fourteenth "
        "fifteenth sixteenth seventeenth eighteenth nineteenth twentieth".split(),
        1,
    )
}


def anniversary(matter: str) -> int | None:
    """The anniversary a renewal row is for: the last one named ("the fifth anniversary", "the 11th anniversary")."""
    m = re.findall(
        r"\b(?:the\s+)?(\d{1,2})(?:st|nd|rd|th)\s+anniversary|\bthe\s+(" + "|".join(WORDS) + r")\s+anniversary",
        matter,
        re.I,
    )
    ns = [int(a) if a else WORDS[b.lower()] for a, b in m]
    return ns[-1] if ns else None


CHEAPER = re.compile(
    r"(?:by|paid by|through) (?:an? )?(?:preferred|approved|electronic) means|by an electronic means approved|"
    r"electronically|online",
    re.I,
)
EXTRA = re.compile(
    r"exceed|in excess|more than (?:10|20|30|50)|additional (?:sheet|claim|page)"
    r"|for each (?:sheet|claim|page|additional)|late|within 6 months after|after the anniversary|after the expiry"
    r"|extension of time|in addition|surcharge"
    r"|^plus|\bplus:|amino acid|nucleotide|sequence",
    re.I,
)
# A base fee's own wording can name the surcharge it is without ("if the specification does not contain more than 20
# claims", "if at no time ... were there more than 20 potential claims")
BASE = re.compile(r"not contain more than|at no time|not more than", re.I)
# (right, fee, the matter's pattern, a pattern it must not match). Renewal rows of patents are split by anniversary.
RULES = [
    ("patent", "provisional_filing", r"request for a patent accompanied by a provisional specification", None),
    ("patent", "standard_filing", r"request for a standard patent accompanied by a complete specification", None),
    ("patent", "petty_filing", r"request for a petty patent accompanied by a complete specification", None),
    ("patent", "innovation_filing", r"request for an innovation patent accompanied by a complete specification", None),
    (
        "patent",
        "standard_examination",
        r"^(?:On )?filing a request for (?:an )?examination",
        r"PCT application if|international preliminary|modified|innovation|re-?examination|direct an applicant|101A"
        r"|section 48|(?<!not )preceded by a direction",
    ),
    ("patent", "innovation_examination", r"101A ?\(b\)[^/]*by the patentee", None),
    ("patent", "acceptance", r"^Acceptance of a patent request|^On acceptance|for acceptance", None),
    ("patent", "sealing", r"sealing a standard patent|For sealing a patent", r"duplicate"),
    (
        "patent",
        "standard_renewal",
        r"^(?:Continuation fee|Renewal fee)[^/]*(?:142|143 ?\(a\))|^Renewal fee for the purposes of paragraph /",
        r"143A",
    ),
    ("patent", "innovation_renewal", r"^Renewal fee[^/]*143A", None),
    (
        "trade_mark",
        "filing",
        r"^Filing an application to register a trade mark under|^On lodging[^/]*an application to register a trade mark"
        r"|^On lodging: / \(a\) (?:on a day, )?an application to register a trade mark",
        r"/ \([a-z]\) by AFS|otherwise than by using|/ \(ii\) otherwise|/ \(b\) on (?:the|a) (?:same )?day",
    ),
    ("trade_mark", "registration", r"^(?:Single registration|Registration|For registration) of a trade mark", None),
    (
        "trade_mark",
        "renewal",
        r"^Renewal of (?:a single )?registration of a trade mark|section 69 of the Act for renewal",
        None,
    ),
    (
        "design",
        "filing",
        r"^(?:On )?(?:Filing|lodging) (?:a design application|an application for the registration of a design)",
        r"more than one design|further design",
    ),
    ("design", "examination", r"^Filing a request, by the registered owner of a design, for examination", None),
    ("design", "renewal", r"^Filing an application for renewal of the registration of a design", None),
    ("design", "extension_1", r"extension of the period of registration[^/]*/ \(a\)", None),
    ("design", "extension_2", r"extension of the period of registration[^/]*/ \(b\)", None),
    ("design", "extension_3", r"extension of the period of registration[^/]*/ \(c\)", None),
    ("pbr", "application", r"^On lodgment of an application under section 26", None),
    (
        "pbr",
        "examination",
        r"^On lodgment of a detailed description",
        r"\(i\) if the testing|each of 2 or more|/ \(b\) a variety to which",
    ),
    ("pbr", "grant", r"^Grant of PBR", None),
    ("pbr", "annual", r"^For annual maintenance of a PBR", None),
]
PER_ANNIVERSARY = ("standard_renewal", "innovation_renewal")


def _pick(rows: pd.DataFrame) -> float | None:
    """The base fee: leave out surcharges (in the paragraphs below the item's own words), then take the cheapest
    way of paying where the schedule offers one, then the lowest amount."""
    below = rows["matter"].str.split(" / ").str[1:].str.join(" / ")
    rows = rows[~below.str.contains(EXTRA) | below.str.contains(BASE)]
    if rows.empty:
        return None
    cheap = rows[rows["matter"].str.contains(CHEAPER)]
    return float((cheap if not cheap.empty else rows)["amount_aud"].min())


def key_fees(rows: pd.DataFrame) -> dict[tuple[str, int], float]:
    """{(fee, anniversary or 0): amount} for one schedule's rows of one right."""
    out = {}
    if rows.empty:
        return out
    right = rows["right"].iloc[0]
    for r, fee, pat, neg in RULES:
        if r != right:
            continue
        d = rows[rows["matter"].str.contains(pat, flags=re.I, regex=True)]
        if neg:
            d = d[~d["matter"].str.contains(neg, flags=re.I, regex=True)]
        if fee in PER_ANNIVERSARY:
            d = d.assign(anniv=d["matter"].map(anniversary)).dropna(subset=["anniv"])
            for a, g in d.groupby("anniv"):
                if (v := _pick(g)) is not None:
                    out[(fee, int(a))] = v
        elif not d.empty and (v := _pick(d)) is not None:
            out[(fee, 0)] = v
    return out


# Fetching --------------------------------------------------------------------------------------------------------


def _get_json(path: str) -> dict:
    return http_get(f"{API}/{path}", timeout=300).json()


def _epub(ctx: Ctx, title: str, doc: dict) -> bytes:
    """One document's EPUB, from the cache or the API."""
    cache = ctx.cache / "epub" / title / f"{doc['start'][:10]}_{doc['volumeNumber']}.epub"
    if not cache.exists():
        cache.parent.mkdir(parents=True, exist_ok=True)
        key = (
            f"titleId='{title}',start={doc['start']},retrospectiveStart={doc['retrospectiveStart']},"
            f"rectificationVersionNumber={doc['rectificationVersionNumber']},type='Primary',"
            f"uniqueTypeNumber={doc['uniqueTypeNumber']},volumeNumber={doc['volumeNumber']},format='Epub'"
        )
        cache.write_bytes(http_get(f"{API}/documents({key})", timeout=300).content)
    return cache.read_bytes()


def _epubs(title: str) -> list[dict]:
    q = f"documents?$filter=titleId eq '{title}' and format eq 'Epub' and type eq 'Primary'&$top=500"
    return _get_json(q)["value"]


def _bundle(ctx: Ctx, name: str, files: dict[str, bytes]) -> None:
    """Raw EPUBs, zipped (stored, with fixed dates, so a re-run gives the same file), kept in R2."""
    p = ctx.cache / name
    with zipfile.ZipFile(p, "w", zipfile.ZIP_STORED) as z:
        for n in sorted(files):
            z.writestr(zipfile.ZipInfo(n, date_time=(1980, 1, 1, 0, 0, 0)), files[n])
    ctx.keep_raw(p, keep="r2", url=API)


# Assembling ------------------------------------------------------------------------------------------------------


def _spells(states: list[tuple[str, str, str, dict]], until: str | None) -> list[dict]:
    """Turn a title's dated states [(date, source, basis, {(fee, anniversary): amount})] into spells of one amount
    per fee, each ending (exclusive) where the amount changes or the fee stops being charged."""
    out, open_ = [], {}
    for date, source, basis, state in states:
        for key in list(open_):
            if state.get(key) != open_[key]["amount_aud"]:
                out.append({**open_.pop(key), "end": date})
        for key, amount in state.items():
            if key not in open_:
                open_[key] = {
                    "fee": key[0],
                    "anniversary": key[1] or None,
                    "start": date,
                    "amount_aud": amount,
                    "source": source,
                    "basis": basis,
                }
    return out + [{**s, "end": until} for s in open_.values()]


def run(ctx: Ctx) -> None:
    gaps = yaml.safe_load((ctx.raw / "gaps.yaml").read_text("utf-8"))["titles"]
    ctx.keep_raw(ctx.raw / "gaps.yaml")
    all_versions, sched, spells, raw_versions = [], [], [], {}
    amending: dict[str, bytes] = {}
    for title, t in TITLES.items():
        right, name, num, from_, until = t["right"], t["name"], t["schedule"], t["start"], t.get("until")
        vs = _get_json(f"versions?$filter=titleId eq '{title}'&$top=500")["value"]
        if not vs:
            raise CorpusError(f"frl_fees: no versions for {title}")
        raw_versions[title] = vs
        docs = {}
        for d in _epubs(title):
            docs.setdefault(d["start"][:10], []).append(d)
        files, states = {}, []
        for v in sorted(vs, key=lambda x: x["start"]):
            start = v["start"][:10]
            all_versions.append(
                {
                    "title_id": title,
                    "title": name,
                    "right": right,
                    "start": start,
                    "end": (v["end"] or "")[:10] or None,
                    "register_id": v["registerId"],
                    "compilation": v["compilationNumber"],
                    "has_text": start in docs,
                    "amended_by": "; ".join(
                        r["affectedByTitle"]["titleId"] for r in v["reasons"] if r.get("affectedByTitle")
                    ),
                }
            )
            skip = {str(d) for d in gaps.get(title, {}).get("skip_compilations", [])}
            if start not in docs or (until and start >= until) or not t.get("compilations", True) or start in skip:
                continue
            blks = []
            for d in sorted(docs[start], key=lambda d: d["volumeNumber"]):
                b = _epub(ctx, title, d)
                files[f"{title}/{start}_{d['volumeNumber']}.epub"] = b
                blks += blocks(b)
            rows = flatten(section(blks, num))
            if not rows:
                raise CorpusError(f"frl_fees: no fee schedule found in {title} {start}")
            df = pd.DataFrame(rows).assign(title_id=title, right=right, start=start)
            sched.append(df.reset_index(names="row"))
            states.append((max(start, from_), v["registerId"] or title, "compilation", key_fees(df)))
        # versions without text, from gaps.yaml
        for e in gaps.get(title, {}).get("entries", []):
            date, inst = str(e["date"]), e["instrument"]
            prev = max((s for s in states if s[0] < date), key=lambda s: s[0], default=(None, None, None, {}))[3]
            state = dict(prev)
            if "parse" in e:
                doc = _epubs(inst)[0]
                b = amending.setdefault(f"{inst}.epub", _epub(ctx, inst, doc))
                found = key_fees(pd.DataFrame(flatten(blocks(b))).assign(right=right))
                if not found:
                    raise CorpusError(f"frl_fees: no key fees read from {inst} ({title}, {date})")
                state = found if e["parse"] == "substitute" else {**state, **found}
            for fee, amount in (e.get("changes") or {}).items():
                base, _, n = fee.rpartition("_")
                key = (base, int(n)) if base in PER_ANNIVERSARY else (fee, 0)
                if amount is None:
                    state.pop(key, None)
                else:
                    state[key] = float(amount)
            states.append((max(date, from_), inst, "amendment", state))
        states.sort(key=lambda s: (s[0], s[2] == "compilation"))
        # a state carries forward to the next dated state; a compilation dated the same day as an entry wins
        dedup = {}
        for s in states:
            dedup[s[0]] = s
        states = [dedup[d] for d in sorted(dedup)]
        for s in _spells(states, until):
            spells.append({"right": right, "title_id": title, **s})
        if files:
            _bundle(ctx, f"{title}.zip", files)
    _bundle(ctx, "amending_instruments.zip", amending)
    ctx.raw_text("versions.json", json.dumps(raw_versions, indent=1, sort_keys=True))

    versions = pd.DataFrame(all_versions)
    rows = pd.concat(sched, ignore_index=True)[
        ["title_id", "right", "start", "row", "part", "item", "matter", "fee_text", "amount_aud"]
    ]
    key = pd.DataFrame(spells)
    key["anniversary"] = key["anniversary"].astype("Int64")
    for c in ("start", "end"):
        key[c] = pd.to_datetime(key[c]).dt.date
    key = key.sort_values(["right", "fee", "anniversary", "start"], na_position="first").reset_index(drop=True)
    _check(key)
    ctx.table(versions, "versions", describe="Every version of the fee regulations on the Federal Register")
    ctx.table(rows, "schedule_rows", describe="Every fee schedule row of every compilation with text")
    ctx.table(
        key[["right", "fee", "anniversary", "start", "end", "amount_aud", "source", "basis", "title_id"]],
        "key_fees",
        describe="The key fees of each right, one row per spell at one amount",
    )
    ctx.table(changes(key), "fee_changes", describe="Each date on which a right's key fees changed")


def changes(key: pd.DataFrame) -> pd.DataFrame:
    """One row per right and date on which a key fee started, changed or stopped being charged (a right's first
    schedule is its start, not a change)."""
    k = key.assign(label=key["fee"] + key["anniversary"].map(lambda a: "" if pd.isna(a) else f"_{int(a)}"))
    out = []
    for (right, label), g in k.sort_values("start").groupby(["right", "label"]):
        prev = None
        for r in g.itertuples():
            if prev is not None and prev.end != r.start:  # the fee stopped, then came back
                out.append((right, prev.end, label, prev.amount_aud, None, None))
                prev = None
            out.append((right, r.start, label, None if prev is None else prev.amount_aud, r.amount_aud, r.source))
            prev = r
        if prev is not None and not pd.isna(prev.end):
            out.append((right, prev.end, label, prev.amount_aud, None, None))
    c = pd.DataFrame(out, columns=["right", "date", "fee", "old", "new", "source"])
    c = c[c["date"] > c.groupby("right")["date"].transform("min")]
    c = c[(c["old"] != c["new"])]
    c["text"] = c["fee"] + ": " + c["old"].map(_aud) + " to " + c["new"].map(_aud)
    return (
        c.groupby(["right", "date"])
        .agg(
            fees_changed=("fee", "count"),
            changes=("text", "; ".join),
            source=("source", lambda s: ", ".join(sorted({x for x in s if isinstance(x, str)}))),
        )
        .reset_index()
        .sort_values(["date", "right"])
        .reset_index(drop=True)
    )


def _aud(x) -> str:
    return "none" if x is None or pd.isna(x) else f"${x:,.0f}"


def _check(key: pd.DataFrame) -> None:
    """Every right has its core fees in every year it should, so that a change of wording does not end a series."""
    need = {
        ("patent", "standard_filing"): ("1991-04-30", None),
        ("patent", "standard_examination"): ("1991-04-30", None),
        ("patent", "provisional_filing"): ("1991-04-30", None),
        ("trade_mark", "filing"): ("1989-07-01", None),
        ("trade_mark", "renewal"): ("1989-07-01", None),
        ("design", "filing"): ("1982-03-11", None),
        ("pbr", "application"): ("1994-11-10", None),
        ("pbr", "annual"): ("1994-11-10", None),
    }
    for (right, fee), (start, _) in need.items():
        g = key[(key["right"] == right) & (key["fee"] == fee)].sort_values("start")
        if g.empty or str(g["start"].iloc[0]) > start:
            raise CorpusError(f"frl_fees: {right} {fee} does not start by {start}")
        ends = g["end"].iloc[:-1].astype(str).tolist()
        starts = g["start"].iloc[1:].astype(str).tolist()
        if ends != starts or not pd.isna(g["end"].iloc[-1]):
            raise CorpusError(f"frl_fees: {right} {fee} has a gap or ends")


def reprocess(ctx: Ctx, tables: list[str] | None = None) -> None:
    """Rebuild from the cached EPUBs (fetching any that are missing) and gaps.yaml."""
    run(ctx)
