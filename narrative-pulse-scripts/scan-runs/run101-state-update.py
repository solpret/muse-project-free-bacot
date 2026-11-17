#!/usr/bin/env python3
"""Run 101 state update (read-only job bookkeeping; no chain writes).

Completes run 101 (window 132192617-132208026, tx 2026-11-07 18:29:11 - 20:23:33 WIB).
Sent/receipts/paid done and verified; inbound leg run-101 window CLOSED in-run
(1589/1589, 2 hits - BOTH are the sent-pass AFeng tracker txs, 0 inbound-only new).
NO new mints. TWO NEW machine-token rotations at 27 wallets each - BOTH NAMED
(Forever Laura / Laura + Seatbelt Dog / Seatbelt), the FIFTH consecutive run with
named rotations (run 97 had 2, run 98 had 4, run 99 had 4, run 100 had 2, run 101
has 2): anomaly under the fast-path amendment, reported ONCE as a paid-only signal
(not a lead, not a buy recommendation, auto-mint blocked at guard (c)).
35 deployments this run (fifth straight run with deployments; 25/72/64/32/35).
Bridge unchanged (0 new mints, 0 not_evaluated). Run-101 NULL receipt RECOVERED
same-run: tx 0x62fb2bb4... (AFeng sale-call, 1 BNB) status 1, block 132198457,
43 logs - contains the same known-repeat 0x636f tracker mint log.
"""
import json, shutil

P = "/home/hatch/workspace/narrative-pulse/tracked-wallet-mint-scan-state.json"
shutil.copy(P, str(P) + ".bak-run101-pre")
s = json.load(open(P))
SR = "/home/hatch/workspace/narrative-pulse/scan-runs"

# ---- inbound totals from chunk JSONs (self-verifying) ----
chunks = {}
for part in ["a", "b1", "b2", "b3"]:
    chunks[part] = json.load(open(f"{SR}/run101-inbound101-{part}.json"))
tot_contracts = sum(c["contracts_checked"] for c in chunks.values())
tot_logs = sum(c["total_logs"] for c in chunks.values())
tot_hits = sum(len(c["hits"]) for c in chunks.values())
tot_failed = sum(len(c["failed"]) for c in chunks.values())
tot_trunc = sum(len(c["truncated"]) for c in chunks.values())
print(f"inbound totals: contracts={tot_contracts} logs={tot_logs} hits={tot_hits} failed={tot_failed} truncated={tot_trunc}")
assert tot_contracts == 1589, f"inbound contracts {tot_contracts} != 1589"
assert tot_hits == 2, f"inbound hits {tot_hits} != 2 (must handle before state update!)"
hit_txs = {h["tx"].lower() for c in chunks.values() for h in c["hits"]}
assert hit_txs == {"0x522c6c82ff845591f0c319f44bc1f79fd3d314efa644660ef68bca920332c485",
                   "0x62fb2bb4c86600a50a5f3170a40ea4fcd3156764b5bab268494a0dbfc771fccb"}, \
    f"inbound hits are NOT the two known-repeat AFeng tracker txs: {hit_txs}"
print("inbound hits verified: both are the known-repeat AFeng tracker txs (0x522c... + 0x62fb...), 0 inbound-only new mints")
failed_contracts = [f for c in chunks.values() for f in c["failed"]]
retry_path = f"{SR}/run101-inbound101-retry.json"
retry = json.load(open(retry_path))
retry_failed_addrs = {f["contract"] for f in failed_contracts}
assert retry["contracts_checked"] == len(retry_failed_addrs), "retry did not cover all failed contracts"
assert retry["failed"] == [], f"retry itself failed: {retry['failed']}"
assert retry["hits"] == [], "retry found hits - must handle before state update!"
print(f"same-run retry recovered {len(retry_failed_addrs)}/{len(retry_failed_addrs)} failed contract(s): "
      f"{sorted(retry_failed_addrs)} -> {retry['total_logs']} logs, 0 hits")
eff_failed = 0
tot_logs_effective = tot_logs + retry["total_logs"]
trunc_all = [t for c in chunks.values() for t in c["truncated"]]

