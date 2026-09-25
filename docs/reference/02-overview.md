# 02 · Overview — what CLC-v1 is, and what it deliberately is not

> **Normative source:** [`capability-language-core-v1.md`](../capability-language-core-v1.md) Abstract, §1 Design Principle, §11 Semantic Boundary
> This page is a readable guide. In case of conflict, the normative specification wins.
> Status: Preview — not for production use.

## TL;DR

CLC-v1 is a **minimal, executable, carrier-neutral language** that says what an agent is authorized to do. It evaluates one relation — *grant ∈ operation* — and answers with a three-valued verdict (`allow`, `deny`, `allow_unresolved`) plus a stable reason code. It is deliberately **not** a policy engine, a trust model, or a wire format: it defines *what* to evaluate, never *how* to carry, sign or verify it.

## The five core models

CLC-v1 rests on five foundational abstractions (spec §1). The same five appear on both the authorization side and the evidence side; only the direction differs.

| # | Model | Authorization side | Evidence side | Reference page |
|---|-------|--------------------|---------------|----------------|
| 1 | **Identity** | CapabilityId (what class of thing is authorized) | ActionId (which concrete instance happened) | [`03-identifiers.md`](03-identifiers.md), [`04-actions.md`](04-actions.md) |
| 2 | **Grant** | a declared permission, possibly narrowed | an asserted fact | [`05-grants.md`](05-grants.md) |
| 3 | **Binding** | entailment: grant ⊆ operation | match: evidence ↔ action | [`06-entailment.md`](06-entailment.md) |
| 4 | **Constraints** | params / `param_bounds` / constraints | evidence requirements / freshness | [`07-parameters.md`](07-parameters.md), [`08-constraints.md`](08-constraints.md) |
| 5 | **Intersection** | ∩ of grants from several sources, then decision | — | [`09-intersection.md`](09-intersection.md) |

The design intent behind these five — including what the language **refuses** — is spelled out in the twelve principles of `capability-language-core-principles-v1.md`:

> P1 minimal core · P2 no control flow · P3 immutable values ·
> P4 domains, not types · P5 deterministic and terminating ·
> P6 fail-closed · P7 define once, consume everywhere ·
> P8 carriers separate from semantics · P9 local decidability ·
> P10 bounded work · P11 composition narrows only ·
> P12 ≥2 independent implementations

Two principles matter most for reading everything else:

- **P6 fail-closed** — every unrecognized or malformed input is a deny with a reason code, never a silent allow or a crash.
- **P11 composition narrows only** — intersecting grants never produces a *wider* permission than any source; the corpus pins this with 1184 property cases (§7, the P11 "wall").

## The verdict is three-valued

| Verdict | Meaning | What a consumer may do |
|---------|---------|------------------------|
| `allow` | request is fully inside the covering grant and every evaluated constraint holds | invoke |
| `deny` | not inside any grant, or a constraint/param violation | refuse; the reason code says why |
| `allow_unresolved` | inside a grant, but at least one recognized constraint was **not evaluated** by the core (e.g. `network`, `time`) | discharge each `unresolved` obligation yourself, or refuse — MUST NOT treat it as `allow` (§8.4) |

The third verdict is not evidence and not "allow with a caveat": §11 is explicit that `allow_unresolved` is an *authorization* result and must not be read as "evidence still required". Consumers that cannot evaluate an obligation MUST deny.

## The carrier-neutral boundary

CLC-v1 defines exactly *what* to evaluate and *what the output means* — and stops there. §11 lists what the language does **not** define:

- **Trust models** — who signs what, issuer trust, delegation chains (belongs to AIC-JWT, OAuth, SPIFFE, …).
- **Native verification** — signature checking, schema validation, freshness enforcement (each native artifact's spec).
- **Execution lifecycle** — consumption, invocation, reconciliation, outcome classification (EMILIA AEB or equivalent).
- **Receipt or token formats** — the wire formats for carrying grants, evidence, or bindings.

The consequence is a clean cut: *CLC-v1 defines **what**; consumers define **how** and **what to do with** the result.* A §6.2 input-boundary refusal is likewise anchored to the text as received — a normalized decoded value is not the same thing, and a pipeline that can apply a permit to a request whose text was never checked has left the CLC boundary (§11).

## Constraints: evaluated, or recognized-but-unevaluated

The core recognizes only `max_rows`, `time` and `network` under the `varwof/constraint-v1` scheme (§8.1):

- **`max_rows`** — evaluated by the core against the request's `max_rows` param (`max_rows:violated`).
- **`network` / `time`** — recognized, grammar-checked, carried on `unresolved`, not evaluated here (§8.4). This is the *residual-obligation channel* — obligations are surfaced explicitly, never silently dropped.

Anything else — any other scheme, any other type — denies `unknown_constraint`. Details: [`08-constraints.md`](08-constraints.md).

## Where conformance stands (honest scope)

- **CLC-A** (authorization side) is the claimed baseline; it is exercised by the published corpus of `vectors.json` and `property-cases.json` (§12).
- **CLC-D** (containment, §13) ships with this revision and its own corpus — see [`12-containment.md`](12-containment.md).
- **CLC-E** (evidence side) is implemented and pinned by a corpus but **not claimed** in this revision.
- The three implementations (Go/Python/TypeScript) **share an author**; their agreement is a regression test *for the text*, **not independent validation**. The §12 bar of two independent implementations (principle P12) is recorded as **unmet**.

Full wording, and what an implementation must do to claim each class: [`13-conformance.md`](13-conformance.md).

For the record, the spec also carries Security, IANA and Privacy Considerations and a References section (normative: BCP 14, RFC 2119/RFC 8174, RFC 3339, RFC 7493, RFC 8785) that these pages do not reproduce — they are authoritative in the normative document and worth reading before shipping.

## Common pitfalls

- **Treating `allow_unresolved` as `allow`** is the single most dangerous reading mistake; it defeats the fail-closed design (§8.4/§11).
- **Assuming CLC is a policy language.** There is no control flow, no mutable state, no general-purpose logic (P2/P3); decisions are deterministic and terminating (P5).
- **Reading the carrier into the semantics.** A grant/SIGNED in another envelope does not make CLC define signatures; that is the carrier's job (P8).
- **Expecting `intersect` to widen.** Because composition narrows only (P11), intersecting two grants never grants more than either source.

---
← [01-quickstart.md](01-quickstart.md) · → [`03-identifiers.md`](03-identifiers.md) · related: [`13-conformance.md`](13-conformance.md), [`15-glossary.md`](15-glossary.md)