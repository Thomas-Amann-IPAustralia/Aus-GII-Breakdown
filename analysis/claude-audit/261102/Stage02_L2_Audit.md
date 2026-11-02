# Stage 2 notebook audit: Lens 2, firms (rechecked and continued)

**Reviewed:** 2 November 2026, by a Claude Code session at the owner's request. **Source:**
`analysis/notebooks/02_bivariate.ipynb` as committed at `cb54448` (SHA-256 in full below), read in the repository. The
GitHub web pages and the evidence atlas were not looked at.

**Provenance:** Rechecks `analysis/GPT-audit/261030/Stage02_L2_Audit.md` (ChatGPT, 2 November 2026, R01 to R27), which
read the notebook before the amendments, and continues it. The earlier findings keep their numbers; new findings are
numbered from R28. Format as in that batch, with a bar in place of the dash after each finding's number.

**Scope of this pass:** §2, §2.0 to §2.7 (B20 to B26, B50, B51): all 27 cells and the 12 code cells (execution counts 24
to 35) with their saved outputs; the 3 figures were judged from their code. Every earlier finding was checked against the
notebook as it now stands, beside passes 1, 3, 4 and 5, which changed this section most. Read beside it: the firms lens's
definitions (`variables.yaml`: `austender_value`, `ip_record`, `age_truncated`), `bivariate.split_half` and ADR 0039.
Nothing was re-executed.

