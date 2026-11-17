#!/usr/bin/env python3
"""Run 132 state update (read-only bookkeeping): last_run + paid_trend_run132 +
inbound_log_leg_run132. No new mints this run, so no new reported_findings
entries. Inbound chain (run-130 residual + run-131 window + run-132 window)
LAUNCHED in background this run (pid 6141, run132-inbound-chain.sh) - aggregation
by run 133. No preview/mint/sign/login."""
import json, shutil
from pathlib import Path

HOME = Path.home()
NP = HOME / "workspace/narrative-pulse"
STATE = NP / "tracked-wallet-mint-scan-state.json"
shutil.copy(STATE, NP / "tracked-wallet-mint-scan-state.json.bak-run132-pre")
s = json.load(open(STATE))

s["last_run"] = {
 "run": 132,
 "block_start": 132466647,
 "block_end": 132470262,
 "window_wib": "2026-11-09 04:44:34 - 05:10:57 WIB (tx times); run executed ~05:05 WIB - ~05:40 WIB (started ~5 min late - brief VM network outage ~05:06-05:10 WIB); sent-pass in-window txs 67, 0 mint-pattern txs",
 "wallets_checked": "55/55 via Ankr module first attempt, 0 failed (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set). 6 wallets active (0xc7c5faa2 15, 0x38031ca8 15, 0xad94ee77 13, 0xa0c1e94f 12, 0x3628764a 6, 0x7488d5da 6); AFeng 0 txs; future1001.ai 0 txs; 0x2325f175 0 txs; 0x89220022 0 txs; 0x6ba79dcc 0 txs; 0x81c3d1b4 0 txs (quiet again); all 6 feed wallets 0 txs.",
 "method_note": "BRIEF-OUTAGE RUN: VM outbound network TOTALLY DOWN at run start ~05:06 WIB (google/Ankr/dataseed all curl 000) - recovered ~05:10 WIB (google 200, Ankr 301), ~4 min, much shorter than run 130 (~17 min) and run 131 (~29 min). Sent pass Ankr ankr_getTransactionsByAddress via module: 55/55 first attempt, 0 failed, 67 in-window txs total, max_block 132470262. Receipts via fast_rpc batch (6, ~4s pause) for 46 non-approve candidates: 44 status 1, 0 status 0, 2 NULL first pass (both PCS buys 0xb6f9de95 to router 0x10ed..., 0.0001 BNB each) - BOTH recovered same-run via run132-receipts-retry.py (2/2 status 0x1, 5 logs each), re-derived on the correct 46-candidate basis (NO approve re-parse; run130/131 lesson applied) -> 46/46 status 1, 0 NULL, 0 mint logs - ninth straight zero-mint run (runs 124-132). fast_rpc batch hit HTTP 429 once (batch 0, race fallback worked); fast_rpc RACE eth_call still totally broken (pair retry 8/8 failed, all-endpoints TimeoutError/OSError) - batch vs race paths differ. Paid: 11 tokens; max 3 wallets/token (4 at 3, 3 at 2, 4 at 1); overlap vs run 131: 0 - the churn set itself turned over COMPLETELY again - twenty-ninth straight run with 0 churn overlap (runs 104-132 also 0). ZERO new rotations - the 27-wallet machine set had 0 txs this run (no buys, no sells, no approvals from any of the 27; verified overlap with active wallets = empty). The named-rotation streak ENDED run 104 (runs 97-103); run 132 has 0, twenty-ninth straight quiet run. No anomaly to report under the fast-path amendment (no new machine token, no name/symbol appearing, no size anomaly among machine buys, no free-mint path; churn trio PCS buys 19 txs). Trigger >25% NOT met by any token (max 3 wallets = 5.5%). No preview, no execution. Seatbelt 1e9c STALLED at 26: 0 wallets this run (0 buys, 0 sells) - sell-wallet union run101+run102 = 26/27, runs 103-132 add 0 - did NOT reach 27. NOT a new rotation; watch run 133 the same way. Deployments: ZERO - twenty-ninth straight run without deployments (run 104: 0 through run 132: 0; runs 97-103 had 25/72/64/32/35/70/68) - verified from raw receipts contractAddress fields, not the parsed JSON. Inbound list for run 132 = run131 list (1734) + 0 deployments + 0 new rotation tokens (total 1734, unchanged). 0 plain BNB transfers this run. Selectors (sent pass, 67 txs): 21 approvals (0x095ea7b3) + 19 PCS buys (0xb6f9de95) + 17 PCS sells (0x791ac947) + 10 aggregator (0x39ecce49). NO contract creations. Nonzero-value txs 24, total 0.00142233 BNB, max 0.0001 BNB (PCS buy). Most active wallets: 0xc7c5faa2 15, 0x38031ca8 15, 0xad94ee77 13, 0xa0c1e94f 12, 0x3628764a 6, 0x7488d5da 6. 0 status-0 txs. INBOUND CHAIN LAUNCHED THIS RUN: run132-inbound-chain.sh (pid 6141, correct cwd scan-runs/) runs SEQUENTIALLY in background: (b) run-130-window residual driver (31 slices, window 132445937-132456148), (a) run-131 own-window driver (35 slices, window 132456149-132466646), (c) run-132 own-window driver (35 slices, window 132466647-132470262) - run 133 aggregates finished slices (run131-inbound-res130-r*.json, run131-inbound-s*.json, run132-inbound-s*.json), do NOT re-run completed slices. This FIXES the run-131 launch failure: run131-inbound-driver.sh was launched from narrative-pulse/ instead of scan-runs/, so it died instantly ('No such file or directory') and the run-131 window was never scanned. Pair retry 8/8 FAILED again (all eight pairs: a6e6/887c/2bfb/c459/43c8/cfdb/0cf8/e68b - token0()/token1() all 'all endpoints failed' via fast_rpc race, TimeoutError/OSError; 0cf8 token1 returned garbage '0x0x') - unverified, not absence; 50th consecutive run for a6e6/887c/2bfb/c459, 45th for 43c8, 44th for cfdb/0cf8/e68b; retry run 133. Pointer-discovery (amendment 19:10 WIB, cap 5/run): NO pointer run this run - bridge queue EMPTY (116 contracts: 13 verified / 103 no-pointer / 0 queued) and 0 new contracts this run (0 deployments, 0 new rotation tokens), so nothing to discover. Bridge unchanged. CHAT REPORT this run: NONE (silent) - 0 new mints, no Free Bacot signal, no anomaly, no auto-mint trigger, no guard block. No preview/mint/sign/login/purchase by this job."
}

