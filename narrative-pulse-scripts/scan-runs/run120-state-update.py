#!/usr/bin/env python3
"""Run 120 state update (read-only bookkeeping): last_run + paid_trend_run120 +
inbound_log_leg_run120. No mint-pattern event this run, so no reported_findings
entry. No preview/mint/sign/login."""
import json, shutil
from pathlib import Path

HOME = Path.home()
NP = HOME / "workspace/narrative-pulse"
STATE = NP / "tracked-wallet-mint-scan-state.json"
shutil.copy(STATE, NP / "tracked-wallet-mint-scan-state.json.bak-run120-pre")
s = json.load(open(STATE))

s["last_run"] = {
 "run": 120,
 "block_start": 132365696,
 "block_end": 132373870,
 "window_wib": "2026-11-08 16:09:29 - 2026-11-08 17:07:46 WIB (tx times); run executed ~17:05 WIB - ~17:45 WIB; sent-pass in-window txs 175, 0 mint-pattern txs (AFeng 11 txs this run - 8 sale-calls 0x4d819a2a to 0x1de4... total 1.575 BNB, 0 mint logs - dividend-tracker pattern did NOT repeat; runs 114-120: no repeat)",
 "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set); 55/55 first attempt, 0 failed; 7 wallets active (AFeng 11 txs, up from 4 in run 119; 0x81c3d1b4 quiet again with 0 txs).",
 "method_note": "Sent pass Ankr ankr_getTransactionsByAddress via module: 55/55 OK first attempt (175 txs), 0 failed - no same-run retry needed. Receipts via fast_rpc batch (6, ~4s pause) for 118 non-approve candidates: 118 status 1, 0 status 0, 0 NULL - no race fallbacks. Mint-pattern txs: 0 - AFeng (0xbf00...) 11 txs: 8 sale-calls 0x4d819a2a to 0x1de4... (0.5 BNB 16:45:37 WIB, 0.25 BNB 16:32:25 WIB, 0.25 BNB 16:31:25 WIB, 0.325 BNB 16:30:53 WIB, 0.25 BNB 16:13:51 WIB, 0 BNB x3) + 3 approvals to 0x5f56.../0x46c6.../0xba30..., 0 mint logs, so the dividend-tracker pattern of runs 70/75/101/102/113 did NOT repeat this run (runs 114-120: no repeat). 0x81c3d1b4 (tier-ab, active in run 119 with the 50-USDT buy) 0 txs this run - quiet again, no follow-up action. future1001.ai (0x355e...) 0 txs this run. 0x2325... 0 txs; 0x8e96... 0 txs; 0x6ba79dcc/0x89220022/0xda91cefe 0 txs. Paid: 27 tokens; max 3 wallets/token (14 tokens at 3 wallets, ALL the same churn trio 0x3803/0xad94/0xc7c5, all ...7777; 5 at 2, all pair 0x3628/0xa0c1; 8 at 1 - 3x 0x7488d5da, 5x AFeng). Overlap with run-119 paid tokens: 0 - the ...7777 churn set turned over COMPLETELY again - seventeenth straight run with 0 churn overlap (runs 104-120 also 0). ZERO new rotations - the 27-wallet machine set had 0 txs this run (no buys, no sells, no approvals from any of the 27; verified overlap with active wallets = empty). The named-rotation streak ENDED run 104 (runs 97-103); run 120 has 0, seventeenth straight quiet run. No anomaly to report under the fast-path amendment (no new machine token, no name/symbol appearing, no size anomaly among machine buys, no free-mint path; max single churn tx 0.0001 BNB - pure micro churn; AFeng sale-calls 0.5/0.325/0.25 BNB are the known dividend-tracker shape, not machine buys). Trigger >25% NOT met by any token (max 3 wallets = 5.5%). No preview, no execution. Seatbelt 1e9c STALLED at 26: 0 wallets this run (0 buys, 0 sells) - sell-wallet union run101+run102 = 26/27, runs 103-120 add 0 - did NOT reach 27. NOT a new rotation; watch run 121 the same way. Deployments: ZERO - seventeenth straight run without deployments (run 104: 0, run 105: 0, run 106: 0, run 107: 0, run 108: 0, run 109: 0, run 110: 0, run 111: 0, run 112: 0, run 113: 0, run 114: 0, run 115: 0, run 116: 0, run 117: 0, run 118: 0, run 119: 0, run 120: 0; runs 97-103 had 25/72/64/32/35/70/68) - verified from raw receipts contractAddress fields, not the parsed JSON. Inbound list for run 120 = run119 list (1734) + 0 deployments + 0 new rotation tokens (total 1734, unchanged). 0xad94... 43 txs; 0x3803... 41 txs; 0xc7c5... 40 txs; 0x3628... 15 txs; 0xa0c1... 15 txs; 0xbf00... 11 txs; 0x7488d5da... 10 txs. 0 plain BNB transfers this run (0 empty-input txs; runs 113: 2, run 114: 1, run 115: 0, run 116: 0, run 117: 2, run 118: 1, run 119: 1, run 120: 0). Selectors (sent pass, 175 txs): 57 approvals (0x095ea7b3) + 41 PCS buys (0xb6f9de95) + 42 PCS sells (0x791ac947) + 27 aggregator (0x39ecce49) + 8 sale-calls (0x4d819a2a). NO new selectors. NO contract creations, NO transfers (0xa9059cbb). Nonzero-value txs 60, total 1.57760139 BNB, max 0.5 BNB (AFeng sale-call; churn micro total only ~0.0026 BNB). Most active wallets: 0xad94ee77 43, 0x38031ca8 41, 0xc7c5faa2 40, 0x3628764a 15, 0xa0c1e94f 15, 0xbf004bff 11, 0x7488d5da 10. 0 NULL receipts this run. 0 status-0 txs. Inbound leg (amendment 12:02 WIB): Ankr getLogs address-filtered per contract, 1734 contracts, 0 hits (0 inbound-only), 11426 logs, window 132365696-132373870. 35 slices of ~50 contracts in 6 parallel rounds (detached via setsid/nohup; rounds ~3-4 min each). 0 in-slice failures this run (third clean run in a row; runs 118, 119, 120 all 0) - NO retry needed, window FULLY CLOSED in-run, no retry deferred to run 121. 8 truncated contracts, all topic-filtered to 0 logs (0x1de4... sale AFeng, 0x55d398... USDT, 0x6288..., 0x636fdfa9... tracker -> 0 logs = tracker pattern did not repeat, 0x63de... AGC, 0x7857..., 0x7e2d..., 0x3dca...). Pair retry 8/8 FAILED this run (all eight pairs: a6e6/887c/2bfb/c459/43c8/cfdb/0cf8/e68b - token0()/token1() all 'all endpoints failed' via fast_rpc race, OSError, in run120-pair-retry.py) - unverified, not absence; 38th consecutive run for a6e6/887c/2bfb/c459, 33rd for 43c8, 32nd for cfdb/0cf8/e68b; retry run 121. fast_rpc race outage TOTAL during the pair retry again - but the receipts batch pass worked fine earlier in the same run, so the outage is time-varying, not permanent. A failed race read is UNVERIFIED, never absence - retry, don't conclude. Pointer-discovery (amendment 19:10): 0 contracts processed - no new mint contracts this run (0 mint logs; AFeng produced none) and the backfill queue is empty (bridge 115 contracts, 0 not_evaluated); bridge unchanged. CHAT REPORT this run: NONE - no new mints, no Free Bacot signal, no anomaly, no auto-mint trigger, no guard block. No preview/mint/sign/login/purchase by this job."
}

