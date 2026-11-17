#!/usr/bin/env python3
"""Run 91 state update (read-only job bookkeeping; no chain writes).

Completes run 91 (window 132093927-132109988, tx 2026-11-07 06:08:32 - 08:08:05 WIB).
Sent/receipts/paid done and verified; inbound leg run-91 window 1346/1347 closed
(1 contract failed transiently, retry run 92). NO new mints. NO new machine-token
rotations: all five run-90 rotations 0 wallets (1st quiet run after debut); 0x1153...
did NOT reach 27 - stalled at 26; 0x79cd... 0 wallets (2nd quiet run, stalled at 20).
0 deployments this run - deployment streak (5 runs) broken. Bridge unchanged
(0 new mints, 0 not_evaluated).
"""
import json, shutil

P = "/home/hatch/workspace/narrative-pulse/tracked-wallet-mint-scan-state.json"
shutil.copy(P, str(P) + ".bak-run91-pre")
s = json.load(open(P))

last_run_91 = {
    "run": 91,
    "block_start": 132093927,
    "block_end": 132109988,
    "window_wib": "2026-11-07 06:08:32 - 08:08:05 WIB (tx times); run executed ~08:06 - ~10:05 WIB; sent-pass in-window txs 357, 0 mint-pattern txs",
    "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set); 0 failed, no retry needed.",
    "method_note": (
        "Sent pass Ankr ankr_getTransactionsByAddress via module: 55/55 OK first attempt, 357 txs, 7 wallets active. "
        "Receipts via fast_rpc batch (6, ~4s pause) for 238 non-approve candidates: 238 status 1, 0 status 0, 0 null, 0 mint logs. "
        "Receipts completed in one attempt, no resume needed. "
        "Paid: 53 tokens; max 3 wallets/token (29 at 3, 13 at 2, 11 at 1 - usual ...7777 churn, no new rotation). "
        "ALL run-90 machine-token rotations 0 wallets this run - 1st quiet run after debut for 0x6a2590934e55671a6fab9fa8edca8da4960e7777, "
        "0x9f7ea7a4eaa7f39782caeb1ecab8176187e97777, 0x8c64aa82e861393bf760ee6d0eb29c0c60f07777, "
        "0xc1ab1e832da23f85a27aa2778f555d00319e7777 (27 wallets each in run 90). "
        "0x1153607e323c42f93c82b80e1772f9cc626b7777: 0 wallets this run - did NOT reach 27 as expected at the end of run 90; rotation STALLED at 26 "
        "wallets (missing wallet 0x2cc8192fc6 never bought in); 1st quiet run after debut. "
        "0x79cd174ca3ec25c06ff5fddae365643f73d77777: 0 wallets this run - rotation STALLED at 20 wallets; 2nd quiet run after debut (runs 88-89 active). "
        "No anomaly under the fast-path amendment (no size deviation, name/symbol, website, or free-mint path appeared for any of them) - "
        "state-only, NO chat report. "
        "AFeng 0 txs; future1001.ai 0 txs; 0x8e96... 0 txs; 0x2325... 1 tx (aggregator 0x296b..., selector 0x27772d13, 0.1 BNB, 08:05:51 WIB, "
        "receipt checked, 0 mint logs - not a mint); 0x3803... 84 txs (55 aggregator 0x39ecce49 + 29 approvals, total value 0.000754 BNB, churn as usual). "
        "Selectors (sent pass, 357 txs): 94 PCS buys (0xb6f9de95) + 87 PCS sells (0x791ac947) + 119 approvals (0x095ea7b3) + 55 aggregator (0x39ecce49) + "
        "1 aggregator (0x27772d13) + 1 plain transfer (0x). Nonzero-value txs 125, total 0.108253 BNB, max 0.1 BNB (the 0x2325 aggregator tx). "
        "Deployments: 0 contract creations by tracked wallets this run - the deployment streak is BROKEN (16 run 87, 36 run 86, 56 run 88, 57 run 89, "
        "107 run 90, 0 run 91). Run-91 inbound list = run90 list (1347), unchanged. "
        "Inbound leg run-91 WINDOW: 1346/1347 contracts completed, 15,449 logs, 0 hits, 1 FAILED: 0x096a4ad7408bd95ca5bc87d2c1e957093092e29f "
        "('Remote end closed connection without response', chunk a, contract 36) - transient, NOT verified as 0 hits for that contract; retry run 92. "
        "8 truncated contracts, all topic-filtered to 0 logs (0x10b3..., 0x1de4... AFeng sale, 0x3dca..., 0x55d398... USDT, 0x6288..., "
        "0x636fdfa9... tracker, 0x63de... AGC, 0x7857...). Chunks a (400, 9,929 logs) + b1 (200, 3,201) + b2 (200, 1,257) + b3 (547, 1,062) = 15,449 logs. "
        "All four chunks completed first attempt (chunk a + b1 + b2 + b3 each had slow ~2-6 min stretches at contracts 150-200, then resumed on their own; "
        "b2 paused ~4 min at 100/200 and ~2 min at 150/200 but did NOT die - unlike run 90). "
        "Pair token0/token1 STILL UNREADABLE for ALL EIGHT pairs in run-91 pair retry (fast_rpc race 'all endpoints failed', OSError on every endpoint, "
        "9th consecutive run for a6e6/887c/2bfb/c459, 4th for 43c8, 2nd for the three run-89 rotation pairs cfdb/0cf8/e68b) - unverified, not absence; "
        "retry run 92. NOTE: fast_rpc batch worked fine for the receipts pass in the same run - the outage is time-varying / per-call, not a permanent "
        "endpoint failure. "
        "Pointer-discovery (amendment 19:10): 0 contracts processed - no new mints this run, and the backfill queue is empty (bridge 115 "
        "contracts, 0 not_evaluated); bridge unchanged. "
        "SILENT RUN - no chat report (no new mints, no Free Bacot signal, no auto-mint trigger, no reportable paid trend). "
        "No preview/mint/sign/login/purchase by this job."
    ),
}
cur_run = s.get("last_run", {}).get("run", 0)
if cur_run < 91:
    s["last_run"] = last_run_91
    print(f"last_run set to 91 (was {cur_run})")
