#!/usr/bin/env python3
"""Re-read of leg4 items that returned null in hot-leg run 2026-11-16 11:54 WIB
(transient RPC read anomaly, same pattern as 11:49 run). Read-only.
Endpoint order: bsc-dataseed1.defibit.io first, then bsc-dataseed1.bnbchain.org."""
import json, sys, time, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from eth_hash.auto import keccak
T0 = time.time()

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.defibit.io/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]

def sel(sig):
    return keccak(sig.encode())[:4].hex()

def call(to, sig, arg=None):
    data = "0x" + sel(sig)
    if arg == "user":
        data += "0" * 24 + USER[2:].lower()
    return (to, data)

PLAN = [
 ("Matrix", "0x1F669b714337F3C2585072c53fdDD89581F928fF",
  [("freeMinted", "freeMinted()", None), ("freeRemaining", "freeRemaining()", None),
   ("totalSupply", "totalSupply()", None), ("mintOpen", "mintOpen()", None)]),
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
]
calls, meta = [], []
for name, addr, views in PLAN:
    for label, sig, arg in views:
        calls.append(call(addr, sig, arg))
        meta.append((name, addr, label))

def batch(calls, ep, timeout=15):
    payload = [{"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                "params": [{"to": to, "data": data}, "latest"]}
               for i, (to, data) in enumerate(calls)]
    req = urllib.request.Request(ep, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        out = json.loads(r.read().decode())
    by_id = {it["id"]: it for it in out if isinstance(it, dict)}
    res = []
    for i in range(len(calls)):
        it = by_id.get(i + 1, {})
        if "result" in it and it["result"] not in (None, "0x"):
            try:
                res.append(int(it["result"], 16))
            except Exception:
                res.append(it["result"])
        else:
            res.append(None)
    return res

out = {}
last_err = None
for ep in EPS:
    try:
        res = batch(calls, ep)
        if all(v is not None for v in res):
            out["endpoint"] = ep
            break
        out["endpoint"] = ep
        out["partial_nulls"] = sum(1 for v in res if v is None)
        last_err = "partial nulls"
        # keep trying next endpoint if many nulls remain
        if out["partial_nulls"] == 0:
            break
        continue
    except Exception as e:
        last_err = f"{type(e).__name__}: {str(e)[:120]}"
        continue
else:
    pass
if "endpoint" not in out:
    out["error"] = str(last_err)
reads = {}
for (name, addr, label), val in zip(meta, res if "res" in dir() else [None] * len(meta)):
    reads.setdefault(name, {"address": addr, "views": {}})["views"][label] = val
out["reads"] = reads
out["elapsed_s"] = round(time.time() - T0, 1)
json.dump(out, open(f"{HF}/hot-leg-2026-11-16-1154-reread-verify.json", "w"), indent=1)
print(json.dumps(out, indent=1))
