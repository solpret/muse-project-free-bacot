#!/usr/bin/env python3
import json
from datetime import datetime, timezone, timedelta
SNAP = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
READ = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-01-1631-read.json"
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
 "Snapshot run; elapsed %.2f min since 16:02 snapshot, block %s at read time. "
 "NO new main candidate. Velocity pass on both legs ONLY for Agentlings (requires >=1.5x prev rate AND >=20 minted): "
 "Agentlings 7062->7105 delta 43, rate vs prev 0.367 (ratio ~3.9x, velocity PASSES) but NOT a candidate: cap UNVERIFIED so >=45 pct cannot be verified, X discussion UNVERIFIED, and age FAILS the 24-hour rule (live since 27 Oct, evidence stands, no new mint phase verified). "
 "All other movers FAIL velocity: BeHand 6862->6870 delta 8, rate vs prev 0.267 (ratio 1.00x); AgentMiner 4680->4681 delta 1 (4681/9999=46.81 pct passes pct alone, 24h+ age exclusion stands); Alibaba 4991->4995 delta 4, rate vs prev 0.067 (ratio ~2x but delta <20); SYMBOL 4019->4025 delta 6, rate vs prev 0.167 (4025/10000=40.25 pct FAILS 45 pct); Hackou 92->93 delta 1. "
 "OTV 559 flat 37.27 pct FAILS 45 pct. Flat: AgentPad 1129, Sonic 2237, danta 2007, AgentImps 666. "
 "Sold out/flat at caps: UMBRA 3000, PixelVulpes 3333, Floppy 3333, Noir 3333, Brutes 5555, Fleet 1000. "
 "Failed-read contracts preserved (no fresh reading, not a pass): Lodepass, MARS PLOTS, Synth Ape Syndicate, URBANOVA, BANKS/Pixel Vaults, Brushborn, CIOW Citizens, Chocho Agent, CyberRonin (totalSupply reverts code 3); Agent Periodic Lab preserved unchanged per forget instruction (this run also HTTP 403 on its read). "
 "No new discovery this run: sweep resurfaced only already-known/excluded material (22-project Substack list Oct-27 items, BLOB Miner excluded, Ptah known, AgentRob on Robinhood Chain - out of BSC-only scope, JAGENT paid token, Typefully 2026-11-01 general guide, BSC AI Platform AGENT ID Odaily 2026-10-30 - launched >24h ago, no contract address/official site/X verified in sweep, not added); no new BSC project with full contract address, official site, project-stated X account, and verifiable launch within 24h."
 % (elapsed, json.load(open(READ))['block'])
)
json.dump(snap, open(SNAP, "w"), indent=1)
print("snapshot written", snap["timestamp_wib"])
