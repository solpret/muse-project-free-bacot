#!/usr/bin/env python3
"""Run 121 state update (read-only bookkeeping): last_run + paid_trend_run121 +
inbound_log_leg_run121. No mint-pattern event this run, so no reported_findings
entry. No preview/mint/sign/login."""
import json, shutil
from pathlib import Path

HOME = Path.home()
NP = HOME / "workspace/narrative-pulse"
STATE = NP / "tracked-wallet-mint-scan-state.json"
shutil.copy(STATE, NP / "tracked-wallet-mint-scan-state.json.bak-run121-pre")
s = json.load(open(STATE))

s["last_run"] = {
 "run": 121,
 "block_start": 132373871,
 "block_end": 132381804,
 "window_wib": "2026-11-08 17:08:41 - 2026-11-08 18:07:18 WIB (tx times); run executed ~18:05 WIB - ~18:36 WIB; sent-pass in-window txs 142, 0 mint-pattern txs (future1001.ai 1 tx - plain 0.88 BNB transfer, 0 logs, NOT a mint; AFeng 3 txs - 2 sale-calls 0x4d819a2a to 0x1de4... total 0.5 BNB, 0 mint logs - dividend-tracker pattern did NOT repeat; runs 114-121: no repeat)",
 "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set); 55/55 first attempt, 0 failed; 8 wallets active (future1001.ai back with 1 tx after 0 in run 120; 0x81c3d1b4 quiet again with 0 txs).",
 "method_note": "Sent pass Ankr ankr_getTransactionsByAddress via module: 55/55 OK first attempt (142 txs), 0 failed - no same-run retry needed. Receipts via fast_rpc batch (6, ~4s pause) for 95 non-approve candidates: 95 status 1, 0 status 0, 0 NULL - no race fallbacks. Mint-pattern txs: 0 - future1001.ai (0x355e...) 1 tx: plain BNB transfer 0.88 BNB to 0xebcc394396f8bffd56b12b163bf6dfadab9cd3cd (NEW recipient, first plain transfer by future1001.ai observed in recent runs), 0 logs, status 1, NOT a mint, no follow-up action. AFeng (0xbf00...) 3 txs: 2 sale-calls 0x4d819a2a to 0x1de4... (0.5 BNB 17:25:25 WIB, 0 BNB 17:39:46 WIB) + 1 approval to 0xdd49..., 0 mint logs, so the dividend-tracker pattern of runs 70/75/101/102/113 did NOT repeat this run (runs 114-121: no repeat). 0x81c3d1b4 (tier-ab, active in run 119 with the 50-USDT buy) 0 txs this run - quiet again, no follow-up action. 0x2325... 0 txs; 0x8e96... 0 txs; 0x6ba79dcc/0x89220022/0xda91cefe 0 txs. Paid: 21 tokens; max 3 wallets/token (10 tokens at 3 wallets, ALL the same churn trio 0x3803/0xad94/0xc7c5, all ...7777; 6 at 2 - 5 pair 0x3628/0xa0c1 + 1 trio pair 0x3803/0xc7c5; 5 at 1 - 4x 0x7488d5da, 1x AFeng). Overlap with run-120 paid tokens: 0 - the ...7777 churn set turned over COMPLETELY again - eighteenth straight run with 0 churn overlap (runs 104-121 also 0). ZERO new rotations - the 27-wallet machine set had 0 txs this run (no buys, no sells, no approvals from any of the 27; verified overlap with active wallets = empty). The named-rotation streak ENDED run 104 (runs 97-103); run 121 has 0, eighteenth straight quiet run. No anomaly to report under the fast-path amendment (no new machine token, no name/symbol appearing, no size anomaly among machine buys, no free-mint path; max single churn buy 0.0001 BNB - pure micro churn; the one ...ffff token also appeared in run 120 and 0x7488's non-7777 suffixes are its established pattern; AFeng sale-calls 0.5/0 BNB are the known dividend-tracker shape, not machine buys). Trigger >25% NOT met by any token (max 3 wallets = 5.5%). No preview, no execution. Seatbelt 1e9c STALLED at 26: 0 wallets this run (0 buys, 0 sells) - sell-wallet union run101+run102 = 26/27, runs 103-121 add 0 - did NOT reach 27. NOT a new rotation; watch run 122 the same way. Deployments: ZERO - eighteenth straight run without deployments (run 104: 0, run 105: 0, run 106: 0, run 107: 0, run 108: 0, run 109: 0, run 110: 0, run 111: 0, run 112: 0, run 113: 0, run 114: 0, run 115: 0, run 116: 0, run 117: 0, run 118: 0, run 119: 0, run 120: 0, run 121: 0; runs 97-103 had 25/72/64/32/35/70/68) - verified from raw receipts contractAddress fields, not the parsed JSON. Inbound list for run 121 = run120 list (1734) + 0 deployments + 0 new rotation tokens (total 1734, unchanged). 0xc7c5... 34 txs; 0x3803... 33 txs; 0xad94... 30 txs; 0x3628... 15 txs; 0xa0c1... 15 txs; 0x7488d5da... 11 txs; 0xbf00... 3 txs; 0x355e... 1 tx. 2 plain BNB transfers this run (0x7407998475: 0xc7c5 -> 0x7f51d464... 0.00200672 BNB, the USUAL recipient; 0x376f84322e: future1001.ai -> 0xebcc3943... 0.88 BNB, NEW recipient; runs 113: 2, run 114: 1, run 115: 0, run 116: 0, run 117: 2, run 118: 1, run 119: 1, run 120: 0, run 121: 2). Selectors (sent pass, 142 txs): 47 approvals (0x095ea7b3) + 35 PCS buys (0xb6f9de95) + 34 PCS sells (0x791ac947) + 22 aggregator (0x39ecce49) + 2 sale-calls (0x4d819a2a) + 2 empty-input. NO new selectors. NO contract creations, NO transfers (0xa9059cbb). Nonzero-value txs 49, total 1.38436958 BNB, max 0.88 BNB (future1001.ai plain transfer; churn micro total only ~0.0021 BNB PCS buys). Most active wallets: 0xc7c5faa2 34, 0x38031ca8 33, 0xad94ee77 30, 0x3628764a 15, 0xa0c1e94f 15, 0x7488d5da 11, 0xbf004bff 3, 0x355ea9e5 1. 0 NULL receipts this run. 0 status-0 txs. Inbound leg (amendment 12:02 WIB): Ankr getLogs address-filtered per contract, 1734 contracts, 0 hits (0 inbound-only), 10930 logs, window 132373871-132381804. 35 slices of ~50 contracts in 6 parallel rounds (detached via setsid/nohup; rounds ~3-4 min each). 0 in-slice failures this run (fourth clean run in a row; runs 118, 119, 120, 121 all 0) - NO retry needed, window FULLY CLOSED in-run, no retry deferred to run 122. 8 truncated contracts, all topic-filtered to 0 logs (0x1de4... sale AFeng, 0x55d398... USDT, 0x6288..., 0x636fdfa9... tracker -> 0 logs = tracker pattern did not repeat, 0x63de... AGC, 0x7857..., 0x7e2d..., 0x3dca...). Pair retry 8/8 FAILED this run (all eight pairs: a6e6/887c/2bfb/c459/43c8/cfdb/0cf8/e68b - token0()/token1() all 'all endpoints failed' via fast_rpc race, OSError, in run121-pair-retry.py) - unverified, not absence; 39th consecutive run for a6e6/887c/2bfb/c459, 34th for 43c8, 33rd for cfdb/0cf8/e68b; retry run 122. fast_rpc race outage TOTAL during the pair retry again - but the receipts batch pass worked fine earlier in the same run, so the outage is time-varying, not permanent. A failed race read is UNVERIFIED, never absence - retry, don't conclude. Pointer-discovery (amendment 19:10): 0 contracts processed - no new mint contracts this run (0 mint logs; future1001.ai produced none) and the backfill queue is empty (bridge 115 contracts, 0 not_evaluated); bridge unchanged. CHAT REPORT this run: NONE - no new mints, no Free Bacot signal, no anomaly, no auto-mint trigger, no guard block. No preview/mint/sign/login/purchase by this job."
}

