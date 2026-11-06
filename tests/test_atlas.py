"""The evidence atlas (analysis/atlas): its pages are built from the Stage 1, 2 and 3 notebooks and checked against
them."""

import json

import pytest
from atlas import build, notebook


@pytest.fixture(scope="module")
def atlas():
    # strict: a missing observation, an unquoted number, an unknown term or source, or an undrawn chart fails here
    return build.build(strict=True, write=False)


def test_every_notebook_observation_has_a_page(atlas):
    assert [o["id"] for o in atlas["observations"]] == [o.id for o in notebook.read_all()]


def test_each_observation_carries_its_stage(atlas):
    stages = {o["id"]: o["stage"] for o in atlas["observations"]}
    for stage, letter in notebook.LETTER.items():
        assert {i[0] for i, s in stages.items() if s == stage} == {letter}
    assert set(atlas["notebooks"]) == {"1", "2", "3"}


def test_stage_3_pages_link_back_to_what_they_revisit(atlas):
    # Every Stage 3 revisit appears on the earlier page as `later`, with the same verdict, and nothing else does
    by = {o["id"]: o for o in atlas["observations"]}
    sent = {(r["id"], o["id"], r["verdict"]) for o in atlas["observations"] for r in o.get("revisits", [])}
    got = {(o["id"], x["id"], x["verdict"]) for o in atlas["observations"] for x in o.get("later", [])}
    assert sent == got and sent
    assert all(by[m]["stage"] == 3 for _, m, _ in got)
    assert all(v in atlas["verdicts"] for _, _, v in got)
    # every Stage 3 observation that tests a Stage 2 signal says which (the descriptive structure pages may not)
    assert all(o.get("revisits") for o in atlas["observations"] if o["stage"] == 3 and o["strength"] != "descriptive")


def test_committed_pages_are_in_step_with_the_notebook_and_content(atlas):
    committed = json.loads((build.DATA / "atlas.json").read_text(encoding="utf-8"))
    assert committed == json.loads(json.dumps(atlas, ensure_ascii=False)), "run `python -m atlas.build` and commit"


def test_every_observation_names_a_lens_and_a_question(atlas):
    lenses, questions = set(atlas["lenses"]), {q["id"] for q in atlas["questions"]}
    for o in atlas["observations"]:
        assert o["lens"] in lenses, o["id"]
        assert (
            o["questions"] and {q["q"] for q in o["questions"]} <= questions and all(q["how"] for q in o["questions"])
        ), o["id"]


def test_numbers_rule_catches_a_number_the_notebook_does_not_show():
    nb = notebook.Observation(
        id="U1",
        strength="descriptive",
        text="There were 4,368,006 rights (53.5%).",
        cell_id="c",
        cell_index=0,
        section="",
        chapter="",
        evidence_text="",
        charts=[],
    )
    ok = {"headline": "4,368,006 rights", "statement": "53.5% are trade marks", "figures": [], "points": []}
    assert build.check_numbers(ok, nb) == []
    assert build.check_numbers({**ok, "points": ["about 4.4 million"]}, nb) == ["4.4"]
    # a stage's name is not a figure, nor is a chart's styling; a chart's data and a verdict row's figures are
    assert build.check_numbers({**ok, "points": ["Stage 2 found it; Stages 1 and 3 did not"]}, nb) == []
    chart = {"type": "bar", "x": {"values": ["a"]}, "series": [{"name": "s", "colour": 3, "data": [53.5]}]}
    assert build.check_numbers({**ok, "chart": chart}, nb) == []
    assert build.check_numbers({**ok, "chart": {**chart, "series": [{"name": "s", "data": [7.7]}]}}, nb) == ["7.7"]
    row = {"signal": "x", "detail": "-6.1 held", "verdict": "holds"}
    assert build.check_numbers({**ok, "verdicts": [row]}, nb) == ["6.1"]


