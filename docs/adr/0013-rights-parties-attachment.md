# 0013: The parties attachment: who filed a right, who holds it, and who represents them

**Date:** 2026-10-25. **Whose:** Claude's (the owner asked for the `rights` attachments, parties first); the owner can
overturn any of it. It carries out the review's B1 and reports N02 (S7). It extends ADR 0012's repair of `has_agent`.
The evidence is in `analysis/notebooks/01_univariate.ipynb`, section 1.8.1 (observations U17 to U21).

**Context.** The `rights` lens took its applicant from IP RAPID's first *current* applicant, so it described who holds
a right now. The research questions also ask who files and from where (Q2), and the review found that the holder's
postcode differs from the filer's for about a tenth of rights (N02). ADR 0012 showed that IP RAPID's "agent" is the
address for service and left open how many of the remaining agents are attorneys.

**Decision.** Twelve columns join the `rights` lens from `iprapid/party`:
1. **The founding applicant** (who filed): `founder_count`, `founder_type`, `founder_country`,
   `founding_australian` (three-valued, over every founding applicant), `founder_postcode` and `founder_state` (the
   first Australian founding applicant's, the state filled from the postcode as in ADR 0012), and `founder_abn` (the
   first founding applicant with one). Each founding applicant is taken as first recorded (its earliest row), and the
   first is ordered by that date, then party id, as the loader orders current applicants. The `applicant_*` columns
   keep describing the current holder.
2. **`holder_changed`:** the founding and current applicants differ, compared by party id. IP RAPID keeps a party's id
   through changes of address (a party can have several rows), so ids, not rows, are compared. It is empty for
   patents filed before FY2003: IP RAPID keeps one set of applicants for them, first recorded a median 5,974 to 7,445
   days after filing (FY1998 to FY2002, against 3 to 8 days from FY2003), so a change of holder was not kept, though
   14.61% to 16.1% of those patents have an assignment event. Their founding columns may describe a later holder.
3. **The agent:** `agent_id`, `agent_name` (organisations only; IP RAPID gives individuals as pseudonymised codes) and
   `agent_clients`: of the right's agents who are not its applicants (ADR 0012), the one acting for the most distinct
   applicants across the whole register.
4. **`representation`:** `attorney` if that agent acts for five or more applicants, `other_agent` if it acts for
   fewer (often a related company or an in-house department), `self` if there is no agent but the applicant, and
   empty for provisional applications. `has_agent` is unchanged in meaning: it is true for `attorney` and
   `other_agent`.

**Use.** "Where and who files" uses the founding columns; "who holds" uses the applicant columns. The `regions` and
`firms` lenses still count applications by the current holder; each switches to the filer in its own Stage 1 section,
before its profiles, as ADR 0007 asks.

**Rejected.**
- **Comparing founding and current applicants by row or by name.** Rows multiply with changes of address (for trade
  marks, most founding rows are no longer current, while the set of holders changed for 15.3%); names change with
  spelling. Ids track the party.
- **Treating "no change" as true for patents before FY2003.** It would read a gap in the record as stable ownership.
- **Classifying attorneys by name** ("patent", "attorneys", "IP"). Many firms' names carry none of these words
  (Spruson & Ferguson, Griffith Hack), and in-house departments often do ("intellectual property bluescope steel").
- **A threshold other than five.** The notebook shows the shares at 1, 2, 5, 20 and 100 applicants. For standard
  patents and designs they barely move; for Australian trade marks they run from 57.08% to 42.59%, so Stage 2 gives
  the shares at 1 and 20 beside the lens's. Plant breeder's rights have few agents, so for them attorney and other
  agent are read together.
- **Corporate groups of attorney firms.** IP RAPID does not record them; concentration by firm name is a lower bound.

**Checked.**
- `tests/test_eda.py`: `representation` is empty exactly for provisional applications; `self` exactly where
  `has_agent` is false; an attorney acts for five or more applicants; a right with no founding applicant has no
  founding origin or holder comparison; a founder postcode belongs to an Australian founding applicant; every founder
  state is one of the eight; and no patent filed before FY2003 has a holder comparison.
- The lens as built: 4,368,006 rows and 41 columns (29 core and 12 from the parties). The other lenses are unchanged.
