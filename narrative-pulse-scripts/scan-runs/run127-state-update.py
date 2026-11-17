#!/usr/bin/env python3
"""Run 127 state update (read-only bookkeeping): last_run + paid_trend_run127 +
inbound_log_leg_run127. No new mints this run, so no new reported_findings
entries. No preview/mint/sign/login."""
import json, shutil
from pathlib import Path

HOME = Path.home()
NP = HOME / "workspace/narrative-pulse"
STATE = NP / "tracked-wallet-mint-scan-state.json"
shutil.copy(STATE, NP / "tracked-wallet-mint-scan-state.json.bak-run127-pre")
s = json.load(open(STATE))

s["last_run"] = {
 "run": 127,
 "block_start": 132422090,
 "block_end": 132430114,
 "window_wib": "2026-11-08 23:11:33 - 2026-11-09 00:09:49 WIB (tx times); run executed ~00:05 WIB - ~00:50 WIB; sent-pass in-window txs 141, 0 mint-pattern txs",
 "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set); 0 FAILED first attempt. 6 wallets active (0x38031ca8 33, 0xc7c5faa2 32, 0xad94ee77 31, 0xa0c1e94f 17, 0x3628764a 16, 0x7488d5da 12); AFeng 0 txs; future1001.ai 0 txs; 0x2325f175 0 txs; 0x89220022 0 txs; 0x6ba79dcc 0 txs; 0x81c3d1b4 0 txs.",
 "method_note": "Sent pass Ankr ankr_getTransactionsByAddress via module: 55/55 OK first attempt (141 txs), 0 failed. Receipts via fast_rpc batch (6, ~4s pause) for 95 non-approve candidates: 95 status 1, 0 status 0, 0 NULL - no race fallbacks. 0 mint logs in any receipt - fourth straight zero-mint run (runs 124, 125, 126, 127; first zero-mint run since run 14 was run 124). NEW SHAPE: 0x38031ca8 made its first 0x4d819a2a sale-call to 0x1de4... (0.017 BNB, 23:44:44 WIB, receipt status 1, 6 logs, 0 mint logs) - a new actor on the AFeng sale-call path, tiny size (AFeng's own calls ran 0.25-2.29 BNB); NOT a mint, NOT the dividend-tracker mint pattern (no zero-from Transfer). 0x38031ca8 also sent 1 ERC20 transfer (0xa9059cbb) to 0x55d3... (value 0, 1 log, not a mint) and all 21 aggregator calls 0x39ecce49 this run. Paid: 21 tokens; max 3 wallets/token (10 tokens at 3 wallets, ALL the same churn trio 0x3803/0xad94/0xc7c5; 6 at 2 - pair 0x3628/0xa0c1; 5 at 1 - 4 by 0x7488, 1 by 0x3803). Overlap with run-126 paid tokens: 0 - the ...7777 churn set itself turned over COMPLETELY again - twenty-fourth straight run with 0 churn overlap (runs 104-127 also 0). ZERO new rotations - the 27-wallet machine set had 0 txs this run (no buys, no sells, no approvals from any of the 27; verified overlap with active wallets = empty). The named-rotation streak ENDED run 104 (runs 97-103); run 127 has 0, twenty-fourth straight quiet run. No anomaly to report under the fast-path amendment (no new machine token, no name/symbol appearing, no size anomaly among machine buys, no free-mint path; churn trio PCS buys 36 txs total only 0.00223 BNB - pure micro churn; 0x3803 sale-call 0.017 BNB is the known dividend-tracker shape, not a machine buy). Trigger >25% NOT met by any token (max 3 wallets = 5.5%). No preview, no execution. Seatbelt 1e9c STALLED at 26: 0 wallets this run (0 buys, 0 sells) - sell-wallet union run101+run102 = 26/27, runs 103-127 add 0 - did NOT reach 27. NOT a new rotation; watch run 128 the same way. Deployments: ZERO - twenty-fourth straight run without deployments (run 104: 0, run 105: 0, run 106: 0, run 107: 0, run 108: 0, run 109: 0, run 110: 0, run 111: 0, run 112: 0, run 113: 0, run 114: 0, run 115: 0, run 116: 0, run 117: 0, run 118: 0, run 119: 0, run 120: 0, run 121: 0, run 122: 0, run 123: 0, run 124: 0, run 125: 0, run 126: 0, run 127: 0; runs 97-103 had 25/72/64/32/35/70/68) - verified from raw receipts contractAddress fields, not the parsed JSON. Inbound list for run 127 = run126 list (1734) + 0 deployments + 0 new rotation tokens (total 1734, unchanged). 0 plain BNB transfers this run. Selectors (sent pass, 141 txs): 46 approvals (0x095ea7b3) + 36 PCS sells (0x791ac947) + 36 PCS buys (0xb6f9de95) + 21 aggregator (0x39ecce49, all 0x3803...) + 1 sale-call (0x4d819a2a, 0x3803... 0.017 BNB) + 1 ERC20 transfer (0xa9059cbb, 0x3803... to 0x55d3...). NO contract creations. Nonzero-value txs 47, total 0.01949237 BNB, max 0.017 BNB (0x3803 sale-call; churn micro PCS buys total only 0.00223 BNB). Most active wallets: 0x38031ca8 33, 0xc7c5faa2 32, 0xad94ee77 31, 0xa0c1e94f 17, 0x3628764a 16, 0x7488d5da 12. 0 NULL receipts this run. 0 status-0 txs. Inbound leg (amendment 12:02 WIB): Ankr getLogs address-filtered per contract, 1734 contracts, 12501 logs (12353 slices + 148 retry), window 132422090-132430114, 0 hits, 0 inbound-only new. 35 slices of ~50 contracts in 6 parallel rounds (rounds ~5-8 min each, Ankr slow this run). 10 in-slice failures (Ankr 'Remote end closed connection without response') - ALL recovered SAME-RUN via run127-inbound-retry.py (148 logs, 0 hits); window FULLY CLOSED in-run. Run-126 residual 0x38cb... (Anonymous Agent token) did NOT fail this run - covered in slices, 0 hits - residual CLOSED. 9 truncated contracts, all topic-filtered to 0 logs, no errors. Pair retry 8/8 FAILED again (all eight pairs: a6e6/887c/2bfb/c459/43c8/cfdb/0cf8/e68b - token0()/token1() all 'all endpoints failed' via fast_rpc race, OSError) - unverified, not absence; 45th consecutive run for a6e6/887c/2bfb/c459, 40th for 43c8, 39th for cfdb/0cf8/e68b; retry run 128. fast_rpc race outage TOTAL during the pair retry AND the pointer contractURI retries - but the receipts batch pass worked fine earlier in the same run, so the outage is time-varying, not permanent. A failed race read is UNVERIFIED, never absence - retry, don't conclude. Pointer-discovery (amendment 19:10 WIB, cap 5/run, backfill 5 oldest gate=None, run-3 entries): AgentOrb website VERIFIED via pointer (tokenURI #2063 -> orb.apeagent.online metadata JSON with external_url https://orb.apeagent.online/; site root https://orb.apeagent.online/ fetched HTTP 200, prints the exact contract) - bridge gate website_verified_via_pointer (already in Free Bacot snapshot as bridge-0x9da90fe3, hint for routine job only, NOT a new lead by scan job). Terragent, Hexagent, Dronegent website_no_pointer_found: contractURI + tokenURI base64 JSON decoded IN FULL - name/description/on-chain SVG image only, no external_url/website/URL anywhere; Sourcify only generic docs/GitHub URLs; ABI no site functions. Agentlings website_no_pointer_found WITH CAVEAT: tokenURI base64 JSON no URLs, Sourcify generic only, but contractURI read FAILED first pass AND retry (3 tries, race outage) - pointer incomplete, not proven absent. AgentOrb contractURI also failed first pass + retry (race outage) - does not change the verified outcome (tokenURI path verified). Bridge: 116 contracts (13 verified via pointer, 102 no-pointer, 1 still queued - Dronefarm 0x5063...). CHAT REPORT this run: NONE (silent) - 0 new mints, no Free Bacot signal, no anomaly, no auto-mint trigger, no guard block. No preview/mint/sign/login/purchase by this job."
}

