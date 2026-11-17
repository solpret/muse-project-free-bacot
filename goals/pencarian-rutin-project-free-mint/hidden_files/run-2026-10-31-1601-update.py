import json
path = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
snap = json.load(open(path))
# previous snapshot timestamp 15:32, reads ~16:02 => elapsed 30 min
elapsed = 30
new = {
 "AgentImps": 666, "AgentMiner": 4456, "AgentPad Pass": 1128, "Agentlings": 6416,
 "Alibaba & The 70 Thieves": 4708, "BeHand Pass": 6472, "Brutes": 5555,
 "Fleet Genesis": 1000, "Floppy Agents": 3333, "Hackou AI Pass": 90, "Noir Brokers": 3333,
 "OTV": 557, "PixelVulpes": 3333, "SYMBOL": 3699, "Sonic Protocol": 2237,
 "UMBRA Agents": 3000, "danta": 2007,
}
for name, cur in new.items():
    e = snap["contracts"][name]
    prev_ts = e["totalSupply"]
    prev_rate = e["ratePerMinute"]
    delta = cur - prev_ts if prev_ts is not None else None
    rate = round(delta/elapsed, 3) if delta is not None else None
    e["previousTotalSupply"] = prev_ts
    e["previousRatePerMinute"] = prev_rate
    e["totalSupply"] = cur
    e["mintedInInterval"] = delta
    e["ratePerMinute"] = rate
# failed-read contracts + Agent Periodic Lab preserved unchanged
snap["timestamp_wib"] = "2026-10-31T16:02:00+07:00"
snap["note"] = ("Snapshot 16:02 WIB run; elapsed ~30 min since 15:32 snapshot. NO new main candidate: NO project passes BOTH >=45% AND velocity >=1.5x with >=20 minted. "
 "AgentMiner delta 38, rate 1.267 vs previous 0.167 (7.59x, passes velocity) BUT 4456/9999 = 44.6% FAILS >=45% (closest item, watch next run). "
 "SYMBOL delta 27, rate 0.900 vs 0.333 (2.70x, passes velocity) BUT 3699/10000 = 37.0% FAILS >=45%. "
 "Agentlings delta 24, rate 0.800 vs 1.967 (0.41x) FAILS velocity; age >24h blocks anyway. "
 "Alibaba delta 8 FAILS; BeHand delta 13 (0.433 vs 0.333 = 1.30x, <20) FAILS. "
 "OTV 557/1500 = 37.1% FAILS, flat. Hackou 90/200 = 45.0% meets % alone but delta 0 FAILS velocity. "
 "Sold out/flat at caps: UMBRA 3000, PixelVulpes 3333, Floppy 3333, Noir 3333, Brutes 5555, Fleet 1000, AgentImps 666. "
 "Failed-read contracts preserved null; Agent Periodic Lab preserved unchanged per forget instruction.")
json.dump(snap, open(path, "w"), indent=1)
print("updated", snap["timestamp_wib"])
