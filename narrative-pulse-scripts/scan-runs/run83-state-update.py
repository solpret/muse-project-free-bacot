#!/usr/bin/env python3
"""Run 83 state update (read-only job bookkeeping; no chain writes).

Completes run 83 (window 132023418-132031246, tx 21:21:35-22:17:05 WIB).
Sent/receipts/paid/deployments done; inbound leg ran in full from ONE frozen
list (run83-inbound-contracts.json, 1061 contracts = run81 list + 3 run-82
machine tokens + 42 run-82 deployment addresses) in 4 parallel chunks, with
retries for every failed contract. If last_run is already 84+ (run 84 started
before this update), merge run-83 results WITHOUT regressing last_run/block_end.
"""
import json, shutil
from pathlib import Path

P = "/home/hatch/workspace/narrative-pulse/tracked-wallet-mint-scan-state.json"
D = Path("/home/hatch/workspace/narrative-pulse/scan-runs")
shutil.copy(P, str(P) + ".bak-run83-pre")
s = json.load(open(P))

ia = json.load(open(D / "run83-inbound-a.json"))
ib1 = json.load(open(D / "run83-inbound-b1.json"))
ib2 = json.load(open(D / "run83-inbound-b2.json"))
ib3 = json.load(open(D / "run83-inbound-b3.json"))
r_b12 = json.load(open(D / "run83-inbound-retry-b12.json"))      # reconstructed (see note below)
r_multi = json.load(open(D / "run83-inbound-retry-multi.json"))  # 2nd retry: b3 34 + b12 leftovers 3
r_a = json.load(open(D / "run83-inbound-retry-a.json"))
r_a_last = json.load(open(D / "run83-inbound-retry-a-last.json"))
r82 = json.load(open(D / "run83-inbound-retry82.json"))
nd = json.load(open(D / "run83-inbound-newdep.json"))
nd_r = json.load(open(D / "run83-inbound-newdep-retry.json"))
dep = json.load(open(D / "run83-deployments.json"))
sent = json.load(open(D / "run83-sent.json"))
paid = json.load(open(D / "run83-paid.json"))

n_logs = ia["total_logs"] + ib1["total_logs"] + ib2["total_logs"] + ib3["total_logs"]
n_hits = len(ia["hits"]) + len(ib1["hits"]) + len(ib2["hits"]) + len(ib3["hits"])
n_failed = len(ia["failed"]) + len(ib1["failed"]) + len(ib2["failed"]) + len(ib3["failed"])
trunc = ia["truncated"] + ib1["truncated"] + ib2["truncated"] + ib3["truncated"]
failed_contracts = [f["contract"] for f in ia["failed"] + ib1["failed"] + ib2["failed"] + ib3["failed"]]
retry_logs = r_b12["total_logs"] + r_multi["total_logs"] + r_a["total_logs"] + r_a_last["total_logs"]
print(f"inbound main: contracts=1061 logs={n_logs} hits={n_hits} failed={n_failed} truncated={len(trunc)}")
print(f"retries: b12={r_b12['total_logs']} logs/{len(r_b12['failed'])} failed; "
      f"multi={r_multi['total_logs']} logs/{len(r_multi['failed'])} failed; "
      f"a={r_a['total_logs']} logs/{len(r_a['failed'])} failed; a-last={r_a_last['total_logs']} logs/{len(r_a_last['failed'])} failed")
print(f"retry82: logs={r82['total_logs']} hits={len(r82['hits'])} failed={len(r82['failed'])}")
print(f"newdep: checked={nd['checked']} logs={nd['total_logs']} hits={len(nd['hits'])} failed={len(nd['failed'])}; "
      f"newdep-retry: logs={nd_r['total_logs']} hits={len(nd_r['hits'])} failed={len(nd_r['failed'])}")
print(f"deployments run83: {len(dep)} created addresses")

