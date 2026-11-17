#!/usr/bin/env python3
"""Run 96 state update (read-only job bookkeeping; no chain writes).

Completes run 96 (window 132141791-132149916, tx 2026-11-07 12:10:05 - 13:07:38 WIB).
Sent/receipts/paid done and verified; inbound leg run-96 window FULLY CLOSED in-run
(1347/1347, 11,473 logs, 0 hits; 6 failed contracts retried same-run, 6/6 OK, 0 logs).
NO new mints. NO new machine-token rotations: all five run-90 rotations 0 wallets
(6th quiet run after debut); 0x1153... STALLED at 26 (6th quiet run);
0x79cd... STALLED at 20 (7th quiet run). 0 deployments this run (6th straight zero).
Bridge unchanged (0 new mints, 0 not_evaluated).
"""
import json, shutil

P = "/home/hatch/workspace/narrative-pulse/tracked-wallet-mint-scan-state.json"
shutil.copy(P, str(P) + ".bak-run96-pre")
s = json.load(open(P))

last_run_96 = {
    "run": 96,
    "block_start": 132141791,
    "block_end": 132149916,
    "window_wib": "2026-11-07 12:10:05 - 13:07:38 WIB (tx times); run executed ~13:05 - ~14:05 WIB; sent-pass in-window txs 204, 0 mint-pattern txs",
    "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set); 0 failed, no retry needed.",
    "method_note": (
        "Sent pass Ankr ankr_getTransactionsByAddress via module: 55/55 OK first attempt, 204 txs, 7 wallets active. "
        "Receipts via fast_rpc batch (6, ~4s pause) for 134 non-approve candidates: 134 status 1, 0 status 0, 0 null, 0 mint logs. "
        "Receipts completed in one attempt, no resume needed. "
        "Paid: 32 tokens; max 3 wallets/token (15 at 3, 6 at 2, 11 at 1 - usual ...7777 churn, no new rotation; 22 of 32 tokens end ...7777; "
        "0 overlap with run-95's 27 paid tokens - the ...7777 churn set turns over every run). "
        "ALL run-90 machine-token rotations 0 wallets this run - 6th quiet run after debut for 0x6a2590934e55671a6fab9fa8edca8da4960e7777, "
        "0x9f7ea7a4eaa7f39782caeb1ecab8176187e97777, 0x8c64aa82e861393bf760ee6d0eb29c0c60f07777, "
        "0xc1ab1e832da23f85a27aa2778f555d00319e7777 (27 wallets each in run 90). "
        "0x1153607e323c42f93c82b80e1772f9cc626b7777: 0 wallets this run - rotation STALLED at 26 wallets "
        "(missing wallet 0x2cc8192fc6 never bought in); 6th quiet run after debut. "
        "0x79cd174ca3ec25c06ff5fddae365643f73d77777: 0 wallets this run - rotation STALLED at 20 wallets; 7th quiet run after debut (runs 88-89 active). "
        "No anomaly under the fast-path amendment (no size deviation, name/symbol, website, or free-mint path appeared for any of them) - "
        "state-only, NO chat report. "
        "AFeng 17 txs (9 sale-calls 0x4d819a2a to 0x1de4... totaling 1.125 BNB - 0.5 + 0.25 + 0.25 + 0.125 - plus 8 approvals; all 9 sale-call "
        "receipts status 1, 7-25 logs each, 0 mint logs - SALES via the known AFeng sale contract, NOT mints); future1001.ai 0 txs; "
        "0x2325... 0 txs; 0x8e96... 0 txs; 0x3803... 44 txs (29 aggregator 0x39ecce49 + 15 approvals, total value 0.00039 BNB, churn as usual). "
        "Selectors (sent pass, 204 txs): 49 PCS buys (0xb6f9de95) + 47 PCS sells (0x791ac947) + 70 approvals (0x095ea7b3) + 29 aggregator (0x39ecce49) + "
        "9 sale-calls (0x4d819a2a, AFeng). Nonzero-value txs 68, total 1.128247 BNB, max 0.5 BNB (AFeng sale-call 0x84aefc473bfa at 12:23:14 WIB; "
        "the other 67 nonzero txs are PCS micro-buys ~0.00003-0.00009 BNB each). "
        "Most active wallets: 0xad94... 45 txs, 0x3803... 44, 0xc7c5... 43, 0x7488... 21, 0xa0c1... 18, 0xbf00... (AFeng) 17, 0x3628... 16. "
        "Deployments: 0 contract creations by tracked wallets this run - 6th straight zero (runs 91, 92, 93, 94, 95, 96). Run-96 inbound list = run93 list (1347), unchanged. "
        "Inbound leg run-96 WINDOW: FULLY CLOSED in-run - 1347/1347 contracts, 11,473 logs, 0 hits. "
        "Chunks a (400, 7,568 logs, 0 failed) + b1 (200, 2,424 logs, 3 failed) + b2 (200, 573 logs, 3 failed) + b3 (547, 908 logs, 0 failed) = 11,473 logs. "
        "6 failed contracts (all transient Ankr 'Remote end closed connection without response' from the simultaneous blip at ~contract 146-148 in all "
        "four chunks) retried SAME-RUN (run96-inbound96-retry.py): 6/6 OK, 0 logs, 0 hits - window fully closed without deferring to run 97. "
        "7 truncated contracts, all topic-filtered to 0 logs (a: 0x1de4... AFeng sale, 0x3dca..., 0x55d398... USDT, 0x6288..., 0x636fdfa9... tracker; "
        "b1: 0x63de... AGC, 0x7857...) - same set as runs 91-95 (0x10b3... not truncated this run, <1000 logs). "
        "FIRST attempt of chunks a and b3 DIED SILENTLY at ~contract 200-205 (a log frozen 06:29:27 UTC at [205], b3 log frozen 06:28:59 UTC at [200], "
        "no JSON, no EXIT - service-restart pattern, same as run 94); both re-run from scratch (a2/b3-2) and completed clean (a2: 400 contracts, "
        "7,568 logs, 0 failed; b3-2: 547 contracts, 908 logs, 0 failed). "
        "All four chunks stalled simultaneously at ~contract 50, ~150, ~250 and ~350 (log mtimes frozen several minutes, processes alive, 0 errors) "
        "and resumed on their own each time - shared Ankr slowdown, same pattern as runs 94-95. "
        "Pair token0/token1 STILL UNREADABLE for ALL EIGHT pairs in run-96 pair retry (fast_rpc race 'all endpoints failed', OSError on every endpoint, "
        "14th consecutive run for a6e6/887c/2bfb/c459, 9th for 43c8, 7th for the three run-89 rotation pairs cfdb/0cf8/e68b) - "
        "unverified, not absence; retry run 97. NOTE: fast_rpc batch worked fine for the receipts pass in the same run (134/134) - the outage "
        "is time-varying / per-call, not a permanent endpoint failure. "
        "Pointer-discovery (amendment 19:10): 0 contracts processed - no new mints this run, and the backfill queue is empty (bridge 115 "
        "contracts, 0 not_evaluated); bridge unchanged. "
        "SILENT RUN - no chat report (no new mints, no Free Bacot signal, no auto-mint trigger, no reportable paid trend). "
        "No preview/mint/sign/login/purchase by this job."
    ),
}
cur_run = s.get("last_run", {}).get("run", 0)
if cur_run < 96:
    s["last_run"] = last_run_96
    print(f"last_run set to 96 (was {cur_run})")
