#!/usr/bin/env python3
"""Run 66 state update (read-only job bookkeeping; no chain writes)."""
import json
P = "/home/hatch/workspace/narrative-pulse/tracked-wallet-mint-scan-state.json"
s = json.load(open(P))
s["last_run"] = {
    "run": 66,
    "block_start": 131862392,
    "block_end": 131870174,
    "window_wib": "2026-11-06 01:11:37 - 02:08:49 WIB; sent-pass in-window txs 762, 0 mint-pattern txs",
    "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set)",
    "method_note": "Sent pass Ankr ankr_getTransactionsByAddress via module (55/55, 0 failed, 762 txs, 34 wallets active). Receipts via fast_rpc batch (6, ~4s pause) for 502 non-approve candidates: 501 status 1, 1 status 0 (failed PCS sell 0x791ac947 by 0x36239612, 01:20:11 WIB, not a mint), 0 null, 0 mint-pattern logs. Inbound leg per 2026-11-03 12:02 amendment: Ankr getLogs address-filtered per contract, 960 contracts, 10564 logs, 0 hits, 6 failed, run as a (0-400, 6202 logs, 3 truncated cleaned topic-filtered 0x55d3.../0x6288... AGC sale/0x63de... AGC, all 0 logs) + b (400-900, 3532 logs per progress line, 0 truncated; process killed by service restart at 500/560) + b2 re-run of the remaining 60 (900-960, 830 logs, 0 hits, 0 failed). Coverage complete: all 960 sorted contracts checked once. 6 failed contracts are transient Ankr 'Remote end closed connection without response' (3 in a + 3 in b, same ~19:36 UTC window) - retry next run; their inbound-only mints are UNVERIFIED this run, not zero. DYOR: contract 0x86956bc830eb62110820ae79164bef61c7e31936 in set (via snapshot), 0 hits - no tracked wallet minted DYOR in this window. CORLA 0x4a9c499574ea003846e81522d59aa4c27ca47777 and the 4 run-64 ASI contracts and the 4 run-65 ASI quad-2 contracts are NOT in the inbound set (PCS tokens; all their activity was wallet-sent txs covered by the sent pass). 58 contract creations in window, all receipts read (58 addresses, 0 unreadable); NEITHER of the two run-66 paid tokens was deployed in this window (both predate it). No preview/mint/sign/login/purchase by this job. INFRA NOTE: fast_rpc direct-egress RECOVERED (receipts + eth_call worked this run); one symbol() call failed transiently with 'all endpoints failed' and was verified via curl JSON-RPC instead. Ankr endpoint had a transient connection-close window mid-run (see failed contracts above)."
}
s["next_run_note"] = ("Next run sent-tx window starts from block 131870175. Dedupe new mints against all tx hashes in reported_findings "
    "(runs 1-41: 219 txs; runs 43-66 added 0 new finding txs, total 219). NEW paid-only signal run 66: tokens 0x19b7.../0x540d... (27/27 wallets each) auto-mint BLOCKED at guard (c) - do not re-signal or re-report the block unless a new mint/buy fact appears for those contracts "
    "(e.g. a genuine free-mint path). Paid fact: run66 max 27 wallets/token (two NEW tokens, same 27-wallet machine set as ASI quad-2); GrokBot 0xfcd0... absent (0 wallets) this run - 7th consecutive quiet run "
    "(59, 61, 62, 63, 64, 65, 66) after the run-60 burst; CORLA-97af 0 wallets; CORLA 0x4a9c 0 wallets; all four run-65 ASI quad-2 contracts 0 wallets this run (machine rotated to the two run-66 tokens); all four run-64 ASI contracts 0 wallets. "
    "Inbound retry next run (transient Ankr failures this run): 0x339df8fa35078dfb947e8cd1e2a85da62cd17ecb, 0x33a8db53339a0c37246216b45394e7e56b3c7d1e, 0x355286c54af4cecf07e13a0aef6ad36ee4d27fb8, "
    "0x9adca6b0777fd8cd5b4795f885c7d5c5f98eea6b, 0x9b5a55dbc77cd41d0b79b45119c300f2a20288db, 0x9cc4d56e6ce5c0ddade134b932023b5cab2458d8. "
    "AFeng 0 txs this run; 0x2325... 0 txs; future1001.ai 0 txs. "
    "Same-owner factory groups now also include 0x293f and 0x1103 (proven 2026-11-06 ~01:14 WIB, AGENTS.md) alongside the groups listed in the body.")
