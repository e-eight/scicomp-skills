---
name: scale-down-first
description: Stage any expensive computation through toy, smoke, pilot, and production configurations before committing real resources, verify checkpoint/restart correctness, and prepare scheduler job scripts rather than blocking on long runs. Use this whenever work involves a cluster, a scheduler (SLURM, PBS, LSF), a parameter sweep, a GPU job, an allocation, or any computation taking more than a few minutes; whenever a user mentions submitting a job or waiting for results; and before any production run.
---

# Scale down first

Model-invoked.

Two constraints shape agent work on expensive computations. An agent session can't wait
six hours for a job, so it can't close the feedback loop the usual way. And a six-hour job
that dies at hour five on a missing output directory has burned real allocation that
somebody has to answer for.

The fix is a ladder. Each rung is a different configuration of the **same code path**, and
you don't climb until the rung below is green.

## The ladder

**Toy** — seconds, runs in-session, small enough that a verification oracle applies.
Its job is correctness. See `numerical-verification`.

**Smoke** — under two minutes, exercises every code path the production run will take:
I/O, checkpoint write and read, logging, the analysis step, and the plotting script, at
accuracy nobody would defend. Its job is to prove the pipeline is whole. A smoke run that
skips the plot script has not tested the thing that will fail at 2am.

**Pilot** — one point of the real sweep, at real resolution, on real hardware. Its job is
measurement: wall time, memory high-water mark, scaling behaviour, and the actual
per-point cost you'll multiply by to request the allocation. One pilot point is worth more
than any estimate.

**Production** — the sweep.

Never submit production without a pilot. Never pilot without a green smoke run.

## Same path, different parameters

The configurations must differ only by parameter values, never by branching. The moment
the smoke configuration takes a different code path — a different solver, a skipped
checkpoint, an `if small: ...` shortcut — it stops testing the production path, and the
untested branch is where the failure will be.

If a genuine branch is unavoidable, say so explicitly in the run record and make sure the
pilot exercises the production branch.

## Checkpoint and restart

Untested restart is the most reliable way to lose a week of compute, because you only
discover it's broken after the thing you needed to restart from has happened.

Test it directly: run N steps in one go; separately run N/2 steps, checkpoint, restart,
run N/2 more. Assert the two agree — bitwise if the code is deterministic, within the
verification tolerance otherwise. Include RNG state in the checkpoint, and include it in
the comparison, or a restarted stochastic run silently replays the same noise.

Also check: does a checkpoint written during a job that gets killed mid-write leave a
corrupt file? Write to a temporary path and rename atomically.

## Submission

Default to preparing the job script and showing it to the user rather than submitting on
their behalf — allocations are somebody's budget, and `CONVENTIONS.md` records whether
this repo permits agent submission at all.

The script should include: account and partition, wall time with margin over the pilot
measurement, node and task counts, environment reconstruction (module loads or container),
the output directory, and a manifest write before the computation starts (see
`run-provenance`). Record the scheduler job id in the manifest so the run can be matched
against accounting logs later.

Request wall time from the pilot measurement plus a factor, not from optimism. A job
killed at the limit has produced nothing unless it checkpointed — which is the other
reason the checkpoint test comes first.

## While it runs

Don't poll in a loop; it burns the session and tells you nothing. Instead, hand the user a
short list of what to check on return:

1. Exit status and whether the job hit its wall-time limit
2. First and last lines of the log — did it start where you thought, did it finish
3. The manifest's `status` field
4. The invariant assertions from `numerical-verification`, re-run against the output
5. Output file sizes and hashes against expectation

Then stop. A clean handoff of what to check beats a session spent waiting.