last_run_101 = {
    "run": 101,
    "block_start": 132192617,
    "block_end": 132208026,
    "window_wib": "2026-11-07 18:29:11 - 20:23:33 WIB (tx times); run executed ~20:05 - ~22:14 WIB; sent-pass in-window txs 855, 2 mint-pattern txs (BOTH known repeats, see method_note)",
    "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set); 1 failed first attempt (0x5b4beded, Ankr 'Remote end closed connection'), retried same-run OK (16 txs) - 0 failed after retry.",
    "method_note": (
        "Sent pass Ankr ankr_getTransactionsByAddress via module: first attempt 54/55 OK (855 txs total after retry); wallet 0x5b4beded failed "
        "('Remote end closed connection without response') and was retried same-run via run101-sent-retry.py - 16 txs recovered, total 855, 36 wallets "
        "active, 0 failed after retry. "
        "Receipts via fast_rpc batch (6, ~4s pause) for 559 non-approve candidates: 554 status 1, 4 status 0 (ALL failed PCS sells 0x791ac947: "
        "0xdb2d83f9 19:38:32 WIB tx 0x5d624c1f0d..., 0xa952331e 19:40:44 WIB tx 0x816c1d094f..., 0x92bc3297 19:40:48 WIB tx 0xe2e280411e... + 20:15:49 WIB "
        "tx 0x2681c993e5...), 1 NULL (0x62fb2bb4... AFeng sale-call, 1 BNB, 19:11:45 WIB) - RECOVERED same-run via fast_rpc race (run101-null-receipt-save.py): "
        "status 1, block 132198457, 43 logs, gasUsed 0xa5c7d - contains the SAME known-repeat 0x636f tracker mint log (see below). Receipts completed in "
        "one attempt, no resume needed. "
        "Mint-pattern txs: 2 - 0x522c6c82... (AFeng sale-call 0x4d819a2a to 0x1de4..., 0.5 BNB, 19:47:35 WIB, block 132203234) and the recovered 0x62fb2bb4... "
        "(AFeng sale-call, 1 BNB, 19:11:45 WIB, block 132198457). BOTH are Transfers from the zero address by the DIVIDEND_TRACKER contract "
        "0x636fdfa9bc3db42c690c09e87b9017d05b36c743 to AFeng - the KNOWN REPEAT of the run-70 finding (AFeng buys moco reflection token via router 0x1de4..., "
        "tracker mints shares 1:1 with the bought balance + WBNB dividends). Per the state note ('do not report as new if it repeats again'), NEITHER is "
        "reported as a new mint. 0 new mints this run. "
        "Paid: 56 tokens; max 27 wallets/token (TWO new rotations at 27 each - see anomaly signal; 23 tokens at 3 wallets, ALL the same churn trio "
        "0x3803/0xad94/0xc7c5, all ...7777; 11 at 2 (the 0x3628/0xa0c1 pair); 20 at 1). ZERO overlap with run-100's 42 paid tokens - the ...7777 churn set "
        "turns over completely every run. "
        "NEW ROTATIONS - ANOMALY (named tokens, FIFTH consecutive run - run 97 had 2 named, run 98 had 4, run 99 had 4, run 100 had 2, run 101 has 2): "
        "0x4727e091d34665249bfbdc1575c7180d19527777 (Forever Laura / Laura), "
        "0x1e9c6d463a096320df3ad60754344b2735a37777 (Seatbelt Dog / Seatbelt). "
        "Both: name+symbol+totalSupply+decimals confirmed via fast_rpc (4727 full pass; 1e9c name pass 1, symbol/totalSupply/decimals retried OK after "
        "pass-1 'all endpoints failed'), totalSupply 1e27, decimals 18. DexScreener independently confirms both (Laura: pair created 1h 5m ago, 216 txns, "
        "vol $17K, buys 82/sells 134, liquidity <$1 - drained after the rotation's sells, pooled Laura 59,594,490 + WBNB 0.00005421; Seatbelt: pair created "
        "30m ago, 227 txns, vol $18K, buys 89/sells 138, liquidity <$1, pooled Seatbelt 78,070,146 + WBNB 0.00004286). "
        "Both bought by the SAME 27-wallet machine set, byte-identical to each other and diff 0 vs the run-100 machine set (27/27 overlap). "
        "Buy sizes WITHIN class norm (NOT a size anomaly): first buy 0.000123025 BNB -> 9,820.29 tokens (4727) / 9,826.24 tokens (1e9c); follow-up medians "
        "0.225521877 (4727) / 0.223364190 (1e9c); max 0.313274 (4727) / 0.416612 (1e9c); totals 8.9392 / 9.4726 BNB; buys 51/57, sells 96/87 (sell wallets "
        "27/24 - 4727 FULLY dumped in-window, 1e9c STILL FILLING at window end: 24/27 sell wallets, debuted 20:13:01 WIB late in the window). First buys: "
        "4727 19:37:59 WIB by 0xcb08c02c0a tx 0xf55b760fe1... block 132201955 pair 0xf4ee6a9b528670fcdce10c8af0f5262b4fef1d3d; "
        "1e9c 20:13:01 WIB by 0xcb08c02c0a tx 0x750d1944ad... block 132206622 pair 0x533623ca2db657de9a36e84e2b5a809fbee7ecbe. Pair token0/token1: NOT read this "
        "run (fast_rpc race outage - retry run 102); DexScreener confirms both are PCS V2 token/WBNB pairs. Trigger >25% met numerically (27 >= 14) but "
        "AUTO-MINT BLOCKED at guard (c): paid PCS tokens, no free-mint path; guard (a) website also unverified. No preview, no execution. "
        "Deployments: 35 contract creations by 14 machine-set wallets (0xaa49e7fe 4; 0x64e893a4 4; 0xf795c525/0x3a39aa05/0xcb08c02c/0x1cce4ec5/0xc0c84518/0x97bd895f "
        "3 each; 0x3154f694/0x5b4beded/0x9b519f5d 2 each; 0xdb2d83f9/0xa952331e/0x92bc3297 1 each) - FIFTH straight run with deployments (25 run 97, 72 run 98, "
        "64 run 99, 32 run 100, 35 run 101); all 35 deployed addresses recovered from RAW receipts (run101-receipts-partial.json), added to the inbound list "
        "(run101-inbound-contracts.json, total 1589) along with the 2 new rotation tokens. The 2 rotation tokens are NOT among the deployments. "
        "PARSER LESSON (run 101): runNN-receipts.py NEVER extracts contractAddress (the parsed JSON has no such field) - the initial '0 deployments' reading "
        "from run101-receipts.json was WRONG; deployments must be read from runNN-receipts-partial.json raw receipts (to is null + contractAddress present). "
        "AFeng (0xbf004bff...) 22 txs (17 sale-calls 0x4d819a2a + 5 approvals, total value 4.125 BNB; sale values 0.75/0.6/0.5/0.375x4/0.25x2/0.125/0.075x2/0x5); "
        "future1001.ai 0 txs; 0x2325... 11 txs (7 aggregator 0x27772d13 + 4 approvals, total value 0.3 BNB); 0x8e96... 0 txs; 0x3803... 66 txs (44 aggregator "
        "0x39ecce49 + 22 approvals, total value 0.0006 BNB, churn as usual). 3 plain BNB transfers (0x3628..., 0xc7c5..., 0x7488... 1 each, empty input). "
        "Selectors (sent pass, 855 txs): 296 approvals (0x095ea7b3) + 260 PCS sells (0x791ac947) + 185 PCS buys (0xb6f9de95) + 44 aggregator (0x39ecce49) + "
        "35 contract creations (0x60806040) + 17 sale-calls (0x4d819a2a, AFeng) + 15 aggregator (0x27772d13) + 3 empty-input (plain BNB transfers). "
        "Nonzero-value txs 260, total 24.1911 BNB, max 0.75 BNB (AFeng sale-call 0x6259a9e27917, 19:57:36 WIB). Most active wallets: 0xc7c5faa2 67 txs, "
        "0x38031ca8 66, 0xad94ee77 65, 0x3628764a 34, 0xc6219468 34, 0x9cdd08f3 34, 0xa0c1e94f 33, 0xa952331e 33, 0x7488d5da 25, 0xf795c525 25, 0x1cce4ec5 25, "
        "0xe9ed24db 24, 0x9b519f5d 24, 0xfdec62fd 24, 0x3a39aa05 23, 0xc0c84518 23, 0xbf004bff (AFeng) 22, 0xcb08c02c 22, 0xf9689b9d 22, 0x92bc3297 21. "
        "1 NULL receipt this run (0x62fb2bb4, AFeng sale-call) - RECOVERED same-run (see above), 0 null remaining. 4 status-0 txs, all failed PCS sells (see above). "
        f"Inbound leg (amendment 12:02 WIB): Ankr getLogs address-filtered per contract, 1589 contracts (run100 list 1552 + 35 run-101 deployments + "
        f"2 new rotation tokens), 2 hits (BOTH the sent-pass AFeng tracker txs - 0 inbound-only new mints), {tot_logs} logs, window 132192617-132208026. "
        f"Chunk a (400, 8,791 logs, 2 failed, 6 truncated) + b1 (200, 4,052 logs, 0 failed, 3 truncated) + b2 (200, 2,450 logs, 0 failed, 0 truncated) + "
        f"b3 (789, 2,882 logs, 1 failed, 0 truncated) + retry (3 contracts, 0 logs, 0 failed - the 3 in-chunk failures 0x3fd85ca8..., 0x563a23b9..., "
        f"0x846f8a0f... recovered same-run) = {tot_logs_effective} logs, 2 hits (sent-pass duplicates), 0 FAILED after retry. "
        "Truncated contracts, all topic-filtered to 0 logs (a: 0x10b3... moco, 0x1de4... AFeng sale, 0x3dca..., 0x55d398... USDT, 0x6288... AGC sale, "
        "0x636fdfa9... tracker - same set as runs 91-100; b1: 0x63de... AGC, 0x7857..., 0x7e2d...; b2/b3: none). "
        "Chunks a/b3 FIRST attempt WEDGED on proxy sockets (logs frozen >5 min with live processes while fresh Ankr calls worked in 7-15s), killed by PID + "
        "re-launched from scratch; SECOND attempt (-2) ALSO wedged ~contract 350 on a/b3, killed by PID + re-launched from scratch as -3; -3 completed "
        "(a 400/400, b3 789/789). All four chunks hit repeated joint Ankr stalls this run (logs frozen minutes at a time with live processes, then resuming "
        "- same pattern as runs 95/100). Window FULLY CLOSED in-run, no retry deferred to run 102. "
        "Pair a6e6/887c/2bfb/c459/43c8/cfdb/0cf8/e68b STILL unreadable: token0()/token1() for all eight pairs failed via fast_rpc race "
        "('all endpoints failed') in run101-pair-retry.py - unverified, not absence; 19th consecutive run for a6e6/887c/2bfb/c459, 14th for 43c8, "
        "13th for cfdb/0cf8/e68b; retry run 102. BUT db49/ff66 pairs READ OK this run (db49 pair 0x41cbb491...: token0 = WBNB, token1 = db49 token; ff66 "
        "pair 0x2d3e053b...: token0 = WBNB, token1 = ff66 token) - REMOVED from the retry list. New run-101 pairs 4727 0xf4ee6a9b... + 1e9c 0x533623ca... "
        "NOT read this run (fast_rpc race outage) - retry run 102. "
        "fast_rpc race OUTAGE this run (time-varying, not permanent): all-endpoint TimeoutError/OSError flapping ~21:00-22:00 WIB - token-meta pass 1 failed "
        "entirely, null-receipt retry failed twice, pair-retry 8/10 failed; but the batch receipts pass completed fine and later retries succeeded "
        "(token-meta pass 2 + targeted 1e9c retry, null receipt, db49/ff66 pairs). A failed race read is UNVERIFIED, never absence. "
        "Pointer-discovery (amendment 19:10): 0 contracts processed - no new mints this run, and the backfill queue is empty (bridge 115 contracts, "
        "0 not_evaluated); bridge unchanged. CHAT REPORT this run: the two-named-machine-token anomaly signal (paid-only, NOT a lead, NOT a buy "
        "recommendation, auto-mint blocked guard (c)) - reported once per the fast-path amendment. No new mints, no Free Bacot signal beyond that, "
        "no auto-mint trigger execution. No preview/mint/sign/login/purchase by this job."
    ),
}
s["last_run"] = last_run_101

