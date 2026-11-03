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
