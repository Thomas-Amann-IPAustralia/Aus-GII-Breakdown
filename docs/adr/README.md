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
| [0012](0012-rights-lens-stage-1-repairs.md) | Five repairs to the rights lens from its Stage 1 profile: attorney use excludes the applicant itself, the technology area is for patents only, two placeholder dates emptied, no time to registration for trade marks dated at filing, and a missing Australian state taken from the postcode | 2026-10-25 | Claude (owner asked for Stage 1 to begin) |
| [0013](0013-rights-parties-attachment.md) | The parties attachment: the founding applicant beside the current holder, whether the holder changed (not knowable for patents filed before FY2003), the main agent, and representation as attorney, other agent or self | 2026-10-25 | Claude (owner asked for the rights attachments, parties first) |
| [0014](0014-timeline-stage-1-repairs.md) | The timeline's series start where their records are complete (15 hand-set starts, past survivors, partial records and batch dates), and the 1995 rise of the patent term to 20 years is the 17th policy event | 2026-10-25 | Claude (owner asked for the next lens's Stage 1) |
| [0015](0015-rights-events-attachment.md) | The events attachment: each right's milestones (examination, acceptance, certification, opposition, assignment, extension of term) and its lifetime, with rights still in force counted as unfinished and trade marks and designs observed to March 2026 | 2026-10-25 | Claude (owner agreed to the events attachment next) |
| [0016](0016-firms-lens-stage-1-repairs.md) | The firms lens counts applications by the filer, adds what each firm holds (and holds in force), flags the ABNs only IPLORD links to IP, and repairs blank states | 2026-10-25 | Claude (owner asked for the firms lens next) |
| [0017](0017-regions-lens-stage-1-repairs.md) | The regions lens counts applications at the filer's postcode, adds organisations' counts and rates per person, shows a rate only where 10 or more applications would be expected, adds SA3s for pooling, and classes the postcodes that are not postal areas | 2026-10-25 | Claude (owner asked for the regions lens) |
| [0018](0018-regions-attachments.md) | The regions lens's attachments: every value of the Census, Data by Region, CABEE, PHIDU and the Clean Energy Regulator in a long table, `region_indicators`, reaching postal areas through 2021 residents by mesh block, and AusTender's suppliers, contracts and value in `regions` | 2026-10-25 | Claude (owner asked for the regions lens to be completed) |

Next free number: 0019.
