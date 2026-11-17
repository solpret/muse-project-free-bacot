#!/usr/bin/env python3
"""Snapshot/seen/state update for free-mint-search run 2026-11-01 22:01 WIB.
Reads: run-2026-11-01-2201-read.json (block 131070799, ~22:12:05 WIB),
scan onchain-scan-2026-11-01-2201.json (window 131068887-131070886).
No previews/mints/signing. Watermark advances ONLY because the scan succeeded."""
import json
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
read = json.load(open(BASE + "run-2026-11-01-2201-read.json"))
scan = json.load(open(BASE + "onchain-scan-2026-11-01-2201.json"))
seen = json.load(open(BASE + "onchain-scan-seen.json"))
state = json.load(open(BASE + "onchain-scan-state.json"))
READ_WIB = "2026-11-01T22:12:05+07:00"
READ_BLOCK = read["block"]
# HIVE: 640 -> 663, interval 21:38:41 -> 22:12:05 = 33.40 min, +23 = 0.689/min, ratio vs 0.331 = 2.08x, >=20 => velocity PASSES again (was FAILING at 21:31)
hive = snap["contracts"]["HIVE Agents"]
hive["previousTotalSupply"] = 640
hive["totalSupply"] = 663
hive["mintedInInterval"] = 23
hive["intervalMinutes"] = 33.40
hive["currentRatePerMin"] = 0.689
hive["previousRatePerMin"] = 0.331
hive["velocityVerified"] = True
hive["velocityNote"] = ("Run 22:01 WIB: +23 tokens in ~33.40 min (21:38:41->22:12:05) = 0.689/min; "
    "ratio vs prior 0.331/min = 2.08x AND 23 >= 20 tokens, so the velocity leg now PASSES again "
    "(it FAILED at 21:31 WIB). Stored as new baseline. HIVE remains a strong lead, still NOT a candidate: X still unverified.")
hive["freePctInference"] = 66.3
hive["freePctNote"] = "Inference only: totalSupply 663 + totalPaid 0 -> 663/1000 FREE_SUPPLY = 66.3%; no freeClaimed view on contract."
hive["lastReadBlock"] = READ_BLOCK
hive["lastReadWib"] = READ_WIB
hive["baselineNote"] = ("Deep-sweep lead; % is inference from totalSupply + totalPaid=0, not a freeClaimed view; "
    "START_TIME 2026-11-01 16:00 WIB; free slot open for user wallet; X unverified; "
    "velocity PASSES again at 22:01 WIB run (23 tokens, 2.08x) after failing at 21:31 WIB; "
    "still NOT a candidate (X unverified); already reported to main chat as watchlist lead 2026-11-01 ~19:36 WIB, "
    "velocity-pass reported once at 21:01 WIB, velocity-fail reported once at 21:31 WIB.")
# Bubblebruin: 618 -> 682, +64 = 1.916/min, ratio vs 7.82 = 0.25x => velocity FAILS still; freeClaimed 681/7777 = 8.8%
bub = snap["contracts"]["Bubblebruin"]
bub["previousTotalSupply"] = 618
bub["totalSupply"] = 682
bub["freeClaimed"] = 681
bub["freePctVerified"] = 8.8
bub["mintedInInterval"] = 64
bub["intervalMinutes"] = 33.40
bub["currentRatePerMin"] = 1.916
bub["previousRatePerMin"] = 7.82
bub["velocityNote"] = ("Run 22:01 WIB: +64 tokens in ~33.40 min (21:38:41->22:12:05) = 1.916/min, ratio vs prior "
    "7.82/min = 0.25x (< 1.5x), so the velocity leg still FAILS. Stored as new baseline. "
    "Scan window of this run: 24 mints / 24 minters for Bubblebruin. "
    "Note: freeClaimed 681 vs totalSupply 682 (1 token difference, unexplained by the views read).")
bub["lastReadBlock"] = READ_BLOCK
bub["lastReadWib"] = READ_WIB
bub["baselineNote"] = ("EARLY lead reported once 2026-11-01 run 20:31 WIB. Never auto-minted/previewed. "
    "Promotes to strong lead only on all 3 strong-lead legs; to candidate only on ALL criteria + safety. "
    "At 22:01 WIB: 681/7777 = 8.8% verified free (far below 50% strong leg), age still UNVERIFIED, "
    "X still UNVERIFIED, slot open by read, velocity still fails (0.25x).")
