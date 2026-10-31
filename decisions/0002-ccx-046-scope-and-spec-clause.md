<!--
SPDX-FileCopyrightText: 2026 Jijie Wei and CLC contributors
SPDX-License-Identifier: Apache-2.0
-->

# 0002 — `ccx-046` scope fields and `spec_clause` prefixes

- **Status:** accepted
- **Date:** 2026-10-31
- **Governance:** Revision 1, effective 2026-10-24
- **Bootstrap:** yes — one maintainer was active when this was decided

## Decision

In `data/_vectors/clc-d/containment-crosswalk-vectors.json`, `ccx-046` declares
`out_of_scope` as the carrier linkage fields `grant_id`, `parent_grant_id` and
`workorder_id`, and carries the four runtime execution checks
(`filesystem:path_canonicalization`, `filesystem:traversal`,
`network:outbound_url_validation`, `system:command_injection`) in `derivation`.
`ccx-046` and `resolve-027` state `spec_clause` with a revision-neutral `CLC §`
prefix.

No expected outcome changes: `ccx-046` remains `contains: true`.

## Alternatives

- **Add `execution_checks` to the `ccx` schema.** Rejected: `out_of_scope` is
  defined as carrier identity and policy dimensions the profile does not map
  into a CLC field, and `additionalProperties: false` leaves no separate slot.
  Execution checks are runtime boundary checks, not carrier policy dimensions —
  the distinction `acx-001` already records.
- **Leave the revisions in `spec_clause`.** Rejected: `clc_revision` already
  states the revision the vector targets, so a second revision number in
  `spec_clause` is a copy that goes stale, and it had already drifted to 1.15
  while the corpus targets 1.19.
- **Keep the editorial fix in an issue.** Rejected: the vector text is what
  implementers read; an issue comment does not travel with the corpus.

## Objections

None raised. The vector author wrote the change, the editor reviewed the diff
and confirmed both files still validate (47 crosswalk and 27 resolve items) and
that `ccx-046` still expects containment before merging.

## Binds

- Pull request [varwof/capability#13](https://github.com/varwof/capability/pull/13),
  merged as `189e1ab`
- `data/_vectors/clc-d/containment-crosswalk-vectors.json` (`ccx-046`)
- `data/_vectors/clc-v1/resolve-vectors.json` (`resolve-027`)
- Audit item JUS-20, closed on the merge
