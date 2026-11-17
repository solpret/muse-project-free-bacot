import json
path = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
snap = json.load(open(path))
elapsed = 30  # 16:32 -> ~17:02 WIB, block 130837579
new = {
 "AgentImps": 666, "AgentMiner": 4469, "AgentPad Pass": 1128, "Agentlings": 6449,
 "Alibaba & The 70 Thieves": 4713, "BeHand Pass": 6490, "Brutes": 5555,
 "Fleet Genesis": 1000, "Floppy Agents": 3333, "Hackou AI Pass": 90, "Noir Brokers": 3333,
 "OTV": 557, "PixelVulpes": 3333, "SYMBOL": 3749, "Sonic Protocol": 2237,
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
snap["timestamp_wib"] = "2026-10-31T17:02:00+07:00"
snap["note"] = ("Snapshot 17:02 WIB run; elapsed ~30 min since 16:32 snapshot, block 130837579. NO new main candidate: NO project passes BOTH >=45% AND velocity >=1.5x with >=20 minted. "
 "AgentMiner 4468->4469 delta 1 rate 0.033 vs prev 0.400 (0.08x) FAILS velocity and 4469/9999=44.7% FAILS >=45%. "
 "SYMBOL 3735->3749 delta 14 rate 0.467 vs prev 1.200 (0.39x) FAILS velocity and 3749/10000=37.5% FAILS >=45%. "
 "Agentlings 6434->6449 delta 15 rate 0.500 vs 0.600 (0.83x, <20) FAILS velocity; age >24h blocks anyway. "
 "BeHand 6480->6490 delta 10 rate 0.333 vs 0.267 (1.25x, <20) FAILS velocity. Alibaba delta 2 FAILS. "
 "OTV 557/1500=37.1% flat FAILS. Hackou 90/200=45.0% meets % alone but delta 0 FAILS velocity. "
 "Sold out/flat at caps: UMBRA 3000, PixelVulpes 3333, Floppy 3333, Noir 3333, Brutes 5555, Fleet 1000, AgentImps 666. "
 "Failed-read contracts preserved null; Agent Periodic Lab preserved unchanged per forget instruction.")
json.dump(snap, open(path, "w"), indent=1)
print("updated", snap["timestamp_wib"])
