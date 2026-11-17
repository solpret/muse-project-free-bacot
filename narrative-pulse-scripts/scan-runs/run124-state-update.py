#!/usr/bin/env python3
"""Run 124 state update (read-only bookkeeping): last_run + paid_trend_run124 +
inbound_log_leg_run124. No new mints this run, so no new reported_findings
entries. No preview/mint/sign/login."""
import json, shutil
from pathlib import Path

HOME = Path.home()
NP = HOME / "workspace/narrative-pulse"
STATE = NP / "tracked-wallet-mint-scan-state.json"
shutil.copy(STATE, NP / "tracked-wallet-mint-scan-state.json.bak-run124-pre")
s = json.load(open(STATE))

s["last_run"] = {
 "run": 124,
 "block_start": 132398352,
 "block_end": 132406092,
 "window_wib": "2026-11-08 20:11:40 - 2026-11-08 21:09:36 WIB (tx times); run executed ~21:05 WIB - ~21:51 WIB; sent-pass in-window txs 179, 0 mint-pattern txs",
 "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set); 0 FAILED first attempt. 8 wallets active (0xad94ee77 36, 0x38031ca8 35, 0xc7c5faa2 34, AFeng 0xbf00... 23, 0xa0c1e94f 18, 0x3628764a 16, 0x7488d5da 11, 0x2325f175 6); future1001.ai 0 txs; 0x81c3d1b4 0 txs; 0x89220022 0 txs; 0x6ba79dcc 0 txs.",
 "method_note": "Sent pass Ankr ankr_getTransactionsByAddress via module: 55/55 OK first attempt (179 txs), 0 failed. Receipts via fast_rpc batch (6, ~4s pause) for 120 non-approve candidates: 120 status 1, 0 status 0, 0 NULL - no race fallbacks. 0 mint logs in any receipt - NO new mints this run (first zero-mint run since run 14). AFeng (0xbf00...) 23 txs: 17 sale-calls 0x4d819a2a to 0x1de4... total 4.775 BNB (values 0x6, 0.075, 0.125, 0.25x3, 0.375, 0.5x3, 0.75, 1.2; max 1.2 BNB) + 6 approvals, 0 mint logs, so the dividend-tracker pattern of runs 70/75/101/102/113 did NOT repeat this run (runs 114-124: no repeat). 0x2325... only 6 txs (vs 31 run 123): 3 aggregator 0x27772d13 to 0x296b... value 0 + 3 approvals (to 0x4902... and 0x0fe8...), 0 mint logs, 0 receives. Paid: 30 tokens; max 3 wallets/token (12 tokens at 3 wallets, ALL the same churn trio 0x3803/0xad94/0xc7c5, all ...7777; 6 at 2 - pair 0x3628/0xa0c1; 12 at 1). Overlap with run-123 paid tokens: 1 token (0x15c33670ceadf3ff6de984647abb37a39ff77777, AFeng only in BOTH runs - NOT a churn token) - the ...7777 churn set itself turned over COMPLETELY again - twenty-first straight run with 0 churn overlap (runs 104-124 also 0). ZERO new rotations - the 27-wallet machine set had 0 txs this run (no buys, no sells, no approvals from any of the 27; verified overlap with active wallets = empty). The named-rotation streak ENDED run 104 (runs 97-103); run 124 has 0, twenty-first straight quiet run. No anomaly to report under the fast-path amendment (no new machine token, no name/symbol appearing, no size anomaly among machine buys, no free-mint path; max single churn buy 0.0001 BNB - pure micro churn; AFeng sale-calls 4.775 BNB are the known dividend-tracker shape, not machine buys; 0x2325 aggregator calls are value 0, not machine buys). Trigger >25% NOT met by any token (max 3 wallets = 5.5%). No preview, no execution. Seatbelt 1e9c STALLED at 26: 0 wallets this run (0 buys, 0 sells) - sell-wallet union run101+run102 = 26/27, runs 103-124 add 0 - did NOT reach 27. NOT a new rotation; watch run 125 the same way. Deployments: ZERO - twenty-first straight run without deployments (run 104: 0, run 105: 0, run 106: 0, run 107: 0, run 108: 0, run 109: 0, run 110: 0, run 111: 0, run 112: 0, run 113: 0, run 114: 0, run 115: 0, run 116: 0, run 117: 0, run 118: 0, run 119: 0, run 120: 0, run 121: 0, run 122: 0, run 123: 0, run 124: 0; runs 97-103 had 25/72/64/32/35/70/68) - verified from raw receipts contractAddress fields, not the parsed JSON. Inbound list for run 124 = run123 list (1734) + 0 deployments + 0 new rotation tokens (total 1734, unchanged). 0 plain BNB transfers this run (runs 113: 2, run 114: 1, run 115: 0, run 116: 0, run 117: 2, run 118: 1, run 119: 1, run 120: 0, run 121: 2, run 122: 1, run 123: 3, run 124: 0). Selectors (sent pass, 179 txs): 59 approvals (0x095ea7b3) + 40 PCS buys (0xb6f9de95) + 37 PCS sells (0x791ac947) + 23 aggregator (0x39ecce49) + 3 aggregator (0x27772d13, all 0x2325) + 17 sale-calls (0x4d819a2a, AFeng) + 0 empty-input. NO contract creations. Nonzero-value txs 63, total 4.77768195 BNB, max 1.2 BNB (AFeng sale-call; churn micro total only 0.00237 BNB PCS buys). Most active wallets: 0xad94ee77 36, 0x38031ca8 35, 0xc7c5faa2 34, 0xbf004bff 23, 0xa0c1e94f 18, 0x3628764a 16, 0x7488d5da 11, 0x2325f175 6. 0 NULL receipts this run. 0 status-0 txs. Inbound leg (amendment 12:02 WIB): Ankr getLogs address-filtered per contract, 1734 contracts, 11967 logs (11965 slices + 2 retry), window 132398352-132406092, 0 hits, 0 inbound-only new. 35 slices of ~50 contracts in 6 parallel rounds (detached via setsid/nohup; rounds ~5-7 min each, Ankr slow this run). 24 in-slice failures (Ankr 'Remote end closed connection without response'): 0x88a4..., 0x95ce..., 0xea1e..., 0xea23..., 0xec23..., 0xf888..., 0xf89c..., 0xfa90..., 0x4043..., 0x1836..., 0xce40..., 0x6d44..., 0x8461..., 0x2dcb..., 0x3732..., 0x3a12..., 0x4a3b..., 0xa46a..., 0xee0b..., 0x2008..., 0xd956..., 0x6d43..., 0x5656..., 0x8843... - ALL 24 recovered SAME-RUN via run124-inbound-retry.py (2 logs, 0 hits, 0 failed) - window FULLY CLOSED in-run. 7 truncated contracts, all topic-filtered to 0 logs (0x1de4..., 0x3dca..., 0x55d3..., 0x6288..., 0x636f..., 0x63de..., 0x7857...). Pair retry 8/8 FAILED this run (all eight pairs: a6e6/887c/2bfb/c459/43c8/cfdb/0cf8/e68b - token0()/token1() all 'all endpoints failed' via fast_rpc race, OSError/TimeoutError) - unverified, not absence; 42nd consecutive run for a6e6/887c/2bfb/c459, 37th for 43c8, 36th for cfdb/0cf8/e68b; retry run 125. fast_rpc race outage TOTAL during the pair retry again - but the receipts batch pass worked fine earlier in the same run, so the outage is time-varying, not permanent. A failed race read is UNVERIFIED, never absence - retry, don't conclude. Pointer-discovery (amendment 19:10 WIB, cap 5/run, 0 new contracts this run so backfill 5 oldest gate=None run-1 entries): DigDown website VERIFIED via pointer (contractURI base64 JSON external_link https://digdown.xyz, also in tokenURI #2657 + Sourcify sources + siteURL() in ABI; fetched https://digdown.xyz HTTP 200, prints the exact contract) - bridge gate website_verified_via_pointer (already in Free Bacot snapshot, hint for routine job only, NOT a new lead by scan job). BNB Bull Pass, ERC1155 unnamed, TRACE Genesis website_no_pointer_found WITH CAVEAT (contractURI() read FAILED - fast_rpc race outage, pointer incomplete not proven absent; tokenURI: BNB Bull Pass base64 JSON no URL, ERC1155 https://build-100.com/lab/meta/{id}.json HTTP 404, TRACE -> tracea.cc metadata host, fetched page does NOT print contract; Sourcify only generic doc/GitHub URLs or 404). Agrifarm website_no_pointer_found (contractURI read OK, base64 JSON no URL; tokenURI base64 JSON no URL; Sourcify generic only; ABI no site function). Bridge: 116 contracts (10 verified via pointer, 90 no-pointer, 16 still queued). CHAT REPORT this run: NONE (silent) - 0 new mints, no Free Bacot signal, no anomaly, no auto-mint trigger, no guard block. No preview/mint/sign/login/purchase by this job."
}

