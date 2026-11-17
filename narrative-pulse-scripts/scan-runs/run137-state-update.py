#!/usr/bin/env python3
"""Run 137 state update (read-only bookkeeping): last_run + paid_trend_run137 +
inbound_log_leg_run137. No new mints this run, so no new reported_findings
entries. Inbound: residual round 3 (r18-r23) AGGREGATED this run (6 slices,
300 contracts, 0 logs, 0 hits); round 4 (r24-r29) launched detached.
0x2325f175 0 txs this run (was 1 aggregator buy run 136); AFeng 0 txs.
No preview/mint/sign/login."""
import json, shutil
from pathlib import Path

HOME = Path.home()
NP = HOME / "workspace/narrative-pulse"
STATE = NP / "tracked-wallet-mint-scan-state.json"
shutil.copy(STATE, NP / "tracked-wallet-mint-scan-state.json.bak-run137-pre")
s = json.load(open(STATE))

s["last_run"] = {
 "run": 137,
 "block_start": 132501973,
 "block_end": 132509888,
 "window_wib": "2026-11-09 09:09:48 - 10:08:12 WIB (tx times); run executed ~10:05 WIB - ~10:21 WIB; sent-pass in-window txs 146, 0 mint-pattern txs",
 "wallets_checked": "55/55 via Ankr module (54/55 first attempt + 1 retry OK: 0x5b4beded 'Remote end closed connection', 0 in-window txs on retry). 6 wallets active (0xad94ee77 35, 0x38031ca8 35, 0xc7c5faa2 34, 0x3628764a 15, 0xa0c1e94f 15, 0x7488d5da 12); AFeng 0 txs; future1001.ai 0 txs; 0x81c3d1b4 0 txs (quiet again); 0x8e966a9f 0 txs; 0x6ba79dcc/0x89220022/0xda91cefe 0 txs; 0x2325f175 0 txs (was 1 aggregator buy run 136).",
 "method_note": "NO TOTAL OUTAGE this run (google 000 + Ankr 000 at ~10:06 WIB, both 15s timeouts - slow network, same shape as run 135's single google 000; sent pass still completed 55/55, so NOT an outage). Sent pass 54/55 first attempt + 1 retry OK (0x5b4beded, 0 in-window txs), 146 in-window txs, max_block 132509888. Receipts via fast_rpc batch (6, ~4s pause) for 97 non-approve candidates: 97 status 1, 0 status 0, 0 NULL (no retry needed), 0 mint logs - fourteenth straight zero-mint run (runs 124-137). fast_rpc RACE eth_call still totally broken (pair retry 8/8 failed, all-endpoints TimeoutError/OSError; 0cf8 token0/token1 returned garbage '0x0x' again) - batch vs race paths differ. Paid: 21 tokens; max 3 wallets/token (12 at 3, 5 at 2, 4 at 1); overlap vs run 136: 0 - the churn set itself turned over COMPLETELY again - thirty-fourth straight run with 0 churn overlap (runs 104-137 also 0). ZERO new rotations - the 27-wallet machine set had 0 txs this run (no buys, no sells, no approvals from any of the 27; verified overlap with active wallets = empty). The named-rotation streak ENDED run 104 (runs 97-103); run 137 has 0, thirty-fourth straight quiet run. No anomaly to report under the fast-path amendment (no new machine token, no name/symbol appearing, no size anomaly among machine buys, no free-mint path; churn trio PCS buys 38 txs). Trigger >25% NOT met by any token (max 3 wallets = 5.5%). No preview, no execution. Seatbelt 1e9c STALLED at 26: 0 wallets this run (0 buys, 0 sells) - sell-wallet union run101+run102 = 26/27, runs 103-137 add 0 - did NOT reach 27. NOT a new rotation; watch run 138 the same way. Deployments: ZERO - thirty-fourth straight run without deployments (run 104: 0 through run 137: 0; runs 97-103 had 25/72/64/32/35/70/68) - verified from raw receipts contractAddress fields, not the parsed JSON. Inbound list for run 137 = run136 list (1734) + 0 deployments + 0 new rotation tokens (total 1734, unchanged). 0 plain BNB transfers this run (no empty-input txs). Selectors (sent pass, 146 txs): 49 approvals (0x095ea7b3) + 38 PCS buys (0xb6f9de95) + 36 PCS sells (0x791ac947) + 23 aggregator (0x39ecce49, all 0x38031ca8). NO contract creations, NO transfer 0xa9059cbb, NO sale-call 0x4d819a2a. Nonzero-value txs 50, total 0.00249121 BNB, max 0.0001 BNB (PCS buy). Most active wallets: 0xad94ee77 35, 0x38031ca8 35, 0xc7c5faa2 34, 0x3628764a 15, 0xa0c1e94f 15, 0x7488d5da 12. 0 status-0 txs. AFeng 0 txs this run. 0x2325f175 0 txs this run (was 1 aggregator buy run 136). INBOUND: residual round 3 DIAGREGASI run ini (run131-inbound-res130-r18..r23.json, run-130 window 132445937-132456148, 300 contracts, 0 logs, 0 hits, 13 Ankr-failed contracts: 0xa1835fed..., 0xc40f71fd..., 0x1615eff9..., 0x2d176735..., 0x43eb0213..., 0x5f7f05d0..., 0xe03e2276..., 0x0f2a925f..., 0x76cb62de..., 0xa01f2b84..., 0x21209278..., 0xe3da8bf6..., 0x73a63a8a... - all 'Remote end closed connection', retry later; 0 truncated). Round 4 (r24-r29) DILUNCURKAN detached di akhir run (pids 16302-16307, 6 alive) - run 138 aggregates r24-r29 and launches round 5 (r30, last residual slice, 37 contracts) the same detached way. DO NOT relaunch run134-inbound-chain.sh - its wait-loop shape is the dead pattern. Backlog after round 4 launch: residual r30 (1 slice) + run-131/132/133/134/135/136/137 windows (35 each = 245 slices) = 246 slices. Pair retry 8/8 FAILED again (all eight pairs: a6e6/887c/2bfb/c459/43c8/cfdb/0cf8/e68b - token0()/token1() all 'all endpoints failed' via fast_rpc race, TimeoutError/OSError; 0cf8 returned garbage '0x0x' again) - unverified, not absence; 55th consecutive run for a6e6/887c/2bfb/c459, 50th for 43c8, 49th for cfdb/0cf8/e68b; retry run 138. Pointer-discovery (amendment 19:10 WIB, cap 5/run): NO pointer run this run - bridge queue EMPTY (116 contracts: 13 verified / 103 no-pointer / 0 queued) and 0 new contracts this run (0 deployments, 0 new rotation tokens), so nothing to discover. Bridge unchanged. CHAT REPORT this run: NONE (silent) - 0 new mints, no Free Bacot signal, no anomaly, no auto-mint trigger, no guard block. No preview/mint/sign/login/purchase by this job."
}

