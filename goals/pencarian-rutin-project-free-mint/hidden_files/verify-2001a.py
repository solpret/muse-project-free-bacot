#!/usr/bin/env python3
"""Leg 2 run 2001 on-chain verification (read-only).
eth_call via bsc-dataseed1/2 (urllib, 8s timeout), sequential, no eth_getCode.
No Ankr getLogs needed: no genuinely-new free-mint contract this run
(first-mint ages already verified in leg 1931 for BRAINROT/HOPKIN)."""
import json, sys, time, urllib.request
from eth_hash.auto import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]

def rpc_call(method, params, timeout=8):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method,
                       "params": params}).encode()
    last = None
    for ep in EPS:
        req = urllib.request.Request(ep, data=body,
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                d = json.loads(resp.read().decode())
            if "error" in d:
                return {"__rpc_error__": d["error"]}
            return d.get("result")
        except Exception as e:
            last = e
    return {"__transport_error__": f"{type(last).__name__}:{str(last)[:100]}"}

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def call(addr, sig, args=""):
    r = rpc_call("eth_call", [{"to": addr, "data": sel(sig) + args}, "latest"])
    if isinstance(r, dict):
        return "ERR:" + json.dumps(r)[:120]
    return r

def dec_uint(out):
    if not isinstance(out, str) or not out.startswith("0x") or len(out) < 66:
        return None
    try:
        return int(out[2:66], 16)
    except Exception:
        return None

def dec_str(out):
    if not isinstance(out, str) or not out.startswith("0x") or len(out) < 130:
        return None
    try:
        b = bytes.fromhex(out[2:])
        off = int.from_bytes(b[0:32], "big")
        ln = int.from_bytes(b[off:off+32], "big")
        return b[off+32:off+32+ln].decode("utf-8", "replace")
    except Exception:
        return None

def enc_addr(a):
    return a[2:].lower().rjust(64, "0")

def enc_uint(n):
    return format(n, "064x")

U = "uint"
S = "str"
VIEWS = {'BRAINROT': ('0x3c7d328027ca0068e7cd8709d64d9161bc35de93', [('totalSupply', 'totalSupply()', '', 'uint'), ('freeLeft', 'freeLeft()', '', 'uint'), ('mintOpen', 'mintOpen()', '', 'uint'), ('MAX_SUPPLY', 'MAX_SUPPLY()', '', 'uint'), ('name', 'name()', '', 'str'), ('symbol', 'symbol()', '', 'str'), ('freeOf_user_1', 'freeOf(address,uint256)', '000000000000000000000000eb237f6f9fb4e826739f0954e9768914f28b2c2e0000000000000000000000000000000000000000000000000000000000000001', 'uint'), ('mintedBy_user', 'mintedBy(address)', '000000000000000000000000eb237f6f9fb4e826739f0954e9768914f28b2c2e', 'uint')]), 'HOG': ('0x7bc0b487febcbb1caa781148bf05a8cd72d02ec5', [('totalSupply', 'totalSupply()', '', 'uint'), ('freeLeft', 'freeLeft()', '', 'uint'), ('mintOpen', 'mintOpen()', '', 'uint'), ('MAX_SUPPLY', 'MAX_SUPPLY()', '', 'uint'), ('name', 'name()', '', 'str'), ('symbol', 'symbol()', '', 'str')]), 'GACHA': ('0x7182f4230cbd53294366a344d13ddd041c4e734c', [('totalSupply', 'totalSupply()', '', 'uint'), ('freeLeft', 'freeLeft()', '', 'uint'), ('MAX_SUPPLY', 'MAX_SUPPLY()', '', 'uint')]), 'HELM': ('0xe0df49c281b8584f03ed21beac0e5002ec4a0599', [('totalSupply', 'totalSupply()', '', 'uint'), ('freeLeft', 'freeLeft()', '', 'uint'), ('MAX_SUPPLY', 'MAX_SUPPLY()', '', 'uint')]), 'OMENS': ('0xbd0e97f1a2b8b192382935a7b69c9514d75a479a', [('totalSupply', 'totalSupply()', '', 'uint'), ('freeLeft', 'freeLeft()', '', 'uint'), ('MAX_SUPPLY', 'MAX_SUPPLY()', '', 'uint')]), 'TPET': ('0x31975837d5c68eea0b66b5fd27de3506c2f109ba', [('totalSupply', 'totalSupply()', '', 'uint'), ('freeMinted', 'freeMinted()', '', 'uint')]), 'AGENTDRAGON': ('0x2df7435f5bce0577bee213e13da68313c74d7d0b', [('totalSupply', 'totalSupply()', '', 'uint'), ('freeClaimed', 'freeClaimed()', '', 'uint')]), 'HOPKIN': ('0x2728c134D79D34A977d6D35D8A3014AbB5C97ed4', [('totalSupply', 'totalSupply()', '', 'uint'), ('mintOpen', 'mintOpen()', '', 'uint')]), 'KZMB': ('0xbd6e4c6def0065007bd163e4223ae4f3aa3b6f09', [('sharesSold', 'sharesSold()', '', 'uint'), ('totalSupply', 'totalSupply()', '', 'uint')]), 'HORUS': ('0x794ad67a5590c7e5848e49181297f9cc7c6ce00e', [('totalSupply', 'totalSupply()', '', 'uint')]), 'PROOF_OF_AGI': ('0xbf7332b1787d916331b592361cb018a1e9aed1cd', [('totalSupply', 'totalSupply()', '', 'uint'), ('name', 'name()', '', 'str'), ('symbol', 'symbol()', '', 'str')]), 'ALCHEMISTER': ('0x69037Db8C6f237eCd9aB4B364D65C6dD05825dCb', [('totalSupply', 'totalSupply()', '', 'uint')]), 'STRAWBS': ('0x9Bed5d806Ed91675127f81d1F13C6Ab3eF9430Cc', [('totalSupply', 'totalSupply()', '', 'uint')])}

out = {"run": "2001", "method": "read-only eth_call via bsc-dataseed1/2 (urllib, 8s timeout), sequential; no eth_getCode; no Ankr getLogs needed this run"}
head = rpc_call("eth_blockNumber", [])
out["head_block"] = int(head, 16) if isinstance(head, str) else head
print("head:", out["head_block"], flush=True)
for name, (addr, views) in VIEWS.items():
    r = {"address": addr}
    for label, sig, args, kind in views:
        raw = call(addr, sig, args)
        v = dec_uint(raw) if kind == U else dec_str(raw)
        r[label] = v if v is not None else (raw if isinstance(raw, str) and raw.startswith("ERR") else "REVERT/EMPTY")
    out[name] = r
    print("probed", name, json.dumps(r), flush=True)

json.dump(out, open(f"{BASE}/verify-2001a.json", "w"), indent=1, ensure_ascii=False)
print("WROTE verify-2001a.json")
