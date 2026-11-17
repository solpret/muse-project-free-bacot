#!/usr/bin/env python3
"""Run 70 state + bridge update (read-only job bookkeeping; no chain writes).

Completes run 70 (window 131896159-131910705), whose sent/receipt/paid/
token-verify/deployments passes were done by the 07:05 WIB execution and
whose inbound leg was re-run IN FULL in this 08:05 WIB execution.
The 5 run-70 signal tokens were already added to signaled_projects_over_20pct
by another process at ~08:10 WIB (before this script ran); this script adds
them only if absent, and writes the missing paid_signal_run70 / paid_trend_run70
/ inbound_log_leg_run70 detail keys + the AFeng finding.
"""
import json
from pathlib import Path

P = "/home/hatch/workspace/narrative-pulse/tracked-wallet-mint-scan-state.json"
B = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/scan-bridge.json"
D = Path("/home/hatch/workspace/narrative-pulse/scan-runs")

s = json.load(open(P))
ia = json.load(open(D / "run70-inbound-a.json"))
ib = json.load(open(D / "run70-inbound-b.json"))
n_contracts = ia["contracts_checked"] + ib["contracts_checked"]
n_logs = ia["total_logs"] + ib["total_logs"]
n_hits = len(ia["hits"]) + len(ib["hits"])
n_failed = len(ia["failed"]) + len(ib["failed"])
trunc = ia["truncated"] + ib["truncated"]
assert n_contracts == 973 and n_logs == 13945 and n_hits == 0 and n_failed == 0, \
    (n_contracts, n_logs, n_hits, n_failed)

# --- bridge: AFeng mint-pattern contract (run-3 ETHBack tracker precedent) ---
bridge = json.load(open(B))
CTR = "0x636fdfa9bc3db42c690c09e87b9017d05b36c743"
assert CTR not in bridge["contracts"], "bridge entry already exists"
bridge["contracts"][CTR] = {
    "source": "scan-tracked",
    "first_seen": "run-70 (2026-11-06 07:05 WIB window, mint 07:12:50 WIB)",
    "reported_as": "finding",
    "freebacot_tier": "unassigned_in_scan",
    "website": None,
    "gate": "website_no_pointer_found",
    "same_owner_discarded": False,
    "note": ("Unnamed ERC20 (name/symbol empty on-chain, decimals 18 verified, "
             "totalSupply 913191475743305484379828919270124) mint-pattern "
             "1024207770370.437134085157116837 tokens (raw 1024207770370437134085157116837, "
             "decimals 18), PAID (tx value 0.15 BNB), 1 entity only (AFeng, feed-only) - "
             "finding, NOT a signal/lead, NOT auto-mint. Via the same sale contract "
             "0x1de460f363af910f51726def188f9004276bf4bc + selector 0x4d819a2a as the run-3 "
             "ETHBack_Dividen_Tracker finding; contract is likely a dividend tracker, so "
             "mint classification beyond the zero-address Transfer is unverified. Owner "
             "0x10b389eed857fdb84089a64188aab6afbbe2cc2a, not a listed factory prefix. "
             "Not in Free Bacot snapshot at scan time. Pointer discovery run-70: "
             "contractURI() reverts on two direct RPCs (function absent, not a read "
             "failure); Sourcify 404 unverified; tokenURI n/a (ERC20). No pointer found."),
}
json.dump(bridge, open(B, "w"), indent=1)
print("bridge: +1 contract (total", len(bridge["contracts"]), ")")

