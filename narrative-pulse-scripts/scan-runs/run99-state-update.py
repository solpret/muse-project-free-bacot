#!/usr/bin/env python3
"""Run 99 state update (read-only job bookkeeping; no chain writes).

Completes run 99 (window 132168468-132179368, tx 2026-11-07 15:26:48 - 16:48:33 WIB).
Sent/receipts/paid done and verified; inbound leg run-99 window FULLY CLOSED in-run
(1517/1517, 14,436 logs, 0 hits, 0 failed - after a/b3 re-runs from scratch).
NO new mints. FOUR NEW machine-token rotations at 27 wallets each - ALL NAMED
(goonerpad / 癫猫 / Gay Executive Officers / 首个开演唱会的猫), the THIRD
consecutive run with named rotations (run 97 had 2, run 98 had 4): anomaly under the
fast-path amendment, reported ONCE as a paid-only signal (not a lead, not a buy
recommendation, auto-mint blocked at guard (c)). 64 deployments this run
(third straight run with deployments; 25/72/64). Bridge unchanged
(0 new mints, 0 not_evaluated).
"""
import json, shutil

P = "/home/hatch/workspace/narrative-pulse/tracked-wallet-mint-scan-state.json"
shutil.copy(P, str(P) + ".bak-run99-pre")
s = json.load(open(P))

