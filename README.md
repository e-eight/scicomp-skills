# Skills for Scientific Computing

A starter set of agent skills for research code, built on the structure of
[mattpocock/skills](https://github.com/mattpocock/skills) but retargeted at a different
failure mode.

Application code fails loudly: it crashes, or the test goes red. Research code fails
quietly: it runs to completion, returns a plausible number, and the number is wrong.
Every skill here exists to close that gap.

## What's in the set

Split on who can invoke them, following the upstream convention. **User-invoked** skills
orchestrate and are reachable only when you type them. **Model-invoked** skills hold the
reusable discipline and can be reached for automatically when the task fits.

**User-invoked**

| Skill | Purpose |
| --- | --- |
| `scope-the-question` | The first thing you run. What's the question, what counts as an answer, what's the gap, what's the kill criterion. |
| `setup-scicomp-skills` | Builds `CONVENTIONS.md` — units, index order, glossary, oracle inventory, tolerance policy, compute environment. |
| `design-experiment` | Grilling session before any code: what claim, what observable, what oracle, what budget, what would falsify it. |

**Model-invoked**

| Skill | Purpose |
| --- | --- |
| `literature-map` | Primary-source survey: claims vs what they're cited for, a notation comparison table, published numbers usable as oracles. |
| `derive` | Derivation with assumptions up front and checks at every step. Ships `check_identity.py`. Produces the numbered equations code will cite. |
| `numerical-verification` | The replacement for TDD. An oracle ladder, the slow-twin rule, and tolerances you can justify. |
| `run-provenance` | No number reaches a figure without a manifest. Ships a `manifest.py` helper. |
| `error-budget` | Enumerate every error source and show each is subdominant to the claim. |
| `numerics-review` | Review a diff on a third axis beyond standards and spec: conditioning, precision, seeds, conventions, silent failure. |
| `scale-down-first` | toy → smoke → pilot → production. Never burn an allocation on an untested path. |
| `layer-separation` | model / method / driver / analysis, with a one-way dependency rule and a `check_layers.py` for CI. Only for codebases outliving their first paper. |

## Contents

```
skills/                     ten SKILL.md files, three with bundled scripts
  derive/scripts/check_identity.py        randomized symbolic identity verification
  run-provenance/scripts/manifest.py      stdlib-only run manifest writer
  layer-separation/scripts/check_layers.py  import-graph layer checker for CI
  setup-scicomp-skills/assets/CONVENTIONS.template.md
templates/
  notes/                    stubbed notes directory — copy to your repo root
  layers.json.example       rename to .layers.json for check_layers.py
```

The three scripts are stdlib-only except `check_identity.py`, which needs sympy. All three
run standalone: `python manifest.py <dir>`, `python check_identity.py` (self-test),
`python check_layers.py <repo>`.

## Install

These are plain `SKILL.md` files. Copy the `skills/` directory into wherever your agent
looks for them — `.claude/skills/`, `.agents/skills/`, or your repo root — or install
with the `skills` CLI:

```bash
npx skills@latest add e-eight/scicomp-skills
```

The CLI installs only the skills. Get `templates/` separately from
[the repo](https://github.com/e-eight/scicomp-skills/tree/main/templates): copy `notes/`
to your repo root, and if you use `check_layers.py`, copy `layers.json.example` to
`.layers.json` at your repo root too.

Take the editable install rather than a managed plugin bundle. You will rewrite parts of
these within a week of using them, and that's the point.

## The pipeline

```
scope-the-question → literature-map → derive → setup-scicomp-skills → design-experiment → code
                                                    ↑
                       numerical-verification, run-provenance, error-budget,
                       numerics-review, scale-down-first, layer-separation
                       are reached for automatically from here on
```

**On an existing repo with code already written**, run `/setup-scicomp-skills` first — the
conventions are already implicit in the code and the point is to surface them.

**On a new project, don't.** Its hardest sections — the conventions table, the glossary, the
oracle inventory — are *outputs* of the literature and derivation work, not inputs to it.
Start with `/scope-the-question`, let `literature-map` fill the notation table and
`derive` populate the oracle inventory, then run setup to consolidate.

## Using it with the upstream repo

These are additive. Install `mattpocock/skills` too and use these upstream skills as-is —
they need no adaptation for research work:

- `grill-me`, `grilling` — general alignment interviews
- `handoff` — compact a session into a document; use it as a lab-notebook entry
- `wait-what` — re-pitch anything that didn't land, in your own vocabulary
- `writing-for-agents` — for when you write your own skills
- `diagnosing-bugs` — the loop is right; `numerical-verification` supplies what "red" means
- `wizard` — excellent for cluster onboarding, allocations, module loads, scheduler setup
- `to-questionnaire` — when a scoping or derivation decision needs an advisor or collaborator
- `teach` — for math you're learning rather than deriving; runs stateful across sessions

`design-experiment` replaces `grill-with-docs`, `scope-the-question` retargets `grill-me` at
research framing, `literature-map` replaces `research`, and `CONVENTIONS.md` plays the role
of upstream's `CONTEXT.md`. If you install both sets, keep one conventions file, not two.

Skip upstream's `improve-codebase-architecture` and the spec-to-tickets pipeline until a
project is big enough to need them. For a 2000-line exploratory script the architecture is
fine and the mud is load-bearing. `layer-separation` here covers the one piece of that
skill that pays off in research code, and only under the conditions it names — don't reach
for it by default.

## What to write next

The obvious gaps, roughly in order of value:

1. **`replicate-first`** — before extending a published result, reproduce one number from
   it. Cheap, doubles as a comprehension check, and hands you a verified oracle.
2. **`figure-reproducibility`** — one command regenerates every figure from stored raw
   data. Partly covered by `run-provenance`; deserves its own skill once you have a paper.
3. **`derivation-traceability`** — each function names the equation it implements, with
   symbolic re-derivation (sympy) where tractable.
4. **`scaling-study`** — strong and weak scaling, roofline, profile-before-optimize, and
   the rule that you never optimize a kernel without a correctness oracle.
5. **`data-release`** — packaging raw data and scripts for a repository at submission time.

## A note on scope

Spend your discipline budget early on oracles and provenance, not on module depth.
Research code is often meant to be discarded; what has to survive is the ability to say
why a number is right.
