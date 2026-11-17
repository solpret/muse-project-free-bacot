#!/usr/bin/env python3
"""Run 94 state update (read-only job bookkeeping; no chain writes).

Completes run 94 (window 132125940-132134019, tx 2026-11-07 10:08:32 - 11:08:22 WIB).
Sent/receipts/paid done and verified; inbound leg run-94 window 1315/1347 completed
(32 contracts failed transiently - Ankr degraded this run, retry run 95). Run-93
window NOW FULLY CLOSED: retry of all four failed contracts returned 0 logs, 0 hits.
NO new mints. NO new machine-token rotations: all five run-90 rotations 0 wallets
(4th quiet run after debut); 0x1153... STALLED at 26 (4th quiet run);
0x79cd... STALLED at 20 (5th quiet run). 0 deployments this run (4th straight zero).
Bridge unchanged (0 new mints, 0 not_evaluated).
"""
import json, shutil

P = "/home/hatch/workspace/narrative-pulse/tracked-wallet-mint-scan-state.json"
shutil.copy(P, str(P) + ".bak-run94-pre")
s = json.load(open(P))

FAILED94 = ["0x071f76c1868039e2f042dca1890ecb0364d8494a", "0x0834648da9229ad33ed17e47b6dab04134bf79a3",
 "0x08393dad165d90e7258501fe1dfb5f3498644011", "0x1c89acab7a497f537f988b5f20055fd11b062f50",
 "0x1cf9e60218493149ace7dc953497c07175aa625e", "0x29ee92a8d6dc62035d0c2b4d53b5df504d3ebe91",
 "0x2a2463d243e5c4df850e48f350392ad23b494132", "0x2a91b304ee74162007730cf1da24c1d8c137c627",
 "0x681d1f88dd93465f17cab905be299b34ea2c414f", "0x683085af799ce53a5e2682440788724b6f2910c2",
 "0x6834a0b5d3bab31a6d9a5505c2a9534daf46dbaf", "0x7eb3a26f895d4d1b8fcd38a67e9689cb2693661f",
 "0x7fa142c23805387c94fbc4adebf1168a7145f528", "0x8a4e6a11789507f39898b840b351c9b102e4c3e7",
 "0x8a6a0931fd0bf0f54501134db616587d2d27b2e0", "0x8aaa14b24e71cc93672939ba3e3c3e9de2674d27",
 "0x9cc4d56e6ce5c0ddade134b932023b5cab2458d8", "0x9d78b216ae96060895837c60df84893cd5ac34f2",
 "0x9da90fe302a987d979c21d7c3ae421cb0b2cf8b0", "0xa624cd94eaae91ccafa5be9857f476a76f57f61a",
 "0xb594b29360bd45975608c92dbdba764c508b5c99", "0xb5a083bd9e8e330085e8f459f13f080d4f8fe5b4",
 "0xbf3488e453c68e9771c26d448e99d0ec5395135f", "0xbfbde67707d00a759e55ee158abfcb3b33f375fd",
 "0xbfccd7de6ef1b3d81632412600a933cd6de14b77", "0xcee93a5bfad6172358f6012a08d83f0d6d7bad46",
 "0xcfa79d53e2b9451f4792a475a5e6ac39602b1e21", "0xd0079025a9bb66a7a1de991de2e4326faba35729",
 "0xe3f0085fd94d4fb2ae9acb4b49f6c0504e3546a0", "0xe41b54504aa171d92e01384ae3ab3007e170aa70",
 "0xf1822144176ad13c5bccfe33a23129c37ca5bdcd", "0xf1968d3f690b2327afef1b8aa87a4fe9e1090591"]

