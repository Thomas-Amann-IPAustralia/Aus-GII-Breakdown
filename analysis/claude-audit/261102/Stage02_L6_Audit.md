# Stage 2 notebook audit: Lens 6, industries

**Reviewed:** 2 November 2026, by a Claude Code session at the owner's request. **Source:**
`analysis/notebooks/02_bivariate.ipynb` as committed at `cb54448` (SHA-256 in full below), read in the repository. The
GitHub web pages and the evidence atlas were not looked at.

**Provenance:** The first audit of this section. Format as in `analysis/GPT-audit/261030/` (themed sections; numbered
findings with an **Issue** and an **Action**; a review boundary), with a bar in place of the dash after each finding's
number. R-numbers are local to this report.

**Scope of this pass:** §6 only, §6.0 to §6.7 (B40 to B43, B53, B54, B57, B60): all 23 cells and the 8 code cells
(execution counts 59 to 66) with their saved outputs; the section has no figures. Read beside it: the industries lens's
definitions (`variables.yaml`, `screens.yaml`), ADR 0030, and the Stage 1 amendments to the same claims (pass 3,
`analysis/GPT-audit/261030/AMENDMENTS.md`). Nothing was re-executed.

**Overall finding:** The quoted numbers match the saved outputs. Five problems matter. Later additions were not carried
back: §6's rules, B41 and §6.7 still say patents reach only goods-producing divisions and that the crosswalk with
services is a step still to take, though §6.4 takes it, and the rules still call the crosswalk "near certain", a phrase
pass 3 withdrew from Stage 1. Counts allocated to divisions by technology are read as what each division's businesses
file. The second "sample" is the same 19 divisions a year later, with business R&D held fixed. Two of the four distinct
leads set a ratio against its own denominator. And B42 and B60 keep the main crosswalk's zeros, which §6.4 showed hold
patent pairs back, while B60 turns B42's "no consistent link" into a direction.

**Priority:** **High** = affects interpretation, validity or downstream use; **Medium** = correct before relying on or
circulating the findings. Apply each correction to §6.7, to §8's industries rows and to `docs/stage-2-summary.md`.

**Read first:** R01 to R05.

## Later additions not carried back

### R01 | High | §6 rules, B41, §6.7, summary: superseded statements about the crosswalk

**Issue:** §6's rules say industry counts are "near certain for divisions" and that "patents reach only goods-producing
industries, because the crosswalk excludes services (U75)". Pass 3 withdrew "near certain" from Stage 1 (S8-S9 R21: the
weights are concentrated, a median 0.996 in U74, not proven right). §6.4 (B53, B54), added after Stage 2, puts patents in
all 19 divisions through ALP's crosswalk with services (business R&D × patents 0.739, interval 0.38 to 0.89, against
0.465 without). Yet B41 still ends "the industries lens cannot say much about R&D and patenting until the crosswalk
includes services (Stage 1's lead: ALP's version with services, free)"; §6.7's B41 row says "Data gap: services
crosswalk" and its closing paragraph "Adding ALP's crosswalk with services (free) is the step that would let this lens
say more"; and the Stage 2 summary's lens table says "patents in 8 divisions only". No earlier audit covered §6, so pass
3's sweep did not reach it.

**Action:** Restate the rules (the weights are concentrated, not certain; two crosswalks, with and without services),
B41's last sentence, §6.7's B41 row and closing paragraph, and the summary's table, each with a dated restatement line.
Evidence: `6fa1c326`, `78e48336`, `0bd73957`, `5cb52913`; `docs/stage-2-summary.md` section 3.

## What the counts measure

### R02 | High | B40, B41, B53, B54, B57, B60: counts allocated by technology are read as what a division's businesses file

**Issue:** The lens's patent counts are expected counts: each application's IPC subclasses are split over ANZSIC
classes by the ALP crosswalk, "a probability, not where the patent is used" (`variables.yaml`). The text reads them as
what each division's businesses do: "manufacturing and utilities file most per business" (B41); "divisions of many small
traders ... file few marks per business" (B40); "divisions of many small businesses file few patents per business" (B53);
"divisions that add more value per business file more trade marks" (B57); "innovating divisions file more trade marks per
business" (B60). The all-origin measure divides every applicant's applications, mostly from overseas, by Australian
businesses: in manufacturing, Australians' applications are 23.76 of the 314.6 per 1,000 businesses. The divisions that
stand out are partly the crosswalk's doing: electricity, gas, water and waste services receive 180.6 standard patents per
1,000 businesses, and public administration and safety 115.2 trade marks.

**Action:** Write "applications allocated to the division by technology (or by goods and services class), per 1,000
of its businesses"; keep "file" for observed filers; use the Australian-origin measure for any statement about
Australian businesses; and, for the divisions that stand out, say which classes put them there. Evidence: `61bded9b`,
`78e48336`, `9ac695bd`, `0bd73957`, `3e094110`, `1e2473ef`; `variables.yaml` (industries, `patents_standard`).

### R03 | High | B40, B53, B57, §6.7: the second year is not a second sample

**Issue:** The replication sample is FY2025 against FY2024's discovery: the same 19 divisions a year apart, with
business R&D held at FY2024 in both. A division's structure barely changes in a year, so agreement is expected whatever
the relationship. ADR 0030 rejected random halves for the rights lens because two halves of one decade "agree almost by
definition"; adjacent years of the same divisions do too. B40's 8 leads, B53's 16 and B57's FY2025 values, and §6.7's
"Holds in the other year? yes", are read as replication.

