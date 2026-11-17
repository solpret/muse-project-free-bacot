#!/usr/bin/env python3
"""Run 2331 Subagent B: on-chain verification of Boltbook leads. Read-only."""
import json, urllib.request, time
from Crypto.Hash import keccak

RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")

def raw(to, data):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as r: out = json.load(r)
            if "error" in out: return None
            v = out["result"]
            if not v or v == "0x": return None
            return v
        except Exception:
            continue
    return None

def call_int(to, sig, args=""):
    v = raw(to, sel(sig) + args)
    if v is None: return None
    try: return int(v, 16)
    except Exception: return v

def call_str(to, sig):
    v = raw(to, sel(sig))
    if v is None: return None
    try:
        b = bytes.fromhex(v[2:])
        # string: offset(32) + len(32) + data
        ln = int.from_bytes(b[32:64], "big")
        return b[64:64+ln].decode("utf-8", "ignore")
    except Exception:
        return v

def code_len(to):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                               "params": [to, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as r: out = json.load(r)
            c = out.get("result", "")
            return (len(c) - 2) // 2 if c.startswith("0x") else None
        except Exception:
            continue
    return None

def block():
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as r: return int(json.load(r)["result"], 16)
        except Exception: continue
    return None

out = {"run": "2331-B", "block": block(), "user": USER, "results": {}}

# Zero Shark — verified ABI, share-sale/token shape
z = "0x3ebbed7de6afa9dcc0078a993c581fb50ada5693"
out["results"]["Zero Shark"] = {"address": z, "code_bytes": code_len(z),
    "name": call_str(z, "name()"), "symbol": call_str(z, "symbol()"),
    "decimals": call_int(z, "decimals()"), "totalSupply": call_int(z, "totalSupply()"),
    "FREE_SHARES": call_int(z, "FREE_SHARES()"), "freeClaimed": call_int(z, "freeClaimed()"),
    "freeClaimedBy_user": call_int(z, "freeClaimedBy(address)", enc(USER)),
    "balanceOf_user": call_int(z, "balanceOf(address)", enc(USER)),
    "opened": call_int(z, "opened()"), "openedAt": call_int(z, "openedAt()"),
    "startAt": call_int(z, "startAt()"), "MINT_START_AT": call_int(z, "MINT_START_AT()"),
    "endAt": call_int(z, "endAt()"), "pair": raw(z, sel("pair()")),
    "TOKENS_PER_SHARE": call_int(z, "TOKENS_PER_SHARE()"),
    "MAX_SUPPLY": call_int(z, "MAX_SUPPLY()"), "REGISTRY": raw(z, sel("REGISTRY()")),
    "phase": call_int(z, "phase()")}

# Moon Cat — unverified, standard views only
m = "0x2c002fa8398e4f55314757c9ee7b35ba850125ec"
out["results"]["Moon Cat"] = {"address": m, "code_bytes": code_len(m),
    "name": call_str(m, "name()"), "symbol": call_str(m, "symbol()"),
    "decimals": call_int(m, "decimals()"), "totalSupply": call_int(m, "totalSupply()"),
    "balanceOf_user": call_int(m, "balanceOf(address)", enc(USER)),
    "freeClaimed": call_int(m, "freeClaimed()"), "FREE_SUPPLY": call_int(m, "FREE_SUPPLY()"),
    "MAX_SUPPLY": call_int(m, "MAX_SUPPLY()"), "mintOpen": call_int(m, "mintOpen()")}

# MORPHA — unverified
mo = "0xb40e4d3b33c5d70ab31a1dde3c240727691cb738"
out["results"]["MORPHA"] = {"address": mo, "code_bytes": code_len(mo),
    "name": call_str(mo, "name()"), "symbol": call_str(mo, "symbol()"),
    "decimals": call_int(mo, "decimals()"), "totalSupply": call_int(mo, "totalSupply()"),
    "balanceOf_user": call_int(mo, "balanceOf(address)", enc(USER)),
    "freeClaimed": call_int(mo, "freeClaimed()"), "freeMinted": call_int(mo, "freeMinted()"),
    "FREE_SUPPLY": call_int(mo, "FREE_SUPPLY()"), "MAX_SUPPLY": call_int(mo, "MAX_SUPPLY()")}

# Believe Binance — unverified
b = "0x5e1a6b3041873b05d21c24cce8c1af763846bea7"
out["results"]["Believe Binance"] = {"address": b, "code_bytes": code_len(b),
    "name": call_str(b, "name()"), "symbol": call_str(b, "symbol()"),
    "decimals": call_int(b, "decimals()"), "totalSupply": call_int(b, "totalSupply()"),
    "balanceOf_user": call_int(b, "balanceOf(address)", enc(USER)),
    "freeClaimed": call_int(b, "freeClaimed()"), "FREE_SUPPLY": call_int(b, "FREE_SUPPLY()")}

# BNB CACHE Server — already tracked, fresh re-read for the change
c = "0x1989058da9eb7f36e69779fcda0ea04578528570"
out["results"]["BNB CACHE Server"] = {"address": c, "code_bytes": code_len(c),
    "name": call_str(c, "name()"), "totalServersMinted": call_int(c, "totalServersMinted()"),
    "freeServersClaimed": call_int(c, "freeServersClaimed()"),
    "freeServersRemaining": call_int(c, "freeServersRemaining()"),
    "FREE_SERVERS_TOTAL": call_int(c, "FREE_SERVERS_TOTAL()"),
    "freeWindowOpen": call_int(c, "freeWindowOpen()"),
    "freeWindowClosesAt": call_int(c, "freeWindowClosesAt()"),
    "freeClaimedBy_user": call_int(c, "freeClaimedBy(address)", enc(USER)),
    "balanceOf_user": call_int(c, "balanceOf(address)", enc(USER))}

json.dump(out, open("run-2026-11-05-2331-verify.json", "w"), indent=1)
print(json.dumps(out, indent=1))
