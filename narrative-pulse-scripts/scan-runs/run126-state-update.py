#!/usr/bin/env python3
"""Run 126 state update (read-only bookkeeping): last_run + paid_trend_run126 +
inbound_log_leg_run126. No new mints this run, so no new reported_findings
entries. No preview/mint/sign/login."""
import json, shutil
from pathlib import Path

HOME = Path.home()
NP = HOME / "workspace/narrative-pulse"
STATE = NP / "tracked-wallet-mint-scan-state.json"
shutil.copy(STATE, NP / "tracked-wallet-mint-scan-state.json.bak-run126-pre")
s = json.load(open(STATE))

s["last_run"] = {
 "run": 126,
 "block_start": 132413939,
 "block_end": 132422090,
 "window_wib": "2026-11-08 22:08:45 - 2026-11-08 23:09:37 WIB (tx times); run executed ~23:07 WIB - ~00:05 WIB; sent-pass in-window txs 209, 0 mint-pattern txs",
 "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set); 0 FAILED first attempt. 8 wallets active (AFeng 0xbf00... 47, 0xad94ee77 40, 0x38031ca8 40, 0xc7c5faa2 39, 0xa0c1e94f 16, 0x3628764a 15, 0x7488d5da 9, 0x2325f175 3); future1001.ai 0 txs; 0x81c3d1b4 0 txs; 0x89220022 0 txs; 0x6ba79dcc 0 txs.",
 "method_note": "Sent pass Ankr ankr_getTransactionsByAddress via module: 55/55 OK first attempt (209 txs), 0 failed. Receipts via fast_rpc batch (6, ~4s pause) for 138 non-approve candidates: 138 status 1, 0 status 0, 0 NULL - no race fallbacks. 0 mint logs in any receipt - third straight zero-mint run (runs 124, 125, 126; first zero-mint run since run 14 was run 124). AFeng (0xbf00...) 47 txs: 30 sale-calls 0x4d819a2a to 0x1de4... total 8.72266833 BNB (max single 2.28691708 BNB - largest AFeng sale-call volume + largest single sale-call seen so far; run 124: 17 calls/4.775 BNB, run 125: 7 calls/3.625 BNB) + 17 approvals, 0 mint logs, so the dividend-tracker pattern of runs 70/75/101/102/113 did NOT repeat this run (runs 114-126: no repeat). 0x2325... 3 txs: 2 aggregator 0x27772d13 to 0x296b... (1 value 0 with 25 logs + 1 value 0.1 BNB with 11 logs) + 1 approval, 0 mint logs, 0 receives. Paid: 32 tokens; max 3 wallets/token (14 tokens at 3 wallets, ALL the same churn trio 0x3803/0xad94/0xc7c5, all ...7777; 5 at 2 - pair 0x3628/0xa0c1; 13 at 1). Overlap with run-125 paid tokens: 0 - the ...7777 churn set itself turned over COMPLETELY again - twenty-third straight run with 0 churn overlap (runs 104-126 also 0). ZERO new rotations - the 27-wallet machine set had 0 txs this run (no buys, no sells, no approvals from any of the 27; verified overlap with active wallets = empty). The named-rotation streak ENDED run 104 (runs 97-103); run 126 has 0, twenty-third straight quiet run. No anomaly to report under the fast-path amendment (no new machine token, no name/symbol appearing, no size anomaly among machine buys, no free-mint path; churn trio PCS buys 28 txs total only 0.00098 BNB - pure micro churn; AFeng sale-calls 8.72 BNB are the known dividend-tracker shape, not machine buys; 0x2325 aggregator calls are mostly value 0 / tiny, not machine buys). Trigger >25% NOT met by any token (max 3 wallets = 5.5%). No preview, no execution. Seatbelt 1e9c STALLED at 26: 0 wallets this run (0 buys, 0 sells) - sell-wallet union run101+run102 = 26/27, runs 103-126 add 0 - did NOT reach 27. NOT a new rotation; watch run 127 the same way. Deployments: ZERO - twenty-third straight run without deployments (run 104: 0, run 105: 0, run 106: 0, run 107: 0, run 108: 0, run 109: 0, run 110: 0, run 111: 0, run 112: 0, run 113: 0, run 114: 0, run 115: 0, run 116: 0, run 117: 0, run 118: 0, run 119: 0, run 120: 0, run 121: 0, run 122: 0, run 123: 0, run 124: 0, run 125: 0, run 126: 0; runs 97-103 had 25/72/64/32/35/70/68) - verified from raw receipts contractAddress fields, not the parsed JSON. Inbound list for run 126 = run125 list (1734) + 0 deployments + 0 new rotation tokens (total 1734, unchanged). 1 plain BNB transfer this run (0xc7c5... -> usual recipient 0x7f51d464..., 0.000126 BNB, 22:28:50 WIB; runs 113: 2, run 114: 1, run 115: 0, run 116: 0, run 117: 2, run 118: 1, run 119: 1, run 120: 0, run 121: 2, run 122: 1, run 123: 3, run 124: 0, run 125: 0, run 126: 1). Selectors (sent pass, 209 txs): 71 approvals (0x095ea7b3) + 38 PCS sells (0x791ac947) + 41 PCS buys (0xb6f9de95) + 26 aggregator (0x39ecce49) + 30 sale-calls (0x4d819a2a, AFeng) + 2 aggregator (0x27772d13, 0x2325) + 1 empty-input. NO contract creations. Nonzero-value txs 70, total 8.82729050 BNB, max 2.28691708 BNB (AFeng sale-call; churn micro total only 0.00098 BNB PCS buys). Most active wallets: 0xbf004bff 47, 0xad94ee77 40, 0x38031ca8 40, 0xc7c5faa2 39, 0xa0c1e94f 16, 0x3628764a 15, 0x7488d5da 9, 0x2325f175 3. 0 NULL receipts this run. 0 status-0 txs. Inbound leg (amendment 12:02 WIB): Ankr getLogs address-filtered per contract, 1734 contracts, 13397 logs (12372 slices + 1025 retry), window 132413939-132422090, 0 hits, 0 inbound-only new. 35 slices of ~50 contracts in 6 parallel rounds (detached via setsid/nohup; rounds ~5-9 min each, Ankr slow this run). 27 in-slice failures (Ankr 'Remote end closed connection without response') - 26 recovered SAME-RUN via run126-inbound-retry.py (1025 logs, 0 hits); 1 contract STILL FAILED after retry (0x38cb... Anonymous Agent token - Ankr remote-end closed in slice AND retry) - recorded as residual, retry run 127; window otherwise FULLY CLOSED in-run. 7 truncated contracts: 6 topic-filtered to 0 logs, 1 (0x6288...) topic-filtered ERROR in slice but recovered in retry (topic-filtered logs=0) - closed. Pair retry 8/8 FAILED this run (all eight pairs: a6e6/887c/2bfb/c459/43c8/cfdb/0cf8/e68b - token0()/token1() all 'all endpoints failed' via fast_rpc race, OSError/TimeoutError) - unverified, not absence; 44th consecutive run for a6e6/887c/2bfb/c459, 39th for 43c8, 38th for cfdb/0cf8/e68b; retry run 127. fast_rpc race outage TOTAL during the pair retry AND the pointer first pass again - but the receipts batch pass worked fine earlier in the same run, so the outage is time-varying, not permanent. A failed race read is UNVERIFIED, never absence - retry, don't conclude. Pointer-discovery (amendment 19:10 WIB, cap 5/run, backfill 5 oldest gate=None: run-2 Talvio + run-3 entries): Talvio Generator website VERIFIED via pointer (tokenURI #20 -> talviogenerate.com metadata host; site root https://talviogenerate.com/ fetched HTTP 200, prints the exact contract) - bridge gate website_verified_via_pointer (NOT in Free Bacot snapshot, hint for routine job only, NOT a new lead by scan job). Proof of AGI website_no_pointer_found: tokenURI #201 -> poagi.top metadata JSON (no external_url, does not print contract); site root poagi.top HTTP 200 does NOT print contract = metadata host only; contractURI read failed both passes (race timeout), Sourcify 404. Plasmagent + Hackagent website_no_pointer_found: contractURI + tokenURI both base64 JSON decoded IN FULL (8679 / 9136 chars) - name/description/on-chain SVG image only, no external_url/website/URL anywhere; Sourcify only generic docs/GitHub URLs; ABI no site functions. Chocho Agent website_no_pointer_found WITH CAVEAT: contractURI + tokenURI reads FAILED on all retries (fast_rpc race timeouts) - pointer incomplete, not proven absent; Sourcify only generic URLs. Bridge: 116 contracts (12 verified via pointer, 98 no-pointer, 6 still queued). CHAT REPORT this run: NONE (silent) - 0 new mints, no Free Bacot signal, no anomaly, no auto-mint trigger, no guard block. No preview/mint/sign/login/purchase by this job."
}

