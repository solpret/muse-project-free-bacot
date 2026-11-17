#!/usr/bin/env python3
"""Run 73 state update (read-only job bookkeeping; no chain writes).

Completes run 73 (window 131934410-131942443), whose sent/receipts/paid/
token-verify/deployments passes are all done and whose inbound leg ran in
full (a 0-400 + b 400-1003 re-run in full after the first b attempt died in a
VM reboot; 0 hits, 0 failed in the end).
"""
import json
import shutil
from pathlib import Path

P = "/home/hatch/workspace/narrative-pulse/tracked-wallet-mint-scan-state.json"
D = Path("/home/hatch/workspace/narrative-pulse/scan-runs")

shutil.copy(P, str(P) + ".bak-run73-pre")
s = json.load(open(P))
ia = json.load(open(D / "run73-inbound-a.json"))
ib = json.load(open(D / "run73-inbound-b.json"))
n_contracts = ia["contracts_checked"] + ib["contracts_checked"]
n_logs = ia["total_logs"] + ib["total_logs"]
n_hits = len(ia["hits"]) + len(ib["hits"])
n_failed = len(ia["failed"]) + len(ib["failed"])
trunc = ia["truncated"] + ib["truncated"]
assert n_contracts == 1003 and n_logs == 15964 and n_hits == 0, \
    (n_contracts, n_logs, n_hits)
assert n_failed == 0, (n_failed, ia["failed"], ib["failed"])
assert len(trunc) == 7, trunc

