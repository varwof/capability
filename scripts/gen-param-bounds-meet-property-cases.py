#!/usr/bin/env python3
"""Generate the CLC-v1 §6.6 BoundMeet property cases (rev CLC-1.15).

Deterministic: the case list is enumerated, not sampled, so re-running this
script reproduces the file byte for byte (no PRNG, no clock).

Property under test (the meet invariant the CLC-1.15 review asked for):

  for every case (a list of sources sharing one identifier and declaring the
  same param_bounds key) and every operation o in the shared `ops` sample:

    * Intersect(sources) MUST NOT raise — it either succeeds or refuses with
      a normative reason code (fail closed, §7 / §9.1 layer 10), and
    * **every successful meet authorizes only what EVERY source authorizes**:
      Entails(G, o)  ==>  Entails(S, o) for every source S (§6.6; this is the
      law the removed numeric∩enum filtered-enum reduction violated: the
      filtered enum accepted the array [3] while the numeric source
      fail-closed it at §6.5 layer 9), and
    * when the meet succeeds, it MUST NOT depend on the order of the sources
      (§7 rule 2/6, P11); a refused meet may refuse with a different code
      under a different fold order and is only required to stay refused.

Usage:
  python3 scripts/gen-param-bounds-meet-property-cases.py \
      [--out data/_vectors/clc-v1/param-bounds-meet-property-cases.json]
"""
import argparse
import itertools
import json
import os

ID = "std/database-v1:query:SELECT"
KEY = "limit"

# Every Bound the §6.5 grammar allows, one per family plus the corners the
# meet rules distinguish: the empty identity, incommensurable steps, a
# cross-family-clash pair (numeric vs enum vs cardinality-only), nested key
# sets that differ, type-sensitive enum members (1 / true / "1" are three
# distinct members, §6.5 layer 8 rev CLC-1.15) and `optional` variants.
BOUNDS = [
    {},
    {"min": 0, "max": 100},
    {"min": 20, "max": 80},
    {"min": 50},
    {"max": 50},
    {"step": 2},
    {"step": 5},
    {"step": 10},
    {"step": 7},
    {"min": 0, "max": 10, "step": 2},
    {"enum": [0, 2, 4, 10, 20, 50, 80, 100]},
    {"enum": [20, 50, 80]},
    {"enum": [1, 3, 5]},
    {"enum": [1, True, "1"]},
    {"enum": [True, False]},
    {"min_items": 1, "max_items": 2},
    {"enum": [2, 4], "min_items": 1, "max_items": 3},
    {"nested": {"a": {"min": 0, "max": 10}}},
    {"nested": {"a": {"max": 5}}},
    {"nested": {"b": {"max": 5}}},
    {"max": 100, "optional": True},
    {"max": 50, "optional": True},
]

# Operation values for the shared key: numbers on and off the step grids and
# interval edges, canonicalization twins (1 / 1.0), the three JSON types that
# type-sensitive equality keeps apart (1, true, "1"), scalars under enum
# bounds, arrays (element-wise membership and cardinality), objects under
# nested bounds, and the key-closure corners.
OPS_PARAMS = [
    {},
    {"limit": 0},
    {"limit": 1},
    {"limit": 1.0},
    {"limit": 2},
    {"limit": 3},
    {"limit": 4},
    {"limit": 5},
    {"limit": 7},
    {"limit": 10},
    {"limit": 20},
    {"limit": 35},
    {"limit": 50},
    {"limit": 80},
    {"limit": 100},
    {"limit": 101},
    {"limit": True},
    {"limit": False},
    {"limit": "1"},
    {"limit": "50"},
    {"limit": []},
    {"limit": [1]},
    {"limit": [2, 4]},
    {"limit": [1, 3, 5]},
    {"limit": [True]},
    {"limit": {"a": 0}},
    {"limit": {"a": 5}},
    {"limit": {"a": 10}},
    {"limit": {"b": 1}},
    {"limit": {"a": 1, "b": 2}},
    {"other": 1},
]

ONE = ID
THREE_SOURCE_PICKS = [
    (1, 2, 4),    # numeric × numeric × numeric: interval folding
    (5, 7, 8),    # step 5 × step 7 × step 10: incommensurable fold
    (10, 11, 12),  # enum × enum × enum: narrowing member sets
    (13, 13, 14),  # type-sensitive members, duplicated source
    (0, 1, 13),   # empty identity × numeric × enum: cross-family via identity
    (17, 18, 19),  # nested key sets that agree then differ
    (15, 2, 16),  # cardinality-only × numeric × cardinality+enum
    (20, 21, 2),  # optional × optional × required
]


def grant(bound):
    return {"id": ONE, "param_bounds": {KEY: bound}}


def operation(params):
    return {"id": ONE, "params": params}


def cases():
    out = []
    n = 0

    def add(sources, note):
        nonlocal n
        n += 1
        out.append({
            "id": "bmp-%04d" % n,
            "sources": sources,
            "note": note,
        })

    # 1. every ordered pair of Bounds, both directions, so order independence
    #    and the cross-family refusals are exercised symmetrically.
    for a, b in itertools.product(BOUNDS, BOUNDS):
        add([grant(a), grant(b)], "bound pair (both orders enumerated)")

    # 2. three-source folds: the meet folds associatively for same-family
    #    bounds and refuses deterministically across family clashes.
    for ia, ib, ic in THREE_SOURCE_PICKS:
        picks = [BOUNDS[ia], BOUNDS[ib], BOUNDS[ic]]
        add([grant(x) for x in picks], "three sources")
        add([grant(x) for x in reversed(picks)], "three sources, reversed")

    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..",
        "data", "_vectors", "clc-v1", "param-bounds-meet-property-cases.json"))
    args = ap.parse_args()

    ops = [operation(p) for p in OPS_PARAMS]
    case_list = cases()

    data = {
        "_meta": {
            "title": "CLC-v1 §6.6 BoundMeet property cases",
            "principle": "P11 — composition narrows only, over param_bounds",
            "spec_clause": "CLC-v1 §6.6 (rev CLC-1.15), §7 rules 2/5/6, §9.1 layer 10",
            "property": ("if Intersect(sources) succeeds, then for every o in `ops`: "
                         "Entails(G, o) implies Entails(S, o) for EVERY source S; the "
                         "successful result MUST NOT depend on the order of the sources; "
                         "otherwise Intersect MUST deny with a normative reason code and "
                         "never raise"),
            "generator": "capability/scripts/gen-param-bounds-meet-property-cases.py",
            "status": "reference",
            "count": len(case_list),
            "ops_count": len(ops),
            "bounds_space": len(BOUNDS),
        },
        "ops": ops,
        "cases": case_list,
    }

    with open(args.out, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("wrote %s with %d cases and %d ops" % (args.out, data["_meta"]["count"], len(ops)))


if __name__ == "__main__":
    main()
