# Standard Payments Capability Reference

> scheme_id: `std/payments-v1` · Version `1.0.0` · Vendor `std` / Product `payments-v1`

Standard semantics for AI-agent money movement and account operations:
transfers, payouts, account opening, KYC reads, refunds and limit changes,
each bounded by amount **ceilings** (scalar number upper bounds per CLC-v1
§6.2) and **allowlists** (currency, counterparty, account = categorical
arrays). A request may send a scalar (must be a member) or an array (every
element must be a member).

## Capability Catalog

| Capability | Summary |
|------|------|
| `transfer` | Transfer funds to an allowlisted counterparty |
| `payout` | Initiate a payout to an external allowlisted counterparty |
| `account:open` | Open an account on an allowlisted product |
| `kyc:read` | Read KYC status for allowlisted accounts |
| `refund` | Refund an allowlisted counterparty |
| `limit:set` | Adjust a spending limit on an allowlisted account |

## Detailed Capability Semantics

### `transfer`
- **summary**: Move money within amount ceiling, currency and counterparty
  allowlist.
- **usage**: Invoice payment, commission, refund execution by agents.
- **when_not**: Never granted without an amount ceiling, a currency set, and a
  counterparty allowlist.
- **examples**: `amount=100000, currency=[USD], counterparty=[acme-eu]`
- **parameters**:
  - `amount` (number, **upper bound**, maximum 1000000).
  - `currency` (array, enum `USD`/`EUR`/`CNY`).
  - `counterparty` (array, **allowlist** — membership is the grant's scope).
  - `account` (array, allowlist).
- **domain types**: `currency`/`counterparty`/`account` = sets;
  `amount` = scalar upper bound.

### `payout`
- **summary**: Disbursement with amount ceiling and counterparty allowlist.
- **usage**: Vendor/creator payouts.
- **when_not**: High-value — always carries a counterparty allowlist and a
  bounded amount.
- **parameters**: `amount` (upper bound, 500000), `currency` (array, enum),
  `counterparty` (array, allowlist), `account` (array, allowlist).

### `account:open`
- **summary**: Create an account of an allowed type.
- **usage**: Agent-assisted onboarding for approved product lines.
- **when_not**: Not granted unapproved account classes or KYC-bypassing flows.
- **parameters**: `account` (array, enum `checking`/`savings`).

### `kyc:read`
- **summary**: Check KYC verification state before money movement.
- **usage**: Pre-transfer verification step.
- **when_not**: Compliance gate — grant only after counterparty KYC is
  verified.
- **parameters**: `account` (array, allowlist).

### `refund`
- **summary**: Reverse a payment within amount ceiling and counterparty
  allowlist.
- **usage**: Agent-led refunds on approved transactions.
- **when_not**: Never grant refunds beyond the original transaction amount.
- **parameters**: `amount` (upper bound, 10000), `currency` (array, enum),
  `counterparty` (array, allowlist).

### `limit:set`
- **summary**: Lower (or raise within cap) limits for an account.
- **usage**: Treasury agents tuning account daily/spend limits.
- **when_not**: Break-glass — raising limits should require human approval and
  audit.
- **parameters**: `account` (array, allowlist), `amount` (upper bound,
  1000000).

## Constraint Types

Grants against this scheme may carry constraints:

| Constraint | Origin | Scope | In CLC v1 known set? |
|------|------|------|------|
| `time:window` | `varwof/constraint-v1` | allowed operation window | **yes** |
| `op:audit:required` | `varwof/constraint-v1` | mandatory audit trail | **no** → fail-closed |
| `payments:quota:daily:<n>` | this scheme (§ extension point) | **cumulative** daily quota | **no** → fail-closed |

An unknown constraint type yields `deny("unknown_constraint")` (fail-closed,
CLC-v1 §8). Note that **CLC v1 decides single operations only**: the
`total over a day` semantic of `payments:quota:daily:<n>` is a **cross-request
accumulation** that CLC v1 does not define (v1 has single-decision upper
bounds only). It is recorded as a **CLC v2 requirement** (see design-notes
§18); it must not be emulated by weakening the single-operation bound.

## Disclaimer

This authorization layer defines the **operation boundary** for an AI agent
moving money. It is **not an anti-fraud, risk, or clearing/settlement
mechanism** and does not replace the financial institution's compliance
controls (AML/CFT, sanctions, fraud detection, reconciliation). Compliance and
risk duties remain with the financial institution.