# Standard Digital Wallet Capability Reference

> scheme_id: `std/wallet-v1` · Version `1.0.0` · Vendor `std` / Product `wallet-v1`

Standard semantics for AI-agent access to digital wallets: balance reads,
transfers with amount/recipient bounds, and history queries. Any wallet
backend can implement this contract through an adapter.

## Capability Catalog

| Capability | Summary | Related |
|------|------|----------|
| `balance` | Read balances for authorized assets/networks | transfer |
| `transfer` | Transfer within amount/recipient/asset/network bounds | balance, history |
| `history` | Read transaction history | balance |

## Detailed Capability Semantics

### `balance`
- **summary**: Query balance of authorized assets on authorized networks.
- **usage**: Agents that need to check funds before proposing actions.
- **when_not**: Not granted when the agent should not know balances.
- **examples**: `GET /v1/wallet/balance?asset=USDC`
- **parameters**: `assets` (array, required), `networks` (array).

### `transfer`
- **summary**: Send authorized assets to allowlisted recipients, bounded per
  transaction and per day.
- **usage**: Agents that pay invoices, refunds, or bounties on behalf of the
  principal.
- **when_not**: High-risk: never without amount/recipient/asset bounds; the
  recipient allowlist is required.
- **examples**: `POST /v1/wallet/transfer {"asset":"USDC","amount":50,"recipient":"0xVendor"}`
- **parameters**: `assets` (array, required), `networks` (array),
  `max_amount_per_tx` (number >= 0), `max_amount_daily` (number >= 0),
  `recipients` (array, required, allowlist).

### `history`
- **summary**: Query past transactions within scope.
- **usage**: Agents that reconcile payments or report spend.
- **when_not**: Not needed for agents that only initiate payments.
- **examples**: `GET /v1/wallet/history?limit=50`
- **parameters**: `assets` (array, required), `networks` (array).
