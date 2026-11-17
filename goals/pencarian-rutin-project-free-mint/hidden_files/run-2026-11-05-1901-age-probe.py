#!/usr/bin/env python3
"""Age-sweep verification run 1901. Read-only."""
import json, urllib.request, datetime
from Crypto.Hash import keccak
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def raw(to, data):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=8) as r: out = json.load(r)
            if "error" in out: return None
            v = out["result"]
            if not v or v == "0x": return None
            return int(v, 16)
        except Exception:
            continue
    return None
def call(to, sig): return raw(to, sel(sig))
def block():
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=8) as r: return int(json.load(r)["result"], 16)
        except Exception: continue
    return None
now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7)))
print("NOW WIB:", now.strftime("%Y-%m-%d %H:%M:%S"))
blk = block()
print("BLOCK:", blk)
targets = {
 "Niubimind": ("0x4b178cB11fBF417803b6ABf525f14Bd7f8719C51", "2026-11-03T19:20:29+07:00", 5000),
 "Shogunode": ("0x20921b2B97090412a39c14B3A10C1E43b5d4aAAb", "2026-11-03T19:18:53+07:00", 3333),
 "Botkirin": ("0xe43818C2C6080E9d2bef53DB14092806B51711D2", "2026-11-03T19:09:40+07:00", 5000),
 "Pumpkinagent": ("0xC9BF67564043573A06685205C4c5296D7D37Bc74", "2026-11-03T19:34:09+07:00", 2222),
}
out = {"block": blk, "now_wib": now.strftime("%Y-%m-%d %H:%M:%S"), "reads": {}}
for name, (addr, fm, freecap) in targets.items():
    ts = call(addr, "totalSupply()")
    fc = call(addr, "freeClaimed()")
    fmint = call(addr, "freeMinted()")
    mo = call(addr, "mintOpen()")
    out["reads"][name] = {"address": addr, "firstMintWib": fm, "FREE_SUPPLY_snapshot": freecap,
                          "totalSupply": ts, "freeClaimed": fc, "freeMinted": fmint, "mintOpen": mo}
    print(name, out["reads"][name])
json.dump(out, open("run-2026-11-05-1901-age-probe.json", "w"), indent=1)
