#!/usr/bin/env python3
"""Run 98 state update (read-only job bookkeeping; no chain writes).

Completes run 98 (window 132158491-132168467, tx 2026-11-07 14:13:51 - 15:26:47 WIB).
Sent/receipts/paid done and verified; inbound leg run-98 window FULLY CLOSED in-run
(1450/1450, 14,328 logs, 0 hits, 0 failed, first attempt - no wedge/death).
NO new mints. FOUR NEW machine-token rotations at 27 wallets each - ALL NAMED
(babydoge2026 / funny trauma / Privacy Index / Eat Trade Fart), the SECOND
consecutive run with named rotations (run 97 had 2): anomaly under the fast-path
amendment, reported ONCE as a paid-only signal (not a lead, not a buy
recommendation, auto-mint blocked at guard (c)). 72 deployments this run
(second straight run with deployments; 0x97bd895f alone 18). Bridge unchanged
(0 new mints, 0 not_evaluated).
"""
import json, shutil

P = "/home/hatch/workspace/narrative-pulse/tracked-wallet-mint-scan-state.json"
shutil.copy(P, str(P) + ".bak-run98-pre")
s = json.load(open(P))

last_run_98 = {
    "run": 98,
    "block_start": 132158491,
    "block_end": 132168467,
    "window_wib": "2026-11-07 14:13:51 - 15:26:47 WIB (tx times); run executed ~15:05 - ~16:37 WIB; sent-pass in-window txs 1286, 0 mint-pattern txs",
    "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set); 0 failed, no retry needed.",
    "method_note": (
        "Sent pass Ankr ankr_getTransactionsByAddress via module: FIRST attempt killed by SIGTERM at wallet 37/55 (service-restart pattern, "
        "no JSON saved - script dumps only at end); re-run from scratch completed 55/55 OK, 1286 txs, 34 wallets active, 0 failed. "
        "Receipts via fast_rpc batch (6, ~4s pause) for 827 non-approve candidates: 826 status 1, 1 status 0, 0 null, 0 mint logs. "
        "Receipts completed in one attempt, no resume needed. "
        "Paid: 31 tokens; max 27 wallets/token (FOUR new rotations at 27 each - see anomaly signal; 13 tokens at 3 wallets, all the same churn trio "
        "0x3803/0xad94/0xc7c5, all ...7777; 8 at 2, 6 at 1; 0 overlap with run-97's 31 paid tokens - the ...7777 churn set turns over every run). "
        "NEW ROTATIONS - ANOMALY (named tokens, second consecutive run - run 97 had 2 named, run 98 has 4): "
        "0x41cc11074f16292f311ecac7d6702bb39b157777 (babydoge2026重新问世 / babydoge), "
        "0x43bcaac4a4aa9711c2846d37fd78879435087777 (funny trauma / trauma), "
        "0x21209278656222412f365716863bfb5110637777 (Privacy Index / PRIVACY), "
        "0xda79bd2e54f46492ac5c44bb7d20da46a2ae7777 (Eat Trade Fart / ETF). "
        "All four: name+symbol confirmed in TWO independent fast_rpc passes, totalSupply 1e27, decimals 18. DexScreener independently confirms all "
        "four (same names/symbols, pairs match the on-chain log-derived pair addresses, liquidity $0.07 each - drained after the rotation's sells). "
        "All four bought by the SAME 27-wallet machine set, byte-identical to each other and diff 0 vs the run-97 c90a set (27/27 overlap). "
        "Buy sizes WITHIN class norm (NOT a size anomaly): first buy ~0.000121 BNB -> ~9,674 tokens each (41cc 0.000121241835356, 43bc 0.000121393351982, "
        "2120 0.000121125, da79 0.000121241835356); follow-up medians 0.223379 (41cc/2120), 0.228465 (43bc), 0.229933 (da79); max 0.348292-0.413007; "
        "totals 9.5211-9.8920 BNB; buys 56-58, sells 98-100 per token. First buys: 41cc 14:18:46 WIB by 0xcb08c02c0a tx 0x5e45877ba389 block 132159401 "
        "pair 0x05ced0b9f08725c126e4f744ba9e58dc95c0c936; 43bc 14:36:24 WIB by 0xcb08c02c0a tx 0x3242f0ef6c85 block 132161751 pair "
        "0xb6d5522d280e3bc7770d0c3446d4dd9da06b946e; 2120 14:55:07 WIB by 0x362396125a tx 0xcc8d4a5f4b7b block 132164246 pair "
        "0xef9bf0f21e5f3bd8c9ca1fb13090e3dad2436520; da79 15:15:56 WIB by 0xcb08c02c0a tx 0x6d1fccce0066 block 132167020 pair "
        "0x7cb8b4530fadb0ffcede1453e1313b0dba7289a9. Pair token0/token1: 43bc token0=token/token1=WBNB, 2120 token0=token/token1=WBNB, da79 "
        "token0=WBNB/token1=token (all READ OK run 98); 41cc pair token0/token1 UNREADABLE (fast_rpc 'all endpoints failed') - unverified, not "
        "absence; retry run 99. Auto-mint BLOCKED at guard (c) for all four (paid PCS tokens, no free-mint path; guard (a) website also unverified) - "
        "no preview, no execution. Anomaly reported ONCE as a paid-only signal per the fast-path amendment (name/symbol appeared); all four recorded "
        "in machine_tokens + signaled_projects_over_20pct (paid-only, run-98). "
        "Run-97 named rotations c90a/e3a8: 0 wallets this run - 1st quiet run after debut. "
        "ALL run-90 machine-token rotations 0 wallets this run - 8th quiet run after debut for 0x6a2590934e55671a6fab9fa8edca8da4960e7777, "
        "0x9f7ea7a4eaa7f39782caeb1ecab8176187e97777, 0x8c64aa82e861393bf760ee6d0eb29c0c60f07777, "
        "0xc1ab1e832da23f85a27aa2778f555d00319e7777 (27 wallets each in run 90). "
        "0x1153607e323c42f93c82b80e1772f9cc626b7777: 0 wallets this run - rotation STALLED at 26 wallets "
        "(missing wallet 0x2cc8192fc6 never bought in); 8th quiet run after debut. "
        "0x79cd174ca3ec25c06ff5fddae365643f73d77777: 0 wallets this run - rotation STALLED at 20 wallets; 9th quiet run after debut (runs 88-89 active). "
        "Deployments: 72 contract creations by tracked wallets this run - SECOND straight run with deployments (25 in run 97); in 4 waves ~14:17, "
        "~14:35, ~14:52, ~15:11 WIB by 13 machine-set wallets (0x97bd895f alone 18, 0x3154f694/0x1cce4ec5/0xc0c84518 6 each, 0xf795c525/0xaa49e7fe/"
        "0x3a39aa05/0x9b519f5d/0x64e893a4 5 each, 0xcb08c02c/0x5b4beded 4 each, 0xc6219468 2, 0xa952331e 1). Deployed addresses added to the inbound list "
        "(run98-inbound-contracts.json, 1450 total) and carried to run 99. Deployed contracts' metadata not read this run (fast_rpc flaky; the 4 "
        "rotation tokens are NOT among the deployments - deployed earlier); no mint logs from them in-window (inbound 0 hits covers them). "
        "AFeng 0 txs; future1001.ai 0 txs; 0x2325... 5 txs (4 aggregator 0x27772d13 + 1 approval); 0x8e96... 0 txs; 0x3803... 39 txs (26 aggregator "
        "0x39ecce49 + 13 approvals, total value ~0.0005 BNB, churn as usual). 2 plain BNB transfers (input 0x, not mints): 0x3628... -> 0xc009... "
        "0.0001255 BNB 14:57:27 WIB + 0xc7c5... -> 0x7f51... 0.0001282 BNB 15:07:45 WIB. "
        "Selectors (sent pass, 1286 txs): 459 approvals (0x095ea7b3) + 446 PCS sells (0x791ac947) + 277 PCS buys (0xb6f9de95) + 72 contract creations "
        "(0x60806040) + 26 aggregator (0x39ecce49) + 4 aggregator (0x27772d13, 0x2325...) + 2 plain transfers (empty input). "
        "Nonzero-value txs 367, total 41.4091 BNB, max 0.413 BNB (2120 follow-up buy). 1 status-0 tx: failed PCS sell by 0xc6219468 (14:42:30 WIB, "
        "tx 0x5c0531f4ea7708d20ec47abb25ba96f69502417fa00609223f2c31596b58b2e7, value 0). "
        "Most active wallets: 0xa952331e 77 txs, 0x9cdd08f3 72, 0xc6219468 71, 0xf795c525 53, 0xe9ed24db 52, 0x1cce4ec5 50, 0x9b519f5d 49, 0x92bc3297 48, "
        "0xfdec62fd 48, 0xdb2d83f9 46, 0xc0c84518 46, 0x3a39aa05 45. Run-98 inbound list = run97 list (1374) + 72 run-98 deployments + 4 new rotation "
        "tokens = 1450. "
        "Inbound leg run-98 WINDOW: FULLY CLOSED in-run - 1450/1450 contracts, 14,328 logs, 0 hits, 0 failed. "
        "Chunks a (400, 7,166 logs, 0 failed, 5 truncated) + b1 (200, 3,310 logs, 0 failed, 2 truncated) + b2 (200, 563 logs, 0 failed) + b3 (650, "
        "3,289 logs, 0 failed) = 14,328 logs, 0 hits. 7 truncated contracts, all topic-filtered to 0 logs (a: 0x1de4... AFeng sale, 0x3dca..., "
        "0x55d398... USDT, 0x6288..., 0x636fdfa9... tracker; b1: 0x63de... AGC, 0x7857...) - same set as runs 91-97 minus 0x10b3... (not truncated this "
        "run). ALL FOUR chunks completed on FIRST attempt - no wedge, no silent death this run (cleaner than runs 94-97). "
        "Pair token0/token1 STILL UNREADABLE for the EIGHT legacy pairs in run-98 pair retry (fast_rpc race 'all endpoints failed', 16th consecutive "
        "run for a6e6/887c/2bfb/c459, 11th for 43c8, 9th for the three run-89 rotation pairs cfdb/0cf8/e68b) - unverified, not absence; retry run 99. "
        "BUT the two run-97 rotation pairs READ OK this run (c90a + e3a8: token0 WBNB 0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c, token1 = the token) - "
        "removed from the retry list; new run-98 pairs 43bc/2120/da79 also READ OK (see above); only the 41cc pair remains unreadable. NOTE: "
        "fast_rpc batch worked fine for the receipts pass in the same run (827/827) and intermittently for token-meta reads - the outage is "
        "time-varying / per-call, not a permanent endpoint failure. Ankr eth_call is NOT available on the multichain endpoint (method -32601) - "
        "cannot substitute for fast_rpc reads. "
        "Pointer-discovery (amendment 19:10): 0 contracts processed - no new mints this run, and the backfill queue is empty (bridge 115 "
        "contracts, 0 not_evaluated); bridge unchanged. "
        "CHAT REPORT this run: the four-named-machine-token anomaly signal (paid-only, NOT a lead, NOT a buy recommendation, auto-mint blocked "
        "guard (c)) - reported once per the fast-path amendment. No new mints, no Free Bacot signal beyond that, no auto-mint trigger execution. "
        "No preview/mint/sign/login/purchase by this job."
    ),
}
cur_run = s.get("last_run", {}).get("run", 0)
if cur_run < 98:
    s["last_run"] = last_run_98
    print(f"last_run set to 98 (was {cur_run})")
