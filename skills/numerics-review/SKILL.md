---
name: numerics-review
description: Review a diff or a file of scientific code on three axes — repo standards, faithfulness to the intended equation or spec, and numerical soundness (precision, conditioning, cancellation, aliasing, RNG and seeding, reduction order, unit and index conventions, boundaries, parallel correctness, silent failure). Use this before merging or committing any change to simulation, solver, or analysis code, whenever a user asks for a code review of numerical work, whenever a result looks surprising and the code is suspect, and before a production run or a paper submission.
---

# Numerics review

Model-invoked.

An ordinary code review asks whether the code is clean and whether it does what the ticket
said. Scientific code needs a third axis, because code can be clean, match the spec, and
still produce a number that is quietly wrong by 30%.

Run the three axes as independent passes so findings from one don't contaminate the
others.

## Axis 1 — Standards

Repo conventions, naming, dead code, the usual smells. Cheapest pass; do it fast.

## Axis 2 — Intent

Does the code implement the equation it claims to? Find the source — the paper, the notes,
the derivation — and check term by term. Watch for the classics: a dropped factor of 2 or
2π, a missing conjugate, a commutator with the arguments swapped, a Hamiltonian with the
wrong overall sign, an index summed over the wrong range, a transpose standing in for a
dagger.

If the code doesn't name its source equation, that's a finding on its own. Ask for a
docstring reference, and read `CONVENTIONS.md` before deciding a term is wrong — half of
apparent sign errors are convention differences.

## Axis 3 — Numerics

Work the checklist. Most items are cheap to check and catch a class of bug that testing
frequently misses.

**Precision and types**
- Silent downcast to float32 / complex64 through a library call or literal
- Integer division or overflow in an index or size computation
- Accumulation in lower precision than the data, in long sums or reductions
- Comparison of floats with `==`, or an `int`/`float` mix in a conditional

**Conditioning and cancellation**
- Subtraction of nearly equal quantities, especially in an energy difference
- Division by a quantity that can approach zero across the parameter range
- Explicit matrix inverse where a solve would do; forming `A^T A`; `expm` of a large
  argument; `log` of something that can underflow
- Naive one-pass variance; naive Gram–Schmidt; normalizing a near-null vector
- Ill-conditioned input the code doesn't detect — is the condition number ever checked?

**Aliasing and mutation**
- In-place modification of an array the caller still owns
- A view where a copy was meant, or vice versa in a hot loop
- Mutable default arguments holding state across calls

**Randomness**
- Global seeding rather than an explicit generator passed down
- The same seed reused across parallel workers or MPI ranks, producing correlated
  "independent" samples — a silent, result-destroying bug
- Seeds derived from clock time, making the run unreproducible
- Seeds not recorded in the manifest

**Reproducibility**
- Reduction order dependent on thread count, chunking, or scheduling
- GPU atomics or non-deterministic kernels
- BLAS thread count unpinned, changing low-order bits between runs
- Iteration over a set or dict where order affects the result

**Conventions**
- Axis order inconsistent with `CONVENTIONS.md`
- Off-by-one between a physical index and an array index
- Units mixed between modules; a hardcoded constant in the wrong unit system
- `linspace` endpoint inclusion changing an effective step size

**Boundaries and domains**
- Periodic vs open boundary handling, ghost cells, wraparound at the seam
- Behaviour at the first and last element of every loop over a lattice or grid
- Parameter values at the edge of the method's validity, unguarded

**Parallel**
- Collective called on some ranks and not others, behind a conditional
- Early return that skips a collective — deadlock waiting to happen
- Double counting at shared boundaries during reduction
- Rank-dependent behaviour that isn't meant to be rank-dependent

**Silent failure**
- Solver convergence flag, eigensolver return code, or optimizer status ignored
- `NaN` or `Inf` propagating without a check at the point of production
- A `try/except` that swallows a numerical error and continues
- Clipping or clamping that hides an out-of-range value instead of surfacing it

**Verification coupling**
- An optimized path added without a test against a slow twin — see
  `numerical-verification`. Optimizing an unverified kernel is the fastest known way to
  produce confident wrong results.

## Output

Findings grouped by severity, each with file and line, what's wrong, and why it matters to
the number rather than to the code:

- **Blocks the result** — the computed number is or may be wrong
- **Correctness risk** — not wrong today, but will break under a plausible parameter change
- **Unverifiable** — may well be right, but nothing in the repo could tell you either way
- **Hygiene** — everything else

Keep the third category distinct. "This is wrong" and "I cannot tell whether this is
wrong" call for different responses from the author, and collapsing them wastes their time
on the wrong one.
