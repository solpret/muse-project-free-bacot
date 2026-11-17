#!/usr/bin/env python3
"""Run 90 state update (read-only job bookkeeping; no chain writes).

Completes run 90 (window 132080960-132093926, tx 2026-11-07 04:30:37 - 06:07:35 WIB).
Sent/receipts/paid done and verified; inbound leg run-90 window FULLY CLOSED.
FIVE new machine-token rotations (4 at 27 wallets, 1 at 26 wallets, identical/subset
set) - all verified routine (class-norm sizes, no name/symbol, no free-mint path) -
state-only, NO chat report per fast-path amendment. 0x79cd... STALLED at 20 wallets
(0 wallets this run, did NOT reach 27). Bridge unchanged (0 new mints).
"""
import json, shutil
from pathlib import Path

P = "/home/hatch/workspace/narrative-pulse/tracked-wallet-mint-scan-state.json"
D = Path("/home/hatch/workspace/narrative-pulse/scan-runs")
shutil.copy(P, str(P) + ".bak-run90-pre")
s = json.load(open(P))

last_run_90 = {
    "run": 90,
    "block_start": 132080960,
    "block_end": 132093926,
    "window_wib": "2026-11-07 04:30:37 - 06:07:35 WIB (tx times); run executed ~06:05 - ~08:00 WIB; sent-pass in-window txs 1674, 0 mint-pattern txs",
    "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set); 0 failed, no retry needed.",
    "method_note": (
        "Sent pass Ankr ankr_getTransactionsByAddress via module: 55/55 OK first attempt, 1674 txs, 33 wallets active. "
        "Receipts via fast_rpc batch (6, ~4s pause) for 1080 non-approve candidates: 1077 status 1, 3 status 0, 0 null, 0 mint logs. "
        "Receipts completed in one attempt, no resume needed. Status-0 (3): ALL failed PCS sells (0x791ac947, value 0, 0 logs) to PCS router "
        "0x10ed43c718714eb63d5aa57b78b54704e256024e - by 0xc621946845 (04:43:12 WIB), 0xb940e4cd40 (05:16:47 WIB), 0xa952331ea4 (04:39:52 WIB). "
        "Paid: 50 tokens; FIVE NEW machine-token rotations - 0x6a2590934e55671a6fab9fa8edca8da4960e7777, "
        "0x9f7ea7a4eaa7f39782caeb1ecab8176187e97777, 0x8c64aa82e861393bf760ee6d0eb29c0c60f07777, "
        "0xc1ab1e832da23f85a27aa2778f555d00319e7777 at 27 wallets (49.1%) each, IDENTICAL 27-wallet set (overlap 27/27 pairwise), plus "
        "0x1153607e323c42f93c82b80e1772f9cc626b7777 at 26 wallets (47.3%), a SUBSET of the same set (overlap 26/26; the one wallet not yet in "
        "is 0x2cc8192fc6 - rotation possibly still filling). All five numerically above the 20% signal and 25% auto-mint thresholds, but "
        "paid-only with NO free-mint path: auto-mint BLOCKED at guard (c); recorded in state + signaled_projects as paid-only machine-tokens, "
        "NO chat report per fast-path amendment - see machine_tokens entries. "
        "0x79cd174ca3ec25c06ff5fddae365643f73d77777: 0 wallets this run - rotation STALLED at 20 wallets, did NOT reach 27 as expected; "
        "1st quiet run after debut (runs 88-89 active). Other tokens max 3 wallets/token (25 at 3, 10 at 2, 10 at 1 - usual ...7777 churn). "
        "AFeng 0 txs; future1001.ai 0 txs; 0x2325... 0 txs; 0x8e96... 0 txs; 0x3803... 68 txs (43 aggregator 0x39ecce49 + 25 approvals, total value 0.00065 BNB). "
        "Selectors: 360 PCS buys (0xb6f9de95) + 569 PCS sells (0x791ac947) + 594 approvals (0x095ea7b3) + 43 aggregator (0x39ecce49) + "
        "107 deployments (0x60806040) + 1 plain transfer (0x). "
        "Deployments: 107 contract creations by tracked wallets, ALL receipt status 1 with contractAddress read (run90-deployments.json, "
        "107 unique; top deployer 0x97bd... x26, 0x1cce... x10, 0xf795... x9, 0x9b51... x9) - FIFTH deployment run in a row (16 run 87, 36 run 86, "
        "56 run 88, 57 run 89, 107 run 90); identities of the 107 contracts NOT verified (same limitation as runs 82/86/87/88/89). "
        "Run-90 inbound list = run89 list (1240) + these 107 = 1347. "
        "Inbound leg run-90 WINDOW: FULLY CLOSED - 1347/1347 contracts, 11,373 logs, 0 hits, 0 failed, 6 truncated (all topic-filtered to 0 logs: "
        "0x1de4... AFeng sale, 0x55d398... USDT, 0x6288..., 0x636fdfa9... tracker, 0x63de... AGC, 0x7857...). "
        "Chunks a (400, 6,730 logs) + b1 (200, 2,802 logs) + b2 (200, 796 logs) + b3 (547, 1,045 logs). Chunk b2 FIRST attempt died silently at "
        "100/200 (service-restart pattern, same as runs 82/84/86/88/89; a service restart also interrupted the operator session mid-run) - "
        "re-run full chunk b2 completed clean (0 failed). Chunks a/b1/b3 completed first attempt (chunk a + b3 each had one slow ~6-8 min stretch "
        "at contracts 150-200, then resumed on their own). "
        "Pair token0/token1 STILL UNREADABLE for ALL EIGHT pairs in run-90 pair retry (fast_rpc race 'all endpoints failed', 8th consecutive run "
        "for a6e6/887c/2bfb/c459, 3rd for 43c8, 1st for the three run-89 rotation pairs cfdb/0cf8/e68b) - unverified, not absence; retry run 91. "
        "NOTE: fast_rpc batch worked fine for the receipts pass and several token-verify reads succeeded in the same run - the outage is "
        "time-varying / per-call, not a permanent endpoint failure. Token-verify reads also partially hit the same outage (6a25 symbol, 9f7e "
        "name/symbol/owner, 8c64 totalSupply, c1ab symbol unreadable at verify time - transient, not proven absent; every other readable field "
        "matches the machine-token pattern). "
        "Pointer-discovery (amendment 19:10): 0 contracts processed - no new mints this run, and the backfill queue is empty (bridge 115 "
        "contracts, 0 not_evaluated); bridge unchanged. "
        "No preview/mint/sign/login/purchase by this job."
    ),
}
cur_run = s.get("last_run", {}).get("run", 0)
if cur_run < 90:
    s["last_run"] = last_run_90
    print(f"last_run set to 90 (was {cur_run})")
