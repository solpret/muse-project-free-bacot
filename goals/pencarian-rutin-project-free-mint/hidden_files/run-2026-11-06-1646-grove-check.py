#!/usr/bin/env python3
"""Agent Grove quick probe run 1901. Read-only."""
import json, urllib.request
from Crypto.Hash import keccak
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
G = "0x8b710e45D38fD55E2D198d2295c0a0D24EBfd64c"
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def raw(to, data):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=8) as r: out = json.load(r)
            if "error" in out: return None
            v = out["result"]
            if not v or v == "0x": return None
            return v
        except Exception:
            continue
    return None
def call(to, sig, args=""):
    v = raw(to, sel(sig) + args)
    if v is None: return None
    try: return int(v, 16)
    except Exception: return v
def call_addr(to, sig, args=""):
    v = raw(to, sel(sig) + args)
    if v is None: return None
    try: return "0x" + v[-40:]
    except Exception: return v
def block():
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=8) as r: return int(json.load(r)["result"], 16)
        except Exception: continue
    return None
out = {"block": block()}
for fn in ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "freeOpen()", "mintOpen()", "FREE_SUPPLY()", "MAX_SUPPLY()", "AGENT_REGISTRY()", "REGISTRY()"]:
    out[fn] = call(G, fn)
out["AGENT_ID()"] = call_addr(G, "AGENT_ID()")
out["balanceOf_user"] = call(G, "balanceOf(address)", enc(USER))
out["freeClaimed_user"] = call(G, "freeClaimed(address)", enc(USER))
out["mintedBy_user"] = call(G, "mintedBy(address)", enc(USER))
print(json.dumps(out, indent=1))
json.dump(out, open("run-2026-11-06-1646-grove-check.json", "w"), indent=1)