last_run_99 = {
    "run": 99,
    "block_start": 132168468,
    "block_end": 132179368,
    "window_wib": "2026-11-07 15:26:48 - 16:48:33 WIB (tx times); run executed ~16:05 - ~18:24 WIB; sent-pass in-window txs 1239, 0 mint-pattern txs",
    "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set); 0 failed, no retry needed.",
    "method_note": (
        "Sent pass Ankr ankr_getTransactionsByAddress via module: FIRST attempt completed 55/55 OK, 1239 txs, 34 wallets active, 0 failed. "
        "Receipts via fast_rpc batch (6, ~4s pause) for 800 non-approve candidates: 791 status 1, 6 status 0 (all failed PCS sells 0x791ac947), "
        "3 null, 0 mint logs. Two batch 429s (batch 348, batch 690) handled by race fallback; one race error (tx 0x4c704bcb64..., PCS sell) -> null receipt. "
        "Receipts completed in one attempt, no resume needed. "
        "Paid: 38 tokens; max 27 wallets/token (FOUR new rotations at 27 each - see anomaly signal; 17 tokens at 3 wallets, all the same churn trio "
        "0x3803/0xad94/0xc7c5, all ...7777; 8 at 2, 9 at 1; 0 overlap with run-98's 38 paid tokens - the ...7777 churn set turns over every run). "
        "NEW ROTATIONS - ANOMALY (named tokens, third consecutive run - run 97 had 2 named, run 98 had 4, run 99 has 4): "
        "0x50e4506e76e816ed5e74557b4b8a57037d927777 (首个开演唱会的猫 / 悟空), "
        "0x6b12a49f7a6aa9061278cdc4efd4f417e5a77777 (Gay Executive Officers / GEO), "
        "0xff6624b5c407780ddd84ed6fd65cc38ec6547777 (癫猫 / 癫猫), "
        "0xdb4950e7c92cf433d971775ea57d2ea7c6757777 (goonerpad / gooner). "
        "All four: name+symbol confirmed via fast_rpc (db49 pass 2 only - pass 1 timeout; ff66/6b12 TWO passes; 50e4 pass 1 - pass 2 timeout on name/symbol "
        "but totalSupply 1e27 + decimals 18 confirmed pass 2), totalSupply 1e27, decimals 18. DexScreener independently confirms all four "
        "(same names/symbols, pairs match the on-chain log-derived pair addresses, liquidity $0.07 each - drained after the rotation's sells). "
        "All four bought by the SAME 27-wallet machine set, byte-identical to each other and diff 0 vs the run-98 machine set (27/27 overlap). "
        "Buy sizes WITHIN class norm (NOT a size anomaly): first buy 0.000121125 BNB -> ~9,640-9,674 tokens each (50e4 9,674.63; 6b12 9,665.31; "
        "ff66 9,674.63; db49 9,640.67); follow-up medians 0.223378725 for ALL FOUR; max 0.270613-0.426751; totals 8.3518-9.7212 BNB; buys 50-58, "
        "sells 64-100 per token (db49 64 sells/23 wallets - rotation still filling at window end). First buys: 50e4 15:36:10 WIB by 0xcb08c02c0a "
        "tx 0x2965f3e1a38fd10c6d5f97094902310c5653072cc3efbeb1e54e6a6614e2038c block 132169717 pair 0x26b53042e668d52056e4449abcd238cf01e3a155; "
        "6b12 15:58:50 WIB by 0x362396125a (NOT the usual first buyer 0xcb08c02c0a) tx 0x985a661af2f0d2e7a66f2e5597becca629b27bcde0bcf821b55e94e7f67ae2f5 "
        "block 132172740 pair 0x43d85c9fa81bc019701431460d1b3459b057af6d; ff66 16:19:28 WIB by 0xcb08c02c0a tx "
        "0x48032425b12968685459fd9867de5f29b424640444b587104eb63dbffa7251b4 block 132175491 pair 0x2d3e053bada0378299010fde9f59209985760bab; "
        "db49 16:40:43 WIB by 0xcb08c02c0a tx 0xc15b4e57f864affae10007a201032e319ec56a0dce126dc7b0f7631b5e332f87 block 132178323 pair "
        "0x41cbb4910fd4959f651d7bff8d8b5ed5cd355dfc. Pair token0/token1: 50e4 READ OK (token0 = token, token1 = WBNB); db49 token1 = token READ OK, "
        "token0 unreadable; ff66 token1 = token READ OK, token0 unreadable; 6b12 token0 = token READ OK, token1 unreadable (fast_rpc outage, "
        "time-varying) - unverified, not absence; retry run 100. Trigger >25% met numerically (27 >= 14) but AUTO-MINT BLOCKED at guard (c): "
        "paid PCS tokens, no free-mint path; guard (a) website also unverified. No preview, no execution. "
        "Deployments: 64 contract creations by 14 machine-set wallets (0x3154f694 7; 0xaa49e7fe/0x1cce4ec5/0xc0c84518/0x9b519f5d/0x64e893a4 6 each; "
        "0xf795c525/0xcb08c02c 5 each; 0x3a39aa05/0x5b4beded 4 each; 0xc6219468 2; 0xa952331e/0xfdec62fd 1 each) - THIRD straight run with deployments "
        "(25 run 97, 72 run 98, 64 run 99); 63 deployed addresses recovered from receipts, added to the inbound list (run99-inbound-contracts.json, "
        "total 1517); ONE creation has a NULL receipt (tx 0x21c210dfea7439ddd710e9c758191c4ad5c0be98e449097c6a338b50dc09c3d3 by 0x3154f694, "
        "15:51:47 WIB, value ~0.1054 BNB) so its deployed address is UNVERIFIED - retry run 100. The 4 rotation tokens are NOT among the deployments. "
        "AFeng 0 txs; future1001.ai 0 txs; 0x2325... 20 txs (13 aggregator 0x27772d13 + 7 approvals, total value 0.52 BNB); 0x8e96... 0 txs; "
        "0x3803... 53 txs (35 aggregator 0x39ecce49 + 18 approvals, total value 0.000468 BNB, churn as usual). 0 plain BNB transfers. "
        "Selectors (sent pass, 1239 txs): 415 PCS sells (0x791ac947) + 272 PCS buys (0xb6f9de95) + 64 contract creations (0x60806040) + 36 aggregator "
        "(0x39ecce49) + 13 aggregator (0x27772d13) + 439 approvals (not in receipt candidates). Nonzero-value txs 360, total 39.4096 BNB, "
        "max 0.4268 BNB (6b12 follow-up buy). Most active wallets: 0xa952331e 71 txs, 0x9cdd08f3 69, 0xc6219468 55, 0x3803... 53, 0xc7c5... 52, "
        "0xad94... 51, 0xf795c525 51, 0xe9ed24db 49, 0x1cce4ec5 48, 0x92bc3297 46, 0xc0c84518 44, 0x9b519f5d 44. "
        "3 NULL receipts (unverified, not absence): 0x21c210df... (creation, see above), 0x2a1a2635... (PCS sell by 0x3154f694, 15:45:02 WIB), "
        "0x4c704bcb64... (PCS sell by 0x92bc3297, 16:21:59 WIB). 6 status-0 txs, all failed PCS sells by machine wallets "
        "(0xdb2d83f9 16:41:17, 0xc6219468 16:42:21 + 16:21:11, 0xa952331e 15:38:55, 0x9b519f5d 16:42:05, 0xfdec62fd 16:20:22 WIB). "
        "Inbound leg (amendment 12:02 WIB): Ankr getLogs address-filtered per contract, 1517 contracts (run98 list 1450 + 63 run-99 deployments + "
        "4 new rotation tokens), 0 hits, 14,436 logs, window 132168468-132179368. Chunk a (400, 7,496 logs, 0 failed, 5 truncated) + b1 (200, 2,727 logs, "
        "0 failed, 2 truncated) + b2 (200, 777 logs, 0 failed) + b3 (717, 3,436 logs, 0 failed) = 14,436 logs, 0 hits, 0 FAILED. "
        "7 truncated contracts, all topic-filtered to 0 logs (a: 0x1de4... AFeng sale, 0x3dca..., 0x55d398... USDT, 0x6288..., 0x636fdfa9... tracker; "
        "b1: 0x63de... AGC, 0x7857...) - same set as runs 91-98. FIRST attempts of chunks a and b3 DIED SILENTLY at ~contract 350/341 "
        "(service restart ~10:35 UTC, no JSON, no EXIT - same pattern as runs 94/96/97); both re-run from scratch (a2/b3-2, read-only, idempotent) "
        "and completed clean; b3's first-attempt failed contract 0x2e6ff381... (Ankr 'Remote end closed connection') re-covered in the re-run. "
        "Pair a6e6/887c/2bfb/c459/43c8/cfdb/0cf8/e68b STILL unreadable: token0()/token1() for all eight pairs failed via fast_rpc race "
        "('all endpoints failed') in run99-pair-retry.py - unverified, not absence; 17th consecutive run for a6e6/887c/2bfb/c459, 12th for 43c8, "
        "10th for cfdb/0cf8/e68b; retry run 100. BUT the 41cc pair READ OK this run (token0 = the token 0x41cc..., token1 = WBNB) - REMOVED from the "
        "retry list; new run-99 pair 50e4 also READ OK (token0 = token, token1 = WBNB); db49/ff66 token1 = token and 6b12 token0 = token READ OK, "
        "other side unreadable - retry run 100. "
        "Pointer-discovery (amendment 19:10): 0 contracts processed - no new mints this run, and the backfill queue is empty (bridge 115 contracts, "
        "0 not_evaluated); bridge unchanged. CHAT REPORT this run: the four-named-machine-token anomaly signal (paid-only, NOT a lead, NOT a buy "
        "recommendation, auto-mint blocked guard (c)) - reported once per the fast-path amendment. No new mints, no Free Bacot signal beyond that, "
        "no auto-mint trigger execution. No preview/mint/sign/login/purchase by this job."
    ),
}
s["last_run"] = last_run_99

