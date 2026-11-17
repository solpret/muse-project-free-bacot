#!/usr/bin/env python3
"""Run 130 state update (read-only bookkeeping): last_run + paid_trend_run130 +
inbound_log_leg_run130. No new mints this run, so no new reported_findings
entries. No preview/mint/sign/login."""
import json, shutil
from pathlib import Path

HOME = Path.home()
NP = HOME / "workspace/narrative-pulse"
STATE = NP / "tracked-wallet-mint-scan-state.json"
shutil.copy(STATE, NP / "tracked-wallet-mint-scan-state.json.bak-run130-pre")
s = json.load(open(STATE))

s["last_run"] = {
 "run": 130,
 "block_start": 132445937,
 "block_end": 132456148,
 "window_wib": "2026-11-09 02:09:00 - 03:25:05 WIB (tx times); run executed ~03:05 WIB - ~04:25 WIB; sent-pass in-window txs 211, 0 mint-pattern txs",
 "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set); 9 FAILED first attempt (Ankr 'Remote end closed connection' / timeouts during the VM network outage); 8 recovered via run130-sent-retry.py (ALL 0 in-window txs); 1 STILL FAILED: 0xaa49e7fec503664a39598645c7a3fbfa0374380d - its window 132445937-132456148 is UNVERIFIED, must be re-read by run 131 (see next_run_note). 6 wallets active (0xc7c5faa2 49, 0xad94ee77 48, 0x38031ca8 48, 0x3628764a 24, 0xa0c1e94f 22, 0x7488d5da 20); AFeng 0 txs; future1001.ai 0 txs; 0x2325f175 0 txs; 0x89220022 0 txs; 0x6ba79dcc 0 txs; 0x81c3d1b4 0 txs (quiet again).",
 "method_note": "OUTAGE RUN: VM outbound network TOTALLY DOWN ~20:06-20:23 UTC (03:06-03:23 WIB) - google.com, rpc.ankr.com, ALL bsc-dataseed endpoints unreachable (curl 000 / timeouts). First sent pass launched 03:06 WIB failed 9/9 wallets, KILLED after 9 failures (pid 5658 confirmed stopped); network recovered ~20:23 UTC (google 200 in 2.4s); sent pass relaunched, 46/55 OK first attempt, 9 failed, 8/9 recovered via retry (0 in-window each). Sent pass Ankr ankr_getTransactionsByAddress via module: 211 in-window txs total, max_block 132456148. Receipts via fast_rpc batch (6, ~4s pause) for 142 non-approve candidates: 130 status 1, 0 status 0, 12 NULL after receipts-retry (only 1 of 13 recovered - fast_rpc all-endpoints TimeoutError persisted all run; receipts-retry re-parse bug inflated nulls to 81 by including 69 approve txs - FIXED by run130-receipts-fix.py back to the correct 142-candidate basis). 0 mint logs in any verified receipt - seventh straight zero-mint run (runs 124-130; first zero-mint run since run 14 was run 124). 12 NULL receipts: 11 to PCS router 0x10ed... (buy/sell 0xb6f9de95/0x791ac947, churn pair/trio) + 1 empty-input plain BNB transfer 0xb94372b4c0 (0x3628 -> 0xc0094886..., 0.00205767 BNB) - all non-mint-pattern by selector/destination, but receipt UNVERIFIED, retry run 131. Paid: 30 tokens; max 3 wallets/token (13 at 3, ALL churn trio 0x3803/0xad94/0xc7c5, ALL ...7777; 9 at 2; 8 at 1). Overlap with run-129 paid tokens: 0 - the churn set itself turned over COMPLETELY again - twenty-seventh straight run with 0 churn overlap (runs 104-130 also 0). ZERO new rotations - the 27-wallet machine set had 0 txs this run (no buys, no sells, no approvals from any of the 27; verified overlap with active wallets = empty). The named-rotation streak ENDED run 104 (runs 97-103); run 130 has 0, twenty-seventh straight quiet run. No anomaly to report under the fast-path amendment (no new machine token, no name/symbol appearing, no size anomaly among machine buys, no free-mint path; churn trio PCS buys 31 txs total only 0.001085 BNB - pure micro churn). Trigger >25% NOT met by any token (max 3 wallets = 5.5%). No preview, no execution. Seatbelt 1e9c STALLED at 26: 0 wallets this run (0 buys, 0 sells) - sell-wallet union run101+run102 = 26/27, runs 103-130 add 0 - did NOT reach 27. NOT a new rotation; watch run 131 the same way. Deployments: ZERO - twenty-seventh straight run without deployments (run 104: 0 through run 130: 0; runs 97-103 had 25/72/64/32/35/70/68) - verified from raw receipts contractAddress fields, not the parsed JSON. Inbound list for run 130 = run129 list (1734) + 0 deployments + 0 new rotation tokens (total 1734, unchanged). 2 plain BNB transfers this run (0xb94372b4c0 0x3628 -> 0xc0094886... 0.00205767 BNB 03:10:33 WIB - receipt NULL, unverified; 0xd1065d7c43 0xc7c5 -> 0x7f51d464... 0.00205942 BNB 03:14:51 WIB - same recipient as run 128). Selectors (sent pass, 211 txs): 69 approvals (0x095ea7b3) + 52 PCS buys (0xb6f9de95) + 56 PCS sells (0x791ac947) + 32 aggregator (0x39ecce49, all 0x3803...) + 2 empty-input. NO contract creations. Nonzero-value txs 70, total 0.00761767 BNB, max 0.00205942 BNB (plain transfer 0xd1065d7c43). Most active wallets: 0xc7c5faa2 49, 0xad94ee77 48, 0x38031ca8 48, 0x3628764a 24, 0xa0c1e94f 22, 0x7488d5da 20. 12 NULL receipts this run (see above). 0 status-0 txs. Inbound leg (amendment 12:02 WIB): PARTIAL ONLY - round 0 (slices s00-s05, contracts 0-299) completed: 163 logs, 0 hits, 103 failed contracts (Ankr 'Remote end closed connection' / timeouts), 0 truncated. Driver STOPPED after round 0 by parent (each slice ~35 min under the outage; 35 slices would be ~3 hrs and collide with runs 131-133). Window NOT FULLY CLOSED in-run - RESIDUAL for run 131: slices s06-s34 (contracts 300-1733) UNRUN for window 132445937-132456148 + 103 failed contracts from round 0 (list in run130-inbound-agg.json) + sent gap 0xaa49e7fe... for the same window. Pair retry 8/8 FAILED again (all eight pairs: a6e6/887c/2bfb/c459/43c8/cfdb/0cf8/e68b - token0()/token1() all 'all endpoints failed' via fast_rpc race, TimeoutError) - unverified, not absence; 48th consecutive run for a6e6/887c/2bfb/c459, 43rd for 43c8, 42nd for cfdb/0cf8/e68b; retry run 131. fast_rpc race outage persisted the WHOLE run (receipts, receipts-retry, pair retry all failed the same way) - unlike run 129's time-varying outage, this one was total for fast_rpc from run start to run end; Ankr flapped (total outage 03:06-03:23 WIB, then flaky). A failed read is UNVERIFIED, never absence - retry, don't conclude. Pointer-discovery (amendment 19:10 WIB, cap 5/run): NO pointer run this run - bridge queue EMPTY (116 contracts: 13 verified / 103 no-pointer / 0 queued) and 0 new contracts this run (0 deployments, 0 new rotation tokens), so nothing to discover. Bridge unchanged. CHAT REPORT this run: NONE (silent) - 0 new mints, no Free Bacot signal, no anomaly, no auto-mint trigger, no guard block. No preview/mint/sign/login/purchase by this job."
}

