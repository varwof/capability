<!--
SPDX-FileCopyrightText: 2026 Jijie Wei and CLC contributors
SPDX-License-Identifier: Apache-2.0
-->

# CLC Governance

Status: initial public governance, effective 2026-10-24.
Revision: 2, 2026-10-31.
Operating mode: `bootstrap` — one maintainer and no second independent
implementation.

This document governs the CLC specification, conformance corpora, reference
material and supporting tooling in this repository. It does not claim that CLC
is an IETF Working Group item or that any external organization has endorsed it.

## Operating modes

This document describes three modes. One is in force at a time, and the
`Operating mode` line at the top names it.

| Mode | In force when | What it changes |
|---|---|---|
| `bootstrap` | one maintainer, no second independent implementation | the single maintainer does the work, records every decision as `bootstrap`, and needs no second approver |
| `shared` | at least two maintainers | consensus, terms and review rules apply as written |
| `transfer` | the criteria in "Change-control transfer" are met | change control moves to a neutral body |

A rule that presumes more than one participant carries a bracketed tag:
`[bootstrap]` for one that only the single maintainer can exercise, and
`[activates: <trigger>]` for one that waits for a trigger from the table below.
The tag is not an aspiration: it marks the clause as dormant, and a dormant
clause is not cited as if it were in force. This document does not describe
obligations it cannot exercise; when a dormant rule is reached by its trigger it
is either implemented or rewritten, not inherited by default.

| Trigger | Activates |
|---|---|
| second maintainer appointed | maintainer consensus; the review windows become approvals; the `bootstrap` exception and `bootstrap` marks end |
| second independent implementation recorded in `conformance/registry.md` | the P12 independence claim, and the path to claiming a further class |
| two external bindings or adoption statements recorded | maintenance obligations for bindings |
| repository moved to an organization account | `triage`/`maintain` roles and organization-level `CODEOWNERS` |
| review date 2027-04-30 | every dormant rule is activated, rewritten or deleted |

In `bootstrap` mode the project does not claim P12 and says so wherever the
single-implementation state is relevant. The absence of that claim restricts no
one: anyone may implement and deploy CLC, and a claim absent from the registry is
unrecorded, not failed.

The review date reviews this document, not the search for a second
implementation. Dormant rules that no one can exercise on that date are removed
rather than carried forward, because an unexercised obligation decays into a
formality that the next participant has to argue with.

## Goals

- keep the core minimal, deterministic, carrier-neutral and locally decidable;
- make specification changes reviewable, testable and implementable;
- prevent a single implementer, carrier or vendor from owning the core;
- allow carrier bindings to evolve independently without widening the core;
- make it possible to transfer change control to a neutral standards body.

## Roles

### Editor

The editor coordinates releases, publication and the change process. The initial
editor is Jijie Wei. The role is procedural and does not override technical
consensus.

### Maintainer

A maintainer can review and merge changes within the scope recorded in
`MAINTAINERS.md`. Maintainers are expected to follow this document, disclose
conflicts and keep the public test suites runnable.

### Binding Maintainer

A binding maintainer owns a carrier-specific profile or projection. A binding
maintainer does not automatically become a core maintainer, and cannot add
carrier semantics to the core.

### Conformance Reviewer

A conformance reviewer verifies an implementation report against a pinned
corpus revision and records the outcome in the public conformance registry.
The role is evidence review, not specification authorship: a reviewer cannot
change normative text or vectors, create or remove a conformance class, or
rule on two conflicting claims. Those remain maintainer decisions.

A reviewer MUST recuse from any implementation they authored, employ, or
financially depend on. The independence rule of §12 applies to the reviewer's
own statement, not only to the implementation author's.

### Contributor

Anyone who submits an issue, review, vector, implementation report or pull
request is a contributor. Contribution credit is recorded according to the
contribution and the applicable license and IPR process.

## Decisions

### Normal changes

Normal changes use public lazy consensus. A pull request may merge when:

- required CI passes;
- no unresolved technical objection remains;
- the change stays within the documented scope; and
- the PR contains the corresponding tests or vectors.

