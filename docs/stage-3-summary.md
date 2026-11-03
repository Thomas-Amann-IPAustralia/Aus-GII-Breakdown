# Stage 3 summary: several variables at once (first pass)

**Status (2026-11-03):** Stage 3's first pass is done, in `analysis/notebooks/03_multivariate.ipynb` (observations M1
to M25), begun on the owner's word (A32) with the methods the final review listed (A29) and the name match (A30). The
method is ADR 0046; the name match as tested is ADR 0047. The website is frozen during Stage 3 (A32): notebooks 1 and
2 and the evidence atlas are unchanged, and the Stage 2 readings that Stage 3 revises are listed in the handover.
Section 8 of the notebook drafts the two tables the plan asks for, for the owner's review. Every observation is an
association (observational) or a description: none is a cause.

## 1. In brief

- **Representation's gaps are not the filer's other characteristics.** Australian individuals' standard patents filed
  alone are granted about 31 points less often than with an attorney, with the route, year, state and co-filers held
  (86% to 87% of the raw gap), in both decades; trade marks about 21 to 23 points; no agent before the first renewal
  goes with 11 to 16 points fewer trade marks and designs in force after it, within individuals and organisations (M1,
  M2). The arrow can still run backwards.
- **Australian organisations' patents: three readings that still disagree.** Within the same reach they are less
  likely to end in any year to 10 years (hazard ratios 0.65 to 0.81); they reach fewer offices and draw about 27% to
  30% fewer citations within five years at the same reach, field, route and year (M3, M4). None is value alone (A22).
- **Expedited examination is not a sign of a longer life** once the filer, field and route are held; for Australian
  individuals it goes with a shorter one (hazard ratios about 1.25, M5). This revises B13.
- **Firms:** among R&D Tax Incentive claimants, age, spend and public form go with a standard patent, held together;
  suppliers with a filing linked hold about 2.4 to 2.6 times the contracts; among large employers the size gap widens
  within industry (M8, M9, M11). A name match to the ABR and ASIC (1.1% to 4.8% of tested matches name another ABN)
  closes most of the recent fall in standard patents linked to an ABN and changes no firm finding (M12).
- **Places:** the characteristics are mostly one advantage gradient (half the variation; variance inflation up to 86);
  with it, business density, degrees and R&D claimants beyond what resources predict, and remoteness all go with
  filing; the gradient is not one filer's; one group of 288 advantaged city areas holds 56% of placed patents (M13 to
  M16).
- **Countries and divisions:** residents' patents follow business R&D at the same income and size across OECD members,
  and patents allocated per business follow business R&D at the same value added across divisions; income adds nothing
  detectable for patents at home (M18, M22). Australia's nearest members on non-IP indicators are Norway, New Zealand
  and Sweden (M17).
- **Institutions:** universities' research measures are largely one measure of research intensity (M23); at the same
  research spend, more patents are not seen to go with more licences or licence income (M24, revising B62).
- **Over time:** with block resampling, B36's one quarterly lead holds, and the quarters are worth 14 to 53 independent
  observations (M19); Raising the Bar's rush and Australians' lower level after it hold with trend and season held,
  while the Designs Act's overseas step does not stand apart from a control (M25).

## 2. How it was done

- **Raw, then held together** (ADR 0046): each Stage 2 signal with its named third factors in one model, reported
  beside the raw figure. Yes or no outcomes: logistic regression as average marginal effects (points). Lifetimes: Cox
  models with delayed entry at grant, as Stage 2's curves (hazard ratios). Counts: negative binomial models with an
  exposure (rate ratios). Small lenses: partial rank correlations with 1,000 resamples. Series: STL, moving-block
  resampling and interrupted time series with Newey-West intervals.
- **Verdict words:** holds, weakened (less than half the raw size left), not detected once held, reversed; appears
  once held or not detected either way where the raw figure was not detected.
- **Clustered by the filer's party** where a filer has many rows, which widened some intervals a lot (organisations'
  older lone filings, M1; women inventors, M7).
- **Only what is settled at filing** is held for outcomes that follow it (the field and classes of a patent, assigned
  as it is classified, are a second reading, M1).
