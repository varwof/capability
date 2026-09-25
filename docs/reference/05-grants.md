# 05 · Grants — the authorization unit

> **Normative source:** [`capability-language-core-v1.md`](../capability-language-core-v1.md) §5 (Grant)
> This page is a readable guide. In case of conflict, the normative specification wins.
> Status: Preview — not for production use.

## TL;DR

A **grant** is the smallest unit of authorization: `CapabilityId` + optional `params` + optional `constraints`. It reads *"the holder may use this class of action, within these bounds and constraints."* All evidence of permission flows through grants — a decision is about one or more grants and one operation.

## The shape

```
grant      = capability-id [ params ] [ constraints ]
constraint = scheme ":" type [ ":" params ]
```

Concretely (the same JSON you see at the decision edge):

```json
{
  "id": "std/database-v1:query:SELECT",
  "params": { "limit": 100, "tables": ["customers"] },
  "constraints": [ "varwof/constraint-v1:time:window:[{\"start\":\"09:00\",\"end\":\"17:00\"}]" ]
}
```

Three fields, three concerns:

| Field | Role | Governed by |
|-------|------|-------------|
| `id` | the class of action | §3 identifiers, §6.1 entailment |
| `params` | value bounds on the request's parameters (upper-bound numbers, enum arrays, recursive objects) | §6.2 |
| `param_bounds` | optional *extended* bounds: min/max/step, enum cardinality, nested, `optional` — always a **separate** field, never mixed into `params` | §6.5 |
| `constraints` | governing limits a consumer must honor (time, network, `max_rows`) | §8 |

`param_bounds` is listed here because it is a grant-level field introduced by §6.5; the value algebra it shares with `params` is covered in [07-parameters.md](07-parameters.md).

## Deny-when-declared

A declared constraint is **not** a wish — it is a denial when it is violated, and an obligation when it cannot be evaluated:

- **Empty bound denies the class.** A grant whose `params` declare an empty array (`{"tables":[]}`) denies the entire class, so the holder can never act — this is fail-closed by construction ([`params-007`](../../data/_vectors/clc-v1/vectors.json) → `deny` `empty_bound_denies_class`).
- **Omitted bound uses the scheme default.** A constraint for which a capability scheme declares a default value takes that default on the grant's parse (§6.3 scheme defaults).
- **Non-compliant constraints fail at layer 1.** Unrecognized schemes/types and grammar-violating values are rejected before entailment runs — `unknown_constraint` ([`decide-003`](../../data/_vectors/clc-v1/vectors.json) `unknown:constraint:type`) and `invalid_constraint` ([`decide-019`](../../data/_vectors/clc-v1/vectors.json) cross-midnight single-segment window; [`decide-021`](../../data/_vectors/clc-v1/vectors.json) pre-v1.2 scalar-second window) never reach §6.1.

## Grants in combination

The decision function is *never* about one grant in isolation:

- **Within one identifier**, several grants may cover the same request — the engine must handle **multi-grant** input (`decide-035`).
- **Across identifiers**, a grant may be combined with constraints on another grant; intersection ([09-intersection.md](09-intersection.md)) and containment ([12-containment.md](12-containment.md)) both treat the grant as the atomic declared unit and never widen a source.

The cardinal rule inherited from P6/P11: **authorization is granted where the engine can prove it — everywhere else it closes the door.** Empty grants, unknown constraints and missing fields deny; they never silently expand.

## Common pitfalls

- **Reading a bounded grant as "allow with parameters".** `params` and `param_bounds` narrow the grant; they never add actions or widen a previous grant.
- **Expecting `constraints` to be evaluated by the CLC core.** The core evaluates `max_rows`; `time`/`network` surface as obligations (`allow_unresolved` + `unresolved`). Borderline values you can't evaluate MUST deny.
- **Omitting the `id`.** A grant without an identifier is not a grant at all — `missing_capability_id` fires at layer 1.

---
← [04-actions.md](04-actions.md) · → [06-entailment.md](06-entailment.md) · related: [07-parameters.md](07-parameters.md), [08-constraints.md](08-constraints.md)