The review window is 7 calendar days, counted from the later of the pull request
opening and the last change to the proposed content. Silence during the window is
consent. An objection counts only if it is technical, identifies the clause,
vector or artifact it concerns, and states what evidence would resolve it; the
maintainer who merges records how it was resolved.

### Core semantic changes

A change to CLC syntax, a relation, a verdict, a reason-code ordering, a
conformance obligation or a claimed conformance class requires:

1. a public issue describing the problem and alternatives;
2. a pull request containing the normative text and executable evidence;
3. a review period of at least 14 calendar days;
4. an impact statement for existing implementations and corpora; and
5. resolution of every unresolved technical objection.

[bootstrap] While one person holds merge rights, the merge conditions are those
of `Bootstrap exception`; the editor also records why consensus was judged
sufficient. The editor MUST NOT use that fallback to bypass CI or an unresolved
technical objection.

### Decision records

A decision that changes normative text, a conformance obligation, the
maintainer or reviewer roster, repository permissions, or this document is
recorded in `decisions/`, one file per decision, named `NNNN-slug.md`.

A record states the decision, its date, the governance revision it was taken
under, the alternatives rejected, any substantive objection and how it was
resolved, and the artifacts it binds (clauses, corpora, registry rows, pull
requests). The pull request that makes the change links its record, and the
record links back.

A record is not a vote log and creates no authority. It exists so that a later
maintainer can learn why a rule exists without reconstructing a comment thread.
A decision taken while only one maintainer is active is marked `bootstrap` in
the record, and the next appointed maintainer reviews it.

### Bootstrap exception

The repository must not be unable to do its own work because no second person
holds merge rights. While exactly one person does, that person may merge a pull
request without an approving review when all of the following hold:

- required CI and DCO checks pass;
- the review window for that change has elapsed;
- no unresolved technical objection is present;
- where the change needs a conformance review, a decision record or a roster
  entry, that artifact exists and is linked from the pull request; and
- the pull request states that the bootstrap exception is being used.

A direct push to the default branch is the same decision and needs the same
conditions. Where a pull request is possible it is preferred, because the
conditions are then visible to everyone rather than only to the person who
merged.

This exception ends when a second person holds merge rights. An external
conformance reviewer does not end it, because that role does not include
approving specification or corpus changes.

### Editorial changes

A change limited to typography, links, formatting or spelling in non-normative
text may merge once CI passes, without a review window and without invoking the
bootstrap exception, provided it changes no normative statement, no vector
expectation, no reason code, no registry row and no decision record. A change
that touches any of those is a normal change, however small its diff looks.

### Security fixes

Security fixes may use a private review period when public disclosure would
create immediate risk. The security contact named in `SECURITY.md` decides
whether a private period applies, sets its end date and records the decision; the
period is at most 90 days from the report unless a longer one is recorded with a
reason. The technical rationale and regression vectors MUST be published when
the period ends, unless doing so would reveal secrets or personal data.

### Bindings

A binding is governed by its binding maintainer. Core maintainers review only:

- whether it preserves the declared core boundary;
- whether its conformance claims are accurate; and
- whether it improperly introduces carrier semantics into the core.

## Maintainer selection

Maintainer candidates are evaluated on sustained, constructive contributions,
including specification text, vectors, implementation reports, security review
or binding maintenance.

A maintainer is active while they have merged a change, reviewed one, or taken
part in a recorded decision within the previous 12 months.

Appointment requires:

- consent of the candidate;
- consensus of current maintainers; and
- a public contribution record.

[bootstrap] While one maintainer is active, an appointment is that maintainer's
decision, recorded in `decisions/`. The consensus line above activates with the
second maintainer.

The target is at least three maintainers from at least two organizations before
change control is transferred. Maintainers who are inactive for 12 months may
move to emeritus status after public notice.

## Conformance review

Conformance claims are recorded, not remembered. Every claim names the
implementation, the conformance class, the language revision, the corpus commit
and file hashes, the exact commands, the results and the reviewer.
`CONFORMANCE.md` defines the procedure and the checklist; verified claims are
listed in `conformance/registry.md`.

Appointment as a conformance reviewer requires:

- a public contribution record in the relevant class or corpus;
- consent of the candidate and consensus of current maintainers;
- disclosure of material implementation, employment or commercial interests;
- for each review, a short independence statement covering that implementation.

[bootstrap] While one maintainer is active, the appointment is recorded in
`decisions/` and is re-checked by the next maintainer appointed.

Reviewers serve 12-month terms and may be renewed. The end date of each scope's
term is recorded in `MAINTAINERS.md`; a row whose term has ended is marked
`expired` until it is renewed, and the claims recorded under it are not
withdrawn by the expiry. A reviewer inactive for 12 months may move to emeritus
after public notice, on the same terms as a maintainer.

Until the first conformance reviewer is appointed, the editor may perform the
review and MUST mark the registry row as a bootstrap review. The bootstrap mark
is removed when an appointed reviewer re-checks the claim. A reviewer who
authored, employs or depends on the implementation cannot clear that mark;
clearing it requires a second appointed reviewer whose scope covers the class.
Until then the row stays `bootstrap` and is cited as a bootstrap review wherever
it is used as evidence.

Reviewers do not decide:

- changes to normative text, vectors or reason codes;
- the creation or removal of a conformance class;
- conflicting claims about the same implementation;
- security errata, IPR, trademark or change-control transfer.

Those escalate to the maintainers under the normal change process.

### Reviewer authority

The reviewer's authority is evidential, not editorial. A claim enters
`conformance/registry.md` only with a review note signed by a reviewer whose
scope covers the class.

A reviewer may:

- accept, reject or return a claim for a rerun;
- require the corpus commit and file hashes to be stated;
- record residual gaps and scope limits in the registry row;
- ask for the commands and results to be reproduced at the same commit.

A reviewer may not:

- edit normative text, vectors, reason codes or schemas;
- merge a change to `docs/`, `data/`, `scripts/`, `tools/` or `decisions/`;
- approve an implementation they authored, employ or depend on;
- create, remove or reclassify a conformance class.

Repository permissions implement this boundary; they do not replace it.
[activates: organization repository] A reviewer may hold `triage`; where the
repository sits on a personal account, that role does not exist and the grant is
`write` limited in practice by `CODEOWNERS` and branch protection to
`conformance/` and `CONFORMANCE.md`. A reviewer does not receive merge rights
over the specification or the corpora, and does not become a maintainer by
accepting the review role.

The registry row is the authority: if the row is absent or unsigned, the claim
is not recorded, whatever a README says.

## Conflicts of interest

Maintainers and editors MUST disclose material employment, commercial,
patent-licensing or implementation interests relevant to a decision. Disclosure
does not disqualify participation, but an undisclosed conflict violates this
policy.

No organization receives a privileged extension point. Core changes proposed for
one product or deployment belong in a scheme or binding unless they satisfy the
same generality and evidence requirements as every other core rule.

## Release process

A release MUST record:

- the language revision and conformance classes claimed;
- the corpus revision and result;
- implementation status;
- known gaps and residual risks; and
- the exact commit used to build publication artifacts.

CLC's own P12 rule applies: agreement between implementations that share an
author is regression evidence, not independent validation.

## Change-control transfer

The initiator intends to transfer change control to an IETF Working Group or a
neutral standards organization when:

- there are at least three maintainers from at least two organizations;
- at least two implementations recorded in `conformance/registry.md` pass the
  applicable public corpora, each with a reviewer whose scope covers the class,
  and neither depends on the other under the independence rule of
  `CONFORMANCE.md` §5;
- at least two external bindings or adoption statements are registered in
  `BINDINGS.md`;
- the security and IPR reviews this document requires are complete and recorded
  in `decisions/`; and
- repository, publication, trademark and succession arrangements are agreed.

Until then, the project remains community-open but explicitly initiated and
edited by its initial editor.

## Amendments

Changes to this document follow the normal public PR process, but use the
14-day window of "Core semantic changes" rather than the 7-day window: the
process that governs every other change should not be the easiest thing to
change. Each amendment increments the `Revision` line at the top of this
document and is recorded in `decisions/`.

A future neutral governing body may replace this document in whole when change
control is transferred.
