<!--
SPDX-FileCopyrightText: 2026 Jijie Wei and CLC contributors
SPDX-License-Identifier: Apache-2.0
-->

# 0005 — Single-maintainer merge path and measurable criteria

- **Status:** accepted
- **Date:** 2026-10-31
- **Governance:** Revision 2; records 0003, 0004 and 0005 form that revision and
  are published together
- **Bootstrap:** yes — one maintainer was active when this was decided

## Decision

Five changes, all closing the gap between what the document says and what the
project can check.

1. The bootstrap exception applies to any pull request, not only documentation
   ones, once the review window has elapsed and the artifacts the change needs
   exist. A direct push to the default branch is the same decision and needs the
   same conditions.
2. A separate editorial path: typography, links, formatting and spelling in
   non-normative text merge on CI alone, provided they change no normative
   statement, vector expectation, reason code, registry row or decision record.
3. "Active maintainer" is defined: merged, reviewed or recorded a decision within
   12 months.
4. Change-control transfer now names its evidence: implementations recorded in
   `conformance/registry.md` with a reviewer whose scope covers the class and an
   independence statement under `CONFORMANCE.md` §5; bindings registered in
   `BINDINGS.md`; security and IPR review outcomes recorded in `decisions/`.
5. Reviewer scopes carry a term end date in `MAINTAINERS.md`, a row past that date
   is marked `expired`, and expiry does not withdraw claims already recorded.
   `decisions/` is added to the paths a reviewer may not merge. The security
   private period gets an owner (the contact named in `SECURITY.md`), a default
   ceiling of 90 days and a recorded decision.

## Alternatives

- **Keep the exception documentation-only and merge technical PRs by admin
  bypass.** Rejected: that is what the project does today, and an undocumented
  bypass is indistinguishable from an absent process.
- **Require the full window even for the exception.** Rejected: with one
  maintainer the window is the only outside review available, so waiving it would
  make the exception the weakest path in the document rather than a disciplined
  one.
- **No editorial path.** Rejected: it prices a dead link at seven days, and the
  predictable result is that people bundle typography into substantive changes or
  push directly.
- **Leave transfer criteria qualitative.** Rejected: "security and IPR reviews are
  complete" cannot be checked by anyone outside the project; a record can.
- **Let a reviewer's term lapse silently.** Rejected: an expiry that changes
  nothing is worse than no term, because it implies oversight that is not
  happening.
- **Set the private security period by taste per incident.** Rejected: the person
  deciding when to disclose should not also be the person choosing the deadline
  without a recorded ceiling.

## Objections

None raised. The 90-day ceiling is the common disclosure norm and is explicitly
overridable with a recorded reason, because a coordinated fix can legitimately
take longer than the default.

## Binds

- `GOVERNANCE.md` — `Bootstrap exception`, `Editorial changes`,
  `Maintainer selection`, `Conformance review`, `Reviewer authority`,
  `Security fixes`, `Change-control transfer`
- `MAINTAINERS.md` — `Term ends` column
- `SECURITY.md` — supported versions
- `BINDINGS.md` — new; `CONTRIBUTING.md` link to it
- `decisions/README.md` — index
