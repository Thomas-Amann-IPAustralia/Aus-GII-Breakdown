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
| Current holder described as the filer; origin from a different party | Yes, but small | `timeline` (`ORIGINS` in `build.py`) and `industries` (`patents_standard_au`, `trade_marks_au`) take origin from the current holder (`australian_applicant`), against ADR 0013's rule that "who files" uses the founding columns. But holder and founder origin disagree for 0.2% to 1.8% of rights in each type and period (FY1985 to FY2026), and the Australian share of rights of known origin moves by at most 1.02 points (trade marks before FY2003: 61.68% by holder, 62.70% by founder; standard patents FY2017 to FY2026: 8.68% and 8.74%). The mixed-party concern (S1 L0-L1 R39, S2 L1 R06): the type of the first founder differs from the first Australian founder's for at most 0.121% of Australian-founded rights (31 of 25,650 standard patents, FY2010 to FY2019). B12's null branch is a real slip (unknown founding origin read as overseas when the type is known), affecting at most 224 standard patents filed FY2000 to FY2009 | Next (owner's item); **done in pass 2** |
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

## Pass 2 (2 November 2026): origin is the filer's, from one party

**Decision record:** ADR 0037 (`docs/adr/0037-origin-is-the-filers.md`). The owner asked for it (A18), as pass 1
proposed (OQ23).

### The check made first

Pass 1's triage found the holder-versus-filer theme real but small; pass 2 re-checked each claim against the code,
the rebuilt lenses and both notebooks before changing anything.

- **The rule existed and was not applied.** ADR 0013 says "where and who files" uses the founding applicants, and ADR
  0024 found `founding_australian` reproduces IP Australia's resident counts. `build.py` still took the `timeline`
  lens's origin series (`ORIGINS`) and the `industries` lens's Australian counts from `australian_applicant`, the
  current holder.
- **Size:** yearly Australian shares move by up to 0.7 points for standard patents, 1.6 for designs and 4.4 for plant
  breeder's rights (U7's table); counts by tens (April 2013's Australian standard patents, 1,018 by the holder and
  1,044 by the filer).
