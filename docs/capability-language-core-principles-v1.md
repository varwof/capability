<!-- Published copy in varwof/capability. Working draft and rationale live in the
     design repository; treat this copy as canonical once committed. -->

# Capability Language Core (CLC-v1) — Design Principles

> ⚠️ **Preview** — Not for production use. APIs and features may change before official release.

Status: declaration, **rev 4** — 2026-09-14 (scopes P11 to composition and takes
delegation containment out of it: a chain shows an intersection of the declared
sets, not containment of a child inside its parent).  rev 3 = 2026-09-13 (adds
the derived decision rules R1–R5 in §2.5, and resolves the CLC-E entry in §9).
rev 2 = 2026-09-11 (P9–P12, three clarifications, the clause↔evidence ledger).
rev 1 = 2026-09-10, P1–P8.
Companion (normative): `capability-language-core-v1.md`

## 0. What this is

CLC-v1 is a **minimal decision language** for authorization and evidence: a
finite set of values, three relations, and two decision functions.  It is not a
policy engine, not a protocol, and not a workflow language.

## 1. The core, in one table

| Element | Authorization side | Evidence side |
|---------|--------------------|---------------|
| Value | Operation (concrete request) | ObservedAction (asserted effect) |
| Identity | CapabilityId (class) | ActionId (instance) |
| Relation | Entailment (⊆) | Match |
| Bound | Grant params / constraints | Evidence requirements / freshness |
| Verdict | `allow` / `deny` | `SATISFIED` / `UNSATISFIED` |

Plus exactly one composition operator: **Intersection** (∩).

## 2. Principles (P1–P12)

Every principle carries a **falsifiable check**: a statement that can be run,
not an adjective.

**P1 — Minimal core.** Five shared abstractions, one composition operator, two
side-specific functions.  Nothing else enters the core.
*Falsifiable check:* delete a rule and re-run the corpus — if no vector's
outcome changes, that rule was not part of the minimal core.

**P2 — No control flow.** No branches, loops, recursion, macros, or
user-defined procedures.  Conditionality is expressed only as *narrower
capabilities and tighter constraints*.
*Falsifiable check:* the §3 grammar admits no construct whose evaluation order
depends on a value; every vector is decided by one pass over its inputs.

**P3 — Immutable values.** No assignment, no mutable state.  Evaluation is a
single pure pass over finite inputs.
*Falsifiable check:* evaluate any vector twice, in either order, in a fresh
evaluator — identical result.

**P4 — Domains, not types.** The JSON type is not enough: `3` as a bound and
`3` as an identifier behave differently.  Each parameter declares a **domain**
(`bound` | `enum` | `exact`) and semantics dispatch on the domain.
*Falsifiable check:* changing a parameter's domain must change at least one
vector's outcome — `grant {"station":[3]}` must not cover `station 2`.

**P5 — Deterministic and terminating — including the reason.** Same inputs →
same verdict **and the same normative reason code** (fixed ordering §9.1,
stable codes §9.2).
*Falsifiable check:* both implementations are compared on the **canonical
reason**, not only the verdict.  Determinism of the *conclusion* is this
principle; predictability of the *cost* is P10.  Keep them separate.

**P6 — Fail-closed.** Undefined, unknown, missing, stale, or unverifiable →
deny.  Nothing is permitted by absence, and **an undeclared parameter does not
constitute a grant**: a request key that the bounded grant does not declare
denies (`undeclared_param`), it does not pass unconstrained.
*Falsifiable check:* every failure path in the corpus returns a stable deny
code; no input yields "allow by omission".

**P7 — Define once, consume everywhere.** Carriers (AIC-JWT DA, EMILIA AEB,
OAuth RAR, delegation chains, …) *reference* this semantics; they never
redefine matching, subset, or deny rules.
*Falsifiable check:* a carrier may add a format or a trust story, but must not
add a second implementation of subset/deny.  Any second implementation is
either a bug or a different language — and must say which.

**P8 — Carriers and semantics are separate.** Two independent separations, each
checked on its own: ① **carrier independence** — the same semantics hold
whatever carries the artifact (JWT / X.509 / ACPs); ② **language independence**
— independent implementations in different languages reach the same verdict
*and* the same reason.  Do not collapse the two into one claim.

