# Standard Data & Privacy Capability Reference

> scheme_id: `std/data-v1` · Version `1.0.0` · Vendor `std` / Product `data-v1`

Standard semantics for AI-agent access to datasets with privacy-relevant
classification: read/export/join/train/delete operations scoped by
dataset/column allowlists, row **upper bounds** (scalar numbers per CLC-v1
§6.2) and `purpose`/`region` classification (categorical arrays). A request may
send a scalar (must be a member) or an array (every element must be a member).

## Capability Catalog

| Capability | Summary |
|------|------|
| `read:dataset` | Read rows from an allowlisted dataset |
| `export` | Export an allowlisted dataset slice |
| `join` | Join allowlisted datasets |
| `train:on` | Train a model on an allowlisted dataset |
| `delete:subject` | Delete a data subject's records |

## Detailed Capability Semantics

### `read:dataset`
- **summary**: Query a dataset within column allowlist, row bound, and
  purpose/region scope.
- **usage**: Analytical reads with declared purpose and allowed regions.
- **when_not**: Not granted without a bounded scope; constrain
  dataset/columns/purpose/region.
- **examples**: `dataset=[public-health], rows=10000, purpose=[research], region=[cn]`
- **parameters**:
  - `dataset` (array, enum `public-health`/`sales-aggregate`/`transport-ops`).
  - `columns` (array, allowlist).
  - `rows` (number, **upper bound**, maximum 100000).
  - `purpose` (array, enum `research`/`operational`/`erasure`/`training`).
  - `region` (array, enum `cn`/`eu`/`us`/`global`).
- **domain types**: `dataset`/`columns`/`purpose`/`region` = sets;
  `rows` = scalar upper bound.

### `export`
- **summary**: Materialize a bounded, scoped export of a dataset.
- **usage**: Deliverables; data sharing with a declared purpose.
- **when_not**: Never granted without purpose/region declaration; row bound
  required.
- **parameters**: `dataset` (array, enum), `columns` (array), `rows`
  (upper bound, 50000), `purpose` (array, enum), `region` (array, enum).

### `join`
- **summary**: Combine datasets whose allowlists overlap the join scope.
- **usage**: Cross-dataset analytics for a declared purpose.
- **when_not**: Joins multiply exposure — grant only when the join column set
  is explicit.
- **parameters**: `dataset` (array, enum), `columns` (array), `purpose`
  (array, enum), `region` (array, enum).

### `train:on`
- **summary**: Use allowed datasets for model training runs.
- **usage**: ML training; purpose must be `training`/`research`.
- **when_not**: Never granted on production personal data without explicit
  erasure/purpose controls.
- **parameters**: `dataset` (array, enum), `rows` (upper bound, 100000),
  `purpose` (array, enum), `region` (array, enum).

### `delete:subject`
- **summary**: Erasure request execution scoped to a dataset and declared
  purpose.
- **usage**: Right-to-erasure fulfillment.
- **when_not**: Irreversible — must require audit and normally a separate
  erasure approval.
- **parameters**: `dataset` (array, enum), `purpose` (array, enum), `region`
  (array, enum).

## Constraint Types

Grants against this scheme may carry constraints:

| Constraint | Origin | Scope | In CLC v1 known set? |
|------|------|------|------|
| `op:audit:required` | `varwof/constraint-v1` | mandatory audit trail | **no** → fail-closed |
| `data:purpose:<v>` | this scheme (§ extension point) | purpose limitation | **no** → fail-closed |
| `data:region:<v>` | this scheme (§ extension point) | data residency / cross-border | **no** → fail-closed |

Unknown constraint types yield `deny("unknown_constraint")` (fail-closed,
CLC-v1 §8). The `data:purpose:<v>` / `data:region:<v>` **constraint-triple**
form is a **classification constraint**, not a numeric bound; CLC v1 does not
evaluate it, so it must not be granted to a v1-only validator. In v1 the
supported way to express these dimensions is the **classification params**
(`purpose`/`region` arrays), which the reference implementations do evaluate.
The constraint-triple form is recorded as a **CLC v2 requirement** (design-
notes §18).

## Disclaimer

This authorization layer defines the **operation boundary** for an AI agent
accessing data. It is **not a privacy compliance certification**: purpose
limitation, retention, consent and cross-border transfer obligations remain
with the data controller.