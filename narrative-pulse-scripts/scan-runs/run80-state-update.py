#!/usr/bin/env python3
"""Run 80 state update (read-only job bookkeeping; no chain writes).

Completes run 80 (window 131999044-132005906), whose sent/receipts/paid/
token-verify/deployments passes are done and whose inbound leg ran in full
(a 0-400 + b 400-799 [killed by service restart at 400/616, numbers from log]
+ b2 799-1016 resume) from ONE frozen contract list
(run80-inbound-contracts.json = run79 list, 1016 contracts), plus the
run-79 failed-contract retry (0x47a5569f..., 0 logs, 0 hits - run-79 window
now FULLY closed).
"""
import json
import shutil
from pathlib import Path

P = "/home/hatch/workspace/narrative-pulse/tracked-wallet-mint-scan-state.json"
D = Path("/home/hatch/workspace/narrative-pulse/scan-runs")

shutil.copy(P, str(P) + ".bak-run80-pre")
s = json.load(open(P))
ia = json.load(open(D / "run80-inbound-a.json"))
ib2 = json.load(open(D / "run80-inbound-b2.json"))
retry79 = json.load(open(D / "run80-inbound-retry79.json"))
# Part b was killed by a service restart at 400/616; its numbers come from its log.
b_contracts, b_logs, b_trunc = 400, 5288, [
    "0x63dea5acdbe1f27c968907d08610a5f0a0284ba6",
    "0x78573ab46e5436e126d3ea1fdef8766cce4efd2b",
    "0x7e2da878217eb995f9e5d36ed32c9cea52442681",
]
n_contracts_unique = 1016
n_logs = ia["total_logs"] + b_logs + ib2["total_logs"]
n_hits = len(ia["hits"]) + len(ib2["hits"])
n_failed = len(ia["failed"]) + len(ib2["failed"])
trunc = ia["truncated"] + b_trunc + ib2["truncated"]
print(f"inbound totals: unique_contracts={n_contracts_unique} logs={n_logs} hits={n_hits} failed={n_failed} truncated={len(trunc)}")
print(f"retry79: ok={retry79.get('ok')} logs={retry79.get('total_logs')} hits={len(retry79.get('hits', []))}")

