<!-- Published copy in varwof/capability. Working draft and rationale live in the design repository; treat this copy as canonical once committed. -->

# Capability Language Core v1 (CLC-v1)

> **Preview** — Not for production use. APIs and features may change before official release.

**Category**: Experimental | **Status**: Working Draft | **Date**: 2026-09-10 | **Last amended**: 2026-09-13

## Abstract

This document defines the Capability Language Core (CLC), a minimal, executable
language for describing what an agent is authorized to do.  It defines the
capability identifier grammar, the entailment relation between a grant and an
operation, intersection of grants from multiple sources, the constraint model,
and a deterministic decision function with stable reason codes and a
three-valued verdict (`allow`, `deny`, `allow_unresolved`).

The language is carrier-neutral: it defines what is evaluated, not how it is
carried or trusted.  Trust models, native verification, execution lifecycle,
and receipt or token formats are out of scope (Section 11).  Conformance is
exercised by a published corpus of 105 vectors and 1184 property cases; three
implementations (Go, Python, TypeScript) that share an author pass both.
**Implementation conformance and this document's claim of a conformance class
are separate.**  An implementation conforms to CLC-A when it meets the
obligations Section 12 lists for that class, and it may claim that conformance on
its own, whatever other implementations exist.  Section 12 additionally sets a
maturity bar for *this document's* claim — two independent implementations
agreeing on verdict and reason — and that bar is met for CLC-A.  The evidence-side
class CLC-E is **not** claimed: its relations, value grammar, reference
implementation and corpus ship here, but that bar is not met yet.

### Revision History

(See the language-revision rule in §12.1 — this revision is incremental and readable compatibly.)

| Rev | Date | Scope | Change |
|-----|------|-------|--------|
| CLC-1.1 | 2026-09-10 | — | Baseline working draft |
| CLC-1.2 | 2026-09-12 | §7, §8.1, §8.4(new), §9, §9.2, §11, §12, Appendix B, Security | Residual-obligation channel `unresolved` (recognized-but-not-evaluated constraints carried explicitly, never silently dropped); `time:window` value grammar defined as a multi-segment UTC window array; recognition upgraded to a "type-name × value-grammar" double check with a new `invalid_constraint` reason code; the "time → intersection" merge rule demoted to v2; constraint merge normalized with deterministic ordering |
| CLC-1.3 | 2026-09-12 | §1, §6.2, §8.1, §8.4, §9, §9.1, Appendix B | Authorization loop tightened + constraint identity namespaced: `Decision.verdict` is three-valued (`allow`/`deny`/`allow_unresolved`), residual obligations no longer mixed into `allow` (kills the fail-closed break where a consumer judges only `verdict == allow`, §8.4); constraint identity becomes the `(scheme,type)` pair, the core recognizes only `max_rows`/`time`/`network` under `varwof/constraint-v1`, everything else → `unknown_constraint` (removes cross-scheme semantic pollution, §8.1); `time:window` value grammar tightened: a single segment must stay within one day (`start < end`), **no single segment may cross midnight** (a crossing must be split into two segments, `end:"00:00"` stays reserved as "next-day midnight"), segment list ascending, non-overlapping, ≤32; `params:{}` ≡ absent = no param constraint (entailment and intersection semantics agree); multi-grant aggregation made explicit (any-one-covers authorizes + residual union + deterministic deny reason, §9.1) |
| CLC-1.4 | 2026-09-13 | §6.2, §8.1, Appendix B | Operation-side value domain enforced: `max_rows` requests must carry a finite non-negative integer; anything else (string, boolean, negative, fractional, non-finite) → `max_rows:violated` instead of passing unchecked.  Size cap restated and implemented in **UTF-8 octets of the canonical serialization** in every path (decoded and raw); measuring code points or UTF-16 code units is non-conforming (the non-ASCII boundary vectors `params-028`/`params-029` pin it).  Evidence-side scope completed in the same working revision: the evidence-side value grammar (`varwof/evidence-v1:*`) and `CLC-REQUIREMENT-v1` are defined (§8.2, §10) and the evidence-side corpus ships (§12, `evidence-vectors.json`, 30 vectors, including ActionId/Match) — CLC-E is **implemented and pinned by a corpus but not claimed**, because the claim needs two independent implementations (§12, P12 of the principles document); genericity is exercised by `crosswalk-vectors.json` (13 vectors, both directions) |
| CLC-1.5 | 2026-09-14 | §4.2, §4.3, §6.4, §10, §11, §12, consumer table, Security | **Instance identity stops claiming CAID.**  The projection identity is the language's own (`clc-action:1:<type>:<suite>:<b64url>`), the v1 suite set is `jcs-sha256` only (the invented `jcs-sha384` is gone), and the text now says what a CAID is not: it covers the **complete** Action Object and identifies no occurrence, while this projection covers the declared material set and occurrence binding consumes a discriminator from the effect boundary.  §10 states the tri-state evaluation → binary report collapse (a top-level `unknown` MUST yield `UNSATISFIED`); §11 states that `allow_unresolved` is an authorization result and not evidence, and fixes the layering (CAID for material-action identity, AEC for evidence satisfaction, AEB for the boundary lifecycle); §12, the consumer table and Security Considerations no longer read a delegation chain as containment.  CLC-A's normative algorithm is unchanged and CLC-1.4 inputs stay readable.  **2026-09-14 review corrections to this revision** (text only): the acknowledgement now states which suites were re-run, for which revision; §12.1 declares CLC-1.5; the reason-ordering and reason-code sections are referenced as §9.1/§9.2 to match the rendered numbering; §9 states the grant-side pre-check precedence that Appendix D15 already pins; the abstract separates implementation conformance from this document's claim of a class; and the occurrence sentence names CAID-02 §4.5/§7. |

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
> P8 carriers separate from semantics · P9 local decidability ·
> P10 bounded work · P11 composition narrows only ·
> P12 ≥2 independent implementations

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
| **Verdict** | Outcome of evaluation: `allow`/`deny`/`allow_unresolved` (auth) or `SATISFIED`/`UNSATISFIED` (evidence). |
| **Decision** | Authorization-side verdict: `allow`, `allow_unresolved`, or `deny` + reason (+ additive `unresolved`). |
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

**Examples**: `std/database-v1:query:SELECT` valid | `database:query` invalid |
`std/database-v1:query:*` valid | `std/database-v1:query:SEL*` invalid

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
- `action_type`: the action type name declared by the relying-party-pinned type definition (the class this projection belongs to)
- `material_fields`: every field the type definition declares **material**
- `digest`: computed over the canonical **material projection** (below)

The material projection is deterministic and normative:
- The action type declares a **material field set** (required and
  optional-but-included).  Only that set enters the digest.
- Canonical serialization is the JSON Canonicalization Scheme (JCS) [RFC8785];
  the one suite defined in v1 is `jcs-sha256` (§4.3).
- The projection identity is the language's own, not a CAID:
  `clc-action:1:<type>:<suite>:<b64url>`.  A CAID [CAID] covers the **complete**
  Action Object under its own suite registry and identifies the action object,
  not an occurrence; this projection covers only the declared material set.  The
  two are related by a relying-party-pinned Action-Mapping Profile (§6.4), never
  by treating the strings as interchangeable.
- A field the type does not declare as material MUST be excluded from the
  digest and MUST NOT affect Match: an ObservedAction carrying undeclared
  fields is not invalidated, but those fields carry no action identity.
