#!/usr/bin/env python3
import json
p = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
snap = json.load(open(p))
cur = {
 "AgentImps": 666, "AgentMiner": 4401, "AgentPad Pass": 1128, "Agentlings": 5975,
 "Alibaba & The 70 Thieves": 4641, "BeHand Pass": 6360, "Brutes": 5555,
 "Fleet Genesis": 1000, "Floppy Agents": 3333, "Hackou AI Pass": 90,
 "Noir Brokers": 3333, "OTV": 557, "PixelVulpes": 3333, "SYMBOL": 3571,
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
snap["timestamp_wib"] = "2026-10-31T13:02:00+07:00"
snap["note"] = ("Snapshot 13:02 WIB run; elapsed ~30 min since 12:32 snapshot. NO new main candidate: "
 "Agentlings velocity passes alone (33 tokens, 1.100 vs 0.733 = 1.50x) but minted % unverified (no verified cap), "
 "no project-stated X, and age >24h (known since 27 Oct) — NOT a candidate. AgentMiner 44.0% fails >=45% and "
 "velocity fails (delta 2 < 20). All other movers fail velocity and/or %. Failed-read contracts preserved null; "
 "Agent Periodic Lab preserved unchanged per forget instruction.")
json.dump(snap, open(p, "w"), indent=1)
print("updated")
for n in cur:
    e = snap["contracts"][n]
    print(n, e["previousTotalSupply"], "->", e["totalSupply"], "delta", e["mintedInInterval"], "rate", e["ratePerMinute"], "prevRate", e["previousRatePerMinute"])
