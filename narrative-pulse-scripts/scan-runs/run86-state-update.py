#!/usr/bin/env python3
"""Run 86 state update (read-only job bookkeeping; no chain writes).

Completes run 86 (window 132047946-132054227, tx 2026-11-07 00:22:34 - 01:09:46 WIB).
Sent/receipts/paid done and verified; inbound leg run-86 window FULLY CLOSED.
TWO new machine-token rotations (0x2bfb... 27 wallets, 0xc459... 26 wallets) verified
routine (class-norm sizes, no name/symbol, no free-mint path) - state-only, NO chat
report per fast-path amendment. Bridge unchanged.
"""
import json, shutil
from pathlib import Path

P = "/home/hatch/workspace/narrative-pulse/tracked-wallet-mint-scan-state.json"
D = Path("/home/hatch/workspace/narrative-pulse/scan-runs")
shutil.copy(P, str(P) + ".bak-run86-pre")
s = json.load(open(P))

last_run_86 = {
    "run": 86,
    "block_start": 132047946,
    "block_end": 132054227,
    "window_wib": "2026-11-07 00:22:34 - 01:09:46 WIB (tx times); run executed ~01:05 - ~01:47 WIB; sent-pass in-window txs 722, 0 mint-pattern txs",
    "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set); 0 failed, no retry needed.",
    "method_note": (
        "Sent pass Ankr ankr_getTransactionsByAddress via module: 55/55 OK first attempt, 722 txs, 34 wallets active. "
        "Receipts via fast_rpc batch (6, ~4s pause) for 461 non-approve candidates: 454 status 1, 7 status 0, 0 null, 0 mint logs. "
        "First receipts attempt died silently at 420/461 (no output, process gone - same service-restart pattern as runs 82/84); resumed from "
        "run86-receipts-partial.json, remaining 41 fetched, completed. Status-0 (7): 6 failed PCS sells (0x791ac947, value 0, 0 logs) + 1 failed PCS "
        "buy 0x51d98b22... by 0x1cce4ec5 (0.2304 BNB, 0 logs, 00:52:42 WIB - a machine-size buy that failed on-chain). "
        "Paid: 27 tokens; TWO NEW machine-token rotations - 0x2bfb481d4812f329b6244450137096157a6b7777 at 27 wallets (49.1%) and "
        "0xc4599c77985efd0353b688b6127ad4f3399e7777 at 26 wallets (47.3%) - both numerically above the 20% signal and 25% auto-mint thresholds, but "
        "paid-only with NO free-mint path: auto-mint BLOCKED at guard (c); recorded in state + signaled_projects as paid-only machine-tokens, NO chat "
        "report per fast-path amendment - see machine_tokens entries. Other tokens max 3 wallets/token (9 at 3, 7 at 2, 9 at 1 - usual ...7777 churn). "
        "AFeng 34 txs (24 calls to 0x1de4... selector 0x4d819a2a values 0-~1.1 BNB, 8 approvals to ...7777 tokens, 1 plain transfer, 1 ERC20 transfer) - 0 mint "
        "logs; future1001.ai 0 txs; 0x2325... 0 txs; 0x8e96... 0 txs; 0x5b2f... 0 txs. "
        "Selectors: 137 PCS buys (0xb6f9de95) + 242 PCS sells (0x791ac947) + 261 approvals (0x095ea7b3) + 19 aggregator (0x39ecce49) + 36 deployments "
        "(0x60806040) + 24x 0x4d819a2a (AFeng) + 2 plain transfers (0x) + 1 ERC20 transfer (0xa9059cbb). "
        "Deployments: 36 contract creations by tracked wallets, ALL receipt status 1 with contractAddress read (run86-deployments.json, 36 unique); "
        "identities of the 36 contracts NOT verified (same limitation as run 82). Run-86 inbound list = run84 list (1075) + these 36 = 1111. "
        "Inbound leg run-86 WINDOW: FULLY CLOSED - 1111/1111 contracts, 10,104 logs, 0 hits, 0 failed, 5 truncated (all topic-filtered to 0 logs: "
        "0x1de4... AFeng sale, 0x55d398... USDT, 0x6288... AGC sale, 0x63de... AGC, 0x78573a...). Chunks a (400, 6,501 logs) + b1 (200, 2,629) + b2 (200, 391) + "
        "b3 (311, 583); a stalled ~4 min at segment 251-350 (high-log contracts, same as run 85) then completed without intervention. "
        "Pair token0/token1 for a6e6 (0x9fac...) and 887c (0xa9fa...) STILL UNREADABLE (fast_rpc race returns None; Ankr eth_call returns null) - "
        "persistently unreadable, 4th consecutive run; unverified, not absence; retry run 87. "
        "No preview/mint/sign/login/purchase by this job."
    ),
}
cur_run = s.get("last_run", {}).get("run", 0)
if cur_run < 86:
    s["last_run"] = last_run_86
    print(f"last_run set to 86 (was {cur_run})")
