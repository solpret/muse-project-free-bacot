#!/usr/bin/env python3
"""Run 122 state update (read-only bookkeeping): last_run + paid_trend_run122 +
inbound_log_leg_run122. No mint-pattern event this run, so no reported_findings
entry. No preview/mint/sign/login."""
import json, shutil
from pathlib import Path

HOME = Path.home()
NP = HOME / "workspace/narrative-pulse"
STATE = NP / "tracked-wallet-mint-scan-state.json"
shutil.copy(STATE, NP / "tracked-wallet-mint-scan-state.json.bak-run122-pre")
s = json.load(open(STATE))

s["last_run"] = {
 "run": 122,
 "block_start": 132381805,
 "block_end": 132389824,
 "window_wib": "2026-11-08 18:08:33 - 2026-11-08 19:07:28 WIB (tx times); run executed ~19:05 WIB - ~19:50 WIB; sent-pass in-window txs 180, 0 mint-pattern txs (AFeng 5 txs - 3 sale-calls 0x4d819a2a to 0x1de4... total 0.25 BNB, 0 mint logs - dividend-tracker pattern did NOT repeat; runs 114-122: no repeat; 0x89220022 NEW shape: 19 ERC20 transfers 0xa9059cbb + 1 plain BNB transfer, all to single recipient 0xa4682b0815..., 0 mint logs, NOT a mint)",
 "wallets_checked": "54/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set); 1 FAILED first attempt: 0x6ba79dcc (feed) 'Remote end closed connection without response' - its activity this window is UNVERIFIED, not absent; retry run 123. 9 wallets active (0x89220022 back with 20 txs after 0 in run 121; future1001.ai 0 txs; 0x81c3d1b4 quiet again with 0 txs).",
 "method_note": "Sent pass Ankr ankr_getTransactionsByAddress via module: 54/55 OK first attempt (180 txs), 1 failed (0x6ba79dcc, Ankr remote-end closed) - no same-run retry, retry run 123. Receipts via fast_rpc batch (6, ~4s pause) for 127 non-approve candidates: 127 status 1, 0 status 0, 0 NULL - no race fallbacks. Mint-pattern txs: 0 - AFeng (0xbf00...) 5 txs: 3 sale-calls 0x4d819a2a to 0x1de4... (0.25 BNB 19:05:59 WIB, 0 BNB 18:59:04 WIB, 0 BNB 18:58:23 WIB) + 2 approvals, 0 mint logs, so the dividend-tracker pattern of runs 70/75/101/102/113 did NOT repeat this run (runs 114-122: no repeat). 0x89220022 (feed) NEW shape: 19 ERC20 transfers (selector 0xa9059cbb, NEW this run) + 1 plain BNB transfer 0.0000089188 BNB, ALL to single recipient 0xa4682b08159a26938e06869739b1025b2bd23d50 (18:43-19:01 WIB), 0 mint logs - outbound token sweep/distribution, NOT a mint, no follow-up action. 0x2325... 1 tx (aggregator 0x27772d13, 0.1 BNB, 14 logs, no mint). future1001.ai 0 txs; 0x81c3d1b4 0 txs. Paid: 24 tokens; max 3 wallets/token (12 tokens at 3 wallets, ALL the same churn trio 0x3803/0xad94/0xc7c5, all ...7777; 6 at 2 - pair 0x3628/0xa0c1; 6 at 1 - 4x 0x7488d5da, 1x 0x2325, 1x AFeng). Overlap with run-121 paid tokens: 0 - the ...7777 churn set turned over COMPLETELY again - nineteenth straight run with 0 churn overlap (runs 104-122 also 0). ZERO new rotations - the 27-wallet machine set had 0 txs this run (no buys, no sells, no approvals from any of the 27; verified overlap with active wallets = empty). The named-rotation streak ENDED run 104 (runs 97-103); run 122 has 0, nineteenth straight quiet run. No anomaly to report under the fast-path amendment (no new machine token, no name/symbol appearing, no size anomaly among machine buys, no free-mint path; max single churn buy 0.0001 BNB - pure micro churn; AFeng sale-calls 0.25/0/0 BNB are the known dividend-tracker shape, not machine buys; 0x89220022 transfers are outbound ERC20, not machine buys). Trigger >25% NOT met by any token (max 3 wallets = 5.5%). No preview, no execution. Seatbelt 1e9c STALLED at 26: 0 wallets this run (0 buys, 0 sells) - sell-wallet union run101+run102 = 26/27, runs 103-122 add 0 - did NOT reach 27. NOT a new rotation; watch run 123 the same way. Deployments: ZERO - nineteenth straight run without deployments (run 104: 0, run 105: 0, run 106: 0, run 107: 0, run 108: 0, run 109: 0, run 110: 0, run 111: 0, run 112: 0, run 113: 0, run 114: 0, run 115: 0, run 116: 0, run 117: 0, run 118: 0, run 119: 0, run 120: 0, run 121: 0, run 122: 0; runs 97-103 had 25/72/64/32/35/70/68) - verified from raw receipts contractAddress fields, not the parsed JSON. Inbound list for run 122 = run121 list (1734) + 0 deployments + 0 new rotation tokens (total 1734, unchanged). 0xad94... 37 txs; 0x3803... 35 txs; 0xc7c5... 34 txs; 0x89220022... 20 txs; 0x3628... 18 txs; 0xa0c1... 18 txs; 0x7488d5da... 12 txs; 0xbf00... 5 txs; 0x2325... 1 tx. 1 plain BNB transfer this run (0x682eea3505: 0x89220022 -> 0xa4682b0815... 0.0000089188 BNB, 0 logs, NOT a mint; runs 113: 2, run 114: 1, run 115: 0, run 116: 0, run 117: 2, run 118: 1, run 119: 1, run 120: 0, run 121: 2, run 122: 1). Selectors (sent pass, 180 txs): 53 approvals (0x095ea7b3) + 40 PCS buys (0xb6f9de95) + 40 PCS sells (0x791ac947) + 23 aggregator (0x39ecce49) + 19 ERC20 transfers (0xa9059cbb, NEW selector this run - all 0x89220022) + 3 sale-calls (0x4d819a2a, AFeng) + 1 aggregator (0x27772d13, 0x2325) + 1 empty-input. NO contract creations. Nonzero-value txs 55, total 0.35269969 BNB, max 0.25 BNB (AFeng sale-call; churn micro total only ~0.0021 BNB PCS buys). Most active wallets: 0xad94ee77 37, 0x38031ca8 35, 0xc7c5faa2 34, 0x89220022 20, 0x3628764a 18, 0xa0c1e94f 18, 0x7488d5da 12, 0xbf004bff 5, 0x2325f175 1. 0 NULL receipts this run. 0 status-0 txs. Inbound leg (amendment 12:02 WIB): Ankr getLogs address-filtered per contract, 1734 contracts, 0 hits (0 inbound-only), 10786 logs, window 132381805-132389824. 35 slices of ~50 contracts in 6 parallel rounds (detached via nohup; rounds ~5-8 min each, Ankr slower this run). 9 in-slice failures (Ankr 'Remote end closed connection without response'): 0x53ba... (tracker), 0x6c90..., 0x7807..., 0x9281..., 0xaa69..., 0xb86c..., 0xc3ba..., 0xdb06..., 0xe206... - those 9 contracts UNVERIFIED for this window, NOT 0 inbound; retry run 123 per the amendment (no in-run retry). Window NOT fully closed in-run (first unclosed run since run 117). 9 truncated contracts, all topic-filtered to 0 logs (0x1de4... sale AFeng, 0x55d398... USDT, 0x6288..., 0x636fdfa9... tracker -> 0 logs = tracker pattern did not repeat, 0x63de... AGC, 0x7857..., 0x7e2d..., 0x3dca..., 0x10b3...). Pair retry 8/8 FAILED this run (all eight pairs: a6e6/887c/2bfb/c459/43c8/cfdb/0cf8/e68b - token0()/token1() all 'all endpoints failed' via fast_rpc race, TimeoutError/OSError, in run122-pair-retry.py) - unverified, not absence; 40th consecutive run for a6e6/887c/2bfb/c459, 35th for 43c8, 34th for cfdb/0cf8/e68b; retry run 123. fast_rpc race outage TOTAL during the pair retry again - but the receipts batch pass worked fine earlier in the same run, so the outage is time-varying, not permanent. A failed race read is UNVERIFIED, never absence - retry, don't conclude. Pointer-discovery (amendment 19:10): 0 contracts processed - no new mint contracts this run (0 mint logs) and the backfill queue is empty (bridge 115 contracts, 0 not_evaluated); bridge unchanged. CHAT REPORT this run: NONE - no new mints, no Free Bacot signal, no anomaly, no auto-mint trigger, no guard block. No preview/mint/sign/login/purchase by this job."
}

