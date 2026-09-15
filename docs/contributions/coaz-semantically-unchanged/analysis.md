# COAZ "semantically unchanged": which values, compared how (17 axes)

Date: 2026-09-15. Audience: the OIDF AuthZEN / COAZ discussion. **This is a discussion
contribution, not part of COAZ and not part of CLC.** Vector ids and the issue draft are English;
the private working copy of this analysis is Chinese.

Sources: the OAUTH-WG / WIMSE thread "Binding OAuth-authorized calls to specific tool-call
arguments in agentic/MCP flows" (2026-09-01 to 2026-09-15, public list archive), plus the CLC
specification and its three implementations in this repository and its siblings.

Conventions used throughout: **D1** the comparison basis is the projected authorization request
object, not raw bytes; **D2** an axis is `DETERMINED` only if a unique answer follows from the
sources; **D3** readings borrowed from CLC are marked `[PROPOSED]` and are never presented as COAZ
requirements; **D4** where the text is silent the default is fail-closed, marked as an assumption;
**D5** differential testing is limited to axes that reach grant/request parameters; **D6** axis 17
is listed separately; **D7** language split as above.

## 0. The question in one sentence

COAZ requires a PEP to verify, before applying a permit, that "the method, selected mapping and
input values are **semantically unchanged** from what was evaluated", and to "re-evaluate or
refuse, never apply the old permit" if they changed. **That is a requirement, not a decision
procedure.**

Quoted source (thread, 2026-09-15, Alex Olivier):

> "The PEP now has to apply every rewrite it knows about before evaluating, and before applying a
> permit it has to check that the method, selected mapping and input values are **semantically
> unchanged** from what was evaluated. If they changed, re-evaluate or refuse, never apply the old
> permit. So 'the PEP authorised an upstream message rather than the effect' is now a conformance
> failure when it happens within one PEP's own hop. **Lifting that invariant into the framework so
> every future binding gets it is still to do.**"

## 1. Summary

| # | Axis | Classification | One line |
|---|---|---|---|
| 1 | Boundary of "rewrites it knows about" | UNDETERMINED | the set is undefined, and behaviour on an unrecognised rewrite is unstated |
| 2 | What "method" is compared against | UNDETERMINED | the name alone, or the name plus the mapping revision that produced it? |
| 3 | Selected mapping: identity or revision | UNDETERMINED | nothing says what happens when the registry changes between evaluation and forwarding |
| 4 | Comparison basis | UNDETERMINED | raw bytes, canonical form, digest, or the projected request object? |
| 5 | Member order | **DETERMINED** | JSON member order is not semantic (RFC 8259 section 4) |
| 6 | Duplicate members | DIVERGENT | first wins, last wins and refuse are all defensible |
| 7 | String normalization | DIVERGENT | NFC/NFD, escapes vs literals, case, lone surrogates |
| 8 | Number normalization | UNDETERMINED | are `1`, `1.0`, `1e0` the same value? what about non-finite input? |
| 9 | Absent vs null vs empty | DIVERGENT | the three states are different inputs; conflating them inverts the answer |
| 10 | Type coercion | DIVERGENT | `1` vs `"1"`, `true` vs `1`: strict or coercing |
| 11 | Array order and duplicates | DIVERGENT | list semantics or set semantics |
| 12 | Where an over-limit input is refused | UNDETERMINED | which layer refuses, and with which reason code |
| 13 | Added members | DIVERGENT | does an ignored added member still count as a change? |
| 14 | Failure semantics | UNDETERMINED | the text allows re-evaluate **or** refuse; selection rule and reason code are open |
| 15 | Atomicity of check and use | UNDETERMINED | where the boundary is, and what concurrent modification does |
| 16 | "Never apply the old permit" | UNDETERMINED | a permit has no identity, so "old" is undefined for the PEP |
| 17 | Unrecognised assertions or rewrite types | UNDETERMINED | refuse, or continue with the understood part? |

Each axis below gives: plain statement / what the current text settles / `[PROPOSED]` reading /
positive example / negative example / classification / missing rule / candidate readings /
suggested wording / trade-off.

