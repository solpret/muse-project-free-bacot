#!/usr/bin/env python3
"""Run 85 state update (read-only job bookkeeping; no chain writes).

Completes run 85 (window 132041620-132047945, tx 2026-11-06 23:35:03 - 2026-11-07 00:22:22 WIB).
Sent/receipts/paid done and verified; BOTH inbound legs FULLY CLOSED (run-84 window retry +
run-85 window). New machine-token rotation 0x2717... verified routine (class norm) - state-only,
NO chat report per fast-path amendment. Bridge unchanged.
"""
import json, shutil
from pathlib import Path

P = "/home/hatch/workspace/narrative-pulse/tracked-wallet-mint-scan-state.json"
D = Path("/home/hatch/workspace/narrative-pulse/scan-runs")
shutil.copy(P, str(P) + ".bak-run85-pre")
s = json.load(open(P))

sent = json.load(open(D / "run85-sent.json"))
paid = json.load(open(D / "run85-paid.json"))
verify = json.load(open(D / "run85-token-verify.json"))
logcheck = json.load(open(D / "run85-2717-logcheck.json"))

last_run_85 = {
    "run": 85,
    "block_start": 132041620,
    "block_end": 132047945,
    "window_wib": "2026-11-06 23:35:03 - 2026-11-07 00:22:22 WIB (tx times); run executed ~00:15 - ~01:00 WIB; sent-pass in-window txs 312, 0 mint-pattern txs",
    "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set); 0 failed, no retry needed.",
    "method_note": (
        "Sent pass Ankr ankr_getTransactionsByAddress via module: 55/55 OK first attempt (Ankr healthy tonight: "
        "getLogs probe 7.1s, getTransactionsByAddress probe 1.4s), 312 txs, 34 wallets active. "
        "Receipts via fast_rpc batch (6, ~4s pause) for 201 non-approve candidates: 201 status 1, 0 status 0, 0 null, 0 mint logs. "
        "Paid: 17 tokens; NEW machine-token rotation 0x2717a156b86c3c8894bb2dea9a34c514e8fc7777 at 27 wallets (49.1% - numerically above the "
        "20% signal and 25% auto-mint thresholds, but paid-only with NO free-mint path: auto-mint BLOCKED at guard (c); recorded in state + "
        "signaled_projects as paid-only machine-token, NO chat report per fast-path amendment - see machine_tokens entry). Other tokens max 3 "
        "wallets/token (9 at 3, 4 at 2, 3 at 1 - usual ...7777 churn). "
        "AFeng 0 txs; future1001.ai 0 txs; 0x2325... 0 txs; 0x8e96... 0 txs; 0x5b2f... 0 txs. "
        "Selectors: 79 PCS buys (0xb6f9de95) + 101 PCS sells (0x791ac947) + 111 approvals (0x095ea7b3) + 19 aggregator (0x39ecce49) + "
        "2x 0x27772d13. Deployments: 0 contract creations by tracked wallets this run (no to=None sent txs, no contractAddress in any receipt) - "
        "2nd consecutive deployment-free run; run-85 inbound list = run84 list (1075) with 0 additions. "
        "Inbound leg run-84 WINDOW RETRY (amendment 12:02): FULLY CLOSED - 1075/1075 contracts, 17,988 logs, 0 hits, 1 failed (0x4b9b8fd6361a9e1baa0705fa77252f14dc54c10a, "
        "Remote end closed) retried OK via topic-filtered re-check (0 logs, verified=True, run85-inbound84-4b9b-retry.json). Run-84 window inbound now "
        "FULLY CLOSED (sent + receipts + inbound all verified 0 mints). "
        "Inbound leg run-85 WINDOW: FULLY CLOSED - 1075/1075 contracts, 12,175 logs, 0 hits, 0 failed, 7 truncated (all topic-filtered to 0 logs). "
        "Run-84 null receipts CLOSED: all 3 recovered this run via fast_rpc race (status 0x1, 6 logs each, 0 mint logs, run85-nullpair-retry.json; "
        "merged into run84-receipts.json) - run-84 receipts now 153/153 status 1, 0 null. "
        "Pair token0/token1 for a6e6 (0x9fac...) and 887c (0xa9fa...) STILL UNREADABLE (fast_rpc race returns None; Ankr eth_call returns null) - "
        "persistently unreadable, 3rd consecutive run; unverified, not absence; retry run 86. "
        "SCRIPT BUG (fixed in-archive): run85-receipts.py was copied from run84 with only sent/partial paths sed-replaced, so its parsed/paid dumps "
        "overwrote run84-receipts.json/run84-paid.json with run-85 data. Restored run84 files from run84-receipts-partial.json + run84-sent.json "
        "(re-ran run84-receipts.py, then merged the 6 recovered null receipts: 3 from run84-receipts-null-retry.json + 3 from run85-nullpair-retry.json) - "
        "run84 parsed now 153 entries, 153 status 1, 0 null, 0 mint logs; run85 parsed/paid saved as run85-receipts.json/run85-paid.json. "
        "FUTURE RUNS: when copying the receipts script, sed-replace the two hardcoded json.dump output paths too (runNN-receipts.json / runNN-paid.json). "
        "No preview/mint/sign/login/purchase by this job."
    ),
}
cur_run = s.get("last_run", {}).get("run", 0)
if cur_run < 85:
    s["last_run"] = last_run_85
    print(f"last_run set to 85 (was {cur_run})")
