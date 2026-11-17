#!/usr/bin/env python3
"""Run 138 state update (read-only bookkeeping): last_run + paid_trend_run138 +
inbound_log_leg_run138. No new mints this run, so no new reported_findings
entries. Inbound: residual rounds 4+5 (r24-r30) AGGREGATED this run - residual
COMPLETE (r00-r30, 1537 contracts, run-130 window fully covered); run-131
window round 0 (s00-s05) launched detached. No preview/mint/sign/login."""
import json, shutil
from pathlib import Path

HOME = Path.home()
NP = HOME / "workspace/narrative-pulse"
STATE = NP / "tracked-wallet-mint-scan-state.json"
shutil.copy(STATE, NP / "tracked-wallet-mint-scan-state.json.bak-run138-pre")
s = json.load(open(STATE))

s["last_run"] = {
 "run": 138,
 "block_start": 132509889,
 "block_end": 132518600,
 "window_wib": "2026-11-09 10:10:39 - 11:13:32 WIB (tx times); run executed ~11:05 WIB - ~11:50 WIB; sent-pass in-window txs 167, 0 mint-pattern txs",
 "wallets_checked": "55/55 via Ankr module (52/55 first attempt + 3 retry OK: 0xdb2d83f9, 0x3a39aa05, 0x92bc3297 - all 'Remote end closed connection', 0 in-window txs each on retry). 7 wallets active (0xc7c5faa2 41, 0x38031ca8 41, 0xad94ee77 39, 0x3628764a 17, 0xa0c1e94f 17, 0x7488d5da 10, 0x5cf3f945 2); AFeng 0 txs; future1001.ai 0 txs; 0x81c3d1b4 0 txs (quiet again); 0x8e966a9f 0 txs; 0x6ba79dcc/0x89220022/0xda91cefe 0 txs; 0x2325f175 0 txs.",
 "method_note": "NO TOTAL OUTAGE this run (Ankr sent pass completed 52/55 first attempt; fast_rpc RACE path still totally broken - block-number race + pair retry all-endpoints TimeoutError, same known quirk, NOT an outage). Sent pass 52/55 first attempt + 3 retry OK (0xdb2d83f9, 0x3a39aa05, 0x92bc3297, 0 in-window txs each), 167 in-window txs, max_block 132518600. Receipts via fast_rpc batch (6, ~4s pause) for 113 non-approve candidates: 113 status 1, 0 status 0, 0 NULL (no retry needed), 0 mint logs - fifteenth straight zero-mint run (runs 124-138). fast_rpc RACE eth_call still totally broken (pair retry 8/8 failed, all-endpoints TimeoutError/OSError) - batch vs race paths differ. Paid: 23 tokens; max 3 wallets/token (13 at 3, 7 at 2, 3 at 1); overlap vs run 137: 0 - the churn set itself turned over COMPLETELY again - thirty-fifth straight run with 0 churn overlap (runs 104-138 also 0). ZERO new rotations - the 27-wallet machine set had 0 txs this run (no buys, no sells, no approvals from any of the 27; verified overlap with active wallets = empty). The named-rotation streak ENDED run 104 (runs 97-103); run 138 has 0, thirty-fifth straight quiet run. No anomaly to report under the fast-path amendment (no new machine token, no name/symbol appearing, no size anomaly among machine buys, no free-mint path; churn trio PCS buys 42 txs). Trigger >25% NOT met by any token (max 3 wallets = 5.5%). No preview, no execution. Seatbelt 1e9c STALLED at 26: 0 wallets this run (0 buys, 0 sells) - sell-wallet union run101+run102 = 26/27, runs 103-138 add 0 - did NOT reach 27. NOT a new rotation; watch run 139 the same way. Deployments: ZERO - thirty-fifth straight run without deployments (run 104: 0 through run 138: 0; runs 97-103 had 25/72/64/32/35/70/68) - verified from raw receipts contractAddress fields, not the parsed JSON. Inbound list for run 138 = run137 list (1734) + 0 deployments + 0 new rotation tokens (total 1734, unchanged). NOTABLE NON-MINT (receipt-verified, NOT a mint/buy/signal): 0x5cf3f945 (0 txs runs 136-137) moved funds in 2 txs 20s apart - 46.62733679476170165 USDT (BSC USDT 0x55d398326f99059ff775485246999027b3197955) + 0.96 BNB plain transfer, both to 0x1e8450231050834dcbc7f0edc8c745cf568966bf, 10:42:57 + 10:43:17 WIB, blocks 132514521 + 132514566, both receipt status 1 - 1 entity fund move, not reported to chat. Plain BNB transfers this run: 3 (0.96 BNB above; 0.00204567 BNB 0x3628764a -> 0xc0094886; 0.00202544 BNB 0xc7c5faa2 -> 0x7f51d464). Selectors (sent pass, 167 txs): 54 approvals (0x095ea7b3) + 42 PCS buys (0xb6f9de95) + 40 PCS sells (0x791ac947) + 27 aggregator (0x39ecce49, all 0x38031ca8) + 3 empty-input + 1 transfer (0xa9059cbb, the USDT move above). NO contract creations, NO sale-call 0x4d819a2a. Nonzero-value txs 59, total 0.96684201 BNB, max 0.96 BNB (plain transfer above, not a buy). Most active wallets: 0xc7c5faa2 41, 0x38031ca8 41, 0xad94ee77 39, 0x3628764a 17, 0xa0c1e94f 17, 0x7488d5da 10, 0x5cf3f945 2. 0 status-0 txs. AFeng 0 txs this run. 0x2325f175 0 txs this run. INBOUND: residual rounds 4+5 AGGREGATED this run (run131-inbound-res130-r24..r30.json, run-130 window 132445937-132456148, 337 contracts, 2785 logs, 0 hits, 4 Ankr-failed contracts: 0xff6624b5c407780ddd84ed6fd65cc38ec6547777, 0x0d37f4cc06c5d0f74dde1c29e4986f3050e85c48, 0x3940372c8566610be8aab650df088aba59dd5b9d, 0x49cfd858f222a2c56a966a25d15c44b857df6ad5 - all 'Remote end closed connection', retry later; 2 truncated: 0x1de460f363af910f51726def188f9004276bf4bc topic-filtered 0 logs, 0 hits; 0x3dca077eb687df96cc987da0035c8fad89ae716c topic-filtered ERROR 'Remote end closed connection' - UNVERIFIED, retry later). RESIDUAL COMPLETE: r00-r30 = 1537 contracts, run-130 window fully covered. Run-131 window round 0 (s00-s05, contracts 0-300, window 132456149-132466646) LAUNCHED detached at end of run (pids 53141-53151, 6 alive) - run 139 aggregates s00-s05 and launches round 1 (s06-s11) the same detached way. DO NOT relaunch run134-inbound-chain.sh - its wait-loop shape is the dead pattern. Backlog after round 0 launch: run-131 window s06-s34 (29 slices) + run-132/133/134/135/136/137 windows (35 each = 210 slices) = 239 slices. Pair retry 8/8 FAILED again (all eight pairs: a6e6/887c/2bfb/c459/43c8/cfdb/0cf8/e68b - token0()/token1() all 'all endpoints failed' via fast_rpc race, TimeoutError/OSError) - unverified, not absence; 56th consecutive run for a6e6/887c/2bfb/c459, 51st for 43c8, 50th for cfdb/0cf8/e68b; retry run 139. Pointer-discovery (amendment 19:10 WIB, cap 5/run): NO pointer run this run - bridge queue EMPTY (116 contracts: 13 verified / 103 no-pointer / 0 queued) and 0 new contracts this run (0 deployments, 0 new rotation tokens), so nothing to discover. Bridge unchanged. CHAT REPORT this run: NONE (silent) - 0 new mints, no Free Bacot signal, no anomaly, no auto-mint trigger, no guard block. No preview/mint/sign/login/purchase by this job."
}