s["paid_trend_run130"] = ("30 tokens paid-bought; max 3 wallets/token (13 at 3, all churn trio 0x3803/0xad94/0xc7c5, all ...7777; "
 "9 at 2; 8 at 1); overlap vs run 129: 0 (churn set itself turned over completely, 27th straight run); "
 "0x81c3d1b4 quiet again (0 txs); "
 "AFeng 0 txs; future1001.ai 0 txs; 0x2325 0 txs; 0x89220022 quiet (0 txs); 0x6ba79dcc 0 txs; "
 "sent pass 46/55 first attempt (9 Ankr failures during VM network outage, 8 recovered via retry, 1 residual 0xaa49e7fe...); "
 "total nonzero value 0.00761767 BNB across 70 txs, max single 0.00205942 BNB (plain transfer); "
 "2 plain BNB transfers this run; 0 deployments (27th straight run); 0 machine-set activity (27th straight quiet run).")

s["inbound_log_leg_run130"] = ("Ankr getLogs address-filtered, PARTIAL: round 0 only (slices s00-s05, contracts 0-299 of 1734), 163 logs, 0 hits, 0 inbound-only, "
 "103 failed contracts (Ankr 'Remote end closed connection' / timeouts), 0 truncated; driver stopped after round 0 (each slice ~35 min under the outage); "
 "RESIDUAL for run 131: slices s06-s34 (contracts 300-1733) unrun + 103 failed contracts, window 132445937-132456148 NOT fully closed.")

