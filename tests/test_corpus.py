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
    assert "value_text" not in t  # every value was a number


def test_sdmx_cells_that_are_not_numbers_are_kept(tmp_path):
    """The OECD's IP tax regimes lost all 2,639 values when only numbers were kept (ADR 0011)."""
    import gzip

    from corpus.sources._abs import tidy_file

    rows = ["12.5%", "Not harmful", "3.1", ""]
    raw = pd.DataFrame({"DATAFLOW": "X", "MEASURE: Measure": [f"M{i}: m" for i in range(4)], "OBS_VALUE": rows})
    t = tidy(raw, "X")
    assert t["value"].iloc[0] == 12.5 and t["value"].iloc[2] == 3.1 and t["value"].iloc[[1, 3]].isna().all()
    assert t["value_text"].tolist()[:2] == ["12.5%", "Not harmful"] and t["value_text"].iloc[2:].isna().all()
    csv = tmp_path / "x.csv.gz"
    with gzip.open(csv, "wt") as f:
        raw.to_csv(f, index=False)
    n, cols = tidy_file(csv, tmp_path / "x.parquet", "X")
    got = pd.read_parquet(tmp_path / "x.parquet")
    assert n == 4 and "value_text" in cols
    assert got["value"].iloc[0] == 12.5 and got["value"].iloc[2] == 3.1 and pd.isna(got["value"].iloc[1])
    assert got["value_text"].tolist()[:2] == ["12.5%", "Not harmful"] and got["value_text"].isna().iloc[2:].all()


def test_abs_cube_keeps_footnoted_and_unpublished_cells_and_row_units(tmp_path):
    from corpus.sources._abs_cube import read_cube

    rows = [
        ["Table 1 Summary statistics", None, None],
        [None, "2023", "2024"],
        ["Expenditure", None, None],
        ["Labour costs", "1,234", "0 (b)"],
        ["Scholarships", "np", "-"],
        ["Researchers", "PYE", "98.5"],
    ]
    path = tmp_path / "cube.xlsx"
    pd.DataFrame(rows).to_excel(path, sheet_name="Table 1", header=False, index=False)
    t = read_cube(path).set_index(["row", "column"])
    assert t.loc[("Labour costs", "2023"), "value"] == 1234 and pd.isna(t.loc[("Labour costs", "2023"), "value_text"])
    assert t.loc[("Labour costs", "2024"), "value"] == 0 and t.loc[("Labour costs", "2024"), "value_text"] == "0 (b)"
    assert pd.isna(t.loc[("Scholarships", "2023"), "value"]) and t.loc[("Scholarships", "2023"), "value_text"] == "np"
    assert t.loc[("Researchers", "2024"), "unit"] == "PYE" and t.loc[("Researchers", "2024"), "value"] == 98.5
    assert t.loc[("Labour costs", "2023"), "section"] == "Expenditure"
    assert t.loc[("Labour costs", "2023"), "sheet_row"] == 4  # as Excel counts rows


def test_cabee_survival_rates_keep_their_size_range():
    from corpus.sources.abs_cabee import parse_cube, parse_national

    cube = pd.DataFrame(
        [
            ["Survival of Businesses by Main State by Subdivision, June 2021 – June 2025", None, None, None, None],
            [None, None, "Operating in June 2021", "Survived to June 2022", "Survived to June 2022"],
            ["State", "ANZSIC Subdivision", "1-4 Employees", "1-4 Employees", "Survival rate"],
            ["Label", "Code", "no.", "no.", "%"],
            ["New South Wales", "1", "9475", "9082", "95.9"],
        ]
    )
    t = parse_cube(cube, "8165DC04", "Table 1")
    rate = t[t.unit == "%"].iloc[0]
    assert rate["size"] == "1-4 Employees" and rate["measure"] == "Survived to June 2022" and rate["value"] == 95.9
    national = pd.DataFrame(
        [
            ["Table 2: Counts of businesses, business survival", None, None, None],
            [None, "Operating in June 2022", "Survived to June 2023", "Survival rate"],
            [None, "no.", "no.", "%"],
            ["Mining", "100", "90", "90.0"],
            ["CHANGED BUSINESS SIZE CATEGORY AT JUNE 2023", None, None, None],
            ["BUSINESS SIZE CATEGORY AT JUNE 2022", None, None, None],
            ["1–4", "5", "6", "7"],
        ]
    )
    n = parse_national(national, "Table 2")
    assert "Survived to June 2023 - survival rate" in set(n.column)
    assert n[n.row == "1–4"].period.unique().tolist() == ["June 2022 to June 2023"]