s["paid_trend_run121"] = ("21 tokens paid-bought; max 3 wallets/token (10 at 3, all churn trio 0x3803/0xad94/0xc7c5; "
 "6 at 2 - 5 pair 0x3628/0xa0c1 + 1 trio pair 0x3803/0xc7c5; 5 at 1 - 4x 0x7488d5da, 1x AFeng); overlap vs run 120: 0 (eighteenth straight complete turnover); "
 "future1001.ai back with 1 tx - plain 0.88 BNB transfer to NEW recipient 0xebcc3943..., 0 logs, NOT a mint; AFeng 3 txs (2 sale-calls 0x4d819a2a to 0x1de4... total 0.5 BNB, 0 mint logs - tracker pattern did NOT repeat; 1 approval); 0x81c3d1b4 quiet again (0 txs, after run-119 activity); "
 "total nonzero value 1.38436958 BNB across 49 txs, max single 0.88 BNB (future1001.ai plain transfer; churn micro total only ~0.0021 BNB PCS buys); "
 "2 plain BNB transfers this run (0xc7c5 -> usual 0x7f51d464... 0.00200672 BNB; future1001.ai -> new 0xebcc3943... 0.88 BNB); "
 "no token >=12 wallets, no signal, no trigger.")

s["inbound_log_leg_run121"] = ("Ankr getLogs address-filtered, 1734 contracts, 10930 logs, 0 hits, 0 inbound-only, "
 "window 132373871-132381804; 0 in-slice failures (fourth clean run in a row; runs 118, 119, 120, 121 all 0) - NO retry needed, window fully closed; "
 "8 truncated contracts topic-filtered (all to 0 logs, incl. tracker 0x636fdfa9 -> 0).")