- **Structure before drivers:** variance inflation and principal components first, then models on the components.
- **Samples** as in Stage 2: two decades for rights, the hash halves for firms and places, two periods (a stability
  check) for countries, divisions and institutions.

## 3. What each lens shows

| Lens | Observations | What stands out |
|---|---|---|
| `rights` | M1 to M7 | Representation's gaps hold; origin within reach; expedite revised; granted patents held overseas; women by field |
| `firms` | M8 to M12 | Age, spend, form; contracts; first filings by cohort; size within industry; the name match |
| `regions` | M13 to M16 | One advantage gradient; business density and degrees beyond it; not one filer's; weak segments |
| `national` | M17, M18 | Several dimensions; Australia's neighbours; patents follow business R&D, not income, at home |
| `timeline` | M19, M20, M25 | Block resampling; trends and seasons; Raising the Bar holds, the Designs Act's step does not stand apart |
| `industries` | M21, M22 | Innovation not seen to go with IP; patents follow business R&D within value added |
| `institutions` | M23, M24 | Research intensity is one measure; commercialisation weak at the same spend |

## 4. Stage 2 readings that Stage 3 revises (waiting for the atlas)

B13 (M5), B17 (M7), B25 (M10), B29 (M14), B33 (M18), B37 (M25), B40, B42 and B60 (M21, M22), B45 (M23) and B62
(M24). Notebook 2 and the atlas keep their Stage 2 wording until the owner lifts the freeze.

## 5. Early signals and data gaps

Drafted in section 8 of the notebook: eleven signals (representation; origin, reach and life; expedite; patents held
overseas; women inventors; firms; places; countries; divisions; institutions; Raising the Bar) and nine gaps (small
firms' size and industry, the ABNs IP RAPID leaves out, trading names, kinds of expedited request, dated ownership
changes, older families, a working-day calendar, a review of the institutions link, business R&D by division in more
years). For the owner's review.

## 6. What Stage 3 cannot tell you

- **Causes.** Holding measured factors fixed is not an experiment; unmeasured ones (resources, the merit of an
  invention, intentions) can still explain an association, and some may run backwards (representation).
- **Individuals from places or countries.** Sections 3, 4 and 6 are ecological.
- **Value.** Lifetimes, reach and citations are candidate signs of private value that disagree (M3, M4); none is
  public value.
- **Small lenses.** 36 countries, 19 divisions, about 40 universities and 65 institutions give wide intervals: leads
  at most.

## 7. Index of observations

| # | Lens | Reading |
|---|---|---|
| M1 | rights | Filing alone and grant, with the factors settled at filing held |
| M2 | rights | No agent before the first renewal and the share in force after it |
| M3 | rights | Origin and the chance of ending, within reach bands (Cox) |
| M4 | rights | Reach and citations within five years, by origin |
| M5 | rights | Expedited examination and the chance of ending (revises B13) |
| M6 | rights | Australian-founded patents now held only overseas: grant, reach, type |
| M7 | rights | Women among inventors: filer, field and year |
| M8 | firms | R&D claimants: spend, form, age and place held together |
| M9 | firms | Suppliers' contracts and value |
| M10 | firms | First trade mark or first patent, by cohort (revises B25) |
| M11 | firms | Size and industry among large employers |
| M12 | firms | The name match: tested, applied, U44, U45 and M8 again |
| M13 | regions | Places' characteristics: correlations, variance inflation, components |
| M14 | regions | Filing against the components and remoteness (revises B29) |
| M15 | regions | B30 with the filer's party |
| M16 | regions | Kinds of places |
| M17 | national | Australia's profile and nearest members |
| M18 | national | Patents against business R&D, income and size (revises B33) |
| M19 | timeline | Quarterly changes with block resampling |
| M20 | timeline | Trend, season and remainders |
| M21 | industries | Innovation against IP with the crosswalk with services (revises B42, B60) |
| M22 | industries | IP per business against business R&D, value added held (revises B40) |
| M23 | institutions | Universities' patenting, research measures held together (revises B45) |
| M24 | institutions | Disclosures, patents and licences with research spend as the exposure (revises B62) |
| M25 | timeline | B37's behavioural breaks with trend and season held (revises B37) |
