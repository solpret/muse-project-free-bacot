import json
p = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
snap = json.load(open(p))
# reads ~01:02 WIB, block 130901546; prev snapshot 2026-11-01T00:32:00+07:00, elapsed 30 min
elapsed = 30.0
new = {
 "AgentImps": 666, "AgentMiner": 4590, "AgentPad Pass": 1129, "Agentlings": 6721,
 "Alibaba & The 70 Thieves": 4859, "BeHand Pass": 6631, "Brutes": 5555,
 "Fleet Genesis": 1000, "Floppy Agents": 3333, "Hackou AI Pass": 92,
 "Noir Brokers": 3333, "OTV": 557, "PixelVulpes": 3333, "SYMBOL": 3883,
 "Sonic Protocol": 2237, "UMBRA Agents": 3000, "danta": 2007,
}
for name, val in new.items():
    c = snap["contracts"][name]
    prev = c["totalSupply"]
    delta = val - prev if prev is not None else None
    c["previousTotalSupply"] = prev
    c["previousRatePerMinute"] = c["ratePerMinute"]
    c["totalSupply"] = val
    c["mintedInInterval"] = delta
    c["ratePerMinute"] = round(delta/elapsed, 3) if delta is not None else None
snap["timestamp_wib"] = "2026-11-01T01:02:00+07:00"
snap["note"] = "Snapshot 01:02 WIB run; elapsed 30 min since 00:32 snapshot, block 130901546 at read time. NO new main candidate. Velocity PASSES but other gates FAIL: Alibaba 4839->4859 delta 20 rate 0.667 vs prev 0.066 (10.1x) but % unverified, known since 28 Oct (>24h), X account not stated; SYMBOL 3858->3883 delta 25 rate 0.833 vs prev 0.360 (2.31x) but 3883/10000=38.8% FAILS >=45%, X fails historically, known since 28 Oct (>24h). Others FAIL velocity: AgentMiner 4582->4590 delta 8 rate 0.267 vs prev 0.098 (delta<20), 4590/9999=45.90% passes % alone but age-excluded; Agentlings 6713->6721 delta 8 rate 0.267 vs prev 0.491; BeHand 6622->6631 delta 9 rate 0.300 vs prev 0.197 (delta<20); AgentPad 1128->1129 delta 1. Flat: OTV 557/1500=37.1% FAILS %, Sonic 2237, danta 2007. Sold out/flat at caps: UMBRA 3000, PixelVulpes 3333, Floppy 3333, Noir 3333, Brutes 5555, Fleet 1000, AgentImps 666, Hackou 92. Failed-read contracts preserved null (Lodepass, Brushborn, BANKS/Pixel Vaults, CIOW Citizens, Chocho Agent, CyberRonin, MARS PLOTS, Synth Ape Syndicate, URBANOVA); Agent Periodic Lab preserved unchanged per forget instruction."
json.dump(snap, open(p, "w"), indent=1)
print("updated", snap["timestamp_wib"])
