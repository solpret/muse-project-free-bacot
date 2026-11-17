import json
snap_path = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
snap = json.load(open(snap_path))
elapsed = 29.73  # minutes, 07:33:00 -> 08:02:44 WIB
new = {
 "AgentImps": 666, "AgentMiner": 4629, "AgentPad Pass": 1129, "Agentlings": 6858,
 "Alibaba & The 70 Thieves": 4892, "BeHand Pass": 6689, "Brutes": 5555,
 "Fleet Genesis": 1000, "Floppy Agents": 3333, "Hackou AI Pass": 92,
 "Noir Brokers": 3333, "OTV": 558, "PixelVulpes": 3333, "SYMBOL": 3944,
 "Sonic Protocol": 2237, "UMBRA Agents": 3000, "danta": 2007,
}
for name, val in new.items():
    e = snap["contracts"][name]
    prev_ts, prev_rate = e["totalSupply"], e["ratePerMinute"]
    delta = val - prev_ts if prev_ts is not None else None
    rate = round(delta / elapsed, 3) if delta is not None else None
    e["previousTotalSupply"], e["previousRatePerMinute"] = prev_ts, prev_rate
    e["totalSupply"], e["mintedInInterval"], e["ratePerMinute"] = val, delta, rate
snap["timestamp_wib"] = "2026-11-01T08:02:44+07:00"
snap["note"] = ("Snapshot 08:02 WIB run; elapsed 29.73 min since 07:33 snapshot, block 130957587 at read time. "
 "NO new main candidate. NO velocity pass (both legs rate>=1.5x AND delta>=20 required): SYMBOL 3930->3944 delta 14 rate 0.471 vs prev 0.267 (ratio 1.76x but delta <20, FAILS), 3944/10000=39.44% FAILS %; "
 "BeHand 6680->6689 delta 9 rate 0.303 vs prev 0.067 (ratio 4.52x but delta <20, FAILS); Agentlings 6853->6858 delta 5 rate 0.168 vs prev 0.467 (ratio 0.36x, FAILS); "
 "Alibaba 4891->4892 delta 1. Flat: AgentMiner 4629, AgentPad 1129, Sonic 2237, danta 2007, AgentImps 666, OTV 558. Sold out/flat at caps: UMBRA 3000, PixelVulpes 3333, Floppy 3333, Noir 3333, Brutes 5555, Fleet 1000, Hackou 92. "
 "Failed-read contracts preserved null (Lodepass, Brushborn, BANKS/Pixel Vaults, CIOW Citizens, Chocho Agent, CyberRonin, MARS PLOTS, Synth Ape Syndicate, URBANOVA); Agent Periodic Lab preserved unchanged per forget instruction.")
json.dump(snap, open(snap_path, "w"), indent=1)
print("snapshot updated")
