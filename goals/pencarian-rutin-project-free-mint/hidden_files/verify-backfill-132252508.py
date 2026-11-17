#!/usr/bin/env python3
"""Backfill triage run 0216 WIB 2026-11-08: verify first-seen 0x1A8Cc307...
(read-only). Sourcify ABI already fetched via curl -> /tmp/sourcify-1a8c.json.
eth_call via bsc-dataseed1/2 (urllib, 8s timeout). Block timestamp via
eth_getBlockByNumber on dataseed (Ankr returns fake 'now' timestamps)."""
import json, sys, urllib.request
from eth_hash.auto import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDR = "0x1A8Cc307006F9EC8600063ccf5915B6AD34348ef"
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

def dec_addr(out):
    if not isinstance(out, str) or not out.startswith("0x") or len(out) < 66:
        return None
    try:
        return "0x" + out[-40:]
    except Exception:
        return None

def dec_bool(out):
    v = dec_uint(out)
    return None if v is None else bool(v)

def enc_addr(a):
    return a[2:].lower().rjust(64, "0")

def enc_uint(n):
    return format(n, "064x")

U, S, A, B = "uint", "str", "addr", "bool"
VIEWS = [
    ("name", "name()", "", S),
    ("symbol", "symbol()", "", S),
    ("totalSupply", "totalSupply()", "", U),
    ("MAX_SUPPLY", "MAX_SUPPLY()", "", U),
    ("FREE_SUPPLY", "FREE_SUPPLY()", "", U),
    ("freeRemaining", "freeRemaining()", "", U),
    ("mintOpen", "mintOpen()", "", B),
    ("PAID_PRICE", "PAID_PRICE()", "", U),
    ("MAX_PER_WALLET", "MAX_PER_WALLET()", "", U),
    ("priceFor_user_1", "priceFor(address,uint256)", enc_addr(USER) + enc_uint(1), U),
    ("nextPrice_user", "nextPrice(address)", enc_addr(USER), U),
    ("paidMintedBy_user", "paidMintedBy(address)", enc_addr(USER), U),
    ("owner", "owner()", "", A),
    ("agentRegistry", "agentRegistry()", "", A),
    ("AGENT_ID_REGISTRY", "AGENT_ID_REGISTRY()", "", A),
    ("agentIdRegistry", "agentIdRegistry()", "", A),
]

out = {"address": ADDR, "sourcify": "exact_match 2026-11-07T18:34:05Z"}
for name, sig, args, typ in VIEWS:
    r = call(ADDR, sig, args)
    if typ == U:
        out[name] = dec_uint(r)
    elif typ == S:
        out[name] = dec_str(r)
    elif typ == A:
        out[name] = dec_addr(r)
    elif typ == B:
        out[name] = dec_bool(r)
    out[name + "_raw"] = r if (isinstance(r, str) and r.startswith("ERR")) else None

# first-mint block timestamp (dataseed, NOT Ankr)
blk = rpc_call("eth_getBlockByNumber", [hex(132254139), False], timeout=10)
if isinstance(blk, dict) and "timestamp" in blk:
    ts = int(blk["timestamp"], 16)
    out["first_block"] = 132254139
    out["first_mint_ts_unix"] = ts
    import datetime
    out["first_mint_wib"] = datetime.datetime.fromtimestamp(
        ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
else:
    out["first_block_ts_error"] = str(blk)[:200]

# owner vs same-owner-discards
disc = json.load(open(BASE + "/same-owner-discards.json"))
owners = {d.get("owner", "").lower() for d in disc if isinstance(d, dict)}
out["owner_in_discards"] = (out.get("owner") or "").lower() in owners if out.get("owner") else None
out["discards_count"] = len(owners)

print(json.dumps(out, indent=1))
with open(BASE + "/backfill-verify-132252508-132254477.json", "w") as f:
    json.dump(out, f, indent=1)
