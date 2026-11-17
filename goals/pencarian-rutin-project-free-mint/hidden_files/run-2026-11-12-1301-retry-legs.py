#!/usr/bin/env python3
"""Run 1301 retry: re-shape-check the 1 error address from legs (0xa161...,
Boltbook tx-hash false positive) via curl."""
import json, subprocess
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
def get(url):
    out = subprocess.run(["curl","-sL","--max-time","25",url], capture_output=True, text=True, timeout=30)
    if out.returncode != 0 or not out.stdout.strip():
        raise RuntimeError(f"curl rc={out.returncode} empty")
    return out.stdout
addrs = ["0xa1611fa81743461930b4fe3f5e77174c8e71405d"]
res = []
for a in addrs:
    try:
        meta = json.loads(get(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi"))
        res.append({"address": a, "status": "verified-now" if meta.get("match") else "not-a-verified-contract",
                    "match": meta.get("match")})
    except Exception as e:
        res.append({"address": a, "status": "still-error", "error": f"{type(e).__name__}: {str(e)[:100]}"})
out = {"run": "2026-11-12 13:01 WIB", "retried": len(addrs),
       "now_verified": [r for r in res if r["status"]=="verified-now"],
       "still_error": [r for r in res if r["status"]!="verified-now"]}
json.dump(out, open(BASE+"run-2026-11-12-1301-retry-legs.json","w"), indent=1)
print(json.dumps(out, indent=1))
