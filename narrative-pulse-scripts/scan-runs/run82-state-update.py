#!/usr/bin/env python3
"""Run 82 state update (read-only job bookkeeping; no chain writes).

Completes run 82 (window 132014632-132023417). Sent/receipts/paid/token-verify/
deployments done; inbound leg ran in full (a 0-400 + b1 400-600 + b2 600-800 +
b3 800-1016) from ONE frozen contract list (run81-inbound-contracts.json, 1016
contracts). If last_run is already 83+ (run 83 started before this update),
merge run-82 results WITHOUT regressing last_run/block_end.
"""
import json, shutil
from pathlib import Path

P = "/home/hatch/workspace/narrative-pulse/tracked-wallet-mint-scan-state.json"
D = Path("/home/hatch/workspace/narrative-pulse/scan-runs")
shutil.copy(P, str(P) + ".bak-run82-pre")
s = json.load(open(P))

ia = json.load(open(D / "run82-inbound-a.json"))
ib1 = json.load(open(D / "run82-inbound-b1.json"))
ib2 = json.load(open(D / "run82-inbound-b2.json"))
ib3 = json.load(open(D / "run82-inbound-b3.json"))
n_logs = ia["total_logs"] + ib1["total_logs"] + ib2["total_logs"] + ib3["total_logs"]
n_hits = len(ia["hits"]) + len(ib1["hits"]) + len(ib2["hits"]) + len(ib3["hits"])
n_failed = len(ia["failed"]) + len(ib1["failed"]) + len(ib2["failed"]) + len(ib3["failed"])
trunc = ia["truncated"] + ib1["truncated"] + ib2["truncated"] + ib3["truncated"]
failed_contracts = [f["contract"] for f in ia["failed"] + ib1["failed"] + ib2["failed"] + ib3["failed"]]
print(f"inbound totals: unique_contracts=1016 logs={n_logs} hits={n_hits} failed={n_failed} truncated={len(trunc)}")
print(f"failed contracts: {failed_contracts}")

