#!/usr/bin/env python3
"""Run 140 state update (read-only bookkeeping): last_run + paid_trend_run140 +
inbound_log_leg_run140. No new mints this run, so no new reported_findings
entries. Inbound: run-131 window rounds 1 (s06-s11) and 2 (s12-s17) AGGREGATED
this run; round 3 (s18-s23) launched detached. No preview/mint/sign/login."""
import json, shutil
from pathlib import Path

HOME = Path.home()
NP = HOME / "workspace/narrative-pulse"
STATE = NP / "tracked-wallet-mint-scan-state.json"
shutil.copy(STATE, NP / "tracked-wallet-mint-scan-state.json.bak-run140-pre")
s = json.load(open(STATE))

s["last_run"] = {
 "run": 140,
 "block_start": 132526590,
 "block_end": 132534898,
 "window_wib": "2026-11-09 12:13:33 - 13:15:51 WIB (tx times); run executed ~13:05 WIB - ~13:35 WIB; sent-pass in-window txs 201, 0 mint-pattern txs",
 "wallets_checked": "55/55 OK via Ankr module (54/55 first attempt; 1 FAILED first attempt: 0xdb2d83f907965fb05ac23b8d40d3a327fc9ea52b - 'Remote end closed connection' in sent pass - RETRY OK, 0 in-window txs; run-139 failed wallet 0x4522e661d9c94ec54b37e71896351a7440ec4f07 VERIFIED OK this run, 0 in-window txs). 8 wallets active (0xad94ee77 44, 0xc7c5faa2 38, 0x38031ca8 38, 0xa0c1e94f 21, 0x81c3d1b4 19, 0x3628764a 16, AFeng 0xbf004bff 16, 0x7488d5da 9); 0x2325f175 0 txs; 0x8e966a9f 0 txs; 0x6ba79dcc/0x89220022/0xda91cefe 0 txs.",
 "method_note": "NO TOTAL OUTAGE this run (google 200 in 9.1s, Ankr 200 in 14.4s, slow network; fast_rpc RACE path still totally broken - pair retry all-endpoints TimeoutError/OSError, same known quirk, NOT an outage). Sent pass stalled at wallet 23/55 (0xdb2d83f9, Ankr 'Remote end closed connection', same shape as runs 133/136/139) then completed; 54/55 first attempt + 1 retry OK (0xdb2d83f9, 0 in-window txs), 201 in-window txs, max_block 132534898. Receipts via fast_rpc batch (6, ~4s pause) for 128 non-approve candidates: 128 status 1, 0 status 0, 0 NULL (no retry needed), 0 mint logs - seventeenth straight zero-mint run (runs 124-140). Paid: 30 tokens; max 3 wallets/token (13 at 3, 6 at 2, 11 at 1); paid-set overlap vs run 139: 1 - token 0x0c6302401aa5325c2e36f170f52c00b1d220b405, AFeng-only in BOTH runs (AFeng buying it again via the known sale contract - NOT churn, NOT a signal); churn (...7777) overlap vs run 139: 0 - the churn set itself turned over COMPLETELY again - thirty-seventh straight run with 0 churn overlap (runs 104-140). ZERO new rotations - the 27-wallet machine set had 0 txs this run (no buys, no sells, no approvals from any of the 27; verified overlap with active wallets = empty; no paid token touches the machine set). The named-rotation streak ENDED run 104 (runs 97-103); run 140 has 0, thirty-seventh straight quiet run. No anomaly to report under the fast-path amendment (no new machine token, no name/symbol appearing, no size anomaly among machine buys, no free-mint path; churn trio PCS buys 42 txs). Trigger >25% NOT met by any token (max 3 wallets = 5.5%). No preview, no execution. Seatbelt 1e9c STALLED at 26: 0 wallets this run (0 buys, 0 sells) - sell-wallet union run101+run102 = 26/27, runs 103-140 add 0 - did NOT reach 27. NOT a new rotation; watch run 141 the same way. Deployments: ZERO - thirty-seventh straight run without deployments (run 104: 0 through run 140: 0; runs 97-103 had 25/72/64/32/35/70/68) - verified from raw receipts contractAddress fields + sent to-None, not the parsed JSON. Inbound list for run 140 = run139 list (1734) + 0 deployments + 0 new rotation tokens (total 1734, unchanged). NOTABLE NON-MINT (receipt-verified, NOT a mint/buy/signal): AFeng (0xbf004bff) 16 txs - 11 sale-calls 0x4d819a2a to the KNOWN sale contract 0x1de460f363af910f51726def188f9004276bf4bc (5.3 + 2.3 + 1.2 + 0.5 + 0.5 + 0.15 = 9.95 BNB; 12:21:24-13:15:51 WIB; blocks 132527641-132534898), buying 4 tokens in the paid map (0x0c6302401aa5325c2e36f170f52c00b1d220b405, 0x205812cd..., 0xa184d5ad..., 0x36551d9a... + others in logs) - each 1 wallet (AFeng only), all receipt status 1, 0 mint logs, same contract+selector pattern as runs 54-63/70/135/139 - 1 entity, far below thresholds, NOT a signal, NOT reported to chat. Plus 5 AFeng approvals (16 total - 11 sale-calls). 0x81c3d1b4 BACK after 0 txs in runs 135-139: 19 txs - 9 aggregator 0x27772d13 calls to known aggregator 0x296b00198dc7ec3410e12da814d9267bb8df506a (12:31:48-12:48:01 WIB) + 1 token transfer 0xa9059cbb to 0xba300df4c929eb137e266d17d1fe6db058837777 (12:55:19 WIB) + 9 approvals - recurring aggregator pattern, 1 entity, not a signal, NOT reported to chat. 0x2325f175: 0 txs this run. Plain BNB transfers this run: 2 (0xa0c1e94f -> 0xe322fc6ddb 0.01129 BNB, 12:44:19 WIB; 0xc7c5faa2 -> 0x7f51d46423 0.00055 BNB, 13:10:53 WIB) - small fund moves, recurring pattern, not buys. Selectors (sent pass, 201 txs): 73 approvals (0x095ea7b3) + 42 PCS buys (0xb6f9de95) + 32 PCS sells (0x791ac947) + 31 aggregator (0x39ecce49, all 0x38031ca8) + 11 sale-call 0x4d819a2a (AFeng) + 9 aggregator 0x27772d13 (0x81c3d1b4) + 2 empty-input + 1 transfer 0xa9059cbb (0x81c3d1b4). NO contract creations. Nonzero-value txs 63, total 9.96618086 BNB, max 5.3 BNB (AFeng sale-call); largest buy 5.3 BNB (AFeng sale-call). Most active wallets: 0xad94ee77 44, 0xc7c5faa2 38, 0x38031ca8 38, 0xa0c1e94f 21, 0x81c3d1b4 19, 0x3628764a 16, AFeng 16, 0x7488d5da 9. 0 status-0 txs. INBOUND: run-131 window round 1 (s06-s11) AGGREGATED this run (run131-inbound-s06..s11.json, window 132456149-132466646, 300 contracts, 5464 logs, 0 hits, 17 Ankr-failed contracts: 0x5189eaeb..., 0x53a3d78f..., 0x53ba2951..., 0x5606c2d7..., 0x5bb425ad..., 0x60b92624..., 0x6810056d..., 0x76439992..., 0x77e38295..., 0x78f37795..., 0x83485fdd..., 0x84f7747b..., 0x857169cd..., 0x885ffc03..., 0x8f8705a9..., 0x926504d1..., 0x942c19a8... - all 'Remote end closed connection', retry later; 4 truncated, all resolved topic-filtered 0 logs: 0x55d398326f99059ff775485246999027b3197955, 0x63dea5acdbe1f27c968907d08610a5f0a0284ba6, 0x78573ab46e5436e126d3ea1fdef8766cce4efd2b, 0x7e2da878217eb995f9e5d36ed32c9cea52442681). Round 2 (s12-s17) AGGREGATED this run (run131-inbound-s12..s17.json, same window, 300 contracts, 716 logs, 0 hits, 7 Ankr-failed: 0xa8e36d37..., 0xb7dce041..., 0xbf0ea868..., 0xc180b8bf..., 0xc433a98b..., 0xcd355d11..., 0xd697bb3e... - all 'Remote end closed connection', retry later; 0 truncated). Round 3 (s18-s23, contracts 900-1200, same window) LAUNCHED detached at end of run (pids 34723-34733, 6 alive) - aggregation + round 4 launch by run 141. DO NOT relaunch run134-inbound-chain.sh - its wait-loop shape is the dead pattern. Backlog after round 3 launch: run-131 window s24-s34 (11 slices) + run-132/133/134/135/136/137/138/139 windows (35 each = 280 slices) = 291 slices. Pair retry 8/8 FAILED again (all eight pairs: a6e6/887c/2bfb/c459/43c8/cfdb/0cf8/e68b - token0()/token1() all 'all endpoints failed' via fast_rpc race, TimeoutError/OSError; 0cf8 token1 garbage '0x0x' again) - unverified, not absence; 58th consecutive run for a6e6/887c/2bfb/c459, 53rd for 43c8, 52nd for cfdb/0cf8/e68b; retry run 141. Pointer-discovery (amendment 19:10 WIB, cap 5/run): NO pointer run this run - bridge queue EMPTY (116 contracts: 13 verified / 103 no-pointer / 0 queued) and 0 new contracts this run (0 deployments, 0 new rotation tokens), so nothing to discover. Bridge unchanged. CHAT REPORT this run: NONE (silent) - 0 new mints, no Free Bacot signal, no anomaly, no auto-mint trigger, no guard block. No preview/mint/sign/login/purchase by this job."
}

