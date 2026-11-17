#!/usr/bin/env python3
"""Run 103 state update (read-only job bookkeeping; no chain writes).

Completes run 103 (window 132224206-132238464, tx 2026-11-07 22:27:12 - 2026-11-08 00:11:54 WIB).
Sent/receipts/paid done and verified; inbound leg run-103 window CLOSED in-run
(1734/1734, 0 hits, 0 failed after same-run retry of 5 failed contracts).
NO new mints - ZERO mint-pattern txs (0 mint logs in 718 receipts; no dividend-tracker
repeats this run, unlike runs 70/75/101/102). THREE NEW machine-token rotations at 27
wallets each - ALL NAMED (DiamondPepe69 / PEPE69 + BTC / 比特币 + propfun / PROPFUN),
the SEVENTH consecutive run with named rotations (run 97 had 2, run 98 had 4, run 99 had 4,
run 100 had 2, run 101 had 2, run 102 had 4, run 103 has 3): anomaly under the fast-path
amendment, reported ONCE as a paid-only signal (not a lead, not a buy recommendation,
auto-mint blocked at guard (c)). 68 deployments this run (seventh straight run with
deployments; 25/72/64/32/35/70/68). Bridge unchanged (0 new mints, 0 not_evaluated).
Pair retry 15/15 FAILED (fast_rpc race outage total) - all 15 pairs unverified, retry run 104.
"""
import json, shutil

P = "/home/hatch/workspace/narrative-pulse/tracked-wallet-mint-scan-state.json"
shutil.copy(P, str(P) + ".bak-run103-pre")
s = json.load(open(P))
SR = "/home/hatch/workspace/narrative-pulse/scan-runs"

# ---- inbound totals from chunk JSONs (self-verifying) ----
chunks = {}
for part in ["a", "b1", "b2", "b3"]:
    chunks[part] = json.load(open(f"{SR}/run103-inbound103-{part}.json"))
tot_contracts = sum(c["contracts_checked"] for c in chunks.values())
tot_logs = sum(c["total_logs"] for c in chunks.values())
tot_hits = sum(len(c["hits"]) for c in chunks.values())
tot_failed = sum(len(c["failed"]) for c in chunks.values())
tot_trunc = sum(len(c["truncated"]) for c in chunks.values())
print(f"inbound totals: contracts={tot_contracts} logs={tot_logs} hits={tot_hits} failed={tot_failed} truncated={tot_trunc}")
assert tot_contracts == 1734, f"inbound contracts {tot_contracts} != 1734"
assert tot_hits == 0, f"inbound hits {tot_hits} != 0 (must handle before state update!)"
failed_contracts = [f for c in chunks.values() for f in c["failed"]]
retry_path = f"{SR}/run103-inbound103-retry.json"
retry = json.load(open(retry_path))
retry_failed_addrs = {f["contract"] for f in failed_contracts}
assert retry["contracts_checked"] == len(retry_failed_addrs), "retry did not cover all failed contracts"
assert retry["failed"] == [], f"retry itself failed: {retry['failed']}"
assert retry["hits"] == [], "retry found hits - must handle before state update!"
print(f"same-run retry recovered {len(retry_failed_addrs)}/{len(retry_failed_addrs)} failed contract(s): "
      f"{sorted(retry_failed_addrs)} -> {retry['total_logs']} logs, 0 hits")
eff_failed = 0
tot_logs_effective = tot_logs + retry["total_logs"]