cur_run = s.get("last_run", {}).get("run", 0)
last_run_83 = {
    "run": 83,
    "block_start": 132023418,
    "block_end": 132031246,
    "window_wib": "2026-11-06 21:21:35 - 22:17:05 WIB (tx times); run executed 22:05 - ~23:20 WIB; sent-pass in-window txs 164, 0 mint-pattern txs",
    "wallets_checked": "55/55 via Ankr module (tier-ab 54 + feed 6 = 55 unique; user wallets excluded, none in set); 0 failed.",
    "method_note": (
        "Sent pass Ankr ankr_getTransactionsByAddress via module (55/55, 0 failed; "
        "164 txs, 19 wallets active). Receipts via fast_rpc batch (6, ~4s pause) for 114 "
        "non-approve candidates: final 114 status 1, 0 status 0, 0 null, 0 mint-pattern txs. "
        "Paid: 23 tokens, max 3 wallets/token (9 at 3, 8 at 2, 6 at 1 - usual ...7777 churn); "
        "NO new machine-token rotation this run (run-82 tokens 0xd468/0xa6e6/0x887c all 0 wallets). "
        "AFeng 2 sent txs (call to 0x1de4... selector 0x4d819a2a, value 0, 21:47:24 WIB, receipt status 1, "
        "13 logs, NO zero-from Transfer - NOT a mint; + 1 approval to 0xf98f...); future1001.ai 0 txs; "
        "0x2325... 3 txs (2 aggregator 0x27772d13, incl. 0.1 BNB 21:49:06 WIB, + 1 approval); "
        "0x8e96... 0 txs; 0x5b2f... 0 txs. "
        "14 contract deployments by 11 tracked wallets at blocks 132024595-132024607 (values 0.025-0.136 BNB funding each, "
        "all status 1; deployers incl. 0x3154.../0x3a39.../0x97bd... x2 each); 14 created addresses in run83-deployments.json; "
        "topic-filtered zero-from->tracked check over all 14 for the run-83 window: 0 hits (4 timed out first pass, all 4 recovered on retry, 0 hits). "
        f"Inbound leg per 2026-11-03 12:02 amendment: Ankr getLogs address-filtered per contract, "
        f"1061 unique contracts, {n_logs} logs summed, "
        f"{n_hits} hit(s), {n_failed} failed, run as a (0-400, {ia['total_logs']} logs, {len(ia['hits'])} hits, "
        f"{len(ia['failed'])} failed, {len(ia['truncated'])} truncated) "
        f"+ b1 (400-600, {ib1['total_logs']} logs, {len(ib1['hits'])} hits, {len(ib1['failed'])} failed, {len(ib1['truncated'])} truncated) "
        f"+ b2 (600-800, {ib2['total_logs']} logs, {len(ib2['hits'])} hits, {len(ib2['failed'])} failed, {len(ib2['truncated'])} truncated) "
        f"+ b3 (800-1061, {ib3['total_logs']} logs, {len(ib3['hits'])} hits, {len(ib3['failed'])} failed, {len(ib3['truncated'])} truncated), "
        "from ONE frozen list (run83-inbound-contracts.json = run81 list 1016 + 3 run-82 machine tokens + 42 run-82 deployment addresses). "
        f"{n_hits} hit(s) - NO inbound-only mints this run. "
        f"Retries recovered {n_failed - 2} of {n_failed} failed contracts ({retry_logs} retry logs, 0 hits): "
        "b1+b2 36 -> 33 recovered, 3 failed -> 2nd retry recovered all 3; b3 34 -> all 34 recovered; "
        "a 41 -> 39 recovered, 2 failed -> last single-attempt retry recovered both (0 logs each). "
        "Final still-failed: NONE for the main leg. "
        f"Truncated {len(trunc)} (0x10b3..., 0x1de4... AFeng sale, 0x3dca..., 0x55d3... USDT, 0x6288... AGC sale, 0x636f... AFeng tracker, "
        "0x63de... AGC, 0x7857...): all topic-filtered to 0 logs EXCEPT 0x3dca077eb687df96cc987da0035c8fad89ae716c, whose topic-filtered "
        "re-check timed out on every route (Ankr full-range x3, Ankr split halves x2, fast_rpc eth_getLogs) - its beyond-1000 logs are "
        "UNVERIFIED for the run-83 window (first 1000 unfiltered logs scanned, 0 hits); retry run 84, never reported as 0. "
        "Run-82 window retry (4 contracts failed run 82): 1006 logs, 0 hits, 0 failed - run-82 window inbound now FULLY CLOSED. "
        "INFRA NOTES: Ankr getLogs severely degraded tonight (bursts of 30s urlopen timeouts + 'Remote end closed connection'; "
        "a direct probe of USDT succeeded in 4.2s mid-outage, so the failures were burst/throttling-shaped, not a hard outage). "
        "fast_rpc eth_call ALSO degraded (all endpoints OSError/TimeoutError): pair token0/token1 for a6e6 (0x9fac...) and 887c (0xa9fa...) "
        "still UNREADABLE after retries via fast_rpc AND via Ankr eth_call (returns null) - unverified, not absence; retry run 84. "
        "No preview/mint/sign/login/purchase by this job."
    ),
}
if cur_run < 83:
    s["last_run"] = last_run_83
    print(f"last_run set to 83 (was {cur_run})")
