#!/usr/bin/env python3
"""Hot-leg 2129 follow-up #2: small-batch (8-view) leg3 re-read for the 2 NEW
S1 contracts. Single calls work (freeMinted 38 and 8); the 31-view batch
failed 3x - same pattern as OBFG leg3a (small batch works). Raced endpoints,
chunks of 8. Read-only except own seen-note appends."""
import json, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-12-2129-followup2"
T0 = time.time()
now_wib = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
TARGETS = ["0xdAc222886b887fC5b6262889B189B8eb57e99794",
           "0xF4D75A6E5FD3158A573d0F58676F9667E97Eb606"]
VIEWS = ["name()", "symbol()", "totalSupply()", "totalMinted()", "freeClaimed()",
         "freeMinted()", "FREE_SUPPLY()", "FREE_CAP()", "FREE_SHARES()", "MAX_SUPPLY()",
         "mintOpen()", "balanceOf(address)", "freeClaimed(address)", "freeUsed(address)",
         "mintedBy(address)", "mintStart()", "freeLeft()", "freeAvailable(address)",
         "saleStart()", "saleEnd()", "PRICE()", "price()", "launched()",
         "freeSharesLeft()", "freeSharesRemaining()", "freeClaimedByWallet(address)",
         "currentState()", "finalized()", "refunding()", "totalFreeMinted()", "openedAt()"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
import subprocess
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
def raw_batch_small(addr, views):
    merged = {}
    for i in range(0, len(views), 8):
        chunk = views[i:i + 8]
        calls, keys = [], []
        for j, sig in enumerate(chunk):
            base = sig.split("(")[0]
            if "(address)" in sig:
                data = sel(sig) + enc(USER); key = base + "_user"
            else:
                data = sel(sig); key = base
            calls.append({"jsonrpc": "2.0", "id": j + 1, "method": "eth_call",
                          "params": [{"to": addr, "data": data}, "latest"]})
            keys.append(key)
        res = post_rpc_race(calls, timeout=12)
        if res is None:
            for k in keys: merged[k] = None
            continue
        for it, key in zip(res, keys):
            merged[key] = (None if (isinstance(it, dict) and "error" in it)
                           else (to_int(it.get("result")) if isinstance(it, dict) else None))
    return merged

out = {"run": "hot-leg 2129 follow-up2 small-batch leg3", "started_wib": now_wib, "results": {}}
seen = json.load(open(BASE + "hot-leg-seen.json"))
for a in TARGETS:
    r = raw_batch_small(a, VIEWS)
    summ = {k: v for k, v in r.items() if v is not None}
    out["results"][a] = {"views": r, "summary": summ}
    if isinstance(seen.get(a), dict):
        if summ:
            seen[a]["status"] = "sale-shape-leg3-verified"
            seen[a]["note"] = (seen[a].get("note", "") +
                f" | LEG3-SMALLBATCH-2129 {now_wib}: views OK " +
                ", ".join(f"{k}={v}" for k, v in summ.items())[:400]).strip()[:900]
        else:
            seen[a]["note"] = (seen[a].get("note", "") +
                f" | LEG3-SMALLBATCH-2129 {now_wib}: small-batch also null - pool/slot/age "
                f"UNVERIFIED, NOT a lead, never previewed/minted; retry next run.").strip()[:900]
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
out["elapsed_s"] = round(time.time() - T0, 1)
json.dump(out, open(BASE + f"hot-leg-{TAG}.json", "w"), indent=1)
print(json.dumps(out, indent=1))