s["paid_trend_run140"] = ("30 tokens paid-bought; max 3 wallets/token (13 at 3, 6 at 2, 11 at 1); paid-set overlap vs run 139: 1 - token 0x0c630240... (AFeng-only in BOTH runs, continuation of AFeng buying via known sale contract, NOT churn); churn (...7777) overlap vs run 139: 0 (churn set itself turned over completely, 37th straight run); "
 "0x81c3d1b4 BACK after 0 txs runs 135-139 - 19 txs: 9 aggregator calls to known 0x296b0019... + 1 token transfer to 0xba300df4...7777 + 9 approvals - receipt-verified, 1 entity, NOT a mint/signal, not reported to chat; "
 "AFeng 16 txs: 11 sale-calls to KNOWN sale contract 0x1de460f3... (9.95 BNB total, buys 4 tokens in paid map, each 1 wallet) + 5 approvals - receipt-verified, 1 entity, NOT a mint/signal, not reported to chat; "
 "0x2325f175 0 txs; 0x8e966a9f 0 txs; 0x6ba79dcc/0x89220022/0xda91cefe 0 txs; "
 "sent pass 54/55 first attempt + 1 retry OK (0xdb2d83f9, 0 in-window txs; run-139 failed wallet 0x4522e661 VERIFIED OK, 0 in-window txs), 201 txs; receipts 128/128 status 1, 0 NULL, no retry needed; "
 "total nonzero value 9.96618086 BNB across 63 txs, max single 5.3 BNB (AFeng sale-call); "
 "2 plain BNB transfers (0.01129 BNB 0xa0c1e94f -> 0xe322fc6ddb; 0.00055 BNB 0xc7c5faa2 -> 0x7f51d46423); 0 deployments (37th straight run); 0 machine-set activity (37th straight quiet run); "
 "inbound: run-131 window rounds 1+2 aggregated (600 contracts, 6180 logs, 0 hits, 24 Ankr-failed to retry, 4 truncated resolved 0 logs); round 3 (s18-s23) launched detached - aggregation + round 4 launch by run 141.")