---

## 2. The axes

### Axis 1 — Boundary of "rewrites it knows about"
**Plain**: the text says the PEP must apply every rewrite *it knows about*. What about a rewrite it does not know?
**Current text**: undefined. The set is not defined, and the action on an unrecognised rewrite is not stated.
**[PROPOSED]**: treat "not known" as "cannot confirm unchanged" and refuse — consistent with rejecting unrecognised `(scheme,type)` constraint identities in the value grammar we use (fail-closed), while how a value is evaluated stays with the declaring scheme.
**Positive**: the binding declares its rewrite set; the PEP applies one of those rewrites and continues.
**Negative**: a rewrite appears that the selected mapping revision does not declare; the PEP neither applied nor noticed it.
**Classification**: UNDETERMINED
**Missing**: where the rewrite set is declared, how it is versioned, how a PEP learns it is behind, and the action on an unknown rewrite.
**Candidate readings**: (a) refuse on any unknown rewrite; (b) continue with the understood part; (c) mark the check incomplete and still apply.
**Suggested wording**: "A PEP MUST apply exactly the rewrites declared by the selected mapping revision. If a rewrite is observed that the selected mapping revision does not declare, the PEP MUST treat the input as changed and refuse."
**Trade-off**: fail-closed refuses during fast binding evolution (re-evaluation first can soften this); fail-open abandons the invariant.

### Axis 2 — What "method" is compared against
**Plain**: is the compared method the name, or the name together with the mapping revision that produced it?
**Current text**: undefined.
**[PROPOSED]**: compare the action identifier in the projected request *and* the mapping revision that produced it (see axis 3).
**Positive**: same `tools/call` name under the same mapping revision.
**Negative**: the name is unchanged but the selected mapping moved to a revision that redefined the tool.
**Classification**: UNDETERMINED
**Missing**: the canonical form of a method and whether it carries the mapping revision.
**Candidate readings**: (a) name only; (b) name plus revision; (c) name plus mapping identity.
**Suggested wording**: "The method comparison MUST include the identity and revision of the mapping that produced it; a method name that is unchanged under a different mapping revision is not unchanged."
**Trade-off**: folding the revision in makes every mapping edit re-evaluate (safer, noisier); keeping them separate needs axis 3.

### Axis 3 — Selected mapping: identity or revision
**Plain**: is the mapping compared by identity, or by identity plus content? What if the registry changed in between?
**Current text**: undefined; "selected mapping ... unchanged" does not define the compared object.
**[PROPOSED]**: compare mapping identity plus content digest; a digest change is a change; a re-matched "equivalent but different" mapping counts as changed unless the digest matches.
**Positive**: same digest, no registry update in between.
**Negative**: the registry publishes a new revision mid-flight; the PEP re-matches to a mapping that is semantically equivalent but has a different digest.
**Classification**: UNDETERMINED
**Missing**: how a mapping is identified (URI, digest), how a revision is bound to it, and whether "equivalent but different" is decidable.
**Candidate readings**: (a) identity only; (b) identity plus digest; (c) identity, with re-evaluation whenever the registry changed.
**Suggested wording**: "A mapping comparison MUST be by the mapping's content digest, not by its name or location. If a selected mapping's digest differs from the one used at evaluation time, the input MUST be treated as changed."
**Trade-off**: digest comparison blocks same-name-different-content; the cost is re-evaluation on harmless registry edits.

### Axis 4 — Comparison basis
**Plain**: what exactly is compared — raw JSON-RPC bytes, a canonical form, a digest, or the projected authorization request?
**Current text**: undefined; the phrase "input values" names no object.
**[PROPOSED] (D1)**: the projected authorization request object that the decision actually evaluated. Rationale: the decision's input is the only thing relative to which "unchanged" means anything. Cost: the projection itself must be deterministic, otherwise the uncertainty moves from bytes to projection.
**Positive**: identical projected object (method, mapping revision, resource, action, context).
**Negative**: raw bytes differ while the projected object is identical (member order, equivalent number forms) — a byte basis would report a spurious change.
**Classification**: UNDETERMINED
**Missing**: determinism and version binding for the projection (who defines it; whether changing it counts as changing the input).
**Candidate readings**: (a) raw bytes; (b) canonical bytes; (c) a digest; (d) the projected request object.
**Suggested wording**: "The comparison basis is the authorization request object produced by the selected mapping revision. The projection MUST be deterministic; a change to the projection definition is itself a change of the comparison basis and MUST force re-evaluation."
**Trade-off**: a projected basis is testable; it requires versioning the projection definition.

