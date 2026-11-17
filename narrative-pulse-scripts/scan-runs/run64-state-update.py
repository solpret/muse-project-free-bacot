#!/usr/bin/env python3
"""Run 64 state update (read-only job bookkeeping; no chain writes)."""
import json
P = "/home/hatch/workspace/narrative-pulse/tracked-wallet-mint-scan-state.json"
s = json.load(open(P))
s["last_run"] = {
    "run": 64,
    "block_start": 131845955,
    "block_end": 131854890,
    "window_wib": "2026-11-05 23:09:54 - 2026-11-06 00:14:10 WIB; sent-pass in-window txs 1341, 0 mint-pattern txs to tracked wallets",
    "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set)",
    "method_note": "Sent pass Ankr ankr_getTransactionsByAddress via module (55/55, 0 failed, 1341 txs, 34 wallets active). Receipts via fast_rpc batch (6, ~4s pause) for 879 non-approve candidates: 871 status 1, 8 status 0 (failed PCS sells 0x791ac947, not mints), 0 null, 0 mint_logs to a tracked wallet. Parser filter from run 55 applied (mint_logs recipient filtered to tracked_padded). Inbound leg per 2026-11-03 12:02 amendment: Ankr getLogs address-filtered per contract, 897 contracts, 12725 logs, 0 hits, 0 failed, run as a (0-400, 6662 logs, 3 truncated cleaned topic-filtered 0x55d3.../0x6288... AGC sale/0x63de... AGC, all 0 logs) + b (400-897, 6063 logs, 0 truncated) in parallel. Coverage complete: all 897 sorted contracts checked once. DYOR: contract 0x86956bc830eb62110820ae79164bef61c7e31936 in set, 0 hits - no tracked wallet minted DYOR in this window. CORLA 0x4a9c499574ea003846e81522d59aa4c27ca47777 and the 4 ASI contracts are NOT in the inbound set (PCS tokens, not NFT/sale contracts; all their activity was wallet-sent txs covered by the sent pass). 90 contract creations in window, all receipts read, none is an ASI token. No preview/mint/sign/login/purchase by this job."
}
s["next_run_note"] = ("Next run sent-tx window starts from block 131854891. Dedupe new mints against all tx hashes in reported_findings "
    "(runs 1-41: 219 txs; runs 43-64 added 0 new finding txs, total 219). ASI 0x7526.../0x3e61.../0x455e.../0x729a... signaled as paid-only in run 64 "
    "(27/27/27/26 raw wallets) and auto-mint BLOCKED at guard (c) - do not re-signal or re-report the block unless a new mint/buy fact appears for "
    "those ASI contracts (e.g. a genuine free-mint path). Paid fact: run64 max 27 wallets/token (ASI x3); GrokBot 0xfcd0... absent (0 wallets) this run - 5th "
    "consecutive quiet run (59, 61, 62, 63, 64) after the run-60 burst; CORLA-97af 0 wallets; CORLA 0x4a9c 0 wallets this run (machine rotated to ASI).")
sig = s.setdefault("signaled_projects_over_20pct", [])
for entry in [
    "Anti Super Inu (ASI) 0x7526782e635c2f4f9d63a7d4736194158d937777 (paid-only, run-64)",
    "Anti Super Inu (ASI) 0x3e612ed93b07239efc7db9da05ff07b7ad6f7777 (paid-only, run-64)",
    "Anti Super Inu (ASI) 0x455e2e30de81c25ec7788d6c08431dbfc2b77777 (paid-only, run-64)",
    "Anti Super Inu (ASI) 0x729a625d9649bbe2802d2cbb4d4ba6c1bb477777 (paid-only, run-64)",
]:
    if entry not in sig:
        sig.append(entry)