last_run_94 = {
    "run": 94,
    "block_start": 132125940,
    "block_end": 132134019,
    "window_wib": "2026-11-07 10:08:32 - 11:08:22 WIB (tx times); run executed ~11:05 - ~12:00 WIB; sent-pass in-window txs 184, 0 mint-pattern txs",
    "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set); 0 failed, no retry needed.",
    "method_note": (
        "Sent pass Ankr ankr_getTransactionsByAddress via module: 55/55 OK first attempt, 184 txs, 7 wallets active. "
        "Receipts via fast_rpc batch (6, ~4s pause) for 123 non-approve candidates: 123 status 1, 0 status 0, 0 null, 0 mint logs. "
        "Receipts completed in one attempt, no resume needed. "
        "Paid: 27 tokens; max 3 wallets/token (14 at 3, 6 at 2, 7 at 1 - usual ...7777 churn, no new rotation; 22 of 27 tokens end ...7777). "
        "ALL run-90 machine-token rotations 0 wallets this run - 4th quiet run after debut for 0x6a2590934e55671a6fab9fa8edca8da4960e7777, "
        "0x9f7ea7a4eaa7f39782caeb1ecab8176187e97777, 0x8c64aa82e861393bf760ee6d0eb29c0c60f07777, "
        "0xc1ab1e832da23f85a27aa2778f555d00319e7777 (27 wallets each in run 90). "
        "0x1153607e323c42f93c82b80e1772f9cc626b7777: 0 wallets this run - rotation STALLED at 26 wallets "
        "(missing wallet 0x2cc8192fc6 never bought in); 4th quiet run after debut. "
        "0x79cd174ca3ec25c06ff5fddae365643f73d77777: 0 wallets this run - rotation STALLED at 20 wallets; 5th quiet run after debut (runs 88-89 active). "
        "No anomaly under the fast-path amendment (no size deviation, name/symbol, website, or free-mint path appeared for any of them) - "
        "state-only, NO chat report. "
        "AFeng 0 txs; future1001.ai 0 txs; 0x8e96... 0 txs; 0x2325... 4 txs (3 aggregator 0x27772d13 + 1 approval, "
        "total value 0.12 BNB - the 0.1 BNB aggregator tx 0x6d7e412d1cc6bc06bd0d4244b6b9465df39c08abb9282eccdcf1825b4c721f86 at 10:47:31 WIB, "
        "receipt checked, 11 logs, 0 mint logs, NOT a mint; plus a 0.02 BNB aggregator tx 0xedb18ce8f62d9209c9c3ab52a6f8ed9380bd5a121285ccf83e3a1fa97216e759 "
        "at 10:26:18 WIB, receipt status 1, 13 logs, 0 mint logs, NOT a mint); 0x3803... 42 txs (28 aggregator 0x39ecce49 + 14 approvals, "
        "total value 0.000364 BNB, churn as usual). "
        "Selectors (sent pass, 184 txs): 45 PCS buys (0xb6f9de95) + 47 PCS sells (0x791ac947) + 61 approvals (0x095ea7b3) + 28 aggregator (0x39ecce49) + "
        "3 aggregator (0x27772d13). Nonzero-value txs 61, total 0.12297 BNB, max 0.1 BNB (aggregator 0x2325... above). "
        "Most active wallets: 0xad94... 44 txs, 0xc7c5... 42, 0x3803... 42, 0x3628... 20, 0xa0c1... 18, 0x7488... 14, 0x2325... 4. "
        "Deployments: 0 contract creations by tracked wallets this run - 4th straight zero (runs 91, 92, 93, 94). Run-94 inbound list = run93 list (1347), unchanged. "
        "Inbound leg run-94 WINDOW: 1315/1347 contracts completed, 12,489 logs, 0 hits, 32 FAILED (all transient Ankr timeouts / 'Remote end closed "
        "connection without response' - NOT verified as 0 hits for those contracts; retry run 95). Chunks a (400, 7,517 logs, 8 failed) + "
        "b1 (200, 2,546 logs, 8 failed) + b2 (200, 1,047 logs, 9 failed) + b3 (547, 1,379 logs, 7 failed) = 12,489 logs. "
        "7 truncated contracts, all topic-filtered to 0 logs (a: 0x1de4... AFeng sale, 0x3dca..., 0x55d398... USDT, 0x6288..., 0x636fdfa9... tracker; "
        "b1: 0x63de... AGC, 0x7857...) - same set as runs 91-93. "
        "FIRST ATTEMPT of the inbound chunks died silently at ~contract 85-87 in all four chunks at 11:20:03 WIB (service-restart pattern, same as "
        "run-86 receipts) - no JSON written; all four chunks re-ran from scratch (idempotent read-only; each first-attempt failed contract was "
        "re-checked successfully in the re-run). Ankr was degraded this run: near-simultaneous blips at contracts ~26-27, ~110-114 and ~153-159 "
        "in all chunks, plus slow stretches (contracts 250-300) that resumed on their own. "
        "Run-93 window NOW FULLY CLOSED: retry of all four failed contracts (0x23f5cdd2... 0 logs, 0x84f7747b... 0 logs, 0xb955e0bf... 0 logs, "
        "0xe86c2e52... 0 logs; run94-inbound93-retry.json) returned 0 hits - run-93 inbound is 1347/1347, 11,883 logs, 0 hits. "
        "Pair token0/token1 STILL UNREADABLE for ALL EIGHT pairs in run-94 pair retry (fast_rpc race 'all endpoints failed', OSError/TimeoutError "
        "on every endpoint, 12th consecutive run for a6e6/887c/2bfb/c459, 7th for 43c8, 5th for the three run-89 rotation pairs cfdb/0cf8/e68b) - "
        "unverified, not absence; retry run 95. NOTE: fast_rpc batch worked fine for the receipts pass in the same run (123/123) - the outage "
        "is time-varying / per-call, not a permanent endpoint failure. "
        "Pointer-discovery (amendment 19:10): 0 contracts processed - no new mints this run, and the backfill queue is empty (bridge 115 "
        "contracts, 0 not_evaluated); bridge unchanged. "
        "SILENT RUN - no chat report (no new mints, no Free Bacot signal, no auto-mint trigger, no reportable paid trend). "
        "No preview/mint/sign/login/purchase by this job."
    ),
}
cur_run = s.get("last_run", {}).get("run", 0)
if cur_run < 94:
    s["last_run"] = last_run_94
    print(f"last_run set to 94 (was {cur_run})")
