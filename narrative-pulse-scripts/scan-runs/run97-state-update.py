#!/usr/bin/env python3
"""Run 97 state update (read-only job bookkeeping; no chain writes).

Completes run 97 (window 132149917-132158490, tx 2026-11-07 13:08:34 - 14:11:56 WIB).
Sent/receipts/paid done and verified; inbound leg run-97 window FULLY CLOSED in-run
(1374/1374, 12,655 logs, 0 hits; 2 failed contracts retried same-run, 2/2 OK, 0 logs).
NO new mints. TWO NEW machine-token rotations at 27 wallets each - BOTH NAMED
(Timothy/TIMOTHY + symbol BTC), the FIRST named machine-token rotations: anomaly
under the fast-path amendment, reported ONCE as a paid-only signal (not a lead,
not a buy recommendation, auto-mint blocked at guard (c)). 25 deployments this run
(first after 6 straight zero runs). Bridge unchanged (0 new mints, 0 not_evaluated).
"""
import json, shutil

P = "/home/hatch/workspace/narrative-pulse/tracked-wallet-mint-scan-state.json"
shutil.copy(P, str(P) + ".bak-run97-pre")
s = json.load(open(P))

last_run_97 = {
    "run": 97,
    "block_start": 132149917,
    "block_end": 132158490,
    "window_wib": "2026-11-07 13:08:34 - 14:11:56 WIB (tx times); run executed ~14:05 - ~15:15 WIB; sent-pass in-window txs 723, 0 mint-pattern txs",
    "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set); 0 failed, no retry needed.",
    "method_note": (
        "Sent pass Ankr ankr_getTransactionsByAddress via module: 55/55 OK first attempt, 723 txs, 35 wallets active. "
        "Receipts via fast_rpc batch (6, ~4s pause) for 462 non-approve candidates: 460 status 1, 2 status 0, 0 null, 0 mint logs. "
        "Receipts completed in one attempt, no resume needed. "
        "Paid: 29 tokens; max 27 wallets/token (TWO new rotations at 27 each - see anomaly signal; 14 tokens at 3 wallets, all the same churn trio "
        "0x3803/0xad94/0xc7c5, all ...7777; 8 at 2, 5 at 1; 0 overlap with run-96's 32 paid tokens - the ...7777 churn set turns over every run). "
        "NEW ROTATIONS - ANOMALY (named tokens, first time in the machine-token class): 0xc90a6cf8d74cf3540eaca3ce63ea7ae4e1ec7777 "
        "(Timothy/TIMOTHY, name+symbol confirmed 2x via fast_rpc, totalSupply 1e27, decimals unverified - fast_rpc timeouts) and "
        "0xe3a8e1ca392b316c42d780c3cf15202f80f37777 (symbol BTC confirmed 1x, totalSupply 1e27, decimals 18; name() unreadable - fast_rpc timeouts, "
        "not absent). Both bought by the SAME 27-wallet machine set, byte-identical to each other and diff 0 vs the run-90 machine set (27/27 overlap). "
        "Buy sizes WITHIN class norm (NOT a size anomaly): first buy 0.000121241835355714 BNB each (9,674.63 tokens), follow-up median 0.221423 "
        "(c90a, max 0.371697, total 9.1951 BNB, 53 buys, 96 sells) / 0.223379 (e3a8, max 0.413838, total 9.9327 BNB, 58 buys, 100 sells). "
        "First buys both by 0xcb08c02c0a: c90a 14:01:10 WIB tx 0xa9bb2a67b61de46564bf3096ffd2fbd1ac5efc6e0bcb81981f6f5f0cbb900079 block 132157055, "
        "pair 0x066aa46ee270d041353749ee9ae485323bd6e6d1; e3a8 13:43:12 WIB tx 0x305ada6cd0b7b80c54a188f6b50346864d060129048706c93744908b3f6f3e5b block 132154658, "
        "pair 0xa39db5002d7ee3dc4596243789702ff4fab993f4. DexScreener independently confirms both: TIMOTHY/WBNB and BTC/WBNB, liquidity $0.07 each "
        "(drained after the rotation's sells), pairs created 14:00:56 / 13:42:59 WIB. Pair token0/token1 unreadable (fast_rpc 'all endpoints failed') - "
        "unverified, not absence; retry run 98. Auto-mint BLOCKED at guard (c) for both (paid PCS tokens, no free-mint path; guard (a) website also "
        "unverified) - no preview, no execution. Anomaly reported ONCE as a paid-only signal per the fast-path amendment (name/symbol appeared); "
        "both recorded in machine_tokens + signaled_projects_over_20pct (paid-only, run-97). "
        "ALL run-90 machine-token rotations 0 wallets this run - 7th quiet run after debut for 0x6a2590934e55671a6fab9fa8edca8da4960e7777, "
        "0x9f7ea7a4eaa7f39782caeb1ecab8176187e97777, 0x8c64aa82e861393bf760ee6d0eb29c0c60f07777, "
        "0xc1ab1e832da23f85a27aa2778f555d00319e7777 (27 wallets each in run 90). "
        "0x1153607e323c42f93c82b80e1772f9cc626b7777: 0 wallets this run - rotation STALLED at 26 wallets "
        "(missing wallet 0x2cc8192fc6 never bought in); 7th quiet run after debut. "
        "0x79cd174ca3ec25c06ff5fddae365643f73d77777: 0 wallets this run - rotation STALLED at 20 wallets; 8th quiet run after debut (runs 88-89 active). "
        "Deployments: 25 contract creations by tracked wallets this run - FIRST after 6 straight zero runs (91-96); all at 13:59:08-13:59:47 WIB by 11 "
        "machine-set wallets (0x97bd895f alone 11, 0xf795c525/0x3154f694/0xcb08c02c/0x9b519f5d 2 each, 7 wallets 1 each). Deployed addresses added to the "
        "inbound list (run97-inbound-contracts.json, 1374 total) and carried to run 98. Deployed contracts' metadata mostly unreadable (fast_rpc "
        "timeouts; one returned name 0x empty) - unverified, not absence; no mint logs from them in-window (inbound 0 hits covers them). "
        "AFeng 2 txs (1 sale-call 0x4d819a2a to 0x1de4... value 0, status 1, 13 logs, 0 mint logs - a SALE, NOT a mint + 1 approval to SLIME "
        "0x8351311fe78e9045a5eebcb11db9d700658c7777); future1001.ai 0 txs; 0x2325... 2 txs (1 aggregator 0x27772d13 + 1 approval, value 0); "
        "0x8e96... 0 txs; 0x3803... 42 txs (28 aggregator 0x39ecce49 + 14 approvals, total value 0.000364 BNB, churn as usual). "
        "Selectors (sent pass, 723 txs): 261 approvals (0x095ea7b3) + 246 PCS sells (0x791ac947) + 160 PCS buys (0xb6f9de95) + 29 aggregator (0x39ecce49) + "
        "25 contract creations (0x60806040) + 1 aggregator (0x27772d13, 0x2325...) + 1 sale-call (0x4d819a2a, AFeng) + 1 plain transfer (empty input). "
        "Nonzero-value txs 200, total 19.8179 BNB, max 0.4138 BNB (e3a8 follow-up buy); 27-set window totals: 111 buys 19.1278 BNB + 198 sells + "
        "196 approvals + 25 deployments. 2 status-0 txs: failed PCS sells by 0xc6219468 (14:07:14 WIB) and 0xa952331e (14:03:54 WIB), both machine-set "
        "wallets in the c90a wave. "
        "Most active wallets: 0xc7c5... 43 txs, 0xad94... 42, 0x3803... 42, 0x9cdd... 36, 0xa952... 34, 0xc621... 33, 0xf795... 26, 0xe9ed... 26, "
        "0x3628... 24, 0x92bc... 24, 0x9b51... 24, 0xfdec... 24, 0xa0c1... 23, 0x1cce... 23, 0xdb2d... 22, 0xf968... 22. Run-97 inbound list = run93 list "
        "(1347) + 25 run-97 deployments + 2 new rotation tokens = 1374. "
        "Inbound leg run-97 WINDOW: FULLY CLOSED in-run - 1374/1374 contracts, 12,655 logs, 0 hits. "
        "Chunks a (400, 7,598 logs, 0 failed) + b1 (200, 2,446 logs, 0 failed) + b2 (200, 542 logs, 0 failed) + b3 (574, 2,069 logs, 2 failed) = 12,655 logs. "
        "2 failed contracts (both transient Ankr 'Remote end closed connection without response': 0xca8820d36bec22e462a45b6f658d3f7bb2542a82, "
        "0xee8d9edfeecfc175a76387a25581c2dc9f5f85f5) retried SAME-RUN (run97-inbound97-retry.py): 2/2 OK, 0 logs, 0 hits - window fully closed without "
        "deferring to run 98. "
        "8 truncated contracts, all topic-filtered to 0 logs (a: 0x10b389... (back this run), 0x1de4... AFeng sale, 0x3dca..., 0x55d398... USDT, "
        "0x6288..., 0x636fdfa9... tracker; b1: 0x63de... AGC, 0x7857...) - same set as runs 91-96 plus 0x10b3... returning. "
        "FIRST attempt of all four chunks WEDGED at ~contract 8-10 (log mtimes frozen 07:26-07:27 UTC, processes alive, sockets stuck in poll on the "
        "egress proxy for 5+ min while a fresh getLogs call worked in ~5s - NOT a silent death, a wedged socket; killed by PID and re-launched "
        "from scratch, idempotent read-only). Re-launched chunks stalled simultaneously at ~contract 50, ~100, ~150, ~250, ~300, ~350 and ~400 "
        "(log mtimes frozen several minutes, processes alive, 0 errors) and resumed on their own each time - shared Ankr slowdown, same pattern "
        "as runs 94-96. "
        "Pair token0/token1 STILL UNREADABLE for ALL EIGHT pairs in run-97 pair retry (fast_rpc race 'all endpoints failed', TimeoutError on every "
        "endpoint, 15th consecutive run for a6e6/887c/2bfb/c459, 10th for 43c8, 8th for the three run-89 rotation pairs cfdb/0cf8/e68b) - "
        "unverified, not absence; retry run 98. NOTE: fast_rpc batch worked fine for the receipts pass in the same run (462/462) and intermittently "
        "for token-meta reads - the outage is time-varying / per-call, not a permanent endpoint failure. Ankr eth_call is NOT available on the "
        "multichain endpoint (method -32601) - cannot substitute for fast_rpc reads. "
        "Pointer-discovery (amendment 19:10): 0 contracts processed - no new mints this run, and the backfill queue is empty (bridge 115 "
        "contracts, 0 not_evaluated); bridge unchanged. "
        "CHAT REPORT this run: the named-machine-token anomaly signal (paid-only, NOT a lead, NOT a buy recommendation, auto-mint blocked guard (c)) - "
        "reported once per the fast-path amendment. No new mints, no Free Bacot signal beyond that, no auto-mint trigger execution. "
        "No preview/mint/sign/login/purchase by this job."
    ),
}
cur_run = s.get("last_run", {}).get("run", 0)
if cur_run < 97:
    s["last_run"] = last_run_97
    print(f"last_run set to 97 (was {cur_run})")
