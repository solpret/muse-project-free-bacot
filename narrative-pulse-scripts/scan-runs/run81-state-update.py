#!/usr/bin/env python3
"""Run 81 state update (read-only job bookkeeping; no chain writes).

Completes run 81 (window 132005907-132014631), whose sent/receipts/paid/
token-verify/deployments passes are done and whose inbound leg ran in full
(a 0-400 + b 400-1016) from ONE frozen contract list
(run81-inbound-contracts.json = run80 list, 1016 contracts).
"""
import json
import shutil
from pathlib import Path

P = "/home/hatch/workspace/narrative-pulse/tracked-wallet-mint-scan-state.json"
D = Path("/home/hatch/workspace/narrative-pulse/scan-runs")

shutil.copy(P, str(P) + ".bak-run81-pre")
s = json.load(open(P))
ia = json.load(open(D / "run81-inbound-a.json"))
ib = json.load(open(D / "run81-inbound-b.json"))
n_contracts_unique = 1016
n_logs = ia["total_logs"] + ib["total_logs"]
n_hits = len(ia["hits"]) + len(ib["hits"])
n_failed = len(ia["failed"]) + len(ib["failed"])
trunc = ia["truncated"] + ib["truncated"]
print(f"inbound totals: unique_contracts={n_contracts_unique} logs={n_logs} hits={n_hits} failed={n_failed} truncated={len(trunc)}")

