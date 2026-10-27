"""Build the lens tables: one analysis-ready table per unit of analysis, written to `analysis/eda/data/` (gitignored).

    uv run python -m eda.build              # every lens (about two minutes once the R2 tables are cached)
    uv run python -m eda.build firms        # one lens

| Lens | One row per | Built from |
|---|---|---|
| `rights` | IP right (patent, trade mark, design, plant breeder's right) | `iprapid/*`, `google_patents*` |
| `firms` | ABN in any IP, R&D, procurement or tax source | `linkage/abn_spine`, `rights`, `rdti`, `ato_ctt` |
| `regions` | Postal area (the ABS's version of a postcode) | `abs_regions`, `abs_census`, `abr`, `rights`, `firms` |
| `region_indicators` | Postal area, source, indicator, period | Census, Data by Region, CABEE, PHIDU, CER |
| `national` | Country, year and indicator | `wdi/panel`, `wipo_ipstats/office_origin`, `oecd/msti` |
| `industries` | ANZSIC division and financial year | `rights`, classification, concordances, CABEE, BERD, WPI |
| `institution_rights` | IP right and research institution that filed it | `iprapid/party`, `ror`, the reviewed link |
| `institutions` | Research institution (ROR) and year | OpenAlex, ARC, NHMRC, `institution_rights`, AusTender |
| `timeline` | Month, for Australia (IP Australia's whole register) | `rights`, `iprapid/events`, `policy_events` |

`regions` also reads `austender`; `region_indicators` holds its attachments, long (ADR 0018), as do
`national_indicators` (ADR 0019) and `industry_indicators` (ADR 0020). `institutions` reads the reviewed link from
research institutions to ROR, names and ABNs in `analysis/eda/institutions/` (ADR 0021). Every column is
described, in plain English, in `analysis/eda/variables.yaml`. Derived columns are defined here and
nowhere else, so a reader can check exactly how each was made.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import pycountry

from .data import LENS_DIR, connect, lens_table, resolve

# Filing counts for places use the ten latest complete Australian financial years (July to June; FY2026 = Jul 2025
# to Jun 2026). IP RAPID lists applications from filing, before publication: patents filed per year show no drop-off
# in FY2025 or FY2026 (35,065 and 41,257). Stage 1 checks this again.
WINDOW = (2017, 2026)
TODAY = "2026-10-22"  # the corpus build date, so ages do not change with the day the notebook is run
TIMELINE_START, TIMELINE_END = (
    "1904-01-01",
    "2026-09-01",
)  # IP RAPID runs to mid-October 2026: Sep is the last full month

# The timeline's monthly series: (column, condition). Applications are counted by application date from the `rights`
# lens; outcomes by effective date from IP RAPID's events, using only categories recorded consistently over time.
# Left out: renewals (their records stop in 2016 for designs and 2018 for trade marks) and every '_historical'
# category (dated on the day records moved between systems, such as 10 November 2018 for trade marks; at least 97% of
# the rights each covers also have the same event with its real date).
# Origin has three values (ADR 0009): a right with no applicant country counts as "origin unknown", never as overseas.
# Outcomes are counts of events, each counted once: an event IP RAPID records twice for a right, with the same type and
# date, counts once (ADR 0010).
ORIGINS = [
    ("au", "australian_applicant"),
    ("overseas", "NOT australian_applicant"),
    ("origin_unknown", "australian_applicant IS NULL"),
]
TIMELINE_APPLICATIONS = [
    *[(f"patents_standard_{o}", f"patent_type = 'standard' AND {cond}") for o, cond in ORIGINS],
    ("patents_provisional", "patent_type = 'provisional'"),
    ("patents_second_tier", "patent_type = 'second_tier'"),
    *[(f"trade_marks_{o}", f"ip_right_type = 'trade_mark' AND {cond}") for o, cond in ORIGINS],
    *[(f"designs_{o}", f"ip_right_type = 'design' AND {cond}") for o, cond in ORIGINS],
    ("pbr_applications", "ip_right_type = 'pbr'"),
]
TIMELINE_EVENTS = [
    ("patents_granted", "ip_right_type = 'patent' AND event_category = 'granted'"),
    ("trade_marks_registered", "ip_right_type = 'trade_mark' AND event_category = 'granted'"),
    ("designs_registered", "ip_right_type = 'design' AND event_category = 'registered'"),
    ("pbr_granted", "ip_right_type = 'pbr' AND event_category = 'granted'"),
    ("patents_lapsed", "ip_right_type = 'patent' AND event_category = 'lapsed'"),
    ("trade_marks_lapsed", "ip_right_type = 'trade_mark' AND event_category = 'lapsed'"),
    ("designs_lapsed", "ip_right_type = 'design' AND event_category = 'lapsed'"),
    ("patents_ceased", "ip_right_type = 'patent' AND event_category = 'ceased'"),
    ("trade_marks_ceased", "ip_right_type = 'trade_mark' AND event_category = 'ceased'"),
    ("designs_ceased", "ip_right_type = 'design' AND event_category = 'ceased'"),
    ("patents_expired", "ip_right_type = 'patent' AND event_category = 'expired'"),
    (
        "patent_oppositions",
        "ip_right_type = 'patent' AND event_type IN "
        "('published_opposition_lodged', 'published_opposition_under_section_104_4_lodged')",
    ),
    ("trade_mark_oppositions", "ip_right_type = 'trade_mark' AND event_category = 'opposition'"),
    (
        "patent_extensions_of_term",
        "event_type = 'published_extension_of_term_of_standard_patent_extension_granted'",
    ),
    ("patent_assignments", "ip_right_type = 'patent' AND event_type LIKE 'published_assignments%'"),
    ("trade_mark_assignments", "ip_right_type = 'trade_mark' AND event_category = 'publish_ownership'"),
]
# The date an event is counted at. A trade mark is registered "as from" its filing date, so IP RAPID's effective date
# for a registration is the filing (priority) date for 85% of them; the date the registration was entered is the
# declared date, which is what a count of registrations a month needs (ADR 0010).
EVENT_DATE = (
    "CASE WHEN ip_right_type = 'trade_mark' AND event_category = 'granted' "
    "THEN coalesce(event_declared_date, event_effective_date) ELSE event_effective_date END"
)
# A series starts where its records become continuous: the first month from which at least 9 of the next 12 have a
# record (ADR 0010), so decades of scattered early records are not read as zeros; earlier months are empty. Before the
# rule, trade mark oppositions read 0 for 777 months. A start can be set by hand here, with the reason.
# The Stage 1 profile (ADR 0014) set 15 more by hand, where the rule starts a series too early: before them IP RAPID
# holds only the rights still on the register when its records were computerised (survivors), or dates its events in
# batches, with empty months between them. The evidence is in `01_univariate.ipynb`, section 5.0.
TIMELINE_START_OVERRIDE = {
    # Registrations are counted by the date entered, which IP RAPID records from December 1985 (every registration
    # since 1986, under 2% before 1984). An earlier registration has only its effective date, which is its filing
    # date (99% of them), so it would count in the month it was filed: a different measure, which leaves a false
    # hole from mid-1983 (registrations entered then are dated at filing; filings then were entered after 1985).
    "trade_marks_registered": "1986-01-01",
    # Survivors. Of trade marks filed in 1981, 2% to 5% were never registered, against 51% to 59% from January 1983
    # to 1988: applications that failed before the records were computerised are missing.
    **dict.fromkeys(["trade_marks_au", "trade_marks_overseas", "trade_marks_origin_unknown"], "1983-01-01"),
    # Of designs filed in 1985, 0.2% to 0.7% were never registered, against 22% to 31% from January 1986 to 1988.
    **dict.fromkeys(["designs_au", "designs_overseas", "designs_origin_unknown"], "1986-01-01"),
    # About 100 provisionals a month to July 1985, then about 350 to 570 a month from September 1985.
    "patents_provisional": "1985-09-01",
    # Grants are recorded only for patents filed from 1979 (68.5% of them, against at most 1.9% of earlier ones);
    # 99.4% of grants come within six years of filing, so from 1985 almost none are of earlier patents.
    "patents_granted": "1985-01-01",
    # Designs filed from 1986 are complete, and 90% of them are registered within 715 days.
    "designs_registered": "1988-01-01",
    # Batches. Cessations are dated on 0 to 3 days a month to March 1995 (31 of the 104 months from September 1986 are
    # empty, and others hold several months' worth), then weekly; April 1995 holds the backlog (3,511).
    "patents_ceased": "1995-05-01",
    # Expiries likewise to December 1994 (20 of 101 months hold 5 or fewer), then dated daily. Their fall from July
    # 1995 is real: the standard patent term rose from 16 to 20 years for every patent still in force (policy event
    # `patent-term-20-years`).
    "patents_expired": "1995-01-01",
    # Lapses have empty months and backlogs to 1988 (3 in December 1985, 1,286 in July 1987); none since.
    "patents_lapsed": "1989-01-01",
    # Empty from October to December 1991, then a backlog of 1,187 in January 1992 (against about 150 a month).
    "patent_assignments": "1992-02-01",
    # 0 to 18 lapses a month to September 1985, then 522.
    "trade_marks_lapsed": "1985-10-01",
    # 0 to 58 a month to 1985, irregular in 1986 (8 to 328), 232 to 424 a month from January 1987.
    "trade_marks_ceased": "1987-01-01",
    # Empty from October to December 1986.
    "trade_mark_assignments": "1987-01-01",
    # Rising from 0 to 138 a month in 1988 as records filled in, and a backlog in May and June 1990 (705 and 1,194).
    "designs_ceased": "1990-07-01",
    # Empty months and backlogs to 1993 (0 in March 1993, 222 in August 1993).
    "designs_lapsed": "1994-01-01",
}
# Series whose zeros after their start are real, not gaps: the "origin unknown" series fall to zero once applicants'
# countries came to be recorded.
TIMELINE_STRUCTURAL_ZEROS = {"patents_standard_origin_unknown", "trade_marks_origin_unknown", "designs_origin_unknown"}
# Months at the end left empty because the register records them late (ADR 0010): a trade mark or design ceases only
# once its six-month grace period for renewal has passed (trade marks: 0 from May 2026, a median 198 days from the
# effective date to the record); recent designs' applicant countries are filled in weeks after filing (origin unknown
# for 843 of September 2026's designs, against about 50 a month before).
TIMELINE_LAG = {
    "trade_marks_ceased": 6,
    "designs_ceased": 6,
    "designs_au": 3,
    "designs_overseas": 3,
    "designs_origin_unknown": 3,
}

# The events attachment (B5, ADR 0015): each right's milestones, from IP RAPID's events, as (column, condition). Each
# is the first such event the register still holds as standing (a lapse later reversed, or an acceptance withdrawn, is
# not standing), dated from 1904 to the corpus date and not before the right's earliest filing (171 events are, such
# as 26 trade mark oppositions dated 1909); 1 January 1970 is a placeholder (3,154 events) and is left out.
# A grant is not here: the grant event's date is `registered_date` for every granted patent.
EXPEDITED = (
    "(ip_right_type = 'patent' AND event_type LIKE 'exam_expedited%') OR event_category = 'exam_request_expedite'"
)
ASSIGNED = (  # one record, published twice for patents (as an assignment and as a party change): the first is used
    "(ip_right_type = 'patent' AND event_type LIKE 'published_assignments%') "
    "OR (ip_right_type IN ('trade_mark', 'design') AND event_category = 'publish_ownership')"
)
RIGHT_EVENTS = [
    # The date the term of a patent runs from: the filing date of the complete application (for a PCT application,
    # the international filing date; for a divisional, often the parent's)
    ("date_of_patent", "ip_right_type = 'patent' AND event_category = 'ip_right_date'"),
    # Examination asked for: patents and designs (a trade mark is examined without a request), not re-examination
    (
        "exam_requested_date",
        f"ip_right_type IN ('patent', 'design') AND (event_category = 'exam_request' OR {EXPEDITED}) "
        "AND event_type NOT LIKE '%re_examination%'",
    ),
    ("accepted_date", "event_category = 'accepted'"),
    ("certified_date", "ip_right_type IN ('patent', 'design') AND event_category = 'certified'"),
    # An opposition to the grant or registration; a trade mark's application for removal for non-use is not one
    (
        "opposed_date",
        "(ip_right_type = 'patent' AND event_type IN "
        "('published_opposition_lodged', 'published_opposition_under_section_104_4_lodged')) "
        "OR (ip_right_type = 'trade_mark' AND event_type = 'dispute_registration')",
    ),
    ("first_assigned_date", ASSIGNED),
    ("term_extended_date", "event_type = 'published_extension_of_term_of_standard_patent_extension_granted'"),
]
# A right's lifetime runs from the date its term runs from (a patent's date of patent; a trade mark's or design's
# earliest filing date, which for a Madrid trade mark is the international registration's; a plant breeder's right's
# grant) to its end, or to the last date the register has finished recording
# ends, after which it counts as still in force. Trade marks and designs cease only after a six-month grace period
# for renewal, so the register's record of their ends stops six months early, as in `TIMELINE_LAG`.
OBSERVED_UNTIL = {"trade_mark": "2026-03-31", "design": "2026-03-31"}

# The links attachment (ADR 0022): how each right came to Australia. A right's own links name the applications it
# claims (its parent, its priorities, its PCT application); the *_child links are the other side of the same pairs.
# IP RAPID labels every PCT number `au`, and many other offices' priority numbers too, so a patent priority's office
# is read from its number: an Australian application number is ten digits, year first (or an associated provisional);
# a PCT number names its receiving office after "PCT"; any other number labelled `au` or `wo` has an unknown office.
AU_NUMBER = r"(19|20)\d{8}"
PRIORITY_LINKS = ("convention", "associated_provisional", "convention_priority")
DIVISIONAL_LINKS = ("divisional_parent", "divisional_parent_unresolved", "exclusive_parent")
# Google Patents (B4, ADR 0022): a family's citations within five years of its first priority are complete only when
# five years and the 18 months before citing applications are published have passed by the release (October 2026)
CITATIONS_5Y_COMPLETE = "2020-04-22"

OECD = (
    "AUS AUT BEL CAN CHL COL CRI CZE DNK EST FIN FRA DEU GRC HUN ISL IRL ISR ITA JPN KOR LVA LTU LUX MEX NLD NZL NOR "
    "POL PRT SVK SVN ESP SWE CHE TUR GBR USA"
).split()


def _postcode(col: str) -> str:
    """A 4-digit Australian postcode from free text ('800' becomes '0800'), or NULL."""
    return (
        f"CASE WHEN regexp_full_match(trim({col}), '\\d{{4}}') THEN trim({col}) "
        f"WHEN regexp_full_match(trim({col}), '\\d{{3}}') THEN '0' || trim({col}) END"
    )


def _fy(col: str) -> str:
    """The Australian financial year (ending 30 June) of a date."""
    return f"(year({col}) + CASE WHEN month({col}) >= 7 THEN 1 ELSE 0 END)"


DROPPED_DIR = Path(__file__).resolve().parent / "dropped"


def design_shells_sql() -> str:
    """Design records with nothing in them (ADR 0029): no date, applicant or class in IP RAPID, and no owner in IP
    Australia's register; numbered 1973 to 1982. They are dropped from the lenses, and listed with what IP RAPID
    gives (status) in `analysis/eda/dropped/design_shells.csv`, written with the rights lens."""
    return """
        SELECT d.application_number, d.status
        FROM {iprapid/design_rights} d
        LEFT JOIN {ipa_register/designs} g USING (application_number)
        WHERE d.application_date IS NULL AND coalesce(d.applicant_count, 0) = 0 AND d.main_class IS NULL
          AND coalesce(g.owner_count, 0) = 0 AND g.filed_date IS NULL AND g.main_class IS NULL
        ORDER BY 1"""


def rights_sql() -> str:
    """One row per right. Origin comes from every current applicant (ADR 0009): Australian if any is in Australia,
    overseas if at least one has a known country and none is in Australia, else unknown (NULL). IP RAPID's own
    `any_applicant_in_australia` turns unknown into false, so it is not used. IP RAPID publishes no agents for
    provisional applications, so `has_agent` is empty (unknown) for them rather than false (ADR 0010).

    Repairs from the Stage 1 section (ADR 0012): IP RAPID's "agent" is the address for service, which is often the
    applicant itself, so `has_agent` counts only an agent who is not one of the right's applicants or owners (by
    party id, or by name with case and punctuation removed); `main_area` is kept for patents only (IP RAPID repeats
    the Nice or Locarno class there for trade marks and designs); two placeholder dates are emptied (a retirement on
    1 January 1970, for 1,282 rights filed from 2013, and a registration before 1904); and a trade mark's days to
    registration are empty before 1986, when its registration date is its filing date. An Australian applicant's
    missing state is taken from the postcode's postal area (IP RAPID leaves it out for many Australian standard
    patents filed from FY2023; where both exist they agree for 99.9% of rights).

    The parties attachment (B1, ADR 0013) adds who filed the right beside who holds it now, and who represents them.
    The founding applicants are those IP RAPID marks `is_founding`, each as first recorded; the applicant columns
    above describe the current holder. `holder_changed` compares the two sets by party id, which IP RAPID keeps
    through changes of address; it is empty for patents filed before FY2003, for which IP RAPID keeps one set of
    applicants, entered when records moved between systems, so filer and holder cannot be told apart. The agent is
    the right's agent who is not an applicant and who acts for the most applicants across the register; an agent of
    five or more is counted as an attorney.

    The events attachment (B5, ADR 0015) adds each right's milestones (`RIGHT_EVENTS`) and its lifetime: the years
    from the date its term runs from to its end, or to `OBSERVED_UNTIL` if it is still in force then (`in_force` is
    then true, and the lifetime is unfinished). Only rights that were granted or registered have a lifetime.

    The last three attachments (ADR 0022). The links say how a right came to Australia (`filing_route`): for a
    standard or second-tier patent, as the national phase of a PCT application, as a divisional of an earlier
    application, claiming a priority abroad (the Paris Convention), claiming only an Australian application (usually a
    provisional), or directly; for a trade mark, through the Madrid system, as a divisional, with a priority or
    directly; for a design, as a divisional, with a priority or directly. Google Patents (B4) gives a patent's family:
    the offices it was filed in, whether the United States granted it, and the families citing it. The inventors are
    those of the family's representative publication (ADR 0008), with their countries and the expected numbers of
    women and men among them (from first names, `wgnd`); a family's inventors are counted for each of its Australian
    applications."""
    milestones = ",\n               ".join(
        f"min(event_effective_date) FILTER ({cond}) AS {col}" for col, cond in RIGHT_EVENTS
    )
    any_milestone = " OR ".join(f"({cond})" for cond in [*(c for _, c in RIGHT_EVENTS), EXPEDITED])
    term_from = (
        "CASE r.ip_right_type WHEN 'patent' THEN m.date_of_patent WHEN 'pbr' THEN r.registered "
        "ELSE r.earliest_filed_date END"
    )
    until = (
        "CASE r.ip_right_type "
        + " ".join(f"WHEN '{t}' THEN DATE '{d}'" for t, d in OBSERVED_UNTIL.items())
        + f" ELSE DATE '{TODAY}' END"
    )
    # In force at some time and observed since; with an end date no earlier than its term began (26 rights end
    # earlier), or, with none, a status of a right in force (6,621 rights have a status that ended them but no date)
    observed = (
        f"r.registered IS NOT NULL AND {term_from} <= {until} "
        f"AND coalesce(r.retired >= {term_from}, r.status IN ('granted', 'certified', 'protected', 'registered'))"
    )
    parts = []
    for kind in ("patent", "trade_mark", "design", "pbr"):
        parts.append(f"""
        SELECT '{kind}' AS ip_right_type, * FROM {{iprapid/{kind}_rights}}""")
    return f"""
    WITH r AS ({" UNION ALL BY NAME ".join(parts)}),
    applicants AS (
        SELECT ip_right_type, application_number,
               count(DISTINCT party_id) FILTER (country_code = 'au') AS applicants_au,
               count(DISTINCT party_id) FILTER (country_code <> 'au') AS applicants_overseas,
               count(DISTINCT party_id) FILTER (country_code IS NULL) AS applicants_country_unknown,
               string_agg(DISTINCT country_code, ' ' ORDER BY country_code) AS applicant_countries
        FROM {{iprapid/party}}
        WHERE party_role_category IN ('applicant', 'owner') AND is_current IS NOT false
        GROUP BY 1, 2
    ),
    party AS (
        SELECT ip_right_type, application_number, party_id, party_role_category,
               regexp_replace(lower(party_name), '[^a-z0-9]', '', 'g') AS name
        FROM {{iprapid/party}}
        WHERE party_role_category IN ('applicant', 'owner', 'applicant_agent')
    ),
    other_agents AS (  -- agents who are not one of the right's applicants or owners, at any time
        SELECT DISTINCT ag.ip_right_type, ag.application_number, ag.party_id
        FROM party ag
        ANTI JOIN party ap
            ON ap.ip_right_type = ag.ip_right_type AND ap.application_number = ag.application_number
           AND ap.party_role_category IN ('applicant', 'owner')
           AND (ap.party_id = ag.party_id OR ap.name = ag.name)
        WHERE ag.party_role_category = 'applicant_agent'
    ),
    clients AS (  -- how many different applicants each such agent acts for, across the whole register
        SELECT o.party_id, count(DISTINCT ap.party_id) AS clients
        FROM other_agents o
        JOIN party ap USING (ip_right_type, application_number)
        WHERE ap.party_role_category IN ('applicant', 'owner')
        GROUP BY 1
    ),
    agents AS (  -- the right's main agent: the one acting for the most applicants
        SELECT o.ip_right_type, o.application_number,
               arg_max(o.party_id, (c.clients, o.party_id)) AS agent_id, max(c.clients) AS agent_clients
        FROM other_agents o JOIN clients c USING (party_id)
        GROUP BY 1, 2
    ),
    agent_info AS (  -- 12,214 agents have more than one name (some are pseudonymised codes): the most used, so that
                     -- every build picks the same one (ADR 0019)
        SELECT agent_id, arg_max(party_name, (n, party_name)) AS agent_name
        FROM (SELECT party_id AS agent_id, party_name, count(*) AS n FROM {{iprapid/party}}
              WHERE party_role_category = 'applicant_agent' AND party_type = 'organisation' GROUP BY 1, 2)
        GROUP BY 1
    ),
    founders AS (  -- each founding applicant or owner, as first recorded
        SELECT * FROM (
            SELECT ip_right_type, application_number, party_id, party_type, country_code, state_code,
                   {_postcode("post_code")} AS postcode, effective_from_date AS since,
                   max(abn) OVER (PARTITION BY ip_right_type, application_number, party_id) AS abn,
                   -- ties (1,686 founders have two postcodes on their first day) go to the lowest postcode, so
                   -- that every build picks the same one (ADR 0019)
                   row_number() OVER (PARTITION BY ip_right_type, application_number, party_id
                                      ORDER BY effective_from_date, country_code NULLS LAST,
                                               {_postcode("post_code")} NULLS LAST, post_code NULLS LAST,
                                               state_code NULLS LAST) AS k
            FROM {{iprapid/party}}
            WHERE party_role_category IN ('applicant', 'owner') AND is_founding
        ) WHERE k = 1
    ),
    founding AS (
        SELECT ip_right_type, application_number,
               count(*) AS founder_count,
               arg_min_null(party_type, (since, party_id)) AS founder_type,
               arg_min_null(country_code, (since, party_id)) AS founder_country,
               CASE WHEN bool_or(country_code = 'au') THEN true
                    WHEN bool_or(country_code IS NOT NULL) THEN false END AS founding_australian,
               arg_min_null(postcode, (since, party_id)) FILTER (country_code = 'au') AS founder_postcode,
               arg_min_null(CASE state_code WHEN 'queensland' THEN 'qld' ELSE state_code END, (since, party_id))
                   FILTER (country_code = 'au') AS founder_state,
               arg_min(abn, (since, party_id)) FILTER (abn IS NOT NULL) AS founder_abn,
               list(party_id ORDER BY party_id) AS ids
        FROM founders GROUP BY 1, 2
    ),
    holders AS (
        SELECT ip_right_type, application_number, list(DISTINCT party_id ORDER BY party_id) AS ids
        FROM {{iprapid/party}}
        WHERE party_role_category IN ('applicant', 'owner') AND is_current IS NOT false
        GROUP BY 1, 2
    ),
    poa_state AS (  -- each postal area's state (ASGS 2021), for an Australian applicant whose state is missing
        SELECT poa_code,
               CASE state_name WHEN 'New South Wales' THEN 'nsw' WHEN 'Victoria' THEN 'vic' WHEN 'Queensland' THEN 'qld'
                   WHEN 'South Australia' THEN 'sa' WHEN 'Western Australia' THEN 'wa' WHEN 'Tasmania' THEN 'tas'
                   WHEN 'Northern Territory' THEN 'nt' WHEN 'Australian Capital Territory' THEN 'act' END AS state
        FROM {{abs_regions/poa}}
    ),
    milestones AS (  -- the events attachment (B5, ADR 0015)
        SELECT ip_right_type, application_number,
               {milestones},
               bool_or({EXPEDITED}) AS expedited,
               count(DISTINCT event_effective_date) FILTER ({ASSIGNED}) AS assignments
        FROM {{iprapid/events}} JOIN r USING (ip_right_type, application_number)
        WHERE is_standing AND event_effective_date BETWEEN DATE '1904-01-01' AND DATE '{TODAY}'
          AND event_effective_date <> DATE '1970-01-01'
          AND (event_category = 'ip_right_date'
               OR event_effective_date >= coalesce(earliest_filed_date, DATE '1904-01-01'))
          AND ({any_milestone})
        GROUP BY 1, 2
    ),
    links AS (  -- the links attachment (ADR 0022): the right's own links
        SELECT ip_right_type, application_number, link_type, linked_application_number AS number,
               nullif(nullif(link_date, DATE '1800-01-01'), DATE '1900-01-01') AS link_date,
               CASE WHEN link_type NOT IN {PRIORITY_LINKS} THEN NULL
                    WHEN ip_right_type <> 'patent' THEN linked_application_country
                    WHEN link_type = 'associated_provisional' OR regexp_full_match(linked_application_number,
                         '{AU_NUMBER}') THEN 'au'
                    WHEN upper(linked_application_number) LIKE 'PCT%'
                         THEN lower(substr(regexp_replace(upper(linked_application_number), '[^A-Z0-9]', '', 'g'),
                                           4, 2))
                    WHEN linked_application_country NOT IN ('au', 'wo') THEN linked_application_country
               END AS office
        FROM {{iprapid/links}}
    ),
    route AS (
        SELECT ip_right_type, application_number,
               bool_or(link_type = 'pct_application_number') AS pct,
               arg_min(number, (coalesce(link_date, DATE '9999-12-31'), number))
                   FILTER (link_type = 'pct_application_number') AS pct_number,
               bool_or(link_type IN {DIVISIONAL_LINKS}) AS divisional,
               bool_or(link_type = 'madrid_import') AS madrid,
               bool_or(link_type = 'madrid_export') AS madrid_export,
               -- a priority with no number (18,898 rights have one) is told apart by its office and date
               count(DISTINCT coalesce(number, concat_ws('|', office, link_date)))
                   FILTER (link_type IN {PRIORITY_LINKS}) AS priorities,
               bool_or(link_type IN {PRIORITY_LINKS} AND office IS DISTINCT FROM 'au') AS foreign_priority,
               bool_or(link_type IN {PRIORITY_LINKS} AND office = 'au') AS australian_priority,
               arg_min(office, (coalesce(link_date, DATE '9999-12-31'), office))
                   FILTER (link_type IN {PRIORITY_LINKS} AND office IS NOT NULL) AS priority_office
        FROM links GROUP BY 1, 2
    ),
    gp AS (  -- Google Patents (B4, ADR 0022): each Australian patent application's family; 734 numbers fall in two
             -- families, of which the first is taken so that every build picks the same one
        SELECT au_application AS application_number, min(family_id) AS family_id
        FROM {{google_patents/members}}
        WHERE country_code = 'AU' AND kind_code <> 'S' AND au_application <> ''
        GROUP BY 1
    ),
    acn_abn AS (  -- an ACN the ABR gives to exactly one ABN
        SELECT acn, any_value(abn) AS abn FROM {{abr/abns}} WHERE acn IS NOT NULL GROUP BY 1 HAVING count(*) = 1
    ),
    reg AS (  -- IP Australia's register, as its APIs give it (ADR 0028, 0029): owners' identifiers and country, and
              -- (trade marks) the register's own expedite events; for the gaps IP RAPID leaves, never instead of it
        SELECT 'trade_mark' AS ip_right_type, application_number, found, owner_count, any_owner_abn,
               lpad(owner_acn, 9, '0') AS owner_acn, owner_country, any_owner_in_australia, expedite_events,
               expedite_date
        FROM {{ipa_register/trade_marks}}
        UNION ALL BY NAME
        SELECT 'design' AS ip_right_type, application_number, found, owner_count, any_owner_abn,
               lpad(owner_acn, 9, '0') AS owner_acn, owner_country, any_owner_in_australia
        FROM {{ipa_register/designs}}
    ),
    shells AS ({design_shells_sql()}),
    dated AS (
        SELECT *,
               CASE WHEN applicant_country = 'au' THEN {_postcode("applicant_postcode")} END AS postcode_au,
               CASE WHEN year(gained_registration_status_date) >= 1904 THEN gained_registration_status_date END
                   AS registered,  -- one trade mark is dated 1 January 1901
               nullif(deemed_retired_date, DATE '1970-01-01') AS retired  -- all 1,282 were filed from 2013
        FROM r
        WHERE NOT (ip_right_type = 'design' AND application_number IN (SELECT application_number FROM shells))
    )
    SELECT
        r.application_number,
        r.ip_right_type,
        r.ip_right_sub_type,
        CASE WHEN r.ip_right_type = 'patent' THEN
            CASE WHEN r.ip_right_sub_type = 'standard_complete' THEN 'standard'
                 WHEN r.ip_right_sub_type = 'provisional' THEN 'provisional'
                 WHEN r.ip_right_sub_type IN ('innovation', 'petty') THEN 'second_tier' END
        END AS patent_type,
        r.status,
        r.application_date,
        r.earliest_filed_date,
        {_fy("r.application_date")} AS filing_fy,
        r.priority_date,
        r.registered AS registered_date,
        CASE WHEN NOT (r.ip_right_type = 'trade_mark' AND r.registered < DATE '1986-01-01')
             THEN date_diff('day', r.application_date, r.registered) END AS days_to_registration,
        r.retired AS retired_date,
        r.applicant_count,
        r.applicant_type,
        r.applicant_country,
        CASE WHEN r.applicant_country = 'au'
             THEN coalesce(CASE r.applicant_state WHEN 'queensland' THEN 'qld' ELSE r.applicant_state END, ps.state)
             ELSE r.applicant_state END AS applicant_state,
        r.postcode_au AS applicant_postcode,
        nullif(trim(r.applicant_postcode), '') AS applicant_postcode_raw,
        a.applicant_countries,
        coalesce(a.applicants_au, 0) AS applicants_au,
        coalesce(a.applicants_overseas, 0) AS applicants_overseas,
        coalesce(a.applicants_country_unknown, 0) AS applicants_country_unknown,
        r.any_applicant_abn AS applicant_abn,
        r.any_applicant_abn IS NOT NULL AS has_abn,
        CASE WHEN a.applicants_au > 0 THEN true WHEN a.applicants_overseas > 0 THEN false END AS australian_applicant,
        CASE WHEN r.ip_right_sub_type <> 'provisional'  -- no agents are published for provisionals
             THEN g.agent_id IS NOT NULL END AS has_agent,
        r.main_class,
        CASE WHEN r.ip_right_type = 'patent' AND r.main_area <> '99_unknown' THEN r.main_area END AS main_area,
        r.class_count,
        coalesce(f.founder_count, 0) AS founder_count,
        f.founder_type,
        f.founder_country,
        f.founding_australian,
        f.founder_postcode,
        coalesce(
            CASE WHEN f.founder_state IN ('nsw', 'vic', 'qld', 'sa', 'wa', 'tas', 'nt', 'act') THEN f.founder_state END,
            fs.state
        ) AS founder_state,
        f.founder_abn,
        coalesce(reg.any_owner_abn, ra.abn) AS register_abn,
        CASE WHEN reg.any_owner_abn IS NOT NULL THEN 'register' WHEN ra.abn IS NOT NULL THEN 'acn' END
            AS register_abn_basis,
        coalesce(
            f.founder_abn,
            -- the register's owner is the filer only while the right has not changed hands
            CASE WHEN NOT coalesce(len(f.ids) > 0 AND len(h.ids) > 0 AND f.ids <> h.ids, false)
                 THEN coalesce(reg.any_owner_abn, ra.abn) END
        ) AS filer_abn,
        r.any_applicant_abn IS NOT NULL OR coalesce(reg.any_owner_abn, ra.abn) IS NOT NULL AS has_abn_filled,
        reg.owner_country AS register_country,
        CASE WHEN a.applicants_au > 0 THEN true WHEN a.applicants_overseas > 0 THEN false
             WHEN reg.owner_country IS NOT NULL THEN reg.any_owner_in_australia END AS australian_applicant_filled,
        CASE WHEN r.ip_right_type = 'trade_mark' AND reg.found THEN reg.expedite_events IS NOT NULL END
            AS register_expedited,
        reg.expedite_date AS register_expedite_date,
        CASE WHEN r.ip_right_type = 'patent' AND coalesce(r.application_date, DATE '1900-01-01') < DATE '2002-07-01'
             THEN NULL  -- one set of applicants, entered when records moved between systems (ADR 0013)
             WHEN len(f.ids) > 0 AND len(h.ids) > 0 THEN f.ids <> h.ids END AS holder_changed,
        g.agent_id,
        ai.agent_name,
        g.agent_clients,
        CASE WHEN r.ip_right_sub_type = 'provisional' THEN NULL
             WHEN g.agent_clients >= 5 THEN 'attorney'
             WHEN g.agent_id IS NOT NULL THEN 'other_agent'
             ELSE 'self' END AS representation,
        m.date_of_patent,
        m.exam_requested_date,
        CASE WHEN m.expedited THEN true
             WHEN r.ip_right_type = 'trade_mark' OR m.exam_requested_date IS NOT NULL THEN false END AS exam_expedited,
        m.accepted_date,
        m.certified_date,
        m.opposed_date,
        CASE WHEN r.ip_right_type <> 'pbr' THEN coalesce(m.assignments, 0) END AS assignment_count,
        m.first_assigned_date,
        m.term_extended_date,
        CASE WHEN {observed} THEN r.retired IS NULL OR r.retired > {until} END AS in_force,
        CASE WHEN {observed}
             THEN round(date_diff('day', {term_from}, least(coalesce(r.retired, {until}), {until})) / 365.25, 2)
        END AS years_in_force,
        CASE WHEN r.ip_right_sub_type = 'provisional' OR r.ip_right_type = 'pbr' THEN NULL
             WHEN rt.pct THEN 'pct'
             WHEN rt.madrid THEN 'madrid'
             WHEN rt.divisional THEN 'divisional'
             WHEN rt.foreign_priority OR (r.ip_right_type <> 'patent' AND rt.priorities > 0) THEN 'convention'
             WHEN rt.australian_priority THEN 'australian_priority'
             ELSE 'direct' END AS filing_route,
        CASE WHEN r.ip_right_type <> 'pbr' THEN coalesce(rt.priorities, 0) END AS priority_claims,
        rt.priority_office,
        CASE WHEN r.ip_right_type = 'patent' THEN coalesce(rt.australian_priority, false) END AS australian_priority,
        CASE WHEN r.ip_right_type <> 'pbr' THEN coalesce(rt.divisional, false) END AS divisional,
        rt.pct_number,
        lower(substr(regexp_replace(upper(rt.pct_number), '[^A-Z0-9]', '', 'g'), 4, 2)) AS pct_office,
        CASE WHEN r.ip_right_type = 'trade_mark' THEN coalesce(rt.madrid_export, false) END AS madrid_export,
        gp.family_id,
        fam.first_priority_date AS family_priority_date,
        fam.n_offices AS family_offices,
        fam.granted_us AS family_granted_us,
        fam.citing_families AS family_citations,
        CASE WHEN fam.first_priority_date <= DATE '{CITATIONS_5Y_COMPLETE}' THEN fam.citing_families_5y END
            AS family_citations_5y,
        inv.inventors,
        inv.inventors_au,
        inv.inventors_abroad,
        inv.inventors_country_unknown,
        CASE WHEN inv.inventors_au > 0 THEN true WHEN inv.inventors_abroad > 0 THEN false END AS invented_in_australia,
        inv.women_expected AS inventors_women_expected,
        inv.men_expected AS inventors_men_expected,
        inv.gender_unknown AS inventors_gender_unknown
    FROM dated r
    LEFT JOIN applicants a USING (ip_right_type, application_number)
    LEFT JOIN agents g USING (ip_right_type, application_number)
    LEFT JOIN agent_info ai ON ai.agent_id = g.agent_id
    LEFT JOIN founding f USING (ip_right_type, application_number)
    LEFT JOIN holders h USING (ip_right_type, application_number)
    LEFT JOIN poa_state ps ON ps.poa_code = r.postcode_au
    LEFT JOIN poa_state fs ON fs.poa_code = f.founder_postcode
    LEFT JOIN milestones m USING (ip_right_type, application_number)
    LEFT JOIN route rt USING (ip_right_type, application_number)
    LEFT JOIN reg USING (ip_right_type, application_number)
    LEFT JOIN acn_abn ra ON ra.acn = reg.owner_acn
    LEFT JOIN gp ON r.ip_right_type = 'patent' AND gp.application_number = r.application_number
    LEFT JOIN {{google_patents/families}} fam ON fam.family_id = gp.family_id
    LEFT JOIN {{google_patents_inventors/family_inventors}} inv ON inv.family_id = gp.family_id
    """


def firms_sql() -> str:
    return f"""
    WITH ip AS (  -- applications by the filer: the first founding applicant with an ABN (ADR 0013, 0016), else the
                  -- register's owner while the right has not changed hands (ADR 0029)
        SELECT filer_abn AS abn,
               count(*) FILTER (patent_type = 'standard') AS n_patents_standard,
               count(*) FILTER (patent_type = 'provisional') AS n_patents_provisional,
               count(*) FILTER (patent_type = 'second_tier') AS n_patents_second_tier,
               count(*) FILTER (ip_right_type = 'trade_mark') AS n_trade_marks,
               count(*) FILTER (ip_right_type = 'design') AS n_designs
        FROM {lens_table("rights")} WHERE filer_abn IS NOT NULL GROUP BY 1
    ),
    first_filed AS (  -- each filer's first and last filing year, by type, from the filled filer ABN (ADR 0029)
        SELECT filer_abn AS abn,
               min(filing_fy) FILTER (patent_type = 'standard') AS patent_first_fy_filled,
               min(filing_fy) FILTER (ip_right_type = 'trade_mark') AS trade_mark_first_fy_filled,
               min(filing_fy) FILTER (ip_right_type = 'design') AS design_first_fy_filled
        FROM {lens_table("rights")} WHERE filer_abn IS NOT NULL GROUP BY 1
    ),
    held AS (  -- rights held now: the first current applicant or owner with an ABN
        SELECT applicant_abn AS abn, count(*) AS n_held, count(*) FILTER (in_force) AS n_held_in_force
        FROM {lens_table("rights")} WHERE applicant_abn IS NOT NULL GROUP BY 1
    ),
    rd_year AS (  -- one value per ABN and year: the latest report's, amended where it was (ADR 0010)
        SELECT abn, income_year, arg_max(coalesce(rd_expenditure_amended, rd_expenditure), report) AS rd
        FROM {{rdti/entities}} WHERE abn IS NOT NULL GROUP BY 1, 2
    ),
    rd AS (
        SELECT abn, count(*) AS rdti_years, avg(rd) AS rd_expenditure_mean, arg_max(rd, income_year) AS rd_latest
        FROM rd_year GROUP BY 1
    ),
    tax_year AS (  -- as rd_year: a later report can restate a year
        SELECT abn, income_year, arg_max(total_income, report) AS income FROM {{ato_ctt/entities}}
        WHERE abn IS NOT NULL GROUP BY 1, 2
    ),
    tax AS (
        SELECT abn, count(*) AS ato_ctt_years, arg_max(income, income_year) AS total_income_latest
        FROM tax_year GROUP BY 1
    ),
    filed AS (  -- applications as a founding applicant, a shared one split equally (IPLORD's weighting)
        SELECT applicant_id AS abn, sum(filed_weighted) AS ip_filed_weighted FROM {{iprapid/applicant_year}}
        WHERE applicant_id_type = 'abn' GROUP BY 1
    ),
    place AS (  -- the postal area's remoteness, advantage and state ('no usual address' areas are not places)
        SELECT p.poa_code, CASE WHEN p.ra_name NOT LIKE 'No usual address%' THEN p.ra_name END AS ra_name,
               s.value AS irsad_decile,
               CASE p.state_name WHEN 'New South Wales' THEN 'NSW' WHEN 'Victoria' THEN 'VIC'
                   WHEN 'Queensland' THEN 'QLD' WHEN 'South Australia' THEN 'SA' WHEN 'Western Australia' THEN 'WA'
                   WHEN 'Tasmania' THEN 'TAS'
                   WHEN 'Northern Territory' THEN 'NT' WHEN 'Australian Capital Territory' THEN 'ACT' END AS state
        FROM {{abs_regions/poa}} p
        LEFT JOIN {{abs_regions/seifa_poa}} s
          ON s.postal_area_code = p.poa_code AND s.index_type = 'IRSAD' AND s.measure = 'RWAD'
    )
    SELECT
        s.abn,
        s.entity_type_text AS entity_type,
        CASE
            WHEN s.entity_type_text = 'Australian Private Company' THEN 'Private company'
            WHEN s.entity_type_text = 'Australian Public Company' THEN 'Public company'
            WHEN s.entity_type_text = 'Individual/Sole Trader' THEN 'Sole trader'
            WHEN s.entity_type_text ILIKE '%superannuation%' OR s.entity_type_text ILIKE '%APRA%fund%' THEN 'Super fund'
            WHEN s.entity_type_text ILIKE '%government%' OR s.entity_type_text ILIKE '%statutory%' THEN 'Government'
            WHEN s.entity_type_text ILIKE '%trust%' THEN 'Trust'
            WHEN s.entity_type_text ILIKE '%partnership%' THEN 'Partnership'
            WHEN s.entity_type_text IS NULL THEN NULL
            ELSE 'Other'
        END AS entity_group,
        s.abn_status = 'ACT' AS abn_active,
        s.gst_status = 'ACT' AS gst_registered,
        coalesce(nullif(s.state, ''), place.state) AS state,  -- the ABR leaves 3,977 blank; 165 filled (ADR 0016)
        {_postcode("s.postcode")} AS postcode,
        place.ra_name AS remoteness,
        place.irsad_decile,
        s.asic_type,
        s.first_seen,
        round(date_diff('day', s.first_seen, DATE '{TODAY}') / 365.25, 1) AS age_years,
        CASE WHEN s.first_seen IS NULL THEN NULL
             WHEN s.first_seen = s.asic_registered THEN 'asic'
             WHEN s.abn_status = 'ACT' AND s.first_seen = s.abn_status_from THEN 'abn'
             WHEN s.first_seen = s.gst_status_from THEN 'gst' END AS age_basis,
        -- ABNs and GST began in 1999-2000: a business first seen then through them may be older
        s.first_seen < DATE '2001-01-01' AND s.first_seen IS DISTINCT FROM s.asic_registered AS age_truncated,
        s.in_iprapid_patent, s.in_iprapid_trade_mark, s.in_iprapid_design,
        s.in_iplord,  -- IPLORD (to FY2020) links 50,790 ABNs to IP that IP RAPID gives no ABN for (ADR 0016)
        s.in_rdti, s.in_austender, s.in_ato_ctt,
        s.patent_first_fy, s.trade_mark_first_fy, s.design_first_fy,
        s.in_register,
        ff.patent_first_fy_filled, ff.trade_mark_first_fy_filled, ff.design_first_fy_filled,
        s.ip_filed_total,
        coalesce(filed.ip_filed_weighted, 0) AS ip_filed_weighted,
        coalesce(ip.n_patents_standard, 0) AS n_patents_standard,
        coalesce(ip.n_patents_provisional, 0) AS n_patents_provisional,
        coalesce(ip.n_patents_second_tier, 0) AS n_patents_second_tier,
        coalesce(ip.n_trade_marks, 0) AS n_trade_marks,
        coalesce(ip.n_designs, 0) AS n_designs,
        coalesce(held.n_held, 0) AS n_held,
        coalesce(held.n_held_in_force, 0) AS n_held_in_force,
        coalesce(rd.rdti_years, 0) AS rdti_years,
        rd.rd_expenditure_mean,
        rd.rd_latest,
        coalesce(tax.ato_ctt_years, 0) AS ato_ctt_years,
        tax.total_income_latest,
        s.austender_contracts,
        s.austender_value
    FROM {{linkage/abn_spine}} s
    LEFT JOIN ip USING (abn)
    LEFT JOIN held USING (abn)
    LEFT JOIN rd USING (abn)
    LEFT JOIN tax USING (abn)
    LEFT JOIN filed USING (abn)
    LEFT JOIN first_filed ff USING (abn)
    LEFT JOIN place ON place.poa_code = {_postcode("s.postcode")}
    """


# Postcodes Australia Post keeps for post office boxes and large-volume receivers, which have no residents and are
# never ABS postal areas (S6, ADR 0017).
NON_GEOGRAPHIC = [
    ("0200", "0299"),
    ("0900", "0999"),
    ("1000", "1999"),
    ("5800", "5999"),
    ("6800", "6999"),
    ("7800", "7999"),
    ("8000", "9999"),
]
# The ranges for street addresses (Australia Post's delivery ranges; 6798 and 6799 are the Indian Ocean Territories,
# 2899 Norfolk Island). A code in one of them that is not a postal area is a post office box, a university or
# another large-volume receiver inside a delivery range, or a mistake.
DELIVERY = [
    ("0800", "0899"),
    ("2000", "2999"),
    ("3000", "3999"),
    ("4000", "4999"),
    ("5000", "5799"),
    ("6000", "6799"),
    ("7000", "7799"),
]


def postcode_range(col: str) -> str:
    """Which of Australia Post's ranges a 4-digit postcode is in: 'delivery', 'non_geographic' or 'none'. Whether it
    is an ABS postal area is a separate join."""

    def any_of(ranges):
        return " OR ".join(f"{col} BETWEEN '{lo}' AND '{hi}'" for lo, hi in ranges)

    return (
        f"CASE WHEN {col} IS NULL THEN NULL WHEN {any_of(NON_GEOGRAPHIC)} THEN 'non_geographic' "
        f"WHEN {any_of(DELIVERY)} THEN 'delivery' ELSE 'none' END"
    )


# The rules for postal-area rates (B3, ADR 0017). Applications are counted where the filer was (the first founding
# applicant in Australia), over the ten financial years of WINDOW, and rates are per year. A rate is empty where fewer
# than MIN_EXPECTED applications of that type would be expected at the national rate: a Poisson count of 10 has a 95%
# interval of about 5 to 18, so a smaller area's rate is mostly chance. Smaller areas are compared by pooling them
# (`sa3_code`) or by shrinking their rates, in Stage 2.
MIN_EXPECTED = 10
RATE_TYPES = [
    ("patents_standard", "patent_type = 'standard'"),
    ("trade_marks", "ip_right_type = 'trade_mark'"),
    ("designs", "ip_right_type = 'design'"),
]


def regions_sql() -> str:
    """One row per ABS postal area with people or businesses (2021), outside the areas the ABS keeps for people with no
    usual address, offshore and migratory, or outside Australia.

    Applications (ADR 0017) are counted by the filer's postcode (`founder_postcode`, ADR 0013), not the current
    holder's, so a right sold to another place stays where it was filed. Postcodes that are not postal areas (post
    office boxes, universities, large-volume receivers: S6) are not counted here; they are in the state totals of the
    rights lens. Rates per person count every filing; rates per business count organisations' filings only, as about
    a fifth to a quarter of filings are by individuals, and the denominator is GST-registered businesses."""
    lo, hi = WINDOW
    years = hi - lo + 1
    seifa = ",\n        ".join(
        f"max(value) FILTER (index_type = '{i}' AND measure = '{m}') AS {i.lower()}_{n}"
        for i in ("IRSAD", "IRSD", "IER", "IEO")
        for m, n in (("SCORE", "score"), ("RWAD", "decile"))
    )
    by_org = " AND founder_type = 'organisation'"
    counts = ",\n               ".join(
        [
            "count(*) FILTER (patent_type = 'standard') AS patents_standard",
            "count(*) FILTER (patent_type = 'provisional') AS patents_provisional",
            "count(*) FILTER (patent_type = 'second_tier') AS patents_second_tier",
            "count(*) FILTER (ip_right_type = 'trade_mark') AS trade_marks",
            "count(*) FILTER (ip_right_type = 'design') AS designs",
            *(f"count(*) FILTER ({cond}{by_org}) AS {t}_by_organisations" for t, cond in RATE_TYPES),
        ]
    )

    def rate(per: int, num: str, den: str, nat_num: str, nat_den: str) -> str:
        # empty where the area would expect fewer than MIN_EXPECTED at the national rate
        return (
            f"CASE WHEN {den} * nat.{nat_num} / nat.{nat_den} >= {MIN_EXPECTED} "
            f"THEN {per}.0 * {num} / {years} / {den} END"
        )

    per_person = [
        rate(10_000, f"coalesce(ip.{t}, 0)", "p.persons", t, "persons") + f" AS {t}_per_10k_people"
        for t, _ in RATE_TYPES
    ]
    org = [f"{t}_by_organisations" for t, _ in RATE_TYPES]
    per_business = [
        rate(1_000, f"coalesce(ip.{o}, 0)", "abr.active_gst_abns", o, "active_gst_abns") + f" AS {t}_per_1k_businesses"
        for (t, _), o in zip(RATE_TYPES, org, strict=True)
    ]
    rates = ",\n        ".join(per_person + per_business)
    nat = ", ".join(
        [
            *(
                f"sum(coalesce(ip.{t}, 0)) AS {t}, sum(coalesce(ip.{t}_by_organisations, 0)) AS {t}_by_organisations"
                for t, _ in RATE_TYPES
            ),
            "sum(p.persons) AS persons",
            "sum(abr.active_gst_abns) AS active_gst_abns",
        ]
    )
    return f"""
    WITH places AS (
        SELECT * FROM {{abs_regions/poa}}
        WHERE ra_name NOT IN ('Outside Australia', 'Migratory - Offshore - Shipping (WA)')
          AND ra_name NOT LIKE 'No usual address%'
    ),
    seifa AS (
        SELECT postal_area_code AS poa_code,
        {seifa}
        FROM {{abs_regions/seifa_poa}} GROUP BY 1
    ),
    census AS (  -- the Census gives 0 where a median has no one to describe (no renters, no residents): empty here
        SELECT replace(POA_CODE_2021, 'POA', '') AS poa_code,
               nullif(Median_age_persons, 0) AS median_age,
               nullif(Median_tot_prsnl_inc_weekly, 0) AS median_personal_income_weekly,
               nullif(Median_tot_hhd_inc_weekly, 0) AS median_household_income_weekly,
               nullif(Median_rent_weekly, 0) AS median_rent_weekly,
               nullif(Average_household_size, 0) AS average_household_size
        FROM {{abs_census/poa_g02}}
    ),
    abr AS (
        SELECT postcode AS poa_code,
               count(*) FILTER (abn_status = 'ACT') AS active_abns,
               count(*) FILTER (abn_status = 'ACT' AND gst_status = 'ACT') AS active_gst_abns
        FROM {{abr/abns}} GROUP BY 1
    ),
    ip AS (  -- by the filer's postcode (ADR 0017)
        SELECT founder_postcode AS poa_code,
               {counts}
        FROM {lens_table("rights")}
        WHERE founder_postcode IS NOT NULL AND filing_fy BETWEEN {lo} AND {hi}
        GROUP BY 1
    ),
    firms AS (
        SELECT postcode AS poa_code,
               count(*) FILTER (abn_active AND ip_filed_total > 0) AS ip_filing_firms,
               count(*) FILTER (abn_active AND in_rdti) AS rdti_firms,
               count(*) FILTER (abn_active AND in_rdti AND ip_filed_total = 0) AS rdti_firms_no_ip
        FROM {lens_table("firms")} GROUP BY 1
    ),
    contracts AS (  -- each contract once, at its latest notice (as in `linkage/abn_spine`, ADR 0010)
        SELECT parent_cn_id,
               arg_max(supplier_abn, (amendment IS NOT NULL, amendment, published)) FILTER (supplier_abn IS NOT NULL)
                 AS abn,
               arg_max(trim(supplier_postcode), (amendment IS NOT NULL, amendment, published))
                 FILTER (supplier_postcode IS NOT NULL) AS poa_code,
               arg_max(value, (amendment IS NOT NULL, amendment, published)) FILTER (value IS NOT NULL) AS value,
               min(published)::DATE AS first_published
        FROM {{austender/contracts}} GROUP BY 1
    ),
    tender AS (  -- contracts first published in the window, by the supplier's postcode on the contract (ADR 0018)
        SELECT poa_code, count(DISTINCT abn) AS austender_suppliers, count(*) AS austender_contracts,
               sum(value) AS austender_value
        FROM contracts WHERE {_fy("first_published")} BETWEEN {lo} AND {hi} GROUP BY 1
    ),
    nat AS (  -- national rates over the lens's places, for the minimum expected count
        SELECT {nat}
        FROM places p LEFT JOIN ip USING (poa_code) LEFT JOIN abr USING (poa_code)
    )
    SELECT
        p.poa_code,
        p.state_name AS state,
        p.ra_name AS remoteness,
        p.share_major_cities,
        p.sa3_code,
        p.sa3_name,
        p.persons,
        seifa.* EXCLUDE (poa_code),
        census.* EXCLUDE (poa_code),
        coalesce(abr.active_abns, 0) AS active_abns,
        coalesce(abr.active_gst_abns, 0) AS active_gst_abns,
        coalesce(ip.patents_standard, 0) AS patents_standard,
        coalesce(ip.patents_provisional, 0) AS patents_provisional,
        coalesce(ip.patents_second_tier, 0) AS patents_second_tier,
        coalesce(ip.trade_marks, 0) AS trade_marks,
        coalesce(ip.designs, 0) AS designs,
        coalesce(ip.patents_standard_by_organisations, 0) AS patents_standard_by_organisations,
        coalesce(ip.trade_marks_by_organisations, 0) AS trade_marks_by_organisations,
        coalesce(ip.designs_by_organisations, 0) AS designs_by_organisations,
        coalesce(firms.ip_filing_firms, 0) AS ip_filing_firms,
        coalesce(firms.rdti_firms, 0) AS rdti_firms,
        coalesce(firms.rdti_firms_no_ip, 0) AS rdti_firms_no_ip,
        coalesce(tender.austender_suppliers, 0) AS austender_suppliers,
        coalesce(tender.austender_contracts, 0) AS austender_contracts,
        tender.austender_value,
        {rates}
    FROM places p
    CROSS JOIN nat
    LEFT JOIN seifa USING (poa_code)
    LEFT JOIN census USING (poa_code)
    LEFT JOIN abr USING (poa_code)
    LEFT JOIN ip USING (poa_code)
    LEFT JOIN firms USING (poa_code)
    LEFT JOIN tender USING (poa_code)
    """


# The regions lens's attachments (ADR 0018): every value of five area sources, one row per postal area, source,
# indicator and period, in `region_indicators`. A count published for SA2s (or PHIDU's PHAs) is split among postal areas
# by the share of the area's 2021 residents living in each (by mesh block; an area with no residents is split by its
# mesh blocks); a level (a median, mean, rate or percentage) is averaged over the areas overlapping a postal area,
# weighted by the residents they share.
CENSUS_TABLES = {
    "G01": "Selected person characteristics",
    "G02": "Medians and averages",
    "G18": "Core activity need for assistance",
    "G19": "Long-term health conditions",
    "G20": "Count of selected long-term health conditions",
    "G23": "Voluntary work for an organisation or group",
    "G25": "Unpaid assistance to a person with a disability, health condition or due to old age",
    "G43": "Selected labour force, education and migration characteristics",
    "G44": "Place of usual residence one year ago",
    "G45": "Place of usual residence five years ago",
    "G46": "Labour force status by age by sex",
    "G50": "Non-school qualification: field of study by age by sex",
    "G54": "Industry of employment by age by sex",
    "G60": "Occupation by age by sex",
}
# A Data by Region item is a level, not a count that can be split or summed, if its unit is one or its label says so
DBR_LEVEL_UNITS = ("PCT", "DECILE", "QUARTILE", "YR", "RATE", "PSNS_PER_SQKM", "ML_PER_HA")
LEVEL_WORDS = "median|mean|average"
# PHIDU's measures are free text: a rate, ratio, percentage or average is a level, the rest are counts of people,
# events, dwellings or years. Its confidence limits are left out: they cannot be carried through an average.
PHIDU_LEVEL = r"(^|[^a-z])(sr|asr|sdr)([^a-z]|$)|%|per cent|rate|ratio|median|average|mean|index"


def region_indicators_sql() -> str:
    census = " UNION ALL ".join(
        f"""
        SELECT replace(POA_CODE_2021, 'POA', '') AS poa_code, '{t}' AS t, indicator, value
        FROM (UNPIVOT (SELECT POA_CODE_2021, COLUMNS(* EXCLUDE POA_CODE_2021)::DOUBLE
                       FROM {{abs_census/poa_{t.lower()}}})
              ON COLUMNS(* EXCLUDE POA_CODE_2021) INTO NAME indicator VALUE value)"""
        for t in CENSUS_TABLES
    )
    topics = " ".join(f"WHEN '{t}' THEN '{t}: {name}'" for t, name in CENSUS_TABLES.items())
    dbr_level = ", ".join(f"'{u}'" for u in DBR_LEVEL_UNITS)
    return f"""
    WITH places AS (SELECT poa_code FROM {lens_table("regions")}),
    mb AS (  -- 2021 residents and mesh blocks in each SA2 and postal area
        SELECT sa2_code, poa_code, sum(coalesce(persons, 0)) AS persons, count(*) AS blocks
        FROM {{abs_regions/mesh_blocks}} WHERE poa_code IN (SELECT poa_code FROM places) GROUP BY 1, 2
    ),
    pha_mb AS (  -- the same for PHIDU's areas, each one SA2 or a group of them
        SELECT p.pha_code AS area, mb.poa_code, sum(mb.persons) AS persons, sum(mb.blocks) AS blocks
        FROM {{phidu/pha_sa2}} p JOIN mb USING (sa2_code) GROUP BY 1, 2
    ),
    overlap AS (SELECT 'sa2' AS kind, sa2_code AS area, poa_code, persons, blocks FROM mb
                UNION ALL SELECT 'pha', area, poa_code, persons, blocks FROM pha_mb),
    w AS (  -- share of the area's count in the postal area; and of the postal area's people in the area, for levels
        SELECT kind, area, poa_code,
               CASE WHEN sum(persons) OVER (PARTITION BY kind, area) > 0
                    THEN persons / sum(persons) OVER (PARTITION BY kind, area)
                    ELSE blocks / sum(blocks) OVER (PARTITION BY kind, area) END AS split,
               CASE WHEN sum(persons) OVER (PARTITION BY kind, poa_code) > 0 THEN persons ELSE blocks END AS weight
        FROM overlap
    ),
    census AS (
        SELECT c.poa_code, 'census' AS source,
               CASE c.t {topics} END AS topic,
               c.t || '.' || c.indicator AS indicator, l.long AS label, '2021' AS period,
               -- the Census gives 0 for a median or average with no one to describe (ADR 0010)
               CASE WHEN c.t = 'G02' THEN nullif(c.value, 0) ELSE c.value END AS value,
               CASE WHEN c.t = 'G02' OR c.indicator ILIKE 'perc%' THEN 'level' ELSE 'count' END AS kind,
               'direct' AS method,
               CASE WHEN c.indicator ILIKE 'perc%' THEN 'percent' WHEN c.t <> 'G02' THEN 'people' END AS unit
        FROM ({census}) c
        LEFT JOIN (SELECT short, regexp_extract(datapackfile, 'G\\d\\d') AS t, any_value(long) AS long
                   FROM {{abs_census/cells}} GROUP BY 1, 2) l ON l.short = c.indicator AND l.t = c.t
        WHERE c.poa_code IN (SELECT poa_code FROM places)
    ),
    dbr AS (
        SELECT region AS area, data_item AS indicator, any_value(data_item_label) AS label, time_period AS period,
               any_value(trim(unit_of_measure_label || coalesce(' (' || unit_of_multiplier_label || ')', ''))) AS unit,
               any_value(CASE WHEN unit_of_measure IN ({dbr_level})
                                OR regexp_matches(lower(data_item_label), '{LEVEL_WORDS}') THEN 'level'
                              ELSE 'count' END) AS kind,
               any_value(split_part(data_item_label, ':', 1)) AS topic, any_value(value) AS value
        FROM {{abs_regions/region_asgs}} WHERE region_type = 'SA2' AND value IS NOT NULL GROUP BY 1, 2, 4
    ),
    cabee AS (
        SELECT sa2_code AS area,
               CASE cube WHEN '8165DC08' THEN 'employment' ELSE 'turnover' END || '|' || industry_code || '|' || size
                 AS indicator,
               'Businesses: ' || industry_label || ', ' || size AS label,
               regexp_extract(table_title, 'June \\d{{4}}') AS period, 'businesses' AS unit, 'count' AS kind,
               'Businesses by industry division and ' ||
                 CASE cube WHEN '8165DC08' THEN 'employment size' ELSE 'turnover size' END AS topic,
               value
        FROM {{abs_cabee/cubes}} WHERE cube IN ('8165DC08', '8165DC09') AND sa2_code IS NOT NULL AND value IS NOT NULL
    ),
    phidu AS (
        SELECT area_code AS area,
               workbook || '|' || sheet || '|' || indicator || '|' || coalesce(sub_indicator, '') || '|' || measure
                 AS indicator,
               indicator || coalesce(': ' || sub_indicator, '') || ' (' || measure || ')' AS label,
               period, measure AS unit,
               CASE WHEN regexp_matches(lower(measure), '{PHIDU_LEVEL}') THEN 'level' ELSE 'count' END AS kind,
               workbook AS topic, value
        FROM {{phidu/indicators}}
        WHERE area_type = 'pha' AND measure NOT LIKE '%C.I.%' AND value IS NOT NULL
    ),
    split AS (  -- SA2 and PHA values to postal areas
        SELECT 'data_by_region' AS source, 'sa2' AS kind_of_area, * FROM dbr
        UNION ALL SELECT 'cabee', 'sa2', * FROM cabee
        UNION ALL SELECT 'phidu', 'pha', * FROM phidu
    ),
    apportioned AS (
        SELECT w.poa_code, s.source, any_value(s.topic) AS topic, s.indicator, any_value(s.label) AS label, s.period,
               CASE any_value(s.kind) WHEN 'count' THEN sum(s.value * w.split)
                    ELSE sum(s.value * w.weight) / nullif(sum(w.weight), 0) END AS value,
               any_value(s.unit) AS unit, any_value(s.kind) AS kind,
               'from ' || CASE any_value(s.kind_of_area) WHEN 'sa2' THEN 'SA2s' ELSE 'PHAs' END AS method
        FROM split s JOIN w ON w.kind = s.kind_of_area AND w.area = s.area
        GROUP BY w.poa_code, s.source, s.indicator, s.period
    ),
    cer AS (  -- installations and capacity per calendar year, by the installation's postcode
        SELECT postcode AS poa_code, 'cer' AS source, technology AS topic, technology || '|' || series AS indicator,
               replace(technology, '_', ' ') || ': ' || any_value(measure) AS label, left(month, 4) AS period,
               sum(value) AS value, series AS unit, 'count' AS kind, 'direct' AS method
        FROM {{cer/installations}}
        WHERE postcode IN (SELECT poa_code FROM places) AND value IS NOT NULL
        GROUP BY postcode, technology, series, left(month, 4)
    )
    SELECT poa_code, source, topic, indicator, label, period, value, unit, kind = 'count' AS additive, method
    FROM (SELECT * FROM census
          UNION ALL SELECT poa_code, source, topic, indicator, label, period, value, kind, method, unit FROM apportioned
          UNION ALL SELECT poa_code, source, topic, indicator, label, period, value, kind, method, unit FROM cer)
    """


# The national lens's places (ADR 0019). A country is an ISO 3166 code. Former states keep their ISO 3166-3 codes, so
# that WIPO's filings by residents of the Soviet Union or East Germany are not lost; they are never added to their
# successors. WIPO's unknown origin ('**') is kept as its own row, 'ZZZ', so that totals over origins can be rebuilt.
# Aggregates (the World Bank's regions, the OECD's and EU totals, the world) are left out.
FORMER_STATES = {
    "SU": ("SUN", "Soviet Union"),
    "DD": ("DDR", "German Democratic Republic"),
    "CS": ("CSK", "Czechoslovakia"),
    "YU": ("YUG", "Yugoslavia"),
    "ZR": ("ZAR", "Zaire"),
    "AN": ("ANT", "Netherlands Antilles"),
}
UNKNOWN_ORIGIN = ("**", "ZZZ", "Origin unknown")
# The WIPO series in the core lens: filings by residents of each country, summed over every office
WIPO_CORE = {
    10: ("WIPO.PAT.APP", "Patent applications filed worldwide by residents (all offices)"),
    23: ("WIPO.PAT.GRANT", "Patent grants received worldwide by residents (all offices)"),
    48: ("WIPO.TM.CLASS", "Trade mark applications by residents, counted in classes (all offices)"),
    68: ("WIPO.DES.COUNT", "Industrial design applications by residents, counted in designs (all offices)"),
}
# Every OECD flow in the corpus goes to `national_indicators`, one indicator per combination of its dimensions
# (ADR 0019). These columns are not dimensions: the place, the time, the value's flags and its display settings.
OECD_FLOWS = [
    "msti", "patents_coinventors", "patents_domestic_ownership_abroad", "patents_foreign_ownership",
    "patents_environment", "patents_wipo_fields", "patents_regions", "innovation_ip_methods", "ip_tax_regimes",
    "venture_capital", "business_births_deaths", "business_survival", "business_high_growth", "child_wellbeing",
    "wellbeing_current", "wellbeing_future", "wellbeing_inequality", "wellbeing_by_age", "wellbeing_by_sex",
    "wellbeing_by_education", "sdg_01_no_poverty", "sdg_02_zero_hunger", "sdg_09_industry_innovation",
    "sdg_13_climate_action",
]  # fmt: skip
OECD_NOT_DIMENSIONS = {
    "flow", "frequency_of_observation", "reference_area", "time_period", "observation_status", "observation_status_2",
    "observation_status_3", "aux_observation_status", "confidentiality_status", "unit_multiplier", "decimals",
    "base_period", "base_year", "price_reference_year", "territorial_level", "country",
}  # fmt: skip
OECD_STATUS = ["observation_status", "observation_status_2", "observation_status_3", "aux_observation_status"]
# Closing the Gap's descriptive columns: together with the table and jurisdiction, they name one series
CTG_SERIES = [
    "measure", "age", "sex", "indigenous_status", "remoteness", "seifa_irsd", "description1", "description2",
    "description3", "description4", "description6", "description7", "uncertainty",
]  # fmt: skip


def _places() -> str:
    """A VALUES list of (ISO alpha-2, alpha-3, kind, name) for every current country, former state and the unknown
    origin."""
    rows = [(c.alpha_2, c.alpha_3, "country", None) for c in pycountry.countries]
    rows += [(a2, a3, "former state", name) for a2, (a3, name) in FORMER_STATES.items()]
    rows += [(UNKNOWN_ORIGIN[0], UNKNOWN_ORIGIN[1], "origin unknown", UNKNOWN_ORIGIN[2])]
    q = lambda v: "NULL" if v is None else "'" + v.replace("'", "''") + "'"  # noqa: E731
    return ", ".join(f"({q(a2)}, {q(a3)}, {q(k)}, {q(n)})" for a2, a3, k, n in sorted(rows))


def _slug(col: str) -> str:
    return f"trim(regexp_replace(lower({col}), '[^a-z0-9]+', '_', 'g'), '_')"


def _year_of(col: str) -> str:
    """The calendar year a published period ends in: '2018-19' and '2018–19' (financial years) give 2019; '2016 to
    2021', '2021-2023' and '41 (2004)' their last year; 'Apr-06' 2006; NULL where the text holds no year."""
    return (
        f"CASE WHEN regexp_matches({col}, '^\\s*\\d{{4}}\\s*[-–]\\s*\\d{{2}}(\\s|\\(|$)') "
        f"THEN CAST(left(trim({col}), 4) AS INTEGER) + 1 "
        f"WHEN regexp_matches({col}, '\\d{{4}}') THEN CAST(regexp_extract_all({col}, '\\d{{4}}')[-1] AS INTEGER) "
        f"WHEN regexp_matches({col}, '^[A-Z][a-z]{{2}}-\\d{{2}}$') "
        f"THEN CAST(right({col}, 2) AS INTEGER) "
        f"+ CASE WHEN CAST(right({col}, 2) AS INTEGER) > 50 THEN 1900 ELSE 2000 END "
        f"END"
    )


