# Stage 2 summary: two variables at a time

**Status (2026-10-28):** Stage 2 of the exploratory data analysis is complete, in
`analysis/notebooks/02_bivariate.ipynb` (observations B1 to B46; section 8 is the short version of this document).
The method is ADR 0030. Every observation is an association (observational) or a description: none is a cause.
The evidence atlas (`evidence/`) has Stage 2's pages (ADR 0035, 2026-10-29); they go live when the branch is published.

## 1. In brief

- **The screen found what Stage 1 led us to expect, and sorted it.** Every pair of every lens was measured on one
  0-to-1 scale; a pair counts as a lead only if it is at least small (0.1), survives the correction for the number of
  pairs, holds in a second decade or half, and is not two versions of one measure. Most leads are the mechanics of the
  IP system or one broad gradient of development (income, education, R&D, business density) that runs through places
  and countries alike. The signals below are what is left once those are set aside.
- **Representation goes with outcomes.** Australian individuals' standard patents filed without an attorney are
  granted about 36 points less often, in both decades and among examined applications too; Australians' trade marks
  with no agent before the first renewal are less often in force after it (31.7% against 50.8% with an attorney; read
  "at any time", the gap was larger, since an agent added at the renewal counts) (B6, B10). The direction of cause is
  open: an abandoned application may never appoint an attorney, and a renewal can bring one. (Restated 2 November
  2026, ADR 0041: it read "Representation matters for outcomes" and "renewed far less".)
- **Some inventions made here are filed, or now held, from overseas.** One patent in seven made in Australia is filed from overseas
  (B16); Australian-founded patents now held only overseas are more often the wide and granted ones (a higher rate, not
  most of them; B19), with no clear difference by the filing firm's age, though those filed before the firm's first
  registration are the most often (B26). These compare two endpoints, not transfer histories, and say nothing of
  where value goes (restated 2 November 2026; the heading, "Value made here is often owned or used elsewhere", too, in
  pass 6); 3% to 5% of
  the US patents citing Australian research have Australian links (B46).
- **Australian organisations' patents reach fewer offices and are cited less, mostly because of that reach, yet
  within the same reach they are more often still in force at 10 years** than overseas organisations' (two to four
  offices 71.8% against 65.1%; five or more 75.6% against 66.5%; no difference among Australia-only patents), so the
  three signals disagree and none is read as value alone (B8, B11, B12; A22). Reach and citations hold for FY2010 to
  FY2019; the older decade's family records are incomplete, so its apparent narrowing of the gap is mostly a records
  gap (B55; restated 2 November 2026; "narrower but kept longer" restated in pass 6, ADR 0041).
- **Where filing happens** follows advantage (1.7 to 1.9 times the standard patent rate per standard deviation of
  IRSAD, unadjusted; 1.44 and 1.49 with remoteness in the model), remoteness and business mix, not one firm (B29 to B31); among firms, company form, age and cities, with R&D
  spend linked only weakly to patenting, and about half of R&D claimants with no filing linked to their ABN, mostly
  private companies of 3 to 10 years: a group to examine, not proven non-filers (B22, B23; restated 1 November 2026,
  ADR 0036).
- **Across countries** IP follows R&D and income; Australia's business R&D fell from 13th to 20th in the OECD, its
  patenting near what that predicts in 2016 to 2020 (104.9%, inside a wide interval; B61's ranks are a different
  analysis, not a shortfall); within a decade, changes in R&D barely move patenting (B33, B34).
- **Policy leaves clean breaks:** two rushes, three steps and the 1995 pauses are far outside placebo dates (B37), the
  starting points for Q5's natural experiments.
- **Women among inventors** vary by field (4.2% in civil engineering to 26.9% in biotechnology) more than by filer;
  on provisionals, organisations' inventors include about 5 points more women than individuals' (B17, B18).

## 2. How it was done

- **One scale** (`bi.association`): |Spearman's rho| for two numbers, the rank correlation ratio for a number and a
  category, bias-corrected Cramér's V for two categories. For a yes/no variable all three are |rho|.
