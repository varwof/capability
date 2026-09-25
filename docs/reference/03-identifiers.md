# 03 · Identifiers — the `capability-id` grammar

> **Normative source:** [`capability-language-core-v1.md`](../capability-language-core-v1.md) §3 (Grammar), §6.1 (Entailment, namespace), §9.1 layer 3/4 (reason ordering)
> This page is a readable guide. In case of conflict, the normative specification wins.
> Status: Preview — not for production use.

## TL;DR

A capability identifier is `scheme:action` (e.g. `std/database-v1:query:SELECT`), optionally ending in a **trailing wildcard** segment `*`. v1 defines exactly **one** wildcard shape — the complete final segment. Everything else (`*:query...`, `re*`, `**`, `{a,b}`, `[a-z]`) is reserved for v2 and rejected in a v1-conforming implementation. Identifiers with different namespaces (scheme + action Class) never entail each other.

## The grammar (v1, closed)

```
capability-id = scheme ":" action [ ":" wildcard ]
wildcard      = "*"
scheme        = vendor "/" product "-v" major
vendor        = 1*( ALPHA / DIGIT / "-" )
product       = 1*( ALPHA / DIGIT / "-" )
major         = 1*DIGIT
action        = segment *( ":" segment )
segment       = 1*( ALPHA / DIGIT / "-" / "_" / "." )
```

Two structural consequences matter in practice:

1. **Scheme is anchored by the *last* `-v<digits>`.** Because `product` may itself contain `-`, the `-v` suffix must be the **last** occurrence of `-v` followed by digits. A product that contains the two-character sequence `-v` internally is invalid (`invalid_capability_id`) rather than ambiguous: `a/b-v1-v2` is **rejected**, it is never parsed two ways; `b-v1` as a product name is simply not expressible in v1.
2. **The trailing wildcard is part of the grammar.** `std/database-v1:query:*` is a *well-formed capability-id*, not a malformed action. Only that complete-final-segment shape is a wildcard.

When the same string would fail both the wildcard-shape check and the generic grammar, **wildcard detection runs first** and reports `unsupported_wildcard` (§3, "before the generic `invalid_capability_id` test").

## Three tiers of identifiers

| Tier | What it is | v1 rule | Example |
|------|-----------|---------|---------|
| Well-formed plain | full grammar, no wildcard | `valid` | `std/database-v1:query:SELECT` |
| Well-formed wildcard | trailing `*` only | `valid` for grant/request patterns | `std/database-v1:query:*` |
| Forbidden wildcard shapes | partial / bare / nested / bracket | `unsupported_wildcard` (v2-reserved) | `std/crm-v1:re*`, `*`, `**` , `{a,b}`, `[a-z]` |
| Ill-formed scheme/action | missing scheme, bad major, `-v` ambiguity | `invalid_capability_id` | `database:query`, `a/b-v1-v2` |

## Field examples (real corpus ids)

**A valid identifier** — [`vectors.json → syntax-001`](../../data/_vectors/clc-v1/vectors.json)

```json
request = { "id": "std/database-v1:query:SELECT" }   →  valid
```

**Default identifiers may be deeper than one action segment** — [`vectors.json → syntax-009`](../../data/_vectors/clc-v1/vectors.json)

```json
request = { "id": "std/data-v1:fetch:item:42" }      →  valid
```

**Forbidden wildcard shapes** — each is `unsupported_wildcard`, never a deep-match attempt:

[`syntax-003`](../../data/_vectors/clc-v1/vectors.json) `*:query:SELECT` (wildcard in scheme position) → `invalid` `unsupported_wildcard` · [`syntax-004`](../../data/_vectors/clc-v1/vectors.json) `std/database-v1:query:SEL*` (partial action) → same · [`syntax-005`](../../data/_vectors/clc-v1/vectors.json) `std/database-v1:query:{read,write}` (expansion set) → same · [`syntax-006`](../../data/_vectors/clc-v1/vectors.json) `std/database-v1:query:[a-z]` (character class) → same. The refusal is identical *as a request*: [`decide-018`](../../data/_vectors/clc-v1/vectors.json). The *one* permitted wildcard shape is still valid as an id — [`syntax-002`](../../data/_vectors/clc-v1/vectors.json) `std/database-v1:query:*` → `valid`.

**Not a v1 identifier at all** — [`syntax-007`](../../data/_vectors/clc-v1/vectors.json) `database:query` (no scheme) → `invalid` `invalid_capability_id`; same code when the grant is well-formed but the request is not ([`decide-004`](../../data/_vectors/clc-v1/vectors.json), [`decide-025`](../../data/_vectors/clc-v1/vectors.json)).

## Namespace: the hard boundary

Entailment only ever happens **inside one namespace**, where namespace = scheme + action Class (`std/database-v1`) (§9.1 layer 3). If grant and operation differ by namespace, the engine answers `different_namespace` **before** looking at the path at all (§6.3 step 1):

[`entail-004`](../../data/_vectors/clc-v1/vectors.json)

```json
grant   = { "id": "std/database-v1:query:*" }
request = { "id": "std/database-v1:admin:DDL" }   →  deny  different_namespace
```

## The class-position wildcard trap

A `*` one segment **before** the end is NOT a wildcard that matches everything up front — a class-position wildcard is a v1-forbidden shape, and its request is rejected at grammar time (§9.1 layer 3, `unsupported_wildcard`), not silently widened at entailment time. The corpus pins both the deny-being-narrow (same action) and the deny-anyway (different action) readings:

[`entail-007`](../../data/_vectors/clc-v1/vectors.json) `grant std/database-v1:*` vs `request std/database-v1:query:SELECT` → `deny` `different_namespace` — the `*` at class position is not a trailing action wildcard; namespace mismatch. Class-position wildcards are v1-forbidden (§3; the requested operation’s own id would be rejected as a `*` in scheme position), and entailment never gets to path coverage.
[`entail-008`](../../data/_vectors/clc-v1/vectors.json) same grant vs `request std/database-v1:SELECT` → `deny` `different_namespace`, class mismatch.

Compare with the **one** full wildcard: [`entail-002`](../../data/_vectors/clc-v1/vectors.json) `grant …query:*` covers `request …query:SELECT` (`allow`) because the `*` occupies the complete trailing segment and there is **at least one** trailing segment. The trailing wildcard never matches the empty remainder ([`entail-005`](../../data/_vectors/clc-v1/vectors.json), `wildcard_requires_trailing_segment`).

## Rules of thumb

- One scheme per vendor/product/`-v` major; the major is digits only.
- Grant `params` and identifier detection happen on the **segment boundary**, not by lexical prefix (so `std/database-v1:query:` + `SEL` is NOT `SELECT`).
- When the same input is both a bad wildcard and bad grammar, the **wildcard error wins** (reported `unsupported_wildcard`, not `invalid_capability_id`).

## Common pitfalls

- **`scheme:action` is mandatory.** An id without a scheme is `invalid_capability_id`, never "assume `std/…`".
- **`-v` (followed by digits) must be the last such run.** A product that embeds `-v1` breaks; `a/b-v1-v2` is ungrammatical.
- **Trailing wildcard requires a remainder.** `query:*` ≠ `query`; the empty remainder is not covered.
- **In σ-position, `*` is a defect, not a shortcut.** Path coverage is strictly per-segment; unknown request segments are `undeclared`-family problems, not "somewhere under a wildcard".

---
← [02-overview.md](02-overview.md) · → [04-actions.md](04-actions.md) · related: [06-entailment.md](06-entailment.md), [09-intersection.md](09-intersection.md)