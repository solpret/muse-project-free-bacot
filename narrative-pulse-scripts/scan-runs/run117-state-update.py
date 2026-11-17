#!/usr/bin/env python3
"""Run 117 state update (read-only bookkeeping): last_run + paid_trend_run117 +
inbound_log_leg_run117. No mint-pattern event this run, so no reported_findings
entry. No preview/mint/sign/login."""
import json, shutil
from pathlib import Path

HOME = Path.home()
NP = HOME / "workspace/narrative-pulse"
STATE = NP / "tracked-wallet-mint-scan-state.json"
shutil.copy(STATE, NP / "tracked-wallet-mint-scan-state.json.bak-run117-pre")
s = json.load(open(STATE))

s["last_run"] = {
 "run": 117,
 "block_start": 132342276,
 "block_end": 132349881,
 "window_wib": "2026-11-08 13:11:56 - 2026-11-08 14:07:45 WIB (tx times); run executed ~14:05 WIB - ~14:50 WIB; sent-pass in-window txs 177, 0 mint-pattern txs (AFeng 11 txs this run - 6 sale-calls 0x4d819a2a to 0x1de4... total 1.95 BNB, 0 mint logs - dividend-tracker pattern did NOT repeat; runs 114-117: no repeat)",
 "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set); 55/55 first attempt, 0 failed; 7 wallets active (AFeng back with 11 txs, up from 6 active in run 116).",
 "method_note": "Sent pass Ankr ankr_getTransactionsByAddress via module: 55/55 OK first attempt (177 txs), 0 failed - no same-run retry needed. Receipts via fast_rpc batch (6, ~4s pause) for 117 non-approve candidates: 117 status 1, 0 status 0, 0 NULL - no race fallbacks. Mint-pattern txs: 0 - AFeng (0xbf00...) 11 txs: 6 sale-calls 0x4d819a2a to 0x1de4... (1.2 BNB 13:42:21 WIB, 0.75 BNB 13:47:34 WIB, 0 BNB x4), 4 approvals (2 to 0xb47574a4..., 1 to 0x4e6533dc..., 1 to 0x29921a53...), 1 plain BNB self-transfer 0.4002578872418582 BNB 14:00:04 WIB - 0 mint logs, so the dividend-tracker pattern of runs 70/75/101/102/113 did NOT repeat this run (runs 114-117: no repeat). future1001.ai (0x355e...) 0 txs this run. 0x2325... 0 txs; 0x8e96... 0 txs; 0x6ba79dcc/0x89220022/0xda91cefe 0 txs. Paid: 25 tokens; max 3 wallets/token (14 tokens at 3 wallets, ALL the same churn trio 0x3803/0xad94/0xc7c5; 5 at 2, all pair 0x3628/0xa0c1; 6 at 1 - 4x 0x7488, 2x AFeng approval targets). Overlap with run-116 paid tokens: 0 - the ...7777 churn set turned over COMPLETELY again - fourteenth straight run with 0 churn overlap (runs 104-117 also 0). ZERO new rotations - the 27-wallet machine set had 0 txs this run (no buys, no sells, no approvals from any of the 27; verified overlap with active wallets = empty). The named-rotation streak ENDED run 104 (runs 97-103); run 117 has 0, fourteenth straight quiet run. No anomaly to report under the fast-path amendment (no new token, no name/symbol appearing, no size anomaly among machine buys, no free-mint path; max single churn tx 0.0001 BNB - pure micro churn; AFeng sale-calls 1.2/0.75 BNB are the known dividend-tracker shape, not machine buys). Trigger >25% NOT met by any token (max 3 wallets = 5.5%). No preview, no execution. Seatbelt 1e9c STALLED at 26: 0 wallets this run (0 buys, 0 sells) - sell-wallet union run101+run102 = 26/27, runs 103-117 add 0 - did NOT reach 27. NOT a new rotation; watch run 118 the same way. Deployments: ZERO - fourteenth straight run without deployments (run 104: 0, run 105: 0, run 106: 0, run 107: 0, run 108: 0, run 109: 0, run 110: 0, run 111: 0, run 112: 0, run 113: 0, run 114: 0, run 115: 0, run 116: 0, run 117: 0; runs 97-103 had 25/72/64/32/35/70/68) - verified from raw receipts contractAddress fields, not the parsed JSON. Inbound list for run 117 = run116 list (1734) + 0 deployments + 0 new rotation tokens (total 1734, unchanged). 0xc7c5... 43 txs (0.00260187 BNB); 0x3803... 42 txs (0.000364 BNB); 0xad94... 40 txs (0.00049 BNB); 0x3628... 15 txs (0.0005 BNB); 0xa0c1... 15 txs (0.0005 BNB); 0x7488d5da... 11 txs (0.00034219 BNB); 0xbf00... 11 txs (2.35025789 BNB). 2 plain BNB transfers this run (0xc7c5... -> 0x7f51d464... 0.002111872411842614 BNB 13:12:49 WIB - same recipient as runs 109/112/114, amount slightly different from 0.00205953 BNB; AFeng self-transfer 0.4002578872418582 BNB 14:00:04 WIB; runs 113: 2, run 114: 1, run 115: 0, run 116: 0). Selectors (sent pass, 177 txs): 60 approvals (0x095ea7b3) + 42 PCS buys (0xb6f9de95) + 39 PCS sells (0x791ac947) + 28 aggregator (0x39ecce49) + 6 sale-calls (0x4d819a2a) + 2 empty-input. NO contract creations, NO transfers (0xa9059cbb). Nonzero-value txs 60, total 2.35505595 BNB, max 1.2 BNB (AFeng sale-call; churn micro total only ~0.0048 BNB). Most active wallets: 0xc7c5faa2 43, 0x38031ca8 42, 0xad94ee77 40, 0x3628764a 15, 0xa0c1e94f 15, 0x7488d5da 11, 0xbf004bff 11. 0 NULL receipts this run. 0 status-0 txs. Inbound leg (amendment 12:02 WIB): Ankr getLogs address-filtered per contract, 1734 contracts, 0 hits (0 inbound-only), 10761 logs (10744 slices + 17 retry), window 132342276-132349881. 35 slices of ~50 contracts in 6 parallel rounds (detached via setsid/nohup; rounds ~4-6 min each). 15 in-slice failures (ALL 'Remote end closed connection without response' - down from 23 in run 116) ALL recovered same-run: retry (run117-inbound117-retry.py, detached via setsid) finished 15/15, 17 logs, 0 hits, 0 failed. 0 FAILED after retry. 6 truncated contracts, all topic-filtered to 0 logs (0x1de4... sale AFeng, 0x55d398... USDT, 0x6288..., 0x636fdfa9... tracker -> 0 logs = tracker pattern did not repeat, 0x63de... AGC, 0x7857...). Window FULLY CLOSED in-run, no retry deferred to run 118. Pair retry 8/8 FAILED this run (all eight pairs: a6e6/887c/2bfb/c459/43c8/cfdb/0cf8/e68b - token0()/token1() all 'all endpoints failed' via fast_rpc race, OSError/TimeoutError, in run117-pair-retry.py) - unverified, not absence; 35th consecutive run for a6e6/887c/2bfb/c459, 30th for 43c8, 29th for cfdb/0cf8/e68b; retry run 118. fast_rpc race outage TOTAL during the pair retry again - but the receipts batch pass worked fine earlier in the same run, so the outage is time-varying, not permanent. A failed race read is UNVERIFIED, never absence - retry, don't conclude. Pointer-discovery (amendment 19:10): 0 contracts processed - no new mint contracts this run (0 mint logs; AFeng produced none) and the backfill queue is empty (bridge 115 contracts, 0 not_evaluated); bridge unchanged. CHAT REPORT this run: NONE - no new mints, no Free Bacot signal, no anomaly, no auto-mint trigger, no guard block. No preview/mint/sign/login/purchase by this job."
}

