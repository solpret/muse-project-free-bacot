import json
path = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
snap = json.load(open(path))
elapsed = 30  # 16:02 -> ~16:32 WIB, block 130833543
new = {
 "AgentImps": 666, "AgentMiner": 4468, "AgentPad Pass": 1128, "Agentlings": 6434,
 "Alibaba & The 70 Thieves": 4711, "BeHand Pass": 6480, "Brutes": 5555,
 "Fleet Genesis": 1000, "Floppy Agents": 3333, "Hackou AI Pass": 90, "Noir Brokers": 3333,
 "OTV": 557, "PixelVulpes": 3333, "SYMBOL": 3735, "Sonic Protocol": 2237,
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
snap["timestamp_wib"] = "2026-10-31T16:32:00+07:00"
snap["note"] = ("Snapshot 16:32 WIB run; elapsed ~30 min since 16:02 snapshot, block 130833543. NO new main candidate: NO project passes BOTH >=45% AND velocity >=1.5x with >=20 minted. "
 "AgentMiner 4456->4468 delta 12 rate 0.400 vs prev 1.267 (0.32x) FAILS velocity and 4468/9999=44.7% FAILS >=45% (still closest, now failing both). "
 "SYMBOL 3699->3735 delta 36 rate 1.200 vs prev 0.900 (1.33x) FAILS velocity and 3735/10000=37.4% FAILS >=45%. "
 "Agentlings 6416->6434 delta 18 rate 0.600 vs 0.800 (0.75x, <20) FAILS velocity; age >24h blocks anyway. "
 "BeHand delta 8 FAILS; Alibaba delta 3 FAILS. OTV 557/1500=37.1% flat FAILS. Hackou 90/200=45.0% meets % alone but delta 0 FAILS velocity. "
 "Sold out/flat at caps: UMBRA 3000, PixelVulpes 3333, Floppy 3333, Noir 3333, Brutes 5555, Fleet 1000, AgentImps 666. "
 "Failed-read contracts preserved null; Agent Periodic Lab preserved unchanged per forget instruction.")
json.dump(snap, open(path, "w"), indent=1)
print("updated", snap["timestamp_wib"])
