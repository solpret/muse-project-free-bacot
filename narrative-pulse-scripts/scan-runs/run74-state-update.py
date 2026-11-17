#!/usr/bin/env python3
"""Run 74 state update (read-only job bookkeeping; no chain writes).

Completes run 74 (window 131942444-131955235), whose sent/receipts/paid/
token-verify/deployments passes are all done and whose inbound leg ran in
full (a 0-400 + b 400-1005, 0 hits, 0 failed).
"""
import json
import shutil
from pathlib import Path

P = "/home/hatch/workspace/narrative-pulse/tracked-wallet-mint-scan-state.json"
D = Path("/home/hatch/workspace/narrative-pulse/scan-runs")

shutil.copy(P, str(P) + ".bak-run74-pre")
s = json.load(open(P))
ia = json.load(open(D / "run74-inbound-a.json"))
ib = json.load(open(D / "run74-inbound-b.json"))
n_contracts = ia["contracts_checked"] + ib["contracts_checked"]
n_logs = ia["total_logs"] + ib["total_logs"]
n_hits = len(ia["hits"]) + len(ib["hits"])
n_failed = len(ia["failed"]) + len(ib["failed"])
trunc = ia["truncated"] + ib["truncated"]
assert n_contracts == 1005 and n_logs == 22454 and n_hits == 0, \
    (n_contracts, n_logs, n_hits)
assert n_failed == 0, (n_failed, ia["failed"], ib["failed"])
assert len(trunc) == 7, trunc

