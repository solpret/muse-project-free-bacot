#!/usr/bin/env python3
"""Run 135 state update (read-only bookkeeping): last_run + paid_trend_run135 +
inbound_log_leg_run135. No new mints this run, so no new reported_findings
entries. Inbound: residual rounds 0-1 (r00-r11) AGGREGATED this run (12 slices,
600 contracts, 7320 logs, 0 hits); round 2 (r12-r17) launched detached.
AFeng + 0x2325f175 BACK after 3 quiet runs each (recurring-pattern buys, NOT
mints, receipt-verified). No preview/mint/sign/login."""
import json, shutil
from pathlib import Path

HOME = Path.home()
NP = HOME / "workspace/narrative-pulse"
STATE = NP / "tracked-wallet-mint-scan-state.json"
shutil.copy(STATE, NP / "tracked-wallet-mint-scan-state.json.bak-run135-pre")
s = json.load(open(STATE))

s["last_run"] = {
 "run": 135,
 "block_start": 132486615,
 "block_end": 132494179,
 "window_wib": "2026-11-09 07:14:02 - 08:10:22 WIB (tx times); run executed ~08:05 WIB - ~08:25 WIB; sent-pass in-window txs 166, 0 mint-pattern txs",
 "wallets_checked": "55/55 via Ankr module, FIRST ATTEMPT, 0 failed (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set). 8 wallets active (0x38031ca8 40, 0xc7c5faa2 39, 0xad94ee77 38, 0xa0c1e94f 16, 0x3628764a 15, 0x7488d5da 14, 0x2325f175 3, 0xbf004bff AFeng 1); future1001.ai 0 txs; 0x81c3d1b4 0 txs (quiet again); 0x8e966a9f 0 txs; 0x6ba79dcc/0x89220022/0xda91cefe 0 txs.",
 "method_note": "NO TOTAL OUTAGE this run (google 000 once at ~08:06 WIB on 10s timeout = slow network, not outage; Ankr 301 in 7.0s, sent pass worked fine). Sent pass 55/55 first attempt, 166 in-window txs, max_block 132494179. Receipts via fast_rpc batch (6, ~4s pause) for 111 non-approve candidates: 111 status 1, 0 status 0, 0 NULL (no retry needed), 0 mint logs - twelfth straight zero-mint run (runs 124-135). fast_rpc RACE eth_call still totally broken (pair retry 8/8 failed, all-endpoints TimeoutError/OSError; 0cf8 garbage '0x0x' again) - batch vs race paths differ. Paid: 26 tokens; max 3 wallets/token (13 at 3, 6 at 2, 7 at 1); overlap vs run 134: 0 - the churn set itself turned over COMPLETELY again - thirty-second straight run with 0 churn overlap (runs 104-135 also 0). ZERO new rotations - the 27-wallet machine set had 0 txs this run (no buys, no sells, no approvals from any of the 27; verified overlap with active wallets = empty). The named-rotation streak ENDED run 104 (runs 97-103); run 135 has 0, thirty-second straight quiet run. No anomaly to report under the fast-path amendment (no new machine token, no name/symbol appearing, no size anomaly among machine buys, no free-mint path; churn trio PCS buys 42 txs). Trigger >25% NOT met by any token (max 3 wallets = 5.5%). No preview, no execution. Seatbelt 1e9c STALLED at 26: 0 wallets this run (0 buys, 0 sells) - sell-wallet union run101+run102 = 26/27, runs 103-135 add 0 - did NOT reach 27. NOT a new rotation; watch run 136 the same way. Deployments: ZERO - thirty-second straight run without deployments (run 104: 0 through run 135: 0; runs 97-103 had 25/72/64/32/35/70/68) - verified from raw receipts contractAddress fields, not the parsed JSON. Inbound list for run 135 = run134 list (1734) + 0 deployments + 0 new rotation tokens (total 1734, unchanged). 1 plain BNB transfer this run (0xc7c5faa2 -> 0x7f51d464..., 0.00200481 BNB, 07:56:51 WIB, 0 logs). Selectors (sent pass, 166 txs): 55 approvals (0x095ea7b3) + 42 PCS buys (0xb6f9de95) + 39 PCS sells (0x791ac947) + 26 aggregator (0x39ecce49) + 2 aggregator (0x27772d13, both 0x2325f175 to 0x296b0019...) + 1 sale-call (0x4d819a2a, AFeng) + 1 empty-input (plain transfer). NO contract creations, NO transfer 0xa9059cbb. Nonzero-value txs 59, total 0.56473573 BNB, max 0.5 BNB (AFeng sale-call; value spike vs run 134's 0.00257 BNB is single-wallet recurring-pattern buys - AFeng 0.5 + 0x2325 0.06 - NOT a trend). Most active wallets: 0x38031ca8 40, 0xc7c5faa2 39, 0xad94ee77 38, 0xa0c1e94f 16, 0x3628764a 15, 0x7488d5da 14, 0x2325f175 3, AFeng 1. 0 status-0 txs. NOTABLE RETURNS (receipt-verified, NOT mints): AFeng BACK after 3 quiet runs (132-134) - 1 tx, sale-call 0x4d819a2a to KNOWN sale contract 0x1de460f363af910f51726def188f9004276bf4bc, 0.5 BNB, 07:43:15 WIB, block 132490564, receipt status 1, 15 logs, bought churn token 0x29b2b7cb9d09e0c85de42db1061a18473dbf7777 via PCS swap inside the receipt - NO Transfer from zero address to AFeng, so NOT a mint; same contract+selector AFeng used in runs 54-63/70 (incl. dividend-tracker mint-patterns then - none this run). 0x2325f175 BACK after 3 quiet runs (132-134) - 3 txs: 2 aggregator calls 0x27772d13 to 0x296b00198dc7ec3410e12da814d9267bb8df506a (0.06 BNB + 0 BNB, bought token 0x9b6187d2aba9f7c93aa986dd48cb2b2fe5b3db99) + 1 approval; same aggregator+selector seen runs 54/61/62. Both returns are recurring-pattern paid buys by single wallets (1 entity each) - far below thresholds, NOT signals, NOT leads, NOT chat-reported (same shape as runs 124-134 silence). INBOUND: residual rounds 0-1 AGGREGATED this run (run131-inbound-res130-r00..r11.json, run-130 window 132445937-132456148, 600 contracts, 7320 logs, 0 hits, 4 Ankr-failed contracts: 0x6ce55cef..., 0x87ca3c67..., 0x94c4834b..., 0xa9481429... - all 'Remote end closed connection', retry later; 5 truncated contracts resolved via topic-filtered re-query, 0 hits). Round 2 (r12-r17) LAUNCHED detached at end of run (pids 22454-22465, 6 alive) - run 136 aggregates r12-r17 and launches round 3 (r18-r23) the same detached way. DO NOT relaunch run134-inbound-chain.sh - its wait-loop shape is the dead pattern. Backlog after round 2 launch: residual r18-r30 (13 slices) + run-131/132/133/134/135 windows (35 each = 175 slices) = 188 slices. Pair retry 8/8 FAILED again (all eight pairs: a6e6/887c/2bfb/c459/43c8/cfdb/0cf8/e68b - token0()/token1() all 'all endpoints failed' via fast_rpc race, TimeoutError/OSError; 0cf8 token0/token1 returned garbage '0x0x' again) - unverified, not absence; 53rd consecutive run for a6e6/887c/2bfb/c459, 48th for 43c8, 47th for cfdb/0cf8/e68b; retry run 136. Pointer-discovery (amendment 19:10 WIB, cap 5/run): NO pointer run this run - bridge queue EMPTY (116 contracts: 13 verified / 103 no-pointer / 0 queued) and 0 new contracts this run (0 deployments, 0 new rotation tokens), so nothing to discover. Bridge unchanged. CHAT REPORT this run: NONE (silent) - 0 new mints, no Free Bacot signal, no anomaly, no auto-mint trigger, no guard block. No preview/mint/sign/login/purchase by this job."
}

