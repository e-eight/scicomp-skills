# Conventions

Read this before touching numerical code in this repo. Update it in the same session that
a new convention gets decided.

## What this code computes

<!-- One paragraph, at the level of the observable. -->

## Units and constants

| Quantity | Convention |
| --- | --- |
| Unit system | |
| Constants set to 1 | |
| Energy scale | |
| Time unit | |

## Signs and normalizations

| Object | Convention |
| --- | --- |
| Hamiltonian sign | |
| Fourier transform sign / prefactor | |
| State normalization | |

## Arrays and indexing

| Array | Shape | Axis meanings, in order | dtype |
| --- | --- | --- | --- |
| | | | |

- Indexing of physical objects (sites, modes, levels): 0-based / 1-based →
- Basis ordering →
- Memory layout assumptions →
- Boundary conditions and their representation →
- Working precision →

## Glossary

| Term | Means | Does **not** mean |
| --- | --- | --- |
| | | |

## Verification oracles

| Oracle | Applies at | Cost | Where implemented |
| --- | --- | --- | --- |
| Closed form | | | |
| Slow reference implementation | | | |
| Invariants preserved | | | |
| Known limits | | | |
| Published values | | | |

Largest size where each oracle remains affordable:

## Tolerances

| Context | rtol | atol | Justification |
| --- | --- | --- | --- |
| Default unit test | | | |
| | | | |

A tolerance loosened to make a test pass is a finding, not a fix. Record why in the commit
message.

## Randomness and determinism

- RNG library →
- Seed derivation (per run / per stream / per rank) →
- Where seeds are recorded →
- Accepted sources of nondeterminism →
- Unacceptable sources →

## Runs and artifacts

- Run output root →
- Run directory naming →
- Git-tracked / artifact store / ephemeral →
- May a production run come from a dirty working tree? →

## Compute environment

| | |
| --- | --- |
| Machines | |
| Scheduler | |
| Account / allocation | |
| Environment reconstruction | |
| Typical production wall time | |
| Typical memory | |
| May the agent submit jobs? | |

## Docs

- Notes →
- ADRs →
- Experiment records →
