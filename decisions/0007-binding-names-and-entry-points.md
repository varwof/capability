<!--
SPDX-FileCopyrightText: 2026 Jijie Wei and CLC contributors
SPDX-License-Identifier: Apache-2.0
-->

# 0007 — Binding names, affected projections, and an English entry point

- **Status:** accepted
- **Date:** 2026-10-31
- **Governance:** Revision 2 (records 0003 onward, published together)
- **Bootstrap:** yes — one maintainer was active when this was decided
- **External evidence:** none — bootstrap, no second maintainer

## Decision

1. A binding name follows `<source>->clc-v<n>` — source identifier, `->clc-v`,
   version of the projection rather than of CLC. First registered use allocates
   the name; a collision is settled by a recorded decision.
2. A proposal that changes normative text lists the bindings or projections it
   affects, by `BINDINGS.md` entry, alongside the affected implementations.
3. `contrib/README.md` opens with an English statement of what the directory is:
   informational or experimental, not cited as evidence, mergeable on CI alone,
   and promotable only through a normal or core change.

## Alternatives

- **Let binding names emerge by convention and disambiguate later.** Rejected: a
  name is what a corpus vector cites, so an ambiguous one is a silent mismatch
  between two projections that both look registered.
- **Allocate names centrally by prefix, by decision each time.** Rejected as the
  default: it turns every projection into an approval and makes the maintainer a
  gatekeeper for work that carries no normative weight. First use plus a recorded
  collision is enough while the number of bindings is small.
- **Ask for affected projections only in the review, not in the proposal.**
  Rejected: the reviewer would have to reconstruct the list from the diff, and
  the authors of those projections are the ones who know.
- **Translate `contrib/README.md` in full.** Rejected for now: duplication
  between two languages that drift is worse than one short English entry point
  pointing at the same rules; a full translation is welcome as a contribution.

## Objections

None raised. The naming rule is deliberately weak — first use allocates — because
a strict registry would gate work that is optional and carrier-owned. It is
strong enough to make a collision visible, which is the failure mode that matters.

## Binds

- `BINDINGS.md` — naming and allocation rules
- `CONTRIBUTING.md` — normative-change checklist
- `contrib/README.md` — English entry point
- Decision 0006, whose `contrib/` lane these rules rely on