s["paid_trend_run132"] = ("11 tokens paid-bought; max 3 wallets/token (4 at 3, 3 at 2, 4 at 1); overlap vs run 131: 0 (churn set itself turned over completely, 29th straight run); "
 "0x81c3d1b4 quiet again (0 txs); "
 "AFeng 0 txs; future1001.ai 0 txs; 0x2325 0 txs; 0x89220022 quiet (0 txs); 0x6ba79dcc 0 txs; all 6 feed wallets 0 txs; "
 "sent pass 55/55 first attempt (0 Ankr failures); receipts 46/46 status 1 after same-run retry of 2 NULLs (2/2 recovered, re-derived on 46-candidate basis); "
 "total nonzero value 0.00142233 BNB across 24 txs, max single 0.0001 BNB (PCS buy); "
 "0 plain BNB transfers this run; 0 deployments (29th straight run); 0 machine-set activity (29th straight quiet run); "
 "inbound chain launched in background (run-130 residual + run-131 window + run-132 window, pid 6141) - aggregation by run 133.")

s["inbound_log_leg_run132"] = ("Ankr getLogs address-filtered, CHAINED DRIVER LAUNCHED in background this run (run132-inbound-chain.sh, pid 6141, correct cwd scan-runs/): "
 "(b) run-130-window residual (31 slices, window 132445937-132456148) -> (a) run-131 own window (35 slices, window 132456149-132466646) -> (c) run-132 own window "
 "(35 slices, window 132466647-132470262), sequential, 6 slices parallel per round. Run 133 aggregates finished slices; do NOT re-run completed slices. "
 "NOTE: the run-131 driver never ran in run 131 - it was launched from the wrong cwd (narrative-pulse/ instead of scan-runs/) and died instantly; this run's chain fixes that.")

n = s.get("next_run_note", "")
repls = [
 ("Next run sent-tx window starts from block 132466647. RETRY run 132:",
  "Next run sent-tx window starts from block 132470263. RETRY run 133:"),
 ("(unreadable run 88-131, 44 consecutive", "(unreadable run 88-132, 45 consecutive"),
 ("(token0/token1 unreadable run 89-131, 43 consecutive", "(token0/token1 unreadable run 89-132, 44 consecutive"),
 ("0 wallets runs 103-131", "0 wallets runs 103-132"),
 ("0 wallets runs 91-131, 41st quiet run", "0 wallets runs 91-132, 42nd quiet run"),
 ("0 wallets runs 90-131, 42nd quiet run", "0 wallets runs 90-132, 43rd quiet run"),
 ("pair retry 8/8 FAILED again (49th consecutive run", "pair retry 8/8 FAILED again (50th consecutive run"),
]
for old, new in repls:
    if old in n:
        n = n.replace(old, new, 1)
        print(f"replaced: {old[:60]}...")
    else:
        print(f"NOT FOUND (skipped): {old[:80]}")
n = ("(Run 132: BRIEF-OUTAGE RUN - VM network totally down at start ~05:06 WIB (~4 min, google/Ankr/dataseed all curl 000), recovered ~05:10 WIB (google 200, Ankr 301); sent 55/55 first attempt, 0 failed (67 txs, max_block 132470262), receipts 46/46 status 1 after same-run retry of 2 NULLs (2/2 recovered, re-derived on 46-candidate basis - NO approve re-parse), 0 mint logs (ninth straight zero-mint run, runs 124-132); "
     "INBOUND CHAIN LAUNCHED in background (run132-inbound-chain.sh pid 6141, correct cwd scan-runs/): (b) run-130 residual 31 slices + (a) run-131 window 35 slices + (c) run-132 window 35 slices, sequential - run 133 aggregates finished slices, do NOT re-run completed ones (FIXES run-131 driver launch that died instantly from wrong cwd). "
     "Paid: 11 tokens, max 3 wallets/token, overlap vs run 131: 0 (29th straight run); 0 deployments (29th straight run); 0 machine-set activity (29th straight quiet run); 1e9c STALLED 26/27; "
     "pair retry 8/8 FAILED again (50th consecutive run a6e6/887c/2bfb/c459) - unverified, retry run 133; NO pointer run - bridge queue EMPTY (116: 13 verified / 103 no-pointer / 0 queued), 0 new contracts; "
     "CHAT REPORT: NONE (silent).) " + n)
s["next_run_note"] = n

json.dump(s, open(STATE, "w"), indent=1)
print("state updated: last_run=132, paid_trend_run132 + inbound_log_leg_run132 added, 0 new reported_findings entries")
print("next window starts 132470263")
print("backup:", NP / "tracked-wallet-mint-scan-state.json.bak-run132-pre")