# ---- paid signal + trend ----
s["paid_signal_run101"] = {
    "note": "ANOMALY SIGNAL (paid-only, NOT a buy recommendation, NOT a Free Bacot lead, NOT an auto-mint trigger). FIFTH consecutive run with NAMED "
            "machine-token rotations - now TWO at once (run 97 had 2, run 98 had 4, run 99 had 4, run 100 had 2, run 101 has 2): the machine set bought TWO tokens "
            "that HAVE on-chain name/symbol, breaking the unnamed pattern of all 24 pre-run-97 machine tokens. Reported once per the fast-path "
            "amendment (name/symbol appeared). Auto-mint BLOCKED at guard (c) for both (paid PCS tokens, no free-mint path). Do not re-signal "
            "unless a new fact appears (e.g. a genuine free-mint path).",
    "tokens": [
        {
            "address": "0x4727e091d34665249bfbdc1575c7180d19527777",
            "name": "Forever Laura",
            "symbol": "Laura",
            "wallets": 27,
            "first_buy": "2026-11-07 19:37:59 WIB, 0.000123025 BNB -> 9,820.29 tokens, wallet 0xcb08c02c0a, tx 0xf55b760fe1..., block 132201955",
            "pair": "0xf4ee6a9b528670fcdce10c8af0f5262b4fef1d3d (PCS V2; token0/token1 NOT read run 101 - fast_rpc race outage, retry run 102; DexScreener confirms token/WBNB pair)",
            "buys": "51 sent buys, median follow-up 0.225521877 BNB, max 0.313274 BNB, total 8.9392 BNB; 96 sells / 27 sell wallets (fully dumped in-window)",
            "verification": "name+symbol+totalSupply+decimals confirmed via fast_rpc; totalSupply 1e27; decimals 18; DexScreener Forever Laura/Laura, pair created 1h 5m ago, 216 txns, vol $17K, buys 82/sells 134, liquidity <$1 (drained after the rotation's sells), pooled Laura 59,594,490 + WBNB 0.00005421",
        },
        {
            "address": "0x1e9c6d463a096320df3ad60754344b2735a37777",
            "name": "Seatbelt Dog",
            "symbol": "Seatbelt",
            "wallets": 27,
            "first_buy": "2026-11-07 20:13:01 WIB, 0.000123025 BNB -> 9,826.24 tokens, wallet 0xcb08c02c0a, tx 0x750d1944ad..., block 132206622",
            "pair": "0x533623ca2db657de9a36e84e2b5a809fbee7ecbe (PCS V2; token0/token1 NOT read run 101 - fast_rpc race outage, retry run 102; DexScreener confirms token/WBNB pair)",
            "buys": "57 sent buys, median follow-up 0.223364190 BNB, max 0.416612 BNB, total 9.4726 BNB; 87 sells / 24 sell wallets (STILL FILLING at window end - debuted 20:13:01 WIB late in the window)",
            "verification": "name confirmed via fast_rpc pass 1; symbol+totalSupply+decimals retried OK (pass-1 'all endpoints failed'); totalSupply 1e27; decimals 18; DexScreener Seatbelt Dog/Seatbelt, pair created 30m ago, 227 txns, vol $18K, buys 89/sells 138, liquidity <$1 (drained after the rotation's sells), pooled Seatbelt 78,070,146 + WBNB 0.00004286",
        },
    ],
}

