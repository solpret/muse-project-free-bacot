#!/usr/bin/env python3
"""Run 71 state + bridge update (read-only job bookkeeping; no chain writes).

Completes run 71 (window 131910706-131926119), whose sent/receipts/paid/
token-verify/deployments/detail/pointer passes are all done and whose inbound
leg ran in full (a 0-400 + b 400-992, 0 failed).
"""
import json
from pathlib import Path

P = "/home/hatch/workspace/narrative-pulse/tracked-wallet-mint-scan-state.json"
B = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/scan-bridge.json"
D = Path("/home/hatch/workspace/narrative-pulse/scan-runs")

s = json.load(open(P))
ia = json.load(open(D / "run71-inbound-a.json"))
ib = json.load(open(D / "run71-inbound-b.json"))
n_contracts = ia["contracts_checked"] + ib["contracts_checked"]
n_logs = ia["total_logs"] + ib["total_logs"]
n_hits = len(ia["hits"]) + len(ib["hits"])
n_failed = len(ia["failed"]) + len(ib["failed"])
trunc = ia["truncated"] + ib["truncated"]
assert n_contracts == 992 and n_logs == 18831 and n_hits == 3 and n_failed == 0, \
    (n_contracts, n_logs, n_hits, n_failed)

# --- bridge: new 0x2325 mint-pattern contract 0x93bf08d2... ---
bridge = json.load(open(B))
CTR = "0x93bf08d2936aefe0cd2ceba8f76cb566fdf9e1c9"
assert CTR not in bridge["contracts"], "bridge entry already exists"
bridge["contracts"][CTR] = {
    "source": "scan-tracked",
    "first_seen": "run-71 (2026-11-06 09:05 WIB window, mint-pattern 07:22:53 WIB)",
    "reported_as": "finding",
    "freebacot_tier": "unassigned_in_scan",
    "website": None,
    "gate": "website_no_pointer_found",
    "same_owner_discarded": False,
    "note": ("Unnamed ERC20 (name()/symbol() both return EMPTY strings on-chain, decimals 18 "
             "verified, totalSupply 2546375629583187808604863069959643) mint-pattern "
             "57779323996.508220387519030261165 tokens (raw 57779323996508220387519030261165, "
             "decimals 18), PAID (tx value 0.03 BNB), 1 entity only (0x2325..., tier-ab) - "
             "finding, NOT a signal/lead, NOT auto-mint. Via aggregator call to "
             "0x296b00198dc7ec3410e12da814d9267bb8df506a + selector 0x27772d13. In-window "
             "zero-address Transfers from this contract: 15 logs to 11 distinct recipients, "
             "only 0x2325... tracked - distribution/tracker-like pattern, so mint "
             "classification beyond the zero-address Transfer is UNVERIFIED (same caveat as "
             "the ETHBack tracker findings). Owner 0xfc48a848dc97233a06dc924af764a0994e457274, "
             "not a listed factory prefix. Not in Free Bacot snapshot at scan time. Pointer "
             "discovery run-71: contractURI() REVERTS via direct curl (function absent, not a "
             "read failure); Sourcify 404 unverified (sources + ABI); tokenURI n/a (ERC20). "
             "No pointer found."),
}
json.dump(bridge, open(B, "w"), indent=1)
print("bridge: +1 contract (total", len(bridge["contracts"]), ")")

