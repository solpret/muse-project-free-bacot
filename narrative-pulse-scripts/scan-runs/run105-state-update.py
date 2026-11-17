#!/usr/bin/env python3
"""Run 105 state update (read-only job bookkeeping; no chain writes).

Completes run 105 (window 132252160-132260249, tx 2026-11-08 01:57:49 - 02:55:19 WIB).
Sent/receipts/paid done and verified; inbound leg run-105 window CLOSED in-run
(1734/1734, 0 hits, 0 failed after same-run retry of 7 failed contracts).
NO new mints - ZERO mint-pattern txs (0 mint logs in 113 receipts; AFeng 0 txs this run,
no sale-calls at all, so no dividend-tracker repeats either).
ZERO new machine-token rotations - the 27-wallet machine set had 0 txs this run; only
6/55 wallets active (churn set). The named-rotation streak ended run 104; run 105 has 0.
ZERO deployments - second straight run without deployments (run 104: 0; runs 97-103 had 25/72/64/32/35/70/68).
Paid max 3 wallets/token (churn trio only). Bridge unchanged (0 new mints, 0 not_evaluated).
Pair retry: 8/8 FAILED again (a6e6/887c/2bfb/c459 23rd consecutive run, 43c8 18th,
cfdb/0cf8/e68b 17th) - retry run 106.
HokiFrog targeted check (parent-reported strong lead, first mint in-window block 132254774):
586 logs, 0 hits - no tracked wallet minted it; already handled by the routine job (sold out).
No chat report this run: nothing new to report (no mints, no signal, no anomaly, no auto-mint trigger).
"""
import json, shutil

P = "/home/hatch/workspace/narrative-pulse/tracked-wallet-mint-scan-state.json"
shutil.copy(P, str(P) + ".bak-run105-pre")
s = json.load(open(P))
SR = "/home/hatch/workspace/narrative-pulse/scan-runs"

# ---- inbound totals from chunk JSONs (self-verifying) ----
chunks = {}
for part in ["a", "b1", "b2", "b3a", "b3b", "b3c"]:
    chunks[part] = json.load(open(f"{SR}/run105-inbound105-{part}.json"))
tot_contracts = sum(c["contracts_checked"] for c in chunks.values())
tot_logs = sum(c["total_logs"] for c in chunks.values())
tot_hits = sum(len(c["hits"]) for c in chunks.values())
tot_failed = sum(len(c["failed"]) for c in chunks.values())
tot_trunc = sum(len(c["truncated"]) for c in chunks.values())
print(f"inbound totals: contracts={tot_contracts} logs={tot_logs} hits={tot_hits} failed={tot_failed} truncated={tot_trunc}")
assert tot_contracts == 1734, f"inbound contracts {tot_contracts} != 1734"
assert tot_hits == 0, f"inbound hits {tot_hits} != 0 (must handle before state update!)"
failed_contracts = [f for c in chunks.values() for f in c["failed"]]
retry = json.load(open(f"{SR}/run105-inbound104-retry.json"))
retry_failed_addrs = {f["contract"] for f in failed_contracts}
assert retry["contracts_checked"] == len(retry_failed_addrs), "retry did not cover all failed contracts"
assert retry["failed"] == [], f"retry itself failed: {retry['failed']}"
assert retry["hits"] == [], "retry found hits - must handle before state update!"
print(f"same-run retry recovered {len(retry_failed_addrs)}/{len(retry_failed_addrs)} failed contract(s): "
      f"{sorted(retry_failed_addrs)} -> {retry['total_logs']} logs, 0 hits")
eff_failed = 0
tot_logs_effective = tot_logs + retry["total_logs"]

