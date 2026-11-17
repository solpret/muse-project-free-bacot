#!/usr/bin/env python3
"""Run 76 state update (read-only job bookkeeping; no chain writes).

Completes run 76 (window 131963292-131974331), whose sent/receipts/paid/
token-verify/deployments passes are all done and whose inbound leg ran in
full (a 0-400 + b 400-1010) plus the retry of run 75's 2 failed contracts.
"""
import json
import shutil
from pathlib import Path

P = "/home/hatch/workspace/narrative-pulse/tracked-wallet-mint-scan-state.json"
D = Path("/home/hatch/workspace/narrative-pulse/scan-runs")

shutil.copy(P, str(P) + ".bak-run76-pre")
s = json.load(open(P))
ia = json.load(open(D / "run76-inbound-a.json"))
ib = json.load(open(D / "run76-inbound-b.json"))
rt = json.load(open(D / "run76-inbound-retry.json"))
n_contracts = ia["contracts_checked"] + ib["contracts_checked"]
n_logs = ia["total_logs"] + ib["total_logs"]
n_hits = len(ia["hits"]) + len(ib["hits"])
n_failed = len(ia["failed"]) + len(ib["failed"])
trunc = ia["truncated"] + ib["truncated"]
print(f"inbound totals: contracts={n_contracts} logs={n_logs} hits={n_hits} failed={n_failed} truncated={len(trunc)}")
print(f"failed contracts: {[f['contract'] for f in ia['failed'] + ib['failed']]}")
print(f"run-75 retry: contracts={rt['contracts_checked']} logs={rt['total_logs']} hits={len(rt['hits'])} failed={len(rt['failed'])}")

