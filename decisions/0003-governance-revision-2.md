<!--
SPDX-FileCopyrightText: 2026 Jijie Wei and CLC contributors
SPDX-License-Identifier: Apache-2.0
-->

# 0003 — Governance revision 2: windows, decision records, revision numbering

- **Status:** accepted
- **Date:** 2026-10-31
- **Governance:** Revision 1, effective 2026-10-24; this record produces
  Revision 2
- **Bootstrap:** yes — one maintainer was active when this was decided

## Decision

`GOVERNANCE.md` gains four things and clarifies one:

1. A 7-day review window for normal changes, counted from the later of the pull
   request opening and the last change to the proposed content. Silence is
   consent. An objection counts only if it is technical, names the clause,
   vector or artifact, and states what evidence would resolve it.
2. A `Decision records` section: rule, roster, permission and governance changes
   are recorded in `decisions/`, with the fields listed in `decisions/README.md`.
3. A `Revision` number for the governance document itself, incremented by every
   amendment.
4. Amendment of this document uses the 14-day core window, not the 7-day window.
5. The conformance-review bootstrap rule now states that a reviewer who authored
   or depends on an implementation cannot clear a bootstrap mark, so clearing it
   needs a second appointed reviewer whose scope covers the class.

No normative CLC text, vector or conformance obligation changes.

## Alternatives

- **Leave "lazy consensus" without a window.** Rejected: a rule whose objection
  period has no duration cannot be audited, and two people reading the same
  paragraph reach different answers about when a change is ripe.
- **One 14-day window for everything.** Rejected: it prices a typo fix like a
  semantic change, which pushes contributors to batch unrelated edits into one
  pull request — the opposite of what the change rules are for.
- **A vote as the fallback when consensus fails.** Rejected: with one or two
  maintainers a vote adds ceremony without adding information, and it invites
  faction counting where the disagreement is usually a missing vector.
- **Record decisions in pull request descriptions only.** Rejected: pull request
  text is editable by the author, is not indexed, and disappears from view once
  the branch is deleted.
- **Version the governance revision together with `CLCRevision`.** Rejected:
  governance and the language revision change on different clocks, and tying
  them would imply that a governance edit touches the specification.

## Objections

None raised. The 7-day window was chosen over 3 days because the project has
contributors in several time zones and, so far, no traffic that requires a
same-day merge; that trade-off is recorded here so a later maintainer can revisit
it without re-deriving the reason.

This amendment was itself adopted under Revision 1, whose text applies ordinary
public review to amendments and sets no fixed window; the 14-day amendment
window it introduces applies to amendments made from Revision 2 onwards. The
record states this so that the shorter adoption of Revision 2 is not later read
as a precedent for amending quickly.

## Binds

- `GOVERNANCE.md` — `Revision: 2`; `Decisions`, `Decision records`,
  `Conformance review`, `Amendments`
- `decisions/README.md`
- `.github/PULL_REQUEST_TEMPLATE.md` — evidence field for a decision record
- `ADOPTION.md` — `Implementations`, which states the licensing and ownership
  position these rules assume
