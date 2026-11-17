#!/usr/bin/env python3
import json, subprocess, re
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
feed=json.load(open(BASE+"run-2026-11-03-0931-sourcify.json"))
seen=json.load(open(BASE+"hot-leg-seen.json"))
snap=json.load(open(BASE+"onchain-snapshot.json"))
snap_addrs={v.get("address","").lower() for v in snap.get("contracts",{}).values()}
new=[]
for it in feed.get("results",[]):
    a=it["address"]
    if a.lower() in seen or a in seen: continue
    if a.lower() in snap_addrs: continue
    new.append(a)
print("new vs hot-seen+snapshot:", new)
FREE=["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeClaimed(address)"]
out=[]
for a in new:
    r=subprocess.run(["curl","-sL","--max-time","20",f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi"],capture_output=True,text=True).stdout
    try: abi=json.loads(r).get("abi",[]) if r.startswith("{") else []
    except Exception: abi=[]
    fns=sorted({f.get("name") for f in abi if f.get("type")=="function"})
    txt=json.dumps(abi).lower()
    has_mint=any(f in fns for f in ["mint","mintFree","mintCard"])
    has_quote=any(f in fns for f in ["quote","cost","getQuote"])
    has_free=any(f in fns for f in ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted"])
    agent=("60b9262456de011f7d15a54cdd8c48baaa8b022f" in txt) or any(f in fns for f in ["agentGate","agentId","agentRegistry","isAgent","AGENT_ID"])
    isnft=any(f in fns for f in ["ownerOf","tokenURI","totalMinted"]) or "erc721" in txt or "erc1155" in txt
    istoken=any(f in fns for f in ["decimals","totalSupply"]) and not isnft
    s1=has_mint and has_quote and has_free and agent
    s2=istoken and ("mintFree" in fns) and has_free and agent
    rec={"address":a,"functions":fns,"S1":s1,"S2":s2,"is_nft":isnft,"has_mint":has_mint,"has_quote":has_quote,"has_free":has_free,"agent":agent}
    out.append(rec)
    print(a, "S1",s1,"S2",s2,"nft",isnft,"mint",has_mint,"quote",has_quote,"free",has_free,"agent",agent, fns[:40])
json.dump(out, open(BASE+"run-2026-11-03-0931-sourcify-shape.json","w"), indent=1)
