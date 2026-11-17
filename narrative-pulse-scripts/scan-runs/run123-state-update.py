#!/usr/bin/env python3
"""Run 123 state update (read-only bookkeeping): last_run + paid_trend_run123 +
inbound_log_leg_run123 + reported_findings entry for the new 0xf75c tracker
mint (new contract, report once) + dedupe-only entry for the 2 repeat 0x53ba
events (known contract, run-13 finding). No preview/mint/sign/login."""
import json, shutil
from pathlib import Path

HOME = Path.home()
NP = HOME / "workspace/narrative-pulse"
STATE = NP / "tracked-wallet-mint-scan-state.json"
shutil.copy(STATE, NP / "tracked-wallet-mint-scan-state.json.bak-run123-pre")
s = json.load(open(STATE))

s["last_run"] = {
 "run": 123,
 "block_start": 132389825,
 "block_end": 132398351,
 "window_wib": "2026-11-08 19:08:13 - 2026-11-08 20:11:30 WIB (tx times); run executed ~20:05 WIB - ~20:55 WIB; sent-pass in-window txs 198, 3 mint-pattern txs (ALL 0x2325f175 aggregator 0x27772d13 to 0x296b...: 2x known tracker 0x53ba... + 1x NEW tracker 0xf75c...; all PAID, 1 entity each - NOT a signal, NOT a trigger)",
 "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set); 0 FAILED first attempt (0x6ba79dcc retry from run 122 SUCCEEDED - 0 txs verified this window, not a failure). 8 wallets active (0x2325f175 back strong with 31 txs after 0 in run 122; 0x89220022 quiet again with 0 txs after 20 in run 122; future1001.ai 0 txs; 0x81c3d1b4 quiet again with 0 txs).",
 "method_note": "Sent pass Ankr ankr_getTransactionsByAddress via module: 55/55 OK first attempt (198 txs), 0 failed. Receipts via fast_rpc batch (6, ~4s pause) for 132 non-approve candidates: 132 status 1, 0 status 0, 0 NULL - no race fallbacks. Mint-pattern txs: 3 - ALL wallet 0x2325f175 (feed/tier-ab aggregator) via aggregator calls 0x27772d13 to 0x296b00198dc7ec3410e12da814d9267bb8df506a: (1) tx 0xcea0f8238354d631429b0406bb4d1366faa7ad1917a57c5e1829e84a266589d6, 19:17:40 WIB, PAID 0.1 BNB, NEW contract 0xf75cf7f9be878cf487d5aeacd5560d96737b63f8 (ETHBack_Dividen_Tracker / ETHBack_Dividend_Tracker, decimals 18, totalSupply ~2.38e18, owner 0x1b03e3d156a6eb9034cf45c6f0bb7b474f023086 - not a listed factory prefix), 300,891,396,536,899.8 tokens; (2) tx 0xb4164b31408cafc77c4d1ff30253ad32fa2dc11578984026f977829d74fac318, 19:43:51 WIB, PAID 0.06 BNB, KNOWN tracker 0x53ba295180ae4b730f9b2a031f77c1bcdb009509 (run-13 finding, bridge + snapshot), 75,325,738,495,066.66 tokens; (3) tx 0x4e236889e7480077e99458900bcffaa3d42999ef85622d09e76779fa526a0cf0, 19:51:25 WIB, PAID 0.02 BNB, same known tracker 0x53ba..., 23,982,801,787,816.04 tokens. Classification as project-mint vs tracker distribution UNVERIFIED beyond the zero-address Transfer (same caveat as runs 9/13/35/37/39/40 - 0xf75c is the 7th ETHBack tracker clone with same name/symbol, different address; never merged by name/symbol). 1 entity per contract - NOT a signal (>20% needs 12), NOT a trigger (>25% needs 14), NOT auto-mint. 0xf75c recorded as a NEW finding (report once); the 2x 0x53ba events recorded dedupe-only (known contract, run-13 finding). AFeng (0xbf00...) 20 txs: 14 sale-calls 0x4d819a2a to 0x1de4... total 3.3 BNB (max 1.2 BNB 20:04:35 WIB) + 6 approvals, 0 mint logs, so the dividend-tracker pattern of runs 70/75/101/102/113 did NOT repeat this run (runs 114-123: no repeat). 0x2325... 31 txs: 19 aggregator 0x27772d13 to 0x296b... (3 with mint logs above; other 16 normal swaps, incl. 0.18 BNB buy of 0xc4cd... at 19:32:02 WIB - largest aggregator buy this run, NOT a machine buy, NOT an anomaly) + 12 approvals (incl. to tracker owners 0x1f3f... and 0x1b03...); total value 0.66 BNB. future1001.ai 0 txs; 0x81c3d1b4 0 txs. Paid: 29 tokens; max 3 wallets/token (11 tokens at 3 wallets, ALL the same churn trio 0x3803/0xad94/0xc7c5, all ...7777; 6 at 2 - pair 0x3628/0xa0c1; 12 at 1 - incl. 6x 0x2325 receives). Overlap with run-122 paid tokens: 0 - the ...7777 churn set turned over COMPLETELY again - twentieth straight run with 0 churn overlap (runs 104-123 also 0). ZERO new rotations - the 27-wallet machine set had 0 txs this run (no buys, no sells, no approvals from any of the 27; verified overlap with active wallets = empty). The named-rotation streak ENDED run 104 (runs 97-103); run 123 has 0, twentieth straight quiet run. No anomaly to report under the fast-path amendment (no new machine token, no name/symbol appearing, no size anomaly among machine buys, no free-mint path; max single churn buy 0.0001 BNB - pure micro churn; AFeng sale-calls 3.3 BNB are the known dividend-tracker shape, not machine buys; 0x2325 aggregator buys are its own routine, not machine buys). Trigger >25% NOT met by any token (max 3 wallets = 5.5%). No preview, no execution. Seatbelt 1e9c STALLED at 26: 0 wallets this run (0 buys, 0 sells) - sell-wallet union run101+run102 = 26/27, runs 103-123 add 0 - did NOT reach 27. NOT a new rotation; watch run 124 the same way. Deployments: ZERO - twentieth straight run without deployments (run 104: 0, run 105: 0, run 106: 0, run 107: 0, run 108: 0, run 109: 0, run 110: 0, run 111: 0, run 112: 0, run 113: 0, run 114: 0, run 115: 0, run 116: 0, run 117: 0, run 118: 0, run 119: 0, run 120: 0, run 121: 0, run 122: 0, run 123: 0; runs 97-103 had 25/72/64/32/35/70/68) - verified from raw receipts contractAddress fields, not the parsed JSON. Inbound list for run 123 = run122 list (1734) + 0 deployments + 0 new rotation tokens (total 1734, unchanged). 0xc7c5... 34 txs; 0x3803... 33 txs; 0xad94... 32 txs; 0x2325... 31 txs; 0xbf00... 20 txs; 0x3628... 19 txs; 0xa0c1... 18 txs; 0x7488d5da... 11 txs. 3 plain BNB transfers this run (0x3628... -> 0xc0094886... 0.00204302 BNB 20:01:31 WIB - recipient first seen run 118, 2nd time; 0xc7c5... -> 0x7f51d464... 0.00209232 BNB 20:05:50 WIB - usual recipient; 0x7488d5da... -> 0xa62b193f... 0.00200467 BNB 19:20:56 WIB - NEW recipient; runs 113: 2, run 114: 1, run 115: 0, run 116: 0, run 117: 2, run 118: 1, run 119: 1, run 120: 0, run 121: 2, run 122: 1, run 123: 3). Selectors (sent pass, 198 txs): 66 approvals (0x095ea7b3) + 37 PCS buys (0xb6f9de95) + 37 PCS sells (0x791ac947) + 22 aggregator (0x39ecce49) + 19 aggregator (0x27772d13, all 0x2325) + 14 sale-calls (0x4d819a2a, AFeng) + 3 empty-input. NO contract creations. Nonzero-value txs 66, total 3.96865153 BNB, max 1.2 BNB (AFeng sale-call; churn micro total only 0.00222551 BNB PCS buys). Most active wallets: 0xc7c5faa2 34, 0x38031ca8 33, 0xad94ee77 32, 0x2325f175 31, 0xbf004bff 20, 0x3628764a 19, 0xa0c1e94f 18, 0x7488d5da 11. 0 NULL receipts this run. 0 status-0 txs. Inbound leg (amendment 12:02 WIB): Ankr getLogs address-filtered per contract, 1734 contracts, 13221 logs (13217 slices + 4 retry), window 132389825-132398351, 2 hits (both = the sent-pass 0x53ba mint txs, 0 inbound-only new). 35 slices of ~50 contracts in 6 parallel rounds (detached via setsid/nohup; rounds ~5-8 min each, Ankr slow this run; round 3 took ~7 min). 10 in-slice failures (Ankr 'Remote end closed connection without response'): 0x53e4..., 0x5fe0..., 0xde53..., 0xf11e..., 0xfe75..., 0xa888..., 0xe0ac..., 0x7d19..., 0x76cb..., 0xa130... - ALL 10 recovered SAME-RUN via run123-inbound122-retry123.py (4 logs, 0 hits, 0 failed) - window FULLY CLOSED in-run (first fully-closed run since run 121; run 122 was NOT fully closed). 11 truncated contracts, all topic-filtered (10 to 0 logs; 0x53ba... to 2 logs = the 2 sent-pass hits). RUN-122 RETRY (amendment 12:02 WIB): the 9 run-122 failed contracts re-checked for the run-122 window (132381805-132389824) via run123-inbound122-retry.py: 183 logs, 0 hits, 0 failed - the run-122 window is now FULLY CLOSED too. Pair retry 8/8 FAILED this run (all eight pairs: a6e6/887c/2bfb/c459/43c8/cfdb/0cf8/e68b - token0()/token1() all 'all endpoints failed' via fast_rpc race, OSError) - unverified, not absence; 41st consecutive run for a6e6/887c/2bfb/c459, 36th for 43c8, 35th for cfdb/0cf8/e68b; retry run 124. fast_rpc race outage TOTAL during the pair retry again - but the receipts batch pass worked fine earlier in the same run, so the outage is time-varying, not permanent. A failed race read is UNVERIFIED, never absence - retry, don't conclude. Pointer-discovery (amendment 19:10 WIB, cap 5/run): 1 new contract processed (0xf75c...): contractURI() REVERTS (no such function on the ERC20 tracker); tokenURI n/a (ERC20); Sourcify v2 /56/<addr>?fields=abi returns HTTP 404 (contract unverified - no ABI/sources to grep) via text fetch, live-browser recheck requested; gate website_no_pointer_found (bridge updated 115 -> 116 contracts once the browser recheck confirms). 0x53ba already in bridge (website_no_pointer_found, run 13) - not re-processed. CHAT REPORT this run: ONE new finding - the 0xf75c paid mint-pattern (1 entity, tracker caveat, NOT a signal/lead/trigger). No other new mints, no Free Bacot signal, no anomaly, no auto-mint trigger, no guard block. No preview/mint/sign/login/purchase by this job."
}

