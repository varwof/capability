<!--
SPDX-FileCopyrightText: 2026 Jijie Wei and CLC contributors
SPDX-License-Identifier: Apache-2.0
-->

# Contributing to CLC

## Before opening a pull request

Open an issue for changes involving:

- syntax, relations, verdicts, reason codes or conformance classes;
- new parameter domains or constraint semantics;
- changes to existing vectors;
- a new carrier binding or evidence projection;
- a claim of independent implementation or conformance.

A change limited to typography, links, formatting or spelling in non-normative
text may go directly to a pull request and merges on CI alone. Anything that
touches a normative statement, a vector expectation, a reason code, a registry row
or a decision record is a normal change however small its diff looks; see
`GOVERNANCE.md` "Editorial changes".

## Licensing and sign-off

Contributions are accepted under Apache-2.0, inbound=outbound. No separate CLA
is required.

Every commit in a pull request MUST include a Developer Certificate of Origin
sign-off:

```text
Signed-off-by: Full Name <email@example.org>
```

The sign-off certifies that you have the right to submit the contribution under
the repository license. See https://developercertificate.org/.

Text intended for an Internet-Draft may also be subject to the IETF Note Well,
BCP 78 and BCP 79. By contributing such text, you agree to the applicable IETF
contribution rules.

## What a change needs

### Normative language changes

A proposal must include:

- the problem and rejected alternatives;
- the exact normative clauses;
- positive and negative vectors;
- reason-code and error-ordering analysis;
- compatibility impact for existing inputs;
- an implementation-impact statement; and
- a public review period under `GOVERNANCE.md`.

### Carrier bindings or projections

A binding must state:

- the native artifact and revision it consumes;
- native verification and trust responsibilities;
- observation, fact, requirement and result mapping;
- occurrence handling;
- information the projection cannot express and who enforces it;
- reproducibility data and positive/negative cases; and
- whether it is normative, experimental or informational.

Registered bindings are listed in `BINDINGS.md`; registration reviews the core
boundary and the cases, and does not transfer ownership.

### New vectors

Vectors must be deterministic, minimal and independently derivable from the
specification. Include the expected outcome and the rationale for any ordering
or precedence decision.

### Implementations

An implementation report must state:

- author or organization independence;
- language and repository;
- implemented CLC revision and conformance class;
- exact runner command;
- pass/fail results by corpus; and
- known unsupported or divergent cases.

Do not describe implementations sharing an author as independent.

## Pull request checks

Before submission:

```sh
python3 scripts/check-offline-vectors.py
python3 scripts/check-bilingual.py
```

Run every corpus-specific checker changed by the proposal. A pull request must
not reduce test coverage or suppress a failing case without a normative
explanation.

## AI assistance

AI tools may be used. The human contributor remains responsible for every
statement, test and license representation. Substantial AI-generated text
should be reviewed and disclosed in the pull request description.

## Conduct

Technical criticism must target claims, text and evidence. Harassment,
discrimination, disclosure of private information and sustained disruptive
posting are not acceptable.

## Security reports

Do not open a public issue for a vulnerability. Follow `SECURITY.md`.
