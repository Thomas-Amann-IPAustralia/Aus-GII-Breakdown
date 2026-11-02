# Stage 2 notebook audit: Lens 5, Australia over time

**Reviewed:** 2 November 2026, by a Claude Code session at the owner's request. **Source:**
`analysis/notebooks/02_bivariate.ipynb` as committed at `cb54448` (SHA-256 `3d250d2a…b7e2`, in full below), read in the
repository. The GitHub web pages and the evidence atlas were not looked at; they are for a separate pass.

**Provenance:** The first audit of this section: the ChatGPT batch (`analysis/GPT-audit/261030/`) stopped at §4. It
follows that batch's format (themed sections; numbered findings with an **Issue** and an **Action**; a closing review
boundary), with a bar in place of the dash after each finding's number. R-numbers are local to this report.

**Scope of this pass:** §5 only, §5.0 to §5.7 (B36 to B39, B47 to B49, B52, B56): all 24 cells, the 9 code cells
(execution counts 50 to 58) with their saved outputs, and the 3 figures (the fee scatter and the provisional follow-up
chart inspected as images). The notebook's introduction and §8's timeline rows were read for the method and the claims
they repeat. Beyond the notebook, the helpers the section calls (`analysis/eda/bivariate.py`), the timeline's
definitions (`analysis/eda/build.py`, `variables.yaml`, `screens.yaml`) and ADR 0030 were read to check what the code
does. Nothing was re-executed and no data were queried.