else:
    print(f"last_run already {cur_run} (>=98) - NOT regressing")
    s["run98_last_run_record"] = last_run_98

# --- four new machine_tokens entries: the NAMED rotations (anomaly class) ---
new_tokens = [
    {
        "address": "0x41cc11074f16292f311ecac7d6702bb39b157777",
        "first_seen": "run-98, 2026-11-07 14:18:46 WIB (tx 0x5e45877ba389, block 132159401)",
        "machine_wallets": 27,
        "typical_first_buy_bnb": 0.000121241835356,
        "followup_buy_range_bnb": "median 0.223379, max 0.348292, total buys 9.8920 BNB (58 sent buys)",
        "label": "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - NAMED (babydoge2026重新问世 / babydoge) - ANOMALY, reported once as signal run 98",
        "note": (
            "ANOMALY under the fast-path amendment: name/symbol APPEARED - name 'babydoge2026重新问世', symbol 'babydoge', confirmed in TWO "
            "independent fast_rpc passes; totalSupply 1e27; decimals 18. DexScreener independently confirms babydoge2026重新问世/babydoge, pair "
            "0x05ced0b9f08725c126e4f744ba9e58dc95c0c936, liquidity $0.07 (drained after the rotation's sells), pair created ~14:18 WIB. First buy "
            "14:18:46 WIB by 0xcb08c02c0a, 0.000121241835356 BNB -> 9,674.63 tokens. Wallet set byte-identical to the other three run-98 rotations "
            "and diff 0 vs the run-97 c90a set (27/27 overlap). Buy sizes WITHIN class norm - NOT a size anomaly. 100 sells in-window. Pair "
            "token0/token1 UNREADABLE run 98 (fast_rpc 'all endpoints failed') - unverified, not absence; retry run 99. No website, no free-mint "
            "path. Auto-mint blocked at guard (c). Reported once as a paid-only signal run 98 (not a lead, not a buy recommendation); do not "
            "re-signal or re-report unless a new fact appears (e.g. a genuine free-mint path)."
        ),
    },
    {
        "address": "0x43bcaac4a4aa9711c2846d37fd78879435087777",
        "first_seen": "run-98, 2026-11-07 14:36:24 WIB (tx 0x3242f0ef6c85, block 132161751)",
        "machine_wallets": 27,
        "typical_first_buy_bnb": 0.000121393351982,
        "followup_buy_range_bnb": "median 0.228465, max 0.384561, total buys 9.5211 BNB (56 sent buys)",
        "label": "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - NAMED (funny trauma / trauma) - ANOMALY, reported once as signal run 98",
        "note": (
            "ANOMALY under the fast-path amendment: name/symbol APPEARED - name 'funny trauma', symbol 'trauma', confirmed in TWO independent "
            "fast_rpc passes; totalSupply 1e27; decimals 18. DexScreener independently confirms funny trauma/trauma, pair "
            "0xb6d5522d280e3bc7770d0c3446d4dd9da06b946e, liquidity $0.07 (drained after the rotation's sells), pair created ~14:36 WIB. First buy "
            "14:36:24 WIB by 0xcb08c02c0a, 0.000121393351982 BNB -> 9,686.72 tokens. Wallet set byte-identical to the other three run-98 rotations "
            "and diff 0 vs the run-97 c90a set (27/27 overlap). Buy sizes WITHIN class norm - NOT a size anomaly. 99 sells in-window. Pair "
            "token0/token1 READ OK run 98: token0 = the token, token1 = WBNB 0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c. No website, no free-mint "
            "path. Auto-mint blocked at guard (c). Reported once as a paid-only signal run 98 (not a lead, not a buy recommendation); do not "
            "re-signal or re-report unless a new fact appears (e.g. a genuine free-mint path)."
        ),
    },
    {
        "address": "0x21209278656222412f365716863bfb5110637777",
        "first_seen": "run-98, 2026-11-07 14:55:07 WIB (tx 0xcc8d4a5f4b7b, block 132164246)",
        "machine_wallets": 27,
        "typical_first_buy_bnb": 0.000121125,
        "followup_buy_range_bnb": "median 0.223379, max 0.413007, total buys 9.8001 BNB (58 sent buys)",
        "label": "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - NAMED (Privacy Index / PRIVACY) - ANOMALY, reported once as signal run 98",
        "note": (
            "ANOMALY under the fast-path amendment: name/symbol APPEARED - name 'Privacy Index', symbol 'PRIVACY', confirmed in TWO independent "
            "fast_rpc passes; totalSupply 1e27; decimals 18. DexScreener independently confirms Privacy Index/PRIVACY, pair "
            "0xef9bf0f21e5f3bd8c9ca1fb13090e3dad2436520, liquidity $0.07 (drained after the rotation's sells), pair created ~14:55 WIB. First buy "
            "14:55:07 WIB by 0x362396125a (NOT the usual 0xcb08c02c0a first buyer - the only run-98 rotation whose first buy came from another "
            "machine-set wallet), 0.000121125 BNB -> 9,665.31 tokens. Wallet set byte-identical to the other three run-98 rotations and diff 0 vs "
            "the run-97 c90a set (27/27 overlap). Buy sizes WITHIN class norm - NOT a size anomaly. 100 sells in-window. Pair token0/token1 READ "
            "OK run 98: token0 = the token, token1 = WBNB 0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c. No website, no free-mint path. Auto-mint blocked "
            "at guard (c). Reported once as a paid-only signal run 98 (not a lead, not a buy recommendation); do not re-signal or re-report unless "
            "a new fact appears (e.g. a genuine free-mint path)."
        ),
    },
    {
        "address": "0xda79bd2e54f46492ac5c44bb7d20da46a2ae7777",
        "first_seen": "run-98, 2026-11-07 15:15:56 WIB (tx 0x6d1fccce0066, block 132167020)",
        "machine_wallets": 27,
        "typical_first_buy_bnb": 0.000121241835356,
        "followup_buy_range_bnb": "median 0.229933, max 0.376747, total buys 9.7681 BNB (58 sent buys)",
        "label": "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - NAMED (Eat Trade Fart / ETF) - ANOMALY, reported once as signal run 98",
        "note": (
            "ANOMALY under the fast-path amendment: name/symbol APPEARED - name 'Eat Trade Fart', symbol 'ETF', confirmed in TWO independent "
            "fast_rpc passes; totalSupply 1e27; decimals 18. DexScreener independently confirms Eat Trade Fart/ETF, pair "
            "0x7cb8b4530fadb0ffcede1453e1313b0dba7289a9, liquidity $0.07 (drained after the rotation's sells), pair created ~15:15 WIB. First buy "
            "15:15:56 WIB by 0xcb08c02c0a, 0.000121241835356 BNB -> 9,674.63 tokens. Wallet set byte-identical to the other three run-98 rotations "
            "and diff 0 vs the run-97 c90a set (27/27 overlap). Buy sizes WITHIN class norm - NOT a size anomaly. 98 sells in-window. Pair "
            "token0/token1 READ OK run 98: token0 = WBNB 0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c, token1 = the token. No website, no free-mint "
            "path. Auto-mint blocked at guard (c). Reported once as a paid-only signal run 98 (not a lead, not a buy recommendation); do not "
            "re-signal or re-report unless a new fact appears (e.g. a genuine free-mint path)."
        ),
    },
]
s.setdefault("machine_tokens", []).extend(new_tokens)
print("machine_tokens now:", len(s["machine_tokens"]))

