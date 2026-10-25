"""Build the lens tables: one analysis-ready table per unit of analysis, written to `analysis/eda/data/` (gitignored).

    uv run python -m eda.build              # every lens (about two minutes once the R2 tables are cached)
    uv run python -m eda.build firms        # one lens

| Lens | One row per | Built from |
|---|---|---|
| `rights` | IP right (patent, trade mark, design, plant breeder's right) | `iprapid/*_rights`, `party`, `events` |
| `firms` | ABN in any IP, R&D, procurement or tax source | `linkage/abn_spine`, `rights`, `rdti`, `ato_ctt` |
| `regions` | Postal area (the ABS's version of a postcode) | `abs_regions`, `abs_census`, `abr`, `rights`, `firms` |
| `national` | Country, year and indicator | `wdi/panel`, `wipo_ipstats/office_origin`, `oecd/msti` |
| `timeline` | Month, for Australia (IP Australia's whole register) | `rights`, `iprapid/events`, `policy_events` |

Every column is described, in plain English, in `analysis/eda/variables.yaml`. Derived columns are defined here and
nowhere else, so a reader can check exactly how each was made.
"""

from __future__ import annotations

import sys
import time

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
    then true, and the lifetime is unfinished). Only rights that were granted or registered have a lifetime."""
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
    agent_info AS (
        SELECT party_id AS agent_id,
               any_value(CASE WHEN party_type = 'organisation' THEN party_name END) AS agent_name
        FROM {{iprapid/party}} WHERE party_role_category = 'applicant_agent'
        GROUP BY 1
    ),
    founders AS (  -- each founding applicant or owner, as first recorded
        SELECT * FROM (
            SELECT ip_right_type, application_number, party_id, party_type, country_code, state_code,
                   {_postcode("post_code")} AS postcode, effective_from_date AS since,
                   max(abn) OVER (PARTITION BY ip_right_type, application_number, party_id) AS abn,
                   row_number() OVER (PARTITION BY ip_right_type, application_number, party_id
                                      ORDER BY effective_from_date, country_code NULLS LAST) AS k
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
    dated AS (
        SELECT *,
               CASE WHEN applicant_country = 'au' THEN {_postcode("applicant_postcode")} END AS postcode_au,
               CASE WHEN year(gained_registration_status_date) >= 1904 THEN gained_registration_status_date END
                   AS registered,  -- one trade mark is dated 1 January 1901
               nullif(deemed_retired_date, DATE '1970-01-01') AS retired  -- all 1,282 were filed from 2013
        FROM r
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
        END AS years_in_force
    FROM dated r
    LEFT JOIN applicants a USING (ip_right_type, application_number)
    LEFT JOIN agents g USING (ip_right_type, application_number)
    LEFT JOIN agent_info ai ON ai.agent_id = g.agent_id
    LEFT JOIN founding f USING (ip_right_type, application_number)
    LEFT JOIN holders h USING (ip_right_type, application_number)
    LEFT JOIN poa_state ps ON ps.poa_code = r.postcode_au
    LEFT JOIN poa_state fs ON fs.poa_code = f.founder_postcode
    LEFT JOIN milestones m USING (ip_right_type, application_number)
    """


def firms_sql() -> str:
    return f"""
    WITH ip AS (  -- applications by the filer: the first founding applicant with an ABN (ADR 0013, 0016)
        SELECT founder_abn AS abn,
               count(*) FILTER (patent_type = 'standard') AS n_patents_standard,
               count(*) FILTER (patent_type = 'provisional') AS n_patents_provisional,
               count(*) FILTER (patent_type = 'second_tier') AS n_patents_second_tier,
               count(*) FILTER (ip_right_type = 'trade_mark') AS n_trade_marks,
               count(*) FILTER (ip_right_type = 'design') AS n_designs
        FROM {lens_table("rights")} WHERE founder_abn IS NOT NULL GROUP BY 1
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
    LEFT JOIN place ON place.poa_code = {_postcode("s.postcode")}
    """


