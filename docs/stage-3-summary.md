# Stage 3 summary: several variables at once (first pass, completed in the review)

**Status (2026-11-03):** Stage 3's first pass is done, in `analysis/notebooks/03_multivariate.ipynb` (observations M1
to M25), begun on the owner's word (A32) with the methods the final review listed (A29) and the name match (A30). The
method is ADR 0046; the name match as tested is ADR 0047. The website is frozen during Stage 3 (A32): notebooks 1 and
2 and the evidence atlas are unchanged, and the Stage 2 readings that Stage 3 revises are listed in the handover.
Section 8 of the notebook drafts the two tables the plan asks for, for the owner's review. Every observation is an
association (observational) or a description: none is a cause.

**Completed in the review of 3 November 2026** (the owner's request to find and correct gaps in every stage, A33, ADR
0048). The first pass's section 0 listed every Stage 2 signal carried to Stage 3 as taken up; eighteen were not (B15,
B16, B22 among suppliers, B24's large taxpayers, B26, B28's attachments, B31, B35, B38, B43, B44, B46, B47, B49, B52,
B56, B58, B59), nor was B49's own request, a test of renewal at each right's anniversary. Each now has its section
(M26 to M38). Two sources in no lens (the Labour Force Survey and the IP judgments) are attached to the timeline and
taken through all three stages (U124, B63, M36). M1 and M16 are corrected, and a fault in the helper for yes or no
outcomes (a meaningless interval when two held factors repeat each other) is fixed: the notebook was re-run in full and
no earlier figure changed.

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
- **Added in the review (M26 to M38):**
  - **Fees:** owners did not let rights go more often at the anniversary after a change in its renewal fee, after any
    of nine changes since 2000 (for patents within about 1.4 points, M28); B47's filing breaks mostly do not read as
    prices with trend and season held, and B49's cessation steps are not seen at each right's anniversary (M34).
  - **Divisionals** doubled among organisations' standard patents within the same filers (+19.18 points for
    Australian organisations, +10.97 overseas, M26). **Inventions made here and filed from overseas** are, in about
    equal numbers, international teams' and all-Australian teams' (M27).
  - **Firms:** among suppliers, form, age and a city address hold together, the postcode's advantage does not; large
    taxpayers with a filing linked report no more income once form, age and state are held (M29); patents filed
    before the firm's first registration are more often now held overseas (M30).
  - **Places:** beyond the advantage gradient, manufacturing's share of businesses goes with more filing per business
    (0.449 and 0.396 for patents), which Stage 2 did not see; incomes add nothing (M31); of 13,673 pairs of an attached
    indicator and a filing rate, 1,281 remain leads beyond the gradient, against 9,539 raw (M32).
  - **Countries:** 56 of 477 attachments remain leads with income and size held (224 raw), mostly research effort;
    women's share of researchers is not detected once business's share of researchers is held (M33).
  - **Over time:** FY2025's lower follow-up of provisionals is new and heavy individual filers' (M35); with block
    resampling only the cycle's pre-2008 pairs with overseas applicants' trade marks are clear of zero (M36).
  - **Divisions and institutions:** B43's three survey items hold with size and value added (M37); across every kind
    of institution, research that patents cite goes with the institution's patenting (M38).

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
| `rights` | M1 to M7, M26 to M28 | Representation's gaps hold; origin within reach; expedite revised; granted patents held overseas; women by field; divisionals within filers; two kinds of team; no renewal response to fees |
| `firms` | M8 to M12, M29, M30 | Age, spend, form; contracts; first filings by cohort; size within industry; the name match; suppliers' form, age and city; filing before registration |
| `regions` | M13 to M16, M31, M32 | One advantage gradient; business density and degrees beyond it; not one filer's; weak segments; manufacturing's share beyond it; most attachments are the gradient |
| `national` | M17, M18, M33 | Several dimensions; Australia's neighbours; patents follow business R&D, not income, at home; research effort beyond income |
| `timeline` | M19, M20, M25, M34 to M36 | Block resampling; trends and seasons; Raising the Bar holds, the Designs Act's step does not stand apart; fee breaks mostly not prices; FY2025 provisionals; the cycle before 2008 only |
| `industries` | M21, M22, M37 | Innovation not seen to go with IP; patents follow business R&D within value added; B43's items hold |
| `institutions` | M23, M24, M38 | Research intensity is one measure; commercialisation weak at the same spend; patent-cited research across kinds |