last_run_105 = {
    "run": 105,
    "block_start": 132252160,
    "block_end": 132260249,
    "window_wib": "2026-11-08 01:57:49 - 2026-11-08 02:55:19 WIB (tx times); run executed ~02:52 WIB - ~03:45 WIB; sent-pass in-window txs 170, 0 mint-pattern txs (0 new mints - AFeng 0 txs this run, no sale-calls at all, so no dividend-tracker repeats either)",
    "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set); 0 failed first attempt, only 6 wallets active.",
    "method_note": (
        "Sent pass Ankr ankr_getTransactionsByAddress via module: 55/55 OK first attempt (170 txs), 0 failed, only 6 wallets active (vs 6 run 104). "
        "Receipts via fast_rpc batch (6, ~4s pause) for 113 non-approve candidates: 113 status 1, 0 status 0, 0 NULL - fast this run, no race fallbacks. "
        "Mint-pattern txs: 0 - ZERO mint logs in 113 receipts. No new mints of any kind. AFeng 0 txs this run (no sale-calls at all) - the dividend-tracker mint "
        "pattern of runs 70/75/101/102 did NOT repeat (and could not repeat without AFeng sale-calls). "
        "Paid: 24 tokens; max 3 wallets/token (14 tokens at 3 wallets, ALL the same churn trio 0x3803/0xad94/0xc7c5, all ...7777; 6 at 2 (ALL the 0x3628/0xa0c1 pair, all ...7777); "
        "4 at 1 (ALL 0x7488d5da)). Overlap with run-104 paid tokens: 0 - the ...7777 churn set turned over COMPLETELY again this run (second straight run with 0 overlap; run 104 overlap was also 0). "
        "ZERO new rotations - the 27-wallet machine set had 0 txs this run (no buys, no sells, no approvals from any of the 27). The named-rotation streak ENDED run 104 "
        "(runs 97-103); run 105 has 0, second straight quiet run. No anomaly to report under the fast-path amendment (no new token, no name/symbol "
        "appearing, no size anomaly, no free-mint path). Trigger >25% NOT met by any token (max 3 wallets = 5.5%). No preview, no execution. "
        "Seatbelt 1e9c STALLED at 26: 0 wallets this run (0 buys, 0 sells) - sell-wallet union run101+run102 = 26/27, runs 103-105 add 0 - did NOT reach 27. "
        "NOT a new rotation; watch run 106 the same way. "
        "Deployments: ZERO - second straight run without deployments (run 104: 0; runs 97-103 had 25/72/64/32/35/70/68). "
        "Inbound list for run 105 = run104 list (1734) + 0 deployments + 0 new rotation tokens (total 1734, unchanged). "
        "HokiFrog targeted check: parent reported HokiFrog 0xeb3ede3893ca798f30648194eCC03119A7071b40 as a Free Bacot strong lead (first mint 2026-11-08 02:14:15 WIB, "
        "block 132254774, INSIDE this run's window), sold out ~03:11 WIB. This job checked the contract directly (Ankr getLogs, window 132252160-132260249): 586 logs, "
        "0 zero-from Transfers to a tracked wallet - NO tracked wallet minted HokiFrog (sent pass already showed 0 mint logs; this closes the inbound-only gap). "
        "HokiFrog is a Free Bacot matter already reported by the routine job; nothing for this job to add, do NOT re-report. "
        "AFeng (0xbf004bff...) 0 txs; future1001.ai (0x36239612...) 0 txs; 0x2325... 0 txs; 0x8e96... 0 txs; 0x6ba79dcc/0x89220022/0xda91cefe 0 txs. "
        "0x3803... 42 txs (28 aggregator 0x39ecce49 + 14 approvals, total value 0.0004 BNB, churn as usual); 0xad94... 41 txs (14 buys + 13 sells + 14 approvals, 0.0005 BNB); "
        "0xc7c5... 42 txs (14 buys + 14 sells + 14 approvals, 0.0014 BNB). 0x3628... 16 txs + 0xa0c1... 17 txs (PCS micro buy-then-sell on the same ...7777 set, "
        "0.0001 BNB per buy pattern as usual). 0x7488d5da... 12 txs (4 buys + 4 sells + 4 approvals). 0 plain BNB transfers (run 104 had 2). "
        "Selectors (sent pass, 170 txs): 57 approvals (0x095ea7b3) + 44 PCS buys (0xb6f9de95) + 41 PCS sells (0x791ac947) + 28 aggregator (0x39ecce49). NO contract creations, "
        "NO sale-calls (0x4d819a2a), NO aggregator 0x27772d13, NO transfers (0xa9059cbb), NO empty-input txs. "
        "Nonzero-value txs 58, total 0.002883 BNB, max 0.0001 BNB - the quietest run by value in the recent series (run 104 total was 0.0088 BNB; run 103 total was 33.4966 BNB). "
        "Most active wallets: 0xc7c5faa2 42, 0x38031ca8 42, 0xad94ee77 41, 0xa0c1e94f 17, 0x3628764a 16, 0x7488d5da 12. "
        "0 NULL receipts this run. 0 status-0 txs. "
        f"Inbound leg (amendment 12:02 WIB): Ankr getLogs address-filtered per contract, 1734 contracts (run104 list, unchanged - 0 deployments + 0 new rotation tokens), "
        f"0 hits, {tot_logs_effective} logs, window 132252160-132260249. "
        f"Chunk a (400, 5,372 logs, 1 failed, 3 truncated) + b1 (200, 3,277 logs, 0 failed, 3 truncated) + b2 (200, 787 logs, 1 failed, 0 truncated) + "
        f"b3a (312, 396 logs, 2 failed, 0 truncated) + b3b (311, 0 logs, 2 failed, 0 truncated) + b3c (311, 0 logs, 1 failed, 0 truncated) + retry (7 contracts, 1 log, "
        f"0 failed - the 7 in-chunk failures 0x3dc4a7ad..., 0xc4f2797f..., 0x95b84cb4..., 0x8e46b149..., 0xe84bd4ff..., 0x80f6bab8..., 0x4f3fe54d... recovered same-run 7/7) = {tot_logs_effective} logs, 0 hits, 0 FAILED after retry. "
        "Truncated contracts, all topic-filtered to 0 logs (a: 0x1de4... AFeng sale, 0x3dca..., 0x55d398... USDT; b1: 0x63de... AGC, 0x7857..., 0x7e2d...; b2/b3a/b3b/b3c: none). "
        "First-attempt chunks did NOT wedge this run (unlike runs 103-104) - all 6 progressed from the start. BUT all chunks stalled TWICE mid-run (~5-7 min frozen log each time, "
        "live processes, first at ~150 contracts, second at ~200/250) and resumed on their own both times - stalls, not wedges. PROCESS LESSON (run 105): the run-104 note's "
        "'wait >5 min frozen WITH a fresh Ankr call working before killing' threshold was MET during the first stall (fresh Ankr call worked in 8.6s) and killing then would still "
        "have been WRONG - the chunks resumed ~2 min later. A frozen log + live process + working fresh Ankr call is a STALL: wait it out; kill only if frozen well past ~10 min. "
        "Window FULLY CLOSED in-run, no retry deferred to run 106. "
        "Pair retry 8/8 FAILED this run (all eight pairs: a6e6/887c/2bfb/c459/43c8/cfdb/0cf8/e68b - token0()/token1() all 'all endpoints failed' via fast_rpc race, OSError/TimeoutError, "
        "in run105-pair-retry.py) - unverified, not absence; 23rd consecutive run for a6e6/887c/2bfb/c459, 18th for 43c8, 17th for cfdb/0cf8/e68b; retry run 106. "
        "fast_rpc race outage was TOTAL during the pair retry (unlike run 104, where the last 7 pairs succeeded minutes later) - but the receipts batch pass worked fine earlier in the "
        "same run, so the outage is time-varying, not permanent. A failed race read is UNVERIFIED, never absence - retry, don't conclude. "
        "SCRIPT QUIRK (run 105, no impact): run105-rotation-analysis.py computed the 'run103 machine set' as size 0 because it reads the PREVIOUS run's paid file (run104-paid.json), "
        "where rotation token 4263 was quiet (0 wallets). Overlap only matters for tokens >=12 wallets (none this run), so no impact; fix opportunistically by deriving the machine set "
        "from the rotation's debut-run paid file instead of the previous run's. "
        "Pointer-discovery (amendment 19:10): 0 contracts processed - no new mints this run, and the backfill queue is empty (bridge 115 contracts, "
        "0 not_evaluated); bridge unchanged. CHAT REPORT this run: NONE - nothing new to report (no new mints, no Free Bacot signal, no anomaly, no auto-mint trigger, "
        "no guard block). No preview/mint/sign/login/purchase by this job."
    ),
}
s["last_run"] = last_run_105

