import json, subprocess, sys
REG="0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE_VIEWS=["freesharesremaining","freeclaimed","freefor","freeleft","freeused","freeavailable","freesharepoolexhausted","freesharesclaimed","freeminted","freeclaim","freemint","freemintleft","freemintedby"]
NEW=['0x0984387ea3e967e19d9190c0a98609e288888888', '0x2d8b22f7b263eeafb695727dc46d685b38dfcb72', '0x307bfb43bfb6a6a736e15bd35cf3e3cbf098ebb4', '0x32368574584ea52d897fbc081d2d4c016c2457f1', '0x32d9c1b0bbf4720667951ede356fd1b6e8888888', '0x5164a2ed85335fa05a6ff28efcd4309cf1fe544f', '0x52931ea992d4efdf198f5690df1df990fb475f62', '0x59c6eca4ff185049a529572e93a2d9655f1b68f0', '0x6f30143c536c02079d77af9cddd51bbf6ecbfc77', '0x8355a07d71170d778171be64d7a377a4cf313b12', '0x9526ae14c60f235d3fadfa88f16a734fc39e1757', '0xa242f7d943fd948c25af7b8f26f9faa4f86158d0', '0xb754e0b67175082da90a826aaf35212e102aa557', '0xbb9056b9c368a902533c5fabbb0bf57e88888888', '0xbe8375d345ff4dc33d683cab6c58adca88888888', '0xd62125790549cdf8fc6e76f899421797f97ef3bc', '0xde1d79b36c1bab83204ec714561a8d59fbe76bca']
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
json.dump(out, open("run-2026-11-07-0931-feed-shape.json","w"), indent=1)
print("HITS:", [a for a,v in out.items() if v.get("S1") or v.get("S2") or v.get("agent_mint")])
