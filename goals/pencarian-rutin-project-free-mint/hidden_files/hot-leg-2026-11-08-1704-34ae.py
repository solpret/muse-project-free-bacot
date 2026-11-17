#!/usr/bin/env python3
"""Hot-leg 1704 leg3: re-check Kiko9393 sale 0x34aE861Fbeb2aaA6071248F8a27AcE5f30aA7bBf.
Watchlist-only (age unverified, zero mints at 16:59). Per-item eth_call so one
revert does not kill the batch. Read-only; no preview, no mint."""
import json, urllib.request, time
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDR = "0x34aE861Fbeb2aaA6071248F8a27AcE5f30aA7bBf"
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "hot-leg-2026-11-08-1704"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]
from Crypto.Hash import keccak

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try:
        return int(v, 16) if v and v != "0x" else None
    except Exception:
        return None

VIEWS = ["freeMinted()", "sharesMinted()", "paidShares()", "freeClaimed(address)",
         "hasMinted(address)", "quotaOf(address)", "freeAvailable()", "soldOut()",
         "closed()", "deployedAt()", "MAX_FREE()", "MAX_SHARES()", "quote(address,uint256)"]
def call(addr, views):
    calls, keys = [], []
    for i, sig in enumerate(views):
        base = sig.split("(")[0]
        if "(address" in sig and "(address,uint256)" not in sig:
            data = sel(sig) + enc(USER); key = base + "_user"
        elif "(address,uint256)" in sig:
            data = sel(sig) + enc(USER) + "0" * 63 + "1"; key = base + "_user1"
        else:
            data = sel(sig); key = base
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": data}, "latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            req = urllib.request.Request(ep, data=json.dumps(calls).encode(),
                headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=15) as r:
                out = json.load(r)
            if not isinstance(out, list) or len(out) != len(calls):
                continue
            res = {}
            for item, key in zip(out, keys):
                if isinstance(item, dict) and "result" in item:
                    res[key] = to_int(item.get("result"))
                else:
                    res[key] = "ERR " + str(item.get("error", {}).get("message", "?"))[:80]
            return res, ep
        except Exception:
            continue
    return None, None

r, ep = call(ADDR, VIEWS)
blk = None
for e in EPS:
    try:
        req = urllib.request.Request(e, data=json.dumps([{"jsonrpc": "2.0", "id": 1,
            "method": "eth_blockNumber", "params": []}]).encode(),
            headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            blk = int(json.load(resp)[0]["result"], 16); break
    except Exception:
        continue
out = {"addr": ADDR, "block": blk, "via": ep, "views": r,
       "wib": "2026-11-08T17:04:38+07:00"}
json.dump(out, open(BASE + TAG + "-34ae-recheck.json", "w"), indent=1)
print(json.dumps(out, indent=1))