else:
    print(f"last_run already {cur_run} (>=83) - NOT regressing; run-83 results merged below only")
    s["run83_last_run_record"] = last_run_83

s["paid_trend_run83"] = {
    "note": "Aggregate only, NOT a buy recommendation. No token reaches the signal threshold. SILENT RUN - no chat report (no new mints, no signal >20%, no auto-mint trigger, no reportable paid trend).",
    "no_rotation": "NO new machine-token rotation: max 3 wallets/token across 23 paid tokens (9 at 3, 8 at 2, 6 at 1). Run-82 tokens 0xd468.../0xa6e6.../0x887c... all 0 wallets (1st quiet run after debut); run-81 tokens 0x7f7a.../0x33f7... 0 wallets (2nd quiet run); run-80 token 0x489e... 0 wallets (3rd quiet run); all earlier machine tokens 0 wallets.",
    "other_paid_activity": [
        {"pattern": "23 paid tokens: 9 at 3 wallets (usual ...7777 set via trio 0x3803.../0xad94.../0xc7c5...), 8 at 2, 6 at 1", "wallets": "see run83-paid.json"},
        {"pattern": "Micro round-trip churn continues: 36 PCS buys (0xb6f9de95) + 36 PCS sells (0x791ac947), 50 approvals (0x095ea7b3), 24 aggregator txs (0x39ecce49); top active 0xc7c5... 37 txs, 0x3803... 36, 0xad94... 27, 0x3628.../0xa0c1... 15 each, 0x7488... 15", "wallets": "churn set"},
        {"pattern": "14 contract deployments by 11 tracked wallets, blocks 132024595-132024607, values 0.025-0.136 BNB each (funding), all status 1; 14 created addresses, none bought by the machine set yet - next rotation's tokens are plausibly among them, watch run 84", "wallets": ["0xc621946845", "0xaa49e7fec5", "0x3154f69492", "0x3a39aa05b1", "0xcb08c02c0a", "0x5b4beded36", "0x1cce4ec5a7", "0xc0c84518ce", "0x9b519f5d52", "0x64e893a4c5", "0x97bd895f81"], "created_addresses": "see run83-deployments.json"},
        {"pattern": "1 call to 0x1de4... sale contract, selector 0x4d819a2a, value 0, receipt status 1, 13 logs, NO zero-from Transfer - not a mint", "wallet": "0xbf004bff64 (AFeng)"},
        {"pattern": "2 aggregator calls (0x27772d13) incl. 0.1 BNB, + 1 approval", "wallet": "0x2325f17597"},
    ],
    "quiet": "future1001.ai 0 txs; 0x8e96... 0 txs; 0x5b2f... 0 txs; GrokBot 0xfcd0... absent (0 wallets) - 24th consecutive quiet run (59, 61-83) after the run-60 burst; CORLA-97af 0 wallets; CORLA 0x4a9c 0 wallets; all run-64/65 ASI contracts 0 wallets; all run-66/68/69/70/71/72/73/74/75/76/77/78/79/80/81/82 machine tokens 0 wallets.",
}

s["inbound_log_leg_run83"] = {
    "contracts": 1061,
    "total_logs": n_logs,
    "hits": n_hits,
    "failed": n_failed,
    "failed_contracts": failed_contracts,
    "retry_logs": retry_logs,
    "note": (
        f"Ankr getLogs address-filtered per contract, window 132023418-132031246, "
        f"a (0-400, {ia['total_logs']} logs, {len(ia['hits'])} hits, {len(ia['failed'])} failed, {len(ia['truncated'])} truncated) "
        f"+ b1 (400-600, {ib1['total_logs']} logs, {len(ib1['hits'])} hits, {len(ib1['failed'])} failed, {len(ib1['truncated'])} truncated) "
        f"+ b2 (600-800, {ib2['total_logs']} logs, {len(ib2['hits'])} hits, {len(ib2['failed'])} failed, {len(ib2['truncated'])} truncated) "
        f"+ b3 (800-1061, {ib3['total_logs']} logs, {len(ib3['hits'])} hits, {len(ib3['failed'])} failed, {len(ib3['truncated'])} truncated), "
        "from ONE frozen list (run83-inbound-contracts.json, 1061 contracts = run81 list + 3 run-82 machine tokens + 42 run-82 deployment addresses). "
        f"{n_hits} hits - 0 NEW inbound-only mints. "
        f"Retries: b1+b2 36 failed -> 33 recovered first pass, 3 failed -> recovered second pass; "
        f"b3 34 failed -> all recovered; a 41 failed -> 39 recovered, 2 failed -> both recovered on last single-attempt retry (0 logs each). "
        "Main leg final failed: NONE. "
        f"Truncated {len(trunc)}: all topic-filtered to 0 logs except 0x3dca... (topic-filtered re-check timed out on Ankr full-range, Ankr split halves, and fast_rpc eth_getLogs - beyond-1000 logs UNVERIFIED, retry run 84). "
        "Run-82 window retry (4 contracts): 1006 logs, 0 hits, 0 failed - run-82 window inbound FULLY CLOSED. "
        "New-deployment check (14 contracts created run 83): 0 hits; 4 timed out first pass, all 4 recovered on retry, 0 hits."
    )
}