else:
    print(f"last_run already {cur_run} (>=97) - NOT regressing")
    s["run97_last_run_record"] = last_run_97

# --- new machine_tokens entries: the two NAMED rotations (anomaly class) ---
s.setdefault("machine_tokens", []).append({
    "address": "0xc90a6cf8d74cf3540eaca3ce63ea7ae4e1ec7777",
    "first_seen": "run-97, 2026-11-07 14:01:10 WIB (tx 0xa9bb2a67b61de46564bf3096ffd2fbd1ac5efc6e0bcb81981f6f5f0cbb900079, block 132157055)",
    "machine_wallets": 27,
    "typical_first_buy_bnb": 0.000121241835355714,
    "followup_buy_range_bnb": "median 0.221423, max 0.371697, total buys 9.1951 BNB (53 sent buys)",
    "label": "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - NAMED (Timothy/TIMOTHY) - ANOMALY, reported once as signal run 97",
    "note": (
        "ANOMALY under the fast-path amendment: name/symbol APPEARED - name 'Timothy', symbol 'TIMOTHY', confirmed in TWO independent fast_rpc "
        "passes; totalSupply 1e27; decimals unverified (fast_rpc timeouts in both passes). DexScreener independently confirms TIMOTHY/WBNB, "
        "pair 0x066aa46ee270d041353749ee9ae485323bd6e6d1, liquidity $0.07 (drained after the rotation's sells), pair created 14:00:56 WIB. "
        "First buy 14:01:10 WIB by 0xcb08c02c0a, 0.000121241835355714 BNB -> 9,674.63 tokens. Wallet set byte-identical to e3a8 and diff 0 vs the "
        "run-90 machine set (27/27 overlap). Buy sizes WITHIN class norm (first ~0.000121, median follow-up ~0.22, max ~0.37) - NOT a size anomaly. "
        "96 sells in-window. Pair token0/token1 unreadable run 97 (fast_rpc 'all endpoints failed') - unverified, not absence. No website, no "
        "free-mint path. Auto-mint blocked at guard (c). Reported once as a paid-only signal run 97 (not a lead, not a buy recommendation); "
        "do not re-signal or re-report unless a new fact appears (e.g. a genuine free-mint path)."
    ),
})
s["machine_tokens"].append({
    "address": "0xe3a8e1ca392b316c42d780c3cf15202f80f37777",
    "first_seen": "run-97, 2026-11-07 13:43:12 WIB (tx 0x305ada6cd0b7b80c54a188f6b50346864d060129048706c93744908b3f6f3e5b, block 132154658)",
    "machine_wallets": 27,
    "typical_first_buy_bnb": 0.000121241835355714,
    "followup_buy_range_bnb": "median 0.223379, max 0.413838, total buys 9.9327 BNB (58 sent buys)",
    "label": "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - NAMED (symbol BTC) - ANOMALY, reported once as signal run 97",
    "note": (
        "ANOMALY under the fast-path amendment: name/symbol APPEARED - symbol 'BTC' confirmed 1x via fast_rpc, totalSupply 1e27, decimals 18; "
        "name() unreadable in both passes (fast_rpc timeouts) - NOT absent, retry opportunistically. DexScreener independently confirms BTC/WBNB, "
        "pair 0xa39db5002d7ee3dc4596243789702ff4fab993f4, liquidity $0.07 (drained after the rotation's sells), pair created 13:42:59 WIB. "
        "First buy 13:43:12 WIB by 0xcb08c02c0a, 0.000121241835355714 BNB -> 9,674.63 tokens. Wallet set byte-identical to c90a and diff 0 vs the "
        "run-90 machine set (27/27 overlap). Buy sizes WITHIN class norm (first ~0.000121, median follow-up ~0.22, max ~0.41) - NOT a size anomaly. "
        "100 sells in-window. Pair token0/token1 unreadable run 97 (fast_rpc 'all endpoints failed') - unverified, not absence. No website, no "
        "free-mint path. Auto-mint blocked at guard (c). Reported once as a paid-only signal run 97 (not a lead, not a buy recommendation); "
        "do not re-signal or re-report unless a new fact appears (e.g. a genuine free-mint path)."
    ),
})
print("machine_tokens now:", len(s["machine_tokens"]))

