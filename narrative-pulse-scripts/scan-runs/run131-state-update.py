#!/usr/bin/env python3
"""Run 131 state update (read-only bookkeeping): last_run + paid_trend_run131 +
inbound_log_leg_run131. No new mints this run, so no new reported_findings
entries. Run 130 residuals CLOSED this run (aa49 sent + 12 NULL receipts).
Inbound leg NOT run in-run (outage delay) - own-window driver launched in
background at end of run; run 132 aggregates. No preview/mint/sign/login."""
import json, shutil
from pathlib import Path

HOME = Path.home()
NP = HOME / "workspace/narrative-pulse"
STATE = NP / "tracked-wallet-mint-scan-state.json"
shutil.copy(STATE, NP / "tracked-wallet-mint-scan-state.json.bak-run131-pre")
s = json.load(open(STATE))

s["last_run"] = {
 "run": 131,
 "block_start": 132456149,
 "block_end": 132466646,
 "window_wib": "2026-11-09 03:26:19 - 04:43:49 WIB (tx times); run executed ~04:42 WIB - ~05:02 WIB (started 37 min late - VM network outage); sent-pass in-window txs 197, 0 mint-pattern txs",
 "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set); 3 FAILED first attempt (Ankr 'Remote end closed connection' / timeouts, post-outage flaky); all 3 recovered via run131-sent-retry.py (ALL 0 in-window txs). 6 wallets active (0xc7c5faa2 47, 0xad94ee77 45, 0x38031ca8 46, 0x3628764a 21, 0xa0c1e94f 20, 0x7488d5da 18); AFeng 0 txs; future1001.ai 0 txs; 0x2325f175 0 txs; 0x89220022 0 txs; 0x6ba79dcc 0 txs; 0x81c3d1b4 0 txs (quiet again); all 6 feed wallets 0 txs.",
 "method_note": "OUTAGE-DELAYED RUN: VM outbound network TOTALLY DOWN ~04:13-04:42 WIB (~29 min; google/Ankr/dataseed all curl 000, DNS resolving) - longer than run 130's ~17-min outage; recovered 21:42 UTC (google 200, Ankr 301). Run scheduled 04:05 WIB but first successful read 04:42 WIB. Sent pass Ankr ankr_getTransactionsByAddress via module: 197 in-window txs total, max_block 132466646. Receipts via fast_rpc batch (6, ~4s pause) for 131 non-approve candidates: 131 status 1, 0 status 0, 0 NULL, 0 mint logs - eighth straight zero-mint run (runs 124-131). fast_rpc BATCH receipts healthy this run (0 NULL) but fast_rpc RACE eth_call still totally broken (pair retry 8/8 failed, all-endpoints TimeoutError) - batch vs race paths differ. Paid: 28 tokens; max 3 wallets/token (15 at 3, 7 at 2, 6 at 1); overlap vs run 130: 0 - the churn set itself turned over COMPLETELY again - twenty-eighth straight run with 0 churn overlap (runs 104-131 also 0). ZERO new rotations - the 27-wallet machine set had 0 txs this run (no buys, no sells, no approvals from any of the 27; verified overlap with active wallets = empty). The named-rotation streak ENDED run 104 (runs 97-103); run 131 has 0, twenty-eighth straight quiet run. No anomaly to report under the fast-path amendment (no new machine token, no name/symbol appearing, no size anomaly among machine buys, no free-mint path; churn trio PCS buys 50 txs). Trigger >25% NOT met by any token (max 3 wallets = 5.5%). No preview, no execution. Seatbelt 1e9c STALLED at 26: 0 wallets this run (0 buys, 0 sells) - sell-wallet union run101+run102 = 26/27, runs 103-131 add 0 - did NOT reach 27. NOT a new rotation; watch run 132 the same way. Deployments: ZERO - twenty-eighth straight run without deployments (run 104: 0 through run 131: 0; runs 97-103 had 25/72/64/32/35/70/68) - verified from raw receipts contractAddress fields, not the parsed JSON. Inbound list for run 131 = run130 list (1734) + 0 deployments + 0 new rotation tokens (total 1734, unchanged). 0 plain BNB transfers this run. Selectors (sent pass, 197 txs): 66 approvals (0x095ea7b3) + 50 PCS buys (0xb6f9de95) + 50 PCS sells (0x791ac947) + 31 aggregator (0x39ecce49). NO contract creations. Nonzero-value txs 65, total 0.00334606 BNB, max 0.0001 BNB (PCS buy). Most active wallets: 0xc7c5faa2 47, 0x38031ca8 46, 0xad94ee77 45, 0x3628764a 21, 0xa0c1e94f 20, 0x7488d5da 18. 0 status-0 txs. RUN-130 RESIDUALS CLOSED THIS RUN: (1) sent gap 0xaa49e7fe... window 132445937-132456148 re-read via run131-sent-residual-aa49.py - RECOVERED, 0 in-window txs, merged into run130-sent.json; (2) 12 NULL receipts recovered 12/12 via run131-receipts-retry130.py (all status 0x1) BUT the retry script reproduced the KNOWN re-parse bug (nulls inflated to 69 by including 69 approve txs) - FIXED same-run via run131-receipts-fix130.py back to the correct 142-candidate basis (142 total, 0 mint logs, 0 null, 142 status 1, paid 30 tokens); LESSON: the run130-receipts-retry.py script still carries the bug - DO NOT reuse it unpatched; always re-derive on the non-approve basis afterwards. Run-130 window now FULLY CLOSED on the sent side (55/55 wallets, 142/142 receipts verified, 0 mint logs). (3) Inbound leg for run-130 window STILL OPEN: slices s06-s34 + 103 failed round-0 contracts NOT run - driver script ready (run131-inbound-residual-driver.sh) but NOT launched this run (time); run 132 MUST run it. Inbound leg (amendment 12:02 WIB) for run-131 OWN window: NOT run in-run (outage delay ate the slot); driver run131-inbound-driver.sh LAUNCHED IN BACKGROUND at end of run 131 (35 slices, window 132456149-132466646) - run 132 must aggregate run131-inbound-s*.json when the driver finishes; do NOT re-run completed slices. Pair retry 8/8 FAILED again (all eight pairs: a6e6/887c/2bfb/c459/43c8/cfdb/0cf8/e68b - token0()/token1() all 'all endpoints failed' via fast_rpc race, TimeoutError) - unverified, not absence; 49th consecutive run for a6e6/887c/2bfb/c459, 44th for 43c8, 43rd for cfdb/0cf8/e68b; retry run 132. Pointer-discovery (amendment 19:10 WIB, cap 5/run): NO pointer run this run - bridge queue EMPTY (116 contracts: 13 verified / 103 no-pointer / 0 queued) and 0 new contracts this run (0 deployments, 0 new rotation tokens), so nothing to discover. Bridge unchanged. CHAT REPORT this run: NONE (silent) - 0 new mints, no Free Bacot signal, no anomaly, no auto-mint trigger, no guard block. No preview/mint/sign/login/purchase by this job."
}

