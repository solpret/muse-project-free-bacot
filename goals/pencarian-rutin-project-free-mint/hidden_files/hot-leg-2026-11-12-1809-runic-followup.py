#!/usr/bin/env python3
"""Runic Key 0x0ec2... targeted follow-up, hot-leg run 2026-11-12 18:09 WIB.
Leg 4 deadline-skipped it; re-read fresh (read-only)."""
import json, subprocess, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-12-1809"
now_wib = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
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
    res = post_rpc_race(calls, timeout=12)
    if res is None:
        return None
    return {key: (None if (isinstance(it, dict) and "error" in it)
                  else (to_int(it.get("result")) if isinstance(it, dict) else None))
            for it, key in zip(res, keys)}
VIEWS = ["name()", "symbol()", "totalSupply()", "totalMinted()", "freeClaimed()",
         "freeMinted()", "FREE_SUPPLY()", "FREE_CAP()", "FREE_SHARES()", "MAX_SUPPLY()",
         "mintOpen()", "balanceOf(address)", "freeClaimed(address)", "freeUsed(address)",
         "mintedBy(address)", "mintStart()", "freeLeft()", "freeAvailable(address)",
         "saleStart()", "saleEnd()", "PRICE()", "price()", "launched()",
         "freeSharesLeft()", "freeSharesRemaining()", "freeClaimedByWallet(address)",
         "currentState()", "finalized()", "refunding()", "totalFreeMinted()", "openedAt()",
         "isFreeOpen()", "FREE_MODE()"]
RUNIC = "0x0ec2c86B8E79c9A664b1ae0D6E3cB06B58ecCFe4"
t0=time.time()
r = raw_batch(RUNIC, VIEWS)
s = {k: v for k, v in r.items() if v is not None} if r else None
out = {"run": "hot-leg 2026-11-12 18:09 Runic follow-up", "at_wib": now_wib,
       "address": RUNIC, "views": r, "summary": s, "elapsed_s": round(time.time()-t0,1)}
json.dump(out, open(BASE+f"hot-leg-{TAG}-runic-followup.json","w"), indent=1)
print(json.dumps(out, indent=1))