s["paid_trend_run101"] = {
    "note": "Aggregate only, NOT a buy recommendation. TWO NEW machine-token rotations at 27 wallets each - BOTH NAMED (Forever Laura/Laura, Seatbelt Dog/Seatbelt), "
            "FIFTH consecutive run with named rotations (run 97 had 2, run 98 had 4, run 99 had 4, run 100 had 2): anomaly reported once as a paid-only signal "
            "(paid_signal_run101); buy sizes in class norm; 4727 fully dumped in-window (96 sells, 27 sell wallets), 1e9c still filling (87 sells, 24 sell wallets). "
            "Run-100 named rotations 6f31/0d7e 0 wallets (1st quiet run after debut); run-99 named rotations 50e4/6b12/ff66 0 wallets (2nd quiet run after debut); "
            "run-98 named rotations 41cc/43bc/2120/da79 0 wallets (4th quiet run after debut); run-97 named rotations c90a/e3a8 0 wallets (4th quiet run after debut); "
            "all five run-90 rotations 0 wallets (11th quiet run after debut); 0x1153... STALLED at 26 wallets (11th quiet run); 0x79cd... STALLED at 20 wallets "
            "(12th quiet run). 35 deployments - fifth straight run with deployments. Inbound run-101 window FULLY CLOSED in-run after a/b3 re-runs "
            f"(1589/1589, {tot_logs_effective} logs, 2 hits - both sent-pass duplicates, 0 failed after same-run retry of 3 failed contracts).",
    "rotations": "TWO NEW, both NAMED (anomaly): 0x4727e091d34665249bfbdc1575c7180d19527777 (Forever Laura/Laura, 27 wallets, first buy 19:37:59 WIB) + "
                 "0x1e9c6d463a096320df3ad60754344b2735a37777 (Seatbelt Dog/Seatbelt, 27 wallets, first buy 20:13:01 WIB). Sets byte-identical, diff 0 vs "
                 "run-100 machine set. All paid-only with no free-mint path; auto-mint blocked at guard (c); reported once as signal per fast-path "
                 "amendment (name/symbol appeared). 1e9c rotation STILL FILLING at window end (24/27 sell wallets) - watch run 102 the same way, NOT a new rotation.",
    "other_paid_activity": [
        {
            "pattern": "23 tokens x 3 wallets, all the same churn trio 0x3803/0xad94/0xc7c5, all ...7777 (PCS micro buy-then-sell)",
            "wallet": "churn trio (see paid_trend_run1 for the pattern)",
        },
        {
            "pattern": "11 tokens x 2 wallets, both 0x3628764a6576b8dfb31fba0aac6a333b64851423 + 0xa0c1e94fbc1a93e39f5eb828f960aa080a9d9b9e, all ...7777",
            "wallet": "0x3628764a6576b8dfb31fba0aac6a333b64851423 + 0xa0c1e94fbc1a93e39f5eb828f960aa080a9d9b9e",
        },
        {
            "pattern": "20 tokens x 1 wallet (PCS micro buys)",
            "wallet": "see pattern",
        },
        {
            "pattern": "7 txs via 0x296b00198dc7ec3410e12da814d9267bb8df506a (selector 0x27772d13), receiving tokens from pair contracts (swap-like, not mints); total value 0.3 BNB",
            "wallet": "0x2325f175975abdbcde555c79cc8e63381d28551b",
        },
        {
            "pattern": "44 txs via aggregator 0x855066c8679c77a0258e792b5ccf19f8c227eb31 (selector 0x39ecce49) + 22 approvals, total value 0.0006 BNB (churn as usual)",
            "wallet": "0x38031ca8a54526f9fe90f11f07b55ae5fc01036a",
        },
        {
            "pattern": "17 AFeng sale-calls (0x4d819a2a) to 0x1de4... total 4.125 BNB; 2 of them carry the known-repeat 0x636f dividend-tracker mint log (0x522c... 0.5 BNB + recovered 0x62fb... 1 BNB) - NOT new mints per the state note",
            "wallet": "0xbf004bff64725914ee36d03b87d6965b0ced4903 (AFeng)",
        },
    ],
}