s["last_run"] = {
    "run": 81,
    "block_start": 132005907,
    "block_end": 132014631,
    "window_wib": "2026-11-06 19:08:05 - 20:12:26 WIB; sent-pass in-window txs 702, 0 mint-pattern txs",
    "wallets_checked": "54/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set); 1 wallet FAILED sent pass: 0x5b2f11cab406f580a7c6faf620ee35daaf8648a5 (Ankr 'Remote end closed connection without response') - its activity this window is UNVERIFIED, retry run 82, never reported as 0 activity",
    "method_note": (
        "Sent pass Ankr ankr_getTransactionsByAddress via module (54/55, 1 failed; "
        "702 txs, 36 wallets active). Receipts via fast_rpc batch (6, ~4s pause) for 452 "
        "non-approve candidates: final 439 status 1, 13 status 0, 0 null, 0 mint-pattern txs. "
        "Status-0 detail: 10x failed calls (0xef7ec2e7) by 0x8e96... via 0xe2ce6ab80874fa9fa2aae65d277dd6b8e65c9de0 "
        "at 19:39:25-19:46:12 WIB, value 0 (that wallet's ENTIRE window activity - 10/10 failed) + 3x failed PCS sells "
        "(0x791ac947) by 0xdb2d83f907 (19:46:03 WIB), 0xc621946845 (19:51:36 WIB), 0xa952331ea4 (20:06:07 WIB), value 0. "
        "AFeng 5 sent txs (3x calls to 0x1de4... sale contract + 2x approves); future1001.ai 0 txs; 0x2325... 0 txs. "
        f"Inbound leg per 2026-11-03 12:02 amendment: Ankr getLogs address-filtered per contract, "
        f"{n_contracts_unique} unique contracts, {n_logs} logs summed, "
        f"{n_hits} hit(s), {n_failed} failed, run as a (0-400, {ia['total_logs']} logs, {len(ia['hits'])} hits, "
        f"{len(ia['failed'])} failed, {len(ia['truncated'])} truncated) "
        f"+ b (400-1016, {ib['total_logs']} logs, {len(ib['hits'])} hits, "
        f"{len(ib['failed'])} failed, {len(ib['truncated'])} truncated), from ONE frozen contract list (run81-inbound-contracts.json, 1016 contracts, "
        "same list as run 80 - no new mint contracts to add, machine tokens not added per precedent). "
        f"{n_hits} hit(s) - NO inbound-only mints this run. "
        f"Truncated {len(trunc)} (all topic-filtered to 0 logs, incl. 0x1de4... AFeng sale, 0x6288... AGC sale, "
        "0x636f... AFeng tracker, 0x55d3... USDT, 0x63de... AGC). "
        "DYOR: contract 0x86956bc830eb62110820ae79164bef61c7e31936 in set (via snapshot), 0 hits - "
        "no tracked wallet minted DYOR in this window. "
        "CORLA 0x4a9c499574ea003846e81522d59aa4c27ca47777, the 4 run-64 ASI contracts, the 4 run-65 "
        "ASI quad-2 contracts, the 2 run-66 tokens, the 2 run-68 tokens, the run-69 token 0x4d15... "
        "the 5 run-70 tokens, the 6 run-71 tokens, the 3 run-72 tokens, the 4 run-73 tokens, the 4 run-74 tokens, "
        "the 3 run-75 tokens, the 2 run-76 tokens, the 3 run-77 tokens, the 2 run-78 tokens, the 2 run-79 tokens, "
        "the run-80 token 0x489e... and GrokBot "
        "0xfcd04501ebaddcda73095a75e078a8e5292f7777 are NOT in the "
        "inbound set (PCS tokens; all their activity was wallet-sent txs covered by the sent pass). "
        "The two new run-81 paid tokens 0x7f7a.../0x33f7... are likewise NOT in the inbound set - sent-pass covered. "
        "10 contract creations in window (all by 9 wallets of the 27-wallet machine set; all status 1; "
        "all 10 created addresses READ from local receipts this run, saved in run81-deployments.json, and NONE is "
        "either new token). "
        "No preview/mint/sign/login/purchase by this job. "
        "INFRA NOTES: (1) fast_rpc was DOWN on all endpoints for ~15 min mid-run (during token-verify pair reads and "
        "the first-tx lookups): eth_getTransaction + eth_call both 'all endpoints failed' - transient, NOT absence; "
        "pair token0/token1 + first-buy values were recovered from local receipts/Ankr logs instead, and fast_rpc "
        "recovered before the deployments read (pair reads re-verified after recovery). Ankr getTransactionsByHash "
        "returned 'transaction not found' for the two distributor txs (method/index gap, not proof the txs do not exist - "
        "both txs are confirmed by Ankr getLogs + getTransactionsByAddress). (2) Ankr getLogs slow stretches again in "
        "inbound part a (no failures). (3) Sent-pass wallet 0x5b2f11ca failed (see wallets_checked) - retry run 82."
    ),
}
s["next_run_note"] = (
    "Next run sent-tx window starts from block 132014632. RETRY run 82: sent pass for 0x5b2f11cab406f580a7c6faf620ee35daaf8648a5 "
    "(failed run 81, Ankr 'Remote end closed connection') - its run-81 window activity is UNVERIFIED, do not report as 0. "
    "Dedupe new mints against all tx hashes in reported_findings (223 mint entries over 221 unique tx hashes, direct count run 77 - the run-75 log's 223 was the mint-entry count, not unique txs; dedupe by tx hash). "
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
    "0x489e... at 27 wallets), run 81 (TWO tokens "
    "0x7f7a.../0x33f7... at 27 wallets each) auto-mint BLOCKED at guard (c) "
    "- do not re-signal or re-report the block unless a new mint/buy fact appears for those contracts "
    "(e.g. a genuine free-mint path). Per the 2026-11-06 ~18:30 machine-token fast-path amendment, routine "
    "machine-token rotations are recorded in state WITHOUT a chat report (no full verification per run); "
    "report only on anomaly (buy size far off norm, name/symbol appears, website, or free-mint path). "
    "Paid fact: run81 max 27 wallets/token (TWO new unnamed tokens 0x7f7a.../0x33f7..., same byte-identical 27-wallet machine set as runs 63-80 - machine rotated again: run-80 one token -> these two tokens, with run-80 token 0x489e... fully quiet (0 wallets) this run; "
    "the other 34 paid tokens max 3 wallets each (20 at 3, 7 at 2, 7 at 1 - usual ...7777 churn); "
    "GrokBot 0xfcd0... absent (0 wallets) this run - 22nd consecutive quiet run (59, 61-81) after the run-60 burst; CORLA-97af 0 wallets; CORLA 0x4a9c 0 wallets; all "
    "four run-64 ASI contracts 0 wallets; all four run-65 ASI quad-2 contracts 0 wallets; both run-66 "
    "tokens 0 wallets; both run-68 tokens 0 wallets; run-69 token 0x4d15 0 wallets; all five run-70 "
    "tokens 0 wallets; all six run-71 tokens 0 wallets; all three run-72 "
    "tokens 0 wallets; all four run-73 tokens 0 wallets; all four run-74 tokens 0 wallets; all three run-75 tokens 0 wallets; both run-76 tokens 0 wallets; all three run-77 tokens 0 wallets; both run-78 tokens 0 wallets; both run-79 tokens 0 wallets; run-80 token 0x489e... 0 wallets. "
    "NEW run-81 oddity (recorded, NOT a chat report - not a listed fast-path anomaly): the FIRST tracked Transfer of EACH new token was a bulk-distribution transfer TO AFeng (0xbf004bff64), not a machine buy - 0x7f7a 20,304.550610120954 tokens in tx 0xc268a346c0da7113c8276f31ad80464330f66bb24dc6aeac459e56ecdc3ee1d9 (block 132013391) from distributor contract 0xb31dfeb4364248a802bd3d439b824bb83280a074, called by 0x81d1d8d050c4c86123e0ec05a8a047f317d58818 via selector 0x025ff12f (long recipient list); 0x33f7 45,042.9657665813 tokens in tx 0xc9fd6b5d72f67360cd8737e2234eda02d9282cc4a7a7e43ce9a8800b0e381351 (block 132011011) from distributor 0x231eb7398ea4639da75940a47ce914cc5cb5e4b3, called by 0x595a51a774193919df05cbcb4819c6c193316dec. Both distributor contracts have identical bytecode size (25,620 bytes); neither caller is in the tracked set; AFeng sent no tx for these (its 5 in-window txs were 0x1de4... sale calls + approves). NOT a free-mint path for the user wallet (recipient was AFeng, chosen by the caller) and no name/symbol/website appeared - machine-token label stands. "
    "AFeng 5 sent txs this run; future1001.ai 0 txs; 0x2325... 0 txs; 0x8e96... 10 txs, ALL failed (0xef7ec2e7 via 0xe2ce6ab808...). "
    "Same-owner factory groups now also include 0x293f and 0x1103 (proven 2026-11-06 ~01:14 WIB, AGENTS.md) alongside the groups listed in the body."
)
s["paid_signal_run81"] = {
    "note": ("NEW paid-only machine-token rotation (NOT a buy recommendation, NOT executable Free Bacot, NOT an "
             "auto-mint trigger by itself). TWO distinct NEW contracts, bought by the SAME byte-identical 27-wallet set "
             "(27/27 each, diff 0 vs the run-80 27-set, overlap 27/27; the two sets are identical to each other too) - the set that also bought CORLA (run 63), ASI quad-1 (run 64), "
             "ASI quad-2 (run 65), the two run-66 tokens, the two run-68 tokens, the run-69 token, the "
             "five run-70 tokens, the six run-71 tokens, the three run-72 tokens, the four run-73 tokens, the four run-74 tokens, the three run-75 tokens, the two run-76 tokens, the three run-77 tokens, the two run-78 tokens, the two run-79 tokens and the run-80 token - the machine rotated again: CORLA (63) -> "
             "ASI quad-1 (64) -> ASI quad-2 (65) -> two unnamed tokens (66) -> quiet (67) -> two new tokens (68) -> one token (69) -> five tokens (70) -> six tokens (71) -> three tokens (72) -> "
             "four tokens (73) -> four tokens (74) -> three tokens (75) -> two tokens (76) -> three tokens (77) -> two tokens (78) -> two tokens (79) -> one token (80) -> these two tokens (81). "
             "No partial continuation this run: run-80 token 0x489e... went fully quiet (0 wallets). "
             "NO CHAT REPORT for this rotation per the 2026-11-06 ~18:30 machine-token fast-path amendment: routine rotation, "
             "no anomaly in a listed class (buy-size shape matches run 80, no name/symbol, no website, no free-mint path) - recorded in state only. "
             "One NEW oddity recorded (not a listed anomaly, not reported): the first tracked Transfer of each token was a bulk-distribution transfer to AFeng - see next_run_note."),
    "project": "NEW paid tokens, same 27-wallet machine set (unnamed, two tokens)",
    "contracts": [
        "0x7f7a40246cbf443e6b6359b1defb81b0098f7777",
        "0x33f7f143e69b451fa5245b525705c7306a867777",
    ],
    "name_symbol_onchain": ("name() and symbol() both return EMPTY strings on-chain for BOTH tokens "
        "(verified via fast_rpc eth_call decode); decimals 18; totalSupply 1e27 "
        "(1,000,000,000,000,000,000,000,000,000) each; "
        "owner() 0x0 for both; "
        "tokenURI not attempted (no name/symbol identity to resolve, paid PCS tokens - same treatment as run-66/run-68/run-69/run-70/run-71/run-72/run-73/run-74/run-75/run-76/run-77/run-78/run-79/run-80 tokens)"),
    "participation": ("0x7f7a at 27 / 55 wallets (49.1%); 0x33f7 at 27 / 55 wallets (49.1%); "
        "0 wallets for both in run 80 (new this run); the 27-wallet set is BYTE-IDENTICAL to the run-80 set (diff 0, overlap 27/27) and identical between the two tokens (diff 0, overlap 27/27); "
        "first tracked PCS buy (selector 0xb6f9de95): "
        "0x7f7a 20:03:23 WIB (tx 0x6b209b944f47..., block 132013423, wallet 0xcb08c02c0a, 0.000123616835355714 BNB, ~9,863.94 token, pair 0xd7fda218fb04e148d5c4c85d6cd1f658dd0a40b1); "
        "0x33f7 19:45:29 WIB (tx 0xcab44fc09003..., block 132011038, wallet 0xcb08c02c0a, 0.000111925572639837 BNB, ~8,931.26 token, pair 0xfcf13a7a4533d5c448c726c11aa494e9b41b4c38); "
        "tracked Transfer logs in window: 56 (0x7f7a, 55 from its pair + 1 distribution to AFeng) / 54 (0x33f7, 53 from its pair + 1 distribution to AFeng); "
        "run-80 token 0x489e... 0 wallets (fully quiet); "
        "not previously signaled; not in Free Bacot snapshot (grep 0); not in bridge (paid-only PCS tokens, per "
        "CORLA/GrokBot/ASI precedent)"),
    "buy_evidence": (
        "Sample PCS buys verified (receipt Transfer from pair + pair token0/token1 on-chain). "
        "Pairs verified on-chain: 0x7f7a pair 0xd7fda218fb04e148d5c4c85d6cd1f658dd0a40b1 (token0 token, token1 WBNB 0xbb4c...); "
        "0x33f7 pair 0xfcf13a7a4533d5c448c726c11aa494e9b41b4c38 (token0 token, token1 WBNB 0xbb4c...). "
        "Buy-size shape (verified from sent.json + Ankr topic-filtered logs, NOT anomalous vs run 80): first buys ~0.000112-0.000124 BNB (norm ~0.000114 BNB); "
        "0x7f7a buys (n=51 matched): min 0.0001235, median 0.2233621, max 0.371685914870312 BNB; "
        "0x33f7 buys (n=53 matched): min 0.000111925572639837, median 0.23087033818308048, max 0.3716723777202687 BNB - same shape as run 80 (median ~0.23 BNB, max ~0.37-0.44 BNB). "
        "27-set window totals (all router activity, recomputed from sent.json by literal selectors, matching token-verify.py): 104x buys (0xb6f9de95, total buy value "
        "18.4495 BNB) + 179x sells (0x791ac947) + 176x approve (0x095ea7b3) + 10x contract creations."),
    "linkage": ("NOT verified: the 27 wallets are BYTE-IDENTICAL to the run-63 CORLA / run-64 ASI / "
        "run-65 ASI quad-2 / run-66 two-token / run-68 two-token / run-69 one-token / run-70 "
        "five-token / run-71 six-token / run-72 three-token / run-73 four-token / run-74 four-token / run-75 three-token / run-76 two-token / run-77 three-token / run-78 two-token / run-79 two-token / run-80 one-token sets (verified set equality vs run-80: diff 0, overlap 27/27) "
        "and deployed 10 contracts in this window via 9 wallets, which suggests the same "
        "coordinated/machine operator, but no entity collapse is applied - counted per wallet with "
        "this note, as in run 60 GrokBot / run 63 CORLA precedents"),
    "auto_mint_block": ("Trigger >25% met numerically (27 >= 14) but BLOCKED at "
        "guard (c): paid PCS tokens, no free-mint quota/path for the user wallet - buying would cost "
        "BNB, never a free mint; guard (a) website also unverified (empty name/symbol, no website "
        "evidence). No preview, no execution. Do not re-report the block unless a genuine free-mint "
        "path appears for these contracts."),
    "deployments_context": ("10 contract-creation txs by 9 of the 27 wallets in this window "
        "(0x97bd895f81 x2, 0xdb2d83f907 x1, 0xaa49e7fec5 x1, 0x3154f69492 x1, 0xcb08c02c0a x1, 0x5b4beded36 x1, "
        "0x1cce4ec5a7 x1, 0xc0c84518ce x1, 0x64e893a4c5 x1), all status 1, all at 20:01:52-20:01:58 WIB; "
        "all 10 created addresses READ from local receipts this run (saved in run81-deployments.json) and NONE is "
        "either new token - the new tokens were first bought via PCS pairs, not "
        "deployed in-window by a tracked wallet; token identity (name/symbol) of the 10 created "
        "contracts was NOT checked, so whether any of them is a future machine token is UNVERIFIED"),
    "afeng_distribution_oddity": (
        "First tracked Transfer of EACH new token was a bulk-distribution transfer TO AFeng (0xbf004bff64725914ee36d03b87d6965b0ced4903), not a machine buy: "
        "0x7f7a 20,304.550610120954 tokens, tx 0xc268a346c0da7113c8276f31ad80464330f66bb24dc6aeac459e56ecdc3ee1d9, block 132013391, from distributor contract "
        "0xb31dfeb4364248a802bd3d439b824bb83280a074, called by 0x81d1d8d050c4c86123e0ec05a8a047f317d58818 via selector 0x025ff12f (calldata = token + long recipient/amount list); "
        "0x33f7 45,042.9657665813 tokens, tx 0xc9fd6b5d72f67360cd8737e2234eda02d9282cc4a7a7e43ce9a8800b0e381351, block 132011011, from distributor "
        "0x231eb7398ea4639da75940a47ce914cc5cb5e4b3, called by 0x595a51a774193919df05cbcb4819c6c193316dec via the same selector. "
        "Both distributor contracts have code (25,620 bytes each, identical size); neither caller is in the tracked set; AFeng sent neither tx "
        "(its 5 in-window txs were 0x1de4... sale calls + approves). This is a transfer to a third-party wallet chosen by the caller, NOT a free-mint path "
        "for the user wallet, and it changes nothing about the machine-token label (no name/symbol, no website, buy sizes normal). Recorded here for transparency; "
        "not a listed fast-path anomaly, so no chat report."),
}
s["paid_trend_run81"] = {
    "note": "Aggregate only, NOT a buy recommendation. TWO NEW paid-only machine-token rotations (27 wallets each - see paid_signal_run81, recorded in state WITHOUT chat report per the 2026-11-06 ~18:30 fast-path amendment); all other tokens far below threshold. ZERO mint-pattern txs this run. One sent-pass wallet failed (0x5b2f11ca) - its activity is UNVERIFIED, retry run 82.",
    "max_wallets_per_token": 27,
    "distribution": "36 paid tokens: 27 wallets x2 (NEW 0x7f7a... + 0x33f7...), 3 wallets x20, 2 wallets x7, 1 wallet x7 (all others ...7777-suffixed churn tokens)",
    "other_paid_activity": [
        {"pattern": "AFeng 5 sent txs (3x 0x1de4... sale calls + 2x approves); future1001.ai 0 txs; 0x2325... 0 txs; 0x8e96... 10 txs, ALL failed (0xef7ec2e7 via 0xe2ce6ab808...)", "wallet": "0xbf004bff64725914ee36d03b87d6965b0ced4903 / 0x355ea9e542b36c645a2dee63b9df079ccb9bf3db / 0x2325f175975abdbcde555c79cc8e63381d28551b / 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6"},
        {"pattern": "13 status-0 receipts: 10 failed calls (0xef7ec2e7) by 0x8e96... (19:39:25-19:46:12 WIB, value 0) + 3 failed PCS sells (0x791ac947) by 0xdb2d83f907 (19:46:03 WIB), 0xc621946845 (19:51:36 WIB), 0xa952331ea4 (20:06:07 WIB)", "wallet": "machine/churn wallets"},
    ],
    "deployments": "10 contract creations in window, all by 9 wallets of the 27-wallet machine set (all status 1, 20:01:52-20:01:58 WIB; see paid_signal_run81 deployments_context)",
    "future1001": "0 tx this run (0x355ea9e542b36c645a2dee63b9df079ccb9bf3db)",
}
s["inbound_log_leg_run81"] = {
    "contracts": n_contracts_unique,
    "total_logs": n_logs,
    "hits": n_hits,
    "failed": n_failed,
    "failed_contracts": [],
    "note": (f"Ankr getLogs address-filtered per contract, window 132005907-132014631, parts a "
             f"(0-400, {ia['total_logs']} logs, {len(ia['hits'])} hits, {len(ia['failed'])} failed, {len(ia['truncated'])} truncated) "
             f"+ b (400-1016, {ib['total_logs']} logs, {len(ib['hits'])} hits, {len(ib['failed'])} failed, {len(ib['truncated'])} truncated), "
             f"from ONE frozen contract list (run81-inbound-contracts.json, 1016 contracts - same list as run 80, no slice-gap in unique coverage). "
             f"{n_hits} hits - 0 NEW inbound-only mints. "
             f"Truncated {len(trunc)} (all topic-filtered to 0 logs). "
             f"Failed {n_failed} - none; window FULLY closed, no retry needed run 82 for the inbound leg. "
             "DYOR 0x8695... in set (via snapshot), 0 hits. CORLA 0x4a9c + 4 run-64 ASI + 4 run-65 ASI quad-2 + the 2 run-66 tokens + the 2 run-68 tokens + the run-69 token + the 5 run-70 tokens + the 6 run-71 tokens + the 3 run-72 tokens + the 4 run-73 tokens + the 4 run-74 tokens + the 3 run-75 tokens + the 2 run-76 tokens + the 3 run-77 tokens + the 2 run-78 tokens + the 2 run-79 tokens + the run-80 token + GrokBot 0xfcd0... + the two new run-81 tokens not in inbound set (PCS tokens; sent-pass covered). New contracts deployed this hour (10, all addresses read, none is a new token) are not in the inbound set - their token identity (name/symbol) is UNVERIFIED."),
}
mt = s.setdefault("machine_tokens", [])
for addr, first_seen, first_buy in [
    ("0x7f7a40246cbf443e6b6359b1defb81b0098f7777",
     "run-81, 2026-11-06 20:03:23 WIB (tx 0x6b209b944f47..., block 132013423)",
     0.000123616835355714),
    ("0x33f7f143e69b451fa5245b525705c7306a867777",
     "run-81, 2026-11-06 19:45:29 WIB (tx 0xcab44fc09003..., block 132011038)",
     0.000111925572639837),
]:
    mt.append({
        "address": addr,
        "first_seen": first_seen,
        "machine_wallets": 27,
        "typical_first_buy_bnb": first_buy,
        "followup_buy_range_bnb": "median ~0.22-0.23, max ~0.37",
        "label": "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB)",
        "note": "Routine rotation, no anomaly in a listed class; recorded in state WITHOUT chat report per fast-path amendment. No name/symbol, no website, no free-mint path. Auto-mint blocked at guard (c). First tracked Transfer was a bulk distribution to AFeng, not a machine buy (see paid_signal_run81 afeng_distribution_oddity).",
    })
sp = s.setdefault("signaled_projects_over_20pct", [])
for new_sig in [
    "Unnamed token (name/symbol empty) 0x7f7a40246cbf443e6b6359b1defb81b0098f7777 (paid-only, machine-token, run-81, no chat report per fast-path amendment)",
    "Unnamed token (name/symbol empty) 0x33f7f143e69b451fa5245b525705c7306a867777 (paid-only, machine-token, run-81, no chat report per fast-path amendment)",
]:
    if new_sig not in sp:
        sp.append(new_sig)
json.dump(s, open(P, "w"), indent=1)
print("state updated: run", s["last_run"]["run"])
print(f"inbound: unique_contracts={n_contracts_unique} logs={n_logs} hits={n_hits} failed={n_failed}")
print("paid_signal_run81 + paid_trend_run81 + inbound_log_leg_run81 written; machine_tokens now", len(mt), "; signaled list now", len(sp))
txs = set(); entries = 0
for f in s["reported_findings"]:
    for m in f.get("mints", []):
        entries += 1
        if m.get("tx"):
            txs.add(m["tx"].lower())
print("reported_findings mint entries:", entries, "unique txs:", len(txs))