### Axis 5 — Member order
**Plain**: are `{"a":1,"b":2}` and `{"b":2,"a":1}` the same input?
**Current text**: silent — but JSON itself is not: RFC 8259 section 4 states that object member order is not semantic.
**[PROPOSED]**: canonical serialization sorts members, so both spellings produce identical bytes.
**Positive**: probes `a05-key-order` and `a05-key-order-nested` — all three implementations canonicalize both spellings to identical bytes (`same=true`).
**Negative**: comparing received bytes would report a change and force a pointless re-evaluation.
**Classification**: **DETERMINED** (follows from RFC 8259 section 4)
**Missing**: nothing, provided the basis is the canonical/projected object (axis 4).
**Suggested wording**: "Member order is not semantic: an input whose members are reordered is unchanged."
**Trade-off**: bound to the axis 4 reading; with a raw-bytes basis this axis reverts to UNDETERMINED.

### Axis 6 — Duplicate members
**Plain**: the same member appears twice — first wins, last wins, or refuse?
**Current text**: undefined. RFC 8259 section 4 says names *should* be unique but does not define behaviour for duplicates, so parsers differ.
**[PROPOSED]**: refuse the object with a stable reason (`invalid_params_duplicate_key`). Both first-wins and last-wins have implementation precedent, so either choice makes the answer depend on the parser.
**Positive**: probe `a06-duplicate-key` on the raw path — all three implementations refuse.
**Negative**: the decoded path alone drops the duplicate (the probe shows both sides canonicalizing identically), so the change disappears. **This is why the check must see the original text.**
**Classification**: DIVERGENT
**Missing**: the basis must retain the original member sequence, or the property is unobservable.
**Candidate readings**: (a) first wins; (b) last wins; (c) refuse.
**Suggested wording**: "An input containing a duplicate member name MUST be treated as changed and refused; the comparison basis MUST retain the original member sequence, since decoding MAY drop duplicates."
**Trade-off**: refusal excludes some JSON dialects; it buys cross-parser agreement.

### Axis 7 — String normalization
**Plain**: NFC vs NFD, `\u00e9` vs literal `é`, case, lone surrogates — which of these are changes?
**Current text**: undefined.
**[PROPOSED]**: exact equality after canonical serialization: no Unicode normalization, no case folding; an escape and its literal spelling are the same character once decoded; malformed Unicode (lone surrogate, invalid UTF-8) is refused with a stable reason.
**Positive**: probe `a07-escape-vs-literal` (identical bytes on all three); probe `a07-lone-surrogate` (identical refusal on all three).
**Negative**: probes `a07-nfc-vs-nfd` and `a07-case` are judged different by all three — so an upstream normalization pass would trigger re-evaluation.
**Classification**: DIVERGENT (exact equality vs Unicode equivalence)
**Missing**: whether Unicode-normalized equivalence is allowed; if it is, it belongs in the declared rewrite set (axis 1).
**Candidate readings**: (a) exact; (b) NFC/NFD equivalent; (c) case-insensitive.
**Suggested wording**: "String comparison is exact after canonical serialization: no Unicode normalization and no case folding is applied unless the selected mapping revision declares it as a rewrite."
**Trade-off**: exact equality is testable; tolerating NFC/NFD requires declaring it as a rewrite.