**P9 — Local decidability.** A decision MUST be computable from the
authorization artifact plus **declared** local inputs.  No core rule may require
a network call, a registry lookup, or an undeclared clock.
*Falsifiable check:* if a rule needs an online input, it belongs to a carrier or
a profile, not to the core.  The core corpus runs with no I/O.  A profile that
does depend on externally refreshed state (OCMP: status snapshots, local facts,
time source) must declare those inputs and deny when they are absent.

**P10 — Bounded work.** The cost of one decision is bounded by the size of its
inputs, with hard limits: **serialized params ≤ 512 bytes**, **nesting depth
≤ 32** (counting the outermost object as one level); over the limit → deny
(`invalid_params_size`).  No backtracking match, no unbounded expansion, no
construct with super-linear cost.
*Falsifiable check:* push the limits — a positive case at exactly 512 bytes and
at exactly the depth limit, and a negative case one step past each.  The limits
are normative text, not an implementation constant.

**P11 — Composition narrows only.** Intersection MUST only remove authority:
the effective grant MUST stay within **every** source, order-independently,
with no exception rule.  Two different relations are involved and must not be
confused:

* **Source coverage (⊑)** — grant against grant, per §7 rule 2: for every
  parameter key the source declares, the merged bound is inside the source's
  bound, and no declared constraint is dropped.  Keys a source does not declare are not
  compared: composition authorizes a parameter when *some* source declares it,
  so the effective key set is the union.
P11 governs **composition**.  It does not govern **delegation containment**:
whether a child grant stays inside its parent's authorization boundary is a
separate relation this document does not define, so no conformance claim rests
on it (language core §12).  A delegation chain shows an intersection of the
declared sets, which is not the same theorem.

* **`Entails`** — grant against *operation*, the authorization relation, which
  applies key closure.  Closure belongs to the **effective** grant only: it is
  the single grant a verifier evaluates, and it is what stops an operation from
  carrying a parameter key that no source declared.

*Falsifiable check:* property test over the shared case file —
`merged ⊑ src` for every source, `Intersect(S) = Intersect(reverse(S))`, and for
a bounded merged grant an operation with an undeclared key denies
(`undeclared_param`).

**P12 — Agreement is the bar.** A normative rule is not done until ≥2
independent implementations agree on the vectors covering it, on verdict **and**
canonical reason; a disagreement is a spec defect, not an implementation
defect.  The bar is bidirectional: a rule with no vector is incomplete, and a
vector with no normative clause is incomplete.
*Falsifiable check:* every rule maps to ≥1 vector and every vector maps to a
clause; both runners exit non-zero on any mismatch.

### 2.5 Derived decision rules (R1–R5)

R1–R5 are **not additional principles**: each one operationalizes the principle(s)
named beside it, so an argument about a proposed feature can be settled by
pointing at a rule instead of re-arguing the principle from scratch.  They are
derived — the falsifiable checks above remain the source of truth.

**R1 — State, time or network ⇒ carrier or profile, never the core.**
*From:* P9 (local decidability) + §6 extension rules.
*In practice:* freshness, status, revocation, wall-clock and epoch inputs live in
a profile that declares them and denies when they are absent; the core corpus
runs with no I/O.

**R2 — A new value domain is a new type; a new operator is new syntax.**
*From:* P4 (domains, not types) + §6.
*In practice:* adding constraint types (`freshness`, `consumption`, `quorum`,
`exclusion`) extends a value grammar and may enter the core; adding a wildcard
shape rewrites §3 and MUST be given a position in the §9.1 ordering.

**R3 — Changing the core for one vendor is a defect; that belongs to a profile.**
*From:* P7 (define once) + P8① (carrier independence).
*In practice:* a carrier's field names appear in its own profile document, never
in the language text; the language may *cite* a consumer (Appendix A), not absorb
it.

**R4 — A rule without a clause, or without a vector, is decoration.**
*From:* §7 ledger discipline.
*In practice:* every addition lands with its normative sentence and its corpus
entries in the same change; "vectors will follow" is not a completed rule.

**R5 — A conformance class is claimed only when ≥2 independent implementations
pass the corpus.**
*From:* P12 (agreement is the bar) + P8② (language independence).
*In practice:* "implemented and pinned by a corpus, not claimed" is a legitimate
and honest state — it is the state of the evidence side in this revision — and
parity between implementations that share an author does not satisfy this rule.

## 3. What CLC-v1 deliberately refuses

