#!/usr/bin/env python3
"""Hot-leg 0834 leg4: re-read the 48-item focus set vs 0829 baseline.
Read-only. Builds calls.json, runs fcfs_read.py (batch+race), decodes
uint256/bool, diffs vs baseline, writes hot-leg-run-2026-11-19-0834-reread.json.
Null/error reads keep baseline (never a change)."""
import json, subprocess, sys, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
T0 = time.time()

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

base = json.load(open(BASE + "hot-leg-run-2026-11-19-0829-reread.json"))
reads = base["reads"]
calls, meta = [], []
for name, item in reads.items():
    addr = item["address"]
    for field in item["views"]:
        cd = calldata(field)
        if cd is None:
            meta.append((name, field, None))
        else:
            calls.append({"to": addr, "data": cd})
            meta.append((name, field, len(calls) - 1))

json.dump(calls, open("/tmp/hot0834_calls.json", "w"))
r = subprocess.run([sys.executable, "/home/hatch/workspace/fast_exec/fcfs_read.py",
                    "/tmp/hot0834_calls.json"], capture_output=True, text=True, timeout=120)
print("fcfs stdout tail:", r.stdout[-500:])
print("fcfs stderr tail:", r.stderr[-500:])
out = json.loads(r.stdout)
results = out["results"]
print("calls:", len(calls), "results:", len(results), "elapsed_s:", round(out.get("elapsed_s", 0), 2))

def decode(h):
    if not h or not isinstance(h, str) or len(h) < 66: return None
    try: return int(h, 16)
    except Exception: return None

new_reads, changes, errors = {}, [], []
for name, field, idx in meta:
    if idx is None:
        continue
    val = decode(results[idx])
    new_reads.setdefault(name, {"address": reads[name]["address"], "views": {}})

for name, field, idx in meta:
    if idx is None:
        new_reads[name]["views"][field] = reads[name]["views"].get(field)
        continue
    val = decode(results[idx])
    prev = reads[name]["views"].get(field)
    new_reads[name]["views"][field] = val if val is not None else prev
    if val is None:
        errors.append(f"{name}.{field}")
    elif prev is not None and val != prev:
        changes.append({"item": name, "field": field, "prev": prev, "now": val})

# block number
try:
    b = subprocess.run([sys.executable, "/home/hatch/workspace/fast_exec/fast_rpc.py", "block"],
                       capture_output=True, text=True, timeout=30)
    block = b.stdout.strip().splitlines()[-1] if b.stdout.strip() else None
except Exception as e:
    block = f"err:{e}"

doc = {"run": "free-mint-hot-leg 2026-11-19 08:34 WIB",
       "started_wib": "2026-11-19T08:34:38+07:00",
       "baseline": "hot-leg-run-2026-11-19-0829-reread.json",
       "block": block, "reads": new_reads,
       "changes_vs_0829": changes, "null_reads": errors,
       "elapsed_s": round(time.time() - T0, 1)}
json.dump(doc, open(BASE + "hot-leg-run-2026-11-19-0834-reread.json", "w"), indent=1)
print("CHANGES:", json.dumps(changes, indent=1))
print("NULL READS:", errors)
print("BLOCK:", block, "elapsed:", round(time.time() - T0, 1))
