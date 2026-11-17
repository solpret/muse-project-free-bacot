import json
path = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
snap = json.load(open(path))
elapsed = 30  # 17:02 -> ~17:32 WIB, block 130841537
new = {
 "AgentImps": 666, "AgentMiner": 4470, "AgentPad Pass": 1128, "Agentlings": 6491,
 "Alibaba & The 70 Thieves": 4717, "BeHand Pass": 6499, "Brutes": 5555,
 "Fleet Genesis": 1000, "Floppy Agents": 3333, "Hackou AI Pass": 90, "Noir Brokers": 3333,
 "OTV": 557, "PixelVulpes": 3333, "SYMBOL": 3756, "Sonic Protocol": 2237,
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
snap["timestamp_wib"] = "2026-10-31T17:32:00+07:00"
snap["note"] = ("Snapshot 17:32 WIB run; elapsed ~30 min since 17:02 snapshot, block 130841537. NO new main candidate. "
 "Agentlings 6449->6491 delta 42 rate 1.400 vs prev 0.500 (2.80x, >=20) PASSES velocity alone, BUT minted % UNVERIFIED (maxSupply view reverts in prior deep-dives; no verified cap), no project-stated X account found, and known since 27 Oct (>24h evidence) — NOT a full on-chain pass and NOT a candidate. "
 "AgentMiner 4469->4470 delta 1 rate 0.033 vs 0.033 (1.00x) FAILS velocity and 4470/9999=44.7% FAILS >=45%. "
 "SYMBOL 3749->3756 delta 7 rate 0.233 vs 0.467 (0.50x) FAILS velocity and 3756/10000=37.6% FAILS >=45%. "
 "BeHand 6490->6499 delta 9 rate 0.300 vs 0.333 (0.90x, <20) FAILS. Alibaba delta 4 (<20) FAILS. "
 "OTV 557/1500=37.1% flat FAILS. Hackou 90/200=45.0% meets % alone but delta 0 FAILS velocity. "
 "Sold out/flat at caps: UMBRA 3000, PixelVulpes 3333, Floppy 3333, Noir 3333, Brutes 5555, Fleet 1000, AgentImps 666. "
 "Failed-read contracts preserved null; Agent Periodic Lab preserved unchanged per forget instruction.")
json.dump(snap, open(path, "w"), indent=1)
print("updated", snap["timestamp_wib"])
