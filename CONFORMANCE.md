<!--
SPDX-FileCopyrightText: 2026 Jijie Wei and CLC contributors
SPDX-License-Identifier: Apache-2.0
-->

# CLC Conformance Review

Status: initial public procedure, effective 2026-10-27.

This document defines how a conformance claim is verified and recorded. It
implements the review role described in `GOVERNANCE.md` and the conformance
classes in the core specification §12. It does not create new semantics.

## 1. What a claim is

A claim is a statement that a specific implementation, at a specific commit,
passes a specific corpus for a specific class and language revision.

A claim is not: a repository description, a README heading, part of an email
thread, or agreement between implementations that share an author.

| Field | Required content |
|---|---|
| Implementation | repository URL and implementation commit |
| Class | `CLC-A` or `CLC-D` (CLC-E is not claimed) |
| Language revision | `CLC-<major>.<minor>` the implementation advertises |
| Corpus | repository commit plus SHA-256 for every corpus file used |
| Commands | exact commands, including flags and environment |
| Results | cases passed and failed per corpus |
| Residual gaps | what the implementation does not implement or did not run |
| Reviewer | the person who verified the evidence |

## 2. Class requirements

- **CLC-A**: `vectors.json` (154) and `property-cases.json` (1,184) pass, with
  both verdict and reason code asserted. An implementation advertising
  `CLC-1.19` must also satisfy the §12.1 minor gate: `param_bounds` grammar and
  §6.6 meet, `Resolve`, `ConstraintUnion`, and §6.2 canonicalization.
- **CLC-D**: `containment-vectors.json` (64) and
  `authorize-chain-vectors.json` (15) pass. The crosswalk (45), reason-collapse
  (3), mode-lattice (5) and containment property (784) corpora are required for
  a profile claim, not for the base CLC-D claim.
- **CLC-E**: implemented and pinned by `evidence-vectors.json` (32), but **not
  claimed**. No review records a CLC-E claim until two independent
  implementations exist and the EMILIA joint review is complete.

## 3. Procedure

1. **Submit.** The implementer opens an issue with the fields in §1 and a link
   to a public CI run at the claimed commit. Private runs are not evidence.
2. **Review.** A conformance reviewer whose scope covers the class and whose
   term is current checks the claim against the checklist in §4. The reviewer
   may ask for a rerun but does not edit the implementation.
3. **Record.** The reviewer writes a review note and adds a row to
   `conformance/registry.md`, or rejects the claim with the specific unmet
   item.
4. **Merge.** A maintainer merges the registry change under the normal pull
   request process. The reviewer's note is linked from the row.
5. **Dispute.** A disagreement about the evidence goes to the maintainers. A
   disagreement about the specification goes through the core change process,
   not through the registry.

## 4. Reviewer checklist

- [ ] The implementation commit is public and the claimed files exist at it.
- [ ] Every corpus file matches the recorded commit and SHA-256.
- [ ] The corpus revision matches the language revision claimed.
- [ ] Verdict **and** reason code are asserted, not only
      contained/not-contained.
- [ ] The §8.4 `allow_unresolved` / `unresolved` channel is not dropped.
- [ ] The §12.1 revision gate fails closed on an incompatible input.
- [ ] If `CLC-1.19` is claimed, the §12.1 minor-gate corpora pass.
- [ ] Public CI builds and runs the same commands at the same commit.
- [ ] Independence is stated for this implementation, and same-author parity is
      not presented as independent validation.
- [ ] Residual gaps are listed, including corpora that were not run.

## 5. Independence

§12 P12 applies. An implementation built without reading another implementation
is independent for this purpose. Three implementations by one author are a
regression test, not independent evidence. A reviewer records which of these
the claim is, using the implementer's statement and, where available, the
cleanroom evidence (repository history, leash checks, pinned inputs).

## 6. What a review does not do

- It does not certify security, fitness for a deployment, or interoperability
  beyond the vectors run.
- It does not change the specification, a corpus, a reason code, or a class.
- It does not endorse an organization or a product.
- It does not replace the change process for normative text.

## 7. Registry and withdrawal

The registry is append-only in substance: a superseded claim gets a new row and
the old row is marked `superseded`, with the replacement ID. A claim found to be
wrong is marked `withdrawn` with the reason; rows are not deleted.

Each row records the reviewer's scope and the end of that scope's term as it stood
when the claim was signed, so a reader can tell whether the row is still covered
by an appointed reviewer. A claim signed while the term was current stays
recorded when the term ends; a reviewer whose term has ended cannot sign a new
claim until the appointment is renewed.

## 8. Review notes

A review note is short and evidence-shaped:

```text
implementation, commit
class, revision
corpus commit and hashes
commands
results per corpus
independence statement
residual gaps
reviewer, date
```

It is linked from the registry row and does not restate the specification.
