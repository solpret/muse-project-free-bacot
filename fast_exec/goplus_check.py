#!/usr/bin/env python3
"""GoPlus token_security for BSC (chain 56), free, no key. Read-only.
Usage: goplus_check.py <addr> [<addr> ...]
Prints one JSON object per token with the fields screening gates use,
plus null-handling notes. urllib honors the sandbox proxy env vars."""
import json, sys, urllib.request

URL = "https://api.gopluslabs.io/api/v1/token_security/56?contract_addresses="
FLAGS = ["is_honeypot", "is_open_source", "is_proxy", "is_mintable", "hidden_owner",
         "can_take_back_ownership", "transfer_pausable", "is_blacklisted", "selfdestruct",
         "cannot_buy", "cannot_sell_all", "is_anti_whale", "anti_whale_modifiable",
         "slippage_modifiable", "trading_cooldown", "personal_slippage_modifiable"]
TAXES = ["buy_tax", "sell_tax"]

def fetch(addrs):
    req = urllib.request.Request(URL + ",".join(a.lower() for a in addrs),
                                 headers={"User-Agent": "Muse-screening/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)

def summarize(addr, res):
    out = {"address": addr}
    for k in FLAGS:
        out[k] = res.get(k)
    for k in TAXES:
        out[k] = res.get(k)
    out["holder_count"] = res.get("holder_count")
    holders = res.get("holders") or []
    top10 = sum(float(h.get("percent") or 0) for h in holders[:10])
    burn = sum(float(h.get("percent") or 0) for h in holders
               if h.get("address") in ("0x000000000000000000000000000000000000dead",
                                       "0x0000000000000000000000000000000000000000"))
    out["top10_percent"] = round(top10, 4)
    out["burn_percent"] = round(burn, 4)
    out["top10_ex_burn_percent"] = round(top10 - burn, 4)
    lp = res.get("lp_holders") or []
    out["lp_burn_percent"] = round(sum(float(h.get("percent") or 0) for h in lp if h.get("is_locked") == 1), 4) if lp else None
    out["dex"] = [{"name": d.get("name"), "pair": d.get("pair"), "liquidity": d.get("liquidity")}
                  for d in (res.get("dex") or [])]
    out["creator"] = res.get("creator_address")
    out["notes"] = []
    if res.get("is_open_source") == "0":
        out["notes"].append("closed source: other risk fields are null by GoPlus design, do not read as safe")
    if res.get("is_proxy") == "1":
        out["notes"].append("proxy: honeypot field may be null; upgrade risk applies")
    if not res.get("buy_tax") and not res.get("sell_tax"):
        out["notes"].append("tax fields empty: no simulated trade available, tax UNVERIFIED (never read as 0)")
    return out

if __name__ == "__main__":
    addrs = sys.argv[1:]
    if not addrs:
        print("usage: goplus_check.py <bsc-address> [...]"); sys.exit(2)
    data = fetch(addrs)
    if data.get("code") != 1:
        print("GoPlus error:", data); sys.exit(1)
    for a in addrs:
        res = (data.get("result") or {}).get(a.lower())
        if res is None:
            print(json.dumps({"address": a, "error": "no result (unknown contract or unsupported)"}))
        else:
            print(json.dumps(summarize(a, res), indent=1))
