#!/usr/bin/env python3
"""Run 112 state update (read-only bookkeeping): last_run + paid_trend_run112 +
inbound_log_leg_run112 + next_run_note. No preview/mint/sign/login."""
import json, shutil
from pathlib import Path

HOME = Path.home()
NP = HOME / "workspace/narrative-pulse"
STATE = NP / "tracked-wallet-mint-scan-state.json"
shutil.copy(STATE, NP / "tracked-wallet-mint-scan-state.json.bak-run112-pre")
s = json.load(open(STATE))

s["last_run"] = {
 "run": 112,
 "block_start": 132301966,
 "block_end": 132309618,
 "window_wib": "2026-11-08 08:09:05 - 2026-11-08 09:05:39 WIB (tx times); run executed ~09:05 WIB - ~09:45 WIB; sent-pass in-window txs 160, 0 mint-pattern txs (0 new mints - AFeng 8 txs, future1001.ai 0 txs, 5 sale-calls but 0 mint logs, so the dividend-tracker mint pattern of runs 70/75/101/102 did NOT repeat)",
 "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set); 55/55 first attempt, 0 failed; 7 wallets active (vs 6 run 111 - AFeng returned).",
 "method_note": "Sent pass Ankr ankr_getTransactionsByAddress via module: 55/55 OK first attempt (160 txs), 0 failed - no same-run retry needed (run 111 also 0 failed first attempt). One slow wallet stall ~3.5 min at wallet 23 (0xdb2d...) mid-pass, resolved on its own (fresh Ankr call = stall, not death - waited it out). 7 wallets active. Receipts via fast_rpc batch (6, ~4s pause) for 107 non-approve candidates: 107 status 1, 0 status 0, 0 NULL - no race fallbacks. Mint-pattern txs: 0 - ZERO mint logs in 107 receipts. AFeng RETURNED after 3 quiet runs (109/110/111: 0 txs): 8 txs (5 sale-calls 0x4d819a2a to 0x1de4... + 3 approvals, total 0.65 BNB; valued calls 0.5 BNB 09:01:50 WIB + 0.15 BNB 08:53:26 WIB) - the sale contract emits its 0x205442d6 zero-from event on every sale-call, which per the established state note is NOT a new mint; 0 standard Transfer/TransferSingle mint logs, so the dividend-tracker mint pattern did NOT repeat. AFeng received 0x6f6e... and 0x50c2... tokens (single-wallet paid, 1.8% each, far below thresholds). future1001.ai (0x355e...) 0 txs this run. Paid: 24 tokens; max 3 wallets/token (12 tokens at 3 wallets, ALL the same churn trio 0x3803/0xad94/0xc7c5; 6 at 2; 6 at 1). Overlap with run-111 paid tokens: 0 - the ...7777 churn set turned over COMPLETELY again this run (ninth straight run with 0 overlap; runs 104-111 also 0). ZERO new rotations - the 27-wallet machine set had 0 txs this run (no buys, no sells, no approvals from any of the 27). The named-rotation streak ENDED run 104 (runs 97-103); run 112 has 0, ninth straight quiet run. No anomaly to report under the fast-path amendment (no new token, no name/symbol appearing, no size anomaly, no free-mint path; max single tx value 0.5 BNB is AFeng's sale-call, not a machine buy). Trigger >25% NOT met by any token (max 3 wallets = 5.5%). No preview, no execution. Seatbelt 1e9c STALLED at 26: 0 wallets this run (0 buys, 0 sells) - sell-wallet union run101+run102 = 26/27, runs 103-112 add 0 - did NOT reach 27. NOT a new rotation; watch run 113 the same way. Deployments: ZERO - ninth straight run without deployments (run 104: 0, run 105: 0, run 106: 0, run 107: 0, run 108: 0, run 109: 0, run 110: 0, run 111: 0, run 112: 0; runs 97-103 had 25/72/64/32/35/70/68) - verified from raw receipts contractAddress fields, not the parsed JSON. Inbound list for run 112 = run111 list (1734) + 0 deployments + 0 new rotation tokens (total 1734, unchanged). 0x2325... 0 txs this run; 0x8e96... 0 txs; 0x6ba79dcc/0x89220022/0xda91cefe 0 txs. 0xad94... 36 txs (0.00042 BNB); 0xc7c5... 35 txs (12 buy + 11 sell + 11 approval + 1 plain BNB transfer 0.00212797 BNB to 0x7f51d464... 08:43:48 WIB, same recipient as run 109); 0x3803... 35 txs (23 aggregator 0x39ecce49 + 12 approval, 0 buy/sell, 0.000312 BNB); 0xa0c1... 18 txs; 0x3628... 16 txs; 0x7488d5da... 12 txs; AFeng 0xbf00... 8 txs (0.65 BNB). 1 plain BNB transfer (empty input, 0xc7c5..., 0.00212797 BNB, 08:43:48 WIB; run 111: 0, run 110: 1, run 109: 1). Selectors (sent pass, 160 txs): 53 approvals (0x095ea7b3) + 40 PCS buys (0xb6f9de95) + 38 PCS sells (0x791ac947) + 23 aggregator (0x39ecce49) + 5 sale-calls (0x4d819a2a) + 1 empty-input. NO contract creations, NO transfers (0xa9059cbb). Nonzero-value txs 55, total 0.65481003 BNB (0.65 of it AFeng sale-calls; micro churn only ~0.0048 BNB), max 0.5 BNB (AFeng sale-call 09:01:50 WIB; run 111 total was 0.00287825 BNB, max 0.0001 BNB). Most active wallets: 0xad94ee77 36, 0xc7c5faa2 35, 0x38031ca8 35, 0xa0c1e94f 18, 0x3628764a 16, 0x7488d5da 12, 0xbf004bff 8. 0 NULL receipts this run. 0 status-0 txs. Inbound leg (amendment 12:02 WIB): Ankr getLogs address-filtered per contract, 1734 contracts, 0 hits, 11880 logs, window 132301966-132309618. 35 slices of ~50 contracts in 6 parallel rounds from the start (lesson runs 109/111 applied - detached via setsid/nohup, no silent death; rounds ~3.5-6 min). 1 in-slice failure (0xb35fd3f7... 'Remote end closed connection without response') recovered same-run via run112-inbound111-retry.py (0 logs, 0 hits; first retry attempt used run-111 window by a stale sed - caught and re-run with the correct run-112 window before closing) - 0 FAILED after retry. 8 truncated contracts, all topic-filtered to 0 logs (0x10b3..., 0x1de4... sale AFeng, 0x3dca..., 0x55d398... USDT, 0x6288..., 0x636fdfa9... tracker, 0x63de... AGC, 0x7857...). Window FULLY CLOSED in-run, no retry deferred to run 113. Pair retry 8/8 FAILED this run (all eight pairs: a6e6/887c/2bfb/c459/43c8/cfdb/0cf8/e68b - token0()/token1() all 'all endpoints failed' via fast_rpc race, OSError/TimeoutError, in run112-pair-retry.py; the first pair-retry launch was lost when its exec wrapper timed out - relaunched separately with an absolute path) - unverified, not absence; 30th consecutive run for a6e6/887c/2bfb/c459, 25th for 43c8, 24th for cfdb/0cf8/e68b; retry run 113. fast_rpc race outage TOTAL during the pair retry again - but the receipts batch pass worked fine earlier in the same run, so the outage is time-varying, not permanent. A failed race read is UNVERIFIED, never absence - retry, don't conclude. Pointer-discovery (amendment 19:10): 0 contracts processed - no new mints this run, and the backfill queue is empty (bridge 115 contracts, 0 not_evaluated); bridge unchanged. CHAT REPORT this run: NONE - nothing new to report (no new mints, no Free Bacot signal, no anomaly, no auto-mint trigger, no guard block). No preview/mint/sign/login/purchase by this job. NOTE: baw session re-logged-in 2026-11-08 ~08:27 WIB (QR pairing ae9248, expires 2026-11-10 08:34:54 WIB) - irrelevant to this run (no trigger met, no execution attempted), but any future auto-mint >25% execution needs a live baw session first."
}

