import json
p = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
snap = json.load(open(p))
cur = {
 "AgentImps": 666, "AgentMiner": 4418, "AgentPad Pass": 1128, "Agentlings": 6392,
 "Alibaba & The 70 Thieves": 4700, "BeHand Pass": 6459, "Brutes": 5555,
 "Fleet Genesis": 1000, "Floppy Agents": 3333, "Hackou AI Pass": 90,
 "Noir Brokers": 3333, "OTV": 557, "PixelVulpes": 3333, "SYMBOL": 3672,
 "Sonic Protocol": 2237, "UMBRA Agents": 3000, "danta": 2007,
}
for name, new_ts in cur.items():
    e = snap["contracts"][name]
    old_ts = e["totalSupply"]; old_rate = e["ratePerMinute"]
    delta = new_ts - old_ts if old_ts is not None else None
    rate = round(delta / 30, 3) if delta is not None else None
    e["previousTotalSupply"] = old_ts; e["previousRatePerMinute"] = old_rate
    e["totalSupply"] = new_ts; e["mintedInInterval"] = delta; e["ratePerMinute"] = rate
snap["timestamp_wib"] = "2026-10-31T15:32:00+07:00"
snap["note"] = ("Snapshot 15:32 WIB run; elapsed ~30 min since 15:02 snapshot. NO new main candidate: NO project passes the on-chain signal this interval. "
 "Agentlings delta 59 but rate 1.967 vs previous 1.700 (1.16x) FAILS velocity, and age >24h (known since 27 Oct) blocks it anyway. "
 "AgentMiner 4418/9999 = 44.2% FAILS >=45% and velocity fails (delta 5, 0.167 vs 0.133 = 1.25x, <20). "
 "Alibaba delta 7 (0.233 vs 0.433 = 0.54x) FAILS velocity. BeHand delta 10 (0.333 vs 0.567 = 0.59x) FAILS velocity. "
 "SYMBOL 3672/10000 = 36.7% FAILS >=45% and velocity fails (delta 10, 0.333 vs 0.400 = 0.83x). "
 "OTV 557/1500 = 37.1% FAILS >=45%, velocity fails. Hackou 90/200 = 45.0% meets % alone but velocity fails (delta 0). "
 "Failed-read contracts preserved null; Agent Periodic Lab preserved unchanged per forget instruction.")
json.dump(snap, open(p, "w"), indent=1)
print("updated")
for n in cur:
    e = snap["contracts"][n]
    print(n, e["previousTotalSupply"], "->", e["totalSupply"], "delta", e["mintedInInterval"], "rate", e["ratePerMinute"], "prevRate", e["previousRatePerMinute"])
