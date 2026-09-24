---
name: literature-map
description: Survey the primary literature on a research question and build a durable map — anchor papers, what each actually claims versus what it gets cited for, regimes of validity, a notation and convention comparison table, and published numbers usable as verification oracles — with the gap statement tested rather than assumed. Use this after scope-the-question and before any derivation or code, whenever a user asks what's known about a topic, whenever a project's novelty claim needs checking, and whenever adapting a result from a paper into different conventions.
---

# Literature map

Model-invoked; also worth invoking directly.

Upstream's `research` skill has the right shape — primary sources, cited markdown captured
in the repo, run as a background task — but it's aimed at documentation and library
behaviour. Research literature needs three things it doesn't do: separating what a paper
claims from what it's cited for, harvesting notation, and extracting numbers you can test
code against.

## Search strategy

Start from an anchor: the paper the user already knows, or the most-cited recent review.
Then work outward in both directions.

**Backward** through the anchor's references, for the origin of each key idea. Claims
frequently trace back through a chain of citations to an assertion that was never actually
demonstrated — a conjecture in a discussion section, a "it is well known that," a special
case quietly generalized in the retelling. Finding the bottom of a chain like that is often
the most valuable thing the search produces, because it's either a real gap or a warning.

**Forward** through who cites the anchor, and — more informative — *why*. A paper cited two
hundred times for its method and never for its central claim is telling you something about
which part held up.

**Sideways** through arXiv listings in the relevant categories for the last year or two, and
through the recent output of the three or four groups working nearest to this. Preprints
matter here; the published record lags by a year or more and the question of whether
something has already been done is a question about preprints.

Search the actual literature rather than answering from memory. Recall of specific papers,
their claims, and their numbers is unreliable at exactly the level of detail that matters
here, and a confidently wrong citation is worse than none.

### Access

Use the official APIs, not the websites. arXiv and the citation indexes rate-limit and block
scrapers, and a blocked agent quietly returns a thinner map.

- **arXiv** through `export.arxiv.org/api/query`, never `arxiv.org/search` or listing pages,
  which its `robots.txt` disallows or throttles for automated use. One request every three
  seconds, one connection at a time.
- **Backward and forward** through the Semantic Scholar Graph API's `/paper/{id}/references`
  and `/paper/{id}/citations`, with `fields=contexts,intents,isInfluential`. The contexts
  are the sentences where each citing paper mentions the anchor, which is the *why* the
  forward step asks for. It takes arXiv IDs directly as `ARXIV:<id>`. OpenAlex is the
  second source when coverage is thin.
- **Field-specific indexes** where they fit: INSPIRE-HEP for high-energy physics, NASA ADS
  for astrophysics (needs a token), PubMed E-utilities for biomedicine.

Requests go one at a time per service, never in parallel. On a `429`, back off and retry
later rather than pushing through. Read `S2_API_KEY`, `OPENALEX_API_KEY`, and `ADS_API_TOKEN`
from the environment when set. When they aren't, run without them and tell the user once
that a free key helps; OpenAlex in particular allows almost nothing without one. Never
write a key into the notes.

Fetching an individual paper's abstract page or HTML version to read it is fine. Crawling
search results or listings is not.

## What to record per paper

For each paper that matters, write in your own words — never paste abstracts or extended
passages, and cite equation and section numbers so a reader can go check:

- **What it actually claims**, stated precisely, including the quantifiers and conditions
- **What it gets cited for**, when that differs. The divergence between these two is where
  most opportunities live: an overstated result that everyone now assumes, a narrow result
  that turned out to be general, a method whose stated limitation nobody reads.
- **Regime of validity** — the assumptions, the parameter range, the system sizes
- **Computed versus asserted.** Which claims are supported by the figures shown, which by a
  citation, which by "one can show that." Mark them differently.
- **Reproducible numbers**: any published value, at stated parameters, that your code could
  be checked against. These are oracle candidates, and they're the most useful thing in the
  paper for your purposes.
- **Code and data**: released or not, and whether it runs
- **Trust markers**: preprint or refereed, whether the key result has been independently
  reproduced, whether the group has a track record in this specific claim

## Harvest the notation

Do this as you read, not afterwards. Every paper carries its own conventions and the
differences are rarely stated. Build the table as a first-class output:

| Paper | Hamiltonian sign | Units / constants set to 1 | Index convention | Normalization | Symbol for <key quantity> |
| --- | --- | --- | --- | --- | --- |

This table does three jobs. It lets you translate a result between papers without
re-deriving it. It's the raw material for `CONVENTIONS.md` when `setup-scicomp-skills` runs.
And it explains the otherwise baffling factor-of-two disagreements that will show up later
when you compare your numbers against published ones — which is the single most common
source of "our code must be broken" panics that turn out to be a convention mismatch.

## Test the gap claim

`scope-the-question` recorded the user's belief about the nearest existing result. Report
back explicitly on it: confirmed, narrowed, or refuted. If someone has already done it, say
so plainly and early — that's the highest-value output this skill can produce, and softening
it wastes months. If it's been done in a neighbouring regime, the gap may have moved, and
the project statement needs updating rather than quiet reinterpretation.

## Output

A map file in the docs directory, kept and updated rather than written once:

```markdown
# Literature map: <topic>

**Last updated:** <date>

## Gap statement
As claimed in the problem statement, and what the search found. Confirmed / narrowed /
refuted.

## Anchor papers
| Ref | Claim (in our words) | Regime | Cited for | Trust |

## Threads
Short narrative per line of work: where it started, where it is, who's active.

## Notation and conventions
<the table above>

## Oracle candidates
| Ref | Quantity | Parameters | Published value | Usable as a test? |

## Open reading
| Paper | Why it matters | Status |

## Dead ends
Chains that bottom out unsupported; claims that didn't replicate.
```

Keep the dead-ends section. It's the part nobody writes down and the part you'll want when
a reviewer asks why you didn't use the obvious prior approach.

## Next

Feed the oracle candidates into the oracle inventory when `setup-scicomp-skills` runs, and
the notation table into `CONVENTIONS.md`. Then `derive`.

If a published result is central to what you're building on, consider reproducing one of its
numbers before extending it — cheap, doubles as a comprehension check, and hands you a
verified oracle.