# ---- paid trend (no paid_signal this run - no anomaly) ----
s["paid_trend_run105"] = {
    "note": "Aggregate only, NOT a buy recommendation. ZERO new rotations - the machine set was dormant again (only 6/55 wallets active; the 27-wallet machine set 0 txs, "
            "second straight quiet run; named-rotation streak ended run 104). ZERO deployments - second straight run without deployments. "
            "Paid max 3 wallets/token (churn trio only, 14 tokens at 3 wallets, all ...7777; 6 at 2, all the 0x3628/0xa0c1 pair; 4 at 1, all 0x7488d5da); "
            "0 overlap with run-104 paid tokens (churn set turned over completely again, second straight run with 0 overlap). "
            "Seatbelt 1e9c STALLED at 26/27 sell wallets (union run101+run102; 0 wallets runs 103-105) - did NOT reach 27. "
            "Run-103 named rotations 7809/7f0a/f3bd: 0 wallets (2nd quiet run after debut); run-102 named rotations 8b19/d826/07b2/4263: 0 wallets (3rd quiet run after debut); "
            "run-101 named rotation 4727: 0 wallets (4th quiet run after debut); run-100 named rotations 6f31/0d7e: 0 wallets (5th quiet run after debut); "
            "run-99 named rotations 50e4/6b12/ff66: 0 wallets (6th quiet run after debut); run-98 named rotations 41cc/43bc/2120/da79: 0 wallets (8th quiet run after debut); "
            "run-97 named rotations c90a/e3a8: 0 wallets (8th quiet run after debut); "
            "0x1153... STALLED at 26 wallets (15th quiet run); 0x79cd... STALLED at 20 wallets (16th quiet run). ZERO deployments - second straight run. "
            "HokiFrog (parent-reported strong lead, first mint in-window): 0 tracked-wallet mints (targeted Ankr getLogs, 586 logs, 0 hits) - already handled by the routine job (sold out). "
            "Inbound run-105 window FULLY CLOSED in-run "
            f"(1734/1734, {tot_logs_effective} logs, 0 hits, 0 failed after same-run retry of 7 failed contracts).",
    "rotations": "ZERO new rotations this run. The 27-wallet machine set had 0 txs, second straight quiet run. Named-rotation streak ended run 104. "
                 "Seatbelt 1e9c rotation STALLED at 26/27 sell wallets (union run101+run102; 0 wallets runs 103-105) - watch run 106 the same way, NOT a new rotation.",
    "other_paid_activity": [
        {
            "pattern": "14 tokens x 3 wallets, all the same churn trio 0x3803/0xad94/0xc7c5, all ...7777 (PCS micro buy-then-sell); 0 overlap with run-104 paid tokens",
            "wallet": "churn trio (see paid_trend_run1 for the pattern)",
        },
        {
            "pattern": "6 tokens x 2 wallets, both 0x3628764a6576b8dfb31fba0aac6a333b64851423 + 0xa0c1e94fbc1a93e39f5eb828f960aa080a9d9b9e, all ...7777",
            "wallet": "0x3628764a6576b8dfb31fba0aac6a333b64851423 + 0xa0c1e94fbc1a93e39f5eb828f960aa080a9d9b9e",
        },
        {
            "pattern": "4 tokens x 1 wallet (PCS micro buys)",
            "wallet": "0x7488d5da6a6097de0ff88c7492c62c2fd1e56650",
        },
        {
            "pattern": "28 txs via aggregator 0x855066c8679c77a0258e792b5ccf19f8c227eb31 (selector 0x39ecce49) + 14 approvals, total value 0.0004 BNB (churn as usual)",
            "wallet": "0x38031ca8a54526f9fe90f11f07b55ae5fc01036a",
        },
        {
            "pattern": "AFeng 0 txs, future1001.ai 0 txs, 0x2325... 0 txs, 0x8e96... 0 txs - the non-churn tracked wallets were all silent this run",
            "wallet": "0xbf004bff64725914ee36d03b87d6965b0ced4903 / 0x362396125a / 0x2325f175975abdbcde555c79cc8e63381d28551b / 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6",
        },
    ],
}

