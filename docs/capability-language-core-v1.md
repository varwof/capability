<!-- Published copy in varwof/capability. Working draft and rationale live in the design repository; treat this copy as canonical once committed. -->

# Capability Language Core v1 (CLC-v1)

> ⚠️ **Preview** — Not for production use. APIs and features may change before official release.

**Category**: Experimental | **Status**: Working Draft | **Date**: 2026-09-10

---

## Abstract

Minimal capability language for AI agent gateways, covering both
authorization and evidence evaluation.  Nine core concepts organized
as a shared foundation with two side-specific operation sets:
authorization (grant, entailment, intersection, decision) and evidence
(match, satisfaction).  Deterministic decision function, fail-closed.

---

## 1. Design Principle

CLC-v1 is a **universal minimal language** that can be consistently
presented on either the authorization side or the evidence side.

The two sides share five foundational abstractions:

| Foundation | Authorization Side | Evidence Side |
|------------|-------------------|---------------|
| **Action** | Operation (concrete request) | ObservedAction (asserted effect) |
| **Identity** | CapabilityId (class-level) | ActionId (instance-level) |
| **Binding** | Entailment (grant ⊆ operation) | Match (evidence ↔ action) |
| **Constraint** | Grant params / limits | Evidence requirements / freshness |
| **Verdict** | allow / deny | SATISFIED / UNSATISFIED |

The language structure is identical on both sides; only the direction
differs:
- Authorization: "I grant you permission to do X"
- Evidence: "I have evidence that X was done"

The design principles behind this core — including what the language
**deliberately refuses** (no control flow, no mutable state, no general-purpose
policy language) — are stated in `capability-language-core-principles-v1.md`:

> P1 minimal core · P2 no control flow · P3 immutable values ·
> P4 domains, not types · P5 deterministic and terminating ·
> P6 fail-closed · P7 define once, consume everywhere ·
> P8 carriers separate from semantics

---

## 2. Terminology

| Term | Definition |
|------|-----------|
| **Action** | The thing being referenced — an abstract operation class (auth) or a concrete asserted effect (evidence). |
| **CapabilityId** | Structured name identifying a class of actions within a scheme. |
| **Operation** | Concrete action request: a CapabilityId plus parameters. |
| **Grant** | Principal's authorization of a CapabilityId with optional params and constraints. |
| **Binding** | Abstract concept connecting an Identity to an Action. Entailment (auth) and Match (evidence) are concrete instances. |
| **Entailment** | Authorization-side binding: "Grant G covers operation O" (⊆). |
| **Match** | Evidence-side binding: "Evidence E is bound to exact action A". |
| **Constraint** | Bound on how an action may be used (auth) or what evidence is required (evidence). |
| **Intersection** | Combining multiple grant sources into an effective set (∩). |
| **Verdict** | Outcome of evaluation: `allow`/`deny` (auth) or `SATISFIED`/`UNSATISFIED` (evidence). |
| **Decision** | Authorization-side verdict: `allow` or `deny` + reason. |
| **Satisfaction** | Evidence-side verdict: `SATISFIED` or `UNSATISFIED`. |

Note: **Binding** in CLC-v1 denotes the identity↔action relation
(coverage on the authorization side, match on the evidence side). It is
**not** key binding (cnf / DPoP / mTLS sender constraint), which belongs
to the native artifact's specification (see §11).

Verdicts are written lowercase on the authorization side (`allow`/`deny`)
and uppercase on the evidence side (`SATISFIED`/`UNSATISFIED`), following
the EMILIA/AEB convention.

---

## 3. Grammar

```
capability-id = scheme ":" action
scheme        = vendor "/" product "-v" major
vendor        = 1*( ALPHA / DIGIT / "-" )
product       = 1*( ALPHA / DIGIT / "-" )
major         = 1*DIGIT
action        = segment *( ":" segment )
segment       = 1*( ALPHA / DIGIT / "-" / "_" / "." )
wildcard      = action ":" "*"
```

A v1 identifier is `scheme:action` (e.g. `std/database-v1:query:SELECT`).
Trailing `*` as a complete segment matches **one or more** remaining segments
(it does not match the empty remainder: `std/database-v1:query:*` does not
cover `std/database-v1:query`).

**Wildcard scope for v1**: CLC-v1 core defines exactly one wildcard shape:
the complete trailing segment `*`.  Partial (`std/crm-v1:re*`), bare `*`,
`**`, `{a,b}`, `[a-z]` are **reserved for v2**; a v1-conforming
implementation MUST reject them (`unsupported_wildcard`).  If a capability
scheme declares its own extended grammar, that scheme's conforming
implementation may accept it; but CLC-v1 core conformance neither requires
nor authorizes those forms (see §12).

**Wildcard detection precedes grammar conformance.**  A forbidden
wildcard shape is reported as `unsupported_wildcard` even when the same
string also violates the base grammar (§3 `segment`): the wildcard-shape
checks run before the generic `invalid_capability_id` test.

**Examples**: `std/database-v1:query:SELECT` ✓ | `database:query` ✗ |
`std/database-v1:query:*` ✓ | `std/database-v1:query:SEL*` ✗

---

## 4. Action

An action is the thing being referenced.  CLC-v1 defines two concrete forms:

### 4.1 Operation (authorization side)

A concrete action request: CapabilityId + parameters.

```
{ "id": "std/database-v1:query:SELECT",
  "params": {"tables":["customers"], "limit":{"max":50}} }
```

Missing `id` → `deny("missing_capability_id")`.

### 4.2 ObservedAction (evidence side)

