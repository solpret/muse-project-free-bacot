#!/usr/bin/env python3
"""Analyze reread 2101 vs snapshot: velocity, promotions, sellouts, changes.
Writes run-2026-11-09-2101-analyze.json + prints compact report.
Interval: block 132593641 (~20:37 WIB) -> 132597982 (~21:10 WIB): 4341 blok x 0.45 dtk = ~32.6 min."""
import json
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-2026-11-09-2101-reread.json"))
contracts = snap.get("contracts", {})
track_c = snap.get("track_c", {})
block = rr.get("block")
print("REREAD BLOCK", block)
INTERVAL = 32.6
out = {"block": block, "interval_minutes": INTERVAL, "velocity_pass": [],
       "promotions": [], "sellouts": [], "changes": [], "all_null": []}
for name, v in contracts.items():
    r = rr.get("reread", {}).get(name)
    if not isinstance(r, dict):
        out["changes"].append((name, "NOT REREAD"))
        continue
    prev_ts = v.get("totalSupply")
    new_ts = r.get("totalSupply")
    prev_free = v.get("freeClaimed")
    new_free = r.get("freeClaimed")
    if (new_ts is None and new_free is None and r.get("freeMinted") is None
            and r.get("balanceOf_user") is None and r.get("FREE_SUPPLY") is None):
        out["all_null"].append(name)
        continue
    minted = new_ts - prev_ts if isinstance(prev_ts, int) and isinstance(new_ts, int) else None
    fs = r.get("FREE_SUPPLY")
    if fs is None: fs = v.get("FREE_SUPPLY") or v.get("freeSupply")
    free_pct = round(100.0*new_free/fs, 2) if isinstance(new_free, int) and isinstance(fs, int) and fs else None
    # operative free counter: freeMinted preferred (freeClaimed() reverts on factory contracts)
    fm_new = r.get("freeMinted")
    fm_prev = v.get("freeMinted")
    free_pct_m = None
    cap = fs
    if isinstance(fm_new, int) and isinstance(cap, int) and cap:
        free_pct_m = round(100.0*fm_new/cap, 2)
    prev_rate = v.get("currentRatePerMin")
    vel_pass = False
    rate = None
    if minted is not None and minted >= 0:
        rate = minted / INTERVAL
        if prev_rate is not None and prev_rate > 0 and minted >= 20 and rate >= 1.5*prev_rate:
            vel_pass = True
    reasons = []
    if minted is not None and minted >= 20: reasons.append(f"minted+{minted}")
    if vel_pass: reasons.append("VELOCITY PASS")
    if free_pct is not None and free_pct != v.get("freePctVerified"):
        reasons.append(f"free% {v.get('freePctVerified')}->{free_pct}")
    if free_pct_m is not None and free_pct_m != v.get("freePctVerified"):
        reasons.append(f"freeMinted% {v.get('freePctVerified')}->{free_pct_m} (fm {fm_prev}->{fm_new})")
    if isinstance(new_free, int) and isinstance(fs, int) and fs and new_free >= fs:
        reasons.append("FREE POOL EXHAUSTED (freeClaimed)")
    if isinstance(fm_new, int) and isinstance(cap, int) and cap and fm_new >= cap:
        reasons.append("FREE POOL EXHAUSTED (freeMinted)")
    if isinstance(new_ts, int) and isinstance(v.get("MAX_SUPPLY"), int) and new_ts >= v["MAX_SUPPLY"]:
        reasons.append("SOLD OUT (ts>=MAX)")
    if reasons:
        out["changes"].append((name, f"ts {prev_ts}->{new_ts} free {prev_free}->{new_free} fm {fm_prev}->{fm_new} free% {free_pct} fm% {free_pct_m} minted {minted} rate {None if rate is None else round(rate,3)} prev_rate {prev_rate} | {'; '.join(reasons)}"))
    if vel_pass:
        out["velocity_pass"].append(name)
print("VELOCITY PASS:", out["velocity_pass"])
print("ALL-NULL reads:", len(out["all_null"]), out["all_null"][:10])
print("--- CHANGES ---")
for c in out["changes"]: print(c)
json.dump(out, open(f"{BASE}/run-2026-11-09-2101-analyze.json", "w"), indent=1)
print("--- FOCUSED contracts ---")
for name in ["TIME CARDS Genesis", "Agentic", "BAHUANG3", "Lenx Agent Pass", "NEURA",
             "FourAgent-5842-1401", "Osiris Guardians", "HIVE Agents", "MONEY", "AURISLE",
             "Aura Agents", "Cryptlichor", "Gachagent", "DigDown", "AgentBone", "Unbroken",
             "SynthMinds", "Shroomlets", "Drakogent", "Astragent", "Orbitagent", "Mars Nexus",
             "Kairos", "Borealux"]:
    r = rr.get("reread", {}).get(name)
    v = contracts.get(name, {})
    print(name, "| ts", v.get("totalSupply"), "->", (r or {}).get("totalSupply"),
          "| free", v.get("freeClaimed"), "->", (r or {}).get("freeClaimed"),
          "| fm", v.get("freeMinted"), "->", (r or {}).get("freeMinted"),
          "| FREE_SUPPLY", (r or {}).get("FREE_SUPPLY") or v.get("FREE_SUPPLY"),
          "| bal_user", (r or {}).get("balanceOf_user"), "| slot_user", (r or {}).get("freeClaimed_user"),
          "| status", v.get("status"))
print("--- TRACK_C focused ---")
for name in ["BHTB", "AgentGrid", "NIBULL", "0x260bf39a-sale", "DeY", "FANBEIMAO-824d",
             "Draco Coin", "PHNX", "YAMA", "CLEPSYDRA", "ChimpAgent", "NUSA", "DROID", "OSK",
             "IMARS", "NIULAI", "KillZero-K0-sale", "FABE", "NIUBI", "960E-sale", "Agentidbsc",
             "FOUNT", "YAOQIAN", "Kiko9393", "BoxBigem-3Ee9", "MONEY"]:
    r = rr.get("track_c", {}).get(name)
    v = track_c.get(name, {})
    print(name, "| prev ts", v.get("totalSupply"), "fm", v.get("freeMinted"),
          "fsr", v.get("freeSharesRemaining"), "bal", v.get("balanceOf_user"),
          "|| new ts", (r or {}).get("totalSupply"), "fm", (r or {}).get("freeMinted"),
          "fsr", (r or {}).get("freeSharesRemaining"), "bal", (r or {}).get("balanceOf_user"),
          "slot", (r or {}).get("freeClaimed_user"), "| status", v.get("status"))
print("--- TRACK_C all changes (ts/fm/fsr delta) ---")
for name, v in track_c.items():
    if not isinstance(v, dict): continue
    r = rr.get("track_c", {}).get(name)
    if not isinstance(r, dict): continue
    deltas = []
    for k in ("totalSupply", "freeMinted", "freeSharesRemaining"):
        if v.get(k) != r.get(k) and r.get(k) is not None:
            deltas.append(f"{k} {v.get(k)}->{r.get(k)}")
    if deltas:
        print(name, "|", "; ".join(deltas), "| status", v.get("status"))
