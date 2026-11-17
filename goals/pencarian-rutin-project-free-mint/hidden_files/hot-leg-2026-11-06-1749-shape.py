import json, urllib.request, time
REG="0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
addrs=[
 ("0xF7bC6f672150186cE20ff4C8D90257d33c489E7c","2026-11-06T10:49:01Z"),
 ("0x1f2b113f0eCe7aB42E6DF2B0C158f736129e09b4","2026-11-06T10:48:37Z"),
 ("0x95A1371A1B457daa4d99da3Ce0A033379E164d8F","2026-11-06T10:47:55Z"),
]
FREE=["freesharesremaining","freeclaimed","freefor","freeleft","freeused","freeavailable","freesharepoolexhausted","freesharesclaimed","freeminted","freemint","free_slots","free_supply","freeamount"]
def fetch(url, timeout=25):
    req=urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()
out={}
for a,vat in addrs:
    status=None; abi=None
    for t in range(3):
        try:
            d=json.loads(fetch(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi"))
            abi=d.get("abi") or []
            status="ok"
            break
        except Exception as e:
            status=str(e); time.sleep(2)
    if abi is None:
        out[a]={"verifiedAt":vat,"error":status}
        print(a,"ERROR",status); continue
    fns=[f.get("name","") for f in abi if f.get("type")=="function"]
    src=json.dumps(abi).lower()
    mint=[f for f in fns if "mint" in f.lower()]
    quote=[f for f in fns if "quote" in f.lower() or "cost" in f.lower() or f.lower() in ("price","getprice")]
    free=[f for f in fns if any(k in f.lower() for k in FREE)]
    agent=[f for f in fns if "agent" in f.lower() or "registry" in f.lower()]
    token=[f for f in fns if f.lower() in ("name","symbol","decimals","totalsupply")]
    s1 = bool(mint) and bool(quote) and bool(free) and (REG in src or bool(agent))
    s2 = len(token)==4 and any("mintfree" in f.lower() for f in fns) and bool(free) and (REG in src or bool(agent))
    out[a]={"verifiedAt":vat,"S1":s1,"S2":s2,"mint":mint,"quote":quote,"free":free,"agent":agent,"token":token,"n_fns":len(fns)}
    print(a,"S1",s1,"S2",s2,"mint",mint,"quote",quote,"free",free,"agent",agent,"token",token)
json.dump(out, open("hot-leg-2026-11-06-1749-shape.json","w"), indent=1)
