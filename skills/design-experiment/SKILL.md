---
name: design-experiment
description: Interrogate the user about a planned numerical experiment or simulation until the claim, observable, parameter regime, verification oracle, error budget, compute cost, and falsification criterion are all pinned down, then write it up as an experiment record. Use this before writing any simulation, sweep, or analysis code, whenever a user describes something they want to compute or measure numerically, and whenever a research question is about to turn into code. Run it every time — the cost of a misaimed sweep is measured in node-hours.
disable-model-invocation: true
---

# Design an experiment

User-invoked. Run before code exists.

An agent asked to "simulate X and plot Y" will produce something. Whether it answers the
question you actually had is a coin flip, and you won't find out until after the sweep has
run. This skill spends twenty minutes closing that gap.

## How to conduct the interview

One question at a time. Wait for the answer. Follow the thread that answer opens before
moving on — the interesting branches are always two questions deep.

Do not accept:

- "We'll see how it goes" on anything that determines the code structure
- A parameter range with no justification for its endpoints
- "It should be obvious if it's wrong"
- Answers that describe the method when you asked about the claim

Do accept "I don't know" — but then record it as an open decision with what it blocks and
what would resolve it, rather than guessing on the user's behalf. A recorded unknown is
progress. A guess that gets implemented is a landmine.

Read `CONVENTIONS.md` first. Use the project's vocabulary in your questions; if the user
introduces a term that isn't there, ask whether it should be.

## What must be resolved before you stop

### The claim

What sentence ends up in the notes or the paper? Write it out, with the number blank.
"Method A converges faster than method B in regime R" and "Method A's error scales as
h² in regime R" are different experiments.

### The observable and estimator

What exact quantity is computed, from what, and how is it reduced to the number in the
claim? Averaged over what? If there's an estimator choice, why this one?

### The regime

Which parameters vary, over what range, sampled how densely, and why those endpoints.
Which parameters are held fixed, and is the conclusion supposed to be independent of them
— if so, that's a control run, not an assumption.

### The oracle

How will you know the result is right? Defer the detail to `numerical-verification`, but
establish here that at least one independent check exists, and at what system size. If the
answer is "there isn't one," that is the experiment's biggest risk and it belongs at the
top of the record.

### The error budget

Which error sources will compete with the effect being measured? Defer to `error-budget`,
but get a first pass: if the expected effect is 1% and the discretization error is 5%, the
experiment as designed cannot succeed, and you want to know that now.

### The cost

Number of runs × wall time per run × resources. Does it fit in the allocation? If the
sweep is 10× the budget, redesign the sweep now — adaptive sampling, a coarser grid with
refinement where it matters, or a smaller system with a finite-size extrapolation.

### The falsifier

What outcome would mean the hypothesis is wrong? And separately: what outcome would make
you distrust the code rather than the hypothesis? Researchers debug until results look
right and stop, which biases everything. Committing in advance to "a result outside
[a, b] means the code is broken" is the cheapest defense there is.

### The tracer bullet

The smallest configuration that exercises the entire pipeline end to end — model setup,
solve, reduce, store, plot — at throwaway accuracy. This gets built first, always. See
`scale-down-first`.

### The artifact

What files exist at the end, where, and what figure or table the claim rests on.

## Output

Write an experiment record to the project's docs directory, named by date and slug:

```markdown
# <Experiment title>

**Status:** planned | running | done | abandoned
**Date:** <date>

## Claim
## Observable and estimator
## Regime
## Verification oracle
## Error budget (first pass)
## Cost estimate
## Falsification criteria
## Tracer bullet
## Artifacts
## Open decisions
| Question | Blocks | Resolved by |
```

Keep the status line current — an abandoned experiment with its reason recorded is worth
more to future-you than a directory of orphaned scripts.

Then offer to break the record into tickets, with the tracer bullet as the first one.
