# 09 · Intersection and the `ConstraintUnion` projection

> **Normative source:** [`capability-language-core-v1.md`](../capability-language-core-v1.md) §7 (7.1 `ConstraintUnion`)
> This page is a readable guide. In case of conflict, the normative specification wins.
> Status: Preview — not for production use.

## TL;DR

`Intersect` composes delegation sources: `P_effective = P_principal ∩ C_agent ∩ P_gateway`. It **only narrows** — the result is covered by every source, order-independent, and denies with a stable reason code when sources cannot meet. `ConstraintUnion` (§7.1) is a separate projection: the chain's *whole constraint burden*, without computing an effective grant.

## 1. The meet over authorization sets (§7)

An "intersection over JSON values" is the wrong picture. Each param value **denotes an authorization set** — a number `(-∞, v]`, an array a membership set, a string/boolean `{v}`, an object a product of its keys' denotations — and the meet is set intersection on that denotation:

- `{"limit":100} ∩ {"limit":50} = {"limit":50}` — a tighter bound wins, i.e. a **minimum**, not an empty set ([`intersect-004`](../../data/_vectors/clc-v1/vectors.json)).
- `{"tables":["a","b"]} ∩ {"tables":["a"]} = {"tables":["a"]}` — allowlist intersection ([`intersect-001`](../../data/_vectors/clc-v1/vectors.json)).
- Two disjoint allowlists (`{"tables":["a"]}` vs `{"tables":["b"]}`) → `deny("no_overlap")`; **zero sources** → `deny("absent_source")` ([`intersect-007`](../../data/_vectors/clc-v1/vectors.json)).

A meet is empty (`no_overlap`) **only** when the denotations are genuinely disjoint — two enum sets with no common member, or divergent key sets. A numeric `params` meet is always a minimum (params has no lower bound).

## 2. The rules (§7)