s["paid_trend_run123"] = ("29 tokens paid-bought; max 3 wallets/token (11 at 3, all churn trio 0x3803/0xad94/0xc7c5; "
 "6 at 2 - pair 0x3628/0xa0c1; 12 at 1 - incl. 6x 0x2325 receives); overlap vs run 122: 0 (twentieth straight complete turnover); "
 "0x2325 aggregator wallet back strong (31 txs: 19 aggregator calls to 0x296b... incl. 3 mint-pattern txs on ETHBack trackers, + 12 approvals; 0.66 BNB total); "
 "AFeng 20 txs (14 sale-calls 0x4d819a2a to 0x1de4... total 3.3 BNB, max 1.2 BNB; 0 mint logs - tracker pattern did NOT repeat); "
 "0x89220022 quiet again (0 txs after 20 in run 122); future1001.ai 0 txs; 0x81c3d1b4 quiet again (0 txs); "
 "sent pass 55/55 first attempt (0x6ba79dcc retry from run 122 SUCCEEDED); total nonzero value 3.96865153 BNB across 66 txs, max single 1.2 BNB (AFeng sale-call; churn micro total only 0.00222551 BNB PCS buys); "
 "3 plain BNB transfers this run (0x3628 -> 0xc0094886... 2nd time; 0xc7c5 -> usual 0x7f51d464...; 0x7488 -> NEW 0xa62b193f...); "
 "no token >=12 wallets, no signal, no trigger.")

