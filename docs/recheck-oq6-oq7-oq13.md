# OQ6, OQ7 and OQ13 rechecked on a fresh IP RAPID release

**Date:** 2026-10-27. **Asked by:** the owner, before taking the three questions to IP Australia: "double check a fresh
pull from the IP RAPID data to ensure it's not just being misclassified". **Decision record:** ADR 0027.

**Data.** IP RAPID's release of 26 October 2026 (`2026-10-26T00:34:12`), downloaded from data.gov.au and read
as published (every column as text), without the corpus or the lenses: `application.csv` (4,371,313 rows),
`application_links.csv` (3,869,594), `party_activity.csv` (12,530,473) and `application_events.csv` (49,390,311). The
corpus's copy is a week older (19 October). Two other sources are used, each in one place: ASIC's company register (`asic/companies`) in
R14, and WIPO's statistics on Madrid designations (the API the corpus's `wipo_ipstats` reads) in R9. Script: `analysis/audit/recheck.py`; every table quoted is in `analysis/audit/output/recheck/`.

Every observation here is **descriptive**: it describes what the register records, not why.

## In short

| | What Stage 1 said | Does it hold on the fresh release? | What changes |
|---|---|---|---|
| OQ6 | Trade mark expedite requests fell from about 1,400 a month to about 230 in November 2018 | **The numbers hold; the reading changes.** Almost the whole fall is one kind of mark: before the move between systems, 97% of marks claiming an overseas filing date (convention priority) carried an "expedited examination" event; after it, almost none do. Other marks barely changed | It is very likely a recording change. The question becomes narrower and easier to answer |
| OQ7 | Fewer Australian organisations' applications carry an ABN since mid-2024 | **Holds, and is sharper.** The break is in July 2024, mostly in applicants new to IP Australia. Newly registered companies dropped from about 90% to 10% with an ABN. The ABNs exist (ASIC's register has them). Two years on, they have not been filled in | Not a misclassification. "Added later" is unlikely; "not collected for new customers" is likely |
| OQ13 | IP RAPID holds 1,994 fewer trade marks for 2018 than the IP Report 2019 counted, all Madrid | **Holds exactly, but WIPO sides with IP RAPID.** WIPO's own count of the Madrid designations of Australia in 2018 is 15,943, against IP RAPID's 15,836 (99.3%), with no 13% rise. A block of 2,292 application numbers from around New Year 2019 is missing from every table, but WIPO's count suggests these were not 2,000 real marks | The IP Report 2019's 2018 count, not IP RAPID, is probably the odd one out. The question asks what that count included |

## OQ6: trade mark expedite requests in November 2018

**R1. The fresh release has the same counts as Stage 1.** Trade marks filed in FY2010 to FY2018 with an expedite
request: 16.67% to 19.69%. Since FY2020: 3.08% to 3.97% (`oq6_share_by_fy.csv`). That is U34's range. Requests by
month: 1,417 in October 2018, 604 in November and 240 in December (`oq6_exam_events_by_month.csv`). So the observation
is not an artefact of how the corpus processed the data.

**R2. The step is on the day the systems changed.** The old system's last trade mark examination event is on
9 November 2018, and the new system's first is on 13 November. On weekdays in the first week of November there were 19
to 62 expedite requests a day, plus 221 on 5 November. From 13 November it was 4 to 20 a day
(`oq6_cutover_days.csv`). The ordinary examination request also stops: 5,188 in October and 1,528 in November 2018,
then none at all. The new system does not record that event for trade marks (`oq6_exam_events_by_month.csv`).

**R3. The fall is almost all in marks that claim convention priority.** Convention priority means a mark claims the
filing date of an earlier application, usually overseas. Requests per month (`oq6_requests_by_month_and_priority.csv`):

- **Marks without a priority claim:** 216 to 285 a month from July to October 2018, 230 in November, and 155 to 292 a
  month in 2019. No step.
- **Marks with a priority claim:** 1,088 to 1,331 a month from July to October 2018, 374 in November, 0 in December,
  and 0 to 7 a month in 2019.

**R4. Before the move, nearly every priority-claiming mark was "expedited". Afterwards, almost none was.** By
financial year of filing (`oq6_share_by_fy.csv`):

- **With a priority claim:** 95.97% to 97.81% from FY2009 to FY2018 had the event; 0.06% to 0.16% from FY2020.
- **Without one:** 4.81% to 6.11% from FY2009 to FY2018 and 3.60% to 4.87% from FY2020. This is a gentle downward
  drift, with no break at November 2018.
- **Australian filers without a priority claim:** 6.28% to 7.34% from FY2009 to FY2018, and 4.77% to 6.19% from
  FY2020.

The same pattern holds in every group of filer (`oq6_share_by_group_and_side.csv`), comparing marks filed in the two
years before 13 November 2018 with those filed after it, up to June 2021:

| Filer | Without priority: before, after | With priority: before, after |
|---|---|---|
| Madrid | 0.24%, 0.01% | 97.70%, 0.01% |
| Direct, overseas | 2.14%, 2.78% | 94.84%, 0.30% |
| Direct, Australian | 6.21%, 5.59% | 86.52%, 2.39% |

**R5. What it means.** A share near 97%, held for over 20 years, tied to one feature of the application and gone on
the day the records moved, does not look like applicants' choices. The likeliest explanation is that the old system
recorded something about convention-priority marks under the expedite event code, such as a fast handling queue that
IP Australia ran itself. Applicants did not ask for it. Requests from applicants, as best the data can show them (marks
without a priority claim), held steady across the move. This is a strong lead, not a finding: only IP Australia can say
what the old event code meant.

**What changes for the question.** OQ6 becomes: "Before November 2018, about 97% of trade marks claiming convention
priority carried an expedited-examination event, and almost none have since. Did the old system record those marks'
handling under that event, rather than applicants' requests?" A yes would close OQ6. U34's trade mark series could then
be compared across 2018, as long as marks with a priority claim are left out.

## OQ13: 2018's trade marks, and the missing Madrid applications

**R6. The fresh release holds the same 2018 shortfall.** Trade marks filed in 2018 total 77,496, of which 15,836 are
Madrid and 61,660 direct (`oq13_by_year.csv`). That is the audit's count (D2) to the mark, against IP Australia's
79,490. The neighbouring years are 2017 (76,621; Madrid 15,844) and 2019 (75,657; Madrid 17,742). Madrid filings in
2018 run at 925 to 1,789 a month, with no empty month. December 2018 is 1,146 (`oq13_madrid_by_month.csv`). So it is not
a missing month, and not a mark dated into the wrong year: 2017 and 2019 agree with IP Australia within 0.05%.

**R7. A block of application numbers from around New Year 2019 is missing from IP RAPID.** Trade mark numbers are
issued in order. Between 1,800,000 and 2,079,999, a block of 10,000 numbers has 283 to 668 missing (3% to 7%), apart
from the two blocks the gap below falls in (`oq13_numbers_by_block.csv`). These would be numbers never used, or records not published. The block from
1,970,000 has 2,316 missing. They are in two runs: 1,978,060 to 1,978,607 (548 numbers) and 1,978,609 to 1,980,352
(1,744). The numbers either side were filed on 31 December 2018 and 2 January 2019. No other gap between 1,800,000 and
2,140,000 is longer than 331 (`oq13_longest_gaps.csv`). Only one number in the range appears anywhere in IP RAPID, and
no Australian trade mark links to any of the others (`oq13_gap_anywhere.csv`).

**R8. What the numbering gap could mean.** The two runs total 2,292 numbers. At the usual rate, 3% to 7%, about 70
to 160 of them would be missing, so roughly 2,100 to 2,200 are missing beyond the usual. That is close to the 1,994
marks IP RAPID lacks, and it falls at the year end, seven weeks after the records moved. But the numbers alone cannot
show what they were, and R9 weighs against their being 2,000 Madrid marks. The likelier reading is a range the new
system skipped.