s["next_run_note"] = (
    "Next run sent-tx window starts from block 132031247. RETRY run 84: (1) 0x3dca077eb687df96cc987da0035c8fad89ae716c truncated "
    "topic-filtered re-check (beyond-1000 logs UNVERIFIED for run-83 window; Ankr full-range x3, split halves x2, and fast_rpc eth_getLogs all timed out run 83) - "
    "do not report as 0. (2) Pair token0/token1 reads for 0xa6e6... pair 0x9fac925655fa4985ab4fe2fe9e0ca8ae323cc9da and 0x887c... pair "
    "0xa9fa6efb21c252b7d4ab81d19a07ee4ecf6d2c97 (fast_rpc 'all endpoints failed' + Ankr eth_call null run 83). "
    "(3) ADD the 14 run-83 deployment created addresses (run83-deployments.json) to the run-84 inbound contract list - they are the plausible next rotation. "
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
    "run 81 (TWO tokens 0x7f7a.../0x33f7... at 27 wallets each), run 82 (THREE tokens 0xd468.../0xa6e6.../0x887c... at 27 wallets each) "
    "auto-mint BLOCKED at guard (c) - do not re-signal or re-report the block unless a new mint/buy fact appears for those contracts "
    "(e.g. a genuine free-mint path). Per the 2026-11-06 ~18:30 machine-token fast-path amendment, routine machine-token rotations are "
    "recorded in state WITHOUT a chat report (no full verification per run); report only on anomaly (buy size far off norm, name/symbol appears, "
    "website, or free-mint path). Paid fact: run83 NO rotation (max 3 wallets/token, 23 tokens, usual ...7777 churn); run-82 tokens 0xd468.../0xa6e6.../0x887c... "
    "all 0 wallets (1st quiet run after debut); run-81 tokens 0 wallets (2nd quiet run); run-80 token 0 wallets (3rd quiet run); "
    "GrokBot 0xfcd0... absent (0 wallets) - 24th consecutive quiet run (59, 61-83) after the run-60 burst; CORLA-97af 0 wallets; "
    "CORLA 0x4a9c 0 wallets; all run-64/65 ASI contracts 0 wallets; all run-66/68/69/70/71/72/73/74/75/76/77/78/79/80/81/82 machine tokens 0 wallets. "
    "NEW run-83 watch item: 14 contracts deployed by 11 tracked wallets at blocks 132024595-132024607 (values 0.025-0.136 BNB, all status 1) - "
    "plausible next machine rotation; check run 84 whether the machine set buys any of them. "
    "AFeng 2 sent txs this run (0x1de4... call value 0, no mint; + approval); future1001.ai 0 txs; 0x2325... 3 txs; 0x8e96... 0 txs; 0x5b2f... 0 txs. "
    "OVERLAP NOTE: run 83 finished ~23:20 WIB, after run 84's 23:05 WIB start - if run 84's sent pass began before this update, it used "
    "FROM_BLOCK 132023418 (state still showed run 82) and re-scanned run 83's window; dedupe by tx hash applies, no mint findings to double-report. "
    "Same-owner factory groups now also include 0x293f and 0x1103 (proven 2026-11-06 ~01:14 WIB, AGENTS.md) alongside the groups listed in the body."
)

json.dump(s, open(P, "w"), indent=1)
print("state updated, machine_tokens total:", len(s.get("machine_tokens", [])))
print("last_run now:", s["last_run"]["run"], "block_end:", s["last_run"]["block_end"])
