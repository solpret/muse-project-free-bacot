#!/usr/bin/env python3
"""Run 102 state update (read-only job bookkeeping; no chain writes).

Completes run 102 (window 132208027-132224205, tx 2026-11-07 20:23:43 - 22:24:57 WIB).
Sent/receipts/paid done and verified; inbound leg run-102 window CLOSED in-run
(1663/1663, 1 hit - the sent-pass AFeng tracker tx 0xb8f3ac7e..., 0 inbound-only new).
NO new mints. FOUR NEW machine-token rotations at 27 wallets each - ALL NAMED
(Kum Jung On / Kum + BTC / 比特币 + 币安币 / 币安币 + debtdog / debtdog), the SIXTH
consecutive run with named rotations (run 97 had 2, run 98 had 4, run 99 had 4,
run 100 had 2, run 101 had 2, run 102 has 4): anomaly under the fast-path amendment,
reported ONCE as a paid-only signal (not a lead, not a buy recommendation, auto-mint
blocked at guard (c)). 70 deployments this run (sixth straight run with deployments;
25/72/64/32/35/70). Bridge unchanged (0 new mints, 0 not_evaluated). Run-102 NULL
receipts (9, all 0xad94ee77 PCS buys/sells) RECOVERED same-run, all status 1.
"""
import json, shutil

P = "/home/hatch/workspace/narrative-pulse/tracked-wallet-mint-scan-state.json"
shutil.copy(P, str(P) + ".bak-run102-pre")
s = json.load(open(P))
SR = "/home/hatch/workspace/narrative-pulse/scan-runs"

# ---- inbound totals from chunk JSONs (self-verifying) ----
chunks = {}
for part in ["a", "b1", "b2", "b3"]:
    chunks[part] = json.load(open(f"{SR}/run102-inbound102-{part}.json"))
tot_contracts = sum(c["contracts_checked"] for c in chunks.values())
tot_logs = sum(c["total_logs"] for c in chunks.values())
tot_hits = sum(len(c["hits"]) for c in chunks.values())
tot_failed = sum(len(c["failed"]) for c in chunks.values())
tot_trunc = sum(len(c["truncated"]) for c in chunks.values())
print(f"inbound totals: contracts={tot_contracts} logs={tot_logs} hits={tot_hits} failed={tot_failed} truncated={tot_trunc}")
assert tot_contracts == 1663, f"inbound contracts {tot_contracts} != 1663"
assert tot_hits == 1, f"inbound hits {tot_hits} != 1 (must handle before state update!)"
hit_txs = {h["tx"].lower() for c in chunks.values() for h in c["hits"]}
assert hit_txs == {"0xb8f3ac7eede305da8b617317e6bed26a639c3a2f4f15184385dd327f20e9da2f"}, \
    f"inbound hit is NOT the known-repeat AFeng tracker tx: {hit_txs}"
print("inbound hit verified: the sent-pass AFeng tracker tx (0xb8f3ac7e...), 0 inbound-only new mints")
failed_contracts = [f for c in chunks.values() for f in c["failed"]]
retry_path = f"{SR}/run102-inbound102-retry.json"
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

