#!/usr/bin/env python3
"""Run 87 state update (read-only job bookkeeping; no chain writes).

Completes run 87 (window 132054228-132061861, tx 2026-11-07 01:10:41 - 02:07:03 WIB).
Sent/receipts/paid done and verified; inbound leg run-87 window FULLY CLOSED.
TWO new machine-token rotations (0x889a... and 0x4249..., both 27 wallets, identical
27-wallet set) verified routine (class-norm sizes, no name/symbol, no free-mint path)
- state-only, NO chat report per fast-path amendment. Bridge unchanged.
"""
import json, shutil
from pathlib import Path

P = "/home/hatch/workspace/narrative-pulse/tracked-wallet-mint-scan-state.json"
D = Path("/home/hatch/workspace/narrative-pulse/scan-runs")
shutil.copy(P, str(P) + ".bak-run87-pre")
s = json.load(open(P))

last_run_87 = {
    "run": 87,
    "block_start": 132054228,
    "block_end": 132061861,
    "window_wib": "2026-11-07 01:10:41 - 02:07:03 WIB (tx times); run executed ~02:05 - ~02:45 WIB; sent-pass in-window txs 668, 0 mint-pattern txs",
    "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set); 0 failed, no retry needed.",
    "method_note": (
        "Sent pass Ankr ankr_getTransactionsByAddress via module: 55/55 OK first attempt, 668 txs, 34 wallets active. "
        "Receipts via fast_rpc batch (6, ~4s pause) for 424 non-approve candidates: 419 status 1, 5 status 0, 0 null, 0 mint logs. "
        "No silent process death this run (receipts completed in one attempt, unlike runs 82/84/86). Status-0 (5): all failed PCS sells "
        "(0x791ac947, value 0, 0 logs) by 0xdb2d83f9, 0xc6219468, 0xc0c84518, 0xa952331e, 0x9b519f5d. "
        "Paid: 24 tokens; TWO NEW machine-token rotations - 0x889a76e4d48169d0398828a36c57b64298577777 at 27 wallets (49.1%) and "
        "0x42491efdffe0aea61799d12b79cfe6ad2a977777 at 27 wallets (49.1%), IDENTICAL 27-wallet set - both numerically above the 20% signal "
        "and 25% auto-mint thresholds, but paid-only with NO free-mint path: auto-mint BLOCKED at guard (c); recorded in state + "
        "signaled_projects as paid-only machine-tokens, NO chat report per fast-path amendment - see machine_tokens entries. Other tokens "
        "max 3 wallets/token (13 at 3, 5 at 2, 4 at 1 - usual ...7777 churn). "
        "AFeng 1 tx: plain self-transfer of 1 gwei (0x3b9aca00 wei, tx 0x7e54217022d3, 01:15:07 WIB) - NOT a mint, no 0x1de4... calls this run; "
        "future1001.ai 0 txs; 0x2325... 0 txs; 0x8e96... 0 txs; 0x5b2f... 0 txs. "
        "Selectors: 148 PCS buys (0xb6f9de95) + 233 PCS sells (0x791ac947) + 244 approvals (0x095ea7b3) + 26 aggregator (0x39ecce49) + "
        "16 deployments (0x60806040) + 1 plain transfer (0x). "
        "Deployments: 16 contract creations by 12 tracked wallets, ALL receipt status 1 with contractAddress read (run87-deployments.json, "
        "16 unique; top deployer 0x97bd... x3, 0x3154.../0x1cce... x2 each); identities of the 16 contracts NOT verified (same limitation as "
        "runs 82/86). All 16 clustered at blocks 132059851-132059865 (~01:52 WIB) except one at 132057444 (01:33:55 WIB). Run-87 inbound list = "
        "run86 list (1111) + these 16 = 1127. "
        "Inbound leg run-87 WINDOW: FULLY CLOSED - 1127/1127 contracts, 10,280 logs, 0 hits, 0 failed, 6 truncated (all topic-filtered to 0 logs: "
        "0x1564... , 0x1de4... AFeng sale, 0x55d398... USDT, 0x6288... AGC sale, 0x636f... AFeng tracker, 0x63de... AGC). "
        "Chunks a (400, 6,623 logs) + b1 (200, 2,522) + b2 (200, 558) + b3 (327, 577); a and b3 each stalled ~4 min at segment 251-300 "
        "(high-log contracts, same as runs 85/86) then completed without intervention. "
        "Pair token0/token1 for a6e6 (0x9fac...) and 887c (0xa9fa...) STILL UNREADABLE (fast_rpc race 'all endpoints failed' + Ankr eth_call "
        "returns null) - persistently unreadable, 5th consecutive run; unverified, not absence; retry run 88. Pair reads for BOTH new rotations "
        "also failed at retry time (same infra outage), but SUCCEEDED later inside run87-token-verify.py once fast_rpc recovered - see entries. "
        "c459 name()/symbol() confirmed EMPTY strings in the run-87 pair retry (fast_rpc recovered for that read) - consistent with the "
        "machine-token pattern; its pair token0/token1 still unreadable at retry time, retry opportunistically run 88, not an anomaly. "
        "No preview/mint/sign/login/purchase by this job."
    ),
}
cur_run = s.get("last_run", {}).get("run", 0)
if cur_run < 87:
    s["last_run"] = last_run_87
    print(f"last_run set to 87 (was {cur_run})")
