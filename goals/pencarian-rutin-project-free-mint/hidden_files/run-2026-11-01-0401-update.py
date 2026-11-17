#!/usr/bin/env python3
import json
snap_path = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
snap = json.load(open(snap_path))
new = {
 "AgentImps": 666, "AgentMiner": 4614, "AgentPad Pass": 1129, "Agentlings": 6811,
 "Alibaba & The 70 Thieves": 4878, "BeHand Pass": 6663, "Brutes": 5555,
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
# Failed-read contracts and Agent Periodic Lab preserved unchanged.
snap["timestamp_wib"] = "2026-11-01T04:03:00+07:00"
snap["note"] = ("Snapshot 04:03 WIB run; elapsed 30 min since 03:32 snapshot, block 130925542 at read time. "
 "NO new main candidate. NO velocity pass this run (all deltas <20): Agentlings 6808->6811 delta 3 rate 0.1 vs prev 0.9 (ratio 0.11x, FAILS); "
 "BeHand 6660->6663 delta 3 rate 0.1 vs prev 0.067 (ratio 1.49x, below 1.5x and delta<20, FAILS); "
 "SYMBOL 3907->3910 delta 3 rate 0.1 vs prev 0.033 (ratio ~3x but delta<20, FAILS), 3910/10000=39.1% FAILS >=45%; "
 "AgentMiner 4612->4614 delta 2 rate 0.067 vs prev 0.067 (ratio 1.0x, delta<20, FAILS), 4614/9999=46.14% passes % alone but age-excluded stands; "
 "Alibaba 4877->4878 delta 1 rate 0.033 vs prev 0.033 (FAILS). "
 "Flat: AgentPad 1129, OTV 557/1500=37.13% FAILS %, Sonic 2237, danta 2007, AgentImps 666. "
 "Sold out/flat at caps: UMBRA 3000, PixelVulpes 3333, Floppy 3333, Noir 3333, Brutes 5555, Fleet 1000, Hackou 92. "
 "Failed-read contracts preserved null (Lodepass, Brushborn, BANKS/Pixel Vaults, CIOW Citizens, Chocho Agent, CyberRonin, MARS PLOTS, Synth Ape Syndicate, URBANOVA); "
 "Agent Periodic Lab preserved unchanged per forget instruction.")
json.dump(snap, open(snap_path, "w"), indent=1)
print("snapshot updated")