# Update the run-90 0x1153 entry in place (0 wallets run 97 - 7th quiet run, stalled at 26).
for mt in s.get("machine_tokens", []):
    if mt.get("address", "").lower() == "0x1153607e323c42f93c82b80e1772f9cc626b7777":
        mt["machine_wallets"] = 26
        mt["label"] = "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - rotation STALLED at 26 wallets (runs 91-97)"
        mt["note"] = mt.get("note", "") + (
            " RUN-97 UPDATE: 0 wallets this run - rotation STALLED at 26 wallets; 7th quiet run after debut. No buys and no sells from "
            "tracked wallets for this token in the run-97 window. Not treated as an anomaly under the fast-path amendment (no size deviation, "
            "name/symbol, website, or free-mint path appeared); watch run 98 for any resumption, do NOT treat a return as a new rotation."
        )
        print("1153 entry updated: stalled at 26, 0 wallets run 97 (7th quiet run)")
        break
# Update the run-88/89 0x79cd entry in place (0 wallets run 97 - 8th quiet run, stalled at 20).
for mt in s.get("machine_tokens", []):
    if mt.get("address", "").lower() == "0x79cd174ca3ec25c06ff5fddae365643f73d77777":
        mt["machine_wallets"] = 20
        mt["label"] = "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - rotation STALLED at 20 wallets (runs 90-97)"
        mt["note"] = mt.get("note", "") + (
            " RUN-97 UPDATE: 0 wallets this run - rotation STALLED at 20 wallets; 8th quiet run after debut (runs 88-89 active). No buys and "
            "no sells from tracked wallets for this token in the run-97 window. Not treated as an anomaly under the fast-path amendment; "
            "watch run 98 for any resumption, do NOT treat a return as a new rotation."
        )
        print("79cd entry updated: stalled at 20, 0 wallets run 97 (8th quiet run)")
        break

