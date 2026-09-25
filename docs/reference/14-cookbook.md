# 14 · Cookbook — scenario-driven recipes

> **Normative source:** the conformance corpora under [`capability-language-core-v1.md`](../capability-language-core-v1.md) (Appendix B and the pinned vector files)
> This page is a readable guide. In case of conflict, the normative specification wins.
> Status: Preview — not for production use.
> Every recipe is a distilled corpus scenario; the vector id is cited so you can replay it.

## TL;DR

A scenario-first summary of what the corpus pins: build the grant, write the operation, and reach the verdict the corpus asserts. Cross-reference the recipe's reason code with [11-reason-codes](11-reason-codes.md) and the targeted page for the fine print.

## 1. Authorizing a database query

**Grant:** `std/database-v1:query:SELECT` with `params: {"limit":100, "tables":["a","b"]}`.
**Operation:** `std/database-v1:query:SELECT` with `params: {"limit":50, "tables":["a"]}`.
**Verdict:** `allow` — params are within bounds and a subset ([`combined-001`](../../data/_vectors/clc-v1/vectors.json), wildcard variant; positive entailment in [`params-001`](../../data/_vectors/clc-v1/vectors.json)). Bump `limit` to 150 → `deny("params_exceed_grant")` ([`combined-002`](../../data/_vectors/clc-v1/vectors.json)); request `tables:["a","b","c"]` → `not_in_enum` ([`params-004`](../../data/_vectors/clc-v1/vectors.json)).

**Quick checks to remember:** a scalar grant number is an **upper bound**; a grant array is a **membership set** (06/07). Ask for `tables:[]` explicitly → `deny("empty_bound_denies_class")` is grant-side, not request-side.

## 2. Intersecting two sources

**Source A:** `std/database-v1:query:SELECT`, `params: {"limit":100}`. **Source B:** same id, `params: {"limit":50}`.
**Effective grant:** `{"limit":50}` — the tighter bound wins (a minimum, not emptiness; [09-intersection](09-intersection.md)) ([`intersect-004`](../../data/_vectors/clc-v1/vectors.json)). allowlists intersect to their common members ([`intersect-001`](../../data/_vectors/clc-v1/vectors.json)); disjoint allowlists → `deny("no_overlap")`.

**Delegation shape:** three sources where one carries no grant → `deny("no_overlap")` ([`combined-008`](../../data/_vectors/clc-v1/vectors.json)); **zero** sources → `deny("absent_source")` ([`intersect-007`](../../data/_vectors/clc-v1/vectors.json)); a delegation hop declaring `tables:[]` propagates `empty_bound_denies_class` ([`combined-011`](../../data/_vectors/clc-v1/vectors.json)).

## 3. Constraints and the residual channel

**Grant + constraint:** `std/database-v1:query:SELECT` with `constraints: ["varwof/constraint-v1:max_rows:100"]`; op params `{"max_rows":500}` → `deny("max_rows:violated")`; `{"max_rows":100}` → `allow` (violation is strict `>`; `decide-027`).

**Recognized-but-unevaluated:** grant with `network:cidr:["192.0.2.0/24"]` → `allow_unresolved` + `unresolved:[<constraint>]` ([`decide-020`](../../data/_vectors/clc-v1/vectors.json)); same for the split cross-midnight `time:window` ([`decide-024`](../../data/_vectors/clc-v1/vectors.json)). Two covering grants, one carrying `network:` and one `time:` → the union is carried ([`decide-035`](../../data/_vectors/clc-v1/vectors.json)). **The consumer must evaluate or confirm every entry or MUST deny** ([08-constraints](08-constraints.md) §3).

**Fail-closed constraint refusals:** unknown `(scheme,type)` → `deny("unknown_constraint")` ([`decide-003`](../../data/_vectors/clc-v1/vectors.json); [`payments-002`](../../data/_vectors/clc-v1/vectors.json)); out-of-grammar values → `deny("invalid_constraint")` ([`decide-019/-021/-022`](../../data/_vectors/clc-v1/vectors.json)); out-of-domain op values → `max_rows:violated` ([`decide-031..034`](../../data/_vectors/clc-v1/vectors.json)).

