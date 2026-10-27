# IP RAPID checked against IP Australia's live register

**Date:** 2026-10-27. **Asked by:** the owner, once API access to IP Australia's register came through: "write the
code so we can query it again in the future", then "use this access to fill in the gaps in the dataset and just
generally check whether IP RAPID is actually accurate". **Decision record:** ADR 0028.

**Data.** The register as IP Australia's Trade Mark, Patent and Design Search APIs gave it on 27 October 2026
(production; `docs/ip-reg-api/`), against the IP RAPID release in the corpus (19 October 2026). Harvest:
`uv run corpus run ipa_api` (corpus source `ipa_api`: 50,772 calls, about two hours). Comparison:
`uv run python -m audit.api_check --live`; every table quoted is in `analysis/audit/output/api/`. One other source
is used, in V12: the ABR (`abr/abns`), to turn the register's ACNs into ABNs.

**What was fetched.** Every trade mark and design number the register's searches find, by year (2,594,082 numbers),
and whole records for: a random sample of IP RAPID's applications (3,000 trade marks, 2,000 designs, 2,000 patents);
the trade marks behind OQ7 (34,635, plus 5,899 from FY2023 for comparison); the designs behind OQ14 (40,748); the
missing trade mark numbers of OQ13 (2,292); and every number one side has and the other's search does not find.
Patents cannot be listed: the patent search ignores its fields and returns at most 5,000 numbers.

Every observation is **descriptive**: it says what the two records hold, not why. Shares come with 95% (Wilson)
intervals where the sample is the base.

## In short

| | Question | Answer |
|---|---|---|
| Complete? | Does IP RAPID hold every right the register holds? | **Yes, to within a week.** 99.94% of IP RAPID's trade marks and every dated design are found by the register's searches; what the register has extra was filed after the release (V2, V3) |
| Accurate? | Do IP RAPID's fields say what the register says? | **Yes.** Where both have a value, dates, classes, owners' places, filing routes and statuses agree in 99.7% to 100% of a random sample of every right (V5 to V9). Two differences are definitions, not errors: Madrid trade marks are dated by IP Australia's notification, PCT patents by their national phase entry (V6, V9) |
| OQ6 | Did expedited examination of trade marks claiming priority stop in November 2018? | **No: IP RAPID stopped publishing it.** The register's own history shows "Examination expedited" on every sampled priority-claiming mark filed since FY2020 (130 of 130), none of which has the event in IP RAPID (V14) |
| OQ7 | Is the ABN missing because it is not collected? | **No: it is collected but not published.** For 83.8% of the Australian organisations' trade marks with no ABN in IP RAPID since July 2024, the register holds an ABN (55.5%) or an ACN the ABR links to one (V12) |
| OQ13 | Were trade mark numbers 1,978,060 to 1,980,352 used? Why is 2018 short? | **The numbers were not used** (1 of 2,292 exists, V10). **The register agrees with IP RAPID about 2018**, by either of its dates; neither gives the IP Report 2019's 79,490 (V11) |
| OQ14 | Does IP Australia hold the origin of designs IP RAPID leaves unknown? | **Yes, and it explains the gap with IP Australia's figures.** The register gives an Australian owner for 270 (2021), 302 (2023) and 425 (2025) of them; IP Australia counts 264, 294 and 425 more resident designs than the lens (V13) |

## The connection

**V1. Access works for both environments, with three quirks the client handles.** The `DEV` credentials are
production's and the `TEST` ones the test host's; each is refused by the other host. The test host holds an old,
partial copy (design 202010001 is missing), so only production is used as evidence. Each API allows 600 requests a
minute. About half of production's patent calls answer 403 ("Invalid Client") or 500 at random and succeed when
sent again (the harvest logged 256 retries for its first 250 patents). Searches return at most 10,000 numbers, and several
big searches at once make the trade mark search answer 500 for minutes. `docs/ip-reg-api/README.md` has the details
and how to query the register again.

## Is IP RAPID complete?

**V2. Trade marks: IP RAPID has 99.94% of what the register's searches find, and the rest is the week since the
release.** By year of application (`completeness.csv`): IP RAPID 2,335,064, the register's searches 2,336,216, both
2,333,568.

