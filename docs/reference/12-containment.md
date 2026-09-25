# 12 · Delegation containment (CLC-D)

> **Normative source:** [`capability-language-core-v1.md`](../capability-language-core-v1.md) §13 (13.1–13.8, 13.11, 13.12)
> This page is a readable guide. In case of conflict, the normative specification wins.
> Status: Preview — not for production use.

## TL;DR

Containment is the third grant-level relation, alongside Entailment (§6.1) and Intersection (§7): **`Contains(parent, child)`** answers "is the child's *declared* grant inside the parent's *declared* grant?" — the per-hop question a delegation chain asks. It is an **optional** conformance class **CLC-D**, stacked on CLC-A: additive, changes no CLC-A verdict, and can be adopted by any CLC-A implementation.

## 1. Why entailment and intersection are not enough (§13.1)

- **Entailment** answers "does a grant cover an operation?" — §6.1.
- **Intersection** answers "what is the effective set of several grants?" — §7.
- Neither answers the delegation question: **is the child's declared grant inside the parent's declared grant?** A result fitted to two grants proves nothing about one grant being a subset of a specific parent.

CLC-D serves the AIC ecosystem at two concrete boundaries: **delegation** (a sub-agent's requested capabilities must lie inside what the principal authorized) and **publication bound** (a rule a certificate holder publishes must not exceed the holder's own grant).

## 2. Relation signature and the fail-closed norm (§13.3)

```
Contains(GP: Grant, GC: Grant) -> ContainmentResult
ContainmentResult = { "contains": <boolean>, "reason": <string> }
```

- `contains = true` **only when every** layer of §13.4 passes; every layer fails closed — any doubt yields `false`.
- `reason` is empty on success; on failure it carries the **first failing layer's** code (§13.4 order, input order never influences which layer reports first).
- The relation is **antisymmetric on semantic equivalence classes**, not on Grant objects: `Contains(A,B) ∧ Contains(B,A)` holds exactly when A and B denote the same identifier coverage, param key set and bounds (surface spellings like `params:{}` ≡ absent identified). Two grants in distinct classes containing each other both ways is a contradiction and MUST NOT be reported ([`contain-040`/`contain-041`](../../data/_vectors/clc-d/containment-vectors.json): the antisymmetry probe pair).

## 3. The four layers (§13.4)

Resolved strictly in order; first failure determines the reason code.