def national_sql() -> str:
    """One row per country, year and indicator: the World Bank's 24 indicators, WIPO's filings by residents of each
    country at every office, and the OECD's R&D intensity (ADR 0010, 0019)."""
    oecd = ", ".join(f"'{c}'" for c in OECD)
    cases = " ".join(f"WHEN {k} THEN '{c}'" for k, (c, _) in WIPO_CORE.items())
    names = " ".join(f"WHEN {k} THEN '{n}'" for k, (_, n) in WIPO_CORE.items())
    return f"""
    WITH iso(a2, a3, kind, name) AS (VALUES {_places()}),
    wdi AS (
        SELECT p.iso3, p.country, p.year, p.indicator, p.indicator_name, p.value, NULL::VARCHAR AS status,
               'WDI' AS source
        FROM {{wdi/panel}} p JOIN {{wdi/countries}} c ON c.iso3 = p.iso3
        WHERE NOT c.aggregate
    ),
    oecd AS (  -- R&D intensity from the OECD's MSTI, beside the World Bank's (never spliced: ADR 0010)
        SELECT m.reference_area AS iso3, any_value(m.reference_area_label) AS country,
               CAST(m.time_period AS INTEGER) AS year, 'OECD.MSTI.' || m.measure AS indicator,
               any_value(m.measure_label) || ', % of GDP (OECD MSTI)' AS indicator_name,
               any_value(m.value) AS value, any_value(m.observation_status_label) AS status, 'OECD' AS source
        FROM {{oecd/msti}} m JOIN iso ON iso.a3 = m.reference_area AND iso.kind = 'country'
        WHERE m.measure IN ('G', 'B') AND m.unit_of_measure = 'PT_B1GQ' AND m.value IS NOT NULL
        GROUP BY m.reference_area, m.time_period, m.measure
    ),
    wipo AS (  -- former states and the unknown origin kept (ADR 0019)
        SELECT iso.a3 AS iso3, any_value(o.origin) AS country, o.year,
               CASE o.indicator_id {cases} END AS indicator,
               CASE o.indicator_id {names} END AS indicator_name,
               sum(o.value) AS value, NULL::VARCHAR AS status, 'WIPO' AS source
        FROM {{wipo_ipstats/office_origin}} o JOIN iso ON iso.a2 = o.origin_code
        WHERE o.indicator_id IN ({", ".join(map(str, WIPO_CORE))}) AND o.breakdown IS NULL
        GROUP BY iso.a3, o.year, o.indicator_id
    )
    SELECT u.* REPLACE (coalesce(n.name, iso.name, u.country) AS country),  -- one name per place (the World Bank's)
           coalesce(iso.kind, 'country') AS entity, u.iso3 IN ({oecd}) AS oecd, u.iso3 = 'AUS' AS australia
    FROM (SELECT * FROM wdi UNION ALL SELECT * FROM wipo UNION ALL SELECT * FROM oecd) u
    LEFT JOIN {{wdi/countries}} n ON n.iso3 = u.iso3
    LEFT JOIN (SELECT DISTINCT a3, kind, name FROM iso) iso ON iso.a3 = u.iso3
    """


