#!/usr/bin/env python3
"""Run 84 state update (read-only job bookkeeping; no chain writes).

Completes run 84 (window 132031247-132041619, tx 22:18:25-23:34:54 WIB).
Sent/receipts/paid done and verified; inbound leg INCOMPLETE (Ankr getLogs
outage) - recorded as unverified, full retry in run 85. Bridge unchanged.
"""
import json, shutil
from pathlib import Path

P = "/home/hatch/workspace/narrative-pulse/tracked-wallet-mint-scan-state.json"
D = Path("/home/hatch/workspace/narrative-pulse/scan-runs")
shutil.copy(P, str(P) + ".bak-run84-pre")
s = json.load(open(P))

failed_contracts = json.load(open(D / "run84-inbound-failed.json"))
sent = json.load(open(D / "run84-sent.json"))
paid = json.load(open(D / "run84-paid.json"))
retry3dca = json.load(open(D / "run84-3dca-retry.json"))
pair = json.load(open(D / "run84-pair-retry.json"))

last_run_84 = {
    "run": 84,
    "block_start": 132031247,
    "block_end": 132041619,
    "window_wib": "2026-11-06 22:18:25 - 23:34:54 WIB (tx times); run executed 23:05 - ~00:10 WIB; sent-pass in-window txs 228, 0 mint-pattern txs",
    "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set); 0 failed after retry.",
    "method_note": (
        "Sent pass Ankr ankr_getTransactionsByAddress via module: FIRST attempt died at wallet 28/55 when the service restarted "
        "(~23:31 WIB, process gone, no output after wallet 28 - same silent-death shape as run 82 inbound part a); relaunched fresh from the "
        "same FROM_BLOCK 132031247 and completed 47/55, 8 failed (Ankr urlopen timeout burst, wallets 33-40); retry pass recovered all 8 "
        "(0 in-window txs each - activity now VERIFIED 0, not a failure). Final: 55/55 OK, 228 txs, 6 wallets active. "
        "Receipts via fast_rpc batch (6, ~4s pause) for 153 non-approve candidates: 147 status 1, 0 status 0, 6 null (fast_rpc all-endpoints "
        "TimeoutError on batch 126 + race fallback); null-retry recovered 3 via fast_rpc race (status 0x1, 6 logs each, 0 mint logs) - 3 remain "
        "NULL/UNVERIFIED (0x3c13e8651a..., 0x98dc3c0d83..., 0xcef045848f...; all 0x38031ca8a5 -> aggregator 0x855066c8679c77a0258e792b5ccf19f8c227eb31 "
        "selector 0x39ecce49, values 0 / 0.000026 BNB - same pattern as 3 verified siblings status 1, 6 logs, 0 mint logs; still UNVERIFIED, never "
        "reported as 0; retry run 85). Final receipts: 150 status 1, 0 status 0, 3 null, 0 mint-pattern txs. "
        "Paid: 31 tokens, max 3 wallets/token (16 at 3, 10 at 2, 5 at 1 - usual ...7777 churn); NO new machine-token rotation this run "
        "(run-82 tokens 0xd468/0xa6e6/0x887c all 0 wallets, 2nd quiet run; run-81 tokens 0 wallets, 3rd quiet; run-80 token 0 wallets, 4th quiet). "
        "AFeng 0 txs; future1001.ai 0 txs; 0x2325... 0 txs; 0x8e96... 0 txs; 0x5b2f... 0 txs. "
        "Selectors: 57 PCS buys (0xb6f9de95) + 57 PCS sells (0x791ac947) + 75 approvals (0x095ea7b3) + 38 aggregator (0x39ecce49) + 1 plain BNB transfer "
        "(0xc7c5faa270 -> 0x7f51d4642399aaa0a4a0e3c202c53bf8cdfd82f8, 0.0001297 BNB, 23:00:43 WIB, block 132037063). "
        "Deployments: 0 contract creations by tracked wallets this run (no to=None sent txs, no contractAddress in any receipt). "
        "Run-83 deployments (14 addresses): NONE in the paid map - machine set did NOT buy any of them via sent txs this window; inbound-only check "
        "for them is pending with the inbound leg retry (indices 1061-1074, chunk b3, never attempted). "
        "Inbound leg per 2026-11-03 12:02 amendment: INCOMPLETE - Ankr getLogs effectively down tonight (direct probes 0/2, 30s timeouts; chunks "
        "attempted only 144/1075 contracts in ~15 min, 60 failed, then stalled with zero output for 2.5+ min while processes were alive but blocked "
        "on network I/O; chunks killed ~00:07 WIB). Attempted 144 (a 36, b1 36, b2 37, b3 35), failed 60 (59 urlopen timeout + 1 remote-end-closed), "
        "0 hits among ~84 completed, 1 truncated (0x05debe44... topic-filtered to 0 logs). Remaining 931 contracts NEVER attempted. "
        "Window NOT closed for inbound-only mints - full retry run 85 from frozen list run84-inbound-contracts.json (1075 contracts). "
        "Run-83 window retry CLOSED: 0x3dca077eb687df96cc987da0035c8fad89ae716c topic-filtered re-check (run-83 window 132023418-132031246) succeeded via "
        "Ankr full-range, 0 logs, 0 hits, verified=True (run84-3dca-retry.json) - run-83 window inbound now FULLY CLOSED. "
        "Pair token0/token1 for a6e6 (0x9fac...) and 887c (0xa9fa...) STILL UNREADABLE after retry (fast_rpc all endpoints TimeoutError; Ankr eth_call "
        "probe timed out 90s, 0/4 answered) - unverified, not absence; retry run 85. "
        "INFRA NOTES: (1) Ankr getTransactionsByAddress burst timeouts at run start (first 7 wallets failed, then recovered) and again mid-run "
        "(wallets 33-40); a direct probe succeeded in 10.5s mid-outage - burst/throttling-shaped. (2) fast_rpc ALL public BSC endpoints TimeoutError "
        "during pair retry and parts of receipts (batch 126); recovered intermittently (3/6 null receipts recovered on race retry). "
        "(3) Background-process lesson: nohup'd children launched from an exec call that then completes normally get killed with the session; "
        "use muse.exec background:true for long legs (sent-retry + inbound chunks survived that way; the pid-3737 sent-retry DID run and recover all 8 "
        "wallets - its 'missing' log was a wrong-cwd cat, not a lost run). No preview/mint/sign/login/purchase by this job."
    ),
}
cur_run = s.get("last_run", {}).get("run", 0)
if cur_run < 84:
    s["last_run"] = last_run_84
    print(f"last_run set to 84 (was {cur_run})")
