#!/usr/bin/env python3
"""Hot-leg 1014 leg-4 completion: b777 + bounded snapshot re-read + isAgent/
quote re-check for the 3 new S1 + fresh sharesSold. Read-only; writes only
hot-leg-2026-11-07-1014-leg4.json. 3 RPCs, 2 attempts each, parallel."""
import json, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-07-1014"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
WIB = timezone(timedelta(hours=7))
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc-dataseed.binance.org",
        "https://bsc-dataseed2.bnbchain.org"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return "0"*24 + a[2:].lower()
def enc_u(n): return format(n, "064x")
def rpc_once(rpc, method, params, timeout=10):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r: return json.load(r)
def call(to, data):
    for rpc in RPCS:
        for _ in range(2):
            try:
                o = rpc_once(rpc, "eth_call", [{"to": to, "data": data}, "latest"])
                if "error" in o or not o.get("result") or o["result"] == "0x": continue
                v = o["result"]
                try: return int(v, 16)
                except Exception: return v
            except Exception: continue
    return "err:RPC"
def call_raw(to, data):
    for rpc in RPCS:
        for _ in range(2):
            try:
                o = rpc_once(rpc, "eth_call", [{"to": to, "data": data}, "latest"])
                if "error" in o or not o.get("result"): continue
                return o["result"]
            except Exception: continue
    return "err:RPC"
def block_number():
    for rpc in RPCS:
        try:
            o = rpc_once(rpc, "eth_blockNumber", [], 8)
            return int(o["result"], 16)
        except Exception: continue
    return None

UP = "0x" + "0"*24 + USER[2:].lower()
TASKS = {}
def add(tag, key, fn): TASKS[(tag, key)] = fn
ITEMS = {
 "b777": ("0x47529CF66091BeB0E8e0F78D5635e367473D52d5",
          ["totalMints()", "MAX_MINTS()", "mintOpen()", "FREE_PER_WALLET()", "MAX_PER_WALLET()"]),
 "KING Agent": ("0x2A2463d243E5c4dF850e48f350392AD23B494132",
                 ["totalMinted()", "remainingFree()", "freeQuota()", "mintOpen()"]),
 "MERGEBORN": ("0x348455be18b700cae8aa425bd84e456e47f16e8b",
               ["freeMinted()", "FREE_CAP()", "totalSupply()"]),
 "Wuyuhive": ("0x250e800025a9a7861970e253bab6975a57f80567",
              ["totalSupply()", "freeClaimed()", "freeMinted()", "FREE_SUPPLY()"]),
 "ChimpAgent": ("0x57D41Ff4895A19f518a0Ec3A2Fa56284a85f5689",
                ["totalSupply()", "totalMints()", "MAX_MINTS()", "mintOpen()"]),
 "Pacture": ("0x95AF9fe16fE5c1741b5E3F1b3b045a8c2470eca9",
             ["totalSupply()", "freeClaimed()", "freeMinted()", "FREE_SHARES()", "freeSharesRemaining()"]),
 "960E-sale": ("0x960E7e4126b97679053B8416fA59f13508be88bf",
               ["freeMinted()", "FREE_CAP()", "freeClaimed()", "totalShares()"]),
 "Tampesta": ("0x6aA51bd62C0c6B0bA206e25952F4063a7e0CCE79",
              ["totalSupply()", "freeMinted()", "FREE_SUPPLY()"]),
 "GLPX": ("0xba5cde0ceea8704b8944deb51228ca59a7bd9cf0", ["sharesSold()", "MAX_SHARES()"]),
 "PLNK": ("0xec266bdd979b19d8a2f1266ef0610b4791dbd24b", ["sharesSold()", "MAX_SHARES()"]),
}
for name, (addr, views) in ITEMS.items():
    for sig in views:
        add(name, sig.split("(")[0], (lambda s=sig, a=addr: call(a, sel(s))))
    add(name, "freeClaimed_user", (lambda a=addr: call(a, sel("freeClaimed(address)") + enc_addr(USER))))
NEW3 = {
 "CRBK": "0x38066aF063b6Eb0fBdF56e2D38eC265D9A79D996",
 "MZWK": "0x892E438425b3A41BC75b25C22Fd878b3fa2e308d",
 "KZMB": "0xBd6e4c6DEF0065007Bd163e4223Ae4f3aa3b6f09",
}
for name, addr in NEW3.items():
    add(name, "sharesSold", (lambda a=addr: call(a, sel("sharesSold()"))))
    add(name, "isAgent_user", (lambda a=addr: call(a, sel("isAgent(address)") + enc_addr(USER))))
    add(name, "freeUsed_user", (lambda a=addr: call(a, sel("freeUsed(address)") + enc_addr(USER))))
    add(name, "quote_user_1_raw", (lambda a=addr: call_raw(a, sel("quote(address,uint256)") + enc_addr(USER) + enc_u(1))))

out = {"run": TS, "t0_wib": datetime.now(WIB).isoformat(timespec="seconds"),
       "block": block_number()}
res = {}
t0 = time.time()
with ThreadPoolExecutor(max_workers=16) as ex:
    futs = {ex.submit(fn): k for k, fn in TASKS.items()}
    for f in as_completed(futs):
        tag, key = futs[f]
        try: res.setdefault(tag, {})[key] = f.result()
        except Exception as e: res.setdefault(tag, {})[key] = f"err:{type(e).__name__}"
out["reread"] = res
out["duration_s"] = round(time.time() - t0, 1)
for tag in res: print(tag, json.dumps(res[tag]), flush=True)
json.dump(out, open(f"{BASE}/hot-leg-{TS}-leg4.json", "w"), indent=1)
print("LEG4 DONE in", out["duration_s"], "s, block", out["block"], flush=True)