# ---- paid signal + trend ----
s["paid_signal_run99"] = {
    "note": "ANOMALY SIGNAL (paid-only, NOT a buy recommendation, NOT a Free Bacot lead, NOT an auto-mint trigger). THIRD consecutive run with NAMED "
            "machine-token rotations - and now FOUR at once again (run 97 had 2, run 98 had 4, run 99 has 4): the machine set bought FOUR tokens "
            "that HAVE on-chain name/symbol, breaking the unnamed pattern of all 24 pre-run-97 machine tokens. Reported once per the fast-path "
            "amendment (name/symbol appeared). Auto-mint BLOCKED at guard (c) for all four (paid PCS tokens, no free-mint path). Do not re-signal "
            "unless a new fact appears (e.g. a genuine free-mint path).",
    "tokens": [
        {
            "address": "0x50e4506e76e816ed5e74557b4b8a57037d927777",
            "name": "首个开演唱会的猫",
            "symbol": "悟空",
            "wallets": 27,
            "first_buy": "2026-11-07 15:36:10 WIB, 0.000121125 BNB -> 9,674.63 tokens, wallet 0xcb08c02c0a, tx 0x2965f3e1a38fd10c6d5f97094902310c5653072cc3efbeb1e54e6a6614e2038c, block 132169717",
            "pair": "0x26b53042e668d52056e4449abcd238cf01e3a155 (PCS V2; token0/token1 READ OK: token0 = token, token1 = WBNB)",
            "buys": "55 sent buys, median follow-up 0.223378725 BNB, max 0.376777 BNB, total 9.4422 BNB; 98 sells",
            "verification": "name+symbol confirmed in pass 1 via fast_rpc (pass 2 timed out on name/symbol; totalSupply 1e27 + decimals 18 confirmed pass 2); DexScreener 首个开演唱会的猫/悟空, liq $0.07, pair created ~15:36 WIB",
        },
        {
            "address": "0x6b12a49f7a6aa9061278cdc4efd4f417e5a77777",
            "name": "Gay Executive Officers",
            "symbol": "GEO",
            "wallets": 27,
            "first_buy": "2026-11-07 15:58:50 WIB, 0.000121125 BNB -> 9,665.31 tokens, wallet 0x362396125a (NOT the usual first buyer 0xcb08c02c0a), tx 0x985a661af2f0d2e7a66f2e5597becca629b27bcde0bcf821b55e94e7f67ae2f5, block 132172740",
            "pair": "0x43d85c9fa81bc019701431460d1b3459b057af6d (PCS V2; token0 = token READ OK, token1 unreadable run 99, fast_rpc outage)",
            "buys": "58 sent buys, median follow-up 0.223378725 BNB, max 0.426751 BNB, total 9.7212 BNB; 100 sells",
            "verification": "name+symbol confirmed 2x via fast_rpc; totalSupply 1e27; decimals 18; DexScreener Gay Executive Officers/GEO, liq $0.07, pair created ~15:58 WIB",
        },
        {
            "address": "0xff6624b5c407780ddd84ed6fd65cc38ec6547777",
            "name": "癫猫",
            "symbol": "癫猫",
            "wallets": 27,
            "first_buy": "2026-11-07 16:19:28 WIB, 0.000121125 BNB -> 9,674.63 tokens, wallet 0xcb08c02c0a, tx 0x48032425b12968685459fd9867de5f29b424640444b587104eb63dbffa7251b4, block 132175491",
            "pair": "0x2d3e053bada0378299010fde9f59209985760bab (PCS V2; token1 = token READ OK, token0 unreadable run 99, fast_rpc outage)",
            "buys": "55 sent buys, median follow-up 0.223378725 BNB, max 0.383807 BNB, total 9.2643 BNB; 92 sells",
            "verification": "name+symbol confirmed 2x via fast_rpc; totalSupply 1e27; decimals 18; DexScreener 癫猫/癫猫, liq $0.07, pair created ~16:19 WIB",
        },
        {
            "address": "0xdb4950e7c92cf433d971775ea57d2ea7c6757777",
            "name": "goonerpad",
            "symbol": "gooner",
            "wallets": 27,
            "first_buy": "2026-11-07 16:40:43 WIB, 0.000121125 BNB -> 9,640.67 tokens, wallet 0xcb08c02c0a, tx 0xc15b4e57f864affae10007a201032e319ec56a0dce126dc7b0f7631b5e332f87, block 132178323",
            "pair": "0x41cbb4910fd4959f651d7bff8d8b5ed5cd355dfc (PCS V2; token1 = token READ OK, token0 unreadable run 99, fast_rpc outage)",
            "buys": "50 sent buys, median follow-up 0.223378725 BNB, max 0.270613 BNB, total 8.3518 BNB; 64 sells / 23 wallets (rotation still filling at window end)",
            "verification": "name+symbol confirmed in pass 2 via fast_rpc (pass 1 timed out); totalSupply 1e27; decimals 18; DexScreener goonerpad/gooner, liq $0.07, pair created ~16:40 WIB",
        },
    ],
}

