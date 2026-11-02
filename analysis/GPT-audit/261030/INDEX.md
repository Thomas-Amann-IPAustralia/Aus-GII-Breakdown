# Index of the notebook audits (batch 261030)

A guide for Claude Code sessions to the twelve external audits in this folder. Each audit reviews one section of an EDA
notebook (its code, saved outputs, charts and prose) and lists prioritised findings, each with an **Issue** and an
**Action**. The folder name is the batch's start date (30 October 2026); the reviews are dated 30 October to
2 November 2026.

**Acted on so far:** see [`AMENDMENTS.md`](AMENDMENTS.md), which records each finding verified and what was changed
(pass 1, 1 November 2026: the firm filing population, ADR 0036; nine findings in five audits. Pass 2, 2 November
2026: origin is the filer's, from one party, ADR 0037; eight findings in five audits. Pass 3, 2 November 2026: later
additions carried back, ADR 0038; 25 findings in all twelve audits).

## What these audits are, and are not

- **External review input, not adopted conclusions.** They were written outside this repo's sessions (the files arrived
  as uploads) and judge the notebooks against their own stated rules (univariate in Stage 1, bivariate in Stage 2) and
  against the evidence on the page. A finding is a claim to check against the notebook, not a fact. Whether and when to
  act on them is the owner's direction (`CLAUDE.md`, working agreement).
- **Not the other "audits" in this repo.** `analysis/audit/` (`python -m audit.benchmark`), `docs/audit-ip-australia.md`
  and `docs/audit-ipa-api.md` compare the lenses with IP Australia's published figures and APIs (ADRs 0024 to 0028).
  This folder reviews the notebooks' reasoning and presentation.
- **Read-only reviews.** None of them re-executed a notebook, inspected the datasets or verified the helpers in
  `analysis/eda/`; each says so in its closing "Review boundary" section. Requested "checks" are not proven defects.

## Are they still current?

Each audit records the SHA-256 of the notebook it read. Compare before relying on one:

```bash
sha256sum analysis/notebooks/01_univariate.ipynb analysis/notebooks/02_bivariate.ipynb
```

| Notebook | SHA-256 the audits read | Audits |
|---|---|---|
| `01_univariate.ipynb` | `1d5e51a6…a357cdb` | all eight Stage 1 audits |
| `02_bivariate.ipynb` | `44167924…18ede2` (commit `1581223`) | all four Stage 2 audits |

On 1 November 2026 both notebooks still matched before the first pass of amendments; those passes changed both
(`AMENDMENTS.md`), so the hashes no longer match. If a hash differs, the notebook has changed since the audit: check
whether a finding still applies before acting on it.

## The audits

Priority is the audits' own: **High** affects interpretation, validity or downstream use; **Medium** should be
corrected before the findings are relied on or circulated.

### Stage 1 (`01_univariate.ipynb`, observations `U`)

| File | Notebook section | Observations | Findings | High / Medium | Reviewed |
|---|---|---|---|---|---|
| [`Stage01_L0-L1_Audit.md`](Stage01_L0-L1_Audit.md) | §0 (one inherited finding, R02) and §1, Lens 1: IP rights (`rights`) | U0; U1 to U21, U31 to U40, U88 to U107 | R01 to R44 | 29 / 15 | 30 Oct |
| [`Stage01_L2_Audit.md`](Stage01_L2_Audit.md) | §2, Lens 2: firms (`firms`) | U41 to U47, U112 | R45 to R70 | 16 / 10 | 31 Oct |
| [`Stage01_L3_Audit.md`](Stage01_L3_Audit.md) | §3, Lens 3: places (`regions`) | U48 to U62, U117, U118 | R01 to R32 | 18 / 14 | 31 Oct |
| [`Stage01_L4_Audit.md`](Stage01_L4_Audit.md) | §4, Lens 4: Australia and other countries (`national`) | U63 to U72, U115, U120 | R01 to R30 | 15 / 15 | 31 Oct |
| [`Stage01_L5_Audit.md`](Stage01_L5_Audit.md) | §5, Lens 5: Australia over time (`timeline`) | U22 to U30, U108 to U111, U113, U116, U123 | R01 to R32 | 14 / 18 | 31 Oct |
| [`Stage01_L6_Audit.md`](Stage01_L6_Audit.md) | §6, Lens 6: industries (`industries`) | U73 to U79, U114, U119 | R01 to R20 | 9 / 11 | 31 Oct |
| [`Stage01_L7_Audit.md`](Stage01_L7_Audit.md) | §7, Lens 7: research institutions (`institutions`) | U80 to U87, U121, U122 | R01 to R24 | 14 / 10 | 31 Oct |
| [`Stage01_S8-S9_Audit.md`](Stage01_S8-S9_Audit.md) | §8 sources outside the lenses, §9 Stage 1 summary | summary rows for all U | R01 to R25 | 19 / 6 | 1 Nov |

