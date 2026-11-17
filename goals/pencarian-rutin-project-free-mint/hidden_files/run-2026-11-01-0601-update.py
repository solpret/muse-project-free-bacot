#!/usr/bin/env python3
import json
snap_path = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
snap = json.load(open(snap_path))
new = {
 "AgentImps": 666, "AgentMiner": 4620, "AgentPad Pass": 1129,
 "Agentlings": 6831, "Alibaba & The 70 Thieves": 4884,
 "BeHand Pass": 6674, "Brutes": 5555, "Fleet Genesis": 1000,
 "Floppy Agents": 3333, "Hackou AI Pass": 92, "Noir Brokers": 3333,
 "OTV": 558, "PixelVulpes": 3333, "SYMBOL": 3917,
 "Sonic Protocol": 2237, "UMBRA Agents": 3000, "danta": 2007,
}
elapsed = 30  # minutes, 05:32 -> 06:02 WIB
for name, cur in new.items():
    e = snap["contracts"][name]
    prev_ts = e["totalSupply"]
    prev_rate = e["ratePerMinute"]
    delta = cur - prev_ts
    e["previousTotalSupply"] = prev_ts
    e["totalSupply"] = cur
    e["mintedInInterval"] = delta
    e["previousRatePerMinute"] = prev_rate
    e["ratePerMinute"] = round(delta / elapsed, 3)
snap["timestamp_wib"] = "2026-11-01T06:02:00+07:00"
snap["note"] = ("Snapshot 06:02 WIB run; elapsed 30 min since 05:32 snapshot, block 130941546 at read time. "
 "NO new main candidate. NO velocity pass: Agentlings 6822->6831 delta 9 rate 0.300 vs prev 0.207 (ratio 1.45x <1.5x AND delta <20, FAILS); "
 "AgentMiner 4618->4620 delta 2 rate 0.067 vs prev 0.069 (ratio 0.97x, FAILS, delta <20), 4620/9999=46.21% passes % alone but age-excluded stands; "
 "BeHand 6672->6674 delta 2 rate 0.067 vs prev 0.207 (ratio 0.32x, FAILS); Alibaba 4883->4884 delta 1 rate 0.033 vs prev 0.069 (ratio 0.48x, FAILS); "
 "SYMBOL 3915->3917 delta 2 rate 0.067 vs prev 0.069 (ratio 0.97x, FAILS), 3917/10000=39.17% FAILS %; OTV 557->558 delta 1 rate 0.033 vs prev 0.0 (delta <20, FAILS), 558/1500=37.20% FAILS %. "
 "Flat: AgentPad 1129, Sonic 2237, danta 2007, AgentImps 666. Sold out/flat at caps: UMBRA 3000, PixelVulpes 3333, Floppy 3333, Noir 3333, Brutes 5555, Fleet 1000, Hackou 92. "
 "Failed-read contracts preserved null (Lodepass, Brushborn, BANKS/Pixel Vaults, CIOW Citizens, Chocho Agent, CyberRonin, MARS PLOTS, Synth Ape Syndicate, URBANOVA); Agent Periodic Lab preserved unchanged per forget instruction.")
json.dump(snap, open(snap_path, "w"), indent=1)
print("snapshot updated")