## 4. Stage 2 readings that Stage 3 revises (waiting for the atlas)

B13 (M5), B17 (M7), B25 (M10), B29 (M14), B33 (M18), B37 (M25), B40, B42 and B60 (M21, M22), B45 (M23) and B62
(M24); from the review, B15 (M26), B16 (M27), B49 (M28, M34), B22 and B24 (M29), B26 (M30), B31, B58 and B59 (M31), B28
(M32), B35 (M33), B47 (M34), B38 (M35), B52 and B56 (M36), B43 (M37), and B44 and B46 (M38). Notebook 2 and the atlas
keep their Stage 2 wording until the owner lifts the freeze; notebooks 1 and 2 gained additions in the review (U124 to
U127, B63), which the atlas does not yet show.

## 5. Early signals and data gaps

Drafted in section 8 of the notebook, completed in the review: fifteen signals (the first pass's eleven (representation; origin, reach and life; expedite; patents held
overseas; women inventors; firms; places; countries; divisions; institutions; Raising the Bar; and, from the review,
divisionals, two kinds of team, renewal and fees, FY2025's provisionals) and thirteen gaps (the first pass's nine: small
firms' size and industry, the ABNs IP RAPID leaves out, trading names, kinds of expedited request, dated ownership
changes, older families, a working-day calendar, a review of the institutions link, business R&D by division in more
years; and renewal payment dates, divisionals' parents, judgments after March 2025, the CER's and AusTender's monthly
series). For the owner's review.

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
| M26 | rights | Divisionals, field and filer held, within the same filers (B15; added in the review) |
| M27 | rights | Inventions made here, filed from overseas: two kinds of team (B16) |
| M28 | rights | Renewal at the anniversary after a fee change (B49's own test) |
| M29 | firms | Suppliers' form, age and place; large taxpayers' income (B22, B24) |
| M30 | firms | The filing firm's age and patents held overseas (B26) |
| M31 | regions | Business mix, incomes and change beyond the components (B31, B58, B59) |
| M32 | regions | Every attached indicator beyond the components (B28) |
| M33 | national | The cross-country attachments with income and size held (B35) |
| M34 | timeline | Fee breaks with trend and season held (B47, B49) |
| M35 | timeline | The FY2025 provisionals with the filer held (B38) |
| M36 | timeline | The cycle, the labour market and the courts with block resampling (B52, B56, B63) |
| M37 | industries | The division-level indicators with size and value added held (B43, B57) |
| M38 | institutions | Every kind of institution: patent-cited research and patenting (B44, B46) |
| M39 | timeline | Trade marks' lead on real GDP, as IP Australia's note (B56; added at A36) |
| M40 | rights | Early, unprompted requests for examination and staying in force, as IP Australia's commissioned study (B13; added at A36) |

## 8. Checked against IP Australia's published evidence (2026-11-04, ADR 0052)

Each of M1 to M38 now has a verdict against IP Australia's publications (`docs/audit-ip-australia.md`, section 11): 9
consistent (M7, M8, M11, M17, M25, M26, M29, M34, M35), 3 qualified (M5, M23, M36) and 26 not testable; none disputed or
contradicted. M5 does not dispute IP Australia's commissioned study on fast-tracked patents: the study's "speeding up"
is wider (early unprompted requests), and it finds delay helps small innovators, as M5 does. Nothing else changes.

## 9. Two tests from IP Australia's research (2026-11-04, A36, ADR 0053)

At the owner's decision, two tests the audit against IP Australia suggested were added (notebook 3, sections 1.11 and
5.8; only the new cells were run):
- **M40:** IP RAPID's directions to request examination give IP Australia's commissioned study's measure, a request
  made before any direction: 41.39% of granted patents (the study, 41.9%). With the filer, field, route, cohort and
  expedited examination held, those patents are more likely to end in a given year after grant (hazard ratios 1.276
  and 1.383), the opposite of the study's reported direction. Its model is not published (OQ28 proposes asking).
- **M39:** trade marks and real GDP share a long-run path (p 0.018, 1983 to 2023), as IP Australia's note finds; in
  changes, with GDP's own growth held, trade marks' lead is small (0.038) and not detected after 2008.

Against IP Australia's publications (section 11.8 of the audit), M39 is consistent with the size differing and M40
disputed in part. Section 8's tables are unchanged; whether M40 joins the third early signal is for the owner's review.
