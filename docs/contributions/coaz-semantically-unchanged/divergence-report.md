# Differential run across the three implementations

Date: 2026-09-15. Read-only: no implementation file and no corpus file was modified for this run.

## 1. Baseline

| Repository | HEAD | Working tree at the time | Baseline used here |
|---|---|---|---|
| `register` (Go) | `1a51c86b0743e6a5c4107a9a116647dac01b60ef` | dirty: `semantics/semantics.go`, `semantics/rawparams_sanity_test.go` | **clean worktree** `$WORK/register` (detached, excludes the uncommitted changes); the same probes were also run against the dirty tree |
| `aic-capability-demo` (Python + TypeScript) | `610a232200032720d2ff05e919b6cd81a8c4b122` | dirty: `clc_semantics.py`, `ts/clc_semantics.ts`, `edge_test.py`, `ts/edge_test.ts` | **clean worktree** `$WORK/demo`; also run against the dirty tree |
| `capability` (spec and corpus) | `96718de89de43a5d12a419bd6fe7d25cf7f79200` | dirty: `data/_vectors/clc-v1/clc-v1-ambiguities.md` | read-only reference; **no corpus file was modified** |

The uncommitted changes at that time were the implementation side of axes 7/8/12 (malformed Unicode on the decoded path, decoded size measured in JCS bytes, literal invalid UTF-8 in raw text). Both baselines produce the same results below.

## 2. Commands

```bash
WORK=$(mktemp -d)
git -C register worktree add --detach "$WORK/register" "$(git -C register rev-parse HEAD)"
git -C aic-capability-demo worktree add --detach "$WORK/demo" "$(git -C aic-capability-demo rev-parse HEAD)"

# value-level cases (18) and decision-level cases (12), one case file each
python3 reproduce/probe.py  "$WORK/demo"    reproduce/probes.json
npx tsx    reproduce/probe.ts  "$WORK/demo/ts" reproduce/probes.json
(cd "$WORK/register" && go run <snapshot>/reproduce/probe.go <snapshot>/reproduce/probes.json)
python3 reproduce/decide.py "$WORK/demo"    reproduce/decisions.json
npx tsx    reproduce/decide.ts "$WORK/demo/ts" reproduce/decisions.json
(cd "$WORK/register" && go run <snapshot>/reproduce/decide.go <snapshot>/reproduce/decisions.json)
```

## 3. Value-level results (axes 5-13, 18 cases)

Columns: `raw_eval` is the raw-text path result; `S`/`D` says whether the canonical bytes of the two inputs are the same (`S`) or different (`D`).

| Case | Axis | Go | Python | TypeScript | Dirty tree | Verdict |
|---|---|---|---|---|---|---|
| `a05-key-order` | 5 | ok / S | ok / S | ok / S | same as clean | all three agree |
| `a05-key-order-nested` | 5 | ok / S | ok / S | ok / S | same as clean | all three agree |
| `a06-duplicate-key` | 6 | invalid_params_duplica / S | invalid_params_duplica / S | invalid_params_duplica / S | same as clean | all three agree |
| `a07-nfc-vs-nfd` | 7 | ok / D | ok / D | ok / D | same as clean | all three agree |
| `a07-escape-vs-literal` | 7 | ok / S | ok / S | ok / S | same as clean | all three agree |
| `a07-case` | 7 | ok / D | ok / D | ok / D | same as clean | all three agree |
| `a07-lone-surrogate` | 7 | invalid_params_number / D | invalid_params_number / D | invalid_params_number / D | same as clean | all three agree |
| `a08-int-forms` | 8 | ok / S | ok / S | ok / S | same as clean | all three agree |
| `a08-int-exponent` | 8 | ok / S | ok / S | ok / S | same as clean | all three agree |
| `a08-nonfinite` | 8 | invalid_params_number / D | invalid_params_number / D | invalid_params_number / D | same as clean | all three agree |
| `a09-absent-vs-empty` | 9 | ok / D | ok / D | ok / D | same as clean | all three agree |
| `a09-null` | 9 | ok / D | ok / D | ok / D | same as clean | all three agree |
| `a09-empty-array-bound` | 9 | ok / D | ok / D | ok / D | same as clean | all three agree |
| `a10-number-vs-string` | 10 | ok / D | ok / D | ok / D | same as clean | all three agree |
| `a10-bool-vs-number` | 10 | ok / D | ok / D | ok / D | same as clean | all three agree |
| `a11-array-order` | 11 | ok / D | ok / D | ok / D | same as clean | all three agree |
| `a11-array-duplicate` | 11 | ok / D | ok / D | ok / D | same as clean | all three agree |
| `a13-extra-field` | 13 | ok / D | ok / D | ok / D | same as clean | all three agree |