s["paid_trend_run131"] = ("28 tokens paid-bought; max 3 wallets/token (15 at 3, 7 at 2, 6 at 1); overlap vs run 130: 0 (churn set itself turned over completely, 28th straight run); "
 "0x81c3d1b4 quiet again (0 txs); "
 "AFeng 0 txs; future1001.ai 0 txs; 0x2325 0 txs; 0x89220022 quiet (0 txs); 0x6ba79dcc 0 txs; all 6 feed wallets 0 txs; "
 "sent pass 52/55 first attempt (3 Ankr failures post-outage, all 3 recovered via retry, 0 in-window each); "
 "total nonzero value 0.00334606 BNB across 65 txs, max single 0.0001 BNB (PCS buy); "
 "0 plain BNB transfers this run; 0 deployments (28th straight run); 0 machine-set activity (28th straight quiet run); "
 "run-130 residuals CLOSED: aa49 sent gap (0 txs) + 12 NULL receipts (12/12 recovered, re-derived on 142-candidate basis).")

s["inbound_log_leg_run131"] = ("Ankr getLogs address-filtered, NOT RUN in-run (outage delay): own-window driver run131-inbound-driver.sh launched in background at end of run 131 "
 "(35 slices, window 132456149-132466646) - PENDING aggregation by run 132. Run-130-window residual (slices s06-s34 + 103 failed round-0 contracts, window 132445937-132456148) "
 "STILL NOT RUN - driver script ready (run131-inbound-residual-driver.sh); run 132 MUST run it.")