s["paid_trend_run138"] = ("23 tokens paid-bought; max 3 wallets/token (13 at 3, 7 at 2, 3 at 1); overlap vs run 137: 0 (churn set itself turned over completely, 35th straight run); "
 "0x81c3d1b4 quiet again (0 txs); future1001.ai 0 txs; 0x8e966a9f 0 txs; 0x6ba79dcc/0x89220022/0xda91cefe 0 txs; "
 "AFeng 0 txs this run; "
 "0x2325f175 0 txs this run; "
 "0x5cf3f945 back after 2 quiet runs (runs 136-137: 0 txs) - 2 txs, NOT buys: 46.63 USDT + 0.96 BNB fund move to 0x1e845023... (receipt-verified, 1 entity, not a signal); "
 "sent pass 52/55 first attempt + 3 retry OK (0xdb2d83f9, 0x3a39aa05, 0x92bc3297, 0 in-window txs each), 167 txs; receipts 113/113 status 1, 0 NULL, no retry needed; "
 "total nonzero value 0.96684201 BNB across 59 txs, max single 0.96 BNB (plain transfer, not a buy); "
 "3 plain BNB transfers; 0 deployments (35th straight run); 0 machine-set activity (35th straight quiet run); "
 "inbound: residual rounds 4+5 aggregated (7 slices, 337 contracts, 2785 logs, 0 hits, 4 Ankr-failed to retry, 2 truncated - 1 resolved 0 logs, 1 topic-filtered ERROR unverified); RESIDUAL COMPLETE (r00-r30, 1537 contracts); run-131 window round 0 (s00-s05) launched detached - aggregation + round 1 launch by run 139.")

