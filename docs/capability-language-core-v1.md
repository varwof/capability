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
exercised by a published corpus of 120 vectors and 1184 property cases; three
implementations (Go, Python, TypeScript) that share an author pass both.
**Implementation conformance and this document's claim of a conformance class
are separate.**  An implementation conforms to CLC-A when it meets the
obligations Section 12 lists for that class, and it may claim that conformance on
its own, whatever other implementations exist.  Section 12 additionally sets a
maturity bar for *this document's* claim — two independent implementations
agreeing on verdict and reason.  That bar is **not** met here: as Section 12
states under "Independence of implementations", the three implementations named in
the README share an author, so their agreement is a regression test for the text,
not independent validation.  CLC-A is still claimed by this revision as the
baseline authorization class, whose obligations are implementable and exercised by
a published corpus; the independent-implementation threshold is recorded as
unmet.  The evidence-side class CLC-E is **not** claimed: its relations, value
grammar, reference implementation and corpus ship here.

This revision also folds the delegation **containment** relation into the
document (Section 13): `Contains(parent, child)` decides whether a child grant
stays inside a parent's declared boundary — the single question a delegation
chain asks at every hop that the core's entailment and intersection do not
answer.  It ships with the conformance class **CLC-D** and its own corpus, is
strictly additive, and changes no CLC-A verdict, reason code, or vector.  It
absorbs the previously separate experimental containment extension,
which is retired.

### Revision History

(See the language-revision rule in §12.1 — this revision is incremental and readable compatibly.)

| Rev | Date | Scope | Change |
|-----|------|-------|--------|
| CLC-1.1 | 2026-09-10 | — | Baseline working draft |
| CLC-1.2 | 2026-09-12 | §7, §8.1, §8.4(new), §9, §9.2, §11, §12, Appendix B, Security | Residual-obligation channel `unresolved` (recognized-but-not-evaluated constraints carried explicitly, never silently dropped); `time:window` value grammar defined as a multi-segment UTC window array; recognition upgraded to a "type-name × value-grammar" double check with a new `invalid_constraint` reason code; the "time → intersection" merge rule demoted to v2; constraint merge normalized with deterministic ordering |
| CLC-1.3 | 2026-09-12 | §1, §6.2, §8.1, §8.4, §9, §9.1, Appendix B | Authorization loop tightened + constraint identity namespaced: `Decision.verdict` is three-valued (`allow`/`deny`/`allow_unresolved`), residual obligations no longer mixed into `allow` (kills the fail-closed break where a consumer judges only `verdict == allow`, §8.4); constraint identity becomes the `(scheme,type)` pair, the core recognizes only `max_rows`/`time`/`network` under `varwof/constraint-v1`, everything else → `unknown_constraint` (removes cross-scheme semantic pollution, §8.1); `time:window` value grammar tightened: a single segment must stay within one day (`start < end`), **no single segment may cross midnight** (a crossing must be split into two segments, `end:"00:00"` stays reserved as "next-day midnight"), segment list ascending, non-overlapping, ≤32; `params:{}` ≡ absent = no param constraint (entailment and intersection semantics agree); multi-grant aggregation made explicit (any-one-covers authorizes + residual union + deterministic deny reason, §9.1) |
| CLC-1.4 | 2026-09-13 | §6.2, §8.1, Appendix B | Operation-side value domain enforced: `max_rows` requests must carry a finite non-negative integer; anything else (string, boolean, negative, fractional, non-finite) → `max_rows:violated` instead of passing unchecked.  Size cap restated and implemented in **UTF-8 octets of the canonical serialization** in every path (decoded and raw); measuring code points or UTF-16 code units is non-conforming (the non-ASCII boundary vectors `params-028`/`params-029` pin it).  Evidence-side scope completed in the same working revision: the evidence-side value grammar (`varwof/evidence-v1:*`) and `CLC-REQUIREMENT-v1` are defined (§8.2, §10) and the evidence-side corpus ships (§12, `evidence-vectors.json`, 30 vectors, including ActionId/Match) — CLC-E is **implemented and pinned by a corpus but not claimed**, because the claim needs two independent implementations (§12, P12 of the principles document); genericity is exercised by `crosswalk-vectors.json` (13 vectors, both directions) |
| CLC-1.5 | 2026-09-14 | §4.2, §4.3, §6.4, §10, §11, §12, consumer table, Security | **Instance identity stops claiming CAID.**  The projection identity is the language's own (`clc-action:1:<type>:<suite>:<b64url>`), the v1 suite set is `jcs-sha256` only (the invented `jcs-sha384` is gone), and the text now says what a CAID is not: it covers the **complete** Action Object and identifies no occurrence, while this projection covers the declared material set and occurrence binding consumes a discriminator from the effect boundary.  §10 states the tri-state evaluation → binary report collapse (a top-level `unknown` MUST yield `UNSATISFIED`); §11 states that `allow_unresolved` is an authorization result and not evidence, and fixes the layering (CAID for material-action identity, AEC for evidence satisfaction, AEB for the boundary lifecycle); §12, the consumer table and Security Considerations no longer read a delegation chain as containment.  CLC-A's normative algorithm is unchanged and CLC-1.4 inputs stay readable.  **2026-09-14 review corrections to this revision** (text only): the acknowledgement now states which suites were re-run, for which revision; §12.1 declares CLC-1.5; the reason-ordering and reason-code sections are referenced as §9.1/§9.2 to match the rendered numbering; §9 states the grant-side pre-check precedence that Appendix D15 already pins; the abstract separates implementation conformance from this document's claim of a class; and the occurrence sentence names CAID-02 §4.5/§7. |
| CLC-1.6 | 2026-09-14 | §4.3, §6.2, §10, §12, Appendix B | **`jcs-sha256` is now a real RFC 8785 implementation.** The canonical serializer no longer uses `json.Marshal`'s HTML escaping (which wrote `&`, `<`, `>` as `\u0026`, `\u003c`, `\u003e`): it orders object members by UTF-16 code units (§3.2.3), escapes strings per §3.2.2.2 (only `"`, `\` and the control characters), renders numbers per ECMAScript `Number::toString` (§3.2.2.3), emits no insignificant whitespace, and fails on invalid UTF-8 or lone surrogates instead of substituting U+FFFD.  **The bytes change, so every `clc-action:` identifier and Decision Record input digest changes for material containing `&`, `<` or `>` — the old digests were not JCS and MUST NOT be compared against the new ones.**  Non-ASCII object keys are re-ordered where UTF-16 order differs from UTF-8 byte order.  Refusal of lone surrogates is enforced on the **raw params text** — a decoder would substitute U+FFFD first — and pinned by `params-031`/`params-032`.  CLC-A's verdicts are unchanged and CLC-1.4/1.5 inputs stay readable; the evidence corpus is 32 vectors (adds the RFC 8785 `&` action-id vector and a requirement vector asserting the exported §10 `Satisfaction` report).  **2026-09-15 review corrections**: the abstract no longer states that the independent-implementation bar is met for CLC-A — Section 12's honest scope governs (all three implementations share an author); the decoded-parameter paths of the three implementations now return the same stable denial for malformed Unicode, and Python's decoded size check measures the JCS serialization, matching Go and TypeScript. |
| CLC-1.7 | 2026-09-15 | §6.2, §12, abstract | **Implementation alignment, not a semantic change.**  The decoded parameter paths of the three implementations now return the same stable denial for malformed Unicode (`invalid_params_number`) that the raw path already returned, and Python's decoded size check measures the JCS serialization instead of a serializer's re-encoding — both were implementations disagreeing with §6.2, not gaps in the language.  The abstract no longer states that the independent-implementation bar is met for CLC-A: Section 12's honest scope governs, since the three implementations share an author.  No change for well-formed inputs. |
| CLC-1.8 | 2026-09-15 | §6.2, §12.1, Appendix B | **Implementation alignment, not a semantic change.**  The three raw parameter validators now measure the §6.2 step 4 size on the **JCS form of a number** instead of the received spelling: `1e-6` counts as `0.000001` (four octets more than the token) and `1.0` counts as `1` (two fewer), so the raw boundary no longer accepts an input the decoded boundary refuses or refuses one it accepts — `params-033`–`params-036` pin both directions at the cap.  TypeScript also counts a literal astral character by Unicode scalar value instead of UTF-16 code unit and refuses a literal control character or lone surrogate, matching Go and Python (`params-037`/`params-038`, the literal and escaped spellings of the same string, and `params-039` for the literal control character).  The same revision also states the input-boundary obligation: §6.2 item 7 requires steps 1-5 to run on the received text before any decoding and says an implementation that exposes only a decoded-value entry point MUST NOT be described as refusing malformed Unicode, and §11 states that a §6.2 refusal does not transfer to a decoded value.  The same revision ships six corpus pins alongside the boundary alignment, taking the corpus from 114 to 120 vectors: `entail-007/-008` (class-position wildcard is not a trailing action wildcard, §5.1/§9.3 layer 3), `decide-035` (multi-grant residual-obligation union across covering grants, §9.1/§8.4) and `nested-001/-002/-003` (key closure and presence recurse into nested objects, §6.2/§9.1 layer 7).  Text only - no verdict changes. |
| CLC-1.9 | 2026-09-21 | §12.1, §12, §13(new), Appendix A, Appendix B, Appendix C(new), Security, abstract | **Additive: delegation containment folded in.**  Section 13 adds the relation `Contains(parent, child)` with the conformance class **CLC-D** — a four-layer decision (structural validity; identifier coverage under a profile; parameter narrowing with numeric-bound/enumeration/nested/symmetric-key-closure rules; profile-declared carrier checks), three stable reason codes (`child_exceeds_parent`, `params_not_narrower`, `delegation_mode_not_narrower`), a profile contract, and the consequence that a refused hop is a carrier failure and never a core deny (Section 11).  It carries its own corpus and is exercised by both cross-implementations and cross-vendor crosswalks against six adjacent drafts (Appendix C).  **`Contains` does not read, compare or validate constraints** — the constraint set of a chain is the union accumulated by chained `Intersect` (Section 7), not a containment of constraint sets; a null constraint check is not evidence of containment and MUST NOT be reported as one.  New Appendix C pins the carrier-vocabulary and reason-code mapping.  This revision absorbs and retires the standalone containment extension.  **No CLC-A verdict, reason code or vector changes**, and CLC-1.8 inputs stay readable.  The corpus grows by 50 containment vectors, 784 containment property cases and 44 crosswalk vectors. |
| CLC-1.10 | 2026-09-21 | §6.3, §6.5(new), §9.1, §9.2, §12.1, §13.4.3, Appendix B | **Additive: extended parameter bounds.**  A new optional grant field `param_bounds` (§6.5) carries the bounds `params` cannot express — inclusive `min`/`max`, a `step` multiple rule, `enum` with `min_items`/`max_items` cardinality, an `optional` key marker, and `nested` recursion — without overloading `params` (a `{min,max}` object there would collide with object recursion), so **no existing grant changes meaning**.  A key MUST be declared in at most one of `params`/`param_bounds` (`invalid_params_binding`); four reason codes are added (`invalid_params_binding`, `params_cardinality`, `params_out_of_range`, `params_not_multiple`); the §6.3 scheme-default hook is given a grammar (`param_defaults`, precedence explicit > default > absent).  `param_bounds` is checked at layer 2 and its bounds at layers 7–9, so an implementation that does not implement it refuses a CLC-1.10 input through the minor gate instead of silently ignoring the field.  §13.4.3 gains the containment narrowing rules for the new bounds.  No CLC-A verdict is changed for inputs without `param_bounds`.  It adds 14 containment-narrowing vectors for the new bounds (CLC-D corpus 50 → 64) and 43 core bound vectors (`param-bounds-vectors.json`). |
| CLC-1.11 | 2026-09-21 | §8.5(new), §9.1, §9.2, §12.1, §13.10.2, Appendix B | **Additive: the residual-obligation consumer loop.**  `Resolve(decision, resolutions, now?)` (§8.5) closes the §8.4 feedback loop: a consumer reports each `unresolved` obligation as `satisfied` / `violated` / `unknown`, the sources combine most-restrictive-first (`violated` ≻ `satisfied` ≻ `unknown`), and the verdict collapses to `allow` (all satisfied), `deny` (`{type}:violated` on any), or `allow_unresolved` (remainder) — terminal `deny`/`allow` inputs pass through untouched.  Supplying `now` makes the core clock evaluate a `time:window` obligation directly, giving it a **TTL**: its discharge horizon is the end of the segment containing `now`, so a cached `allow` expires with the window.  Two input-error codes are added (`invalid_resolution`, `invalid_timestamp`).  §13.10.2 is closed as folded in.  No `Authorize` verdict, reason code or vector changes; a CLC-1.10 implementation that does not implement `Resolve` remains CLC-A conformant.  It adds 26 `Resolve` vectors (`resolve-vectors.json`). |
| CLC-1.12 | 2026-09-21 | §7.1(new), §12.1, §13.10.3, Appendix B | **Additive: `ConstraintUnion`, the derived chain-constraint projection.**  A consumer that has a verified delegation chain often needs the chain's whole constraint burden without an effective grant; §7.1 exposes the constraint projection of `Intersect` rule 3 as `ConstraintUnion(chain) → string[]` (normalized union, duplicates folded, deterministically ordered).  It is a **projection, not a meet**: no identifier/parameter comparison, no constraint reading/validation, no containment check, and an empty chain fails closed with `absent_source`.  This closes §13.10.3: `Contains` stays a pure subset over `(identifier, parameters)` (constraints outside the relation), and the union is a separate function rather than folded into `Contains`.  It adds 12 `ConstraintUnion` vectors (`constraint-union-vectors.json`). |
| CLC-1.13 | 2026-09-21 | §13.6, §13.10.4, §13.11(new), §13.12(renumbered), §12.1, Appendix B | **Additive, CLC-D-scoped: `AuthorizeWithChain`, the fused chain check.**  §13.11 adds `AuthorizeWithChain(chain, op)`: an empty chain denies `absent_source`; each adjacent hop is checked with `Contains` and the first failure denies with that hop's §13.5 code (before op validation); otherwise the operation is authorized against `Intersect(chain...)`, which is what brings every ancestor's params **and** constraints (a union axis, outside containment) into force.  Authorizing against the leaf alone was rejected as unsound.  It closes §13.10.4: the fourth relation is now defined, as a CLC-D function, not a core change.  CLC-D conformance now also requires it.  It adds 14 `authorize-chain-vectors.json` vectors; no CLC-A verdict changes.  **Editorial review corrections to this revision (text only, no verdict or corpus change):** §6.3 `Entails` now shows the §6.5 `param_bounds` step and reads the declared key set; §6.5 states that intersecting `param_bounds` is undefined and fails closed (`invalid_params_binding`) and renders the Bound grammar as JSON; §9.2 widens `invalid_params_number` to "no canonical form" (matching §6.2 step 7); §7's object example now intersects numeric leaves to their minimum (`{"a":1}`∩`{"a":2}`→`{"a":1}`) instead of denying; §8.1's `time:window` rule is stated in seconds-of-day, defining the reserved `end:"00:00"` as 86400; §8.5/§11 add the caching horizon for a core-clock discharge; §9 runs the grant-side pre-check before op validation and unions residuals only across covering-*and-allowing* grants; §10 says a top-level `unknown` yields `UNSATISFIED` (no evidence-side `allow_unresolved`); §13.2's `ContainmentResult` is rendered as JSON; the BCP 14 / RFC 3339 / JCS / I-JSON conventions and references are added; and stale cross-references (Appendix D15, §5.1/§9.3, "four foreign representations") are corrected.  **Second editorial pass (text only):** §7 rule 3 states the constraint merge as a **union** (constraints are conjunctive; a tighter same-type bound binds by construction, nothing is dropped as a "meet"); §6.5 closes the `optional` × `param_defaults` precedence (presence is decided first, `optional` wins over a default, no "is the default needed?" recursion) and states that a default is not part of the declared set nor the containment lattice; §6.5 adds the four-layer presence/declaration/constraint/value model that keeps the three senses of `{}` distinct; and §7 makes the **value → authorization-set denotation** explicit (numbers denote `(-∞,v]`, so `{"a":1}∩{"a":2}={"a":1}` is a minimum, and an empty meet needs genuinely disjoint denotations). |
| CLC-1.14 | 2026-09-21 | §6.6(new), §7, §13.11, §12.1, Appendix B | **Additive: `Intersect` now meets `param_bounds` (`BoundMeet`).**  CLC-1.10 grafted the extended bounds onto the grant but left their intersection undefined, so `Intersect` refused any source carrying `param_bounds` (`invalid_params_binding`) and a delegation chain that used `param_bounds` could never be fused-authorized (`AuthorizeWithChain` denies at its `Intersect` step).  §6.6 defines the meet per family: numeric `min`=greatest, `max`=least, `step`=the coarser grid when one exactly divides the other (else fail-closed); enum member intersection and tightened cardinality; `nested` recursion over identical key sets; `optional` by conjunction; numeric∩enum reduces to the filtered enum; scalar∩nested and `min>max` are an empty meet (`no_overlap`).  A key must keep one declaration site across sources (§13.4.3 already guarantees this for a valid chain).  It adds no reason code and is strictly additive: a chain without `param_bounds` is byte-for-byte unchanged, so every existing verdict, reason code and vector is untouched.  It adds `param-bounds-meet-vectors.json`, and updates `authorize-chain-vectors.json` (`ac-012` now allows — a `param_bounds` chain fuses — and `ac-015` denies with `params_out_of_range` at a meet that is empty). |

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
| **Verdict** | allow / deny / allow_unresolved | SATISFIED / UNSATISFIED |

