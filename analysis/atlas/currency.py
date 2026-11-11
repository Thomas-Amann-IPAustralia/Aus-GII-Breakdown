"""Keep every observation current: the relation graph, the ledger, the review records and the gate (ADR 0058).

    uv run python -m atlas.currency status              # what is stale, proposed, open or retired
    uv run python -m atlas.currency check M41           # find M41's nearest observations; write its review to judge
    uv run python -m atlas.currency check --stale       # the same for every observation whose review is stale
    uv run python -m atlas.currency search "free text"  # the hybrid search on its own, to explore
    uv run python -m atlas.currency impact B38          # what leans on B38: observations and atlas content
    uv run python -m atlas.currency confirm U5 "why"    # new data under U5, its cells re-run, outputs the same

**The policy.** Every observation the atlas shows must be current. When an observation is added or changed, or the
data or evidence under it change, it is compared at once with the observations nearest to it, and each pair is
judged (`JUDGEMENTS`). A judgement other than "none" is a typed relation in `content/relations.yaml`:

- `supports`: agrees with it, and adds weight;
- `refines`: sharpens or narrows it, which stays true (its page says how);
- `contests`: the two point different ways without settling it: an area for further exploration, with what would
  settle it (`settle`);
- `outmodes`: gives a clearer statement of the same thing, so the other is no longer the best one;
- `disproves`: shows the other is wrong.

An observation that is outmoded or disproved is *proposed for retirement*: its page says so at once, at the top, and
the owner is asked (`asked`, an open question in `docs/owner-questions.md`). Only the owner's approval, recorded in
`content/ledger.yaml` with their words, retires it; the atlas then drops it from every list, search and the chat's
evidence, and its address shows the ledger's entry and what replaced it. Nothing is removed without that approval.

**Statuses** are derived, never written by hand: `retired` (in the ledger, approved), `proposed` (outmoded or
disproved, awaiting approval), `open` (contested), `current`.

**The gate** (run by `atlas.build`, so the strict build and the tests fail): every observation has a review whose
fingerprint matches what it now rests on (its own words and reading, the outputs above it, its data files, and the
words and status of every observation it cites), every candidate in it is judged, each pair judged against a
candidate as it now reads, and every relation, proposal and retirement is complete. New data under an observation
whose outputs are unchanged need its cells re-run, or a recorded reason it is unaffected (`confirm`); a fresh
fingerprint alone does not clear it. Atlas content may not lean on a retired observation: only its own entry and the
observations that replaced it may name it.

**Finding the candidates** fuses rankings by reciprocal rank (`search`): keywords (BM25 over the headline, the
reading and the notebook's words), meaning read two ways (a latent semantic index from scikit-learn, always; and a
small local embedding model, model2vec's potion-retrieval-32M, free, when it is installed), and structure (the
columns the evidence names, the sources, terms and lens). Observations linked explicitly (one cites the other, a
Stage 3 revisit, `related`) are always candidates.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

import yaml

from . import notebook

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CONTENT = HERE / "content"
RELATIONS = CONTENT / "relations.yaml"
LEDGER = CONTENT / "ledger.yaml"
REVIEWS = HERE / "reviews"
BRIEF = REVIEWS / "BRIEF.md"  # the latest check's reading list, for the judge (gitignored)
QUESTIONS = ROOT / "docs" / "owner-questions.md"

TYPES = ["supports", "refines", "contests", "outmodes", "disproves"]
RETIRING = {"outmodes", "disproves"}
JUDGEMENTS = ["none", *TYPES]
# Stage 3's verdicts that settle the relation to the page revisited without a judgement; every other verdict
# (reversed, not detected, does not replicate, appears once held, mixed) needs one in relations.yaml
DERIVED = {"holds": "supports", "weakened": "refines", "refined": "refines"}
# Candidates from the search, besides the explicit links. Measured on the 69 known relations (11 November 2026):
# searching from the later observation alone, the other is in its top 8 for 91% and its top 12 for 99%. A new or
# reworded observation is searched from its own side only, so it takes 12 (K_NEW). A re-check for another reason (its
# data, or an observation it cites) keeps the pairs it has: a newer neighbour was searched from its own side, and the
# pair is mirrored. K is the baseline's width, and how near the top a ranking must put a hit to be named.
K = 8
K_NEW = 12
KINDS = {"outmodes": "outmoded", "disproves": "disproven"}

_ID = re.compile(r"\b([UBM]\d+)\b")
_SNAKE = re.compile(r"\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b")
_WORD = re.compile(r"[a-z][a-z'-]+")
_STOP = set(
    """the and for with that this from are was were has have had not but its their they them than then there these
    those which who whom what when where while into onto over under about after before also each every more most less
    least other some such only same both all any can may might could would should will one two three four five per
    out off our his her him she does did doing done been being very much many few how why own just like near far
    between among within without across against through during until since upon whether either neither nor yet
    observation observations stage notebook reading plain english held holds shows show shown figure figures""".split()
)


# --------------------------------------------------------------------------------------------- loading the records
def _iso(x):
    """Dates as ISO text, so the records travel into atlas.json as written."""
    if isinstance(x, dt.date):
        return x.isoformat()
    if isinstance(x, dict):
        return {k: _iso(v) for k, v in x.items()}
    if isinstance(x, list):
        return [_iso(v) for v in x]
    return x


def _load(path: Path) -> list:
    return _iso(yaml.safe_load(path.read_text(encoding="utf-8")) or []) if path.exists() else []


def relations() -> list[dict]:
    return _load(RELATIONS)


def ledger() -> list[dict]:
    return _load(LEDGER)


def review(oid: str) -> dict | None:
    p = REVIEWS / f"{oid}.yaml"
    return yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else None


def _dump(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=118)
    path.write_text(text, encoding="utf-8")


def entries() -> dict[str, dict]:
    """Every observation's plain-English entry (the YAML), by id, as written."""
    out = {}
    for folder in ["", "stage2", "stage3"]:
        for p in sorted((CONTENT / "observations" / folder).glob("*.yaml")):
            for o in yaml.safe_load(p.read_text(encoding="utf-8")) or []:
                out[o["id"]] = o
    return out