### Axis 8 — Number normalization
**Plain**: are `1`, `1.0`, `1e0` the same value? What about `NaN` / `Infinity`?
**Current text**: undefined.
**[PROPOSED]**: canonicalize per RFC 8785 section 3.2.2.3 (ECMAScript `Number::toString`), so all three forms render as `1` and are unchanged; non-finite values and over-precision literals are refused.
**Positive**: probes `a08-int-forms` and `a08-int-exponent` — identical bytes on all three.
**Negative**: probe `a08-nonfinite` (`1e400`) is refused by all three; an upstream rewrite from `1e400` to `1` is a change that gets refused, not "unchanged".
**Classification**: UNDETERMINED (the current text names no numeric equivalence)
**Missing**: the numeric equivalence rule (double, decimal, canonical form) and the handling of over-precision and non-finite input.
**Candidate readings**: (a) IEEE-754 double equality; (b) decimal literal equality; (c) canonical JSON form.
**Suggested wording**: "Numbers are compared in their canonical JSON form (RFC 8785 section 3.2.2.3); values that have no finite canonical form MUST be refused."
**Trade-off**: binding to a canonical form gives cross-language agreement cheaply; decimal-exact comparison is expensive across languages.

### Axis 9 — Absent vs null vs empty
**Plain**: a member that is absent, a member that is null, and an empty value are three different things.
**Current text**: undefined.
**[PROPOSED]**: the three states differ: absent under a bounded grant is `params_missing`; `null` is invalid (`invalid_params_null`); an empty string is a legal string; additionally, no params and `params:{}` are equivalent.
**Positive**: decision probes `d02` (null under a present bound) and `d07` (missing member) — all three implementations agree on the distinct reason codes.
**Negative**: treating `{"limit":null}` as "limit not supplied" inverts the outcome.
**Classification**: DIVERGENT (reading null as absent reverses the answer)
**Missing**: the action for each of the three states, stated in the text.
**Candidate readings**: (a) three distinct states; (b) null means absent; (c) null means empty.
**Suggested wording**: "Absent, null and empty are three different inputs. An absent member MUST NOT be treated as null, and null MUST NOT be treated as an absent member."
**Trade-off**: three-state clarity is testable; JSON producers must not use null for "no value".

### Axis 10 — Type coercion
**Plain**: are `1` and `"1"` the same input? `true` and `"true"`? `true` and `1`?
**Current text**: undefined.
**[PROPOSED]**: no coercion. Booleans match by exact equality and are never treated as numbers; a number and a string that render alike are different values.
**Positive**: decision probes `d01` (`true` against a numeric bound) and `d09` (`"1"` against a number) — all three implementations refuse with the same reason.
**Negative**: an implementation that parses `"1"` into 1 lets an input through that must be refused; this is the most common cross-language divergence.
**Classification**: DIVERGENT (strict versus coercing)
**Missing**: the strictness of the comparison, stated in the text.
**Candidate readings**: (a) strict; (b) coercing for string/number; (c) a declared coercion table.
**Suggested wording**: "Input values MUST be compared without type coercion: a number and a string that render alike are different values, and booleans are never numbers."
**Trade-off**: strict comparison is testable and matches "unchanged" literally; coercion needs a rule per combination.

### Axis 11 — Array order and duplicates
**Plain**: are `[1,2]` and `[2,1]` the same input? `[1,1]` and `[1]`?
**Current text**: undefined. In JSON an array *is* ordered (RFC 8259 section 5), so a byte comparison necessarily reports a change.
**[PROPOSED]**: set semantics exist only on the grant side (a granted array is the set of allowed values); no set semantics is defined for "input equality".
**Positive**: decision probes `d05` (grant `[1,2,3]` against operation `[3,2,1]`) and `d06` (operation `[1,1]`) — all three implementations allow, i.e. order-insensitive at the authorization layer.
**Negative**: applying that same set reading to input equality would call `[1,2]` and `[2,1]` unchanged, while a byte/JCS comparison calls them changed. **Both readings have support; the text decides neither.**
**Classification**: DIVERGENT (list semantics versus set semantics)
**Missing**: which semantics applies to input equality, and the treatment of duplicate elements.
**Candidate readings**: (a) list (order significant); (b) set (order insignificant); (c) per-member declaration.
**Suggested wording**: "Unless the selected mapping revision declares an array-valued member as a set, array order and duplicate elements are significant, and a reordering or duplication is a change."
**Trade-off**: list semantics matches canonical bytes and is trivial to implement; set semantics requires a per-member declaration.