# Track B: binanceai.fun still pending
tb = snap["pending_claims"]["binanceai.fun"]
tb["totalShares_last"] = 3080
tb["lastCheckBlock"] = READ_BLOCK
tb["lastCheckWib"] = READ_WIB
tb["note"] = ("Seeded per user auto-claim approval 2026-11-01 ~20:27 WIB; dedicated 1h binanceai-claim-watch disabled as subsumed by routine track-B tracking. "
    "Already known to user (mint + blocked claim reported); do NOT re-report as a new pending claim — report only on open/claim/block/refund changes. "
    "Re-checked 22:01 run: launched still false, isRefundPhase false, failed false, totalShares 3080 (was 3079, +1 paid share), "
    "MINT holds 13,358,000,000 TOKEN, pair reserves 0/0 — still PENDING, never previewed while not open.")
snap["timestamp_wib"] = "2026-11-01T22:01:00+07:00"
snap["note"] = (snap["note"] + " "
    "Run 2026-11-01 22:01 WIB: HIVE 663 (+23, velocity now PASSES again: 0.689/min, 2.08x, >=20 tokens — was failing at 21:31; still strong lead, NOT a candidate: X unverified), "
    "Bubblebruin 681/7777 = 8.8% verified free (still EARLY, age + X unverified, velocity still fails 0.25x), binanceai.fun still pending (launched false, totalShares 3080), "
    "scan window 131068887-131070886 (2000 blocks, 80 Ankr calls, 0 errors, 430 NFT contracts, 6084 mints; skipped gap 131066400-131068886 recorded because head minus last_scanned exceeded the 2000 cap), "
    "no new early lead (20 first-seen verified+free-shaped contracts triaged: closest were Agent Harvest Land 2185 total vs 390 window mints, Sundial Agent 297 vs 155, Beacon Agent 289 vs 88, Bluefroggo 176 vs 73, Rattleboy 111 vs 48 — all totals above window mints with no same-day launch evidence, so first mints in this run NOT verified; rest are 7000-template continuations or free-exhausted lanes Chromecricket/Jiucaillama with freeClaimed = FREE_SUPPLY), "
    "Sourcify feed cross-check 1 match (Sundial Agent, already in scan triage — no double report), seen file updated to 941, watermark advanced to 131070886.")
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
added = 0
for c in scan["contracts"]:
    key = c["address"].lower()
    if key not in seen["contracts"]:
        seen["contracts"][key] = c["first_block"]
        added += 1
seen["_meta"]["contracts_count"] = len(seen["contracts"])
seen["_meta"]["last_scan_wib"] = "2026-11-01 ~22:31 WIB (run 22:01 WIB)"
seen["_meta"]["last_scan_window"] = "blocks 131068887-131070886 (2000 blocks, head 131070886); skipped gap 131066400-131068886 (window exceeded 2000 cap)"
seen["_meta"]["last_scan_added"] = added
json.dump(seen, open(BASE + "onchain-scan-seen.json", "w"), indent=1)
state["last_scanned_block"] = scan["to_block"]
state["last_scan_window_from"] = scan["from_block"]
state["last_scan_wib"] = "2026-11-01T22:31:00+07:00"
state["ankr_calls"] = scan["ankr_calls"]
state["errors"] = scan["errors"]
state["nft_contracts"] = len(scan["contracts"])
state["note"] = ("Run 22:01 WIB scan: 2000 blocks (capped; head 131070886 minus last_scanned 131066399 = 4487 > 2000, "
    "so only the most recent 2000 scanned; skipped gap 131066400-131068886 recorded, never scanned). "
    "Scan wall time ~18 min with python3 -u (log fetch fast; per-contract checks dominate). "
    "BSC block pace explains ~4000+ blocks per 30 min and the recurring gap; changing the cap needs its own user approval; it is NOT changed here. "
    "Next run scans from last_scanned_block+1, capped at 2000 blocks.")
json.dump(state, open(BASE + "onchain-scan-state.json", "w"), indent=1)
print(f"snapshot updated; seen added {added}, total {len(seen['contracts'])}; watermark -> {scan['to_block']}")
