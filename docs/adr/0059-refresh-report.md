# 0059: What a re-run would move: bindings, a re-run in a copy, and lens fingerprints (the report-only part)

**Date:** 2026-11-12. **Whose:** the owner's ("Yes to OQ38, build the report-only part first", A43); Claude's (how),
which the owner can overturn. The plan is `docs/plan-refresh-check.md`; this builds its steps 1 to 4. Steps 5 and 6
(drafting the changes, and a tripwire for the words) are not built.

**Context.** A data refresh was noticed (ADR 0058) but not followed through: nothing checked that an observation's
words still matched what its cells would now produce, and the owner was reluctant to re-run the reviewed notebooks to
find out, since a re-run changes outputs and may force the prose to change. A new source or a change to the lens code
could also change a column that existing observations read without any source file changing.

## Decision

1. **Lens fingerprints** (`eda.fingerprint`, `analysis/eda/fingerprints.json`, committed). For each of the 11 lens
   tables: its row count, and for each of its 388 columns a digest of the values (the sum of each value's MD5, kept
   to 64 bits: it ignores row order, changes if any value does, and does not cancel on repeats). Reproducible: four
   tables rebuilt and fingerprinted again were identical. About four minutes for all 11.
2. **The currency check rests on them.** An observation's fingerprint gains a fifth part, the lens tables it reads:
   its own lens's tables and any other its cells name (erring wide on purpose). When a lens table's fingerprint
   changes, every such observation waits, as it does for a changed source file.
3. **Bindings** (`atlas.refresh`), worked out from the reviewed notebooks each time, never stored. A place is named
   by labels, not positions: in a table, the cell's notebook id, the row's label and the column's label; in printed
   text, the line with its numbers masked. Each number an observation quotes is bound to its places as written,
   rounded, as a percentage, in thousands or millions, or as read on another observation's page. Old values quoted in
   dated notes and section numbers are set aside as history. Years and one-digit numbers are not bound; a two-digit
   number only where exactly one place holds it.
4. **A re-run in a copy.** `atlas.refresh run` executes each notebook with the kernel working where the notebook
   lives and writes the result to `analysis/atlas/refresh_runs/` (gitignored). The reviewed file is only read. No
   cell of the three notebooks writes a file.
5. **The report** (`atlas.refresh report`, `docs/refresh-report.md`): for each observation, every bound number read
   again at its place: the same, moved (old and new), place gone, or under a cell that failed. Where the prose
   already states the new value (a dated correction made ahead of its output), it says so.
6. **Clearing the wait** (`atlas.refresh confirm`): an observation waiting on a changed source or lens table whose
   bound numbers all came out as quoted is confirmed with that as the reason, and how many of its numbers were not
   traced. The others are left for a person.

## What was measured

**Bindings.** Of 5,778 quoted numbers that are claims (107 more are history):

| How the number is bound | Numbers | Share |
|---|---:|---:|
| As written, at one place | 4,209 | 72.8% |
| As written, at several places | 705 | 12.2% |
| A share given as a percentage | 459 | 7.9% |
| Rounded, or in thousands or millions | 89 | 1.5% |
| Read on another observation's page | 75 | 1.3% |
| Not traced (arithmetic, a chart, outside the outputs) | 241 | 4.2% |

**The first re-run, 12 November 2026** (the corpus and code as committed; no data had changed). Run times: notebook 1
in 2 min 55 s, notebook 2 in 7 min 32 s, notebook 3 in 17 min 4 s; no cell failed.

- **229 of 231 observations: every traced number exactly as quoted** (5,460 of 5,462 numbers). The three notebooks
  reproduce, the random-number cells included.
- **U1: "89 columns" is now 90.** Stage 3 added `name_matched_abn` to the rights lens (ADR 0045, 0047), and U1's
  overview cell was not run again; its count of columns by attachment (29 core and 60 from seven attachments) leaves
  the new one out. Not amended here: the owner asked for the report first (OQ40).
- **U22: its stored output says 79 columns, its prose says 86.** The prose was corrected on 10 November (ADR 0057)
  without the cell being run again; the re-run agrees with the prose. Nothing to amend.

## Consequences

- A refresh, a new source or a change to the lens code now ends in a list: `eda.build`, `eda.fingerprint`,
  `atlas.refresh run`, `report`, `confirm`. About half an hour of machine time, free, and nothing reviewed is touched.
- The check is only as wide as the bindings: 241 quoted numbers are not traced, charts are not compared (a number
  that exists only in a drawing), and a two-digit number is traced only where it sits at one place. A re-run could
  move those unseen.
- `eda.build` ran out of memory building every lens in one go in this environment (15 GB) while its tables were
  downloading; built one lens at a time it completes. Not changed.
- The baseline is as of this run: every review carries the fingerprints of the lens tables as built on 12 November.
  U1 is known to be out of step and is recorded in the report and in OQ40, not in the gate.
