#!/usr/bin/env python3
"""Run 110 state update (read-only job bookkeeping; no chain writes).

Completes run 110 (window 132287240-132296160, tx 2026-11-08 06:24:08 - 07:24:41 WIB).
Sent/receipts/paid done and verified; inbound leg run-110 window CLOSED in-run
(1734/1734, 0 hits, 3 in-chunk failures recovered same-run via retry 3/3).
NO new mints - ZERO mint-pattern txs (0 mint logs in 99 receipts; AFeng 0 txs this run,
no sale-calls at all, so no dividend-tracker repeats either).
ZERO new machine-token rotations - the 27-wallet machine set had 0 txs this run; only
7/55 wallets active (churn set + one 0x2325 aggregator tx). The named-rotation streak
ended run 104; run 110 has 0.
ZERO deployments - seventh straight run without deployments (run 104: 0, run 105: 0,
run 106: 0, run 107: 0, run 108: 0, run 109: 0, run 110: 0).
Paid max 3 wallets/token (churn trio only). Bridge unchanged (0 new mints, 0 not_evaluated).
Pair retry: 8/8 FAILED again (a6e6/887c/2bfb/c459 28th consecutive run, 43c8 23rd,
cfdb/0cf8/e68b 22nd) - retry run 111.
PROCESS NOTE (run 110): inbound leg ran as 35x ~50-contract slices in 6 parallel
rounds from the start (run-109 lesson applied - no full-chunk attempt, no silent
death); rounds took ~3.5-6 min each, one stall in round 3 (fresh Ankr call OK in
7.9s = stall, waited out). 3 in-chunk failures, all 'Remote end closed connection
without response', recovered same-run via run110-inbound109-retry.py 3/3.
No chat report this run: nothing new to report (no mints, no signal, no anomaly,
no auto-mint trigger).
No preview/mint/sign/login/purchase by this job.
"""
import json, shutil, glob

P = "/home/hatch/workspace/narrative-pulse/tracked-wallet-mint-scan-state.json"
shutil.copy(P, str(P) + ".bak-run110-pre")
s = json.load(open(P))
SR = "/home/hatch/workspace/narrative-pulse/scan-runs"

# ---- inbound totals from 35 slice JSONs + retry JSON (self-verifying) ----
slices = sorted(glob.glob(f"{SR}/run110-inbound109-s*.json"))
assert len(slices) == 35, f"slices {len(slices)} != 35"
tot_contracts = tot_logs = tot_hits = tot_failed = tot_trunc = 0
failed_contracts, trunc_contracts = [], []
regions = {"a": (0, 8), "b1": (8, 12), "b2": (12, 16), "b3a": (16, 24), "b3b": (24, 30), "b3c": (30, 35)}
region_totals = {}
for i, f in enumerate(slices):
    d = json.load(open(f))
    assert d["from"] == 132287240 and d["to"] == 132296160, f"slice {f} window mismatch"
    tot_contracts += d["contracts_checked"]
    tot_logs += d["total_logs"]
    tot_hits += len(d["hits"])
    tot_failed += len(d["failed"])
    tot_trunc += len(d["truncated"])
    failed_contracts += [x["contract"] for x in d["failed"]]
    trunc_contracts += d["truncated"]
for name, (lo, hi) in regions.items():
    c = l = h = fa = t = 0
    for j in range(lo, hi):
        d = json.load(open(f"{SR}/run110-inbound109-s{j:02d}.json"))
        c += d["contracts_checked"]; l += d["total_logs"]; h += len(d["hits"])
        fa += len(d["failed"]); t += len(d["truncated"])
    region_totals[name] = (c, l, h, fa, t)
retry = json.load(open(f"{SR}/run110-inbound109-retry.json"))
assert retry["from"] == 132287240 and retry["to"] == 132296160
assert len(retry["failed"]) == 0, f"retry failed {retry['failed']} != 0 (must retry before state update!)"
assert len(retry["hits"]) == 0, f"retry hits {retry['hits']} != 0 (must handle before state update!)"
assert sorted(x["contract"] for x in []) == []
assert set(failed_contracts) == set(["0x29adf4d894ccde764237270444444aec308dd905",
    "0x9c0586c9324af9ac3dd09367582f143d99afb6a9", "0xcdce49721d2fed646d4c1a34a51ec001cd879449"]), f"failed set mismatch: {failed_contracts}"
