# 10 · Decisions and Satisfaction

> **Normative source:** [`capability-language-core-v1.md`](../capability-language-core-v1.md) §9 (9.1 reason ordering), §10, Appendix A
> This page is a readable guide. In case of conflict, the normative specification wins.
> Status: Preview — not for production use.

## TL;DR

`Authorize(grants, operation) → Decision` is a three-valued verdict: `allow` / `deny` / `allow_unresolved`. `Satisfy(evidence_set, requirement)` (§10) is the evidence-side binary report: `SATISFIED` / `UNSATISFIED`. Both are deterministic, fail-closed, and carry stable reason codes. Appendix A shows how consumers bind this shared vocabulary.

## 1. `Authorize` — the authorization side (§9)

```
Decision = { verdict: "allow"|"deny"|"allow_unresolved",
             reason: string|null,
             unresolved: string[] }   // additive, §8.4
```

Algorithm (mirrors §9.1's layer order for what follows, **not** the precedence):

| Step | Check | Resolves to |
|------|-------|-------------|
| 0. **Pre-check** | Absent or empty grant set → `capability_not_authorized` (§9.1 layer 10), **before** any operation check, even when the operation is absent too | [`decide-016`](../../data/_vectors/clc-v1/vectors.json): `{}` grants + `{}` op → `capability_not_authorized`, not `missing_capability_id` |
| 1. **Operation validation** | Missing/invalid id — the **specific layer-1 code** is reported, never collapsed | `missing_capability_id` [`decide-017`](../../data/_vectors/clc-v1/vectors.json); `unsupported_wildcard` [`decide-018`](../../data/_vectors/clc-v1/vectors.json); `invalid_capability_id` [`decide-025`](../../data/_vectors/clc-v1/vectors.json) |
| 2. **Find covering grants** | Via `Entails` (§6.1); none covering → `capability_not_authorized` (§9.1 layer 10) | [`decide-002`](../../data/_vectors/clc-v1/vectors.json) |
| 3. **Evaluate constraints** | Per covering grant, §8.1 | `unknown_constraint` / `invalid_constraint` / `{type}:violated` / residual (§8.4) |
| 4. **Aggregate** (multi-grant, §9.1) | Any-one-covers-and-allows → allow; residual union across covering grants that allow; all reject → first covering grant in canonical order (§9.1), deterministic | [`decide-029`](../../data/_vectors/clc-v1/vectors.json), [`decide-030`](../../data/_vectors/clc-v1/vectors.json), [`decide-035`](../../data/_vectors/clc-v1/vectors.json) |
| 5. **Verdict** | allow with non-empty residual → `allow_unresolved`; allow with empty → `allow` | [`decide-020`](../../data/_vectors/clc-v1/vectors.json) |

The pre-check is the one precedence rule: an absent-or-empty grant set denies with `capability_not_authorized` (layer 10) — a caller that passes neither input gets that reason, not `missing_capability_id`. An absent operation resolves to `missing_capability_id` (layer 1). A language revision mismatch (§12.1) resolves before every layer with `unsupported_language_revision`.

## 2. Multi-grant aggregation (§9.1)

`Authorize` operates on an **ordered list of grants**; authorization outcome is order-independent, only reason selection uses input order:

1. **Any one covering-and-allowing grant allows** (a narrow grant must never deny the legal operation of a broad grant) — [`decide-029`](../../data/_vectors/clc-v1/vectors.json).
2. Residual obligations = `unresolved` **union across the covering grants that also allow** (normalized + sorted). A covering grant rejected at params/constraint layer contributes none — it does not authorize, so its residuals are not carried ([`decide-035`](../../data/_vectors/clc-v1/vectors.json): two grants, network + time, both allow → union carried as `allow_unresolved`).
3. No grant covers → `capability_not_authorized`; op layer-1 errors always precede any coverage/aggregation.
4. All covering grants reject at params/constraint → deny, reason = the layer 5–11 rejection of the **first covering grant in canonical order** (input list order; MUST NOT be chosen by hash/iteration order) — [`decide-030`](../../data/_vectors/clc-v1/vectors.json).

**Op-ID validation errors propagate their specific layer-1 code** (`missing_capability_id` / `unsupported_wildcard` / `invalid_capability_id`), never a catch-all and never `capability_not_authorized`; only **coverage** failures (layers 3–4 and 10) collapse to `capability_not_authorized`. A malformed id **in a grant** makes that grant non-matching: `Entails` reports its layer-1 code as false reason, but `Authorize` folds the non-match into coverage (`capability_not_authorized`) — the grant's own code is not surfaced.

## 3. `Resolved Reason Ordering` (§9.1, normative)

The single reported reason is the **first applicable layer** in this fixed order (applies to `Entails`, `Intersect`, `Authorize`):

| # | Layer | Reason code(s) |
|---|-------|----------------|
| 1 | CapabilityId validity | `invalid_capability_id`, `missing_capability_id`, `unsupported_wildcard` |
| 2 | Params normalization | `invalid_params_duplicate_key`, `invalid_params_number`, `invalid_params_size`, `invalid_params_binding` |
| 3 | Namespace (scheme + action Class) | `different_namespace` |
| 4 | Path coverage (same namespace) | `literal_mismatch`, `wildcard_requires_trailing_segment` |
| 5 | Explicit empty bound | `empty_bound_denies_class` |
| 6 | Null values | `invalid_params_null` |
| 7 | Param presence (both directions) | `params_missing`, `undeclared_param` |
| 8 | Enum membership and cardinality | `not_in_enum`, `params_cardinality` |
| 9 | Bound comparison | `params_exceed_grant`, `params_out_of_range`, `params_not_multiple` |
| 10 | Coverage emptiness | `no_overlap`, `absent_source`, `capability_not_authorized` |
| 11 | Constraint evaluation | `unknown_constraint`, `invalid_constraint`, `{type}:violated` |

`Resolve` (§8.5) is **post-decision, not a layer**: it consumes a `Decision`, never re-runs `Authorize`; only `invalid_resolution` / `invalid_timestamp` and a discharged `{type}:violated` are introduced by it, on `allow_unresolved` input only.

## 4. `Satisfy` — the evidence side (§10)

```
Satisfy(evidence_set, requirement) → Satisfaction
Satisfaction = { verdict: "SATISFIED"|"UNSATISFIED", reason: string|null }
```

Algorithm: **(1)** verify each evidence artifact under its native rules; **(2)** each required evidence role filled; **(3)** each artifact bound to the exact action via `Match` (§6.4); **(4)** evaluate freshness, consumption, and role constraints (§8.2 evidence-side grammar: `varwof/evidence-v1:freshness:sec:<n>`). A recognized constraint whose evaluation belongs to the enforcement point (consumption) evaluates to `unknown`, which at top level yields `UNSATISFIED`; **(5)** all roles filled and bound → `SATISFIED`; **(6)** any unfilled / unbound / violated → `UNSATISFIED`.

**Tri-state evaluation, binary report.** A recognized evidence-side constraint is evaluated three-valued (`satisfied` / `violated` / `unknown`), but the report is binary: `unknown` at the top level **MUST produce `UNSATISFIED`**, never `SATISFIED`. The evidence side has **no `allow_unresolved`**; `unresolved` is authorization-only (§8.4, §11). Deterministic, fail-closed, stable reason codes (§10).

## 5. Consumption mapping (Appendix A)

Appendix A is **informative** — conformance to CLC-A does not depend on any consumer profile:

| Consumer | Grammar | Binding | Verdict |
|----------|---------|---------|---------|
| AIC-JWT DA | `capability[].id` | Entailment (§6.1) | Decision (§9) |
| EMILIA AEB | AEG capability_class | Match (§6.4) + Entailment (§6.1) | SATISFIED (§10) + Decision (§9) |
| RAR authorization_details | `type="capability"` (RFC 9396) | Entailment (§6.1) | Decision (§9) |
| Delegation chain | each hop's declared set | Intersection (§7) | Decision (§9) |
| Delegation containment | parent and child boundaries | `Contains` (§13) | Containment verdict (§13) |

The delegation-chain and containment rows are the two you should not conflate: intersection answers the chain's effective authority, containment answers each hop's `child ⊆ parent`; a hop that must stay inside its parent is checked with `Contains` (§13) — see [12-containment](12-containment.md).

## Prevent-mixup checklist

- [ ] Grant-side pre-check (layer 10) precedes operation validation (layer 1): absent grant + absent op → `capability_not_authorized`.
- [ ] Op-ID layer-1 codes propagate specifically; grant-side codes fold into `capability_not_authorized`.
- [ ] Multi-grant is any-one-covers: a narrow grant must not deny the broad grant's operation.
- [ ] Residual obligations are the union across covering-and-allowing grants only; rejected grants contribute none.
- [ ] `allow_unresolved` is never `allow`; `unknown` is internal, never a third top-level verdict on the evidence side.

## Common pitfalls

- **Testing only `verdict == "allow"`** — a residual obligation slips through as an unconfirmed allow (§8.4).
- **Expecting the evidence side to report `unknown`** — it reports a binary `UNSATISFIED` with a stable reason.

---
← [09-intersection.md](09-intersection.md) · → [11-reason-codes.md](11-reason-codes.md) · related: [08-constraints.md](08-constraints.md), [11-reason-codes.md](11-reason-codes.md)