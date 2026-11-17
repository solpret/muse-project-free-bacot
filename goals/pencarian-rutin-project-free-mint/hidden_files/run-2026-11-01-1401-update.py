#!/usr/bin/env python3
import json
from datetime import datetime, timezone, timedelta
SNAP = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
READ = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-01-1401-read.json"
snap = json.load(open(SNAP))
read = json.load(open(READ))["results"]
prev_ts = datetime.fromisoformat(snap["timestamp_wib"])
new_ts = datetime.now(timezone(timedelta(hours=7))).replace(second=0, microsecond=0)
elapsed = (new_ts - prev_ts).total_seconds() / 60.0
print(f"elapsed {elapsed:.2f} min, block {json.load(open(READ))['block']}, new_ts {new_ts.isoformat()}")
for name, c in snap["contracts"].items():
    if name == "Agent Periodic Lab":
        continue
    new = read[name].get("totalSupply")
    old = c.get("totalSupply")
    if new is None:
        print(name, "READ FAILED, preserved", old)
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
snap["note"] = ("Snapshot 14:0x WIB run; elapsed %.2f min since 13:32 snapshot, block 0x7cefc2b at read time. "
 "NO new main candidate. NO velocity pass on both legs (requires >=1.5x prev rate AND >=20 minted): "
 "AgentMiner 4659->4661 delta 2 (velocity FAILS; 4661/9999=46.61%% passes %% alone, 24h+ age exclusion stands); "
 "Agentlings 6959->6976 delta 17 (delta<20, velocity FAILS; %% UNVERIFIED, known >24h); "
 "BeHand 6773->6787 delta 14 (delta<20, velocity FAILS; %% UNVERIFIED, X/age UNVERIFIED); "
 "Alibaba 4967->4973 delta 6 (velocity FAILS; cap UNVERIFIED, known >24h); "
 "SYMBOL 3994->3996 delta 2 (velocity FAILS; 3996/10000=39.96%% FAILS %%). "
 "OTV 559 flat 37.27%% FAILS %%. Flat: AgentPad 1129, Sonic 2237, danta 2007, AgentImps 666. "
 "Sold out/flat at caps: UMBRA 3000, PixelVulpes 3333, Floppy 3333, Noir 3333, Brutes 5555, Fleet 1000, Hackou 92. "
 "Failed-read contracts preserved: Lodepass, MARS PLOTS, Synth Ape Syndicate, URBANOVA (totalSupply view reverts); BANKS/Pixel Vaults, Brushborn, CIOW Citizens, Chocho Agent, CyberRonin (all 4 dataseeds failed this run, last endpoint HTTP 403 — not a fresh reading, not a pass). Agent Periodic Lab preserved unchanged per forget instruction. "
 "No new discovery this run: sweep resurfaced only already-known/excluded material (BLOB Miner exclusion list, Ptah known, Substack 22-project list incl. old Oct-27 items, Typefully guides 2026-11-01 with no new contract, Coracle Agents already owned #897/#898 and already recorded as upcoming/unverified — no contract address in page text, no project-stated X link, Mint 'Soon' — not re-promoted, Boltbook receipts for known projects incl. Synth Ape watchlist, NONCE, Niche/Worldygg excluded, partial-address mentions Night Shift/SYNTH//CORE with no full contract, mint.day Base chain out of scope); no new project with full contract address, official site, project-stated X account, and verifiable launch within 24h." % elapsed)
json.dump(snap, open(SNAP, "w"), indent=1)
print("snapshot written", snap["timestamp_wib"])