**Action:** Call the second year a stability check; treat the leads as a single sample of 19 units, as B43 does for the
attachments; if a second sample is wanted, use an earlier pair of years with its own R&D survey. Evidence: `d4ae03dc`,
`9ac695bd`, `f3f462a4`, `8e70adea`, `5cb52913`; ADR 0030 (Rejected).

### R04 | High | B40, B53: two of the four distinct leads set a ratio against its own denominator

**Issue:** Businesses at the start of the year are screened against ratios divided by them: trade marks per 1,000
businesses (-0.675; -0.674), business R&D per business (-0.623; -0.602) and Australians' trade marks per 1,000 businesses
(-0.616; -0.6); B53 adds patents per 1,000 businesses (-0.639; -0.653). A ratio falls as its denominator grows unless
the numerator grows in proportion, so these correlations are partly arithmetic. "Divisions of many small traders ... file
few marks per business" may be true, but the screen cannot show it.

**Action:** Mark denominator-against-ratio pairs as related by construction in `screens.yaml`, or test them as counts
with businesses as the exposure (or log count against log businesses, reading the slope and its interval). Evidence:
`d4ae03dc`, `9ac695bd`, `f3f462a4`, `0bd73957`.

### R05 | High | B42, B60, summary: patent pairs on the main crosswalk's zeros, and conclusions beyond 17 divisions

**Issue:** §6.4 found that the main crosswalk's zeros (11 of 19 divisions with no patents) hold patent pairs back, and
B54 says Stage 3 should report both crosswalks. B42 and B60 still use the main crosswalk only, so their patent
correlations (-0.406, -0.104, -0.325) largely set the service divisions, all at zero patents, against their
innovation-active shares; B60's headline ("innovating divisions file more trade marks per business, not more patents")
may be the zeros. B42's "the survey's innovation is not what IP measures, which matters for Q3" is a conclusion from
17-division correlations whose strength intervals run from 0.01 to 0.86, and B60 turns B42's "does not consistently go
with its filing" into a direction, which the summary repeats ("survey innovation is not IP"; "B42 holds in a third
survey").

**Action:** Redo B42 and B60 with the crosswalk with services beside the main one; describe the results as weak and
imprecise across 17 divisions; keep "not what IP measures" as a hypothesis for Q3. Evidence: `467ad512`, `34a69580`,
`f00f6abf`, `1e2473ef`, `27731507`; `docs/stage-2-summary.md` sections 3 and 9.

## Attachments, value added and presentation

### R06 | Medium | B43: the screen's scope, periods and single pass

**Issue:** B43 screens "2,157 division-level indicators" from the business surveys and the Wage Price Index. The 2024-25
survey cubes (`bcs_cubes`, added after Stage 2, U119) are not in it, and §6.3 does not say so (as §3.1 now does for the
places lens). Each indicator is taken in its latest period, against FY2024 filing, and the periods are not shown. The one
pass (q 0.016) is one of 4,270 tests among survey items that are versions of one another (by size, region and so on),
with no second sample, and patents come through the main crosswalk.

**Action:** Name this the original screen and its exclusions; show each indicator's period; report the pass as a single
sample among dependent items; repeat the patent column with the crosswalk with services. Evidence: `9e6917b1`,
`7640b5ee`.

### R07 | Medium | B57: no intervals, and a measure that is partly size

**Issue:** B57 reports five rank correlations over 19 divisions with no interval, though the notebook promises one for
every planned pair, and its FY2025 values are the same divisions a year on (R03). Value added per business is chain-volume
value added divided by CABEE's count of businesses, which includes non-employing businesses, so it measures business size
and capital intensity as much as productivity.

**Action:** Add intervals, as B41 does; describe the measure and its denominator; apply R02's wording. Evidence:
`8e70adea`, `3e094110`.

### R08 | Medium | B41: "no patent class to services" is not what the table shows

**Issue:** B41 says "the other 11 divisions none, because the ALP crosswalk sends no patent class to services (U75)".
Its table shows the main crosswalk placing patents in three service divisions: public administration and safety (8.762
per 1,000 businesses), other services (0.221) and professional, scientific and technical services (0.022).

**Action:** Say that the main crosswalk places patents in 8 divisions, mostly goods-producing, and that the 11 with none
are service divisions. Evidence: `61bded9b`, `78e48336`.

### R09 | Medium | §6, §6.7: no charts, and replication labels that are not replication

**Issue:** §6 has no charts: its eight code cells end in tables, though the project's evidence rules prefer charts, and
B41 and B54 are rankings a dot chart would show. §6.7's column "Holds in the other year?" holds "yes (R&D fixed)", "two
survey years", "three surveys" and "interval", none of which is a replication (R03). B54's "the recommended one as the
main measure" does not say which crosswalk is recommended.

**Action:** Add a dot chart for B54 (both crosswalks) and one for B41's trade marks; relabel §6.7's column; name the
recommended crosswalk and why. Evidence: `27731507`, `0bd73957`, `5cb52913`.

## Review boundary and reproducibility

This report contains **9 issue/action entries** (5 High, 4 Medium). It reviews §6's text, code and saved outputs and the
definitions they rely on. It did not re-execute the notebook or query the lenses; numbers were checked against the saved
outputs. All 8 code cells have saved outputs, execution counts 59 to 66 in order, and no saved errors. No notebook, code
or website files were changed.

**Evidence locators:** B-numbers and section headings are searchable; eight-character identifiers are the notebook
JSON's stable cell `id` values.

Repository commit: `cb544481aa64830e95c1ecd64260454baef41ed5`.

Reviewed notebook SHA-256: `3d250d2a14a58e9b4546c01601969bbe7d14e963f46b030276abbbd01a02b7e2`.
