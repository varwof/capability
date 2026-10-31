<!--
SPDX-FileCopyrightText: 2026 Jijie Wei and CLC contributors
SPDX-License-Identifier: Apache-2.0
-->

# 0008 — Record the reference implementation as a claim

- **Status:** accepted
- **Date:** 2026-10-31
- **Governance:** Revision 2 (records 0003 onward, published together)
- **Bootstrap:** yes — one maintainer was active when this was decided
- **External evidence:** none — bootstrap, no second maintainer

## Decision

`conformance/registry.md` gains `reg-2026-002`, a CLC-A core claim for
`varwof/register` at `e422020` against the corpus at `1ef567c`: 154/154 vectors
and 1,184/1,184 property cases. The row is marked as a bootstrap review and
states that the implementation shares an author with the corpora.

The transfer criterion "at least two implementations recorded in
`conformance/registry.md`" is now checkable: two rows, two authors, one of them
declared not independent.

## Alternatives

- **Leave the reference implementation unrecorded.** Rejected: the criterion
  then reads as unmet by omission, and a reader cannot tell whether the project
  has one recorded implementation or has simply never recorded its own. The
  registry is the authority; an unrecorded claim does not exist.
- **Record it as an ordinary claim.** Rejected: the editor wrote the corpus and
  the implementation, so the row is regression evidence and saying otherwise
  would be the exact self-certification P12 exists to prevent.
- **Wait for a second reviewer to sign it.** Rejected as a precondition: the
  claim's value is that it makes the two-author picture visible now, and the
  bootstrap mark already carries its own limitation. A reviewer clearing the
  mark later changes the mark, not the row's existence.
- **Record `varwof/register` plus the Python and TypeScript ports as three
  claims.** Rejected: three rows by one author would look like three independent
  pieces of evidence to anyone skimming the table, which is the failure mode
  `CONFORMANCE.md` §5 names explicitly.

## Objections

None raised. The row also records a provenance defect it exposed: the
`clc-conformance` workflow clones the corpus without pinning a commit, so a
public run cannot state which corpus it used. The reproduction in the notes is
therefore local, and the notes say so rather than presenting it as public
evidence.

## Binds

- `conformance/registry.md` — `reg-2026-002` and its notes
- `CONFORMANCE.md` §5 — independence rule applied to the row
- Follow-up: pin the corpus commit in `varwof/register`'s `clc-conformance.yml`