else:
    print(f"last_run already {cur_run} (>=86) - NOT regressing")
    s["run86_last_run_record"] = last_run_86

s["machine_tokens"].append({
    "address": "0x2bfb481d4812f329b6244450137096157a6b7777",
    "first_seen": "run-86, 2026-11-07 00:29:31 WIB (first tracked Transfer tx 0x82203f4c14dbf62c4f768ae57b9fa366faab9f4836cc52c47e5f98351d39f209, block 132049245)",
    "machine_wallets": 27,
    "typical_first_buy_bnb": 0.000109050454151017,
    "followup_buy_range_bnb": "median 0.223378725, max 0.37170389340055415, total buys 9.3875 BNB (55 sent buys)",
    "label": "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB)",
    "note": (
        "Routine rotation, NO anomaly in a listed class; recorded in state WITHOUT chat report per fast-path amendment. "
        "Sizes WITHIN the established class norm (runs 80-82/85: first buy ~0.000106-0.000124 BNB, follow-up median ~0.19-0.23, max ~0.37-0.40). "
        "No name/symbol (empty strings), decimals 18, totalSupply 1e27, owner 0x0. Pair PCS V2 0x782671f637bf1a01de482824c4b2520bc58a5a4b "
        "(token0/token1 unreadable via fast_rpc 'all endpoints failed' at read time - unverified, not absence; reserves unreadable for the same reason). "
        "No free-mint path (0 mint logs; all receives PCS buys). Auto-mint blocked at guard (c). "
        "27-wallet set = same machine set as runs 80-82/85; 98 sells from tracked wallets in-window (round-trip churn). "
        "NEW OBSERVATION (same class as run 85): first tracked Transfer (47,867.36 tokens) arrived via tx 0x82203f4c... NOT sent by a tracked wallet "
        "(56 Ankr Transfer-to-tracked logs vs 55 sent buys); still a plain PCS buy from the pair, 0 zero-from logs. "
        "Not in Free Bacot snapshot; NOT added to bridge (paid-only PCS token, precedent runs 63-85)."
    ),
})
s["machine_tokens"].append({
    "address": "0xc4599c77985efd0353b688b6127ad4f3399e7777",
    "first_seen": "run-86, 2026-11-07 00:54:34 WIB (first tracked Transfer tx 0xde2f132d9ab6d79f4c8f4913bc08c63b69144f2dd496a2f5df94704d0e0d4652, block 132051675)",
    "machine_wallets": 26,
    "typical_first_buy_bnb": 0.000121125,
    "followup_buy_range_bnb": "median 0.22947754197046055, max 0.3973800746008488, total buys 8.5569 BNB (48 sent buys)",
    "label": "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB)",
    "note": (
        "Routine rotation, NO anomaly in a listed class; recorded in state WITHOUT chat report per fast-path amendment. "
        "Sizes WITHIN the established class norm (runs 80-82/85: first buy ~0.000106-0.000124 BNB, follow-up median ~0.19-0.23, max ~0.37-0.40). "
        "Symbol '' (read OK); name() read FAILED transiently (fast_rpc 'all endpoints failed' at read time) - NOT a verified empty name, unverified not absence. "
        "Decimals 18, totalSupply 1e27, owner 0x0. Pair PCS V2 0xeca06856c88fcdf1506886431a079d3f2565ca82 "
        "(token0/token1 unreadable via fast_rpc 'all endpoints failed' at read time - unverified, not absence). "
        "No free-mint path (0 mint logs; all receives PCS buys). Auto-mint blocked at guard (c). "
        "26-wallet set = 2bfb set minus 0x1cce4ec5 (the wallet whose 0.2304 BNB buy failed on-chain this run); 84 sells from tracked wallets in-window. "
        "NEW OBSERVATION (same class as run 85): first tracked Transfer (63,988.46 tokens) arrived via tx 0xde2f132d... NOT sent by a tracked wallet "
        "(49 Ankr Transfer-to-tracked logs vs 48 sent buys); still a plain PCS buy from the pair, 0 zero-from logs. "
        "Not in Free Bacot snapshot; NOT added to bridge (paid-only PCS token, precedent runs 63-85)."
    ),
})

