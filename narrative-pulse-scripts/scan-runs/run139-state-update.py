#!/usr/bin/env python3
"""Run 139 state update (read-only bookkeeping): last_run + paid_trend_run139 +
inbound_log_leg_run139. No new mints this run, so no new reported_findings
entries. Inbound: run-131 window round 0 (s00-s05) AGGREGATED this run (relaunched
after run-138's launch died mid-run - relative-path cwd quirk, fixed with absolute
paths); round 1 (s06-s11) launched detached. No preview/mint/sign/login."""
import json, shutil
from pathlib import Path

HOME = Path.home()
NP = HOME / "workspace/narrative-pulse"
STATE = NP / "tracked-wallet-mint-scan-state.json"
shutil.copy(STATE, NP / "tracked-wallet-mint-scan-state.json.bak-run139-pre")
s = json.load(open(STATE))

s["last_run"] = {
 "run": 139,
 "block_start": 132518601,
 "block_end": 132526589,
 "window_wib": "2026-11-09 11:15:00 - 12:13:31 WIB (tx times); run executed ~12:05 WIB - ~12:35 WIB; sent-pass in-window txs 155, 0 mint-pattern txs",
 "wallets_checked": "54/55 OK via Ankr module (54/55 first attempt; 1 FAILED both attempts: 0x4522e661d9c94ec54b37e71896351a7440ec4f07 - 'Remote end closed connection' in sent pass AND in retry - activity UNVERIFIED this run, retry run 140, do NOT report 0 txs for it). 8 wallets active (0xc7c5faa2 33, 0xad94ee77 33, 0x38031ca8 33, 0x3628764a 15, 0xa0c1e94f 15, 0x7488d5da 15, AFeng 0xbf004bff 8, 0x2325f175 3); 0x81c3d1b4 0 txs (quiet again); 0x8e966a9f 0 txs; 0x6ba79dcc/0x89220022/0xda91cefe 0 txs.",
 "method_note": "NO TOTAL OUTAGE this run (google 000 once, 15s timeout, slow network; Ankr 301 in 13.3s; fast_rpc RACE path still totally broken - block-number race + pair retry all-endpoints TimeoutError, same known quirk, NOT an outage). Sent pass stalled ~4 min at wallet 23/55 (0xdb2d83f9, Ankr latency, same shape as runs 133/136) then completed; 54/55 first attempt + 1 failed wallet 0x4522e661 (retry ALSO failed 'Remote end closed connection' - UNVERIFIED, retry run 140), 155 in-window txs, max_block 132526589. Receipts via fast_rpc batch (6, ~4s pause) for 105 non-approve candidates: 105 status 1, 0 status 0, 0 NULL (no retry needed), 0 mint logs - sixteenth straight zero-mint run (runs 124-139). fast_rpc RACE eth_call still totally broken (pair retry 8/8 failed, all-endpoints TimeoutError/OSError) - batch vs race paths differ. Paid: 25 tokens; max 3 wallets/token (11 at 3, 5 at 2, 9 at 1); overlap vs run 138: 0 - the churn set itself turned over COMPLETELY again - thirty-sixth straight run with 0 churn overlap (runs 104-139 also 0). ZERO new rotations - the 27-wallet machine set had 0 txs this run (no buys, no sells, no approvals from any of the 27; verified overlap with active wallets = empty; no paid token touches the machine set). The named-rotation streak ENDED run 104 (runs 97-103); run 139 has 0, thirty-sixth straight quiet run. No anomaly to report under the fast-path amendment (no new machine token, no name/symbol appearing, no size anomaly among machine buys, no free-mint path; churn trio PCS buys 37 txs). Trigger >25% NOT met by any token (max 3 wallets = 5.5%). No preview, no execution. Seatbelt 1e9c STALLED at 26: 0 wallets this run (0 buys, 0 sells) - sell-wallet union run101+run102 = 26/27, runs 103-139 add 0 - did NOT reach 27. NOT a new rotation; watch run 140 the same way. Deployments: ZERO - thirty-sixth straight run without deployments (run 104: 0 through run 139: 0; runs 97-103 had 25/72/64/32/35/70/68) - verified from raw receipts contractAddress fields + sent to-None, not the parsed JSON. Inbound list for run 139 = run138 list (1734) + 0 deployments + 0 new rotation tokens (total 1734, unchanged). NOTABLE NON-MINT (receipt-verified, NOT a mint/buy/signal): AFeng (0xbf004bff, 0 txs runs 137-138) BACK with 8 txs - 5 sale-calls 0x4d819a2a to the KNOWN sale contract 0x1de460f363af910f51726def188f9004276bf4bc (5.3 + 0 + 1.2 + 13.0 + 2.3 = 21.8 BNB; 12:02:07, 12:09:40, 12:11:03, 12:12:17, 12:13:31 WIB; blocks 132525069-132526589), buying 3 tokens (0x0c6302401aa5325c2e36f170f52c00b1d220b405 in 4 calls, 0x6b2ce31a577d92f73516c7a91febc7672247e694 in 2, 0xdd806e436dda5588bf54061c11590c77ddc87777 in 1) - each 1 wallet (AFeng only), all receipt status 1, 0 mint logs, same contract+selector pattern as runs 54-63/70/135 - 1 entity, far below thresholds, NOT a signal, NOT reported to chat. Plus 2 AFeng self-transfers (empty-input, to own address): 55.02322168 BNB (0x624afe6b79c8, 12:03:54 WIB) + 0.000000001 BNB dust (0x71a6ea68c2ac, 12:06:02 WIB) - fund moves within own wallet, not buys. 0x2325f175: 3 txs - 2 aggregator 0x27772d13 to known aggregator 0x296b00198dc7ec3410e12da814d9267bb8df506a (0.1 + 0 BNB, 11:24:15 + 11:25:17 WIB) + 1 approval - recurring pattern, 1 entity, not a signal. Plain BNB transfers this run: 2 (both AFeng self-transfers above). Selectors (sent pass, 155 txs): 50 approvals (0x095ea7b3) + 37 PCS buys (0xb6f9de95) + 37 PCS sells (0x791ac947) + 22 aggregator (0x39ecce49, all 0x38031ca8) + 5 sale-call 0x4d819a2a (AFeng) + 2 aggregator 0x27772d13 (0x2325f175) + 2 empty-input (AFeng self). NO contract creations, NO transfer (0xa9059cbb). Nonzero-value txs 55, total 76.92571206 BNB, max 55.02322168 BNB (AFeng self-transfer, not a buy); largest buy 13.0 BNB (AFeng sale-call). Most active wallets: 0xc7c5faa2 33, 0xad94ee77 33, 0x38031ca8 33, 0x3628764a 15, 0xa0c1e94f 15, 0x7488d5da 15, AFeng 8, 0x2325f175 3. 0 status-0 txs. INBOUND: run-131 window round 0 (s00-s05) AGGREGATED this run (run131-inbound-s00..s05.json, window 132456149-132466646, 300 contracts, 1850 logs, 0 hits, 9 Ankr-failed contracts: 0x1a7a8bbb49e3e8cf951996789fd69d4c7524a2b4, 0x1bb3701da38d1572984cd200821d1162d6783435, 0x265b2a6b32045af53d142f4e32123b28b0df4d7c, 0x28a38a372639e8c481ad41b9b16e52c3c6366acc, 0x2fb4598cc4c0758d9a541cae813e81f0b138024a, 0x3611455be1fc2c6987fe9d016971b7e40b341684, 0x37d39fcc21addbb753e9366216e494d7956bd859, 0x3ebbed7de6afa9dcc0078a993c581fb50ada5693, 0x493b6bd3fd88de1d86ce0dea45168d2ef8182caa - all 'Remote end closed connection', retry later; 1 truncated: 0x1de460f363af910f51726def188f9004276bf4bc topic-filtered 0 logs, 0 hits). Round 0 was RELAUNCHED this run after run-138's launch died mid-run (relative-path cwd quirk: setsid children resolved script/log paths against /home/hatch - 6 stray error logs at /home/hatch/run131-inbound-s0*.log; fixed with absolute paths; the 6 relaunched slices all completed). Round 1 (s06-s11, contracts 300-600, same window) LAUNCHED detached at end of run (pids 17419-17429, 6 alive) - aggregation + round 2 launch by run 140. DO NOT relaunch run134-inbound-chain.sh - its wait-loop shape is the dead pattern. Backlog after round 1 launch: run-131 window s12-s34 (23 slices) + run-132/133/134/135/136/137/138 windows (35 each = 245 slices) = 268 slices. Pair retry 8/8 FAILED again (all eight pairs: a6e6/887c/2bfb/c459/43c8/cfdb/0cf8/e68b - token0()/token1() all 'all endpoints failed' via fast_rpc race, TimeoutError/OSError; 0cf8 token1 garbage '0x0x' again) - unverified, not absence; 57th consecutive run for a6e6/887c/2bfb/c459, 52nd for 43c8, 51st for cfdb/0cf8/e68b; retry run 140. Pointer-discovery (amendment 19:10 WIB, cap 5/run): NO pointer run this run - bridge queue EMPTY (116 contracts: 13 verified / 103 no-pointer / 0 queued) and 0 new contracts this run (0 deployments, 0 new rotation tokens), so nothing to discover. Bridge unchanged. CHAT REPORT this run: NONE (silent) - 0 new mints, no Free Bacot signal, no anomaly, no auto-mint trigger, no guard block. No preview/mint/sign/login/purchase by this job."
}

