import json, subprocess, sys
REG="0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE_VIEWS=["freesharesremaining","freeclaimed","freefor","freeleft","freeused","freeavailable","freesharepoolexhausted","freesharesclaimed","freeminted","freeclaim","freemint","freemintleft","freemintedby"]
NEW=['0x939fE42ab910eD576DbCD555b44639fCc66707aE', '0x9aAB6Ce57119731EAB16EAd492481DcD5E608256', '0x67A199E1e3d5Da1098762a2724ed11E7A16F06e7', '0x485E77296c55E122C53249A3F71A67871aB200C5', '0x84a9798b11c70a71905107e0657a19883355B12B', '0xa1bb41d70dE493d247DA331B46551cA8d99FaD98', '0x039D925C197f8DD5135322Ff0A898fAcFc667273', '0x2d9d5868aB91c1E4FE4A525F7cfe06Cb097FD040', '0x2DCC49cfAc68b4aCEe3779e9F2a0b4Eca6973339', '0xc361525Cb20BaF97c10a5c55dc7F6Cf05d83034f', '0x3Db869A40354f66203770cdF0E9a87dE0dE88729', '0xbA5CdE0ceEA8704B8944Deb51228Ca59A7BD9cF0', '0xEC266bDD979b19d8A2f1266EF0610B4791Dbd24B', '0x85F6bA1Af50f9083740Dc1F5Fab5de991b36C536', '0x3eA21CDCd4eBcCEA9d00d4BFF68fCF521f8aeD47', '0x452c9593cb3c438cF224AbCa1EdfEf30aa7e014f', '0xBb1A23763214b2fc3713489613a9bA3C099a1ce8', '0xCF91A0545EaBD94549A5aE7Dc48dD895da97F547', '0xE3A376D0985eF9b7d13E69De1a9179146e34fbef', '0xd576F638b5eF8906C13CE9Ca534113DdBd0a9038']
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
json.dump(out, open("run-2026-11-07-0901-feed-shape.json","w"), indent=1)
print("HITS:", [a for a,v in out.items() if v.get("S1") or v.get("S2") or v.get("agent_mint")])