sig = s.setdefault("signaled_projects_over_20pct", [])
sig.append("Unnamed token (name/symbol empty) 0x2bfb481d4812f329b6244450137096157a6b7777 (paid-only, machine-token, run-86, no chat report per fast-path amendment)")
sig.append("Unnamed token (symbol empty; name unreadable transiently) 0xc4599c77985efd0353b688b6127ad4f3399e7777 (paid-only, machine-token, run-86, no chat report per fast-path amendment)")

s["paid_trend_run86"] = {
    "note": "Aggregate only, NOT a buy recommendation. TWO new machine-token rotations at 27 and 26 wallets are paid-only with no free-mint path (auto-mint blocked at guard (c)); recorded in state, NO chat report per fast-path amendment. SILENT RUN - no chat report (no new mints, no Free Bacot signal, no auto-mint trigger, no reportable paid trend beyond the routine rotations).",
    "rotations": (
        "TWO NEW machine-token rotations, same 27-wallet machine set as runs 80-82/85: "
        "0x2bfb481d4812f329b6244450137096157a6b7777 at 27 wallets (49.1% of 55): 55 sent buys (min 0.000109, median 0.2234, max 0.3717 BNB, total 9.3875 BNB) + "
        "1 proxy-routed buy + 98 sells, first tracked Transfer 00:29:31 WIB. "
        "0xc4599c77985efd0353b688b6127ad4f3399e7777 at 26 wallets (47.3% of 55): 48 sent buys (min 0.000121, median 0.2295, max 0.3974 BNB, total 8.5569 BNB) + "
        "1 proxy-routed buy + 84 sells, first tracked Transfer 00:54:34 WIB. Both sizes within class norm; no name/symbol, no website pointer, no free-mint path; guard (c) blocks auto-mint. "
        "The two sets overlap 26/26 (c459 set is 2bfb set minus 0x1cce4ec5)."
    ),
    "other_paid_activity": [
        {"pattern": "25 other paid tokens: 9 at 3 wallets (usual ...7777 set via trio 0x38031ca8a5/0xad94ee77d0/0xc7c5faa270), 7 at 2, 9 at 1", "wallets": "see run86-paid.json"},
        {"pattern": "Micro round-trip churn continues: 137 PCS buys (0xb6f9de95) + 242 PCS sells (0x791ac947), 261 approvals (0x095ea7b3), 19 aggregator txs (0x39ecce49), 24 AFeng calls to 0x1de4... (0x4d819a2a); top active 0xa952... 40 txs, 0x9cdd... 36, 0xc621... 34, AFeng 0xbf00... 34, 0xad94.../0x3803... 29 each", "wallets": "churn set"},
        {"pattern": "36 contract deployments by tracked wallets this run (all status 1, addresses in run86-deployments.json) - first deployment run after two deployment-free runs (84, 85); identities unverified, added to run-86 inbound list (0 hits)", "wallets": "15 deployers, incl. 0x97bd... x6, 0x3154... x5, 0xc621.../0xaa49.../0xcb08.../0xc0c8... x3 each"},
        {"pattern": "7 failed txs (all 0 logs): 6 PCS sells + 1 PCS buy 0.2304 BNB by 0x1cce4ec5 (machine-size buy, failed on-chain)", "wallets": "0xdb2d..., 0xc621... x2, 0x9cdd..., 0x1cce..., 0x92bc... x2"},
    ],
    "quiet": "AFeng 34 txs (0 mints); future1001.ai 0 txs; 0x2325... 0 txs; 0x8e96... 0 txs; 0x5b2f... 0 txs; GrokBot 0xfcd0... absent (0 wallets) - 27th consecutive quiet run (59, 61-86) after the run-60 burst; CORLA-97af 0 wallets; CORLA 0x4a9c 0 wallets; all run-64/65 ASI contracts 0 wallets; run-85 token 0x2717... 2 wallets (1st quiet run after debut, down from 27); run-82 tokens 0xd468.../0xa6e6.../0x887c... 0 wallets (4th quiet run after debut); run-81 tokens 0 wallets (5th quiet run); run-80 token 0 wallets (6th quiet run); all other run-66/68/69/70/71/72/73/74/75/76/77/78/79 machine tokens 0 wallets.",
}

s["inbound_log_leg_run86"] = {
    "contracts": 1111,
    "attempted": 1111,
    "completed_with_0_hits": 1111,
    "total_logs": 10104,
    "hits": 0,
    "failed": 0,
    "failed_contracts": [],
    "never_attempted": 0,
    "complete": True,
    "note": (
        "Ankr getLogs address-filtered per contract, window 132047946-132054227, from frozen list run86-inbound-contracts.json (1111 contracts = "
        "run84 list 1075 + 36 run-86 deployment addresses). Full pass a (400, 6,501 logs) + b1 (200, 2,629) + b2 (200, 391) + b3 (311, 583) = "
        "10,104 logs, 0 hits, 0 failed. 5 truncated contracts, all topic-filtered to 0 logs (0x1de4... AFeng sale, 0x55d398... USDT, 0x6288... AGC sale, "
        "0x63de... AGC, 0x78573a...). RUN-86 WINDOW INBOUND FULLY CLOSED. Chunk a stalled ~4 min at segment 251-350 (high-log contracts) then completed "
        "without intervention; b3's final segment (36 new deployment addresses) completed cleanly, 0 hits."
    ),
}

