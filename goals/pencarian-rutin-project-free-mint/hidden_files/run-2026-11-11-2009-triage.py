#!/usr/bin/env python3
"""Triage run 2009: retry Sourcify ABI fetch (curl) for the 2 feed addresses
whose urllib fetch hit IncompleteRead in legs.py. Read-only except
run-2026-11-11-2009-triage.json + hot-leg-seen.json note update for resolved ones.
No preview/mint."""
import json, subprocess, time
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
REG="60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE=["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining","freeSupply","FREE_SUPPLY"]
def curl_json(url, timeout=30):
    r=subprocess.run(["curl","-sL","--max-time",str(timeout),url],capture_output=True,text=True,timeout=timeout+5)
    return json.loads(r.stdout)
out={}
for addr in ["0x212d37DD95a203010Be972093cFe4D925686B78c","0x4172719294816d45d25A57609852261EDD60efb9","0x2b3F6A3D22659739F672A1e46e82Ffe5233451D7","0x26db627D2dD9061296B2BE6C760b1273d11b9999","0xb7c64DA97c6a4dc81eb873f530C89765A72131fB","0x4E937830Fec463B6AB0f73513B3f168aAc5d8888","0x06Bf46B0971C7F40167B9904e38B6727c58AA372","0xaeed94086eAD221419d09D37e8f0952E0998bc7F","0x39271fed6FE07AD92094910c77a79b515C2152db","0x272831D45ac4bc8a32DBAB14a65C66080853bAcb","0xFb183bfF18bD9C7A7c9c3D143D5EBBBc43627B76","0x23aE135B7f479e6040A8C7F4dC1ebC4E4ca746eA","0x0799b437309007785DEaC26d8f0397Dc84d1C3d6","0xD3a86392249a9a79ae6be6faE9DC8cE336492A9E","0x425AdE3892129E59B7Ff512a1F5CeAfCcB4FE47C"]:
    d={"address":addr}
    try:
        meta=curl_json(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi,sources")
        abi=meta.get("abi",[])
        fns=[f.get("name") for f in abi if isinstance(f,dict) and f.get("type")=="function"]
        names=set(fns)
        has_mint=any(n.lower().startswith("mint") for n in names)
        has_quote=bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
        free_views=sorted(names & set(FREE))
        src=json.dumps(meta.get("sources",{}))
        agent_ref=REG in src.lower() or bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate"})
        is_token=bool(names & {"name","symbol","decimals","totalSupply","balanceOf"}) and "totalSupply" in names
        is_nft=bool(names & {"tokenURI","ownerOf","safeTransferFrom"}) or "uri" in names
        mintfree="mintFree" in names
        s1=has_mint and has_quote and bool(free_views) and agent_ref
        s2=is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
        d.update({"verified":True,"fn_count":len(names),"has_mint":has_mint,"has_quote":has_quote,
                  "free_views":free_views,"agent_ref":agent_ref,"is_token":is_token,"is_nft":is_nft,
                  "S1":s1,"S2":s2})
    except Exception as e:
        d.update({"verified":None,"error":f"{type(e).__name__}: {str(e)[:120]}"})
    print(addr, d, flush=True)
    out[addr]=d
json.dump(out, open(BASE+"run-2026-11-11-2009-triage.json","w"), indent=1)
# update seen notes for resolved ones
try:
    seen=json.load(open(BASE+"hot-leg-seen.json"))
    for addr,d in out.items():
        if d.get("verified") and addr in seen:
            seen[addr]["note"]=f"S1={d.get('S1')} S2={d.get('S2')} mint={d.get('has_mint')} quote={d.get('has_quote')} free={d.get('free_views')} agent={d.get('agent_ref')} token={d.get('is_token')} (triage-retry 20:04)"
            seen[addr]["status"]="sale-shape" if (d.get("S1") or d.get("S2")) else "checked-not-sale-shape"
    json.dump(seen, open(BASE+"hot-leg-seen.json","w"), indent=1)
    print("SEEN updated", flush=True)
except Exception as e:
    print("SEEN update FAIL", e, flush=True)
print("TRIAGE DONE")