## 4. Multi-grant aggregation

**Scenario:** G1 `{"limit":10}`, G2 `{"limit":100}`, op `{"limit":50}` → `allow` — any-one-covers authorizes ([`decide-029`](../../data/_vectors/clc-v1/vectors.json)). The reverse universe: G1 `{"limit":10}`, G2 `{"limit":6}`, op `{"limit":50}` → `deny("params_exceed_grant")` with the **first covering grant in canonical order** (deterministic; [`decide-030`](../../data/_vectors/clc-v1/vectors.json)). Operation id model: absent/empty grants + absent op → `capability_not_authorized` ([`decide-016`](../../data/_vectors/clc-v1/vectors.json)); valid grant + absent op id → `missing_capability_id` ([`decide-017`](../../data/_vectors/clc-v1/vectors.json)).

## 5. Containment and chain authorization

**Parent:** `query:SELECT`, `params:{"limit":100}`. **Child:** `query:SELECT`, `params:{"limit":50}` → `contains:true` ([`contain-040`](../../data/_vectors/clc-d/containment-vectors.json)); the reverse → `params_not_narrower` ([`contain-041`](../../data/_vectors/clc-d/containment-vectors.json)); a different scheme → `different_namespace` ([`contain-004`](../../data/_vectors/clc-d/containment-vectors.json)).

**Fused chain:** `AuthorizeWithChain` — empty chain → `absent_source` ([`ac-001`](../../data/_vectors/clc-d/authorize-chain-vectors.json)); widening child hop → `params_not_narrower` ([`ac-006`](../../data/_vectors/clc-d/authorize-chain-vectors.json)); broken hop that would hide an id-less operation → `child_exceeds_parent` ([`ac-007`](../../data/_vectors/clc-d/authorize-chain-vectors.json)); ancestor constraint leaking only through `Intersect` → `max_rows:violated` ([`ac-009`](../../data/_vectors/clc-d/authorize-chain-vectors.json)).

## 6. Evidence-side satisfaction (CLIP of the withheld CLC-E)

The evidence relations (§6.4/§10) are implemented and pinned by `evidence-vectors.json` (32) but the class is **not claimed** ([13-conformance](13-conformance.md)). If you write against them today, remember: `Satisfy` reports binary `SATISFIED`/`UNSATISFIED`; an internal `unknown` at the top level MUST be `UNSATISFIED`, never `SATISFIED`; and `ActionId` is the JCS digest of the **declared material projection** — undeclared fields must not affect it, missing declared material fields make the action non-matchable.

## 7. Recipe anti-patterns worth internalizing

| Anti-pattern | Why it fails | Fix |
|--------------|-------------|-----|
| Reading `allow_unresolved` as `allow` | the enum values are distinct; residual obligations are additive | evaluate/confirm, else deny (08) |
| Merging a string `"1"` with a number `1` in an enum intersection | equality is JSON type-sensitive | compare after §6.2 canonicalization (intersect-011/-012) |
| Letting a child drop an ancestor constraint | constraints are outside `Contains`, composed by union | chain `Intersect` brings ancestors into force (ac-009) |
| Normalizing a scalar number down to bool(`1`) | boolean is exact, never numeric | `{"flag":1}` vs grant `{"flag":true}` → deny (params-022) |
| Expecting an id-less op to be `capability_not_authorized` | layer-1 op-ID codes propagate specifically | `missing_capability_id` (decide-017) |
| Assuming verdict stability across minors on `param_bounds` meets | the 1.10→1.15 history is not stable there | declare the right revision, use the §12.1 gate (13) |

---
← [13-conformance.md](13-conformance.md) · → [15-glossary.md](15-glossary.md) · related: [01-quickstart.md](01-quickstart.md), [11-reason-codes.md](11-reason-codes.md)