s["last_run"] = {
    "run": 80,
    "block_start": 131999044,
    "block_end": 132005906,
    "window_wib": "2026-11-06 18:16:20 - 19:06:59 WIB; sent-pass in-window txs 462, 0 mint-pattern txs",
    "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set)",
    "method_note": (
        "Sent pass Ankr ankr_getTransactionsByAddress via module (55/55, 0 failed; "
        "462 txs, 34 wallets active). Receipts via fast_rpc batch (6, ~4s pause) for 304 "
        "non-approve candidates: batch 0 hit HTTP 403 on all fast_rpc endpoints, race fallback used; "
        "final 301 status 1, 3 status 0, 0 null (1 receipt initially null - 0xa0c0b6561e... PCS buy by "
        "0x3628764a65, 19:03:09 WIB - resolved on retry as status 1, 5 logs, NO Transfer from zero address, "
        "a buy of ...7777 token 0x5d972a038f1c41357ee505d54e3c1b46ecfc7777, NOT a mint), 0 mint-pattern txs. "
        "Status-0 detail: 2x failed PCS buys (0xb6f9de95) by 0xc7c5faa270 at 18:44:32 + 18:49:37 WIB "
        "(tx 0xf8339af8... / 0x50caf853..., both value 0.000135 BNB) + 1x failed PCS sell (0x791ac947) by "
        "0xdb2d83f907 (0x95ddab8c..., 18:24:12 WIB). "
        "AFeng 0 sent txs; future1001.ai 0 txs; 0x2325... 0 txs; 0x8e96... 0 txs. "
        f"Inbound leg per 2026-11-03 12:02 amendment: Ankr getLogs address-filtered per contract, "
        f"{n_contracts_unique} unique contracts, {n_logs} logs summed (1 overlap contract at the b/b2 boundary counted twice), "
        f"{n_hits} hit(s), {n_failed} failed, run as a (0-400, {ia['total_logs']} logs, {len(ia['hits'])} hits, "
        f"{len(ia['failed'])} failed, {len(ia['truncated'])} truncated) + b (400-799, {b_logs} logs from log, 0 hits, "
        f"0 failed, {len(b_trunc)} truncated - KILLED by a service restart at 400/616, no json saved, numbers from log) "
        f"+ b2 (799-1016 resume, {ib2['total_logs']} logs, {len(ib2['hits'])} hits, {len(ib2['failed'])} failed, "
        f"{len(ib2['truncated'])} truncated), from ONE frozen contract list (run80-inbound-contracts.json, 1016 contracts, "
        "same list as run 79 - no new mint contracts to add, machine token not added per precedent). "
        f"{n_hits} hit(s) - NO inbound-only mints this run. "
        f"Truncated {len(trunc)} (all topic-filtered to 0 logs, incl. 0x1de4... AFeng sale, 0x6288... AGC sale, "
        "0x636f... AFeng tracker, 0x55d3... USDT, 0x63de... AGC). "
        f"Retry of the run-79 failed contract 0x47a5569f94c6055edf3e5900402c2c79bcc39dd4 on window 131992566-131999043: "
        f"OK, {retry79.get('total_logs')} logs, {len(retry79.get('hits', []))} hits - the run-79 window is now FULLY CLOSED, no retry needed run 81. "
        "DYOR: contract 0x86956bc830eb62110820ae79164bef61c7e31936 in set (via snapshot), 0 hits - "
        "no tracked wallet minted DYOR in this window. "
        "CORLA 0x4a9c499574ea003846e81522d59aa4c27ca47777, the 4 run-64 ASI contracts, the 4 run-65 "
        "ASI quad-2 contracts, the 2 run-66 tokens, the 2 run-68 tokens, the run-69 token 0x4d15... "
        "the 5 run-70 tokens, the 6 run-71 tokens, the 3 run-72 tokens, the 4 run-73 tokens, the 4 run-74 tokens, "
        "the 3 run-75 tokens, the 2 run-76 tokens, the 3 run-77 tokens, the 2 run-78 tokens, the 2 run-79 tokens "
        "(0x5833.../0x32b4... 0 wallets), and GrokBot "
        "0xfcd04501ebaddcda73095a75e078a8e5292f7777 are NOT in the "
        "inbound set (PCS tokens; all their activity was wallet-sent txs covered by the sent pass). "
        "The new run-80 paid token 0x489e... is likewise NOT in the inbound set - sent-pass covered. "
        "18 contract creations in window (all by 10 wallets of the 27-wallet machine set; all status 1; "
        "all 18 created addresses READ from receipts this run, saved in run80-deployments.json, and NONE is "
        "the new token 0x489e...). "
        "No preview/mint/sign/login/purchase by this job. "
        "INFRA NOTES: (1) Inbound part b killed mid-run by a service restart (runtime) at 400/616 - resumed as b2 "
        "from index 799 (1-contract overlap with b's last processed index, counted twice in summed logs). "
        "(2) fast_rpc batch-0 HTTP 403 on all endpoints at receipts start; race fallback worked, 1 receipt "
        "initially null and resolved on retry (see above). (3) Ankr getLogs slow stretches again in all inbound "
        "parts - slow, not stuck."
    ),
}
s["next_run_note"] = (
    "Next run sent-tx window starts from block 132005907. Dedupe new mints against all tx hashes "
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
    "0x5833.../0x32b4... at 27 wallets each), run 80 (ONE token "
    "0x489e... at 27 wallets) auto-mint BLOCKED at guard (c) "
    "- do not re-signal or re-report the block unless a new mint/buy fact appears for those contracts "
    "(e.g. a genuine free-mint path). Per the 2026-11-06 ~18:30 machine-token fast-path amendment, routine "
    "machine-token rotations are recorded in state WITHOUT a chat report (no full verification per run); "
    "report only on anomaly (buy size far off norm, name/symbol appears, website, or free-mint path). "
    "Paid fact: run80 max 27 wallets/token (ONE new unnamed token 0x489e..., same byte-identical 27-wallet machine set as runs 63-79 - machine rotated again: run-79 two tokens -> this one token, with run-79 tokens 0x5833.../0x32b4... fully quiet (0 wallets) this run; "
    "the other 36 paid tokens max 3 wallets each (12 at 3, 14 at 2, 10 at 1 - usual ...7777 churn); "
    "GrokBot 0xfcd0... absent (0 wallets) this run - 21st consecutive quiet run (59, 61-80) after the run-60 burst; CORLA-97af 0 wallets; CORLA 0x4a9c 0 wallets; all "
    "four run-64 ASI contracts 0 wallets; all four run-65 ASI quad-2 contracts 0 wallets; both run-66 "
    "tokens 0 wallets; both run-68 tokens 0 wallets; run-69 token 0x4d15 0 wallets; all five run-70 "
    "tokens 0 wallets; all six run-71 tokens 0 wallets; all three run-72 "
    "tokens 0 wallets; all four run-73 tokens 0 wallets; all four run-74 tokens 0 wallets; all three run-75 tokens 0 wallets; both run-76 tokens 0 wallets; all three run-77 tokens 0 wallets; both run-78 tokens 0 wallets; both run-79 tokens 0 wallets. "
    "No inbound retry needed run 81 - run-79 window fully closed (retry79 OK, 0 logs, 0 hits) and run-80 window fully closed (0 failed). "
    "AFeng 0 sent txs this run; future1001.ai 0 txs; 0x2325... 0 txs; 0x8e96... 0 txs. "
    "Same-owner factory groups now also include 0x293f and 0x1103 (proven 2026-11-06 ~01:14 WIB, AGENTS.md) alongside the groups listed in the body."
)
s["paid_signal_run80"] = {
    "note": ("NEW paid-only machine-token rotation (NOT a buy recommendation, NOT executable Free Bacot, NOT an "
             "auto-mint trigger by itself). ONE distinct NEW contract, bought by the SAME byte-identical 27-wallet set "
             "(27/27, diff 0 vs the run-79 27-set, overlap 27/27) - the set that also bought CORLA (run 63), ASI quad-1 (run 64), "
             "ASI quad-2 (run 65), the two run-66 tokens, the two run-68 tokens, the run-69 token, the "
             "five run-70 tokens, the six run-71 tokens, the three run-72 tokens, the four run-73 tokens, the four run-74 tokens, the three run-75 tokens, the two run-76 tokens, the three run-77 tokens, the two run-78 tokens and the two run-79 tokens - the machine rotated again: CORLA (63) -> "
             "ASI quad-1 (64) -> ASI quad-2 (65) -> two unnamed tokens (66) -> quiet (67) -> two new tokens (68) -> one token (69) -> five tokens (70) -> six tokens (71) -> three tokens (72) -> "
             "four tokens (73) -> four tokens (74) -> three tokens (75) -> two tokens (76) -> three tokens (77) -> two tokens (78) -> two tokens (79) -> this one token (80). "
             "No partial continuation this run: run-79 tokens 0x5833.../0x32b4... went fully quiet (0 wallets). "
             "NO CHAT REPORT for this rotation per the 2026-11-06 ~18:30 machine-token fast-path amendment: routine rotation, "
             "no anomaly (buy-size shape matches run 79, no name/symbol, no website, no free-mint path) - recorded in state only."),
    "project": "NEW paid token, same 27-wallet machine set (unnamed)",
    "contracts": [
        "0x489e9bba4d7599aba33dacb2c0dfef4f64f17777",
    ],
    "name_symbol_onchain": ("name() and symbol() both return EMPTY strings on-chain "
        "(verified via fast_rpc eth_call decode); decimals 18; totalSupply 1e27 "
        "(1,000,000,000,000,000,000,000,000,000); "
        "owner() 0x0; "
        "tokenURI not attempted (no name/symbol identity to resolve, paid PCS token - same treatment as run-66/run-68/run-69/run-70/run-71/run-72/run-73/run-74/run-75/run-76/run-77/run-78/run-79 tokens)"),
    "participation": ("0x489e at 27 / 55 wallets (49.1%); "
        "0 wallets in run 79 (new this run); the 27-wallet set is BYTE-IDENTICAL to the run-79 set (diff 0, overlap 27/27); "
        "first tracked buy (selector 0xb6f9de95): "
        "0x489e 18:23:38 WIB (tx 0xd3372f4a0b9852eea1b1923120e9575b78beff695a8570b46f1acc37d37d1a32, block 132000129, wallet 0xcb08c02c0a, 0.000106082874383268 BNB, ~8,465,055 token, pair 0x3f8a7a3df307c5638073de86e0ceb42103706d66); "
        "tracked Transfer logs in window: 55 (0x489e); "
        "run-79 tokens 0x5833.../0x32b4... 0 wallets (fully quiet); "
        "not previously signaled; not in Free Bacot snapshot; not in bridge (paid-only PCS token, per "
        "CORLA/GrokBot/ASI precedent)"),
    "buy_evidence": (
        "Sample PCS buys verified (receipt Transfer from pair + pair token0/token1 on-chain). "
        "Pair verified on-chain: 0x489e pair 0x3f8a7a3df307c5638073de86e0ceb42103706d66 (token0 token, token1 WBNB 0xbb4c...). "
        "Buy-size shape (verified, NOT anomalous vs run 79): first buy per token ~0.000106 BNB (norm ~0.000114 BNB); "
        "follow-up buys 0.1340-0.3743 BNB, median ~0.23 BNB - same shape as run 79 (median 0.2256 BNB, max 0.4395 BNB, "
        "only 4 of 121 buys < 0.001 BNB). 27-set window totals (all router activity, recomputed from sent.json "
        "by literal selectors, matching token-verify.py): 55x buys (0xb6f9de95, total buy value "
        "9.9472 BNB) + 99x sells (0x791ac947) + 98x approve (0x095ea7b3) + 18x contract creations."),
    "linkage": ("NOT verified: the 27 wallets are BYTE-IDENTICAL to the run-63 CORLA / run-64 ASI / "
        "run-65 ASI quad-2 / run-66 two-token / run-68 two-token / run-69 one-token / run-70 "
        "five-token / run-71 six-token / run-72 three-token / run-73 four-token / run-74 four-token / run-75 three-token / run-76 two-token / run-77 three-token / run-78 two-token / run-79 two-token sets (verified set equality vs run-79: diff 0, overlap 27/27) "
        "and deployed 18 contracts in this window via 10 wallets, which suggests the same "
        "coordinated/machine operator, but no entity collapse is applied - counted per wallet with "
        "this note, as in run 60 GrokBot / run 63 CORLA precedents"),
    "auto_mint_block": ("Trigger >25% met numerically (27 >= 14) but BLOCKED at "
        "guard (c): paid PCS token, no free-mint quota/path for the user wallet - buying would cost "
        "BNB, never a free mint; guard (a) website also unverified (empty name/symbol, no website "
        "evidence). No preview, no execution. Do not re-report the block unless a genuine free-mint "
        "path appears for this contract."),
    "deployments_context": ("18 contract-creation txs by 10 of the 27 wallets in this window "
        "(0x97bd895f81 x3, 0xaa49e7fec5 x2, 0x3154f69492 x2, 0x5b4beded36 x2, 0x1cce4ec5a7 x2, 0xc0c84518ce x2, "
        "0x64e893a4c5 x2, 0xdb2d83f907 x1, 0xca4e67bb57 x1, 0x9b519f5d52 x1), all status 1; "
        "all 18 created addresses READ from receipts this run (saved in run80-deployments.json) and NONE is "
        "the new token - the new token was first bought via PCS pair, not "
        "deployed in-window by a tracked wallet; token identity (name/symbol) of the 18 created "
        "contracts was NOT checked, so whether any of them is a future machine token is UNVERIFIED"),
}
s["paid_trend_run80"] = {
    "note": "Aggregate only, NOT a buy recommendation. ONE NEW paid-only machine-token rotation (27 wallets - see paid_signal_run80, recorded in state WITHOUT chat report per the 2026-11-06 ~18:30 fast-path amendment); all other tokens far below threshold. ZERO mint-pattern txs this run.",
    "max_wallets_per_token": 27,
    "distribution": "37 paid tokens: 27 wallets x1 (NEW 0x489e...), 3 wallets x12, 2 wallets x14, 1 wallet x10 (all others ...7777-suffixed churn tokens)",
    "other_paid_activity": [
        {"pattern": "AFeng 0 sent txs; future1001.ai 0 txs; 0x2325... 0 txs; 0x8e96... 0 txs", "wallet": "0xbf004bff64725914ee36d03b87d6965b0ced4903 / 0x355ea9e542b36c645a2dee63b9df079ccb9bf3db / 0x2325f175975abdbcde555c79cc8e63381d28551b / 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6"},
        {"pattern": "3 status-0 receipts: 2 failed PCS buys (0xb6f9de95) by 0xc7c5faa270 (18:44:32 + 18:49:37 WIB, 0.000135 BNB each) + 1 failed PCS sell (0x791ac947) by 0xdb2d83f907 (18:24:12 WIB); 1 receipt initially null (0xa0c0b656..., PCS buy by 0x3628764a65, 19:03:09 WIB) resolved on retry as status 1, not a mint", "wallet": "machine/churn wallets"},
    ],
    "deployments": "18 contract creations in window, all by 10 wallets of the 27-wallet machine set (all status 1; see paid_signal_run80 deployments_context)",
    "future1001": "0 tx this run (0x355ea9e542b36c645a2dee63b9df079ccb9bf3db)",
}
s["inbound_log_leg_run80"] = {
    "contracts": n_contracts_unique,
    "total_logs": n_logs,
    "hits": n_hits,
    "failed": n_failed,
    "failed_contracts": [],
    "note": (f"Ankr getLogs address-filtered per contract, window 131999044-132005906, parts a "
             f"(0-400, {ia['total_logs']} logs, {len(ia['hits'])} hits, {len(ia['failed'])} failed, {len(ia['truncated'])} truncated) "
             f"+ b (400-799, {b_logs} logs from log, 0 hits, 0 failed, {len(b_trunc)} truncated - killed by service restart at 400/616, no json) "
             f"+ b2 (799-1016 resume, {ib2['total_logs']} logs, {len(ib2['hits'])} hits, {len(ib2['failed'])} failed, {len(ib2['truncated'])} truncated), "
             f"from ONE frozen contract list (run80-inbound-contracts.json, 1016 contracts - same list as run 79, no slice-gap in unique coverage). "
             f"{n_hits} hits - 0 NEW inbound-only mints. "
             f"Truncated {len(trunc)} (all topic-filtered to 0 logs). "
             f"Failed {n_failed} - none; window FULLY closed, no retry needed run 81. "
             f"Retry of run-79 failed contract 0x47a5569f94c6055edf3e5900402c2c79bcc39dd4 on window 131992566-131999043: OK, "
             f"{retry79.get('total_logs')} logs, {len(retry79.get('hits', []))} hits - run-79 window FULLY CLOSED. "
             "DYOR 0x8695... in set (via snapshot), 0 hits. No residual open from run 79. CORLA 0x4a9c + 4 run-64 ASI + 4 run-65 ASI quad-2 + the 2 run-66 tokens + the 2 run-68 tokens + the run-69 token + the 5 run-70 tokens + the 6 run-71 tokens + the 3 run-72 tokens + the 4 run-73 tokens + the 4 run-74 tokens + the 3 run-75 tokens + the 2 run-76 tokens + the 3 run-77 tokens + the 2 run-78 tokens + the 2 run-79 tokens + GrokBot 0xfcd0... + the new run-80 token not in inbound set (PCS tokens; sent-pass covered). New contracts deployed this hour (18, all addresses read, none is the new token) are not in the inbound set - their token identity (name/symbol) is UNVERIFIED."),
}
mt = s.setdefault("machine_tokens", [])
mt.append({
    "address": "0x489e9bba4d7599aba33dacb2c0dfef4f64f17777",
    "first_seen": "run-80, 2026-11-06 18:23:38 WIB (tx 0xd3372f4a0b9852eea1b1923120e9575b78beff695a8570b46f1acc37d37d1a32, block 132000129)",
    "machine_wallets": 27,
    "typical_first_buy_bnb": 0.000106082874383268,
    "followup_buy_range_bnb": "0.1340-0.3743",
    "label": "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB)",
    "note": "Routine rotation, no anomaly; recorded in state WITHOUT chat report per fast-path amendment. No name/symbol, no website, no free-mint path. Auto-mint blocked at guard (c).",
})
sp = s.setdefault("signaled_projects_over_20pct", [])
new_sig = "Unnamed token (name/symbol empty) 0x489e9bba4d7599aba33dacb2c0dfef4f64f17777 (paid-only, machine-token, run-80, no chat report per fast-path amendment)"
if new_sig not in sp:
    sp.append(new_sig)
json.dump(s, open(P, "w"), indent=1)
print("state updated: run", s["last_run"]["run"])
print(f"inbound: unique_contracts={n_contracts_unique} logs={n_logs} hits={n_hits} failed={n_failed}")
print("paid_signal_run80 + paid_trend_run80 + inbound_log_leg_run80 written; machine_tokens now", len(mt), "; signaled list now", len(sp))
txs = set(); entries = 0
for f in s["reported_findings"]:
    for m in f.get("mints", []):
        entries += 1
        if m.get("tx"):
            txs.add(m["tx"].lower())
print("reported_findings mint entries:", entries, "unique txs:", len(txs))
