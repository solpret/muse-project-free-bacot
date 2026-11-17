#!/usr/bin/env python3
"""Run 129 state update (read-only bookkeeping): last_run + paid_trend_run129 +
inbound_log_leg_run129. No new mints this run, so no new reported_findings
entries. No preview/mint/sign/login."""
import json, shutil
from pathlib import Path

HOME = Path.home()
NP = HOME / "workspace/narrative-pulse"
STATE = NP / "tracked-wallet-mint-scan-state.json"
shutil.copy(STATE, NP / "tracked-wallet-mint-scan-state.json.bak-run129-pre")
s = json.load(open(STATE))

s["last_run"] = {
 "run": 129,
 "block_start": 132437954,
 "block_end": 132445937,
 "window_wib": "2026-11-09 01:09:48 - 02:08:30 WIB (tx times); run executed ~02:05 WIB - ~02:42 WIB; sent-pass in-window txs 158, 0 mint-pattern txs",
 "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set); 0 FAILED first attempt. 6 wallets active (0xad94ee77 39, 0x38031ca8 38, 0xc7c5faa2 34, 0xa0c1e94f 18, 0x3628764a 16, 0x7488d5da 13); AFeng 0 txs; future1001.ai 0 txs; 0x2325f175 0 txs; 0x89220022 0 txs; 0x6ba79dcc 0 txs; 0x81c3d1b4 0 txs (quiet again after returning run 128).",
 "method_note": "Sent pass Ankr ankr_getTransactionsByAddress via module: 55/55 OK first attempt (158 txs), 0 failed. Receipts via fast_rpc batch (6, ~4s pause) for 105 non-approve candidates: 105 status 1, 0 status 0, 0 NULL - no race fallbacks. 0 mint logs in any receipt - sixth straight zero-mint run (runs 124, 125, 126, 127, 128, 129; first zero-mint run since run 14 was run 124). 0x81c3d1b4 quiet again (0 txs) after its run-128 return (4 txs, bought non-churn 0x55d39832...). NO sale-calls 0x4d819a2a at all this run (AFeng 0 txs; 0x3803 made none either). Paid: 24 tokens; max 3 wallets/token (14 tokens at 3 wallets, ALL the same churn trio 0x3803/0xad94/0xc7c5; 6 at 2 - pair 0x3628/0xa0c1; 4 at 1 - all by 0x7488, non-churn). Overlap with run-128 paid tokens: 0 - the churn set itself turned over COMPLETELY again - twenty-sixth straight run with 0 churn overlap (runs 104-129 also 0). ZERO new rotations - the 27-wallet machine set had 0 txs this run (no buys, no sells, no approvals from any of the 27; verified overlap with active wallets = empty). The named-rotation streak ENDED run 104 (runs 97-103); run 129 has 0, twenty-sixth straight quiet run. No anomaly to report under the fast-path amendment (no new machine token, no name/symbol appearing, no size anomaly among machine buys, no free-mint path; churn trio PCS buys 44 txs total only 0.00251 BNB - pure micro churn). Trigger >25% NOT met by any token (max 3 wallets = 5.5%). No preview, no execution. Seatbelt 1e9c STALLED at 26: 0 wallets this run (0 buys, 0 sells) - sell-wallet union run101+run102 = 26/27, runs 103-129 add 0 - did NOT reach 27. NOT a new rotation; watch run 130 the same way. Deployments: ZERO - twenty-sixth straight run without deployments (run 104: 0 through run 129: 0; runs 97-103 had 25/72/64/32/35/70/68) - verified from raw receipts contractAddress fields, not the parsed JSON. Inbound list for run 129 = run128 list (1734) + 0 deployments + 0 new rotation tokens (total 1734, unchanged). 0 plain BNB transfers this run. Selectors (sent pass, 158 txs): 53 approvals (0x095ea7b3) + 44 PCS buys (0xb6f9de95) + 37 PCS sells (0x791ac947) + 24 aggregator (0x39ecce49, all 0x3803...). NO contract creations. Nonzero-value txs 58, total 0.00287847 BNB, max 0.0001 BNB (a PCS buy to router 0x10ed...). Most active wallets: 0xad94ee77 39, 0x38031ca8 38, 0xc7c5faa2 34, 0xa0c1e94f 18, 0x3628764a 16, 0x7488d5da 13. 0 NULL receipts this run. 0 status-0 txs. Inbound leg (amendment 12:02 WIB): Ankr getLogs address-filtered per contract, 1734 contracts, 9423 logs (9423 slices + 0 retry), window 132437954-132445937, 0 hits, 0 inbound-only new. 35 slices of ~50 contracts in 6 parallel rounds (rounds ~4-5 min each). 3 in-slice failures (Ankr 'Remote end closed connection without response': 0x1cf9e602..., 0x2c215262..., 0x5ad666a8...) - ALL recovered SAME-RUN via run129-inbound-retry.py (0 logs, 0 hits); window FULLY CLOSED in-run. 6 truncated contracts, all topic-filtered to 0 logs, no errors. Pair retry 8/8 FAILED again (all eight pairs: a6e6/887c/2bfb/c459/43c8/cfdb/0cf8/e68b - token0()/token1() all 'all endpoints failed' via fast_rpc race, OSError/TimeoutError mix) - unverified, not absence; 47th consecutive run for a6e6/887c/2bfb/c459, 42nd for 43c8, 41st for cfdb/0cf8/e68b; retry run 130. fast_rpc race outage during the pair retry (and a total race outage on the block-number read at run start, recovered on retry) - but the receipts batch pass worked fine earlier in the same run, so the outage is time-varying, not permanent. A failed race read is UNVERIFIED, never absence - retry, don't conclude. Pointer-discovery (amendment 19:10 WIB, cap 5/run): NO pointer run this run - bridge queue EMPTY (116 contracts: 13 verified / 103 no-pointer / 0 queued) and 0 new contracts this run (0 deployments, 0 new rotation tokens), so nothing to discover. Bridge unchanged. CHAT REPORT this run: NONE (silent) - 0 new mints, no Free Bacot signal, no anomaly, no auto-mint trigger, no guard block. No preview/mint/sign/login/purchase by this job."
}