def open_questions() -> set[str]:
    """The owner questions still open (above the "Answered" heading)."""
    if not QUESTIONS.exists():
        return set()
    text = QUESTIONS.read_text(encoding="utf-8").split("\n## Answered", 1)[0]
    return set(re.findall(r"^\| (OQ\d+) \|", text, re.M))


# ---------------------------------------------------------------------------------------------------- the graph
def edges(ents: dict[str, dict]) -> list[dict]:
    """The explicit relations, then those Stage 3's revisits settle on their own (an explicit one wins)."""
    out = [dict(r, origin="judged") for r in relations()]
    have = {frozenset((r["from"], r["to"])) for r in out}
    for oid, e in ents.items():
        for r in e.get("revisits", []) or []:
            t = DERIVED.get(r.get("verdict"))
            if t and frozenset((oid, r["id"])) not in have:
                out.append({"from": oid, "to": r["id"], "type": t, "why": r.get("what", ""), "origin": "revisit"})
    return out


def statuses(ents: dict[str, dict], graph: list[dict] | None = None) -> dict[str, str]:
    """current, open (contested), proposed (outmoded or disproved, awaiting approval) or retired (approved)."""
    graph = edges(ents) if graph is None else graph
    retired = {x["id"] for x in ledger() if (x.get("approved") or {}).get("words")}
    out = dict.fromkeys(ents, "current")
    for r in graph:
        if r["type"] == "contests":
            for side in (r["from"], r["to"]):
                if out.get(side) == "current":
                    out[side] = "open"
    for r in graph:
        if r["type"] in RETIRING and r["to"] in out:
            out[r["to"]] = "proposed"
    for oid in retired:
        if oid in out:
            out[oid] = "retired"
    return out


def cites(nb: notebook.Observation, e: dict) -> set[str]:
    """The observations this one names: in its own words, its reading, its entry, its revisits and `related`."""
    text = " ".join([nb.text, nb.plain, json.dumps(e, ensure_ascii=False)])
    found = set(_ID.findall(text)) | {r["id"] for r in e.get("revisits", []) or []} | set(e.get("related") or [])
    return found - {nb.id}


def replacement(oid: str, graph: list[dict], status: dict[str, str]) -> list[str]:
    """The current observations that replace a proposed or retired one, following a chain of replacements."""
    seen, todo, out = {oid}, [oid], []
    while todo:
        x = todo.pop()
        for r in graph:
            if r["type"] in RETIRING and r["to"] == x and r["from"] not in seen:
                seen.add(r["from"])
                (todo if status.get(r["from"]) in {"proposed", "retired"} else out).append(r["from"])
    return sorted(out)


