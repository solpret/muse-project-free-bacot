#!/usr/bin/env python3
"""Run 118 state update (read-only bookkeeping): last_run + paid_trend_run118 +
inbound_log_leg_run118. No mint-pattern event this run, so no reported_findings
entry. No preview/mint/sign/login."""
import json, shutil
from pathlib import Path

HOME = Path.home()
NP = HOME / "workspace/narrative-pulse"
STATE = NP / "tracked-wallet-mint-scan-state.json"
shutil.copy(STATE, NP / "tracked-wallet-mint-scan-state.json.bak-run118-pre")
s = json.load(open(STATE))

s["last_run"] = {
 "run": 118,
 "block_start": 132349882,
 "block_end": 132357942,
 "window_wib": "2026-11-08 14:09:54 - 2026-11-08 15:08:14 WIB (tx times); run executed ~15:05 WIB - ~15:40 WIB; sent-pass in-window txs 178, 0 mint-pattern txs (AFeng 30 txs this run - 20 sale-calls 0x4d819a2a to 0x1de4... total 2.75 BNB, 0 mint logs - dividend-tracker pattern did NOT repeat; runs 114-118: no repeat)",
 "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set); 55/55 first attempt, 0 failed; 7 wallets active (AFeng 30 txs, up from 11 in run 117).",
 "method_note": "Sent pass Ankr ankr_getTransactionsByAddress via module: 55/55 OK first attempt (178 txs), 0 failed - no same-run retry needed. Receipts via fast_rpc batch (6, ~4s pause) for 120 non-approve candidates: 120 status 1, 0 status 0, 0 NULL - no race fallbacks. Mint-pattern txs: 0 - AFeng (0xbf00...) 30 txs: 20 sale-calls 0x4d819a2a to 0x1de4... (2.75 BNB total, max 0.75 BNB 14:15:57 WIB, 8x 0 BNB) + 10 approvals, 0 mint logs, so the dividend-tracker pattern of runs 70/75/101/102/113 did NOT repeat this run (runs 114-118: no repeat). future1001.ai (0x355e...) 0 txs this run. 0x2325... 0 txs; 0x8e96... 0 txs; 0x6ba79dcc/0x89220022/0xda91cefe 0 txs. Paid: 26 tokens; max 3 wallets/token (11 tokens at 3 wallets, ALL the same churn trio 0x3803/0xad94/0xc7c5; 6 at 2, all pair 0x3628/0xa0c1; 9 at 1). Overlap with run-117 paid tokens: 0 - the ...7777 churn set turned over COMPLETELY again - fifteenth straight run with 0 churn overlap (runs 104-118 also 0). ZERO new rotations - the 27-wallet machine set had 0 txs this run (no buys, no sells, no approvals from any of the 27; verified overlap with active wallets = empty). The named-rotation streak ENDED run 104 (runs 97-103); run 118 has 0, fifteenth straight quiet run. No anomaly to report under the fast-path amendment (no new token, no name/symbol appearing, no size anomaly among machine buys, no free-mint path; max single churn tx 0.0001 BNB - pure micro churn; AFeng sale-calls 0.75/0.375/0.325 BNB are the known dividend-tracker shape, not machine buys). Trigger >25% NOT met by any token (max 3 wallets = 5.5%). No preview, no execution. Seatbelt 1e9c STALLED at 26: 0 wallets this run (0 buys, 0 sells) - sell-wallet union run101+run102 = 26/27, runs 103-118 add 0 - did NOT reach 27. NOT a new rotation; watch run 119 the same way. Deployments: ZERO - fifteenth straight run without deployments (run 104: 0, run 105: 0, run 106: 0, run 107: 0, run 108: 0, run 109: 0, run 110: 0, run 111: 0, run 112: 0, run 113: 0, run 114: 0, run 115: 0, run 116: 0, run 117: 0, run 118: 0; runs 97-103 had 25/72/64/32/35/70/68) - verified from raw receipts contractAddress fields, not the parsed JSON. Inbound list for run 118 = run117 list (1734) + 0 deployments + 0 new rotation tokens (total 1734, unchanged). 0xad94... 35 txs; 0xc7c5... 33 txs; 0x3803... 33 txs; 0xbf00... 30 txs (2.75 BNB sale-calls + approvals); 0x3628... 19 txs; 0xa0c1... 18 txs; 0x7488d5da... 10 txs. 1 plain BNB transfer this run (0x3628... -> 0xc0094886... 0.002056728188348988 BNB 14:26:31 WIB - NEW recipient, not the usual 0x7f51d464...; runs 113: 2, run 114: 1, run 115: 0, run 116: 0, run 117: 2, run 118: 1). Selectors (sent pass, 178 txs): 58 approvals (0x095ea7b3) + 37 PCS buys (0xb6f9de95) + 40 PCS sells (0x791ac947) + 22 aggregator (0x39ecce49) + 20 sale-calls (0x4d819a2a) + 1 empty-input. NO contract creations, NO transfers (0xa9059cbb). Nonzero-value txs 59, total 2.75456967 BNB, max 0.75 BNB (AFeng sale-call; churn micro total only ~0.0048 BNB). Most active wallets: 0xad94ee77 35, 0xc7c5faa2 33, 0x38031ca8 33, 0xbf004bff 30, 0x3628764a 19, 0xa0c1e94f 18, 0x7488d5da 10. 0 NULL receipts this run. 0 status-0 txs. Inbound leg (amendment 12:02 WIB): Ankr getLogs address-filtered per contract, 1734 contracts, 0 hits (0 inbound-only), 11955 logs, window 132349882-132357942. 35 slices of ~50 contracts in 6 parallel rounds (detached via setsid/nohup; rounds ~3-6 min each). 0 in-slice failures this run (first clean run since the failure counts started being tracked; run 117 had 15, run 116 had 23) - NO retry needed, window FULLY CLOSED in-run, no retry deferred to run 119. 9 truncated contracts, all topic-filtered to 0 logs (0x1de4... sale AFeng, 0x55d398... USDT, 0x6288..., 0x636fdfa9... tracker -> 0 logs = tracker pattern did not repeat, 0x63de... AGC, 0x7857..., 0x3bf1..., 0x3dca..., 0x7e2d...). Pair retry 8/8 FAILED this run (all eight pairs: a6e6/887c/2bfb/c459/43c8/cfdb/0cf8/e68b - token0()/token1() all 'all endpoints failed' via fast_rpc race, OSError/TimeoutError, in run118-pair-retry.py) - unverified, not absence; 36th consecutive run for a6e6/887c/2bfb/c459, 31st for 43c8, 30th for cfdb/0cf8/e68b; retry run 119. fast_rpc race outage TOTAL during the pair retry again - but the receipts batch pass worked fine earlier in the same run, so the outage is time-varying, not permanent. A failed race read is UNVERIFIED, never absence - retry, don't conclude. Pointer-discovery (amendment 19:10): 0 contracts processed - no new mint contracts this run (0 mint logs; AFeng produced none) and the backfill queue is empty (bridge 115 contracts, 0 not_evaluated); bridge unchanged. CHAT REPORT this run: NONE - no new mints, no Free Bacot signal, no anomaly, no auto-mint trigger, no guard block. No preview/mint/sign/login/purchase by this job."
}

