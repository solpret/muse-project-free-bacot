#!/usr/bin/env python3
import json
snap_path = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
snap = json.load(open(snap_path))
old = snap["contracts"]
# reads ~21:32 WIB, block 130873523; prev snapshot 21:03:00; elapsed 29.1 min
elapsed = 29.1
new_reads = {
 "AgentImps": 666, "AgentMiner": 4556, "AgentPad Pass": 1128, "Agentlings": 6635,
 "Alibaba & The 70 Thieves": 4805, "BeHand Pass": 6581, "Brutes": 5555,
 "Fleet Genesis": 1000, "Floppy Agents": 3333, "Hackou AI Pass": 92,
 "Noir Brokers": 3333, "OTV": 557, "PixelVulpes": 3333, "SYMBOL": 3818,
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
snap["timestamp_wib"] = "2026-10-31T21:32:00+07:00"
snap["note"] = ("Snapshot 21:32 WIB run; elapsed ~29.1 min since 21:03 snapshot, block 130873523. "
 "NO new main candidate. Agentlings 6621->6635 delta 14 rate 0.481 vs prev 0.361 (1.33x, delta<20) FAILS velocity; "
 "AgentMiner 4555->4556 delta 1 rate 0.034 vs prev 0.230 FAILS; 4556/9999=45.57% passes % alone; already 24h+ age-excluded 20:01 run. "
 "Alibaba 4798->4805 delta 7 rate 0.241 vs prev 0.230 (1.05x) FAILS. BeHand 6571->6581 delta 10 rate 0.344 vs prev 0.328 (1.05x, delta<20) FAILS. "
 "SYMBOL 3815->3818 delta 3 rate 0.103 vs prev 0.557 FAILS; 3818/10000=38.18% FAILS %. "
 "Flat: Hackou 92/200=46% passes % alone but velocity FAILS; OTV 557/1500=37.1% FAILS; Sonic 2237, danta 2007, AgentPad 1128 flat. "
 "Sold out/flat at caps: UMBRA 3000, PixelVulpes 3333, Floppy 3333, Noir 3333, Brutes 5555, Fleet 1000, AgentImps 666. "
 "Failed-read contracts preserved null; Agent Periodic Lab preserved unchanged per forget instruction.")
json.dump(snap, open(snap_path, "w"), indent=1)
print("snapshot updated")
