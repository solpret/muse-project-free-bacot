#!/usr/bin/env python3
"""Run 100 state update (read-only job bookkeeping; no chain writes).

Completes run 100 (window 132179369-132192616, tx 2026-11-07 16:48:43 - 18:27:56 WIB).
Sent/receipts/paid done and verified; inbound leg run-100 window CLOSED in-run
(1552/1552, 0 hits - chunks a/b1/b2 first attempt, b3 died silently ~contract 688
and re-run from scratch as b3-2).
NO new mints. TWO NEW machine-token rotations at 27 wallets each - BOTH NAMED
(Nigga Its Over / NIO + 癫猫 / 癫猫), the FOURTH consecutive run with named
rotations (run 97 had 2, run 98 had 4, run 99 had 4, run 100 has 2): anomaly under
the fast-path amendment, reported ONCE as a paid-only signal (not a lead, not a buy
recommendation, auto-mint blocked at guard (c)). 32 deployments this run
(fourth straight run with deployments; 25/72/64/32). Bridge unchanged
(0 new mints, 0 not_evaluated). Run-99 NULL creation receipt RECOVERED this run:
tx 0x21c210df... status 1, block 132171801, contract 0x7ad2271298c0d7b5510ff5eed079edce0911bbb1.
db49 rotation COMPLETED this run (sell-wallet union run99+run100 = 27/27).
"""
import json, shutil

P = "/home/hatch/workspace/narrative-pulse/tracked-wallet-mint-scan-state.json"
shutil.copy(P, str(P) + ".bak-run100-pre")
s = json.load(open(P))
SR = "/home/hatch/workspace/narrative-pulse/scan-runs"

# ---- inbound totals from chunk JSONs (self-verifying) ----
chunks = {}
for part in ["a", "b1", "b2", "b3-2"]:
    chunks[part] = json.load(open(f"{SR}/run100-inbound100-{part}.json"))
tot_contracts = sum(c["contracts_checked"] for c in chunks.values())
tot_logs = sum(c["total_logs"] for c in chunks.values())
tot_hits = sum(len(c["hits"]) for c in chunks.values())
tot_failed = sum(len(c["failed"]) for c in chunks.values())
tot_trunc = sum(len(c["truncated"]) for c in chunks.values())
print(f"inbound totals: contracts={tot_contracts} logs={tot_logs} hits={tot_hits} failed={tot_failed} truncated={tot_trunc}")
assert tot_contracts == 1552, f"inbound contracts {tot_contracts} != 1552"
assert tot_hits == 0, f"inbound hits {tot_hits} != 0 (must handle before state update!)"
failed_contracts = [f for c in chunks.values() for f in c["failed"]]
# same-run single-contract retry for the b3-2 failure (run-97 precedent)
retry_path = f"{SR}/run100-inbound100-b3-retry.json"
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

