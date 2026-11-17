import json
p = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
snap = json.load(open(p))
cur = {
 "AgentImps": 666, "AgentMiner": 4413, "AgentPad Pass": 1128, "Agentlings": 6333,
 "Alibaba & The 70 Thieves": 4693, "BeHand Pass": 6449, "Brutes": 5555,
 "Fleet Genesis": 1000, "Floppy Agents": 3333, "Hackou AI Pass": 90,
 "Noir Brokers": 3333, "OTV": 557, "PixelVulpes": 3333, "SYMBOL": 3662,
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
snap["timestamp_wib"] = "2026-10-31T15:02:00+07:00"
snap["note"] = ("Snapshot 15:02 WIB run; elapsed ~30 min since 14:32 snapshot. NO new main candidate: NO project passes the on-chain signal this interval. "
 "Agentlings delta 51 but rate 1.700 vs previous 5.800 (0.29x) FAILS velocity, and age >24h (known since 27 Oct) blocks it anyway. "
 "Alibaba delta 13 (0.433 vs 0.200 = 2.17x but delta < 20) FAILS velocity. BeHand delta 17 (0.567 vs 0.267 = 2.12x but delta < 20) FAILS velocity. "
 "AgentMiner 4413/9999 = 44.1% FAILS >=45% and velocity fails (delta 4 < 20). SYMBOL 3662/10000 = 36.6% FAILS >=45% and velocity fails (12 tokens, 0.400 vs 0.400 = 1.00x). "
 "OTV 557/1500 = 37.1% FAILS >=45%, velocity fails. Hackou 90/200 = 45.0% meets % alone but velocity fails (delta 0). "
 "Failed-read contracts preserved null; Agent Periodic Lab preserved unchanged per forget instruction.")
json.dump(snap, open(p, "w"), indent=1)
print("updated")
for n in cur:
    e = snap["contracts"][n]
    print(n, e["previousTotalSupply"], "->", e["totalSupply"], "delta", e["mintedInInterval"], "rate", e["ratePerMinute"], "prevRate", e["previousRatePerMinute"])
