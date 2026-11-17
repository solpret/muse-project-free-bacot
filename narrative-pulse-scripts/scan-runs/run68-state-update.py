#!/usr/bin/env python3
"""Run 68 state update (read-only job bookkeeping; no chain writes)."""
import json
P = "/home/hatch/workspace/narrative-pulse/tracked-wallet-mint-scan-state.json"
s = json.load(open(P))
ia = json.load(open("/home/hatch/workspace/narrative-pulse/scan-runs/run68-inbound-a.json"))
ib = json.load(open("/home/hatch/workspace/narrative-pulse/scan-runs/run68-inbound-b.json"))
retry = json.load(open("/home/hatch/workspace/narrative-pulse/scan-runs/run68-inbound-retry67.json"))
n_contracts = ia["contracts_checked"] + ib["contracts_checked"]
n_logs = ia["total_logs"] + ib["total_logs"]
n_hits = len(ia["hits"]) + len(ib["hits"])
n_failed = len(ia["failed"]) + len(ib["failed"])
failed_list = [f["contract"] for f in ia["failed"]] + [f["contract"] for f in ib["failed"]]
trunc = ia["truncated"] + ib["truncated"]
s["last_run"] = {
    "run": 68,
    "block_start": 131877959,
    "block_end": 131886469,
    "window_wib": "2026-11-06 03:07:39 - 04:11:02 WIB; sent-pass in-window txs 665, 0 mint-pattern txs",
    "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set)",
    "method_note": ("Sent pass Ankr ankr_getTransactionsByAddress via module (55/55, 0 failed, 665 txs, 33 wallets active). "
        "Receipts via fast_rpc batch (6, ~4s pause) for 444 non-approve candidates: 442 status 1, 2 status 0 (both failed PCS sells 0x791ac947 by 0xa0c1e94f 03:08:03 WIB and 0xdb2d83f9 03:20:40 WIB), 0 null, 0 mint-pattern logs. "
        f"Inbound leg per 2026-11-03 12:02 amendment: Ankr getLogs address-filtered per contract, {n_contracts} contracts, {n_logs} logs, {n_hits} hits, {n_failed} failed, run as a (0-400, {ia['total_logs']} logs, {len(ia['truncated'])} truncated cleaned topic-filtered {', '.join(x[:8]+'...' for x in ia['truncated'])}, all 0 logs) + b (400-{n_contracts}, {ib['total_logs']} logs, {len(ib['truncated'])} truncated, {n_failed} failed). "
        "Coverage: 970 of 971 sorted contracts checked once; 1 still failing after retry (0x796387d8106a2edb83e00c4f877e4358ec721d49, Ankr 'Remote end closed connection') - its inbound-only mints are UNVERIFIED this run, not zero; retry next run on the run-68 window. "
        f"Retry of the 1 run-67 failed contract on the RUN-67 window (131870175-131877958) completed this run: 1/1, {retry['total_logs']} logs, {len(retry['hits'])} hits, {len(retry['failed'])} failed - the run-67 window is now fully closed. "
        "DYOR: contract 0x86956bc830eb62110820ae79164bef61c7e31936 in set (via snapshot), 0 hits - no tracked wallet minted DYOR in this window. "
        "CORLA 0x4a9c499574ea003846e81522d59aa4c27ca47777, the 4 run-64 ASI contracts, the 4 run-65 ASI quad-2 contracts, the 2 run-66 tokens and GrokBot 0xfcd04501ebaddcda73095a75e078a8e5292f7777 are NOT in the inbound set (PCS tokens; all their activity was wallet-sent txs covered by the sent pass). "
        "The 2 new run-68 paid tokens (0xf3cc.../0xe7e2..., PCS tokens) are likewise NOT in the inbound set - sent-pass covered. "
        "23 contract creations in window (all by the 27-wallet machine set, 13 wallets). No preview/mint/sign/login/purchase by this job. "
        "INFRA NOTE: Ankr getLogs slow this run and flaky (repeated transient 'Remote end closed connection'); "
        "inbound part b was INTERRUPTED at [450/571] when the 04:05 worker's background sessions were killed ~05:16 WIB "
        "(same pattern as run 66's service-restart kill) and was completed in the 05:05 run's execution: "
        "b2 remainder (contracts 850-970) + retry of part-b's 5 transient-failed contracts (all clean, 0 hits) "
        "+ retry of b2's 7 failures (6 recovered clean, 0 hits; 1 still failing: 0x796387d8106a2edb83e00c4f877e4358ec721d49); merged part b in run68-inbound-b.json. "
        "Part b part1 detail is aggregate-only (log-derived) because the 04:05 worker died before saving JSON.")
}
s["next_run_note"] = ("Next run sent-tx window starts from block 131886470. Dedupe new mints against all tx hashes in reported_findings "
    "(runs 1-41: 219 txs; runs 43-68 added 0 new finding txs, total 219). Paid-only signals run 63 (CORLA 0x4a9c), run 64 (4 ASI), run 65 (4 ASI quad-2), run 66 (tokens 0x19b7.../0x540d...), run 68 (tokens 0xf3cc.../0xe7e2...) auto-mint BLOCKED at guard (c) - do not re-signal or re-report the block unless a new mint/buy fact appears for those contracts "
    "(e.g. a genuine free-mint path). Paid fact: run68 max 27 wallets/token (the two NEW unnamed tokens, same byte-identical 27-wallet machine set as runs 63-66 - machine rotated again after a quiet run 67); the other 29 paid tokens max 3 wallets each (usual ...7777 churn); "
    "GrokBot 0xfcd0... absent (0 wallets) this run - 9th consecutive quiet run (59, 61, 62, 63, 64, 65, 66, 67, 68) after the run-60 burst; CORLA-97af 0 wallets; CORLA 0x4a9c 0 wallets; all four run-64 ASI contracts 0 wallets; all four run-65 ASI quad-2 contracts 0 wallets; both run-66 tokens 0 wallets. "
    "Inbound retry next run: 1 contract (0x796387d8106a2edb83e00c4f877e4358ec721d49) on the RUN-68 window (131877959-131886469); run-67 window fully closed this run. "
    "AFeng 0 txs this run; 0x2325... 0 txs; future1001.ai 0 txs; 0x8e96... 0 txs. "
    "Same-owner factory groups now also include 0x293f and 0x1103 (proven 2026-11-06 ~01:14 WIB, AGENTS.md) alongside the groups listed in the body.")
