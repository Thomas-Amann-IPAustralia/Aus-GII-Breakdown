# 0021: The institutions lens: research institutions by ROR and year, through a reviewed link to names and ABNs

**Date:** 2026-10-26. **Whose:** Claude's (the owner asked for the `institutions` lens, 2026-10-26); the owner can
overturn any of it, and OQ11 asks whether someone who knows the sector should review the link. It builds the last lens
ADR 0007 planned and attaches the tables the plan maps to it (OpenAlex, Reliance on Science, the ARC and NHMRC
grants), with Google Patents and AusTender. The evidence is in `analysis/notebooks/01_univariate.ipynb`, section 7
(observations U80 to U87).

**Context.** ADR 0007 set the unit: an Australian research institution (identified by ROR) and year, holding research
output and citations, citations from patents, ARC and NHMRC grants, and the IP the institution files. None of the
sources shares a key with IP RAPID: OpenAlex carries each institution's ROR, the NHMRC gives the administering
institution's ROR only from its 2025 round, the ARC gives names, and IP RAPID gives the filer's name and, from about
2000, an ABN. Universities often file through companies they own (UNSW through NewSouth Innovations, formerly
Unisearch), and many institutions have changed name or merged (the Howard Florey Institute, the Mental Health Research
Institute and the National Stroke Research Institute into the Florey; the University of Adelaide and the University
of South Australia into Adelaide University, 2026). The corpus held no list of research institutions.

**Decision.**
1. **A new corpus source, `ror`:** every Australian record in ROR's data dump (v2.15, 20 October 2026; 2,052 records,
   active, inactive and withdrawn), with every name, alias and acronym (`names`) and every relationship (parent,
   child, related, predecessor, successor). ROR's API is not used: its pages are not in a stable order, so paging
   through a query returned 2,052 rows for 1,518 records.
2. **The institutions (130):** every Australian university (44, including Adelaide University and its two
   predecessors, which keep their own rows); 11 public research agencies (CSIRO, Data61, ANSTO, DSTG, AIMS,
   Geoscience Australia, the Bureau of Meteorology, the Australian Antarctic Division, the Australian Astronomical
   Observatory, the National Acoustic Laboratories and SARDI); 46 medical research institutes (those the NHMRC classes
   as research institutes, the members of the sector that file IP, and Peter MacCallum); and every other organisation
   that administered an ARC or NHMRC grant (4 other research institutes, 7 health services, 18 others: academies,
   museums, foundations). Each is in `analysis/eda/institutions/institutions.csv`, with its kind and, where it is part
   of another, its parent (Data61, the Royal Melbourne Hospital, the Australian Maritime College).
3. **Names.** A filer, grant holder or supplier belongs to an institution if its name matches one of the institution's:
   ROR's names, labels and aliases (not its acronyms), and 116 reviewed names in `names.csv` (former names,
   predecessors, commercialisation companies, divisions and misspellings), each marked with the sources it applies to.
   Names are compared without case, apostrophes, punctuation, "the" or legal suffixes (`_name_key`). Only the lens's
   institutions' names are used, so a name ROR gives two records (a hospital and its foundation) is not ambiguous
   unless both are in the lens; a test checks that no name points to two institutions.
4. **ABNs (146)**, in `abns.csv`: each institution's own, its commercialisation companies' and controlled entities',
   and its predecessors', found from the filers matched by name and from the ABR's names, then reviewed (six were
   rejected: namesakes, and an ABN on another body's record). In IP RAPID a name decides: an ABN matches only a filer
   whose name does not (the University of Sydney's ABN appears on seven rights that name UTS).
5. **IP by the filer** (ADR 0013, 0016): a right belongs to an institution if the institution is among its founding
   applicants or owners, in Australia or of no recorded country (old records), and not an individual. The detail is
   a companion table, `institution_rights` (31,528 rows: one per right and institution), joinable to `rights`, with
   how it was matched and whether the right was filed with others. **Plant breeder's rights are left out:** IP RAPID
   gives their applicants' names as codes, with no ABNs.
6. **The core lens, `institutions`:** one row per institution and calendar year, 1990 to 2026 (4,810 rows), because
   OpenAlex, the ARC and the NHMRC count by calendar year. Each column is empty outside its source's years:
   - OpenAlex's works and citations by year (2010 on), at the institution's own OpenAlex record (a work with authors
     at two institutions counts for both; a child's works are not added to its parent's);
   - US patents' citations to the institution's works, by the work's publication year (Reliance on Science through
     `openalex_works`), and those from patents whose family has an Australian applicant or inventor;
   - ARC grants by the year funding starts, at the organisation that won the grant (at announcement), from 2001, with
     the industry-partner schemes counted apart (`ARC_INDUSTRY_SCHEMES`: Linkage Projects, the Industrial
     Transformation hubs and centres, the industry fellowships). The ARC's "Linkage" program also holds the Centres of
     Excellence, infrastructure and the learned academies' projects, so it is not a measure of work with industry;
   - NHMRC grants by round (2013 on), at the administering institution (its ROR from 2025, its name before);
   - IP applications by type, by the year of the application date (for a PCT filing, its national phase entry), and
     standard patents filed with another founding applicant;
   - the Google Patents families of the institution's Australian patent applications, by the year of first priority,
     those granted in the US, and the families citing them within five years;
   - AusTender contracts with one of the institution's ABNs as supplier, by the year first published, each contract
     once at its latest notice (ADR 0010).

**Use.**
- Count a university's IP with its companies: UNSW files 96.5% of its patent applications through NewSouth
  Innovations (U81).
- Never add works or citations across institutions as if they were distinct, or a child's to its parent's.
- Patent citations to recent works, and families' citations, are still accumulating: compare cohorts of the same age.
- Families filed only abroad are not found (the review's F07); 97.0% of the institutions' standard applications are
  found, 4.3% of their provisionals (U85).
- The `regions` lens's postal-area counts miss half the universities' standard patents (U87); `institution_rights`
  and ROR's locations can place them.

**Rejected.**
- **Fuzzy name matching.** It would find more variants, but also namesakes (a "Newcastle University" in England); the
  reviewed list finds the variants that matter (eight of CSIRO's spellings) and says which.
- **Rolling children into parents.** OpenAlex's counts overlap, and NICTA (now Data61) was independent until 2016.
- **Cooperative research centres and rural R&D corporations as institutions.** CRCs are joint ventures of
  universities, agencies and firms, so their filings are not one institution's; the R&D corporations fund research
  rather than do it. Both can be added as their own kinds if Stage 2 needs them.
- **Matching Google Patents' assignee names.** They are abbreviated ("AGRICULTURE VICTORIA SERV PTY"); families are
  reached through the institutions' Australian applications instead.

**Checked.**
- `tests/test_eda.py`: one row per key in both tables; every institution, name and ABN names a ROR record, each ABN
  one institution, no name key two institutions; the name key agrees across spellings; the lens holds all but 14
  of the ARC's grants and 15 of the NHMRC's (secretariats, networks and foundations outside the lens); its IP counts
  equal its links to rights; every institution has every year.
- The tables as built: `institutions` 4,810 rows and 30 columns; `institution_rights` 31,528 rows and 7 columns.
