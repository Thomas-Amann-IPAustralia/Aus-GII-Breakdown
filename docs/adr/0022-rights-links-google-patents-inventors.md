# 0022: The last three rights attachments: the links, Google Patents and the inventors

**Date:** 2026-10-26. **Whose:** Claude's (the owner asked for the three remaining `rights` attachments, 2026-10-26);
the owner can overturn any of it. It carries out the review's B4 (Google Patents) and the plan's links and inventors
attachments, and adds two WIPO indicators to the corpus for the checks. The evidence is in
`analysis/notebooks/01_univariate.ipynb`, sections 1.8.3 to 1.8.5 (observations U88 to U98).

**Context.** After the parties (ADR 0013) and the events (ADR 0015), three planned attachments to the `rights` lens
were left: how each right came to Australia (`iprapid/links`), each patent's worldwide family (`google_patents`), and
the inventors behind it (`google_patents_inventors`). Two known problems stood in the way. IP RAPID labels every PCT
number, and many other offices' priority numbers, as Australian (`analysis/README.md`), so the links' own country
field cannot say where a priority was filed. And inventors' gender is estimated from first names with WIPO's
dictionary, whose quality varies by country; the plan asked for the estimates to be checked country by country against
WIPO's published shares, above all for China and Korea, before any use.

**Decision.**
1. **The links: eight columns.** `filing_route` takes the first of these that applies:
   - standard and second-tier patents: `pct` (the national phase of an international application), `divisional`,
     `convention` (a priority filed abroad), `australian_priority` (claiming only an Australian application, usually a
     provisional) or `direct`;
   - trade marks: `madrid` (an international registration designating Australia), `divisional`, `convention` or
     `direct`; designs: `divisional` (including a design excluded from an earlier application under the Designs Act
     2003, which IP RAPID links as `exclusive_parent` from 2004, when its `divisional_parent` links stop), `convention`
     or `direct`;
   - empty for provisional applications, which claim nothing, and plant breeder's rights, which have no links.

   Beside it: `priority_claims`, `priority_office` (the earliest priority's office), `australian_priority`,
   `divisional`, `pct_number`, `pct_office` (the receiving office, read from the PCT number) and `madrid_export` (an
   Australian trade mark that is the basis of a Madrid application). Only a right's own links count; the `*_child`
   links are the other side of the same pairs.
2. **A patent priority's office is read from its number,** not IP RAPID's label: `au` for an Australian application
   number (ten digits, year first) or an associated provisional; the receiving office for a PCT number; IP RAPID's
   label otherwise; empty where the label is `au` or `wo` and the number is neither (0.7% of standard patents with a
   priority). 93.88% of PCT numbers and 15,568 convention priorities with other offices' numbers are labelled `au` in
   the source. Trade mark and design priorities keep IP RAPID's label, which is sound for them. Placeholder link dates
   (1800, 1900) are not used to order priorities.
3. **Google Patents: six columns** (`family_id`, `family_priority_date`, `family_offices`, `family_granted_us`,
   `family_citations`, `family_citations_5y`), joined on Google's Australian application number (`au_application`) with
   designs (kind S) left out. 734 numbers fall in two families; the lower `family_id` is taken, so that every build
   picks the same one. A family's measures are the whole family's, so a divisional shares its parent's.
4. **The citation follow-up flag (F38a):** `family_citations_5y` is empty for families first filed after 22 April
   2020, whose five years, and the 18 months before citing applications are published, are not complete at the
   October 2026 release.
5. **The inventors: eight columns,** from `family_inventors` (one publication per family, ADR 0008): counts in
   Australia, abroad and of unknown country, `invented_in_australia` (three-valued), and the expected numbers of women
   and men. A family's inventors are counted for each of its Australian applications.
6. **The gender estimates are used for inventors in Australia only.** Against WIPO's share of women among inventors in
   PCT applications (2016 to 2023), the estimate for Australia is within 0.8 points (14.6% against 13.8%), and the
   estimates for the Netherlands, Spain, New Zealand, Finland and Ireland are within 2 points; but the median country
   is 4.5 points high, China 11.2 and Korea 21.3. So:
   - levels of women's share are read for inventors in Australia, and compared over time;
   - for other countries, only within one country over time, never as levels and never across countries;
   - for China and Korea, not at all.
   `inventors_women_expected` and `inventors_men_expected` stay in the lens for every patent, with this rule in the
   register's note.
7. **Two WIPO indicators join the corpus** (`wipo_ipstats`): direct applications and PCT national phase entries by
   office and origin (patent indicators 1a and 1b, `office_origin`), and the share of women inventors in PCT
   applications by origin (PCT indicator 15, `pmh`). The loader now reads exports already in the raw folder rather than
   fetching them again, so the other indicators' values are unchanged (checked: every earlier row is identical). The
   `national_indicators` table carries them, the women's share with the unit `percent`.

**Evidence.** The links' PCT route equals WIPO's count of PCT national phase entries at IP Australia within 0.4% in
every year from 1995 to 2024 except 2006 (0.981) and 2008 (1.007), and the other standard patents equal WIPO's direct
applications within 1.9% (U89). 94.81% to 99.23% of standard patents filed in each decade since the 1980s find their
Google Patents family (U92).

**Consequences.**
- The `rights` lens has 74 columns (29 core, 12 from the parties, 11 from the events, 8 from the links, 6 from Google
  Patents and 8 from the inventors). A test checks the new columns' consistency.
- Patents filed only in Australia rarely carry inventors' countries in Google Patents (Australian publications give
  none), so `invented_in_australia` is empty for about a third of Australian filers' standard patents, almost all
  filed only in Australia: shares of patents "invented here" are among those whose inventors' countries are known.
- Provisional applications are rarely published, so they rarely have a family or inventors.
- Still not done: sizing the families of Australian inventions filed only abroad that Google's selection misses (the
  review's F07), which needs WIPO's patent families by origin; and the 7-digit numbers of the 1990s and 2000s that do
  not match (F06), now 1% to 5% of standard patents in those decades.