else:
    print(f"last_run already {cur_run} (>=94) - NOT regressing")
    s["run94_last_run_record"] = last_run_94

# Close the run-93 inbound leg: retry of all four failed contracts succeeded (0 hits).
if "inbound_log_leg_run93" in s:
    leg93 = s["inbound_log_leg_run93"]
    leg93["completed_with_0_hits"] = 1347
    leg93["failed"] = 0
    leg93["failed_contracts"] = []
    leg93["complete"] = True
    leg93["note"] = leg93.get("note", "") + (
        " RUN-94 UPDATE: retry of all four failed contracts for the run-93 window 132119035-132125939 returned 0 hits "
        "(0x23f5cdd233925ea83369a495b95f825ed710fbaa: 0 logs, 0x84f7747b0a8dfaf636b06087c635ecb7a2a49791: 0 logs, "
        "0xb955e0bf694da92fecd63c3e98b00216be959138: 0 logs, 0xe86c2e52a5ebaf4afd18020834d5c771aff59cde: 0 logs; "
        "run94-inbound93-retry.json) - run-93 window inbound NOW FULLY CLOSED (1347/1347, 11,883 logs, 0 hits)."
    )
    print("inbound93 leg closed: 1347/1347, complete=True")

# Update the run-90 0x1153 entry in place (0 wallets run 94 - 4th quiet run, stalled at 26).
for mt in s.get("machine_tokens", []):
    if mt.get("address", "").lower() == "0x1153607e323c42f93c82b80e1772f9cc626b7777":
        mt["machine_wallets"] = 26
        mt["label"] = "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - rotation STALLED at 26 wallets (runs 91-94)"
        mt["note"] = mt.get("note", "") + (
            " RUN-94 UPDATE: 0 wallets this run - rotation STALLED at 26 wallets; 4th quiet run after debut. No buys and no sells from "
            "tracked wallets for this token in the run-94 window. Not treated as an anomaly under the fast-path amendment (no size deviation, "
            "name/symbol, website, or free-mint path appeared); watch run 95 for any resumption, do NOT treat a return as a new rotation."
        )
        print("1153 entry updated: stalled at 26, 0 wallets run 94 (4th quiet run)")
        break