**Conventions.**  The key words MUST, MUST NOT, SHOULD, SHOULD NOT and MAY in
this document are to be interpreted as described in BCP 14 [RFC2119] and
[RFC8174] when, and only when, they appear in all capitals, as shown here.  "UTC instant"
is an [RFC3339] timestamp.  "JCS" is the JSON Canonicalization Scheme
[RFC8785]; "I-JSON" is [RFC7493].

The language structure is identical on both sides; only the direction
differs:
- Authorization: "I grant you permission to do X"
- Evidence: "I have evidence that X was done"

The design principles behind this core — including what the language
**deliberately refuses** (no control flow, no mutable state, no general-purpose
policy language) — are stated in `capability-language-core-principles-v1.md`
(in [CLC-CORPUS]):

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

Verdicts are written lowercase on the authorization side (`allow`/`deny`/
`allow_unresolved`) and uppercase on the evidence side
(`SATISFIED`/`UNSATISFIED`), following the EMILIA/AEB convention.

---

## 3. Grammar

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

The trailing wildcard is part of the identifier grammar (the optional final
`":" "*"` above), so `std/database-v1:query:*` is a well-formed
`capability-id`; only that shape is a wildcard (§3, below).

**Unambiguous `scheme`.**  Because `product` may contain `-`, the `-v<major>`
suffix is the **last** occurrence of `-v` followed by digits.  A `product`
that itself contains the two-character sequence `-v` is invalid
(`invalid_capability_id`), so `a/b-v1-v2` is rejected rather than parsed two
ways; `b-v1` as a product name is not expressible.  A scheme in use before
this rule that relies on such a product is out of grammar in v1.

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

1. **Canonical serialization.** Params are normalized to the JSON
   Canonicalization Scheme form (JCS, RFC 8785): object members sorted by code
   unit, numbers in the ECMAScript `Number::toString` form, no insignificant
   whitespace.  The original key order, number spelling and spacing are
   **not** preserved — canonicalization replaces them with the deterministic
   form (this is what the size cap in step 4 and the material digest are
   measured on).  Evaluation never guesses; a lossy re-serialization (e.g. a
   map that drops duplicate keys) is not used for decisions.
2. **Duplicate keys.** A params object with a duplicate JSON key is rejected:
   `deny("invalid_params_duplicate_key")`.
3. **Number shape.** A numeric param is rejected with
   `deny("invalid_params_number")` when it is **non-finite or out of IEEE-754
   range** (e.g. `1e400`, an exponent beyond the representable maximum — it is
   an overflow, not an over-precision case) or **over-precision** (more than 17
   significant decimal digits, e.g. `1.0000000000000001`).  The digit count operates on the
   **JSON token as received** — the raw digit-character sequence at the input
   boundary, before it enters any storage / float / decimal representation —
   so float64 and decimal/bignum implementations MUST NOT diverge: the judged
   input is always the raw token text (`params-*` number probes in the corpus;
   near-limit forms such as `1.0000000000000001` extend the probes without
   changing the rule).  Malformed params text that cannot be parsed as an
   object is refused with the same code (see step 7).
4. **Size and depth.** Params whose canonical length exceeds 512 **UTF-8
   octets** — measured in octets, never in code points or UTF-16 code units
   (rev CLC-1.4) — or whose nesting depth exceeds 32, are rejected:
   `deny("invalid_params_size")`.  Nesting depth counts **both** objects and
   arrays, with the outermost object as level 1 (31 nested arrays inside the
   top-level object therefore = depth 32).
5. **Order of checks.** Size/depth (4) precede duplicate keys (2), which
   precedes number shape (3); the first failing check wins.  All five run
   before §9.1 layer 1, so normalized params are the only view the layers see.
   The size in step 4 is measured with every token in its JCS spelling
   (numbers re-spelled per ECMAScript `Number::toString`, strings per JCS
   §3.2.2.2) but **without** requiring key uniqueness, so it is defined even
   when a duplicate key makes full JCS undefined; this is why an over-limit
   input that also has a duplicate key reports `invalid_params_size`
   (`params-025`/`params-026`).
6. **Decoded-object path.** A caller that supplies params already decoded
   (no `raw_params` text) cannot reproduce the original byte stream; in
   that case the size check (4) applies to a **canonical serialization**
   (the JCS form of the decoded object: sorted keys, compact), and the
   depth check (4) applies to the decoded structure directly.
   Byte-exactness against a specific original text is guaranteed only for
   the raw path; but **both** entry points MUST reject the caps — an
   oversized/deep params object is denied whichever way it arrives.

7. **Malformed Unicode is a property of the received text.**  A lone surrogate
   escape, or an octet that is not valid UTF-8, has no JCS form (§3.2.2.2):
   step 1 cannot normalize it, so the input is refused.  The refusal reuses
   `invalid_params_number` (§9.2), whose scope is **"the params input is not
   representable in canonical form"** — a numeric param that is non-finite /
   over-precision *or* text that is not well-formed Unicode / not parseable as
   a JSON object.  (One stable code, not one per malformation: introducing a
   second code would change the reason for inputs already pinned to
   `invalid_params_number`, which the additive rule forbids.)  That check is defined over the octets as
   received and MUST run **before** any decoding step, because a general-purpose
   JSON decoder does not preserve the distinction.  Go's `encoding/json`, for
   example, replaces both a lone surrogate escape and an invalid octet with
   U+FFFD, so `{"s":"\ud800"}`, `{"s":"\ufffd"}` and a literal invalid octet
   arrive at the decision function as the same value — `{"s":"\ufffd"}` — and
   the refusal cannot be recovered afterwards.  Therefore:

   - the party that receives the input MUST run steps 1-5 on the received text,
     not on a re-serialization of a decoded value;
   - an implementation that exposes **only** a decoded-value entry point MUST
     NOT be described as refusing malformed Unicode: its verdict is defined
     over the value it was handed, which may already be a repaired one.  The
     entry point that takes the text is the normative one, and an
     implementation SHOULD name the two so a caller cannot mistake one for the
     other;
   - two parties that must agree on the verdict MUST agree on the received
     text, or on a digest of it.

### 6.3 Algorithm

```
Entails(G, O) → bool:
  1. G.namespace ≠ O.namespace → false      (namespace = scheme + action Class, §9.1 layer 3)
  2. G.id doesn't cover O.id → false        (path coverage, §9.1 layer 4)
  3. G declares no key → true               (both `params` and `param_bounds` absent/empty
                                             → grant unconstrained, absent ≡ empty object)
  4. O.params absent → false                (bounded grant, request omits it → fail-closed,
                                             except a declared key marked `optional`, §6.5)
  5. params_subset(O.params, keys(params) ∪ keys(param_bounds), param_bounds)
                                            (compare declared set incl. §6.5 bounds, §9.1 layers 5–9)
```

Step 5 is the §9.1 layers 5–9 comparison over the grant's **declared key set**
(`keys(params) ∪ keys(param_bounds)`, §6.5): `params` values follow §6.2 value
subset, and a `param_bounds` key additionally enforces its Bound (inclusive
`min`/`max`, `step`, enum cardinality, `optional`, `nested`).  A grant with no
`param_bounds` reduces step 5 to the `params`-only comparison of earlier
revisions.  Steps 3 and 4 read the declared key set, so a grant whose only
declarations are `param_bounds` is still "bounded" for presence purposes.

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

### 6.5 Extended parameter bounds (`param_bounds`)

`params` (§6.2) stays exactly as defined: a scalar number is an upper bound, an
array is a membership set, an object recurses per key, and there is no lower
bound, no step, no cardinality bound and no optional-key marker.  This
subsection adds those as a **separate, optional grant field**, `param_bounds`,
so that **no existing `params` input changes meaning**: a grant without
`param_bounds` behaves exactly as before, and every `params` verdict is
unchanged.

**Binding rule (one authoritative representation per key).**  A parameter key
MUST be declared in **at most one** of `params` and `param_bounds`.  Declaring
the same key in both is rejected: `deny("invalid_params_binding")`.  The
**declared key set** of a grant is `keys(params) ∪ keys(param_bounds)`; key
closure (§9.1 layer 7) and the `params:{}`≡absent rule are read over that set.

**Four distinct layers — do not collapse them in a decoder.**  A bare `{}` has
different meaning at each layer, and an implementation must keep them separate
before normalizing:
1. **Container presence** — `"params"` absent vs `"params":{}`.  Both are
   **unconstrained** (no declared keys); `{}` is not "declares nothing and
   denies".
2. **Declaration site** — a key is declared via `params` **or** `param_bounds`
   (never both).  The site decides which value algebra applies to the key.
3. **Value constraint** — inside `params`, an empty value **is** a restriction
   (`{"tables":[]}` denies the class; deny-when-declared, §6.2); inside
   `param_bounds`, an empty Bound `{}` declares the key with **no** value
   constraint (it only participates in key closure).  Same `{}`, opposite
   reading, because the layer differs.
4. **Request value** — what `O` supplies (or a materialized default), evaluated
   per the key's family at layers 7–9.

A decoder that maps `{}`→"absent" or `{}`→"empty set" uniformly across these
layers will disagree with the language on at least one of them.

**Bound grammar (closed).**  `param_bounds` maps a key to a `Bound` object:

```
Bound = {                          // a closed JSON object, at most one family
  // numeric family
  "min":       <number>,           // inclusive lower bound
  "max":       <number>,           // inclusive upper bound
  "step":      <number > 0>,       // value must be an integer multiple of step
  // enum family
  "enum":      [ <scalar> ],       // allowed values (membership set)
  "min_items": <integer >= 0>,     // request cardinality lower bound
  "max_items": <integer >= 0>,     // request cardinality upper bound
  // nested family
  "nested":    { <key>: Bound },   // recursion for an object-valued key
  // orthogonal to all families
  "optional":  <boolean>           // request MAY omit the key (default false)
}
```
(Bound is JSON, not ASN.1: the members above are JSON keys and the comments are
notation only.)

Every member is optional and the object is **closed** — a member outside this
set is rejected (`invalid_params_binding`).  A Bound carries **at most one
value family**, plus `optional` which is orthogonal:

- **numeric family** — any of `min`, `max`, `step`;
- **enum family** — `enum`, and/or `min_items`/`max_items`;
- **nested family** — `nested`.

Mixing families (e.g. `enum` with `max`, or `nested` with `min`) is rejected
(`invalid_params_binding`).  An **empty** Bound `{}` declares the key with no
value constraint (it still participates in key closure).  `min > max`,
`step ≤ 0`, `min_items > max_items`, or a negative `min_items` are rejected
(`invalid_params_binding`).  The whole `param_bounds` object is subject to the
same input normalization as `params` (§6.2): canonical serialization, duplicate
keys, number shape, size (512 octets) and depth (32), checked at layer 2.

**Entailment semantics (grant `G` vs operation `O`).**

- **Presence (layer 7).**  A declared key with `optional: true` MAY be absent
  from `O`; a declared key with `optional` absent or `false` MUST be present
  (`params_missing` otherwise).  An operation key not in the declared key set is
  `undeclared_param`.  (Unchanged behavior for grants that declare no
  `param_bounds`, where every declared key is required.)
- **Enum family (layer 8).**  If `enum` is declared, the request value must be a
  member (`not_in_enum`, unchanged rule): a scalar request must equal a member;
  an array request must have every element equal to a member.  If `min_items` /
  `max_items` are declared, the **request cardinality** (an array's length; a
  scalar counts as 1) must satisfy `min_items ≤ n ≤ max_items`, else
  `params_cardinality`.
- **Numeric family (layer 9).**  `min`/`max` are **inclusive**: a numeric
  request value must satisfy `min ≤ v ≤ max` (each bound, when declared), else
  `params_out_of_range`.  `step` requires the request value to be an integer
  multiple of `step`, evaluated in IEEE-754 binary64 as
  `let q = v / step in q == floor(q) && q * step == v` (deterministic across
  implementations, since both operands arrive at the boundary as binary64), else
  `params_not_multiple`.  A numeric-family bound applied to a non-number
  request value is fail-closed (`params_exceed_grant`).
- **Nested family (layer 8/9).**  `nested` recurses the value comparison on an
  object-valued request key with the same rules, including symmetric key closure
  and `optional` at each depth.  A `nested` bound applied to a non-object
  request value is fail-closed (`params_exceed_grant`).

**Scheme defaults.**  A capability scheme (§3 scheme grammar; `data/std/...`) MAY
declare `param_defaults`, a map from a parameter key to its **default value**.
The consumer obligation of §6.3 is thereby made concrete: before evaluating
`Entails(G, O)`, an implementation MUST materialize, for every key `O` omits that
the scheme declares a default for, that default into `O`'s params; precedence is
**explicit operation value > scheme default > absent**.  A default is applied
only when it is needed to satisfy a grant-declared key; it never adds a key the
grant does not declare (the key-closure check is unchanged).

**`optional` closes the default interaction (no recursion).**  The presence of
the key is decided **first**, by the grant's `optional` marker, and only then is
a default consulted — so there is no "is the default needed?" loop:
- a **required** declared key (no `optional`/`optional:false`) that `O` omits:
  materialize `param_defaults[key]` if the scheme declares one (the key is then
  present with that value), else `deny("params_missing")`;
- an **`optional:true`** declared key that `O` omits: the default is **not**
  materialized — `optional` is the explicit "may be absent" marker and wins over
  the default, so the key is simply absent (and satisfies presence);
- either way, an explicitly supplied `O` value wins over the default.

