# Stage 2 notebook audit: §8 summary, the method across lenses, and the Stage 2 summary document

**Reviewed:** 2 November 2026, by a Claude Code session at the owner's request. **Source:**
`analysis/notebooks/02_bivariate.ipynb` as committed at `cb54448` (SHA-256 in full below) and `docs/stage-2-summary.md`
at the same commit, read in the repository. The GitHub web pages and the evidence atlas were not looked at.

**Provenance:** The first audit of §8. Format as in `analysis/GPT-audit/261030/` (compare `Stage01_S8-S9_Audit.md` for
Stage 1's summary), with a bar in place of the dash after each finding's number. R-numbers are local to this report.

**Scope of this pass:** §8 (one cell, `de334709`); the notebook's front matter (`b29e8754`, `0a9fee61`); the lens
summaries (§1.9, §2.7, §3.7, §4.5, §5.7, §6.7, §7.4) as they feed §8; `docs/stage-2-summary.md`, which §8 calls "the
fuller account", checked line by line against the notebook; and the helpers behind the claims that cut across lenses
(`analysis/eda/bivariate.py`: `association`, `strength_interval`, `leads_table`, `split_half`, `screen_sample`,
`strength_map`), with ADR 0030. The method findings here apply to every lens file in this batch.

**Overall finding:** §8 and the summary document are where Stage 3 will be planned from, and both lag the notebook.
§8's opening says every lens and companion table was screened, which is not true of the sources added after Stage 2; its
signal table leaves out two carried observations; and its one-line rows inherit the overstatements found in the lens
audits. The summary document's headline about value contradicts its own body, and it quotes figures no longer on the
notebook's page. Across lenses, "the halves" are drawn by two different hash functions, second samples of the same units
are read as replications, intervals rest on 100 resamples, and weak associations are written as absences.

**Priority:** **High** = affects interpretation, validity or downstream use; **Medium** = correct before relying on or
circulating the findings.

**Read first:** R07 (two hash functions), R01 to R03 and R05 (what Stage 3 will read), R08 (second samples).

## §8, the notebook's summary

### R01 | High | §8: "every lens and every companion table has been screened ... (B1 to B46)"

**Issue:** §8 opens "Every lens and every companion table has been screened (ADR 0030; `screens.yaml` names every
column), and each planned pair of the Stage 1 summary has its sizes, intervals, second period or half, and third factors
(B1 to B46)." Several sources added after Stage 2 were not screened: the ATO's postcode tables and the Census time series
(§3.1 says so), the 2024-25 business survey cubes (S2 L6 R06), WIPO's families by origin and the GII supplements
(examined as selected pairs, B55 and B61), and the PBS series (no Stage 2 treatment, S2 L5 R13). Several planned pairs
have no interval (B31, B52, B56, B57, B58, B59) or no second sample (B39, B43, B61). The range stops at B46, though B47 to
B62 appear in the table below.

**Action:** Say what was screened, what was examined as selected pairs, and what has no Stage 2 treatment; name B1 to
B62; mark the pairs without intervals. Evidence: `de334709`, `5cc45503`.

### R02 | High | §8: two observations carried in their lens summaries are missing from the signals

**Issue:** §7.4 carries B62 ("Yes: Q2") and §1.9 carries B15's divisionals ("Divisionals: lead"); neither appears in
§8's "Signals carried to Stage 3", the list Stage 3 will start from.

**Action:** Add both, or record why they are not carried. Evidence: `3833193b`, `12ee8be5`, `de334709`.

### R03 | High | §8: each row inherits the overstatements of the observations it compresses

**Issue:** §8's rows condense lens findings into single lines, and each line keeps wording the lens audits question:
"fewer renewals" (B10; S2 L1 R12, R34); "keep patents longer ... and are cited less mostly because of that narrower
reach" (B8, B12; S2 L1 R12, R18, R33); "pooled, a composition effect" (B13; S2 L1 R14); "Inventions and research made
here are often owned or used abroad" (B16, B46; S2 L1 R20, S2 L7 R01); "suppliers with IP win more and larger contracts"
(B24; S2 L2 R12, R13); "steep in the top fifth, not one firm's ... manufacturing's share shows no association ... does
not move it" (B29 to B31, B59; S2 L3 R16, R18, R20, R27); "changes in R&D barely move patenting" (B34; S2 L4 R13); "Six
policy changes give clean breaks" (B37; S2 L5 R02); "Fee changes rarely moved filing or lapsing ...; patent cessations
after the 2002 renewal rise did" (B47, B49; S2 L5 R03 to R05); "Among employers of 100 or more, filing rises with size
... R&D's weak link to patenting holds within size" (B50, B51; S2 L2 R21, R24); "Trade marks per business follow business
R&D across divisions" (B40; S2 L6 R02 to R04). "Recorded, not carried" lists B39 and B43 as screens "with no lead beyond
the expected", though B39's table holds one (S2 L5 R09).

