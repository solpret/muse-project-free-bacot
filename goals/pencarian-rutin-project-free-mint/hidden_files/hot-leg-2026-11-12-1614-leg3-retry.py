#!/usr/bin/env python3
"""One-off leg3 retry for new S1 0x22e69F9a7BeC3D991C0ceB5a103E509319E42B2A (run 1614 leg3 views null)."""
import json, subprocess, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
ADDR = "0x22e69F9a7BeC3D991C0ceB5a103E509319E42B2A"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
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

VIEWS = ["name()", "symbol()", "totalSupply()", "totalMinted()", "freeClaimed()",
         "freeMinted()", "FREE_SUPPLY()", "FREE_CAP()", "FREE_SHARES()", "MAX_SUPPLY()",
         "mintOpen()", "balanceOf(address)", "freeClaimed(address)", "freeUsed(address)",
         "mintedBy(address)", "mintStart()", "freeLeft()", "freeAvailable(address)",
         "saleStart()", "saleEnd()", "PRICE()", "price()", "launched()",
         "freeSharesLeft()", "freeSharesRemaining()", "freeClaimedByWallet(address)",
         "currentState()", "finalized()", "refunding()", "totalFreeMinted()", "openedAt()",
         "totalFreeShares()", "freeSharesClaimed()", "quote(address,uint256)",
         "agentRegistry()", "agentGate()"]
calls, keys = [], []
for i, sig in enumerate(VIEWS):
    base = sig.split("(")[0]
    if "(address)" in sig:
        data = sel(sig) + enc(USER); key = base + "_user"
    elif "(address,uint256)" in sig:
        data = sel(sig) + enc(USER) + "0".rjust(64, "0"); key = base + "_user_1"
    else:
        data = sel(sig); key = base
    calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                  "params": [{"to": ADDR, "data": data}, "latest"]})
    keys.append(key)
res = post_rpc_race(calls, timeout=12)
out = {"address": ADDR, "views": None}
if res is not None:
    out["views"] = {key: (None if (isinstance(it, dict) and "error" in it)
                          else (to_int(it.get("result")) if isinstance(it, dict) else None))
                    for it, key in zip(res, keys)}
    out["summary"] = {k: v for k, v in out["views"].items() if v is not None}
print(json.dumps(out, indent=1))
json.dump(out, open(BASE + "hot-leg-2026-11-12-1614-leg3-retry-22e6.json", "w"), indent=1)
# record into seen note
seen = json.load(open(BASE + "hot-leg-seen.json"))
if isinstance(seen.get(ADDR), dict) and out.get("views"):
    ssum = out.get("summary", {})
    seen[ADDR]["note"] = (seen[ADDR].get("note", "") +
        " | LEG3-RETRY 2026-11-12T16:2x: " + ", ".join(f"{k}={v}" for k, v in ssum.items())[:300]).strip()[:600]
    json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
    print("SEEN-UPDATED")
