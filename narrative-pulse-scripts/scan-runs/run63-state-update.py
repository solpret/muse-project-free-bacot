#!/usr/bin/env python3
"""Run 63 state update (read-only job bookkeeping; no chain writes)."""
import json
P = "/home/hatch/workspace/narrative-pulse/tracked-wallet-mint-scan-state.json"
s = json.load(open(P))
s["last_run"] = {
    "run": 63,
    "block_start": 131838261,
    "block_end": 131845954,
    "window_wib": "2026-11-05 blocks 131838261-131845954; tx 22:10:21-23:07:07 WIB; sent-pass in-window txs 448, 0 mint-pattern txs to tracked wallets",
    "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set)",
    "method_note": "Sent pass Ankr ankr_getTransactionsByAddress via module (55/55, 0 failed, 448 txs, 36 wallets active). Receipts via fast_rpc batch (6, ~4s pause) for 291 non-approve candidates: 289 status 1, 2 status 0 (failed PCS sells 0x791ac947, not mints), 0 null, 0 mint_logs to a tracked wallet. One batch chunk failed HTTP 400 and was recovered via race fallback (same as run 62 pattern). Parser filter from run 55 applied (mint_logs recipient filtered to tracked_padded). Inbound leg per 2026-11-03 12:02 amendment: Ankr getLogs address-filtered per contract, 868 contracts, 10854 logs, 0 hits, 0 failed, run as a (0-400, 6229 logs, 3 truncated cleaned topic-filtered 0x55d3.../0x6288... AGC sale/0x63de... AGC, all 0 logs) + b (400-468, 4625 logs, 0 truncated) in parallel; no service-restart death this run. Coverage complete: all 868 sorted contracts checked once. DYOR: contract 0x86956bc830eb62110820ae79164bef61c7e31936 in set, 0 hits - no tracked wallet minted DYOR in this window. CORLA 0x4a9c499574ea003846e81522d59aa4c27ca47777 is NOT in the inbound set (PCS token, not an NFT/sale contract; all its activity was wallet-sent txs covered by the sent pass). No preview/mint/sign/login/purchase by this job."
}
s["next_run_note"] = ("Next run sent-tx window starts from block 131845955. Dedupe new mints against all tx hashes in reported_findings "
    "(runs 1-41: 219 txs; runs 43-63 added 0 new finding txs, total 219). CORLA 0x4a9c...7777 signaled as paid-only in run 63 (27 raw wallets) "
    "and auto-mint BLOCKED at guard (c) - do not re-signal or re-report the block unless a new mint/buy fact appears for that CORLA contract "
    "(e.g. a genuine free-mint path). Paid fact: run63 max 27 wallets/token (CORLA 0x4a9c); GrokBot 0xfcd0... absent (0 wallets) this run - 4th "
    "consecutive quiet run (59, 61, 62, 63) after the run-60 burst; CORLA-97af also 0 wallets.")
sig = s.setdefault("signaled_projects_over_20pct", [])
entry = "CORLA 0x4a9c499574ea003846e81522d59aa4c27ca47777 (paid-only, run-63)"
if entry not in sig:
    sig.append(entry)
