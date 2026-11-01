# Amendments made in response to the audits (batch 261030)

What has been changed because of these audits, finding by finding, with the check made first. Each finding was
verified against the code, the lenses as built and the notebooks before anything was changed; a finding is cited as
in `INDEX.md` (for example "S1 L2 R47"). The website (`evidence/`, `analysis/atlas/`) is updated in its own pass and is
not covered here.

## Pass 1 (1 November 2026): the firm filing population

**Decision record:** ADR 0036 (`docs/adr/0036-one-filing-flag-for-firms.md`).

### How the issue was chosen

The owner asked for the most urgent cross-cutting issue, verified before any action, and corrected in the back end.
The recurring themes in `INDEX.md` were tested against three questions: does the claim hold against the code and the
data; does it change numbers or conclusions carried into Stage 3; and is its source in the back end (`build.py`, the
lenses), so that one fix corrects every use downstream?

| Theme (from `INDEX.md`) | Holds? | What the check found | Chosen |
|---|---|---|---|
| "Filer" defined differently within a lens; no linked filing treated as "never filed" | Yes, and a back-end defect | Three definitions of "has filed IP" in use. The `regions` lens counted firms from IP RAPID's own applicant panel, which predates the register's ABNs (ADR 0029), so 60,021 firms whose filings only the register's ABNs link were invisible to it. Active IP-filing firms placed in a postal area: 162,359 against 207,537 with every linked filing. R&D claimants "that have never filed IP": 50.7% against 48.3% with no filing linked (44.7% with no link to IP at all). One conclusion reverses (U47) and one figure was wrongly computed (B23's IPLORD share) | **Yes** |
| Current holder described as the filer; origin from a different party | Yes, but small | `timeline` (`ORIGINS` in `build.py`) and `industries` (`patents_standard_au`, `trade_marks_au`) take origin from the current holder (`australian_applicant`), against ADR 0013's rule that "who files" uses the founding columns. But holder and founder origin disagree for 0.2% to 1.8% of rights in each type and period (FY1985 to FY2026), and the Australian share of rights of known origin moves by at most 1.02 points (trade marks before FY2003: 61.68% by holder, 62.70% by founder; standard patents FY2017 to FY2026: 8.68% and 8.74%). The mixed-party concern (S1 L0-L1 R39, S2 L1 R06): the type of the first founder differs from the first Australian founder's for at most 0.121% of Australian-founded rights (31 of 25,650 standard patents, FY2010 to FY2019). B12's null branch is a real slip (unknown founding origin read as overseas when the type is known), affecting at most 224 standard patents filed FY2000 to FY2009 | Next (owner's item) |
| Later additions not carried back | Yes, in the samples checked | For example, U79's 1,409,875 leaves out the 15,282 rows of business survey cubes; B61 says "B34's gap holds" where B34 reports 104.9% of its fitted value. A document-consistency sweep, item by item, best done after back-end corrections, since each correction moves numbers again (this pass moved B27 and B28) | Later |
| Analysis beyond the stage's scope | A matter of framing | The method of each stage, not a defect in data or numbers | No |

The holder-and-founder figures come from queries on the `rights` lens as built on 1 November 2026 (comparing
`australian_applicant` with `founding_australian`, and `founder_type` with the type of the first Australian founding
party in `iprapid/party`); they are recorded here so the next pass need not repeat the check.

### Findings acted on