The material action constructed by the effect boundary from
executor-controlled facts.  CLC-v1 defines the interface, not the
construction algorithm.

An ObservedAction carries:
- `action_type`: the CAID action type (or equivalent canonical form)
- `material_fields`: every field the type definition declares required
- `digest`: computed over canonical bytes of the action object

The effect boundary MUST construct the ObservedAction from facts it
controls.  It MUST NOT copy a requester-supplied action digest without
deriving or checking the corresponding fact.

### 4.3 Identity

Two identity levels, corresponding to the two Action forms:

| Level | Identity | Scope | Example |
|-------|----------|-------|---------|
| Class | CapabilityId | Covers a class of actions | `std/database-v1:query:*` |
| Instance | ActionId | Identifies one exact action | `caid:1:payment.release.1:jcs-sha256:...` |

A CapabilityId covers a class; an ActionId identifies a single instance.
Entailment checks class coverage; Match checks instance binding.

---

## 5. Grant

A grant = CapabilityId + optional params + optional constraints.

```
grant       = capability-id [ params ] [ constraints ]
constraint  = scheme ":" type [ ":" params ]
```

Constraints are deny-when-declared: explicitly empty bound (e.g. zero
max, empty allowlist) denies the class; omitted bound uses scheme default.

---

## 6. Binding

Binding is the abstract concept of connecting an Identity to an Action.
CLC-v1 defines two concrete instances:

### 6.1 Entailment (authorization binding)

Grant G covers operation O if:

1. **Literal**: G = O (byte-for-byte after normalization).
2. **Trailing wildcard**: G = `scheme:prefix:*` and O has **at least one**
   segment after `scheme:prefix:` (segment-boundary comparison, not lexical
   prefix).

| Grant | Operation | Result |
|-------|-----------|--------|
| `std/database-v1:query:*` | `std/database-v1:query:SELECT` | ✓ wildcard matches |
| `std/database-v1:query:*` | `std/database-v1:query:SELECT:deep` | ✓ matches multi-segment |
| `std/database-v1:query:*` | `std/database-v1:admin:DDL` | ✗ different namespace |
| `std/database-v1:query:SELECT` | `std/database-v1:query:INSERT` | ✗ literal mismatch |

### 6.2 Parameters

| Type | Rule | Example |
|------|------|---------|
| number | op ≤ grant | 50 ≤ 100 ✓ |
| string | exact | "a" = "a" ✓ |
| boolean | exact | true = true ✓ |
| array | set of allowed values (enum): request scalar must equal a member; request array — every element must equal a member | `{"station":[1,2,3]}` ⊇ `2` ✓; ⊇ `9` ✗ |
| object | every grant key in op, values recurse | `{"t":["id"]}` ⊆ `{"t":["id","name"]}` ✓ |
| other | exact equality | — |

**Boolean parameters are exact only.** A boolean grant value is matched by
exact equality (`true` covers `true` only).  Booleans are **not** numbers: an
implementation MUST NOT interpret `true`/`false` as `1`/`0` and MUST NOT run
them through the numeric-bound rule (op ≤ grant).  They also play no role in
numeric comparisons or bounds.  (Boolean GRANT-side bounds are rare in
practice; the setting that matters — an operation-side boolean value under
key closure — is pinned by `undeclared-001`.)

Table rows map to vectors: number → `params-001`/`params-002`; array scalar
member → `params-009` (✓) / `params-010` (✗); array element-wise →
`params-011` (✓) / `params-012` (✗); object recursion allow → `params-015`,
deny-direction → `params-005`; categorical guard → `params-014`.
Under the old (pre-v1.1) array-as-bound rule the object example read ✗; with the
v1.1 enum rule the request-side element `id` is a member of the granted set, so
the row is ✓ (see `clc-v1-ambiguities.md` §2).

**Enum semantics of arrays (v1.1).** An array-valued grant parameter is the
**set of allowed values**, not an order.  The request MAY supply a single
scalar (must be a member of the set) or an array (every element must be a
member).  Members compare by **exact equality**: a number inside a granted
array denotes that exact value, not a bound.  This is what keeps categorical
identifiers safe — `grant {"station":[3]}` does **not** cover `station 2`
(failure → `deny("not_in_enum")`).  Scheme authors SHOULD encode categorical
parameters (station, cell, batch, tool id) as arrays; a scalar number in the
grant keeps upper-bound (bound) semantics for ordered quantities
(`max_rows`, `speed`, `angle`).

An explicitly empty grant array `[]` denies the class
(`empty_bound_denies_class`).

Grant with no params covers any operation params (unconstrained).

A `null` parameter value is invalid in v1 → reject (`invalid_params_null`).
Absent ≠ explicitly empty (see §8).

**Key closure (Plan A).**  A bounded grant governs its declared keys: an
operation carrying a parameter key the grant does not declare is rejected →
`deny("undeclared_param")` (fail-closed, §9.3 layer 7 request side).  An
unconstrained grant (no `params`) accepts any operation params, so no key
closure applies there.  Within layer 7 the missing-key check
(`params_missing`) resolves **before** the undeclared-key check
(`undeclared_param`); both are key-level and run before the enum/bound value
checks (layers 8–9).

**Params representation and input normalization (v1.1).** Before any §9.3
layer runs, the `params` object is normalized at the input boundary:

1. **Canonical serialization.** Params are serialized per the JSON
   Canonicalization Scheme (I-JSON, RFC 8785) — key order, number form, and
   spacing are preserved exactly.  Evaluation never guesses; a lossy
   re-serialization (e.g. a map that drops duplicate keys) is not used for
   decisions.