cur_run = s.get("last_run", {}).get("run", 0)
last_run_82 = {
    "run": 82,
    "block_start": 132014632,
    "block_end": 132023417,
    "window_wib": "2026-11-06 20:12:27 - 21:18:21 WIB; sent-pass in-window txs 1090, 0 mint-pattern txs",
    "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set); 0 failed. RETRY run-81 window for 0x5b2f11cab406f580a7c6faf620ee35daaf8648a5 (failed run 81, Ankr 'Remote end closed connection'): 0 txs in blocks 132005907-132014631 - run-81 window activity for that wallet is now VERIFIED as 0 sent txs, not a failure; item closed.",
    "method_note": (
        "Sent pass Ankr ankr_getTransactionsByAddress via module (55/55, 0 failed; "
        "1090 txs, 34 wallets active). Receipts via fast_rpc batch (6, ~4s pause) for 697 "
        "non-approve candidates: final 692 status 1, 5 status 0, 0 null, 0 mint-pattern txs. "
        "Status-0 detail: 5x failed PCS sells (0x791ac947, value 0) by 0x3628764a65 (20:55:19 WIB), "
        "0xdb2d83f907 (20:23:07 WIB), 0xc621946845 (21:04:24 WIB), 0xa952331ea4 (20:43:28 WIB), "
        "0x92bc32975b (20:25:24 WIB). "
        "AFeng 1 sent tx (call to 0x1de4... selector 0x4d819a2a, 0.145 BNB, 20:39:25 WIB, receipt status 1, "
        "13 logs, NO zero-from Transfer - NOT a mint); future1001.ai 0 txs; 0x2325... 0 txs; 0x8e96... 0 txs; "
        "0x5b2f... 0 txs in run-82 window. "
        f"Inbound leg per 2026-11-03 12:02 amendment: Ankr getLogs address-filtered per contract, "
        f"1016 unique contracts, {n_logs} logs summed, "
        f"{n_hits} hit(s), {n_failed} failed, run as a (0-400, {ia['total_logs']} logs, {len(ia['hits'])} hits, "
        f"{len(ia['failed'])} failed, {len(ia['truncated'])} truncated) "
        f"+ b1 (400-600, {ib1['total_logs']} logs, {len(ib1['hits'])} hits, {len(ib1['failed'])} failed, {len(ib1['truncated'])} truncated) "
        f"+ b2 (600-800, {ib2['total_logs']} logs, {len(ib2['hits'])} hits, {len(ib2['failed'])} failed, {len(ib2['truncated'])} truncated) "
        f"+ b3 (800-1016, {ib3['total_logs']} logs, {len(ib3['hits'])} hits, {len(ib3['failed'])} failed, {len(ib3['truncated'])} truncated), "
        "from ONE frozen contract list (run81-inbound-contracts.json, 1016 contracts, same list as run 81). "
        f"{n_hits} hit(s) - NO inbound-only mints this run. "
        f"Truncated {len(trunc)} (all topic-filtered to 0 logs, incl. 0x1de4... AFeng sale, 0x6288... AGC sale, "
        "0x636f... AFeng tracker, 0x55d3... USDT, 0x63de... AGC). "
        f"Failed {n_failed} (all Ankr 'Remote end closed connection without response': "
        "0x55d3... USDT, 0x8cc3..., 0xbcc5..., 0xc34c...) - their window activity is UNVERIFIED, retry run 83, "
        "never reported as 0. "
        "INFRA NOTES: (1) First inbound part-a attempt died silently mid-run (~100/400, no error, process gone - "
        "same shape as run 14's service-restart cut); leg re-run in full (a + b1/b2/b3 in parallel) and the "
        "complete re-run is what counts. (2) Ankr getLogs ~4s/contract tonight (probe call 3.92s for a 0-log "
        "contract) - the leg took ~1h wall time across the re-run; part b was split into 3 parallel chunks "
        "to finish before the next run. (3) fast_rpc eth_call flaky mid-run ('all endpoints failed' on "
        "several endpoints): 0x887c name/symbol/decimals/totalSupply/owner + pair token0/token1 for all "
        "three pairs initially unreadable - 0x887c + d468 pair re-verified after recovery (see paid_signal_run82); "
        "a6e6/887c pair token0/token1 still unreadable after retries - UNVERIFIED, not absence. "
        "Ankr getTransactionsByHash returned 'no tx' for the two AFeng-distribution txs (method/index gap, "
        "same as run 81's distributor txs - not proof the txs do not exist; both confirmed by receipts). "
        "No preview/mint/sign/login/purchase by this job."
    ),
}
if cur_run < 82:
    s["last_run"] = last_run_82
    print(f"last_run set to 82 (was {cur_run})")
else:
    print(f"last_run already {cur_run} (>=82) - NOT regressing; run-82 results merged below only")
    s.setdefault("run82_last_run_record", last_run_82)