else:
    print(f"last_run already {cur_run} (>=91) - NOT regressing")
    s["run91_last_run_record"] = last_run_91

# Update the run-90 0x1153 entry in place (0 wallets run 91 - did NOT reach 27, stalled at 26).
for mt in s.get("machine_tokens", []):
    if mt.get("address", "").lower() == "0x1153607e323c42f93c82b80e1772f9cc626b7777":
        mt["machine_wallets"] = 26
        mt["label"] = "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - rotation STALLED at 26 wallets (run 91)"
        mt["note"] = mt.get("note", "") + (
            " RUN-91 UPDATE: 0 wallets this run - rotation did NOT reach 27 as expected at the end of run 90; the missing wallet "
            "0x2cc8192fc6 never bought in, so the rotation STALLED at 26 wallets; 1st quiet run after debut. No buys and no sells from "
            "tracked wallets for this token in the run-91 window. Not treated as an anomaly under the fast-path amendment (no size deviation, "
            "name/symbol, website, or free-mint path appeared); watch run 92 for any resumption, do NOT treat a return as a new rotation."
        )
        print("1153 entry updated: stalled at 26, 0 wallets run 91")
        break
# Update the run-88/89 0x79cd entry in place (0 wallets run 91 - 2nd quiet run, stalled at 20).
for mt in s.get("machine_tokens", []):
    if mt.get("address", "").lower() == "0x79cd174ca3ec25c06ff5fddae365643f73d77777":
        mt["machine_wallets"] = 20
        mt["label"] = "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - rotation STALLED at 20 wallets (runs 90-91)"
        mt["note"] = mt.get("note", "") + (
            " RUN-91 UPDATE: 0 wallets this run - rotation STALLED at 20 wallets; 2nd quiet run after debut (runs 88-89 active). No buys and "
            "no sells from tracked wallets for this token in the run-91 window. Not treated as an anomaly under the fast-path amendment; "
            "watch run 92 for any resumption, do NOT treat a return as a new rotation."
        )
        print("79cd entry updated: stalled at 20, 0 wallets run 91 (2nd quiet run)")
        break