s["paid_trend_run124"] = ("30 tokens paid-bought; max 3 wallets/token (12 at 3, all churn trio 0x3803/0xad94/0xc7c5; "
 "6 at 2 - pair 0x3628/0xa0c1; 12 at 1); overlap vs run 123: 1 token (0x15c3...7777, AFeng only in both runs - NOT churn; "
 "churn set itself turned over completely, 21st straight run); "
 "0x2325 quiet (6 txs: 3 aggregator calls value 0 + 3 approvals; 0 mint logs, 0 receives); "
 "AFeng 23 txs (17 sale-calls 0x4d819a2a to 0x1de4... total 4.775 BNB, max 1.2 BNB; 0 mint logs - tracker pattern did NOT repeat); "
 "0x89220022 quiet (0 txs); future1001.ai 0 txs; 0x81c3d1b4 0 txs; "
 "sent pass 55/55 first attempt; total nonzero value 4.77768195 BNB across 63 txs, max single 1.2 BNB (AFeng sale-call; churn micro total only 0.00237 BNB PCS buys); "
 "0 plain BNB transfers this run; 0 deployments (21st straight run); 0 machine-set activity (21st straight quiet run).")

s["inbound_log_leg_run124"] = ("Ankr getLogs address-filtered, 1734 contracts, 11967 logs (11965 slices + 2 same-run retry), 0 hits, 0 inbound-only, "
 "24 in-slice failures ALL recovered same-run via retry (2 logs, 0 hits) - window FULLY CLOSED in-run; "
 "7 truncated contracts topic-filtered to 0 logs.")