s["next_run_note"] = (
    "Next run sent-tx window starts from block 132054228. RETRY run 87: (1) Pair token0/token1 reads for 0xa6e6... pair "
    "0x9fac925655fa4985ab4fe2fe9e0ca8ae323cc9da and 0x887c... pair 0xa9fa6efb21c252b7d4ab81d19a07ee4ecf6d2c97 "
    "(fast_rpc race returns None + Ankr eth_call returns null, 4 consecutive runs - persistently unreadable, unverified not absence). "
    "Also unreadable at run-86 read time (fast_rpc 'all endpoints failed'): pair token0/token1 for BOTH new rotations "
    "(0x2bfb pair 0x782671f637bf1a01de482824c4b2520bc58a5a4b; 0xc459 pair 0xeca06856c88fcdf1506886431a079d3f2565ca82) and name() for 0xc459 - "
    "transient infra failure, not verified absence; retry opportunistically, do not re-report as anomaly. "
    "(2) Run-86 inbound list for run 87 = run86 list (1111) unless run 87's own sent pass finds new deployments to add. "
    "(3) Run-86 window inbound FULLY CLOSED (1111/1111, 10,104 logs, 0 hits). "
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
    "run 86 (TWO tokens 0x2bfb481d4812f329b6244450137096157a6b7777 at 27 wallets + 0xc4599c77985efd0353b688b6127ad4f3399e7777 at 26 wallets) "
    "auto-mint BLOCKED at guard (c) - do not re-signal or re-report the block unless a new mint/buy fact appears for those contracts "
    "(e.g. a genuine free-mint path). Per the 2026-11-06 ~18:30 machine-token fast-path amendment, routine machine-token rotations are "
    "recorded in state WITHOUT a chat report (no full verification per run); report only on anomaly (buy size far off norm, name/symbol appears, "
    "website, or free-mint path). Paid fact: run86 TWO NEW rotations 0x2bfb... (27 wallets) + 0xc459... (26 wallets), both routine class-norm sizes, "
    "no anomaly - state-only, no chat report; run-85 token 0x2717... 2 wallets (1st quiet run after debut); run-82 tokens 0xd468.../0xa6e6.../0x887c... "
    "all 0 wallets (4th quiet run after debut); run-81 tokens 0 wallets (5th quiet run); run-80 token 0 wallets (6th quiet run); "
    "GrokBot 0xfcd0... absent (0 wallets) - 27th consecutive quiet run (59, 61-86) after the run-60 burst; CORLA-97af 0 wallets; "
    "CORLA 0x4a9c 0 wallets; all run-64/65 ASI contracts 0 wallets; all run-66/68/69/70/71/72/73/74/75/76/77/78/79/80/81/82/85 machine tokens 0 wallets except 0x2717... (2). "
    "Run 86 had 36 deployments (first deployment run after two deployment-free runs 84-85); all 36 addresses added to the run-86 inbound list (0 hits). "
    "AFeng 34 txs (0 mints); future1001.ai 0 txs; 0x2325... 0 txs; 0x8e96... 0 txs; 0x5b2f... 0 txs. "
    "SCRIPT LESSON (run 85, FIXED run 86): when copying runNN-receipts.py for the next run, sed-replace the two hardcoded json.dump output paths too "
    "(runNN-receipts.json / runNN-paid.json) - run 86's copy was fixed before running (dumps to run86-receipts.json / run86-paid.json, verified). "
    "PROCESS LESSON (run 86): the receipts pass died silently at 420/461 (service-restart pattern, same as runs 82/84) - the partial-file resume worked; "
    "always re-run the same script to resume rather than re-fetching from scratch. "
    "Same-owner factory groups now also include 0x293f and 0x1103 (proven 2026-11-06 ~01:14 WIB, AGENTS.md) alongside the groups listed in the body."
)

json.dump(s, open(P, "w"), indent=1)
print("state updated; last_run now:", s["last_run"]["run"], "block_end:", s["last_run"]["block_end"])
print("machine_tokens:", len(s.get("machine_tokens", [])), "| signaled:", len(s.get("signaled_projects_over_20pct", [])))
print("inbound86 complete:", s["inbound_log_leg_run86"]["complete"])