| # | Rule | Pinned by |
|---|------|-----------|
| 1 | Each source provides a grant set | — |
| 2 | Effective grant MUST be covered by at least one grant from every source | [`intersect-010`](../../data/_vectors/clc-v1/vectors.json) |
| 3 | Same-capability constraints merged by **union** (each kept — constraints are conjunctive, dropping a source's constraint drops its restriction) | [`cu-008`](../../data/_vectors/clc-v1/constraint-union-vectors.json) (reversed hop order, same union) |
| 4 | Any source missing the capability → capability absent from the effective set | no dedicated vector; nearest pin [`combined-008`](../../data/_vectors/clc-v1/vectors.json) |
| 5 | **Zero / absent sources fail closed** → `deny("absent_source")` (a source that exists but carries no grant for the capability is rule 4, not 5) | [`intersect-007`](../../data/_vectors/clc-v1/vectors.json) |
| 6 | **Empty params declares no constraint**: a present-but-empty `params` contributes no restriction; bounded-then-empty and empty-then-bounded give the same result — source order MUST NOT change the outcome | [`intersect-008`](../../data/_vectors/clc-v1/vectors.json) `{limit:50} ∩ {} = {limit:50}` |

**Identifier comparison is params-free (rule 2).** The effective identifier is the **narrowest** one covered by every source, chosen by the §6.1 identifier rules alone — routing grants through `Entails` with params would make a bounded grant meet a params-less sibling and wrongly fail presence handling (§6.3 step 4) ([`intersect-010`](../../data/_vectors/clc-v1/vectors.json): `query:SELECT` ∩ `query:*` → `{}`, narrower identifier wins).

**Deny-when-declared interplays with rule 6:** an explicitly **empty `[]`/`{}` param value** denies the class — `{"tables":[]}` is a restriction, `params:{}` is not. A delegation chain whose intermediate hop declares an empty bound propagates `empty_bound_denies_class` ([`combined-011`](../../data/_vectors/clc-v1/vectors.json)), and a three-source intersection where one source is absent falls to `no_overlap` ([`combined-008`](../../data/_vectors/clc-v1/vectors.json)).

**Object values require identical key sets.** `{"a":1} ∩ {"b":1}` → `deny("no_overlap")` (merging "shared keys" would drop the keys the other source constrains, breaking composition-narrows-only); when key sets match, values recurse — `{"a":1} ∩ {"a":2} = {"a":1}`. Both are your reason to prefer uniform parameter shapes across delegation hops.

**`param_bounds` merges by the §6.6 meet**, not the §7 value rules: numeric `min`/`max`/`step`, enum member intersection and cardinality, `nested` recursion, `optional` by conjunction. An empty meet is `no_overlap`; an unrepresentable one (cross-family numeric × enum in either order, scalar × nested, incommensurable steps, or a key in `params` for one source and `param_bounds` for another) is `invalid_params_binding` (§7; [07-parameters](07-parameters.md) §3).

## 3. `ConstraintUnion` — the chain's whole constraint burden (§7.1)

```
ConstraintUnion(chain) → string[]        // chain = ordered Grant[]
```

Returns the **normalized union** of every constraint string in `chain` — duplicates folded, result deterministically ordered. It is a **projection, not a meet**: it does not compare identifiers or parameters, does not read or validate constraint values, does not check containment ([`cu-001`](../../data/_vectors/clc-v1/constraint-union-vectors.json) single grant: the union is its own set, normalized and sorted; [`cu-008`](../../data/_vectors/clc-v1/constraint-union-vectors.json) reversed hop order → same sorted union).

- **Empty chain fails closed** → `deny("absent_source")` ([`cu-007`](../../data/_vectors/clc-v1/constraint-union-vectors.json)) — a caller that lost the chain must not mistake "nothing to union" for "no constraints".
- **Ordering is UTF-8 byte order** (§7.1, rev CLC-1.15): the normalized strings compare octet by octet over their UTF-8 encodings — identical in every implementation; *not* UTF-16 code-unit order (which would place an emoji before U+E000–U+FFFF characters despite its higher code point). Pinned by [`constraint-union-collation-vectors.json`](../../data/_vectors/clc-v1/constraint-union-collation-vectors.json). This same collation governs the §8.4 `unresolved` list and the §8.5 `Resolve` output.
- JCS member order inside a serialized object and this list collation coexist: one governs object **members**, the other the constraint-string **list**; neither re-orders the other (§7.1).

`ConstraintUnion` asserts nothing about authority: per-hop `Contains` (§13) and `Authorize`/`Resolve` (§9, §8.5) remain separate steps. It is also why `Contains` stays pure — folding the union into it would stop the relation being a subset on the declared tuple.

## Prevent-mixup checklist

- [ ] Intersection is over **denotations**, not JSON values: numeric meet = minimum, not empty.
- [ ] `no_overlap` only when denotations are disjoint (enums / key sets); `absent_source` only for zero/absent sources.
- [ ] Empty `[]`/`{}` **value** = deny the class; `params:{}` = **no** restriction. Never conflate the two.
- [ ] Identifier comparison is params-free; never route `Intersect` through `Entails` with params.
- [ ] `param_bounds` meets go through the §6.6 algebra, not the §7 value rules (and cross-family → `invalid_params_binding`).
- [ ] `ConstraintUnion` sorts by **UTF-8 byte order**, folds duplicates, and fails closed on an empty chain.

## Common pitfalls

- **Reading an empty `Intersect` source as "no constraint"** — rule 4 treats a missing grant as absence of the capability; only a *present* empty `params` is no constraint.
- **Assuming `Intersect` validates constraint values** — it only merges constraint strings; the §8.1 value grammar is enforced at the decision boundary (§9), never here.

---
← [08-constraints.md](08-constraints.md) · → [10-decisions.md](10-decisions.md) · related: [06-entailment.md](06-entailment.md), [07-parameters.md](07-parameters.md)