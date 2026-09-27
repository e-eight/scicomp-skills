---
name: render-notes
description: Render the project's Markdown notes (notes/**/*.md and CONVENTIONS.md) to standalone HTML with pandoc, so equations, equation numbers, and tables are readable in a browser. Output goes to notes/_html/, which ignores itself in git. Use this only when the user asks to render, preview, or view notes as HTML, or asks to see a derivation, experiment record, or conventions file rendered. Do not run it unprompted after writing notes.
---

# Render notes

Model-invoked, but only on request. Ships `scripts/render.py`.

The notes are the record; the HTML is a local view of them. Nothing here changes a note, and
nothing rendered is ever committed.

## Running it

From the repo root, where `<skill-dir>` is the directory holding this file:

```bash
python <skill-dir>/scripts/render.py              # every note that changed since last render
python <skill-dir>/scripts/render.py notes/derivations/03-foo.md   # just one
python <skill-dir>/scripts/render.py --force      # everything, e.g. after upgrading pandoc
python <skill-dir>/scripts/render.py --check      # only check the math delimiters
```

`notes/derivations/03-foo.md` becomes `notes/_html/derivations/03-foo.html`, and
`CONVENTIONS.md` becomes `notes/_html/CONVENTIONS.html`. Relative links between notes are
rewritten to point at the HTML, so cross-references keep working in the browser.

Tell the user the path of the page they asked for. Don't open a browser for them.

## Requirements

A local `pandoc`, or failing that `docker`, in which case the script runs the `pandoc/core`
image as the current user. If neither is on PATH the script exits 2 and renders nothing.
Report that to the user and suggest one of the two. Don't try to install either.

## Math

Rendered with MathJax 4, loaded from jsDelivr, so a page needs a network connection to show
its math. MathML would work offline, but pandoc's MathML writer silently drops `\tag{N}`,
and those equation numbers are what code cites. Don't switch to it.

Write math the way pandoc Markdown expects: `$...$` inline with no space inside the
dollars, and `$$...$$` for display. Anything else (bare `\epsilon`, `x^2` or `H_0` in
prose, `\(...\)`, TeX in backticks) shows up in the page as plain text or code.

Before rendering a note, the script checks it for exactly these and prints a `WARNING`
with the file and line for each one. The note still renders. When there are warnings,
list them for the user and offer to fix the note. Don't edit it without asking, because
nothing here changes a note. `render.py --check [file.md ...]` runs only the check,
renders nothing, and exits 1 if it finds anything. The check doesn't flag Unicode
symbols like ε or →, which render fine as text.

## Layout and lists

`scripts/style.html` goes in after pandoc's default stylesheet and widens the page from
pandoc's 36em to most of the window, rules and stripes table rows, and lets tables and long
equations scroll sideways rather than overflow. Edit it to change the look.

Notes are read as pandoc Markdown with `lists_without_preceding_blankline`, so a list
directly under a line of text renders as a list, the way it does on GitHub. A nested list
still has to be indented to line up with its parent item's text: two spaces under `-`,
three under `1.`.

## Stale pages

A page is re-rendered when its source is newer, or when anything in `scripts/` is — so
editing the stylesheet refreshes every page on the next run. Pages for notes that were renamed or deleted
are not removed. `rm -rf notes/_html` clears everything, and the next run rebuilds it.
