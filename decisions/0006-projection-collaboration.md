<!--
SPDX-FileCopyrightText: 2026 Jijie Wei and CLC contributors
SPDX-License-Identifier: Apache-2.0
-->

# 0006 — Projection collaboration without a second maintainer

- **Status:** accepted
- **Date:** 2026-10-31
- **Governance:** Revision 2 (records 0003 onward, published together)
- **Bootstrap:** yes — one maintainer was active when this was decided
- **External evidence:** none — bootstrap, no second maintainer

## Decision

Three changes, all aimed at the case where an outside collaborator builds a
projection into CLC while the project still has one maintainer.

1. A change confined to `contrib/` merges on CI alone, with no review window,
   because nothing in `contrib/` is cited as conformance evidence. Promotion out
   of `contrib/` — a vector, a registered binding, a normative sentence — is a
   normal or core change and is reviewed as one.
2. A decision record carries an `External evidence` field: who re-ran the change
   at which commit, or `none`.
3. A conformance reviewer does not approve a change to the specification, the
   corpora or a binding. Where such a change bears on a claim, the reviewer
   re-runs the pinned corpora at the candidate commit and publishes the result.

## Alternatives

- **Keep `contrib/` under the 7-day window.** Rejected: it is the directory
  outside collaborators iterate in, nothing there is evidence, and pricing each
  probe iteration at a week ends in either batching unrelated work or a bypass —
  the two outcomes the window exists to prevent.
- **Let the appointed reviewer approve corpus changes, since a reviewer is
  available and no second maintainer is.** Rejected twice over. The role is
  evidential by construction, and the reviewer's own three claims are made
  against those corpora, so approval would be asked of the one person whose
  evidence depends on the answer.
- **Leave the single-maintainer state unstated in records.** Rejected: an
  undocumented bypass is indistinguishable from an absent process. A record that
  says `none` is weaker evidence than a re-run and far stronger than silence.
- **Require an external re-run before any corpus change.** Rejected for now: it
  would make an outside party a gate on core work, which is the same capture in
  the other direction. The field records what exists rather than inventing a
  requirement nobody has agreed to.

## Objections

None raised. The `contrib/` lane assumes the status table in
`contrib/README.md` stays current; if it drifts, the lane is still safe, because
the lane's safety comes from `contrib/` never being cited as evidence rather than
from the table.

## Binds

- `GOVERNANCE.md` — `Non-normative work in contrib/`, `Reviewer authority`,
  `Decision records`
- `decisions/README.md` — required fields, index
