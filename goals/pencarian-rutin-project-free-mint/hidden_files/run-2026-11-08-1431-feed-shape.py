import json, urllib.request
REG="60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE_VIEWS=["freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeSharesRemaining","freeMinted","freeMint","freeSupply","free"]
def fetch(addr):
    url=f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    req=urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r: return json.load(r)
    except Exception as e: return {"_error": str(e)}
out={}
for addr in ["0x03D04613c0ad5a0F041AB12c1Ba64e374E20BbCa","0xEB71a7cbF97e091beBE2175C48E350D1993a04c9","0xF724aceFcdaC769ca000323DB8e34cA526dD3ECb","0x633c72cD79cefE5f2130bad6C6Ebe7C42b9f3Bae","0xF7cE63f2093F54d1A920d839A48eE4d29370839b"]:
    d=fetch(addr)
    abi=d.get("abi") or (d.get("stdJson",{}).get("output",{}).get("abi") if isinstance(d.get("stdJson"),dict) else None)
    if d.get("_error"): out[addr]={"error":d["_error"]}; print(addr,"ERROR",d["_error"],flush=True); continue
    fns=[]
    if isinstance(abi,list):
        for e in abi:
            if e.get("type")=="function": fns.append(e.get("name",""))
    src=json.dumps(d).lower()
    has_mint=any(n in fns for n in ["mint","mintFree","freeMint","mintAgent","claimFree"])
    has_quote=any(n in fns for n in ["quote","cost","price","priceForSerial","mintQuote","getQuote"])
    freeviews=[n for n in fns if any(fv.lower() in n.lower() for fv in FREE_VIEWS)]
    registry=REG in src
    is_token = all(n in fns for n in ["name","symbol","decimals","totalSupply"])
    noarg_free = any(n in fns for n in ["mintFree"]) 
    s1 = has_mint and has_quote and bool(freeviews) and registry
    s2 = is_token and noarg_free and bool(freeviews) and registry
    nft = has_mint and bool(freeviews) and registry
    out[addr]={"fns":fns,"has_mint":has_mint,"has_quote":has_quote,"free_views":freeviews,"registry_bytes":registry,"is_token":is_token,"S1":s1,"S2":s2,"NFT_shape":nft}
    print(addr, "fns=",len(fns), "mint=",has_mint,"quote=",has_quote,"freeviews=",freeviews,"registry=",registry,"token=",is_token,"S1=",s1,"S2=",s2,"NFT=",nft, flush=True)
    print("   fn sample:", fns[:30], flush=True)
json.dump(out, open("run-2026-11-08-1431-feed-shape.json","w"), indent=1)