n = s.get("next_run_note", "")
repls = [
 ("Next run sent-tx window starts from block 132398352. RETRY run 124:",
  "Next run sent-tx window starts from block 132406093. RETRY run 125:"),
 ("41 consecutive runs", "42 consecutive runs"),
 ("(unreadable run 88-123, 36 consecutive", "(unreadable run 88-124, 37 consecutive"),
 ("(token0/token1 unreadable run 89-123, 35 consecutive", "(token0/token1 unreadable run 89-124, 36 consecutive"),
 ("0 wallets runs 103-123", "0 wallets runs 103-124"),
 ("0 wallets runs 91-123, 33rd quiet run", "0 wallets runs 91-124, 34th quiet run"),
 ("0 wallets runs 90-123, 34th quiet run", "0 wallets runs 90-124, 35th quiet run"),
]
for old, new in repls:
    if old in n:
        n = n.replace(old, new, 1)
        print(f"replaced: {old[:60]}...")
    else:
        print(f"NOT FOUND (skipped): {old[:80]}")
n = ("(Run 124: inbound list = run123 list (1734) + 0 deployments + 0 new rotation tokens; window FULLY CLOSED 132398352-132406092, 0 hits, 0 inbound-only, 24 in-slice failures ALL recovered same-run via retry (2 logs, 0 hits); "
     "sent pass 55/55 first attempt; 0 mint logs (first zero-mint run since run 14); "
     "DigDown website VERIFIED via pointer (digdown.xyz, run-124 backfill; already in Free Bacot snapshot, hint only); 4 more backfill entries -> website_no_pointer_found (3 with contractURI-read-failed caveat); bridge 116 (10 verified / 90 no-pointer / 16 queued); "
     "1e9c still STALLED 26/27, 1153 STALLED 26, 79cd STALLED 20; 0x2325 quiet (6 txs, value 0); 0x89220022 quiet (0 txs); "
     "AFeng 23 txs (17 sale-calls 4.775 BNB, 0 mint logs - tracker pattern did NOT repeat, runs 114-124); future1001.ai 0 txs; 0x81c3d1b4 0 txs; "
     "paid overlap vs run 123: 1 token (AFeng-only, NOT churn; churn set itself turned over completely, 21st straight run); total value 4.77768195 BNB (max 1.2 BNB); "
     "0 plain BNB transfers this run; 0 deployments (21st straight run).) " + n)
s["next_run_note"] = n

json.dump(s, open(STATE, "w"), indent=1)
print("state updated: last_run=124, paid_trend_run124 + inbound_log_leg_run124 added, 0 new reported_findings entries")
print("next window starts 132406093")
print("backup:", NP / "tracked-wallet-mint-scan-state.json.bak-run124-pre")