s["paid_trend_run122"] = ("24 tokens paid-bought; max 3 wallets/token (12 at 3, all churn trio 0x3803/0xad94/0xc7c5; "
 "6 at 2 - pair 0x3628/0xa0c1; 6 at 1 - 4x 0x7488d5da, 1x 0x2325, 1x AFeng); overlap vs run 121: 0 (nineteenth straight complete turnover); "
 "0x89220022 NEW shape: 19 ERC20 transfers (0xa9059cbb, NEW selector) + 1 plain BNB transfer, all to single recipient 0xa4682b0815..., 0 mint logs, NOT a mint; "
 "AFeng 5 txs (3 sale-calls 0x4d819a2a to 0x1de4... total 0.25 BNB, 0 mint logs - tracker pattern did NOT repeat; 2 approvals); "
 "0x2325 1 tx (aggregator 0.1 BNB, 14 logs, no mint); future1001.ai 0 txs; 0x81c3d1b4 quiet again (0 txs); "
 "sent pass 54/55 (0x6ba79dcc failed, Ankr remote-end closed - retry run 123); total nonzero value 0.35269969 BNB across 55 txs, max single 0.25 BNB (AFeng sale-call; churn micro total only ~0.0021 BNB PCS buys); "
 "1 plain BNB transfer this run (0x89220022 -> 0xa4682b0815... 0.0000089188 BNB); "
 "no token >=12 wallets, no signal, no trigger.")

