#!/usr/bin/env python3
"""BOBBIE fresh verification for run 1931 — READ-ONLY."""
import json, urllib.request, datetime
from Crypto.Hash import keccak

RPC = "https://bsc-dataseed.binance.org"
ADDR = "0x3BF121dC4c5a1Ba567F3eE801d0e447601726207"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]

def call(data):
    body = json.dumps({"jsonrpc": "2.0", "method": "eth_call",
                       "params": [{"to": ADDR, "data": data}, "latest"], "id": 1}).encode()
    req = urllib.request.Request(RPC, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def u(fn):
    try:
        res = call(sel(fn))
        if "result" in res and res["result"] and res["result"] != "0x":
            return int(res["result"], 16)
        return ("ERR", res.get("error"))
    except Exception as e:
        return ("EXC", str(e))

def addr_arg(a):
    return "0" * 24 + a[2:].lower()

def uint_arg(n):
    return format(n, "064x")

def bool_arg(b):
    return format(1 if b else 0, "064x")

out = {}
for fn in ["totalMinted()", "freeAllocated()", "FREE_SUPPLY()", "MAX_SUPPLY()",
           "mintStartsAt()", "mintEndsAt()", "mintOpen()", "paused()",
           "poolRemaining()", "freeLeft()"]:
    out[fn] = u(fn)
    print(fn, out[fn])

# quote(address,uint256,bool) -> (freeQuantity, paidQuantity, cost, nonce) presumed 4x uint256
for qty, flag in [(1, False), (1, True)]:
    data = sel("quote(address,uint256,bool)") + addr_arg(USER) + uint_arg(qty) + bool_arg(flag)
    try:
        res = call(data)
        raw = res.get("result", "")
        vals = [int(raw[2 + i * 64: 2 + (i + 1) * 64], 16) for i in range(len(raw[2:]) // 64)] if raw and raw != "0x" else ("ERR", res.get("error"))
        print(f"quote(user,{qty},{flag})", vals)
        out[f"quote_{qty}_{flag}"] = vals
    except Exception as e:
        print(f"quote(user,{qty},{flag}) EXC", e)
        out[f"quote_{qty}_{flag}"] = ("EXC", str(e))

# per-address views
for fn in ["mintedBy(address)", "freeUsed(address)", "freeClaimed(address)",
           "eligible(address)", "balanceOf(address)"]:
    data = sel(fn) + addr_arg(USER)
    try:
        res = call(data)
        if "result" in res and res["result"] and res["result"] != "0x":
            v = int(res["result"], 16)
        else:
            v = ("ERR", res.get("error"))
        print(fn, v)
        out[fn] = v
    except Exception as e:
        print(fn, "EXC", e)
        out[fn] = ("EXC", str(e))

# block + timestamps
body = json.dumps({"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 2}).encode()
req = urllib.request.Request(RPC, data=body, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req, timeout=30) as r:
    blk = int(json.load(r)["result"], 16)
print("block", blk)
out["block"] = blk
for k in ["mintStartsAt()", "mintEndsAt()"]:
    v = out.get(k)
    if isinstance(v, int):
        print(k, "->", datetime.datetime.fromtimestamp(v, datetime.timezone(datetime.timedelta(hours=7))).isoformat())

json.dump(out, open("run-2026-11-07-1931-bobbie-verify.json", "w"), indent=1, default=str)
print("saved run-2026-11-07-1931-bobbie-verify.json")