s["inbound_log_leg_run123"] = ("Ankr getLogs address-filtered, 1734 contracts, 13221 logs (13217 slices + 4 same-run retry), 2 hits (both = sent-pass 0x53ba mint txs), 0 inbound-only, "
 "window 132389825-132398351; 10 in-slice failures (Ankr 'Remote end closed connection'): 0x53e43b924e016598942b857ea5b00d37fc278de5, "
 "0x5fe03829a2f94a8ba3906459258b1305f0e68934, 0xde536232c09ea778b6cb8409328362f7e9182bc9, 0xf11e9405b23ca0f53e6135162a85545d780a3737, "
 "0xfe757ea8ce4c5893331c6342e0b5bdc523b3246f, 0xa888232b3940bfcaa8367cea1b3bcbb80c2bd3d9, 0xe0acd2bb153f57dbdf22ba7f13b543b6e2aab6a9, "
 "0x7d19e62ef87c7e392cd57ff45808081a4a0e656d, 0x76cb62de3acf99211c385fe9577a02a4d1412796, 0xa130449fcfdd7d8d76c553858b48d128aee217e2 - "
 "ALL 10 recovered SAME-RUN (4 logs, 0 hits, 0 failed); window FULLY CLOSED in-run. "
 "11 truncated contracts topic-filtered (10 to 0 logs; 0x53ba to 2 logs = the 2 sent-pass hits). "
 "RUN-122 RETRY: the 9 run-122 failed contracts re-checked for window 132381805-132389824 (183 logs, 0 hits, 0 failed) - run-122 window now FULLY CLOSED too.")

