# 01 · Quickstart — your first authorization decision in four steps

> **Normative source:** [`capability-language-core-v1.md`](../capability-language-core-v1.md) §5 (Grant), §6 (Binding), §9 (Decision Function)
> This page is a readable guide. In case of conflict, the normative specification wins.
> Status: Preview — not for production use.

## TL;DR

CLC-v1 answers one question: **is this request inside what I granted?** You write a **grant** (what an agent may do), you are given a **request** (what the agent wants to do), and the language returns a verdict: `allow`, `deny`, or `allow_unresolved` — always with a stable reason code. Everything below is documentation-only: no install, no runtime, the examples are real corpus vectors you can re-run later with any conformance runner.

## The mental model

A `grant` and a `request` share the same shape: a **capability identifier** (`id`) plus optional **params**, **param_bounds** and **constraints**. The decision function checks, in order: are the identifiers compatible? are the params inside the grant's bounds? are the grant's constraints satisfied?

```
grant   { id, params?, param_bounds?, constraints? }
request { id, params? }          ← an Operation
                 ↓
        verdict + reason   (allow / deny / allow_unresolved)
```

## Step 1 — the minimal closed loop (exact identifier)

The smallest possible case: the request identifier is **literally equal** to the grant identifier.

**Input** — [`vectors.json → entail-001`](../../data/_vectors/clc-v1/vectors.json)

```json
grant   = { "id": "std/database-v1:query:SELECT" }
request = { "id": "std/database-v1:query:SELECT" }
```

**Output**: `allow` (reason: *—*). **Derivation**: literal match (§6.1).

An identifier has the form `scheme:path:action`. Matching is hierarchical left-to-right, so a more specific request must still fall inside the grant — which brings us to wildcards.

## Step 2 — add a wildcard (grant a class of actions)

A trailing `*` matches **one or more** remaining segments.

**Input** — [`vectors.json → entail-002`](../../data/_vectors/clc-v1/vectors.json)

```json
grant   = { "id": "std/database-v1:query:*" }
request = { "id": "std/database-v1:query:SELECT" }
```

**Output**: `allow`. The grant covers any single action under `std/database-v1:query:`.

The wildcard has sharp edges — see the pitfalls below — and a `*` earlier in the path is a different animal entirely:

**Input** — [`vectors.json → entail-007`](../../data/_vectors/clc-v1/vectors.json)

```json
grant   = { "id": "std/database-v1:*" }
request = { "id": "std/database-v1:query:SELECT" }
```

**Output**: `deny` `different_namespace`. A `*` at *class* (product) position is **not** a trailing action wildcard (§5.1/§9.3 layer 3). Full rules live in [`03-identifiers.md`](03-identifiers.md).

## Step 3 — add params and bounds (narrow the grant)

A grant can carry `params` — exact values a request must respect — or `param_bounds`, which express ranges an array-based `params` cannot.

**params — numeric ceiling** — [`vectors.json → params-001`](../../data/_vectors/clc-v1/vectors.json)

```json
grant   = { "id": "std/database-v1:query:SELECT", "params": { "limit": 100 } }
request = { "id": "std/database-v1:query:SELECT", "params": { "limit": 50 } }
```

**Output**: `allow` (50 ≤ 100).

**param_bounds — inclusive range** — [`param-bounds-vectors.json → pb-001 / pb-004`](../../data/_vectors/clc-v1/param-bounds-vectors.json)

```json
grant   = { "id": "std/database-v1:query:SELECT",
            "param_bounds": { "limit": { "min": 10, "max": 100 } } }
request = { "id": "std/database-v1:query:SELECT", "params": { "limit": 50 } }
```

**Output**: `allow`. But with `"limit": 9` ([`pb-004`](../../data/_vectors/clc-v1/param-bounds-vectors.json)) the same grant answers **`deny` `params_out_of_range`**.

**An array param is a *set* (enum) — the request may only pick members.** — [`vectors.json → params-004`](../../data/_vectors/clc-v1/vectors.json)