s["last_run"] = {
    "run": 73,
    "block_start": 131934410,
    "block_end": 131942443,
    "window_wib": "2026-11-06 10:10:40 - 11:10:54 WIB; sent-pass in-window txs 1033, 0 mint-pattern txs",
    "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set)",
    "method_note": (
        "Sent pass Ankr ankr_getTransactionsByAddress via module (55/55, 0 failed; "
        "1033 txs, 34 wallets active). Receipts via fast_rpc batch (6, ~4s pause) for 662 "
        "non-approve candidates: 657 status 1, 5 status 0 (all failed PCS sells 0x791ac947: "
        "0xcdaeb6dc... by 0xdb2d83f907 10:49:23 WIB, 0x35e582ee... by 0xc621946845 10:30:42 WIB, "
        "0xf84dcebe... by 0x9cdd08f301 10:11:08 WIB, 0xee0462da... by 0xa952331ea4 11:10:28 WIB, "
        "0xbbee2217... by 0xa952331ea4 10:31:39 WIB), 0 null, 0 mint-pattern logs. "
        f"Inbound leg per 2026-11-03 12:02 amendment: Ankr getLogs address-filtered per contract, "
        f"{n_contracts} contracts, {n_logs} logs, {n_hits} hits, {n_failed} failed in the end, run as a "
        f"(0-400, {ia['total_logs']} logs, {len(ia['truncated'])} truncated, {len(ia['failed'])} failed) "
        f"+ b (400-{n_contracts}, {ib['total_logs']} logs, {len(ib['truncated'])} truncated, {len(ib['failed'])} failed). "
        "Part b was first attempted as run73-inbound-b (died at 133/603 with 1 transient Ankr failure "
        "0x86a49a9e..., no json saved) when the VM rebooted ~04:59 UTC (uptime showed 11 min at 05:10 UTC); "
        "it was RE-RUN IN FULL as run73-inbound-b2 (603 contracts, 5922 logs, 0 hits, 0 failed, 0 truncated) "
        "- the 0x86a49a9e... contract passed cleanly in the re-run, so no contract is left unverified and no "
        "retry is owed to run 74. Coverage complete: all 1003 sorted contracts checked once. "
        "Truncated 7 (all in part a: 0x10b389... AFeng tracker owner / 0x1de4... AFeng sale / 0x53ba... tracker / "
        "0x55d3... USDT / 0x6288... AGC sale / 0x636f... AFeng tracker / 0x63de... AGC - all topic-filtered, 0 logs each). "
        "DYOR: contract 0x86956bc830eb62110820ae79164bef61c7e31936 in set (via snapshot), 0 hits - "
        "no tracked wallet minted DYOR in this window. "
        "CORLA 0x4a9c499574ea003846e81522d59aa4c27ca47777, the 4 run-64 ASI contracts, the 4 run-65 "
        "ASI quad-2 contracts, the 2 run-66 tokens, the 2 run-68 tokens, the run-69 token 0x4d15... "
        "the 5 run-70 tokens, the 6 run-71 tokens, the 3 run-72 tokens, and GrokBot 0xfcd04501ebaddcda73095a75e078a8e5292f7777 are NOT in the "
        "inbound set (PCS tokens; all their activity was wallet-sent txs covered by the sent pass). "
        "The 4 new run-73 paid tokens are likewise NOT in the inbound set - sent-pass covered. "
        "45 contract creations in window (all by 15 wallets of the 27-wallet machine set, all status 1; "
        "none is any of the 4 new tokens). "
        "No preview/mint/sign/login/purchase by this job. "
        "INFRA NOTES: (1) run73-receipts.py was built by sed from run72 and the sed missed the paid-map "
        "path, so the receipts run OVERWROTE run72-paid.json with run-73 data; recovered by mv to "
        "run73-paid.json (verified: 26 keys, 0x4bd1 at 27 wallets, run-72 tokens at 0) and the script path "
        "was fixed. Run-72 per-token wallet lists are lost from the file; the key facts survive in state "
        "(paid_signal_run72/paid_trend_run72) and the run-72 log entry, and the run-72 27-set is recoverable "
        "as byte-identical to run-71's set in run71-paid.json. (2) fast_rpc endpoints flaky in spots this run "
        "(symbol() 0x1d9f..., decimals() 0xe0f0..., pair token0()/token1() for 0x4bd1/0x1d9f... all 'all endpoints "
        "failed', incl. a full 7-endpoint timeout burst during the retry pass) - all recorded as unreadable/transient, "
        "NOT as empty/zero; receipts all recovered, 0 null in the end."
    ),
}
s["next_run_note"] = (
    "Next run sent-tx window starts from block 131942444. Dedupe new mints against all tx hashes "
    "in reported_findings (runs 1-41: 219 txs; run 70 added 1 new finding tx (AFeng 0x5f560493...); "
    "run 71 added 1 new finding tx (0x2325 0xa20c70c1...); run 72 added 0; run 73 added 0, total 221). Paid-only signals run 63 "
    "(CORLA 0x4a9c), run 64 (4 ASI), run 65 (4 ASI quad-2), run 66 (tokens 0x19b7.../0x540d...), run 68 "
    "(tokens 0xf3cc.../0xe7e2...), run 69 (token 0x4d15...), run 70 (FIVE tokens "
    "0x4df7.../0xae06.../0x2516.../0x1247.../0x8e0d...), run 71 (SIX tokens "
    "0xe51b.../0xc2e1.../0x5785.../0xfff4.../0xe4c9.../0x25b4...), run 72 (THREE tokens "
    "0x26ef.../0x7145.../0xdfb3...), run 73 (FOUR tokens 0x4bd1.../0x1d9f.../0xe0f0... at 27 wallets + "
    "0x198c... at 21 wallets) auto-mint BLOCKED at guard (c) "
    "- do not re-signal or re-report the block unless a new mint/buy fact appears for those contracts "
    "(e.g. a genuine free-mint path). Paid fact: run73 max 27 wallets/token (THREE new unnamed tokens "
    "at 27 wallets each + one at 21 wallets, same byte-identical 27-wallet machine set as runs 63-66/68/69/70/71/72 - machine "
    "rotated again: run-72 three tokens -> quiet for them (0 wallets) -> these four tokens; the 21-wallet set is a "
    "subset of the 27-set); the other 22 paid tokens max 3 wallets each (11 at 3, 6 at 2, 5 at 1 - usual ...7777 churn); "
    "GrokBot 0xfcd0... absent (0 wallets) this run - 14th consecutive quiet run (59, 61, 62, 63, 64, 65, 66, "
    "67, 68, 69, 70, 71, 72, 73) after the run-60 burst; CORLA-97af 0 wallets; CORLA 0x4a9c 0 wallets; all "
    "four run-64 ASI contracts 0 wallets; all four run-65 ASI quad-2 contracts 0 wallets; both run-66 "
    "tokens 0 wallets; both run-68 tokens 0 wallets; run-69 token 0x4d15 0 wallets; all five run-70 "
    "tokens 0 wallets; all six run-71 tokens 0 wallets; all three run-72 tokens 0 wallets. Inbound retry next run: none open - run-73 window fully closed this run "
    "(1003/1003, 0 hits, 0 failed after the full b re-run). AFeng 0 txs this run; 0x2325... 0 txs; future1001.ai 0 txs; 0x8e96... 0 txs. "
    "Same-owner factory groups now also include 0x293f and 0x1103 (proven 2026-11-06 ~01:14 WIB, AGENTS.md) alongside the groups listed in the body."
)
s["paid_signal_run73"] = {
    "note": ("NEW paid-only signal (NOT a buy recommendation, NOT executable Free Bacot, NOT an "
             "auto-mint trigger by itself). Same-machine warning: FOUR distinct NEW contracts, "
             "three bought by the SAME byte-identical 27-wallet set (27/27, pairwise diffs 0/0/0, and diff 0 "
             "vs the run-71 27-set: overlap 27/27) and the fourth by 21 wallets that are a SUBSET of that "
             "same 27-set - the set that also bought CORLA (run 63), ASI quad-1 (run 64), "
             "ASI quad-2 (run 65), the two run-66 tokens, the two run-68 tokens, the run-69 token, the "
             "five run-70 tokens, the six run-71 tokens and the three run-72 tokens - the machine rotated again: CORLA (63) -> "
             "ASI quad-1 (64) -> ASI quad-2 (65) -> two unnamed tokens (66) -> quiet (67) -> two new "
             "tokens (68) -> one token (69) -> five tokens (70) -> six tokens (71) -> three tokens (72) -> "
             "these four tokens (73). The four are NOT one project - 4 different contracts, never merged."),
    "project": "NEW paid tokens, same 27-wallet machine set (unnamed)",
    "contracts": [
        "0x4bd131d1b0e7824e0dc35fca80c30cf24d167777",
        "0x1d9f4deecd45f624bd36be64c2c93d3cbedc7777",
        "0xe0f0dcfb256b689508a0bd9ece66e59a14667777",
        "0x198c1af4ff6732ab7a5c29fffe01a8637f9a7777",
    ],
    "name_symbol_onchain": ("name() and symbol() both return EMPTY strings on-chain for 0x4bd1, 0xe0f0 and 0x198c "
        "(verified via fast_rpc eth_call decode); for 0x1d9f name() is empty but symbol() was UNREADABLE transiently "
        "('all endpoints failed', twice incl. retry - NOT proven empty); decimals 18 for 0x4bd1/0x1d9f/0x198c, "
        "decimals() for 0xe0f0 UNREADABLE transiently ('all endpoints failed', twice); totalSupply 1e27 "
        "(1,000,000,000,000,000,000,000,000,000) for all four; "
        "owner() 0x0 for all four; tokenURI not attempted (no name/symbol identity to resolve, paid "
        "PCS tokens - same treatment as run-66/run-68/run-69/run-70/run-71/run-72 tokens)"),
    "participation": ("3 tokens at 27 / 55 wallets (49.1%) + 1 token at 21 / 55 wallets (38.2%); "
        "0xe0f0 was already bought by 4 machine wallets in run 72 (per run-72 log/trend) and is new only in "
        "crossing the thresholds this run; the other three are 0 wallets in run 72 (new this run); "
        "first tracked buys (selector 0xb6f9de95, wallet 0xcb08c02c0a unless noted, ~9,092,300 tokens, 0.000114 BNB): "
        "0x1d9f 10:29:00 WIB (tx 0x4be105296c57a928b5857c1070b8b6d596913783b55e56d6bdfaebe47e94590f, pair 0xece51df8...), "
        "0x4bd1 10:48:47 WIB (tx 0x6570ef33d98c43830d78f4c41138114313e4ba0c470cbfacd7a86ba191adef06, pair 0x8f40e852...), "
        "0x198c 11:07:39 WIB (tx 0xd6ffebf499bba366dc261c93b3c19337cdc1d4709934b711e45463be5a22d375, pair 0xb3157a76...); "
        "0xe0f0 first tracked buy 10:10:44 WIB (tx 0x1101b78cd85460181ceca9515278de1e6a4cf5a60096259d4b286f7e62322633, wallet "
        "0xc194efe22e, 0.27075 BNB, ~11,721,396 tokens - UNUSUALLY LARGE vs the machine norm of 0.000114 BNB, pair 0xc4f73160...); "
        "tracked Transfer logs in window: 62 / 60 / 50 / 33 respectively; caveat: the FIRST tracked Transfer (any sender) "
        "for 0x4bd1 (block 131939472, tx 0xe361911b..., from 0x6b7d7275..., ~16.28 tokens) and for 0x1d9f (block 131936833, "
        "tx 0xbca23a58..., from 0x4f68dd3c..., ~27.13 tokens) came from NON-tracked senders (both txs confirmed absent from "
        "sent.json) - small external transfers to tracked wallets, not tracked-wallet buys; not previously "
        "signaled; not in Free Bacot snapshot; not in bridge (paid-only PCS tokens, per "
        "CORLA/GrokBot/ASI precedent)"),
    "buy_evidence": (
        "Sample PCS buys verified (receipt Transfer from pair + pair token0/token1 on-chain where readable). "
        "Pairs verified on-chain: 0xe0f0 pair 0xc4f73160d81a31857accda225fb0b8a5f218d0c1 (token0 WBNB 0xbb4c..., token1 token); "
        "0x198c pair 0xb3157a768a50d53e73b2c3de5313a77ef8f0d52d (token0 token, token1 WBNB); "
        "0x4bd1 pair token0/token1 UNREADABLE transiently (fast_rpc 'all endpoints failed' twice) - pair addresses "
        "0x6b7d7275... (first-transfer source) and 0x8f40e852... (first tracked-buy source) identified from Transfer logs only; "
        "0x1d9f pair token0/token1 likewise UNREADABLE transiently - pair addresses 0x4f68dd3c... (first-transfer source) "
        "and 0xece51df8... (first tracked-buy source) from logs only. "
        "27-wallet set window totals (all router activity, not per-token; recomputed from sent.json "
        "by literal selectors, matching token-verify.py): 193x buys (0xb6f9de95, total buy value "
        "37.2276 BNB) + 325x sells (0x791ac947) + 322x approve (0x095ea7b3) + 45x contract creations."),
    "linkage": ("NOT verified: the 27 wallets are BYTE-IDENTICAL to the run-63 CORLA / run-64 ASI / "
        "run-65 ASI quad-2 / run-66 two-token / run-68 two-token / run-69 one-token / run-70 "
        "five-token / run-71 six-token / run-72 three-token sets (verified set equality vs run-71: diff 0, overlap 27/27; "
        "the 21-wallet set for 0x198c is a subset of the 27-set) "
        "and deployed 45 contracts in this window via 15 wallets, which suggests the same "
        "coordinated/machine operator, but no entity collapse is applied - counted per wallet with "
        "this note, as in run 60 GrokBot / run 63 CORLA precedents"),
    "auto_mint_block": ("Trigger >25% met numerically for all four (27 >= 14, 21 >= 14) but BLOCKED at "
        "guard (c): paid PCS tokens, no free-mint quota/path for the user wallet - buying would cost "
        "BNB, never a free mint; guard (a) website also unverified (empty name/symbol, no website "
        "evidence). No preview, no execution. Do not re-report the block unless a genuine free-mint "
        "path appears for these contracts."),
    "deployments_context": ("45 contract-creation txs by 15 of the 27 wallets in this window "
        "(0xdb2d83f9 x4, 0xc6219468 x4, 0x9cdd08f3 x1, 0xaa49e7fe x3, 0x3154f694 x3, 0xca4e67bb x3, "
        "0x5b4beded x4, 0x36239612 x4, 0xf9689b9d x5, 0x2cc8192f x2, 0x1cce4ec5 x3, 0xc0c84518 x3, "
        "0xa952331e x1, 0x64e893a4 x1, 0x97bd895f x4), all status 1; "
        "all 45 created addresses READ from receipts this run (saved in run73-deployments.json) and NONE is any of "
        "the four new tokens - the new tokens were first bought via PCS pairs, not "
        "deployed in-window by a tracked wallet; token identity (name/symbol) of the 45 created "
        "contracts was NOT checked, so whether any of them is a future machine token is UNVERIFIED"),
}
s["paid_trend_run73"] = {
    "note": "Aggregate only, NOT a buy recommendation. FOUR NEW paid-only signals (3 at 27 wallets, 1 at 21 wallets - see paid_signal_run73); all other tokens far below threshold.",
    "max_wallets_per_token": 27,
    "distribution": "26 paid tokens: 27 wallets x3 (NEW unnamed machine tokens), 21 wallets x1 (NEW unnamed machine token 0x198c...), 3 wallets x11, 2 wallets x6, 1 wallet x5 (all others ...7777-suffixed churn tokens)",
    "other_paid_activity": [
        {"pattern": "AFeng 0 txs; 0x2325... 0 txs; future1001.ai 0 txs; 0x8e96... 0 txs - all four quiet this run", "wallet": "0xbf004bff64725914ee36d03b87d6965b0ced4903 / 0x2325f175975abdbcde555c79cc8e63381d28551b / 0x355ea9e542b36c645a2dee63b9df079ccb9bf3db / 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6"},
        {"pattern": "5 status-0 receipts, all failed PCS sells (0x791ac947) by machine wallets, not mints", "wallet": "machine wallets"},
    ],
    "deployments": "45 contract creations in window, all by 15 wallets of the 27-wallet machine set (see paid_signal_run73 deployments_context)",
    "future1001": "0 tx this run (0x355ea9e542b36c645a2dee63b9df079ccb9bf3db)",
}
s["inbound_log_leg_run73"] = {
    "contracts": n_contracts,
    "total_logs": n_logs,
    "hits": n_hits,
    "failed": 0,
    "failed_contracts": [],
    "note": (f"Ankr getLogs address-filtered per contract, window 131934410-131942443, parts a "
             f"(0-400, {ia['total_logs']} logs, {len(ia['truncated'])} truncated, {len(ia['failed'])} failed) "
             f"+ b (400-{n_contracts}, {ib['total_logs']} logs, {len(ib['truncated'])} truncated, {len(ib['failed'])} failed). "
             f"{n_hits} hits - 0 inbound-only new mints. Truncated 7 (a: 0x10b389... / 0x1de4... / "
             "0x53ba... / 0x55d3... USDT / 0x6288... AGC sale / 0x636f... tracker / 0x63de... AGC - all topic-filtered, 0 logs each). "
             "Part b first attempt (run73-inbound-b) died at 133/603 when the VM rebooted ~04:59 UTC; it was RE-RUN IN FULL "
             "(run73-inbound-b2, saved as run73-inbound-b.json): 603 contracts, 5922 logs, 0 hits, 0 failed - the transient "
             "0x86a49a9e... Ankr failure from the first attempt passed cleanly in the re-run. "
             "DYOR 0x8695... in set (via snapshot), 0 hits. No residual open from run 72 (its window fully "
             "closed, 0 failed). CORLA 0x4a9c + 4 run-64 ASI + 4 run-65 ASI quad-2 + the 2 run-66 tokens + "
             "the 2 run-68 tokens + the run-69 token + the 5 run-70 tokens + the 6 run-71 tokens + the 3 run-72 tokens + GrokBot 0xfcd0... + the 4 new "
             "run-73 tokens not in inbound set (PCS tokens; sent-pass covered). New contracts deployed this hour (45, all "
             "addresses read, none is any of the 4 new tokens) are not in the inbound set - their token "
             "identity (name/symbol) is UNVERIFIED."),
}
sp = s.setdefault("signaled_projects_over_20pct", [])
for new_sig in [
    "Unnamed token (name/symbol empty) 0x4bd131d1b0e7824e0dc35fca80c30cf24d167777 (paid-only, run-73)",
    "Unnamed token (name/symbol empty) 0x1d9f4deecd45f624bd36be64c2c93d3cbedc7777 (paid-only, run-73)",
    "Unnamed token (name/symbol empty) 0xe0f0dcfb256b689508a0bd9ece66e59a14667777 (paid-only, run-73)",
    "Unnamed token (name/symbol empty) 0x198c1af4ff6732ab7a5c29fffe01a8637f9a7777 (paid-only, run-73)",
]:
    if new_sig not in sp:
        sp.append(new_sig)
json.dump(s, open(P, "w"), indent=1)
print("state updated: run", s["last_run"]["run"])
print(f"inbound: contracts={n_contracts} logs={n_logs} hits={n_hits} failed=0")
print("paid_signal_run73 + paid_trend_run73 + inbound_log_leg_run73 written; signaled list now", len(sp))
print("reported_findings total txs now:", sum(len(f.get('mints', [])) for f in s['reported_findings']))
