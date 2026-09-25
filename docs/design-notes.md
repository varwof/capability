# CLC-v1 design notes — decision record (English)

Normative text: [`capability-language-core-v1.md`](capability-language-core-v1.md).
Principles: [`capability-language-core-principles-v1.md`](capability-language-core-principles-v1.md).
Full narrative history (Chinese, superset of this record):
[`capability-language-core-design-notes-zh.md`](../archive/capability-language-core-design-notes-zh.md)
(archived 2026-09-24; this file is the decision record of record).

This file is the English record of the **decisions** a reviewer is likely to ask
about: what was chosen, what was rejected, and why.  Entries are dated.

## D1 — Numeric parameter domain semantics (2026-09-10, v1.1). Option A chosen.

A number inside a granted **array** denotes that exact value, not an upper bound:
`grant {"station":[3]}` does not cover `station 2` (deny `not_in_enum`), whereas a
scalar number keeps bound semantics (`{"max_rows":100}` covers 50).
Rejected Option B (array members as bounds) because it silently widens categorical
parameters — station, cell, batch, tool id — where a bound is meaningless.
Scheme authors SHOULD encode categorical parameters as arrays.

## D2 — Resolved reason ordering (2026-09-10, v1.2).

When several conditions fail at once, exactly one code is reported: the first
applicable layer in a fixed order.  The ordering is normative (§9.3), and the
corpus asserts the **canonical reason**, not just the verdict
(canonical = everything before the first `:` in a code, §9.4).

## D3 — Fail-closed on an absent/empty effective grant (2026-09-10, rev 5).

`Authorize` called with no grant (or an empty record) MUST return
`deny(capability_not_authorized)` rather than raising.  The empty-effective-grant
check is a **pre-check** that precedes layer 1 — so it wins even when the operation
is also malformed (`decide-016`).

## D4 — Input normalization and language revision (2026-09-11).

- §6.2.1: params are normalized at the input boundary in a fixed order —
  **size/depth → duplicate keys → number shape**.  Limits: serialized form ≤ 512
  bytes (octets of the canonical UTF-8 form) and nesting depth ≤ 32, counting the
  outermost object as level 1.  Over the limit → `invalid_params_size`.
- §12.1: an input declares its revision; an implementation evaluates it only when
  the revision is compatible (same major, minor ≤ its own), otherwise
  `deny(unsupported_language_revision)` **before any layer**.  No silent downgrade.

## D5 — Key closure (`undeclared_param`, 2026-09-11). Fail-closed chosen.

A bounded grant rejects an operation that declares a parameter the grant does not
declare.  The alternative ("a grant constrains only what it declares") was
rejected: it lets an operation smuggle a parameter past a grant that never
authorized it.  See D8 for how closure composes with intersection.

## D6 — Spec-text closeout (2026-09-11).

Six reason codes that existed only in the implementations and the corpus were added
to §9.4 (`undeclared_param`, `invalid_params_duplicate_key`, `invalid_params_number`,
`invalid_params_size`, `unsupported_language_revision`, `absent_source`);
§12.1 was added; §9.3 was rewritten as a pre-check plus **11 layers** so the layer
numbers cited by the corpus point at the right rows; the appendix vector counts were
brought in line with the machine-readable corpus.

## D7 — P11 "composition narrows only" (2026-09-11).

An intersection must stay inside every source and must not depend on source order.
Two relations are involved and must not be conflated:

- **source coverage (⊑, §7 rule 2)** — grant vs grant, comparing only the keys the
  source declares; a parameter is authorized when *some* source declares it, so the
  effective key set is the union;
- **`Entails`** — grant vs *operation*, the authorization relation, which applies
  key closure (D5).

Closure belongs to the **effective** grant only: every verifier entry point
evaluates exactly one grant (`Authorize(effectiveGrant, op)`;
`Entails(signerGrant, ruleCapability)`), and no code path re-evaluates each source.
An earlier property test re-applied each source's closure separately and reported
176 "failures" that were an artefact of the question, not of the implementation.

## D8 — Three divergences found by probing (2026-09-11, evening).

After the third spec batch, six probe vectors were run against **all three**
implementations (Go, Python, TypeScript):

| Probe | Spec | Go | Python | TypeScript |
|---|---|---|---|---|
| boolean exact (`true` vs `1`) | deny `params_exceed_grant` | ✅ | ❌ **allow (fail-open)** | ✅ |
| layer 6 (null) before layer 7 (presence) | `invalid_params_null` | ❌ `params_missing` | ✅ | ✅ |
| wildcard-shaped operation id | `unsupported_wildcard` | ❌ `invalid_capability_id` | ✅ | ✅ |

Root causes and fixes:

