#!/usr/bin/env python3
"""Hot-leg 1704 leg3: verify new S1 sale-shape 0x7D08289E962f5aEc00d56D67322eb2FD056B687c
(fresh from Sourcify feed, not in main snapshot) + re-check Kiko9393 0x34aE...
Per-item eth_call so one revert does not kill the batch. Read-only; no preview, no mint."""
import json, urllib.request
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
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

def call(addr, views):
    calls, keys = [], []
    for i, sig in enumerate(views):
        base = sig.split("(")[0]
        if "(address,uint256)" in sig:
            data = sel(sig) + enc(USER) + "0" * 63 + "1"; key = base + "_user1"
        elif "(address" in sig:
            data = sel(sig) + enc(USER); key = base + "_user"
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

def head_block():
    for e in EPS:
        try:
            req = urllib.request.Request(e, data=json.dumps([{"jsonrpc": "2.0", "id": 1,
                "method": "eth_blockNumber", "params": []}]).encode(),
                headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=10) as resp:
                return int(json.load(resp)[0]["result"], 16)
        except Exception:
            continue
    return None

VIEWS_7D08 = ["freeMinted()", "MAX_FREE()", "MAX_SHARES()", "sharesMinted()",
              "paidShares()", "freeAvailable()", "freeClaimed(address)",
              "hasMinted(address)", "quotaOf(address)", "quote(address,uint256)",
              "soldOut()", "closed()", "deployedAt()", "windDownAt()",
              "token()", "agentId()", "PRICE()", "TOKENS_PER_SHARE()"]
VIEWS_34AE = ["freeMinted()", "sharesMinted()", "paidShares()", "freeClaimed(address)",
              "hasMinted(address)", "quotaOf(address)", "freeAvailable()", "soldOut()",
              "closed()", "deployedAt()", "MAX_FREE()", "MAX_SHARES()", "quote(address,uint256)"]
blk = head_block()
r7, ep7 = call("0x7D08289E962f5aEc00d56D67322eb2FD056B687c", VIEWS_7D08)
r34, ep34 = call("0x34aE861Fbeb2aaA6071248F8a27AcE5f30aA7bBf", VIEWS_34AE)
out = {"block": blk, "wib": "2026-11-08T17:04:38+07:00",
       "new_7d08": {"addr": "0x7D08289E962f5aEc00d56D67322eb2FD056B687c", "via": ep7, "views": r7},
       "kiko9393_34ae": {"addr": "0x34aE861Fbeb2aaA6071248F8a27AcE5f30aA7bBf", "via": ep34, "views": r34}}
json.dump(out, open(BASE + TAG + "-leg3.json", "w"), indent=1)
print(json.dumps(out, indent=1))