last_run_100 = {
    "run": 100,
    "block_start": 132179369,
    "block_end": 132192616,
    "window_wib": "2026-11-07 16:48:43 - 18:27:56 WIB (tx times); run executed ~18:26 - ~20:16 WIB; sent-pass in-window txs 856, 0 mint-pattern txs",
    "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set); 0 failed, no retry needed.",
    "method_note": (
        "Sent pass Ankr ankr_getTransactionsByAddress via module: FIRST attempt completed 55/55 OK, 856 txs, 34 wallets active, 0 failed. "
        "Receipts via fast_rpc batch (6, ~4s pause) for 547 non-approve candidates: 546 status 1, 1 status 0 (failed PCS sell 0x791ac947 by 0xdb2d83f9, "
        "tx 0xe2cfe08125..., 17:01:42 WIB), 0 null, 0 mint logs. Receipts completed in one attempt, no resume needed. "
        "Paid: 42 tokens; max 27 wallets/token (TWO new rotations at 27 each - see anomaly signal; 21 tokens at 3 wallets, ALL the same churn trio "
        "0x3803/0xad94/0xc7c5, all ...7777; 10 at 2 (the 0x3628/0xa0c1 pair); 9 at 1 (incl. db49 tail buy by 0x9cdd08f3). Only 2 tokens overlap run-99's "
        "42 paid tokens (0xa9d3d7... + db49) - the ...7777 churn set turns over every run. "
        "NEW ROTATIONS - ANOMALY (named tokens, FOURTH consecutive run - run 97 had 2 named, run 98 had 4, run 99 had 4, run 100 has 2): "
        "0x6f31f7cf4a3fe26f1b849d71c146e4fc08ea7777 (Nigga Its Over / NIO), "
        "0x0d7e74c412c3bb4b32459f0f25efbe49c43e7777 (癫猫 / 癫猫). "
        "Both: name+symbol confirmed via fast_rpc (6f31 pass 1; 0d7e name/symbol pass 1, totalSupply pass 1 ERROR 'all endpoints failed' then RETRIED OK "
        "1e27), totalSupply 1e27, decimals 18. DexScreener independently confirms both (same names/symbols, pairs match the on-chain log-derived pair "
        "addresses, liquidity $0.07 each - drained after the rotation's sells; 6f31 h6 buys 88/sells 138, vol $18,680.30; 0d7e h6 buys 85/sells 137, "
        "vol $18,165.41; both price -99.99% h6). "
        "Both bought by the SAME 27-wallet machine set, byte-identical to each other and diff 0 vs the run-99 machine set (27/27 overlap). "
        "Buy sizes WITHIN class norm (NOT a size anomaly): first buy 0.000121125 BNB -> 9,674.63 tokens each; follow-up medians 0.223378725 for BOTH; "
        "max 0.422068 (6f31) / 0.389734 (0d7e); totals 9.6850 / 9.2907 BNB; buys 58/55, sells 100/98 (27 sell wallets each - BOTH rotations fully dumped "
        "in-window). First buys: 0d7e 17:01:07 WIB by 0xcb08c02c0a tx 0x145ac13be3... block 132181044 pair 0x98fe67c6aeb645e6c9aa41c1fd79898261e7fde7; "
        "6f31 17:24:09 WIB by 0xcb08c02c0a tx 0x98defacdac... block 132184115 pair 0xc9299379d122a1a84d45fdf1ee87dd0ce1a5e3e8. Pair token0/token1: BOTH "
        "READ OK run 100 (token0 = the token, token1 = WBNB 0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c). Trigger >25% met numerically (27 >= 14) but "
        "AUTO-MINT BLOCKED at guard (c): paid PCS tokens, no free-mint path; guard (a) website also unverified. No preview, no execution. "
        "SCRIPT FIX (run 100): run100-rotation-analysis.py sell counting was broken (required the token Transfer's `to` to be a tracked wallet, but a "
        "PCS sell transfers wallet->pair, so it counted 0 sells - run99's rotation-analysis.json also records n_sells 0 for db49 while its state text "
        "cites 64 sells from a manual count). Patched to count SELL_SEL txs whose receipt logs touch the token; re-ran - now 6f31 100 sells / 0d7e 98 "
        "sells, both 27 sell wallets. Next runs copy the FIXED script via sed. "
        "db49 rotation COMPLETED this run (NOT a new rotation): 26 sell txs / 25 wallets + 1 buy tx (0x9cdd08f301, 16:48:43 WIB) in run 100; sell-wallet "
        "union run99 (23) + run100 (25) = 27/27. "
        "Deployments: 32 contract creations by 13 machine-set wallets (0xaa49e7fe 5; 0x3154f694/0xcb08c02c/0x1cce4ec5/0x9b519f5d/0x97bd895f 3 each; "
        "0xdb2d83f9/0x3a39aa05/0x5b4beded/0xc0c84518/0x64e893a4 2 each; 0xc6219468/0xf795c525 1 each) - FOURTH straight run with deployments "
        "(25 run 97, 72 run 98, 64 run 99, 32 run 100); all 32 deployed addresses recovered from receipts, added to the inbound list "
        "(run100-inbound-contracts.json, total 1552) along with the 2 new rotation tokens and the RECOVERED run-99 creation 0x7ad2271298c0d7b5510ff5eed079edce0911bbb1. "
        "Run-99 NULL creation receipt RECOVERED run 100: tx 0x21c210dfea7439ddd710e9c758191c4ad5c0be98e449097c6a338b50dc09c3d3 (wallet 0x3154f694, "
        "15:51:47 WIB run-99 window) status 1, block 132171801, contractAddress 0x7ad2271298c0d7b5510ff5eed079edce0911bbb1, gasUsed 0x12395 - no longer "
        "unverified; added to the run-100 inbound list. The 2 rotation tokens are NOT among the deployments. "
        "AFeng (0xbf004bff...) 0 txs; future1001.ai 0 txs; 0x2325... 8 txs (5 aggregator 0x27772d13 + 3 approvals 0x095ea7b3, total value 0.09 BNB); "
        "0x8e96... 0 txs; 0x3803... 60 txs (39 aggregator 0x39ecce49 + 21 approvals, total value 0.000546 BNB, churn as usual). 1 plain BNB transfer: "
        "0x537ac4c93a5e... by 0xc7c5faa270 to 0x7f51d4642399aaa0a4a0e3c202c53bf8cdfd82f8, 0.000129 BNB, 17:04:46 WIB. "
        "Selectors (sent pass, 856 txs): 288 PCS sells (0x791ac947) + 182 PCS buys (0xb6f9de95) + 32 contract creations (0x60806040) + 39 aggregator "
        "(0x39ecce49) + 5 aggregator (0x27772d13) + 309 approvals (0x095ea7b3, not in receipt candidates) + 1 empty-input (plain BNB transfer). "
        "Nonzero-value txs 238, total 20.5439 BNB, max 0.4221 BNB (6f31 follow-up buy). Most active wallets: 0xad94ee77 63 txs, 0x38031ca8 60, "
        "0xc7c5faa2 58, 0xa952331e 40, 0x9cdd08f3 39, 0xc6219468 38, 0xa0c1e94f 29, 0xe9ed24db 28, 0x3628764a 28, 0xf795c525 27, 0x1cce4ec5 27, 0xfdec62fd 26. "
        "0 NULL receipts this run (vs 3 in run 99). 1 status-0 tx, a failed PCS sell (see above). "
        f"Inbound leg (amendment 12:02 WIB): Ankr getLogs address-filtered per contract, 1552 contracts (run99 list 1517 + 32 run-100 deployments + "
        f"2 new rotation tokens + 1 recovered run-99 creation), 0 hits, {tot_logs} logs, window 132179369-132192616. "
        f"Chunk a (400, 8,009 logs, 0 failed, 5 truncated) + b1 (200, 3,773 logs, 0 failed, 3 truncated) + b2 (200, 1,829 logs, 0 failed, 1 truncated) + "
        f"b3-2 (752, {chunks['b3-2']['total_logs']} logs, 1 failed in-chunk, 0 truncated) + b3-retry (1 contract, 0 logs, 0 failed - the b3-2 failure "
        f"0xd987945d1df5fcd111155bf9c494faade3f91e3e recovered same-run) = {tot_logs_effective} logs, "
        f"0 hits, 0 FAILED after retry. "
        "Truncated contracts, all topic-filtered to 0 logs (a: 0x1de4... AFeng sale, 0x3dca..., 0x55d398... USDT, 0x6288..., 0x636fdfa9... tracker - same "
        "set as runs 91-99; b1: 0x63de... AGC, 0x7857..., 0x7e2d... (NEW truncated this run); b2: 0xb40e... (NEW truncated this run)). "
        "b3 FIRST attempt DIED SILENTLY at ~contract 688 (log ends with Ankr 'Remote end closed connection' ERROR on 0x0ba97102b878f77b958ce9f442d75a725b94c886, "
        "no JSON, no process - same service-restart pattern as runs 94/96/97/99); re-run from scratch as b3-2 (read-only, idempotent) and completed clean. "
        "All four chunks hit repeated joint Ankr stalls this run (logs frozen minutes at a time with live processes, then resuming - same pattern as run 95); "
        "no chunk was killed or re-run for stalling alone. "
        "Pair a6e6/887c/2bfb/c459/43c8/cfdb/0cf8/e68b STILL unreadable: token0()/token1() for all eight pairs failed via fast_rpc race "
        "('all endpoints failed') in run100-pair-retry.py - unverified, not absence; 18th consecutive run for a6e6/887c/2bfb/c459, 13th for 43c8, "
        "12th for cfdb/0cf8/e68b; retry run 101. BUT the 6b12 pair READ OK this run (token0 = the token 0x6b12..., token1 = WBNB) - REMOVED from the "
        "retry list; db49/ff66 token1 = token READ OK, token0 still unreadable - retry run 101. New run-100 pairs 6f31/0d7e READ OK (token0 = token, "
        "token1 = WBNB). "
        "Pointer-discovery (amendment 19:10): 0 contracts processed - no new mints this run, and the backfill queue is empty (bridge 115 contracts, "
        "0 not_evaluated); bridge unchanged. CHAT REPORT this run: the two-named-machine-token anomaly signal (paid-only, NOT a lead, NOT a buy "
        "recommendation, auto-mint blocked guard (c)) - reported once per the fast-path amendment. No new mints, no Free Bacot signal beyond that, "
        "no auto-mint trigger execution. No preview/mint/sign/login/purchase by this job."
    ),
}
s["last_run"] = last_run_100