def test_phidu_sheet_keeps_sub_indicators_notes_and_area_types():
    from corpus.sources.phidu import pha_sa2, sheet

    df = pd.DataFrame(
        [
            ["©", "licence", "The data are estimates.", None],
            ["BACK", "Notes", "Bladder cancer", "Colorectal cancer"],
            [None, None, None, None],
            ["Key", None, "2017 to 2021", "2017 to 2021"],
            ["Code", "Name", "Number", "Number"],
            ["NEW SOUTH WALES", None, None, None],
            ["10283", "Adamstown - Kotara", "28", "30"],
            [None, None, "0", "0"],  # a spacer row with zeros
            [None, "AUSTRALIA+", "500", "600"],
            ["101", "Capital Region", "7", "8"],
            ["10102", "Queanbeyan", "2", "3"],
        ]
    )
    t = sheet(df)
    assert set(t.indicator) == {"Bladder cancer", "Colorectal cancer"} and set(t.note) == {"The data are estimates."}
    kinds = dict(zip(t.area_name, t.area_type, strict=False))
    assert kinds == {"Adamstown - Kotara": "pha", "AUSTRALIA+": "total", "Capital Region": "sa4", "Queanbeyan": "sa3"}
    assert len(t) == 8  # four areas, two indicators; the spacer row is dropped
    phas = pd.DataFrame(
        [
            ["SA2 codes", "SA2 names", "PHA code", "PHA name"],
            ["NSW - Greater Sydney", None, None, None],
            ["119041668, 119041381", "Arncliffe, Rockdale", "10063", "Arncliffe/ Rockdale"],
        ]
    )
    pairs = pha_sa2(phas)
    assert pairs.sa2_code.tolist() == ["119041668", "119041381"] and set(pairs.section) == {"NSW - Greater Sydney"}


def test_austender_notices_keep_their_amendment_number_and_latest_version(tmp_path):
    import gzip
    import json

    from corpus.sources.austender import _api, _flatten

    def release(rid, date, tag, n=None, value=100):
        c = {"id": "CN1", "value": {"amount": value}}
        if n:
            c["amendments"] = [{"id": f"CN1-A{n}"}]
        return {"id": rid, "date": date, "tag": [tag], "contracts": [c], "parties": []}

    r = _flatten(release("r1", "2023-04-27T08:08:01Z", "contractAmendment", 3))
    assert (r["cn_id"], r["parent_cn_id"], r["amendment"]) == ("CN1-A3", "CN1", 3)
    odd = release("r9", "2019-07-21T00:00:00Z", "contract")  # a contract release under an amendment's id
    odd["contracts"][0]["id"] = "CN1-A4"
    r = _flatten(odd)
    assert (r["cn_id"], r["parent_cn_id"], r["amendment"]) == ("CN1-A4", "CN1", 4)
    bad = release("r8", "2020-01-01T00:00:00Z", "contractAmendment")  # an amendment with no numbered id
    bad["contracts"][0]["amendments"] = [{"id": "CN1-AMEND"}]
    r = _flatten(bad)
    assert (r["cn_id"], r["parent_cn_id"], r["amendment"]) == ("CN1-AMEND", "CN1", None)
    p = tmp_path / "api.jsonl.gz"
    with gzip.open(p, "wt") as f:
        for x in (
            release("r0", "2019-07-07T00:00:00Z", "contract"),
            release("r1", "2020-01-02T00:00:00Z", "contractAmendment", 1, 150),
            release("r2", "2023-05-01T00:00:00Z", "contractAmendment", 1, 160),  # the same notice, republished
            release("r3", "2023-05-01T00:00:00Z", "contractAmendment", 2, 170),  # first seen in that batch
        ):
            f.write(json.dumps(x) + "\n")
    api = _api([p]).set_index("cn_id")
    assert len(api) == 3 and api.loc["CN1-A1", "value"] == 160 and api.loc["CN1-A1", "published"] == "2020-01-02"
    assert api.published_batch.to_dict() == {"CN1": False, "CN1-A1": False, "CN1-A2": True}


