<!-- Published copy in varwof/capability. Working draft and rationale live in the
     design repository; treat this copy as canonical once committed. -->

# Offline Capability Manifest Profile (OCMP) v0

> ⚠️ **Preview** — Not for production use. APIs and features may change before official release.

Status: draft profile, 2026-09-10
Scope: how to evaluate authorization **offline** using CLC-v1 semantics
Depends on: CLC-v1 (capability-language-core-v1.md), AIC / AIC-JWT (credential)

## 1. Purpose

Devices that must authorize actions while disconnected (industrial cells,
isolated networks, mobile/robotic platforms) need a defined set of inputs and
a defined failure behaviour.  This profile does not define new authorization
semantics: it reuses CLC-v1 (§6 Entailment, §7 Intersection, §9 Decision) and
specifies **what must be present locally** and **what happens when it is not**.

Non-goals: trust establishment, credential provisioning, execution lifecycle,
evidence/receipt formats (CLC-v1 §11 boundary applies).

## 2. Definitions

**Offline Capability Manifest (OCM)** — the set of artifacts provisioned to a
device so it can authorize locally:

| # | Input | Source (example) | Required |
|---|-------|------------------|----------|
| 1 | Grant set (principal-signed DA/PA + capability declarations) | AIC certificate / AIC-JWT; shift-scoped | MUST |
| 2 | Trust anchors (principal key, issuer chain) | device provisioning | MUST |
| 3 | Status snapshot: signed list with `as_of`, `valid_until`, `version` | issuer or principal | MUST (for revocation) |
| 4 | Local policy (deployment rules; not credential-bound) | device configuration | MUST |
| 5 | Local facts (e.g. cell occupied, maintenance mode, guard state) | safety PLC / sensors | scheme-declared |
| 6 | Replay state (monotonic counter or nonce pool) | TEE / secure element | MUST if the scheme requires it |

## 3. Evaluation rules (normative)

**R1 — Determinism.** Evaluation MUST depend only on the OCM inputs and the
request.  No network access, no wall-clock-dependent policy beyond R4/R5.

**R2 — Fail-closed on missing input.** If any input marked MUST in §2 is
absent or unreadable, the evaluator MUST deny.  Codes:

| Condition | Reason code |
|-----------|-------------|
| no grant covers the request (or grant absent/empty) | `capability_not_authorized` (CLC-v1 §9 layer 10) |
| trust anchor missing/unusable | `trust_anchor_missing` |
| status snapshot absent | `status_snapshot_missing` |
| local policy absent | `local_policy_missing` |
| required local fact unavailable | `fact_unavailable` |
| replay state unusable | `replay_state_invalid` |

**R3 — Snapshot validity window.** Let `t` be the trusted local time.  If
`t < as_of` or `t > valid_until`, the evaluator MUST deny
(`status_snapshot_expired`).  A stale snapshot MUST NOT be treated as "no
revocations".  The snapshot MUST be signature-verified before use, and its
`version` MUST be monotonic (a lower version than the last accepted one MUST
be rejected: `status_snapshot_rollback`).

**R4 — Credential lifetime.** Expired grants MUST be rejected
(`capability_not_authorized`).  A snapshot entry marking a grant revoked MUST
cause denial for that grant even if it is still within its lifetime
(`revoked`).

**R5 — Replay protection.** Where the scheme declares replay protection, each
accepted operation MUST consume exactly one counter value (or nonce).  Reuse
MUST be denied (`replay_detected`); a counter going backwards MUST be denied
(`replay_state_invalid`).

**R6 — Local facts.** Facts declared required by the scheme MUST be readable;
if not, deny (`fact_unavailable`).  Facts MUST NOT be invented, defaulted, or
cached beyond their scheme-declared freshness.

**R7 — Time source.** A monotonic source is REQUIRED for R3/R5 ordering.  If
wall-clock time is used and its offset from the last trusted sync exceeds the
scheme-declared tolerance, the evaluator MUST deny (`clock_unsynchronized`).

## 4. Refresh and reconnection

1. On reconnection the device MUST refresh (a) status snapshot, (b) replay
   state, (c) grants.  Operations MAY resume only after a successful refresh.
2. **Shift-scoped credentials** are RECOMMENDED: provisioning a grant set per
   shift (≤ 12 h) bounds the revocation window by the credential lifetime and
   avoids the need for online revocation.
3. Status snapshot refresh interval SHOULD be ≤ min(credential lifetime / 2,
   8 h).  Deployments MAY trade availability for stricter bounds by shortening
   `valid_until`.

## 5. Conformance classes

- **OCMP-1 (baseline)**: R1–R4 (deterministic offline evaluation with a
  freshness-bounded snapshot).
- **OCMP-2 (replay-protected)**: OCMP-1 + R5.
- **OCMP-3 (context-aware)**: OCMP-2 + R6 (local facts) + R7 (time source).

## 6. Industrial mapping (example)

For `std/robot-line-v1` with shift-scoped grants:

| Element | Offline value |
|---------|---------------|
| Grant | `{station:[3]}` + `speed ≤ 0.3` for the operator role |
| Status snapshot | valid_until = end of shift; carries any mid-shift revocations |
| Local policy | "cell must be unoccupied for auto start" |
| Local fact | safety PLC reports cell occupancy |
| Replay state | per-station operation counter in the controller's secure element |
| Deny examples | `not_in_enum` (station 2 under a station-3 grant), `status_snapshot_expired`, `fact_unavailable`, `replay_detected` |

## 7. Security considerations

- **Availability vs. security**: aggressive `valid_until` values cause
  denial-of-service in isolated plants; this profile makes the tradeoff explicit
  rather than implicit.
- **Snapshot replay/rollback**: signed + monotonic `version` (R3).
- **Counter rollback**: secure storage required; a writable counter is not a
  replay defence.
- **Fact spoofing**: fact sources are part of the trusted computing base; a
  spoofable "cell unoccupied" signal voids R6.
- **Clock manipulation**: mitigated by monotonic ordering + R7 tolerance.
- **This profile is not a functional-safety mechanism** (see the industrial use
  case): E-stop / safety PLC / interlocks remain independent.

## 8. Proposed offline test vectors (next step)

Suggest a separate `offline-vectors.json` (not part of CLC-A/B semantics):
snapshot valid / expired / not-yet-valid / rolled back; revoked grant;
replay (counter reuse); required fact unavailable; clock unsynchronized;
missing anchor; missing local policy.  Each with expected verdict + reason.

---

## 中文要点

- **目的**：规定"离线判定"需要哪些本地材料、缺了怎么拒，语义完全复用 CLC-v1，不新增授权语义。
- **六类必需输入**：授权（DA/PA+能力）、信任锚、状态快照（as_of/valid_until/version）、本地策略、本地事实、防重放状态（计数器/凭据池）。
- **七条规则**：确定性；缺输入即拒；快照过期/回滚即拒；凭证过期或已吊销即拒；重放即拒；必需事实取不到即拒；时钟不可信即拒。
- **工程要点**：**班次寿命凭证**（≤12h）把离线吊销问题转成"寿命到期"；快照刷新间隔 ≤ min(寿命/2, 8h)；重新联网后先刷新再恢复。
- **取舍**：`valid_until` 越短越安全但越容易在离线工厂里误拒——本 profile 把这个取舍显式写出来，而不是留给实现。
- **边界**：本 profile 不是功能安全机制；E-stop/安全 PLC/互锁独立于授权层。