# ---- paid signal + trend ----
s["paid_signal_run100"] = {
    "note": "ANOMALY SIGNAL (paid-only, NOT a buy recommendation, NOT a Free Bacot lead, NOT an auto-mint trigger). FOURTH consecutive run with NAMED "
            "machine-token rotations - now TWO at once (run 97 had 2, run 98 had 4, run 99 had 4, run 100 has 2): the machine set bought TWO tokens "
            "that HAVE on-chain name/symbol, breaking the unnamed pattern of all 24 pre-run-97 machine tokens. Reported once per the fast-path "
            "amendment (name/symbol appeared). Auto-mint BLOCKED at guard (c) for both (paid PCS tokens, no free-mint path). Do not re-signal "
            "unless a new fact appears (e.g. a genuine free-mint path).",
    "tokens": [
        {
            "address": "0x6f31f7cf4a3fe26f1b849d71c146e4fc08ea7777",
            "name": "Nigga Its Over",
            "symbol": "NIO",
            "wallets": 27,
            "first_buy": "2026-11-07 17:24:09 WIB, 0.000121125 BNB -> 9,674.63 tokens, wallet 0xcb08c02c0a, tx 0x98defacdac..., block 132184115",
            "pair": "0xc9299379d122a1a84d45fdf1ee87dd0ce1a5e3e8 (PCS V2; token0/token1 READ OK run 100: token0 = token, token1 = WBNB)",
            "buys": "58 sent buys, median follow-up 0.223378725 BNB, max 0.422068 BNB, total 9.6850 BNB; 100 sells / 27 sell wallets (fully dumped in-window)",
            "verification": "name+symbol confirmed via fast_rpc; totalSupply 1e27; decimals 18; DexScreener Nigga Its Over/NIO, liq $0.07, price -99.99% h6, vol $18,680.30 h24, pair created ~17:24 WIB",
        },
        {
            "address": "0x0d7e74c412c3bb4b32459f0f25efbe49c43e7777",
            "name": "癫猫",
            "symbol": "癫猫",
            "wallets": 27,
            "first_buy": "2026-11-07 17:01:07 WIB, 0.000121125 BNB -> 9,674.63 tokens, wallet 0xcb08c02c0a, tx 0x145ac13be3..., block 132181044",
            "pair": "0x98fe67c6aeb645e6c9aa41c1fd79898261e7fde7 (PCS V2; token0/token1 READ OK run 100: token0 = token, token1 = WBNB)",
            "buys": "55 sent buys, median follow-up 0.223378725 BNB, max 0.389734 BNB, total 9.2907 BNB; 98 sells / 27 sell wallets (fully dumped in-window)",
            "verification": "name+symbol confirmed via fast_rpc; totalSupply 1e27 (first read ERROR 'all endpoints failed', retried OK); decimals 18; DexScreener 癫猫/癫猫, liq $0.07, price -99.99% h6, vol $18,165.41 h24, pair created ~17:01 WIB",
        },
    ],
}

