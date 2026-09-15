"""Value-level differential probe (axis 5-13).

Usage: python3 probe.py <path-to-clc_semantics-dir> [cases.json]
Prints one JSON line per case: raw-path result on both sides and the canonical
bytes, so the caller can see whether the two inputs are the same value.
"""
import importlib.util, json, sys
base = sys.argv[1]
cases = sys.argv[2] if len(sys.argv) > 2 else "probes.json"
spec = importlib.util.spec_from_file_location("clcsem", f"{base}/clc_semantics.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
out = []
for p in json.load(open(cases)):
    rec = {"id": p["id"], "lang": "py", "raw_eval": None, "raw_app": None, "canon_eval": None, "canon_app": None}
    for side, key in (("evaluated", "raw_eval"), ("applied", "raw_app")):
        try:
            m.validate_raw_params(p[side]); rec[key] = "ok"
        except Exception as e:
            rec[key] = str(e).split(":")[0]
    for side, key in (("evaluated", "canon_eval"), ("applied", "canon_app")):
        try:
            rec[key] = m.canonical_json(json.loads(p[side]))
        except Exception as e:
            rec[key] = "ERR:" + type(e).__name__
    rec["same"] = (bool(rec["canon_eval"]) and bool(rec["canon_app"])
                   and not str(rec["canon_eval"]).startswith("ERR")
                   and rec["canon_eval"] == rec["canon_app"])
    out.append(rec)
print(json.dumps(out, ensure_ascii=False))
