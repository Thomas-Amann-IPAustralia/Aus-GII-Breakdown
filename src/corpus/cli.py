"""`corpus`: ingest sources into the corpus, and check what is there.

corpus run iprapid rdti     fetch and process these sources (writes data/, uploads to R2, updates the manifest)
corpus run all              every source in config/sources.yaml with a module
corpus reprocess cer        process a source again from the raw files it already holds, fetching nothing new (for a
                            parser fix that should not change the data's vintage); `oecd:ip_tax_regimes` names tables
corpus list                 the sources, their tier and what the manifest holds for each
corpus verify [--r2]        repo files against the manifest's SHA-256 (and, with --r2, that R2 holds the rest)
"""

from __future__ import annotations

import argparse
import importlib
import importlib.util
import sys
import traceback

import yaml

from .core import BUCKET, ROOT, CorpusError, Ctx, r2, read_manifest, sha256


def register() -> list[dict]:
    return yaml.safe_load((ROOT / "config/sources.yaml").read_text("utf-8"))["sources"]


def run(ids: list[str]) -> int:
    known = [s["id"] for s in register()]
    if ids == ["all"]:
        ids = [i for i in known if importlib.util.find_spec(f"corpus.sources.{i}")]
    failed = []
    for i in ids:
        if i not in known:
            print(f"corpus: {i} is not in config/sources.yaml", file=sys.stderr)
            return 2
        ctx = Ctx(i)
        try:
            importlib.import_module(f"corpus.sources.{i}").run(ctx)
        except Exception as e:  # one source failing should not stop the rest
            msg = str(e) if isinstance(e, CorpusError) else traceback.format_exc(limit=3)
            print(f"[{i}] FAILED: {msg}", file=sys.stderr)
            failed.append(i)
            continue
        ctx.save()
    if failed:
        print(f"corpus run: failed: {', '.join(failed)}", file=sys.stderr)
        return 2
    return 0


def reprocess(specs: list[str]) -> int:
    """`source` or `source:table,table`: the module's `reprocess(ctx, tables)` rebuilds its tables from the raw files
    the manifest already records, and the manifest entry is merged rather than replaced (`Ctx.save(merge=True)`)."""
    known = [s["id"] for s in register()]
    for spec in specs:
        sid, _, names = spec.partition(":")
        if sid not in known:
            print(f"corpus: {sid} is not in config/sources.yaml", file=sys.stderr)
            return 2
        module = importlib.import_module(f"corpus.sources.{sid}")
        if not hasattr(module, "reprocess"):
            print(f"corpus: {sid} cannot be reprocessed (no reprocess function); use corpus run", file=sys.stderr)
            return 2
        ctx = Ctx(sid)
        try:
            module.reprocess(ctx, [n for n in names.split(",") if n] or None)
        except CorpusError as e:
            print(f"[{sid}] FAILED: {e}", file=sys.stderr)
            return 2
        ctx.save(merge=True)
    return 0


def verify(check_r2: bool) -> int:
    bad, n, remote = [], 0, []
    for sid, s in read_manifest()["sources"].items():
        for f in s["files"].values():
            if f["location"] == "repo":
                n += 1
                p = ROOT / f["path"]
                if not p.exists() or sha256(p) != f["sha256"]:
                    bad.append(f["path"])
            else:
                remote.append((sid, f))
    if check_r2:
        c = r2()
        for _sid, f in remote:
            try:
                h = c.head_object(Bucket=BUCKET, Key=f["key"])
                if h["ContentLength"] != f["bytes"]:
                    bad.append(f"r2:{f['key']} (size)")
            except c.exceptions.ClientError:
                bad.append(f"r2:{f['key']} (missing)")
    if bad:
        print("corpus verify: differ from the manifest:\n  " + "\n  ".join(bad), file=sys.stderr)
        return 2
    print(f"corpus verify: {n} repo files match" + (f"; R2 holds all {len(remote)} others" if check_r2 else ""))
    return 0


