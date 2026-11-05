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
| `reg-2026-002` | `varwof/register` (Go) | CLC-A core | CLC-1.19, Section 12 core corpus | `e422020b0e55` | `1ef567c` | 154/154; 1,184/1,184 | Jijie Wei (editor, bootstrap) | bootstrap review; not independent | 2026-10-31 | verified |
| `reg-2026-003` | `jdieselny/ecr-wg` → `rust/clc-rust-cleanroom` | CLC-D | CLC-1.19, §13.4 and §13.11 base corpora | `3c1a97e` | `80e483f` | 79/79 (64 containment + 15 authorize-chain) | Jijie Wei (editor, bootstrap) | bootstrap review; no appointed scope | 2026-11-03 | verified |
| `reg-2026-004` | `jdieselny/ecr-wg` → `rust/clc-rust-cleanroom` | CLC-A core | CLC-1.19, Section 12 core corpus and the §12.1 minor gate | `3c1a97e` | `80e483f` | 154/154; 1,184/1,184; 669/669; 50/50 optional | Jijie Wei (editor, bootstrap) | bootstrap review; no appointed scope | 2026-11-05 | verified |

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
- Revision fields, recorded because the review first misread them: the
  containment corpus declares each vector's revision through `ext_revision`,
  a field retained from the retired EXT-00 draft and documented in
  `containment-vectors.schema.json` as not short-circuiting (the §12.1 language
  revision gate applies to CLC-A inputs; CLC-D is declared per implementation);
  the chain corpus declares `CLC-1.13` (13) or `CLC-1.14` (2). Older tags are
  the revision each vector was written under, not a defect and not a statement
  that the corpus is at that revision. The claim rests on the corpus hash.
- Erratum recorded against the next corpus revision, deferred so this row's pins
  stay valid: `ac-012` asserts `"reason": ""`, while `ac-011` writes `null` for
  the same absence and `containment-vectors.schema.json` documents `null` or
  omission as "not asserted". No other vector in either base corpus asserts an
  empty-string reason.
- Subsequent run, not a claim: `--clc-d-profile` at `ee20e0f`, public run
  <https://github.com/jdieselny/ecr-wg/actions/runs/41919095046>, passes
  `containment-property-cases.json` 784/784 and `reason-collapse-vectors.json`
  2 of 3. The third, `rc-003` (`delegation_mode_not_narrower`, recorded as a
  binding-profile pre-check), is not applicable to an engine that carries no
  binding profile, and is reported as a gap in the engine rather than a defect
  in the vector. Of the 784 property cases, 120 make the forward-closure
  implication reachable and exercise 588 operation-level witnesses, 26 at the
  deepest pair. No profile claim is recorded: the base CLC-D claim is
  unchanged.

### `reg-2026-004` — notes

- Report: `varwof/capability#14`, the CLC-A paragraph, on the author's option to
  cite the issue rather than file a separate report.
- Public CI: <https://github.com/jdieselny/ecr-wg/actions/runs/41191306714>
  (success at `3c1a97e`). The counts below are read from that run's log, which
  prints the minor-gate suite table and `REQUIRED 669 669 0`.