- **Four tests for a lead** (`bi.replicate`): strength 0.1 or more; Benjamini-Hochberg false discovery rate under 5%;
  the same again, same direction, in a replication sample; not related by construction (`screens.yaml`'s groups).
- **Samples:** rights by decade (FY2010-19 against FY2000-09), within each type of right; firms, places and
  institution rights by hash halves; countries by period (2016-20 against 2006-10); the timeline as quarterly
  year-on-year changes by period; divisions FY2024 against FY2025; institutions 2017-23 against 2010-16, as rates per
  1,000 works.
- **Companion tables** (`region_indicators`, `national_indicators`, `industry_indicators`): each indicator against the
  lens's IP measures, not against every other indicator (millions of pairs that serve no question).
- **Planned pairs** (the Stage 1 summary's section 7): each in the units that mean something, with intervals (Wilson,
  Newcombe, bootstrap that resamples whole patents, Greenwood for survival curves, negative binomial models for area
  counts), in two periods, with third factors named.
- **Reproducible:** sampling by one hash rule for every half (`bivariate.half_sql`, DuckDB's hash of the key; until
  2 November 2026 `split_half` used pandas' hash, so B35's GII split, B50, B58 and B59 had other halves than the
  screens, ADR 0041), bootstraps on sorted inputs with fixed seeds, and exact sums in the build. Two full builds agree
  number for number since pass 4 (2 November 2026, ADR 0039); before it they did not (B28's lead count moved by one).
  The notebook takes about ten minutes.

## 3. What each lens shows

| Lens | Observations | Distinct leads | What stands out |
|---|---|---|---|
| `rights` | B1 to B19 | 221 over six types | Representation and outcomes; shares in force and reach by origin; expedite by filer and kind of request; inventions filed or held from abroad; gender by field |
| `firms` | B20 to B26 | 33 | Who files among R&D claimants and suppliers; claimants with no filing linked; contracts; age at first observed linked filing (one in five dated before the firm's first registration); firm age and patents with no Australian holder now |
| `regions` | B27 to B31 | 128 (79 on IP); 24,947 indicator pairs | One gradient of advantage, education and business density; negative binomial ratios; not one firm's; business mix |
| `national` | B32 to B35 | 188 (134 on IP); 225 attachments | Development gradient; Australia's OECD ranks; R&D and patenting in levels and changes |
| `timeline` | B36 to B39 | 1 | No common cycle; policy breaks against placebos; provisional follow-up; Australia-only series give context only |
| `industries` | B40 to B43 | 4 | Trade marks follow business R&D; patents in 8 divisions only; survey innovation is not IP |
| `institutions` | B44 to B46 | 18 (plus 3 in the IP detail) | Kind sorts measures; universities' patenting follows size and patent-cited research; little Australian use of cited research |

## 4. Carried to Stage 3

The signals in section 1, each with its candidate third factors: the filer (origin and type), family reach, the route
of filing, the technology field, selection at grant, firm size and industry, business density and mix, education,
income, and the kind of institution. Stage 3 tests whether each signal survives these together (`multi.partial_corr`,
models), and reduces the place and country gradients to a few components (`multi.pca`) before reading any indicator
as a driver.

## 5. Recorded, not carried

- **Mechanics** (B2): PCT receiving offices, where inventions are made, examination timing, Google Patents' inventor
  countries, the trade mark expedite recording (U103).
- **A record quirk** (B3): IP RAPID gives no origin for designs never registered; the register's fill covers them.
- **Did not hold in a second period:** the origin gap in time to grant (B7), organisations' lone-filing gap (B6), the
  trade mark expedites and the share in force (B14). (The pooled expedite link, B13, holds in both periods once
  patents are counted from grant: restated 2 November 2026.)
- **Screens with no lead beyond the expected:** the timeline's changes (B36), Australia-only annual series (B39),
  division-level survey indicators (B43).

## 6. Open items and data gaps

- **For IP Australia, proposed (OQ18):** whether priority claims and associated provisionals are recorded late in IP
  RAPID (B38, U90).
- **Data worth adding:** firms' size and industry (the third factors most firm leads need; BLADE stays ruled out),
  ALP's crosswalk with services (B41), the fee history (R3, OQ2), and a check of Google Patents' coverage of older
  Australian-only families (B11). All were added after Stage 2 (A15): size and industry for employers of 100 or more
  only (B50, B51), the crosswalk (B53, B54), the fees (B47 to B49) and the check (B55).
- **Still open:** a sector review of the institutions link (OQ11), which B44 to B46 rest on.

## 7. What Stage 2 cannot tell you

- **Causes.** Every pair has candidate third factors, and some may run backwards (representation and abandonment,
  B6). Effects need the designs that follow Stage 3.
- **Individuals from places or countries.** Section 3's and 4's pairs are between areas and countries (ecological).
- **Value.** Lifetimes on the register, reach and citations are candidate signs of private value, which need
  validating, and they disagree (B8); none is public value (the research goal's Q1). A lifetime is a share still in
  force, not a renewal decision (U36; restated 2 November 2026, ADR 0041).
- **Small units.** Industries (19) and OECD members (36) give wide intervals; their pairs are leads at most.

## 8. Index of observations

B1 to B4 the rights screen; B5 to B7 filing alone and grant; B8 to B10 shares in force; B11, B12 reach and citations; B13,
B14 expedited examination; B15, B16 routes and invention; B17, B18 gender; B19 Australian-founded rights now held only overseas. B20, B21 the
firms screen; B22 who files; B23 R&D and claimants with no filing linked; B24 contracts and income; B25 age at first filing; B26 firm age and
patents held only overseas. B27 the places screen; B28 attached indicators; B29 advantage and remoteness; B30 the largest
filer; B31 business mix. B32 the countries screen; B33 Australia among OECD members; B34 R&D and patenting; B35
attachments. B36 the timeline screen; B37 policy breaks; B38 provisional follow-up; B39 Australian against overseas,
and Australia-only series. B40 the industries screen; B41 IP per business; B42 innovation and IP; B43 attachments. B44
the institutions screen; B45 universities; B46 Australian use of cited research. B47 to
B49 fee changes (added after Stage 2); B50, B51 firms' size and industry; B52 the dollar and the cash rate; B53, B54
the crosswalk with services; B55 B11 again (families' coverage); B56 GDP and states' demand; B57 value added by
division; B58 incomes by postcode; B59 change between Censuses; B60 innovation in 2024-25; B61 the GII's blanks; B62
the NSRC.

## 9. Data gaps filled after Stage 2 (2026-10-28, A15)

- **Fees (B47 to B49; ADR 0031).** Changes in the fees to obtain a right rarely moved filing beyond placebo months:
  of 34 pairs after changes of 10% or more, 3 rushes and 2 steps beyond 95% of placebos, about what chance gives;
  the clear breaks are the 1995 and 2003 Acts. Across the larger changes, bigger rises go with smaller steps (rho
  -0.307, interval -0.639 to 0.070). Cessations rose beyond every placebo month after three renewal changes: patents
  after September 2002 (0.353 in logs), but not against the trend of the two years before (0.189, 38.89% of
  placebos); trade marks after July 1992 and July 1993, of which only July 1993 holds in the window that fits trade
  marks' dating and against the trend (0.232 and 0.235, 0% of 66). The national series show no response beyond
  placebo variation for the other changes, at this design's power. Carried to Stage 3: each right's renewal at the
  anniversary a fee changed. (Restated 2 November 2026, audits S2 L5 R04 to R06, ADR 0041: "no other renewal change
  ... did".)
- **Size and industry (B50, B51; ADR 0032).** Among employers of 100 or more, the largest are 22 points (14.6 to
  30.3) more likely than the smallest to have filed a standard patent; industry sorts patenting far more (manufacturing
  0.395, accommodation 0.006); R&D spend's weak link to patenting holds within size bands (0.105 to 0.253).
- **The cash rate and the dollar (B52).** No consistent sign for the dollar against overseas filing; the cash rate
  rises with overseas filing in booms, a cycle to allow for in before-and-after comparisons.
- **The crosswalk with services (B53, B54).** Patents per business follow business R&D per business across divisions
  (0.739, interval 0.38 to 0.89; 0.465 without services); 16 screen leads against 8. Stage 3 reports both crosswalks.
- **B11 again (B55).** Most of the fall in Australian organisations' "Australia only" patents is a gap in older
  records: through the PCT, 63.22% to 11.42% between decades (a fall of 51.8 points, 50.5 to 53.0), while WIPO's
  share of families filed abroad held at about 64%. Family measures for Australian applicants from FY2010 only.
- **The economy (B56, B57).** Real GDP's growth goes with overseas applicants' patenting (0.158 to 2008, 0.38
  after), not with Australians'; the states' demand tracks neither. Across divisions, value added per business goes
  with trade marks per business (0.591; 0.572) and business R&D (0.693; 0.677), with patents only through the
  crosswalk with services (0.581).
- **Incomes by postcode (B58).** Taxable income per individual goes with filing (trade marks 0.453; 0.518), the share
  running a business much less (0.194; 0.212); individuals' own filing per 1,000 individuals with business income
  rises from 3.84 in the most disadvantaged tenth of areas to 11.0 in the most advantaged (halves restated 2 November
  2026, ADR 0041). The advantage gradient
  is not explained by the number of people in business.
- **Change between Censuses (B59).** Areas that gained graduates or income from 2011 to 2021 did not gain filing
  (rho -0.147 to -0.016, negative in both halves; restated 2 November 2026, ADR 0041): levels go together, changes
  do not.
- **Innovation in 2024-25 (B60).** B42 holds in a third survey: innovating divisions file more trade marks per
  business (0.262), not more patents (-0.325), over 17 divisions with wide intervals.
- **The GII's blanks (B61).** Across OECD members, business-financed R&D goes with patents per GDP (rho 0.78) and
  so does the share of researchers in business (0.67); Australia ranks 17th of 38 on the first, 28th on patents and
  31st of 37 on researchers in business.
- **Commercialisation (B62).** Across institutions, per research dollar, invention disclosures go with standard patents
  (0.617; 0.615) and patents with licence income (0.593; 0.525) in both 2004-2009 and 2010-2015.
