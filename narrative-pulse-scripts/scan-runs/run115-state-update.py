#!/usr/bin/env python3
"""Run 115 state update (read-only bookkeeping): last_run + paid_trend_run115 +
inbound_log_leg_run115. No mint-pattern event this run, so no reported_findings
entry. No preview/mint/sign/login."""
import json, shutil
from pathlib import Path

HOME = Path.home()
NP = HOME / "workspace/narrative-pulse"
STATE = NP / "tracked-wallet-mint-scan-state.json"
shutil.copy(STATE, NP / "tracked-wallet-mint-scan-state.json.bak-run115-pre")
s = json.load(open(STATE))

s["last_run"] = {
 "run": 115,
 "block_start": 132325599,
 "block_end": 132333593,
 "window_wib": "2026-11-08 11:08:10 - 2026-11-08 12:05:32 WIB (tx times); run executed ~12:05 WIB - ~13:05 WIB; sent-pass in-window txs 167, 0 mint-pattern txs (AFeng sale-calls produced 0 mint logs - dividend-tracker pattern did NOT repeat this run)",
 "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set); 55/55 first attempt, 0 failed; 7 wallets active (same 7 as runs 112/113/114).",
 "method_note": "Sent pass Ankr ankr_getTransactionsByAddress via module: 55/55 OK first attempt (167 txs), 0 failed - no same-run retry needed. Receipts via fast_rpc batch (6, ~4s pause) for 111 non-approve candidates: 111 status 1, 0 status 0, 0 NULL - no race fallbacks. Mint-pattern txs: 0 - AFeng (0xbf00...) 5 sale-calls 0x4d819a2a to 0x1de4... (1.75 BNB 11:16:56 WIB hash 0xf557ea8e185d95a12ae4bf3bbd201cc4792322f0e1c6c9d085dea84f2242ab5c, 0.375 BNB 11:38:30 WIB hash 0x5cfb3684fee6, 0 BNB x3) produced 0 mint logs, so the dividend-tracker pattern of runs 70/75/101/102/113 did NOT repeat this run (run 113 repeated after a one-run gap; runs 114-115: no repeat). AFeng 8 txs total: 5 sale-calls (2.125 BNB) + 3 approvals (2 to 0x78573ab46e, 1 to 0xa63652f5a4). future1001.ai (0x355e...) 0 txs this run. Paid: 25 tokens; max 3 wallets/token (12 tokens at 3 wallets, ALL the same churn trio 0x3803/0xad94/0xc7c5; 7 at 2, all pair 0x3628/0xa0c1; 6 at 1 - 4x 0x7488, 2x AFeng). Overlap with run-114 paid tokens: 0 - the ...7777 churn set turned over COMPLETELY again - twelfth straight run with 0 churn overlap (runs 104-115 also 0). ZERO new rotations - the 27-wallet machine set had 0 txs this run (no buys, no sells, no approvals from any of the 27). The named-rotation streak ENDED run 104 (runs 97-103); run 115 has 0, twelfth straight quiet run. No anomaly to report under the fast-path amendment (no new token, no name/symbol appearing, no size anomaly among machine buys, no free-mint path; the 1.75 BNB max single tx is AFeng's sale-call, not a machine buy). Trigger >25% NOT met by any token (max 3 wallets = 5.5%). No preview, no execution. Seatbelt 1e9c STALLED at 26: 0 wallets this run (0 buys, 0 sells) - sell-wallet union run101+run102 = 26/27, runs 103-115 add 0 - did NOT reach 27. NOT a new rotation; watch run 116 the same way. Deployments: ZERO - twelfth straight run without deployments (run 104: 0, run 105: 0, run 106: 0, run 107: 0, run 108: 0, run 109: 0, run 110: 0, run 111: 0, run 112: 0, run 113: 0, run 114: 0, run 115: 0; runs 97-103 had 25/72/64/32/35/70/68) - verified from raw receipts contractAddress fields, not the parsed JSON. Inbound list for run 115 = run114 list (1734) + 0 deployments + 0 new rotation tokens (total 1734, unchanged). 0x2325... 0 txs this run; 0x8e96... 0 txs; 0x6ba79dcc/0x89220022/0xda91cefe 0 txs. 0xad94... 36 txs (0.00042 BNB); 0xc7c5... 34 txs (0.00042 BNB); 0x3803... 35 txs (0.000312 BNB); 0xa0c1... 21 txs (0.0007 BNB); 0x3628... 21 txs (0.0007 BNB); 0x7488d5da... 12 txs (0.00034671 BNB); AFeng 0xbf00... 8 txs (2.125 BNB). 0 plain BNB transfers this run (runs 109/112 had 1 each, run 113 had 2, run 114 had 1). Selectors (sent pass, 167 txs): 56 approvals (0x095ea7b3) + 42 PCS buys (0xb6f9de95) + 41 PCS sells (0x791ac947) + 23 aggregator (0x39ecce49) + 5 sale-calls (0x4d819a2a). NO contract creations, NO transfers (0xa9059cbb). Nonzero-value txs 56, total 2.12789871 BNB (2.125 of it AFeng; micro churn only ~0.0029 BNB), max 1.75 BNB (AFeng sale-call 11:16:56 WIB; run 114 total was 0.5798468 BNB, max 0.5 BNB). Most active wallets: 0xad94ee77 36, 0x38031ca8 35, 0xc7c5faa2 34, 0x3628764a 21, 0xa0c1e94f 21, 0x7488d5da 12, 0xbf004bff 8. 0 NULL receipts this run. 0 status-0 txs. Inbound leg (amendment 12:02 WIB): Ankr getLogs address-filtered per contract, 1734 contracts, 0 hits (0 inbound-only), 12316 logs (12225 slices + 39 retry1 + 52 retry2), window 132325599-132333593. 35 slices of ~50 contracts in 6 parallel rounds (lesson runs 109/111 applied - detached via setsid/nohup; round 1 took ~9 min, others ~3.5-11 min). NOTE: first driver launch failed instantly - driver called run115-inbound114.py which did not exist (sed had produced run115-inbound115.py); fixed by copying to the called name and relaunching. 44 in-slice failures (ALL 'Remote end closed connection without response' - up from 35 in run 113/114) ALL recovered same-run: retry1 (run115-inbound115-retry.py) covered 21/44 then the process died silently at [21] when its exec session was lost - log-verified 39 logs, 0 hits; retry2 (run115-inbound115-retry2.py, remaining 23, detached via setsid) finished 23/23, 52 logs, 0 hits, 0 failed (one contract needed a 2nd attempt, recovered). 0 FAILED after retry. 9 truncated contracts, all topic-filtered to 0 logs (0x10b3..., 0x1de4... sale AFeng, 0x3dca..., 0x55d398... USDT, 0x6288..., 0x636fdfa9... tracker -> 0 logs = tracker pattern did not repeat, 0x63de... AGC, 0x7857..., 0x7e2d...). Window FULLY CLOSED in-run, no retry deferred to run 116. Pair retry 8/8 FAILED this run (all eight pairs: a6e6/887c/2bfb/c459/43c8/cfdb/0cf8/e68b - token0()/token1() all 'all endpoints failed' via fast_rpc race, OSError/TimeoutError, in run115-pair-retry.py) - unverified, not absence; 33rd consecutive run for a6e6/887c/2bfb/c459, 28th for 43c8, 27th for cfdb/0cf8/e68b; retry run 116. fast_rpc race outage TOTAL during the pair retry again - but the receipts batch pass worked fine earlier in the same run, so the outage is time-varying, not permanent. A failed race read is UNVERIFIED, never absence - retry, don't conclude. Pointer-discovery (amendment 19:10): 0 contracts processed - no new mint contracts this run (0 mint logs; AFeng sale-calls produced none) and the backfill queue is empty (bridge 115 contracts, 0 not_evaluated); bridge unchanged. CHAT REPORT this run: NONE - no new mints, no Free Bacot signal, no anomaly, no auto-mint trigger, no guard block. No preview/mint/sign/login/purchase by this job. NOTE: baw session died prematurely a 2nd time ~12:39 WIB (MEMORY.md update during this run) and was re-logged-in ~12:54 WIB (QR d01be7e6, CONNECTED, verified live after scan) - irrelevant to this run (no trigger met, no execution attempted), but any future auto-mint >25% execution needs a live baw session first."
}