s["paid_signal_run82"] = {
    "note": "NEW paid-only machine-token rotation (NOT a buy recommendation, NOT executable Free Bacot, NOT an auto-mint trigger by itself). THREE distinct NEW contracts, bought by the SAME byte-identical 27-wallet set (27/27 each, diff 0 vs the run-81 27-set, overlap 27/27; the three sets are identical to each other too) - the set that also bought CORLA (run 63), ASI quad-1 (run 64), ASI quad-2 (run 65), the two run-66 tokens, the two run-68 tokens, the run-69 token, the five run-70 tokens, the six run-71 tokens, the three run-72 tokens, the four run-73 tokens, the four run-74 tokens, the three run-75 tokens, the two run-76 tokens, the three run-77 tokens, the two run-78 tokens, the two run-79 tokens, the run-80 token and the two run-81 tokens - the machine rotated again: run-81 two tokens -> these three tokens, with run-81 tokens 0x7f7a.../0x33f7... fully quiet (0 wallets) this run. NO CHAT REPORT for this rotation per the 2026-11-06 ~18:30 machine-token fast-path amendment: routine rotation, no anomaly in a listed class (buy-size shape matches run 81, no name/symbol, no website, no free-mint path) - recorded in state only. One recorded oddity (same class as run 81, NOT a listed anomaly, not reported): the first tracked Transfer of a6e6 and 887c was a bulk distribution TO AFeng, not a machine buy - see afeng_distribution_oddity.",
    "project": "NEW paid tokens, same 27-wallet machine set (unnamed, three tokens)",
    "contracts": [
        "0xd4689089b842d3d6fc5db80f09d0cf30710a7777",
        "0xa6e6df413cb8e876c6f85bfc788478109c577777",
        "0x887cf69e1d86ac9bad48f44347c56052128b7777"
    ],
    "name_symbol_onchain": "name() and symbol() both return EMPTY strings on-chain for ALL THREE tokens (verified via fast_rpc eth_call decode; 0x887c initially unreadable on fast_rpc 'all endpoints failed', re-verified on retry); decimals 18; totalSupply 1e27 (1,000,000,000,000,000,000,000,000,000) for all three; owner() returns the zero address for all three.",
    "pairs": {
        "0xd4689089b842d3d6fc5db80f09d0cf30710a7777": "PCS V2 pair 0xbf4cd9fbd198725e22bbf0fb38086703b2ec29cf, token0 WBNB 0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c, token1 the token itself (verified after fast_rpc recovery)",
        "0xa6e6df413cb8e876c6f85bfc788478109c577777": "PCS V2 pair 0x9fac925655fa4985ab4fe2fe9e0ca8ae323cc9da; token0/token1 UNREADABLE after repeated retries (fast_rpc 'all endpoints failed') - unverified, not absence",
        "0x887cf69e1d86ac9bad48f44347c56052128b7777": "PCS V2 pair 0xa9fa6efb21c252b7d4ab81d19a07ee4ecf6d2c97; token0/token1 UNREADABLE after repeated retries (fast_rpc 'all endpoints failed') - unverified, not absence"
    },
    "first_tracked_transfers": {
        "0xd4689089b842d3d6fc5db80f09d0cf30710a7777": "machine buy: 8.394 tokens to 0xcb08c02c0a (27-set) in tx 0x75a89bc2e0e0056ac436432e4004932b4f34d9057213de97c645fc69ca4f772f, block 132020748, 20:58:20 WIB, value 0.000105197854608339 BNB, selector 0xb6f9de95 (router buy)",
        "0xa6e6df413cb8e876c6f85bfc788478109c577777": "bulk distribution TO AFeng (0xbf004bff64): 50,278.20616691389 tokens in tx 0x282436db148f74c1beb66185b1e69da098c6b59efb914b53124328436a88e89e, block 132018375; tx sent directly TO the pair 0x9fac... (receipt status 1, 162 logs, 1 Transfer-to-tracked); sender UNVERIFIED (Ankr getTransactionsByHash returns no tx; fast_rpc eth_getTransaction failing) - same oddity class as run 81",
        "0x887cf69e1d86ac9bad48f44347c56052128b7777": "bulk distribution TO AFeng (0xbf004bff64): 66,885.03790900267 tokens in tx 0xaefd47ea65ab273f361465c6479411b5900c7df24fc33949f2ea112d4029407d, block 132015957; tx sent directly TO the pair 0xa9fa... (receipt status 1, 162 logs, 1 Transfer-to-tracked); sender UNVERIFIED (Ankr getTransactionsByHash returns no tx; fast_rpc eth_getTransaction failing) - same oddity class as run 81"
    },
    "afeng_distribution_oddity": "First tracked Transfer of a6e6 (50,278.21 tokens, tx 0x282436db, block 132018375) and 887c (66,885.04 tokens, tx 0xaefd47ea, block 132015957) was a bulk distribution TO AFeng (0xbf004bff64), not a machine buy. Difference vs run 81: run-81 distributions came from distributor contracts (0xb31d.../0x231e...) called by non-tracked callers; run-82 distribution txs were sent directly TO the pair contracts, sender unverified. NOT a free-mint path for the user wallet (recipient was AFeng, chosen by the sender) and no name/symbol/website appeared - machine-token label stands. Recorded, NOT a chat report (not a listed fast-path anomaly).",
    "buy_shape": "Per-token receipt-attributed router buys (selector 0xb6f9de95, 27 wallets each): d468 first buys min 0.000105 / max 0.37165 BNB, follow-ups n=29, median 0.1885, max 0.404; a6e6 first buys min 0.000106 / max 0.371702, follow-ups n=28, median 0.2345, max 0.3876; 887c first buys min 0.00011 / max 0.371687, follow-ups n=27, median 0.1939, max 0.3967. 27-set window totals: buys 165, buy_value 29.2418 BNB, sells 317, approves 312, deployments 42 (all 14 deploying wallets in the 27-set; 42 created addresses, all status 1, none is a new paid token). Shape matches run 81 (tiny first buy ~0.0001, follow-ups ~0.19-0.40).",
    "old_machine_tokens_quiet": "All prior machine tokens 0 wallets this run: CORLA 0x4a9c, GrokBot 0xfcd0, all 4 ASI quad-1, all 4 ASI quad-2, both run-66, both run-68, run-69, all 5 run-70, all 6 run-71, all 3 run-72, all 4 run-73, all 4 run-74, all 3 run-75, both run-76, all 3 run-77, both run-78, both run-79, run-80 0x489e, both run-81 (0x7f7a/0x33f7).",
    "guard_c_block": "Auto-mint BLOCKED at guard (c): no free-mint path (paid PCS buys only, no name/symbol/website, no contractURI/tokenURI evidence). Do not re-signal or re-report unless a new fact appears (genuine free-mint path, name/symbol, or website)."
}

