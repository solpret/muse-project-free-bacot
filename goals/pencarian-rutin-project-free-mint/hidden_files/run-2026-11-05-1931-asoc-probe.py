#!/usr/bin/env python3
"""Run 1931 ASOC targeted probe (read-only): verify free-lane exhaustion."""
import json, urllib.request
from Crypto.Hash import keccak
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
SALE = "0x43cEef9313CB8c4ca3757bA841C44DF40A223205"
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")
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
def block():
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=8) as r: return int(json.load(r)["result"], 16)
        except Exception: continue
    return None
blk = block()
out = {"block": blk}
out["freeUsed"] = call(SALE, "freeUsed()")
out["FREE_QUOTA"] = call(SALE, "FREE_QUOTA()")
out["totalSold"] = call(SALE, "totalSold()")
out["TOTAL_SHARES"] = call(SALE, "TOTAL_SHARES()")
out["saleEnded"] = call(SALE, "saleEnded()")
out["freeClaimed_user"] = call(SALE, "freeClaimed(address)", enc(USER))
out["startTime"] = call(SALE, "startTime()")
print(json.dumps(out, indent=1))
json.dump(out, open("run-2026-11-05-1931-asoc-probe.json", "w"), indent=1)
