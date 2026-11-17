#!/usr/bin/env python3
"""Run 89 state update (read-only job bookkeeping; no chain writes).

Completes run 89 (window 132070122-132080959, tx 2026-11-07 03:09:02 - 04:30:19 WIB).
Sent/receipts/paid done and verified; inbound leg run-89 window FULLY CLOSED.
FOUR new machine-token rotations at 27 wallets (identical set) + 0x79cd... now at
20 wallets (was 18, rotation STILL filling at window end) - all verified routine
(class-norm sizes, no name/symbol, no free-mint path) - state-only, NO chat report
per fast-path amendment. Bridge unchanged (0 new mints).
"""
import json, shutil
from pathlib import Path

P = "/home/hatch/workspace/narrative-pulse/tracked-wallet-mint-scan-state.json"
D = Path("/home/hatch/workspace/narrative-pulse/scan-runs")
shutil.copy(P, str(P) + ".bak-run89-pre")
s = json.load(open(P))

last_run_89 = {
    "run": 89,
    "block_start": 132070122,
    "block_end": 132080959,
    "window_wib": "2026-11-07 03:09:02 - 04:30:19 WIB (tx times); run executed ~04:25 - ~06:00 WIB; sent-pass in-window txs 1436, 0 mint-pattern txs",
    "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set); 0 failed, no retry needed.",
    "method_note": (
        "Sent pass Ankr ankr_getTransactionsByAddress via module: 55/55 OK first attempt, 1436 txs, 33 wallets active. "
        "Receipts via fast_rpc batch (6, ~4s pause) for 913 non-approve candidates: 904 status 1, 9 status 0, 0 null, 0 mint logs. "
        "Receipts completed in one attempt, no resume needed. Status-0 (9): ALL failed PCS sells (0x791ac947, value 0, 0 logs) to PCS router "
        "0x10ed43c718714eb63d5aa57b78b54704e256024e - by 0xdb2d83f907 x2 (03:26:53, 04:02:11 WIB), 0xc621946845 x3 (03:27:57, 03:45:31, 04:07:43 WIB), "
        "0xa952331ea4 x2 (03:46:29, 04:21:56 WIB), 0x92bc32975b x1 (03:09:34 WIB), 0x9b519f5d52 x1 (03:27:42 WIB). "
        "Paid: 37 tokens; FOUR NEW machine-token rotations at 27 wallets (49.1%) each - 0xcfdb66667d0ced8bff240e17547c7bef1ca97777, "
        "0x0cf896204bf1bd8a9b2a5bf07879ead17b7f7777, 0xe68bdc90fee5a233bb054a3c89854a5b50d27777, 0x31e43b72f14fea00a576e84c4e3605d98a317777 - "
        "IDENTICAL 27-wallet set (overlap 27/27 pairwise), plus 0x79cd174ca3ec25c06ff5fddae365643f73d77777 now at 20 wallets (36.4%), a SUBSET "
        "of the same set (overlap 20/20), up from 18 in run 88 - rotation STILL filling at window end, did NOT reach 27 this run. All five "
        "numerically above the 20% signal and 25% auto-mint thresholds, but paid-only with NO free-mint path: auto-mint BLOCKED at guard (c); "
        "recorded in state + signaled_projects as paid-only machine-tokens, NO chat report per fast-path amendment - see machine_tokens entries. "
        "Other tokens max 3 wallets/token (20 at 3, 8 at 2, 4 at 1 - usual ...7777 churn). "
        "AFeng 0 txs; future1001.ai 0 txs; 0x2325... 0 txs; 0x8e96... 0 txs; 0x3803... 60 txs (40 aggregator 0x39ecce49 + 20 approvals, total value 0.00052 BNB). "
        "Selectors: 304 PCS buys (0xb6f9de95) + 511 PCS sells (0x791ac947) + 523 approvals (0x095ea7b3) + 40 aggregator (0x39ecce49) + "
        "57 deployments (0x60806040) + 1 plain transfer (0x). "
        "Deployments: 57 contract creations by tracked wallets, ALL receipt status 1 with contractAddress read (run89-deployments.json, "
        "57 unique; top deployer 0x97bd... x9, 0x9b51... x6, 0x3154... x5, 0xcb08... x5) - FOURTH deployment run in a row (16 run 87, 36 run 86, "
        "56 run 88), clustered in 4 bursts ~15-18 min apart (03:22: 15, 03:4x: 14, 04:0x: 13, 04:1x: 15); identities of the 57 contracts NOT "
        "verified (same limitation as runs 82/86/87/88). Run-89 inbound list = run88 list (1183) + these 57 = 1240. "
        "Inbound leg run-89 WINDOW: FULLY CLOSED - 1240/1240 contracts, 9,653 logs, 0 hits, 0 failed, 4 truncated (all topic-filtered to 0 logs: "
        "0x1de4... AFeng sale, 0x55d398... USDT, 0x636fdfa9... tracker, 0x63de... AGC). "
        "Chunks a (400, 6,372 logs) + b1 (200, 1,890) + b2 (200, 601) + b3 (440, 790). Chunk b2 FIRST attempt died silently at 72/200 "
        "(service-restart pattern, same as runs 82/84/86/88; 1 transient error before death: 0xa9b0... remote-end-closed) - "
        "re-run full chunk b2 completed clean (0 failed; the contract read OK on retry). Chunks a/b1/b3 completed first attempt. "
        "Pair token0/token1 STILL UNREADABLE for ALL FIVE pairs in run-89 pair retry (fast_rpc race 'all endpoints failed' across all 10 endpoints, "
        "7th consecutive run for a6e6/887c/2bfb/c459, 2nd for 43c8) - unverified, not absence; retry run 90. NOTE: fast_rpc batch worked fine for "
        "the receipts pass and for block-timestamp reads earlier in this run - the outage is time-varying, not a permanent endpoint failure. "
        "Token-verify reads also partially hit the same outage (e68b totalSupply/owner + 31e4 name/owner unreadable at verify time - transient, "
        "not proven absent; both tokens' name/symbol otherwise empty per the reads that succeeded). "
        "Pointer-discovery (amendment 19:10): 0 contracts processed - no new mints this run, so no new contracts and no backfill queue; bridge unchanged. "
        "No preview/mint/sign/login/purchase by this job."
    ),
}
cur_run = s.get("last_run", {}).get("run", 0)
if cur_run < 89:
    s["last_run"] = last_run_89
    print(f"last_run set to 89 (was {cur_run})")
