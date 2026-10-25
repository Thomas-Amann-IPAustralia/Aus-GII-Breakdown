"""Changes to the IP system, for natural experiments on IP Australia's levers (Q4, Q5), and IP Australia's IP policy
register, an inventory of the levers already proposed and where each stands.

Raw: `events.yaml` (repo; compiled here, with `verify` marking details to confirm) and each policy register page's
HTML (repo, gzipped). Processed: `events` (date, rights, lever, event, source, verify) and `policy_register` (policy
id, title, status, priority, tags, issue summary, comments and URL, as IP Australia publishes them).
"""

from __future__ import annotations

import gzip
import re

import pandas as pd
import yaml

from ..core import CorpusError, Ctx, http_get

SITEMAP = "https://www.ipaustralia.gov.au/sitemap.xml"


def _text(html: str) -> list[str]:
    body = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    return [t.strip() for t in re.sub(r"<[^>]+>", "\n", body).splitlines() if t.strip()]


def _field(lines: list[str], label: str) -> str | None:
    for i, t in enumerate(lines):
        if t.rstrip(":") == label and i + 1 < len(lines):
            return lines[i + 1]
    return None


def _section(lines: list[str], start: str, stops: tuple[str, ...]) -> str | None:
    if start not in lines:
        return None
    i, out = lines.index(start) + 1, []
    while i < len(lines) and lines[i] not in stops:
        out.append(lines[i])
        i += 1
    return " ".join(out) or None


def _events(ctx: Ctx) -> None:
    ev = ctx.raw / "events.yaml"
    ctx.keep_raw(ev)
    events = pd.DataFrame(yaml.safe_load(ev.read_text("utf-8"))["events"])
    if events["id"].duplicated().any():
        raise CorpusError("policy_events: an event id is used twice in events.yaml")
    events["date"] = pd.to_datetime(events["date"]).dt.date
    events["rights"] = events["rights"].map(lambda r: ",".join(r))
    ctx.table(events.sort_values("date").reset_index(drop=True), "events", describe="Dated changes to the IP system")


def reprocess(ctx: Ctx, tables: list[str] | None = None) -> None:
    """`events` again from events.yaml; the policy register (scraped) is left as it is."""
    _events(ctx)


def run(ctx: Ctx) -> None:
    _events(ctx)

    urls = sorted(set(re.findall(r"<loc>([^<]*/policy-register/[^<]+)</loc>", http_get(SITEMAP).text)))
    if len(urls) < 50:
        raise CorpusError(f"policy_events: only {len(urls)} policy register pages in the sitemap")
    rows, pages = [], {}
    for u in urls:
        html = http_get(u).text
        pages[u.rsplit("/", 1)[1]] = html
        lines = _text(html)
        title = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S)
        title = re.sub(r"<[^>]+>|\s+", " ", title.group(1)).strip() if title else None
        pid = _field(lines, "Policy ID")
        status = _field(lines, "Status")
        priority = _field(lines, "Priority")
        tags = []
        if priority and priority in lines:
            i = lines.index(priority) + 1
            while i < len(lines) and lines[i] not in ("Issue summary", "Comments") and len(tags) < 6:
                tags.append(lines[i])
                i += 1
        rows.append(
            {
                "policy_id": int(pid) if pid and pid.isdigit() else None,
                "title": title,
                "status": status,
                "priority": priority,
                "tags": "; ".join(tags),
                "issue_summary": _section(lines, "Issue summary", ("Comments", "Related links", "Share")),
                "comments": _section(lines, "Comments", ("Related links", "Share", "Was this page useful?")),
                "url": u,
            }
        )
    raw = ctx.raw / "policy-register-pages.html.gz"
    with open(raw, "wb") as f, gzip.GzipFile(fileobj=f, mode="wb", mtime=0, filename="") as g:
        g.write("\n<!-- page -->\n".join(f"<!-- {k} -->\n{v}" for k, v in sorted(pages.items())).encode())
    ctx.keep_raw(raw, url=SITEMAP)
    reg = pd.DataFrame(rows).sort_values("policy_id", na_position="last")
    ctx.table(reg, "policy_register", describe="IP Australia's IP policy register")
