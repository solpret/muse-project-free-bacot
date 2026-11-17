#!/usr/bin/env python3
"""Run 69 state update (read-only job bookkeeping; no chain writes)."""
import json
from pathlib import Path
P = "/home/hatch/workspace/narrative-pulse/tracked-wallet-mint-scan-state.json"
D = Path("/home/hatch/workspace/narrative-pulse/scan-runs")
s = json.load(open(P))
ia = json.load(open(D / "run69-inbound-a.json"))
ib = json.load(open(D / "run69-inbound-b.json"))
retry = json.load(open(D / "run69-inbound-retry68.json"))
r69 = {}
rp = D / "run69-inbound-retry.json"
if rp.exists():
    r69 = json.load(open(rp))
n_contracts = ia["contracts_checked"] + ib["contracts_checked"]
n_logs = ia["total_logs"] + ib["total_logs"] + r69.get("total_logs", 0)
n_hits = len(ia["hits"]) + len(ib["hits"]) + len(r69.get("hits", []))
# failures still open after retry (if a retry file exists, only its failures remain)
if r69:
    failed_list = [f["contract"] for f in r69.get("failed", [])]
else:
    failed_list = [f["contract"] for f in ia["failed"]] + [f["contract"] for f in ib["failed"]]
n_failed = len(failed_list)
trunc = ia["truncated"] + ib["truncated"] + r69.get("truncated", [])
s["last_run"] = {
    "run": 69,
    "block_start": 131886470,
    "block_end": 131896158,
    "window_wib": "2026-11-06 04:11:19 - 05:23:42 WIB; sent-pass in-window txs 384, 0 mint-pattern txs",
    "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set)",
    "method_note": ("Sent pass Ankr ankr_getTransactionsByAddress via module (55/55 after one retry sweep: "
        "6 wallets transient-failed in the first pass (Ankr 'Remote end closed connection'/timeout cluster), "
        "all 6 recovered on retry with 0 in-window txs each; max_block unchanged 131896158; 384 txs, 33 wallets active). "
        "Receipts via fast_rpc batch (6, ~4s pause) for 277 non-approve candidates: 276 status 1, 1 status 0 "
        "(failed PCS sell 0x791ac947 by 0xc7c5faa2 04:34:49 WIB), 0 null, 0 mint-pattern logs. "
        f"Inbound leg per 2026-11-03 12:02 amendment: Ankr getLogs address-filtered per contract, {n_contracts} contracts, {n_logs} logs, {n_hits} hits, {n_failed} failed, "
        f"run as a (0-400, {ia['total_logs']} logs, {len(ia['truncated'])} truncated, {len(ia['failed'])} failed) + b (400-{n_contracts}, {ib['total_logs']} logs, {len(ib['truncated'])} truncated, {len(ib['failed'])} failed)"
        + (f" + retry of a/b failures ({r69['contracts_checked']} contracts, {r69['total_logs']} logs, {len(r69['hits'])} hits, {len(r69['failed'])} still failing)" if r69 else " (a/b failures NOT retried this run - see next_run_note)") + ". "
        + (f"Coverage: {n_contracts - n_failed} of {n_contracts} sorted contracts checked once; {n_failed} still failing after retry - inbound-only mints from them are UNVERIFIED, not zero; retry next run." if n_failed else f"Coverage complete: all {n_contracts} sorted contracts checked once. ")
        + f"Retry of the 1 run-68 residual contract (0x796387d8106a2edb83e00c4f877e4358ec721d49) on the RUN-68 window (131877959-131886469) completed this run: 1/1, {retry['total_logs']} logs, {len(retry['hits'])} hits, {len(retry['failed'])} failed - the run-68 window is now FULLY closed (971/971, 0 hits). "
        "DYOR: contract 0x86956bc830eb62110820ae79164bef61c7e31936 in set (via snapshot), 0 hits - no tracked wallet minted DYOR in this window. "
        "CORLA 0x4a9c499574ea003846e81522d59aa4c27ca47777, the 4 run-64 ASI contracts, the 4 run-65 ASI quad-2 contracts, the 2 run-66 tokens, the 2 run-68 tokens and GrokBot 0xfcd04501ebaddcda73095a75e078a8e5292f7777 are NOT in the inbound set (PCS tokens; all their activity was wallet-sent txs covered by the sent pass). "
        "The new run-69 paid token (0x4d15..., PCS token) is likewise NOT in the inbound set - sent-pass covered. "
        "26 contract creations in window (all by 11 wallets of the 27-wallet machine set, all status 1). No preview/mint/sign/login/purchase by this job. "
        "INFRA NOTE: Ankr flaky again this run (transient 'Remote end closed connection'/timeout clusters during the sent pass ~05:20-05:35 WIB and at the start of both inbound parts); fast_rpc batch slow once (deployments step) but recovered; the 04:05 worker's background sessions were killed ~05:16 WIB (run-68 completion + first run-69 sent attempt died with them) - relaunches via nohup + disown survived. Inbound part b first attempt was interrupted at 438/569 (worker session ended ~06:07 WIB); part b was re-run IN FULL in this completion (569 contracts, 2716 logs, 0 hits, 4 failed, all 4 recovered on retry) and the re-run numbers are the ones recorded above; the interrupted attempt's log is preserved as run69-inbound-b-part1-interrupted.log.")
}
s["next_run_note"] = ("Next run sent-tx window starts from block 131896159. Dedupe new mints against all tx hashes in reported_findings "
    "(runs 1-41: 219 txs; runs 43-69 added 0 new finding txs, total 219). Paid-only signals run 63 (CORLA 0x4a9c), run 64 (4 ASI), run 65 (4 ASI quad-2), run 66 (tokens 0x19b7.../0x540d...), run 68 (tokens 0xf3cc.../0xe7e2...), run 69 (token 0x4d15...) auto-mint BLOCKED at guard (c) - do not re-signal or re-report the block unless a new mint/buy fact appears for those contracts "
    "(e.g. a genuine free-mint path). Paid fact: run69 max 27 wallets/token (ONE new unnamed token 0x4d15..., same byte-identical 27-wallet machine set as runs 63-66/68 - machine rotated again: run-68 two tokens -> quiet for them -> this one token); the other 29 paid tokens max 3 wallets each (usual ...7777 churn); "
    "GrokBot 0xfcd0... absent (0 wallets) this run - 10th consecutive quiet run (59, 61, 62, 63, 64, 65, 66, 67, 68, 69) after the run-60 burst; CORLA-97af 0 wallets; CORLA 0x4a9c 0 wallets; all four run-64 ASI contracts 0 wallets; all four run-65 ASI quad-2 contracts 0 wallets; both run-66 tokens 0 wallets; both run-68 tokens 0 wallets. "
    + (f"Inbound retry next run: {n_failed} contract(s) ({', '.join(failed_list)}) on the RUN-69 window (131886470-131896158). " if n_failed else "Inbound retry next run: none open - run-68 window fully closed this run, 0 failed contracts this run. ")
    + "AFeng 0 txs this run; 0x2325... 0 txs; future1001.ai 0 txs; 0x8e96... 0 txs. "
    "Same-owner factory groups now also include 0x293f and 0x1103 (proven 2026-11-06 ~01:14 WIB, AGENTS.md) alongside the groups listed in the body.")
