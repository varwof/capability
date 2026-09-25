# 04 · Actions — Operation, ObservedAction, Identity

> **Normative source:** [`capability-language-core-v1.md`](../capability-language-core-v1.md) §4 (Action)
> This page is a readable guide. In case of conflict, the normative specification wins.
> Status: Preview — not for production use.

## TL;DR

The language is about actions. It defines two concrete Action forms and two identity levels:

- **Operation** (§4.1) — the authorization-side request: a CapabilityId plus parameters.
- **ObservedAction** (§4.2) — the evidence-side artifact: the effect boundary's projection of a material action, bound to a digest.
- **Identity** (§4.3) — **Class** = CapabilityId (covers a class of actions); **Instance** = ActionId (a digest identifying the material content of one action).

Authorization sees the *class*; evidence sees the *content instance*. The two check different things and MUST NOT be conflated: "Entailment checks class coverage; Match checks content binding" (§4.3).

## 4.1 Operation (authorization side)

An Operation is the thing being authorized: `id` (CapabilityId) + optional `params`.

```
{ "id": "std/database-v1:query:SELECT",
  "params": { "tables": ["customers"], "limit": { "max": 50 } } }
```

- The `id` is the CapabilityId whose class membership is tested by [entailment](06-entailment.md).
- The `params` are the request's parameter binding, subject to [parameters](07-parameters.md) rules.
- An Operation with no `id` is refused **at layer 1**, before anything else — `deny("missing_capability_id")` ([`decide-017`](../../data/_vectors/clc-v1/vectors.json), grant `std/database-v1:query:SELECT`, request `{}`).

## 4.2 ObservedAction (evidence side)

The effect boundary constructs an ObservedAction from **facts the executor controls** — it MUST NOT copy a requester-supplied action digest without deriving or checking the corresponding fact.

An ObservedAction carries:

| Field | Meaning |
|-------|---------|
| `action_type` | the action-type name declared by the relying-party-pinned type definition — the class this projection belongs to |
| `material_fields` | every field the type definition declares **material** |
| `digest` | computed over the canonical **material projection** |

**The material projection is deterministic and normative:**

1. The action type declares a **material field set** (required and optional-but-included). Only that set enters the digest.
2. Canonical serialization is **JCS** ([RFC 8785]); the single suite defined in v1 is `jcs-sha256`.
3. The projection identity is the language's own: `clc-action:1:<type>:<suite>:<b64url>`.
   A **CAID** [CAID] covers the *complete* Action Object under its own suite registry and identifies the action object, not an occurrence. The two are related by a relying-party-pinned **Action-Mapping Profile** (§6.4) — never by treating the strings as interchangeable.
4. A field the type does **not** declare material MUST be excluded from the digest and MUST NOT affect **Match**: an ObservedAction carrying undeclared fields is **not invalidated**, but those fields carry no action identity.
5. A type-declared material field that is **missing** makes the ObservedAction **non-matchable** — coverage MUST NOT be inferred, defaulted, or repaired (`UNSATISFIED`, §10). This is the evidence-side mirror of key closure (§6.2): absence of a governing field is fail-closed, never fail-open.

> Example (the §4.3 identity table's own row, shown with the digest elided):
> `clc-action:1:payment.release.1:jcs-sha256:...` as an ActionId binding the material projection of one payment-release action, not the occurrence.

## 4.3 Identity — two levels

| Level | Identity | Scope | Example |
|-------|----------|-------|---------|
| **Class** | `CapabilityId` | covers a *class* of actions | `std/database-v1:query:*` |
| **Instance** | `ActionId` (projection digest) | the material *content of one action*, **not** an occurrence | `clc-action:1:payment.release.1:jcs-sha256:…` |

- A CapabilityId covers a class; an ActionId identifies the material content of one action.
- An ActionId **does not identify an occurrence**: it binds the declared material content. Correlating to a particular occurrence additionally requires an **occurrence discriminator** defined and checked by the consuming profile (CAID-02 Section 4.5 carries it as the optional `occurrence_id`; when a profile uses one, it MUST appear among the declared material fields to affect the digest). Allocating unique occurrences and proving one-time consumption/execution stay outside both documents (CAID-02 Section 7).
- **Entailment checks class coverage; Match checks content binding** — the two mechanisms are deliberately different layers.

## Where this fits in decisions

The decision function ([10-decisions.md](10-decisions.md)) consumes an Operation for authorization (`allow`/`deny`/`allow_unresolved`) and, on the evidence side, an ObservedAction for Match (§6.4). The material-projection rules above are what make Match deterministic across consumers — the same facts must produce the same digest.

## Common pitfalls

- **Treating a CAID as the projection identity.** They are different objects over different scopes; only an Action-Mapping Profile relates them.
- **Assuming an ActionId identifies an occurrence.** It does not; occurrence correlation is the consuming profile's job.
- **Feeding an undeclared field into Match.** Undeclared fields carry zero identity — they neither add nor destroy matchability, but a *missing declared* material field does make the action non-matchable.
- **Digest trust.** The effect boundary must construct ObservedAction from executor-controlled facts, never from a requester-supplied digest without checking the underlying fact.

---
← [03-identifiers.md](03-identifiers.md) · → [05-grants.md](05-grants.md) · related: [10-decisions.md](10-decisions.md), [12-containment.md](12-containment.md)