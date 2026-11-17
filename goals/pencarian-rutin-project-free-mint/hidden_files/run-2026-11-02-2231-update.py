#!/usr/bin/env python3
"""Main run 2026-11-02 22:01 WIB: apply route-1 reread to snapshot.
Idempotent for reread fields (same read block / values). Scan triage
additions (if any) are applied by a second step after the scan finishes."""
import json, os, shutil
BASE = os.path.expanduser("~/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/")
snap = json.load(open(BASE + "onchain-snapshot.json"))
read = json.load(open(BASE + "run-2026-11-02-2231-read.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot-2026-11-02-2231.bak.json")
READ_BLOCK = read["block"]  # 131261497, block time 2026-11-02T22:32:16+07:00
READ_WIB = "2026-11-02T22:32:16+07:00"
INTERVAL = 29.75  # minutes, 22:02:31 -> 22:32:16 (read-block times)
velocity_pass = []
crossed = []
for name, v in snap["contracts"].items():
    if name not in read:
        continue
    if str(v.get("status", "")).startswith("minted-by-user"):
        continue
    r = read[name]
    old_ts = v.get("totalSupply")
    new_ts = r.get("totalSupply()")
    old_fc = v.get("freeClaimed")
    new_fc = r.get("freeClaimed()")
    old_fs = v.get("FREE_SUPPLY")
    new_fs = r.get("FREE_SUPPLY()")
    old_fm = v.get("freeMinted")
    new_fm = r.get("freeMinted()")
    old_fl = v.get("freeLeft")
    new_fl = r.get("freeLeft()")
    if new_ts is not None:
        minted = (new_ts - old_ts) if old_ts is not None else 0
        prev_rate = v.get("currentRatePerMin", v.get("previousRatePerMin"))
        cur_rate = round(minted / INTERVAL, 3) if minted else 0.0
        passes = bool(prev_rate and minted >= 20 and cur_rate >= 1.5 * prev_rate)
        if passes:
            velocity_pass.append((name, minted, cur_rate, prev_rate))
        v["previousTotalSupply"] = old_ts
        v["totalSupply"] = new_ts
        v["mintedInInterval"] = minted
        v["intervalMinutes"] = INTERVAL
        v["previousRatePerMin"] = prev_rate
        v["currentRatePerMin"] = cur_rate
        v["velocityLegPasses"] = passes
        v["velocityNote"] = f"Run 22:01 WIB (read block {READ_BLOCK}): {minted:+d} tokens in ~{INTERVAL} min = {cur_rate}/min, ratio vs prior {prev_rate} -> velocity leg {'PASSES' if passes else 'FAILS'}."
    if new_fc is not None:
        v["freeClaimed"] = new_fc
    if new_fs is not None:
        v["FREE_SUPPLY"] = new_fs
    if new_fm is not None:
        v["freeMinted"] = new_fm
    if new_fl is not None:
        v["freeLeft"] = new_fl
    fc = new_fc if new_fc is not None else old_fc
    fs = new_fs if new_fs is not None else old_fs
    fm = new_fm if new_fm is not None else old_fm
    fl = new_fl if new_fl is not None else old_fl
    pct = None
    if fc is not None and fs:
        pct = round(100 * fc / fs, 2)
    elif fm is not None and fl is not None and (fm + fl):
        pct = round(100 * fm / (fm + fl), 2)
    elif fm is not None and fs:
        pct = round(100 * fm / fs, 2)
    if pct is not None:
        old_pct = v.get("freePctVerified")
        v["freePctVerified"] = pct
        if old_pct is not None and old_pct < 50 <= pct:
            crossed.append((name, old_pct, pct))
    v["userMintedBy"] = r.get("mintedBy(address)")
    v["userFreeUsed"] = r.get("freeUsed(address)")
    v["userBalance"] = r.get("balanceOf(address)")
    v["lastReadBlock"] = READ_BLOCK
    v["lastReadWib"] = READ_WIB
print("velocity_pass:", velocity_pass)
print("crossed_50:", crossed)
snap["timestamp_wib"] = READ_WIB
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("snapshot updated, contracts:", len(snap["contracts"]))