tot_logs_retry = retry["total_logs"]
print(f"inbound totals: slices={len(slices)} contracts={tot_contracts} logs={tot_logs} hits={tot_hits} failed_in_chunk={tot_failed} truncated={tot_trunc}")
print(f"regions: {region_totals}")
print(f"retry: contracts={retry['contracts_checked']} logs={tot_logs_retry} hits={len(retry['hits'])} failed={len(retry['failed'])}")
assert tot_contracts == 1734, f"inbound contracts {tot_contracts} != 1734"
assert tot_hits == 0, f"inbound hits {tot_hits} != 0 (must handle before state update!)"
assert tot_failed == 3, f"inbound failed {tot_failed} != 3 (expected 3 in-chunk failures)"
print(f"truncated contracts (all topic-filtered to 0 logs): {trunc_contracts}")
print(f"failed then recovered same-run: {failed_contracts}")

last_run_110 = {
    "run": 110,
    "block_start": 132287240,
    "block_end": 132296160,
    "window_wib": "2026-11-08 06:24:08 - 2026-11-08 07:24:41 WIB (tx times); run executed ~07:22 WIB - ~08:05 WIB; sent-pass in-window txs 147, 0 mint-pattern txs (0 new mints - AFeng 0 txs this run, no sale-calls at all, so no dividend-tracker repeats either)",
    "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set); 55/55 first attempt, 0 failed; only 7 wallets active.",
    "method_note": (
        "Sent pass Ankr ankr_getTransactionsByAddress via module: 55/55 OK first attempt (147 txs), 0 failed - no same-run retry needed (run 109 also 0 failed first attempt). "
        "Only 7 wallets active (vs 6 run 109 - the same churn set + one 0x2325 aggregator tx). "
        "Receipts via fast_rpc batch (6, ~4s pause) for 99 non-approve candidates: 99 status 1, 0 status 0, 0 NULL - no race fallbacks. "
        "Mint-pattern txs: 0 - ZERO mint logs in 99 receipts. No new mints of any kind. AFeng 0 txs this run (no sale-calls at all) - the dividend-tracker mint "
        "pattern of runs 70/75/101/102 did NOT repeat (and could not repeat without AFeng sale-calls). "
        "Paid: 23 tokens; max 3 wallets/token (9 tokens at 3 wallets, ALL the same churn trio 0x3803/0xad94/0xc7c5, all ...7777; 4 at 2 (the 0x3628/0xa0c1 pair); "
        "3 at 2 (0x3803+0xc7c5, trio minus ad94); 7 at 1 (1x 0x2325, 1x 0x3628, 5x 0x7488d5da)). Overlap with run-109 paid tokens: 0 - the ...7777 churn set turned over COMPLETELY again this run (seventh straight run with 0 overlap; run 104 overlap was also 0, run 105 also 0, run 106 also 0, run 107 also 0, run 108 also 0, run 109 also 0). "
        "ZERO new rotations - the 27-wallet machine set had 0 txs this run (no buys, no sells, no approvals from any of the 27). The named-rotation streak ENDED run 104 "
        "(runs 97-103); run 110 has 0, seventh straight quiet run. No anomaly to report under the fast-path amendment (no new token, no name/symbol "
        "appearing, no size anomaly, no free-mint path; the single 0x2325 aggregator buy of 0.01 BNB is one named feed wallet, not a machine-set rotation). Trigger >25% NOT met by any token (max 3 wallets = 5.5%). No preview, no execution. "
        "Seatbelt 1e9c STALLED at 26: 0 wallets this run (0 buys, 0 sells) - sell-wallet union run101+run102 = 26/27, runs 103-110 add 0 - did NOT reach 27. "
        "NOT a new rotation; watch run 111 the same way. "
        "Deployments: ZERO - seventh straight run without deployments (run 104: 0, run 105: 0, run 106: 0, run 107: 0, run 108: 0, run 109: 0, run 110: 0; runs 97-103 had 25/72/64/32/35/70/68). "
        "Inbound list for run 110 = run109 list (1734) + 0 deployments + 0 new rotation tokens (total 1734, unchanged). "
        "AFeng (0xbf004bff...) 0 txs; future1001.ai (0x36239612...) 0 txs; 0x2325... 1 tx (aggregator 0x27772d13 to 0x296b0019..., 0.01 BNB, 06:26:46 WIB - first 0x27772d13 tx since run 106 and first 0x2325 activity since run 106; single-wallet paid buy of token 0x415aac3e..., NOT a rotation/signal); "
        "0x8e96... 0 txs; 0x6ba79dcc/0x89220022/0xda91cefe 0 txs. "
        "0xc7c5... 36 txs (12 buys + 12 sells + 12 approvals, total value 0.00042 BNB); 0x3803... 36 txs (24 aggregator 0x39ecce49 + 12 approvals, total value 0.000312 BNB, 0 buys/sells); "
        "0xad94... 28 txs (9 buys + 10 sells + 9 approvals, 0.000315 BNB); 0x3628... 18 txs (5 buys + 6 sells + 6 approvals + 1 plain BNB transfer 0.00216596 BNB to 0xc0094886... at 07:00:30 WIB, 0.00256596 BNB); "
        "0x7488d5da... 15 txs (5 buys + 5 sells + 5 approvals, 0.00042004 BNB); 0xa0c1... 13 txs (4 buys + 5 sells + 4 approvals, 0.0004 BNB). 1 plain BNB transfer (empty input, 0x3628..., 0.00216596 BNB, 07:00:30 WIB; run 109: 1 by 0xc7c5, run 108: 0). "
        "Selectors (sent pass, 147 txs): 48 approvals (0x095ea7b3) + 35 PCS buys (0xb6f9de95) + 38 PCS sells (0x791ac947) + 24 aggregator (0x39ecce49) + 1 aggregator (0x27772d13) + 1 empty-input. NO contract creations, "
        "NO sale-calls (0x4d819a2a), NO transfers (0xa9059cbb). "
        "Nonzero-value txs 49, total 0.014433 BNB, max 0.01 BNB (0x2325 aggregator tx 06:26:46 WIB; run 109 total was 0.00450149 BNB, max 0.00200741 BNB; run 108 total was 0.00212282 BNB). "
        "Most active wallets: 0xc7c5faa2 36, 0x38031ca8 36, 0xad94ee77 28, 0x3628764a 18, 0x7488d5da 15, 0xa0c1e94f 13, 0x2325f175 1. "
        "0 NULL receipts this run. 0 status-0 txs. "
        f"Inbound leg (amendment 12:02 WIB): Ankr getLogs address-filtered per contract, 1734 contracts (run109 list, unchanged - 0 deployments + 0 new rotation tokens), "
        f"0 hits, {tot_logs} logs, window 132287240-132296160. "
        f"35 slices of ~50 contracts in 6 parallel rounds (run110-inbound110.py, rounds ~3.5-6 min each; run-109 lesson applied - sliced from the start, no full-chunk attempt, no silent death). "
        f"3 in-chunk failures (0x29adf4.../0x9c0586.../0xcdce49..., all 'Remote end closed connection without response') recovered same-run via run110-inbound109-retry.py 3/3 (0 logs, 0 hits) - 0 FAILED after retry. "
        "Round 3 stalled once (fresh Ankr call OK in 7.9s = stall, waited out; all 6 processes alive). "
        "Truncated contracts, all topic-filtered to 0 logs (a: 0x1de4... sale AFeng, 0x3dca..., 0x55d398... USDT, 0x6288..., 0x636fdfa9... tracker; "
        "b1: 0x63de... AGC, 0x7857..., 0x7e2d...; b2/b3a/b3b/b3c: none). "
        "Window FULLY CLOSED in-run, no retry deferred to run 111. "
        "Pair retry 8/8 FAILED this run (all eight pairs: a6e6/887c/2bfb/c459/43c8/cfdb/0cf8/e68b - token0()/token1() all 'all endpoints failed' via fast_rpc race, OSError/TimeoutError, "
        "in run110-pair-retry.py) - unverified, not absence; 28th consecutive run for a6e6/887c/2bfb/c459, 23rd for 43c8, 22nd for cfdb/0cf8/e68b; retry run 111. "
        "fast_rpc race outage TOTAL during the pair retry again - but the receipts batch pass worked fine earlier in the same run, so the outage is time-varying, not permanent. "
        "A failed race read is UNVERIFIED, never absence - retry, don't conclude. "
        "Pointer-discovery (amendment 19:10): 0 contracts processed - no new mints this run, and the backfill queue is empty (bridge 115 contracts, "
        "0 not_evaluated); bridge unchanged. CHAT REPORT this run: NONE - nothing new to report (no new mints, no Free Bacot signal, no anomaly, no auto-mint trigger, "
        "no guard block). No preview/mint/sign/login/purchase by this job."
    ),
}
s["last_run"] = last_run_110

