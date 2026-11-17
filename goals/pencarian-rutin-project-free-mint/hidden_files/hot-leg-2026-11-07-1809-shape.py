import json, subprocess
REG="0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE_VIEWS=["freesharesremaining","freeclaimed","freefor","freeleft","freeused","freeavailable","freesharepoolexhausted","freesharesclaimed","freeminted","freeclaim","freemint","freemintleft","freemintedby"]
NEW=['0x9CCd858cBFffD61A94086B954337D4a64013fF5e','0x871E9aFaED4e4D6f743BbF5C851672D8FDa8B5DD','0xb58f46961d6169c7cE86209004110518f25579E2','0x4Bb5E1e900704381b0a83edd9382A44c0552C658','0x16d2bB14699253be43424512d03D86eCD49aC527','0x46298D752bb8Ff308c60e208b3a4dfA0828b06FB','0xCcE63963fCe37A033264ba2D1d2F68d3138a2255','0xe9d22f9AA1ceED72c03FBde027C87E268bb1276F']
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
json.dump(out, open("hot-leg-2026-11-07-1809-feed-shape.json","w"), indent=1)
print("HITS:", [a for a,v in out.items() if v.get("S1") or v.get("S2") or v.get("agent_mint")])