s["paid_trend_run82"] = {
    "note": "Aggregate only, NOT a buy recommendation. No token reaches the signal threshold.",
    "new_machine_rotation": "THREE new unnamed tokens at 27 wallets each (0xd468.../0xa6e6.../0x887c...), same byte-identical 27-wallet machine set as runs 63-81; run-81 tokens fully quiet. See paid_signal_run82. No chat report (fast-path amendment).",
    "other_paid_activity": [
        {"pattern": "42 other paid tokens max 3 wallets each (21 at 3, 14 at 2, 7 at 1 - usual ...7777 churn)", "wallets": "see run82-paid.json"},
        {"pattern": "5x failed PCS sells (0x791ac947, value 0, receipt status 0, 0 logs)", "wallets": ["0x3628764a65", "0xdb2d83f907", "0xc621946845", "0xa952331ea4", "0x92bc32975b"]},
        {"pattern": "1 call to 0x1de4... sale contract, selector 0x4d819a2a, 0.145 BNB, receipt status 1, 13 logs, NO zero-from Transfer - not a mint", "wallet": "0xbf004bff64 (AFeng)"},
        {"pattern": "42 contract deployments, all status 1, 14 deploying wallets, all in the 27-wallet machine set; 42 created addresses, none is a new paid token", "wallets": "machine set"}
    ],
    "quiet": "future1001.ai 0 txs; 0x2325... 0 txs; 0x8e96... 0 txs; 0x5b2f... 0 txs (run-82 window; run-81 window retry also 0 txs, verified); GrokBot 0xfcd0... absent (0 wallets) - 23rd consecutive quiet run (59, 61-82) after the run-60 burst; CORLA-97af 0 wallets; CORLA 0x4a9c 0 wallets; all run-64/65 ASI contracts 0 wallets; all run-66/68/69/70/71/72/73/74/75/76/77/78/79/80/81 machine tokens 0 wallets."
}