s.setdefault("signaled_projects_over_20pct", []).append(
    "Timothy (TIMOTHY) 0xc90a6cf8d74cf3540eaca3ce63ea7ae4e1ec7777 (paid-only, machine-token, run-97, NAMED - anomaly reported once as signal)"
)
s["signaled_projects_over_20pct"].append(
    "BTC (symbol BTC, name unverified) 0xe3a8e1ca392b316c42d780c3cf15202f80f37777 (paid-only, machine-token, run-97, NAMED - anomaly reported once as signal)"
)
print("signaled now:", len(s["signaled_projects_over_20pct"]))

s["paid_signal_run97"] = {
    "note": "ANOMALY SIGNAL (paid-only, NOT a buy recommendation, NOT a Free Bacot lead, NOT an auto-mint trigger). FIRST NAMED machine-token rotations: the machine set bought TWO tokens that HAVE on-chain name/symbol, breaking the unnamed pattern of all 24 prior machine tokens. Reported once per the fast-path amendment (name/symbol appeared). Auto-mint BLOCKED at guard (c) for both (paid PCS tokens, no free-mint path). Do not re-signal unless a new fact appears (e.g. a genuine free-mint path).",
    "tokens": [
        {"address": "0xc90a6cf8d74cf3540eaca3ce63ea7ae4e1ec7777", "name": "Timothy", "symbol": "TIMOTHY",
         "wallets": 27, "first_buy": "2026-11-07 14:01:10 WIB, 0.000121241835355714 BNB -> 9,674.63 tokens, wallet 0xcb08c02c0a, tx 0xa9bb2a67b61de46564bf3096ffd2fbd1ac5efc6e0bcb81981f6f5f0cbb900079, block 132157055",
         "pair": "0x066aa46ee270d041353749ee9ae485323bd6e6d1 (PCS V2; token0/token1 unreadable run 97, fast_rpc outage)",
         "buys": "53 sent buys, median follow-up 0.221423 BNB, max 0.371697 BNB, total 9.1951 BNB; 96 sells",
         "verification": "name+symbol confirmed 2x via fast_rpc; totalSupply 1e27; decimals unverified (timeouts); DexScreener TIMOTHY/WBNB, liq $0.07, pair created 14:00:56 WIB"},
        {"address": "0xe3a8e1ca392b316c42d780c3cf15202f80f37777", "name": "unverified (name() read failed, fast_rpc timeouts - NOT absent)", "symbol": "BTC",
         "wallets": 27, "first_buy": "2026-11-07 13:43:12 WIB, 0.000121241835355714 BNB -> 9,674.63 tokens, wallet 0xcb08c02c0a, tx 0x305ada6cd0b7b80c54a188f6b50346864d060129048706c93744908b3f6f3e5b, block 132154658",
         "pair": "0xa39db5002d7ee3dc4596243789702ff4fab993f4 (PCS V2; token0/token1 unreadable run 97, fast_rpc outage)",
         "buys": "58 sent buys, median follow-up 0.223379 BNB, max 0.413838 BNB, total 9.9327 BNB; 100 sells",
         "verification": "symbol BTC confirmed 1x via fast_rpc; totalSupply 1e27; decimals 18; DexScreener BTC/WBNB, liq $0.07, pair created 13:42:59 WIB"},
    ],
    "set_check": "Both 27-wallet sets byte-identical to each other and diff 0 vs the run-90 machine set (27/27 overlap). Buy sizes WITHIN class norm - NOT a size anomaly; the anomaly is name/symbol appearing.",
    "auto_mint": "BLOCKED at guard (c) for both: paid PCS tokens, no free-mint path for the user wallet; guard (a) website also unverified. No preview, no execution.",
}

