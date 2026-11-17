#!/usr/bin/env python3
"""00:01 run: totals check for 15 first-seen verified+free/registry scan contracts. Read-only."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
def call(to, data):
    for ep in EPS:
        try: return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0), None
        except Exception as e: err = f"{type(e).__name__}: {str(e)[:120]}"
    return None, err
cand = json.load(open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-02-0001-scan-triage-cand.json"))
out = {}
for c in cand:
    a = c["address"]; d = {"scan": c}
    for name, sig in [("totalSupply", "totalSupply()"), ("totalMinted", "totalMinted()"), ("freeClaimed", "freeClaimed()"), ("FREE_SUPPLY", "FREE_SUPPLY()"), ("MAX_SUPPLY", "MAX_SUPPLY()"), ("mintOpen", "mintOpen()")]:
        v, e = call(a, sel(sig))
        try: iv = int(v, 16) if v else None
        except Exception: iv = None
        d[name] = {"int": iv, "error": e if v is None else None}
    out[a] = d
    print(a, c["name"], "window", c["mint_count"], "totalSupply", d["totalSupply"]["int"], "totalMinted", d["totalMinted"]["int"], "freeClaimed", d["freeClaimed"]["int"], "FREE_SUPPLY", d["FREE_SUPPLY"]["int"])
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-02-0001-scan-triage.json", "w"), indent=1)
