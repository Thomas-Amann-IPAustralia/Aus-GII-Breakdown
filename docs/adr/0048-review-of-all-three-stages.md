# 0048: A review of all three stages: every carried signal, source and column taken through, in the notebooks

**Date:** 2026-11-03. **Whose:** the owner asked for a review of every stage, to find gaps and omissions and correct
them, in the notebooks only, not the website (A33). How it is done is Claude's; the owner can overturn any of it.

**Context.** Stage 3's first pass (ADR 0046) took up each lens, and its section 0 listed every Stage 2 signal as
taken up. Checked against notebook 2's section 8 (the sixteen signals carried, with their observations), the plan
(`docs/eda-plan.md`: every dataset through every stage, ADR 0007) and the lens registers (`variables.yaml`,
`screens.yaml`), the three notebooks had these gaps:

1. **Stage 3: carried signals not taken up**, though section 0's table said they were: B15 (divisionals), B16 (made
   here, filed from overseas), B22 among suppliers and B24's large taxpayers, B26 (firm age and patents held
   overseas), B31, B58 and B59 (business mix, incomes and change), B35 (the cross-country attachments), B38 (the
   FY2025 provisionals), B43 and B57 (the division-level indicators), B44 and B46 (every kind of institution), B47 and
   B49 (fee breaks), and B52 and B56 (the cycle, which the final review's block resampling covers). B49 also left a
   test explicitly to Stage 3 (renewal at each right's anniversary), which was not done.
2. **Stage 3: attachments not taken through.** `region_indicators`, `national_indicators` and most of
   `industry_indicators` appeared in Stage 3 only through the few measures the models used.
3. **Every stage: two sources in no lens.** The Labour Force Survey (`abs_labour`, added 25 October 2026) and the IP
   judgments (`fedcourt`) are planned timeline attachments that were never attached, so neither had a profile, a pair
   or a model (ADR 0007 requires every table to be attached to at least one lens). Stage 1's section 8 listed
   `fedcourt` with no output and did not list the Labour Force Survey.
4. **Stage 1: columns without a profile.** Stage 3's name-match columns (one in `rights`, four in `firms`), the
   timeline's fee components (13 columns; only the six totals were profiled) and `institution_rights`'s
   `shared_with_institution`; and, by the notebook's own account (5.11's summary), the shape of state final demand,
   nominal GDP and the PBS series.
5. **Errors in Stage 3's text:** M1 called a result "not detected once held" where the verdict was "not detected either
   way"; M16 gave the lowest silhouette as 0.231 (0.2316 on the page).
6. **A fault in a Stage 3 helper:** `multi.adjusted_effect` gave a meaningless clustered interval, without warning,
   when two held factors picked out the same rows (a patent with no technology field also has no class count): the
   model is then rank-deficient.

**Decision.**

1. **Fill the Stage 3 gaps in notebook 3**, each in the section of its lens, numbered in the order added (M26 to M38),
   with the same methods (ADR 0046): logistic average marginal effects clustered by the filer's party; partial rank
   correlations with 1,000 resamples; negative binomial and gamma models; interrupted time series with trend and
   season held; moving-block resampling for quarterly changes. Each section says it was added in the review.
2. **The renewal test at each anniversary** (B49's own request): for each change in a fee to keep a right since 2000,
   the rights whose changed anniversary fell in the year either side, the share let go at it, with a straight-line
   trend on each side, the anniversary, filer and field held; anniversaries whose fee did not change as a control.
   The month of the year is not held: within a two-year window it is nearly collinear with the before-and-after split
   (a first fit with it gave designs in 2020 a 48-point jump that the quarterly shares do not show).
3. **The attachments beyond the gradient:** B28's and B35's screens repeated with the components (places) or income
   and size (countries) held, with B28's and B35's rule for a lead, and B43's surviving items with size and value
   added held.
4. **Attach the Labour Force Survey and the IP judgments to the timeline** (`build.timeline_sql`): employed persons,
   the unemployment and participation rates (Australia, seasonally adjusted), owner-managers (original), and IP
   judgments in all, on patents and on trade marks (January 1995, when they become continuous, to February 2025, when
   the corpus closes; empty after). They are not filing series, so `screens.yaml` marks them as not screened, as it
   did the RBA's and the national accounts' (ADR 0042 practice): Stage 2 reads them as selected pairs (B63), Stage 3
   with block resampling (M36). Their monthly companions the plan also listed, the CER's national installations and
   AusTender by month, stay unbuilt: both sources are already attached to other lenses, so ADR 0007 is met.
5. **Fill the Stage 1 gaps in notebook 1** (U124 to U127) and the Stage 2 gap in notebook 2 (B63), **by additions and
   dated corrections only**: no reviewed observation is rewritten, so the evidence atlas, which quotes them and stays
   frozen (A32), is out of step only where the handover lists it. Notebooks 1 and 2 are run cell by cell for the new
   cells (with their setup cells), not in full, so that the reviewed outputs stay as they were reviewed.
6. **Fix the helper:** `adjusted_effect` now refits on the columns that are not exact combinations of the others (read
   from the cross-product matrix), keeping the intercept and the signal; the fitted chances, and so the effect, are
   unchanged, and the interval is finite. A test covers it. Notebook 3 was re-run in full, and every earlier output
   compared with the one before the fix (the comparison is recorded in the handover).
7. **Correct M1 and M16** where they are, with a dated note, and **correct section 0's table**, so that it names where
   each carried signal is taken up.

**Rejected.**
- **Rewriting notebooks 1 and 2 in place,** or re-running them in full: the atlas quotes them, and a full re-run would
  change outputs the owner's reviews checked (U1's column count, for one) for no gain in what they show.
- **Holding the month of the year in the anniversary test:** see Decision 2.
- **Attaching the CER's monthly series and AusTender by month now:** their sources are in other lenses already; the
  plan's monthly versions are a convenience, recorded in the handover, not a gap in coverage.
- **New sources for the medicine strand (TGA, the PBS beyond Stage 1):** they wait for OQ8, the owner's call.

**Consequences.** `03_multivariate.ipynb` gains thirteen sections; its lens summaries and section 8's tables carry
them. The timeline lens has 86 columns. `variables.yaml`, `screens.yaml` and `GLOSSARY.md` gain the new columns and
terms. Stage 2 readings that Stage 3 now revises are listed for the atlas in the handover, with notebooks 1 and 2's
additions. Until the atlas carries them, its five tests fail (they require a page for every observation of
notebooks 1 and 2: U124 to U127 and B63 have none), as they did during pass 7; nothing else fails.