# --------------------------------------------------------------------------------------------- the fingerprints
def _h(*parts: str) -> str:
    return hashlib.sha256("\x1f".join(re.sub(r"\s+", " ", p).strip() for p in parts).encode()).hexdigest()[:12]


def text_hash(nb: notebook.Observation) -> str:
    return _h(nb.text, nb.plain)


def _manifest() -> dict:
    p = ROOT / "data" / "manifest.json"
    return json.loads(p.read_text())["sources"] if p.exists() else {}


def source_hashes(e: dict, manifest: dict) -> dict[str, str]:
    """Each of an observation's sources with a hash of its processed files, to say which one changed."""
    out = {}
    for s in sorted(e.get("sources") or []):
        files = manifest.get(s, {}).get("files", {})
        out[s] = _h(*[f"{n}:{f.get('sha256', '')}" for n, f in sorted(files.items()) if n.startswith("processed/")])
    return out


def fingerprint(nb, e, nbs, status, manifest) -> dict:
    """What a review rests on. A change to any part makes the review stale."""
    data = []
    for s in sorted(e.get("sources") or []):
        files = manifest.get(s, {}).get("files", {})
        data += [f"{s}:{n}:{f.get('sha256', '')}" for n, f in sorted(files.items()) if n.startswith("processed/")]
    linked = []
    for c in sorted(cites(nb, e)):
        if c in nbs:  # a cited observation's words, and whether it is still standing
            linked.append(f"{c}:{text_hash(nbs[c])}:{'down' if status.get(c) in {'proposed', 'retired'} else 'up'}")
    return {
        "text": text_hash(nb),
        "evidence": _h(nb.evidence_text),
        "data": _h(*data),
        "links": _h(*linked),
    }


PARTS = {
    "text": "its own words or reading changed",
    "evidence": "the outputs above it changed",
    "data": "the data files under it changed",
    "links": "an observation it cites changed, or was proposed for retirement",
}


# ------------------------------------------------------------------------------------------------------ the search
def _stem(w: str) -> str:
    for suf in ("ings", "ing", "ies", "ed", "es", "s"):
        if len(w) > len(suf) + 3 and w.endswith(suf):
            return w[: -len(suf)] + ("y" if suf == "ies" else "")
    return w


def tokens(text: str) -> list[str]:
    text = re.sub(r"\[\[([^\]|]+)\|?([^\]]*)\]\]", r"\2 \1", text.lower())
    return [_stem(w.strip("'-")) for w in _WORD.findall(text) if len(w) > 2 and w not in _STOP]


def document(nb: notebook.Observation, e: dict) -> str:
    return " ".join([e.get("headline", ""), e.get("headline", ""), nb.plain, nb.text])