s["paid_trend_run91"] = {
    "note": "Aggregate only, NOT a buy recommendation. NO new machine-token rotations this run; all five run-90 rotations 0 wallets (1st quiet run after debut); 0x1153... STALLED at 26 wallets (did NOT reach 27); 0x79cd... STALLED at 20 wallets (2nd quiet run). 0 deployments - deployment streak broken. SILENT RUN - no chat report (no new mints, no Free Bacot signal, no auto-mint trigger, no reportable paid trend beyond routine churn).",
    "rotations": "NONE NEW. Run-90 rotations all 0 wallets (1st quiet run after debut): 0x6a2590934e55671a6fab9fa8edca8da4960e7777, 0x9f7ea7a4eaa7f39782caeb1ecab8176187e97777, 0x8c64aa82e861393bf760ee6d0eb29c0c60f07777, 0xc1ab1e832da23f85a27aa2778f555d00319e7777 (27 wallets each in run 90) + 0x1153607e323c42f93c82b80e1772f9cc626b7777 (26 wallets in run 90, did NOT reach 27 - STALLED at 26). All paid-only with no free-mint path; auto-mint blocked at guard (c); recorded in state, NO chat report per fast-path amendment.",
    "other_paid_activity": [
        {"pattern": "53 paid tokens: 29 at 3 wallets, 13 at 2, 11 at 1 (usual ...7777 churn)", "wallets": "see run91-paid.json"},
        {"pattern": "Micro round-trip churn continues: 94 PCS buys (0xb6f9de95) + 87 PCS sells (0x791ac947), 119 approvals (0x095ea7b3), 55 aggregator txs (0x39ecce49); top active 0xad94... 85 txs, 0x3803... 84, 0xc7c5... 82, 0xa0c1... 39, 0x3628... 37, 0x7488... 29", "wallets": "churn set"},
        {"pattern": "0 contract deployments by tracked wallets this run - deployment streak BROKEN (16 run 87, 36 run 86, 56 run 88, 57 run 89, 107 run 90, 0 run 91)", "wallets": "none"},
        {"pattern": "1 aggregator tx by 0x2325... (0x296b..., selector 0x27772d13, 0.1 BNB, 08:05:51 WIB) - receipt checked, 0 mint logs, not a mint", "wallets": "0x2325... x1"},
        {"pattern": "0 failed txs this run (all 238 receipt candidates status 1)", "wallets": "none"},
    ],
    "quiet": "AFeng 0 txs; future1001.ai 0 txs; 0x8e96... 0 txs; 0x2325... 1 tx (aggregator, not a mint); 0x3803... 84 txs (55 aggregator + 29 approvals, churn as usual); GrokBot 0xfcd0... absent (0 wallets) - 32nd consecutive quiet run (59, 61-91) after the run-60 burst; CORLA-97af 0 wallets; CORLA 0x4a9c 0 wallets; all run-64/65 ASI contracts 0 wallets; run-90 tokens 0x6a25.../0x9f7e.../0x8c64.../0xc1ab.../0x1153... 0 wallets (1st quiet run after debut, down from 27/27/27/27/26); run-89 tokens 0xcfdb.../0x0cf8.../0xe68b.../0x31e4... 0 wallets (2nd quiet run after debut); run-88 tokens 0x43c8.../0x3d12.../0xeae0... 0 wallets (3rd quiet run after debut); run-87 tokens 0x889a.../0x4249... 0 wallets (4th quiet run after debut); run-86 tokens 0x2bfb.../0xc459... 0 wallets (5th quiet run after debut); run-85 token 0x2717... 0 wallets (6th quiet run); run-82 tokens 0xd468.../0xa6e6.../0x887c... 0 wallets (9th quiet run after debut); run-81 tokens 0 wallets (10th quiet run); run-80 token 0 wallets (11th quiet run); 0x79cd... 0 wallets (rotation STALLED at 20, 2nd quiet run after debut); all other run-66/68/69/70/71/72/73/74/75/76/77/78/79 machine tokens 0 wallets.",
}