Defaults are **scheme configuration, not language semantics**: the relation
itself takes no scheme argument, and two consumers that load the same scheme
reach the same verdict (a deployment that omits the scheme's defaults is a
different input, and the difference is attributable to the input, not to
`Entails`).  In the containment relation a default is resolved **before** the
grants are compared (§13.8.1 obligation 1), so containment compares resolved
declared sets.  A `param_defaults` entry is **not** part of a grant's declared
set and does **not** enter the containment lattice: `Contains` narrows over
`keys(params) ∪ keys(param_bounds)` and the `optional` markers alone, so a
parent's default never widens or inverts the `optional`→required narrowing
direction (§13.4.3).

**Containment (§13).**  §13.4.3 narrows a child grant against its parent using
this grammar: a `param_bounds` bound of the child must be within the parent's
bound for the same key (numeric `min` raised or equal, `max` lowered or equal,
`step` refined to an integer multiple, `enum` a subset, cardinality bounds
tightened, `optional` not widened from required to optional, `nested` recursed).
A parameter declared in one of `params`/`param_bounds` and not the other is a
key-set difference and fails key closure (`params_not_narrower`).

---

### 6.6 Intersection of bounds (`BoundMeet`)

`Intersect` (§7) combines the `param_bounds` of its sources with a **meet**,
over the same "value → authorization set" denotation §7 uses for `params`.  The
families are those of §6.5; the meet is defined per key declared in
`param_bounds` by two or more sources.

- **`optional`** is orthogonal and combines by **conjunction**: the result key is
  optional only if every source marks it optional (`optional := AND`); a key
  required by any source stays required.
- **numeric family** (`min`/`max`/`step`): `min` is the **greatest** declared
  minimum, `max` the **least** declared maximum (undeclared means unbounded).
  `step`: if both declare one and one is an exact multiple of the other (the
  §6.5 multiple predicate), the meet's `step` is the **coarser** (larger) of the
  two — the coarser grid is a subset of the finer, so it is the meet; if neither
  divides the other, no single binary64 `step` denotes both grids and the meet
  **fails closed** (`invalid_params_binding`).  One declared `step` is carried
  through.  `min > max` after combining → the meet is **empty** → `no_overlap`.
- **enum family** (`enum`/`min_items`/`max_items`): the `enum` member sets
  intersect (exact equality); if both sources declare `enum` and the intersection
  is empty → `no_overlap`; `min_items` is the **greatest** declared value,
  `max_items` the **least**; `max_items < min_items` → `no_overlap`.
- **nested family** (`nested`): the two objects MUST have the **same key set**,
  else `no_overlap` (exactly as object-valued `params`, §7); the result recurses
  `BoundMeet` per key, with `optional` combining as above at every depth.
- **numeric ∩ enum**: the enum member list is filtered to members that satisfy
  the numeric bound (`min`/`max`/`step`); the result is an **enum**-family bound
  (the enumerated members fully denote the meet) carrying the enum side's
  cardinality.  An empty filtered list → `no_overlap`.  If the enum side has
  **no member list** (only `min_items`/`max_items`), the meet would require a
  numeric scalar bound **and** a cardinality bound at once — two families, which
  the closed grammar cannot express — and **fails closed**
  (`invalid_params_binding`).
- **scalar ∩ nested** (numeric or enum vs. `nested`): a scalar value and an
  object value have no common value → `no_overlap`.
- **empty Bound** `{}` is the identity for the value families (`{} ∩ X = X`);
  its `optional` still participates.

The result always carries **at most one** value family, so it is a valid §6.5
Bound.  All failure modes are the §9.2 codes already associated with `Intersect`
(`no_overlap` for an empty meet, `invalid_params_binding` for an unrepresentable
one); no new reason code is introduced.

**Key site.**  A key's **declaration site** (`params` vs `param_bounds`) must
agree across the sources of one `Intersect`.  A key declared in `params` by one
source and in `param_bounds` by another is refused (`invalid_params_binding`).
This can only arise for independent authority sources, never for a delegation
chain: §13.4.3 already requires the sites to match at every hop (a site
difference is a key-set difference).  A key that no source declares in
`param_bounds` stays in `params` and follows the §7 `params` meet unchanged.

---

## 7. Intersection (∩)

P_effective = P_principal ∩ C_agent ∩ P_gateway.

Rules:
1. Each source provides a grant set.
2. Effective grant MUST be covered by at least one grant from every source.
3. Same-capability constraints merged by **union**: every source's constraint
   strings are kept (constraints are conjunctive — each is independently
   checked, so a tighter bound of the same type binds by construction).  The
   merge is a set union of normalized constraint strings, **not** a meet that
   discards a looser one; dropping a source's constraint would drop its
   restriction.
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

**The meet is over authorization sets, not JSON values.**  Neither `Intersect`
nor §6.2 compares JSON values directly; each value denotes an **authorization
set** and the meet is set intersection on that denotation.  A number denotes
`(-∞, v]` (an upper bound), an array denotes a membership set, a string/boolean
denotes the singleton `{v}`, and an object denotes the product of its keys'
denotations.  So `{"a":1}` is not the set `{1}` but `(-∞,1]`, and
`{"a":1} ∩ {"a":2} = (-∞,1] = {"a":1}` — a minimum, not an empty set.  A meet is
**empty** (→ `deny("no_overlap")`) only when the denotations are genuinely
disjoint: two enum sets with no common member (a numeric `params` meet is always
a minimum, since `params` has no lower bound), or divergent key sets (next
paragraph).

**Object-value intersection requires identical key sets.**  Two object
values intersect key-by-key only when their key sets are the same; object
values with different key sets → `no_overlap` deny.  Merging "shared keys"
would drop the keys the other source constrains, so the result would not be
covered by that source (P11 composition narrows only): `{"a":1}` ∩ `{"b":1}`
→ deny(`no_overlap`).  When the key sets **are** the same the values recurse
under the §6.2 rules, so a numeric leaf intersects to its **minimum**
(`{"a":1}` ∩ `{"a":2}` → `{"a":1}`, not a deny — matching the `{"limit":100}`
∩ `{"limit":50}` row above), and `{"a":1}` ∩ `{"a":1}` → `{"a":1}`.

**`param_bounds` merges by a defined meet.**  `Intersect` combines each key
declared in `param_bounds` with the meet of §6.6: numeric `min`/`max`/`step`,
enum member intersection and cardinality, and `nested` recursion, with
`optional` combined by conjunction.  An empty meet is `no_overlap`; an
unrepresentable one (two step grids with no common multiple, or a numeric
bound met with a cardinality-only enum) is `invalid_params_binding`.  A key
declared in `params` by one source and `param_bounds` by another is refused
(`invalid_params_binding`, §6.6 "Key site").  The §7.1 `ConstraintUnion`
projection is separate and unaffected.

### 7.1 ConstraintUnion (derived projection)

A consumer that has established a delegation chain often needs the chain's
**whole constraint burden** without computing an effective grant.  That is
exactly the constraint projection of chained `Intersect` (rule 3), exposed as
a named function:

```
ConstraintUnion(chain) → string[]        // chain = ordered Grant[]
```

It returns the **normalized union** of every constraint string carried by the
grants in `chain` — duplicates folded, result deterministically ordered
(lexically sorted) — the same normalization `Intersect` applies, so the two
never disagree.

`ConstraintUnion` is a **projection, not a meet**: it does not compare
identifiers or parameters, does not read or validate constraint values, and
does not check containment.  It asserts nothing about authority; the chain's
per-hop `Contains` check (§13) and the operation's `Authorize`/`Resolve`
(§9, §8.5) remain separate steps.  Because it is not an effective-set
computation, it carries no membership semantics of its own — an **empty
`chain` fails closed** with `absent_source` (the same refusal `Intersect`
gives over zero sources, §7 rule 5), so a caller that lost the chain cannot
mistake "nothing to union" for "no constraints".

This function is why `Contains` stays pure (§13.4.4): containment answers
"is the child's declared boundary inside the parent's?", and the union
answers "what does the chain collectively require?".  Folding the union into
`Contains` would make the relation no longer a subset on the declared tuple
and would let a null constraint check hide a broken boundary.

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
| `time` (`window`) | non-empty JSON array (≤ 32 elements), elements `{"start":"HH:MM[:SS]","end":"HH:MM[:SS]"}`, UTC, repeated daily, single window = one-element array; each endpoint is a **seconds-of-day** value (parsed from `HH:MM[:SS]`), with the reserved endpoint `"00:00"` in the `end` position read as **86400** (next-day midnight, 24:00) — so a segment is the half-open `[startSec, endSec)` and MUST satisfy `startSec < endSec` (**not** lexical string order, which would wrongly reject the canonical `22:00→00:00` segment, since `"22:00" > "00:00"` as text); a single segment **must not cross midnight**, so a crossing window is split into two same-day segments (`22:00→00:00` + `00:00→06:00`); the segment list MUST be ascending by `(startSec,endSec)` and **non-overlapping** | recognized only → `allow_unresolved` + `unresolved` (§8.4) |
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

### 8.5 Resolving residual obligations (`Resolve`)

§8.4 delivers residual obligations but leaves the consumer's feedback loop
undefined.  `Resolve` closes it: a consumer reports, per obligation, whether it
is satisfied, violated, or still unknown, and the core collapses the result to
a fresh decision.

```
Resolution = { constraint: string,
               status: "satisfied" | "violated" | "unknown" }
Resolve(decision, resolutions, now?) → Decision
```

`decision` is a §9 `Decision`; `resolutions` is an ordered list (possibly
empty) of `Resolution`; `now` is an optional UTC instant (`RFC3339`, `Z`).
`now` is the only input that lets the core tick a residual itself.

Algorithm, in order:

1. **Terminal verdicts are fixed.**  If `decision.verdict` is `deny` or
   `allow`, `Resolve` returns `decision` unchanged and ignores `resolutions`:
   a deny is never revived and an allow carries nothing to discharge.
2. **Malformed input fails closed.**  An entry that violates the grammar above
   (unrecognized `status`, empty/non-string `constraint`) → `deny` with
   `invalid_resolution`; a `now` that is not a valid instant →
   `deny` with `invalid_timestamp`.
3. **Discharge on `allow_unresolved`.**  Let `O = decision.unresolved` (already
   normalized and sorted, §8.4).  For each `o ∈ O`, a status in
   `{satisfied, violated, unknown}` is computed by combining the sources below
   under the order **`violated` ≻ `satisfied` ≻ `unknown`** (the most
   restrictive source wins — a consumer that reports `violated` is never
   overridden by a lenient one, and the core clock is never overridden by a
   lenient assertion):
   - **Core clock** — if `o` is a core-recognized `varwof/constraint-v1:time`
     obligation whose value is a §8.1 window array, **and `now` is supplied**,
     the core evaluates it: `now` inside a segment → `satisfied`; outside every
     segment → `violated`.  This is the obligation's **TTL**: the discharge
     horizon is the end of the segment containing `now`, so re-invoking
     `Resolve` with a later `now` re-evaluates to `violated` once the window has
     passed — a cached `allow` does not outlive its window.
   - **Consumer resolution** — a `Resolution` for `o` contributes its `status`;
     the most restrictive of the two wins.
   - Absent everywhere → `unknown`.
4. **Repeated entries** for the same `constraint` combine under the same
   `violated` ≻ `satisfied` ≻ `unknown` order.
5. **Unrelated resolutions are ignored.**  A `Resolution` whose `constraint` is
   not in `O` cannot widen the outcome; `O` is authoritative.
6. **Result**:
   - any `o` has status `violated` → `deny`, reason = that constraint's
     `{type}:violated` (`time:violated` for a core-clock violation; otherwise
     the type segment of the constraint string), `unresolved = []`;
   - every `o` is `satisfied` → `allow`, reason `null`, `unresolved = []`;
   - otherwise → `allow_unresolved`, reason `null`, `unresolved` = the still-
     `unknown` subset (normalized + sorted, §8.4).

Without `now`, the core attaches no TTL to a `time:window` obligation: a
consumer may report it `satisfied` (its declaring scheme owns its clock), but
that discharge is only as fresh as the call, and a consumer that needs a
core-enforced horizon MUST pass `now`.

**Acting on a result (caching rule).**  `Resolve` returns a plain decision; it
does **not** carry an expiry field, so a core-clock discharge is only valid for
the instant of the call.  A consumer that acts on a `Resolve` result involving a
core-evaluated `time:window` obligation MUST either re-invoke `Resolve` with a
current `now` immediately before acting, or not cache the result beyond the
current segment's end (the discharge horizon, §8.5 step 3) — it MUST NOT hold a
cached `allow` past that horizon.  Equivalently: a suite that needs a
mechanically enforceable "valid until" value derives it from the segment end
itself, not from the returned `Decision`.  (The obligation carried on an
`allow_unresolved` decision remains the §8.4 object a consumer evaluates; this
rule is only about not outliving a clock-based discharge.)

