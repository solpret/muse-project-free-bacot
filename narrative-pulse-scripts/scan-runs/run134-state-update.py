#!/usr/bin/env python3
"""Run 134 state update (read-only bookkeeping): last_run + paid_trend_run134 +
inbound_log_leg_run134. No new mints this run, so no new reported_findings
entries. Inbound: run-133 chain VERIFIED DEAD (0 slices); root cause found -
bash wait-loop driver shape dies when its exec session ends; detached nohup
slices SURVIVE (residual round 0: 6/6 finished). Round 1 launched detached
at end of run; aggregation by run 135. No preview/mint/sign/login."""
import json, shutil
from pathlib import Path

HOME = Path.home()
NP = HOME / "workspace/narrative-pulse"
STATE = NP / "tracked-wallet-mint-scan-state.json"
shutil.copy(STATE, NP / "tracked-wallet-mint-scan-state.json.bak-run134-pre")
s = json.load(open(STATE))

s["last_run"] = {
 "run": 134,
 "block_start": 132478155,
 "block_end": 132486614,
 "window_wib": "2026-11-09 06:12:02 - 07:13:36 WIB (tx times); run executed ~07:05 WIB - ~07:40 WIB; sent-pass in-window txs 148, 0 mint-pattern txs",
 "wallets_checked": "55/55 via Ankr module (53 first attempt + 2 recovered via retry: 0x2325f175 + 0x341bed5b, both Ankr 'Remote end closed connection', both 0 txs in-window after retry; tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set). 6 wallets active (0xc7c5faa2 36, 0x38031ca8 36, 0xad94ee77 33, 0xa0c1e94f 17, 0x3628764a 16, 0x7488d5da 10); AFeng 0 txs; future1001.ai 0 txs; 0x2325f175 0 txs; 0x89220022 0 txs; 0x6ba79dcc 0 txs; 0x81c3d1b4 0 txs (quiet again); all 6 feed wallets 0 txs.",
 "method_note": "NO TOTAL OUTAGE this run (network slow but up: google 200 in 10.3s, Ankr 301 in 5.6s, dataseed 404-on-GET at ~07:07 WIB). Sent pass 55/55 (2 Ankr flakes recovered via run134-sent-retry.py, both 0 txs), 148 in-window txs, max_block 132486614. Receipts via fast_rpc batch (6, ~4s pause) for 99 non-approve candidates: 99 status 1, 0 status 0, 0 NULL (no retry needed), 0 mint logs - eleventh straight zero-mint run (runs 124-134). fast_rpc RACE eth_call still totally broken (pair retry 8/8 failed, all-endpoints TimeoutError/OSError) - batch vs race paths differ. Paid: 21 tokens; max 3 wallets/token (11 at 3, 7 at 2, 3 at 1); overlap vs run 133: 0 - the churn set itself turned over COMPLETELY again - thirty-first straight run with 0 churn overlap (runs 104-134 also 0). ZERO new rotations - the 27-wallet machine set had 0 txs this run (no buys, no sells, no approvals from any of the 27; verified overlap with active wallets = empty). The named-rotation streak ENDED run 104 (runs 97-103); run 134 has 0, thirty-first straight quiet run. No anomaly to report under the fast-path amendment (no new machine token, no name/symbol appearing, no size anomaly among machine buys, no free-mint path; churn trio PCS buys 38 txs). Trigger >25% NOT met by any token (max 3 wallets = 5.5%). No preview, no execution. Seatbelt 1e9c STALLED at 26: 0 wallets this run (0 buys, 0 sells) - sell-wallet union run101+run102 = 26/27, runs 103-134 add 0 - did NOT reach 27. NOT a new rotation; watch run 135 the same way. Deployments: ZERO - thirty-first straight run without deployments (run 104: 0 through run 134: 0; runs 97-103 had 25/72/64/32/35/70/68) - verified from raw receipts contractAddress fields, not the parsed JSON. Inbound list for run 134 = run133 list (1734) + 0 deployments + 0 new rotation tokens (total 1734, unchanged). 0 plain BNB transfers this run. Selectors (sent pass, 148 txs): 49 approvals (0x095ea7b3) + 38 PCS buys (0xb6f9de95) + 37 PCS sells (0x791ac947) + 24 aggregator (0x39ecce49). NO contract creations, NO sale-call 0x4d819a2a, NO transfer 0xa9059cbb, NO empty-input txs. Nonzero-value txs 50, total 0.00257284 BNB, max 0.0001 BNB. Most active wallets: 0xc7c5faa2 36, 0x38031ca8 36, 0xad94ee77 33, 0xa0c1e94f 17, 0x3628764a 16, 0x7488d5da 10. 0 status-0 txs. INBOUND: run-133 chain VERIFIED DEAD this run (pid 23588 gone; 0 JSON slices finished - died in residual round 0 like the run-132 chain). ROOT CAUSE FOUND + FIX VERIFIED: a bash wait-loop driver dies when its launching exec session ends (~5 min in, session record dropped from process list); a single python launched as detached nohup SURVIVES (sent pass, receipts pass, and the setsid sleep test all completed; the foreground round-0 relaunch died the same way). Drivers patched with skip-if-exists (run131-inbound-residual-driver.sh + run131/132/133/134-inbound-driver.sh). Residual round 0 RELAUNCHED as 6 detached nohup slices (pids 2916-2926) - ALL 6 FINISHED: run131-inbound-res130-r00..r05.json, 300 contracts, 6592 logs, 0 hits, 3 Ankr-failed contracts (0x6ce55cef..., 0x87ca3c67..., 0x94c4834b... - 'Remote end closed connection', retry later). Round 1 (r06-r11) LAUNCHED detached at end of run (pids 5769-5779, 6 alive) - run 135 aggregates r00-r11 and launches round 2 (r12-r17) the same detached way. DO NOT relaunch run134-inbound-chain.sh - its wait-loop shape is the dead pattern. Backlog after round 1: residual r12-r30 (19 slices) + run-131/132/133/134 windows (35 each = 140 slices) = 159 slices. Pair retry 8/8 FAILED again (all eight pairs: a6e6/887c/2bfb/c459/43c8/cfdb/0cf8/e68b - token0()/token1() all 'all endpoints failed' via fast_rpc race, TimeoutError/OSError) - unverified, not absence; 52nd consecutive run for a6e6/887c/2bfb/c459, 47th for 43c8, 46th for cfdb/0cf8/e68b; retry run 135. Pointer-discovery (amendment 19:10 WIB, cap 5/run): NO pointer run this run - bridge queue EMPTY (116 contracts: 13 verified / 103 no-pointer / 0 queued) and 0 new contracts this run (0 deployments, 0 new rotation tokens), so nothing to discover. Bridge unchanged. CHAT REPORT this run: NONE (silent) - 0 new mints, no Free Bacot signal, no anomaly, no auto-mint trigger, no guard block. No preview/mint/sign/login/purchase by this job."
}

