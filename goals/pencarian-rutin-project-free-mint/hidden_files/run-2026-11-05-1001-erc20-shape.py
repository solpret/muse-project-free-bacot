import json, urllib.request, pathlib
base=pathlib.Path.home()/"workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
d=json.load(open(base/"onchain-scan-2026-11-05-0931.json"))
checked=json.load(open(base/"track-c-scan-checked.json"))
ck=set(k.lower() for k in (checked.keys() if isinstance(checked,dict) else checked))
erc=[e for e in d.get("erc20_mint_contracts_list",[]) if isinstance(e,dict) and e.get("mint_count",0)>=10]
erc.sort(key=lambda e: e.get("mint_count",0), reverse=True)
todo=[e for e in erc if e["address"].lower() not in ck][:20]
print("todo:", len(todo), "of", len(erc), "mint>=10")
FREE=["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted"]
res={}
for e in todo:
    a=e["address"]; out={"mint_count":e.get("mint_count")}
    for attempt in range(3):
        try:
            req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi",headers={"Accept":"application/json"})
            with urllib.request.urlopen(req,timeout=30) as r: dd=json.load(r)
            abi=dd.get("abi") or []
            names=[x.get("name","") for x in abi if isinstance(x,dict)]
            out["abi_funcs"]=len(names)
            out["mint"]=any(n.startswith("mint") for n in names)
            out["quote_cost"]=any("quote" in n.lower() or "cost" in n.lower() for n in names)
            out["free_views"]=[n for n in names if any(f.lower() in n.lower() for f in FREE)]
            out["gate"]=any("agent" in n.lower() or "registry" in n.lower() for n in names)
            out["is_token"]=all(n in names for n in ["name","symbol","decimals","totalSupply"])
            out["mintFree_noarg"]=any(n in ("mintFree","freeMint","claimFree") for n in names)
            out["s1_full"]=bool(out["mint"] and out["quote_cost"] and out["free_views"] and out["gate"])
            out["s2_full"]=bool(out["is_token"] and out["mintFree_noarg"] and out["free_views"] and out["gate"])
            break
        except Exception as ex:
            out["error"]=str(ex)[:100]
    res[a]=out
    print(a, json.dumps(out), flush=True)
json.dump(res,open(base/"run-2026-11-05-1001-erc20-shape.json","w"),indent=1)