s["last_run"] = {
    "run": 76,
    "block_start": 131963292,
    "block_end": 131974331,
    "window_wib": "2026-11-06 13:47:28 - 15:10:07 WIB; sent-pass in-window txs 883, 0 mint-pattern txs",
    "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set)",
    "method_note": (
        "Sent pass Ankr ankr_getTransactionsByAddress via module (55/55, 0 failed; "
        "883 txs, 36 wallets active). Receipts via fast_rpc batch (6, ~4s pause) for 568 "
        "non-approve candidates: 560 status 1, 8 status 0, 0 null, 0 mint-pattern txs. "
        "Status-0 detail: 2x 0x8e96... 0xef7ec2e7 calls to 0xe2ce... (13:53:32 + 13:53:34 WIB, "
        "txs 0xd665adbcec66... + 0x520d9a07880e...); 5x failed PCS sells 0x791ac947 by machine "
        "wallets (0xa9d59492... by 0xdb2d83f907 14:20:00 WIB, 0x44811249... by 0xdb2d83f907 14:00:40 WIB, "
        "0x5d70093d... by 0xc621946845 14:25:37 WIB, 0x8be9e810... by 0xa952331ea4 14:02:47 WIB, "
        "0xc5b8408b... by 0x9b519f5d52 14:20:49 WIB); 1x failed PCS buy 0xb6f9de95 by 0xe9ed24db10 "
        "(0x891f5153..., 14:00:27 WIB, value 0.0142 BNB) - this failed buy is why 0xe9ed24db is in "
        "the 27-set for 0x0cda but missing from the 26-set for 0xacc8. "
        "AFeng 105 sent txs (69 non-approve receipts + 36 approves): all 69 to sale "
        "0x1de460f363af910f51726def188f9004276bf4bc selector 0x4d819a2a - 36 value 0, 33 with BNB "
        "0.075-7.357 (incl. 0.15 x2, 0.5, 0.6, 1.75, 2.3, 3.5, 7.357) - NO mint log in any receipt "
        "(no Transfer from zero to AFeng), so 0 mint-pattern txs this run; the run-70 AFeng tracker "
        "mint (0x636f...) did NOT repeat. Plus 1 plain BNB transfer 0.8125 BNB to 0x28ff6b5e... "
        "(13:49:00 WIB, 0 logs, not a mint). future1001.ai 0 txs; 0x2325... 0 txs; 0x8e96... 4 txs "
        "(2 status-0 above + 1 approve + 1 call 0xef7ec2e7 status 1). "
        f"Inbound leg per 2026-11-03 12:02 amendment: Ankr getLogs address-filtered per contract, "
        f"{n_contracts} contracts, {n_logs} logs, {n_hits} hit(s), {n_failed} failed, run as a "
        f"(0-400, {ia['total_logs']} logs, {len(ia['hits'])} hits, {len(ia['failed'])} failed, {len(ia['truncated'])} truncated) "
        f"+ b (400-{n_contracts}, {ib['total_logs']} logs, {len(ib['hits'])} hits, {len(ib['failed'])} failed, {len(ib['truncated'])} truncated). "
        f"0 hits - NO inbound-only mints this run. "
        f"Failed: {[f['contract'] for f in ia['failed'] + ib['failed']]} - retry run 77 on the same window (amendment 12:02); window NOT fully closed for those 2 contracts only. "
        f"Truncated {len(trunc)} (all topic-filtered to 0 logs, incl. 0x636f... AFeng tracker, 0x1de4... AFeng sale, 0xaea143... VAULT CRACK). "
        f"Run-75 retry (2 contracts on window 131955236-131963291): {rt['total_logs']} logs, 0 hits, 0 failed - run-75 window now FULLY CLOSED. "
        "DYOR: contract 0x86956bc830eb62110820ae79164bef61c7e31936 in set (via snapshot), 0 hits - "
        "no tracked wallet minted DYOR in this window. "
        "CORLA 0x4a9c499574ea003846e81522d59aa4c27ca47777, the 4 run-64 ASI contracts, the 4 run-65 "
        "ASI quad-2 contracts, the 2 run-66 tokens, the 2 run-68 tokens, the run-69 token 0x4d15... "
        "the 5 run-70 tokens, the 6 run-71 tokens, the 3 run-72 tokens, the 4 run-73 tokens, the 4 run-74 tokens, "
        "the 3 run-75 tokens (0x5205 0 wallets, 0x4f6d 0 wallets; 0x167b residual 2 wallets only - "
        "0x3a39aa05... + 0xc194efe2...), and GrokBot 0xfcd04501ebaddcda73095a75e078a8e5292f7777 are NOT in the "
        "inbound set (PCS tokens; all their activity was wallet-sent txs covered by the sent pass). "
        "The 2 new run-76 paid tokens are likewise NOT in the inbound set - sent-pass covered. "
        "32 contract creations in window (all by 14 wallets of the 27-wallet machine set, all status 1; "
        "none is either of the 2 new tokens). "
        "No preview/mint/sign/login/purchase by this job. "
        "INFRA NOTES: (1) Inbound part b first attempt (nohup, detached) DIED at contract ~239/608 "
        "with no completion line - re-run as a tracked background exec completed 610/610, 0 failed "
        "(the connection-refused error on 0xa233c45f... in the killed attempt did NOT recur; that "
        "contract read fine in the re-run). (2) fast_rpc transient unreadable read again (pair "
        "token0() 0x1318dd45... for token 0x0cda... - 'all endpoints failed', recorded as "
        "unreadable/transient, NOT as empty/zero; token1 WBNB read fine). (3) Ankr getLogs slow "
        "stretches again in inbound-a (ranges 150-200 and 250-300 each several minutes with no "
        "progress line) and inbound-b (50-100, 150-200, 200-250) - slow, not stuck, 0 extra failures."
    ),
}
s["next_run_note"] = (
    "Next run sent-tx window starts from block 131974332. Dedupe new mints against all tx hashes "
    "in reported_findings (direct count this run: 221 unique tx hashes; the state note's 223 figure "
    "from run 75 does NOT match the direct count - 221 is the verified number, the 223 was an error). "
    "Run-75 mint tx 0x23cd8740... (AFeng, tracker 0x636f..., 0.15 BNB) is a KNOWN REPEAT of the run-70 finding - do not report as new if it repeats again. "
    "Paid-only signals run 63 "
    "(CORLA 0x4a9c), run 64 (4 ASI), run 65 (4 ASI quad-2), run 66 (tokens 0x19b7.../0x540d...), run 68 "
    "(tokens 0xf3cc.../0xe7e2...), run 69 (token 0x4d15...), run 70 (FIVE tokens "
    "0x4df7.../0xae06.../0x2516.../0x1247.../0x8e0d...), run 71 (SIX tokens "
    "0xe51b.../0xc2e1.../0x5785.../0xfff4.../0xe4c9.../0x25b4...), run 72 (THREE tokens "
    "0x26ef.../0x7145.../0xdfb3...), run 73 (FOUR tokens 0x4bd1.../0x1d9f.../0xe0f0... at 27 wallets + "
    "0x198c... at 21 wallets), run 74 (FOUR tokens 0xe4e0.../0x4d2e.../0xaf84... at 27 wallets + "
    "0x73c9... at 26 wallets), run 75 (THREE tokens 0x167b.../0x5205.../0x4f6d... at 27 wallets each), run 76 (TWO tokens "
    "0x0cda... at 27 wallets + 0xacc8... at 26 wallets) auto-mint BLOCKED at guard (c) "
    "- do not re-signal or re-report the block unless a new mint/buy fact appears for those contracts "
    "(e.g. a genuine free-mint path). Paid fact: run76 max 27 wallets/token (TWO new unnamed tokens, "
    "same byte-identical 27-wallet machine set as runs 63-75 - machine rotated again: run-75 three tokens -> "
    "quiet for two of them (0 wallets) + residual 2 wallets on 0x167b -> these two tokens; "
    "the other 55 paid tokens max 3 wallets each (13 at 3, 9 at 2, 33 at 1 - usual ...7777 churn); "
    "GrokBot 0xfcd0... absent (0 wallets) this run - 17th consecutive quiet run (59, 61-76) after the run-60 burst; CORLA-97af 0 wallets; CORLA 0x4a9c 0 wallets; all "
    "four run-64 ASI contracts 0 wallets; all four run-65 ASI quad-2 contracts 0 wallets; both run-66 "
    "tokens 0 wallets; both run-68 tokens 0 wallets; run-69 token 0x4d15 0 wallets; all five run-70 "
    "tokens 0 wallets; all six run-71 tokens 0 wallets; all three run-72 tokens 0 wallets; all four "
    "run-73 tokens 0 wallets; all four run-74 tokens 0 wallets; run-75 0x5205 0 wallets, 0x4f6d 0 wallets, "
    "0x167b 2 wallets (residual only). "
    "Inbound retry next run: 2 contracts failed this run - 0x3b3c00d4616a4a48c115b8e321aa6b983a2beb10 (part a) and 0x3b843b46cdfa173e947e1d662629933af1d94231 (part a), both Ankr 'Remote end closed connection without response' - retry on window 131963292-131974331. "
    "Run-75 window is now FULLY CLOSED (its 2 failed contracts retried OK this run, 0 hits). "
    "AFeng 105 sent txs this run (69 to sale 0x1de4... selector 0x4d819a2a, 36 value 0 + 33 BNB 0.075-7.357, NO mint log in any; 36 approves; 1 plain 0.8125 BNB transfer to 0x28ff...); future1001.ai 0 txs; 0x2325... 0 txs; 0x8e96... 4 txs. "
    "Same-owner factory groups now also include 0x293f and 0x1103 (proven 2026-11-06 ~01:14 WIB, AGENTS.md) alongside the groups listed in the body."
)
s["paid_signal_run76"] = {
    "note": ("NEW paid-only signal (NOT a buy recommendation, NOT executable Free Bacot, NOT an "
             "auto-mint trigger by itself). Same-machine warning: TWO distinct NEW contracts, bought by the SAME byte-identical 27-wallet set "
             "(27/27, diff 0 vs the run-75 27-set) - the set that also bought CORLA (run 63), ASI quad-1 (run 64), "
             "ASI quad-2 (run 65), the two run-66 tokens, the two run-68 tokens, the run-69 token, the "
             "five run-70 tokens, the six run-71 tokens, the three run-72 tokens, the four run-73 tokens, the four run-74 tokens and the three run-75 tokens - the machine rotated again: CORLA (63) -> "
             "ASI quad-1 (64) -> ASI quad-2 (65) -> two unnamed tokens (66) -> quiet (67) -> two new tokens (68) -> one token (69) -> five tokens (70) -> six tokens (71) -> three tokens (72) -> "
             "four tokens (73) -> four tokens (74) -> three tokens (75) -> these two tokens (76). The two are NOT one project - 2 different contracts, never merged."),
    "project": "NEW paid tokens, same 27-wallet machine set (unnamed)",
    "contracts": [
        "0x0cdadc486f579144ce220b6895d6f8a253187777",
        "0xacc8c1430cf30bc1cf8426bd854191def7d07777",
    ],
    "name_symbol_onchain": ("name() and symbol() both return EMPTY strings on-chain for both "
        "(verified via fast_rpc eth_call decode); decimals 18 for both; totalSupply 1e27 "
        "(1,000,000,000,000,000,000,000,000,000) for both; "
        "owner() 0x0 for both; "
        "tokenURI not attempted (no name/symbol identity to resolve, paid PCS tokens - same treatment as run-66/run-68/run-69/run-70/run-71/run-72/run-73/run-74/run-75 tokens)"),
    "participation": ("0x0cda at 27 / 55 wallets (49.1%), 0xacc8 at 26 / 55 wallets (47.3%); "
        "both are 0 wallets in run 75 (new this run); "
        "the 26-set is the 27-set minus 0xe9ed24db10 (whose buy of 0xacc8 FAILED status 0, tx 0x891f5153..., 14:00:27 WIB, 0.0142 BNB) - the only difference; "
        "first tracked buys (selector 0xb6f9de95, 0.000114 BNB each): "
        "0xacc8 14:00:01 WIB (tx 0xc9442c95d7752a74e581869e12d04b7d6274f0cf59c412f94379cd0bbb2e4890, block 131964987, wallet 0xcb08c02c0a, pair 0x1819ef59...), "
        "0x0cda 14:19:25 WIB (tx 0x318cf689d82953a41cc932e5c3eac123c9ba137fb844bf075e4547771a9f9aea, block 131967572, wallet 0x362396125a, pair 0x1318dd45...); "
        "tracked Transfer logs in window: 59 (0x0cda) / 55 (0xacc8); "
        "run-75 tokens quiet this run (0x5205 0 wallets, 0x4f6d 0 wallets, 0x167b residual 2 wallets); "
        "not previously signaled; not in Free Bacot snapshot; not in bridge (paid-only PCS tokens, per "
        "CORLA/GrokBot/ASI precedent)"),
    "buy_evidence": (
        "Sample PCS buys verified (receipt Transfer from pair + pair token0/token1 on-chain where readable). "
        "Pairs verified on-chain: 0xacc8 pair 0x1819ef59afef4f0b38c828244fd1e95350cb69c0 (token0 token, token1 WBNB 0xbb4c...); "
        "0x0cda pair 0x1318dd454226c13cc5b7eb276f1a826caa7dd08a (token0 UNREADABLE transiently - fast_rpc 'all endpoints failed', token1 WBNB). "
        "27-wallet set window totals (all router activity, not per-token; recomputed from sent.json "
        "by literal selectors, matching token-verify.py): 117x buys (0xb6f9de95, total buy value "
        "22.5594 BNB) + 218x sells (0x791ac947) + 213x approve (0x095ea7b3) + 32x contract creations."),
    "linkage": ("NOT verified: the 27 wallets are BYTE-IDENTICAL to the run-63 CORLA / run-64 ASI / "
        "run-65 ASI quad-2 / run-66 two-token / run-68 two-token / run-69 one-token / run-70 "
        "five-token / run-71 six-token / run-72 three-token / run-73 four-token / run-74 four-token / run-75 three-token sets (verified set equality vs run-75: diff 0, overlap 27/27) "
        "and deployed 32 contracts in this window via 14 wallets, which suggests the same "
        "coordinated/machine operator, but no entity collapse is applied - counted per wallet with "
        "this note, as in run 60 GrokBot / run 63 CORLA precedents"),
    "auto_mint_block": ("Trigger >25% met numerically for both (27 and 26 >= 14) but BLOCKED at "
        "guard (c): paid PCS tokens, no free-mint quota/path for the user wallet - buying would cost "
        "BNB, never a free mint; guard (a) website also unverified (empty name/symbol, no website "
        "evidence). No preview, no execution. Do not re-report the block unless a genuine free-mint "
        "path appears for these contracts."),
    "deployments_context": ("32 contract-creation txs by 14 of the 27 wallets in this window "
        "(0xc6219468 x5, 0x1cce4ec5 x4, 0xdb2d83f9 x3, 0x5b4beded x3, 0x3154f694 x2, 0xca4e67bb x2, "
        "0x36239612 x2, 0xf9689b9d x2, 0x2cc8192f x2, 0xc0c84518 x2, 0x97bd895f x2, 0xaa49e7fe x1, "
        "0xa952331e x1, 0x64e893a4 x1), all status 1; "
        "all 32 created addresses READ from receipts this run (saved in run76-deployments.json) and NONE is either of "
        "the two new tokens - the new tokens were first bought via PCS pairs, not "
        "deployed in-window by a tracked wallet; token identity (name/symbol) of the 32 created "
        "contracts was NOT checked, so whether any of them is a future machine token is UNVERIFIED"),
}
s["paid_trend_run76"] = {
    "note": "Aggregate only, NOT a buy recommendation. TWO NEW paid-only signals (27 + 26 wallets - see paid_signal_run76); all other tokens far below threshold. ZERO mint-pattern txs this run (AFeng tracker mint did NOT repeat).",
    "max_wallets_per_token": 27,
    "distribution": "57 paid tokens: 27 wallets x1 (NEW 0x0cda...), 26 wallets x1 (NEW 0xacc8...), 3 wallets x13, 2 wallets x9, 1 wallet x33 (all others ...7777-suffixed churn tokens)",
    "other_paid_activity": [
        {"pattern": "AFeng 105 sent txs: 69 to sale 0x1de460f363af910f51726def188f9004276bf4bc selector 0x4d819a2a (36 value 0, 33 BNB 0.075-7.357) - NO mint log in any; 36 approves; 1 plain 0.8125 BNB transfer to 0x28ff6b5e... 13:49:00 WIB, 0 logs", "wallet": "0xbf004bff64725914ee36d03b87d6965b0ced4903"},
        {"pattern": "future1001.ai 0 txs; 0x2325... 0 txs", "wallet": "0x355ea9e542b36c645a2dee63b9df079ccb9bf3db / 0x2325f175975abdbcde555c79cc8e63381d28551b"},
        {"pattern": "0x8e96... 4 txs: 2 status-0 0xef7ec2e7 calls to 0xe2ce... (13:53:32 + 13:53:34 WIB) + 1 approve + 1 call 0xef7ec2e7 status 1", "wallet": "0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6"},
        {"pattern": "8 status-0 receipts: 2x 0x8e96 0xef7ec2e7 + 5x failed PCS sells 0x791ac947 + 1x failed PCS buy 0xb6f9de95 by 0xe9ed24db10 (0x891f5153..., 14:00:27 WIB)", "wallet": "machine wallets + 0x8e96..."},
    ],
    "deployments": "32 contract creations in window, all by 14 wallets of the 27-wallet machine set (see paid_signal_run76 deployments_context)",
    "future1001": "0 tx this run (0x355ea9e542b36c645a2dee63b9df079ccb9bf3db)",
}
s["inbound_log_leg_run76"] = {
    "contracts": n_contracts,
    "total_logs": n_logs,
    "hits": n_hits,
    "failed": n_failed,
    "failed_contracts": [f["contract"] for f in ia["failed"] + ib["failed"]],
    "note": (f"Ankr getLogs address-filtered per contract, window 131963292-131974331, parts a "
             f"(0-400, {ia['total_logs']} logs, {len(ia['hits'])} hits, {len(ia['failed'])} failed, {len(ia['truncated'])} truncated) "
             f"+ b (400-{n_contracts}, {ib['total_logs']} logs, {len(ib['hits'])} hits, {len(ib['failed'])} failed, {len(ib['truncated'])} truncated). "
             f"{n_hits} hits - 0 NEW inbound-only mints. "
             f"Truncated {len(trunc)} (all topic-filtered to 0 logs). "
             f"Failed {n_failed}: {[f['contract'] for f in ia['failed'] + ib['failed']]} - retry run 77 on the same window. "
             f"Run-75 retry this run: 2/2 contracts read OK, {rt['total_logs']} logs, 0 hits - run-75 window FULLY CLOSED. "
             "DYOR 0x8695... in set (via snapshot), 0 hits. No residual open from run 75. CORLA 0x4a9c + 4 run-64 ASI + 4 run-65 ASI quad-2 + the 2 run-66 tokens + the 2 run-68 tokens + the run-69 token + the 5 run-70 tokens + the 6 run-71 tokens + the 3 run-72 tokens + the 4 run-73 tokens + the 4 run-74 tokens + the 3 run-75 tokens + GrokBot 0xfcd0... + the 2 new run-76 tokens not in inbound set (PCS tokens; sent-pass covered). New contracts deployed this hour (32, all "
             "addresses read, none is either of the 2 new tokens) are not in the inbound set - their token "
             "identity (name/symbol) is UNVERIFIED."),
}
sp = s.setdefault("signaled_projects_over_20pct", [])
for new_sig in [
    "Unnamed token (name/symbol empty) 0x0cdadc486f579144ce220b6895d6f8a253187777 (paid-only, run-76)",
    "Unnamed token (name/symbol empty) 0xacc8c1430cf30bc1cf8426bd854191def7d07777 (paid-only, run-76)",
]:
    if new_sig not in sp:
        sp.append(new_sig)
json.dump(s, open(P, "w"), indent=1)
print("state updated: run", s["last_run"]["run"])
print(f"inbound: contracts={n_contracts} logs={n_logs} hits={n_hits} failed={n_failed}")
print("paid_signal_run76 + paid_trend_run76 + inbound_log_leg_run76 written; signaled list now", len(sp))
print("reported_findings total txs now:", sum(len(f.get('mints', [])) for f in s['reported_findings']))
