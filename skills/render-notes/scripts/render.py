"""Render notes/**/*.md and CONVENTIONS.md to HTML under notes/_html/.

Standard library only. Uses a local `pandoc` if one is on PATH, otherwise the
`pandoc/core` Docker image, run as the current user so the output isn't owned by root.

Math is rendered with MathJax, not MathML: pandoc's MathML writer silently drops
`\\tag{N}`, and the equation numbers are exactly what code cites. The trade-off is that
the HTML loads MathJax from a CDN, so math needs a network connection to display.

The output directory carries its own `.gitignore` containing `*`, so it is never
committed and the repo's own `.gitignore` needs no edit. Usage:

    python render.py [--root DIR] [--force] [file.md ...]

With no files, renders every note whose HTML is missing or older than its source.
Delete notes/_html/ to clear out pages for notes that no longer exist.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

OUT_DIR = Path("notes") / "_html"
FILTER = Path(__file__).resolve().parent / "md_links.lua"
DOCKER_IMAGE = "pandoc/core"
# Pinned explicitly: distro pandoc builds default to a local MathJax 2 path that usually
# doesn't exist. MathJax 3 handles \tag inside display math.
MATHJAX_URL = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml-full.js"
# Older pandoc releases add a polyfill.io script next to MathJax. That domain changed
# hands in 2024 and served malware, so the tag is stripped from every page.
POLYFILL_TAG = re.compile(r'[ \t]*<script src="https://polyfill\.io/[^"]*"></script>\n?')


def find_sources(root: Path) -> list[Path]:
    notes = root / "notes"
    sources = [
        p.relative_to(root)
        for p in sorted(notes.rglob("*.md"))
        if OUT_DIR not in p.relative_to(root).parents
    ] if notes.is_dir() else []
    if (root / "CONVENTIONS.md").is_file():
        sources.append(Path("CONVENTIONS.md"))
    return sources


def output_for(src: Path) -> Path:
    # notes/derivations/03-x.md -> notes/_html/derivations/03-x.html
    rel = src.relative_to("notes") if src.parts[0] == "notes" else src
    return OUT_DIR / rel.with_suffix(".html")


def pandoc_command(root: Path) -> list[str] | None:
    if shutil.which("pandoc"):
        return ["pandoc", "--lua-filter", str(FILTER)]
    if shutil.which("docker"):
        user = f"{os.getuid()}:{os.getgid()}" if hasattr(os, "getuid") else None
        return [
            "docker", "run", "--rm",
            *(["-u", user] if user else []),
            "-v", f"{root}:/data", "-w", "/data",
            "-v", f"{FILTER.parent}:/skill:ro",
            DOCKER_IMAGE, "--lua-filter", f"/skill/{FILTER.name}",
        ]
    return None


def render(root: Path, files: list[str], force: bool) -> int:
    base = pandoc_command(root)
    if base is None:
        print("Neither pandoc nor docker is on PATH; nothing rendered.", file=sys.stderr)
        return 2

    if files:
        sources = [Path(f).resolve().relative_to(root) for f in files]
    else:
        sources = find_sources(root)
    out_root = root / OUT_DIR
    out_root.mkdir(parents=True, exist_ok=True)
    (out_root / ".gitignore").write_text("*\n")

    rendered = failed = 0
    for src in sources:
        out = output_for(src)
        html = root / out
        if not force and html.exists() and html.stat().st_mtime >= (root / src).stat().st_mtime:
            continue
        html.parent.mkdir(parents=True, exist_ok=True)
        cmd = base + [
            str(src), "-o", str(out),
            "--from", "markdown", "--standalone", f"--mathjax={MATHJAX_URL}",
            "--metadata", f"pagetitle={src.stem}",
        ]
        result = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
        if result.returncode != 0:
            failed += 1
            print(f"FAILED {src}\n{result.stderr.strip()}", file=sys.stderr)
        else:
            html.write_text(POLYFILL_TAG.sub("", html.read_text()))
            rendered += 1
            print(f"{src} -> {out}")

    print(f"{rendered} rendered, {failed} failed, output in {OUT_DIR}/")
    return 1 if failed else 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=".", help="repo root (default: .)")
    parser.add_argument("files", nargs="*", help="specific .md files to render")
    parser.add_argument(
        "--force", action="store_true", help="re-render even if up to date"
    )
    args = parser.parse_args()
    sys.exit(render(Path(args.root).resolve(), args.files, args.force))


if __name__ == "__main__":
    main()