else:
    print(f"last_run already {cur_run} (>=85) - NOT regressing")
    s["run85_last_run_record"] = last_run_85

s["machine_tokens"].append({
    "address": "0x2717a156b86c3c8894bb2dea9a34c514e8fc7777",
    "first_seen": "run-85, 2026-11-07 00:14:31 WIB (first tracked Transfer tx 0x19c3608ad3e5612b102d9208adfe18c7650c8a77fd649fcbb85adfc313081ba2, block 132046898)",
    "machine_wallets": 27,
    "typical_first_buy_bnb": 0.000123616835355714,
    "followup_buy_range_bnb": "median 0.2233621, max 0.3716799509316338, total buys 8.6724 BNB (51 sent buys)",
    "label": "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB)",
    "note": (
        "Routine rotation, NO anomaly in a listed class; recorded in state WITHOUT chat report per fast-path amendment. "
        "Sizes WITHIN the established class norm (runs 80-82: first buy ~0.000106-0.000124 BNB, follow-up median ~0.19-0.23, max ~0.37-0.40). "
        "No name/symbol (empty strings), decimals 18, totalSupply 1e27. Pair PCS V2 0xc62abedf32b72ceff46d8a0a58098aabef97ada3 "
        "(token0 = token; token1 unreadable via eth_call, corroborated WBNB by reserves ~63M tokens / 0.05915 BNB). "
        "Sourcify sources/abi reads transport-truncated (IncompleteRead, 4 attempts); partial sources show no website URL and no site functions - "
        "NOT a verified absence. No free-mint path (0 mint logs; all receives PCS buys). Auto-mint blocked at guard (c). "
        "27/27 wallet overlap with run-82 rotation sets (same machine set). 71 sells from tracked wallets in-window (round-trip churn). "
        "NEW OBSERVATION: 5 additional receives (56 Ankr Transfer-to-tracked logs vs 51 sent buys) arrived via txs NOT sent by tracked wallets - "
        "buys routed through a proxy/aggregator (amounts 413-7442 tokens); still plain PCS buys from the pair, 0 zero-from logs. "
        "First tracked Transfer was a normal machine buy (0xcb08..., 0.0001236 BNB, 9.86 tokens) - no AFeng bulk-distribution oddity this run. "
        "Not in Free Bacot snapshot; NOT added to bridge (paid-only PCS token, precedent runs 63-84)."
    ),
})

sig = s.setdefault("signaled_projects_over_20pct", [])
sig.append("Unnamed token (name/symbol empty) 0x2717a156b86c3c8894bb2dea9a34c514e8fc7777 (paid-only, machine-token, run-85, no chat report per fast-path amendment)")