s["inbound_log_leg_run105"] = {
    "contracts": 1734,
    "attempted": 1734,
    "completed_with_0_hits": 1734,
    "total_logs": tot_logs_effective,
    "hits": 0,
    "failed": eff_failed,
    "failed_contracts": [],
    "failed_then_recovered_same_run": failed_contracts,
    "never_attempted": 0,
    "complete": eff_failed == 0,
    "note": "Ankr getLogs address-filtered per contract, window 132252160-132260249, from list run105-inbound-contracts.json (1734 contracts = run104 list, unchanged - "
            f"0 run-105 deployments + 0 new rotation tokens). Full pass a (400, 5,372 logs, 1 failed, 3 truncated) + "
            f"b1 (200, 3,277 logs, 0 failed, 3 truncated) + b2 (200, 787 logs, 1 failed, 0 truncated) + b3a (312, 396 logs, 2 failed, 0 truncated) + "
            f"b3b (311, 0 logs, 2 failed, 0 truncated) + b3c (311, 0 logs, 1 failed, 0 truncated) + retry (7 contracts, 1 log, 0 hits - the 7 in-chunk failures "
            f"0x3dc4a7ad..., 0xc4f2797f..., 0x95b84cb4..., 0x8e46b149..., 0xe84bd4ff..., 0x80f6bab8..., 0x4f3fe54d... recovered 7/7 same-run) = {tot_logs_effective} logs, 0 hits, 0 FAILED after retry. "
            "Truncated contracts, all topic-filtered to 0 logs (a: 0x1de4... AFeng sale, 0x3dca..., 0x55d398... USDT; "
            "b1: 0x63de... AGC, 0x7857..., 0x7e2d...; b2/b3a/b3b/b3c: none). "
            "First-attempt chunks did NOT wedge this run (unlike runs 103-104) - all 6 progressed from the start; but all chunks stalled TWICE mid-run (~5-7 min frozen log, "
            "live processes) and resumed on their own both times - stalls, not wedges. "
            "Window FULLY CLOSED in-run, no retry deferred to run 106."
            if eff_failed == 0 else
            "Window NOT fully closed: failed contracts must be retried in run 106.",
}

