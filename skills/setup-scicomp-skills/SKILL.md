---
name: setup-scicomp-skills
description: Configure a scientific computing repo for the scicomp skill set — builds CONVENTIONS.md (units, index and sign conventions, glossary, oracle inventory, tolerance policy, RNG policy, run directory layout, compute environment). Run this once per repo before using design-experiment, numerical-verification, run-provenance, error-budget, numerics-review, or scale-down-first. Use it whenever those skills find no CONVENTIONS.md, whenever a user starts a new simulation or analysis repo, and whenever someone asks how to set up a research codebase for agent work.
disable-model-invocation: true
---

# Setup: scientific computing skills

User-invoked. Run once per repository.

The other skills in this set read `CONVENTIONS.md` and will nag you if it's missing. This
skill produces it, by interviewing the user.

## Why this matters more than it looks

Most wrong numbers in research code come from a convention mismatch, not a bug: someone
assumed the first axis was time and it was space, someone set ħ=1 in one module and not
another, someone's lattice was 0-indexed and the analytic formula was 1-indexed. These are
invisible in review because nobody wrote the convention down. Writing it down also buys
concision — "the Trotter step" beats "the time slice you split the Hamiltonian into" in
every subsequent session, and costs fewer tokens to think about.

## Procedure

Interview the user one question at a time. Don't batch. Don't guess an answer from reading
the code — code shows what was done, not what was intended, and you're trying to catch
places where those differ. If the code contradicts what they tell you, that's a finding:
report it.

Ask in this order, skipping anything already unambiguous in the repo:

### 1. What does this code compute

One paragraph, at the level of the observable, not the implementation. If they can't
state it in a paragraph, that's the first thing to fix.

### 2. Conventions

Work through these explicitly. For each, the answer goes in the file even if it's "the
obvious one" — the point is that it's no longer implicit.

- Unit system and which constants are set to 1
- Sign conventions (Hamiltonian sign, Fourier transform sign, metric signature)
- Normalization conventions (Fourier prefactor, state normalization, measure)
- Index and axis conventions: what each dimension of the main arrays means, in order
- 0- vs 1-indexing for physical objects (sites, modes, levels, time steps)
- Basis ordering, and whether it's consistent across modules
- Memory layout assumptions (row/column major, contiguity requirements)
- Boundary conditions and how they're represented
- Real vs complex dtype, and the working precision

### 3. Glossary

Every term the project uses that a competent outsider would misread: overloaded words,
in-group shorthand, anything with a different meaning in a neighbouring subfield. Aim for
10–30 entries. Push back when a term is defined circularly.

### 4. Oracle inventory

Which independent checks exist for this code, and at what cost. See `numerical-verification`
for the full ladder. Record concretely:

- Closed-form or exactly solvable cases, with the sizes and regimes where they apply
- A slow reference implementation, if one exists — and if not, flag that as the highest
  priority piece of missing infrastructure
- Invariants the code should preserve: conservation laws, normalization, positivity,
  hermiticity, unitarity, symmetries, sum rules
- Known limits that must be recovered, and known published values to reproduce
- The largest size where each oracle is still affordable, in wall time

### 5. Tolerance and determinism policy

- Default relative and absolute tolerance for tests, and the justification
- Which RNG library, and how seeds are derived and recorded (per-run, per-stream, per-rank)
- Which sources of nondeterminism are accepted and why (BLAS threading, reduction order,
  GPU atomics), and which are not

### 6. Runs and artifacts

- Where run outputs land, and the directory naming scheme
- What's git-tracked, what's in an artifact store, what's ephemeral
- Whether uncommitted code may be used for a production run (recommend: no; see
  `run-provenance`)

### 7. Compute environment

- Local, cluster, or both; scheduler; account or allocation; typical partition
- How the environment is reconstructed (module loads, container, lockfile)
- Typical wall time and memory for a real run — needed by `scale-down-first`
- Whether the agent may submit jobs, or only prepare scripts for the user to submit

### 8. Docs

Where notes, ADRs, and experiment records live.

## Output

Write `CONVENTIONS.md` at the repo root from `assets/CONVENTIONS.template.md`, filling in
what the interview established and leaving explicit `TODO` markers for anything the user
deferred. A `TODO` is honest; a plausible guess is worse than a blank.

Then add a pointer to `AGENTS.md` or `CLAUDE.md` so every session picks it up:

```markdown
## Conventions
Read `CONVENTIONS.md` before touching numerical code. It defines the unit system, index
and sign conventions, the project glossary, and the verification oracles available.
```

Finally, tell the user the one rule that keeps this alive: **when a new convention gets
decided mid-session, it goes into `CONVENTIONS.md` in that same session.** A conventions
file that lags the code is worse than none, because it will be trusted.

For decisions with real alternatives — a choice of basis, a discretization scheme, a
solver — write a short ADR in the docs directory instead of a glossary line: the
alternatives considered, why this one, and what would make you revisit it.
