#!/usr/bin/env python3
"""Worker B run 1601: Sourcify shape-check for the 7 NEW contracts in the
1601 feed (verified 08:26:44-08:28:00 UTC), i.e. newer than hot-leg 1524's
feed (top 08:25:02Z). Read-only; writes only run-2026-11-06-1601-sourcify-shape.json.
Never writes hot-leg-seen.json / snapshot / any shared state."""
import json, urllib.request, urllib.error, time, subprocess
from concurrent.futures import ThreadPoolExecutor

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
FREE_SHARE_VIEWS = ["freesharesremaining", "freeclaimed", "freefor", "freeleft",
                    "freeused", "freeavailable", "freesharepoolexhausted",
                    "freesharesclaimed", "freeminted", "freeremaining",
                    "free_slots", "free_supply", "free_amount"]
QUOTE_FNS = ["quote", "quotefor", "quotemint", "quotemintfor", "cost", "costfor",
             "getcost", "price", "mintprice", "feefor"]
GATE_WORDS = ["agentid", "agentregistry", "agentgate", "hasagentid", "isagent"]

def classify(abi):
    funcs = [it.get("name", "") for it in abi if isinstance(abi, list)
             and isinstance(it, dict) and it.get("type") == "function"]
    mint_fns = [f for f in funcs if "mint" in f.lower()]
    quote_fns = [f for f in funcs if f.lower() in QUOTE_FNS or f.lower().startswith("quote") or f.lower().startswith("cost")]
    free_views = [f for f in funcs if f.lower() in FREE_SHARE_VIEWS]
    gate = [f for f in funcs if any(g in f.lower() for g in GATE_WORDS)]
    token_fns = [f for f in funcs if f.lower() in ("name", "symbol", "decimals", "totalsupply")]
    noarg_free = [f for f in funcs if f.lower() in ("mintfree", "mint", "claimfree")]
    s1 = bool(mint_fns) and bool(quote_fns) and bool(free_views) and bool(gate)
    s2 = len(token_fns) >= 3 and bool(noarg_free) and bool(free_views) and bool(gate)
    return {"functions": len(funcs), "mint_fns": mint_fns, "quote_fns": quote_fns,
            "free_views": free_views, "gate_fns": gate, "token_fns": token_fns,
            "S1": s1, "S2": s2}

def fast_abi(addr, deadline):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    for i in range(3):
        if time.time() > deadline:
            return ("error:deadline", None)
        try:
            out = subprocess.run(["curl","-sL","--max-time","10","-A","Mozilla/5.0",url],
                                 capture_output=True, text=True, timeout=15)
            if out.returncode == 0 and out.stdout.strip():
                data = json.loads(out.stdout)
                if "abi" in data:
                    return ("verified", data.get("abi"))
                return ("not_verified", None)
        except Exception:
            pass
        time.sleep(1)
    return ("error:retry-exhausted", None)

feed = json.load(open(f"{BASE}/run-2026-11-06-1601-sourcify-feed.json"))
results = feed.get("results", [])
seen = json.load(open(f"{BASE}/hot-leg-seen.json"))
seen_l = {k.lower() for k in seen}
vat = {it["address"].lower(): it.get("verifiedAt") for it in results}
new = [x["address"] for x in results if x["address"].lower() not in seen_l]
print("FEED", len(results), "NEW", len(new), new, flush=True)
dl = time.time() + 60
def check(a):
    st, abi = fast_abi(a, dl)
    r = {"address": a, "verifiedAt": vat.get(a.lower()), "sourcify": st}
    if abi is not None:
        r.update(classify(abi))
    else:
        r["S1"] = False; r["S2"] = False
    return r
with ThreadPoolExecutor(max_workers=6) as ex:
    shape_out = list(ex.map(check, new))
for r in shape_out:
    print(r["address"], r["sourcify"], "S1=", r.get("S1"), "S2=", r.get("S2"),
          "mint=", r.get("mint_fns"), "quote=", r.get("quote_fns"),
          "free=", r.get("free_views"), "agent=", r.get("gate_fns"),
          "token=", r.get("token_fns"), flush=True)
json.dump(shape_out, open(f"{BASE}/run-2026-11-06-1601-sourcify-shape.json", "w"), indent=1)
print("WROTE shape file, sale shapes:", sum(1 for r in shape_out if r.get("S1") or r.get("S2")))
