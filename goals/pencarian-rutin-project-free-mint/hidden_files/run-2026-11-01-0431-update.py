#!/usr/bin/env python3
import json
snap_path = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
snap = json.load(open(snap_path))
new = {
 "AgentImps": 666, "AgentMiner": 4615, "AgentPad Pass": 1129, "Agentlings": 6813,
 "Alibaba & The 70 Thieves": 4879, "BeHand Pass": 6665, "Brutes": 5555,
 "Fleet Genesis": 1000, "Floppy Agents": 3333, "Hackou AI Pass": 92,
 "Noir Brokers": 3333, "OTV": 557, "PixelVulpes": 3333, "SYMBOL": 3910,
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
snap["timestamp_wib"] = "2026-11-01T04:33:00+07:00"
snap["note"] = ("Snapshot 04:33 WIB run; elapsed 30 min since 04:03 snapshot, block 130929528 at read time. "
 "NO new main candidate. NO velocity pass (all deltas <20): Agentlings 6811->6813 delta 2 rate 0.067 vs prev 0.1 (ratio 0.67x, FAILS); "
 "BeHand 6663->6665 delta 2 rate 0.067 vs prev 0.1 (ratio 0.67x, FAILS); "
 "AgentMiner 4614->4615 delta 1 rate 0.033 vs prev 0.067 (ratio 0.5x, FAILS), 4615/9999=46.16% passes % alone but age-excluded stands; "
 "Alibaba 4878->4879 delta 1 rate 0.033 vs prev 0.033 (ratio 1.0x, FAILS); SYMBOL flat 3910/10000=39.1% FAILS %. "
 "Flat: AgentPad 1129, OTV 557/1500=37.13% FAILS %, Sonic 2237, danta 2007, AgentImps 666. "
 "Sold out/flat at caps: UMBRA 3000, PixelVulpes 3333, Floppy 3333, Noir 3333, Brutes 5555, Fleet 1000, Hackou 92. "
 "Failed-read contracts preserved null (Lodepass, Brushborn, BANKS/Pixel Vaults, CIOW Citizens, Chocho Agent, CyberRonin, MARS PLOTS, Synth Ape Syndicate, URBANOVA); "
 "Agent Periodic Lab preserved unchanged per forget instruction.")
json.dump(snap, open(snap_path, "w"), indent=1)
print("snapshot updated")
