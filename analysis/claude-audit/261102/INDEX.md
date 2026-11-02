# Index of the Stage 2 notebook audit (batch 261102)

An audit of all of Stage 2 (`analysis/notebooks/02_bivariate.ipynb`, §1 to §8), written by a Claude Code session on
2 November 2026 at the owner's request: review the observations ChatGPT made in its Stage 2 audits, which were written
before the notebook was amended, and continue the audit to the end of Stage 2, in the same format. The folder name is
the batch's date.

**The owner's decisions (2 November 2026):** this batch is the working list for Stage 2, in place of ChatGPT's four
Stage 2 audits, whose files stay the source of the Issue and Action text for findings marked "Holds" (A24); the
survival pass comes next, with S2 S8 R07's fix to the halves, in a fresh session (A23); and B8 stays a Stage 3 signal
only as a comparison within reach bands, read beside B11 and B12 (A22, which answers OQ24).

**Acted on (2 November 2026, pass 6, ADR 0041):** the survival theme (the 16 findings in the table below, with Stage
1's S1 L0-L1 R20, R21 and S8-S9 R10) and S2 S8 R07, which also settles S2 L3 R02 and S2 L2 R28. Each was checked
first; all hold (S2 L1 R15 in part, and S2 L1 R14's "Simpson's paradox" proved wrong, not just unshown). What was
changed, finding by finding, is in `analysis/GPT-audit/261030/AMENDMENTS.md` (pass 6), so one log holds every pass.
The notebook's SHA-256 below is the one this batch read; it has changed since.

**Acted on (2 November 2026, pass 7, ADR 0042; the owner's choice, A27):** later additions not carried back in §5 to §8
(S2 L5 R01, R13; S2 L6 R01, R06; S2 S8 R01, R06, with R02 and R04) and policy and fees (S2 L5 R02, R03, R07). All
hold. Recorded in `analysis/GPT-audit/261030/AMENDMENTS.md` (pass 7).

## What this audit is, and is not

- **A recheck and a continuation.** The ChatGPT batch (`analysis/GPT-audit/261030/`) audited §1 to §4 of this notebook
  on 1 and 2 November 2026, before passes 1 to 5 amended it (`analysis/GPT-audit/261030/AMENDMENTS.md`), and stopped
  there. This batch checks each of those 115 findings against the notebook as it now stands, and audits §5 to §8 for
  the first time. It also checks `docs/stage-2-summary.md` against the notebook, since §8 calls it "the fuller account".
- **Review input, not adopted conclusions.** A finding is a claim to check, and acting on it is the owner's direction
  (`CLAUDE.md`, working agreement). The one finding that needed the owner's decision (OQ24) has it: A22.
- **Read further than the earlier batch, but not re-run.** Besides the notebook's text, code and saved outputs, this
  audit read the helpers and definitions the notebook relies on (`analysis/eda/bivariate.py`, `univariate.py`,
  `build.py`, `variables.yaml`, `screens.yaml`, ADR 0030), which settles several of the earlier batch's
  "implementation-dependent" checks. It did not re-execute the notebook or query the lenses.
- **Not the website.** The GitHub pages and the evidence atlas (`evidence/`, `analysis/atlas/`) were not looked at; they
  are for a separate pass.

## Overall finding

The quoted numbers match the saved outputs almost everywhere; what needs correcting is what they are taken to show. Of
the earlier batch's 115 findings, the five passes resolved 20, 19 hold in part and 76 hold as written; none was wrong,
though part of one (a rounding concern) proves harmless. The sections no earlier audit covered (§5 to §8) show the same
pattern the passes corrected elsewhere: material added after Stage 2 not carried back (the fee history in B37, the
crosswalk with services in §6, the sources added after Stage 2 in §8's opening), breaks and counts that are made by the
law, the crosswalk or the arithmetic read as behaviour, and weak associations written as absences. Two findings cut
across lenses and are back-end matters: "the halves" are drawn by two different hash functions, which is why the places
lens's halves did not reconcile; and where a lens has few units, its "replication" is the same units at another time.
Survival, the next theme, needs the most work in §1: the screen treats unfinished lifetimes as finished, "in force after
N years" means different things for patents and trade marks, survival is read as renewal and as value against Stage 1's
own U36 and the owner's condition for adopting it, and renewal is compared by a representation measure that the renewal
itself can create.

## Is it still current?

Compare the notebook's SHA-256 with the one this batch read:

```bash
sha256sum analysis/notebooks/02_bivariate.ipynb
```

| Notebook | SHA-256 this batch read | Commit |
|---|---|---|
| `02_bivariate.ipynb` | `3d250d2a14a58e9b4546c01601969bbe7d14e963f46b030276abbbd01a02b7e2` | `cb54448` |

If it differs, the notebook has changed since: check a finding against the notebook before acting on it.

## The files

| File | Notebook section | Observations | Earlier findings rechecked (resolved / in part / hold) | Entries in this batch | High / Medium (new) |
|---|---|---|---|---|---|
| [`Stage02_L1_Audit.md`](Stage02_L1_Audit.md) | §1, IP rights | B1 to B19, B55 | 31 (4 / 6 / 21) | 3 restated (R09, R11, R12), 6 new (R32 to R37) | 3 / 3 |
| [`Stage02_L2_Audit.md`](Stage02_L2_Audit.md) | §2, firms | B20 to B26, B50, B51 | 27 (11 / 6 / 10) | 3 new (R28 to R30) | 0 / 3 |
| [`Stage02_L3_Audit.md`](Stage02_L3_Audit.md) | §3, places | B27 to B31, B58, B59 | 33 (2 / 3 / 28) | 1 new (R34) | 0 / 1 |
| [`Stage02_L4_Audit.md`](Stage02_L4_Audit.md) | §4, Australia and other countries | B32 to B35, B61 | 24 (3 / 4 / 17) | 1 new (R25) | 0 / 1 |
| [`Stage02_L5_Audit.md`](Stage02_L5_Audit.md) | §5, Australia over time | B36 to B39, B47 to B49, B52, B56 | none | 14 (R01 to R14) | 9 / 5 |
| [`Stage02_L6_Audit.md`](Stage02_L6_Audit.md) | §6, industries | B40 to B43, B53, B54, B57, B60 | none | 9 (R01 to R09) | 5 / 4 |
| [`Stage02_L7_Audit.md`](Stage02_L7_Audit.md) | §7, research institutions | B44 to B46, B62 | none | 6 (R01 to R06) | 3 / 3 |
| [`Stage02_S8_Audit.md`](Stage02_S8_Audit.md) | §8, the method across lenses, `docs/stage-2-summary.md` | all | none | 12 (R01 to R12) | 6 / 6 |

**Totals.** Earlier findings: 115, of which 20 resolved, 19 holding in part and 76 holding. New findings: 52 (26 High,
26 Medium), plus 3 earlier findings restated with new evidence. Open now: 147 (95 earlier, in full or in part, and 52
new).

## Read first

1. **S2 S8 R07, two hash functions.** A back-end inconsistency, and the cause of S2 L3 R02 and S2 L2 R28: one fix
   corrects the halves of B50, B58, B59 and B35's GII split.
2. **The survival theme, next on the owner's list** (the cluster below), starting with S2 L1 R33 (decided: A22), R12, R32, R11
   and R34.
3. **Later additions not carried back** in the sections no earlier audit covered: S2 L5 R01, S2 L6 R01, S2 S8 R01 and
   R06.
4. **Policy and fees, for Q5:** S2 L5 R02, R03 and R05.
5. **What a count measures:** S2 L6 R02 (counts allocated by a crosswalk), S2 L7 R01 (US citations), S2 L6 R04 and
   S2 L7 R02 (ratios on a shared denominator).
6. **What Stage 3 will read:** S2 S8 R01 to R03 and R05.

## The survival theme in one place

Every finding in this batch that the survival pass (survival, or years in force, read as renewal behaviour or value)
should take, with the Stage 1 findings in the earlier batch that belong to the same theme.

| Finding | Priority | Observation | What it says |
|---|---|---|---|
| S2 L1 R11 | High | §1.2, §1.4 | What "in force after N years" measures: eligibility (`in_force`), ends without dates left out, patents' ends dated at the end of grace but trade marks' at the anniversary, the harmless rounding, and cohorts by application year against a clock from the date of patent |
| S2 L1 R12 | High | §1.2, B8, B10, B14, §1.9 | Survival read as renewal and as value, against U36 ("not value") and the glossary; immortal time before grant |
| S2 L1 R32 | High | B4 | The screen treats unfinished lifetimes as finished; B4's medians are not survival medians |
| S2 L1 R33 | High | B8, §8, summary | Survival carried alone, against A1's condition; reach and citations point the other way. Decided (A22): keep B8 only within reach bands, beside B11 and B12 |
| S2 L1 R34 | High | B10 | Representation "at any time" includes the renewal |
| S2 L1 R14 | High | B13 | "Simpson's paradox" not shown |
| S2 L1 R15 | High (in part) | B14 | Expedite meaning, missing priority counts, points against a 0-to-1 threshold |
| S2 L1 R13 | Medium | B8, B9 | Within fields in one period; wrong cross-references |
| S2 L1 R30 | Medium | B10 | "Every interval is within about 1 point" |
| S2 L1 R35 | Medium | B13 | The rise in expedites may be work-sharing requests (the Patent Prosecution Highway), not urgency |
| S2 L1 R36 | Medium | B8 | Cohorts' longer lives read without the fee changes |
| S2 L5 R04 | High | B49 | The heading says one renewal change moved cessations; the bullet shows three |
| S2 L5 R05 | High | B49, §8 | "A weak lever" from a design that could not detect a modest effect; "lapsing" for cessations |
| S2 L5 R06 | Medium | B49 | The window fits patents' dating, not trade marks' or designs' |
| S2 S8 R03, R05 | High | §8, summary | "Renewals", "keep" and "signs of private value" carried into the summaries |
| S1 L0-L1 R20, R21; S8-S9 R10 | (earlier batch) | Stage 1 | The same theme in Stage 1; not rechecked here |

`GLOSSARY.md`'s "Lifetime (years in force)" entry, which calls a lifetime a judgement of the right's worth, is part of
the same wording (S2 L1 R12).

## Themes that recur in this batch

| Theme | Where raised |
|---|---|
| Later additions or corrections not carried back (pass 3's theme, recurring in §5, §6 and §8) | S2 L5 R01, R13; S2 L6 R01, R06; S2 S8 R01, R06 |
| Survival read as renewal or value | the table above |
| Mechanics or arithmetic read as behaviour: breaks the law makes certain, shared denominators, allocation by crosswalk, funding rules, representation over a right's life | S2 L5 R02; S2 L3 R07, S2 L4 R05, S2 L6 R04, S2 L7 R02; S2 L6 R02; S2 L7 R03; S2 L1 R07, R34 |
| Second samples that are not independent | S2 S8 R08; S2 L4 R25; S2 L6 R03; S2 L7 R03; S2 L1 R03; S2 L2 R03; S2 L3 R03 |
| Halves drawn two ways | S2 S8 R07; S2 L3 R02; S2 L2 R28 |
| Absence read from weak or non-significant associations | S2 S8 R12; S2 L5 R08, R09, R11; S2 L6 R05; S2 L7 R05; S2 L3 R27; S2 L4 R13 |
| Dependence ignored in intervals (serial, clustered, two pairs per change) | S2 S8 R09; S2 L5 R07, R08 |
| US citations read as foreign use | S2 L7 R01 (S1 L7 R13 and S8-S9 R23 in the earlier batch) |
| Inventor address read as place of invention | S2 L1 R20; S2 S8 R03 |
| Attorney representation as an unvalidated proxy | S2 L1 R07, R34 |
| Charts and tables lose their qualifications | S2 S8 R11; S2 L1 R31; S2 L2 R27; S2 L3 R32; S2 L4 R09; S2 L5 R03; S2 L6 R09 |

## How the files are laid out

The template of the earlier batch (`analysis/GPT-audit/261030/INDEX.md`, "How each audit is laid out"), with two
differences:

1. A bar replaces the dash after a finding's number: `### R12 | High | §1.2, B8: claim`, then **Issue** and **Action**.
   The earlier batch's search commands still work.
2. The rechecked files (L1 to L4) open with a status table of every earlier finding: "Resolved (pass N)", "Holds in
   part" (with what changed) or "Holds" (the earlier Issue and Action apply as written). Full entries follow only for
   earlier findings restated with new evidence ("carried, sharpened") and for new findings.

Each file closes with its review boundary, the commit and the notebook's SHA-256.

### Citing a finding

Cite as "S2 L5 R03", and "S2 S8 R07" for the summary and method file. In L1 to L4 the earlier batch's numbers are kept,
so "S2 L1 R12" is the same finding in both batches, and this batch's file holds its current status; new findings
continue the numbering (L1 from R32, L2 from R28, L3 at R34, L4 at R25). L5 to L7 and S8 have no counterpart in the
earlier batch.

```bash
grep -n '^## \|^### R' analysis/claude-audit/261102/Stage02_L5_Audit.md        # a file's table of contents
grep -n '^\*\*Read first' analysis/claude-audit/261102/*.md                     # each file's priorities
grep -n -A8 '^### R03 ' analysis/claude-audit/261102/Stage02_L5_Audit.md        # one finding, Issue and Action
grep -n '^| R12 ' analysis/claude-audit/261102/Stage02_L1_Audit.md              # an earlier finding's status now
grep -n 'B49' analysis/claude-audit/261102/*.md                                 # every finding on one observation
```