s["paid_trend_run112"] = ("24 tokens paid-bought; max 3 wallets/token (12 at 3, all churn trio 0x3803/0xad94/0xc7c5; "
 "6 at 2, all pair 0x3628/0xa0c1; 6 at 1 - 4x 0x7488, 2x AFeng 0xbf00); overlap vs run 111: 0 (ninth straight complete turnover); "
 "AFeng returned (8 txs, 5 sale-calls to 0x1de4..., 0.65 BNB) but 0 mint logs - dividend-tracker mint pattern did NOT repeat; "
 "total nonzero value 0.65481003 BNB across 55 txs (0.65 AFeng sale-calls), max single 0.5 BNB; no token >=12 wallets, no signal, no trigger.")

s["inbound_log_leg_run112"] = ("Ankr getLogs address-filtered, 1734 contracts, 11880 logs, 0 hits, window 132301966-132309618; "
 "1 failure (0xb35fd3f7...) retried same-run OK (0 logs); 8 truncated contracts topic-filtered to 0 logs; window fully closed.")

n = s.get("next_run_note", "")
n = n.replace("Next run sent-tx window starts from block 132296161. RETRY run 111:",
              "Next run sent-tx window starts from block 132309619. RETRY run 113:", 1)
n = n.replace("28 consecutive runs", "30 consecutive runs", 1)
n = n.replace("(unreadable run 88-110, 23 consecutive", "(unreadable run 88-112, 25 consecutive", 1)
n = n.replace("(token0/token1 unreadable run 89-110, 22 consecutive", "(token0/token1 unreadable run 89-112, 24 consecutive", 1)
n = n.replace("0 wallets runs 103-110", "0 wallets runs 103-112", 1)
n = n.replace("0 wallets runs 91-110, 20th quiet run", "0 wallets runs 91-112, 22nd quiet run", 1)
n = n.replace("0 wallets runs 90-110, 21st quiet run", "0 wallets runs 90-112, 23rd quiet run", 1)
n = ("(Run 112: inbound list = run111 list (1734) + 0 deployments + 0 new rotation tokens; window fully closed "
     "132301966-132309618, 0 hits, 1 in-chunk failure recovered same-run via run112-inbound111-retry.py; "
     "1e9c still STALLED 26/27, 1153 STALLED 26, 79cd STALLED 20; AFeng returned with 5 sale-calls, 0 mint logs.) " + n)
s["next_run_note"] = n

json.dump(s, open(STATE, "w"), indent=1)
print("state updated: last_run=112, paid_trend_run112 + inbound_log_leg_run112 added")
print("next window starts 132309619")
print("backup:", NP / "tracked-wallet-mint-scan-state.json.bak-run112-pre")