**Overall finding:** The quoted numbers match the saved outputs, with one miscount (B52's "ten pairs"). The weaknesses
are in what the outputs are taken to show. A sentence left from before §5.4 says the fee history is not in the data.
Breaks that the law makes certain (expiries stopping when the patent term lengthened, filings stopping when a right
closed) are counted beside behavioural responses as "clean breaks" for natural experiments. B47's count of rushes and
steps mixes falls with rises and leaves out the one break that moved the way a price would. B49's heading contradicts
its own bullet, and its "weak lever" rests on a design that could not detect a modest effect. "Do not move together"
rests on missing significance in serially dependent quarterly changes, and B39's own table contradicts its reading.
B38's follow-up measure breaks in August 2021, when innovation patents closed.

**Priority:** **High** = affects interpretation, validity or downstream use; **Medium** = correct before relying on or
circulating the findings. Apply each correction to §5.7, to §8's timeline rows and to `docs/stage-2-summary.md`, as well
as to the observation.

**Read first:** R01 (the stale fee sentence), R02 and R03 (what counts as a break), R04 and R05 (B49), R08 and R09 (B36,
B39), R12 (B38's break).

## Later additions not carried back

### R01 | High | B37, §5.7: the fee history is said not to be in the data

**Issue:** B37 ends "The fee changes, IP Australia's most direct lever, are still not in the data (R3, OQ2)". §5.4 (B47
to B49), added after Stage 2 from the fee history (gap A1, ADR 0031), analyses 22 months of fee changes in the same lens,
and §8's data-gap paragraph says the fee history was filled. Pass 3 swept later additions that were not carried back,
but no earlier audit covered §5, so this sentence was missed. A reader of B37 is told that the lever Q5 most needs is
unavailable.

**Action:** Replace the sentence with a pointer to §5.4 and its limits (B47 to B49, and R03 to R06 here), with a dated
restatement line. Check §5's other cross-references (B37 to B47; B39 to B52 and B56) for the same lag. Evidence:
`9ccc4779`, `f5daa298`, `a8e97186`, §8 in `de334709`.

## Policy breaks and fee changes against placebo months

### R02 | High | B37, §5.7, §8, summary: breaks the law makes certain are read as clean natural experiments

**Issue:** Several of B37's breaks "far outside anything seen at placebo dates" are definitional or administrative:
patent expiries stop for four years when the term rises from 16 to 20 years (a step of -3.937; `build.py` records that
the fall is the term change); second-tier filings stop when the innovation patent closes (-3.17); extensions of term
begin when their regime begins (2.419); trade mark registrations pause when the 1995 Act commences (-7.205). A placebo
comparison cannot tell these from behaviour: it confirms that the law changed the series, which was known. Only Raising
the Bar's rush, and perhaps the Designs Act's overseas step, are plausibly behavioural. "These six changes give clean
breaks for the natural experiments ... each beside series it should not have moved" overstates: `CANDIDATES` lists only
target series, so no control series was tested. The heading's "three of the four steps" sits beside bullets in which
every candidate step is beyond every placebo in at least one series (the Designs Act's overseas designs, 0.338, 0%).
And the 20-year term's own baseline is six months: the expiry series starts in January 1995, and `spike_step` does not
check the event's window for gaps, while every placebo must have a complete one.

**Action:** Classify each break as mechanical, administrative or behavioural, and say what each could identify (for
example, renewal around the 20-year term), not that it is a natural experiment. Name control series and test them
before writing "beside series it should not have moved". Correct the heading's count, and apply the placebos'
completeness check to the event itself. Evidence: `8024a330`, `9ccc4779`, `c9d57cd6`, `de334709`;
`build.TIMELINE_START_OVERRIDE` (`patents_expired`: 1995-01-01).

### R03 | High | B47, §5.7, summary: the count of rushes and steps mixes directions and leaves out the one price-like break

**Issue:** The placebo test is two-sided (absolute values). So "filing rushed beyond 95% of its placebo months 3 times"
counts falls as rushes: two of the three are the Trade Marks Act's January 1996 pause (Australians -0.304, overseas
applicants -0.202), and the third is a rise before a cut (overseas applicants' patents, January 1998, +0.147). Of the two
"steps" after rises, one is overseas designs after June 2004's 122.2% rise, which rose (+0.334, against a price). The
other, in neither B47 nor §5.7, is Australians' designs after July 1988's 15.38% rise: a fall of 0.136 in logs, as large
as only 2.778% of 36 placebos, and the only counted break in a price's direction. "The clearest breaks are new Acts, not
prices" may still be right, but the counts as written do not show it. The chart draws two dots per change (Australian
and overseas series) without saying which is which.

**Action:** Report rushes and steps by sign and by whether they point the way a price would; name every pair counted;
add the July 1988 design step to B47 and §5.7; mark the series in the chart. Read "about 1.7 of each expected by chance"
as a rough guide, since the 34 pairs share 18 changes (R07). Evidence: `638d00a5` (the full table), `de31406f`,
`a8e97186`, `c9d57cd6`; `docs/stage-2-summary.md` section 9.

### R04 | High | B49, §5.7, §8, summary: the heading says only one renewal change moved cessations; the bullet shows three

**Issue:** B49's heading says "no other change in the fees to keep a right, up or down, moved cessations beyond the
ordinary", but its trade mark bullet reports July 1992 and July 1993 (rises of 4.255% and 2.041%) with steps of 0.148
and 0.283, larger than every placebo month (0%). The bullet explains them by cessations "climbing in the series' first
years (it starts in 1987)": an untested explanation, in a design the section says allows for trends. §5.7 ("Only
patents after September 2002"), §8 ("patent cessations after the 2002 renewal rise did") and the Stage 2 summary ("no
other renewal change ... did") repeat the heading.

**Action:** Report the three changes beyond every placebo month; present the trend reading as a hypothesis, with a
check (placebos drawn only after the series settled, or a detrended baseline); correct §5.7, §8 and the summary.
Evidence: `c5b83a0e`, `a8e97186`, `c9d57cd6`, `de334709`.

### R05 | High | B49, §8: "a weak lever" is concluded from a design that could not detect a modest effect

**Issue:** "At the national level, fee changes have been a weak lever on how many rights are filed or kept" is a claim
about an effect. The design compares national monthly counts with placebo months; cessations in any month mix many
cohorts reaching different anniversaries and are driven mainly by how many rights fell due, so an effect smaller than
the series' ordinary movement cannot show. The renewal fee is summarised as "the full term's renewals" (a total over the
term), not as the fees for the anniversaries that fell due. §8 says fee changes "rarely moved filing or lapsing": B49
measures cessations, which IP RAPID records as a different event category from lapses (`build.TIMELINE_EVENTS`).

**Action:** Say that the national series show no response beyond placebo variation for most changes, at this design's
power; keep the effect question for the anniversary-level test that B49 itself proposes for Stage 3. Name the
anniversaries whose fees changed. Write "cessations" in §8. Evidence: `c5b83a0e`, `a8e97186`, `de334709`.

### R06 | Medium | B49: the window after a renewal change fits how patents are dated, not trade marks or designs

**Issue:** "Months 7 to 18 after the change ... since a renewal falls due on an anniversary and can be paid up to six
months late" fits patents, whose recorded cessation falls 6 to 7 months after an anniversary (`variables.yaml`,
`years_in_force`). Trade mark and design cessations appear to be dated at the anniversary: their records follow the
effective date by about six months (a median 198 days for trade marks, the note on `build.TIMELINE_LAG`). For those two
series, months 0 to 6 hold the first renewals the change affected, and they are left out.

