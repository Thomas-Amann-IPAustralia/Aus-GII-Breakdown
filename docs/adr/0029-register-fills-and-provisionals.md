# 0029: IP Australia's register fills IP RAPID's gaps in the lenses; empty design records dropped; every provisional with its inventors

**Date:** 2026-10-27. **Whose:** the owner decided to use the fills, reword the request to IP Australia, harvest every
provisional with its inventors (a gender analysis is to come), drop the design records with no information, and make
no guesses about the remaining designs' origin (A12, A13); Claude decided how.

**Context.** The register check (ADR 0028, `docs/audit-ipa-api.md`) found IP RAPID complete and accurate, and its gaps
in what it publishes: owners' ABNs and ACNs (OQ7), design applicants' countries (OQ14) and the register's own expedite
events (OQ6). It also found the 11,099 undated designs to be records with nothing in them (V16), and that the register
names provisionals' inventors, which Google Patents never sees (V15). The audit fetched only a sample and targets;
filling every year alike needs every record.

**Decision.**

1. **Two corpus sources read the register whole.** `ipa_register` takes every trade mark and design a page of 100 at
   a time (`/page/advanced`, about 20,000 records a minute; 2,338,036 trade marks and 269,048 designs on 27 October
   2026, under an hour). `ipa_provisionals` takes every provisional by number (the patent search cannot list): IP
   RAPID's 264,024, 236 filed since its release, and a recorded probe of 300 numbers missing inside the yearly
   sequences (none in the register, as a first probe of 360 found). Both flatten records as they arrive (raw trade mark
   responses would be about 25 GB), cache them so a run resumes on any day, and stop cleanly at `IPA_BUDGET_MINUTES`.
2. **The client counts only what the server counts.** Production's patent API answers about half its calls with 403
   or 500 at random; those answers carry no rate-limit headers and do not count toward the limit, so the client
   refunds them and retries at once. With 24 threads that gives about 500 patents a minute, against about 115 before:
   the provisionals take about nine hours, not days.
3. **Fills sit beside IP RAPID's values, never instead of them.** The `rights` lens gains `register_abn` (the ABN the
   register gives a current owner, else the ABN of the ACN it gives, where the ABR gives that ACN one ABN) and
   `register_abn_basis`; `filer_abn` (IP RAPID's founding applicant's ABN, else the register's while the right has not
   changed hands, since the register gives current owners); `has_abn_filled`; `register_country` and
   `australian_applicant_filled` (IP RAPID's origin, else the register's); and `register_expedited` and
   `register_expedite_date` (trade marks). Patents are not filled.
4. **Firms are credited by the filled filer ABN.** The ABN spine (`linkage`) takes the register's ABNs (463,279 ABNs,
   64,829 of them only through the register, flagged `in_register`); `firms` counts applications by `filer_abn` and
   adds `*_first_fy_filled` beside IP RAPID's first-filing years.
5. **Design shells are dropped and recorded.** A design with no date, applicant or class in IP RAPID and no owner, date
   or class in the register is left out of the lenses: 11,098, numbered 1973 to 1982, all ceased. The rule is
   `build.design_shells_sql()`; the build writes the list to `analysis/eda/dropped/design_shells.csv`, and a test
   checks that none is in the lens. Yearly counts do not change (the shells had no date); totals and shares across all
   rights do slightly.
6. **The observations are restated, not rewritten.** Notebook section 1.8.6 adds U99 to U104; U7, U13, U34 and U45 keep
   their wording and gain a restatement. Figures moved by the drop and the larger firms table are corrected (U1 to U4,
   U9, U13, U41 to U47, U88, U95, the summaries), and the atlas follows. The decisions revised: firm-level filing by
   year is compared to FY2026 with the filled columns (was: to FY2024, ADR 0016); trade mark expedite requests are
   compared across November 2018 with IP RAPID's events, and priority-claiming marks with either record (was: on one
   side only); design shares are no longer lower bounds once filled (the audit's D1).
7. **No guessing.** The 576 designs with an owner but no country, and the 15,154 with no owner anywhere, stay of
   unknown origin; name matching is not used.
8. **Provisionals' inventors and gender.** `ipa_provisionals/inventors` (R2, names) carries each inventor's given name
   and estimated chance of being a woman by the method of ADR 0022 (the World Gender-Name Dictionary). The register
   gives no inventor's country, so the first applicant's country in IP RAPID stands in (`country_basis` =
   `applicant`). The per-provisional counts (`provisionals`, repo) are attached to the lens when the harvest ends.

**Consequences.** U45's lead and U34's puzzle are explained as publication, not behaviour (U100, U101, U103), and the
request to IP Australia now asks why IP RAPID leaves these out (OQ6, OQ7, OQ13, OQ14 reworded). The filled ABN series
is not one constant method: the register records more ABNs in recent years (23% to 29.2% of IP RAPID's gaps filled to
FY2019, 77.4% in FY2026), so its earlier years are lower bounds (U100). The harvests rerun with `corpus run
ipa_register`, `corpus run ipa_provisionals` and `corpus run linkage`, then `python -m eda.build`.