def _oecd_flow_sql(flow: str, iso: str) -> str:
    """One OECD flow, long: one indicator per combination of its dimensions, coded 'OECD.<FLOW>.<codes>' and labelled
    by the dimensions' labels (a dimension that does not apply, '_Z', is left out of the label)."""
    import duckdb

    from .data import table

    cols = [r[0] for r in duckdb.sql(f"DESCRIBE SELECT * FROM {table('oecd', flow)}").fetchall()]
    dims = [c for c in cols if f"{c}_label" in cols and c not in OECD_NOT_DIMENSIONS]
    bases = [c for c in ("base_period", "base_year") if c in cols]
    code = ", ".join(dims + [f"nullif({b}, '_Z')" for b in bases])
    label = ", ".join(f"CASE WHEN {d} <> '_Z' THEN {d}_label END" for d in dims)
    # a normal value ('A') carries no flag; a suppressed one ('Q', confidential) is published as 0, so it is emptied
    status = ", ".join(f"CASE WHEN {c} <> 'A' THEN {c}_label END" for c in OECD_STATUS if f"{c}_label" in cols)
    suppressed = "observation_status = 'Q'" if "observation_status" in cols else "false"
    unit = ["unit_of_measure_label"] if "unit_of_measure_label" in cols else ["NULL"]
    if "unit_multiplier" in cols:
        unit.append("CASE WHEN unit_multiplier <> '0' THEN unit_multiplier_label END")
    unit = ", ".join(unit + [f"'base ' || nullif({b}, '_Z')" for b in bases])
    where = [f"(reference_area IN ({iso}) OR reference_area = 'YUG_F')"]
    where.append(f"(value IS NOT NULL OR {'value_text IS NOT NULL OR ' if 'value_text' in cols else ''}{suppressed})")
    if "territorial_level" in cols:
        where.append("territorial_level = 'CTRY'")  # its regions are within countries, not countries
    if flow == "msti":  # the core lens holds these (OECD.MSTI.G and .B)
        where.append("NOT (measure IN ('G', 'B') AND unit_of_measure = 'PT_B1GQ')")
    return f"""
        SELECT CASE reference_area WHEN 'YUG_F' THEN 'YUG' ELSE reference_area END AS iso3,
               reference_area_label AS place_name, CAST(left(time_period, 4) AS INTEGER) AS year,
               time_period AS period, 'oecd' AS source, '{flow}' AS dataset,
               'OECD.{flow.upper()}.' || concat_ws('.', {code}) AS indicator, concat_ws(', ', {label}) AS label,
               CASE WHEN {suppressed} THEN NULL ELSE value END AS value,
               {"value_text" if "value_text" in cols else "NULL::VARCHAR"} AS value_text,
               concat_ws(', ', {unit}) AS unit, nullif(concat_ws('; ', {status or "NULL"}), '') AS status
        FROM {{oecd/{flow}}}
        WHERE {" AND ".join(where)}"""


