# Issue draft (NOT SENT): COAZ "input values semantically unchanged" — which values, compared how?

Status: draft for review. Not posted anywhere.

## The question

COAZ requires a PEP to check, before applying a permit, that "the method, selected mapping and input
values are **semantically unchanged** from what was evaluated". That reads as a requirement, but the
comparison itself — what is compared, and which readings count as unchanged — is not defined. The
notes below list only the points the current text does not settle, with a proposed reading for each.
They are written to be executable, and each is backed by a language-independent vector.

## The invariant as written

From the thread (Alex Olivier, 2026-09-15):

> "The PEP now has to apply every rewrite it knows about before evaluating, and before applying a
> permit it has to check that the method, selected mapping and input values are **semantically
> unchanged** from what was evaluated. If they changed, re-evaluate or refuse, never apply the old
> permit. … Lifting that invariant into the framework so every future binding gets it is still to do."

## Points the text does not settle

1. **Boundary of "rewrites it knows about".** The set is not defined, and the behaviour on an
   unrecognised rewrite is not stated (fail-open or fail-closed).
2. **What "method" is compared against** — the method name alone, or the name together with the
   mapping revision that produced it?
3. **"Selected mapping": identity or revision.** Nothing says whether a mapping comparison is by
   identity or by content, nor what happens if the registry changed between evaluation and forwarding.
4. **The comparison basis.** Raw JSON-RPC bytes, a canonical form, a digest, or the projected
   authorization request object? Without a fixed basis the property cannot be evaluated.
5. **Number equality.** `1`, `1.0`, `1e0`; precision; non-finite values.
6. **Over-limit inputs.** If a rewrite pushes a value past a serialized-size or depth limit, which
   layer refuses and with what reason?
7. **Failure semantics.** The text allows "re-evaluate **or** refuse" without saying how to choose,
   and does not name a reason code or say who can observe the outcome.
8. **Atomicity of check and use.** "Before applying a permit" — which boundary is atomic, and what
   happens if the input is modified concurrently?
9. **"Never apply the old permit."** A permit has no identity today; nothing defines what makes a
   permit "old", or what binds it to the input it was evaluated against.
10. **Unrecognised assertions or rewrite types.** Refuse, or continue with the understood part?
    Silently dropping a conjunct is the classic failure mode here.

## Proposed wording (for discussion, not a claim about the current text)

- Member order: "Member order is not semantic: an input whose members are reordered is unchanged."
- Duplicate members: "An input containing a duplicate member name MUST be treated as changed and
  refused; the comparison basis MUST retain the original member sequence, since decoding MAY drop
  duplicates."
- Strings: "String comparison is exact after canonical serialization: no Unicode normalization and no
  case folding is applied unless the selected mapping revision declares it as a rewrite."
- Numbers: "Numbers are compared in their canonical JSON form (RFC 8785 §3.2.2.3); values with no
  finite canonical form MUST be refused."
- Absent / null / empty: "Absent, null and empty are three different inputs. An absent member MUST NOT
  be treated as null, and null MUST NOT be treated as an absent member."
- Types: "Input values MUST be compared without type coercion: a number and a string that render alike
  are different values, and booleans are never numbers."
- Arrays: "Unless the selected mapping revision declares an array-valued member as a set, array order
  and duplicate elements are significant."
- Added members: "An added member is a change of the input even when the policy ignores it; if a
  binding intends to ignore members, it MUST declare the compared member set explicitly."
- Unrecognised types: "A PEP MUST refuse when it encounters an assertion or rewrite type it does not
  recognise; dropping an unrecognised conjunct is a change of the evaluated input."
- Comparison basis: "The comparison basis is the authorization request object produced by the selected
  mapping revision; the projection MUST be deterministic, and a change to the projection definition is
  itself a change of the basis."

## Vectors

`vectors.json` (28 vectors: value-level pairs and decision-level grant/operation pairs) records, for
each point above, the input pair, the expected relation (`unchanged` / `changed`), the expected PEP
action (`apply` / `reevaluate` / `refuse`) and a reason code where one exists. The readings in the
vectors are proposed, not quoted from the current text.

## Request

If the working group finds the list useful, the natural split is: the framework keeps the invariant,
each binding declares its rewrite set and its projection revision, and the value comparison is
normed once for all bindings. Which of the ten points above can be settled by the framework, and which
belong to each binding?
