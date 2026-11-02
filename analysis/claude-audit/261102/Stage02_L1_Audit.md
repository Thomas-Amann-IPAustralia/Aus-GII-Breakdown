# Stage 2 notebook audit: Lens 1, IP rights (rechecked and continued)

**Reviewed:** 2 November 2026, by a Claude Code session at the owner's request. **Source:**
`analysis/notebooks/02_bivariate.ipynb` as committed at `cb54448` (SHA-256 in full below), read in the repository. The
GitHub web pages and the evidence atlas were not looked at.

**Provenance:** Rechecks `analysis/GPT-audit/261030/Stage02_L1_Audit.md` (ChatGPT, 1 November 2026, R01 to R31), which
read the notebook before the five passes of amendments (`analysis/GPT-audit/261030/AMENDMENTS.md`), and continues it.
The earlier findings keep their numbers; new findings are numbered from R32. Format as in that batch, with a bar in
place of the dash after each finding's number.

**Scope of this pass:** §1, §1.0 to §1.9 (B1 to B19, B55): all 42 cells and the 22 code cells (execution counts 2 to 23)
with their saved outputs; the 11 figures were judged from their code, not re-inspected as images. Every earlier finding
was checked against the notebook as it now stands. Because survival is the next theme to be acted on, the code and
definitions behind the survival analyses were read closely: `lifetimes` and `at_years` in the notebook,
`univariate.kaplan_meier`, `bivariate.survival_with_interval`, `variables.yaml` (`in_force`, `years_in_force`,
`has_agent`, `representation`), `screens.yaml` (rights), and notebook 1's U36 and U103, on which §1.2 and §1.4 rest.
Nothing was re-executed.

**Overall finding:** Of the earlier audit's 31 findings, 4 are resolved by the passes (R06, R25, R26, R29), 6 hold in
part and 21 hold as written; none is wrong, though one concern in R11 (rounding) proves harmless. The survival analyses
need the most work. The screen treats unfinished lifetimes as finished. "In force after 10 years" means different things
for patents and for trade marks. Survival is read as renewal and as value, against Stage 1's own U36 and against the
condition on which the owner adopted the measure, and the comparison of renewal by representation counts representation
at any time, renewal included. Separately, B6's near-universal design registration is an artefact of the selection that
B3 itself warns about.

**Priority:** **High** = affects interpretation, validity or downstream use; **Medium** = correct before relying on or
circulating the findings. Apply corrections to §1.9, §8 and `docs/stage-2-summary.md` as well as to the observation.

