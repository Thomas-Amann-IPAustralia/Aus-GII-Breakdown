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


def test_dropped_tables_take_the_first_row_with_three_values_as_the_header():
    from corpus.sources._manual import _framed

    raw = pd.DataFrame([["A title", None, None], [None, None, None], ["Origin", "Year", "Count"], ["AU", "2020", "5"]])
    t = _framed(raw)
    assert list(t.columns) == ["origin", "year", "count"]
    assert t.iloc[0].tolist() == ["AU", "2020", "5"]


def test_artg_ingredients_drop_quantities_and_equivalents():
    from corpus.sources.tga import ingredients

    s = "natural fish oil, Quantity: 1000 mg (Equivalent: eicosapentaenoic acid, Qty 180 mg); Biotin, Quantity: 1 mg"
    assert ingredients(s) == ["natural fish oil", "biotin"]


def test_federal_court_cover_page_fields():
    from corpus.sources.fedcourt import court, cover, last_date

    text = (
        "FEDERAL COURT OF AUSTRALIA\n\nA Pty Ltd v B Inc [2017] FCA 1075\n"
        "File number:          VID 885 of 2017\n\nJudge:                KENNY J\n\n"
        "Catchwords:           PATENTS – infringement\n                      PATENTS – validity\n\n"
        "Legislation:          Patents Act 1990 (Cth)\n\n"
        "National Practice Area:   Intellectual Property\n\n"
        "Counsel for the Applicant:  Mr X SC\n\nSolicitor for the Applicant:  Allens\n\nORDERS\n\nJudge:  ignored\n"
    )
    c = cover(text)
    assert c["file_number"] == "VID 885 of 2017" and c["judges"] == "KENNY J"
    assert c["catchwords"] == "PATENTS – infringement\nPATENTS – validity"
    assert c["practice_area"] == "Intellectual Property" and c["solicitors"] == "Allens"
    assert "Mr X SC" not in c.values()
    assert court("A Pty Ltd v B Inc [2017] FCAFC 75") == "FCAFC"
    assert last_date("26 and 27 November 2013") == "27 November 2013"


def test_wipo_exports_read_long_with_thousands_separators():
    from corpus.sources.wipo_ipstats import _read

    text = (
        "Intellectual property right :Madrid\n\nIndicator :2a - Applications\n\n"
        "Source: WIPO statistics database. Last updated: October 2026\n\n"
        '"Country of holder","Country of holder(Code)",2024,2025,\n"Australia","AU","1,959","1,995",\n'
    )
    updated, df = _read(text)
    assert updated == "October 2026"
    assert df[["year", "value"]].values.tolist() == [[2024, 1959.0], [2025, 1995.0]]


def test_google_patents_au_application_numbers_match_ip_rapid():
    import pyarrow as pa

    from corpus.sources.google_patents import _au_application

    got = _au_application(pa.array(["AU-2017352992-A", "AU-6508386-A", "US-123-A", None]))
    assert got == ["2017352992", "1986065083", None, None]