last_run_103 = {
    "run": 103,
    "block_start": 132224206,
    "block_end": 132238464,
    "window_wib": "2026-11-07 22:27:12 - 2026-11-08 00:11:54 WIB (tx times); run executed ~00:05 WIB - ~01:50 WIB; sent-pass in-window txs 1103, 0 mint-pattern txs (0 new mints - no dividend-tracker repeats this run, see method_note)",
    "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set); 0 failed first attempt, 35 wallets active.",
    "method_note": (
        "Sent pass Ankr ankr_getTransactionsByAddress via module: 55/55 OK first attempt (1103 txs), 0 failed, 35 wallets active. "
        "Receipts via fast_rpc batch (6, ~4s pause) for 718 non-approve candidates: 711 status 1, 7 status 0 (ALL failed PCS sells 0x791ac947: "
        "0xdb2d83f9 23:21:16 WIB tx 0xb273dca2... + 22:56:58 WIB tx 0x34fa784d..., 0xc6219468 23:02:28 WIB tx 0xf195c66d... + 22:35:33 WIB tx 0xb8200aec..., "
        "0xa952331e 22:59:06 WIB tx 0x5b758f10... + 22:36:36 WIB tx 0x196dba98..., 0xfdec62fd 23:21:33 WIB tx 0x0147a9f5...), 0 NULL. Receipts pass ran slow "
        "(~35 min) because the fast_rpc race outage forced batch failures into per-tx race fallbacks. "
        "Mint-pattern txs: 0 - ZERO mint logs in 718 receipts. No new mints of any kind. AFeng's 10 sale-calls (total 3.0 BNB) carried NO zero-from Transfer "
        "to a tracked wallet this run - the dividend-tracker mint pattern of runs 70/75/101/102 did NOT repeat. "
        "Paid: 47 tokens; max 27 wallets/token (THREE new rotations at 27 each - see anomaly signal; 21 tokens at 3 wallets, ALL the same churn trio "
        "0x3803/0xad94/0xc7c5, all ...7777; 10 at 2 (ALL the 0x3628/0xa0c1 pair); 13 at 1). Overlap with run-102 paid tokens: only 1 "
        "(0x415aac3e46264c046d103c994a1da71f05c547f9, a ...7777 churn token) - the ...7777 churn set turns over almost completely every run. "
        "NEW ROTATIONS - ANOMALY (named tokens, SEVENTH consecutive run - run 97 had 2 named, run 98 had 4, run 99 had 4, run 100 had 2, run 101 had 2, run 102 "
        "has 4, run 103 has 3): 0x780967274cca69ee9e64cf6546488830c03f7777 (DiamondPepe69 / PEPE69), 0x7f0a67b94ee0faf41d0ee352a44f0fc94e8e7777 (BTC / 比特币), "
        "0xf3bdc9ef1343fa3ef7c555414e9cc2a5e5537777 (propfun / PROPFUN). "
        "All: name+symbol+totalSupply+decimals confirmed via fast_rpc, totalSupply 1e27, decimals 18. DexScreener independently confirms all three (PCS V2 token/WBNB pairs, "
        "liquidity $0.07 each - drained after the rotation's sells): PEPE69 pair created 23:20:04 WIB (38s before first buy), vol24 $18,764.65, txns h24 buys 85/sells 133; "
        "BTC pair created 22:55:49 WIB (35s before first buy), vol24 $17,708.50, txns h24 buys 81/sells 134; PROPFUN pair created 22:33:12 WIB (42s before first buy), vol24 $18,020.59, "
        "txns h24 buys 83/sells 133. "
        "All three bought by the SAME 27-wallet machine set, byte-identical to each other and diff 0 vs the run-102 machine set (27/27 overlap with 4263 wallets). "
        "Buy sizes WITHIN class norm (NOT a size anomaly): first buy 0.000123025 BNB -> 9,816.72 tokens (7809) / 9,826.24 tokens (7f0a) / 0.000123142 BNB -> 9,826.04 tokens (f3bd); "
        "follow-up medians 0.224256584 (7809) / 0.2337475 (7f0a) / 0.226420430 (f3bd); max 0.351022 (7809) / 0.347077 (7f0a) / 0.401811 (f3bd); "
        "totals 9.3775 / 9.0140 / 9.2594 BNB; buys 54/50/53, sells 95/96/95 (sell wallets 27/27/27 - ALL THREE fully dumped in-window). First buys: "
        "7809 23:20:42 WIB by 0x36239612 (future1001.ai) tx 0x1c83fe90f4... block 132231639 pair 0xfaba06b92f8e425055417fac8388dedf1cd58a72; "
        "7f0a 22:56:24 WIB by 0xcb08c02c0a tx 0x81549ae212... block 132228400 pair 0x25a1bf1d836ba5865d9ba1dfaea33c33ad06c754; "
        "f3bd 22:33:54 WIB by 0xcb08c02c0a tx 0x45550f4238... block 132225398 pair 0xbf243f454ac1463f2b596d9843026299e0ea5e31. Pair token0/token1: NOT read this "
        "run (fast_rpc race outage total) - retry run 104; DexScreener confirms all three are PCS V2 token/WBNB pairs. Trigger >25% met numerically (27 >= 14) but AUTO-MINT BLOCKED at guard (c): "
        "paid PCS tokens, no free-mint path; guard (a) website also unverified. No preview, no execution. "
        "Seatbelt 1e9c STALLED at 26: 0 wallets this run (0 buys, 0 sells) - sell-wallet union run101+run102 = 26/27, run 103 adds 0 - did NOT reach 27. NOT a new rotation; watch run 104 the same way. "
        "Deployments: 68 contract creations by 16 machine-set wallets (0x64e893a4 9; 0x1cce4ec5/0xc0c84518/0x97bd895f 6 each; 0x3a39aa05/0x5b4beded/0x9b519f5d 5 each; "
        "0xaa49e7fe/0x3154f694/0xcb08c02c 4 each; 0xc6219468/0xf795c525 3 each; 0xdb2d83f9/0xa952331e/0x92bc3297 2 each; 0x36239612/0xfdec62fd 1 each) - SEVENTH straight run with deployments "
        "(25 run 97, 72 run 98, 64 run 99, 32 run 100, 35 run 101, 70 run 102, 68 run 103); all 68 deployed addresses recovered from RAW receipts "
        "(run103-receipts-partial.json), added to the inbound list (run103-inbound-contracts.json, total 1734) along with the 3 new rotation tokens. The 3 rotation "
        "tokens are NOT among the deployments. "
        "AFeng (0xbf004bff...) 16 txs (10 sale-calls 0x4d819a2a + 5 approvals + 1 transfer 0xa9059cbb, total value 3.0 BNB - much smaller than run 102's 34.4 BNB; "
        "sale values 0.075, 0.325, 0.65, 0.75, 1.2 + five 0); future1001.ai (0x36239612...) 13 txs (4 PCS buys of the new rotations + 3 sells + 3 approvals + 1 contract creation "
        "0.0198 BNB, total value ~0.72 BNB - first buyer of the 0x7809 rotation); 0x2325... 6 txs (4 aggregator 0x27772d13 + 2 approvals, total value 0.21 BNB); "
        "0x8e96... 0 txs; 0x6ba79dcc/0x89220022/0xda91cefe 0 txs; 0x3803... 65 txs (44 aggregator 0x39ecce49 + 21 approvals, total value 0.0005 BNB, churn as usual); "
        "0xad94... 65 txs (21 buys + 23 sells + 21 approvals, 0.0007 BNB); 0xc7c5... 68 txs (21 buys + 23 sells + 23 approvals + 1 plain, 0.0028 BNB). 1 plain BNB "
        "transfer (0xc7c5..., empty input). "
        "Selectors (sent pass, 1103 txs): 385 approvals (0x095ea7b3) + 364 PCS sells (0x791ac947) + 226 PCS buys (0xb6f9de95) + 68 contract creations (0x60806040) + "
        "44 aggregator (0x39ecce49) + 10 sale-calls (0x4d819a2a, AFeng) + 4 aggregator (0x27772d13) + 1 empty-input (plain BNB transfer) + 1 transfer (0xa9059cbb). "
        "Nonzero-value txs 323, total 33.4966 BNB, max 1.2 BNB (AFeng sale-call 0x57d8b8548870ac50c81308baf04e02ca8829241825f3b842d7c779f554e4005c, 22:55:15 WIB). Most active wallets: "
        "0xc7c5faa2 68 txs, 0xad94ee77 65, 0x38031ca8 65, 0x9cdd08f3 54, 0xa952331e 51, 0xc6219468 45, 0xf795c525 39, 0xe9ed24db 39, 0x1cce4ec5 39, 0x92bc3297 38, "
        "0x9b519f5d 38, 0xc0c84518 36. "
        "0 NULL receipts this run. 7 status-0 txs, all failed PCS sells (see above). "
        f"Inbound leg (amendment 12:02 WIB): Ankr getLogs address-filtered per contract, 1734 contracts (run102 list 1663 + 68 run-103 deployments + "
        f"3 new rotation tokens), 0 hits, {tot_logs_effective} logs, window 132224206-132238464. "
        f"Chunk a (400, 7,477 logs, 1 failed, 5 truncated) + b1 (200, 3,726 logs, 1 failed, 3 truncated) + b2 (200, 1,641 logs, 1 failed, 0 truncated) + "
        f"b3 (934, 2,870 logs, 2 failed, 0 truncated) + retry (5 contracts, 18 logs, 0 failed - the 5 in-chunk failures 0x0c4370ed..., 0x688ffc04..., "
        f"0x9f1e4d41..., 0xd06518ea..., 0x4aad13d4... recovered same-run 5/5) = {tot_logs_effective} logs, 0 hits, 0 FAILED after retry. "
        "Truncated contracts, all topic-filtered to 0 logs (a: 0x10b3... moco, 0x1de4... AFeng sale, 0x55d398... USDT, 0x6288... AGC sale, 0x636fdfa9... tracker; "
        "b1: 0x63de... AGC, 0x7857..., 0x7e2d...; b2/b3: none). "
        "First-attempt chunks ALL WEDGED on proxy sockets (every chunk hit Ankr 'Remote end closed connection' on contract #1-2, only ~2 contracts in ~12 min) - killed by PID + "
        "re-launched from scratch as -2 (pkill -f matched the wrapper shell itself and SIGTERM'd the launcher - use kill <pid>, per the run-101 lesson; the compound nohup launch only "
        "started chunk a, b1/b2/b3 needed separate launches). -2 chunks completed: a 400, b1/b2 200 each, b3 934 (~50 contracts/5 min, Ankr ~10s/call). "
        "Window FULLY CLOSED in-run, no retry deferred to run 104. "
        "Pair a6e6/887c/2bfb/c459/43c8/cfdb/0cf8/e68b STILL unreadable: token0()/token1() for all eight pairs failed via fast_rpc race "
        "('all endpoints failed' / OSError / TimeoutError) in run103-pair-retry.py - unverified, not absence; 21st consecutive run for a6e6/887c/2bfb/c459, 16th for 43c8, "
        "15th for cfdb/0cf8/e68b; retry run 104. Run-102 pairs 8b19/d826/07b2/4263 ALSO failed again (2nd attempt) - retry run 104. New run-103 pairs 7809 0xfaba06b9... + "
        "7f0a 0x25a1bf1d... + f3bd 0xbf243f45... NOT read (fast_rpc race outage TOTAL this run: 15/15 pairs failed) - retry run 104. "
        "fast_rpc race OUTAGE TOTAL this run (~00:25-00:45 WIB): all-endpoint TimeoutError/OSError on every pair-retry call (15/15 failed); receipts pass batch failures forced "
        "slow per-tx race fallbacks (~35 min); token-meta calls succeeded earlier in the run (12 calls, ~19s) - the outage is time-varying, not permanent. "
        "A failed race read is UNVERIFIED, never absence - retry, don't conclude. "
        "Pointer-discovery (amendment 19:10): 0 contracts processed - no new mints this run, and the backfill queue is empty (bridge 115 contracts, "
        "0 not_evaluated); bridge unchanged. CHAT REPORT this run: the three-named-machine-token anomaly signal (paid-only, NOT a lead, NOT a buy "
        "recommendation, auto-mint blocked guard (c)) - reported once per the fast-path amendment. No new mints, no Free Bacot signal beyond that, "
        "no auto-mint trigger execution. No preview/mint/sign/login/purchase by this job."
    ),
}
s["last_run"] = last_run_103