**Read first:** R33 and R12 (survival read as value and renewal), R32 (the screen's lifetimes), R11 (what "in force
after N years" measures), R34 (representation and renewal), R09 (designs).

## The earlier audit's findings, checked again

"Holds" means the earlier finding's Issue and Action still apply as written (read them in the earlier file); "holds in
part" says what has changed; findings marked "below" have a full entry here, with new evidence.

| Finding | Priority | Status now | What the notebook shows now |
|---|---|---|---|
| R01 | High | Holds | B6 still compares within requested examinations, B8 within fields, B12 within reach, B13 by filer, without calling them stratified; pass 1 judged this framing and did not act. `1f1747cd`, `3658ea02`, `7a25fb76`, `fd83230a` |
| R02 | High | Holds | The introduction still says the measures "give the same value" for yes/no variables and that rho reads association "in any shape"; see S2 S8 R10 for where the shared scale fails. `0a9fee61` |
| R03 | High | Holds | §1 still says a pair holding in both periods "is not an accident of one decade"; intervals still resample rows (100 resamples, S2 S8 R09). `d97bc865` |
| R04 | High | Holds | The screen still includes overseas gender estimates and lifetimes; the lifetime part is now R32. `474fc7fd`, `2c348216` |
| R05 | Medium | Holds | B1 still applies 0.859 to "the 5,207 pairs measured in both" (the correlation leaves out pairs related by construction) and heads "most of them holding in a second decade", though every lead holds by definition. `9878ed51`, `2c348216` |
| R06 | High | Resolved (pass 2) | `FILER` is built from `filer_group`, one party, empty when origin is unknown, so B12's null branch is gone; B15's holder-based statistic remains (R19). `ea1827ce` |
| R07 | High | Holds | "Filed alone" throughout; B6 still explains the earlier decade's lone organisations as "firms with their own patent staff", and the 1,149 are applications. B5 found design agents recorded differently between decades, which suggests a recording explanation for these organisations too. See also R34. `20488ed2` |
| R08 | High | Holds | B6's heading still says "among applications that were examined" (its bullet: requested); the conditional rate still divides all grants by requests; B19 still calls the complement of a grant date "never granted", though FY2012 to FY2021 filings include applications still pending. `1f1747cd`, `20488ed2`, `7546a9f3` |
| R09 | High | Holds; below | B6's "99.4% to 100% ... whoever files" drops failed designs; B3's own table measures how many. |
| R10 | Medium | Holds | B7's heading still says the gap did not occur in FY2000 to FY2009 (0.082 years, 0.044 to 0.123); the table's `size` counts rows without a request date; B2 still says "the applicant, not only the office, sets the pace". `1468d831`, `2c348216` |
| R11 | High | Holds in part; below | The grant filter is answered by `in_force`'s definition and the rounding is harmless; the rest holds, with more. |
| R12 | High | Holds; below | Renewal and value wording remain, against U36. |
| R13 | Medium | Holds | The within-field check is still FY2005 to FY2009 only; B8 still cites B6 for Australians' lower grant rate and B10, not B11, for family reach. `3658ea02`, `fb8284f8` |
| R14 | High | Holds | B13 and §1.9 still say "Simpson's paradox" and "a composition effect" with no decomposition; subgroup gaps change too (Australian organisations +3.3 then -9.1 points; Australian individuals -6.6 then -14.9). `fd83230a`, `321301d0`, `12ee8be5` |
| R15 | High | Holds in part | The meaning of non-priority trade mark expedites now rests on U103's decision (applicants' requests, compared across November 2018); `coalesce(priority_claims, 0)` still treats a missing count as none; "1 to 4 points ... below the size this stage looks for" still sets points against a 0-to-1 scale. `d1239afb`, `fd83230a`, `321301d0` |
| R16 | High | Holds | B11's heading still says "reach fewer countries"; the measure counts offices, among applications at IP Australia. `7bb3ecee` |
| R17 | High | Holds | B12 and its chart still say "citations within five years". `7a25fb76`, `7bb3ecee` |
| R18 | High | Holds in part | "Most of the gap goes with family reach", "reach is the main third factor" and "two readings of the same expected value" remain. The final `ELSE` would put a null office count in "5 or more", but the query's filter on citations makes nulls unlikely (not checked against data). `7a25fb76`, `7bb3ecee` |
| R19 | Medium | Holds | B15 still quotes `applicant_type` (the current holder) × route, 0.243 and 0.29, beside a table built on the filer; "divisionals doubled" is about shares. `c32476f3`, `46f31d3d` |
| R20 | High | Holds | "Made in Australia" and "made here" remain in B16, §1.9 and §8 (an open theme). `b30fd8d7`, `46f31d3d` |
| R21 | High | Holds | §1.6 still says WIPO's shares "confirm" Australia's estimates. `ec39ffe6` |
| R22 | High | Holds in part | B18 now says provisionals' estimates use the applicant's country; it still reports the overseas groups, heads "organisations' inventors include more women" without "Australian" (overseas individuals 16.6%, organisations 6.66%), and calls WA and NSW lowest beside the NT's 13.92%. `4e794326`, `a9201297` |
| R23 | Medium | Holds | "The field matters more than the filer" remains; the field-by-filer mix is not tabulated. `a9201297` |
| R24 | Medium | Holds | Textile and paper machines (39.7% to 15.9%) and provisionals' FY2012 to FY2014 fall (organisations 27.03% to 18.46%; individuals 23.59% to 15.41%) are still not discussed. `f243256f`, `4e794326` |
| R25 | High | Resolved (pass 5) | B19 is in endpoint terms; "valued most" is withdrawn. `7546a9f3` |
| R26 | High | Resolved (pass 5) | B19's cell adds the composition of overseas-held patents, with unknown reach counted. `5ef8906d` |
| R27 | High | Holds in part | B55 now uses `filer_group`; its route still calls every non-PCT application "direct"; families, calendar priority years and WIPO's foreign-oriented share are still set beside B11's applications. `8ff5a116`, `b38c4ca4` |
| R28 | High | Holds in part | B55 gained a limits paragraph, but its heading still gives "most" of the fall to records, "the FY2010 to FY2019 results stand" and "not a believable practice" remain, and Google Patents' share is 33.92% against WIPO's 64.6% in 2006 (differently defined), so the later decade's coverage is not shown either. `b3ed6e03` |
| R29 | High | Resolved (pass 3) | B11's heading, §1.9's rows and the notebook's status were restated. `7bb3ecee`, `12ee8be5`, `b29e8754` |
| R30 | Medium | Holds | B2's "individuals have no ABN", B4's "attorney markets are local" and B10's "Every interval is within about 1 point" remain (overseas individuals' designs: 33.8% to 40.0%). `2c348216`, `fb8284f8` |
| R31 | Medium | Holds | Lead tables still truncate at 90 characters; heatmaps still lack a key (S2 S8 R11). `7455cfd8`, `474fc7fd`, `876656ad` |