s["paid_trend_run115"] = ("25 tokens paid-bought; max 3 wallets/token (12 at 3, all churn trio 0x3803/0xad94/0xc7c5; "
 "7 at 2, all pair 0x3628/0xa0c1; 6 at 1 - 4x 0x7488, 2x AFeng); overlap vs run 114: 0 (twelfth straight complete turnover); "
 "AFeng 8 txs (5 sale-calls to 0x1de4..., 2.125 BNB, 0 mint logs - tracker pattern did NOT repeat); "
 "total nonzero value 2.12789871 BNB across 56 txs (2.125 AFeng), max single 1.75 BNB (AFeng sale-call); "
 "no token >=12 wallets, no signal, no trigger.")

s["inbound_log_leg_run115"] = ("Ankr getLogs address-filtered, 1734 contracts, 12316 logs (12225 slices + 39 retry1 + 52 retry2), 0 hits, 0 inbound-only, "
 "window 132325599-132333593; 44 in-slice failures (all 'Remote end closed connection without response' - up from 35 in run 114) "
 "recovered same-run: retry1 21/44 (log-verified, process died at [21] when exec session lost, JSON never written) + retry2 23/23 via run115-inbound115-retry2.py (52 logs, 0 hits, 0 failed); "
 "9 truncated contracts topic-filtered (all to 0 logs, incl. tracker 0x636fdfa9 -> 0); window fully closed.")

