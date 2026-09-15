"""Decision-level differential probe (axes 9/10/11/13/17).

Usage: python3 decide.py <path-to-clc_semantics-dir> [decisions.json]
Uses the decision entry point (authorize_set), not entails(): constraints are
evaluated in the decision function, so entails() would report them as absent.
"""
import importlib.util, json, sys
base = sys.argv[1]
cases = sys.argv[2] if len(sys.argv) > 2 else "decisions.json"
spec = importlib.util.spec_from_file_location("clcsem", f"{base}/clc_semantics.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
out = []
for p in json.load(open(cases)):
    try:
        r = m.authorize_set([p["grant"]], p["op"])
    except Exception as e:
        r = {"verdict": None, "reason": "EXC:" + type(e).__name__}
    out.append({"id": p["id"], "lang": "py", "verdict": r.get("verdict"), "reason": r.get("reason")})
print(json.dumps(out, ensure_ascii=False))