s["paid_trend_run118"] = ("26 tokens paid-bought; max 3 wallets/token (11 at 3, all churn trio 0x3803/0xad94/0xc7c5; "
 "6 at 2, all pair 0x3628/0xa0c1; 9 at 1); overlap vs run 117: 0 (fifteenth straight complete turnover); "
 "AFeng 30 txs (20 sale-calls 0x4d819a2a to 0x1de4... total 2.75 BNB, 0 mint logs - tracker pattern did NOT repeat; 10 approvals); future1001.ai 0 txs; "
 "total nonzero value 2.75456967 BNB across 59 txs, max single 0.75 BNB (AFeng sale-call; churn micro total only ~0.0048 BNB); "
 "1 plain BNB transfer (0x3628... -> 0xc0094886... 0.00205673 BNB, NEW recipient); "
 "no token >=12 wallets, no signal, no trigger.")

s["inbound_log_leg_run118"] = ("Ankr getLogs address-filtered, 1734 contracts, 11955 logs, 0 hits, 0 inbound-only, "
 "window 132349882-132357942; 0 in-slice failures (first clean run; run 117 had 15) - NO retry needed, window fully closed; "
 "9 truncated contracts topic-filtered (all to 0 logs, incl. tracker 0x636fdfa9 -> 0).")

n = s.get("next_run_note", "")
repls = [
 ("Next run sent-tx window starts from block 132349882. RETRY run 118:",
  "Next run sent-tx window starts from block 132357943. RETRY run 119:"),
 ("35 consecutive runs", "36 consecutive runs"),
 ("(unreadable run 88-117, 30 consecutive", "(unreadable run 88-118, 31 consecutive"),
 ("(token0/token1 unreadable run 89-117, 29 consecutive", "(token0/token1 unreadable run 89-118, 30 consecutive"),
 ("0 wallets runs 103-117", "0 wallets runs 103-118"),
 ("0 wallets runs 91-117, 27th quiet run", "0 wallets runs 91-118, 28th quiet run"),
 ("0 wallets runs 90-117, 28th quiet run", "0 wallets runs 90-118, 29th quiet run"),
]
for old, new in repls:
    if old in n:
        n = n.replace(old, new, 1)
        print(f"replaced: {old[:60]}...")
    else:
        print(f"NOT FOUND (skipped): {old[:80]}")
n = ("(Run 118: inbound list = run117 list (1734) + 0 deployments + 0 new rotation tokens; window fully closed "
     "132349882-132357942, 0 hits, 0 in-slice failures (FIRST clean run - no retry needed; run 117 had 15, run 116 had 23); "
     "1e9c still STALLED 26/27, 1153 STALLED 26, 79cd STALLED 20; AFeng 30 txs (20 sale-calls 2.75 BNB, 0 mint logs - tracker pattern did NOT repeat, runs 114-118); "
     "paid overlap vs run 117: 0 (churn set itself turned over completely, 15th straight run); total value 2.75456967 BNB (max 0.75 BNB); "
     "1 plain BNB transfer to NEW recipient 0xc0094886... (not the usual 0x7f51d464...).) " + n)
s["next_run_note"] = n

json.dump(s, open(STATE, "w"), indent=1)
print("state updated: last_run=118, paid_trend_run118 + inbound_log_leg_run118 added")
print("next window starts 132357943")
print("backup:", NP / "tracked-wallet-mint-scan-state.json.bak-run118-pre")