# ---- paid trend (no paid_signal this run - no anomaly) ----
s["paid_trend_run110"] = {
    "note": "Aggregate only, NOT a buy recommendation. ZERO new rotations - the machine set was dormant again (only 7/55 wallets active; the 27-wallet machine set 0 txs, "
            "seventh straight quiet run; named-rotation streak ended run 104). ZERO deployments - seventh straight run without deployments. "
            "Paid max 3 wallets/token (churn trio only, 9 tokens at 3 wallets, all ...7777; 4 at 2, the 0x3628/0xa0c1 pair; 3 at 2, 0x3803+0xc7c5; 7 at 1, incl. one 0x2325 aggregator buy); "
            "0 overlap with run-109 paid tokens (churn set turned over completely again, seventh straight run with 0 overlap). "
            "Seatbelt 1e9c STALLED at 26/27 sell wallets (union run101+run102; 0 wallets runs 103-110) - did NOT reach 27. "
            "Run-103 named rotations 7809/7f0a/f3bd: 0 wallets (7th quiet run after debut); run-102 named rotations 8b19/d826/07b2/4263: 0 wallets (8th quiet run after debut); "
            "run-101 named rotation 4727: 0 wallets (9th quiet run after debut); run-100 named rotations 6f31/0d7e: 0 wallets (10th quiet run after debut); "
            "run-99 named rotations 50e4/6b12/ff66: 0 wallets (11th quiet run after debut); run-98 named rotations 41cc/43bc/2120/da79: 0 wallets (13th quiet run after debut); "
            "run-97 named rotations c90a/e3a8: 0 wallets (13th quiet run after debut); "
            "0x1153... STALLED at 26 wallets (20th quiet run); 0x79cd... STALLED at 20 wallets (21st quiet run). ZERO deployments - seventh straight run. "
            "Inbound run-110 window FULLY CLOSED in-run "
            f"(1734/1734, {tot_logs} logs, 0 hits, 3 in-chunk failures recovered same-run 3/3, 0 failed after retry).",
    "rotations": "ZERO new rotations this run. The 27-wallet machine set had 0 txs, seventh straight quiet run. Named-rotation streak ended run 104. "
                 "Seatbelt 1e9c rotation STALLED at 26/27 sell wallets (union run101+run102; 0 wallets runs 103-110) - watch run 111 the same way, NOT a new rotation.",
    "other_paid_activity": [
        {
            "pattern": "9 tokens x 3 wallets, all the same churn trio 0x3803/0xad94/0xc7c5, all ...7777 (PCS micro buy-then-sell); 0 overlap with run-109 paid tokens",
            "wallet": "churn trio (see paid_trend_run1 for the pattern)",
        },
        {
            "pattern": "4 tokens x 2 wallets, both 0x3628764a6576b8dfb31fba0aac6a333b64851423 + 0xa0c1e94fbc1a93e39f5eb828f960aa080a9d9b9e, all ...7777",
            "wallet": "0x3628764a6576b8dfb31fba0aac6a333b64851423 + 0xa0c1e94fbc1a93e39f5eb828f960aa080a9d9b9e",
        },
        {
            "pattern": "3 tokens x 2 wallets, 0x38031ca8a54526f9fe90f11f07b55ae5fc01036a + 0xc7c5faa270eb2394c7bf9f411fed0d0126f2eb74 (trio minus ad94)",
            "wallet": "0x38031ca8a54526f9fe90f11f07b55ae5fc01036a + 0xc7c5faa270eb2394c7bf9f411fed0d0126f2eb74",
        },
        {
            "pattern": "7 tokens x 1 wallet (PCS micro buys: 5x 0x7488d5da, 1x 0x3628) + 1 aggregator buy by 0x2325 (token 0x415aac3e..., 0.01 BNB, 06:26:46 WIB)",
            "wallet": "0x7488d5da6a6097de0ff88c7492c62c2fd1e56650 / 0x3628764a6576b8dfb31fba0aac6a333b64851423 / 0x2325f175975abdbcde555c79cc8e63381d28551b",
        },
        {
            "pattern": "24 txs via aggregator 0x855066c8679c77a0258e792b5ccf19f8c227eb31 (selector 0x39ecce49) + 12 approvals, total value 0.000312 BNB (churn as usual; 0 buys/sells from this wallet this run)",
            "wallet": "0x38031ca8a54526f9fe90f11f07b55ae5fc01036a",
        },
        {
            "pattern": "1 tx via aggregator 0x296b00198dc7ec3410e12da814d9267bb8df506a (selector 0x27772d13), 0.01 BNB, 06:26:46 WIB - first 0x27772d13 tx since run 106, first 0x2325 activity since run 106; largest-value tx this run; single-wallet paid buy, NOT a rotation/signal",
            "wallet": "0x2325f175975abdbcde555c79cc8e63381d28551b",
        },
        {
            "pattern": "1 plain BNB transfer 0.00216596 BNB to 0xc0094886dcc9040cf37c2845ebfaf478aacd7f3f, 07:00:30 WIB",
            "wallet": "0x3628764a6576b8dfb31fba0aac6a333b64851423",
        },
        {
            "pattern": "AFeng 0 txs, future1001.ai 0 txs, 0x8e96... 0 txs - the non-churn tracked wallets were all silent this run except 0x2325 (1 aggregator tx)",
            "wallet": "0xbf004bff64725914ee36d03b87d6965b0ced4903 / 0x362396125a / 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6",
        },
    ],
}

