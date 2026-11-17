import json, urllib.request
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS="2026-11-05-1524"
REG="60b9262456de011f7d15a54cdd8c48baaa8b022f"
def abi_of(a):
    try:
        req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi",headers={"User-Agent":"curl"})
        with urllib.request.urlopen(req,timeout=15) as r: d=json.load(r)
        return d.get("abi") or d.get("stdJson",{}).get("abi") or []
    except Exception as e: return {"error":str(e)[:100]}
feed=json.load(open("/tmp/hotleg-1524-sourcify.json"))
seen=json.load(open(f"{BASE}/hot-leg-seen.json")); seen_l={k.lower() for k in seen}
new=[x["address"] for x in feed["results"] if x["address"].lower() not in seen_l]
excluded=["0x827e83e49bd7e15b67efa0e90fc25f17b8d96124","0x8b47354e7b76b1970a0d06365c8244a810d37493"]
new=[a for a in new if a.lower() not in excluded]
FREE=["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed"]
shape={}
for a in new:
    abi=abi_of(a)
    if isinstance(abi,dict):
        shape[a]={"error":abi.get("error"),"S1":False,"S2":False}; print("SHAPE",a,"ABI-ERR",abi.get("error")); continue
    fns=sorted({f.get("name") for f in abi if f.get("type")=="function" and f.get("name")})
    has_mint=any(n.startswith("mint") for n in fns)
    has_quote="quote" in fns
    free=[f for f in fns if any(x in f for x in FREE)]
    agent=("agentRegistry" in fns or "AGENT_REGISTRY" in fns or "registry" in fns or REG in json.dumps(abi).lower())
    is_token=("name" in fns and "symbol" in fns and "decimals" in fns and "totalSupply" in fns)
    has_mintfree="mintFree" in fns
    s1=has_mint and has_quote and bool(free) and agent
    s2=is_token and has_mintfree and ("freeClaimed" in fns or "freeMinted" in fns) and ("FREE_SLOTS" in fns or "FREE_SUPPLY" in fns) and agent
    shape[a]={"S1":s1,"S2":s2,"has_mint":has_mint,"has_quote":has_quote,"free_views":free,"agent_ref":agent,"is_token":is_token,"fns":fns,
              "verifiedAt":[x["verifiedAt"] for x in feed["results"] if x["address"].lower()==a.lower()]}
    print("SHAPE",a,"S1",s1,"S2",s2,"mint",has_mint,"quote",has_quote,"free",free,"agent",agent,"token",is_token)
json.dump(shape,open(f"{BASE}/hot-leg-{TS}-sourcify-shape.json","w"),indent=1)
print("saved sourcify-shape; new:",new)