else:
    print(f"last_run already {cur_run} (>=96) - NOT regressing")
    s["run96_last_run_record"] = last_run_96

# Update the run-90 0x1153 entry in place (0 wallets run 96 - 6th quiet run, stalled at 26).
for mt in s.get("machine_tokens", []):
    if mt.get("address", "").lower() == "0x1153607e323c42f93c82b80e1772f9cc626b7777":
        mt["machine_wallets"] = 26
        mt["label"] = "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - rotation STALLED at 26 wallets (runs 91-96)"
        mt["note"] = mt.get("note", "") + (
            " RUN-96 UPDATE: 0 wallets this run - rotation STALLED at 26 wallets; 6th quiet run after debut. No buys and no sells from "
            "tracked wallets for this token in the run-96 window. Not treated as an anomaly under the fast-path amendment (no size deviation, "
            "name/symbol, website, or free-mint path appeared); watch run 97 for any resumption, do NOT treat a return as a new rotation."
        )
        print("1153 entry updated: stalled at 26, 0 wallets run 96 (6th quiet run)")
        break
# Update the run-88/89 0x79cd entry in place (0 wallets run 96 - 7th quiet run, stalled at 20).
for mt in s.get("machine_tokens", []):
    if mt.get("address", "").lower() == "0x79cd174ca3ec25c06ff5fddae365643f73d77777":
        mt["machine_wallets"] = 20
        mt["label"] = "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - rotation STALLED at 20 wallets (runs 90-96)"
        mt["note"] = mt.get("note", "") + (
            " RUN-96 UPDATE: 0 wallets this run - rotation STALLED at 20 wallets; 7th quiet run after debut (runs 88-89 active). No buys and "
            "no sells from tracked wallets for this token in the run-96 window. Not treated as an anomaly under the fast-path amendment; "
            "watch run 97 for any resumption, do NOT treat a return as a new rotation."
        )
        print("79cd entry updated: stalled at 20, 0 wallets run 96 (7th quiet run)")
        break