`Resolve` is deterministic and fail-closed; it is idempotent
(`Resolve(Resolve(d, r, now), r, now) = Resolve(d, r, now)`) and
monotone (adding a `violated` never turns a deny into an allow; removing one
never turns an allow into a deny).  It neither invents nor drops obligations.
It subsumes the coarser identity-level consumer gate (the reference
implementations' `Discharge`, which only answers "do I understand and commit
to every obligation?"): confirming an obligation is the `satisfied` case.  It
defines no policy about *how* the consumer evaluates an obligation (P2) — that
is the declaring scheme's (§11).

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
(§9.1 layer 10; Appendix B.5, row D15, pins it), so a caller that passes neither
input gets that reason and not `missing_capability_id`.  The algorithm below
therefore runs the grant-side pre-check **first**, ahead of the numbered
operation steps — the numbering mirrors §9.1's layer order for what follows, not
the precedence of the pre-check.
0. (Pre-check) An absent or empty grant set → `deny("capability_not_authorized")`
   (§9.1 layer 10), before any operation check; this is why the absent-grant /
   absent-operation pair resolves here and not to a layer-1 code.
1. Validate operation: missing/invalid id → deny with stable reason.  The
   operation's **specific layer-1 code** is reported — `missing_capability_id`
   (no id), `unsupported_wildcard` (v1-forbidden wildcard shape) or
   `invalid_capability_id` (other grammar violation) — and is **not**
   collapsed to a generic code.
2. Find covering grants via Entailment (§6.1).  No covering grant →
   `deny("capability_not_authorized")` (§9.1 layer 10); the absent/empty case
   was already resolved by step 0.
3. For each covering grant: evaluate constraints (§8.1): non-recognized
   `(scheme,type)` → `unknown_constraint`; recognized but non-conforming
   value → `invalid_constraint`; recognized with a core evaluator
   (`varwof/constraint-v1:max_rows`) and violated →
   `{type}:violated`; recognized without a core evaluator (`time`,
   `network`) → residual obligation (§8.4).
4. **Aggregate** (multi-grant set, §9.1):
   - Any covering grant that "allows" (no params/constraint rejection) →
     overall allow;
   - Residual obligations = the `unresolved` **union across the covering grants
     that also allow** (normalized + sorted).  A covering grant that is rejected
     at the params/constraint layer contributes **no** obligations: it does not
     authorize, so its residuals are not carried.  The union is nevertheless
     order-independent, because every covering-and-allowing grant is visited;
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
| 2 | Params normalization | Duplicate JSON keys; non-normalizable numbers (non-finite / out-of-range / over-precision) and malformed-Unicode text; size/depth limits (§6.2); `param_bounds` well-formedness and the one-representation binding rule (§6.5) | `invalid_params_duplicate_key`, `invalid_params_number`, `invalid_params_size`, `invalid_params_binding` |
| 3 | Namespace = scheme + action Class | Grant vs operation scheme and Class | `different_namespace` |
| 4 | Path coverage (same namespace) | Literal path segments, trailing-wildcard depth | `literal_mismatch`, `wildcard_requires_trailing_segment` |
| 5 | Explicit empty bound | Any grant/intersection source declares a **parameter value** that is `[]`/`{}` (a present-but-empty `params` object is *no* constraint, §7 rule 6) | `empty_bound_denies_class` |
| 6 | Null values | Any `null` parameter value | `invalid_params_null` |
| 7 | Param presence | Grant bounds a param the operation omits (or operation has no `params`); operation carries a key the grant does not declare.  A `param_bounds` key with `optional:true` is exempt from the omission half (§6.5) | `params_missing`, `undeclared_param` |
| 8 | Enum membership and cardinality | Request value not a member of a granted array set (§6.2); request cardinality outside a `param_bounds` `min_items`/`max_items` (§6.5) | `not_in_enum`, `params_cardinality` |
| 9 | Bound comparison | Numeric/bound exceeded; `param_bounds` `min`/`max` out of range; `step` not an integer multiple (§6.5) | `params_exceed_grant`, `params_out_of_range`, `params_not_multiple` |
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
  2. Residual obligations = `unresolved` **union across the covering grants
     that allow** (normalized + sorted).  A covering grant rejected at the
     params/constraint layer contributes none — it does not authorize, so its
     residuals are not carried (they are never silently dropped from a
     decision it does not produce);
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
- **`Resolve` (§8.5) is post-decision, not a layer.**  It consumes a
  `Decision` and never re-runs `Authorize`; only `invalid_resolution` /
  `invalid_timestamp` (§9.2) and a `{type}:violated` obligation result are
  introduced by it, and only on an `allow_unresolved` input.

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
| `invalid_params_number` | The params input has no canonical form: a numeric param is non-finite, out of IEEE-754 range, or over-precision (> 17 significant decimal digits) (§6.2 step 3), or the text is not well-formed Unicode / not parseable as a JSON object (§6.2 step 7).  One stable code covers every "cannot be normalized" params failure (§6.2 representation, §9.1 layer 2) |
| `invalid_params_size` | Params exceed the 512-byte serialized size or the depth-32 nesting limit (§6.2 representation, §9.1 layer 2) |
| `invalid_params_binding` | A `param_bounds` bound is malformed (unknown member, mixed families, `min > max`, `step ≤ 0`, `min_items > max_items`), or a key is declared in both `params` and `param_bounds` (§6.5, §9.1 layer 2) |
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
| `params_cardinality` | Request cardinality is outside a `param_bounds` `min_items`/`max_items` (§6.5) |
| `params_out_of_range` | Request value is outside a `param_bounds` `min`/`max` inclusive bound (§6.5) |
| `params_not_multiple` | Request value is not an integer multiple of a `param_bounds` `step`, per the IEEE-754 rule (§6.5) |
| `invalid_params_null` | `null` parameter value (rejected in v1) |
| `unsupported_language_revision` | Declared CLC revision is incompatible with the implementation (§12.1; fails closed, no silent downgrade) |
| `unknown_constraint` | Unknown constraint type (fail-closed) |
| `invalid_constraint` | Recognized type whose value fails its §8.1 value grammar |
| `{type}:violated` | A known constraint is violated (e.g. `max_rows:violated`); also reported by `Resolve` for a discharged-as-violated obligation (§8.5) |
| `invalid_resolution` | A `Resolve` resolution entry is malformed (unknown `status`, non-string/empty `constraint`) (§8.5) |
| `invalid_timestamp` | The `Resolve` `now` argument is not a valid UTC instant (§8.5) |

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
   point (consumption) evaluates to `unknown`, which at the top level yields
   `UNSATISFIED` (never `SATISFIED`) — the evidence side has no
   `allow_unresolved`; `unresolved` is an authorization-side channel (§8.4,
   §11).
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
- **A §6.2 refusal does not transfer to a decoded value.**  The input-boundary
  checks are defined over the text as received (§6.2).  A deployment that must
  reproduce a refusal, or that applies a permit to a request it did not
  evaluate, therefore anchors the decision to the **received octets** or to a
  digest of them (§4.3) — never to a value a decoder has already normalized.  A
  pipeline that can apply a permit to a request whose text was never checked has
  left the CLC boundary
- CLC-A stays the **scope language**: material-action identity is referenced from
  CAID, evidence satisfaction from AEC, and the boundary lifecycle from AEB; the
  narrow crosswalk between them is the composition point

---

## 12. Conformance

CLC-v1 defines **three conformance classes**:

**CLC-A (authorization side)** — the v1 baseline. A conforming
implementation MUST implement: grammar (§3), entailment (§6.1),
intersection (§7), decision function (§9), rejection of non-recognized
`(scheme,type)` constraints (`unknown_constraint`, §8.1), rejection of
non-conforming recognized-type values (`invalid_constraint`, §8.1),
exposure of recognized-but-unevaluated constraints via the decision's
`unresolved` field on an independent `allow_unresolved` verdict (never
silently dropped, §8.4), multi-grant aggregation (§9.1), and stable
reason codes (§9.2).

**CLC-D (delegation side)** — the containment relation, defined in
**Section 13**.  A conforming implementation MUST implement
`Contains(parent, child)` with its four ordered layers, its three stable
reason codes (`child_exceeds_parent`, `params_not_narrower`,
`delegation_mode_not_narrower`) and its profile contract (§13.8.1), and MUST
pass `containment-vectors.json`.  A delegation policy that requires each hop
to stay inside the previous hop's boundary reads `Contains`, not §7:
entailment and intersection over the **declared** sets are necessary but not
sufficient, because they do not compare a child's boundary against a parent's.
An operation fitting a grant proves nothing about a child staying inside its
parent, and where containment cannot be established a binding profile MUST NOT
authorize the delegation.  `Contains` is a language relation over grant
values, not a wire format; the effective subset a delegation record carries is
still the profile's to define.

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

**Conformance corpora.**  The suites below are published in the repository
tree pinned as [CLC-CORPUS]; repository paths written as `capability/...`
throughout this document are relative to that pinned tree, so the exact
vectors named here are retrievable.  CLC-A conformance is exercised by two
machine-readable reference suites at
`capability/data/_vectors/clc-v1/`: `vectors.json` — 120 vectors mapped
to Appendix B — and `property-cases.json` — 1184 cases pinning the §7
meet-law, identifier narrowing and source-order independence.  Their
syntax is defined by `vectors.schema.json`; `offline-vectors.json` is a
timestamped snapshot mirror.  A conforming implementation MUST pass both
suites.  CLC-D conformance (§13) is exercised by `containment-vectors.json` —
64 vectors mapped to §13 — together with `containment-property-cases.json`
(784 cases pinning the §13.3–§13.7 narrowing laws).  `containment-crosswalk-vectors.json`
carries 44 cross-vendor vectors that map six adjacent capability
representations into CLC grants through pinned profiles and assert the
containment verdict the unchanged relation reaches (Appendix C).

**Genericity is exercised, not asserted.**  `crosswalk-vectors.json` in the same
directory carries 13 vectors in both directions: 5 that project a CLC decision
into the members an AEB crossing record asks of a native source (the members CLC
can establish, and the ones it explicitly does not), and 8 that map five foreign
capability representations —
OAuth RAR `authorization_details`, an AIC-JWT delegation authorization, an
Action Evidence Graph capability class, a UCAN `{with, can}` capability, and a
delegation chain — into CLC grants through pinned cross-walk profiles and assert
the decision the unchanged core reaches.  A profile is a few lines of mapping
written by whoever owns the foreign format; the core is not modified for any of
them.

The evidence side ships `evidence-vectors.json` in the same directory — 32 vectors covering the four evidence-side constraint types, their
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
this document declares **`CLC-1.14`**.  A capability input (grant,
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
- **CLC-1.9 is additive**: it adds the containment relation and conformance
  class CLC-D (§13) without changing any CLC-A verdict, reason code or
  vector.  A CLC-1.8 implementation that does not claim CLC-D MAY claim
  CLC-1.8 against this document and remains CLC-A conformant; an
  implementation that claims CLC-D MUST pass `containment-vectors.json`
  (§12).
- **CLC-1.10 is additive with a minor gate**: it adds the optional
  `param_bounds` field and its four reason codes (§6.5).  Every input that
  declares no `param_bounds` is unchanged, so a CLC-1.10 implementation reads
  every CLC-1.x input.  An input that **uses** `param_bounds` MUST declare
  CLC-1.10 or later; an implementation that does not implement §6.5 MUST refuse
  such an input through the minor gate (`unsupported_language_revision`) and
  MUST NOT ignore the field — silently dropping bounds would grant more than
  the input declares (fail-closed).

- **CLC-1.11 is additive**: it adds the `Resolve` function (§8.5) and its two
  input-error reason codes (`invalid_resolution`, `invalid_timestamp`) without
  changing any `Authorize` verdict, reason code or vector.  A CLC-1.10
  implementation that does not implement `Resolve` MAY claim CLC-1.10 against
  this document and remains CLC-A conformant; `Resolve` is exercised only when a
  consumer feeds a decision back, so no input shape is reinterpreted.  A
  `time:window` obligation is still delivered as `allow_unresolved` (§8.4) — the
  core clock evaluator of §8.5 runs only inside `Resolve` with a supplied `now`.

- **CLC-1.12 is additive**: it adds the derived function `ConstraintUnion`
  (§7.1) without changing any other relation, verdict, reason code or vector.
  The function is exactly the constraint projection of `Intersect` rule 3, so
  `Intersect`'s output is unchanged; an implementation that does not implement
  `ConstraintUnion` MAY claim CLC-1.11 against this document and remains CLC-A
  conformant.

- **CLC-1.13 is additive and CLC-D-scoped**: it adds `AuthorizeWithChain`
  (§13.11), a CLC-D function that fixes the order of `Contains` and
  `Authorize` over an effective-chain `Intersect`.  It changes no CLC-A
  verdict, reason code or vector; an implementation claiming only CLC-A is
  unaffected, and a CLC-D implementation adds it to its CLC-1.9-era
  `Contains` surface.

- **CLC-1.14 is additive**: it defines the intersection of `param_bounds`
  (`BoundMeet`, §6.6) so that `Intersect` can combine a grant carrying the
  bounds §6.5 defines.  It changes no verdict, reason code or vector for an
  input without `param_bounds`; it changes the refusal of an input **with**
  `param_bounds` from `invalid_params_binding` to the correct meet or empty-meet
  result.  An implementation that does not implement §6.6 MUST refuse a
  `param_bounds` input through the minor gate rather than intersect it wrongly.

- **CLC-A conformance and the minor gate are the two sides of one rule.**
  Claiming CLC-A (this section) means implementing the CLC-A-relevant
  semantics of the revision claimed — so an implementation that advertises
  `CLC-1.14` MUST implement `param_bounds` (grammar and the §6.6 meet), `Resolve`, `ConstraintUnion` and
  the §6.2 canonicalization, not merely tolerate their inputs.  The minor gate
  is the complement for an implementation that **lags**: it declares an older
  revision and refuses any input that uses a field or function introduced
  after it.  The two MUST agree — an implementation MUST NOT claim a revision
  higher than it implements (which would silently evaluate newer inputs), nor
  claim CLC-A while refusing a well-formed input of its own declared revision.

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

## 13. Delegation Containment

This section defines **containment**, the third grant-level relation of CLC-v1
alongside entailment (§6.1) and intersection (§7), and the conformance class
**CLC-D** that exercises it.  It is additive: it changes no CLC-A verdict,
reason code or vector, and a CLC-A implementation that does not claim CLC-D is
unaffected.  It was folded into this document from the formerly separate
containment extension, which is retired.

### 13.1 Motivation

The two relations the core defines answer different questions:

- **Entailment** (§6.1): does an *operation* fit inside a *grant*?
- **Intersection** (§7): what is the effective set when several grants cover one
  authority?

Neither answers the question a delegation chain asks of every hop: **is the
child's *declared* grant inside the parent's *declared* grant?**  Intersection
delivers a set that is necessarily common to the sources, but a result fitted to
two grants proves nothing that one of the grants' boundaries would not also
authorize on its own — it reasons about the *combined set*, not about a *child*
that must be a subset of a *specific parent*.

The AIC ecosystem needs the child-parent question at two concrete boundaries:

1. **Delegation** (`DelegationAuthTBS` vs. a principal's grant): a sub-agent's
   requested capabilities, constraints and delegation mode must lie inside what
   the principal authorized.  Without a shared relation this obligation is the
   *profile's* job and is re-implemented per profile, so two profiles can differ
   on the same sub-agent grant.
2. **Publication bound** (rule signing): a rule a certificate holder publishes
   must not exceed the holder's own grant.  This section states the general
   relation; `register/ruleexec` already applies the same idea in one instance
   (`RuleWithinSignerGrant`), and is a candidate early adopter.

Containment is intentionally **additive, not a CLC-v2 feature**: it does not
change any CLC-A verdict, does not touch the CLC-A corpus, and can be adopted by
any implementation that claims CLC-A without breaking compatible reading of
existing inputs.

### 13.2 Terminology and Notation

Grant and Operation are as defined in §2/§5 (identifier per §3, parameters per
§6.2, constraints per §8).  ``Contains(GP, GC)`` names the relation parent ``GP``
× child ``GC``.

- **Declared set** — the parameters a grant carries as constraints on
  operations (§6.2 value semantics: numbers bind as upper bounds, arrays as
  membership sets, objects recursively per key, explicit empty `[]`/`{}` deny
  the class, `{}`≡absent).
- **Bound** — a declared constraint value as interpreted by §6.2/§8.1 value
  semantics.
- **Narrower** — a child grant is narrower than its parent when every value it
  declares is within the parent's declared bounds, its key set is closed by the
  parent's, and its delegation mode does not widen the parent's.
- **Mode lattice** — an abstract carrier-defined order over delegation modes;
  the AIC-JWT ordering is pinned in §13.8.

### 13.3 Relation Signature

```
Contains(GP: Grant, GC: Grant) -> ContainmentResult

ContainmentResult = {        // JSON object (not ASN.1)
  "contains": <boolean>,     // false <=> one of the layers 2-4 failed
  "reason":   <string>       // resolved reason code (core §9.2 code)
}
```

- `contains` is `true` **only when** every layer of §13.4 passes.
- `reason` on success is empty; on failure it carries the **first failing
  layer's** reason code, per §13.4 layer order (deterministic: input order of the
  two grants never influences which layer reports first).
- The relation is **antisymmetric**: `Contains(A,B)` and `Contains(B,A)` both
  hold only when A and B denote identical declared sets and identical bounds
  (and equal modes); containment of two *distinct* grants in both directions is
  a contradiction and MUST NOT be reported.

### 13.4 Containment Algorithm

The relation resolves layers strictly in order; the first failure determines
the reason code.  Every layer is fail-closed: any doubt yields `false`.

#### 13.4.1 Layer 1: Grant validity

- If a grant identifier is malformed per §3, `Contains` returns
  `false` with the matching CLC-A syntax code (`invalid_capability_id` /
  `missing_capability_id`).  Validation errors are reused from the core,
  not re-invented.
- If `GC.Params` violates the grant-side parameter grammar (§6.2), the child is
  not a valid grant and `Contains` yields `false`
  (`invalid_params_<n>` codes as in the core).
- An invalid parent grant also yields `false`: a boundary that cannot itself be
  evaluated must not authorize a child.

#### 13.4.2 Layer 2: Identifier coverage

The child identifier must be covered by the parent identifier using **exactly
the CLC-v1 path-coverage relation** (the rules `Entails` applies to identifiers,
§6.1/§6.3, with parameters excluded — the identical keyset empty-object edge is
not relevant here because parameters are excluded from this layer by
construction):

- same namespace (`scheme:action-class`) — else `different_namespace`;
- same segment depth with equal literal segments, OR parent trailing `*`
  wildcard covering the child's trailing segments ("*" matches one or more
  segments, never zero) — else `child_exceeds_parent`.

Mid-identifier wildcards remain `unsupported_wildcard` per §3: this section does
not enlarge the v1 wildcard surface.

#### 13.4.3 Layer 3: Parameter narrowing

Every parameter the child declares must be *within* the parent's declared
bounds, using the §6.2 value-subset semantics, **and the key sets must be
identical** (symmetric closure).  The child and parent key sets are each the
union of `params` and `param_bounds` keys (§6.5):

- **number (from `params`)**: child value ≤ parent bound (upper bound only in
  `params`; richer bounds are expressed in `param_bounds`, below);
- **string / boolean**: exact equality with the parent's value;
- **array (enum)**: every child element must equal a member of the parent's set;
  a child empty array inside a non-empty parent enum is vacuously within it
  (child denotes "nothing", which is inside anything) — but a **parent** empty
  set denies the class (deny-when-declared), and a child empty set under a
  parent empty set is therefore `false` (`params_not_narrower`): the class is
  denied, not "narrowed to nothing";
- **object**: recursion per shared key, with the same symmetric key closure at
  every depth (a child object may not add a key the parent object does not
  declare, and may not omit one the parent declares);
- **`param_bounds` bound (§6.5)**: for a key with a Bound on the parent's side,
  the child's Bound for that key must be within it — a numeric family bound must
  have `min` raised or equal and `max` lowered or equal (`min_child ≥ min_parent`
  / `max_child ≤ max_parent`, and the child MUST declare a `min`/`max` the parent
  declares), a `step` must be an integer multiple of the parent's `step` (a
  coarser-or-equal grid whose values are a subset of the parent's allowed
  values), an `enum` family must be a subset with `min_items`/`max_items`
  tightened or equal, and a `nested` bound recurses.  A parent key that is
  required (`optional` absent or `false`) forces the child's key to be required;
  a child MAY keep an optional key optional or make it required, but MUST NOT
  turn a required parent key optional.  A child Bound that adds a family the
  parent does not declare, or omits a bound the parent declares, is
  `params_not_narrower` (the child would allow a value the parent denies);