class Index:
    """The hybrid search over the observations: keywords, meaning and structure, fused by reciprocal rank."""

    def __init__(self, nbs: dict, ents: dict, skip: set[str] = frozenset()):
        self.ids = [i for i in nbs if i in ents and i not in skip]
        self.nbs, self.ents = nbs, ents
        docs = [tokens(document(nbs[i], ents[i])) for i in self.ids]
        self.tf = [Counter(d) for d in docs]
        self.len = [len(d) for d in docs]
        self.avg = sum(self.len) / max(len(self.len), 1)
        df = Counter(w for d in self.tf for w in d)
        n = len(docs)
        self.idf = {w: math.log(1 + (n - c + 0.5) / (c + 0.5)) for w, c in df.items()}
        self.cols = [self._columns(i) for i in self.ids]
        cdf = Counter(c for s in self.cols for c in s)
        self.cidf = {c: math.log(n / k) for c, k in cdf.items()}
        self.method, self.vec = self._vectors([document(nbs[i], ents[i]) for i in self.ids])

    def _columns(self, oid: str) -> set[str]:
        nb, e = self.nbs[oid], self.ents[oid]
        snake = set(_SNAKE.findall(nb.text + "\n" + nb.evidence_text))
        tags = {f"src:{s}" for s in e.get("sources") or []} | {f"term:{t}" for t in e.get("terms") or []}
        tags |= {f"term:{t}" for t in re.findall(r"\[\[([^\]|]+)", json.dumps(e, ensure_ascii=False))}
        return snake | tags | {f"lens:{e.get('lens')}"}

    def _vectors(self, docs: list[str]):
        """Two readings of meaning: a latent semantic index (always), and a small embedding model if it is installed.
        On the 72 known relations (11 November 2026) the two together put the other observation in the top 8 for 96%
        and the top 12 for 99%; keywords alone, 90% and 92%; the embedding model alone, 83% and 92%."""
        import numpy as np
        from sklearn.decomposition import TruncatedSVD
        from sklearn.feature_extraction.text import TfidfVectorizer

        def unit(v):
            return v / np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-9)

        self._unit = unit
        self._tfidf = TfidfVectorizer(tokenizer=tokens, lowercase=False, token_pattern=None)
        x = self._tfidf.fit_transform(docs)
        self._svd = TruncatedSVD(n_components=max(2, min(100, x.shape[1] - 1, len(docs) - 1)), random_state=0)
        self.topics = unit(self._svd.fit_transform(x))
        try:
            from model2vec import StaticModel

            self._model = StaticModel.from_pretrained("minishlab/potion-retrieval-32M")
            vec, method = unit(np.asarray(self._model.encode(docs))), "model2vec potion-retrieval-32M and a "
        except Exception:  # not installed or not reachable: the latent semantic index alone
            self._model, vec, method = None, None, ""
        return method + "latent semantic index", vec

    def _embed(self, text: str):
        import numpy as np

        return None if self._model is None else self._unit(np.asarray(self._model.encode([text]))[0])

    def bm25(self, q: list[str]) -> list[float]:
        k1, b, out = 1.4, 0.75, []
        for tf, n in zip(self.tf, self.len, strict=True):
            s = 0.0
            for w in set(q):
                f = tf.get(w, 0)
                if f:
                    s += self.idf.get(w, 0) * f * (k1 + 1) / (f + k1 * (1 - b + b * n / self.avg))
            out.append(s)
        return out

    def rank(self, query: str, cols: set[str] | None = None, vec=None, row=None) -> list[tuple[str, float, list[str]]]:
        """Every observation, best first, with its fused score and the rankings that put it near the top."""
        lists = {"keywords": self.bm25(tokens(query))}
        vec = self._embed(query) if vec is None else vec
        if vec is not None and self.vec is not None:
            lists["meaning"] = list(self.vec @ vec)
        topic = (
            self.topics[row] if row is not None else self._unit(self._svd.transform(self._tfidf.transform([query]))[0])
        )
        lists["topics"] = list(self.topics @ topic)
        if cols:
            lists["columns"] = [sum(self.cidf[c] for c in cols & s) for s in self.cols]
        fused = [0.0] * len(self.ids)
        near: list[list[str]] = [[] for _ in self.ids]
        for name, scores in lists.items():
            order = sorted(range(len(scores)), key=lambda i: -scores[i])
            for r, i in enumerate(order):
                if scores[i] <= 0:
                    break
                fused[i] += 1 / (60 + r)
                if r < 2 * K:
                    near[i].append(name)
        order = sorted(range(len(fused)), key=lambda i: -fused[i])
        return [(self.ids[i], round(fused[i] * 1000, 2), near[i]) for i in order]

    def neighbours(self, oid: str, k: int = K) -> list[tuple[str, float, list[str]]]:
        i = self.ids.index(oid) if oid in self.ids else None
        nb, e = self.nbs[oid], self.ents[oid]
        vec = self.vec[i] if i is not None and self.vec is not None else None
        cols = self._columns(oid)
        hits = [h for h in self.rank(document(nb, e), cols, vec, i) if h[0] != oid]
        return hits[:k]


