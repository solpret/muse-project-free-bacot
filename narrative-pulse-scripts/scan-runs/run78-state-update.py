#!/usr/bin/env python3
"""Run 78 state update (read-only job bookkeeping; no chain writes).

Completes run 78 (window 131986347-131992565), whose sent/receipts/paid/
token-verify/deployments passes are all done and whose inbound leg ran in
full (a 0-400 + b 400-1016).
"""
import json
import shutil
from pathlib import Path

P = "/home/hatch/workspace/narrative-pulse/tracked-wallet-mint-scan-state.json"
D = Path("/home/hatch/workspace/narrative-pulse/scan-runs")

shutil.copy(P, str(P) + ".bak-run78-pre")
s = json.load(open(P))
ia = json.load(open(D / "run78-inbound-a.json"))
ib = json.load(open(D / "run78-inbound-b.json"))
ig = json.load(open(D / "run78-inbound-gap.json"))
n_contracts = ia["contracts_checked"] + ib["contracts_checked"] + ig["contracts_checked"]
n_logs = ia["total_logs"] + ib["total_logs"] + ig["total_logs"]
n_hits = len(ia["hits"]) + len(ib["hits"]) + len(ig["hits"])
n_failed = len(ia["failed"]) + len(ib["failed"]) + len(ig["failed"])
trunc = ia["truncated"] + ib["truncated"] + ig["truncated"]
print(f"inbound totals: contracts={n_contracts} logs={n_logs} hits={n_hits} failed={n_failed} truncated={len(trunc)}")
print(f"failed contracts: {[f['contract'] for f in ia['failed'] + ib['failed']]}")

