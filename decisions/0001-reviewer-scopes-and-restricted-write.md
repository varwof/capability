<!--
SPDX-FileCopyrightText: 2026 Jijie Wei and CLC contributors
SPDX-License-Identifier: Apache-2.0
-->

# 0001 — Reviewer scopes and restricted write

- **Status:** accepted
- **Date:** 2026-10-31
- **Governance:** Revision 1, effective 2026-10-24
- **Bootstrap:** yes — one maintainer was active when this was decided

## Decision

The conformance reviewer appointment is one person holding three separate
scopes, each with its own evidence and expiry: CLC-A core (154 core vectors and
1,184 property cases), the CLC-1.19 minor-gate corpora (669 required and 50
optional symmetry cases), and CLC-D (64 containment and 15 authorize-chain
vectors).

The reviewer is granted `write`, limited in practice to `conformance/` and
`CONFORMANCE.md` by `CODEOWNERS` and branch protection, with
`require_code_owner_review` enabled. This replaces the `triage` grant that the
appointment originally assumed. The reviewer does not gain merge rights over
the specification or corpora, release or tag rights, or maintainer status.

## Alternatives

- **One combined scope.** Rejected: a single lapse or withdrawal would remove
  authority over classes whose evidence is unrelated, and the CLC-D scope
  depended on results that had not been published yet.
- **`triage` plus a separate conformance grant.** Rejected: the repository is on
  a personal account, where GitHub rejects the `triage` role
  (`422 Cannot assign jdieselny permission of triage`); the repository only
  offers `read`, `write` and `admin`.
- **No repository permission until a full maintainer path exists.** Rejected:
  the reviewer's work would then be recorded in issue comments rather than in
  the registry, which is the artifact `CONFORMANCE.md` treats as authoritative.

## Objections

None raised. The reviewer's own condition — that the write grant stays
conditional on published CLC-D and minor-gate results — was satisfied before the
invitation was sent: run
[41163351869](https://github.com/jdieselny/ecr-wg/actions/runs/41163351869) at
`ac4f9aa`, with all 14 vendored corpus pins matching `capability@80e483f`.

## Binds

- `MAINTAINERS.md` — three reviewer rows, commit `e2cbf49`
- `.github/CODEOWNERS` — `conformance/` and `CONFORMANCE.md` co-owned by
  `@varwof` and `@jdieselny`, commit `802ad68`
- Repository ruleset `21937083` (`DCO & CI`), `require_code_owner_review: true`
- Write invitation `340674568`
- `GOVERNANCE.md` § "Conformance review", § "Reviewer authority"