# ---- paid signal + trend ----
s["paid_signal_run103"] = {
    "note": "ANOMALY SIGNAL (paid-only, NOT a buy recommendation, NOT a Free Bacot lead, NOT an auto-mint trigger). SEVENTH consecutive run with NAMED "
            "machine-token rotations - now THREE at once (run 97 had 2, run 98 had 4, run 99 had 4, run 100 had 2, run 101 had 2, run 102 had 4, run 103 has 3): the machine set bought THREE tokens "
            "that HAVE on-chain name/symbol, breaking the unnamed pattern of all 24 pre-run-97 machine tokens. Reported once per the fast-path "
            "amendment (name/symbol appeared). Auto-mint BLOCKED at guard (c) for all three (paid PCS tokens, no free-mint path). Do not re-signal "
            "unless a new fact appears (e.g. a genuine free-mint path).",
    "tokens": [
        {
            "address": "0x780967274cca69ee9e64cf6546488830c03f7777",
            "name": "DiamondPepe69",
            "symbol": "PEPE69",
            "wallets": 27,
            "first_buy": "2026-11-07 23:20:42 WIB, 0.000123025 BNB -> 9,816.72 tokens, wallet 0x36239612 (future1001.ai), tx 0x1c83fe90f4..., block 132231639",
            "pair": "0xfaba06b92f8e425055417fac8388dedf1cd58a72 (PCS V2; token0/token1 NOT read run 103 - retry run 104; DexScreener confirms token/WBNB pair)",
            "buys": "54 sent buys, median follow-up 0.224256584 BNB, max 0.351022 BNB, total 9.3775 BNB; 95 sells / 27 sell wallets (fully dumped in-window)",
            "verification": "name+symbol+totalSupply+decimals confirmed via fast_rpc; totalSupply 1e27; decimals 18; DexScreener DiamondPepe69/PEPE69, pair created 23:20:04 WIB, vol24 $18,764.65, txns h24 buys 85/sells 133, liquidity $0.07 (drained after the rotation's sells)",
        },
        {
            "address": "0x7f0a67b94ee0faf41d0ee352a44f0fc94e8e7777",
            "name": "BTC",
            "symbol": "比特币",
            "wallets": 27,
            "first_buy": "2026-11-07 22:56:24 WIB, 0.000123025 BNB -> 9,826.24 tokens, wallet 0xcb08c02c0a, tx 0x81549ae212..., block 132228400",
            "pair": "0x25a1bf1d836ba5865d9ba1dfaea33c33ad06c754 (PCS V2; token0/token1 NOT read run 103 - retry run 104; DexScreener confirms token/WBNB pair)",
            "buys": "50 sent buys, median follow-up 0.2337475 BNB, max 0.347077 BNB, total 9.0140 BNB; 96 sells / 27 sell wallets (fully dumped in-window)",
            "verification": "name+symbol+totalSupply+decimals confirmed via fast_rpc; totalSupply 1e27; decimals 18; DexScreener BTC/比特币, pair created 22:55:49 WIB, vol24 $17,708.50, txns h24 buys 81/sells 134, liquidity $0.07 (drained after the rotation's sells)",
        },
        {
            "address": "0xf3bdc9ef1343fa3ef7c555414e9cc2a5e5537777",
            "name": "propfun",
            "symbol": "PROPFUN",
            "wallets": 27,
            "first_buy": "2026-11-07 22:33:54 WIB, 0.000123142 BNB -> 9,826.04 tokens, wallet 0xcb08c02c0a, tx 0x45550f4238..., block 132225398",
            "pair": "0xbf243f454ac1463f2b596d9843026299e0ea5e31 (PCS V2; token0/token1 NOT read run 103 - retry run 104; DexScreener confirms token/WBNB pair)",
            "buys": "53 sent buys, median follow-up 0.226420430 BNB, max 0.401811 BNB, total 9.2594 BNB; 95 sells / 27 sell wallets (fully dumped in-window)",
            "verification": "name+symbol+totalSupply+decimals confirmed via fast_rpc; totalSupply 1e27; decimals 18; DexScreener propfun/PROPFUN, pair created 22:33:12 WIB, vol24 $18,020.59, txns h24 buys 83/sells 133, liquidity $0.07 (drained after the rotation's sells)",
        },
    ],
}

