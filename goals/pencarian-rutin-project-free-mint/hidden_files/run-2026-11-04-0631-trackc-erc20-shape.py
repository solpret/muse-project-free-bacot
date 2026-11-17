import urllib.request, json
FREE = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCount"]
REG = ["registry","agentRegistry","AGENT_ID","agentId","agentGate","AgentGate","isAgent","hasAgentId","requireAgentId"]
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
todo=json.load(open(BASE+'run-2026-11-04-0631-trackc-erc20-todo.json'))
out={}
for e in todo:
    a=e['address']
    try:
        req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi", headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as r: d=json.load(r)
        abi=d.get("stdJson",{}).get("abi") or d.get("abi") or []
        fns=[f.get("name") for f in abi if f.get("type")=="function"]
        has_mint=any(n in fns for n in ("mint","mintFree","mintPaid","freeMint","claimFree")) or any("mint" in (n or "").lower() for n in fns)
        fv=[n for n in fns if n in FREE]; rg=[n for n in fns if n in REG]
        has_quote="quote" in fns or "costFor" in fns
        is_token=("name" in fns and "symbol" in fns and "decimals" in fns and "totalSupply" in fns)
        out[a]={"verified":True,"has_mint":has_mint,"free_views":fv,"registry_refs":rg,"has_quote":has_quote,"is_token":is_token,
                "sale_S1":bool(has_mint and has_quote and fv and rg),"sale_S2":bool(is_token and ("mintFree" in fns) and fv and rg),
                "window_mint_count": e['mint_count']}
        print(a, "S1" if out[a]["sale_S1"] else "", "S2" if out[a]["sale_S2"] else "-", "mint" if has_mint else "nomint", fv, rg, "token" if is_token else "")
    except Exception as ex:
        out[a]={"verified":False,"error":f"{type(ex).__name__}: {str(ex)[:120]}","window_mint_count": e['mint_count']}
        print(a, "UNVERIFIED", out[a]["error"])
json.dump(out, open(BASE+'run-2026-11-04-0631-trackc-erc20-shape.json','w'), indent=1)
checked=json.load(open(BASE+'track-c-scan-checked.json'))
for a, r in out.items():
    if r.get("verified"):
        checked["checked"][a] = {"source": "run-2026-11-04-0631-5c", "result": "sale-shape-pass" if (r["sale_S1"] or r["sale_S2"]) else "checked-not-sale-shape"}
    else:
        print("NOT marked checked (transient fetch failure):", a)
json.dump(checked, open(BASE+'track-c-scan-checked.json','w'), indent=1)
print("checked total now:", len(checked["checked"]))
