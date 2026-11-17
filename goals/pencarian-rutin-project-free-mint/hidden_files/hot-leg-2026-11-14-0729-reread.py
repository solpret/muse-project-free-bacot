#!/usr/bin/env python3
"""0729 reread: single targeted re-read of the 6 PLAN entries that returned
all/partial None in the 0729 run (one RPC chunk likely failed). Read-only,
one batch, no retry loop. Distinguishes read failure from genuine change,
esp. binanceai pending-claim launched flag."""
import json, subprocess, time
from eth_hash.auto import keccak
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_PAD = USER[2:].lower().rjust(64, "0")
def sel(sig): return "0x" + keccak(sig.encode()).hex()[:8]
PLAN = [
 ("CRACE", "0x7B1ca439312368dE8652b9B5d7A54cA74A884680",
  [("freeMinted", False), ("FREE_QUOTA", False), ("mintOpen", False), ("totalSupply", False), ("freeClaimed", True)]),
 ("OLIVER", "0xad86e4d52e55709d1bda08f922853d4b109e0810",
  [("freeMinted", False), ("FREE_MAX", False), ("freeRemaining", False), ("mintOpen", False)]),
 ("binanceai-mint", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
  [("launched", False), ("failed", False), ("isRefundPhase", False), ("tokenClaimed", True)]),
 ("AngelEye-77D9", "0x77D98247BA3dDAfa9ffBceA1F13d3e4cFe3f2d4C",
  [("freeMinted", False), ("freeRemaining", False), ("FREE_POOL", False), ("saleActive", False), ("mintStart", False)]),
 ("AbsurdAgentNFT", "0x72c14121681F1133545947B0735563835CC07B67",
  [("totalMinted", False), ("mintOpen", False), ("mintStartTime", False)]),
 ("AZEN", "0x699b6397986cc6c444069efe692023b1253dc26d",
  [("totalSupply", False), ("MAX_SUPPLY", False), ("freeMintedPerWallet", True)]),
]
reqs, keys = [], []
for name, addr, views in PLAN:
    for fn, uarg in views:
        data = sel(fn + ("(address)" if uarg else "()")) + (USER_PAD if uarg else "")
        reqs.append({"jsonrpc": "2.0", "id": len(reqs), "method": "eth_call",
                     "params": [{"to": addr, "data": data}, "latest"]})
        keys.append((name, fn + ("_user" if uarg else "")))
body = subprocess.run(["curl","-sS","-m","60","-A","Mozilla/5.0","-H","Content-Type: application/json","-d",json.dumps(reqs),"https://bsc-dataseed.binance.org/"], capture_output=True, text=True, timeout=70).stdout
out = {"reread_wib": time.strftime("%Y-%m-%dT%H:%M:%S+07:00", time.gmtime(time.time()+7*3600)), "reads": {}}
try:
    resp = json.loads(body)
    items = resp if isinstance(resp, list) else [resp]
    by_id = {it.get("id"): it for it in items if isinstance(it, dict)}
    for cid, r in enumerate(reqs):
        name, fn = keys[cid]
        res = by_id.get(cid, {}).get("result")
        v = None
        if res and res != "0x" and len(res) >= 66:
            try: v = int(res[-64:], 16)
            except Exception: v = None
        out["reads"].setdefault(name, {})[fn] = v
except Exception as e:
    out["error"] = str(e)[:200]
print(json.dumps(out, indent=1))
json.dump(out, open("hot-leg-run-2026-11-14-0729-reread.json","w"), indent=1)