last_run_102 = {
    "run": 102,
    "block_start": 132208027,
    "block_end": 132224205,
    "window_wib": "2026-11-07 20:23:43 - 22:24:57 WIB (tx times); run executed ~22:19 WIB - ~00:05 WIB; sent-pass in-window txs 1457, 7 mint-pattern txs (0 new mints - all dividend-tracker repeats, see method_note)",
    "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set); 0 failed first attempt, 36 wallets active.",
    "method_note": (
        "Sent pass Ankr ankr_getTransactionsByAddress via module: 55/55 OK first attempt (1457 txs), 0 failed, 36 wallets active. "
        "Receipts via fast_rpc batch (6, ~4s pause) for 945 non-approve candidates: 929 status 1, 7 status 0 (ALL failed PCS sells 0x791ac947: "
        "0xc6219468 22:13:10 WIB tx 0x464466f32a... + 21:17:05 WIB tx 0x413693f5..., 0xcb08c02c 22:16:56 WIB tx 0x09525b35..., 0xa952331e 21:18:13 WIB tx "
        "0x78b8cf2c..., 0x92bc3297 22:14:19 WIB tx 0x9d602b02... + 20:54:33 WIB tx 0x73585103..., 0x9b519f5d 22:12:53 WIB tx 0x9227c476...), 9 NULL (ALL "
        "0xad94ee77 PCS buys/sells) - ALL 9 RECOVERED same-run via fast_rpc race (run102-null-receipt-retry.py): all status 1, 5 logs each, no mint logs, "
        "0 null remaining. Receipts pass ran slow (~40 min) because the fast_rpc race outage forced batch failures into per-tx race fallbacks. "
        "Mint-pattern txs: 7 - ZERO new mints. (1) 0xb8f3ac7e... (AFeng sale-call 0x4d819a2a to 0x1de4..., 0.15 BNB, 21:05:41 WIB, block 132212376) is a Transfer "
        "from the zero address by the DIVIDEND_TRACKER contract 0x636fdfa9bc3db42c690c09e87b9017d05b36c743 to AFeng - the KNOWN REPEAT of the run-70 finding "
        "(AFeng buys moco reflection token 0x10b389... via router 0x1de4..., tracker mints shares 1:1 with the bought balance + WBNB dividends). "
        "(2) FIVE AFeng sale-calls with a NEW tracker contract 0x0c84aed253eaab9b7263665d7e213b7aec718f23 (name/symbol ETHBack_Dividen_Tracker, totalSupply "
        "65564192225221406208665, decimals 18) - same mechanism, different reflection token: AFeng bought corla 0xd2c1cad9a374947b17f49d69fff7f278d7255555 "
        "(name/symbol corla/corla, totalSupply 1e23, decimals 18) via pair 0x3276c62edcec628edd95437b2c63f01f7380e657: 0xe8824827... 21:17:43 WIB 0.225 BNB, "
        "0xc7c21408... 21:17:48 WIB 0.75 BNB, 0xcc0815ca... 21:24:58 WIB 0.5 BNB, 0x791b4b79... 21:51:09 WIB 0.5 BNB, 0xa2b5b308... 22:00:04 WIB 0.25 BNB "
        "(total 2.225 BNB). (3) 0x42d33fdb... (0x2325f175 aggregator 0x27772d13 to 0x296b..., 0.1 BNB, 22:13:49 WIB) with a NEW tracker contract "
        "0x5e07ec958492da93caa306c12c3a0552d5d594ed (ETHBack_Dividen_Tracker, totalSupply 797528065519987781188887626424, decimals unreadable pass 1 - race "
        "outage) - same mechanism: 0x2325 bought BAGENT 0x0e2272d0e5e9ea71ff458c8a2f73bc837c844734 (name BAGENT retried OK, symbol BAGENT, totalSupply 1.02e30, "
        "decimals 18) via pair 0x890cce5e30d522c09cc2c0b969e2b7279a74416c. All 7 are dividend-tracker share mints accompanying PAID buys of ETHBack reflection "
        "tokens - NOT free mints, NOT new mints, NOT reported as new (same handling as the run-70 repeats in runs 75/101). corla here is a DIFFERENT contract "
        "from the run-63 paid-only signal CORLA 0x4a9c; this 0xd2c1 corla was bought by AFeng only (1 wallet, paid-only). BAGENT bought by 0x2325 only "
        "(1 wallet, paid-only). "
        "Paid: 66 tokens; max 27 wallets/token (FOUR new rotations at 27 each - see anomaly signal; 22 tokens at 3 wallets, ALL the same churn trio "
        "0x3803/0xad94/0xc7c5, all ...7777; 12 at 2 (the 0x3628/0xa0c1 pair); 28 at 1). Overlap with run-101 paid tokens: only 3 (0x2567e74882c92ded24f7df2767184af19b1b7777, "
        "moco 0x10b389..., WBNB 0xbb4cdb9c...) - the ...7777 churn set turns over almost completely every run. "
        "NEW ROTATIONS - ANOMALY (named tokens, SIXTH consecutive run - run 97 had 2 named, run 98 had 4, run 99 had 4, run 100 had 2, run 101 had 2, run 102 "
        "has 4): 0x42637d6471cd50286a0801060d88e05007197777 (debtdog / debtdog), 0x07b225cecc3733f71fd613dbf80a275dfd5a7777 (币安币 / 币安币), "
        "0xd826883c65bd3b760ee1b0720c8c31cc2b177777 (BTC / 比特币), 0x8b19cdca84f9e57cbb2946f1c8d27be25ef87777 (Kum Jung On / Kum). "
        "All: name+symbol+totalSupply+decimals confirmed via fast_rpc (07b2 decimals failed pass 1, retried OK = 18; 0e22 name failed pass 1, retried OK), "
        "totalSupply 1e27, decimals 18. DexScreener independently confirms all four (PCS V2 token/WBNB pairs, liquidity <$1 - drained after the rotation's sells): "
        "debtdog pair created 2h 8m ago, 224 txns, vol $18K, buys 87/sells 137, pooled debtdog 60,759,293 + WBNB 0.00005574; 币安币 pair created 1h 45m ago, 217 txns, "
        "vol $18K, buys 83/sells 134, pooled 59,433,836 + WBNB 0.00005394; BTC pair created 1h 14m ago, 227 txns, vol $18K, buys 88/sells 139, pooled 60,842,803 + "
        "WBNB 0.00005586; Kum pair created 48m ago, 214 txns, vol $18K, buys 84/sells 130, pooled Kum 59,199,033 + WBNB 0.00005363. "
        "All four bought by the SAME 27-wallet machine set, byte-identical to each other and diff 0 vs the run-101 machine set (27/27 overlap with 4727 wallets). "
        "Buy sizes WITHIN class norm (NOT a size anomaly): first buy 0.000123025 BNB -> 9,826.24 tokens (4263) / 9,816.72 tokens (07b2) / 9,826.24 tokens (d826, 8b19); "
        "follow-up medians 0.231031840 (4263) / 0.223379289 (07b2) / 0.223364190 (d826, 8b19); max 0.349560 (4263) / 0.396382 (07b2) / 0.382606 (d826) / 0.384152 (8b19); "
        "totals 9.6043 / 9.2459 / 9.8176 / 9.0523 BNB; buys 57/53/58/54, sells 99/95/100/91 (sell wallets 27/27/27/27 - ALL FOUR fully dumped in-window). First buys: "
        "4263 20:51:46 WIB by 0xcb08c02c0a tx 0xb39e72fd2c... block 132211785 pair 0x70b31f93bff68d87ccd7b11c4458af5a7deb8d44; "
        "07b2 21:15:28 WIB by 0x36239612 (future1001.ai) tx 0xf5ced4bd56... block 132214945 pair 0x39f0227ba7aa712db15bdb51046647e8f0939b54; "
        "d826 21:45:43 WIB by 0xcb08c02c0a tx 0x80eec3e4c9... block 132218975 pair 0x2315f44831bcac27bd7308e2d50943b4f115f4bd; "
        "8b19 22:11:30 WIB by 0xcb08c02c0a tx 0x5037866306... block 132222413 pair 0xf7a2396852111ed1480d4ffca583696369c87eab. Pair token0/token1: NOT read this "
        "run - retry run 103; DexScreener confirms all four are PCS V2 token/WBNB pairs. Trigger >25% met numerically (27 >= 14) but AUTO-MINT BLOCKED at guard (c): "
        "paid PCS tokens, no free-mint path; guard (a) website also unverified. No preview, no execution. "
        "Seatbelt 1e9c STALLED at 26: 0 buys this run, 8 sells / 8 sell wallets (2 NEW vs run 101: 0xc194efe22e874a3fe666b5de5a8fd369f12c32d5 + "
        "0xc6591fde9b44aa081062c9fc6ee48e443d24ef57); sell-wallet union run101+run102 = 26/27 - did NOT reach 27. NOT a new rotation; watch run 103 the same way. "
        "Deployments: 70 contract creations by 15 machine-set wallets (0x9b519f5d 10; 0xcb08c02c 8; 0xc0c84518 7; 0x97bd895f 7; 0xaa49e7fe/0x3154f694/0x1cce4ec5/0x64e893a4 "
        "5 each; 0xf795c525/0x3a39aa05/0x5b4beded 4 each; 0xc6219468/0x92bc3297 2 each; 0x2cc8192f/0xa952331e 1 each) - SIXTH straight run with deployments "
        "(25 run 97, 72 run 98, 64 run 99, 32 run 100, 35 run 101, 70 run 102); all 70 deployed addresses recovered from RAW receipts "
        "(run102-receipts-partial.json), added to the inbound list (run102-inbound-contracts.json, total 1663) along with the 4 new rotation tokens. The 4 rotation "
        "tokens are NOT among the deployments. "
        "AFeng (0xbf004bff...) 42 txs (31 sale-calls 0x4d819a2a + 10 approvals + 1 transfer 0xa9059cbb, total value 34.4 BNB - MUCH bigger than run 101's 4.125 BNB; "
        "sale values 0x10, 0.075, 0.15x2, 0.25x2, 0.375, 0.5x4, 0.75, 1.2, 2.3x4, 3.0x2, 3.5x2, 7.0); future1001.ai (0x36239612...) 16 txs (8 PCS buys + 4 sells + "
        "4 approvals, total value 0.935 BNB - first buyer of the 0x07b2 rotation); 0x2325... 34 txs (24 aggregator 0x27772d13 + 10 approvals, total value 1.45 BNB); "
        "0x8e96... 0 txs; 0x6ba79dcc/0x89220022/0xda91cefe 0 txs; 0x3803... 66 txs (44 aggregator 0x39ecce49 + 22 approvals, total value 0.0006 BNB, churn as usual); "
        "0xad94... 65 txs (22 buys + 21 sells + 22 approvals, 0.0008 BNB); 0xc7c5... 67 txs (22 buys + 22 sells + 22 approvals + 1 plain, 0.0028 BNB). 1 plain BNB "
        "transfer (0xc7c5..., empty input). "
        "Selectors (sent pass, 1457 txs): 512 approvals (0x095ea7b3) + 476 PCS sells (0x791ac947) + 297 PCS buys (0xb6f9de95) + 70 contract creations (0x60806040) + "
        "44 aggregator (0x39ecce49) + 31 sale-calls (0x4d819a2a, AFeng) + 25 aggregator (0x27772d13) + 1 empty-input (plain BNB transfer) + 1 transfer (0xa9059cbb). "
        "Nonzero-value txs 425, total 75.6768 BNB, max 7.0 BNB (AFeng sale-call 0xc2cd838bd3134a0a4cb77ef5c66984df43b4e74fe6e0fc93948d90125134fc0c). Most active wallets: "
        "0xa952331e 75 txs, 0x9cdd08f3 72, 0xc7c5faa2 67, 0x38031ca8 66, 0xad94ee77 65, 0xc6219468 58, 0xf795c525 52, 0xe9ed24db 52, 0xdb2d83f9 50, 0x1cce4ec5 49, "
        "0x9b519f5d 49, 0xfdec62fd 48. "
        "9 NULL receipts this run (all 0xad94ee77 PCS buys/sells) - ALL RECOVERED same-run (see above), 0 null remaining. 7 status-0 txs, all failed PCS sells (see above). "
        f"Inbound leg (amendment 12:02 WIB): Ankr getLogs address-filtered per contract, 1663 contracts (run101 list 1589 + 70 run-102 deployments + "
        f"4 new rotation tokens), 1 hit (the sent-pass AFeng tracker tx 0xb8f3ac7e... - 0 inbound-only new mints), {tot_logs_effective} logs, window 132208027-132224205. "
        f"Chunk a (400, 8,052 logs, 1 failed, 6 truncated) + b1 (200, 3,669 logs, 1 failed, 3 truncated) + b2 (200, 1,542 logs, 1 failed, 0 truncated) + "
        f"b3 (863, 3,586 logs, 0 failed, 0 truncated) + retry (3 contracts, 0 logs, 0 failed - the 3 in-chunk failures 0x13eea6a9..., 0x76c0c753..., "
        f"0xab518344... recovered same-run 3/3) = {tot_logs_effective} logs, 1 hit (sent-pass duplicate), 0 FAILED after retry. "
        "Truncated contracts, all topic-filtered to 0 logs except the 0x636f tracker (a: 0x10b3... moco, 0x1de4... AFeng sale, 0x3dca..., 0x55d398... USDT, "
        "0x6288... AGC sale, 0x636fdfa9... tracker -> 1 log = the hit - same set as runs 91-101; b1: 0x63de... AGC, 0x7857..., 0x7e2d...; b2/b3: none). "
        "Chunk b3 stalled ~10 min at 50/863 with a live process (log frozen, fresh Ankr calls working 7.6s) - resumed on its own, NO kill/re-run needed this run. "
        "All four chunks hit repeated joint Ankr stalls this run (logs frozen minutes at a time with live processes, then resuming - same pattern as runs 95/100/101). "
        "Window FULLY CLOSED in-run, no retry deferred to run 103. "
        "Pair a6e6/887c/2bfb/c459/43c8/cfdb/0cf8/e68b STILL unreadable: token0()/token1() for all eight pairs failed via fast_rpc race "
        "('all endpoints failed' / OSError) in run102-pair-retry.py - unverified, not absence; 20th consecutive run for a6e6/887c/2bfb/c459, 15th for 43c8, "
        "14th for cfdb/0cf8/e68b; retry run 103. BUT 4727/1e9c pairs READ OK this run (4727 pair 0xf4ee6a9b...: token0 = 4727 token, token1 = WBNB; 1e9c pair "
        "0x533623ca...: token0 = 1e9c token, token1 = WBNB) - REMOVED from the retry list. New run-102 pairs 8b19 0xf7a23968... + d826 0x2315f448... + 07b2 "
        "0x39f0227b... + 4263 0x70b31f93... NOT read this run - retry run 103. "
        "fast_rpc race OUTAGE continued this run (time-varying, not permanent): all-endpoint TimeoutError/OSError flapping ~22:00-00:00 WIB - receipts pass batch "
        "failures forced per-tx race fallbacks (slow, ~40 min), token-meta pass 1 partial failures (07b2 decimals + 0e22 name failed, retried OK), pair-retry 8/10 "
        "failed; but later retries succeeded (token-meta retries, all 9 NULL receipts, 4727/1e9c pairs). A failed race read is UNVERIFIED, never absence. "
        "Pointer-discovery (amendment 19:10): 0 contracts processed - no new mints this run, and the backfill queue is empty (bridge 115 contracts, "
        "0 not_evaluated); bridge unchanged. CHAT REPORT this run: the four-named-machine-token anomaly signal (paid-only, NOT a lead, NOT a buy "
        "recommendation, auto-mint blocked guard (c)) - reported once per the fast-path amendment. No new mints, no Free Bacot signal beyond that, "
        "no auto-mint trigger execution. No preview/mint/sign/login/purchase by this job."
    ),
}
s["last_run"] = last_run_102

