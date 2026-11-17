import json, urllib.request, time
ADDRS = ["0x31CeA5F65519C36437D2A14E37aBD00b76133CdF","0x942c19A87a77b062D94C452ED8FaC6162aff45aD","0x5AD10026B4233aC004043DBB9291CFad19b1B3C3","0x45a74ce70689C157113d875c2A94C21a58a27654","0x3ef2A97Abf2E43182eACAe323B82d2CAC2132C6A","0xaa890A3B658eCFa56f0d0486665F0D4e77f3Fa0F","0x4d37eD4381Ed9A0577C634FC55e95Db44BbBc9cA"]
REG = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeMint","canFreeMint","claimedFree","freeSupply","free_slots","FREE_SLOTS","FREE_SUPPLY","FREE_AMOUNT"]
def get(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=timeout).read()
out=[]
for a in ADDRS:
    try:
        raw = get(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi")
        d = json.loads(raw)
        abi = d.get("abi") or d.get("stdJson",{}).get("abi") or []
        fns = [f.get("name") for f in abi if f.get("type")=="function"]
        src = json.dumps(d).lower()
        has_mint = any(n and ("mint" in n.lower()) for n in fns)
        has_quote = any(n and ("quote" in n.lower() or n.lower() in ("costof","cost","price","getprice","getcost")) for n in fns)
        free_views = [n for n in fns if any(fv.lower()==n.lower() or fv.lower() in n.lower() for fv in FREE_VIEWS)]
        has_registry = REG in src or "agentregistry" in src or "agentgate" in src
        is_token = all(any(n==x for n in fns) for x in ("name","symbol","decimals","totalSupply"))
        noarg_free = any(n and n.lower() in ("mintfree","freemint","claimfree") for n in fns)
        s1 = has_mint and has_quote and bool(free_views) and has_registry
        s2 = is_token and noarg_free and bool(free_views) and has_registry
        out.append({"address":a,"verified":True,"functions":len(fns),"name_symbol":None,
                    "mint_funcs":[n for n in fns if n and 'mint' in n.lower()][:8],
                    "free_views":free_views,"has_quote":has_quote,"has_registry_ref":has_registry,
                    "is_token":is_token,"noarg_free_mint":noarg_free,
                    "S1":s1,"S2":s2,"verdict":"SALE-SHAPED" if (s1 or s2) else ("agent-shaped-no-sale" if has_registry else "not-agent-shaped")})
    except Exception as e:
        out.append({"address":a,"verified":False,"error":str(e)[:200],"S1":False,"S2":False,"verdict":"abi-fetch-failed"})
    time.sleep(0.5)
json.dump(out, open("run-2026-11-05-1901-feed-shape.json","w"), indent=1)
for o in out:
    print(o["address"], o["verdict"], "S1",o.get("S1"),"S2",o.get("S2"),"mint:",o.get("mint_funcs"),"free:",o.get("free_views"),"reg:",o.get("has_registry_ref"),"token:",o.get("is_token"))