s["paid_trend_run127"] = ("21 tokens paid-bought; max 3 wallets/token (10 at 3, all churn trio 0x3803/0xad94/0xc7c5; "
 "6 at 2 - pair 0x3628/0xa0c1; 5 at 1 - 4 by 0x7488, 1 by 0x3803); overlap vs run 126: 0 tokens (churn set itself turned over completely, 24th straight run); "
 "0x3803 first 0x4d819a2a sale-call to 0x1de4... (0.017 BNB, 23:44:44 WIB, 6 logs, 0 mint logs - new actor on AFeng sale-call path, tiny size) + 1 ERC20 transfer to 0x55d3... (value 0, not a mint) + all 21 aggregator calls 0x39ecce49; "
 "AFeng 0 txs; future1001.ai 0 txs; 0x2325 0 txs; 0x89220022 quiet (0 txs); 0x6ba79dcc 0 txs; 0x81c3d1b4 0 txs; "
 "sent pass 55/55 first attempt; total nonzero value 0.01949237 BNB across 47 txs, max single 0.017 BNB (0x3803 sale-call; churn micro PCS buys total only 0.00223 BNB); "
 "0 plain BNB transfers this run; 0 deployments (24th straight run); 0 machine-set activity (24th straight quiet run).")

s["inbound_log_leg_run127"] = ("Ankr getLogs address-filtered, 1734 contracts, 12501 logs (12353 slices + 148 same-run retry), 0 hits, 0 inbound-only, "
 "10 in-slice failures, ALL recovered same-run via retry (148 logs, 0 hits); window FULLY CLOSED in-run; "
 "run-126 residual 0x38cb... (Anonymous Agent token) did NOT fail this run - covered in slices, 0 hits - residual CLOSED; "
 "9 truncated contracts, all topic-filtered to 0 logs, no errors.")

