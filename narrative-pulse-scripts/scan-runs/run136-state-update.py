#!/usr/bin/env python3
"""Run 136 state update (read-only bookkeeping): last_run + paid_trend_run136 +
inbound_log_leg_run136. No new mints this run, so no new reported_findings
entries. Inbound: residual round 2 (r12-r17) AGGREGATED this run (6 slices,
300 contracts, 157 logs, 0 hits); round 3 (r18-r23) launched detached.
0x2325f175 1 tx (recurring aggregator buy, NOT a mint, receipt-verified).
No preview/mint/sign/login."""
import json, shutil
from pathlib import Path

HOME = Path.home()
NP = HOME / "workspace/narrative-pulse"
STATE = NP / "tracked-wallet-mint-scan-state.json"
shutil.copy(STATE, NP / "tracked-wallet-mint-scan-state.json.bak-run136-pre")
s = json.load(open(STATE))

s["last_run"] = {
 "run": 136,
 "block_start": 132494180,
 "block_end": 132501972,
 "window_wib": "2026-11-09 08:11:27 - 09:08:49 WIB (tx times); run executed ~09:05 WIB - ~09:25 WIB; sent-pass in-window txs 152, 0 mint-pattern txs",
 "wallets_checked": "55/55 via Ankr module, FIRST ATTEMPT, 0 failed (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set). 7 wallets active (0xc7c5faa2 38, 0xad94ee77 37, 0x38031ca8 37, 0xa0c1e94f 15, 0x3628764a 15, 0x7488d5da 9, 0x2325f175 1); AFeng 0 txs; future1001.ai 0 txs; 0x81c3d1b4 0 txs (quiet again); 0x8e966a9f 0 txs; 0x6ba79dcc/0x89220022/0xda91cefe 0 txs.",
 "method_note": "NO TOTAL OUTAGE this run (google 200 in 4.5s, Ankr 301 in 5.2s ~09:06 WIB; sent pass stalled ~4 min at wallet 22/55 on Ankr latency, same shape as run 133, then completed). Sent pass 55/55 first attempt, 152 in-window txs, max_block 132501972. Receipts via fast_rpc batch (6, ~4s pause) for 102 non-approve candidates: 102 status 1, 0 status 0, 0 NULL (no retry needed), 0 mint logs - thirteenth straight zero-mint run (runs 124-136). fast_rpc RACE eth_call still totally broken (pair retry 8/8 failed, all-endpoints TimeoutError/OSError) - batch vs race paths differ. Paid: 21 tokens; max 3 wallets/token (12 at 3, 5 at 2, 4 at 1); overlap vs run 135: 0 - the churn set itself turned over COMPLETELY again - thirty-third straight run with 0 churn overlap (runs 104-136 also 0). ZERO new rotations - the 27-wallet machine set had 0 txs this run (no buys, no sells, no approvals from any of the 27; verified overlap with active wallets = empty). The named-rotation streak ENDED run 104 (runs 97-103); run 136 has 0, thirty-third straight quiet run. No anomaly to report under the fast-path amendment (no new machine token, no name/symbol appearing, no size anomaly among machine buys, no free-mint path; churn trio PCS buys 37 txs). Trigger >25% NOT met by any token (max 3 wallets = 5.5%). No preview, no execution. Seatbelt 1e9c STALLED at 26: 0 wallets this run (0 buys, 0 sells) - sell-wallet union run101+run102 = 26/27, runs 103-136 add 0 - did NOT reach 27. NOT a new rotation; watch run 137 the same way. Deployments: ZERO - thirty-third straight run without deployments (run 104: 0 through run 136: 0; runs 97-103 had 25/72/64/32/35/70/68) - verified from raw receipts contractAddress fields, not the parsed JSON. Inbound list for run 136 = run135 list (1734) + 0 deployments + 0 new rotation tokens (total 1734, unchanged). 0 plain BNB transfers this run (no empty-input txs). Selectors (sent pass, 152 txs): 50 approvals (0x095ea7b3) + 37 PCS buys (0xb6f9de95) + 39 PCS sells (0x791ac947) + 25 aggregator (0x39ecce49) + 1 aggregator (0x27772d13, 0x2325f175 to 0x296b0019...). NO contract creations, NO transfer 0xa9059cbb, NO sale-call 0x4d819a2a. Nonzero-value txs 50, total 0.06240078 BNB, max 0.06 BNB (0x2325f175 aggregator buy). Most active wallets: 0xc7c5faa2 38, 0xad94ee77 37, 0x38031ca8 37, 0xa0c1e94f 15, 0x3628764a 15, 0x7488d5da 9, 0x2325f175 1. 0 status-0 txs. NOTABLE (receipt-verified, NOT a mint): 0x2325f175 1 tx - aggregator call 0x27772d13 to 0x296b00198dc7ec3410e12da814d9267bb8df506a, 0.06 BNB, 08:28:02 WIB, block 132496533, receipt status 1, 12 logs, bought churn token 0x0aa4f116014fc09490fd4b5766f5c94c6c377777 via PCS swap inside the receipt - NO Transfer from zero address to 0x2325f175, so NOT a mint; same aggregator+selector seen runs 54/61/62 and run 135 (2 calls then). Single-wallet recurring-pattern paid buy (1 entity) - far below thresholds, NOT a signal, NOT a lead, NOT chat-reported (same shape as runs 124-135 silence). AFeng 0 txs this run (was 1 sale-call run 135). INBOUND: residual round 2 DIAGREGASI run ini (run131-inbound-res130-r12..r17.json, run-130 window 132445937-132456148, 300 contracts, 157 logs, 0 hits, 6 Ankr-failed contracts: 0xe2826b50..., 0xe63ae4f9..., 0xfe5ab5ce..., 0xb6c6d00c..., 0x796630c6..., 0xa5d46ed9... - all 'Remote end closed connection', retry later; 0 truncated). Round 3 (r18-r23) DILUNCURKAN detached di akhir run (pids 38739-38744, 6 alive) - run 137 aggregates r18-r23 and launches round 4 (r24-r29) the same detached way. DO NOT relaunch run134-inbound-chain.sh - its wait-loop shape is the dead pattern. Backlog after round 3 launch: residual r24-r30 (7 slices) + run-131/132/133/134/135/136 windows (35 each = 210 slices) = 217 slices. Pair retry 8/8 FAILED again (all eight pairs: a6e6/887c/2bfb/c459/43c8/cfdb/0cf8/e68b - token0()/token1() all 'all endpoints failed' via fast_rpc race, TimeoutError/OSError) - unverified, not absence; 54th consecutive run for a6e6/887c/2bfb/c459, 49th for 43c8, 48th for cfdb/0cf8/e68b; retry run 137. Pointer-discovery (amendment 19:10 WIB, cap 5/run): NO pointer run this run - bridge queue EMPTY (116 contracts: 13 verified / 103 no-pointer / 0 queued) and 0 new contracts this run (0 deployments, 0 new rotation tokens), so nothing to discover. Bridge unchanged. CHAT REPORT this run: NONE (silent) - 0 new mints, no Free Bacot signal, no anomaly, no auto-mint trigger, no guard block. No preview/mint/sign/login/purchase by this job."
}

