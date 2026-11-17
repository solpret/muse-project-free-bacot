#!/usr/bin/env python3
"""Xigo track-C verification run 2231. Read-only. Uses _fast_single sequential
fallback like Leg 1 binanceai script."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single as _fast_single
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/",
       "https://rpc.ankr.com/bsc"]
DEADLINE = time.time() + 200
SALE = "0x796387D8106a2edb83e00c4f877e4358Ec721d49"
TOKEN = "0xbB30a6C4bafA060C586Eb13128F2250B6285F823"

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")
def raw(to, data):
    if time.time() > DEADLINE: return "deadline"
    for ep in EPS:
        try:
            v = _fast_single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0)
            if v is None or v == "0x": return None
            try: return int(v, 16)
            except Exception: return v
        except Exception:
            continue
    return None
def call(to, sig, args=""): return raw(to, sel(sig) + args)

blk = None
for ep in EPS:
    try:
        v = _fast_single(ep, "eth_blockNumber", [], 8, retries=0)
        if v: blk = int(v, 16); break
    except Exception: continue
print("head block:", blk, flush=True)
out = {"run": "2231", "block": blk, "sale": SALE, "token": TOKEN,
       "site": "https://xigo.shop/", "site_prints_contracts": True,
       "scheduled_start_utc": "2026-11-02T14:31:03Z",
       "scheduled_end_utc": "2026-11-05T14:31:03Z", "sale": {}}
s = out["sale"]
for sig, key in [("startTime()", "startTime"), ("endTime()", "endTime"),
                 ("totalShares()", "totalShares"), ("freeShares()", "freeShares"),
                 ("freeClaimedTotal()", "freeClaimedTotal"),
                 ("freeMinted()", "freeMinted"), ("paidOpen()", "paidOpen"),
                 ("launched()", "launched"), ("owner()", "owner")]:
    s[key] = call(SALE, sig)
for sig, key in [("freeAvailableFor(address)", "freeAvailableFor_user"),
                 ("freeClaimed(address)", "freeClaimed_user"),
                 ("minted(address)", "minted_user"),
                 ("mintableFor(address)", "mintableFor_user")]:
    s[key] = call(SALE, sig, enc(USER))
s["quote_1"] = call(SALE, "quote(uint256)", enc_uint(1))
out["token_totalSupply"] = call(TOKEN, "totalSupply()")
out["token_balance_user"] = call(TOKEN, "balanceOf(address)", enc(USER))
out["token_name"] = call(TOKEN, "name()")
out["token_symbol"] = call(TOKEN, "symbol()")
json.dump(out, open(f"{BASE}/run-2026-11-07-2231-xigo.json", "w"), indent=1)
print(json.dumps(out, indent=1), flush=True)