- **In the register only (2,648):** 2,257 were lodged from 17 October 2026, after the release's last application
  (16 October). The other 391 were lodged earlier but entered later (13 in 2025, 11 in 2024).
- **In IP RAPID only (1,496):** 888 are not in the register at all, 886 of them IP RAPID's status "voided" (876
  filed in 2023). The other 608 are in the register, but with no lodgement date, so a date search cannot find them
  (443 of them "Protected").

**V3. Designs: every dated design is in both.** IP RAPID 268,782, the register's searches 257,866, both 257,637. In
the register only: 229, 228 of them filed in 2026. In IP RAPID only: 11,145, of which 11,143 have no application date
in IP RAPID and no filing date the register's search can find (fetched by number, all are there; 11,099 of them
have no owner in either); 2 are not in the register.

**V4. A week changes about 1.3% of trade marks.** The register changed 29,558 trade marks and 1,512 designs between
the release (19 October) and the harvest (27 October). They are left out of the field comparison; for patents the
register cannot be asked, so a few patent differences may be timing.

## Is IP RAPID accurate?

**V5. Trade marks: a random sample of 3,000 agrees field by field.** 2,998 were found; 37 changed after the release,
leaving 2,961 (`fields.csv`). Where both have a value:

- application date (marks not through Madrid) 2,567 of 2,567; priority date 2,961 of 2,961; date entered on the
  register 1,981 of 1,981; Nice classes 2,961 of 2,961; convention priority claimed 2,961 of 2,961; Madrid 2,960 of
  2,961; number of owners 2,958 of 2,961; any owner in Australia 2,958 of 2,961;
- one owner's country 2,814 of 2,814 (interval 99.86% to 100%), state 1,681 of 1,681, postcode 1,681 of 1,681;
- status: 2,961 of 2,961, comparing IP RAPID's status with the register's status group (`status.csv`).

IP RAPID has a registration date for 145 marks where the register shows none, and a postcode for 9.

**V6. A Madrid mark's application date in IP RAPID is the day IP Australia was notified, not the international
registration's date.** In the sample, IP RAPID's date equals the register's IR notification date for 393 of 393 Madrid
marks and its lodgement (international registration) date for none. Over all marks, 90,005 of IP RAPID's 311,568
Madrid marks fall in a later calendar year than the register's lodgement date. Both are defensible; they must not be
mixed. The lenses use IP RAPID's date, as IP Australia's own counts do (ADR 0024).

**V7. Owners' ABNs: the two records hold different sets.** In the trade mark sample IP RAPID has an ABN for 1,119
marks and the register for 252; where both have one, they agree for 152 of 161 (94.4%; interval 89.7% to 97.0%).
IP RAPID has one for 958 marks the register shows without one, and the register for 91 that IP RAPID lacks. So the
register's ABN is not a replacement for IP RAPID's, but it fills some of its gaps (V12). Designs: 56 of 56 agree; IP
RAPID 516 more, the register 21 more.

**V8. Designs: a random sample of 2,000 agrees.** 7 changed after the release, leaving 1,993. Application, priority,
registration and certification dates, Locarno class, number of owners, one owner's state and postcode, and ABNs: 100%
where both have a value (for example application date 1,902 of 1,902). Status: 1,992 of 1,993. The one field that
differs is where IP RAPID has no country: the register gives a country for 139 single-owner designs that have none
in IP RAPID, and so "any owner in Australia" differs for 143 (all of them unknown in IP RAPID, Australian in the
register). IP RAPID has a postcode for 469 designs whose owner the register gives without one.

**V9. Patents: a random sample of 2,000 agrees, once the PCT date is read as IP RAPID defines it.** All 2,000 found.
Type 2,000 of 2,000; number of applicants 2,000 of 2,000; application date of patents not through PCT 1,226 of
1,226; priority date 1,237 of 1,237 where the register has one (where it has none, IP RAPID gives the application
date: 705 of 706); grant (sealing) date of standard patents 717 of 717; IP RAPID's main IPC subclass is among the
register's for 1,533 of 1,533. Status 1,997 of 2,000 (the 3 are moves a week could make: filed to lapsed, granted to
ceased, accepted to granted). For PCT patents, IP RAPID's application date is the national phase entry date (715 of
717) and its earliest filing date the international filing date (717 of 717), which the register calls the filing
date: the convention N06 records.

