#!/usr/bin/env python3
"""Run 0901 route 5c: Sourcify ABI shape-check, top 20 unchecked ERC-20 backlog. Read-only."""
import json, urllib.request, urllib.error
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
FREE=['freesharesremaining','freeclaimed','freefor','freeleft','freeused','freeavailable','freesharepoolexhausted','freesharesclaimed','freebyid','soldfree','freetotal']
scan=json.load(open(BASE+"onchain-scan-2026-11-03-0901.json"))
tc=json.load(open(BASE+"track-c-scan-checked.json"))
checked={k.lower() for k in tc.get("checked",{}).keys()}
filt=sorted([e for e in scan["erc20_mint_contracts_list"] if e.get("mint_count",0)>=10], key=lambda e:-e["mint_count"])
todo=[]
for e in filt:
    if e["address"].lower() not in checked:
        todo.append(e)
    if len(todo)>=20: break
out=[]
for e in todo:
    a=e["address"]
    try:
        req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi", headers={"User-Agent":"Mozilla/5.0"})
        d=json.loads(urllib.request.urlopen(req, timeout=20).read())
        abi=d.get("abi") or []
        fns=[f.get("name","") for f in abi if f.get("type")=="function"]
        low=[f.lower() for f in fns]
        has_mint=any("mint" in f for f in low)
        has_quote=any("quote" in f or f=="costfor" or f.startswith("cost") for f in low)
        has_free=any(f in FREE for f in low)
        has_reg=any("agent" in f or "registry" in f for f in low)
        has_token=any(f in ("name","symbol","decimals","totalsupply") for f in low)
        has_nofree=any(f in ("mintfree",) for f in low)
        s1=has_mint and has_quote and has_free and has_reg
        s2=has_token and has_nofree and has_free and has_reg
        out.append({"address":a,"mint_count":e["mint_count"],"functions":fns,"S1":s1,"S2":s2,"has_mint":has_mint,"has_quote":has_quote,"free_views":has_free,"agent_ref":has_reg,"is_token":has_token})
        print(a, e["mint_count"], "S1" if s1 else "-", "S2" if s2 else "-", flush=True)
    except urllib.error.HTTPError as ex:
        out.append({"address":a,"mint_count":e["mint_count"],"error":f"http_{ex.code}"}); print(a, e["mint_count"], "UNVERIFIED http", ex.code, flush=True)
    except Exception as ex:
        out.append({"address":a,"mint_count":e["mint_count"],"error":str(ex)[:100]}); print(a, e["mint_count"], "ERR", str(ex)[:100], flush=True)
json.dump(out, open(BASE+"run-2026-11-03-0901-trackc-5c.json","w"), indent=1)
print("checked_total_before", len(checked), "todo", len(todo), "passes", [o["address"] for o in out if o.get("S1") or o.get("S2")])