# --- reported_findings: 0x2325 paid mint-pattern (1 new finding tx) ---
TX93 = "0xa20c70c177541d76b369f296640231bc45a578163aff03fcf8048e513d19db95"
existing_txs = {m.get("tx") for f in s.get("reported_findings", []) for m in f.get("mints", [])}
assert TX93 not in existing_txs, "0x2325 tx already in reported_findings"
s["reported_findings"].append({
    "counts": "1 tx, 1 mint-pattern event, 1 mint contract (ERC20 Transfer from zero address)",
    "free_vs_paid": "tx value 0.03 BNB = paid (gas excluded); free/paid label is per tx value, not a quote read",
    "in_free_bacot_snapshot": False,
    "mints": [{
        "call_to": "0x296b00198dc7ec3410e12da814d9267bb8df506a",
        "kind": "ERC20 mint-pattern (Transfer from zero address)",
        "mint_contract": CTR,
        "name": "unverified (name()/symbol() both return empty strings on-chain)",
        "symbol": "unverified (empty string)",
        "time_wib": "2026-11-06 07:22:53",
        "amount": "57779323996.508220387519030261165 tokens (raw 57779323996508220387519030261165, decimals 18 verified)",
        "tx": TX93,
        "input_selector": "0x27772d13",
        "tx_value_bnb": 0.03,
        "owner": "0xfc48a848dc97233a06dc924af764a0994e457274",
        "note": ("Counted as a mint-pattern event because the receipt contains a Transfer "
                 "from the zero address to the wallet, per this job's method. In-window "
                 "zero-address Transfers from this contract total 15 logs to 11 distinct "
                 "recipients, only 0x2325... tracked - distribution/tracker-like pattern, so "
                 "classifying this as a project mint (vs a distribution/tracker allocation) "
                 "is UNVERIFIED beyond the zero-address Transfer (same caveat as the ETHBack "
                 "tracker findings runs 9/13/70)."),
    }],
    "not_a_signal": ("1 entity only (0x2325..., tier-ab); far below the 12-entity >20% threshold "
                     "and the 14-entity >25% auto-mint trigger. This is a finding for user "
                     "decision, NOT a signal, NOT an auto-mint trigger, NOT a Free Bacot lead "
                     "by itself. No preview/mint/sign by this job."),
    "type": "PAID ERC20 mint-pattern event, tx value 0.03 BNB",
    "wallet": "0x2325f175975abdbcde555c79cc8e63381d28551b",
    "wallet_label": "0x2325f175 (tier-ab)",
})

