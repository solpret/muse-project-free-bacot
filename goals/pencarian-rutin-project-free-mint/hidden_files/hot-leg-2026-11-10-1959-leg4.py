#!/usr/bin/env python3
"""Leg4-only for hot-leg 2026-11-10 19:59: re-read the 48-item set vs the
19:59 baseline (hot-leg-2026-11-10-1959-reread.json). Null reads keep the
baseline value (never a change). Read-only except this run's own outputs.
No preview/mint, no chain-wide scan."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EP = "https://bsc.nodereal.io/"
T0 = time.time()
out = {}

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]

def enc_addr(a): return a.lower().replace("0x", "").rjust(64, "0")
def enc_uint(n): return format(n, "064x")

NOARG = ["totalSupply", "totalMinted", "totalMints", "freeMinted", "freeClaimed",
         "freeMintedTotal", "freeLeft", "freeUsed", "FREE_CAP", "FREE_SUPPLY",
         "FREE_SHARES", "FREE_QUOTA", "FREE_PER_WALLET", "remainingFree",
         "MAX_SUPPLY", "MAX_FREE", "sharesMinted", "sold", "phase", "launched",
         "soldOut", "closed", "finalized", "mintOpen", "mintActive",
         "totalSkunksMinted", "freeSkunksClaimed", "freeSkunksRemaining",
         "freeRemaining", "mintCount", "MAX_MINTS", "opened", "openedAt", "saleActive",
         "soldShares", "publicMinted", "launchTime", "totalShares", "totalFreeShares",
         "mintingOpen", "TOTAL_SHARES", "MAX_FREE_SHARES", "SALE_START", "isSaleEnded",
         "remaining", "mintEnd", "mintStart", "SALE_END", "startTime",
         "freeWindowOpen", "agentFreeUsed", "AGENT_FREE_CAP", "paidMinted"]
ADDRARG = ["balanceOf", "mintedBy", "freeClaimed", "freeLeft", "freeUsed",
           "freeCount", "freeMinted", "mintedCount", "freeAvailable",
           "hasMinted", "quotaOf", "freeTakenBy", "priceFor", "freeClaimedBy",
           "freeUsedByWallet", "hasFreeMinted", "freeAllowance", "maxShares", "remainingShares"]
ADDRUINT = ["quote", "freeFor"]

def calldata(field):
    if field in ("address", "_batch_fail"): return None
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

def run_batch(calls):
    payload = json.dumps([{"jsonrpc": "2.0", "id": i, "method": "eth_call",
                           "params": [{"to": to, "data": data}, "latest"]}
                          for i, (to, data) in enumerate(calls)])
    p = subprocess.run(["curl", "-s", "--max-time", "30", "-X", "POST", EP,
                        "-H", "Content-Type: application/json", "--data", payload],
                       capture_output=True, text=True)
    try: return json.loads(p.stdout)
    except Exception: return {"_curl_error": p.stdout[:200] + p.stderr[:200]}

def decode(r):
    if not isinstance(r, str) or not r.startswith("0x"): return None
    try: return int(r, 16)
    except Exception: return None

prev = json.load(open(BASE + "hot-leg-2026-11-10-1954-reread.json"))
items = prev["items"]
jobs = []
for name, entry in items.items():
    for field in entry:
        data = calldata(field)
        if data: jobs.append((name, field, entry["address"], data))
p = subprocess.run(["curl", "-s", "--max-time", "15", "-X", "POST", EP,
                    "-H", "Content-Type: application/json",
                    "--data", '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'],
                   capture_output=True, text=True)
try: block = int(json.loads(p.stdout)["result"], 16)
except Exception: block = None
results, failed = {}, []
for i in range(0, len(jobs), 25):
    chunk = jobs[i:i + 25]
    resp = run_batch([(to, data) for (_, _, to, data) in chunk])
    if isinstance(resp, dict) and "_curl_error" in resp:
        for (name, field, to, data) in chunk:
            results[(name, field)] = None; failed.append((name, field))
        continue
    if isinstance(resp, dict): resp = [resp]
    for j, item in enumerate(resp):
        name, field, to, data = chunk[j]
        if isinstance(item, dict) and "result" in item:
            results[(name, field)] = decode(item["result"])
        else:
            results[(name, field)] = None; failed.append((name, field))
reread = {"block": block, "items": {}, "duration_sec": round(time.time() - T0, 1)}
read_failed2 = []
for name, entry in items.items():
    row = {"address": entry["address"]}
    for field in entry:
        if field == "address": continue
        v = results.get((name, field))
        if v is None:
            row[field] = entry.get(field)
            read_failed2.append((name, field))
        else:
            row[field] = v
    reread["items"][name] = row
reread["read_failed"] = [{"item": n, "field": f} for n, f in read_failed2]
diffs = []
for name, row in reread["items"].items():
    base = items.get(name, {})
    for field, val in row.items():
        if field == "address": continue
        old = base.get(field)
        if old is None and val is None: continue
        if old != val: diffs.append({"item": name, "field": field, "old": old, "new": val})
reread["diffs_vs_1954"] = diffs
json.dump(reread, open(BASE + "hot-leg-2026-11-10-1959-reread.json", "w"), indent=1)

# promo flags (0039-style)
snap2 = json.load(open(BASE + "onchain-snapshot.json"))
sc = snap2.get("contracts", {}) or {}
st = snap2.get("track_c", {}) or {}
flags = []
for name, entry in reread["items"].items():
    meta = sc.get(name) or st.get(name) or {}
    status = (meta.get("status") or "") if isinstance(meta, dict) else ""
    free = entry.get("freeMinted", entry.get("freeClaimed", entry.get("freeMintedTotal")))
    cap = entry.get("FREE_CAP", entry.get("FREE_SUPPLY", entry.get("FREE_SHARES",
          entry.get("FREE_QUOTA", entry.get("MAX_SUPPLY")))))
    if isinstance(free, int) and isinstance(cap, int) and cap > 0:
        pct = free / cap
        user_open = entry.get("freeClaimed_user") in (0, False, None) or entry.get("balanceOf_user") == 0
        if free >= cap:
            flags.append({"item": name, "flag": "sellout?", "pct": round(pct, 4), "free": free, "cap": cap, "snap_status": status})
        elif pct >= 0.25 and user_open:
            flags.append({"item": name, "flag": "promo-candidate-check", "pct": round(pct, 4), "free": free, "cap": cap, "snap_status": status})
pend = snap2.get("pending_claims", {}) or {}
out["leg4"] = {"block": block, "prev_block": prev.get("block"), "rpc": EP,
               "items_n": len(items), "changes": diffs,
               "failed_call_idx": [{"item": n, "field": f} for n, f in failed],
               "read_failed": reread["read_failed"],
               "mode": "chunked eth_call batches of <=25 (read-only); null reads keep baseline, never a change"}
out["leg4_promo_flags"] = flags
out["pending_claims"] = "snapshot pending_claims empty - nothing to re-read" if not pend else f"{len(pend)} pending claims present"
out["duration_sec"] = round(time.time() - T0, 1)

json.dump(out, open(BASE + "hot-leg-run-2026-11-10-1959-leg4.json", "w"), indent=1)
print(json.dumps(out, indent=1)[:6000])
