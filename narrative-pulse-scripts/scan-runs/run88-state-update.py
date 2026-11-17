#!/usr/bin/env python3
"""Run 88 state update (read-only job bookkeeping; no chain writes).

Completes run 88 (window 132061862-132070121, tx 2026-11-07 02:08:30 - 03:09:01 WIB).
Sent/receipts/paid done and verified; inbound leg run-88 window FULLY CLOSED.
THREE new machine-token rotations at 27 wallets (identical set) + a FOURTH at 18
wallets (subset of the same set, rotation still in progress at window end) -
all verified routine (class-norm sizes, no name/symbol, no free-mint path) -
state-only, NO chat report per fast-path amendment. Bridge unchanged (0 new mints).
"""
import json, shutil
from pathlib import Path

P = "/home/hatch/workspace/narrative-pulse/tracked-wallet-mint-scan-state.json"
D = Path("/home/hatch/workspace/narrative-pulse/scan-runs")
shutil.copy(P, str(P) + ".bak-run88-pre")
s = json.load(open(P))

last_run_88 = {
    "run": 88,
    "block_start": 132061862,
    "block_end": 132070121,
    "window_wib": "2026-11-07 02:08:30 - 03:09:01 WIB (tx times); run executed ~03:05 - ~04:35 WIB; sent-pass in-window txs 1055, 0 mint-pattern txs",
    "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set); 0 failed, no retry needed.",
    "method_note": (
        "Sent pass Ankr ankr_getTransactionsByAddress via module: 55/55 OK first attempt, 1055 txs, 34 wallets active. "
        "Receipts via fast_rpc batch (6, ~4s pause) for 680 non-approve candidates: 679 status 1, 1 status 0, 0 null, 0 mint logs. "
        "Receipts completed in one attempt, no resume needed. Status-0 (1): failed PCS sell (0x791ac947, value 0, 0 logs) by 0xc6219468, "
        "02:15:08 WIB, tx 0x4b60d00a75765ff9418712ba32cff3856b49652e0913dd69f6d476984a68fa31. "
        "Paid: 30 tokens; THREE NEW machine-token rotations at 27 wallets (49.1%) each - 0x43c8f55b12391671d1f00b04ba1ef6d1842e7777, "
        "0x3d1201ea0d559e7071bc42d24e1494c6d7547777, 0xeae0936e2f9ecb0a1acac8c5b9e43f86d3d37777 - IDENTICAL 27-wallet set, plus a FOURTH "
        "0x79cd174ca3ec25c06ff5fddae365643f73d77777 at 18 wallets (32.7%), a SUBSET of the same set (overlap 18/18), first tracked "
        "Transfer only 03:06:45 WIB - rotation still in progress at window end, likely to reach 27 next run. All four numerically above "
        "the 20% signal and 25% auto-mint thresholds, but paid-only with NO free-mint path: auto-mint BLOCKED at guard (c); recorded in "
        "state + signaled_projects as paid-only machine-tokens, NO chat report per fast-path amendment - see machine_tokens entries. "
        "Other tokens max 3 wallets/token (11 at 3, 5 at 2, 10 at 1 - usual ...7777 churn). "
        "AFeng 2 txs: 1 call to 0x1de4... (0x4d819a2a, value 0, 13 logs, status 1, 02:12:57 WIB, NO mint logs) + 1 approval to SLIME "
        "0x8351311f... (approve selector, excluded from receipts); future1001.ai 0 txs; 0x2325... 0 txs; 0x8e96... 0 txs; 0x5b2f... 0 txs. "
        "Selectors: 234 PCS buys (0xb6f9de95) + 365 PCS sells (0x791ac947) + 375 approvals (0x095ea7b3) + 22 aggregator (0x39ecce49) + "
        "56 deployments (0x60806040) + 2 plain transfers (0x) + 1 AFeng sale call (0x4d819a2a). "
        "Deployments: 56 contract creations by 13 tracked wallets, ALL receipt status 1 with contractAddress read (run88-deployments.json, "
        "56 unique; top deployer 0x97bd... x9, 0x3154... x8, 0x9b51... x6, 0x1cce... x5) - third deployment run in a row (16 run 87, 36 run 86), "
        "clustered in 4 bursts ~18 min apart (blocks ~132062501-513 ~02:11, ~132064861-875 ~02:29, ~132067247-260 ~02:47, ~132069597-619 ~03:05); "
        "identities of the 56 contracts NOT verified (same limitation as runs 82/86/87). Run-88 inbound list = run87 list (1127) + these 56 = 1183. "
        "Inbound leg run-88 WINDOW: FULLY CLOSED - 1183/1183 contracts, 8,882 logs, 0 hits, 0 failed, 3 truncated (all topic-filtered to 0 logs: "
        "0x1de4... AFeng sale, 0x55d398... USDT, 0x63de... AGC). "
        "Chunks a (400, 5,858 logs) + b1 (200, 1,932) + b2 (200, 517) + b3 (383, 575). Chunk a FIRST attempt died silently at 125/400 "
        "(service-restart pattern, same as runs 82/84/86; 2 transient errors before death: 0x02f1... remote-end-closed, 0x213a... SSL EOF) - "
        "re-run full chunk a completed clean (0 failed; both contracts read OK on retry). Chunks b1/b2/b3 completed first attempt. "
        "Pair token0/token1 STILL UNREADABLE for a6e6 (0x9fac...), 887c (0xa9fa...), 2bfb (0x7826...), c459 (0xeca0...) in run-88 pair retry "
        "(fast_rpc race 'all endpoints failed', 6th consecutive run) AND for new rotation 43c8 (0xaafebb...) - fast_rpc endpoints failing at "
        "retry time (transient infra outage; 3d12/eae0/79cd pairs DID read OK inside run88-token-verify.py before the outage worsened); "
        "unverified, not absence; retry run 89. 43c8 pair address itself is known from its first Transfer log (0xaafebb...). "
        "Pointer-discovery (amendment 19:10): 0 contracts processed - no new mints this run, so no new contracts and no backfill queue; bridge unchanged. "
        "No preview/mint/sign/login/purchase by this job."
    ),
}
cur_run = s.get("last_run", {}).get("run", 0)
if cur_run < 88:
    s["last_run"] = last_run_88
    print(f"last_run set to 88 (was {cur_run})")