s["paid_trend_run97"] = {
    "note": "Aggregate only, NOT a buy recommendation. TWO NEW machine-token rotations at 27 wallets each - BOTH NAMED (Timothy/TIMOTHY + symbol BTC), FIRST named rotations in the class: anomaly reported once as a paid-only signal (paid_signal_run97); buy sizes in class norm. All five run-90 rotations 0 wallets (7th quiet run after debut); 0x1153... STALLED at 26 wallets (7th quiet run); 0x79cd... STALLED at 20 wallets (8th quiet run). 25 deployments - first after 6 straight zero runs. Inbound run-97 window FULLY CLOSED in-run (1374/1374, 12,655 logs, 0 hits; 2 failed contracts retried same-run, 2/2 OK).",
    "rotations": "TWO NEW, both NAMED (anomaly): 0xc90a6cf8d74cf3540eaca3ce63ea7ae4e1ec7777 (Timothy/TIMOTHY, 27 wallets, first buy 14:01:10 WIB) + 0xe3a8e1ca392b316c42d780c3cf15202f80f37777 (symbol BTC, 27 wallets, first buy 13:43:12 WIB). Sets byte-identical, diff 0 vs run-90 machine set. All paid-only with no free-mint path; auto-mint blocked at guard (c); reported once as signal per fast-path amendment (name/symbol appeared).",
    "other_paid_activity": [
        {"pattern": "29 paid tokens: 2 at 27 wallets (new named rotations), 14 at 3 wallets (all the same churn trio 0x3803/0xad94/0xc7c5, all ...7777), 8 at 2, 5 at 1; 0 overlap with run-96's 32 tokens", "wallets": "see run97-paid.json"},
        {"pattern": "Micro round-trip churn continues: 160 PCS buys (0xb6f9de95) + 246 PCS sells (0x791ac947), 261 approvals (0x095ea7b3), 29 aggregator txs (0x39ecce49); top active 0xc7c5... 43 txs, 0xad94... 42, 0x3803... 42, 0x9cdd... 36, 0xa952... 34, 0xc621... 33", "wallets": "churn set"},
        {"pattern": "25 contract deployments by tracked wallets this run - first after 6 straight zero runs (91-96); all 13:59:08-13:59:47 WIB, 0x97bd895f alone 11", "wallets": "11 machine-set wallets"},
        {"pattern": "AFeng 1 sale-call 0x4d819a2a to 0x1de4... value 0, status 1, 13 logs, 0 mint logs - a SALE, NOT a mint (+ 1 approval to SLIME)", "wallets": "0xbf00... x1"},
        {"pattern": "2 failed txs this run (failed PCS sells by 0xc6219468 14:07:14 WIB and 0xa952331e 14:03:54 WIB, both in the c90a wave); all other 460 receipt candidates status 1", "wallets": "2 machine-set wallets"},
    ],
    "quiet": "AFeng 2 txs (1 sale-call + 1 approval); future1001.ai 0 txs; 0x2325... 2 txs (1 aggregator + 1 approval); 0x8e96... 0 txs; GrokBot 0xfcd0... absent (0 wallets) - 38th consecutive quiet run (59, 61-97) after the run-60 burst; CORLA-97af 0 wallets; CORLA 0x4a9c 0 wallets; all run-64/65 ASI contracts 0 wallets; run-90 tokens 0x6a25.../0x9f7e.../0x8c64.../0xc1ab.../0x1153... 0 wallets (7th quiet run after debut, down from 27/27/27/27/26); run-89 tokens 0xcfdb.../0x0cf8.../0xe68b.../0x31e4... 0 wallets (8th quiet run after debut); run-88 tokens 0x43c8.../0x3d12.../0xeae0... 0 wallets (9th quiet run after debut); run-87 tokens 0x889a.../0x4249... 0 wallets (10th quiet run after debut); run-86 tokens 0x2bfb.../0xc459... 0 wallets (11th quiet run after debut); run-85 token 0x2717... 0 wallets (12th quiet run); run-82 tokens 0xd468.../0xa6e6.../0x887c... all 0 wallets (15th quiet run after debut); run-81 tokens 0 wallets (16th quiet run); run-80 token 0 wallets (17th quiet run); 0x79cd... 0 wallets (rotation STALLED at 20, 8th quiet run after debut); all other run-66/68/69/70/71/72/73/74/75/76/77/78/79 machine tokens 0 wallets.",
}