s["paid_trend_run85"] = {
    "note": "Aggregate only, NOT a buy recommendation. New machine-token rotation at 27 wallets is paid-only with no free-mint path (auto-mint blocked at guard (c)); recorded in state, NO chat report per fast-path amendment. SILENT RUN - no chat report (no new mints, no Free Bacot signal, no auto-mint trigger, no reportable paid trend beyond the routine rotation).",
    "rotation": "NEW machine-token rotation 0x2717a156b86c3c8894bb2dea9a34c514e8fc7777 at 27 wallets (49.1% of 55; same 27-wallet set as runs 80-82, 27/27 overlap with run-82 sets): 51 sent buys (median 0.2234 BNB, max 0.3717, total 8.6724 BNB) + 5 proxy-routed buys + 71 sells, window 00:14:31-00:21:37 WIB. Sizes within class norm; no name/symbol, no website pointer, no free-mint path; guard (c) blocks auto-mint.",
    "other_paid_activity": [
        {"pattern": "16 other paid tokens: 9 at 3 wallets (usual ...7777 set via trio 0x38031ca8a5/0xad94ee77d0/0xc7c5faa270), 4 at 2, 3 at 1 (incl. USDT 0x55d398... at 1 wallet)", "wallets": "see run85-paid.json"},
        {"pattern": "Micro round-trip churn continues: 79 PCS buys (0xb6f9de95) + 101 PCS sells (0x791ac947), 111 approvals (0x095ea7b3), 19 aggregator txs (0x39ecce49), 2x 0x27772d13; top active 0xc7c5... 29 txs, 0x3803... 28, 0xad94... 27, 0xa952... 17, 0x9cdd... 15", "wallets": "churn set"},
        {"pattern": "0 contract deployments by tracked wallets this run (2nd consecutive deployment-free run)", "wallets": "none"},
    ],
    "quiet": "AFeng 0 txs; future1001.ai 0 txs; 0x2325... 0 txs; 0x8e96... 0 txs; 0x5b2f... 0 txs; GrokBot 0xfcd0... absent (0 wallets) - 26th consecutive quiet run (59, 61-85) after the run-60 burst; CORLA-97af 0 wallets; CORLA 0x4a9c 0 wallets; all run-64/65 ASI contracts 0 wallets; all run-66/68/69/70/71/72/73/74/75/76/77/78/79/80/81/82 machine tokens 0 wallets (run-82 tokens 0xd468.../0xa6e6.../0x887c... 3rd quiet run after debut; run-81 tokens 4th quiet; run-80 token 5th quiet).",
}

s["inbound_log_leg_run84"] = {
    "contracts": 1075,
    "attempted": 1075,
    "completed_with_0_hits": 1075,
    "total_logs": 17988,
    "hits": 0,
    "failed": 0,
    "failed_contracts": [],
    "failed_then_retried_ok": ["0x4b9b8fd6361a9e1baa0705fa77252f14dc54c10a"],
    "never_attempted": 0,
    "complete": True,
    "note": (
        "Ankr getLogs address-filtered per contract, window 132031247-132041619, from ONE frozen list "
        "(run84-inbound-contracts.json, 1075 contracts = run83 list 1061 + 14 run-83 deployment addresses). "
        "RETRY RUN 85: full pass a (400) + b1 (200) + b2 (200) + b3 (275) = 1075 contracts, 17,988 logs, 0 hits, 1 failed "
        "(0x4b9b... Remote end closed) - retried OK via topic-filtered re-check (0 logs, verified=True, run85-inbound84-4b9b-retry.json). "
        "9 truncated contracts, all topic-filtered to 0 logs. RUN-84 WINDOW INBOUND NOW FULLY CLOSED (sent + receipts + inbound all verified 0 mints). "
        "14 run-83 deployment addresses (indices 1061-1074): 0 hits via inbound; machine set did not buy them via sent txs either (run 84 paid map 0 hits)."
    ),
}
s["inbound_log_leg_run85"] = {
    "contracts": 1075,
    "attempted": 1075,
    "completed_with_0_hits": 1075,
    "total_logs": 12175,
    "hits": 0,
    "failed": 0,
    "failed_contracts": [],
    "never_attempted": 0,
    "complete": True,
    "note": (
        "Ankr getLogs address-filtered per contract, window 132041620-132047945, from frozen list run84-inbound-contracts.json (1075 contracts; "
        "run 85 had 0 deployments, so no additions). Full pass a (400, 7,368 logs) + b1 (200, 3,398) + b2 (200, 651) + b3 (275, 758) = 12,175 logs, "
        "0 hits, 0 failed. 7 truncated contracts, all topic-filtered to 0 logs (incl. 0x3dca..., 0x55d398... USDT, 0x636f... AFeng tracker, 0x6288... AGC sale). "
        "RUN-85 WINDOW INBOUND FULLY CLOSED. Chunk a ran slow in segments (251-300, 301-350: ~2-4 min silence each - high-log contracts needing "
        "topic-filtered second calls) but completed without intervention."
    ),
}

