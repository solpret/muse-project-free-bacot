#!/usr/bin/env python3
"""Triage run 2004: retry Sourcify ABI fetch (curl) for the 2 feed addresses
whose urllib fetch hit IncompleteRead in legs.py. Read-only except
run-2026-11-11-2004-triage.json + hot-leg-seen.json note update for resolved ones.
No preview/mint."""
import json, subprocess, time
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
REG="60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE=["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining","freeSupply","FREE_SUPPLY"]
def curl_json(url, timeout=30):
    r=subprocess.run(["curl","-sL","--max-time",str(timeout),url],capture_output=True,text=True,timeout=timeout+5)
    return json.loads(r.stdout)
out={}
for addr in ["0x1BDBDD73f51079c64BCA3917629c84c257921aCc","0x3eB1Cba72Bc58F3fbAF7a27bdE5547Be4cb9eD7e"]:
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
json.dump(out, open(BASE+"run-2026-11-11-2004-triage.json","w"), indent=1)
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
