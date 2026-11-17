import json, urllib.request, concurrent.futures
HF="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
FEED=["0xe15e68C9198ee0A5780fba96016e1780204aF3B4","0xaBFB4b2Ae7BF97A76ad6804e7dE71325877Ff68C","0x647a37bFD60348f9EE471aaD3FB3e7eCd6584Cd5","0x81F34cBF06D747715E1691CBB92bCCB2452265CE","0xa196f6e2BbbE4191f623156b0a906199Ee8e2766","0xE2047f286E390483dB2adE8BAA433F797cd3f9B3","0xdBC044EB8f2756B0F7bc7dA573DeF8c8aD433122","0x91088abB4975C8bA424Ceb430e98fF4808046cB2","0xDB66aFddafEb59cbE83178750398482AC42E50A9","0x79B5D86089a29a65faC3278572f00C8FADc361fb","0xaE3eb0525BF6CCFf4A914Ec65537CE6E7F2CDc79","0xa7b012332a6dc244Ac7195241023042092929314"]
FREE_VIEWS=["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"]
def fetch(addr):
    url=f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        req=urllib.request.Request(url, headers={"User-Agent":"hot-leg/1.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            abi=json.loads(r.read().decode()).get("abi", [])
        fns={}
        for e in abi:
            if e.get("type")=="function": fns.setdefault(e["name"],[]).append(e)
        names=set(fns)
        has_mint=any(n.lower().startswith("mint") for n in names)
        has_quote=bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
        fv=sorted(names & set(FREE_VIEWS))
        agent=bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate"})
        s1=has_mint and has_quote and bool(fv) and agent
        is_token=bool(names & {"name","symbol","decimals","totalSupply"})
        mf="mintFree" in fns and any(len(e.get("inputs",[]))==0 for e in fns["mintFree"])
        s2=is_token and mf and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent
        return {"address":addr,"functions":sorted(names),"S1":s1,"S2":s2,"has_mint":has_mint,"has_quote":has_quote,"free_views":fv,"agent_ref":agent,"is_token":is_token}
    except Exception as ex:
        return {"address":addr,"error":f"{type(ex).__name__}: {str(ex)[:120]}"}
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
    out=list(ex.map(fetch, FEED))
for o in out: print(json.dumps(o))
json.dump(out, open(f"{HF}/hot-leg-2026-11-01-2334-sourcify-shape.json","w"), indent=1)
print("S1_PASS:",[o["address"] for o in out if o.get("S1")])
print("S2_PASS:",[o["address"] for o in out if o.get("S2")])