s["paid_signal_run64"] = {
    "note": "NEW paid-only signals (NOT buy recommendations, NOT executable Free Bacot, NOT auto-mint triggers by themselves). Same-name warning: FOUR distinct contracts share name Anti Super Inu / symbol ASI + IDENTICAL tokenURI metadata + identical totalSupply 1e9 - never merged by name/symbol. Same operator set as run-63 CORLA (byte-identical 27-wallet set for the first three tokens).",
    "project": "Anti Super Inu (ASI)",
    "contracts": [
        "0x7526782e635c2f4f9d63a7d4736194158d937777",
        "0x3e612ed93b07239efc7db9da05ff07b7ad6f7777",
        "0x455e2e30de81c25ec7788d6c08431dbfc2b77777",
        "0x729a625d9649bbe2802d2cbb4d4ba6c1bb477777"
    ],
    "name_symbol_onchain": "name Anti Super Inu / symbol ASI, decimals 18, totalSupply 1000000000000000000000000000 (1e9) for ALL FOUR contracts; owner() 0x0 for all four; tokenURI identical for all four (base64 JSON: only image ipfs://QmNduX5JWTDK36NCcnpe1Bo7pzuCETQk7enat7mza55VMQ + twitter field https://x.com/RepYassAnsari/status/2118054336077127797 - a status link, NOT a project profile; NO website/external_url)",
    "participation": "27 / 27 / 27 / 26 raw wallets of 55 (49.1% / 49.1% / 49.1% / 47.3%); first-seen 2026-11-05 23:21:12 WIB; activity 23:21:12-00:11:37 WIB; not previously signaled; not in Free Bacot snapshot; not in bridge (paid-only PCS tokens, per CORLA/GrokBot precedent)",
    "buy_evidence": "Sample PCS buys verified per token (receipt Transfer from pair + pair token0/token1 on-chain): 0x7526 buy 0x0c17dd1cd299 by 0x1cce4ec5 23:54:39 WIB value 0.2252 BNB, pair 0xb83b0be076e77a9858d44adaca51925f9466e672, ~5,250,055 ASI; 0x3e61 buy 0x308e867bc6f6 by 0x1cce4ec5 23:40:52 WIB value 0.2594 BNB, pair 0x67c3e9b01f3bc805265d84b04ae45f5c1b6b115b, ~7,479,924 ASI; 0x455e buy 0xda5283fc635d by 0x1cce4ec5 23:26:25 WIB value 0.2231 BNB, pair 0xb54e4c4cbb75488481bb815d38465e9bea429cae, ~5,379,585 ASI; 0x729a buy 0x25d38a70201a by 0x1cce4ec5 2026-11-06 00:06:54 WIB value 0.2234 BNB, pair 0xe41dc7f8b237a0493bcd4d54181f15de4437db1f, ~5,571,861 ASI; all pairs token1=WBNB 0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c. 27-wallet set window totals (all router activity, not per-token): 263x swapExactETHForTokensSupportingFeeOnTransferTokens (0xb6f9de95) + 404x sells (0x791ac947) + 399x approve (0x095ea7b3), buy value ~41.89 BNB.",
    "linkage": "NOT verified: the 27 wallets are BYTE-IDENTICAL to the run-63 CORLA 27-set (first three tokens 27/27 overlap; fourth token 26/26 subset) and deployed 90 contracts in this window via 25 wallets, which suggests the same coordinated/machine operator, but no entity collapse is applied - counted per wallet with this note, as in run 60 GrokBot / run 63 CORLA precedents",
    "auto_mint_block": "Trigger >25% met numerically for all four (27/27/27/26 >= 14) but BLOCKED at guard (c): paid PCS tokens, no free-mint quota/path for the user wallet - buying would cost BNB, never a free mint; guard (a) website also unverified (tokenURI has no website/external_url). No preview, no execution. Do not re-report the block unless a genuine free-mint path appears for these contracts.",
    "deployments_context": "90 contract-creation txs by 25 tracked wallets in window, all receipts read (90 addresses, all status 1, 0 unreadable); NONE of the created contracts is an ASI token - all four ASI contracts predate this window. Top deployers: 0x82c6... 7, 0xaa49... 6, 0xe9ed... 4; token identity of the deployed contracts UNVERIFIED (no name()/symbol() sampled this run)"
}
s["paid_trend_run64"] = {
    "note": "Aggregate only, NOT a buy recommendation. Four tokens reach the signal threshold (ASI x4, see paid_signal_run64).",
    "max_wallets_per_token": 27,
    "distribution": "33 paid tokens: 27 wallets x3, 26 wallets x1, 3 wallets x8, 2 wallets x13, 1 wallet x8",
    "other_paid_activity": [
        {"pattern": "8 tokens ...7777 at 3 wallets each + 13 tokens at 2 wallets each + 8 tokens at 1 wallet each - usual ...7777 machine churn below the ASI rotation, far below threshold", "wallets": "machine set subsets"},
        {"pattern": "AFeng 19 txs: 9 calls 0x0c307f76 + 9 approvals (0x095ea7b3) + 1 call 0x98d2ac62, total tx value 0 BNB; receipts checked, no mint logs", "wallet": "0xbf004bff64725914ee36d03b87d6965b0ced4903"},
        {"pattern": "0x7488... 12 txs: 4 approve + 4 PCS buys (0xb6f9de95) + 4 PCS sells (0x791ac947), total value ~0.0003 BNB; no mint logs", "wallet": "0x7488d5da6a6097de0ff88c7492c62c2fd1e56650"},
        {"pattern": "0x2325... 0 txs; 0x8e96... 0 txs this run", "wallet": "0x2325f175975abdbcde555c79cc8e63381d28551b / 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6"},
        {"pattern": "8 failed PCS sells (status 0, selector 0x791ac947, value 0): 0x3628... 23:49:33, 0xc621... 23:51:46, 0x9cdd... 23:37:53, 0x82c6... 23:37:40, 0xcb08... 23:23:49, 0xf968... 23:52:10, 0x92bc... 00:05:58, 0x97bd... 23:24:15 WIB - failed sells, not mints", "wallet": "machine set members"}
    ],
    "deployments": "90 contract creations by 25 tracked wallets in window, all status 1; see paid_signal_run64.deployments_context",
    "future1001": "0 tx this run"
}
s["inbound_log_leg_run64"] = {
    "contracts": 897,
    "total_logs": 12725,
    "hits": 0,
    "failed": 0,
    "note": "Ankr getLogs address-filtered per contract, window 131845955-131854890, parts a (0-400, 6662 logs, 3 truncated cleaned topic-filtered 0x55d3..., 0x6288... AGC sale, 0x63de... AGC - all 0 logs) + b (400-897, 6063 logs, 0 truncated) in parallel; DYOR 0x8695... in set, 0 hits. No residual open. CORLA 0x4a9c + 4 ASI contracts not in inbound set (PCS tokens; sent-pass covered). New contracts deployed this hour (90) are not in the inbound set - inbound-only mints from them would be unverified by this leg (same method limitation as prior runs)."
}
json.dump(s, open(P, "w"), indent=1)
print("state updated: run", s["last_run"]["run"], "signaled total", len(sig))
print("paid_signal_run64 + paid_trend_run64 + inbound_log_leg_run64 written")
