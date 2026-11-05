<!--
SPDX-FileCopyrightText: 2026 Jijie Wei and CLC contributors
SPDX-License-Identifier: Apache-2.0
-->

# 0009 — A claim review is not a code review

- **Status:** accepted
- **Date:** 2026-11-05
- **Governance:** Revision 2 (records 0003 onward, published together)
- **Bootstrap:** yes — one maintainer was active when this was decided
- **External evidence:** none — bootstrap, no second maintainer

## Decision

A review recorded under a conformance reviewer's scope reviews the claim, not the
source: the CI run and the commit it points at, the corpus digests against the
ones the row cites, whether the claim wording stays inside what the corpus
supports, and whether the independence statement is accurate. The implementation
source is outside that review.

If a deeper review of source is ever wanted, it is a decision recorded **before**
the reviewer opens the source, stating what it does to that reviewer's
independence statement for that implementation. Where the reviewer is also an
implementer, the decision is taken after that implementation is pinned and
published, so the order of events stays legible. A source review is not a side
effect of a claim review, and it is not implied by one being requested.

## Context

The reviewer of `reg-2026-002` wrote their own implementation under a statement
that the reference implementation was never read. That statement stops being
checkable the moment a reader cannot tell what was read, and an unstated boundary
is indistinguishable from one that was crossed. Recording the boundary protects
the statement rather than the reviewer.

## Alternatives

- **Let the reviewer decide case by case.** Rejected: the basis of a review is
  what a later reader can check, and a boundary decided privately is not
  checkable.
- **Forbid source review outright.** Rejected: a security or correctness review
  may legitimately need the source later. The condition is that it be decided
  first, recorded, and accompanied by the effect on the independence statement —
  not that it never happens.

## Objections

None raised. The reviewer proposed the boundary in `varwof/capability#14` on
2026-11-04; the editor accepted it there and recorded it here.

## Binds

- `conformance/registry.md` — the notes of `reg-2026-002` record the review under
  this boundary
- `CONFORMANCE.md` §4 — the reviewer checklist is the claim review this record
  describes