else:
    print(f"last_run already {cur_run} (>=88) - NOT regressing")
    s["run88_last_run_record"] = last_run_88

s["machine_tokens"].append({
    "address": "0x43c8f55b12391671d1f00b04ba1ef6d1842e7777",
    "first_seen": "run-88, 2026-11-07 ~02:48 WIB (first tracked Transfer block 132067427, tx 0x4e40722b72f8420f18a88210857eaaf0ccb33456dad1dc40366cd131e88b73dd)",
    "machine_wallets": 27,
    "typical_first_buy_bnb": 0.000121125,
    "followup_buy_range_bnb": "median 0.223378725, max 0.42734472596879547, total buys 9.9019 BNB (58 sent buys)",
    "label": "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB)",
    "note": (
        "Routine rotation, NO anomaly in a listed class; recorded in state WITHOUT chat report per fast-path amendment. "
        "Sizes WITHIN the established class norm (runs 80-82/85-87: first buy ~0.000106-0.000124 BNB, follow-up median ~0.19-0.23, max ~0.37-0.43). "
        "No name/symbol (empty strings, read OK), decimals 18, totalSupply 1e27, owner 0x0. Pair PCS V2 0xaafebb5244e2e546f7cd18a2c89f85bbee03f1e0 "
        "(pair token0/token1 UNREADABLE at retry time - fast_rpc 'all endpoints failed', transient outage; retry run 89). "
        "No free-mint path (0 mint logs; all receives PCS buys). Auto-mint blocked at guard (c). "
        "27-wallet set IDENTICAL to the 0x3d12... and 0xeae0... sets this run (overlap 27/27) and the same machine set as runs 80-82/85-87; "
        "100 sells from tracked wallets in-window (round-trip churn). First tracked Transfer arrived via a tracked-wallet PCS buy "
        "(0xcb08c02c, 0.000121 BNB) - no proxy-routed first transfer. "
        "Not in Free Bacot snapshot; NOT added to bridge (paid-only PCS token, precedent runs 63-87)."
    ),
})
s["machine_tokens"].append({
    "address": "0x3d1201ea0d559e7071bc42d24e1494c6d7547777",
    "first_seen": "run-88, 2026-11-07 02:31:18 WIB (first tracked Transfer tx 0x01c3b2e87213..., block 132065093)",
    "machine_wallets": 27,
    "typical_first_buy_bnb": 0.000105776459161118,
    "followup_buy_range_bnb": "median 0.223378725, max 0.37451967580643714, total buys 10.1657 BNB (58 sent buys)",
    "label": "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB)",
    "note": (
        "Routine rotation, NO anomaly in a listed class; recorded in state WITHOUT chat report per fast-path amendment. "
        "Sizes WITHIN the established class norm (first buy 0.0001058 BNB is a hair below the usual 0.000106-0.000124 band - same PCS-buy "
        "selector 0xb6f9de95 by the same wallet 0xcb08c02c, not a distinct pattern; median/max/total all in norm). "
        "No name/symbol (empty strings, read OK), decimals 18, totalSupply 1e27, owner 0x0. Pair PCS V2 0x709c70dee63ce868fa9b38509a8235f696a7a966 "
        "(token0 = token, token1 = WBNB 0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c; reserves ~62,117,928 token / 0.05772 BNB). "
        "No free-mint path (0 mint logs; all receives PCS buys). Auto-mint blocked at guard (c). "
        "27-wallet set IDENTICAL to the 0x43c8... and 0xeae0... sets this run (overlap 27/27) and the same machine set as runs 80-82/85-87; "
        "100 sells from tracked wallets in-window (round-trip churn). "
        "Not in Free Bacot snapshot; NOT added to bridge (paid-only PCS token, precedent runs 63-87)."
    ),
})
s["machine_tokens"].append({
    "address": "0xeae0936e2f9ecb0a1acac8c5b9e43f86d3d37777",
    "first_seen": "run-88, 2026-11-07 02:13:27 WIB (first tracked Transfer tx 0xd32f9b5a1bd2..., block 132062715)",
    "machine_wallets": 27,
    "typical_first_buy_bnb": 0.000121125,
    "followup_buy_range_bnb": "median 0.223378725, max 0.3716796990564023, total buys 9.6629 BNB (56 sent buys)",
    "label": "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB)",
    "note": (
        "Routine rotation, NO anomaly in a listed class; recorded in state WITHOUT chat report per fast-path amendment. "
        "Sizes WITHIN the established class norm. "
        "No name/symbol (empty strings, read OK), decimals 18, totalSupply 1e27, owner 0x0. Pair PCS V2 0x11a3e370f569c73a45e47d98b4f99d4bfdbb6b9c "
        "(token0 = WBNB 0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c, token1 = token; reserves 0.0556 BNB / ~60,651,036 token). "
        "No free-mint path (0 mint logs; all receives PCS buys). Auto-mint blocked at guard (c). "
        "27-wallet set IDENTICAL to the 0x43c8... and 0x3d12... sets this run (overlap 27/27) and the same machine set as runs 80-82/85-87; "
        "96 sells from tracked wallets in-window (round-trip churn). First tracked Transfer arrived via a tracked-wallet PCS buy "
        "(0xcb08c02c, 0.000126 BNB). "
        "Not in Free Bacot snapshot; NOT added to bridge (paid-only PCS token, precedent runs 63-87)."
    ),
})
s["machine_tokens"].append({
    "address": "0x79cd174ca3ec25c06ff5fddae365643f73d77777",
    "first_seen": "run-88, 2026-11-07 03:06:45 WIB (first tracked Transfer tx 0x8bd73d5b173d..., block 132069819)",
    "machine_wallets": 18,
    "typical_first_buy_bnb": 0.000121125,
    "followup_buy_range_bnb": "median 0.223378725, max 0.3716636489654331, total buys 3.4956 BNB (19 sent buys)",
    "label": "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - rotation IN PROGRESS at window end",
    "note": (
        "Routine rotation, NO anomaly in a listed class; recorded in state WITHOUT chat report per fast-path amendment. "
        "18 wallets is a SUBSET of the same 27-wallet machine set (overlap 18/18 with each of the three 27-wallet rotations this run); "
        "first tracked Transfer only 03:06:45 WIB, ~2 min before window end - the rotation was still filling, expect it to reach 27 wallets "
        "in run 89; do NOT treat run-89 growth to 27 as a new rotation. Sizes WITHIN the established class norm (median identical "
        "0.223378725 to the other three rotations - same machine program). "
        "No name/symbol (empty strings, read OK), decimals 18, totalSupply 1e27, owner 0x0. Pair PCS V2 0xb5a05c4ed28689daa8a35818a6debd9e8b45f8d7 "
        "(token0 = token, token1 = WBNB; reserves ~62,351,117 token / 0.05808 BNB). "
        "No free-mint path (0 mint logs; all receives PCS buys). Auto-mint blocked at guard (c). 24 sells from tracked wallets in-window. "
        "Not in Free Bacot snapshot; NOT added to bridge (paid-only PCS token, precedent runs 63-87)."
    ),
})

