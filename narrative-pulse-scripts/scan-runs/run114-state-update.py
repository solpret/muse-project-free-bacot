#!/usr/bin/env python3
"""Run 114 state update (read-only bookkeeping): last_run + paid_trend_run114 +
inbound_log_leg_run114. No mint-pattern event this run, so no reported_findings
entry. No preview/mint/sign/login."""
import json, shutil
from pathlib import Path

HOME = Path.home()
NP = HOME / "workspace/narrative-pulse"
STATE = NP / "tracked-wallet-mint-scan-state.json"
shutil.copy(STATE, NP / "tracked-wallet-mint-scan-state.json.bak-run114-pre")
s = json.load(open(STATE))

s["last_run"] = {
 "run": 114,
 "block_start": 132318096,
 "block_end": 132325598,
 "window_wib": "2026-11-08 10:09:21 - 2026-11-08 11:05:32 WIB (tx times); run executed ~11:05 WIB - ~11:57 WIB; sent-pass in-window txs 180, 0 mint-pattern txs (AFeng sale-calls produced 0 mint logs - dividend-tracker pattern did NOT repeat this run)",
 "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set); 55/55 first attempt, 0 failed; 7 wallets active (same 7 as runs 112/113).",
 "method_note": "Sent pass Ankr ankr_getTransactionsByAddress via module: 55/55 OK first attempt (180 txs), 0 failed - no same-run retry needed. Receipts via fast_rpc batch (6, ~4s pause) for 120 non-approve candidates: 120 status 1, 0 status 0, 0 NULL - no race fallbacks. Mint-pattern txs: 0 - AFeng (0xbf00...) 5 sale-calls 0x4d819a2a to 0x1de4... (0.5 BNB 10:14:44 WIB hash 0x76dfaadc6863d14c338da61f57ef09ef84b361c5e64deee0196a5446b097afa3, 0.075 BNB 10:36:06 WIB hash 0x7a168d970fb6, 0 BNB x3) produced 0 mint logs, so the dividend-tracker pattern of runs 70/75/101/102/113 did NOT repeat this run (run 113 repeated after a one-run gap; run 114: no repeat). AFeng 8 txs total: 5 sale-calls (0.575 BNB) + 3 approvals. future1001.ai (0x355e...) 0 txs this run. Paid: 25 tokens; max 3 wallets/token (14 tokens at 3 wallets, ALL the same churn trio 0x3803/0xad94/0xc7c5; 6 at 2, all pair 0x3628/0xa0c1; 5 at 1 - 3x 0x7488, 2x AFeng). Overlap with run-113 paid tokens: 1 - token 0xe36a062176dc86cd8c5a2ddc743108bab27e7777, AFeng-only in BOTH runs (AFeng single-wallet paid receive, not a churn token); the ...7777 churn set itself turned over COMPLETELY again (all 14 trio + 6 pair tokens new) - eleventh straight run with 0 churn overlap (runs 104-114 also 0). ZERO new rotations - the 27-wallet machine set had 0 txs this run (no buys, no sells, no approvals from any of the 27). The named-rotation streak ENDED run 104 (runs 97-103); run 114 has 0, eleventh straight quiet run. No anomaly to report under the fast-path amendment (no new token, no name/symbol appearing, no size anomaly among machine buys, no free-mint path; the 0.5 BNB max single tx is AFeng's sale-call, not a machine buy). Trigger >25% NOT met by any token (max 3 wallets = 5.5%). No preview, no execution. Seatbelt 1e9c STALLED at 26: 0 wallets this run (0 buys, 0 sells) - sell-wallet union run101+run102 = 26/27, runs 103-114 add 0 - did NOT reach 27. NOT a new rotation; watch run 115 the same way. Deployments: ZERO - eleventh straight run without deployments (run 104: 0, run 105: 0, run 106: 0, run 107: 0, run 108: 0, run 109: 0, run 110: 0, run 111: 0, run 112: 0, run 113: 0, run 114: 0; runs 97-103 had 25/72/64/32/35/70/68) - verified from raw receipts contractAddress fields, not the parsed JSON. Inbound list for run 114 = run113 list (1734) + 0 deployments + 0 new rotation tokens (total 1734, unchanged). 0x2325... 0 txs this run; 0x8e96... 0 txs; 0x6ba79dcc/0x89220022/0xda91cefe 0 txs. 0xad94... 42 txs (0.00049 BNB); 0xc7c5... 45 txs (0.00254953 BNB); 0x3803... 43 txs (0.000364 BNB); 0xa0c1... 17 txs (0.0006 BNB); 0x3628... 16 txs (0.0006 BNB); 0x7488d5da... 9 txs (0.00024327 BNB); AFeng 0xbf00... 8 txs (0.575 BNB). 1 plain BNB transfer (empty input, 0xc7c5... -> 0x7f51d4642399aaa0a4a0e3c202c53bf8cdfd82f8, 0.00205953 BNB, 10:55:49 WIB - same recipient as runs 109/112; run 113: 2, both AFeng; run 112: 1, run 111: 0, run 110: 1, run 109: 1). Selectors (sent pass, 180 txs): 60 approvals (0x095ea7b3) + 43 PCS buys (0xb6f9de95) + 42 PCS sells (0x791ac947) + 29 aggregator (0x39ecce49) + 5 sale-calls (0x4d819a2a) + 1 empty-input. NO contract creations, NO transfers (0xa9059cbb). Nonzero-value txs 60, total 0.5798468 BNB (0.575 of it AFeng; micro churn only ~0.0048 BNB), max 0.5 BNB (AFeng sale-call 10:14:44 WIB; run 113 total was 6.10029756 BNB, max 4.59779515 BNB AFeng self-transfer). Most active wallets: 0xc7c5faa2 45, 0x38031ca8 43, 0xad94ee77 42, 0xa0c1e94f 17, 0x3628764a 16, 0x7488d5da 9, 0xbf004bff 8. 0 NULL receipts this run. 0 status-0 txs. Inbound leg (amendment 12:02 WIB): Ankr getLogs address-filtered per contract, 1734 contracts, 0 hits (0 inbound-only), 11574 logs (11564 slices + 10 retry), window 132318096-132325598. 35 slices of ~50 contracts in 6 parallel rounds from the start (lesson runs 109/111 applied - detached via setsid/nohup, no silent death; round 4 took ~9.5 min, others ~4-6 min). 35 in-slice failures (ALL 'Remote end closed connection without response' - sharp spike vs 1 in run 113; Ankr endpoint instability this run) ALL recovered same-run via run114-inbound114-retry.py (35/35, 10 logs, 0 hits) - 0 FAILED after retry. 9 truncated contracts, all topic-filtered to 0 logs (0x10b3..., 0x1de4... sale AFeng, 0x3dca..., 0x55d398... USDT, 0x6288..., 0x636fdfa9... tracker -> 0 logs = tracker pattern did not repeat, 0x63de... AGC, 0x7857..., 0x7e2d...). Window FULLY CLOSED in-run, no retry deferred to run 115. Pair retry 8/8 FAILED this run (all eight pairs: a6e6/887c/2bfb/c459/43c8/cfdb/0cf8/e68b - token0()/token1() all 'all endpoints failed' via fast_rpc race, OSError/TimeoutError, in run114-pair-retry.py) - unverified, not absence; 32nd consecutive run for a6e6/887c/2bfb/c459, 27th for 43c8, 26th for cfdb/0cf8/e68b; retry run 115. fast_rpc race outage TOTAL during the pair retry again - but the receipts batch pass worked fine earlier in the same run, so the outage is time-varying, not permanent. A failed race read is UNVERIFIED, never absence - retry, don't conclude. Pointer-discovery (amendment 19:10): 0 contracts processed - no new mint contracts this run (0 mint logs; AFeng sale-calls produced none) and the backfill queue is empty (bridge 115 contracts, 0 not_evaluated); bridge unchanged. CHAT REPORT this run: NONE - no new mints, no Free Bacot signal, no anomaly, no auto-mint trigger, no guard block. No preview/mint/sign/login/purchase by this job. NOTE: baw session re-logged-in 2026-11-08 ~08:27 WIB (QR pairing ae9248, expires 2026-11-10 08:34:54 WIB) - irrelevant to this run (no trigger met, no execution attempted), but any future auto-mint >25% execution needs a live baw session first."
}