def national_indicators_sql() -> str:
    """The national lens's attachments, long (ADR 0019): one row per country, source, indicator and period, holding
    every value of the GII, every OECD flow, WIPO's other tables, Measuring What Matters and Closing the Gap."""
    iso = ", ".join(f"'{c.alpha_3}'" for c in pycountry.countries)
    oecd = ", ".join(f"'{c}'" for c in OECD)
    core_wipo = ", ".join(map(str, WIPO_CORE))
    wipo_label = "regexp_replace(o.indicator, '^\\S+\\s*-\\s*', '') || coalesce(': ' || o.breakdown, '')"
    wipo_unit = "CASE WHEN o.indicator ILIKE '%(days)%' THEN 'days' ELSE 'number' END"
    flows = "\n        UNION ALL".join(_oecd_flow_sql(f, iso) for f in OECD_FLOWS)
    gii_status = (
        "nullif(concat_ws('; ', CASE WHEN outdated = '1' THEN 'outdated: older than the most common data year' END, "
        "CASE WHEN dmc = '1' THEN 'data minimum coverage not met' END), '')"
    )
    mwm_period = (
        "regexp_full_match(row, '(\\d{4}([-–]\\d{2}(\\d{2})?)?|[A-Z][a-z]{2}-\\d{2}|\\d+ \\(\\d{4}\\))( \\([a-z]\\))?')"
    )
    ctg_key = ", ".join(CTG_SERIES + ["unit"])
    ctg_label = ", ".join(CTG_SERIES)
    col_fy = "nullif(regexp_extract(\"column\", '\\d{4}-\\d{2}'), '')"  # an ABS column such as "2023-24 | $'000"
    col_no_fy = "regexp_replace(\"column\", '\\d{4}-\\d{2}( \\| )?', '')"
    return f"""
    WITH iso(a2, a3, kind, name) AS (VALUES {_places()}),
    oecd AS ({flows}
    ),
    wipo AS (
        SELECT iso.a3 AS iso3, any_value(o.origin) AS place_name, o.year, CAST(o.year AS VARCHAR) AS period,
               'wipo' AS source, 'office_origin' AS dataset,
               'WIPO.ORIGIN.' || o.indicator_id || coalesce('.' || {_slug("o.breakdown")}, '') AS indicator,
               any_value({wipo_label}) || ' (by origin, all offices)' AS label, sum(o.value) AS value,
               NULL::VARCHAR AS value_text, any_value({wipo_unit}) AS unit, NULL::VARCHAR AS status
        FROM {{wipo_ipstats/office_origin}} o JOIN iso ON iso.a2 = o.origin_code
        -- the core lens holds the four totals; a foreign-oriented family is counted at each office it goes to, so
        -- summing indicator 21 over offices would count families more than once
        WHERE o.indicator_id <> 21 AND NOT (o.indicator_id IN ({core_wipo}) AND o.breakdown IS NULL)
        GROUP BY iso.a3, o.year, o.indicator_id, o.breakdown
        UNION ALL
        SELECT iso.a3, o.origin, o.year, CAST(o.year AS VARCHAR), 'wipo', 'office_origin',
               'WIPO.AU.' || o.indicator_id || coalesce('.' || {_slug("o.breakdown")}, ''),
               {wipo_label} || ' (at IP Australia, by origin)', o.value, NULL, {wipo_unit}, NULL
        FROM {{wipo_ipstats/office_origin}} o JOIN iso ON iso.a2 = o.origin_code
        WHERE o.office_code = 'AU'
        UNION ALL  -- by office: the office's country (regional offices, such as the EPO, are not countries)
        SELECT iso.a3, o.office, o.year, CAST(o.year AS VARCHAR), 'wipo', 'office',
               'WIPO.OFFICE.' || o.right || '.' || o.indicator_id || coalesce('.' || {_slug("o.breakdown")}, ''),
               {wipo_label} || ' (' || o.right || ', by office)', o.value, NULL, {wipo_unit}, NULL
        FROM {{wipo_ipstats/office}} o JOIN iso ON iso.a2 = o.office_code AND iso.kind = 'country'
        UNION ALL
        SELECT iso.a3, o.origin, o.year, CAST(o.year AS VARCHAR), 'wipo', 'pmh', 'WIPO.PMH.' || o.indicator_id,
               regexp_replace(o.indicator, '^\\S+\\s*-\\s*', '') || ' (' || upper(o.system) || ', by origin)', o.value,
               NULL, CASE WHEN o.indicator_id = 1042 THEN 'percent' ELSE 'number' END, NULL
        FROM {{wipo_ipstats/pmh}} o JOIN iso ON iso.a2 = o.origin_code
    ),
    g AS (
        SELECT d.*, coalesce(nullif(d.num, ''), 'GII') AS node, CAST(d.datayr AS INTEGER) AS y
        FROM {{gii/data}} d
    ),
    gii AS (  -- the GII 2026 edition: a composite's year is the edition's; an indicator's is its data year
        SELECT iso3, economy_name AS place_name, coalesce(y, 2026) AS year,
               coalesce(CAST(y AS VARCHAR), 'GII 2026') AS period, 'gii' AS source, 'data' AS dataset,
               'GII.' || node || '.' || m.k AS indicator, name || ': ' || m.l AS label,
               CASE m.k WHEN 'score' THEN score WHEN 'rank' THEN rank WHEN 'value' THEN value_screen END AS value,
               CASE m.k WHEN 'strength_overall' THEN sw_overall WHEN 'strength_income_group' THEN sw_incgrp END
                 AS value_text,
               CASE m.k WHEN 'score' THEN 'score, 0 to 100' WHEN 'rank' THEN 'rank, of 139 economies'
                        WHEN 'value' THEN 'as named (the value WIPO screened)' ELSE 'S = strength, W = weakness' END
                 AS unit,
               {gii_status} AS status
        FROM g CROSS JOIN (VALUES ('score', 'score'), ('rank', 'rank'), ('value', 'value'),
                                  ('strength_overall', 'strength or weakness, overall'),
                                  ('strength_income_group', 'strength or weakness, within its income group')) m(k, l)
        WHERE CASE m.k WHEN 'score' THEN score IS NOT NULL WHEN 'rank' THEN rank IS NOT NULL
                       WHEN 'value' THEN value_screen IS NOT NULL WHEN 'strength_overall' THEN sw_overall IS NOT NULL
                       ELSE sw_incgrp IS NOT NULL END
        UNION ALL
        SELECT iso3, economy_name, 2026, 'GII 2026', 'gii', 'economies', 'GII.ECONOMY.' || m.k, m.l,
               CASE m.k WHEN 'population' THEN pop WHEN 'gdp_ppp' THEN pppgdp WHEN 'gdp_ppp_per_person' THEN ppppc END,
               CASE m.k WHEN 'income_group' THEN income_grp WHEN 'region' THEN subreg_un END, m.u, NULL
        FROM {{gii/economies}} CROSS JOIN (VALUES
            ('population', 'Population (GII 2026)', 'thousands'), ('gdp_ppp', 'GDP (GII 2026)', '$ billion, PPP'),
            ('gdp_ppp_per_person', 'GDP per person (GII 2026)', '$, PPP'),
            ('income_group', 'World Bank income group (GII 2026)', 'category'),
            ('region', 'United Nations region (GII 2026)', 'category')) m(k, l, u)
        WHERE CASE m.k WHEN 'population' THEN pop WHEN 'gdp_ppp' THEN pppgdp WHEN 'gdp_ppp_per_person' THEN ppppc
                       END IS NOT NULL
           OR CASE m.k WHEN 'income_group' THEN income_grp WHEN 'region' THEN subreg_un END IS NOT NULL
    ),
    mwm AS (  -- a table's first column is usually the period; where it is a group, a year in the series' name is
        SELECT 'AUS' AS iso3, 'Australia' AS place_name,
               {_year_of("period")} AS year, period, 'mwm' AS source, theme || '/' || indicator AS dataset,
               'MWM.' || indicator || '.' || "table" || coalesce('.' || {_slug("block")}, '') || '.' || series
                 AS indicator,
               concat_ws(', ', title, caption, block, series_label) AS label, value, NULL::VARCHAR AS value_text,
               NULL::VARCHAR AS unit, NULL::VARCHAR AS status
        FROM (
            SELECT d.*, i.title,
                   CASE WHEN {mwm_period} THEN row WHEN regexp_matches("column", '^\\d{{4}}') THEN "column" END
                     AS period,
                   CASE WHEN {mwm_period} THEN {_slug('"column"')}
                        WHEN regexp_matches("column", '^\\d{{4}}') THEN {_slug("row")}
                        ELSE {_slug("row")} || '.' || {_slug('"column"')} END AS series,
                   CASE WHEN {mwm_period} THEN "column" WHEN regexp_matches("column", '^\\d{{4}}') THEN row
                        ELSE row || ', ' || "column" END AS series_label
            FROM {{mwm/data}} d JOIN {{mwm/indicators}} i USING (theme, indicator))
    ),
    ctg AS (  -- Closing the Gap 2026: Australia, and its jurisdictions as breakdowns
        SELECT 'AUS' AS iso3, 'Australia' AS place_name, {_year_of("year")} AS year, year AS period,
               'ctg' AS source, target AS dataset,
               'CTG.' || table_number || '.' || left(md5(concat_ws('|', {ctg_key})), 8) || '.'
                 || replace(jurisdiction, ' ', '_') AS indicator,
               concat_ws(', ', {ctg_label}) || ' (' || jurisdiction || ')' AS label, value,
               CASE WHEN value IS NULL THEN value_text END AS value_text, unit,
               CASE description7 WHEN 'Trajectory' THEN 'projected: the trajectory to the target'
                    WHEN 'Linear regression estimates' THEN 'modelled: linear regression estimate'
                    WHEN 'Estimated annual change' THEN 'assessment: estimated annual change'
                    WHEN 'Assessment of progress' THEN 'assessment: progress'
                    WHEN 'Confidence in assessment of progress' THEN 'assessment: confidence' END AS status
        FROM {{ctg/data}}
    ),
    abs_nat AS (  -- the ABS's and BCARR's tables for Australia as a whole (their industry tables are in
                  -- industry_indicators): CABEE's national tables 4 to 16, R&D and venture capital, creative domains
        SELECT 'AUS' AS iso3, 'Australia' AS place_name,
               {_year_of("coalesce(period, 'June 2026')")} AS year,
               coalesce(period, 'survival, June 2022 to June 2026') AS period, 'abs' AS source,
               'cabee_national' AS dataset,
               'CABEE.' || replace("table", 'Table ', 'T') || '.' || {_slug("row")} || '.' || {_slug('"column"')}
                 AS indicator, table_title || ': ' || row || ', ' || "column" AS label, value,
               NULL::VARCHAR AS value_text,
               CASE WHEN "column" LIKE '%rate%' OR "column" LIKE 'Percentage%' THEN '%' ELSE 'businesses' END AS unit,
               NULL::VARCHAR AS status
        FROM {{abs_cabee/national}}
        WHERE "table" NOT IN ('Table 1', 'Table 2', 'Table 3')
        UNION ALL
        SELECT 'AUS', 'Australia',
               {_year_of(f"coalesce({col_fy}, period)")}, coalesce({col_fy}, period), 'abs', release,
               -- the row on the sheet is part of the code: headings can nest deeper than the cube reader records,
               -- so two blocks of a table can share a section and row label (the venture capital tables)
               'ABS.' || upper(release) || '.' || regexp_extract(cube, '^[^_.]+') || '.' || sheet || '.' || sheet_row
                 || '.' || concat_ws('|', {_slug("coalesce(section, '')")}, {_slug("row")},
                              {_slug(col_no_fy)}),
               title || ': ' || concat_ws(', ', section, row, "column"), value, value_text,
               coalesce(nullif(split_part("column", ' | ', 2), ''), unit), NULL
        FROM {{abs_rd_vc/cubes}}
        WHERE NOT (release = 'berd' AND title LIKE '%industry subdivision%')
        UNION ALL
        SELECT 'AUS', 'Australia', fy_end, financial_year, 'bcarr', release,
               'BCARR.' || left(release, 4) || '.' || {_slug("table_title")} || '.' || {_slug("series")} || '.'
                 || {_slug("unit")},
               table_title || ': ' || series || ' (' || release || ' release)', value, NULL, unit, NULL
        FROM {{bcarr_creative/activity}}
        WHERE NOT (table_title LIKE '%by industry division' OR table_title IN ('Specialised activity',
                   'Support activity', 'Embedded activity', 'In-scope cultural and creative industry subdivisions'))
    ),
    u AS (
        SELECT * FROM oecd UNION ALL SELECT * FROM wipo UNION ALL SELECT * FROM gii
        UNION ALL SELECT * FROM mwm UNION ALL SELECT * FROM ctg UNION ALL SELECT * FROM abs_nat
    )
    SELECT u.iso3, coalesce(n.name, p.name, u.place_name) AS country, coalesce(p.kind, 'country') AS entity,
           u.year, u.period, u.source, u.dataset, u.indicator, u.label, u.value, u.value_text, u.unit, u.status,
           u.iso3 IN ({oecd}) AS oecd, u.iso3 = 'AUS' AS australia
    FROM u
    LEFT JOIN {{wdi/countries}} n ON n.iso3 = u.iso3
    LEFT JOIN (SELECT DISTINCT a3, kind, name FROM iso) p ON p.a3 = u.iso3
    """