s["inbound_log_leg_run91"] = {
    "contracts": 1347,
    "attempted": 1347,
    "completed_with_0_hits": 1346,
    "total_logs": 15449,
    "hits": 0,
    "failed": 1,
    "failed_contracts": ["0x096a4ad7408bd95ca5bc87d2c1e957093092e29f"],
    "never_attempted": 0,
    "complete": False,
    "note": (
        "Ankr getLogs address-filtered per contract, window 132093927-132109988, from list run91-inbound-contracts.json (1347 contracts = "
        "run90 list, unchanged - 0 deployments in run 91). Full pass a (400, 9,929 logs) + b1 (200, 3,201) + b2 (200, 1,257) + b3 (547, 1,062) = "
        "15,449 logs, 0 hits, 1 FAILED: 0x096a4ad7408bd95ca5bc87d2c1e957093092e29f ('Remote end closed connection without response', chunk a, "
        "contract 36) - transient, retry run 92; that contract is NOT verified as 0 hits for the run-91 window. 8 truncated contracts, all "
        "topic-filtered to 0 logs (0x10b3..., 0x1de4... AFeng sale, 0x3dca..., 0x55d398... USDT, 0x6288..., 0x636fdfa9... tracker, 0x63de... AGC, "
        "0x7857...). RUN-91 WINDOW INBOUND NOT FULLY CLOSED (1346/1347) - the 1 failed contract is the only open item. All four chunks completed "
        "first attempt (no silent deaths this run; slow stretches at contracts 150-200 in each chunk resumed on their own). NOTE: inbound chunk "
        "output files are correctly named run91-inbound91-{a,b1,b2,b3}.json."
    ),
}