# ---- paid signal + trend ----
s["paid_signal_run102"] = {
    "note": "ANOMALY SIGNAL (paid-only, NOT a buy recommendation, NOT a Free Bacot lead, NOT an auto-mint trigger). SIXTH consecutive run with NAMED "
            "machine-token rotations - now FOUR at once (run 97 had 2, run 98 had 4, run 99 had 4, run 100 had 2, run 101 had 2, run 102 has 4): the machine set bought FOUR tokens "
            "that HAVE on-chain name/symbol, breaking the unnamed pattern of all 24 pre-run-97 machine tokens. Reported once per the fast-path "
            "amendment (name/symbol appeared). Auto-mint BLOCKED at guard (c) for all four (paid PCS tokens, no free-mint path). Do not re-signal "
            "unless a new fact appears (e.g. a genuine free-mint path).",
    "tokens": [
        {
            "address": "0x42637d6471cd50286a0801060d88e05007197777",
            "name": "debtdog",
            "symbol": "debtdog",
            "wallets": 27,
            "first_buy": "2026-11-07 20:51:46 WIB, 0.000123025 BNB -> 9,826.24 tokens, wallet 0xcb08c02c0a, tx 0xb39e72fd2c..., block 132211785",
            "pair": "0x70b31f93bff68d87ccd7b11c4458af5a7deb8d44 (PCS V2; token0/token1 NOT read run 102 - retry run 103; DexScreener confirms token/WBNB pair)",
            "buys": "57 sent buys, median follow-up 0.231031840 BNB, max 0.349560 BNB, total 9.6043 BNB; 99 sells / 27 sell wallets (fully dumped in-window)",
            "verification": "name+symbol+totalSupply+decimals confirmed via fast_rpc; totalSupply 1e27; decimals 18; DexScreener debtdog/debtdog, pair created 2h 8m ago, 224 txns, vol $18K, buys 87/sells 137, liquidity <$1 (drained after the rotation's sells), pooled debtdog 60,759,293 + WBNB 0.00005574",
        },
        {
            "address": "0x07b225cecc3733f71fd613dbf80a275dfd5a7777",
            "name": "币安币",
            "symbol": "币安币",
            "wallets": 27,
            "first_buy": "2026-11-07 21:15:28 WIB, 0.000123025 BNB -> 9,816.72 tokens, wallet 0x36239612 (future1001.ai), tx 0xf5ced4bd56..., block 132214945",
            "pair": "0x39f0227ba7aa712db15bdb51046647e8f0939b54 (PCS V2; token0/token1 NOT read run 102 - retry run 103; DexScreener confirms token/WBNB pair)",
            "buys": "53 sent buys, median follow-up 0.223379289 BNB, max 0.396382 BNB, total 9.2459 BNB; 95 sells / 27 sell wallets (fully dumped in-window)",
            "verification": "name+symbol+totalSupply confirmed via fast_rpc pass 1; decimals failed pass 1 ('all endpoints failed'), retried OK = 18; totalSupply 1e27; DexScreener 币安币/币安币, pair created 1h 45m ago, 217 txns, vol $18K, buys 83/sells 134, liquidity <$1 (drained after the rotation's sells), pooled 59,433,836 + WBNB 0.00005394",
        },
        {
            "address": "0xd826883c65bd3b760ee1b0720c8c31cc2b177777",
            "name": "BTC",
            "symbol": "比特币",
            "wallets": 27,
            "first_buy": "2026-11-07 21:45:43 WIB, 0.000123025 BNB -> 9,826.24 tokens, wallet 0xcb08c02c0a, tx 0x80eec3e4c9..., block 132218975",
            "pair": "0x2315f44831bcac27bd7308e2d50943b4f115f4bd (PCS V2; token0/token1 NOT read run 102 - retry run 103; DexScreener confirms token/WBNB pair)",
            "buys": "58 sent buys, median follow-up 0.223364190 BNB, max 0.382606 BNB, total 9.8176 BNB; 100 sells / 27 sell wallets (fully dumped in-window)",
            "verification": "name+symbol+totalSupply+decimals confirmed via fast_rpc; totalSupply 1e27; decimals 18; DexScreener BTC/比特币, pair created 1h 14m ago, 227 txns, vol $18K, buys 88/sells 139, liquidity <$1 (drained after the rotation's sells), pooled 60,842,803 + WBNB 0.00005586",
        },
        {
            "address": "0x8b19cdca84f9e57cbb2946f1c8d27be25ef87777",
            "name": "Kum Jung On",
            "symbol": "Kum",
            "wallets": 27,
            "first_buy": "2026-11-07 22:11:30 WIB, 0.000123025 BNB -> 9,826.24 tokens, wallet 0xcb08c02c0a, tx 0x5037866306..., block 132222413",
            "pair": "0xf7a2396852111ed1480d4ffca583696369c87eab (PCS V2; token0/token1 NOT read run 102 - retry run 103; DexScreener confirms token/WBNB pair)",
            "buys": "54 sent buys, median follow-up 0.223364190 BNB, max 0.384152 BNB, total 9.0523 BNB; 91 sells / 27 sell wallets (fully dumped in-window)",
            "verification": "name+symbol+totalSupply+decimals confirmed via fast_rpc; totalSupply 1e27; decimals 18; DexScreener Kum Jung On/Kum, pair created 48m ago, 214 txns, vol $18K, buys 84/sells 130, liquidity <$1 (drained after the rotation's sells), pooled Kum 59,199,033 + WBNB 0.00005363",
        },
    ],
}

