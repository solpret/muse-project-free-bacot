#!/usr/bin/env python3
"""Run 2026-11-09 04:01 WIB — route 5c: ERC-20 backlog shape-check from the
PARTIAL scan output (window broke at chunk 9/20; 128 ERC-20 mint contracts).
mint_count>=10, sorted desc, max 20, skip already-checked. Read-only vs snapshot.
"""
import json, time, subprocess
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-09-0401"
FREE = ["freeClaimed", "freeMinted", "freeLeft", "freeSupply", "freeFor", "freeUsed",
        "freeAvailable", "freeSharesRemaining", "freeSharePoolExhausted",
        "freeSharesClaimed", "freeOf", "freeCount", "freeRemaining"]
AGENT = ["agentRegistry", "AGENT_ID_REGISTRY", "AGENT_REGISTRY", "registry",
         "agentIds", "agentTokenIdOf", "agentId", "isAgent"]
scan = json.load(open(f"{BASE}/onchain-scan-{TS}.json"))
lst = scan.get("erc20_mint_contracts_list", [])
lst = [e for e in lst if e.get("mint_count", 0) >= 10]
lst.sort(key=lambda e: -e["mint_count"])
chk = json.load(open(f"{BASE}/track-c-scan-checked.json"))
checked_set = {a.lower() for a in chk.get("checked", [])}
checked_set |= {k.lower() for k in chk if isinstance(chk[k], dict)}
todo = [e for e in lst if e["address"].lower() not in checked_set][:20]
print(f"5c: {len(lst)} candidates mc>=10, {len(todo)} new to check (max 20), "
      f"{len(lst)-len(todo)} skipped/dropped as sampling limit", flush=True)

def sourcify_abi(addr):
    try:
        out = subprocess.run(["curl", "-sL", "--max-time", "20",
            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi",
            "-H", "User-Agent: Mozilla/5.0"], capture_output=True, text=True, timeout=25).stdout
        d = json.loads(out)
        abi = d.get("abi")
        if isinstance(abi, list) and abi:
            return {"verified": True, "fns": sorted({f.get("name") for f in abi
                    if isinstance(f, dict) and f.get("type") == "function" and f.get("name")})}
        return {"verified": False, "note": str(d)[:150]}
    except Exception as e:
        return {"verified": False, "error": f"{type(e).__name__}: {e}"}

out = {}
for e in todo:
    a = e["address"]
    s = sourcify_abi(a)
    fns = s.get("fns", [])
    shape = {"address": a, "mint_count": e["mint_count"], "verified": s.get("verified"),
             "free": [f for f in fns if any(x.lower() in f.lower() for x in FREE)],
             "mint": [f for f in fns if "mint" in f.lower() or "claim" in f.lower()],
             "quote": [f for f in fns if f.lower() in ("quote", "costof", "priceof", "price", "cost")],
             "agent": [f for f in fns if any(x.lower() in f.lower() for x in AGENT)],
             "token": [f for f in fns if f.lower() in ("name", "symbol", "decimals", "totalsupply")],
             "all_fns": fns}
    shape["S1"] = bool(shape["mint"] and shape["quote"] and shape["free"] and shape["agent"])
    shape["S2"] = bool(shape["token"] and len(shape["token"]) >= 4 and shape["mint"] and shape["free"] and shape["agent"])
    out[a] = shape
    print(a, "mc=", e["mint_count"], "verified:", s.get("verified"), "S1:", shape["S1"],
          "S2:", shape["S2"], "free:", shape["free"], "mint:", shape["mint"][:5],
          "quote:", shape["quote"], "agent:", shape["agent"], "err:", s.get("error", ""), flush=True)
    time.sleep(1)
json.dump(out, open(f"{BASE}/run-{TS}-5c.json", "w"), indent=1)
for a, v in out.items():
    chk[a] = {"checked_wib": "2026-11-09 04:01 run", "run": TS, "S1": v["S1"], "S2": v["S2"],
              "verdict": "checked-not-sale-shape" if not (v["S1"] or v["S2"]) else "SALE-SHAPE-HIT"}
json.dump(chk, open(f"{BASE}/track-c-scan-checked.json", "w"), indent=1)
print("5c DONE hits:", [a for a, v in out.items() if v["S1"] or v["S2"]], "checked total now:", len(chk), flush=True)
