#!/usr/bin/env python3
"""Track-C 5c for backfill run 134710240-134716239 (2026-11-20 ~23:16 WIB cron).
Sourcify ABI shape-check, max 20 NEW (mint_count>=10, desc), skip already-checked.
Records checked entries in track-c-scan-checked.json. Read-only on-chain (no calls
here; on-chain verification only if a shape passes).
"""
import json, subprocess, time

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
OUT = f"{BASE}/backfill-trackc-134710240-134716239.json"
CHECKED = f"{BASE}/track-c-scan-checked.json"

def sourcify(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    for _ in range(2):
        try:
            p = subprocess.run(["curl", "-s", "-m", "25", url],
                               capture_output=True, text=True, timeout=35)
            d = json.loads(p.stdout)
            if isinstance(d, dict) and isinstance(d.get("abi"), list):
                return d["abi"], None
            if isinstance(d, dict) and "message" in d:
                return None, str(d.get("message"))[:80]
            return None, "no-abi-field"
        except Exception as e:
            err = f"{type(e).__name__}: {str(e)[:80]}"
            time.sleep(3)
    return None, err

agg = {}
for f in ["backfill-134710240-134712239.json",
          "backfill-134712240-134714239.json",
          "backfill-134714240-134716239.json"]:
    d = json.load(open(f"{BASE}/{f}"))
    for e in d.get("erc20_mint_contracts_list", []):
        a = e["address"].lower()
        if a not in agg:
            agg[a] = dict(e)
        else:
            agg[a]["mint_count"] += e["mint_count"]

checked = json.load(open(CHECKED))
checked_set = {x.lower() for x in checked.get("checked", [])}
checked_set |= {k.lower() for k in checked.keys() if k.startswith("0x")}
cand = [(a, e) for a, e in agg.items() if e["mint_count"] >= 10]
cand.sort(key=lambda kv: -kv[1]["mint_count"])
new = [(a, e) for a, e in cand if a not in checked_set]
print(f"erc20 unique={len(agg)} mint>=10={len(cand)} new={len(new)} taking top 20", flush=True)
top = new[:20]

REG = {"agentRegistry", "AGENT_ID_REGISTRY", "agentIdRegistry", "AGENT_REGISTRY",
       "REGISTRY", "AgentGate", "agentGate"}
FREE = {"freeClaimed", "freeMinted", "freeSupply", "freeLeft", "FREE_SUPPLY",
        "FREE_SLOTS", "freeFor", "freeClaim", "freeMint"}
QUOTE = {"quote", "costOf", "bnbQuote", "cost", "getCost", "mintPrice", "price", "PRICE"}
MINT = {"mint", "mintFree", "freeMint", "claim", "claimFree", "mintShare", "buyShare"}

results = {}
for a, e in top:
    addr = e["address"]
    abi, err = sourcify(addr)
    if abi is None:
        note = f"Sourcify not_verified ({err})"
        results[addr] = {"mint_count": e["mint_count"], "verified": False,
                         "s1": False, "s2": False, "note": note}
        print(f"{addr} mint={e['mint_count']} {note}", flush=True)
    else:
        fns = {fn.get("name") for fn in abi
               if fn.get("type") == "function" and fn.get("name")}
        has_mint = bool(fns & MINT)
        has_quote = bool(fns & QUOTE)
        has_free = bool(fns & FREE)
        has_reg = bool(fns & REG)
        s1 = has_mint and has_quote and has_free and has_reg
        s2 = ({"name", "symbol", "decimals", "totalSupply"} <= fns
              and "mintFree" in fns
              and bool(fns & {"freeClaimed", "freeMinted"})
              and bool(fns & {"FREE_SLOTS", "FREE_SUPPLY"})
              and has_reg and "mintPaid" in fns and "PRICE" in fns)
        note = (f"S1={s1} S2={s2} (mint={has_mint} quote={has_quote} "
                f"free={has_free} reg={has_reg})")
        results[addr] = {"mint_count": e["mint_count"], "verified": True,
                         "s1": s1, "s2": s2, "note": note,
                         "functions": sorted(fns)}
        print(f"{addr} mint={e['mint_count']} {note}", flush=True)
    # record in checked file
    status = "checked-sale-shape" if results[addr].get("s1") or results[addr].get("s2") \
        else "checked-not-sale-shape"
    checked.setdefault("checked", [])
    if addr not in checked["checked"] and addr.lower() not in checked_set:
        checked["checked"].append(addr)
    checked[addr] = {"source": "backfill-134710240-134716239-5c",
                     "status": status,
                     "mint_count": e["mint_count"],
                     "note": results[addr]["note"]}
    json.dump(checked, open(CHECKED, "w"), indent=1)
    json.dump(results, open(OUT, "w"), indent=1)

hits = [a for a, r in results.items() if r.get("s1") or r.get("s2")]
print(f"DONE checked={len(results)} sale-shape hits={len(hits)} {hits}", flush=True)