s["inbound_log_leg_run122"] = ("Ankr getLogs address-filtered, 1734 contracts, 10786 logs, 0 hits, 0 inbound-only, "
 "window 132381805-132389824; 9 in-slice failures (Ankr 'Remote end closed connection'): 0x53ba295180ae4b730f9b2a031f77c1bcdb009509, "
 "0x6c90d2302bf0a9daaf453f3af2cd79f3c9b79cf8, 0x7807202fbe09f4aac9ac312ed593ba16806f6b34, 0x9281740a566901afba3e566e505e1896be176ff8, "
 "0xaa695698d59ee375dd822b3d940e3ba25932cf78, 0xb86cadb2dba0d2effdb74ba8796c41311612b9e1, 0xc3ba321124e0f621da8c4a0c1875705c83d6ce8c, "
 "0xdb062c12bf0a14227e7fe896a988950b050b51c1, 0xe20638c26fd7eac342a4164b4f026754375aebfe - those 9 contracts UNVERIFIED for this window, retry run 123; "
 "window NOT fully closed in-run (first unclosed run since run 117); 9 truncated contracts topic-filtered (all to 0 logs, incl. tracker 0x636fdfa9 -> 0).")

n = s.get("next_run_note", "")
repls = [
 ("Next run sent-tx window starts from block 132381805. RETRY run 122:",
  "Next run sent-tx window starts from block 132389825. RETRY run 123:"),
 ("39 consecutive runs", "40 consecutive runs"),
 ("(unreadable run 88-121, 34 consecutive", "(unreadable run 88-122, 35 consecutive"),
 ("(token0/token1 unreadable run 89-121, 33 consecutive", "(token0/token1 unreadable run 89-122, 34 consecutive"),
 ("0 wallets runs 103-121", "0 wallets runs 103-122"),
 ("0 wallets runs 91-121, 31st quiet run", "0 wallets runs 91-122, 32nd quiet run"),
 ("0 wallets runs 90-121, 32nd quiet run", "0 wallets runs 90-122, 33rd quiet run"),
]
for old, new in repls:
    if old in n:
        n = n.replace(old, new, 1)
        print(f"replaced: {old[:60]}...")
    else:
        print(f"NOT FOUND (skipped): {old[:80]}")
n = ("(Run 122: inbound list = run121 list (1734) + 0 deployments + 0 new rotation tokens; window NOT fully closed "
     "132381805-132389824, 0 hits, 9 in-slice failures (Ankr remote-end closed: 0x53ba tracker, 0x6c90, 0x7807, 0x9281, 0xaa69, 0xb86c, 0xc3ba, 0xdb06, 0xe206) - retry run 123; "
     "sent pass 54/55 (0x6ba79dcc failed, Ankr remote-end closed - retry run 123); "
     "1e9c still STALLED 26/27, 1153 STALLED 26, 79cd STALLED 20; 0x89220022 NEW shape: 19 ERC20 transfers + 1 plain BNB transfer, all to single recipient 0xa4682b0815..., 0 mint logs, NOT a mint; "
     "AFeng 5 txs (3 sale-calls 0.25 BNB, 0 mint logs - tracker pattern did NOT repeat, runs 114-122); future1001.ai 0 txs; 0x81c3d1b4 quiet again (0 txs); "
     "paid overlap vs run 121: 0 (churn set itself turned over completely, 19th straight run); total value 0.35269969 BNB (max 0.25 BNB); "
     "1 plain BNB transfer this run (0x89220022 -> 0xa4682b0815...).) " + n)
s["next_run_note"] = n

json.dump(s, open(STATE, "w"), indent=1)
print("state updated: last_run=122, paid_trend_run122 + inbound_log_leg_run122 added")
print("next window starts 132389825")
print("backup:", NP / "tracked-wallet-mint-scan-state.json.bak-run122-pre")