s["paid_trend_run99"] = {
    "note": "Aggregate only, NOT a buy recommendation. FOUR NEW machine-token rotations at 27 wallets each - ALL NAMED (首个开演唱会的猫/悟空, "
            "Gay Executive Officers/GEO, 癫猫/癫猫, goonerpad/gooner), THIRD consecutive run with named rotations (run 97 had 2, run 98 had 4): "
            "anomaly reported once as a paid-only signal (paid_signal_run99); buy sizes in class norm. Run-98 named rotations 41cc/43bc/2120/da79 "
            "0 wallets (2nd quiet run after debut); run-97 named rotations c90a/e3a8 0 wallets (2nd quiet run after debut); all five run-90 rotations "
            "0 wallets (9th quiet run after debut); 0x1153... STALLED at 26 wallets (9th quiet run); 0x79cd... STALLED at 20 wallets (10th quiet run). "
            "64 deployments - third straight run with deployments. Inbound run-99 window FULLY CLOSED in-run after a/b3 re-runs (1517/1517, 14,436 logs, "
            "0 hits, 0 failed).",
    "rotations": "FOUR NEW, all NAMED (anomaly): 0x50e4506e76e816ed5e74557b4b8a57037d927777 (首个开演唱会的猫/悟空, 27 wallets, first buy 15:36:10 WIB) + "
                 "0x6b12a49f7a6aa9061278cdc4efd4f417e5a77777 (Gay Executive Officers/GEO, 27 wallets, first buy 15:58:50 WIB) + "
                 "0xff6624b5c407780ddd84ed6fd65cc38ec6547777 (癫猫/癫猫, 27 wallets, first buy 16:19:28 WIB) + "
                 "0xdb4950e7c92cf433d971775ea57d2ea7c6757777 (goonerpad/gooner, 27 wallets, first buy 16:40:43 WIB). Sets byte-identical, diff 0 vs "
                 "run-98 machine set. All paid-only with no free-mint path; auto-mint blocked at guard (c); reported once as signal per fast-path "
                 "amendment (name/symbol appeared).",
    "other_paid_activity": [
        {
            "pattern": "17 tokens x 3 wallets, all the same churn trio 0x3803/0xad94/0xc7c5, all ...7777 (PCS micro buy-then-sell, ~0.00003 BNB per buy)",
            "wallet": "churn trio (see paid_trend_run1 for the pattern)",
        },
        {
            "pattern": "13 txs via 0x296b00198dc7ec3410e12da814d9267bb8df506a (selector 0x27772d13), receiving tokens from pair contracts (swap-like, not mints); total value 0.52 BNB",
            "wallet": "0x2325f175975abdbcde555c79cc8e63381d28551b",
        },
        {
            "pattern": "35 txs via aggregator 0x855066c8679c77a0258e792b5ccf19f8c227eb31 (selector 0x39ecce49) + 18 approvals, total value 0.000468 BNB (churn as usual)",
            "wallet": "0x38031ca8a54526f9fe90f11f07b55ae5fc01036a",
        },
    ],
}

s["inbound_log_leg_run99"] = {
    "contracts": 1517,
    "attempted": 1517,
    "completed_with_0_hits": 1517,
    "total_logs": 14436,
    "hits": 0,
    "failed": 0,
    "failed_contracts": [],
    "never_attempted": 0,
    "complete": True,
    "note": "Ankr getLogs address-filtered per contract, window 132168468-132179368, from list run99-inbound-contracts.json (1517 contracts = run98 list "
            "1450 + 63 run-99 deployments + 4 new rotation tokens). Full pass a (400, 7,496 logs, 0 failed) + b1 (200, 2,727 logs, 0 failed) + b2 "
            "(200, 777 logs, 0 failed) + b3 (717, 3,436 logs, 0 failed) = 14,436 logs, 0 hits, 0 FAILED. 7 truncated contracts, all topic-filtered to "
            "0 logs (a: 0x1de4... AFeng sale, 0x3dca..., 0x55d398... USDT, 0x6288..., 0x636fdfa9... tracker; b1: 0x63de... AGC, 0x7857...) - same set as "
            "runs 91-98. FIRST attempts of chunks a and b3 DIED SILENTLY at ~contract 350/341 (service restart ~10:35 UTC, no JSON, no EXIT); both "
            "re-run from scratch (a2/b3-2) and completed clean; b3's first-attempt failed contract 0x2e6ff381... (Ankr 'Remote end closed connection') "
            "re-covered in the re-run. Window FULLY CLOSED in-run, no retry deferred to run 100.",
}