s["paid_trend_run117"] = ("25 tokens paid-bought; max 3 wallets/token (14 at 3, all churn trio 0x3803/0xad94/0xc7c5; "
 "5 at 2, all pair 0x3628/0xa0c1; 6 at 1 - 4x 0x7488, 2x AFeng approval targets); overlap vs run 116: 0 (fourteenth straight complete turnover); "
 "AFeng back with 11 txs (6 sale-calls 0x4d819a2a to 0x1de4... total 1.95 BNB, 0 mint logs - tracker pattern did NOT repeat; 1 plain BNB self-transfer 0.4002578872418582 BNB); future1001.ai 0 txs; "
 "total nonzero value 2.35505595 BNB across 60 txs, max single 1.2 BNB (AFeng sale-call; churn micro total only ~0.0048 BNB); "
 "no token >=12 wallets, no signal, no trigger.")

s["inbound_log_leg_run117"] = ("Ankr getLogs address-filtered, 1734 contracts, 10761 logs (10744 slices + 17 retry), 0 hits, 0 inbound-only, "
 "window 132342276-132349881; 15 in-slice failures (all 'Remote end closed connection without response' - down from 23 in run 116) "
 "recovered same-run: retry 15/15 via run117-inbound117-retry.py (17 logs, 0 hits, 0 failed); "
 "6 truncated contracts topic-filtered (all to 0 logs, incl. tracker 0x636fdfa9 -> 0); window fully closed.")

n = s.get("next_run_note", "")
repls = [
 ("Next run sent-tx window starts from block 132342276. RETRY run 117:",
  "Next run sent-tx window starts from block 132349882. RETRY run 118:"),
 ("34 consecutive runs", "35 consecutive runs"),
 ("(unreadable run 88-116, 29 consecutive", "(unreadable run 88-117, 30 consecutive"),
 ("(token0/token1 unreadable run 89-116, 28 consecutive", "(token0/token1 unreadable run 89-117, 29 consecutive"),
 ("0 wallets runs 103-116", "0 wallets runs 103-117"),
 ("0 wallets runs 91-116, 26th quiet run", "0 wallets runs 91-117, 27th quiet run"),
 ("0 wallets runs 90-116, 27th quiet run", "0 wallets runs 90-117, 28th quiet run"),
]
for old, new in repls:
    if old in n:
        n = n.replace(old, new, 1)
        print(f"replaced: {old[:60]}...")
    else:
        print(f"NOT FOUND (skipped): {old[:80]}")
n = ("(Run 117: inbound list = run116 list (1734) + 0 deployments + 0 new rotation tokens; window fully closed "
     "132342276-132349881, 0 hits, 15 in-chunk failures (Ankr 'Remote end closed connection', down from 23) recovered same-run 15/15 via run117-inbound117-retry.py (17 logs, 0 hits, 0 failed); "
     "1e9c still STALLED 26/27, 1153 STALLED 26, 79cd STALLED 20; AFeng BACK with 11 txs (6 sale-calls 1.95 BNB, 0 mint logs - tracker pattern did NOT repeat); "
     "paid overlap vs run 116: 0 (churn set itself turned over completely, 14th straight run); total value 2.35505595 BNB (max 1.2 BNB) vs 0.00250384 BNB run 116 - AFeng returned.) " + n)
s["next_run_note"] = n

json.dump(s, open(STATE, "w"), indent=1)
print("state updated: last_run=117, paid_trend_run117 + inbound_log_leg_run117 added")
print("next window starts 132349882")
print("backup:", NP / "tracked-wallet-mint-scan-state.json.bak-run117-pre")
