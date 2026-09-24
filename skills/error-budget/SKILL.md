---
name: error-budget
description: Enumerate every source of error in a computed result — discretization, truncation, statistical, finite-size, solver tolerance, floating point, model, and implementation — estimate each by measurement rather than assertion, and show that all of them are subdominant to the claim being made. Use this before quoting any number in a paper, talk, thesis, or figure; whenever a user asks how accurate a result is, how many digits to report, or whether an effect is real; whenever two methods are being compared; and whenever a result is surprising or close to a threshold.
---

# Error budget

Model-invoked.

A result without an error budget is a number, not a measurement. The budget answers one
question: is the effect being claimed larger than everything that could be faking it?

Two failure modes this prevents. The first is quoting a difference of 2% when the
discretization error is 5%. The second is reporting eight digits when the budget supports
two — which reads as either carelessness or overreach, and referees notice.

## Enumerate the sources

Go through all of these and say something about each, including "not applicable, because".
The one you skip is the one that dominates.

| Source | Mechanism | Knob | Expected scaling |
| --- | --- | --- | --- |
| Discretization | Time step, grid spacing, Trotter step | `dt`, `h` | Method order: `h^p` |
| Truncation | Basis size, bond dimension, cutoff, series order | `chi`, `N_basis` | Often exponential, sometimes not |
| Statistical | Finite sampling, shot noise | `N_samples` | `1/sqrt(N)` × sqrt(autocorrelation time) |
| Finite size | System is not the thermodynamic limit | `L`, `N` | `1/L` or `exp(-L/xi)` depending on gap |
| Solver tolerance | Linear solve, eigensolver, optimizer stopping | `tol`, `max_iter` | Set by tolerance, unless it stopped early |
| Optimizer quality | Local minima, initialization dependence | seed, restarts | Not a scaling — a distribution |
| Floating point | Accumulation, cancellation, conditioning | precision | `eps × kappa × ops` |
| Model | The system simulated is not the system meant | — | Not reducible by computation |
| Implementation | Bugs | — | Bounded only by `numerical-verification` |

Two of these are qualitatively different and deserve saying out loud. **Model error**
can't be shrunk by a finer grid; it's an argument, not a number. **Implementation error**
has no scaling at all — the only bound on it is the strength of your verification oracles,
which is why an error budget on unverified code is theater.

## Measure, don't assert

The cheapest honest estimate of any convergence-controlled term: vary the knob by 2× and
look at how much the answer moves. Then vary it again and check the movement follows the
expected power law. If it doesn't, you've learned something more important than the error
estimate — either the asymptotic regime hasn't been reached, or the method isn't the order
you think it is.

For the extrapolation-friendly terms, Richardson extrapolation gives both a better estimate
and an error bar on it for the price of one extra run.

For statistical error, the naive sample standard deviation is wrong whenever samples are
correlated, which for Markov-chain methods is always. Estimate the autocorrelation time
and inflate accordingly, or use blocking. Underestimated statistical error is the single
most common defect in published Monte Carlo results.

For optimizer quality, run multiple restarts and report the spread, not the best value.
Reporting the minimum over restarts biases the result and is not reproducible.

## Output

A table in the notes or paper draft, ordered by size:

| Source | Estimate | How estimated | Notes |
| --- | --- | --- | --- |
| Truncation (`chi`) | 3e-4 | `chi` 64→128, extrapolated | dominant |
| Statistical | 8e-5 | blocking, `tau ≈ 12` | |
| Discretization | 2e-5 | `dt` halved, second order confirmed | |
| ... | | | |
| **Total (added in quadrature / linearly)** | | | |

State which combination rule you used and why. Independent random errors add in
quadrature; systematic errors that could align add linearly. When in doubt, be
conservative and say so.

Then compare the total against the claim's margin, explicitly, in one sentence:
"the difference between the two methods is 2.1e-3, roughly seven times the combined
uncertainty of 3e-4."

## Rules

- **If the dominant term is unmeasured, the claim is unsupported.** Say that plainly
  rather than hedging in prose. "We believe the truncation error is small" is not a budget.
- **Never quote more digits than the budget supports.** Round the uncertainty to one or two
  significant figures and match the result to it.
- A budget computed once and reused across a parameter sweep is wrong wherever the physics
  changes character — near a transition, at small gap, in a stiff regime. Recompute at the
  hardest point in the sweep, not the easiest.
- Record the budget in the experiment record and the run manifest, so it travels with the
  number.