s["inbound_log_leg_run110"] = {
    "contracts": 1734,
    "attempted": 1734,
    "completed_with_0_hits": 1734,
    "total_logs": tot_logs,
    "hits": 0,
    "failed": 0,
    "failed_contracts": [],
    "failed_then_recovered_same_run": failed_contracts,
    "never_attempted": 0,
    "complete": True,
    "note": "Ankr getLogs address-filtered per contract, window 132287240-132296160, from list run110-inbound-contracts.json (1734 contracts = run109 list, unchanged - "
            f"0 run-110 deployments + 0 new rotation tokens). Ran as 35x ~50-contract slices (run110-inbound109-s00..s34.json) in 6 parallel rounds from the start "
            f"(run-109 lesson applied - no full-chunk attempt, no silent death; rounds 00:36:34/00:40:04/00:46:01/00:52:40/00:56:36/00:59:41 UTC). "
            f"Slice regions: a (400, 7,167 logs, 1 failed, 5 truncated) + b1 (200, 3,515 logs, 0 failed, 3 truncated) + b2 (200, 510 logs, 1 failed, 0 truncated) + "
            f"b3a (400, 456 logs, 1 failed, 0 truncated) + b3b (300, 0 logs, 0 failed, 0 truncated) + b3c (234, 0 logs, 0 failed, 0 truncated) = {tot_logs} logs, 0 hits, "
            f"3 in-chunk failures (all 'Remote end closed connection without response') recovered same-run via run110-inbound109-retry.py 3/3 (0 logs, 0 hits) - 0 FAILED after retry. "
            f"Truncated contracts, all topic-filtered to 0 logs (a: 0x1de4... sale AFeng, 0x3dca..., 0x55d398... USDT, 0x6288..., 0x636fdfa9... tracker; "
            f"b1: 0x63de... AGC, 0x7857..., 0x7e2d...; b2/b3a/b3b/b3c: none). Window FULLY CLOSED in-run, no retry deferred to run 111."
}

