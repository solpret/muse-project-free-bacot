#!/usr/bin/env python3
"""Run 113 state update (read-only bookkeeping): last_run + paid_trend_run113 +
inbound_log_leg_run113 + repeat tracker finding in reported_findings. No preview/mint/sign/login."""
import json, shutil
from pathlib import Path

HOME = Path.home()
NP = HOME / "workspace/narrative-pulse"
STATE = NP / "tracked-wallet-mint-scan-state.json"
shutil.copy(STATE, NP / "tracked-wallet-mint-scan-state.json.bak-run113-pre")
s = json.load(open(STATE))

s["last_run"] = {
 "run": 113,
 "block_start": 132309618,
 "block_end": 132318095,
 "window_wib": "2026-11-08 09:08:29 - 2026-11-08 10:09:15 WIB (tx times); run executed ~10:05 WIB - ~10:55 WIB; sent-pass in-window txs 180, 1 mint-pattern tx (REPEAT of the already-reported run-70 dividend-tracker contract 0x636fdfa9, NOT a new mint - see below)",
 "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set); 55/55 first attempt, 0 failed; 7 wallets active (same 7 as run 112).",
 "method_note": "Sent pass Ankr ankr_getTransactionsByAddress via module: 55/55 OK first attempt (180 txs), 0 failed - no same-run retry needed. Receipts via fast_rpc batch (6, ~4s pause) for 122 non-approve candidates: 122 status 1, 0 status 0, 0 NULL - no race fallbacks. Mint-pattern txs: 1 - AFeng (0xbf00...) sale-call 0x4d819a2a to 0x1de4... 09:26:48 WIB, value 0.075 BNB, tx 0x3b827b5ee6a3ef389f058e793f8d3878c1da4081eb5a94a8d6791a0cd5c6704b, receipt status 1, 43 logs, Transfer from zero address from tracker contract 0x636fdfa9bc3db42c690c09e87b9017d05b36c743 for 269,631,881,702.31 tokens (raw 269631881702311123909224821251, decimals 18). This is the dividend-tracker mint pattern of runs 70/75/101/102 REPEATING after a one-run gap (run 112: 0 mint logs) - SAME contract already in bridge (first seen run 70, gate website_no_pointer_found) and already reported in run 70, so NOT a new finding, NOT a signal (1 entity), NOT a trigger; recorded in reported_findings as a repeat occurrence for dedupe only. The other 9 AFeng sale-calls (0/0.02/0.075/0.15/0.325 BNB) produced 0 mint logs. AFeng 16 txs total: 10 sale-calls (1.5 BNB) + 4 approvals + 2 empty-input (self-transfer 4.59779515 BNB 09:20:56 WIB hash 0x9923112479cd + 0.001 BNB 09:25:11 WIB); total AFeng value 6.09779515 BNB. future1001.ai (0x355e...) 0 txs this run. Paid: 27 tokens; max 3 wallets/token (13 tokens at 3 wallets, ALL the same churn trio 0x3803/0xad94/0xc7c5; 5 at 2, all pair 0x3628/0xa0c1; 9 at 1 - 6x AFeng 0xbf00, 3x 0x7488). Overlap with run-112 paid tokens: 0 - the ...7777 churn set turned over COMPLETELY again this run (tenth straight run with 0 overlap; runs 104-112 also 0). ZERO new rotations - the 27-wallet machine set had 0 txs this run (no buys, no sells, no approvals from any of the 27). The named-rotation streak ENDED run 104 (runs 97-103); run 113 has 0, tenth straight quiet run. No anomaly to report under the fast-path amendment (no new token, no name/symbol appearing, no size anomaly among machine buys, no free-mint path; the 4.5978 BNB max single tx is AFeng's SELF-transfer, not a machine buy). Trigger >25% NOT met by any token (max 3 wallets = 5.5%). No preview, no execution. Seatbelt 1e9c STALLED at 26: 0 wallets this run (0 buys, 0 sells) - sell-wallet union run101+run102 = 26/27, runs 103-113 add 0 - did NOT reach 27. NOT a new rotation; watch run 114 the same way. Deployments: ZERO - tenth straight run without deployments (run 104: 0, run 105: 0, run 106: 0, run 107: 0, run 108: 0, run 109: 0, run 110: 0, run 111: 0, run 112: 0, run 113: 0; runs 97-103 had 25/72/64/32/35/70/68) - verified from raw receipts contractAddress fields, not the parsed JSON. Inbound list for run 113 = run112 list (1734) + 0 deployments + 0 new rotation tokens (total 1734, unchanged). 0x2325... 0 txs this run; 0x8e96... 0 txs; 0x6ba79dcc/0x89220022/0xda91cefe 0 txs. 0xad94... 40 txs (0.000455 BNB); 0xc7c5... 41 txs (0.000455 BNB); 0x3803... 40 txs (0.000338 BNB); 0xa0c1... 16 txs (0.0005 BNB); 0x3628... 17 txs (0.0005 BNB); 0x7488d5da... 10 txs (0.00025441 BNB); AFeng 0xbf00... 16 txs (6.09779515 BNB). 2 plain BNB transfers (empty input, both AFeng: self-transfer 4.59779515 BNB 09:20:56 WIB + 0.001 BNB 09:25:11 WIB; run 112: 1, run 111: 0, run 110: 1, run 109: 1). Selectors (sent pass, 180 txs): 58 approvals (0x095ea7b3) + 44 PCS sells (0x791ac947) + 39 PCS buys (0xb6f9de95) + 27 aggregator (0x39ecce49) + 10 sale-calls (0x4d819a2a) + 2 empty-input. NO contract creations, NO transfers (0xa9059cbb). Nonzero-value txs 60, total 6.10029756 BNB (6.09779515 of it AFeng; micro churn only ~0.0025 BNB), max 4.59779515 BNB (AFeng self-transfer 09:20:56 WIB; run 112 total was 0.65481003 BNB, max 0.5 BNB). Most active wallets: 0xc7c5faa2 41, 0xad94ee77 40, 0x38031ca8 40, 0x3628764a 17, 0xa0c1e94f 16, 0xbf004bff 16, 0x7488d5da 10. 0 NULL receipts this run. 0 status-0 txs. Inbound leg (amendment 12:02 WIB): Ankr getLogs address-filtered per contract, 1734 contracts, 0 hits inbound-only (1 hit = the sent-pass tracker mint tx), 12141 logs, window 132309618-132318095. 35 slices of ~50 contracts in 6 parallel rounds from the start (lesson runs 109/111 applied - detached via setsid/nohup, no silent death; rounds ~4-6 min). 1 in-slice failure (0x3b3c00d4616a4a48c115b8e321aa6b983a2beb10 'Remote end closed connection without response') recovered same-run via run113-inbound113-retry.py (0 logs, 0 hits) - 0 FAILED after retry. 7 truncated contracts, all topic-filtered (6 to 0 logs: 0x1de4... sale AFeng, 0x3dca..., 0x55d398... USDT, 0x6288..., 0x63de... AGC, 0x7857...; 0x636fdfa9... tracker to 1 log = the known hit). Window FULLY CLOSED in-run, no retry deferred to run 114. Pair retry 8/8 FAILED this run (all eight pairs: a6e6/887c/2bfb/c459/43c8/cfdb/0cf8/e68b - token0()/token1() all 'all endpoints failed' via fast_rpc race, OSError/TimeoutError, in run113-pair-retry.py) - unverified, not absence; 31st consecutive run for a6e6/887c/2bfb/c459, 26th for 43c8, 25th for cfdb/0cf8/e68b; retry run 114. fast_rpc race outage TOTAL during the pair retry again - but the receipts batch pass worked fine earlier in the same run, so the outage is time-varying, not permanent. A failed race read is UNVERIFIED, never absence - retry, don't conclude. Pointer-discovery (amendment 19:10): 0 contracts processed - no new mint contracts this run (the tracker contract is already in bridge with gate website_no_pointer_found), and the backfill queue is empty (bridge 115 contracts, 0 not_evaluated); bridge unchanged. CHAT REPORT this run: NONE - the tracker mint is a repeat of the already-reported run-70 contract/pattern (not a new finding), no new mints, no Free Bacot signal, no anomaly, no auto-mint trigger, no guard block. No preview/mint/sign/login/purchase by this job. NOTE: baw session re-logged-in 2026-11-08 ~08:27 WIB (QR pairing ae9248, expires 2026-11-10 08:34:54 WIB) - irrelevant to this run (no trigger met, no execution attempted), but any future auto-mint >25% execution needs a live baw session first."
}

