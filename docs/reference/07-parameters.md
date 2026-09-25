# 07 · Parameters, parameter bounds, and BoundMeet

> **Normative source:** [`capability-language-core-v1.md`](../capability-language-core-v1.md) §6.2 (Parameters), §6.5 (Extended parameter bounds), §6.6 (Intersection of bounds)
> This page is a readable guide. In case of conflict, the normative specification wins.
> Status: Preview — not for production use.

## TL;DR

Parameter constraints come from two **never-mixed fields**: `params` (the v1.1 value rules) and `param_bounds` (CLC-1.10: signed bounds, enum cardinality, nested, optional keys). Existing `params` inputs keep their meaning. The §6.6 bounds-meet has its own closed algebra, refusing anything unrepresentable in one value family.

## 1. `params`: the value rules (§6.2)

| Type | Rule | Example |
|------|------|---------|
| number | op ≤ grant (upper bound) | `50 ≤ 100` ✅ [`params-001`](../../data/_vectors/clc-v1/vectors.json); `150` ❌ `params-002` |
| string | exact | `"a"="a"` ✅ |
| boolean | exact only — never numeric (`true` ≠ `1`) | — |
| array | **set of allowed values** (enum): scalar equal to a member; array: every element a member | `{"station":[1,2,3]}` |
| object | every grant key in op, values recurse | `{"t":["id"]} ⊆ {"t":["id","name"]}` ✅ |

**Enum semantics of arrays — v1.1 rule.** An array-valued grant param is the **set** of allowed values, not an order or a range: categorical params (station, cell, tool id) SHOULD be arrays; a scalar number in `params` keeps upper-bound semantics. `["a"] ⊉ ["a","b"]` → `not_in_enum` ([`params-004`](../../data/_vectors/clc-v1/vectors.json)).

**Empty arrays / empty set.** `{"tables":[]}` denies the class — `empty_bound_denies_class` ([`params-007`](../../data/_vectors/clc-v1/vectors.json)). A grant with no `params`, or `"params":{}`, is **unconstrained** (covers any params).

**Null is invalid in v1** — `null` in grant or request params → `invalid_params_null` ([`params-008`](../../data/_vectors/clc-v1/vectors.json), [`decide-008`](../../data/_vectors/clc-v1/vectors.json)).

### Input normalization (rev CLC-1.1/1.4/1.8)

Before any §9.1 layer runs, `params` is normalized at the input boundary, checks in fixed order: **(1)** JCS canonical serialization (RFC 8785: sorted keys, ECMAScript-`Number::toString` numbers); **(2)** duplicate JSON keys → `invalid_params_duplicate_key` ([`params-016`](../../data/_vectors/clc-v1/vectors.json)); **(3)** number shape — non-finite / out-of-IEEE-754-range / >17 significant digits → `invalid_params_number` ([`params-017`](../../data/_vectors/clc-v1/vectors.json) `1e400`), judged on the **raw token as received**; **(4)** size/depth — ≤ 512 **UTF-8 octets**, depth ≤ 32 (outermost = level 1) → `invalid_params_size` ([`params-018`/`params-020`](../../data/_vectors/clc-v1/vectors.json) both sides of the octet cap; [`params-033`](../../data/_vectors/clc-v1/vectors.json) the JCS-measured form); **(5)** first failing check wins, before layer 1; **(6)** decoded-value entries are capped via canonical serialization — both paths reject; **(7)** malformed Unicode (lone surrogate / invalid UTF-8 octet) has no JCS form → **refused `invalid_params_number` on the raw text**, before any decoding (a decoder collapse would make it unrecoverable).

## 2. `param_bounds`: extended bounds (§6.5)

`param_bounds` is a **separate optional grant field**, with one hard rule: **one authoritative representation per key** — a key MAY sit in `params` **or** in `param_bounds`, never both, or the grant is `invalid_params_binding` ([`pb-031`](../../data/_vectors/clc-v1/param-bounds-vectors.json): same key in both). The declared key set is `keys(params) ∪ keys(param_bounds)`.

### Bound grammar (closed)

```
Bound = {   // at most one value family + the orthogonal "optional"
  min/max, step             →  numeric
  enum, min_items/max_items →  enum
  nested                    →  nested
  optional                  →  orthogonal (default false)
}
```

Every member is optional, the object is **closed** (unknown members rejected), and families may not mix. `min > max`, `step ≤ 0`, `min_items > max_items` → `invalid_params_binding`. An **empty** Bound `{}` declares the key with no value constraint — it *still serves key closure* and is **required by default** ([`pb-038`](../../data/_vectors/clc-v1/param-bounds-vectors.json): empty bound, omitted request param → `params_missing`).

### The four "{}"—never collapse them

| Layer | Reading of `{}` |
|-------|----------------|
| Container presence | `params` absent ≡ `params:{}` → **unconstrained** |
| Declaration site | key in `params` **or** `param_bounds`, never both |
| Value constraint | `params:{"k":[]}` **is** a restriction; `param_bounds:{"k":{}}` **is not** (key closure only) |
| Request value | what `O` supplies, judged by the key's family |

### Entailment semantics per family (grant vs operation)

