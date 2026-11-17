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
VIEWS = {'LIONSHARE': ('0x6AC03204aFE631D673938Eb82D2F121B015eAB3F', [('totalSupply', 'totalSupply()', '', 'uint')]), 'PANDA_V4': ('0x2820e61eD78aC29F52eDAE05F01aB552307b907C', [('totalSupply', 'totalSupply()', '', 'uint'), ('name', 'name()', '', 'str'), ('symbol', 'symbol()', '', 'str')]), 'NIGHTSHIFT': ('0x427aed3f7427b48e45f5e648105aa1b77724cf14', [('totalSupply', 'totalSupply()', '', 'uint')]), 'BOUNDAGENT': ('0xa75526d63bd5E3b3e8A65a5f2efEF45072904d04', [('totalSupply', 'totalSupply()', '', 'uint')]), 'OTV': ('0xfab9c88d25e111edd68a2cca3e0f650863a5bf25', [('totalSupply', 'totalSupply()', '', 'uint')]), 'FLEET': ('0x5bc4fb61270c2628c93bf507c4ba125b868d34ff', [('totalSupply', 'totalSupply()', '', 'uint')]), 'ONLYAI': ('0x156482ad3f0eebd8e3f70d494ebd1da3f738f5ba', [('totalSupply', 'totalSupply()', '', 'uint')]), 'TACOTRON': ('0x05debe4445232205ae7e79d02cb5de5aa0641eff', [('totalSupply', 'totalSupply()', '', 'uint'), ('freeClaimed', 'freeClaimed()', '', 'uint')]), 'MARS_CLAIM': ('0xD87f8e06c4063457A3E5E12849bedbEF23de7B1e', [('totalSupply', 'totalSupply()', '', 'uint'), ('name', 'name()', '', 'str'), ('symbol', 'symbol()', '', 'str')]), 'MARSCOIN': ('0xfe189e97832da1573e4e4ff034f4ffc3a15c7777', [('totalSupply', 'totalSupply()', '', 'uint'), ('name', 'name()', '', 'str'), ('symbol', 'symbol()', '', 'str')]), 'AGENTVOLT_MINT': ('0xc58ecec1437777061134c1bddf0ed5ea6eafabf4', [('totalSupply', 'totalSupply()', '', 'uint')]), 'VOLT_TOKEN': ('0x39c9778c6aab547a6c265c2e556217636bbe680a', [('totalSupply', 'totalSupply()', '', 'uint')])}

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

json.dump(out, open(f"{BASE}/verify-2001b.json", "w"), indent=1, ensure_ascii=False)
print("WROTE verify-2001b.json")