s["inbound_log_leg_run82"] = {
    "contracts": 1016,
    "total_logs": n_logs,
    "hits": n_hits,
    "failed": n_failed,
    "failed_contracts": failed_contracts,
    "note": (
        f"Ankr getLogs address-filtered per contract, window 132014632-132023417, "
        f"a (0-400, {ia['total_logs']} logs, {len(ia['hits'])} hits, {len(ia['failed'])} failed, {len(ia['truncated'])} truncated) "
        f"+ b1 (400-600, {ib1['total_logs']} logs, {len(ib1['hits'])} hits, {len(ib1['failed'])} failed, {len(ib1['truncated'])} truncated) "
        f"+ b2 (600-800, {ib2['total_logs']} logs, {len(ib2['hits'])} hits, {len(ib2['failed'])} failed, {len(ib2['truncated'])} truncated) "
        f"+ b3 (800-1016, {ib3['total_logs']} logs, {len(ib3['hits'])} hits, {len(ib3['failed'])} failed, {len(ib3['truncated'])} truncated), "
        "from ONE frozen contract list (run81-inbound-contracts.json, 1016 contracts - same list as run 81, no new mint contracts to add, machine tokens not added per precedent). "
        f"{n_hits} hits - 0 NEW inbound-only mints. "
        f"Truncated {len(trunc)} (all topic-filtered to 0 logs). "
        f"Failed {n_failed} (all Ankr 'Remote end closed connection without response'): {failed_contracts} - "
        "their window activity is UNVERIFIED, retry run 83, never reported as 0. "
        "First part-a attempt died silently at ~100/400 (no error, process gone - service-restart shape, as run 14); "
        "leg re-run in full (a + b1/b2/b3 parallel) and the complete re-run counts. Ankr getLogs ~4s/contract tonight."
    )
}

new_tokens = [
    {
        "address": "0xd4689089b842d3d6fc5db80f09d0cf30710a7777",
        "first_seen": "run-82, 2026-11-06 20:58:20 WIB (first machine buy tx 0x75a89bc2e0e0056ac436432e4004932b4f34d9057213de97c645fc69ca4f772f, block 132020748)",
        "machine_wallets": 27,
        "typical_first_buy_bnb": 0.000105197854608339,
        "followup_buy_range_bnb": "median ~0.19, max ~0.40",
        "label": "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB)",
        "note": "Routine rotation, no anomaly in a listed class; recorded in state WITHOUT chat report per fast-path amendment. No name/symbol, no website, no free-mint path. Auto-mint blocked at guard (c). Pair PCS V2 0xbf4cd9fbd198725e22bbf0fb38086703b2ec29cf (token0 WBNB, token1 token). First tracked Transfer was a normal machine buy (0xcb08..., 8.394 tokens)."
    },
    {
        "address": "0xa6e6df413cb8e876c6f85bfc788478109c577777",
        "first_seen": "run-82, 2026-11-06 ~20:37 WIB (first tracked Transfer tx 0x282436db148f74c1beb66185b1e69da098c6b59efb914b53124328436a88e89e, block 132018375)",
        "machine_wallets": 27,
        "typical_first_buy_bnb": 0.000106,
        "followup_buy_range_bnb": "median ~0.23, max ~0.39",
        "label": "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB)",
        "note": "Routine rotation, no anomaly in a listed class; recorded in state WITHOUT chat report per fast-path amendment. No name/symbol, no website, no free-mint path. Auto-mint blocked at guard (c). Pair PCS V2 0x9fac925655fa4985ab4fe2fe9e0ca8ae323cc9da (token0/token1 unreadable - fast_rpc flaky, unverified not absence). First tracked Transfer was a bulk distribution of 50,278.21 tokens TO AFeng (see paid_signal_run82 afeng_distribution_oddity) - not a machine buy, not a free-mint path."
    },
    {
        "address": "0x887cf69e1d86ac9bad48f44347c56052128b7777",
        "first_seen": "run-82, 2026-11-06 ~20:14 WIB (first tracked Transfer tx 0xaefd47ea65ab273f361465c6479411b5900c7df24fc33949f2ea112d4029407d, block 132015957)",
        "machine_wallets": 27,
        "typical_first_buy_bnb": 0.00011,
        "followup_buy_range_bnb": "median ~0.19, max ~0.40",
        "label": "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB)",
        "note": "Routine rotation, no anomaly in a listed class; recorded in state WITHOUT chat report per fast-path amendment. No name/symbol, no website, no free-mint path. Auto-mint blocked at guard (c). Pair PCS V2 0xa9fa6efb21c252b7d4ab81d19a07ee4ecf6d2c97 (token0/token1 unreadable - fast_rpc flaky, unverified not absence). First tracked Transfer was a bulk distribution of 66,885.04 tokens TO AFeng (see paid_signal_run82 afeng_distribution_oddity) - not a machine buy, not a free-mint path."
    },
]
existing = {t.get("address", "").lower() for t in s.get("machine_tokens", [])}
for t in new_tokens:
    if t["address"].lower() not in existing:
        s.setdefault("machine_tokens", []).append(t)
        print("added machine token", t["address"][:10])
    else:
        print("already present", t["address"][:10])

