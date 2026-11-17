#!/usr/bin/env python3
"""Run 128 state update (read-only bookkeeping): last_run + paid_trend_run128 +
inbound_log_leg_run128. No new mints this run, so no new reported_findings
entries. No preview/mint/sign/login."""
import json, shutil
from pathlib import Path

HOME = Path.home()
NP = HOME / "workspace/narrative-pulse"
STATE = NP / "tracked-wallet-mint-scan-state.json"
shutil.copy(STATE, NP / "tracked-wallet-mint-scan-state.json.bak-run128-pre")
s = json.load(open(STATE))

s["last_run"] = {
 "run": 128,
 "block_start": 132430114,
 "block_end": 132437954,
 "window_wib": "2026-11-09 00:10:35 - 01:08:37 WIB (tx times); run executed ~01:05 WIB - ~01:47 WIB; sent-pass in-window txs 143, 0 mint-pattern txs",
 "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set); 0 FAILED first attempt. 7 wallets active (0xc7c5faa2 34, 0xad94ee77 33, 0x38031ca8 33, 0x3628764a 15, 0xa0c1e94f 15, 0x7488d5da 9, 0x81c3d1b4 4); AFeng 0 txs; future1001.ai 0 txs; 0x2325f175 0 txs; 0x89220022 0 txs; 0x6ba79dcc 0 txs; 0x81c3d1b4 4 txs (returned after quiet runs).",
 "method_note": "Sent pass Ankr ankr_getTransactionsByAddress via module: 55/55 OK first attempt (143 txs), 0 failed. Receipts via fast_rpc batch (6, ~4s pause) for 95 non-approve candidates: 95 status 1, 0 status 0, 0 NULL - no race fallbacks. 0 mint logs in any receipt - fifth straight zero-mint run (runs 124, 125, 126, 127, 128; first zero-mint run since run 14 was run 124). 0x81c3d1b4 RETURNED after quiet runs (4 txs: 2 aggregator 0x27772d13 to 0x296b... + 2 approvals, 00:33:56-00:34:10 WIB, 0 mint logs) and bought 0x55d39832... - the same non-churn token 0x38031ca8 bought run 127 (and sent an ERC20 transfer to in run 127); 1 wallet each run, no signal, no rotation. NO sale-calls 0x4d819a2a at all this run (AFeng 0 txs; 0x3803 made none either - its run-127 first sale-call did NOT repeat). Paid: 21 tokens; max 3 wallets/token (11 tokens at 3 wallets, ALL the same churn trio 0x3803/0xad94/0xc7c5; 5 at 2 - pair 0x3628/0xa0c1; 5 at 1 - 3 by 0x7488, 2 by 0x81c3). Overlap with run-127 paid tokens: 1 (non-churn 0x55d39832... only); CHURN ...7777 overlap: 0 - the churn set itself turned over COMPLETELY again - twenty-fifth straight run with 0 churn overlap (runs 104-128 also 0). ZERO new rotations - the 27-wallet machine set had 0 txs this run (no buys, no sells, no approvals from any of the 27; verified overlap with active wallets = empty). The named-rotation streak ENDED run 104 (runs 97-103); run 128 has 0, twenty-fifth straight quiet run. No anomaly to report under the fast-path amendment (no new machine token, no name/symbol appearing, no size anomaly among machine buys, no free-mint path; churn trio PCS buys 35 txs total only 0.00202 BNB - pure micro churn). Trigger >25% NOT met by any token (max 3 wallets = 5.5%). No preview, no execution. Seatbelt 1e9c STALLED at 26: 0 wallets this run (0 buys, 0 sells) - sell-wallet union run101+run102 = 26/27, runs 103-128 add 0 - did NOT reach 27. NOT a new rotation; watch run 129 the same way. Deployments: ZERO - twenty-fifth straight run without deployments (run 104: 0 through run 128: 0; runs 97-103 had 25/72/64/32/35/70/68) - verified from raw receipts contractAddress fields, not the parsed JSON. Inbound list for run 128 = run127 list (1734) + 0 deployments + 0 new rotation tokens (total 1734, unchanged). 1 plain BNB transfer this run (0xc7c5faa2 -> usual recipient 0x7f51d464..., 0.00207253 BNB, 00:45:51 WIB). Selectors (sent pass, 143 txs): 48 approvals (0x095ea7b3) + 35 PCS sells (0x791ac947) + 35 PCS buys (0xb6f9de95) + 22 aggregator (0x39ecce49, all 0x3803...) + 2 aggregator (0x27772d13, both 0x81c3...) + 1 empty-input. NO contract creations. Nonzero-value txs 47, total 0.00437908 BNB, max 0.00207253 BNB (plain BNB transfer above; churn micro PCS buys total only 0.00202 BNB). Most active wallets: 0xc7c5faa2 34, 0xad94ee77 33, 0x38031ca8 33, 0x3628764a 15, 0xa0c1e94f 15, 0x7488d5da 9, 0x81c3d1b4 4. 0 NULL receipts this run. 0 status-0 txs. Inbound leg (amendment 12:02 WIB): Ankr getLogs address-filtered per contract, 1734 contracts, 11427 logs (11343 slices + 84 retry), window 132430114-132437954, 0 hits, 0 inbound-only new. 35 slices of ~50 contracts in 6 parallel rounds (rounds ~4-5 min each). 1 in-slice failure (Ankr 'Remote end closed connection without response', 0x60b92624...) - recovered SAME-RUN via run128-inbound-retry.py (84 logs, 0 hits); window FULLY CLOSED in-run. 6 truncated contracts, all topic-filtered to 0 logs, no errors. Pair retry 8/8 FAILED again (all eight pairs: a6e6/887c/2bfb/c459/43c8/cfdb/0cf8/e68b - token0()/token1() all 'all endpoints failed' via fast_rpc race, OSError/TimeoutError) - unverified, not absence; 46th consecutive run for a6e6/887c/2bfb/c459, 41st for 43c8, 40th for cfdb/0cf8/e68b; retry run 129. fast_rpc race outage TOTAL during the pair retry - but the receipts batch pass worked fine earlier in the same run, so the outage is time-varying, not permanent. A failed race read is UNVERIFIED, never absence - retry, don't conclude. Pointer-discovery (amendment 19:10 WIB, cap 5/run, backfill LAST queued entry): Dronefarm website_no_pointer_found (contractURI + tokenURI #247 base64 JSON decoded IN FULL - name/description/on-chain SVG image only, no external_url/website/URL anywhere; Sourcify only generic docs/EIP URLs; ABI no site functions) - bridge gate website_no_pointer_found (already reported as finding run 3, hint for routine job only, NOT a new lead by scan job). Bridge: 116 contracts (13 verified via pointer, 103 no-pointer, 0 still queued - pointer backfill queue now EMPTY). CHAT REPORT this run: NONE (silent) - 0 new mints, no Free Bacot signal, no anomaly, no auto-mint trigger, no guard block. No preview/mint/sign/login/purchase by this job."
}