n = s.get("next_run_note", "")
repls = [
 ("Next run sent-tx window starts from block 132437955. RETRY run 129:",
  "Next run sent-tx window starts from block 132456149. RETRY run 131:"),
 ("47 consecutive runs", "48 consecutive runs"),
 ("(unreadable run 88-129, 42 consecutive", "(unreadable run 88-130, 43 consecutive"),
 ("(token0/token1 unreadable run 89-129, 41 consecutive", "(token0/token1 unreadable run 89-130, 42 consecutive"),
 ("0 wallets runs 103-129", "0 wallets runs 103-130"),
 ("0 wallets runs 91-129, 39th quiet run", "0 wallets runs 91-130, 40th quiet run"),
 ("0 wallets runs 90-129, 40th quiet run", "0 wallets runs 90-130, 41st quiet run"),
]
for old, new in repls:
    if old in n:
        n = n.replace(old, new, 1)
        print(f"replaced: {old[:60]}...")
    else:
        print(f"NOT FOUND (skipped): {old[:80]}")
n = ("(Run 130: OUTAGE RUN - VM outbound network totally down ~03:06-03:23 WIB (google/Ankr/dataseed all unreachable), then Ankr flaky + fast_rpc total outage all run. "
     "RESIDUALS FOR RUN 131 (must-do): (1) re-read sent txs for 0xaa49e7fec503664a39598645c7a3fbfa0374380d, window 132445937-132456148 (failed main pass + 2 retry attempts); "
     "(2) retry the 12 NULL receipts (list in run130-receipts.json; 11 PCS router + 1 plain transfer 0xb94372b4c0); "
     "(3) inbound leg window 132445937-132456148 NOT closed: run slices s06-s34 (contracts 300-1733) + retry the 103 failed contracts from round 0 (run130-inbound-agg.json). "
     "Run 130 proper: inbound round 0 only (300 contracts, 163 logs, 0 hits, 103 failed, 0 truncated); sent pass 211 txs (46/55 first attempt, 8/9 recovered via retry); receipts 142 candidates, 130 status 1, 0 status 0, 12 NULL, 0 mint logs (seventh straight zero-mint run, runs 124-130); "
     "NO pointer run - bridge queue EMPTY (116: 13 verified / 103 no-pointer / 0 queued), 0 new contracts; "
     "1e9c still STALLED 26/27, 1153 STALLED 26, 79cd STALLED 20; 0x81c3d1b4 quiet again (0 txs); NO sale-calls 0x4d819a2a this run (AFeng 0 txs; 0x3803 none either); 0x2325 0 txs; 0x89220022 quiet (0 txs); "
     "AFeng 0 txs; 0 sale-calls from AFeng this run (tracker pattern did NOT repeat, runs 114-130); future1001.ai 0 txs; "
     "paid overlap vs run 129: 0 (churn set itself turned over completely, 27th straight run); total nonzero value 0.00761767 BNB (max 0.00205942 BNB plain transfer); "
     "2 plain BNB transfers this run (0xb94372b4c0 receipt NULL - unverified; 0xd1065d7c43 to 0x7f51d464... same recipient as run 128); 0 deployments (27th straight run).) " + n)
s["next_run_note"] = n

json.dump(s, open(STATE, "w"), indent=1)
print("state updated: last_run=130, paid_trend_run130 + inbound_log_leg_run130 added, 0 new reported_findings entries")
print("next window starts 132456149")
print("backup:", NP / "tracked-wallet-mint-scan-state.json.bak-run130-pre")
