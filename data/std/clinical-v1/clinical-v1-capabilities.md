# Standard Clinical Information-System Capability Reference

> scheme_id: `std/clinical-v1` · Version `1.0.0` · Vendor `std` / Product `clinical-v1`

Standard semantics for AI-agent operations inside a clinical information
system: record reads, lab/imaging orders, prescribing and infusion
administration, note writing, and de-identified epidemiology queries — each
bounded by dose ceilings, department/ward/drug-class allowlists, and
grant-scoped patient pseudonyms. Categorical identifiers are encoded per
CLC-v1 §6.2 (v1.1): an operation may send a scalar (must be a member) or an
array (every element must be a member); ordered quantities (dose) are scalar
number **upper bounds**.

## Capability Catalog

| Capability | Summary | Risk |
|------|------|------|
| `read:record` | Read a patient clinical record | — |
| `order:lab` | Order a laboratory test | — |
| `order:imaging` | Order an imaging study | — |
| `prescribe:medication` | Prescribe medication within drug-class/dose bounds | **HIGH-RISK** |
| `administer:infusion` | Authorize infusion administration | **HIGH-RISK** |
| `write:note` | Write a clinical note | — |
| `query:epidemiology` | Query de-identified epidemiology data | — |

## Detailed Capability Semantics

### `read:record`
- **summary**: List/read records under a grant-scoped patient pseudonym and
  department.
- **usage**: Clinical summary, medication reconciliation.
- **when_not**: Not granted with broad department sets or real patient
  identifiers.
- **examples**: `patient=P-1001, department=[icu]`
- **parameters**:
  - `patient` (string, required) — grant-scoped **pseudonym/internal ID
    only**; never real identity data.
  - `department` (array, enum: `icu`/`oncology`/`emergency`/`cardiology`/`administrative`).

### `order:lab`
- **summary**: Create a lab order for a grant-scoped patient.
- **usage**: Standard lab panels ordered on behalf of clinical staff.
- **when_not**: Not granted without an explicit department and ward allowlist.
- **parameters**: `patient` (string), `department` (array, enum), `ward`
  (array, enum: `ward-a`/`ward-b`/`ward-c`).

### `order:imaging`
- **summary**: Create an imaging order within department/ward bounds.
- **usage**: Radiology orders by agents under supervision.
- **when_not**: Not granted broad ward coverage; imaging is high-cost.
- **parameters**: `patient` (string), `department` (array, enum), `ward`
  (array, enum).

### `prescribe:medication` (HIGH-RISK)
- **summary**: Create a prescription within drug-class allowlist and dose
  ceiling.
- **usage**: Medication orders; every grant MUST constrain `drug-class` and
  `dose`.
- **when_not**: `narcotic`/`psychotropic` classes must be single-class grants;
  dose must always be bounded; grants should normally carry
  `clinical:quorum:2`.
- **parameters**:
  - `patient` (string, pseudonym).
  - `drug-class` (array, required; enum: `general`/`narcotic`/`psychotropic`).
  - `dose` (number, required; **upper bound**, maximum 1000).
- **domain types**: `drug-class` = set (categorical allowlist); `dose` =
  scalar upper bound.

### `administer:infusion` (HIGH-RISK)
- **summary**: Authorize infusion administration with dose ceiling and
  ward/class bounds.
- **usage**: Infusion start for an in-patient under agent guidance.
- **when_not**: Always requires bounded dose, a single ward, and normally
  `clinical:quorum:2`.
- **parameters**: `patient` (string), `ward` (array, enum), `drug-class`
  (array, enum), `dose` (number, upper bound, maximum 2000).
- **domain types**: `ward`/`drug-class` = sets; `dose` = scalar upper bound.

### `write:note`
- **summary**: Append a structured note to a grant-scoped patient record.
- **usage**: Agent-drafted progress/op notes for review.
- **when_not**: Not granted for unsigned or unaudited note streams.
- **parameters**: `patient` (string), `department` (array, enum).

### `query:epidemiology`
- **summary**: Aggregate queries over de-identified records.
- **usage**: Outbreak trends, quality dashboards.
- **when_not**: Never granted with patient-scoped parameters; only aggregate
  de-identified scopes.
- **parameters**: `department` (array, enum).

## Constraint Types

Grants against this scheme may carry constraints:

| Constraint | Origin | Scope | In CLC v1 known set? |
|------|------|------|------|
| `time:window` | `varwof/constraint-v1` | duty-hours window | **yes** |
| `op:audit:required` | `varwof/constraint-v1` | operation audit trail | **no** → fail-closed |
| `clinical:quorum:2` | this scheme (§ extension point) | dual-person confirmation for high-risk ops | **no** → fail-closed |

An **unknown** constraint type yields `deny("unknown_constraint")`
(fail-closed, CLC-v1 §8) in the reference implementations; it is not silently
ignored. `clinical:quorum:2` is a declared extension type of this scheme and
is expected to become evaluatable in CLC v2 (multi-party/evidence-side
constraint), not in v1.

## Disclaimer

This authorization layer defines the **operation boundary** for an AI agent
inside a clinical information system. It is **not a clinical decision
mechanism**: it does not replace prescription review, medication-management,
or medical-safety regulations, and it does not constitute a medical device or
a clinical functional-safety measure. This scheme carries **no patient
identity information** and applies the minimum-necessary principle to every
parameter.