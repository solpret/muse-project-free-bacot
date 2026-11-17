import json
snap_path = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
snap = json.load(open(snap_path))
elapsed = 30.27  # minutes, 08:32:35 -> 09:02:51 WIB
new = {
 "AgentImps": 666, "AgentMiner": 4633, "AgentPad Pass": 1129, "Agentlings": 6872,
 "Alibaba & The 70 Thieves": 4922, "BeHand Pass": 6699, "Brutes": 5555,
 "Fleet Genesis": 1000, "Floppy Agents": 3333, "Hackou AI Pass": 92,
 "Noir Brokers": 3333, "OTV": 559, "PixelVulpes": 3333, "SYMBOL": 3950,
 "Sonic Protocol": 2237, "UMBRA Agents": 3000, "danta": 2007,
}
for name, val in new.items():
    e = snap["contracts"][name]
    prev_ts, prev_rate = e["totalSupply"], e["ratePerMinute"]
    delta = val - prev_ts if prev_ts is not None else None
    rate = round(delta / elapsed, 3) if delta is not None else None
    e["previousTotalSupply"], e["previousRatePerMinute"] = prev_ts, prev_rate
    e["totalSupply"], e["mintedInInterval"], e["ratePerMinute"] = val, delta, rate
snap["timestamp_wib"] = "2026-11-01T09:02:51+07:00"
snap["note"] = ("Snapshot 09:02 WIB run; elapsed 30.27 min since 08:32 snapshot, block 130965593 at read time. "
 "NO new main candidate. NO velocity pass on both legs this run: BeHand 6691->6699 delta 8 rate 0.264 vs prev 0.067 (ratio ~3.9x but delta<20); SYMBOL 3945->3950 delta 5 rate 0.165 vs prev 0.034 (ratio ~4.9x but delta<20, and 3950/10000=39.50% FAILS %); Agentlings 6864->6872 delta 8 rate 0.264 vs prev 0.201 (ratio ~1.31x, delta<20); Alibaba 4918->4922 delta 4 rate 0.132 vs prev 0.871 (slowing); AgentMiner 4632->4633 delta 1 rate 0.033 vs prev 0.101; OTV 559 flat, 559/1500=37.27% FAILS %. "
 "Flat: AgentPad 1129, Sonic 2237, danta 2007, AgentImps 666. Sold out/flat at caps: UMBRA 3000, PixelVulpes 3333, Floppy 3333, Noir 3333, Brutes 5555, Fleet 1000, Hackou 92. "
 "Failed-read contracts preserved null (Lodepass, Brushborn, BANKS/Pixel Vaults, CIOW Citizens, Chocho Agent, CyberRonin, MARS PLOTS, Synth Ape Syndicate, URBANOVA); Agent Periodic Lab preserved unchanged per forget instruction.")
json.dump(snap, open(snap_path, "w"), indent=1)
print("snapshot updated")