s["inbound_log_leg_run140"] = ("Ankr getLogs address-filtered, RUN-131 WINDOW ROUNDS 1+2 AGGREGATED this run: "
 "round 1 run131-inbound-s06..s11.json, window 132456149-132466646, 300 contracts, 5464 logs, 0 hits, 17 failed "
 "(0x5189eaeb67d2a799cd9094aec4af6eb76c6e073b, 0x53a3d78ff23d9c9cb14ae8b2fd168a44391b2010, 0x53ba295180ae4b730f9b2a031f77c1bcdb009509, 0x5606c2d70e390dd0ec0b0c3079d567063fad415c, 0x5bb425ad2069de77abc8c341d4d322bcff26c550, 0x60b9262456de011f7d15a54cdd8c48baaa8b022f, 0x6810056d235c949f425b394de590835096dd6adc, 0x76439992cce24651080040a6f9c62eb6387ae672, 0x77e38295603a06654a6ed3ed0849e6aa50749963, 0x78f377952bd84383dd226148ab8093fc0f7ecdfd, 0x83485fdd9a30757eff74f5a43afc8fd2efbeaab1, 0x84f7747b0a8dfaf636b06087c635ecb7a2a49791, 0x857169cde48cf9fd8874e26a43fbbca838fc56a1, 0x885ffc03f68d444e8d33da81c4a8b37349f6c481, 0x8f8705a91cb8af615ce35179b0d33200ade71dab, 0x926504d174e99db699141049b3dd94df501ff813, 0x942c19a87a77b062d94c452ed8fac6162aff45ad - all Ankr 'Remote end closed connection', retry later), "
 "4 truncated (0x55d398326f99059ff775485246999027b3197955, 0x63dea5acdbe1f27c968907d08610a5f0a0284ba6, 0x78573ab46e5436e126d3ea1fdef8766cce4efd2b, 0x7e2da878217eb995f9e5d36ed32c9cea52442681 - all topic-filtered 0 logs, 0 hits); "
 "round 2 run131-inbound-s12..s17.json, same window, 300 contracts, 716 logs, 0 hits, 7 failed "
 "(0xa8e36d374de1cb2664d4631e7035481ad3b4a877, 0xb7dce0412bb89de075413855875d1db31ac89e8f, 0xbf0ea868de36dc3a5fffbf45018694398b7a22f5, 0xc180b8bffdd65531f4bae6ac7586cfb192164a9b, 0xc433a98bcccc90556de112742ba97ffea7882fcc, 0xcd355d1191ce9849b3a935c821a66d9df37cfe77, 0xd697bb3e5d19d56b4575ee4bf77033ef26093e14 - all Ankr 'Remote end closed connection', retry later), "
 "0 truncated. "
 "Round 3 (s18-s23, contracts 900-1200, same window) launched detached at end of run (pids 34723-34733, 6 alive); run 141 aggregates s18-s23 + launches round 4 (s24-s29). "
 "DO NOT relaunch run134-inbound-chain.sh (wait-loop shape = dead pattern). "
 "Backlog after round 3 launch: run-131 window s24-s34 (11 slices) + run-132/133/134/135/136/137/138/139 windows (35 each = 280 slices) = 291 slices. "
 "Inbound list unchanged: 1734 contracts.")

