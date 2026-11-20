#!/usr/bin/env python3
"""Retry for main run 2026-11-19 06:31 WIB — single eth_call via urllib, rotating
endpoints (fast_rpc.batch is 429 right now; hot-leg pattern: small direct batches).
Read-only. Failed read stays None, never 0.
"""
import json, time, urllib.request
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_PAD = "0x" + "00" * 12 + USER[2:].lower()
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-rpc.publicnode.com/"]

def sel(sig):
    h = keccak.new(digest_bits=256)
    h.update(sig.encode())
    return "0x" + h.hexdigest()[:8]

def eth_call(ep, to, data, timeout=12):
    req = urllib.request.Request(ep, data=json.dumps(
        {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
         "params": [{"to": to, "data": data}, "latest"]}).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        j = json.load(r)
        if "result" in j and j["result"]:
            return int(j["result"], 16)
        return None

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

t0 = time.time()
out = {"run": "free-mint-search 2026-11-19 06:31 WIB (retry single-call)", "reads": {}}
ep_i = 0
for name, (addr, views) in ITEMS.items():
    for v in views:
        key, sig = v[0], v[1]
        data = sel(sig)
        if len(v) > 2 and v[2] == "user":
            data += USER_PAD[2:]
        val, err = None, None
        for attempt in range(3):
            ep = EPS[(ep_i + attempt) % len(EPS)]
            try:
                val = eth_call(ep, addr, data)
                ep_i += 1
                break
            except Exception as e:
                err = f"{type(e).__name__}: {e}"
                time.sleep(1.5)
        out["reads"].setdefault(name, {})[key] = val
        if val is None:
            out["reads"][name][key + "_error"] = err
        time.sleep(0.3)

out["elapsed_s"] = round(time.time() - t0, 1)
# block
for ep in EPS:
    try:
        req = urllib.request.Request(ep, data=json.dumps(
            {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode(),
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as r:
            out["block"] = int(json.load(r)["result"], 16)
            out["block_endpoint"] = ep
            break
    except Exception:
        continue

print(json.dumps(out, indent=1))
json.dump(out, open(BASE + "main-run-2026-11-19-0631-reread.json", "w"), indent=1)