## The gaps

**V10. OQ13: trade mark numbers 1,978,060 to 1,980,352 were not used.** Of the 2,292 numbers missing from IP RAPID,
the register holds one (1,978,200, a voided Madrid designation from 2015). The rest answer "not found" (`gaps.csv`).
This closes the second half of OQ13.

**V11. OQ13: the register agrees with IP RAPID about 2018, by either of its dates.** Trade marks in 2018
(`madrid.csv`): by the register's lodgement date 78,643 (Madrid 16,941); by its filing date 77,726 (Madrid 15,999); IP
RAPID 77,496 (Madrid 15,836); the IP Report 2019 79,490 (Madrid about 17,830, implied). The lodgement-date count is
the nearest to the report's, 847 short, and its Madrid count 889 short; it differs from IP RAPID's by year in both
directions (Madrid: +1,105 in 2018, +2,366 in 2016, −2,289 in 2023), as notification dates move marks between years.
So the register does not explain the report's 2018 figure either; with WIPO's count (ADR 0027), three sources now
stand against it.

**V12. OQ7: the register holds an identifier for most of the ABNs IP RAPID leaves out.** Trade marks filed from July
2024 whose first current applicant is an Australian organisation without an ABN in IP RAPID: 34,635, all in the
register (`gaps.csv`).

| Filed | Records | Register's ABN | ACN, linked to one ABN by the ABR | Either |
|---|---:|---:|---:|---:|
| FY2023 (comparison) | 5,899 | 2,502 | 1,031 | 3,533 (59.9%) |
| FY2025 | 11,443 | 5,811 | 3,354 | 9,165 (80.1%) |
| FY2026 | 16,888 | 9,655 | 4,742 | 14,397 (85.2%) |
| FY2027 (to 26 October) | 6,304 | 3,749 | 1,730 | 5,479 (86.9%) |
| From July 2024 | 34,635 | 19,215 (55.5%) | 9,826 | 29,041 (83.8%) |

19,198 of the register's 19,215 ABNs are in the ABR. So since July 2024 IP Australia has collected an ABN or ACN for
most of these applicants, and IP RAPID does not publish it. Before July 2024 IP RAPID also left some out (FY2023:
59.9% fillable), but there were far fewer such marks (U45's break).

**V13. OQ14: the register gives a country for most designs IP RAPID leaves unknown, and that closes the gap with IP
Australia's resident counts.** Designs with no applicant country in IP RAPID: 40,748. The register gives a country
for 25,018 (61.4%), Australia for 20,870. Where it does not, it has no owner at all: 11,099 undated designs and 1,350
of 1,366 from the 1970s. By year of filing, the register's Australian owners among them are 286 (2019), 292 (2020),
270 (2021), 232 (2022), 302 (2023), 420 (2024) and 425 (2025). The audit (D1) found that IP Australia counts 264
(2021), 294 (2023) and 425 (2025) more resident designs than the lens; the lens plus these would be 2,601, 2,660 and
3,078 against IP Australia's 2,595, 2,652 and 3,078. (A caveat: the lens counts a founding applicant in Australia,
and the register gives the current owner.)

**V14. OQ6: the register still expedites the examination of marks claiming convention priority; IP RAPID stopped
publishing it in November 2018.** In the trade mark sample (`expedite.csv`):

- **Filed FY2009 to FY2018, with a priority claim:** IP RAPID's expedite event on 128 of 134; the register's history
  shows no expedite entry for any of them.
- **Filed FY2020 to FY2026, with a priority claim:** IP RAPID 0 of 130; the register's history shows "Examination
  expedited" on 130 of 130.