s["paid_trend_run102"] = {
    "note": "Aggregate only, NOT a buy recommendation. FOUR NEW machine-token rotations at 27 wallets each - ALL NAMED (debtdog/debtdog, 币安币/币安币, BTC/比特币, Kum Jung On/Kum), "
            "SIXTH consecutive run with named rotations (run 97 had 2, run 98 had 4, run 99 had 4, run 100 had 2, run 101 had 2, run 102 has 4): anomaly reported once as a paid-only signal "
            "(paid_signal_run102); buy sizes in class norm; all four fully dumped in-window (91-100 sells, 27 sell wallets each). "
            "Seatbelt 1e9c STALLED at 26 sell wallets (sell-wallet union run101+run102 = 26/27; 0 buys + 8 sells run 102) - did NOT reach 27. "
            "Run-101 named rotations 4727/1e9c: 4727 0 wallets (1st quiet run after debut); run-100 named rotations 6f31/0d7e 0 wallets (2nd quiet run after debut); "
            "run-99 named rotations 50e4/6b12/ff66 0 wallets (3rd quiet run after debut); "
            "run-98 named rotations 41cc/43bc/2120/da79 0 wallets (5th quiet run after debut); run-97 named rotations c90a/e3a8 0 wallets (5th quiet run after debut); "
            "0x1153... STALLED at 26 wallets (12th quiet run); 0x79cd... STALLED at 20 wallets (13th quiet run). 70 deployments - sixth straight run with deployments. Inbound run-102 window FULLY CLOSED in-run "
            f"(1663/1663, {tot_logs_effective} logs, 1 hit - the sent-pass AFeng tracker tx, 0 failed after same-run retry of 3 failed contracts).",
    "rotations": "FOUR NEW, all NAMED (anomaly): 0x42637d6471cd50286a0801060d88e05007197777 (debtdog/debtdog, 27 wallets, first buy 20:51:46 WIB) + "
                 "0x07b225cecc3733f71fd613dbf80a275dfd5a7777 (币安币/币安币, 27 wallets, first buy 21:15:28 WIB) + "
                 "0xd826883c65bd3b760ee1b0720c8c31cc2b177777 (BTC/比特币, 27 wallets, first buy 21:45:43 WIB) + "
                 "0x8b19cdca84f9e57cbb2946f1c8d27be25ef87777 (Kum Jung On/Kum, 27 wallets, first buy 22:11:30 WIB). Sets byte-identical, diff 0 vs "
                 "run-101 machine set. All paid-only with no free-mint path; auto-mint blocked at guard (c); reported once as signal per fast-path "
                 "amendment (name/symbol appeared). Seatbelt 1e9c rotation STALLED at 26/27 sell wallets (union run101+run102) - watch run 103 the same way, NOT a new rotation.",
    "other_paid_activity": [
        {
            "pattern": "22 tokens x 3 wallets, all the same churn trio 0x3803/0xad94/0xc7c5, all ...7777 (PCS micro buy-then-sell)",
            "wallet": "churn trio (see paid_trend_run1 for the pattern)",
        },
        {
            "pattern": "12 tokens x 2 wallets, both 0x3628764a6576b8dfb31fba0aac6a333b64851423 + 0xa0c1e94fbc1a93e39f5eb828f960aa080a9d9b9e, all ...7777",
            "wallet": "0x3628764a6576b8dfb31fba0aac6a333b64851423 + 0xa0c1e94fbc1a93e39f5eb828f960aa080a9d9b9e",
        },
        {
            "pattern": "28 tokens x 1 wallet (PCS micro buys)",
            "wallet": "see pattern",
        },
        {
            "pattern": "24 txs via 0x296b00198dc7ec3410e12da814d9267bb8df506a (selector 0x27772d13), receiving tokens from pair contracts (swap-like, not mints); total value 1.45 BNB - includes the BAGENT buy 0x42d33fdb... (0.1 BNB, tracker 0x5e07... mint log, same mechanism as run-70)",
            "wallet": "0x2325f175975abdbcde555c79cc8e63381d28551b",
        },
        {
            "pattern": "44 txs via aggregator 0x855066c8679c77a0258e792b5ccf19f8c227eb31 (selector 0x39ecce49) + 22 approvals, total value 0.0006 BNB (churn as usual)",
            "wallet": "0x38031ca8a54526f9fe90f11f07b55ae5fc01036a",
        },
        {
            "pattern": "31 AFeng sale-calls (0x4d819a2a) to 0x1de4... total 34.4 BNB (much bigger than run 101's 4.125 BNB; values incl. 7.0 + 3.5x2 + 3.0x2 + 2.3x4); 6 of them carry dividend-tracker mint logs (1x 0x636f moco 0xb8f3ac7e... 0.15 BNB - known repeat; 5x 0x0c84 corla 0xd2c1... total 2.225 BNB - same mechanism, new tracker/token) - NOT new mints per the state note",
            "wallet": "0xbf004bff64725914ee36d03b87d6965b0ced4903 (AFeng)",
        },
    ],
}