s["paid_trend_run136"] = ("21 tokens paid-bought; max 3 wallets/token (12 at 3, 5 at 2, 4 at 1); overlap vs run 135: 0 (churn set itself turned over completely, 33rd straight run); "
 "0x81c3d1b4 quiet again (0 txs); future1001.ai 0 txs; 0x8e966a9f 0 txs; 0x6ba79dcc/0x89220022/0xda91cefe 0 txs; "
 "AFeng 0 txs this run (was 1 sale-call run 135); "
 "0x2325f175 1 tx: aggregator 0x27772d13 to 0x296b0019..., 0.06 BNB, bought churn token 0x0aa4f116...7777 via PCS swap in receipt - NOT a mint (no zero-address Transfer), recurring pattern, 1 entity; "
 "sent pass 55/55 first attempt, 152 txs; receipts 102/102 status 1, 0 NULL, no retry needed; "
 "total nonzero value 0.06240078 BNB across 50 txs, max single 0.06 BNB (0x2325f175); "
 "0 plain BNB transfers; 0 deployments (33rd straight run); 0 machine-set activity (33rd straight quiet run); "
 "inbound: residual round 2 aggregated (6 slices, 300 contracts, 157 logs, 0 hits, 6 Ankr-failed to retry, 0 truncated); round 3 (r18-r23) launched detached at end of run - aggregation + round 4 launch by run 137.")