s["paid_trend_run135"] = ("26 tokens paid-bought; max 3 wallets/token (13 at 3, 6 at 2, 7 at 1); overlap vs run 134: 0 (churn set itself turned over completely, 32nd straight run); "
 "0x81c3d1b4 quiet again (0 txs); future1001.ai 0 txs; 0x8e966a9f 0 txs; 0x6ba79dcc/0x89220022/0xda91cefe 0 txs; "
 "AFeng BACK after 3 quiet runs: 1 sale-call 0x4d819a2a to known 0x1de460f3..., 0.5 BNB, bought churn token 0x29b2b7cb...7777 via PCS swap in receipt - NOT a mint (no zero-address Transfer); "
 "0x2325f175 BACK after 3 quiet runs: 3 txs, 2 aggregator 0x27772d13 to 0x296b0019... (0.06 + 0 BNB) + 1 approval; "
 "sent pass 55/55 first attempt, 166 txs; receipts 111/111 status 1, 0 NULL, no retry needed; "
 "total nonzero value 0.56473573 BNB across 59 txs, max single 0.5 BNB (AFeng) - value spike is single-wallet recurring buys, not a trend; "
 "1 plain BNB transfer (0xc7c5faa2 -> 0x7f51d464..., 0.002 BNB); 0 deployments (32nd straight run); 0 machine-set activity (32nd straight quiet run); "
 "inbound: residual rounds 0-1 aggregated (12 slices, 600 contracts, 7320 logs, 0 hits, 4 Ankr-failed to retry, 5 truncated resolved via topic filter); round 2 (r12-r17) launched detached at end of run - aggregation + round 3 launch by run 136.")