# ---- stalled-label run-range updates ----
for e in s["machine_tokens"]:
    addr = e["address"].lower()
    if addr.startswith("0x1153607e"):
        e["label"] = "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - rotation STALLED at 26 wallets (runs 91-105)"
    if addr.startswith("0x79cd174c"):
        e["label"] = "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - rotation STALLED at 20 wallets (runs 90-105)"
    if addr.startswith("0x1e9c6d46"):
        e["label"] = "machine-token (fast-path amendment 2026-11-06 ~18:30 WIB) - NAMED (Seatbelt Dog / Seatbelt) - ANOMALY, reported once as signal run 101 - rotation STALLED at 26/27 sell wallets (union run101+run102; 0 wallets runs 103-105)"
        e["note"] = e.get("note", "") + " Run 105: 0 wallets (0 buys, 0 sells); sell-wallet union run101+run102 = 26/27 - STALLED at 26, did NOT reach 27. NOT a new rotation."

# ---- next run note: anchored updates on the existing note ----
note = s["next_run_note"]

def rep_once(old, new, tag):
    global note
    c = note.count(old)
    assert c == 1, f"{tag}: anchor count {c} != 1: {old[:120]!r}"
    note = note.replace(old, new)

# (0) window start
rep_once("Next run sent-tx window starts from block 132252160.",
         "Next run sent-tx window starts from block 132260250.", "window")

