<!--
SPDX-FileCopyrightText: 2026 Jijie Wei and CLC contributors
SPDX-License-Identifier: Apache-2.0
-->

# CLC Conformance Registry

Status: initial registry, effective 2026-10-27.

This registry records evidence. It assigns nothing: no code points, media types,
namespaces, reason codes or binding names are allocated here, and this is not an
IANA registry. Parameters are defined by the specification; where CLC is
published through the IETF, registration follows the IANA Considerations section
of the draft. If an entry here ever conflicts with a registered parameter, the
registered parameter governs.

An entry records a corpus run at a pinned commit. It is not an endorsement of an
implementation, and its absence means a claim is unrecorded, not that it failed.

One row per verified conformance claim. The procedure and checklist are in
`CONFORMANCE.md`. Rows are append-only in substance: a superseded claim gets a
new row and the old row is marked `superseded`; a wrong claim is marked
`withdrawn` with the reason and is not deleted.

CLC-E is not in this registry. It is implemented and pinned by a corpus but not
claimed.

## Verified claims

| ID | Implementation | Class | Revision | Impl. commit | Corpus commit | Result | Reviewer | Scope / term | Date | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| `reg-2026-001` | `jdieselny/ecr-wg` → `rust/clc-rust-cleanroom` | CLC-A core | CLC-1.19, Section 12 core corpus | `8db495ac68f9` | `1f3cbdf` | 44 tests; 154/154; 1,184/1,184 | Jijie Wei (editor, bootstrap) | bootstrap review; no appointed scope | 2026-10-27 | verified |
| `reg-2026-002` | `varwof/register` (Go) | CLC-A core | CLC-1.19, Section 12 core corpus | `e422020b0e55` | `1ef567c` | 154/154; 1,184/1,184 | Jijie Wei (editor, bootstrap) | bootstrap review; not independent | 2026-10-31 | verified |
| `reg-2026-003` | `jdieselny/ecr-wg` → `rust/clc-rust-cleanroom` | CLC-D | CLC-1.19, §13.4 and §13.11 base corpora | `3c1a97e` | `80e483f` | 79/79 (64 containment + 15 authorize-chain) | Jijie Wei (editor, bootstrap) | bootstrap review; no appointed scope | 2026-11-03 | verified |

### `reg-2026-001` — notes

- Public CI: <https://github.com/jdieselny/ecr-wg/actions/runs/40503426566>
  (success at `8db495a`).
- Corpus hashes at `1f3cbdf`:
  - `data/_vectors/clc-v1/vectors.json`
    `3c1a5672d6f107444903f06c51a71ce92451f1b45ca92c5a84a345b0de5a5bbd`
  - `data/_vectors/clc-v1/property-cases.json`
    `f00ed1f49299293ac9fff1e10287b9642aa49d6dacf25b2b4a1be2d7103b2f07`
- Commands: `cargo test`; `cargo run --release -- --vector
  vectors/clc-a-core-vectors.json`; `cargo run --release -- --properties
  vectors/property-cases.json`.
- Bootstrap: the editor performed this review under the bootstrap rule in
  `GOVERNANCE.md`. The implementation author was appointed provisional CLC-A
  core reviewer on 2026-10-27 (`MAINTAINERS.md`) and recuses from this row, so
  the bootstrap mark stands until a different appointed reviewer re-checks the
  claim.
- Reviewer appointment: `@jdieselny`, CLC-A core corpus, provisional, since
  2026-10-27. The appointment does not cover this implementation.
- Independence: cleanroom implementation; no access to the `varwof` reference
  implementations, stated by the author and supported by the repository's
  cleanroom leash.
- Residual gaps: the CLC-1.19 minor-gate corpora (`param_bounds`, §6.6 meet,
  `Resolve`, `ConstraintUnion`, scheme declaration, declared domains) were not
  run; no CLC-D official corpus was run. The row records the core corpus, not a
  full CLC-1.19 or CLC-D claim.

### `reg-2026-002` — notes

- Public CI: <https://github.com/varwof/register/actions/runs/41149493086>
  (`clc-conformance` at `e422020`, success).
- That workflow clones `varwof/capability` `--depth 1` without pinning the commit,
  so the run does not record which corpus it used. The hashes below are from
  `capability@1ef567c`; the run was reproduced at `e422020` against those files:
  `154/154` vectors and `1,184/1,184` property cases (869 order-symmetry checks,
  841 closure probes).
- Corpus hashes at `1ef567c`, unchanged since `1f3cbdf`:
  - `data/_vectors/clc-v1/vectors.json`
    `3c1a5672d6f107444903f06c51a71ce92451f1b45ca92c5a84a345b0de5a5bbd`
  - `data/_vectors/clc-v1/property-cases.json`
    `f00ed1f49299293ac9fff1e10287b9642aa49d6dacf25b2b4a1be2d7103b2f07`