**Overall finding:** The passes resolved 11 of the earlier audit's 27 findings, including all those on the filing flag,
apparent non-filers, firms' age and recorded ownership; 6 hold in part and 10 hold as written. What remains open is
mostly interpretation: contract totals read as contract sizes (now confirmed from the variable's definition),
"within every kind of entity", the WGEA population and its latest attributes, and the size check that changes B23's
measure. Three new findings: B50's "halves" are not the lens's halves, B25's within-firm order is read within a window
that selects pairs filed close together, and B26's heading still leans on the patent-level rate that pass 5 judged the
weaker reading.

**Priority:** **High** = affects interpretation, validity or downstream use; **Medium** = correct before relying on or
circulating the findings. Apply corrections to §2.7, §8 and `docs/stage-2-summary.md` as well as to the observation.

**Read first:** R12 and R13 (contracts), R21 to R24 (WGEA), R11 (windows), then R28 to R30.

## The earlier audit's findings, checked again

"Holds" means the earlier finding's Issue and Action still apply as written (read them in the earlier file); "holds in
part" says what has changed.

| Finding | Priority | Status now | What the notebook shows now |
|---|---|---|---|
| R01 | High | Holds | B24 within entity groups and B51 within size bands are still not called stratified checks (framing, as pass 1 judged). `162ee072`, `6880dc9f` |
| R02 | High | Holds | As S2 L1 R02; B24 also applies "negligible" and "lead" to rank-biserial correlations. `e82d4b3e` |
| R03 | Medium | Holds in part | B20 now says random halves are a weaker test, but its heading still says "the two halves agree almost exactly", and usable counts per pair are not shown. `2acf090e` |
| R04 | High | Holds in part | One flag, `ip_record`, now defines filing in B22 to B24 and B50 (pass 1); §2's opening rule still calls firms' IP counts "lower bounds (50,790 ABNs only IPLORD links to IP have counts of 0, U41)", wording passes 1 and 4 qualified elsewhere. `44597b98` |
| R05 | Medium | Holds | B21 still reads "larger firms", "firms that hold patents also hold designs" (applicant-or-owner flags) and "suppliers cluster in the ACT"; several pairs it says are "followed up below" are not. `2acf090e` |
| R06 | High | Resolved (pass 4) | Undated firms are their own age group. `dff03f5c` |
| R07 | Medium | Holds | "Rises steadily" (20.2%, 23.1%, 19.8%, 19.4% ... 27.14%); "once a firm does R&D, where it is registered does not go with filing", beside claimants in outer regional areas 39.3% against major cities 51.9% (discovery); firm size as a fact. `dff03f5c`, `1d5add86` |
| R08 | High | Resolved (pass 1) | The IPLORD share uses the right denominator. `5db69f06`, `472585cd` |
| R09 | High | Resolved (pass 1) | "No filing linked"; "close to exact" withdrawn. `472585cd` |
| R10 | High | Resolved (pass 1) | A joint table of entity group by age. `5db69f06` |
| R11 | High | Holds | Unaligned windows; B23's 17,514 claimants with a positive mean spend against B22's 17,643 active claimants, the 129 still unexplained. `c9f6c794`, `472585cd` |
| R12 | High | Holds; confirmed | `austender_value` is "the sum of the contracts' values at their latest notice" for each firm (`variables.yaml`), so "a median contract value of $273,400 against $113,800" is a median of firms' totals; "win more and larger contracts" remains in B24, §2.7 and §8. `d25160cd`, `e82d4b3e` |
| R13 | High | Holds | "Within every kind of entity" remains, for value only, in five groups, with trusts at 0.044 and 0.065. `162ee072`, `e82d4b3e` |
| R14 | Medium | Holds in part | B24 gives the replication interval (-$8.3m to $19.5m) but not discovery's ($13.38m to $45.04m); §2.7 still leaves the income comparison out. `d25160cd`, `67eaba22` |
| R15 | High | Resolved (pass 4) | The sample is named "not truncated", with a from-2001 sensitivity check. `3f4b06bf`, `18df0008` |
| R16 | High | Resolved (pass 4) | Ages from dates; a density axis. `3f4b06bf`, `18df0008` |
| R17 | High | Resolved (pass 4) | First observed linked filing; a within-firm order (one residual: R29). `8926adb5` |
| R18 | High | Resolved (pass 5) | Firm-level counts and each band's largest firm. `18df0008` |
| R19 | High | Resolved (pass 5) | Endpoint wording; the join's party alignment printed (1,194 of 26,204 jointly founded; 171 with a first founder not Australian). `ec3ec3a0` |
| R20 | High | Resolved (pass 5) | "Reach is not ruled out"; unknown reach shown. `ec3ec3a0` |
| R21 | High | Holds in part | B51 notes 683 reporters under 100 employees; §2.6's title, B50's heading and §8 still say "employers of 100 or more", and the query still selects `wgea_year IS NOT NULL`. `00f6b33d`, `9f01d1f9`, `efb8d829` |
| R22 | High | Holds | Latest WGEA attributes are still set against all historical filing. `9f01d1f9`, `efb8d829` |
| R23 | High | Holds | "Industry sorts patenting far more than size does" remains in B51 and the summary. `efb8d829` |
| R24 | High | Holds | B51 still checks B23 with the latest spend among WGEA claimants, without B23's filters, and concludes "the weak link holds within size". `6880dc9f`, `efb8d829` |
| R25 | Medium | Holds in part | B50 now says the headcount correlations are under 0.1; §2.7 still puts "within bands" and "halves (weak as rho)" in the replication column; the five bands hold 7,120 of the 7,126 firms. B50's halves are not §2's (R28). `9f01d1f9`, `67eaba22` |
| R26 | Medium | Resolved (pass 3) | Size and industry stated as available for WGEA reporters only. `2acf090e`, `efb8d829`, `67eaba22` |
| R27 | Medium | Holds in part | B25's histogram now pools 25 years and more in its axis label, and B23's figure says "no filing linked"; lead details still truncate, B23's figure caption still omits IP Australia's register, and the heatmap lacks a key (S2 S8 R11). `c9f6c794`, `3f4b06bf` |

## New findings

### R28 | Medium | B50: "the two halves of the lens" are not §2's halves

**Issue:** B50 splits the WGEA firms with `bi.split_half` (pandas' hash of the ABN) and calls them "the two halves of the
lens (the replication rule of section 2)". §2's screen and B22 to B24 split by DuckDB's hash of the ABN. The two
functions put different firms in each half (S2 S8 R07), so B50's halves are a different random split from the one the
rest of §2 uses.

**Action:** Use §2's split in B50, or say that it is a different random split. Evidence: `9f01d1f9`, `dff03f5c`;
`bivariate.split_half`, `bivariate.screen_sample`.

### R29 | Medium | B25: the within-firm order is read among firms whose two first filings both fall in the window

**Issue:** "72.86% filed the trade mark first" is among the 4,550 firms whose first observed linked trade mark and first
standard patent were both filed FY2010 to FY2026. Firms whose first trade mark came before FY2010 and first patent
after (trade mark first), firms with a patent before FY2010, and firms whose second kind has not yet come are left out,
so the share depends on the window, and pairs filed close together are over-represented.

**Action:** State the condition beside the share; show the share among firms with both first filings at any date, and
the number of firms with only one of them. Evidence: `3f4b06bf`, `8926adb5`.

### R30 | Medium | B26: the heading still leans on the patent-level rate

**Issue:** B26's heading says patents now held only overseas are "a little more common among the youngest firms' in
FY2003 to FY2011". Its text says the firm counts are "the safer reading", and by firm the youngest are 4.34% (of 346
firms) against 3.63% (of 1,186) for firms 10 years or more, with no interval; pass 5 concluded there is no clear
difference by firm, and §2.7 and §8 say so.

**Action:** Head B26 by the firm-level comparison, with an interval for it. Evidence: `18df0008`, `ec3ec3a0`,
`67eaba22`.

## Review boundary and reproducibility

This file holds the status of the earlier audit's **27 findings** (11 resolved, 6 holding in part, 10 holding) and **3
new issue/action entries** (R28 to R30, all Medium). It reviews §2's text, code and saved outputs and the definitions and
helpers named above; it did not re-execute the notebook or query the lenses. All 12 code cells have saved outputs,
execution counts 24 to 35 in order, and no saved errors. No notebook, code or website files were changed.

**Evidence locators:** B-numbers and section headings are searchable; eight-character identifiers are the notebook
JSON's stable cell `id` values. The earlier ChatGPT findings keep their numbers, so "S2 L2 R12" is the same finding in
both batches.

Repository commit: `cb544481aa64830e95c1ecd64260454baef41ed5`.

Reviewed notebook SHA-256: `3d250d2a14a58e9b4546c01601969bbe7d14e963f46b030276abbbd01a02b7e2`.