n = s.get("next_run_note", "")
repls = [
 ("Next run sent-tx window starts from block 132518601. RETRY run 139:",
  "Next run sent-tx window starts from block 132534899. RETRY run 141:"),
 ("(unreadable run 88-139, 52 consecutive", "(unreadable run 88-140, 53 consecutive"),
 ("(token0/token1 unreadable run 89-139, 51 consecutive", "(token0/token1 unreadable run 89-140, 52 consecutive"),
 ("0 wallets runs 103-139", "0 wallets runs 103-140"),
 ("0 wallets runs 91-139, 49th quiet run", "0 wallets runs 91-140, 50th quiet run"),
 ("0 wallets runs 90-139, 50th quiet run", "0 wallets runs 90-140, 51st quiet run"),
 ("pair retry 8/8 FAILED again (57th consecutive run", "pair retry 8/8 FAILED again (58th consecutive run"),
]
for old, new in repls:
    if old in n:
        n = n.replace(old, new, 1)
        print(f"replaced: {old[:60]}...")
    else:
        print(f"NOT FOUND (skipped): {old[:80]}")
n = ("(Run 140: NO TOTAL OUTAGE - google 200 in 9.1s, Ankr 200 in 14.4s (slow network); sent pass stalled at wallet 23/55 (0xdb2d83f9, Ankr 'Remote end closed connection', same shape as runs 133/136/139) then completed; 54/55 first attempt + 1 retry OK (0xdb2d83f9, 0 in-window txs; run-139 failed wallet 0x4522e661 VERIFIED OK, 0 in-window txs), 201 txs, max_block 132534898, receipts 128/128 status 1, 0 NULL, no retry needed, 0 mint logs (seventeenth straight zero-mint run, runs 124-140); "
     "AFeng 16 txs - 11 sale-calls to KNOWN sale contract 0x1de460f3... (9.95 BNB, 4 tokens, 1 wallet each) + 5 approvals - receipt-verified, NOT a mint/signal; 0x81c3d1b4 BACK after 0 txs runs 135-139 (19 txs: 9 aggregator calls to known 0x296b0019... + 1 token transfer + 9 approvals) - receipt-verified, NOT a mint/signal; 0x2325f175 0 txs; value total 9.96618 BNB, max 5.3 BNB (AFeng sale-call); "
     "INBOUND: run-131 window rounds 1+2 aggregated (600 contracts, 6180 logs, 0 hits, 24 Ankr-failed to retry, 4 truncated resolved 0 logs); round 3 (s18-s23) launched detached (pids 34723-34733) - run 141 aggregates s18-s23 + launches round 4 (s24-s29); DO NOT relaunch run134-inbound-chain.sh. "
     "Paid: 30 tokens, max 3 wallets/token (13/6/11), paid-set overlap vs run 139: 1 (AFeng-only 0x0c630240, NOT churn); churn overlap 0 (37th straight run); 0 deployments (37th straight run); 0 machine-set activity (37th straight quiet run); 1e9c STALLED 26/27; "
     "pair retry 8/8 FAILED again (58th consecutive run a6e6/887c/2bfb/c459) - unverified, retry run 141; NO pointer run - bridge queue EMPTY (116: 13 verified / 103 no-pointer / 0 queued), 0 new contracts; "
     "CHAT REPORT: NONE (silent).) " + n)
s["next_run_note"] = n

json.dump(s, open(STATE, "w"), indent=1)
print("state updated: last_run=140, paid_trend_run140 + inbound_log_leg_run140 added, 0 new reported_findings entries")
print("next window starts 132534899")
print("backup:", NP / "tracked-wallet-mint-scan-state.json.bak-run140-pre")
