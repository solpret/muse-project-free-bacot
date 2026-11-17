import json, subprocess
REG="0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE_VIEWS=["freesharesremaining","freeclaimed","freefor","freeleft","freeused","freeavailable","freesharepoolexhausted","freesharesclaimed","freeminted","freeclaim","freemint","freemintleft","freemintedby"]
NEW=json.load(open("hot-leg-2026-11-07-1844-boltbook-new.json"))
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
    is_token=("name" in low and "symbol" in low and "decimals" in low and "totalsupply" in low)
    s1 = has_mint and has_quote and bool(free_views) and reg
    s2 = is_token and any(n in low for n in ("mintfree","claimfree")) and bool(free_views) and reg
    agent_mint = has_mint and bool(free_views) and reg
    print(a, "match=",match,"fns=",len(names),"mint=",has_mint,"quote=",has_quote,"free=",free_views,"reg=",reg,"S1=",s1,"S2=",s2,"agentMint=",agent_mint,flush=True)
    out[a]={"match":match,"fns":len(names),"fn_names":sorted(set(names)),"mint":has_mint,"quote":has_quote,"free_views":free_views,"registry":reg,"S1":s1,"S2":s2,"agent_mint":agent_mint}
json.dump(out, open("hot-leg-2026-11-07-1844-boltbook-shape.json","w"), indent=1)
print("HITS:", [a for a,v in out.items() if v.get("S1") or v.get("S2") or v.get("agent_mint")])