s["paid_trend_run128"] = ("21 tokens paid-bought; max 3 wallets/token (11 at 3, all churn trio 0x3803/0xad94/0xc7c5; "
 "5 at 2 - pair 0x3628/0xa0c1; 5 at 1 - 3 by 0x7488, 2 by 0x81c3); overlap vs run 127: 1 token (non-churn 0x55d39832... only); churn ...7777 overlap 0 (25th straight run); "
 "0x81c3d1b4 returned (4 txs: 2 aggregator 0x27772d13 + 2 approvals) and bought 0x55d39832... (also bought by 0x3803 run 127); "
 "AFeng 0 txs; future1001.ai 0 txs; 0x2325 0 txs; 0x89220022 quiet (0 txs); 0x6ba79dcc 0 txs; "
 "sent pass 55/55 first attempt; total nonzero value 0.00437908 BNB across 47 txs, max single 0.00207253 BNB (plain BNB 0xc7c5 -> 0x7f51d464...); "
 "1 plain BNB transfer this run; 0 deployments (25th straight run); 0 machine-set activity (25th straight quiet run).")

s["inbound_log_leg_run128"] = ("Ankr getLogs address-filtered, 1734 contracts, 11427 logs (11343 slices + 84 same-run retry), 0 hits, 0 inbound-only, "
 "1 in-slice failure (0x60b92624...), recovered same-run via retry (84 logs, 0 hits); window FULLY CLOSED in-run; "
 "6 truncated contracts, all topic-filtered to 0 logs, no errors.")

n = s.get("next_run_note", "")
repls = [
 ("Next run sent-tx window starts from block 132430115. RETRY run 128:",
  "Next run sent-tx window starts from block 132437955. RETRY run 129:"),
 ("45 consecutive runs", "46 consecutive runs"),
 ("(unreadable run 88-127, 40 consecutive", "(unreadable run 88-128, 41 consecutive"),
 ("(token0/token1 unreadable run 89-127, 39 consecutive", "(token0/token1 unreadable run 89-128, 40 consecutive"),
 ("0 wallets runs 103-127", "0 wallets runs 103-128"),
 ("0 wallets runs 91-127, 37th quiet run", "0 wallets runs 91-128, 38th quiet run"),
 ("0 wallets runs 90-127, 38th quiet run", "0 wallets runs 90-128, 39th quiet run"),
]
for old, new in repls:
    if old in n:
        n = n.replace(old, new, 1)
        print(f"replaced: {old[:60]}...")
    else:
        print(f"NOT FOUND (skipped): {old[:80]}")
n = ("(Run 128: inbound list = run127 list (1734) + 0 deployments + 0 new rotation tokens; window 132430114-132437954, 0 hits, 0 inbound-only, 1 in-slice failure, recovered same-run via retry (84 logs, 0 hits); window FULLY CLOSED in-run; 6 truncated, all topic-filtered 0 logs; sent pass 55/55 first attempt; 0 mint logs (fifth straight zero-mint run, runs 124-128); "
     "Dronefarm website_no_pointer_found (contractURI + tokenURI #247 base64 JSON, no URLs; Sourcify generic only; ABI no site functions) - bridge 116 (13 verified / 103 no-pointer / 0 queued - pointer backfill queue EMPTY); "
     "1e9c still STALLED 26/27, 1153 STALLED 26, 79cd STALLED 20; 0x81c3d1b4 RETURNED (4 txs, bought non-churn 0x55d39832... also bought by 0x3803 run 127 - 1 wallet each, no signal); NO sale-calls 0x4d819a2a this run (AFeng 0 txs; 0x3803 none either); 0x2325 0 txs; 0x89220022 quiet (0 txs); "
     "AFeng 0 txs; 0 sale-calls from AFeng this run (tracker pattern did NOT repeat, runs 114-128); future1001.ai 0 txs; "
     "paid overlap vs run 127: 1 non-churn token only, churn overlap 0 (25th straight run); total value 0.00437908 BNB (max 0.00207253 BNB plain transfer); "
     "1 plain BNB transfer this run; 0 deployments (25th straight run).) " + n)
s["next_run_note"] = n

json.dump(s, open(STATE, "w"), indent=1)
print("state updated: last_run=128, paid_trend_run128 + inbound_log_leg_run128 added, 0 new reported_findings entries")
print("next window starts 132437955")
print("backup:", NP / "tracked-wallet-mint-scan-state.json.bak-run128-pre")