n = s.get("next_run_note", "")
repls = [
 ("Next run sent-tx window starts from block 132456149. RETRY run 131:",
  "Next run sent-tx window starts from block 132466647. RETRY run 132:"),
 ("49 consecutive runs", "50 consecutive runs"),
 ("(unreadable run 88-130, 43 consecutive", "(unreadable run 88-131, 44 consecutive"),
 ("(token0/token1 unreadable run 89-130, 42 consecutive", "(token0/token1 unreadable run 89-131, 43 consecutive"),
 ("0 wallets runs 103-130", "0 wallets runs 103-131"),
 ("0 wallets runs 91-130, 40th quiet run", "0 wallets runs 91-131, 41st quiet run"),
 ("0 wallets runs 90-130, 41st quiet run", "0 wallets runs 90-131, 42nd quiet run"),
]
for old, new in repls:
    if old in n:
        n = n.replace(old, new, 1)
        print(f"replaced: {old[:60]}...")
    else:
        print(f"NOT FOUND (skipped): {old[:80]}")
n = ("(Run 131: OUTAGE-DELAYED RUN - VM network totally down ~04:13-04:42 WIB (~29 min, longer than run 130's ~17 min), run started 37 min late; sent 55/55 (197 txs, max_block 132466646), receipts 131/131 status 1, 0 NULL, 0 mint logs (eighth straight zero-mint run, runs 124-131); "
     "RUN-130 RESIDUALS CLOSED: aa49 sent gap re-read (0 txs) + 12 NULL receipts recovered 12/12 (re-parse bug reproduced by retry script - FIXED same-run to 142-candidate basis; DO NOT reuse run130-receipts-retry.py unpatched); run-130 window now FULLY CLOSED sent-side. "
     "INBOUND PENDING FOR RUN 132: (a) run-131 own-window driver RUNNING in background (run131-inbound-driver.sh, 35 slices, window 132456149-132466646) - aggregate run131-inbound-s*.json when done, do NOT re-run completed slices; "
     "(b) run-130-window residual driver NOT YET RUN - run run131-inbound-residual-driver.sh (31 slices, window 132445937-132456148, slices s06-s34 + 103 failed round-0) and aggregate run131-inbound-res130-r*.json. "
     "Paid: 28 tokens, max 3 wallets/token, overlap vs run 130: 0 (28th straight run); 0 deployments (28th straight run); 0 machine-set activity (28th straight quiet run); 1e9c STALLED 26/27; "
     "pair retry 8/8 FAILED again (49th consecutive run a6e6/887c/2bfb/c459) - unverified, retry run 132; NO pointer run - bridge queue EMPTY (116: 13 verified / 103 no-pointer / 0 queued), 0 new contracts; "
     "CHAT REPORT: NONE (silent).) " + n)
s["next_run_note"] = n

json.dump(s, open(STATE, "w"), indent=1)
print("state updated: last_run=131, paid_trend_run131 + inbound_log_leg_run131 added, 0 new reported_findings entries")
print("next window starts 132466647")
print("backup:", NP / "tracked-wallet-mint-scan-state.json.bak-run131-pre")
