import urllib.request, json
FREE = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCount"]
REG = ["registry","agentRegistry","AGENT_ID","agentId","agentGate","AgentGate","isAgent","hasAgentId","requireAgentId"]
todo=json.load(open('run-2026-11-02-0601-trackc-erc20-todo.json'))['todo_top20']
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
        out[a]={"verified":True,"functions":fns,"has_mint":has_mint,"free_views":fv,"registry_refs":rg,"has_quote":has_quote,"is_token":is_token,
                "sale_S1":bool(has_mint and has_quote and fv and rg),"sale_S2":bool(is_token and ("mintFree" in fns) and fv and rg),
                "window_mint_count": e['mint_count']}
        print(a, "S1" if out[a]["sale_S1"] else "", "S2" if out[a]["sale_S2"] else "-", "mint" if has_mint else "nomint", fv, rg)
    except Exception as ex:
        out[a]={"verified":False,"error":f"{type(ex).__name__}: {str(ex)[:120]}","window_mint_count": e['mint_count']}
        print(a, "UNVERIFIED", out[a]["error"])
json.dump(out, open('run-2026-11-02-0601-trackc-erc20-shape.json','w'), indent=1)
checked=json.load(open('track-c-scan-checked.json'))
for e in todo:
    if e['address'] not in checked['checked']: checked['checked'].append(e['address'])
json.dump(checked, open('track-c-scan-checked.json','w'), indent=1)
print("checked total now:", len(checked['checked']))