1. **Python** ordered the boolean branch after the numeric branch, and `True == 1`
   in Python — a boolean grant was satisfied by `1` (fail-open).  Boolean handling
   now precedes the numeric branch, and `bool` is excluded from numeric comparison.
2. **Go `Entails`** tested `op.Params == nil` before grant-side null validation;
   the null check now runs first (in `paramsSubset` too, ordered 5 → 6 → 7).
3. **Go `Authorize`** collapsed every layer-1 failure into `invalid_capability_id`;
   it now propagates the validator's specific code.

The corpus could not see any of this: it had no boolean-vs-number, null-plus-missing
params, or wildcard-shaped operation id inputs.  Four vectors were added
(`params-022/023/024`, `decide-018`).

## D9 — Raw-params check order in TypeScript (2026-09-11, evening).

The TypeScript `validateRawParams` was a single-pass parser: it threw
duplicate-key / bad-number errors *during* parsing and checked the total size only
at the end, so for "over-limit + duplicate" the reported code was the reverse of
§6.2 item 5.  It is now **two passes** — pass 1 computes size and depth and throws
`invalid_params_size`; pass 2 enforces duplicates and number shape.  Depth is still
checked inline (it belongs to item 4).  Three combination vectors pin the order:
`params-025` (over-limit + duplicate → size), `params-026` (over-limit + `1e400` →
size), `params-027` (duplicate + `1e400`, under the limit → duplicate).

## D10 — CLC-1.3 closeout: verdict channel, constraint identity, multi-grant (2026-09-12).

Two review observations closed the CLC-1.2 sweep:

**Observation 1: "allow + unresolved" is a pseudo-allow.**  A decision that
says `allow` while carrying constraints the core cannot evaluate invites
consumers to act first and ask later.  Rev CLC-1.3 gives the residual
channel its own verdict value, `allow_unresolved` (§8.4): it is a distinct,
single surface (the informational `verbatim` field was removed from all three
implementations), and the consumer's obligation is unchanged — evaluate each
listed constraint or deny.  **Decision:** the verdict enum gains
`allow_unresolved`; `decide-020/024` pin time/network cases and `decide-019`
pins the cross-midnight single-window segment as `invalid_constraint`
(rewritten from the CLC-1.2 corpus where it generated `unresolved`).

**Observation 2: multi-grant authorization was undefined.**  A verifier that
holds several authorities for the same operation needs a rule.  §9.3 now
defines aggregation: any covering-and-allowing grant authorizes (union, so a
narrow grant cannot veto a broad one); residual obligations union across the
covering-and-allowing grants; when none allows, the first covering grant's
params/constraint reason in canonical (input) order is returned.  Implemented
as `AuthorizeSet(grants, op)` (single-grant `Authorize` is the degenerate
case).  The corpus pins it with `decide-028` (`{}` ≡ absent → any params
allowed), `decide-029` (any-allow) and `decide-030` (all-deny, first reason).

Two smaller closures rode along because they changed the same lines:
constraint identity is now the full `scheme:type` pair (only
`varwof/constraint-v1` is core-recognized — a same-name constraint under any
other scheme is `unknown_constraint`), and the time-window value grammar
forbids single segments crossing midnight (the reserved `end:"00:00"`
denotes next-day midnight, so a crossing is *split* into plain same-day
segments like `22:00→00:00` + `00:00→06:00`).

## D11 — CLC-1.10/1.11 candidate closeout: `param_bounds` and `Resolve` (2026-09-21).

Two of §13.10's four *candidate v1.x* items were closed as additive core
revisions, in the order 1.1 → 1.2.

