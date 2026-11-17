#!/usr/bin/env python3
"""Bounded 40s retry for Wuyuhive + Orchidia (all-'deadline' at 04:44 and 04:49). Read-only."""
import json, time, urllib.request
from Crypto.Hash import keccak
RPC = "https://bsc-dataseed1.bnbchain.org"
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def call(to, data, timeout=6):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                       "params": [{"to": to, "data": data}, "latest"]}).encode()
    req = urllib.request.Request(RPC, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        o = json.load(r)
    v = o.get("result")
    if not v or v == "0x" or "error" in o:
        return None
    try: return int(v, 16)
    except Exception: return v
VIEWS = ["totalSupply()", "freeClaimed()", "freeMinted()", "FREE_SUPPLY()"]
out = {}
t0 = time.time()
for name, addr in {"Wuyuhive": "0x250e800025a9a7861970e253bab6975a57f80567",
                   "Orchidia": "0x09bcdd97186f6f37521bd1b281d329e48ac54b89"}.items():
    d = {}
    for sig in VIEWS:
        if time.time() - t0 > 40:
            d[sig.split("(")[0]] = "deadline"; continue
        try: d[sig.split("(")[0]] = call(addr, sel(sig))
        except Exception as e: d[sig.split("(")[0]] = f"err:{type(e).__name__}"
    out[name] = d
out["duration_s"] = round(time.time() - t0, 1)
json.dump(out, open("hot-leg-2026-11-07-0449-reread-retry.json", "w"), indent=1)
print(json.dumps(out, indent=1))