s["paid_trend_run129"] = ("24 tokens paid-bought; max 3 wallets/token (14 at 3, all churn trio 0x3803/0xad94/0xc7c5; "
 "6 at 2 - pair 0x3628/0xa0c1; 4 at 1 - all by 0x7488, non-churn); overlap vs run 128: 0 (churn set itself turned over completely, 26th straight run); "
 "0x81c3d1b4 quiet again (0 txs) after returning run 128; "
 "AFeng 0 txs; future1001.ai 0 txs; 0x2325 0 txs; 0x89220022 quiet (0 txs); 0x6ba79dcc 0 txs; "
 "sent pass 55/55 first attempt; total nonzero value 0.00287847 BNB across 58 txs, max single 0.0001 BNB (PCS buy to router); "
 "0 plain BNB transfers this run; 0 deployments (26th straight run); 0 machine-set activity (26th straight quiet run).")

s["inbound_log_leg_run129"] = ("Ankr getLogs address-filtered, 1734 contracts, 9423 logs (9423 slices + 0 retry), 0 hits, 0 inbound-only, "
 "3 in-slice failures (0x1cf9e602..., 0x2c215262..., 0x5ad666a8...), ALL recovered same-run via retry (0 logs, 0 hits); window FULLY CLOSED in-run; "
 "6 truncated contracts, all topic-filtered to 0 logs, no errors.")

n = s.get("next_run_note", "")
repls = [
 ("Next run sent-tx window starts from block 132437955. RETRY run 129:",
  "Next run sent-tx window starts from block 132445938. RETRY run 130:"),
 ("46 consecutive runs", "47 consecutive runs"),
 ("(unreadable run 88-128, 41 consecutive", "(unreadable run 88-129, 42 consecutive"),
 ("(token0/token1 unreadable run 89-128, 40 consecutive", "(token0/token1 unreadable run 89-129, 41 consecutive"),
 ("0 wallets runs 103-128", "0 wallets runs 103-129"),
 ("0 wallets runs 91-128, 38th quiet run", "0 wallets runs 91-129, 39th quiet run"),
 ("0 wallets runs 90-128, 39th quiet run", "0 wallets runs 90-129, 40th quiet run"),
]
for old, new in repls:
    if old in n:
        n = n.replace(old, new, 1)
        print(f"replaced: {old[:60]}...")
    else:
        print(f"NOT FOUND (skipped): {old[:80]}")
n = ("(Run 129: inbound list = run128 list (1734) + 0 deployments + 0 new rotation tokens; window 132437954-132445937, 0 hits, 0 inbound-only, 3 in-slice failures, ALL recovered same-run via retry (0 logs, 0 hits); window FULLY CLOSED in-run; 6 truncated, all topic-filtered 0 logs; sent pass 55/55 first attempt; 0 mint logs (sixth straight zero-mint run, runs 124-129); NO pointer run - bridge queue EMPTY (116: 13 verified / 103 no-pointer / 0 queued), 0 new contracts; "
     "1e9c still STALLED 26/27, 1153 STALLED 26, 79cd STALLED 20; 0x81c3d1b4 quiet again (0 txs) after returning run 128; NO sale-calls 0x4d819a2a this run (AFeng 0 txs; 0x3803 none either); 0x2325 0 txs; 0x89220022 quiet (0 txs); "
     "AFeng 0 txs; 0 sale-calls from AFeng this run (tracker pattern did NOT repeat, runs 114-129); future1001.ai 0 txs; "
     "paid overlap vs run 128: 0 (churn set itself turned over completely, 26th straight run); total value 0.00287847 BNB (max 0.0001 BNB PCS buy); "
     "0 plain BNB transfers this run; 0 deployments (26th straight run).) " + n)
s["next_run_note"] = n

json.dump(s, open(STATE, "w"), indent=1)
print("state updated: last_run=129, paid_trend_run129 + inbound_log_leg_run129 added, 0 new reported_findings entries")
print("next window starts 132445938")
print("backup:", NP / "tracked-wallet-mint-scan-state.json.bak-run129-pre")