2. **Duplicate keys.** A params object with a duplicate JSON key is rejected:
   `deny("invalid_params_duplicate_key")`.
3. **Number shape.** A numeric param that is non-finite or over-precision
   (> 17 significant decimal digits, e.g. `1e400`) is rejected:
   `deny("invalid_params_number")`.  Malformed JSON that cannot be parsed as
   an object falls into the same code.
4. **Size and depth.** Params whose JCS-serialized form exceeds 512 bytes
   (octets of the canonical UTF-8 form), or whose nesting depth exceeds 32,
   are rejected:
   `deny("invalid_params_size")`.  Nesting depth counts **both** objects and
   arrays, with the outermost object as level 1 (31 nested arrays inside the
   top-level object therefore = depth 32).
5. **Order of checks.** Size/depth (4) precede duplicate keys (2), which
   precedes number shape (3); the first failing check wins.  All five run
   before §9.3 layer 1, so normalized params are the only view the layers see.

### 6.3 Algorithm

```
Entails(G, O) → bool:
  1. G.namespace ≠ O.namespace → false      (namespace = scheme + action Class, §9.3 layer 3)
  2. G.id doesn't cover O.id → false        (path coverage, §9.3 layer 4)
  3. G.params absent → true                 (grant unconstrained)
  4. O.params absent → false                (bounded grant, request omits it → fail-closed)
  5. params_subset(O.params, G.params)      (both present → compare, §9.3 layers 5–9)
```

When more than one check fails, the reported reason follows the fixed
resolved-reason ordering of §9.3.  The remaining rules of this section
are unchanged.

**Rule for missing operation params**: If the grant has a params bound
(step 3 does not apply) and the operation has **no `params` field at
all** (not merely a key missing, but the entire field absent), step 4
applies: `Entails → false` → `deny("params_missing")`.  This covers
both "operation omits the entire params object" and "operation omits a
single bounded key" — both fail closed.

If a capability scheme declares a default value for a parameter, the
implementation MUST apply that scheme default to O before step 4; absent
such a declared default, step 4 denies.