# ---- machine tokens: 4 new entries ----
new_entries = [
    {
        "address": "0x50e4506e76e816ed5e74557b4b8a57037d927777",
        "first_seen": "run-99, 2026-11-07 15:36:10 WIB (tx 0x2965f3e1a38fd10c6d5f97094902310c5653072cc3efbeb1e54e6a6614e2038c, block 132169717)",
        "machine_wallets": 27,
        "typical_first_buy_bnb": 0.000121125,
        "followup_buy_range_bnb": "median 0.223378725, max 0.376777, total buys 9.4422 BNB (55 sent buys)",
        "label": "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - NAMED (首个开演唱会的猫 / 悟空) - ANOMALY, reported once as signal run 99",
        "note": "ANOMALY under the fast-path amendment: name/symbol APPEARED - name '首个开演唱会的猫', symbol '悟空', confirmed in pass 1 via fast_rpc "
                "(pass 2 timed out on name/symbol; totalSupply 1e27 + decimals 18 confirmed pass 2). DexScreener independently confirms "
                "首个开演唱会的猫/悟空, pair 0x26b53042e668d52056e4449abcd238cf01e3a155, liquidity $0.07 (drained after the rotation's sells), pair created "
                "~15:36 WIB. First buy 15:36:10 WIB by 0xcb08c02c0a, 0.000121125 BNB -> 9,674.63 tokens. Wallet set byte-identical to the other three "
                "run-99 rotations and diff 0 vs the run-98 machine set (27/27 overlap). Buy sizes WITHIN class norm - NOT a size anomaly. 98 sells "
                "in-window. Pair token0/token1 READ OK run 99: token0 = the token, token1 = WBNB 0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c. "
                "Auto-mint BLOCKED at guard (c) - paid PCS token, no free-mint path. Do not re-signal unless a new fact appears.",
    },
    {
        "address": "0x6b12a49f7a6aa9061278cdc4efd4f417e5a77777",
        "first_seen": "run-99, 2026-11-07 15:58:50 WIB (tx 0x985a661af2f0d2e7a66f2e5597becca629b27bcde0bcf821b55e94e7f67ae2f5, block 132172740)",
        "machine_wallets": 27,
        "typical_first_buy_bnb": 0.000121125,
        "followup_buy_range_bnb": "median 0.223378725, max 0.426751, total buys 9.7212 BNB (58 sent buys)",
        "label": "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - NAMED (Gay Executive Officers / GEO) - ANOMALY, reported once as signal run 99",
        "note": "ANOMALY under the fast-path amendment: name/symbol APPEARED - name 'Gay Executive Officers', symbol 'GEO', confirmed in TWO independent "
                "fast_rpc passes; totalSupply 1e27; decimals 18. DexScreener independently confirms Gay Executive Officers/GEO, pair "
                "0x43d85c9fa81bc019701431460d1b3459b057af6d, liquidity $0.07 (drained after the rotation's sells), pair created ~15:58 WIB. First buy "
                "15:58:50 WIB by 0x362396125a (NOT the usual first buyer 0xcb08c02c0a - the second run-99 rotation whose first buy came from another "
                "machine-set wallet), 0.000121125 BNB -> 9,665.31 tokens. Wallet set byte-identical to the other three run-99 rotations and diff 0 vs "
                "the run-98 machine set (27/27 overlap). Buy sizes WITHIN class norm - NOT a size anomaly. 100 sells in-window. Pair token0/token1 "
                "PARTIAL run 99: token0 = the token READ OK, token1 unreadable (fast_rpc outage) - retry run 100. Auto-mint BLOCKED at guard (c) - "
                "paid PCS token, no free-mint path. Do not re-signal unless a new fact appears.",
    },
    {
        "address": "0xff6624b5c407780ddd84ed6fd65cc38ec6547777",
        "first_seen": "run-99, 2026-11-07 16:19:28 WIB (tx 0x48032425b12968685459fd9867de5f29b424640444b587104eb63dbffa7251b4, block 132175491)",
        "machine_wallets": 27,
        "typical_first_buy_bnb": 0.000121125,
        "followup_buy_range_bnb": "median 0.223378725, max 0.383807, total buys 9.2643 BNB (55 sent buys)",
        "label": "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - NAMED (癫猫 / 癫猫) - ANOMALY, reported once as signal run 99",
        "note": "ANOMALY under the fast-path amendment: name/symbol APPEARED - name '癫猫', symbol '癫猫', confirmed in TWO independent fast_rpc passes; "
                "totalSupply 1e27; decimals 18. DexScreener independently confirms 癫猫/癫猫, pair 0x2d3e053bada0378299010fde9f59209985760bab, liquidity "
                "$0.07 (drained after the rotation's sells), pair created ~16:19 WIB. First buy 16:19:28 WIB by 0xcb08c02c0a, 0.000121125 BNB -> "
                "9,674.63 tokens. Wallet set byte-identical to the other three run-99 rotations and diff 0 vs the run-98 machine set (27/27 overlap). "
                "Buy sizes WITHIN class norm - NOT a size anomaly. 92 sells in-window. Pair token0/token1 PARTIAL run 99: token1 = the token READ OK, "
                "token0 unreadable (fast_rpc outage) - retry run 100. Auto-mint BLOCKED at guard (c) - paid PCS token, no free-mint path. Do not "
                "re-signal unless a new fact appears.",
    },
    {
        "address": "0xdb4950e7c92cf433d971775ea57d2ea7c6757777",
        "first_seen": "run-99, 2026-11-07 16:40:43 WIB (tx 0xc15b4e57f864affae10007a201032e319ec56a0dce126dc7b0f7631b5e332f87, block 132178323)",
        "machine_wallets": 27,
        "typical_first_buy_bnb": 0.000121125,
        "followup_buy_range_bnb": "median 0.223378725, max 0.270613, total buys 8.3518 BNB (50 sent buys)",
        "label": "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - NAMED (goonerpad / gooner) - ANOMALY, reported once as signal run 99",
        "note": "ANOMALY under the fast-path amendment: name/symbol APPEARED - name 'goonerpad', symbol 'gooner', confirmed in pass 2 via fast_rpc "
                "(pass 1 timed out); totalSupply 1e27; decimals 18. DexScreener independently confirms goonerpad/gooner, pair "
                "0x41cbb4910fd4959f651d7bff8d8b5ed5cd355dfc, liquidity $0.07 (drained after the rotation's sells), pair created ~16:40 WIB. First buy "
                "16:40:43 WIB by 0xcb08c02c0a, 0.000121125 BNB -> 9,640.67 tokens. Wallet set byte-identical to the other three run-99 rotations and "
                "diff 0 vs the run-98 machine set (27/27 overlap). Buy sizes WITHIN class norm - NOT a size anomaly. 64 sells / 23 wallets in-window - "
                "rotation STILL FILLING at window end (sells lag buys); watch run 100 whether it completes to 27 wallets - do NOT treat completion as "
                "a new rotation. Pair token0/token1 PARTIAL run 99: token1 = the token READ OK, token0 unreadable (fast_rpc outage) - retry run 100. "
                "Auto-mint BLOCKED at guard (c) - paid PCS token, no free-mint path. Do not re-signal unless a new fact appears.",
    },
]
s.setdefault("machine_tokens", []).extend(new_entries)

# update stalled labels' run ranges
for e in s["machine_tokens"]:
    if e["address"].lower().startswith("0x1153607e"):
        e["label"] = "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - rotation STALLED at 26 wallets (runs 91-99)"
    if e["address"].lower().startswith("0x79cd174c"):
        e["label"] = "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - rotation STALLED at 20 wallets (runs 90-99)"

# signaled projects: append the four (paid-only)
s.setdefault("signaled_projects_over_20pct", []).extend([
    "首个开演唱会的猫 (悟空) 0x50e4506e76e816ed5e74557b4b8a57037d927777 (paid-only, machine-token, run-99, NAMED - anomaly reported once as signal)",
    "Gay Executive Officers (GEO) 0x6b12a49f7a6aa9061278cdc4efd4f417e5a77777 (paid-only, machine-token, run-99, NAMED - anomaly reported once as signal)",
    "癫猫 (癫猫) 0xff6624b5c407780ddd84ed6fd65cc38ec6547777 (paid-only, machine-token, run-99, NAMED - anomaly reported once as signal)",
    "goonerpad (gooner) 0xdb4950e7c92cf433d971775ea57d2ea7c6757777 (paid-only, machine-token, run-99, NAMED - anomaly reported once as signal)",
])