# Update the run-97 named entries in place (0 wallets run 98 - 1st quiet run after debut).
for mt in s.get("machine_tokens", []):
    if mt.get("address", "").lower() in ("0xc90a6cf8d74cf3540eaca3ce63ea7ae4e1ec7777",
                                          "0xe3a8e1ca392b316c42d780c3cf15202f80f37777"):
        mt["note"] = mt.get("note", "") + (
            " RUN-98 UPDATE: 0 wallets this run - 1st quiet run after debut. No buys and no sells from tracked wallets for this token in the "
            "run-98 window. Not treated as an anomaly under the fast-path amendment; watch run 99 for any resumption, do NOT treat a return as "
            "a new rotation."
        )
        print(mt["address"][:10], "entry updated: 0 wallets run 98 (1st quiet run)")
# Update the run-90 0x1153 entry in place (0 wallets run 98 - 8th quiet run, stalled at 26).
for mt in s.get("machine_tokens", []):
    if mt.get("address", "").lower() == "0x1153607e323c42f93c82b80e1772f9cc626b7777":
        mt["machine_wallets"] = 26
        mt["label"] = "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - rotation STALLED at 26 wallets (runs 91-98)"
        mt["note"] = mt.get("note", "") + (
            " RUN-98 UPDATE: 0 wallets this run - rotation STALLED at 26 wallets; 8th quiet run after debut. No buys and no sells from "
            "tracked wallets for this token in the run-98 window. Not treated as an anomaly under the fast-path amendment (no size deviation, "
            "name/symbol, website, or free-mint path appeared); watch run 99 for any resumption, do NOT treat a return as a new rotation."
        )
        print("1153 entry updated: stalled at 26, 0 wallets run 98 (8th quiet run)")
        break