else:
    print(f"last_run already {cur_run} (>=87) - NOT regressing")
    s["run87_last_run_record"] = last_run_87

s["machine_tokens"].append({
    "address": "0x889a76e4d48169d0398828a36c57b64298577777",
    "first_seen": "run-87, 2026-11-07 01:55:32 WIB (first tracked Transfer tx 0x1f2d2d6ed5230d5505eab90910777fa19d070377d1d2d0a46242f2f604a8b988, block 132060326)",
    "machine_wallets": 27,
    "typical_first_buy_bnb": 0.000121125,
    "followup_buy_range_bnb": "median 0.2301375, max 0.3716893877978409, total buys 9.4095 BNB (53 sent buys)",
    "label": "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB)",
    "note": (
        "Routine rotation, NO anomaly in a listed class; recorded in state WITHOUT chat report per fast-path amendment. "
        "Sizes WITHIN the established class norm (runs 80-82/85/86: first buy ~0.000106-0.000124 BNB, follow-up median ~0.19-0.23, max ~0.37-0.40). "
        "No name/symbol (empty strings, read OK), decimals 18, totalSupply 1e27, owner 0x0. Pair PCS V2 0x1c30eb170510aac11e5e00d7df1a51e6ddcd75ef "
        "(token0 = token, token1 = WBNB 0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c; reserves ~60,135,756 token / 0.05488 BNB). "
        "No free-mint path (0 mint logs; all receives PCS buys). Auto-mint blocked at guard (c). "
        "27-wallet set IDENTICAL to the 0x4249... set this run (overlap 27/27) and the same machine set as runs 80-82/85/86; "
        "91 sells from tracked wallets in-window (round-trip churn). First tracked Transfer arrived via a tracked-wallet PCS buy "
        "(0xcb08c02c, 0.000121 BNB) - no proxy-routed first transfer this time, unlike runs 85/86. "
        "Not in Free Bacot snapshot; NOT added to bridge (paid-only PCS token, precedent runs 63-86)."
    ),
})
s["machine_tokens"].append({
    "address": "0x42491efdffe0aea61799d12b79cfe6ad2a977777",
    "first_seen": "run-87, 2026-11-07 01:35:19 WIB (first tracked Transfer tx 0x350af1a5c830945a7a35261e1d8b375a8a2e9ed32dcdfe2f9c7ba70e3fa7454d, block 132057630)",
    "machine_wallets": 27,
    "typical_first_buy_bnb": 0.000121125,
    "followup_buy_range_bnb": "median 0.223378725, max 0.3834182956516277, total buys 9.7078 BNB (55 sent buys)",
    "label": "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB)",
    "note": (
        "Routine rotation, NO anomaly in a listed class; recorded in state WITHOUT chat report per fast-path amendment. "
        "Sizes WITHIN the established class norm (runs 80-82/85/86: first buy ~0.000106-0.000124 BNB, follow-up median ~0.19-0.23, max ~0.37-0.40). "
        "No name/symbol (empty strings, read OK), decimals 18, totalSupply 1e27, owner 0x0. Pair PCS V2 0xbc4e69067c169da77026a263aa00296c181e59da "
        "(token0 = token, token1 = WBNB 0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c; reserves ~61,208,106 token / 0.05639 BNB). "
        "No free-mint path (0 mint logs; all receives PCS buys). Auto-mint blocked at guard (c). "
        "27-wallet set IDENTICAL to the 0x889a... set this run (overlap 27/27) and the same machine set as runs 80-82/85/86; "
        "98 sells from tracked wallets in-window (round-trip churn). First tracked Transfer arrived via a tracked-wallet PCS buy "
        "(0xcb08c02c, 0.000121 BNB) - no proxy-routed first transfer this time, unlike runs 85/86. "
        "Not in Free Bacot snapshot; NOT added to bridge (paid-only PCS token, precedent runs 63-86)."
    ),
})