s["paid_trend_run96"] = {
    "note": "Aggregate only, NOT a buy recommendation. NO new machine-token rotations this run; all five run-90 rotations 0 wallets (6th quiet run after debut); 0x1153... STALLED at 26 wallets (6th quiet run); 0x79cd... STALLED at 20 wallets (7th quiet run). 0 deployments - 6th straight zero. Inbound run-96 window FULLY CLOSED in-run (1347/1347, 11,473 logs, 0 hits; 6 failed contracts retried same-run, 6/6 OK). SILENT RUN - no chat report (no new mints, no Free Bacot signal, no auto-mint trigger, no reportable paid trend beyond routine churn).",
    "rotations": "NONE NEW. Run-90 rotations all 0 wallets (6th quiet run after debut): 0x6a2590934e55671a6fab9fa8edca8da4960e7777, 0x9f7ea7a4eaa7f39782caeb1ecab8176187e97777, 0x8c64aa82e861393bf760ee6d0eb29c0c60f07777, 0xc1ab1e832da23f85a27aa2778f555d00319e7777 (27 wallets each in run 90) + 0x1153607e323c42f93c82b80e1772f9cc626b7777 (26 wallets in run 90, did NOT reach 27 - STALLED at 26). All paid-only with no free-mint path; auto-mint blocked at guard (c); recorded in state, NO chat report per fast-path amendment.",
    "other_paid_activity": [
        {"pattern": "32 paid tokens: 15 at 3 wallets, 6 at 2, 11 at 1 (usual ...7777 churn; 22 of 32 end ...7777; 0 overlap with run-95's 27 tokens)", "wallets": "see run96-paid.json"},
        {"pattern": "Micro round-trip churn continues: 49 PCS buys (0xb6f9de95) + 47 PCS sells (0x791ac947), 70 approvals (0x095ea7b3), 29 aggregator txs (0x39ecce49); top active 0xad94... 45 txs, 0x3803... 44, 0xc7c5... 43, 0x7488... 21, 0xa0c1... 18, 0x3628... 16", "wallets": "churn set"},
        {"pattern": "0 contract deployments by tracked wallets this run - 6th straight zero (runs 91, 92, 93, 94, 95, 96)", "wallets": "none"},
        {"pattern": "AFeng 9 sale-calls 0x4d819a2a to 0x1de4... totaling 1.125 BNB (0.5 + 0.25 + 0.25 + 0.125), all status 1, 0 mint logs - SALES, NOT mints", "wallets": "0xbf00... x9"},
        {"pattern": "0 failed txs this run (all 134 receipt candidates status 1)", "wallets": "none"},
    ],
    "quiet": "AFeng 17 txs (9 sale-calls + 8 approvals); future1001.ai 0 txs; 0x2325... 0 txs; 0x8e96... 0 txs; GrokBot 0xfcd0... absent (0 wallets) - 37th consecutive quiet run (59, 61-96) after the run-60 burst; CORLA-97af 0 wallets; CORLA 0x4a9c 0 wallets; all run-64/65 ASI contracts 0 wallets; run-90 tokens 0x6a25.../0x9f7e.../0x8c64.../0xc1ab.../0x1153... 0 wallets (6th quiet run after debut, down from 27/27/27/27/26); run-89 tokens 0xcfdb.../0x0cf8.../0xe68b.../0x31e4... 0 wallets (7th quiet run after debut); run-88 tokens 0x43c8.../0x3d12.../0xeae0... 0 wallets (8th quiet run after debut); run-87 tokens 0x889a.../0x4249... 0 wallets (9th quiet run after debut); run-86 tokens 0x2bfb.../0xc459... 0 wallets (10th quiet run after debut); run-85 token 0x2717... 0 wallets (11th quiet run); run-82 tokens 0xd468.../0xa6e6.../0x887c... all 0 wallets (14th quiet run after debut); run-81 tokens 0 wallets (15th quiet run); run-80 token 0 wallets (16th quiet run); 0x79cd... 0 wallets (rotation STALLED at 20, 7th quiet run after debut); all other run-66/68/69/70/71/72/73/74/75/76/77/78/79 machine tokens 0 wallets.",
}