- Commands: `CLC_VECTORS=<capability>/data/_vectors/clc-v1/vectors.json go run
  ./cmd/vectors-run/`; `CLC_PROPERTY_CASES=<capability>/data/_vectors/clc-v1/property-cases.json
  go test -count=1 ./semantics/ -run TestIntersectionProperty -v`.
- Independence: the implementation shares an author with the corpora. It is
  regression evidence, not independent evidence, and it does not count towards
  P12 or the two-implementation transfer criterion on its own.
- Bootstrap: the editor reviewed an implementation the editor wrote, which the
  reviewer rules would otherwise exclude. The row stays `bootstrap` until an
  appointed reviewer whose scope covers CLC-A re-checks it.
- Residual gaps: this row claims the CLC-A core corpus only. The CLC-D corpora
  and the CLC-1.19 minor-gate corpora are not claimed here even where the
  implementation passes them locally, and independence is explicitly not
  claimed, so the row does not count towards the two-implementation criterion.
- Pinning gap, now closed: `clc-conformance.yml` pins the corpus commit
  (`CLC_CAPABILITY_SHA`), asserts the checked-out commit, and prints it with the
  two corpus hashes at the start of every run. This row was recorded before that
  pin existed and cites the corpus it was reproduced against.

### `reg-2026-003` — notes

- Report: `varwof/capability#14`.
- Public CI: <https://github.com/jdieselny/ecr-wg/actions/runs/41191306714>
  (success at `3c1a97e`).
- Corpus hashes at `80e483f`, byte-identical at `1f3cbdf` and at `18f6b1a`:
  - `data/_vectors/clc-d/containment-vectors.json`
    `3d03e5318f1e0cef07bd6cb38111cf6b7fbcc24aa13bd83fb7728ee1d4527b13`
  - `data/_vectors/clc-d/authorize-chain-vectors.json`
    `1ae22422c4c8632fa2d391473f1a9a244845d079baf381875134597409fcfa12`
- Commands: `cargo run --release -- --clc-d`;
  `python3 scripts/verify_vector_pins.py`.
- Assertion coverage checked against the corpus rather than taken from the
  report: 31 of 64 containment vectors assert `contains: false` with a reason
  (`params_not_narrower` 20, `child_exceeds_parent` 4, `different_namespace` 2,
  `unsupported_wildcard` 2, `invalid_params_null` 2, `missing_capability_id`
  1); 8 of 15 chain vectors assert a non-empty reason; `expect.unresolved` is
  present on 10 of 15 and non-empty on `ac-011`, whose verdict is
  `allow_unresolved`.
- Independence: cleanroom implementation, no author or organization in common
  with the `varwof` implementations; the author states that no reference
  implementation was read, and the repository's cleanroom leash, the pinned
  upstream corpora and a history predating the reference runner's crosswalk
  output support that statement.
- Bootstrap: the author recuses as author of the implementation, and no other
  appointed reviewer covers CLC-D, so the editor recorded it. The mark stands
  until a different appointed reviewer re-checks the claim.
- Residual gaps: this row claims the CLC-D base corpora only. Not claimed or not
  run: the profile corpora (containment crosswalk 47, authorize crosswalk 1,
  reason-collapse 3, mode lattice 5, containment property 784), the §13.8.1
  carrier mapping, and CLC-E.
- Corpus errata recorded against the next corpus revision, deferred so this
  row's pins stay valid: `ac-012` asserts `"reason": ""` where `ac-011` uses
  `null`; the chain corpus tags vectors `clc_revision` `CLC-1.13` (13) or
  `CLC-1.14` (2), and the containment corpus carries no revision tag, while the
  claim is CLC-1.19.

## Baseline (not a claim)

The reference implementation is listed for context. It is not independent
evidence: it shares an author with the specification, so it is a regression
baseline, not third-party validation.

| Implementation | Class | Revision | Impl. commit | Corpus commit | Evidence |
|---|---|---|---|---|---|
| `varwof/register` (Go) | CLC-A + CLC-D | CLC-1.19 | `145252c` | `1f3cbdf` | public CI: <https://github.com/varwof/register/actions/workflows/clc-conformance.yml> |

Corpus hashes used by the baseline:

- `clc-v1/vectors.json` `3c1a5672…`
- `clc-v1/property-cases.json` `f00ed1f4…`
- `clc-d/containment-vectors.json`
  `3d03e5318f1e0cef07bd6cb38111cf6b7fbcc24aa13bd83fb7728ee1d4527b13`
- `clc-d/authorize-chain-vectors.json`
  `1ae22422c4c8632fa2d391473f1a9a244845d079baf381875134597409fcfa12`

## Superseded or withdrawn

None.