s["paid_trend_run139"] = ("25 tokens paid-bought; max 3 wallets/token (11 at 3, 5 at 2, 9 at 1); overlap vs run 138: 0 (churn set itself turned over completely, 36th straight run); "
 "0x81c3d1b4 quiet again (0 txs); future1001.ai 0 txs; 0x8e966a9f 0 txs; 0x6ba79dcc/0x89220022/0xda91cefe 0 txs; "
 "AFeng BACK after 2 quiet runs (runs 137-138: 0 txs) - 8 txs: 5 sale-calls to KNOWN sale contract 0x1de460f3... (21.8 BNB total, buys 3 tokens, each 1 wallet) + 2 self-transfers (55.02 BNB + dust) - receipt-verified, 1 entity, NOT a mint/signal, not reported to chat; "
 "0x2325f175 3 txs (2 aggregator buys to known 0x296b0019... + 1 approval, recurring pattern); "
 "sent pass 54/55 first attempt + 1 FAILED wallet 0x4522e661 (retry ALSO failed 'Remote end closed connection' - UNVERIFIED, retry run 140), 155 txs; receipts 105/105 status 1, 0 NULL, no retry needed; "
 "total nonzero value 76.92571206 BNB across 55 txs, max single 55.02 BNB (AFeng self-transfer, not a buy); largest buy 13.0 BNB (AFeng sale-call); "
 "2 plain BNB transfers (both AFeng self); 0 deployments (36th straight run); 0 machine-set activity (36th straight quiet run); "
 "inbound: run-131 window round 0 aggregated (6 slices, 300 contracts, 1850 logs, 0 hits, 9 Ankr-failed to retry, 1 truncated resolved 0 logs); round 1 (s06-s11) launched detached - aggregation + round 2 launch by run 140.")