s["inbound_log_leg_run96"] = {
    "contracts": 1347,
    "attempted": 1347,
    "completed_with_0_hits": 1347,
    "total_logs": 11473,
    "hits": 0,
    "failed": 0,
    "failed_contracts": [],
    "never_attempted": 0,
    "complete": True,
    "note": (
        "Ankr getLogs address-filtered per contract, window 132141791-132149916, from list run93-inbound-contracts.json (1347 contracts = "
        "run93 list, unchanged - 0 deployments in run 96). Full pass a (400, 7,568 logs, 0 failed) + b1 (200, 2,424 logs, 3 failed) + "
        "b2 (200, 573 logs, 3 failed) + b3 (547, 908 logs, 0 failed) = 11,473 logs, 0 hits, 6 FAILED initially (all transient Ankr "
        "'Remote end closed connection without response' from the simultaneous blip at ~contract 146-148 in all four chunks). "
        "All 6 failed contracts retried SAME-RUN (run96-inbound96-retry.py): 6/6 OK, 0 logs, 0 hits - window FULLY CLOSED in-run, no retry "
        "deferred to run 97. 7 truncated contracts, all topic-filtered to 0 logs (a: 0x1de4... AFeng sale, 0x3dca..., 0x55d398... USDT, "
        "0x6288..., 0x636fdfa9... tracker; b1: 0x63de... AGC, 0x7857...) - same set as runs 91-95. "
        "FIRST attempt of chunks a and b3 DIED SILENTLY at ~contract 200-205 (service-restart pattern, same as run 94) - no JSON written, "
        "so both chunks were re-run from scratch (a2/b3-2, idempotent read-only; the inbound scripts write JSON only at the end, so a silent "
        "death loses the whole chunk - check log mtimes + ps if a chunk looks stalled). "
        "All four chunks stalled simultaneously at ~contract 50, ~150, ~250 and ~350 (log mtimes frozen several minutes, processes alive, "
        "0 errors) and resumed on their own each time - shared Ankr slowdown, same pattern as runs 94-95. A frozen log mtime with a live "
        "process is a stall, not a death - wait before re-running."
    ),
}

# --- next_run_note for run 97: surgical updates on the run-96 note ---
note = s["next_run_note"]
def rep(old, new, label):
    global note
    if old in note:
        note = note.replace(old, new)
        print(f"note[{label}]: replaced")
    else:
        print(f"note[{label}]: WARNING - target not found, left unchanged")

rep("Next run sent-tx window starts from block 132141791.",
    "Next run sent-tx window starts from block 132149917.", "window")
rep("13 consecutive runs - persistently unreadable, unverified not absence",
    "14 consecutive runs - persistently unreadable, unverified not absence", "pair14")
rep("(unreadable run 88, 89, 90, 91, 92, 93, 94 AND 95 - retry opportunistically, not an anomaly)",
    "(unreadable run 88, 89, 90, 91, 92, 93, 94, 95 AND 96 - retry opportunistically, not an anomaly)", "pair43c8")
rep("(token0/token1 unreadable run 89, 90, 91, 92, 93, 94 AND 95; 0x31e4 pair 0x60ca0aef... READ OK run 89)",
    "(token0/token1 unreadable run 89, 90, 91, 92, 93, 94, 95 AND 96; 0x31e4 pair 0x60ca0aef... READ OK run 89)", "pair89")
rep("NOTE: fast_rpc worked for the receipts batch in run 95 (112/112)",
    "NOTE: fast_rpc worked for the receipts batch in run 96 (134/134)", "fast_rpc_note")
rep("(2) RETRY run 96 inbound: NONE - run-95 inbound closed fully on first attempt (1347/1347, 0 failed); run-94 window closed by the run-95 "
    "retry of all 32 failed contracts (63 logs, 0 hits). No inbound retry carried into run 96. ",
    "(2) RETRY run 97 inbound: NONE - run-96 inbound closed fully in-run (1347/1347, 11,473 logs, 0 hits; 6 failed contracts retried same-run, "
    "6/6 OK, 0 logs, 0 hits). No inbound retry carried into run 97. ", "retry97")
