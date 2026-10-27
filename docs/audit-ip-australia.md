# Audit: Stage 1 against IP Australia's published evidence

**What this is.** A check of Stage 1's observations (U0 to U98, `analysis/notebooks/01_univariate.ipynb`) against what
IP Australia has published: its Australian IP Reports 2015 to 2026, its economic research papers and analytic notes,
and (for a few observations) the WIPO publications held beside them. The aim is to validate or invalidate each
observation wherever IP Australia's evidence allows. The decisions it leads to are recorded in
[ADR 0024](adr/0024-audit-against-ip-australia.md).

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
   behind it, and whether a few heavy filers (U8) are part of it.
3. **OQ7 (ABN linking)** narrows: IP Australia's record resident trade marks in 2025, and first-time filers counted by
   applicant, show the fall is in linking. What remains is whether ABNs are attached late or collected less.
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
