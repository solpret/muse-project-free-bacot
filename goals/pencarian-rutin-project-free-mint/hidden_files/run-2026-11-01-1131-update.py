#!/usr/bin/env python3
"""Update snapshot for 2026-11-01 11:31 run. Failed reads preserve old values; Agent Periodic Lab preserved unchanged per forget instruction."""
import json
from datetime import datetime, timezone, timedelta
SNAP = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
READ = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-01-1131-read.json"
snap = json.load(open(SNAP))
read = json.load(open(READ))["results"]
prev_ts = datetime.fromisoformat(snap["timestamp_wib"])
new_ts = datetime(2026, 11, 1, 11, 32, 32, tzinfo=timezone(timedelta(hours=7)))
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
snap["note"] = ("Snapshot 11:32 WIB run; elapsed 27.43 min since 11:05 snapshot, block 0x7ceae58 at read time. "
 "NO new main candidate. NO velocity pass on both legs (requires >=1.5x prev rate AND >=20 minted): "
 "Agentlings 6904->6922 delta 18 rate 0.656 vs prev 0.185 (ratio 3.54x but delta<20, closest this run); "
 "Alibaba 4938->4949 delta 11 rate 0.401 vs prev 0.031 (ratio high but delta<20); "
 "BeHand 6739->6748 delta 9 rate 0.328 vs prev 0.216 (ratio 1.52x but delta<20); "
 "AgentMiner 4642->4644 delta 2 rate 0.073 vs prev 0.124 (slowing; 4644/9999=46.44% passes % alone, 24h+ age exclusion stands); "
 "SYMBOL 3970->3975 delta 5 rate 0.182 vs prev 0.124 (ratio 1.47x, delta<20; 3975/10000=39.75% FAILS %); "
 "OTV 559 flat 37.27% FAILS %. Flat: AgentPad 1129, Sonic 2237, danta 2007, AgentImps 666. "
 "Sold out/flat at caps: UMBRA 3000, PixelVulpes 3333, Floppy 3333, Noir 3333, Brutes 5555, Fleet 1000, Hackou 92. "
 "Failed-read contracts preserved (totalSupply view reverts, consistent with missing/different supply view): BANKS/Pixel Vaults, Brushborn, CIOW Citizens, Chocho Agent, CyberRonin, Lodepass, MARS PLOTS, Synth Ape Syndicate, URBANOVA. Agent Periodic Lab preserved unchanged per forget instruction. "
 "New discovery Coracle Agents (https://coracle-agents.pages.dev/, 10,000 cap, first 2 free, .ai-gated) NOT added to snapshot: contract address absent from crawled page text and no project-stated X link found in page text or targeted search; roadmap Mint stage reads 'Soon' and mint counters blank, so treated as upcoming/unverified, not launched, not a candidate.")
json.dump(snap, open(SNAP, "w"), indent=1)
print("snapshot written", snap["timestamp_wib"])
