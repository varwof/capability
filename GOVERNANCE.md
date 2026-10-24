<!--
SPDX-FileCopyrightText: 2026 Jijie Wei and CLC contributors
SPDX-License-Identifier: Apache-2.0
-->

# CLC Governance

Status: initial public governance, effective 2026-10-24.

This document governs the CLC specification, conformance corpora, reference
material and supporting tooling in this repository. It does not claim that CLC
is an IETF Working Group item or that any external organization has endorsed it.

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

### Core semantic changes

A change to CLC syntax, a relation, a verdict, a reason-code ordering, a
conformance obligation or a claimed conformance class requires:

1. a public issue describing the problem and alternatives;
2. a pull request containing the normative text and executable evidence;
3. a review period of at least 14 calendar days;
4. an impact statement for existing implementations and corpora; and
5. resolution of every unresolved technical objection.

Until there are at least two active maintainers, the editor may merge after the
review period but must record why consensus was judged sufficient. The editor
MUST NOT use that fallback to bypass CI or an unresolved technical objection.

### Bootstrap exception

The repository must not be unable to adopt its own review process because no
second reviewer exists yet. The initial editor may therefore merge a
documentation-only governance, adoption or contribution-policy PR without an
approving review when all of the following hold:

- required CI and DCO checks pass;
- the PR states that the bootstrap exception is being used;
- no unresolved technical objection is present;
- the change does not modify CLC semantics, conformance claims, vectors,
  security behavior or release artifacts; and
- the exception is recorded in the pull request history.

This exception ends when another maintainer or an external reviewer is
available. It MUST NOT be reused for routine technical changes.

### Security fixes

Security fixes may use a private review period when public disclosure would
create immediate risk. The technical rationale and regression vectors MUST be
published after coordinated disclosure unless doing so would reveal secrets or
personal data.

### Bindings

A binding is governed by its binding maintainer. Core maintainers review only:

- whether it preserves the declared core boundary;
- whether its conformance claims are accurate; and
- whether it improperly introduces carrier semantics into the core.

## Maintainer selection

Maintainer candidates are evaluated on sustained, constructive contributions,
including specification text, vectors, implementation reports, security review
or binding maintenance.

Appointment requires:

- consent of the candidate;
- consensus of current maintainers; and
- a public contribution record.

The target is at least three maintainers from at least two organizations before
change control is transferred. Maintainers who are inactive for 12 months may
move to emeritus status after public notice.

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
- at least two independent implementations pass the applicable public corpora;
- at least two external bindings or adoption statements exist;
- security and IPR reviews are complete; and
- repository, publication, trademark and succession arrangements are agreed.

Until then, the project remains community-open but explicitly initiated and
edited by its initial editor.

## Amendments

Changes to this document follow the normal public PR process. A future neutral
governing body may replace this document in whole when change control is
transferred.