n = s.get("next_run_note", "")
repls = [
 ("Next run sent-tx window starts from block 132422091. RETRY run 127:",
  "Next run sent-tx window starts from block 132430115. RETRY run 128:"),
 ("44 consecutive runs", "45 consecutive runs"),
 ("(unreadable run 88-126, 39 consecutive", "(unreadable run 88-127, 40 consecutive"),
 ("(token0/token1 unreadable run 89-126, 38 consecutive", "(token0/token1 unreadable run 89-127, 39 consecutive"),
 ("0 wallets runs 103-126", "0 wallets runs 103-127"),
 ("0 wallets runs 91-126, 36th quiet run", "0 wallets runs 91-127, 37th quiet run"),
 ("0 wallets runs 90-126, 37th quiet run", "0 wallets runs 90-127, 38th quiet run"),
]
for old, new in repls:
    if old in n:
        n = n.replace(old, new, 1)
        print(f"replaced: {old[:60]}...")
    else:
        print(f"NOT FOUND (skipped): {old[:80]}")
n = ("(Run 127: inbound list = run126 list (1734) + 0 deployments + 0 new rotation tokens; window 132422090-132430114, 0 hits, 0 inbound-only, 10 in-slice failures, ALL recovered same-run via retry (148 logs, 0 hits); window FULLY CLOSED in-run; run-126 residual 0x38cb... CLOSED (covered in slices, 0 hits); 9 truncated, all topic-filtered 0 logs; sent pass 55/55 first attempt; 0 mint logs (fourth straight zero-mint run, runs 124-127); "
     "AgentOrb website VERIFIED via pointer (orb.apeagent.online, run-127 backfill; already in Free Bacot snapshot as bridge-0x9da90fe3, hint only); Terragent/Hexagent/Dronegent base64 JSON no URLs; Agentlings pointer incomplete (contractURI failed first pass + retry - caveat); bridge 116 (13 verified / 102 no-pointer / 1 queued - Dronefarm 0x5063...); "
     "1e9c still STALLED 26/27, 1153 STALLED 26, 79cd STALLED 20; 0x3803 first 0x4d819a2a sale-call to 0x1de4... (0.017 BNB, tiny, 0 mint logs - new actor on AFeng sale-call path); 0x2325 0 txs; 0x89220022 quiet (0 txs); "
     "AFeng 0 txs; 0 sale-calls from AFeng this run (tracker pattern did NOT repeat, runs 114-127); future1001.ai 0 txs; 0x81c3d1b4 0 txs; "
     "paid overlap vs run 126: 0 (churn set itself turned over completely, 24th straight run); total value 0.01949237 BNB (max 0.017 BNB); "
     "0 plain BNB transfers this run; 0 deployments (24th straight run).) " + n)
s["next_run_note"] = n

json.dump(s, open(STATE, "w"), indent=1)
print("state updated: last_run=127, paid_trend_run127 + inbound_log_leg_run127 added, 0 new reported_findings entries")
print("next window starts 132430115")
print("backup:", NP / "tracked-wallet-mint-scan-state.json.bak-run127-pre")
