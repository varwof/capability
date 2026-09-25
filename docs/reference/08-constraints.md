# 08 · Constraints, residual obligations, and `Resolve`

> **Normative source:** [`capability-language-core-v1.md`](../capability-language-core-v1.md) §8
> This page is a readable guide. In case of conflict, the normative specification wins.
> Status: Preview — not for production use.

## TL;DR

Constraints limit **how** a capability may be used. v1 core recognizes exactly three `(scheme, type)` pairs; only `max_rows` has a core evaluator. A recognized-but-unevaluated constraint is carried on the verdict as `allow_unresolved` + `unresolved` — never silently dropped. `Resolve` closes the consumer's feedback loop per obligation.

## 1. Constraint identity: `(scheme, type)`

Constraints use colon-notation triples `scheme:type[:params]`; **the identity is the pair** `(scheme, type)`, never the type name alone (§8.1).

```
varwof/constraint-v1 : max_rows      (core evaluator exists)
varwof/constraint-v1 : time          (validated, not evaluated)
varwof/constraint-v1 : network       (validated, not evaluated)
```

- `std/database-v1:max_rows` is **not** recognized — scheme-frame matters (§8.1). A non-recognized pair → `deny("unknown_constraint")`, fail-closed ([`decide-003`](../../data/_vectors/clc-v1/vectors.json) `unknown:constraint:type`; [`payments-002`](../../data/_vectors/clc-v1/vectors.json) a scheme-scoped `payments:quota:daily` which is out of the v1 known set).
- A recognized pair must conform to that type's **value grammar**; non-conforming → `deny("invalid_constraint")`.

## 2. Value grammars (§8.1)

| type | legal value (v1) | core behavior |
|------|------------------|---------------|
| `max_rows` | strict non-negative integer | **evaluated** against op params |
| `time:window` | JSON array (≤ 32), each element `{"start":"HH:MM[:SS]","end":"HH:MM[:SS]"}`, UTC segments; segments ascending, **non-overlapping**, half-open `[start, end)`, no single segment crossing midnight | recognized only |
| `network:cidr` | JSON array (≤ 32) of legal IPv4/IPv6 CIDR strings | recognized only |

**Grammar traps** (each pinned by a vector):
- **Scalar `time:window:3600`** is not a legal `time:window` value → `invalid_constraint` ([`decide-021`](../../data/_vectors/clc-v1/vectors.json)).
- **CIDR without a prefix length** → `invalid_constraint` ([`decide-022`](../../data/_vectors/clc-v1/vectors.json)).
- **A single segment crossing midnight** (`22:00→06:00`) must be split into `22:00→00:00` + `00:00→06:00` ([`decide-019`](../../data/_vectors/clc-v1/vectors.json) → `invalid_constraint`). The `end` value `"00:00"` is read as **86400** (next-day midnight): `22:00→00:00` is legal because comparison is on seconds-of-day, not lexical string order (§8.1).

**Operation-side `max_rows` domain** (rev CLC-1.4): absent, string, boolean, negative, fractional or non-finite → `max_rows:violated` (cannot-be-shown-conforming = fail-closed). Pinned by `decide-023` (absent), `decide-031` (`"garbage"`), `decide-032` (`true`), `decide-033` (`-1`), `decide-034` (`1.5`), all → `max_rows:violated`.

**Core recognizes by pair, evaluates `max_rows` only.** Evaluation of `time`/`network` is the declaring scheme's responsibility (§11); core's non-recognition of other pairs is fail-closed, killing cross-scheme pollution: a scheme that defines its own `max_rows` cannot be hijacked by Core's evaluator (§8.1).

## 3. The residual-obligation channel (§8.4)

A recognized constraint whose value conforms to its §8.1 grammar but for which v1 core defines **no evaluator** (`time`, `network`) MUST NOT be dropped: it appears on the decision's additive `unresolved` list, and the verdict is `allow_unresolved` — **an independent enum value, never equal to `allow`** ([`decide-020`](../../data/_vectors/clc-v1/vectors.json) `network:cidr`; [`decide-024`](../../data/_vectors/clc-v1/vectors.json) split cross-midnight window, both recognized-only).

