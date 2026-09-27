---
name: explain-derivation
description: Turn a verified derivation record from notes/derivations/ into a readable walk-through that sits next to it. It gives the overall strategy, one algebraic move per step with the identity named, the reason for each choice, where each assumption enters, and what the result means physically. Every intermediate step it adds is checked with the derive skill's check_identity.py. Use this only when the user asks to explain, walk through, unpack, or learn a derivation, or asks how a result in the notes was obtained. Do not run it unprompted after derive finishes.
---

# Explain derivation

Model-invoked, but only on request. Uses `derive/scripts/check_identity.py`.

A `derive` record is written for a reviewer. It is short, every step carries a label, and
the equation numbers are stable so code can cite them. That makes it easy to check and hard
to learn from: the moves are named but not motivated, and several manipulations often share
one line. This skill writes the companion document for a reader who wants to understand
the derivation, not just confirm it.

The danger is specific. An explanation fills gaps, and a gap filled from memory is an
unverified step placed inside a verified derivation. So the rule here matches the rule in
`derive`: every line the explanation adds is checked.

## Inputs and when to stop

The input is one record in `notes/derivations/`. Read all of it, including the assumptions,
the checks table, and the open steps.

- **Status `verified`:** proceed.
- **Status `in progress`:** tell the user the explanation may go stale. Proceed only if
  they confirm, and set the companion's status to `draft`.
- **Status `superseded`:** explain the superseding record instead, unless the user wants
  to understand what went wrong in the old one.

Establish who the reader is before writing. The default is someone with the field's
background who hasn't seen this derivation, like a new group member. If the user names a
different reader (themselves six months from now, a collaborator from another field, a
student), the level of detail follows that reader. Record the choice in the header.

## The companion file

Write it next to the record, with the same number:
`notes/derivations/03-foo.md` → `notes/derivations/03-foo.explained.md`.

The companion is a living document, not an append-only record. It carries `**Updated:**`
and the commit of the record it explains. When the record changes, the explanation is
regenerated, not patched by hand.

**Code never cites the companion.** Code cites the record. The companion reuses the
record's equation numbers exactly, and any intermediate equation it adds gets a letter
suffix on the preceding number, like (3a) and (3b). The suffix shows at a glance that the
equation exists only in the explanation.

## Per-step discipline

For each step in the record, in order:

**One move per step.** If the record's line from Eq. (3) to Eq. (4) does three things,
the explanation shows three steps: (3a), (3b), then (4). A move is one substitution, one
identity, one integration, one rearrangement, or one dropped term.

**Name the specific move.** Not "identity" but "identity: cyclic property of the trace".
Not "approximation" but "approximation: drop $\mathcal{O}(\epsilon^2)$ terms, valid
because $\epsilon \ll 1$ by Assumption 1". If the record's label is only the category and
the specific move can't be recovered, that is a gap. Handle it as described under
"Gaps and disagreements".

**Say why at every fork.** Where the derivation could have gone another way (a choice of
basis, gauge, contour, ordering, or expansion point), give one sentence on why this way.
Steps with no choice don't need this. Padding them with motivation hides the steps that
matter.

**Point to the assumption.** When a step uses an assumption, cite it by its number in the
record: "(uses Assumption 3: the spectrum is gapped)". A reader should be able to find
every place an assumption is used, and see what breaks when it fails.

**Check what you add.** Every intermediate equation that isn't in the record gets checked
before it goes in the file:

- Algebraic and analytic identities: `check_identity`, with random substitution for every
  free symbol, as in `derive`.
- Operator identities: `check_matrix_identity` on matrices of the smallest nontrivial
  size, with a separate symbol for each entry, so the random substitution fills them in.
- Expansions: `check_series`, confirming agreement through the claimed order.
- Dimensions: both sides of every added equation, the same as in `derive`.

Import the checker from the `derive` skill's directory. Don't copy it.

```python
import sys; sys.path.insert(0, "<derive-skill-dir>/scripts")
from check_identity import check_identity, check_matrix_identity, check_series
```

List the added steps and how each was checked in the companion's check table. A step you
could not check goes in the file marked **unverified**, never silently.

## Gaps and disagreements

Filling in a record will sometimes turn up a problem. There are two cases.

- **A step can't be reconstructed.** The record goes from (7) to (8) and you can't find a
  checked path between them. Don't invent one. Mark the gap in the companion, tell the
  user, and suggest adding the missing steps to the record through `derive`.
- **An added step fails its check.** Either your reconstruction is wrong or the record
  is. Try a different route. If every route fails, **stop**. The record may have an
  error, and code may already cite it. Report the failing step with the counterexample
  `check_identity` returned. Don't publish an explanation that works around it. Fixing
  the record is `derive`'s job, and the record's rules for corrections apply.

Either way, the explanation doesn't add claims. It may not add results, widen the regime
of validity, or drop assumptions. Interpretation is welcome, but label it as
interpretation.

## Template

```markdown
# <What is derived>, explained

**Explains:** [NN-slug.md](NN-slug.md) at <commit>
**Updated:** <date>
**Status:** current | draft | stale
**Written for:** <the reader, and what they're assumed to know>

## The idea in brief
What is derived, why anyone needs it, and the strategy in three to five sentences:
the starting point, the key move, and where the approximation enters.

## Before you start
What the reader needs: definitions, prior results, conventions that differ from what a
textbook would use. Link CONVENTIONS.md and its glossary rather than repeating them.

## Walk-through
The record's equation numbers, with letter-suffixed intermediate steps between them.
Each step: the equation, the named move, and why when there was a choice.

## Where the assumptions enter
| Assumption | Used at | What fails without it |
| --- | --- | --- |

## What the result means
Physical reading of each term, scaling with the parameters, limiting cases in words.
Labelled as interpretation.

## Where it breaks
The edge of the regime of validity, and what the first neglected term would do there.
Taken from the record's accumulated error; nothing new is claimed here.

## Added steps and their checks
| Step | Move | Check | Result |
| --- | --- | --- | --- |
| (3a) | trace cyclicity | `check_matrix_identity`, 3×3 | passes |

## Gaps
Steps that could not be reconstructed or checked, and what was reported.
```

## After writing

Tell the user the file path. If they want to read it with rendered math, `render-notes`
renders the companion like any other note. If they want to learn the material over several
sessions with exercises and recall practice, upstream's `teach` skill can use the
companion as a primary source. Run it in a separate directory, because it writes its own
workspace files where it runs.

## Failure modes

- **Filling a gap from memory.** This is the one this skill exists to prevent. An
  unchecked step inside a checked derivation borrows trust it hasn't earned.
- **Explaining around an error.** The reconstruction fails, so the explanation takes a
  vaguer path that happens to reach the right answer. Stop and report instead.
- **New equation numbers.** Renumbering, or adding plain numbers that collide with the
  record's, breaks the link between the companion, the record, and the code.
- **Motivation everywhere.** A reason given for every trivial step drowns the few steps
  where the choice mattered.
- **Scope creep.** "This also holds when..." is a new claim. It belongs in a new
  derivation, not in an explanation.
- **Stale companion.** The record gets a correction and the explanation still teaches the
  old version. Check the commit in the header against the record before relying on it.