- **key closure**: the child key set MUST equal the parent key set, both ways.
  A child that omits a parent-declared key would allow operations the parent
  denies (the missing key is `params_missing` in entailment); a child that adds
  a key the parent does not declare allows operations the parent denies
  (`undeclared_param`).  Either failure is `params_not_narrower`.  This is the
  same symmetric closure §6.2 layer 7 applies to an operation vs. a grant,
  carried over to grant-vs-grant comparison;
- **extra rule**: the parent's `{}` (or absent) params object is unconstrained
  and contains any child params; a child `{}` under a *bounded* parent is
  `false` (`params_not_narrower`) — declaring nothing is not the same as
  declaring a subset of the parent's bounds.

The presence semantics match §6.2 exactly: a grant (parent or child) whose
params are present-but-empty `{}` is unconstrained, identical to an absent
params object (§9.2/§6.2).

#### 13.4.4 Constraints are outside the relation

Constraints are **not** part of `Contains`.  A grant carries constraints (§8),
but they are a separate axis with a different composition rule:

- **Constraints compose by union (conjunction), not by subset.**  Along a
  delegation chain the effective constraint set is the *union* of every link's
  constraints (§7 `Intersect` already unions them).  A child therefore
  need not re-declare its parent's constraints, and adding or tightening a
  constraint only narrows.
- **`Contains` compares identifier and parameters only.**  It does not read,
  compare, or validate the `constraints` field: a constraint difference never
  changes the `Contains` verdict.
- **Constraint grammar and evaluation stay where they already are.**  Whether a
  constraint identity is recognized, whether its value is in grammar, and
  whether an operation satisfies it are the CLC-A concern of the consumer and
  `Intersect`/the decision function (including the `allow_unresolved`
  residual-obligation channel, §8.4).  This section neither re-decides nor
  weakens them.

Consequences a reviewer should take as intended: `Contains(P, C)` does **not**
by itself assert that `C`'s operation set is inside `P`'s when constraints are in
play — the parent's constraints are carried forward by the chain's union
(`Intersect`), and a consumer that uses `Contains` as its *only* gate must
compose the chain's intersections as well (§13.8).  This is the honest reading:
containment is a relation over the declared **identifier and parameter**
boundary, and constraints are enforced by the union, not by this relation.

#### 13.4.5 Delegation-mode lattice

Where a carrier defines a delegation mode, the child's mode must not widen the
parent's.  The lattice order is carrier-defined (CLC-D does not invent modes);
the AIC-JWT order is `authorized < representative` — a child may be
`authorized` under a `representative` parent, never the reverse.  Failure yields
`delegation_mode_not_narrower`.  A carrier without a mode concept SHALL treat
this layer as passing.  As with constraints, mode is a carrier-level concept:
the language relation `Contains(GP, GC)` takes no mode argument.

### 13.5 Reason Codes

CLC-D adds exactly three child-level reason codes to the core's registry.
Everything else reuses CLC-A codes.  An implementation MAY collapse
`child_exceeds_parent` for identifier failures into the core's
`capability_not_authorized` at a boundary that must not reveal policy shape
(§11), but MUST NOT collapse the other two.

| Code | Layer | Meaning |
|------|-------|---------|
| `child_exceeds_parent` | 2 | child identifier not covered by parent identifier |
| `params_not_narrower` | 3 | a child parameter is not within the parent's declared bounds / key set |
| `delegation_mode_not_narrower` | carrier | child delegation mode widens the parent's |

There is deliberately no constraint reason code: constraints are not part of the
relation (§13.4.4).

### 13.6 Conformance Class CLC-D

**CLC-D** is an optional conformance class stacked on CLC-A.  A conforming
implementation:

- MUST implement `Contains` (§13.4) and the three §13.5 reason codes, and pass
  the CLC-D corpus (§13.7);
- MUST (rev CLC-1.13) implement `AuthorizeWithChain` (§13.11) and pass the
  `authorize-chain-vectors.json` corpus, so the one-call chain check is exercised
  by the same class that owns containment;
- MUST NOT alter any CLC-A verdict, reason code, or the CLC-A corpus — this
  section is strictly additive;
- MUST treat containment as **declared-set comparison**: it declares no
  consequence about execution lifecycle, time windows after the fact, or
  post-hoc bounds; where a binding profile cannot establish containment at
  delegation time, the profile MUST NOT authorize.

An implementation claiming CLC-A does **not** claim CLC-D.  A delegation profile
(a binding profile (§13.8), an AIC-JWT DA validator, a certificate-issuance
stack) that needs the boundary check SHOULD require CLC-D of the module it
delegates to, and MUST NOT substitute intersection (§7) for containment.

**Implementation status (single-author parity).**  `Contains` is implemented in
all three reference implementations (Go: `register/semantics.Contains`;
Python: `aic-capability-demo/clc_semantics.py contains`; TypeScript:
`ts/clc_semantics.ts contains`) and mirrors the cases this section pins.
Agreement between implementations that share an author is a regression test for
this text, not independent validation — the §12 honesty rule applies unchanged
to CLC-D (see §13.7).

### 13.7 Corpus

Because CLC-D is a new relation, its corpus is new and independent of the CLC-A
suites (`vectors.json` / `property-cases.json` / `crosswalk-vectors.json` /
`evidence-vectors.json`).  The corpus ships as
`capability/data/_vectors/clc-d/containment-vectors.json` (**64** vectors) and a
forward-closure property file
`capability/data/_vectors/clc-d/containment-property-cases.json` (**784** cases
× 39 shared operations, generated by
`capability/scripts/gen-contain-property-cases.py`), plus a cross-walk corpus
`capability/data/_vectors/clc-d/containment-crosswalk-vectors.json` (**44**
vectors) that maps a carrier's native representation (AIC-JWT DA, OAuth RAR,
UCAN, delegation chain, and the adjacent agent drafts ATN, AAT, AIP, AAE, AOA,
AEGIS) to a grant on each side and asserts `Contains` (§13.9.3).  Rev CLC-1.13
adds `capability/data/_vectors/clc-d/authorize-chain-vectors.json` (**15**
vectors) pinning the fused `AuthorizeWithChain` relation (§13.11).
The vectors cover:

- **identifier coverage** (layer 2): trailing-wildcard coverage, namespace
  mismatch, depth mismatch, same-length literal mismatch, `unsupported_wildcard`
  kept stable, wildcard-requires-a-trailing-segment;
- **parameter narrowing** (layer 3): number upper bound at/under/over, enum
  subset / element-absent / scalar-member, empty child enum under non-empty
  parent, parent empty set deny-class, key-closure violation in both directions
  (child omits, child adds), nested object recursion and nested key closure,
  child `{}` under bounded parent, child `null` (layer-1 grammar), unconstrained
  parent `{}`;
- **constraint non-participation** (§13.4.4): a tighter, wider, added, dropped,
  or differently-identified child constraint, and a child constraint the parent
  lacks — every one MUST leave the verdict unchanged (all assert `contains`);
- **validity** (layer 1): malformed parent/child identifiers, `null` params;
- **symmetry**: both-directions containment identity, antisymmetry probe pair
  (contain-040/041), a fully-narrower combined grant.

The **delegation-mode lattice** is *not* part of the language-level corpus: the
relation `Contains(GP, GC)` takes no mode, so a profile that binds a carrier
mode (the AIC-JWT DA validator, §13.8) exercises it itself.  The language corpus
therefore ships no mode vectors; a carrier adopting CLC-D MUST add mode vectors
to its own profile corpus.

The **property** the property corpus checks is *forward closure*: for every
(parent P, child C) and every operation `o` in the shared sample,
`Contains(P, C)` MUST NOT raise, and
`Contains(P, C) ∧ Entails(C, o) ⟹ Entails(P, o)`.  This is the declared-set
consequence that makes a delegation boundary sound, and the reason the §13.5
collapse of layer-2 failures into `child_exceeds_parent` cannot weaken the
boundary.  On the shipped corpus the Go and Python/TS runs report the same
120 contained pairs and 30576 operation checks with zero violations.

The parity bar and the "independence of implementations" honesty rule of §12
apply unchanged to CLC-D: until two *independent* implementations agree, the
corpus is evidence that this text is implementable, not that it has been
independently interpreted.

### 13.8 AIC-JWT / AIC Certificate Binding

This subsection is a *cross-walk profile of the relation*, not part of the
language.  At the AIC delegation boundary the parent grant is produced from the
principal's authorization and the child grant from the
`DelegationAuthTBS`/AIC-JWT DA capabilities:

- **Parent grant** `GP`: the principal's capability entry (scheme:id params),
  plus principal-level `authorizationConstraints` projected as parent
  constraints, plus the principal's own delegation mode.
- **Child grant** `GC`: the sub-agent's requested capability
  (`Capability.SchemeId:CapabilityId`, `Parameters`), its `authorizationConstraints`,
  and its `DelegationMode`.
- **Boundary result**: `P_effective = P_principal ∩ C_agent ∩ P_gateway`
  keeps its intersection meaning — intersection determines the
  *effective* set; containment (§13.4) is the *per-child* admission predicate
  that runs before the intersection is composed, on each
  (parent-capability, child-capability) pair.  The child's constraints are **not**
  compared by containment; they are carried forward by the intersection's union
  (§13.4.4), so the principal's constraints remain in force in `P_effective`.
- A sub-agent that requests a capability the principal did not grant fails at
  layer 2 (`child_exceeds_parent`); a sub-agent whose requested params exceed the
  principal's declared bounds fails at layer 3; a sub-agent that widens the
  carrier's delegation mode fails the lattice (§13.4.5).  Binding profiles MUST
  surface the `reason` code into their audit trail, and MUST compose the
  intersection so the principal's constraints stay in force.

#### 13.8.1 Profile contract (for any binding profile)

A **binding profile** maps a carrier's native authorization structure to the CLC
grants `Contains` compares (§13.9.3).  The profile is the carrier's, not the
language's (a carrier's field names appear in its own profile, never in the
language text).  Because every §13.9.3 mapping is a profile, this subsection
states the obligations a conforming profile carries.  It adds no CLC-A or CLC-D
verdict and changes no relation.

1. **Resolve the carrier's own inheritance and defaults before mapping.**  The
   language has no inheritance, no default values and no "absent means inherit"
   rule (§13.10.1).  A carrier that resolves an absent dimension against an
   ancestor (AIP §4.4) MUST do so in the profile and emit the *resolved* declared
   set.  `Contains` is defined over the grants the profile emits, so an
   unresolved default is a profile defect, not a containment result.

2. **Preserve every identity dimension the carrier treats as identity.**  If the
   carrier treats two artifacts with the same name but different metadata as
   distinct capabilities (ATN §9.1: same `id`, different `schema.digest`), the
   profile MUST carry that metadata into the mapped grant — here, a trailing
   identifier segment — so a mismatch fails closed.  A profile MUST NOT drop an
   identity dimension and then compare the artifacts as equal.

3. **Residualize semantics the relation cannot see; never drop them silently.**
   Dimensions the mapped grant has no field for (AEGIS `allowed_roles`,
   `environment`, `risk_level`; AAE `validity`) are not compared by `Contains`.
   The profile either models them in its own document and enforces them outside
   the relation, or declares them out of scope — but it MUST NOT report
   containment as if they had been checked (fail-closed: what the relation
   cannot see, it does not permit).

4. **Do not invent carrier semantics the carrier does not state.**  A profile
   must not widen what the carrier leaves undefined into an allow.  AEGIS's
   dotted ids are hierarchical, but AEGIS grants capabilities individually and
   does not define domain-level containment, so the profile does not turn a bare
   domain into a namespace wildcard (ccx-042 fails closed).

5. **Non-goals (recorded, not prohibitions on carriers).**  Three properties are
   deliberately outside both the relation and the profile contract:
   - **union of authority sources** — a sub-agent that combines narrow delegated
     authority with broad independent authority (AEGIS §5.1, AOA) composes over a
     *set* of grants, which is carrier composition governance, not a per-pair
     predicate;
   - **chain-level verification** — `Contains` is a per-pair predicate, not a
     transitive closure; a chain check is the profile's iteration of `Contains`
     over hops (§13.9.3, `delegation-chain->clc-v1`);
   - **cross-carrier identity** — CLC defines no equivalence between two carriers'
     capability names; a profile MAY publish its own mapping, but the language
     asserts none.

### 13.9 Related Work and Positioning

This subsection is **informative** and carries no requirements.  It records why
a language-level containment relation is needed at all, how CLC relates to the
authorization work already in flight, and what the adoption risks are.

#### 13.9.1 The gap CLC fills

CLC **does not define a carrier** — it is not a credential format, a transport,
or a policy store.  It defines the *evaluation semantics* that carrier-facing
work leaves open: a deterministic decision, stable reason codes, and (here) a
containment relation.  The recurring shortfall in today's landscape is not "how
do I carry an authorization" but "how do two independent implementations agree
on what a carried authorization *means*, and on whether a delegated one stayed
inside its parent".

#### 13.9.2 What containment is for

1. **A standardizable evaluation core.**  Structured authorization payloads
   exist, but their semantics are pinned by each profile's own `type`
   vocabulary, so cross-implementation agreement is not guaranteed.  CLC
   supplies the deterministic decision function and the stable reason-code
   registry those profiles can reference instead of re-inventing.