s["paid_trend_run100"] = {
    "note": "Aggregate only, NOT a buy recommendation. TWO NEW machine-token rotations at 27 wallets each - BOTH NAMED (Nigga Its Over/NIO, 癫猫/癫猫), "
            "FOURTH consecutive run with named rotations (run 97 had 2, run 98 had 4, run 99 had 4): anomaly reported once as a paid-only signal "
            "(paid_signal_run100); buy sizes in class norm; both fully dumped in-window (100/98 sells). Run-99 named rotations 50e4/6b12/ff66 0 wallets "
            "(1st quiet run after debut); db49 rotation COMPLETED this run (sell-wallet union 27/27, NOT a new rotation); run-98 named rotations "
            "41cc/43bc/2120/da79 0 wallets (3rd quiet run after debut); run-97 named rotations c90a/e3a8 0 wallets (3rd quiet run after debut); all five "
            "run-90 rotations 0 wallets (10th quiet run after debut); 0x1153... STALLED at 26 wallets (10th quiet run); 0x79cd... STALLED at 20 wallets "
            "(11th quiet run). 32 deployments - fourth straight run with deployments. Inbound run-100 window FULLY CLOSED in-run after b3 re-run "
            f"(1552/1552, {tot_logs_effective} logs, 0 hits, 0 failed after same-run retry of 1 failed contract).",
    "rotations": "TWO NEW, both NAMED (anomaly): 0x6f31f7cf4a3fe26f1b849d71c146e4fc08ea7777 (Nigga Its Over/NIO, 27 wallets, first buy 17:24:09 WIB) + "
                 "0x0d7e74c412c3bb4b32459f0f25efbe49c43e7777 (癫猫/癫猫, 27 wallets, first buy 17:01:07 WIB). Sets byte-identical, diff 0 vs "
                 "run-99 machine set. All paid-only with no free-mint path; auto-mint blocked at guard (c); reported once as signal per fast-path "
                 "amendment (name/symbol appeared).",
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
            "pattern": "9 tokens x 1 wallet: 6 by 0x7488d5da6a6097de0ff88c7492c62c2fd1e56650, 2 by 0x2325f175975abdbcde555c79cc8e63381d28551b (0xa9d3d7... also in run 99), 1 db49 tail buy by 0x9cdd08f30188c2732cdbcac8eebf4e6e8bf0c1b2",
            "wallet": "see pattern",
        },
        {
            "pattern": "5 txs via 0x296b00198dc7ec3410e12da814d9267bb8df506a (selector 0x27772d13), receiving tokens from pair contracts (swap-like, not mints); total value 0.09 BNB",
            "wallet": "0x2325f175975abdbcde555c79cc8e63381d28551b",
        },
        {
            "pattern": "39 txs via aggregator 0x855066c8679c77a0258e792b5ccf19f8c227eb31 (selector 0x39ecce49) + 21 approvals, total value 0.000546 BNB (churn as usual)",
            "wallet": "0x38031ca8a54526f9fe90f11f07b55ae5fc01036a",
        },
    ],
}

