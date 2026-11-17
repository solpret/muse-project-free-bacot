#!/usr/bin/env python3
import json
snap_path = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
snap = json.load(open(snap_path))
new = {
 "AgentImps": 666, "AgentMiner": 4582, "AgentPad Pass": 1128, "Agentlings": 6713,
 "Alibaba & The 70 Thieves": 4839, "BeHand Pass": 6622, "Brutes": 5555,
 "Fleet Genesis": 1000, "Floppy Agents": 3333, "Hackou AI Pass": 92,
 "Noir Brokers": 3333, "OTV": 557, "PixelVulpes": 3333, "SYMBOL": 3858,
 "Sonic Protocol": 2237, "UMBRA Agents": 3000, "danta": 2007,
}
elapsed = 30.53
for name, cur in new.items():
    e = snap["contracts"][name]
    prev_ts, prev_rate = e["totalSupply"], e["ratePerMinute"]
    delta = cur - prev_ts if prev_ts is not None else 0
    e["previousTotalSupply"] = prev_ts
    e["previousRatePerMinute"] = prev_rate
    e["totalSupply"] = cur
    e["mintedInInterval"] = delta
    e["ratePerMinute"] = round(delta / elapsed, 3)
# Failed-read contracts + Agent Periodic Lab preserved unchanged (nulls kept)
snap["timestamp_wib"] = "2026-11-01T00:32:00+07:00"
snap["note"] = ("Snapshot 00:32 WIB run; elapsed ~30.5 min since 00:02 snapshot, block 130897543 at read time. "
 "NO new main candidate. NO contract passes velocity: Agentlings 6698->6713 delta 15 rate 0.491 vs prev 0.361 (1.36x, delta<20) FAILS; "
 "BeHand 6616->6622 delta 6 rate 0.197 vs prev 0.131 (~1.50x BUT delta<20) FAILS; SYMBOL 3847->3858 delta 11 rate 0.360 vs prev 0.459 FAILS; "
 "AgentMiner 4579->4582 delta 3 rate 0.098 vs prev 0.098 FAILS, 4582/9999=45.82% passes % alone, age-excluded 20:01 run stands; "
 "Alibaba 4837->4839 delta 2 rate 0.066 vs prev 0.164 FAILS. Flat: OTV 557/1500=37.1% FAILS %, AgentPad 1128, Sonic 2237, danta 2007. "
 "Sold out/flat at caps: UMBRA 3000, PixelVulpes 3333, Floppy 3333, Noir 3333, Brutes 5555, Fleet 1000, AgentImps 666, Hackou 92. "
 "Failed-read contracts preserved null (Lodepass, Brushborn, BANKS/Pixel Vaults, CIOW Citizens, Chocho Agent, CyberRonin, MARS PLOTS, Synth Ape Syndicate, URBANOVA); Agent Periodic Lab preserved unchanged per forget instruction.")
json.dump(snap, open(snap_path, "w"), indent=1)
print("snapshot updated")
