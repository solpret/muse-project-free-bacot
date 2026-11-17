#!/usr/bin/env python3
import json
from datetime import datetime, timezone, timedelta
SNAP = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
READ = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-01-1801-read.json"
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
        print(name, "READ FAILED, preserved", old, read[name].get("error"))
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
snap["note"] = (
 "Snapshot run; elapsed %.2f min since 17:03 snapshot, block %s at read time. "
 "NO new main candidate. Velocity pass on both legs ONLY for BeHand Pass (requires >=1.5x prev rate AND >=20 minted): "
 "BeHand 6882->6907 delta 25, rate vs prev 0.387 (ratio ~2.2x, velocity PASSES) BUT minted pct UNVERIFIED (no verified cap), X discussion UNVERIFIED, and known since 28 Oct (>24h) - NOT a candidate. "
 "All other movers FAIL velocity: AgentMiner 4704->4722 delta 18, rate vs prev 0.742 (ratio ~0.8x, slowing; 4722/9999=47.23 pct passes pct alone but 24h+ age exclusion stands and X UNVERIFIED); Agentlings 7119->7137 delta 18, rate vs prev 0.452 (ratio ~1.3x); Alibaba 4999->5017 delta 18, rate vs prev 0.129 (ratio ~4.7x but delta <20); SYMBOL 4035->4049 delta 14, rate vs prev 0.323 (ratio ~1.4x and delta <20; 4049/10000=40.49 pct FAILS 45 pct). "
 "OTV 559 flat 37.27 pct FAILS 45 pct. Flat: AgentPad 1129, Sonic 2237, danta 2007, Hackou 93, AgentImps 666 (read succeeded this run after prior 403). "
 "Sold out/flat at caps: UMBRA 3000, PixelVulpes 3333, Floppy 3333, Noir 3333, Brutes 5555, Fleet 1000. "
 "Failed-read contracts preserved (no fresh reading, not a pass): Lodepass, MARS PLOTS, Synth Ape Syndicate, URBANOVA, BANKS/Pixel Vaults, Brushborn, CIOW Citizens, Chocho Agent, CyberRonin (totalSupply reverts code 3); Agent Periodic Lab preserved unchanged per forget instruction (this run also reverted code 3). "
 "No new discovery this run: sweep resurfaced only already-known/excluded material (22-project Substack list Oct-27 items, BLOB Miner excluded, Ptah known, BSC AI Platform AGENT ID Odaily 2026-10-30 - launched >24h ago, no contract/official site/X verified, not added, Typefully 2026-11-01 general guides incl. Grok Bot monetization guide with no new project); no new BSC project with full contract address, official site, project-stated X account, and verifiable launch within 24h."
 % (elapsed, json.load(open(READ))['block'])
)
json.dump(snap, open(SNAP, "w"), indent=1)
print("snapshot written", snap["timestamp_wib"])