s["inbound_log_leg_run100"] = {
    "contracts": 1552,
    "attempted": 1552,
    "completed_with_0_hits": 1552,
    "total_logs": tot_logs_effective,
    "hits": 0,
    "failed": eff_failed,
    "failed_contracts": [],
    "failed_then_recovered_same_run": failed_contracts,
    "never_attempted": 0,
    "complete": eff_failed == 0,
    "note": "Ankr getLogs address-filtered per contract, window 132179369-132192616, from list run100-inbound-contracts.json (1552 contracts = run99 list "
            f"1517 + 32 run-100 deployments + 2 new rotation tokens + 1 recovered run-99 creation 0x7ad22712...). Full pass a (400, 8,009 logs, 0 failed) + "
            f"b1 (200, 3,773 logs, 0 failed) + b2 (200, 1,829 logs, 0 failed) + b3-2 (752, {chunks['b3-2']['total_logs']} logs, "
            f"1 failed in-chunk, recovered 1/1 by same-run single-contract retry b3-retry: 0xd987945d1df5fcd111155bf9c494faade3f91e3e -> 0 logs, 0 hits) = "
            f"{tot_logs_effective} logs, 0 hits, 0 FAILED after retry. "
            "Truncated contracts, all topic-filtered to 0 logs (a: 0x1de4... AFeng sale, 0x3dca..., 0x55d398... USDT, 0x6288..., 0x636fdfa9... tracker - same "
            "set as runs 91-99; b1: 0x63de... AGC, 0x7857..., 0x7e2d... (NEW); b2: 0xb40e... (NEW)). b3 FIRST attempt DIED SILENTLY at ~contract 688 "
            "(Ankr 'Remote end closed connection' on 0x0ba97102b878f77b958ce9f442d75a725b94c886, no JSON, no process - service-restart pattern); re-run from "
            "scratch as b3-2 completed clean. All four chunks hit repeated joint Ankr stalls (logs frozen minutes, live processes, then resuming - run-95 "
            "pattern); no chunk was killed or re-run for stalling alone. Window FULLY CLOSED in-run, no retry deferred to run 101."
            if eff_failed == 0 else
            "Window NOT fully closed: failed contracts must be retried in run 101.",
}