```json
grant   = { "id": "std/database-v1:query:SELECT", "params": { "tables": ["a"] } }
request = { "id": "std/database-v1:query:SELECT", "params": { "tables": ["a", "b"] } }
```

**Output**: `deny` `not_in_enum` — `"b"` is not a member of the allowed set. Detail in [`07-parameters.md`](07-parameters.md).

## Step 4 — add constraints (governing limits) and meet the third verdict

Constraints are `(scheme,type):value` strings on the grant. The core evaluates `max_rows` directly; `network`/`time` are recognized but not evaluated by the core — they surface as obligations.

**evaluated constraint** — [`vectors.json → decide-006`](../../data/_vectors/clc-v1/vectors.json)

```json
grant = { "id": "std/database-v1:query:SELECT",
          "constraints": [ "varwof/constraint-v1:max_rows:10" ] }
request = { "id": "std/database-v1:query:SELECT", "params": { "max_rows": 50 } }
```

**Output**: `deny` `max_rows:violated`.

**recognized-but-unevaluated — the third verdict** — [`vectors.json → decide-035`](../../data/_vectors/clc-v1/vectors.json) (two covering grants, `multi`)

```json
grant-zero = { "id": "std/database-v1:query:SELECT",
               "constraints": [ "varwof/constraint-v1:network:cidr:[\"192.0.2.0/24\"]" ] }
grant-one  = { "id": "std/database-v1:query:SELECT",
               "constraints": [ "varwof/constraint-v1:time:window:[{\"start\":\"00:00\",\"end\":\"06:00\"}]" ] }
request    = { "id": "std/database-v1:query:SELECT" }
```

**Output**: `allow_unresolved` with

```json
"unresolved": [ "varwof/constraint-v1:network:cidr:[\"192.0.2.0/24\"]",
                "varwof/constraint-v1:time:window:[{\"start\":\"00:00\",\"end\":\"06:00\"}]" ]
```

`allow_unresolved` is **not** `allow`: the consumer must discharge each obligation itself or refuse (§8.4). See [`08-constraints.md`](08-constraints.md) and [`10-decisions.md`](10-decisions.md).

## What you built

| Step | Grant feature | Verdict seen | Real corpus id |
|------|---------------|--------------|----------------|
| 1 | literal identifier | allow | `entail-001` |
| 2 | trailing `*` wildcard / class-position `*` | allow / `different_namespace` | `entail-002` / `entail-007` |
| 3 | params ceiling, `param_bounds` range, enum set | allow / `params_out_of_range` / `not_in_enum` | `params-001`, `pb-001`/`pb-004`, `params-004` |
| 4 | evaluated + residual constraints | `max_rows:violated` / `allow_unresolved` | `decide-006` / `decide-035` |

## Common pitfalls

- **Trailing `*` matches one-or-more segments, not zero.** A grant `std/database-v1:query:*` does **not** cover the bare `std/database-v1:query` — that request has no trailing segment to match and denies `wildcard_requires_trailing_segment` ([`entail-005`](../../data/_vectors/clc-v1/vectors.json)).
- **`*` is only legal as an action wildcard.** Any other position makes the identifier a different class, not a wildcard superset (`different_namespace`).
- **An array in `params` is an enumeration, not a range.** The request must pick members of the set; a request `["a","b"]` against grant `["a"]` is `deny`, because the whole request set must be covered.
- **A **literal** mismatch** — grant `...:SELECT`, request `...:INSERT` — denies `literal_mismatch`, even though both are "a query action" ([`entail-006`](../../data/_vectors/clc-v1/vectors.json)).
- **`allow_unresolved` is not `allow`.** Consumers MUST NOT fold the third verdict into an allow decision.

---
← [README.md](README.md) · → [`02-overview.md`](02-overview.md) · related: [`03-identifiers.md`](03-identifiers.md), [`07-parameters.md`](07-parameters.md), [`08-constraints.md`](08-constraints.md)