- **Without a priority claim:** FY2009 to FY2018, IP RAPID 30 of 740 and the register 34 (30 the same marks); FY2020
  to FY2026, IP RAPID 34 of 644 and the register 162 (every one of IP RAPID's 34 among them).

So since the move to the new system, the register records "Examination expedited" for every priority-claiming mark
and for about a quarter of the others, and IP RAPID publishes only the expedites an applicant asked for ("Expedite
Work Initiated"). Before it, IP RAPID's event came from the old system and the register's history does not show it.
U34's fall in November 2018 is a change in what IP RAPID publishes, not in how IP Australia examines. The sample is
small for any one year (13 to 22 priority-claiming marks a year); the pattern holds in every year.

## Added after the owner's questions (2026-10-27)

**V15. Inventors: the register fills the two holes in Google Patents' coverage, and agrees with it elsewhere.** The
corpus's inventors come from Google Patents (ADR 0022). For the patent sample (`inventors.csv`):

- **Standard patents filed before 1970:** the register names inventors for 210 of 300; Google Patents for none (it
  holds 9 of these patents, without inventors).
- **Provisional applications filed since 2000:** the register for 167 of 183; Google Patents for 1 (provisionals are
  not published). Before 2000 neither has any (123 of 123).
- **Standard patents filed since 1970:** the register for 1,265 of 1,282, Google Patents for 1,230; the register
  alone for 49, Google Patents alone for 14. Where both name inventors, the counts are the same for 1,129 and Google
  Patents' larger for 87 (it counts the family's inventors across every office's publication); the register's is
  never the larger.
- **Innovation and petty patents:** the register for 55 of 55, Google Patents for 46.

Over IP RAPID, the two holes are 283,917 standard patents filed before 1970 and 161,429 provisionals filed since
2000. At the sample's rates the register would name inventors for roughly 200,000 and 150,000 of them (projected).
Fetching them would take days: production's patent API answers about half its calls with an error, and the harvest
fetched about 115 patents a minute (1,500 in about 13 minutes, from its log). The errors cost time, not accuracy: every sampled patent
was fetched in the end. The register gives inventors' names only, no countries, so their places would have to come
from elsewhere.

**V16. The designs with no date are numbered 1973 to 1982 and are empty shells.** A design number begins with its
year. IP RAPID has 11,126 undated designs without a country (`gaps.csv`); the register gives a country for 27. Of the
other 11,099, 11,098 are numbered 1973 to 1982 (1,028 to 1,655 a year, but 63 in 1980 and 104 in 1982) and one
2016, and none has an owner in either record (`design_location.csv`). (An earlier version of this page called them
old without checking; their numbers bear it out.)

**V17. Of the 15,730 designs the register leaves without a country, 15,154 have no owner on record at all.** By
period (`design_location.csv`):

- **No owner in IP RAPID or the register: 15,154.** 11,099 undated designs (V16), 1,350 from the 1970s, 2,703 from
  the 1980s and 2 from the 2010s. 1,208 of them still have an attorney or other party on record (1,205 from the 1980s), but an
  Australian attorney acts for foreign owners too, so it says nothing about where the owner was.
- **An owner but no country: 576** (10 from the 1970s, 196 from the 1980s, 370 since). 275 have a clue: an ABN (86),
  a postcode (26), "Pty" in the name (41), or a name that IP RAPID gives a single country on other rights (232, of
  which 75 Australia). The last is a name match, so it is an inference, not a record.

So the register's 61.4% (V13) is close to all that can be located from IP Australia's data. Of the rest, 96% are
pre-1990 designs with no owner on record. They could only be traced from the published journals of the time, if at
all.

## What it means

1. **IP RAPID can be trusted as a copy of the register.** Its omissions are the week since the release and records
   with no dates; its fields agree with the register's to within the sample's precision. No observation rests on an
   error in IP RAPID's fields.
2. **Its gaps are in what it publishes, not in what IP Australia holds.** ABNs and ACNs (OQ7), design applicants'
   countries (OQ14) and expedite events (OQ6) are all in the register. The corpus now holds them for the rights
   fetched (`ipa_api/trade_marks`, `designs`; owners' names in `owners`, R2).
3. **What changes is the owner's call** (ADR 0028): whether to attach the fills to the `rights` lens (U45, the design
   origin shares, U34), and how the request to IP Australia is reworded.