- `if/then/else`, loops, recursion, macros, user procedures;
- general-purpose policy languages (Rego / Cedar / XACML scale);
- trust establishment, key binding (cnf/DPoP/mTLS), provisioning, revocation transport;
- wire formats, execution lifecycle, evidence/receipt formats.

## 4. Why minimality matters (engineering consequences)

1. **Two independent implementations can be checked against one vector file.**
   Current state: 105 vectors (`syntax` (9) / `entail` (37) / `intersect` (14)
   / `decide` (38)),
   Go, Python and TypeScript, asserted on verdict *and* normative reason code,
   non-zero exit on mismatch, run in CI in both repositories.
2. **Reason assignment is normative**, not implementation-specific: a fixed
   ordering resolves multi-failure cases to a single code.
3. **Small surface** → reviewable security analysis, publishable test vectors,
   and a defensible "no new protocol" position.

## 5. How to consume it

| Consumer | Uses | Must not redefine |
|----------|------|-------------------|
| AIC-JWT DA | Grant / Operation / Entailment / Decision | matching, subset, deny rules |
| EMILIA AEB | Match + evidence-side verdict mapping | authorization semantics |
| OAuth RAR `authorization_details` | capability-shaped details | subset / deny rules |
| Delegation chain | Intersection of the declared sets across hops | per-hop semantics; containment is not defined here (language core §12) |

## 6. Extension rules (for v2)

- Adding a **domain** (e.g. `range`, `pattern`) = adding a type, not syntax.
- Adding an **operator** (e.g. `**`, `{a,b}`, `[a-z]`) = adding syntax, and it
  MUST be given a position in the §9.1 ordering.
- Anything that needs state, time, or network belongs to a **carrier** or a
  **profile** (e.g. the Offline Capability Manifest Profile), never to the core.

## 7. Clause ↔ evidence ledger (the discipline)

**A principle that binds no normative clause and no vector is decoration.**
Every principle below is listed with the clause that states it, the artifact
that tests it, and its state.  States are `ok`, `gap` (something is missing) or
`open` (a decision is pending).

| Principle | Normative clause | Executable evidence | State |
|---|---|---|---|
| P1 Minimal core | this document §2 | 105 vectors; the previously orphan rule has a clause and a vector | ok |
| P2 No control flow | §3 grammar, §6.3 | no such construct exists | ok |
| P3 Immutable values | §6.3, §9 | both runners, 1184 property cases | ok |
| P4 Domains | §6.2 | `params-001..027` | ok |
| P5 Determinism incl. reason | §9.1 (pre-check + 11 layers), §9.2 (21 codes), §12.1 | 105 vectors assert the canonical reason (incl. §9.1 multi-grant aggregation, rev CLC-1.3) | ok — the 6 undocumented codes and the revision rule were added; the layer table now matches the numbering the corpus cites |
| P6 Fail-closed | §6.2.1, §6.3 step 4, §9.1 layers 5–7 | `params-*`, `undeclared-001/002`, closure probes in the property test | ok — closure applies to the effective grant (§7 rule 2), so an undeclared parameter is still denied |
| P7 Define once | §11, Appendix A | `ruleexec` consumes `semantics.Entails` | **gap** — no carrier document cites CLC yet, and `aic-jwt/wit-wpt-interop` ships a second subset implementation whose wildcard surface (`**`, `{a,b}`, `[a-z]`) is v1-forbidden |
| P8 Separation | Appendix A | Go, Python and TypeScript agree on 105 vectors **and** 1184 property cases | **gap** — all three implementations share one author; third-party parity is the unproven half |
| P9 Local decidability | §6.3; OCMP §3 | `offline-vectors.json` (12 cases, 11/11 codes) with a coverage+vocabulary gate in CI | ok — the profile has no evaluator by design, so the gate checks coverage and vocabulary, not evaluation |
| P10 Bounded work | §6.2.1 (512 bytes, depth 32, counting rule) | `params-018/019` (negative) + `params-020/021` (positive) | ok |
| P11 Narrows only (composition; delegation containment is out of scope, rev 4) | §7 rules 2, 5, 6 (⊑ defined) | property test over 1184 cases in all three implementations (they report identical numbers); `intersect-007/008/009/010`; dict intersection requires identical key sets, else `no_overlap` (P11 catch, rev CLC-1.2) | ok — the closure/union conflict is resolved in §8; the 2026-09-12 key-set catch is fixed in all three |
| P12 Agreement is the bar | §12, §12.1, vectors README | 105 vectors with `result_*` assertions + property cases, CI in three repositories | **gap** — the corpus cannot see the same-author limitation |

