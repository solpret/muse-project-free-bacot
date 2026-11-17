#!/usr/bin/env python3
"""Track-C 5c shape-check for backfill chunk 132051227-132053666 (read-only + state write)."""
import json, subprocess, sys

CHUNKS = ["backfill-132051227-132053226.json", "backfill-132053227-132053666.json"]
CHECKED = "track-c-scan-checked.json"
RUN_TAG = "backfill-132051227-132053666-5c"

def sourcify_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        p = subprocess.run(["curl", "-s", "-m", "20", "-A", "Mozilla/5.0", url],
                           capture_output=True, text=True, timeout=30)
        d = json.loads(p.stdout)
        abi = d.get("abi")
        if isinstance(abi, list):
            return ("verified", abi)
        return ("no-abi", None)
    except Exception as e:
        return (f"error:{type(e).__name__}", None)

def fn_names(abi):
    return [it.get("name", "") for it in abi if it.get("type") == "function"]

def classify(names):
    low = [n.lower() for n in names]
    has = lambda *subs: any(all(s in n for s in subs) for n in low)
    has_any = lambda *subs: any(any(s in n for s in subs) for n in low)
    # S1: mint + quote/cost + free-share view + registry/AgentGate
    s1 = (has("mint") and (has("quote") or has("cost"))
          and has_any("free") and (has("agentregistry") or has("agentgate") or has("registry")))
    # S2: token fns + mintFree + free views + FREE_SLOTS/FREE_SUPPLY + agentRegistry + mintPaid + PRICE
    s2 = (has("name") and has("symbol") and has("decimals") and has("totalsupply")
          and has("mintfree") and has_any("freeclaimed", "freeminted")
          and (has("free_slots") or has("free_supply"))
          and has("agentregistry") and has("mintpaid"))
    return s1, s2

def main():
    merged = {}
    for fn in CHUNKS:
        chunk = json.load(open(fn))
        for c in chunk["erc20_mint_contracts_list"]:
            a = c["address"]
            if a in merged:
                merged[a]["mint_count"] += c.get("mint_count", 0)
                merged[a]["distinct_minters"] = max(merged[a].get("distinct_minters",0), c.get("distinct_minters",0))
                merged[a]["last_block"] = max(merged[a].get("last_block",0), c.get("last_block",0))
            else:
                merged[a] = dict(c)
    lst = list(merged.values())
    checked = json.load(open(CHECKED))
    checked_lower = {k.lower() for k in checked.keys()}
    cands = sorted([c for c in lst if c.get("mint_count", 0) >= 10],
                   key=lambda c: -c.get("mint_count", 0))
    print(f"erc20 mint_count>=10: {len(cands)}")
    todo = [c for c in cands if c["address"].lower() not in checked_lower][:20]
    skipped = len(cands) - len([c for c in cands if c["address"].lower() not in checked_lower])
    print(f"already checked (skipped): {skipped}; to shape-check this run: {len(todo)}")
    results = []
    for c in todo:
        addr = c["address"]
        status, abi = sourcify_abi(addr)
        if abi is None:
            s1 = s2 = False
            note = f"sourcify={status}"
        else:
            names = fn_names(abi)
            s1, s2 = classify(names)
            note = f"sourcify=verified fns={len(names)}"
        rec = {"source": RUN_TAG, "run": "2026-11-07-0101", "mint_count": c["mint_count"],
               "S1": s1, "S2": s2, "sourcify": status, "note": note}
        checked[addr] = rec
        results.append((addr, c["mint_count"], s1, s2, status))
        print(f"  {addr} mints={c['mint_count']} S1={s1} S2={s2} {status}")
    # backup + atomic write
    import shutil, os
    shutil.copy(CHECKED, CHECKED + ".bak-" + RUN_TAG)
    tmp = CHECKED + ".tmp-5c"
    with open(tmp, "w") as f:
        json.dump(checked, f, indent=1)
    os.replace(tmp, CHECKED)
    hits = [r for r in results if r[2] or r[3]]
    print(f"shape-check done: {len(results)} checked, S1/S2 hits: {len(hits)}")
    for h in hits:
        print("  HIT:", h)
    json.dump(results, open("trackc-5c-132051227-132053666-results.json", "w"), indent=1)

if __name__ == "__main__":
    main()