s["paid_trend_run134"] = ("21 tokens paid-bought; max 3 wallets/token (11 at 3, 7 at 2, 3 at 1); overlap vs run 133: 0 (churn set itself turned over completely, 31st straight run); "
 "0x81c3d1b4 quiet again (0 txs); "
 "AFeng 0 txs; future1001.ai 0 txs; 0x2325 0 txs (recovered via retry); 0x89220022 quiet (0 txs); 0x6ba79dcc 0 txs; all 6 feed wallets 0 txs; "
 "sent pass 55/55 (53 first attempt + 2 Ankr flakes recovered via retry, 148 txs); receipts 99/99 status 1, 0 NULL, no retry needed; "
 "total nonzero value 0.00257284 BNB across 50 txs, max single 0.0001 BNB; "
 "0 plain BNB transfers; 0 deployments (31st straight run); 0 machine-set activity (31st straight quiet run); "
 "inbound: run-133 chain verified DEAD (0 slices); ROOT CAUSE FOUND - bash wait-loop drivers die at exec-session end, detached nohup slices survive; residual round 0 finished 6/6 detached (300 contracts, 6592 logs, 0 hits, 3 Ankr-failed to retry); round 1 (r06-r11) launched detached at end of run - aggregation + round 2 launch by run 135.")

