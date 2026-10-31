<!--
SPDX-FileCopyrightText: 2026 Jijie Wei and CLC contributors
SPDX-License-Identifier: Apache-2.0
-->

# Decision records

`GOVERNANCE.md` requires a decision record for a change to normative text, a
conformance obligation, the maintainer or reviewer roster, repository
permissions, or the governance document itself. This directory holds them.

A record is evidence of why a rule exists. It is not a vote log and creates no
authority.

## Naming

`NNNN-slug.md`, numbered in order of the decision rather than the merge date. A
record is written once and not rewritten; a decision that reverses an earlier
one gets its own record, and the earlier one is marked `superseded by NNNN`.

## Required fields

| Field | Content |
|---|---|
| Status | `accepted`, `superseded by NNNN`, or `withdrawn` |
| Date | the date the decision was taken |
| Governance | the `Revision` of `GOVERNANCE.md` in force when it was taken |
| Decision | what is now the rule, in one or two sentences |
| Alternatives | what was rejected, and why |
| Objections | substantive objections and how each was resolved, or `none raised` |
| Binds | clauses, corpora, registry rows, commits or pull requests |
| Bootstrap | present only while one maintainer is active |

An objection is quoted rather than characterised. "Nobody objected" and "the
objection was answered by the pinned pin check" are different facts, and a
later reader needs to be able to tell which one happened.

## Index

| ID | Decision | Date | Status |
|---|---|---|---|
| [0001](0001-reviewer-scopes-and-restricted-write.md) | Reviewer appointment held as three separate scopes; restricted write in place of triage | 2026-10-31 | accepted |
| [0002](0002-ccx-046-scope-and-spec-clause.md) | `ccx-046` scope fields, execution checks moved to `derivation`, `spec_clause` prefixes aligned | 2026-10-31 | accepted |
| [0003](0003-governance-revision-2.md) | Objection windows, decision records, governance revision numbering | 2026-10-31 | accepted |
| [0004](0004-bootstrap-mode-and-exit-triggers.md) | Operating modes, dormant-rule tags, exit triggers from `bootstrap` | 2026-10-31 | accepted |
| [0005](0005-merge-path-and-measurable-criteria.md) | Single-maintainer merge path, editorial path, measurable transfer criteria, term expiry | 2026-10-31 | accepted |