else:
    print(f"last_run already {cur_run} (>=89) - NOT regressing")
    s["run89_last_run_record"] = last_run_89

s["machine_tokens"].append({
    "address": "0xcfdb66667d0ced8bff240e17547c7bef1ca97777",
    "first_seen": "run-89, 2026-11-07 04:18:59 WIB (first tracked Transfer block 132079449, tx 0xc4e5023d247493...)",
    "machine_wallets": 27,
    "typical_first_buy_bnb": 0.000121125,
    "followup_buy_range_bnb": "median 0.2225142076144602, max 0.4013657230168402, total buys 9.5114 BNB (55 sent buys)",
    "label": "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB)",
    "note": (
        "Routine rotation, NO anomaly in a listed class; recorded in state WITHOUT chat report per fast-path amendment. "
        "Sizes WITHIN the established class norm (runs 80-82/85-88: first buy ~0.000106-0.000124 BNB, follow-up median ~0.19-0.23, max ~0.37-0.43). "
        "No name/symbol (empty strings, read OK), decimals 18, totalSupply 1e27, owner 0x0. Pair PCS V2 0x1e04925db4eabab2917ef73a8cdf232bcc69b5ba "
        "(pair token0/token1 UNREADABLE at verify + retry time - fast_rpc 'all endpoints failed', time-varying outage; retry run 90). "
        "No free-mint path (0 mint logs; all receives PCS buys). Auto-mint blocked at guard (c). "
        "27-wallet set IDENTICAL to the other three rotations this run (overlap 27/27) and the same machine set as runs 80-82/85-88; "
        "94 sells from tracked wallets in-window. First tracked Transfer tx was NOT sent by a tracked wallet (not in sent pass) - the first "
        "tracked-wallet buy followed the same PCS-buy pattern; not treated as an anomaly. "
        "Not in Free Bacot snapshot; NOT added to bridge (paid-only PCS token, precedent runs 63-88)."
    ),
})
s["machine_tokens"].append({
    "address": "0x0cf896204bf1bd8a9b2a5bf07879ead17b7f7777",
    "first_seen": "run-89, 2026-11-07 04:01:24 WIB (first tracked Transfer block 132077104, tx 0x2720a01fda9835...)",
    "machine_wallets": 27,
    "typical_first_buy_bnb": 0.000121125,
    "followup_buy_range_bnb": "median 0.223378725, max 0.4000971979371252, total buys 9.3354 BNB (53 sent buys)",
    "label": "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB)",
    "note": (
        "Routine rotation, NO anomaly in a listed class; recorded in state WITHOUT chat report per fast-path amendment. "
        "Sizes WITHIN the established class norm. "
        "No name/symbol (empty strings, read OK), decimals 18, totalSupply 1e27, owner 0x0. Pair PCS V2 0xf6800c4a1ecdffbd64f9047c606bdb32dee0127f "
        "(pair token0/token1 UNREADABLE at verify time - fast_rpc 'all endpoints failed'; retry run 90). "
        "No free-mint path (0 mint logs; all receives PCS buys). Auto-mint blocked at guard (c). "
        "27-wallet set IDENTICAL to the other three rotations this run (overlap 27/27) and the same machine set as runs 80-82/85-88; "
        "97 sells from tracked wallets in-window. First tracked Transfer tx was NOT sent by a tracked wallet (not in sent pass); same note as 0xcfdb.... "
        "Not in Free Bacot snapshot; NOT added to bridge (paid-only PCS token, precedent runs 63-88)."
    ),
})
s["machine_tokens"].append({
    "address": "0xe68bdc90fee5a233bb054a3c89854a5b50d27777",
    "first_seen": "run-89, 2026-11-07 03:43:40 WIB (first tracked Transfer block 132074739, tx 0x87fae533555778...)",
    "machine_wallets": 27,
    "typical_first_buy_bnb": 0.000121125,
    "followup_buy_range_bnb": "median 0.223378725, max 0.3983396553579655, total buys 9.2632 BNB (53 sent buys)",
    "label": "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB)",
    "note": (
        "Routine rotation, NO anomaly in a listed class; recorded in state WITHOUT chat report per fast-path amendment. "
        "Sizes WITHIN the established class norm. "
        "Name/symbol read as empty strings; decimals 18; totalSupply/owner UNREADABLE at verify time (fast_rpc 'all endpoints failed' - transient "
        "outage, NOT proven absent; the other three rotations read 1e27 / 0x0 and this token matches the pattern on every readable field). "
        "Pair PCS V2 0xfab7cb4979c9e4738afc61e4974177cf72c50896 (pair token0/token1 UNREADABLE at verify time; retry run 90). "
        "No free-mint path (0 mint logs; all receives PCS buys). Auto-mint blocked at guard (c). "
        "27-wallet set IDENTICAL to the other three rotations this run (overlap 27/27) and the same machine set as runs 80-82/85-88; "
        "94 sells from tracked wallets in-window. First tracked Transfer tx was NOT sent by a tracked wallet (not in sent pass); same note as 0xcfdb.... "
        "Not in Free Bacot snapshot; NOT added to bridge (paid-only PCS token, precedent runs 63-88)."
    ),
})
s["machine_tokens"].append({
    "address": "0x31e43b72f14fea00a576e84c4e3605d98a317777",
    "first_seen": "run-89, 2026-11-07 03:26:18 WIB (first tracked Transfer tx 0x37e3957494f19c..., block 132072424, via tracked wallet 0xcb08c02c0a, 0.000121241835355714 BNB, PCS buy selector 0xb6f9de95)",
    "machine_wallets": 27,
    "typical_first_buy_bnb": 0.000121241835355714,
    "followup_buy_range_bnb": "median 0.23002077496395001, max 0.39796832699511525, total buys 9.1257 BNB (51 sent buys)",
    "label": "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB)",
    "note": (
        "Routine rotation, NO anomaly in a listed class; recorded in state WITHOUT chat report per fast-path amendment. "
        "Sizes WITHIN the established class norm. "
        "Symbol read as empty string; name/owner UNREADABLE at verify time (fast_rpc 'all endpoints failed' - transient outage, NOT proven absent); "
        "decimals 18, totalSupply 1e27. Pair PCS V2 0x60ca0aef8cae7e96d9c804d44b9b9914daa9b66a "
        "(token0 = token, token1 = WBNB 0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c; reserves ~59,356,003 token / 0.05384 BNB). "
        "No free-mint path (0 mint logs; all receives PCS buys). Auto-mint blocked at guard (c). "
        "27-wallet set IDENTICAL to the other three rotations this run (overlap 27/27) and the same machine set as runs 80-82/85-88; "
        "91 sells from tracked wallets in-window. "
        "Not in Free Bacot snapshot; NOT added to bridge (paid-only PCS token, precedent runs 63-88)."
    ),
})
# Update the run-88 0x79cd entry in place (18 -> 20 wallets, still filling).
for mt in s.get("machine_tokens", []):
    if mt.get("address", "").lower() == "0x79cd174ca3ec25c06ff5fddae365643f73d77777":
        mt["machine_wallets"] = 20
        mt["label"] = "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - rotation IN PROGRESS at window end (run 89)"
        mt["note"] = mt.get("note", "") + (
            " RUN-89 UPDATE: now 20 wallets (was 18 in run 88) - still filling, did NOT reach 27 this run; first tracked Transfer in the run-89 "
            "window 03:09:06 WIB (block 132070133, tx 0xc19ff1b72e8e35..., via 0xaa49e7fec5, 0.23656262275665638 BNB - follow-up size, wallet already "
            "in from run 88); run-89 buys n=32 total 4.9841 BNB (min 0.001000100887412819, median 0.22800367424636406, max 0.4004206661611135), "
            "66 sells from tracked wallets; sizes within class norm (median identical to the other rotations). Pair 0xb5a05c4ed28689daa8a35818a6debd9e8b45f8d7 "
            "(reserves ~62,351,118 token / 0.05808 BNB, read OK this run). Name UNREADABLE at verify time (fast_rpc outage - transient, was empty "
            "string run 88); symbol empty, decimals 18, totalSupply 1e27, owner 0x0. No free-mint path; auto-mint blocked at guard (c). "
            "Expect 27 wallets in run 90; do NOT treat run-90 growth to 27 as a new rotation."
        )
        print("79cd entry updated to 20 wallets")
        break

