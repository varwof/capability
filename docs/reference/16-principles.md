# 16 · Design Principles

> **Normative source:** [`capability-language-core-principles-v1.md`](../capability-language-core-principles-v1.md) — the design-principles **declaration** (rev 4, 2026-09-14), a companion of the specification; the binding normative anchors are [`capability-language-core-v1.md`](../capability-language-core-v1.md) §1 and §12.
> This page is a readable guide. In case of conflict, the normative specification wins.
> Status: Preview — not for production use.

## TL;DR

CLC-v1 ships a **principles declaration**: twelve principles (**P1–P12**), each carrying a **falsifiable check** — a statement that can be run, not an adjective — plus five **derived decision rules** (**R1–R5**) for settling feature arguments, four **runnable properties**, and a **clause↔evidence ledger** (declaration §7) enforcing the discipline: *a principle that binds no normative clause and no vector is decoration*. The honest current state includes three recorded **gaps**: P7 (no carrier document cites CLC yet), and P8②/P12 (all three implementations share one author — their agreement is a regression test, not independent validation).

## 1. What the declaration is (and is not)

The declaration is a **companion document**, not a second normative spec: it states *why* the core looks the way it does and *how every principle is tested*; the language spec remains the only authority for semantics, verdicts and reason codes. Its revision history is part of its method:

| Rev | Date | Change |
|-----|------|--------|
| 1 | 2026-09-10 | P1–P8 |
| 2 | 2026-09-11 | P9–P12, three clarifications, the clause↔evidence ledger |
| 3 | 2026-09-13 | derived rules R1–R5 (§2.5); the CLC-E open item resolved ("implemented, not claimed") |
| 4 | 2026-09-14 | P11 scoped to **composition**; delegation containment explicitly taken out of it |

## 2. The core, in one table

| Element | Authorization side | Evidence side |
|---------|--------------------|---------------|
| Value | Operation (concrete request) | ObservedAction (asserted effect) |
| Identity | CapabilityId (class) | ActionId (instance) |
| Relation | Entailment (⊆) | Match |
| Bound | Grant params / constraints | Evidence requirements / freshness |
| Verdict | `allow` / `deny` | `SATISFIED` / `UNSATISFIED` |

Plus exactly one composition operator: **Intersection (∩)** — see [`09-intersection.md`](09-intersection.md).

## 3. The twelve principles (P1–P12)

| # | Principle | In one line | Falsifiable check (compressed) |
|---|-----------|-------------|-------------------------------|
| P1 | Minimal core | Five shared abstractions, one composition operator, two side-specific functions; nothing else enters the core | delete a rule and re-run the corpus — if no vector's outcome changes, the rule was not part of the minimal core |
| P2 | No control flow | no branches, loops, recursion, macros or user procedures; conditionality only as *narrower capabilities and tighter constraints* | the §3 grammar admits no construct whose evaluation order depends on a value; every vector is decided in one pass |
| P3 | Immutable values | no assignment, no mutable state; evaluation is a single pure pass over finite inputs | evaluate any vector twice, in either order, in a fresh evaluator — identical result |
| P4 | Domains, not types | `3` as a bound and `3` as an identifier behave differently; each parameter declares a domain (`bound` \| `enum` \| `exact`) | changing a parameter's domain must change ≥1 vector outcome — grant `{"station":[3]}` must not cover `station 2` |
| P5 | Deterministic and terminating — **including the reason** | same inputs → same verdict **and** the same normative reason code (§9.1 fixed ordering, §9.2 stable codes) | implementations are compared on the **canonical reason**, not only the verdict |
| P6 | Fail-closed | undefined / unknown / missing / stale / unverifiable → deny; **an undeclared parameter does not constitute a grant** (`undeclared_param`) | every failure path in the corpus returns a stable deny code; no input yields "allow by omission" |
| P7 | Define once, consume everywhere | carriers (AIC-JWT DA, EMILIA AEB, OAuth RAR, delegation chains…) *reference* the semantics, never redefine matching/subset/deny | a second implementation of subset/deny is either a bug or a different language — and must say which |
| P8 | Carriers and semantics are separate | ① carrier independence (JWT / X.509 / ACPs); ② language independence (independent implementations, same verdict *and* reason) | the two separations are checked on their own; never collapse them into one claim |
| P9 | Local decidability | a decision is computable from the artifact plus **declared** local inputs; no core rule may need a network call, registry lookup or undeclared clock | the core corpus runs with no I/O; a profile depending on external state must declare it and deny when absent |
| P10 | Bounded work | serialized params ≤ **512 bytes**, nesting ≤ **32 levels**; over the limit → deny (`invalid_params_size`); no backtracking or super-linear construct | push the limits: positive cases exactly at each limit, negative cases one step past — the limits are normative text, not an implementation constant |
| P11 | Composition narrows only | the effective grant stays within **every** source, order-independently; source coverage (⊑) compares only the keys a source declares (the effective key set is the union); key closure belongs to the **effective** grant | property test: `merged ⊑ src` for every source, `Intersect(S) = Intersect(reverse(S))`, and an operation with a key no source declared denies |
| P12 | Agreement is the bar | a rule is not done until **≥2 independent implementations** agree on verdict **and** canonical reason; a disagreement is a *spec* defect | bidirectional: every rule maps to ≥1 vector and every vector to a clause; runners exit non-zero on any mismatch |