# Update the run-88/89 0x79cd entry in place (0 wallets run 94 - 5th quiet run, stalled at 20).
for mt in s.get("machine_tokens", []):
    if mt.get("address", "").lower() == "0x79cd174ca3ec25c06ff5fddae365643f73d77777":
        mt["machine_wallets"] = 20
        mt["label"] = "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - rotation STALLED at 20 wallets (runs 90-94)"
        mt["note"] = mt.get("note", "") + (
            " RUN-94 UPDATE: 0 wallets this run - rotation STALLED at 20 wallets; 5th quiet run after debut (runs 88-89 active). No buys and "
            "no sells from tracked wallets for this token in the run-94 window. Not treated as an anomaly under the fast-path amendment; "
            "watch run 95 for any resumption, do NOT treat a return as a new rotation."
        )
        print("79cd entry updated: stalled at 20, 0 wallets run 94 (5th quiet run)")
        break

s["paid_trend_run94"] = {
    "note": "Aggregate only, NOT a buy recommendation. NO new machine-token rotations this run; all five run-90 rotations 0 wallets (4th quiet run after debut); 0x1153... STALLED at 26 wallets (4th quiet run); 0x79cd... STALLED at 20 wallets (5th quiet run). 0 deployments - 4th straight zero. SILENT RUN - no chat report (no new mints, no Free Bacot signal, no auto-mint trigger, no reportable paid trend beyond routine churn).",
    "rotations": "NONE NEW. Run-90 rotations all 0 wallets (4th quiet run after debut): 0x6a2590934e55671a6fab9fa8edca8da4960e7777, 0x9f7ea7a4eaa7f39782caeb1ecab8176187e97777, 0x8c64aa82e861393bf760ee6d0eb29c0c60f07777, 0xc1ab1e832da23f85a27aa2778f555d00319e7777 (27 wallets each in run 90) + 0x1153607e323c42f93c82b80e1772f9cc626b7777 (26 wallets in run 90, did NOT reach 27 - STALLED at 26). All paid-only with no free-mint path; auto-mint blocked at guard (c); recorded in state, NO chat report per fast-path amendment.",
    "other_paid_activity": [
        {"pattern": "27 paid tokens: 14 at 3 wallets, 6 at 2, 7 at 1 (usual ...7777 churn; 22 of 27 end ...7777)", "wallets": "see run94-paid.json"},
        {"pattern": "Micro round-trip churn continues: 45 PCS buys (0xb6f9de95) + 47 PCS sells (0x791ac947), 61 approvals (0x095ea7b3), 28 aggregator txs (0x39ecce49) + 3 aggregator (0x27772d13); top active 0xad94... 44 txs, 0xc7c5... 42, 0x3803... 42, 0x3628... 20, 0xa0c1... 18, 0x7488... 14, 0x2325... 4", "wallets": "churn set"},
        {"pattern": "0 contract deployments by tracked wallets this run - 4th straight zero (runs 91, 92, 93, 94)", "wallets": "none"},
        {"pattern": "2 aggregator txs by 0x2325... (0.1 BNB 10:47:31 WIB tx 0x6d7e41... + 0.02 BNB 10:26:18 WIB tx 0xedb18c..., both status 1, 0 mint logs) - NOT mints", "wallets": "0x2325... x2"},
        {"pattern": "0 failed txs this run (all 123 receipt candidates status 1)", "wallets": "none"},
    ],
    "quiet": "AFeng 0 txs; future1001.ai 0 txs; 0x8e96... 0 txs; 0x2325... 4 txs (3 aggregator + 1 approval, churn as usual); GrokBot 0xfcd0... absent (0 wallets) - 35th consecutive quiet run (59, 61-94) after the run-60 burst; CORLA-97af 0 wallets; CORLA 0x4a9c 0 wallets; all run-64/65 ASI contracts 0 wallets; run-90 tokens 0x6a25.../0x9f7e.../0x8c64.../0xc1ab.../0x1153... 0 wallets (4th quiet run after debut, down from 27/27/27/27/26); run-89 tokens 0xcfdb.../0x0cf8.../0xe68b.../0x31e4... 0 wallets (5th quiet run after debut); run-88 tokens 0x43c8.../0x3d12.../0xeae0... 0 wallets (6th quiet run after debut); run-87 tokens 0x889a.../0x4249... 0 wallets (7th quiet run after debut); run-86 tokens 0x2bfb.../0xc459... 0 wallets (8th quiet run after debut); run-85 token 0x2717... 0 wallets (9th quiet run); run-82 tokens 0xd468.../0xa6e6.../0x887c... all 0 wallets (12th quiet run after debut); run-81 tokens 0 wallets (13th quiet run); run-80 token 0 wallets (14th quiet run); 0x79cd... 0 wallets (rotation STALLED at 20, 5th quiet run after debut); all other run-66/68/69/70/71/72/73/74/75/76/77/78/79 machine tokens 0 wallets.",
}

