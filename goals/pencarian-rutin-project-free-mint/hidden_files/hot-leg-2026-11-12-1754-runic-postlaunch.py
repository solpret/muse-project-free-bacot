#!/usr/bin/env python3
"""Post-launch targeted re-read of Runic Key 0x0ec2 (saleStart 18:00:19 WIB).
Small-batch single-endpoint (the approach that worked at 17:44), one retry
on the second endpoint. Read-only."""
import json, subprocess, time
from Crypto.Hash import keccak
ADDR = "0x0ec2c86B8E79c9A664b1ae0D6E3cB06B58ecCFe4"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
VIEWS = ["name()", "totalSupply()", "totalMinted()", "freeMinted()", "FREE_SUPPLY()",
         "MAX_SUPPLY()", "mintOpen()", "isFreeOpen()", "FREE_MODE()", "freeRemaining()",
         "freeAvailable(address)", "balanceOf(address)", "freeClaimed(address)",
         "saleStart()", "saleEnd()", "PRICE()"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
calls, keys = [], []
for i, sig in enumerate(VIEWS):
    base = sig.split("(")[0]
    if "(address)" in sig:
        data = sel(sig) + enc(USER); key = base + "_user"
    else:
        data = sel(sig); key = base
    calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                  "params": [{"to": ADDR, "data": data}, "latest"]})
    keys.append(key)
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
res = None
for ep in ("https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"):
    try:
        r = subprocess.run(["curl", "-sL", "--max-time", "15", "-X", "POST", ep,
                            "-H", "Content-Type: application/json", "-d", json.dumps(calls)],
                           capture_output=True, text=True, timeout=20)
        j = json.loads(r.stdout)
        if isinstance(j, list) and len(j) == len(calls):
            res = {k: (None if (isinstance(it, dict) and "error" in it)
                       else (to_int(it.get("result")) if isinstance(it, dict) else None))
                   for it, k in zip(j, keys)}
            print("endpoint OK:", ep); break
    except Exception as e:
        print("endpoint fail:", ep, str(e)[:100])
print(json.dumps(res, indent=1))
# block number
try:
    r = subprocess.run(["curl", "-sL", "--max-time", "10", "-X", "POST", "https://bsc-dataseed.binance.org/",
                        "-H", "Content-Type: application/json",
                        "-d", json.dumps([{"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}])],
                       capture_output=True, text=True, timeout=15)
    print("block:", int(json.loads(r.stdout)[0]["result"], 16))
except Exception as e:
    print("block fail:", e)
json.dump({"ts_wib": time.strftime("%Y-%m-%dT%H:%M:%S+07:00", time.gmtime(time.time()+7*3600)),
           "views": res}, open("hot-leg-2026-11-12-1754-runic-postlaunch.json", "w"), indent=1)