### Axis 12 — Where an over-limit input is refused
**Plain**: a rewrite pushes the serialized size or nesting depth past a limit — who refuses, and with what reason?
**Current text**: undefined; the quoted material mentions no limits.
**[PROPOSED]**: check at the input boundary, before any decision layer, using canonical UTF-8 octets and depth, with a stable reason (`invalid_params_size`). Measuring in code points or UTF-16 units is non-conforming in the language we implement.
**Positive**: the published corpus pins over-limit refusal on both the raw and the decoded path; all three implementations agree.
**Negative**: checking after the rewrite or after forwarding lets an over-limit input proceed first and fail later, with no observable reason.
**Classification**: UNDETERMINED
**Missing**: whether limits exist, their values, the layer, and the reason code. Note that `invalid_params_size` is CLC's code, offered here as `[PROPOSED]`, not as a COAZ requirement.
**Candidate readings**: (a) refuse at the input boundary; (b) refuse after the rewrite; (c) no limit, handled downstream.
**Suggested wording**: "Where a binding defines input limits, they MUST be checked at the input boundary before evaluation, and exceeding them MUST be a refusal, not a modification."
**Trade-off**: boundary checking is observable and testable; deep checking cannot guarantee the "unchanged" conclusion.

### Axis 13 — Added members
**Plain**: a rewrite adds a member — is that a change? What if the policy ignores that member?
**Current text**: undefined.
**[PROPOSED]**: under a bounded grant, an added undeclared member is refused (`undeclared_param`); under an unbounded grant it does not affect the authorization outcome, but the canonical bytes have changed — "input unchanged" and "decision unchanged" are two different statements.
**Positive**: decision probe `d03` (grant declares `a`, operation adds `extra`) — all three implementations refuse.
**Negative**: calling an ignored added member "unchanged" means the old input was authorized while a new input is executed.
**Classification**: DIVERGENT (ignore versus count as change)
**Missing**: the treatment of added members, and the choice between comparing the whole input and comparing only the members that participated in the decision.
**Candidate readings**: (a) any added member is a change; (b) only compared members count; (c) binding declares the compared set.
**Suggested wording**: "An added member is a change of the input even when the policy ignores it; if a binding intends to ignore members, it MUST declare the compared member set explicitly."
**Trade-off**: comparing everything is safe but re-evaluates on harmless additions; declaring the compared set is precise but must be enumerated.

### Axis 14 — Failure semantics: re-evaluate or refuse
**Plain**: the text offers two actions and does not say how to choose; nor which reason code, nor who observes the outcome.
**Current text**: undefined — both actions are present, with no selection rule.
**[PROPOSED]**: the language does not prescribe the PEP's orchestration, but it does prescribe stable reason codes; a refusal should carry one, and a re-evaluation should be auditable as a second decision over the same input.
**Positive**: the change can be absorbed by a fresh evaluation (for example the mapping was updated and the new decision is still allow), with a new record.
**Negative**: neither action leaves a trace, so nobody can tell afterwards whether the change widened or narrowed authority.
**Classification**: UNDETERMINED
**Missing**: the selection rule, the reason vocabulary, and the observability requirement.
**Candidate readings**: (a) always refuse; (b) re-evaluate when possible, otherwise refuse; (c) left to each binding.
**Suggested wording**: "A PEP MAY re-evaluate a changed input; if it does not, it MUST refuse. Either way the outcome MUST be observable with a stable reason, and a re-evaluation MUST NOT reuse the previous permit."
**Trade-off**: allowing re-evaluation is more usable but needs an audit surface; refuse-only is safest and least usable.

