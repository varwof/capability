<!--
SPDX-FileCopyrightText: 2026 Jijie Wei and CLC contributors
SPDX-License-Identifier: Apache-2.0
-->

# CLC bindings

A binding or projection consumes a carrier's native artifact and maps it into
CLC fields. It is optional and does not change the core: a binding that needs a
new core rule is a core change proposal in disguise.

`CONTRIBUTING.md` lists what a binding must state. This file records which
bindings are registered, who owns each one, and how a registration ends.

## Status values

| Status | Meaning |
|---|---|
| `proposed` | a description and runnable cases exist; the core boundary has not been reviewed |
| `registered` | a maintainer reviewed the core boundary and the cases, and a decision record exists |
| `deprecated` | superseded or unmaintained; kept for reference, not for new deployments |

Registration reviews boundaries and evidence. It endorses no carrier and claims
no interoperability beyond the cases that were run.

## Registered bindings

None yet. A registration is made by a pull request that adds a row and a
`decisions/` record; the record is the artifact, and this table only indexes it.

| Binding | Carrier | Owner | Status | Record |
|---|---|---|---|---|

## Not registered

Absence from the table above is not a judgement. Two things exist today and are
deliberately not listed:

- the vector field `profile` carries `iicp->clc-v1` in the CLC-D crosswalk
  corpora;
- `contrib/` holds probes and experimental projections, whose own status table is
  in `contrib/README.md`. Those are experiments about CLC, not bindings to it.

## Rules

- A binding may define its own authorship, release schedule and IPR process while
  citing the CLC clauses it uses.
- A binding MUST NOT silently add carrier semantics to the core.
- A `registered` binding whose owner becomes unreachable moves to `deprecated`
  after public notice; it does not stay registered by default.
- Registration does not transfer ownership of the binding or of its code.