**R9. WIPO's own count agrees with IP RAPID, not with the IP Report 2019.** WIPO's statistics give the designations of
Australia recorded in its international register each year, in new registrations and in later designations
(indicator 6, data of October 2026; `oq13_wipo_designations.csv`). They were 15,780 in 2017, 15,943 in 2018 and 17,573
in 2019. IP RAPID's Madrid marks are 0.9884 to 1.0121 of WIPO's count in every year from 2014 to 2024, apart from 2023
(1.0662). For 2018 the ratio is 0.9933. The IP Report 2019's figures imply about 17,830 Madrid applications in 2018
(IP RAPID's 15,836 plus the 1,994). That is 1.118 times WIPO's count, and a 13% rise that WIPO's count (+1.0%) does
not show. Where IP Australia published a Madrid count that the audit could check (2015, 2020, 2021, 2023, 2024 and 2025), it
agrees with IP RAPID within 0.1% (`analysis/audit/output/benchmark.csv`).

**R10. What it means.** The 1,994 marks are probably not missing from IP RAPID. More likely, the IP Report 2019 counted
2018 differently, or counted something extra. That report was prepared early in 2019, a few months after the records
moved, so double counting during the move is one possibility. TM-Link, IP Australia's own trade mark data released in
2020, has the same 2018 count as IP RAPID (77,468 marks, 15,807 Madrid), and has no records in the gap but one. WIPO's
register itself (Madrid Monitor) could list the individual registrations, but its terms of use forbid automated
queries and bulk downloads (sections 5 and 6), so it was not searched.

**What changes for the question.** OQ13 becomes: "WIPO records 15,943 designations of Australia in 2018, and IP RAPID
holds 15,836 Madrid marks, but the IP Report 2019 implies about 17,830 (+13%). What did the 2018 count in the IP Report
2019 include, and does IP Australia still stand by 79,490? (And were trade mark numbers 1,978,060 to 1,980,352 ever
issued?)"

## OQ7: ABNs on Australian organisations' applications

**R11. The fall in ABNs holds, and it starts in July 2024.** Among trade marks filed by Australian organisations (the
founding applicant is an organisation in Australia), the share with an ABN is 84.0% to 85.8% from FY2020 to FY2024.
It is 71.7% in FY2025, 59.8% in FY2026 and 54.0% so far in FY2027 (`oq7_abn_by_fy.csv`). Stage 1's U45 counted these
slightly differently (84.1%, 71.4%, 59.9%), and the result is the same. By month of filing
(`oq7_tm_abn_by_month.csv`), the share holds at 82.2% to 87.1% until June 2024. It then falls: 79.2% in July, 75.7% in
August, 63.3% by June 2025 and 51.8% in October 2026. Designs fall from 88.9% (FY2024) to 77.9% (FY2026), and
patents from 88.9% to 67.4%.

**R12. It is not a misclassification of who files, or where the ABN is kept.**

- **Type of applicant:** organisations make up a nearly steady share of Australian trade mark filers: 35,314 of
  46,464 trade marks (76.0%) in FY2020, 37,108 of 49,872 (74.4%) in FY2024 and 42,477 of 59,342 (71.6%) in FY2026
  (`oq7_tm_australian_filers_by_type.csv`). The organisations themselves are still counted; it is their ABN that
  goes missing.
- **Where the ABN sits:** an ABN belongs to the applicant (the party), not to the application. Of 927,766
  organisation applicants, 214 have an ABN on some of their records but not others
  (`oq7_party_abn_consistency.csv`). Counting an ABN held by any other party to the application except attorneys
  (owners, opponents and so on) adds 0.0 to 0.5 points, and nothing to the trend (`oq7_abn_on_any_role.csv`).
- **The same applicant elsewhere:** an applicant with no ABN on a recent application has none on any other
  application either.

**R13. The fall is among applicants new to IP Australia.** Count an applicant as new if it first appears within 30
days of the filing (`oq7_abn_by_fy.csv`). For new applicants, the share of trade marks with an ABN was 80.0% to 83.0%
from FY2022 to FY2024. It is 59.2% in FY2025, 42.5% in FY2026 and 37.1% in FY2027. For applicants seen before, it is
86.9% to 88.5% in FY2020 to FY2024 and 77.7% in FY2026. Some of those applicants first appeared after July 2024 without
an ABN. Patents and designs show the same split: new patent applicants 77.3% to 79.0% (FY2020 to FY2024), then 29.7%
(FY2026).

**R14. The companies have ABNs. IP RAPID does not hold them.** Matched by exact name to ASIC's register, among
Australian proprietary companies ("Pty Ltd") filing trade marks (`oq7_tm_pty_in_asic.csv`):

- **Matches:** 80.0% of the FY2026 trade marks with no ABN in IP RAPID belong to a company that ASIC lists with an ABN.
- **New companies:** 75.2% of those companies were registered after 1 July 2024, against 5.2% for the companies whose
  ABN IP RAPID does hold.
- **By company age** (`oq7_tm_pty_by_company_age.csv`): companies under a year old at filing had an ABN on 89.0% to
  90.2% of their trade marks in FY2022 to FY2024. In FY2025 it was 29.8%, in FY2026 10.1% and in FY2027 8.2%. For
  older companies it was 91.7% to 92.1%, then 83.2% in FY2026. Where an application has more than one Australian
  company as founding applicant, the first name alphabetically is matched.

**R15. It is not filled in later, at least within two years.** If ABNs were attached after filing, the oldest months
would have recovered by now. They have not. Trade marks filed in July 2024 stand at 79.2% with an ABN, more than two
years later, against 82.2% to 87.1% before (R11). Companies under a year old that filed in FY2025 stand at 29.8% (R14).

**What it means.** The fall is not a misclassification. From about July 2024, new customer records at IP Australia
mostly stop carrying an ABN, and the applicant record is not updated later. Newly registered companies are the
clearest case. Possible causes include a change in how new customers are set up (a new portal or form, or the ABN made
optional), or a change in what IP RAPID publishes. Only IP Australia can say which.

**What changes for the question.** OQ7 becomes: "From July 2024, applicants new to IP Australia mostly have no ABN in
IP RAPID: 89% of trade marks from newly registered companies carried one in FY2022 to FY2024, against 10% in FY2026,
though ASIC's register shows the companies have ABNs. Did something change in July 2024 in how new customers are set
up, or in what IP RAPID publishes? Is the ABN collected but not published?"

## What the recheck does not change

- **U34 and U45 stand as Stage 1 wrote them.** The fresh release reproduces their figures. The recheck explains more of
  each, but revising observations is the owner's decision (ADR 0026). Meanwhile:
  - trade mark expedite shares are compared only on one side of November 2018 (U34);
  - firm filing by year is compared only to FY2024 (U45);
  - 2018 is flagged in trade mark series (D2).
- **The corpus is a week behind the release used here.** The counts that both cover agree. Stage 2 can refresh it with
  `corpus run iprapid`.
