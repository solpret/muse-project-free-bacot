#!/usr/bin/env python3
import json
snap_path = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
snap = json.load(open(snap_path))
new = {
 "AgentImps": 666, "AgentMiner": 4610, "AgentPad Pass": 1129, "Agentlings": 6781,
 "Alibaba & The 70 Thieves": 4876, "BeHand Pass": 6658, "Brutes": 5555,
 "Fleet Genesis": 1000, "Floppy Agents": 3333, "Hackou AI Pass": 92,
 "Noir Brokers": 3333, "OTV": 557, "PixelVulpes": 3333, "SYMBOL": 3906,
 "Sonic Protocol": 2237, "UMBRA Agents": 3000, "danta": 2007,
}
for name, val in new.items():
    old = snap["contracts"][name]
    prev_ts = old["totalSupply"]
    prev_rate = old["ratePerMinute"]
    delta = val - prev_ts if prev_ts is not None else None
    snap["contracts"][name] = {
        "address": old["address"],
        "previousTotalSupply": prev_ts,
        "totalSupply": val,
        "mintedInInterval": delta,
        "previousRatePerMinute": prev_rate,
        "ratePerMinute": round(delta / 30, 3) if delta is not None else None,
    }
# Failed-read contracts and Agent Periodic Lab preserved unchanged.
snap["timestamp_wib"] = "2026-11-01T03:02:00+07:00"
snap["note"] = ("Snapshot 03:02 WIB run; elapsed 30 min since 02:32 snapshot, block 130917539 at read time. "
 "NO new main candidate. NO velocity pass: Agentlings 6780->6781 delta 1 rate 0.033 vs prev 0.733 (ratio 0.05x, delta<20); "
 "BeHand 6651->6658 delta 7 rate 0.233 vs prev 0.233 (ratio 1.00x); "
 "SYMBOL 3903->3906 delta 3 rate 0.1 vs prev 0.1 (ratio 1.00x), 3906/10000=39.06% FAILS >=45%; "
 "AgentMiner 4610->4610 delta 0, 4610/9999=46.11% passes % alone but velocity FAILS and age-excluded; "
 "Alibaba 4876->4876 delta 0. Flat: AgentPad 1129, OTV 557/1500=37.1% FAILS %, Sonic 2237, danta 2007. "
 "Sold out/flat at caps: UMBRA 3000, PixelVulpes 3333, Floppy 3333, Noir 3333, Brutes 5555, Fleet 1000, AgentImps 666, Hackou 92. "
 "Failed-read contracts preserved null (Lodepass, Brushborn, BANKS/Pixel Vaults, CIOW Citizens, Chocho Agent, CyberRonin, MARS PLOTS, Synth Ape Syndicate, URBANOVA); "
 "Agent Periodic Lab preserved unchanged per forget instruction.")
json.dump(snap, open(snap_path, "w"), indent=1)
print("snapshot updated")
