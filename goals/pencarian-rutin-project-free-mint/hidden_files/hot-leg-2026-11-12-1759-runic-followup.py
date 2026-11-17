#!/usr/bin/env python3
"""Hot-leg 2026-11-12 1759 follow-up: targeted Runic Key re-read (leg 4 skipped it:
deadline-hit-skipped, RPC degraded). Single raced batch, read-only."""
import json, subprocess, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-12-1759"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDR = "0x0ec2c86B8E79c9A664b1ae0D6E3cB06B58ecCFe4"
T0 = time.time()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None

EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
def _post_one(ep, payload, timeout=12):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True, timeout=timeout + 5)
    return json.loads(r.stdout)
def post_rpc_race(payload, timeout=12):
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
         "FREE_CAP()", "MAX_SUPPLY()", "mintOpen()", "balanceOf(address)", "freeClaimed(address)",
         "freeUsed(address)", "mintedBy(address)", "saleStart()", "PRICE()", "price()",
         "freeRemaining()", "freeLeft()", "isFreeOpen()", "FREE_MODE()", "freeAvailable(address)",
         "launched()", "freeSharesRemaining()", "freeMintedBy(address)", "mintStart()"]
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
res = post_rpc_race(calls, timeout=12)
out = {"address": ADDR, "elapsed_s": round(time.time() - T0, 1)}
if res is None:
    out["views"] = None
else:
    views = {}
    for it, key in zip(res, keys):
        views[key] = None if (isinstance(it, dict) and "error" in it) else (
            to_int(it.get("result")) if isinstance(it, dict) else None)
    out["views"] = views
    out["summary"] = {k: v for k, v in views.items() if v is not None}
    fm = views.get("freeMinted"); fs = views.get("FREE_SUPPLY")
    if fm is not None and fs:
        out["free_pct"] = round(100.0 * fm / fs, 2)
json.dump(out, open(BASE + f"hot-leg-{TAG}-runic-followup.json", "w"), indent=1)
print(json.dumps(out, indent=1))