**Action:** Set the window by right from how each series is dated, or show both windows. Evidence: `c5b83a0e`;
`build.py` (`TIMELINE_LAG`, `EVENT_DATE`).

### R07 | Medium | B48, B37, B47: intervals and placebo shares treat dependent units as independent

**Issue:** B48's bootstrap resamples the 34 pairs, though the code's comment says "a bootstrap interval over changes";
the Australian and overseas pairs of one change share its cost change, so the interval (-0.639 to 0.070) is too narrow
for 18 changes. Placebo months' windows overlap one another by up to 23 months and include other events, so "0% of 72"
is a rank among dependent windows, not a p-value of 1 in 72; for the 20-year term, only 36 placebos exist.

**Action:** Resample changes, not pairs; describe placebo shares as ranks with their number of placebos, not as
p-values. Evidence: `de31406f`, `8024a330`, `638d00a5`.

## How the series move together

### R08 | High | B36, B39, §5.7, §8: "do not move together" rests on missing significance in serially dependent changes

**Issue:** The screen has 68 and 72 quarterly changes. Of 378 pairs measured, 197 reached 0.1 in the discovery period
but did not survive the correction: that is absence of evidence at this sample size, not evidence of no association.
Year-on-year changes of quarterly totals are serially dependent, so the screen's p-values, the one lead's interval (0.498
to 0.786, from resampling quarters as if independent), and B52's and B56's correlations overstate the information.
B39's heading ("do not move together from quarter to quarter") also sits beside standard patents' 0.444 in the
replication period, and "no common cycle" (§5.7) passes over shared events: Raising the Bar's rush moved both origins at
once. The screen compares changes in the same quarter, so "filings and the events that follow them a year or more later"
were not tested.

**Action:** Write "no association detected at this power", with intervals that respect serial dependence (a block
bootstrap, or effective sample sizes). Say that the screen is contemporaneous, and test lags where a pair is planned.
Evidence: `963a0e6d`, `a7778e51`, `0a9810e0`, `9c64ef93`, `c9d57cd6`.

### R09 | High | B39, §8, summary: its own table contradicts its reading

