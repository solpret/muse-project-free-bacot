#!/usr/bin/env python3
"""Analyze reread 1801 vs snapshot: velocity, promotions, sellouts, changes.
Writes run-2026-11-09-1801-analyze.json + prints compact report."""
import json, datetime
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-2026-11-09-1801-reread.json"))
contracts = snap.get("contracts", {})
track_c = snap.get("track_c", {})
block = rr.get("block")
print("REREAD BLOCK", block)
# last read block from snapshot (1731): 132571528
prev_block = 132571528
# interval minutes: use block diff * 0.45s? No — use snapshot lastReadWib 17:1x vs now 18:1x ~50 min.
# Better: compute from run timestamps: 1731 run at ~17:31-17:50, this run ~18:10. Use 50 min nominal like prior runs? 
# Prior runs used intervalMinutes ~50.06 (from snapshot fields). Use stored interval: compare totalSupply vs previousTotalSupply in snapshot.
out = {"block": block, "velocity_pass": [], "promotions": [], "sellouts": [], "changes": [], "all_null": []}
for name, v in contracts.items():
    r = rr.get("reread", {}).get(name)
    if not isinstance(r, dict):
        out["changes"].append((name, "NOT REREAD"))
        continue
    prev_ts = v.get("totalSupply")
    new_ts = r.get("totalSupply")
    prev_free = v.get("freeClaimed")
    new_free = r.get("freeClaimed")
    if new_ts is None and new_free is None and r.get("balanceOf_user") is None and r.get("FREE_SUPPLY") is None:
        out["all_null"].append(name)
        continue
    # velocity: minted in interval = new - prev (only if both ints)
    minted = None
    if isinstance(prev_ts, int) and isinstance(new_ts, int):
        minted = new_ts - prev_ts
    # free pct
    free_pct = None
    fs = r.get("FREE_SUPPLY")
    if fs is None: fs = v.get("FREE_SUPPLY") or v.get("freeSupply")
    if isinstance(new_free, int) and isinstance(fs, int) and fs:
        free_pct = round(100.0*new_free/fs, 2)
    elif isinstance(new_free, int) and isinstance(v.get("freePctVerified"), (int,float)):
        pass
    # velocity leg: need previous rate from snapshot
    prev_rate = v.get("currentRatePerMin")
    interval = 50.0  # approx minutes since run 1731 read (~17:31-18:2x); refined below
    # use snapshot intervalMinutes if present (1731: 50.06)
    vel_pass = False
    rate = None
    if minted is not None and minted >= 0:
        rate = minted / interval
        if prev_rate is not None and prev_rate > 0 and minted >= 20 and rate >= 1.5*prev_rate:
            vel_pass = True
    # flag interesting
    interesting = False
    reasons = []
    if minted is not None and minted >= 20: reasons.append(f"minted+{minted}"); interesting = True
    if vel_pass: reasons.append("VELOCITY PASS"); interesting = True
    if free_pct is not None and isinstance(v.get("freePctVerified"), (int,float)) and free_pct != v.get("freePctVerified"):
        reasons.append(f"free% {v.get('freePctVerified')}->{free_pct}"); interesting = True
    if isinstance(new_free, int) and isinstance(fs, int) and fs and new_free >= fs:
        reasons.append("FREE POOL EXHAUSTED"); interesting = True
    if isinstance(new_ts, int) and isinstance(v.get("MAX_SUPPLY"), int) and new_ts >= v["MAX_SUPPLY"]:
        reasons.append("SOLD OUT (ts>=MAX)"); interesting = True
    if interesting:
        out["changes"].append((name, f"ts {prev_ts}->{new_ts} free {prev_free}->{new_free} free% {free_pct} minted {minted} rate {None if rate is None else round(rate,3)} prev_rate {prev_rate} | {'; '.join(reasons)}"))
    if vel_pass:
        out["velocity_pass"].append(name)
print("VELOCITY PASS:", out["velocity_pass"])
print("ALL-NULL reads:", len(out["all_null"]))
print("--- CHANGES ---")
for c in out["changes"]: print(c)
json.dump(out, open(f"{BASE}/run-2026-11-09-1801-analyze.json","w"), indent=1)
# focused items
print("--- FOCUSED ---")
for name in ["Agentite","Lenx Agent Pass","Reel","Osiris Guardians","Marbleworks","Motor Agent","Frost Agent","Quar Agent","0x13A1Ebc9-new","ALL ACCESS","AgentPad Pass","LIKHIN","HIVE Agents","Bubblebruin"]:
    r = rr.get("reread", {}).get(name)
    v = contracts.get(name, {})
    print(name, "| prev ts", v.get("totalSupply"), "-> new", (r or {}).get("totalSupply"),
          "| prev free", v.get("freeClaimed"), "-> new", (r or {}).get("freeClaimed"),
          "| FREE_SUPPLY", (r or {}).get("FREE_SUPPLY") or v.get("FREE_SUPPLY"),
          "| bal_user", (r or {}).get("balanceOf_user"), "| status", v.get("status"))
print("--- TRACK_C focused ---")
for name in ["DROID","OSK","IMARS","NIULAI","KillZero-K0-sale","FABE","NIUBI","960E-sale","Agentidbsc","DeY","FANBEIMAO-824d","BoxBigem-3Ee9","0x260bf39a-sale","NIBULL","NUSA","PACTA","Minority Pass"]:
    r = rr.get("track_c", {}).get(name)
    v = track_c.get(name, {})
    if r is None and not isinstance(v, dict):
        print(name, "NOT IN REREAD/TRACK_C"); continue
    print(name, "| prev:", str(v)[:120].replace("\n"," "), "|| reread:", r)