s["inbound_log_leg_run101"] = {
    "contracts": 1589,
    "attempted": 1589,
    "completed_with_0_hits": 1588,
    "total_logs": tot_logs_effective,
    "hits": 2,  # both on the same contract (0x636f tracker) - sent-pass duplicates, 0 inbound-only new
    "failed": eff_failed,
    "failed_contracts": [],
    "failed_then_recovered_same_run": failed_contracts,
    "never_attempted": 0,
    "complete": eff_failed == 0,
    "note": "Ankr getLogs address-filtered per contract, window 132192617-132208026, from list run101-inbound-contracts.json (1589 contracts = run100 list "
            f"1552 + 35 run-101 deployments + 2 new rotation tokens). Full pass a (400, 8,791 logs, 2 failed, 6 truncated) + "
            f"b1 (200, 4,052 logs, 0 failed, 3 truncated) + b2 (200, 2,450 logs, 0 failed, 0 truncated) + b3 (789, 2,882 logs, "
            f"1 failed, 0 truncated) + retry (3 contracts, 0 logs, 0 hits - the 3 in-chunk failures 0x3fd85ca8..., 0x563a23b9..., 0x846f8a0f... recovered "
            f"3/3 same-run) = {tot_logs_effective} logs, 2 hits, 0 FAILED after retry. "
            "The 2 hits are BOTH the sent-pass AFeng tracker txs (0x522c... block 132203234 + 0x62fb... block 132198457) - 0 inbound-only new mints. "
            "Truncated contracts, all topic-filtered to 0 logs (a: 0x10b3... moco, 0x1de4... AFeng sale, 0x3dca..., 0x55d398... USDT, 0x6288... AGC sale, "
            "0x636fdfa9... tracker - same set as runs 91-100; b1: 0x63de... AGC, 0x7857..., 0x7e2d...; b2/b3: none). Chunks a/b3 FIRST attempt WEDGED on proxy "
            "sockets (logs frozen >5 min, live processes, fresh Ankr calls working 7-15s), killed by PID + re-launched from scratch; SECOND attempt (-2) "
            "ALSO wedged ~contract 350 on a/b3, killed by PID + re-launched from scratch as -3; -3 completed (a 400/400, b3 789/789). All four chunks hit "
            "repeated joint Ankr stalls (logs frozen minutes, live processes, then resuming - run-95/100 pattern). Window FULLY CLOSED in-run, no retry "
            "deferred to run 102."
            if eff_failed == 0 else
            "Window NOT fully closed: failed contracts must be retried in run 102.",
}