s["inbound_log_leg_run94"] = {
    "contracts": 1347,
    "attempted": 1347,
    "completed_with_0_hits": 1315,
    "total_logs": 12489,
    "hits": 0,
    "failed": 32,
    "failed_contracts": FAILED94,
    "never_attempted": 0,
    "complete": False,
    "note": (
        "Ankr getLogs address-filtered per contract, window 132125940-132134019, from list run94-inbound-contracts.json (1347 contracts = "
        "run93 list, unchanged - 0 deployments in run 94). Full pass a (400, 7,517 logs, 8 failed) + b1 (200, 2,546 logs, 8 failed) + "
        "b2 (200, 1,047 logs, 9 failed) + b3 (547, 1,379 logs, 7 failed) = 12,489 logs, 0 hits, 32 FAILED (all transient Ankr timeouts / "
        "'Remote end closed connection without response' - retry run 95; those contracts are NOT verified as 0 hits for the run-94 window). "
        "7 truncated contracts, all topic-filtered to 0 logs (a: 0x1de4... AFeng sale, 0x3dca..., 0x55d398... USDT, 0x6288..., 0x636fdfa9... "
        "tracker; b1: 0x63de... AGC, 0x7857...) - same set as runs 91-93. "
        "FIRST ATTEMPT of the inbound chunks died silently at ~contract 85-87 in all four chunks at 11:20:03 WIB (service-restart pattern, same "
        "as run-86 receipts) - no JSON written; all four chunks re-ran from scratch (idempotent read-only; each first-attempt failed contract was "
        "re-checked successfully in the re-run). Ankr was degraded this run: near-simultaneous blips at contracts ~26-27, ~110-114 and ~153-159 "
        "in all chunks, plus slow stretches (contracts 250-300) that resumed on their own. "
        "RUN-94 WINDOW INBOUND NOT FULLY CLOSED (1315/1347) - the 32 failed contracts are the only open items. "
        "Run-93 window closed in this run (retry of all four failed contracts 0 hits - see inbound_log_leg_run93, now complete=True)."
    ),
}

# --- next_run_note for run 95: surgical updates on the run-94 note ---
note = s["next_run_note"]
def rep(old, new, label):
    global note
    if old in note:
        note = note.replace(old, new)
        print(f"note[{label}]: replaced")
    else:
        print(f"note[{label}]: WARNING - target not found, left unchanged")

rep("Next run sent-tx window starts from block 132125940.",
    "Next run sent-tx window starts from block 132134020.", "window")
rep("11 consecutive runs - persistently unreadable, unverified not absence",
    "12 consecutive runs - persistently unreadable, unverified not absence", "pair12")
rep("(unreadable run 88, 89, 90, 91, 92 AND 93 - retry opportunistically, not an anomaly)",
    "(unreadable run 88, 89, 90, 91, 92, 93 AND 94 - retry opportunistically, not an anomaly)", "pair43c8")
rep("(token0/token1 unreadable run 89, 90, 91, 92 AND 93; 0x31e4 pair 0x60ca0aef... READ OK run 89)",
    "(token0/token1 unreadable run 89, 90, 91, 92, 93 AND 94; 0x31e4 pair 0x60ca0aef... READ OK run 89)", "pair89")
rep("NOTE: fast_rpc worked for the receipts batch in run 93 (123/123)",
    "NOTE: fast_rpc worked for the receipts batch in run 94 (123/123)", "fast_rpc_note")