# Update the run-88/89 0x79cd entry in place (0 wallets run 98 - 9th quiet run, stalled at 20).
for mt in s.get("machine_tokens", []):
    if mt.get("address", "").lower() == "0x79cd174ca3ec25c06ff5fddae365643f73d77777":
        mt["machine_wallets"] = 20
        mt["label"] = "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - rotation STALLED at 20 wallets (runs 90-98)"
        mt["note"] = mt.get("note", "") + (
            " RUN-98 UPDATE: 0 wallets this run - rotation STALLED at 20 wallets; 9th quiet run after debut (runs 88-89 active). No buys and "
            "no sells from tracked wallets for this token in the run-98 window. Not treated as an anomaly under the fast-path amendment; "
            "watch run 99 for any resumption, do NOT treat a return as a new rotation."
        )
        print("79cd entry updated: stalled at 20, 0 wallets run 98 (9th quiet run)")
        break

s.setdefault("signaled_projects_over_20pct", []).extend([
    "babydoge2026重新问世 (babydoge) 0x41cc11074f16292f311ecac7d6702bb39b157777 (paid-only, machine-token, run-98, NAMED - anomaly reported once as signal)",
    "funny trauma (trauma) 0x43bcaac4a4aa9711c2846d37fd78879435087777 (paid-only, machine-token, run-98, NAMED - anomaly reported once as signal)",
    "Privacy Index (PRIVACY) 0x21209278656222412f365716863bfb5110637777 (paid-only, machine-token, run-98, NAMED - anomaly reported once as signal)",
    "Eat Trade Fart (ETF) 0xda79bd2e54f46492ac5c44bb7d20da46a2ae7777 (paid-only, machine-token, run-98, NAMED - anomaly reported once as signal)",
])
print("signaled now:", len(s["signaled_projects_over_20pct"]))

