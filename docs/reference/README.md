# CLC-v1 Language Reference

> **Normative source:** [`capability-language-core-v1.md`](../capability-language-core-v1.md) — the CLC-v1 specification in full.
> This set of pages is a readable guide. In case of conflict, the normative specification wins.
> Status: Preview — not for production use.

Welcome to the readable language reference for the **Capability Language Core v1 (CLC-v1)** — a minimal, deterministic language for describing what an agent is authorized to do.

This reference is organized the way a programming-language manual is: a quickstart, concept pages, field tables, ✅/❌ example pairs drawn from the conformance corpus, and a reason-code cheat sheet. It is **derived** from the specification: every page anchors its claims to a spec section, and every JSON example is either a real corpus vector or a value constructed from a stated grammar rule.

## The 17 pages at a glance

| # | Page | What it covers | Spec anchor |
|---|------|----------------|-------------|
| — | [`README.md`](README.md) | This index: reading paths, authority statement, coverage map, spec baseline | whole document |
| 01 | [`01-quickstart.md`](01-quickstart.md) | Build your first grant → request → verdict in four steps, no runtime required | §5/§6/§9 |
| 02 | [`02-overview.md`](02-overview.md) | The five core models, three-valued verdict, carrier-neutral boundary, design principles | Abstract/§1/§11 |
| 03 | [`03-identifiers.md`](03-identifiers.md) | `capability-id` grammar, wildcards, scheme disambiguation | §3 |
| 04 | [`04-actions.md`](04-actions.md) | Operation, ObservedAction, Identity and ActionId projection | §4 |
| 05 | [`05-grants.md`](05-grants.md) | The Grant object, field by field | §5 |
| 06 | [`06-entailment.md`](06-entailment.md) | Authorization binding: entailment, the §6.3 algorithm, and evidence Match | §6.1/6.3/6.4 |
| 07 | [`07-parameters.md`](07-parameters.md) | Params, extended `param_bounds`, and `BoundMeet` | §6.2/6.5/6.6 |
| 08 | [`08-constraints.md`](08-constraints.md) | Constraint identities, value grammars, residual obligations, `Resolve` | §8 |
| 09 | [`09-intersection.md`](09-intersection.md) | Intersection ∩ of grants, and the `ConstraintUnion` projection | §7 (7.1) |
| 10 | [`10-decisions.md`](10-decisions.md) | Decision and satisfaction functions, verdicts, reason ordering | §9/§10 |
| 11 | [`11-reason-codes.md`](11-reason-codes.md) | One-page cheat sheet of **all** reason codes | §9.1/9.2/13.5/C.2 |
| 12 | [`12-containment.md`](12-containment.md) | Delegation containment, CLC-D, AIC-JWT binding, `AuthorizeWithChain` | §13 |
| 13 | [`13-conformance.md`](13-conformance.md) | Conformance classes, corpora, language revision rule | §12/12.1/Appendix B |
| 14 | [`14-cookbook.md`](14-cookbook.md) | Scenario-driven ✅/❌ recipes distilled from the corpus | all vectors |
| 15 | [`15-glossary.md`](15-glossary.md) | Alphabetical term glossary | §2/§13.2 |
| 16 | [`16-principles.md`](16-principles.md) | Design principles P1–P12 with falsifiable checks, derived rules R1–R5, runnable properties, the clause↔evidence ledger | principles declaration; §1/§12 |

## Three reading paths

- **Writing an authorization policy** (you configure grants): `01-quickstart` → `05-grants` → `07-parameters` → `08-constraints` → `14-cookbook`.
- **Implementing a validator** (you build or audit an evaluator): `02-overview` → `03-identifiers` → `06-entailment` → `09-intersection` → `10-decisions` → `11-reason-codes` → `13-conformance` → `16-principles`.
- **Building delegation chains** (you want `Contains`/`AuthorizeWithChain`): `02-overview` → `12-containment` → `13-conformance`.

## Authority statement

