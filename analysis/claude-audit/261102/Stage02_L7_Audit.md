# Stage 2 notebook audit: Lens 7, research institutions

**Reviewed:** 2 November 2026, by a Claude Code session at the owner's request. **Source:**
`analysis/notebooks/02_bivariate.ipynb` as committed at `cb54448` (SHA-256 in full below), read in the repository. The
GitHub web pages and the evidence atlas were not looked at.

**Provenance:** The first audit of this section. Format as in `analysis/GPT-audit/261030/`, with a bar in place of the
dash after each finding's number. R-numbers are local to this report.

**Scope of this pass:** §7 only, §7.0 to §7.4 (B44 to B46, B62): all 14 cells, the 5 code cells (execution counts 67
to 71) with their saved outputs, and the one figure (the screen's heatmap, read from its code). Read beside it: the
institutions lens's definitions (`variables.yaml`, `screens.yaml`) and the open review of the institutions link (OQ11).
Nothing was re-executed.

**Overall finding:** The quoted numbers match the saved outputs, apart from two counts in §7.1's text. B46 reads US
patents' citations as evidence of where Australian research is used, a theme the earlier audits raised for Stage 1 and
the passes have left open. B62's six ratios share one denominator, and its "fair sign of commercialisation" is an
evaluation the correlations cannot carry. The second period is mostly the same institutions, so "holds" means stable,
and the strongest lead (ARC grants by kind) is a funding rule. Citation measures are compared across periods of
different ages. Weak or imprecise correlations become "no link".

**Priority:** **High** = affects interpretation, validity or downstream use; **Medium** = correct before relying on or
circulating the findings. Apply each correction to §7.4, to §8's rows and to `docs/stage-2-summary.md`.

**Read first:** R01 to R03.

## Interpretation of the citation and commercialisation measures

### R01 | High | B46, §7.4, §8, summary: US patents' citations read as where Australian research is used

**Issue:** B46's population is citations from US patents (Reliance on Science), most of which are owned abroad whatever
they cite. That a median 3.252% (2017 to 2023, 82 institutions) and 5.482% (2010 to 2016, 69) of those citations come
from patent families with an Australian applicant or inventor says little without a baseline, such as the Australian
share of all US patents, or of US patents citing comparable research from elsewhere. A citation, often added by an
examiner or an attorney, is not use, and an inventor's address is not where an invention is made. Yet B46 concludes
"Australian research is used mostly by inventions owned and made elsewhere", §8 that research "made here [is] often ...
used abroad", and the summary's lens table "little Australian use of cited research". The earlier audits raised this
theme for Stage 1 (S1 L7 R13, S8-S9 R23), and pass 5 left it open with B46 in it.

**Action:** Describe the measure exactly (the share of US-patent citations to the institution's works that come from
families with an Australian applicant or inventor); add a baseline; keep "use" and "made elsewhere" as questions for Q1.
Evidence: `797899c5`, `843f4da2`, `3833193b`, `de334709`; `variables.yaml` (`patent_citations_au`).

### R02 | High | B62: six ratios on one denominator, and an evaluative conclusion

**Issue:** Every measure in B62 is divided by the same research expenditure, so an institution whose reported
expenditure is low, or misreported, is high on all six, and the six correlations (0.349 to 0.694) are inflated by the
shared denominator. "Size is removed by the ratios" is asserted, not shown. "An institution's patents are a fair sign of
its commercialisation at this level" is an evaluation drawn from correlations of about 0.5 across 66 and 67 institutions,
with lumpy licence income and survey data that end in 2015. Patents are counted by the year of application, which for a
PCT filing is national phase entry (`variables.yaml`), while disclosures are counted in the year reported, so "the same
years" are not aligned for PCT filings. The NSRC is joined to the lens by name.

**Action:** Test the pairs as counts with research expenditure as the exposure (or as partial correlations of logs,
holding log expenditure); report what remains; replace "a fair sign" with the association and its period (2004 to
2015); note the year alignment and the name join. Evidence: `f0269567`, `7ee1c7e9`; `variables.yaml` (`nsrc_*`,
`patents_standard`).

## The design of the comparison

### R03 | High | B44, B45, §7.4: the second period is the same institutions, and kind encodes funding rules

**Issue:** The discovery (2017 to 2023) and replication (2010 to 2016) samples are mostly the same institutions (112
and 111); kind, size, age and state are fixed traits, so "holds in the other period" shows stability, not an
independent replication. The strongest lead, ARC grants per 1,000 works by kind (0.898; 0.794), reflects the ARC's rule
that its grants are administered by eligible organisations, almost all universities; NHMRC grants by kind (0.36) is the
same kind of mechanic. "Larger institutions win more ARC grants per work (0.803; 0.826)" is largely universities against
medical research institutes (kind is the pair's first candidate third factor) and is not checked within kind.

**Action:** Call the period comparison a stability check; record ARC and NHMRC grants by kind as mechanics of funding,
not performance (as B2 does for the rights lens); check size against ARC grants within universities. Evidence:
`0cb36a4b`, `28dd3fe0`, `3833193b`.

### R04 | Medium | B44 to B46: patent citations to recent works are compared across periods of different ages

**Issue:** §7's rules say patent citations are compared by cohorts of the same age, but the two periods are not the same
age: works published in 2017 to 2023 have had less time to be cited by patents (to 2025) than those of 2010 to 2016, as
`variables.yaml` notes for `works_patent_cited`. B46 sets 3.252% beside 5.482%; B44 and B45 compare correlations with
citation measures across the periods.

**Action:** Compare citation measures at a fixed age (for example, each work's first five years), or state the
truncation beside each comparison and avoid reading the two periods' levels as a change. Evidence: `0cb36a4b`,
`797899c5`, `843f4da2`; `variables.yaml` (`works_patent_cited`).

### R05 | Medium | B45: "no link" and "not about what changes" from imprecise correlations

**Issue:** The industry-partner pair is 0.127 and -0.074 over 36 and 33 universities, with strength intervals reaching
0.50 and 0.43; "no link" and "Universities that do more industry-partnered research do not file more of their patents
jointly" say more than that. The changes between periods (rho 0.111 and -0.221 over 42 universities) have no interval,
and differences of ratios between two periods are noisy, so "the levels' strong links are about which universities are
research-intensive, not about what changes within them" is a hypothesis.

**Action:** Say that no association was detected, with the intervals; add intervals to the changes; keep the reading as
a hypothesis. Evidence: `dafca199`, `a0717d6a`.

### R06 | Medium | §7.1: the text does not match the output

**Issue:** §7.1 says "The 44 universities" and "Four pairs"; the output has 43 and 42 universities and five pairs (ARC
grants per 1,000 works against patents per 1,000 works was added to `PAIRS`).

**Action:** Correct both. Evidence: `750aae08`, `dafca199`.

## Review boundary and reproducibility

This report contains **6 issue/action entries** (3 High, 3 Medium). It reviews §7's text, code and saved outputs and the
definitions they rely on; it did not re-execute the notebook or query the lenses, and it does not assess the
institutions link itself (OQ11). All 5 code cells have saved outputs, execution counts 67 to 71 in order, and no saved
errors. No notebook, code or website files were changed.

**Evidence locators:** B-numbers and section headings are searchable; eight-character identifiers are the notebook
JSON's stable cell `id` values.

Repository commit: `cb544481aa64830e95c1ecd64260454baef41ed5`.

Reviewed notebook SHA-256: `3d250d2a14a58e9b4546c01601969bbe7d14e963f46b030276abbbd01a02b7e2`.