- A type-declared material field that is **missing** makes the
  ObservedAction non-matchable: coverage MUST NOT be inferred, defaulted,
  or repaired (`UNSATISFIED`, §10).  This is the evidence-side mirror of
  key closure (§6.2): the absence of a governing field is fail-closed,
  never fail-open.

The effect boundary MUST construct the ObservedAction from facts it
controls.  It MUST NOT copy a requester-supplied action digest without
deriving or checking the corresponding fact.

### 4.3 Identity

Two identity levels, corresponding to the two Action forms:

| Level | Identity | Scope | Example |
|-------|----------|-------|---------|
| Class | CapabilityId | Covers a class of actions | `std/database-v1:query:*` |
| Instance | ActionId (projection digest) | Identifies the material content of one action, **not** an occurrence | `clc-action:1:payment.release.1:jcs-sha256:...` |

A CapabilityId covers a class; an ActionId identifies the material content of one
action.  It does not identify an **occurrence**: ActionId binds the declared
material content, and correlation to a particular occurrence additionally requires
an occurrence discriminator defined and checked by the consuming profile.  CAID-02
Section 4.5 carries such a discriminator as the optional `occurrence_id` of an
action object; when a profile uses one, it MUST appear among the declared material
fields for it to affect the digest.  Allocating unique occurrences and proving
one-time consumption or execution stay outside both documents (CAID-02 Section 7).
Entailment checks class coverage; Match checks content binding.

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
| `std/database-v1:query:*` | `std/database-v1:query:SELECT` | yes: wildcard matches |
| `std/database-v1:query:*` | `std/database-v1:query:SELECT:deep` | yes: matches multi-segment |
| `std/database-v1:query:*` | `std/database-v1:admin:DDL` | no: different namespace |
| `std/database-v1:query:SELECT` | `std/database-v1:query:INSERT` | no: literal mismatch |

### 6.2 Parameters

| Type | Rule | Example |
|------|------|---------|
| number | op ≤ grant | 50 ≤ 100 (holds) |
| string | exact | "a" = "a" (holds) |
| boolean | exact | true = true (holds) |
| array | set of allowed values (enum): request scalar must equal a member; request array — every element must equal a member | `{"station":[1,2,3]}` ⊇ `2` (holds); ⊇ `9` (does not hold) |
| object | every grant key in op, values recurse | `{"t":["id"]}` ⊆ `{"t":["id","name"]}` (holds) |
| other | exact equality | — |

**Boolean parameters are exact only.** A boolean grant value is matched by
exact equality (`true` covers `true` only).  Booleans are **not** numbers: an
implementation MUST NOT interpret `true`/`false` as `1`/`0` and MUST NOT run
them through the numeric-bound rule (op ≤ grant).  They also play no role in
numeric comparisons or bounds.  (Boolean GRANT-side bounds are rare in
practice; the setting that matters — an operation-side boolean value under
key closure — is pinned by `undeclared-001`.)

Table rows map to vectors: number → `params-001`/`params-002`; array scalar
member → `params-009` (holds) / `params-010` (fails); array element-wise →
`params-011` (holds) / `params-012` (fails); object recursion allow → `params-015`,
deny-direction → `params-005`; categorical guard → `params-014`.
Under the old (pre-v1.1) array-as-bound rule the object example read (does not hold); with the
v1.1 enum rule the request-side element `id` is a member of the granted set, so
the row is (holds) (see `clc-v1-ambiguities.md` §2).

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

Grant with no params — or with an **empty `{}` params object** — covers any
operation params (unconstrained).  An absent `params` and `"params":{}` are
semantically equivalent — consistent across entailment (§6.3) and
intersection (§7 rule 6; §9.1).

A `null` parameter value is invalid in v1 → reject (`invalid_params_null`).
Absent ≠ explicitly empty (see §8).

**Key closure (Plan A).**  A bounded grant governs its declared keys: an
operation carrying a parameter key the grant does not declare is rejected →
`deny("undeclared_param")` (fail-closed, §9.1 layer 7 request side).  An
unconstrained grant (no `params`, or `params:{}`) accepts any operation
params, so no key closure applies there.  Within layer 7 the missing-key check
(`params_missing`) resolves **before** the undeclared-key check
(`undeclared_param`); both are key-level and run before the enum/bound value
checks (layers 8–9).

**Params representation and input normalization (v1.1).** Before any §9.1
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
   an object falls into the same code.  The digit count operates on the
   **JSON token as received** — the raw digit-character sequence at the input
   boundary, before it enters any storage / float / decimal representation —
   so float64 and decimal/bignum implementations MUST NOT diverge: the judged
   input is always the raw token text (`params-*` number probes in the corpus;
   near-limit forms such as `1.0000000000000001` extend the probes without
   changing the rule).
4. **Size and depth.** Params whose JCS-serialized form exceeds 512 **UTF-8 octets** (the canonical serialization is measured in octets — never in code points or UTF-16 code units; rev CLC-1.4)
   (octets of the canonical UTF-8 form), or whose nesting depth exceeds 32,
   are rejected:
   `deny("invalid_params_size")`.  Nesting depth counts **both** objects and
   arrays, with the outermost object as level 1 (31 nested arrays inside the
   top-level object therefore = depth 32).
5. **Order of checks.** Size/depth (4) precede duplicate keys (2), which
   precedes number shape (3); the first failing check wins.  All five run
   before §9.1 layer 1, so normalized params are the only view the layers see.
6. **Decoded-object path.** A caller that supplies params already decoded
   (no `raw_params` text) cannot reproduce the original byte stream; in
   that case the size check (4) applies to a **canonical serialization**
   (the JCS form of the decoded object: sorted keys, compact), and the
   depth check (4) applies to the decoded structure directly.
   Byte-exactness against a specific original text is guaranteed only for
   the raw path; but **both** entry points MUST reject the caps — an
   oversized/deep params object is denied whichever way it arrives.

### 6.3 Algorithm

```
Entails(G, O) → bool:
  1. G.namespace ≠ O.namespace → false      (namespace = scheme + action Class, §9.1 layer 3)
  2. G.id doesn't cover O.id → false        (path coverage, §9.1 layer 4)
  3. G.params absent (or `{}`) → true       (grant unconstrained — absent ≡ empty object)
  4. O.params absent → false                (bounded grant, request omits it → fail-closed)
  5. params_subset(O.params, G.params)      (both present → compare, §9.1 layers 5–9)
```

When more than one check fails, the reported reason follows the fixed
resolved-reason ordering of §9.1.  The remaining rules of this section
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
`invalid_params_null` (§9.1 layer 6) and is reported even when the
operation omits the `params` field entirely — i.e. layer 6 resolves
**before** step 4's `params_missing`.  This is the fixed §9.1 ordering; it
shadows the literal step order of the algorithm above, which lists presence
before the null checks.

### 6.4 Match (evidence binding)

Evidence E is bound to exact action A if:
1. E carries a valid ActionId in the language's projection form (`clc-action:1:…`,
   §4.3).  A CAID is a different object and relates to it only through a pinned
   Action-Mapping Profile.
2. E's ActionId equals the recomputed ActionId of the ObservedAction.
3. The ActionId was computed under the relying-party-pinned suite and
   definition source.

