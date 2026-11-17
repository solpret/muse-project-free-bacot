#!/usr/bin/env python3
"""Run 72 state update (read-only job bookkeeping; no chain writes).

Completes run 72 (window 131926120-131934409), whose sent/receipts/paid/
token-verify/deployments passes are all done and whose inbound leg ran in
full (a 0-400 + b 400-1003, 1 transient failure recovered by retry, 0 hits).
"""
import json
from pathlib import Path

P = "/home/hatch/workspace/narrative-pulse/tracked-wallet-mint-scan-state.json"
D = Path("/home/hatch/workspace/narrative-pulse/scan-runs")

s = json.load(open(P))
ia = json.load(open(D / "run72-inbound-a.json"))
ib = json.load(open(D / "run72-inbound-b.json"))
retry = json.load(open(D / "run72-inbound-retry-b345.json"))
n_contracts = ia["contracts_checked"] + ib["contracts_checked"]
n_logs = ia["total_logs"] + ib["total_logs"]
n_hits = len(ia["hits"]) + len(ib["hits"])
n_failed = len(ia["failed"]) + len(ib["failed"])
trunc = ia["truncated"] + ib["truncated"]
assert n_contracts == 1003 and n_logs == 18793 and n_hits == 0, \
    (n_contracts, n_logs, n_hits)
assert n_failed == 1 and retry.get("failed") is False and retry.get("hits") == [], \
    (n_failed, retry)
assert len(trunc) == 8, trunc