## 8. What the property test found (2026-09-11)

The P11 property test (`property-cases.json`, 1184 deterministic cases, run by
all three implementations) replaced "the vectors are green" with an invariant, and
immediately produced three findings.  Two were real defects and are fixed; one
is a language decision that is still open.  A fourth finding (2026-09-12) — dict
intersection could *widen* the composition — fixed the same day in all three.

**Fixed 1 — Python widened on an empty `params` object.**  The merge tested
`params` for *truthiness*, so a source with a present-but-empty `params` object
was treated as falsy and **overwrote** the accumulated bound:

```
A = {id: ...:query:SELECT, params:{limit:50}},  B = {id: ...:query:SELECT, params:{}}
Intersect(A,B):  {"params":{}}          <- Go: {"params":{"limit":50}}   [divergence]
Intersect(B,A):  {"params":{"limit":50}}
```

Go was already order-independent; Python was not.  The corpus could not see it
because **neither runner read `result_params`**, so 4 vectors that appeared to
assert the merged result asserted nothing.  Both runners now compare
`result_params` and `result_constraints`, and the merge conditions in Python
mirror Go (`is not None`, not truthiness).

**Fixed 2 — intersection adopted the *wider* identifier.**  When two sources
carried different identifiers, both implementations adopted the broader one
(`query:SELECT ∩ query:* → query:*`), so the merged grant covered operations
that one source did not.  Both now keep the narrower identifier
(`→ query:SELECT`), which is also what makes the result order-independent.

**Fixed 3 — identifier comparison was not params-free.**  A third defect fell out
of the same probe: `Intersect` compared identifiers by calling `Entails(grant,
{id})` — an operation **without** params — so two grants carrying a
present-but-empty `params` object (`query:SELECT` vs `query:*`) failed closed at
§6.3 step 4 and the merge reported `no_overlap` instead of returning the narrower
identifier.  Identifier coverage is now computed on params-free copies, in both
implementations (`intersect-010` pins it).

**Resolved — key closure vs union merge (decision, 2026-09-11).**  The remaining
class was not an implementation defect but a **mis-stated property**: the check
re-applied each source's closure separately, which the verifier never does.
Deciding criterion: *the merged result must be unambiguous to execute under the
verifier's rules.*  Every verifier entry point evaluates exactly one grant —
`Authorize(effectiveGrant, op)` in the gateway,
`Entails(signerGrant, ruleCapability)` in the rule loader — so the merged grant
is the sole authority, and closure is a property of that grant, not of the
sources:

* source coverage (⊑) compares only the keys a source declares → the merge is
  narrowing on every source's own terms;
* the effective key set is the **union** of the declared keys → a parameter is
  authorized when *some* source declares it;
* an operation carrying a parameter key that **no** source declared is still
  denied (`undeclared_param`), because closure runs against the effective grant.

The former "176 open cases" now pass on both sides; the count is not
suppressed, the property itself was corrected and §7 rule 2 now states ⊑ as
normative text.

## 9. Open items

1. ~~Decide closure vs union~~ — **decided 2026-09-11** (§8): the effective grant
   is the sole authority, closure belongs to it, and ⊑ compares only the keys a
   source declares.  No item in the ledger is left in the `open` state.
2. Third-party parity run — the half of P7/P8 that only someone else can prove.
3. Carriers: cite CLC where they consume it, and either retire the second subset
   implementation in `aic-jwt/wit-wpt-interop` or declare it a different
   language.
4. **CLC-E (evidence side)** — **resolved 2026-09-13, the other way**: the
   evidence side now has a value grammar (§8.2, §10), a reference implementation
   and a corpus (`evidence-vectors.json`, 32 vectors: constraints, requirement
   binding, ActionId, Match), and §12 states explicitly that **this revision
   makes no CLC-E conformance claim**.  The claim is withheld **on principle**,
   not for lack of material: P12 sets the bar at ≥2 *independent*
   implementations and P8② counts parity only between independent ones, so
   "implemented, not claimed" is the honest state until a second implementation
   of the evidence side exists — and the evidence-side semantics are EMILIA's to
   gate (division of work), which is the second precondition.  Carrier-neutral
   genericity is now exercised rather than asserted: `crosswalk-vectors.json`
   carries 13 vectors in both directions (8 mapping foreign capability
   representations into CLC, 5 projecting a CLC decision into an AEB crossing).
