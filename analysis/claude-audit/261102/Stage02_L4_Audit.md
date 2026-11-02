# Stage 2 notebook audit: Lens 4, Australia and other countries (rechecked and continued)

**Reviewed:** 2 November 2026, by a Claude Code session at the owner's request. **Source:**
`analysis/notebooks/02_bivariate.ipynb` as committed at `cb54448` (SHA-256 in full below), read in the repository. The
GitHub web pages and the evidence atlas were not looked at.

**Provenance:** Rechecks `analysis/GPT-audit/261030/Stage02_L4_Audit.md` (ChatGPT, 2 November 2026, R01 to R24), which
read the notebook before the amendments, and continues it. The earlier findings keep their numbers; the new finding is
R25. Format as in that batch, with a bar in place of the dash after each finding's number.

**Scope of this pass:** §4, §4.0 to §4.5 (B32 to B35, B61): all 16 cells and the 5 code cells (execution counts 45 to 49)
with their saved outputs; the 2 figures were judged from their code. Every earlier finding was checked against the
notebook as it now stands. Nothing was re-executed.

**Overall finding:** Pass 3 resolved 3 of the earlier audit's 24 findings (B61's claim that B34's gap holds, its
"interval" as replication, and §4.5's strengthened summary) and part of 4 more; 17 hold as written. Unchanged and still
High: business R&D said to be measured "for OECD members only", unscaled attachment totals, the GII edition set against
2016 to 2020, B34's reading of a weak change correlation as an intervention result, and its attribution of Australia's
changed position to falling R&D alone. One new finding: the second period is the same countries a decade earlier.

**Priority:** **High** = affects interpretation, validity or downstream use; **Medium** = correct before relying on or
circulating the findings. Apply corrections to §4.5, §8 and `docs/stage-2-summary.md` as well as to the observation.

**Read first:** R07, R12 to R15, R17, R18, R21.

## The earlier audit's findings, checked again

"Holds" means the earlier finding's Issue and Action still apply as written (read them in the earlier file); "holds in
part" says what has changed.

| Finding | Priority | Status now | What the notebook shows now |
|---|---|---|---|
| R01 | High | Holds in part (pass 3) | §4.5 now says "a development gradient in rank correlations"; B32 still says "as one development gradient", "Nothing about IP is unrelated to development" and "trade marks follow commerce, patents follow research". `f6a82fbe`, `6fccbbc5` |
| R02 | High | Holds | The core keeps countries of a million people or more; B61 uses the OECD flag without that rule; membership comes from `bool_or(oecd)`. `56ed2b2a`, `9702b2e1` |
| R03 | High | Holds | Each indicator is still averaged over whatever years it has. `56ed2b2a` |
| R04 | Medium | Holds in part | B61 now takes each economy's latest year explicitly (`QUALIFY year = max(year) ...`); other checks are still not shown. `9702b2e1` |
| R05 | High | Holds | Shared population denominators and mixed scalings. `56ed2b2a`, `a2d420b8` |
| R06 | Medium | Holds | `nlab` still labels transformed values by their source units ("journal articles", "High-technology exports (current US$)", "New businesses registered (number)"). `56ed2b2a`, `6be88b85` |
| R07 | High | Holds | "Business R&D is measured for OECD members only" remains. `f6a82fbe` |
| R08 | Medium | Holds | The 134-row lead table still prints with an ellipsis; the focus table has no pair counts or intervals. `56ed2b2a` |
| R09 | Medium | Holds | The heatmap's scale stops at 0.6 and its symbols have no key (S2 S8 R11). `56ed2b2a` |
| R10 | Medium | Holds | B33 still says "top for business entry, trade marks and research articles" and "near the bottom for ... exports" (high-technology exports' share of manufactured exports: 9th of 36). `4a741ad9` |
| R11 | Medium | Holds in part (pass 3) | "Now" is gone from §4.5; B33's missing researchers and technicians in 2016 to 2020 are still unexplained. `6be88b85`, `6fccbbc5` |
| R12 | High | Holds | §4.2 is still headed "Invention against R&D"; "23 members' residents filed less" is per person. `ee18f43f`, `c510ff8c` |
| R13 | High | Holds | "Raising R&D would not, on this evidence, raise patenting quickly" remains, from a change correlation of 0.165 with no interval. `c510ff8c` |
| R14 | High | Holds | "Its change in position came from falling R&D (B33), not rising patenting" remains. `c510ff8c` |
| R15 | High | Holds | Australia is still in the fit it is judged against; prediction intervals are read as members' ranges. `a2d420b8`, `c510ff8c` |
| R16 | Medium | Holds | §4.3 is still headed "every cross-country indicator". `c0ecdc77` |
| R17 | High | Holds | Attachment totals are still unscaled (venture capital in US dollars; BERD in PPP dollars). `9fae40b0`, `4e8a6b09` |
| R18 | High | Holds | The GII 2026 edition is still set against 2016 to 2020 patenting. `9fae40b0` |
| R19 | Medium | Holds | Patent-labelled indicators are still dropped after the correction, by the substring "atent"; the 225 leads are not distinct. `9fae40b0` |
| R20 | High | Holds in part | B35 now calls it "a third-factor pattern to test", but still asserts that "business research employs fewer women". `4e8a6b09` |
| R21 | High | Holds | B61 still gives ranks without the values, periods and caveats, and truncates average ranks with `int`. `9702b2e1`, `06b4368b` |
| R22 | High | Resolved (pass 3) | B61 is "Not a replication of B34". `06b4368b` |
| R23 | Medium | Resolved (pass 3) | §4.5 says "interval only, one period". `6fccbbc5` |
| R24 | Medium | Resolved (pass 3) | §4.5 regenerated; measured and proposed third factors split. `6fccbbc5` |

## New finding

### R25 | Medium | B32 to B35, §4.5: the second period is the same countries a decade earlier

**Issue:** B32's heading says the gradient "holds over a decade", and §4.5's column records "yes (2006 to 2010)". The
two samples are the same countries ten years apart (160 and 159), whose development, institutions and statistical
systems persist, so agreement is expected whatever the relationship (S2 S8 R08). Only B35's GII halves split the
countries.

**Action:** Call the second period a stability check across a decade, not a replication. Evidence: `56ed2b2a`,
`f6a82fbe`, `6fccbbc5`.

## Review boundary and reproducibility

This file holds the status of the earlier audit's **24 findings** (3 resolved, 4 holding in part, 17 holding) and **1 new
issue/action entry** (R25, Medium). It reviews §4's text, code and saved outputs; it did not re-execute the notebook,
refit the models or query the lenses. All 5 code cells have saved outputs, execution counts 45 to 49 in order, and no
saved errors. No notebook, code or website files were changed.

**Evidence locators:** B-numbers and section headings are searchable; eight-character identifiers are the notebook
JSON's stable cell `id` values. The earlier ChatGPT findings keep their numbers, so "S2 L4 R13" is the same finding in
both batches.

Repository commit: `cb544481aa64830e95c1ecd64260454baef41ed5`.

Reviewed notebook SHA-256: `3d250d2a14a58e9b4546c01601969bbe7d14e963f46b030276abbbd01a02b7e2`.