else:
    print(f"last_run already {cur_run} (>=84) - NOT regressing; run-84 record stored separately")
    s["run84_last_run_record"] = last_run_84

s["paid_trend_run84"] = {
    "note": "Aggregate only, NOT a buy recommendation. No token reaches the signal threshold. SILENT RUN - no chat report (no new mints, no signal >20%, no auto-mint trigger, no reportable paid trend; inbound leg incomplete - recorded as unverified, NOT as 0).",
    "no_rotation": "NO new machine-token rotation: max 3 wallets/token across 31 paid tokens (16 at 3, 10 at 2, 5 at 1). Run-82 tokens 0xd468.../0xa6e6.../0x887c... all 0 wallets (2nd quiet run after debut); run-81 tokens 0x7f7a.../0x33f7... 0 wallets (3rd quiet run); run-80 token 0x489e... 0 wallets (4th quiet run); all earlier machine tokens 0 wallets.",
    "other_paid_activity": [
        {"pattern": "31 paid tokens: 16 at 3 wallets (usual ...7777 set via trio 0x38031ca8a5/0xad94ee77d0/0xc7c5faa270), 10 at 2 (pair 0x3628764a65/0xa0c1e94fbc at 7 + trio pairs at 3), 5 at 1 (0x7488d5da6a)", "wallets": "see run84-paid.json"},
        {"pattern": "Micro round-trip churn continues: 57 PCS buys (0xb6f9de95) + 57 PCS sells (0x791ac947), 75 approvals (0x095ea7b3), 38 aggregator txs (0x39ecce49); top active 0xc7c5... 58 txs, 0xad94... 58, 0x3803... 57, 0xa0c1... 21, 0x3628... 19, 0x7488... 15", "wallets": "churn set"},
        {"pattern": "0 contract deployments by tracked wallets this run (first deployment-free run in the recent sequence)", "wallets": "none"},
        {"pattern": "1 plain BNB transfer 0.0001297 BNB to 0x7f51d4642399aaa0a4a0e3c202c53bf8cdfd82f8, 23:00:43 WIB, block 132037063 - trivial churn funding, not a mint (receipt: 0 mint logs)", "wallet": "0xc7c5faa270"},
        {"pattern": "Run-83 deployment addresses (14): 0 bought by the machine set via sent txs (paid map 0 hits); inbound-only check pending with leg retry", "wallets": "machine set"},
    ],
    "quiet": "AFeng 0 txs; future1001.ai 0 txs; 0x2325... 0 txs; 0x8e96... 0 txs; 0x5b2f... 0 txs; GrokBot 0xfcd0... absent (0 wallets) - 25th consecutive quiet run (59, 61-84) after the run-60 burst; CORLA-97af 0 wallets; CORLA 0x4a9c 0 wallets; all run-64/65 ASI contracts 0 wallets; all run-66/68/69/70/71/72/73/74/75/76/77/78/79/80/81/82 machine tokens 0 wallets.",
}