s["last_run"] = {
    "run": 71,
    "block_start": 131910706,
    "block_end": 131926119,
    "window_wib": "2026-11-06 07:13:09 - 09:08:27 WIB; sent-pass in-window txs 2156, 4 mint-pattern txs (1 new 0x2325 + 3 repeat AFeng tracker)",
    "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set)",
    "method_note": (
        "Sent pass Ankr ankr_getTransactionsByAddress via module (55/55, 0 failed; "
        "2156 txs, 37 wallets active). Receipts via fast_rpc batch (6, ~4s pause) for 1378 "
        "non-approve candidates: 1365 status 1, 13 status 0 (all failed PCS sells 0x791ac947 "
        "by machine wallets), 0 null after recovery (2 initially NULL receipts "
        "0x2f64cd6b25... + 0x6477ee82ca..., both PCS buys 0xb6f9de95, recovered via race "
        "fallback: status 1, 5 logs each, no zero-from Transfer), 4 mint-pattern logs "
        "(1 new 0x2325 0x93bf... paid 0.03 BNB + 3 AFeng 0x636f... repeat of the run-70 "
        "tracker contract, see reported_findings). "
        f"Inbound leg per 2026-11-03 12:02 amendment: Ankr getLogs address-filtered per contract, "
        f"{n_contracts} contracts, {n_logs} logs, {n_hits} hits, {n_failed} failed, run as a "
        f"(0-400, {ia['total_logs']} logs, {len(ia['truncated'])} truncated, {len(ia['failed'])} failed) "
        f"+ b (400-{n_contracts}, {ib['total_logs']} logs, {len(ib['truncated'])} truncated, {len(ib['failed'])} failed). "
        "Coverage complete: all 992 sorted contracts checked once. "
        "Truncated 4 (0x55d3... USDT 0 logs / 0x6288... AGC sale 0 logs / 0x636f... tracker 3 logs = "
        "the 3 sent-pass AFeng txs / 0x63de... AGC 0 logs, all topic-filtered). "
        "DYOR: contract 0x86956bc830eb62110820ae79164bef61c7e31936 in set (via snapshot), 0 hits - "
        "no tracked wallet minted DYOR in this window. "
        "CORLA 0x4a9c499574ea003846e81522d59aa4c27ca47777, the 4 run-64 ASI contracts, the 4 run-65 "
        "ASI quad-2 contracts, the 2 run-66 tokens, the 2 run-68 tokens, the run-69 token 0x4d15... "
        "the 5 run-70 tokens, and GrokBot 0xfcd04501ebaddcda73095a75e078a8e5292f7777 are NOT in the "
        "inbound set (PCS tokens; all their activity was wallet-sent txs covered by the sent pass). "
        "The 6 new run-71 paid tokens are likewise NOT in the inbound set - sent-pass covered. "
        "The new 0x93bf... contract is NOT in the inbound set either (new this run) - covered by "
        "the topic-filtered re-check in run71-detail-93bf.py (1 tracked log = the finding tx itself; "
        "15 zero-from logs to 11 recipients, only 0x2325... tracked). "
        "112 contract creations in window (all by 16 wallets of the 27-wallet machine set, all status 1; "
        "none is any of the 6 new tokens or 0x93bf...). "
        "No preview/mint/sign/login/purchase by this job. "
        "INFRA NOTE: fast_rpc endpoints flaky in spots this run (2 receipts initially NULL, recovered; "
        "totalSupply/owner unreadable transiently for 0x5785...; pair token0/token1 unreadable "
        "transiently for 0xe51b.../0xe4c9...; symbol() for 0x93bf... failed once then returned '' on "
        "retry; contractURI for 0x93bf... failed on all fast_rpc endpoints, then REVERTED via direct "
        "curl to bsc-dataseed.binance.org - function absent, not a read failure)."
    ),
}
s["next_run_note"] = (
    "Next run sent-tx window starts from block 131926120. Dedupe new mints against all tx hashes "
    "in reported_findings (runs 1-41: 219 txs; run 70 added 1 new finding tx (AFeng 0x5f560493...); "
    "run 71 added 1 new finding tx (0x2325 0xa20c70c1...), total 221). Paid-only signals run 63 "
    "(CORLA 0x4a9c), run 64 (4 ASI), run 65 (4 ASI quad-2), run 66 (tokens 0x19b7.../0x540d...), run 68 "
    "(tokens 0xf3cc.../0xe7e2...), run 69 (token 0x4d15...), run 70 (FIVE tokens "
    "0x4df7.../0xae06.../0x2516.../0x1247.../0x8e0d...), run 71 (SIX tokens "
    "0xe51b.../0xc2e1.../0x5785.../0xfff4.../0xe4c9.../0x25b4...) auto-mint BLOCKED at guard (c) "
    "- do not re-signal or re-report the block unless a new mint/buy fact appears for those contracts "
    "(e.g. a genuine free-mint path). Paid fact: run71 max 27 wallets/token (FIVE new unnamed tokens "
    "at 27 wallets each + ONE at 26 wallets, same byte-identical 27-wallet machine set as runs "
    "63-66/68/69/70 - machine rotated again: run-70 five tokens -> quiet for them (0 wallets) -> "
    "these six tokens); the other 58 paid tokens max 3 wallets each (usual ...7777 churn); GrokBot "
    "0xfcd0... absent (0 wallets) this run - 12th consecutive quiet run (59, 61, 62, 63, 64, 65, 66, "
    "67, 68, 69, 70, 71) after the run-60 burst; CORLA-97af 0 wallets; CORLA 0x4a9c 0 wallets; all "
    "four run-64 ASI contracts 0 wallets; all four run-65 ASI quad-2 contracts 0 wallets; both run-66 "
    "tokens 0 wallets; both run-68 tokens 0 wallets; run-69 token 0x4d15 0 wallets; all five run-70 "
    "tokens 0 wallets. Inbound retry next run: none open - run-71 window fully closed this run "
    "(992/992, 3 hits = sent-pass AFeng txs, 0 failed). AFeng 159 txs this run (67x tracker calls "
    "0x4d819a2a incl. the 3 mint-pattern txs to the SAME run-70 tracker contract 0x636f..., 76x "
    "approve, 16x 0x0c307f76); 0x2325... 8 txs (incl. the new 0x93bf... finding); future1001.ai 0 txs; "
    "0x8e96... 3 txs. Same-owner factory groups now also include 0x293f and 0x1103 (proven 2026-11-06 "
    "~01:14 WIB, AGENTS.md) alongside the groups listed in the body."
)
s["paid_signal_run71"] = {
    "note": ("NEW paid-only signal (NOT a buy recommendation, NOT executable Free Bacot, NOT an "
             "auto-mint trigger by itself). Same-machine warning: SIX distinct NEW contracts, "
             "bought by the SAME byte-identical 27-wallet set (27/27, verified set equality vs the "
             "run-70 27-set: diff empty; the five 27-wallet sets are pairwise identical, and the "
             "26-wallet set is a subset of the 27-set, missing only 0xf9689b9d...) that also bought "
             "CORLA (run 63), ASI quad-1 (run 64), ASI quad-2 (run 65), the two run-66 tokens, the "
             "two run-68 tokens, the run-69 token and the five run-70 tokens - the machine rotated "
             "again: CORLA (63) -> ASI quad-1 (64) -> ASI quad-2 (65) -> two unnamed tokens (66) -> "
             "quiet (67) -> two new tokens (68) -> one token (69) -> five tokens (70) -> these six "
             "tokens (71). The six are NOT one project - 6 different contracts, never merged."),
    "project": "NEW paid tokens, same 27-wallet machine set (unnamed)",
    "contracts": [
        "0xe51bf2d65277348d637aa2f5da0c469fcbe37777",
        "0xc2e1817850a53f79c86945aa693164d966e67777",
        "0x578532b4d613d63fafcf6e469ce5447cb8fa7777",
        "0xfff4f02e8dd452b24583440d5def001d34357777",
        "0xe4c99e2cd10284d549c040369a775ff7f3f47777",
        "0x25b466a9fff9292b863b2449facd9dc570b07777",
    ],
    "name_symbol_onchain": ("name() and symbol() both return EMPTY strings on-chain for all six "
        "(verified via fast_rpc eth_call decode); decimals 18; totalSupply 1e27 "
        "(1,000,000,000,000,000,000,000,000,000) for 0xe51b/0xc2e1/0xfff4/0xe4c9/0x25b4; "
        "totalSupply + owner() unreadable for 0x5785 (all endpoints failed transiently); owner() "
        "0x0 for the other five; tokenURI not attempted (no name/symbol identity to resolve, paid "
        "PCS tokens - same treatment as run-66/run-68/run-69/run-70 tokens)"),
    "participation": ("5 tokens at 27 / 55 wallets (49.1%) + 1 token at 26 / 55 wallets (47.3%); "
        "0 wallets for all six in run 70 (new this run); first tracked buys: 0x25b4 07:16:22 WIB, "
        "0xfff4 07:54:58 WIB, 0x5785 08:14:15 WIB, 0xc2e1 08:33:16 WIB (all selector 0xb6f9de95, "
        "~0.000114 BNB, wallets 0xcb08c02c0a / 0x362396125a); first tracked Transfer tx NOT a "
        "tracked sent tx for 0xe51b (first log block 131923983) and 0xe4c9 (first log block "
        "131913709), so first-buy wallet/value is UNVERIFIED for those two; "
        "tracked Transfer logs in window: 58 / 61 / 58 / 62 / 59 / 61 respectively; not previously "
        "signaled; not in Free Bacot snapshot; not in bridge (paid-only PCS tokens, per "
        "CORLA/GrokBot/ASI precedent)"),
    "buy_evidence": (
        "Sample PCS buys verified (receipt Transfer from pair + pair token0/token1 on-chain). "
        "FIRST tracked buy per token (selector 0xb6f9de95, ~0.000114 BNB) where the tx is a tracked "
        "sent tx: 0x25b4 tx 0x1ff742b1b801e070ce3dc7ee36fc47fa8afc9da2c22d1582a0bba7b8445092a9 block "
        "131911177 07:16:22 WIB wallet 0xcb08c02c0a, pair 0x4ada878a533c23a92f943d4c16dd026cf96b65c6; "
        "0xfff4 tx 0xd5e26ee014779ab28137240570bf891f56de8cfb605129983053d99346af73b5 block 131916322 "
        "07:54:58 WIB wallet 0xcb08c02c0a, pair 0xa999f19acdf0ab799c529658897bebfd47420207; "
        "0x5785 tx 0xf9bbc41ae2c4ba632847377ceb6e2a5d4edb6a6b97db8fd6ca4688b8cd34ca6f block 131918893 "
        "08:14:15 WIB wallet 0xcb08c02c0a, pair 0xe07f184e78651f7e3bd1f15d73f886932d74710a; "
        "0xc2e1 tx 0xa915a3c5347213bf15f09e36fba22a48be12763138c6ba0fd5aa645c8b3076a6 block 131921428 "
        "08:33:16 WIB wallet 0x362396125a, pair 0x941113b82700c6cd06b9719ecbcaba261a984ebf; "
        "0xe51b first tracked log tx 0xb98d4e3d71aaa68e56a748d13807e096d79ee1e0584d257cb16e8eed839f6028 "
        "block 131923983 from pair 0x588916d9193bcec05c966f31cb57cad98c09c131 (pair token0/token1 "
        "unreadable transiently); 0xe4c9 first tracked log tx "
        "0xac518a45793522ab2768979267c7ef522c61211e4f9d3de6de93952fb6d6ad36 block 131913709 from pair "
        "0x843b7a9b06765a5bf08e85fc17a54ff3df272ee1 (pair token0/token1 unreadable transiently). "
        "27-wallet set window totals (all router activity, not per-token; recomputed from sent.json "
        "by literal selectors, matching token-verify.py): 357x buys (0xb6f9de95, total buy value "
        "67.6758 BNB) + 593x sells (0x791ac947) + 584x approve (0x095ea7b3) + 112x contract creations "
        "(0x60806040) by 16 of the 27 wallets."),
    "linkage": ("NOT verified: the 27 wallets are BYTE-IDENTICAL to the run-63 CORLA / run-64 ASI / "
        "run-65 ASI quad-2 / run-66 two-token / run-68 two-token / run-69 one-token / run-70 "
        "five-token sets (verified set equality vs run-70: diff empty) and deployed 112 contracts "
        "in this window via 16 wallets, which suggests the same coordinated/machine operator, but "
        "no entity collapse is applied - counted per wallet with this note, as in run 60 GrokBot / "
        "run 63 CORLA precedents"),
    "auto_mint_block": ("Trigger >25% met numerically for all six (27 >= 14, 26 >= 14) but BLOCKED at "
        "guard (c): paid PCS tokens, no free-mint quota/path for the user wallet - buying would cost "
        "BNB, never a free mint; guard (a) website also unverified (empty name/symbol, no website "
        "evidence). No preview, no execution. Do not re-report the block unless a genuine free-mint "
        "path appears for these contracts."),
    "deployments_context": ("112 contract-creation txs by 16 of the 27 wallets in this window "
        "(0xdb2d83f9 x17, 0x97bd895f x10, 0xaa49e7fe x8, 0xca4e67bb x8, 0x5b4beded x8, 0xf9689b9d x8, "
        "0x2cc8192f x8, 0x1cce4ec5 x8, 0xc6219468 x7, 0x3154f694 x7, 0x36239612 x7, 0xc0c84518 x6, "
        "0xfdec62fd x3, 0x64e893a4 x3, 0xa952331e x2, 0x92bc3297 x2), all status 1; all 112 created "
        "addresses READ from receipts this run (saved in run71-deployments.json) and NONE is any of "
        "the six new tokens or 0x93bf... - the new tokens were first bought via PCS pairs, not "
        "deployed in-window by a tracked wallet; token identity (name/symbol) of the 112 created "
        "contracts was NOT checked, so whether any of them is a future machine token is UNVERIFIED"),
}
s["paid_trend_run71"] = {
    "note": "Aggregate only, NOT a buy recommendation. SIX NEW paid-only signals at 27/27/27/27/27/26 wallets (see paid_signal_run71); all other tokens far below threshold.",
    "max_wallets_per_token": 27,
    "distribution": "64 paid tokens: 27 wallets x5 (NEW unnamed machine tokens), 26 wallets x1 (NEW unnamed machine token), 3 wallets x27, 2 wallets x12, 1 wallet x19 (all others ...7777-suffixed churn tokens except 0x7488...'s micro-buys)",
    "other_paid_activity": [
        {"pattern": "5x 0x27772d13 calls via 0x296b00198dc7ec3410e12da814d9267bb8df506a (values 0.03 / 0 / 0 / 0 / 0.1 BNB, total 0.13 BNB) + 3x approve 0x095ea7b3; the 0.03 BNB call is the new 0x93bf... mint-pattern finding, the rest swap-like receiving from pair contracts, not mints", "wallet": "0x2325f175975abdbcde555c79cc8e63381d28551b"},
        {"pattern": "2x 0xef7ec2e7 calls via 0xe2ce6ab80874fa9fa2aae65d277dd6b8e65c9de0 (values 0 / 0.002 BNB) + 1x approve, receiving from pair", "wallet": "0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6"},
        {"pattern": "13 status-0 receipts: all failed PCS sells (0x791ac947) by 0xdb2d83f9 (3x), 0xc6219468 (4x), 0xc0c84518 (2x), 0xa952331e (2x), 0x92bc3297 (1x), 0xfdec62fd (1x) - machine churn, not mints", "wallet": "machine wallets"},
        {"pattern": "AFeng 159 txs: 67x tracker calls 0x4d819a2a (incl. 3 mint-pattern txs to the SAME run-70 tracker contract 0x636f..., values 0.075/0.15/0.075 BNB - repeat events of an already-reported contract, NOT a new finding) + 76x approve 0x095ea7b3 + 16x 0x0c307f76; 0x2325... 8 txs; future1001.ai 0 txs; 0x8e96... 3 txs", "wallet": "0xbf004bff64725914ee36d03b87d6965b0ced4903 / 0x2325f175975abdbcde555c79cc8e63381d28551b / 0x355ea9e542b36c645a2dee63b9df079ccb9bf3db / 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6"},
    ],
    "deployments": "112 contract creations in window, all by 16 wallets of the 27-wallet machine set (see paid_signal_run71 deployments_context)",
    "future1001": "0 tx this run (0x355ea9e542b36c645a2dee63b9df079ccb9bf3db)",
}
s["inbound_log_leg_run71"] = {
    "contracts": n_contracts,
    "total_logs": n_logs,
    "hits": n_hits,
    "failed": n_failed,
    "failed_contracts": [],
    "note": (f"Ankr getLogs address-filtered per contract, window 131910706-131926119, parts a "
             f"(0-400, {ia['total_logs']} logs, {len(ia['truncated'])} truncated, {len(ia['failed'])} failed) "
             f"+ b (400-{n_contracts}, {ib['total_logs']} logs, {len(ib['truncated'])} truncated, {len(ib['failed'])} failed). "
             f"{n_hits} hits - all 3 are the sent-pass AFeng tracker txs (0x636f..., blocks 131911935/131923300/131925570) - "
             "0 inbound-only new mints. Truncated 4 (0x55d3... USDT 0 logs / 0x6288... AGC sale 0 logs / "
             "0x636f... tracker 3 logs = sent-pass / 0x63de... AGC 0 logs, all topic-filtered). "
             "DYOR 0x8695... in set (via snapshot), 0 hits. No residual open from run 70 (its window fully "
             "closed, 0 failed). CORLA 0x4a9c + 4 run-64 ASI + 4 run-65 ASI quad-2 + the 2 run-66 tokens + "
             "the 2 run-68 tokens + the run-69 token + the 5 run-70 tokens + GrokBot 0xfcd0... + the 6 new "
             "run-71 tokens + 0x93bf... not in inbound set (PCS tokens / new contract; sent-pass + "
             "topic-filtered detail re-check covered). New contracts deployed this hour (112, all "
             "addresses read, none is any of the 6 new tokens or 0x93bf...) are not in the inbound set - their token "
             "identity (name/symbol) is UNVERIFIED."),
}
sp = s.setdefault("signaled_projects_over_20pct", [])
for new_sig in [
    "Unnamed token (name/symbol empty) 0xe51bf2d65277348d637aa2f5da0c469fcbe37777 (paid-only, run-71)",
    "Unnamed token (name/symbol empty) 0xc2e1817850a53f79c86945aa693164d966e67777 (paid-only, run-71)",
    "Unnamed token (name/symbol empty) 0x578532b4d613d63fafcf6e469ce5447cb8fa7777 (paid-only, run-71)",
    "Unnamed token (name/symbol empty) 0xfff4f02e8dd452b24583440d5def001d34357777 (paid-only, run-71)",
    "Unnamed token (name/symbol empty) 0xe4c99e2cd10284d549c040369a775ff7f3f47777 (paid-only, run-71)",
    "Unnamed token (name/symbol empty) 0x25b466a9fff9292b863b2449facd9dc570b07777 (paid-only, run-71)",
]:
    if new_sig not in sp:
        sp.append(new_sig)
json.dump(s, open(P, "w"), indent=1)
print("state updated: run", s["last_run"]["run"])
print(f"inbound: contracts={n_contracts} logs={n_logs} hits={n_hits} failed={n_failed}")
print("paid_signal_run71 + paid_trend_run71 + inbound_log_leg_run71 written; signaled list now", len(sp))
print("reported_findings total txs now:", sum(len(f.get('mints', [])) for f in s['reported_findings']))
