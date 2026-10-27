"""The audit against IP Australia's published figures (analysis/audit, ADR 0024)."""

import re

import pandas as pd
import pytest
from audit import benchmark
from eda import data


@pytest.fixture(scope="module")
def published():
    return pd.read_csv(benchmark.PUBLISHED)


def test_every_published_figure_has_a_lens_query_a_source_and_an_observation(published):
    assert set(published["measure"]) <= set(benchmark.MEASURES)
    assert published["published"].notna().all() and published["page"].gt(0).all()
    assert published["source"].str.fullmatch(r"(ipr-20\d\d|erp\d\d-[a-z-]+|note-[a-z-]+)").all()
    for obs in published["observations"]:
        assert all(re.fullmatch(r"U\d{1,2}", o) and int(o[1:]) <= 98 for o in obs.split()), obs
    assert not published.duplicated(["measure", "year"]).any(), "one published figure per measure and year"


def test_committed_benchmark_is_in_step_with_the_lenses():
    if not (data.LENS_DIR / "rights.parquet").exists():
        pytest.skip("lens not built here (run: uv run python -m eda.build)")
    cols = ["measure", "year", "published", "lens"]
    committed = pd.read_csv(benchmark.OUT)[cols]
    fresh = benchmark.benchmark()[cols].astype({"lens": float})
    assert committed.equals(fresh), "run `python -m audit.benchmark` and commit"


def test_the_atlas_shows_the_review_on_a_page_of_its_own():
    from atlas import audit as audit_page

    page, problems = audit_page.page(write=False)
    assert not problems, problems
    tested = [v["id"] for v in page["verdicts"]]
    untested = [i for g in page["untestable"] for i in g["ids"]]
    assert sorted(tested + untested, key=lambda u: int(u[1:])) == [f"U{i}" for i in range(99)], "one verdict each"
    assert sum(page["counts"].values()) == 99
    assert all(v["note"] for v in page["verdicts"]), "every tested observation has a plain-English note"


def test_committed_audit_charts_are_in_step():
    from atlas import audit as audit_page

    assert not audit_page.stale_charts(), "run `python -m atlas.build` and commit"