s["inbound_log_leg_run84"] = {
    "contracts": 1075,
    "attempted": 144,
    "completed_with_0_hits": 84,
    "total_logs": "unknown (leg killed before JSON write; ~84 completed contracts, 0 hits; 1 truncated topic-filtered to 0 logs)",
    "hits": 0,
    "failed": len(failed_contracts),
    "failed_contracts": failed_contracts,
    "never_attempted": 931,
    "complete": False,
    "note": (
        "Ankr getLogs address-filtered per contract, window 132031247-132041619, from ONE frozen list "
        "(run84-inbound-contracts.json, 1075 contracts = run83 list 1061 + 14 run-83 deployment addresses). "
        "LEG INCOMPLETE - KILLED ~00:07 WIB: Ankr getLogs effectively down (direct probes 0/2 at 30s timeout; chunks attempted 144 contracts "
        "in ~15 min: a 36, b1 36, b2 37, b3 35; 60 failed - 59 urlopen timeout + 1 remote-end-closed; 0 hits among ~84 completed; "
        "1 truncated 0x05debe44... topic-filtered to 0 logs; then zero output for 2.5+ min with processes alive but blocked on network I/O). "
        "931 contracts NEVER attempted. Run-84 window NOT closed for inbound-only mints - FULL RETRY run 85 from the same frozen list. "
        "Run-83 window retry CLOSED this run: 0x3dca... topic-filtered re-check (Ankr full-range) 0 logs, 0 hits, verified=True - "
        "run-83 window inbound now FULLY CLOSED. "
        "14 run-83 deployment addresses sit at indices 1061-1074 (chunk b3) and were never attempted - their inbound-only check is pending with the retry."
    ),
}

