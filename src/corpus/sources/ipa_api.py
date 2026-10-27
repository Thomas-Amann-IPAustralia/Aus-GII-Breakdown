"""IP Australia's register APIs: the live records behind IP RAPID, to check it against and to fill its gaps (ADR 0028).

The client is `corpus.ipa_api` (production; credentials in the environment). A run takes:

- `numbers`: every trade mark and design number the APIs' searches find, by year of lodgement (trade marks) or filing
  (designs), and whether the record changed after the IP RAPID release in the corpus. Patents cannot be listed: the
  patent search ignores fields and returns at most 5,000 numbers.
- records, fetched one by one, for these targets (a right can have several; `reasons` lists them):
  - `sample`: a random sample of IP RAPID's applications (seed 2026): 3,000 trade marks, 2,000 designs and 2,000
    patents, to check IP RAPID field by field;
  - `abn_gap`: trade marks filed from July 2024 whose first current applicant is an Australian organisation with no
    ABN in IP RAPID (OQ7); `abn_control`: the same in FY2023, before the change;
  - `country_gap`: designs with no applicant country in IP RAPID (OQ14);
  - `number_gap`: trade mark numbers 1,978,060 to 1,980,352, missing from IP RAPID (OQ13);
  - `api_only`, `iprapid_only`: numbers one side has and the other's searches do not find.

Raw: the records as the API sent them, gzipped JSON lines by right (R2: they hold individuals' names and addresses).
Processed: `trade_marks`, `designs` and `patents`, one row per number fetched (whether found, status, dates, the
first current owner's ABN, ACN, country, state and postcode, classes), without names (repo); `owners`, one row per
right and current owner with names, as the API gives them (R2).

A run takes about two hours (600 requests a minute per API). Records already fetched today are kept if a run is
interrupted, so running it again the same day carries on.
"""

from __future__ import annotations

import datetime as dt
import gzip
import json
import re
import shutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import duckdb
import pandas as pd
import pycountry

from .. import ipa_api
from ..core import CorpusError, Ctx, path, read_manifest

SAMPLE = {"trade_mark": 3000, "design": 2000, "patent": 2000}
SEED = 2026
NUMBER_GAP = (1_978_060, 1_980_352)
DATE_TYPE = {"trade_mark": "LODGEMENT_DATE", "design": "FILED"}
FIRST_YEAR = {"trade_mark": 1900, "design": 1900}
BATCH = 250
MAX_DIFF = 60_000
# Names the trade mark API uses that pycountry does not know, or would match wrongly ("REPUBLIC OF KOREA" fuzzily
# matches North Korea). Former states keep IP RAPID's codes for them.
COUNTRY_NAMES = {
    "REPUBLIC OF KOREA": "kr",
    "KOREA, REPUBLIC OF": "kr",
    "SOUTH KOREA": "kr",
    "THE NETHERLANDS": "nl",
    "TURKEY": "tr",
    "REPUBLIC OF IRELAND": "ie",
    "CZECHOSLOVAKIA": "cs",
    "USSR": "su",
    "YUGOSLAVIA": "yu",
    "GERMAN DEMOCRATIC REPUBLIC": "dd",
    "ENGLAND": "gb",
    "SCOTLAND": "gb",
    "WALES": "gb",
    "TAIWAN": "tw",
    "HONG KONG": "hk",
}


def release_date() -> str:
    """The date of the IP RAPID release the corpus holds (from its manifest note)."""
    for n in read_manifest()["sources"]["iprapid"].get("notes", []):
        if m := re.search(r"release of (\d{4}-\d{2}-\d{2})", n):
            return m.group(1)
    raise ValueError("no IP RAPID release date in the manifest")


# -- numbers ----------------------------------------------------------------------------------------------------------


def numbers(client: ipa_api.Client, release: str, cache: Path) -> pd.DataFrame:
    """Every trade mark and design number the searches find, with its year and whether it changed since `release`.
    Each year's numbers are kept in `cache` for the day, so an interrupted run carries on."""
    this_year = dt.date.today().year
    stamp = dt.date.today().isoformat()
    jobs = [(r, y) for r in DATE_TYPE for y in range(FIRST_YEAR[r], this_year + 1)]
    jobs += [(r, "changed") for r in DATE_TYPE]

    def year(job):
        right, y = job
        f = cache / f"numbers-{stamp}" / f"{right}-{y}.json"
        if f.exists():
            return right, y, json.loads(f.read_text())
        if y == "changed":
            first, last = f"{FIRST_YEAR[right]}-01-01", f"{this_year}-12-31"
            ids = client.ids(right, DATE_TYPE[right], first, last, changedSinceDate=release)
        else:
            ids = client.ids(right, DATE_TYPE[right], f"{y}-01-01", f"{y}-12-31")
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps(ids))
        return right, y, ids

    frames, changed = [], set()
    with ThreadPoolExecutor(3) as pool:  # big searches several at a time make the server answer 500
        for right, y, ids in pool.map(year, jobs):
            if y == "changed":
                changed |= {(right, i) for i in ids}
            elif ids:
                frames.append(pd.DataFrame({"ip_right_type": right, "application_number": ids, "year": y}))
    out = pd.concat(frames, ignore_index=True)
    out["changed_since_release"] = [
        (r, n) in changed for r, n in zip(out.ip_right_type, out.application_number, strict=True)
    ]
    out["date_type"] = out.ip_right_type.map(DATE_TYPE)
    return out.drop_duplicates(["ip_right_type", "application_number"])