- The **specification** [`capability-language-core-v1.md`](../capability-language-core-v1.md) is the *only* authoritative source for CLC-v1 semantics, verdicts, reason codes and conformance obligations. These reference pages are an editorial re-presentation and must not be treated as independent of it.
- Every page carries a "Normative source" banner naming the exact section(s) it summarizes. Where this guide and the spec disagree, the **spec wins**.
- The status of the language is **Preview / Working Draft**; none of these pages should be relied on for production decisions.
- JSON examples are traced to corpus vectors where possible (see the id links) or are marked **constructed from §X grammar** — never invented by hand beyond a stated rule.

## Conformance status (short version)

Refer to `13-conformance` for the full, carefully-worded statement and to `Spec` §12. In one line: the corpus and all three same-author implementations (Go/Python/TypeScript) exercise **CLC-A** (the claimed baseline authorization class) and ship **CLC-D** (containment); **CLC-E** (evidence side) is implemented and pinned by a corpus but is **not claimed** — the §12 bar of two *independent* implementations is **unmet**, and parity among implementations that share an author is a regression test, not independent validation.

## Coverage map (spec section → reference page)

| Spec part | Reference page | Notes |
|-----------|----------------|-------|
| Abstract | `02-overview`, `13-conformance` | the honest conformance scope is repeated verbatim in spirit there |
| Revision History | `13-conformance` (§12.1 rule) | the per-revision table lives in the spec only |
| §1 Design Principle | `02-overview` | why the core exists; P1–P12 |
| Principles declaration (companion document) | `16-principles` | P1–P12 with falsifiable checks, R1–R5, the runnable properties and the ledger; the declaration is not part of the spec |
| §2 Terminology | `15-glossary` | every defined term, alphabetized |
| §3 Grammar | `03-identifiers` | capability-id, wildcard, scheme disambiguation |
| §4 Action | `04-actions` | 4.1 Operation / 4.2 ObservedAction / 4.3 Identity |
| §5 Grant | `05-grants` | field-by-field dissection |
| §6 Binding | `06-entailment`, `07-parameters` | 6.1 entailment → 06; 6.2 parameters → 07; 6.3 algorithm → 06; 6.4 match → 06; 6.5 `param_bounds` → 07; 6.6 `BoundMeet` → 07 |
| §7 Intersection | `09-intersection` | 7.1 `ConstraintUnion` → 09 |
| §8 Constraint | `08-constraints` | 8.1 auth-side / 8.2 evidence-side / 8.3 unified grammar / 8.4 residual channel / 8.5 `Resolve` |
| §9 Decision Function | `10-decisions`, `11-reason-codes` | 9.1 ordering → 10; 9.2 reason codes → 11 |
| §10 Satisfaction Function | `10-decisions` | evidence-side three-valued report |
| §11 Semantic Boundary | `02-overview` | what CLC deliberately does **not** define |
| §12 Conformance | `13-conformance` | 12.1 Language Revision → 13 |
| §13 Delegation Containment | `12-containment` | 13.1–13.8, 13.11, 13.12 → 12; §13.9 Related Work and §13.10 Open Issues are **excluded** (linked as further reading at the end of 12-containment) |
| Appendix A Consumption Mapping | `10-decisions` | how consumers map verdicts |
| Appendix B Reference Vectors | `13-conformance`, `14-cookbook` | corpus layout and how the cookbook derives from it |
| Appendix C Carrier Vocabulary & Reason-Code Mapping | `12-containment`, `11-reason-codes` | C.1 vocabulary → 12; C.2 failure-code mapping → 11 |
| Security / IANA / Privacy Considerations | **excluded** | one-paragraph pointer in `02-overview` links to the spec sections |
| Acknowledgements / References | **excluded** | normative references are named where each page needs them |

**Deliberately excluded items** (fixed set, per the task red lines): Acknowledgements, References, the full text of the Security/IANA/Privacy Considerations, and §13.9 Related Work / §13.10 Open Issues. Their existence is pointed to from `02-overview` and `12-containment`.

## Spec baseline

`Spec baseline: 46b10d1c64433ec74592dff44cdb4c68ae91073f` (`git rev-parse HEAD` of the capability repository at the time this reference was written; the normative text this set of pages was written against is the working-tree revision dated 2026-09-25).

---
← *This is the index.* · → continue with [`01-quickstart.md`](01-quickstart.md) · related: [`02-overview.md`](02-overview.md), [`13-conformance.md`](13-conformance.md)