#!/usr/bin/env python3
"""Hot-leg run 1744 follow-up: retry leg3 on-chain reads for the new S1+S2
sale-shape contract 0x0ec2c86B8E79c9A664b1ae0D6E3cB06B58ecCFe4 (leg3 views were
null — RPC race failed). Read-only. Raced batch across 2 endpoints, 3 attempts."""
import json, subprocess, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
ADDR = "0x0ec2c86B8E79c9A664b1ae0D6E3cB06B58ecCFe4"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None

def _post_one(ep, payload, timeout=15):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True, timeout=timeout + 5)
    return json.loads(r.stdout)

def post_race(payload, timeout=15):
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

VIEWS = ["name()", "symbol()", "decimals()", "totalSupply()", "totalMinted()",
         "freeClaimed()", "freeMinted()", "FREE_SUPPLY()", "FREE_CAP()", "FREE_SHARES()",
         "MAX_SUPPLY()", "mintOpen()", "isFreeOpen()", "FREE_MODE()", "free_per_wallet()",
         "freeRemaining()", "freeSupply()", "freeSharesRemaining()", "freeSharesLeft()",
         "balanceOf(address)", "freeClaimed(address)", "freeMintedBy(address)",
         "freeAvailable(address)", "mintedBy(address)", "mintStart()", "saleStart()",
         "saleEnd()", "PRICE()", "price()", "launched()", "currentState()", "finalized()",
         "refunding()", "totalFreeMinted()", "openedAt()", "claimFree()", "mintFree()",
         "contractURI()", "agentRegistry()", "agentGate()", "agentIdRegistry()"]

def raw_batch(views):
    calls, keys = [], []
    for i, sig in enumerate(views):
        base = sig.split("(")[0]
        if "(address)" in sig:
            data = sel(sig) + enc(USER); key = base + "_user"
        else:
            data = sel(sig); key = base
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": ADDR, "data": data}, "latest"]})
        keys.append(key)
    res = post_race(calls)
    if res is None:
        return None
    out = {}
    for it, key in zip(res, keys):
        if isinstance(it, dict) and "error" in it:
            out[key] = None
        elif isinstance(it, dict):
            raw = it.get("result") or ""
            out[key] = raw if len(raw) > 66 else to_int(raw)
    return out

result = None
for attempt in range(1, 4):
    result = raw_batch(VIEWS)
    if result and any(v is not None for v in result.values()):
        break
    time.sleep(2)
print(json.dumps({"address": ADDR, "attempts": attempt, "views": result}, indent=1))
json.dump({"address": ADDR, "views": result},
          open(BASE + "hot-leg-2026-11-12-1744-0ec2-leg3retry.json", "w"), indent=1)
