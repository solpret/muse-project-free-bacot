#!/usr/bin/env python3
import json
from datetime import datetime, timezone, timedelta
SNAP = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
READ = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-01-1331-read.json"
snap = json.load(open(SNAP))
read = json.load(open(READ))["results"]
prev_ts = datetime.fromisoformat(snap["timestamp_wib"])
new_ts = datetime(2026, 11, 1, 13, 32, 0, tzinfo=timezone(timedelta(hours=7)))
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
snap["note"] = ("Snapshot 13:32 WIB run; elapsed 29.53 min since 13:02 snapshot, block 0x7ceec76 at read time. "
 "NO new main candidate. NO velocity pass on both legs (requires >=1.5x prev rate AND >=20 minted): "
 "AgentMiner 4652->4659 delta 7 rate 0.237 vs prev 0.067 (ratio 3.54x but delta<20; 4659/9999=46.59% passes % alone, 24h+ age exclusion stands); "
 "Agentlings 6950->6959 delta 9 rate 0.305 vs prev 0.233 (ratio 1.31x and delta<20; % UNVERIFIED, known >24h); "
 "BeHand 6761->6773 delta 12 rate 0.406 vs prev 0.200 (ratio 2.03x but delta<20; % UNVERIFIED, X/age UNVERIFIED); "
 "Alibaba 4957->4967 delta 10 rate 0.339 vs prev 0.166 (ratio 2.04x but delta<20; cap UNVERIFIED, known >24h); "
 "SYMBOL 3986->3994 delta 8 rate 0.271 vs prev 0.067 (ratio 4.04x but delta<20; 3994/10000=39.94% FAILS %). "
 "OTV 559 flat 37.27% FAILS %. Flat: AgentPad 1129, Sonic 2237, danta 2007, AgentImps 666. "
 "Sold out/flat at caps: UMBRA 3000, PixelVulpes 3333, Floppy 3333, Noir 3333, Brutes 5555, Fleet 1000, Hackou 92. "
 "Failed-read contracts preserved (totalSupply view reverts): BANKS/Pixel Vaults, Brushborn, CIOW Citizens, Chocho Agent, CyberRonin, Lodepass, MARS PLOTS, Synth Ape Syndicate, URBANOVA. Agent Periodic Lab preserved unchanged per forget instruction. "
 "No new discovery this run: sweep resurfaced only already-known/excluded material (BLOB Miner exclusion list, Ptah known, Substack 22-project list incl. old Oct-27 items, Typefully guides 2026-11-01 with no new contract, Boltbook receipts for known projects incl. Synth Ape watchlist and NONCE, partial-address mentions Night Shift/SYNTH//CORE with no full contract, mint.day Base chain out of scope); no new project with full contract address, official site, project-stated X account, and verifiable launch within 24h.")
json.dump(snap, open(SNAP, "w"), indent=1)
print("snapshot written", snap["timestamp_wib"])
