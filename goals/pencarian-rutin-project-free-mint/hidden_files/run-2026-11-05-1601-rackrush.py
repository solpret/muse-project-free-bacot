#!/usr/bin/env python3
"""RACKRUSH first-mint + free-shape verify (main job deep-dive). Read-only."""
import json, sys, urllib.request
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
from Crypto.Hash import keccak
ADDR = "0x5e42DB19A22F5c858DC72df6352495FFFF9abb62"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x" + "00" * 32
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc-dataseed2.bnbchain.org"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def raw(to, data):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=8) as r: out = json.load(r)
            if "error" in out: return {"error": str(out["error"])[:60]}
            v = out["result"]
            if not v or v == "0x": return None
            try: return int(v, 16)
            except Exception: return v
        except Exception: continue
    return {"error": "rpc-fail"}
def call(to, sig, args=""): return raw(to, sel(sig) + args)
def block_ts(n):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                               "params": [hex(n), False]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=8) as r:
                return int(json.load(r)["result"]["timestamp"], 16)
        except Exception: continue
    return None
def any_mint(lo, hi):
    params = {"blockchain": "bsc", "fromBlock": hex(lo), "toBlock": hex(hi),
              "pageSize": 1000, "decodeLogs": False, "topics": [TRANSFER, ZERO], "address": ADDR}
    body = ankr_post("ankr_getLogs", params, timeout=30)
    logs = (body.get("result", {}) or {}).get("logs", []) if isinstance(body, dict) else []
    for lg in logs:
        if len(lg.get("topics", [])) == 4:
            return int(lg["blockNumber"], 16)
    return None
print("name/symbol/supply/free:")
print(" totalSupply", call(ADDR, "totalSupply()"))
print(" freeMinted", call(ADDR, "freeMinted()"))
print(" FREE_CAP", call(ADDR, "FREE_CAP()"))
print(" MAX_SUPPLY", call(ADDR, "MAX_SUPPLY()"))
print(" freeClaimed", call(ADDR, "freeClaimed()"))
print(" mintOpen", call(ADDR, "mintOpen()"))
print(" owner", call(ADDR, "owner()"))
LO, HI = 131650000, 131789854
print("any_mint in window:", any_mint(LO, HI))
lo, hi = LO, HI
if any_mint(lo, hi) is not None:
    while lo < hi:
        mid = (lo + hi) // 2
        if any_mint(lo, mid) is not None:
            hi = mid
        else:
            lo = mid + 1
    print("FIRST_MINT_BLOCK", lo, "TS", block_ts(lo))
else:
    print("NO_MINT_IN_WINDOW")