s["last_run"] = {
    "run": 74,
    "block_start": 131942444,
    "block_end": 131955235,
    "window_wib": "2026-11-06 11:10:56 - 12:46:52 WIB; sent-pass in-window txs 1492, 0 mint-pattern txs",
    "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set)",
    "method_note": (
        "Sent pass Ankr ankr_getTransactionsByAddress via module (55/55, 0 failed; "
        "1492 txs, 35 wallets active). Receipts via fast_rpc batch (6, ~4s pause) for 960 "
        "non-approve candidates: 954 status 1, 6 status 0 (5 failed PCS sells 0x791ac947: "
        "0x29624f8b... by 0xdb2d83f907 12:15:13 WIB, 0xaa4c21f2... by 0xdb2d83f907 11:27:38 WIB, "
        "0xa985fa4e... by 0xc621946845 12:37:59 WIB, 0x4bc6cc1b... by 0xa952331ea4 12:39:06 WIB, "
        "0xf6d93b3f... by 0xa952331ea4 12:17:24 WIB; plus 1 failed PCS buy 0xb6f9de95 0.014 BNB "
        "targeting the new token 0x73c9... by 0xe9ed24db10 12:36:44 WIB, tx 0xfc4eeef6... - "
        "the missing 27th wallet for 0x73c9, see paid_signal_run74), 0 null, 0 mint-pattern logs. "
        f"Inbound leg per 2026-11-03 12:02 amendment: Ankr getLogs address-filtered per contract, "
        f"{n_contracts} contracts, {n_logs} logs, {n_hits} hits, {n_failed} failed, run as a "
        f"(0-400, {ia['total_logs']} logs, {len(ia['truncated'])} truncated, {len(ia['failed'])} failed) "
        f"+ b (400-{n_contracts}, {ib['total_logs']} logs, {len(ib['truncated'])} truncated, {len(ib['failed'])} failed). "
        "Truncated 7 (all in part a: 0x10b389... AFeng tracker owner / 0x1de4... AFeng sale / 0x53ba... tracker / "
        "0x55d3... USDT / 0x6288... AGC sale / 0x636f... AFeng tracker / 0x63de... AGC - all topic-filtered, 0 logs each). "
        "DYOR: contract 0x86956bc830eb62110820ae79164bef61c7e31936 in set (via snapshot), 0 hits - "
        "no tracked wallet minted DYOR in this window. "
        "CORLA 0x4a9c499574ea003846e81522d59aa4c27ca47777, the 4 run-64 ASI contracts, the 4 run-65 "
        "ASI quad-2 contracts, the 2 run-66 tokens, the 2 run-68 tokens, the run-69 token 0x4d15... "
        "the 5 run-70 tokens, the 6 run-71 tokens, the 3 run-72 tokens, the 4 run-73 tokens, and GrokBot 0xfcd04501ebaddcda73095a75e078a8e5292f7777 are NOT in the "
        "inbound set (PCS tokens; all their activity was wallet-sent txs covered by the sent pass). "
        "The 4 new run-74 paid tokens are likewise NOT in the inbound set - sent-pass covered. "
        "64 contract creations in window (all by 14 wallets of the 27-wallet machine set, all status 1; "
        "none is any of the 4 new tokens). "
        "No preview/mint/sign/login/purchase by this job. "
        "INFRA NOTES: (1) Ankr getLogs ran in slow stretches during inbound-b (the 250-300 and 500-550 "
        "ranges each took several minutes with no progress line; 0 failures in the end - slow, not stuck; "
        "the process stayed on an ESTAB connection throughout). (2) fast_rpc transient unreadable reads "
        "this run (name() 0x4d2e..., owner() 0xe4e0..., pair token0()/token1() 0xaf84... - all 'all endpoints "
        "failed') recorded as unreadable/transient, NOT as empty/zero."
    ),
}
s["next_run_note"] = (
    "Next run sent-tx window starts from block 131955236. Dedupe new mints against all tx hashes "
    "in reported_findings (runs 1-41: 219 txs; run 70 added 1 new finding tx (AFeng 0x5f560493...); "
    "run 71 added 1 new finding tx (0x2325 0xa20c70c1...); run 72 added 0; run 73 added 0; run 74 added 0, total 221). Paid-only signals run 63 "
    "(CORLA 0x4a9c), run 64 (4 ASI), run 65 (4 ASI quad-2), run 66 (tokens 0x19b7.../0x540d...), run 68 "
    "(tokens 0xf3cc.../0xe7e2...), run 69 (token 0x4d15...), run 70 (FIVE tokens "
    "0x4df7.../0xae06.../0x2516.../0x1247.../0x8e0d...), run 71 (SIX tokens "
    "0xe51b.../0xc2e1.../0x5785.../0xfff4.../0xe4c9.../0x25b4...), run 72 (THREE tokens "
    "0x26ef.../0x7145.../0xdfb3...), run 73 (FOUR tokens 0x4bd1.../0x1d9f.../0xe0f0... at 27 wallets + "
    "0x198c... at 21 wallets), run 74 (FOUR tokens 0xe4e0.../0x4d2e.../0xaf84... at 27 wallets + "
    "0x73c9... at 26 wallets) auto-mint BLOCKED at guard (c) "
    "- do not re-signal or re-report the block unless a new mint/buy fact appears for those contracts "
    "(e.g. a genuine free-mint path). Paid fact: run74 max 27 wallets/token (THREE new unnamed tokens "
    "at 27 wallets each + one at 26 wallets, same byte-identical 27-wallet machine set as runs 63-73 - machine "
    "rotated again: run-73 four tokens -> quiet for three of them (0 wallets) except 0x198c... still at 18 wallets -> "
    "these four tokens; the 26-wallet set is the 27-set minus 0xe9ed24db10, whose 0.014 BNB buy of 0x73c9... "
    "reverted (status 0, tx 0xfc4eeef6...)); the other 41 paid tokens max 3 wallets each (22 at 3, 8 at 2, 10 at 1 - usual ...7777 churn); "
    "GrokBot 0xfcd0... absent (0 wallets) this run - 15th consecutive quiet run (59, 61-74) after the run-60 burst; CORLA-97af 0 wallets; CORLA 0x4a9c 0 wallets; all "
    "four run-64 ASI contracts 0 wallets; all four run-65 ASI quad-2 contracts 0 wallets; both run-66 "
    "tokens 0 wallets; both run-68 tokens 0 wallets; run-69 token 0x4d15 0 wallets; all five run-70 "
    "tokens 0 wallets; all six run-71 tokens 0 wallets; all three run-72 tokens 0 wallets; three of the "
    "four run-73 tokens 0 wallets (0x4bd1/0x1d9f/0xe0f0), 0x198c... still 18 wallets (already signaled run 73 - no re-signal). Inbound retry next run: none open - run-74 window fully closed this run "
    "(1005/1005, 0 hits, 0 failed). AFeng 0 txs this run; future1001.ai 0 txs; 0x2325... 4 txs; 0x8e96... 6 txs. "
    "Same-owner factory groups now also include 0x293f and 0x1103 (proven 2026-11-06 ~01:14 WIB, AGENTS.md) alongside the groups listed in the body."
)
s["paid_signal_run74"] = {
    "note": ("NEW paid-only signal (NOT a buy recommendation, NOT executable Free Bacot, NOT an "
             "auto-mint trigger by itself). Same-machine warning: FOUR distinct NEW contracts, "
             "three bought by the SAME byte-identical 27-wallet set (27/27, pairwise diffs 0/0/0, and diff 0 "
             "vs the run-73 27-set: overlap 27/27) and the fourth by 26 wallets that are that same 27-set "
             "minus ONE wallet (0xe9ed24db10, whose 0.014 BNB buy of it reverted - see below) - the set that also bought CORLA (run 63), ASI quad-1 (run 64), "
             "ASI quad-2 (run 65), the two run-66 tokens, the two run-68 tokens, the run-69 token, the "
             "five run-70 tokens, the six run-71 tokens, the three run-72 tokens and the four run-73 tokens - the machine rotated again: CORLA (63) -> "
             "ASI quad-1 (64) -> ASI quad-2 (65) -> two unnamed tokens (66) -> quiet (67) -> two new "
             "tokens (68) -> one token (69) -> five tokens (70) -> six tokens (71) -> three tokens (72) -> "
             "four tokens (73) -> these four tokens (74). The four are NOT one project - 4 different contracts, never merged."),
    "project": "NEW paid tokens, same 27-wallet machine set (unnamed)",
    "contracts": [
        "0xe4e0acdda42c4c6b7fb899c2493080029ddf7777",
        "0x4d2e71a7e5329880786e873077567859220b7777",
        "0xaf847e9cca135c6fb2a1b6e25476be945d167777",
        "0x73c9997c98bdf0dc9b3c425cb1d6604832217777",
    ],
    "name_symbol_onchain": ("name() and symbol() both return EMPTY strings on-chain for 0xe4e0, 0xaf84 and 0x73c9 "
        "(verified via fast_rpc eth_call decode); for 0x4d2e symbol() is empty but name() was UNREADABLE transiently "
        "('all endpoints failed' - NOT proven empty); decimals 18 for all four; totalSupply 1e27 "
        "(1,000,000,000,000,000,000,000,000,000) for all four; "
        "owner() 0x0 for 0x4d2e/0xaf84/0x73c9, owner() for 0xe4e0 UNREADABLE transiently ('all endpoints failed' - NOT proven 0x0); "
        "tokenURI not attempted (no name/symbol identity to resolve, paid PCS tokens - same treatment as run-66/run-68/run-69/run-70/run-71/run-72/run-73 tokens)"),
    "participation": ("3 tokens at 27 / 55 wallets (49.1%) + 1 token at 26 / 55 wallets (47.3%); "
        "all four are 0 wallets in run 73 (new this run); "
        "first tracked buys (selector 0xb6f9de95, wallet 0xcb08c02c0a, ~9,092,300 tokens, 0.000114 BNB): "
        "0x4d2e 11:46:37 WIB (tx 0xa300bb10cfd83d41a285f880ead69e65a92de7e29ec26478d457f7ec2c33d6d9, block 131947202, pair 0x637b123a...), "
        "0xe4e0 12:14:35 WIB (tx 0x74a3309f90346e97f8b1a6b1b53395bf3188734f1993faac4feb2db529264c96, block 131950931, pair 0x4104764d...), "
        "0x73c9 12:36:17 WIB (tx 0xd37f9b1e4049791e835d8c7ede4cd56ca6ab6ebfec8f9d49b354958a94857d4d, block 131953824, pair 0x578d8540...); "
        "0xaf84 first tracked buy NOT VERIFIED: its first tracked Transfer (block 131944572, tx 0xd9efaa3e54c3c1a706d2f01d355456574e4c2c8cfaa0f1764de4ffbe7fcaa1fb, "
        "from pair 0xa7652fab..., ~53.48 tokens) is NOT a tracked-wallet sent tx (tx confirmed absent from sent.json) - small external transfer to a tracked wallet, not a tracked buy; "
        "tracked Transfer logs in window: 58 / 64 / 62 / 56 respectively; "
        "run-73 token 0x198c... still bought by 18 wallets this run (subset of the same 27-set, already signaled run 73 - NOT re-signaled); "
        "not previously signaled; not in Free Bacot snapshot; not in bridge (paid-only PCS tokens, per "
        "CORLA/GrokBot/ASI precedent)"),
    "buy_evidence": (
        "Sample PCS buys verified (receipt Transfer from pair + pair token0/token1 on-chain where readable). "
        "Pairs verified on-chain: 0xe4e0 pair 0x4104764d196c188ddf0e8e53c135856046f6f36e (token0 WBNB 0xbb4c..., token1 token); "
        "0x4d2e pair 0x637b123a8ce13130ae656e1ab940bf38275d2651 (token0 token, token1 WBNB); "
        "0x73c9 pair 0x578d8540f34fdcdbf41370432019bc5f4081f955 (token0 token, token1 WBNB); "
        "0xaf84 pair token0/token1 UNREADABLE transiently (fast_rpc 'all endpoints failed') - pair address "
        "0xa7652fab73a8e629e382769c6d9fcbb47d11c414 identified from Transfer logs only. "
        "27-wallet set window totals (all router activity, not per-token; recomputed from sent.json "
        "by literal selectors, matching token-verify.py): 266x buys (0xb6f9de95, total buy value "
        "51.0541 BNB) + 448x sells (0x791ac947) + 442x approve (0x095ea7b3) + 64x contract creations."),
    "linkage": ("NOT verified: the 27 wallets are BYTE-IDENTICAL to the run-63 CORLA / run-64 ASI / "
        "run-65 ASI quad-2 / run-66 two-token / run-68 two-token / run-69 one-token / run-70 "
        "five-token / run-71 six-token / run-72 three-token / run-73 four-token sets (verified set equality vs run-73: diff 0, overlap 27/27; "
        "the 26-wallet set for 0x73c9 is the 27-set minus 0xe9ed24db10) "
        "and deployed 64 contracts in this window via 14 wallets, which suggests the same "
        "coordinated/machine operator, but no entity collapse is applied - counted per wallet with "
        "this note, as in run 60 GrokBot / run 63 CORLA precedents"),
    "auto_mint_block": ("Trigger >25% met numerically for all four (27 >= 14, 26 >= 14) but BLOCKED at "
        "guard (c): paid PCS tokens, no free-mint quota/path for the user wallet - buying would cost "
        "BNB, never a free mint; guard (a) website also unverified (empty name/symbol, no website "
        "evidence). No preview, no execution. Do not re-report the block unless a genuine free-mint "
        "path appears for these contracts."),
    "deployments_context": ("64 contract-creation txs by 14 of the 27 wallets in this window "
        "(0xdb2d83f9 x5, 0xc6219468 x7, 0xaa49e7fe x4, 0x3154f694 x4, 0xca4e67bb x4, "
        "0x5b4beded x4, 0x36239612 x5, 0xf9689b9d x5, 0x2cc8192f x3, 0x1cce4ec5 x8, "
        "0xc0c84518 x5, 0xa952331e x2, 0x64e893a4 x3, 0x97bd895f x5), all status 1; "
        "all 64 created addresses READ from receipts this run (saved in run74-deployments.json) and NONE is any of "
        "the four new tokens - the new tokens were first bought via PCS pairs, not "
        "deployed in-window by a tracked wallet; token identity (name/symbol) of the 64 created "
        "contracts was NOT checked, so whether any of them is a future machine token is UNVERIFIED"),
    "anomaly_0xe9ed24db10": ("Machine wallet 0xe9ed24db10 attempted a 0.014 BNB PCS buy of 0x73c9... at 12:36:44 WIB "
        "(tx 0xfc4eeef641591e57743513716ca760203cfd1ad8a44526bc0d2899c57cd7f887, path WBNB -> 0x73c9..., "
        "amountOutMin ~13,085,228 tokens) - ~123x the machine norm of 0.000114 BNB - and it REVERTED (receipt status 0, 0 logs). "
        "That wallet IS in the 27-wallet sets of the other three new tokens, so the failed buy is exactly why 0x73c9 sits at 26 wallets instead of 27. "
        "Recorded as an anomaly, not a signal change."),
}
s["paid_trend_run74"] = {
    "note": "Aggregate only, NOT a buy recommendation. FOUR NEW paid-only signals (3 at 27 wallets, 1 at 26 wallets - see paid_signal_run74); all other tokens far below threshold.",
    "max_wallets_per_token": 27,
    "distribution": "45 paid tokens: 27 wallets x3 (NEW unnamed machine tokens), 26 wallets x1 (NEW unnamed machine token 0x73c9...), 18 wallets x1 (run-73 token 0x198c..., already signaled), 3 wallets x22, 2 wallets x8, 1 wallet x10 (all others ...7777-suffixed churn tokens)",
    "other_paid_activity": [
        {"pattern": "AFeng 0 txs; future1001.ai 0 txs", "wallet": "0xbf004bff64725914ee36d03b87d6965b0ced4903 / 0x355ea9e542b36c645a2dee63b9df079ccb9bf3db"},
        {"pattern": "0x2325... 4 txs: 3x aggregator 0x27772d13 to 0x296b00198d... (values 0 / 0.000233 / 0.0016 BNB, total ~0.001833 BNB) + 1 approve", "wallet": "0x2325f175975abdbcde555c79cc8e63381d28551b"},
        {"pattern": "0x8e96... 6 txs: 3x 0xef7ec2e7 to 0xe2ce6ab8... (values 0 / 0.002 / 0.002 BNB) + 2 approves", "wallet": "0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6"},
        {"pattern": "6 status-0 receipts: 5 failed PCS sells (0x791ac947) by machine wallets + 1 failed PCS buy 0.014 BNB targeting 0x73c9... by 0xe9ed24db10 (the missing 27th wallet for that token)", "wallet": "machine wallets"},
    ],
    "deployments": "64 contract creations in window, all by 14 wallets of the 27-wallet machine set (see paid_signal_run74 deployments_context)",
    "future1001": "0 tx this run (0x355ea9e542b36c645a2dee63b9df079ccb9bf3db)",
}
s["inbound_log_leg_run74"] = {
    "contracts": n_contracts,
    "total_logs": n_logs,
    "hits": n_hits,
    "failed": 0,
    "failed_contracts": [],
    "note": (f"Ankr getLogs address-filtered per contract, window 131942444-131955235, parts a "
             f"(0-400, {ia['total_logs']} logs, {len(ia['truncated'])} truncated, {len(ia['failed'])} failed) "
             f"+ b (400-{n_contracts}, {ib['total_logs']} logs, {len(ib['truncated'])} truncated, {len(ib['failed'])} failed). "
             f"{n_hits} hits - 0 inbound-only new mints. Truncated 7 (a: 0x10b389... / 0x1de4... / "
             "0x53ba... / 0x55d3... USDT / 0x6288... AGC sale / 0x636f... tracker / 0x63de... AGC - all topic-filtered, 0 logs each). "
             "Part b ran in slow stretches (250-300 and 500-550 ranges each took several minutes with no progress line; 0 failures - slow, not stuck). "
             "DYOR 0x8695... in set (via snapshot), 0 hits. No residual open from run 73 (its window fully "
             "closed, 0 failed). CORLA 0x4a9c + 4 run-64 ASI + 4 run-65 ASI quad-2 + the 2 run-66 tokens + "
             "the 2 run-68 tokens + the run-69 token + the 5 run-70 tokens + the 6 run-71 tokens + the 3 run-72 tokens + the 4 run-73 tokens + GrokBot 0xfcd0... + the 4 new "
             "run-74 tokens not in inbound set (PCS tokens; sent-pass covered). New contracts deployed this hour (64, all "
             "addresses read, none is any of the 4 new tokens) are not in the inbound set - their token "
             "identity (name/symbol) is UNVERIFIED."),
}
sp = s.setdefault("signaled_projects_over_20pct", [])
for new_sig in [
    "Unnamed token (name/symbol empty) 0xe4e0acdda42c4c6b7fb899c2493080029ddf7777 (paid-only, run-74)",
    "Unnamed token (name/symbol empty) 0x4d2e71a7e5329880786e873077567859220b7777 (paid-only, run-74)",
    "Unnamed token (name/symbol empty) 0xaf847e9cca135c6fb2a1b6e25476be945d167777 (paid-only, run-74)",
    "Unnamed token (name/symbol empty) 0x73c9997c98bdf0dc9b3c425cb1d6604832217777 (paid-only, run-74)",
]:
    if new_sig not in sp:
        sp.append(new_sig)
json.dump(s, open(P, "w"), indent=1)
print("state updated: run", s["last_run"]["run"])
print(f"inbound: contracts={n_contracts} logs={n_logs} hits={n_hits} failed=0")
print("paid_signal_run74 + paid_trend_run74 + inbound_log_leg_run74 written; signaled list now", len(sp))
print("reported_findings total txs now:", sum(len(f.get('mints', [])) for f in s['reported_findings']))
