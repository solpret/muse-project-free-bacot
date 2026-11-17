#!/usr/bin/env python3
"""Run 119 state update (read-only bookkeeping): last_run + paid_trend_run119 +
inbound_log_leg_run119. No mint-pattern event this run, so no reported_findings
entry. No preview/mint/sign/login."""
import json, shutil
from pathlib import Path

HOME = Path.home()
NP = HOME / "workspace/narrative-pulse"
STATE = NP / "tracked-wallet-mint-scan-state.json"
shutil.copy(STATE, NP / "tracked-wallet-mint-scan-state.json.bak-run119-pre")
s = json.load(open(STATE))

s["last_run"] = {
 "run": 119,
 "block_start": 132357943,
 "block_end": 132365695,
 "window_wib": "2026-11-08 15:09:04 - 2026-11-08 16:06:25 WIB (tx times); run executed ~16:05 WIB - ~16:39 WIB; sent-pass in-window txs 155, 0 mint-pattern txs (AFeng 4 txs this run - 3 sale-calls 0x4d819a2a to 0x1de4... total 1.95 BNB, 0 mint logs - dividend-tracker pattern did NOT repeat; runs 114-119: no repeat)",
 "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set); 55/55 first attempt, 0 failed; 8 wallets active (AFeng 4 txs, down from 30 in run 118; 0x81c3d1b4 active again with 2 txs).",
 "method_note": "Sent pass Ankr ankr_getTransactionsByAddress via module: 55/55 OK first attempt (155 txs), 0 failed - no same-run retry needed. Receipts via fast_rpc batch (6, ~4s pause) for 103 non-approve candidates: 103 status 1, 0 status 0, 0 NULL - no race fallbacks. Mint-pattern txs: 0 - AFeng (0xbf00...) 4 txs: 3 sale-calls 0x4d819a2a to 0x1de4... (1.2 BNB 15:37:12 WIB, 0.75 BNB 15:15:00 WIB, 0 BNB 15:17:15 WIB) + 1 approval to 0xf0b3..., 0 mint logs, so the dividend-tracker pattern of runs 70/75/101/102/113 did NOT repeat this run (runs 114-119: no repeat). 0x81c3d1b4 (tier-ab, previously quiet) 2 txs: 0x27772d13 call to 0x296b... 15:51:01 WIB (50 USDT in -> 119,869.87 tokens 0x2567e74882... via WBNB route, 0.4 USDT to 0x799e... + 49.6 USDT swapped) + approval to USDT 0x55d398... - a ~$50 buy by ONE wallet only, NOT a signal (1 wallet), NOT a machine-token anomaly (not a machine buy, not micro size); wallet noted as active again, no follow-up action. future1001.ai (0x355e...) 0 txs this run. 0x2325... 0 txs; 0x8e96... 0 txs; 0x6ba79dcc/0x89220022/0xda91cefe 0 txs. Paid: 25 tokens; max 3 wallets/token (11 tokens at 3 wallets, ALL the same churn trio 0x3803/0xad94/0xc7c5, all ...7777; 6 at 2, all pair 0x3628/0xa0c1; 8 at 1 - 5x 0x7488d5da, 1x 0x81c3d1b4 (0x2567...), 2x AFeng). Overlap with run-118 paid tokens: 0 - the ...7777 churn set turned over COMPLETELY again - sixteenth straight run with 0 churn overlap (runs 104-119 also 0). ZERO new rotations - the 27-wallet machine set had 0 txs this run (no buys, no sells, no approvals from any of the 27; verified overlap with active wallets = empty). The named-rotation streak ENDED run 104 (runs 97-103); run 119 has 0, sixteenth straight quiet run. No anomaly to report under the fast-path amendment (no new machine token, no name/symbol appearing, no size anomaly among machine buys, no free-mint path; max single churn tx 0.0001 BNB - pure micro churn; AFeng sale-calls 1.2/0.75 BNB are the known dividend-tracker shape, not machine buys; 0x81c3 50-USDT buy is a single-wallet paid buy, not machine activity). Trigger >25% NOT met by any token (max 3 wallets = 5.5%). No preview, no execution. Seatbelt 1e9c STALLED at 26: 0 wallets this run (0 buys, 0 sells) - sell-wallet union run101+run102 = 26/27, runs 103-119 add 0 - did NOT reach 27. NOT a new rotation; watch run 120 the same way. Deployments: ZERO - sixteenth straight run without deployments (run 104: 0, run 105: 0, run 106: 0, run 107: 0, run 108: 0, run 109: 0, run 110: 0, run 111: 0, run 112: 0, run 113: 0, run 114: 0, run 115: 0, run 116: 0, run 117: 0, run 118: 0, run 119: 0; runs 97-103 had 25/72/64/32/35/70/68) - verified from raw receipts contractAddress fields, not the parsed JSON. Inbound list for run 119 = run118 list (1734) + 0 deployments + 0 new rotation tokens (total 1734, unchanged). 0xc7c5... 34 txs; 0x3803... 33 txs; 0xad94... 32 txs; 0x3628... 18 txs; 0xa0c1... 18 txs; 0x7488d5da... 14 txs; 0xbf00... 4 txs; 0x81c3d1b4... 2 txs. 1 plain BNB transfer this run (0xc7c5... -> 0x7f51d464... 0.002007164150486659 BNB 15:21:50 WIB - the USUAL recipient again; run 118 went to NEW recipient 0xc0094886...; runs 113: 2, run 114: 1, run 115: 0, run 116: 0, run 117: 2, run 118: 1, run 119: 1). Selectors (sent pass, 155 txs): 52 approvals (0x095ea7b3) + 39 PCS buys (0xb6f9de95) + 37 PCS sells (0x791ac947) + 22 aggregator (0x39ecce49) + 3 sale-calls (0x4d819a2a) + 1 empty-input + 1 new selector 0x27772d13 (0x81c3 USDT route). NO contract creations, NO transfers (0xa9059cbb). Nonzero-value txs 53, total 1.95467494 BNB, max 1.2 BNB (AFeng sale-call; churn micro total only ~0.0047 BNB). Most active wallets: 0xc7c5faa2 34, 0x38031ca8 33, 0xad94ee77 32, 0x3628764a 18, 0xa0c1e94f 18, 0x7488d5da 14, 0xbf004bff 4, 0x81c3d1b4 2. 0 NULL receipts this run. 0 status-0 txs. Inbound leg (amendment 12:02 WIB): Ankr getLogs address-filtered per contract, 1734 contracts, 0 hits (0 inbound-only), 10745 logs, window 132357943-132365695. 35 slices of ~50 contracts in 6 parallel rounds (detached via setsid/nohup; rounds ~3-4 min each). 0 in-slice failures this run (second clean run in a row; run 118 also 0, run 117 had 15) - NO retry needed, window FULLY CLOSED in-run, no retry deferred to run 120. 7 truncated contracts, all topic-filtered to 0 logs (0x1de4... sale AFeng, 0x55d398... USDT, 0x6288..., 0x636fdfa9... tracker -> 0 logs = tracker pattern did not repeat, 0x63de... AGC, 0x7857..., 0x7e2d...). Pair retry 8/8 FAILED this run (all eight pairs: a6e6/887c/2bfb/c459/43c8/cfdb/0cf8/e68b - token0()/token1() all 'all endpoints failed' via fast_rpc race, OSError/TimeoutError, in run119-pair-retry.py) - unverified, not absence; 37th consecutive run for a6e6/887c/2bfb/c459, 32nd for 43c8, 31st for cfdb/0cf8/e68b; retry run 120. fast_rpc race outage TOTAL during the pair retry again - but the receipts batch pass worked fine earlier in the same run, so the outage is time-varying, not permanent. A failed race read is UNVERIFIED, never absence - retry, don't conclude. Pointer-discovery (amendment 19:10): 0 contracts processed - no new mint contracts this run (0 mint logs; AFeng produced none) and the backfill queue is empty (bridge 115 contracts, 0 not_evaluated); bridge unchanged. CHAT REPORT this run: NONE - no new mints, no Free Bacot signal, no anomaly, no auto-mint trigger, no guard block. No preview/mint/sign/login/purchase by this job."
}

