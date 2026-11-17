#!/usr/bin/env python3
import json
snap_path = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
snap = json.load(open(snap_path))
new = {
 "AgentImps": 666, "AgentMiner": 4612, "AgentPad Pass": 1129, "Agentlings": 6808,
 "Alibaba & The 70 Thieves": 4877, "BeHand Pass": 6660, "Brutes": 5555,
 "Fleet Genesis": 1000, "Floppy Agents": 3333, "Hackou AI Pass": 92,
 "Noir Brokers": 3333, "OTV": 557, "PixelVulpes": 3333, "SYMBOL": 3907,
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
snap["timestamp_wib"] = "2026-11-01T03:32:00+07:00"
snap["note"] = ("Snapshot 03:32 WIB run; elapsed 30 min since 03:02 snapshot, block 130921544 at read time. "
 "NO new main candidate. ONE velocity pass alone: Agentlings 6781->6808 delta 27 rate 0.9 vs prev 0.033 (ratio ~27x, delta>=20) "
 "BUT minted % UNVERIFIED (no stated cap found; this run's web search for cap returned only an unrelated Mind Network contract), "
 "no project-stated X account verified, and known since 28 Oct (>24h) so age FAILS for a main candidate. Watchlist only. "
 "AgentMiner 4610->4612 delta 2 rate 0.067 vs prev 0.0 (delta<20, velocity FAILS), 4612/9999=46.13% passes % alone but age-excluded stands. "
 "BeHand 6658->6660 delta 2 rate 0.067 vs prev 0.233 (ratio 0.29x, FAILS); Alibaba 4876->4877 delta 1 rate 0.033 vs prev 0.1 (FAILS); "
 "SYMBOL 3906->3907 delta 1 rate 0.033 vs prev 0.1 (FAILS), 3907/10000=39.07% FAILS >=45%. "
 "Flat: AgentPad 1129, OTV 557/1500=37.1% FAILS %, Sonic 2237, danta 2007, AgentImps 666. "
 "Sold out/flat at caps: UMBRA 3000, PixelVulpes 3333, Floppy 3333, Noir 3333, Brutes 5555, Fleet 1000, Hackou 92. "
 "Failed-read contracts preserved null (Lodepass, Brushborn, BANKS/Pixel Vaults, CIOW Citizens, Chocho Agent, CyberRonin, MARS PLOTS, Synth Ape Syndicate, URBANOVA); "
 "Agent Periodic Lab preserved unchanged per forget instruction.")
json.dump(snap, open(snap_path, "w"), indent=1)
print("snapshot updated")