s["inbound_log_leg_run136"] = ("Ankr getLogs address-filtered, RESIDUAL ROUND 2 AGGREGATED this run: "
 "run131-inbound-res130-r12..r17.json, run-130 window 132445937-132456148, 300 contracts of the 1537-contract residual list, 157 logs, 0 hits, 6 failed "
 "(0xe2826b507da79a642aa1fce108aa8dd11ce67e3f, 0xe63ae4f98673d845e6538083ae2562f24a49dfc5, 0xfe5ab5ce9b1d86a55d70e7d0573a14d559029c18, 0xb6c6d00cc059de3f5a84fb5af9ea2ae6abc0dfdf, 0x796630c66a34336edc1daa4baff8d91e4ec1ca41, 0xa5d46ed9d6f19985ad1b71b6bd15fcee01b69ac2 - all Ankr 'Remote end closed connection', retry later), "
 "0 truncated contracts. "
 "Round 3 (r18-r23) launched detached at end of run (pids 38739-38744, 6 alive); run 137 aggregates r18-r23 and launches round 4 (r24-r29) detached. "
 "DO NOT relaunch run134-inbound-chain.sh (wait-loop shape = dead pattern). "
 "Backlog after round 3 launch: residual r24-r30 (7 slices) + run-131/132/133/134/135/136 windows (35 each = 210 slices) = 217 slices. "
 "Inbound list unchanged: 1734 contracts.")

n = s.get("next_run_note", "")
repls = [
 ("Next run sent-tx window starts from block 132494180. RETRY run 136:",
  "Next run sent-tx window starts from block 132501973. RETRY run 137:"),
 ("(unreadable run 88-135, 48 consecutive", "(unreadable run 88-136, 49 consecutive"),
 ("(token0/token1 unreadable run 89-135, 47 consecutive", "(token0/token1 unreadable run 89-136, 48 consecutive"),
 ("0 wallets runs 103-135", "0 wallets runs 103-136"),
 ("0 wallets runs 91-135, 45th quiet run", "0 wallets runs 91-136, 46th quiet run"),
 ("0 wallets runs 90-135, 46th quiet run", "0 wallets runs 90-136, 47th quiet run"),
 ("pair retry 8/8 FAILED again (53rd consecutive run", "pair retry 8/8 FAILED again (54th consecutive run"),
]
for old, new in repls:
    if old in n:
        n = n.replace(old, new, 1)
        print(f"replaced: {old[:60]}...")
    else:
        print(f"NOT FOUND (skipped): {old[:80]}")
n = ("(Run 136: NO TOTAL OUTAGE - google 200 in 4.5s, Ankr 301 in 5.2s; sent pass stalled ~4 min at wallet 22/55 (Ankr latency, same shape as run 133) then 55/55 FIRST ATTEMPT, 0 failed (152 txs, max_block 132501972), receipts 102/102 status 1, 0 NULL, no retry needed, 0 mint logs (thirteenth straight zero-mint run, runs 124-136); "
     "0x2325f175 1 tx - aggregator 0x27772d13, 0.06 BNB, bought churn token 0x0aa4f116...7777 via PCS swap, no zero-address Transfer, NOT a mint (recurring pattern); AFeng 0 txs; value total 0.0624 BNB = single-wallet recurring buy, not a trend; "
     "INBOUND: residual round 2 aggregated (6 slices, 300 contracts, 157 logs, 0 hits, 6 Ankr-failed to retry, 0 truncated); round 3 (r18-r23) launched detached (pids 38739-38744) - run 137 aggregates r18-r23 + launches round 4; DO NOT relaunch run134-inbound-chain.sh. "
     "Paid: 21 tokens, max 3 wallets/token (12/5/4), overlap vs run 135: 0 (33rd straight run); 0 deployments (33rd straight run); 0 machine-set activity (33rd straight quiet run); 1e9c STALLED 26/27; "
     "pair retry 8/8 FAILED again (54th consecutive run a6e6/887c/2bfb/c459) - unverified, retry run 137; NO pointer run - bridge queue EMPTY (116: 13 verified / 103 no-pointer / 0 queued), 0 new contracts; "
     "CHAT REPORT: NONE (silent).) " + n)
s["next_run_note"] = n

json.dump(s, open(STATE, "w"), indent=1)
print("state updated: last_run=136, paid_trend_run136 + inbound_log_leg_run136 added, 0 new reported_findings entries")
print("next window starts 132501973")
print("backup:", NP / "tracked-wallet-mint-scan-state.json.bak-run136-pre")