s["inbound_log_leg_run135"] = ("Ankr getLogs address-filtered, RESIDUAL ROUNDS 0-1 AGGREGATED this run: "
 "run131-inbound-res130-r00..r11.json, run-130 window 132445937-132456148, 600 contracts of the 1537-contract residual list, 7320 logs, 0 hits, 4 failed "
 "(0x6ce55cef08ce723257dafae4c7e5f9eb80548b18, 0x87ca3c6704a08b56dc4e173315e948761ea2eb0c, 0x94c4834b186938f95edc67ff0536ac17f3102523, 0xa9481429169c883c7fd5f5eadfd08737ad688337 - all Ankr 'Remote end closed connection', retry later), "
 "5 truncated contracts (0x55d39832..., 0x636fdfa9..., 0x63dea5ac..., 0x78573ab4..., 0x7e2da878...) each re-queried topic-filtered (Transfer from zero to tracked) with 0 hits. "
 "Round 2 (r12-r17) launched detached at end of run (pids 22454-22465, 6 alive); run 136 aggregates r12-r17 and launches round 3 (r18-r23) detached. "
 "DO NOT relaunch run134-inbound-chain.sh (wait-loop shape = dead pattern). "
 "Backlog after round 2 launch: residual r18-r30 (13 slices) + run-131/132/133/134/135 windows (35 each = 175 slices) = 188 slices. "
 "Inbound list unchanged: 1734 contracts.")

n = s.get("next_run_note", "")
repls = [
 ("Next run sent-tx window starts from block 132486615. RETRY run 135:",
  "Next run sent-tx window starts from block 132494180. RETRY run 136:"),
 ("(unreadable run 88-134, 47 consecutive", "(unreadable run 88-135, 48 consecutive"),
 ("(token0/token1 unreadable run 89-134, 46 consecutive", "(token0/token1 unreadable run 89-135, 47 consecutive"),
 ("0 wallets runs 103-134", "0 wallets runs 103-135"),
 ("0 wallets runs 91-134, 44th quiet run", "0 wallets runs 91-135, 45th quiet run"),
 ("0 wallets runs 90-134, 45th quiet run", "0 wallets runs 90-135, 46th quiet run"),
 ("pair retry 8/8 FAILED again (52nd consecutive run", "pair retry 8/8 FAILED again (53rd consecutive run"),
]
for old, new in repls:
    if old in n:
        n = n.replace(old, new, 1)
        print(f"replaced: {old[:60]}...")
    else:
        print(f"NOT FOUND (skipped): {old[:80]}")
n = ("(Run 135: NO TOTAL OUTAGE - google 000 once ~08:06 WIB (10s timeout, slow network), Ankr 301 in 7.0s; sent pass 55/55 FIRST ATTEMPT, 0 failed (166 txs, max_block 132494179), receipts 111/111 status 1, 0 NULL, no retry needed, 0 mint logs (twelfth straight zero-mint run, runs 124-135); "
     "NOTABLE RETURNS (receipt-verified, NOT mints): AFeng back after 3 quiet runs - 1 sale-call 0x4d819a2a to known 0x1de460f3..., 0.5 BNB, bought churn token 0x29b2b7cb...7777 via PCS swap, no zero-address Transfer; 0x2325f175 back after 3 quiet runs - 3 txs incl. 2 aggregator 0x27772d13 (0.06 + 0 BNB); value total 0.5647 BNB vs 0.0026 run 134 = single-wallet recurring buys, not a trend; "
     "INBOUND: residual rounds 0-1 aggregated (12 slices, 600 contracts, 7320 logs, 0 hits, 4 Ankr-failed to retry, 5 truncated resolved via topic filter); round 2 (r12-r17) launched detached (pids 22454-22465) - run 136 aggregates r12-r17 + launches round 3; DO NOT relaunch run134-inbound-chain.sh. "
     "Paid: 26 tokens, max 3 wallets/token (13/6/7), overlap vs run 134: 0 (32nd straight run); 0 deployments (32nd straight run); 0 machine-set activity (32nd straight quiet run); 1e9c STALLED 26/27; "
     "pair retry 8/8 FAILED again (53rd consecutive run a6e6/887c/2bfb/c459) - unverified, retry run 136; NO pointer run - bridge queue EMPTY (116: 13 verified / 103 no-pointer / 0 queued), 0 new contracts; "
     "CHAT REPORT: NONE (silent).) " + n)
s["next_run_note"] = n

json.dump(s, open(STATE, "w"), indent=1)
print("state updated: last_run=135, paid_trend_run135 + inbound_log_leg_run135 added, 0 new reported_findings entries")
print("next window starts 132494180")
print("backup:", NP / "tracked-wallet-mint-scan-state.json.bak-run135-pre")