def test_austender_bulk_amendments_take_their_own_publish_date(tmp_path):
    from corpus.sources.austender import _bulk

    path = tmp_path / "bulk.xlsx"
    pd.DataFrame(
        {
            "Parent Contract ID": [None, "CN9", "CN9"],
            "Contract ID": ["CN9", "CN9-A2", "CN9-A2"],  # the file gives one amendment's id twice
            "Contract Notice Type": ["Parent", "Amendment", "Amendment"],
            "Publish Date": ["2010-01-05", "2010-01-05", "2010-01-05"],
            "Applicable Publish Date": ["2010-01-05", "2011-03-01", "2010-07-01"],
            "Value": ["100", "180", "150"],
        }
    ).to_excel(path, index=False)
    b = _bulk(path).set_index("cn_id")
    assert len(b) == 2 and b.loc["CN9-A2", "value"] == "180"
    assert b.loc["CN9-A2", "published"] == "2011-03-01" and b.loc["CN9-A2", "amendment"] == 2
    assert b.loc["CN9", "amendment"] == 0 and b.loc["CN9-A2", "parent_cn_id"] == "CN9"


def test_austender_asks_by_id_for_bulk_contracts_running_at_its_end_and_keeps_the_earlier_date():
    from corpus.sources.austender import _combine, _running

    bulk = pd.DataFrame(
        {
            "cn_id": ["CN1", "CN1-A1", "CN2", "CN3"],
            "parent_cn_id": ["CN1", "CN1", "CN2", "CN3"],
            "amendment": [0, 1, 0, 0],
            "published": ["2018-01-01", "2018-06-01", "2018-02-01", "2018-03-01"],
            "end": ["2019-06-30", "2021-06-30", "2019-08-29", None],  # CN1's amendment extends it past the cut-off
            "value": ["100", "150", "50", "70"],
        }
    )
    assert _running(bulk) == ["CN1"]
    api = pd.DataFrame(  # the API's copy of CN1-A1 (re-released in 2025, with its current values) and a new CN1-A2
        {
            "cn_id": ["CN1-A1", "CN1-A2"],
            "parent_cn_id": ["CN1", "CN1"],
            "amendment": [1, 2],
            "published": ["2025-09-22", "2025-09-22"],
            "end": ["2021-06-30", "2023-06-30"],
            "value": [150.0, 400.0],
            "published_batch": [True, True],
        }
    )
    both = _combine(api, bulk).set_index("cn_id")
    assert len(both) == 5 and both.loc["CN1-A1", "published"] == "2018-06-01"
    assert both.loc["CN1-A2", "value"] == 400 and both.loc["CN1-A2", "published"] == "2025-09-22"
    assert both.published_batch.to_dict() == {"CN1": False, "CN1-A1": False, "CN2": False, "CN3": False, "CN1-A2": True}
    assert list(both.columns[:4]) == ["parent_cn_id", "amendment", "published", "published_batch"]
    assert not both.value_jump.any() and list(both.columns).index("value_jump") == list(both.columns).index("value") + 1


