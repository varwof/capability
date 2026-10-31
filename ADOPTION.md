<!--
SPDX-FileCopyrightText: 2026 Jijie Wei and CLC contributors
SPDX-License-Identifier: Apache-2.0
-->

# Adopting CLC

## Status

CLC is an experimental, carrier-neutral semantic layer. It is not itself an
Internet Standard and does not require adoption of a particular token,
credential, transport or trust framework.

## Licensing

- Repository code, specification source, conformance vectors and supporting
  documentation are licensed under Apache-2.0.
- Contributions are accepted inbound=outbound under Apache-2.0.
- No separate CLA is required; commits use DCO sign-off.
- Published Internet-Drafts remain subject to BCP 78/79 and IETF Trust rules.

The repository is permissively licensed. It is not public domain, and it is not
accurate to describe it as having no copyright.

## Patent position

To the best of the current maintainer's knowledge, no patent claim owned or
controlled by the current maintainer is necessarily infringed by implementing
the CLC specification. Any such claim that becomes known will be disclosed
through the applicable process.

To the extent the current maintainer owns or controls patent claims necessarily
infringed by a conforming implementation, the maintainer intends to make those
claims available on royalty-free terms.

This statement is not a warranty concerning patents or other rights held by
third parties. Organizations considering deployment should perform their own
legal and patent review.

## Implementations

CLC is meant to be a shared, community-governed semantic layer. Anyone may
implement it, including commercially and including in a product that competes
with the reference implementation, without a separate licence, registration or
permission from this project.

An implementation belongs to its author. This project does not claim ownership
of an implementer's code, does not require a CLA, and does not impose copyright
or patent conditions beyond Apache-2.0 and the patent position above. A
conformance claim changes nothing about ownership; it only records that a
pinned corpus was run at a pinned commit.

New bindings, profiles or semantic additions are best discussed in the open
before they are proposed as corpus or specification changes, so that other
implementers can say early whether the addition belongs in the core, in a
binding, or nowhere.

## Claiming adoption or conformance

An adopter may state:

- which CLC revision it implements;
- which conformance class it claims;
- which public corpus and exact command were run;
- which binding or projection it uses; and
- which requirements remain outside the implementation.

An implementation MUST NOT claim independence merely because it uses a
different programming language. CLC's own P12 test treats implementations with
the same author or controlling organization as non-independent.

Verified claims are recorded in [conformance/registry.md](conformance/registry.md);
the procedure and checklist are in [CONFORMANCE.md](CONFORMANCE.md).

## Current implementation status

| Implementation | Language | CLC revision | Status |
|---|---|---|---|
| `varwof/register` | Go | CLC-1.19 | reference implementation |
| `varwof/aic-capability-demo` | Python | CLC-1.19 | cross-language implementation |
| `varwof/aic-capability-demo/ts` | TypeScript | CLC-1.19 | cross-language implementation |

All three implementations currently share an author. Their agreement is
regression evidence, not satisfaction of the independent-implementation claim.

## Reporting an adoption

Open an implementation-report issue with the exact repository commit, runner
command, corpus revision, result and known limitations. Adoption reporting does
not transfer ownership of the implementation to this project.

## Bindings and projections

Carrier bindings are separate, optional documents. A binding may define its own
authorship, release schedule and IPR process while citing the CLC clauses it
uses. A binding MUST NOT silently add carrier semantics to the CLC core.