s["paid_trend_run103"] = {
    "note": "Aggregate only, NOT a buy recommendation. THREE NEW machine-token rotations at 27 wallets each - ALL NAMED (DiamondPepe69/PEPE69, BTC/比特币, propfun/PROPFUN), "
            "SEVENTH consecutive run with named rotations (run 97 had 2, run 98 had 4, run 99 had 4, run 100 had 2, run 101 had 2, run 102 had 4, run 103 has 3): anomaly reported once as a paid-only signal "
            "(paid_signal_run103); buy sizes in class norm; all three fully dumped in-window (95-96 sells, 27 sell wallets each). "
            "Seatbelt 1e9c STALLED at 26/27 sell wallets (union run101+run102; 0 wallets run 103) - did NOT reach 27. "
            "Run-102 named rotations 8b19/d826/07b2/4263: 0 wallets (1st quiet run after debut); run-101 named rotations 4727 0 wallets (2nd quiet run after debut); run-100 named rotations 6f31/0d7e 0 wallets (3rd quiet run after debut); "
            "run-99 named rotations 50e4/6b12/ff66 0 wallets (4th quiet run after debut); "
            "run-98 named rotations 41cc/43bc/2120/da79 0 wallets (6th quiet run after debut); run-97 named rotations c90a/e3a8 0 wallets (6th quiet run after debut); "
            "0x1153... STALLED at 26 wallets (13th quiet run); 0x79cd... STALLED at 20 wallets (14th quiet run). 68 deployments - seventh straight run with deployments. Inbound run-103 window FULLY CLOSED in-run "
            f"(1734/1734, {tot_logs_effective} logs, 0 hits, 0 failed after same-run retry of 5 failed contracts).",
    "rotations": "THREE NEW, all NAMED (anomaly): 0x780967274cca69ee9e64cf6546488830c03f7777 (DiamondPepe69/PEPE69, 27 wallets, first buy 23:20:42 WIB) + "
                 "0x7f0a67b94ee0faf41d0ee352a44f0fc94e8e7777 (BTC/比特币, 27 wallets, first buy 22:56:24 WIB) + "
                 "0xf3bdc9ef1343fa3ef7c555414e9cc2a5e5537777 (propfun/PROPFUN, 27 wallets, first buy 22:33:54 WIB). Sets byte-identical, diff 0 vs "
                 "run-102 machine set. All paid-only with no free-mint path; auto-mint blocked at guard (c); reported once as signal per fast-path "
                 "amendment (name/symbol appeared). Seatbelt 1e9c rotation STALLED at 26/27 sell wallets (union run101+run102; 0 wallets run 103) - watch run 104 the same way, NOT a new rotation.",
    "other_paid_activity": [
        {
            "pattern": "21 tokens x 3 wallets, all the same churn trio 0x3803/0xad94/0xc7c5, all ...7777 (PCS micro buy-then-sell)",
            "wallet": "churn trio (see paid_trend_run1 for the pattern)",
        },
        {
            "pattern": "10 tokens x 2 wallets, both 0x3628764a6576b8dfb31fba0aac6a333b64851423 + 0xa0c1e94fbc1a93e39f5eb828f960aa080a9d9b9e, all ...7777",
            "wallet": "0x3628764a6576b8dfb31fba0aac6a333b64851423 + 0xa0c1e94fbc1a93e39f5eb828f960aa080a9d9b9e",
        },
        {
            "pattern": "13 tokens x 1 wallet (PCS micro buys)",
            "wallet": "see pattern",
        },
        {
            "pattern": "4 txs via 0x296b00198dc7ec3410e12da814d9267bb8df506a (selector 0x27772d13), receiving tokens from pair contracts (swap-like, not mints); values 0 / 0 / 0.03 / 0.18 BNB, total 0.21 BNB",
            "wallet": "0x2325f175975abdbcde555c79cc8e63381d28551b",
        },
        {
            "pattern": "44 txs via aggregator 0x855066c8679c77a0258e792b5ccf19f8c227eb31 (selector 0x39ecce49) + 21 approvals, total value 0.0005 BNB (churn as usual)",
            "wallet": "0x38031ca8a54526f9fe90f11f07b55ae5fc01036a",
        },
        {
            "pattern": "10 AFeng sale-calls (0x4d819a2a) to 0x1de4... total 3.0 BNB (much smaller than run 102's 34.4 BNB; values 0.075/0.325/0.65/0.75/1.2 + five 0) - NONE carried a dividend-tracker mint log this run (pattern did not repeat)",
            "wallet": "0xbf004bff64725914ee36d03b87d6965b0ced4903 (AFeng)",
        },
    ],
}

