# Standard Database Capability Reference

> scheme_id: `std/database-v1` · Version `1.0.0` · Vendor `std` / Product `database-v1`

Standard semantics for database access capabilities. Any database engine can
implement this contract through an adapter. Three restriction levels:
**tables** (object level), **columns** (column level), and **row filtering**
via WHERE (row level).

Full capability identifier format: `std/database-v1:capability_id`
(e.g., `std/database-v1:query:SELECT`).

## Capability Catalog

| Capability | Summary | Related |
|------|------|----------|
| `query:SELECT` | Read-only query within the authorized scope | query:INSERT |
| `query:INSERT` | Insert into authorized tables/columns | query:SELECT |
| `query:UPDATE` | Update within the authorized column and row-filter scope | query:SELECT |
| `query:DELETE` | Delete rows matching the row filter only | query:SELECT |
| `query:EXECUTE` | Execute allowlisted stored procedures/functions | query:SELECT |
| `admin:DDL` | Apply schema changes to allowlisted tables | admin:TRUNCATE |
| `admin:TRUNCATE` | Truncate allowlisted tables | admin:DDL |

## Detailed Capability Semantics

### `query:SELECT`

- **summary**: Read data from authorized tables within the authorized column
  and row-filter scope.
- **usage**: Data analysis, reporting, auditing, business queries.
- **when_not**: Must not be granted for write operations, unauthorized
  tables/columns, or missing row filters (multi-tenant data).
- **examples**: `SELECT id,name FROM customers WHERE tenant_id='org-a' LIMIT 100`
- **parameters**:
  - `tables` (array, required): allowlisted table names (1..32).
  - `columns` (object, required): table -> list of allowed columns; `"*"`
    means all columns.
  - `filter_columns` (object): columns usable only in WHERE, never returned
    (e.g. `tenant_id`).
  - `row_filter` (object): table -> structured predicate (raw SQL prohibited);
    column/op/value (`=`, `!=`, `<`, `<=`, `>`, `>=`, `in`, `not in`,
    `between`, `like`, `is null`, `is not null`) or `and`/`or`/`not`
    composition.
  - `limit` (object): `max` (1..100000) bounds the row count.
  - `aggregate` (object): allowed aggregate functions.

### `query:INSERT`

- **summary**: Insert data into authorized tables, only into authorized columns.
- **usage**: Append-only workloads (logs, events, orders).
- **when_not**: Must not be granted when the agent only reads; columns not in
  the allowlist must be rejected.
- **examples**: `INSERT INTO audit_log(event, ts) VALUES ('login', now())`
- **parameters**: `tables` (required), `columns` (required).

### `query:UPDATE`

- **summary**: Update data within the authorized column and row-filter scope.
- **usage**: Correcting records the agent owns or is responsible for.
- **when_not**: Never without a row filter for multi-tenant tables; column
  allowlist must be narrow.
- **examples**: `UPDATE orders SET status='shipped' WHERE tenant_id='org-a' AND id=42`
- **parameters**: `tables` (required), `columns` (required), `row_filter`.

### `query:DELETE`

- **summary**: Delete only rows matching the row filter.
- **usage**: Hard-delete of records explicitly scoped to the agent's tenant.
- **when_not**: Highest-risk write; missing row filter must be rejected.
- **examples**: `DELETE FROM sessions WHERE tenant_id='org-a' AND expired=1`
- **parameters**: `tables` (required), `row_filter` (required).

### `query:EXECUTE`

- **summary**: Execute stored procedures or functions on the allowlist.
- **usage**: Invoking curated procedures with side effects.
- **when_not**: Arbitrary procedure execution must never be allowed.
- **parameters**: `procedures` (array, required, 1..N).

### `admin:DDL`

- **summary**: Apply schema changes to allowlisted tables.
- **usage**: Migrations owned by the agent or platform team.
- **when_not**: Not for data-plane agents; operations are limited to
  `create`, `alter`, `drop` on allowlisted tables.
- **parameters**: `operations` (array, required; enum `create`/`alter`/`drop`),
  `tables` (required).

### `admin:TRUNCATE`

- **summary**: Truncate allowlisted tables.
- **usage**: Resetting staging or ephemeral tables.
- **when_not**: Never for production data tables outside the allowlist.
- **parameters**: `tables` (required).
