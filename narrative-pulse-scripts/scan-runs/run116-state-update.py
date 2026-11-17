#!/usr/bin/env python3
"""Run 116 state update (read-only bookkeeping): last_run + paid_trend_run116 +
inbound_log_leg_run116. No mint-pattern event this run, so no reported_findings
entry. No preview/mint/sign/login."""
import json, shutil
from pathlib import Path

HOME = Path.home()
NP = HOME / "workspace/narrative-pulse"
STATE = NP / "tracked-wallet-mint-scan-state.json"
shutil.copy(STATE, NP / "tracked-wallet-mint-scan-state.json.bak-run116-pre")
s = json.load(open(STATE))

s["last_run"] = {
 "run": 116,
 "block_start": 132333594,
 "block_end": 132342275,
 "window_wib": "2026-11-08 12:11:44 - 2026-11-08 13:10:41 WIB (tx times); run executed ~13:05 WIB - ~13:55 WIB; sent-pass in-window txs 155, 0 mint-pattern txs (AFeng 0 txs this run - dividend-tracker pattern did NOT repeat; no sale-calls at all)",
 "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set); 55/55 first attempt, 0 failed; 6 wallets active (AFeng 0 txs this run, down from 7 active in runs 112-115).",
 "method_note": "Sent pass Ankr ankr_getTransactionsByAddress via module: 55/55 OK first attempt (155 txs), 0 failed - no same-run retry needed. Receipts via fast_rpc batch (6, ~4s pause) for 104 non-approve candidates: 104 status 1, 0 status 0, 0 NULL - no race fallbacks. Mint-pattern txs: 0 - AFeng (0xbf00...) 0 txs this run (no 0x4d819a2a sale-calls at all, first run without any AFeng activity in the recent stretch), so the dividend-tracker pattern of runs 70/75/101/102/113 did NOT repeat this run (runs 114-116: no repeat). future1001.ai (0x355e...) 0 txs this run. 0x2325... 0 txs; 0x8e96... 0 txs; 0x6ba79dcc/0x89220022/0xda91cefe 0 txs. Paid: 21 tokens; max 3 wallets/token (13 tokens at 3 wallets, ALL the same churn trio 0x3803/0xad94/0xc7c5; 5 at 2, all pair 0x3628/0xa0c1; 3 at 1 - all 0x7488). Overlap with run-115 paid tokens: 0 - the ...7777 churn set turned over COMPLETELY again - thirteenth straight run with 0 churn overlap (runs 104-116 also 0). ZERO new rotations - the 27-wallet machine set had 0 txs this run (no buys, no sells, no approvals from any of the 27). The named-rotation streak ENDED run 104 (runs 97-103); run 116 has 0, thirteenth straight quiet run. No anomaly to report under the fast-path amendment (no new token, no name/symbol appearing, no size anomaly among machine buys, no free-mint path; max single tx 0.0001 BNB - pure micro churn). Trigger >25% NOT met by any token (max 3 wallets = 5.5%). No preview, no execution. Seatbelt 1e9c STALLED at 26: 0 wallets this run (0 buys, 0 sells) - sell-wallet union run101+run102 = 26/27, runs 103-116 add 0 - did NOT reach 27. NOT a new rotation; watch run 117 the same way. Deployments: ZERO - thirteenth straight run without deployments (run 104: 0, run 105: 0, run 106: 0, run 107: 0, run 108: 0, run 109: 0, run 110: 0, run 111: 0, run 112: 0, run 113: 0, run 114: 0, run 115: 0, run 116: 0; runs 97-103 had 25/72/64/32/35/70/68) - verified from raw receipts contractAddress fields, not the parsed JSON. Inbound list for run 116 = run115 list (1734) + 0 deployments + 0 new rotation tokens (total 1734, unchanged). 0xad94... 40 txs (0.000455 BNB); 0x3803... 38 txs (0.000338 BNB); 0xc7c5... 37 txs (0.000455 BNB); 0x3628... 15 txs (0.0005 BNB); 0xa0c1... 15 txs (0.0005 BNB); 0x7488d5da... 10 txs (0.00025584 BNB). 0 plain BNB transfers this run (runs 109/112 had 1 each, run 113 had 2, run 114 had 1, run 115 had 0). Selectors (sent pass, 155 txs): 51 approvals (0x095ea7b3) + 39 PCS buys (0xb6f9de95) + 40 PCS sells (0x791ac947) + 25 aggregator (0x39ecce49). NO contract creations, NO transfers (0xa9059cbb), NO sale-calls (0x4d819a2a). Nonzero-value txs 52, total 0.00250384 BNB, max 0.0001 BNB (run 115 total was 2.12789871 BNB, max 1.75 BNB - both AFeng). Most active wallets: 0xad94ee77 40, 0x38031ca8 38, 0xc7c5faa2 37, 0x3628764a 15, 0xa0c1e94f 15, 0x7488d5da 10. 0 NULL receipts this run. 0 status-0 txs. Inbound leg (amendment 12:02 WIB): Ankr getLogs address-filtered per contract, 1734 contracts, 0 hits (0 inbound-only), 11599 logs (11599 slices + 0 retry), window 132333594-132342275. 35 slices of ~50 contracts in 6 parallel rounds (lesson runs 109/111 applied - detached via setsid/nohup; rounds ~4-6 min each). 23 in-slice failures (ALL 'Remote end closed connection without response' - down from 44 in run 115) ALL recovered same-run: retry (run116-inbound116-retry.py, detached via setsid) finished 23/23, 0 logs, 0 hits, 0 failed. 0 FAILED after retry. 8 truncated contracts, all topic-filtered to 0 logs (0x10b3..., 0x1de4... sale AFeng, 0x3dca..., 0x55d398... USDT, 0x6288..., 0x636fdfa9... tracker -> 0 logs = tracker pattern did not repeat, 0x63de... AGC, 0x7857...). Window FULLY CLOSED in-run, no retry deferred to run 117. Pair retry 8/8 FAILED this run (all eight pairs: a6e6/887c/2bfb/c459/43c8/cfdb/0cf8/e68b - token0()/token1() all 'all endpoints failed' via fast_rpc race, OSError/TimeoutError, in run116-pair-retry.py) - unverified, not absence; 34th consecutive run for a6e6/887c/2bfb/c459, 29th for 43c8, 28th for cfdb/0cf8/e68b; retry run 117. fast_rpc race outage TOTAL during the pair retry again - but the receipts batch pass worked fine earlier in the same run, so the outage is time-varying, not permanent. A failed race read is UNVERIFIED, never absence - retry, don't conclude. Pointer-discovery (amendment 19:10): 0 contracts processed - no new mint contracts this run (0 mint logs; AFeng produced none) and the backfill queue is empty (bridge 115 contracts, 0 not_evaluated); bridge unchanged. CHAT REPORT this run: NONE - no new mints, no Free Bacot signal, no anomaly, no auto-mint trigger, no guard block. No preview/mint/sign/login/purchase by this job."
}

