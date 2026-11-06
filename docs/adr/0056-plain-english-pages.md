# 0056: The rest of each observation page in plain English, and one meaning for "Australian applications"

**Date:** 2026-11-06. **Whose:** the owner's (what: OQ32, answered A40, "Go ahead with #1. You must ensure that they
still read well as plain english"); Claude's (the wording, the measure of plain English, the rule changes), which the
owner can overturn.

**Context.** ADR 0055 put the notebook's plain-English reading at the top of each observation page. The rest of the
page was the atlas's own wording, written for analysts: headlines averaging 18 words (up to 31), and method notes,
figure labels and Stage 3 tables full of "held together", intervals, hazard ratios, components, crosswalks, cohorts,
leads and screens. The readings also used "Australian standard patent applications" for every applicant's
applications in Australia in some places and for Australians' own in others.

**Decision.**

1. **A measure of plain English, so "reads well" is checked, not asserted.** Each visible field is scored for
   technical terms per 100 words (a list of about 70: interval, hazard ratio, held together, component, crosswalk,
   cohort, lens, lead, screen, median, decile, percentile, log, negative binomial and the like), words per sentence and
   Flesch reading ease. Every item with a technical term, a sentence over 25 words, or a number not on the page was
   rewritten, about 880 of 3,379; the rest were already plain and are unchanged. Result, over every observation page:
   technical terms 2.47 per 100 words before, 0.04 after (Stage 3's tables 6.27 to 0); reading ease 67.1 both (it
   counts syllables, and plain wording here still needs words such as "applications" and "organisations"); no sentence
   over 30 words but a handful of lists. What remains is glossary-linked on purpose (survival curve, Tweedie, ANZSIC
   and SEIFA named in brackets after the plain words).
2. **Headlines.** All 231 rewritten as one idea in at most 21 words (average 14, from 18), never stronger than the
   finding (observational ones say "goes with", not "makes"), and checked against each reading. Eight were corrected
   on a second pass where the first draft lost a qualifier (U5, U6, U10, U25 said "patents" where only standard
   patents fit; U21's share is of attorney-filed applications; U120's scope; B12 and B44 read as causes).
3. **Plain conventions**, used throughout: "allowing for" (not "held together"); "likely range" (not "interval");
   "typical" (not "median"); "summary measures" (not "components"); "the method that assigns patents to industries"
   (not "crosswalk"), "estimated counts" (not "expected counts"); "comparison months" (not "placebo months");
   "patterns worth following up" (not "leads"); "times as likely to end in a given year" (not "hazard ratio");
   "original applicant" or "applicants named at filing" (not "founding applicant"); financial years written the
   Australian way ("2025–26", not "FY2026"). The page code's fixed labels follow: "Stage 3 allowed for", "Each
   comparison", "On its own, then allowing for the rest".
4. **"Australian ... applications".** "An Australian patent" or "trade mark" is a right granted or registered in
   Australia, and stays. Where a reading meant every applicant's applications it now says "applications in Australia",
   and where it meant Australians' own, "Australians'" or "Australian applicants'". 28 readings changed in the
   notebooks, each with a dated note giving the supplied wording; no original observation changed (re-read and
   compared, as in ADR 0055).
5. **The numbers rule now covers every visible field, with one allowance.** It had checked only the headline,
   statement, figures, points, Stage 3 tables and revisits; now also the questions, preparation, steps, assumptions,
   limits, next steps and what was held. That found numbers on 31 pages that are not on their notebook's page (for example
   U47's 165 and 3,977 firms, U109's 36 years, M36's 1,000 resamples), each removed or reworded. The words may now
   round as a reading may (ADR 0055); a financial year written in full or short ("1999–2000", "2007–08") passes if its
   last year is on the page. A quoted chart's values must still be on the page exactly.
6. **Repairs on the way.** Three Stage 3 "held" lists split an item at a comma inside brackets (M14, M22, M23), so the
   page showed broken chips; each is now quoted. One glossary link Claude first wrote (`seifa`) has no entry, which
   the build caught; it links to `irsad`.

**Not changed.** The Stage 3 outcome names ("not detected once held", "appears once held") are ADR 0046's defined
vocabulary, counted and defined on the Stage 3 page, and the section titles under each page's badges are the
notebooks' own headings; both still read technically and are OQ34. The notebooks' original observations, the charts
and the analysis are untouched. The YAML's `statement` and `points` (not shown since ADR 0055) were not rewritten.

**Consequences.** The edits were made in place in the YAML, so the diff shows only changed sentences. The strict build
passes (231 pages); 99 tests pass (44 need the lens tables); the chat's passages are rebuilt (4,519) and reach the chat
only when Econ is refreshed (OQ33).