s["paid_trend_run126"] = ("32 tokens paid-bought; max 3 wallets/token (14 at 3, all churn trio 0x3803/0xad94/0xc7c5; "
 "5 at 2 - pair 0x3628/0xa0c1; 13 at 1); overlap vs run 125: 0 tokens (churn set itself turned over completely, 23rd straight run); "
 "0x2325 3 txs (2 aggregator calls to 0x296b...: 1 value 0 + 1 value 0.1 BNB; 1 approval; 0 mint logs, 0 receives); "
 "AFeng 47 txs (30 sale-calls 0x4d819a2a to 0x1de4... total 8.72266833 BNB, max single 2.28691708 BNB - largest AFeng sale-call volume + largest single sale-call seen so far; 17 approvals; 0 mint logs - tracker pattern did NOT repeat); "
 "0x89220022 quiet (0 txs); future1001.ai 0 txs; 0x81c3d1b4 0 txs; 0x6ba79dcc 0 txs; "
 "sent pass 55/55 first attempt; total nonzero value 8.82729050 BNB across 70 txs, max single 2.28691708 BNB (AFeng sale-call; churn micro total only 0.00098 BNB PCS buys); "
 "1 plain BNB transfer this run (0xc7c5 -> usual 0x7f51d464..., 0.000126 BNB); 0 deployments (23rd straight run); 0 machine-set activity (23rd straight quiet run).")

