#!/usr/bin/env python3
import json
snap_path = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
snap = json.load(open(snap_path))
new = {
 "AgentImps": 666, "AgentMiner": 4610, "AgentPad Pass": 1129, "Agentlings": 6780,
 "Alibaba & The 70 Thieves": 4876, "BeHand Pass": 6651, "Brutes": 5555,
 "Fleet Genesis": 1000, "Floppy Agents": 3333, "Hackou AI Pass": 92,
 "Noir Brokers": 3333, "OTV": 557, "PixelVulpes": 3333, "SYMBOL": 3903,
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
snap["timestamp_wib"] = "2026-11-01T02:32:00+07:00"
snap["note"] = ("Snapshot 02:32 WIB run; elapsed 30 min since 02:02 snapshot, block 130913543 at read time. "
 "NO new main candidate. NO velocity pass: Agentlings 6758->6780 delta 22 rate 0.733 vs prev 0.733 (ratio 1.00x <1.5x, velocity FAILS despite delta>=20); "
 "AgentMiner 4608->4610 delta 2 rate 0.067 vs prev 0.167, 4610/9999=46.11% passes % alone but velocity FAILS and age-excluded; "
 "SYMBOL 3900->3903 delta 3 rate 0.1 vs prev 0.267, 3903/10000=39.03% FAILS >=45%; Alibaba 4873->4876 delta 3 rate 0.1 vs prev 0.267; "
 "BeHand 6644->6651 delta 7 rate 0.233 vs prev 0.233 (ratio 1.00x). Flat: AgentPad 1129, OTV 557/1500=37.1% FAILS %, Sonic 2237, danta 2007. "
 "Sold out/flat at caps: UMBRA 3000, PixelVulpes 3333, Floppy 3333, Noir 3333, Brutes 5555, Fleet 1000, AgentImps 666, Hackou 92. "
 "Failed-read contracts preserved null (Lodepass, Brushborn, BANKS/Pixel Vaults, CIOW Citizens, Chocho Agent, CyberRonin, MARS PLOTS, Synth Ape Syndicate, URBANOVA); "
 "Agent Periodic Lab preserved unchanged per forget instruction.")
json.dump(snap, open(snap_path, "w"), indent=1)
print("snapshot updated")