sig = s.setdefault("signaled_projects_over_20pct", [])
for entry in [
    "Unnamed token (name/symbol empty) 0x19b7fd3ae4234e4e632ff0b0f01f62a5340d7777 (paid-only, run-66)",
    "ASI-symbol token (name empty / symbol ASI) 0x540df48115f469c4083ba7a6d03255ea5f6f7777 (paid-only, run-66)",
]:
    if entry not in sig:
        sig.append(entry)
s["paid_signal_run66"] = {
    "note": "NEW paid-only signals (NOT buy recommendations, NOT executable Free Bacot, NOT auto-mint triggers by themselves). Same-machine warning: TWO distinct NEW contracts, each bought by the SAME byte-identical 27-wallet set (27/27 overlap each way) that also bought all four ASI quad-2 contracts in run 65 (27/27 overlap with each) - the machine rotated again: CORLA (run 63) -> ASI quad-1 (run 64) -> ASI quad-2 (run 65) -> these two tokens (run 66). The two tokens are NOT one project - distinct contract identities, never merged; one has empty name AND empty symbol, the other empty name but symbol ASI (same symbol as the ASI quads, different contract - never merge by symbol).",
    "project": "Two NEW paid tokens, same 27-wallet machine set",
    "contracts": [
        "0x19b7fd3ae4234e4e632ff0b0f01f62a5340d7777",
        "0x540df48115f469c4083ba7a6d03255ea5f6f7777"
    ],
    "name_symbol_onchain": "0x19b7: name() and symbol() both return EMPTY strings on-chain (verified twice: fast_rpc decode + curl raw 0x...0020...0000 length 0); 0x540d: name() EMPTY string, symbol() 'ASI' (raw 0x...0020...0003 415349); decimals 18 for both; totalSupply 1000000000000000000000000000 (1e9) for both; owner() 0x0 for both; tokenURI not attempted (no name/symbol identity to resolve, paid PCS tokens - same treatment as ASI quads, whose tokenURI reverted)",
    "participation": "27 / 27 raw wallets of 55 (49.1% each); 0 wallets for both in run 65 (new this run); activity 01:17:33-02:08:49 WIB; not previously signaled; not in Free Bacot snapshot; not in bridge (paid-only PCS tokens, per CORLA/GrokBot/ASI precedent)",
    "buy_evidence": "Sample PCS buys verified per token (receipt Transfer from pair + pair token0/token1 on-chain): 0x540d FIRST tracked buy tx 0x1859463831dc22230f1711b2ad097d1579917f30e8c6e03dbfabcb41a905bf29 by 0xfdec62fde1f1dc56c0ba5e50f4cae5d6c63762bf, block 131863340, 01:17:33 WIB, value 0.0001141216 BNB, selector 0xb6f9de95, pair 0xb277c5630ba02d1205bb602ee974d3e3234949ae (token0=0x540d, token1=WBNB), ~9.102e21 raw received; 0x19b7 FIRST tracked buy tx 0x243c62003b60bd8cd04ae1da531fe6ffe4f2116653133b11d13e22678e2caae3 by 0xf9689b9d0a675ff9ad876f1d766fb460dbde7d20, block 131865219, 01:31:38 WIB, value 0.0001142151 BNB, selector 0xb6f9de95, pair 0x2327212dacfa3dc3ddc0165d1e6ab8964fa7ae70 (token0=0x19b7, token1=WBNB), ~9.109e21 raw received. Per-token Ankr topic-filtered Transfer-to-tracked log counts: 63 (0x19b7) / 65 (0x540d). 27-wallet set window totals (all router activity, not per-token): 128x buys (0xb6f9de95, total buy value ~24.07 BNB) + 204x sells (0x791ac947) + 203x approve (0x095ea7b3) + 58x contract creations (0x60806040) + 1x native transfer.",
    "linkage": "NOT verified: the 27 wallets are BYTE-IDENTICAL across both tokens and byte-identical to the run-65 ASI quad-2 set and the run-64 ASI / run-63 CORLA sets, which suggests the same coordinated/machine operator, but no entity collapse is applied - counted per wallet with this note, as in run 60 GrokBot / run 63 CORLA / run 64-65 ASI precedents",
    "auto_mint_block": "Trigger >25% met numerically for both (27 >= 14) but BLOCKED at guard (c): paid PCS tokens, no free-mint quota/path for the user wallet - buying would cost BNB, never a free mint; guard (a) website also unverified (no name, no website evidence). No preview, no execution. Do not re-report the block unless a genuine free-mint path appears for these contracts.",
    "deployments_context": "58 contract-creation txs by 22 tracked wallets in window, all receipts read (58 addresses, 0 unreadable); NEITHER new token was deployed in this window - both predate it. Top deployers: 0xca4e67bb 10, 0xc0c84518 9, 0xdb2d83f9 5, 0xb940e4cd 4, 0x3a39aa05 3."
}
s["paid_trend_run66"] = {
    "note": "Aggregate only, NOT a buy recommendation. Two tokens reach the signal threshold (see paid_signal_run66).",
    "max_wallets_per_token": 27,
    "distribution": "27 paid tokens: 27 wallets x2, 3 wallets x13, 2 wallets x6, 1 wallet x6",
    "other_paid_activity": [
        {"pattern": "13 tokens ...7777 at 3 wallets each (the usual ...7777 machine churn set: 0x38031ca8/0xad94ee77/0xc7c5faa2) + 6 tokens at 2 wallets each + 6 tokens at 1 wallet each - below threshold, far below the 27-wallet rotation", "wallets": "machine set subsets"},
        {"pattern": "AFeng 0 txs this run; 0x2325... 0 txs; 0x8e96... 2 txs; 0x7488... 14 txs (PCS micro buy/sell pattern)", "wallet": "0xbf004bff64725914ee36d03b87d6965b0ced4903 / 0x2325f175975abdbcde555c79cc8e63381d28551b / 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6 / 0x7488d5da6a6097de0ff88c7492c62c2fd1e56650"},
        {"pattern": "1 failed PCS sell (status 0, selector 0x791ac947, value 0): 0x36239612 01:20:11 WIB - failed sell, not a mint", "wallet": "0x362396125a55d932a09f0a5182140cbbcaf30b70"}
    ],
    "deployments": "58 contract creations by 22 tracked wallets in window, all status 1 (receipts read, 0 unreadable); see paid_signal_run66.deployments_context",
    "future1001": "0 tx this run (0x355ea9e542b36c645a2dee63b9df079ccb9bf3db)"
}
s["inbound_log_leg_run66"] = {
    "contracts": 960,
    "total_logs": 10564,
    "hits": 0,
    "failed": 6,
    "failed_contracts": [
        "0x339df8fa35078dfb947e8cd1e2a85da62cd17ecb",
        "0x33a8db53339a0c37246216b45394e7e56b3c7d1e",
        "0x355286c54af4cecf07e13a0aef6ad36ee4d27fb8",
        "0x9adca6b0777fd8cd5b4795f885c7d5c5f98eea6b",
        "0x9b5a55dbc77cd41d0b79b45119c300f2a20288db",
        "0x9cc4d56e6ce5c0ddade134b932023b5cab2458d8"
    ],
    "note": "Ankr getLogs address-filtered per contract, window 131862392-131870174, parts a (0-400, 6202 logs, 3 truncated cleaned topic-filtered 0x55d3..., 0x6288... AGC sale, 0x63de... AGC - all 0 logs) + b (400-900, 3532 logs per progress line, 0 truncated; process killed by service restart at 500/560) + b2 re-run of remaining 60 (900-960, 830 logs, 0 hits, 0 failed). Coverage complete: all 960 sorted contracts checked once. 6 failed contracts are transient Ankr 'Remote end closed connection without response' - retry next run; inbound-only mints from them are UNVERIFIED this run, not zero. DYOR 0x8695... in set (via snapshot), 0 hits. No residual open except the 6 failed contracts. CORLA 0x4a9c + 4 run-64 ASI + 4 run-65 ASI quad-2 + the 2 run-66 tokens not in inbound set (PCS tokens; sent-pass covered). New contracts deployed this hour (58) are not in the inbound set - inbound-only mints from them would be unverified by this leg (same method limitation as prior runs)."
}
json.dump(s, open(P, "w"), indent=1)
print("state updated: run", s["last_run"]["run"], "signaled total", len(sig))
print("paid_signal_run66 + paid_trend_run66 + inbound_log_leg_run66 written")