n = s.get("next_run_note", "")
repls = [
 ("Next run sent-tx window starts from block 132325599. RETRY run 115:",
  "Next run sent-tx window starts from block 132333594. RETRY run 116:"),
 ("32 consecutive runs", "33 consecutive runs"),
 ("(unreadable run 88-114, 27 consecutive", "(unreadable run 88-115, 28 consecutive"),
 ("(token0/token1 unreadable run 89-114, 26 consecutive", "(token0/token1 unreadable run 89-115, 27 consecutive"),
 ("0 wallets runs 103-114", "0 wallets runs 103-115"),
 ("0 wallets runs 91-114, 24th quiet run", "0 wallets runs 91-115, 25th quiet run"),
 ("0 wallets runs 90-114, 25th quiet run", "0 wallets runs 90-115, 26th quiet run"),
]
for old, new in repls:
    if old in n:
        n = n.replace(old, new, 1)
        print(f"replaced: {old[:60]}...")
    else:
        print(f"NOT FOUND (skipped): {old[:80]}")
n = ("(Run 115: inbound list = run114 list (1734) + 0 deployments + 0 new rotation tokens; window fully closed "
     "132325599-132333593, 0 hits, 44 in-chunk failures (Ankr 'Remote end closed connection' spike, up from 35) recovered same-run 44/44 via run115-inbound115-retry.py (21, log-verified, process died at [21]) + run115-inbound115-retry2.py (23/23); "
     "first driver launch failed instantly (driver called run115-inbound114.py, file did not exist - fixed by copy + relaunch); "
     "1e9c still STALLED 26/27, 1153 STALLED 26, 79cd STALLED 20; AFeng 5 sale-calls (2.125 BNB, max 1.75), 0 mint logs - dividend-tracker pattern did NOT repeat; "
     "paid overlap vs run 114: 0 (churn set itself turned over completely, 12th straight run); baw session died prematurely 12:39 WIB, re-logged-in 12:54 WIB (QR d01be7e6).) " + n)
s["next_run_note"] = n

json.dump(s, open(STATE, "w"), indent=1)
print("state updated: last_run=115, paid_trend_run115 + inbound_log_leg_run115 added")
print("next window starts 132333594")
print("backup:", NP / "tracked-wallet-mint-scan-state.json.bak-run115-pre")