def test_austender_flags_a_hundredfold_jump_in_a_contracts_value():
    from corpus.sources.austender import _combine

    notices = pd.DataFrame(
        {
            "cn_id": ["CN7", "CN7-A1", "CN7-A2", "CN8", "CN8-A1"],
            "parent_cn_id": ["CN7", "CN7", "CN7", "CN8", "CN8"],
            "amendment": [0, 1, 2, 0, 1],
            "published": ["2020-01-01", "2021-01-01", "2022-01-01", "2020-01-01", "2021-01-01"],
            "value": ["6000000", "9626000000", "9626000", "2000000000", "15000000000"],  # CN8: a sevenfold rise
        }
    )
    api = notices.iloc[:0].assign(published_batch=pd.Series(dtype=bool))
    flags = _combine(api, notices).set_index("cn_id").value_jump
    assert flags.to_dict() == {"CN7": False, "CN7-A1": True, "CN7-A2": False, "CN8": False, "CN8-A1": False}


def test_rdti_takes_the_abn_from_an_acn_only_when_one_abn_holds_it(tmp_path):
    from corpus.sources.rdti import abn_from_acn

    abr = tmp_path / "abns.parquet"
    pd.DataFrame({"abn": ["11111111111", "22222222222", "33333333333"], "acn": ["111", "222", "222"]}).to_parquet(abr)
    df = pd.DataFrame({"abn": [None, None, "44444444444", None], "acn": ["111", "222", None, None]})
    out = abn_from_acn(df, str(abr)).fillna("")
    assert out.abn.tolist() == ["11111111111", "", "44444444444", ""]
    assert out.abn_from.tolist() == ["acn", "", "report", ""]


def test_cer_series_are_read_by_month_without_their_totals(tmp_path):
    from corpus.sources.cer import series_file

    path = tmp_path / "sgu-solar-installations-2011-to-present-and-totals.csv"
    path.write_text(
        "Small Unit Installation Postcode,Historic Total Installation Quantity (2001 - 2010),"
        "Jan 2011 - Installation Quantity,Feb 2011 - Installation\xa0Quantity,Total Installation Quantity\n"
        '0800,5,1,"1,002",1008\n'
    )
    t = series_file(path)
    assert t.month.tolist() == ["2011-01", "2011-02"] and t.value.tolist() == [1, 1002]
    assert set(t.technology) == {"solar_pv"} and set(t.series) == {"installations"}


def test_committed_tables_have_one_row_per_key():
    """Corpus tables whose parsers were repaired (ADR 0011) keep one row per natural key."""
    import duckdb

    from corpus.core import path

    keys = {
        ("cer", "installations"): "technology, series, postcode, month",
        (
            "phidu",
            "indicators",
        ): "workbook, sheet, area_type, area_code, area_name, quintile, indicator, sub_indicator, period, measure",
        ("phidu", "pha_sa2"): "sa2_code",
        ("abs_cabee", "national"): '"table", period, "row", "column", release',
        ("tga", "artg"): "artg_id, product_name, sponsor_name, device_manufacturer, active_ingredients",
        ("tga", "artg_ingredients"): "artg_id, ingredient",
        ("abs_rd_vc", "cubes"): 'cube, sheet, sheet_row, "column"',
        ("policy_events", "events"): "id",
        ("austender", "contracts"): "cn_id",
    }
    con = duckdb.connect()
    for (source, table), key in keys.items():
        p = path(source, table)
        rows, distinct = con.execute(f"SELECT count(*), count(DISTINCT ({key})) FROM '{p}'").fetchone()
        assert rows == distinct, f"{source}/{table}: {rows - distinct} rows repeat ({key})"


def test_contracts_are_counted_once_in_the_spine():
    """Each AusTender contract counts once, at its latest notice, for the supplier that notice names (ADR 0011)."""
    import duckdb

    from corpus.core import path

    contracts, spine = path("austender", "contracts"), path("linkage", "abn_spine")
    want, got = (
        duckdb.connect()
        .execute(f"""
        SELECT (SELECT count(*) FROM (
                  SELECT parent_cn_id FROM '{contracts}' GROUP BY 1
                  HAVING arg_max(supplier_abn, (amendment IS NOT NULL, amendment, published))
                         FILTER (supplier_abn IS NOT NULL) IS NOT NULL)),
               (SELECT sum(austender_contracts) FROM '{spine}')""")
        .fetchone()
    )
    assert want == got


