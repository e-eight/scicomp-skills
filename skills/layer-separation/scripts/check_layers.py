"""Check that imports respect the model / method / driver / analysis layering.

Standard library only. Reads `.layers.json` from the repo root:

    {
      "package": "myproject",
      "layers": {
        "model":    ["src/myproject/model/**"],
        "method":   ["src/myproject/method/**"],
        "driver":   ["src/myproject/driver/**", "scripts/run_*.py"],
        "analysis": ["src/myproject/analysis/**", "scripts/plot_*.py"]
      }
    }

The allowed edges are fixed, because the whole value of the rule is that it is not
negotiable per-project:

    driver   -> model, method
    model    -> (nothing)
    method   -> (nothing)
    analysis -> (nothing)

Anything not matched by a glob is unassigned and ignored, so you can adopt this on part of
a repo first. Usage:

    python check_layers.py [repo_root]

Exits 1 if any forbidden import is found, so it drops into CI unchanged.
"""

from __future__ import annotations

import ast
import json
import sys
from fnmatch import fnmatch
from pathlib import Path

CONFIG_NAME = ".layers.json"

ALLOWED: dict[str, set[str]] = {
    "model": set(),
    "method": set(),
    "driver": {"model", "method"},
    "analysis": set(),
}

RATIONALE = {
    ("model", "method"): "the model must not know how it is solved",
    ("method", "model"): "the solver must work for any model satisfying its interface",
    ("model", "driver"): "physics must not depend on run bookkeeping",
    ("method", "driver"): "solvers must not know about run directories or I/O",
    ("model", "analysis"): "physics must not depend on plotting",
    ("method", "analysis"): "solvers must not depend on plotting",
    ("driver", "analysis"): "drivers produce artifacts; analysis consumes them separately",
    ("analysis", "model"): "analysis must read results from disk, never recompute physics",
    ("analysis", "method"): "analysis must read results from disk, never re-solve",
    ("analysis", "driver"): "analysis must not trigger runs",
}


def load_config(root: Path) -> dict:
    path = root / CONFIG_NAME
    if not path.exists():
        sys.exit(
            f"No {CONFIG_NAME} found in {root}.\n"
            "Create one mapping each layer to path globs; see the module docstring."
        )
    config = json.loads(path.read_text())
    unknown = set(config.get("layers", {})) - set(ALLOWED)
    if unknown:
        sys.exit(f"Unknown layer(s) in {CONFIG_NAME}: {sorted(unknown)}")
    return config


def layer_of(rel: str, layers: dict[str, list[str]]) -> str | None:
    for name, patterns in layers.items():
        if any(fnmatch(rel, pat) for pat in patterns):
            return name
    return None


def module_layer(module: str, package: str, layers: dict[str, list[str]]) -> str | None:
    """Map an imported dotted module name onto a layer by matching its path fragment.

    `myproject.method.integrators` matches the glob `src/myproject/method/**` because the
    fragment `myproject/method` appears in it. Crude, but it needs no import machinery and
    never executes project code.
    """
    if package and not module.startswith(package):
        return None
    fragment = module.replace(".", "/")
    for name, patterns in layers.items():
        for pat in patterns:
            if fragment in pat.replace("**", "").replace("*", ""):
                return name
            if fnmatch(fragment + "/x.py", pat) or fnmatch(fragment + ".py", pat):
                return name
    return None


def imports_in(path: Path) -> list[tuple[str, int]]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (SyntaxError, UnicodeDecodeError) as exc:
        print(f"  skipped {path}: {exc}")
        return []
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found += [(alias.name, node.lineno) for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            found.append((node.module, node.lineno))
    return found


def check(root: Path) -> int:
    config = load_config(root)
    layers = config.get("layers", {})
    package = config.get("package", "")

    violations = []
    for path in sorted(root.rglob("*.py")):
        rel = str(path.relative_to(root))
        if any(part.startswith(".") or part == "__pycache__" for part in path.parts):
            continue
        src = layer_of(rel, layers)
        if src is None:
            continue
        for module, lineno in imports_in(path):
            dst = module_layer(module, package, layers)
            if dst is None or dst == src:
                continue
            if dst not in ALLOWED[src]:
                violations.append((rel, lineno, src, dst, module))

    if not violations:
        print("Layer check passed: no forbidden imports.")
        return 0

    print(f"Layer check failed: {len(violations)} forbidden import(s).\n")
    for rel, lineno, src, dst, module in violations:
        why = RATIONALE.get((src, dst), "not an allowed dependency edge")
        print(f"{rel}:{lineno}")
        print(f"  {src} -> {dst}   (imports {module})")
        print(f"  {why}\n")
    return 1


if __name__ == "__main__":
    sys.exit(check(Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()))
