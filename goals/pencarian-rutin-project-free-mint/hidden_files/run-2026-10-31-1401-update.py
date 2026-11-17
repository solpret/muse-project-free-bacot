#!/usr/bin/env python3
import json
p = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
snap = json.load(open(p))
cur = {
 "AgentImps": 666, "AgentMiner": 4407, "AgentPad Pass": 1128, "Agentlings": 6108,
 "Alibaba & The 70 Thieves": 4674, "BeHand Pass": 6424, "Brutes": 5555,
 "Fleet Genesis": 1000, "Floppy Agents": 3333, "Hackou AI Pass": 90,
 "Noir Brokers": 3333, "OTV": 557, "PixelVulpes": 3333, "SYMBOL": 3638,
 "Sonic Protocol": 2237, "UMBRA Agents": 3000, "danta": 2007,
}
for name, new_ts in cur.items():
    e = snap["contracts"][name]
    old_ts = e["totalSupply"]
    old_rate = e["ratePerMinute"]
    delta = new_ts - old_ts if old_ts is not None else None
    rate = round(delta / 30, 3) if delta is not None else None
    e["previousTotalSupply"] = old_ts
    e["previousRatePerMinute"] = old_rate
    e["totalSupply"] = new_ts
    e["mintedInInterval"] = delta
    e["ratePerMinute"] = rate
snap["timestamp_wib"] = "2026-10-31T14:02:00+07:00"
snap["note"] = ("Snapshot 14:02 WIB run; elapsed ~30 min since 13:32 snapshot. NO new main candidate: "
 "Alibaba & The 70 Thieves velocity passes alone (27 tokens, 0.900 vs 0.200 = 4.50x) but minted % unverified "
 "(no verified cap found in this run's targeted searches), no project-stated X found, launch age UNVERIFIED - NOT a candidate. "
 "Agentlings velocity FAILS this interval (27 tokens, 0.900 vs 3.533 = 0.25x) and % unverified + age >24h. "
 "AgentMiner 44.1% fails >=45% and velocity fails (delta 1 < 20). BeHand velocity fails (11 tokens, 0.367 vs 1.767). "
 "SYMBOL 36.4% fails >=45% and velocity fails (10 tokens). Failed-read contracts preserved null; "
 "Agent Periodic Lab preserved unchanged per forget instruction.")
json.dump(snap, open(p, "w"), indent=1)
print("updated")
for n in cur:
    e = snap["contracts"][n]
    print(n, e["previousTotalSupply"], "->", e["totalSupply"], "delta", e["mintedInInterval"], "rate", e["ratePerMinute"], "prevRate", e["previousRatePerMinute"])