### Stage 2 (`02_bivariate.ipynb`, observations `B`)

| File | Notebook section | Observations | Findings | High / Medium | Reviewed |
|---|---|---|---|---|---|
| [`Stage02_L1_Audit.md`](Stage02_L1_Audit.md) | §1, Lens 1: IP rights | B1 to B19, B55 | R01 to R31 | 23 / 8 | 1 Nov |
| [`Stage02_L2_Audit.md`](Stage02_L2_Audit.md) | §2, Lens 2: firms | B20 to B26, B50, B51 | R01 to R27 | 20 / 7 | 2 Nov |
| [`Stage02_L3_Audit.md`](Stage02_L3_Audit.md) | §3, Lens 3: places | B27 to B31, B58, B59 | R01 to R33 | 24 / 9 | 2 Nov |
| [`Stage02_L4_Audit.md`](Stage02_L4_Audit.md) | §4, Lens 4: Australia and other countries | B32 to B35, B61 | R01 to R24 | 14 / 10 | 2 Nov |

Total: 348 findings (215 High, 133 Medium).

### Not yet audited

- Stage 2 §5 timeline (B36 to B39, B47 to B49, B52, B56), §6 industries (B40 to B43, B53, B54, B57, B60), §7
  institutions (B44 to B46, B62) and §8 summary of Stage 2.
- `03_multivariate.ipynb` (Stage 3), and the summaries outside the notebooks (`docs/stage-1-summary.md`,
  `docs/stage-2-summary.md`) and the evidence atlas, which every audit puts out of scope.

## How each audit is laid out

Every file follows the same template, set by `Stage01_L0-L1_Audit.md`:

1. A header: **Reviewed** (date and notebook link), **Provenance** or **Format**, **Scope of this pass** (cells, code
   cells, figures and observations covered), **Overall finding**, **Priority** and **Read first** (the findings that
   matter most; start there).
2. Thematic `##` sections, each holding findings as `### Rnn — Priority | Location: claim`, then an **Issue** paragraph
   and an **Action** paragraph.
3. A closing "Review boundary and reproducibility" section (in `Stage02_L3_Audit.md`, "Audit trail and limits") with
   the finding count, what was not checked, the commit and the notebook SHA-256.

Locators inside a finding: `§` numbers and `U`/`B` numbers are searchable in the notebook; eight-character hex strings
(for example `6491eaa5`) are the notebook JSON's stable cell `id` values, not execution counts.

To navigate without reading a whole file (they are 24 to 43 KB each):

```bash
grep -n '^## \|^### R' analysis/GPT-audit/261030/Stage01_L4_Audit.md                 # the table of contents
grep -n '^\*\*Read first' analysis/GPT-audit/261030/*.md                              # each audit's priorities
grep -n -A6 '^### R11 ' analysis/GPT-audit/261030/Stage01_L4_Audit.md                 # one finding, Issue and Action
grep -n 'U36\b' analysis/GPT-audit/261030/*.md                                        # every finding on one observation
```

### Citing a finding

R-numbers are **local to each file**, except that `Stage01_L2_Audit.md` continues from L0–L1 (R45 to R70), so `R12`
alone is ambiguous. The audits cite Stage 1 findings as "L4 R11" (lens and number); use "S1 L4 R11" or "S2 L1 R07"
when both stages are in play, and "S8–S9 R05" for the Stage 1 summary audit. `Stage02_L3_Audit.md` cites
`Stage01_L0-L1_Audit_Completed.md`, the earlier name of `Stage01_L0-L1_Audit.md` (renamed on 30 October).

## Per-audit section maps

Use these to jump to the right part of a file. Each line is a `##` section and the findings in it.

