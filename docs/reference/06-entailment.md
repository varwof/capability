# 06 · Entailment — the authorization binding

> **Normative source:** [`capability-language-core-v1.md`](../capability-language-core-v1.md) §6.1 (Entailment), §6.3 (Algorithm), §6.4 (Match)
> This page is a readable guide. In case of conflict, the normative specification wins.
> Status: Preview — not for production use.

## TL;DR

Binding answers *"does this grant authorize this request?"* on the authorization side (**entailment**) and *"does this evidence correspond to this action?"* on the evidence side (**Match**). Entailment decides **class coverage**: grant G covers operation O if the identifier matches *and* every declared parameter/constraint holds. Match decides **content binding**: an ActionId equals the recomputed projection — with no occurrence claims and no native verification.

## §6.1 — Entailment, the two identifier rules

Grant G covers operation O when one of two things is true:

1. **Literal**: G = O, byte-for-byte after normalization.
2. **Trailing wildcard**: G = `scheme:prefix:*` and O has **at least one** trailing segment after `scheme:prefix:` — segment-boundary comparison, **not** lexical prefix.

| Grant | Operation | Result |
|-------|-----------|--------|
| `std/database-v1:query:*` | `std/database-v1:query:SELECT` | ✅ wildcard matches ([`entail-002`](../../data/_vectors/clc-v1/vectors.json)) |
| `std/database-v1:query:*` | `std/database-v1:query:SELECT:deep` | ✅ multi-segment ([`entail-003`](../../data/_vectors/clc-v1/vectors.json)) |
| `std/database-v1:query:*` | `std/database-v1:admin:DDL` | ❌ different namespace ([`entail-004`](../../data/_vectors/clc-v1/vectors.json)) |
| `std/database-v1:query:SELECT` | `std/database-v1:query:INSERT` | ❌ literal mismatch ([`entail-006`](../../data/_vectors/clc-v1/vectors.json)) |

Two shapes are **always refused** (§6.3 steps 1–2): a namespace mismatch (`different_namespace`, layer 3) and a wildcard with no trailing segment ([`entail-005`](../../data/_vectors/clc-v1/vectors.json), `wildcard_requires_trailing_segment`). The class-position wildcard (`std/database-v1:*`) is a grammar defect, not a superset — see [03-identifiers.md](03-identifiers.md) for the `different_namespace` pair `entail-007/-008`.

## §6.3 — The `Entails` algorithm

```
Entails(G, O) → bool:
  1. G.namespace ≠ O.namespace   → false   (namespace = scheme + action Class, §9.1 layer 3)
  2. G.id doesn't cover O.id     → false   (path coverage, §9.1 layer 4)
  3. G declares no key           → true    (no `params` and no `param_bounds` ⇒ unconstrained, absent ≡ empty object)
  4. O.params absent             → false   (bounded grant, request omits it → `params_missing`)
  5. params_subset(O.params, keys(params) ∪ keys(param_bounds), param_bounds)
                                  (declared key set, §9.1 layers 5–9)
```

Working through the rulebook:

- **Step 3 — unconstrained means all-params-welcome.** A grant with no `params` and no `param_bounds` (or with `"params":{}`) covers *any* operation params. Absent and `{}` are semantically identical (§6.2; §7 rule 6; §9.1).
- **Step 4 — bounded grants are fail-closed on omission.** If the grant narrows anything and the operation omits the whole `params` field, `deny("params_missing")` — one bound key missing reads the same as the whole object missing ([`decide-007`](../../data/_vectors/clc-v1/vectors.json)); the case of a bounded grant against an operation carrying undeclared keys is pinned by `undeclared-002`, resolved `params_missing` because the **missing-key check beats the undeclared-key check** within layer 7.
- **Step 5 — the declared key set.** Comparison runs over `keys(params) ∪ keys(param_bounds)`; a `param_bounds` key additionally enforces its Bound (inclusive `min`/`max`, `step`, enum cardinality, `optional`, `nested` — §6.5). Step 5 reduces to the `params`-only comparison when no `param_bounds` exist.

**When more than one check fails, the reported reason follows the fixed §9.1 ordering**, not the textual step order. The two orderings that surprise:

- **`params_missing` wins over `undeclared_param`** (§9.1 layer 7 internal order), as `undeclared-002` shows.
- **Layer 6 (`invalid_params_null`) resolves before presence.** A `null` param value fails with `invalid_params_null` *even when the operation omits the whole `params` field* — the null check shadows step 4's `params_missing` ([`decide-008`](../../data/_vectors/clc-v1/vectors.json) → `invalid_params_null`).

**Scheme defaults.** A capability scheme may declare `param_defaults`; per §6.5 the implementation MUST materialize them into `O` **before** step 4, with precedence **explicit operation value > scheme default > absent**. Apply a default only when it is needed to satisfy a grant-declared key; `optional:true` keys are never materialized (the marker wins over the default).

## §6.4 — Match (evidence binding)

Evidence E is bound to action A when:

1. E carries a valid ActionId in the language's projection form `clc-action:1:…` (§4.3);
2. E's ActionId **equals the recomputed** ActionId of the ObservedAction;
3. the ActionId was computed under the relying-party-pinned suite and definition source.

Match is **content correlation only** (see [04-actions.md](04-actions.md)): it does not validate a native artifact, does not authorize execution, and does not identify an occurrence. Cross-format mapping (E's native format ≠ A's canonical form) must be pinned as an Action-Mapping Profile, with results `EQUIVALENT_UNDER_PROFILE`, `NOT_EQUIVALENT`, or `INDETERMINATE`.

## Correlation quick-ref

| Binding | Side | Checks | Corpus examples |
|---------|------|--------|-----------------|
| **Entailment** | authorization | class coverage: identifier + params + constraints | `entail-001…008`, `params-001/002`, `decide-007/008` |
| **Match** | evidence | content identity: recomputed projection digest | evidence corpus (`evidence-vectors.json`) |

## Common pitfalls

- **Reading layer ordering off the algorithm text.** §6.3's numbered steps are *presentation*; the authoritative outcome order is §9.1 (layers 1–9). When two checks fail, always prefer the fixed layer order over "the first step that failed."
- **Mistaking the declared key set for an ordered list.** Step 5 compares over the *set* `keys(params) ∪ keys(param_bounds)`; declaration order and field choice carry no semantic meaning for these checks.
- **Treating `allow_unresolved` as entailment's end.** Entailment may *succeed* while the decision is `allow_unresolved` because a constraint wasn't evaluated — that is §8.4's business, not entailment's.

---
← [05-grants.md](05-grants.md) · → [07-parameters.md](07-parameters.md) · related: [10-decisions.md](10-decisions.md), [11-reason-codes.md](11-reason-codes.md)