5. Commit and publish: the specification, the vectors and both implementations
   are still uncommitted, so none of this is reachable from the repositories yet.
   As of 2026-09-13 that list also includes the evidence-side value grammar and
   corpus (§8.2/§10, `evidence-vectors.json`), the two cross-walk directions and
   the execution-side evidence face (decision/admission/outcome records with
   profile and recorder subjects).  A language revision that nobody can fetch is
   not yet a language revision.
6. Execution layer (`ruleexec`) follow-ups recorded in
   `database-scheme-design.md`: rule schema promotion, flow state machine,
   budget-exceeded rollback semantics, more shared vectors.

---

## 中文要点（设计原则声明）

- **定位**：CLC-v1 是一门**极小的判定语言**——有限的值 + 三条关系（蕴含/匹配/交集）+ 两个判定函数，
  不是策略引擎、不是协议、不是工作流语言。
- **三条纪律**：① **没有控制流**（条件性只能靠"更窄的能力 + 更紧的约束"表达）；② **值不可变**（无赋值、无状态，单次纯求值）；
  ③ **类型系统 = 值域**（bound / enum / exact，语义按值域分派）。
- **六条不可让**：不做通用策略语言；不做信任与密钥绑定；不做发放/吊销传输；不做执行生命周期；不做线格式；**不靠"缺省即允许"**。
- **R1–R5（§2.5，派生判定规则，不是新原则）**：R1 状态/时间/网络 → 归 carrier 或 profile，绝不进核心；R2 新值域 = 加类型、新算子 = 加语法（且必须进 §9.1 顺序）；R3 为某一家改核心 = 缺陷，那属于 profile；R4 没有条文或没有向量的规则是装饰；**R5 一致性类只在 ≥2 个独立实现通过语料后才声称**（因此证据侧现在是「已实现、有语料、不声称」）。
- **P1–P12**：P1 最小核、P2 无控制流、P3 值不可变、P4 值域而非类型、P5 确定性（含 reason）、P6 缺省即拒绝、
  P7 定义一次处处消费、P8 载体与语义分离（分①载体无关②实现语言无关两层检验）、
  P9 **本地可判**、P10 **有界工作量**（参数 ≤512 字节、嵌套 ≤32 层，超限即拒）、
  P11 **组合只收窄**、P12 **一致即门槛**。
- **纪律**：每条原则必须绑定 ≥1 条规范条文 + ≥1 条向量/测试（本文 §7 台账），没有条文或没有向量的原则只是装饰。
- **本轮结果**：规范补齐了输入归一化上限、11 层顺序表、6 个缺失规范码、§12.1 语言版本与附录计数、
  §3 scheme 文法、§8.1 值文法与 §8.4 `unresolved` 残余通道；
  向量 68 → **95**，属性用例 524 → **1184**，另 **12** 条 OCMP 离线用例；
  属性测试与语料抓出并修好**多处**真实缺陷（① Python 在空 `params` 上放宽并覆盖已收的边界；
  ② 两实现在交集里取了更宽的 id；③ id 比较走了 `Entails`，被 §6.3 step 4 打成"无交集"；
  ④ Python 把 bool 当数字（`True==1`）放行；⑤ 对象值交集键集不一致时意外**加宽**（P11，prop-0956）；
  ⑥ Go 已知约束集越过 `parts[1]` 文法漂移；⑦ `max_rows` op 缺席时静默跳过）。
- **P11 的裁决（2026-09-11）**：合并后的**有效 grant 是唯一权威**——验证侧的入口只有
  `Authorize(有效grant, op)`（网关）与 `Entails(签名者的grant, 规则声明)`（规则加载），**没有任何地方逐源再判一次**。
  因此：**源覆盖 ⊑ 只比较"该源自己声明的键"**（组合时"某个源声明过"即视为授权），
  而**键闭包（`undeclared_param`）只对有效 grant 生效**——任何源都没声明过的参数键依然被拒。
  这条既保证了最小权限（每个源自己的边界不被放宽），也保证了验证侧结果无歧义；
  原先"176 例待裁决"不是实现缺陷，而是我那条属性**问错了关系**。
