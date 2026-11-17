#!/usr/bin/env python3
"""Hot-leg 2129 follow-up: leg3 re-read for the 2 NEW S1 contracts whose
leg3 batch returned views=null (RPC batch failure, not on-chain state).
0xdAc222886b887fC5b6262889B189B8eb57e99794 and
0xF4D75A6E5FD3158A573d0F58676F9667E97Eb606.
Up to 3 attempts, raced endpoints. Read-only except own seen-note appends.
If views stay null: record unverified, NOT a lead, retry next run."""
import json, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-12-2129-followup"
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

out = {"run": "hot-leg 2129 follow-up leg3 retry", "started_wib": now_wib, "results": {}}
seen = json.load(open(BASE + "hot-leg-seen.json"))
for a in TARGETS:
    r = None
    for attempt in range(3):
        r = raw_batch(a, VIEWS)
        if r is not None and any(v is not None for v in r.values()):
            break
        time.sleep(2)
    summ = {k: v for k, v in r.items() if v is not None} if r else None
    out["results"][a] = {"views": r, "summary": summ}
    if isinstance(seen.get(a), dict):
        if r and summ:
            seen[a]["status"] = "sale-shape-leg3-verified"
            seen[a]["note"] = (seen[a].get("note", "") +
                f" | LEG3-RETRY-2129 {now_wib}: views OK " +
                ", ".join(f"{k}={v}" for k, v in summ.items())[:350]).strip()[:700]
        else:
            seen[a]["status"] = "sale-shape-leg3-unverified"
            seen[a]["note"] = (seen[a].get("note", "") +
                f" | LEG3-RETRY-2129 {now_wib}: views STILL null after 3 attempts "
                f"(RPC batch failure, not on-chain state) - pool/slot/age UNVERIFIED, "
                f"NOT a lead, never previewed/minted; retry next run.").strip()[:700]
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
out["elapsed_s"] = round(time.time() - T0, 1)
json.dump(out, open(BASE + f"hot-leg-{TAG}.json", "w"), indent=1)
print(json.dumps(out, indent=1))