# The industries lens (ADR 0020): one row per ANZSIC 2006 division and financial year. A division is identified by its
# letter; a subdivision's two-digit code falls in one division's range (ABS, ANZSIC 2006, cat. no. 1292.0).
ANZSIC_DIVISIONS = {
    "A": ("Agriculture, Forestry and Fishing", 1, 5),
    "B": ("Mining", 6, 10),
    "C": ("Manufacturing", 11, 25),
    "D": ("Electricity, Gas, Water and Waste Services", 26, 29),
    "E": ("Construction", 30, 32),
    "F": ("Wholesale Trade", 33, 38),
    "G": ("Retail Trade", 39, 43),
    "H": ("Accommodation and Food Services", 44, 45),
    "I": ("Transport, Postal and Warehousing", 46, 53),
    "J": ("Information Media and Telecommunications", 54, 60),
    "K": ("Financial and Insurance Services", 62, 64),
    "L": ("Rental, Hiring and Real Estate Services", 66, 67),
    "M": ("Professional, Scientific and Technical Services", 69, 70),
    "N": ("Administrative and Support Services", 72, 73),
    "O": ("Public Administration and Safety", 75, 77),
    "P": ("Education and Training", 80, 82),
    "Q": ("Health Care and Social Assistance", 84, 87),
    "R": ("Arts and Recreation Services", 89, 92),
    "S": ("Other Services", 94, 96),
}
# IP applications by industry run from FY1990: before 1989 IP RAPID records few overseas applicants' countries (U67)
INDUSTRIES_FY = (1990, 2026)
# B6 (the review's F27): IPC subclasses the ALP crosswalk does not know, mapped to the subclass they came from (new
# ones, 2018 to 2026) or were merged into (obsolete ones). Each is flagged in the profile, never silently added.
IPC_PREDECESSORS = {
    "G16H": "G06F",  # healthcare informatics, from G06F 19/00 (2018)
    "G16B": "G06F",  # bioinformatics, from G06F 19/10 (2019)
    "G16C": "G06F",  # computational chemistry, from G06F 19/00 (2019)
    "G16Z": "G06F",  # other ICT for specific fields, from G06F 19/00 (2019)
    "G16Y": "H04L",  # ICT for the Internet of Things, from H04L 29 and H04W (2020)
    "G06V": "G06K",  # image and video recognition, from G06K 9 (2022)
    "F24S": "F24J",  # solar heat collectors, from F24J 2 (2018)
    "F24T": "F24J",  # geothermal collectors, from F24J 3 (2018)
    "F24V": "F24J",  # other heat production, from F24J 1 (2018)
    "B64U": "B64C",  # unmanned aerial vehicles, from B64C 39/02 (2023)
    "H10B": "H01L",  # electronic memory devices, from H01L 27 (2023)
    "H10K": "H01L",  # organic semiconductor devices, from H01L 51 (2023)
    "H10N": "H01L",  # thermoelectric and other devices, from H01L 35 to 49 (2023)
    "H10D": "H01L",  # inorganic semiconductor devices, from H01L 29 (2025)
    "H10F": "H01L",  # light-sensitive semiconductor devices, from H01L 31 (2025)
    "H10P": "H01L",  # semiconductor processes, from H01L 21 (2026)
    "H10W": "H01L",  # semiconductor packaging, from H01L 23 (2026)
    "B65J": "B65D",  # containers, from B65D (2025)
    "B29F": "B29C",  # obsolete rubber and plastics subclasses, merged into B29C
    "B29G": "B29C",
    "B29H": "B29C",
    "B29J": "B29C",
    "C08D": "C08C",  # obsolete rubber subclass, merged into C08C
    "F21M": "F21S",  # obsolete lighting subclasses, merged into F21S and F21V
    "F21P": "F21V",
    "F21Q": "F21S",
}