**1.1 — extended parameter bounds (§6.5, CLC-1.10).**  The rejected shape was a
`{min,max}` object *inside* `params` (it collides with object recursion).  The
bounds went into a sibling grant field `param_bounds`: one value family per key
(numeric `min`/`max`/`step`, enum `enum`/`min_items`/`max_items`, nested
`nested`), an orthogonal `optional` marker, and a one-representation binding
rule (a key MUST NOT appear in both `params` and `param_bounds` →
`invalid_params_binding`).  Fractions put `params` and `param_bounds` in
different fields; `min`/`max` are inclusive; `step` uses the IEEE-754 rule
`q=v/step; q==trunc(q) && q*step==v`.  Containment narrowing is defined in
§13.4.3 — the subtlety that a **coarser** child grid is the subset (child step
must be an integer multiple of the parent's) was written backwards first and
corrected in the corpus and text.  `Intersect` refuses `param_bounds`
fail-closed (its intersection is undefined in this revision).  43 core vectors
plus 14 containment-narrowing vectors.

**1.2 — the residual-obligation consumer loop (§8.5, CLC-1.11).**  §8.4
delivered `allow_unresolved` but not the loop.  `Resolve(decision, resolutions,
now?)` adds it: each obligation is reported `satisfied`/`violated`/`unknown`,
sources combine most-restrictive-first (`violated` ≻ `satisfied` ≻ `unknown`),
and the verdict collapses to `allow` / `deny({type}:violated)` /
`allow_unresolved(remainder)`; terminal `deny`/`allow` pass through untouched.
Supplying `now` lets the **core clock** evaluate a `time:window` obligation
(half-open `[start,end)`, UTC) and gives it a **TTL**: the discharge horizon is
the end of the segment containing `now`, so a cached `allow` expires with the
window — a stale `satisfied` report is overridden by a `violated` core clock
(the most-restrictive rule).  The `now`-less path accepts a consumer assertion
(scheme owns its clock) but attaches no core TTL.  Two input-error codes
(`invalid_resolution`, `invalid_timestamp`) and 26 vectors.  The coarser
identity-level gate `Discharge` stays as the `satisfied`-only case.

Both are additive: no `Authorize` verdict, reason code or vector changes, and an
implementation that does not implement either remains CLC-A conformant.  This
also settles the §13.10.2 split — the earlier design note said `Resolve` was
core but TTL was profile policy; the owner ruled both into the core.

**1.3 — chain constraints stay out of `Contains` (§7.1, CLC-1.12).**  The
constraint-axis ruling (constraints are a *union*, not a containment, so
`Contains` must not read them) left §13.10.3 open: should `Contains` also return
the accumulated union?  The owner chose a separate function rather than
overloading the relation.  `ConstraintUnion(chain)` exposes exactly the
constraint projection of `Intersect` rule 3 — normalized union, duplicates
folded, lexically sorted — as a **projection, not a meet**: no identifier or
parameter comparison, no constraint reading/validation, no containment check,
and an empty chain fails closed with `absent_source`.  `Contains` therefore
stays the pure subset over `(identifier, parameters)`, and a consumer composes
the two (per-hop `Contains` + `ConstraintUnion` over the chain).  Folding the
union into `Contains` was rejected because it would stop the relation being a
subset on the declared tuple and a null constraint check could hide a broken
boundary.  12 vectors.

**1.4 — the fused chain check (§13.11, CLC-1.13, CLC-D).**  §13.10.4 named a
possible fourth relation.  `AuthorizeWithChain(chain, op)` is it: an empty chain
denies `absent_source`; each adjacent hop is checked with `Contains` and the
first failure denies with that hop's §13.5 code **before** op validation;
otherwise the operation is authorized against `Intersect(chain...)`.  The key
design point is soundness: because constraints are a union axis *outside*
containment, authorizing against the leaf grant alone (§13.10.4's literal
"op fits child") would let an operation pass that violates an ancestor's
constraints; the effective intersection is what brings ancestors' params and
constraints into force.  The user chose the intersection judgment and a
`Decision deny(reason)` outcome for a broken chain.  It is a CLC-D function:
CLC-D conformance now also requires it and the chain vectors.  As shipped in
CLC-1.13 it refused a `param_bounds` chain with `invalid_params_binding`
(Intersect defined no `param_bounds` intersection), rather than dropping the
bound; **1.5 supersedes that** by defining the meet.

**1.5 — `Intersect` meets `param_bounds` (§6.6, CLC-1.14).**  1.4 left a real
gap: `Contains` accepted a `param_bounds` chain hop, but the fused function's
next step, `Intersect`, refused any source carrying `param_bounds`, so a
delegation chain that used the CLC-1.10 bounds could never be authorized
(`AuthorizeWithChain` denied `invalid_params_binding`).  CLC-1.14 defines the
meet.  Per family: numeric `min` is the greatest declared minimum, `max` the
least maximum, and `step` is the **coarser** grid when one exactly divides the
other (otherwise the two grids have no single representable `step` and the meet
fails closed); the enum member sets intersect with tightened cardinality;
`nested` recurses over an identical key set; `optional` combines by
conjunction; numeric∩enum reduces to the filtered enum; scalar∩nested and
`min>max` are an empty meet (`no_overlap`).  A key must keep one declaration
site across the sources — §13.4.3 already guarantees this for a valid chain, so
the cross-site refusal only affects independent sources.  The meet is strictly
additive: a chain without `param_bounds` is unchanged, so every existing
verdict, reason code and vector is untouched; it adds 25 `BoundMeet` vectors
and two `authorize-chain` vectors (a bounds chain that now allows, and an
out-of-range request that is denied against the effective intersection).  It
also aligns `Authorize`'s params-level reason propagation with the four bound
codes, so a bound violation reports `params_out_of_range` rather than collapsing
to `capability_not_authorized`.

## D12 — Cross-family `BoundMeet` is refused (2026-09-25; decided and applied in CLC-1.15).

Iman Schrock's review of revision 1.14 found the numeric ∩ enum meet in §6.6
unsound: with numeric `{min:2,max:4}` and enum `{1,3,5}` the meet is `enum{3}`,
which **accepts the array `[3]`** — an operation the numeric source rejects
(`params_exceed_grant`, §6.5 layer 9) while the enum source admits it (§6.5
layer 8).  The meet is therefore broader than either source, and §6.6's claim
that "the enumerated members fully denote the meet" does not hold.

**Decision: remove the exception rather than repair it.**  §6.5 already states
that "mixing families (e.g. `enum` with `max` ...) is rejected
(`invalid_params_binding`)", and §6.6 already fails the cardinality-only
sub-case closed for the same reason ("two families, which the closed grammar
cannot express").  The numeric ∩ enum bullet is the one place the grammar tried
to combine instead of refuse; it goes, and every cross-family combination fails
closed with `invalid_params_binding`.

**Why removal and not repair.**  A sound cross-family meet would have to carry
both the numeric shape constraint and the enum member set — two families in one
Bound, which the closed grammar deliberately does not express.  Repairing it
would add algebra; removing it deletes a rule.  If a real need for cross-family
narrowing appears, a rule can be added then, with a sound definition.  Precedent
for adding it later is CLC-1.14 itself: it turned "a `param_bounds` chain can
never be fused-authorized" into "it can" without changing any existing
successful result.

**Companion changes.**  §6.5's enum equality is defined as JSON type-sensitive
(the same review's second finding: Python treats `true` and `1` as equal, so it
allows where TypeScript denies), and the property suite gains the invariant the
review asked for — every successful meet authorizes only operations that each
source authorizes — plus `param_bounds` cases, which the 1,184 and 784 suites
currently lack.

**Confirmed when recording it.**  §13.4.3 containment already refuses
cross-family comparison — "a numeric family bound must [be within it]", "an
`enum` family must be a subset", and "a child Bound that **adds a family the
parent does not declare** ... is `params_not_narrower`".  So of the three places
a bound is compared, two (`§6.5` grammar, `§13.4.3` containment) already refuse
cross-family and only `Intersect` combined; removing the exception makes all
three agree.

## Corpus and tooling state

| Item | State |
|---|---|
| Conformance corpus | `vectors.json` — **120 vectors** (syntax 9 / entail 47 / intersect 14 / decide 50) |
| Revision extensions | `param-bounds-vectors.json` — **43** §6.5 vectors (CLC-1.10); `resolve-vectors.json` — **26** §8.5 vectors (CLC-1.11); `constraint-union-vectors.json` — **12** §7.1 vectors (CLC-1.12); `authorize-chain-vectors.json` — **15** §13.11 vectors (CLC-1.13/1.14); `param-bounds-meet-vectors.json` — **25** §6.6 vectors (CLC-1.14) |
| Property corpus | `property-cases.json` — 1184 deterministic P11 cases, reproducible byte-for-byte |
| Implementations | Go (`varwof/register`), Python and TypeScript (`varwof/aic-capability-demo`) — all three 120/120, 1184/1184, param-bounds 43/43, resolve 26/26, constraint-union 12/12, authorize-chain 15/15 and param-bounds-meet 25/25 (0 failures; counters 869/841) |
| Schema | `vectors.schema.json` (verdict enum incl. `allow_unresolved`, `multi` switch), `param-bounds-vectors.schema.json`, `resolve-vectors.schema.json`, `constraint-union-vectors.schema.json`, `authorize-chain-vectors.schema.json` and `param-bounds-meet-vectors.schema.json`, enforced in CI together with the documented counts |

Engineering discipline carried from the principles: one contract with several
consumers; fail-closed by default; all-or-nothing generation; a gate must cover every
entry point; and every artifact needs a gate (or it drifts).

## Open items

1. **CLC-E (evidence side)**: §4.2/§6.4/§10 have text and §12 declares the
   conformance class, but there is no implementation and no vector.  Either
   implement it or state explicitly that v1 makes no CLC-E conformance claim.
2. **Third-party parity**: the three implementations share one author; an
   independent implementation is the half of P7/P8 that cannot be self-certified.
3. **Carrier citations**: no carrier document (AIC-JWT, gateway-core, types) cites
   CLC yet, and a second subset implementation exists in the WIT/WPT interop study
   whose wildcard surface is one v1 forbids.

## Slim-down attempt (2026-09-21) — reverted 2026-09-24

A slim-down of the published text was prepared on 2026-09-21 and reverted on
2026-09-24.  It had removed material that the published text carries again, and
part of what it removed was not recorded here at all.  The published text is the
revision-1.14 text in full: **nothing is held back in these notes.**  The
archive of that attempt is not kept here; it is preserved in the working
back-up outside this repository.
