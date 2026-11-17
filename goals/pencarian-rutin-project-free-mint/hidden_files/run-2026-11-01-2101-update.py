#!/usr/bin/env python3
"""Snapshot/seen/state update for free-mint-search run 2026-11-01 21:01 WIB.
Reads: run-2026-11-01-2101-read.json (block 131061518, ~21:02:23 WIB),
scan onchain-scan-2026-11-01-2101.json (window 131060025-131062024).
No previews/mints/signing. Watermark advances ONLY because the scan succeeded."""
import json

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
read = json.load(open(BASE + "run-2026-11-01-2101-read.json"))
scan = json.load(open(BASE + "onchain-scan-2026-11-01-2101.json"))
seen = json.load(open(BASE + "onchain-scan-seen.json"))
state = json.load(open(BASE + "onchain-scan-state.json"))

READ_WIB = "2026-11-01T21:02:23+07:00"
READ_BLOCK = read["block"]

# --- HIVE Agents: 590 -> 628, interval 20:31:51 -> 21:02:23 = 30.53 min ---
hive = snap["contracts"]["HIVE Agents"]
hive["previousTotalSupply"] = 590
hive["totalSupply"] = 628
hive["mintedInInterval"] = 38
hive["intervalMinutes"] = 30.53
hive["currentRatePerMin"] = 1.244
hive["previousRatePerMin"] = 0.616
hive["velocityVerified"] = True
hive["velocityNote"] = ("Run 21:01 WIB: +38 tokens in ~30.53 min (20:31:51->21:02:23) = 1.244/min; "
    "ratio vs prior 0.616/min = 2.02x AND 38 >= 20 tokens, so the velocity leg now PASSES. "
    "Stored as new baseline. HIVE remains watchlist-only (NOT a candidate) because the X leg is still unverified.")
hive["freePctInference"] = 62.8
hive["freePctNote"] = "Inference only: totalSupply 628 + totalPaid 0 -> 628/1000 FREE_SUPPLY = 62.8%; no freeClaimed view on contract."
hive["lastReadBlock"] = READ_BLOCK
hive["lastReadWib"] = READ_WIB
hive["baselineNote"] = ("Deep-sweep lead; % is inference from totalSupply + totalPaid=0, not a freeClaimed view; "
    "START_TIME 2026-11-01 16:00 WIB; free slot open for user wallet; X unverified; "
    "velocity PASSES at 21:01 WIB run (38 tokens, 2.02x) — reported once as a velocity change; "
    "still NOT a candidate (X unverified); already reported to main chat as watchlist lead 2026-11-01 ~19:36 WIB.")

# --- Bubblebruin: 172 -> 334, interval 20:41:12 -> 21:02:23 = 21.18 min ---
bub = snap["contracts"]["Bubblebruin"]
bub["previousTotalSupply"] = 172
bub["totalSupply"] = 334
bub["freeClaimed"] = 334
bub["freePctVerified"] = 4.3
bub["mintedInInterval"] = 162
bub["intervalMinutes"] = 21.18
bub["currentRatePerMin"] = 7.65
bub["velocityNote"] = ("Run 21:01 WIB: +162 tokens in ~21.18 min (20:41:12->21:02:23) = 7.65/min, recorded as the first "
    "interval baseline; velocity leg does NOT pass yet (no previous rate existed at interval start). "
    "Scan window of this run: 115 mints / 114 minters for Bubblebruin.")
bub["lastReadBlock"] = READ_BLOCK
bub["lastReadWib"] = READ_WIB
bub["baselineNote"] = ("EARLY lead reported once 2026-11-01 run 20:31 WIB. Never auto-minted/previewed. "
    "Promotes to strong lead only on all 3 strong-lead legs; to candidate only on ALL criteria + safety. "
    "At 21:01 WIB: 334/7777 = 4.3% (far below 50% strong leg), age still UNVERIFIED, X still UNVERIFIED, slot open by read.")

