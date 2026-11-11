"""Keeping every observation current (analysis/atlas/currency.py, ADR 0058): the gate catches a change the moment it
is made, statuses follow from the judged relations, and nothing leaves the atlas without the owner's approval."""

import copy
import dataclasses

import pytest
from atlas import build, currency


@pytest.fixture(scope="module")
def records():
    nbs, ents = currency._load_all()
    return nbs, ents


def _problems(nbs, ents):
    return currency.gate(nbs, ents)[0]


def test_the_committed_records_pass_the_gate(records):
    assert _problems(*records) == []


def test_every_observation_has_a_review_with_every_pair_judged(records):
    nbs, ents = records
    for oid in ents:
        rv = currency.review(oid)
        assert rv and rv["candidates"], oid
        assert all(c["judgement"] in currency.JUDGEMENTS for c in rv["candidates"]), oid


def test_a_changed_observation_is_caught_at_once(records):
    nbs, ents = records
    nbs = dict(nbs)
    nbs["U8"] = dataclasses.replace(nbs["U8"], plain=nbs["U8"].plain + " A new sentence.")
    problems = _problems(nbs, ents)
    assert any(p.startswith("U8: its check is stale (its own words or reading changed") for p in problems)
    # and every observation that judged a pair with U8 must judge it again
    assert any("U8 changed since the pair was judged" in p for p in problems)


def test_new_outputs_above_an_observation_make_its_check_stale(records):
    nbs, ents = records
    nbs = dict(nbs)
    nbs["B38"] = dataclasses.replace(nbs["B38"], evidence_text=nbs["B38"].evidence_text + "\n6.70%")
    assert any(p.startswith("B38: its check is stale (the outputs above it changed") for p in _problems(nbs, ents))


def test_new_data_under_an_observation_make_its_check_stale(records, monkeypatch):
    nbs, ents = records
    manifest = copy.deepcopy(currency._manifest())
    src = ents["U1"]["sources"][0]
    name = next(n for n in manifest[src]["files"] if n.startswith("processed/"))
    manifest[src]["files"][name]["sha256"] = "0" * 64
    monkeypatch.setattr(currency, "_manifest", lambda: manifest)
    assert any(p.startswith("U1: its check is stale (the data files under it changed") for p in _problems(nbs, ents))


def test_statuses_follow_from_the_judged_relations(records):
    nbs, ents = records
    status = currency.statuses(ents)
    graph = currency.edges(ents)
    for r in graph:
        if r["type"] in currency.RETIRING:
            assert status[r["to"]] in {"proposed", "retired"}
        if r["type"] == "contests":
            assert status[r["from"]] != "current" and status[r["to"]] != "current"
    assert {i for i, s in status.items() if s == "retired"} == {
        x["id"] for x in currency.ledger() if x.get("approved", {}).get("words")
    }


def test_a_proposal_must_be_put_to_the_owner_and_a_contest_must_say_what_would_settle_it(records, monkeypatch):
    nbs, ents = records
    rel = currency.relations()
    bad = rel + [
        {"from": "M1", "to": "U20", "type": "outmodes", "why": "x", "found": "2026-11-11"},
        {"from": "M2", "to": "U36", "type": "contests", "why": "x", "found": "2026-11-11"},
    ]
    monkeypatch.setattr(currency, "relations", lambda: bad)
    problems = _problems(nbs, ents)
    assert any("a proposal to retire U20 needs 'asked'" in p for p in problems)
    assert any("M2 contests U36: a contest needs 'settle'" in p for p in problems)


def test_retiring_needs_the_owners_words_and_the_notebook_note(records, monkeypatch):
    nbs, ents = records
    entry = {"id": "B62", "kind": "outmoded", "by": ["M24"], "why": "x", "approved": {"date": "2026-11-12"}}
    monkeypatch.setattr(currency, "ledger", lambda: [entry])
    problems = _problems(nbs, ents)
    assert "ledger: B62 has no recorded approval (the owner's date and words)" in problems
    assert "ledger: B62's notebook cell needs its dated 'Retired (...)' note" in problems


def test_a_retired_observation_leaves_the_atlas_and_only_its_replacement_may_name_it(records, monkeypatch):
    nbs, ents = records
    approved = {"date": "2026-11-12", "words": "Yes"}
    entry = {"id": "B62", "kind": "outmoded", "by": ["M24"], "why": "x", "approved": approved}
    monkeypatch.setattr(currency, "ledger", lambda: [entry])
    assert currency.statuses(ents)["B62"] == "retired"
    problems, pages = currency.gate(nbs, ents)
    # a summary and another observation's entry must point at the replacement ...
    assert "site.yaml: cites B62, which is retired (cite M24)" in problems
    assert "U122: its entry cites B62, which is retired (cite M24)" in problems
    # ... but its own entry, and the observation that replaced it (which says what it revisits), may name it
    assert not any(p.startswith(("B62:", "M24: its entry")) for p in problems)
    # and pairs judged against it while it stood are not asked for again
    assert not any("B62 changed since the pair was judged" in p or "its pair with B62" in p for p in problems)
    assert [x["id"] for x in pages["retired"]] == ["B62"] and pages["retired"][0]["now"] == ["M24"]
    obs = [{"id": i} for i in ents]
    kept, page, _ = build.keep_current(obs, nbs)
    assert "B62" not in {o["id"] for o in kept} and page["retired"][0]["id"] == "B62"


def test_new_data_cannot_be_cleared_by_checking_again(records, monkeypatch, tmp_path):
    # the outputs are as before, so the cells have not been re-run on the new data: a fresh fingerprint is not enough
    import shutil

    nbs, ents = records
    shutil.copytree(currency.REVIEWS, tmp_path / "reviews")
    monkeypatch.setattr(currency, "REVIEWS", tmp_path / "reviews")
    monkeypatch.setattr(currency, "BRIEF", tmp_path / "reviews" / "BRIEF.md")
    manifest = copy.deepcopy(currency._manifest())
    src = "abs_cabee"
    for f in manifest[src]["files"].values():
        f["sha256"] = "0" * 64
    monkeypatch.setattr(currency, "_manifest", lambda: manifest)
    ids = currency.stale(nbs, ents)
    assert ids and all(src in ents[i]["sources"] for i in ids)
    currency.check(ids, nbs, ents)
    problems = _problems(nbs, ents)
    assert len(problems) == len(ids) and all(f"the data under it changed ({src})" in p for p in problems)
    assert all(c["judgement"] in currency.JUDGEMENTS for i in ids for c in currency.review(i)["candidates"])
    currency.confirm(ids, "cells re-run on the refreshed table; outputs identical")
    assert _problems(nbs, ents) == []


def test_a_new_or_reworded_observation_is_searched_more_widely(records):
    assert currency.K_NEW > currency.K


def test_the_search_finds_the_observations_about_the_same_thing(records):
    nbs, ents = records
    index = currency.Index(nbs, ents)
    top = [h[0] for h in index.rank("patents filed without an attorney are granted less often")[:5]]
    assert {"B6", "M1"} <= set(top)
    near = [h[0] for h in index.neighbours("B38")]
    assert "M35" in near and "U8" in near