else:
    print(f"last_run already {cur_run} (>=90) - NOT regressing")
    s["run90_last_run_record"] = last_run_90

s["machine_tokens"].append({
    "address": "0x6a2590934e55671a6fab9fa8edca8da4960e7777",
    "first_seen": "run-90, 2026-11-07 05:49:31 WIB (first tracked Transfer block 132091517, tx 0xc79586b656bb..., via tracked wallet 0xcb08c02c0a, 0.000121241835355714 BNB, PCS buy selector 0xb6f9de95)",
    "machine_wallets": 27,
    "typical_first_buy_bnb": 0.000121241835355714,
    "followup_buy_range_bnb": "median 0.223378725, max 0.37873139373405734, total buys 9.8844 BNB (58 sent buys)",
    "label": "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB)",
    "note": (
        "Routine rotation, NO anomaly in a listed class; recorded in state WITHOUT chat report per fast-path amendment. "
        "Sizes WITHIN the established class norm (runs 80-82/85-89: first buy ~0.000106-0.000124 BNB, follow-up median ~0.19-0.23, max ~0.37-0.43). "
        "Name read as empty string; symbol UNREADABLE at verify time (fast_rpc 'all endpoints failed' - transient outage, NOT proven absent); "
        "decimals 18, totalSupply 1e27, owner 0x0. Pair PCS V2 0xa528208db86d680109abc6efff448dc896221ce4 "
        "(token0 = token, token1 = WBNB 0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c; reserves ~61,464,769 token / 0.05676 BNB). "
        "No free-mint path (0 mint logs; all receives PCS buys). Auto-mint blocked at guard (c). "
        "27-wallet set IDENTICAL to the other three 27-wallet rotations this run (overlap 27/27) and the same machine set as runs 80-82/85-89; "
        "97 sells from tracked wallets in-window. "
        "Not in Free Bacot snapshot; NOT added to bridge (paid-only PCS token, precedent runs 63-89)."
    ),
})
s["machine_tokens"].append({
    "address": "0x9f7ea7a4eaa7f39782caeb1ecab8176187e97777",
    "first_seen": "run-90, 2026-11-07 05:31:45 WIB (first tracked Transfer block 132089149, tx 0x7f3daea6706c..., via tracked wallet 0xcb08c02c0a, 0.000121125 BNB, PCS buy selector 0xb6f9de95)",
    "machine_wallets": 27,
    "typical_first_buy_bnb": 0.000121125,
    "followup_buy_range_bnb": "median 0.22410325416011004, max 0.4301606918903611, total buys 9.8832 BNB (58 sent buys)",
    "label": "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB)",
    "note": (
        "Routine rotation, NO anomaly in a listed class; recorded in state WITHOUT chat report per fast-path amendment. "
        "Sizes WITHIN the established class norm. "
        "Name/symbol/owner UNREADABLE at verify time (fast_rpc 'all endpoints failed' - transient outage, NOT proven absent; the other rotations "
        "read empty strings / 0x0 and this token matches the pattern on every readable field); decimals 18, totalSupply 1e27. "
        "Pair PCS V2 0x430e7ac91f57f618dff0114d1b981a20b90f0985 "
        "(token0 = token, token1 = WBNB; reserves ~52,078,151 token / 0.06628 BNB). "
        "No free-mint path (0 mint logs; all receives PCS buys). Auto-mint blocked at guard (c). "
        "27-wallet set IDENTICAL to the other three 27-wallet rotations this run (overlap 27/27) and the same machine set as runs 80-82/85-89; "
        "100 sells from tracked wallets in-window. "
        "Not in Free Bacot snapshot; NOT added to bridge (paid-only PCS token, precedent runs 63-89)."
    ),
})
s["machine_tokens"].append({
    "address": "0x8c64aa82e861393bf760ee6d0eb29c0c60f07777",
    "first_seen": "run-90, 2026-11-07 04:54:48 WIB (first tracked Transfer block 132084222, tx 0x952f8402655e..., via tracked wallet 0xcb08c02c0a, 0.000123921636510755 BNB, PCS buy selector 0xb6f9de95)",
    "machine_wallets": 27,
    "typical_first_buy_bnb": 0.000123921636510755,
    "followup_buy_range_bnb": "median 0.22416315536620893, max 0.4031044308723099, total buys 10.0000 BNB (58 sent buys)",
    "label": "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB)",
    "note": (
        "Routine rotation, NO anomaly in a listed class; recorded in state WITHOUT chat report per fast-path amendment. "
        "Sizes WITHIN the established class norm. "
        "Name/symbol read as empty strings; decimals 18; totalSupply UNREADABLE at verify time (fast_rpc 'all endpoints failed' - transient "
        "outage, NOT proven absent; the other rotations read 1e27 and this token matches the pattern on every readable field); owner 0x0. "
        "Pair PCS V2 0xa29fee30f7176ab4c40a258f1fa179eac871ab98 "
        "(token0 = token, token1 = WBNB; reserves ~74,486,540 token / 0.04659 BNB). "
        "No free-mint path (0 mint logs; all receives PCS buys). Auto-mint blocked at guard (c). "
        "27-wallet set IDENTICAL to the other three 27-wallet rotations this run (overlap 27/27) and the same machine set as runs 80-82/85-89; "
        "100 sells from tracked wallets in-window. "
        "Not in Free Bacot snapshot; NOT added to bridge (paid-only PCS token, precedent runs 63-89)."
    ),
})
s["machine_tokens"].append({
    "address": "0xc1ab1e832da23f85a27aa2778f555d00319e7777",
    "first_seen": "run-90, 2026-11-07 04:37:07 WIB (first tracked Transfer block 132081866, tx 0xebb9a22fdddc..., via tracked wallet 0xcb08c02c0a, 0.000121241835355714 BNB, PCS buy selector 0xb6f9de95)",
    "machine_wallets": 27,
    "typical_first_buy_bnb": 0.000121241835355714,
    "followup_buy_range_bnb": "median 0.223378725, max 0.3756084323795862, total buys 9.2924 BNB (53 sent buys)",
    "label": "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB)",
    "note": (
        "Routine rotation, NO anomaly in a listed class; recorded in state WITHOUT chat report per fast-path amendment. "
        "Sizes WITHIN the established class norm. "
        "Name read as empty string; symbol UNREADABLE at verify time (fast_rpc 'all endpoints failed' - transient outage, NOT proven absent); "
        "decimals 18, totalSupply 1e27, owner 0x0. Pair PCS V2 0xaac71a1eec286602f020ba6ea7047583d973857c "
        "(token0 = WBNB, token1 = token; reserves 0.06589 BNB / ~51,785,687 token). "
        "No free-mint path (0 mint logs; all receives PCS buys). Auto-mint blocked at guard (c). "
        "27-wallet set IDENTICAL to the other three 27-wallet rotations this run (overlap 27/27) and the same machine set as runs 80-82/85-89; "
        "98 sells from tracked wallets in-window. "
        "Not in Free Bacot snapshot; NOT added to bridge (paid-only PCS token, precedent runs 63-89)."
    ),
})
s["machine_tokens"].append({
    "address": "0x1153607e323c42f93c82b80e1772f9cc626b7777",
    "first_seen": "run-90, 2026-11-07 05:14:12 WIB (first tracked Transfer block 132086809, tx 0xc5d21d86f6ea..., via tracked wallet 0xcb08c02c0a, 0.000121241835355714 BNB, PCS buy selector 0xb6f9de95)",
    "machine_wallets": 26,
    "typical_first_buy_bnb": 0.000121241835355714,
    "followup_buy_range_bnb": "median 0.2301375, max 0.3716816138116324, total buys 9.5966 BNB (53 sent buys)",
    "label": "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - rotation possibly still filling at window end (run 90)",
    "note": (
        "Routine rotation, NO anomaly in a listed class; recorded in state WITHOUT chat report per fast-path amendment. "
        "Sizes WITHIN the established class norm. "
        "Name/symbol read as empty strings; decimals 18, totalSupply 1e27, owner 0x0. Pair PCS V2 0x2c1577fea68003ffd6b6e94e8472e0dd1155786b "
        "(token0 = token, token1 = WBNB; reserves ~60,623,343 token / 0.05556 BNB). "
        "No free-mint path (0 mint logs; all receives PCS buys). Auto-mint blocked at guard (c). "
        "26-wallet set is a SUBSET of the same 27-wallet machine set as the other four rotations this run (overlap 26/26); the one wallet not "
        "yet in is 0x2cc8192fc6 - rotation possibly still filling at window end (like 0x79cd... in runs 88-89), or that wallet skipped this token; "
        "do NOT treat run-91 growth to 27 as a new rotation. 98 sells from tracked wallets in-window. "
        "Not in Free Bacot snapshot; NOT added to bridge (paid-only PCS token, precedent runs 63-89)."
    ),
})
# Update the run-88/89 0x79cd entry in place (0 wallets run 90 - rotation STALLED at 20, did not reach 27).
for mt in s.get("machine_tokens", []):
    if mt.get("address", "").lower() == "0x79cd174ca3ec25c06ff5fddae365643f73d77777":
        mt["machine_wallets"] = 20
        mt["label"] = "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - rotation STALLED at 20 wallets (run 90)"
        mt["note"] = mt.get("note", "") + (
            " RUN-90 UPDATE: 0 wallets this run - rotation STALLED at 20 wallets, did NOT reach 27 as expected at the end of run 89; "
            "1st quiet run after debut (runs 88-89 active). No buys and no sells from tracked wallets for this token in the run-90 window. "
            "Not treated as an anomaly under the fast-path amendment (no size deviation, name/symbol, website, or free-mint path appeared); "
            "watch run 91 for any resumption."
        )
        print("79cd entry updated: stalled at 20, 0 wallets run 90")
        break

