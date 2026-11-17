#!/usr/bin/env python3
"""Run 67 state update (read-only job bookkeeping; no chain writes)."""
import json
P = "/home/hatch/workspace/narrative-pulse/tracked-wallet-mint-scan-state.json"
s = json.load(open(P))
s["last_run"] = {
    "run": 67,
    "block_start": 131870175,
    "block_end": 131877958,
    "window_wib": "2026-11-06 02:11:50 - 03:07:12 WIB; sent-pass in-window txs 152, 0 mint-pattern txs",
    "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set)",
    "method_note": "Sent pass Ankr ankr_getTransactionsByAddress via module (55/55, 0 failed, 152 txs, 7 wallets active). Receipts via fast_rpc batch (6, ~4s pause) for 102 non-approve candidates: 102 status 1, 0 status 0, 0 null, 0 mint-pattern logs. Inbound leg per 2026-11-03 12:02 amendment: Ankr getLogs address-filtered per contract, 960 contracts, 8783 logs, 0 hits, 1 failed, run as a (0-400, 5385 logs, 3 truncated cleaned topic-filtered 0x55d3.../0x6288... AGC sale/0x63de... AGC, all 0 logs) + b (400-960, 3398 logs, 0 truncated, 0 failed). Coverage complete: all 960 sorted contracts checked once. 1 failed contract is transient Ankr 'Remote end closed connection without response' (0x050a11c2bfcf881b546983a20550a0e409bf69da, in part a) - retry next run; its inbound-only mints are UNVERIFIED this run, not zero. Retry of the 6 run-66 failed contracts on the RUN-66 window (131862392-131870174) completed this run: 6/6, 5 logs, 0 hits, 0 failed - the run-66 window is now fully closed. DYOR: contract 0x86956bc830eb62110820ae79164bef61c7e31936 in set (via snapshot), 0 hits - no tracked wallet minted DYOR in this window. CORLA 0x4a9c499574ea003846e81522d59aa4c27ca47777, the 4 run-64 ASI contracts, the 4 run-65 ASI quad-2 contracts and the 2 run-66 tokens are NOT in the inbound set (PCS tokens; all their activity was wallet-sent txs covered by the sent pass). 0 contract creations in window. No preview/mint/sign/login/purchase by this job. INFRA NOTE: Ankr getLogs ran unusually slowly this run (~29 min for the two inbound parts vs ~10-15 min typical); no service-restart death this run."
}
s["next_run_note"] = ("Next run sent-tx window starts from block 131877959. Dedupe new mints against all tx hashes in reported_findings "
    "(runs 1-41: 219 txs; runs 43-67 added 0 new finding txs, total 219). Paid-only signals run 63 (CORLA 0x4a9c), run 64 (4 ASI), run 65 (4 ASI quad-2), run 66 (tokens 0x19b7.../0x540d...) auto-mint BLOCKED at guard (c) - do not re-signal or re-report the block unless a new mint/buy fact appears for those contracts "
    "(e.g. a genuine free-mint path). Paid fact: run67 max 3 wallets/token (only ...7777 churn); the 27-wallet rotation machine set had 0 txs this run - no member of that set appears among the 7 active wallets, and none of its tokens (CORLA, ASI quads, run-66 tokens, GrokBot) appears in the paid map; GrokBot 0xfcd0... absent (0 wallets) this run - 8th consecutive quiet run "
    "(59, 61, 62, 63, 64, 65, 66, 67) after the run-60 burst; CORLA-97af 0 wallets; CORLA 0x4a9c 0 wallets; all four run-64 ASI contracts 0 wallets; all four run-65 ASI quad-2 contracts 0 wallets; both run-66 tokens 0 wallets. "
    "Inbound retry next run (transient Ankr failure this run): 0x050a11c2bfcf881b546983a20550a0e409bf69da. "
    "AFeng 0 txs this run; 0x2325... 0 txs; future1001.ai 0 txs. "
    "Same-owner factory groups now also include 0x293f and 0x1103 (proven 2026-11-06 ~01:14 WIB, AGENTS.md) alongside the groups listed in the body.")
s["paid_trend_run67"] = {
    "note": "Aggregate only, NOT a buy recommendation. No token reaches the signal threshold.",
    "max_wallets_per_token": 3,
    "distribution": "22 paid tokens: 3 wallets x12, 2 wallets x6, 1 wallet x4 (all ...7777-suffixed churn tokens)",
    "other_paid_activity": [
        {"pattern": "12 tokens ...7777 at 3 wallets each (the usual ...7777 machine churn set: 0x38031ca8/0xad94ee77/0xc7c5faa2) + 6 tokens at 2 wallets each + 4 tokens at 1 wallet each - far below threshold", "wallets": "machine set subsets"},
        {"pattern": "0x7488... 9 txs: 3 PCS micro buy/sell cycles (buy 0xb6f9de95 ~0.00008-0.00009 BNB, sell 0x791ac947 value 0)", "wallet": "0x7488d5da6a6097de0ff88c7492c62c2fd1e56650"},
        {"pattern": "0x8e96... 1 tx: aggregator call 0xef7ec2e7 to 0xe2ce..., value 0 - not a mint", "wallet": "0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6"},
        {"pattern": "AFeng 0 txs; 0x2325... 0 txs; future1001.ai 0 txs", "wallet": "0xbf004bff64725914ee36d03b87d6965b0ced4903 / 0x2325f175975abdbcde555c79cc8e63381d28551b / 0x355ea9e542b36c645a2dee63b9df079ccb9bf3db"}
    ],
    "deployments": "0 contract creations in window (to=None in sent pass)",
    "future1001": "0 tx this run (0x355ea9e542b36c645a2dee63b9df079ccb9bf3db)"
}
s["inbound_log_leg_run67"] = {
    "contracts": 960,
    "total_logs": 8783,
    "hits": 0,
    "failed": 1,
    "failed_contracts": [
        "0x050a11c2bfcf881b546983a20550a0e409bf69da"
    ],
    "note": "Ankr getLogs address-filtered per contract, window 131870175-131877958, parts a (0-400, 5385 logs, 3 truncated cleaned topic-filtered 0x55d3..., 0x6288... AGC sale, 0x63de... AGC - all 0 logs) + b (400-960, 3398 logs, 0 truncated, 0 failed). Coverage complete: all 960 sorted contracts checked once. 1 failed contract is transient Ankr 'Remote end closed connection without response' - retry next run; inbound-only mints from it are UNVERIFIED this run, not zero. Retry of the 6 run-66 failed contracts on the RUN-66 window (131862392-131870174) completed this run: 6/6, 5 logs, 0 hits, 0 failed - run-66 window fully closed, no residual open except the 1 failed contract above. DYOR 0x8695... in set (via snapshot), 0 hits. No residual open except the 1 failed contract. CORLA 0x4a9c + 4 run-64 ASI + 4 run-65 ASI quad-2 + the 2 run-66 tokens not in inbound set (PCS tokens; sent-pass covered). New contracts deployed this hour (0) are not in the inbound set - no such limitation this run."
}
json.dump(s, open(P, "w"), indent=1)
print("state updated: run", s["last_run"]["run"])
print("paid_trend_run67 + inbound_log_leg_run67 written")