s["inbound_log_leg_run102"] = {
    "contracts": 1663,
    "attempted": 1663,
    "completed_with_0_hits": 1662,
    "total_logs": tot_logs_effective,
    "hits": 1,  # the sent-pass AFeng tracker tx 0xb8f3ac7e... - sent-pass duplicate, 0 inbound-only new
    "failed": eff_failed,
    "failed_contracts": [],
    "failed_then_recovered_same_run": failed_contracts,
    "never_attempted": 0,
    "complete": eff_failed == 0,
    "note": "Ankr getLogs address-filtered per contract, window 132208027-132224205, from list run102-inbound-contracts.json (1663 contracts = run101 list "
            f"1589 + 70 run-102 deployments + 4 new rotation tokens). Full pass a (400, 8,052 logs, 1 failed, 6 truncated) + "
            f"b1 (200, 3,669 logs, 1 failed, 3 truncated) + b2 (200, 1,542 logs, 1 failed, 0 truncated) + b3 (863, 3,586 logs, "
            f"0 failed, 0 truncated) + retry (3 contracts, 0 logs, 0 hits - the 3 in-chunk failures 0x13eea6a9..., 0x76c0c753..., 0xab518344... recovered "
            f"3/3 same-run) = {tot_logs_effective} logs, 1 hit, 0 FAILED after retry. "
            "The 1 hit is the sent-pass AFeng tracker tx (0xb8f3ac7e..., block 132212376, contract 0x636f... tracker, moco) - 0 inbound-only new mints. "
            "Truncated contracts, all topic-filtered to 0 logs except the 0x636f tracker (a: 0x10b3... moco, 0x1de4... AFeng sale, 0x3dca..., 0x55d398... USDT, "
            "0x6288... AGC sale, 0x636fdfa9... tracker -> 1 log = the hit - same set as runs 91-101; b1: 0x63de... AGC, 0x7857..., 0x7e2d...; b2/b3: none). "
            "Chunk b3 stalled ~10 min at 50/863 with a live process (log frozen, fresh Ankr calls working 7.6s) - resumed on its own, NO kill/re-run needed. "
            "All four chunks hit repeated joint Ankr stalls (logs frozen minutes, live processes, then resuming - run-95/100/101 pattern). Window FULLY "
            "CLOSED in-run, no retry deferred to run 103."
            if eff_failed == 0 else
            "Window NOT fully closed: failed contracts must be retried in run 103.",
}

