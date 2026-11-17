import json, subprocess, sys
REG="0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE_VIEWS=["freesharesremaining","freeclaimed","freefor","freeleft","freeused","freeavailable","freesharepoolexhausted","freesharesclaimed","freeminted","freeclaim","freemint","freemintleft","freemintedby"]
NEW=["0xb89a812dca4ca754c32619867a2ecf68fb683cf7","0xd71fd80211d82fa63debbab6bf40e18afad42beb","0xf27259e9e4df5381c3a1625bb8852df1ce6d511c","0x345020e31177ada99e31b2cbfdbf3c7ad972c7b4","0xe8ff7dc755b3f479af228cc47783a031149a4aed","0xc12e2d8d4476c99fd5ae4700c87746a996c991a2","0x74bda11e34eb02121104ff38471d91fe1c37f81a","0x24d0baa58d0bb02c25bd599cd38e343ae79fe4ea","0x1fa1eed462b58e0bb97e4119421f101b97efa0b9","0x0280c8c5e0e0611ca3d5cfd48d34b8abb66156ea","0xe84ae66b578c9660efb96e5cda566e845d71dd52","0x50a5d10e4aa7205ef455f2c48cb70089e9064292","0x07a554cbdf58bcdec3416cb7d4a1732e9f352316","0xfc29876fa700bacb0f925e258f61d0387f73cbb8"]
def fetch_abi(a):
    for attempt in range(2):
        try:
            r=subprocess.run(["curl","-s","-m","30",f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi"],capture_output=True,text=True,timeout=40)
            d=json.loads(r.stdout)
            abi=d.get("stdJson",{}).get("output",{}).get("abi") or d.get("abi")
            if abi: return d.get("match"), abi
            return d.get("match"), None
        except Exception as e:
            print(a,"fetch err",e,flush=True)
    return None, None
out={}
for a in NEW:
    match, abi = fetch_abi(a)
    if not abi:
        print(a,"NO-ABI match=",match,flush=True); out[a]={"match":match,"shape":"no-abi"}; continue
    fns=[x for x in abi if x.get("type")=="function"]
    names=[x.get("name","") for x in fns]
    low=[n.lower() for n in names]
    has_mint=any(n.startswith("mint") or n in ("claim","claimfree","claimfreeshare","mintfree") for n in low)
    has_quote=any("quote" in n or "cost" in n or n.startswith("price") for n in low)
    free_views=[n for n in low if any(fv in n for fv in FREE_VIEWS)]
    src=json.dumps(abi).lower()
    reg = REG.lower() in src or "agentregistry" in low or "registry" in low or "agentgate" in src or "agentid" in low
    is_token = all(x in low for x in ("name","symbol","decimals","totalsupply"))
    s1 = has_mint and has_quote and bool(free_views) and reg
    s2 = is_token and any(n in low for n in ("mintfree","claimfree")) and bool(free_views) and reg
    agent_mint = has_mint and bool(free_views) and reg
    print(a, "match=",match,"fns=",len(names),"mint=",has_mint,"quote=",has_quote,"free=",free_views,"reg=",reg,"S1=",s1,"S2=",s2,"agentMint=",agent_mint,flush=True)
    out[a]={"match":match,"fns":len(names),"fn_names":sorted(set(names)),"mint":has_mint,"quote":has_quote,"free_views":free_views,"registry":reg,"S1":s1,"S2":s2,"agent_mint":agent_mint}
json.dump(out, open("run-2026-11-07-0831-feed-shape.json","w"), indent=1)
print("HITS:", [a for a,v in out.items() if v.get("S1") or v.get("S2") or v.get("agent_mint")])
