# 11 · Reason codes — the cheat sheet

> **Normative source:** [`capability-language-core-v1.md`](../capability-language-core-v1.md) §9.2 (authorization), §13.5 (containment), Appendix C.2 (carrier mapping)
> This page is a readable guide. In case of conflict, the normative specification wins.
> Status: Preview — not for production use.

## TL;DR

Reason codes are **stable identifiers**: `canonical code = everything before the first ":"`. An implementation MAY append `: <detail>` (e.g. the offending parameter name) as a diagnostic suffix; the canonical code is unchanged. **All tooling and compatibility checks MUST compare the canonical prefix only** (§9.2). v1 codes are closed below; other schemes MAY define additional codes but MUST NOT redefine these.

## 1. Authorization codes by layer (§9.1/9.2)

Reason selection follows the §9.1 layer order (the *first applicable* layer wins; see [10-decisions](10-decisions.md) §3).

| Code | Meaning (§9.2) |
|------|----------------|
| **Layer 1 — CapabilityId validity** | |
| `unsupported_wildcard` | Wildcard shape forbidden in v1 (bare `*`, partial segment, `**`, `{a,b}`, `[a-z]`) |
| `invalid_capability_id` | CapabilityId does not conform to the §3 grammar |
| `missing_capability_id` | Operation has no `id` (layer 1) |
| **Layer 2 — Params normalization** | |
| `invalid_params_duplicate_key` | Duplicate JSON key (§6.2) |
| `invalid_params_number` | No canonical form: non-finite / out-of-range / over-precision (>17 significant decimal digits) number, or malformed-Unicode / unparseable text (§6.2 steps 3/7) |
| `invalid_params_size` | > 512-byte serialized size, or nesting deeper than depth 32 (§6.2) |
| `invalid_params_binding` | A `param_bounds` bound is malformed (unknown member, mixed families, `min > max`, `step ≤ 0`, `min_items > max_items`) or a key is in both `params` and `param_bounds` (§6.5) |
| **Layer 3–4 — Coverage** | |
| `different_namespace` | Grant and operation differ in namespace (scheme + action Class) |
| `literal_mismatch` | Literal identifiers differ |
| `wildcard_requires_trailing_segment` | Wildcard has no remaining segment (`...:*` does not cover `...`) |
| **Layer 5 — Deny-when-declared** | |
| `empty_bound_denies_class` | An explicitly empty bound at a param value (`[]`/`{}`) denies the class; `params:{}` is *not* an empty bound (≡ absent) |
| **Layer 6 — Null** | |
| `invalid_params_null` | `null` parameter value (rejected in v1) |
| **Layer 7 — Presence (both directions)** | |
| `params_missing` | Grant bounds a param the request omits, or the request has no `params` at all (fail-closed, §6.3 step 4) |
| `undeclared_param` | Operation param key not declared by the grant (key closure, §6.2) |
| **Layer 8–9 — Values** | |
| `not_in_enum` | Request value not a member of the granted array-as-set (§6.2) |
| `params_cardinality` | Request cardinality outside a `param_bounds` `min_items`/`max_items` (§6.5) |
| `params_out_of_range` | Request value outside a `param_bounds` `min`/`max` inclusive bound (§6.5) |
| `params_not_multiple` | Request value not an integer multiple of `step`, per the IEEE-754 rule (§6.5) |
| `params_exceed_grant` | Request parameters exceed the granted bound |
| **Layer 10 — Coverage emptiness** | |
| `capability_not_authorized` | No grant in the effective set covers the operation |
| `no_overlap` | Intersection of multiple sources is empty |
| `absent_source` | Intersection over zero sources — no effective set (§7 rule 5) |
| **Layer 11 — Constraints** | |
| `unknown_constraint` | Unknown constraint type (fail-closed) |
| `invalid_constraint` | Recognized type with a value failing its §8.1 value grammar |
| `{type}:violated` | A known constraint violated (e.g. `max_rows:violated`); also reported by `Resolve` for a discharged-as-violated obligation (§8.5) |
| **Cross-cutting** | |
| `unsupported_language_revision` | Declared CLC revision incompatible with the implementation (§12.1; fails closed, no downgrade) |
| `invalid_resolution` | A `Resolve` resolution entry is malformed (unknown `status`, non-string/empty `constraint`) (§8.5) |
| `invalid_timestamp` | The `Resolve` `now` argument is not a valid UTC instant (§8.5) |