# ---- machine tokens: 4 new entries ----
new_entries = [
    {
        "address": "0x42637d6471cd50286a0801060d88e05007197777",
        "first_seen": "run-102, 2026-11-07 20:51:46 WIB (tx 0xb39e72fd2c..., block 132211785)",
        "machine_wallets": 27,
        "typical_first_buy_bnb": 0.000123025,
        "followup_buy_range_bnb": "median 0.231031840, max 0.349560, total buys 9.6043 BNB (57 sent buys)",
        "label": "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - NAMED (debtdog / debtdog) - ANOMALY, reported once as signal run 102",
        "note": "ANOMALY under the fast-path amendment: name/symbol APPEARED - name 'debtdog', symbol 'debtdog', confirmed via fast_rpc; totalSupply 1e27; "
                "decimals 18. DexScreener independently confirms debtdog/debtdog, pair 0x70b31f93bff68d87ccd7b11c4458af5a7deb8d44, pair created 2h 8m ago, "
                "224 txns, volume $18K, buys 87/sells 137, liquidity <$1 (drained after the rotation's sells), pooled debtdog 60,759,293 + WBNB 0.00005574. "
                "First buy 20:51:46 WIB by 0xcb08c02c0a, 0.000123025 BNB -> 9,826.24 tokens. Wallet set byte-identical to the other run-102 rotations and diff 0 "
                "vs the run-101 machine set (27/27 overlap). Buy sizes WITHIN class norm - NOT a size anomaly. 99 sells / 27 sell wallets in-window - rotation "
                "fully dumped. Pair token0/token1 NOT read run 102 - retry run 103. Auto-mint BLOCKED at guard (c) - paid PCS token, "
                "no free-mint path. Do not re-signal unless a new fact appears.",
    },
    {
        "address": "0x07b225cecc3733f71fd613dbf80a275dfd5a7777",
        "first_seen": "run-102, 2026-11-07 21:15:28 WIB (tx 0xf5ced4bd56..., block 132214945)",
        "machine_wallets": 27,
        "typical_first_buy_bnb": 0.000123025,
        "followup_buy_range_bnb": "median 0.223379289, max 0.396382, total buys 9.2459 BNB (53 sent buys)",
        "label": "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - NAMED (币安币 / 币安币) - ANOMALY, reported once as signal run 102",
        "note": "ANOMALY under the fast-path amendment: name/symbol APPEARED - name '币安币', symbol '币安币', confirmed via fast_rpc (decimals failed pass 1, "
                "retried OK = 18); totalSupply 1e27; decimals 18. DexScreener independently confirms 币安币/币安币, pair 0x39f0227ba7aa712db15bdb51046647e8f0939b54, "
                "pair created 1h 45m ago, 217 txns, volume $18K, buys 83/sells 134, liquidity <$1 (drained after the rotation's sells), pooled 59,433,836 + WBNB 0.00005394. "
                "First buy 21:15:28 WIB by 0x36239612 (future1001.ai), 0.000123025 BNB -> 9,816.72 tokens. Wallet set byte-identical to the other run-102 rotations and diff 0 "
                "vs the run-101 machine set (27/27 overlap). Buy sizes WITHIN class norm - NOT a size anomaly. 95 sells / 27 sell wallets in-window - rotation "
                "fully dumped. Pair token0/token1 NOT read run 102 - retry run 103. Auto-mint BLOCKED at guard (c) - paid PCS token, "
                "no free-mint path. Do not re-signal unless a new fact appears.",
    },
    {
        "address": "0xd826883c65bd3b760ee1b0720c8c31cc2b177777",
        "first_seen": "run-102, 2026-11-07 21:45:43 WIB (tx 0x80eec3e4c9..., block 132218975)",
        "machine_wallets": 27,
        "typical_first_buy_bnb": 0.000123025,
        "followup_buy_range_bnb": "median 0.223364190, max 0.382606, total buys 9.8176 BNB (58 sent buys)",
        "label": "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - NAMED (BTC / 比特币) - ANOMALY, reported once as signal run 102",
        "note": "ANOMALY under the fast-path amendment: name/symbol APPEARED - name 'BTC', symbol '比特币', confirmed via fast_rpc; totalSupply 1e27; "
                "decimals 18. DexScreener independently confirms BTC/比特币, pair 0x2315f44831bcac27bd7308e2d50943b4f115f4bd, pair created 1h 14m ago, "
                "227 txns, volume $18K, buys 88/sells 139, liquidity <$1 (drained after the rotation's sells), pooled 60,842,803 + WBNB 0.00005586. "
                "First buy 21:45:43 WIB by 0xcb08c02c0a, 0.000123025 BNB -> 9,826.24 tokens. Wallet set byte-identical to the other run-102 rotations and diff 0 "
                "vs the run-101 machine set (27/27 overlap). Buy sizes WITHIN class norm - NOT a size anomaly. 100 sells / 27 sell wallets in-window - rotation "
                "fully dumped. Pair token0/token1 NOT read run 102 - retry run 103. Auto-mint BLOCKED at guard (c) - paid PCS token, "
                "no free-mint path. Do not re-signal unless a new fact appears.",
    },
    {
        "address": "0x8b19cdca84f9e57cbb2946f1c8d27be25ef87777",
        "first_seen": "run-102, 2026-11-07 22:11:30 WIB (tx 0x5037866306..., block 132222413)",
        "machine_wallets": 27,
        "typical_first_buy_bnb": 0.000123025,
        "followup_buy_range_bnb": "median 0.223364190, max 0.384152, total buys 9.0523 BNB (54 sent buys)",
        "label": "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - NAMED (Kum Jung On / Kum) - ANOMALY, reported once as signal run 102",
        "note": "ANOMALY under the fast-path amendment: name/symbol APPEARED - name 'Kum Jung On', symbol 'Kum', confirmed via fast_rpc; totalSupply 1e27; "
                "decimals 18. DexScreener independently confirms Kum Jung On/Kum, pair 0xf7a2396852111ed1480d4ffca583696369c87eab, pair created 48m ago, "
                "214 txns, volume $18K, buys 84/sells 130, liquidity <$1 (drained after the rotation's sells), pooled Kum 59,199,033 + WBNB 0.00005363. "
                "First buy 22:11:30 WIB by 0xcb08c02c0a, 0.000123025 BNB -> 9,826.24 tokens. Wallet set byte-identical to the other run-102 rotations and diff 0 "
                "vs the run-101 machine set (27/27 overlap). Buy sizes WITHIN class norm - NOT a size anomaly. 91 sells / 27 sell wallets in-window - rotation "
                "fully dumped. Pair token0/token1 NOT read run 102 - retry run 103. Auto-mint BLOCKED at guard (c) - paid PCS token, "
                "no free-mint path. Do not re-signal unless a new fact appears.",
    },
]
s.setdefault("machine_tokens", []).extend(new_entries)

# update stalled labels' run ranges
for e in s["machine_tokens"]:
    if e["address"].lower().startswith("0x1153607e"):
        e["label"] = "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - rotation STALLED at 26 wallets (runs 91-102)"
    if e["address"].lower().startswith("0x79cd174c"):
        e["label"] = "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - rotation STALLED at 20 wallets (runs 90-102)"
    if e["address"].lower().startswith("0x1e9c6d46"):
        e["label"] = "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - NAMED (Seatbelt Dog / Seatbelt) - ANOMALY, reported once as signal run 101 - rotation STALLED at 26/27 sell wallets (union run101+run102)"
        e["note"] = e.get("note", "") + " Run 102: 0 buys, 8 sells / 8 sell wallets (2 new: 0xc194efe22e874a3fe666b5de5a8fd369f12c32d5 + 0xc6591fde9b44aa081062c9fc6ee48e443d24ef57); sell-wallet union run101+run102 = 26/27 - STALLED at 26, did NOT reach 27. NOT a new rotation."

# signaled projects: append the four (paid-only)
s.setdefault("signaled_projects_over_20pct", []).extend([
    "debtdog (debtdog) 0x42637d6471cd50286a0801060d88e05007197777 (paid-only, machine-token, run-102, NAMED - anomaly reported once as signal)",
    "币安币 (币安币) 0x07b225cecc3733f71fd613dbf80a275dfd5a7777 (paid-only, machine-token, run-102, NAMED - anomaly reported once as signal)",
    "BTC (比特币) 0xd826883c65bd3b760ee1b0720c8c31cc2b177777 (paid-only, machine-token, run-102, NAMED - anomaly reported once as signal)",
    "Kum Jung On (Kum) 0x8b19cdca84f9e57cbb2946f1c8d27be25ef87777 (paid-only, machine-token, run-102, NAMED - anomaly reported once as signal)",
])

# ---- next run note: anchored updates on the existing note ----
note = s["next_run_note"]

def rep_once(old, new, tag):
    global note
    c = note.count(old)
    assert c == 1, f"{tag}: anchor count {c} != 1: {old[:120]!r}"
    note = note.replace(old, new)

# (0) window start
rep_once("Next run sent-tx window starts from block 132208027.",
         "Next run sent-tx window starts from block 132224206.", "window")

