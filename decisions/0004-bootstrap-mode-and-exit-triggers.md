<!--
SPDX-FileCopyrightText: 2026 Jijie Wei and CLC contributors
SPDX-License-Identifier: Apache-2.0
-->

# 0004 — Operating modes and exit from `bootstrap`

- **Status:** accepted
- **Date:** 2026-10-31
- **Governance:** Revision 2 (records 0003 onward, published together)
- **Bootstrap:** yes — one maintainer was active when this was decided

## Decision

`GOVERNANCE.md` names the mode it is operating in at the top of the document —
currently `bootstrap`, meaning exactly one maintainer — and describes the three
modes: `bootstrap`, `shared`,
`transfer`.

A rule that presumes more than one participant carries a bracketed tag naming
its trigger and is dormant until that trigger is reached. Five triggers are
recorded: a second maintainer appointed; a second independent
implementation in `conformance/registry.md`; two external bindings or adoption
statements; an organization repository; and a review date of 2027-04-30, at
which every dormant rule is activated, rewritten or deleted.

In `bootstrap` mode the project does not claim P12 and says so where the
single-implementation state is relevant, while stating that the absence of that
claim restricts no one.

The reviewer-permission sentence is qualified for the same reason: `triage`
exists only in an organization repository.

## Alternatives

- **Write only the rules that one person can exercise today.** Rejected: a second
  implementer arriving tomorrow should find the rules that will apply to them
  already written. A process improvised after the second participant appears
  looks like it was tailored to the incumbent, whether or not it was.
- **Write every rule as if it were in force.** Rejected: this is the failure the
  project already has. The ruleset requires one approving review, one maintainer
  cannot supply it, and merges therefore use an admin bypass that the governance
  document did not describe. An obligation nobody can exercise teaches
  participants to bypass, and the bypass then becomes normal.
- **Delete the people-dependent rules until there are people.** Rejected:
  deletion removes the fairness signal and is the actual self-limitation. Tagging
  costs one line per rule and keeps the promise visible.
- **Set a deadline for finding a second independent implementation.** Rejected:
  governance cannot manufacture an independent implementer. A deadline would
  convert a factual state into a project failure and would invite a second
  implementation produced for the deadline rather than for use.
- **Review every dormant rule on a fixed calendar instead of one date.**
  Rejected for now: one date with an explicit outcome (activate, rewrite, delete)
  is easier to keep than a recurring obligation with no owner.

## Objections

None raised. The review date was set six months out because it is long enough for
a second implementation to appear through ordinary work and short enough that
dormant rules do not survive a year of nobody reading them.

## Binds

- `GOVERNANCE.md` — `Operating mode` line, `Operating modes`, and the
  `[bootstrap]` / `[activates: ...]` tags in `Core semantic changes`,
  `Maintainer selection`, `Conformance review` and `Reviewer authority`
- `decisions/README.md` — index
- Review date 2027-04-30
- Decision 0003, which supplies the review windows and the record format this
  decision is written in