# ---- stalled-label run-range updates ----
for e in s["machine_tokens"]:
    addr = e["address"].lower()
    if addr.startswith("0x1153607e"):
        e["label"] = "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - rotation STALLED at 26 wallets (runs 91-110)"
    if addr.startswith("0x79cd174c"):
        e["label"] = "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - rotation STALLED at 20 wallets (runs 90-110)"
    if addr.startswith("0x1e9c6d46"):
        e["label"] = "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - NAMED (Seatbelt Dog / Seatbelt) - ANOMALY, reported once as signal run 101 - rotation STALLED at 26/27 sell wallets (union run101+run102; 0 wallets runs 103-110)"
        e["note"] = e.get("note", "") + " Run 110: 0 wallets (0 buys, 0 sells); sell-wallet union run101+run102 = 26/27 - STALLED at 26, did NOT reach 27. NOT a new rotation."

# ---- next run note: anchored updates on the existing note ----
note = s["next_run_note"]

def rep_once(old, new, tag):
    global note
    c = note.count(old)
    assert c == 1, f"{tag}: anchor count {c} != 1: {old[:120]!r}"
    note = note.replace(old, new)

# (0) window start
rep_once("Next run sent-tx window starts from block 132287240.",
         "Next run sent-tx window starts from block 132296161.", "window")