sig = s.setdefault("signaled_projects_over_20pct", [])
sig.append("Unnamed token (name/symbol empty) 0x43c8f55b12391671d1f00b04ba1ef6d1842e7777 (paid-only, machine-token, run-88, no chat report per fast-path amendment)")
sig.append("Unnamed token (name/symbol empty) 0x3d1201ea0d559e7071bc42d24e1494c6d7547777 (paid-only, machine-token, run-88, no chat report per fast-path amendment)")
sig.append("Unnamed token (name/symbol empty) 0xeae0936e2f9ecb0a1acac8c5b9e43f86d3d37777 (paid-only, machine-token, run-88, no chat report per fast-path amendment)")
sig.append("Unnamed token (name/symbol empty) 0x79cd174ca3ec25c06ff5fddae365643f73d77777 (paid-only, machine-token, run-88, 18 wallets, rotation in progress, no chat report per fast-path amendment)")

s["paid_trend_run88"] = {
    "note": "Aggregate only, NOT a buy recommendation. THREE new machine-token rotations at 27 wallets each (identical set) + a FOURTH at 18 wallets (subset, still filling) are paid-only with no free-mint path (auto-mint blocked at guard (c)); recorded in state, NO chat report per fast-path amendment. SILENT RUN - no chat report (no new mints, no Free Bacot signal, no auto-mint trigger, no reportable paid trend beyond the routine rotations).",
    "rotations": (
        "THREE NEW machine-token rotations, same 27-wallet machine set as runs 80-82/85-87, IDENTICAL set (overlap 27/27): "
        "0x43c8f55b12391671d1f00b04ba1ef6d1842e7777 at 27 wallets (49.1% of 55): 58 sent buys (min 0.000121, median 0.2234, max 0.4273 BNB, total 9.9019 BNB) + "
        "100 sells, first tracked Transfer block 132067427, pair 0xaafebb... (token0/token1 unreadable at retry - transient fast_rpc outage). "
        "0x3d1201ea0d559e7071bc42d24e1494c6d7547777 at 27 wallets (49.1%): 58 sent buys (min 0.000106, median 0.2234, max 0.3745 BNB, total 10.1657 BNB) + "
        "100 sells, first tracked Transfer 02:31:18 WIB, pair 0x709c... (reserves ~62.1M token / 0.0577 BNB). "
        "0xeae0936e2f9ecb0a1acac8c5b9e43f86d3d37777 at 27 wallets (49.1%): 56 sent buys (min 0.000121, median 0.2234, max 0.3717 BNB, total 9.6629 BNB) + "
        "96 sells, first tracked Transfer 02:13:27 WIB, pair 0x11a3... (reserves 0.0556 BNB / ~60.7M token). "
        "FOURTH rotation 0x79cd174ca3ec25c06ff5fddae365643f73d77777 at 18 wallets (32.7%): 19 sent buys (min 0.000121, median 0.2234, max 0.3717 BNB, total 3.4956 BNB) + "
        "24 sells, first tracked Transfer 03:06:45 WIB - still filling at window end, expect 27 in run 89. All sizes within class norm; no name/symbol, "
        "no website pointer, no free-mint path; guard (c) blocks auto-mint."
    ),
    "other_paid_activity": [
        {"pattern": "26 other paid tokens: 11 at 3 wallets (usual ...7777 set), 5 at 2, 10 at 1", "wallets": "see run88-paid.json"},
        {"pattern": "Micro round-trip churn continues: 234 PCS buys (0xb6f9de95) + 365 PCS sells (0x791ac947), 375 approvals (0x095ea7b3), 22 aggregator txs (0x39ecce49); top active 0xa952... 67 txs, 0x9cdd... 59, 0xc621... 51", "wallets": "churn set"},
        {"pattern": "56 contract deployments by 13 tracked wallets this run (all status 1, addresses in run88-deployments.json) - third deployment run in a row (16 run 87, 36 run 86), in 4 bursts ~18 min apart; identities unverified, added to run-88 inbound list (0 hits)", "wallets": "0x97bd... x9, 0x3154... x8, 0x9b51... x6, 0x1cce... x5"},
        {"pattern": "1 failed tx: failed PCS sell by 0xc621... (0 logs)", "wallets": "0xc621..."},
    ],
    "quiet": "AFeng 2 txs (1 sale call 0x1de4... value 0, 13 logs, no mint + 1 approval to SLIME); future1001.ai 0 txs; 0x2325... 0 txs; 0x8e96... 0 txs; 0x5b2f... 0 txs; GrokBot 0xfcd0... absent (0 wallets) - 29th consecutive quiet run (59, 61-88) after the run-60 burst; CORLA-97af 0 wallets; CORLA 0x4a9c 0 wallets; all run-64/65 ASI contracts 0 wallets; run-87 tokens 0x889a.../0x4249... 0 wallets (1st quiet run after debut, down from 27/27); run-86 tokens 0x2bfb.../0xc459... 0 wallets (2nd quiet run after debut); run-85 token 0x2717... 0 wallets (3rd quiet run); run-82 tokens 0xd468.../0xa6e6.../0x887c... 0 wallets (6th quiet run after debut); run-81 tokens 0 wallets (7th quiet run); run-80 token 0 wallets (8th quiet run); all other run-66/68/69/70/71/72/73/74/75/76/77/78/79 machine tokens 0 wallets.",
}

