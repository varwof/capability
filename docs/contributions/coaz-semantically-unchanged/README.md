# COAZ "semantically unchanged" — review material

Status: discussion contribution, 2026-09-15. **This is not part of COAZ or of CLC.**
It is a review input for the OIDF AuthZEN / COAZ discussion of the invariant that a PEP must
verify that "the method, selected mapping and input values are semantically unchanged" before
applying a permit. Nothing here claims that the current COAZ text is incomplete: the material
lists the points the text does not settle, proposes a reading for each, and records which of
those readings are already executable and agreed by three implementations.

## Files

| File | What it is |
|---|---|
| `analysis.md` | 17 axes, each with a plain-language statement, the reading the current text supports (if any), a proposed reading, a positive and a negative example, the missing rule, candidate readings and the trade-off |
| `vectors.json` | 28 language-independent vectors (value-level pairs and decision-level grant/operation pairs) with expected relation, PEP action and reason code where one exists |
| `divergence-report.md` | Baseline revisions, commands, measured results of the three implementations, and where they agree or differ |
| `issue-draft.md` | Draft text for an issue in `openid/authzen` (tag `coaz`); **not posted** |
| `reproduce/` | The probe harness used for the differential run: case files plus one runner per language |

## What the material does and does not claim

- It claims that a specific set of value-level questions (keys, duplicates, strings, numbers,
  absent/null/empty, type coercion, arrays, added members, unrecognised constraint types) has an
  executable answer, and that three implementations agree on it.
- It does **not** claim that the three implementations are independent evidence: they share an
  author, so their agreement is a regression test for the reading, not third-party validation.
- It does not define the COAZ rewrite set, does not touch the deferred-effect / consequence
  admission layer, and does not claim any gap in the gateway or MCP-server hop.

## Reproduce

See `reproduce/README.md`. The recorded results were produced from detached worktrees of the
implementation repositories at the revisions listed in `divergence-report.md`.
