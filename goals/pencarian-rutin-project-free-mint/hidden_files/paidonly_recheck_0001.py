#!/usr/bin/env python3
"""Paid-only re-check, run 0001 (2026-11-06 00:01 WIB). Read-only.
The PRICKLY correction proved price()=0.0002 BNB does NOT mean paid-only:
the template's first mint is free via costOf(user,1)=0. Re-check every
watchlist-only-paid-only-2026-11-05 contract with the template views:
owner(), costOf(user,1), mintsLeft(user), mintedBy(user), totalSupply().
A reverted/absent view is None, never zero."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from eth_hash.auto import keccak

USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def call(addr, data, timeout=7):
    last = None
    for ep in EPS:
        try:
            return _single(ep, "eth_call", [{"to": addr, "data": data}, "latest"], timeout, retries=0)
        except Exception as e:
            last = e
    return {"_error": str(last)[:100]}

def dec_uint(out):
    if not isinstance(out, str) or not out.startswith("0x") or len(out) < 66:
        return None
    try:
        return int(out[2:66], 16)
    except Exception:
        return None

def dec_addr(out):
    if not isinstance(out, str) or len(out) < 66:
        return None
    return "0x" + out[26:66]

def main():
    snap = json.load(open("onchain-snapshot.json"))
    paid = [(k, v) for k, v in snap["contracts"].items()
            if v.get("status") == "watchlist-only-paid-only-2026-11-05"]
    try:
        blk = None
        for ep in EPS:
            try:
                blk = int(_single(ep, "eth_blockNumber", [], 7, retries=0), 16)
                break
            except Exception:
                continue
    except Exception:
        blk = None
    print("read block:", blk)
    out = {"block": blk, "results": {}}
    ua = "000000000000000000000000" + USER[2:].lower()
    for label, v in paid:
        addr = v.get("address")
        r = {"address": addr}
        r["owner"] = dec_addr(call(addr, sel("owner()")))
        r["costOf_user_1"] = dec_uint(call(addr, sel("costOf(address,uint256)") + ua + format(1, "064x")))
        r["mintsLeft_user"] = dec_uint(call(addr, sel("mintsLeft(address)") + ua))
        r["mintedBy_user"] = dec_uint(call(addr, sel("mintedBy(address)") + ua))
        r["totalSupply"] = dec_uint(call(addr, sel("totalSupply()")))
        out["results"][label] = r
        print(f"{label}: owner={r['owner']} costOf(user,1)={r['costOf_user_1']} mintsLeft={r['mintsLeft_user']} mintedBy={r['mintedBy_user']} totalSupply={r['totalSupply']}")
    json.dump(out, open("paidonly-recheck-2026-11-06-0001.json", "w"), indent=1)
    print("wrote paidonly-recheck-2026-11-06-0001.json")

if __name__ == "__main__":
    main()