s["inbound_log_leg_run97"] = {
    "contracts": 1374,
    "attempted": 1374,
    "completed_with_0_hits": 1374,
    "total_logs": 12655,
    "hits": 0,
    "failed": 0,
    "failed_contracts": [],
    "never_attempted": 0,
    "complete": True,
    "note": (
        "Ankr getLogs address-filtered per contract, window 132149917-132158490, from list run97-inbound-contracts.json (1374 contracts = "
        "run93 list 1347 + 25 run-97 deployments + 2 new rotation tokens). Full pass a (400, 7,598 logs, 0 failed) + b1 (200, 2,446 logs, 0 failed) + "
        "b2 (200, 542 logs, 0 failed) + b3 (574, 2,069 logs, 2 failed) = 12,655 logs, 0 hits, 2 FAILED initially (both transient Ankr "
        "'Remote end closed connection without response': 0xca8820d36bec22e462a45b6f658d3f7bb2542a82, 0xee8d9edfeecfc175a76387a25581c2dc9f5f85f5). "
        "Both failed contracts retried SAME-RUN (run97-inbound97-retry.py): 2/2 OK, 0 logs, 0 hits - window FULLY CLOSED in-run, no retry "
        "deferred to run 98. 8 truncated contracts, all topic-filtered to 0 logs (a: 0x10b389... (back this run), 0x1de4... AFeng sale, 0x3dca..., "
        "0x55d398... USDT, 0x6288..., 0x636fdfa9... tracker; b1: 0x63de... AGC, 0x7857...) - same set as runs 91-96 plus 0x10b3... returning. "
        "FIRST attempt of all four chunks WEDGED at ~contract 8-10 (log mtimes frozen 07:26-07:27 UTC, processes alive, sockets stuck in poll on "
        "the egress proxy for 5+ min while a fresh getLogs call worked in ~5s) - killed by PID and re-launched from scratch (idempotent read-only; "
        "the inbound scripts write JSON only at the end, so a wedged chunk loses nothing except time). Re-launched chunks stalled simultaneously "
        "at ~contract 50, ~100, ~150, ~250, ~300, ~350 and ~400 (log mtimes frozen several minutes, processes alive, 0 errors) and resumed on "
        "their own each time - shared Ankr slowdown, same pattern as runs 94-96. A frozen log mtime with a live process is a stall, not a death - "
        "wait before re-running; a socket wedged >5 min while fresh calls work is a wedge - kill by PID (pkill -f can match the wrapper shell, "
        "use kill <pid> or pkill with a pattern that excludes the shell) and re-run the chunk from scratch."
    ),
}

# --- next_run_note for run 98: surgical updates on the run-97 note ---
note = s["next_run_note"]
def rep(old, new, label):
    global note
    if old in note:
        note = note.replace(old, new)
        print(f"note[{label}]: replaced")
    else:
        print(f"note[{label}]: WARNING - target not found, left unchanged")

rep("Next run sent-tx window starts from block 132149917.",
    "Next run sent-tx window starts from block 132158491.", "window")
rep("14 consecutive runs - persistently unreadable, unverified not absence",
    "15 consecutive runs - persistently unreadable, unverified not absence", "pair15")
rep("(unreadable run 88, 89, 90, 91, 92, 93, 94, 95 AND 96 - retry opportunistically, not an anomaly)",
    "(unreadable run 88, 89, 90, 91, 92, 93, 94, 95, 96 AND 97 - retry opportunistically, not an anomaly)", "pair43c8")
rep("(token0/token1 unreadable run 89, 90, 91, 92, 93, 94, 95 AND 96; 0x31e4 pair 0x60ca0aef... READ OK run 89)",
    "(token0/token1 unreadable run 89, 90, 91, 92, 93, 94, 95, 96 AND 97; 0x31e4 pair 0x60ca0aef... READ OK run 89)", "pair89")
rep("NOTE: fast_rpc worked for the receipts batch in run 96 (134/134)",
    "NOTE: fast_rpc worked for the receipts batch in run 97 (462/462)", "fast_rpc_note")
rep("(2) RETRY run 97 inbound: NONE - run-96 inbound closed fully in-run (1347/1347, 11,473 logs, 0 hits; 6 failed contracts retried same-run, "
    "6/6 OK, 0 logs, 0 hits). No inbound retry carried into run 97. ",
    "(2) RETRY run 98 inbound: NONE - run-97 inbound closed fully in-run (1374/1374, 12,655 logs, 0 hits; 2 failed contracts retried same-run, "
    "2/2 OK, 0 logs, 0 hits). No inbound retry carried into run 98. ", "retry98")
rep("(3) Run-96 inbound list for run 97 = run93 list (1347) unless run 97's own sent pass finds new deployments to add.",
    "(3) Run-97 inbound list for run 98 = run97 list (1374 = run93 list + 25 run-97 deployments + 2 new rotation tokens) unless run 98's own "
    "sent pass finds new deployments to add.", "inbound_list")
rep("(4) Run-96 window inbound FULLY CLOSED in-run (1347/1347, 11,473 logs, 0 hits; 6 failed contracts retried same-run, 6/6 OK, 0 logs, 0 hits). "
    "Run-95 window FULLY CLOSED on first attempt (1347/1347, 11,364 logs, 0 hits, 0 failed).",
    "(4) Run-97 window inbound FULLY CLOSED in-run (1374/1374, 12,655 logs, 0 hits; 2 failed contracts retried same-run, 2/2 OK, 0 logs, 0 hits). "
    "Run-96 window inbound FULLY CLOSED in-run (1347/1347, 11,473 logs, 0 hits; 6 failed contracts retried same-run, 6/6 OK, 0 logs, 0 hits).",
    "window_status")