# (1)+(2) pair retry paragraph + inbound list line: replace span between
# "RETRY run 105:" and "(3) Run-104 inbound window"
i0 = note.index("RETRY run 105: (1) Pair token0/token1 reads")
i1 = note.index("(3) Run-104 inbound window")
new_retry = (
    "RETRY run 106: (1) Pair token0/token1 reads for 0xa6e6... pair 0x9fac925655fa4985ab4fe2fe9e0ca8ae323cc9da and 0x887c... pair "
    "0xa9fa6efb21c252b7d4ab81d19a07ee4ecf6d2c97 (fast_rpc race returns None / 'all endpoints failed', 23 consecutive runs - persistently unreadable, "
    "unverified not absence), plus 0x2bfb pair 0x782671f637bf1a01de482824c4b2520bc58a5a4b, 0xc459 pair 0xeca06856c88fcdf1506886431a079d3f2565ca82, and "
    "rotation 0x43c8 pair 0xaafebb5244e2e546f7cd18a2c89f85bbee03f1e0 (unreadable run 88-105, 18 consecutive - retry opportunistically, not an anomaly), "
    "PLUS run-89 rotation pairs 0xcfdb 0x1e04925db4eabab2917ef73a8cdf232bcc69b5ba, 0x0cf8 0xf6800c4a1ecdffbd64f9047c606bdb32dee0127f, 0xe68b "
    "0xfab7cb4979c9e4738afc61e4974177cf72c50896 (token0/token1 unreadable run 89-105, 17 consecutive; 0x31e4 pair 0x60ca0aef... READ OK run 89), PLUS "
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
    "(2) Run-105 inbound list = run104 list (1734) + 0 run-105 deployments + 0 new rotation tokens (total 1734, unchanged); run-106 inbound list = run105 list (1734) "
    "+ run-106 deployments + new rotation tokens. "
)
note = note[:i0] + new_retry + note[i1:]

# (3) inbound window line
rep_once("(3) Run-104 inbound window FULLY CLOSED in-run (1734/1734, 0 hits, 0 failed after same-run retry of 3 failed contracts - "
         "verify at state-update time; if the retry had failures, they are listed in inbound_log_leg_run104.failed_contracts and must be retried in run 105). ",
         "(3) Run-105 inbound window FULLY CLOSED in-run (1734/1734, 0 hits, 0 failed after same-run retry of 7 failed contracts - "
         "verify at state-update time; if the retry had failures, they are listed in inbound_log_leg_run105.failed_contracts and must be retried in run 106). ",
         "inbound-closed")

# (4) watch paragraph: replace span from "(4) 0x1e9c6d46... rotation STALLED" up to the dedupe sentence start
j0 = note.index("(4) 0x1e9c6d46... (Seatbelt) rotation STALLED")
j1 = note.index("Dedupe new mints against all tx hashes")
new_watch = (
    "(4) 0x1e9c6d46... (Seatbelt) rotation STALLED at 26/27 sell wallets (union run101+run102; 0 wallets runs 103-105) - "
    "did NOT reach 27; watch run 106 the same way, do NOT treat continuation as a new rotation. 0xdb4950e7... rotation COMPLETED run 100 (sell-wallet union "
    "run99+run100 = 27/27) - do NOT treat any db49 activity as a new rotation. 0x1153607e... rotation STALLED at 26 wallets (0 wallets runs 91-105, 15th quiet "
    "run after debut) - watch run 106 the same way. 0x79cd... STALLED at 20 wallets (0 wallets runs 90-105, 16th quiet run after debut) - same. Run-103 named "
    "rotations 0x7809.../0x7f0a.../0xf3bd...: 0 wallets run 105 (2nd quiet run after debut) - watch run 106 the same way. Run-102 named rotations 0x8b19.../0xd826.../0x07b2.../0x4263...: "
    "0 wallets run 105 (3rd quiet run after debut) - same. Run-101 named rotations 0x4727...: "
    "0 wallets run 105 (4th quiet run after debut) - same. Run-100 named rotations 0x6f31.../0x0d7e...: 0 wallets run 105 (5th quiet run after debut) - same. "
    "Run-99 named rotations 0x50e4.../0x6b12.../0xff66...: 0 wallets run 105 (6th quiet run after debut) - same. Run-98 named rotations 0x41cc.../0x43bc.../0x2120.../0xda79...: "
    "0 wallets run 105 (8th quiet run after debut) - same. Run-97 named rotations 0xc90a.../0xe3a8...: 0 wallets run 105 (8th quiet run after debut) - same. "
)
note = note[:j0] + new_watch + note[j1:]