# ---- machine tokens: 2 new entries ----
new_entries = [
    {
        "address": "0x6f31f7cf4a3fe26f1b849d71c146e4fc08ea7777",
        "first_seen": "run-100, 2026-11-07 17:24:09 WIB (tx 0x98defacdac..., block 132184115)",
        "machine_wallets": 27,
        "typical_first_buy_bnb": 0.000121125,
        "followup_buy_range_bnb": "median 0.223378725, max 0.422068, total buys 9.6850 BNB (58 sent buys)",
        "label": "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - NAMED (Nigga Its Over / NIO) - ANOMALY, reported once as signal run 100",
        "note": "ANOMALY under the fast-path amendment: name/symbol APPEARED - name 'Nigga Its Over', symbol 'NIO', confirmed via fast_rpc; totalSupply 1e27; "
                "decimals 18. DexScreener independently confirms Nigga Its Over/NIO, pair 0xc9299379d122a1a84d45fdf1ee87dd0ce1a5e3e8, liquidity $0.07 (drained "
                "after the rotation's sells), price -99.99% h6, volume $18,680.30 h24, pair created ~17:24 WIB. First buy 17:24:09 WIB by 0xcb08c02c0a, "
                "0.000121125 BNB -> 9,674.63 tokens. Wallet set byte-identical to the other run-100 rotation and diff 0 vs the run-99 machine set (27/27 "
                "overlap). Buy sizes WITHIN class norm - NOT a size anomaly. 100 sells / 27 sell wallets in-window - rotation fully dumped. Pair "
                "token0/token1 READ OK run 100: token0 = the token, token1 = WBNB 0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c. Auto-mint BLOCKED at guard (c) - "
                "paid PCS token, no free-mint path. Do not re-signal unless a new fact appears.",
    },
    {
        "address": "0x0d7e74c412c3bb4b32459f0f25efbe49c43e7777",
        "first_seen": "run-100, 2026-11-07 17:01:07 WIB (tx 0x145ac13be3..., block 132181044)",
        "machine_wallets": 27,
        "typical_first_buy_bnb": 0.000121125,
        "followup_buy_range_bnb": "median 0.223378725, max 0.389734, total buys 9.2907 BNB (55 sent buys)",
        "label": "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - NAMED (癫猫 / 癫猫) - ANOMALY, reported once as signal run 100",
        "note": "ANOMALY under the fast-path amendment: name/symbol APPEARED - name '癫猫', symbol '癫猫', confirmed via fast_rpc; totalSupply 1e27 (first "
                "read ERROR 'all endpoints failed', retried OK); decimals 18. DexScreener independently confirms 癫猫/癫猫, pair "
                "0x98fe67c6aeb645e6c9aa41c1fd79898261e7fde7, liquidity $0.07 (drained after the rotation's sells), price -99.99% h6, volume $18,165.41 h24, "
                "pair created ~17:01 WIB. First buy 17:01:07 WIB by 0xcb08c02c0a, 0.000121125 BNB -> 9,674.63 tokens. Wallet set byte-identical to the other "
                "run-100 rotation and diff 0 vs the run-99 machine set (27/27 overlap). Buy sizes WITHIN class norm - NOT a size anomaly. 98 sells / 27 "
                "sell wallets in-window - rotation fully dumped. Pair token0/token1 READ OK run 100: token0 = the token, token1 = WBNB "
                "0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c. Auto-mint BLOCKED at guard (c) - paid PCS token, no free-mint path. Do not re-signal unless a new "
                "fact appears.",
    },
]
s.setdefault("machine_tokens", []).extend(new_entries)

# update stalled labels' run ranges
for e in s["machine_tokens"]:
    if e["address"].lower().startswith("0x1153607e"):
        e["label"] = "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - rotation STALLED at 26 wallets (runs 91-100)"
    if e["address"].lower().startswith("0x79cd174c"):
        e["label"] = "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - rotation STALLED at 20 wallets (runs 90-100)"
# db49 entry: rotation now complete
for e in s["machine_tokens"]:
    if e["address"].lower().startswith("0xdb4950e7"):
        e["note"] = e.get("note", "") + " UPDATE run 100: rotation COMPLETED - 26 sell txs / 25 wallets + 1 buy tx in run 100; sell-wallet union run99 (23) + run100 (25) = 27/27. NOT a new rotation."

# signaled projects: append the two (paid-only)
s.setdefault("signaled_projects_over_20pct", []).extend([
    "Nigga Its Over (NIO) 0x6f31f7cf4a3fe26f1b849d71c146e4fc08ea7777 (paid-only, machine-token, run-100, NAMED - anomaly reported once as signal)",
    "癫猫 (癫猫) 0x0d7e74c412c3bb4b32459f0f25efbe49c43e7777 (paid-only, machine-token, run-100, NAMED - anomaly reported once as signal)",
])

