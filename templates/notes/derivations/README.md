# Derivations

Numbered, not dated — the filename is an address that code cites, so it must be stable.

Code citing a result names the equation:

```python
# implements Eq. (17) of notes/derivations/02-error-bound.md
```

Once a derivation is verified and cited, its equations and their numbers are frozen. Never
rewrite one silently. A correction is the one permitted change:

- Add a new numbered section with the corrected result. It names the section it replaces
  and says why.
- In the old section, strike through the wrong text and add one line, such as
  "Superseded by §4, Eq. (23)". Change nothing else there, and keep its number.
- Grep for citations of the superseded equation and re-point them in the same commit.

If a renumber is unavoidable, grep for citations and fix them in the same commit.

Start from `00-template.md`.

A file `NN-slug.explained.md` next to a record is a walk-through written by
`explain-derivation`. It is for reading, not citing: code always cites the record.

## Index

| File | Derives | Status | Cited by |
| --- | --- | --- | --- |
| `00-template.md` | — | template | — |

<!-- Keep this index current. Once there are more than a handful of derivations, a flat
     directory stops being navigable and the agent starts guessing which file to read. -->