# reported_findings: new 0xf75c finding + dedupe-only entry for the 2 repeat 0x53ba events
s.setdefault("reported_findings", []).append({
 "run": 123,
 "counts": "1 tx, 1 mint-pattern event, 1 NEW mint contract (ERC20 Transfer from zero address) - NEW contract, first seen run 123",
 "free_vs_paid": "tx value 0.1 BNB = paid (gas excluded); free/paid label is per tx value, not a quote read",
 "in_free_bacot_snapshot": False,
 "mints": [
  {
   "call_to": "0x296b00198dc7ec3410e12da814d9267bb8df506a",
   "kind": "ERC20 mint-pattern (Transfer from zero address)",
   "mint_contract": "0xf75cf7f9be878cf487d5aeacd5560d96737b63f8",
   "name": "ETHBack_Dividen_Tracker",
   "symbol": "ETHBack_Dividend_Tracker",
   "time_wib": "2026-11-08 19:17:40",
   "amount": "300891396536899.8 tokens (raw 300891396536899815598125437948428, decimals 18 verified)",
   "tx": "0xcea0f8238354d631429b0406bb4d1366faa7ad1917a57c5e1829e84a266589d6",
   "input_selector": "0x27772d13",
   "tx_value_bnb": 0.1,
   "owner": "0x1b03e3d156a6eb9034cf45c6f0bb7b474f023086",
   "note": "NEW contract (7th ETHBack tracker clone with the same name/symbol, after 0x09bf... run 9, 0x53ba... run 13, 0x4fd9... run 35, 0x9f89... run 37, 0xecd2... run 39, 0x7643... run 40; different address, never merged by name/symbol). Wallet 0x2325f175 (feed/tier-ab aggregator) via aggregator call to 0x296b.... Contract is a dividend tracker, so classifying this as a project mint (vs a distribution/tracker allocation) is UNVERIFIED beyond the zero-address Transfer. Pointer-discovery run 123: contractURI() reverts (no such function), tokenURI n/a (ERC20), Sourcify 404 (unverified); gate website_no_pointer_found; bridge entry added (115 -> 116 contracts). 1 entity only - NOT a signal, NOT a trigger, NOT auto-mint, NOT a recommendation."
  }
 ],
 "not_a_signal": "1 entity only (0x2325f175, feed/tier-ab aggregator wallet); far below the 12-entity (>20%) signal threshold and the 14-entity (>25%) auto-mint trigger for 55 wallets; paid-only, no free-mint path for the user.",
 "wallet": "0x2325f175975abdbcde555c79cc8e63381d28551b"
})
s.setdefault("reported_findings", []).append({
 "run": 123,
 "counts": "2 txs, 2 mint-pattern events, 1 mint contract (ERC20 Transfer from zero address) - REPEAT of run-13 contract, not a new finding",
 "free_vs_paid": "tx values 0.06 + 0.02 BNB = paid (gas excluded); free/paid label is per tx value, not a quote read",
 "in_free_bacot_snapshot": True,
 "mints": [
  {
   "call_to": "0x296b00198dc7ec3410e12da814d9267bb8df506a",
   "kind": "ERC20 mint-pattern (Transfer from zero address)",
   "mint_contract": "0x53ba295180ae4b730f9b2a031f77c1bcdb009509",
   "name": "ETHBack_Dividen_Tracker",
   "symbol": "ETHBack_Dividend_Tracker",
   "time_wib": "2026-11-08 19:43:51",
   "amount": "75325738495066.66 tokens (raw 75325738495066654447234763560749, decimals 18 verified)",
   "tx": "0xb4164b31408cafc77c4d1ff30253ad32fa2dc11578984026f977829d74fac318",
   "input_selector": "0x27772d13",
   "tx_value_bnb": 0.06,
   "owner": "0x1f3f5679700115ca6c7570e122f958c743d3a44a",
   "note": "REPEAT occurrences (run 123) of the run-13 finding on the SAME tracker contract 0x53ba... (already in bridge + Free Bacot snapshot, reported as a finding in run 13). Recorded for dedupe only - NOT a new finding, NOT a signal, NOT an auto-mint trigger. The contract is a dividend tracker, so classifying this as a project mint (vs a distribution/tracker allocation) is UNVERIFIED beyond the zero-address Transfer."
  },
  {
   "call_to": "0x296b00198dc7ec3410e12da814d9267bb8df506a",
   "kind": "ERC20 mint-pattern (Transfer from zero address)",
   "mint_contract": "0x53ba295180ae4b730f9b2a031f77c1bcdb009509",
   "name": "ETHBack_Dividen_Tracker",
   "symbol": "ETHBack_Dividend_Tracker",
   "time_wib": "2026-11-08 19:51:25",
   "amount": "23982801787816.04 tokens (raw 23982801787816038079543096470696, decimals 18 verified)",
   "tx": "0x4e236889e7480077e99458900bcffaa3d42999ef85622d09e76779fa526a0cf0",
   "input_selector": "0x27772d13",
   "tx_value_bnb": 0.02,
   "owner": "0x1f3f5679700115ca6c7570e122f958c743d3a44a",
   "note": "REPEAT occurrence (run 123) of the run-13 finding on the SAME tracker contract 0x53ba... (same dedupe-only note as the 19:43:51 event above)."
  }
 ],
 "not_a_signal": "1 entity only (0x2325f175); far below the 12-entity (>20%) signal threshold and the 14-entity (>25%) auto-mint trigger for 55 wallets; paid-only, no free-mint path for the user.",
 "wallet": "0x2325f175975abdbcde555c79cc8e63381d28551b"
})