rep("(3) Run-95 inbound list for run 96 = run93 list (1347) unless run 96's own sent pass finds new deployments to add.",
    "(3) Run-96 inbound list for run 97 = run93 list (1347) unless run 97's own sent pass finds new deployments to add.", "inbound_list")
rep("(4) Run-95 window inbound FULLY CLOSED on first attempt (1347/1347, 11,364 logs, 0 hits, 0 failed). Run-94 window NOW FULLY CLOSED "
    "(1347/1347, 12,552 logs, 0 hits) after the run-95 retry of all 32 failed contracts (63 logs, 0 hits).",
    "(4) Run-96 window inbound FULLY CLOSED in-run (1347/1347, 11,473 logs, 0 hits; 6 failed contracts retried same-run, 6/6 OK, 0 logs, 0 hits). "
    "Run-95 window FULLY CLOSED on first attempt (1347/1347, 11,364 logs, 0 hits, 0 failed).", "window_status")
rep("(5) 0x1153607e... rotation STALLED at 26 wallets (did NOT reach 27 as expected; 0 wallets runs 91-95, 5th quiet run after debut) - watch run 96 "
    "for any resumption; do NOT treat a return as a new rotation. 0x79cd... STALLED at 20 wallets (0 wallets runs 90-95, 6th quiet run) - same.",
    "(5) 0x1153607e... rotation STALLED at 26 wallets (did NOT reach 27 as expected; 0 wallets runs 91-96, 6th quiet run after debut) - watch run 97 "
    "for any resumption; do NOT treat a return as a new rotation. 0x79cd... STALLED at 20 wallets (0 wallets runs 90-96, 7th quiet run) - same.",
    "stalls")
rep("run 95 (ZERO new rotations; all five run-90 tokens 0 wallets, 5th quiet run after debut; 0x1153... STALLED at 26, 5th quiet run; "
    "0x79cd... STALLED at 20, 6th quiet run; inbound FULLY CLOSED first attempt, 0 failed) ",
    "run 95 (ZERO new rotations; all five run-90 tokens 0 wallets, 5th quiet run after debut; 0x1153... STALLED at 26, 5th quiet run; "
    "0x79cd... STALLED at 20, 6th quiet run; inbound FULLY CLOSED first attempt, 0 failed) "
    "run 96 (ZERO new rotations; all five run-90 tokens 0 wallets, 6th quiet run after debut; 0x1153... STALLED at 26, 6th quiet run; "
    "0x79cd... STALLED at 20, 7th quiet run; inbound FULLY CLOSED in-run after 6-contract same-run retry; chunks a/b3 died silently first "
    "attempt ~contract 200, re-run from scratch) ", "history96")
rep("Paid fact: run95 ZERO new rotations; run-90 tokens 0x6a25.../0x9f7e.../0x8c64.../0xc1ab.../0x1153... 0 wallets (5th quiet run after debut); run-89 tokens 0xcfdb.../0x0cf8.../0xe68b.../0x31e4... 0 wallets (6th quiet run after debut); run-88 tokens 0x43c8.../0x3d12.../0xeae0... 0 wallets (7th quiet run after debut); run-87 tokens 0x889a.../0x4249... 0 wallets (8th quiet run after debut); run-86 tokens "
    "0x2bfb.../0xc459... 0 wallets (9th quiet run after debut); run-85 token 0x2717... 0 wallets (10th quiet run); run-82 tokens 0xd468.../0xa6e6.../0x887c... "
    "all 0 wallets (13th quiet run after debut); run-81 tokens 0 wallets (14th quiet run); run-80 token 0 wallets (15th quiet run); "
    "GrokBot 0xfcd0... absent (0 wallets) - 36th consecutive quiet run (59, 61-95) after the run-60 burst;",
    "Paid fact: run96 ZERO new rotations; run-90 tokens 0x6a25.../0x9f7e.../0x8c64.../0xc1ab.../0x1153... 0 wallets (6th quiet run after debut); run-89 tokens 0xcfdb.../0x0cf8.../0xe68b.../0x31e4... 0 wallets (7th quiet run after debut); run-88 tokens 0x43c8.../0x3d12.../0xeae0... 0 wallets (8th quiet run after debut); run-87 tokens 0x889a.../0x4249... 0 wallets (9th quiet run after debut); run-86 tokens "
    "0x2bfb.../0xc459... 0 wallets (10th quiet run after debut); run-85 token 0x2717... 0 wallets (11th quiet run); run-82 tokens 0xd468.../0xa6e6.../0x887c... "
    "all 0 wallets (14th quiet run after debut); run-81 tokens 0 wallets (15th quiet run); run-80 token 0 wallets (16th quiet run); "
    "GrokBot 0xfcd0... absent (0 wallets) - 37th consecutive quiet run (59, 61-96) after the run-60 burst;", "paid_fact")