s["inbound_log_leg_run134"] = ("Ankr getLogs address-filtered, RESIDUAL ROUND 0 FINISHED via NEW detached-nohup launch shape (replaces the dead chain): "
 "run131-inbound-res130-r00..r05.json, run-130 window 132445937-132456148, contracts 0-299 of residual list (1537), 300 contracts, 6592 logs, 0 hits, 3 failed "
 "(0x6ce55cef08ce723257dafae4c7e5f9eb80548b18, 0x87ca3c6704a08b56dc4e173315e948761ea2eb0c, 0x94c4834b186938f95edc67ff0536ac17f3102523 - all Ankr 'Remote end closed connection', retry later). "
 "Round 1 (r06-r11) launched detached at end of run (pids 5769-5779); run 135 aggregates r00-r11 and launches round 2 (r12-r17) detached. "
 "NOTE: the run-133 chain (pid 23588, setsid) DIED in residual round 0 with 0 slices, same as the run-132 chain (pid 6141) - the bash wait-loop driver shape dies when its "
 "launching exec session ends (~5 min in, session record dropped). Single nohup-detached python processes survive (proven: sent pass, receipts pass, setsid sleep test, "
 "and now round 0's 6 slices). DO NOT relaunch run134-inbound-chain.sh (wait-loop shape). Drivers patched with skip-if-exists. "
 "Backlog after round 1: residual r12-r30 (19 slices) + run-131/132/133/134 windows (35 each = 140 slices) = 159 slices. "
 "Inbound list unchanged: 1734 contracts (run-130 residual list is a subset of it).")

n = s.get("next_run_note", "")
repls = [
 ("Next run sent-tx window starts from block 132478155. RETRY run 134:",
  "Next run sent-tx window starts from block 132486615. RETRY run 135:"),
 ("(unreadable run 88-133, 46 consecutive", "(unreadable run 88-134, 47 consecutive"),
 ("(token0/token1 unreadable run 89-133, 45 consecutive", "(token0/token1 unreadable run 89-134, 46 consecutive"),
 ("0 wallets runs 103-133", "0 wallets runs 103-134"),
 ("0 wallets runs 91-133, 43rd quiet run", "0 wallets runs 91-134, 44th quiet run"),
 ("0 wallets runs 90-133, 44th quiet run", "0 wallets runs 90-134, 45th quiet run"),
 ("pair retry 8/8 FAILED again (51st consecutive run", "pair retry 8/8 FAILED again (52nd consecutive run"),
]
for old, new in repls:
    if old in n:
        n = n.replace(old, new, 1)
        print(f"replaced: {old[:60]}...")
    else:
        print(f"NOT FOUND (skipped): {old[:80]}")
n = ("(Run 134: NO-OUTAGE RUN - network slow but up (google 200 in 10.3s, Ankr 301 in 5.6s); sent pass 55/55 (53 first attempt + 2 Ankr flakes 0x2325/0x341b recovered via retry, both 0 txs; 148 txs, max_block 132486614), receipts 99/99 status 1, 0 NULL, no retry needed, 0 mint logs (eleventh straight zero-mint run, runs 124-134); "
     "INBOUND: run-133 chain VERIFIED DEAD (0 slices) - ROOT CAUSE FOUND: bash wait-loop drivers die at exec-session end; detached nohup slices SURVIVE (residual round 0 finished 6/6: 300 contracts, 6592 logs, 0 hits, 3 Ankr-failed to retry); round 1 (r06-r11) launched detached at end of run - run 135 aggregates r00-r11 + launches round 2 detached; DO NOT relaunch run134-inbound-chain.sh. "
     "Paid: 21 tokens, max 3 wallets/token (11/7/3), overlap vs run 133: 0 (31st straight run); 0 deployments (31st straight run); 0 machine-set activity (31st straight quiet run); 1e9c STALLED 26/27; "
     "pair retry 8/8 FAILED again (52nd consecutive run a6e6/887c/2bfb/c459) - unverified, retry run 135; NO pointer run - bridge queue EMPTY (116: 13 verified / 103 no-pointer / 0 queued), 0 new contracts; "
     "CHAT REPORT: NONE (silent).) " + n)
s["next_run_note"] = n

json.dump(s, open(STATE, "w"), indent=1)
print("state updated: last_run=134, paid_trend_run134 + inbound_log_leg_run134 added, 0 new reported_findings entries")
print("next window starts 132486615")
print("backup:", NP / "tracked-wallet-mint-scan-state.json.bak-run134-pre")