s["inbound_log_leg_run103"] = {
    "contracts": 1734,
    "attempted": 1734,
    "completed_with_0_hits": 1734,
    "total_logs": tot_logs_effective,
    "hits": 0,
    "failed": eff_failed,
    "failed_contracts": [],
    "failed_then_recovered_same_run": failed_contracts,
    "never_attempted": 0,
    "complete": eff_failed == 0,
    "note": "Ankr getLogs address-filtered per contract, window 132224206-132238464, from list run103-inbound-contracts.json (1734 contracts = run102 list "
            f"1663 + 68 run-103 deployments + 3 new rotation tokens). Full pass a (400, 7,477 logs, 1 failed, 5 truncated) + "
            f"b1 (200, 3,726 logs, 1 failed, 3 truncated) + b2 (200, 1,641 logs, 1 failed, 0 truncated) + b3 (934, 2,870 logs, "
            f"2 failed, 0 truncated) + retry (5 contracts, 18 logs, 0 hits - the 5 in-chunk failures 0x0c4370ed..., 0x688ffc04..., 0x9f1e4d41..., "
            f"0xd06518ea..., 0x4aad13d4... recovered 5/5 same-run) = {tot_logs_effective} logs, 0 hits, 0 FAILED after retry. "
            "Truncated contracts, all topic-filtered to 0 logs (a: 0x10b3... moco, 0x1de4... AFeng sale, 0x55d398... USDT, 0x6288... AGC sale, 0x636fdfa9... tracker; "
            "b1: 0x63de... AGC, 0x7857..., 0x7e2d...; b2/b3: none). "
            "First-attempt chunks ALL WEDGED on proxy sockets (every chunk hit Ankr 'Remote end closed connection' on contract #1-2, only ~2 contracts in ~12 min) - "
            "killed by PID + re-launched from scratch as -2; -2 chunks completed. "
            "Window FULLY CLOSED in-run, no retry deferred to run 104."
            if eff_failed == 0 else
            "Window NOT fully closed: failed contracts must be retried in run 104.",
}

# ---- machine tokens: 3 new entries ----
new_entries = [
    {
        "address": "0x780967274cca69ee9e64cf6546488830c03f7777",
        "first_seen": "run-103, 2026-11-07 23:20:42 WIB (tx 0x1c83fe90f4..., block 132231639)",
        "machine_wallets": 27,
        "typical_first_buy_bnb": 0.000123025,
        "followup_buy_range_bnb": "median 0.224256584, max 0.351022, total buys 9.3775 BNB (54 sent buys)",
        "label": "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - NAMED (DiamondPepe69 / PEPE69) - ANOMALY, reported once as signal run 103",
        "note": "ANOMALY under the fast-path amendment: name/symbol APPEARED - name 'DiamondPepe69', symbol 'PEPE69', confirmed via fast_rpc; totalSupply 1e27; "
                "decimals 18. DexScreener independently confirms DiamondPepe69/PEPE69, pair 0xfaba06b92f8e425055417fac8388dedf1cd58a72, pair created 23:20:04 WIB, "
                "vol24 $18,764.65, txns h24 buys 85/sells 133, liquidity $0.07 (drained after the rotation's sells). "
                "First buy 23:20:42 WIB by 0x36239612 (future1001.ai), 0.000123025 BNB -> 9,816.72 tokens. Wallet set byte-identical to the other run-103 rotations and diff 0 "
                "vs the run-102 machine set (27/27 overlap). Buy sizes WITHIN class norm - NOT a size anomaly. 95 sells / 27 sell wallets in-window - rotation "
                "fully dumped. Pair token0/token1 NOT read run 103 - retry run 104. Auto-mint BLOCKED at guard (c) - paid PCS token, "
                "no free-mint path. Do not re-signal unless a new fact appears.",
    },
    {
        "address": "0x7f0a67b94ee0faf41d0ee352a44f0fc94e8e7777",
        "first_seen": "run-103, 2026-11-07 22:56:24 WIB (tx 0x81549ae212..., block 132228400)",
        "machine_wallets": 27,
        "typical_first_buy_bnb": 0.000123025,
        "followup_buy_range_bnb": "median 0.2337475, max 0.347077, total buys 9.0140 BNB (50 sent buys)",
        "label": "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - NAMED (BTC / 比特币) - ANOMALY, reported once as signal run 103",
        "note": "ANOMALY under the fast-path amendment: name/symbol APPEARED - name 'BTC', symbol '比特币', confirmed via fast_rpc; totalSupply 1e27; "
                "decimals 18. DexScreener independently confirms BTC/比特币, pair 0x25a1bf1d836ba5865d9ba1dfaea33c33ad06c754, pair created 22:55:49 WIB, "
                "vol24 $17,708.50, txns h24 buys 81/sells 134, liquidity $0.07 (drained after the rotation's sells). "
                "First buy 22:56:24 WIB by 0xcb08c02c0a, 0.000123025 BNB -> 9,826.24 tokens. Wallet set byte-identical to the other run-103 rotations and diff 0 "
                "vs the run-102 machine set (27/27 overlap). Buy sizes WITHIN class norm - NOT a size anomaly. 96 sells / 27 sell wallets in-window - rotation "
                "fully dumped. Pair token0/token1 NOT read run 103 - retry run 104. Auto-mint BLOCKED at guard (c) - paid PCS token, "
                "no free-mint path. Do not re-signal unless a new fact appears.",
    },
    {
        "address": "0xf3bdc9ef1343fa3ef7c555414e9cc2a5e5537777",
        "first_seen": "run-103, 2026-11-07 22:33:54 WIB (tx 0x45550f4238..., block 132225398)",
        "machine_wallets": 27,
        "typical_first_buy_bnb": 0.000123142,
        "followup_buy_range_bnb": "median 0.226420430, max 0.401811, total buys 9.2594 BNB (53 sent buys)",
        "label": "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - NAMED (propfun / PROPFUN) - ANOMALY, reported once as signal run 103",
        "note": "ANOMALY under the fast-path amendment: name/symbol APPEARED - name 'propfun', symbol 'PROPFUN', confirmed via fast_rpc; totalSupply 1e27; "
                "decimals 18. DexScreener independently confirms propfun/PROPFUN, pair 0xbf243f454ac1463f2b596d9843026299e0ea5e31, pair created 22:33:12 WIB, "
                "vol24 $18,020.59, txns h24 buys 83/sells 133, liquidity $0.07 (drained after the rotation's sells). "
                "First buy 22:33:54 WIB by 0xcb08c02c0a, 0.000123142 BNB -> 9,826.04 tokens. Wallet set byte-identical to the other run-103 rotations and diff 0 "
                "vs the run-102 machine set (27/27 overlap). Buy sizes WITHIN class norm - NOT a size anomaly. 95 sells / 27 sell wallets in-window - rotation "
                "fully dumped. Pair token0/token1 NOT read run 103 - retry run 104. Auto-mint BLOCKED at guard (c) - paid PCS token, "
                "no free-mint path. Do not re-signal unless a new fact appears.",
    },
]
s.setdefault("machine_tokens", []).extend(new_entries)

