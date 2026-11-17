#!/usr/bin/env python3
"""Run 77 state update (read-only job bookkeeping; no chain writes).

Completes run 77 (window 131974332-131986346), whose sent/receipts/paid/
token-verify/deployments passes are all done and whose inbound leg ran in
full (a 0-400 + b 400-1010) plus the retry of run 76's 2 failed contracts.
"""
import json
import shutil
from pathlib import Path

P = "/home/hatch/workspace/narrative-pulse/tracked-wallet-mint-scan-state.json"
D = Path("/home/hatch/workspace/narrative-pulse/scan-runs")

shutil.copy(P, str(P) + ".bak-run77-pre")
s = json.load(open(P))
ia = json.load(open(D / "run77-inbound-a.json"))
ib = json.load(open(D / "run77-inbound-b.json"))
rt = json.load(open(D / "run77-inbound-retry.json"))
n_contracts = ia["contracts_checked"] + ib["contracts_checked"]
n_logs = ia["total_logs"] + ib["total_logs"]
n_hits = len(ia["hits"]) + len(ib["hits"])
n_failed = len(ia["failed"]) + len(ib["failed"])
trunc = ia["truncated"] + ib["truncated"]
print(f"inbound totals: contracts={n_contracts} logs={n_logs} hits={n_hits} failed={n_failed} truncated={len(trunc)}")
print(f"failed contracts: {[f['contract'] for f in ia['failed'] + ib['failed']]}")
print(f"run-76 retry: contracts={rt['contracts_checked']} logs={rt['total_logs']} hits={len(rt['hits'])} failed={len(rt['failed'])}")