s["paid_signal_run98"] = {
    "note": "ANOMALY SIGNAL (paid-only, NOT a buy recommendation, NOT a Free Bacot lead, NOT an auto-mint trigger). SECOND consecutive run with NAMED machine-token rotations - and now FOUR at once (run 97 had 2): the machine set bought FOUR tokens that HAVE on-chain name/symbol, breaking the unnamed pattern of all 24 pre-run-97 machine tokens. Reported once per the fast-path amendment (name/symbol appeared). Auto-mint BLOCKED at guard (c) for all four (paid PCS tokens, no free-mint path). Do not re-signal unless a new fact appears (e.g. a genuine free-mint path).",
    "tokens": [
        {"address": "0x41cc11074f16292f311ecac7d6702bb39b157777", "name": "babydoge2026重新问世", "symbol": "babydoge",
         "wallets": 27, "first_buy": "2026-11-07 14:18:46 WIB, 0.000121241835356 BNB -> 9,674.63 tokens, wallet 0xcb08c02c0a, tx 0x5e45877ba389, block 132159401",
         "pair": "0x05ced0b9f08725c126e4f744ba9e58dc95c0c936 (PCS V2; token0/token1 unreadable run 98, fast_rpc outage)",
         "buys": "58 sent buys, median follow-up 0.223379 BNB, max 0.348292 BNB, total 9.8920 BNB; 100 sells",
         "verification": "name+symbol confirmed 2x via fast_rpc; totalSupply 1e27; decimals 18; DexScreener babydoge2026重新问世/babydoge, liq $0.07, pair created ~14:18 WIB"},
        {"address": "0x43bcaac4a4aa9711c2846d37fd78879435087777", "name": "funny trauma", "symbol": "trauma",
         "wallets": 27, "first_buy": "2026-11-07 14:36:24 WIB, 0.000121393351982 BNB -> 9,686.72 tokens, wallet 0xcb08c02c0a, tx 0x3242f0ef6c85, block 132161751",
         "pair": "0xb6d5522d280e3bc7770d0c3446d4dd9da06b946e (PCS V2; token0 = token, token1 = WBNB, read OK run 98)",
         "buys": "56 sent buys, median follow-up 0.228465 BNB, max 0.384561 BNB, total 9.5211 BNB; 99 sells",
         "verification": "name+symbol confirmed 2x via fast_rpc; totalSupply 1e27; decimals 18; DexScreener funny trauma/trauma, liq $0.07, pair created ~14:36 WIB"},
        {"address": "0x21209278656222412f365716863bfb5110637777", "name": "Privacy Index", "symbol": "PRIVACY",
         "wallets": 27, "first_buy": "2026-11-07 14:55:07 WIB, 0.000121125 BNB -> 9,665.31 tokens, wallet 0x362396125a, tx 0xcc8d4a5f4b7b, block 132164246",
         "pair": "0xef9bf0f21e5f3bd8c9ca1fb13090e3dad2436520 (PCS V2; token0 = token, token1 = WBNB, read OK run 98)",
         "buys": "58 sent buys, median follow-up 0.223379 BNB, max 0.413007 BNB, total 9.8001 BNB; 100 sells",
         "verification": "name+symbol confirmed 2x via fast_rpc; totalSupply 1e27; decimals 18; DexScreener Privacy Index/PRIVACY, liq $0.07, pair created ~14:55 WIB"},
        {"address": "0xda79bd2e54f46492ac5c44bb7d20da46a2ae7777", "name": "Eat Trade Fart", "symbol": "ETF",
         "wallets": 27, "first_buy": "2026-11-07 15:15:56 WIB, 0.000121241835356 BNB -> 9,674.63 tokens, wallet 0xcb08c02c0a, tx 0x6d1fccce0066, block 132167020",
         "pair": "0x7cb8b4530fadb0ffcede1453e1313b0dba7289a9 (PCS V2; token0 = WBNB, token1 = token, read OK run 98)",
         "buys": "58 sent buys, median follow-up 0.229933 BNB, max 0.376747 BNB, total 9.7681 BNB; 98 sells",
         "verification": "name+symbol confirmed 2x via fast_rpc; totalSupply 1e27; decimals 18; DexScreener Eat Trade Fart/ETF, liq $0.07, pair created ~15:15 WIB"},
    ],
    "set_check": "All four 27-wallet sets byte-identical to each other and diff 0 vs the run-97 c90a set (27/27 overlap). Buy sizes WITHIN class norm - NOT a size anomaly; the anomaly is name/symbol appearing on all four. Note: 2120's first buy came from 0x362396125a, not the usual first buyer 0xcb08c02c0a.",
    "auto_mint": "BLOCKED at guard (c) for all four: paid PCS tokens, no free-mint path for the user wallet; guard (a) website also unverified. No preview, no execution.",
}

s["paid_trend_run98"] = {
    "note": "Aggregate only, NOT a buy recommendation. FOUR NEW machine-token rotations at 27 wallets each - ALL NAMED (babydoge2026重新问世/babydoge, funny trauma/trauma, Privacy Index/PRIVACY, Eat Trade Fart/ETF), SECOND consecutive run with named rotations (run 97 had 2): anomaly reported once as a paid-only signal (paid_signal_run98); buy sizes in class norm. Run-97 named rotations c90a/e3a8 0 wallets (1st quiet run after debut); all five run-90 rotations 0 wallets (8th quiet run after debut); 0x1153... STALLED at 26 wallets (8th quiet run); 0x79cd... STALLED at 20 wallets (9th quiet run). 72 deployments - second straight run with deployments. Inbound run-98 window FULLY CLOSED in-run, first attempt (1450/1450, 14,328 logs, 0 hits, 0 failed).",
    "rotations": "FOUR NEW, all NAMED (anomaly): 0x41cc11074f16292f311ecac7d6702bb39b157777 (babydoge2026重新问世/babydoge, 27 wallets, first buy 14:18:46 WIB) + 0x43bcaac4a4aa9711c2846d37fd78879435087777 (funny trauma/trauma, 27 wallets, first buy 14:36:24 WIB) + 0x21209278656222412f365716863bfb5110637777 (Privacy Index/PRIVACY, 27 wallets, first buy 14:55:07 WIB) + 0xda79bd2e54f46492ac5c44bb7d20da46a2ae7777 (Eat Trade Fart/ETF, 27 wallets, first buy 15:15:56 WIB). Sets byte-identical, diff 0 vs run-97 c90a set. All paid-only with no free-mint path; auto-mint blocked at guard (c); reported once as signal per fast-path amendment (name/symbol appeared).",
    "other_paid_activity": [
        {"pattern": "31 paid tokens: 4 at 27 wallets (new named rotations), 13 at 3 wallets (all the same churn trio 0x3803/0xad94/0xc7c5, all ...7777), 8 at 2, 6 at 1; 0 overlap with run-97's 31 tokens", "wallets": "see run98-paid.json"},
        {"pattern": "Micro round-trip churn continues: 277 PCS buys (0xb6f9de95) + 446 PCS sells (0x791ac947), 459 approvals (0x095ea7b3), 26 aggregator txs (0x39ecce49); top active 0xa952... 77 txs, 0x9cdd... 72, 0xc621... 71, 0xf795... 53, 0xe9ed... 52, 0x1cce... 50", "wallets": "churn set"},
        {"pattern": "72 contract deployments by tracked wallets this run - second straight run with deployments (25 in run 97); in 4 waves ~14:17/14:35/14:52/15:11 WIB, 0x97bd895f alone 18", "wallets": "13 machine-set wallets"},
        {"pattern": "AFeng 0 txs; future1001.ai 0 txs; 0x8e96... 0 txs; 0x2325... 5 txs (4 aggregator 0x27772d13 + 1 approval); 0x3803... 39 txs (26 aggregator 0x39ecce49 + 13 approvals, churn as usual)", "wallets": "feed wallets"},
        {"pattern": "2 plain BNB transfers (input 0x, not mints): 0x3628... -> 0xc009... 0.0001255 BNB 14:57:27 WIB; 0xc7c5... -> 0x7f51... 0.0001282 BNB 15:07:45 WIB; 1 failed tx (failed PCS sell by 0xc6219468 14:42:30 WIB)", "wallets": "2 machine-set wallets"},
    ],
    "quiet": "AFeng 0 txs; future1001.ai 0 txs; 0x2325... 5 txs (4 aggregator + 1 approval); 0x8e96... 0 txs; GrokBot 0xfcd0... absent (0 wallets) - 39th consecutive quiet run (59, 61-98) after the run-60 burst; CORLA-97af 0 wallets; CORLA 0x4a9c 0 wallets; all run-64/65 ASI contracts 0 wallets; run-97 tokens 0xc90a.../0xe3a8... 0 wallets (1st quiet run after debut); run-90 tokens 0x6a25.../0x9f7e.../0x8c64.../0xc1ab.../0x1153... 0 wallets (8th quiet run after debut, down from 27/27/27/27/26); run-89 tokens 0xcfdb.../0x0cf8.../0xe68b.../0x31e4... 0 wallets (9th quiet run after debut); run-88 tokens 0x43c8.../0x3d12.../0xeae0... 0 wallets (10th quiet run after debut); run-87 tokens 0x889a.../0x4249... 0 wallets (11th quiet run after debut); run-86 tokens 0x2bfb.../0xc459... 0 wallets (12th quiet run after debut); run-85 token 0x2717... 0 wallets (13th quiet run); run-82 tokens 0xd468.../0xa6e6.../0x887c... all 0 wallets (16th quiet run after debut); run-81 tokens 0 wallets (17th quiet run); run-80 token 0 wallets (18th quiet run); 0x79cd... 0 wallets (rotation STALLED at 20, 9th quiet run after debut); all other run-66/68/69/70/71/72/73/74/75/76/77/78/79 machine tokens 0 wallets.",
}