def _divisions() -> str:
    """A VALUES list of (division, name, first subdivision, last subdivision)."""
    return ", ".join(f"('{d}', '{n}', {lo}, {hi})" for d, (n, lo, hi) in ANZSIC_DIVISIONS.items())


def _division_of(code: str, digits: int = 4) -> str:
    """The division of an ANZSIC code given as text, or NULL: a class (`digits` 4: '111' is class 0111) or a
    subdivision (`digits` 2: '1' is subdivision 01)."""
    sub = f"TRY_CAST(left(lpad(trim({code}), {digits}, '0'), 2) AS INTEGER)"
    cases = " ".join(f"WHEN {sub} BETWEEN {lo} AND {hi} THEN '{d}'" for d, (_, lo, hi) in ANZSIC_DIVISIONS.items())
    return f"CASE WHEN {sub} = 99 THEN 'X' {cases} END"


def _norm(col: str) -> str:
    return f"trim(regexp_replace(lower({col}), '[^a-z0-9]+', ' ', 'g'))"


def _industry_names() -> str:
    """CTEs `divs` (the 19 divisions) and `names` (a normalised division or subdivision name, or a word for all
    industries or an unknown one, to its division: 'TOTAL' and 'X'), for tables that name industries in words."""
    return f"""
    divs(division, division_name, lo, hi) AS (VALUES {_divisions()}),
    names AS (
        SELECT {_norm("division_name")} AS name, division FROM divs
        UNION
        SELECT DISTINCT {_norm("anzsic_subdivision_label")}, {_division_of("anzsic_subdivision_code", 2)}
        FROM {{abs_cabee/cubes}} WHERE anzsic_subdivision_code IS NOT NULL AND cube = '8165DC04'
        UNION SELECT * FROM (VALUES ('all industries', 'TOTAL'), ('total all industries', 'TOTAL'), ('total', 'TOTAL'),
                                    ('currently unknown', 'X')) t(name, division)
    )"""


def _ip_by_division() -> str:
    """CTEs `ip_pat` and `ip_tm`: each patent's and trade mark's expected share in each division, through the ALP
    crosswalks (ADR 0020). A right's current classes share its weight equally (1/n), each class's weight is split over
    ANZSIC classes by the crosswalk's probabilities, so each right sums to 1 over the divisions. Patent subclasses the
    crosswalk does not know are first mapped to their predecessors (`IPC_PREDECESSORS`, B6); a patent with no known
    subclass is left out."""
    pred = ", ".join(f"('{a}', '{b}')" for a, b in IPC_PREDECESSORS.items())
    return f"""
    pred(ipc_from, ipc_to) AS (VALUES {pred}),
    ipc AS (
        SELECT DISTINCT c.application_number, coalesce(p.ipc_to, left(c.classification, 4)) AS ipc4
        FROM {{iprapid/classification}} c LEFT JOIN pred p ON p.ipc_from = left(c.classification, 4)
        WHERE c.ip_right_type = 'patent' AND c.classification_system = 'ipc_mark' AND c.is_current
          AND coalesce(p.ipc_to, left(c.classification, 4)) IN (SELECT ipc4 FROM {{concordances/ipc4_anzsic}})
    ),
    ip_pat AS (
        SELECT i.application_number, left(lpad(a.anzsic, 4, '0'), 2) AS subdivision,
               {_division_of("a.anzsic")} AS division, sum(a.weight / i.n) AS share
        FROM (SELECT *, count(*) OVER (PARTITION BY application_number) AS n FROM ipc) i
        JOIN {{concordances/ipc4_anzsic}} a USING (ipc4)
        GROUP BY 1, 2, 3
    ),
    nice AS (
        SELECT DISTINCT application_number, lpad(trim(classification), 2, '0') AS nice
        FROM {{iprapid/classification}}
        WHERE ip_right_type = 'trade_mark' AND classification_system = 'nice' AND is_current
    ),
    ip_tm AS (
        SELECT c.application_number, left(lpad(a.anzsic, 4, '0'), 2) AS subdivision,
               {_division_of("a.anzsic")} AS division, sum(a.weight / c.n) AS share
        FROM (SELECT *, count(*) OVER (PARTITION BY application_number) AS n FROM nice) c
        JOIN {{concordances/nice_anzsic}} a USING (nice)
        GROUP BY 1, 2, 3
    )"""


def industries_sql() -> str:
    """One row per ANZSIC division (A to S) and financial year, FY1990 to FY2026. IP applications are expected counts
    (a right's share in each division, ADR 0020); the rest is the ABS's: businesses, entries and exits (CABEE),
    business R&D (BERD), wages (the WPI, the financial year's average of its quarterly index) and the cultural and
    creative industries' value added (BCARR). Each is empty outside the years its source covers."""
    lo, hi = INDUSTRIES_FY
    core = (
        "'Operating at start of financial year', 'Operating at end of financial year', 'Entries - Total', "
        "'Exits - Total', 'Entry rate', 'Exit rate'"
    )
    return f"""
    WITH {_industry_names()},
    {_ip_by_division()},
    grid AS (
        SELECT d.division, d.division_name, f.fy
        FROM divs d CROSS JOIN (SELECT unnest(range({lo}, {hi + 1})) AS fy) f
    ),
    r AS (
        SELECT ip_right_type, application_number, patent_type, australian_applicant, filing_fy
        FROM {lens_table("rights")} WHERE filing_fy BETWEEN {lo} AND {hi}
    ),
    pat AS (
        SELECT p.division, r.filing_fy AS fy,
               sum(p.share) FILTER (r.patent_type = 'standard') AS patents_standard,
               sum(p.share) FILTER (r.patent_type = 'standard' AND r.australian_applicant) AS patents_standard_au,
               sum(p.share) FILTER (r.patent_type = 'second_tier') AS patents_second_tier
        FROM ip_pat p JOIN r ON r.ip_right_type = 'patent' AND r.application_number = p.application_number
        GROUP BY 1, 2
    ),
    tm AS (
        SELECT t.division, r.filing_fy AS fy, sum(t.share) AS trade_marks,
               sum(t.share) FILTER (r.australian_applicant) AS trade_marks_au
        FROM ip_tm t JOIN r ON r.ip_right_type = 'trade_mark' AND r.application_number = t.application_number
        GROUP BY 1, 2
    ),
    cabee AS (  -- CABEE's national release: counts by division and financial year
        SELECT n.division, CAST(left(c.period, 4) AS INTEGER) + 1 AS fy,
               max(c.value) FILTER (c."column" = 'Operating at start of financial year') AS businesses_start,
               max(c.value) FILTER (c."column" = 'Operating at end of financial year') AS businesses_end,
               max(c.value) FILTER (c."column" = 'Entries - Total') AS business_entries,
               max(c.value) FILTER (c."column" = 'Exits - Total') AS business_exits,
               max(c.value) FILTER (c."column" = 'Entry rate') AS business_entry_rate,
               max(c.value) FILTER (c."column" = 'Exit rate') AS business_exit_rate
        FROM {{abs_cabee/national}} c JOIN names n ON n.name = {_norm("c.row")}
        WHERE c."table" = 'Table 1' AND c."column" IN ({core})
        GROUP BY 1, 2
    ),
    berd AS (  -- business expenditure on R&D, 2023-24: each division's total row
        SELECT n.division, 2024 AS fy, b.value AS berd
        FROM {{abs_rd_vc/cubes}} b JOIN names n ON n.name = {_norm("b.section")}
        WHERE b.cube = '81040DO002_202324.xlsx' AND b."column" = 'Total expenditure on R&D | $''000'
          AND {_norm("b.row")} = 'total ' || n.name
    ),
    wpi AS (  -- the financial year's average of the quarterly index, where it has all four quarters
        SELECT industry AS division,
               CAST(left(time_period, 4) AS INTEGER) + (right(time_period, 1) IN ('3', '4'))::INT AS fy,
               CASE WHEN count(*) = 4 THEN avg(value) END AS wpi_index
        FROM {{abs_prices/wpi}}
        WHERE measure = '1' AND index = 'THRPEB' AND sector = '7' AND adjustment_type = '10' AND region = 'AUS'
          AND industry IN (SELECT division FROM divs)
        GROUP BY 1, 2
    ),
    creative AS (  -- the cultural and creative industries' value added by division, the newer release (2015-16 on)
        SELECT n.division, a.fy_end AS fy, a.value AS creative_gva
        FROM {{bcarr_creative/activity}} a JOIN names n ON n.name = {_norm("a.series")}
        WHERE a.release = '2015-16 to 2024-25' AND a.table_title LIKE '%GVA by industry division'
          AND n.division IN (SELECT division FROM divs)
    )
    SELECT g.division, g.division_name, g.fy,
           coalesce(pat.patents_standard, 0) AS patents_standard,
           coalesce(pat.patents_standard_au, 0) AS patents_standard_au,
           coalesce(pat.patents_second_tier, 0) AS patents_second_tier,
           coalesce(tm.trade_marks, 0) AS trade_marks, coalesce(tm.trade_marks_au, 0) AS trade_marks_au,
           cabee.* EXCLUDE (division, fy), berd.berd, wpi.wpi_index, creative.creative_gva
    FROM grid g
    LEFT JOIN pat USING (division, fy) LEFT JOIN tm USING (division, fy) LEFT JOIN cabee USING (division, fy)
    LEFT JOIN berd USING (division, fy) LEFT JOIN wpi USING (division, fy) LEFT JOIN creative USING (division, fy)
    ORDER BY g.division, g.fy
    """