# ------------------------------------------------------------------------------------------------------- the gate
def gate(nbs: dict, ents: dict) -> tuple[list[str], dict]:
    """The problems that stop the strict build, and what the pages need: each observation's status and relations."""
    problems: list[str] = []
    graph = edges(ents)
    status = statuses(ents, graph)
    manifest = _manifest()
    asked = open_questions()
    led = {x["id"]: x for x in ledger()}

    for r in relations():
        tag = f"relation {r.get('from')} {r.get('type')} {r.get('to')}"
        if r.get("from") not in nbs or r.get("to") not in nbs or r.get("from") == r.get("to"):
            problems.append(f"{tag}: names an observation that does not exist, or itself")
        if r.get("type") not in TYPES:
            problems.append(f"{tag}: the type must be one of {TYPES}")
        if not r.get("why") or not r.get("found"):
            problems.append(f"{tag}: needs 'why' (one plain sentence) and 'found' (the date)")
        if r.get("type") == "contests" and not r.get("settle"):
            problems.append(f"{tag}: a contest needs 'settle', what would settle it")
        if r.get("type") in RETIRING and r.get("to") not in led and r.get("asked") not in asked:
            problems.append(f"{tag}: a proposal to retire {r.get('to')} needs 'asked', an open question to the owner")
    pairs = [frozenset((r.get("from"), r.get("to"))) for r in relations()]
    problems += [
        f"relations: {' and '.join(sorted(p))} are related twice" for p in {p for p in pairs if pairs.count(p) > 1}
    ]

    judged = {frozenset((r["from"], r["to"])) for r in relations()}
    for oid, e in ents.items():
        for r in e.get("revisits", []) or []:
            if r.get("verdict") not in DERIVED and frozenset((oid, r["id"])) not in judged:
                problems.append(
                    f"{oid}: its revisit of {r['id']} ({r.get('verdict')}) needs a judged relation in relations.yaml"
                )

    for oid, x in led.items():
        ap = x.get("approved") or {}
        if oid not in nbs:
            problems.append(f"ledger: {oid} is not an observation")
            continue
        if x.get("kind") not in KINDS.values() or not x.get("by") or not x.get("why"):
            problems.append(f"ledger: {oid} needs kind ({'/'.join(KINDS.values())}), 'by' and 'why'")
        if not (ap.get("date") and ap.get("words")):
            problems.append(f"ledger: {oid} has no recorded approval (the owner's date and words)")
        if not re.search(r"Retired \(\d{1,2} \w+ \d{4}", nbs[oid].text):
            problems.append(f"ledger: {oid}'s notebook cell needs its dated 'Retired (...)' note")
        for b in x.get("by") or []:
            if b not in nbs:
                problems.append(f"ledger: {oid} is replaced by {b}, which is not an observation")

    for oid, nb in nbs.items():
        if oid not in ents or status.get(oid) == "retired":
            continue
        rv = review(oid)
        if not rv:
            problems.append(
                f"{oid}: never checked against the other observations (python -m atlas.currency check {oid})"
            )
            continue
        fp = fingerprint(nb, ents[oid], nbs, status, manifest)
        why = [PARTS[k] for k in PARTS if (rv.get("fingerprint") or {}).get(k) != fp[k]]
        if why:
            problems.append(f"{oid}: its check is stale ({'; '.join(why)}): python -m atlas.currency check {oid}")
            continue
        d = rv.get("data") or {}
        if d and not (d.get("confirmed") or {}).get("how"):
            which = ", ".join(d.get("changed") or ["a source"])
            problems.append(
                f"{oid}: the data under it changed ({which}) and the outputs above it are as before: re-run its"
                f" cells, then `python -m atlas.currency check {oid}`; or, if they were re-run and came out the"
                f' same, or it cannot be affected, `python -m atlas.currency confirm {oid} "why"`'
            )
        for c in rv.get("candidates", []):
            if c.get("judgement") not in JUDGEMENTS:
                problems.append(f"{oid}: its pair with {c.get('id')} is not judged")
            elif status.get(c["id"]) == "retired":
                continue  # judged while it stood; the ledger is its record now
            elif c["id"] in nbs and c.get("seen") != text_hash(nbs[c["id"]]):
                problems.append(
                    f"{oid}: {c['id']} changed since the pair was judged: python -m atlas.currency check {oid}"
                )
            elif c["judgement"] != "none" and c.get("judgement") != _pair_type(graph, oid, c["id"]):
                problems.append(f"{oid}: judged '{c['judgement']}' with {c['id']}, but relations.yaml does not say so")

    problems += leaning(ents, graph, status, led)

    pages = _pages(nbs, ents, graph, status, led)
    return problems, pages


