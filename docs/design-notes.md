# CLC-v1 design notes — decision record (English)

Normative text: [`capability-language-core-v1.md`](capability-language-core-v1.md).
Principles: [`capability-language-core-principles-v1.md`](capability-language-core-principles-v1.md).
Full narrative history (Chinese, superset of this record):
[`capability-language-core-design-notes-zh.md`](capability-language-core-design-notes-zh.md).

This file is the English record of the **decisions** a reviewer is likely to ask
about: what was chosen, what was rejected, and why.  Entries are dated.

## D1 — Numeric parameter domain semantics (2026-09-10, v1.1). Option A chosen.

A number inside a granted **array** denotes that exact value, not an upper bound:
`grant {"station":[3]}` does not cover `station 2` (deny `not_in_enum`), whereas a
scalar number keeps bound semantics (`{"max_rows":100}` covers 50).
Rejected Option B (array members as bounds) because it silently widens categorical
parameters — station, cell, batch, tool id — where a bound is meaningless.
Scheme authors SHOULD encode categorical parameters as arrays.

## D2 — Resolved reason ordering (2026-09-10, v1.2).

When several conditions fail at once, exactly one code is reported: the first
applicable layer in a fixed order.  The ordering is normative (§9.3), and the
corpus asserts the **canonical reason**, not just the verdict
(canonical = everything before the first `:` in a code, §9.4).

## D3 — Fail-closed on an absent/empty effective grant (2026-09-10, rev 5).

`Authorize` called with no grant (or an empty record) MUST return
`deny(capability_not_authorized)` rather than raising.  The empty-effective-grant
check is a **pre-check** that precedes layer 1 — so it wins even when the operation
is also malformed (`decide-016`).

## D4 — Input normalization and language revision (2026-09-11).

- §6.2.1: params are normalized at the input boundary in a fixed order —
  **size/depth → duplicate keys → number shape**.  Limits: serialized form ≤ 512
  bytes (octets of the canonical UTF-8 form) and nesting depth ≤ 32, counting the
  outermost object as level 1.  Over the limit → `invalid_params_size`.
- §12.1: an input declares its revision; an implementation evaluates it only when
  the revision is compatible (same major, minor ≤ its own), otherwise
  `deny(unsupported_language_revision)` **before any layer**.  No silent downgrade.

## D5 — Key closure (`undeclared_param`, 2026-09-11). Fail-closed chosen.

A bounded grant rejects an operation that declares a parameter the grant does not
declare.  The alternative ("a grant constrains only what it declares") was
rejected: it lets an operation smuggle a parameter past a grant that never
authorized it.  See D8 for how closure composes with intersection.

## D6 — Spec-text closeout (2026-09-11).

Six reason codes that existed only in the implementations and the corpus were added
to §9.4 (`undeclared_param`, `invalid_params_duplicate_key`, `invalid_params_number`,
`invalid_params_size`, `unsupported_language_revision`, `absent_source`);
§12.1 was added; §9.3 was rewritten as a pre-check plus **11 layers** so the layer
numbers cited by the corpus point at the right rows; the appendix vector counts were
brought in line with the machine-readable corpus.

## D7 — P11 "composition narrows only" (2026-09-11).

An intersection must stay inside every source and must not depend on source order.
Two relations are involved and must not be conflated:

- **source coverage (⊑, §7 rule 2)** — grant vs grant, comparing only the keys the
  source declares; a parameter is authorized when *some* source declares it, so the
  effective key set is the union;
- **`Entails`** — grant vs *operation*, the authorization relation, which applies
  key closure (D5).

Closure belongs to the **effective** grant only: every verifier entry point
evaluates exactly one grant (`Authorize(effectiveGrant, op)`;
`Entails(signerGrant, ruleCapability)`), and no code path re-evaluates each source.
An earlier property test re-applied each source's closure separately and reported
176 "failures" that were an artefact of the question, not of the implementation.

## D8 — Three divergences found by probing (2026-09-11, evening).

After the third spec batch, six probe vectors were run against **all three**
implementations (Go, Python, TypeScript):

| Probe | Spec | Go | Python | TypeScript |
|---|---|---|---|---|
| boolean exact (`true` vs `1`) | deny `params_exceed_grant` | ✅ | ❌ **allow (fail-open)** | ✅ |
| layer 6 (null) before layer 7 (presence) | `invalid_params_null` | ❌ `params_missing` | ✅ | ✅ |
| wildcard-shaped operation id | `unsupported_wildcard` | ❌ `invalid_capability_id` | ✅ | ✅ |

Root causes and fixes:

