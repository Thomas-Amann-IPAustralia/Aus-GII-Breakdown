"""The refresh report (analysis/atlas/refresh.py, ADR 0059): each quoted number is bound to its place in the outputs
above its observation, and a re-run in a copy shows which moved. Nothing here runs a notebook."""

import copy
import json
import shutil

import pytest
from atlas import currency, notebook, refresh
from eda import fingerprint

TABLE = """<table class="dataframe"><thead>
<tr><th></th><th>filed</th><th>granted (%)</th></tr><tr><th>origin</th><th></th><th></th></tr></thead><tbody>
<tr><th>Australia</th><td>2,345</td><td>54.4</td></tr>
<tr><th>Overseas</th><td>28,798</td><td>69.0</td></tr></tbody></table>"""


def _cell(html: str, cid: str = "c1") -> dict:
    return {"cell_type": "code", "id": cid, "source": "", "outputs": [{"data": {"text/html": html, "text/plain": "x"}}]}


def test_a_place_is_named_by_its_labels_so_new_and_reordered_rows_do_not_move_it():
    before = refresh.places(_cell(TABLE))
    assert before["c1 | table 1 | Overseas | granted (%)"] == "69.0"
    assert before["c1 | table 1 | Australia | filed"] == "2,345"
    rows = TABLE.split("<tbody>")[1].split("</tbody>")[0].strip().split("\n")
    extra = "<tr><th>Unknown</th><td>12</td><td>1.5</td></tr>"
    after = refresh.places(_cell(TABLE.replace("\n".join(rows), "\n".join([extra, rows[1], rows[0]]))))
    assert {k: after[k] for k in before} == before


def test_printed_lines_are_named_by_their_words_with_the_numbers_masked():
    cell = {"cell_type": "code", "id": "c2", "outputs": [{"name": "stdout", "text": "4,356,908 rows, 89 columns\n"}]}
    assert refresh.places(cell) == {"c2 | line | # rows, # columns": "4,356,908 rows, 89 columns"}
    assert refresh.numbers_at("4,356,908 rows, 89 columns") == ["4356908", "89"]


def test_a_quoted_number_fits_a_place_as_written_rounded_as_a_percentage_or_scaled():
    assert refresh._fits("54.4", "54.4") == "exact"
    assert refresh._fits("54.4", "54.3712") == "rounded"
    assert refresh._fits("34.6", "0.346") == "percent"
    assert refresh._fits("214.6", "214600000") == "millions"
    assert refresh._fits("54.4", "55.1") is None
    assert refresh._form("percent", "34.6", "0.351") == "35.1"


def test_old_values_in_dated_notes_and_section_numbers_are_history_not_claims():
    text = (
        "**U1 (descriptive). The table holds 4,356,908 rights (5.4).**\n"
        "- The emptiest column is 28.97% filled.\n"
        "- **Corrected (10 November 2026; ADR 0057):** this said 3,111,222 rights."
    )
    now, past = refresh._spoken(text)
    assert {"4356908", "28.97"} <= now and "3111222" in past and "5.4" in past and "3111222" not in now


def test_most_quoted_numbers_are_bound_to_a_place():
    c = refresh.summary(refresh.bind_all())
    total = sum(v for k, v in c.items() if not k.startswith("history"))
    assert total > 5000
    assert c["untraced"] / total < 0.06
    assert (c["exact, one place"] + c["exact, several places"]) / total > 0.8


@pytest.fixture
def copies(tmp_path, monkeypatch):
    """The reviewed notebooks standing in for a re-run: compared with themselves, nothing has moved."""
    monkeypatch.setattr(refresh, "RUNS", tmp_path)
    for p in notebook.NOTEBOOKS.values():
        shutil.copy(p, tmp_path / p.name)
        meta = {"notebook": p.name, "seconds": 0, "failed_cells": 0, "ran": "2026-11-12T00:00:00"}
        (tmp_path / f"{p.stem}.json").write_text(json.dumps(meta))
    return tmp_path


def test_compared_with_themselves_nothing_moves_except_prose_already_corrected(copies):
    obs = refresh.compare()["observations"]
    assert len(obs) == len(notebook.read_all())
    assert {r["status"] for r in obs.values()} <= {"same"}


