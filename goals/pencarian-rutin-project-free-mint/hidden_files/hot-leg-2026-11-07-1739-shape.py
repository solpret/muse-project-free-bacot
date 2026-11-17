#!/usr/bin/env python3
"""Hot-leg 1739: shape-check S1/S2 for the 18 new Sourcify-feed contracts. Read-only except own run file."""
import json, time, urllib.request, urllib.error
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REGISTRY="60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE_VIEWS=["freesharesremaining","freeclaimed","freefor","freeleft","freeused","freeavailable","freesharepoolexhausted","freesharesclaimed","freeminted","free_slots","free_supply","freeslots","freesupply"]
QUOTE_WORDS=["quote","cost","price","getprice","mintprice","mintcost"]
feed=json.load(open(f"{BASE}/hot-leg-2026-11-07-1739-sourcify.json"))["results"]
seen=json.load(open(f"{BASE}/hot-leg-seen.json"))
seen_l={k.lower() for k in seen}
new=[it["address"] for it in feed if it["address"].lower() not in seen_l]
def fetch_abi(addr):
    url=f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        req=urllib.request.Request(url, headers={"User-Agent":"free-bacot-sourcify/1.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode()).get("abi"), None
    except urllib.error.HTTPError as e:
        return ("__not_verified__" if e.code==404 else None), f"HTTP{e.code}"
    except Exception as e:
        return None, f"{type(e).__name__}:{e}"
out={"checked":[],"hits":[]}
for addr in new:
    abi,err=fetch_abi(addr)
    row={"address":addr,"error":err}
    if abi=="__not_verified__" or not isinstance(abi,list):
        row["shape"]="not_verified" if abi=="__not_verified__" else "abi-unavailable"
        out["checked"].append(row); print(addr,row["shape"],flush=True); continue
    fns=[e for e in abi if isinstance(e,dict) and e.get("type")=="function"]
    names=[f.get("name","").lower() for f in fns]
    name_set=set(names); raw=json.dumps(abi).lower()
    mint=[n for n in names if n.startswith("mint") or n in ("claim","claimfree")]
    quote=[n for n in names if any(w in n for w in QUOTE_WORDS)]
    freev=[n for n in names if n in FREE_VIEWS]
    has_reg=REGISTRY in raw or "agentregistry" in name_set or "agentgate" in name_set
    is_token = all(x in name_set for x in ("name","symbol","decimals","totalsupply"))
    noarg_free=any(f.get("name","").lower() in ("mintfree","claimfree") and len(f.get("inputs",[]))==0 for f in fns)
    s1 = bool(mint) and bool(quote) and bool(freev) and has_reg
    s2 = is_token and noarg_free and bool(freev) and has_reg
    agent_mint = bool(mint) and bool(freev) and has_reg
    row.update({"fns":len(fns),"mint":mint[:4],"quote":quote[:4],"free_views":freev[:6],"registry":has_reg,"is_token":is_token,"noarg_free":noarg_free,"S1":s1,"S2":s2,"agent_mint_shape":agent_mint})
    out["checked"].append(row)
    tag="HIT S1" if s1 else ("HIT S2" if s2 else ("agent-mint" if agent_mint else "no-shape"))
    print(addr,tag,"mint=",mint[:3],"free=",freev[:4],"reg=",has_reg,flush=True)
    if s1 or s2 or agent_mint: out["hits"].append(row)
    time.sleep(0.3)
json.dump(out,open(f"{BASE}/hot-leg-2026-11-07-1739-sourcify-shape.json","w"),indent=1)
print("DONE checked=",len(out["checked"]),"hits=",len(out["hits"]),flush=True)
