#!/usr/bin/env python3
"""Targeted read: bridge-Agent Harvest Land-2 (run 0701). Read-only."""
import json, urllib.request
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com", "https://bsc-dataseed2.bnbchain.org"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDR = "0xacf150d9eC909E3d339Bf4c6D090b18495674E66"
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def raw(data):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": ADDR, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=8) as r: out = json.load(r)
            if "error" in out: continue
            v = out["result"]
            if not v or v == "0x": return None
            try: return int(v, 16)
            except Exception: return v
        except Exception:
            continue
    return None
def block():
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=8) as r: return int(json.load(r)["result"], 16)
        except Exception: continue
    return None
blk = block()
res = {"block": blk, "address": ADDR}
for sig in ["totalSupply()", "totalMinted()", "freeMinted()", "freeClaimed()", "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()"]:
    res[sig] = raw(sel(sig))
for sig in ["mintedBy(address)", "freeUsed(address)", "balanceOf(address)", "canFreeMint(address)", "claimedFree(address)"]:
    res[sig + "_user"] = raw(sel(sig) + enc(USER))
res["quote_user_1"] = raw(sel("quote(address,uint256)") + enc(USER) + format(1, "064x"))
res["costOf_user_1"] = raw(sel("costOf(address,uint256)") + enc(USER) + format(1, "064x"))
print(json.dumps(res, indent=1))
json.dump(res, open(f"{BASE}/run-2026-11-06-0701-agentharvest.json", "w"), indent=1)