def test_a_number_that_changes_in_the_copy_is_reported_where_it_sits(copies):
    path = copies / notebook.NOTEBOOKS[1].name
    nb = json.loads(path.read_text(encoding="utf-8"))
    ev = next(e for e in refresh.evidence(1) if e.obs.id == "U1")
    hit = False
    for c in nb["cells"]:
        if c.get("id") in {x.get("id") for x in ev.cells}:
            for o in c.get("outputs", []):
                if "4,356,908" in "".join(o.get("text", "")):
                    o["text"] = ["".join(o["text"]).replace("4,356,908", "4,400,000")]
                    hit = True
    assert hit
    path.write_text(json.dumps(nb), encoding="utf-8")
    obs = refresh.compare()["observations"]
    assert obs["U1"]["status"] == "moved"
    assert any(m["number"] == "4356908" and m["now"] == ["4400000"] for m in obs["U1"]["moved"])
    assert sum(1 for r in obs.values() if r["status"] != "same") == 1


def test_a_failed_cell_marks_the_observations_under_it(copies):
    path = copies / notebook.NOTEBOOKS[2].name
    nb = json.loads(path.read_text(encoding="utf-8"))
    ev = next(e for e in refresh.evidence(2) if e.obs.id == "B6")
    target = ev.cells[-1]["id"]
    for c in nb["cells"]:
        if c.get("id") == target:
            c["outputs"] = [
                {"output_type": "error", "ename": "CatalogException", "evalue": "no such column", "traceback": []}
            ]
    path.write_text(json.dumps(nb), encoding="utf-8")
    assert refresh.compare()["observations"]["B6"]["status"] == "a cell failed"


# ------------------------------------------------------------------------------------------ the lens fingerprints
def test_the_committed_fingerprints_cover_every_lens_table():
    from eda import build as lens_build

    f = fingerprint.committed()
    assert set(f) == set(lens_build.LENSES)
    assert all(v["rows"] > 0 and v["columns"] for v in f.values())


def test_fingerprint_differences_name_the_lens_and_the_columns():
    old = {"firms": {"rows": 10, "columns": {"abn": "aa", "age": "bb"}}}
    new = copy.deepcopy(old)
    assert fingerprint.differences(new, old) == {}
    new["firms"]["rows"], new["firms"]["columns"]["age"], new["firms"]["columns"]["size"] = 12, "cc", "dd"
    assert fingerprint.differences(new, old) == {
        "firms": {"rows": [10, 12], "added": ["size"], "dropped": [], "changed": ["age"]}
    }


def test_the_built_lens_tables_match_the_committed_fingerprints():
    # where the lens tables are built: a new source or a change to the lens code shows here first
    from eda import data

    if not (data.LENS_DIR / "timeline.parquet").exists():
        pytest.skip("the lens tables are not built here")
    small = {k: fingerprint.of(k) for k in ("timeline", "institutions", "regions", "national")}
    diff = fingerprint.differences(small, {k: fingerprint.committed()[k] for k in small})
    assert diff == {}, "run `python -m eda.fingerprint`, then `python -m atlas.refresh run` and `report`"


def test_a_changed_lens_table_makes_its_observations_wait_for_a_re_run(monkeypatch, tmp_path):
    nbs, ents = currency._load_all()
    shutil.copytree(currency.REVIEWS, tmp_path / "reviews")
    monkeypatch.setattr(currency, "REVIEWS", tmp_path / "reviews")
    monkeypatch.setattr(currency, "BRIEF", tmp_path / "reviews" / "BRIEF.md")
    prints = dict(currency.lens_prints())
    prints["timeline"] = "changed"
    monkeypatch.setattr(currency, "lens_prints", lambda: prints)
    stale = currency.stale(nbs, ents)
    reads = [i for i in ents if "timeline" in currency.lenses_read(nbs[i], ents[i])]
    # every timeline observation, and those on other lenses whose cells read the timeline table (U38, U39)
    assert set(stale) == set(reads) and {i for i in ents if ents[i]["lens"] == "timeline"} <= set(stale)
    problems = currency.gate(nbs, ents)[0]
    assert all("a lens table it reads changed" in p for p in problems)
    currency.check(stale, nbs, ents)
    problems = currency.gate(nbs, ents)[0]
    assert len(problems) == len(stale) and all("(lens timeline)" in p for p in problems)
