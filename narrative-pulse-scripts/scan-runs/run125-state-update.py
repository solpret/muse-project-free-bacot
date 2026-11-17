#!/usr/bin/env python3
"""Run 125 state update (read-only bookkeeping): last_run + paid_trend_run125 +
inbound_log_leg_run125. No new mints this run, so no new reported_findings
entries. No preview/mint/sign/login."""
import json, shutil
from pathlib import Path

HOME = Path.home()
NP = HOME / "workspace/narrative-pulse"
STATE = NP / "tracked-wallet-mint-scan-state.json"
shutil.copy(STATE, NP / "tracked-wallet-mint-scan-state.json.bak-run125-pre")
s = json.load(open(STATE))

s["last_run"] = {
 "run": 125,
 "block_start": 132406092,
 "block_end": 132413939,
 "window_wib": "2026-11-08 21:12:28 - 2026-11-08 22:08:28 WIB (tx times); run executed ~22:05 WIB - ~23:03 WIB; sent-pass in-window txs 217, 0 mint-pattern txs",
 "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set); 0 FAILED first attempt. 8 wallets active (0xc7c5faa2 50, 0xad94ee77 50, 0x38031ca8 49, 0x3628764a 20, 0xa0c1e94f 18, 0x7488d5da 12, AFeng 0xbf00... 10, 0x2325f175 8); future1001.ai 0 txs; 0x81c3d1b4 0 txs; 0x89220022 0 txs; 0x6ba79dcc 0 txs.",
 "method_note": "Sent pass Ankr ankr_getTransactionsByAddress via module: 55/55 OK first attempt (217 txs), 0 failed. Receipts via fast_rpc batch (6, ~4s pause) for 146 non-approve candidates: 146 status 1, 0 status 0, 0 NULL - no race fallbacks. 0 mint logs in any receipt - second straight zero-mint run (run 124 also 0; first zero-mint run since run 14). AFeng (0xbf00...) 10 txs: 7 sale-calls 0x4d819a2a to 0x1de4... total 3.625 BNB (values incl. max 1.75 BNB) + 2 approvals + 1 ERC20 transfer 0xa9059cbb to 0xa8de... value 0, 0 mint logs, so the dividend-tracker pattern of runs 70/75/101/102/113 did NOT repeat this run (runs 114-125: no repeat). 0x2325... 8 txs: 5 aggregator 0x27772d13 to 0x296b... (3 value 0 + 2 small-value 0.06 and 0.03 BNB) + 3 approvals (to 0xf4c7... x2 and 0xe916...), 0 mint logs, 0 receives. Paid: 33 tokens; max 3 wallets/token (16 tokens at 3 wallets, ALL the same churn trio 0x3803/0xad94/0xc7c5, all ...7777; 6 at 2 - pair 0x3628/0xa0c1; 11 at 1). Overlap with run-124 paid tokens: 0 - the ...7777 churn set itself turned over COMPLETELY again - twenty-second straight run with 0 churn overlap (runs 104-125 also 0). ZERO new rotations - the 27-wallet machine set had 0 txs this run (no buys, no sells, no approvals from any of the 27; verified overlap with active wallets = empty). The named-rotation streak ENDED run 104 (runs 97-103); run 125 has 0, twenty-second straight quiet run. No anomaly to report under the fast-path amendment (no new machine token, no name/symbol appearing, no size anomaly among machine buys, no free-mint path; churn trio PCS buys 32 txs total only 0.00112 BNB - pure micro churn; AFeng sale-calls 3.625 BNB are the known dividend-tracker shape, not machine buys; 0x2325 aggregator calls are mostly value 0 / tiny, not machine buys). Trigger >25% NOT met by any token (max 3 wallets = 5.5%). No preview, no execution. Seatbelt 1e9c STALLED at 26: 0 wallets this run (0 buys, 0 sells) - sell-wallet union run101+run102 = 26/27, runs 103-125 add 0 - did NOT reach 27. NOT a new rotation; watch run 126 the same way. Deployments: ZERO - twenty-second straight run without deployments (run 104: 0, run 105: 0, run 106: 0, run 107: 0, run 108: 0, run 109: 0, run 110: 0, run 111: 0, run 112: 0, run 113: 0, run 114: 0, run 115: 0, run 116: 0, run 117: 0, run 118: 0, run 119: 0, run 120: 0, run 121: 0, run 122: 0, run 123: 0, run 124: 0, run 125: 0; runs 97-103 had 25/72/64/32/35/70/68) - verified from raw receipts contractAddress fields, not the parsed JSON. Inbound list for run 125 = run124 list (1734) + 0 deployments + 0 new rotation tokens (total 1734, unchanged). 0 plain BNB transfers this run (runs 113: 2, run 114: 1, run 115: 0, run 116: 0, run 117: 2, run 118: 1, run 119: 1, run 120: 0, run 121: 2, run 122: 1, run 123: 3, run 124: 0, run 125: 0). Selectors (sent pass, 217 txs): 71 approvals (0x095ea7b3) + 52 PCS sells (0x791ac947) + 48 PCS buys (0xb6f9de95) + 33 aggregator (0x39ecce49) + 5 aggregator (0x27772d13, all 0x2325) + 7 sale-calls (0x4d819a2a, AFeng) + 1 ERC20 transfer (0xa9059cbb, AFeng) + 0 empty-input. NO contract creations. Nonzero-value txs 71, total 3.71805757 BNB, max 1.75 BNB (AFeng sale-call; churn micro total only 0.00112 BNB PCS buys). Most active wallets: 0xc7c5faa2 50, 0xad94ee77 50, 0x38031ca8 49, 0x3628764a 20, 0xa0c1e94f 18, 0x7488d5da 12, 0xbf004bff 10, 0x2325f175 8. 0 NULL receipts this run. 0 status-0 txs. Inbound leg (amendment 12:02 WIB): Ankr getLogs address-filtered per contract, 1734 contracts, 11600 logs (11439 slices + 161 retry), window 132406092-132413939, 0 hits, 0 inbound-only new. 35 slices of ~50 contracts in 6 parallel rounds (detached via setsid/nohup; rounds ~5-7 min each, Ankr slow this run). 47 in-slice failures (Ankr 'Remote end closed connection without response' / timeouts) - ALL 47 recovered SAME-RUN via run125-inbound-retry.py (161 logs, 0 hits, 0 failed) - window FULLY CLOSED in-run. 7 truncated contracts, all topic-filtered to 0 logs (same set as run 124: 0x1de4..., 0x3dca..., 0x55d3..., 0x6288..., 0x636f..., 0x63de..., 0x7857...). Pair retry 8/8 FAILED this run (all eight pairs: a6e6/887c/2bfb/c459/43c8/cfdb/0cf8/e68b - token0()/token1() all 'all endpoints failed' via fast_rpc race, OSError/TimeoutError) - unverified, not absence; 43rd consecutive run for a6e6/887c/2bfb/c459, 38th for 43c8, 37th for cfdb/0cf8/e68b; retry run 126. PROCESS LESSON (run 125): the first pair-retry launch died silently at startup - the compound shell command backgrounded the `cd` with the pointer pass (`&` split the cd from the second nohup), so python3 ran from /home/hatch and could not open run125-pair-retry.py; pgrep self-matched the shell command line and falsely showed PAIR-RUNNING for ~40 min while no pair-retry process existed and no log file was created. Re-launched from the scan-runs dir and it completed (8/8 failed). Rule: always cd in the same command as the python3 invocation, and verify the log file exists + the process by exact 'python3 <script>' match, never by a bare substring pgrep. fast_rpc race outage TOTAL during the pair retry again - but the receipts batch pass worked fine earlier in the same run, so the outage is time-varying, not permanent. A failed race read is UNVERIFIED, never absence - retry, don't conclude. Pointer-discovery (amendment 19:10 WIB, cap 5/run, 0 new contracts this run so backfill 5 oldest gate=None run-1 entries): AigentCard website VERIFIED via pointer (contractURI returns https://aigentcards.com/meta/collection.json, tokenURI #1744 external_url https://aigentcards.com/; fetched https://aigentcards.com/ HTTP 200, prints the exact contract) - bridge gate website_verified_via_pointer (NOT in Free Bacot snapshot, hint for routine job only, NOT a new lead by scan job). Emberforge, Rackfarm, Musk Agent, Agent Panda website_no_pointer_found: first pass contractURI()/tokenURI() reads ALL failed (fast_rpc race outage), RETRIED same-run and reads succeeded - Emberforge tokenURI -> emberforge-b9w.pages.dev/77.json fetched HTTP 200, metadata JSON only (Tier Legendary, no external_url, does NOT print contract) = metadata host only; Rackfarm contractURI + tokenURI both base64 JSON decoded, NO URLs; Musk Agent contractURI + tokenURI both empty; Agent Panda tokenURI -> agentpandabnb.xyz/metadata/867 but metadata host AND site root both unreachable (Remote end closed) - fetch-failure caveat, not a verified website. Bridge: 116 contracts (11 verified via pointer, 94 no-pointer, 11 still queued). PROCESS LESSON (run 125, receipts script): run125-receipts.py as generated by sed still wrote paid output to run124-paid.json (the sed list missed that filename) and OVERWROTE run 124's paid file; run124's paid map was reconstructed from run124 raw receipts (30 tokens, max 3 wallets - matches run-124 state note exactly) and restored, and run125's paid data (33 tokens) verified identical by independent re-derivation from run125 raw receipts before the restore. Rule: after sed-generating a run script, grep every output filename in it before running; the rotation-analysis script had the same class of bug (paid_prev pointed at run125 instead of run124) and was fixed before running. CHAT REPORT this run: NONE (silent) - 0 new mints, no Free Bacot signal, no anomaly, no auto-mint trigger, no guard block. No preview/mint/sign/login/purchase by this job."
}