def test_oecd_tax_regimes_keep_every_value():
    import duckdb

    from corpus.core import path, raw_path

    raw, t = raw_path("oecd", "ip_tax_regimes.csv.gz"), path("oecd", "ip_tax_regimes")
    nonempty, kept = (
        duckdb.connect()
        .execute(f"""
        SELECT (SELECT count(*) FROM read_csv('{raw}', all_varchar=true) WHERE trim(OBS_VALUE) <> ''),
               (SELECT count(*) FROM '{t}' WHERE value IS NOT NULL OR value_text IS NOT NULL)""")
        .fetchone()
    )
    assert nonempty == kept == 2639


def test_policy_events_are_checked_and_unique():
    from corpus.core import load

    e = load("policy_events", "events")
    assert not e["verify"].any() and e["id"].is_unique
    assert str(e.set_index("id").loc["patents-act-1990", "date"]) == "1991-04-30"  # s 2(2); not 1 May
    assert str(e.set_index("id").loc["patent-term-20-years", "date"]) == "1995-07-01"  # 1994 Act, s 2 (ADR 0014)


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


def test_inventor_given_names_and_gender_estimates():
    import duckdb

    from corpus.sources.google_patents_inventors import estimate_sql, given_sql

    con = duckdb.connect()
    con.execute(
        "CREATE TABLE n AS SELECT * FROM (VALUES (1, 'SMITH, JOHN A'), (2, 'JOHN A SMITH'), (3, 'J A SMITH'),"
        " (4, 'O''BRIEN MARY-JANE')) t(id, name)"
    )
    first = [r[0] for r in con.execute(f"SELECT {given_sql('name', 1)} FROM n ORDER BY id").fetchall()]
    second = [r[0] for r in con.execute(f"SELECT {given_sql('name', 2)} FROM n ORDER BY id").fetchall()]
    assert first == ["john", "john", None, "obrien"]
    assert second == ["john", None, None, "mary-jane"]

    con.execute(
        "CREATE TABLE inv AS SELECT * FROM (VALUES ('SMITH ANDREA', 'AU'), ('ROSSI ANDREA', 'IT'),"
        " ('LEE JORDAN', 'NZ'), ('KUMAR X', 'IN')) t(name, country_code)"
    )
    con.execute(
        "CREATE TABLE wc AS SELECT * FROM (VALUES ('andrea', 'AU', 'F', 0.93), ('andrea', 'AU', 'M', 0.07),"
        " ('andrea', 'IT', 'M', 1.0)) t(name, code, gender, wgt)"
    )
    con.execute("CREATE TABLE wn AS SELECT * FROM (VALUES ('andrea', 'F'), ('jordan', 'M')) t(name, gender)")
    got = con.execute(
        f"SELECT name, round(p_female, 2), p_female_basis FROM ({estimate_sql('inv', 'wc', 'wn', 2)}) ORDER BY name"
    ).fetchall()
    assert got == [
        ("KUMAR X", None, None),
        ("LEE JORDAN", 0.0, "name"),
        ("ROSSI ANDREA", 0.0, "country"),
        ("SMITH ANDREA", 0.93, "country"),
    ]