rep("Run 95 had 0 deployments (5th straight zero; runs 91, 92, 93, 94, 95).",
    "Run 96 had 0 deployments (6th straight zero; runs 91, 92, 93, 94, 95, 96).", "deployments")
rep("AFeng 0 txs; future1001.ai 0 txs; 0x2325... 4 txs (3 aggregator 0x27772d13 + 1 approval, total value 0.11 BNB - 0.1 + 0.01 BNB aggregator txs); 0x8e96... 0 txs; 0x3803... 38 txs (24 aggregator + 12 approvals + 1 USDT transfer + 1 sale-call 0x4d819a2a 0.029 BNB).",
    "AFeng 17 txs (9 sale-calls 0x4d819a2a to 0x1de4... totaling 1.125 BNB + 8 approvals, all status 1, 0 mint logs - sales, NOT mints); future1001.ai 0 txs; 0x2325... 0 txs; 0x8e96... 0 txs; 0x3803... 44 txs (29 aggregator 0x39ecce49 + 15 approvals, churn as usual).", "activity")
rep("PROCESS LESSON (run 86): the receipts pass died silently at 420/461 (service-restart pattern, same as runs 82/84) - the partial-file resume worked; "
    "always re-run the same script to resume rather than re-fetching from scratch. Run 95 receipts completed in one attempt, no resume needed; "
    "inbound chunks did NOT die silently in run 95 (contrast run 94) but all four stalled simultaneously at ~contract 150, ~200 and ~350 "
    "(log mtimes frozen several minutes, processes alive, 0 errors) and resumed on their own each time - shared Ankr slowdown; b1/b2 finished "
    "first, a second, b3 last; 0 failed, inbound FULLY CLOSED on first attempt (1347/1347, 11,364 logs). A frozen log mtime with a live process "
    "is a stall, not a death - wait before re-running.",
    "PROCESS LESSON (run 86): the receipts pass died silently at 420/461 (service-restart pattern, same as runs 82/84) - the partial-file resume worked; "
    "always re-run the same script to resume rather than re-fetching from scratch. Run 96 receipts completed in one attempt, no resume needed; "
    "inbound chunks a and b3 DIED SILENTLY on FIRST attempt at ~contract 200-205 (a log frozen 06:29:27 UTC at [205], b3 log frozen 06:28:59 UTC at "
    "[200], no JSON, no EXIT - service-restart pattern, same as run 94) - both re-run from scratch (a2/b3-2, idempotent read-only) and completed "
    "clean; b1/b2 finished first attempt. All four chunks stalled simultaneously at ~contract 50, ~150, ~250 and ~350 (log mtimes frozen several "
    "minutes, processes alive, 0 errors) and resumed on their own each time - shared Ankr slowdown; plus a simultaneous Ankr blip at ~contract "
    "146-148 in all four chunks (6 failed total, retried SAME-RUN 6/6 OK, 0 logs, 0 hits - window fully closed in-run, no deferral to run 97). "
    "A frozen log mtime with a live process is a stall, not a death - wait before re-running; a log frozen >5 min with NO live process is a "
    "silent death - re-run the chunk from scratch.",
    "process_lesson")
s["next_run_note"] = note

json.dump(s, open(P, "w"), indent=1)
print("state updated; last_run now:", s["last_run"]["run"], "block_end:", s["last_run"]["block_end"])
print("machine_tokens:", len(s.get("machine_tokens", [])), "| signaled:", len(s.get("signaled_projects_over_20pct", [])))
print("inbound96 complete:", s["inbound_log_leg_run96"]["complete"], "| failed:", s["inbound_log_leg_run96"]["failed"])
print("inbound95 complete:", s["inbound_log_leg_run95"]["complete"], "| failed:", s["inbound_log_leg_run95"]["failed"])