| Layer | Checks | Reason on failure |
|-------|--------|-------------------|
| **1. Grant validity** (§13.4.1) | §3 identifier valid on both sides; child `params` matches the grant-side §6.2 grammar. An invalid *parent* also fails — a boundary that cannot be evaluated must not authorize a child | CLC-A syntax codes reused (`invalid_capability_id`, `missing_capability_id`, `invalid_params_<n>`) — [`contain-011`](../../data/_vectors/clc-d/containment-vectors.json): empty parent id |
| **2. Identifier coverage** (§13.4.2) | Exactly the CLC-v1 path-coverage relation (Entails' identifier rules, params excluded): same namespace; then equal literal depth OR parent trailing `*` covering child's trailing segments (`*` matches one or more, never zero). Mid-identifier wildcards stay `unsupported_wildcard` | `different_namespace` (namespace differs — [`contain-004`](../../data/_vectors/clc-d/containment-vectors.json)); `child_exceeds_parent` (coverage gap) |
| **3. Parameter narrowing** (§13.4.3) | Every child-declared param within parent's declared bounds (number ≤, string/boolean exact, array ⊆ enum, object recursion) **and identical key sets** (symmetric closure, union of `params` + `param_bounds` keys). `param_bounds` Bounds: child `min` raised-or-equal, `max` lowered-or-equal, `step` an integer multiple, enum ⊆ subset, nested recursion; required parent key forces required child key. Parent `{}` (or absent) is unconstrained and contains any child; child `{}` under a *bounded* parent fails | `params_not_narrower` (any child value/key-set failure) — [`contain-041`](../../data/_vectors/clc-d/containment-vectors.json) |
| **4. Delegation-mode lattice** (§13.4.5) | **Binding-profile pre-check, NOT a relation layer**: Grant values carry no mode, `Contains` takes no mode argument. A mode-carrying carrier MUST run the lattice itself and report `delegation_mode_not_narrower` from the profile when the child widens the parent (AIC-JWT order: `authorized < representative`) | `delegation_mode_not_narrower` (profile-owned; never by `Contains`) |

**Constraints are outside the relation** (§13.4.4): `Contains` does not read, compare, or validate the `constraints` field — a constraint difference never changes the verdict. Constraints compose by **union** along the chain (§7, conjunctive), so a child need not re-declare its parent's constraints and adding one only narrows. A consumer using `Contains` as its *only* gate MUST compose the chain's intersections so the parent's constraints stay in force.

Deep example for layer 3: parent `{limit:100}`, child `{limit:50}` → contained ([`contain-040`](../../data/_vectors/clc-d/containment-vectors.json)); the reverse ([`contain-041`](../../data/_vectors/clc-d/containment-vectors.json)) → `params_not_narrower`. Note the declared-value reading: child `{limit:-5}` is *within* a parent `{limit:100}` upper bound (subset-only, no lower-bound semantics) — [`contain-042`](../../data/_vectors/clc-d/containment-vectors.json).

## 4. `AuthorizeWithChain` — the fused chain check (§13.11)

```
AuthorizeWithChain(chain, op) → Decision   // chain = ordered Grant[], root first
```

1. **Empty chain fails closed** → `deny("absent_source")` (§7 rule 5; [`ac-001`](../../data/_vectors/clc-d/authorize-chain-vectors.json)).
2. **Chain gate:** for each adjacent pair, `Contains(chain[i], chain[i+1])`; the first broken hop ends with that hop's §13.5 code (`child_exceeds_parent` / `params_not_narrower` — never `delegation_mode_not_narrower`). This runs **before op validation**: a broken chain is reported even when the operation is also absent ([`ac-007`](../../data/_vectors/clc-d/authorize-chain-vectors.json): broken hop + id-less op → `child_exceeds_parent`; [`ac-006`](../../data/_vectors/clc-d/authorize-chain-vectors.json): child widens `limit` → `params_not_narrower`).
3. **Effective chain grant** `G = Intersect(chain...)` — the step that brings every ancestor's params **and constraints** into force ([`ac-009`](../../data/_vectors/clc-d/authorize-chain-vectors.json): ancestor `max_rows:10`, leaf carries none, op asks 50 → `max_rows:violated` via the union axis; [`ac-015`](../../data/_vectors/clc-d/authorize-chain-vectors.json): `param_bounds` meet keeps the ancestor `max:50`, op 75 → `params_out_of_range`).
4. **Return `Authorize(G, op)`** unchanged.

**Caller obligation:** the caller MUST supply the complete, authenticated, root-first chain. The function fetches no missing link, verifies no signature, detects no truncation or reordering — a verdict is about the *presented sequence* (authentication is the carrier's concern, §11). The two-grant form `AuthorizeWithChain(parent, child, op)` is the degenerate case.

## 5. CLC-D conformance and profile contract (§13.6, §13.8.1)

A CLC-D implementation MUST implement `Contains` with its ordered layers, the relation's two §13.5 codes (`child_exceeds_parent`, `params_not_narrower`), the profile contract, `AuthorizeWithChain` (rev CLC-1.13) with its corpus, and MUST pass `containment-vectors.json`. It MUST NOT alter any CLC-A verdict or code. Claiming CLC-A alone does **not** claim CLC-D; intersection MUST NOT be substituted for containment.

A **binding profile** maps a carrier's native structure to the grants `Contains` compares. Obligations (§13.8.1): (1) resolve the carrier's inheritance/defaults before mapping; (2) preserve identity dimensions (ATN `schema.digest` → trailing id segment, so a mismatch fails closed); (3) residualize dimensions the relation cannot see — never report containment as if they were checked; (4) do not invent carrier semantics (a bare AEGIS domain is not a namespace wildcard); (5) non-goals recorded: union of authority sources, chain-level verification, cross-carrier identity are all outside the relation.

## Prevent-mixup checklist

- [ ] `Contains` compares **identifier + parameters only**; constraints and modes stay out (union axis + profile pre-check).
- [ ] Layer order is strict; reason = first failing layer, never `delegation_mode_not_narrower`.
- [ ] Key sets must be **identical** (symmetric closure), not merely subsets.
- [ ] `AuthorizeWithChain` gate runs before op validation; the operation's own layer-1 errors only appear once the chain passes.
- [ ] `AuthorizeWithChain` = gate → `Intersect(chain...)` → `Authorize` — the intersection is what keeps ancestor constraints in force.

## Common pitfalls

- **Substituting intersection for containment** — intersection reasons about the combined set; containment is the per-child, per-parent admission predicate.
- **Letting a child drop a parent constraint** — needs the chain's `Intersect` union, never containment alone.
- **Caching an `allow` past a Resolve horizon** — see [08-constraints](08-constraints.md) §4; containment and `allow_unresolved` are orthogonal, and `allow_unresolved` MUST NOT be read as a containment result.
- **(excluded) §13.9 Related Work / §13.10 Open Issues** — informative / resolved-record only; see `README.md` coverage map.

---
← [11-reason-codes.md](11-reason-codes.md) · → [13-conformance.md](13-conformance.md) · related: [09-intersection.md](09-intersection.md), [13-conformance.md](13-conformance.md)