# --- reported_findings: AFeng paid mint-pattern (1 new finding tx) ---
AFENG_TX = "0x5f560493b1adc1014fc55ef29dd91b2541e7822545fdebda5c61c945f4eebdc7"
existing_txs = {m.get("tx") for f in s.get("reported_findings", []) for m in f.get("mints", [])}
assert AFENG_TX not in existing_txs, "AFeng tx already in reported_findings"
s["reported_findings"].append({
    "counts": "1 tx, 1 mint-pattern event, 1 mint contract (ERC20 Transfer from zero address)",
    "free_vs_paid": "tx value 0.15 BNB = paid (gas excluded); free/paid label is per tx value, not a quote read",
    "in_free_bacot_snapshot": False,
    "mints": [{
        "call_to": "0x1de460f363af910f51726def188f9004276bf4bc",
        "kind": "ERC20 mint-pattern (Transfer from zero address)",
        "mint_contract": CTR,
        "name": "unverified (name()/symbol() both return empty strings on-chain)",
        "symbol": "unverified (empty string)",
        "time_wib": "2026-11-06 07:12:50",
        "amount": "1024207770370.437134085157116837 tokens (raw 1024207770370437134085157116837, decimals 18 verified)",
        "tx": AFENG_TX,
        "input_selector": "0x4d819a2a",
        "tx_value_bnb": 0.15,
        "owner": "0x10b389eed857fdb84089a64188aab6afbbe2cc2a",
        "note": ("Counted as a mint-pattern event because the receipt contains a Transfer "
                 "from the zero address to the wallet, per this job's method. Same sale "
                 "contract + selector as the run-3 ETHBack_Dividen_Tracker finding "
                 "(0x09bf84e67785974021222b72660b94d81e2901e6, 0.075 BNB); this is a different "
                 "tracker contract with a different amount. The contract is likely a dividend "
                 "tracker, so classifying this as a project mint (vs a distribution/tracker "
                 "allocation) is UNVERIFIED beyond the zero-address Transfer."),
    }],
    "not_a_signal": ("1 entity only (AFeng, feed-only); far below the 12-entity >20% threshold "
                     "and the 14-entity >25% auto-mint trigger. This is a finding for user "
                     "decision, NOT a signal, NOT an auto-mint trigger, NOT a Free Bacot lead "
                     "by itself. No preview/mint/sign by this job."),
    "type": "PAID ERC20 mint-pattern event, tx value 0.15 BNB",
    "wallet": "0xbf004bff64725914ee36d03b87d6965b0ced4903",
    "wallet_label": "AFeng (feed-only)",
})