s["paid_signal_run63"] = {
    "note": "NEW paid-only signal (NOT a buy recommendation, NOT executable Free Bacot, NOT an auto-mint trigger by itself). Same-name warning: CORLA 0x97af53eab330b607846a7fbfe1e6b51317427777 was signaled in run 56; this 0x4a9c contract is a DIFFERENT contract with the same name/symbol - never merged by name/symbol.",
    "project": "CORLA",
    "contract": "0x4a9c499574ea003846e81522d59aa4c27ca47777",
    "name_symbol_onchain": "name CORLA / symbol CORLA, decimals 18, totalSupply 1000000000000000000000000000 (1e9)",
    "participation": "27 raw wallets of 55 (49.1%) bought via PCS in window 22:45-22:55 WIB; 0 wallets in runs 60-62; not previously signaled",
    "buy_evidence": "64x swapExactETHForTokensSupportingFeeOnTransferTokens (0xb6f9de95) with BNB value + 112x sells (0x791ac947) + 110x approve (0x095ea7b3) by the 27 wallets; sample Transfer from PCS pair 0xbff868d924c19f3b9cd7309f5be7c2dcc48ba839 (token0=CORLA 0x4a9c, token1=WBNB, verified on-chain) to wallet 0xdb2d83f907965fb05ac23b8d40d3a327fc9ea52b, ~4.68M CORLA; 87 nonzero-value txs by the 27 wallets totaling 11.65 BNB (deployments + swaps)",
    "linkage": "NOT verified: the 27 wallets deployed 23 contracts in the same minute (22:45:00-22:45:12 WIB) and traded the same token, which suggests coordinated/machine behavior, but no entity collapse is applied - counted per wallet with this note, as in run 60 GrokBot precedent",
    "auto_mint_block": "Trigger >25% met numerically (27 >= 14) but BLOCKED at guard (c): paid PCS token, no free-mint quota/path for the user wallet - buying would cost BNB, never a free mint; guard (a) website also unverified. No preview, no execution. Do not re-report the block unless a genuine free-mint path appears for this contract.",
    "deployments_context": "23 contract-creation txs by 17 of the 27 wallets at blocks 131843006-131843033 (22:45:00-22:45:12 WIB), values 0.0048-0.108 BNB each, all status 1; 22 contract addresses read (none is 0x4a9c - CORLA 0x4a9c was NOT deployed in this window), 1 receipt unreadable after retries (tx 0x7c1d5f6aa919, NOT proven absent/failed); 3 sampled created contracts return no name()/symbol() (0x) - token identity of the deployed contracts UNVERIFIED"
}
s["paid_trend_run63"] = {
    "note": "Aggregate only, NOT a buy recommendation. One token reaches the signal threshold (CORLA 0x4a9c, see paid_signal_run63).",
    "max_wallets_per_token": 27,
    "distribution": "24 paid tokens: 27 wallets x1, 3 wallets x8, 2 wallets x7, 1 wallet x8",
    "other_paid_activity": [
        {"pattern": "8 tokens ...7777 at 3 wallets each (trio/pairs churn): 0x7cdd..., 0x4da8..., 0x097c..., 0x7e14..., 0x4e21..., 0xf992..., 0xf975..., 0xdb38...", "wallets": "trio 0x3803.../0xad94.../0xc7c5... + pairs 0x3628.../0xa0c1..."},
        {"pattern": "7 tokens at 2 wallets each, 8 tokens at 1 wallet each - usual ...7777 machine churn, far below threshold", "wallets": "various"},
        {"pattern": "AFeng 6 txs: 3 calls to 0x1de460f363af910f51726def188f9004276bf4bc selector 0x4d819a2a (values 0 / 0 / 0.6 BNB) + 2 approvals (to 0x4ae3...7777 and 0xf098...7777) + 1 self-transfer ~0.0023 BNB; total tx value 0.636 BNB; receipts checked, no mint logs", "wallet": "0xbf004bff64725914ee36d03b87d6965b0ced4903"},
        {"pattern": "0x2325... 5 txs (3 aggregator 0x27772d13 + 2 approve 0x095ea7b3); 0x8e96... 3 txs (2 aggregator 0xef7ec2e7 + 1 approve); no mint logs", "wallet": "0x2325f175975abdbcde555c79cc8e63381d28551b / 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6"},
        {"pattern": "2 failed PCS sells (status 0, selector 0x791ac947, value 0): 0x1cce... 22:49:03 WIB + 0x92bc... 22:50:08 WIB - failed sells, not mints", "wallet": "0x1cce4ec5a7c5e8cfc8dedd771876c61e60b8b645 / 0x92bc32975b0fbf1a19caf7cc6e3f9ea4092fd314"}
    ],
    "deployments": "23 contract creations by 17 tracked wallets in one minute (22:45:00-22:45:12 WIB), blocks 131843006-131843033, all status 1; see paid_signal_run63.deployments_context",
    "future1001": "0 tx this run"
}
s["inbound_log_leg_run63"] = {
    "contracts": 868,
    "total_logs": 10854,
    "hits": 0,
    "failed": 0,
    "note": "Ankr getLogs address-filtered per contract, window 131838261-131845954, parts a (0-400) + b (400-868) run in parallel; 3 truncated in a cleaned topic-filtered (0x55d3..., 0x6288... AGC sale, 0x63de... AGC - all 0 logs); DYOR 0x8695... in set, 0 hits. No residual open. CORLA 0x4a9c not in inbound set (PCS token; sent-pass covered). New contracts deployed this hour (23) are not in the inbound set - inbound-only mints from them would be unverified by this leg (same method limitation as prior runs)."
}
json.dump(s, open(P, "w"), indent=1)
print("state updated: run", s["last_run"]["run"], "signaled total", len(sig))
print("paid_signal_run63 + paid_trend_run63 + inbound_log_leg_run63 written")