s["inbound_log_leg_run139"] = ("Ankr getLogs address-filtered, RUN-131 WINDOW ROUND 0 AGGREGATED this run: "
 "run131-inbound-s00..s05.json, window 132456149-132466646, 300 contracts, 1850 logs, 0 hits, 9 failed "
 "(0x1a7a8bbb49e3e8cf951996789fd69d4c7524a2b4, 0x1bb3701da38d1572984cd200821d1162d6783435, 0x265b2a6b32045af53d142f4e32123b28b0df4d7c, 0x28a38a372639e8c481ad41b9b16e52c3c6366acc, 0x2fb4598cc4c0758d9a541cae813e81f0b138024a, 0x3611455be1fc2c6987fe9d016971b7e40b341684, 0x37d39fcc21addbb753e9366216e494d7956bd859, 0x3ebbed7de6afa9dcc0078a993c581fb50ada5693, 0x493b6bd3fd88de1d86ce0dea45168d2ef8182caa - all Ankr 'Remote end closed connection', retry later), "
 "1 truncated (0x1de460f363af910f51726def188f9004276bf4bc: topic-filtered 0 logs, 0 hits). "
 "Round 0 was RELAUNCHED this run after run-138's launch died mid-run (relative-path cwd quirk in setsid children - fixed with absolute paths). "
 "Round 1 (s06-s11, contracts 300-600, same window) launched detached at end of run (pids 17419-17429, 6 alive); run 140 aggregates s06-s11 + launches round 2 (s12-s17). "
 "DO NOT relaunch run134-inbound-chain.sh (wait-loop shape = dead pattern). "
 "Backlog after round 1 launch: run-131 window s12-s34 (23 slices) + run-132/133/134/135/136/137/138 windows (35 each = 245 slices) = 268 slices. "
 "Inbound list unchanged: 1734 contracts.")