**Action:** Regenerate §8 from the corrected observations as each theme is acted on; until then, mark the rows whose
wording is under review. Evidence: `de334709` and the findings cited.

### R04 | Medium | §8: firm size and industry are said to be "not in the data"

**Issue:** §8's list of third factors includes "firm size and industry (not in the data)", while its own data-gap
paragraph, B50 and B51 say that WGEA added size and industry for 7,126 firms.

**Action:** Write "known for WGEA reporters only (B50, B51); not for most filers". Evidence: `de334709`, `efb8d829`.

## The Stage 2 summary document

### R05 | High | `docs/stage-2-summary.md`: a headline contradicts its own body, and others claim more than the notebook

**Issue:** Section 1 heads a bullet "Value made here is often owned or used elsewhere", while its body says the
comparison "say[s] nothing of where value goes (restated 2 November 2026)": pass 5 restated the body and left the
heading. Other lines claim more than the notebook: "Representation matters for outcomes" is causal, though the next
sentence says the direction of cause is open; "lone filers' trade marks and designs are renewed far less" reads survival
as renewal; "Policy leaves clean breaks" (S2 L5 R02); section 3's industries row says "patents in 8 divisions only;
survey innovation is not IP" (superseded by B53 and B54, and S2 L6 R05); the institutions row says "little Australian use
of cited research" (S2 L7 R01); and section 7 says "Lifetimes, reach and citations are signs of private value", where
Stage 1's U36 says lifetimes are "on the register, not value".

**Action:** Restate those lines with the qualifications the notebook carries, each dated. Evidence:
`docs/stage-2-summary.md` sections 1, 3 and 7; notebook 1, cell `c7c3060d` (U36).

### R06 | Medium | `docs/stage-2-summary.md`: figures and method statements not on the notebook's page or out of date

**Issue:** Section 9 gives B58's most advantaged tenth as 11.03; B58 and its output give 11.0 (11.03 was the figure
before passes 1 and 2 moved the counts; the earlier places audit quoted it). Section 9 says "no other renewal change ...
did", against B49's July 1992 and July 1993 (S2 L5 R04), and that WIPO's share "held at about 64%", from two endpoints
(2006 and 2022) only. The status line says "observations B1 to B46". Section 2 says "Reproducible: sampling by hash ...
two full runs agree number for number": until pass 4 (2 November 2026) two builds did not agree (B28's lead count
flipped), and "by hash" covers two hash functions that give different halves (R07).

**Action:** Take the figures from the notebook's page; date the reproducibility statement and say what it covers.
Evidence: `ecc34934`, `539d13ec`, `c5b83a0e`, `b38c4ca4`; `docs/stage-2-summary.md` sections 2 and 9; pass 4 in
`analysis/GPT-audit/261030/AMENDMENTS.md`.

## Method across the lenses

### R07 | High | Two hash functions define "the halves"

**Issue:** The halves are drawn by two different functions. `screen_sample` and the SQL in §2 and §3 use DuckDB's
`hash(key || 'stage2') % 2`; `split_half` (B50, B58, B59) and the GII's halves in B35 use pandas' `hash_pandas_object(key
+ 'stage2') % 2`. They put different keys in each half. So B50's "two halves of the lens (the replication rule of section
2)" are not §2's halves, and B58's and B59's are not §3's: B29 and B30 fit 1,317 and 1,211 areas, B58 1,256 and 1,265,
under nearly the same filters. This is the cause of the inconsistency the earlier places audit found but could not
attribute (S2 L3 R02). `split_half`'s docstring ("the same row always lands in the same half whichever columns are
loaded") holds within each function only.