s["last_run"] = {
    "run": 72,
    "block_start": 131926120,
    "block_end": 131934409,
    "window_wib": "2026-11-06 09:08:42 - 10:10:39 WIB; sent-pass in-window txs 1045, 0 mint-pattern txs",
    "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set)",
    "method_note": (
        "Sent pass Ankr ankr_getTransactionsByAddress via module (55/55, 0 failed; "
        "1045 txs, 35 wallets active). Receipts via fast_rpc batch (6, ~4s pause) for 674 "
        "non-approve candidates: 673 status 1, 1 status 0 (failed PCS sell 0x791ac947 by "
        "0xc621946845, 09:13:16 WIB, tx 0xb7e52e5a...), 0 null, 0 mint-pattern logs. "
        f"Inbound leg per 2026-11-03 12:02 amendment: Ankr getLogs address-filtered per contract, "
        f"{n_contracts} contracts, {n_logs} logs, {n_hits} hits, {n_failed} failed in the main "
        f"pass (1 transient Ankr 'Remote end closed connection' for 0xb3455523cc10061d2e9d5ae67dbcfb4db76727ad, "
        f"recovered by retry: 0 logs, 0 hits, so 0 failed in the end), run as a "
        f"(0-400, {ia['total_logs']} logs, {len(ia['truncated'])} truncated, {len(ia['failed'])} failed) "
        f"+ b (400-{n_contracts}, {ib['total_logs']} logs, {len(ib['truncated'])} truncated, {len(ib['failed'])} failed). "
        "Coverage complete: all 1003 sorted contracts checked once. "
        "Truncated 8 (a: 0x10b389... AFeng tracker owner / 0x1de4... AFeng sale / 0x53ba... tracker / "
        "0x55d3... USDT / 0x6288... AGC sale / 0x636f... AFeng tracker / 0x63de... AGC; b: 0xaea1... "
        "VAULT CRACK - all topic-filtered, 0 logs each). "
        "DYOR: contract 0x86956bc830eb62110820ae79164bef61c7e31936 in set (via snapshot), 0 hits - "
        "no tracked wallet minted DYOR in this window. "
        "CORLA 0x4a9c499574ea003846e81522d59aa4c27ca47777, the 4 run-64 ASI contracts, the 4 run-65 "
        "ASI quad-2 contracts, the 2 run-66 tokens, the 2 run-68 tokens, the run-69 token 0x4d15... "
        "the 5 run-70 tokens, the 6 run-71 tokens, and GrokBot 0xfcd04501ebaddcda73095a75e078a8e5292f7777 are NOT in the "
        "inbound set (PCS tokens; all their activity was wallet-sent txs covered by the sent pass). "
        "The 3 new run-72 paid tokens are likewise NOT in the inbound set - sent-pass covered. "
        "45 contract creations in window (all by 14 wallets of the 27-wallet machine set, all status 1 "
        "after 3 NULL receipts recovered via race fallback; none is any of the 3 new tokens). "
        "No preview/mint/sign/login/purchase by this job. "
        "INFRA NOTE: fast_rpc endpoints flaky in spots this run (decimals()/owner() for 0x7145... "
        "failed transiently 'all endpoints failed', recovered on retry: decimals 18, owner 0x0; "
        "3 deployment receipts initially NULL, recovered via race fallback: status 1 with created "
        "addresses). Ankr closed one connection transiently mid-inbound (0xb345...), recovered by retry."
    ),
}
s["next_run_note"] = (
    "Next run sent-tx window starts from block 131934410. Dedupe new mints against all tx hashes "
    "in reported_findings (runs 1-41: 219 txs; run 70 added 1 new finding tx (AFeng 0x5f560493...); "
    "run 71 added 1 new finding tx (0x2325 0xa20c70c1...); run 72 added 0, total 221). Paid-only signals run 63 "
    "(CORLA 0x4a9c), run 64 (4 ASI), run 65 (4 ASI quad-2), run 66 (tokens 0x19b7.../0x540d...), run 68 "
    "(tokens 0xf3cc.../0xe7e2...), run 69 (token 0x4d15...), run 70 (FIVE tokens "
    "0x4df7.../0xae06.../0x2516.../0x1247.../0x8e0d...), run 71 (SIX tokens "
    "0xe51b.../0xc2e1.../0x5785.../0xfff4.../0xe4c9.../0x25b4...), run 72 (THREE tokens "
    "0x26ef.../0x7145.../0xdfb3...) auto-mint BLOCKED at guard (c) "
    "- do not re-signal or re-report the block unless a new mint/buy fact appears for those contracts "
    "(e.g. a genuine free-mint path). Paid fact: run72 max 27 wallets/token (THREE new unnamed tokens "
    "at 27 wallets each, same byte-identical 27-wallet machine set as runs 63-66/68/69/70/71 - machine "
    "rotated again: run-71 six tokens -> quiet for them (0 wallets) -> these three tokens); the other 28 "
    "paid tokens max 4 wallets each (1 token at 4 wallets, 14 at 3, 5 at 2, 8 at 1 - usual ...7777 churn); "
    "GrokBot 0xfcd0... absent (0 wallets) this run - 13th consecutive quiet run (59, 61, 62, 63, 64, 65, 66, "
    "67, 68, 69, 70, 71, 72) after the run-60 burst; CORLA-97af 0 wallets; CORLA 0x4a9c 0 wallets; all "
    "four run-64 ASI contracts 0 wallets; all four run-65 ASI quad-2 contracts 0 wallets; both run-66 "
    "tokens 0 wallets; both run-68 tokens 0 wallets; run-69 token 0x4d15 0 wallets; all five run-70 "
    "tokens 0 wallets; all six run-71 tokens 0 wallets. Inbound retry next run: none open - run-72 window fully closed this run "
    "(1003/1003, 0 hits, 0 failed after retry). AFeng 18 txs this run (12x tracker calls "
    "0x4d819a2a to 0x1de4... values 0/0.25/0.5/0.75/2.3/5.0 BNB + 6x approve; 0 mint-pattern logs - "
    "no new finding); 0x2325... 0 txs; future1001.ai 0 txs; 0x8e96... 3 txs (2x aggregator 0xef7ec2e7 + "
    "1 approve). Same-owner factory groups now also include 0x293f and 0x1103 (proven 2026-11-06 ~01:14 WIB, AGENTS.md) alongside the groups listed in the body."
)
s["paid_signal_run72"] = {
    "note": ("NEW paid-only signal (NOT a buy recommendation, NOT executable Free Bacot, NOT an "
             "auto-mint trigger by itself). Same-machine warning: THREE distinct NEW contracts, "
             "bought by the SAME byte-identical 27-wallet set (27/27, pairwise diffs 0/0/0, and diff 0 "
             "vs the run-71 27-set: overlap 27/27) that also bought CORLA (run 63), ASI quad-1 (run 64), "
             "ASI quad-2 (run 65), the two run-66 tokens, the two run-68 tokens, the run-69 token, the "
             "five run-70 tokens and the six run-71 tokens - the machine rotated again: CORLA (63) -> "
             "ASI quad-1 (64) -> ASI quad-2 (65) -> two unnamed tokens (66) -> quiet (67) -> two new "
             "tokens (68) -> one token (69) -> five tokens (70) -> six tokens (71) -> these three "
             "tokens (72). The three are NOT one project - 3 different contracts, never merged."),
    "project": "NEW paid tokens, same 27-wallet machine set (unnamed)",
    "contracts": [
        "0x26efdb0dbfff75fff21af39601f590d60dd27777",
        "0x7145739e914cbf7b4ca18d36d3867dda11a67777",
        "0xdfb3f4a716fdc292e41f6b3af5ed7d0c2c3b7777",
    ],
    "name_symbol_onchain": ("name() and symbol() both return EMPTY strings on-chain for all three "
        "(verified via fast_rpc eth_call decode); decimals 18 (0x7145 decimals/owner unreadable "
        "transiently in the first pass, 'all endpoints failed', recovered on retry: decimals 18, "
        "owner 0x0); totalSupply 1e27 (1,000,000,000,000,000,000,000,000,000) for all three; "
        "owner() 0x0 for all three; tokenURI not attempted (no name/symbol identity to resolve, paid "
        "PCS tokens - same treatment as run-66/run-68/run-69/run-70/run-71 tokens)"),
    "participation": ("3 tokens at 27 / 55 wallets (49.1%); "
        "0 wallets for all three in run 71 (new this run); first tracked buys: 0xdfb3 09:11:34 WIB, "
        "0x7145 09:30:46 WIB, 0x26ef 09:49:46 WIB (all selector 0xb6f9de95, "
        "0.000114 BNB, wallet 0xcb08c02c0a, ~9,092,300 tokens each); "
        "tracked Transfer logs in window: 64 / 64 / 62 respectively; not previously "
        "signaled; not in Free Bacot snapshot; not in bridge (paid-only PCS tokens, per "
        "CORLA/GrokBot/ASI precedent)"),
    "buy_evidence": (
        "Sample PCS buys verified (receipt Transfer from pair + pair token0/token1 on-chain). "
        "FIRST tracked buy per token (selector 0xb6f9de95, 0.000114 BNB, ~9,092,300 tokens): "
        "0xdfb3 tx 0x2feccdd0170bf8a0393e591641038da2c702c2de59be1222ebb0c64e57962c6d block "
        "131926534 09:11:34 WIB wallet 0xcb08c02c0a, pair 0xcc965c4fc07ac1aa1d5061c53b5982f11a0f4563; "
        "0x7145 tx 0x5a24678eeb08e54db783d9fd0348f54b1664bd210baf3a85fbb2c5115831a41e block 131929094 "
        "09:30:46 WIB wallet 0xcb08c02c0a, pair 0x496e903657411bcb115a210956eb2e98878ac88b; "
        "0x26ef tx 0xf37eb0fe75c69ee9f3f913ad0c512ee626ab815ea9043ad82e792a6f53f6c0d3 block 131931627 "
        "09:49:46 WIB wallet 0xcb08c02c0a, pair 0x38185a450382d7b71c1eb629175462a9f75c6bdd. "
        "27-wallet set window totals (all router activity, not per-token; recomputed from sent.json "
        "by literal selectors, matching token-verify.py): 194x buys (0xb6f9de95, total buy value "
        "36.6732 BNB) + 310x sells (0x791ac947) + 309x approve (0x095ea7b3) + 45x contract creations."),
    "linkage": ("NOT verified: the 27 wallets are BYTE-IDENTICAL to the run-63 CORLA / run-64 ASI / "
        "run-65 ASI quad-2 / run-66 two-token / run-68 two-token / run-69 one-token / run-70 "
        "five-token / run-71 six-token sets (verified set equality vs run-71: diff 0, overlap 27/27) "
        "and deployed 45 contracts in this window via 14 wallets, which suggests the same "
        "coordinated/machine operator, but no entity collapse is applied - counted per wallet with "
        "this note, as in run 60 GrokBot / run 63 CORLA precedents"),
    "auto_mint_block": ("Trigger >25% met numerically for all three (27 >= 14) but BLOCKED at "
        "guard (c): paid PCS tokens, no free-mint quota/path for the user wallet - buying would cost "
        "BNB, never a free mint; guard (a) website also unverified (empty name/symbol, no website "
        "evidence). No preview, no execution. Do not re-report the block unless a genuine free-mint "
        "path appears for these contracts."),
    "deployments_context": ("45 contract-creation txs by 14 of the 27 wallets in this window "
        "(0xdb2d83f9 x5, 0xc6219468 x4, 0xf795c525 x1, 0xaa49e7fe x4, 0x3154f694 x3, 0xca4e67bb x4, "
        "0x5b4beded x3, 0x36239612 x3, 0xf9689b9d x3, 0x2cc8192f x2, 0x1cce4ec5 x4, 0xc0c84518 x4, "
        "0x64e893a4 x1, 0x97bd895f x4), all status 1 (3 receipts initially NULL, recovered via race "
        "fallback); all 45 created addresses READ from receipts this run (saved in run72-deployments.json) and NONE is any of "
        "the three new tokens - the new tokens were first bought via PCS pairs, not "
        "deployed in-window by a tracked wallet; token identity (name/symbol) of the 45 created "
        "contracts was NOT checked, so whether any of them is a future machine token is UNVERIFIED"),
}
s["paid_trend_run72"] = {
    "note": "Aggregate only, NOT a buy recommendation. THREE NEW paid-only signals at 27 wallets each (see paid_signal_run72); all other tokens far below threshold.",
    "max_wallets_per_token": 27,
    "distribution": "31 paid tokens: 27 wallets x3 (NEW unnamed machine tokens), 4 wallets x1 (unnamed 0xe0f0..., wallets all machine-set members), 3 wallets x14, 2 wallets x5, 1 wallet x8 (all others ...7777-suffixed churn tokens)",
    "other_paid_activity": [
        {"pattern": "AFeng 18 txs: 12x tracker calls 0x4d819a2a to 0x1de4... (values 0 / 0.25 / 0.5 / 0.75 / 2.3 / 5.0 BNB) + 6x approve 0x095ea7b3; 0 mint-pattern logs this run - no new finding, repeat tracker activity only", "wallet": "0xbf004bff64725914ee36d03b87d6965b0ced4903"},
        {"pattern": "2x 0xef7ec2e7 calls via 0xe2ce6ab80874fa9fa2aae65d277dd6b8e65c9de0 (values 0 / 0.002 BNB) + 1x approve, receiving from pair", "wallet": "0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6"},
        {"pattern": "1 status-0 receipt: failed PCS sell (0x791ac947) by 0xc621946845, 09:13:16 WIB, tx 0xb7e52e5a... - machine churn, not a mint", "wallet": "machine wallets"},
        {"pattern": "0x2325... 0 txs; future1001.ai 0 txs", "wallet": "0x2325f175975abdbcde555c79cc8e63381d28551b / 0x355ea9e542b36c645a2dee63b9df079ccb9bf3db"},
    ],
    "deployments": "45 contract creations in window, all by 14 wallets of the 27-wallet machine set (see paid_signal_run72 deployments_context)",
    "future1001": "0 tx this run (0x355ea9e542b36c645a2dee63b9df079ccb9bf3db)",
}
s["inbound_log_leg_run72"] = {
    "contracts": n_contracts,
    "total_logs": n_logs,
    "hits": n_hits,
    "failed": 0,
    "failed_contracts": [],
    "note": (f"Ankr getLogs address-filtered per contract, window 131926120-131934409, parts a "
             f"(0-400, {ia['total_logs']} logs, {len(ia['truncated'])} truncated, {len(ia['failed'])} failed) "
             f"+ b (400-{n_contracts}, {ib['total_logs']} logs, {len(ib['truncated'])} truncated, {len(ib['failed'])} failed). "
             f"{n_hits} hits - 0 inbound-only new mints. Truncated 8 (a: 0x10b389... / 0x1de4... / "
             "0x53ba... / 0x55d3... USDT / 0x6288... AGC sale / 0x636f... tracker / 0x63de... AGC; b: "
             "0xaea1... VAULT CRACK - all topic-filtered, 0 logs each). "
             "1 transient failure in the main pass (0xb345..., Ankr 'Remote end closed connection') "
             "recovered by retry (run72-inbound-retry-b345.json): 0 logs, 0 hits. "
             "DYOR 0x8695... in set (via snapshot), 0 hits. No residual open from run 71 (its window fully "
             "closed, 0 failed). CORLA 0x4a9c + 4 run-64 ASI + 4 run-65 ASI quad-2 + the 2 run-66 tokens + "
             "the 2 run-68 tokens + the run-69 token + the 5 run-70 tokens + the 6 run-71 tokens + GrokBot 0xfcd0... + the 3 new "
             "run-72 tokens not in inbound set (PCS tokens; sent-pass covered). New contracts deployed this hour (45, all "
             "addresses read, none is any of the 3 new tokens) are not in the inbound set - their token "
             "identity (name/symbol) is UNVERIFIED."),
}
sp = s.setdefault("signaled_projects_over_20pct", [])
for new_sig in [
    "Unnamed token (name/symbol empty) 0x26efdb0dbfff75fff21af39601f590d60dd27777 (paid-only, run-72)",
    "Unnamed token (name/symbol empty) 0x7145739e914cbf7b4ca18d36d3867dda11a67777 (paid-only, run-72)",
    "Unnamed token (name/symbol empty) 0xdfb3f4a716fdc292e41f6b3af5ed7d0c2c3b7777 (paid-only, run-72)",
]:
    if new_sig not in sp:
        sp.append(new_sig)
json.dump(s, open(P, "w"), indent=1)
print("state updated: run", s["last_run"]["run"])
print(f"inbound: contracts={n_contracts} logs={n_logs} hits={n_hits} failed=0 (after retry)")
print("paid_signal_run72 + paid_trend_run72 + inbound_log_leg_run72 written; signaled list now", len(sp))
print("reported_findings total txs now:", sum(len(f.get('mints', [])) for f in s['reported_findings']))