rep("(5) 0x1153607e... rotation STALLED at 26 wallets (did NOT reach 27 as expected; 0 wallets runs 91-96, 6th quiet run after debut) - watch run 97 "
    "for any resumption; do NOT treat a return as a new rotation. 0x79cd... STALLED at 20 wallets (0 wallets runs 90-96, 7th quiet run) - same.",
    "(5) 0x1153607e... rotation STALLED at 26 wallets (did NOT reach 27 as expected; 0 wallets runs 91-97, 7th quiet run after debut) - watch run 98 "
    "for any resumption; do NOT treat a return as a new rotation. 0x79cd... STALLED at 20 wallets (0 wallets runs 90-97, 8th quiet run) - same.",
    "stalls")
rep("run 96 (ZERO new rotations; all five run-90 tokens 0 wallets, 6th quiet run after debut; 0x1153... STALLED at 26, 6th quiet run; "
    "0x79cd... STALLED at 20, 7th quiet run; inbound FULLY CLOSED in-run after 6-contract same-run retry; chunks a/b3 died silently first "
    "attempt ~contract 200, re-run from scratch) ",
    "run 96 (ZERO new rotations; all five run-90 tokens 0 wallets, 6th quiet run after debut; 0x1153... STALLED at 26, 6th quiet run; "
    "0x79cd... STALLED at 20, 7th quiet run; inbound FULLY CLOSED in-run after 6-contract same-run retry; chunks a/b3 died silently first "
    "attempt ~contract 200, re-run from scratch) "
    "run 97 (TWO NEW rotations 0xc90a... Timothy/TIMOTHY + 0xe3a8... symbol BTC at 27 wallets each - FIRST NAMED machine-token rotations, "
    "anomaly reported once as signal run 97; buy sizes in class norm; 0x1153... STALLED at 26, 7th quiet run; 0x79cd... STALLED at 20, 8th quiet "
    "run; 25 deployments (first in 7 runs); inbound FULLY CLOSED in-run, 1374 contracts, 12,655 logs, 0 hits, 2 failed retried same-run 2/2 OK; "
    "first-attempt chunks WEDGED on proxy sockets ~contract 10, killed by PID + re-launched from scratch) ", "history97")
rep("Paid fact: run96 ZERO new rotations; run-90 tokens 0x6a25.../0x9f7e.../0x8c64.../0xc1ab.../0x1153... 0 wallets (6th quiet run after debut); run-89 tokens 0xcfdb.../0x0cf8.../0xe68b.../0x31e4... 0 wallets (7th quiet run after debut); run-88 tokens 0x43c8.../0x3d12.../0xeae0... 0 wallets (8th quiet run after debut); run-87 tokens 0x889a.../0x4249... 0 wallets (9th quiet run after debut); run-86 tokens "
    "0x2bfb.../0xc459... 0 wallets (10th quiet run after debut); run-85 token 0x2717... 0 wallets (11th quiet run); run-82 tokens 0xd468.../0xa6e6.../0x887c... "
    "all 0 wallets (14th quiet run after debut); run-81 tokens 0 wallets (15th quiet run); run-80 token 0 wallets (16th quiet run); "
    "GrokBot 0xfcd0... absent (0 wallets) - 37th consecutive quiet run (59, 61-96) after the run-60 burst;",
    "Paid fact: run97 TWO NEW rotations 0xc90a... (Timothy/TIMOTHY) + 0xe3a8... (symbol BTC) at 27 wallets each - FIRST NAMED machine-token rotations "
    "(anomaly: name/symbol appeared; reported once as signal run 97, paid-only, auto-mint blocked guard (c)); run-90 tokens 0x6a25.../0x9f7e.../0x8c64.../0xc1ab.../0x1153... 0 wallets (7th quiet run after debut); run-89 tokens 0xcfdb.../0x0cf8.../0xe68b.../0x31e4... 0 wallets (8th quiet run after debut); run-88 tokens 0x43c8.../0x3d12.../0xeae0... 0 wallets (9th quiet run after debut); run-87 tokens 0x889a.../0x4249... 0 wallets (10th quiet run after debut); run-86 tokens "
    "0x2bfb.../0xc459... 0 wallets (11th quiet run after debut); run-85 token 0x2717... 0 wallets (12th quiet run); run-82 tokens 0xd468.../0xa6e6.../0x887c... "
    "all 0 wallets (15th quiet run after debut); run-81 tokens 0 wallets (16th quiet run); run-80 token 0 wallets (17th quiet run); "
    "GrokBot 0xfcd0... absent (0 wallets) - 38th consecutive quiet run (59, 61-97) after the run-60 burst;", "paid_fact")
rep("Run 96 had 0 deployments (6th straight zero; runs 91, 92, 93, 94, 95, 96).",
    "Run 97 had 25 deployments (first deployments after 6 straight zero runs 91-96; all 13:59:08-13:59:47 WIB by 11 machine-set wallets, "
    "0x97bd895f alone 11; added to the inbound list for run 98).", "deployments")