# update stalled labels' run ranges
for e in s["machine_tokens"]:
    if e["address"].lower().startswith("0x1153607e"):
        e["label"] = "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - rotation STALLED at 26 wallets (runs 91-103)"
    if e["address"].lower().startswith("0x79cd174c"):
        e["label"] = "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - rotation STALLED at 20 wallets (runs 90-103)"
    if e["address"].lower().startswith("0x1e9c6d46"):
        e["label"] = "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - NAMED (Seatbelt Dog / Seatbelt) - ANOMALY, reported once as signal run 101 - rotation STALLED at 26/27 sell wallets (union run101+run102; 0 wallets run 103)"
        e["note"] = e.get("note", "") + " Run 103: 0 wallets (0 buys, 0 sells); sell-wallet union run101+run102 = 26/27 - STALLED at 26, did NOT reach 27. NOT a new rotation."

# signaled projects: append the three (paid-only)
s.setdefault("signaled_projects_over_20pct", []).extend([
    "DiamondPepe69 (PEPE69) 0x780967274cca69ee9e64cf6546488830c03f7777 (paid-only, machine-token, run-103, NAMED - anomaly reported once as signal)",
    "BTC (比特币) 0x7f0a67b94ee0faf41d0ee352a44f0fc94e8e7777 (paid-only, machine-token, run-103, NAMED - anomaly reported once as signal)",
    "propfun (PROPFUN) 0xf3bdc9ef1343fa3ef7c555414e9cc2a5e5537777 (paid-only, machine-token, run-103, NAMED - anomaly reported once as signal)",
])

# ---- next run note: anchored updates on the existing note ----
note = s["next_run_note"]

def rep_once(old, new, tag):
    global note
    c = note.count(old)
    assert c == 1, f"{tag}: anchor count {c} != 1: {old[:120]!r}"
    note = note.replace(old, new)

# (0) window start
rep_once("Next run sent-tx window starts from block 132224206.",
         "Next run sent-tx window starts from block 132238465.", "window")

# (1)+(2) pair retry paragraph + inbound list line: replace span between
# "RETRY run 103:" and "(3) Run-102 inbound window"
i0 = note.index("RETRY run 103: (1) Pair token0/token1 reads")
i1 = note.index("(3) Run-102 inbound window")
new_retry = (
    "RETRY run 104: (1) Pair token0/token1 reads for 0xa6e6... pair 0x9fac925655fa4985ab4fe2fe9e0ca8ae323cc9da and 0x887c... pair "
    "0xa9fa6efb21c252b7d4ab81d19a07ee4ecf6d2c97 (fast_rpc race returns None / 'all endpoints failed', 21 consecutive runs - persistently unreadable, "
    "unverified not absence), plus 0x2bfb pair 0x782671f637bf1a01de482824c4b2520bc58a5a4b, 0xc459 pair 0xeca06856c88fcdf1506886431a079d3f2565ca82, and "
    "rotation 0x43c8 pair 0xaafebb5244e2e546f7cd18a2c89f85bbee03f1e0 (unreadable run 88-103, 16 consecutive - retry opportunistically, not an anomaly), "
    "PLUS run-89 rotation pairs 0xcfdb 0x1e04925db4eabab2917ef73a8cdf232bcc69b5ba, 0x0cf8 0xf6800c4a1ecdffbd64f9047c606bdb32dee0127f, 0xe68b "
    "0xfab7cb4979c9e4738afc61e4974177cf72c50896 (token0/token1 unreadable run 89-103, 15 consecutive; 0x31e4 pair 0x60ca0aef... READ OK run 89), PLUS "
    "run-102 rotation pairs 0x8b19 0xf7a2396852111ed1480d4ffca583696369c87eab + 0xd826 0x2315f44831bcac27bd7308e2d50943b4f115f4bd + 0x07b2 "
    "0x39f0227ba7aa712db15bdb51046647e8f0939b54 + 0x4263 0x70b31f93bff68d87ccd7b11c4458af5a7deb8d44 (NOT read run 102 or run 103 - 2nd attempt failed, fast_rpc race outage total run 103; "
    "DexScreener confirms all four PCS V2 token/WBNB pairs), PLUS run-103 rotation pairs 0x7809 0xfaba06b92f8e425055417fac8388dedf1cd58a72 + 0x7f0a "
    "0x25a1bf1d836ba5865d9ba1dfaea33c33ad06c754 + 0xf3bd 0xbf243f454ac1463f2b596d9843026299e0ea5e31 (NOT read run 103 - retry run 104; DexScreener confirms all three "
    "PCS V2 token/WBNB pairs); 4727 pair 0xf4ee6a9b528670fcdce10c8af0f5262b4fef1d3d READ OK run 102 (token0 = 4727 token, token1 = WBNB) - REMOVED from retry; "
    "1e9c pair 0x533623ca2db657de9a36e84e2b5a809fbee7ecbe READ OK run 102 (token0 = 1e9c token, token1 = WBNB) - REMOVED from retry; db49 pair "
    "0x41cbb4910fd4959f651d7bff8d8b5ed5cd355dfc READ OK run 101 (token0 = WBNB, token1 = db49 token) - REMOVED from retry; ff66 pair "
    "0x2d3e053bada0378299010fde9f59209985760bab READ OK run 101 (token0 = WBNB, token1 = ff66 token) - REMOVED from retry; 0x6b12 pair READ OK run 100 - "
    "already removed; 0x50e4 pair READ OK run 99 - already removed; 41cc pair READ OK run 99 - already removed; run-97 rotation pairs c90a/e3a8 READ OK "
    "run 98 - already removed; run-100 pairs 6f31 0xc9299379d122a1a84d45fdf1ee87dd0ce1a5e3e8 + 0d7e 0x98fe67c6aeb645e6c9aa41c1fd79898261e7fde7 READ OK run 100 "
    "(token0 = token, token1 = WBNB) - no retry needed. "
    "(2) Run-103 inbound list = run102 list (1663) + 68 run-103 deployments + 3 new rotation tokens (total 1734); run-104 inbound list = run103 list (1734) "
    "+ run-104 deployments + new rotation tokens. "
)
note = note[:i0] + new_retry + note[i1:]