s["last_run"] = {
    "run": 70,
    "block_start": 131896159,
    "block_end": 131910705,
    "window_wib": "2026-11-06 05:25:50 - 07:12:50 WIB; sent-pass in-window txs 1677, 1 mint-pattern tx (AFeng, paid)",
    "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set)",
    "method_note": (
        "Sent pass Ankr ankr_getTransactionsByAddress via module (55/55, 0 failed; "
        "1677 txs, 36 wallets active). Receipts via fast_rpc batch (6, ~4s pause) for 1088 "
        "non-approve candidates: 1081 status 1, 7 status 0 (6 failed PCS sells 0x791ac947 + "
        "1 failed aggregator call 0xef7ec2e7 by 0x8e96... 06:05:47 WIB), 0 null, 1 mint-pattern "
        "log (AFeng 0x5f560493..., paid 0.15 BNB, see reported_findings). "
        f"Inbound leg per 2026-11-03 12:02 amendment: Ankr getLogs address-filtered per contract, "
        f"{n_contracts} contracts, {n_logs} logs, {n_hits} hits, {n_failed} failed, run as a "
        f"(0-400, {ia['total_logs']} logs, {len(ia['truncated'])} truncated, {len(ia['failed'])} failed) "
        f"+ b (400-{n_contracts}, {ib['total_logs']} logs, {len(ib['truncated'])} truncated, {len(ib['failed'])} failed). "
        "Both parts were first attempted by the 07:05 WIB execution and killed mid-run "
        "(a at 200/400, b at 150/573); both were RE-RUN IN FULL in this 08:05 WIB execution "
        "(nohup + disown) and the re-run numbers are the ones recorded here. "
        f"Coverage complete: all {n_contracts} sorted contracts checked once. "
        "Truncated 3 (0x55d3... USDT / 0x6288... AGC sale / 0x63de... AGC) all topic-filtered to 0 logs. "
        "DYOR: contract 0x86956bc830eb62110820ae79164bef61c7e31936 in set (via snapshot), 0 hits - "
        "no tracked wallet minted DYOR in this window. "
        "CORLA 0x4a9c499574ea003846e81522d59aa4c27ca47777, the 4 run-64 ASI contracts, the 4 run-65 "
        "ASI quad-2 contracts, the 2 run-66 tokens, the 2 run-68 tokens, the run-69 token 0x4d15... "
        "and GrokBot 0xfcd04501ebaddcda73095a75e078a8e5292f7777 are NOT in the inbound set "
        "(PCS tokens; all their activity was wallet-sent txs covered by the sent pass). "
        "The 5 new run-70 paid tokens (PCS tokens) are likewise NOT in the inbound set - sent-pass covered. "
        "91 contract creations in window (all by 23 wallets of the 27-wallet machine set, all status 1; "
        "one receipt initially NULL 0x8eb28c90... recovered via race fallback). "
        "No preview/mint/sign/login/purchase by this job. "
        "INFRA NOTE: fast_rpc endpoints flaky in spots this run (totalSupply/symbol/owner reads "
        "failed transiently for 2 of the 5 new tokens, re-verified where possible; contractURI read "
        "for the AFeng tracker failed on all fast_rpc endpoints, then reverts on two direct RPCs - "
        "function absent, not a read failure)."
    ),
}
s["next_run_note"] = (
    "Next run sent-tx window starts from block 131910706. Dedupe new mints against all tx hashes "
    "in reported_findings (runs 1-41: 219 txs; run 70 added 1 new finding tx (AFeng 0x5f560493...), "
    "total 220). Paid-only signals run 63 (CORLA 0x4a9c), run 64 (4 ASI), run 65 (4 ASI quad-2), "
    "run 66 (tokens 0x19b7.../0x540d...), run 68 (tokens 0xf3cc.../0xe7e2...), run 69 (token 0x4d15...), "
    "run 70 (FIVE tokens 0x4df7.../0xae06.../0x2516.../0x1247.../0x8e0d...) auto-mint BLOCKED at guard (c) "
    "- do not re-signal or re-report the block unless a new mint/buy fact appears for those contracts "
    "(e.g. a genuine free-mint path). Paid fact: run70 max 27 wallets/token (FOUR new unnamed tokens "
    "at 27 wallets each + ONE at 23 wallets, same byte-identical 27-wallet machine set as runs "
    "63-66/68/69 - machine rotated again: run-69 one token -> quiet for it -> these five tokens); "
    "the other 58 paid tokens max 3 wallets each (usual ...7777 churn); GrokBot 0xfcd0... absent "
    "(0 wallets) this run - 11th consecutive quiet run (59, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70) "
    "after the run-60 burst; CORLA-97af 0 wallets; CORLA 0x4a9c 0 wallets; all four run-64 ASI contracts "
    "0 wallets; all four run-65 ASI quad-2 contracts 0 wallets; both run-66 tokens 0 wallets; both "
    "run-68 tokens 0 wallets; run-69 token 0x4d15 0 wallets. Inbound retry next run: none open - "
    "run-70 window fully closed this run (973/973, 0 hits, 0 failed). AFeng 1 tx this run (the paid "
    "mint-pattern finding, 0.15 BNB); 0x2325... 8 txs; future1001.ai 0 txs; 0x8e96... 4 txs. "
    "Same-owner factory groups now also include 0x293f and 0x1103 (proven 2026-11-06 ~01:14 WIB, "
    "AGENTS.md) alongside the groups listed in the body."
)
s["paid_signal_run70"] = {
    "note": ("NEW paid-only signal (NOT a buy recommendation, NOT executable Free Bacot, NOT an "
             "auto-mint trigger by itself). Same-machine warning: FIVE distinct NEW contracts, "
             "bought by the SAME byte-identical 27-wallet set (27/27, verified set equality vs the "
             "run-69 27-set: diff empty; the four 27-wallet sets are pairwise identical, and the "
             "23-wallet set is a subset of the 27-set) that also bought CORLA (run 63), ASI quad-1 "
             "(run 64), ASI quad-2 (run 65), the two run-66 tokens, the two run-68 tokens and the "
             "run-69 token - the machine rotated again: CORLA (63) -> ASI quad-1 (64) -> ASI quad-2 "
             "(65) -> two unnamed tokens (66) -> quiet (67) -> two new tokens (68) -> one token (69) "
             "-> these five tokens (70). The five are NOT one project - 5 different contracts, never merged."),
    "project": "NEW paid tokens, same 27-wallet machine set (unnamed)",
    "contracts": [
        "0x4df70606906311ea68dc75034a8ef45ffa547777",
        "0xae060d25764a93b1e873ca6e1678bf38c8127777",
        "0x25167807d55c4faf1b87990c268e1510bb057777",
        "0x1247be8f13c178e663aa6971ee7d8847bb1a7777",
        "0x8e0dacb670d5e2ba527b7b128ac2a395b03a7777",
    ],
    "name_symbol_onchain": ("name() and symbol() both return EMPTY strings on-chain for all five "
        "(verified via fast_rpc eth_call decode); decimals 18; totalSupply 1e9 (1,000,000,000,000,000,"
        "000,000,000,000) for 0xae06/0x2516/0x1247/0x8e0d; totalSupply unreadable for 0x4df7 (all "
        "endpoints failed transiently); owner() 0x0 for 0x4df7/0x2516/0x1247/0x8e0d, unreadable for "
        "0xae06 (all endpoints failed transiently); tokenURI not attempted (no name/symbol identity "
        "to resolve, paid PCS tokens - same treatment as run-66/run-68/run-69 tokens)"),
    "participation": ("4 tokens at 27 / 55 wallets (49.1%) + 1 token at 23 / 55 wallets (41.8%); "
        "0 wallets for all five in run 69 (new this run); first tracked buys: 0x8e0d 05:34:18 WIB, "
        "0x1247 05:56:53 WIB, 0x2516 06:15:36 WIB, 0xae06 06:36:27 WIB, 0x4df7 06:56:28 WIB; "
        "tracked Transfer logs in window: 30 / 59 / 61 / 61 / 58 respectively; not previously "
        "signaled; not in Free Bacot snapshot; not in bridge (paid-only PCS tokens, per "
        "CORLA/GrokBot/ASI precedent)"),
    "buy_evidence": (
        "Sample PCS buys verified (receipt Transfer from pair + pair token0/token1 on-chain). "
        "FIRST tracked buy per token (all selector 0xb6f9de95, ~9.09-9.10e21 raw received, ~0.000114 BNB): "
        "0x8e0d tx 0x3a9fa387d79c66a1d8f4825ae1211433d6dd84ca6055ed52974a0878cc230f14 block 131897572 "
        "05:34:18 WIB wallet 0x362396125a, pair 0x7d86b7350e6dde831ccd2f2d13f3a1adc4c64691; "
        "0x1247 tx 0x992f8d33ba4fd6c44a98e450d17b08be9769f6ed9156f8ba299ce12c7f3f994e block 131900582 "
        "05:56:53 WIB wallet 0xcb08c02c0a, pair 0x3d69c985fbc34302a6d292fbe1cc1c61bc2f1baf; "
        "0x2516 tx 0x8fbaf022bc17f85e75d376969edea15cf1a0c4f7925b0b18c58a2e014c6dba87 block 131903078 "
        "06:15:36 WIB wallet 0xcb08c02c0a, pair 0xde66bcd809bd8cd5ae6bf777ee21fbf742572061; "
        "0xae06 tx 0x16e39400521f4b4e1481db9bfbbe9197caf51b6a657db1151ebe173849d6cf8f block 131905858 "
        "06:36:27 WIB wallet 0xcb08c02c0a, pair 0xadebab10d213afdf47c9716f61798e60cd80fa9b; "
        "0x4df7 tx 0x60a0db3002cd349efb0d9775cb41f55c03c89ac1c86af9141d1fdf309776c319 block 131908526 "
        "06:56:28 WIB wallet 0xcb08c02c0a, pair 0xa5d5e5cda79e7bb7da067e251baa4eb4a59635d1 (pair "
        "token0 unreadable transiently, token1=WBNB 0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c). "
        "27-wallet set window totals (all router activity, not per-token; recomputed from sent.json "
        "by literal selectors, matching token-verify.py): 269x buys (0xb6f9de95, total buy value "
        "52.2492 BNB) + 471x sells (0x791ac947) + 465x approve (0x095ea7b3) + 91x contract creations "
        "(0x60806040) by 23 of the 27 wallets."),
    "linkage": ("NOT verified: the 27 wallets are BYTE-IDENTICAL to the run-63 CORLA / run-64 ASI / "
        "run-65 ASI quad-2 / run-66 two-token / run-68 two-token / run-69 one-token sets (verified "
        "set equality vs run-69: diff empty) and deployed 91 contracts in this window via 23 wallets, "
        "which suggests the same coordinated/machine operator, but no entity collapse is applied - "
        "counted per wallet with this note, as in run 60 GrokBot / run 63 CORLA precedents"),
    "auto_mint_block": ("Trigger >25% met numerically for all five (27 >= 14, 23 >= 14) but BLOCKED at "
        "guard (c): paid PCS tokens, no free-mint quota/path for the user wallet - buying would cost "
        "BNB, never a free mint; guard (a) website also unverified (empty name/symbol, no website "
        "evidence). No preview, no execution. Do not re-report the block unless a genuine free-mint "
        "path appears for these contracts."),
    "deployments_context": ("91 contract-creation txs by 23 of the 27 wallets in this window "
        "(0x97bd895f x9, 0xdb2d83f9 x7, 0x5b4beded x7, 0xf9689b9d x7, 0x1cce4ec5 x7, 0x36239612 x6, "
        "0xc6219468 x5, 0xaa49e7fe x5, 0x3154f694 x5, 0xca4e67bb x5, 0xc0c84518 x5, 0x82c6085f x4, "
        "0xa952331e x4, 0x2cc8192f x3, 0xb940e4cd x2, 0x9b519f5d x2, 0x64e893a4 x2, 0xf795c525 x1, "
        "0xc6591fde x1, 0xcb08c02c x1, 0x92bc3297 x1, 0xfdec62fd x1, 0x4522e661 x1), all status 1; all 91 created "
        "addresses READ from receipts this run (saved in run70-deployments.json) and NONE is any of "
        "the five new tokens - the new tokens were first bought via PCS pairs, not deployed in-window "
        "by a tracked wallet; token identity (name/symbol) of the 91 created contracts was NOT "
        "checked, so whether any of them is a future machine token is UNVERIFIED"),
}
s["paid_trend_run70"] = {
    "note": "Aggregate only, NOT a buy recommendation. FIVE NEW paid-only signals at 27/27/27/27/23 wallets (see paid_signal_run70); all other tokens far below threshold.",
    "max_wallets_per_token": 27,
    "distribution": "63 paid tokens: 27 wallets x4 (NEW unnamed machine tokens), 23 wallets x1 (NEW unnamed machine token), 3 wallets x29, 2 wallets x14, 1 wallet x15 (all others ...7777-suffixed churn tokens except 0x7488...'s micro-buys)",
    "other_paid_activity": [
        {"pattern": "6x 0x27772d13 calls via 0x296b00198dc7ec3410e12da814d9267bb8df506a (values 0 / 0.02 / 0 / 0.1 / 0.1 / 0.1 BNB, total 0.32 BNB) + 2x approve 0x095ea7b3, receiving tokens from pair contracts (swap-like, not mints)", "wallet": "0x2325f175975abdbcde555c79cc8e63381d28551b"},
        {"pattern": "3x 0xef7ec2e7 calls via 0xe2ce6ab80874fa9fa2aae65d277dd6b8e65c9de0 (values 0 / 0.002 / 0.002 BNB; the 06:05:47 call is status 0) + 1x approve, receiving from pair", "wallet": "0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6"},
        {"pattern": "9 PCS micro buy/sell cycles (buy 0xb6f9de95 ~0.00008-0.00009 BNB, sell 0x791ac947 value 0) + 1 extra sell, each buy preceded by an approve; 28 txs total", "wallet": "0x7488d5da6a6097de0ff88c7492c62c2fd1e56650"},
        {"pattern": "7 status-0 receipts: 6 failed PCS sells (0x791ac947) by 0xdb2d83f9 (2x), 0xc6219468 (1x), 0xa952331e (3x) + 1 failed aggregator call (0xef7ec2e7) by 0x8e96... - machine churn, not mints", "wallet": "machine wallets / 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6"},
        {"pattern": "AFeng 1 tx: the paid mint-pattern finding (0.15 BNB, tracker 0x636fdfa9...); 0x2325... 8 txs; future1001.ai 0 txs; 0x8e96... 4 txs", "wallet": "0xbf004bff64725914ee36d03b87d6965b0ced4903 / 0x2325f175975abdbcde555c79cc8e63381d28551b / 0x355ea9e542b36c645a2dee63b9df079ccb9bf3db / 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6"},
    ],
    "deployments": "91 contract creations in window, all by 23 wallets of the 27-wallet machine set (see paid_signal_run70 deployments_context)",
    "future1001": "0 tx this run (0x355ea9e542b36c645a2dee63b9df079ccb9bf3db)",
}
s["inbound_log_leg_run70"] = {
    "contracts": n_contracts,
    "total_logs": n_logs,
    "hits": n_hits,
    "failed": n_failed,
    "failed_contracts": [],
    "note": (f"Ankr getLogs address-filtered per contract, window 131896159-131910705, parts a "
             f"(0-400, {ia['total_logs']} logs, {len(ia['truncated'])} truncated, {len(ia['failed'])} failed) "
             f"+ b (400-{n_contracts}, {ib['total_logs']} logs, {len(ib['truncated'])} truncated, {len(ib['failed'])} failed). "
             "Both parts first attempted by the 07:05 WIB execution and killed mid-run (a 200/400, b 150/573); "
             "both RE-RUN IN FULL in this 08:05 WIB execution (nohup + disown) - the re-run numbers are the "
             "ones recorded here. 0 hits - 0 inbound-only new mints. Truncated 3 (0x55d3... USDT / 0x6288... "
             "AGC sale / 0x63de... AGC) all topic-filtered to 0 logs. "
             "DYOR 0x8695... in set (via snapshot), 0 hits. No residual open from run 69 (its window fully "
             "closed, 0 failed). CORLA 0x4a9c + 4 run-64 ASI + 4 run-65 ASI quad-2 + the 2 run-66 tokens + "
             "the 2 run-68 tokens + the run-69 token + GrokBot 0xfcd0... + the 5 new run-70 tokens not in "
             "inbound set (PCS tokens; sent-pass covered). New contracts deployed this hour (91, all "
             "addresses read, none is any of the 5 new tokens) are not in the inbound set - their token "
             "identity (name/symbol) is UNVERIFIED."),
}
sp = s.setdefault("signaled_projects_over_20pct", [])
for new_sig in [
    "Unnamed token (name/symbol empty) 0x4df70606906311ea68dc75034a8ef45ffa547777 (paid-only, run-70)",
    "Unnamed token (name/symbol empty) 0xae060d25764a93b1e873ca6e1678bf38c8127777 (paid-only, run-70)",
    "Unnamed token (name/symbol empty) 0x25167807d55c4faf1b87990c268e1510bb057777 (paid-only, run-70)",
    "Unnamed token (name/symbol empty) 0x1247be8f13c178e663aa6971ee7d8847bb1a7777 (paid-only, run-70)",
    "Unnamed token (name/symbol empty) 0x8e0dacb670d5e2ba527b7b128ac2a395b03a7777 (paid-only, run-70)",
]:
    if new_sig not in sp:
        sp.append(new_sig)
json.dump(s, open(P, "w"), indent=1)
print("state updated: run", s["last_run"]["run"])
print(f"inbound: contracts={n_contracts} logs={n_logs} hits={n_hits} failed={n_failed}")
print("paid_signal_run70 + paid_trend_run70 + inbound_log_leg_run70 written; signaled list now", len(sp))
print("reported_findings total txs now:", sum(len(f.get('mints', [])) for f in s['reported_findings']))