- **Presence (layer 7):** `optional:true` → MAY be absent; otherwise MUST be present (`params_missing`, [`pb-025`](../../data/_vectors/clc-v1/param-bounds-vectors.json)). A request key outside the declared set → `undeclared_param`.
- **Enum family (layer 8):** request value must be a member — scalar equal to a member, or array with every element a member ([`pb-015`](../../data/_vectors/clc-v1/param-bounds-vectors.json): `enum:["a","b"]` vs `["a","c"]` → `not_in_enum`). Membership equality is **JSON type-sensitive**: `true` ≠ `1` ≠ `"1"`; numbers compare after JCS canonicalization (`1` ≡ `1.0`). `min_items`/`max_items` bound the request cardinality (array length; scalar counts 1) → `params_cardinality` ([`pb-017`](../../data/_vectors/clc-v1/param-bounds-vectors.json): 3 > 2).
- **Numeric family (layer 9):** `min ≤ v ≤ max` (each bound inclusive) → `params_out_of_range` ([`pb-004`](../../data/_vectors/clc-v1/param-bounds-vectors.json): `limit:9` vs `min:10`). `step`: `q = v/step; q==floor(q) && q*step==v` (binary64) → `params_not_multiple` ([`pb-011`](../../data/_vectors/clc-v1/param-bounds-vectors.json): `1.3` with `step:0.5`). A numeric-family bound applied to a **non-number** request value → fail-closed `params_exceed_grant` ([`pb-037`](../../data/_vectors/clc-v1/param-bounds-vectors.json): `limit:"x"`).
- **Nested family:** recursion on an object-valued key with the same rules, symmetric key closure and optional at every depth. A `nested` bound applied to a **non-object** → fail-closed `params_exceed_grant` ([`pb-030`](../../data/_vectors/clc-v1/param-bounds-vectors.json): `columns:5`).
- **Scheme defaults (`param_defaults`):** materialize into `O` before step 4; precedence **explicit operation value > scheme default > absent** ([`pb-042`](../../data/_vectors/clc-v1/param-bounds-vectors.json): explicit `50` beats default `10` → `allow`). A default never adds an undeclared key; `optional:true` keys are never defaulted.

## 3. `BoundMeet` — intersecting bounds (§6.6, added CLC-1.14/revised 1.15)

`Intersect` combines each key declared in `param_bounds` by **two or more** sources, keeping the meet inside one family:

| Rule | Result |
|------|--------|
| `optional` | **AND across sources**: result optional only if *every* source marks it optional |
| numeric `min`/`max` | greatest min, least max (undeclared = unbounded); combined `min > max` → **empty meet** → `no_overlap` |
| numeric `step` | one an exact multiple of the other → the coarser; else `invalid_params_binding` — no undeclared grid synthesized |
| enum | member-set **intersection** (type-sensitive equality); empty → `no_overlap`; `min_items` = greatest, `max_items` = least; `max_items < min_items` → `no_overlap` ([`bm-010`,`bm-011`](../../data/_vectors/clc-v1/param-bounds-meet-vectors.json)) |
| nested | **identical key sets** required, else `no_overlap`; recurse per key |
| numeric ∩ enum (either order) | **refused** `invalid_params_binding` — CLC-1.14's "filter members" rule was removed (broader than either source); symmetric, decided before any math |
| scalar ∩ nested (either order) | **refused** `invalid_params_binding` (CLC-1.15: `no_overlap` → `invalid_params_binding`) |
| empty Bound `{}` | identity for value families; its `optional` still participates |

The result always carries **at most one** family, hence a valid §6.5 Bound; reason codes stay in the existing §9.2 set — `no_overlap` for empty meets *within one family*, `invalid_params_binding` for unrepresentable ones.

**Key site must agree across sources:** a key in `params` for one `Intersect` source, `param_bounds` for another → `invalid_params_binding` (a delegation chain cannot hit this — §13.4.3 requires matching sites every hop).

## Prevent-mixup checklist (the two revisions' incrementals)

- [ ] `params` value algebra for a scalar number is **upper-bound only** — no lower bound, step, cardinality, or optional marker inside `params`.
- [ ] min/max/step/enum/min_items/max_items/nested/optional, live **only** in `param_bounds`.
- [ ] The CLC-1.14 enum-filtering meet is **gone**: numeric × enum is `invalid_params_binding`, never a filtered enum; `no_overlap` stays reserved for empty meets *within one family* (incl. scalar∩nested → `invalid_params_binding`).
- [ ] Membership equality is **JSON type-sensitive** everywhere (enum `params`, §6.5 enum, §6.6 enum, §13.4.3 narrowing); a host-language `true==1` comparison is a conformance bug.

## Common pitfalls

- **Declaring a key in both `params` and `param_bounds`** — `invalid_params_binding`, not a "merger".
- **Reading `param_bounds: {k: {}}` as "unconstrained for k"** — it *declares* k (required, key-closed) but constrains no value; opposite of `params`, where `[]` is the sharpest restriction; and `params:{}` ≡ absent ≠ an empty `param_bounds` Bound.

---
← [06-entailment.md](06-entailment.md) · → [08-constraints.md](08-constraints.md) · related: [09-intersection.md](09-intersection.md), [11-reason-codes.md](11-reason-codes.md)