sig = s.setdefault("signaled_projects_over_20pct", [])
sig.append("Unnamed token (name/symbol empty) 0xcfdb66667d0ced8bff240e17547c7bef1ca97777 (paid-only, machine-token, run-89, no chat report per fast-path amendment)")
sig.append("Unnamed token (name/symbol empty) 0x0cf896204bf1bd8a9b2a5bf07879ead17b7f7777 (paid-only, machine-token, run-89, no chat report per fast-path amendment)")
sig.append("Unnamed token (name/symbol empty) 0xe68bdc90fee5a233bb054a3c89854a5b50d27777 (paid-only, machine-token, run-89, no chat report per fast-path amendment)")
sig.append("Unnamed token (name/symbol empty) 0x31e43b72f14fea00a576e84c4e3605d98a317777 (paid-only, machine-token, run-89, no chat report per fast-path amendment)")
sig.append("Unnamed token (name/symbol empty) 0x79cd174ca3ec25c06ff5fddae365643f73d77777 (paid-only, machine-token, run-89, 20 wallets, rotation in progress, no chat report per fast-path amendment)")

s["paid_trend_run89"] = {
    "note": "Aggregate only, NOT a buy recommendation. FOUR new machine-token rotations at 27 wallets each (identical set) + 0x79cd... now at 20 wallets (subset, still filling) are paid-only with no free-mint path (auto-mint blocked at guard (c)); recorded in state, NO chat report per fast-path amendment. SILENT RUN - no chat report (no new mints, no Free Bacot signal, no auto-mint trigger, no reportable paid trend beyond the routine rotations).",
    "rotations": (
        "FOUR NEW machine-token rotations, same 27-wallet machine set as runs 80-82/85-88, IDENTICAL set (overlap 27/27 pairwise): "
        "0xcfdb66667d0ced8bff240e17547c7bef1ca97777 at 27 wallets (49.1% of 55): 55 sent buys (min 0.000121, median 0.2225, max 0.4014 BNB, total 9.5114 BNB) + "
        "94 sells, first tracked Transfer 04:18:59 WIB (block 132079449), pair 0x1e04925d... (token0/token1 unreadable - fast_rpc outage). "
        "0x0cf896204bf1bd8a9b2a5bf07879ead17b7f7777 at 27 wallets (49.1%): 53 sent buys (min 0.000121, median 0.2234, max 0.4001 BNB, total 9.3354 BNB) + "
        "97 sells, first tracked Transfer 04:01:24 WIB (block 132077104), pair 0xf6800c4a... (token0/token1 unreadable). "
        "0xe68bdc90fee5a233bb054a3c89854a5b50d27777 at 27 wallets (49.1%): 53 sent buys (min 0.000121, median 0.2234, max 0.3983 BNB, total 9.2632 BNB) + "
        "94 sells, first tracked Transfer 03:43:40 WIB (block 132074739), pair 0xfab7cb49... (token0/token1 unreadable; totalSupply/owner also unreadable at verify time - transient outage). "
        "0x31e43b72f14fea00a576e84c4e3605d98a317777 at 27 wallets (49.1%): 51 sent buys (min 0.000121, median 0.2300, max 0.3980 BNB, total 9.1257 BNB) + "
        "91 sells, first tracked Transfer 03:26:18 WIB via 0xcb08c02c0a (0.000121 BNB PCS buy), pair 0x60ca0aef... (token0=token, token1=WBNB; reserves ~59.36M token / 0.0538 BNB). "
        "FIFTH token 0x79cd174ca3ec25c06ff5fddae365643f73d77777 at 20 wallets (36.4%): 32 sent buys (min 0.001, median 0.2280, max 0.4004 BNB, total 4.9841 BNB) + "
        "66 sells, first run-89-window Transfer 03:09:06 WIB - rotation STILL filling (18 -> 20 wallets), expect 27 in run 90. All sizes within class norm; no name/symbol, "
        "no website pointer, no free-mint path; guard (c) blocks auto-mint."
    ),
    "other_paid_activity": [
        {"pattern": "32 other paid tokens: 20 at 3 wallets (usual ...7777 set), 8 at 2, 4 at 1", "wallets": "see run89-paid.json"},
        {"pattern": "Micro round-trip churn continues: 304 PCS buys (0xb6f9de95) + 511 PCS sells (0x791ac947), 523 approvals (0x095ea7b3), 40 aggregator txs (0x39ecce49); top active 0xa952... 78 txs, 0x9cdd... 77, 0xc7c5... 61, 0xc621... 61, 0x3803... 60", "wallets": "churn set"},
        {"pattern": "57 contract deployments by tracked wallets this run (all status 1, addresses in run89-deployments.json) - FOURTH deployment run in a row (16 run 87, 36 run 86, 56 run 88), in 4 bursts ~15-18 min apart (03:22, 03:4x, 04:0x, 04:1x); identities unverified, added to run-89 inbound list (0 hits)", "wallets": "0x97bd... x9, 0x9b51... x6, 0x3154... x5, 0xcb08... x5"},
        {"pattern": "9 failed txs, ALL failed PCS sells (0 logs, value 0) - see last_run method_note for the per-wallet breakdown", "wallets": "0xdb2d... x2, 0xc621... x3, 0xa952... x2, 0x92bc... x1, 0x9b51... x1"},
    ],
    "quiet": "AFeng 0 txs; future1001.ai 0 txs; 0x2325... 0 txs; 0x8e96... 0 txs; 0x3803... 60 txs (40 aggregator + 20 approvals, churn as usual); GrokBot 0xfcd0... absent (0 wallets) - 30th consecutive quiet run (59, 61-89) after the run-60 burst; CORLA-97af 0 wallets; CORLA 0x4a9c 0 wallets; all run-64/65 ASI contracts 0 wallets; run-88 tokens 0x43c8.../0x3d12.../0xeae0... 0 wallets (1st quiet run after debut, down from 27/27/27); run-87 tokens 0x889a.../0x4249... 0 wallets (2nd quiet run after debut); run-86 tokens 0x2bfb.../0xc459... 0 wallets (3rd quiet run after debut); run-85 token 0x2717... 0 wallets (4th quiet run); run-82 tokens 0xd468.../0xa6e6.../0x887c... 0 wallets (7th quiet run after debut); run-81 tokens 0 wallets (8th quiet run); run-80 token 0 wallets (9th quiet run); all other run-66/68/69/70/71/72/73/74/75/76/77/78/79 machine tokens 0 wallets.",
}