## Survival (years in force): the next theme

### R11 | High | §1.2, §1.4: what "in force after N years" measures differs by right and by cohort (carried, sharpened)

**Issue:** The checks the earlier audit asked for give these answers. **Eligibility:** `in_force` is empty for rights
never granted, so `in_force IS NOT NULL` does restrict the curves to granted or registered rights; it also drops 6,621
rights whose status ended them without an end date and 26 dated to end before their term began (`variables.yaml`), with
no count of how many fall in each cohort and group. **The anniversary:** a patent's cessation is dated 6 to 7 months
after the anniversary at which it was not renewed, at the end of the grace period (`variables.yaml`), so "in force after
10 years" for a patent means renewed through the ninth anniversary. Trade marks' and designs' ends appear to fall on the
anniversary itself (their records follow a median 198 days later, `build.py`'s notes), so "in force after 10 years (the
first renewal)" includes the renewal decision. The 0.1-year rounding the earlier audit questioned is harmless here: it
puts a trade mark's 10-year end (3,652 or 3,653 days, 9.9986 or 10.0014 years) at 10.0, inside the reading at 10
(`survival_with_interval` takes the last time not after the year); without it, about half those ends would fall just
after 10. None of this is stated. **Time origin and cohort:** curves run from the date of patent, but cohorts are
financial years of application, which for a PCT filing is national phase entry, about 19 months after its date of
patent; Stage 1's U36 used the date of patent for both. Overseas applicants file mostly through the PCT (B15), so the
origin groups' cohorts sit at different calendar times.

**Action:** State each right's convention beside every survival figure; count the ended-without-date rights by cohort
and group; define cohorts by the date of patent, as U36 does, or show the PCT share by group; keep the rounding and say
why it is there. Evidence: `ce1d1389`, `287a3efb`, `fd83230a`; `variables.yaml` (`in_force`, `years_in_force`);
`bivariate.survival_with_interval`; notebook 1, `c7c3060d` (U36).

### R12 | High | §1.2, B8, B10, B14, §1.9: survival read as renewal behaviour and as value (carried, sharpened)

**Issue:** The outputs are shares still in force; the text reads them as owners' decisions and value. §1.2 opens "How
long owners keep a right is a sign of the value they expect from it"; B10 and B14 speak of renewing, and §1.9 of
"renewed least". Stage 1's U36, on which these build, says "they are lifetimes on the register, not value"; `GLOSSARY.md`
calls a lifetime a measure of "how long owners judged the right worth its fees". A right's end can be a lapse for
non-payment, a surrender, a revocation or the end of its term, and a holder other than the filer may make the decision
(B19). Conditioning on grant adds immortal time: a patent cannot cease between its date of patent and its grant, so
groups granted later look more durable at early anniversaries. B13's five-year figures show it: not expedited 100% and
98.1%, expedited 99.3% and 97.3%.