s["inbound_log_leg_run126"] = ("Ankr getLogs address-filtered, 1734 contracts, 13397 logs (12372 slices + 1025 same-run retry), 0 hits, 0 inbound-only, "
 "27 in-slice failures, 26 recovered same-run via retry (1025 logs, 0 hits); 1 contract STILL FAILED after retry (0x38cb... Anonymous Agent token, Ankr remote-end closed in slice AND retry) - residual, retry run 127; "
 "7 truncated contracts: 6 topic-filtered to 0 logs, 1 (0x6288...) recovered in retry (topic-filtered 0 logs) - window otherwise FULLY CLOSED in-run.")

n = s.get("next_run_note", "")
repls = [
 ("Next run sent-tx window starts from block 132413940. RETRY run 126:",
  "Next run sent-tx window starts from block 132422091. RETRY run 127:"),
 ("43 consecutive runs", "44 consecutive runs"),
 ("(unreadable run 88-125, 38 consecutive", "(unreadable run 88-126, 39 consecutive"),
 ("(token0/token1 unreadable run 89-125, 37 consecutive", "(token0/token1 unreadable run 89-126, 38 consecutive"),
 ("0 wallets runs 103-125", "0 wallets runs 103-126"),
 ("0 wallets runs 91-125, 35th quiet run", "0 wallets runs 91-126, 36th quiet run"),
 ("0 wallets runs 90-125, 36th quiet run", "0 wallets runs 90-126, 37th quiet run"),
]
for old, new in repls:
    if old in n:
        n = n.replace(old, new, 1)
        print(f"replaced: {old[:60]}...")
    else:
        print(f"NOT FOUND (skipped): {old[:80]}")
n = ("(Run 126: inbound list = run125 list (1734) + 0 deployments + 0 new rotation tokens; window 132413939-132422090, 0 hits, 0 inbound-only, 27 in-slice failures, 26 recovered same-run via retry (1025 logs, 0 hits); 1 contract STILL FAILED after retry (0x38cb... Anonymous Agent token) - residual, retry run 127; 7 truncated, 6 topic-filtered 0 logs, 1 (0x6288...) recovered in retry; sent pass 55/55 first attempt; 0 mint logs (third straight zero-mint run, runs 124-126); "
     "Talvio Generator website VERIFIED via pointer (talviogenerate.com, run-126 backfill; NOT in Free Bacot snapshot, hint only); Proof of AGI metadata host only (poagi.top root does not print contract); Plasmagent/Hackagent base64 JSON no URLs; Chocho pointer incomplete (reads failed all retries - caveat); bridge 116 (12 verified / 98 no-pointer / 6 queued); "
     "1e9c still STALLED 26/27, 1153 STALLED 26, 79cd STALLED 20; 0x2325 3 txs (2 aggregator, 1 value 0 + 0.1 BNB); 0x89220022 quiet (0 txs); "
     "AFeng 47 txs (30 sale-calls 8.72266833 BNB, max single 2.28691708 BNB - largest AFeng sale-call volume so far, 0 mint logs - tracker pattern did NOT repeat, runs 114-126); future1001.ai 0 txs; 0x81c3d1b4 0 txs; "
     "paid overlap vs run 125: 0 (churn set itself turned over completely, 23rd straight run); total value 8.82729050 BNB (max 2.28691708 BNB); "
     "1 plain BNB transfer this run (0xc7c5 -> usual 0x7f51d464..., 0.000126 BNB); 0 deployments (23rd straight run).) " + n)
s["next_run_note"] = n

json.dump(s, open(STATE, "w"), indent=1)
print("state updated: last_run=126, paid_trend_run126 + inbound_log_leg_run126 added, 0 new reported_findings entries")
print("next window starts 132422091")
print("backup:", NP / "tracked-wallet-mint-scan-state.json.bak-run126-pre")