s["last_run"] = {
    "run": 77,
    "block_start": 131974332,
    "block_end": 131986346,
    "window_wib": "2026-11-06 15:10:15 - 16:40:14 WIB; sent-pass in-window txs 976, 0 mint-pattern txs",
    "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set)",
    "method_note": (
        "Sent pass Ankr ankr_getTransactionsByAddress via module (55/55, 0 failed; "
        "976 txs, 35 wallets active). Receipts via fast_rpc batch (6, ~4s pause) for 664 "
        "non-approve candidates: 660 status 1, 4 status 0, 0 null, 0 mint-pattern txs. "
        "Status-0 detail: 4x failed PCS sells 0x791ac947 by machine wallets (0x1df14fa4... by 0xdb2d83f907 16:37:06 WIB, "
        "0x4d9f8cb6... by 0xdb2d83f907 16:13:44 WIB, 0xd6ff5eeb... by 0xa952331ea4 16:39:17 WIB, "
        "0x2041352f... by 0xa952331ea4 16:15:53 WIB). "
        "AFeng 15 sent txs: 9 calls to sale 0x1de460f363af910f51726def188f9004276bf4bc selector 0x4d819a2a "
        "(5 value 0, plus 0.075 BNB 15:24:01 WIB, 0.5 BNB 15:32:15 WIB, 1.2 BNB 15:50:09 WIB, 3.5 BNB 15:27:06 WIB) "
        "+ 5 approves (0x095ea7b3) + 1 transfer 0xa9059cbb value 0 - NO mint log in any receipt, so 0 mint-pattern "
        "txs this run; the run-70 AFeng tracker mint (0x636f...) did NOT repeat (the 0.075 BNB call matches the "
        "run-9 mint-pattern value but produced no zero-address Transfer this time). "
        "future1001.ai 0 txs; 0x2325... 0 txs; 0x8e96... 0 txs. "
        f"Inbound leg per 2026-11-03 12:02 amendment: Ankr getLogs address-filtered per contract, "
        f"{n_contracts} contracts, {n_logs} logs, {n_hits} hit(s), {n_failed} failed, run as a "
        f"(0-400, {ia['total_logs']} logs, {len(ia['hits'])} hits, {len(ia['failed'])} failed, {len(ia['truncated'])} truncated) "
        f"+ b (400-{n_contracts}, {ib['total_logs']} logs, {len(ib['hits'])} hits, {len(ib['failed'])} failed, {len(ib['truncated'])} truncated). "
        f"0 hits - NO inbound-only mints this run. "
        f"Failed: {[f['contract'] for f in ia['failed'] + ib['failed']]} - none, window FULLY CLOSED. "
        f"Truncated {len(trunc)} (all topic-filtered to 0 logs, incl. 0x636f... AFeng tracker, 0x1de4... AFeng sale, 0xaea143... VAULT CRACK). "
        f"Run-76 retry (2 contracts on window 131963292-131974331): {rt['total_logs']} logs, 0 hits, 0 failed - run-76 window now FULLY CLOSED. "
        "DYOR: contract 0x86956bc830eb62110820ae79164bef61c7e31936 in set (via snapshot), 0 hits - "
        "no tracked wallet minted DYOR in this window. "
        "CORLA 0x4a9c499574ea003846e81522d59aa4c27ca47777, the 4 run-64 ASI contracts, the 4 run-65 "
        "ASI quad-2 contracts, the 2 run-66 tokens, the 2 run-68 tokens, the run-69 token 0x4d15... "
        "the 5 run-70 tokens, the 6 run-71 tokens, the 3 run-72 tokens, the 4 run-73 tokens, the 4 run-74 tokens, "
        "the 3 run-75 tokens, the 2 run-76 tokens (0x0cda... 0 wallets, 0xacc8... 0 wallets), and GrokBot "
        "0xfcd04501ebaddcda73095a75e078a8e5292f7777 are NOT in the "
        "inbound set (PCS tokens; all their activity was wallet-sent txs covered by the sent pass). "
        "The 3 new run-77 paid tokens are likewise NOT in the inbound set - sent-pass covered. "
        "46 contract creations in window (all by 20 wallets of the 27-wallet machine set, all status 1; "
        "none is any of the 3 new tokens). "
        "No preview/mint/sign/login/purchase by this job. "
        "INFRA NOTES: (1) Sent pass and inbound-a ran in parallel this run (different services: Ankr txs vs Ankr getLogs) - no failures from the overlap; receipts (fast_rpc) also overlapped inbound-a cleanly. "
        "(2) Ankr getLogs slow stretches again in inbound-b (ranges 350-400 and 400-450 each several minutes with no "
        "progress line) - slow, not stuck, 0 extra failures. (3) No fast_rpc transient unreadable reads noted this run; "
        "token-verify reads (name/symbol/decimals/totalSupply/owner/pair token0/token1) all succeeded for the 3 new tokens."
    ),
}
s["next_run_note"] = (
    "Next run sent-tx window starts from block 131986347. Dedupe new mints against all tx hashes "
    "in reported_findings (223 mint entries over 221 unique tx hashes, direct count this run - the run-75 log's 223 was the mint-entry count, not unique txs; dedupe by tx hash). "
    "Run-75 mint tx 0x23cd8740... (AFeng, tracker 0x636f..., 0.15 BNB) is a KNOWN REPEAT of the run-70 finding - do not report as new if it repeats again. "
    "Paid-only signals run 63 "
    "(CORLA 0x4a9c), run 64 (4 ASI), run 65 (4 ASI quad-2), run 66 (tokens 0x19b7.../0x540d...), run 68 "
    "(tokens 0xf3cc.../0xe7e2...), run 69 (token 0x4d15...), run 70 (FIVE tokens "
    "0x4df7.../0xae06.../0x2516.../0x1247.../0x8e0d...), run 71 (SIX tokens "
    "0xe51b.../0xc2e1.../0x5785.../0xfff4.../0xe4c9.../0x25b4...), run 72 (THREE tokens "
    "0x26ef.../0x7145.../0xdfb3...), run 73 (FOUR tokens 0x4bd1.../0x1d9f.../0xe0f0... at 27 wallets + "
    "0x198c... at 21 wallets), run 74 (FOUR tokens 0xe4e0.../0x4d2e.../0xaf84... at 27 wallets + "
    "0x73c9... at 26 wallets), run 75 (THREE tokens 0x167b.../0x5205.../0x4f6d... at 27 wallets each), run 76 (TWO tokens "
    "0x0cda... at 27 wallets + 0xacc8... at 26 wallets), run 77 (THREE tokens "
    "0x3029.../0x5eb1.../0x1a57... at 27 wallets each) auto-mint BLOCKED at guard (c) "
    "- do not re-signal or re-report the block unless a new mint/buy fact appears for those contracts "
    "(e.g. a genuine free-mint path). Paid fact: run77 max 27 wallets/token (THREE new unnamed tokens, "
    "same byte-identical 27-wallet machine set as runs 63-76 - machine rotated again: run-76 two tokens -> "
    "quiet for both (0 wallets) -> these three tokens; "
    "the other 44 paid tokens max 3 wallets each (18 at 3, 12 at 2, 14 at 1 - usual ...7777 churn); "
    "GrokBot 0xfcd0... absent (0 wallets) this run - 18th consecutive quiet run (59, 61-77) after the run-60 burst; CORLA-97af 0 wallets; CORLA 0x4a9c 0 wallets; all "
    "four run-64 ASI contracts 0 wallets; all four run-65 ASI quad-2 contracts 0 wallets; both run-66 "
    "tokens 0 wallets; both run-68 tokens 0 wallets; run-69 token 0x4d15 0 wallets; all five run-70 "
    "tokens 0 wallets; all six run-71 tokens 0 wallets; all three run-72 tokens 0 wallets; all four "
    "run-73 tokens 0 wallets; all four run-74 tokens 0 wallets; all three run-75 tokens 0 wallets; both run-76 tokens 0 wallets. "
    "Inbound retry next run: none - run 77 inbound had 0 failed contracts, window FULLY CLOSED. "
    "Run-76 window is now FULLY CLOSED (its 2 failed contracts retried OK this run, 6 logs, 0 hits). "
    "AFeng 15 sent txs this run (9 to sale 0x1de4... selector 0x4d819a2a, values 0/0.075/0.5/1.2/3.5 BNB, NO mint log in any; 5 approves; 1 transfer value 0); future1001.ai 0 txs; 0x2325... 0 txs; 0x8e96... 0 txs. "
    "Same-owner factory groups now also include 0x293f and 0x1103 (proven 2026-11-06 ~01:14 WIB, AGENTS.md) alongside the groups listed in the body."
)
s["paid_signal_run77"] = {
    "note": ("NEW paid-only signal (NOT a buy recommendation, NOT executable Free Bacot, NOT an "
             "auto-mint trigger by itself). Same-machine warning: THREE distinct NEW contracts, bought by the SAME byte-identical 27-wallet set "
             "(27/27, pairwise diffs 0/0/0, diff 0 vs the run-76 27-set, overlap 27/27) - the set that also bought CORLA (run 63), ASI quad-1 (run 64), "
             "ASI quad-2 (run 65), the two run-66 tokens, the two run-68 tokens, the run-69 token, the "
             "five run-70 tokens, the six run-71 tokens, the three run-72 tokens, the four run-73 tokens, the four run-74 tokens, the three run-75 tokens and the two run-76 tokens - the machine rotated again: CORLA (63) -> "
             "ASI quad-1 (64) -> ASI quad-2 (65) -> two unnamed tokens (66) -> quiet (67) -> two new tokens (68) -> one token (69) -> five tokens (70) -> six tokens (71) -> three tokens (72) -> "
             "four tokens (73) -> four tokens (74) -> three tokens (75) -> two tokens (76) -> these three tokens (77). The three are NOT one project - 3 different contracts, never merged."),
    "project": "NEW paid tokens, same 27-wallet machine set (unnamed)",
    "contracts": [
        "0x302941695afa1d83d648851b0898e39c63db7777",
        "0x5eb157a3872c019f36989830a26e93ade0d97777",
        "0x1a573d9c3baf15072773b2077d08176335a07777",
    ],
    "name_symbol_onchain": ("name() and symbol() both return EMPTY strings on-chain for all three "
        "(verified via fast_rpc eth_call decode); decimals 18 for all three; totalSupply 1e27 "
        "(1,000,000,000,000,000,000,000,000,000) for all three; "
        "owner() 0x0 for all three; "
        "tokenURI not attempted (no name/symbol identity to resolve, paid PCS tokens - same treatment as run-66/run-68/run-69/run-70/run-71/run-72/run-73/run-74/run-75/run-76 tokens)"),
    "participation": ("0x3029 at 27 / 55 wallets (49.1%), 0x5eb1 at 27 / 55 wallets (49.1%), 0x1a57 at 27 / 55 wallets (49.1%); "
        "all three are 0 wallets in run 76 (new this run); the three 27-wallet sets are BYTE-IDENTICAL (pairwise diffs 0, diff 0 vs the run-76 27-set, incl. 0xe9ed24db10 back in the set after its failed 0xacc8 buy in run 76); "
        "first tracked buys (selector 0xb6f9de95): "
        "0x1a57 15:29:44 WIB (tx 0xdc9b39f00125d3f903fe979a95fe59ef80bb03ea4270360e9c49856381b165b6, block 131976948, wallet 0xcb08c02c0a, 0.000114 BNB, ~9,092,300 token, pair 0x276bf984...), "
        "0x5eb1 16:13:08 WIB (tx 0xfecceb8860661e59519e89435ccc453bebaca29bae51c63f9dd4c6ce249d64c5, block 131982733, wallet 0xcb08c02c0a, 0.00012169 BNB, ~9,633,602 token, pair 0xf5d5099b...), "
        "0x3029 16:36:33 WIB (tx 0xd4d79527f8079adf86ef23f3e4883d47e71d20dd9ca952385faef8e2691a3df9, block 131985856, wallet 0x362396125a, 0.00012169 BNB, ~9,633,602 token, pair 0xebc7d742...); "
        "tracked Transfer logs in window: 121 (0x1a57) / 58 (0x5eb1) / 36 (0x3029); "
        "run-76 tokens quiet this run (0x0cda 0 wallets, 0xacc8 0 wallets); "
        "not previously signaled; not in Free Bacot snapshot; not in bridge (paid-only PCS tokens, per "
        "CORLA/GrokBot/ASI precedent)"),
    "buy_evidence": (
        "Sample PCS buys verified (receipt Transfer from pair + pair token0/token1 on-chain). "
        "Pairs verified on-chain: 0x3029 pair 0xebc7d74228a5fc5a4cc72c3ffe5ef4f52efdbbaa (token0 token, token1 WBNB 0xbb4c...); "
        "0x5eb1 pair 0xf5d5099b6175bff8363ccc20c640ffd93178cd07 (token0 token, token1 WBNB); "
        "0x1a57 pair 0x276bf984779b8a8993f31e678d57bdb2397e9121 (token0 token, token1 WBNB). "
        "27-wallet set window totals (all router activity, not per-token; recomputed from sent.json "
        "by literal selectors, matching token-verify.py): 213x buys (0xb6f9de95, total buy value "
        "27.7809 BNB) + 224x sells (0x791ac947) + 222x approve (0x095ea7b3) + 46x contract creations."),
    "linkage": ("NOT verified: the 27 wallets are BYTE-IDENTICAL to the run-63 CORLA / run-64 ASI / "
        "run-65 ASI quad-2 / run-66 two-token / run-68 two-token / run-69 one-token / run-70 "
        "five-token / run-71 six-token / run-72 three-token / run-73 four-token / run-74 four-token / run-75 three-token / run-76 two-token sets (verified set equality vs run-76: diff 0, overlap 27/27) "
        "and deployed 46 contracts in this window via 20 wallets, which suggests the same "
        "coordinated/machine operator, but no entity collapse is applied - counted per wallet with "
        "this note, as in run 60 GrokBot / run 63 CORLA precedents"),
    "auto_mint_block": ("Trigger >25% met numerically for all three (27 >= 14) but BLOCKED at "
        "guard (c): paid PCS tokens, no free-mint quota/path for the user wallet - buying would cost "
        "BNB, never a free mint; guard (a) website also unverified (empty name/symbol, no website "
        "evidence). No preview, no execution. Do not re-report the block unless a genuine free-mint "
        "path appears for these contracts."),
    "deployments_context": ("46 contract-creation txs by 20 of the 27 wallets in this window "
        "(0x97bd895f x5, 0x5b4beded x4, 0x64e893a4 x4, 0xdb2d83f9 x3, 0xca4e67bb x3, 0x2cc8192f x3, "
        "0xc0c84518 x3, 0xa952331e x3, 0xaa49e7fe x2, 0x3154f694 x2, 0x36239612 x2, 0xf9689b9d x2, "
        "0x1cce4ec5 x2, 0x9b519f5d52 x2, 0xc6219468 x1, 0x82c6085f x1, 0xcb08c02c x1, 0x4522e661 x1, "
        "0xfdec62fd x1, 0xc6591fde x1), all status 1; "
        "all 46 created addresses READ from receipts this run (saved in run77-deployments.json) and NONE is any of "
        "the three new tokens - the new tokens were first bought via PCS pairs, not "
        "deployed in-window by a tracked wallet; token identity (name/symbol) of the 46 created "
        "contracts was NOT checked, so whether any of them is a future machine token is UNVERIFIED"),
}
s["paid_trend_run77"] = {
    "note": "Aggregate only, NOT a buy recommendation. THREE NEW paid-only signals (27 wallets each - see paid_signal_run77); all other tokens far below threshold. ZERO mint-pattern txs this run (AFeng tracker mint did NOT repeat).",
    "max_wallets_per_token": 27,
    "distribution": "47 paid tokens: 27 wallets x3 (NEW 0x3029.../0x5eb1.../0x1a57...), 3 wallets x18, 2 wallets x12, 1 wallet x14 (all others ...7777-suffixed churn tokens)",
    "other_paid_activity": [
        {"pattern": "AFeng 15 sent txs: 9 to sale 0x1de460f363af910f51726def188f9004276bf4bc selector 0x4d819a2a (5 value 0, 0.075/0.5/1.2/3.5 BNB) - NO mint log in any; 5 approves; 1 transfer value 0", "wallet": "0xbf004bff64725914ee36d03b87d6965b0ced4903"},
        {"pattern": "future1001.ai 0 txs; 0x2325... 0 txs; 0x8e96... 0 txs", "wallet": "0x355ea9e542b36c645a2dee63b9df079ccb9bf3db / 0x2325f175975abdbcde555c79cc8e63381d28551b / 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6"},
        {"pattern": "4 status-0 receipts, all failed PCS sells 0x791ac947 by machine wallets (0xdb2d83f907 x2, 0xa952331ea4 x2)", "wallet": "machine wallets"},
    ],
    "deployments": "46 contract creations in window, all by 20 wallets of the 27-wallet machine set (see paid_signal_run77 deployments_context)",
    "future1001": "0 tx this run (0x355ea9e542b36c645a2dee63b9df079ccb9bf3db)",
}
s["inbound_log_leg_run77"] = {
    "contracts": n_contracts,
    "total_logs": n_logs,
    "hits": n_hits,
    "failed": n_failed,
    "failed_contracts": [f["contract"] for f in ia["failed"] + ib["failed"]],
    "note": (f"Ankr getLogs address-filtered per contract, window 131974332-131986346, parts a "
             f"(0-400, {ia['total_logs']} logs, {len(ia['hits'])} hits, {len(ia['failed'])} failed, {len(ia['truncated'])} truncated) "
             f"+ b (400-{n_contracts}, {ib['total_logs']} logs, {len(ib['hits'])} hits, {len(ib['failed'])} failed, {len(ib['truncated'])} truncated). "
             f"{n_hits} hits - 0 NEW inbound-only mints. "
             f"Truncated {len(trunc)} (all topic-filtered to 0 logs). "
             f"Failed {n_failed} - none, window FULLY CLOSED, no retry needed next run. "
             f"Run-76 retry this run: 2/2 contracts read OK, {rt['total_logs']} logs, 0 hits - run-76 window FULLY CLOSED. "
             "DYOR 0x8695... in set (via snapshot), 0 hits. No residual open from run 76. CORLA 0x4a9c + 4 run-64 ASI + 4 run-65 ASI quad-2 + the 2 run-66 tokens + the 2 run-68 tokens + the run-69 token + the 5 run-70 tokens + the 6 run-71 tokens + the 3 run-72 tokens + the 4 run-73 tokens + the 4 run-74 tokens + the 3 run-75 tokens + the 2 run-76 tokens + GrokBot 0xfcd0... + the 3 new run-77 tokens not in inbound set (PCS tokens; sent-pass covered). New contracts deployed this hour (46, all "
             "addresses read, none is any of the 3 new tokens) are not in the inbound set - their token "
             "identity (name/symbol) is UNVERIFIED."),
}
sp = s.setdefault("signaled_projects_over_20pct", [])
for new_sig in [
    "Unnamed token (name/symbol empty) 0x302941695afa1d83d648851b0898e39c63db7777 (paid-only, run-77)",
    "Unnamed token (name/symbol empty) 0x5eb157a3872c019f36989830a26e93ade0d97777 (paid-only, run-77)",
    "Unnamed token (name/symbol empty) 0x1a573d9c3baf15072773b2077d08176335a07777 (paid-only, run-77)",
]:
    if new_sig not in sp:
        sp.append(new_sig)
json.dump(s, open(P, "w"), indent=1)
print("state updated: run", s["last_run"]["run"])
print(f"inbound: contracts={n_contracts} logs={n_logs} hits={n_hits} failed={n_failed}")
print("paid_signal_run77 + paid_trend_run77 + inbound_log_leg_run77 written; signaled list now", len(sp))
txs = set(); entries = 0
for f in s["reported_findings"]:
    for m in f.get("mints", []):
        entries += 1
        if m.get("tx"):
            txs.add(m["tx"].lower())
print("reported_findings mint entries:", entries, "unique txs:", len(txs))
