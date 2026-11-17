#!/usr/bin/env python3
import json
from datetime import datetime, timezone, timedelta
SNAP = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
READ = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-01-1431-read.json"
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
 "Snapshot run; elapsed " + ("%.2f" % elapsed) + " min since 14:02 snapshot, block 0x7cf0be2 at read time. "
 "NO new main candidate. TWO velocity passes on both legs (requires >=1.5x prev rate AND >=20 minted), NEITHER promoted: "
 "Agentlings 6976->7027 delta 51 (velocity PASSES; cap UNVERIFIED, X discussion UNVERIFIED, age FAILS 24h rule: live since 27 Oct per Boltbook bigwealth post, evidence stands, no new evidence overturns it); "
 "BeHand 6787->6817 delta 30 (velocity PASSES; cap/X/age UNVERIFIED, plus fresh site read behandbots.surge.sh states 3,000 Bots PAID 0.0005 BNB rising per 500 and a free soulbound Pass 1/wallet - the free element is non-transferable, the Bots mint is paid, and the site cap 3,000 contradicts on-chain totalSupply 6817, so contract-match/pct remain UNVERIFIED and no free tradable quota is verified). "
 "AgentMiner 4661->4665 delta 4 (velocity FAILS delta<20; 4665/9999=46.65 pct passes pct alone, 24h+ age exclusion stands); "
 "Alibaba 4973->4977 delta 4 (velocity FAILS; cap UNVERIFIED, known >24h); "
 "SYMBOL 3996->4005 delta 9 (velocity FAILS delta<20; 4005/10000=40.05 pct FAILS 45 pct). "
 "OTV 559 flat 37.27 pct FAILS 45 pct. Flat: AgentPad 1129, Sonic 2237, danta 2007, AgentImps 666. "
 "Sold out/flat at caps: UMBRA 3000, PixelVulpes 3333, Floppy 3333, Noir 3333, Brutes 5555, Fleet 1000, Hackou 92. "
 "Failed-read contracts preserved (totalSupply view reverts code 3 on dataseeds this run, incl. previously 403-failed BANKS/Pixel Vaults, Brushborn, CIOW Citizens, Chocho Agent, CyberRonin - a revert, not a fresh reading, not a pass): Lodepass, MARS PLOTS, Synth Ape Syndicate, URBANOVA, BANKS/Pixel Vaults, Brushborn, CIOW Citizens, Chocho Agent, CyberRonin. Agent Periodic Lab preserved unchanged per forget instruction. "
 "Cap-view attempt for velocity passers (maxSupply, MAX_SUPPLY, collectionSize, supply, cap selectors) reverted on both BeHand and Agentlings contracts - cap stays UNVERIFIED. "
 "No new discovery this run: sweep resurfaced only already-known/excluded material (22-project Substack list Oct-27 items, general Agentic Wallet guides incl. Typefully 2026-11-01, Ptah known, OneMint/AgentBNB unrelated, contract-address search returned no project pages); no new project with full contract address, official site, project-stated X account, and verifiable launch within 24h."
)
json.dump(snap, open(SNAP, "w"), indent=1)
print("snapshot written", snap["timestamp_wib"])