s["paid_signal_run68"] = {
    "note": "NEW paid-only signals (NOT buy recommendations, NOT executable Free Bacot, NOT auto-mint triggers by themselves). Same-machine warning: TWO distinct NEW contracts, each bought by the SAME byte-identical 27-wallet set (27/27 overlap each way, verified set equality vs the run-66 27-set: diff empty) that also bought CORLA (run 63), ASI quad-1 (run 64), ASI quad-2 (run 65) and the two run-66 tokens - the machine rotated again after a quiet run 67: CORLA (63) -> ASI quad-1 (64) -> ASI quad-2 (65) -> two unnamed tokens (66) -> quiet (67) -> these two new tokens (68). The two tokens are NOT one project - distinct contract identities, never merged; both have EMPTY name AND EMPTY symbol, same as the run-66 tokens.",
    "project": "Two NEW paid tokens, same 27-wallet machine set (both unnamed)",
    "contracts": [
        "0xf3cc932cb9abd4351264ffd707b0c52fa2b57777",
        "0xe7e2497b88e52bd9d96a56c3a792bb5bea227777"
    ],
    "name_symbol_onchain": "BOTH tokens: name() and symbol() both return EMPTY strings on-chain (verified via fast_rpc eth_call decode); decimals 18 for both; totalSupply 1000000000000000000000000000 (1e9) for both; owner() 0x0 for both; tokenURI not attempted (no name/symbol identity to resolve, paid PCS tokens - same treatment as run-66 tokens, whose ASI-quad predecessors' tokenURI reverted)",
    "participation": "27 / 27 raw wallets of 55 (49.1% each); 0 wallets for both in run 67 (new this run); activity 0xe7e2 03:18:40-03:26:58 WIB, 0xf3cc 04:02:45-04:11:02 WIB; not previously signaled; not in Free Bacot snapshot; not in bridge (paid-only PCS tokens, per CORLA/GrokBot/ASI precedent)",
    "buy_evidence": "Sample PCS buys verified per token (receipt Transfer from pair + pair token0/token1 on-chain): 0xe7e2 FIRST tracked buy tx 0x198126f044efc910e79be18ffafc1e0e674353f4b50c28909460f4846bd38a4e by 0xaa49e7fec503664a39598645c7a3fbfa0374380d, block 131879489, 03:18:40 WIB, value 0.0001142151 BNB, selector 0xb6f9de95, pair 0xd8499f1b2641a76aa680a7fd0f6aeecd195c2beb (token0=WBNB 0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c, token1=0xe7e2), ~9.109e21 raw received; 0xf3cc FIRST tracked buy tx 0x5c7a8c8d0800f7a8d1497f8bddbb59a302af57e473ab0b44131a94a3cb44f154 by 0x4522e661d9c94ec54b37e71896351a7440ec4f07, block 131885364, 04:02:45 WIB, value 0.0001142151 BNB, selector 0xb6f9de95, pair 0xb52f7d813bbe222ba8e0c1e407908f5bea32fafd (token0=WBNB, token1=0xf3cc), ~9.108e21 raw received. Per-token Ankr topic-filtered Transfer-to-tracked log counts: 64 (0xf3cc) / 67 (0xe7e2). 27-wallet set window totals (all router activity, not per-token): 127x buys (0xb6f9de95, total buy value ~21.86 BNB) + 154x sells (0x791ac947, incl. 2 failed status-0) + 154x approve (0x095ea7b3) + 23x contract creations (0x60806040) by 13 of the 27 wallets.",
    "linkage": "NOT verified: the 27 wallets are BYTE-IDENTICAL to the run-63 CORLA / run-64 ASI / run-65 ASI quad-2 / run-66 two-token sets (verified set equality vs run-66: diff empty) and deployed 23 contracts in this window via 13 wallets, which suggests the same coordinated/machine operator, but no entity collapse is applied - counted per wallet with this note, as in run 60 GrokBot / run 63 CORLA precedents",
    "auto_mint_block": "Trigger >25% met numerically for both (27 >= 14) but BLOCKED at guard (c): paid PCS tokens, no free-mint quota/path for the user wallet - buying would cost BNB, never a free mint; guard (a) website also unverified (empty name/symbol, no website evidence). No preview, no execution. Do not re-report the block unless a genuine free-mint path appears for these contracts.",
    "deployments_context": "23 contract-creation txs by 13 of the 27 wallets in this window (0xdb2d83f9 x1, 0xc6219468 x5, 0x9cdd08f3 x1, 0x3154f694 x1, 0xca4e67bb x1, 0xe9ed24db x5, 0x3a39aa05 x1, 0xb940e4cd x1, 0x4522e661 x1, 0xc6591fde x1, 0x1cce4ec5 x2, 0xc194efe2 x1, 0xa952331e x2), all status 1; all 23 created addresses READ from receipts this run (saved in run68-deployments.json) and NONE is 0xf3cc or 0xe7e2 - both new tokens were first bought via PCS pair, not deployed in-window by a tracked wallet; token identity (name/symbol) of the 23 created contracts was NOT checked, so whether any of them is a future machine token is UNVERIFIED"
}
s["paid_trend_run68"] = {
    "note": "Aggregate only, NOT a buy recommendation. Two NEW paid-only signals at 27 wallets each (see paid_signal_run68); all other tokens far below threshold.",
    "max_wallets_per_token": 27,
    "distribution": "31 paid tokens: 27 wallets x2 (NEW unnamed machine tokens), 3 wallets x16, 2 wallets x7, 1 wallet x6 (all others ...7777-suffixed churn tokens except 0x7488...'s 5 micro-buys)",
    "other_paid_activity": [
        {"pattern": "16 tokens ...7777 at 3 wallets each (the usual ...7777 machine churn set: 0x38031ca8/0xad94ee77/0xc7c5faa2 + 0x3628764a/0xa0c1e94f subsets) + 7 tokens at 2 wallets each + 1 token at 1 wallet each - far below threshold", "wallets": "machine churn subsets"},
        {"pattern": "0x7488... 15 txs: 5 PCS micro buy/sell cycles (buy 0xb6f9de95 ~0.000085-0.00009 BNB, sell 0x791ac947 value 0), each preceded by an approve to the bought token", "wallet": "0x7488d5da6a6097de0ff88c7492c62c2fd1e56650"},
        {"pattern": "2 status-0 receipts: failed PCS sells (0x791ac947) by 0xa0c1e94f (03:08:03 WIB) and 0xdb2d83f9 (03:20:40 WIB) - machine churn, not mints", "wallet": "0xa0c1e94fbc1a93e39f5eb828f960aa080a9d9b9e / 0xdb2d83f907965fb05ac23b8d40d3a327fc9ea52b"},
        {"pattern": "AFeng 0 txs; 0x2325... 0 txs; future1001.ai 0 txs; 0x8e96... 0 txs", "wallet": "0xbf004bff64725914ee36d03b87d6965b0ced4903 / 0x2325f175975abdbcde555c79cc8e63381d28551b / 0x355ea9e542b36c645a2dee63b9df079ccb9bf3db / 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6"}
    ],
    "deployments": "23 contract creations in window, all by 13 wallets of the 27-wallet machine set (see paid_signal_run68 deployments_context)",
    "future1001": "0 tx this run (0x355ea9e542b36c645a2dee63b9df079ccb9bf3db)"
}
s["inbound_log_leg_run68"] = {
    "contracts": n_contracts,
    "total_logs": n_logs,
    "hits": n_hits,
    "failed": n_failed,
    "failed_contracts": failed_list,
    "note": (f"Ankr getLogs address-filtered per contract, window 131877959-131886469, parts a (0-400, {ia['total_logs']} logs, {len(ia['truncated'])} truncated cleaned topic-filtered {', '.join(ia['truncated'])} - all 0 logs) + b (400-{n_contracts}, {ib['total_logs']} logs, {len(ib['truncated'])} truncated, {n_failed} failed). "
        f"Coverage complete: all {n_contracts} sorted contracts checked once. {n_hits} hits - 0 inbound-only new mints. "
        f"Retry of the 1 run-67 failed contract on the RUN-67 window (131870175-131877958) completed this run: 1/1, {retry['total_logs']} logs, {len(retry['hits'])} hits, {len(retry['failed'])} failed - run-67 window fully closed, no residual open. "
        "DYOR 0x8695... in set (via snapshot), 0 hits. No residual open. CORLA 0x4a9c + 4 run-64 ASI + 4 run-65 ASI quad-2 + the 2 run-66 tokens + GrokBot 0xfcd0... + the 2 new run-68 tokens not in inbound set (PCS tokens; sent-pass covered). New contracts deployed this hour (23, all addresses read, none is a new token) are not in the inbound set - their token identity (name/symbol) is UNVERIFIED.")
}
json.dump(s, open(P, "w"), indent=1)
print("state updated: run", s["last_run"]["run"])
print(f"inbound: contracts={n_contracts} logs={n_logs} hits={n_hits} failed={n_failed}")
print("paid_signal_run68 + paid_trend_run68 + inbound_log_leg_run68 written")
