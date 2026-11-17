#!/usr/bin/env python3
import json
snap_path = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
snap = json.load(open(snap_path))
# Reads ~21:02 WIB; previous snapshot 2026-10-31T20:32:00+07:00 -> elapsed ~30.5 min
elapsed = 30.5
reads = {
 "AgentImps": 666, "AgentMiner": 4555, "AgentPad Pass": 1128, "Agentlings": 6621,
 "Alibaba & The 70 Thieves": 4798, "BeHand Pass": 6571, "Brutes": 5555,
 "Fleet Genesis": 1000, "Floppy Agents": 3333, "Hackou AI Pass": 92,
 "Noir Brokers": 3333, "OTV": 557, "PixelVulpes": 3333, "SYMBOL": 3815,
 "Sonic Protocol": 2237, "UMBRA Agents": 3000, "danta": 2007,
}
for name, cur in reads.items():
    e = snap["contracts"][name]
    prev_ts = e["totalSupply"]
    prev_rate = e["ratePerMinute"]
    delta = (cur - prev_ts) if prev_ts is not None else None
    rate = round(delta / elapsed, 3) if delta is not None else None
    e["previousTotalSupply"] = prev_ts
    e["previousRatePerMinute"] = prev_rate
    e["totalSupply"] = cur
    e["mintedInInterval"] = delta
    e["ratePerMinute"] = rate
snap["timestamp_wib"] = "2026-10-31T21:03:00+07:00"
snap["note"] = ("Snapshot 21:03 WIB run; elapsed ~30.5 min since 20:32 snapshot, block 130869546. "
 "NO new main candidate. Agentlings 6610->6621 delta 11 rate 0.361 vs prev 1.133 (0.32x) FAILS velocity; % unverified, known since 27 Oct (>24h). "
 "AgentMiner 4548->4555 delta 7 rate 0.230 vs prev 0.400 (0.57x) FAILS; 4555/9999=45.56% passes % alone; already 24h+ age-excluded 20:01 run. "
 "Alibaba 4791->4798 delta 7 FAILS. BeHand 6561->6571 delta 10 rate 0.328 vs prev 0.267 (1.23x, delta<20) FAILS. "
 "SYMBOL 3798->3815 delta 17 rate 0.557 vs prev 0.300 (1.86x but delta<20) FAILS velocity; 3815/10000=38.15% FAILS %. "
 "Flat: Hackou 92/200=46% passes % alone but velocity FAILS; OTV 557/1500=37.1% FAILS; Sonic 2237, danta 2007, AgentPad 1128 flat. "
 "Sold out/flat at caps: UMBRA 3000, PixelVulpes 3333, Floppy 3333, Noir 3333, Brutes 5555, Fleet 1000, AgentImps 666. "
 "Failed-read contracts preserved null; Agent Periodic Lab preserved unchanged per forget instruction.")
json.dump(snap, open(snap_path, "w"), indent=1)
print("updated")
for n in reads:
    e = snap["contracts"][n]
    print(n, e["previousTotalSupply"], "->", e["totalSupply"], "delta", e["mintedInInterval"], "rate", e["ratePerMinute"], "prevRate", e["previousRatePerMinute"])