n = s.get("next_run_note", "")
repls = [
 ("Next run sent-tx window starts from block 132518601. RETRY run 139:",
  "Next run sent-tx window starts from block 132526590. RETRY run 140:"),
 ("(unreadable run 88-138, 51 consecutive", "(unreadable run 88-139, 52 consecutive"),
 ("(token0/token1 unreadable run 89-138, 50 consecutive", "(token0/token1 unreadable run 89-139, 51 consecutive"),
 ("0 wallets runs 103-138", "0 wallets runs 103-139"),
 ("0 wallets runs 91-138, 48th quiet run", "0 wallets runs 91-139, 49th quiet run"),
 ("0 wallets runs 90-138, 49th quiet run", "0 wallets runs 90-139, 50th quiet run"),
 ("pair retry 8/8 FAILED again (56th consecutive run", "pair retry 8/8 FAILED again (57th consecutive run"),
]
for old, new in repls:
    if old in n:
        n = n.replace(old, new, 1)
        print(f"replaced: {old[:60]}...")
    else:
        print(f"NOT FOUND (skipped): {old[:80]}")
n = ("(Run 139: NO TOTAL OUTAGE - google 000 once (15s timeout, slow), Ankr 301 in 13.3s; sent pass stalled ~4 min at wallet 23/55 (0xdb2d83f9, Ankr latency, same shape as runs 133/136) then completed; 54/55 first attempt + 1 FAILED wallet 0x4522e661 (retry ALSO failed 'Remote end closed connection' - UNVERIFIED, retry run 140), 155 txs, max_block 132526589, receipts 105/105 status 1, 0 NULL, no retry needed, 0 mint logs (sixteenth straight zero-mint run, runs 124-139); "
     "AFeng BACK after 2 quiet runs - 5 sale-calls to KNOWN sale contract 0x1de460f3... (21.8 BNB, 3 tokens, 1 wallet each) + 2 self-transfers (55.02 BNB + dust) - receipt-verified, NOT a mint/signal; 0x2325f175 3 txs (recurring aggregator pattern); value total 76.92571 BNB, max 55.02 BNB (AFeng self-transfer, not a buy); "
     "INBOUND: run-131 window round 0 aggregated (6 slices, 300 contracts, 1850 logs, 0 hits, 9 Ankr-failed to retry, 1 truncated resolved 0 logs); round 1 (s06-s11) launched detached (pids 17419-17429) - run 140 aggregates s06-s11 + launches round 2 (s12-s17); DO NOT relaunch run134-inbound-chain.sh. "
     "Paid: 25 tokens, max 3 wallets/token (11/5/9), overlap vs run 138: 0 (36th straight run); 0 deployments (36th straight run); 0 machine-set activity (36th straight quiet run); 1e9c STALLED 26/27; "
     "pair retry 8/8 FAILED again (57th consecutive run a6e6/887c/2bfb/c459) - unverified, retry run 140; NO pointer run - bridge queue EMPTY (116: 13 verified / 103 no-pointer / 0 queued), 0 new contracts; "
     "CHAT REPORT: NONE (silent).) " + n)
s["next_run_note"] = n

json.dump(s, open(STATE, "w"), indent=1)
print("state updated: last_run=139, paid_trend_run139 + inbound_log_leg_run139 added, 0 new reported_findings entries")
print("next window starts 132526590")
print("backup:", NP / "tracked-wallet-mint-scan-state.json.bak-run139-pre")