# -- targets ----------------------------------------------------------------------------------------------------------


def targets(nums: pd.DataFrame) -> pd.DataFrame:
    """(ip_right_type, application_number, reason) for every record to fetch."""
    con = duckdb.connect()
    con.execute(f"CREATE VIEW app AS SELECT * FROM '{path('iprapid', 'application')}'")
    con.execute(f"CREATE VIEW tmr AS SELECT * FROM '{path('iprapid', 'trade_mark_rights')}'")
    con.execute(f"CREATE VIEW dr AS SELECT * FROM '{path('iprapid', 'design_rights')}'")
    con.register("nums", nums)
    org_no_abn = (
        "SELECT 'trade_mark', application_number, '{r}' FROM tmr WHERE applicant_type = 'organisation' "
        "AND applicant_country = 'au' AND any_applicant_abn IS NULL AND application_date BETWEEN '{a}' AND '{b}'"
    )
    parts = [
        *(  # a fixed pseudo-random order, so the sample is the same on every run of the same release
            f"(SELECT ip_right_type, application_number, 'sample' FROM app WHERE ip_right_type = '{r}' "
            f"ORDER BY hash(application_number || '{SEED}') LIMIT {n})"
            for r, n in SAMPLE.items()
        ),
        org_no_abn.format(r="abn_gap", a="2024-07-01", b="2100-01-01"),
        org_no_abn.format(r="abn_control", a="2022-07-01", b="2023-06-30"),
        "SELECT 'design', application_number, 'country_gap' FROM dr WHERE applicant_country IS NULL",
        f"SELECT 'trade_mark', CAST(n AS VARCHAR), 'number_gap' FROM range({NUMBER_GAP[0]}, {NUMBER_GAP[1] + 1}) t(n)"
        " WHERE CAST(n AS VARCHAR) NOT IN (SELECT application_number FROM app WHERE ip_right_type = 'trade_mark')",
        "SELECT ip_right_type, application_number, 'api_only' FROM nums ANTI JOIN app USING (ip_right_type, "
        "application_number)",
        "SELECT ip_right_type, application_number, 'iprapid_only' FROM app ANTI JOIN nums USING (ip_right_type, "
        "application_number) WHERE ip_right_type IN ('trade_mark', 'design')",
    ]
    sql = " UNION ALL ".join(f"({p})" for p in parts)
    df = con.execute(f"SELECT * FROM ({sql}) t(ip_right_type, application_number, reason)").df().drop_duplicates()
    diff = df[df.reason.isin(["api_only", "iprapid_only"])].groupby(["ip_right_type", "reason"]).size()
    if (diff > MAX_DIFF).any():  # a search that failed quietly would send millions of requests
        raise CorpusError(f"ipa_api: the number lists differ too much to fetch one by one:\n{diff}")
    return df


# -- fetching ---------------------------------------------------------------------------------------------------------


def _read_jsonl(p: Path) -> dict[str, dict | None]:
    """The records in a raw file written by `fetch` (a run cut off mid-write loses only its last batch)."""
    out: dict[str, dict | None] = {}
    if not p.exists():
        return out
    try:
        with gzip.open(p, "rt", encoding="utf-8") as f:
            for line in f:
                row = json.loads(line)
                out[row["number"]] = row["record"]
    except (EOFError, gzip.BadGzipFile, json.JSONDecodeError):
        pass
    return out