**P11's scope (rev 4).** P11 governs **composition** (intersection of declared sets) — *not* delegation containment: whether a child grant stays inside its parent's boundary is the separate `Contains` relation of spec §13 (CLC-D, [`12-containment.md`](12-containment.md)). A delegation chain shows an intersection of the declared sets, which is not the same theorem.

**P5 vs P10.** Determinism of the *conclusion* is P5; predictability of the *cost* is P10. Keep them separate.

## 4. Derived decision rules (R1–R5)

R1–R5 are **not additional principles** — each operationalizes the principle(s) named beside it, so a feature argument is settled by pointing at a rule instead of re-arguing from scratch. The falsifiable checks remain the source of truth.

| Rule | Statement | From |
|------|-----------|------|
| R1 | State, time or network ⇒ carrier or profile, **never the core** | P9 + §6 extension rules |
| R2 | A new value **domain** is a new type; a new **operator** is new syntax — and MUST be given a position in the §9.1 ordering | P4 + §6 |
| R3 | Changing the core for one vendor is a **defect**; that belongs to a profile | P7 + P8① |
| R4 | A rule without a clause, or without a vector, is **decoration** | ledger discipline (§7) |
| R5 | A conformance class is claimed only when **≥2 independent implementations** pass the corpus | P12 + P8② |

R5 in practice: "implemented and pinned by a corpus, **not claimed**" is a legitimate and honest state — it is the state of the evidence side (CLC-E) in this revision, and parity between implementations that share an author does not satisfy it (see [`13-conformance.md`](13-conformance.md)).

## 5. The four runnable properties

| Property | Principle | Where it runs |
|----------|-----------|---------------|
| **Local decidability** | P9 | the core corpus runs with no I/O; `offline-vectors.json` (12 OCMP cases, all 11 §3 reason codes) has a coverage + vocabulary gate in CI |
| **Bounded work** | P10 | `params-018/019` (one step past each limit → deny) + `params-020/021` (exactly at each limit → pass) |
| **Composition narrows only** | P11 | `property-cases.json` — 1184 deterministic cases run by all three implementations (identical numbers); CLC-D adds `containment-property-cases.json` (784 forward-closure cases); CLC-1.15 adds `param-bounds-meet-property-cases.json` (500 cases: every successful meet authorizes only what **every** source authorizes) |
| **Agreement is the bar** | P12 | 123 vectors asserted on verdict *and* canonical reason by the Go, Python and TypeScript runners, non-zero exit on mismatch, CI in three repositories — **with the same-author caveat of §6 below** |

## 6. The ledger discipline — and the recorded gaps

Declaration §7 lists every principle with the clause that states it, the artifact that tests it, and a state: `ok`, `gap` (something is missing) or `open` (a decision pending). No item is currently `open`. The three **gaps** are stated in the declaration itself:

- **P7 — gap:** no carrier document cites CLC yet, and `aic-jwt/wit-wpt-interop` ships a second subset implementation whose wildcard surface (`**`, `{a,b}`, `[a-z]`) is v1-forbidden. (The interop study is an experimental neighbour, not CLC — see [`13-conformance.md`](13-conformance.md) §3.)
- **P8 — gap:** all three implementations (Go, Python, TypeScript) share one author; third-party parity is the unproven half.
- **P12 — gap:** the corpus cannot see the same-author limitation — the ≥2-*independent*-implementations bar is recorded as **unmet**.

The checks bite: the P11 property test (2026-09-11) immediately found real defects that "the vectors are green" had hidden — Python widened an empty-`params` merge through a truthiness test, both implementations adopted the *wider* identifier in a merge, and identifier comparison ran through `Entails` instead of params-free copies; a fourth defect (dict intersection could widen the composition) followed on 2026-09-12. All were fixed in all implementations, and the corpus now asserts merged results (`result_params` / `result_constraints`), not just verdicts.

## 7. What CLC deliberately refuses

- `if/then/else`, loops, recursion, macros, user procedures;
- general-purpose policy languages (Rego / Cedar / XACML scale);
- trust establishment, key binding (cnf/DPoP/mTLS), provisioning, revocation transport;
- wire formats, execution lifecycle, evidence/receipt formats.

Extension rules for v2 (declaration §6): adding a **domain** (e.g. `range`, `pattern`) = adding a type, not syntax; adding an **operator** (e.g. `**`, `{a,b}`, `[a-z]`) = adding syntax *and* a position in the §9.1 ordering; anything needing state, time or network belongs to a **carrier** or a **profile** (R1), never to the core.

## Common pitfalls

- **Treating the declaration as a second normative spec** — it is a companion; the language spec wins on every semantic question, and principles bind only through the clauses that state them.
- **Reading P11 as covering delegation containment** — rev 4 explicitly scopes P11 to composition; containment is §13 / CLC-D and has its own relation, corpus and property file.
- **Reading "≥2 independent implementations" as satisfied** — same-author parity does not meet the bar (P12, R5); this is why CLC-E is implemented but not claimed.
- **Treating R1–R5 as new principles** — they are derived operationalizations; the falsifiable checks of P1–P12 remain the source of truth.

---
← [15-glossary.md](15-glossary.md) · *this is the last page* · related: [02-overview.md](02-overview.md), [13-conformance.md](13-conformance.md), [README.md](README.md)
