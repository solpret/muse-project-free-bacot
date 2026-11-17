import json
p = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
snap = json.load(open(p))
cur = {
 "AgentImps": 666, "AgentMiner": 4409, "AgentPad Pass": 1128, "Agentlings": 6282,
 "Alibaba & The 70 Thieves": 4680, "BeHand Pass": 6432, "Brutes": 5555,
 "Fleet Genesis": 1000, "Floppy Agents": 3333, "Hackou AI Pass": 90,
 "Noir Brokers": 3333, "OTV": 557, "PixelVulpes": 3333, "SYMBOL": 3650,
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
snap["timestamp_wib"] = "2026-10-31T14:32:00+07:00"
snap["note"] = ("Snapshot 14:32 WIB run; elapsed ~30 min since 14:02 snapshot. NO new main candidate: "
 "Agentlings velocity PASSES alone (174 tokens, 5.800 vs 0.900 = 6.44x) but age >24h (known since 27 Oct) blocks it as a main candidate regardless of %/velocity, and % cap + project-stated X remain unverified after this run's targeted searches - no new mint phase/batch verified, so NOT a candidate. "
 "Alibaba velocity FAILS this interval (6 tokens, 0.200 vs 0.900 = 0.22x). AgentMiner 44.1% fails >=45% and velocity fails (delta 2 < 20). "
 "BeHand velocity fails (8 tokens, 0.267 vs 0.367). SYMBOL 36.5% fails >=45% and velocity fails (12 tokens). "
 "Failed-read contracts preserved null; Agent Periodic Lab preserved unchanged per forget instruction.")
json.dump(snap, open(p, "w"), indent=1)
print("updated")
for n in cur:
    e = snap["contracts"][n]
    print(n, e["previousTotalSupply"], "->", e["totalSupply"], "delta", e["mintedInInterval"], "rate", e["ratePerMinute"], "prevRate", e["previousRatePerMinute"])
