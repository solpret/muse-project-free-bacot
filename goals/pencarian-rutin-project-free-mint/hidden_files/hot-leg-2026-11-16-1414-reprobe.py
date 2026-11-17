#!/usr/bin/env python3
"""Re-probe leg-4 entries that returned None in the 14:14 run (AGCLUB, REOPIR,
RAVE, MORFO all-None; Matrix + binanceai-mint partial) via direct curl batches,
to distinguish RPC read failure from real state change."""
import json, subprocess, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from eth_hash.auto import keccak
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(sig): return keccak(sig.encode())[:4].hex()
def enc_addr(a): return "0"*24 + a[2:].lower()
def call(to, sig, arg=None):
    d = "0x" + sel(sig)
    if arg == "user": d += enc_addr(USER)
    return (to, d)
PLAN = [
 ("AGCLUB", "0x67270bb351515abf3089ca5420456897363f5e75",
  [("totalMinted", "totalMinted()", None), ("freeMinted", "freeMinted()", None),
   ("FREE_CAP", "FREE_CAP()", None), ("mintOpen", "mintOpen()", None),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("REOPIR", "0x12f65bc14037ccdf3f97afc0e67a0e4aca3cf5b9",
  [("freeClaimed", "freeClaimed()", None), ("totalSupply", "totalSupply()", None),
   ("mintOpen", "mintOpen()", None)]),
 ("RAVE", "0x7c40B78992d86EDfFB5553C74dB5EF427100bb95",
  [("totalMinted", "totalMinted()", None), ("freeMinted", "freeMinted()", None),
   ("mintOpen", "mintOpen()", None)]),
 ("MORFO", "0xb22ac9b2ac90e77f342cba2cc38b28eb8c718186",
  [("totalMinted", "totalMinted()", None), ("mintOpen", "mintOpen()", None)]),
 ("Matrix", "0x1F669b714337F3C2585072c53fdDD89581F928fF",
  [("freeMinted", "freeMinted()", None), ("freeRemaining", "freeRemaining()", None),
   ("totalSupply", "totalSupply()", None), ("mintOpen", "mintOpen()", None)]),
 ("binanceai-mint", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
  [("launched", "launched()", None), ("failed", "failed()", None),
   ("isRefundPhase", "isRefundPhase()", None), ("totalShares", "totalShares()", None),
   ("tokenClaimed_user", "tokenClaimed(address)", "user")]),
]
calls, meta = [], []
for name, addr, views in PLAN:
    for label, sig, arg in views:
        calls.append(call(addr, sig, arg)); meta.append((name, addr, label))
out = {}
for i in range(0, len(calls), 5):
    chunk = calls[i:i+5]
    payload = [{"jsonrpc":"2.0","id":j+1,"method":"eth_call",
                "params":[{"to":to,"data":data},"latest"]}
               for j,(to,data) in enumerate(chunk)]
    r = subprocess.run(["curl","-s","--max-time","20","https://bsc-dataseed.binance.org/",
                        "-H","Content-Type: application/json","-d",json.dumps(payload)],
                       capture_output=True, timeout=25)
    resp = json.loads(r.stdout.decode())
    by_id = {it["id"]: it for it in resp if isinstance(it, dict)}
    for j in range(len(chunk)):
        it = by_id.get(j+1, {})
        name, addr, label = meta[i+j]
        val = None
        if "result" in it and it["result"] not in (None, "0x"):
            try: val = int(it["result"], 16)
            except Exception: val = it["result"]
        out.setdefault(name, {"address": addr, "views": {}})["views"][label] = val
print(json.dumps(out, indent=1))
json.dump(out, open(f"{HF}/hot-leg-2026-11-16-1414-reprobe.json","w"), indent=1)