| Finding | The audit's claim | Verified | Amendment |
|---|---|---|---|
| S1 L2 R47 (High) | "IP filers" changes meaning: 301,249 trade mark filers but 265,615 ABNs with `ip_filed_total`; 323,604 by the per-type counts; 1,379,824 credits against 1,253,998 | **Confirmed**: all five figures reproduce. The cause, not shown by the audit: 60,035 ABNs are credited as filers but absent from IP RAPID's panel (60,021 of them through the register's ABNs only), and 2,046 are in the panel only (co-applicants not credited as the filer) | One flag, `firms.ip_record` (filed by either rule; another link to IP; none). U42 and U47 regenerated with it; U44 shows the reconciliation by ABN (263,569 both, 60,035 credited only, 2,046 panel only) and the flag (325,650 filed, 72,265 another link, 65,364 none); U112's filer count and size bands use it |
| S1 L2 R48 (High) | Zero-filled counts are not complete observations of non-use | **Confirmed**: a 0 is a recorded zero under the attribution rules; the 50,790 IPLORD-only firms carry 0 in every count | `ip_record` separates firms with a filing linked, with another link to IP, and with none; a note in U41. Not changed: the overview still shows the count columns as 100% filled (they are filled; the flag carries the meaning) |
| S1 L3 R15 (High) | "Never filed IP" is not established; whether the regions lens's counts include the register's ABNs is not shown | **Confirmed**: they did not. `regions` built `ip_filing_firms` and `rdti_firms_no_ip` from `ip_filed_total` | `build.regions_sql` counts by `ip_record`; `rdti_firms_no_ip` is now `rdti_firms_no_filing`, with `rdti_firms_no_ip_link` beside it. U54 restated: 48.3% with no filing linked, 44.7% no link to IP; filing firms 63.3 per 1,000 businesses in the cities (49.7 before) |
| S8-S9 R17 (High) | §9's "never filed IP" is unsupported | **Confirmed** | §9's and §3.8's U54 rows and `docs/stage-1-summary.md` restated with "no filing linked" and the new figures |
| S2 L2 R04 (High) | "Filed IP" changes definition within the lens: B22 and B24 the union, B23 `ip_filed_total` alone, B50 the per-type counts | **Confirmed** from the code | Every one uses `ip_record` (which equals the union, so B22's and B24's outputs are unchanged); B23 and B50 restated (B50: 0.704 to 0.825, 12.1 points, 4.7 to 17.8) |
| S2 L2 R08 (High) | B23's IPLORD percentage uses the wrong denominator | **Confirmed**: it was IPLORD membership among all claimants in a group, labelled as a share of the missing filers | Replaced by the share of claimants with no filing linked who are linked to IP another way, numerators and denominators shown: 10.9% (13.4%) of the oldest, not 54.3% (56.2%). The conclusion changes: another link to IP explains little of the group |
| S2 L2 R09 (High) | B23's "never filed" and "close to exact" are unsupported | **Confirmed** | "No filing linked" throughout; "close to exact" withdrawn |
| S2 L2 R10 (High) | Separate margins do not show a joint target group or an intervention benefit | **Confirmed**: no joint table was shown | A joint table of the group by entity and age: of 8,444 claimants with no filing linked, 95.7% are private companies, 55.3% private companies 3 to 10 years old on the record. "Where an intervention could add most" replaced by "a group for Q4 to examine, not a proven set of non-filers" |
| S2 L3 R06 (High) | B27 still calls claimants with no linked filing "never filing" | **Confirmed** | B27 reworded and restated from the re-run (128 distinct leads, 79 on IP or R&D; the share falls with every filing rate per business, -0.178 to -0.254). The screen's `missing_filer_share` is `no_filing_share` |

### What else changed as a result

- **U47's conclusion.** IP filers are a little more metropolitan than firms in general (86.9% in major cities against
  85.3%) but no more advantaged (33.3% in the top tenth of postcodes against 33.4%; 34.1% before). R&D claimants
  remain more of both. Corrected in the notebook and in `docs/stage-1-summary.md` (§4.3 and theme 3).
- **U42.** Sole traders are 10.6% of IP filers, not 4.1%; private companies 76.4%, not 82.2%.
- **B28.** 24,948 indicator pairs are leads (24,792 before): the false discovery correction runs over every pair, so
  changing one rate moves the threshold. `docs/stage-2-summary.md` updated.
- **Wording.** `GLOSSARY.md` gains "Filing linked (a firm's IP record)" and "No filing linked"; "missing filers" is
  no longer used for the group.
- **Tests.** `tests/test_eda.py::test_firms_have_one_filing_flag_and_regions_count_by_it`.

### Left for other passes

- **The website.** The atlas's observation files (`analysis/atlas/content/observations/` for U42, U47, U54, B23,
  B27 and B28) and `evidence/` still quote the superseded figures, and `analysis/atlas/charts.py` selects "IP filers"
  by `ip_filed_total > 0`. The five tests in `tests/test_atlas.py` stop at the atlas's numbers rule (its pages for
  U47, U54, B23, B27 and B50 quote figures no longer on the notebook's page) until the atlas is rebuilt, as they
  should; every other test passes (119).
- **Related findings not acted on:** S1 L2 R50 (first observed filing as entry), R51 (right-level linkage shares);
  S1 L3 R05 (other filled-cell claims), R07 and S2 L3 R07 (shared denominators); S1 L0-L1 R05 (missing values in the
  rights lens). They touch the same counts but are separate claims.
- **Incidental on re-running** (not caused by this pass, none quoted): a tie in the industries overview (699 or 698
  distinct values), the order of rows in one unordered table, and the titles `any_value` picks for some business
  survey cubes in U119's inventory.
- **The audits' hashes.** Both notebooks have changed, so the SHA-256 values in `INDEX.md` no longer match; a finding
  outside this pass still needs checking against the notebook before it is acted on.
