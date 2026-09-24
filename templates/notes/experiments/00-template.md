# <Experiment title>

**Status:** planned
**Date:** <date>
**Runs:** <!-- run ids in runs/, once they exist -->

<!-- Written by /design-experiment. Copy to YYYY-MM-DD-slug.md. One per experiment.
     Keep the status line current: planned | running | done | abandoned. An abandoned
     experiment with its reason recorded beats an orphaned directory. -->

## Claim

<!-- The sentence that ends up in the notes or paper, with the number left blank. -->

## Observable and estimator

<!-- What exact quantity, computed from what, reduced how. Averaged over what. If there was
     an estimator choice, why this one. -->

## Regime

| Parameter | Range | Sampling | Why these endpoints |
| --- | --- | --- | --- |
| | | | |

**Held fixed:** <!-- and whether the conclusion is meant to be independent of them — if so,
                    that's a control run, not an assumption -->

## Verification oracle

<!-- Which oracle applies, at what size. If there isn't one, say so here — that's the
     experiment's biggest risk. See numerical-verification. -->

## Error budget, first pass

<!-- Which error sources will compete with the effect being measured. If the expected effect
     is 1% and discretization error is 5%, the experiment cannot succeed as designed — and
     this is where you find that out. See error-budget. -->

| Source | Expected size | Knob |
| --- | --- | --- |
| | | |

## Cost estimate

<!-- runs × wall time × resources, from a pilot measurement rather than optimism.
     See scale-down-first. -->

## Falsification criteria

**The hypothesis is wrong if:**

**The code is broken if:** <!-- Committing in advance to "a result outside [a,b] means the
                                code is broken" is the cheapest defense against debugging
                                until results look right and then stopping. -->

## Tracer bullet

<!-- Smallest configuration exercising the whole pipeline end to end — model, solve, reduce,
     store, plot — at throwaway accuracy. Built first, always. -->

## Artifacts

| What | Where |
| --- | --- |
| Raw runs | `runs/...` |
| Figure | `figures/...` |

## Outcome

<!-- Filled in when status becomes done or abandoned. What was found, or why it stopped. -->
