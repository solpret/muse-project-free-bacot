#!/usr/bin/env python3
"""Retry 11 abi-unavailable Sourcify ABIs via curl (1901 precedent)."""
import json, subprocess
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REGISTRY = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE_VIEWS = ["freesharesremaining", "freeclaimed", "freefor", "freeleft",
              "freeused", "freeavailable", "freesharepoolexhausted",
              "freesharesclaimed", "isfreemintavailable", "freeminted",
              "free_slots", "free_supply", "freeslots", "freesupply"]
QUOTE_WORDS = ["quote", "cost", "price", "getprice", "mintprice", "mintcost"]
out = json.load(open(f"{BASE}/run-2026-11-07-1931-sourcify.json"))
def shape(abi):
    fns = [e for e in abi if isinstance(e, dict) and e.get("type") == "function"]
    names = [f.get("name", "").lower() for f in fns]
    name_set = set(names)
    raw = json.dumps(abi).lower()
    mint = [n for n in names if n.startswith("mint") or n in ("claim", "claimfree")]
    quote = [n for n in names if any(w in n for w in QUOTE_WORDS)]
    freev = [n for n in names if n in FREE_VIEWS]
    has_reg = REGISTRY in raw or "agentregistry" in name_set or "agentgate" in name_set
    is_token = ({"name", "symbol", "decimals", "totalSupply"} <= name_set)
    noarg_free = any(f.get("name", "").lower() in ("mintfree", "claimfree")
                     and len(f.get("inputs", [])) == 0 for f in fns)
    return {"fns": len(fns), "mint": mint[:4], "quote": quote[:4],
            "free_views": freev[:6], "registry": has_reg,
            "is_token": is_token, "noarg_free": noarg_free,
            "S1": bool(mint) and bool(quote) and bool(freev) and has_reg,
            "S2": is_token and noarg_free and bool(freev) and has_reg,
            "agent_mint_shape": bool(mint) and bool(freev) and has_reg}
for row in out["checked"]:
    if row.get("shape") != "abi-unavailable":
        continue
    addr = row["address"]
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        p = subprocess.run(["curl", "-sS", "--max-time", "30", url],
                           capture_output=True, text=True, timeout=35)
        d = json.loads(p.stdout)
        abi = d.get("abi")
        if isinstance(abi, list):
            row.update(shape(abi)); row["shape"] = "retried-via-curl"; row["error"] = None
            tag = "HIT S1" if row["S1"] else ("HIT S2" if row["S2"] else ("agent-mint" if row["agent_mint_shape"] else "no-shape"))
            print(addr, tag, "mint=", row["mint"][:3], "free=", row["free_views"][:4], "reg=", row["registry"], flush=True)
            if row["S1"] or row["S2"] or row["agent_mint_shape"]:
                out["hits"].append(row)
        else:
            row["error"] = f"curl-no-abi:{str(d)[:120]}"
            print(addr, "curl-no-abi", flush=True)
    except Exception as e:
        row["error"] = f"curl-retry:{type(e).__name__}:{e}"
        print(addr, "curl-retry-fail", row["error"], flush=True)
json.dump(out, open(f"{BASE}/run-2026-11-07-1931-sourcify.json", "w"), indent=1)
print(f"RETRY DONE hits={len(out['hits'])}", flush=True)
