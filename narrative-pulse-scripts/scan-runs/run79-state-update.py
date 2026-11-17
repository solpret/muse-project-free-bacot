#!/usr/bin/env python3
"""Run 79 state update (read-only job bookkeeping; no chain writes).

Completes run 79 (window 131992566-131999043), whose sent/receipts/paid/
token-verify/deployments passes are all done and whose inbound leg ran in
full (a 0-400 + b 400-1016) from ONE frozen contract list (run-78 lesson:
no slice-gap this run).
"""
import json
import shutil
from pathlib import Path

P = "/home/hatch/workspace/narrative-pulse/tracked-wallet-mint-scan-state.json"
D = Path("/home/hatch/workspace/narrative-pulse/scan-runs")

shutil.copy(P, str(P) + ".bak-run79-pre")
s = json.load(open(P))
ia = json.load(open(D / "run79-inbound-a.json"))
ib = json.load(open(D / "run79-inbound-b.json"))
n_contracts = ia["contracts_checked"] + ib["contracts_checked"]
n_logs = ia["total_logs"] + ib["total_logs"]
n_hits = len(ia["hits"]) + len(ib["hits"])
n_failed = len(ia["failed"]) + len(ib["failed"])
trunc = ia["truncated"] + ib["truncated"]
print(f"inbound totals: contracts={n_contracts} logs={n_logs} hits={n_hits} failed={n_failed} truncated={len(trunc)}")
print(f"failed contracts: {[f['contract'] for f in ia['failed'] + ib['failed']]}")

