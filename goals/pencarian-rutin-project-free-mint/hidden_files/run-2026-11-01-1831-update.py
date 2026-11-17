#!/usr/bin/env python3
import json
SNAP = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
READ = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-01-1831-read.json"
snap = json.load(open(SNAP))
read = json.load(open(READ))
# Read file stdout starts with "exit=0" line? No: read.json was redirected stdout of script only,
# but exec output interleaved; handle: load raw and find first '{'
raw = open(READ).read()
data = json.loads(raw[raw.index("{"):])
elapsed = 29.2  # 18:03 -> ~18:32 WIB
for name, r in data["results"].items():
    c = snap["contracts"][name]
    if r["totalSupply"] is None:
        continue  # preserve failed-read entry unchanged
    prev_ts = c.get("totalSupply")
    prev_rate = c.get("ratePerMinute")
    delta = r["totalSupply"] - prev_ts if prev_ts is not None else None
    rate = round(delta / elapsed, 3) if delta is not None else None
    c["previousTotalSupply"] = prev_ts
    c["totalSupply"] = r["totalSupply"]
    c["mintedInInterval"] = delta
    c["previousRatePerMinute"] = prev_rate
    c["ratePerMinute"] = rate
snap["timestamp_wib"] = "2026-11-01T18:32:00+07:00"
snap["note"] = ("Snapshot run 2026-11-01 ~18:32 WIB; elapsed 29.2 min since 18:03 snapshot, block 0x7cf88c4 at read time. "
 "NO new main candidate. NO velocity pass this run: BeHand 6927->6950 delta 23 rate 0.788 vs prev 0.667 ratio ~1.18x FAIL; "
 "Alibaba 5044->5063 delta 19 rate 0.651 vs prev 0.900 ratio ~0.72x and delta <20 FAIL (slowing after last run's pass); "
 "Agentlings 7160->7177 delta 17 rate 0.582 vs prev 0.767 ratio ~0.76x FAIL; AgentMiner 4743->4746 delta 3 rate 0.103 vs prev 0.700 FAIL "
 "(4746/9999=47.47 pct passes pct alone but 24h+ age exclusion stands and X UNVERIFIED); SYMBOL 4067->4078 delta 11 rate 0.377 vs prev 0.600 FAIL, "
 "4078/10000=40.78 pct FAILS 45 pct; OTV 559 flat 37.27 pct FAILS 45 pct. Flat: AgentPad 1129, Sonic 2237, danta 2007, Hackou 93, AgentImps 666. "
 "Sold out/flat at caps: UMBRA 3000, PixelVulpes 3333, Floppy 3333, Noir 3333, Brutes 5555, Fleet 1000. Failed-read contracts preserved: "
 "Lodepass, MARS PLOTS, Synth Ape Syndicate, URBANOVA, BANKS/Pixel Vaults, Brushborn, CIOW Citizens, Chocho Agent, CyberRonin, Agent Periodic Lab "
 "(totalSupply reverts code 3). No new discovery this run: sweep resurfaced only already-known/excluded material (22-project Substack list Oct-27 items, "
 "BLOB Miner excluded, Ptah known, BSC AI Platform AGENT ID Odaily 2026-10-30 - launched >24h ago, no contract/official site/X verified, not added, "
 "Typefully 2026-11-01 general guides, AgentRob Medium 2026-11-01 - Robinhood Chain/ETH-settled, NOT BSC scope, excluded, Boltbook AlienID sold out "
 "7000/7000, Oathbots sold out, Night Shift truncated address 0x427a...cf14 only - full contract unverifiable, comments ~3d old, not added, "
 "SYNTH//CORE 890/7777=11.4 pct FAILS 45 pct, SEVY/HashOre/Gremlins/Lingji/LMWR Boltbook mentions are sold-out/free-tier-done or >24h old, no new contract); "
 "NOTHUMANAI (user-named, mint opens 19:00 WIB) and Agent Harvest phase watch / Hive launch watch are handled by their own dedicated tasks, not reported "
 "as routine candidates here; no new BSC project with full contract address, official site, project-stated X account, and verifiable launch within 24h.")
json.dump(snap, open(SNAP, "w"), indent=1)
print("updated", snap["timestamp_wib"])
