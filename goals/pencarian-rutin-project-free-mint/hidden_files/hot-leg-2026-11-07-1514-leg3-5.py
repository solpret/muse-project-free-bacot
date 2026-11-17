#!/usr/bin/env python3
"""Leg 3 verification for the 5 new S1 contracts found in hot-leg run 2026-11-07 15:04 WIB.
Read-only on-chain reads. No preview, no mint, no snapshot writes."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single as _fast_single
from Crypto.Hash import keccak

USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDRS = [
    "0x8717fc8751b8Ebd6832EA145974AA77D86bE9EaD",
    "0xe8b5E3ca9f4F51366f9f4860ed70b8e929e80470",
    "0x16A8aFdc97F8Cf48617bF15E47b4dA2217ea04A5",
    "0xab3F2dA0b63F5A823510095263789E9e6F26329a",
    "0x2a71CEF7101B8b19c4ab18BeD40C3ec5EC87B9b7",
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
        # string ABI: offset(32) + len(32) + data
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
        "AGENT_ID_REGISTRY": call(a, sel("AGENT_ID_REGISTRY()")),
        "FREE_PER_AGENT": call_int(a, "FREE_PER_AGENT()"),
        "MAX_SHARES": call_int(a, "MAX_SHARES()"),
        "sharesSold": call_int(a, "sharesSold()"),
        "freeSharesClaimed": call_int(a, "freeSharesClaimed()"),
        "TOKENS_PER_SHARE": call_int(a, "TOKENS_PER_SHARE()"),
        "PRICE_PER_SHARE": call_int(a, "PRICE_PER_SHARE()"),
        "AGENT_PRICE_PER_SHARE": call_int(a, "AGENT_PRICE_PER_SHARE()"),
        "MAX_PER_WALLET": call_int(a, "MAX_PER_WALLET()"),
        "MAX_PER_TX": call_int(a, "MAX_PER_TX()"),
        "totalRevenue": call_int(a, "totalRevenue()"),
        "treasury": call(a, sel("treasury()")),
        "quote_user1": call_tuple2(a, "quote(address,uint256)", enc(USER) + enc_uint(1)),
        "freeUsed_user": call_int(a, "freeUsed(address)", enc(USER)),
        "mintedBy_user": call_int(a, "mintedBy(address)", enc(USER)),
        "balanceOf_user": call_int(a, "balanceOf(address)", enc(USER)),
        "isAgent_user": call_int(a, "isAgent(address)", enc(USER)),
    }
    # normalize address results
    for k in ("AGENT_ID_REGISTRY", "treasury"):
        v = d[k]
        if isinstance(v, str) and v.startswith("0x") and len(v) == 66:
            d[k] = "0x" + v[-40:]
    out["contracts"][a] = d

json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-2026-11-07-1514-leg3-5.json", "w"), indent=1)
for a, d in out["contracts"].items():
    q = d["quote_user1"]
    print(a, d["name"], d["symbol"], "| FREE_PER_AGENT", d["FREE_PER_AGENT"], "MAX_SHARES", d["MAX_SHARES"],
          "sharesSold", d["sharesSold"], "freeClaimed", d["freeSharesClaimed"],
          "quote(user,1)", q, "freeUsed(user)", d["freeUsed_user"], "mintedBy(user)", d["mintedBy_user"],
          "bal(user)", d["balanceOf_user"], "isAgent(user)", d["isAgent_user"],
          "registry", d["AGENT_ID_REGISTRY"], "treasury", d["treasury"],
          "TOKENS/SHARE", d["TOKENS_PER_SHARE"], "PRICE", d["PRICE_PER_SHARE"], "AGENT_PRICE", d["AGENT_PRICE_PER_SHARE"])
print("block", blk)