# (3) inbound window line
rep_once("(3) Run-102 inbound window FULLY CLOSED in-run (1663/1663, 1 hit - the sent-pass AFeng tracker tx 0xb8f3ac7e..., 0 failed after same-run retry of 3 failed contracts - "
         "verify at state-update time; if the retry had failures, they are listed in inbound_log_leg_run102.failed_contracts and must be retried in run 103). ",
         "(3) Run-103 inbound window FULLY CLOSED in-run (1734/1734, 0 hits, 0 failed after same-run retry of 5 failed contracts - "
         "verify at state-update time; if the retry had failures, they are listed in inbound_log_leg_run103.failed_contracts and must be retried in run 104). ",
         "inbound-closed")

# (4) watch paragraph: replace span from "(4) 0x1e9c6d46... rotation STALLED" up to the dedupe sentence start
j0 = note.index("(4) 0x1e9c6d46... (Seatbelt) rotation STALLED")
j1 = note.index("Dedupe new mints against all tx hashes")
new_watch = (
    "(4) 0x1e9c6d46... (Seatbelt) rotation STALLED at 26/27 sell wallets (union run101+run102; 0 wallets run 103) - "
    "did NOT reach 27; watch run 104 the same way, do NOT treat continuation as a new rotation. 0xdb4950e7... rotation COMPLETED run 100 (sell-wallet union "
    "run99+run100 = 27/27) - do NOT treat any db49 activity as a new rotation. 0x1153607e... rotation STALLED at 26 wallets (0 wallets runs 91-103, 13th quiet "
    "run after debut) - watch run 104 the same way. 0x79cd... STALLED at 20 wallets (0 wallets runs 90-103, 14th quiet run after debut) - same. Run-102 named "
    "rotations 0x8b19.../0xd826.../0x07b2.../0x4263...: 0 wallets run 103 (1st quiet run after debut) - watch run 104 the same way. Run-101 named rotations 0x4727...: "
    "0 wallets run 103 (2nd quiet run after debut) - same. Run-100 named rotations 0x6f31.../0x0d7e...: 0 wallets run 103 (3rd quiet run after debut) - same. "
    "Run-99 named rotations 0x50e4.../0x6b12.../0xff66...: 0 wallets run 103 (4th quiet run after debut) - same. Run-98 named rotations 0x41cc.../0x43bc.../0x2120.../0xda79...: "
    "0 wallets run 103 (6th quiet run after debut) - same. Run-97 named rotations 0xc90a.../0xe3a8...: 0 wallets run 103 (6th quiet run after debut) - same. "
)
note = note[:j0] + new_watch + note[j1:]

# dedupe: append run-103 note after the run-102 repeats sentence
rep_once("corla 0xd2c1... is a DIFFERENT contract from the run-63 paid-only signal CORLA 0x4a9c. ",
         "corla 0xd2c1... is a DIFFERENT contract from the run-63 paid-only signal CORLA 0x4a9c. "
         "Run-103: ZERO mint-pattern txs (0 mint logs in 718 receipts) - no dividend-tracker repeats this run; AFeng's 10 sale-calls (total 3.0 BNB) carried no zero-from Transfer to a tracked wallet. ",
         "dedupe-run103")

# append run-103 entry to the paid-only signals list (after the run-102 entry's ending anchor)
rep_once("new run-102 pairs 8b19/d826/07b2/4263 NOT read (fast_rpc race outage continues) - retry run 103) ",
         "new run-102 pairs 8b19/d826/07b2/4263 NOT read (fast_rpc race outage continues) - retry run 103) "
         "run 103 (THREE NEW rotations 0x7809... DiamondPepe69/PEPE69 + 0x7f0a... BTC/比特币 + 0xf3bd... propfun/PROPFUN at 27 wallets each - ALL NAMED, "
         "seventh consecutive run with named rotations, anomaly reported once as signal run 103; buy sizes in class norm; all three fully dumped in-window (95/96/95 sells, 27 sell wallets each); "
         "1e9c STALLED at 26/27 sell wallets (union run101+run102, 0 wallets run 103); 8b19/d826/07b2/4263 0 wallets (1st quiet run after debut); 4727 0 wallets (2nd quiet run); "
         "6f31/0d7e 0 wallets (3rd quiet run); 50e4/6b12/ff66 0 wallets (4th quiet run); 41cc/43bc/2120/da79 0 wallets (6th quiet run); c90a/e3a8 0 wallets (6th quiet run); "
         "0x1153... STALLED at 26, 13th quiet run; 0x79cd... STALLED at 20, 14th quiet run; 68 deployments (seventh straight run with deployments, 0x64e893a4 alone 9); inbound FULLY CLOSED in-run "
         "(first-attempt chunks ALL WEDGED on proxy sockets, killed by PID + re-launched from scratch as -2), 1734 contracts, 15,732 logs, 0 hits, 0 failed after same-run retry of 5 failed "
         "contracts; 0 NULL receipts; pair retry 15/15 FAILED (fast_rpc race outage TOTAL) - all 15 pairs unverified, retry run 104) ",
         "paid-list-run103")