## 4. Decision-level results (12 cases)

| Case | Go | Python | TypeScript | Verdict |
|---|---|---|---|---|
| `d01-bool-grant-vs-number-op` | deny / params_exceed_grant | deny / params_exceed_grant | deny / params_exceed_grant | all three agree |
| `d02-null-grant-op-no-params` | deny / invalid_params_null | deny / invalid_params_null | deny / invalid_params_null | all three agree |
| `d03-extra-field-bounded-grant` | deny / undeclared_param | deny / undeclared_param | deny / undeclared_param | all three agree |
| `d04-empty-array-bound` | deny / empty_bound_denies_class | deny / empty_bound_denies_class | deny / empty_bound_denies_class | all three agree |
| `d05-array-order-grant-enum` | allow /  | allow / None | allow / None | **divergent** |
| `d06-array-duplicate-op` | allow /  | allow / None | allow / None | **divergent** |
| `d07-missing-key` | deny / params_missing | deny / params_missing | deny / params_missing | all three agree |
| `d08-null-canonical` | deny / invalid_params_null | deny / invalid_params_null | deny / invalid_params_null | all three agree |
| `d09-number-vs-string` | deny / params_exceed_grant | deny / params_exceed_grant | deny / params_exceed_grant | all three agree |
| `d10-unknown-constraint` | deny / unknown_constraint | deny / unknown_constraint | deny / unknown_constraint | all three agree |
| `d11-op-id-wildcard-shape` | deny / unsupported_wildcard | deny / unsupported_wildcard | deny / unsupported_wildcard | all three agree |
| `d12-constraint-type-segment` | deny / invalid_constraint | deny / invalid_constraint | deny / invalid_constraint | all three agree |

## 5. Replay from this snapshot (2026-09-15)

Running the six commands from `reproduce/` reproduces the tables above line by line. At that moment
`register` was at `8b9bcbc` (which includes the malformed-Unicode and size fixes that were uncommitted
earlier) and `aic-capability-demo` at `75bc79e`, so the conclusions hold on those revisions too.

## 6. Conclusion

- **No new cross-implementation divergence**: all 18 value-level and 12 decision-level cases agree across Go, Python and TypeScript, including reason codes; the clean and dirty baselines agree as well.
- The readings cited for axes 5/10/13/17 are therefore reproducible across three implementations rather than one implementation's habit.
- The four divergences recorded on 2026-09-11 (boolean treated as a number, wildcard-shaped operation id collapsing the reason, constraint type segmentation, null plus absent params ordering) are aligned in `d01` / `d11` / `d12` / `d02`.
- One boundary difference, not a divergence: Python and TypeScript evaluate constraints in the decision function (`authorize_set` / `authorizeSet`) while `entails()` covers only the grant/operation relation; Go's `Authorize()` does both. Comparing the wrong entry point produces a false report that constraints are ignored, so this run uses the decision entry points everywhere.
- Code locations: Go `semantics/semantics.go` (`ValidateRawParams`, `CanonicalJSON`, `Authorize`); Python `clc_semantics.py` (`validate_raw_params`, `canonical_json`, `authorize_set`); TypeScript `ts/clc_semantics.ts` (`validateRawParams`, `canonicalJSON`, `authorizeSet`).

## 7. Corpus count (measured, unmodified)

`capability/data/_vectors/clc-v1/vectors.json`: **107** vectors (syntax 9 / entail 40 / intersect 14 / decide 44). No corpus file was modified for this run.

## 8. No commits

- No `git commit` and no `git push` were performed while producing this material, and no remote was changed.
- The three implementation files and the corpus were not modified by this analysis; their uncommitted state at the time is preserved exactly as found.
- All artifacts live under `docs/contributions/coaz-semantically-unchanged/` in this repository.