sig = s.setdefault("signaled_projects_over_20pct", [])
sig.append("Unnamed token (name/symbol empty) 0x889a76e4d48169d0398828a36c57b64298577777 (paid-only, machine-token, run-87, no chat report per fast-path amendment)")
sig.append("Unnamed token (name/symbol empty) 0x42491efdffe0aea61799d12b79cfe6ad2a977777 (paid-only, machine-token, run-87, no chat report per fast-path amendment)")

s["paid_trend_run87"] = {
    "note": "Aggregate only, NOT a buy recommendation. TWO new machine-token rotations at 27 wallets each (identical set) are paid-only with no free-mint path (auto-mint blocked at guard (c)); recorded in state, NO chat report per fast-path amendment. SILENT RUN - no chat report (no new mints, no Free Bacot signal, no auto-mint trigger, no reportable paid trend beyond the routine rotations).",
    "rotations": (
        "TWO NEW machine-token rotations, same 27-wallet machine set as runs 80-82/85/86, IDENTICAL set (overlap 27/27): "
        "0x889a76e4d48169d0398828a36c57b64298577777 at 27 wallets (49.1% of 55): 53 sent buys (min 0.000121, median 0.2301, max 0.3717 BNB, total 9.4095 BNB) + "
        "91 sells, first tracked Transfer 01:55:32 WIB, pair 0x1c30... (reserves ~60.1M token / 0.0549 BNB). "
        "0x42491efdffe0aea61799d12b79cfe6ad2a977777 at 27 wallets (49.1% of 55): 55 sent buys (min 0.000121, median 0.2234, max 0.3834 BNB, total 9.7078 BNB) + "
        "98 sells, first tracked Transfer 01:35:19 WIB, pair 0xbc4e... (reserves ~61.2M token / 0.0564 BNB). Both sizes within class norm; no name/symbol, "
        "no website pointer, no free-mint path; guard (c) blocks auto-mint."
    ),
    "other_paid_activity": [
        {"pattern": "22 other paid tokens: 13 at 3 wallets (usual ...7777 set via trio 0x38031ca8a5/0xad94ee77d0/0xc7c5faa270), 5 at 2, 4 at 1", "wallets": "see run87-paid.json"},
        {"pattern": "Micro round-trip churn continues: 148 PCS buys (0xb6f9de95) + 233 PCS sells (0x791ac947), 244 approvals (0x095ea7b3), 26 aggregator txs (0x39ecce49); top active 0xc7c5.../0xad94.../0x3803... 39 txs each, 0x9cdd... 36, 0xa952... 35", "wallets": "churn set"},
        {"pattern": "16 contract deployments by 12 tracked wallets this run (all status 1, addresses in run87-deployments.json) - second deployment run in a row (36 in run 86); identities unverified, added to run-87 inbound list (0 hits)", "wallets": "0x97bd... x3, 0x3154.../0x1cce... x2 each, 9 x1"},
        {"pattern": "5 failed txs (all 0 logs): all failed PCS sells", "wallets": "0xdb2d..., 0xc621..., 0xc0c8..., 0xa952..., 0x9b51..."},
    ],
    "quiet": "AFeng 1 tx (plain 1-gwei self-transfer, 0 mints); future1001.ai 0 txs; 0x2325... 0 txs; 0x8e96... 0 txs; 0x5b2f... 0 txs; GrokBot 0xfcd0... absent (0 wallets) - 28th consecutive quiet run (59, 61-87) after the run-60 burst; CORLA-97af 0 wallets; CORLA 0x4a9c 0 wallets; all run-64/65 ASI contracts 0 wallets; run-86 tokens 0x2bfb.../0xc459... 0 wallets (1st quiet run after debut, down from 27/26); run-85 token 0x2717... 0 wallets (2nd quiet run after debut); run-82 tokens 0xd468.../0xa6e6.../0x887c... 0 wallets (5th quiet run after debut); run-81 tokens 0 wallets (6th quiet run); run-80 token 0 wallets (7th quiet run); all other run-66/68/69/70/71/72/73/74/75/76/77/78/79 machine tokens 0 wallets.",
}

