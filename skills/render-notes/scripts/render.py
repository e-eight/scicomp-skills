"""Render notes/**/*.md and CONVENTIONS.md to HTML under notes/_html/.

Standard library only. Uses a local `pandoc` if one is on PATH, otherwise the
`pandoc/core` Docker image, run as the current user so the output isn't owned by root.

Math is rendered with MathJax, not MathML: pandoc's MathML writer silently drops
`\\tag{N}`, and the equation numbers are exactly what code cites. The trade-off is that
the HTML loads MathJax from a CDN, so math needs a network connection to display.

The output directory carries its own `.gitignore` containing `*`, so it is never
committed and the repo's own `.gitignore` needs no edit. Usage:

    python render.py [--root DIR] [--force | --check] [file.md ...]

With no files, renders every note whose HTML is missing or older than its source.
Delete notes/_html/ to clear out pages for notes that no longer exist.

Each note is checked for inline math outside $...$ (bare TeX commands, sub- and
superscripts, \\( delimiters, a space just inside the dollars), since pandoc prints that
as plain text. Problems are warnings: the note still renders. --check runs only this.
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
STYLE = FILTER.with_name("style.html")
# Pandoc's own Markdown needs a blank line before a list; GitHub's doesn't, and notes are
# usually written the GitHub way. Without this, "Assumptions:\n- a\n- b" is one paragraph.
FROM = "markdown+lists_without_preceding_blankline"
DOCKER_IMAGE = "pandoc/core"
# Pinned explicitly: distro pandoc builds default to a local MathJax 2 path that usually
# doesn't exist. MathJax 4 handles \tag inside display math.
MATHJAX_URL = "https://cdn.jsdelivr.net/npm/mathjax@4/tex-chtml.js"
# Older pandoc releases add a polyfill.io script next to MathJax. That domain changed
# hands in 2024 and served malware, so the tag is stripped from every page.
POLYFILL_TAG = re.compile(r'[ \t]*<script src="https://polyfill\.io/[^"]*"></script>\n?')

# Regions masked out before looking for math that escaped its delimiters, in this order.
# Pandoc's rules for inline math: the opening $ has a non-space on its right, the closing
# $ has a non-space on its left and no digit after it.
CODE_SPAN = re.compile(r"(`+)(.*?)\1", re.S)
MASKS = [
    re.compile(r"^(```|~~~).*?^\1[^\n]*$", re.M | re.S),  # fenced code
    re.compile(r"<!--.*?-->", re.S),                      # HTML comments
    re.compile(r"\\\$"),                                  # escaped dollar
    re.compile(r"\$\$.*?\$\$", re.S),                     # display math
    CODE_SPAN,
    # Inline math may wrap onto the next line but not past a blank one.
    re.compile(r"\$(?=\S)(?:[^$\\\n]|\\.|\n(?![ \t]*\n))*?(?<=\S)\$(?!\d)"),
    re.compile(r"\]\([^)]*\)"),                           # link targets
]
TEX_IN_CODE = re.compile(r"\\[A-Za-z]{2,}|[\^_]\{")
STRAY = [
    (re.compile(r"\\[()\[\]]"), "\\( or \\[ delimiter; use $...$ or $$...$$"),
    (re.compile(r"\\[A-Za-z]+"), "TeX command outside $...$"),
    (re.compile(r"[A-Za-z0-9)}]\^[A-Za-z0-9{(\-]"), "superscript outside $...$"),
    (re.compile(r"\b[A-Za-z]_(?:\{|[A-Za-z0-9]\b)"), "subscript outside $...$"),
    (re.compile(r"\$"), "unpaired $ (escape a literal one: \\$) or space inside the $s"),
]


def _blank(match: re.Match) -> str:
    # Keep newlines so line numbers survive masking.
    return re.sub(r"[^\n]", " ", match.group(0))


def lint_math(text: str) -> list[tuple[int, str, str]]:
    """Find inline math that pandoc won't render: (line, problem, offending text)."""
    problems = []
    for mask in MASKS:
        if mask is CODE_SPAN:
            # Math written as code renders as code, not as math.
            for m in CODE_SPAN.finditer(text):
                if TEX_IN_CODE.search(m.group(2)):
                    line = text.count("\n", 0, m.start()) + 1
                    problems.append((line, "TeX in backticks renders as code", m.group(0)))
        text = mask.sub(_blank, text)
    for number, line in enumerate(text.splitlines(), 1):
        for pattern, problem in STRAY:
            found = [m.group(0) for m in pattern.finditer(line)]
            if found:
                problems.append((number, problem, " ".join(dict.fromkeys(found))))
    return sorted(problems)


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
        return ["pandoc", "--lua-filter", str(FILTER), "--include-in-header", str(STYLE)]
    if shutil.which("docker"):
        user = f"{os.getuid()}:{os.getgid()}" if hasattr(os, "getuid") else None
        return [
            "docker", "run", "--rm",
            *(["-u", user] if user else []),
            "-v", f"{root}:/data", "-w", "/data",
            "-v", f"{FILTER.parent}:/skill:ro",
            DOCKER_IMAGE,
            "--lua-filter", f"/skill/{FILTER.name}",
            "--include-in-header", f"/skill/{STYLE.name}",
        ]
    return None