# ---- machine tokens: 2 new entries ----
new_entries = [
    {
        "address": "0x4727e091d34665249bfbdc1575c7180d19527777",
        "first_seen": "run-101, 2026-11-07 19:37:59 WIB (tx 0xf55b760fe1..., block 132201955)",
        "machine_wallets": 27,
        "typical_first_buy_bnb": 0.000123025,
        "followup_buy_range_bnb": "median 0.225521877, max 0.313274, total buys 8.9392 BNB (51 sent buys)",
        "label": "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - NAMED (Forever Laura / Laura) - ANOMALY, reported once as signal run 101",
        "note": "ANOMALY under the fast-path amendment: name/symbol APPEARED - name 'Forever Laura', symbol 'Laura', confirmed via fast_rpc; totalSupply 1e27; "
                "decimals 18. DexScreener independently confirms Forever Laura/Laura, pair 0xf4ee6a9b528670fcdce10c8af0f5262b4fef1d3d, pair created 1h 5m ago, "
                "216 txns, volume $17K, buys 82/sells 134, liquidity <$1 (drained after the rotation's sells), pooled Laura 59,594,490 + WBNB 0.00005421. "
                "First buy 19:37:59 WIB by 0xcb08c02c0a, 0.000123025 BNB -> 9,820.29 tokens. Wallet set byte-identical to the other run-101 rotation and diff 0 "
                "vs the run-100 machine set (27/27 overlap). Buy sizes WITHIN class norm - NOT a size anomaly. 96 sells / 27 sell wallets in-window - rotation "
                "fully dumped. Pair token0/token1 NOT read run 101 (fast_rpc race outage) - retry run 102. Auto-mint BLOCKED at guard (c) - paid PCS token, "
                "no free-mint path. Do not re-signal unless a new fact appears.",
    },
    {
        "address": "0x1e9c6d463a096320df3ad60754344b2735a37777",
        "first_seen": "run-101, 2026-11-07 20:13:01 WIB (tx 0x750d1944ad..., block 132206622)",
        "machine_wallets": 27,
        "typical_first_buy_bnb": 0.000123025,
        "followup_buy_range_bnb": "median 0.223364190, max 0.416612, total buys 9.4726 BNB (57 sent buys)",
        "label": "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - NAMED (Seatbelt Dog / Seatbelt) - ANOMALY, reported once as signal run 101",
        "note": "ANOMALY under the fast-path amendment: name/symbol APPEARED - name 'Seatbelt Dog', symbol 'Seatbelt', confirmed via fast_rpc (name pass 1; "
                "symbol/totalSupply/decimals retried OK after pass-1 'all endpoints failed'); totalSupply 1e27; decimals 18. DexScreener independently "
                "confirms Seatbelt Dog/Seatbelt, pair 0x533623ca2db657de9a36e84e2b5a809fbee7ecbe, pair created 30m ago, 227 txns, volume $18K, buys 89/sells 138, "
                "liquidity <$1 (drained after the rotation's sells), pooled Seatbelt 78,070,146 + WBNB 0.00004286. First buy 20:13:01 WIB by 0xcb08c02c0a, "
                "0.000123025 BNB -> 9,826.24 tokens. Wallet set byte-identical to the other run-101 rotation and diff 0 vs the run-100 machine set (27/27 "
                "overlap). Buy sizes WITHIN class norm - NOT a size anomaly. 87 sells / 24 sell wallets in-window - rotation STILL FILLING at window end "
                "(debuted 20:13:01 WIB late in the window). Pair token0/token1 NOT read run 101 (fast_rpc race outage) - retry run 102. Auto-mint BLOCKED "
                "at guard (c) - paid PCS token, no free-mint path. Do not re-signal unless a new fact appears.",
    },
]
s.setdefault("machine_tokens", []).extend(new_entries)

# update stalled labels' run ranges
for e in s["machine_tokens"]:
    if e["address"].lower().startswith("0x1153607e"):
        e["label"] = "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - rotation STALLED at 26 wallets (runs 91-101)"
    if e["address"].lower().startswith("0x79cd174c"):
        e["label"] = "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - rotation STALLED at 20 wallets (runs 90-101)"

# signaled projects: append the two (paid-only)
s.setdefault("signaled_projects_over_20pct", []).extend([
    "Forever Laura (Laura) 0x4727e091d34665249bfbdc1575c7180d19527777 (paid-only, machine-token, run-101, NAMED - anomaly reported once as signal)",
    "Seatbelt Dog (Seatbelt) 0x1e9c6d463a096320df3ad60754344b2735a37777 (paid-only, machine-token, run-101, NAMED - anomaly reported once as signal)",
])

