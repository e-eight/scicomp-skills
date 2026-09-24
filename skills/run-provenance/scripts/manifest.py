"""Write a provenance manifest for a computational run.

Standard library only, so it can be vendored into a research repo without adding a
dependency and still works on a login node with no network.

Typical use:

    from manifest import RunManifest

    with RunManifest(outdir, params=params, seeds={"init": 1234}) as m:
        result = simulate(**params)
        path = save(outdir / "artifacts" / "result.npz", result)
        m.add_output(path)

The manifest is written on entry with status "running" and finalized on exit, including
when the body raises. A run that dies at hour five is exactly the run you want recorded.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import socket
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

MANIFEST_NAME = "manifest.json"
_HASH_CHUNK = 1 << 20


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(cmd, cwd=None):
    try:
        out = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, timeout=30, check=False
        )
        return out.stdout.strip() if out.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def git_state(repo: Path | None = None, capture_diff: bool = True) -> dict:
    """Commit, branch, dirty flag, and the diff if the tree is dirty.

    A commit hash recorded from a dirty tree is a lie about what ran, so the diff is
    captured by default.
    """
    repo = Path(repo or Path.cwd())
    commit = _run(["git", "rev-parse", "HEAD"], cwd=repo)
    if commit is None:
        return {"available": False}
    status = _run(["git", "status", "--porcelain"], cwd=repo) or ""
    dirty = bool(status.strip())
    state = {
        "available": True,
        "commit": commit,
        "short": commit[:7],
        "branch": _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo),
        "dirty": dirty,
    }
    if dirty and capture_diff:
        state["diff"] = _run(["git", "diff", "HEAD"], cwd=repo)
        state["untracked"] = [
            line[3:] for line in status.splitlines() if line.startswith("??")
        ]
    return state


def environment() -> dict:
    """Everything that can change a floating point result without changing the code."""
    env = {
        "python": sys.version.split()[0],
        "executable": sys.executable,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "hostname": socket.gethostname(),
        "cpu_count": os.cpu_count(),
        "packages": _packages(),
        "threads": {
            var: os.environ[var]
            for var in (
                "OMP_NUM_THREADS",
                "MKL_NUM_THREADS",
                "OPENBLAS_NUM_THREADS",
                "NUMEXPR_NUM_THREADS",
            )
            if var in os.environ
        },
    }
    scheduler = {
        key: os.environ[key]
        for key in os.environ
        if key.startswith(("SLURM_", "PBS_", "LSB_", "COBALT_"))
        and key
        in {
            "SLURM_JOB_ID",
            "SLURM_JOB_NAME",
            "SLURM_JOB_PARTITION",
            "SLURM_NNODES",
            "SLURM_NTASKS",
            "SLURM_JOB_ACCOUNT",
            "PBS_JOBID",
            "LSB_JOBID",
            "COBALT_JOBID",
        }
    }
    if scheduler:
        env["scheduler"] = scheduler
    return env


def _packages() -> dict:
    """Versions of numerics-relevant packages that are actually importable here."""
    versions = {}
    for name in (
        "numpy",
        "scipy",
        "pandas",
        "numba",
        "jax",
        "torch",
        "cupy",
        "mpi4py",
        "h5py",
        "qutip",
        "netket",
        "matplotlib",
    ):
        mod = sys.modules.get(name)
        if mod is None:
            try:
                from importlib import metadata

                versions[name] = metadata.version(name)
            except Exception:
                continue
        else:
            versions[name] = getattr(mod, "__version__", "unknown")
    if "numpy" in versions:
        versions["blas"] = _blas_info()
    return versions


def _blas_info():
    """BLAS backend changes reduction order, which changes low bits. Worth recording."""
    try:
        import numpy as np

        cfg = getattr(np, "__config__", None)
        if cfg is not None and hasattr(cfg, "show"):
            info = getattr(cfg, "get_info", lambda _: {})("blas_opt_info")
            if info:
                return str(info.get("libraries", info))[:200]
    except Exception:
        pass
    return None


def file_hash(path: os.PathLike | str, algorithm: str = "sha256") -> str:
    h = hashlib.new(algorithm)
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(_HASH_CHUNK), b""):
            h.update(chunk)
    return f"{algorithm}:{h.hexdigest()}"


def _describe(path: os.PathLike | str) -> dict:
    p = Path(path)
    entry = {"path": str(p)}
    if p.is_file():
        entry["bytes"] = p.stat().st_size
        entry["hash"] = file_hash(p)
    else:
        entry["missing"] = True
    return entry


class RunManifest:
    """Context manager that records a run's provenance.

    Parameters
    ----------
    outdir : path
        Run directory. Created if absent; the manifest lands inside it.
    params : dict
        The **resolved** parameters, after defaults and overrides are applied. Recording
        the command line instead is the most common way provenance silently fails.
    seeds : dict
        Every RNG stream, by name. One global seed is rarely enough to reproduce a run
        that uses more than one stream or more than one rank.
    inputs : iterable of paths
        Input files, recorded with content hashes.
    require_clean : bool
        Refuse to start if the working tree is dirty. Recommended for production runs.
    """

    def __init__(
        self,
        outdir,
        params: dict,
        seeds: dict | None = None,
        inputs=(),
        run_id: str | None = None,
        repo=None,
        require_clean: bool = False,
        extra: dict | None = None,
    ):
        self.outdir = Path(outdir)
        self.path = self.outdir / MANIFEST_NAME
        self.git = git_state(repo)
        if require_clean and self.git.get("dirty"):
            raise RuntimeError(
                "Working tree is dirty; refusing to start a production run. "
                "Commit, or pass require_clean=False to record the diff instead."
            )
        short = self.git.get("short", "nogit")
        self.data = {
            "run_id": run_id or f"{_utc_now().replace(':', '-')}_{short}",
            "timestamp_utc": _utc_now(),
            "status": "running",
            "git": self.git,
            "params": params,
            "seeds": seeds or {},
            "env": environment(),
            "inputs": [_describe(p) for p in inputs],
            "outputs": [],
            "argv": sys.argv,
        }
        if extra:
            self.data.update(extra)
        self._t0 = None

    # -- lifecycle ---------------------------------------------------------

    def __enter__(self) -> "RunManifest":
        self.outdir.mkdir(parents=True, exist_ok=True)
        (self.outdir / "artifacts").mkdir(exist_ok=True)
        self._t0 = time.time()
        self.write()
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        self.data["wall_time_s"] = round(time.time() - self._t0, 3)
        if exc_type is None:
            self.data["status"] = "complete"
            self.data["exit_code"] = 0
        else:
            self.data["status"] = "failed"
            self.data["exit_code"] = 1
            self.data["error"] = {
                "type": exc_type.__name__,
                "message": str(exc),
                "traceback": "".join(traceback.format_exception(exc_type, exc, tb))[
                    -4000:
                ],
            }
        self.data["outputs"] = [_describe(p["path"]) for p in self.data["outputs"]]
        self.write()
        return False  # never swallow the exception

    # -- recording ---------------------------------------------------------

    def add_output(self, path) -> None:
        """Register an artifact. Hashed at exit, so it may not exist yet."""
        self.data["outputs"].append({"path": str(Path(path))})

    def note(self, key: str, value) -> None:
        """Attach anything else worth recording: iteration counts, convergence flags."""
        self.data.setdefault("notes", {})[key] = value

    def write(self) -> Path:
        tmp = self.path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(self.data, indent=2, default=str))
        tmp.replace(self.path)  # atomic, so a killed job never leaves half a manifest
        return self.path


def read_manifest(run_dir) -> dict:
    return json.loads((Path(run_dir) / MANIFEST_NAME).read_text())


def write_figure_provenance(figure_path, script_path, run_dirs) -> Path:
    """Record which runs a figure was built from, beside the figure itself."""
    figure_path = Path(figure_path)
    out = figure_path.with_suffix(".provenance.json")
    out.write_text(
        json.dumps(
            {
                "figure": figure_path.name,
                "script": str(script_path),
                "script_commit": git_state().get("commit"),
                "runs": [Path(d).name for d in run_dirs],
                "generated_utc": _utc_now(),
            },
            indent=2,
        )
    )
    return out


if __name__ == "__main__":
    # Smoke test: python manifest.py <outdir>
    target = Path(sys.argv[1] if len(sys.argv) > 1 else "./_manifest_demo")
    with RunManifest(target, params={"n": 4, "dt": 0.01}, seeds={"init": 1234}) as m:
        artifact = target / "artifacts" / "demo.txt"
        artifact.write_text("hello\n")
        m.add_output(artifact)
        m.note("iterations", 12)
    print(json.dumps(read_manifest(target), indent=2)[:800])