rep("""(2) RETRY run 94 inbound: contracts 0x23f5cdd233925ea83369a495b95f825ed710fbaa, 0x84f7747b0a8dfaf636b06087c635ecb7a2a49791, "
    "0xb955e0bf694da92fecd63c3e98b00216be959138 and 0xe86c2e52a5ebaf4afd18020834d5c771aff59cde failed in run 93 "
    "('Remote end closed connection without response') - re-check them for the run-93 window 132119035-132125939 (topic-filtered, Transfer from "
    "zero address to tracked wallets) before treating the run-93 window as closed. """,
    "(2) RETRY run 95 inbound: 32 contracts failed in run 94 (all transient Ankr timeouts / 'Remote end closed connection without response') - "
    "re-check them for the run-94 window 132125940-132134019 (topic-filtered, Transfer from zero address to tracked wallets) before treating the "
    "run-94 window as closed: " + ", ".join(FAILED94) + ". ", "retry95")
rep("(3) Run-93 inbound list for run 94 = run92 list (1347) unless run 94's own sent pass finds new deployments to add.",
    "(3) Run-94 inbound list for run 95 = run93 list (1347) unless run 95's own sent pass finds new deployments to add.", "inbound_list")
rep("(4) Run-93 window inbound NOT FULLY CLOSED (1343/1347, 11,883 logs, 0 hits, 4 failed - see (2)). Run-92 window NOW FULLY CLOSED "
    "(1347/1347, 13,000 logs, 0 hits) after the run-93 retry of both failed contracts (0x3bf1... 98 logs, 0xfcea... 0 logs).",
    "(4) Run-94 window inbound NOT FULLY CLOSED (1315/1347, 12,489 logs, 0 hits, 32 failed - see (2)). Run-93 window NOW FULLY CLOSED "
    "(1347/1347, 11,883 logs, 0 hits) after the run-94 retry of all four failed contracts (0x23f5... 0 logs, 0x84f7... 0 logs, 0xb955... 0 logs, "
    "0xe86c... 0 logs).", "window_status")
rep("(5) 0x1153607e... rotation STALLED at 26 wallets (did NOT reach 27 as expected; 0 wallets runs 91-93, 3rd quiet run after debut) - watch run 94 "
    "for any resumption; do NOT treat a return as a new rotation. 0x79cd... STALLED at 20 wallets (0 wallets runs 90-93, 4th quiet run) - same.",
    "(5) 0x1153607e... rotation STALLED at 26 wallets (did NOT reach 27 as expected; 0 wallets runs 91-94, 4th quiet run after debut) - watch run 95 "
    "for any resumption; do NOT treat a return as a new rotation. 0x79cd... STALLED at 20 wallets (0 wallets runs 90-94, 5th quiet run) - same.",
    "stalls")
rep("run 93 (ZERO new rotations; all five run-90 tokens 0 wallets, 3rd quiet run after debut; 0x1153... STALLED at 26, 3rd quiet run; "
    "0x79cd... STALLED at 20, 4th quiet run) ",
    "run 93 (ZERO new rotations; all five run-90 tokens 0 wallets, 3rd quiet run after debut; 0x1153... STALLED at 26, 3rd quiet run; "
    "0x79cd... STALLED at 20, 4th quiet run) "
    "run 94 (ZERO new rotations; all five run-90 tokens 0 wallets, 4th quiet run after debut; 0x1153... STALLED at 26, 4th quiet run; "
    "0x79cd... STALLED at 20, 5th quiet run) ", "history94")