s["last_run"] = {
    "run": 78,
    "block_start": 131986347,
    "block_end": 131992565,
    "window_wib": "2026-11-06 16:40:18 - 17:26:53 WIB; sent-pass in-window txs 807, 0 mint-pattern txs",
    "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set)",
    "method_note": (
        "Sent pass Ankr ankr_getTransactionsByAddress via module (55/55, 0 failed; "
        "807 txs, 33 wallets active). Receipts via fast_rpc batch (6, ~4s pause) for 517 "
        "non-approve candidates: 510 status 1, 7 status 0, 0 null, 0 mint-pattern txs. "
        "Status-0 detail: 7x failed PCS sells 0x791ac947 by machine wallets (0xa5f91a06... by 0xdb2d83f907 17:16:37 WIB, "
        "0x57222b53... by 0xc621946845 17:22:12 WIB, 0xd82c4099... by 0xc621946845 17:03:02 WIB, "
        "0x1c0c518c... by 0xc621946845 16:42:38 WIB, 0xabb7d08b... by 0xa952331ea4 16:59:38 WIB, "
        "0xf551caa1... by 0x9b519f5d52 17:17:26 WIB, 0x27b6c251... by 0x9b519f5d52 16:58:17 WIB). "
        "AFeng 0 sent txs; future1001.ai 0 txs; 0x2325... 0 txs; 0x8e96... 0 txs. "
        f"Inbound leg per 2026-11-03 12:02 amendment: Ankr getLogs address-filtered per contract, "
        f"{n_contracts} contracts, {n_logs} logs, {n_hits} hit(s), {n_failed} failed, run as a "
        f"(0-400, {ia['total_logs']} logs, {len(ia['hits'])} hits, {len(ia['failed'])} failed, {len(ia['truncated'])} truncated) "
        f"+ b (400-{ia['contracts_checked'] + ib['contracts_checked']}, {ib['total_logs']} logs, {len(ib['hits'])} hits, {len(ib['failed'])} failed, {len(ib['truncated'])} truncated) "
        f"+ gap supplement (3 contracts, {ig['total_logs']} logs, {len(ig['hits'])} hits, {len(ig['failed'])} failed, {len(ig['truncated'])} truncated). "
        f"{n_hits} hit(s) - NO inbound-only mints this run. "
        f"Failed: {[f['contract'] for f in ia['failed'] + ib['failed']]} - none, window FULLY CLOSED. "
        f"Truncated {len(trunc)} (all topic-filtered to 0 logs, incl. 0x636f... AFeng tracker, 0x1de4... AFeng sale, 0xaea143... VAULT CRACK). "
        "DYOR: contract 0x86956bc830eb62110820ae79164bef61c7e31936 in set (via snapshot), 0 hits - "
        "no tracked wallet minted DYOR in this window. "
        "CORLA 0x4a9c499574ea003846e81522d59aa4c27ca47777, the 4 run-64 ASI contracts, the 4 run-65 "
        "ASI quad-2 contracts, the 2 run-66 tokens, the 2 run-68 tokens, the run-69 token 0x4d15... "
        "the 5 run-70 tokens, the 6 run-71 tokens, the 3 run-72 tokens, the 4 run-73 tokens, the 4 run-74 tokens, "
        "the 3 run-75 tokens, the 2 run-76 tokens (0x0cda... 0 wallets, 0xacc8... 0 wallets), the 2 run-77 tokens "
        "0x5eb1.../0x1a57... (0 wallets; 0x3029... still 15 wallets - see paid_signal_run78), and GrokBot "
        "0xfcd04501ebaddcda73095a75e078a8e5292f7777 are NOT in the "
        "inbound set (PCS tokens; all their activity was wallet-sent txs covered by the sent pass). "
        "The 2 new run-78 paid tokens are likewise NOT in the inbound set - sent-pass covered. "
        "36 contract creations in window (all by 15 wallets of the 27-wallet machine set, all status 1; "
        "none is either of the 2 new tokens). "
        "No preview/mint/sign/login/purchase by this job. "
        "INFRA NOTES: (1) Inbound part b first attempt DIED at contract ~73/616 (no completion line, process gone - same failure mode as run-76 part b) after 1 caught error "
        "('Remote end closed connection' on 0x75a2d4f6f158240cb5fd4b4f866cea85b143d165, recorded as failed in the dead attempt only); re-run as tracked background exec "
        "completed the full 616/616, 0 failed. (2) run78-receipts.py sed bug: the paid-map dump path was left as run77-paid.json, so run-78 data OVERWROTE run77-paid.json; "
        "recovered by rebuilding run77-paid.json from run77-receipts-partial.json (664 raw receipts, exact same derivation) - rebuilt map verified: 47 tokens, distribution "
        "{1:14, 2:12, 3:18, 27:3}, three machine tokens byte-identical 27-sets (pairwise diffs 0); run-78 map saved to run78-paid.json; script path fixed. "
        "(3) Token-verify pair token0()/token1() for 0x41cc pair 0x22a249... failed transiently on first read (fast_rpc all endpoints failed) - verified on single retry "
        "(token0 token, token1 WBNB). (4) Ankr getLogs slow stretches again in inbound-b (several ranges minutes without progress line) - slow, not stuck. "
        "(5) SLICE-GAP found and closed this run: the Free Bacot snapshot grew between part a's list build (~10:28 UTC, 1010-list) and part b2's list build "
        "(~10:45 UTC, 1016-list), so 3 contracts sorted into B[0:400] (0x3dca07..., 0x46cb1d..., 0x4ab809...) were checked by NEITHER slice; a supplementary "
        "getLogs pass (run78-inbound-gap.py, same method/window) checked all 3 - 1,002 logs, 0 hits, 0 failed (0x3dca07 truncated, topic-filtered 0 logs). "
        "Totals above INCLUDE the gap supplement: 1,019 contracts, 16,221 logs. Window FULLY CLOSED only with the supplement."
    ),
}
s["next_run_note"] = (
    "Next run sent-tx window starts from block 131992566. Dedupe new mints against all tx hashes "
    "in reported_findings (223 mint entries over 221 unique tx hashes, direct count run 77 - the run-75 log's 223 was the mint-entry count, not unique txs; dedupe by tx hash). "
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
    "0x3029.../0x5eb1.../0x1a57... at 27 wallets each), run 78 (TWO tokens "
    "0xcbbc.../0x41cc... at 27 wallets each) auto-mint BLOCKED at guard (c) "
    "- do not re-signal or re-report the block unless a new mint/buy fact appears for those contracts "
    "(e.g. a genuine free-mint path). Paid fact: run78 max 27 wallets/token (TWO new unnamed tokens, "
    "same byte-identical 27-wallet machine set as runs 63-77 - machine rotated again: run-77 three tokens -> "
    "these two tokens, with run-77 token 0x3029... still bought by 15 of the 27 wallets as a partial continuation; "
    "the other 21 paid tokens max 3 wallets each (12 at 3, 5 at 2, 4 at 1 - usual ...7777 churn); "
    "GrokBot 0xfcd0... absent (0 wallets) this run - 19th consecutive quiet run (59, 61-78) after the run-60 burst; CORLA-97af 0 wallets; CORLA 0x4a9c 0 wallets; all "
    "four run-64 ASI contracts 0 wallets; all four run-65 ASI quad-2 contracts 0 wallets; both run-66 "
    "tokens 0 wallets; both run-68 tokens 0 wallets; run-69 token 0x4d15 0 wallets; all five run-70 "
    "tokens 0 wallets; all six run-71 tokens 0 wallets; all three run-72 tokens 0 wallets; all four "
    "run-73 tokens 0 wallets; all four run-74 tokens 0 wallets; all three run-75 tokens 0 wallets; both run-76 tokens 0 wallets; run-77 tokens 0x5eb1.../0x1a57... 0 wallets. "
    "Inbound retry next run: none - run 78 inbound had 0 failed contracts, window FULLY CLOSED. "
    "AFeng 0 sent txs this run; future1001.ai 0 txs; 0x2325... 0 txs; 0x8e96... 0 txs. "
    "Same-owner factory groups now also include 0x293f and 0x1103 (proven 2026-11-06 ~01:14 WIB, AGENTS.md) alongside the groups listed in the body."
)
s["paid_signal_run78"] = {
    "note": ("NEW paid-only signal (NOT a buy recommendation, NOT executable Free Bacot, NOT an "
             "auto-mint trigger by itself). Same-machine warning: TWO distinct NEW contracts, bought by the SAME byte-identical 27-wallet set "
             "(27/27, pairwise diff 0, diff 0 vs the run-77 27-set, overlap 27/27) - the set that also bought CORLA (run 63), ASI quad-1 (run 64), "
             "ASI quad-2 (run 65), the two run-66 tokens, the two run-68 tokens, the run-69 token, the "
             "five run-70 tokens, the six run-71 tokens, the three run-72 tokens, the four run-73 tokens, the four run-74 tokens, the three run-75 tokens, the two run-76 tokens and the three run-77 tokens - the machine rotated again: CORLA (63) -> "
             "ASI quad-1 (64) -> ASI quad-2 (65) -> two unnamed tokens (66) -> quiet (67) -> two new tokens (68) -> one token (69) -> five tokens (70) -> six tokens (71) -> three tokens (72) -> "
             "four tokens (73) -> four tokens (74) -> three tokens (75) -> two tokens (76) -> three tokens (77) -> these two tokens (78). The two are NOT one project - 2 different contracts, never merged. "
             "Partial continuation: run-77 token 0x3029... was still bought by 15 of the 27 wallets this run; run-77 tokens 0x5eb1.../0x1a57... went fully quiet (0 wallets)."),
    "project": "NEW paid tokens, same 27-wallet machine set (unnamed)",
    "contracts": [
        "0xcbbc541c2df116da9dd47dea5926dbbdae7a7777",
        "0x41cc8180b9ca58300ac2f50368945ce41b327777",
    ],
    "name_symbol_onchain": ("name() and symbol() both return EMPTY strings on-chain for both "
        "(verified via fast_rpc eth_call decode); decimals 18 for both; totalSupply 1e27 "
        "(1,000,000,000,000,000,000,000,000,000) for both; "
        "owner() 0x0 for both; "
        "tokenURI not attempted (no name/symbol identity to resolve, paid PCS tokens - same treatment as run-66/run-68/run-69/run-70/run-71/run-72/run-73/run-74/run-75/run-76/run-77 tokens)"),
    "participation": ("0xcbbc at 27 / 55 wallets (49.1%), 0x41cc at 27 / 55 wallets (49.1%); "
        "both are 0 wallets in run 77 (new this run); the two 27-wallet sets are BYTE-IDENTICAL (pairwise diff 0, diff 0 vs the run-77 27-set, overlap 27/27); "
        "first tracked buys (selector 0xb6f9de95): "
        "0x41cc 16:56:54 WIB (tx 0xe06a03e7dc9c75f6d8b90d01af1d5303b8d30806f643d9d44c50a5f7dcaf1c8f, block 131988568, wallet 0xcb08c02c0a, 0.0001216 BNB, ~9,626,203 token, pair 0x22a249dabea1d0a9aab73d579988d6b2c4feeb22), "
        "0xcbbc 17:16:03 WIB (tx 0x08878ce127b90744566c41348dfc373b66a708e0e1775df3e84488593c782cff, block 131991121, wallet 0xcb08c02c0a, 0.0001216 BNB, ~9,626,203 token, pair 0xce10caf511e8b4c9b27b90341d49bb756a4545b8); "
        "tracked Transfer logs in window: 59 (0xcbbc) / 59 (0x41cc); "
        "run-77 token 0x3029... still 15 wallets this run (partial continuation), 0x5eb1.../0x1a57... 0 wallets; "
        "not previously signaled; not in Free Bacot snapshot; not in bridge (paid-only PCS tokens, per "
        "CORLA/GrokBot/ASI precedent)"),
    "buy_evidence": (
        "Sample PCS buys verified (receipt Transfer from pair + pair token0/token1 on-chain). "
        "Pairs verified on-chain: 0xcbbc pair 0xce10caf511e8b4c9b27b90341d49bb756a4545b8 (token0 WBNB 0xbb4c..., token1 token); "
        "0x41cc pair 0x22a249dabea1d0a9aab73d579988d6b2c4feeb22 (token0 token, token1 WBNB - first read failed transiently, verified on retry). "
        "27-wallet set window totals (all router activity, not per-token; recomputed from sent.json "
        "by literal selectors, matching token-verify.py): 139x buys (0xb6f9de95, total buy value "
        "27.6319 BNB) + 244x sells (0x791ac947) + 241x approve (0x095ea7b3) + 36x contract creations."),
    "linkage": ("NOT verified: the 27 wallets are BYTE-IDENTICAL to the run-63 CORLA / run-64 ASI / "
        "run-65 ASI quad-2 / run-66 two-token / run-68 two-token / run-69 one-token / run-70 "
        "five-token / run-71 six-token / run-72 three-token / run-73 four-token / run-74 four-token / run-75 three-token / run-76 two-token / run-77 three-token sets (verified set equality vs run-77: diff 0, overlap 27/27) "
        "and deployed 36 contracts in this window via 15 wallets, which suggests the same "
        "coordinated/machine operator, but no entity collapse is applied - counted per wallet with "
        "this note, as in run 60 GrokBot / run 63 CORLA precedents"),
    "auto_mint_block": ("Trigger >25% met numerically for both (27 >= 14) but BLOCKED at "
        "guard (c): paid PCS tokens, no free-mint quota/path for the user wallet - buying would cost "
        "BNB, never a free mint; guard (a) website also unverified (empty name/symbol, no website "
        "evidence). No preview, no execution. Do not re-report the block unless a genuine free-mint "
        "path appears for these contracts."),
    "deployments_context": ("36 contract-creation txs by 15 of the 27 wallets in this window "
        "(0x1cce4ec5a7 x5, 0xaa49e7fec5 x4, 0xca4e67bb57 x3, 0x362396125a x3, 0xa952331ea4 x3, 0x97bd895f81 x3, "
        "0xdb2d83f907 x2, 0x3154f69492 x2, 0x5b4beded36 x2, 0xf9689b9d0a x2, 0xc0c84518ce x2, 0x64e893a4c5 x2, "
        "0xf795c5250f x1, 0x2cc8192fc6 x1, 0x9b519f5d52 x1), all status 1; "
        "all 36 created addresses READ from receipts this run (saved in run78-deployments.json) and NONE is either of "
        "the two new tokens - the new tokens were first bought via PCS pairs, not "
        "deployed in-window by a tracked wallet; token identity (name/symbol) of the 36 created "
        "contracts was NOT checked, so whether any of them is a future machine token is UNVERIFIED"),
}
s["paid_trend_run78"] = {
    "note": "Aggregate only, NOT a buy recommendation. TWO NEW paid-only signals (27 wallets each - see paid_signal_run78); all other tokens far below threshold. ZERO mint-pattern txs this run.",
    "max_wallets_per_token": 27,
    "distribution": "24 paid tokens: 27 wallets x2 (NEW 0xcbbc.../0x41cc...), 15 wallets x1 (run-77 token 0x3029..., partial continuation), 3 wallets x12, 2 wallets x5, 1 wallet x4 (all others ...7777-suffixed churn tokens)",
    "other_paid_activity": [
        {"pattern": "AFeng 0 sent txs; future1001.ai 0 txs; 0x2325... 0 txs; 0x8e96... 0 txs", "wallet": "0xbf004bff64725914ee36d03b87d6965b0ced4903 / 0x355ea9e542b36c645a2dee63b9df079ccb9bf3db / 0x2325f175975abdbcde555c79cc8e63381d28551b / 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6"},
        {"pattern": "7 status-0 receipts, all failed PCS sells 0x791ac947 by machine wallets (0xc621946845 x3, 0x9b519f5d52 x2, 0xdb2d83f907 x1, 0xa952331ea4 x1)", "wallet": "machine wallets"},
    ],
    "deployments": "36 contract creations in window, all by 15 wallets of the 27-wallet machine set (see paid_signal_run78 deployments_context)",
    "future1001": "0 tx this run (0x355ea9e542b36c645a2dee63b9df079ccb9bf3db)",
}
s["inbound_log_leg_run78"] = {
    "contracts": n_contracts,
    "total_logs": n_logs,
    "hits": n_hits,
    "failed": n_failed,
    "failed_contracts": [f["contract"] for f in ia["failed"] + ib["failed"]],
    "note": (f"Ankr getLogs address-filtered per contract, window 131986347-131992565, parts a "
             f"(0-400, {ia['total_logs']} logs, {len(ia['hits'])} hits, {len(ia['failed'])} failed, {len(ia['truncated'])} truncated) "
             f"+ b (400-1016, {ib['total_logs']} logs, {len(ib['hits'])} hits, {len(ib['failed'])} failed, {len(ib['truncated'])} truncated) "
             f"+ gap supplement (3 contracts, {ig['total_logs']} logs, {len(ig['hits'])} hits, {len(ig['failed'])} failed, {len(ig['truncated'])} truncated). "
             f"{n_hits} hits - 0 NEW inbound-only mints. "
             f"Truncated {len(trunc)} (all topic-filtered to 0 logs). "
             f"Failed {n_failed} - none, window FULLY CLOSED (only with the gap supplement - see method_note (5)), no retry needed next run. "
             "DYOR 0x8695... in set (via snapshot), 0 hits. No residual open from run 77. CORLA 0x4a9c + 4 run-64 ASI + 4 run-65 ASI quad-2 + the 2 run-66 tokens + the 2 run-68 tokens + the run-69 token + the 5 run-70 tokens + the 6 run-71 tokens + the 3 run-72 tokens + the 4 run-73 tokens + the 4 run-74 tokens + the 3 run-75 tokens + the 2 run-76 tokens + run-77 tokens 0x5eb1.../0x1a57... + GrokBot 0xfcd0... + the 2 new run-78 tokens not in inbound set (PCS tokens; sent-pass covered). New contracts deployed this hour (36, all "
             "addresses read, none is either of the 2 new tokens) are not in the inbound set - their token "
             "identity (name/symbol) is UNVERIFIED."),
}
sp = s.setdefault("signaled_projects_over_20pct", [])
for new_sig in [
    "Unnamed token (name/symbol empty) 0xcbbc541c2df116da9dd47dea5926dbbdae7a7777 (paid-only, run-78)",
    "Unnamed token (name/symbol empty) 0x41cc8180b9ca58300ac2f50368945ce41b327777 (paid-only, run-78)",
]:
    if new_sig not in sp:
        sp.append(new_sig)
json.dump(s, open(P, "w"), indent=1)
print("state updated: run", s["last_run"]["run"])
print(f"inbound: contracts={n_contracts} logs={n_logs} hits={n_hits} failed={n_failed}")
print("paid_signal_run78 + paid_trend_run78 + inbound_log_leg_run78 written; signaled list now", len(sp))
txs = set(); entries = 0
for f in s["reported_findings"]:
    for m in f.get("mints", []):
        entries += 1
        if m.get("tx"):
            txs.add(m["tx"].lower())
print("reported_findings mint entries:", entries, "unique txs:", len(txs))
