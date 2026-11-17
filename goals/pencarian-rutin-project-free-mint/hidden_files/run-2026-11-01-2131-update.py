#!/usr/bin/env python3
"""Snapshot/seen/state update for free-mint-search run 2026-11-01 21:31 WIB.
Reads: run-2026-11-01-2131-read.json (block 131066346, ~21:38:41 WIB),
scan onchain-scan-2026-11-01-2131.json (window 131064400-131066399).
No previews/mints/signing. Watermark advances ONLY because the scan succeeded."""
import json

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
read = json.load(open(BASE + "run-2026-11-01-2131-read.json"))
scan = json.load(open(BASE + "onchain-scan-2026-11-01-2131.json"))
seen = json.load(open(BASE + "onchain-scan-seen.json"))
state = json.load(open(BASE + "onchain-scan-state.json"))

READ_WIB = "2026-11-01T21:38:41+07:00"
READ_BLOCK = read["block"]

# --- HIVE Agents: 628 -> 640, interval 21:02:23 -> 21:38:41 = 36.30 min ---
# +12 tokens = 0.331/min; ratio vs prior 1.244/min = 0.27x AND 12 < 20 tokens
# => velocity leg now FAILS (was passing at 21:01). New baseline stored.
hive = snap["contracts"]["HIVE Agents"]
hive["previousTotalSupply"] = 628
hive["totalSupply"] = 640
hive["mintedInInterval"] = 12
hive["intervalMinutes"] = 36.30
hive["currentRatePerMin"] = 0.331
hive["previousRatePerMin"] = 1.244
hive["velocityVerified"] = False
hive["velocityNote"] = ("Run 21:31 WIB: +12 tokens in ~36.30 min (21:02:23->21:38:41) = 0.331/min; "
    "ratio vs prior 1.244/min = 0.27x AND 12 < 20 tokens, so the velocity leg now FAILS "
    "(it passed at 21:01 WIB). Stored as new baseline. HIVE remains a strong lead "
    "(age <=48h, free % inference 64.0%, slot open) but NOT a candidate: X still unverified "
    "and velocity now also fails.")
hive["freePctInference"] = 64.0
hive["freePctNote"] = "Inference only: totalSupply 640 + totalPaid 0 -> 640/1000 FREE_SUPPLY = 64.0%; no freeClaimed view on contract."
hive["lastReadBlock"] = READ_BLOCK
hive["lastReadWib"] = READ_WIB
hive["baselineNote"] = ("Deep-sweep lead; % is inference from totalSupply + totalPaid=0, not a freeClaimed view; "
    "START_TIME 2026-11-01 16:00 WIB; free slot open for user wallet; X unverified; "
    "velocity FAILED at 21:31 WIB run (12 tokens, 0.27x) after passing at 21:01 WIB; "
    "still NOT a candidate (X unverified); already reported to main chat as watchlist lead 2026-11-01 ~19:36 WIB, "
    "velocity-pass reported once at 21:01 WIB.")

# --- Bubblebruin: 334 -> 618, interval 21:02:23 -> 21:38:41 = 36.30 min ---
# +284 tokens = 7.82/min; ratio vs prior 7.65/min = 1.02x (< 1.5x) => velocity FAILS still.
# freeClaimed 617 vs totalSupply 618 (1 token difference, recorded plainly).
bub = snap["contracts"]["Bubblebruin"]
bub["previousTotalSupply"] = 334
bub["totalSupply"] = 618
bub["freeClaimed"] = 617
bub["freePctVerified"] = 7.9
bub["mintedInInterval"] = 284
bub["intervalMinutes"] = 36.30
bub["currentRatePerMin"] = 7.82
bub["previousRatePerMin"] = 7.65
bub["velocityNote"] = ("Run 21:31 WIB: +284 tokens in ~36.30 min (21:02:23->21:38:41) = 7.82/min, ratio vs prior "
    "7.65/min = 1.02x (< 1.5x), so the velocity leg still FAILS. Stored as new baseline. "
    "Scan window of this run: 72 mints / 72 minters for Bubblebruin. "
    "Note: freeClaimed 617 vs totalSupply 618 (1 token difference, unexplained by the views read).")
bub["lastReadBlock"] = READ_BLOCK
bub["lastReadWib"] = READ_WIB
bub["baselineNote"] = ("EARLY lead reported once 2026-11-01 run 20:31 WIB. Never auto-minted/previewed. "
    "Promotes to strong lead only on all 3 strong-lead legs; to candidate only on ALL criteria + safety. "
    "At 21:31 WIB: 617/7777 = 7.9% verified free (far below 50% strong leg), age still UNVERIFIED, "
    "X still UNVERIFIED, slot open by read, velocity still fails (1.02x).")

# --- Track B: binanceai.fun still pending ---
tb = snap["pending_claims"]["binanceai.fun"]
tb["totalShares_last"] = 3079
tb["lastCheckBlock"] = READ_BLOCK
tb["lastCheckWib"] = READ_WIB
tb["note"] = ("Seeded per user auto-claim approval 2026-11-01 ~20:27 WIB; dedicated 1h binanceai-claim-watch disabled as subsumed by routine track-B tracking. "
    "Already known to user (mint + blocked claim reported); do NOT re-report as a new pending claim — report only on open/claim/block/refund changes. "
    "Re-checked 21:31 run: launched still false, isRefundPhase false, failed false, totalShares 3079 (was 2941, +138 paid shares), "
    "MINT holds 13,358,000,000 TOKEN, pair reserves 0/0 — still PENDING, never previewed while not open.")

