import json, urllib.request
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REG="60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE=["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed"]
new=json.load(open(f"{BASE}/run-2026-11-05-1331-erc20-new.json"))
top=new[:20]
def abi_of(a):
    try:
        req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi",headers={"User-Agent":"curl"})
        with urllib.request.urlopen(req,timeout=15) as r: d=json.load(r)
        return d.get("abi") or d.get("stdJson",{}).get("abi") or []
    except Exception as e: return {"error":str(e)[:80]}
out={}
for e in top:
    a=e["address"]
    abi=abi_of(a)
    if isinstance(abi,dict):
        out[a]={"error":abi.get("error"),"mint_count":e["mint_count"],"S1":False,"S2":False}
        print(a,"SOURCIFY-404/ERR",e["mint_count"]); continue
    fns=sorted({f.get("name") for f in abi if f.get("type")=="function" and f.get("name")})
    has_mint=any(n.startswith("mint") for n in fns)
    has_quote="quote" in fns
    free=[f for f in fns if any(x in f for x in FREE)]
    agent=("agentRegistry" in fns or "AGENT_REGISTRY" in fns or "registry" in fns or REG in json.dumps(abi).lower())
    is_token=all(x in fns for x in ("name","symbol","decimals","totalSupply"))
    s1=has_mint and has_quote and bool(free) and agent
    s2=is_token and "mintFree" in fns and ("freeClaimed" in fns or "freeMinted" in fns) and ("FREE_SLOTS" in fns or "FREE_SUPPLY" in fns) and agent
    out[a]={"mint_count":e["mint_count"],"S1":s1,"S2":s2,"mint":has_mint,"quote":has_quote,"free":free,"agent":agent,"token":is_token,"fns":fns}
    print(a,"S1",s1,"S2",s2,"mint",has_mint,"quote",has_quote,"free",free,"agent",agent)
json.dump(out, open(f"{BASE}/run-2026-11-05-1331-trackc-shape.json","w"), indent=1)
