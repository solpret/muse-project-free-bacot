#!/usr/bin/env python3
"""Run 133 state update (read-only bookkeeping): last_run + paid_trend_run133 +
inbound_log_leg_run133. No new mints this run, so no new reported_findings
entries. Inbound chain run-132 DIED mid-round-0 (verified: 0 JSON slices);
relaunched as run133-inbound-chain.sh with setsid (pid 23588) - aggregation
by run 134. No preview/mint/sign/login."""
import json, shutil
from pathlib import Path

HOME = Path.home()
NP = HOME / "workspace/narrative-pulse"
STATE = NP / "tracked-wallet-mint-scan-state.json"
shutil.copy(STATE, NP / "tracked-wallet-mint-scan-state.json.bak-run133-pre")
s = json.load(open(STATE))

s["last_run"] = {
 "run": 133,
 "block_start": 132470263,
 "block_end": 132478154,
 "window_wib": "2026-11-09 05:11:56 - 06:10:08 WIB (tx times); run executed ~06:05 WIB - ~06:35 WIB; sent-pass in-window txs 162, 0 mint-pattern txs",
 "wallets_checked": "55/55 via Ankr module first attempt, 0 failed (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set). 6 wallets active (0xc7c5faa2 40, 0x38031ca8 39, 0xad94ee77 38, 0x3628764a 17, 0xa0c1e94f 16, 0x7488d5da 12); AFeng 0 txs; future1001.ai 0 txs; 0x2325f175 0 txs; 0x89220022 0 txs; 0x6ba79dcc 0 txs; 0x81c3d1b4 0 txs (quiet again); all 6 feed wallets 0 txs.",
 "method_note": "NO TOTAL OUTAGE this run (unlike runs 130-132): network slow but up (google 200 in 6.3s, Ankr 301 in 4.5s at ~06:07 WIB); sent pass stalled ~4 min at wallet 22/55 (Ankr latency) then completed 55/55 first attempt, 0 failed, 162 in-window txs total, max_block 132478154. Receipts via fast_rpc batch (6, ~4s pause) for 108 non-approve candidates: 108 status 1, 0 status 0, 0 NULL (no retry needed), 0 mint logs - tenth straight zero-mint run (runs 124-133). fast_rpc RACE eth_call still totally broken (pair retry 8/8 failed, all-endpoints TimeoutError/OSError) - batch vs race paths differ. Paid: 22 tokens; max 3 wallets/token (13 at 3, 7 at 2, 2 at 1); overlap vs run 132: 0 - the churn set itself turned over COMPLETELY again - thirtieth straight run with 0 churn overlap (runs 104-133 also 0). ZERO new rotations - the 27-wallet machine set had 0 txs this run (no buys, no sells, no approvals from any of the 27; verified overlap with active wallets = empty). The named-rotation streak ENDED run 104 (runs 97-103); run 133 has 0, thirtieth straight quiet run. No anomaly to report under the fast-path amendment (no new machine token, no name/symbol appearing, no size anomaly among machine buys, no free-mint path; churn trio PCS buys 40 txs). Trigger >25% NOT met by any token (max 3 wallets = 5.5%). No preview, no execution. Seatbelt 1e9c STALLED at 26: 0 wallets this run (0 buys, 0 sells) - sell-wallet union run101+run102 = 26/27, runs 103-133 add 0 - did NOT reach 27. NOT a new rotation; watch run 134 the same way. Deployments: ZERO - thirtieth straight run without deployments (run 104: 0 through run 133: 0; runs 97-103 had 25/72/64/32/35/70/68) - verified from raw receipts contractAddress fields, not the parsed JSON. Inbound list for run 133 = run132 list (1734) + 0 deployments + 0 new rotation tokens (total 1734, unchanged). 1 plain BNB transfer this run (0xc7c5..., 0.00203845 BNB, 05:36:51 WIB). Selectors (sent pass, 162 txs): 54 approvals (0x095ea7b3) + 40 PCS buys (0xb6f9de95) + 41 PCS sells (0x791ac947) + 26 aggregator (0x39ecce49) + 1 empty-input. NO contract creations. Nonzero-value txs 54, total 0.00462291 BNB, max 0.00203845 BNB (plain transfer). Most active wallets: 0xc7c5faa2 40, 0x38031ca8 39, 0xad94ee77 38, 0x3628764a 17, 0xa0c1e94f 16, 0x7488d5da 12. 0 status-0 txs. INBOUND: run-132 chain VERIFIED DEAD this run (pid 6141 gone; 0 JSON slices finished - residual r00-r05 logs only, killed ~2 min into round 0; the chain launched via exec background:true did NOT survive). RELAUNCHED as run133-inbound-chain.sh with setsid (pid 23588, session leader Ss, verified alive after launch): (b) run-130 residual 31 slices + (a) run-131 window 35 + (c) run-132 window 35 + (d) run-133 own window 35 = 136 slices sequential - run 134 aggregates finished slices, do NOT re-run completed slices. Pair retry 8/8 FAILED again (all eight pairs: a6e6/887c/2bfb/c459/43c8/cfdb/0cf8/e68b - token0()/token1() all 'all endpoints failed' via fast_rpc race, TimeoutError/OSError; 0cf8 token1 returned garbage '0x0x') - unverified, not absence; 51st consecutive run for a6e6/887c/2bfb/c459, 46th for 43c8, 45th for cfdb/0cf8/e68b; retry run 134. Pointer-discovery (amendment 19:10 WIB, cap 5/run): NO pointer run this run - bridge queue EMPTY (116 contracts: 13 verified / 103 no-pointer / 0 queued) and 0 new contracts this run (0 deployments, 0 new rotation tokens), so nothing to discover. Bridge unchanged. CHAT REPORT this run: NONE (silent) - 0 new mints, no Free Bacot signal, no anomaly, no auto-mint trigger, no guard block. No preview/mint/sign/login/purchase by this job."
}

