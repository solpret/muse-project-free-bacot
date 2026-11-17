#!/usr/bin/env python3
import json
from datetime import datetime, timezone, timedelta
SNAP = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
READ = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-01-1231-read.json"
snap = json.load(open(SNAP))
read = json.load(open(READ))["results"]
prev_ts = datetime.fromisoformat(snap["timestamp_wib"])
new_ts = datetime(2026, 11, 1, 12, 32, 26, tzinfo=timezone(timedelta(hours=7)))
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
snap["note"] = ("Snapshot 12:32 WIB run; elapsed 30.65 min since 12:01 snapshot, block 0x7cecd61 at read time. "
 "NO new main candidate. NO velocity pass on both legs (requires >=1.5x prev rate AND >=20 minted): "
 "Agentlings 6929->6943 delta 14 rate 0.457 vs prev 0.239 (ratio 1.91x but delta<20; % UNVERIFIED, known >24h); "
 "BeHand 6750->6755 delta 5 rate 0.163 vs prev 0.068 (ratio 2.40x but delta<20; % UNVERIFIED, X/age UNVERIFIED); "
 "Alibaba 4950->4952 delta 2 rate 0.065 vs prev 0.034 (ratio 1.92x but delta<20; cap UNVERIFIED, known >24h); "
 "AgentMiner 4648->4650 delta 2 rate 0.065 vs prev 0.137 (slowing; 4650/9999=46.50% passes % alone, 24h+ age exclusion stands); "
 "SYMBOL 3981->3984 delta 3 rate 0.098 vs prev 0.205 (slowing; 3984/10000=39.84% FAILS %). "
 "OTV 559 flat 37.27% FAILS %. Flat: AgentPad 1129, Sonic 2237, danta 2007, AgentImps 666. "
 "Sold out/flat at caps: UMBRA 3000, PixelVulpes 3333, Floppy 3333, Noir 3333, Brutes 5555, Fleet 1000, Hackou 92. "
 "Failed-read contracts preserved (totalSupply view reverts, consistent with missing/different supply view): BANKS/Pixel Vaults, Brushborn, CIOW Citizens, Chocho Agent, CyberRonin, Lodepass, MARS PLOTS, Synth Ape Syndicate, URBANOVA. Agent Periodic Lab preserved unchanged per forget instruction. "
 "No new discovery this run: sweep resurfaced only already-known/excluded material (BLOB Miner exclusion list, Ptah known, Substack 22-project list, Boltbook receipts for known projects; Night Shift / SYNTH//CORE mentioned only with truncated addresses, not added); no new project with full contract address, official site, project-stated X account, and verifiable launch within 24h.")
json.dump(snap, open(SNAP, "w"), indent=1)
print("snapshot written", snap["timestamp_wib"])