s["paid_trend_run137"] = ("21 tokens paid-bought; max 3 wallets/token (12 at 3, 5 at 2, 4 at 1); overlap vs run 136: 0 (churn set itself turned over completely, 34th straight run); "
 "0x81c3d1b4 quiet again (0 txs); future1001.ai 0 txs; 0x8e966a9f 0 txs; 0x6ba79dcc/0x89220022/0xda91cefe 0 txs; "
 "AFeng 0 txs this run; "
 "0x2325f175 0 txs this run (was 1 aggregator buy run 136); "
 "sent pass 54/55 first attempt + 1 retry OK (0x5b4beded, 0 in-window txs), 146 txs; receipts 97/97 status 1, 0 NULL, no retry needed; "
 "total nonzero value 0.00249121 BNB across 50 txs, max single 0.0001 BNB (PCS buy); "
 "0 plain BNB transfers; 0 deployments (34th straight run); 0 machine-set activity (34th straight quiet run); "
 "inbound: residual round 3 aggregated (6 slices, 300 contracts, 0 logs, 0 hits, 13 Ankr-failed to retry, 0 truncated); round 4 (r24-r29) launched detached at end of run - aggregation + round 5 launch by run 138.")

s["inbound_log_leg_run137"] = ("Ankr getLogs address-filtered, RESIDUAL ROUND 3 AGGREGATED this run: "
 "run131-inbound-res130-r18..r23.json, run-130 window 132445937-132456148, 300 contracts of the 1537-contract residual list, 0 logs, 0 hits, 13 failed "
 "(0xa1835fedbc5c7f97aeacbad845283c7803a62102, 0xc40f71fd8575da432a3f249e5fdc2f783f567a8f, 0x1615eff9039075f5415b4a3c2040257989b0058a, 0x2d1767354fca28f3aa79def1ffe39ad78886bde9, 0x43eb021329251814af63989ad2e8cb23dea8675f, 0x5f7f05d0c16a03b7790179fe8c6c94e55c9ac3aa, 0xe03e227680b18171b0528c4aa8fa26fdfbe1380b, 0x0f2a925fdfe36ae9adafb1c4eb3fcd5895ddea60, 0x76cb62de3acf99211c385fe9577a02a4d1412796, 0xa01f2b8467e4950abec06fc7c3b0d57e737305a4, 0x21209278656222412f365716863bfb5110637777, 0xe3da8bf6a66a25e1d9c197c269a9a03b8d590bbd, 0x73a63a8aefd63767c19b05401159f06f8eed2cc4 - all Ankr 'Remote end closed connection', retry later), "
 "0 truncated contracts. "
 "Round 4 (r24-r29) launched detached at end of run (pids 16302-16307, 6 alive); run 138 aggregates r24-r29 and launches round 5 (r30, last residual slice) detached. "
 "DO NOT relaunch run134-inbound-chain.sh (wait-loop shape = dead pattern). "
 "Backlog after round 4 launch: residual r30 (1 slice) + run-131/132/133/134/135/136/137 windows (35 each = 245 slices) = 246 slices. "
 "Inbound list unchanged: 1734 contracts.")

