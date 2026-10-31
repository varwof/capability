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
- Pinning gap: `clc-conformance.yml` should pin the corpus commit the way the
  reviewer's repository does, so a public run identifies its own corpus.
