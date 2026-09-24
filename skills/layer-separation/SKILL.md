---
name: layer-separation
description: Enforce the four-layer separation in research code — model (what the system is), method (how it is solved), driver (what gets run and recorded), analysis (what the numbers mean) — with a one-way dependency rule, a checker for violating imports, and guidance on when the separation is worth paying for. Use this when a research codebase is outliving its first paper, when swapping a model or solver turns out to require edits in several places, when a figure disagrees with the run it came from, when adding a second physical system or second numerical method to existing code, and when reviewing the structure of a group or shared simulation code.
---

# Layer separation

Model-invoked. Ships `scripts/check_layers.py`.

Most architectural advice doesn't transfer to research code, because most research code is
meant to be discarded when the paper ships and module depth is the wrong thing to optimize.
One rule survives the translation, and it survives because it buys two concrete
capabilities rather than an aesthetic:

- **Swap the model without touching the solver, and the solver without touching the model.**
  That's what makes the second physical system cost days instead of weeks.
- **Regenerate every figure from stored artifacts with the solver uninstalled.** That's what
  makes a figure traceable to the run it came from.

If a project needs neither, skip this skill. A 500-line single-use script is fine as it is,
and time spent on boundaries is time not spent on verification oracles.

## The four layers

**Model** — what the system *is*. Hamiltonians, operators, couplings, geometry, boundary
conditions, observables as mathematical objects. Knows physics. Owns the conventions in
`CONVENTIONS.md`: index ordering, basis ordering, units. Knows nothing about how anything
is solved.

**Method** — how it is *solved*. Integrators, eigensolvers, optimizers, samplers,
decompositions, tensor contractions. Knows numerics. Operates on whatever satisfies its
interface — a matrix, a callable applying an operator, a sampler — and never on "the Ising
model". Contains no `if model == ...`.

**Driver** — what gets *run and recorded*. Parameter sweeps, run directories, manifests,
checkpointing, scheduler interaction, logging. Knows bookkeeping. Knows neither physics nor
numerics; it wires the other two together and writes the results down.

**Analysis** — what the numbers *mean*. Reduction, fitting, extrapolation, error budgets,
tables, figures. Reads run artifacts from disk. **Never recomputes physics.**

## The dependency rule

```
driver ──> model
   └────> method
analysis ──> artifacts on disk (only)
```

Model does not import method. Method does not import model. Analysis imports neither. Each
arrow that doesn't appear above is a violation, and the most expensive one is an arrow out
of analysis.

Why that one matters most: the moment a plot script can recompute the physics, it will grow
its own copy of a formula, and that copy will drift from the one the run used. The figure
then disagrees with the data it claims to show, and nothing detects this — it just looks
like a result. Forcing analysis to read from disk makes the drift structurally impossible.

## Detecting violations

Three checks, in increasing strength.

**Import graph.** Run `scripts/check_layers.py`, which maps files to layers from a
`.layers.json` at the repo root and reports imports crossing a forbidden edge. Cheap enough
to run in CI.

**The swap test.** Add a second model (even a trivial one — a free particle, a two-level
system) and a second method (even a bad one — dense diagonalization). Count the files you
had to touch. If adding either required editing the other's layer, the boundary is fictional
regardless of what the directory tree says.

**The uninstall test.** Move the model and method packages aside and regenerate every figure
from stored run artifacts. If a figure script fails, analysis is recomputing something it
should be reading. This is the sharpest of the three and takes ten minutes.

## Violations worth naming

These are the ones that actually show up:

- A solver with a branch on which physical system it's given, or importing a specific
  Hamiltonian for a "default"
- A plot script that takes parameters and recomputes the observable, instead of reading it
- A model module that calls an eigensolver "just to check" — verification belongs in tests,
  where `numerical-verification` can see it
- A driver that knows the basis ordering or unpacks an index convention, rather than asking
  the model for a labelled result
- A method module that writes files or knows about run directory layout
- Checkpointing logic living inside the solver loop instead of arriving as a callback
- Analysis importing the model to build a reference curve — store the reference in the
  artifact instead, so the figure and the check share one source
- A single global config object read directly at every layer: the import graph looks clean
  and everything is coupled through the config anyway

## Fixing, in order

Do not undertake a general refactor. Take the cheapest cut with the highest payoff first:

1. **Sever analysis from everything else.** Make every figure script take run directories
   as input. This alone delivers figure reproducibility and usually takes an afternoon.
2. **Lift I/O and bookkeeping out of the method layer** into the driver. Usually mechanical.
3. **Define the interface the method needs from the model** — often just "apply this
   operator to a vector" plus a shape — and make the method depend on that interface rather
   than on a concrete model. This is the expensive one; do it when the second model arrives,
   not in anticipation of it.

At each step, the verification oracles must still pass. A refactor of numerical code without
a slow-twin test to compare against is not a refactor, it's a rewrite with extra confidence.
Read `numerical-verification` before starting one.

## Recording the boundaries

Once the layers exist, add the mapping and the dependency rule to `CONVENTIONS.md`, and an
ADR for the model/method interface — that choice is the one a future contributor will want
the reasoning behind. Add `check_layers.py` to CI so the boundary erodes visibly rather than
silently.