- **Which definition matches whom.** Against the World Bank's resident patents (WIPO's), 1989 to 2024: median ratio
  1.0017 by the holder, 1.0110 by any founding applicant (IP Australia's definition), 1.0006 by the first founding
  applicant. WIPO counts a resident by the first-named applicant; `variables.yaml` had said the World Bank and WIPO
  count by the current applicant, which was wrong.
- **Two parties:** the first founder's type differs from the first Australian founder's for at most 0.121% of
  Australian-founded rights; the same pairing was in the `regions` lens's counts of organisations' filings.
- **B12's null branch:** unknown origin read as overseas for at most 224 patents.

### Findings acted on

| Finding | The audit's claim | Verified | Amendment |
|---|---|---|---|
| S1 L0-L1 R04 (High) | §1.8.1 defines `applicant_*` as the current holder, yet U5 to U8, U13, U15 and U90 to U94 describe filers with them | **Confirmed**, cell by cell | Every filer claim uses the founding columns: origin `founding_australian`, type and origin `filer_group`, place `founder_state`, ABN `founder_abn`, counts `founder_count`. U7, U8, U13, U15, U16, U20, U90, U91, U93, U94, U98, U105 to U107 restated (U5's counts by type do not depend on origin) |
| S1 L0-L1 R39 (High) | U13 (and later queries) pair an any-founder Australian flag with the first founder's type | **Confirmed**, and found in the `regions` lens too; small (at most 0.121%) | `rights.filer_group` takes origin and type from one party; notebook 1's cells, Stage 2's `FILER` and the regions lens's organisations' counts use it |
| S1 L0-L1 R43 (Medium) | Shares of rights described as shares of filers (U20, U34, U100) | **Confirmed** for U20 and U100 | U13 and U20 say shares are of applications; U100's heading reworded. U34 not changed (its claim is about expedite events, left for the sweep) |
| S1 L4 R12 (High) | Lens 4 uses `australian_applicant` to reconcile resident filings and to select Australian families (U67, U115) | **Confirmed** | U67 by the filer's origin, with the first founding applicant's country shown as the WIPO-comparable count (median 1.011 and 1.001); U115 selects families by the filer's origin |
| S1 L5 R03 (High) | Lens 5's origin series are built without saying from which party | **Confirmed**: the current holder's | `ORIGINS` uses `founding_australian`; `variables.yaml` and U22 say so; U22 to U29 restated. The design series stay IP RAPID's (fills sit beside, ADR 0029; U102 has the filled shares) |
| S1 L5 R09 (Medium) | U26 calls pooled provisional and plant breeder's series "Australian filers" | **Confirmed** | U26 separates the origin-split series from the two pooled ones (with their Australian shares) and defines the measure as a ratio to the surrounding months |
| S8-S9 R05 (High) | §9's 91.3% overseas and 59.0% Australian are holder classifications | **Confirmed** | §9, §1.9 and `docs/stage-1-summary.md` restated by the filer's origin (91.3% overseas, the United States 43.6%; trade marks 59.2%) |
| S2 L1 R06 (High) | `FILER` mixes parties; B12 sends unknown origin to overseas; some text uses holder fields | **Confirmed** | `FILER` is made from `filer_group` (empty when origin is unknown); B5 to B19 and B55 restated; B19 and B26 keep the holder for "moved overseas", which is about who holds |

### What else changed as a result

- **The timeline and industries in notebook 2.** B36 to B39, B47 to B49, B52 and B56 (the timeline's origin
  series) and B40, B41 (the industries lens's Australian counts) restated. One conclusion softened: in B47, the
  Designs Act 2003's rush from overseas is now within the placebo range (12.5%; its step is still beyond it), and the
  October 2016 trade mark cut's overseas step is at the threshold (5.556%), so fee changes show 3 rushes and 2 steps
  beyond 95% of placebos, not 4 and 3. `docs/stage-2-summary.md` updated.
- **Places.** Organisations' filings now counted by the party that gives the postcode: B27, B28 (24,947 indicator
  pairs are leads), B31, B58 and U48 move in the third decimal.
- **U7.** Trade marks' FY1995 Australian share is no longer given: the founding applicant's country is missing for
  6.3% of them. U24: trade marks of unknown filer's origin run at a median 5 a month (by the holder, mostly none).
- **U1** counts 88 columns; **U99** and **U102** give the filer's filled origin (designs 32.64% Australian, 0.083%
  unknown; the register fills only designs that have not changed hands).
- **Wording.** `GLOSSARY.md` gains "Filer's origin" and "Filer group"; `variables.yaml` labels `australian_applicant`
  as the current holder's.
- **Tests.** `tests/test_eda.py::test_filer_origin_comes_from_one_party_and_feeds_the_timeline`. The IP Australia
  benchmark (`python -m audit.benchmark`) is unchanged: it already used the founding applicants.

### Left for other passes

- **The website,** as after pass 1: the atlas's pages for the restated observations quote the old figures, and
  `tests/test_atlas.py` stops at its numbers rule until the atlas is rebuilt.
- **`founder_abn`** remains "the first founding applicant with an ABN" (ADR 0016), a third selection rule; for a
  jointly filed right it can be another party than `filer_group`'s. Not changed: the firms lens's crediting rests on
  it, and pass 1 measured that lens.
- **The sweep of later additions not carried back** (24 findings) and the other recurring themes in `INDEX.md`.

## Pass 3 (2 November 2026): later additions carried back

**Decision record:** ADR 0038 (`docs/adr/0038-later-additions-carried-back.md`). The owner asked for the audit work
to continue, correcting what holds (A19); this is the sweep that passes 1 and 2 proposed.

### The check made first

Each of the 25 findings in the theme "later additions or corrections not carried back" (`INDEX.md`) was checked
against both notebooks as they stood after pass 2, the lenses as rebuilt on 2 November 2026, and both stage summaries.
None is false; 19 hold in full and 6 in part. The audits' hashes no longer match (passes 1 and 2), so every locator was
found again by observation number and cell id.

### Findings acted on

| Finding | The audit's claim | Verified | Amendment |
|---|---|---|---|
| S1 L0-L1 R12 (High) | U13's ABN conclusion, design-origin results and a route caption are not updated for U99 to U102 | **In part.** U13's ABN figures were restated in pass 2 (13% to 21%, pointing to U99 and U100). The caption is false: designs' origin is unknown for 4.6% to 23.4% of each five-year period's designs (a lens query), not "recorded for few Australian designs" | Caption corrected (cell `5d808e57`, citing U7's 4.0% to 25.1% a year); §1.9's U13 row points to the register's fills. **Not done:** making the filled results primary, against ADR 0029 and the owner's A12 (fills beside IP RAPID's columns) |
| S1 L0-L1 R32 (High) | U34's lead and one-side-only decision stand after U103; IP RAPID, register and either-record rates not distinguished | **Confirmed**: U103's table gives either-record rates of 4.94% (FY2018), 14.97% (FY2019) and 24.11% (FY2020) for marks without priority, against IP RAPID's 4.81% and 4.48% | U34's heading and decision retired with a dated restatement; the three records distinguished; §1.9's row and `docs/stage-1-summary.md` (themes 7 and 9, §4.1, the rules, the leads, the index) restated |
| S1 L0-L1 R36 (Medium) | One authoritative version; external checks unlabelled | **In part.** U1 and U4 already point to U104. Found: U0's lens table gave 4,368,006 rights and 398,450 firms (4,356,908 and 463,279 now); U17 did not point to U35's assignment measure; U99's check is documented outside the page | U0's table corrected; U17 points to U35; U99's check labelled as documented in `docs/audit-ipa-api.md`, not re-run. The notebook's dated "Restated" lines serve as the change log (ADR 0038) |
| S1 L2 R49 (High) | U45's chart and table use the unfilled first years; the fall is reduced, not removed; patent scopes differ | **Confirmed**: cell `ce3fe734` plotted `*_first_fy` (trade marks 7,384 in FY2026) though U45's revised decision uses the filled columns; `patent_first_fy` is any patent, `patent_first_fy_filled` standard patents only (`variables.yaml`) | The chart plots filled trade marks and designs, IP RAPID's dashed, and patents by IP RAPID's any-patent column, named as such; U45's heading no longer "a lead"; 92.3% to 90.9% is "much reduced, not removed"; standard patents' fall (88.7% to 83.9%) stands, unfilled; §2.7's row |
| S1 L2 R70 (Medium) | §2.7 drops qualifications; acronyms not expanded; prerequisites | **In part.** Pass 1 restated U42, U44 and U47. ABN, ABR, ACN, GST, IRSAD and WGEA were not expanded in §2 | A terms paragraph opens §2; U44's row says 55.3% is of the standard patents credited to an ABN and that no filing linked is not proof of none. **Not done:** the notebook runs top to bottom by design, so shared definitions stay in the setup |
| S1 L3 R02 (Medium) | U55's total is a five-source subtotal; "every value they publish" | **Confirmed**: the query excluded `ato_postcode` and `census_tsp` while its chart included all seven: 28,960,234 rows and 11,379 indicator-periods in all | The table covers seven sources and prints the five-source subtotal (22,511,923, 8,874); U55, §3's introduction and §3.5 restated; "the values taken from their selected tables" |
| S1 L3 R06 (Medium) | U49's prospective wording after U87; six or seven universities | **Confirmed**: Stage 2 never placed these patents by institution; the summary said six, the observation lists seven codes | U49 cites U87 (742 of 1,474, 50.34%) and says placement is proposed, not done; §3.8's and §9's rows |
| S1 L3 R32 (Medium) | §3.8 and §9 lose qualifications | **In part.** U53's range mixed postal areas (68.2%, 6.7%) with pooled SA3s (72.5%, 15.5%); U56's row lacked the 1,000-person threshold; U49's action was stale. "Never filed" was already corrected in pass 1 | U53 (chance named as a Poisson model), U55, U56 and U49 rows; the Stage 1 summary's theme 3 and §4.4 |
| S1 L4 R14 (Medium) | U68's total excludes later additions | **Confirmed**: the query left out WIPO's families by origin (11,579 rows), ABS Schools (300) and the GII supplements (23), 11,902 in all | The cell prints the reconciliation to 41,230,072 rows; U68 restated, with text and empty rows noted; §4.4 and §4.7 |
| S1 L4 R28 (Medium) | U63 and U69 not pointed to U120; U120's 11.8 in 2023 not on the page | **Confirmed**: the value is in the data (`GIISUP.2.1.5`) but the query kept the latest year only | U120's cell prints 2023 and 2025; U63 and U69 point to U120, distinguishing the published series' gaps |
| S1 L5 R02 (Medium) | U22's column count, U23's fifteen, U28's missing fees, the status ending at U104 | **Confirmed**: 79 columns (35 + 26 fee + 4 Reserve Bank + 10 national accounts + 4 PBS); 18 rows in U23's table | U22, U23, U28, §5's introduction, notebook 1's status, §5.11, and the Stage 1 summary (18 series in three places; the fee history marked done) |
| S1 L5 R13 (Medium) | U27 and U29's leads already settled by U38 and U39 | **Confirmed** | Both linked, with what U38 does not show; §5.11's portfolio transfer reads "what may be one" (U29 says the data do not name it) |
| S1 L5 R32 (Medium) | §5.11 says cessations "keep rising"; added series little profiled | **In part.** Trade mark cessations were 29,802 (2019), 28,283 (2021), 28,319 (2023), 35,484 (2025). U30's base already reads correctly | U27 and §5.11 restated; a note marks the profiling of state final demand, nominal GDP and the PBS series as incomplete |
| S1 L6 R02 (High) | U73 omits gross value added, filled for every division and year | **Confirmed** from the overview (`gva_cvm` 100% filled, 19 divisions, FY1990 to FY2026) | A compact profile of value added in the overview cell (manufacturing 14.2% of the divisions' sum in FY1990, 6.0% in FY2026); U73, §6's introduction and §6.7; the scope decision revised for value added. A slip of this pass corrected before publishing: value added was first said to be followed over time in B57, which uses FY2024 and FY2025 only |
| S1 L6 R03 (High) | U75 and §6.7 treat the services crosswalk as future work; windows differ; totals "agree" | **Confirmed** | U75 links U114 with the matched window (90.63% against 79.67%, FY2016 to FY2025); "nearly equal (2 apart)"; the lead retired |
| S1 L6 R15 (Medium) | U79's total excludes the cubes; rows are not values | **Confirmed**: 1,409,875 plus 15,282 cube rows is 1,425,157 | The cell prints the reconciliation and the cubes' empty rows; U79 and §6.7 |
| S1 L7 R21 (High) | U85 lacks U121's coverage note; U80 omits NSRC; §7.9 sheds qualifications | **Confirmed**; U121's "does not change the institutions' order" is untested (23 sampled works) | U85 states the lower bound (about 5.6%, 3.5% to 8.3%) and that the rankings' robustness is not tested; U121's decision says it is an assumption; U80 adds NSRC (2000 to 2015, 82 institutions); §7.9 |
| S8-S9 R03 (Medium) | §9's pointers obsolete; fees "missing" twice; §8 omits later sources | **Confirmed** | Pointers 1.9, 2.7, 3.8, 4.7, 5.11, 6.7, 7.9; an "added after Stage 2" note with its limits; §8 gains a row of the sources added after Stage 2 |
| S8-S9 R21 (High) | "Divisions near certain" overstated; the services comparison done | **Confirmed** | §9's U75 row says weights are concentrated (median 0.996, U74), not proven right, with the matched-window comparison; item 7 defines allocated IP per business. The Stage 1 summary's §4.6 and rules likewise |
| S2 L1 R29 (High) | B11, B12 and §1.9 keep conclusions B55 restricts; B55 "yes"; "B8's reach"; the inventory omits B55 | **Confirmed**; also B19's earlier cohort (FY2003 to FY2011) rests on the older family records | B11's heading, B12, B19 and B55 (its limits added; B8 named correctly) restated; §1.9's rows (B11 not replicated; B12 from FY2010; B55 explains rather than replicates); notebook 2's status lists B47 to B62; §8 and `docs/stage-2-summary.md` |
| S2 L2 R26 (Medium) | Size and industry said absent though WGEA adds them; B51 too absolute | **Confirmed**: 683 firms with a WGEA report have under 100 employees in their latest one (a new column in U112's table); B20's screen skips the WGEA columns (`screens.yaml`) without saying so | B20, B24, B51, §2.7's gap paragraph and rows; U112's decision |
| S2 L3 R10 (Medium) | §3.1's 6,406 indicators are a five-source subset | **Confirmed**: the query excludes the ATO (243 indicators) and the Census time series (233) | Named the original five-source screen, its exclusions and why its false discovery family is kept. Also found: §3.7 still gave B28's 24,948 leads, 24,947 since pass 2 |
| S2 L3 R33 (High) | The places summaries overstate; B58, B59 not reconciled | **In part.** "1.7 to 1.9" is standard patents unadjusted (with remoteness, 1.44 and 1.49); B29's heading claimed the joint reading in SA3s, never fitted; B59's "yes" means the same sign; §8's row stopped at B31 | B29's heading; §3.7's rows; a note that B29 (levels) and B59 (changes) answer different questions; §8's row includes B58 and B59. **Not done:** the business-owner denominator, which is B58's stated measure |
| S2 L4 R22 (High) | B61 does not replicate B34's gap | **Confirmed**: B34 puts Australia at 104.9% of its prediction in 2016 to 2020 | B61's claim removed; what each analysis measures stated; a rank contrast is not a shortfall |
| S2 L4 R24 (Medium) | §4.5 strengthens claims; "named most often" with no tally | **Confirmed** | Populations, periods and intervals restored; candidate factors split into measured and proposed; the same "named most often" wording replaced in §1.9, §3.7 and §8 |

### What else changed as a result

- **The Stage 1 summary** (`docs/stage-1-summary.md`) was behind the notebook beyond the audits' scope: its lens
  table (rows, columns and the three subtotals), §4.1 (rights before U104), §4.3 (firms before the register's ABNs:
  398,450 ABNs, five schemes, 74.7% private companies, a median age of 13.6) and the index rows; all restated.
  `docs/eda-plan.md`'s lens table likewise.
- **No conclusion carried to Stage 3 reverses.** Narrowed: B11 and B12 hold from FY2010; B61 is no longer evidence that
  Australia under-patents; value added reopens a longer industry comparison for Stage 3.
- **Outputs added to put a claim on the page:** U120's 2023 value, the inventories' reconciliations, gross value
  added's profile and the count of WGEA reporters under 100 employees. Notebook 1 re-executed whole; notebook 2's
  changes are to text only.

### Left for other passes

- **The website,** as after passes 1 and 2.
- **The other open themes** in `INDEX.md` (first observed filing as entry; survival as value; ownership histories;
  attorney representation; geographic allocation; WGEA's latest attributes; policy timing; and the rest), and the
  findings outside any theme.

## Pass 4 (2 November 2026): first observed filing, firms' age, and reproducible builds

**Decision record:** ADR 0039 (`docs/adr/0039-first-observed-filing-and-exact-ages.md`). The owner asked for the next
theme, looked at "deeply and widely to ensure all errors are expunged" (A20).

### The check made first

The theme "first observed filing treated as true entry" has three findings; four more rest on the same computation
(firms' age at filing) and were taken with it. Each was checked against `build.py`, the lenses, both notebooks and both
stage summaries. Then the check went wider: every age and first-filing computation in both notebooks, every claim of
"entry", "first-time", "lower bound" or "years old" in them and the summaries, and, when one count moved with nothing
behind it, the reproducibility of the build itself (two full builds compared table by table).

### Findings acted on

| Finding | The audit's claim | Verified | Amendment |
|---|---|---|---|
| S1 L0-L1 R31 (High) | U100 "does not fall"; U101's "entry"; U102's lower bounds could be biased either way | **In part.** U100 and U101 confirmed: the filled share falls 92.3% to 90.9% (trade marks) and 92.3% to 89.3% (designs); first observed filings are not entry. **Not confirmed:** U102. IP Australia's counts (D1, `docs/audit-ip-australia.md`) show IP RAPID's unknown-origin designs are mostly Australian, so its known-origin shares are lower bounds, about 2 points low, as the filled share shows | U100's heading quantifies the fall; U101 restated with a check (below); U102's lower-bound reading kept and its evidence named. A slip of this pass corrected before committing: U102 was first reworded to "biased either way", then restored on finding D1 |
| S1 L2 R50 (High) | U45: first observed filing is not entry; "lower bounds" not assured; the publication mechanism not shown | **Confirmed.** Of each year's first observed linked trade mark filers, 4.32% to 9.1% were already linked to IP another way (an earlier trade mark in IP RAPID's panel or held, a patent or design, or IPLORD's link to FY2020): 852 of 19,730 in FY2026. Filers with no ABN are missed. So the counts are neither upper nor lower bounds | A table in U101's cell (`ae577e36`) shows the overlap each year; U45, U101, the chart's title, axis and caption (`ce3fe734`) say "first observed linked"; U100's "So" bullet says the mechanism is not shown (OQ7) |
| S2 L2 R17 (High) | B25: first observed filing is not entry or a guaranteed age bound; medians across groups do not show sequencing | **Confirmed, and larger**: 17.07% to 19.57% of first observed filings are dated before the firm's first public registration | B25 rebuilt from dates, with filings before registration reported apart and a within-firm comparison: the trade mark first for 72.86% (71.55% to 74.13%) of 4,550 firms with both |
| S2 L2 R15 (High) | B25 and B26 filter on `NOT age_truncated`, not first seen from 2001; B26's 4,341 ten-plus patents are impossible under the stated rule | **Confirmed**: `age_truncated` never flags an ASIC-dated company; 51,712 were first seen before 2001. Restricted to firms first seen from 2001, B26's earlier ten-plus band holds 2 patents | The sample is named ("not truncated") and the from-2001 subset shown as a sensitivity check in both; §2.4 and §2.5 say which is which |
| S2 L2 R16 (High) | `fy - 0.5` is the start of the financial year; negative ages counted in the first year; B26 uses calendar years; the axis is a density | **Confirmed** (financial years are named by their end, `build._fy`) | Ages from dates: the lens gains the three `*_first_date_filled` columns; B26 uses each patent's application date; the axis reads "probability density" |
| S1 L2 R54 (High) | U43's age needs a reference date and population; undated firms read as not truncated | **Confirmed**: the 32,600 undated firms had `age_truncated` false | The flag is empty when there is no date (`build.firms_sql`, a test); U43 states the date (22 October 2026), the population (430,679 dated ABNs, active or not), what the flag does and does not catch (a new table), and that age usually understates but does not bound a business's start |
| S8-S9 R15 (High) | §9's firm populations and bounds overstated; 19,730 is first observed, not first ever | **In part** (the entry and bound parts; the IPLORD count belongs to another finding) | §9's row: "first observed linked", with the 4.32% overlap; "lower bounds, if each recorded link is right" |

### Found by the wider check, not in the audits

1. **Undated firms counted as the oldest.** Notebook 2's `AGE` grouping (B22, B23) sent a missing age to "20 years or
   more". No table moved: every undated firm is inactive (32,348) or not in the ABR (252), and those tables use active
   ABNs. Fixed: undated firms are their own group. The firms screen did move, through the flag: entity type against
   truncation 0.441 to 0.452, local government 15.9 to 14.8 times chance (B21).
2. **Builds that differed from run to run.** Two builds of the same corpus differed in 383,271 values of
   `region_indicators`, 696 rows of `industries`, 3,190 of `industry_indicators`, 677 of `regions` and 228 of
   `institutions`, all in the last digits of parallel sums of fractions. B28's lead count moved between 24,947 and
   24,948 from one build to the next, so pass 2's move of one lead, credited to ADR 0037, cannot be told apart from it.
   Fixed with exact decimal sums (`build._exact_sum`); two full builds now agree in all eleven lenses. The first fix
   tried (ordered sums) nearly tripled memory and killed notebook 1's kernel; it was replaced before committing.
3. **A label that changed between runs:** U119's example cube titles (`any_value`, noted in pass 1); now fixed.
4. **Stale since earlier passes:** §1.9's U99 row (designs of unknown origin 29,628 to 4,622, against U99's 30,215 to
   5,539 since pass 2); the Stage 1 summary's rule that firm filing by year stops at FY2024 (revised by U45); the
   firms lens's column count (54 now).
5. **B22's age** is on the record at 22 October 2026, not at the time of the claim or contract; now said.

### What else changed as a result

- **B26's conclusion weakens.** The youngest firms' patents moved overseas more in FY2003 to FY2011 (5.79%, 3.98% to
  8.35%) but not clearly in FY2012 to FY2021 (2.89%, 1.95% to 4.26%, overlapping every band); patents filed before the
  firm's first registration move most in both periods (7.01%, 7.77%). §2.7, §8 and `docs/stage-2-summary.md` updated.
- **B25's figures lengthen** (medians 2.61, 5.22 and 5.24 years) and its ordering rests on the within-firm comparison.
- **Wording.** `GLOSSARY.md` gains "First observed linked filing" and "Reproducible build", and qualifies "Lower bound"
  and "Left-truncated". The Stage 1 summary's firms section and rules restated.
- **Tests.** `tests/test_eda.py::test_firms_age_basis_names_the_date_that_set_first_seen` now also checks that
  undated firms have no flag and that each first filing's date falls in its financial year. Both notebooks re-executed;
  the IP Australia benchmark is unchanged.

### Left for other passes

- **The website,** as before.
- **Related findings not acted on:** S1 L2 R51 (linkage shares are of applications, now said in U100, but its party
  and provisional points are separate), the IPLORD count in S8-S9 R15, and S2 L2 R18 to R20 (recorded ownership, the
  next theme on the list).

## Pass 5 (2 November 2026): recorded ownership read at two endpoints

**Decision record:** ADR 0040 (`docs/adr/0040-ownership-endpoints-not-transfers.md`). The owner asked for the next
theme (A21).

### The check made first

The theme "recorded ownership changes read as complete ownership histories" (five findings) was taken with the two
findings on B26's unit and reach (S2 L2 R18, R20), since they concern the same outcome. Each was checked against the
lens definitions (`holder_changed`, `assignment_count`, `australian_applicant`, `filer_abn` in `variables.yaml` and
`build.py`) and both notebooks; then both notebooks and the summaries were swept for "moved", "move overseas",
"leave", "came the other way", "valued most", "captured abroad", "transfer" and "fill most of the gap".

### Findings acted on

| Finding | The audit's claim | Verified | Amendment |
|---|---|---|---|
| S1 L0-L1 R16 (High) | U17 to U19 and U35 read recorded differences as transfers and moves; the pre-FY2003 two-thirds is uncalibrated | **Confirmed**: U18 compares `founding_australian` with `australian_applicant` (two endpoints); `holder_changed` compares party ids; U19's postcode differences cannot tell a new address from a new holder; U35's 64.68% to 74.66% is measured from FY2003 only. Also found: U19's ABN range left out provisionals (1.739%) and its state figures were stale (1.589%, 0.4418% now) | U17 says what "not the filer" can mean; U18 restated in endpoint terms with what it does not show; U19's "moves" become differences and its figures corrected; U35's heading and decision say "incomplete indicator, coverage unknown" |
| S8-S9 R07 (High) | §9 carries the two-thirds into a decision; Stage 2 item 3 speaks of rights moving overseas | **Confirmed** | §9's U17/U35 row and item 3 restated; the Stage 1 summary's U18 line, rule, Stage 2 list and index rows |
| S2 L1 R25 (High) | B19 reads endpoints as the export of the most valuable rights | **Confirmed**: grant and reach do not measure what an owner valued | B19 restated in endpoint terms; "valued most" and "captured abroad" withdrawn; reach and grant noted as seen today, not before the holder changed; §1.7's heading; B46's reference to B19 removed |
| S2 L1 R26 (High) | B19's rates are not the composition of overseas-held patents | **Confirmed**: 539 of 1,219 overseas-held patents of FY2003 to FY2011 are single-office (44.22%) | A composition table in B19's cell (`5ef8906d`), with reach unknown counted (1,626 and 966 patents) |
| S2 L2 R18 (High) | B26 counts patents, not firms; intervals ignore clustering; concentration unshown | **Confirmed**: by firm, the youngest 4.34% against 3.63% (FY2003 to FY2011), 2.96% against 3.33% (FY2012 to FY2021); one firm holds 44.26% of the 5-to-10-year band's overseas-held patents in the earlier period | B26's cell (`18df0008`) adds distinct firms, the share with a patent held only overseas and the largest firm's share in each band; the text reads the firm counts as the safer ones |
| S2 L2 R19 (High) | B26's endpoints are over-interpreted; the ABN join's party alignment is unshown | **Confirmed**: 1,194 of 26,204 joined patents (4.56%) are jointly founded and in 171 the first founding applicant is not Australian (now printed) | Endpoint wording; sale of young firms and founders moving abroad kept as hypotheses; the join named |
| S2 L2 R20 (High) | "Reach does not explain the gap" is unsupported; unknown reach hidden; B55 not carried | **Confirmed** | The claim withdrawn; reach unknown shown per band (24 to 272 patents); B55's caveat carried; §2.7's and §8's rows |

### What else changed as a result

- **B26's lead weakens further**: counted by firm, the youngest firms show no clear difference in either period. The
  Stage 2 summary's "value made here is often owned or used elsewhere" line is restated in endpoint terms.
- **No lens changes.** Notebook 2 re-executed; notebook 1's changes are text only.

### Left for other passes

- **The website,** as before.
- **Overlapping themes not acted on here:** US citations read as foreign invention or use (S1 L7 R13, S8-S9 R23),
  where B46 also sits; survival read as renewal or value (the next on the list).

## Pass 6 (2 November 2026): survival read as the share still in force; one rule for the halves

**Decision record:** ADR 0041 (`docs/adr/0041-survival-as-share-in-force.md`). The owner asked for the survival pass,
with the fix to the halves, in a fresh session (A23), and decided how B8 is carried (A22). The findings are the full
Stage 2 audit's survival table (`analysis/claude-audit/261102/INDEX.md`, cited as there, the numbers shared with this
batch) and Stage 1's findings on the same theme here.

### The check made first

Every finding was checked against `build.py`, `variables.yaml`, the survival helpers and both notebooks, with
queries on the lenses, before anything changed. The checks (scratch queries; the results now on the notebooks' pages
are cited in the table):
1. **How ends are dated.** Of ended rights filed FY2000 to FY2015, 97% of standard patents' recorded ends fall 0.5 to
   0.7 of a year past an anniversary (the end of the grace period), and 95% of trade marks' (349,057) on a whole year.
2. **What `in_force IS NOT NULL` drops.** At most 6 granted rights in any cohort used in §1.2 and §1.4; the 6,621
   ended without a date are in older cohorts.
3. **Clock and cohort.** A standard patent's date of patent precedes its application date by a median 1.48 to 1.52
   years for overseas filers and organisations, 0.38 to 1.26 for Australian individuals; 48.5% to 89.0% of each
   group's patents fall in a different financial year by the two dates.
4. **Immortal time.** Of patents with an examination request (FY2003 to FY2009), 62.8% of those not expedited were
   granted more than five years after their date of patent, against 19.0% of the expedited; none can cease before
   grant (4 of 269,723 recorded as doing so).
5. **The agent's date.** IP RAPID's party records carry `effective_from_date`; for trade marks it is the registration
   date (a median 0 days from it in every cohort to FY2018), so representation can be dated before the first renewal,
   not at filing.
6. **What `exam_expedited` holds.** IP RAPID has no event for Patent Prosecution Highway requests; they are recorded as
   expedited examination (the Global PPH began on 6 January 2014; the US arrangement in April 2008).
7. **U36's cohorts.** By year, 116 innovation patents (1997 to 2000) counted as petty and 96 petty patents (2001) as
   innovation; designs filed in 2003 and to 16 June 2004 (6,280) are under the 1906 Act.

### Findings acted on

| Finding | The audit's claim | Verified | Amendment |
|---|---|---|---|
| S2 L1 R11 (High) | "In force after N years" differs by right and cohort; ended-without-date rights uncounted; cohorts by application year against a clock from the date of patent | **Confirmed** (checks 1 to 3); the rounding is harmless, as the audit said | Cohorts by the financial year the term began (`TERM_FY`), as U36; each right's dating convention stated in §1.2's introduction and in U36; the `in_force` exclusion named |
| S2 L1 R12 (High) | Survival read as renewal and value, against U36 and the glossary; immortal time before grant | **Confirmed** (check 4) | Delayed entry: each right joins at grant or registration (`univariate.kaplan_meier(entered=...)`, both notebooks); "share still in force" in headings, tables and summaries; §1.2 reconciled with U36; `GLOSSARY.md`'s "Lifetime" and "Ceased" restated, "Share still in force at N years", "Immortal time" and "Delayed entry" added |
| S2 L1 R32 (High) | The screen takes unfinished lifetimes as finished; B4's medians are not survival medians | **Confirmed** | `years_in_force` out of the screen (`screens.yaml`); B1 restated (221 distinct leads, 5,006 pairs, rho 0.867, from 223, 5,207, 0.859); B4's lifetimes from curves by cohort (a new cell, `b4curves`): designs 20.1% (class 02) to 75.9% (class 24) after 5 years; innovation patents with an ABN 56.7% against 38.6%; China's low share (21.4%) not replicated |
| S2 L1 R33 (High) | B8 carried alone, against A1; reach and citations disagree | **Confirmed**; acted on as A22 decided | A new cell (`b8reach1`): within reach bands (date of patent FY2010 to FY2016), Australian organisations 71.8% against 65.1% (two to four offices) and 75.6% against 66.5% (five or more), no difference among Australia-only patents (73.3% against 74.6%). B8, §1.9, §8 and the summary read it beside B11 and B12 and say the signals disagree |
| S2 L1 R34 (High) | Representation "at any time" includes the renewal | **Confirmed, and material**: Australian marks whose agent first appears after 9.5 years are 89.5% (99.0%) in force at 10 years | The rights lens gains `agent_first_date`; B10 reads representation before the first renewal: the attorney gap 19.1 points (15.3), not 23.4 (21.9) |
| S2 L1 R13 (Medium) | Within-field check in one period; wrong cross-references | **Confirmed** | Both periods (31 fields: Australian organisations lower in 11 and 3); B6 and B10 references replaced (section 1.1; B11) |
| S2 L1 R14 (High) | "Simpson's paradox" not shown | **Confirmed, and the claim is wrong**: with cohorts and entry corrected, expedited patents are ahead pooled in both periods (72.6% against 68.9%; 67.6% against 66.6%), and a direct standardisation gives 5.88 and 0.68 points against the pooled 3.79 and 1.03 | B13 rebuilt with the standardisation in `fd83230a`; the earlier specification kept beside it, its five-year figures showing the immortal time |
| S2 L1 R35 (Medium) | The rise in expedites may be work-sharing requests | **Confirmed in timing** (check 6): Japanese-priority patents 1.53% (2013) to 7.98% (2014), US-priority 3.07% to 6.77%; a separate 2011 and 2012 rise in every group (Australian organisations 41.26% in 2012) | A table by year of request (`b13kind1`); B13 names the kind of request as a third factor; `GLOSSARY.md` gains "Patent Prosecution Highway" |
| S2 L1 R15 (High, in part) | Missing priority counts read as none; points against a 0-to-1 threshold | **In part**: `priority_claims` is never empty for trade marks (757,895 in FY2003 to FY2015), so the `coalesce` does nothing; the threshold wording holds | B14 says "no priority claim recorded" and gives differences in percentage points, not against the screen's scale |
| S2 L1 R30 (Medium) | "Every interval is within about 1 point" | **Confirmed** | B10 gives the wider intervals of small groups |
| S2 L1 R36 (Medium) | Cohorts' longer lives read as behaviour, without the fees | **Confirmed** | B8 calls it a difference between cohorts, beside B49's dates and U35 |
| S2 L5 R04 (High) | B49's heading says one renewal change moved cessations; the bullet shows three | **Confirmed** | B49 reports all three, with checks (a window by dating, a trend baseline); only trade marks' July 1993 holds under every check (0.232 and 0.235, 0% of 66 placebos); September 2002's patent step is within the ordinary against the trend (0.189, 38.89%) |
| S2 L5 R05 (High) | "A weak lever" from a design that cannot detect a modest effect; "lapsing" for cessations | **Confirmed** | "No response beyond placebo variation, at this design's power"; the anniversaries each patent change moved are named (a table in `c5b83a0e`); "cessations" in §8 |
| S2 L5 R06 (Medium) | The window fits patents' dating only | **Confirmed** (check 1) | Months 1 to 12 for trade marks and designs, beside months 7 to 18 |
| S2 S8 R03, R05 (High) | "Renewals", "keep" and "signs of private value" carried into §8 and the summary | **Confirmed** | §8's survival rows and the Stage 2 summary's restated, each dated; the summary's headline "Value made here is often owned or used elsewhere", which its body contradicted, restated too |
| S1 L0-L1 R20 (High) | U36's cohorts mix regimes | **Confirmed** (check 7) | U36 by recorded subtype and by Act: designs from 17 June 2004 to 2009 51.8% after 5 years (the "2000s" read 64.8%); 1906-Act designs of 2000 to June 2004 apart (87.0%); innovation 35.7%, petty 68.3% |
| S1 L0-L1 R21 (High) | Survival is not a renewal rate; entry rules, denominators, rounding, the censoring date | **Confirmed** | U36 counts each right from its grant, states the dating convention, the month rounding, the censoring date and the 629 rights left out, and shows the number at risk at 10 years; patents' shares fall 1 to 4 points (2000s 71.2% to 67.5%; medians 10.6, 10.6 and 13.5) |
| S8-S9 R10 (High) | §9 and the summary present survival as renewal and value | **Confirmed** | U36's rows in §9 and the Stage 1 summary restated |
| S2 S8 R07 (High) | Two hash functions define the halves | **Confirmed** | `bivariate.half_sql` is the one rule; `split_half` computes it in DuckDB; B35's GII split uses it; a test checks that the two agree. B50, B58, B59 and B35 rerun and restated: B58's halves now hold 1,311 and 1,210 areas (B29's 1,317 and 1,211); no reading changed, though B50's patent correlation reaches 0.11 in one half. This also settles S2 L3 R02 and S2 L2 R28 |

### Found on the way, not in the audits

1. **Delayed entry needs two guards.** A trade mark registered after the record of ends closes (31 March 2026) would
   join after its own censoring, and 629 rights (616 trade marks) are recorded as ending before their own grant or
   registration; either drove a curve towards zero in the first run (trade marks of the 2000s read 0%). Entries are
   now clamped to the end, those 629 are left out, and `kaplan_meier` refuses counts with more ended than at risk.
2. **Tiny early risk sets.** With delayed entry, the first month can hold very few registered rights (22 trade marks
   of the 2010s, 3 of which ended then, which took the whole curve to 85%). Curves start once 30 are at risk, the
   minimum for any reading. A first threshold of 100 dropped small groups (the within-field check fell to 15 fields)
   and was replaced before committing.
3. **§8's table had a line break inside the B16 row,** which split the row; fixed.

### What else changed as a result

- **Readings that change:** B8 (carried only within reach, where the gap is not the narrow patents'), B10 (the
  representation gap smaller), B13 (no composition effect; a small link in both periods), B49 (one change survives
  every check, not "only patents after September 2002"), U36 (patents' shares 1 to 4 points lower). B9's order is
  less stable (rho 0.311).
- **Tests:** delayed entry by hand count, its start threshold, and the halves' agreement. Both notebooks re-executed;
  apart from the cells this pass changed, no output moved.

### Left for other passes

- **The website,** as before.
- **On the audit's list but not this theme:** S2 L5 R01 to R03 and R07 to R14, S2 S8 R01, R02, R04, R06 (in part:
  the summary's reproducibility line and B58's 11.03 were corrected here), R08 to R12, and §8's other rows (S2 S8 R03
  marks them as under review).