s["paid_trend_run125"] = ("33 tokens paid-bought; max 3 wallets/token (16 at 3, all churn trio 0x3803/0xad94/0xc7c5; "
 "6 at 2 - pair 0x3628/0xa0c1; 11 at 1); overlap vs run 124: 0 tokens (churn set itself turned over completely, 22nd straight run); "
 "0x2325 8 txs (5 aggregator calls to 0x296b...: 3 value 0 + 2 small-value 0.06/0.03 BNB; 3 approvals; 0 mint logs, 0 receives); "
 "AFeng 10 txs (7 sale-calls 0x4d819a2a to 0x1de4... total 3.625 BNB, max 1.75 BNB; 2 approvals + 1 ERC20 transfer value 0; 0 mint logs - tracker pattern did NOT repeat); "
 "0x89220022 quiet (0 txs); future1001.ai 0 txs; 0x81c3d1b4 0 txs; 0x6ba79dcc 0 txs; "
 "sent pass 55/55 first attempt; total nonzero value 3.71805757 BNB across 71 txs, max single 1.75 BNB (AFeng sale-call; churn micro total only 0.00112 BNB PCS buys); "
 "0 plain BNB transfers this run; 0 deployments (22nd straight run); 0 machine-set activity (22nd straight quiet run).")

s["inbound_log_leg_run125"] = ("Ankr getLogs address-filtered, 1734 contracts, 11600 logs (11439 slices + 161 same-run retry), 0 hits, 0 inbound-only, "
 "47 in-slice failures ALL recovered same-run via retry (161 logs, 0 hits) - window FULLY CLOSED in-run; "
 "7 truncated contracts topic-filtered to 0 logs.")