# dedupe: append run-105 note after the run-104 note
rep_once("Run-104: ZERO mint-pattern txs (0 mint logs in 185 receipts) - AFeng 0 txs this run (no sale-calls at all), so no dividend-tracker repeats either. ",
         "Run-104: ZERO mint-pattern txs (0 mint logs in 185 receipts) - AFeng 0 txs this run (no sale-calls at all), so no dividend-tracker repeats either. "
         "Run-105: ZERO mint-pattern txs (0 mint logs in 113 receipts) - AFeng 0 txs this run (no sale-calls at all), so no dividend-tracker repeats either. "
         "HokiFrog targeted check run 105: 586 logs, 0 hits - no tracked wallet minted HokiFrog. ",
         "dedupe-run105")

# append run-105 entry to the paid-only signals list (after the run-104 entry's ending anchor)
rep_once("NO chat report this run - nothing new) ",
         "NO chat report this run - nothing new) "
         "run 105 (ZERO new rotations - the 27-wallet machine set had 0 txs, second straight quiet run; only 6/55 wallets active; named-rotation streak ended run 104; ZERO deployments - "
         "second straight run without deployments; paid max 3 wallets/token (churn trio only, 14 tokens at 3 wallets, all ...7777; "
         "0 overlap with run-104 paid tokens - churn set turned over completely again); 1e9c STALLED at 26/27 sell wallets (union run101+run102, 0 wallets runs 103-105); "
         "7809/7f0a/f3bd 0 wallets (2nd quiet run after debut); 8b19/d826/07b2/4263 0 wallets (3rd quiet run); 4727 0 wallets (4th quiet run); "
         "6f31/0d7e 0 wallets (5th quiet run); 50e4/6b12/ff66 0 wallets (6th quiet run); 41cc/43bc/2120/da79 0 wallets (8th quiet run); c90a/e3a8 0 wallets (8th quiet run); "
         "0x1153... STALLED at 26, 15th quiet run; 0x79cd... STALLED at 20, 16th quiet run; inbound FULLY CLOSED in-run "
         "(chunks did NOT wedge this run but stalled twice ~5-7 min and resumed on their own - wait it out, do not kill), 1734 contracts, 9,833 logs, 0 hits, "
         "0 failed after same-run retry of 7 failed contracts; 0 NULL receipts; 0 status-0 txs; pair retry 8/8 FAILED (a6e6/887c/2bfb/c459 23rd consecutive run, 43c8 18th, cfdb/0cf8/e68b 17th), retry run 106; "
         "HokiFrog targeted check: 0 tracked-wallet mints (586 logs, 0 hits) - already handled by the routine job; NO chat report this run - nothing new) ",
         "paid-list-run105")