n = s.get("next_run_note", "")
repls = [
 ("Next run sent-tx window starts from block 132373871. RETRY run 121:",
  "Next run sent-tx window starts from block 132381805. RETRY run 122:"),
 ("38 consecutive runs", "39 consecutive runs"),
 ("(unreadable run 88-120, 33 consecutive", "(unreadable run 88-121, 34 consecutive"),
 ("(token0/token1 unreadable run 89-120, 32 consecutive", "(token0/token1 unreadable run 89-121, 33 consecutive"),
 ("0 wallets runs 103-120", "0 wallets runs 103-121"),
 ("0 wallets runs 91-120, 30th quiet run", "0 wallets runs 91-121, 31st quiet run"),
 ("0 wallets runs 90-120, 31st quiet run", "0 wallets runs 90-121, 32nd quiet run"),
]
for old, new in repls:
    if old in n:
        n = n.replace(old, new, 1)
        print(f"replaced: {old[:60]}...")
    else:
        print(f"NOT FOUND (skipped): {old[:80]}")
n = ("(Run 121: inbound list = run120 list (1734) + 0 deployments + 0 new rotation tokens; window fully closed "
     "132373871-132381804, 0 hits, 0 in-slice failures (fourth clean run in a row - no retry needed; runs 118, 119, 120, 121 all 0); "
     "1e9c still STALLED 26/27, 1153 STALLED 26, 79cd STALLED 20; future1001.ai back with 1 tx (plain 0.88 BNB transfer to NEW recipient 0xebcc3943..., 0 logs, NOT a mint); "
     "AFeng 3 txs (2 sale-calls 0.5 BNB, 0 mint logs - tracker pattern did NOT repeat, runs 114-121); "
     "0x81c3d1b4 quiet again (0 txs, after run-119 activity); "
     "paid overlap vs run 120: 0 (churn set itself turned over completely, 18th straight run); total value 1.38436958 BNB (max 0.88 BNB); "
     "2 plain BNB transfers this run (0xc7c5 -> usual 0x7f51d464...; future1001.ai -> new 0xebcc3943...).) " + n)
s["next_run_note"] = n

json.dump(s, open(STATE, "w"), indent=1)
print("state updated: last_run=121, paid_trend_run121 + inbound_log_leg_run121 added")
print("next window starts 132381805")
print("backup:", NP / "tracked-wallet-mint-scan-state.json.bak-run121-pre")