def report_math(root: Path, src: Path) -> int:
    problems = lint_math((root / src).read_text())
    for line, problem, snippet in problems:
        print(f"WARNING {src}:{line}: {problem}: {snippet}", file=sys.stderr)
    return len(problems)


def select_sources(root: Path, files: list[str]) -> list[Path]:
    if files:
        sources = []
        for f in files:
            # Relative paths work from the current directory or from the repo root.
            path = (Path(f) if Path(f).exists() else root / f).resolve()
            if not path.is_file():
                print(f"{f} does not exist; skipped.", file=sys.stderr)
            elif not path.is_relative_to(root):
                print(f"{f} is not inside {root}; skipped.", file=sys.stderr)
            else:
                sources.append(path.relative_to(root))
    else:
        sources = find_sources(root)
    return sources


def check(root: Path, files: list[str]) -> int:
    warned = sum(report_math(root, src) for src in select_sources(root, files))
    print(f"{warned} math warning(s)")
    return 1 if warned else 0


def render(root: Path, files: list[str], force: bool) -> int:
    base = pandoc_command(root)
    if base is None:
        print("Neither pandoc nor docker is on PATH; nothing rendered.", file=sys.stderr)
        return 2

    sources = select_sources(root, files)
    out_root = root / OUT_DIR
    out_root.mkdir(parents=True, exist_ok=True)
    (out_root / ".gitignore").write_text("*\n")

    # A change to the renderer itself (this script, the filter, the stylesheet) makes every
    # page stale, not just the ones whose notes changed.
    renderer_mtime = max(p.stat().st_mtime for p in (Path(__file__), FILTER, STYLE))

    rendered = failed = warned = 0
    for src in sources:
        out = output_for(src)
        html = root / out
        newest_input = max((root / src).stat().st_mtime, renderer_mtime)
        if not force and html.exists() and html.stat().st_mtime >= newest_input:
            continue
        warned += report_math(root, src)
        html.parent.mkdir(parents=True, exist_ok=True)
        cmd = base + [
            str(src), "-o", str(out),
            "--from", FROM, "--standalone", f"--mathjax={MATHJAX_URL}",
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

    print(
        f"{rendered} rendered, {failed} failed, {warned} math warning(s), "
        f"output in {OUT_DIR}/"
    )
    return 1 if failed else 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=".", help="repo root (default: .)")
    parser.add_argument("files", nargs="*", help="specific .md files to render")
    parser.add_argument(
        "--force", action="store_true", help="re-render even if up to date"
    )
    parser.add_argument(
        "--check", action="store_true",
        help="only report inline math pandoc won't render; exit 1 if any",
    )
    args = parser.parse_args()
    root = Path(args.root).resolve()
    if args.check:
        sys.exit(check(root, args.files))
    sys.exit(render(root, args.files, args.force))


if __name__ == "__main__":
    main()