sig = s.setdefault("signaled_projects_over_20pct", [])
sig.append("Unnamed token (name/symbol empty) 0x6a2590934e55671a6fab9fa8edca8da4960e7777 (paid-only, machine-token, run-90, no chat report per fast-path amendment)")
sig.append("Unnamed token (name/symbol empty) 0x9f7ea7a4eaa7f39782caeb1ecab8176187e97777 (paid-only, machine-token, run-90, no chat report per fast-path amendment)")
sig.append("Unnamed token (name/symbol empty) 0x8c64aa82e861393bf760ee6d0eb29c0c60f07777 (paid-only, machine-token, run-90, no chat report per fast-path amendment)")
sig.append("Unnamed token (name/symbol empty) 0xc1ab1e832da23f85a27aa2778f555d00319e7777 (paid-only, machine-token, run-90, no chat report per fast-path amendment)")
sig.append("Unnamed token (name/symbol empty) 0x1153607e323c42f93c82b80e1772f9cc626b7777 (paid-only, machine-token, run-90, 26 wallets, rotation possibly still filling, no chat report per fast-path amendment)")

s["paid_trend_run90"] = {
    "note": "Aggregate only, NOT a buy recommendation. FIVE new machine-token rotations (4 at 27 wallets, 1 at 26 wallets, same machine set) are paid-only with no free-mint path (auto-mint blocked at guard (c)); recorded in state, NO chat report per fast-path amendment. 0x79cd... STALLED at 20 wallets (0 wallets this run). SILENT RUN - no chat report (no new mints, no Free Bacot signal, no auto-mint trigger, no reportable paid trend beyond the routine rotations).",
    "rotations": (
        "FIVE NEW machine-token rotations, same 27-wallet machine set as runs 80-82/85-89, IDENTICAL set for the four 27-wallet tokens (overlap 27/27 pairwise): "
        "0x6a2590934e55671a6fab9fa8edca8da4960e7777 at 27 wallets (49.1% of 55): 58 sent buys (min 0.000121, median 0.2234, max 0.3787 BNB, total 9.8844 BNB) + "
        "97 sells, first tracked Transfer 05:49:31 WIB (block 132091517) via 0xcb08c02c0a, pair 0xa528208d... (token0=token, token1=WBNB; reserves ~61.46M token / 0.0568 BNB). "
        "0x9f7ea7a4eaa7f39782caeb1ecab8176187e97777 at 27 wallets (49.1%): 58 sent buys (min 0.000121, median 0.2241, max 0.4302 BNB, total 9.8832 BNB) + "
        "100 sells, first tracked Transfer 05:31:45 WIB (block 132089149) via 0xcb08c02c0a, pair 0x430e7ac9... (token0=token, token1=WBNB; reserves ~52.08M token / 0.0663 BNB). "
        "0x8c64aa82e861393bf760ee6d0eb29c0c60f07777 at 27 wallets (49.1%): 58 sent buys (min 0.000121, median 0.2242, max 0.4031 BNB, total 10.0000 BNB) + "
        "100 sells, first tracked Transfer 04:54:48 WIB (block 132084222) via 0xcb08c02c0a, pair 0xa29fee30... (token0=token, token1=WBNB; reserves ~74.49M token / 0.0466 BNB). "
        "0xc1ab1e832da23f85a27aa2778f555d00319e7777 at 27 wallets (49.1%): 53 sent buys (min 0.000121, median 0.2234, max 0.3756 BNB, total 9.2924 BNB) + "
        "98 sells, first tracked Transfer 04:37:07 WIB (block 132081866) via 0xcb08c02c0a, pair 0xaac71a1e... (token0=WBNB, token1=token; reserves 0.0659 BNB / ~51.79M token). "
        "FIFTH token 0x1153607e323c42f93c82b80e1772f9cc626b7777 at 26 wallets (47.3%): 53 sent buys (min 0.000121, median 0.2301, max 0.3717 BNB, total 9.5966 BNB) + "
        "98 sells, first tracked Transfer 05:14:12 WIB (block 132086809) via 0xcb08c02c0a, pair 0x2c1577fe... (token0=token, token1=WBNB; reserves ~60.62M token / 0.0556 BNB) - "
        "subset of the same set (missing wallet 0x2cc8192fc6); rotation possibly still filling at window end. All sizes within class norm; no name/symbol, "
        "no website pointer, no free-mint path; guard (c) blocks auto-mint."
    ),
    "other_paid_activity": [
        {"pattern": "45 other paid tokens: 25 at 3 wallets (usual ...7777 set), 10 at 2, 10 at 1", "wallets": "see run90-paid.json"},
        {"pattern": "Micro round-trip churn continues: 360 PCS buys (0xb6f9de95) + 569 PCS sells (0x791ac947), 594 approvals (0x095ea7b3), 43 aggregator txs (0x39ecce49); top active 0xa952... 93 txs, 0x9cdd... 90, 0xc621... 88, 0xad94... 76, 0xf795... 69, 0x3803... 68", "wallets": "churn set"},
        {"pattern": "107 contract deployments by tracked wallets this run (all status 1, addresses in run90-deployments.json) - FIFTH deployment run in a row (16 run 87, 36 run 86, 56 run 88, 57 run 89, 107 run 90); identities unverified, added to run-90 inbound list (0 hits)", "wallets": "0x97bd... x26, 0x1cce... x10, 0xf795... x9, 0x9b51... x9"},
        {"pattern": "3 failed txs, ALL failed PCS sells (0 logs, value 0) - see last_run method_note for the per-wallet breakdown", "wallets": "0xc621... x1, 0xb940... x1, 0xa952... x1"},
    ],
    "quiet": "AFeng 0 txs; future1001.ai 0 txs; 0x2325... 0 txs; 0x8e96... 0 txs; 0x3803... 68 txs (43 aggregator + 25 approvals, churn as usual); GrokBot 0xfcd0... absent (0 wallets) - 31st consecutive quiet run (59, 61-90) after the run-60 burst; CORLA-97af 0 wallets; CORLA 0x4a9c 0 wallets; all run-64/65 ASI contracts 0 wallets; run-89 tokens 0xcfdb.../0x0cf8.../0xe68b.../0x31e4... 0 wallets (1st quiet run after debut, down from 27/27/27/27); run-88 tokens 0x43c8.../0x3d12.../0xeae0... 0 wallets (2nd quiet run after debut); run-87 tokens 0x889a.../0x4249... 0 wallets (3rd quiet run after debut); run-86 tokens 0x2bfb.../0xc459... 0 wallets (4th quiet run after debut); run-85 token 0x2717... 0 wallets (5th quiet run); run-82 tokens 0xd468.../0xa6e6.../0x887c... 0 wallets (8th quiet run after debut); run-81 tokens 0 wallets (9th quiet run); run-80 token 0 wallets (10th quiet run); 0x79cd... 0 wallets (rotation STALLED at 20, 1st quiet run after debut); all other run-66/68/69/70/71/72/73/74/75/76/77/78/79 machine tokens 0 wallets.",
}