# append "Paid fact: run105" before the "Run 101 had 35 deployments" paragraph
rep_once("Run 101 had 35 deployments",
         "Paid fact: run105 ZERO new rotations (the 27-wallet machine set had 0 txs, second straight quiet run; only 6/55 wallets active - churn trio 0x3803/0xad94/0xc7c5 + pair 0x3628/0xa0c1 + 0x7488d5da); "
         "named-rotation streak ended run 104; ZERO deployments (second straight run without deployments); "
         "paid max 3 wallets/token (14 tokens at 3 wallets, all churn trio, all ...7777; 6 at 2, all the 0x3628/0xa0c1 pair; 4 at 1, all 0x7488d5da); 0 overlap with run-104 paid tokens (churn set turned over completely again); "
         "1e9c STALLED at 26/27 sell wallets (union run101+run102, 0 wallets runs 103-105); run-103 tokens 0x7809.../0x7f0a.../0xf3bd... 0 wallets (2nd quiet run after debut); "
         "run-102 tokens 0x8b19.../0xd826.../0x07b2.../0x4263... 0 wallets (3rd quiet run after debut); run-101 token 0x4727... 0 wallets (4th quiet run); "
         "run-100 tokens 0x6f31.../0x0d7e... 0 wallets (5th quiet run); run-99 tokens 0x50e4.../0x6b12.../0xff66... 0 wallets (6th quiet run); "
         "run-98 tokens 0x41cc.../0x43bc.../0x2120.../0xda79... 0 wallets (8th quiet run); run-97 tokens 0xc90a.../0xe3a8... 0 wallets (8th quiet run); "
         "run-90 tokens 0x6a25.../0x9f7e.../0x8c64.../0xc1ab.../0x1153... 0 wallets (15th quiet run after debut); run-89 tokens 0xcfdb.../0x0cf8.../0xe68b.../0x31e4... 0 wallets (16th quiet run after debut); "
         "run-88 tokens 0x43c8.../0x3d12.../0xeae0... 0 wallets (17th quiet run after debut); run-87 tokens 0x889a.../0x4249... 0 wallets (18th quiet run after debut); "
         "run-86 tokens 0x2bfb.../0xc459... 0 wallets (19th quiet run after debut); run-85 token 0x2717... 0 wallets (20th quiet run); "
         "run-82 tokens 0xd468.../0xa6e6.../0x887c... all 0 wallets (23rd quiet run after debut); run-81 tokens 0 wallets (24th quiet run); run-80 token 0 wallets (25th quiet run); "
         "GrokBot 0xfcd0... absent (0 wallets) - 46th consecutive quiet run (59, 61-105) after the run-60 burst; CORLA-97af 0 wallets; CORLA 0x4a9c 0 wallets; all run-64/65 ASI contracts 0 wallets; "
         "all run-66/68/69/70/71/72/73/74/75/76/77/78/79 machine tokens 0 wallets. Run 105 had ZERO deployments (second straight run without deployments). "
         "AFeng 0 txs; future1001.ai 0 txs; 0x2325... 0 txs; 0x8e96... 0 txs; 0x3803... 42 txs (28 aggregator 0x39ecce49 + 14 approvals, 0.0004 BNB); 0xad94... 41 txs (14 buys + 13 sells + 14 approvals, 0.0005 BNB); "
         "0xc7c5... 42 txs (14 buys + 14 sells + 14 approvals, 0.0014 BNB); 0x3628... 16 txs + 0xa0c1... 17 txs (PCS micro buy-then-sell); 0x7488d5da... 12 txs (4 buys + 4 sells + 4 approvals). "
         "PROCESS LESSON (run 105): inbound chunks stalled TWICE mid-run (~5-7 min frozen log each time, live processes) and resumed on their own both times - a frozen log + live process + "
         "working fresh Ankr call is a STALL, not a wedge: wait it out; kill only if frozen well past ~10 min. The run-104 '>5 min frozen WITH fresh Ankr call working' kill threshold was met "
         "during the first stall and killing then would still have been wrong. fast_rpc race outage TOTAL during the pair retry (8/8 failed) while the receipts batch worked fine earlier the same run - "
         "the outage is time-varying, not permanent; a failed race read is UNVERIFIED, never absence - retry, don't conclude. HokiFrog targeted check (parent-reported strong lead, first mint "
         "in-window block 132254774): 586 logs, 0 hits - no tracked wallet minted it; already handled by the routine job (sold out), do NOT re-report. Run 101 had 35 deployments",
         "paid-fact-run105")

s["next_run_note"] = note

json.dump(s, open(P, "w"), indent=1)
print("state updated; last_run now:", s["last_run"]["run"], "block_end:", s["last_run"]["block_end"])
print("machine_tokens:", len(s.get("machine_tokens", [])), "| signaled:", len(s.get("signaled_projects_over_20pct", [])))
print("inbound105 complete:", s["inbound_log_leg_run105"]["complete"], "| failed:", s["inbound_log_leg_run105"]["failed"],
      "| total_logs:", s["inbound_log_leg_run105"]["total_logs"], "| hits:", s["inbound_log_leg_run105"]["hits"])
print("next_run_note len:", len(s["next_run_note"]))
