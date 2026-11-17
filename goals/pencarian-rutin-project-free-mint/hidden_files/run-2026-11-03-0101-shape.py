import json, subprocess, concurrent.futures
FREE_VIEWS={"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"}
AGENT_NAMES={"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate","AGENT_ID","AGENT_ID_REGISTRY","agentIdOf","hasAgentId","AGENT_REGISTRY"}
def shape(addr):
    try:
        out=subprocess.run(["curl","-sL","--max-time","20",f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],capture_output=True,text=True).stdout
        meta=json.loads(out); abi=meta.get("abi",[])
        fns={}
        for e in abi:
            if e.get("type")=="function": fns.setdefault(e["name"],[]).append(e)
        names=set(fns)
        has_mint=any(n.lower().startswith("mint") or n in ("freeMint","claimFreeShare","claimFree") for n in names)
        has_quote=bool(names & {"quote","cost","getQuote","mintCost","price","getPrice","costFor"})
        free_views=sorted(names & FREE_VIEWS)
        free_supply=bool(names & {"FREE_SUPPLY","FREE_SLOTS","FREE_SHARES","FREE_CAP","FREE_TOTAL"})
        agent_ref=bool(names & AGENT_NAMES)
        is_nft=bool(names & {"ownerOf","tokenURI"})
        is_token=bool(names & {"name","symbol","decimals","totalSupply"})
        s1=has_mint and has_quote and bool(free_views) and agent_ref
        mintfree="mintFree" in fns and any(len(e.get("inputs",[]))==0 for e in fns["mintFree"])
        s2=is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
        agent_shaped=is_nft and has_mint and (bool(free_views) or free_supply) and agent_ref
        return {"address":addr,"match":meta.get("match"),"functions":sorted(names),"S1":s1,"S2":s2,"agent_shaped":agent_shaped,"is_nft":is_nft,"is_token":is_token,"has_mint":has_mint,"has_quote":has_quote,"free_views":free_views,"free_supply":free_supply,"agent_ref":agent_ref}
    except Exception as ex:
        return {"address":addr,"error":f"{type(ex).__name__}: {str(ex)[:120]}"}
scan=json.load(open("onchain-scan-2026-11-03-0101.json"))
first=json.load(open("run-2026-11-03-0101-scan-firstseen.json"))
# NFT shape candidates: verified + mint_count>=5, skip infra positions
SKIP_NAMES={"UNI-V4-POSM","PCS-V3-POS","UNI-V3-POS","TOPAZ-CL-POS","PCS-INFINITY-POSM","ALGB-POS"}
cands=[c for c in first if c.get("sourcify")=="verified" and c.get("mint_count",0)>=5 and c.get("symbol") not in SKIP_NAMES]
print("NFT candidates:", len(cands))
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
    shapes=list(ex.map(shape, [c["address"] for c in cands]))
byaddr={c["address"]:c for c in cands}
for s in shapes:
    c=byaddr[s["address"]]
    print("NFTSHAPE", c["name"], s["address"], "mints=",c["mint_count"], "S1=",s.get("S1"),"S2=",s.get("S2"),"agent=",s.get("agent_shaped"),"mint=",s.get("has_mint"),"quote=",s.get("has_quote"),"free=",s.get("free_views"),"fsup=",s.get("free_supply"),"agentref=",s.get("agent_ref"),"err=",s.get("error",""))
json.dump(shapes, open("run-2026-11-03-0101-nft-shape.json","w"), indent=1)
# 5c ERC20
checked=set(a.lower() for a in json.load(open("track-c-scan-checked.json"))["checked"])
snap=json.load(open("onchain-snapshot.json"))
snap_addrs={v["address"].lower() for v in snap["contracts"].values()}
for v in snap.get("track_c",{}).values():
    for kk in ("sale","address","token"):
        if v.get(kk): snap_addrs.add(v[kk].lower())
erc=sorted(scan["erc20_mint_contracts_list"], key=lambda e: -e.get("mint_count",0))
todo=[]
for e in erc:
    if e.get("mint_count",0)<10: break
    if e["address"].lower() in checked or e["address"].lower() in snap_addrs: continue
    todo.append(e)
    if len(todo)>=20: break
print("5c todo:", len(todo))
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
    shapes2=list(ex.map(shape, [e["address"] for e in todo]))
for s,e in zip(shapes2,todo):
    print("5c", e["address"], "mints=",e["mint_count"], "S1=",s.get("S1"),"S2=",s.get("S2"),"nft=",s.get("is_nft"),"mint=",s.get("has_mint"),"quote=",s.get("has_quote"),"free=",s.get("free_views"),"agentref=",s.get("agent_ref"),"err=",s.get("error",""))
json.dump([{"address":e["address"],"mint_count":e["mint_count"],**s} for e,s in zip(todo,shapes2)], open("run-2026-11-03-0101-trackc-5c.json","w"), indent=1)