def test_fee_schedules_split_cells_and_keep_the_items_words():
    from corpus.sources.frl_fees import anniversary, flatten, money

    assert [money(s) for s in ("$1 000 less any amount", "$1,250", "$250 for each class", "1000", "$12.50", "nil")] == [
        1000.0,
        1250.0,
        250.0,
        1000.0,
        12.5,
        None,
    ]
    assert anniversary("Continuation fee ... for: / (h) the tenth anniversary / (i) the eleventh anniversary") == 11
    assert anniversary("Renewal fee for: / (a) the 4th anniversary: / (ii) fee paid by another means") == 4
    blocks = [
        ("p", "Part 2—General fees"),
        ("tr", [["Item"], ["Matter"], ["Fee"]]),
        (
            "tr",
            [
                ["1"],
                ["Filing an application to register a trade mark:", "(a) in a single class", "(b) more"],
                ["$200", "$200 plus $150 for each additional class"],
            ],
        ),
        ("tr", [["2"], ["Renewal of registration:"], []]),
        ("tr", [[], ["(a) fee paid by preferred means;"], ["$400"], []]),
        ("tr", [["3"], ["Renewal fee for:"], []]),  # "(i)" after "(h)": a numeral under it, then the next letter
        ("tr", [[], ["(h) the 11th anniversary:"], []]),
        ("tr", [[], ["(i) fee paid by preferred means;"], ["$645"]]),
        ("tr", [[], ["(i) the 12th anniversary:"], []]),
        ("tr", [[], ["(i) fee paid by preferred means;"], ["$780"]]),
    ]
    rows = flatten(blocks)
    assert [(r["item"], r["matter"], r["amount_aud"]) for r in rows] == [
        ("1", "Filing an application to register a trade mark: / (a) in a single class", 200.0),
        ("1", "Filing an application to register a trade mark: / (b) more", 200.0),
        ("2", "Renewal of registration: / (a) fee paid by preferred means;", 400.0),
        ("3", "Renewal fee for: / (h) the 11th anniversary: / (i) fee paid by preferred means;", 645.0),
        ("3", "Renewal fee for: / (i) the 12th anniversary: / (i) fee paid by preferred means;", 780.0),
    ]


def test_key_fees_are_the_base_fee_paid_the_cheapest_way():
    from corpus.sources.frl_fees import key_fees

    item = "Filing a request for a standard patent accompanied by a complete specification:"
    renew = (
        "Continuation fee under paragraph 142(2)(d) of the Act, or renewal fee under paragraph 143(a) of the Act, for:"
    )
    rows = pd.DataFrame(
        {
            "matter": [
                f"{item} / (a) by preferred means;",
                f"{item} / (b) by another means",
                f"{item} / (c) if the specification includes a nucleotide sequence filed by electronic means",
                f"{renew} / (a) the fourth anniversary: / (i) fee paid by preferred means;",
                f"{renew} / (a) the fourth anniversary: / (ii) fee paid by another means;",
                f"{renew} / (a) the fourth anniversary: / and, in addition, if the fee is paid within 6 months after",
            ],
            "amount_aud": [400.0, 600.0, 1000.0, 300.0, 350.0, 100.0],
        }
    ).assign(right="patent")
    assert key_fees(rows) == {("standard_filing", 0): 400.0, ("standard_renewal", 4): 300.0}
    accept = "Acceptance of a patent request and complete specification under section 49 of the Act:"
    rows = pd.DataFrame(
        {
            "matter": [
                f"{accept} / (a) if the specification does not contain more than 20 claims at acceptance;",
                f"{accept} / (b) if the specification contains more than 20 claims at acceptance",
            ],
            "amount_aud": [250.0, 250.0],
        }
    ).assign(right="patent")
    assert key_fees(rows) == {("acceptance", 0): 250.0}