def leaning(ents: dict, graph: list[dict], status: dict, led: dict) -> list[str]:
    """Atlas content that still leans on a retired observation. Its own entry may name it, and so may the
    observations that replaced it (they say what they replaced); the ledger and the graph are its history.
    Everything else (another observation's entry, a summary, an early signal) must cite its replacement."""
    retired = {i for i, s in status.items() if s == "retired"}
    if not retired:
        return []
    problems = []
    now = {r: ", ".join(replacement(r, graph, status)) or "its replacement" for r in retired}
    by = {r: set(led[r].get("by") or []) for r in retired}
    for oid, e in ents.items():
        if oid in retired:
            continue
        for ref in sorted(retired & set(_ID.findall(json.dumps(e, ensure_ascii=False)))):
            if oid not in by[ref]:
                problems.append(f"{oid}: its entry cites {ref}, which is retired (cite {now[ref]})")
    for p in sorted(CONTENT.glob("*.yaml")):  # the site's own pages: summaries, signals, the audit, lenses
        if p in {RELATIONS, LEDGER}:
            continue
        for ref in sorted(retired & set(_ID.findall(p.read_text(encoding="utf-8")))):
            problems.append(f"{p.name}: cites {ref}, which is retired (cite {now[ref]})")
    return problems


def _pair_type(graph, a, b) -> str | None:
    for r in graph:
        if {r["from"], r["to"]} == {a, b}:
            return r["type"]
    return None


def _pages(nbs, ents, graph, status, led) -> dict:
    """What the atlas shows: each observation's status and relations, the ledger, proposals and open questions."""
    rel: dict[str, list] = {}
    for r in graph:
        for me, other, way in ((r["from"], r["to"], "out"), (r["to"], r["from"], "in")):
            rel.setdefault(me, []).append(
                {
                    k: v
                    for k, v in {
                        "id": other,
                        "type": r["type"],
                        "way": way,
                        "why": r.get("why"),
                        "settle": r.get("settle"),
                        "asked": r.get("asked"),
                        "origin": r["origin"],
                        "found": r.get("found"),
                    }.items()
                    if v
                }
            )
    proposals = [
        {
            "id": r["to"],
            "by": r["from"],
            "type": r["type"],
            "why": r.get("why", ""),
            "asked": r.get("asked"),
            "found": r.get("found"),
        }
        for r in graph
        if r["type"] in RETIRING and status.get(r["to"]) == "proposed"
    ]
    contests = [
        {"a": r["from"], "b": r["to"], "why": r.get("why", ""), "settle": r.get("settle", ""), "found": r.get("found")}
        for r in graph
        if r["type"] == "contests" and "retired" not in (status.get(r["from"]), status.get(r["to"]))
    ]
    retired = []
    for oid, x in led.items():
        if status.get(oid) != "retired":
            continue
        e = ents.get(oid, {})
        retired.append(
            {
                "id": oid,
                "headline": e.get("headline", ""),
                "lens": e.get("lens"),
                "stage": nbs[oid].stage,
                "plain": nbs[oid].plain,
                "kind": x["kind"],
                "by": x["by"],
                "why": x["why"],
                "now": replacement(oid, graph, status) or x["by"],
                "proposed": x.get("proposed"),
                "approved": x["approved"],
            }
        )
    counts = Counter(status.values())
    return {
        "status": status,
        "relations": rel,
        "proposals": proposals,
        "contests": contests,
        "retired": retired,
        "counts": {k: counts.get(k, 0) for k in ("current", "open", "proposed", "retired")},
        "relation_counts": dict(Counter(r["type"] for r in graph)),
    }


# ----------------------------------------------------------------------------------------------------- the check
def _load_all():
    nbs = {o.id: o for o in notebook.read_all()}
    return nbs, entries()


def stale(nbs, ents) -> list[str]:
    problems, _ = gate(nbs, ents)
    out = []
    for p in problems:
        m = re.match(r"([UBM]\d+): ", p)
        if m and m.group(1) not in out and ("atlas.currency check" in p or "not judged" in p):
            out.append(m.group(1))
    return out