**Issue:** B39 says the four annual pairs that pass the correction "are other counts of the same filings". The strongest
is "Trademark applications, nonresident, by count" (the World Bank's IP.TMK.NRCT; rho 0.785 over 20 years, q 0.012):
applications from non-residents, that is, overseas applicants' trade marks in Australia. So Australians' and overseas
applicants' trade mark filing rise and fall together from year to year, which contradicts the heading's second clause
(no annual series moves with Australians' filing once the number of series is allowed for) and undercuts its first.
§8 and the summary list B39 among "screens with no lead beyond the expected".

**Action:** Correct the reading of that row and restate the heading for the annual evidence; check the residents' rows,
which count classes at all offices and so are not the same filings either. Evidence: `0a9810e0`, `9c64ef93`,
`de334709`.

### R10 | Medium | B36: the one lead's explanation does not match its third factors

**Issue:** "More marks reaching the end of examination means more to oppose and more to register" invokes acceptances,
which are not in the lens; the candidate third factors printed (patent expiries, patent cessations, designs of unknown
origin) are not that process. The opposition series also counts non-use removal requests, which concern registered
marks, not those being examined.

**Action:** Present the explanation as a hypothesis, add acceptances if the events hold them, and say what the
opposition series contains. Evidence: `963a0e6d`, `a7778e51`; `build.TIMELINE_EVENTS`.

### R11 | High | B52, B56: planned pairs without intervals, and readings beyond the correlations

**Issue:** The notebook promises a 95% interval for every planned pair; B52 and B56 report 36 pairs (72 correlations)
with none, no correction and no replication rule, on serially dependent changes. Their readings go beyond the numbers:
"a dearer dollar goes with more, not fewer, which is a shared cycle, not a price"; interest rates and overseas filing
"rise together in booms"; and "the cycle ... and real growth go with filing from overseas, not from here", although
Australians' standard patents reach 0.191 with GDP in the later period. B52's "-0.172 to 0.242 over the ten pairs"
covers six pairs (twelve values). B56's "about what chance gives" is not computed on the page. §5.7's "cash rate with
overseas filing (0.46, 0.198)" is overseas trade marks only.

**Action:** Add intervals that respect serial dependence; present the cycle and price readings as hypotheses; correct
the pair count; compute the chance comparison or drop it; label §5.7's figures by series. Evidence: `bb6728df`,
`9febc3de`, `a05822b0`, `9b554c9c`, `c9d57cd6`.

## Provisional follow-up

### R12 | High | B38, §8: the follow-up measure changes in August 2021, when innovation patents closed

**Issue:** A provisional counts as followed up if a patent links to it (`associated_provisional`, `convention`,
`complete_from_a_provisional` or `innovation_from_a_provisional`) within 380 days. From 26 August 2021 new innovation
patents could no longer be filed (B37's closure), so provisionals filed from FY2022 lost a follow-up route that earlier
years had; FY2021's peak (individuals 18.76%, organisations 20.68%) coincides with the rush before the closure (B37's
spike of 1.459). B38 sets FY2025 against "12.24% to 18.76% in FY2018 to FY2024", a range across the break. Its
"Reading" uses FY2024 (12.27% to 6.66%), the comparable base, but the headline range does not. A shift from an
Australian complete application to the PCT, which this 12-month measure cannot see, is a third explanation beside late
recording and unpursued placeholders.

**Action:** Compare FY2025 with FY2022 to FY2024 (individuals 12.24% to 14.15%; organisations 10.63% to 12.23%), mark
the August 2021 break on the chart, and add the PCT route to the reading. Evidence: `010c79b5`, `75fbe082`, `8024a330`.

## Completeness and the record

### R13 | Medium | §5, `screens.yaml`: the PBS series have no Stage 2 treatment, and the record says they do

**Issue:** The timeline's four PBS columns (gap B11, U123) are skipped in the screen as "added after Stage 2 (gap B11):
its own section", but notebook 2 has no PBS section and §5.7 and §8 do not mention the series; the handover records that
their Stage 2 pair waits for OQ8. ADR 0007 asks that every dataset go through all three stages. Separately,
`screens.yaml`'s timeline reasons cite stale sections: the fees "5.5" (now 5.4), the Reserve Bank "5.6" (now 5.5) and the
national accounts "5.5" (now 5.6).

**Action:** Record in §5 and §8 that the PBS's Stage 2 pair is deferred to OQ8, or add it; correct the section numbers.
Evidence: `screens.yaml` (timeline), `af5407df`, `c9d57cd6`; `docs/handover-eda.md` (B11).

### R14 | Medium | §5.7: the summary carries the overstatements above

**Issue:** §5.7 carries B37 as "Yes: Q5, natural experiments", B39 as "No common movement", B47 without July 1988, B49
as "Only patents after September 2002" and B52 as "a cycle", and puts "placebo test" in the column "Holds in the other
period?", which a placebo comparison is not.

**Action:** Regenerate §5.7 from the corrected observations, and explain the placebo design in a note rather than in the
replication column. Evidence: `c9d57cd6`.

## Review boundary and reproducibility

This report contains **14 issue/action entries** (9 High, 5 Medium). It reviews §5's text, code and saved outputs, and
reads the helpers and definitions the section relies on. It did not re-execute the notebook or query the lenses:
numbers were checked against the saved outputs and arithmetic on them, and claims about dating rest on the notes in
`build.py` and `variables.yaml`, not on the data. All 9 code cells have saved outputs, execution counts 50 to 58 in
order, and no saved errors; that shows a coherent saved run, not that current data and helpers reproduce it. No
notebook, code or website files were changed.

**Evidence locators:** B-numbers and section headings are searchable; eight-character identifiers are the notebook
JSON's stable cell `id` values, not execution counts.

Repository commit: `cb544481aa64830e95c1ecd64260454baef41ed5`.

Reviewed notebook SHA-256: `3d250d2a14a58e9b4546c01601969bbe7d14e963f46b030276abbbd01a02b7e2`.