# (1)+(2) pair retry paragraph + inbound list line: replace span between
# "RETRY run 102:" and "(3) Run-101 inbound window"
i0 = note.index("RETRY run 102: (1) Pair token0/token1 reads")
i1 = note.index("(3) Run-101 inbound window")
new_retry = (
    "RETRY run 103: (1) Pair token0/token1 reads for 0xa6e6... pair 0x9fac925655fa4985ab4fe2fe9e0ca8ae323cc9da and 0x887c... pair "
    "0xa9fa6efb21c252b7d4ab81d19a07ee4ecf6d2c97 (fast_rpc race returns None / 'all endpoints failed', 20 consecutive runs - persistently unreadable, "
    "unverified not absence), plus 0x2bfb pair 0x782671f637bf1a01de482824c4b2520bc58a5a4b, 0xc459 pair 0xeca06856c88fcdf1506886431a079d3f2565ca82, and "
    "rotation 0x43c8 pair 0xaafebb5244e2e546f7cd18a2c89f85bbee03f1e0 (unreadable run 88-102, 15 consecutive - retry opportunistically, not an anomaly), "
    "PLUS run-89 rotation pairs 0xcfdb 0x1e04925db4eabab2917ef73a8cdf232bcc69b5ba, 0x0cf8 0xf6800c4a1ecdffbd64f9047c606bdb32dee0127f, 0xe68b "
    "0xfab7cb4979c9e4738afc61e4974177cf72c50896 (token0/token1 unreadable run 89-102, 14 consecutive; 0x31e4 pair 0x60ca0aef... READ OK run 89), PLUS "
    "run-102 rotation pairs 0x8b19 0xf7a2396852111ed1480d4ffca583696369c87eab + 0xd826 0x2315f44831bcac27bd7308e2d50943b4f115f4bd + 0x07b2 "
    "0x39f0227ba7aa712db15bdb51046647e8f0939b54 + 0x4263 0x70b31f93bff68d87ccd7b11c4458af5a7deb8d44 (NOT read run 102 - retry run 103; DexScreener confirms all four "
    "PCS V2 token/WBNB pairs); 4727 pair 0xf4ee6a9b528670fcdce10c8af0f5262b4fef1d3d READ OK run 102 (token0 = 4727 token, token1 = WBNB) - REMOVED from retry; "
    "1e9c pair 0x533623ca2db657de9a36e84e2b5a809fbee7ecbe READ OK run 102 (token0 = 1e9c token, token1 = WBNB) - REMOVED from retry; db49 pair "
    "0x41cbb4910fd4959f651d7bff8d8b5ed5cd355dfc READ OK run 101 (token0 = WBNB, token1 = db49 token) - REMOVED from retry; ff66 pair "
    "0x2d3e053bada0378299010fde9f59209985760bab READ OK run 101 (token0 = WBNB, token1 = ff66 token) - REMOVED from retry; 0x6b12 pair READ OK run 100 - "
    "already removed; 0x50e4 pair READ OK run 99 - already removed; 41cc pair READ OK run 99 - already removed; run-97 rotation pairs c90a/e3a8 READ OK "
    "run 98 - already removed; run-100 pairs 6f31 0xc9299379d122a1a84d45fdf1ee87dd0ce1a5e3e8 + 0d7e 0x98fe67c6aeb645e6c9aa41c1fd79898261e7fde7 READ OK run 100 "
    "(token0 = token, token1 = WBNB) - no retry needed. "
    "(2) Run-102 inbound list = run101 list (1589) + 70 run-102 deployments + 4 new rotation tokens (total 1663); run-103 inbound list = run102 list (1663) "
    "+ run-103 deployments + new rotation tokens. "
)
note = note[:i0] + new_retry + note[i1:]

# (3) inbound window line
rep_once("(3) Run-101 inbound window FULLY CLOSED in-run (1589/1589, 2 hits - both sent-pass duplicates, 0 failed after same-run retry of 3 failed contracts - "
         "verify at state-update time; if the retry had failures, they are listed in inbound_log_leg_run101.failed_contracts and must be retried in run 102). ",
         "(3) Run-102 inbound window FULLY CLOSED in-run (1663/1663, 1 hit - the sent-pass AFeng tracker tx 0xb8f3ac7e..., 0 failed after same-run retry of 3 failed contracts - "
         "verify at state-update time; if the retry had failures, they are listed in inbound_log_leg_run102.failed_contracts and must be retried in run 103). ",
         "inbound-closed")

# (4) watch paragraph: replace span from "(4) 0x1e9c6d46... rotation STILL FILLING" up to the dedupe sentence start
j0 = note.index("(4) 0x1e9c6d46... rotation STILL FILLING")
j1 = note.index("Dedupe new mints against all tx hashes")
new_watch = (
    "(4) 0x1e9c6d46... (Seatbelt) rotation STALLED at 26/27 sell wallets (union run101+run102; 0 buys + 8 sells run 102, 2 new sell wallets 0xc194... + 0xc659...) - "
    "did NOT reach 27; watch run 103 the same way, do NOT treat continuation as a new rotation. 0xdb4950e7... rotation COMPLETED run 100 (sell-wallet union "
    "run99+run100 = 27/27) - do NOT treat any db49 activity as a new rotation. 0x1153607e... rotation STALLED at 26 wallets (0 wallets runs 91-102, 12th quiet "
    "run after debut) - watch run 103 the same way. 0x79cd... STALLED at 20 wallets (0 wallets runs 90-102, 13th quiet run after debut) - same. Run-101 named "
    "rotations 0x4727.../0x1e9c...: 4727 0 wallets run 102 (1st quiet run after debut) - watch run 103 the same way. Run-100 named rotations 0x6f31.../0x0d7e...: "
    "0 wallets run 102 (2nd quiet run after debut) - same. Run-99 named rotations 0x50e4.../0x6b12.../0xff66...: 0 wallets run 102 (3rd quiet run after debut) - "
    "same. Run-98 named rotations 0x41cc.../0x43bc.../0x2120.../0xda79...: 0 wallets run 102 (5th quiet run after debut) - same. Run-97 named rotations "
    "0xc90a.../0xe3a8...: 0 wallets run 102 (5th quiet run after debut) - same. "
)
note = note[:j0] + new_watch + note[j1:]

# dedupe: append run-102 tracker repeats after the run-101 sentence
rep_once("Run-101 added TWO more repeats of the same pattern (0x522c6c82... 0.5 BNB + 0x62fb2bb4... 1 BNB, both AFeng sale-calls with 0x636f tracker mint logs) - also NOT new. ",
         "Run-101 added TWO more repeats of the same pattern (0x522c6c82... 0.5 BNB + 0x62fb2bb4... 1 BNB, both AFeng sale-calls with 0x636f tracker mint logs) - also NOT new. "
         "Run-102 added SEVEN more mint-pattern txs, ALL the same dividend-tracker mechanism, NONE new: 0xb8f3ac7e... (AFeng sale-call, 0x636f tracker, moco, 0.15 BNB - known repeat); "
         "FIVE AFeng sale-calls with NEW tracker 0x0c84... (token corla 0xd2c1..., total 2.225 BNB: 0xe8824827... 0.225 + 0xc7c21408... 0.75 + 0xcc0815ca... 0.5 + 0x791b4b79... 0.5 + 0xa2b5b308... 0.25); "
         "ONE 0x2325 aggregator tx 0x42d33fdb... with NEW tracker 0x5e07... (token BAGENT 0x0e22..., 0.1 BNB). The trackers differ per reflection token - a new tracker contract does NOT make it a new mint: "
         "the 'mint' is tracker shares minted 1:1 with a PAID buy, not a free mint. corla 0xd2c1... is a DIFFERENT contract from the run-63 paid-only signal CORLA 0x4a9c. ",
         "dedupe-repeats")