def check(ids: list[str], nbs=None, ents=None, k: int | None = None) -> Path:
    """Write each observation's review with its candidates (judged pairs that still stand are kept), and a brief."""
    nbs, ents = (nbs, ents) if nbs else _load_all()
    graph = edges(ents)
    status = statuses(ents, graph)
    manifest = _manifest()
    skip = {i for i, s in status.items() if s == "retired"}
    index = Index(nbs, ents, skip)
    brief = [f"# Currency check, {dt.date.today().isoformat()}\n", f"Search: keywords, {index.method}, columns.\n"]
    for oid in ids:
        nb, e = nbs[oid], ents[oid]
        fp = fingerprint(nb, e, nbs, status, manifest)
        old = review(oid) or {}
        same_self = (old.get("fingerprint") or {}).get("text") == fp["text"] and (old.get("fingerprint") or {}).get(
            "evidence"
        ) == fp["evidence"]
        kept = {c["id"]: c for c in old.get("candidates", [])}
        if k or not (old and same_self):  # new, or its own words or outputs changed: search afresh
            found = {h[0]: (h[1], h[2]) for h in index.neighbours(oid, k or K_NEW)}
        else:  # stale for another reason (its data, or an observation it cites): the pairs it has are the pairs
            found = {
                cid: (c.get("score", 0.0), list(c.get("found") or ["search"]))
                for cid, c in kept.items()
                if cid in nbs and cid not in skip
            }
        for c in sorted(cites(nb, e) | _linked(oid, ents)):
            if c in nbs and c not in skip and c not in found:
                found[c] = (0.0, ["cited"])
            elif c in found and "cited" not in found[c][1]:
                found[c][1].append("cited")
        cands = []
        for cid, (score, why) in found.items():
            seen = text_hash(nbs[cid])
            prior = kept.get(cid)
            mirror = _mirror(cid, oid, fp["text"], seen)
            c = {"id": cid, "found": why or ["search"], "score": score, "seen": seen}
            if prior and same_self and prior.get("seen") == seen and prior.get("judgement") in JUDGEMENTS:
                c["judgement"], c["note"] = prior["judgement"], prior.get("note", "")
            elif mirror:
                c["judgement"], c["note"] = mirror
            else:
                c["judgement"] = None
                if prior and prior.get("judgement"):
                    c["was"] = prior["judgement"]
            cands.append(c)
        rv = {
            "id": oid,
            "checked": dt.date.today().isoformat(),
            "search": index.method,
            "fingerprint": fp,
            "sources": source_hashes(e, manifest),
            "candidates": cands,
        }
        if old.get("basis"):
            rv["basis"] = old["basis"]
        # New data under an observation whose outputs are as before: a fresh fingerprint must not paper over it.
        # The cells are re-run (the outputs change, and every pair is judged again) or the reason it is
        # unaffected is recorded (`confirm`).
        old_fp = old.get("fingerprint") or {}
        if old_fp and old_fp.get("data") != fp["data"] and old_fp.get("evidence") == fp["evidence"]:
            was = old.get("sources") or {}
            changed = [s for s, h in rv["sources"].items() if was.get(s) != h] if was else list(rv["sources"])
            rv["data"] = {"changed": changed or list(rv["sources"]), "found": rv["checked"], "confirmed": None}
        elif old.get("data") and old_fp.get("data") == fp["data"] and old_fp.get("evidence") == fp["evidence"]:
            rv["data"] = old["data"]
        _dump(REVIEWS / f"{oid}.yaml", rv)
        brief.append(_brief(oid, nbs, ents, status, graph, cands))
    BRIEF.write_text("\n".join(brief), encoding="utf-8")
    return BRIEF


def confirm(ids: list[str], how: str) -> None:
    """Record why new data leave an observation as it stands: its cells re-run with the same outputs, or a reason."""
    for oid in ids:
        rv = review(oid)
        if not rv or not rv.get("data"):
            sys.exit(f"{oid}: no data change is waiting on it (run `check {oid}` first)")
        rv["data"]["confirmed"] = {"date": dt.date.today().isoformat(), "how": how}
        _dump(REVIEWS / f"{oid}.yaml", rv)


def _linked(oid: str, ents: dict) -> set[str]:
    """Observations that cite this one, or are related to it in the graph."""
    out = set()
    for other, e in ents.items():
        if other != oid and re.search(rf"\b{oid}\b", json.dumps(e, ensure_ascii=False)):
            out.add(other)
    for r in relations():
        if oid in (r["from"], r["to"]):
            out.add(r["to"] if r["from"] == oid else r["from"])
    return out


def _mirror(cid: str, oid: str, own_text: str, cand_text: str):
    """The same pair judged from the other side, if neither has changed since: the judgement and note, mirrored."""
    rv = review(cid)
    if not rv or (rv.get("fingerprint") or {}).get("text") != cand_text:
        return None
    for c in rv.get("candidates", []):
        if c["id"] == oid and c.get("seen") == own_text and c.get("judgement") in JUDGEMENTS:
            return c["judgement"], f"(judged in {cid}'s review) {c.get('note', '')}".strip()
    return None