s["inbound_log_leg_run90"] = {
    "contracts": 1347,
    "attempted": 1347,
    "completed_with_0_hits": 1347,
    "total_logs": 11373,
    "hits": 0,
    "failed": 0,
    "failed_contracts": [],
    "never_attempted": 0,
    "complete": True,
    "note": (
        "Ankr getLogs address-filtered per contract, window 132080960-132093926, from list run90-inbound-contracts.json (1347 contracts = "
        "run89 list 1240 + 107 run-90 deployment addresses). Full pass a (400, 6,730 logs) + b1 (200, 2,802) + b2 (200, 796) + b3 (547, 1,045) = "
        "11,373 logs, 0 hits, 0 failed. 6 truncated contracts, all topic-filtered to 0 logs (0x1de4... AFeng sale, 0x55d398... USDT, "
        "0x6288..., 0x636fdfa9... tracker, 0x63de... AGC, 0x7857...). RUN-90 WINDOW INBOUND FULLY CLOSED. Chunk b2 first attempt died silently at "
        "100/200 (service-restart pattern) and was re-run in full; re-run completed with 0 failed. NOTE: inbound chunk output files are correctly "
        "named run90-inbound90-*.json."
    ),
}

s["next_run_note"] = (
    "Next run sent-tx window starts from block 132093927. RETRY run 91: (1) Pair token0/token1 reads for 0xa6e6... pair "
    "0x9fac925655fa4985ab4fe2fe9e0ca8ae323cc9da and 0x887c... pair 0xa9fa6efb21c252b7d4ab81d19a07ee4ecf6d2c97 "
    "(fast_rpc race returns None / 'all endpoints failed', 8 consecutive runs - persistently unreadable, unverified not absence), "
    "plus 0x2bfb pair 0x782671f637bf1a01de482824c4b2520bc58a5a4b, 0xc459 pair 0xeca06856c88fcdf1506886431a079d3f2565ca82, and rotation "
    "0x43c8 pair 0xaafebb5244e2e546f7cd18a2c89f85bbee03f1e0 (unreadable run 88, 89 AND 90 - retry opportunistically, not an anomaly), "
    "PLUS run-89 rotation pairs 0xcfdb 0x1e04925db4eabab2917ef73a8cdf232bcc69b5ba, 0x0cf8 0xf6800c4a1ecdffbd64f9047c606bdb32dee0127f, "
    "0xe68b 0xfab7cb4979c9e4738afc61e4974177cf72c50896 (token0/token1 unreadable run 89 AND run 90; 0x31e4 pair 0x60ca0aef... READ OK run 89), "
    "PLUS new run-90 rotation pairs 0x6a25 0xa528208db86d680109abc6efff448dc896221ce4, 0x9f7e 0x430e7ac91f57f618dff0114d1b981a20b90f0985, "
    "0x8c64 0xa29fee30f7176ab4c40a258f1fa179eac871ab98, 0xc1ab 0xaac71a1eec286602f020ba6ea7047583d973857c, 0x1153 0x2c1577fea68003ffd6b6e94e8472e0dd1155786b "
    "(all five pairs' token0/token1 READ OK in run-90 token-verify via fast_rpc race - do NOT re-read unless a new question arises; the retry list "
    "above is for the pairs that are still unreadable). "
    "NOTE: fast_rpc worked for the receipts batch + several token-verify reads in run 90 - the outage is time-varying / per-call; a retry at a "
    "different time may succeed. "
    "c459 name()/symbol() CONFIRMED empty strings run 87 (not transient) - consistent with machine-token pattern. "
    "e68b totalSupply/owner + 31e4 name/owner unreadable run 89 ONLY (transient outage) - retry opportunistically; do NOT treat as pattern break. "
    "9f7e name/symbol/owner + 6a25 symbol + 8c64 totalSupply + c1ab symbol unreadable run 90 ONLY (transient outage) - same treatment. "
    "(2) Run-90 inbound list for run 91 = run90 list (1347) unless run 91's own sent pass finds new deployments to add. "
    "(3) Run-90 window inbound FULLY CLOSED (1347/1347, 11,373 logs, 0 hits). "
    "(4) 0x1153607e... rotation was at 26 wallets at run-90 window end (missing wallet 0x2cc8192fc6) - expect it at 27 wallets in run 91; do NOT "
    "treat that growth as a new rotation. 0x79cd... STALLED at 20 wallets (0 wallets run 90) - watch run 91 for any resumption; do NOT treat a "
    "return as a new rotation either. "
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
    "0x31e43b72f14fea00a576e84c4e3605d98a317777 at 27 wallets each + 0x79cd174ca3ec25c06ff5fddae365643f73d77777 at 20 wallets, rotation still in progress), "
    "run 90 (FIVE tokens 0x6a2590934e55671a6fab9fa8edca8da4960e7777 + 0x9f7ea7a4eaa7f39782caeb1ecab8176187e97777 + 0x8c64aa82e861393bf760ee6d0eb29c0c60f07777 + "
    "0xc1ab1e832da23f85a27aa2778f555d00319e7777 at 27 wallets each + 0x1153607e323c42f93c82b80e1772f9cc626b7777 at 26 wallets, rotation possibly still filling "
    "+ 0x79cd174ca3ec25c06ff5fddae365643f73d77777 STALLED at 20 wallets, 0 wallets run 90) "
    "auto-mint BLOCKED at guard (c) - do not re-signal or re-report the block unless a new mint/buy fact appears for those contracts "
    "(e.g. a genuine free-mint path). Per the 2026-11-06 ~18:30 machine-token fast-path amendment, routine machine-token rotations are "
    "recorded in state WITHOUT a chat report (no full verification per run); report only on anomaly (buy size far off norm, name/symbol appears, "
    "website, or free-mint path). Paid fact: run90 FIVE NEW rotations (4 at 27 wallets identical set + 1 at 26 wallets subset, still filling) "
    "all routine class-norm sizes, no anomaly - state-only, no chat report; run-89 tokens 0xcfdb.../0x0cf8.../0xe68b.../0x31e4... 0 wallets (1st quiet run after debut); run-88 tokens 0x43c8.../0x3d12.../0xeae0... 0 wallets (2nd quiet run after debut); run-87 tokens 0x889a.../0x4249... 0 wallets (3rd quiet run after debut); run-86 tokens "
    "0x2bfb.../0xc459... 0 wallets (4th quiet run after debut); run-85 token 0x2717... 0 wallets (5th quiet run); run-82 tokens 0xd468.../0xa6e6.../0x887c... "
    "all 0 wallets (8th quiet run after debut); run-81 tokens 0 wallets (9th quiet run); run-80 token 0 wallets (10th quiet run); "
    "GrokBot 0xfcd0... absent (0 wallets) - 31st consecutive quiet run (59, 61-90) after the run-60 burst; CORLA-97af 0 wallets; "
    "CORLA 0x4a9c 0 wallets; all run-64/65 ASI contracts 0 wallets; all run-66/68/69/70/71/72/73/74/75/76/77/78/79 machine tokens 0 wallets. "
    "Run 90 had 107 deployments (fifth deployment run in a row after 16 in run 87, 36 in run 86, 56 in run 88, 57 in run 89), top deployer 0x97bd... x26; "
    "all 107 addresses added to the run-90 inbound list (0 hits). "
    "AFeng 0 txs; future1001.ai 0 txs; 0x2325... 0 txs; 0x8e96... 0 txs; 0x3803... 68 txs (43 aggregator + 25 approvals). "
    "SCRIPT LESSON (run 85, FIXED run 86): when copying runNN-receipts.py for the next run, sed-replace the two hardcoded json.dump output paths too "
    "(runNN-receipts.json / runNN-paid.json) - run 90's copy was verified correct before running (dumps to run90-receipts.json/run90-paid.json). "
    "PROCESS LESSON (run 86): the receipts pass died silently at 420/461 (service-restart pattern, same as runs 82/84) - the partial-file resume worked; "
    "always re-run the same script to resume rather than re-fetching from scratch. Run 90 receipts completed in one attempt, no resume needed; "
    "BUT inbound chunk b2 died silently at 100/200 in run 90 (service restart interrupted the operator session too) and had to be re-run in full "
    "(inbound script saves no partial) - same restart pattern. "
    "INBOUND FILENAME QUIRK FIXED run 88: chunk output files are now correctly named run90-inbound90-{a,b1,b2,b3}.json. "
    "Same-owner factory groups now also include 0x293f and 0x1103 (proven 2026-11-06 ~01:14 WIB, AGENTS.md) alongside the groups listed in the body."
)

json.dump(s, open(P, "w"), indent=1)
print("state updated; last_run now:", s["last_run"]["run"], "block_end:", s["last_run"]["block_end"])
print("machine_tokens:", len(s.get("machine_tokens", [])), "| signaled:", len(s.get("signaled_projects_over_20pct", [])))
print("inbound90 complete:", s["inbound_log_leg_run90"]["complete"])
