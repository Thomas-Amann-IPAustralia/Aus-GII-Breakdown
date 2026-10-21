"""The build's rules, on small hand-made inputs, and the committed outputs against a rebuild from data/raw."""

import json
from pathlib import Path

import pytest

from breakdown.build import main
from breakdown.countries import Countries
from breakdown.lenses import Lenses
from breakdown.model import BuildError, canonical, number, sig
from breakdown.sources.ctg import _name, place_year
from breakdown.sources.gii import appendix_flags

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    ("label", "year"),
    [
        ("2018", 2018),
        ("2018-19", 2019),  # a financial year: the year it ends
        ("1999-00", 2000),
        ("2010-12", 2011),  # a three-year period: its middle year
        ("2016-2020", 2018),
        ("2017-2020", 2018),  # four years: the middle, rounded down
        ("2008-2016", None),  # longer than five years
        ("2016 to 2021", None),  # a change over a period
        ("2031", None),  # a projection
        ("Total", None),
    ],
)
def test_ctg_years_are_placed_as_documented(label, year):
    assert place_year(label) == year


def test_ctg_names_leave_out_default_breakdowns():
    key = {
        "Description1": "Deaths",
        "Description6": "Rate per 1000 people",
        "Indigenous_Status": "All people",
        "Sex": "All people",
        "Age": "All ages",
        "Remoteness": "Major cities",
        "Description2": None,
    }
    assert _name(key) == "Deaths [rate per 1000 people] (All people; Major cities) (CtG)"


def test_numbers_and_rounding():
    assert number("1,234.5") == 1234.5
    assert number("..") is None and number("") is None and number(float("nan")) is None and number(True) is None
    assert sig(0.123456789) == 0.123457 and sig(2.0) == 2 and isinstance(sig(2.0), int)
    assert canonical({"b": 1, "a": [1.5, None]}) == '{"a":[1.5,null],"b":1}'


def test_countries_match_exactly_never_fuzzily():
    c = Countries({"AUS": "Australia", "HKG": "Hong Kong, China"})
    assert c.iso3("Australia") == "AUS"
    assert c.iso3("Korea (Republic of)") == "KOR"
    assert c.iso3("Türkiye") == "TUR"
    assert c.iso3("DR Congo") == "COD"
    assert c.iso3("World") is None and c.iso3("Arab States") is None and c.iso3("East Asia and the Pacific") is None
    assert c.iso3("North Cyprus") is None
    assert c.name("HKG") == "Hong Kong, China"


def test_lenses_longest_prefix_wins(tmp_path):
    p = tmp_path / "lenses.yaml"
    p.write_text('lenses: {a: {name: A}, b: {name: B}}\nwdi: {"": a, IP: b, IP.JRN: a}\ndefault: {whr: b}\n')
    lz = Lenses(p)
    assert lz.of("wdi", "IP.PAT.RESD") == "b" and lz.of("wdi", "IP.JRN.ARTC.SC") == "a" and lz.of("wdi", "NY") == "a"
    assert lz.of("whr") == "b"
    p.write_text('lenses: {a: {name: A}}\nwdi: {"": z}\n')
    with pytest.raises(BuildError):
        Lenses(p)


def test_appendix_markers(tmp_path):
    p = tmp_path / "a.md"
    p.write_text(
        "**4.3.1 Applied tariff rate**\n\nTariff rate (%) <sup>a</sup> | 2024\n\n"
        "314 **1.2.1 Regulatory quality** <sup>*</sup>\n\nRegulatory quality index <sup>*b</sup> | 2024\n"
    )
    f = appendix_flags(p)
    assert f["IN.4.3.1"] == {"bad": True, "half_weight": False}
    assert f["IN.1.2.1"] == {"bad": False, "half_weight": True}


def test_committed_outputs_match_a_rebuild(capsys):
    """The published data are exactly what the raw files give (the CI runs the same check)."""
    assert main(["build", "--check"]) == 0, capsys.readouterr().err


def test_outputs_hold_what_the_pages_expect():
    out = ROOT / "data/processed"
    aus = json.loads((out / "australia.json").read_text())
    eco = json.loads((out / "economies.json").read_text())
    page = json.loads((out / "gii-australia.json").read_text())
    ids = {v["id"] for v in aus["variables"]} | {v["id"] for v in eco["variables"]}
    # the explorer's starter questions and defaults name these
    for i in [
        "wdi:IP.PAT.RESD",
        "wdi:GB.XPD.RSDV.GD.ZS",
        "whr:life-evaluation",
        "gii:score:GII",
        "gii:score:IN",
        "gii:economy:PPPPC",
        "gii:value:OUT.6.1.1",
        "hdr:gini",
        "hdr:gii",
    ]:
        assert i in ids, i
    iso = [e["iso3"] for e in eco["economies"]]
    assert iso == sorted(iso) and "AUS" in iso
    for v in eco["variables"]:
        assert len(v["values"]) == len(iso)
    top = next(n for n in page["nodes"] if n["num"] == "")
    assert top["au"]["rank"] == 20 and len(page["league"]) == 139
