#!/usr/bin/env python3
"""Run 65 state update (read-only job bookkeeping; no chain writes)."""
import json
P = "/home/hatch/workspace/narrative-pulse/tracked-wallet-mint-scan-state.json"
s = json.load(open(P))
s["last_run"] = {
    "run": 65,
    "block_start": 131854891,
    "block_end": 131862391,
    "window_wib": "2026-11-06 00:15:11 - 01:10:26 WIB; sent-pass in-window txs 1300, 2 mint-pattern txs to tracked wallets (investigated: dividend-tracker shares, NOT project mints)",
    "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set)",
    "method_note": "Sent pass Ankr ankr_getTransactionsByAddress via module (55/55, 0 failed, 1300 txs, 35 wallets active). Receipts via fast_rpc batch (6, ~4s pause) for 851 non-approve candidates: 844 status 1, 7 status 0 (failed PCS sells 0x791ac947, not mints), 0 null, 2 mint-pattern logs to AFeng only - both investigated (see investigated_non_finding_run65): dividend-tracker share mints tied to paid moco buys, NOT NFT/share-sale mints. Parser filter from run 55 applied (mint_logs recipient filtered to tracked_padded). Inbound leg per 2026-11-03 12:02 amendment: Ankr getLogs address-filtered per contract, 937 contracts, 9703 logs, 0 hits, 0 failed, run as a (0-400, 5880 logs, 3 truncated cleaned topic-filtered 0x55d3.../0x6288... AGC sale/0x63de... AGC, all 0 logs) + b (400-937, 3823 logs, 0 truncated) in parallel. Coverage complete: all 937 sorted contracts checked once. DYOR: contract 0x86956bc830eb62110820ae79164bef61c7e31936 in set (via snapshot), 0 hits - no tracked wallet minted DYOR in this window. CORLA 0x4a9c499574ea003846e81522d59aa4c27ca47777 and the 4 run-64 ASI contracts are NOT in the inbound set (PCS tokens; all their activity was wallet-sent txs covered by the sent pass). 93 contract creations in window, all receipts read (93 addresses, 0 unreadable, via curl JSON-RPC batch after fast_rpc outage); NONE of the created contracts is a run-65 ASI token, moco, or the dividend tracker. No preview/mint/sign/login/purchase by this job. INFRA NOTE: fast_rpc direct-egress broke ~01:35 WIB (OSError/TimeoutError on ALL public endpoints; curl via egress proxy still worked) - later verifications (tx 0xf151304c, pair token0/token1, tokenURI retry, deployment receipts) were done via curl JSON-RPC instead; the receipts pass itself finished before the outage. If the next run's fast_rpc batch fails the same way, use the curl fallback - do NOT report 0 as absence."
}
s["next_run_note"] = ("Next run sent-tx window starts from block 131862392. Dedupe new mints against all tx hashes in reported_findings "
    "(runs 1-41: 219 txs; runs 43-65 added 0 new finding txs, total 219). ASI quad-2 0xa77c.../0xcf06.../0xfd80.../0x5c5a... signaled as paid-only in run 65 "
    "(27/27/27/27 raw wallets) and auto-mint BLOCKED at guard (c) - do not re-signal or re-report the block unless a new mint/buy fact appears for those ASI contracts "
    "(e.g. a genuine free-mint path). Paid fact: run65 max 27 wallets/token (ASI quad-2 x4); GrokBot 0xfcd0... absent (0 wallets) this run - 6th consecutive quiet run "
    "(59, 61, 62, 63, 64, 65) after the run-60 burst; CORLA-97af 0 wallets; CORLA 0x4a9c 0 wallets; all four run-64 ASI contracts 0 wallets this run (machine rotated to ASI quad-2). "
    "AFeng txs 0xc80089cc.../0x8373484f... investigated run 65: dividend-tracker share mints, NOT findings - do not re-flag if re-seen. "
    "Same-owner factory groups now also include 0x293f and 0x1103 (proven 2026-11-06 ~01:14 WIB, AGENTS.md) alongside the groups listed in the body.")
