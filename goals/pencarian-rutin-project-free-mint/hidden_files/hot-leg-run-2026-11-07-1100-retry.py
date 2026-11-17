#!/usr/bin/env python3
"""Focused retry for leg-4 items that hit the 90s deadline in hot-leg run 2026-11-07-1100.
Read-only eth_calls; 8 priority items only (AGENT GOATS + Alchemister + Sage Trials + 5 newest track-C leads).
Never writes the main snapshot."""
import json, time
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-07-1100"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com",
        "https://bsc-dataseed.binance.org", "https://rpc.ankr.com/bsc",
        "https://bsc-dataseed-public.bnbchain.org"]
t0 = time.time()
DEADLINE = t0 + 60

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")

def raw(to, data):
    for rpc in RPCS:
        if time.time() > DEADLINE:
            return "deadline"
        try:
            import urllib.request
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as r:
                o = json.load(r)
            if "error" in o:
                continue
            v = o.get("result")
            if not v or v == "0x":
                return None
            try:
                return int(v, 16)
            except Exception:
                return v
        except Exception:
            continue
    return None

def call(to, sig, args=""): return raw(to, sel(sig) + args)

def rpc_block():
    for rpc in RPCS:
        try:
            import urllib.request
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=4) as r:
                o = json.load(r)
            if "error" not in o:
                return int(o["result"], 16), rpc
        except Exception:
            continue
    return None, None

blk, blk_rpc = rpc_block()

NFT_VIEWS = ["totalSupply()", "freeClaimed()", "freeMinted()", "FREE_SUPPLY()",
             "balanceOf(address)", "mintedBy(address)", "freeUsed(address)",
             "claimedFree(address)", "mintOpen()"]
SALE_VIEWS = ["freeClaimed()", "freeSharesRemaining()", "freeLeft(address)",
              "quote(address,uint256)", "mintedBy(address)", "mintOpen()",
              "totalMinted()", "freeMinted()", "totalSupply()"]
ITEMS = {
 "Agent Goats": ("0x0E9E0a3B46dC0d36A1Ab64f553Dd8A0693E6aAa6", NFT_VIEWS),
 "Alchemister": ("0x69037Db8C6f237eCd9aB4B364D65C6dD05825dCb", NFT_VIEWS),
 "Sage Trials": ("0xB0d58925E1075c4E4C02B72f4Bbb3656A6f0b3A3", NFT_VIEWS),
 "GlorpixAgent": ("0xba5cde0ceea8704b8944deb51228ca59a7bd9cf0", SALE_VIEWS),
 "PlonkraAgent": ("0xec266bdd979b19d8a2f1266ef0610b4791dbd24b", SALE_VIEWS),
 "CrumborkAgent": ("0x38066aF063b6Eb0fBdF56e2D38eC265D9A79D996", SALE_VIEWS),
 "MizzlewickAgent": ("0x892E438425b3A41BC75b25C22Fd878b3fa2e308d", SALE_VIEWS),
 "KazoombaAgent": ("0xBd6e4c6DEF0065007Bd163e4223Ae4f3aa3b6f09", SALE_VIEWS),
}
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))

def read_item(args):
    name, (addr, views) = args
    d = {"address": addr}
    for sig in views:
        key = sig.split("(")[0]
        if sig.startswith("quote("):
            v = call(addr, sig, enc(USER) + enc_uint(1)); key += "_user1"
        elif "address" in sig:
            v = call(addr, sig, enc(USER)); key += "_user"
        else:
            v = call(addr, sig)
        d[key] = v
    snap_v = snap.get("contracts", {}).get(name, {}) or snap.get("track_c", {}).get(name, {})
    d["snap"] = {k: snap_v.get(k) for k in ("freeClaimed", "FREE_SUPPLY", "freeSupply", "totalSupply", "status", "freeMinted", "totalMinted") if isinstance(snap_v, dict) and snap_v.get(k) is not None}
    return name, d

with ThreadPoolExecutor(max_workers=8) as ex:
    items = dict(ex.map(read_item, list(ITEMS.items())))
out = {"retry_of": "hot-leg-run-2026-11-07-1100 leg4 deadline-missed items",
       "block": blk, "via": blk_rpc, "items": items, "duration_s": round(time.time() - t0, 1)}
json.dump(out, open(f"{BASE}/hot-leg-{TS}-reread-retry.json", "w"), indent=1)
print(json.dumps(out, indent=1))
