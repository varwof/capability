<!--
SPDX-FileCopyrightText: 2026 Jijie Wei and CLC contributors
SPDX-License-Identifier: Apache-2.0
-->

# Maintainers

## Current

| Maintainer | GitHub | Scope | Since |
|---|---|---|---|
| Jijie Wei | [@varwof](https://github.com/varwof) | CLC core, corpora, releases, initial governance | 2026-09 |

## Open roles

The project is actively seeking maintainers for:

- independent implementations;
- carrier bindings and projection profiles;
- security review;
- additional conformance-review capacity; the CLC-A, CLC-1.19 and CLC-D scopes
  are covered by the appointed reviewer (`CONFORMANCE.md`).

Maintainer eligibility and appointment are defined in `GOVERNANCE.md`.

## Conformance reviewers

| Reviewer | Scope | Since | Term ends | Verified |
|---|---|---|---|---|
| Justin D. Kintzele ([@jdieselny](https://github.com/jdieselny)) | CLC-A core corpus: 154 core vectors and 1,184 property cases, including verdict, reason code and the unresolved channel | 2026-10 | 2027-10 | 2026-10-27 (appointment) |
| Justin D. Kintzele ([@jdieselny](https://github.com/jdieselny)) | CLC-1.19 minor-gate corpora: 669 required cases and 50 optional symmetry cases | 2026-10 | 2027-10 | 2026-10-31, `ac4f9aa`, run [41163351869](https://github.com/jdieselny/ecr-wg/actions/runs/41163351869) |
| Justin D. Kintzele ([@jdieselny](https://github.com/jdieselny)) | CLC-D: 64 containment vectors and 15 authorize-chain vectors | 2026-10 | 2027-10 | 2026-10-31, `ac4f9aa`, run [41163351869](https://github.com/jdieselny/ecr-wg/actions/runs/41163351869) |

Appointed 2026-10-27 on the reviewer's written acceptance, which carried a
P12 independence statement and a standing commitment to rerun the corpora on
each revision published here. The appointment is one person with three separate
scopes, not one combined scope. CLC-A is active. The CLC-1.19 and CLC-D scopes
were verified at `ac4f9aa` in public run
[41163351869](https://github.com/jdieselny/ecr-wg/actions/runs/41163351869):
669/669 required and 50/50 optional symmetry for the minor gate, and 64/64
containment plus 15/15 authorize-chain for CLC-D. The 14 vendored corpus pins
match `capability@80e483f`. Each scope keeps its own evidence and expiry; if one
lapses or is withdrawn, the others do not move. CLC-E and governance votes are
outside the reviewer role. Claims authored by the reviewer are outside the
reviewer's scope in every class: the reviewer authored `reg-2026-001` and
recuses from it. Term 12 months, renewable; the end date is in the `Term ends` column and a row
whose date has passed is marked `expired` until it is renewed. The role and its limits are in
`GOVERNANCE.md`; review ownership is recorded in `.github/CODEOWNERS`, which
takes effect only if the reviewer is given write access.

Reviewer scope, term and recusal rules are in `GOVERNANCE.md`; the procedure
and checklist are in `CONFORMANCE.md`; verified claims are recorded in
`conformance/registry.md`.

## Emeritus

None.
