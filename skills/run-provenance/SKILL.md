---
name: run-provenance
description: Record the full provenance of every computational run — git commit and dirty diff, resolved parameters, RNG seeds, dependency and compiler versions, hardware, job id, wall time, and input/output hashes — into a manifest written before the run starts, so any number can be traced back to what produced it. Use this whenever writing or reviewing a simulation driver, parameter sweep, analysis script, or figure script; whenever results are saved to disk; whenever someone asks where a number or figure came from or can't reproduce one; and before any result is used in a paper, talk, or thesis.
---

# Run provenance

Model-invoked. Ships `scripts/manifest.py`.

The rule: **a number that can't be traced to a manifest doesn't go in a figure, a talk, or
a paper.** Not because provenance is virtuous, but because six months from now the
referee's question will be "what were the parameters in Fig. 3" and the honest answer will
otherwise be a guess.

Upstream engineering skills treat the issue tracker as the system of record. In research
the system of record is data lineage, and nothing else fills that role.

## The manifest

Written as `manifest.json` in the run directory. Fields:

| Field | Why |
| --- | --- |
| `run_id` | Stable handle for citing this run elsewhere |
| `timestamp_utc` | Ordering, and matching against scheduler logs |
| `git.commit`, `git.branch` | The code |
| `git.dirty`, `git.diff` | The code that actually ran, when it wasn't committed |
| `params` | The **resolved** parameter dict, after defaults and overrides — not the command line |
| `seeds` | Every RNG stream, by name |
| `env.python`, `env.packages`, `env.compiler`, `env.blas` | Version-dependent numerics |
| `env.threads`, `env.mpi_ranks`, `env.gpu` | Reduction order and nondeterminism |
| `host`, `partition`, `nodes`, `job_id` | Matching against scheduler accounting |
| `inputs` | Path plus content hash for every input file |
| `status`, `wall_time_s`, `exit_code` | Whether to trust it at all |
| `outputs` | Path plus content hash for every artifact produced |

Storing the resolved parameters rather than the invocation is the part people get wrong.
A command line plus a config file plus a default that changed in commit `abc123` is not a
record of anything.

## Workflow

1. Resolve parameters fully.
2. **Write the manifest before the computation starts**, with `status: "running"`. A run
   that crashes at hour five is exactly the run you'll want a record of.
3. Run.
4. Update `status`, `wall_time_s`, `exit_code`, and the output hashes on completion or
   failure.

One directory per run, never a shared output file that runs append to:

```
runs/2026-09-21T14-03-12Z_a3f19c4_sweep-gamma/
├── manifest.json
├── params.json
├── stdout.log
├── stderr.log
└── artifacts/
```

## Dirty trees

Production runs should refuse to launch from a dirty working tree. Exploratory runs may be
dirty, but the manifest must embed the diff — a commit hash alone is a lie about a dirty
tree, and it's the most common way provenance silently fails.

Check `CONVENTIONS.md` for the project's policy; if there isn't one, recommend refusing
and make the refusal overridable with an explicit flag that gets recorded in the manifest.

## Raw versus derived

Raw run outputs are append-only and never edited in place. Everything downstream is
derived and should be reconstructible by deleting the derived directory and re-running the
analysis. If an analysis step can't be re-run because it mutated its input, that's a defect
to fix before the next production sweep.

## Figures

Every figure script takes run directories as input — never a notebook's in-memory state,
never a hand-edited CSV. Alongside `figures/<name>.pdf`, write
`figures/<name>.provenance.json`:

```json
{
  "figure": "fig3_convergence.pdf",
  "script": "scripts/plot_convergence.py",
  "script_commit": "a3f19c4",
  "runs": ["2026-09-21T14-03-12Z_a3f19c4_sweep-gamma", "..."],
  "generated_utc": "2026-09-21T15:22:03Z"
}
```

This is what makes "regenerate every figure from stored data with one command" achievable
rather than aspirational.

## Using the helper

`scripts/manifest.py` is stdlib-only and copies into a project without adding a
dependency. Read it before suggesting a project adopt a heavier experiment-tracking tool:
for most research repos this is sufficient, and it survives being run on a login node with
no network.

```python
from manifest import RunManifest

with RunManifest(outdir, params=params, seeds={"init": 1234, "noise": 5678}) as m:
    result = simulate(**params)
    save(outdir / "artifacts" / "result.npz", result)
    m.add_output(outdir / "artifacts" / "result.npz")
```

The context manager writes the manifest on entry and finalizes it on exit, including when
the body raises — which is the whole point.
