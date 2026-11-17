#!/usr/bin/env python3
"""Grove watch run 2026-11-09 04:01 WIB. Read-only: freeOpen() + freeClaimed(user)."""
import json, urllib.request
from Crypto.Hash import keccak
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com",
        "https://bsc-dataseed.binance.org", "https://bsc-dataseed2.bnbchain.org"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
G = "0x8b710e45D38fD55E2D198d2295c0a0D24EBfd64c"
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def rpc(method, params):
    for rpc_url in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
            req = urllib.request.Request(rpc_url, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=8) as r: out = json.load(r)
            if "error" in out: continue
            return out["result"]
        except Exception:
            continue
    return None
def call(sig, args=""):
    v = rpc("eth_call", [{"to": G, "data": sel(sig) + args}, "latest"])
    if v is None or v == "0x": return None
    try: return int(v, 16)
    except Exception: return v
blk = rpc("eth_blockNumber", [])
out = {
    "block": int(blk, 16) if blk else None,
    "freeOpen": call("freeOpen()"),
    "freeClaimed_user": call("freeClaimed(address)", enc(USER)),
}
print(json.dumps(out, indent=1))