s["paid_trend_run119"] = ("25 tokens paid-bought; max 3 wallets/token (11 at 3, all churn trio 0x3803/0xad94/0xc7c5; "
 "6 at 2, all pair 0x3628/0xa0c1; 8 at 1 - 5x 0x7488d5da, 1x 0x81c3d1b4 (0x2567... ~$50 buy), 2x AFeng); overlap vs run 118: 0 (sixteenth straight complete turnover); "
 "AFeng 4 txs (3 sale-calls 0x4d819a2a to 0x1de4... total 1.95 BNB, 0 mint logs - tracker pattern did NOT repeat; 1 approval); 0x81c3d1b4 active again (2 txs, 50 USDT -> 119,869.87 tokens 0x2567...); future1001.ai 0 txs; "
 "total nonzero value 1.95467494 BNB across 53 txs, max single 1.2 BNB (AFeng sale-call; churn micro total only ~0.0047 BNB); "
 "1 plain BNB transfer (0xc7c5... -> 0x7f51d464... 0.00200716 BNB, usual recipient); "
 "no token >=12 wallets, no signal, no trigger.")

s["inbound_log_leg_run119"] = ("Ankr getLogs address-filtered, 1734 contracts, 10745 logs, 0 hits, 0 inbound-only, "
 "window 132357943-132365695; 0 in-slice failures (second clean run in a row; run 118 also 0) - NO retry needed, window fully closed; "
 "7 truncated contracts topic-filtered (all to 0 logs, incl. tracker 0x636fdfa9 -> 0).")

