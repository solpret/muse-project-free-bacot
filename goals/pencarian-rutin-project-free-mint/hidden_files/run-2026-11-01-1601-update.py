#!/usr/bin/env python3
import json
from datetime import datetime, timezone, timedelta
SNAP = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
READ = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-01-1601-read.json"
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
snap["note"] = (
 "Snapshot run; elapsed %.2f min since 15:32 snapshot, block %s at read time. "
 "NO new main candidate. NO velocity pass on both legs this run (requires >=1.5x prev rate AND >=20 minted): "
 "BeHand 6854->6862 delta 8, rate vs prev 0.567 (velocity FAILS on both legs); "
 "Agentlings 7051->7062 delta 11, rate vs prev 0.333 (velocity FAILS); "
 "AgentMiner 4677->4680 delta 3 (velocity FAILS on >=20 leg despite ratio >1.5x; 4680/9999=46.80 pct passes pct alone, 24h+ age exclusion stands); "
 "Alibaba 4989->4991 delta 2 (velocity FAILS; cap UNVERIFIED, known >24h); "
 "SYMBOL 4014->4019 delta 5 (velocity FAILS; 4019/10000=40.19 pct FAILS 45 pct). "
 "OTV 559 flat 37.27 pct FAILS 45 pct. Flat: AgentPad 1129, Sonic 2237, danta 2007, AgentImps 666. "
 "Sold out/flat at caps: UMBRA 3000, PixelVulpes 3333, Floppy 3333, Noir 3333, Brutes 5555, Fleet 1000, Hackou 92. "
 "Failed-read contracts preserved (no fresh reading, not a pass): Lodepass, MARS PLOTS, Synth Ape Syndicate, URBANOVA (totalSupply reverts code 3), BANKS/Pixel Vaults, Brushborn, CIOW Citizens, Chocho Agent, CyberRonin (dataseed errors this run). Agent Periodic Lab preserved unchanged per forget instruction. "
 "Prior velocity passers NOT promoted again: Agentlings cap/X UNVERIFIED and age FAILS 24h rule (live since 27 Oct, evidence stands); BeHand cap/X/age UNVERIFIED plus prior site mismatch stands, no free tradable quota verified. "
 "No new discovery this run: sweep resurfaced only already-known/excluded material (22-project Substack list Oct-27 items, BLOB Miner excluded, Ptah known, general Agentic Wallet guides incl. Typefully 2026-11-01, AgentRob on Robinhood Chain token - out of BSC-only scope, JAGENT paid token, mint.day on Base - out of BSC-only scope, CyberRonin already on watchlist as failed-read); no new BSC project with full contract address, official site, project-stated X account, and verifiable launch within 24h."
 % (elapsed, json.load(open(READ))['block'])
)
json.dump(snap, open(SNAP, "w"), indent=1)
print("snapshot written", snap["timestamp_wib"])
