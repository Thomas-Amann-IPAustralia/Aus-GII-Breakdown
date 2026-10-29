"""The evidence atlas (analysis/atlas): its pages are built from the notebook and checked against it."""

import json

import pytest
from atlas import build, notebook


def _pending() -> list[str]:
    """Notebook observations the committed atlas does not have yet: those added while the website waits for the
    owner (OQ19; the data-gaps brief keeps `evidence/` and `analysis/atlas/` as they are until then)."""
    committed = {o["id"] for o in json.loads((build.DATA / "atlas.json").read_text(encoding="utf-8"))["observations"]}
    return [o.id for o in notebook.read() if o.id not in committed]


@pytest.fixture(scope="module")
def atlas():
    pending = _pending()
    if pending:
        pytest.skip(f"the atlas waits for OQ19; the notebook has {len(pending)} newer observations ({pending[0]} on)")
    # strict: a missing observation, an unquoted number, an unknown term or source, or an undrawn chart fails here
    return build.build(strict=True, write=False)


def test_every_notebook_observation_has_a_page(atlas):
    assert [o["id"] for o in atlas["observations"]] == [o.id for o in notebook.read()]


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