s["paid_trend_run113"] = ("27 tokens paid-bought; max 3 wallets/token (13 at 3, all churn trio 0x3803/0xad94/0xc7c5; "
 "5 at 2, all pair 0x3628/0xa0c1; 9 at 1 - 6x AFeng 0xbf00, 3x 0x7488); overlap vs run 112: 0 (tenth straight complete turnover); "
 "AFeng 16 txs (10 sale-calls to 0x1de4..., 1.5 BNB; self-transfer 4.59779515 BNB) and the dividend-tracker mint pattern REPEATED "
 "(1 mint log, tracker 0x636fdfa9, 0.075 BNB, same contract as run 70 - repeat, not new); "
 "total nonzero value 6.10029756 BNB across 60 txs (6.09779515 AFeng), max single 4.59779515 BNB (AFeng self-transfer); "
 "no token >=12 wallets, no signal, no trigger.")

s["inbound_log_leg_run113"] = ("Ankr getLogs address-filtered, 1734 contracts, 12141 logs, 1 hit (= sent-pass tracker mint tx, 0 inbound-only), "
 "window 132309618-132318095; 1 failure (0x3b3c00d4616a4a48c115b8e321aa6b983a2beb10) retried same-run OK (0 logs); "
 "7 truncated contracts topic-filtered (6 to 0 logs, tracker 0x636fdfa9 to 1 log = the hit); window fully closed.")

