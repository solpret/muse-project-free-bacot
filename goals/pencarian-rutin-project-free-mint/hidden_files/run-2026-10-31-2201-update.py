#!/usr/bin/env python3
import json
snap_path = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
snap = json.load(open(snap_path))
old = snap["contracts"]
elapsed = 30.0
new_reads = {
 "AgentImps": 666, "AgentMiner": 4558, "AgentPad Pass": 1128, "Agentlings": 6645,
 "Alibaba & The 70 Thieves": 4810, "BeHand Pass": 6585, "Brutes": 5555,
 "Fleet Genesis": 1000, "Floppy Agents": 3333, "Hackou AI Pass": 92,
 "Noir Brokers": 3333, "OTV": 557, "PixelVulpes": 3333, "SYMBOL": 3821,
 "Sonic Protocol": 2237, "UMBRA Agents": 3000, "danta": 2007,
}
for name, cur in new_reads.items():
    prev = old[name]["totalSupply"]
    rate = round((cur - prev) / elapsed, 3) if prev is not None else None
    old[name] = {
        "address": old[name]["address"],
        "previousTotalSupply": prev,
        "totalSupply": cur,
        "mintedInInterval": (cur - prev) if prev is not None else None,
        "previousRatePerMinute": old[name]["ratePerMinute"],
        "ratePerMinute": rate,
    }
snap["timestamp_wib"] = "2026-10-31T22:02:00+07:00"
snap["note"] = ("Snapshot 22:02 WIB run; elapsed ~30.0 min since 21:32 snapshot, block 130877522. "
 "NO new main candidate. AgentMiner 4556->4558 delta 2 rate 0.067 vs prev 0.034 (1.96x but delta<20) FAILS velocity; "
 "4558/9999=45.59% passes % alone; already 24h+ age-excluded 20:01 run. Agentlings 6635->6645 delta 10 rate 0.333 vs prev 0.481 FAILS. "
 "Alibaba 4805->4810 delta 5 rate 0.167 vs prev 0.241 FAILS. BeHand 6581->6585 delta 4 rate 0.133 vs prev 0.344 FAILS. "
 "SYMBOL 3818->3821 delta 3 rate 0.100 vs prev 0.103 FAILS; 3821/10000=38.21% FAILS %. "
 "Flat: Hackou 92/200=46% passes % alone but velocity FAILS; OTV 557/1500=37.1% FAILS; Sonic 2237, danta 2007, AgentPad 1128 flat. "
 "Sold out/flat at caps: UMBRA 3000, PixelVulpes 3333, Floppy 3333, Noir 3333, Brutes 5555, Fleet 1000, AgentImps 666. "
 "Failed-read contracts preserved null; Agent Periodic Lab preserved unchanged per forget instruction.")
json.dump(snap, open(snap_path, "w"), indent=1)
print("snapshot updated")
