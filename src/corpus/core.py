"""What every source module shares: downloads, the R2 store, Parquet output and the manifest.

A source runs in a `Ctx`. It fetches raw files (kept in the repo when small, in R2 when large), writes Parquet tables
(in the repo when under the size limit, in R2 otherwise) and the context records every file's SHA-256, size and
location in `data/manifest.json`. Large raw files pass through a local cache outside the repo
(`$IPHOLMES_CACHE`, default `~/.cache/ipholmes`), so the repo never holds them.

Fails loudly: a source that cannot do its job raises `CorpusError` with one line naming the source and what to check.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import requests

ROOT = Path(__file__).resolve().parents[2]
CACHE = Path(os.environ.get("IPHOLMES_CACHE", Path.home() / ".cache/ipholmes"))
MANIFEST = ROOT / "data/manifest.json"
BUCKET = os.environ.get("IPHOLMES_BUCKET", "ipholmes")
REPO_LIMIT = 50 * 1024 * 1024  # GitHub refuses files over 100 MB; stay well under
UA = "ipholmes-corpus/1.0 (IP Australia research; https://github.com/Thomas-Amann-IPAustralia/Aus-GII-Breakdown)"


class CorpusError(Exception):
    """A source could not do its job. The message is one line naming the source and what to check."""


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def http_get(url: str, *, params=None, headers=None, tries: int = 5, timeout: int = 120, stream: bool = False):
    """GET with retries (2, 4, 8, 16 s) on network errors and 5xx/429; raises on anything else that is not 200."""
    h = {"User-Agent": UA, **(headers or {})}
    for i in range(tries):
        try:
            r = requests.get(url, params=params, headers=h, timeout=timeout, stream=stream)
            if r.status_code == 200:
                return r
            if r.status_code not in (429, 500, 502, 503, 504):
                raise CorpusError(f"GET {r.url} answered {r.status_code}")
        except requests.RequestException as e:
            if i == tries - 1:
                raise CorpusError(f"GET {url} failed: {e}") from e
        time.sleep(2 ** (i + 1))
    raise CorpusError(f"GET {url} kept failing after {tries} tries")


def download(url: str, dest: Path, *, force: bool = False, **kw) -> Path:
    """Stream a URL to `dest` (skipped when it is already there, unless `force`)."""
    if dest.exists() and dest.stat().st_size > 0 and not force:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(dest.name + ".part")
    with http_get(url, stream=True, timeout=600, **kw) as r, open(tmp, "wb") as f:
        for chunk in r.iter_content(1 << 20):
            f.write(chunk)
    tmp.replace(dest)
    return dest


def unzip_names(zpath: Path) -> list[str]:
    """Members of a zip, by Info-ZIP (which reads Deflate64, unlike Python's zipfile)."""
    out = subprocess.run(["unzip", "-Z1", str(zpath)], check=True, capture_output=True, text=True).stdout
    return [n for n in out.splitlines() if n and not n.endswith("/")]


def unzip_member(zpath: Path, member: str, dest_dir: Path) -> Path:
    """Extract one member to dest_dir (flattened to its base name) and return its path."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / Path(member).name
    with open(dest, "wb") as f:
        subprocess.run(["unzip", "-p", str(zpath), member], check=True, stdout=f)
    return dest


# R2 -------------------------------------------------------------------------------------------------------------------


def r2():
    import boto3

    try:
        account = os.environ["R2_ACCOUNT_ID"]
        key, secret = os.environ["R2_ACCESS_KEY_ID"], os.environ["R2_SECRET_ACCESS_KEY"]
    except KeyError as e:
        raise CorpusError(f"R2 needs {e.args[0]} in the environment") from e
    return boto3.client(
        "s3",
        endpoint_url=f"https://{account}.r2.cloudflarestorage.com",
        aws_access_key_id=key,
        aws_secret_access_key=secret,
        region_name="auto",
    )


def r2_put(local: Path, key: str, digest: str) -> None:
    """Upload unless R2 already holds the same bytes (by the SHA-256 kept in the object's metadata)."""
    c = r2()
    try:
        if c.head_object(Bucket=BUCKET, Key=key).get("Metadata", {}).get("sha256") == digest:
            return
    except c.exceptions.ClientError:
        pass
    c.upload_file(str(local), BUCKET, key, ExtraArgs={"Metadata": {"sha256": digest}})


def r2_get(key: str, dest: Path) -> Path:
    if not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp = dest.with_name(dest.name + ".part")
        r2().download_file(BUCKET, key, str(tmp))
        tmp.replace(dest)
    return dest


# The manifest -------------------------------------------------------------------------------------------------------


def read_manifest() -> dict:
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text("utf-8"))
    return {"bucket": BUCKET, "sources": {}}


def write_manifest(m: dict) -> None:
    m["sources"] = dict(sorted(m["sources"].items()))
    tmp = MANIFEST.with_suffix(".tmp")
    tmp.write_text(json.dumps(m, indent=1, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(MANIFEST)


# The context a source runs in ---------------------------------------------------------------------------------------


class Ctx:
    """One source's run. `raw`, `out` (repo) and `cache` (outside the repo) are its directories."""

    def __init__(self, source: str):
        self.source = source
        self.raw = ROOT / "data/raw" / source
        self.out = ROOT / "data/processed" / source
        self.cache = CACHE / source
        self.files: dict[str, dict] = {}
        self.notes: list[str] = []

    def log(self, msg: str) -> None:
        print(f"[{self.source}] {msg}", flush=True)

    def note(self, msg: str) -> None:
        """Something left out or worth knowing, kept in the manifest."""
        self.notes.append(msg)
        self.log(msg)

    # raw files

    def fetch(self, url: str, name: str, *, keep: str = "repo", force: bool = False, **kw) -> Path:
        """Download a raw file. keep='repo' puts it in data/raw/<source>/; keep='r2' caches it and uploads it;
        keep='auto' chooses by size."""
        if keep == "auto":  # the repo when it fits, R2 otherwise
            tmp = download(url, self.cache / name, force=force, **kw)
            if tmp.stat().st_size > REPO_LIMIT:
                return self.keep_raw(tmp, keep="r2", url=url)
            self.raw.mkdir(parents=True, exist_ok=True)
            tmp.replace(self.raw / name)
            return self.keep_raw(self.raw / name, keep="repo", url=url)
        dest = (self.raw if keep == "repo" else self.cache) / name
        if keep == "repo" and not dest.exists() and (self.cache / name).exists() and not force:
            (self.cache / name).replace(dest)
        download(url, dest, force=force, **kw)
        return self.keep_raw(dest, keep=keep, url=url)

    def keep_raw(self, path: Path, *, keep: str = "repo", url: str | None = None) -> Path:
        digest = sha256(path)
        size = path.stat().st_size
        if keep == "repo":
            if size > REPO_LIMIT:
                raise CorpusError(f"{self.source}: {path.name} is {size >> 20} MB, too big for the repo; keep it in R2")
            entry = {"location": "repo", "path": str(path.relative_to(ROOT))}
        else:
            key = f"raw/{self.source}/{path.name}"
            r2_put(path, key, digest)
            entry = {"location": "r2", "key": key}
        self.files[f"raw/{path.name}"] = {**entry, "sha256": digest, "bytes": size, **({"url": url} if url else {})}
        return path

    def raw_text(self, name: str, text: str) -> Path:
        """A small raw file made here (an API response, a scraped table), kept in the repo."""
        p = self.raw / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        return self.keep_raw(p)

    # processed tables

    def table(self, df: pd.DataFrame | pa.Table, name: str, *, keep: str = "auto", describe: str = "") -> Path:
        """Write a Parquet table. keep='auto' puts it in the repo when it fits, R2 otherwise."""
        t = df if isinstance(df, pa.Table) else pa.Table.from_pandas(df, preserve_index=False)
        local = self.cache / "processed" / f"{name}.parquet"
        local.parent.mkdir(parents=True, exist_ok=True)
        pq.write_table(t, local, compression="zstd", compression_level=9)
        return self.keep_table(local, name, t.num_rows, t.schema.names, keep=keep, describe=describe)

    def keep_table(self, local: Path, name: str, rows: int, columns: list[str], *, keep="auto", describe="") -> Path:
        size = local.stat().st_size
        if keep == "auto":
            keep = "repo" if size <= REPO_LIMIT else "r2"
        digest = sha256(local)
        if keep == "repo":
            dest = self.out / f"{name}.parquet"
            dest.parent.mkdir(parents=True, exist_ok=True)
            if local != dest:
                local.replace(dest)
            entry = {"location": "repo", "path": str(dest.relative_to(ROOT))}
        else:
            for stale in (self.out / f"{name}.parquet",):
                stale.unlink(missing_ok=True)
            key = f"processed/{self.source}/{name}.parquet"
            r2_put(local, key, digest)
            entry = {"location": "r2", "key": key}
            dest = local
        self.files[f"processed/{name}"] = {
            **entry,
            "sha256": digest,
            "bytes": size,
            "rows": rows,
            "columns": list(columns),
            **({"describe": describe} if describe else {}),
        }
        self.log(f"{name}: {rows:,} rows, {size / 1e6:.1f} MB -> {entry['location']}")
        return dest

    def save(self) -> None:
        import fcntl

        with open(MANIFEST.with_suffix(".lock"), "w") as lock:  # sources may run in parallel
            fcntl.flock(lock, fcntl.LOCK_EX)
            m = read_manifest()
            m["bucket"] = BUCKET
            m["sources"][self.source] = {
                "run": dt.date.today().isoformat(),
                "files": dict(sorted(self.files.items())),
                **({"notes": self.notes} if self.notes else {}),
            }
            write_manifest(m)


# Reading the corpus (for analysis sessions) -------------------------------------------------------------------------


def load(source: str, name: str, **kw) -> pd.DataFrame:
    """A processed table as a DataFrame, from the repo or (downloaded once into the cache) from R2.

    `kw` passes to `pandas.read_parquet` (for example `columns=[...]` or `filters=[...]`).
    """
    m = read_manifest()
    try:
        f = m["sources"][source]["files"][f"processed/{name}"]
    except KeyError as e:
        raise CorpusError(f"no table {source}/{name} in data/manifest.json (see docs/catalogue.md)") from e
    path = ROOT / f["path"] if f["location"] == "repo" else r2_get(f["key"], CACHE / f["key"])
    return pd.read_parquet(path, **kw)


def path(source: str, name: str) -> Path:
    """The local path of a processed table (downloading it from R2 if needed), for DuckDB or Polars."""
    f = read_manifest()["sources"][source]["files"][f"processed/{name}"]
    return ROOT / f["path"] if f["location"] == "repo" else r2_get(f["key"], CACHE / f["key"])


def individual_abns() -> set[str]:
    """ABNs the ABR records as individuals (sole traders), for leaving their names out of repo tables."""
    import duckdb

    abns = path("abr", "abns")
    return {r[0] for r in duckdb.connect().execute(f"SELECT abn FROM '{abns}' WHERE entity_type = 'IND'").fetchall()}


def gcp_credentials() -> Path:
    """The Google Cloud service account key, from `GCP_SERVICE_ACCOUNT_JSON` (the key file's whole contents, as set in
    the environment's settings), written to a private file outside the repo and named in
    GOOGLE_APPLICATION_CREDENTIALS for the BigQuery client. The key never goes in the repo."""
    raw = os.environ.get("GCP_SERVICE_ACCOUNT_JSON")
    if not raw:
        raise CorpusError("BigQuery needs GCP_SERVICE_ACCOUNT_JSON (the key file's contents) in the environment")
    if not raw.lstrip().startswith("{"):  # also accept it base64-encoded
        import base64

        raw = base64.b64decode(raw).decode("utf-8")
    key = json.loads(raw)
    dest = Path.home() / ".config/ipholmes/gcp-service-account.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.touch(mode=0o600, exist_ok=True)
    dest.write_text(json.dumps(key), encoding="utf-8")
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(dest)
    return dest