# BCS tables (the ABS's business characteristics and innovation surveys): every column with a label is a dimension,
# except these, which place the value in time or describe it
BCS_TABLES = [
    "bcs_inn", "bcs_innact", "bcs_innsig", "bcs_businf", "bcs_businf2", "bcs_busgvtsk", "abs_it_innovation",
    "abs_it_barrier", "abs_it_bus_struc", "abs_it_finance", "abs_it_mktcomp", "abs_it_perf", "abs_it_support",
]  # fmt: skip
BCS_NOT_DIMENSIONS = {
    "flow",
    "frequency",
    "time_period",
    "observation_status",
    "decimals",
    "industry",
    "unit_of_measure",
}


def _bcs_sql(name: str) -> str:
    import duckdb

    from .data import table

    cols = [r[0] for r in duckdb.sql(f"DESCRIBE SELECT * FROM {table('abs_bcs', name)}").fetchall()]
    dims = [c for c in cols if f"{c}_label" in cols and c not in BCS_NOT_DIMENSIONS]
    return f"""
        SELECT industry AS division, 'bcs' AS source,
               '{name}' AS dataset, 'BCS.{name.upper()}.' || concat_ws('.', {", ".join(dims)}) AS indicator,
               concat_ws(', ', {", ".join(f"{d}_label" for d in dims)}) AS label, time_period AS period,
               CAST(left(time_period, 4) AS INTEGER) AS fy, value, NULL::VARCHAR AS value_text,
               unit_of_measure_label AS unit, observation_status_label AS status
        FROM {{abs_bcs/{name}}}"""


def industry_indicators_sql() -> str:
    """The industries lens's attachments, long (ADR 0020): one row per division, source, indicator and period, for
    every value the ABS and BCARR publish by industry. A value for all industries has the division 'TOTAL' and one
    for an unknown industry 'X'; the core lens's own values are not repeated."""
    core = (
        "'Operating at start of financial year', 'Operating at end of financial year', 'Entries - Total', "
        "'Exits - Total', 'Entry rate', 'Exit rate'"
    )
    period_fy = "CAST(left({p}, 4) AS INTEGER) + 1"
    return f"""
    WITH {_industry_names()},
    {_ip_by_division()},
    cabee_national AS (  -- CABEE's national release, tables 1 to 3 (by division)
        SELECT n.division, 'cabee' AS source, 'national' AS dataset,
               'CABEE.' || replace(c."table", 'Table ', 'T') || '.' || {_slug('c."column"')} AS indicator,
               c.table_title || ': ' || c."column" AS label,
               coalesce(c.period, 'survival, June 2022 to June 2026') AS period,
               coalesce({period_fy.format(p="c.period")}, 2026) AS fy, c.value, NULL::VARCHAR AS value_text,
               CASE WHEN c."column" LIKE '%rate%' OR c."column" LIKE 'Percentage%' THEN '%' ELSE 'businesses' END
                 AS unit, NULL::VARCHAR AS status
        FROM {{abs_cabee/national}} c JOIN names n ON n.name = {_norm("c.row")}
        WHERE c."table" IN ('Table 1', 'Table 2', 'Table 3')
          AND NOT (c."table" = 'Table 1' AND c."column" IN ({core}) AND n.division IN (SELECT division FROM divs))
    ),
    cabee_cubes AS (  -- CABEE's cubes by state and class or subdivision, and by local government area and division
        SELECT coalesce(c.industry_code, {_division_of("c.anzsic_industry_code")},
                        {_division_of("c.anzsic_subdivision_code", 2)}, 'TOTAL') AS division,
               'cabee' AS source, c.cube AS dataset,
               'CABEE.' || c.cube || '.' || concat_ws('|', coalesce(c.measure, 'count'),
                   coalesce(c.anzsic_industry_code, c.anzsic_subdivision_code, ''),
                   coalesce(c.lga_code, c.state_name, c.state_label, ''), c.size, c.unit) AS indicator,
               concat_ws(', ', coalesce(c.measure, 'Businesses'),
                         coalesce(c.anzsic_industry_label, c.anzsic_subdivision_label, c.industry_label),
                         coalesce(c.lga_label, c.state_label), c.size) AS label,
               regexp_extract(c.table_title, 'June \\d{{4}}( – June \\d{{4}})?') AS period,
               CAST(regexp_extract(c.table_title, '(\\d{{4}}) \\(a\\)', 1) AS INTEGER) AS fy,
               c.value, NULL::VARCHAR AS value_text, c.unit, NULL::VARCHAR AS status
        FROM {{abs_cabee/cubes}} c WHERE c.cube NOT IN ('8165DC08', '8165DC09')  -- SA2s: in region_indicators
    ),
    bcs AS ({"UNION ALL".join(_bcs_sql(t) for t in BCS_TABLES)}
    ),
    berd AS (  -- business R&D by subdivision, 2023-24: the division from the section, or from the row
        SELECT coalesce(ns.division, nr.division, CASE WHEN {_norm("b.row")} LIKE 'total%' THEN 'TOTAL' END)
                 AS division,
               'berd' AS source, regexp_extract(b.cube, 'DO\\d+') AS dataset,
               'BERD.' || regexp_extract(b.cube, 'DO\\d+') || '.' || b.sheet || '.' || b.sheet_row || '.' ||
                 concat_ws('|', {_slug("coalesce(b.section, '')")}, {_slug("b.row")}, {_slug('b."column"')})
                 AS indicator,
               b.title || ': ' || concat_ws(', ', b.section, b.row, b."column") AS label, b.period,
               {period_fy.format(p="b.period")} AS fy, b.value, b.value_text,
               CASE WHEN b.title LIKE '%RELATIVE STANDARD ERROR%' THEN '% (relative standard error)'
                    ELSE coalesce(nullif(split_part(b."column", ' | ', 2), ''), b.unit) END AS unit,
               NULL::VARCHAR AS status
        FROM {{abs_rd_vc/cubes}} b
        LEFT JOIN names ns ON ns.name = {_norm("b.section")}
        LEFT JOIN names nr ON nr.name = regexp_replace({_norm("b.row")}, '^total ', '')
        WHERE b.release = 'berd' AND b.title LIKE '%industry subdivision%'
          AND NOT (b.cube = '81040DO002_202324.xlsx' AND b."column" = 'Total expenditure on R&D | $''000'
                   AND {_norm("b.row")} = 'total ' || ns.name)
    ),
    creative AS (  -- cultural and creative value added by division or subdivision, both releases (never spliced)
        SELECT coalesce(n.division, CASE WHEN a.series LIKE 'Total%' OR a.series LIKE 'Cultural and creative%'
                                         THEN 'TOTAL' END) AS division,
               'bcarr' AS source, a.release AS dataset,
               'BCARR.' || left(a.release, 4) || '.' || {_slug("a.table_title")} || '.' || {_slug("a.series")}
                 || '.' || {_slug("a.unit")} AS indicator,
               a.table_title || ': ' || a.series || ' (' || a.release || ' release)' AS label,
               a.financial_year AS period, a.fy_end AS fy, a.value, NULL::VARCHAR AS value_text, a.unit,
               NULL::VARCHAR AS status
        FROM {{bcarr_creative/activity}} a LEFT JOIN names n ON n.name = {_norm("a.series")}
        WHERE (a.table_title LIKE '%by industry division' OR a.table_title IN ('Specialised activity',
               'Support activity', 'Embedded activity', 'In-scope cultural and creative industry subdivisions'))
          AND NOT (a.release = '2015-16 to 2024-25' AND a.table_title LIKE '%GVA by industry division'
                   AND n.division IN (SELECT division FROM divs))
    ),
    r AS (
        SELECT ip_right_type, application_number, patent_type, australian_applicant, filing_fy
        FROM {lens_table("rights")} WHERE filing_fy BETWEEN {INDUSTRIES_FY[0]} AND {INDUSTRIES_FY[1]}
    ),
    ip_sub AS (  -- the core lens's IP counts by subdivision: the detail within a division (ADR 0020)
        SELECT x.division, x.subdivision, x.kind, r.filing_fy AS fy, sum(x.share) AS value
        FROM (SELECT application_number, 'patent' AS ip_right_type, subdivision, division, share, 'patents' AS kind
              FROM ip_pat
              UNION ALL SELECT application_number, 'trade_mark', subdivision, division, share, 'trade_marks'
              FROM ip_tm) x
        JOIN r ON r.ip_right_type = x.ip_right_type AND r.application_number = x.application_number
        WHERE x.kind = 'trade_marks' OR r.patent_type = 'standard'
        GROUP BY ALL
    ),
    ip AS (
        SELECT division, 'ip' AS source, 'rights' AS dataset,
               'IP.' || upper(kind) || '.' || subdivision AS indicator,
               CASE kind WHEN 'patents' THEN 'Standard patent applications (expected)'
                         ELSE 'Trade mark applications (expected)' END || ', ' || subdivision || ' '
                 || coalesce(sub_name, '') AS label,
               CAST(fy - 1 AS VARCHAR) || '-' || right(CAST(fy AS VARCHAR), 2) AS period, fy, value,
               NULL::VARCHAR AS value_text, 'applications (expected)' AS unit, NULL::VARCHAR AS status
        FROM ip_sub LEFT JOIN (SELECT DISTINCT lpad(anzsic_subdivision_code, 2, '0') AS subdivision,
                                          anzsic_subdivision_label AS sub_name
                               FROM {{abs_cabee/cubes}} WHERE cube = '8165DC04' AND anzsic_subdivision_code IS NOT NULL)
          USING (subdivision)
    ),
    wpi AS (  -- the Wage Price Index by industry, quarterly (a quarter is never spread over months or years)
        SELECT CASE industry WHEN 'TOT' THEN 'TOTAL' ELSE industry END AS division, 'wpi' AS source,
               'wpi' AS dataset, 'WPI.' || measure || '.' || index || '.' || sector || '.' || adjustment_type
                 AS indicator,
               concat_ws(', ', index_label, measure_label, sector_label, adjustment_type_label) AS label,
               time_period AS period,
               CAST(left(time_period, 4) AS INTEGER) + (right(time_period, 1) IN ('3', '4'))::INT AS fy,
               value, NULL::VARCHAR AS value_text, unit_of_measure_label AS unit,
               nullif(observation_status_label, 'not applicable') AS status
        FROM {{abs_prices/wpi}} WHERE region = 'AUS'
    )
    SELECT u.*, d.division_name
    FROM (SELECT * FROM cabee_national UNION ALL SELECT * FROM cabee_cubes UNION ALL SELECT * FROM bcs
          UNION ALL SELECT * FROM berd UNION ALL SELECT * FROM creative UNION ALL SELECT * FROM wpi
          UNION ALL SELECT * FROM ip) u
    LEFT JOIN divs d USING (division)
    """


# The institutions lens (ADR 0021): one row per Australian research institution (its ROR identifier) and calendar
# year. The reviewed link is three files in `analysis/eda/institutions/`: the institutions and their kind, the names
# they appear under beyond ROR's own (former names, commercialisation companies, misspellings) and their ABNs.
INSTITUTIONS_DIR = Path(__file__).resolve().parent / "institutions"
OPENALEX_FROM = 2010  # OpenAlex gives an institution's works and citations by year for 2010 on
# The ARC's schemes for research with industry partners. The ARC's 'Linkage' program also holds the Centres of
# Excellence, infrastructure (LIEF), Special Research Initiatives and the learned academies' projects
ARC_INDUSTRY_SCHEMES = (
    "Linkage Projects", "Industrial Transformation Training Centres", "Industrial Transformation Research Hubs",
    "Industry Laureate Fellowships", "Mid-Career Industry Fellowships", "Early Career Industry Fellowships",
)  # fmt: skip
INSTITUTIONS_YEARS = (1990, 2026)  # IP and grants run further back than OpenAlex's counts (2010 on); each is empty
# outside the years its source covers. OpenAlex's later years (2027 to 10000) are placeholders on a few works.


def _name_key(col: str) -> str:
    """An organisation's name for matching: capitals, no apostrophes, '&' as 'AND', other punctuation as spaces, and
    no 'THE' or legal suffixes ('PTY', 'LTD', 'INC' ...), so 'The Walter & Eliza Hall Institute ... Ltd' and 'WALTER
    AND ELIZA HALL INSTITUTE ...' agree."""
    s = f"regexp_replace(upper({col}), '[''’`]', '', 'g')"
    s = f"regexp_replace({s}, '&', ' AND ', 'g')"
    s = f"regexp_replace({s}, '[^A-Z0-9]+', ' ', 'g')"
    s = f"regexp_replace({s}, '\\b(THE|PTY|PROPRIETARY|LTD|LIMITED|INC|INCORPORATED|CO|COMPANY)\\b', ' ', 'g')"
    return f"trim(regexp_replace({s}, ' +', ' ', 'g'))"


def _institution_names(sources: tuple[str, ...]) -> str:
    """CTEs `inst` (the lens's institutions), `inst_names` (each name key to its institution: ROR's names, labels and
    aliases for the lens's institutions, acronyms excepted, and the reviewed names for these `sources`) and
    `inst_abns` (each reviewed ABN to its institution). A test checks that no key names two institutions."""
    d = INSTITUTIONS_DIR
    src = ", ".join(f"'{s}'" for s in (*sources, "any"))
    return f"""
    inst AS (SELECT * FROM read_csv('{d / "institutions.csv"}', all_varchar = true)),
    inst_names AS (
        SELECT DISTINCT {_name_key("n.name")} AS key, n.ror
        FROM {{ror/names}} n JOIN inst USING (ror) WHERE n.name_types <> 'acronym'
        UNION
        SELECT DISTINCT {_name_key("a.name")}, a.ror FROM read_csv('{d / "names.csv"}', all_varchar = true) a
        WHERE a.source IN ({src})
    ),
    inst_abns AS (SELECT abn, ror FROM read_csv('{d / "abns.csv"}', all_varchar = true))"""