s["paid_trend_run116"] = ("21 tokens paid-bought; max 3 wallets/token (13 at 3, all churn trio 0x3803/0xad94/0xc7c5; "
 "5 at 2, all pair 0x3628/0xa0c1; 3 at 1 - all 0x7488); overlap vs run 115: 0 (thirteenth straight complete turnover); "
 "AFeng 0 txs this run (no sale-calls, tracker pattern did NOT repeat); future1001.ai 0 txs; "
 "total nonzero value 0.00250384 BNB across 52 txs, max single 0.0001 BNB (pure micro churn, vs 2.12789871 BNB / 1.75 BNB in run 115); "
 "no token >=12 wallets, no signal, no trigger.")

s["inbound_log_leg_run116"] = ("Ankr getLogs address-filtered, 1734 contracts, 11599 logs (11599 slices + 0 retry), 0 hits, 0 inbound-only, "
 "window 132333594-132342275; 23 in-slice failures (all 'Remote end closed connection without response' - down from 44 in run 115) "
 "recovered same-run: retry 23/23 via run116-inbound116-retry.py (0 logs, 0 hits, 0 failed); "
 "8 truncated contracts topic-filtered (all to 0 logs, incl. tracker 0x636fdfa9 -> 0); window fully closed.")

n = s.get("next_run_note", "")
repls = [
 ("Next run sent-tx window starts from block 132333594. RETRY run 116:",
  "Next run sent-tx window starts from block 132342276. RETRY run 117:"),
 ("33 consecutive runs", "34 consecutive runs"),
 ("(unreadable run 88-115, 28 consecutive", "(unreadable run 88-116, 29 consecutive"),
 ("(token0/token1 unreadable run 89-115, 27 consecutive", "(token0/token1 unreadable run 89-116, 28 consecutive"),
 ("0 wallets runs 103-115", "0 wallets runs 103-116"),
 ("0 wallets runs 91-115, 25th quiet run", "0 wallets runs 91-116, 26th quiet run"),
 ("0 wallets runs 90-115, 26th quiet run", "0 wallets runs 90-116, 27th quiet run"),
]
for old, new in repls:
    if old in n:
        n = n.replace(old, new, 1)
        print(f"replaced: {old[:60]}...")
    else:
        print(f"NOT FOUND (skipped): {old[:80]}")
n = ("(Run 116: inbound list = run115 list (1734) + 0 deployments + 0 new rotation tokens; window fully closed "
     "132333594-132342275, 0 hits, 23 in-chunk failures (Ankr 'Remote end closed connection' spike, down from 44) recovered same-run 23/23 via run116-inbound116-retry.py (0 logs, 0 hits, 0 failed); "
     "1e9c still STALLED 26/27, 1153 STALLED 26, 79cd STALLED 20; AFeng 0 txs this run (no sale-calls, tracker pattern did NOT repeat); "
     "paid overlap vs run 115: 0 (churn set itself turned over completely, 13th straight run); total value collapsed to 0.00250384 BNB (max 0.0001 BNB) vs 2.12789871 BNB run 115 - AFeng absent.) " + n)
s["next_run_note"] = n

json.dump(s, open(STATE, "w"), indent=1)
print("state updated: last_run=116, paid_trend_run116 + inbound_log_leg_run116 added")
print("next window starts 132342276")
print("backup:", NP / "tracked-wallet-mint-scan-state.json.bak-run116-pre")
