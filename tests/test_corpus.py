"""The corpus's rules on small inputs, and the committed files against the manifest."""

import importlib
import pkgutil
from pathlib import Path

import pandas as pd
import pytest
import yaml

import corpus.sources
from corpus.cli import verify
from corpus.core import REPO_LIMIT, read_manifest
from corpus.sources._abs import tidy
from corpus.sources._ato import snake
from corpus.sources.concordances import _groups, _ipc_refs

ROOT = Path(__file__).resolve().parents[1]


def test_every_module_is_registered_and_every_registered_source_is_described():
    register = yaml.safe_load((ROOT / "config/sources.yaml").read_text("utf-8"))["sources"]
    ids = [s["id"] for s in register]
    assert len(ids) == len(set(ids))
    for s in register:
        assert {"id", "title", "publisher", "tier", "questions", "url", "licence"} <= set(s), s["id"]
    modules = {m.name for m in pkgutil.iter_modules(corpus.sources.__path__) if not m.name.startswith("_")}
    assert modules <= set(ids), modules - set(ids)
    for m in modules:
        assert hasattr(importlib.import_module(f"corpus.sources.{m}"), "run")


def test_repo_files_match_the_manifest():
    assert verify(check_r2=False) == 0


def test_no_repo_file_is_too_big_for_github():
    big = [p for p in (ROOT / "data").rglob("*") if p.is_file() and p.stat().st_size > REPO_LIMIT]
    assert not big


def test_every_table_in_the_manifest_records_rows_and_columns():
    for sid, s in read_manifest()["sources"].items():
        for name, f in s["files"].items():
            if name.startswith("processed/"):
                assert f["rows"] >= 0 and f["columns"], (sid, name)
                assert f["location"] in ("repo", "r2")


@pytest.mark.parametrize(
    ("text", "refs"),
    [
        ("F03D", ["F03D"]),
        ("B63B 35/00. E04H 12/00. F03D 13/00", ["B63B 35/00", "E04H 12/00", "F03D 13/00"]),
        ("F03D 1/04, 9/00, 13/20. F03G 6/00", ["F03D 1/04", "F03D 9/00", "F03D 13/20", "F03G 6/00"]),
    ],
)
def test_green_inventory_references_are_split_by_subclass_and_group(text, refs):
    assert _ipc_refs(text) == refs


def test_group_specs_expand_ranges_and_lists():
    assert _groups("0-3;41;43") == [0, 1, 2, 3, 41, 43]


def test_abs_columns_split_into_code_and_label():
    raw = pd.DataFrame(
        {
            "DATAFLOW": ["ABS:X(1.0.0)"],
            "MEASURE: Measure": ["P1: Percent of businesses"],
            "TIME_PERIOD: Time Period": ["2023"],
            "OBS_VALUE": ["12.5"],
        }
    )
    t = tidy(raw, "X")
    assert t.loc[0, "measure"] == "P1" and t.loc[0, "measure_label"] == "Percent of businesses"
    assert t.loc[0, "time_period"] == "2023" and t.loc[0, "value"] == 12.5


def test_ato_headers_become_snake_case_without_units():
    assert (
        snake("Total R&D expenditure (notional deductions less feedstock adjustments) $") == "total_randd_expenditure"
    )