s["paid_trend_run114"] = ("25 tokens paid-bought; max 3 wallets/token (14 at 3, all churn trio 0x3803/0xad94/0xc7c5; "
 "6 at 2, all pair 0x3628/0xa0c1; 5 at 1 - 3x 0x7488, 2x AFeng); overlap vs run 113: 1 token (0xe36a0621...7777, AFeng-only in both runs - "
 "NOT a churn token; the ...7777 churn set turned over completely again, eleventh straight run with 0 churn overlap); "
 "AFeng 8 txs (5 sale-calls to 0x1de4..., 0.575 BNB, 0 mint logs - tracker pattern did NOT repeat); "
 "total nonzero value 0.5798468 BNB across 60 txs (0.575 AFeng), max single 0.5 BNB (AFeng sale-call); "
 "no token >=12 wallets, no signal, no trigger.")

s["inbound_log_leg_run114"] = ("Ankr getLogs address-filtered, 1734 contracts, 11574 logs (11564 slices + 10 retry), 0 hits, 0 inbound-only, "
 "window 132318096-132325598; 35 in-slice failures (all 'Remote end closed connection without response' - spike vs 1 in run 113) "
 "recovered same-run 35/35 via run114-inbound114-retry.py (10 logs, 0 hits); "
 "9 truncated contracts topic-filtered (all to 0 logs, incl. tracker 0x636fdfa9 -> 0); window fully closed.")