2. **Verifiable attenuation.**  A delegation chain must only narrow.  Declaring
   attenuation is easy; *verifying* it at the receiving endpoint requires a
   shared relation.  `Contains` (§13.4) plus its reason codes
   (`child_exceeds_parent` et al., §13.5) turn "only narrows" from an
   application-layer assumption into a checkable language-level fact.
3. **One model for authorization and evidence.**  The core deliberately uses the
   same identifier and constraint model on the authorization side (the grant)
   and, prospectively, on the evidence side (the observed action), so an audit
   trail can be reasoned about with the same relation that authorized it.

#### 13.9.3 How CLC relates to adjacent work

The comparison below is by role, not by feature count: the other works are
carriers, profiles, or architecture, whereas CLC is the semantic layer.

Two principles keep the relationship complementary rather than competitive:

1. **CLC defines evaluation, not carriage.**  CLC does not define token
   formats, trust models, or policy languages.  The mapping from a carrier's
   native authorization structure to a CLC grant is the **carrier profile's
   responsibility**; CLC only fixes what the mapped grant then *means*.
2. **The core already ships consumption mappings.**  Appendix A ("Consumption
   Mapping") lists example consumers (AIC-JWT DA, RAR `authorization_details`,
   EMILIA AEB, delegation chains), and
   `capability/data/_vectors/clc-v1/crosswalk-vectors.json` pins executable
   cross-walk cases for the `oauth-rar->clc-v1`, `aic-jwt-da->clc-v1`,
   `emilia-aeg->clc-v1`, `ucan->clc-v1`, and `delegation-chain->clc-v1`
   profiles.  A carrier adopting CLC-D adds a containment case to that crosswalk
   rather than a new mapping mechanism.  CLC-D ships its own such corpus:
   `capability/data/_vectors/clc-d/containment-crosswalk-vectors.json` maps a
   native representation (AIC-JWT DA, OAuth RAR, UCAN, delegation chain, and the
   adjacent drafts ATN, AAT, AIP, AAE, AOA, AEGIS) to a grant on each side and
   asserts `Contains` — the attenuation analogue of the CLC-A cross-walk.

The mappings that are already pinned, and the ones a carrier would add, are:

| Carrier / native form | Maps to CLC | Relation | Status |
|-----------------------|-------------|----------|--------|
| AIC-JWT DA `capability[]` (`{id, params, constraints}`) | one Grant per entry | Entailment; CLC-D `Contains` for the `C_agent ⊆ P_grants` boundary | pinned (`aic-jwt-da->clc-v1`, ccx-001..005, ccx-013) |
| OAuth RAR `authorization_details` (`{type, actions[], params}`) | one Grant per action (`type:action`) | Entailment | pinned (`oauth-rar->clc-v1`, ccx-006..007) |
| UCAN `{with, can}` | Grant `{with:can}` | Entailment | pinned (`ucan->clc-v1`, ccx-008..009) |
| EMILIA AEG `capability_class` | Grant `{capability_class}` | Entailment | pinned (`emilia-aeg->clc-v1`) |
| Delegation chain (per-hop granted sets) | `Intersect` of the links | Intersection; CLC-D `Contains` per hop for attenuation | pinned (`delegation-chain->clc-v1`, ccx-010..012) |
| ATN Capability Manifest (`draft-somoza-dmsc-atn-agent-trust-negotiation` §5.1/§9.1/§9.2) | one Grant per capability: `atn/manifest-v1:<id>:<action>[:<schema_digest>]`; `resource_bounds` and numeric `conditions` → params | CLC-D `Contains` is the per-capability form of ATN's intersection; ATN's identity rule (same `id` **and** same schema digest) is carried by the digest path segment; `preconditions` are a **union** axis (§9.2), never compared | pinned (`atn-manifest->clc-v1`, ccx-014..017, ccx-043..044) |
| Attenuating Agent Tokens I4 (`draft-niyikiza-oauth-attenuating-agent-tokens` §4.5) | one Grant per tool: `aat/toolset-v1:<tool>`; the argument-constraint map → params | CLC-D `Contains` for `tools(derived) ⊆ tools(parent)` and the per-type constraint subsumption | pinned (`aat-i4->clc-v1`, ccx-018..023) |
| AIP attenuation walk (`draft-prakash-aip` §4.4) | Grant `aip/scope-v1:<capability>`; `budget` ceiling → params | CLC-D `Contains` for the per-dimension narrower-or-equal walk (scope, budget) | pinned (`aip-attenuation->clc-v1`, ccx-024..029) |
| AAE mandates and CONSTRAINTS (`draft-kroehl-agentic-trust-aae` §2.3/§3) | Grant `aae/mandate-v1:<action>`; unwrapped CONSTRAINTS values → params | CLC-D `Contains` for AAE's per-element "equal to or more restrictive" | pinned (`aae-constraint->clc-v1`, ccx-030..034) |
| AOA operation scope (`draft-liu-agent-operation-authorization` §6.2) | Grant `aoa/scope-v1:<operation>` | CLC-D `Contains` for the "scope string containment" the AS validates | pinned (`aoa-scope->clc-v1`, ccx-035..037) |
| AEGIS AIAM-1 delegation (`aegis-initiative/aegis-governance`, `AIAM1-DEL-010`) | Grant `aegis/action-v1:<domain>:<operation>`; numeric `context` bounds → params | CLC-D `Contains` for monotonic authority narrowing; `allowed_roles`/`environment`/`risk_level`/`scope` have no CLC field and are left to the carrier, not compared (see Appendix C) | pinned (`aegis-delegation->clc-v1`, ccx-038..042) |
| W3C ZCAPs capability document | Grant (delegation schema/type → id; caveats → params/constraints) | Entailment; CLC-D `Contains` for chained delegation | profile to be written by the ZCAPs adopter |

Two mapping notes the pinned profiles make explicit, because they are places a
reader could mistake a carrier's rule for the relation itself:

1. **A carrier's own "contains"/"subset" may name a *constraint type*, not the
   capability relation.**  AAT §4.5 defines argument-constraint types named
   `contains` and `subset` (a required-set superset and an allowed-set subset).
   Those are values *inside* `params`; the capability-level relation is still
   `Contains`, and the constraint axes compose by union across a chain.  The
   same applies to AAE's `allowed_domains` and AEGIS's `context` bounds.
2. **A profile resolves a carrier's inheritance and defaults before mapping, and
   must not invent semantics the carrier does not state.**  AIP resolves an absent
   dimension to its nearest ancestor (§4.4), so the profile maps an absent
   dimension to *no bound*, not to a bound.  AEGIS's dotted ids are hierarchical,
   but AEGIS grants capabilities individually and does not define domain-level
   containment, so the profile does **not** widen a bare domain into a namespace
   wildcard (ccx-042 fails closed).  `Contains` is defined over the *declared* sets
   the profile emits: the profile carries the carrier's resolution, and what the
   carrier leaves undefined the profile leaves undefined — it does not fill the
   gap with an allow.  The full contract is §13.8.1.

The rows marked *profile to be written* are placeholders: this document does not
guess another draft's field grammar.  A carrier profile lands as a `MapProfile`
case plus cross-walk vectors, exactly as the pinned profiles did.

| Work | Role | Relationship to CLC |
|------|------|---------------------|
| OAuth Rich Authorization Requests (RAR) | Structured `authorization_details` carried in the authorization request | RAR defines the *carriage* of structured authorization; CLC is a candidate *evaluation language* for the capabilities RAR declares.  Attenuating-agent-token work observes that RAR expresses a request but does not itself define how a holder derives or verifies a *narrower* token — the layer `Contains` addresses |
| OpenID Connect agent-identity claims | Agent capability claims in an ID Token | A profile could define how OIDC-delivered capabilities are evaluated and how a delegation chain is containment-checked |
| WIMSE AI Identity Management System (`draft-ietf-wimse-aims`) | Informational best-practice framework reusing WIMSE and OAuth; explicitly identifies gaps rather than defining a capability algebra | CLC is a candidate concrete evaluation language for the authorization step AIMS describes and a candidate answer to the "capability containment" gap it leaves open; the two are complementary, not competing |
| W3C ZCAPs | Linked-Data-Proof signed capability documents with caveats and chaining | ZCAPs defines the document/carrier; CLC can define the containment relation over its capabilities |
| UCAN | DID/IPLD authorization tokens with delegation and attenuation | Same split: UCAN is the carrier, CLC the semantics |
| AEGIS capability registry and AIAM-1 delegation ([AEGIS], `aegis-initiative/aegis-governance`) | Hierarchical dotted capability registry, per-grant `scope`/`constraints`, a deterministic decision algorithm with verdicts (allow/constrain/escalate/deny), and monotonic authority narrowing (`AIAM1-DEL-010`); composition is explicitly *not* closed under transitivity (`AIAM1-CAP-011`) | Closest in *goal* (capability declaration + deterministic evaluation + narrowing); differs in *form* — AEGIS is a governance architecture with a policy/registry layer, CLC a carrier-neutral decision function over grants.  `Contains` is the relation AEGIS's monotonic-narrowing check needs; AEGIS's non-transitive composition rule is compatible (CLC-D `Contains` is also non-transitive: it is a per-pair predicate, not a closure) |
| Agent Identity Protocol ([AIP], `draft-prakash-aip`) | Delegation-chain token with a Datalog policy layer and a structural attenuation walk (V4) over scope, budget, time, domains, principal | Overlaps CLC's entailment/intersection *functionally*, but pins a Datalog policy language.  AIP §4.4 makes the same distinction CLC-D does — attenuation is a property of capability content, not of the append-only container — so CLC can be the shared deterministic semantics such a checker is validated against |
| Agent Trust Negotiation ([ATN], `draft-somoza-dmsc-atn-agent-trust-negotiation`) | Capability Manifest JSON with schema binding, dimension semantics, and a Capability Intersection Algebra (§9) with per-dimension rules including `preconditions` union | Overlaps the capability-container target and defines an intersection; CLC-D supplies the *single-pair containment* predicate that runs before and alongside that intersection (§13.8).  ATN's ordered dimension lattices (`effects`, `external_calls`, …) are the carrier-level analogue of CLC-D's mode lattice (§13.4.5), which stays out of the language relation |
| Agent Operation Authorization ([AOA], `draft-liu-agent-operation-authorization`) | Operation-proposal/authorization JWTs with a `delegation_chain`; the AS validates that a sub-operation is "strictly narrower in scope" (§6.2) via policy templates, OPA, or scope-string containment | Same "no escalation beyond the original scope" goal; AOA's scope-string containment is exactly a carrier instance of `Contains`, and AOA's `delegation_chain` is the carrier for the chain CLC-D reasons over |
| Attenuating Agent Tokens ([AAT], `draft-niyikiza-oauth-attenuating-agent-tokens`) | Token chain with a capability lattice (`C(child) ⊆ C(parent)`, §4.1) and six attenuation invariants; I4 defines per-type constraint subsumption with Decidable/Sound/Deterministic requirements (§3.5.1) | The closest formal neighbour: `C(child) ⊆ C(parent)` is the property `Contains` decides, and AAT's naming of a constraint type `contains` is a caution that the *relation* and a *constraint value* must not be conflated |
| Agent Authorization Envelope ([AAE], `draft-kroehl-agentic-trust-aae`) | Verifiable Credential envelope with MANDATE/`CONSTRAINTS`/VALIDITY blocks and an explicit "equal to or more restrictive" definition per element (§3); warns of delegation amplification (§7.4) | AAE defines the carrier blocks and a closed, deterministic constraint language; CLC-D's `params_not_narrower` / `child_exceeds_parent` are the stable reason codes that make AAE's "strictly subordinate" check reportable |
| External Verifier Contract ([EVC], `draft-kondoju-evc`) | Standardizes *how* an external verifier is invoked and returns a verdict (allow/deny/denial codes, fail-closed exit semantics) | Orthogonal and complementary: EVC is the verdict *interface*, CLC-D is the decision *semantics* and its reason codes.  An EVC implementation can compute CLC-D's verdict and surface the same reason codes |
| Agent-auth architecture drafts (e.g. `draft-klrc-aiagent-auth`) | "Agent as workload", reusing existing mechanisms; notes that no single existing policy engine covers the full delegation-chain verification need | A natural consumer: CLC can be the evaluation language such a framework calls into |
| Dual-identity / attenuating-token drafts (e.g. `draft-ni-wimse-ai-agent-identity`, AAT above) | Bind agent identity to owner identity; define how a holder derives and a verifier checks a narrower token | Answers *who delegated* and *how derivation is carried*; CLC answers *what was delegated and whether it narrowed* |
| Agent interaction/delegation protocols (e.g. AIDP) | Interaction and delegation flow over capability systems | Capability-based sibling; CLC is the evaluation layer rather than the interaction flow |

The external names above are recorded as context and MUST be re-verified against
their current revisions before any submission or citation; this subsection makes
no claim about their exact present contents.  The mapping rows were checked
against these revisions on 2026-09-21: `draft-somoza-dmsc-atn-agent-trust-negotiation-00`
(§5, §6, §9), `draft-niyikiza-oauth-attenuating-agent-tokens-01` (§3.5, §4),
`draft-prakash-aip-01` (§3.3, §4.4), `draft-kroehl-agentic-trust-aae-02` (§2.3,
§2.5, §3), `draft-liu-agent-operation-authorization-02` (§3, §6),
`draft-ietf-wimse-aims-00`, and the `aegis-initiative/aegis-governance` repository
(AIAM-1 v0.1, `AIAM1-DEL-010`).  Each is an individual or informational draft (or
a non-IETF repository); none is a working-group standard, and the AEGIS material
is an informational architecture, not a specification with a formal standing.

#### 13.9.4 Where the demand actually is

The need for a shared evaluation layer is increasingly explicit in the
authorization community: the recurring complaint is not a lack of *carriage*
formats but a lack of agreement on *what a carried authorization means* and on
how a delegation chain is verified to only narrow.  The following distinction
determines what "demand" should be taken to mean here:

- **If demand means "adopted as a WG standard":** uncertain.  Several
  in-flight efforts (AIP, ATN, AOA, AEGIS, above) are attacking the same
  problem from different angles, and there is no consensus that a *separate*
  authorization language is wanted.  A standalone individual draft is unlikely
  to be adopted directly on that basis alone.
- **If demand means "used by implementers":** the need is real and immediate.
  Agent frameworks and enterprise security teams each re-implement an
  authorization check and each ask the same question — "what may this agent
  actually do, and did the delegation only narrow?".  A small,
  carrier-neutral, *tested* decision function plus corpus is directly reusable
  there.

The strategic consequence is that adoption is *earned by use*, not awaited from
a standards vote: the corpus and the reference implementations are the
contribution, and the standards reference follows if and when downstream
implementers cite it.

#### 13.9.5 Adoption risks

- **Carrier dependence.**  CLC only matters once a carrier (AIC, WIMSE, ZCAPs,
  UCAN, a RAR profile) binds it.  The §13.8 AIC-JWT cross-walk is one such
  binding; without bindings CLC has no reach.
- **Competing semantics, not a blank field.**  AIP, ATN, AOA, and AEGIS each
  define (or assume) evaluation semantics of their own.  CLC enters a field with
  several incumbents, so it must be *smaller* (a decision function, not a policy
  language or registry), *carrier-neutral*, and *tested* to be worth citing.
- **Ecosystem competition.**  A working group could prefer to define its own
  authorization meta-syntax rather than reference an external language.  The
  response is scope discipline: CLC defines the *evaluation* and nothing else,
  and stays small enough to be cited.