Match is content correlation only.  It does not validate a native
artifact and does not authorize execution.  It also does not identify an
occurrence: correlation to a particular occurrence additionally requires an
occurrence discriminator defined and checked by the consuming profile (CAID-02
Section 4.5), and a profile that uses one MUST pin how it is obtained and that the
language sees it among the declared material fields.

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
must give the same result — source order MUST NOT change the outcome
   (consistent with direct-grant `params:{} ≡ absent`, §6.3 step 3).

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
preserves across sources; it is pinned by `property-cases.json` (1184
cases, §12).

**Notation in this section**: params are JSON objects (e.g.
 `{"tables":["a"]}`); constraints use colon-notation triples (e.g.
 `varwof/constraint-v1:time:window:[{"start":"00:00","end":"01:00"}]`).  The example tables below use
compact shorthand for readability; each row shows the relevant params or
constraints only.

**Deny-when-declared**: `{"tables":[]}` (explicitly empty) = deny the class.
Omitted = scheme default.  A `null` value is invalid in v1 → reject
(`invalid_params_null`).  Canonicalization MUST NOT broaden (segment-boundary
comparison, not lexical prefix).

| Source A | Source B | Result |
|----------|----------|--------|
| `{"tables":["a","b"]}` | `{"tables":["a"]}` | `{"tables":["a"]}` (holds) |
| `{"tables":["a"]}` | `{"tables":[]}` | deny |
| (unconstrained) | (no grant) | deny |
| `{"limit":100}` | `{"limit":50}` | `{"limit":50}` (holds) |
| (unconstrained) | constraint `time:window:[{"start":"00:00","end":"01:00"}]` | recognized, not evaluated by core (→ `allow_unresolved` + `unresolved`) |
| `{"tables":["a"]}` | `{"tables":["b"]}` | deny |

**Object-value intersection requires identical key sets.**  Two object
values intersect key-by-key only when their key sets are the same; object
values with different key sets → `no_overlap` deny.  Merging "shared keys"
would drop the keys the other source constrains, so the result would not be
covered by that source (P11 composition narrows only): `{"a":1}` ∩ `{"b":1}`
→ deny(`no_overlap`); `{"a":1}` ∩ `{"a":2}` → deny; `{"a":1}` ∩ `{"a":1}` →
`{"a":1}`.

---

## 8. Constraint

Constraints are shared between authorization and evidence sides.

### 8.1 Authorization-side constraints

Limit how a capability may be used.  Constraints use colon-notation
triples: `scheme:type[:params]`, where **`type` is the second
`:`-delimited segment** (`scheme` `:` `type` [ `:` params... ]):

- `varwof/constraint-v1:max_rows:100` — type `max_rows`, param `100`
- `varwof/constraint-v1:time:window:[{"start":"00:00","end":"01:00"}]`
  — type `time`, param `window:` array of UTC window segments (a single
  window = a one-element array).  A scalar form (`time:window:3600`, the
  sliding-duration/freshness concept) is not a legal `time:window` value in
  v1 → `invalid_constraint`.
- `varwof/constraint-v1:network:cidr:["10.0.0.0/8"]` — type `network`, param
  `cidr:` JSON array (≤ 32 elements, each a legal IPv4/IPv6 CIDR string)

v1 core **recognizes constraints by `(scheme, type)` pair**, not by type
name alone: the identity of a constraint is **two** things — the declaring
scheme and the type.  The core recognizes exactly these pairs:

```
varwof/constraint-v1 : max_rows
varwof/constraint-v1 : time
varwof/constraint-v1 : network
```

Any other `(scheme, type)` — including `foo/database-v1:max_rows` — is
**not** core-recognized: it is rejected as `unknown_constraint` (fail-closed),
never handed to a core evaluator.  This kills cross-scheme semantic
pollution: the type name alone never selects an evaluator, so a scheme
that defines its own `max_rows` cannot have its semantics hijacked by
Core's `max_rows` evaluator (§P7 define once, consume everywhere — scoped
per declaring scheme).  Scheme-defined constraint types belong to the
v2 / profile layer (evaluated by the declaring scheme); core's
non-recognition of them is fail-closed (`unknown_constraint`).

A recognized constraint MUST also conform to that type's **value grammar**
(table below); a recognized type with a non-conforming value is rejected
as `invalid_constraint` — never silently skipped, never passed through.
Intersection itself neither evaluates nor validates constraint values (it
only merges constraint strings; the §8.1 value grammar is enforced at the
decision boundary, §9, and in the constraint merge rules below).

The core defines an evaluator for `max_rows` only; evaluation of
`time`/`network` bounds is the declaring capability scheme's
responsibility (the scheme evaluates, the core owns only what the §8.1
value grammar *is*, not whether a moment/address currently hits it; §11).
A recognized-but-unevaluated constraint is carried
on the decision's additive `unresolved` field — never silently dropped
(§8.4).  A non-recognized `(scheme,type)` → `deny("unknown_constraint")`
(fail-closed).

| type | value grammar (v1) | core behavior |
|------|--------------------|---------------|
| `max_rows` | strict non-negative integer (JSON number grammar: no leading `+`, no `0x`, no trailing characters) | evaluated against op params; the **operation-side value domain** is a finite non-negative integer — an absent param, a string, a boolean, a negative, a fractional or a non-finite value, or a value above the bound → `max_rows:violated` (cannot be shown conforming = fail-closed; rev CLC-1.4); constraint value out of grammar → `invalid_constraint` |
| `time` (`window`) | non-empty JSON array (≤ 32 elements), elements `{"start":"HH:MM[:SS]","end":"HH:MM[:SS]"}`, UTC, repeated daily, single window = one-element array; **a single segment must have `start < end` within one day (lexical time order)**, a single segment **must not cross midnight**; a crossing window must be split into two segments (`22:00→00:00` + `00:00→06:00`), where `end:"00:00"` is reserved as **next-day midnight** (i.e. segment end 24:00, requiring `start != end`); segment list ascending by (start,end), **segments non-overlapping** | recognized only → `allow_unresolved` + `unresolved` (§8.4) |
| `network` (`cidr`) | legal IPv4/IPv6 CIDR strings (`addr/mask`), syntax-level check only; JSON array ≤ 32 elements | recognized only → `allow_unresolved` + `unresolved` (§8.4) |

The expressible window set has no empty window and no full-day window; a
declaring scheme that needs such windows extends the grammar (§11).

Merge rules in v1: numeric → minimum wins; allowlist → intersection;
unknown → deny.  The allowlist is the
array-enum set (§6.2); intersecting it takes the shared members.  v1 core
defines **no denylist constraint** — merging applies only to the
`varwof/constraint-v1` types the core itself evaluates; it does not
define or merge scheme-defined types (§11).  Constraint-set merging is
always **normalized and deterministically ordered** (duplicate strings
collapsed, result ordered) — the same input yields the same constraint
sequence in any implementation.  v1 does not tighten `time`/`network`
bounds at intersection: intersection keeps only the constraint strings it
encounters (no evaluation, no tightening, §8.4).

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

### 8.4 Recognized but not evaluated (residual-obligation channel)

A recognized constraint whose value conforms to its §8.1 value grammar but
for which the v1 core defines **no evaluator** — v1: `time`, `network`;
evaluation belongs to the declaring scheme (§11) — MUST NOT be silently
dropped: it must appear
in the decision's additive `unresolved` list (§9), and the verdict must be
**`allow_unresolved`** (not `allow`):

```
Decision = { verdict: "allow"|"deny"|"allow_unresolved",
             reason, unresolved: string[] }
```