s["inbound_log_leg_run138"] = ("Ankr getLogs address-filtered, RESIDUAL ROUNDS 4+5 AGGREGATED this run - RESIDUAL COMPLETE: "
 "run131-inbound-res130-r24..r30.json, run-130 window 132445937-132456148, 337 contracts of the 1537-contract residual list, 2785 logs, 0 hits, 4 failed "
 "(0xff6624b5c407780ddd84ed6fd65cc38ec6547777, 0x0d37f4cc06c5d0f74dde1c29e4986f3050e85c48, 0x3940372c8566610be8aab650df088aba59dd5b9d, 0x49cfd858f222a2c56a966a25d15c44b857df6ad5 - all Ankr 'Remote end closed connection', retry later), "
 "2 truncated (0x1de460f363af910f51726def188f9004276bf4bc: topic-filtered 0 logs, 0 hits; 0x3dca077eb687df96cc987da0035c8fad89ae716c: topic-filtered ERROR 'Remote end closed connection' - UNVERIFIED, retry later). "
 "Residual r00-r30 total: 1537 contracts, run-130 window fully covered. "
 "Run-131 window round 0 (s00-s05, contracts 0-300, window 132456149-132466646) launched detached at end of run (pids 53141-53151, 6 alive); run 139 aggregates s00-s05 and launches round 1 (s06-s11) detached. "
 "DO NOT relaunch run134-inbound-chain.sh (wait-loop shape = dead pattern). "
 "Backlog after round 0 launch: run-131 window s06-s34 (29 slices) + run-132/133/134/135/136/137 windows (35 each = 210 slices) = 239 slices. "
 "Inbound list unchanged: 1734 contracts.")

n = s.get("next_run_note", "")
repls = [
 ("Next run sent-tx window starts from block 132509889. RETRY run 138:",
  "Next run sent-tx window starts from block 132518601. RETRY run 139:"),
 ("(unreadable run 88-137, 50 consecutive", "(unreadable run 88-138, 51 consecutive"),
 ("(token0/token1 unreadable run 89-137, 49 consecutive", "(token0/token1 unreadable run 89-138, 50 consecutive"),
 ("0 wallets runs 103-137", "0 wallets runs 103-138"),
 ("0 wallets runs 91-137, 47th quiet run", "0 wallets runs 91-138, 48th quiet run"),
 ("0 wallets runs 90-137, 48th quiet run", "0 wallets runs 90-138, 49th quiet run"),
 ("pair retry 8/8 FAILED again (55th consecutive run", "pair retry 8/8 FAILED again (56th consecutive run"),
]
for old, new in repls:
    if old in n:
        n = n.replace(old, new, 1)
        print(f"replaced: {old[:60]}...")
    else:
        print(f"NOT FOUND (skipped): {old[:80]}")
n = ("(Run 138: NO TOTAL OUTAGE - Ankr sent pass 52/55 first attempt (fast_rpc race path still totally broken - block-number race all-endpoints TimeoutError, known quirk, NOT an outage); sent pass 52/55 first attempt + 3 retry OK (0xdb2d83f9, 0x3a39aa05, 0x92bc3297, 0 in-window txs each), 167 txs, max_block 132518600, receipts 113/113 status 1, 0 NULL, no retry needed, 0 mint logs (fifteenth straight zero-mint run, runs 124-138); "
     "AFeng 0 txs; 0x2325f175 0 txs; 0x5cf3f945 back after 2 quiet runs - 46.63 USDT + 0.96 BNB fund move to 0x1e845023... (receipt-verified, NOT a mint/buy/signal); value total 0.96684 BNB, max 0.96 BNB (plain transfer, not a buy); "
     "INBOUND: residual rounds 4+5 aggregated (7 slices, 337 contracts, 2785 logs, 0 hits, 4 Ankr-failed to retry, 2 truncated - 1 resolved 0 logs, 1 topic-filtered ERROR unverified); RESIDUAL COMPLETE (r00-r30, 1537 contracts, run-130 window fully covered); run-131 window round 0 (s00-s05) launched detached (pids 53141-53151) - run 139 aggregates s00-s05 + launches round 1 (s06-s11); DO NOT relaunch run134-inbound-chain.sh. "
     "Paid: 23 tokens, max 3 wallets/token (13/7/3), overlap vs run 137: 0 (35th straight run); 0 deployments (35th straight run); 0 machine-set activity (35th straight quiet run); 1e9c STALLED 26/27; "
     "pair retry 8/8 FAILED again (56th consecutive run a6e6/887c/2bfb/c459) - unverified, retry run 139; NO pointer run - bridge queue EMPTY (116: 13 verified / 103 no-pointer / 0 queued), 0 new contracts; "
     "CHAT REPORT: NONE (silent).) " + n)
s["next_run_note"] = n

json.dump(s, open(STATE, "w"), indent=1)
print("state updated: last_run=138, paid_trend_run138 + inbound_log_leg_run138 added, 0 new reported_findings entries")
print("next window starts 132518601")
print("backup:", NP / "tracked-wallet-mint-scan-state.json.bak-run138-pre")
