#!/usr/bin/env python3
import json
snap_path = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
snap = json.load(open(snap_path))
# Reads ~06:33 WIB, block 130945646. Elapsed 31 min since 06:02 snapshot.
elapsed = 31
new = {
    "AgentImps": 666, "AgentMiner": 4620, "AgentPad Pass": 1129,
    "Agentlings": 6832, "Alibaba & The 70 Thieves": 4886,
    "BeHand Pass": 6676, "Brutes": 5555, "Fleet Genesis": 1000,
    "Floppy Agents": 3333, "Hackou AI Pass": 92, "Noir Brokers": 3333,
    "OTV": 558, "PixelVulpes": 3333, "SYMBOL": 3918,
    "Sonic Protocol": 2237, "UMBRA Agents": 3000, "danta": 2007,
}
for name, val in new.items():
    e = snap["contracts"][name]
    prev_total = e["totalSupply"]
    prev_rate = e["ratePerMinute"]
    e["previousTotalSupply"] = prev_total
    e["totalSupply"] = val
    e["mintedInInterval"] = val - prev_total
    e["previousRatePerMinute"] = prev_rate
    e["ratePerMinute"] = round((val - prev_total) / elapsed, 3)
snap["timestamp_wib"] = "2026-11-01T06:33:00+07:00"
snap["note"] = ("Snapshot 06:33 WIB run; elapsed 31 min since 06:02 snapshot, block 130945646 at read time. "
    "NO new main candidate. NO velocity pass: Agentlings 6831->6832 delta 1 rate 0.032 vs prev 0.300 (ratio 0.11x, FAILS, delta <20); "
    "BeHand 6674->6676 delta 2 rate 0.065 vs prev 0.067 (ratio 0.97x, FAILS, delta <20); "
    "Alibaba 4884->4886 delta 2 rate 0.065 vs prev 0.033 (ratio 1.97x but delta <20, FAILS both-legs rule); "
    "SYMBOL 3917->3918 delta 1 rate 0.032 vs prev 0.067 (ratio 0.48x, FAILS), 3918/10000=39.18% FAILS %; "
    "OTV 558->558 delta 0 (FAILS), 558/1500=37.20% FAILS %. Flat: AgentMiner 4620, AgentPad 1129, Sonic 2237, danta 2007, AgentImps 666. "
    "Sold out/flat at caps: UMBRA 3000, PixelVulpes 3333, Floppy 3333, Noir 3333, Brutes 5555, Fleet 1000, Hackou 92. "
    "Failed-read contracts preserved null (Lodepass, Brushborn, BANKS/Pixel Vaults, CIOW Citizens, Chocho Agent, CyberRonin, MARS PLOTS, Synth Ape Syndicate, URBANOVA); "
    "Agent Periodic Lab preserved unchanged per forget instruction.")
json.dump(snap, open(snap_path, "w"), indent=1)
print("updated", snap["timestamp_wib"])