s["inbound_log_leg_run88"] = {
    "contracts": 1183,
    "attempted": 1183,
    "completed_with_0_hits": 1183,
    "total_logs": 8882,
    "hits": 0,
    "failed": 0,
    "failed_contracts": [],
    "never_attempted": 0,
    "complete": True,
    "note": (
        "Ankr getLogs address-filtered per contract, window 132061862-132070121, from list run88-inbound-contracts.json (1183 contracts = "
        "run87 list 1127 + 56 run-88 deployment addresses). Full pass a (400, 5,858 logs) + b1 (200, 1,932) + b2 (200, 517) + b3 (383, 575) = "
        "8,882 logs, 0 hits, 0 failed. 3 truncated contracts, all topic-filtered to 0 logs (0x1de4... AFeng sale, 0x55d398... USDT, "
        "0x63de... AGC). RUN-88 WINDOW INBOUND FULLY CLOSED. Chunk a first attempt died silently at 125/400 (service-restart pattern) and "
        "was re-run in full; re-run completed with 0 failed. NOTE: inbound chunk output files are now correctly named run88-inbound88-*.json "
        "(filename quirk from run 87 fixed)."
    ),
}

s["next_run_note"] = (
    "Next run sent-tx window starts from block 132070122. RETRY run 89: (1) Pair token0/token1 reads for 0xa6e6... pair "
    "0x9fac925655fa4985ab4fe2fe9e0ca8ae323cc9da and 0x887c... pair 0xa9fa6efb21c252b7d4ab81d19a07ee4ecf6d2c97 "
    "(fast_rpc race returns None / 'all endpoints failed', 6 consecutive runs - persistently unreadable, unverified not absence), "
    "plus 0x2bfb pair 0x782671f637bf1a01de482824c4b2520bc58a5a4b, 0xc459 pair 0xeca06856c88fcdf1506886431a079d3f2565ca82, and new rotation "
    "0x43c8 pair 0xaafebb5244e2e546f7cd18a2c89f85bbee03f1e0 (unreadable run 88 only, transient outage - retry opportunistically, not an anomaly). "
    "c459 name()/symbol() CONFIRMED empty strings run 87 (not transient) - consistent with machine-token pattern. "
    "(2) Run-88 inbound list for run 89 = run88 list (1183) unless run 89's own sent pass finds new deployments to add. "
    "(3) Run-88 window inbound FULLY CLOSED (1183/1183, 8,882 logs, 0 hits). "
    "(4) 0x79cd... rotation was still filling at 18 wallets at run-88 window end - expect it at 27 wallets in run 89; do NOT treat that growth "
    "as a new rotation. "
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
    "run 87 (TWO tokens 0x889a76e4d48169d0398828a36c57b64298577777 at 27 wallets + 0x42491efdffe0aea61799d12b79cfe6ad2a977777 at 27 wallets), "
    "run 88 (THREE tokens 0x43c8f55b12391671d1f00b04ba1ef6d1842e7777 + 0x3d1201ea0d559e7071bc42d24e1494c6d7547777 + 0xeae0936e2f9ecb0a1acac8c5b9e43f86d3d37777 at 27 wallets each "
    "+ 0x79cd174ca3ec25c06ff5fddae365643f73d77777 at 18 wallets, rotation in progress) "
    "auto-mint BLOCKED at guard (c) - do not re-signal or re-report the block unless a new mint/buy fact appears for those contracts "
    "(e.g. a genuine free-mint path). Per the 2026-11-06 ~18:30 machine-token fast-path amendment, routine machine-token rotations are "
    "recorded in state WITHOUT a chat report (no full verification per run); report only on anomaly (buy size far off norm, name/symbol appears, "
    "website, or free-mint path). Paid fact: run88 THREE NEW rotations at 27 wallets (identical set) + FOURTH at 18 wallets (subset, still filling), "
    "all routine class-norm sizes, no anomaly - state-only, no chat report; run-87 tokens 0x889a.../0x4249... 0 wallets (1st quiet run after debut); run-86 tokens "
    "0x2bfb.../0xc459... 0 wallets (2nd quiet run after debut); run-85 token 0x2717... 0 wallets (3rd quiet run); run-82 tokens 0xd468.../0xa6e6.../0x887c... "
    "all 0 wallets (6th quiet run after debut); run-81 tokens 0 wallets (7th quiet run); run-80 token 0 wallets (8th quiet run); "
    "GrokBot 0xfcd0... absent (0 wallets) - 29th consecutive quiet run (59, 61-88) after the run-60 burst; CORLA-97af 0 wallets; "
    "CORLA 0x4a9c 0 wallets; all run-64/65 ASI contracts 0 wallets; all run-66/68/69/70/71/72/73/74/75/76/77/78/79 machine tokens 0 wallets. "
    "Run 88 had 56 deployments (third deployment run in a row after 16 in run 87 and 36 in run 86), in 4 bursts ~18 min apart; all 56 addresses added to the run-88 inbound list (0 hits). "
    "AFeng 2 txs (1 sale call 0x1de4... value 0, 13 logs, no mint + 1 approval to SLIME); future1001.ai 0 txs; 0x2325... 0 txs; 0x8e96... 0 txs; 0x5b2f... 0 txs. "
    "SCRIPT LESSON (run 85, FIXED run 86): when copying runNN-receipts.py for the next run, sed-replace the two hardcoded json.dump output paths too "
    "(runNN-receipts.json / runNN-paid.json) - run 88's copy was verified correct before running (dumps to run88-receipts.json/run88-paid.json). "
    "PROCESS LESSON (run 86): the receipts pass died silently at 420/461 (service-restart pattern, same as runs 82/84) - the partial-file resume worked; "
    "always re-run the same script to resume rather than re-fetching from scratch. Run 88 receipts completed in one attempt, no resume needed; "
    "BUT inbound chunk a died silently at 125/400 in run 88 and had to be re-run in full (inbound script saves no partial) - same restart pattern. "
    "INBOUND FILENAME QUIRK FIXED run 88: chunk output files are now correctly named run88-inbound88-{a,b1,b2,b3}.json. "
    "Same-owner factory groups now also include 0x293f and 0x1103 (proven 2026-11-06 ~01:14 WIB, AGENTS.md) alongside the groups listed in the body."
)

json.dump(s, open(P, "w"), indent=1)
print("state updated; last_run now:", s["last_run"]["run"], "block_end:", s["last_run"]["block_end"])
print("machine_tokens:", len(s.get("machine_tokens", [])), "| signaled:", len(s.get("signaled_projects_over_20pct", [])))
print("inbound88 complete:", s["inbound_log_leg_run88"]["complete"])
