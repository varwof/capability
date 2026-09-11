#!/usr/bin/env python3
"""OCMP offline-vector gate: coverage and vocabulary.

`data/_vectors/clc-v1/offline-vectors.json` holds the fail-closed reference
classes for the Offline Capability Manifest Profile (OCMP v0 §3, rules R2–R7).
There is no OCMP *evaluator* yet — the profile is a carrier-side document — so
this gate does not evaluate anything.  What it does enforce, on every run:

  1. structure: unique ids, required fields, every case denies (never raises);
  2. vocabulary: every reported reason code is one of the codes OCMP §3 defines,
     and it matches the case's declared class;
  3. coverage: every rule R2–R7, every conformance level (OCMP-1/2/3) and every
     normative reason code appears in at least one case;
  4. level consistency: a case's rule must belong to the rules its level claims.

Usage: python3 scripts/check-offline-vectors.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT = os.path.join(HERE, "..", "data", "_vectors", "clc-v1", "offline-vectors.json")

# OCMP v0 §3 normative reason codes.
CODES = {
    "capability_not_authorized",
    "trust_anchor_missing",
    "status_snapshot_missing",
    "local_policy_missing",
    "fact_unavailable",
    "replay_state_invalid",
    "status_snapshot_expired",
    "status_snapshot_rollback",
    "revoked",
    "replay_detected",
    "clock_unsynchronized",
}

RULES = ["R2", "R3", "R4", "R5", "R6", "R7"]
# A level is the cumulative set of rules it claims (OCMP v0 §5).
LEVEL_RULES = {
    "OCMP-1": {"R2", "R3", "R4"},
    "OCMP-2": {"R2", "R3", "R4", "R5"},
    "OCMP-3": {"R2", "R3", "R4", "R5", "R6", "R7"},
}


def main():
    path = os.environ.get("OCMP_VECTORS", DEFAULT)
    with open(path) as f:
        vectors = json.load(f)["vectors"]

    problems = []
    seen_ids = set()
    rules_seen = set()
    levels_seen = set()
    codes_seen = set()

    for v in vectors:
        vid = v.get("id", "<no id>")
        if vid in seen_ids:
            problems.append("%s: duplicate id" % vid)
        seen_ids.add(vid)

        for field in ("rule", "ocmp_class", "ocmp_level", "scenario", "inputs", "expect", "derivation"):
            if field not in v:
                problems.append("%s: missing field %r" % (vid, field))

        expect = v.get("expect", {})
        if expect.get("verdict") != "deny":
            problems.append("%s: offline reference cases must deny, got %r" % (vid, expect.get("verdict")))
        reason = expect.get("reason")
        if reason not in CODES:
            problems.append("%s: reason %r is not an OCMP §3 code" % (vid, reason))
        if reason and v.get("ocmp_class") and reason != v["ocmp_class"]:
            problems.append("%s: reason %r does not match class %r" % (vid, reason, v["ocmp_class"]))

        rule = v.get("rule")
        level = v.get("ocmp_level")
        if rule in RULES:
            rules_seen.add(rule)
        if level in LEVEL_RULES:
            levels_seen.add(level)
            if rule not in LEVEL_RULES[level]:
                problems.append("%s: rule %s is not part of level %s" % (vid, rule, level))
        if reason:
            codes_seen.add(reason)

    for rule in RULES:
        if rule not in rules_seen:
            problems.append("no case covers %s" % rule)
    for level in LEVEL_RULES:
        if level not in levels_seen:
            problems.append("no case covers %s" % level)
    for code in sorted(CODES):
        if code not in codes_seen:
            problems.append("no case reports %s" % code)

    print("offline vectors: %d cases | rules %s | levels %s | codes %d/%d"
          % (len(vectors), ",".join(sorted(rules_seen)), ",".join(sorted(levels_seen)),
             len(codes_seen), len(CODES)))
    for p in problems:
        print("FAIL " + p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