s["next_run_note"] = (
    "Next run sent-tx window starts from block 132047946. RETRY run 86: (1) Pair token0/token1 reads for 0xa6e6... pair "
    "0x9fac925655fa4985ab4fe2fe9e0ca8ae323cc9da and 0x887c... pair 0xa9fa6efb21c252b7d4ab81d19a07ee4ecf6d2c97 "
    "(fast_rpc race returns None + Ankr eth_call returns null, 3 consecutive runs - persistently unreadable, unverified not absence). "
    "(2) Run-85 inbound list for run 86 = run84 list (1075) unless run 86's own sent pass finds new deployments to add. "
    "(3) Run-84 window inbound FULLY CLOSED (retry run 85: 1075/1075, 17,988 logs, 0 hits). Run-85 window inbound FULLY CLOSED (1075/1075, 12,175 logs, 0 hits). "
    "(4) Run-84 null receipts CLOSED (all 3 recovered run 85, status 1, 0 mint logs; run84-receipts.json restored to 153/153 status 1). "
    "Dedupe new mints against all tx hashes in reported_findings (223 mint entries over 221 unique tx hashes, direct count run 77). "
    "Run-75 mint tx 0x23cd8740... (AFeng, tracker 0x636f..., 0.15 BNB) is a KNOWN REPEAT of the run-70 finding - do not report as new if it repeats again. "
    "Paid-only signals run 63 (CORLA 0x4a9c), run 64 (4 ASI), run 65 (4 ASI quad-2), run 66 (tokens 0x19b7.../0x540d...), "
    "run 68 (tokens 0xf3cc.../0xe7e2...), run 69 (token 0x4d15...), run 70 (FIVE tokens 0x4df7.../0xae06.../0x2516.../0x1247.../0x8e0d...), "
    "run 71 (SIX tokens 0xe51b.../0xc2e1.../0x5785.../0xfff4.../0xe4c9.../0x25b4...), run 72 (THREE tokens 0x26ef.../0x7145.../0xdfb3...), "
    "run 73 (FOUR tokens 0x4bd1.../0x1d9f.../0xe0f0... at 27 wallets + 0x198c... at 21 wallets), "
    "run 74 (FOUR tokens 0xe4e0.../0x4d2e.../0xaf84... at 27 wallets + 0x73c9... at 26 wallets), "
    "run 75 (THREE tokens 0x167b.../0x5205.../0x4f6d... at 27 wallets each), run 76 (TWO tokens 0x0cda... at 27 wallets + 0xacc8... at 26 wallets), "
    "run 77 (THREE tokens 0x3029.../0x5eb1.../0x1a57... at 27 wallets each), run 78 (TWO tokens 0xcbbc.../0x41cc... at 27 wallets each), "
    "run 79 (TWO tokens 0x5833.../0x32b4... at 27 wallets each), run 80 (ONE token 0x489e... at 27 wallets), "
    "run 81 (TWO tokens 0x7f7a.../0x33f7... at 27 wallets each), run 82 (THREE tokens 0xd468.../0xa6e6.../0x887c... at 27 wallets each), "
    "run 85 (ONE token 0x2717a156b86c3c8894bb2dea9a34c514e8fc7777 at 27 wallets) "
    "auto-mint BLOCKED at guard (c) - do not re-signal or re-report the block unless a new mint/buy fact appears for those contracts "
    "(e.g. a genuine free-mint path). Per the 2026-11-06 ~18:30 machine-token fast-path amendment, routine machine-token rotations are "
    "recorded in state WITHOUT a chat report (no full verification per run); report only on anomaly (buy size far off norm, name/symbol appears, "
    "website, or free-mint path). Paid fact: run85 NEW rotation 0x2717... at 27 wallets (routine, class-norm sizes, no anomaly - state-only, no chat report); "
    "run-82 tokens 0xd468.../0xa6e6.../0x887c... all 0 wallets (3rd quiet run after debut); run-81 tokens 0 wallets (4th quiet run); run-80 token 0 wallets (5th quiet run); "
    "GrokBot 0xfcd0... absent (0 wallets) - 26th consecutive quiet run (59, 61-85) after the run-60 burst; CORLA-97af 0 wallets; "
    "CORLA 0x4a9c 0 wallets; all run-64/65 ASI contracts 0 wallets; all run-66/68/69/70/71/72/73/74/75/76/77/78/79/80/81/82 machine tokens 0 wallets. "
    "Run 85 had 0 deployments - 2nd consecutive deployment-free run. "
    "AFeng 0 txs; future1001.ai 0 txs; 0x2325... 0 txs; 0x8e96... 0 txs; 0x5b2f... 0 txs. "
    "SCRIPT LESSON (run 85): when copying runNN-receipts.py for the next run, sed-replace the two hardcoded json.dump output paths too "
    "(runNN-receipts.json / runNN-paid.json) - run 85's copy overwrote run 84's parsed files (restored in-archive from partial + sent + null-retry files). "
    "Same-owner factory groups now also include 0x293f and 0x1103 (proven 2026-11-06 ~01:14 WIB, AGENTS.md) alongside the groups listed in the body."
)

json.dump(s, open(P, "w"), indent=1)
print("state updated; last_run now:", s["last_run"]["run"], "block_end:", s["last_run"]["block_end"])
print("machine_tokens:", len(s.get("machine_tokens", [])), "| signaled:", len(s.get("signaled_projects_over_20pct", [])))
print("inbound84 complete:", s["inbound_log_leg_run84"]["complete"], "| inbound85 complete:", s["inbound_log_leg_run85"]["complete"])