rep("Paid fact: run93 ZERO new rotations; run-90 tokens 0x6a25.../0x9f7e.../0x8c64.../0xc1ab.../0x1153... 0 wallets (3rd quiet run after debut); run-89 tokens 0xcfdb.../0x0cf8.../0xe68b.../0x31e4... 0 wallets (4th quiet run after debut); run-88 tokens 0x43c8.../0x3d12.../0xeae0... 0 wallets (5th quiet run after debut); run-87 tokens 0x889a.../0x4249... 0 wallets (6th quiet run after debut); run-86 tokens "
    "0x2bfb.../0xc459... 0 wallets (7th quiet run after debut); run-85 token 0x2717... 0 wallets (8th quiet run); run-82 tokens 0xd468.../0xa6e6.../0x887c... "
    "all 0 wallets (11th quiet run after debut); run-81 tokens 0 wallets (12th quiet run); run-80 token 0 wallets (13th quiet run); "
    "GrokBot 0xfcd0... absent (0 wallets) - 34th consecutive quiet run (59, 61-93) after the run-60 burst;",
    "Paid fact: run94 ZERO new rotations; run-90 tokens 0x6a25.../0x9f7e.../0x8c64.../0xc1ab.../0x1153... 0 wallets (4th quiet run after debut); run-89 tokens 0xcfdb.../0x0cf8.../0xe68b.../0x31e4... 0 wallets (5th quiet run after debut); run-88 tokens 0x43c8.../0x3d12.../0xeae0... 0 wallets (6th quiet run after debut); run-87 tokens 0x889a.../0x4249... 0 wallets (7th quiet run after debut); run-86 tokens "
    "0x2bfb.../0xc459... 0 wallets (8th quiet run after debut); run-85 token 0x2717... 0 wallets (9th quiet run); run-82 tokens 0xd468.../0xa6e6.../0x887c... "
    "all 0 wallets (12th quiet run after debut); run-81 tokens 0 wallets (13th quiet run); run-80 token 0 wallets (14th quiet run); "
    "GrokBot 0xfcd0... absent (0 wallets) - 35th consecutive quiet run (59, 61-94) after the run-60 burst;", "paid_fact")
rep("Run 93 had 0 deployments (3rd straight zero; runs 91, 92, 93).",
    "Run 94 had 0 deployments (4th straight zero; runs 91, 92, 93, 94).", "deployments")
rep("AFeng 0 txs; future1001.ai 0 txs; 0x2325... 7 txs (4 aggregator + 3 approvals, total value 0.1 BNB); 0x8e96... 0 txs; 0x3803... 39 txs (23 aggregator + 16 approvals).",
    "AFeng 0 txs; future1001.ai 0 txs; 0x2325... 4 txs (3 aggregator 0x27772d13 + 1 approval, total value 0.12 BNB - 0.1 + 0.02 BNB aggregator txs); 0x8e96... 0 txs; 0x3803... 42 txs (28 aggregator + 14 approvals).", "activity")
rep("PROCESS LESSON (run 86): the receipts pass died silently at 420/461 (service-restart pattern, same as runs 82/84) - the partial-file resume worked; "
    "always re-run the same script to resume rather than re-fetching from scratch. Run 93 receipts completed in one attempt, no resume needed; "
    "inbound chunks a/b1/b2/b3 all completed first attempt in run 93 (no silent deaths; slow stretches at contracts 150-200 and 200-250 resumed on "
    "their own; one near-simultaneous transient Ankr blip at ~contract 131-134 cost exactly 1 contract per chunk, each recovered immediately).",
    "PROCESS LESSON (run 86): the receipts pass died silently at 420/461 (service-restart pattern, same as runs 82/84) - the partial-file resume worked; "
    "always re-run the same script to resume rather than re-fetching from scratch. Run 94 receipts completed in one attempt, no resume needed; "
    "inbound chunks died silently on FIRST attempt at ~contract 85-87 in all four chunks at 11:20:03 WIB (service-restart pattern) - no JSON written, "
    "so all four chunks were re-run from scratch (idempotent read-only; the inbound scripts write JSON only at the end, so a silent death loses the "
    "whole chunk - check log mtimes + ps if a chunk looks stalled). Ankr was degraded in run 94: near-simultaneous blips at contracts ~26-27, "
    "~110-114 and ~153-159 in all chunks (32 failed total, retry run 95) plus slow stretches at contracts 250-300 that resumed on their own.",
    "process_lesson")
s["next_run_note"] = note

json.dump(s, open(P, "w"), indent=1)
print("state updated; last_run now:", s["last_run"]["run"], "block_end:", s["last_run"]["block_end"])
print("machine_tokens:", len(s.get("machine_tokens", [])), "| signaled:", len(s.get("signaled_projects_over_20pct", [])))
print("inbound94 complete:", s["inbound_log_leg_run94"]["complete"], "| failed:", s["inbound_log_leg_run94"]["failed"])
print("inbound93 complete:", s["inbound_log_leg_run93"]["complete"], "| failed:", s["inbound_log_leg_run93"]["failed"])