**Action:** Write "share still in force at N years (granted rights)" in headings, tables and summaries; present renewal
decisions and value as interpretations that need separate evidence; reconcile §1.2 with U36 and the glossary; as a
sensitivity check, read early anniversaries from grant or start the curves at grant. Evidence: `2823d69c`, `fb8284f8`,
`321301d0`, `12ee8be5`; notebook 1, `c7c3060d`; `GLOSSARY.md` ("Lifetime (years in force)").

### R32 | High | B4, `screens.yaml`: the screen treats unfinished lifetimes as finished

**Issue:** `screens.yaml` screens `years_in_force` as an ordinary number. For a right still in force, that value is only
how long it has lasted so far (to the date in `in_force`), so the screen's measures, and B4's medians, mix finished and
unfinished lifetimes, which `GLOSSARY.md` says makes rights "look shorter-lived than they are". The discovery decade
(FY2010 to FY2019) is far more censored than the replication decade, so agreement between them is no check. B4's
"Lifetimes" bullet ("a median 9.41 years for class 04, 5 for class 02"; second-tier patents "China lowest, a median 2.54
years"; "6.54 years against 3.54") does not give survival medians. ADR 0030 treats only filing year against years in
force as cut short for recent rights.

**Action:** Drop `years_in_force` from the screen and keep `in_force`, or replace it with a censoring-aware measure (in
force at a fixed anniversary, among cohorts that reached it); restate B4's lifetime leads from survival curves, by
cohort. Evidence: `screens.yaml` (rights, `years_in_force: number`), `474fc7fd`, `2c348216`; `variables.yaml`
(`years_in_force`); `GLOSSARY.md` ("Unfinished (censored)"); ADR 0030, point 5.

### R33 | High | B8, §8, summary: survival is carried alone, against A1's condition, and the other signals disagree

**Issue:** The owner adopted years in force "as a working measure of how long owners keep their rights ... as long as it
is used alongside other signals" (A1, 25 October 2026). B8 carries it alone: "Australian organisations keep their
standard patents longer than overseas organisations do". The other signals of private value point the other way:
Australian organisations' patents are filed in fewer offices (B11: 40.68% in Australia only, against 8.23% for overseas
organisations) and are cited less (B12: a mean percentile of 32.3 against 52.3). B8's own third factor, "an
Australian-only patent has one set of fees", is a cost explanation that would lengthen narrow patents' lives without
implying more value. §8 ("keep patents longer than overseas ones, file them in fewer countries, and are cited less mostly
because of that narrower reach") and the summary ("narrower but kept longer") set the three side by side without
reconciling them.

**Action:** Read B8 with B11 and B12, as A1 asks: compare years in force within reach bands (Australia only, two to
four offices, five or more), which the lens allows, before carrying an origin gap; say in §8 that the signals disagree.
The owner has decided (A22, 2 November 2026): B8 stays a Stage 3 signal only as that comparison within reach bands,
worded as the share still in force and read beside B11 and B12. Evidence: `fb8284f8`, `7bb3ecee`, `de334709`;
`docs/owner-questions.md` (A1).

### R34 | High | B10, §1.9, summary: representation "on the record at any time" includes the renewal itself

**Issue:** `representation` rests on an agent being "on the record at any time" (`variables.yaml`, `has_agent`). For
grants, B6 notes that "the arrow can run backwards". For renewal the reverse path is stronger: an owner who renews often
does so through an attorney or a renewal service, which puts an agent on the record, while a right left to lapse needs
no one. B10's "Australians who file alone renew far less" (trade marks: with an attorney 52.0%, alone 28.6%; designs
47.2% and 28.9%) and §1.9's "lone filers" may therefore partly measure renewal, not representation at filing. B10 does
not say so.

**Action:** Use the agent on record at filing, or before the first renewal, if IP RAPID's party records carry dates;
otherwise state the reverse path beside B10, §1.9, §8 and the summary. Evidence: `287a3efb`, `fb8284f8`, `12ee8be5`;
`variables.yaml` (`has_agent`, `representation`).

### R35 | Medium | B13: the rise in expedited patents may be a different kind of request