# (1)+(2) pair retry paragraph + inbound list line: replace span between
# "RETRY run 110:" and "(3) Run-109 inbound window"
i0 = note.index("RETRY run 110: (1) Pair token0/token1 reads")
i1 = note.index("(3) Run-109 inbound window")
new_retry = (
    "RETRY run 111: (1) Pair token0/token1 reads for 0xa6e6... pair 0x9fac925655fa4985ab4fe2fe9e0ca8ae323cc9da and 0x887c... pair "
    "0xa9fa6efb21c252b7d4ab81d19a07ee4ecf6d2c97 (fast_rpc race returns None / 'all endpoints failed', 28 consecutive runs - persistently unreadable, "
    "unverified not absence), plus 0x2bfb pair 0x782671f637bf1a01de482824c4b2520bc58a5a4b, 0xc459 pair 0xeca06856c88fcdf1506886431a079d3f2565ca82, and "
    "rotation 0x43c8 pair 0xaafebb5244e2e546f7cd18a2c89f85bbee03f1e0 (unreadable run 88-110, 23 consecutive - retry opportunistically, not an anomaly), "
    "PLUS run-89 rotation pairs 0xcfdb 0x1e04925db4eabab2917ef73a8cdf232bcc69b5ba, 0x0cf8 0xf6800c4a1ecdffbd64f9047c606bdb32dee0127f, 0xe68b "
    "0xfab7cb4979c9e4738afc61e4974177cf72c50896 (token0/token1 unreadable run 89-110, 22 consecutive; 0x31e4 pair 0x60ca0aef... READ OK run 89), PLUS "
    "run-102 rotation pairs 0x8b19 0xf7a2396852111ed1480d4ffca583696369c87eab + 0xd826 0x2315f44831bcac27bd7308e2d50943b4f115f4bd + 0x07b2 "
    "0x39f0227ba7aa712db15bdb51046647e8f0939b54 + 0x4263 0x70b31f93bff68d87ccd7b11c4458af5a7deb8d44 - ALL FOUR READ OK run 104 (token0/token1 confirmed, PCS V2 token/WBNB) - "
    "REMOVED from retry; PLUS run-103 rotation pairs 0x7809 0xfaba06b92f8e425055417fac8388dedf1cd58a72 + 0x7f0a "
    "0x25a1bf1d836ba5865d9ba1dfaea33c33ad06c754 + 0xf3bd 0xbf243f454ac1463f2b596d9843026299e0ea5e31 - ALL THREE READ OK run 104 (token0/token1 confirmed, PCS V2 token/WBNB) - "
    "REMOVED from retry; 4727 pair 0xf4ee6a9b528670fcdce10c8af0f5262b4fef1d3d READ OK run 102 (token0 = 4727 token, token1 = WBNB) - REMOVED from retry; "
    "1e9c pair 0x533623ca2db657de9a36e84e2b5a809fbee7ecbe READ OK run 102 (token0 = 1e9c token, token1 = WBNB) - REMOVED from retry; db49 pair "
    "0x41cbb4910fd4959f651d7bff8d8b5ed5cd355dfc READ OK run 101 (token0 = WBNB, token1 = db49 token) - REMOVED from retry; ff66 pair "
    "0x2d3e053bada0378299010fde9f59209985760bab READ OK run 101 (token0 = WBNB, token1 = ff66 token) - REMOVED from retry; 0x6b12 pair READ OK run 100 - "
    "already removed; 0x50e4 pair READ OK run 99 - already removed; 41cc pair READ OK run 99 - already removed; run-97 rotation pairs c90a/e3a8 READ OK "
    "run 98 - already removed; run-100 pairs 6f31 0xc9299379d122a1a84d45fdf1ee87dd0ce1a5e3e8 + 0d7e 0x98fe67c6aeb645e6c9aa41c1fd79898261e7fde7 READ OK run 100 "
    "(token0 = token, token1 = WBNB) - no retry needed. "
    "(2) Run-110 inbound list = run109 list (1734) + 0 run-110 deployments + 0 new rotation tokens (total 1734, unchanged); run-111 inbound list = run110 list (1734) "
    "+ run-111 deployments + new rotation tokens. "
    "PROCESS LESSON (run 110): inbound leg ran as 35x ~50-contract slices in 6 parallel rounds from the start (run110-inbound110.py <part> <start> <end>, ~3.5-6 min each round) - "
    "no full-chunk attempt, no silent death; round 3 stalled once (fresh Ankr call OK in 7.9s = stall, waited out); 3 in-chunk failures ('Remote end closed connection without response') "
    "recovered same-run via run110-inbound109-retry.py 3/3. A log frozen with NO live process is a silent death, re-run from scratch in smaller slices; "
    "a log frozen WITH live processes + a fresh Ankr call succeeding = a stall, wait it out. "
)
note = note[:i0] + new_retry + note[i1:]

# (3) inbound window line
rep_once("(3) Run-109 inbound window FULLY CLOSED in-run (1734/1734, 0 hits, 0 failed, NO retry needed - 0 in-chunk failures; "
         "verify at state-update time; if the retry had failures, they are listed in inbound_log_leg_run109.failed_contracts and must be retried in run 110). ",
         "(3) Run-110 inbound window FULLY CLOSED in-run (1734/1734, 0 hits, 3 in-chunk failures recovered same-run 3/3 via run110-inbound109-retry.py, 0 failed after retry; "
         "verify at state-update time; if the retry had failures, they are listed in inbound_log_leg_run110.failed_contracts and must be retried in run 111). ",
         "inbound-closed")

# (4) watch paragraph: replace span from "(4) 0x1e9c6d46... rotation STALLED" up to the dedupe sentence start
j0 = note.index("(4) 0x1e9c6d46... (Seatbelt) rotation STALLED")
j1 = note.index("Dedupe new mints against all tx hashes")
new_watch = (
    "(4) 0x1e9c6d46... (Seatbelt) rotation STALLED at 26/27 sell wallets (union run101+run102; 0 wallets runs 103-110) - "
    "did NOT reach 27; watch run 111 the same way, do NOT treat continuation as a new rotation. 0xdb4950e7... rotation COMPLETED run 100 (sell-wallet union "
    "run99+run100 = 27/27) - do NOT treat any db49 activity as a new rotation. 0x1153607e... rotation STALLED at 26 wallets (0 wallets runs 91-110, 20th quiet "
    "run after debut) - watch run 111 the same way. 0x79cd... STALLED at 20 wallets (0 wallets runs 90-110, 21st quiet run after debut) - same. Run-103 named "
    "rotations 0x7809.../0x7f0a.../0xf3bd...: 0 wallets run 110 (7th quiet run after debut) - watch run 111 the same way. Run-102 named rotations 0x8b19.../0xd826.../0x07b2.../0x4263...: "
    "0 wallets run 110 (8th quiet run after debut) - same. Run-101 named rotations 0x4727...: "
    "0 wallets run 110 (9th quiet run after debut) - same. Run-100 named rotations 0x6f31.../0x0d7e...: 0 wallets run 110 (10th quiet run after debut) - same. "
    "Run-99 named rotations 0x50e4.../0x6b12.../0xff66...: 0 wallets run 110 (11th quiet run after debut) - same. Run-98 named rotations 0x41cc.../0x43bc.../0x2120.../0xda79...: "
    "0 wallets run 110 (13th quiet run after debut) - same. Run-97 named rotations 0xc90a.../0xe3a8...: 0 wallets run 110 (13th quiet run after debut) - same. "
)
note = note[:j0] + new_watch + note[j1:]

