#!/usr/bin/env python3
"""Generate the CLC-D containment property cases (capability-language-core-v1 §13.7).

Deterministic: the case list is enumerated, not sampled, so re-running this
script reproduces the file byte for byte (no PRNG, no clock).

Property under test (CLC-D, "forward closure"):

  for every case (parent P, child C) and every operation o in the shared
  `ops` sample:
    * Contains(P, C) MUST NOT raise (fail-closed: it returns false), and
    * when Contains(P, C) is true and Entails(C, o) is true, Entails(P, o)
      MUST also be true — containment narrows the authorized operation class
      (§4; this is the DECLARED-set consequence that makes a delegation
      boundary sound and the reason the §5 collapse of layer-2 failures into
      child_exceeds_parent is safe).

The operation sample is shared (`ops`) rather than repeated per case, which
keeps the file comparable in size to the CLC-A property corpus.

Usage:
  python3 scripts/gen-contain-property-cases.py [--out data/_vectors/clc-d/containment-property-cases.json]
"""
import argparse
import itertools
import json
import os

IDS = [
    "std/database-v1:query:SELECT",
    "std/database-v1:query:INSERT",
    "std/database-v1:query:*",
    "std/database-v1:admin:DDL",
]

# None = params absent; {} = present-but-empty (== absent, CLC-A rev CLC-1.3)
PARAMS = [
    None,
    {},
    {"limit": 50},
    {"limit": 100},
    {"limit": 50, "offset": 10},
    {"tables": ["a", "b"]},
    {"cfg": {"width": 10}},
]

# Constraints are deliberately absent: they are NOT part of the containment
# relation (they compose by union across a chain, §7 Intersect), so varying
# them would only duplicate cases.  The vectors corpus pins the constraint
# non-participation explicitly.

# Only literal ids appear in an operation id (wildcards never do).
OPS_IDS = [
    "std/database-v1:query:SELECT",
    "std/database-v1:query:INSERT",
    "std/database-v1:admin:DDL",
]
OPS_PARAMS = [
    {},
    {"limit": 5},
    {"limit": 50},
    {"limit": 100},
    {"limit": 150},
    {"limit": 50, "offset": 10},
    {"tables": ["a"]},
    {"tables": ["a", "b"]},
    {"tables": ["z"]},
    {"cfg": {"width": 5}},
    {"cfg": {"width": 10}},
    {"cfg": {"width": 20}},
    {"cfg": {"width": 10, "depth": 3}},
]


def grant(gid, params):
    g = {"id": gid}
    if params is not None:
        g["params"] = json.loads(json.dumps(params))
    return g


def operation(oid, params):
    o = {"id": oid}
    if params is not None:
        o["params"] = json.loads(json.dumps(params))
    return o


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/_vectors/clc-d/containment-property-cases.json")
    args = ap.parse_args()
    here = os.path.dirname(os.path.abspath(__file__))
    out = args.out if os.path.isabs(args.out) else os.path.join(here, "..", args.out)

    grants = [
        grant(gid, params)
        for gid, params in itertools.product(IDS, PARAMS)
    ]
    ops = [operation(oid, params)
           for oid, params in itertools.product(OPS_IDS, OPS_PARAMS)]

    cases = []
    n = 0
    for p, c in itertools.product(grants, grants):
        n += 1
        cases.append({
            "id": "contain-prop-%04d" % n,
            "parent": p,
            "child": c,
        })

    os.makedirs(os.path.dirname(out), exist_ok=True)
    doc = {
        "_meta": {
            "count": len(cases),
            "generator": "capability/scripts/gen-contain-property-cases.py",
            "property": "CLC-D forward closure: Contains(P,C) never raises; and when "
                        "Contains(P,C) is true and Entails(C,o) is true, Entails(P,o) "
                        "is true, for every o in `ops`",
            "spec_clause": "CLC §13.4 (layers 2-4) and §13.3 antisymmetry; "
                           "CLC-v1 §5 Entails side",
            "status": "reference",
            "title": "CLC-D containment forward-closure property cases",
            "ops_count": len(ops),
            "grant_space": len(grants),
        },
        "ops": ops,
        "cases": cases,
    }
    with open(out, "w") as f:
        json.dump(doc, f, indent=1)
        f.write("\n")
    print("wrote %d cases (%d ops) to %s" % (len(cases), len(ops), out))


if __name__ == "__main__":
    main()