# append "Paid fact: run103" after the "Paid fact: run102" paragraph (anchor on its ending)
rep_once("don't conclude. Run 101 had 35 deployments",
         "don't conclude. "
         "Paid fact: run103 THREE NEW rotations 0x7809... (DiamondPepe69/PEPE69) + 0x7f0a... (BTC/比特币) + 0xf3bd... (propfun/PROPFUN) at 27 wallets each - ALL NAMED, "
         "seventh consecutive run with named rotations (anomaly: name/symbol appeared; reported once as signal run 103, paid-only, auto-mint blocked guard (c)); "
         "run-102 tokens 0x8b19.../0xd826.../0x07b2.../0x4263... 0 wallets (1st quiet run after debut); 1e9c STALLED at 26/27 sell wallets (union run101+run102, 0 wallets run 103); "
         "run-101 token 0x4727... 0 wallets (2nd quiet run after debut); run-100 tokens 0x6f31.../0x0d7e... 0 wallets (3rd quiet run after debut); "
         "run-99 tokens 0x50e4.../0x6b12.../0xff66... 0 wallets (4th quiet run after debut); run-98 tokens 0x41cc.../0x43bc.../0x2120.../0xda79... 0 wallets (6th quiet run after debut); "
         "run-97 tokens 0xc90a.../0xe3a8... 0 wallets (6th quiet run after debut); run-90 tokens 0x6a25.../0x9f7e.../0x8c64.../0xc1ab.../0x1153... 0 wallets (13th quiet run after debut); "
         "run-89 tokens 0xcfdb.../0x0cf8.../0xe68b.../0x31e4... 0 wallets (14th quiet run after debut); run-88 tokens 0x43c8.../0x3d12.../0xeae0... 0 wallets (15th quiet run after debut); "
         "run-87 tokens 0x889a.../0x4249... 0 wallets (16th quiet run after debut); run-86 tokens 0x2bfb.../0xc459... 0 wallets (17th quiet run after debut); run-85 token 0x2717... 0 wallets (18th quiet run); "
         "run-82 tokens 0xd468.../0xa6e6.../0x887c... all 0 wallets (21st quiet run after debut); run-81 tokens 0 wallets (22nd quiet run); run-80 token 0 wallets (23rd quiet run); "
         "GrokBot 0xfcd0... absent (0 wallets) - 44th consecutive quiet run (59, 61-103) after the run-60 burst; CORLA-97af 0 wallets; CORLA 0x4a9c 0 wallets; all run-64/65 ASI contracts 0 wallets; "
         "all run-66/68/69/70/71/72/73/74/75/76/77/78/79 machine tokens 0 wallets. Run 103 had 68 deployments (seventh straight run with deployments; 0x64e893a4 alone 9; added to the inbound list "
         "for run 104 - all 68 addresses recovered from RAW receipts, 0 NULL receipts). AFeng 16 txs (10 sale-calls + 5 approvals + 1 transfer, total value 3.0 BNB - "
         "much smaller than run 102's 34.4 BNB; NO dividend-tracker mint logs this run); future1001.ai 13 txs (4 PCS buys of the new rotations + 3 sells + 3 approvals + 1 creation, total value ~0.72 BNB - first buyer of the 0x7809 rotation); 0x2325... 6 txs (4 aggregator 0x27772d13 + "
         "2 approvals, total value 0.21 BNB); 0x8e96... 0 txs; 0x3803... 65 txs (44 aggregator 0x39ecce49 + 21 approvals, total value 0.0005 BNB, churn as usual). "
         "PROCESS LESSON (run 103): first-attempt inbound chunks ALL WEDGED on proxy sockets at once (every chunk 'Remote end closed connection' on contract #1-2, ~2 contracts in ~12 min) while a fresh "
         "Ankr call worked in ~11s - a wedge is chunk-wide, not per-contract; kill by PID (pkill -f matches the wrapper shell itself - use kill <pid>) and re-run chunks from scratch; the compound nohup "
         "launch only started chunk a (b1/b2/b3 needed separate launches). fast_rpc race OUTAGE TOTAL (run 103): all-endpoint TimeoutError/OSError ~00:25-00:45 WIB - pair-retry 15/15 failed, receipts pass batch "
         "failures forced slow per-tx race fallbacks (~35 min); token-meta calls succeeded earlier in the run (12 calls, ~19s) - the outage is time-varying, not permanent. A failed race read is UNVERIFIED, "
         "never absence - retry, don't conclude. Run 101 had 35 deployments",
         "paid-fact-run103")

s["next_run_note"] = note

json.dump(s, open(P, "w"), indent=1)
print("state updated; last_run now:", s["last_run"]["run"], "block_end:", s["last_run"]["block_end"])
print("machine_tokens:", len(s.get("machine_tokens", [])), "| signaled:", len(s.get("signaled_projects_over_20pct", [])))
print("inbound103 complete:", s["inbound_log_leg_run103"]["complete"], "| failed:", s["inbound_log_leg_run103"]["failed"],
      "| total_logs:", s["inbound_log_leg_run103"]["total_logs"], "| hits:", s["inbound_log_leg_run103"]["hits"])
print("inbound102 complete:", s["inbound_log_leg_run102"]["complete"], "| failed:", s["inbound_log_leg_run102"]["failed"])
print("next_run_note len:", len(s["next_run_note"]))