# dedupe: append run-110 note after the run-109 note
rep_once("Run-109: ZERO mint-pattern txs (0 mint logs in 95 receipts) - AFeng 0 txs this run (no sale-calls at all), so no dividend-tracker repeats either. ",
         "Run-109: ZERO mint-pattern txs (0 mint logs in 95 receipts) - AFeng 0 txs this run (no sale-calls at all), so no dividend-tracker repeats either. "
         "Run-110: ZERO mint-pattern txs (0 mint logs in 99 receipts) - AFeng 0 txs this run (no sale-calls at all), so no dividend-tracker repeats either. ",
         "dedupe-run110")

# append run-110 entry to the paid-only signals list (after the run-109 entry's ending anchor)
rep_once("WAR3 #2511 routine mint (06:21:22 WIB, block 132287716) falls OUTSIDE this run's window (max block 132287239) - routine job's item, NOT reported here; "
         "NO chat report this run - nothing new) ",
         "WAR3 #2511 routine mint (06:21:22 WIB, block 132287716) falls OUTSIDE this run's window (max block 132287239) - routine job's item, NOT reported here; "
         "NO chat report this run - nothing new) "
         "run 110 (ZERO new rotations - the 27-wallet machine set had 0 txs, seventh straight quiet run; only 7/55 wallets active (churn set + one 0x2325 aggregator tx); named-rotation streak ended run 104; ZERO deployments - "
         "seventh straight run without deployments; paid max 3 wallets/token (churn trio only, 9 tokens at 3 wallets, all ...7777; 4 at 2, the 0x3628/0xa0c1 pair; 3 at 2, 0x3803+0xc7c5; 7 at 1, incl. one 0x2325 aggregator buy); "
         "0 overlap with run-109 paid tokens - churn set turned over completely again, seventh straight run with 0 overlap; 1e9c STALLED at 26/27 sell wallets (union run101+run102, 0 wallets runs 103-110); "
         "7809/7f0a/f3bd 0 wallets (7th quiet run after debut); 8b19/d826/07b2/4263 0 wallets (8th quiet run); 4727 0 wallets (9th quiet run); "
         "6f31/0d7e 0 wallets (10th quiet run); 50e4/6b12/ff66 0 wallets (11th quiet run); 41cc/43bc/2120/da79 0 wallets (13th quiet run); c90a/e3a8 0 wallets (13th quiet run); "
         "0x1153... STALLED at 26, 20th quiet run; 0x79cd... STALLED at 20, 21st quiet run; inbound FULLY CLOSED in-run "
         "(35x ~50-contract slices in 6 parallel rounds from the start - no silent death; 3 in-chunk failures recovered same-run 3/3 via retry, 0 failed after retry), 1734 contracts, 11,648 logs, 0 hits; "
         "0 NULL receipts; 0 status-0 txs; pair retry 8/8 FAILED (a6e6/887c/2bfb/c459 28th consecutive run, 43c8 23rd, cfdb/0cf8/e68b 22nd), retry run 111; "
         "0x2325 first activity since run 106 (1 aggregator 0x27772d13 tx, 0.01 BNB, 06:26:46 WIB - single-wallet paid buy, NOT a rotation/signal); "
         "NO chat report this run - nothing new) ",
         "paid-list-run110")

