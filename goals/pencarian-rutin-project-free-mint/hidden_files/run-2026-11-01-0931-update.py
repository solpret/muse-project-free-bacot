import json
snap_path = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
snap = json.load(open(snap_path))
elapsed = 29.88  # minutes, 09:02:51 -> 09:32:44 WIB
new = {
 "AgentImps": 666, "AgentMiner": 4637, "AgentPad Pass": 1129, "Agentlings": 6884,
 "Alibaba & The 70 Thieves": 4923, "BeHand Pass": 6702, "Brutes": 5555,
 "Fleet Genesis": 1000, "Floppy Agents": 3333, "Hackou AI Pass": 92,
 "Noir Brokers": 3333, "OTV": 559, "PixelVulpes": 3333, "SYMBOL": 3963,
 "Sonic Protocol": 2237, "UMBRA Agents": 3000, "danta": 2007,
}
for name, val in new.items():
    e = snap["contracts"][name]
    prev_ts, prev_rate = e["totalSupply"], e["ratePerMinute"]
    delta = val - prev_ts if prev_ts is not None else None
    rate = round(delta / elapsed, 3) if delta is not None else None
    e["previousTotalSupply"], e["previousRatePerMinute"] = prev_ts, prev_rate
    e["totalSupply"], e["mintedInInterval"], e["ratePerMinute"] = val, delta, rate
snap["timestamp_wib"] = "2026-11-01T09:32:44+07:00"
snap["note"] = ("Snapshot 09:32 WIB run; elapsed 29.88 min since 09:02 snapshot, block 130969586 at read time. "
 "NO new main candidate. NO velocity pass on both legs this run (velocity requires current rate >= 1.5x previous rate AND >= 20 tokens minted in the interval; max delta this run was 13): Agentlings 6872->6884 delta 12 rate 0.402 vs prev 0.264 (ratio ~1.52x BUT delta<20); SYMBOL 3950->3963 delta 13 rate 0.435 vs prev 0.165 (ratio ~2.64x BUT delta<20, and 3963/10000=39.63% FAILS %); AgentMiner 4633->4637 delta 4 rate 0.134 vs prev 0.033 (ratio ~4.06x BUT delta<20; 4637/9999=46.37% passes % alone, 24h+ age exclusion stands); BeHand 6699->6702 delta 3 rate 0.100 vs prev 0.264 (slowing); Alibaba 4922->4923 delta 1 rate 0.033 vs prev 0.132 (slowing); OTV 559 flat, 559/1500=37.27% FAILS %. "
 "Flat: AgentPad 1129, Sonic 2237, danta 2007, AgentImps 666. Sold out/flat at caps: UMBRA 3000, PixelVulpes 3333, Floppy 3333, Noir 3333, Brutes 5555, Fleet 1000, Hackou 92. "
 "Failed-read contracts preserved null (Lodepass, Brushborn, BANKS/Pixel Vaults, CIOW Citizens, Chocho Agent, CyberRonin, MARS PLOTS, Synth Ape Syndicate, URBANOVA); Agent Periodic Lab preserved unchanged per forget instruction.")
json.dump(snap, open(snap_path, "w"), indent=1)
print("snapshot updated")
