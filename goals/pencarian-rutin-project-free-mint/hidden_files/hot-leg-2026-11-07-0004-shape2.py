import json, subprocess
REG="0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
addrs=[
 "0x4C0B9F9cD42414025Aaff684306c8C525baa1132",
 "0xB987E4e5BC272F589069A2bE1B52FeBd1aF76521",
 "0xEC1b9C603FaF9a48194A748A590466FF3D1156Ea",
 "0x634bb120C3eA1ADDB0196318BbF841B0841d4CC6",
 "0xB9384D034694B1cD1B94B973c9230a863f136fEc",
 "0x1e9B437a84daB05b55ce3Cfe3A09c92Cdb8b871A",
 "0x423d25764e4d3d792c08e04c759ce3b0fcde8596",
 "0x43F046F5C49E54D42913743a8fd2D146CE494C4C",
 "0xfab9c88d25e111edd68a2cca3e0f650863a5bf25",
]
FREE=["freesharesremaining","freeclaimed","freefor","freeleft","freeused","freeavailable","freesharepoolexhausted","freesharesclaimed","freeminted","freemint","free_slots","free_supply","freeamount"]
out={}
for a in addrs:
    abi=None; err=None
    for t in range(3):
        try:
            r=subprocess.run(["curl","-s","--max-time","20","-A","Mozilla/5.0",f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi"],capture_output=True,text=True,timeout=30)
            d=json.loads(r.stdout)
            abi=d.get("abi") or []
            break
        except Exception as e:
            err=str(e)
    if abi is None:
        out[a]={"error":err}; print(a,"ERROR",err); continue
    fns=[f.get("name","") for f in abi if f.get("type")=="function"]
    src=json.dumps(abi).lower()
    mint=[f for f in fns if "mint" in f.lower()]
    quote=[f for f in fns if "quote" in f.lower() or "cost" in f.lower() or f.lower() in ("price","getprice")]
    free=[f for f in fns if any(k in f.lower() for k in FREE)]
    agent=[f for f in fns if "agent" in f.lower() or "registry" in f.lower()]
    token=[f for f in fns if f.lower() in ("name","symbol","decimals","totalsupply")]
    s1 = bool(mint) and bool(quote) and bool(free) and (REG.lower() in src or bool(agent))
    s2 = len(token)==4 and any("mintfree" in f.lower() for f in fns) and bool(free) and (REG.lower() in src or bool(agent))
    out[a]={"S1":s1,"S2":s2,"mint":mint,"quote":quote,"free":free,"agent":agent,"token":token,"n_fns":len(fns)}
    print(a,"S1",s1,"S2",s2,"mint",mint,"quote",quote,"free",free,"agent",agent,"token",token)
json.dump(out, open("hot-leg-2026-11-07-0004-shape2.json","w"), indent=1)
