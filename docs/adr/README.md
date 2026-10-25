# Decisions (ADRs)

One file per decision, numbered and dated, written in plain English. They are append-only: to change a decision,
write a new ADR that supersedes the old one and name the old one in it. Each ADR says whose decision it was:
the owner's, or Claude's, which the owner can overturn.

| # | Decision | Date | Whose |
|---|---|---|---|
| [0001](0001-working-agreement.md) | Claude gets on with the work and asks only about direction, money, adoption and outward-facing actions | 2026-10-23 | Owner |
| [0002](0002-eda-in-three-notebooks-by-lens.md) | The EDA is three notebooks (one per stage), each organised by four lenses (five from 0006; its rule for other sources is superseded by 0007) | 2026-10-23 | Owner (stages), Claude (lenses) |
| [0003](0003-duckdb-first-context-safe-analysis.md) | Aggregate in DuckDB; notebooks committed with outputs; lens tables rebuilt, not committed | 2026-10-23 | Claude |
| [0004](0004-evidence-conventions.md) | Numbered, evidenced observations with a strength label; plain English; accessible charts | 2026-10-23 | Owner (principles), Claude (format) |
| [0005](0005-lens-definitions-v1.md) | How the four lenses are defined, and their known limits | 2026-10-23 | Claude |
| [0006](0006-timeline-lens.md) | Add a fifth lens: Australia over time, one row per month | 2026-10-23 | Owner (the lens), Claude (its contents) |
| [0007](0007-every-dataset-through-every-stage.md) | Every dataset goes through all three stages: each table attached to a lens, two new lenses (industries, institutions), repairs before each table's Stage 1 section | 2026-10-25 | Owner (the principle and the two lenses), Claude (how) |
| [0008](0008-inventors-from-one-publication-per-family.md) | Count a patent family's inventors from one representative publication, borrowing countries from the rest of the family, because counting every name nearly doubled them | 2026-10-25 | Claude |
| [0009](0009-rights-lens-repairs.md) | Repair the rights lens: applicant origin has three values (unknown is not overseas), patents are split into standard, provisional and second-tier everywhere, and raw applicant locations are kept | 2026-10-25 | Claude (owner asked for the repairs) |
| [0010](0010-lens-definitions-v2.md) | Lens definitions, version 2: contracts counted once, R&D from the latest report, age labelled honestly, census zeros empty, OECD R&D beside the World Bank's, and a timeline without false zeros at either end, with trade mark registrations by the date entered | 2026-10-25 | Claude (owner asked for the last check before Stage 1) |
| [0011](0011-corpus-repairs-and-reprocessing.md) | Corpus repairs: every published value kept, one row per key, AusTender's amendments in order, every policy date checked against the Federal Register, and `corpus reprocess` to rebuild from stored raw files | 2026-10-25 | Claude (owner asked for the last check before Stage 1) |

Next free number: 0012.