s["last_run"] = {
    "run": 79,
    "block_start": 131992566,
    "block_end": 131999043,
    "window_wib": "2026-11-06 17:28:21 - 18:15:29 WIB; sent-pass in-window txs 697, 0 mint-pattern txs",
    "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set)",
    "method_note": (
        "Sent pass Ankr ankr_getTransactionsByAddress via module (55/55, 0 failed; "
        "697 txs, 35 wallets active). Receipts via fast_rpc batch (6, ~4s pause) for 450 "
        "non-approve candidates: 443 status 1, 7 status 0, 0 null, 0 mint-pattern txs. "
        "Status-0 detail: 6x failed contract creations (input 0x60806040) at 17:58:00-17:58:01 WIB by machine wallets "
        "(0xc0768f20... by 0xdb2d83f907, 0xf00de33c... by 0xaa49e7fec5, 0x4cad596c... by 0x3154f69492, "
        "0x89bfc57f... by 0xca4e67bb57, 0x5a2355a9... by 0xc0c84518ce, 0xe031b71d... by 0x97bd895f81) + "
        "1x failed PCS sell 0x791ac947 by 0xc621946845 (0x25a9a429..., 17:42:42 WIB). "
        "AFeng 4 sent txs (3 calls to sale 0x1de460f363af910f51726def188f9004276bf4bc selector 0x4d819a2a - "
        "0.5 BNB 17:42:30 WIB + 0.5 BNB 17:49:53 WIB + value 0 17:56:39 WIB - all WITHOUT mint logs; 1 approve); "
        "future1001.ai 0 txs; 0x2325... 0 txs; 0x8e96... 0 txs. "
        f"Inbound leg per 2026-11-03 12:02 amendment: Ankr getLogs address-filtered per contract, "
        f"{n_contracts} contracts, {n_logs} logs, {n_hits} hit(s), {n_failed} failed, run as a "
        f"(0-400, {ia['total_logs']} logs, {len(ia['hits'])} hits, {len(ia['failed'])} failed, {len(ia['truncated'])} truncated) "
        f"+ b (400-1016, {ib['total_logs']} logs, {len(ib['hits'])} hits, {len(ib['failed'])} failed, {len(ib['truncated'])} truncated), "
        "from ONE frozen contract list (run79-inbound-contracts.json, 1016 contracts, built once before the run - run-78 slice-gap lesson applied, no gap supplement needed). "
        f"{n_hits} hit(s) - NO inbound-only mints this run. "
        f"Failed: {[f['contract'] for f in ia['failed'] + ib['failed']]} - 1 contract (0x47a5569f94c6055edf3e5900402c2c79bcc39dd4, part a, Ankr 'Remote end closed connection without response') - window NOT fully closed; retry run 80 on the same window. "
        f"Truncated {len(trunc)} (all topic-filtered to 0 logs, incl. 0x636f... AFeng tracker, 0x1de4... AFeng sale, 0x6288... AGC sale). "
        "DYOR: contract 0x86956bc830eb62110820ae79164bef61c7e31936 in set (via snapshot), 0 hits - "
        "no tracked wallet minted DYOR in this window. "
        "CORLA 0x4a9c499574ea003846e81522d59aa4c27ca47777, the 4 run-64 ASI contracts, the 4 run-65 "
        "ASI quad-2 contracts, the 2 run-66 tokens, the 2 run-68 tokens, the run-69 token 0x4d15... "
        "the 5 run-70 tokens, the 6 run-71 tokens, the 3 run-72 tokens, the 4 run-73 tokens, the 4 run-74 tokens, "
        "the 3 run-75 tokens, the 2 run-76 tokens, the 3 run-77 tokens, the 2 run-78 tokens "
        "(0xcbbc.../0x41cc... 0 wallets), and GrokBot "
        "0xfcd04501ebaddcda73095a75e078a8e5292f7777 are NOT in the "
        "inbound set (PCS tokens; all their activity was wallet-sent txs covered by the sent pass). "
        "The 2 new run-79 paid tokens are likewise NOT in the inbound set - sent-pass covered. "
        "40 contract creations in window (all by 17 wallets of the 27-wallet machine set; 34 status 1, 6 status 0; "
        "all 40 created addresses READ from receipts this run, saved in run79-deployments.json, and NONE is either of "
        "the 2 new tokens). "
        "No preview/mint/sign/login/purchase by this job. "
        "INFRA NOTES: (1) Inbound part a first attempt never started (parent shell cut off by the exec drain timeout after starting receipts) - restarted as a detached nohup and completed 400/400, 1 failed. "
        "(2) Ankr getLogs slow stretches again in both inbound parts (several ranges minutes without progress line) - slow, not stuck. "
        "(3) No fast_rpc transient read failures recorded this run; all token-verify reads succeeded first try."
    ),
}
s["next_run_note"] = (
    "Next run sent-tx window starts from block 131999044. Dedupe new mints against all tx hashes "
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
    "0xcbbc.../0x41cc... at 27 wallets each), run 79 (TWO tokens "
    "0x5833.../0x32b4... at 27 wallets each) auto-mint BLOCKED at guard (c) "
    "- do not re-signal or re-report the block unless a new mint/buy fact appears for those contracts "
    "(e.g. a genuine free-mint path). Paid fact: run79 max 27 wallets/token (TWO new unnamed tokens, "
    "same byte-identical 27-wallet machine set as runs 63-78 - machine rotated again: run-78 two tokens -> "
    "these two tokens, with run-78 tokens 0xcbbc.../0x41cc... fully quiet (0 wallets) this run; "
    "the other 21 paid tokens max 3 wallets each (10 at 3, 4 at 2, 7 at 1 - usual ...7777 churn); "
    "GrokBot 0xfcd0... absent (0 wallets) this run - 20th consecutive quiet run (59, 61-79) after the run-60 burst; CORLA-97af 0 wallets; CORLA 0x4a9c 0 wallets; all "
    "four run-64 ASI contracts 0 wallets; all four run-65 ASI quad-2 contracts 0 wallets; both run-66 "
    "tokens 0 wallets; both run-68 tokens 0 wallets; run-69 token 0x4d15 0 wallets; all five run-70 "
    "tokens 0 wallets; all six run-71 tokens 0 wallets; all three run-72 tokens 0 wallets; all four "
    "run-73 tokens 0 wallets; all four run-74 tokens 0 wallets; all three run-75 tokens 0 wallets; both run-76 tokens 0 wallets; all three run-77 tokens 0 wallets; both run-78 tokens 0 wallets. "
    "Inbound retry next run: 1 contract - 0x47a5569f94c6055edf3e5900402c2c79bcc39dd4 on window 131992566-131999043 (part a, Ankr 'Remote end closed connection'); window NOT fully closed until it reads OK. "
    "AFeng 4 sent txs this run (3 calls to sale 0x1de4... + 1 approve, no mint logs); future1001.ai 0 txs; 0x2325... 0 txs; 0x8e96... 0 txs. "
    "Same-owner factory groups now also include 0x293f and 0x1103 (proven 2026-11-06 ~01:14 WIB, AGENTS.md) alongside the groups listed in the body."
)
s["paid_signal_run79"] = {
    "note": ("NEW paid-only signal (NOT a buy recommendation, NOT executable Free Bacot, NOT an "
             "auto-mint trigger by itself). Same-machine warning: TWO distinct NEW contracts, bought by the SAME byte-identical 27-wallet set "
             "(27/27, pairwise diff 0, diff 0 vs the run-78 27-set, overlap 27/27) - the set that also bought CORLA (run 63), ASI quad-1 (run 64), "
             "ASI quad-2 (run 65), the two run-66 tokens, the two run-68 tokens, the run-69 token, the "
             "five run-70 tokens, the six run-71 tokens, the three run-72 tokens, the four run-73 tokens, the four run-74 tokens, the three run-75 tokens, the two run-76 tokens, the three run-77 tokens and the two run-78 tokens - the machine rotated again: CORLA (63) -> "
             "ASI quad-1 (64) -> ASI quad-2 (65) -> two unnamed tokens (66) -> quiet (67) -> two new tokens (68) -> one token (69) -> five tokens (70) -> six tokens (71) -> three tokens (72) -> "
             "four tokens (73) -> four tokens (74) -> three tokens (75) -> two tokens (76) -> three tokens (77) -> two tokens (78) -> these two tokens (79). The two are NOT one project - 2 different contracts, never merged. "
             "No partial continuation this run: run-78 tokens 0xcbbc.../0x41cc... went fully quiet (0 wallets)."),
    "project": "NEW paid tokens, same 27-wallet machine set (unnamed)",
    "contracts": [
        "0x5833d3e050c1bcc931ab9967aa4b83052c8c7777",
        "0x32b432ccdd5a3dc7584ee2683bc8a0c200bc7777",
    ],
    "name_symbol_onchain": ("name() and symbol() both return EMPTY strings on-chain for both "
        "(verified via fast_rpc eth_call decode); decimals 18 for both; totalSupply 1e27 "
        "(1,000,000,000,000,000,000,000,000,000) for both; "
        "owner() 0x0 for both; "
        "tokenURI not attempted (no name/symbol identity to resolve, paid PCS tokens - same treatment as run-66/run-68/run-69/run-70/run-71/run-72/run-73/run-74/run-75/run-76/run-77/run-78 tokens)"),
    "participation": ("0x5833 at 27 / 55 wallets (49.1%), 0x32b4 at 27 / 55 wallets (49.1%); "
        "both are 0 wallets in run 78 (new this run); the two 27-wallet sets are BYTE-IDENTICAL (pairwise diff 0, diff 0 vs the run-78 27-set, overlap 27/27); "
        "first tracked buys (selector 0xb6f9de95): "
        "0x32b4 17:36:36 WIB (tx 0xc9b16e9349766a18dc4443a74e92b134542a3e158d85096e9d3b829cedef0767, block 131993861, wallet 0x362396125a, 0.00012169 BNB, ~9,633,602 token, pair 0x77c47b05064cef3b092fa867b1a78b1bd26fdc77), "
        "0x5833 18:04:09 WIB (tx 0x8bf7c4fb36493f5e6f00a1abb7740f540c1c22140b83eb12a805612bb661de30, block 131997533, wallet 0xcb08c02c0a, 0.00012361 BNB, ~9,864,137 token, pair 0xa9717bb3607c72316570aa15d9056f20286497bc); "
        "tracked Transfer logs in window: 58 (0x5833) / 63 (0x32b4); "
        "run-78 tokens 0xcbbc.../0x41cc... 0 wallets (fully quiet); "
        "not previously signaled; not in Free Bacot snapshot; not in bridge (paid-only PCS tokens, per "
        "CORLA/GrokBot/ASI precedent)"),
    "buy_evidence": (
        "Sample PCS buys verified (receipt Transfer from pair + pair token0/token1 on-chain). "
        "Pairs verified on-chain: 0x5833 pair 0xa9717bb3607c72316570aa15d9056f20286497bc (token0 token, token1 WBNB 0xbb4c...); "
        "0x32b4 pair 0x77c47b05064cef3b092fa867b1a78b1bd26fdc77 (token0 token, token1 WBNB). "
        "27-wallet set window totals (all router activity, not per-token; recomputed from sent.json "
        "by literal selectors, matching token-verify.py): 121x buys (0xb6f9de95, total buy value "
        "22.6341 BNB) + 202x sells (0x791ac947) + 203x approve (0x095ea7b3) + 40x contract creations."),
    "linkage": ("NOT verified: the 27 wallets are BYTE-IDENTICAL to the run-63 CORLA / run-64 ASI / "
        "run-65 ASI quad-2 / run-66 two-token / run-68 two-token / run-69 one-token / run-70 "
        "five-token / run-71 six-token / run-72 three-token / run-73 four-token / run-74 four-token / run-75 three-token / run-76 two-token / run-77 three-token / run-78 two-token sets (verified set equality vs run-78: diff 0, overlap 27/27) "
        "and deployed 40 contracts in this window via 17 wallets, which suggests the same "
        "coordinated/machine operator, but no entity collapse is applied - counted per wallet with "
        "this note, as in run 60 GrokBot / run 63 CORLA precedents"),
    "auto_mint_block": ("Trigger >25% met numerically for both (27 >= 14) but BLOCKED at "
        "guard (c): paid PCS tokens, no free-mint quota/path for the user wallet - buying would cost "
        "BNB, never a free mint; guard (a) website also unverified (empty name/symbol, no website "
        "evidence). No preview, no execution. Do not re-report the block unless a genuine free-mint "
        "path appears for these contracts."),
    "deployments_context": ("40 contract-creation txs by 17 of the 27 wallets in this window "
        "(0x1cce4ec5a7 x4, 0xdb2d83f907 x3, 0xaa49e7fec5 x3, 0x5b4beded36 x3, 0x362396125a x3, 0xf9689b9d0a x3, "
        "0x2cc8192fc6 x3, 0x64e893a4c5 x3, 0x97bd895f81 x3, 0x3154f69492 x2, 0xca4e67bb57 x2, 0xc0c84518ce x2, "
        "0x9b519f5d52 x2, 0xc621946845 x1, 0xf795c5250f x1, 0xcb08c02c0a x1, 0xc6591fde9b x1), 34 status 1 + 6 status 0; "
        "all 40 created addresses READ from receipts this run (saved in run79-deployments.json) and NONE is either of "
        "the two new tokens - the new tokens were first bought via PCS pairs, not "
        "deployed in-window by a tracked wallet; token identity (name/symbol) of the 40 created "
        "contracts was NOT checked, so whether any of them is a future machine token is UNVERIFIED"),
}
s["paid_trend_run79"] = {
    "note": "Aggregate only, NOT a buy recommendation. TWO NEW paid-only signals (27 wallets each - see paid_signal_run79); all other tokens far below threshold. ZERO mint-pattern txs this run.",
    "max_wallets_per_token": 27,
    "distribution": "23 paid tokens: 27 wallets x2 (NEW 0x5833.../0x32b4...), 3 wallets x10, 2 wallets x4, 1 wallet x7 (all others ...7777-suffixed churn tokens)",
    "other_paid_activity": [
        {"pattern": "AFeng 4 sent txs (3 calls to sale 0x1de4... selector 0x4d819a2a - 0.5 BNB 17:42:30 WIB + 0.5 BNB 17:49:53 WIB + value 0 17:56:39 WIB, no mint logs; 1 approve); future1001.ai 0 txs; 0x2325... 0 txs; 0x8e96... 0 txs", "wallet": "0xbf004bff64725914ee36d03b87d6965b0ced4903 / 0x355ea9e542b36c645a2dee63b9df079ccb9bf3db / 0x2325f175975abdbcde555c79cc8e63381d28551b / 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6"},
        {"pattern": "7 status-0 receipts: 6 failed contract creations (0x60806040) at 17:58:00-17:58:01 WIB by machine wallets + 1 failed PCS sell 0x791ac947 by 0xc621946845 (17:42:42 WIB)", "wallet": "machine wallets"},
    ],
    "deployments": "40 contract creations in window, all by 17 wallets of the 27-wallet machine set (34 status 1, 6 status 0; see paid_signal_run79 deployments_context)",
    "future1001": "0 tx this run (0x355ea9e542b36c645a2dee63b9df079ccb9bf3db)",
}
s["inbound_log_leg_run79"] = {
    "contracts": n_contracts,
    "total_logs": n_logs,
    "hits": n_hits,
    "failed": n_failed,
    "failed_contracts": [f["contract"] for f in ia["failed"] + ib["failed"]],
    "note": (f"Ankr getLogs address-filtered per contract, window 131992566-131999043, parts a "
             f"(0-400, {ia['total_logs']} logs, {len(ia['hits'])} hits, {len(ia['failed'])} failed, {len(ia['truncated'])} truncated) "
             f"+ b (400-1016, {ib['total_logs']} logs, {len(ib['hits'])} hits, {len(ib['failed'])} failed, {len(ib['truncated'])} truncated), "
             f"from ONE frozen contract list (run79-inbound-contracts.json, 1016 contracts - no slice-gap, no supplement needed). "
             f"{n_hits} hits - 0 NEW inbound-only mints. "
             f"Truncated {len(trunc)} (all topic-filtered to 0 logs). "
             f"Failed {n_failed} - 1 contract (0x47a5569f94c6055edf3e5900402c2c79bcc39dd4, Ankr 'Remote end closed connection'), window NOT fully closed; retry next run. "
             "DYOR 0x8695... in set (via snapshot), 0 hits. No residual open from run 78. CORLA 0x4a9c + 4 run-64 ASI + 4 run-65 ASI quad-2 + the 2 run-66 tokens + the 2 run-68 tokens + the run-69 token + the 5 run-70 tokens + the 6 run-71 tokens + the 3 run-72 tokens + the 4 run-73 tokens + the 4 run-74 tokens + the 3 run-75 tokens + the 2 run-76 tokens + the 3 run-77 tokens + the 2 run-78 tokens + GrokBot 0xfcd0... + the 2 new run-79 tokens not in inbound set (PCS tokens; sent-pass covered). New contracts deployed this hour (40, all "
             "addresses read, none is either of the 2 new tokens) are not in the inbound set - their token "
             "identity (name/symbol) is UNVERIFIED."),
}
sp = s.setdefault("signaled_projects_over_20pct", [])
for new_sig in [
    "Unnamed token (name/symbol empty) 0x5833d3e050c1bcc931ab9967aa4b83052c8c7777 (paid-only, run-79)",
    "Unnamed token (name/symbol empty) 0x32b432ccdd5a3dc7584ee2683bc8a0c200bc7777 (paid-only, run-79)",
]:
    if new_sig not in sp:
        sp.append(new_sig)
json.dump(s, open(P, "w"), indent=1)
print("state updated: run", s["last_run"]["run"])
print(f"inbound: contracts={n_contracts} logs={n_logs} hits={n_hits} failed={n_failed}")
print("paid_signal_run79 + paid_trend_run79 + inbound_log_leg_run79 written; signaled list now", len(sp))
txs = set(); entries = 0
for f in s["reported_findings"]:
    for m in f.get("mints", []):
        entries += 1
        if m.get("tx"):
            txs.add(m["tx"].lower())
print("reported_findings mint entries:", entries, "unique txs:", len(txs))