**Re-use across functions.** `Resolve` (a `Decision` consumer, §8.5) introduces only `invalid_resolution` / `invalid_timestamp` and a discharged `{type}:violated`; the rest of the code set is §9.1's. The `no_overlap`/`absent_source`/`empty_bound_denies_class` codes are shared by `Intersect` (§7). `capability_not_authorized` is the one coverage collapse: only coverage failures (layers 3–4, 10) collapse to it; op-ID errors propagate their specific layer-1 code instead (§9.1).

## 2. Containment codes and CLC-D (§13.5)

`Contains(parent, child)` reports two stable codes; a third comes from the binding-profile pre-check:

| Code | Reported by | Meaning |
|------|-------------|---------|
| `child_exceeds_parent` | `Contains`, layer 2 (§13.4.2) | child identifier not covered by parent identifier |
| `params_not_narrower` | `Contains`, layer 3 (§13.4.3) | a child parameter is not within the parent's declared bounds / key set |
| `delegation_mode_not_narrower` | binding-profile pre-check (§13.4.5) — **never** by `Contains` | child delegation mode (a carrier concept) widens the parent's |

`Contains` is fail-closed by construction: every layer defaults to `false`; any layer that cannot validate is refused, no warning-then-allow (§13.4). An implementation MAY collapse `child_exceeds_parent` into `capability_not_authorized` where the boundary must not leak policy shape — never `params_not_narrower` (§13.5). A profile that adopts a mode-carrying carrier MUST NOT collapse `delegation_mode_not_narrower` either (§13.4.5).

## 3. Carrier failure-code mapping (Appendix C.2, informative)

Carrier failure codes collapse onto CLC-D's codes. The mapping is **many-to-one and not reversible** without the carrier recording its own code first:

| Carrier failure | CLC-D reason |
|-----------------|--------------|
| ATN different `id` · AAT tool outside parent set · AAE action-subset failure · AEGIS capability-the-delegator-lacks | `different_namespace`* |
| ATN `schema.digest` mismatch · AIP `aip_scope_insufficient` · AIP `aip_depth_exceeded` · AOA scope not strictly narrower | `child_exceeds_parent` |
| ATN raised `resource_bounds` · AAT constraint not subsumed · AIP `aip_budget_exceeded` · AAE constraint not more restrictive · AEGIS authority-exceeds-delegator's | `params_not_narrower` |

\* `different_namespace` is not in the §13.5 containment set; the C.2 table is a carrier-facing projection — see the spec appendix for the exact rows. Note the collapse visible in the sheet: both AIP scope and depth failures and an ATN digest mismatch reach `child_exceeds_parent`; every carrier's bound-widening reaches `params_not_narrower`. CLC-D guarantees the stable language-level reason, not the carrier's.

## Verify-a-reason checklist

- [ ] Compare the canonical prefix only (before the first `:`); `max_rows:violated:limit` is `max_rows:violated`.
- [ ] Match the layer: an op-ID failure is layer-1 specific (`unsupported_wildcard`, never `invalid_capability_id` or a catch-all).
- [ ] `capability_not_authorized` appears only for coverage failures; params/constraint rejections keep their own codes.
- [ ] `resolved reason` = first applicable §9.1 layer across the grant/operation pair.
- [ ] Deterministic same-input-same-reason across implementations (stable reason codes, §9.1/§12).

## Common pitfalls

- **Comparing the full string including `: <detail>`** — breaks stability; details are diagnostic only.
- **Reading `{type}:violated` as two codes** — the canonical code is everything before the first `:`, and `violated` *is* the consumed part.
- **Collapsing op-ID errors into `capability_not_authorized`** — op layer-1 codes propagate specifically; only coverage folds.

---
← [10-decisions.md](10-decisions.md) · → [12-containment.md](12-containment.md) · related: [09-intersection.md](09-intersection.md), [08-constraints.md](08-constraints.md)