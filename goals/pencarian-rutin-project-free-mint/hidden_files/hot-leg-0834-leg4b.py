#!/usr/bin/env python3
"""Hot-leg 0834 leg4 (retry): re-read the 48-item focus set vs 0829 baseline.
Chunked direct JSON-RPC batches of 4 contracts via publicnode (primary) /
nodereal (fallback). Read-only. Null/error reads keep baseline."""
import json, time, urllib.request
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
T0 = time.time()
EPS = ["https://bsc.publicnode.com/", "https://bsc.nodereal.io/"]

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a.lower().replace("0x", "").rjust(64, "0")
def enc_uint(n): return format(n, "064x")

NOARG = ["totalSupply","totalMinted","totalMints","freeMinted","freeClaimed",
 "freeMintedTotal","freeLeft","freeUsed","FREE_CAP","FREE_SUPPLY","FREE_SHARES",
 "FREE_QUOTA","FREE_PER_WALLET","remainingFree","MAX_SUPPLY","MAX_FREE",
 "sharesMinted","sold","phase","launched","soldOut","closed","finalized",
 "mintOpen","mintActive","totalSkunksMinted","freeSkunksClaimed",
 "freeSkunksRemaining","freeRemaining","mintCount","MAX_MINTS","opened",
 "openedAt","saleActive","soldShares","publicMinted","launchTime","totalShares",
 "totalFreeShares","mintingOpen","TOTAL_SHARES","MAX_FREE_SHARES","SALE_START",
 "isSaleEnded","remaining","mintEnd","mintStart","SALE_END","startTime",
 "freeWindowOpen","agentFreeUsed","AGENT_FREE_CAP","paidMinted","freeSharesLeft",
 "isFreePhase","standardRemaining","legendaryRemaining","normalMinted",
 "failed","isRefundPhase","mintClosed"]
ADDRARG = ["balanceOf","mintedBy","freeClaimed","freeLeft","freeUsed","freeCount",
 "freeMinted","mintedCount","freeAvailable","hasMinted","quotaOf","freeTakenBy",
 "priceFor","freeClaimedBy","freeUsedByWallet","hasFreeMinted","freeAllowance",
 "maxShares","remainingShares","freeMintedByWallet","freeBooked","tokenClaimed",
 "hasClaimed","hasClaimedFree","freeMintedBy","freeTaken"]
ADDRUINT = ["quote","freeFor","cost","mintPriceFor","costFor"]

def calldata(field):
    if field.endswith("_user1"):
        fn = field[:-6]
        if fn in ADDRUINT: return sel(f"{fn}(address,uint256)") + enc_addr(USER) + enc_uint(1)
        return None
    if field.endswith("_user"):
        fn = field[:-5]
        if fn in ADDRARG: return sel(f"{fn}(address)") + enc_addr(USER)
        return None
    if field in NOARG: return sel(f"{field}()")
    return None

def rpc_batch(url, batch):
    req = urllib.request.Request(url, data=json.dumps(batch).encode(),
        headers={"Content-Type": "application/json", "User-Agent": "curl/8"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)

def decode(h):
    if not h or not isinstance(h, str) or len(h) < 66: return None
    try: return int(h, 16)
    except Exception: return None

base = json.load(open(BASE + "hot-leg-run-2026-11-19-0829-reread.json"))
reads = base["reads"]
items = list(reads.items())
# build per-contract call lists
plan = []  # (name, addr, [(field, data)])
for name, item in items:
    cl = []
    for field in item["views"]:
        cd = calldata(field)
        if cd: cl.append((field, cd))
    plan.append((name, item["address"], cl))

results = {}  # (name, field) -> int|None
chunk_errors = []
for ci in range(0, len(plan), 4):
    chunk = plan[ci:ci+4]
    batch, keys = [], []
    for name, addr, cl in chunk:
        for field, cd in cl:
            batch.append({"jsonrpc": "2.0", "method": "eth_call",
                          "params": [{"to": addr, "data": cd}, "latest"],
                          "id": len(batch)})
            keys.append((name, field))
    got = None
    for ep in EPS:
        try:
            got = rpc_batch(ep, batch)
            break
        except Exception as e:
            chunk_errors.append(f"chunk@{ci} {ep} err:{type(e).__name__}")
            got = None
    if got is None:
        for k in keys: results[k] = None
        continue
    by_id = {r.get("id"): r for r in got} if isinstance(got, list) else {}
    for i, k in enumerate(keys):
        r = by_id.get(i, {})
        results[k] = decode(r.get("result")) if not r.get("error") else None

block = None
for ep in EPS:
    try:
        b = rpc_batch(ep, [{"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 0}])
        block = int(b[0]["result"], 16)
        break
    except Exception:
        continue

new_reads, changes, nulls = {}, [], []
for name, item in items:
    new_reads[name] = {"address": item["address"], "views": {}}
    for field, prev in item["views"].items():
        val = results.get((name, field))
        if val is None and calldata(field) is None:
            val = prev  # unmapped field: keep baseline
        new_reads[name]["views"][field] = val if val is not None else prev
        if val is None and calldata(field) is not None:
            nulls.append(f"{name}.{field}")
        elif val is not None and prev is not None and val != prev:
            changes.append({"item": name, "field": field, "prev": prev, "now": val})

doc = {"run": "free-mint-hot-leg 2026-11-19 08:34 WIB",
       "started_wib": "2026-11-19T08:34:38+07:00",
       "baseline": "hot-leg-run-2026-11-19-0829-reread.json",
       "block": block, "reads": new_reads,
       "changes_vs_0829": changes, "null_reads": nulls,
       "chunk_errors": chunk_errors,
       "rpc_note": "chunked direct JSON-RPC batches of 4 contracts via publicnode/nodereal; fcfs_read batch+race failed all endpoints (TimeoutError, oversized single batch) + bsc-dataseed.binance.org now 403",
       "elapsed_s": round(time.time() - T0, 1)}
json.dump(doc, open(BASE + "hot-leg-run-2026-11-19-0834-reread.json", "w"), indent=1)
print("BLOCK:", block)
print("CHANGES:", json.dumps(changes, indent=1))
print("NULLS:", nulls)
print("CHUNK_ERRORS:", chunk_errors)
print("elapsed:", round(time.time() - T0, 1))