s["next_run_note"] = (
    "Next run sent-tx window starts from block 132041620. RETRY run 85: (1) FULL inbound leg for the RUN-84 window (132031247-132041619) "
    "from frozen list run84-inbound-contracts.json (1075 contracts = run83 list 1061 + 14 run-83 deployment addresses): 60 failed contracts "
    "(see inbound_log_leg_run84 failed_contracts) + 931 never attempted; the ~84 completed with 0 hits do NOT need re-checking, but the leg as a "
    "whole is UNVERIFIED until a full pass completes - never report the run-84 window as 0 inbound-only mints. "
    "(2) 3 null receipts from run 84 (all 0x38031ca8a5 -> aggregator 0x855066c8679c77a0258e792b5ccf19f8c227eb31 selector 0x39ecce49): "
    "0x3c13e8651ae7eaeffe7f5117d924ea240dcb7528bea6b0a7d8cd80293818f42c, 0x98dc3c0d8388e144f1e2ad55068cfb274b4e35d9766acbee6d8151d62541d8a5, "
    "0xcef045848f25c492fe62cf7e9e50aeb1c493372e19b65a9c3dcc2907fb28a204 - unverified, not 0. "
    "(3) Pair token0/token1 reads for 0xa6e6... pair 0x9fac925655fa4985ab4fe2fe9e0ca8ae323cc9da and 0x887c... pair "
    "0xa9fa6efb21c252b7d4ab81d19a07ee4ecf6d2c97 (fast_rpc all-endpoints TimeoutError + Ankr eth_call timeout run 84). "
    "(4) Run 84 had 0 deployments, so the run-85 inbound list = run84 list (1075) unless run 85's own sent pass finds new deployments to add. "
    "(5) Run-83 window inbound FULLY CLOSED (3dca retry 0 hits, verified run 84). "
    "Dedupe new mints against all tx hashes in reported_findings (223 mint entries over 221 unique tx hashes, direct count run 77). "
    "Run-75 mint tx 0x23cd8740... (AFeng, tracker 0x636f..., 0.15 BNB) is a KNOWN REPEAT of the run-70 finding - do not report as new if it repeats again. "
    "Paid-only signals run 63 (CORLA 0x4a9c), run 64 (4 ASI), run 65 (4 ASI quad-2), run 66 (tokens 0x19b7.../0x540d...), "
    "run 68 (tokens 0xf3cc.../0xe7e2...), run 69 (token 0x4d15...), run 70 (FIVE tokens 0x4df7.../0xae06.../0x2516.../0x1247.../0x8e0d...), "
    "run 71 (SIX tokens 0xe51b.../0xc2e1.../0x5785.../0xfff4.../0xe4c9.../0x25b4...), run 72 (THREE tokens 0x26ef.../0x7145.../0xdfb3...), "
    "run 73 (FOUR tokens 0x4bd1.../0x1d9f.../0xe0f0... at 27 wallets + 0x198c... at 21 wallets), "
    "run 74 (FOUR tokens 0xe4e0.../0x4d2e.../0xaf84... at 27 wallets + 0x73c9... at 26 wallets), "
    "run 75 (THREE tokens 0x167b.../0x5205.../0x4f6d... at 27 wallets each), run 76 (TWO tokens 0x0cda... at 27 wallets + 0xacc8... at 26 wallets), "
    "run 77 (THREE tokens 0x3029.../0x5eb1.../0x1a57... at 27 wallets each), run 78 (TWO tokens 0xcbbc.../0x41cc... at 27 wallets each), "
    "run 79 (TWO tokens 0x5833.../0x32b4... at 27 wallets each), run 80 (ONE token 0x489e... at 27 wallets), "
    "run 81 (TWO tokens 0x7f7a.../0x33f7... at 27 wallets each), run 82 (THREE tokens 0xd468.../0xa6e6.../0x887c... at 27 wallets each) "
    "auto-mint BLOCKED at guard (c) - do not re-signal or re-report the block unless a new mint/buy fact appears for those contracts "
    "(e.g. a genuine free-mint path). Per the 2026-11-06 ~18:30 machine-token fast-path amendment, routine machine-token rotations are "
    "recorded in state WITHOUT a chat report (no full verification per run); report only on anomaly (buy size far off norm, name/symbol appears, "
    "website, or free-mint path). Paid fact: run84 NO rotation (max 3 wallets/token, 31 tokens, usual ...7777 churn); run-82 tokens 0xd468.../0xa6e6.../0x887c... "
    "all 0 wallets (2nd quiet run after debut); run-81 tokens 0 wallets (3rd quiet run); run-80 token 0 wallets (4th quiet run); "
    "GrokBot 0xfcd0... absent (0 wallets) - 25th consecutive quiet run (59, 61-84) after the run-60 burst; CORLA-97af 0 wallets; "
    "CORLA 0x4a9c 0 wallets; all run-64/65 ASI contracts 0 wallets; all run-66/68/69/70/71/72/73/74/75/76/77/78/79/80/81/82 machine tokens 0 wallets. "
    "Run-84 watch item RESOLVED (sent side): 14 run-83 deployments NOT bought by the machine set (paid map 0 hits); inbound-only check pending with the leg retry. "
    "Run 84 had 0 deployments - first deployment-free run in the recent sequence. "
    "AFeng 0 txs; future1001.ai 0 txs; 0x2325... 0 txs; 0x8e96... 0 txs; 0x5b2f... 0 txs. "
    "OVERLAP NOTE: run 84 finished ~00:10 WIB, after run 85's 00:05 WIB start - if run 85's sent pass began before this update, it used "
    "FROM_BLOCK 132031247 (state still showed run 83) and re-scanned run 84's window; dedupe by tx hash applies, no mint findings to double-report. "
    "Same-owner factory groups now also include 0x293f and 0x1103 (proven 2026-11-06 ~01:14 WIB, AGENTS.md) alongside the groups listed in the body."
)

json.dump(s, open(P, "w"), indent=1)
print("state updated; last_run now:", s["last_run"]["run"], "block_end:", s["last_run"]["block_end"])
print("machine_tokens:", len(s.get("machine_tokens", [])), "| signaled:", len(s.get("signaled_projects_over_20pct", [])))