# append "Paid fact: run110" before the "Run 101 had 35 deployments" paragraph
rep_once("Run 101 had 35 deployments",
         "Paid fact: run110 ZERO new rotations (the 27-wallet machine set had 0 txs, seventh straight quiet run; only 7/55 wallets active - churn trio 0x3803/0xad94/0xc7c5 + pair 0x3628/0xa0c1 + 0x7488d5da + one 0x2325 aggregator tx); "
         "named-rotation streak ended run 104; ZERO deployments (seventh straight run without deployments); "
         "paid max 3 wallets/token (9 tokens at 3 wallets, all churn trio, all ...7777; 4 at 2, the 0x3628/0xa0c1 pair; 3 at 2, 0x3803+0xc7c5; 7 at 1, incl. one 0x2325 aggregator buy); 0 overlap with run-109 paid tokens (churn set turned over completely again); "
         "1e9c STALLED at 26/27 sell wallets (union run101+run102, 0 wallets runs 103-110); run-103 tokens 0x7809.../0x7f0a.../0xf3bd... 0 wallets (7th quiet run after debut); "
         "run-102 tokens 0x8b19.../0xd826.../0x07b2.../0x4263... 0 wallets (8th quiet run after debut); run-101 token 0x4727... 0 wallets (9th quiet run); "
         "run-100 tokens 0x6f31.../0x0d7e... 0 wallets (10th quiet run); run-99 tokens 0x50e4.../0x6b12.../0xff66... 0 wallets (11th quiet run); "
         "run-98 tokens 0x41cc.../0x43bc.../0x2120.../0xda79... 0 wallets (13th quiet run); run-97 tokens 0xc90a.../0xe3a8... 0 wallets (13th quiet run); "
         "run-90 tokens 0x6a25.../0x9f7e.../0x8c64.../0xc1ab.../0x1153... 0 wallets (20th quiet run after debut); run-89 tokens 0xcfdb.../0x0cf8.../0xe68b.../0x31e4... 0 wallets (21st quiet run after debut); "
         "run-88 tokens 0x43c8.../0x3d12.../0xeae0... 0 wallets (22nd quiet run after debut); run-87 tokens 0x889a.../0x4249... 0 wallets (23rd quiet run after debut); "
         "run-86 tokens 0x2bfb.../0xc459... 0 wallets (24th quiet run after debut); run-85 token 0x2717... 0 wallets (25th quiet run); "
         "run-82 tokens 0xd468.../0xa6e6.../0x887c... all 0 wallets (28th quiet run after debut); run-81 tokens 0 wallets (29th quiet run); run-80 token 0 wallets (30th quiet run); "
         "GrokBot 0xfcd0... absent (0 wallets) - 51st consecutive quiet run (59, 61-110) after the run-60 burst; CORLA-97af 0 wallets; CORLA 0x4a9c 0 wallets; all run-64/65 ASI contracts 0 wallets; "
         "all run-66/68/69/70/71/72/73/74/75/76/77/78/79 machine tokens 0 wallets. Run 110 had ZERO deployments (seventh straight run without deployments). "
         "AFeng 0 txs; future1001.ai 0 txs; 0x2325... 1 tx (aggregator 0x27772d13, 0.01 BNB, 06:26:46 WIB - first activity since run 106, single-wallet paid buy, NOT a rotation/signal); 0x8e96... 0 txs; "
         "0xc7c5... 36 txs (12 buys + 12 sells + 12 approvals, 0.00042 BNB); 0x3803... 36 txs (24 aggregator 0x39ecce49 + 12 approvals, 0.000312 BNB, 0 buys/sells); 0xad94... 28 txs (9 buys + 10 sells + 9 approvals, 0.000315 BNB); "
         "0x3628... 18 txs (5 buys + 6 sells + 6 approvals + 1 plain BNB transfer 0.00216596 BNB to 0xc0094886... at 07:00:30 WIB, 0.00256596 BNB); 0x7488d5da... 15 txs (5 buys + 5 sells + 5 approvals, 0.00042004 BNB); 0xa0c1... 13 txs (4 buys + 5 sells + 4 approvals, 0.0004 BNB). "
         "PROCESS NOTE (run 110): inbound leg ran as 35x ~50-contract slices in 6 parallel rounds from the start - no full-chunk attempt, no silent death; round 3 stalled once (fresh Ankr call OK in 7.9s = stall, waited out); "
         "3 in-chunk failures ('Remote end closed connection without response') recovered same-run via retry 3/3. "
         "fast_rpc race outage TOTAL during the pair retry again (8/8 failed) while the receipts batch worked fine earlier the same run - "
         "the outage is time-varying, not permanent; a failed race read is UNVERIFIED, never absence - retry, don't conclude. Run 101 had 35 deployments",
         "paid-fact-run110")

s["next_run_note"] = note

json.dump(s, open(P, "w"), indent=1)
print("state updated; last_run now:", s["last_run"]["run"], "block_end:", s["last_run"]["block_end"])
print("machine_tokens:", len(s.get("machine_tokens", [])), "| signaled:", len(s.get("signaled_projects_over_20pct", [])))
print("inbound110 complete:", s["inbound_log_leg_run110"]["complete"], "| failed:", s["inbound_log_leg_run110"]["failed"],
      "| total_logs:", s["inbound_log_leg_run110"]["total_logs"], "| hits:", s["inbound_log_leg_run110"]["hits"])
print("next_run_note len:", len(s["next_run_note"]))