# ---- next run note ----
note = (
    "Next run sent-tx window starts from block 132192617. "
    "RETRY run 101: (1) Pair token0/token1 reads for 0xa6e6... pair 0x9fac925655fa4985ab4fe2fe9e0ca8ae323cc9da and 0x887c... pair "
    "0xa9fa6efb21c252b7d4ab81d19a07ee4ecf6d2c97 (fast_rpc race returns None / 'all endpoints failed', 18 consecutive runs - persistently unreadable, "
    "unverified not absence), plus 0x2bfb pair 0x782671f637bf1a01de482824c4b2520bc58a5a4b, 0xc459 pair 0xeca06856c88fcdf1506886431a079d3f2565ca82, and "
    "rotation 0x43c8 pair 0xaafebb5244e2e546f7cd18a2c89f85bbee03f1e0 (unreadable run 88-100, 13 consecutive - retry opportunistically, not an anomaly), "
    "PLUS run-89 rotation pairs 0xcfdb 0x1e04925db4eabab2917ef73a8cdf232bcc69b5ba, 0x0cf8 0xf6800c4a1ecdffbd64f9047c606bdb32dee0127f, 0xe68b "
    "0xfab7cb4979c9e4738afc61e4974177cf72c50896 (token0/token1 unreadable run 89-100, 12 consecutive; 0x31e4 pair 0x60ca0aef... READ OK run 89), PLUS "
    "run-99 rotation pairs 0xdb49 0x41cbb4910fd4959f651d7bff8d8b5ed5cd355dfc (token1 = token READ OK, token0 unreadable runs 99-100), 0xff66 "
    "0x2d3e053bada0378299010fde9f59209985760bab (token1 = token READ OK, token0 unreadable runs 99-100); 0x6b12 pair 0x43d85c9fa81bc019701431460d1b3459b057af6d "
    "READ OK run 100 (token0 = token, token1 = WBNB) - REMOVED from retry; 0x50e4 pair 0x26b53042e668d52056e4449abcd238cf01e3a155 READ OK run 99 - already "
    "removed; 41cc pair 0x05ced0b9f08725c126e4f744ba9e58dc95c0c936 READ OK run 99 - already removed; run-97 rotation pairs c90a/e3a8 READ OK run 98 - already "
    "removed; run-100 pairs 6f31 0xc9299379d122a1a84d45fdf1ee87dd0ce1a5e3e8 + 0d7e 0x98fe67c6aeb645e6c9aa41c1fd79898261e7fde7 READ OK run 100 (token0 = token, "
    "token1 = WBNB) - no retry needed. "
    "(2) Run-100 inbound list = run99 list (1517) + 32 run-100 deployments + 2 new rotation tokens + 1 recovered run-99 creation 0x7ad2271298c0d7b5510ff5eed079edce0911bbb1 "
    "(total 1552); run-101 inbound list = run100 list (1552) + run-101 deployments + new rotation tokens. "
    "(3) Run-100 inbound window FULLY CLOSED in-run after b3 re-run from scratch as b3-2 (1552/1552, 0 hits, 0 failed - verify at state-update time; "
    "if b3-2 had failures, they are listed in inbound_log_leg_run100.failed_contracts and must be retried in run 101). "
    "(4) 0xdb4950e7... rotation COMPLETED run 100 (sell-wallet union run99+run100 = 27/27) - do NOT treat any db49 activity as a new rotation. "
    "0x1153607e... rotation STALLED at 26 wallets (0 wallets runs 91-100, 10th quiet run after debut) - watch run 101 the same way. 0x79cd... STALLED at "
    "20 wallets (0 wallets runs 90-100, 11th quiet run after debut) - same. Run-99 named rotations 0x50e4.../0x6b12.../0xff66...: 0 wallets run 100 (1st "
    "quiet run after debut) - watch run 101 the same way. Run-98 named rotations 0x41cc.../0x43bc.../0x2120.../0xda79...: 0 wallets run 100 (3rd quiet run "
    "after debut) - same. Run-97 named rotations 0xc90a.../0xe3a8...: 0 wallets run 100 (3rd quiet run after debut) - same. "
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
    "run 100 (TWO NEW rotations 0x6f31... Nigga Its Over/NIO + 0x0d7e... 癫猫/癫猫 at 27 wallets each - BOTH NAMED, fourth consecutive run with named "
    "rotations, anomaly reported once as signal run 100; buy sizes in class norm; both fully dumped in-window (100/98 sells, 27 sell wallets each); "
    "50e4/6b12/ff66 0 wallets (1st quiet run after debut); db49 rotation COMPLETED (sell-wallet union run99+run100 = 27/27, NOT a new rotation); "
    "41cc/43bc/2120/da79 0 wallets (3rd quiet run); c90a/e3a8 0 wallets (3rd quiet run); 0x1153... STALLED at 26, 10th quiet run; 0x79cd... STALLED at 20, "
    "11th quiet run; 32 deployments (fourth straight run with deployments, 0xaa49e7fe alone 5); inbound FULLY CLOSED in-run after b3 re-run from scratch "
    "as b3-2 (b3 first attempt died silently ~contract 688, Ankr 'Remote end closed connection' on 0x0ba97102...), 1552 contracts, 0 hits, 0 failed; "
    "run-99 NULL creation receipt RECOVERED (tx 0x21c210df..., status 1, block 132171801, contract 0x7ad2271298c0d7b5510ff5eed079edce0911bbb1); 6b12 pair "
    "READ OK run 100 - removed from retry list) "
    "auto-mint BLOCKED at guard (c) - do not re-signal or re-report the block unless a new mint/buy fact appears for those contracts (e.g. a genuine "
    "free-mint path). Per the 2026-11-06 ~18:30 machine-token fast-path amendment, routine machine-token rotations are recorded in state WITHOUT a chat "
    "report (no full verification per run); report only on anomaly (buy size far off norm, name/symbol appears, website, or free-mint path). "
    "Paid fact: run100 TWO NEW rotations 0x6f31... (Nigga Its Over/NIO) + 0x0d7e... (癫猫/癫猫) at 27 wallets each - BOTH NAMED, fourth consecutive run "
    "with named rotations (anomaly: name/symbol appeared; reported once as signal run 100, paid-only, auto-mint blocked guard (c)); run-99 tokens "
    "0x50e4.../0x6b12.../0xff66... 0 wallets (1st quiet run after debut); db49 rotation COMPLETED (27/27 sell wallets); run-98 tokens 0x41cc.../0x43bc.../0x2120.../0xda79... "
    "0 wallets (3rd quiet run after debut); run-97 tokens 0xc90a.../0xe3a8... 0 wallets (3rd quiet run after debut); run-90 tokens 0x6a25.../0x9f7e.../0x8c64.../0xc1ab.../0x1153... "
    "0 wallets (10th quiet run after debut); run-89 tokens 0xcfdb.../0x0cf8.../0xe68b.../0x31e4... 0 wallets (11th quiet run after debut); run-88 tokens 0x43c8.../0x3d12.../0xeae0... "
    "0 wallets (12th quiet run after debut); run-87 tokens 0x889a.../0x4249... 0 wallets (13th quiet run after debut); run-86 tokens 0x2bfb.../0xc459... "
    "0 wallets (14th quiet run after debut); run-85 token 0x2717... 0 wallets (15th quiet run); run-82 tokens 0xd468.../0xa6e6.../0x887c... all 0 wallets "
    "(18th quiet run after debut); run-81 tokens 0 wallets (19th quiet run); run-80 token 0 wallets (20th quiet run); GrokBot 0xfcd0... absent "
    "(0 wallets) - 41st consecutive quiet run (59, 61-100) after the run-60 burst; CORLA-97af 0 wallets; CORLA 0x4a9c 0 wallets; all run-64/65 ASI "
    "contracts 0 wallets; all run-66/68/69/70/71/72/73/74/75/76/77/78/79 machine tokens 0 wallets. Run 100 had 32 deployments (fourth straight run with "
    "deployments; 0xaa49e7fe alone 5; added to the inbound list for run 101 - all 32 addresses recovered, 0 NULL receipts). AFeng 0 txs; future1001.ai 0 txs; "
    "0x2325... 8 txs (5 aggregator 0x27772d13 + 3 approvals, total value 0.09 BNB); 0x8e96... 0 txs; 0x3803... 60 txs (39 aggregator 0x39ecce49 + 21 approvals, "
    "total value 0.000546 BNB, churn as usual). SCRIPT LESSON (run 85, FIXED run 86): when copying runNN-receipts.py for the next run, sed-replace the two "
    "hardcoded json.dump output paths too (runNN-receipts.json / runNN-paid.json) - run 93's copy was verified correct before running (dumps to "
    "run93-receipts.json/run93-paid.json). PROCESS LESSON (run 86): the receipts pass died silently at 420/461 (service-restart pattern, same as runs "
    "82/84) - the partial-file resume worked; always re-run the same script to resume rather than re-fetching from scratch. Run 100 receipts completed in "
    "one attempt, no resume needed; sent pass completed first attempt 55/55 OK; inbound b3 first attempt DIED SILENTLY at ~contract 688 (no JSON saved) "
    "and was re-run from scratch as b3-2 to completion. A frozen log mtime with a live process is a stall, not a death - wait before re-running; a log "
    "frozen >5 min with NO live process is a silent death - re-run the chunk from scratch; a socket wedged >5 min while fresh calls work is a wedge - "
    "kill by PID (pkill -f can match the wrapper shell itself, use kill <pid>) and re-run the chunk from scratch. "
    "SCRIPT FIX (run 100): run100-rotation-analysis.py sell counting fixed (old `to in wallets` filter counted 0 sells because a PCS sell transfers "
    "wallet->pair; run99's rotation-analysis.json also records n_sells 0 for db49) - now counts SELL_SEL txs whose receipt logs touch the token; "
    "run 101 copies the FIXED script via sed. "
    "INBOUND FILENAME QUIRK FIXED run 88: chunk output files are now correctly named run93-inbound93-{a,b1,b2,b3}.json. Same-owner factory groups now also "
    "include 0x293f and 0x1103 (proven 2026-11-06 ~01:14 WIB, AGENTS.md) alongside the groups listed in the body."
)
s["next_run_note"] = note

json.dump(s, open(P, "w"), indent=1)
print("state updated; last_run now:", s["last_run"]["run"], "block_end:", s["last_run"]["block_end"])
print("machine_tokens:", len(s.get("machine_tokens", [])), "| signaled:", len(s.get("signaled_projects_over_20pct", [])))
print("inbound100 complete:", s["inbound_log_leg_run100"]["complete"], "| failed:", s["inbound_log_leg_run100"]["failed"],
      "| total_logs:", s["inbound_log_leg_run100"]["total_logs"])
print("inbound99 complete:", s["inbound_log_leg_run99"]["complete"], "| failed:", s["inbound_log_leg_run99"]["failed"])