**Layer 6 (null) resolves before presence.**  If the grant's params carry a
`null` value (or the operation's params do), the failure is
`invalid_params_null` (§9.3 layer 6) and is reported even when the
operation omits the `params` field entirely — i.e. layer 6 resolves
**before** step 4's `params_missing`.  This is the fixed §9.3 ordering; it
shadows the literal step order of the algorithm above, which lists presence
before the null checks.

### 6.4 Match (evidence binding)

Evidence E is bound to exact action A if:
1. E carries a valid ActionId (CAID or equivalent).
2. E's ActionId equals the recomputed ActionId of the ObservedAction.
3. The ActionId was computed under the relying-party-pinned suite and
   definition source.

Match is content correlation only.  It does not validate a native
artifact and does not authorize execution.

Cross-format mapping (E's native format ≠ A's canonical form) uses an
Action-Mapping Profile: a hash-identified projection pinned by the
relying party, with results EQUIVALENT_UNDER_PROFILE, NOT_EQUIVALENT,
or INDETERMINATE.

---

## 7. Intersection (∩)

P_effective = P_principal ∩ C_agent ∩ P_gateway (ACA §4.2).

Rules:
1. Each source provides a grant set.
2. Effective grant MUST be covered by at least one grant from every source.
3. Same-capability constraints merged: tightest bound wins.
4. Any source missing a capability → capability absent from effective set.
5. **Zero or absent sources fail closed.** An intersection over **no**
   sources at all — an empty source list, or every source absent — has no
   effective set: `deny("absent_source")`.  (A source that *exists* but
   carries no grant for the capability is rule 4, not rule 5.)
6. **Empty params declares no constraint.** A source whose grant has a
   present-but-empty `params` object contributes no restriction.  The
   accumulated bound is preserved: bounded-then-empty and empty-then-bounded
   must give the same result — source order MUST NOT change the outcome.

**Identifier comparison is params-free (rule 2).**  The effective identifier
is the **narrowest** one covered by every source, chosen by the §6.1
identifier rules alone.  It MUST NOT be resolved by routing grants through
`Entails` with params — a bounded grant faced with a params-less sibling
would trigger presence handling (§6.3 step 4) and wrongly fail this
open; the identifier is compared, params merge separately (rule 3).

**Property: composition narrows only.**  If `Intersect` succeeds, the
result MUST be covered by every source and MUST NOT depend on the order
of the sources; otherwise it MUST deny with a normative reason code and
MUST never raise.  This meet-law is what the §6.2 param-subset algebra
preserves across sources; it is pinned by `property-cases.json` (524
cases, §12).

**Notation in this section**: params are JSON objects (e.g.
`{"tables":["a"]}`); constraints use colon-notation triples (e.g.
`varwof/constraint-v1:time:window:3600`).  The example tables below use
compact shorthand for readability; each row shows the relevant params or
constraints only.

**Deny-when-declared**: `{"tables":[]}` (explicitly empty) = deny the class.
Omitted = scheme default.  A `null` value is invalid in v1 → reject
(`invalid_params_null`).  Canonicalization MUST NOT broaden (segment-boundary
comparison, not lexical prefix).

| Source A | Source B | Result |
|----------|----------|--------|
| `{"tables":["a","b"]}` | `{"tables":["a"]}` | `{"tables":["a"]}` ✓ |
| `{"tables":["a"]}` | `{"tables":[]}` | deny ✗ |
| (unconstrained) | (no grant) | deny ✗ |
| `{"limit":100}` | `{"limit":50}` | `{"limit":50}` ✓ |
| (unconstrained) | constraint `time:window:3600` | constraint applied ✓ |
| `{"tables":["a"]}` | `{"tables":["b"]}` | deny ✗ |

---

## 8. Constraint

Constraints are shared between authorization and evidence sides.

### 8.1 Authorization-side constraints

Limit how a capability may be used.  Constraints use colon-notation
triples: `scheme:type[:params]`, where **`type` is the second
`:`-delimited segment** (`scheme` `:` `type` [ `:` params... ]):

- `varwof/constraint-v1:max_rows:100` — type `max_rows`, param `100`
- `varwof/constraint-v1:time:window:3600` — type `time`, param
  `window:3600`
- `varwof/constraint-v1:network:cidr:10.0.0.0/8` — type `network`, param
  `cidr:10.0.0.0/8`

v1 **recognizes** the constraint types `max_rows`, `time`, `network`; a
constraint of a recognized type is never `unknown_constraint`.  The core
defines an evaluator for `max_rows` only; evaluation of `time`/`network`
bounds is the declaring capability scheme's responsibility (§11).  Unknown
constraint → reject (fail-closed).

Merge rules: numeric → minimum wins; allowlist → intersection; denylist
→ union; time → intersection; unknown → deny.  The allowlist is the
array-enum set (§6.2); intersecting it takes the shared members.  v1 core
defines **no denylist constraint** — the denylist merge rule applies only
to scheme-defined denylist types (§11).

### 8.2 Evidence-side constraints

Require specific evidence properties: freshness, consumption, quorum,
initiator-exclusion, etc.

These are structurally identical to authorization constraints — a
`type` plus optional `params` — but evaluated against evidence artifacts
rather than operation parameters.

### 8.3 Unified constraint grammar

```
constraint = scheme ":" type [ ":" params ]
```

Both sides use the same grammar.  The validator (authorization) or
evidence evaluator (evidence) interprets the type-specific params.

---

## 9. Decision Function (Authorization Side)

```
Authorize(effective_grants, operation) → Decision
Decision = { verdict: "allow"|"deny", reason: string|null }
```

Algorithm:
1. Validate operation: missing/invalid id → deny with stable reason.  The
   operation's **specific layer-1 code** is reported — `missing_capability_id`
   (no id), `unsupported_wildcard` (v1-forbidden wildcard shape) or
   `invalid_capability_id` (other grammar violation) — and is **not**
   collapsed to a generic code.
2. Find matching grants via Entailment (§6.1).
3. No match → `deny("capability_not_authorized")`.
4. Evaluate constraints: unknown → `deny("unknown_constraint")`;
   violation → `deny("{type}:violated")`.
5. All pass → `allow`.

The effective grant set may be **absent or empty** — e.g. an integrator
calls `Authorize` with no grant value or with an empty capability record.
A safe evaluator MUST NOT raise; it MUST resolve such input to
`deny("capability_not_authorized")` (falling out of layer 10/step 3).
An absent operation resolves to `deny("missing_capability_id")`
(layer 1); the evaluator MUST NOT raise there either.

Properties: deterministic (same input → same output), fail-closed,
stable reason codes.

### 9.3 Resolved Reason Ordering (normative)

When more than one condition fails for a grant/operation pair, the
**resolved reason** (the single code reported) is the first applicable
layer in this fixed order.  It applies to `Entails` (§6.3),
`Intersect` (§7) and `Authorize` (this section).

| # | Layer | Checks | Reason code(s) |
|---|-------|--------|----------------|
| 1 | CapabilityId validity | §3 grammar, wildcard shape | `invalid_capability_id`, `missing_capability_id`, `unsupported_wildcard` |
| 2 | Params normalization | Duplicate JSON keys; non-finite/over-precision numbers; size/depth limits (§6.2) | `invalid_params_duplicate_key`, `invalid_params_number`, `invalid_params_size` |
| 3 | Namespace = scheme + action Class | Grant vs operation scheme and Class | `different_namespace` |
| 4 | Path coverage (same namespace) | Literal path segments, trailing-wildcard depth | `literal_mismatch`, `wildcard_requires_trailing_segment` |
| 5 | Explicit empty bound | Any grant/intersection source declares `[]`/`{}` | `empty_bound_denies_class` |
| 6 | Null values | Any `null` parameter value | `invalid_params_null` |
| 7 | Param presence | Grant bounds a param the operation omits (or operation has no `params`); operation carries a key the grant does not declare | `params_missing`, `undeclared_param` |
| 8 | Enum membership | Request value not a member of a granted array set (§6.2) | `not_in_enum` |
| 9 | Bound comparison | Numeric/bound exceeded | `params_exceed_grant` |
| 10 | Coverage emptiness | Intersection result empty; zero sources; no grant covers the operation | `no_overlap`, `absent_source`, `capability_not_authorized` |
| 11 | Constraint evaluation | Unknown constraint type; known type violated | `unknown_constraint`, `{type}:violated` |

Notes:

- **Namespace** is `scheme:action_class` (the first two `:`-delimited
  segments).  Identifiers in the same namespace differ only below the
  Class; such mismatches are path-level (`literal_mismatch` /
  `wildcard_requires_trailing_segment`), not `different_namespace`.
- **Params normalization fires at the input boundary**: duplicate keys,
  over-precision/non-finite numbers, and size/depth overruns (§6.2) are
  detected before any grant-vs-operation comparison and therefore before
  every other layer of this table.
- **Deny-when-declared**: layer 5 is evaluated on the grant/intersection
  side — an explicitly empty `[]` or `{}` param value denies the class
  regardless of the request, before any member or bound check.
- **Layer 7 key closure runs both directions**: granted keys must be present
  in the operation (`params_missing`) and operation keys must be declared by
  the grant (`undeclared_param`); the missing-key check resolves first, and
  both precede the layer 8–9 value checks.
- **Layer 11 runs last by construction**: constraints are evaluated only
  after coverage and parameters pass.
- In `Authorize` with a single effective string of grants, layers 3–4 and
  10 surface as `capability_not_authorized` when **no** grant covers;
  a matching grant's params layer (5–9) propagates its own reason.
- **Op-ID validation errors propagate their specific layer-1 code**
  (`missing_capability_id` / `unsupported_wildcard` / `invalid_capability_id`),
  never `capability_not_authorized` and never an invented catch-all: step 1
  reports the very code that describes the operation id.  Only **coverage**
  failures (layers 3–4 and 10) collapse to `capability_not_authorized`.
- **Layer 1 validates the operation id only.**  A malformed id in a
  **grant** makes that grant non-matching for every operation: `Entails`
  reports the specific layer-1 code as its false reason, and `Authorize`
  folds the non-match into coverage (`capability_not_authorized`) — the
  grant's own code is not surfaced by the decision.
- An **absent/empty effective grant** drops straight to layer 10
  (`capability_not_authorized`); the evaluator MUST return this decision
  rather than raising.  An absent operation drops to layer 1
  (`missing_capability_id`).
- A **language revision mismatch** (§12.1) is resolved before any layer
  and reports `unsupported_language_revision` (fail-closed, no downgrade).

---

### 9.4 Reason Codes (normative)

Reason codes are stable identifiers. v1 defines:

**Canonical code = everything before the first `:`**.  An implementation
MAY append `: <detail>` (e.g. the offending parameter name) as a
diagnostic suffix; the canonical code is unchanged.  All tooling and
compatibility checks MUST compare the canonical prefix only.

| Reason code | Meaning |
|-------------|---------|
| `unsupported_wildcard` | Wildcard shape forbidden in v1 (bare `*`, partial segment, `**`, `{a,b}`, `[a-z]`) |
| `invalid_capability_id` | CapabilityId does not conform to the §3 grammar |
| `missing_capability_id` | Operation has no `id` (layer 1) |
| `invalid_params_duplicate_key` | Params contain a duplicate JSON key (§6.2 representation, §9.3 layer 2) |
| `invalid_params_number` | A numeric param is non-finite or over-precision (> 17 significant decimal digits) (§6.2 representation, §9.3 layer 2) |
| `invalid_params_size` | Params exceed the 512-byte serialized size or the depth-32 nesting limit (§6.2 representation, §9.3 layer 2) |
| `different_namespace` | Grant and operation differ in namespace (scheme + action Class, §9.3 layer 3) |
| `literal_mismatch` | Literal identifiers differ |
| `wildcard_requires_trailing_segment` | Wildcard has no remaining segment (`...:*` does not cover `...`) |
| `capability_not_authorized` | No grant in the effective set covers the operation |
| `no_overlap` | Intersection of multiple sources is empty |
| `absent_source` | Intersection over zero sources — no effective set (§7 rule 5) |
| `params_exceed_grant` | Request parameters exceed the granted bound |
| `params_missing` | Grant bounds a parameter but the request omits it, or the request has no `params` field at all (fail-closed, §6.3 step 4) |
| `undeclared_param` | Operation parameter key not declared by the grant's params (key closure, §6.2; §9.3 layer 7 request side) |
| `empty_bound_denies_class` | Explicitly empty bound (`[]`/`{}`) denies the class |
| `not_in_enum` | Request value is not a member of the allowed set granted as an array (§6.2 enum rule) |
| `invalid_params_null` | `null` parameter value (rejected in v1) |
| `unsupported_language_revision` | Declared CLC revision is incompatible with the implementation (§12.1; fails closed, no silent downgrade) |
| `unknown_constraint` | Unknown constraint type (fail-closed) |
| `{type}:violated` | A known constraint is violated (e.g. `max_rows:violated`) |

Other schemes MAY define additional codes, but MUST NOT redefine these.

---

## 10. Satisfaction Function (Evidence Side)

```
Satisfy(evidence_set, requirement) → Satisfaction
Satisfaction = { verdict: "SATISFIED"|"UNSATISFIED", reason: string|null }
```

Algorithm:
1. Verify each evidence artifact under its native rules.
2. For each required evidence role, check that an artifact fills it.
3. Check that each artifact is bound to the exact action via Match (§6.4).
4. Evaluate freshness, consumption, and role constraints.
5. All required roles filled and bound → `SATISFIED`.
6. Any role unfilled, unbound, or violated → `UNSATISFIED`.

Properties: deterministic, fail-closed, stable reason codes.

---

## 11. Semantic Boundary

CLC-v1 defines the **shared minimal vocabulary** and **evaluation
algorithms** for both authorization and evidence.

CLC-v1 does NOT define:
- **Trust models**: who signs what, issuer trust, delegation chains
  (belongs to AIC-JWT, OAuth, SPIFFE, etc.)
- **Native verification**: signature checking, schema validation,
  freshness enforcement (belongs to each native artifact's spec)
- **Execution lifecycle**: consumption, invocation, reconciliation,
  outcome classification (belongs to EMILIA AEB or equivalent)
- **Receipt or token formats**: the wire formats for carrying grants,
  evidence, or bindings (belongs to protocol-specific specs)

The boundary is:
- CLC-v1 defines **what** to evaluate (grant ⊆ operation, evidence ↔ action)
- Consumers define **how** to evaluate (native verification, trust anchors)
- CLC-v1 defines **what** the output means (allow/deny, SATISFIED/UNSATISFIED)
- Consumers define **what to do** with the output (invoke, record, reconcile)

---

## 12. Conformance

CLC-v1 defines **two conformance classes**:

**CLC-A (authorization side)** — the v1 baseline. A conforming
implementation MUST implement: grammar (§3), entailment (§6.1),
intersection (§7), decision function (§9), rejection of unknown
constraints, and stable reason codes (§9.4).

**CLC-E (evidence side)** — optional profile, **not claimed by this
version**.  §6.4 (match) and §10 (satisfaction) define the evidence-side
relations, but **no CLC-E implementation and no CLC-E vectors are published
with v1**: an implementation MUST NOT claim CLC-E conformance against this
revision.  The evidence-side text is a semantic mapping — carriers that need
it (e.g. an Action Evidence Envelope) define their own profile over §6.4/§10
and supply their own corpora.  A future revision that ships both an
implementation and vectors is what would make CLC-E a claimable class.

**Conformance corpora.**  CLC-A conformance is exercised by two
machine-readable reference suites shipped at
`capability/data/_vectors/clc-v1/`: `vectors.json` — 83 vectors mapped
to Appendix B — and `property-cases.json` — 524 cases pinning the §7
meet-law, identifier narrowing and source-order independence.  Their
syntax is defined by `vectors.schema.json`; `offline-vectors.json` is a
timestamped snapshot mirror.  A conforming implementation MUST pass both
suites.

Implementations MUST NOT: redefine semantics, accept v1-forbidden
wildcards, or broaden bounds during canonicalization.

**Independence of implementations (honest scope).**  The three implementations
named in this repository's README (Go, Python, TypeScript) are **not independent
evidence**: they share an author, and their agreement is a regression test for
the specification, not third-party validation.  An independent implementation is
invited; until one exists, the parity claim in this document is scoped to
"same-author, three languages, one corpus".  Reviewers SHOULD treat a
single-author parity claim as evidence that the text is *implementable*, not that
it has been independently *interpreted*.

**Experimental neighbours are not CLC.**  The WIT/WPT interop study in
`varwof/aic-jwt` (`wit-wpt-interop/`) is an **experimental** research artifact that
implements a *different*, wider wildcard surface (`**`, `{a,b}`, `[a-z]`) which
this revision rejects as `unsupported_wildcard` (§9.4).  It is not a CLC-A
implementation and MUST NOT be cited as one; it exists to study WIT/WPT
provisioning and carries its own EXPERIMENTAL banner.

### 12.1 Language Revision

Every implementation declares a language revision `CLC-<major>.<minor>` —
this document declares **`CLC-1.1`**.  A capability input (grant,
operation, or OCM) SHOULD carry the revision it was authored against; an
input without a declared revision is treated as `CLC-1.0`.

- **Compatible reading**: an implementation MAY evaluate an input whose
  declared major equals its own AND whose declared minor is ≤ its own
  (so an implementation of CLC-1.1 reads a CLC-1.0 or CLC-1.1 input, but
  not CLC-1.2 or CLC-2.0).
- **Incompatible reading MUST fail closed** with
  `deny("unsupported_language_revision")`.  An implementation MUST NOT
  silently evaluate under a different revision — no downgrade, no
  warning-then-allow.
- The revision check resolves **before any §9.3 layer** and yields the
  single resolved reason code `unsupported_language_revision`.

Vectors: `revision-001` (input CLC-1.0 against an implementation declaring
CLC-1.1 → eval normally, allow); `revision-002` (input CLC-2.0 → deny
`unsupported_language_revision`).

---

## Appendix A: Consumption Mapping

| Consumer | Grammar | Binding | Verdict | Notes |
|----------|---------|---------|---------|-------|
| AIC-JWT DA | capability[].id | Entailment (§6.1) | Decision (§9) | AIC-JWT §5 binding |
| EMILIA AEB | AEG capability_class | Match (§6.4) + Entailment (§6.1) | SATISFIED (§10) + Decision (§9) | AEB §3 判定层级（VERIFIED/MATCH/SATISFIED）+ §5.1 ObservedAction + §7 AEC slots；被 VERIFIED 的授权工件承载 Grant |
| RAR authorization_details | type="capability" | Entailment (§6.1) | Decision (§9) | RFC 9396 format |
| Delegation chain | each DA narrows | Intersection (§7) | Decision (§9) | monotonic narrowing |

---

## Appendix B: Reference Vectors

**Grouping vs `kind` mapping**: The appendix groups vectors by semantic
category (B.1–B.6).  The machine-readable `vectors.json` uses a `kind`
field that collates these groups differently: `kind=entail (31)` covers
B.2 (6) + B.3 (21) plus the four scheme stress-test entail vectors;
`kind=decide (25)` covers B.5 (16, including the two revision vectors)
plus the seven combined vectors that call the decision function and the
two scheme stress-test decision vectors; `kind=intersect (14)` covers
B.4 (10) plus the four combined vectors that call the intersect function.

### B.1 Syntax (6 vectors)

| # | Input | Expected | Derivation |
|---|-------|----------|------------|
| S1 | `std/database-v1:query:SELECT` | valid | literal identifier |
| S2 | `std/database-v1:query:*` | valid | trailing wildcard |
| S3 | `*:query:SELECT` | deny | bare `*` illegal |
| S4 | `std/database-v1:query:SEL*` | deny | partial segment wildcard |
| S5 | `std/database-v1:query:{read,write}` | deny | alternation not v1 |
| S6 | `std/database-v1:query:[a-z]` | deny | character class not v1 |

### B.2 Entailment (6 vectors)

| # | Grant | Operation | Expected | Derivation |
|---|-------|-----------|----------|------------|
| E1 | `std/database-v1:query:SELECT` | `std/database-v1:query:SELECT` | allow | literal match |
| E2 | `std/database-v1:query:*` | `std/database-v1:query:SELECT` | allow | trailing wildcard |
| E3 | `std/database-v1:query:*` | `std/database-v1:query:SELECT:deep` | allow | wildcard multi-segment |
| E4 | `std/database-v1:query:*` | `std/database-v1:admin:DDL` | deny | different namespace |
| E5 | `std/database-v1:query:*` | `std/database-v1:query` | deny | no trailing segment |
| E6 | `std/database-v1:query:SELECT` | `std/database-v1:query:INSERT` | deny | literal mismatch |

### B.3 Params (21 vectors)

| # | Grant | Operation | Expected | Derivation |
|---|-------|-----------|----------|------------|
| P1 | `{"limit":100}` | `{"limit":50}` | allow | 50 ≤ 100 |
| P2 | `{"limit":100}` | `{"limit":150}` | deny | 150 > 100 |
| P3 | `{"tables":["a","b"]}` | `{"tables":["a"]}` | allow | subset |
| P4 | `{"tables":["a"]}` | `{"tables":["a","b"]}` | deny | "b" absent (`not_in_enum`) |
| P5 | `{"columns":{"t":["id"]}}` | `{"columns":{"t":["id","name"]}}` | deny | "name" absent (`not_in_enum`) |
| P6 | `{}` | `{"limit":50}` | allow | unconstrained |
| P7 | `{"tables":[]}` | `{"tables":["a"]}` | deny | explicit empty bound denies the class |
| P8 | `{"limit":100}` | `{"limit":null}` | deny | null invalid in v1 (`invalid_params_null`) |
| P9 | `{"station":[1,2,3]}` | `{"station":2}` | allow | scalar member of array set |
| P10 | `{"station":[1,2,3]}` | `{"station":9}` | deny | 9 ∉ allowed set (`not_in_enum`) |
| P11 | `{"station":[1,3]}` | `{"station":[1,3]}` | allow | array, every element a member |
| P12 | `{"station":[1,3]}` | `{"station":[1,2,3]}` | deny | 2 ∉ allowed set (`not_in_enum`) |
| P13 | `{"station":[1],"speed":0.3}` | `{"station":1,"speed":0.25}` | allow | member + number bound unaffected |
| P14 | `{"station":[3]}` | `{"station":2}` | deny | categorical: granting 3 does not cover 1/2 (`not_in_enum`) |
| P15 | `{"columns":{"t":["id","name"]}}` | `{"columns":{"t":["id"]}}` | allow | object recursion: request element is a member of the granted set (§6.2 v1.1) |
| P16 | `{"limit":100}` | raw `{"limit":100,"limit":150}` | deny(`invalid_params_duplicate_key`) | duplicate JSON key rejected at input normalization (§6.2 step 2) |
| P17 | `{"limit":100}` | raw `{"limit":1e400}` | deny(`invalid_params_number`) | non-finite number literal (§6.2 step 3) |
| P18 | `{"s":"x"}` | raw `{"s":"<600 chars>"}` | deny(`invalid_params_size`) | serialized form > 512 B (§6.2 step 4) |
| P19 | `{"d":0}` | raw depth-33 object | deny(`invalid_params_size`) | nesting beyond depth 32 (§6.2 step 4) |
| P20 | `{"s":"x"}` | raw `{"s":"<512 B>"}` | allow | serialized = exactly the 512 B limit (`≤`); positive boundary of P18 (§6.2 step 4) |
| P21 | `{"d":0}` | raw depth-32 object | allow | depth exactly the 32 limit (`≤`); positive boundary of P19 (§6.2 step 4) |

### B.4 Intersection (10 vectors)

Shorthand: params shown compact; constraints use colon notation.

| # | Source A | Source B | Expected | Derivation |
|---|---------|---------|----------|------------|
| I1 | `{"tables":["a","b"]}` | `{"tables":["a"]}` | `{"tables":["a"]}` | overlap |
| I2 | `{"tables":["a"]}` | `{"tables":[]}` | deny | deny-when-declared |
| I3 | (unconstrained) | (no grant) | deny | absent source |
| I4 | `{"limit":100}` | `{"limit":50}` | `{"limit":50}` | tighter bound |
| I5 | (unconstrained) | constraint `time:window:3600` | constraint applied | constraint added |
| I6 | `{"tables":["a"]}` | `{"tables":["b"]}` | deny | no overlap |
| I7 | (no source / `null`) | — | deny(`absent_source`) | zero sources: fail-closed (§7 rule 5) |
| I8 | `{"limit":50}` | `{}` | `{"limit":50}` | empty params declares no constraint → bound preserved (bounded then empty, §7 rule 6) |
| I9 | `{}` | `{"limit":50}` | `{"limit":50}` | source order must not matter (empty then bounded, §7 rule 6) |
| I10 | `{}`, id `query:SELECT` | `{}`, id `query:*` | `{}` | narrower identifier wins; identifier comparison is params-free (§7 rule 2) |

### B.5 Decision (16 vectors)

| # | Scenario | Expected | Derivation |
|---|---------|----------|------------|
| D1 | valid grant, valid op, constraints pass | allow | all checks pass |
| D2 | no matching grant | deny("capability_not_authorized") | fail-closed |
| D3 | unknown constraint type | deny("unknown_constraint") | fail-closed |
| D4 | malformed capability_id | deny("invalid_capability_id") | input validation |
| D5 | same input twice | same output | deterministic |
| D6 | constraint violation | deny("{type}:violated") | constraint fail |
| D7 | grant bounds a param, operation omits it | deny("params_missing") | §6.3 step 4 fail-closed |
| D8 | operation param value is `null` | deny("invalid_params_null") | §6.2 null rule; may carry `: <param>` detail (§9.4) |
| D9 | bounded grant, operation has **no `params` field at all** | deny("params_missing") | §6.3 step 4 fail-closed |
| D10 | `Authorize` called with an **absent/empty grant** | deny("capability_not_authorized") | §9 fail-closed, no exception |
| D11 | input declares CLC-1.0 against a CLC-1.1 implementation | allow | same major, 1.0 ≤ 1.1 → compatible (§12.1) |
| D12 | input declares CLC-2.0 against a CLC-1.1 implementation | deny("unsupported_language_revision") | different major → fail-closed (§12.1) |
| D13 | operation carries a param key the grant does not declare (key closure) | deny("undeclared_param") | §6.2 key closure, §9.3 layer 7 request side |
| D14 | both a missing grant key and an undeclared request key | deny("params_missing") | layer-7 order: missing before undeclared |
| D15 | absent/empty grant **and** absent operation | deny("capability_not_authorized") | §9.3 pre-check resolves before any layer, incl. the absent-operation case |
| D16 | grant valid, operation has **no `id`** | deny("missing_capability_id") | layer 1 |

### B.6 Combined (11 vectors)

| # | Scenario | Expected | Derivation |
|---|---------|----------|------------|
| C1 | wildcard grant + params within bounds | allow | E2 + P1 |
| C2 | wildcard grant + params exceed bounds | deny | E2 + P2 |
| C3 | intersection + constraint violation | deny | I4 + D6 |
| C4 | two-source intersection, both narrow | allow, narrowest | I1 + I4 |
| C5 | grant with empty constraint bound | deny | deny-when-declared |
| C6 | unknown scheme in grant | deny("unknown_constraint") | fail-closed |
| C7 | grant: `std/database-v1:query:*`, op: `std/database-v1:query:SELECT`, params mismatch | deny | E2 + P4 |
| C8 | three-source intersection, one absent | deny | I3 |
| C9 | valid grant + valid constraint + valid op | allow | D1 |
| C10 | malformed id in operation | deny("invalid_capability_id") | D4 |
| C11 | delegation chain, intermediate hop declares empty bound | deny | deny-when-declared propagates |

**Total: 83 vectors**

> The corpus additionally carries 6 scheme stress-test vectors
> (`clinical-001/-002`, `payments-001/-002`, `data-001/-002`) exercised
> against `std/{clinical,payments,data}-v1`: their enum/bound outcomes follow
> the grouping rules above (→ B.3 params semantics), and `payments-002`
> additionally exercises §8 fail-closed `unknown_constraint` for a
> scheme-scoped constraint type.  These vectors add no new normative rule;
> the v2 requirements evidence they record lives in design-notes §18.
> `undeclared-001/-002` (→ B.5 D13/D14) pin the §6.2 key-closure rule.
> `params-006`/`params-013` (→ B.3 P6/P13) close two previously-unmapped
> rows; `params-020/021` (→ P20/P21) are the positive boundary cases of
> `params-018/019`; `decide-016/017` (→ D15/D16) pin the §9.3 pre-check and
> layer-1 paths for absent/empty grant and id-less operation;
> `intersect-007..010` (→ I7..I10) pin §7 rules 5–6 including empty-params
> sources, order independence, and a params-free identifier comparison.

---

## Security Considerations

- **Fail-closed**: undefined/malformed/unknown → deny.
- **Deny-when-declared**: empty bounds deny the class.
- **No canonical broadening**: segment-boundary, not lexical prefix.
- **Delegation monotonicity**: capability shrinks along chain.
- **Stable reason codes**: same input → same reason across implementations.
- **Evidence binding is separate from native verification**: Match checks
  content correlation; native verification is the consumer's responsibility.
- **Parsing divergence must not change the decision**: params are
  normalized at the input boundary per §6.2 (JCS serialization, duplicate
  keys, non-finite/over-precision numbers, size/depth caps).  A consumer
  that decodes into a re-orderable map and re-encodes loses duplicate keys
  and cannot represent non-finite numbers; two such consumers would reach
  different verdicts on the same raw input.  Decisions are made on the
  boundary-validated form, not on a lossy re-serialization.
- **Reason-code detail suffix is diagnostic-only**: everything after the
  first `:` (e.g. the offending param name) MUST NOT change the verdict and
  MUST NOT be relied upon for decisions.  Consumers match on the code
  prefix before the `:` (§9.4).
- **Revision mismatch is fail-closed**: an incompatible language revision
  (§12.1) yields `deny("unsupported_language_revision")` resolved before
  any layer — never a silent downgrade or best-effort re-interpretation.
- **Resource exhaustion is bounded at the input boundary**: the 512-byte
  serialized-size cap and the depth-32 nesting cap (§6.2 step 4) apply to
  `raw_params` as much as to every other input, keeping recursive
  evaluators safe from deep-nesting and oversized-params blowup.

---

## References

- [ACA] draft-wei-agent-capability-authorization-00
- [AIC-JWT] draft-wei-aic-jwt-01
- [CAID] draft-schrock-canonical-action-identifier-02
- [EMILIA-AEB] draft-schrock-action-evidence-boundary-05
- [RFC8785] JCS: JSON Canonicalization Scheme
