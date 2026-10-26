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