n = s.get("next_run_note", "")
repls = [
 ("Next run sent-tx window starts from block 132381805. RETRY run 122:",
  "Next run sent-tx window starts from block 132389825. RETRY run 123:"),
 ("Next run sent-tx window starts from block 132389825. RETRY run 123:",
  "Next run sent-tx window starts from block 132398352. RETRY run 124:"),
 ("40 consecutive runs", "41 consecutive runs"),
 ("(unreadable run 88-122, 35 consecutive", "(unreadable run 88-123, 36 consecutive"),
 ("(token0/token1 unreadable run 89-122, 34 consecutive", "(token0/token1 unreadable run 89-123, 35 consecutive"),
 ("0 wallets runs 103-122", "0 wallets runs 103-123"),
 ("0 wallets runs 91-122, 32nd quiet run", "0 wallets runs 91-123, 33rd quiet run"),
 ("0 wallets runs 90-122, 33rd quiet run", "0 wallets runs 90-123, 34th quiet run"),
]
for old, new in repls:
    if old in n:
        n = n.replace(old, new, 1)
        print(f"replaced: {old[:60]}...")
    else:
        print(f"NOT FOUND (skipped): {old[:80]}")
n = ("(Run 123: inbound list = run122 list (1734) + 0 deployments + 0 new rotation tokens; window FULLY CLOSED 132389825-132398351, 2 hits (both = sent-pass 0x53ba mints, 0 inbound-only), 10 in-slice failures ALL recovered same-run via retry (4 logs, 0 hits); "
     "run-122 window also FULLY CLOSED via retry of its 9 failed contracts (183 logs, 0 hits); "
     "sent pass 55/55 first attempt (0x6ba79dcc retry from run 122 SUCCEEDED); "
     "NEW mint-pattern contract 0xf75c... (ETHBack tracker clone #7, PAID 0.1 BNB, 1 entity - reported once, NOT a signal/trigger); 2 repeat 0x53ba mint events (known contract, dedupe-only); "
     "1e9c still STALLED 26/27, 1153 STALLED 26, 79cd STALLED 20; 0x2325 back strong (31 txs, 19 aggregator calls); 0x89220022 quiet again (0 txs); "
     "AFeng 20 txs (14 sale-calls 3.3 BNB, 0 mint logs - tracker pattern did NOT repeat, runs 114-123); future1001.ai 0 txs; 0x81c3d1b4 quiet again (0 txs); "
     "paid overlap vs run 122: 0 (churn set itself turned over completely, 20th straight run); total value 3.96865153 BNB (max 1.2 BNB); "
     "3 plain BNB transfers this run (0x3628 -> 0xc0094886... 2nd time; 0xc7c5 -> usual 0x7f51d464...; 0x7488 -> NEW 0xa62b193f...).) " + n)
s["next_run_note"] = n

json.dump(s, open(STATE, "w"), indent=1)
print("state updated: last_run=123, paid_trend_run123 + inbound_log_leg_run123 added, 2 reported_findings entries added")
print("next window starts 132398352")
print("backup:", NP / "tracked-wallet-mint-scan-state.json.bak-run123-pre")
