import json, urllib.request
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REG="60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE_VIEWS=["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeSupply"]
feed=json.load(open(f"{BASE}/run-2026-11-05-2231-sourcify-feed.json"))
seen=json.load(open(f"{BASE}/hot-leg-seen.json"))
seen_l={k.lower() for k in seen}
new=[x for x in feed["results"] if x["address"].lower() not in seen_l]
print("feed:",len(feed["results"]),"new vs hot-leg-seen:",len(new))
out={}
for x in new:
    a=x["address"]
    try:
        req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi", headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as r: d=json.load(r)
        abi=d.get("abi",[])
        fns=sorted({f.get("name") for f in abi if isinstance(f,dict) and f.get("name")})
        src=json.dumps(d).lower()
        mint=any(n in fns for n in ["mint","mintFree","mintShare","buyShare","claimFree"])
        quote=any(n in fns for n in ["quote","cost","getQuote","price"])
        free=[n for n in FREE_VIEWS if n in fns]
        agent=(REG in src) or any(n in fns for n in ["AGENT_REGISTRY","agentRegistry","AgentGate","agentGate"])
        token=any(n in fns for n in ["name","symbol","decimals","totalSupply"]) and "transfer" in fns
        nft=any(n in fns for n in ["tokenURI","ownerOf","totalSupply"]) and "transferFrom" in fns
        s1=mint and quote and bool(free) and agent
        s2=token and ("mintFree" in fns) and bool(free) and agent
        out[a]={"verifiedAt":x["verifiedAt"],"abi_functions":fns,"S1":s1,"S2":s2,"mint":mint,"quote":quote,"free":free,"agent":agent,"token":token,"nft":nft}
        print(a, "S1",s1,"S2",s2,"mint",mint,"quote",quote,"free",free,"agent",agent)
    except Exception as e:
        out[a]={"verifiedAt":x["verifiedAt"],"error":str(e)[:200]}
        print(a,"ERROR",str(e)[:120])
json.dump(out, open(f"{BASE}/run-2026-11-05-2231-sourcify-shape.json","w"), indent=1)
print("saved")