def institution_rights_sql() -> str:
    """One row per IP right and research institution among its founding applicants (ADR 0021): the detail behind the
    `institutions` lens's IP counts, joinable to `rights` by application number. A founding applicant or owner (ADR
    0013) in Australia, or of no recorded country, and not an individual, belongs to an institution when its name
    matches one of the institution's names, or else when its ABN is one of the institution's ABNs."""
    return f"""
    WITH {_institution_names(("iprapid",))},
    founders AS (
        SELECT DISTINCT ip_right_type, application_number, party_id, abn, country_code, party_type,
               {_name_key("party_name")} AS key
        FROM {{iprapid/party}}
        WHERE party_role_category IN ('applicant', 'owner') AND is_founding
    ),
    matched AS (
        SELECT f.ip_right_type, f.application_number, f.party_id, coalesce(n.ror, a.ror) AS ror,
               CASE WHEN n.ror IS NOT NULL AND n.ror = a.ror THEN 'both'
                    WHEN n.ror IS NOT NULL THEN 'name' ELSE 'abn' END AS matched_by, f.country_code
        FROM founders f
        LEFT JOIN inst_names n USING (key)
        LEFT JOIN inst_abns a ON a.abn = f.abn
        WHERE (f.country_code = 'au' OR f.country_code IS NULL) AND (n.ror IS NOT NULL OR a.ror IS NOT NULL)
          AND f.party_type IS DISTINCT FROM 'individual'
    ),
    per AS (
        SELECT ip_right_type, application_number, ror,
               CASE WHEN count(DISTINCT matched_by) > 1 OR bool_or(matched_by = 'both') THEN 'both'
                    ELSE any_value(matched_by) END AS matched_by,
               bool_and(country_code IS NULL) AS country_unknown, list(DISTINCT party_id) AS parties
        FROM matched GROUP BY 1, 2, 3
    ),
    n_founders AS (SELECT ip_right_type, application_number, count(DISTINCT party_id) AS n FROM founders GROUP BY 1, 2),
    n_inst AS (SELECT ip_right_type, application_number, count(*) AS n FROM per GROUP BY 1, 2)
    SELECT p.ip_right_type, p.application_number, p.ror, p.matched_by, p.country_unknown,
           nf.n > len(p.parties) AS shared, ni.n > 1 AS shared_with_institution
    FROM per p
    JOIN n_founders nf USING (ip_right_type, application_number)
    JOIN n_inst ni USING (ip_right_type, application_number)
    ORDER BY p.ror, p.ip_right_type, p.application_number
    """


def institutions_sql() -> str:
    """One row per research institution and calendar year (ADR 0021). Research output and citations are OpenAlex's
    (works by publication year); citations from US patents are to the institution's works published that year;
    grants are the ARC's (by the year funding starts, at the organisation that won it) and the NHMRC's (by round);
    IP applications are those with the institution among their founding applicants (`institution_rights`), by the
    year of the application date (plant breeder's rights cannot be linked: IP RAPID gives their applicants' names as
    codes, with no ABNs); patent families (Google Patents) by the year of their first priority; government
    contracts (AusTender) by the year first published, each contract once at its latest notice."""
    lo, hi = INSTITUTIONS_YEARS
    industry = "g.scheme_name IN (" + ", ".join(f"'{x}'" for x in ARC_INDUSTRY_SCHEMES) + ")"
    return f"""
    WITH {_institution_names(("arc", "nhmrc"))},
    grid AS (
        SELECT i.ror, y.year FROM inst i CROSS JOIN (SELECT unnest(range({lo}, {hi + 1})) AS year) y
    ),
    oa AS (SELECT id, replace(ror, 'https://ror.org/', '') AS ror FROM {{openalex/institutions}}),
    works AS (
        SELECT oa.ror, y.year, y.works_count AS works, y.cited_by_count AS citations
        FROM {{openalex/institution_year}} y JOIN oa USING (id)
    ),
    cited AS (  -- the institution's works that US patents cite, by the work's publication year
        SELECT oa.ror, w.year, count(DISTINCT c.work_id) AS works_patent_cited,
               sum(pc.n) AS patent_citations, sum(pc.n_au) AS patent_citations_au
        FROM (SELECT DISTINCT work_id, institution_id FROM {{openalex_works/cited_au_works}}) c
        JOIN oa ON oa.id = c.institution_id
        JOIN {{openalex_works/au_works}} w USING (work_id)
        JOIN (SELECT work_id, count(*) AS n, count(*) FILTER (citing_au_family) AS n_au
              FROM {{openalex_works/patent_citations}} GROUP BY 1) pc USING (work_id)
        GROUP BY 1, 2
    ),
    arc AS (  -- the organisation that won the grant (at announcement), else the one administering it now
        SELECT n.ror, g.funding_commencement_year AS year, count(*) AS arc_grants,
               sum(coalesce(g.announced_funding_amount, g.current_funding_amount)) AS arc_funding,
               count(*) FILTER ({industry}) AS arc_industry_grants,
               sum(coalesce(g.announced_funding_amount, g.current_funding_amount)) FILTER ({industry})
                 AS arc_industry_funding
        FROM {{arc_grants/grants}} g
        JOIN inst_names n
          ON n.key = {_name_key("coalesce(g.announcement_admin_organisation, g.current_admin_organisation)")}
        GROUP BY 1, 2
    ),
    nhmrc AS (  -- the NHMRC gives the institution's ROR from the 2025 round; before then it is matched by name
        SELECT coalesce(replace(g.admin_institution_ror, 'https://ror.org/', ''), n.ror) AS ror,
               CAST(g.round AS INTEGER) AS year, count(*) AS nhmrc_grants, sum(g.amount) AS nhmrc_funding
        FROM {{nhmrc_grants/grants}} g LEFT JOIN inst_names n ON n.key = {_name_key("g.admin_institution")}
        GROUP BY 1, 2
    ),
    ir AS (
        SELECT x.ror, x.shared, r.application_number, r.ip_right_type, r.patent_type, year(r.application_date) AS year
        FROM {lens_table("institution_rights")} x
        JOIN {lens_table("rights")} r USING (ip_right_type, application_number)
    ),
    ip AS (
        SELECT ror, year,
               count(*) FILTER (patent_type = 'standard') AS patents_standard,
               count(*) FILTER (patent_type = 'standard' AND shared) AS patents_standard_shared,
               count(*) FILTER (patent_type = 'provisional') AS patents_provisional,
               count(*) FILTER (patent_type = 'second_tier') AS patents_second_tier,
               count(*) FILTER (ip_right_type = 'trade_mark') AS trade_marks,
               count(*) FILTER (ip_right_type = 'design') AS designs
        FROM ir GROUP BY 1, 2
    ),
    fam AS (  -- the patent families of the institution's Australian applications, by year of first priority
        SELECT DISTINCT ir.ror, m.family_id
        FROM ir JOIN {{google_patents/members}} m
          ON m.country_code = 'AU' AND m.au_application = ir.application_number
        WHERE ir.ip_right_type = 'patent'
    ),
    families AS (
        SELECT fam.ror, year(f.first_priority_date) AS year, count(*) AS patent_families,
               count(*) FILTER (f.granted_us) AS patent_families_us_granted,
               sum(f.citing_families_5y) AS patent_family_citations_5y
        FROM fam JOIN {{google_patents/families}} f USING (family_id) GROUP BY 1, 2
    ),
    contracts AS (  -- each contract once, at its latest notice (as in `linkage/abn_spine`, ADR 0010)
        SELECT parent_cn_id,
               arg_max(supplier_abn, (amendment IS NOT NULL, amendment, published)) FILTER (supplier_abn IS NOT NULL)
                 AS abn,
               arg_max(value, (amendment IS NOT NULL, amendment, published)) FILTER (value IS NOT NULL) AS value,
               min(published)::DATE AS first_published
        FROM {{austender/contracts}} GROUP BY 1
    ),
    tender AS (
        SELECT a.ror, year(c.first_published) AS year, count(*) AS contracts, sum(c.value) AS contract_value
        FROM contracts c JOIN inst_abns a USING (abn) GROUP BY 1, 2
    ),
    o AS (SELECT ror, state, established, status FROM {{ror/organisations}})
    SELECT g.ror, i.institution, i.kind, nullif(i.parent_ror, '') AS parent_ror, upper(o.state) AS state,
           o.established, o.status AS ror_status, g.year,
           CASE WHEN g.year >= {OPENALEX_FROM} AND oa.id IS NOT NULL THEN coalesce(works.works, 0) END AS works,
           CASE WHEN g.year >= {OPENALEX_FROM} AND oa.id IS NOT NULL THEN coalesce(works.citations, 0) END
             AS citations,
           CASE WHEN oa.id IS NOT NULL THEN coalesce(cited.works_patent_cited, 0) END AS works_patent_cited,
           CASE WHEN oa.id IS NOT NULL THEN coalesce(cited.patent_citations, 0) END AS patent_citations,
           CASE WHEN oa.id IS NOT NULL THEN coalesce(cited.patent_citations_au, 0) END AS patent_citations_au,
           CASE WHEN g.year >= 2001 THEN coalesce(arc.arc_grants, 0) END AS arc_grants,
           CASE WHEN g.year >= 2001 THEN coalesce(arc.arc_funding, 0) END AS arc_funding,
           CASE WHEN g.year >= 2001 THEN coalesce(arc.arc_industry_grants, 0) END AS arc_industry_grants,
           CASE WHEN g.year >= 2001 THEN coalesce(arc.arc_industry_funding, 0) END AS arc_industry_funding,
           CASE WHEN g.year >= 2013 THEN coalesce(nhmrc.nhmrc_grants, 0) END AS nhmrc_grants,
           CASE WHEN g.year >= 2013 THEN coalesce(nhmrc.nhmrc_funding, 0) END AS nhmrc_funding,
           coalesce(ip.patents_standard, 0) AS patents_standard,
           coalesce(ip.patents_standard_shared, 0) AS patents_standard_shared,
           coalesce(ip.patents_provisional, 0) AS patents_provisional,
           coalesce(ip.patents_second_tier, 0) AS patents_second_tier,
           coalesce(ip.trade_marks, 0) AS trade_marks,
           coalesce(ip.designs, 0) AS designs,
           coalesce(families.patent_families, 0) AS patent_families,
           coalesce(families.patent_families_us_granted, 0) AS patent_families_us_granted,
           coalesce(families.patent_family_citations_5y, 0) AS patent_family_citations_5y,
           CASE WHEN g.year >= 2005 THEN coalesce(tender.contracts, 0) END AS contracts,
           CASE WHEN g.year >= 2005 THEN coalesce(tender.contract_value, 0) END AS contract_value
    FROM grid g
    JOIN inst i USING (ror)
    LEFT JOIN o USING (ror)
    LEFT JOIN oa USING (ror)
    LEFT JOIN works USING (ror, year) LEFT JOIN cited USING (ror, year) LEFT JOIN arc USING (ror, year)
    LEFT JOIN nhmrc USING (ror, year) LEFT JOIN ip USING (ror, year) LEFT JOIN families USING (ror, year)
    LEFT JOIN tender USING (ror, year)
    ORDER BY g.ror, g.year
    """


def timeline_sql() -> str:
    """One row per month. A series is empty before its records become continuous (the 9-in-12 rule, or
    `TIMELINE_START_OVERRIDE`) and in the final months the register has not finished recording (`TIMELINE_LAG`), so
    that 'not recorded' is not read as 0. The CPI is quarterly: it sits in each quarter's last month only."""
    series = [c for c, _ in TIMELINE_APPLICATIONS + TIMELINE_EVENTS]

    def counts(defs):
        return ",\n            ".join(f"count(*) FILTER ({cond}) AS {col}" for col, cond in defs)

    window = f"BETWEEN DATE '{TIMELINE_START}' AND DATE '{TIMELINE_END}' + INTERVAL 1 MONTH - INTERVAL 1 DAY"
    any_event = " OR ".join(f"({cond})" for _, cond in TIMELINE_EVENTS)
    nonzero = ",\n        ".join(f"sum((coalesce({c}, 0) > 0)::INT) OVER w AS nz_{c}" for c in series)
    starts = ", ".join(
        f"DATE '{TIMELINE_START_OVERRIDE[c]}' AS start_{c}"
        if c in TIMELINE_START_OVERRIDE
        else f"min(month) FILTER (nz_{c} >= 9 AND months_ahead = 12) AS start_{c}"
        for c in series
    )
    kept = ",\n        ".join(
        f"CASE WHEN j.month >= f.start_{c} AND j.month <= DATE '{TIMELINE_END}' - INTERVAL {TIMELINE_LAG.get(c, 0)} "
        f"MONTH THEN coalesce(j.{c}, 0) END AS {c}"
        for c in series
    )
    return f"""
    WITH months AS (
        SELECT CAST(m AS DATE) AS month
        FROM unnest(generate_series(DATE '{TIMELINE_START}', DATE '{TIMELINE_END}', INTERVAL 1 MONTH)) t(m)
    ),
    apps AS (
        SELECT CAST(date_trunc('month', application_date) AS DATE) AS month,
            {counts(TIMELINE_APPLICATIONS)}
        FROM {lens_table("rights")} WHERE application_date {window} GROUP BY 1
    ),
    e AS (  -- each event once: a right's repeated record of the same event on the same day counts once
        SELECT DISTINCT ip_right_type, application_number, event_type, event_category, {EVENT_DATE} AS event_date
        FROM {{iprapid/events}} WHERE {any_event}
    ),
    events AS (
        SELECT CAST(date_trunc('month', event_date) AS DATE) AS month,
            {counts(TIMELINE_EVENTS)}
        FROM e WHERE event_date {window} GROUP BY 1
    ),
    policy AS (
        SELECT CAST(date_trunc('month', date) AS DATE) AS month, string_agg(id, ', ' ORDER BY date) AS policy_events
        FROM {{policy_events/events}} GROUP BY 1
    ),
    cpi AS (  -- all groups, Australia (weighted average of the eight capitals), original, quarterly
        SELECT make_date(CAST(left(time_period, 4) AS INTEGER), 3 * CAST(right(time_period, 1) AS INTEGER), 1) AS month,
               value AS cpi
        FROM {{abs_prices/cpi}}
        WHERE index = '10001' AND region = '50' AND measure = '1' AND adjustment_type = '10' AND frequency = 'Q'
    ),
    j AS (
        SELECT months.month, apps.* EXCLUDE (month), events.* EXCLUDE (month), policy.policy_events, cpi.cpi
        FROM months LEFT JOIN apps USING (month) LEFT JOIN events USING (month) LEFT JOIN policy USING (month)
        LEFT JOIN cpi USING (month)
    ),
    nz AS (
        SELECT month, count(*) OVER w AS months_ahead,
        {nonzero}
        FROM j WINDOW w AS (ORDER BY month ROWS BETWEEN CURRENT ROW AND 11 FOLLOWING)
    ),
    f AS (SELECT {starts} FROM nz)
    SELECT
        j.month,
        year(j.month) AS year,
        month(j.month) AS month_of_year,
        {_fy("j.month")} AS fy,
        day(last_day(j.month)) AS days_in_month,
        {kept},
        j.cpi,
        j.policy_events
    FROM j CROSS JOIN f
    ORDER BY j.month
    """


LENSES = {
    "rights": rights_sql,
    "firms": firms_sql,
    "regions": regions_sql,
    "region_indicators": region_indicators_sql,
    "national": national_sql,
    "national_indicators": national_indicators_sql,
    "industries": industries_sql,
    "industry_indicators": industry_indicators_sql,
    "institution_rights": institution_rights_sql,
    "institutions": institutions_sql,
    "timeline": timeline_sql,
}
ORDER = [
    "rights",
    "firms",
    "regions",
    "region_indicators",
    "national",
    "national_indicators",
    "industries",
    "industry_indicators",
    "institution_rights",
    "institutions",
    "timeline",
]  # later lenses read the earlier ones


def build(name: str) -> None:
    """Write one lens table, atomically, and print its size."""
    LENS_DIR.mkdir(parents=True, exist_ok=True)
    out, tmp = LENS_DIR / f"{name}.parquet", LENS_DIR / f"{name}.parquet.tmp"
    t0 = time.time()
    con = connect()
    con.execute(f"COPY ({resolve(LENSES[name]())}) TO '{tmp}' (FORMAT parquet, COMPRESSION zstd)")
    tmp.replace(out)
    if name == "rights":  # the records the lens leaves out, recorded where they can be read
        DROPPED_DIR.mkdir(exist_ok=True)
        con.execute(f"COPY ({resolve(design_shells_sql())}) TO '{DROPPED_DIR / 'design_shells.csv'}' (HEADER)")
    rows = con.execute(f"SELECT count(*) FROM '{out}'").fetchall()[0][0]
    cols = len(con.sql(f"SELECT * FROM '{out}' LIMIT 0").columns)
    print(f"{name}: {rows:,} rows, {cols} columns, {out.stat().st_size / 1e6:.1f} MB, {time.time() - t0:.0f} s")


def main(argv: list[str]) -> None:
    names = argv or ORDER
    unknown = set(names) - set(LENSES)
    if unknown:
        sys.exit(f"unknown lens: {', '.join(sorted(unknown))} (choose from {', '.join(ORDER)})")
    for name in ORDER:
        if name in names:
            build(name)


if __name__ == "__main__":
    main(sys.argv[1:])
