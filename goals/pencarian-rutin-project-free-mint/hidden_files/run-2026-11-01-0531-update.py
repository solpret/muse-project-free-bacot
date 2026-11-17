#!/usr/bin/env python3
import json
snap_path = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
snap = json.load(open(snap_path))
new = {
 "AgentImps": 666, "AgentMiner": 4618, "AgentPad Pass": 1129, "Agentlings": 6822,
 "Alibaba & The 70 Thieves": 4883, "BeHand Pass": 6672, "Brutes": 5555,
 "Fleet Genesis": 1000, "Floppy Agents": 3333, "Hackou AI Pass": 92,
 "Noir Brokers": 3333, "OTV": 557, "PixelVulpes": 3333, "SYMBOL": 3915,
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
        "ratePerMinute": round(delta / 29, 3) if delta is not None else None,
    }
snap["timestamp_wib"] = "2026-11-01T05:32:00+07:00"
snap["note"] = ("Snapshot 05:32 WIB run; elapsed 29 min since 05:03 snapshot, block 130937563 at read time. "
 "NO new main candidate. NO velocity pass: Agentlings 6816->6822 delta 6 rate 0.207 vs prev 0.1 (ratio 2.07x but delta <20, FAILS); "
 "BeHand 6666->6672 delta 6 rate 0.207 vs prev 0.033 (ratio 6.27x but delta <20, FAILS); "
 "AgentMiner 4616->4618 delta 2 rate 0.069 vs prev 0.033 (ratio 2.09x but delta <20, FAILS), 4618/9999=46.19% passes % alone but age-excluded stands; "
 "Alibaba 4881->4883 delta 2 rate 0.069 vs prev 0.067 (ratio 1.03x, FAILS, delta <20); "
 "SYMBOL 3913->3915 delta 2 rate 0.069 vs prev 0.1 (ratio 0.69x, FAILS), 3915/10000=39.15% FAILS %. "
 "Flat: AgentPad 1129, OTV 557/1500=37.13% FAILS %, Sonic 2237, danta 2007, AgentImps 666. "
 "Sold out/flat at caps: UMBRA 3000, PixelVulpes 3333, Floppy 3333, Noir 3333, Brutes 5555, Fleet 1000, Hackou 92. "
 "Failed-read contracts preserved null (Lodepass, Brushborn, BANKS/Pixel Vaults, CIOW Citizens, Chocho Agent, CyberRonin, MARS PLOTS, Synth Ape Syndicate, URBANOVA); "
 "Agent Periodic Lab preserved unchanged per forget instruction.")
json.dump(snap, open(snap_path, "w"), indent=1)
print("snapshot updated")
