# Stage 2 notebook audit: Lens 3, places (rechecked and continued)

**Reviewed:** 2 November 2026, by a Claude Code session at the owner's request. **Source:**
`analysis/notebooks/02_bivariate.ipynb` as committed at `cb54448` (SHA-256 in full below), read in the repository. The
GitHub web pages and the evidence atlas were not looked at.

**Provenance:** Rechecks `analysis/GPT-audit/261030/Stage02_L3_Audit.md` (ChatGPT, 2 November 2026, R01 to R33), which
read the notebook before the amendments, and continues it. The earlier findings keep their numbers; the new finding is
R34. Format as in that batch, with a bar in place of the dash after each finding's number.

**Scope of this pass:** §3, §3.0 to §3.7 (B27 to B31, B58, B59): all 24 cells and the 9 code cells (execution counts 36
to 44) with their saved outputs; the 2 figures were judged from their code. Every earlier finding was checked against
the notebook as it now stands. The helpers that draw the halves (`bivariate.screen_sample`, `bivariate.split_half`) were
read to find the cause of the earlier audit's R02. Nothing was re-executed.

**Overall finding:** Passes 1 and 3 resolved 2 of the earlier audit's 33 findings ("never filed" and the five-source
inventory) and part of 3 more (B29's SA3 heading, the verdict counts beside 0.962, and several rows of §3.7); 28 hold as
written. The earlier audit's inconsistent halves now have a cause: two different hash functions draw "the lens's
halves" (S2 S8 R07). The rest of what holds is interpretation: shared denominators, a single gradient, the model's
adequacy, the largest-filer check, business mix, the ATO denominator and the Census changes. One new finding: B30's
largest filer and the postcode that places a patent can be different parties.

**Priority:** **High** = affects interpretation, validity or downstream use; **Medium** = correct before relying on or
circulating the findings. Apply corrections to §3.7, §8 and `docs/stage-2-summary.md` as well as to the observation.

**Read first:** R02 (now with its cause), R07, R13, R18, R20 and R21, R26 and R27.

## The earlier audit's findings, checked again

"Holds" means the earlier finding's Issue and Action still apply as written (read them in the earlier file); "holds in
part" says what has changed.

| Finding | Priority | Status now | What the notebook shows now |
|---|---|---|---|
| R01 | High | Holds | B29's joint model (IRSAD with remoteness) is still presented as a Stage 2 pair (framing). `f80eb1ec`, `8175d81b` |
| R02 | High | Holds; cause found | Two hash functions: B27's screen halves 1,377 and 1,264 (DuckDB, `screen_sample`); B29 and B30 fit 1,317 and 1,211 areas (DuckDB, in SQL); B58 has 1,256 and 1,265 and B59 891 and 898 (pandas, `split_half`). See S2 S8 R07. `1cb83215`, `f80eb1ec`, `348901fd`, `ecc34934`, `b7179e5a` |
| R03 | High | Holds | Neighbouring areas still fall in both halves; intervals ignore spatial dependence. `1ca091d5`, `f80eb1ec` |
| R04 | High | Holds | FY2017 to FY2026 filings against a 2021 population, an active-ABN snapshot, 2023-24 tax records and June 2025 CABEE. `1ca091d5`, `ecc34934` |
| R05 | High | Holds | Unmatched postcodes and SA3 pooling are not tested; registered addresses stand for places. `1ca091d5`, `f80eb1ec` |
| R06 | High | Resolved (pass 1) | "No filing linked", restated with the re-run. `bd7702fc` |
| R07 | High | Holds | The strongest pair is still two rates on one denominator: firms with a filing linked and R&D claimants per 1,000 businesses (0.879; 0.894). `1cb83215`, `bd7702fc` |
| R08 | Medium | Holds | Samples differ by analysis (431 and 1,074 areas in discovery; 2,528 in B29; B58's and B59's filters). |
| R09 | Medium | Holds in part | B27 now gives the verdict counts beside 0.962, but still calls 0.962 the halves' agreement without saying it is a rank correlation of pair strengths. `bd7702fc` |
| R10 | Medium | Resolved (pass 3) | §3.1 names the original five-source screen and its exclusions. `5cc45503` |
| R11 | Medium | Holds | Counts per 1,000 residents are still called "a share of the whole population"; land area is divided like a count. `5cc45503`, `0a576241` |
| R12 | Medium | Holds | `BEST` still picks the period with the most rows, ties by lexical order. `0a576241` |
| R13 | High | Holds | "The attachments describe one dimension of places" remains, with no component analysis shown. `47c98879` |
| R14 | High | Holds in part (pass 3) | The heading now says the joint model was not fitted on SA3s; "falls with remoteness" still implies a steady decline (standard patents: inner regional 0.259, outer 0.289, remote 0.338, very remote 0.173). `8175d81b` |
| R15 | High | Holds | "All fits converged" with warnings suppressed and no diagnostics. `f80eb1ec` |
| R16 | Medium | Holds | "Most of the gradient is in the most advantaged fifth" and the city-centre explanation remain; trade marks fall from decile 9 to 10 in discovery (31.6 to 29.24). `9ea0a1c6`, `8175d81b` |
| R17 | High | Holds | The decile chart's bars are still Poisson intervals on pooled counts. `9ea0a1c6` |
| R18 | High | Holds | "The advantage gradient is not one firm's" and "add noise to areas' counts, not the gradient" remain; "holds" for filed. `8f0bb876` |
| R19 | High | Holds | CABEE's industry shares against filing per ABR business. `c3c0b719` |
| R20 | High | Holds | B31's heading generalises standard patents' pattern to "files more"; "manufacturing's share makes no difference" remains in the heading (the bullet says "no consistent link"). `c3a6cba9` |
| R21 | High | Holds | "Patents are filed by manufacturers (U75) ... a firm's head office ... sits among the services of the city centres" remains. `c3a6cba9` |
| R22 | Medium | Holds | Shares that sum to one, read one at a time. `c3c0b719` |
| R23 | High | Holds | Individuals with business income still stand for "each person who runs a business". `ecc34934`, `539d13ec` |
| R24 | High | Holds | Individuals' filing is still total minus organisations. `ecc34934` |
| R25 | Medium | Holds | Three rights pooled; unweighted medians by decile. `ecc34934` |
| R26 | High | Holds | "The advantage gradient is not only more business owners"; "the denominator does not explain B29's gradient away". `539d13ec` |
| R27 | High | Holds | "Areas that gained graduates or income did not gain filing"; "an area's rising education or income does not lift its filing". `926d52ec` |
| R28 | High | Holds | Historical SA2 values allocated by 2021 weights. `b7179e5a` |
| R29 | High | Holds | The pseudocount; "its residents' standard patents per 10,000 people fell (-0.145 in logs)". `b7179e5a`, `926d52ec` |
| R30 | Medium | Holds | "The median area's share ... rose 5.9 points, its median income 0.332 ...". `926d52ec` |
| R31 | High | Holds | B31, B58 and B59 still have no intervals. `c3c0b719`, `ecc34934`, `b7179e5a` |
| R32 | Medium | Holds | B28 still names finance at 0.575 first, not the top row (finance, $200,000 to $2 million turnover, 0.595; 0.621); the Parenting Payment row; "healthier"; the heatmap key (S2 S8 R11). `b259f002`, `47c98879` |
| R33 | High | Holds in part (pass 3) | §3.7's B29, B31, B58 and B59 rows were restated and a note added on levels against changes; "on one gradient" (B28), "Rule: the gradient is not one firm's" (B30) and the business-owner denominator (B58) remain. `a9f5687a` |

## New finding

### R34 | Medium | B30: the largest filer and the postcode that places a patent can be different parties

**Issue:** B30 places each patent by `founder_postcode` and identifies its filer by `filer_abn`, the first founding
applicant with an ABN (ADR 0016), which for a jointly founded patent need not be the party whose postcode places it.
Pass 2 aligned the regions lens's organisation counts to the party that gives the postcode, and pass 5 found that 4.56%
of the patents B26 joins to firms are jointly founded. B30's own query was not aligned.

**Action:** Take the filer from the party that gives the postcode, as the lens now does, or count the jointly founded
patents affected. Evidence: `348901fd`; `analysis/GPT-audit/261030/AMENDMENTS.md` (passes 2 and 5).

## Review boundary and reproducibility

This file holds the status of the earlier audit's **33 findings** (2 resolved, 3 holding in part, 28 holding) and **1 new
issue/action entry** (R34, Medium). It reviews §3's text, code and saved outputs and the helpers named above; it did not
re-execute the notebook, refit the models or query the lenses. All 9 code cells have saved outputs, execution counts 36
to 44 in order, and no saved errors. No notebook, code or website files were changed.

**Evidence locators:** B-numbers and section headings are searchable; eight-character identifiers are the notebook
JSON's stable cell `id` values. The earlier ChatGPT findings keep their numbers, so "S2 L3 R02" is the same finding in
both batches.

Repository commit: `cb544481aa64830e95c1ecd64260454baef41ed5`.

Reviewed notebook SHA-256: `3d250d2a14a58e9b4546c01601969bbe7d14e963f46b030276abbbd01a02b7e2`.
