---
name: derive
description: Work through a mathematical derivation with checks at every step — assumptions stated up front, dimensional analysis on each equation, limiting and special cases checked as you go, symbolic verification with sympy, and a numerical spot check of the final expression against brute force at small size — then record it as numbered equations that code can cite. Use this whenever a user is deriving, expanding, transforming, or simplifying anything analytically; whenever a formula is about to be implemented in code; whenever an expression from a paper needs to be adapted to a different convention or regime; and whenever a derivation result is surprising or disagrees with a simulation.
---

# Derive

Model-invoked. Ships `scripts/check_identity.py`.

A derivation that only gets checked at the end is checked once, badly. This skill front-loads
the assumptions and threads cheap verification through every step, so an error is caught
three lines after it's made rather than three weeks later when the simulation disagrees with
the analytics and nobody knows which one is lying.

It also produces the artifact the rest of the pipeline needs: numbered equations in a file,
so code can say `implements Eq. (17) of notes/derivation-xyz.md` and a reviewer can check it.

## Before any algebra

Write the assumptions down first, in the record, as a numbered list. Do not start until
these are explicit:

- What is being expanded in, and what is assumed small relative to what
- The regime of validity: which parameters, which limits, what must stay finite
- Structural assumptions: spectral gap, regularity, boundedness, positivity, commutation
- Which terms will be dropped and at what order
- Which conventions are in force — sign, units, normalization, index ordering — and whether
  they match `CONVENTIONS.md`

Half of all derivation errors are an assumption that was implicit at step 3 and violated at
step 11. Listing them up front is the only defense, because nobody notices a violated
assumption they never wrote down.

If the user can't state the regime of validity, that's the first thing to resolve. A result
without one isn't a result.

## Per-step discipline

For each line of the derivation, do all four. They are individually cheap and collectively
catch almost everything.

**Label the move.** Every step is one of: an exact identity, a definition, a convention
choice, or an approximation. Say which, in a word. Approximations additionally carry the
order of the discarded term. A step that can't be labelled is a step that isn't understood.

**Dimensional check.** Every equation, every time. Both sides, including inside exponentials,
logarithms, and trigonometric functions — an argument with dimensions is an error even when
the prefactors work out. In natural units where constants are set to 1, track the one
remaining scale explicitly rather than trusting that everything is dimensionless.

**Order bookkeeping.** When a term is dropped, record what it was and its order. At the end,
the accumulated discarded terms tell you the accuracy of the result — and that number goes
straight into `error-budget` as the model error.

**Special-case check.** Not at the end — as you go. Cheap ones, at the current line:

- Set a coupling, a field, or an interaction to zero and confirm you recover the known
  simpler case
- Check symmetry properties survive: hermiticity, reality, positivity, behaviour under
  exchange, parity, time reversal
- Check counting: does the expression have the right number of terms, the right degree, the
  right number of independent components
- Take a limit where the answer is known independently
- Check the sign in a regime where you know the sign on physical grounds

## Symbolic verification

Use sympy wherever the expressions are small enough. Three tactics that work better than the
obvious one:

**Verify identities numerically, not by simplification.** `simplify(A - B) == 0` frequently
fails to close even for true identities, and its failure tells you nothing. Substituting
random values for every free symbol and comparing, repeated a few times at high precision,
gives a decisive answer in milliseconds. `scripts/check_identity.py` does this; use it rather
than fighting `simplify`.

**Verify expansions with `series`,** and check that the order of the first neglected term
matches what you claimed in the order bookkeeping.

**Verify operator algebra on explicit small matrices.** A commutator identity, an
anticommutation relation, a transformation rule — instantiate at the smallest nontrivial
size with random matrices and check numerically. This catches dropped conjugations and
transposed indices, which are invisible in index-free notation.

## The numerical spot check

Before the derivation is considered finished, instantiate the final expression at small size
and compare it against brute force — direct summation, exact diagonalization, whatever the
unapproximated computation is. Do this at several parameter points, including at least one
awkward one.

This is the step that connects to everything downstream. The brute-force computation you
write here is the first entry in the project's oracle inventory, and it should be committed
as a test, not discarded. See `numerical-verification`.

If the derivation involved an approximation, the spot check won't agree exactly — so check
that the disagreement has the size and the scaling the order bookkeeping predicted. Agreement
to the wrong order is a bug that looks like success.

## The record

Write to the project's notes directory, one file per derivation:

```markdown
# <What is being derived>

**Status:** in progress | verified | superseded
**Conventions:** <deviations from CONVENTIONS.md, or "as CONVENTIONS.md">

## Assumptions
1. ...

## Derivation
Numbered equations. Each step labelled: identity / definition / convention / approximation
(with order). Result equations get stable numbers that code will cite.

## Checks performed
| Check | Type | Result |
| --- | --- | --- |
| gamma -> 0 recovers <known case> | limiting | passes |
| dimensions of Eq. (12) | dimensional | passes |
| Eq. (17) vs brute force, n=4 | numerical | agrees to 1e-14 |

## Accumulated error
The dropped terms and their order; what this implies for the error budget.

## Oracle inventory additions
What brute-force computation now exists, at what sizes, and where the test lives.

## Open steps
```

Equation numbers must be stable once code cites them. If a renumber is unavoidable, grep for
citations and fix them in the same commit.

## Failure modes

- **Algebra done in the session, with no record.** The derivation is then unreviewable and
  will be redone from scratch in a month.
- **"It's obvious that."** This phrase marks the location of the error more reliably than
  anything else in mathematics. Expand the step or check it numerically.
- **Conventions drifting mid-derivation.** A sign flips at step 8 because a source used the
  other convention, and nothing downstream notices.
- **Dropped conjugation or transpose** in index-free notation.
- **Motivated stopping.** The derivation reaches the expected answer and checking ceases.
  The expected answer is exactly when to run the numerical spot check, not when to skip it.
- **An approximation reused outside its stated regime** by a later step or by the code.