1. **Python** ordered the boolean branch after the numeric branch, and `True == 1`
   in Python — a boolean grant was satisfied by `1` (fail-open).  Boolean handling
   now precedes the numeric branch, and `bool` is excluded from numeric comparison.
2. **Go `Entails`** tested `op.Params == nil` before grant-side null validation;
   the null check now runs first (in `paramsSubset` too, ordered 5 → 6 → 7).
3. **Go `Authorize`** collapsed every layer-1 failure into `invalid_capability_id`;
   it now propagates the validator's specific code.

The corpus could not see any of this: it had no boolean-vs-number, null-plus-missing
params, or wildcard-shaped operation id inputs.  Four vectors were added
(`params-022/023/024`, `decide-018`).

## D9 — Raw-params check order in TypeScript (2026-09-11, evening).

The TypeScript `validateRawParams` was a single-pass parser: it threw
duplicate-key / bad-number errors *during* parsing and checked the total size only
at the end, so for "over-limit + duplicate" the reported code was the reverse of
§6.2 item 5.  It is now **two passes** — pass 1 computes size and depth and throws
`invalid_params_size`; pass 2 enforces duplicates and number shape.  Depth is still
checked inline (it belongs to item 4).  Three combination vectors pin the order:
`params-025` (over-limit + duplicate → size), `params-026` (over-limit + `1e400` →
size), `params-027` (duplicate + `1e400`, under the limit → duplicate).

## D10 — CLC-1.3 closeout: verdict channel, constraint identity, multi-grant (2026-09-12).

Two review observations closed the CLC-1.2 sweep:

**Observation 1: "allow + unresolved" is a pseudo-allow.**  A decision that
says `allow` while carrying constraints the core cannot evaluate invites
consumers to act first and ask later.  Rev CLC-1.3 gives the residual
channel its own verdict value, `allow_unresolved` (§8.4): it is a distinct,
single surface (the informational `verbatim` field was removed from all three
implementations), and the consumer's obligation is unchanged — evaluate each
listed constraint or deny.  **Decision:** the verdict enum gains
`allow_unresolved`; `decide-020/024` pin time/network cases and `decide-019`
pins the cross-midnight single-window segment as `invalid_constraint`
(rewritten from the CLC-1.2 corpus where it generated `unresolved`).

**Observation 2: multi-grant authorization was undefined.**  A verifier that
holds several authorities for the same operation needs a rule.  §9.3 now
defines aggregation: any covering-and-allowing grant authorizes (union, so a
narrow grant cannot veto a broad one); residual obligations union across the
covering-and-allowing grants; when none allows, the first covering grant's
params/constraint reason in canonical (input) order is returned.  Implemented
as `AuthorizeSet(grants, op)` (single-grant `Authorize` is the degenerate
case).  The corpus pins it with `decide-028` (`{}` ≡ absent → any params
allowed), `decide-029` (any-allow) and `decide-030` (all-deny, first reason).

Two smaller closures rode along because they changed the same lines:
constraint identity is now the full `scheme:type` pair (only
`varwof/constraint-v1` is core-recognized — a same-name constraint under any
other scheme is `unknown_constraint`), and the time-window value grammar
forbids single segments crossing midnight (the reserved `end:"00:00"`
denotes next-day midnight, so a crossing is *split* into plain same-day
segments like `22:00→00:00` + `00:00→06:00`).

## Corpus and tooling state

| Item | State |
|---|---|
| Conformance corpus | `vectors.json` — **120 vectors** (syntax 9 / entail 47 / intersect 14 / decide 50) |
| Property corpus | `property-cases.json` — 1184 deterministic P11 cases, reproducible byte-for-byte |
| Implementations | Go (`varwof/register`), Python and TypeScript (`varwof/aic-capability-demo`) — all three 120/120 and 1184/1184 (0 failures; counters 869/841) |
| Schema | `vectors.schema.json` (verdict enum incl. `allow_unresolved`, `multi` switch), enforced in CI together with the documented counts |

Engineering discipline carried from the principles: one contract with several
consumers; fail-closed by default; all-or-nothing generation; a gate must cover every
entry point; and every artifact needs a gate (or it drifts).

## Open items

1. **CLC-E (evidence side)**: §4.2/§6.4/§10 have text and §12 declares the
   conformance class, but there is no implementation and no vector.  Either
   implement it or state explicitly that v1 makes no CLC-E conformance claim.
2. **Third-party parity**: the three implementations share one author; an
   independent implementation is the half of P7/P8 that cannot be self-certified.
3. **Carrier citations**: no carrier document (AIC-JWT, gateway-core, types) cites
   CLC yet, and a second subset implementation exists in the WIT/WPT interop study
   whose wildcard surface is one v1 forbids.