- **Implementation independence.**  The three current implementations share an
  author, so they are a regression test, not independent validation (§12,
  restated for CLC-D in §13.7).  Independent implementation remains the gating
  risk for any standards claim.

#### 13.9.6 Positioning statement

CLC is best positioned not as a standalone standard but as the **language
specification other standards reference** when they need to define authorization
evaluation and delegation narrowing.  Concretely: when an AIP-style Datalog
checker, an ATN-style condition evaluator, or an AEGIS-style policy evaluator
needs a shared, deterministic semantic to validate against or interoperate
with, CLC is a candidate.  Publishing CLC as the capability language core of a
wider agent-authorization architecture (the AIC direction) is exactly that
positioning; containment is kept additive so such a reference can be made
without disturbing the CLC-A core any adopter already implements.

### 13.10 Open Issues

§13.10 records the consciously-deferred gaps surfaced in review; the items
already landed as core revisions are marked *closed*, the rest are recorded for
later discussion.  Items marked *candidate v1.x* are candidates for the *core
language* to adopt without breaking CLC-A inputs; items under "CLC-D" would
extend containment itself.

#### 13.10.1 Parameter model rigidity (closed in CLC-1.10)

Landed as §6.5, the optional `param_bounds` field:

- **Number**: inclusive `min`/`max` intervals and a `step` multiple rule.
- **Enums**: array membership plus `min_items`/`max_items` cardinality.
- **Optional keys**: an `optional` marker exempts a declared key from the
  omission half of layer 7.
- **Defaults**: a `param_defaults` grammar with the precedence explicit >
  default > absent.

The rejected shape is a `{min,max}` object inside `params` — it would collide
with object recursion (§6.2), so the bounds live in a sibling field and no
existing grant changes meaning.

#### 13.10.2 Consumer obligations for `allow_unresolved` (closed in CLC-1.11)

§8.4 delivers residual obligations on an `allow_unresolved` verdict; §8.5
**now defines the consumer's feedback loop** and this item is closed:

- `Resolve(decision, resolutions, now?) -> Decision`, with each unresolved
  constraint reported as `satisfied` / `violated` / `unknown`;
- a propagation rule for partially-evaluated sets (all satisfied → `allow`, any
  violated → `deny` with `{type}:violated`, remainder → `allow_unresolved`);
