#!/usr/bin/env python3
"""Generate the CLC-v1 intersection property cases (P11).

Deterministic: the case list is enumerated, not sampled, so re-running this
script reproduces the file byte for byte (no PRNG, no clock).

Property under test (B.4 / §7 rules 2, 5, 6):

  for every case
    * Intersect(sources) either denies with a normative reason code, or
    * returns a grant that is covered by *every* source
      (Entails(source, result) is true for each source), and
    * the result does not depend on the order of the sources.

Usage:
  python3 scripts/gen-property-cases.py [--out data/_vectors/clc-v1/property-cases.json]
"""
import argparse
import itertools
import json
import os

IDS = [
    "std/database-v1:query:SELECT",
    "std/database-v1:query:*",
    "std/database-v1:admin:DDL",
    "std/database-v1:query:INSERT",
    "std/database-v1:*",
]

# None = params absent; {} = params present but empty (identity, §6.2.1)
# The nested forms (profile/filters/flags) exercise §7 rule 6 object-path
# intersection: partial multi-key overlap must narrow only on shared keys
# (rev CLC-1.2), and boolean vs numeric on the same key must not merge
# (True == 1 guard parity).
PARAMS = [
    None,
    {},
    {"limit": 50},
    {"limit": 100},
    {"tables": ["a"]},
    {"tables": ["a", "b"]},
    {"tables": []},
    {"tables": ["a"], "limit": 100},
    {"profile": {"role": "admin"}},
    {"profile": {"role": "viewer"}},
    {"filters": {"status": ["active"], "region": "eu"}},
    {"filters": {"status": ["active"]}},
    {"flags": {"admin": True}},
    {"flags": {"admin": 1}},
]


def grant(gid, params):
    g = {"id": gid}
    if params is not None:
        g["params"] = json.loads(json.dumps(params))
    return g


def forms():
    for gid in IDS:
        for params in PARAMS:
            yield grant(gid, params)


def cases():
    out = []
    n = 0

    def add(sources, note):
        nonlocal n
        n += 1
        out.append({
            "id": "prop-%04d" % n,
            "sources": sources,
            "note": note,
        })

    # 1. same-identifier pairs: every unordered pair of param forms, in both
    #    orders, so order independence is exercised on the merge path.
    for gid in IDS:
        for a, b in itertools.combinations(PARAMS, 2):
            add([grant(gid, a), grant(gid, b)], "same id, two param forms")
            add([grant(gid, b), grant(gid, a)], "same id, reversed")
        for a in PARAMS:
            add([grant(gid, a), grant(gid, a)], "same id, identical params")

    # 2. cross-identifier pairs: namespace and path coverage interactions.
    for ia, ib in itertools.combinations(range(len(IDS)), 2):
        for pa in (None, {"limit": 50}, {"tables": ["a"]}):
            for pb in (None, {}, {"tables": ["a", "b"]}):
                add([grant(IDS[ia], pa), grant(IDS[ib], pb)], "cross id")
                add([grant(IDS[ib], pb), grant(IDS[ia], pa)], "cross id, reversed")

    # 3. three-source chains: attenuation must still be covered by every hop.
    for mid in (IDS[0], IDS[1], IDS[3]):
        for pa, pb, pc in (
            ({"limit": 100}, {"limit": 50}, {"limit": 50}),
            ({"tables": ["a", "b"]}, {"tables": ["a"]}, {"tables": ["a"]}),
            ({"limit": 100}, {}, {"limit": 50}),
            ({"tables": ["a"]}, {"tables": []}, {"tables": ["a"]}),
        ):
            add([grant(mid, pa), grant(mid, pb), grant(mid, pc)], "three sources")
            add([grant(mid, pc), grant(mid, pb), grant(mid, pa)], "three sources, reversed")

    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..",
        "data", "_vectors", "clc-v1", "property-cases.json"))
    args = ap.parse_args()

    data = {
        "_meta": {
            "title": "CLC-v1 intersection property cases",
            "principle": "P11 — composition narrows only",
            "spec_clause": "CLC-v1 §7 rules 2/5/6, §9.1 layer 10",
            "property": ("if Intersect(sources) succeeds, the result MUST be "
                         "covered by every source and MUST NOT depend on the "
                         "order of the sources; otherwise it MUST deny with a "
                         "normative reason code and never raise"),
            "generator": "capability/scripts/gen-property-cases.py",
            "status": "reference",
            "count": 0,
        },
        "cases": [],
    }
    data["cases"] = cases()
    data["_meta"]["count"] = len(data["cases"])

    with open(args.out, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("wrote %s with %d cases" % (args.out, data["_meta"]["count"]))


if __name__ == "__main__":
    main()