**Fail-closed boundary:** a consumer (PEP / profile / declaring scheme) MUST evaluate or confirm every `unresolved` constraint before allowing; **if it cannot, it MUST deny**. A consumer that only checks `if verdict == "allow"` cannot, on the literal enum, release a residual as an already-satisfied allow (§8.4).

- `unresolved` ordering (§8.4, rev CLC-1.15): normalized strings, duplicates folded, ordered **by UTF-8 byte sequence** — the §7.1 collation, *not* the ECMAScript default (UTF-16 code-unit) order. Join once and sort exactly once before emitting.
- **Combined obligations** (consumer side): multiple `unresolved` of the same `(scheme,type)` form a **conjunction (AND)** — satisfying A and B satisfies all; OR / any-one / first-wins / ignoring some are forbidden. Different `(scheme,type)` do not interact (§8.4).

## 4. `Resolve` — the consumer's feedback loop (§8.5)

```
Resolution = { constraint: string, status: "satisfied" | "violated" | "unknown" }
Resolve(decision, resolutions, now?) → Decision
```

In order: **(1)** terminal verdicts fixed — `deny`/`allow` return unchanged, `resolutions` ignored; **(2)** malformed input fails closed — bad `status`/constraint → `invalid_resolution`, bad `now` → `invalid_timestamp`; **(3)** discharge — for each obligation combine core clock + consumer resolutions under **`violated` ≻ `satisfied` ≻ `unknown`**; **(4)** repeated entries combine the same way; **(5)** unrelated resolutions are ignored (`O` is authoritative); **(6)** any violated → `deny({type}:violated)`; all satisfied → `allow`; else `allow_unresolved` with the still-`unknown` subset.

**Core clock:** when `now` is supplied, a `varwof/constraint-v1:time` obligation whose value is a §8.1 window array is evaluated by the core: inside a segment → satisfied, outside → `time:violated` ([`resolve-015`](../../data/_vectors/clc-v1/resolve-vectors.json): `now=21:00` outside `[22:00,24:00)`; malformed `now` refused in [`resolve-024`](../../data/_vectors/clc-v1/resolve-vectors.json)). Pinned elsewhere: partial satisfaction → `allow_unresolved` with the remainder ([`resolve-006`](../../data/_vectors/clc-v1/resolve-vectors.json)); any violated → deny with the offending `{type}:violated` ([`resolve-009`](../../data/_vectors/clc-v1/resolve-vectors.json)); a resolution outside `O` is ignored ([`resolve-013`](../../data/_vectors/clc-v1/resolve-vectors.json)); unrecognized `status` → `invalid_resolution` ([`resolve-023`](../../data/_vectors/clc-v1/resolve-vectors.json)).

**No caching beyond the horizon:** a core-clock discharge is valid for the instant of the call. A consumer acting on a `Resolve` result must either re-invoke with current `now` immediately before acting or not cache past the current segment's end — a cached `allow` must not outlive its window (§8.5).

`Resolve` is deterministic, fail-closed, idempotent (`Resolve(Resolve(d,r,now),r,now) = Resolve(d,r,now)`) and monotone. It neither invents nor drops obligations.

## Prevent-mixup checklist

- [ ] Identity is `(scheme,type)`: `foo/database-v1:max_rows` is `unknown_constraint`, never Core's evaluator.
- [ ] Recognized-but-unevaluated ⇒ `allow_unresolved` + `unresolved` — `allow_unresolved` is not `allow`.
- [ ] Grammar refusals are `invalid_constraint` (value out of grammar) — distinct from `unknown_constraint` (pair not recognized).
- [ ] `time:window` crossing midnight is split into two same-day segments; `"00:00"` in `end` = 86400.
- [ ] `Resolve` never revives a `deny`, never widens via an unrelated resolution, and resolves `now`-starved `time` obligations to `unknown` (no TTL).

## Common pitfalls

- **Silently skipping an unevaluated constraint** — conformance bug; residual obligations are additive (§8.4).
- **Trusting `time`/`network` as evaluated** — core recognizes the value grammar only; evaluation belongs to the declaring scheme.
- **Caching a `Resolve` allow past the segment end** — outlives its discharge horizon (§8.5).

---
← [07-parameters.md](07-parameters.md) · → [09-intersection.md](09-intersection.md) · related: [10-decisions.md](10-decisions.md), [11-reason-codes.md](11-reason-codes.md)