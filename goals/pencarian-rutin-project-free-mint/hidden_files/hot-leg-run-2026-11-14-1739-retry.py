#!/usr/bin/env python3
"""Retry for hot-leg run 2026-11-14 17:39 WIB.
(1) Sourcify feed was feed-fetch-failed in the main run; a direct curl retry
    seconds later succeeded - shape-check the 2 contracts newer than the 1734
    run top (0xB13d...): 0x166F... (10:41:34Z) and 0xb2FA... (10:39:01Z).
(2) Leg-4 chunks @26/@52 failed on all RPC endpoints in the main run: 9 items
    read all-null (RaceAgents, Pengu, Zephyra, DragonAgents, BinanceAI-mint,
    AngelEye-77D9, NOTV, AbsurdAgentNFT, AgentBubble). Re-read them once with
    smaller chunks. Nulls are read failures, never state changes.
Writes ONLY hot-leg-run-2026-11-14-1739-retry.json + updates hot-leg-seen.json
with the 2 new feed contracts. Never writes main snapshot / main seen files.
"""
import importlib.util, json, time
from datetime import datetime, timezone, timedelta

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
WIB = timezone(timedelta(hours=7))
NOW_WIB = datetime.now(WIB).strftime("%Y-%m-%dT%H:%M+07:00")

spec = importlib.util.spec_from_file_location(
    "hl1739", f"{HF}/hot-leg-run-2026-11-14-1739.py")
hl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hl)

NEW_FEED = ["0x166F4Bb7040aF6A61e189e47Ac47e1A8463d0333",
            "0xb2FA2194254473336bCF1A4B1A83109DfcFb3b1E"]
RETRY_ITEMS = ["RaceAgents", "Pengu", "Zephyra", "DragonAgents",
               "BinanceAI-mint", "AngelEye-77D9", "NOTV", "AbsurdAgentNFT",
               "AgentBubble"]

def main():
    t0 = time.time()
    out = {"run": "free-mint-hot-leg 2026-11-14 17:39 WIB retry",
           "started_wib": NOW_WIB}
    seen = json.load(open(f"{HF}/hot-leg-seen.json"))

    # (1) shape-check the 2 new feed contracts
    sc = []
    for a in NEW_FEED:
        r = hl.shape_check(a)
        r["address"] = a
        sc.append(r)
        if a not in seen and a.lower() not in {k.lower() for k in seen}:
            seen[a] = {"first_seen_wib": NOW_WIB, "source": "sourcify-feed-retry",
                       "status": "checked" if r.get("status") == "checked" else r.get("status"),
                       "note": f"S1={r.get('S1')} S2={r.get('S2')} mint={r.get('mint')} quote={r.get('quote')} free={r.get('free')} agent={r.get('agent')}"}
    out["shape_check_retry"] = sc
    out["shape_hits_retry"] = [s["address"] for s in sc if s.get("S1") or s.get("S2")]

    # (2) re-read the 9 failed items, smaller chunks (13) to dodge rate limits
    calls, keys = [], []
    for name in RETRY_ITEMS:
        addr, views = hl.ITEMS[name]
        for label, sig, args in views:
            calls.append((addr, hl.build_data(sig, args)))
            keys.append((name, label))
    res = hl.rpc_batch(calls, chunk=13)
    results = {}
    for (name, label), r in zip(keys, res):
        results.setdefault(name, {})[label] = hl.decode(r)
    out["reread_retry"] = {"reads": {n: {"address": hl.ITEMS[n][0],
                                          "views": results.get(n, {})} for n in RETRY_ITEMS},
                           "reads_ok": sum(1 for n in RETRY_ITEMS if any(v is not None for v in results.get(n, {}).values())),
                           "reads_total": len(RETRY_ITEMS),
                           "block": hl.rpc_block()}

    # compare vs 1734 run for real changes
    prev = json.load(open(f"{HF}/hot-leg-run-2026-11-14-1734.json"))["reread"]["reads"]
    changes = {}
    for n in RETRY_ITEMS:
        va = (prev.get(n) or {}).get("views") or {}
        vb = results.get(n) or {}
        diffs = {k: (va.get(k), vb.get(k)) for k in set(va) | set(vb) if va.get(k) != vb.get(k)}
        if diffs:
            changes[n] = diffs
    out["changes_vs_1734"] = changes

    out["elapsed_s"] = round(time.time() - t0, 1)
    json.dump(out, open(f"{HF}/hot-leg-run-2026-11-14-1739-retry.json", "w"), indent=1)
    json.dump(seen, open(f"{HF}/hot-leg-seen.json", "w"))
    print(json.dumps(out, indent=1))

if __name__ == "__main__":
    main()