# ---- next run note ----
note = (
    "Next run sent-tx window starts from block 132208027. "
    "RETRY run 102: (1) Pair token0/token1 reads for 0xa6e6... pair 0x9fac925655fa4985ab4fe2fe9e0ca8ae323cc9da and 0x887c... pair "
    "0xa9fa6efb21c252b7d4ab81d19a07ee4ecf6d2c97 (fast_rpc race returns None / 'all endpoints failed', 19 consecutive runs - persistently unreadable, "
    "unverified not absence), plus 0x2bfb pair 0x782671f637bf1a01de482824c4b2520bc58a5a4b, 0xc459 pair 0xeca06856c88fcdf1506886431a079d3f2565ca82, and "
    "rotation 0x43c8 pair 0xaafebb5244e2e546f7cd18a2c89f85bbee03f1e0 (unreadable run 88-101, 14 consecutive - retry opportunistically, not an anomaly), "
    "PLUS run-89 rotation pairs 0xcfdb 0x1e04925db4eabab2917ef73a8cdf232bcc69b5ba, 0x0cf8 0xf6800c4a1ecdffbd64f9047c606bdb32dee0127f, 0xe68b "
    "0xfab7cb4979c9e4738afc61e4974177cf72c50896 (token0/token1 unreadable run 89-101, 13 consecutive; 0x31e4 pair 0x60ca0aef... READ OK run 89), PLUS "
    "run-101 rotation pairs 0x4727 0xf4ee6a9b528670fcdce10c8af0f5262b4fef1d3d + 0x1e9c 0x533623ca2db657de9a36e84e2b5a809fbee7ecbe (NOT read run 101 - fast_rpc "
    "race outage; DexScreener confirms both PCS V2 token/WBNB pairs); db49 pair 0x41cbb4910fd4959f651d7bff8d8b5ed5cd355dfc READ OK run 101 (token0 = WBNB, "
    "token1 = db49 token) - REMOVED from retry; ff66 pair 0x2d3e053bada0378299010fde9f59209985760bab READ OK run 101 (token0 = WBNB, token1 = ff66 token) - "
    "REMOVED from retry; 0x6b12 pair READ OK run 100 - already removed; 0x50e4 pair READ OK run 99 - already removed; 41cc pair READ OK run 99 - already "
    "removed; run-97 rotation pairs c90a/e3a8 READ OK run 98 - already removed; run-100 pairs 6f31 0xc9299379d122a1a84d45fdf1ee87dd0ce1a5e3e8 + 0d7e "
    "0x98fe67c6aeb645e6c9aa41c1fd79898261e7fde7 READ OK run 100 (token0 = token, token1 = WBNB) - no retry needed. "
    "(2) Run-101 inbound list = run100 list (1552) + 35 run-101 deployments + 2 new rotation tokens (total 1589); run-102 inbound list = run101 list (1589) "
    "+ run-102 deployments + new rotation tokens. "
    "(3) Run-101 inbound window FULLY CLOSED in-run (1589/1589, 2 hits - both sent-pass duplicates, 0 failed after same-run retry of 3 failed contracts - "
    "verify at state-update time; if the retry had failures, they are listed in inbound_log_leg_run101.failed_contracts and must be retried in run 102). "
    "(4) 0x1e9c6d46... rotation STILL FILLING at window end (24/27 sell wallets, debuted 20:13:01 WIB late in the window) - watch run 102 the same way, "
    "do NOT treat continuation as a new rotation. 0xdb4950e7... rotation COMPLETED run 100 (sell-wallet union run99+run100 = 27/27) - do NOT treat any db49 "
    "activity as a new rotation. 0x1153607e... rotation STALLED at 26 wallets (0 wallets runs 91-101, 11th quiet run after debut) - watch run 102 the same "
    "way. 0x79cd... STALLED at 20 wallets (0 wallets runs 90-101, 12th quiet run after debut) - same. Run-100 named rotations 0x6f31.../0x0d7e...: "
    "0 wallets run 101 (1st quiet run after debut) - watch run 102 the same way. Run-99 named rotations 0x50e4.../0x6b12.../0xff66...: 0 wallets run 101 "
    "(2nd quiet run after debut) - same. Run-98 named rotations 0x41cc.../0x43bc.../0x2120.../0xda79...: 0 wallets run 101 (4th quiet run after debut) - same. "
    "Run-97 named rotations 0xc90a.../0xe3a8...: 0 wallets run 101 (4th quiet run after debut) - same. "
    "Dedupe new mints against all tx hashes in reported_findings (223 mint entries over 221 unique tx hashes, direct count run 77). Run-75 mint tx "
    "0x23cd8740... (AFeng, tracker 0x636f..., 0.15 BNB) is a KNOWN REPEAT of the run-70 finding - do not report as new if it repeats again. Run-101 added "
    "TWO more repeats of the same pattern (0x522c6c82... 0.5 BNB + 0x62fb2bb4... 1 BNB, both AFeng sale-calls with 0x636f tracker mint logs) - also NOT new. "
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
    "run 100 (TWO NEW rotations 0x6f31... Nigga Its Over/NIO + 0x0d7e... 癫猫/癫猫 at 27 wallets each - BOTH NAMED, fourth consecutive run with named "
    "rotations, anomaly reported once as signal run 100; buy sizes in class norm; both fully dumped in-window (100/98 sells, 27 sell wallets each); "
    "50e4/6b12/ff66 0 wallets (1st quiet run after debut); db49 rotation COMPLETED (sell-wallet union run99+run100 = 27/27, NOT a new rotation); "
    "41cc/43bc/2120/da79 0 wallets (3rd quiet run); c90a/e3a8 0 wallets (3rd quiet run); 0x1153... STALLED at 26, 10th quiet run; 0x79cd... STALLED at 20, "
    "11th quiet run; 32 deployments (fourth straight run with deployments, 0xaa49e7fe alone 5); inbound FULLY CLOSED in-run after b3 re-run from scratch "
    "as b3-2 (b3 first attempt died silently ~contract 688, Ankr 'Remote end closed connection' on 0x0ba97102...), 1552 contracts, 0 hits, 0 failed; "
    "run-99 NULL creation receipt RECOVERED (tx 0x21c210df..., status 1, block 132171801, contract 0x7ad2271298c0d7b5510ff5eed079edce0911bbb1); 6b12 pair "
    "READ OK run 100 - removed from retry list) "
    "run 101 (TWO NEW rotations 0x4727... Forever Laura/Laura + 0x1e9c... Seatbelt Dog/Seatbelt at 27 wallets each - BOTH NAMED, fifth consecutive run "
    "with named rotations, anomaly reported once as signal run 101; buy sizes in class norm; 4727 fully dumped in-window (96 sells, 27 sell wallets), "
    "1e9c STILL FILLING at window end (87 sells, 24 sell wallets, debuted 20:13:01 WIB late in the window); 6f31/0d7e 0 wallets (1st quiet run after "
    "debut); 50e4/6b12/ff66 0 wallets (2nd quiet run); 41cc/43bc/2120/da79 0 wallets (4th quiet run); c90a/e3a8 0 wallets (4th quiet run); 0x1153... STALLED "
    "at 26, 11th quiet run; 0x79cd... STALLED at 20, 12th quiet run; 35 deployments (fifth straight run with deployments, 0xaa49e7fe + 0x64e893a4 4 each); "
    "inbound FULLY CLOSED in-run after a/b3 re-runs from scratch TWICE (first attempt + -2 both wedged ~contract 350, -3 completed), 1589 contracts, "
    "18,175 logs, 2 hits (both sent-pass duplicates - the AFeng tracker txs), 0 failed after same-run retry of 3 failed contracts; run-101 NULL receipt "
    "(0x62fb2bb4...) RECOVERED same-run (status 1, block 132198457, 43 logs - contains the known-repeat 0x636f tracker mint log); db49/ff66 pairs READ OK "
    "run 101 (token0 = WBNB, token1 = token) - removed from retry list; new run-101 pairs 4727/1e9c NOT read (fast_rpc race outage) - retry run 102) "
    "auto-mint BLOCKED at guard (c) - do not re-signal or re-report the block unless a new mint/buy fact appears for those contracts (e.g. a genuine "
    "free-mint path). Per the 2026-11-06 ~18:30 machine-token fast-path amendment, routine machine-token rotations are recorded in state WITHOUT a chat "
    "report (no full verification per run); report only on anomaly (buy size far off norm, name/symbol appears, website, or free-mint path). "
    "Paid fact: run101 TWO NEW rotations 0x4727... (Forever Laura/Laura) + 0x1e9c... (Seatbelt Dog/Seatbelt) at 27 wallets each - BOTH NAMED, fifth "
    "consecutive run with named rotations (anomaly: name/symbol appeared; reported once as signal run 101, paid-only, auto-mint blocked guard (c)); "
    "run-100 tokens 0x6f31.../0x0d7e... 0 wallets (1st quiet run after debut); run-99 tokens 0x50e4.../0x6b12.../0xff66... 0 wallets (2nd quiet run after "
    "debut); run-98 tokens 0x41cc.../0x43bc.../0x2120.../0xda79... 0 wallets (4th quiet run after debut); run-97 tokens 0xc90a.../0xe3a8... 0 wallets (4th "
    "quiet run after debut); run-90 tokens 0x6a25.../0x9f7e.../0x8c64.../0xc1ab.../0x1153... 0 wallets (11th quiet run after debut); run-89 tokens "
    "0xcfdb.../0x0cf8.../0xe68b.../0x31e4... 0 wallets (12th quiet run after debut); run-88 tokens 0x43c8.../0x3d12.../0xeae0... 0 wallets (13th quiet run "
    "after debut); run-87 tokens 0x889a.../0x4249... 0 wallets (14th quiet run after debut); run-86 tokens 0x2bfb.../0xc459... 0 wallets (15th quiet run "
    "after debut); run-85 token 0x2717... 0 wallets (16th quiet run); run-82 tokens 0xd468.../0xa6e6.../0x887c... all 0 wallets (19th quiet run after debut); "
    "run-81 tokens 0 wallets (20th quiet run); run-80 token 0 wallets (21st quiet run); GrokBot 0xfcd0... absent (0 wallets) - 42nd consecutive quiet run "
    "(59, 61-101) after the run-60 burst; CORLA-97af 0 wallets; CORLA 0x4a9c 0 wallets; all run-64/65 ASI contracts 0 wallets; all run-66/68/69/70/71/72/73/74/75/76/77/78/79 "
    "machine tokens 0 wallets. Run 101 had 35 deployments (fifth straight run with deployments; 0xaa49e7fe + 0x64e893a4 4 each; added to the inbound list "
    "for run 102 - all 35 addresses recovered from RAW receipts, 0 NULL receipts after same-run recovery of the 1 null). AFeng 22 txs (17 sale-calls + 5 "
    "approvals, total value 4.125 BNB); future1001.ai 0 txs; 0x2325... 11 txs (7 aggregator 0x27772d13 + 4 approvals, total value 0.3 BNB); 0x8e96... 0 txs; "
    "0x3803... 66 txs (44 aggregator 0x39ecce49 + 22 approvals, total value 0.0006 BNB, churn as usual). PARSER LESSON (run 101): runNN-receipts.py NEVER "
    "extracts contractAddress - deployments must be read from runNN-receipts-partial.json raw receipts; the parsed JSON '0 deployments' reading was wrong. "
    "PROCESS LESSON (run 101): inbound chunks a/b3 wedged TWICE (first attempt + -2 re-run both froze ~contract 350); -3 attempt completed. A frozen log "
    "mtime with a live process is a stall, not a death - wait before re-running (stalls resolved on their own within ~5 min several times this run); a log "
    "frozen >5 min with NO live process is a silent death - re-run the chunk from scratch; a socket wedged >5 min while fresh calls work is a wedge - "
    "kill by PID (pkill -f can match the wrapper shell itself, use kill <pid>) and re-run the chunk from scratch. fast_rpc race OUTAGE (run 101): "
    "all-endpoint TimeoutError/OSError flapping ~21:00-22:00 WIB - token-meta pass 1 failed entirely, null-receipt retry failed twice, pair-retry 8/10 "
    "failed; later retries succeeded (token-meta pass 2 + targeted 1e9c retry, null receipt, db49/ff66 pairs). A failed race read is UNVERIFIED, never "
    "absence - retry, don't conclude. "
    "SCRIPT FIX (run 100): run100-rotation-analysis.py sell counting fixed (old `to in wallets` filter counted 0 sells because a PCS sell transfers "
    "wallet->pair; run99's rotation-analysis.json also records n_sells 0 for db49) - now counts SELL_SEL txs whose receipt logs touch the token; "
    "run 101 copied the FIXED script via sed. "
    "INBOUND FILENAME QUIRK FIXED run 88: chunk output files are now correctly named run93-inbound93-{a,b1,b2,b3}.json. Same-owner factory groups now also "
    "include 0x293f and 0x1103 (proven 2026-11-06 ~01:14 WIB, AGENTS.md) alongside the groups listed in the body."
)
s["next_run_note"] = note

json.dump(s, open(P, "w"), indent=1)
print("state updated; last_run now:", s["last_run"]["run"], "block_end:", s["last_run"]["block_end"])
print("machine_tokens:", len(s.get("machine_tokens", [])), "| signaled:", len(s.get("signaled_projects_over_20pct", [])))
print("inbound101 complete:", s["inbound_log_leg_run101"]["complete"], "| failed:", s["inbound_log_leg_run101"]["failed"],
      "| total_logs:", s["inbound_log_leg_run101"]["total_logs"], "| hits:", s["inbound_log_leg_run101"]["hits"])
print("inbound100 complete:", s["inbound_log_leg_run100"]["complete"], "| failed:", s["inbound_log_leg_run100"]["failed"])