def test_a_plain_english_reading_may_round_but_not_invent():
    # ADR 0055: the reading's numbers are the page's, rounded, as percentages of shares, scaled, or listed as derived
    nb = notebook.Observation(
        id="U1",
        strength="descriptive",
        text="There were 4,368,006 rights, 82.17% of them patents, a share of 0.346, in FY1990 to FY1993.",
        cell_id="c",
        cell_index=0,
        section="",
        chapter="",
    )
    fine = "About 4.4 million rights, 82% of them patents, 34.6% in all, from 1990–93."
    assert build.check_plain("U1", fine, nb) == []
    wrong = "About 4.5 million rights, 83% of them patents, from 1990–94."
    assert build.check_plain("U1", wrong, nb) == ["83", "94", "4.5"]
    # a derived number passes on its own observation's page only
    assert build.check_plain("M14", "93% more filings", nb) == []
    assert build.check_plain("U1", "93% more filings", nb) == ["93"]


def test_every_observation_leads_with_its_plain_english_reading(atlas):
    # ADR 0055: the reading comes from the notebook; the technical words travel only as `original`, for step 4
    for o in atlas["observations"]:
        assert o["plain"] and "statement" not in o and "points" not in o, o["id"]
        assert o["plain"] not in o["original"], o["id"]


def test_chart_shape_catches_a_label_split_at_its_comma():
    # In a YAML flow list an unquoted "Standard patent, division" is two labels, so the bars no longer line up
    split = {"type": "bar", "x": {"values": ["Standard patent", "division"]}, "series": [{"name": "s", "data": [0.9]}]}
    assert build.chart_shape("U74", split) == ["U74: chart series 's' has 1 values for 2 categories"]
    assert build.chart_shape("U74", {**split, "x": {"values": ["Standard patent, division"]}}) == []


def test_site_lists_of_text_hold_only_text(atlas):
    # A colon followed by a space turns an unquoted YAML list item into a mapping, which the page cannot render
    site = atlas["site"]
    lists = [site["limits"]["assumptions"]] + [site["next"][k] for k in ("puzzles", "owner", "ipa", "after")]
    assert all(isinstance(x, str) for xs in lists for x in xs)
    # Stage 3's two tables (section 8 of the Stage 3 notebook): every cell is text, every id an observation
    ids = {o["id"] for o in atlas["observations"]}
    for row in site["next"]["signals"]:
        assert all(isinstance(row[k], str) for k in ("signal", "strength", "next")) and set(row["ids"]) <= ids
    assert all(isinstance(g[k], str) for g in site["next"]["data_gaps"] for k in ("gap", "why", "source", "cost"))
    # every outcome Stage 3 uses has a plain-English meaning
    assert set(atlas["verdicts"]) <= set(site["verdict_words"])


def _markdown_copies():
    import shutil
    import subprocess

    node = shutil.which("node")
    if not node:
        pytest.skip("node is not installed")
    script = build.ROOT / "analysis" / "atlas" / "markdown_check.mjs"
    out = subprocess.run([node, str(script)], capture_output=True, text=True, check=True).stdout
    return [json.loads(line) for line in out.splitlines()]


def test_each_page_has_a_markdown_copy_with_its_chart_as_a_table(atlas):
    # The "Copy as Markdown" button (evidence/js/markdown.js): every page's copy carries its words, its trail and,
    # for a page with a chart, the chart's numbers as a table, one per view
    by = {o["id"]: o for o in atlas["observations"]}
    copies = _markdown_copies()
    assert [c["id"] for c in copies] == list(by)
    for c in copies:
        o, md = by[c["id"]], c["md"]
        assert md.startswith(f"# {o['id']}: "), o["id"]
        for heading in [
            "## Follow the evidence",
            "### Step 1 of 4",
            "### Step 4 of 4",
            "## Assumptions and limits",
            "## What happens next",
        ]:
            assert heading in md, (o["id"], heading)
        # the observation is the notebook's plain-English reading; its own words close step 4 (ADR 0055)
        assert f"## Observation {o['id']} ({o['strength']})\n\n{o['plain']}" in md, o["id"]
        assert f"**Which gives observation {o['id']}, in the notebook's own words**" in md, o["id"]
        assert ("## For analysts: the notebook's own charts" in md) == bool(o["notebook_charts"]), o["id"]
        assert all(f"[{s['title']}]" in md or s["title"] in md for s in (atlas["sources"][x] for x in o["sources"]))
        assert "[[" not in md and not build._ID.search(md), o["id"]  # the site's markup is turned into Markdown
        assert c["chart"] == bool(o.get("chart")), o["id"]
        if c["chart"]:
            assert "## Chart" in md and all(n > 0 for n in c["rows"]), o["id"]
            # a table's rows: one per category and view, beside the key figures, verdicts and source tables
            assert md.count("\n| ") >= sum(c["rows"]), o["id"]


