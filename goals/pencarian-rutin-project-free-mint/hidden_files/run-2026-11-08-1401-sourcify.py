import json, urllib.request, sys
REG="60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE_VIEWS=["freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeSharesRemaining","freeMinted","freeMint","freeSupply","freeFor","free"]
def fetch(addr):
    url=f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    req=urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r)
    except Exception as e:
        return {"_error": str(e)}
out={}
for addr in ["0x511cBf82CBFCA04a0F7c391dE75eeC2DAc446097","0x009Fb09d9B3Ba29bdf8d9f9da96e177Da929a445","0x3335c02f9763f004932294E051087e4807b30dE7"]:
    d=fetch(addr)
    abi=d.get("abi") or (d.get("stdJson",{}).get("output",{}).get("abi") if isinstance(d.get("stdJson"),dict) else None)
    if d.get("_error"):
        out[addr]={"error":d["_error"]}; print(addr,"ERROR",d["_error"],flush=True); continue
    fns=[]
    if isinstance(abi,list):
        for e in abi:
            if e.get("type")=="function":
                fns.append(e.get("name",""))
    src=json.dumps(d).lower()
    has_mint=any(n in fns for n in ["mint","mintFree","freeMint","mintAgent","claimFree"])
    has_quote=any(n in fns for n in ["quote","cost","price","priceForSerial","mintQuote","getQuote"])
    freeviews=[n for n in fns if any(fv.lower() in n.lower() for fv in FREE_VIEWS)]
    registry=REG in src
    name=None
    try:
        name=d.get("stdJson",{}).get("output",{}).get("contracts",{})
    except Exception: pass
    out[addr]={"fns":fns,"has_mint":has_mint,"has_quote":has_quote,"free_views":freeviews,"registry_bytes":registry,"s1":has_mint and has_quote and bool(freeviews) and registry,"nft_shape":has_mint and bool(freeviews) and registry}
    print(addr, "fns=",len(fns), "mint=",has_mint,"quote=",has_quote,"freeviews=",freeviews,"registry=",registry, "S1=",out[addr]["s1"], "NFT=",out[addr]["nft_shape"], flush=True)
    print("   fn sample:", fns[:25], flush=True)
json.dump(out, open("run-2026-11-08-1401-sourcify.json","w"), indent=1)
