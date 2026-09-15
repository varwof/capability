# Reproduce

Two probe sets, three languages, one shared case file each. Both entry points are the
**decision** functions (`semantics.Authorize`, `authorize_set`, `authorizeSet`) — not
`entails()`, which only covers the grant/operation relation and would report constraint
evaluation as absent.

## Case files

- `probes.json` — 18 value-level pairs (`evaluated` vs `applied` raw text). Each case yields,
  per language, the raw-path result on both sides and the canonical bytes, so a caller can see
  whether the two inputs are the same value.
- `decisions.json` — 12 decision-level cases (`grant` vs `op`), covering the axes that need the
  decision function (null/absent, empty bound, array order and duplicates, added member,
  unrecognised constraint, wildcard-shaped id).

## Commands

```bash
# Python (Go and TypeScript implementations live in siblings of this repository)
python3 reproduce/probe.py   ../aic-capability-demo          reproduce/probes.json
python3 reproduce/decide.py  ../aic-capability-demo          reproduce/decisions.json

# TypeScript
npx tsx reproduce/probe.ts   ../aic-capability-demo/ts       reproduce/probes.json
npx tsx reproduce/decide.ts  ../aic-capability-demo/ts       reproduce/decisions.json

# Go — run from the register checkout so the module resolves
(cd ../register && go run ../capability/docs/contributions/coaz-semantically-unchanged/reproduce/probe.go \
   ../capability/docs/contributions/coaz-semantically-unchanged/reproduce/probes.json)
(cd ../register && go run ../capability/docs/contributions/coaz-semantically-unchanged/reproduce/decide.go \
   ../capability/docs/contributions/coaz-semantically-unchanged/reproduce/decisions.json)
```

To compare against a fixed revision rather than a working tree, create a detached worktree for
each implementation repository at the commit recorded in `../divergence-report.md` and point the
commands at that path.

## Reading the output

`raw_eval` / `raw_app` are the raw-text path results (`ok` or the leading reason code);
`canon_eval` / `canon_app` are the canonical bytes; `same` is whether the two are the same value.
A divergence to report is any of:

1. two languages disagreeing on verdict, reason code or canonical bytes for the same case;
2. one implementation's raw path and decoded path disagreeing;
3. a result that is not stable across runs (uncaught exception, panic, timeout).