rep("AFeng 17 txs (9 sale-calls 0x4d819a2a to 0x1de4... totaling 1.125 BNB + 8 approvals, all status 1, 0 mint logs - sales, NOT mints); future1001.ai 0 txs; 0x2325... 0 txs; 0x8e96... 0 txs; 0x3803... 44 txs (29 aggregator 0x39ecce49 + 15 approvals, churn as usual).",
    "AFeng 2 txs (1 sale-call 0x4d819a2a to 0x1de4... value 0, status 1, 13 logs, 0 mint logs - a sale, NOT a mint + 1 approval to SLIME 0x8351311f...); future1001.ai 0 txs; 0x2325... 2 txs (1 aggregator 0x27772d13 + 1 approval, value 0); 0x8e96... 0 txs; 0x3803... 42 txs (28 aggregator 0x39ecce49 + 14 approvals, total value 0.000364 BNB, churn as usual).", "activity")
rep("PROCESS LESSON (run 86): the receipts pass died silently at 420/461 (service-restart pattern, same as runs 82/84) - the partial-file resume worked; "
    "always re-run the same script to resume rather than re-fetching from scratch. Run 96 receipts completed in one attempt, no resume needed; "
    "inbound chunks a and b3 DIED SILENTLY on FIRST attempt at ~contract 200-205 (a log frozen 06:29:27 UTC at [205], b3 log frozen 06:28:59 UTC at "
    "[200], no JSON, no EXIT - service-restart pattern, same as run 94) - both re-run from scratch (a2/b3-2, idempotent read-only) and completed "
    "clean; b1/b2 finished first attempt. All four chunks stalled simultaneously at ~contract 50, ~150, ~250 and ~350 (log mtimes frozen several "
    "minutes, processes alive, 0 errors) and resumed on their own each time - shared Ankr slowdown; plus a simultaneous Ankr blip at ~contract "
    "146-148 in all four chunks (6 failed total, retried SAME-RUN 6/6 OK, 0 logs, 0 hits - window fully closed in-run, no deferral to run 97). "
    "A frozen log mtime with a live process is a stall, not a death - wait before re-running; a log frozen >5 min with NO live process is a "
    "silent death - re-run the chunk from scratch.",
    "PROCESS LESSON (run 86): the receipts pass died silently at 420/461 (service-restart pattern, same as runs 82/84) - the partial-file resume worked; "
    "always re-run the same script to resume rather than re-fetching from scratch. Run 97 receipts completed in one attempt, no resume needed; "
    "inbound chunks ALL FOUR WEDGED on FIRST attempt at ~contract 8-10 (log mtimes frozen 07:26-07:27 UTC, processes alive, sockets stuck in poll "
    "on the egress proxy for 5+ min while a fresh getLogs call worked in ~5s - a wedged socket, NOT a silent death) - killed by PID and re-launched "
    "from scratch (idempotent read-only; the inbound scripts write JSON only at the end, so a wedged chunk loses nothing but time). Re-launched "
    "chunks stalled simultaneously at ~contract 50, ~100, ~150, ~250, ~300, ~350 and ~400 (log mtimes frozen several minutes, processes alive, "
    "0 errors) and resumed on their own each time - shared Ankr slowdown; 2 failed contracts (transient Ankr 'Remote end closed connection') "
    "retried SAME-RUN 2/2 OK, 0 logs, 0 hits - window fully closed in-run, no deferral to run 98. "
    "A frozen log mtime with a live process is a stall, not a death - wait before re-running; a log frozen >5 min with NO live process is a "
    "silent death - re-run the chunk from scratch; a socket wedged >5 min while fresh calls work is a wedge - kill by PID (pkill -f can match "
    "the wrapper shell itself, use kill <pid>) and re-run the chunk from scratch.",
    "process_lesson")
rep("(all five pairs' token0/token1 READ OK in run-90 token-verify via fast_rpc race - do NOT re-read unless a new question arises; the retry list above is for the pairs that are still unreadable).",
    "(all five pairs' token0/token1 READ OK in run-90 token-verify via fast_rpc race - do NOT re-read unless a new question arises; the retry list above is for the pairs that are still unreadable). "
    "PLUS new run-97 rotation pairs 0xc90a 0x066aa46ee270d041353749ee9ae485323bd6e6d1, 0xe3a8 0xa39db5002d7ee3dc4596243789702ff4fab993f4 (token0/token1 unreadable "
    "run 97, fast_rpc 'all endpoints failed' - unverified, not absence; pair addresses known from first-buy logs; retry opportunistically run 98).",
    "pairs97")
s["next_run_note"] = note

json.dump(s, open(P, "w"), indent=1)
print("state updated; last_run now:", s["last_run"]["run"], "block_end:", s["last_run"]["block_end"])
print("machine_tokens:", len(s.get("machine_tokens", [])), "| signaled:", len(s.get("signaled_projects_over_20pct", [])))
print("inbound97 complete:", s["inbound_log_leg_run97"]["complete"], "| failed:", s["inbound_log_leg_run97"]["failed"])
print("inbound96 complete:", s["inbound_log_leg_run96"]["complete"], "| failed:", s["inbound_log_leg_run96"]["failed"])