s["inbound_log_leg_run98"] = {
    "contracts": 1450,
    "attempted": 1450,
    "completed_with_0_hits": 1450,
    "total_logs": 14328,
    "hits": 0,
    "failed": 0,
    "failed_contracts": [],
    "never_attempted": 0,
    "complete": True,
    "note": (
        "Ankr getLogs address-filtered per contract, window 132158491-132168467, from list run98-inbound-contracts.json (1450 contracts = "
        "run97 list 1374 + 72 run-98 deployments + 4 new rotation tokens). Full pass a (400, 7,166 logs, 0 failed) + b1 (200, 3,310 logs, 0 failed) + "
        "b2 (200, 563 logs, 0 failed) + b3 (650, 3,289 logs, 0 failed) = 14,328 logs, 0 hits, 0 FAILED. 7 truncated contracts, all topic-filtered "
        "to 0 logs (a: 0x1de4... AFeng sale, 0x3dca..., 0x55d398... USDT, 0x6288..., 0x636fdfa9... tracker; b1: 0x63de... AGC, 0x7857...) - same set "
        "as runs 91-97 minus 0x10b3... (not truncated this run). ALL FOUR chunks completed on FIRST attempt - no wedge, no silent death this run "
        "(cleaner than runs 94-97). Window FULLY CLOSED in-run, no retry deferred to run 99."
    ),
}

# --- next_run_note for run 99: surgical updates on the run-98 note ---
note = s["next_run_note"]
def rep(old, new, label):
    global note
    if old in note:
        note = note.replace(old, new)
        print(f"note[{label}]: replaced")
    else:
        print(f"note[{label}]: WARNING - target not found, left unchanged")

rep("Next run sent-tx window starts from block 132158491.",
    "Next run sent-tx window starts from block 132168468.", "window")
rep("15 consecutive runs - persistently unreadable, unverified not absence",
    "16 consecutive runs - persistently unreadable, unverified not absence", "pair16")
rep("(unreadable run 88, 89, 90, 91, 92, 93, 94, 95, 96 AND 97 - retry opportunistically, not an anomaly)",
    "(unreadable run 88, 89, 90, 91, 92, 93, 94, 95, 96, 97 AND 98 - retry opportunistically, not an anomaly)", "pair43c8")
rep("(token0/token1 unreadable run 89, 90, 91, 92, 93, 94, 95, 96 AND 97; 0x31e4 pair 0x60ca0aef... READ OK run 89)",
    "(token0/token1 unreadable run 89, 90, 91, 92, 93, 94, 95, 96, 97 AND 98; 0x31e4 pair 0x60ca0aef... READ OK run 89)", "pair89")
rep("NOTE: fast_rpc worked for the receipts batch in run 97 (462/462)",
    "NOTE: fast_rpc worked for the receipts batch in run 98 (827/827)", "fast_rpc_note")
rep("(2) RETRY run 98 inbound: NONE - run-97 inbound closed fully in-run (1374/1374, 12,655 logs, 0 hits; 2 failed contracts retried same-run, "
    "2/2 OK, 0 logs, 0 hits). No inbound retry carried into run 98. ",
    "(2) RETRY run 99 inbound: NONE - run-98 inbound closed fully in-run, first attempt (1450/1450, 14,328 logs, 0 hits, 0 failed). No inbound "
    "retry carried into run 99. ", "retry99")