- staleness/**TTL** semantics for `time:window` residuals: with `now`, the core
  clock evaluates the window and the discharge horizon is the current segment's
  end, so a cached `allow` expires with the window.

This went beyond the original "`Resolve` is core, TTL is profile policy" split:
both are now core (§8.5).  The coarser identity-level consumer gate `Discharge`
(the reference implementations' helper) remains as the `satisfied`-only case.

#### 13.10.3 Constraints as a union axis (closed in CLC-1.12)

This revision makes an explicit design decision: constraints are **not** part of
the containment relation (§13.4.4).  They compose by *union* (conjunction) along
a chain, which `Intersect` already implements, and no `Contains` layer reads
them.

`Contains` therefore stays the smaller relation — containment over
`(identifier, parameters)` — and the "what does the chain collectively
require?" question is answered by the separate derived function
`ConstraintUnion` (§7.1, new in CLC-1.12).  Folding the union into `Contains`
was considered and rejected: it would make the relation no longer a pure subset
on the declared tuple, and a null constraint check would then be able to hide a
broken identifier/parameter boundary.  A consumer wanting "the child's whole
authority is inside the parent's" composes the two: `Contains` per hop plus
`ConstraintUnion` over the chain.

#### 13.10.4 Containment as evidence, not authorization (closed in CLC-1.13)

§13.4 keeps containment a declared-set comparison.  A delegation *certificate*
binds a child grant; an operation-time authorization still needs the decision
function (§9).  CLC-1.13 adds the fourth relation `AuthorizeWithChain(chain,
op)` (§13.11), the one-call chain check named here: it evaluates `Contains` per
hop and then `Authorize` against the **intersection** of the chain, so the
parent's constraints (a union axis, outside containment) are not lost.  It is a
CLC-D function, not a core change; a CLC-A implementation is unaffected.

### 13.11 AuthorizeWithChain (fused chain authorization)

`Contains` is a declared-set comparison and `Authorize` is an operation-time
decision; a delegating consumer that has a chain often wants both in one call.
`AuthorizeWithChain` is that convenience, defined at the CLC-D layer:

```
AuthorizeWithChain(chain, op) → Decision      // chain = ordered Grant[], root first
```

1. An **empty chain fails closed**: `deny("absent_source")` (§7 rule 5).
2. For each adjacent pair `(chain[i], chain[i+1])`, evaluate `Contains`
   (§13.4).  The first hop that is not contained ends the call with
   `deny(reason)`, where `reason` is that hop's §13.5 code
   (`child_exceeds_parent`, `params_not_narrower`,
   `delegation_mode_not_narrower`).  This chain gate runs **before** op
   validation: a broken chain is reported even when the operation is also
   absent, because the chain is the subject of this function.
3. Otherwise compute the effective chain grant `G = Intersect(chain...)`
   (§7).  Because constraints are outside containment (§13.4.4), this step is
   what brings every ancestor's params **and** constraints into force —
   authorizing against the leaf grant alone would let an operation pass that
   violates an ancestor's constraints (the union axis is not in `Contains`).
   An `Intersect` refusal (`no_overlap`, `empty_bound_denies_class`,
   `invalid_params_binding`) is returned as `deny(reason)`.
4. Return `Authorize(G, op)` (§9) unchanged — `allow` / `allow_unresolved` /
   `deny` with its own §9 reason codes.

`AuthorizeWithChain` is a **CLC-D function**: it is not part of CLC-A, and an
implementation claiming only CLC-A is unaffected.  It introduces no new core
semantics — it fixes the order of two existing relations and refuses
fail-closed at each step.  A chain carrying `param_bounds` is authorizable:
step 3's `Intersect(chain...)` combines the hops' bounds with the §6.6 meet, so
an ancestor's bound (e.g. `max:100`) stays in force over a narrower child
(e.g. `max:50`).  Because §13.4.3 requires the declaration site of every key to
match at each hop, a valid chain never presents the cross-site case §6.6
refuses.  The two-grant form `AuthorizeWithChain(parent, child, op)` named in
§13.10.4 is the degenerate case `chain = [parent, child]`.

### 13.12 Revision and Governance

Containment is folded into this document's revision stream: its changes are
recorded in the Revision History and its conformance class CLC-D is declared in
§12.1 in step with the language revision (this revision is `CLC-1.14`; CLC-D
first appeared in `CLC-1.9`, folded from `EXT-00 rev 0`).

- A CLC-A input is unaffected by the addition of CLC-D; compatible reading of
  CLC-A inputs is the floor.
- CLC-D adoption is per-implementation: an implementation may claim CLC-A
  without claiming CLC-D.
- The corpus (64 containment vectors, 784 property cases, 44 cross-walk
  vectors, 15 `AuthorizeWithChain` vectors) is a draft snapshot; the README in
  `capability/data/_vectors/clc-d/` maintains the live count and the date the
  snapshot was generated.

---

## Appendix A: Consumption Mapping

The rows below are examples of consumers of this shared vocabulary, not
required profiles: conformance to CLC-A does not depend on any of them.

| Consumer | Grammar | Binding | Verdict | Notes |
|----------|---------|---------|---------|-------|
| AIC-JWT DA | capability[].id | Entailment (§6.1) | Decision (§9) | AIC-JWT §5 binding |
| EMILIA AEB | AEG capability_class | Match (§6.4) + Entailment (§6.1) | SATISFIED (§10) + Decision (§9) | AEB §3 decision levels (VERIFIED/MATCH/SATISFIED) + §5.1 ObservedAction + §7 AEC slots; a VERIFIED authorization artifact carries the Grant |
| RAR authorization_details | type="capability" | Entailment (§6.1) | Decision (§9) | [RFC9396] format |
| Delegation chain | each hop's declared set | Intersection (§7) | Decision (§9) | intersection over declared sets only; a hop that must stay inside its parent is checked with Containment (§13) |
| Delegation containment | parent and child boundaries | Contains (§13) | Containment verdict (§13) | per-hop `child ⊆ parent`; carrier vocabularies and reason-code mapping in Appendix C |

---

## Appendix B: Reference Vectors

**Grouping vs `kind` mapping**: The appendix groups vectors by semantic
category (B.1–B.6).  The machine-readable `vectors.json` uses a `kind`
field that collates these groups differently:
`kind=entail (47)` covers B.2 (8), the 35 params vectors that sit under
`kind=entail` (B.3's 39 rows minus `params-028/-029/-034/-036`, which are
`kind=decide`), and the four scheme stress-test entail vectors
(`clinical-001/-002`, `payments-001`, `data-002`); `kind=decide (50)`
covers the B.5 rows below (34), the seven combined decision vectors,
`payments-002` and `data-001`, the four params boundary decisions that
sit under `kind=decide` (`params-028/-029/-034/-036`, all four also
listed in B.3) and the three nested key-closure vectors
(`nested-001/-002/-003`);
`kind=intersect (14)` covers B.4 (10) plus the four combined vectors that
call the intersect function (`combined-004/-005/-008/-011`); `kind=syntax
(9)` is exactly B.1.  These counts are reproducible from the corpus itself:
every vector in `vectors.json` carries its `kind`, so the mapping is
machine-checkable rather than maintained by hand.

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

### B.2 Entailment (8 vectors)

| # | Grant | Operation | Expected | Derivation |
|---|-------|-----------|----------|------------|
| E1 | `std/database-v1:query:SELECT` | `std/database-v1:query:SELECT` | allow | literal match |
| E2 | `std/database-v1:query:*` | `std/database-v1:query:SELECT` | allow | trailing wildcard |
| E3 | `std/database-v1:query:*` | `std/database-v1:query:SELECT:deep` | allow | wildcard multi-segment |
| E4 | `std/database-v1:query:*` | `std/database-v1:admin:DDL` | deny | different namespace |
| E5 | `std/database-v1:query:*` | `std/database-v1:query` | deny | no trailing segment |
| E6 | `std/database-v1:query:SELECT` | `std/database-v1:query:INSERT` | deny | literal mismatch |
| E7 | `std/database-v1:*` | `std/database-v1:query:SELECT` | deny | class-position (product-segment) wildcard is v1-forbidden: only a trailing action segment may be `*` (§3; §9.1 layer 3) |
| E8 | `std/database-v1:*` | `std/database-v1:admin:DDL` | deny | same class-position wildcard; the v1-forbidden shape denies regardless of the action it faces (§3; §9.1 layer 3) |

### B.3 Params (39 vectors)

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
| P28 | `{}` | raw `{"n":1e-6,"s":"<494 a>"}` | deny(`invalid_params_size`) | the received text is 511 octets but the JCS form writes `1e-6` as `0.000001`, so the §6.2 step 4 size is 515 (`params-033`) |
| P29 | `{}` | `{"n":1e-6,"s":"<494 a>"}` (decoded) | deny(`invalid_params_size`) | decoded counterpart of P28: both boundaries agree (`params-034`) |
| P30 | `{}` | raw `{"n":1.0,"s":"<498 a>"}` | allow | the received text is 514 octets but the JCS form writes `1.0` as `1`, so the size is 512 and inside the cap (`params-035`) |
| P31 | `{}` | `{"n":1.0,"s":"<498 a>"}` (decoded) | allow | decoded counterpart of P30: a raw check counting the received token would refuse it (`params-036`) |
| P32 | `{}` | raw `{"s":"<100×U+1F600>"}` | allow | 100 literal astral characters are 408 JCS octets; counting UTF-16 code units would double the count and refuse (`params-037`) |
| P33 | `{}` | raw `{"s":"<100×\ud83d\ude00>"}` | allow | escaped spelling of P32: literal and escaped forms of one string MUST reach the same verdict and the same size (`params-038`) |
| P34 | `{}` | raw `{"s":"a\nb"}` (literal U+000A) | deny(`invalid_params_number`) | a literal control character is not valid JSON text; Go and Python refused it already (`params-039`) |
| P35 | `{}` | `{"x":"<260×é>"}` (decoded) | deny(`invalid_params_size`) | 260 U+00E9 code points serialize to 528 JCS octets > 512; non-ASCII sizes are measured on the canonical UTF-8 form, never in code points or UTF-16 units (`params-028`, rev CLC-1.4) |
| P36 | `{}` | `{"x":"<251×é>"}` (decoded) | allow | 251 U+00E9 serialize to 510 octets ≤ 512; the positive side of P35 (`params-029`, rev CLC-1.4) |
| P37 | `{"s":"x"}` | raw `{"s":"<251×\u00e9 escapes>"}` | allow | the same 510-octet string spelled with `\u00e9` escapes reaches the same verdict and the same size as the literal form of P36 (`params-030`, rev CLC-1.4) |
| P38 | `{"limit":100}` | raw `{"s":"\ud800"}` | deny(`invalid_params_number`) | a lone surrogate escape is not valid Unicode: refused at the raw boundary, never repaired to U+FFFD (RFC 8785 §3.2.2.2; §6.2 step 2; `params-031`, rev CLC-1.6) |
| P39 | `{}` | raw `{"s":"\ud83d\ude02"}` | allow | a valid surrogate pair is one character (U+1F602, four UTF-8 octets) and counts as such under the size rule (`params-032`, rev CLC-1.6) |

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

### B.5 Decision (34 vectors)

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
| D29 | multi-grant allow_unresolved: G1 `network:cidr` + G2 `time:window` | `allow_unresolved`, `unresolved:[both]` | residual obligations union across covering grants (`decide-035`, §9.1/§8.4) |
| D30 | operation id uses a forbidden wildcard shape (`*:query:SELECT`) | deny("unsupported_wildcard") | wildcard-shape detection precedes the base grammar, and layer 1 propagates the specific code rather than `invalid_capability_id` (`decide-018`, §3/§9.1) |
| D31 | grant bounds `max_rows:10`, operation carries `max_rows:"garbage"` | deny("max_rows:violated") | op-side value outside the §8.1 domain (finite non-negative integer) fails closed, never passes unchecked (`decide-031`, rev CLC-1.4) |
| D32 | grant bounds `max_rows:10`, operation carries `max_rows:true` | deny("max_rows:violated") | boolean is outside the §8.1 domain (`decide-032`, rev CLC-1.4) |
| D33 | grant bounds `max_rows:10`, operation carries `max_rows:-1` | deny("max_rows:violated") | a negative is outside the §8.1 domain (`decide-033`, rev CLC-1.4) |
| D34 | grant bounds `max_rows:10`, operation carries `max_rows:1.5` | deny("max_rows:violated") | a fraction is outside the §8.1 domain (`decide-034`, rev CLC-1.4) |

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

**Total: 120 vectors**

> Decisions D17–D28 are the corpus pin for the
> residual-obligation channel `unresolved` / `allow_unresolved`, the §8.1
> `(scheme,type)` identity, the `invalid_constraint` value grammar and the
> §9.1 multi-grant aggregation.  `decide-025/-026` and `syntax-007/-008`
> pin the §3 scheme grammar; `decide-021/-022`, `decide-019/-024` pin §8.1
> time/network value shapes; `decide-019` pins the no-cross-midnight rule;
> `decide-028/-029/-030` pin §9.1 (`{}`≡absent, any-allow union, deterministic
> deny reason); `decide-035` (D29) pins multi-grant residual-obligation
> union across covering grants; `decide-031/-032/-033/-034` (D31–D34) pin
> the §8.1 `max_rows` request-side value domain (rev CLC-1.4); `decide-018`
> (D30) pins §3 wildcard-shape detection ahead of the base grammar.

> The corpus additionally carries 6 scheme stress-test vectors
> (`clinical-001/-002`, `payments-001/-002`, `data-001/-002`) exercised
> against `std/{clinical,payments,data}-v1`: their enum/bound outcomes follow
> the grouping rules above (→ B.3 params semantics), and `payments-002`
> additionally exercises §8 fail-closed `unknown_constraint` for a
> scheme-scoped constraint type.  These vectors add no new normative rule;
> they exist to record the v2 requirements evidence, not to extend v1.
> `undeclared-001/-002` (→ B.5 D13/D14) pin the §6.2 key-closure rule.
> `params-006`/`params-013` (→ B.3 P6/P13) close two previously-unmapped
> rows; `params-020/021` (→ P20/P21) are the positive boundary cases of
> `params-018/019`; `decide-016/017` (→ D15/D16) pin the §9.1 pre-check and
> layer-1 paths for absent/empty grant and id-less operation;
> `intersect-007..010` (→ I7..I10) pin §7 rules 5–6 including empty-params
> sources, order independence, and a params-free identifier comparison.

### B.7 Containment (external corpus)

The delegation-containment relation (§13) is pinned by a separate corpus at
`capability/data/_vectors/clc-d/`: `containment-vectors.json` (64 vectors,
groups: identifier coverage, parameter narrowing, constraint
non-participation, validity, symmetry), `containment-property-cases.json`
(784 forward-closure cases over 39 shared operations) and
`containment-crosswalk-vectors.json` (44 cross-vendor vectors).  It is not
re-tabulated here; the corpus README maintains the live count and the snapshot
date.

### B.8 Extended parameter bounds (external corpus)

The §6.5 `param_bounds` grammar is pinned by
`capability/data/_vectors/clc-v1/param-bounds-vectors.json` (43 vectors,
groups: numeric interval/step, enum cardinality, optional keys, nested
recursion, the binding rule, malformed bounds, scheme defaults), with
`param-bounds-vectors.schema.json`.  It is not re-tabulated here.  These
vectors exercise a CLC-1.10 field; a CLC-1.9 or earlier implementation refuses
them through the §12.1 minor gate rather than ignoring the bounds.

### B.9 Resolve (external corpus)

The §8.5 `Resolve` function is pinned by
`capability/data/_vectors/clc-v1/resolve-vectors.json` (26 vectors, groups:
terminal pass-through, all-satisfied → allow, partial → allow_unresolved,
violated → deny, the `time:window` core clock in and out of window, TTL
re-evaluation, bare assertion without `now`, conflict precedence and malformed
input), with `resolve-vectors.schema.json`.  Vectors that exercise the core
clock carry `now`; a CLC-1.10 implementation that does not implement `Resolve`
is unaffected by this corpus.

### B.10 ConstraintUnion (external corpus)

The §7.1 derived `ConstraintUnion` projection is pinned by
`capability/data/_vectors/clc-v1/constraint-union-vectors.json` (12 vectors:
union over one/many grants, duplicate folding across sources, deterministic
ordering, empty constraints, and the empty-chain `absent_source` refusal),
with `constraint-union-vectors.schema.json`.

### B.11 AuthorizeWithChain (external corpus)

The §13.11 fused chain check is pinned by
`capability/data/_vectors/clc-d/authorize-chain-vectors.json` (15 vectors:
empty chain, broken identifier/parameter hop, a broken hop reported before op
validation, the degenerate two-grant form, ancestor-constraint enforcement via
the effective intersection, the `param_bounds` refusal, and pass-through of
`allow` / `allow_unresolved` / operation-layer `deny`), with
`authorize-chain-vectors.schema.json`.

### B.12 BoundMeet (external corpus)

The §6.6 intersection of `param_bounds` is pinned by
`capability/data/_vectors/clc-v1/param-bounds-meet-vectors.json` (groups:
numeric `min`/`max`/`step` meet including the coarser-grid and fail-closed
step cases, enum intersection and tightened cardinality, `optional` conjunction,
`nested` recursion, numeric∩enum reduction, the empty meets (`min>max`,
disjoint enums, scalar∩nested → `no_overlap`), the unrepresentable crosses
(cardinality-only enum, incommensurable steps → `invalid_params_binding`), the
identity empty Bound, and the cross-site refusal), with
`param-bounds-meet-vectors.schema.json`.

---

## Appendix C: Containment Carrier Vocabulary and Reason-Code Mapping

This appendix is **informative**.  It puts a carrier's own vocabulary and its
failure codes beside CLC-D's, so an adopter can explain a containment verdict in
the carrier's terms — and can see exactly where the mapping is many-to-one and
therefore not reversible without carrier context.  The profiles named here are
the pinned ones in §13.9.3; the profile obligations are §13.8.1.

### C.1 Vocabulary

| Carrier | Carrier term | CLC term used here | Note |
|---|---|---|---|
| CLC-D | identifier `scheme:action:path` | `CapabilityId` | the relation's left/right identity |
| CLC-D | parameter bound | `params` | declared bound; absent or `{}` = unconstrained |
| CLC-D | constraint (`varwof/constraint-v1:*`) | `constraints` | **union** axis, outside `Contains` (§13.4.4) |
| ATN | `resource_bounds`, numeric `conditions` | `params` (upper bounds) | §9.2 takes the per-dimension `min` |
| ATN | `id` + `schema.digest` | identifier segments | digest mismatch ⇒ distinct capability (ccx-043) |
| ATN | `preconditions` | — (union axis) | never compared by `Contains` |
| AAT | `tools(derived) ⊆ tools(parent)` | identifier coverage | |
| AAT | argument constraints (`exact/range/one_of/…`) | `params` | AAT's own `contains`/`subset` are *constraint types*, not the relation |
| AIP | scope, budget, expiry, domains | identifier + `params` | absent ⇒ nearest ancestor, resolved by the profile |
| AAE | `mandate.actions` | identifier coverage | |
| AAE | CONSTRAINTS `value` (unwrapped) | `params` | numeric ≤, allowlist ⊆ |
| AAE | `validity` | — (carrier/time, CLC-A R1) | not a declared `Contains` input |
| AOA | operation scope string | identifier path | `*` maps to a CLC trailing wildcard |
| AEGIS | dotted `capability` | identifier path | |
| AEGIS | numeric `context` | `params` | |
| AEGIS | `allowed_roles`, `environment`, `risk_level`, `scope` | — (**not mapped**) | identity/policy dimensions with no CLC field; the profile leaves them to the carrier (C.3) |

### C.2 Failure-code mapping

Carrier failure codes collapse onto CLC-D's three codes.  The mapping is
many-to-one and is therefore **not reversible** without the carrier recording
which of its own codes applied before mapping.

| Carrier | Carrier code / failure | CLC-D reason |
|---|---|---|
| ATN §9.1 identity rule | different `id` | `different_namespace` |
| ATN §9.1 identity rule | different `schema.digest` | `child_exceeds_parent` |
| ATN §9.2 | raised `resource_bounds` | `params_not_narrower` |
| AAT I4 | tool outside parent set | `different_namespace` |
| AAT I4 | constraint not subsumed | `params_not_narrower` |
| AIP §4.4 | `aip_scope_insufficient` | `child_exceeds_parent` |
| AIP §4.4 | `aip_budget_exceeded` | `params_not_narrower` |
| AIP §4.4 | `aip_depth_exceeded` | `child_exceeds_parent` |
| AAE §3 | action not a subset | `different_namespace` |
| AAE §3/§7.4 | constraint not more restrictive | `params_not_narrower` |
| AOA §6.2 | scope not strictly narrower | `child_exceeds_parent` |
| AEGIS AIAM1-DEL-010 | authority exceeds the delegator's | `params_not_narrower` |
| AEGIS AIAM1-DEL-011 | capability the delegator lacks | `different_namespace` |

The collapse is visible in the right column: `child_exceeds_parent` is reached by
both AIP scope and AIP depth failures and by an ATN digest mismatch, and
`params_not_narrower` by every carrier's bound-widening.  A carrier that needs
its own code back must keep it alongside the CLC-D reason; CLC-D guarantees the
stable language-level reason, not the carrier's.

### C.3 Profile obligations exercised by the corpus

Two of the §13.8.1 obligations are visible in the pinned vectors:

- **Identity dimensions the language cannot carry fail closed.**  ATN's schema
  digest is carried as an identifier segment (ccx-043) rather than dropped, so a
  digest mismatch is `child_exceeds_parent` instead of a silent match.
- **Semantics the relation cannot see are a profile limitation, not a CLC gap.**
  AEGIS's `allowed_roles`/`environment`/`risk_level` and AAE's `validity` have no
  CLC field; the profile leaves them to the carrier and asserts nothing about
  them.  They are not modelled here, and a profile MUST NOT claim
  containment of a dimension the relation cannot see.

---

## Security Considerations

- **Fail-closed**: undefined/malformed/unknown → deny.
- **Deny-when-declared**: empty bounds deny the class.
- **No canonical broadening**: segment-boundary, not lexical prefix.
- **Composition narrows only**: an intersection removes authority.  Whether a
  *delegated* grant stays inside its parent's boundary is the containment
  question §13 answers (`Contains`); intersection alone (§7) does not answer it,
  and a delegation profile MUST NOT substitute one for the other.
- **Containment is fail-closed by construction**: every `Contains` layer
  defaults to `false`; a grant pair any layer cannot validate is refused, with
  no warning-then-allow path (§13.4).
- **Containment is not a constraint oracle**: `Contains` does not read
  constraints (§13.4.4).  A consumer that uses `Contains` as its *only* gate MUST
  compose the delegation chain's `Intersect` so the parent's constraints stay in
  force; otherwise a child that omits a parent constraint could be admitted
  while the constraint is unenforced.  `allow_unresolved` is orthogonal to
  containment and MUST NOT be read as a containment result.
- **Containment reason-code leakage**: `child_exceeds_parent` reveals that a
  child requested an identifier the parent does not cover.  A boundary that must
  not leak policy shape MAY collapse that single code into
  `capability_not_authorized` (never `params_not_narrower`, §13.5).
- **Mode lattice must be carrier-pinned**: an implementer that maps
  `authorized`/`representative` the wrong way round inverts the boundary; §13.8
  pins the AIC-JWT ordering, and other carriers MUST pin theirs in the profile that
  adopts CLC-D.
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
- **A core-clock discharge is time-bounded**: when `Resolve` (§8.5) evaluates a
  `time:window` obligation with a supplied `now`, the discharge is valid only
  for the segment containing `now`.  A consumer MUST NOT cache the resulting
  `allow` past that segment's end — it re-invokes `Resolve` with a current `now`
  before acting, or derives the horizon from the segment end.  Caching a
  clock-based `allow` turns a window into an unbounded permit.

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

The containment relation (§13) defines three additional reason codes
(`child_exceeds_parent`, `params_not_narrower`,
`delegation_mode_not_narrower`); they are part of the same fixed set, and no
constraint reason code is defined for containment because constraints are
outside the relation (§13.4.4).

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
- Containment reasons (§13) are emitted to the child's requestor at the
  delegation step, not to end-users, and the child receives the failure code,
  not the parent's declared bounds.  Where bounds themselves are sensitive
  (e.g. network/scope declarations), a profile SHOULD log codes, not values.

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
(Sections 4.2, 4.3 and 6.4).  For revisions 1.6 to 1.8 he re-ran the three
implementations and reported the raw-boundary cases those revisions fix: the
HTML-escaping and key-order defects in the canonical serializer, the decoded
paths that disagreed with the raw path on malformed Unicode, and the raw size
checks that counted a number by its received spelling and a literal astral
character by UTF-16 code unit.  Revision 1.9 folds the delegation-containment
relation and the CLC-D class into this document (Section 13, Appendix C),
retiring the formerly separate containment extension, and pins it against six
adjacent capability drafts (ATN, AAT, AIP, AAE, AOA, AEGIS) reviewed on
2026-09-21.

## References

### Normative References

- [RFC2119] S. Bradner, "Key words for use in RFCs to Indicate Requirement
  Levels", BCP 14, RFC 2119, DOI 10.17487/RFC2119, March 1997,
  <https://www.rfc-editor.org/info/rfc2119>.
- [RFC8174] B. Leiba, "Ambiguity of Uppercase vs Lowercase in RFC 2119 Key
  Words", BCP 14, RFC 8174, DOI 10.17487/RFC8174, May 2017,
  <https://www.rfc-editor.org/info/rfc8174>.
- [RFC3339] G. Klyne and C. Newman, "Date and Time on the Internet:
  Timestamps", RFC 3339, DOI 10.17487/RFC3339, July 2002,
  <https://www.rfc-editor.org/info/rfc3339>.
- [RFC7493] T. Bray, Ed., "The I-JSON Message Format", RFC 7493,
  DOI 10.17487/RFC7493, March 2015,
  <https://www.rfc-editor.org/info/rfc7493>.
- [RFC8785] A. Rundgren, B. Jordan, S. Erdtman, "JSON Canonicalization Scheme
  (JCS)", RFC 8785, DOI 10.17487/RFC8785, June 2020,
  <https://www.rfc-editor.org/info/rfc8785>.

### Informative References

- [RFC9396] T. Lodderstedt, et al., "OAuth 2.0 Rich Authorization Requests",
  RFC 9396, DOI 10.17487/RFC9396, May 2023,
  <https://www.rfc-editor.org/info/rfc9396>.
- [AIC-JWT] J. Wei, "AI Agent Identity Certificate (AIC) JSON Web Token
  Profile", draft-wei-aic-jwt-01, Work in Progress, September 2026.
- [CAID] "Canonical Action Identifier",
  draft-schrock-canonical-action-identifier-02, Work in Progress.  Section 4.5
  defines the optional `occurrence_id`; Section 7 keeps occurrence allocation and
  one-time consumption outside the identifier.
- [EMILIA-AEB] "Action Evidence Boundary",
  draft-schrock-action-evidence-boundary-05, Work in Progress.
- [ATN] "Agent Trust Negotiation", draft-somoza-dmsc-atn-agent-trust-negotiation-00,
  Work in Progress.  §9 defines a capability intersection algebra; §5.1/§9.1 an
  identity rule over `id` and `schema.digest`.
- [AAT] "OAuth 2.0 Attenuating Agent Tokens",
  draft-niyikiza-oauth-attenuating-agent-tokens-01, Work in Progress.  §4.1
  states `C(child) ⊆ C(parent)`; §4.5 (I4) defines per-type constraint
  subsumption.
- [AIP] "Agent Identity Protocol", draft-prakash-aip-01, Work in Progress.
  §4.4 defines a structural attenuation walk over scope and budget.
- [AAE] "Agentic Trust Agent Authorization Envelope",
  draft-kroehl-agentic-trust-aae-02, Work in Progress.  §3 defines
  "equal to or more restrictive" per constrained element.
- [AOA] "Agent Operation Authorization",
  draft-liu-agent-operation-authorization-02, Work in Progress.  §6.2 requires a
  sub-operation to be strictly narrower in scope.
- [EVC] "External Verifier Contract", draft-kondoju-evc-02, Work in Progress.
- [CLC-CORPUS] J. Wei, "Capability Language Core — conformance corpus,
  schemas and working documents", commit c97fd93, September 2026.
  <https://github.com/varwof/capability/tree/c97fd93e20446db39d5b57f76df2aea46ad48a25>
- [AEGIS] AEGIS Governance, `aegis-initiative/aegis-governance`, repository
  (AIAM-1 v0.1).  `AIAM1-DEL-010` requires monotonic authority narrowing;
  `AIAM1-CAP-011` states composition is not closed under transitivity.
