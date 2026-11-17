#!/usr/bin/env python3
"""Hot-leg run 2026-11-07 22:49 WIB. Targeted on-chain verification (read-only).
HOG ORBIT (new Boltbook lead) + re-read ONLYAI / WAR3 / Tri333 (snapshot items
with fresh Boltbook signals or just-minted). Uses fast_rpc.call_many (raced,
batched). Per AGENTS.md fast_rpc.batch quirk: one revert kills the whole batch,
so each contract gets a LEAN batch of its own safe views; failures fall back
to single calls. Never writes the main snapshot."""
import json, sys, time, urllib.request
from eth_utils import function_signature_to_4byte_selector as sel
from eth_abi import encode as abi_encode

RPCS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
        "https://bsc-dataseed3.bnbchain.org/", "https://bsc-dataseed4.bnbchain.org/"]

def rpc_call(method, params, timeout=20):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    last = None
    for rpc in RPCS:
        try:
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                o = json.load(r)
            if "error" in o:
                last = o["error"]; continue
            return o.get("result"), rpc
        except Exception as e:
            last = e; continue
    return None, None

def eth_call(to, data):
    res, _ = rpc_call("eth_call", [{"to": to, "data": data}, "latest"])
    return res

USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
HOG = "0x7bc0b487febcbb1caa781148bf05a8cd72d02ec5"
ONLYAI = "0x156482ad3f0eebd8e3f70d494ebd1da3f738f5ba"
WAR3 = "0x1Aa9797cC762b838388566Daa45A56b1709F4Bbe"
TRI = "0x157D860e30b6c6d4dC0abe3bD6e66e659A9d524f"
REG = "0x60b9262456de011f7d15a54cdd8c48baa8b022f"

def call(to, sig, args=(), types=()):
    data = "0x" + sel(sig).hex()
    if args:
        data += abi_encode(list(types), list(args)).hex()
    return (to, data)

def dec_uint(res):
    if res is None: return None
    try: return int(res, 16)
    except Exception: return f"raw:{res}"

def dec_addr(res):
    if res is None: return None
    try: return "0x" + res[-40:]
    except Exception: return f"raw:{res}"

def dec_bool(res):
    if res is None: return None
    try: return int(res, 16) != 0
    except Exception: return f"raw:{res}"

out = {"run": "free-mint-hot-leg 2026-11-07 22:49:38 WIB"}
t0 = time.time()
blk, blk_rpc = rpc_call("eth_blockNumber", [])
out["block"] = int(blk, 16) if blk else None
out["block_rpc"] = blk_rpc

def batch_read(label, calls):
    """calls: list of (key, to, sig, args, types, decoder). One eth_call each
    (dataseed is fast for single calls now); a revert returns None, never
    kills the other reads."""
    r = {}
    for (k, to, sig, args, types, dec) in calls:
        data = "0x" + sel(sig).hex()
        if args:
            data += abi_encode(list(types), list(args)).hex()
        try:
            res = eth_call(to, data)
        except Exception as e:
            res = None
            r[k + "_error"] = f"{type(e).__name__}: {e}"
        r[k] = dec(res)
    out[label] = r
    return r

U = USER.lower()
pad_user = USER  # eth_abi handles padding

# HOG ORBIT
batch_read("hog", [
    ("totalSupply", HOG, "totalSupply()", (), (), dec_uint),
    ("MAX_SUPPLY", HOG, "MAX_SUPPLY()", (), (), dec_uint),
    ("freeLeft", HOG, "freeLeft()", (), (), dec_uint),
    ("mintOpen", HOG, "mintOpen()", (), (), dec_bool),
    ("price", HOG, "price()", (), (), dec_uint),
    ("agentIds", HOG, "agentIds()", (), (), dec_addr),
    ("costOf_user_1", HOG, "costOf(address,uint256)", (USER, 1), ("address", "uint256"), dec_uint),
    ("freeOf_user_1", HOG, "freeOf(address,uint256)", (USER, 1), ("address", "uint256"), dec_uint),
    ("mintedBy_user", HOG, "mintedBy(address)", (USER,), ("address",), dec_uint),
    ("balanceOf_user", HOG, "balanceOf(address)", (USER,), ("address",), dec_uint),
    ("name", HOG, "name()", (), (), lambda v: v),
    ("symbol", HOG, "symbol()", (), (), lambda v: v),
])

# ONLYAI
batch_read("onlyai", [
    ("totalSupply", ONLYAI, "totalSupply()", (), (), dec_uint),
    ("balanceOf_user", ONLYAI, "balanceOf(address)", (USER,), ("address",), dec_uint),
])

# WAR3
batch_read("war3", [
    ("totalSupply", WAR3, "totalSupply()", (), (), dec_uint),
    ("freeMinted", WAR3, "freeMinted()", (), (), dec_uint),
    ("agentFreeUsed", WAR3, "agentFreeUsed()", (), (), dec_uint),
    ("mintOpen", WAR3, "mintOpen()", (), (), dec_uint),
    ("balanceOf_user", WAR3, "balanceOf(address)", (USER,), ("address",), dec_uint),
])

# Tri333 (post-mint confirm)
batch_read("tri333", [
    ("freeMinted", TRI, "freeMinted()", (), (), dec_uint),
    ("freeCount_user", TRI, "freeCount(address)", (USER,), ("address",), dec_uint),
    ("balanceOf_user", TRI, "balanceOf(address)", (USER,), ("address",), dec_uint),
    ("mintOpen", TRI, "mintOpen()", (), (), dec_uint),
])

out["registry_expected"] = REG
out["duration_s"] = round(time.time() - t0, 1)
print(json.dumps(out, indent=1))
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-run-2026-11-07-2249-verify.json", "w"), indent=1)
