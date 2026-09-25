# 15 · Glossary

> **Normative source:** [`capability-language-core-v1.md`](../capability-language-core-v1.md) §2, §13.2
> This page is a readable guide. In case of conflict, the normative specification wins.
> Status: Preview — not for production use.

## A

**Action** — The thing being referenced: an abstract operation class (authorization) or a concrete asserted effect (evidence). See [04-actions](04-actions.md).

**ActionId** — Evidence-side identifier: the JCS digest of the declared material projection of an ObservedAction (§4.2/§6.4). Undeclared fields must not affect it; a missing declared material field makes the action non-matchable.

**allow** — Authorization verdict: the operation is fully enforced; no residual obligations. Distinct from `allow_unresolved` (§9/§11).

**allow_unresolved** — Authorization verdict: authorization holds but at least one recognized-but-unevaluated constraint is carried on `unresolved`. Never equal to `allow`; a consumer that cannot evaluate or confirm MUST deny (§8.4).

**Authorize** — Decision function: `Authorize(grants, operation) → Decision` (§9).

**AuthorizeWithChain** — Fused chain check (CLC-D): `Contains` each adjacent hop, then `Intersect(chain...)`, then `Authorize` (§13.11).

## B

**Binding** — The relation connecting an Identity to an Action: Entailment (auth) or Match (evidence). *Not* key binding (cnf/DPoP/mTLS), which belongs to the native artifact's spec (§11).

**Bound** — A declared constraint value as interpreted by the §6.2/§8.1 value semantics (§13.2).

**BoundMeet** — The §6.6 meet that `Intersect` uses to combine `param_bounds` across sources (§6.6). See [07-parameters](07-parameters.md).

## C

**CapabilityId** — Structured name identifying a class of actions within a scheme (per the §3 grammar) (§2/§3).

**CLC-A / CLC-D / CLC-E** — Conformance classes: authorization baseline (claimed), delegation containment (claimed), evidence side (**implemented, not claimed**) (§12). See [13-conformance](13-conformance.md).

**CLC-<major>.<minor>** — The language revision an implementation declares and each input is authored against; an input without a declaration is treated as CLC-1.0 (§12.1).

**Constraint** — Bound on how an action may be used (auth) or what evidence is required (evidence); identity is the `(scheme,type)` pair (§8.1). Outside the `Contains` relation (§13.4.4).

**ConstraintUnion** — Derived projection: the normalized, deterministically-ordered union of a chain's constraint strings (§7.1). See [09-intersection](09-intersection.md).

**Contains(parent, child)** — The containment relation (CLC-D): is the child's declared grant inside the parent's declared grant? (§13.4).

## D

**Decision** — Authorization-side result: `{verdict: "allow"|"deny"|"allow_unresolved", reason, unresolved}` (§9).

**Declared set** — The parameters a grant carries as constraints on operations (§6.2 value semantics), plus its declared key set (union of `params` and `param_bounds` keys) (§13.2/§13.4.3).

**delegation_mode_not_narrower** — CLC-D reason code produced by the **binding-profile pre-check** (§13.4.5), never by `Contains` (§13.5). See [12-containment](12-containment.md).

**deny** — Authorization verdict: the operation is not authorized, with a stable reason code (§9).

## E

**Empty bound** — `[]`/`{}` **at a value** — explicitly empty, denies the class. Contrast `params:{}` (no constraint) (§7 rule 6, §13.2).

**Entailment** — Authorization-side binding: grant covers operation (⊆) (§6.1).

**Evidence side** — The Match (§6.4) / Satisfy (§10) machinery plus evidence-side constraints (§8.2); pinned but **not claimed** as CLC-E (§12).

## G

**Grant** — A principal's authorization of a CapabilityId with optional params, `param_bounds`, and constraints (§5).

## I

**Intersection** — Combining multiple grant sources into an effective set (∩); P_effective = P_principal ∩ C_agent ∩ P_gateway (§7).

## M

**Match** — Evidence-side binding: evidence is bound to the exact action (MATCH / NOT_EQUIVALENT / INDETERMINATE) (§6.4).

**Mode lattice** — Carrier-defined order over delegation modes, exercised by the binding profile (§13.4.5); AIC-JWT: `authorized < representative`.

## N

**Narrower** — A child grant whose every declared value is within the parent's bounds and whose key set is closed by the parent's (§13.2).

**Native verification** — Signature/schema/freshness checking that belongs to the native artifact's spec, outside CLC (§11).

## O

**Operation** — Concrete action request: a CapabilityId plus parameters (§4.1).

**ObservedAction** — Evidence-side record of a concrete action taken (§4.2).

## P

**params** — Declared parameter constraints on a grant (§6.2). `params:{}` ≡ absent = unconstrained.

**param_bounds** — Extended parameter-bound field (CLC-1.10+) (§6.5); a key sits in `params` **or** `param_bounds`, never both.

**Profile (binding)** — A carrier's mapping of its native authorization structure to CLC grants (§13.8.1).

## R

**Reason code** — A stable identifier; canonical code = everything before the first `:`; `: <detail>` is a diagnostic suffix only (§9.2).

**Resolve** — Post-decision function consuming a Decision to discharge residual obligations (§8.5).

**Residual obligation** — A recognized-but-unevaluated constraint carried on `unresolved` (§8.4).

## S

**Satisfaction** — Evidence-side verdict: `SATISFIED` or `UNSATISFIED` (binary; `unknown` is internal) (§10).

## U

**unsupported_language_revision** — Fail-closed reason when an input's declared revision is incompatible (§12.1).

**unresolved** — The additive list of recognized-but-unevaluated constraints on a Decision; authorizes only through `allow_unresolved`, never on its own (§8.4/§11).

## V

**Verdict** — Outcome of evaluation: `allow`/`deny`/`allow_unresolved` (auth, lowercase) or `SATISFIED`/`UNSATISFIED` (evidence, uppercase) (§2/§9/§10).

## W

**Wildcard** — Trailing `*` action segment in an identifier; matches one or more trailing segments, never zero. Bare `*`, partial segments, `**`, `{a,b}`, `[a-z]` are `unsupported_wildcard` in v1 (§3).

---
← [14-cookbook.md](14-cookbook.md) · → [16-principles.md](16-principles.md) · related: [02-overview.md](02-overview.md), [README.md](README.md)