rep("(3) Run-97 inbound list for run 98 = run97 list (1374 = run93 list + 25 run-97 deployments + 2 new rotation tokens) unless run 98's own "
    "sent pass finds new deployments to add.",
    "(3) Run-98 inbound list for run 99 = run98 list (1450 = run97 list + 72 run-98 deployments + 4 new rotation tokens) unless run 99's own "
    "sent pass finds new deployments to add.", "inbound_list")
rep("(4) Run-97 window inbound FULLY CLOSED in-run (1374/1374, 12,655 logs, 0 hits; 2 failed contracts retried same-run, 2/2 OK, 0 logs, 0 hits). "
    "Run-96 window inbound FULLY CLOSED in-run (1347/1347, 11,473 logs, 0 hits; 6 failed contracts retried same-run, 6/6 OK, 0 logs, 0 hits).",
    "(4) Run-98 window inbound FULLY CLOSED in-run, first attempt (1450/1450, 14,328 logs, 0 hits, 0 failed). "
    "Run-97 window inbound FULLY CLOSED in-run (1374/1374, 12,655 logs, 0 hits; 2 failed contracts retried same-run, 2/2 OK, 0 logs, 0 hits).",
    "window_status")
rep("(5) 0x1153607e... rotation STALLED at 26 wallets (did NOT reach 27 as expected; 0 wallets runs 91-97, 7th quiet run after debut) - watch run 98 "
    "for any resumption; do NOT treat a return as a new rotation. 0x79cd... STALLED at 20 wallets (0 wallets runs 90-97, 8th quiet run) - same.",
    "(5) 0x1153607e... rotation STALLED at 26 wallets (did NOT reach 27 as expected; 0 wallets runs 91-98, 8th quiet run after debut) - watch run 99 "
    "for any resumption; do NOT treat a return as a new rotation. 0x79cd... STALLED at 20 wallets (0 wallets runs 90-98, 9th quiet run) - same. "
    "Run-97 named rotations 0xc90a.../0xe3a8...: 0 wallets run 98 (1st quiet run after debut) - watch run 99 the same way.",
    "stalls")
rep("run 97 (TWO NEW rotations 0xc90a... Timothy/TIMOTHY + 0xe3a8... symbol BTC at 27 wallets each - FIRST NAMED machine-token rotations, "
    "anomaly reported once as signal run 97; buy sizes in class norm; 0x1153... STALLED at 26, 7th quiet run; 0x79cd... STALLED at 20, 8th quiet "
    "run; 25 deployments (first in 7 runs); inbound FULLY CLOSED in-run, 1374 contracts, 12,655 logs, 0 hits, 2 failed retried same-run 2/2 OK; "
    "first-attempt chunks WEDGED on proxy sockets ~contract 10, killed by PID + re-launched from scratch) ",
    "run 97 (TWO NEW rotations 0xc90a... Timothy/TIMOTHY + 0xe3a8... symbol BTC at 27 wallets each - FIRST NAMED machine-token rotations, "
    "anomaly reported once as signal run 97; buy sizes in class norm; 0x1153... STALLED at 26, 7th quiet run; 0x79cd... STALLED at 20, 8th quiet "
    "run; 25 deployments (first in 7 runs); inbound FULLY CLOSED in-run, 1374 contracts, 12,655 logs, 0 hits, 2 failed retried same-run 2/2 OK; "
    "first-attempt chunks WEDGED on proxy sockets ~contract 10, killed by PID + re-launched from scratch) "
    "run 98 (FOUR NEW rotations 0x41cc... babydoge2026/babydoge + 0x43bc... funny trauma/trauma + 0x2120... Privacy Index/PRIVACY + 0xda79... Eat "
    "Trade Fart/ETF at 27 wallets each - ALL NAMED, second consecutive run with named rotations, anomaly reported once as signal run 98; buy "
    "sizes in class norm; c90a/e3a8 0 wallets (1st quiet run); 0x1153... STALLED at 26, 8th quiet run; 0x79cd... STALLED at 20, 9th quiet run; "
    "72 deployments (second straight run with deployments, 0x97bd895f alone 18); inbound FULLY CLOSED in-run FIRST ATTEMPT, 1450 contracts, "
    "14,328 logs, 0 hits, 0 failed; sent pass attempt 1 SIGTERM at 37/55, re-run from scratch 55/55 OK) ", "history98")
rep("Paid fact: run97 TWO NEW rotations 0xc90a... (Timothy/TIMOTHY) + 0xe3a8... (symbol BTC) at 27 wallets each - FIRST NAMED machine-token rotations "
    "(anomaly: name/symbol appeared; reported once as signal run 97, paid-only, auto-mint blocked guard (c)); run-90 tokens 0x6a25.../0x9f7e.../0x8c64.../0xc1ab.../0x1153... 0 wallets (7th quiet run after debut); run-89 tokens 0xcfdb.../0x0cf8.../0xe68b.../0x31e4... 0 wallets (8th quiet run after debut); run-88 tokens 0x43c8.../0x3d12.../0xeae0... 0 wallets (9th quiet run after debut); run-87 tokens 0x889a.../0x4249... 0 wallets (10th quiet run after debut); run-86 tokens "
    "0x2bfb.../0xc459... 0 wallets (11th quiet run after debut); run-85 token 0x2717... 0 wallets (12th quiet run); run-82 tokens 0xd468.../0xa6e6.../0x887c... "
    "all 0 wallets (15th quiet run after debut); run-81 tokens 0 wallets (16th quiet run); run-80 token 0 wallets (17th quiet run); "
    "GrokBot 0xfcd0... absent (0 wallets) - 38th consecutive quiet run (59, 61-97) after the run-60 burst;",
    "Paid fact: run98 FOUR NEW rotations 0x41cc... (babydoge2026/babydoge) + 0x43bc... (funny trauma/trauma) + 0x2120... (Privacy Index/PRIVACY) + "
    "0xda79... (Eat Trade Fart/ETF) at 27 wallets each - ALL NAMED, second consecutive run with named rotations (anomaly: name/symbol appeared; "
    "reported once as signal run 98, paid-only, auto-mint blocked guard (c)); run-97 tokens 0xc90a.../0xe3a8... 0 wallets (1st quiet run after "
    "debut); run-90 tokens 0x6a25.../0x9f7e.../0x8c64.../0xc1ab.../0x1153... 0 wallets (8th quiet run after debut); run-89 tokens 0xcfdb.../0x0cf8.../0xe68b.../0x31e4... 0 wallets (9th quiet run after debut); run-88 tokens 0x43c8.../0x3d12.../0xeae0... 0 wallets (10th quiet run after debut); run-87 tokens 0x889a.../0x4249... 0 wallets (11th quiet run after debut); run-86 tokens "
    "0x2bfb.../0xc459... 0 wallets (12th quiet run after debut); run-85 token 0x2717... 0 wallets (13th quiet run); run-82 tokens 0xd468.../0xa6e6.../0x887c... "
    "all 0 wallets (16th quiet run after debut); run-81 tokens 0 wallets (17th quiet run); run-80 token 0 wallets (18th quiet run); "
    "GrokBot 0xfcd0... absent (0 wallets) - 39th consecutive quiet run (59, 61-98) after the run-60 burst;", "paid_fact")
