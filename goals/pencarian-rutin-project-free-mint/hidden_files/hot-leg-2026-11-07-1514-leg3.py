#!/usr/bin/env python3
"""Leg 3 verification for the 2 new S1 contracts found via Boltbook in hot-leg run 2026-11-07 15:14 WIB.
Read-only on-chain reads. No preview, no mint, no snapshot writes."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single as _fast_single
from Crypto.Hash import keccak

USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDRS = [
    "0x001502c9ee19908f36db306da4dca7976db95bc4",
    "0xcbe2dbbff4264dc67bf557c64e29997b82439354",
]
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/",
       "https://rpc.ankr.com/bsc"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")

def call(to, data, timeout=8):
    for ep in EPS:
        try:
            v = _fast_single(ep, "eth_call", [{"to": to, "data": data}, "latest"], timeout, retries=0)
            if v is None or v == "0x":
                return None
            return v
        except Exception:
            continue
    return "transport-fail"

def call_int(to, sig, args=""):
    v = call(to, sel(sig) + args)
    if v is None or v == "transport-fail":
        return v
    try:
        return int(v, 16)
    except Exception:
        return v

def call_str(to, sig):
    v = call(to, sel(sig))
    if v is None or v == "transport-fail":
        return v
    try:
        raw = bytes.fromhex(v[2:])
        ln = int.from_bytes(raw[32:64], "big")
        return raw[64:64+ln].decode("utf-8", "replace")
    except Exception:
        return v

def call_tuple2(to, sig, args=""):
    v = call(to, sel(sig) + args)
    if v is None or v == "transport-fail":
        return v
    try:
        raw = bytes.fromhex(v[2:])
        return (int.from_bytes(raw[0:32], "big"), int.from_bytes(raw[32:64], "big"))
    except Exception:
        return v

def call_addr(to, sig):
    v = call(to, sel(sig))
    if isinstance(v, str) and v.startswith("0x") and len(v) == 66:
        return "0x" + v[-40:]
    return v

blk = None
for ep in EPS:
    try:
        blk = _fast_single(ep, "eth_blockNumber", [], 8, retries=0)
        if blk: blk = int(blk, 16); break
    except Exception:
        continue

out = {"block": blk, "contracts": {}}
for a in ADDRS:
    d = {
        "name": call_str(a, "name()"),
        "symbol": call_str(a, "symbol()"),
        "decimals": call_int(a, "decimals()"),
        "totalSupply": call_int(a, "totalSupply()"),
        "AGENT_ID_REGISTRY": call_addr(a, "AGENT_ID_REGISTRY()"),
        "agentIdRegistry": call_addr(a, "agentIdRegistry()"),
        "agentRegistry": call_addr(a, "agentRegistry()"),
        "FREE_PER_AGENT": call_int(a, "FREE_PER_AGENT()"),
        "FREE_AMOUNT": call_int(a, "FREE_AMOUNT()"),
        "FREE_SLOTS": call_int(a, "FREE_SLOTS()"),
        "FREE_SUPPLY": call_int(a, "FREE_SUPPLY()"),
        "MAX_SHARES": call_int(a, "MAX_SHARES()"),
        "MAX_MINTS": call_int(a, "MAX_MINTS()"),
        "sharesSold": call_int(a, "sharesSold()"),
        "totalMints": call_int(a, "totalMints()"),
        "totalMinted": call_int(a, "totalMinted()"),
        "freeSharesClaimed": call_int(a, "freeSharesClaimed()"),
        "freeClaimed": call_int(a, "freeClaimed()"),
        "freeMinted": call_int(a, "freeMinted()"),
        "freeSharesRemaining": call_int(a, "freeSharesRemaining()"),
        "mintOpen": call_int(a, "mintOpen()"),
        "TOKENS_PER_SHARE": call_int(a, "TOKENS_PER_SHARE()"),
        "MINT_AMOUNT": call_int(a, "MINT_AMOUNT()"),
        "PRICE_PER_SHARE": call_int(a, "PRICE_PER_SHARE()"),
        "AGENT_PRICE_PER_SHARE": call_int(a, "AGENT_PRICE_PER_SHARE()"),
        "PRICE": call_int(a, "PRICE()"),
        "MAX_PER_WALLET": call_int(a, "MAX_PER_WALLET()"),
        "MAX_PER_TX": call_int(a, "MAX_PER_TX()"),
        "totalRevenue": call_int(a, "totalRevenue()"),
        "treasury": call_addr(a, "treasury()"),
        "factory": call_addr(a, "FACTORY()"),
        "quote_user1": call_tuple2(a, "quote(address,uint256)", enc(USER) + enc_uint(1)),
        "freeUsed_user": call_int(a, "freeUsed(address)", enc(USER)),
        "freeLeft_user": call_int(a, "freeLeft(address)", enc(USER)),
        "mintedBy_user": call_int(a, "mintedBy(address)", enc(USER)),
        "balanceOf_user": call_int(a, "balanceOf(address)", enc(USER)),
        "isAgent_user": call_int(a, "isAgent(address)", enc(USER)),
    }
    out["contracts"][a] = d

json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-2026-11-07-1514-leg3.json", "w"), indent=1)
for a, d in out["contracts"].items():
    print(a, d["name"], d["symbol"], "| block", blk)
    for k, v in d.items():
        if v is not None and v != "transport-fail":
            print("   ", k, "=", v)
print("block", blk)