**Issue:** Overseas organisations' expedited share rose from 0.84% (FY2003 to FY2009) to 8.0% (FY2010 on). B13's third
factor is "the urgency behind a request (a product on the market, a dispute)". Accelerated examination under work-sharing
arrangements such as the Patent Prosecution Highway, which rests on claims another office has already found allowable, is
a different request, made for patents already examined abroad, and it would be expected to go with grant and a longer
life. Whether IP RAPID's `exam_expedited` events include such requests is not checked, and the repository does not
mention them.

**Action:** List the event types behind `exam_expedited` by year, and read B13 by type of request before naming urgency
as the third factor. Evidence: `d1239afb`, `fd83230a`, `321301d0`; `build.EXPEDITED`.

### R36 | Medium | B8: the later cohorts' longer lives are read without the fee changes

**Issue:** "Every cohort lengthened its patents' lives in the later period, in line with U36" compares filings of FY2000
to FY2004 with FY2005 to FY2009 (overseas organisations 62.9% to 72.3% in force at 10 years). "Lengthened" implies a
change in behaviour, but the cohorts met different renewal fees (B49: the September 2002 rise moved cessations, and the
fees changed again in 2010, 2012 and 2016), differ in how often the founding applicant may be a later holder (before
FY2003, §1.2's caution, U35), and were examined under different practice.

**Action:** Describe the difference as one between cohorts; set it beside B49's dates; leave the cause open. Evidence:
`ce1d1389`, `fb8284f8`, `c5b83a0e`.

## Designs, and the record of leads

### R09 | High | B5, B6, §1.9: "registered ... whoever files" is the selection B3 warns against (carried, sharpened)

**Issue:** B6 says "Designs are registered without examination, so 99.4% to 100% are, whoever files." Its query keeps
rights with a known filer (`filer_group IS NOT NULL`), built from IP RAPID's founding applicants, and B3's table shows
that every lapsed and withdrawn design is of unknown origin in IP RAPID (100%), so B6's population holds almost no failed
designs. B3's own table counts them: 2,680 lapsed and 446 withdrawn designs filed FY2010 to FY2019 (4.6% of the 68,218
in the statuses shown) and 5,035 and 560 filed FY2000 to FY2009 (11.0% of 50,943) never registered. B3 concludes that
origin comparisons "must use the filled origin"; B5's and B6's design rows do not.

**Action:** Rerun B5's and B6's design rows with the register's filled origin (ADR 0029), or report registration for
all designs without origin; withdraw "99.4% to 100% ... whoever files". Evidence: `5c0b8418`, `ea1827ce`, `1f1747cd`,
`20488ed2`.

### R37 | Medium | §1.9: B4's leads that are not followed up are recorded nowhere

**Issue:** §1.9 lists B1 to B3 and B5 onward but not B4, whose leads include several followed up nowhere: the attorney
firm by state, trade mark classes by applicant type, the plant breeder's genus by origin and by time to grant, and
lifetimes by design class (R32). They are neither carried nor recorded as not carried, in §1.9, §8 or the summary.

**Action:** Add B4 to §1.9, with each lead's fate (followed up where, carried or not). Evidence: `2c348216`, `12ee8be5`.

## Review boundary and reproducibility

This file holds the status of the earlier audit's **31 findings** (4 resolved, 6 holding in part, 21 holding) and **9
issue/action entries**: 3 earlier findings restated with new evidence (R09, R11, R12) and 6 new ones (R32 to R37; 3 High,
3 Medium). It reviews §1's text, code and saved outputs and the definitions and helpers named above; it did not
re-execute the notebook or query the lenses. Claims about how ends are dated rest on the notes in `variables.yaml` and
`build.py`, not on the data. All 22 code cells have saved outputs, execution counts 2 to 23 in order, and no saved
errors. No notebook, code or website files were changed.

**Evidence locators:** B-numbers and section headings are searchable; eight-character identifiers are the notebook
JSON's stable cell `id` values (notebook 1's are marked). Findings in other files of this batch are cited as "S2 S8 R07"
and so on; the earlier ChatGPT findings keep their numbers, so "S2 L1 R12" is the same finding in both batches.

Repository commit: `cb544481aa64830e95c1ecd64260454baef41ed5`.

Reviewed notebook SHA-256: `3d250d2a14a58e9b4546c01601969bbe7d14e963f46b030276abbbd01a02b7e2`.
