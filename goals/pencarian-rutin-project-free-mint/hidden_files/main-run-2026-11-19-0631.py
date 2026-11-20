#!/usr/bin/env python3
"""Main run free-mint-search 2026-11-19 06:31 WIB — route-1 re-read (read-only).
Batch eth_call reads for the operative watchlist + Kigae (new Boltbook lead)
+ binanceai.fun pending claim. No preview/mint. A failed read is None, never 0.
"""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from Crypto.Hash import keccak
from fast_rpc import batch as _batch

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_PAD = "0x" + "00" * 12 + USER[2:].lower()

def sel(sig):
    h = keccak.new(digest_bits=256)
    h.update(sig.encode())
    return "0x" + h.hexdigest()[:8]

def call(to, sig, arg=None):
    data = sel(sig)
    if arg == "user":
        data += USER_PAD[2:]
    return {"to": to, "data": data}

ITEMS = {
    "HIVE Agents": ("0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77",
                    [("totalSupply", "totalSupply()"), ("balanceOf_user", "balanceOf(address)", "user")]),
    "Bubblebruin": ("0xc205F8c74733D914776D66cBc4Cf10BF701D96Aa",
                    [("totalSupply", "totalSupply()"), ("freeClaimed", "freeClaimed()"),
                     ("balanceOf_user", "balanceOf(address)", "user")]),
    "STOCK AGENT": ("0xba7068233da805bdebcc167be361c219002e6b7f",
                    [("totalSupply", "totalSupply()"), ("freeLeft", "freeLeft()"),
                     ("FREE_SUPPLY", "FREE_SUPPLY()"), ("MAX_SUPPLY", "MAX_SUPPLY()"),
                     ("balanceOf_user", "balanceOf(address)", "user")]),
    "Lumenhold": ("0x9701980b0afd825134390ee46fb3bd675a2f356f",
                  [("totalSupply", "totalSupply()"), ("freeClaimed", "freeClaimed()"),
                   ("FREE_SUPPLY", "FREE_SUPPLY()"), ("MAX_SUPPLY", "MAX_SUPPLY()"),
                   ("balanceOf_user", "balanceOf(address)", "user")]),
    "AGATE-Pass": ("0x5b63bd45e61a2e6540548c3509b598b6384206c5",
                   [("totalSupply", "totalSupply()"), ("MAX_SUPPLY", "MAX_SUPPLY()"),
                    ("balanceOf_user", "balanceOf(address)", "user")]),
    "ARKYN": ("0x69b0b5756671680766d232eb4b0f39a34be5d852",
              [("totalSupply", "totalSupply()"), ("MAX_SUPPLY", "MAX_SUPPLY()"),
               ("balanceOf_user", "balanceOf(address)", "user")]),
    "Kigae": ("0x33fd00af8bff3db611d3222d394da33eaaa6a566",
              [("totalSupply", "totalSupply()"), ("freeMinted", "freeMinted()"),
               ("FREE_SUPPLY", "FREE_SUPPLY()"), ("freeLeft", "freeLeft()"),
               ("MAX_SUPPLY", "MAX_SUPPLY()"), ("balanceOf_user", "balanceOf(address)", "user")]),
    "binanceai-mint": ("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
                       [("launched", "launched()"), ("failed", "failed()"),
                        ("isRefundPhase", "isRefundPhase()"),
                        ("tokenClaimed_user", "tokenClaimed(address)", "user"),
                        ("totalShares", "totalShares()")]),
}

calls, meta = [], []
for name, (addr, views) in ITEMS.items():
    for v in views:
        key, sig = v[0], v[1]
        arg = v[2] if len(v) > 2 else None
        calls.append(call(addr, sig, arg))
        meta.append((name, key))

t0 = time.time()
try:
    results = _batch(calls, timeout=10)
except Exception as e:
    results = [None] * len(calls)
    print("batch error:", e, file=sys.stderr)

out = {"run": "free-mint-search 2026-11-19 06:31 WIB", "elapsed_s": round(time.time() - t0, 1), "reads": {}}
for (name, key), res in zip(meta, results):
    val = None
    if res:
        try:
            val = int(res, 16)
        except Exception:
            val = res
    out["reads"].setdefault(name, {})[key] = val

# current block
out["block"] = None
# eth_blockNumber via direct urllib
import urllib.request
for ep in ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
           "https://bsc-rpc.publicnode.com/"]:
    try:
        req = urllib.request.Request(ep, data=json.dumps(
            {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode(),
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as r:
            out["block"] = int(json.load(r)["result"], 16)
            out["block_endpoint"] = ep
            break
    except Exception as e:
        out.setdefault("block_errors", []).append(f"{ep}: {e}")

print(json.dumps(out, indent=1))
json.dump(out, open(BASE + "main-run-2026-11-19-0631-reread.json", "w"), indent=1)