def listing() -> int:
    m = read_manifest()["sources"]
    for s in register():
        files = m.get(s["id"], {}).get("files", {})
        tables = [k.split("/", 1)[1] for k in files if k.startswith("processed/")]
        print(f"{s['id']:<22} tier {s.get('tier', '-')}  {len(tables):>3} tables  {s['title']}")
    return 0


CATALOGUE_HEAD = """# Data catalogue

Every source in the corpus and every table it holds. Written by `uv run corpus catalogue` from `config/sources.yaml`
and `data/manifest.json`; edit those (or a source's module docstring), not this file. What each source is for, and
what is still missing, is in `docs/data-plan.md`; how to use the corpus is in `README.md`.

**Where a table lives.** *repo* tables are in `data/processed/<source>/<table>.parquet`. *R2* tables are in the
`ipholmes` bucket at `processed/<source>/<table>.parquet`; `corpus.load` and `corpus.path` fetch them once into
`~/.cache/ipholmes` (R2 credentials in `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID` and `R2_SECRET_ACCESS_KEY`).

**Join keys.** `abn` (11 digits, as text) joins IP RAPID, IPLORD, the ABR, ASIC (through `acn`), the R&D Tax Incentive,
AusTender and the corporate tax reports; `linkage/abn_spine` already does it. Postcodes join to ABS geography through
`abs_regions/poa` and `poa_sa2` (a postcode is a postal area code, as text). IPC subclasses join to industries and
technology fields through `concordances`. ISO3 codes join the cross-country sources (`gii`, `oecd`, `wdi`).
"""


def catalogue() -> int:
    m = read_manifest()["sources"]
    out = [CATALOGUE_HEAD]
    for s in register():
        sid = s["id"]
        mod = importlib.util.find_spec(f"corpus.sources.{sid}")
        doc = importlib.import_module(f"corpus.sources.{sid}").__doc__ if mod else None
        files = m.get(sid, {}).get("files", {})
        out.append(f"## {s['title']} (`{sid}`)\n")
        out.append(
            f"{s['publisher']}. Tier {s.get('tier', '-')}; questions {', '.join(map(str, s.get('questions', [])))}."
            f" Licence: {s['licence']}. Source: {s['url']}\n"
        )
        if doc:
            out.append(doc.strip() + "\n")
        tables = {k.split("/", 1)[1]: f for k, f in files.items() if k.startswith("processed/")}
        if tables:
            out.append("| Table | Rows | Where | Columns |\n|---|---:|---|---|")
            for name, f in sorted(tables.items()):
                cols = ", ".join(f"`{c}`" for c in f["columns"][:14]) + (" …" if len(f["columns"]) > 14 else "")
                where = "repo" if f["location"] == "repo" else "R2"
                out.append(f"| `{name}` | {f['rows']:,} | {where} ({f['bytes'] / 1e6:.1f} MB) | {cols} |")
            out.append("")
        else:
            out.append("*Not ingested yet: see the status in `docs/data-plan.md`.*\n")
        for n in m.get(sid, {}).get("notes", []):
            out.append(f"- Note: {n}")
        if m.get(sid, {}).get("notes"):
            out.append("")
    (ROOT / "docs/catalogue.md").write_text("\n".join(out), encoding="utf-8")
    print(f"wrote docs/catalogue.md ({len(register())} sources)")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="corpus", description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("ids", nargs="+")
    rp = sub.add_parser("reprocess")
    rp.add_argument("specs", nargs="+")
    v = sub.add_parser("verify")
    v.add_argument("--r2", action="store_true")
    sub.add_parser("list")
    sub.add_parser("catalogue")
    a = ap.parse_args(argv)
    if a.cmd == "run":
        return run(a.ids)
    if a.cmd == "reprocess":
        return reprocess(a.specs)
    if a.cmd == "verify":
        return verify(a.r2)
    if a.cmd == "catalogue":
        return catalogue()
    return listing()


if __name__ == "__main__":
    sys.exit(main())
