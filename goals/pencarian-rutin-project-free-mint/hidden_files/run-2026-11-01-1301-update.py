#!/usr/bin/env python3
import json
from datetime import datetime, timezone, timedelta
SNAP = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
READ = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-01-1301-read.json"
snap = json.load(open(SNAP))
read = json.load(open(READ))["results"]
prev_ts = datetime.fromisoformat(snap["timestamp_wib"])
new_ts = datetime(2026, 11, 1, 13, 2, 28, tzinfo=timezone(timedelta(hours=7)))
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
snap["note"] = ("Snapshot 13:02 WIB run; elapsed 30.03 min since 12:32 snapshot, block 0x7cedcfb at read time. "
 "NO new main candidate. NO velocity pass on both legs (requires >=1.5x prev rate AND >=20 minted): "
 "Agentlings 6943->6950 delta 7 rate 0.233 vs prev 0.457 (slowing; % UNVERIFIED, known >24h); "
 "BeHand 6755->6761 delta 6 rate 0.200 vs prev 0.163 (ratio 1.23x and delta<20; % UNVERIFIED, X/age UNVERIFIED); "
 "Alibaba 4952->4957 delta 5 rate 0.166 vs prev 0.065 (ratio 2.56x but delta<20; cap UNVERIFIED, known >24h); "
 "AgentMiner 4650->4652 delta 2 rate 0.067 vs prev 0.065 (ratio ~1.03x and delta<20; 4652/9999=46.53% passes % alone, 24h+ age exclusion stands); "
 "SYMBOL 3984->3986 delta 2 rate 0.067 vs prev 0.098 (slowing; 3986/10000=39.86% FAILS %). "
 "OTV 559 flat 37.27% FAILS %. Flat: AgentPad 1129, Sonic 2237, danta 2007, AgentImps 666. "
 "Sold out/flat at caps: UMBRA 3000, PixelVulpes 3333, Floppy 3333, Noir 3333, Brutes 5555, Fleet 1000, Hackou 92. "
 "Failed-read contracts preserved (totalSupply view reverts, consistent with missing/different supply view): BANKS/Pixel Vaults, Brushborn, CIOW Citizens, Chocho Agent, CyberRonin, Lodepass, MARS PLOTS, Synth Ape Syndicate, URBANOVA. Agent Periodic Lab preserved unchanged per forget instruction. "
 "No new discovery this run: sweep resurfaced only already-known/excluded material (BLOB Miner exclusion list, Ptah known, Substack 22-project list, Coracle Agents already owned #897/#898 and recorded as upcoming/unverified, Boltbook receipts for known projects, AIMONSTERS Genesis Egg with no full contract address in snippet, mint.day Base chain out of scope); no new project with full contract address, official site, project-stated X account, and verifiable launch within 24h.")
json.dump(snap, open(SNAP, "w"), indent=1)
print("snapshot written", snap["timestamp_wib"])
