# notes/

Reasoning lives here. Results do not — those go in `runs/` with manifests, so that every
number keeps its provenance. A value pasted into a markdown file has none, and will outlive
the run that produced it.

## Two kinds of file

**Living documents** are rewritten in place and always state current belief. They carry
`**Updated:**`.

- `problem.md` — what this project is
- `literature.md` — what's known
- `conventions-sources.md` — how each paper writes things

**Append-only records** are written once and never edited. They carry `**Status:**`.

- `derivations/` — frozen once verified, because code cites their equation numbers
- `experiments/` — one per experiment, dated
- `decisions/` — ADRs; superseding one means writing a new one
- `log.md` — session log, newest first

Mixing the two is how a notes directory dies: once you can't tell whether a file is current,
you stop trusting all of them. Every file carries a status line and a date at the top for
exactly this reason.

## Conventions

- Derivations are **numbered, not dated** — the filename is an address that code cites, so
  it must be stable. Corrections go in as a new section with the old one struck through.
  A renumber that breaks citations is worse than an ugly file.
- Experiments are **dated**, one per file, and keep their status line current. An abandoned
  experiment with its reason recorded is worth more than an orphaned file.
- No scratch directory. Algebra either becomes a derivation record or is disposable.

## Which skill writes what

| File | Skill |
| --- | --- |
| `problem.md` | `scope-the-question` |
| `literature.md`, `conventions-sources.md` | `literature-map` |
| `derivations/NN-*.md` | `derive` |
| `experiments/YYYY-MM-DD-*.md` | `design-experiment` |
| `decisions/NNNN-*.md` | `derive`, `setup-scicomp-skills`, `layer-separation` |
| `log.md` | `handoff` |
