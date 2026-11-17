#!/usr/bin/env python3
"""Backfill run 2026-11-07 00:46 WIB route 5c ERC-20 shape-check. Read-only except checked-file update."""
import json, subprocess, sys
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
FREE_VIEWS = {"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeShares","freeCount"}
def sourcify_abi(addr):
    for attempt in range(2):
        try:
            r = subprocess.run(["curl","-sS","--max-time","30","-H","User-Agent: free-mint-search/1.0",
                                f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],
                               capture_output=True, text=True)
            if r.returncode == 0 and r.stdout.strip():
                return json.loads(r.stdout)
        except Exception as e:
            if attempt == 1: raise
    raise RuntimeError("curl failed")
merged = {}
for f in ["backfill-132049047-132051046.json","backfill-132051047-132051226.json"]:
    d = json.load(open(BASE + f))
    for e in d.get("erc20_mint_contracts_list", []):
        a = e["address"].lower()
        if a in merged: merged[a]["mint_count"] += e["mint_count"]
        else: merged[a] = dict(e)
chk = json.load(open(BASE + "track-c-scan-checked.json"))
checked = set(a.lower() for a in chk.get("checked", []))
snap = json.load(open(BASE + "onchain-snapshot.json"))
known = set()
for v in snap.get("track_c", {}).values():
    if isinstance(v, dict):
        for k in ("sale","token","address"):
            if v.get(k): known.add(v[k].lower())
    elif isinstance(v, str):
        known.add(v.lower())
cand = [x for x in merged.values() if x["mint_count"] >= 10 and x["address"].lower() not in checked and x["address"].lower() not in known]
cand.sort(key=lambda x: -x["mint_count"])
todo = cand[:20]
print("candidates>=10:", len(cand), "todo:", len(todo), "dropped as sampling limit:", len(cand)-len(todo))
out = []
for x in todo:
    A = x["address"]
    entry = {"address": A, "mint_count": x["mint_count"], "distinct_minters": x["distinct_minters"]}
    try:
        d = sourcify_abi(A)
        fns = [e["name"] for e in d.get("abi", []) if e.get("type") == "function"]
        entry["sourcify"] = "verified" if d.get("abi") else "unverified"; entry["functions"] = fns
        has_mint = any(f in fns for f in ("mint","mintFree","claimFree"))
        has_quote = any(f in fns for f in ("quote","costFor","quoteFor"))
        free = [f for f in fns if f in FREE_VIEWS]
        agent = any(("registry" in f.lower() or "gate" in f.lower()) for f in fns)
        is_token = all(f in fns for f in ("name","symbol","decimals","totalSupply"))
        entry.update({"has_mint": has_mint, "has_quote": has_quote, "free_views": free, "agent_ref_name": agent, "is_token": is_token})
        entry["S1"] = bool(has_mint and has_quote and free and agent)
        entry["S2"] = bool(is_token and ("mintFree" in fns) and free and agent)
        entry["S2_variant"] = bool(is_token and ("claimFree" in fns) and free and agent)
    except Exception as e:
        entry["sourcify"] = "unverified-or-error"; entry["error"] = f"{type(e).__name__}: {str(e)[:120]}"
        entry["S1"] = False; entry["S2"] = False
    out.append(entry)
    print(json.dumps(entry)[:700], flush=True)
json.dump(out, open(BASE + "run-2026-11-07-0046-trackc-erc20.json","w"), indent=1)
chk["checked"] = sorted(checked | {x["address"].lower() for x in todo})
for e in out:
    chk[e["address"]] = {"source": "backfill-2026-11-07-0046-5c",
                         "status": "sale-shape" if (e.get("S1") or e.get("S2") or e.get("S2_variant")) else "checked-not-sale-shape",
                         "note": f"S1={e.get('S1')} S2={e.get('S2')} mint={e.get('has_mint')} quote={e.get('has_quote')} free={e.get('free_views')} agent={e.get('agent_ref_name')} token={e.get('is_token')} sourcify={e.get('sourcify')}"}
json.dump(chk, open(BASE + "track-c-scan-checked.json","w"), indent=1)
print("checked total now:", len(chk["checked"]))
print("SALE-SHAPE PASSES:", [e["address"] for e in out if e.get("S1") or e.get("S2") or e.get("S2_variant")])