**Stage01_L0-L1** (Lens 1, rights): scope, freshness and definitions R01–R05; core rights profile R06–R14; parties,
events and lifetimes R15–R22; links, families and inventors R23–R30; register updates, inconsistencies and overlooked
observations R31–R36; additional findings R37–R44. Read first: R04, R05, R10, R17, R21, R27, R31, R33, R39; stale
conclusions R12, R32, R36.

**Stage01_L2** (Lens 2, firms): scope, freshness and definitions R45–R48; entity status, age and IP use R49–R56; R&D,
income and government contracts R57–R59; geography and WGEA R60–R66; overlooked observations and amendments R67–R70.
Read first: R47–R51, R58, R60, R62–R65.

**Stage01_L3** (Lens 3, places): scope, freshness and definitions R01–R06; core places profile and IP rates R07–R16;
attachments and geographic allocation R17–R25; later additions and completeness R26–R32. Read first: R07, R12–R15,
R18–R19, R25, R28–R30.

**Stage01_L4** (Lens 4, national): scope, coverage and definitions R01–R05; core indicators and international
comparisons R06–R13; attachments, GII and office statistics R14–R22; patent families and GII supplements R23–R28;
completeness R29–R30. Read first: R04, R06, R11, R12, R20, R23–R27; freshness R14, R28.

**Stage01_L5** (Lens 5, timeline): scope, freshness and definitions R01–R05; applications, seasonality and outcomes
R06–R13; policy windows and anomalous months R14–R20; fees, prices and later additions R21–R32. Read first: R03, R06,
R12, R14, R15, R23, R29; stale claims R02, R13.

**Stage01_L6** (Lens 6, industries): scope, freshness and definitions R01–R03; crosswalks, coverage and industry shares
R04–R09; businesses, R&D and value added R10–R14; attachments, innovation and overlooked observations R15–R20. Read
first: R02–R06, R10, R16–R17; not carried back R03, R15.

**Stage01_L7** (Lens 7, institutions): scope, coverage and definitions R01–R04; research output, linkage and grants
R05–R10; patent applications, citations and contracts R11–R15; postcode coverage R16–R18; later additions R19–R24.
Read first: R05, R12–R13, R16–R20, R22.

**Stage01_S8-S9** (sources outside the lenses, Stage 1 summary): scope, source coverage and freshness R01–R04; rights,
parties and proxy measures R05–R14; firms and places R15–R18; national, industry and institution summaries R19–R24;
policy interpretation R25. Read first: R02–R05, R12, R16–R17, R19, R21–R25. Its findings mostly restate lens findings
as they surface in §9; each names the lens finding it carries (for example "L4 R11").

**Stage02_L1** (Lens 1, rights): scope, screening and inference R01–R05; parties, representation and grant outcomes
R06–R10; survival, renewal and expedited examination R11–R15; family reach, citations, routes and inventor location
R16–R20; name-based gender estimates R21–R24; ownership endpoints and the B55 coverage amendment R25–R29; accuracy and
presentation R30–R31. Read first: R06–R09, R16–R18, R25–R29.

**Stage02_L2** (Lens 2, firms): scope, screening and definitions R01–R05; filing profiles and apparent non-filers
R06–R10; expenditure, contracts and income R11–R14; first filing, age and ownership R15–R20; WGEA addition R21–R26;
presentation R27. Read first: R04, R08–R10, R12–R13, R15–R20, R21–R26.

**Stage02_L3** (Lens 3, places): scope, samples and measurement R01–R08; core and attachment screens R09–R13;
advantage, remoteness and concentration R14–R18; business mix R19–R22; ATO income and individual filing R23–R26;
Census change R27–R30; presentation and reconciliation R31–R33. Read first: R01–R03, R05, R13–R14, R21, R23–R29. Its
closing section has a table of the Stage 1 findings it carries forward.

**Stage02_L4** (Lens 4, national): scope, populations and measurement R01–R06; core screen and Australia's relative
position R07–R11; patenting against business R&D R12–R15; attachment screen R16–R20; supplementary comparison (B61)
and reconciliation R21–R24. Read first: R07, R12–R15, R17–R18, R21–R23.

## Themes that recur across audits

The same problem often appears in several files. Fix it once, at its source, and then in every place listed. Each entry
gives the audit file (S1 or S2, then lens) and finding numbers.