# Repeat occurrence of the already-reported run-70 tracker contract (dedupe only; not a new finding)
s["reported_findings"].append({
 "counts": "1 tx, 1 mint-pattern event, 1 mint contract (ERC20 Transfer from zero address) - REPEAT of run-70 contract, not a new finding",
 "free_vs_paid": "tx value 0.075 BNB = paid (gas excluded); free/paid label is per tx value, not a quote read",
 "in_free_bacot_snapshot": False,
 "mints": [{
   "call_to": "0x1de460f363af910f51726def188f9004276bf4bc",
   "kind": "ERC20 mint-pattern (Transfer from zero address)",
   "mint_contract": "0x636fdfa9bc3db42c690c09e87b9017d05b36c743",
   "name": "unverified (name()/symbol() both return empty strings on-chain)",
   "symbol": "unverified (empty string)",
   "time_wib": "2026-11-08 09:26:48",
   "amount": "269631881702.31113 tokens (raw 269631881702311123909224821251, decimals 18 verified)",
   "tx": "0x3b827b5ee6a3ef389f058e793f8d3878c1da4081eb5a94a8d6791a0cd5c6704b",
   "input_selector": "0x4d819a2a",
   "tx_value_bnb": 0.075,
   "owner": "0x10b389eed857fdb84089a64188aab6afbbe2cc2a",
   "note": "REPEAT occurrence (run 113) of the run-70 finding on the SAME tracker contract 0x636fdfa9; the dividend-tracker mint pattern of runs 70/75/101/102 repeating after a one-run gap (run 112: 0 mint logs). Recorded for dedupe only - NOT a new finding, NOT a signal, NOT an auto-mint trigger. The contract is likely a dividend tracker, so classifying this as a project mint (vs a distribution/tracker allocation) is UNVERIFIED beyond the zero-address Transfer."
  }],
 "not_a_signal": "1 entity only (AFeng, feed-only); far below the 12-entity >20% threshold and the 14-entity >25% auto-mint trigger. Repeat of an already-reported contract - not reported to chat as new. No preview/mint/sign by this job.",
 "type": "PAID ERC20 mint-pattern event, tx value 0.075 BNB (REPEAT)",
 "wallet": "0xbf004bff64725914ee36d03b87d6965b0ced4903",
 "wallet_label": "AFeng (feed-only)"
})

n = s.get("next_run_note", "")
n = n.replace("Next run sent-tx window starts from block 132309619. RETRY run 113:",
              "Next run sent-tx window starts from block 132318096. RETRY run 114:", 1)
n = n.replace("30 consecutive runs", "31 consecutive runs", 1)
n = n.replace("(unreadable run 88-112, 25 consecutive", "(unreadable run 88-113, 26 consecutive", 1)
n = n.replace("(token0/token1 unreadable run 89-112, 24 consecutive", "(token0/token1 unreadable run 89-113, 25 consecutive", 1)
n = n.replace("0 wallets runs 103-112", "0 wallets runs 103-113", 1)
n = n.replace("0 wallets runs 91-112, 22nd quiet run", "0 wallets runs 91-113, 23rd quiet run", 1)
n = n.replace("0 wallets runs 90-112, 23rd quiet run", "0 wallets runs 90-113, 24th quiet run", 1)
n = ("(Run 113: inbound list = run112 list (1734) + 0 deployments + 0 new rotation tokens; window fully closed "
     "132309618-132318095, 1 hit (= sent-pass tracker mint, 0 inbound-only), 1 in-chunk failure recovered same-run via run113-inbound113-retry.py; "
     "1e9c still STALLED 26/27, 1153 STALLED 26, 79cd STALLED 20; AFeng dividend-tracker mint pattern REPEATED (0x636fdfa9, 0.075 BNB, repeat of run 70).) " + n)
s["next_run_note"] = n

json.dump(s, open(STATE, "w"), indent=1)
print("state updated: last_run=113, paid_trend_run113 + inbound_log_leg_run113 added, repeat tracker finding appended")
print("next window starts 132318096")
print("backup:", NP / "tracked-wallet-mint-scan-state.json.bak-run113-pre")