s["paid_trend_run133"] = ("22 tokens paid-bought; max 3 wallets/token (13 at 3, 7 at 2, 2 at 1); overlap vs run 132: 0 (churn set itself turned over completely, 30th straight run); "
 "0x81c3d1b4 quiet again (0 txs); "
 "AFeng 0 txs; future1001.ai 0 txs; 0x2325 0 txs; 0x89220022 quiet (0 txs); 0x6ba79dcc 0 txs; all 6 feed wallets 0 txs; "
 "sent pass 55/55 first attempt (0 Ankr failures, 162 txs; stalled ~4 min at wallet 22/55 on Ankr latency, no total outage); receipts 108/108 status 1, 0 NULL, no retry needed; "
 "total nonzero value 0.00462291 BNB across 54 txs, max single 0.00203845 BNB (plain transfer 0xc7c5, 05:36:51 WIB); "
 "1 plain BNB transfer this run; 0 deployments (30th straight run); 0 machine-set activity (30th straight quiet run); "
 "inbound run-132 chain verified DEAD (0 slices), relaunched with setsid as run133-inbound-chain.sh (pid 23588) covering run-130 residual + run-131/132/133 windows (136 slices) - aggregation by run 134.")

s["inbound_log_leg_run133"] = ("Ankr getLogs address-filtered, CHAIN RELAUNCHED with setsid this run (run133-inbound-chain.sh, pid 23588, session leader Ss, verified alive after launch): "
 "(b) run-130-window residual (31 slices, window 132445937-132456148) -> (a) run-131 own window (35 slices, window 132456149-132466646) -> (c) run-132 own window "
 "(35 slices, window 132466647-132470262) -> (d) run-133 own window (35 slices, window 132470263-132478154), sequential, 6 slices parallel per round, 136 slices total. "
 "Run 134 aggregates finished slices; do NOT re-run completed slices. "
 "NOTE: the run-132 chain (pid 6141, launched via exec background:true) DIED ~2 min into residual round 0 - verified this run: 0 JSON slices finished (r00-r05 logs only). "
 "The setsid launch is the fix; if this chain also dies, run 134 must note the launch mechanism as the failure, not the slices.")

n = s.get("next_run_note", "")
repls = [
 ("Next run sent-tx window starts from block 132470263. RETRY run 133:",
  "Next run sent-tx window starts from block 132478155. RETRY run 134:"),
 ("(unreadable run 88-132, 45 consecutive", "(unreadable run 88-133, 46 consecutive"),
 ("(token0/token1 unreadable run 89-132, 44 consecutive", "(token0/token1 unreadable run 89-133, 45 consecutive"),
 ("0 wallets runs 103-132", "0 wallets runs 103-133"),
 ("0 wallets runs 91-132, 42nd quiet run", "0 wallets runs 91-133, 43rd quiet run"),
 ("0 wallets runs 90-132, 43rd quiet run", "0 wallets runs 90-133, 44th quiet run"),
 ("pair retry 8/8 FAILED again (50th consecutive run", "pair retry 8/8 FAILED again (51st consecutive run"),
]
for old, new in repls:
    if old in n:
        n = n.replace(old, new, 1)
        print(f"replaced: {old[:60]}...")
    else:
        print(f"NOT FOUND (skipped): {old[:80]}")
n = ("(Run 133: NO-OUTAGE RUN - network slow but up (google 200 in 6.3s, Ankr 301 in 4.5s); sent pass stalled ~4 min at wallet 22/55 on Ankr latency, then 55/55 first attempt, 0 failed (162 txs, max_block 132478154), receipts 108/108 status 1, 0 NULL, no retry needed, 0 mint logs (tenth straight zero-mint run, runs 124-133); "
     "INBOUND: run-132 chain VERIFIED DEAD (0 JSON slices, killed ~2 min into residual round 0) - RELAUNCHED with setsid as run133-inbound-chain.sh (pid 23588, verified alive after launch): (b) run-130 residual 31 slices + (a) run-131 window 35 + (c) run-132 window 35 + (d) run-133 own window 35 = 136 slices sequential - run 134 aggregates finished slices, do NOT re-run completed ones. "
     "Paid: 22 tokens, max 3 wallets/token, overlap vs run 132: 0 (30th straight run); 0 deployments (30th straight run); 0 machine-set activity (30th straight quiet run); 1e9c STALLED 26/27; "
     "pair retry 8/8 FAILED again (51st consecutive run a6e6/887c/2bfb/c459) - unverified, retry run 134; NO pointer run - bridge queue EMPTY (116: 13 verified / 103 no-pointer / 0 queued), 0 new contracts; "
     "CHAT REPORT: NONE (silent).) " + n)
s["next_run_note"] = n

json.dump(s, open(STATE, "w"), indent=1)
print("state updated: last_run=133, paid_trend_run133 + inbound_log_leg_run133 added, 0 new reported_findings entries")
print("next window starts 132478155")
print("backup:", NP / "tracked-wallet-mint-scan-state.json.bak-run133-pre")
