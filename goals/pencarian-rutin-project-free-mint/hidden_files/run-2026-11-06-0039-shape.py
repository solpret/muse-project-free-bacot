#!/usr/bin/env python3
"""Hot-leg run 2026-11-06 00:39 WIB — Leg 1 shape-check for 8 new Sourcify feed contracts."""
import json, urllib.request, time
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
NEW=[
 ("0xB48a0A2199A895262A049f07417187Fa3590a1BD","2026-11-05T17:42:06Z"),
 ("0x642B2Cb1a28cE691cBF508186690B0d99bFc6268","2026-11-05T17:42:03Z"),
 ("0x193243ce79C41724D998C5B8a4f08cB04Ee9567f","2026-11-05T17:41:44Z"),
 ("0xA41Fd9885A8C70297978C7bBCEb91B0EdC3b00dB","2026-11-05T17:40:47Z"),
 ("0xa2089193df7773D6b95f54769fC30250054f4Db5","2026-11-05T17:39:46Z"),
 ("0xf962e4F67e5FF379b3D8237b69385a3D9cf78e55","2026-11-05T17:36:56Z"),
 ("0x77a4C407907c24daF6CbAdbb90a5cbD2ad233Fa2","2026-11-05T17:34:53Z"),
 ("0x92aDF8Fa4F1b5Fc022ea5e2DF76a4ab6AF410D00","2026-11-05T17:34:29Z"),
]
FREE_VIEWS={"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted"}
AGENT_VIEWS={"AGENT_REGISTRY","agentRegistry","agentId","hasAgentId","agentGate","AgentGate","registry"}
def fetch_abi(addr):
    url=f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    for attempt in range(3):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"hot-leg/1.0"})
            with urllib.request.urlopen(req,timeout=15) as r:
                d=json.load(r)
            abi=d.get("abi") or d.get("stdJson",{}).get("abi") or []
            return abi, "verified" if attempt==0 else "verified-retry"
        except Exception as e:
            if attempt<2: time.sleep(2); continue
            return None, f"error:{e}"
    return None, "error"
out={}
for addr,vat in NEW:
    abi,status=fetch_abi(addr)
    if abi is None:
        out[addr]={"verifiedAt":vat,"sourcify":status,"S1":False,"S2":False}
        print(addr,"ABI-FETCH-FAIL",status,flush=True); continue
    fns=[e for e in abi if e.get("type")=="function"]
    names=[f.get("name","") for f in fns]
    mint=[n for n in names if "mint" in n.lower()]
    quote=[n for n in names if "quote" in n.lower() or n in ("PRICE","price","cost","getCost","mintCost")]
    free=[n for n in names if n in FREE_VIEWS]
    agent=[n for n in names if n in AGENT_VIEWS]
    token=[n for n in names if n in ("name","symbol","decimals","totalSupply")]
    nft = ("ownerOf" in names) or ("tokenURI" in names)
    s1 = bool(mint) and bool(quote) and bool(free) and bool(agent)
    # S2: token all 4 + no-arg mintFree + freeClaimed/freeMinted + FREE_SLOTS/FREE_SUPPLY + agent
    mintfree=[f for f in fns if f.get("name")=="mintFree" and len(f.get("inputs",[]))==0]
    s2 = (len(token)==4) and bool(mintfree) and bool(set(free)&{"freeClaimed","freeMinted"}) \
         and bool(set(names)&{"FREE_SLOTS","FREE_SUPPLY"}) and bool(agent)
    out[addr]={"verifiedAt":vat,"sourcify":status,"functions":len(fns),"mint":mint,"quote":quote,
               "free":free,"agent":agent,"token":token,"nft":nft,"S1":s1,"S2":s2}
    print(addr,"S1",s1,"S2",s2,"nft",nft,"mint",mint,"quote",quote,"free",free,"agent",agent,"token",token,flush=True)
json.dump(out,open(f"{BASE}/run-2026-11-06-0039-sourcify-shape.json","w"),indent=1)
print("DONE",flush=True)