s["next_run_note"] = (
    "Next run sent-tx window starts from block 132109989. RETRY run 92: (1) Pair token0/token1 reads for 0xa6e6... pair "
    "0x9fac925655fa4985ab4fe2fe9e0ca8ae323cc9da and 0x887c... pair 0xa9fa6efb21c252b7d4ab81d19a07ee4ecf6d2c97 "
    "(fast_rpc race returns None / 'all endpoints failed', 9 consecutive runs - persistently unreadable, unverified not absence), "
    "plus 0x2bfb pair 0x782671f637bf1a01de482824c4b2520bc58a5a4b, 0xc459 pair 0xeca06856c88fcdf1506886431a079d3f2565ca82, and rotation "
    "0x43c8 pair 0xaafebb5244e2e546f7cd18a2c89f85bbee03f1e0 (unreadable run 88, 89, 90 AND 91 - retry opportunistically, not an anomaly), "
    "PLUS run-89 rotation pairs 0xcfdb 0x1e04925db4eabab2917ef73a8cdf232bcc69b5ba, 0x0cf8 0xf6800c4a1ecdffbd64f9047c606bdb32dee0127f, "
    "0xe68b 0xfab7cb4979c9e4738afc61e4974177cf72c50896 (token0/token1 unreadable run 89, 90 AND 91; 0x31e4 pair 0x60ca0aef... READ OK run 89), "
    "PLUS new run-90 rotation pairs 0x6a25 0xa528208db86d680109abc6efff448dc896221ce4, 0x9f7e 0x430e7ac91f57f618dff0114d1b981a20b90f0985, "
    "0x8c64 0xa29fee30f7176ab4c40a258f1fa179eac871ab98, 0xc1ab 0xaac71a1eec286602f020ba6ea7047583d973857c, 0x1153 0x2c1577fea68003ffd6b6e94e8472e0dd1155786b "
    "(all five pairs' token0/token1 READ OK in run-90 token-verify via fast_rpc race - do NOT re-read unless a new question arises; the retry list "
    "above is for the pairs that are still unreadable). "
    "NOTE: fast_rpc worked for the receipts batch in run 91 - the outage is time-varying / per-call; a retry at a different time may succeed. "
    "c459 name()/symbol() CONFIRMED empty strings run 87 (not transient) - consistent with machine-token pattern. "
    "e68b totalSupply/owner + 31e4 name/owner unreadable run 89 ONLY (transient outage) - retry opportunistically; do NOT treat as pattern break. "
    "9f7e name/symbol/owner + 6a25 symbol + 8c64 totalSupply + c1ab symbol unreadable run 90 ONLY (transient outage) - same treatment. "
    "(2) RETRY run 92 inbound: contract 0x096a4ad7408bd95ca5bc87d2c1e957093092e29f failed in run 91 chunk a ('Remote end closed connection without "
    "response') - re-check it for the run-91 window 132093927-132109988 (topic-filtered, Transfer from zero address to tracked wallets) before "
    "treating the run-91 window as closed. "
    "(3) Run-91 inbound list for run 92 = run90 list (1347) unless run 92's own sent pass finds new deployments to add. "
    "(4) Run-91 window inbound NOT FULLY CLOSED (1346/1347, 15,449 logs, 0 hits, 1 failed - see (2)). "
    "(5) 0x1153607e... rotation STALLED at 26 wallets (did NOT reach 27 as expected; 0 wallets run 91, 1st quiet run after debut) - watch run 92 "
    "for any resumption; do NOT treat a return as a new rotation. 0x79cd... STALLED at 20 wallets (0 wallets runs 90-91, 2nd quiet run) - same. "
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
    "run 91 (ZERO new rotations; all five run-90 tokens 0 wallets, 1st quiet run after debut; 0x1153... STALLED at 26, did NOT reach 27; "
    "0x79cd... STALLED at 20, 2nd quiet run) "
    "auto-mint BLOCKED at guard (c) - do not re-signal or re-report the block unless a new mint/buy fact appears for those contracts "
    "(e.g. a genuine free-mint path). Per the 2026-11-06 ~18:30 machine-token fast-path amendment, routine machine-token rotations are "
    "recorded in state WITHOUT a chat report (no full verification per run); report only on anomaly (buy size far off norm, name/symbol appears, "
    "website, or free-mint path). Paid fact: run91 ZERO new rotations; run-90 tokens 0x6a25.../0x9f7e.../0x8c64.../0xc1ab.../0x1153... 0 wallets (1st quiet run after debut); run-89 tokens 0xcfdb.../0x0cf8.../0xe68b.../0x31e4... 0 wallets (2nd quiet run after debut); run-88 tokens 0x43c8.../0x3d12.../0xeae0... 0 wallets (3rd quiet run after debut); run-87 tokens 0x889a.../0x4249... 0 wallets (4th quiet run after debut); run-86 tokens "
    "0x2bfb.../0xc459... 0 wallets (5th quiet run after debut); run-85 token 0x2717... 0 wallets (6th quiet run); run-82 tokens 0xd468.../0xa6e6.../0x887c... "
    "all 0 wallets (9th quiet run after debut); run-81 tokens 0 wallets (10th quiet run); run-80 token 0 wallets (11th quiet run); "
    "GrokBot 0xfcd0... absent (0 wallets) - 32nd consecutive quiet run (59, 61-91) after the run-60 burst; CORLA-97af 0 wallets; "
    "CORLA 0x4a9c 0 wallets; all run-64/65 ASI contracts 0 wallets; all run-66/68/69/70/71/72/73/74/75/76/77/78/79 machine tokens 0 wallets. "
    "Run 91 had 0 deployments (deployment streak BROKEN after 16 run 87, 36 run 86, 56 run 88, 57 run 89, 107 run 90). "
    "AFeng 0 txs; future1001.ai 0 txs; 0x2325... 1 tx (aggregator 0.1 BNB, not a mint); 0x8e96... 0 txs; 0x3803... 84 txs (55 aggregator + 29 approvals). "
    "SCRIPT LESSON (run 85, FIXED run 86): when copying runNN-receipts.py for the next run, sed-replace the two hardcoded json.dump output paths too "
    "(runNN-receipts.json / runNN-paid.json) - run 91's copy was verified correct before running (dumps to run91-receipts.json/run91-paid.json). "
    "PROCESS LESSON (run 86): the receipts pass died silently at 420/461 (service-restart pattern, same as runs 82/84) - the partial-file resume worked; "
    "always re-run the same script to resume rather than re-fetching from scratch. Run 91 receipts completed in one attempt, no resume needed; "
    "inbound chunks a/b1/b2/b3 all completed first attempt in run 91 (no silent deaths; slow stretches at contracts 150-200 resumed on their own). "
    "INBOUND FILENAME QUIRK FIXED run 88: chunk output files are now correctly named run91-inbound91-{a,b1,b2,b3}.json. "
    "Same-owner factory groups now also include 0x293f and 0x1103 (proven 2026-11-06 ~01:14 WIB, AGENTS.md) alongside the groups listed in the body."
)

json.dump(s, open(P, "w"), indent=1)
print("state updated; last_run now:", s["last_run"]["run"], "block_end:", s["last_run"]["block_end"])
print("machine_tokens:", len(s.get("machine_tokens", [])), "| signaled:", len(s.get("signaled_projects_over_20pct", [])))
print("inbound91 complete:", s["inbound_log_leg_run91"]["complete"], "| failed:", s["inbound_log_leg_run91"]["failed"])