# append run-102 entry to the paid-only signals list (after the run-101 entry's ending anchor)
rep_once("db49/ff66 pairs READ OK run 101 (token0 = WBNB, token1 = token) - removed from retry list; new run-101 pairs 4727/1e9c NOT read (fast_rpc race outage) - retry run 102) ",
         "db49/ff66 pairs READ OK run 101 (token0 = WBNB, token1 = token) - removed from retry list; new run-101 pairs 4727/1e9c NOT read (fast_rpc race outage) - retry run 102) "
         "run 102 (FOUR NEW rotations 0x8b19... Kum Jung On/Kum + 0xd826... BTC/比特币 + 0x07b2... 币安币/币安币 + 0x4263... debtdog/debtdog at 27 wallets each - ALL NAMED, "
         "sixth consecutive run with named rotations, anomaly reported once as signal run 102; buy sizes in class norm; all four fully dumped in-window (91/95/100/99 sells, 27 sell wallets each); "
         "1e9c STALLED at 26/27 sell wallets (union run101+run102, 0 buys + 8 sells run 102); 4727 0 wallets (1st quiet run after debut); 6f31/0d7e 0 wallets (2nd quiet run); "
         "50e4/6b12/ff66 0 wallets (3rd quiet run); 41cc/43bc/2120/da79 0 wallets (5th quiet run); c90a/e3a8 0 wallets (5th quiet run); 0x1153... STALLED at 26, 12th quiet run; "
         "0x79cd... STALLED at 20, 13th quiet run; 70 deployments (sixth straight run with deployments, 0x9b519f5d alone 10); inbound FULLY CLOSED in-run (b3 stalled ~10 min at 50/863 "
         "with a live process, resumed on its own - no kill needed), 1663 contracts, 16,849 logs, 1 hit (the sent-pass AFeng tracker tx 0xb8f3ac7e...), 0 failed after same-run retry of 3 failed "
         "contracts; run-102 NULL receipts (9, all 0xad94ee77 PCS buys/sells) RECOVERED same-run (all status 1, 5 logs each); 4727/1e9c pairs READ OK run 102 (token0 = token, token1 = WBNB) - "
         "removed from retry list; new run-102 pairs 8b19/d826/07b2/4263 NOT read (fast_rpc race outage continues) - retry run 103) ",
         "paid-list-run102")

# append "Paid fact: run102" after the "Paid fact: run101" paragraph (anchor on its ending)
rep_once("all run-66/68/69/70/71/72/73/74/75/76/77/78/79 machine tokens 0 wallets. ",
         "all run-66/68/69/70/71/72/73/74/75/76/77/78/79 machine tokens 0 wallets. "
         "Paid fact: run102 FOUR NEW rotations 0x8b19... (Kum Jung On/Kum) + 0xd826... (BTC/比特币) + 0x07b2... (币安币/币安币) + 0x4263... (debtdog/debtdog) at 27 wallets each - ALL NAMED, "
         "sixth consecutive run with named rotations (anomaly: name/symbol appeared; reported once as signal run 102, paid-only, auto-mint blocked guard (c)); "
         "run-101 tokens 0x4727... 0 wallets (1st quiet run after debut); 1e9c STALLED at 26/27 sell wallets (union run101+run102); run-100 tokens 0x6f31.../0x0d7e... 0 wallets (2nd quiet run after debut); "
         "run-99 tokens 0x50e4.../0x6b12.../0xff66... 0 wallets (3rd quiet run after debut); run-98 tokens 0x41cc.../0x43bc.../0x2120.../0xda79... 0 wallets (5th quiet run after debut); "
         "run-97 tokens 0xc90a.../0xe3a8... 0 wallets (5th quiet run after debut); run-90 tokens 0x6a25.../0x9f7e.../0x8c64.../0xc1ab.../0x1153... 0 wallets (12th quiet run after debut); "
         "run-89 tokens 0xcfdb.../0x0cf8.../0xe68b.../0x31e4... 0 wallets (13th quiet run after debut); run-88 tokens 0x43c8.../0x3d12.../0xeae0... 0 wallets (14th quiet run after debut); "
         "run-87 tokens 0x889a.../0x4249... 0 wallets (15th quiet run after debut); run-86 tokens 0x2bfb.../0xc459... 0 wallets (16th quiet run after debut); run-85 token 0x2717... 0 wallets (17th quiet run); "
         "run-82 tokens 0xd468.../0xa6e6.../0x887c... all 0 wallets (20th quiet run after debut); run-81 tokens 0 wallets (21st quiet run); run-80 token 0 wallets (22nd quiet run); "
         "GrokBot 0xfcd0... absent (0 wallets) - 43rd consecutive quiet run (59, 61-102) after the run-60 burst; CORLA-97af 0 wallets; CORLA 0x4a9c 0 wallets; all run-64/65 ASI contracts 0 wallets; "
         "all run-66/68/69/70/71/72/73/74/75/76/77/78/79 machine tokens 0 wallets. Run 102 had 70 deployments (sixth straight run with deployments; 0x9b519f5d alone 10; added to the inbound list "
         "for run 103 - all 70 addresses recovered from RAW receipts, 0 NULL receipts after same-run recovery of the 9 nulls). AFeng 42 txs (31 sale-calls + 10 approvals + 1 transfer, total value 34.4 BNB - "
         "much bigger than run 101's 4.125 BNB); future1001.ai 16 txs (8 PCS buys + 4 sells + 4 approvals, total value 0.935 BNB - first buyer of the 0x07b2 rotation); 0x2325... 34 txs (24 aggregator 0x27772d13 + "
         "10 approvals, total value 1.45 BNB); 0x8e96... 0 txs; 0x3803... 66 txs (44 aggregator 0x39ecce49 + 22 approvals, total value 0.0006 BNB, churn as usual). "
         "PROCESS LESSON (run 102): chunk b3 stalled ~10 min at 50/863 with a live process - it resumed on its own WITHOUT a kill, so a frozen log with a live process is a stall to WAIT OUT, not a wedge, "
         "unless it stays frozen well past ~10 min while fresh Ankr calls work. fast_rpc race OUTAGE continued (run 102): all-endpoint TimeoutError/OSError flapping ~22:00-00:00 WIB - receipts pass batch "
         "failures forced slow per-tx race fallbacks (~40 min), token-meta pass 1 partial failures (07b2 decimals + 0e22 name failed, retried OK), pair-retry 8/10 failed; later retries succeeded "
         "(token-meta retries, all 9 NULL receipts, 4727/1e9c pairs). A failed race read is UNVERIFIED, never absence - retry, don't conclude. ",
         "paid-fact-run102")

s["next_run_note"] = note

json.dump(s, open(P, "w"), indent=1)
print("state updated; last_run now:", s["last_run"]["run"], "block_end:", s["last_run"]["block_end"])
print("machine_tokens:", len(s.get("machine_tokens", [])), "| signaled:", len(s.get("signaled_projects_over_20pct", [])))
print("inbound102 complete:", s["inbound_log_leg_run102"]["complete"], "| failed:", s["inbound_log_leg_run102"]["failed"],
      "| total_logs:", s["inbound_log_leg_run102"]["total_logs"], "| hits:", s["inbound_log_leg_run102"]["hits"])
print("inbound101 complete:", s["inbound_log_leg_run101"]["complete"], "| failed:", s["inbound_log_leg_run101"]["failed"])
print("next_run_note len:", len(s["next_run_note"]))