n = s.get("next_run_note", "")
repls = [
 ("Next run sent-tx window starts from block 132318096. RETRY run 114:",
  "Next run sent-tx window starts from block 132325599. RETRY run 115:"),
 ("31 consecutive runs", "32 consecutive runs"),
 ("(unreadable run 88-113, 26 consecutive", "(unreadable run 88-114, 27 consecutive"),
 ("(token0/token1 unreadable run 89-113, 25 consecutive", "(token0/token1 unreadable run 89-114, 26 consecutive"),
 ("0 wallets runs 103-113", "0 wallets runs 103-114"),
 ("0 wallets runs 91-113, 23rd quiet run", "0 wallets runs 91-114, 24th quiet run"),
 ("0 wallets runs 90-113, 24th quiet run", "0 wallets runs 90-114, 25th quiet run"),
]
for old, new in repls:
    if old in n:
        n = n.replace(old, new, 1)
        print(f"replaced: {old[:60]}...")
    else:
        print(f"NOT FOUND (skipped): {old[:80]}")
n = ("(Run 114: inbound list = run113 list (1734) + 0 deployments + 0 new rotation tokens; window fully closed "
     "132318096-132325598, 0 hits, 35 in-chunk failures (Ankr 'Remote end closed connection' spike) recovered same-run 35/35 via run114-inbound114-retry.py; "
     "1e9c still STALLED 26/27, 1153 STALLED 26, 79cd STALLED 20; AFeng 5 sale-calls, 0 mint logs - dividend-tracker pattern did NOT repeat; "
     "paid overlap vs run 113: 1 token (0xe36a0621, AFeng-only both runs - churn set itself turned over completely, 11th straight run).) " + n)
s["next_run_note"] = n

json.dump(s, open(STATE, "w"), indent=1)
print("state updated: last_run=114, paid_trend_run114 + inbound_log_leg_run114 added")
print("next window starts 132325599")
print("backup:", NP / "tracked-wallet-mint-scan-state.json.bak-run114-pre")