**Fail-closed boundary**: `allow_unresolved` is an **independent enum value**,
never equal to `allow`.  A consumer (PEP / profile / declaring scheme) MUST
evaluate or confirm every `unresolved` constraint before allowing;
**if it cannot execute or confirm, it MUST deny** (AAC §6.6: "when it cannot
perform or confirm, it should be treated as deny").  A consumer that only
writes `if decision.verdict == "allow"` cannot, on the literal enum, release
a residual obligation as an already-satisfied allow — a path that leaves
obligations unconfirmed must explicitly handle `allow_unresolved` to pass.
**"the caller is supposed to check unresolved" is not sufficient defense**:
the verdict itself must refuse the two-value short-circuit.

`unresolved` semantics and ordering: `[]` for `deny` and for fully evaluated
`allow`; for `allow_unresolved` the normalized + sorted constraint strings
(duplicates folded, result ordered) — the order is deterministic: the same
input yields the same sequence in any implementation.

**Combined obligations (consumer side)**: multiple `unresolved` constraints
of the same `(scheme,type)` form a conjunction (AND) — satisfying A and B
satisfies all; OR, any-one, first-wins, and ignoring some entries are all
**forbidden**.  Constraints of different `(scheme,type)` do not interact;
each evaluates under its own declaring scheme (P11 composition narrows only:
conjunction only narrows).

The core owns only the **value grammar** ("what it is"); "whether this
window/CIDR currently forms a boundary" ("how to evaluate") belongs to the
declaring scheme (§11) — but the **boundary-moment semantics are part of the
grammar** (§8.1: half-open `[start, end)`, single segment within one day,
crossing split into segments), and a scheme MUST NOT change that
interpretation, only evaluate on top of it.

---

## 9. Decision Function (Authorization Side)

```
Authorize(grants, operation) → Decision
Decision = { verdict: "allow"|"deny"|"allow_unresolved",
             reason: string|null,
             unresolved: string[] }   // additive, §8.4
```

Algorithm.  One precedence rule governs the whole function: **the grant-side
pre-check resolves before operation validation.**  An absent or empty grant set
denies with `capability_not_authorized` even when the operation is absent as well
(§9.1 layer 10; Appendix D15 pins it), so a caller that passes neither input gets
that reason and not `missing_capability_id`.
1. Validate operation: missing/invalid id → deny with stable reason.  The
   operation's **specific layer-1 code** is reported — `missing_capability_id`
   (no id), `unsupported_wildcard` (v1-forbidden wildcard shape) or
   `invalid_capability_id` (other grammar violation) — and is **not**
   collapsed to a generic code.
2. Find covering grants via Entailment (§6.1).  Zero/empty `grants` → directly
   `deny("capability_not_authorized")` (§9.1 layer 10).
3. For each covering grant: evaluate constraints (§8.1): non-recognized
   `(scheme,type)` → `unknown_constraint`; recognized but non-conforming
   value → `invalid_constraint`; recognized with a core evaluator
   (`varwof/constraint-v1:max_rows`) and violated →
   `{type}:violated`; recognized without a core evaluator (`time`,
   `network`) → residual obligation (§8.4).
4. **Aggregate** (multi-grant set, §9.1):
   - Any covering grant that "allows" (no params/constraint rejection) →
     overall allow;
   - Residual obligations = the `unresolved` **union across all covering and
     allowing grants** (normalized + sorted, obligations of any covering grant
     are never dropped);
   - When no covering grant allows: if at least one covering grant rejects at
     the params/constraint layer → use the rejection reason of the **first
     covering grant in canonical order** (deterministic, §9.1); if no grant
     covers at all → `capability_not_authorized`.
5. Allow with non-empty residual obligations → `verdict = allow_unresolved`;
   allow with empty obligations → `verdict = allow`.

The grant set may be **absent or empty** — e.g. an integrator
calls `Authorize` with no grant value or with an empty capability record.
A safe evaluator MUST NOT raise; it MUST resolve such input to
`deny("capability_not_authorized")` (falling out of layer 10/step 2).
An absent operation resolves to `deny("missing_capability_id")`
(layer 1); the evaluator MUST NOT raise there either.

Properties: deterministic (same input → same output), fail-closed,
stable reason codes.

### 9.1 Resolved Reason Ordering (normative)

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
| 5 | Explicit empty bound | Any grant/intersection source declares a **parameter value** that is `[]`/`{}` (a present-but-empty `params` object is *no* constraint, §7 rule 6) | `empty_bound_denies_class` |
| 6 | Null values | Any `null` parameter value | `invalid_params_null` |
| 7 | Param presence | Grant bounds a param the operation omits (or operation has no `params`); operation carries a key the grant does not declare | `params_missing`, `undeclared_param` |
| 8 | Enum membership | Request value not a member of a granted array set (§6.2) | `not_in_enum` |
| 9 | Bound comparison | Numeric/bound exceeded | `params_exceed_grant` |
| 10 | Coverage emptiness | Intersection result empty; zero sources; no grant covers the operation | `no_overlap`, `absent_source`, `capability_not_authorized` |
| 11 | Constraint evaluation | Non-recognized `(scheme,type)`; recognized type value out of §8.1 grammar; recognized type violated | `unknown_constraint`, `invalid_constraint`, `{type}:violated` |

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
- **`params:{}` ≡ absent**: the params constraint looks only at the
   **set of declared param names**, independent of carrier form — an absent
   `params` and `"params":{}` both mean "no param names declared" =
   **no param constraint** (consistent across entailment and intersection;
   the same representation cannot have different semantics in different
   functions).  Therefore:
  - Direct grant: a grant with `params:{}` **allows** an op carrying any
    params (`.{x:1}` does not trigger `undeclared_param`);
  - Intersection: a `params:{}` source **contributes no param constraint**
    (`{limit:50}` ∩ `{}` = `{limit:50}`);
  - Key closure (next bullet) applies only when the grant declares a
    **non-empty** set of param names.
- **Layer 7 key closure runs both directions**: granted keys must be present
  in the operation (`params_missing`) and operation keys must be declared by
  the grant (`undeclared_param`); the missing-key check resolves first, and
  both precede the layer 8–9 value checks.  (Applies only to a non-empty set
of declared names, see the bullet above.)
- **Layer 11 runs last by construction**: constraints are evaluated only
  after coverage and parameters pass.
- **Multi-grant aggregation (normative)**: `Authorize` operates on a
  **ordered list of grants**, not a single grant.  Authorization semantics are
  order-independent; only reason selection (rule 4) uses the input order.  Rules:
  1. **Any one covering-and-allowing grant allows** (∃ `g`: Entails(g,op) ∧
     no params-layer rejection ∧ no constraint-layer rejection);
  2. Residual obligations = `unresolved` **union across all covering and
     allowing grants** (normalized + sorted); the obligations of any covering
     grant are never dropped;
  3. No grant covers → `capability_not_authorized`; op layer-1 errors always
     precede any coverage/aggregation decision;
  4. Some grant covers but all covering grants reject at the params/constraint
     layer → deny, reason = the layer 5–11 rejection reason of the **first
     covering grant in canonical order** (deterministic).
  **Canonical order** = the appearance order in the input grant list (the
  capability-record body order); an implementation MUST NOT choose the reason
  by internal hash/iteration order.
  Counter-examples pinned (forbidden): NOT any-one-allows — otherwise, with
  multiple grants held, a narrow grant would wrongly deny the legal operation
  of a broad grant; NOT first-match-wins — otherwise grant order would
  change the authorization outcome; NOT all-must-pass — synonymous with
  "any-one-covers authorizes", letting a narrow grant's existence invalidate a
  broad grant.
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

### 9.2 Reason Codes (normative)

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
| `invalid_params_duplicate_key` | Params contain a duplicate JSON key (§6.2 representation, §9.1 layer 2) |
| `invalid_params_number` | A numeric param is non-finite or over-precision (> 17 significant decimal digits) (§6.2 representation, §9.1 layer 2) |
| `invalid_params_size` | Params exceed the 512-byte serialized size or the depth-32 nesting limit (§6.2 representation, §9.1 layer 2) |
| `different_namespace` | Grant and operation differ in namespace (scheme + action Class, §9.1 layer 3) |
| `literal_mismatch` | Literal identifiers differ |
| `wildcard_requires_trailing_segment` | Wildcard has no remaining segment (`...:*` does not cover `...`) |
| `capability_not_authorized` | No grant in the effective set covers the operation |
| `no_overlap` | Intersection of multiple sources is empty |
| `absent_source` | Intersection over zero sources — no effective set (§7 rule 5) |
| `params_exceed_grant` | Request parameters exceed the granted bound |
| `params_missing` | Grant bounds a parameter but the request omits it, or the request has no `params` field at all (fail-closed, §6.3 step 4) |
| `undeclared_param` | Operation parameter key not declared by the grant's params (key closure, §6.2; §9.1 layer 7 request side) |
| `empty_bound_denies_class` | An explicitly empty bound at a parameter value (`[]`/`{}`) denies the class.  `params:{}` is not an empty bound: it is equivalent to an absent `params` (§7 rule 6) |
| `not_in_enum` | Request value is not a member of the allowed set granted as an array (§6.2 enum rule) |
| `invalid_params_null` | `null` parameter value (rejected in v1) |
| `unsupported_language_revision` | Declared CLC revision is incompatible with the implementation (§12.1; fails closed, no silent downgrade) |
| `unknown_constraint` | Unknown constraint type (fail-closed) |
| `invalid_constraint` | Recognized type whose value fails its §8.1 value grammar |
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
4. Evaluate freshness, consumption, and role constraints.  The evidence-side
   value grammar is defined in this revision: `varwof/evidence-v1:freshness:sec:<n>`,
   `:consumption:once`, `:quorum:distinct:<n>`, `:exclusion:initiator|executor`
   (§8.2).  A recognized constraint whose evaluation belongs to the enforcement
   point (consumption) yields an unresolved obligation, never `SATISFIED`.
5. All required roles filled and bound → `SATISFIED`.
6. Any role unfilled, unbound, or violated → `UNSATISFIED`.

**Tri-state evaluation, binary report.**  A recognized evidence-side constraint
is evaluated three-valued (`satisfied` / `violated` / `unknown`).  `Satisfaction`
itself is binary.  A constraint that evaluates to `unknown` at the top level —
including one whose evaluation belongs to the enforcement point (`consumption`) —
MUST produce `UNSATISFIED` with a stable reason, never `SATISFIED`.  `unknown`
is an internal evaluation result, not a third top-level verdict.

Properties: deterministic, fail-closed, stable reason codes.

---

## 11. Semantic Boundary

CLC-v1 defines the **shared minimal vocabulary** and **evaluation
algorithms** for both authorization and evidence.

CLC-v1 does NOT define:
- **Trust models**: who signs what, issuer trust, delegation chains
  (belongs to AIC-JWT [AIC-JWT], OAuth, SPIFFE, etc.)
- **Native verification**: signature checking, schema validation,
  freshness enforcement (belongs to each native artifact's spec)
- **Execution lifecycle**: consumption, invocation, reconciliation,
  outcome classification (belongs to EMILIA AEB [EMILIA-AEB] or equivalent)
- **Receipt or token formats**: the wire formats for carrying grants,
  evidence, or bindings (belongs to protocol-specific specs)

The boundary is:
- CLC-v1 defines **what** to evaluate (grant ⊆ operation, evidence ↔ action)
- Consumers define **how** to evaluate (native verification, trust anchors)
- CLC-v1 defines **what** the output means (allow/deny/allow_unresolved,
  SATISFIED/UNSATISFIED) — **`allow` and `allow_unresolved` are distinct
  enum values**; a consumer MUST NOT treat `allow_unresolved` as `allow`
  (§8.4)
- Consumers define **what to do** with the output (invoke, record, reconcile)
- CLC-v1 defines each known type's **value grammar** (what counts as a legal
  constraint value); the declaring scheme defines **how** that value is
  evaluated (whether this window/CIDR currently forms a boundary)
- **`allow_unresolved` is an authorization result, not evidence.**  It marks an
  unresolved authorization (or policy) condition.  A consumer that can evaluate
  the obligation under a pinned rule may release it; one that cannot MUST refuse.
  It takes on an evidence role only where a relying party separately defines one
  together with the native verifier for it (AEB); the language itself makes no
  such claim, and `unresolved` MUST NOT be read as "evidence still required"
- CLC-A stays the **scope language**: material-action identity is referenced from
  CAID, evidence satisfaction from AEC, and the boundary lifecycle from AEB; the
  narrow crosswalk between them is the composition point

---

## 12. Conformance

CLC-v1 defines **two conformance classes**:

**CLC-A (authorization side)** — the v1 baseline. A conforming
implementation MUST implement: grammar (§3), entailment (§6.1),
intersection (§7), decision function (§9), rejection of non-recognized
`(scheme,type)` constraints (`unknown_constraint`, §8.1), rejection of
non-conforming recognized-type values (`invalid_constraint`, §8.1),
exposure of recognized-but-unevaluated constraints via the decision's
`unresolved` field on an independent `allow_unresolved` verdict (never
silently dropped, §8.4), multi-grant aggregation (§9.1), and stable
reason codes (§9.2).

**Delegation narrowing is not part of this revision.**  A delegation policy may require that the constraint set an agent requests lies inside the principal's boundary, and that the delegation record carry the effective subset.  That obligation belongs to the delegation/authorization binding profile, not to the language: this revision defines neither a conformance class nor a reason code for it, and implementations must not infer one.  A future revision may add it as **one reusable containment relation with a shared corpus**, alongside entailment and intersection, once the profile that requires it is settled.  Delegation stays out of CLC-A until that relation exists: the delegation examples in this document and in the crosswalk corpus demonstrate an **intersection of the declared grant sets**, which is not a proof that a child grant remains inside its parent's authorization boundary.  An operation fitting a grant proves nothing about a child staying inside its parent, and where containment cannot be established a binding profile MUST NOT authorize the delegation.

**CLC-E (evidence side)** — optional conformance profile, **implemented and
pinned by a corpus in this revision, but NOT claimed**.  §6.4 (match) and §10
(satisfaction) define the evidence-side relations; this revision also defines the
evidence-side constraint value grammar (`varwof/evidence-v1:freshness:sec:<n>`,
`:consumption:once`, `:quorum:distinct:<n>`, `:exclusion:initiator|executor`) and
ships a reference implementation and a corpus.

The class is withheld **on principle, not for lack of material**: agreement is
the bar, and the bar is two *independent* implementations (§12 of the principles
document, P12; §12 here, "Independence of implementations").  Parity between
implementations that share an author does not meet it.  A second precondition is
stewardship: the evidence-side semantics are the subject of joint review with
EMILIA, so no claim is made ahead of that review.

A future revision that claims CLC-E would carry these obligations, and an
implementation that claims it today MUST:

* evaluate the four evidence-side types over eligible evidence facts, returning
  a three-valued result (`satisfied` / `violated` / `unknown`) where `unknown` is
  never read as satisfied, and report a recognized constraint whose evaluation
  belongs to the enforcement point (`consumption`) as `unknown` rather than
  satisfied;
* take eligibility from integrity-protected native results only: a fact that did
  not reach VERIFIED, or whose protected subject identifier is absent, MUST NOT
  be counted for quorum or exclusion;
* implement instance identity and binding (§4.2/§6.4): an ActionId is the digest
  of the JCS canonical serialization of the **declared material projection**, an
  undeclared field MUST NOT affect it, a missing declared material field makes the
  action non-matchable (never inferred or defaulted), and a comparison across
  suites or action types is INDETERMINATE — a mapping problem, never a match —
  unless a relying-party-pinned Action-Mapping Profile projects it;
* implement `CLC-REQUIREMENT-v1` as a **closed** object (an undefined member is
  rejected) whose expression uses the bounded grammar — `AND`/`OR` with equal
  binding strength, evaluated strictly left to right, parentheses as the only
  precedence mechanism — and treat an identifier with no eligible component as
  false;
* take the requirement from relying-party configuration: a requirement supplied
  by the presenter MUST NOT be accepted or weakened;
* pass `evidence-vectors.json` (§12 conformance corpora).

An implementation that implements only CLC-A MUST NOT claim CLC-E.  CLC-E does
not add a wire format: carriers that need one (e.g. an Action Evidence Envelope)
profile §6.4/§10 themselves.

**Conformance corpora.**  CLC-A conformance is exercised by two
machine-readable reference suites shipped at
`capability/data/_vectors/clc-v1/`: `vectors.json` — 105 vectors mapped
to Appendix B — and `property-cases.json` — 1184 cases pinning the §7
meet-law, identifier narrowing and source-order independence.  Their
syntax is defined by `vectors.schema.json`; `offline-vectors.json` is a
timestamped snapshot mirror.  A conforming implementation MUST pass both
suites.

**Genericity is exercised, not asserted.**  `crosswalk-vectors.json` in the same
directory carries 13 vectors in both directions: 5 that project a CLC decision
into the members an AEB crossing record asks of a native source (the members CLC
can establish, and the ones it explicitly does not), and 8 that map four foreign
capability representations —
OAuth RAR `authorization_details`, an AIC-JWT delegation authorization, an
Action Evidence Graph capability class, a UCAN `{with, can}` capability, and a
delegation chain — into CLC grants through pinned cross-walk profiles and assert
the decision the unchanged core reaches.  A profile is a few lines of mapping
written by whoever owns the foreign format; the core is not modified for any of
them.

The evidence side ships `evidence-vectors.json` in the same directory — 30 vectors covering the four evidence-side constraint types, their
value-grammar rejections, requirement-expression binding, the closed requirement
object, ActionId computation (§4.2: declared material projection, undeclared
fields excluded, missing material field non-matchable, suite-tagged identifiers)
and Match verdicts (§6.4: `MATCH` / `NOT_EQUIVALENT` / `INDETERMINATE`).  Its
runner ships with the reference implementation (`register`), and its syntax
mirrors `vectors.json`.

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
this revision rejects as `unsupported_wildcard` (§9.2).  It is not a CLC-A
implementation and MUST NOT be cited as one; it exists to study WIT/WPT
provisioning and carries its own EXPERIMENTAL banner.

### 12.1 Language Revision

Every implementation declares a language revision `CLC-<major>.<minor>` —
this document declares **`CLC-1.5`**.  A capability input (grant,
operation, or OCM) SHOULD carry the revision it was authored against; an
input without a declared revision is treated as `CLC-1.0`.

- **Compatible reading**: an implementation MAY evaluate an input whose
  declared major equals its own AND whose declared minor is ≤ its own
  (so an implementation of CLC-1.3 reads a CLC-1.0/1.1/1.2/1.3
  input, but not CLC-1.4 or CLC-2.0).
- **CLC-1.2 is additive**: it adds the `unresolved` field to the Decision
  shape and the `invalid_constraint` reason code without changing v1
  verdicts on existing inputs; a CLC-1.1 implementation MAY claim CLC-1.1
  against this document but is not CLC-A conformant (§12) until it exposes
  `unresolved` and rejects non-conforming recognized-type values.
- **CLC-1.3 is additive, with one verdict value re-scoped**: it adds the
  `allow_unresolved` verdict value, closes the decision loop for residual
  obligations, and re-scopes `allow` to mean "fully enforced" only;
  `allow`/`deny` outputs on inputs with **no** residual obligations do not
  change.  A CLC-1.2 implementation MAY claim CLC-1.2 against this document
  but is not CLC-A conformant (§12) until it emits the `allow_unresolved`
  value and applies the §8.1 `(scheme,type)` identity and cross-midnight
  window grammar.

- **Incompatible reading MUST fail closed** with
  `deny("unsupported_language_revision")`.  An implementation MUST NOT
  silently evaluate under a different revision — no downgrade, no
  warning-then-allow.
- The revision check resolves **before any §9.1 layer** and yields the
  single resolved reason code `unsupported_language_revision`.

Vectors: `revision-001` (input CLC-1.0 against an implementation declaring
CLC-1.3 → eval normally, allow); `revision-002` (input CLC-2.0 → deny
`unsupported_language_revision`).

---

## Appendix A: Consumption Mapping

The rows below are examples of consumers of this shared vocabulary, not
required profiles: conformance to CLC-A does not depend on any of them.

| Consumer | Grammar | Binding | Verdict | Notes |
|----------|---------|---------|---------|-------|
| AIC-JWT DA | capability[].id | Entailment (§6.1) | Decision (§9) | AIC-JWT §5 binding |
| EMILIA AEB | AEG capability_class | Match (§6.4) + Entailment (§6.1) | SATISFIED (§10) + Decision (§9) | AEB §3 decision levels (VERIFIED/MATCH/SATISFIED) + §5.1 ObservedAction + §7 AEC slots; a VERIFIED authorization artifact carries the Grant |
| RAR authorization_details | type="capability" | Entailment (§6.1) | Decision (§9) | RFC 9396 format |
| Delegation chain | each hop's declared set | Intersection (§7) | Decision (§9) | intersection over declared sets only; containment is out of scope (§12) |

---

## Appendix B: Reference Vectors

**Grouping vs `kind` mapping**: The appendix groups vectors by semantic
category (B.1–B.6).  The machine-readable `vectors.json` uses a `kind`
field that collates these groups differently:
`kind=entail (37)` covers B.2 (6) + B.3 (27) plus the four scheme
stress-test entail vectors (`clinical-001/-002`, `payments-001`,
`data-002`); `kind=decide (38)` covers the B.5 rows below (29: the 25
`decide-*` ids, the two `revision-*` vectors and the two `undeclared-*`
layer-7 vectors, including the nine residual/value-grammar decision
vectors, the re-pinned `decide-019/-020/-024` and the added
`decide-028/-029/-030`) plus the seven combined decision vectors,
`payments-002` and `data-001`;
`kind=intersect (14)` covers B.4 (10) plus the four combined vectors that
call the intersect function (`combined-004/-005/-008/-011`).

### B.1 Syntax (9 vectors)

| # | Input | Expected | Derivation |
|---|-------|----------|------------|
| S1 | `std/database-v1:query:SELECT` | valid | literal identifier |
| S2 | `std/database-v1:query:*` | valid | trailing wildcard |
| S3 | `*:query:SELECT` | deny | bare `*` illegal |
| S4 | `std/database-v1:query:SEL*` | deny | partial segment wildcard |
| S5 | `std/database-v1:query:{read,write}` | deny | alternation not v1 |
| S6 | `std/database-v1:query:[a-z]` | deny | character class not v1 |
| S7 | `database:query` | deny(`invalid_capability_id`) | §3 scheme grammar: no vendor `"/"` product `"-v"` major (the spec's own counter-example) |
| S8 | `bad:op` | deny(`invalid_capability_id`) | §3 scheme grammar: scheme `bad` does not match vendor/product-vN (snips the lax-intake hole) |
| S9 | `std/data-v1:fetch:item:42` | valid | multi-segment action + conforming scheme (positive boundary) |

### B.2 Entailment (6 vectors)

| # | Grant | Operation | Expected | Derivation |
|---|-------|-----------|----------|------------|
| E1 | `std/database-v1:query:SELECT` | `std/database-v1:query:SELECT` | allow | literal match |
| E2 | `std/database-v1:query:*` | `std/database-v1:query:SELECT` | allow | trailing wildcard |
| E3 | `std/database-v1:query:*` | `std/database-v1:query:SELECT:deep` | allow | wildcard multi-segment |
| E4 | `std/database-v1:query:*` | `std/database-v1:admin:DDL` | deny | different namespace |
| E5 | `std/database-v1:query:*` | `std/database-v1:query` | deny | no trailing segment |
| E6 | `std/database-v1:query:SELECT` | `std/database-v1:query:INSERT` | deny | literal mismatch |

### B.3 Params (27 vectors)

| # | Grant | Operation | Expected | Derivation |
|---|-------|-----------|----------|------------|
| P1 | `{"limit":100}` | `{"limit":50}` | allow | 50 ≤ 100 |
| P2 | `{"limit":100}` | `{"limit":150}` | deny | 150 > 100 |
| P3 | `{"tables":["a","b"]}` | `{"tables":["a"]}` | allow | subset |
| P4 | `{"tables":["a"]}` | `{"tables":["a","b"]}` | deny | "b" absent (`not_in_enum`) |
| P5 | `{"columns":{"t":["id"]}}` | `{"columns":{"t":["id","name"]}}` | deny | "name" absent (`not_in_enum`) |
| P6 | `{}` | `{"limit":50}` | allow | unconstrained (`{}` ≡ absent; the literal `{}` is pinned by `decide-028`, `params-006` pins the absent form) |
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
| P22 | `{"flag":true}` | `{"flag":1}` | deny(`params_exceed_grant`) | boolean is exact and is NOT a number: `1` must not satisfy a granted `true` (`params-022`) |
| P23 | `{"flag":true}` | `{"flag":true}` | allow | positive side of P22 (`params-023`) |
| P24 | `{"x":null}` | (no params) | deny(`invalid_params_null`) | layer 6 (null) precedes layer 7 (presence) (`params-024`) |
| P25 | `{"s":"x"}` | raw `{"s":"<512 B>","s":"dup"}` | deny(`invalid_params_size`) | multi-fault: size (4) precedes duplicate keys (2) (`params-025`) |
| P26 | `{"s":"x"}` | raw `{"n":1e400,"s":"<512 B>"}` | deny(`invalid_params_size`) | multi-fault: size (4) precedes number shape (3) (`params-026`) |
| P27 | `{"a":1}` | raw `{"a":1,"a":2,"n":1e400}` | deny(`invalid_params_duplicate_key`) | multi-fault under the size limit: duplicate keys (2) precede number shape (3) (`params-027`) |

### B.4 Intersection (10 vectors)

Shorthand: params shown compact; constraints use colon notation.

| # | Source A | Source B | Expected | Derivation |
|---|---------|---------|----------|------------|
| I1 | `{"tables":["a","b"]}` | `{"tables":["a"]}` | `{"tables":["a"]}` | overlap |
| I2 | `{"tables":["a"]}` | `{"tables":[]}` | deny | deny-when-declared |
| I3 | (unconstrained) | (no grant) | deny | absent source |
| I4 | `{"limit":100}` | `{"limit":50}` | `{"limit":50}` | tighter bound |
| I5 | (unconstrained) | constraint `time:window:[{"start":"00:00","end":"01:00"}]` | recognized, not evaluated → `unresolved` carried on `allow_unresolved` verdict | constraint added |
| I6 | `{"tables":["a"]}` | `{"tables":["b"]}` | deny | no overlap |
| I7 | (no source / `null`) | — | deny(`absent_source`) | zero sources: fail-closed (§7 rule 5) |
| I8 | `{"limit":50}` | `{}` | `{"limit":50}` | empty params declares no constraint → bound preserved (bounded then empty, §7 rule 6) |
| I9 | `{}` | `{"limit":50}` | `{"limit":50}` | source order must not matter (empty then bounded, §7 rule 6) |
| I10 | `{}`, id `query:SELECT` | `{}`, id `query:*` | `{}` | narrower identifier wins; identifier comparison is params-free (§7 rule 2) |

### B.5 Decision (29 vectors)

| # | Scenario | Expected | Derivation |
|---|---------|----------|------------|
| D1 | valid grant, valid op, constraints pass | allow | all checks pass |
| D2 | no matching grant | deny("capability_not_authorized") | fail-closed |
| D3 | unknown constraint type | deny("unknown_constraint") | fail-closed |
| D4 | malformed capability_id | deny("invalid_capability_id") | input validation |
| D5 | same input twice | same output | deterministic |
| D6 | constraint violation | deny("{type}:violated") | constraint fail |
| D7 | grant bounds a param, operation omits it | deny("params_missing") | §6.3 step 4 fail-closed |
| D8 | operation param value is `null` | deny("invalid_params_null") | §6.2 null rule; may carry `: <param>` detail (§9.2) |
| D9 | bounded grant, operation has **no `params` field at all** | deny("params_missing") | §6.3 step 4 fail-closed |
| D10 | `Authorize` called with an **absent/empty grant** | deny("capability_not_authorized") | §9 fail-closed, no exception |
| D11 | input declares CLC-1.0 against a CLC-1.3 implementation | allow | same major, 1.0 ≤ 1.3 → compatible (§12.1) |
| D12 | input declares CLC-2.0 against a CLC-1.3 implementation | deny("unsupported_language_revision") | different major → fail-closed (§12.1) |
| D13 | operation carries a param key the grant does not declare (key closure) | deny("undeclared_param") | §6.2 key closure, §9.1 layer 7 request side |
| D14 | both a missing grant key and an undeclared request key | deny("params_missing") | layer-7 order: missing before undeclared |
| D15 | absent/empty grant **and** absent operation | deny("capability_not_authorized") | §9.1 pre-check resolves before any layer, incl. the absent-operation case |
| D16 | grant valid, operation has **no `id`** | deny("missing_capability_id") | layer 1 |
| D17 | grant carries `time:window` with a **cross-midnight single segment** (`22:00→06:00`) | deny("invalid_constraint") | a single segment crossing midnight is out of grammar (`decide-019`) — a crossing must be split into two segments |
| D18 | grant carries `network:cidr` (array form, IPv4/IPv6) | `allow_unresolved`, `unresolved:[<constraint>]` | recognized, no core evaluator → residual obligation (§8.4; `decide-020`) |
| D19 | `time:window` scalar second form (`window:3600`) | deny("invalid_constraint") | out of §8.1 value grammar (`decide-021`) |
| D20 | `network:cidr` without prefix length | deny("invalid_constraint") | out of §8.1 value grammar (`decide-022`) |
| D21 | `max_rows` constraint, op carries **no** `max_rows` value | deny("max_rows:violated") | fail-closed op-absent (`decide-023`) |
| D22 | `time:window` split-form multi-segment window (`22:00→00:00` + `00:00→06:00`) | `allow_unresolved`, `unresolved:[<constraint>]` | cross-midnight split-segment grammar (`decide-024`) |
| D23 | op scheme `bad` passes no vendor/product-vN | deny("invalid_capability_id") | §3 scheme grammar (`decide-025`) |
| D24 | grant id `bad:op` against a valid operation | deny("capability_not_authorized") | §3 fails in Entails; ID-level reason collapses (`decide-026`) |
| D25 | `max_rows` exactly at the bound | allow | violation is strict `>`; core-evaluated so no unresolved (`decide-027`) |
| D26 | grant `params:{}`, op any params → unconstrained | allow | `{}` ≡ absent (`decide-028`, §9.1) |
| D27 | multi-grant: G1 `{limit:10}` denies, G2 `{limit:100}` allows | allow | any-one-covers authorizes (`decide-029`, §9.1) |
| D28 | multi-grant: G1 `{limit:10}` + G2 `{limit:6}`, op `{limit:50}` | deny("params_exceed_grant") | all covering grants reject → first reason in canonical order (`decide-030`, §9.1) |

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

**Total: 105 vectors**

> Decisions D17–D28 are the corpus pin for the
> residual-obligation channel `unresolved` / `allow_unresolved`, the §8.1
> `(scheme,type)` identity, the `invalid_constraint` value grammar and the
> §9.1 multi-grant aggregation.  `decide-025/-026` and `syntax-007/-008`
> pin the §3 scheme grammar; `decide-021/-022`, `decide-019/-024` pin §8.1
> time/network value shapes; `decide-019` pins the no-cross-midnight rule;
> `decide-028/-029/-030` pin §9.1 (`{}`≡absent, any-allow union, deterministic
> deny reason).

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
> `params-018/019`; `decide-016/017` (→ D15/D16) pin the §9.1 pre-check and
> layer-1 paths for absent/empty grant and id-less operation;
> `intersect-007..010` (→ I7..I10) pin §7 rules 5–6 including empty-params
> sources, order independence, and a params-free identifier comparison.

---

## Security Considerations

- **Fail-closed**: undefined/malformed/unknown → deny.
- **Deny-when-declared**: empty bounds deny the class.
- **No canonical broadening**: segment-boundary, not lexical prefix.
- **Composition narrows only**: an intersection removes authority.  Whether a
  *delegated* grant stays inside its parent's boundary is a containment question
  this revision does not answer anywhere (§12).
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
- **Recognized-but-unevaluated is not silent acceptance**: a constraint
  the core recognizes but cannot evaluate MUST appear in the decision's
  `unresolved` field — never dropped (§8.4).  The consumer must evaluate
  or confirm each such constraint before acting, otherwise it MUST deny
  (AAC §6.6).

- **Reason-code detail suffix is diagnostic-only**: everything after the
  first `:` (e.g. the offending param name) MUST NOT change the verdict and
  MUST NOT be relied upon for decisions.  Consumers match on the code
  prefix before the `:` (§9.2).
- **Revision mismatch is fail-closed**: an incompatible language revision
  (§12.1) yields `deny("unsupported_language_revision")` resolved before
  any layer — never a silent downgrade or best-effort re-interpretation.
- **Resource exhaustion is bounded at the input boundary**: the 512-byte
  serialized-size cap and the depth-32 nesting cap (§6.2 step 4) apply to
  `raw_params` as much as to every other input, keeping recursive
  evaluators safe from deep-nesting and oversized-params blowup.

---

## IANA Considerations

This document requests no IANA actions.

Constraint types (`max_rows`, `time`, `network`) and reason codes are defined
by this document as fixed sets.  Should this work be adopted by a working
group, that group may wish to consider whether either set warrants a registry;
this revision does not propose one.

## Privacy Considerations

The language itself transports and stores nothing.  Privacy exposure comes from
what carriers put into it and from what evaluators report:

- Capability identifiers and parameter values describe policy.  They can reveal
  organizational structure, service topology, network ranges (`network`
  constraints), working hours (`time` windows), tenant names, or purposes.
  Deployments should treat grants as policy-confidential material.
- Distinct reason codes reveal the shape of a grant: the difference between
  `params_missing`, `undeclared_param` and `not_in_enum` tells an observer what
  the grant constrains.  Where the requester is untrusted, a consumer should
  consider collapsing reason codes at the boundary, as this specification
  already does for identifier-level failures (Section 9.1).
- Parameter values may carry personal data if a scheme defines them that way.
  Scheme authors should avoid personal identifiers as parameter names or values.
- Residual obligations (`unresolved`, Section 8.4) and any audit record built
  from decisions can persist policy and usage information; retention is the
  carrier's responsibility (Section 11).
- The reference corpus published with this document is synthetic and contains
  no personal data.

## Acknowledgements

Iman Schrock (EMILIA Protocol) reviewed the intersection and constraint
semantics against the revision 1.1 corpus and supplied the adversarial cases
that revisions 1.2 and 1.3 fix: nested partial overlap in intersection,
constraint value handling for `max_rows`, and the public entry-point contract.
For revision 1.4 he re-ran the Go, Python and TypeScript implementations and the
1,184 property cases, and closed the two objections he had raised against the
`max_rows` value domain and the UTF-8 size bound.  For revision 1.5 he re-ran the
three Go suites — 105 authorization, 30 evidence and 13 crosswalk cases — and
supplied the four corrections that revision carries: the collapse from
three-valued evaluation to the binary report (Section 10), the separation of
`allow_unresolved` from evidence (Section 11), the scope of delegation
(Section 12), and the boundary between this projection identity and CAID
(Sections 4.2, 4.3 and 6.4).

## References

### Normative References

- [RFC8785] "JSON Canonicalization Scheme (JCS)", RFC 8785,
  DOI 10.17487/RFC8785, June 2020,
  <https://www.rfc-editor.org/info/rfc8785>.

### Informative References

- [ACA] Agent Capability Authorization and Delegation Binding,
  draft-wei-agent-capability-authorization-00, Work in Progress.
- [AIC-JWT] J. Wei, "AI Agent Identity Certificate (AIC) JSON Web Token
  Profile", draft-wei-aic-jwt-01, Work in Progress, September 2026.
- [CAID] "Canonical Action Identifier",
  draft-schrock-canonical-action-identifier-02, Work in Progress.  Section 4.5
  defines the optional `occurrence_id`; Section 7 keeps occurrence allocation and
  one-time consumption outside the identifier.
- [EMILIA-AEB] "Action Evidence Boundary",
  draft-schrock-action-evidence-boundary-05, Work in Progress.