### Axis 15 — Atomicity of check and use
**Plain**: "before applying a permit" — which segment is atomic, and what happens if the input is modified concurrently?
**Current text**: undefined; the boundary and concurrency are not mentioned.
**[PROPOSED]**: verification and application operate on the same immutable input snapshot, and the comparison records the digest of that snapshot rather than re-reading a mutable source.
**Positive**: one immutable snapshot is compared and forwarded; outside changes are irrelevant to this request.
**Negative**: compare one object and forward another that was re-read between the two steps.
**Classification**: UNDETERMINED
**Missing**: the definition of atomicity (time window, object identity) and the handling of concurrent modification.
**Candidate readings**: (a) one immutable snapshot; (b) re-read but re-verify; (c) implementation-defined.
**Suggested wording**: "Verification and application MUST operate on the same immutable input snapshot; re-reading the input between verification and application is a change and MUST force re-evaluation or refusal."
**Trade-off**: snapshot semantics is easy to implement and test; locking the source is not realistic in distributed deployments.

### Axis 16 — "Never apply the old permit"
**Plain**: a permit has no identity today, so how does the PEP know that a given permit is "old"?
**Current text**: undefined; the sentence uses "old permit" without defining what makes one old.
**[PROPOSED]**: bind the comparison result to something — at minimum the digest of the evaluated input including the mapping revision. This is **not** an attempt to add validity windows or one-time capabilities, which belong to the adjacent proposals.
**Positive**: the permit is bound to an input digest; a failed comparison makes it inapplicable.
**Negative**: the permit carries an opaque id only, so the PEP cannot tell whether it corresponds to the current input.
**Classification**: UNDETERMINED
**Missing**: the binding representation between a permit and its input/mapping, and the treatment of one permit used after the input changed.
**Candidate readings**: (a) bind to the input digest; (b) add validity/nonce; (c) no binding, re-decide every time.
**Suggested wording**: "A permit MUST be bound to the digest of the evaluated input (including the mapping revision); a permit whose binding does not match the current input is not applicable."
**Trade-off**: digest binding is testable; it requires a field on the permit representation, which is a COAZ framework decision, not a conclusion of this analysis.

### Axis 17 — Unrecognised assertions or rewrite types (listed separately)
**Plain**: on an unknown assertion or rewrite type, refuse, or continue with the understood part?
**Current text**: not directly stated — but **silently dropping a conjunct is the classic failure mode**: treating an unknown item as absent removes a condition.
**[PROPOSED]**: refuse on anything unrecognised. In the value grammar we implement, an unrecognised `(scheme,type)` is rejected before any decision layer, and "unrecognised" is a different reason code from "recognised but malformed".
**Positive**: decision probes `d10` (an unknown constraint identity) and `d12` (a malformed constraint type) — all three implementations refuse, with distinct reasons.
**Negative**: an implementation that knows only one constraint type treats the others as absent, widening authority — exactly the direction this invariant is meant to prevent.
**Classification**: UNDETERMINED (COAZ does not say; three-implementation agreement is the available evidence)
**Missing**: the action and reason code for unrecognised items, and whether partial understanding is allowed.
**Candidate readings**: (a) refuse (the three implementations' current behaviour); (b) continue and mark; (c) route to a residual-obligation channel.
**Suggested wording**: "A PEP MUST refuse when it encounters an assertion or rewrite type it does not recognise; dropping an unrecognised conjunct is a change of the evaluated input."
**Trade-off**: fail-closed blocks new types on old PEPs (binding revision and capability negotiation soften this); fail-open abandons the invariant.

---

## 3. What the material does not do

- It does not enumerate rewrites or define equivalence classes (that belongs to COAZ and each binding).
- It does not touch the deferred-effect / consequence-admission layer, including the adjacent proposals that mint one-time authority; no gap is claimed there.
- It does not claim a gap in the gateway or MCP-server hop, which has been addressed elsewhere.
- It does not promote any particular credential system; it contributes decision and verification semantics only.
- External material that could not be retrieved while writing this is marked UNVERIFIED rather than guessed.

## 4. Differential evidence

`divergence-report.md` records the three-implementation run behind the readings used above: 18
value-level cases and 12 decision-level cases, with the same verdict, reason code and canonical
bytes from all three implementations, and the harness is in `reproduce/`. The readings are marked
`[PROPOSED]` because the implementations share an author: their agreement is a regression test for
the reading, not independent validation.