rep("Run 97 had 25 deployments (first deployments after 6 straight zero runs 91-96; all 13:59:08-13:59:47 WIB by 11 machine-set wallets, "
    "0x97bd895f alone 11; added to the inbound list for run 98).",
    "Run 98 had 72 deployments (second straight run with deployments; in 4 waves ~14:17/14:35/14:52/15:11 WIB by 13 machine-set wallets, "
    "0x97bd895f alone 18; added to the inbound list for run 99).", "deployments")
rep("AFeng 2 txs (1 sale-call 0x4d819a2a to 0x1de4... value 0, status 1, 13 logs, 0 mint logs - a sale, NOT a mint + 1 approval to SLIME 0x8351311f...); future1001.ai 0 txs; 0x2325... 2 txs (1 aggregator 0x27772d13 + 1 approval, value 0); 0x8e96... 0 txs; 0x3803... 42 txs (28 aggregator 0x39ecce49 + 14 approvals, total value 0.000364 BNB, churn as usual).",
    "AFeng 0 txs; future1001.ai 0 txs; 0x2325... 5 txs (4 aggregator 0x27772d13 + 1 approval); 0x8e96... 0 txs; 0x3803... 39 txs (26 aggregator 0x39ecce49 + 13 approvals, churn as usual).", "activity")
rep("PROCESS LESSON (run 86): the receipts pass died silently at 420/461 (service-restart pattern, same as runs 82/84) - the partial-file resume worked; "
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
    "PROCESS LESSON (run 86): the receipts pass died silently at 420/461 (service-restart pattern, same as runs 82/84) - the partial-file resume worked; "
    "always re-run the same script to resume rather than re-fetching from scratch. Run 98 receipts completed in one attempt, no resume needed; "
    "sent pass attempt 1 was SIGTERM-killed at wallet 37/55 (service restart, no JSON saved since the script dumps only at the end) - re-run from "
    "scratch completed 55/55 OK; inbound chunks ALL FOUR completed on FIRST attempt (no wedge, no silent death - cleaner than runs 94-97). "
    "A frozen log mtime with a live process is a stall, not a death - wait before re-running; a log frozen >5 min with NO live process is a "
    "silent death - re-run the chunk from scratch; a socket wedged >5 min while fresh calls work is a wedge - kill by PID (pkill -f can match "
    "the wrapper shell itself, use kill <pid>) and re-run the chunk from scratch.",
    "process_lesson")
rep("(all five pairs' token0/token1 READ OK in run-90 token-verify via fast_rpc race - do NOT re-read unless a new question arises; the retry list above is for the pairs that are still unreadable). "
    "PLUS new run-97 rotation pairs 0xc90a 0x066aa46ee270d041353749ee9ae485323bd6e6d1, 0xe3a8 0xa39db5002d7ee3dc4596243789702ff4fab993f4 (token0/token1 unreadable "
    "run 97, fast_rpc 'all endpoints failed' - unverified, not absence; pair addresses known from first-buy logs; retry opportunistically run 98).",
    "(all five pairs' token0/token1 READ OK in run-90 token-verify via fast_rpc race - do NOT re-read unless a new question arises; the retry list above is for the pairs that are still unreadable). "
    "Run-97 rotation pairs 0xc90a 0x066aa46ee270d041353749ee9ae485323bd6e6d1, 0xe3a8 0xa39db5002d7ee3dc4596243789702ff4fab993f4 READ OK run 98 "
    "(token0 WBNB 0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c, token1 = the token) - REMOVED from the retry list. "
    "PLUS new run-98 rotation pairs 0x41cc 0x05ced0b9f08725c126e4f744ba9e58dc95c0c936 (token0/token1 UNREADABLE run 98, fast_rpc 'all endpoints failed' - "
    "unverified, not absence; retry run 99), 0x43bc 0xb6d5522d280e3bc7770d0c3446d4dd9da06b946e (READ OK run 98: token0 = token, token1 = WBNB), 0x2120 "
    "0xef9bf0f21e5f3bd8c9ca1fb13090e3dad2436520 (READ OK run 98: token0 = token, token1 = WBNB), 0xda79 0x7cb8b4530fadb0ffcede1453e1313b0dba7289a9 "
    "(READ OK run 98: token0 = WBNB, token1 = token).",
    "pairs98")
s["next_run_note"] = note

json.dump(s, open(P, "w"), indent=1)
print("state updated; last_run now:", s["last_run"]["run"], "block_end:", s["last_run"]["block_end"])
print("machine_tokens:", len(s.get("machine_tokens", [])), "| signaled:", len(s.get("signaled_projects_over_20pct", [])))
print("inbound98 complete:", s["inbound_log_leg_run98"]["complete"], "| failed:", s["inbound_log_leg_run98"]["failed"])
print("inbound97 complete:", s["inbound_log_leg_run97"]["complete"], "| failed:", s["inbound_log_leg_run97"]["failed"])