# ---- next run note ----
note = (
    "Next run sent-tx window starts from block 132179369. "
    "RETRY run 100: (1) Pair token0/token1 reads for 0xa6e6... pair 0x9fac925655fa4985ab4fe2fe9e0ca8ae323cc9da and 0x887c... pair "
    "0xa9fa6efb21c252b7d4ab81d19a07ee4ecf6d2c97 (fast_rpc race returns None / 'all endpoints failed', 17 consecutive runs - persistently unreadable, "
    "unverified not absence), plus 0x2bfb pair 0x782671f637bf1a01de482824c4b2520bc58a5a4b, 0xc459 pair 0xeca06856c88fcdf1506886431a079d3f2565ca82, and "
    "rotation 0x43c8 pair 0xaafebb5244e2e546f7cd18a2c89f85bbee03f1e0 (unreadable run 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98 AND 99 - retry "
    "opportunistically, not an anomaly), PLUS run-89 rotation pairs 0xcfdb 0x1e04925db4eabab2917ef73a8cdf232bcc69b5ba, 0x0cf8 "
    "0xf6800c4a1ecdffbd64f9047c606bdb32dee0127f, 0xe68b 0xfab7cb4979c9e4738afc61e4974177cf72c50896 (token0/token1 unreadable run 89, 90, 91, 92, 93, 94, "
    "95, 96, 97, 98 AND 99; 0x31e4 pair 0x60ca0aef... READ OK run 89), PLUS new run-99 rotation pairs 0xdb49 0x41cbb4910fd4959f651d7bff8d8b5ed5cd355dfc "
    "(token1 = token READ OK run 99, token0 unreadable), 0xff66 0x2d3e053bada0378299010fde9f59209985760bab (token1 = token READ OK, token0 unreadable), "
    "0x6b12 0x43d85c9fa81bc019701431460d1b3459b057af6d (token0 = token READ OK, token1 unreadable); 0x50e4 pair 0x26b53042e668d52056e4449abcd238cf01e3a155 "
    "READ OK run 99 (token0 = token, token1 = WBNB) - removed from retry. 41cc pair 0x05ced0b9f08725c126e4f744ba9e58dc95c0c936 READ OK run 99 (token0 = "
    "token, token1 = WBNB) - REMOVED from the retry list; run-97 rotation pairs c90a/e3a8 READ OK run 98 - already removed. "
    "(2) RETRY run 100 receipt for creation tx 0x21c210dfea7439ddd710e9c758191c4ad5c0be98e449097c6a338b50dc09c3d3 (wallet 0x3154f694, 15:51:47 WIB, "
    "value ~0.1054 BNB) - NULL receipt run 99, deployed address UNVERIFIED; add its contractAddress to the run-100 inbound list if recovered. "
    "(3) Run-100 inbound list = run99 list (1517) + run-100 deployments + new rotation tokens. "
    "(4) Run-99 inbound window FULLY CLOSED in-run after a/b3 re-runs (1517/1517, 14,436 logs, 0 hits, 0 failed) - no inbound retry carried into run 100. "
    "(5) 0xdb4950e7... rotation STILL FILLING at window end (64 sells / 23 wallets; buys complete at 27) - watch run 100 whether sells complete to 27 "
    "wallets; do NOT treat completion as a new rotation. 0x1153607e... rotation STALLED at 26 wallets (0 wallets runs 91-99, 9th quiet run after debut) - "
    "watch run 100 the same way. 0x79cd... STALLED at 20 wallets (0 wallets runs 90-99, 10th quiet run after debut) - same. Run-98 named rotations "
    "0x41cc.../0x43bc.../0x2120.../0xda79...: 0 wallets run 99 (2nd quiet run after debut) - watch run 100 the same way. Run-97 named rotations "
    "0xc90a.../0xe3a8...: 0 wallets run 99 (2nd quiet run after debut) - same. "
    "Dedupe new mints against all tx hashes in reported_findings (223 mint entries over 221 unique tx hashes, direct count run 77). Run-75 mint tx "
    "0x23cd8740... (AFeng, tracker 0x636f..., 0.15 BNB) is a KNOWN REPEAT of the run-70 finding - do not report as new if it repeats again. "
    "Paid-only signals run 63 (CORLA 0x4a9c), run 64 (4 ASI), run 65 (4 ASI quad-2), run 66 (tokens 0x19b7.../0x540d...), run 68 (tokens 0xf3cc.../0xe7e2...), "
    "run 69 (token 0x4d15...), run 70 (FIVE tokens 0x4df7.../0xae06.../0x2516.../0x1247.../0x8e0d...), run 71 (SIX tokens 0xe51b.../0xc2e1.../0x5785.../0xfff4.../0xe4c9.../0x25b4...), "
    "run 72 (THREE tokens 0x26ef.../0x7145.../0xdfb3...), run 73 (FOUR tokens 0x1d9f.../0xe0f0... at 27 wallets + 0x198c... at 21 wallets), run 74 (FOUR tokens "
    "0xe4e0.../0x4d2e.../0xaf84... at 27 wallets + 0x73c9... at 26 wallets), run 75 (THREE tokens 0x167b.../0x5205.../0x4f6d... at 27 wallets each), run 76 (TWO tokens "
    "0x0cda... at 27 wallets + 0xacc8... at 26 wallets), run 77 (THREE tokens 0x3029.../0x5eb1.../0x1a57... at 27 wallets each), run 78 (TWO tokens "
    "0xcbbc.../0x41cc... at 27 wallets each), run 79 (TWO tokens 0x5833.../0x32b4... at 27 wallets each), run 80 (ONE token 0x489e... at 27 wallets), "
    "run 81 (TWO tokens 0x7f7a.../0x33f7... at 27 wallets each), run 82 (THREE tokens 0xd468.../0xa6e6.../0x887c... at 27 wallets each), run 85 (ONE token "
    "0x2717a156b86c3c8894bb2dea9a34c514e8fc7777 at 27 wallets), run 86 (TWO tokens 0x2bfb481d4812f329b6244450137096157a6b7777 at 27 wallets + "
    "0xc4599c77985efd0353b688b6127ad4f3399e7777 at 26 wallets), run 87 (TWO tokens 0x889a76e4d48169d0398828a36c57b64298577777 at 27 wallets + "
    "0x42491efdffe0aea61799d12b79cfe6ad2a977777 at 27 wallets), run 88 (THREE tokens 0x43c8f55b12391671d1f00b04ba1ef6d1842e7777 + "
    "0x3d1201ea0d559e7071bc42d24e1494c6d7547777 + 0xeae0936e2f9ecb0a1acac8c5b9e43f86d3d37777 at 27 wallets each + 0x79cd174ca3ec25c06ff5fddae365643f73d77777 at "
    "18 wallets, rotation in progress), run 89 (FOUR tokens 0xcfdb66667d0ced8bff240e17547c7bef1ca97777 + 0x0cf896204bf1bd8a9b2a5bf07879ead17b7f7777 + "
    "0xe68bdc90fee5a233bb054a3c89854a5b50d27777 + 0x31e43b72f14fea00a576e84c4e3605d98a317777 at 27 wallets each + 0x79cd174ca3ec25c06ff5fddae365643f73d77777 at "
    "20 wallets, rotation still in progress), run 90 (FIVE tokens 0x6a2590934e55671a6fab9fa8edca8da4960e7777 + 0x9f7ea7a4eaa7f39782caeb1ecab8176187e97777 + "
    "0x8c64aa82e861393bf760ee6d0eb29c0c60f07777 + 0xc1ab1e832da23f85a27aa2778f555d00319e7777 at 27 wallets each + 0x1153607e323c42f93c82b80e1772f9cc626b7777 at "
    "26 wallets, rotation possibly still filling + 0x79cd174ca3ec25c06ff5fddae365643f73d77777 STALLED at 20 wallets, 0 wallets run 90) "
    "run 91 (ZERO new rotations; all five run-90 tokens 0 wallets, 1st quiet run after debut; 0x1153... STALLED at 26, did NOT reach 27; 0x79cd... "
    "STALLED at 20, 2nd quiet run) run 92 (ZERO new rotations; all five run-90 tokens 0 wallets, 2nd quiet run after debut; 0x1153... STALLED at 26, "
    "2nd quiet run; 0x79cd... STALLED at 20, 3rd quiet run) run 93 (ZERO new rotations; all five run-90 tokens 0 wallets, 3rd quiet run after debut; "
    "0x1153... STALLED at 26, 3rd quiet run; 0x79cd... STALLED at 20, 4th quiet run) run 94 (ZERO new rotations; all five run-90 tokens 0 wallets, 4th "
    "quiet run after debut; 0x1153... STALLED at 26, 4th quiet run; 0x79cd... STALLED at 20, 5th quiet run) run 95 (ZERO new rotations; all five run-90 "
    "tokens 0 wallets, 5th quiet run after debut; 0x1153... STALLED at 26, 5th quiet run; 0x79cd... STALLED at 20, 6th quiet run; inbound FULLY CLOSED "
    "first attempt, 0 failed) run 96 (ZERO new rotations; all five run-90 tokens 0 wallets, 6th quiet run after debut; 0x1153... STALLED at 26, 6th "
    "quiet run; 0x79cd... STALLED at 20, 7th quiet run; inbound FULLY CLOSED in-run after 6-contract same-run retry; chunks a/b3 died silently first "
    "attempt ~contract 200, re-run from scratch) run 97 (TWO NEW rotations 0xc90a... Timothy/TIMOTHY + 0xe3a8... symbol BTC at 27 wallets each - FIRST "
    "NAMED machine-token rotations, anomaly reported once as signal run 97; buy sizes in class norm; 0x1153... STALLED at 26, 7th quiet run; 0x79cd... "
    "STALLED at 20, 8th quiet run; 25 deployments (first in 7 runs); inbound FULLY CLOSED in-run, 1374 contracts, 12,655 logs, 0 hits, 2 failed retried "
    "same-run 2/2 OK; first-attempt chunks WEDGED on proxy sockets ~contract 10, killed by PID + re-launched from scratch) run 98 (FOUR NEW rotations "
    "0x41cc... babydoge2026/babydoge + 0x43bc... funny trauma/trauma + 0x2120... Privacy Index/PRIVACY + 0xda79... Eat Trade Fart/ETF at 27 wallets each - "
    "ALL NAMED, second consecutive run with named rotations, anomaly reported once as signal run 98; buy sizes in class norm; c90a/e3a8 0 wallets (1st "
    "quiet run); 0x1153... STALLED at 26, 8th quiet run; 0x79cd... STALLED at 20, 9th quiet run; 72 deployments (second straight run with deployments, "
    "0x97bd895f alone 18); inbound FULLY CLOSED in-run FIRST ATTEMPT, 1450 contracts, 14,328 logs, 0 hits, 0 failed; sent pass attempt 1 SIGTERM at "
    "37/55, re-run from scratch 55/55 OK) run 99 (FOUR NEW rotations 0x50e4... 首个开演唱会的猫/悟空 + 0x6b12... Gay Executive Officers/GEO + 0xff66... "
    "癫猫/癫猫 + 0xdb49... goonerpad/gooner at 27 wallets each - ALL NAMED, third consecutive run with named rotations, anomaly reported once as signal "
    "run 99; buy sizes in class norm; db49 rotation still filling at window end (64 sells/23 wallets); 41cc/43bc/2120/da79 0 wallets (2nd quiet run); "
    "c90a/e3a8 0 wallets (2nd quiet run); 0x1153... STALLED at 26, 9th quiet run; 0x79cd... STALLED at 20, 10th quiet run; 64 deployments (third straight "
    "run with deployments, 0x3154f694 alone 7); inbound FULLY CLOSED in-run after a/b3 re-runs (service restart killed first attempts ~contract 350/341), "
    "1517 contracts, 14,436 logs, 0 hits, 0 failed; 1 creation receipt NULL (0x21c210df...) - deployed address unverified, retry run 100) "
    "auto-mint BLOCKED at guard (c) - do not re-signal or re-report the block unless a new mint/buy fact appears for those contracts (e.g. a genuine "
    "free-mint path). Per the 2026-11-06 ~18:30 machine-token fast-path amendment, routine machine-token rotations are recorded in state WITHOUT a chat "
    "report (no full verification per run); report only on anomaly (buy size far off norm, name/symbol appears, website, or free-mint path). "
    "Paid fact: run99 FOUR NEW rotations 0x50e4... (首个开演唱会的猫/悟空) + 0x6b12... (Gay Executive Officers/GEO) + 0xff66... (癫猫/癫猫) + 0xdb49... "
    "(goonerpad/gooner) at 27 wallets each - ALL NAMED, third consecutive run with named rotations (anomaly: name/symbol appeared; reported once as "
    "signal run 99, paid-only, auto-mint blocked guard (c)); run-98 tokens 0x41cc.../0x43bc.../0x2120.../0xda79... 0 wallets (2nd quiet run after debut); "
    "run-97 tokens 0xc90a.../0xe3a8... 0 wallets (2nd quiet run after debut); run-90 tokens 0x6a25.../0x9f7e.../0x8c64.../0xc1ab.../0x1153... 0 wallets "
    "(9th quiet run after debut); run-89 tokens 0xcfdb.../0x0cf8.../0xe68b.../0x31e4... 0 wallets (10th quiet run after debut); run-88 tokens 0x43c8.../0x3d12.../0xeae0... "
    "0 wallets (11th quiet run after debut); run-87 tokens 0x889a.../0x4249... 0 wallets (12th quiet run after debut); run-86 tokens 0x2bfb.../0xc459... "
    "0 wallets (13th quiet run after debut); run-85 token 0x2717... 0 wallets (14th quiet run); run-82 tokens 0xd468.../0xa6e6.../0x887c... all 0 wallets "
    "(17th quiet run after debut); run-81 tokens 0 wallets (18th quiet run); run-80 token 0 wallets (19th quiet run); GrokBot 0xfcd0... absent "
    "(0 wallets) - 40th consecutive quiet run (59, 61-99) after the run-60 burst; CORLA-97af 0 wallets; CORLA 0x4a9c 0 wallets; all run-64/65 ASI "
    "contracts 0 wallets; all run-66/68/69/70/71/72/73/74/75/76/77/78/79 machine tokens 0 wallets. Run 99 had 64 deployments (third straight run with "
    "deployments; 0x3154f694 alone 7; added to the inbound list for run 100 - 63 addresses recovered, 1 NULL receipt). AFeng 0 txs; future1001.ai 0 txs; "
    "0x2325... 20 txs (13 aggregator 0x27772d13 + 7 approvals, total value 0.52 BNB); 0x8e96... 0 txs; 0x3803... 53 txs (35 aggregator 0x39ecce49 + 18 approvals, "
    "total value 0.000468 BNB, churn as usual). SCRIPT LESSON (run 85, FIXED run 86): when copying runNN-receipts.py for the next run, sed-replace the two "
    "hardcoded json.dump output paths too (runNN-receipts.json / runNN-paid.json) - run 93's copy was verified correct before running (dumps to "
    "run93-receipts.json/run93-paid.json). PROCESS LESSON (run 86): the receipts pass died silently at 420/461 (service-restart pattern, same as runs "
    "82/84) - the partial-file resume worked; always re-run the same script to resume rather than re-fetching from scratch. Run 99 receipts completed in "
    "one attempt, no resume needed; sent pass completed first attempt 55/55 OK; inbound chunks a/b3 first attempts DIED SILENTLY at ~contract 350/341 "
    "(service restart ~10:35 UTC, no JSON saved) and were re-run from scratch (a2/b3-2) to completion. A frozen log mtime with a live process is a stall, "
    "not a death - wait before re-running; a log frozen >5 min with NO live process is a silent death - re-run the chunk from scratch; a socket wedged "
    ">5 min while fresh calls work is a wedge - kill by PID (pkill -f can match the wrapper shell itself, use kill <pid>) and re-run the chunk from scratch. "
    "INBOUND FILENAME QUIRK FIXED run 88: chunk output files are now correctly named run93-inbound93-{a,b1,b2,b3}.json. Same-owner factory groups now also "
    "include 0x293f and 0x1103 (proven 2026-11-06 ~01:14 WIB, AGENTS.md) alongside the groups listed in the body."
)
s["next_run_note"] = note

json.dump(s, open(P, "w"), indent=1)
print("state updated; last_run now:", s["last_run"]["run"], "block_end:", s["last_run"]["block_end"])
print("machine_tokens:", len(s.get("machine_tokens", [])), "| signaled:", len(s.get("signaled_projects_over_20pct", [])))
print("inbound99 complete:", s["inbound_log_leg_run99"]["complete"], "| failed:", s["inbound_log_leg_run99"]["failed"])
print("inbound98 complete:", s["inbound_log_leg_run98"]["complete"], "| failed:", s["inbound_log_leg_run98"]["failed"])
