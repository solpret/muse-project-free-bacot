#!/usr/bin/env python3
"""Run 75 state update (read-only job bookkeeping; no chain writes).

Completes run 75 (window 131955236-131963291), whose sent/receipts/paid/
token-verify/deployments passes are all done and whose inbound leg ran in
full (a 0-400 + b 400-1004).
"""
import json
import shutil
from pathlib import Path

P = "/home/hatch/workspace/narrative-pulse/tracked-wallet-mint-scan-state.json"
D = Path("/home/hatch/workspace/narrative-pulse/scan-runs")

shutil.copy(P, str(P) + ".bak-run75-pre")
s = json.load(open(P))
ia = json.load(open(D / "run75-inbound-a.json"))
ib = json.load(open(D / "run75-inbound-b.json"))
n_contracts = ia["contracts_checked"] + ib["contracts_checked"]
n_logs = ia["total_logs"] + ib["total_logs"]
n_hits = len(ia["hits"]) + len(ib["hits"])
n_failed = len(ia["failed"]) + len(ib["failed"])
trunc = ia["truncated"] + ib["truncated"]
print(f"inbound totals: contracts={n_contracts} logs={n_logs} hits={n_hits} failed={n_failed} truncated={len(trunc)}")
print(f"failed contracts: {[f['contract'] for f in ia['failed'] + ib['failed']]}")