n = s.get("next_run_note", "")
repls = [
 ("Next run sent-tx window starts from block 132357943. RETRY run 119:",
  "Next run sent-tx window starts from block 132365696. RETRY run 120:"),
 ("36 consecutive runs", "37 consecutive runs"),
 ("(unreadable run 88-118, 31 consecutive", "(unreadable run 88-119, 32 consecutive"),
 ("(token0/token1 unreadable run 89-118, 30 consecutive", "(token0/token1 unreadable run 89-119, 31 consecutive"),
 ("0 wallets runs 103-118", "0 wallets runs 103-119"),
 ("0 wallets runs 91-118, 28th quiet run", "0 wallets runs 91-119, 29th quiet run"),
 ("0 wallets runs 90-118, 29th quiet run", "0 wallets runs 90-119, 30th quiet run"),
]
for old, new in repls:
    if old in n:
        n = n.replace(old, new, 1)
        print(f"replaced: {old[:60]}...")
    else:
        print(f"NOT FOUND (skipped): {old[:80]}")
n = ("(Run 119: inbound list = run118 list (1734) + 0 deployments + 0 new rotation tokens; window fully closed "
     "132357943-132365695, 0 hits, 0 in-slice failures (second clean run in a row - no retry needed; run 118 also 0); "
     "1e9c still STALLED 26/27, 1153 STALLED 26, 79cd STALLED 20; AFeng 4 txs (3 sale-calls 1.95 BNB, 0 mint logs - tracker pattern did NOT repeat, runs 114-119); "
     "0x81c3d1b4 active again (50 USDT -> 119,869.87 tokens 0x2567..., 1 wallet only, not a signal); "
     "paid overlap vs run 118: 0 (churn set itself turned over completely, 16th straight run); total value 1.95467494 BNB (max 1.2 BNB); "
     "1 plain BNB transfer to the USUAL recipient 0x7f51d464... (0.00200716 BNB).) " + n)
s["next_run_note"] = n

json.dump(s, open(STATE, "w"), indent=1)
print("state updated: last_run=119, paid_trend_run119 + inbound_log_leg_run119 added")
print("next window starts 132365696")
print("backup:", NP / "tracked-wallet-mint-scan-state.json.bak-run119-pre")