n = s.get("next_run_note", "")
repls = [
 ("Next run sent-tx window starts from block 132501973. RETRY run 137:",
  "Next run sent-tx window starts from block 132509889. RETRY run 138:"),
 ("(unreadable run 88-136, 49 consecutive", "(unreadable run 88-137, 50 consecutive"),
 ("(token0/token1 unreadable run 89-136, 48 consecutive", "(token0/token1 unreadable run 89-137, 49 consecutive"),
 ("0 wallets runs 103-136", "0 wallets runs 103-137"),
 ("0 wallets runs 91-136, 46th quiet run", "0 wallets runs 91-137, 47th quiet run"),
 ("0 wallets runs 90-136, 47th quiet run", "0 wallets runs 90-137, 48th quiet run"),
 ("pair retry 8/8 FAILED again (54th consecutive run", "pair retry 8/8 FAILED again (55th consecutive run"),
]
for old, new in repls:
    if old in n:
        n = n.replace(old, new, 1)
        print(f"replaced: {old[:60]}...")
    else:
        print(f"NOT FOUND (skipped): {old[:80]}")
n = ("(Run 137: NO TOTAL OUTAGE - google 000 + Ankr 000 at ~10:06 WIB (both 15s timeouts, slow network, same shape as run 135's google 000); sent pass 54/55 first attempt + 1 retry OK (0x5b4beded, 0 in-window txs), 146 txs, max_block 132509888, receipts 97/97 status 1, 0 NULL, no retry needed, 0 mint logs (fourteenth straight zero-mint run, runs 124-137); "
     "AFeng 0 txs; 0x2325f175 0 txs (was 1 aggregator buy run 136); value total 0.00249 BNB, max 0.0001 BNB (PCS buy) - micro churn only, not a trend; "
     "INBOUND: residual round 3 aggregated (6 slices, 300 contracts, 0 logs, 0 hits, 13 Ankr-failed to retry, 0 truncated); round 4 (r24-r29) launched detached (pids 16302-16307) - run 138 aggregates r24-r29 + launches round 5 (r30); DO NOT relaunch run134-inbound-chain.sh. "
     "Paid: 21 tokens, max 3 wallets/token (12/5/4), overlap vs run 136: 0 (34th straight run); 0 deployments (34th straight run); 0 machine-set activity (34th straight quiet run); 1e9c STALLED 26/27; "
     "pair retry 8/8 FAILED again (55th consecutive run a6e6/887c/2bfb/c459) - unverified, retry run 138; NO pointer run - bridge queue EMPTY (116: 13 verified / 103 no-pointer / 0 queued), 0 new contracts; "
     "CHAT REPORT: NONE (silent).) " + n)
s["next_run_note"] = n

json.dump(s, open(STATE, "w"), indent=1)
print("state updated: last_run=137, paid_trend_run137 + inbound_log_leg_run137 added, 0 new reported_findings entries")
print("next window starts 132509889")
print("backup:", NP / "tracked-wallet-mint-scan-state.json.bak-run137-pre")