| Theme | Where it is raised |
|---|---|
| Analysis goes beyond the stage's scope (relationships in Stage 1; conditional or joint models in Stage 2) | S1 L0-L1 R01; S1 L2 R45; S1 L3 R01; S1 L4 R01; S1 L5 R01; S1 L6 R01; S1 L7 R01; S8-S9 R04; S2 L1 R01; S2 L2 R01; S2 L3 R01; S2 L4 R01 |
| Later additions or corrections not carried back into earlier observations and summaries (**acted on, pass 3**) | S1 L0-L1 R12, R32, R36; S1 L2 R49, R70; S1 L3 R02, R06, R32; S1 L4 R14, R28; S1 L5 R02, R13, R32; S1 L6 R02, R03, R15; S1 L7 R21; S8-S9 R03, R21; S2 L1 R29; S2 L2 R26; S2 L3 R10, R33; S2 L4 R22, R24 |
| Current holder described as the filer; origin left undefined or taken from a different party (**acted on, pass 2**) | S1 L0-L1 R04, R39, R43; S1 L4 R12; S1 L5 R03, R09; S8-S9 R05; S2 L1 R06 |
| "Filer" or "filed IP" defined differently within a lens (**acted on, pass 1**) | S1 L2 R47; S2 L2 R04 |
| No linked filing treated as "never filed"; missing or zero treated as observed absence (**firms' filing acted on, pass 1**: S1 L2 R48, S1 L3 R15, S8-S9 R17, S2 L2 R09, S2 L3 R06; the rest open) | S1 L0-L1 R05; S1 L2 R48; S1 L3 R05, R15; S1 L4 R16; S8-S9 R17; S2 L2 R09; S2 L3 R06 |
| First observed filing treated as true entry | S1 L0-L1 R31; S1 L2 R50; S2 L2 R17 |
| Survival (years in force) read as renewal behaviour or value | S1 L0-L1 R20, R21; S8-S9 R10; S2 L1 R11, R12 |
| Recorded ownership changes read as complete ownership histories | S1 L0-L1 R16; S8-S9 R07; S2 L1 R25, R26; S2 L2 R19 |
| Attorney representation as an unvalidated proxy for help | S1 L0-L1 R15; S8-S9 R08; S2 L1 R07 |
| Expedite events described as requests | S1 L0-L1 R32; S8-S9 R09; S2 L1 R15 |
| Patent family and citation measures: units, the five-year window, reach | S1 L0-L1 R25, R26; S1 L4 R23–R26; S8-S9 R11; S2 L1 R16–R18, R27 |
| Inventor address read as place of invention | S1 L0-L1 R28; S8-S9 R13; S2 L1 R20, R22 |
| Benchmark agreement treated as validation of name-based gender estimates | S1 L0-L1 R29, R30; S8-S9 R14; S2 L1 R21 |
| Geographic allocation (postcode to area) treated as observed; area statistics read as statistics about people | S1 L3 R08, R09, R18, R19, R29; S8-S9 R18; S2 L3 R05, R28 |
| Funnel plots and "far more than chance" depend on one null model | S1 L3 R12; S8-S9 R16 |
| WGEA employers ("100 or more") and latest attributes paired with historical filing | S1 L2 R62–R65; S2 L2 R21–R24 |
| Policy timing presented as a policy response | S1 L5 R14–R16; S8-S9 R25 |
| Industry crosswalk concentration read as certainty | S1 L6 R04, R05; S8-S9 R21 |
| US citations read as evidence of foreign invention or research use | S1 L7 R13; S8-S9 R23 |
| Summed institutional credits read as distinct research output | S1 L7 R05 |
| Institutional postcodes: deduplication and what a postcode shows | S1 L7 R16–R18; S8-S9 R24 |
| GII supplementary observations used for precise rankings | S1 L4 R27; S2 L4 R21 |
| Mixed reporting years, periods or observation windows in one comparison | S1 L2 R58; S1 L4 R10, R19; S2 L2 R11; S2 L3 R04; S2 L4 R03, R18 |
| Charts and tables lose their qualifications when read alone | S1 L0-L1 R44; S1 L4 R13; S1 L6 R19; S2 L1 R31; S2 L2 R27; S2 L3 R32 |
| Promised univariate profiles left incomplete | S1 L0-L1 R41; S1 L2 R67; S1 L3 R30; S1 L4 R29; S1 L6 R20; S1 L7 R04; S8-S9 R01 |

This table is a reading aid compiled from the finding headings; open the finding before relying on it.