s["paid_trend_run120"] = ("27 tokens paid-bought; max 3 wallets/token (14 at 3, all churn trio 0x3803/0xad94/0xc7c5; "
 "5 at 2, all pair 0x3628/0xa0c1; 8 at 1 - 3x 0x7488d5da, 5x AFeng); overlap vs run 119: 0 (seventeenth straight complete turnover); "
 "AFeng 11 txs (8 sale-calls 0x4d819a2a to 0x1de4... total 1.575 BNB, max 0.5 BNB, 0 mint logs - tracker pattern did NOT repeat; 3 approvals); 0x81c3d1b4 quiet again (0 txs, after run-119 activity); future1001.ai 0 txs; "
 "total nonzero value 1.57760139 BNB across 60 txs, max single 0.5 BNB (AFeng sale-call; churn micro total only ~0.0026 BNB); "
 "0 plain BNB transfers this run (0 empty-input txs); "
 "no token >=12 wallets, no signal, no trigger.")

s["inbound_log_leg_run120"] = ("Ankr getLogs address-filtered, 1734 contracts, 11426 logs, 0 hits, 0 inbound-only, "
 "window 132365696-132373870; 0 in-slice failures (third clean run in a row; runs 118, 119, 120 all 0) - NO retry needed, window fully closed; "
 "8 truncated contracts topic-filtered (all to 0 logs, incl. tracker 0x636fdfa9 -> 0).")

n = s.get("next_run_note", "")
repls = [
 ("Next run sent-tx window starts from block 132365696. RETRY run 120:",
  "Next run sent-tx window starts from block 132373871. RETRY run 121:"),
 ("37 consecutive runs", "38 consecutive runs"),
 ("(unreadable run 88-119, 32 consecutive", "(unreadable run 88-120, 33 consecutive"),
 ("(token0/token1 unreadable run 89-119, 31 consecutive", "(token0/token1 unreadable run 89-120, 32 consecutive"),
 ("0 wallets runs 103-119", "0 wallets runs 103-120"),
 ("0 wallets runs 91-119, 29th quiet run", "0 wallets runs 91-120, 30th quiet run"),
 ("0 wallets runs 90-119, 30th quiet run", "0 wallets runs 90-120, 31st quiet run"),
]
for old, new in repls:
    if old in n:
        n = n.replace(old, new, 1)
        print(f"replaced: {old[:60]}...")
    else:
        print(f"NOT FOUND (skipped): {old[:80]}")
n = ("(Run 120: inbound list = run119 list (1734) + 0 deployments + 0 new rotation tokens; window fully closed "
     "132365696-132373870, 0 hits, 0 in-slice failures (third clean run in a row - no retry needed; runs 118, 119, 120 all 0); "
     "1e9c still STALLED 26/27, 1153 STALLED 26, 79cd STALLED 20; AFeng 11 txs (8 sale-calls 1.575 BNB, max 0.5 BNB, 0 mint logs - tracker pattern did NOT repeat, runs 114-120); "
     "0x81c3d1b4 quiet again (0 txs, after run-119 activity); "
     "paid overlap vs run 119: 0 (churn set itself turned over completely, 17th straight run); total value 1.57760139 BNB (max 0.5 BNB); "
     "0 plain BNB transfers this run (0 empty-input txs).) " + n)
s["next_run_note"] = n

json.dump(s, open(STATE, "w"), indent=1)
print("state updated: last_run=120, paid_trend_run120 + inbound_log_leg_run120 added")
print("next window starts 132373871")
print("backup:", NP / "tracked-wallet-mint-scan-state.json.bak-run120-pre")
