#!/usr/bin/env python3
import json, shutil
B = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
shutil.copy(B + "onchain-snapshot.json", B + "onchain-snapshot-2026-11-02-1331.bak.json")
snap = json.load(open(B + "onchain-snapshot.json"))
read = json.load(open(B + "run-2026-11-02-1331-read.json"))
block = read["block"]
for k, v in read["watchlist"].items():
    if k not in snap["contracts"]:
        continue
    e = snap["contracts"][k]
    old_ts, old_free = e.get("totalSupply"), e.get("freeClaimed")
    ts, fc, fs = v.get("totalSupply()"), v.get("freeClaimed()"), v.get("FREE_SUPPLY()")
    if ts is not None:
        e["totalSupply"] = ts
    if fc is not None:
        e["freeClaimed"] = fc
    if fs is not None:
        e["FREE_SUPPLY"] = fs
    if fc is not None and fs:
        e["freePctVerified"] = round(fc / fs * 100, 2)
    e["userMintedBy"] = v.get("mintedBy(address)")
    e["userFreeUsed"] = v.get("freeUsed(address)")
    e["userBalance"] = v.get("balanceOf(address)")
    e["lastReadBlock"] = block
    e["lastReadWib"] = "2026-11-02T13:33:00+07:00"
    if old_ts is not None and ts is not None:
        e["lastIntervalMinted"] = ts - old_ts
        e["lastIntervalNote"] = f"Run 13:31 WIB: totalSupply {old_ts} -> {ts} (+{ts-old_ts}) since snapshot read 13:10 WIB (block 131189620); free {old_free} -> {fc}."
snap["timestamp_wib"] = "2026-11-02T13:33:00+07:00"
# pending claims (read-only, no preview while not open)
snap["pending_claims"]["binanceai.fun"]["launched"] = bool(read["binanceai"]["launched()"])
snap["pending_claims"]["binanceai.fun"]["tokenClaimed"] = bool(read["binanceai"]["tokenClaimed(address)"])
snap["pending_claims"]["hive-pollen"]["launched"] = bool(read["pollen"]["launched()"])
snap["pending_claims"]["hive-pollen"]["pollenAgents"] = read["pollen"]["pollenAgents()"]
json.dump(snap, open(B + "onchain-snapshot.json", "w"), indent=1)
print("updated, block", block)
for k in ["Malabao", "Wispuff", "Servopaw", "Neonhare", "Mercubo", "Chimerito", "Nightsable", "NightshadeClub"]:
    e = snap["contracts"][k]
    print(k, e.get("totalSupply"), e.get("freeClaimed"), e.get("FREE_SUPPLY"), e.get("freePctVerified"), e.get("lastIntervalMinted"))