# --- Track B: binanceai.fun still pending ---
tb = snap["pending_claims"]["binanceai.fun"]
tb["totalShares_last"] = 2941
tb["lastCheckBlock"] = READ_BLOCK
tb["lastCheckWib"] = READ_WIB
tb["note"] = ("Seeded per user auto-claim approval 2026-11-01 ~20:27 WIB; dedicated 1h binanceai-claim-watch disabled as subsumed by routine track-B tracking. "
    "Already known to user (mint + blocked claim reported); do NOT re-report as a new pending claim — report only on open/claim/block/refund changes. "
    "Re-checked 21:01 run: launched still false, isRefundPhase false, failed false, totalShares 2941 (was 2892), "
    "MINT holds 13,358,000,000 TOKEN, pair reserves 0/0 — still PENDING, never previewed while not open.")

snap["timestamp_wib"] = "2026-11-01T21:01:00+07:00"
snap["note"] = ("Watchlist emptied 2026-11-01 ~18:38 WIB per user approval (27 contracts removed); the archive records were then PERMANENTLY DELETED 2026-11-01 ~18:55 WIB per user instruction — no archive file remains. "
    "Reader adapter: if totalSupply() reverts, use totalMinted() + MAX_SUPPLY()/remaining() and record the view used. "
    "Run 2026-11-01 ~19:31 WIB: no contracts re-read (empty keys), web/social sweep found no new candidate, no snapshot entry added. "
    "HIVE Agents added 2026-11-01 ~19:40 WIB per user approval of the deep-sweep fix (baseline totalSupply 564, fresh read); cadence stays 30m; strong-lead reporting rule + systematic Boltbook leg added to cron body same time. "
    "Run 2026-11-01 20:31 WIB (first wired scan): HIVE 590 (+19, velocity still fails on <20 tokens), binanceai.fun still pending (launched false), Bubblebruin added as EARLY lead (172/7777, 2.2%), scan watermark 131057467, seen file 289 contracts. "
    "Run 2026-11-01 21:01 WIB: HIVE 628 (+38, velocity now PASSES: 1.244/min, 2.02x, >=20 tokens — reported once as velocity change, still NOT a candidate: X unverified), "
    "Bubblebruin 334/7777 = 4.3% (still EARLY, age + X unverified), binanceai.fun still pending (launched false, totalShares 2941), "
    "scan window 131060025-131062024 (2000 blocks, 80 Ankr calls, 0 errors, 465 NFT contracts, 7723 mints; skipped gap 131057468-131060024 recorded because head minus last_scanned exceeded the 2000 cap), "
    "no new early lead (73 first-seen verified+free-shaped contracts triaged: all continuations with totals far above window mints, or free-exhausted), "
    "Sourcify feed cross-check 0 matches, seen file updated, watermark advanced to 131062024.")
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)

# --- Seen file: append every scan contract absent from seen ---
added = 0
for c in scan["contracts"]:
    key = c["address"].lower()
    if key not in seen["contracts"]:
        seen["contracts"][key] = c["first_block"]
        added += 1
seen["_meta"]["contracts_count"] = len(seen["contracts"])
seen["_meta"]["last_scan_wib"] = "2026-11-01 ~21:32 WIB (run 21:01 WIB)"
seen["_meta"]["last_scan_window"] = "blocks 131060025-131062024 (2000 blocks, head 131062024); skipped gap 131057468-131060024 (window exceeded 2000 cap)"
seen["_meta"]["last_scan_added"] = added
json.dump(seen, open(BASE + "onchain-scan-seen.json", "w"), indent=1)

# --- Scan state: advance watermark ONLY on success ---
state["last_scanned_block"] = scan["to_block"]
state["last_scan_window_from"] = scan["from_block"]
state["last_scan_wib"] = "2026-11-01T21:32:00+07:00"
state["ankr_calls"] = scan["ankr_calls"]
state["errors"] = scan["errors"]
state["nft_contracts"] = len(scan["contracts"])
state["note"] = ("Run 21:01 WIB scan: 2000 blocks (capped; head 131062024 minus last_scanned 131057467 = 4557 > 2000, "
    "so only the most recent 2000 scanned; skipped gap 131057468-131060024 recorded, never scanned). "
    "First scan attempt this run died without output (buffered stdout lost); rerun with python3 -u succeeded in ~26 min. "
    "Next run scans from last_scanned_block+1, capped at 2000 blocks.")
json.dump(state, open(BASE + "onchain-scan-state.json", "w"), indent=1)
print(f"snapshot updated; seen added {added}, total {len(seen['contracts'])}; watermark -> {scan['to_block']}")