s["inbound_log_leg_run87"] = {
    "contracts": 1127,
    "attempted": 1127,
    "completed_with_0_hits": 1127,
    "total_logs": 10280,
    "hits": 0,
    "failed": 0,
    "failed_contracts": [],
    "never_attempted": 0,
    "complete": True,
    "note": (
        "Ankr getLogs address-filtered per contract, window 132054228-132061861, from frozen list run87-inbound-contracts.json (1127 contracts = "
        "run86 list 1111 + 16 run-87 deployment addresses). Full pass a (400, 6,623 logs) + b1 (200, 2,522) + b2 (200, 558) + b3 (327, 577) = "
        "10,280 logs, 0 hits, 0 failed. 6 truncated contracts, all topic-filtered to 0 logs (0x1564..., 0x1de4... AFeng sale, 0x55d398... USDT, "
        "0x6288... AGC sale, 0x636f... AFeng tracker, 0x63de... AGC). RUN-87 WINDOW INBOUND FULLY CLOSED. Chunks a and b3 each stalled ~4 min at "
        "segment 251-300 (high-log contracts) then completed without intervention. NOTE: inbound chunk output files are named run87-inbound86-*.json "
        "(script filename quirk carried from run 86) - contents are run-87 data."
    ),
}

s["next_run_note"] = (
    "Next run sent-tx window starts from block 132061862. RETRY run 88: (1) Pair token0/token1 reads for 0xa6e6... pair "
    "0x9fac925655fa4985ab4fe2fe9e0ca8ae323cc9da and 0x887c... pair 0xa9fa6efb21c252b7d4ab81d19a07ee4ecf6d2c97 "
    "(fast_rpc race returns None / 'all endpoints failed' + Ankr eth_call returns null, 5 consecutive runs - persistently unreadable, unverified not absence). "
    "Also still unreadable at run-87 retry time: pair token0/token1 for run-86 rotations "
    "(0x2bfb pair 0x782671f637bf1a01de482824c4b2520bc58a5a4b; 0xc459 pair 0xeca06856c88fcdf1506886431a079d3f2565ca82) - retry opportunistically, "
    "do not re-report as anomaly. c459 name()/symbol() CONFIRMED empty strings run 87 (not transient) - consistent with machine-token pattern. "
    "(2) Run-87 inbound list for run 88 = run87 list (1127) unless run 88's own sent pass finds new deployments to add. "
    "(3) Run-87 window inbound FULLY CLOSED (1127/1127, 10,280 logs, 0 hits). "
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
    "run 81 (TWO tokens 0x7f7a.../0x33f7... at 27 wallets each), run 82 (THREE tokens 0xd468.../0xa6e6.../0x887c... at 27 wallets each), "
    "run 85 (ONE token 0x2717a156b86c3c8894bb2dea9a34c514e8fc7777 at 27 wallets), "
    "run 86 (TWO tokens 0x2bfb481d4812f329b6244450137096157a6b7777 at 27 wallets + 0xc4599c77985efd0353b688b6127ad4f3399e7777 at 26 wallets), "
    "run 87 (TWO tokens 0x889a76e4d48169d0398828a36c57b64298577777 at 27 wallets + 0x42491efdffe0aea61799d12b79cfe6ad2a977777 at 27 wallets) "
    "auto-mint BLOCKED at guard (c) - do not re-signal or re-report the block unless a new mint/buy fact appears for those contracts "
    "(e.g. a genuine free-mint path). Per the 2026-11-06 ~18:30 machine-token fast-path amendment, routine machine-token rotations are "
    "recorded in state WITHOUT a chat report (no full verification per run); report only on anomaly (buy size far off norm, name/symbol appears, "
    "website, or free-mint path). Paid fact: run87 TWO NEW rotations 0x889a... (27 wallets) + 0x4249... (27 wallets, identical set), both routine "
    "class-norm sizes, no anomaly - state-only, no chat report; run-86 tokens 0x2bfb.../0xc459... 0 wallets (1st quiet run after debut); run-85 token "
    "0x2717... 0 wallets (2nd quiet run); run-82 tokens 0xd468.../0xa6e6.../0x887c... all 0 wallets (5th quiet run after debut); run-81 tokens 0 wallets "
    "(6th quiet run); run-80 token 0 wallets (7th quiet run); "
    "GrokBot 0xfcd0... absent (0 wallets) - 28th consecutive quiet run (59, 61-87) after the run-60 burst; CORLA-97af 0 wallets; "
    "CORLA 0x4a9c 0 wallets; all run-64/65 ASI contracts 0 wallets; all run-66/68/69/70/71/72/73/74/75/76/77/78/79/80/81/82/85/86 machine tokens 0 wallets. "
    "Run 87 had 16 deployments (second deployment run in a row after 36 in run 86); all 16 addresses added to the run-87 inbound list (0 hits). "
    "AFeng 1 tx (plain 1-gwei self-transfer, 0 mints); future1001.ai 0 txs; 0x2325... 0 txs; 0x8e96... 0 txs; 0x5b2f... 0 txs. "
    "SCRIPT LESSON (run 85, FIXED run 86): when copying runNN-receipts.py for the next run, sed-replace the two hardcoded json.dump output paths too "
    "(runNN-receipts.json / runNN-paid.json) - run 87's copy was verified correct before running (dumps to run87-receipts.json/run87-paid.json). "
    "PROCESS LESSON (run 86): the receipts pass died silently at 420/461 (service-restart pattern, same as runs 82/84) - the partial-file resume worked; "
    "always re-run the same script to resume rather than re-fetching from scratch. Run 87 receipts completed in one attempt, no resume needed. "
    "INBOUND FILENAME QUIRK (run 87): chunk output files are named run87-inbound86-{a,b1,b2,b3}.json (script carried the 'inbound86' literal from run 86) - "
    "contents are run-87 data; fix the filename literal when copying the script for run 88. "
    "Same-owner factory groups now also include 0x293f and 0x1103 (proven 2026-11-06 ~01:14 WIB, AGENTS.md) alongside the groups listed in the body."
)

json.dump(s, open(P, "w"), indent=1)
print("state updated; last_run now:", s["last_run"]["run"], "block_end:", s["last_run"]["block_end"])
print("machine_tokens:", len(s.get("machine_tokens", [])), "| signaled:", len(s.get("signaled_projects_over_20pct", [])))
print("inbound87 complete:", s["inbound_log_leg_run87"]["complete"])