s["paid_signal_run69"] = {
    "note": "NEW paid-only signal (NOT a buy recommendation, NOT executable Free Bacot, NOT an auto-mint trigger by itself). Same-machine warning: ONE distinct NEW contract, bought by the SAME byte-identical 27-wallet set (27/27, verified set equality vs the run-68 27-set: diff empty) that also bought CORLA (run 63), ASI quad-1 (run 64), ASI quad-2 (run 65), the two run-66 tokens and the two run-68 tokens - the machine rotated again: CORLA (63) -> ASI quad-1 (64) -> ASI quad-2 (65) -> two unnamed tokens (66) -> quiet (67) -> two new tokens (68) -> this one token (69).",
    "project": "NEW paid token, same 27-wallet machine set (unnamed)",
    "contracts": ["0x4d15f82596c44040c17181d5670f36a5c9807777"],
    "name_symbol_onchain": "name() and symbol() both return EMPTY strings on-chain (verified via fast_rpc eth_call decode); decimals 18; totalSupply 1000000000000000000000000000 (1e9); owner() 0x0; tokenURI not attempted (no name/symbol identity to resolve, paid PCS token - same treatment as run-66/run-68 tokens)",
    "participation": "27 / 27 raw wallets of 55 (49.1%); 0 wallets for it in run 68 (new this run); first tracked buy 04:39:41 WIB; 76 tracked Transfer logs in window; not previously signaled; not in Free Bacot snapshot; not in bridge (paid-only PCS token, per CORLA/GrokBot/ASI precedent)",
    "buy_evidence": "Sample PCS buy verified (receipt Transfer from pair + pair token0/token1 on-chain): FIRST tracked buy tx 0x817efd296fa2f07abfb2794ab23b6f5083533a33b0c012ef7a98d4fc456ed32c by 0xca4e67bb57, block 131890289, 04:39:41 WIB, value 0.0001142151 BNB, selector 0xb6f9de95, pair 0x1d9a9b875920e49a1e5a8b637db0121234caea81 (token0=0x4d15, token1=WBNB 0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c), ~9.109e21 raw received. 27-wallet set window totals (all router activity, not per-token; counted from sent.json by literal selectors - token-verify.py's BUY selector is miscomputed and reports buys=0, do NOT use that figure): 76x buys (0xb6f9de95, total buy value ~6.99 BNB) + 40x sells (0x791ac947) + 40x approve (0x095ea7b3) + 26x contract creations (0x60806040) by 11 of the 27 wallets.",
    "linkage": "NOT verified: the 27 wallets are BYTE-IDENTICAL to the run-63 CORLA / run-64 ASI / run-65 ASI quad-2 / run-66 two-token / run-68 two-token sets (verified set equality vs run-68: diff empty) and deployed 26 contracts in this window via 11 wallets, which suggests the same coordinated/machine operator, but no entity collapse is applied - counted per wallet with this note, as in run 60 GrokBot / run 63 CORLA precedents",
    "auto_mint_block": "Trigger >25% met numerically (27 >= 14) but BLOCKED at guard (c): paid PCS token, no free-mint quota/path for the user wallet - buying would cost BNB, never a free mint; guard (a) website also unverified (empty name/symbol, no website evidence). No preview, no execution. Do not re-report the block unless a genuine free-mint path appears for this contract.",
    "deployments_context": "26 contract-creation txs by 11 of the 27 wallets in this window (0xca4e67bb x2, 0xb940e4cd x1, 0x4522e661 x5, 0x5b4beded x2, 0x36239612 x5, 0xf9689b9d x1, 0x1cce4ec5 x1, 0x92bc3297 x2, 0x9b519f5d x3, 0xfdec62fd x3, 0x64e893a4 x1), all status 1; all 26 created addresses READ from receipts this run (saved in run69-deployments.json) and NONE is 0x4d15 - the new token was first bought via PCS pair, not deployed in-window by a tracked wallet; token identity (name/symbol) of the 26 created contracts was NOT checked, so whether any of them is a future machine token is UNVERIFIED"
}
s["paid_trend_run69"] = {
    "note": "Aggregate only, NOT a buy recommendation. One NEW paid-only signal at 27 wallets (see paid_signal_run69); all other tokens far below threshold.",
    "max_wallets_per_token": 27,
    "distribution": "30 paid tokens: 27 wallets x1 (NEW unnamed machine token), 3 wallets x15, 2 wallets x9, 1 wallet x5 (all others ...7777-suffixed churn tokens except 0x7488...'s 5 micro-buys)",
    "other_paid_activity": [
        {"pattern": "15 tokens ...7777 at 3 wallets each (the usual ...7777 machine churn set) + 9 tokens at 2 wallets each + 5 tokens at 1 wallet each - far below threshold", "wallets": "machine churn subsets"},
        {"pattern": "0x7488... 15 txs: 5 PCS micro buy/sell cycles (buy 0xb6f9de95 ~0.000085-0.00009 BNB, sell 0x791ac947 value 0), each preceded by an approve to the bought token", "wallet": "0x7488d5da6a6097de0ff88c7492c62c2fd1e56650"},
        {"pattern": "1 status-0 receipt: failed PCS sell (0x791ac947) by 0xc7c5faa2 (04:34:49 WIB) - machine churn, not a mint", "wallet": "0xc7c5faa270eb2394c7bf9f411fed0d0126f2eb74"},
        {"pattern": "AFeng 0 txs; 0x2325... 0 txs; future1001.ai 0 txs; 0x8e96... 0 txs", "wallet": "0xbf004bff64725914ee36d03b87d6965b0ced4903 / 0x2325f175975abdbcde555c79cc8e63381d28551b / 0x355ea9e542b36c645a2dee63b9df079ccb9bf3db / 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6"}
    ],
    "deployments": "26 contract creations in window, all by 11 wallets of the 27-wallet machine set (see paid_signal_run69 deployments_context)",
    "future1001": "0 tx this run (0x355ea9e542b36c645a2dee63b9df079ccb9bf3db)"
}
s["inbound_log_leg_run69"] = {
    "contracts": n_contracts,
    "total_logs": n_logs,
    "hits": n_hits,
    "failed": n_failed,
    "failed_contracts": failed_list,
    "note": (f"Ankr getLogs address-filtered per contract, window 131886470-131896158, parts a (0-400, {ia['total_logs']} logs, {len(ia['truncated'])} truncated, {len(ia['failed'])} failed) + b (400-{n_contracts}, {ib['total_logs']} logs, {len(ib['truncated'])} truncated, {len(ib['failed'])} failed)"
        + (f" + retry of a/b failures ({r69['contracts_checked']} contracts, {r69['total_logs']} logs, {len(r69['hits'])} hits, {len(r69['failed'])} still failing)" if r69 else " (a/b failures NOT retried this run)") + f". {n_hits} hits - 0 inbound-only new mints. "
        f"Retry of the 1 run-68 residual contract on the RUN-68 window (131877959-131886469) completed this run: 1/1, {retry['total_logs']} logs, {len(retry['hits'])} hits, {len(retry['failed'])} failed - run-68 window fully closed, no residual open. "
        "DYOR 0x8695... in set (via snapshot), 0 hits. No residual open from run 68. CORLA 0x4a9c + 4 run-64 ASI + 4 run-65 ASI quad-2 + the 2 run-66 tokens + the 2 run-68 tokens + GrokBot 0xfcd0... + the new run-69 token not in inbound set (PCS tokens; sent-pass covered). New contracts deployed this hour (26, all addresses read, none is the new token) are not in the inbound set - their token identity (name/symbol) is UNVERIFIED.")
}
s["inbound_log_leg_retry68"] = retry
sp = s.setdefault("signaled_projects_over_20pct", [])
new_sig = "Unnamed token 0x4d15f82596c44040c17181d5670f36a5c9807777 (paid-only, run-69)"
if new_sig not in sp:
    sp.append(new_sig)
json.dump(s, open(P, "w"), indent=1)
print("state updated: run", s["last_run"]["run"])
print(f"inbound: contracts={n_contracts} logs={n_logs} hits={n_hits} failed={n_failed}")
print("paid_signal_run69 + paid_trend_run69 + inbound_log_leg_run69 written")
