# <What is being derived>

**Status:** in progress
**Updated:** <date>
**Conventions:** as CONVENTIONS.md <!-- or list deviations explicitly -->

<!-- Written by /derive. Copy to NN-slug.md and add a row to README.md. -->

## Assumptions

<!-- Write these BEFORE any algebra. Half of all derivation errors are an assumption that
     was implicit at step 3 and violated at step 11. -->

1. **Expanding in:** <!-- what's small, relative to what -->
2. **Regime of validity:** <!-- parameter ranges, what must stay finite -->
3. **Structural:** <!-- gap, regularity, boundedness, positivity, commutation -->
4. **Dropped at order:** <!-- what will be discarded, and at what order -->

## Derivation

<!-- Number every equation. Label every step: identity | definition | convention |
     approximation (with order). A step that can't be labelled isn't understood. -->

Starting from

$$ ... \tag{1} $$

*(identity)* Applying ...

$$ ... \tag{2} $$

*(approximation, error O(...))* Dropping the term ... on the grounds that ...

$$ ... \tag{3} $$

### Result

$$ ... \tag{17} $$

<!-- Result equations get stable numbers. These are what code cites. -->

## Checks performed

| Check | Type | Result |
| --- | --- | --- |
| dimensions of Eq. (n) | dimensional | |
| <coupling> → 0 recovers <known case> | limiting | |
| hermiticity / positivity / reality of Eq. (n) | symmetry | |
| term count / degree of Eq. (n) | counting | |
| Eq. (n) identity | symbolic (`check_identity.py`) | |
| expansion order matches claim | symbolic (`check_series`) | |
| Eq. (17) vs brute force, n=4 | numerical | |

<!-- Special-case checks happen DURING the derivation, at the line in question — not here
     at the end. This table records them; it isn't the place they get done. -->

## Numerical spot check

**Brute-force comparison:** <!-- what unapproximated computation, at what sizes, at which
                                parameter points including at least one awkward one -->

**Agreement:** <!-- If the derivation involved an approximation, exact agreement is a red
                    flag, not a success. Check the discrepancy has the size AND scaling the
                    order bookkeeping predicted. -->

**Test committed at:** <!-- path. This code is now an entry in the oracle inventory and
                            does not get deleted. -->

## Accumulated error

<!-- The dropped terms and their orders; what this implies for the error budget's model
     error term. -->

## Oracle inventory additions

| Oracle | Applies at | Cost | Test location |
| --- | --- | --- | --- |
| | | | |

## Open steps

<!-- Unfinished branches, steps taken on faith, things to check when time allows. Being
     explicit here is what stops "it's obvious that" from silently becoming load-bearing. -->
