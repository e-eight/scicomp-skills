---
name: scope-the-question
description: Interrogate a research idea until the question, the form a valid answer would take, the nearest existing result, the smallest decidable version, and the kill criterion are all pinned down, then write it up as a one-page problem statement. Use this at the start of any new research project or subproject, whenever a user describes something they are thinking about working on, whenever a project has drifted and needs restating, and before any literature search or derivation — it runs before design-experiment and before setup-scicomp-skills.
disable-model-invocation: true
---

# Scope the question

User-invoked. The first thing you run on a new project.

Upstream's `grilling` interviews you about a design. This interviews you about a research
question, which fails differently: designs fail by being underspecified, research questions
fail by being unanswerable, already answered, or not worth answering. Those three are
detectable in an afternoon and otherwise cost a semester.

One question at a time. Follow threads. Push on vagueness — "it would be interesting to
look at" is where projects go to die, and the useful response is "interesting to whom, and
what would they do differently."

## What must be resolved

### The question, with no method in it

One sentence. If the method appears in the statement — "use technique T to study S" — the
question hasn't been separated from the approach yet, and you'll be unable to tell later
whether a negative result means S is uninteresting or T was the wrong tool. Push until
there's a statement about the world, then note the method separately as a hypothesis about
how to get at it.

### What would count as an answer

Force a choice of form: a number, a bound, a scaling exponent, a yes/no, a construction, an
existence proof, a demonstration that something is feasible, a counterexample. Different
forms demand entirely different work, and people routinely start computing before deciding
which one they're after.

Then: how precise does it have to be to be worth reporting? An order of magnitude, a factor
of two, three digits? This feeds straight into `error-budget`, and it is far cheaper to
discover now that the required precision is unreachable.

### Who it's for

Who reads this and does something differently as a result? "The community" is not an answer.
Name a subfield, a debate, a competing claim, or a practical decision. If nobody's behaviour
changes either way, that's worth knowing before the work, not after.

### The nearest existing result

What's the closest thing already known, and what exactly is the gap — a different regime, a
weaker assumption, a larger system, a sharper bound, a first demonstration? State the gap in
one sentence. The literature search (`literature-map`) will test this claim; right now you
want the user's belief on record so it can be falsified.

### Why hasn't it been done

Make the user pick one, explicitly:

1. **It has been done** — and they don't know the reference yet
2. **It's harder than it looks** — there's a known obstruction
3. **Nobody needs it** — it's doable and uninteresting
4. **Something changed** — new method, new hardware, new data, new theory opened it up

Most ideas that feel new are (1) or (2), and both are cheap to check. If the answer is (4),
name the thing that changed — that's usually the paper's actual contribution and belongs in
the framing.

### The smallest decidable version

What's the smallest version of this that would still be worth writing up? Not the smallest
test case — the smallest *result*. One system instead of a family, one regime instead of a
phase diagram, a numerical demonstration instead of a proof. Scope only ever grows once work
starts, so the version defined here should feel slightly too small.

### The kill criterion

What could you learn in the first two weeks that would make you stop? Write it down and put
a date on it. Committing in advance is the only thing that works, because by week six the
sunk cost will have quietly rewritten the question into whatever the results support.

### Logistics

Who else is involved and what do they own. Whether this is a paper, a note, a thesis chapter,
a code release, or a talk — the target shapes how much verification and documentation the
work needs. Rough timeline, and what it's competing with.

## Output

A one-page problem statement in the docs directory. Not a spec — no methods, no
implementation, no parameters:

```markdown
# <Question>

**Status:** scoping | active | parked | killed | done
**Date:** <date>

## Question
One sentence, no method.

## What counts as an answer
Form, and required precision.

## Audience and consequence
Who changes what they do.

## Nearest existing result and the gap
(to be tested by literature-map)

## Why it hasn't been done
Which of the four, and the evidence.

## Smallest decidable version

## Kill criterion
What we could learn by <date> that stops this.

## Open questions
| Question | Blocks | Resolved by |
```

Keep the status line honest. A project marked `killed` with its reason recorded is a real
contribution to your future self; an abandoned directory with no note is a trap you'll fall
into twice.

## Next

`literature-map` to test the gap claim, then `derive` to fix the mathematics, then
`setup-scicomp-skills`, then `design-experiment`. Don't let the interview slide into
experiment design — if the user starts specifying parameter sweeps, note it and bring them
back; that's a different skill and it comes after the math.
