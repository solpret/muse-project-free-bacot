import json
snap_path = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
snap = json.load(open(snap_path))
elapsed = 29.85  # minutes, 08:02:44 -> 08:32:35 WIB
new = {
 "AgentImps": 666, "AgentMiner": 4632, "AgentPad Pass": 1129, "Agentlings": 6864,
 "Alibaba & The 70 Thieves": 4918, "BeHand Pass": 6691, "Brutes": 5555,
 "Fleet Genesis": 1000, "Floppy Agents": 3333, "Hackou AI Pass": 92,
 "Noir Brokers": 3333, "OTV": 559, "PixelVulpes": 3333, "SYMBOL": 3945,
 "Sonic Protocol": 2237, "UMBRA Agents": 3000, "danta": 2007,
}
for name, val in new.items():
    e = snap["contracts"][name]
    prev_ts, prev_rate = e["totalSupply"], e["ratePerMinute"]
    delta = val - prev_ts if prev_ts is not None else None
    rate = round(delta / elapsed, 3) if delta is not None else None
    e["previousTotalSupply"], e["previousRatePerMinute"] = prev_ts, prev_rate
    e["totalSupply"], e["mintedInInterval"], e["ratePerMinute"] = val, delta, rate
snap["timestamp_wib"] = "2026-11-01T08:32:35+07:00"
snap["note"] = ("Snapshot 08:32 WIB run; elapsed 29.85 min since 08:02 snapshot, block 130961569 at read time. "
 "NO new main candidate. ONE velocity pass on both legs: Alibaba 4892->4918 delta 26 rate 0.871 vs prev 0.034 (ratio ~25.6x, delta>=20) — but NOT promoted: cap UNVERIFIED (so % unverified), no project-stated X account found in deep dive (address search + name search returned only unrelated Alibaba Group material), known since 28 Oct (>24h). "
 "Others fail velocity: AgentMiner 4629->4632 delta 3 rate 0.101 vs prev 0.0 (delta<20); Agentlings 6858->6864 delta 6 rate 0.201 vs prev 0.168 (1.20x, delta<20); BeHand 6689->6691 delta 2; SYMBOL 3944->3945 delta 1, 3945/10000=39.45% FAILS %; OTV 558->559 delta 1, 559/1500=37.27% FAILS %. "
 "Flat: AgentPad 1129, Sonic 2237, danta 2007, AgentImps 666. Sold out/flat at caps: UMBRA 3000, PixelVulpes 3333, Floppy 3333, Noir 3333, Brutes 5555, Fleet 1000, Hackou 92. "
 "Failed-read contracts preserved null (Lodepass, Brushborn, BANKS/Pixel Vaults, CIOW Citizens, Chocho Agent, CyberRonin, MARS PLOTS, Synth Ape Syndicate, URBANOVA); Agent Periodic Lab preserved unchanged per forget instruction.")
json.dump(snap, open(snap_path, "w"), indent=1)
print("snapshot updated")