def _brief(oid, nbs, ents, status, graph, cands) -> str:
    nb, e = nbs[oid], ents[oid]
    out = [
        f"\n## {oid} ({nb.strength}; Stage {nb.stage}; {status[oid]}): {e['headline']}\n",
        f"Reading: {nb.plain}\n",
        "Own words:\n",
        nb.text,
        "\n### Candidates\n",
    ]
    for c in cands:
        o, oe = nbs[c["id"]], ents[c["id"]]
        r = _pair_type(graph, oid, c["id"])
        mark = f" [judged: {c['judgement']}]" if c.get("judgement") else (f" [was {c['was']}]" if c.get("was") else "")
        out.append(
            f"- **{c['id']}** (Stage {o.stage}, {o.strength}, {status[c['id']]}; found by {', '.join(c['found'])}"
            f"{'; relation: ' + r if r else ''}){mark}: {oe['headline']}. {o.plain}"
        )
    return "\n".join(out)


def impact(oid: str, nbs=None, ents=None) -> list[str]:
    """What leans on an observation: observations that cite it or are related to it, and atlas content that names it."""
    nbs, ents = (nbs, ents) if nbs else _load_all()
    out = [f"observation {o}" for o in sorted(_linked(oid, ents))]
    out += [
        f"observation {o} (its notebook words)"
        for o, nb in nbs.items()
        if o != oid and re.search(rf"\b{oid}\b", nb.text)
    ]
    for p in sorted(CONTENT.glob("*.yaml")):
        if p not in {RELATIONS, LEDGER} and re.search(rf"\b{oid}\b", p.read_text(encoding="utf-8")):
            out.append(f"content/{p.name}")
    return sorted(set(out))


def report(nbs=None, ents=None) -> str:
    nbs, ents = (nbs, ents) if nbs else _load_all()
    problems, pages = gate(nbs, ents)
    c = pages["counts"]
    lines = [
        f"{len(ents)} observations: {c['current']} current, {c['open']} open (contested), {c['proposed']} proposed for"
        f" retirement, {c['retired']} retired.",
        f"Relations: {pages['relation_counts']}.",
    ]
    for p in pages["proposals"]:
        lines.append(f"  proposed: {p['id']} {KINDS[p['type']]} by {p['by']} (asked {p.get('asked')}): {p['why']}")
        lines += [f"    leans on it: {x}" for x in impact(p["id"], nbs, ents)]
    for p in pages["contests"]:
        lines.append(f"  open: {p['a']} and {p['b']}: {p['settle']}")
    lines.append(f"{len(problems)} problems" + (":" if problems else "."))
    lines += [f"  - {p}" for p in problems[:60]]
    if len(problems) > 60:
        lines.append(f"  ... and {len(problems) - 60} more")
    return "\n".join(lines)


def main(argv: list[str]) -> None:
    cmd, rest = (argv[0], argv[1:]) if argv else ("status", [])
    if cmd == "status":
        print(report())
    elif cmd == "check":
        nbs, ents = _load_all()
        ids = stale(nbs, ents) if rest in ([], ["--stale"]) else [i for i in rest if not i.startswith("--")]
        unknown = [i for i in ids if i not in ents]
        if unknown:
            sys.exit(f"Not observations: {unknown}")
        if not ids:
            print("Nothing to check: every review is current.")
            return
        path = check(ids, nbs, ents)
        open_ = sum(1 for i in ids for c in review(i)["candidates"] if c.get("judgement") is None)
        print(f"{len(ids)} reviewed ({', '.join(ids[:20])}{' ...' if len(ids) > 20 else ''}); {open_} pairs to judge.")
        print(
            f"Read {path.relative_to(ROOT)}, judge each pair in analysis/atlas/reviews/<id>.yaml, and add a relation to"
        )
        print("content/relations.yaml for each judgement other than 'none' (ADR 0058).")
    elif cmd == "confirm":
        if len(rest) < 2 or len(rest[-1].split()) < 3:
            sys.exit('confirm <ids...> "what was done, in a sentence" (for example: cells re-run, outputs identical)')
        confirm(rest[:-1], rest[-1])
        print(f"{len(rest) - 1} confirmed: {rest[-1]}")
    elif cmd == "search":
        nbs, ents = _load_all()
        idx = Index(nbs, ents)
        for oid, score, why in idx.rank(" ".join(rest))[: K * 2]:
            print(f"{oid:5} {score:6.2f} {','.join(why):24} {ents[oid]['headline']}")
    elif cmd == "impact":
        for x in impact(rest[0]):
            print(x)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