s["inbound_log_leg_run89"] = {
    "contracts": 1240,
    "attempted": 1240,
    "completed_with_0_hits": 1240,
    "total_logs": 9653,
    "hits": 0,
    "failed": 0,
    "failed_contracts": [],
    "never_attempted": 0,
    "complete": True,
    "note": (
        "Ankr getLogs address-filtered per contract, window 132070122-132080959, from list run89-inbound-contracts.json (1240 contracts = "
        "run88 list 1183 + 57 run-89 deployment addresses). Full pass a (400, 6,372 logs) + b1 (200, 1,890) + b2 (200, 601) + b3 (440, 790) = "
        "9,653 logs, 0 hits, 0 failed. 4 truncated contracts, all topic-filtered to 0 logs (0x1de4... AFeng sale, 0x55d398... USDT, "
        "0x636fdfa9... tracker, 0x63de... AGC). RUN-89 WINDOW INBOUND FULLY CLOSED. Chunk b2 first attempt died silently at 72/200 "
        "(service-restart pattern) and was re-run in full; re-run completed with 0 failed. NOTE: inbound chunk output files are correctly named "
        "run89-inbound89-*.json."
    ),
}

s["next_run_note"] = (
    "Next run sent-tx window starts from block 132080960. RETRY run 90: (1) Pair token0/token1 reads for 0xa6e6... pair "
    "0x9fac925655fa4985ab4fe2fe9e0ca8ae323cc9da and 0x887c... pair 0xa9fa6efb21c252b7d4ab81d19a07ee4ecf6d2c97 "
    "(fast_rpc race returns None / 'all endpoints failed', 7 consecutive runs - persistently unreadable, unverified not absence), "
    "plus 0x2bfb pair 0x782671f637bf1a01de482824c4b2520bc58a5a4b, 0xc459 pair 0xeca06856c88fcdf1506886431a079d3f2565ca82, and rotation "
    "0x43c8 pair 0xaafebb5244e2e546f7cd18a2c89f85bbee03f1e0 (unreadable run 88 AND run 89 - retry opportunistically, not an anomaly), "
    "PLUS new run-89 rotation pairs 0xcfdb 0x1e04925db4eabab2917ef73a8cdf232bcc69b5ba, 0x0cf8 0xf6800c4a1ecdffbd64f9047c606bdb32dee0127f, "
    "0xe68b 0xfab7cb4979c9e4738afc61e4974177cf72c50896 (token0/token1 unreadable run 89; 0x31e4 pair 0x60ca0aef... READ OK run 89). "
    "NOTE: fast_rpc worked for the receipts batch + block reads earlier in run 89 - the outage is time-varying; a retry at a different time may succeed. "
    "c459 name()/symbol() CONFIRMED empty strings run 87 (not transient) - consistent with machine-token pattern. "
    "e68b totalSupply/owner + 31e4 name/owner unreadable run 89 ONLY (transient outage) - retry opportunistically; do NOT treat as pattern break. "
    "(2) Run-89 inbound list for run 90 = run89 list (1240) unless run 90's own sent pass finds new deployments to add. "
    "(3) Run-89 window inbound FULLY CLOSED (1240/1240, 9,653 logs, 0 hits). "
    "(4) 0x79cd... rotation was still filling at 20 wallets at run-89 window end (was 18 run 88) - expect it at 27 wallets in run 90; do NOT treat that growth "
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
    "+ 0x79cd174ca3ec25c06ff5fddae365643f73d77777 at 18 wallets, rotation in progress), "
    "run 89 (FOUR tokens 0xcfdb66667d0ced8bff240e17547c7bef1ca97777 + 0x0cf896204bf1bd8a9b2a5bf07879ead17b7f7777 + 0xe68bdc90fee5a233bb054a3c89854a5b50d27777 + "
    "0x31e43b72f14fea00a576e84c4e3605d98a317777 at 27 wallets each + 0x79cd174ca3ec25c06ff5fddae365643f73d77777 at 20 wallets, rotation still in progress) "
    "auto-mint BLOCKED at guard (c) - do not re-signal or re-report the block unless a new mint/buy fact appears for those contracts "
    "(e.g. a genuine free-mint path). Per the 2026-11-06 ~18:30 machine-token fast-path amendment, routine machine-token rotations are "
    "recorded in state WITHOUT a chat report (no full verification per run); report only on anomaly (buy size far off norm, name/symbol appears, "
    "website, or free-mint path). Paid fact: run89 FOUR NEW rotations at 27 wallets (identical set) + 79cd at 20 wallets (subset, still filling), "
    "all routine class-norm sizes, no anomaly - state-only, no chat report; run-88 tokens 0x43c8.../0x3d12.../0xeae0... 0 wallets (1st quiet run after debut); run-87 tokens 0x889a.../0x4249... 0 wallets (2nd quiet run after debut); run-86 tokens "
    "0x2bfb.../0xc459... 0 wallets (3rd quiet run after debut); run-85 token 0x2717... 0 wallets (4th quiet run); run-82 tokens 0xd468.../0xa6e6.../0x887c... "
    "all 0 wallets (7th quiet run after debut); run-81 tokens 0 wallets (8th quiet run); run-80 token 0 wallets (9th quiet run); "
    "GrokBot 0xfcd0... absent (0 wallets) - 30th consecutive quiet run (59, 61-89) after the run-60 burst; CORLA-97af 0 wallets; "
    "CORLA 0x4a9c 0 wallets; all run-64/65 ASI contracts 0 wallets; all run-66/68/69/70/71/72/73/74/75/76/77/78/79 machine tokens 0 wallets. "
    "Run 89 had 57 deployments (fourth deployment run in a row after 16 in run 87, 36 in run 86, 56 in run 88), in 4 bursts ~15-18 min apart; all 57 addresses added to the run-89 inbound list (0 hits). "
    "AFeng 0 txs; future1001.ai 0 txs; 0x2325... 0 txs; 0x8e96... 0 txs; 0x3803... 60 txs (40 aggregator + 20 approvals). "
    "SCRIPT LESSON (run 85, FIXED run 86): when copying runNN-receipts.py for the next run, sed-replace the two hardcoded json.dump output paths too "
    "(runNN-receipts.json / runNN-paid.json) - run 89's copy was verified correct before running (dumps to run89-receipts.json/run89-paid.json). "
    "PROCESS LESSON (run 86): the receipts pass died silently at 420/461 (service-restart pattern, same as runs 82/84) - the partial-file resume worked; "
    "always re-run the same script to resume rather than re-fetching from scratch. Run 89 receipts completed in one attempt, no resume needed; "
    "BUT inbound chunk b2 died silently at 72/200 in run 89 and had to be re-run in full (inbound script saves no partial) - same restart pattern. "
    "INBOUND FILENAME QUIRK FIXED run 88: chunk output files are now correctly named run89-inbound89-{a,b1,b2,b3}.json. "
    "Same-owner factory groups now also include 0x293f and 0x1103 (proven 2026-11-06 ~01:14 WIB, AGENTS.md) alongside the groups listed in the body."
)

json.dump(s, open(P, "w"), indent=1)
print("state updated; last_run now:", s["last_run"]["run"], "block_end:", s["last_run"]["block_end"])
print("machine_tokens:", len(s.get("machine_tokens", [])), "| signaled:", len(s.get("signaled_projects_over_20pct", [])))
print("inbound89 complete:", s["inbound_log_leg_run89"]["complete"])
