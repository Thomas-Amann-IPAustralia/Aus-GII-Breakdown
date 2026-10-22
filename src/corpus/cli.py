"""`corpus`: ingest sources into the corpus, and check what is there.

corpus run ipgod iplord     fetch and process these sources (writes data/, uploads to R2, updates the manifest)
corpus run all              every source in config/sources.yaml with a module
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


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="corpus", description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("ids", nargs="+")
    v = sub.add_parser("verify")
    v.add_argument("--r2", action="store_true")
    sub.add_parser("list")
    a = ap.parse_args(argv)
    if a.cmd == "run":
        return run(a.ids)
    if a.cmd == "verify":
        return verify(a.r2)
    return listing()


if __name__ == "__main__":
    sys.exit(main())