n = s.get("next_run_note", "")
repls = [
 ("Next run sent-tx window starts from block 132406093. RETRY run 125:",
  "Next run sent-tx window starts from block 132413940. RETRY run 126:"),
 ("42 consecutive runs", "43 consecutive runs"),
 ("(unreadable run 88-124, 37 consecutive", "(unreadable run 88-125, 38 consecutive"),
 ("(token0/token1 unreadable run 89-124, 36 consecutive", "(token0/token1 unreadable run 89-125, 37 consecutive"),
 ("0 wallets runs 103-124", "0 wallets runs 103-125"),
 ("0 wallets runs 91-124, 34th quiet run", "0 wallets runs 91-125, 35th quiet run"),
 ("0 wallets runs 90-124, 35th quiet run", "0 wallets runs 90-125, 36th quiet run"),
]
for old, new in repls:
    if old in n:
        n = n.replace(old, new, 1)
        print(f"replaced: {old[:60]}...")
    else:
        print(f"NOT FOUND (skipped): {old[:80]}")
n = ("(Run 125: inbound list = run124 list (1734) + 0 deployments + 0 new rotation tokens; window FULLY CLOSED 132406092-132413939, 0 hits, 0 inbound-only, 47 in-slice failures ALL recovered same-run via retry (161 logs, 0 hits); "
     "sent pass 55/55 first attempt; 0 mint logs (second straight zero-mint run, run 124 also 0); "
     "AigentCard website VERIFIED via pointer (aigentcards.com, run-125 backfill; NOT in Free Bacot snapshot, hint only); 4 more backfill entries -> website_no_pointer_found (reads retried same-run after first-pass race outage; Agent Panda metadata host unreachable - fetch-failure caveat); bridge 116 (11 verified / 94 no-pointer / 11 queued); "
     "1e9c still STALLED 26/27, 1153 STALLED 26, 79cd STALLED 20; 0x2325 8 txs (5 aggregator, 3 value 0 + 0.06/0.03 BNB); 0x89220022 quiet (0 txs); "
     "AFeng 10 txs (7 sale-calls 3.625 BNB, max 1.75 BNB, 0 mint logs - tracker pattern did NOT repeat, runs 114-125); future1001.ai 0 txs; 0x81c3d1b4 0 txs; "
     "paid overlap vs run 124: 0 (churn set itself turned over completely, 22nd straight run); total value 3.71805757 BNB (max 1.75 BNB); "
     "0 plain BNB transfers this run; 0 deployments (22nd straight run).) " + n)
s["next_run_note"] = n

json.dump(s, open(STATE, "w"), indent=1)
print("state updated: last_run=125, paid_trend_run125 + inbound_log_leg_run125 added, 0 new reported_findings entries")
print("next window starts 132413940")
print("backup:", NP / "tracked-wallet-mint-scan-state.json.bak-run125-pre")
