#!/usr/bin/env python3
"""Re-probe 2 (14:14 run): same targets as reprobe.py but via fast_rpc endpoints
excluding bsc-dataseed.binance.org (now HTTP 403), using urllib batches."""
import json, sys, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from eth_hash.auto import keccak
import fast_rpc
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

EPS = [e for e in (fast_rpc.healthy_endpoints() or fast_rpc.ENDPOINTS)
       if "bsc-dataseed.binance.org" not in e]
def batch(calls, timeout=15):
    payload = [{"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                "params": [{"to": to, "data": data}, "latest"]}
               for i, (to, data) in enumerate(calls)]
    body = json.dumps(payload).encode()
    last = None
    for ep in EPS:
        try:
            req = urllib.request.Request(ep, data=body,
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                outp = json.loads(r.read().decode())
            res = []
            by_id = {it["id"]: it for it in outp if isinstance(it, dict)}
            for i in range(len(calls)):
                it = by_id.get(i + 1, {})
                if "result" in it and it["result"] not in (None, "0x"):
                    try: res.append(int(it["result"], 16))
                    except Exception: res.append(it["result"])
                else:
                    res.append(None)
            return res, ep
        except Exception as e:
            last = e
            continue
    raise IOError(f"all non-binance endpoints failed: {last}")

out, used = {}, None
for i in range(0, len(calls), 8):
    chunk = calls[i:i+8]
    res, used = batch(chunk)
    for (name, addr, label), val in zip(meta[i:i+8], res):
        out.setdefault(name, {"address": addr, "views": {}})["views"][label] = val
print("endpoint:", used)
print(json.dumps(out, indent=1))
json.dump(out, open(f"{HF}/hot-leg-2026-11-16-1414-reprobe2.json","w"), indent=1)