def regions_sql() -> str:
    lo, hi = WINDOW
    seifa = ",\n        ".join(
        f"max(value) FILTER (index_type = '{i}' AND measure = '{m}') AS {i.lower()}_{n}"
        for i in ("IRSAD", "IRSD", "IER", "IEO")
        for m, n in (("SCORE", "score"), ("RWAD", "decile"))
    )
    return f"""
    WITH seifa AS (
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
    ip AS (
        SELECT applicant_postcode AS poa_code,
               count(*) FILTER (patent_type = 'standard') AS patents_standard,
               count(*) FILTER (patent_type = 'provisional') AS patents_provisional,
               count(*) FILTER (patent_type = 'second_tier') AS patents_second_tier,
               count(*) FILTER (ip_right_type = 'trade_mark') AS trade_marks,
               count(*) FILTER (ip_right_type = 'design') AS designs
        FROM {lens_table("rights")}
        WHERE applicant_postcode IS NOT NULL AND filing_fy BETWEEN {lo} AND {hi}
        GROUP BY 1
    ),
    firms AS (
        SELECT postcode AS poa_code,
               count(*) FILTER (abn_active AND ip_filed_total > 0) AS ip_filing_firms,
               count(*) FILTER (abn_active AND in_rdti) AS rdti_firms,
               count(*) FILTER (abn_active AND in_rdti AND ip_filed_total = 0) AS rdti_firms_no_ip
        FROM {lens_table("firms")} GROUP BY 1
    )
    SELECT
        p.poa_code,
        p.state_name AS state,
        p.ra_name AS remoteness,
        p.share_major_cities,
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
        coalesce(firms.ip_filing_firms, 0) AS ip_filing_firms,
        coalesce(firms.rdti_firms, 0) AS rdti_firms,
        coalesce(firms.rdti_firms_no_ip, 0) AS rdti_firms_no_ip,
        1000.0 * coalesce(ip.patents_standard, 0) / nullif(abr.active_gst_abns, 0)
            AS patents_standard_per_1k_businesses,
        1000.0 * coalesce(ip.trade_marks, 0) / nullif(abr.active_gst_abns, 0) AS trade_marks_per_1k_businesses,
        1000.0 * coalesce(ip.designs, 0) / nullif(abr.active_gst_abns, 0) AS designs_per_1k_businesses
    FROM {{abs_regions/poa}} p
    LEFT JOIN seifa USING (poa_code)
    LEFT JOIN census USING (poa_code)
    LEFT JOIN abr USING (poa_code)
    LEFT JOIN ip USING (poa_code)
    LEFT JOIN firms USING (poa_code)
    WHERE p.ra_name NOT IN ('Outside Australia', 'Migratory - Offshore - Shipping (WA)')
      AND p.ra_name NOT LIKE 'No usual address%'
    """


def national_sql() -> str:
    iso3 = {c.alpha_2: c.alpha_3 for c in pycountry.countries}
    pairs = ", ".join(f"('{a2}', '{a3}')" for a2, a3 in sorted(iso3.items()))
    oecd = ", ".join(f"'{c}'" for c in OECD)
    wipo = {
        10: ("WIPO.PAT.APP", "Patent applications filed worldwide by residents (all offices)"),
        23: ("WIPO.PAT.GRANT", "Patent grants received worldwide by residents (all offices)"),
        48: ("WIPO.TM.CLASS", "Trade mark applications by residents, counted in classes (all offices)"),
        68: ("WIPO.DES.COUNT", "Industrial design applications by residents, counted in designs (all offices)"),
    }
    cases = " ".join(f"WHEN {k} THEN '{c}'" for k, (c, _) in wipo.items())
    names = " ".join(f"WHEN {k} THEN '{n}'" for k, (_, n) in wipo.items())
    return f"""
    WITH iso(a2, a3) AS (VALUES {pairs}),
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
        FROM {{oecd/msti}} m JOIN iso ON iso.a3 = m.reference_area
        WHERE m.measure IN ('G', 'B') AND m.unit_of_measure = 'PT_B1GQ' AND m.value IS NOT NULL
        GROUP BY m.reference_area, m.time_period, m.measure
    ),
    wipo AS (
        SELECT iso.a3 AS iso3, any_value(o.origin) AS country, o.year,
               CASE o.indicator_id {cases} END AS indicator,
               CASE o.indicator_id {names} END AS indicator_name,
               sum(o.value) AS value, NULL::VARCHAR AS status, 'WIPO' AS source
        FROM {{wipo_ipstats/office_origin}} o JOIN iso ON iso.a2 = o.origin_code
        WHERE o.indicator_id IN ({", ".join(map(str, wipo))}) AND o.breakdown IS NULL
        GROUP BY iso.a3, o.year, o.indicator_id
    )
    SELECT u.* REPLACE (coalesce(n.name, u.country) AS country),  -- one name per country (the World Bank's)
           u.iso3 IN ({oecd}) AS oecd, u.iso3 = 'AUS' AS australia
    FROM (SELECT * FROM wdi UNION ALL SELECT * FROM wipo UNION ALL SELECT * FROM oecd) u
    LEFT JOIN {{wdi/countries}} n ON n.iso3 = u.iso3
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
    "national": national_sql,
    "timeline": timeline_sql,
}
ORDER = ["rights", "firms", "regions", "national", "timeline"]  # later lenses read the earlier ones


def build(name: str) -> None:
    """Write one lens table, atomically, and print its size."""
    LENS_DIR.mkdir(parents=True, exist_ok=True)
    out, tmp = LENS_DIR / f"{name}.parquet", LENS_DIR / f"{name}.parquet.tmp"
    t0 = time.time()
    con = connect()
    con.execute(f"COPY ({resolve(LENSES[name]())}) TO '{tmp}' (FORMAT parquet, COMPRESSION zstd)")
    tmp.replace(out)
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
