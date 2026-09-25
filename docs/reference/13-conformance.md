# 13 · Conformance

> **Normative source:** [`capability-language-core-v1.md`](../capability-language-core-v1.md) §12 (12.1 Language Revision), Appendix B
> This page is a readable guide. In case of conflict, the normative specification wins.
> Status: Preview — not for production use.

## TL;DR

CLC-v1 defines **three conformance classes**. **CLC-A** (authorization side) is the baseline; **CLC-D** (delegation containment) is optional, stacked on CLC-A; **CLC-E** (evidence side) is **implemented and pinned by a corpus but NOT claimed**. The honesty rule: agreement between implementations that share an author is a regression test, not independent validation.

## 1. The three classes (§12)

| Class | What it includes | Status |
|-------|------------------|--------|
| **CLC-A** | §3 grammar, §6.1 entailment, §7 intersection, §9 decision, `unknown_constraint`/`invalid_constraint`, the `allow_unresolved` + additive `unresolved` channel (§8.4), multi-grant aggregation (§9.1), stable reason codes (§9.2); MUST pass `vectors.json` (120) and `property-cases.json` (1184) | **claimed — the v1 baseline** |
| **CLC-D** | `Contains(parent, child)` with its ordered layers, two stable relation codes (`child_exceeds_parent`, `params_not_narrower`), the profile contract (§13.8.1), `AuthorizeWithChain` (rev CLC-1.13); MUST pass `containment-vectors.json` (64) + `authorize-chain-vectors.json` (15). The third code `delegation_mode_not_narrower` belongs to the binding-profile pre-check, never `Contains` | **claimed** |
| **CLC-E** | §6.4 match, §10 satisfaction, the evidence-side constraint grammar, `evidence-vectors.json` (32) | **implemented, NOT claimed** |

**Why CLC-E is withheld** (§12): not for lack of material, but on **principle** — agreement is the bar, and the bar is two *independent* implementations (P12). Same-author parity does not meet it; and the evidence-side semantics are under joint review with EMILIA, so no claim is made ahead of that review. The obligations a future claim would carry are enumerated in §12 (verbatim there): three-valued evaluation where `unknown` is never read as satisfied; eligibility from integrity-protected native results only; `ActionId` as the digest of the declared material projection; a closed `CLC-REQUIREMENT-v1`; requirement from relying-party configuration; passing `evidence-vectors.json`.

An implementation that implements only CLC-A MUST NOT claim CLC-E.

## 2. Conformance corpora (§12, Appendix B)

CLC-A conformance is exercised by two machine-readable suites in `capability/data/_vectors/clc-v1/`:

- **`vectors.json`** — 120 vectors mapped to Appendix B (the machine-readable `kind` grouping differs from the appendix's semantic B.1–B.6 grouping; both counts are reproducible from the corpus): `kind=entail` (47), `kind=decide` (50), `kind=intersect` (14), `kind=syntax` (9).
- **`property-cases.json`** — 1184 cases pinning the §7 meet-law, identifier narrowing, and source-order independence.

CLC-D adds `capability/data/_vectors/clc-d/containment-vectors.json` (64), `containment-property-cases.json` (784 cases × 39 shared operations, forward-closure: `Contains(P,C) ∧ Entails(C,o) ⟹ Entails(P,o)`), `containment-crosswalk-vectors.json` (44), and `authorize-chain-vectors.json` (15). The evidence side ships `evidence-vectors.json` (32).

Additional generated/pinned corpora: `param-bounds-vectors.json` (43), `param-bounds-meet-vectors.json`, `constraint-union-vectors.json` (12), `constraint-union-collation-vectors.json` (2), `resolve-vectors.json` (26), `crosswalk-vectors.json` (13, both directions: AEB crossing members + five foreign representations incl. OAuth RAR, AIC-JWT DA, AEG, UCAN, delegation chain → CLC grants).

**Genericity is exercised, not asserted** (§12): a profile is a few lines of mapping written by the foreign-format owner; the core is not modified for any of them. Implementations MUST NOT redefine semantics, accept v1-forbidden wildcards, or broaden bounds during canonicalization.

## 3. Independence of implementations (honest scope, §12/§13.7)

The three implementations named in the repository README (Go, Python, TypeScript) are **not independent evidence**: they share an author, and their agreement is a regression test for the specification, not third-party validation. Until an independent implementation exists, the parity claim is scoped to **"same-author, three languages, one corpus"**. Reviewers SHOULD treat a single-author parity claim as evidence the text is *implementable*, not independently *interpreted*.

**Experimental neighbours are not CLC** (§12): the WIT/WPT interop study (`varwof/aic-jwt`) implements a wider wildcard surface (`**`, `{a,b}`, `[a-z]`) that this revision rejects as `unsupported_wildcard`; it is not CLC-A and MUST NOT be cited as one.

## 4. Language Revision (§12.1)

Every implementation declares a language revision `CLC-<major>.<minor>`; **this document declares `CLC-1.15`**. An input (grant, operation, OCM) SHOULD carry the revision it was authored against; **an input without one is treated as `CLC-1.0`**.

- **Compatible reading:** an implementation MAY evaluate an input whose declared major equals its own AND whose declared minor is ≤ its own (a CLC-1.3 implementation reads 1.0–1.3, not 1.4 or 2.0).
- **Incompatible reading MUST fail closed** → `deny("unsupported_language_revision")`, resolved **before any §9.1 layer**; no downgrade, no warning-then-allow ([`revision-002`](../../data/_vectors/clc-v1/vectors.json); the positive side is [`revision-001`](../../data/_vectors/clc-v1/vectors.json)).
- **CLC-A conformance and the minor gate are two sides of one rule** (§12.1): claiming CLC-A means implementing the semantics of the revision claimed — advertising `CLC-1.15` MUST implement `param_bounds` (grammar + §6.6 meet), `Resolve`, `ConstraintUnion`, and §6.2 canonicalization, not merely tolerate their inputs. An implementation that lags declares an older revision and refuses newer inputs through the gate; it MUST NOT claim a revision higher than it implements, nor claim CLC-A while refusing a well-formed input of its own declared revision.

**Revision-by-revision summary** (full texts in §12.1; each entry's verdict impact is stated there):

| Rev | Nature | Key addition / change |
|-----|--------|----------------------|
| 1.2 | additive | decision `unresolved` field + `invalid_constraint` |
| 1.3 | additive, one re-scope | `allow_unresolved` verdict value; `allow` = "fully enforced" |
| 1.9 | additive | containment + CLC-D (§13) |
| 1.10 | additive, minor gate | `param_bounds` + four reason codes |
| 1.11 | additive | `Resolve` (§8.5) + `invalid_resolution`/`invalid_timestamp` |
| 1.12 | additive | `ConstraintUnion` (§7.1) |
| 1.13 | additive, CLC-D-scoped | `AuthorizeWithChain` (§13.11) |
| 1.14 | additive | `BoundMeet` §6.6 (`param_bounds` intersection) |
| 1.15 | **corrective** | cross-family meet refuses `invalid_params_binding` (allow→deny on that sub-set); JSON type-sensitive enum `equal`; UTF-8 byte-order collations; `delegation_mode_not_narrower` re-attributed to the profile pre-check |

**Verdict-stability honesty** (§12.1): compatible reading governs *readability*, not verdict stability. On the §6.6 meet subset, CLC-1.10→1.14 moved `invalid_params_binding` → correct meet (deny→allow) and 1.15 moved the cross-family sub-case back to `invalid_params_binding` (allow→deny). Every input without `param_bounds` is verdict-stable across the 1.x range; a consumer MUST NOT assume stability on the `param_bounds`-meet subset.

## Summary: what a conformance review checks

- [ ] CLC-A: `vectors.json` (120) + `property-cases.json` (1184) pass; §8.4 `allow_unresolved`/`unresolved` not dropped.
- [ ] CLC-D: `containment-vectors.json` (64) + `authorize-chain-vectors.json` (15) pass; `Contains` stays declared-set-only.
- [ ] CLC-E: NOT claimed (independence bar unmet, EMILIA review pending).
- [ ] Minor gate: no silent downgrade; `unsupported_language_revision` before any layer on incompatible input.
- [ ] Honest scope: same-author parity is a regression test, not independent validation.

## Common pitfalls

- **Reading the 120/123 counts interchangeably** — Appendix B totals 120; the working-tree corpus currently holds 123 vectors (extra revision-pinned vectors) with the README lagging the live count.
- **Claiming CLC-E** — the corpus exists, but the class is withheld on principle (§12, P12).
- **Assuming verdict stability on `param_bounds`-meet inputs across minors** — explicitly not guaranteed (§12.1).

---
← [12-containment.md](12-containment.md) · → [14-cookbook.md](14-cookbook.md) · related: [02-overview.md](02-overview.md), [11-reason-codes.md](11-reason-codes.md)