s["last_run"] = {
    "run": 75,
    "block_start": 131955236,
    "block_end": 131963291,
    "window_wib": "2026-11-06 12:46:55 - 13:47:18 WIB; sent-pass in-window txs 930, 1 mint-pattern tx (KNOWN repeat, see method_note)",
    "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set)",
    "method_note": (
        "Sent pass Ankr ankr_getTransactionsByAddress via module (55/55, 0 failed; "
        "930 txs, 35 wallets active). Receipts via fast_rpc batch (6, ~4s pause) for 608 "
        "non-approve candidates: 601 status 1, 7 status 0 (all failed PCS sells 0x791ac947 by machine wallets: "
        "0x3bff1a59... by 0xdb2d83f907 13:40:02 WIB, 0xbde77cff... by 0xc621946845 13:41:06 WIB, "
        "0xcfbae672... by 0xc621946845 13:19:32 WIB, 0x00d002bb... by 0xa952331ea4 13:20:38 WIB, "
        "0xd7f83e86... by 0xa952331ea4 12:58:35 WIB, 0xb5eefbbe... by 0x92bc32975b 13:20:41 WIB, "
        "0x4ba9775a... by 0xfdec62fde1 13:01:15 WIB), 0 null, 1 mint-pattern tx. "
        "MINT tx 0x23cd8740876e4f42436622c983ba289be96131eade71276f81fa7412acab6241 (AFeng 0xbf004bff..., "
        "to sale 0x1de460f363af910f51726def188f9004276bf4bc, selector 0x4d819a2a, value 0.15 BNB, status 1, "
        "block 131960962, 13:29:50 WIB): Transfer from zero on 0x636fdfa9bc3db42c690c09e87b9017d05b36c743 "
        "to AFeng, 480,516,374,385.097 tokens (raw 480516374385097375327260362464, decimals 18) - KNOWN REPEAT of the "
        "run-70 finding (tx 0x5f560493..., same wallet/sale/selector/value/contract, 1,024,207,770,370.44 tokens), "
        "already in bridge + Free Bacot snapshot; NOT a new finding, NOT re-reported as new, NOT a signal (1 entity). "
        "AFeng's second call to the same sale 0x1f75d6fd2e3a... (13:23:39 WIB, block 131960139, same selector/value 0.15 BNB, "
        "status 1, 28 logs) has NO mint log - not a mint-pattern tx. "
        f"Inbound leg per 2026-11-03 12:02 amendment: Ankr getLogs address-filtered per contract, "
        f"{n_contracts} contracts, {n_logs} logs, {n_hits} hit(s), {n_failed} failed, run as a "
        f"(0-400, {ia['total_logs']} logs, {len(ia['hits'])} hit, {len(ia['failed'])} failed, {len(ia['truncated'])} truncated) "
        f"+ b (400-{n_contracts}, {ib['total_logs']} logs, {len(ib['hits'])} hits, {len(ib['failed'])} failed, {len(ib['truncated'])} truncated). "
        f"Hit = the same known AFeng mint above (contract 0x636f..., tx 0x23cd8740..., block 131960962) - inbound confirmation of the sent-pass finding, NOT a new finding. "
        f"Failed: {[f['contract'] for f in ia['failed'] + ib['failed']]} - retry run 76 on the same window (amendment 12:02); window NOT fully closed for those 2 contracts only. "
        f"Truncated {len(trunc)} (all topic-filtered; 0x636f...'s filtered query returned the hit above). "
        "DYOR: contract 0x86956bc830eb62110820ae79164bef61c7e31936 in set (via snapshot), 0 hits - "
        "no tracked wallet minted DYOR in this window. "
        "CORLA 0x4a9c499574ea003846e81522d59aa4c27ca47777, the 4 run-64 ASI contracts, the 4 run-65 "
        "ASI quad-2 contracts, the 2 run-66 tokens, the 2 run-68 tokens, the run-69 token 0x4d15... "
        "the 5 run-70 tokens, the 6 run-71 tokens, the 3 run-72 tokens, the 4 run-73 tokens, the 4 run-74 tokens, and GrokBot 0xfcd04501ebaddcda73095a75e078a8e5292f7777 are NOT in the "
        "inbound set (PCS tokens; all their activity was wallet-sent txs covered by the sent pass). "
        "The 3 new run-75 paid tokens are likewise NOT in the inbound set - sent-pass covered. "
        "52 contract creations in window (all by 14 wallets of the 27-wallet machine set, all status 1; "
        "none is any of the 3 new tokens). "
        "No preview/mint/sign/login/purchase by this job. "
        "INFRA NOTES: (1) The receipts job was killed by a service restart at 60/608 and resumed from the partial file (60 receipts kept, 548 remaining) - no data lost. "
        "(2) fast_rpc transient unreadable reads this run (pair token0()/token1() 0x7cd86c00... for token 0x167b... - 'all endpoints failed', retried once, still failed) recorded as unreadable/transient, NOT as empty/zero. "
        "(3) Ankr getLogs slow stretches again in inbound-a (ranges 50-100 and 200-250 each took several minutes with no progress line; 0 failures in the end for those ranges - slow, not stuck)."
    ),
}
s["next_run_note"] = (
    "Next run sent-tx window starts from block 131963292. Dedupe new mints against all tx hashes "
    "in reported_findings (runs 1-41: 219 txs; run 70 added 1 new finding tx (AFeng 0x5f560493...); "
    "run 71 added 1 new finding tx (0x2325 0xa20c70c1...); run 72 added 0; run 73 added 0; run 74 added 0; run 75 added 0, total 221). "
    "Run-75 mint tx 0x23cd8740... (AFeng, tracker 0x636f..., 0.15 BNB) is a KNOWN REPEAT of the run-70 finding - do not report as new if it repeats again. "
    "Paid-only signals run 63 "
    "(CORLA 0x4a9c), run 64 (4 ASI), run 65 (4 ASI quad-2), run 66 (tokens 0x19b7.../0x540d...), run 68 "
    "(tokens 0xf3cc.../0xe7e2...), run 69 (token 0x4d15...), run 70 (FIVE tokens "
    "0x4df7.../0xae06.../0x2516.../0x1247.../0x8e0d...), run 71 (SIX tokens "
    "0xe51b.../0xc2e1.../0x5785.../0xfff4.../0xe4c9.../0x25b4...), run 72 (THREE tokens "
    "0x26ef.../0x7145.../0xdfb3...), run 73 (FOUR tokens 0x4bd1.../0x1d9f.../0xe0f0... at 27 wallets + "
    "0x198c... at 21 wallets), run 74 (FOUR tokens 0xe4e0.../0x4d2e.../0xaf84... at 27 wallets + "
    "0x73c9... at 26 wallets), run 75 (THREE tokens 0x167b.../0x5205.../0x4f6d... at 27 wallets each) auto-mint BLOCKED at guard (c) "
    "- do not re-signal or re-report the block unless a new mint/buy fact appears for those contracts "
    "(e.g. a genuine free-mint path). Paid fact: run75 max 27 wallets/token (THREE new unnamed tokens "
    "at 27 wallets each, same byte-identical 27-wallet machine set as runs 63-74 - machine "
    "rotated again: run-74 four tokens -> quiet for all four (0 wallets) -> these three tokens; "
    "the other 26 paid tokens max 3 wallets each (13 at 3, 5 at 2, 8 at 1 - usual ...7777 churn); "
    "GrokBot 0xfcd0... absent (0 wallets) this run - 16th consecutive quiet run (59, 61-75) after the run-60 burst; CORLA-97af 0 wallets; CORLA 0x4a9c 0 wallets; all "
    "four run-64 ASI contracts 0 wallets; all four run-65 ASI quad-2 contracts 0 wallets; both run-66 "
    "tokens 0 wallets; both run-68 tokens 0 wallets; run-69 token 0x4d15 0 wallets; all five run-70 "
    "tokens 0 wallets; all six run-71 tokens 0 wallets; all three run-72 tokens 0 wallets; all four "
    "run-73 tokens 0 wallets (incl. 0x198c... which still had 18 wallets in run 74); all four run-74 tokens 0 wallets. "
    "Inbound retry next run: 2 contracts failed this run - 0x259b5da3f44a44c89bca5ee2297582c41c758d0f (part a) and 0xa9b060551764f3213a64a449fd3d06db3b8cbcff (part b), both Ankr 'Remote end closed connection without response' - retry on window 131955236-131963291. "
    "AFeng 2 txs this run (both to sale 0x1de4..., 0.15 BNB each; 1 mint-pattern, 1 without mint log - see method_note); future1001.ai 0 txs; 0x2325... 0 txs; 0x8e96... 2 txs. "
    "Same-owner factory groups now also include 0x293f and 0x1103 (proven 2026-11-06 ~01:14 WIB, AGENTS.md) alongside the groups listed in the body."
)
s["paid_signal_run75"] = {
    "note": ("NEW paid-only signal (NOT a buy recommendation, NOT executable Free Bacot, NOT an "
             "auto-mint trigger by itself). Same-machine warning: THREE distinct NEW contracts, all bought by the SAME byte-identical 27-wallet set "
             "(27/27, pairwise diffs 0/0/0, and diff 0 vs the run-74 27-set: overlap 27/27) - the set that also bought CORLA (run 63), ASI quad-1 (run 64), "
             "ASI quad-2 (run 65), the two run-66 tokens, the two run-68 tokens, the run-69 token, the "
             "five run-70 tokens, the six run-71 tokens, the three run-72 tokens, the four run-73 tokens and the four run-74 tokens - the machine rotated again: CORLA (63) -> "
             "ASI quad-1 (64) -> ASI quad-2 (65) -> two unnamed tokens (66) -> quiet (67) -> two new tokens (68) -> one token (69) -> five tokens (70) -> six tokens (71) -> three tokens (72) -> "
             "four tokens (73) -> four tokens (74) -> these three tokens (75). The three are NOT one project - 3 different contracts, never merged."),
    "project": "NEW paid tokens, same 27-wallet machine set (unnamed)",
    "contracts": [
        "0x167bdc3f4e9305d454d9ef083ef44fe613267777",
        "0x520562aef97bd519dc36aec7e45babe2c6487777",
        "0x4f6deab013d6444ef1e348a8870ca673a15b7777",
    ],
    "name_symbol_onchain": ("name() and symbol() both return EMPTY strings on-chain for all three "
        "(verified via fast_rpc eth_call decode); decimals 18 for all three; totalSupply 1e27 "
        "(1,000,000,000,000,000,000,000,000,000) for all three; "
        "owner() 0x0 for all three; "
        "tokenURI not attempted (no name/symbol identity to resolve, paid PCS tokens - same treatment as run-66/run-68/run-69/run-70/run-71/run-72/run-73/run-74 tokens)"),
    "participation": ("3 tokens at 27 / 55 wallets (49.1%); "
        "all three are 0 wallets in run 74 (new this run); "
        "first tracked buys (selector 0xb6f9de95, wallet 0xcb08c02c0a, ~9,092,300 tokens, 0.000114 BNB): "
        "0x4f6d 12:55:49 WIB (tx 0xbc36662bdcf27bc3129b9a023d4c8c12cf5901bd6af6e2da398065ef542bdfc0, block 131956428, pair 0x7c2b6e8b...), "
        "0x5205 13:17:49 WIB (tx 0x50597da4944492094c8b2f754526938f30770baa9049993b8113d9ced60f297a, block 131959361, pair 0x544d14bd...); "
        "0x167b first tracked buy NOT VERIFIED: its first tracked Transfer (block 131962215, tx 0x36b7f0c722d039b71c6146cea9df23b13ab38b4724671e971c3cd77aa3977ec4, "
        "from pair 0x7cd86c00..., ~98,063.88 tokens) is NOT a tracked-wallet sent tx (tx confirmed absent from sent.json) - small external transfer to a tracked wallet, not a tracked buy; "
        "tracked Transfer logs in window: 58 / 58 / 60 respectively; "
        "all four run-74 tokens 0 wallets this run (machine rotated fully to these three); "
        "not previously signaled; not in Free Bacot snapshot; not in bridge (paid-only PCS tokens, per "
        "CORLA/GrokBot/ASI precedent)"),
    "buy_evidence": (
        "Sample PCS buys verified (receipt Transfer from pair + pair token0/token1 on-chain where readable). "
        "Pairs verified on-chain: 0x5205 pair 0x544d14bd29cde53e81456bc0cec62a053ee3d0c8 (token0 token, token1 WBNB 0xbb4c...); "
        "0x4f6d pair 0x7c2b6e8b5c1657b860b386be61cb770785fd6d0e (token0 token, token1 WBNB); "
        "0x167b pair token0/token1 UNREADABLE transiently (fast_rpc 'all endpoints failed', retried once, still failed) - pair address "
        "0x7cd86c007f6a2a6ea6185376730af3b110dd1883 identified from Transfer logs only. "
        "27-wallet set window totals (all router activity, not per-token; recomputed from sent.json "
        "by literal selectors, matching token-verify.py): 172x buys (0xb6f9de95, total buy value "
        "32.8182 BNB) + 274x sells (0x791ac947) + 268x approve (0x095ea7b3) + 52x contract creations."),
    "linkage": ("NOT verified: the 27 wallets are BYTE-IDENTICAL to the run-63 CORLA / run-64 ASI / "
        "run-65 ASI quad-2 / run-66 two-token / run-68 two-token / run-69 one-token / run-70 "
        "five-token / run-71 six-token / run-72 three-token / run-73 four-token / run-74 four-token sets (verified set equality vs run-74: diff 0, overlap 27/27) "
        "and deployed 52 contracts in this window via 14 wallets, which suggests the same "
        "coordinated/machine operator, but no entity collapse is applied - counted per wallet with "
        "this note, as in run 60 GrokBot / run 63 CORLA precedents"),
    "auto_mint_block": ("Trigger >25% met numerically for all three (27 >= 14) but BLOCKED at "
        "guard (c): paid PCS tokens, no free-mint quota/path for the user wallet - buying would cost "
        "BNB, never a free mint; guard (a) website also unverified (empty name/symbol, no website "
        "evidence). No preview, no execution. Do not re-report the block unless a genuine free-mint "
        "path appears for these contracts."),
    "deployments_context": ("52 contract-creation txs by 14 of the 27 wallets in this window "
        "(0xdb2d83f9 x6, 0xc6219468 x6, 0xaa49e7fe x3, 0x3154f694 x4, 0xca4e67bb x4, "
        "0x5b4beded x3, 0xf9689b9d x4, 0x2cc8192f x4, 0x1cce4ec5 x4, "
        "0xc0c84518 x3, 0xa952331e x3, 0x92bc3297 x3, 0xfdec62fd x1, 0x97bd895f x4), all status 1; "
        "all 52 created addresses READ from receipts this run (saved in run75-deployments.json) and NONE is any of "
        "the three new tokens - the new tokens were first bought via PCS pairs, not "
        "deployed in-window by a tracked wallet; token identity (name/symbol) of the 52 created "
        "contracts was NOT checked, so whether any of them is a future machine token is UNVERIFIED"),
}
s["paid_trend_run75"] = {
    "note": "Aggregate only, NOT a buy recommendation. THREE NEW paid-only signals (3 at 27 wallets - see paid_signal_run75); all other tokens far below threshold. ONE known-repeat mint-pattern tx (AFeng tracker, already reported run 70 - NOT new).",
    "max_wallets_per_token": 27,
    "distribution": "29 paid tokens: 27 wallets x3 (NEW unnamed machine tokens), 3 wallets x13, 2 wallets x5, 1 wallet x8 (all others ...7777-suffixed churn tokens)",
    "other_paid_activity": [
        {"pattern": "AFeng 2 txs: 2x sale 0x1de460f363af910f51726def188f9004276bf4bc selector 0x4d819a2a, 0.15 BNB each (13:23:39 tx 0x1f75d6fd..., 28 logs, NO mint log; 13:29:50 tx 0x23cd8740..., 19 logs, 1 mint log on tracker 0x636f... - KNOWN REPEAT of run-70 finding, not new)", "wallet": "0xbf004bff64725914ee36d03b87d6965b0ced4903"},
        {"pattern": "future1001.ai 0 txs; 0x2325... 0 txs", "wallet": "0x355ea9e542b36c645a2dee63b9df079ccb9bf3db / 0x2325f175975abdbcde555c79cc8e63381d28551b"},
        {"pattern": "0x8e96... 2 txs: 1 approve 0xdb5df5ea to 0xf8ec... 13:38:32 WIB + 1 call 0xef7ec2e7 (0xcd1f28ba) to 0xe2ce... 13:38:29 WIB", "wallet": "0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6"},
        {"pattern": "7 status-0 receipts: all failed PCS sells (0x791ac947) by machine wallets", "wallet": "machine wallets"},
    ],
    "deployments": "52 contract creations in window, all by 14 wallets of the 27-wallet machine set (see paid_signal_run75 deployments_context)",
    "future1001": "0 tx this run (0x355ea9e542b36c645a2dee63b9df079ccb9bf3db)",
}
s["inbound_log_leg_run75"] = {
    "contracts": n_contracts,
    "total_logs": n_logs,
    "hits": n_hits,
    "failed": n_failed,
    "failed_contracts": [f["contract"] for f in ia["failed"] + ib["failed"]],
    "note": (f"Ankr getLogs address-filtered per contract, window 131955236-131963291, parts a "
             f"(0-400, {ia['total_logs']} logs, {len(ia['hits'])} hit, {len(ia['failed'])} failed, {len(ia['truncated'])} truncated) "
             f"+ b (400-{n_contracts}, {ib['total_logs']} logs, {len(ib['hits'])} hits, {len(ib['failed'])} failed, {len(ib['truncated'])} truncated). "
             f"{n_hits} hit - the known AFeng mint (contract 0x636f..., tx 0x23cd8740..., block 131960962), already reported run 70 - 0 NEW inbound-only mints. "
             f"Truncated {len(trunc)} (all topic-filtered). "
             f"Failed {n_failed}: {[f['contract'] for f in ia['failed'] + ib['failed']]} - retry run 76 on the same window. "
             "DYOR 0x8695... in set (via snapshot), 0 hits. No residual open from run 74 (its window fully closed, 0 failed). CORLA 0x4a9c + 4 run-64 ASI + 4 run-65 ASI quad-2 + the 2 run-66 tokens + the 2 run-68 tokens + the run-69 token + the 5 run-70 tokens + the 6 run-71 tokens + the 3 run-72 tokens + the 4 run-73 tokens + the 4 run-74 tokens + GrokBot 0xfcd0... + the 3 new run-75 tokens not in inbound set (PCS tokens; sent-pass covered). New contracts deployed this hour (52, all "
             "addresses read, none is any of the 3 new tokens) are not in the inbound set - their token "
             "identity (name/symbol) is UNVERIFIED."),
}
sp = s.setdefault("signaled_projects_over_20pct", [])
for new_sig in [
    "Unnamed token (name/symbol empty) 0x167bdc3f4e9305d454d9ef083ef44fe613267777 (paid-only, run-75)",
    "Unnamed token (name/symbol empty) 0x520562aef97bd519dc36aec7e45babe2c6487777 (paid-only, run-75)",
    "Unnamed token (name/symbol empty) 0x4f6deab013d6444ef1e348a8870ca673a15b7777 (paid-only, run-75)",
]:
    if new_sig not in sp:
        sp.append(new_sig)
json.dump(s, open(P, "w"), indent=1)
print("state updated: run", s["last_run"]["run"])
print(f"inbound: contracts={n_contracts} logs={n_logs} hits={n_hits} failed={n_failed}")
print("paid_signal_run75 + paid_trend_run75 + inbound_log_leg_run75 written; signaled list now", len(sp))
print("reported_findings total txs now:", sum(len(f.get('mints', [])) for f in s['reported_findings']))
