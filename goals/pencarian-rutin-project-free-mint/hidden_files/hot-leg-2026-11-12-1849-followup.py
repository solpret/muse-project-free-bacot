#!/usr/bin/env python3
"""Hot-leg 1849 follow-up: one quick retry of RunicKey + Stampooor only (front items).
Raced batch, 2 endpoints, hard 60s budget. Read-only."""
import json, subprocess, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-12-1849"
T0 = time.time()
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
def _post_one(ep, payload, timeout=10):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True, timeout=timeout + 5)
    return json.loads(r.stdout)
def post_rpc_race(payload, timeout=10):
    with ThreadPoolExecutor(max_workers=2) as ex:
        futs = {ex.submit(_post_one, ep, payload, timeout): ep for ep in EPS}
        for fut in as_completed(futs):
            try:
                res = fut.result()
                if isinstance(res, list) and len(res) == len(payload):
                    return res
            except Exception:
                continue
    return None
VIEWS = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "FREE_SUPPLY()",
         "MAX_SUPPLY()", "mintOpen()", "balanceOf(address)", "freeClaimed(address)",
         "freeAvailable(address)", "freeMintedBy(address)"]
def raw_batch(addr, views):
    calls, keys = [], []
    for i, sig in enumerate(views):
        base = sig.split("(")[0]
        if "(address)" in sig:
            data = sel(sig) + enc(USER); key = base + "_user"
        else:
            data = sel(sig); key = base
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": data}, "latest"]})
        keys.append(key)
    res = post_rpc_race(calls, timeout=10)
    if res is None: return None
    return {key: (None if (isinstance(it, dict) and "error" in it)
                  else (to_int(it.get("result")) if isinstance(it, dict) else None))
            for it, key in zip(res, keys)}
out = {}
for name, addr in [("RunicKey", "0x0ec2c86B8E79c9A664b1ae0D6E3cB06B58ecCFe4"),
                   ("Stampooor", "0x467696af8c2206B977B24081445104632dc1D459")]:
    if time.time() - T0 > 55:
        out[name] = {"error": "deadline-skipped"}; continue
    r = raw_batch(addr, VIEWS)
    out[name] = {"address": addr, "views": r,
                 "summary": {k: v for k, v in r.items() if v is not None} if r else None}
out["elapsed_s"] = round(time.time() - T0, 1)
json.dump(out, open(BASE + f"hot-leg-{TAG}-followup.json", "w"), indent=1)
print(json.dumps(out, indent=1))
