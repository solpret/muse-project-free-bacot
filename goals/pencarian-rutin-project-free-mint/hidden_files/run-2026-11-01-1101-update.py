#!/usr/bin/env python3
"""Update snapshot for 2026-11-01 11:01 run from main + retry reads. Failed reads preserve old values; Agent Periodic Lab preserved unchanged per forget instruction."""
import json
from datetime import datetime, timezone, timedelta
SNAP = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
MAIN = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-01-1101-read.json"
RETRY = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-01-1101-retry.json"
snap = json.load(open(SNAP))
main = json.load(open(MAIN))["results"]
retry = json.load(open(RETRY))
prev_ts = datetime.fromisoformat(snap["timestamp_wib"])
new_ts = datetime(2026, 11, 1, 11, 5, 6, tzinfo=timezone(timedelta(hours=7)))
elapsed = (new_ts - prev_ts).total_seconds() / 60.0
print(f"elapsed {elapsed:.2f} min")
merged = {}
for name, r in main.items():
    merged[name] = r.get("totalSupply")
for name, r in retry.items():
    if r.get("totalSupply") is not None:
        merged[name] = r["totalSupply"]
for name, c in snap["contracts"].items():
    if name == "Agent Periodic Lab":
        continue
    new = merged.get(name)
    old = c.get("totalSupply")
    if new is None:
        # Preserve old reading; do not fabricate a rate. Keep previous fields as-is.
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
snap["note"] = ("Snapshot 11:05 WIB run; elapsed 32.37 min since 10:32 snapshot, block 0x7ce9f8f at read time. "
 "NO new main candidate. NO velocity pass on both legs (velocity requires >=1.5x prev rate AND >=20 minted): "
 "BeHand 6732->6739 delta 7 rate 0.216 vs prev 0.140 (ratio 1.54x but delta<20); AgentMiner 4638->4642 delta 4 rate 0.124 vs prev 0.035 (delta<20; 4642/9999=46.42% passes % alone, 24h+ age exclusion stands); "
 "Agentlings 6898->6904 delta 6 rate 0.185 vs prev 0.175 (ratio 1.06x, delta<20); SYMBOL 3966->3970 delta 4 rate 0.124 vs prev 0.035 (delta<20; 3970/10000=39.70% FAILS %); "
 "Alibaba 4937->4938 delta 1 rate 0.031 vs prev 0.175 (slowing); OTV 559 flat 37.27% FAILS %. Flat: AgentPad 1129, Sonic 2237, danta 2007, AgentImps 666. "
 "Sold out/flat at caps: UMBRA 3000, PixelVulpes 3333, Floppy 3333, Noir 3333, Brutes 5555, Fleet 1000, Hackou 92. "
 "Failed-read contracts preserved (totalSupply view fails, consistent with missing/different supply view, not a fresh reading): BANKS/Pixel Vaults, Brushborn, CIOW Citizens, Chocho Agent, CyberRonin, Lodepass, MARS PLOTS, Synth Ape Syndicate, URBANOVA. Agent Periodic Lab preserved unchanged per forget instruction. "
 "Note: first read attempt used the full 11-endpoint race and stalled on an external-share approval card for onfinality in this detached run; the completed reads used Binance dataseeds only, plus direct sequential retries for failed contracts.")
json.dump(snap, open(SNAP, "w"), indent=1)
print("snapshot written", snap["timestamp_wib"])