snap["timestamp_wib"] = "2026-11-01T21:31:00+07:00"
snap["note"] = ("Watchlist emptied 2026-11-01 ~18:38 WIB per user approval (27 contracts removed); the archive records were then PERMANENTLY DELETED 2026-11-01 ~18:55 WIB per user instruction — no archive file remains. "
    "Reader adapter: if totalSupply() reverts, use totalMinted() + MAX_SUPPLY()/remaining() and record the view used. "
    "Run 2026-11-01 ~19:31 WIB: no contracts re-read (empty keys), web/social sweep found no new candidate, no snapshot entry added. "
    "HIVE Agents added 2026-11-01 ~19:40 WIB per user approval of the deep-sweep fix (baseline totalSupply 564, fresh read); cadence stays 30m; strong-lead reporting rule + systematic Boltbook leg added to cron body same time. "
    "Run 2026-11-01 20:31 WIB (first wired scan): HIVE 590 (+19, velocity still fails on <20 tokens), binanceai.fun still pending (launched false), Bubblebruin added as EARLY lead (172/7777, 2.2%), scan watermark 131057467, seen file 289 contracts. "
    "Run 2026-11-01 21:01 WIB: HIVE 628 (+38, velocity now PASSES: 1.244/min, 2.02x, >=20 tokens — reported once as velocity change, still NOT a candidate: X unverified), "
    "Bubblebruin 334/7777 = 4.3% (still EARLY, age + X unverified), binanceai.fun still pending (launched false, totalShares 2941), "
    "scan window 131060025-131062024 (2000 blocks, 80 Ankr calls, 0 errors, 465 NFT contracts, 7723 mints; skipped gap 131057468-131060024 recorded because head minus last_scanned exceeded the 2000 cap), "
    "no new early lead (73 first-seen verified+free-shaped contracts triaged: all continuations with totals far above window mints, or free-exhausted), "
    "Sourcify feed cross-check 0 matches, seen file updated, watermark advanced to 131062024. "
    "Run 2026-11-01 21:31 WIB: HIVE 640 (+12, velocity now FAILS: 0.331/min, 0.27x, <20 tokens — was passing at 21:01; still strong lead, NOT a candidate: X unverified), "
    "Bubblebruin 617/7777 = 7.9% verified free (still EARLY, age + X unverified, velocity still fails 1.02x), binanceai.fun still pending (launched false, totalShares 3079), "
    "scan window 131064400-131066399 (2000 blocks, 80 Ankr calls, 0 errors, 535 NFT contracts, 10600 mints; skipped gap 131062025-131064399 recorded because head minus last_scanned exceeded the 2000 cap), "
    "no new early lead (65 first-seen verified+free-shaped contracts triaged: closest were Oathbots Pass 203 total vs 86 window mints, Ink Agent 316 vs 192, Harbour Agent 342 vs 196 — all totals above window mints with no same-day launch evidence, so first mints in this run NOT verified; rest are continuations with totals far above window mints), "
    "Sourcify feed cross-check 1 match (Harbour Agent, already in scan triage — no double report), seen file updated to 826, watermark advanced to 131066399.")
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)

# --- Seen file: append every scan contract absent from seen ---
added = 0
for c in scan["contracts"]:
    key = c["address"].lower()
    if key not in seen["contracts"]:
        seen["contracts"][key] = c["first_block"]
        added += 1
seen["_meta"]["contracts_count"] = len(seen["contracts"])
seen["_meta"]["last_scan_wib"] = "2026-11-01 ~22:06 WIB (run 21:31 WIB)"
seen["_meta"]["last_scan_window"] = "blocks 131064400-131066399 (2000 blocks, head 131066399); skipped gap 131062025-131064399 (window exceeded 2000 cap)"
seen["_meta"]["last_scan_added"] = added
json.dump(seen, open(BASE + "onchain-scan-seen.json", "w"), indent=1)

# --- Scan state: advance watermark ONLY on success ---
state["last_scanned_block"] = scan["to_block"]
state["last_scan_window_from"] = scan["from_block"]
state["last_scan_wib"] = "2026-11-01T22:06:00+07:00"
state["ankr_calls"] = scan["ankr_calls"]
state["errors"] = scan["errors"]
state["nft_contracts"] = len(scan["contracts"])
state["note"] = ("Run 21:31 WIB scan: 2000 blocks (capped; head 131066399 minus last_scanned 131062024 = 4375 > 2000, "
    "so only the most recent 2000 scanned; skipped gap 131062025-131064399 recorded, never scanned). "
    "Scan wall time ~26 min with python3 -u (log fetch fast this run; per-contract checks dominate). "
    "BSC block pace ~0.45s/block (per Boltbook post this evening) explains ~4000+ blocks per 30 min and the recurring gap; "
    "changing the cap needs its own user approval; it is NOT changed here. "
    "Next run scans from last_scanned_block+1, capped at 2000 blocks.")
json.dump(state, open(BASE + "onchain-scan-state.json", "w"), indent=1)
print(f"snapshot updated; seen added {added}, total {len(seen['contracts'])}; watermark -> {scan['to_block']}")