- Corpus hashes at `80e483f`:
  - `data/_vectors/clc-v1/vectors.json`
    `3c1a5672d6f107444903f06c51a71ce92451f1b45ca92c5a84a345b0de5a5bbd`
  - `data/_vectors/clc-v1/property-cases.json`
    `f00ed1f49299293ac9fff1e10287b9642aa49d6dacf25b2b4a1be2d7103b2f07`
  - `data/_vectors/clc-v1/param-bounds-vectors.json`
    `f37ad8dfa21c36b9ddc40961a844856cf674130355fe3d1fd3097789e7b9f82e`
  - `data/_vectors/clc-v1/param-bounds-equality-vectors.json`
    `ffdcc3153890125c1bfe0edf3e5d5733155050a7f5696497d3fb2f117af64ec3`
  - `data/_vectors/clc-v1/param-bounds-meet-vectors.json`
    `26faff835c2e3f5c6793e7f03375b8dd572b65262a1016682991374a7c848680`
  - `data/_vectors/clc-v1/param-bounds-meet-property-cases.json`
    `c102f75ba0791be3220ecfaf35c6439b4f791e0d32fa161eeb80a1b6ce5e2e50`
  - `data/_vectors/clc-v1/resolve-vectors.json`
    `1f9217f6f6257ccd599a2b650c811bf6f92f302ad5e44019bfd8fdf5e7293498`
  - `data/_vectors/clc-v1/constraint-union-vectors.json`
    `3fa1224f94a0357e03fbd66ce414654601bf53f5b23eae493e38a6de7a87e98b`
  - `data/_vectors/clc-v1/constraint-union-collation-vectors.json`
    `1395e4298e7aa2f7321a1a529dd7dfecaa5c2bd916eb2e69d60c6213c2eb5d91`
  - `data/_vectors/clc-v1/scheme-declaration-vectors.json`
    `382007d2c8b9af8d4acddfa2d336575a485c8ad104859aa20695ddf0a6acd98a`
  - `data/_vectors/clc-v1/quantity-vectors.json`
    `739f95be0735e7b917457e5f35f3c95e844dd4506e5d4757a001e72922242111`
  - `data/_vectors/clc-v1/string-domain-vectors.json`
    `15e977d06e73b9a956665ceafcd790536a754a10fb7785a954461707decf88f0`
  - `data/_vectors/clc-v1/symmetry-vectors.json`
    `a6ddd5e03220ad4ee3756432854f88ea1ed6e7219a6c6e57e929bbee7e7dec1d`
- The two core files are byte-identical at `1f3cbdf`, `1ef567c` (the corpus
  commit `reg-2026-002` cites) and `80e483f`, so the two rows cite the same
  bytes from different commits.
- Commands: `cargo test`; `cargo run --release -- --vector
  vectors/clc-a-core-vectors.json`; `cargo run --release -- --properties
  vectors/property-cases.json`; `cargo run --release -- --clc-v1` (minor gate);
  `python3 scripts/verify_vector_pins.py`.
- The core corpus defines `clc_revision` as the revision a vector's inputs
  declare (README), and `vectors.schema.json` requires a revision outside the
  implementation's compatible range to resolve to
  `deny/unsupported_language_revision`. That is why the tags run from
  `CLC-1.0` to `CLC-1.17` and one vector, `revision-002`, declares `CLC-2.0`.
  The claim rests on the corpus hash, not on a per-vector tag.
- Minor-gate composition, from the run log: `param-bounds` 49,
  `param-bounds-equality` 11, `param-bounds-meet` 27,
  `param-bounds-meet-property` 500, `resolve` 27, `constraint-union` 12,
  `constraint-union-collation` 2, `scheme-declaration` 9, `quantity` 8,
  `string-domain` 24 — 669 required; `symmetry` 50 optional.
- Independence: cleanroom implementation, no author or organization in common
  with the `varwof` implementations; the author states that no reference
  implementation was read, and the cleanroom leash, the hash-pinned corpora and
  a history predating the reference runner's crosswalk output support it.
- Bootstrap: the author recuses as author of the implementation, and no other
  appointed reviewer covers CLC-A core, so the editor recorded it. The mark
  stands until a different appointed reviewer re-checks the claim.
- Supersedes `reg-2026-001`, which recorded the core corpus alone and listed the
  minor-gate corpora as a gap.
- Residual gaps: this row claims CLC-A only. The CLC-D base corpora are recorded
  in `reg-2026-003`; the CLC-D profile corpora and CLC-E are not claimed.

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

A superseded claim gets a new row and the old one is recorded here, not deleted.

| ID | Status | Superseded by | Note |
|---|---|---|---|
| reg-2026-001 | superseded | `reg-2026-004` | core corpus alone; the minor gate is included in the replacement row |

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