**Action:** Use one function everywhere (DuckDB's, which defines the screens), rerun B50, B58, B59 and B35's GII halves,
and add a test that every analysis's halves agree with the screen's. Evidence: `bivariate.split_half`,
`bivariate.screen_sample`; `dff03f5c`, `f80eb1ec`, `348901fd`, `9f01d1f9`, `ecc34934`, `b7179e5a`, `9fae40b0`.

### R08 | High | Second samples of the same units are read as replications

**Issue:** Where a lens has few units, its second sample is the same units at another time: the same 19 divisions a year
later, with R&D held fixed (§6); mostly the same 112 institutions seven years earlier (§7); the same countries a decade
earlier (§4). Persistent traits make agreement likely whatever the relationship. ADR 0030 rejected random halves of one
decade for the rights lens because they "agree almost by definition"; the same reasoning applies here. "Holds in the
other period? yes" in §4.5, §6.7 and §7.4 is read as replication.

**Action:** Call these stability checks, keep "replicated" for independent samples, and say in each lens summary which
kind of check its "yes" is. Evidence: `56ed2b2a`, `d4ae03dc`, `0cb36a4b`; ADR 0030 (Rejected).

### R09 | Medium | Intervals rest on 100 resamples that treat rows as independent

**Issue:** Every lead's "95% bootstrap interval" comes from 100 resamples (`leads_table`'s `reps=100`; ADR 0030, point
7). With 100 draws the 2.5th and 97.5th percentiles are close to the 3rd and 98th values, whose resampling error is about
the size of the third decimal printed. Rows are resampled as independent, which they are not within a family or applicant
(rights), a firm (firms), neighbouring areas (places) or adjacent quarters (timeline).

**Action:** Use 1,000 or more resamples for intervals that are quoted, and state the resampling unit and the dependence
it ignores. Evidence: `bivariate.leads_table`, `bivariate.strength_interval`; ADR 0030.

### R10 | Medium | The shared scale breaks down for categories in small lenses

**Issue:** The method says the three measures coincide for yes/no variables (the notebook's introduction; the summary's
"For a yes/no variable all three are |rho|"). That holds for the rank correlation ratio. It does not hold for the
bias-corrected Cramér's V: for two yes/no variables `association` computes V² = (phi² − 1/(n − 1)) / (1 − 1/(n − 1)). At
200,000 rows the difference is nil; with 112 institutions a phi of 0.1 gives a V of about 0.03, below the lead threshold,
and for a six-level category such as kind the subtraction is larger. Category pairs in the small lenses are therefore
held to a stricter bar than number pairs. Spearman's rho also measures monotonic association, not association "in any
shape" (S2 L1 R02).

**Action:** State the exception; in the small lenses, show the uncorrected value beside V for category pairs, or set the
threshold on it. Evidence: `0a9fee61`, `bivariate.association`.

### R11 | Medium | The heatmaps explain neither their symbols nor their saturation

**Issue:** `strength_map` explains its symbols (a black outline for a lead, grey hatching for "by construction", a cross
for "not replicated") only in its default title, and every call in the notebook passes its own title, so no heatmap
explains them. Its colour scale stops at 0.6 (`vmax=0.6`), so strengths from 0.6 to 0.98 share one shade, and the colour
is unsigned. This confirms from the code what the earlier audits saw in the figures (S2 L1 R31, S2 L2 R27, S2 L3 R32,
S2 L4 R09), and it applies to §5's and §7's heatmaps as well.

**Action:** Add a legend for the symbols, extend the scale to 1 or mark saturation, and say that colour shows strength
without direction. Evidence: `bivariate.strength_map`; `876656ad`, `c0c3cee3`, `1cb83215`, `56ed2b2a`, `963a0e6d`,
`0cb36a4b`.

### R12 | Medium | Weak or non-significant associations are written as absences

**Issue:** Across sections, weak or non-significant associations become statements that something does not happen:
"changes in R&D barely move patenting" (B34), "hardly move together" and "no common cycle" (B36), "do not move together"
(B39), "not what IP measures" (B42), "no link" (B45), "not from here" (B56), "does not lift its filing" (B59). With these
sample sizes, an absence needs an interval that excludes associations large enough to matter, not a small point estimate
or a failed correction.

**Action:** Adopt one wording rule ("no association detected; the interval allows up to ..."), and apply it in the
observations and the summaries. Evidence: `c510ff8c`, `a7778e51`, `9c64ef93`, `34a69580`, `a0717d6a`, `9b554c9c`,
`926d52ec`.

## Review boundary and reproducibility

This report contains **12 issue/action entries** (6 High, 6 Medium). It reviews §8, the front matter, the lens
summaries as they feed §8, the summary document against the notebook, and the helpers named above. It did not
re-execute the notebook or query the lenses: the two hash functions' disagreement is shown by the saved counts and the
code, not by recomputing the halves. No notebook, code, summary or website files were changed by this audit.

**Evidence locators:** B-numbers and section headings are searchable; eight-character identifiers are the notebook
JSON's stable cell `id` values; Stage 1 cells are marked "notebook 1".

Repository commit: `cb544481aa64830e95c1ecd64260454baef41ed5`.

Reviewed notebook SHA-256: `3d250d2a14a58e9b4546c01601969bbe7d14e963f46b030276abbbd01a02b7e2`.