s["next_run_note"] = (
    "Next run sent-tx window starts from block 132023418. RETRY run 83: inbound leg for 4 contracts that FAILED run 82 "
    "(all Ankr 'Remote end closed connection without response'): 0x55d398326f99059ff775485246999027b3197955 (USDT), "
    "0x8cc3d52e886423e093c307399e2915d95c92e0f9, 0xbcc595ba692188a499026cd9dc0e6df00b19d1ec, 0xc34c51d6cc280b35577b2d45b956ab7300d372d5 "
    "- their run-82 window activity is UNVERIFIED, do not report as 0. Also retry pair token0/token1 reads for "
    "0xa6e6... pair 0x9fac925655fa4985ab4fe2fe9e0ca8ae323cc9da and 0x887c... pair 0xa9fa6efb21c252b7d4ab81d19a07ee4ecf6d2c97 "
    "(fast_rpc 'all endpoints failed' run 82). Dedupe new mints against all tx hashes in reported_findings "
    "(223 mint entries over 221 unique tx hashes, direct count run 77). Run-75 mint tx 0x23cd8740... (AFeng, tracker 0x636f..., "
    "0.15 BNB) is a KNOWN REPEAT of the run-70 finding - do not report as new if it repeats again. "
    "Paid-only signals run 63 (CORLA 0x4a9c), run 64 (4 ASI), run 65 (4 ASI quad-2), run 66 (tokens 0x19b7.../0x540d...), "
    "run 68 (tokens 0xf3cc.../0xe7e2...), run 69 (token 0x4d15...), run 70 (FIVE tokens 0x4df7.../0xae06.../0x2516.../0x1247.../0x8e0d...), "
    "run 71 (SIX tokens 0xe51b.../0xc2e1.../0x5785.../0xfff4.../0xe4c9.../0x25b4...), run 72 (THREE tokens 0x26ef.../0x7145.../0xdfb3...), "
    "run 73 (FOUR tokens 0x4bd1.../0x1d9f.../0xe0f0... at 27 wallets + 0x198c... at 21 wallets), "
    "run 74 (FOUR tokens 0xe4e0.../0x4d2e.../0xaf84... at 27 wallets + 0x73c9... at 26 wallets), "
    "run 75 (THREE tokens 0x167b.../0x5205.../0x4f6d... at 27 wallets each), run 76 (TWO tokens 0x0cda... at 27 wallets + 0xacc8... at 26 wallets), "
    "run 77 (THREE tokens 0x3029.../0x5eb1.../0x1a57... at 27 wallets each), run 78 (TWO tokens 0xcbbc.../0x41cc... at 27 wallets each), "
    "run 79 (TWO tokens 0x5833.../0x32b4... at 27 wallets each), run 80 (ONE token 0x489e... at 27 wallets), "
    "run 81 (TWO tokens 0x7f7a.../0x33f7... at 27 wallets each), run 82 (THREE tokens 0xd468.../0xa6e6.../0x887c... at 27 wallets each) "
    "auto-mint BLOCKED at guard (c) - do not re-signal or re-report the block unless a new mint/buy fact appears for those contracts "
    "(e.g. a genuine free-mint path). Per the 2026-11-06 ~18:30 machine-token fast-path amendment, routine machine-token rotations are "
    "recorded in state WITHOUT a chat report (no full verification per run); report only on anomaly (buy size far off norm, name/symbol appears, "
    "website, or free-mint path). Paid fact: run82 max 27 wallets/token (THREE new unnamed tokens 0xd468.../0xa6e6.../0x887c..., same byte-identical "
    "27-wallet machine set as runs 63-81 - machine rotated again: run-81 two tokens -> these three tokens, with run-81 tokens 0x7f7a.../0x33f7... "
    "fully quiet (0 wallets) this run; the other 42 paid tokens max 3 wallets each (21 at 3, 14 at 2, 7 at 1 - usual ...7777 churn); "
    "GrokBot 0xfcd0... absent (0 wallets) this run - 23rd consecutive quiet run (59, 61-82) after the run-60 burst; CORLA-97af 0 wallets; "
    "CORLA 0x4a9c 0 wallets; all four run-64 ASI contracts 0 wallets; all four run-65 ASI quad-2 contracts 0 wallets; both run-66 tokens 0 wallets; "
    "both run-68 tokens 0 wallets; run-69 token 0x4d15 0 wallets; all five run-70 tokens 0 wallets; all six run-71 tokens 0 wallets; "
    "all three run-72 tokens 0 wallets; all four run-73 tokens 0 wallets; all four run-74 tokens 0 wallets; all three run-75 tokens 0 wallets; "
    "both run-76 tokens 0 wallets; all three run-77 tokens 0 wallets; both run-78 tokens 0 wallets; both run-79 tokens 0 wallets; "
    "run-80 token 0x489e... 0 wallets; both run-81 tokens 0 wallets. NEW run-82 oddity (recorded, NOT a chat report - same class as run 81, not a listed "
    "fast-path anomaly): the FIRST tracked Transfer of a6e6 (50,278.21 tokens, tx 0x282436db, block 132018375) and 887c (66,885.04 tokens, "
    "tx 0xaefd47ea, block 132015957) was a bulk-distribution transfer TO AFeng (0xbf004bff64), via txs sent directly to the pair contracts "
    "(0x9fac.../0xa9fa...), sender unverified (Ankr getTransactionsByHash returns no tx; fast_rpc eth_getTransaction failing). "
    "NOT a free-mint path for the user wallet (recipient was AFeng, chosen by the sender) and no name/symbol/website appeared - machine-token label stands. "
    "AFeng 1 sent tx this run (0.145 BNB to 0x1de4... sale contract, no mint); future1001.ai 0 txs; 0x2325... 0 txs; 0x8e96... 0 txs; 0x5b2f... 0 txs. "
    "OVERLAP NOTE: run 82 finished ~22:13 WIB, after run 83's 22:05 WIB start - if run 83's sent pass began before this update, it used "
    "FROM_BLOCK 132014632 (state still showed run 81) and re-scanned run 82's window; dedupe by tx hash applies, no mint findings to double-report, "
    "and the 3 run-82 machine tokens are already recorded in machine_tokens - do not re-add them. "
    "Same-owner factory groups now also include 0x293f and 0x1103 (proven 2026-11-06 ~01:14 WIB, AGENTS.md) alongside the groups listed in the body."
)

json.dump(s, open(P, "w"), indent=1)
print("state updated, machine_tokens total:", len(s.get("machine_tokens", [])))
