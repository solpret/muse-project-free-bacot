#!/usr/bin/env python3
"""Update snapshot for 2026-11-01 12:01 run. Failed reads preserve old values; Agent Periodic Lab preserved unchanged per forget instruction."""
import json
from datetime import datetime, timezone, timedelta
SNAP = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
READ = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-01-1201-read.json"
snap = json.load(open(SNAP))
read = json.load(open(READ))["results"]
prev_ts = datetime.fromisoformat(snap["timestamp_wib"])
new_ts = datetime(2026, 11, 1, 12, 1, 47, tzinfo=timezone(timedelta(hours=7)))
elapsed = (new_ts - prev_ts).total_seconds() / 60.0
print(f"elapsed {elapsed:.2f} min, block {json.load(open(READ))['block']}")
for name, c in snap["contracts"].items():
    if name == "Agent Periodic Lab":
        continue
    new = read[name].get("totalSupply")
    old = c.get("totalSupply")
    if new is None:
        continue
    delta = new - old if old is not None else None
    rate = round(delta / elapsed, 3) if delta is not None else None
    c["previousTotalSupply"] = old
    c["totalSupply"] = new
    c["mintedInInterval"] = delta
    c["previousRatePerMinute"] = c.get("ratePerMinute")
    c["ratePerMinute"] = rate
    print(name, old, "->", new, "delta", delta, "rate", rate, "prevRate", c["previousRatePerMinute"])
snap["timestamp_wib"] = new_ts.isoformat()
snap["note"] = ("Snapshot 12:01 WIB run; elapsed 29.25 min since 11:32 snapshot, block 0x7cebda1 at read time. "
 "NO new main candidate. NO velocity pass on both legs (requires >=1.5x prev rate AND >=20 minted): "
 "AgentMiner 4644->4648 delta 4 rate 0.137 vs prev 0.073 (ratio 1.87x but delta<20; 4648/9999=46.48% passes % alone, 24h+ age exclusion stands); "
 "SYMBOL 3975->3981 delta 6 rate 0.205 vs prev 0.182 (ratio 1.13x, delta<20; 3981/10000=39.81% FAILS %); "
 "Agentlings 6922->6929 delta 7 rate 0.239 vs prev 0.656 (slowing); "
 "Alibaba 4949->4950 delta 1 rate 0.034 vs prev 0.401 (slowing); "
 "BeHand 6748->6750 delta 2 rate 0.068 vs prev 0.328 (slowing). "
 "OTV 559 flat 37.27% FAILS %. Flat: AgentPad 1129, Sonic 2237, danta 2007, AgentImps 666. "
 "Sold out/flat at caps: UMBRA 3000, PixelVulpes 3333, Floppy 3333, Noir 3333, Brutes 5555, Fleet 1000, Hackou 92. "
 "Failed-read contracts preserved (totalSupply view reverts, consistent with missing/different supply view): BANKS/Pixel Vaults, Brushborn, CIOW Citizens, Chocho Agent, CyberRonin, Lodepass, MARS PLOTS, Synth Ape Syndicate, URBANOVA. Agent Periodic Lab preserved unchanged per forget instruction. "
 "No new discovery this run: sweep resurfaced only already-known/excluded material (BLOB Miner exclusion list, Ptah known, Substack 22-project list, Coracle Agents already recorded as upcoming/unverified, Boltbook receipts for known projects); no new project with full contract address, official site, project-stated X account, and verifiable launch within 24h.")
json.dump(snap, open(SNAP, "w"), indent=1)
print("snapshot written", snap["timestamp_wib"])
