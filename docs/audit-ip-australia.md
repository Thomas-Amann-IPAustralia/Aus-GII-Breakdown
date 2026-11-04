# Audit: Stage 1 against IP Australia's published evidence

**What this is.** A check of Stage 1's observations (U0 to U98, `analysis/notebooks/01_univariate.ipynb`) against what
IP Australia has published: its Australian IP Reports 2015 to 2026, its economic research papers and analytic notes,
and (for a few observations) the WIPO publications held beside them. The aim is to validate or invalidate each
observation wherever IP Australia's evidence allows. The decisions it leads to are recorded in
[ADR 0024](adr/0024-audit-against-ip-australia.md).

**Extended on 4 November 2026** to Stage 1's later observations (U99 to U127) and Stages 2 and 3 (B1 to B63, M1 to
M38), at the owner's decision (A35): section 11, with [ADR 0052](adr/0052-audit-extended-to-stages-2-and-3.md).
Sections 1 to 10 are as they were.

**Date:** 27 October 2026. **Whose:** Claude's, at the owner's request. **Strength:** every verdict is descriptive. A
match says the lens reproduces IP Australia's published reading of its own register; it does not make either a
cause.

**Sources.** The IP Australia publications as the Econ repository holds them (its knowledge base,
`Econ/library/elements/<doc_id>.jsonl`: each document's text in reading order, with the PDF page of every passage).
A citation such as *ipr-2026 p21* is the Australian IP Report 2026, page 21 of its PDF. The documents: the twelve IP
Reports (`ipr-2015` to `ipr-2026`; the 2018 and 2021 editions are scanned and read by OCR), nine economic research
papers (`erp01` to `erp16`), two analytic notes and one Office of the Chief Economist report; and six WIPO documents
(`wipo-*`), used only where an observation already rests on WIPO.

---

## 1. In brief

**The outcome.** Stage 1's counts of IP Australia's register are corroborated: IP Australia's own published figures
are reproduced from the lenses, year by year, for every type of right. Where IP Australia publishes a figure Stage 1
also measured, the two agree, with one exception that needs IP Australia to explain its base (D3 below). The audit
also found four things the observations did not know, three of which change how observations should be read, and
it closes or narrows four leads (U8, U45, U67, U90).

**The numbers** (`analysis/audit/output/benchmark.csv`, written by `python -m audit.benchmark`):

1. **195 published figures** were recomputed from the lenses on IP Australia's definitions; **155 agree** within the
   tolerance (a count within 2%, a share within 1 percentage point).
2. **Applications agree almost exactly:** standard patents 12 of 12 years (2014 to 2025) within 0.34%; provisional
   applications 11 of 11 within 0.25%; plant breeder's rights 5 of 5 within 0.71%; designs 4 of 4 within 0.59%; trade
   marks 10 of 11 within 0.05% (2018 is 2.51% low, D2). Grants of standard patents agree in all 10 years published
   (within 0.03%), and trade mark registrations, design certifications and plant breeder's rights registrations in
   every year published.
3. **Who and how agree:** resident standard patents within 1.2% in every year from 2018 (exactly, in 2022 and 2025);
   non-resident within 0.36% in all 8 years; US applicants within 1.82%; the PCT route within 0.35% (shares within 0.34
   points); Madrid trade marks within 0.1%; states' shares of resident patents within 0.2 points; Aristocrat's
   applications, IP Australia's leading domestic filer, within 1.4%.
4. **The 40 figures outside tolerance** are explained by a difference of definition (32: states counted per
   applicant, an older resident definition, innovation patents' conversions, small counts), or are real
   discrepancies (8 figures in four findings, D1 to D4).
5. **Verdicts** on the 99 observations (section 5): 23 corroborated (three with a qualification, U1, U7 and U27, and
   one with a single figure disputed, U13), 9 consistent, 1 disputed in part (U48) and 66 that IP Australia's
   publications cannot test (they concern the data's structure, the repairs, or sources other than IP Australia's).
   None is contradicted.

**What changes** (ADR 0024):

- **Design shares** (U7, U13): the designs IP RAPID leaves "origin unknown" are mostly Australian on IP Australia's
  count, so Australian design shares among known origin are lower bounds, about 2 to 3 points low.
- **Trade marks filed in 2018** (U5, U25, U90): IP RAPID holds 1,994 fewer than IP Australia reported, in its Madrid
  applications; Stage 2 flags 2018 in trade mark series.
- **Two leads close or narrow:** IP RAPID's innovation patents in 2016 (U67) were a real rise, which IP Australia
  reported; and the fall in first-time trade mark filers (U45) is a fall in ABN linking, not in filing.
- **One policy response is added:** the innovation patent's closure also pulled forward Australians' standard patents
  in 2021 (U28).
- **Three questions for IP Australia** join the owner's request (section 8).

---

## 2. How the audit was done

1. **Finding IP Australia's evidence.** The IP Report 2026 was read in full; the other documents were searched by
   topic (applications, residency, origins, routes, states, fields, filers, grants, times, expedited examination,
   renewals, assignments, attorneys and self-filing, firms and SMEs, ABNs, universities, gender, regions, industry,
   R&D and policy changes), and every relevant passage was read in context. Each IP Australia figure used is cited
   by document and page.
2. **Like for like.** Each published figure that Stage 1's data can also produce is in
   `analysis/audit/published.csv` (195 figures, with its document and page), and `analysis/audit/benchmark.py`
   recomputes it from the lens tables on IP Australia's definitions:
   - **a calendar year** of filing, grant or registration (the notebook uses financial years, so its figures are not
     quoted against IP Australia's directly);
   - **a resident application** has a founding applicant in Australia (`founding_australian`). IP Australia says
     residency "is based on the origin that an applicant provides in their first application to IP Australia"
     (ipr-2026 p32); this definition gives its 2,494 resident standard patents in 2022 and its 2,810 in 2025 exactly;
   - **a PCT application** counts when it enters the national phase, as in the lens (ADR 0010).
3. **Tolerance.** A count agrees if it is within 2% of the published figure, a share within 1 percentage point (5
   points where IP Australia gives the share in words, such as "close to half"). IP Australia revises its series
   ("data presented in this report may vary from data updates in IPRAPID", ipr-2025 p6), and the latest edition to
   state a year is used.
4. **Lens-only figures** that the audit quotes beside IP Australia's text (design applications of unknown origin,
   new filers counted by applicant, examination times by year) are in `analysis/audit/output/context.csv`, and the
   states' shares in `state_shares.csv`.
5. **Verdicts:**

| Verdict | Meaning |
|---|---|
| **Corroborated** | IP Australia publishes the same quantity, and the lens reproduces it within tolerance once definitions are aligned |
| **Consistent** | IP Australia publishes a related figure or finding that points the same way, but not the same quantity |
| **Qualified** | IP Australia's figures agree in part, but show a caveat the observation does not state |
| **Disputed** | IP Australia publishes a figure for what reads as the same quantity, and the lens cannot reproduce it |
| **Contradicted** | IP Australia's figure for the same quantity disagrees beyond tolerance with no difference of definition to explain it (none found) |
| **Not testable** | IP Australia has published nothing comparable |

6. **IP Australia's interpretations** are reported with the strength IP Australia itself gives them ("consistent
   with", "suggests", "not causal"). They are evidence about the leads, not conclusions of this project: adopting
   any of them is the owner's call (CLAUDE.md).

Run it: `cd analysis && uv run python -m audit.benchmark` (seconds, once `python -m eda.build` has built the lenses).
`tests/test_audit.py` checks that every published figure has a lens query, a source and a valid observation, and
that the committed output is in step with the lenses where they are built.

---

## 3. What agrees

Figures from `analysis/audit/output/benchmark.csv`; the ratio is the lens's value over IP Australia's.

| Measure | Years published | Agree | Ratio (or difference) | Observations |
|---|---|---|---|---|
| Standard patent applications | 2014 to 2025 (12) | 12 | 0.9995 to 1.0034 | U5, U6, U25 |
| Resident standard patents | 2014 to 2025 (11) | 7 | 0.9977 to 1.0118 from 2018; 1.0202 to 1.0268 in 2014 to 2017 | U7, U13 |
| Non-resident standard patents | 2017 to 2025 (8) | 8 | 0.9995 to 1.0036 | U7, U13 |
| US applicants' standard patents | 2015 to 2025 (5) | 5 | 0.9818 to 1.0010 | U13, U70 |
| Chinese applicants' standard patents | 2023, 2025 | 2 | 0.9870, 1.0082 | U13, U70 |
| Standard patents through the PCT | 2020 to 2024 (4) | 4 | 0.9965 to 1.0013 | U89, U90 |
| PCT share of standard patents | 2022, 2024, 2025 | 3 | +0.04, +0.06 and −0.34 points | U89, U90 |
| Pharmaceuticals, medical technology, biotechnology | 2021, 2023, 2025 (9) | 7 | 0.9541 to 1.0013 | U14 |
| Standard patents granted | 2014 to 2025 (10) | 10 | 0.9997 to 1.0000 | U10, U27 |
| Provisional applications | 2014 to 2025 (11) | 11 | 0.9976 to 1.0025 | U5, U8, U25 |
| Resident provisional applications | 2016 to 2024 (8) | 8 | 0.9993 to 1.0054 | U7, U13 |
| Individuals' share of provisionals | 2024, 2025 | 2 | 34.08% against "around one-third"; 48.25% against "close to half" | U8 |
| Trade mark applications | 2015 to 2025 (11) | 10 | 0.9749 (2018); 1.0000 to 1.0005 otherwise | U5, U6, U25 |
| Resident trade marks | 2015 to 2025 (7) | 7 | 0.9972 to 1.0004 | U7, U13 |
| Madrid trade marks | 2015 to 2025 (6) | 6 | 1.0000 to 1.0010 | U90 |
| Madrid share of overseas trade marks | 2020 | 1 | 56.14% against 56% | U90 |
| Trade marks registered | 2021, 2023, 2025 | 3 | 1.0000 to 1.0007 | U27 |
| Design applications | 2014 to 2025 (4) | 4 | 1.0007 to 1.0059 | U5, U25 |
| Designs certified | 2021, 2023, 2025 | 3 | 1.0000 | U32 |
| Plant breeder's rights: applications, registrations | 2018 to 2025 (10) | 10 | 0.9929 to 1.0000 | U5, U27 |
| Aristocrat's standard applications | 2017, 2021, 2025 | 3 | 159, 72 and 123 against 157, 71 and 123 | U52 |
| Median request for examination to acceptance | 2020 | 1 | 1.23 years against 1.3 | U33 |

**States** (`state_shares.csv`): IP Australia counts a resident application in the state of each of its Australian
applicants, the lens in its first founding applicant's, so the lens's counts are mostly lower, by up to 7.4% (IP
Australia's 2025 states sum to 2,836 against 2,810 resident applications). As shares the two agree within 0.2 points
in every state in
2021, 2023 and 2025: New South Wales 40.6% (IP Australia) against 40.5% (lens) in 2025, Victoria 22.5% and 22.4%,
Queensland 18.0% and 18.0%. IP RAPID omits the state for 34.96% of Australian standard patents filed from FY2024
(U16), so the agreement in 2025 also checks the repair that takes the state from the postcode (ADR 0012).

**Explained by definition** (the remaining figures outside tolerance that are not findings):

- **Resident standard patents, 2014 to 2017** (1.0202 to 1.0268): IP Australia's editions of those years count the
  first applicant's origin; counted that way (`context.csv`) the lens gives 1,988, 2,295, 2,624 and 2,518 against
  IP Australia's 1,979, 2,284, 2,620 and 2,503, all within 0.6%. From 2018 IP Australia's figures match
  `founding_australian`.
- **Innovation patents, 2015 to 2017** (1.0633 to 1.0721): IP RAPID holds 6% to 7% more than IP Australia then
  reported, the same in each year; IP Australia's 2020 and 2021 figures, which it says include "standard patents
  converted to innovation patents" (ipr-2022 p16), agree within 0.14%. So the earlier editions left conversions out.
- **Resident grants, 2018 and 2019** (1.0409 and 1.0434): IP Australia's 2020 edition, again by the first applicant's
  origin, which gives 900 and 833 against its 905 and 829 (`context.csv`); from 2021 the figures match exactly.
- **Pharmaceuticals, 2021 and 2023** (0.9731, 0.9541): IP Australia gives fields as a "share of total classes"
  (ipr-2024 p32), so a patent can count in more than one field, while the lens counts each patent once, in its main
  field. Unclassified filings are few in those years (158 and 238 of the year's standard applications, `context.csv`;
  1,184 in 2025).
- **Small counts:** CSIRO's 48 standard applications in 2017 against 45; plant breeder's rights by residents in 2021
  (129 against 124); overseas applications with two or more applicants in 2020 (2,014 against 1,811, the lens counting
  every founding applicant); trade mark individuals' shares 28.39% and 26.29% against "private applicants" 27% and 28%
  (2010 and 2015, ipr-2017 p36).

---

## 4. What does not agree, and what it means

**D1 (qualifies U7 and U13). The designs IP RAPID leaves "origin unknown" are mostly Australian.** IP Australia
reports 2,595 resident design applications in 2021, 2,652 in 2023 and 3,078 in 2025 (ipr-2022 p3, ipr-2024 p7,
ipr-2026 p58); the lens finds 2,331, 2,358 and 2,653 with a founding applicant in Australia (ratios 0.8619 to 0.8983),
while total designs agree within 0.59%. The gap is the designs with no applicant country in IP RAPID: 332 (2021), 435
(2023) and 577 (2025), of which IP Australia counts 264, 294 and 425 as residents, about three in four (80%, 68% and
74%). So the unknowns are not a random sample of designs, and a design share among known origin understates
Australians: 2025's known-origin share is 2,653 of 9,726 (27.3%) against IP Australia's 29.9%; 2021's 29.9% against
32%. U7's rule (a design share is always shown with its unknown share) stands, and gains a note: the known-origin
share is a lower bound, by about 2 to 3 points in recent years. IP Australia holds the origin IP RAPID does not
publish (a question for IP Australia, section 8).

**D2 (a data caveat for U5, U25 and U90). Trade marks filed in 2018: IP RAPID holds 1,994 fewer than IP Australia
reported, all in Madrid applications.** IP Australia reported 79,490 applications in 2018, with Madrid applications
"increasing by around 13 per cent" to 22% of the total (ipr-2019 p8, p9); the lens holds 77,496 (0.9749), with 15,836
through Madrid, the same as 2017's 15,844 (20.43% of the total, against 22%). Every other year from 2015 to 2025
agrees within 0.05%, including 2017's Madrid growth, "27 per cent" (ipr-2018 p17), which the lens shows as 12,468 to
15,844 (`context.csv`). The cause is not known: Madrid designations that IP RAPID dates in another year, or holds
under another number, are the likeliest; the move of the trade mark records between systems in November 2018 (U34)
is a candidate, not a finding. The financial-year counts of U5 (FY2018 and FY2019) and the growth rates of U25 that
span 2018 may be about 2.5% low there. Stage 2 flags 2018 in any trade mark series and reads Madrid counts across it
with care.

**D3 (disputes part of U13 and U48). IP Australia's "55.6% of resident applications were filed by individuals" (2022)
cannot be reproduced.** IP Australia writes that its firm-level aggregates "exclude the contributions of individual
applicants. In 2022, 55.6% of resident applications were filed by individuals rather than organisations"
(ipr-2023 p12), in a passage on standard patents. The lens gives 20.65% of 2022's resident standard applications with
an individual as the first founding applicant (U13 says 20.59% for FY2017 to FY2026, U48 21.53% by postcode), and
26.76% of their distinct founding applicants in Australia are individuals (`context.csv`). Neither base, applications
or applicants, comes near 55.6%, and nor do provisional applications, whose individuals' share is 34.08% (2024) and
48.25% (2025) (section 3). The same page says SMEs filed 69.6% of resident standard applications, which cannot sit
beside 55.6% from individuals on one base. So U13 and U48 stand on the lens's
evidence, but the conflict is recorded as disputed until IP Australia says what the 55.6% counts (section 8).

**D4 (context, no observation affected). Trade marks in force in 2005.** IP Australia counts 391,450 trade marks in
force in 2005 and 635,355 in 2017 (ipr-2019 p16); the lens's registered and not yet ended marks are 367,344 (0.9384)
and 645,872 (1.0166). 2017 agrees; 2005 is 6% lower, which fits U23's finding that trade mark ends before the late
1980s are recorded in batches and survivors, and IP Australia's count may include marks pending renewal. No
observation quotes a stock of marks in force, so nothing changes; U36's lifetimes start from complete cohorts.

---

## 5. Verdicts, observation by observation

### 5.1 Observations IP Australia's evidence can test

| # | Verdict | IP Australia's evidence | What follows |
|---|---|---|---|
| U1 | Corroborated | Annual applications for every type reproduce IP Australia's (section 3); the completeness U1 claims holds for 2014 to 2025 | Origin "known for 86.37%": for designs, IP Australia knows more than IP RAPID publishes (D1) |
| U3 | Consistent | The 2013 rush before Raising the Bar, and the 13% fall in 2014 (ipr-2015 p8); the innovation patent's closure (ipr-2022 p16) | None |
| U5 | Corroborated | Section 3; trade marks in 2018 apart (D2) | FY2018 and FY2019 trade marks may be 2.5% low (D2) |
| U6 | Corroborated | 2025: standard patents 30,448 against 30,348 (1.0033), trade marks 97,343 against 97,345, designs 10,303 against 10,296, provisionals 6,874 against 6,867 | None |
| U7 | Corroborated; designs qualified | Residents' standard patents, provisionals, trade marks and plant breeder's rights match (section 3); innovation patents 53.22% non-resident in 2016 against IP Australia's 54% (ipr-2017 p9); IP Australia: residents 9.3% of standard patents in 2025 (ipr-2026 p22) | Design shares among known origin are lower bounds (D1) |
| U8 | Corroborated; an explanation offered | IP Australia: 4,343 (2024) to 6,867 (2025), "one of the clearest structural shifts"; individuals "close to half", up from "around one-third"; 'new filers' 63% (42% in 2021 to 2024); self-filers 52% (19% to 27%); "consistent with reduced entry costs and faster drafting and search enabled by digital tools, including artificial intelligence" (ipr-2026 p21). Lens: 6,874; individuals 48.25% and 34.08%; new filers by applicant 68.85% (2025) against 56.02% to 60.07% (2021 to 2024), a jump in the same year (the lens's level is higher: an applicant counted by party id) | IP Australia's explanation is a hypothesis in its own words; U8's concentration (54 individuals with 10 or more, one with 375) is not in IP Australia's account, and fits its warning of "higher volumes of speculative filings". OQ5 narrows (section 8) |
| U10 | Corroborated (counts) | Grants match in all 10 years published; IP Australia publishes no grant rate by year of application | Rates themselves untested |
| U13 | Corroborated; one figure disputed | Origins: US applicants 12,374 (IP Australia) against 12,185 (2025), China 2,938 against 2,962; residents as in U7; private applicants 27% to 28% of residents' trade marks (ipr-2017 p36) against the lens's 26.29% to 28.39%. Disputed: individuals' share of resident standard patents (D3) | U13 stands; D3 goes to IP Australia |
| U14 | Corroborated | Pharmaceuticals, medical technology and biotechnology 33.3% of 2025's standard filings, a share that "has gradually deepened" (ipr-2026 p27); field counts within 2% in 7 of 9 years | None |
| U15 | Corroborated | States' shares within 0.2 points (2021, 2023, 2025) | None |
| U16 | Corroborated | The repaired state reproduces IP Australia's state shares in 2023 and 2025, when IP RAPID omits the state for 13.65% (FY2023) and 34.96% (from FY2024) of Australian standard patents | Repair 5 of ADR 0012 is validated |
| U25 | Corroborated | Annual counts (section 3); the 2009 fall "following the events of the Global Financial Crisis" (ipr-2017 p6); trade marks −11.2% in 2022 (ipr-2023 p6; U25: −11.2%); design records in 2024 and 2025 with non-residents 70.1% (ipr-2026 p57, p58); IP Australia's 2.5% average growth of standard patents in 2010 to 2019 (ipr-2020 p7) against U25's 2.0% a year (a compound rate; IP Australia does not say how it averaged) | Rates spanning 2018 for trade marks: D2 |
| U27 | Corroborated; wording clarified | Standard grants match exactly (section 3), peaking at 23,743 in 2016 among the years IP Australia published (2014 to 2025); 2024's 24% rise "due largely to productivity improvements in examination" (ipr-2025 p4). U27's 25,687 counts all patents granted (the timeline's series includes second-tier patents); standard patents alone are 23,744 | Quote standard grants from `rights`, all patents from `timeline`, and say which |
| U28 | Corroborated and extended | Raising the Bar: residents' applications fell 35% in 2014 (ipr-2015 p9; lens 3,122 to 2,028, −35.0%). The innovation closure: 7,844 applications in 2021, +71%, non-residents 78% of the growth (ipr-2022 p16; lens 7,833). And a response U28 does not list: residents' standard patents grew 24.8% in 2021 because applicants "bring forward standard patent applications" to keep the option of converting them into innovation patents (ipr-2023 p13); the lens's resident standard patents rise 2,403 to 2,998, +24.8% | Stage 2's closure window includes Australians' standard patents in 2021 and 2022 |
| U32 | Corroborated (recent certifications) | Design certifications 1,377, 1,540 and 1,448 match exactly | The history of milestones is untested |
| U33 | Corroborated | Median request for examination to acceptance 1.3 years "as of 2020" (ipr-2025 p9); lens 1.23 years for 2020's requests and 1.12 to 1.55 for those of 2014 to 2022 (`context.csv`; later requests are still in progress), beside U33's 422 to 516 days since FY2014. Applications with an examination request before 15 April 2013 kept the old law, "leading to an increase in granted patents as applicants expedited examination between 2013 and 2016" (erp15 p13), which U33's 44 days for FY2013 and U27's 2016 grant peak show | None |
| U36 | Corroborated (trade marks) | "The renewal rate after the first ten-year registration term has dropped from around 70 per cent in the 1980s to 50 per cent in the 2000s" (ipr-2019 p16); U36: 67.3% of 1983 to 1989 marks in force after 10 years, 46.9% of the 2000s'. For patents, IP Australia's commissioned study reads "the lifetime over which the applicant renews the patent" as a sign of its value (ipr-2025 p9) | Supports the owner's adoption of years in force as a working measure (answer A1 in `owner-questions.md`) |
| U44 | Consistent | "Domestic patenting is relatively concentrated in Australia. Around 3,100 businesses with active operations in Australia hold a domestic patent annually" (ipr-2023 p12); resident patenting "reflects activity by a relatively small subset of firms" (ipr-2026 p22) | None |
| U45 | Consistent; the lead's reading supported | IP Australia: resident trade marks reached a record 55,913 in 2025, +15.1% (ipr-2026 p39; lens 55,759). Counted by applicant, which needs no ABN, first-time resident trade mark filers rose from 22,838 (2024) to 28,626 (2025) in the lens (`context.csv`), while those linked to an ABN fell (U45: 11,318 in FY2024 to 7,384 in FY2026) | The fall is in ABN linking, not in filing; firm filing by year still stops at FY2024 until IP Australia says why (OQ7) |
| U48 | Disputed in part | Individuals' share of standard patents (D3) | As U13 |
| U52 | Corroborated (the firms named) | Aristocrat Technologies is IP Australia's leading domestic patent filer in 2017 (157), 2021 (71) and 2025 (123) (ipr-2018 p11, ipr-2022 p10, ipr-2026 p32); the lens: 159, 72 and 123. CSIRO, NewSouth Innovations, ResMed and Breville complete 2021's top five (ipr-2022 p10), the firms U52 finds behind single postcodes | None |
| U67 | Corroborated; the 2016 lead closed | IP Australia's own standard patent counts agree with the lens (section 3). Innovation patents: IP Australia reported 2,322 in 2016, +27%, from "a significant increase in non-resident applications of some 79 per cent" (ipr-2017 p9). The lens's 2,469 is 1.0633 of that, as in 2015 and 2017 (conversions, section 3), so the 1.331 against WIPO's 1,855 is mostly between IP Australia's count and WIPO's, and the 2016 rise was real | The lead is not an IP RAPID artefact; WIPO's utility model count for Australia is used with care |
| U69 | Corroborated (WIPO) | WIPO's page for Australia: 20th of 139, inputs 13th, outputs 24th, "between ranks 18 and 21" (wipo-gii-2026-australia p1). Same publisher as the data, so a check of the reading, not the source | None |
| U70 | Corroborated | Australians abroad: U70's 10,633 at every office less 2,542 at home is 8,091 in 2024, IP Australia's figure (ipr-2026 p34). China equal to Australians in 2024: IP Australia's China +13.4% to 2,938 in 2025 implies about 2,591 in 2024, beside residents' 2,578 (ipr-2026 p22, p23); in 2025 China leads (9.7% against 9.3%). The 222-day trade mark path rests on WIPO only; IP Australia publishes no trade mark times | None |
| U75 | Consistent with its caveat | IP Australia's firm-level research finds the industries intensive in all three rights "almost all concentrated in the Manufacturing and Wholesale Trade industries" (ipr-2020 p40): firms' own industries, including a service industry, which supports U75's warning that the crosswalk's 90.78% for manufacturing reflects leaving services out | A crosswalk with services (ALP's) stays a Stage 2 choice |
| U76 | Consistent | "Resident trade mark filers remain more concentrated in service-intensive sectors" (ipr-2026 p45); U76: Australians 66.99% to 79.75% of services divisions' trade marks, 47.46% to 58.24% of goods divisions' | None |
| U81 | Consistent | IP Australia names NewSouth Innovations as "the commercialisation arm of the University of New South Wales" among 2021's top five domestic filers (ipr-2022 p11) | Supports counting a university with its companies; OQ11 stands |
| U84 | Consistent | 21% of Australian universities' PCT applications in 2000 to 2015 were filed with a collaborator (ipr-2017 p27), beside U84's 24.3% to 34.2% of the institutions' standard patents filed with others. In 2025 "the reduced prominence of public research organisations and universities among the top domestic filers" (ipr-2026 p32): the institutions' share of resident standard applications was 10.02% (2022), 8.09% (2024) and 7.97% (2025) in the lens | None |
| U89 | Corroborated | PCT applications within 0.35% in 2020, 2022, 2023 and 2024; direct within 0.93% in 2019 and 2020 | None |
| U90 | Corroborated; the direct-filing lead supported | PCT share 73.4% (2022), 69.6% (2024) and 66.7% (2025) (ipr-2023 p11, ipr-2026 p26), within 0.34 points; "provisional patents and direct filings have expanded, particularly among domestic innovators" (ipr-2026 p19). Madrid: 56% of overseas trade marks in 2020 (ipr-2021 p12; U90's 57.2% in FY2020); Australians lodged 3 of 14,451 Madrid applications in 2015 (ipr-2016 p14), as U90's 97.9% to 99.1% direct shows | IP Australia explains the overall shift partly by country mix (fewer US filings, more Australian and Chinese); U90's rise is among Australians, so the mix does not explain it, and IP Australia reads it as a real change. "Priority claims recorded late" is not excluded |
| U91 | Consistent | "The share of Australian classes filed abroad through the Madrid system has increased, from 45.0% in 2019 to 56.6% in 2024" (ipr-2026 p54); 53% of Australians' trade mark applications abroad went through Madrid in 2021 (ipr-2022 p23). U91 counts marks taken abroad, a different unit | None |
| U97 | Corroborated | "In 2022, women constituted 14.6% of Australian inventors, the same level as in 2021", a participation rate "2 percentage points lower than the international average" (ipr-2023 p66, p67). Its 14.6% for 2021 is the WIPO figure U97 checked its estimate (14.9%) against, so IP Australia reads WIPO's data as U97 does. About 12% of unique Australian inventors on applications in Australia in 2016 (ipr-2022 p17), beside U97's 13.6% estimate for 2015 | None |
| U98 | Consistent | As U97: IP Australia's 14.6% (PCT, 2022) and about 12% (2016), beside U98's 14.34%, 12.43% and 12.75% | None |

### 5.2 Observations IP Australia's publications cannot test (66)

| Why | Observations |
|---|---|
| The corpus, the lens's structure and its repairs | U0, U2, U22, U23, U24, U31, U40, U88 |
| The register's own detail, which IP Australia does not publish in aggregate (statuses, holders, postcodes, attorneys, milestones, assignments, lapses) | U4, U9, U11, U12, U17, U18, U19, U20, U21, U26, U29, U34, U35, U37, U38, U39 |
| Firms, places and money from other sources (the ABR, the R&D Tax Incentive, AusTender, the Census and others) | U41, U42, U43, U46, U47, U49, U50, U51, U53, U54, U55, U56, U57, U58, U59, U60, U61, U62 |
| Other countries, industries and institutions from other publishers | U63, U64, U65, U66, U68, U71, U72, U73, U74, U77, U78, U79, U80, U82, U83, U85, U86, U87 |
| Google Patents families, citations and inventors | U92, U93, U94, U95, U96 |
| Prices | U30 |

Notes on some of them: U4 rests on the annual counts that section 3 corroborates. U11's 222-day trade mark peak is
corroborated by WIPO (U70), not by IP Australia, whose reports give no trade mark times. U20: IP Australia publishes
self-filing only for provisional applicants (52% in 2025, ipr-2026 p21), which IP RAPID cannot show, since it
publishes no agents for provisionals (ADR 0010). U34: no IP Australia publication mentions the fall in trade mark
expedite requests in November 2018, so OQ6 stays open; for patents, IP Australia reports that 41.9% of granted
patents had examination requested early and unprompted (ipr-2025 p10). U41 and U42: IP Australia's firm figures
(firms with IP rights cancelled their ABN less often, 25% against 35%, ipr-2016 p28; 3.2% of SMEs own IP rights,
erp10 p7) rest on BLADE and other periods, so they do not test the lens.

The tally, by each observation's main verdict: 23 corroborated (U1, U5, U6, U7, U8, U10, U13, U14, U15, U16, U25,
U27, U28, U32, U33, U36, U52, U67, U69, U70, U89, U90 and U97; U1, U7 and U27 with a qualification, U13 with one
figure disputed), 9 consistent (U3, U44, U45, U75, U76, U81, U84, U91 and U98), 1 disputed in part (U48) and 66 not
testable: 99 in all. None is contradicted.

---

## 6. IP Australia's conclusions that bear on the leads

What IP Australia concludes, how strongly it says it, and what Stage 1's evidence adds. None is adopted here.

| # | IP Australia's conclusion | Its strength, in its words | What Stage 1 adds |
|---|---|---|---|
| C1 | The provisional surge reflects digital tools, including AI, lowering entry costs (ipr-2026 p21) | "Consistent with"; "an important focus for ongoing analysis" | U8: the rise is broad (single-filing individuals 1,538 to 2,507) and concentrated (54 individuals filed 1,528); both fit, and neither proves it |
| C2 | Firms' first patent grant and first trade mark registration coincide with persistent gains in income and productivity (ipr-2026 p12 to p14) | "Dynamic associations, not definitive causal effects"; "selection effects are likely present" | Nothing to test: Stage 1 has no firm outcomes (BLADE is ruled out, OQ9). The Minister's foreword states it more strongly than the chapter ("businesses that register ... record substantially better rates", ipr-2026 p3) |
| C3 | Using fast-track options predicts renewal, commercialisation and follow-on patents; delays help small innovators (ipr-2025 p9 to p15) | A commissioned study (Motu and EPFL); observational | U34's expedited requests (1.87% to 10.31%) and U36's years in force are the same two measures: a Stage 2 pair that would replicate IP Australia's finding with open data |
| C4 | The innovation patent did not meet its policy goal for SMEs (ipr-2018 p10, ipr-2020 p14) | IP Australia's and the Productivity Commission's research | U7: second-tier patents' Australian share fell from 79.2% to 87.4% (FY1990 to FY2010) to 16.1% in FY2021; IP Australia: non-residents 8% (2000) to 47% (2019), China the second origin |
| C5 | Raising the Bar increased technological competition and follow-on innovation, unevenly across fields (ipr-2026 p15, p16; erp14) | Commissioned research | U28 and U33 show the rush and the early examination requests that kept applications under the old law: the timing any evaluation must allow for |
| C6 | Trade mark clutter is "not an immediate concern", though falling first renewals are a potential source (ipr-2019 p15, p16) | IP Australia's own measures | U36 corroborates the fall in renewals; Stage 1 cannot measure use |
| C7 | IP rights do not significantly raise market concentration (ipr-2020 p42; erp10) | Econometric, observational | Not testable here; Stage 1's concentration is of filing (U44, U52), a different thing |
| C8 | The 2021 surge in resident patents was brought forward by the innovation closure, and 2022's fall corrects it (ipr-2023 p13) | "Likely" | Corroborated by the counts (U28's extension) |
| C9 | China's patent filings in Australia halted in 2021 and fell 8.2% in 2022, most likely after China ended subsidies for filing abroad (ipr-2023 p12) | "Most likely reflects nonmarket factors" | Not in an observation; Stage 2's origin series (U13, U70) should allow for it |
| C10 | The rise in direct patent filing in 2025 partly reflects country mix (ipr-2026 p26) | Descriptive | U90: Australians' own direct filing rose, which mix cannot explain |
| C11 | Women are under-represented among Australian inventors, below the world average (ipr-2023 p65 to p68) | WIPO's PCT data | U97 and U98 agree on the level |
| C12 | University-industry collaboration is "not a crisis": Australia 13th of 35 OECD countries for university-industry PCT applications (ipr-2017 p20 to p27) | IP Australia's analysis of co-filed IP | U84's joint filing is the same kind of measure for Australian standard patents; Stage 2 can update it |

---

## 7. Decisions

Recorded in [ADR 0024](adr/0024-audit-against-ip-australia.md):

1. The benchmark (`analysis/audit/`) is kept, tested and rerun whenever the lenses are rebuilt; Stage 2 adds a row for
   any new IP Australia figure it leans on.
2. Comparisons with IP Australia use calendar years and `founding_australian` for residency.
3. Design shares among known origin are labelled lower bounds (D1).
4. 2018 is flagged in trade mark series (D2).
5. Second-tier counts include conversions from standard patents; IP Australia's editions before 2020 did not (U67's
   lead closed).
6. The innovation closure's event window in Stage 2 covers Australians' standard patents (U28).
7. First-time filers are counted by applicant (party id) beside ABNs from FY2025 on (U45).
8. Timeline grants include second-tier patents; standard grants come from `rights` (U27).
9. Expedited examination against years in force joins Stage 2's pairs (C3).
10. The notebook's observations are not rewritten: they quote the outputs above them, and IP Australia's figures are
    not among those outputs. The audit's verdicts live here, in the ADR, in the handover and in `stage-1-summary.md`,
    and the evidence atlas shows them on a page of their own, read from this record's tables (ADR 0025).

---

## 8. For the owner

1. **Three questions for IP Australia**, to add to the request already being made (OQ5 to OQ7): what base its "55.6%
   of resident applications were filed by individuals" (2022) uses (D3); why IP RAPID holds about 2,000 fewer Madrid
   trade marks for 2018 than its report (D2); and whether IP RAPID could publish the origin it holds for designs that
   IP RAPID leaves unknown (D1). Recorded as OQ12 to OQ14, and added to the request by the owner on 27 October
   2026.
2. **OQ5 (the provisional rise)** now has IP Australia's published reading: digital tools, including AI, lowering
   entry costs, with new filers 63% and self-filers 52% in 2025. The question to IP Australia narrows to the evidence
   behind it, and whether a few heavy filers (U8) are part of it. Reworded so by the owner on 27 October 2026.
3. **OQ7 (ABN linking)** narrows: IP Australia's record resident trade marks in 2025, and first-time filers counted by
   applicant, show the fall is in linking. What remains is whether ABNs are attached late or collected less.
   Reworded so by the owner on 27 October 2026.
4. **Two items in the request are now answered from IP Australia's reports:** its published counts, as a benchmark
   (this audit), and why IP RAPID holds more innovation patents in 2016 than WIPO's utility models (U67).

---

## 9. Limits

- **Not independent.** IP Australia's reports are built from its own register, as IP RAPID is, so agreement shows the
  lenses read the register as IP Australia does; it cannot show the register is right. The independent checks are
  WIPO's and the World Bank's (U67, U89), and they agree too.
- **Two reports are scanned.** Figures from the 2018 and 2021 editions come through OCR; each one used agrees with
  the lens or is explained, which checks both.
- **Calendar years.** The notebook's financial-year figures are not compared with IP Australia's directly; the
  benchmark recomputes calendar years from the same records.
- **Search, not a full read.** Beyond the 2026 report, the documents were searched by topic. A statement IP Australia
  makes in words the searches did not reach may be missed; the topics covered are listed in section 2.
- **What IP Australia does not publish** (holders, attorneys, lifetimes by cohort, regions below states, firms by ABN)
  leaves 66 observations untested, and they stand on Stage 1's own checks.

---

## 10. Since the audit (added 4 November 2026)

The sections above are the audit as it was made on 27 October 2026, and are left as they were. This section records
what has happened to each of its findings since, so that the atlas's page can say where each one now stands. It adds
no new comparison with IP Australia's figures; every figure below is quoted from the record named beside it.

**The benchmark still holds.** `python -m audit.benchmark`, run against the lenses as rebuilt on 4 November 2026,
gives the same 195 figures and the same 155 agreements (`tests/test_audit.py` checks the committed outputs against
the lenses). The benchmark reads IP RAPID's own origin (`founding_australian`), not the register's fills, so D1's
figures are unchanged by them.

**Scope.** The audit covered U0 to U98, the observations Stage 1 had on 27 October 2026. Stage 1 has since gained
U99 to U127 (the register's fills, the data gaps filled after Stage 2, and the review of 3 November 2026), and Stages
2 and 3 have added B1 to B63 and M1 to M38. None of these has been checked against IP Australia's published figures
in the same way.

**D1 (designs of unknown origin): settled in the lenses.** IP Australia's register gives a country for 25,018 of the
40,748 designs IP RAPID leaves without one (61.4%), Australia for 20,870 (`docs/audit-ipa-api.md`, V13). For 2021, 2023 and
2025, the lens's Australian designs plus the register's Australian owners are 2,601, 2,660 and 3,078, against IP
Australia's 2,595, 2,652 and 3,078. At the owner's decision the register's country now sits beside IP RAPID's in the
lenses (ADR 0029, `founding_australian_filled`). With it, 32.64% of designs filed FY2017 to FY2026 are Australian and
0.083% are of unknown origin, against 30.44% and 5.058% in IP RAPID alone (U102). So the filled share is no longer a
lower bound; IP RAPID's own share still is, and is shown beside it. OQ14 now asks whether IP RAPID could publish the
country the register holds.

**D2 (trade marks filed in 2018): IP RAPID is not the odd one out.** WIPO counts 15,943 designations of Australia in
2018, against IP RAPID's 15,836 Madrid marks (0.9933); the IP Report 2019's figures imply about 17,830, or 1.118 times
WIPO's count (`docs/recheck-oq6-oq7-oq13.md`, R9). IP Australia's own register counts 78,643 trade marks lodged in
2018 (Madrid 16,941) and 77,726 by filing date (Madrid 15,999), so neither of its dates gives the report's 79,490
(the lodgement date is 847 short; `docs/audit-ipa-api.md`, V11). Trade mark numbers 1,978,060 to 1,980,352, missing
from IP RAPID, were not used: 1 of 2,292 exists (V10). Three sources now stand against the report's 2018 figure. 2018
stays flagged in trade mark series, and OQ13 now asks what the report's count included.

**D3 (55.6% of resident applications filed by individuals): still open.** IP Australia has not yet answered OQ12;
U13 and U48 stand on the lens's evidence.

**D4 (marks in force in 2005): unchanged.** No observation quotes a stock of marks in force.

**Observations restated since, beside their first wording.** The register check (ADR 0028) and its fills (ADR 0029)
restated U7, U13, U34 and U45 in the notebook, with U99 to U104 beside them, and the later passes restated others
(ADR 0037, 0038, 0043). The audit's verdicts above are as they were made on 27 October 2026, against the observations
as they then read.

- **U45 and OQ7.** The register holds an ABN, or an ACN the ABR links to one, for 83.8% of the Australian
  organisations' trade marks filed since July 2024 with no ABN in IP RAPID (`docs/audit-ipa-api.md`, V12). U100 and
  U101 restore most of the link, and first observed filers are counted with the filled ABNs.
- **U34 and OQ6.** The register shows "Examination expedited" on 130 of 130 sampled priority-claiming trade marks
  filed FY2020 to FY2026, none of which has the event in IP RAPID (V14): IP RAPID stopped publishing it in November
  2018 (U103).

**IP Australia's conclusions, as Stages 2 and 3 have tested them since.** None is adopted; each is an association.

- **C1 (the provisional surge).** Australian individuals' provisionals filed in FY2025 were followed by a complete
  application within 12 months 6.66% of the time, against 12.24% to 14.15% in FY2022 to FY2024 (B38). With the filer's
  state, volume, history and month held, the fall is -6.42 points (-6.25 raw); among individuals who also filed in the
  earlier years it is not detected, so it is in new and heavy filers (M35). Late recording of claims is not ruled out
  (B38, OQ18).
- **C3 (fast-track examination and renewal).** Stage 2 found expedited standard patents slightly more often in force
  after 10 years, pooled, in both periods (B13). With the filer, field, route, cohort, co-filers and classes held
  together, the link is not detected in FY2010 to FY2016 (a hazard ratio of 1.021) and reverses in FY2003 to FY2009
  (1.124: more likely to end); Australian individuals' expedited patents are more likely to end in both periods (1.264
  and 1.249) (M5). The open data do not repeat the commissioned study's finding once other factors are held.
- **C5 (Raising the Bar).** With each series' trend and season held, Raising the Bar (April 2013) brought a rush of
  Australians' standard patents (0.605 in logs) and a lower level after it (a step of -0.334, about 28% fewer a
  month), which then recovers (M25).
- **C8 (the 2021 rise brought forward by the innovation patent's closure).** The closure (August 2021) shows a rush of
  1.459 and a step of -3.17, both beyond every placebo month (B37).

**The questions for IP Australia** (OQ12 to OQ14) were reworded by the owner after the register check (A13, 27
October 2026): OQ13 and OQ14 now ask what the report counted and whether IP RAPID could publish what the register
holds. All three are still open (`docs/owner-questions.md`).

---

## 11. Stage 1's later observations and Stages 2 and 3 (added 4 November 2026)

**What this is.** The same check, made of the 130 observations sections 1 to 9 did not cover: Stage 1's U99 to U127
(29: the register's fills, the data gaps filled after Stage 2 and the review of 3 November 2026), Stage 2's B1 to B63
(63) and Stage 3's M1 to M38 (38), at the owner's decision (A35; [ADR 0052](adr/0052-audit-extended-to-stages-2-and-3.md)).
**Whose:** Claude's. **Strength:** every verdict is descriptive. Stages 2 and 3 read associations, two at a time and
then with other factors held; IP Australia publishes few of either, so most of these observations cannot be tested,
and where its research reaches the same question it usually does so on other data (the ABS's BLADE) or with another
design. A "consistent" verdict then says the two point the same way, not that one confirms the other's size.

### 11.1 How it was done

1. **The same documents, searched by the new observations' topics:** the register's fills, provisionals and their
   inventors, fees and fee changes, divisionals, renewals and lapses by origin, expedited examination, filing abroad and
   patent families, citations, women inventors by field, inventors in Australia and owners overseas, firms (size, age,
   industry, R&D, contracts, income), places below the states, countries, industries, research institutions and
   research funding, the economy (GDP, the dollar, interest rates, the labour market), policy breaks, the PBS and court
   judgments. Each passage used is cited by document and page; IP Australia's analytical note on trade marks and the
   business cycle is `note-tm` (*note-tm-leading-indicator*).
2. **Like for like, as before** (section 2): 13 figures are added to `analysis/audit/published.csv`, recomputed by
   `analysis/audit/benchmark.py` on IP Australia's definitions. A fee is read as in force on 1 March of the edition's
   year, as the report went to press; a change is a percentage change on the year before, compared as a difference in
   percentage points (within 1 point).
3. **Verdicts on the same scale** (section 2). The tables below are read by the atlas's audit page, as sections 5.1
   and 5.2 are.

### 11.2 What agrees

All 13 new figures agree (`analysis/audit/output/benchmark.csv`): the benchmark now holds 208 published figures, of
which 168 agree; the 195 of sections 1 to 10 are unchanged (155 agree). With the commissioned study's share added for
M40 (section 11.8), 209 figures, 169 agreeing.

| Measure | Years published | Agree | Ratio (or difference) | Observations |
|---|---|---|---|---|
| Australians' design applications, with the register's country filling IP RAPID's gaps | 2014, 2021, 2023, 2025 | 4 | 0.9943 to 1.0004: 2,615, 2,596, 2,649 and 3,072 against 2,630, 2,595, 2,652 and 3,078 (IP RAPID's own origin: 2,342, 2,331, 2,358 and 2,653) | U99, U102 |
| The official fees, as the IP Report 2015 lists them | 2015 (6) | 6 | 1.0000: a standard patent application $370, a design $250 and its examination $420, a plant breeder's right $345 and its examination $1,610, a trade mark $120 a class | U108, U125 |
| Divisional applications in 2019 | 2019 (3) | 3 | direct divisionals -2.92% against -2.9%; direct originals -0.54% against -1.2%; divisionals 86.21% of the fall in residents' applications against 87% | B15, M26 |
| Granted patents asked for examination early and unprompted (added with M40, section 11.8) | 2004 to 2016 (1) | 1 | 41.39% against 41.9% (a difference of -0.51 points) | M40 |

### 11.3 Verdicts, observation by observation: those IP Australia's evidence can test

| # | Verdict | IP Australia's evidence | What follows |
|---|---|---|---|
| U99 | Corroborated (designs) | With the register's country, Australians' designs are 2,615, 2,596, 2,649 and 3,072 in 2014, 2021, 2023 and 2025, against IP Australia's 2,630, 2,595, 2,652 and 3,078, within 0.57% (section 11.2); IP RAPID's own origin gives 2,342, 2,331, 2,358 and 2,653. IP Australia publishes no counts of ABNs, so the ABN fills are not tested | The fills settle D1 for designs (section 10) |
| U100 | Consistent | IP Australia reports record resident trade marks in 2025, 55,913, up 15.1% (ipr-2026 p39), so filing did not fall as IP RAPID's ABNs did; with the register, 90.9% of FY2026's trade marks have a filer's ABN, against IP RAPID's 59.9% | None |
| U101 | Consistent | As U100. Counted by applicant, which needs no ABN, first-time resident trade mark filers rose from 22,838 (2024) to 28,626 (2025) (`context.csv`), as U101's filled counts rise (14,728 in FY2024 to 19,730 in FY2026) | None |
| U102 | Corroborated | As U99: the filled counts match IP Australia's within 0.57% in all four years published, where IP RAPID's own origin falls short (D1) | The filled share is not a lower bound; IP RAPID's own share is (section 10) |
| U105 | Consistent | IP Australia's yearly provisional counts agree with IP RAPID's within 0.25% in all 11 years published (section 3), as a complete record would | None |
| U108 | Corroborated | The IP Report 2015 lists the fees then in force (ipr-2015 p35 to p37): a standard patent application $370, a design $250 and its optional examination $420, a plant breeder's right $345 and its examination $1,610, a trade mark $120 a class, each online. The fee lens gives all six exactly on 1 March 2015 | The fee series rests on the regulations (ADR 0031); its 2015 level is now checked against IP Australia's own statement. IP Australia publishes no history of its fees, so U109 to U111 are not tested |
| U114 | Consistent | IP Australia's firm-level research puts professional, scientific and technical services among the three industries with the most businesses owning IP rights (ipr-2020 p40) and among the three where patenting is concentrated (erp15 p38): firms' patenting is not confined to manufacturing, as the crosswalk without services would have it | Supports reporting both crosswalks (B53, B54) |
| U115 | Consistent | IP Australia, from WIPO's data, reports that Australians file several times as many patent applications abroad as at home: 9,012 against 3,061 in 2013 (ipr-2015 p17); 8,091 abroad in 2024 (ipr-2026 p34). That fits U115's Australian families that never reach IP Australia | IP Australia counts applications, U115 families |
| B10 | Consistent (designs) | IP Australia finds that non-residents register, certify and renew more designs than Australians in the product classes where the two differ most (erp08 p3, p14; ipr-2019 p19), as B10 finds overseas organisations' designs most often in force after the first renewal. IP Australia publishes no trade mark renewals by origin | None |
| B13 | Consistent | IP Australia's commissioned study (Motu and EPFL): applicants who use the options to speed up examination are more likely to renew, commercialise and build on their patents (ipr-2025 p9, p13). B13 finds expedited standard patents slightly more often in force at 10 years, pooled, in both periods | See M5 |
| B15 | Consistent; the divisional measure corroborated | IP Australia attributes 2019's fall in standard applications to divisionals: among direct filings, divisionals fell 2.9% and originals 1.2%, and 87% of the fall in residents' applications was in divisionals (ipr-2020 p7, p8); the lens gives -2.92%, -0.54% and 86.21% (section 11.2). IP Australia's rankings count divisionals, and "applicants differ in their approaches to divisional filings" (ipr-2026 p32) | B15's shares by decade are not published; the measure behind them reads the register as IP Australia does |
| B17 | Consistent | "Representation of women on patents varies across technology fields": women are named on 61% of PCT applications in biotechnology and 59% in organic fine chemistry and in pharmaceuticals (worldwide, 2022; ipr-2023 p66), as B17 finds the field matters more than the filer | None |
| B22 | Consistent | IP Australia (BLADE): firms that own IP rights are on average older (13 years against 8) and larger (105 employees against 6) than firms without (ipr-2020 p39), as B22 finds filing going with age and being a company | Age is on the record at the build date (M8's caveat) |
| B23 | Consistent | IP Australia's BLADE study: R&D expenditure is "positively and significantly associated" with patents filed, granted and retired, with age, size, industry and state held (erp15 p36, p39) | IP Australia gives no size of link to set beside B23's "only weakly" |
| B37 | Consistent | IP Australia reports the rush before Raising the Bar and the fall after it (ipr-2015 p8, p9; erp15 p13), and the rush before the innovation patent closed (ipr-2022 p16; ipr-2023 p13): C5 and C8 (sections 6 and 10) | None |
| B38 | Consistent | IP Australia warns of "higher volumes of speculative filings" in its account of 2025's provisionals (ipr-2026 p21), which fits fewer followed up within 12 months (6.66% against 12.24% to 14.15%) | Late recording of priority claims is still not ruled out (OQ18) |
| B41 | Consistent | IP Australia's firm-level research: manufacturing "alone accounts for eight of the top ten patent-intensive industries" (patents per employee; erp10 p3), as B41's allocated patents favour manufacturing (314.6 per 1,000 businesses in FY2024). IP Australia counts firms' own industries, B41 what the patents protect (U75) | None |
| B45 | Qualified | IP Australia's study of publicly funded research organisations, each followed over time: more ARC funding goes with more patent applications, and collaborative (Linkage) grants more than others; for collaborative grants, $1 million more a year goes with three more PCT and six more provisional applications (ipr-2018 p30, p31). B45, across universities in each of two periods, agrees in part: ARC grants per 1,000 works go with patents per work (0.637 and 0.628). Its share of ARC grants with industry partners is not seen to go with the share of patents filed with others (0.127 and -0.074, intervals reaching 0.50 and 0.43): a different outcome from IP Australia's (applications, not joint filing) and a different design | Not seeing the collaborative link across about 40 universities does not rule out IP Australia's effect within institutions; see M23 |
| B47 | Consistent; an explanation offered | IP Australia's analytical note: the Trade Marks Act 1995 let one application cover several classes, which Jensen and Webster (2004) held behind the drop in trade mark filings in 1996, and the note scales filings from 1996 up by a factor of 1.11 (note-tm p3). B47's clearest break is that Act (January 1996) | The 1996 fall is in applications: a count of classes would not show it (M34) |
| B50 | Consistent | IP Australia's BLADE study: with age, industry, state and year held, medium and large firms are more inclined to file patents, "with large firms standing out as the most active filers" (erp15 p16, p38) | None |
| B51 | Consistent | The same study: patenting is concentrated in manufacturing, wholesale trade and professional services, and is positively correlated with manufacturing, mining and wholesale trade with size held (erp15 p38), as B51 finds industry sorts patenting more than size | None |
| B54 | Consistent | As U114 | None |
| B55 | Consistent | IP Australia's counts of Australians' patent applications abroad are steady (9,012 in 2013, 9,253 in 2014, 8,737 in 2016), two thirds through the PCT, a split "largely stable over the last 10 years" (ipr-2015 p17; ipr-2016 p11; ipr-2018 p13). That fits B55's reading that the fall in "Australia only" patents is a gap in older records, not a change in practice | IP Australia counts applications abroad, not families |
| B56 | Qualified | IP Australia's analytical note: trade mark filings are procyclical and lead the economy; they are cointegrated with real GDP, and a 10% rise in a quarter predicts 1.8% more real GDP the next quarter and 2.7% the quarter after (note-tm p1, p4). B56 compares changes in the same quarter: overseas applicants' trade marks and designs go with GDP at 0.051 to 0.205, and Australians' trade marks at 0.207, then -0.201. It does not test a lead | A lead of one or two quarters is not tested here (section 11.6) |
| B63 | Qualified | As B56. Overseas applicants' trade marks move against unemployment (-0.561, then -0.224), as procyclical filing would, and the note ranks the unemployment rate among the five best leading indicators of recessions (note-tm p3); Australians' trade marks move against employment (-0.182 and -0.332), which procyclical filing does not predict for changes in the same quarter. The note also finds COVID-19's shock brought a trade mark boom in 2020 and 2021 (note-tm p3) | As B56 |
| M5 | Qualified | The commissioned study's "speeding up" includes asking for examination early and unprompted, which 41.9% of granted patents do (ipr-2025 p10), as well as fast track and the Patent Prosecution Highway; M5's expedited examination is IP RAPID's request, 1.87% to 10.31% of requests (U34). And the study finds that for small innovators "delays tend to predict stronger post-grant outcomes" (ipr-2025 p9), as M5's Australian individuals' expedited patents are more likely to end (1.264 and 1.249) | M5 does not dispute the study: the two measure different things. Early unprompted requests against years in force would be the like-for-like test (section 11.6) |
| M7 | Consistent | As B17: the field sorts women's representation among inventors (ipr-2023 p66) | None |
| M8 | Consistent | As B22 and B23. IP Australia's BLADE study also finds that among firms using the patent system, younger firms file more patents a year (erp15 p16, p38), which fits M8's caveat that part of the age gap is time on the record | None |
| M11 | Consistent | As B50 and B51 | None |
| M17 | Consistent (WIPO) | WIPO's page for Australia: its strongest indicators include school life expectancy (2nd) and tertiary enrolment (7th), its weakest production and export complexity (72nd) (wipo-gii-2026-australia p7), as M17 places Australia: little manufacturing and exporting, much tertiary education. Same publisher as part of the data, so a check of the reading, not the source | None |
| M23 | Qualified | As B45 | As B45 |
| M25 | Consistent | C5 (sections 6 and 10): IP Australia reports the rush to file before Raising the Bar and the 35% fall in residents' applications in 2014 (ipr-2015 p8, p9) | None |
| M26 | Consistent | As B15: the lens reproduces IP Australia's divisional figures for 2019 | None |
| M29 | Consistent (form and age) | As B22. IP Australia finds IP owners more profitable per employee ($48,368 against $23,404) but slightly less per invested capital (4.4% against 4.8%) (ipr-2020 p39, p40): profit, not the reported income of M29's large taxpayers, which is not tested | None |
| M34 | Consistent; an explanation offered | As B47: M34 finds the Trade Marks Act 1995 "a fall, not a rush" (Australians' step -0.495), and IP Australia's note gives the reason it adopts, multi-class applications | Read the 1996 step as a change in what one application covers, not a response to price |
| M35 | Consistent | IP Australia: new filers were 63% of provisional applicants in 2025 (42% in 2021 to 2024) and self-filers 52% (ipr-2026 p21); M35 finds the fall in follow-up among new and heavy filers, not among those who filed before | C1 (section 10) |
| M36 | Qualified | As B56: with block resampling no cycle pair is clear of zero in both periods; IP Australia's note finds a lead, which M36 does not test | As B56 |
| M39 | Consistent; the size differs | Added with A36 (section 11.8). IP Australia's note (note-tm p1, p4): trade marks cointegrated with real GDP, and 10% more trade marks predicting 1.8% and 2.7% more GDP one and two quarters on. M39: cointegrated over 1983Q1 to 2023Q2 (p 0.018); in levels 3.069% and 3.296%, over a window from 1983, not 1970; in changes, with GDP's own growth held, 0.038 (0.014 to 0.063) over 1983 to 2023 and not detected after 2008 (p 0.316) | The note's lead holds in direction and the shared path is found; once GDP's own momentum is known the lead is small, and not detected since 2008 |
| M40 | Disputed in part | Added with A36 (section 11.8). The commissioned study (ipr-2025 p9, p10, p13): applicants who speed up examination, including by asking for it early and unprompted (41.9% of granted patents), are more likely to renew, commercialise and build on their patents. The lens reproduces the measure (41.39%, section 11.2), but with the filer, field, route, cohort, co-filers, classes and expedited examination held, those patents are more likely to end in a given year after grant (hazard ratios 1.276 and 1.383) | The study's outcome and model are not in IP Australia's report, so this disputes its direction on its own measure, not its model; a question proposed for IP Australia (OQ28) |

### 11.4 Observations IP Australia's publications cannot test (93)

| Why | Observations |
|---|---|
| The register check, the lens's structure and the screens of each lens | U103, U104, U106, U126, B1, B2, B3, B4, B20, B21, M12 |
| The register's detail by filer, which IP Australia does not publish (agents, grant, lifetimes, reach, citations, inventors, routes, owners abroad) | U107, B5, B6, B7, B8, B9, B11, B12, B14, B16, B18, B19, M1, M2, M3, M4, M6, M27 |
| Fees over time, and filing's response to them | U109, U110, U111, U125, B48, B49, M28 |
| Firms matched to other registers (the ABR, WGEA, AusTender, the ATO) | U112, B24, B25, B26, M9, M10, M30 |
| Places below the states | U117, U118, B27, B28, B29, B30, B31, B58, B59, M13, M14, M15, M16, M31, M32 |
| Countries | U120, B32, B33, B34, B35, B61, M18, M33 |
| The economy, the labour market, the courts and the timeline's other series | U113, U116, U123, U124, B36, B39, B52, M19, M20 |
| Industries, from the ABS's statistics | U119, B40, B42, B43, B53, B57, B60, M21, M22, M37 |
| Research institutions' research and commercialisation | U121, U122, U127, B44, B46, B62, M24, M38 |

Notes on some of them: U103: no IP Australia publication mentions trade mark expedite requests (OQ6 stays open).
U107: IP Australia's women inventors (14.6% of Australian inventors on PCT applications in 2022, ipr-2023 p67; about
12% in 2016, ipr-2022 p17) are of other applications; U107's "about one in five" on provisionals is a population IP
Australia does not report. B5: IP Australia publishes self-filing only for provisional applicants (52% in 2025,
ipr-2026 p21). U125 and U110: the fees' level is corroborated for 2015 (U108), their history is not published. B24 and
M29: IP Australia's profit figures (above) are not large taxpayers' income. B33: WIPO's page for Australia does not
rank business entry, trade marks or research articles among its strengths, so B33 is not checked by it. B52: IP
Australia's study of exporters (erp11 p3, p4) finds that trade mark holders' exports respond less to the exchange
rate, which concerns sales abroad, not filing. Places: IP Australia publishes states only (for example, the ACT the
largest filer per head, 137 standard applications per million residents in 2014, ipr-2015 p22). B62 and M24: IP
Australia's finding that research funding raises patenting is within institutions (C15 below), and M24 builds research
spending into its exposure. U124: IP Australia publishes no count of IP judgments.

The tally, by each observation's main verdict: 3 corroborated (U99, U102 and U108), 28 consistent (U100, U101, U105,
U114, U115, B10, B13, B15, B17, B22, B23, B37, B38, B41, B47, B50, B51, B54, B55, M7, M8, M11, M17, M25, M26, M29, M34
and M35), 6 qualified (B45, B56, B63, M5, M23 and M36), none disputed and none contradicted, and 93 not testable: 130
in all. With sections 1 to 10, all 229 observations of the three notebooks have a verdict. With M39 and M40, added the
same day (section 11.8): 3 corroborated, 29 consistent, 6 qualified, 1 disputed in part (M40), none contradicted and 93
not testable, 132 in all; with sections 1 to 10, all 231.

### 11.5 IP Australia's conclusions that bear on Stages 2 and 3

As in section 6: what IP Australia concludes, how strongly it says it, and what the stages add. None is adopted here.

| # | IP Australia's conclusion | Its strength, in its words | What Stages 2 and 3 add |
|---|---|---|---|
| C13 | Trade mark filings are procyclical and lead real GDP by one or two quarters (note-tm p1, p4) | "Predicts"; a cointegration test and a regression; an analytical note's "preliminary results" | B56, B63 and M36 compare changes in the same quarter, not a lead: qualified |
| C14 | Larger and older firms are more likely to use IP rights; among firms using the patent system, younger and larger ones file more; R&D spending goes with patents (ipr-2020 p39; erp15 p38, p39) | "Our analysis does not imply causation" (erp15 p6) | B22, B23, B50, B51, M8, M11 and M29 point the same way on other registers |
| C15 | Public research funding raises research organisations' patenting, and collaborative grants more (ipr-2018 p30 to p32) | "Likely to boost"; models within each organisation over time; its effect is "far outweighed by the importance of factors internal to funding recipients" | B45 finds ARC grants per work going with patents per work across universities; B45 and M23 do not see the collaborative-grant link, or ARC success once size and citations are held: a different design, so qualified |
| C16 | The 1996 fall in trade mark filings reflects the Trade Marks Act 1995's multi-class applications (note-tm p3, after Jensen and Webster 2004) | Attributed, and adjusted for in the note's own series | B47 and M34 find the Act's fall; this is its likely mechanism |

### 11.6 Decisions and items for the owner

Recorded in [ADR 0052](adr/0052-audit-extended-to-stages-2-and-3.md):

1. The benchmark is extended by 13 figures (208 in all, 168 agree) and its test allows an observation of any of the
   three notebooks.
2. Every observation of the three notebooks now has a verdict; for the 130 added, 3 are corroborated, 28 consistent, 6
   qualified, none disputed or contradicted, and 93 not testable.
3. Three measures the stages rest on are corroborated for the first time: the register's origin for designs (U102),
   the fee lens's level (U108) and the divisional flag (B15, M26).
4. The notebooks are not rewritten: IP Australia's figures are not among their outputs. The verdicts live here, in the
   ADR, in the handover and on the atlas's audit page.

**For the owner** (direction, OQ27): IP Australia's research suggests three tests the stages have not made, each free
and quick with the lenses as they are. (a) Trade marks' lead on real GDP (C13), with the timeline's quarterly series,
beside B56 and M36. (b) Early, unprompted examination requests against years in force (C3, M5), the commissioned
study's wider measure of speeding up. (c) Research funding within institutions over time (C15, B45, M23). The
recommendation: (a) and (b) as additions to Stage 3, since they use its methods and its data; (c) after Stage 3, since
the institutions' yearly funding would need the NSRC and ARC series lined up first.

### 11.7 Limits

Section 9's limits hold. Two more: IP Australia's firm findings come from the ABS's BLADE, which this project cannot
use (OQ9), so a "consistent" verdict on a firm observation is about direction, on other data; and Stage 3's
associations held together have no published counterpart, so a verdict on one checks the signal it revisits, not its
model.

### 11.8 M39 and M40: two tests IP Australia's research suggested (added 4 November 2026)

At the owner's decision (OQ27, answered A36; [ADR 0053](adr/0053-two-tests-from-ip-australias-research.md)), the first
two of section 11.6's tests were added to Stage 3 (notebook 3, sections 1.11 and 5.8). Their verdicts are in section
11.3's table, beside the observations they follow.

- **C3, the commissioned study's finding on speeding up (M40).** IP RAPID records each direction to request
  examination, so the study's own measure, a request made before any direction, can be built: it covers 41.39% of
  granted patents, against the study's 41.9% (section 11.2). But those patents are more likely to end, not less, with
  the filer, field, route, cohort, co-filers, classes and expedited examination held (1.276 in FY2010 to FY2016, 1.383
  in FY2003 to FY2009). So M40 is **disputed in part**: the measure is reproduced, the direction is not. The study's
  outcome ("the lifetime over which the applicant renews the patent") and its controls are not in the report, so its
  model is not contradicted. M5's "qualified" is answered: on the study's wider measure, too, asking for examination
  sooner does not go with a patent kept longer. B13's "consistent" stands for what it compared (raw shares).
- **C13, trade marks' lead on real GDP (M39).** Found in direction: trade marks and real GDP share a long-run path
  (p 0.018 over 1983Q1 to 2023Q2), and in levels 10% more trade marks go with 3.069% and 3.296% more GDP one and two
  quarters on (the note: 1.8% and 2.7%, over a window from 1970). But in changes, with GDP's own growth held, the lead
  is small (0.038, interval 0.014 to 0.063) and not detected after 2008 (p 0.316). M39 is **consistent; the size
  differs**. B56, B63 and M36's "qualified" is answered: the lead they did not test exists, and is small.
- **Proposed for IP Australia (OQ28, the owner's decision whether to ask):** how did the commissioned study measure the
  renewal lifetime, and what did it hold, so that M40 can be set beside it like for like?