sig = s.setdefault("signaled_projects_over_20pct", [])
for entry in [
    "Anti Super Inu (ASI) 0xa77c4d2a395dd4d7d51696edf5a9cc7f730b7777 (paid-only, run-65)",
    "Anti Super Inu (ASI) 0xcf060b7d5007a11bf71007f745df3e79b98c7777 (paid-only, run-65)",
    "Anti Super Inu (ASI) 0xfd800ac441efabb02d4059131a135b38d9c37777 (paid-only, run-65)",
    "Anti Super Inu (ASI) 0x5c5aaafbc9ef01511eace8ab28a22808d2667777 (paid-only, run-65)",
]:
    if entry not in sig:
        sig.append(entry)
s["paid_signal_run65"] = {
    "note": "NEW paid-only signals (NOT buy recommendations, NOT executable Free Bacot, NOT auto-mint triggers by themselves). Same-name warning: FOUR distinct NEW contracts share name Anti Super Inu / symbol ASI + identical totalSupply 1e9 + owner 0x0 - never merged by name/symbol, and NEVER merged with the run-64 ASI quad (0x7526/0x3e61/0x455e/0x729a), which had 0 wallets this run. The machine rotated: CORLA (run 63) -> ASI quad-1 (run 64) -> ASI quad-2 (run 65).",
    "project": "Anti Super Inu (ASI) - quad 2, four NEW contracts",
    "contracts": [
        "0xa77c4d2a395dd4d7d51696edf5a9cc7f730b7777",
        "0xcf060b7d5007a11bf71007f745df3e79b98c7777",
        "0xfd800ac441efabb02d4059131a135b38d9c37777",
        "0x5c5aaafbc9ef01511eace8ab28a22808d2667777"
    ],
    "name_symbol_onchain": "name Anti Super Inu / symbol ASI, decimals 18, totalSupply 1000000000000000000000000000 (1e9) for ALL FOUR contracts; owner() 0x0 for all four; tokenURI(0) and tokenURI(1) REVERT on 0xa77c (execution reverted, verified via curl JSON-RPC after fast_rpc outage) - NO website evidence from tokenURI, website UNVERIFIED (a reverting call is not proof of no website either)",
    "participation": "27 / 27 / 27 / 27 raw wallets of 55 (49.1% each); first PCS buy of the quad 2026-11-06 00:19:29 WIB (0x5c5a); activity 00:19:29-01:09:19 WIB; not previously signaled; not in Free Bacot snapshot; not in bridge (paid-only PCS tokens, per CORLA/GrokBot/ASI precedent)",
    "buy_evidence": "Sample PCS buys verified per token (receipt/getLogs Transfer from pair + pair token0/token1 on-chain): 0xa77c buy tx 0x6f14977aab1873754c96b45cf9360c7534a64d014e5bdb530a904fa734320954 by 0xc6219468 01:01:03 WIB block 131861142, value 0x706dc98f4442, pair 0xea8d27311f75eabdb8e9834d55bf2bdae3c4209d (token0=0xa77c, token1=WBNB), ~9,858,299,777,724,292,703,472 ASI; 0xcf06 buy tx 0xedcf35e52705a180265ab1247b173c101654c2857692b281262e0256c9bbc485 by 0x1cce4ec5 00:47:22 WIB block 131859316, pair 0x7d705ee06823c50dbe64028579fe8a94fc1edb32 (token0=WBNB, token1=0xcf06), ~9,859,273,024,927,658,495,032 ASI; 0xfd80 buy tx 0xac3ccb5009efa9c9547b1085dc472cafab6ee7ec2f26648e47e358d4fc0fd142 by 0xf9689b9d 00:33:37 WIB block 131857483, pair 0xcad3a64abc43dbcb6a027e4e299ef267656cfde3 (token0=WBNB, token1=0xfd80), ~9,859,273,000,379,751,068,968 ASI; 0x5c5a FIRST REAL pair buy tx 0xbdb8329e1d1f497910cebc933c8aa413a68ccf7a259a6ea308d39ef88afc7391 by 0xc6591fde 00:19:29 WIB block 131855599, pair 0x53fcf36371ead64b5586e07bd5a4271a485e243c (token0=0x5c5a, token1=WBNB), ~9,859,273,000,379,751,068,968 ASI. Per-token getLogs Transfer counts to tracked wallets: 56 / 71 / 61 / 61 (0x5c5a: 60 from PCS pair + 1 distribution, see below). 27-wallet set window totals (all router activity, not per-token): 248x swapExactETHForTokensSupportingFeeOnTransferTokens (0xb6f9de95) + 401x sells (0x791ac947) + 393x approve (0x095ea7b3), buy value ~41.48 BNB.",
    "linkage": "NOT verified: the 27 wallets are BYTE-IDENTICAL across all four tokens (27/27 overlap each pair) and overlap 27/27/27/26 with the run-64 ASI sets and the run-63 CORLA set, which suggests the same coordinated/machine operator, but no entity collapse is applied - counted per wallet with this note, as in run 60 GrokBot / run 63 CORLA / run 64 ASI precedents",
    "auto_mint_block": "Trigger >25% met numerically for all four (27 >= 14) but BLOCKED at guard (c): paid PCS tokens, no free-mint quota/path for the user wallet - buying would cost BNB, never a free mint; guard (a) website also unverified (tokenURI reverts, no website). No preview, no execution. Do not re-report the block unless a genuine free-mint path appears for these contracts.",
    "distribution_note": "0x5c5a has ONE non-pair receipt: AFeng received 6,538,769,855,642,865,992,094 (~6,539 ASI) from distributor contract 0xf755fe13e43d35627082d570a2a63ef807a60fe0 in tx 0xf151304c31032a3ce4906ec23d984c00715829cccff81460474e0eaa1299327e (block 131855585, sender 0xb19fe323d64033cb6b5f63f8cc5ef30e39bc0af5, NOT a tracked wallet, value 0, selector 0x025ff12f, 162 logs) - a mass distribution to ~150 addresses plus a 792,000,000 ASI burn to dead. 0xf755fe13 is NOT a PCS pair (token0() reverts). This receipt does not change the 27-wallet count (AFeng is in the set via PCS buys too) and is NOT a mint finding.",
    "deployments_context": "93 contract-creation txs by 23 tracked wallets in window, all receipts read (93 addresses, 0 unreadable); NONE of the created contracts is a run-65 ASI token, moco, or the dividend tracker - all four ASI contracts predate this window. Top deployers: 0x82c6... 19, 0xc621... 11, 0x5b4b... 7."
}
s["paid_trend_run65"] = {
    "note": "Aggregate only, NOT a buy recommendation. Four tokens reach the signal threshold (ASI quad-2, see paid_signal_run65).",
    "max_wallets_per_token": 27,
    "distribution": "29 paid tokens: 27 wallets x4, 3 wallets x12, 2 wallets x5, 1 wallet x8",
    "other_paid_activity": [
        {"pattern": "12 tokens ...7777 at 3 wallets each + 5 tokens at 2 wallets each + 8 tokens at 1 wallet each - usual ...7777 machine churn below the ASI rotation, far below threshold", "wallets": "machine set subsets"},
        {"pattern": "AFeng 15 txs: 9 calls to 0x1de460f363af910f51726def188f9004276bf4bc (selector 0x4d819a2a) + 6 approvals (0x095ea7b3); valued calls 0.5 + 0.375 + 0.325 = 1.2 BNB total (moco buys 0.5 + 0.375 BNB, 0x4c89 buy 0.325 BNB - see investigated_non_finding_run65); receipts checked, no project mint", "wallet": "0xbf004bff64725914ee36d03b87d6965b0ced4903"},
        {"pattern": "0x7488... activity: see receipts (PCS micro buy/sell pattern, ~0.0003 BNB scale); 0x2325... 0 txs; 0x8e96... 1 tx this run", "wallet": "0x7488d5da6a6097de0ff88c7492c62c2fd1e56650 / 0x2325f175975abdbcde555c79cc8e63381d28551b / 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6"},
        {"pattern": "7 failed PCS sells (status 0, selector 0x791ac947, value 0): 0xb940e4cd 00:36:14, 0x2cc8192f 00:21:21, 0xc194efe2 01:04:04, 0xa952331e 00:36:40, 0xa952331e 00:21:26, 0x9b519f5d 01:03:39, 0xfdec62fd 00:21:21 WIB - failed sells, not mints", "wallet": "machine set members"}
    ],
    "deployments": "93 contract creations by 23 tracked wallets in window, all status 1 (receipts read, 0 unreadable); see paid_signal_run65.deployments_context",
    "future1001": "0 tx this run (0x355ea9e542b36c645a2dee63b9df079ccb9df3db)"
}
s["inbound_log_leg_run65"] = {
    "contracts": 937,
    "total_logs": 9703,
    "hits": 0,
    "failed": 0,
    "note": "Ankr getLogs address-filtered per contract, window 131854891-131862391, parts a (0-400, 5880 logs, 3 truncated cleaned topic-filtered 0x55d3..., 0x6288... AGC sale, 0x63de... AGC - all 0 logs) + b (400-937, 3823 logs, 0 truncated) in parallel; DYOR 0x8695... in set (via snapshot), 0 hits. No residual open. CORLA 0x4a9c + 4 run-64 ASI contracts not in inbound set (PCS tokens; sent-pass covered). New contracts deployed this hour (93) are not in the inbound set - inbound-only mints from them would be unverified by this leg (same method limitation as prior runs)."
}
s["investigated_non_finding_run65"] = {
    "note": "Parser flagged 2 mint-pattern logs (Transfer from zero address to a tracked wallet). Verified NOT project mints - do not add to reported_findings, do not report as mints.",
    "txs": [
        {"hash": "0xc80089cca2f3a4d9067adcf1fb7497275167087301a7b7adfca861c664d8ea1b", "block": 131861598, "time_wib": "2026-11-06 01:04:29", "wallet": "0xbf004bff64725914ee36d03b87d6965b0ced4903 (AFeng)", "to": "0x1de460f363af910f51726def188f9004276bf4bc", "selector": "0x4d819a2a", "value_bnb": 0.5},
        {"hash": "0x8373484fa9aaa516a08d5ab7b4fed27ec50906b76e2834fc3a6540fbde7e1561", "block": 131860481, "time_wib": "2026-11-06 00:56:06", "wallet": "0xbf004bff64725914ee36d03b87d6965b0ced4903 (AFeng)", "to": "0x1de460f363af910f51726def188f9004276bf4bc", "selector": "0x4d819a2a", "value_bnb": 0.375}
    ],
    "finding": "Both are paid buys of reflection token 'moco' (0x10b389eed857fdb84089a64188aab6afbbe2cc2a, name/symbol moco/moco, decimals 1, totalSupply 1e33, owner 0x0) via router 0x1de460f363af910f51726def188f9004276bf4bc. The flagged zero-from Transfers are from the token's DIVIDEND_TRACKER contract (0x636fdfa9bc3db42c690c09e87b9017d05b36c743, symbol DIVIDEND_TRACKER, owner 0x10b389ee...) minting tracker shares 1:1 with the bought moco balance (4,150,380,606,246,269,253,053,158,649,683 and 3,637,027,757,959,207,822,871,485,568,999 units) plus WBNB dividend distributions to holders. Internal accounting of a paid reflection-token buy, NOT an NFT mint and NOT a share-sale mint. AFeng alone received moco (1 wallet) - paid trend only. Neither moco nor the tracker is in the Free Bacot snapshot or bridge (paid PCS token precedent - not added), and neither was deployed in this window.",
    "afeng_third_valued_call": "Tx 0x77fe53947c7f5272f8c3ef76b3fa75bc19141fbc82bdaca7ee54df29b80d3adb (00:56:25 WIB, 0.325 BNB, same router/selector) bought token 0x4c892e1e9ac6a2394409c9c88cd72a5475357777 (~5.026e25 raw) - no zero-from mint in its receipt; 1-wallet paid buy, paid trend only."
}
json.dump(s, open(P, "w"), indent=1)
print("state updated: run", s["last_run"]["run"], "signaled total", len(sig))
print("paid_signal_run65 + paid_trend_run65 + inbound_log_leg_run65 + investigated_non_finding_run65 written")