def test_fee_history_ends_at_ip_australias_current_fees():
    """The latest version of each fee regulation gives the fees IP Australia's website lists (ADR 0031)."""
    from corpus.core import load

    key = load("frl_fees", "key_fees")
    now = key[key["end"].isna()].assign(a=lambda d: d["anniversary"].fillna(0).astype(int))
    got = {(r.right, r.fee, r.a): r.amount_aud for r in now.itertuples()}
    site = load("ipa_fees", "fees").dropna(subset=["amount_aud"])

    def listed(right, heading, row, column=None):
        s = site[(site["right"] == right) & site["heading"].str.contains(heading) & (site["row"] == row)]
        s = s[s["column"].str.contains(column)] if column else s
        assert len(s) == 1, (right, heading, row)
        return s["amount_aud"].iloc[0]

    want = {
        ("patent", "provisional_filing", 0): listed("patent", "Provisional patent", "Provisional patent application"),
        ("patent", "standard_filing", 0): listed("patent", "Standard patent", "Standard patent application"),
        ("patent", "standard_examination", 0): listed("patent", "Fees", "Examination request"),
        ("trade_mark", "filing", 0): listed(
            "trade_mark", "Standard application", "Trade mark application with picklist"
        ),
        ("design", "filing", 0): listed(
            "design", "1. Application", "First design identified in the application at the time of filing"
        ),
        ("design", "examination", 0): listed(
            "design", "2. Examination", "Request to examine a registered design - by registered owner"
        ),
        ("design", "renewal", 0): listed("design", "3. Renewal", "Renewal of registration"),
        ("pbr", "application", 0): listed(
            "pbr", "Application part 1", "Application part 1 (submitted via online services)"
        ),
        ("pbr", "examination", 0): listed("pbr", "Fees", "Examination - single application"),
        **{
            ("patent", "standard_renewal", n): listed(
                "renewals", "Standard patent renewal", f"{n}th anniversary", "online"
            )
            for n in range(4, 20)
        },
    }
    assert {k: got.get(k) for k in want} == want
    assert key.groupby(["right", "fee", "anniversary"], dropna=False)["end"].apply(lambda e: e.isna().sum() <= 1).all()


def test_ato_postcode_items_take_units_from_headers_and_one_name_across_years():
    from corpus.sources.ato_postcode import harmonise, items

    def year(cols, rows, y):
        df = pd.DataFrame(rows, columns=cols, dtype=str)
        return items(df, y)

    # 2013-14 names the count of individuals without its unit; footnote numbers end some names
    a = year(["State/Territory1", "Postcode", "Number of individuals", "Taxable income or loss3 $"],
             [["NSW", "2000", "10", "500"], ["Total", "Total", "10", "500"]], 2014)  # fmt: skip
    b = year(["State/ Territory1", "Postcode", "Individuals no.", "Taxable income or loss3 no.",
              "Taxable income or loss3 $"], [["VIC", "3000", "20", "19", "900"]], 2024)  # fmt: skip
    out = harmonise(pd.concat([a, b], ignore_index=True))
    assert set(out["postcode"]) == {"2000", "3000"}  # the total row is not a postcode
    assert set(zip(out["item"], out["unit"], strict=True)) == {
        ("Individuals", "no."), ("Taxable income or loss", "$"), ("Taxable income or loss", "no.")
    }  # fmt: skip
    assert out.loc[out.item.eq("Individuals"), "income_year"].tolist() == ["2013-14", "2023-24"]


def test_census_time_series_cells_lose_their_year_in_every_spelling():
    from corpus.sources.abs_census_tsp import labels, long_table

    df = pd.DataFrame(
        {
            "SA2_CODE_2021": ["101021007"],
            "Tot_persons_C11_P": [10],
            "Tot_persons_C21_P": [12],
            "Med_age_persns_C2016": [40],
            "Brthplace_Aust_2011_Ce_P": [7],
        }
    )
    t = long_table(df, "T01")
    assert sorted(zip(t["indicator"], t["census_year"], strict=True)) == [
        ("Brthplace_Aust_P", 2011), ("Med_age_persns", 2016), ("Tot_persons_P", 2011), ("Tot_persons_P", 2021)
    ]  # fmt: skip
    meta = pd.DataFrame(
        [["Cell descriptors", None, None], ["Sequential", "Short", "Long"],
         ["T1", "Tot_persons_C11_P", "Total_persons_2011_Census_Persons"],
         ["T2", "Med_age_persns_C2011", "Median_age_of_persons_Census_year_2011"]]
    )  # fmt: skip
    assert labels(meta) == {"Tot_persons_P": "Total persons Persons", "Med_age_persns": "Median age of persons"}