def _passages():
    import shutil
    import subprocess

    node = shutil.which("node")
    if not node:
        pytest.skip("node is not installed")
    script = build.ROOT / "analysis" / "atlas" / "passages.mjs"
    done = subprocess.run([node, str(script), "--check"], capture_output=True, text=True)
    assert done.returncode == 0, done.stderr  # the committed file is what the script writes now
    path = build.DATA / "passages.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_chat_passages_are_current_and_cover_every_page(atlas):
    # The chat's evidence (analysis/atlas/passages.mjs, ADR 0054): every page split into passages of at most 260 words
    import re

    passages = _passages()
    meta = json.loads((build.DATA / "passages.meta.json").read_text(encoding="utf-8"))
    assert meta["passages"] == len(passages) and meta["built"] == atlas["built"]
    ids = [p["passage_id"] for p in passages]
    assert len(ids) == len(set(ids))
    assert all(len(p["text"].split()) <= meta["word_cap"] for p in passages)
    assert all(p["text"].strip() for p in passages)
    # the site's markup is rendered, and no link or hash survives into the text
    assert not any("[[" in p["text"] or re.search(r"\{[UBM]\d", p["text"]) for p in passages)
    assert not any(re.search(r"\]\(https?:", p["text"]) or re.search(r"\b[0-9a-f]{16,}\b", p["text"]) for p in passages)
    # every observation has a passage in its own "Observation X" section
    statement = {p["observation"] for p in passages if p["section"][0].startswith(f"Observation {p['observation']} (")}
    assert statement == {o["id"] for o in atlas["observations"]}
    # every passage leads to a page the atlas serves (evidence/js/app.js, route())
    obs = {o["id"] for o in atlas["observations"]}
    pages = {"", "stage3", "limits", "next", "audit", "data"}
    pages |= {f"lens/{k}" for k in atlas["lenses"]} | {f"question/{q['id']}" for q in atlas["questions"]}
    pages |= {f"glossary/{t}" for t in atlas["glossary"]} | obs
    for p in passages:
        assert p["url"].startswith(meta["base"] + "#/"), p["passage_id"]
        assert p["url"][len(meta["base"]) + 2 :] in pages, p["passage_id"]
        assert p["kind"] in {"observation", "glossary", "lens", "question", "source", "page"}
        assert set(p["related"]) <= obs


def test_the_chat_calls_only_the_address_its_policy_allows(atlas):
    # "Ask the atlas" (ADR 0054): the page connects to the chat's API and nothing else besides this site
    import re
    from urllib.parse import urlparse

    html = (build.OUT / "index.html").read_text(encoding="utf-8")
    csp = re.search(r'http-equiv="Content-Security-Policy" content="([^"]+)"', html).group(1)
    rules = dict(r.strip().split(" ", 1) for r in csp.split(";") if r.strip())
    api = urlparse(atlas["site"]["chat"]["api"])
    assert api.scheme == "https" and api.path.rstrip("/").endswith("/api/atlas")
    assert rules["connect-src"].split() == ["'self'", f"{api.scheme}://{api.netloc}"]
    assert rules["script-src"] == "'self'" and rules["default-src"] == "'none'"  # nothing else in the policy loosened


def test_the_chat_page_works_in_a_browser():
    # analysis/atlas/chat_check.mjs: the page against a recorded event stream, at 1,366 and 390 pixels
    import shutil
    import subprocess

    node = shutil.which("node")
    fixture = build.ROOT / "analysis" / "atlas" / "fixtures" / "chat-stream.json"
    if not node or not fixture.exists():
        pytest.skip("node or the chat's recorded stream is not here")
    probe = subprocess.run([node, "-e", "require('playwright')"], capture_output=True, cwd=build.ROOT)
    if probe.returncode != 0:
        pytest.skip("Playwright is not installed here")
    done = subprocess.run(
        [node, str(build.ROOT / "analysis" / "atlas" / "chat_check.mjs")], capture_output=True, text=True, timeout=180
    )
    out = json.loads(done.stdout.strip().splitlines()[-1])
    assert out["ok"], out["results"]