def fetch(client: ipa_api.Client, right: str, wanted: list[str], raw: Path, log) -> dict[str, dict | None]:
    """Each wanted record (None where the API has none), appended to `raw` a batch at a time."""
    have = _read_jsonl(raw)
    todo = [n for n in dict.fromkeys(wanted) if n not in have or ipa_api.failed(have[n])]
    log(f"{right}: {len(have):,} records already fetched today, {len(todo):,} to fetch")
    for i in range(0, len(todo), BATCH):
        batch = list(client.get_many(right, todo[i : i + BATCH], workers=10))
        with gzip.open(raw, "at", encoding="utf-8") as f:  # one gzip member a batch
            for n, rec in batch:
                f.write(json.dumps({"number": n, "record": rec}) + "\n")
        have.update(batch)
        if (i // BATCH) % 20 == 0:
            log(f"{right}: {min(i + BATCH, len(todo)):,} of {len(todo):,} ({client.retries:,} retries so far)")
    return have


# -- flattening -------------------------------------------------------------------------------------------------------


def country(name: str | None) -> str | None:
    """A country name as the trade mark API gives it ('AUSTRALIA', 'VIET NAM') as IP RAPID's lowercase ISO code."""
    if not name:
        return None
    if len(name) == 2:
        return name.lower()
    if name.upper() in COUNTRY_NAMES:
        return COUNTRY_NAMES[name.upper()]
    try:
        return pycountry.countries.lookup(name).alpha_2.lower()
    except LookupError:
        try:
            return pycountry.countries.search_fuzzy(name)[0].alpha_2.lower()
        except LookupError:
            return None


def _abn(v) -> str | None:
    v = re.sub(r"\D", "", str(v or ""))
    return v.zfill(11) if v and set(v) != {"0"} else None


def _owner(o: dict, *, nested: bool) -> dict:
    a = (o.get("structuredAddress") or {}) if nested else o
    return {
        "name": o.get("name"),
        "abn": _abn(o.get("abn")),
        "acn": re.sub(r"\D", "", str(o.get("acnOrArbn") or "")) or None,
        "country": country(a.get("countryName") if nested else a.get("countryCode")),
        "state": (a.get("state") or None) and a["state"].strip().lower(),
        "postcode": (a.get("postalCode") or None) and str(a["postalCode"]).strip(),
    }


def owners(right: str, n: str, rec: dict | None) -> list[dict]:
    if not rec or ipa_api.failed(rec):
        return []
    if right == "trade_mark":
        os_ = [_owner(o, nested=True) for o in rec.get("owner") or []]
    elif right == "design":
        os_ = [_owner(o, nested=False) for o in rec.get("currentOwners") or []]
    else:  # the patent API gives names only
        os_ = [{"name": o.get("legalEntityName")} for o in rec.get("applicant") or []]
    return [{"ip_right_type": right, "application_number": n, "seq": i, **o} for i, o in enumerate(os_)]


def _first_owner(right, n, rec) -> dict:
    os_ = owners(right, n, rec)
    first = os_[0] if os_ else {}
    return {
        "owner_count": len(os_),
        **{f"owner_{k}": first.get(k) for k in ("abn", "acn", "country", "state", "postcode")},
        "any_owner_abn": next((o["abn"] for o in os_ if o.get("abn")), None),
        "any_owner_in_australia": any(o.get("country") == "au" for o in os_) if right != "patent" else None,
    }


def _date(v) -> dt.date | None:
    if not v:
        return None
    v = str(v)
    return dt.date.fromisoformat(f"{v[:4]}-{v[4:6]}-{v[6:8]}" if re.fullmatch(r"\d{8}", v) else v[:10])


def flat(right: str, n: str, rec: dict | None) -> dict:
    if ipa_api.failed(rec):  # the register would not answer: neither found nor not found
        return {"application_number": n, "found": None, "error": rec["_error"][:200]}
    row = {"application_number": n, "found": rec is not None}
    if rec is None:
        return row
    if right == "trade_mark":
        classes = sorted({int(g["class"]) for g in rec.get("goodsAndServices") or [] if str(g.get("class")).isdigit()})
        history = rec.get("historyAndPublicationDetails") or []
        expedite = [h for h in history if "xpedit" in (h.get("displayName") or "")]
        row |= {
            "status_group": rec.get("statusGroup"),
            "status_code": rec.get("statusCode"),
            "status_detail": rec.get("statusDetail"),
            **{
                re.sub(r"(?<!^)(?=[A-Z])", "_", k).lower(): _date(rec.get(k))
                for k in (
                    "lodgementDate",
                    "filingDate",
                    "priorityDate",
                    "divisionalDate",
                    "irNotificationDate",
                    "firstReportDate",
                    "acceptanceDate",
                    "enteredOnRegisterDate",
                    "registeredFromDate",
                    "renewalDueDate",
                    "lapsedDate",
                    "withdrawalDate",
                )
            },
            "ir_number": rec.get("irNumber"),
            "kinds": ",".join(rec.get("kind") or []) or None,
            "classes": ",".join(map(str, classes)) or None,
            "class_count": len(classes),
            "convention": bool(rec.get("conventionDetails")),
            "series": rec.get("seriesIndicator"),
            "history_events": len(history),
            # the register's own record of expedited examination (OQ6): which events, and the first one's date
            "expedite_events": ";".join(sorted({h["displayName"] for h in expedite})) or None,
            "expedite_date": min((d for h in expedite if (d := _date(h.get("date")))), default=None),
        }
    elif right == "design":
        d = rec.get("dates") or {}
        row |= {
            "status": rec.get("status"),
            **{
                f"{k}_date": _date(d.get(k))
                for k in (
                    "filed",
                    "registered",
                    "certified",
                    "published",
                    "ceased",
                    "lapsed",
                    "refused",
                    "withdrawn",
                    "revoked",
                )
            },
            "priority_date": _date(rec.get("priorityDate")),
            "registered_until": _date(d.get("currentlyRegisteredUntil")),
            "main_class": next((c.get("code") for c in rec.get("classification") or []), None),
            "convention": bool(rec.get("conventionDetails")),
        }
    else:
        b = rec.get("bibliographicData") or {}
        life = rec.get("lifecycleDetails") or {}
        ipc = sorted(b.get("ipcrClassification") or [], key=lambda c: c.get("sequenceNumber") or 0)
        conv = b.get("conventionDetails") or []
        row |= {
            "patent_type": b.get("patentApplicationType"),
            "status_code": rec.get("ipRightStatusCode"),
            "filed_date": _date(rec.get("filedDate")),
            "priority_date": _date(rec.get("priorityDate")),
            "opi_date": _date(rec.get("auOPIDate")),
            "acceptance_published_date": _date((life.get("acceptanceDetails") or {}).get("acceptancePublishedDate")),
            "sealing_date": _date((life.get("sealingDetails") or {}).get("sealingDate")),
            "expiry_date": _date(rec.get("expiryDate")),
            "inforce_to_date": _date(rec.get("inforceToDate")),
            "main_ipc": ipc[0].get("classificationText") if ipc else None,
            "ipc_subclasses": " ".join(
                dict.fromkeys(re.sub(r"\s", "", c.get("classificationText") or "")[:4] for c in ipc)
            )
            or None,
            "ipc_count": len(ipc),
            "pct": str(b.get("pctApplicationIndicator")).lower() == "true",
            "pct_number": (b.get("pctDetails") or rec.get("pctDetails") or {}).get("pctNumber"),
            "pct_national_phase_date": _date(
                (b.get("pctDetails") or rec.get("pctDetails") or {}).get("pctNationalPhaseEntryDate")
            ),
            "convention_countries": ",".join(sorted({c.get("priorityCountryCode") or "" for c in conv} - {""})) or None,
            "inventor_count": len(rec.get("inventors") or []),
            "representative_count": len(rec.get("representatives") or []),
            "extensions_of_term": len(life.get("extensionsOfTerm") or []),
        }
    return row | _first_owner(right, n, rec)


# -- run --------------------------------------------------------------------------------------------------------------


def run(ctx: Ctx) -> None:
    client = ipa_api.Client("prod")
    release = release_date()
    ctx.note(f"ipa_api: production register as at {dt.date.today()}; compared with the IP RAPID release of {release}")
    nums = numbers(client, release, ctx.cache)
    ctx.table(nums, "numbers", describe="Every trade mark and design number the APIs' searches find, by year")
    tg = targets(nums)
    reasons = tg.groupby(["ip_right_type", "application_number"])["reason"].agg(lambda r: ",".join(sorted(set(r))))
    stamp = dt.date.today().isoformat()
    all_owners = []
    for right in ("trade_mark", "design", "patent"):
        wanted = list(reasons.loc[right].index) if right in reasons.index.get_level_values(0) else []
        raw = ctx.cache / f"{right}-{stamp}.jsonl.gz"
        raw.parent.mkdir(parents=True, exist_ok=True)
        recs = fetch(client, right, wanted, raw, ctx.log)
        rows = pd.DataFrame([flat(right, n, recs[n]) for n in wanted])
        rows.insert(1, "reasons", [reasons.loc[(right, n)] for n in wanted])
        rows["fetched"] = dt.date.fromisoformat(stamp)
        ctx.table(rows, f"{right}s", keep="repo", describe=f"API records of {right}s fetched, without names")
        all_owners += [o for n in wanted for o in owners(right, n, recs[n])]
        final = ctx.cache / f"{right}.jsonl.gz"
        shutil.copyfile(raw, final)  # the dated file stays, so a second run the same day fetches nothing again
        ctx.keep_raw(final, keep="r2")
    ctx.table(pd.DataFrame(all_owners), "owners", keep="r2", describe="Each fetched right's current owners, named")
    ctx.note(f"ipa_api: {client.calls:,} calls, {client.retries:,} retried (production patents answer 403 at random)")
    ctx.save()
