#!/usr/bin/env python3
"""Triage run 2034: curl-retry shape-check for 2 feed-new addrs whose legs
urllib ABI fetch hit IncompleteRead, plus 1 new Boltbook address.
Read-only except run-2026-11-11-2034-triage.json + hot-leg-seen.json note updates.
No preview/mint."""
import json, subprocess
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
REG="60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE=["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining","freeSupply","FREE_SUPPLY"]
def curl_json(url, timeout=30):
    r=subprocess.run(["curl","-sL","--max-time",str(timeout),url],capture_output=True,text=True,timeout=timeout+5)
    return json.loads(r.stdout)
def shape(addr):
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
        is_token=bool(names & {"name","symbol","decimals","totalSupply"})
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
    return d
out={}
for a in ("0x48D9AaF5E2a7b72b31c9A83F21994F81b4F7E607",
          "0x9b570792AF9Cc1C25b58405Cd08acF19F3291097",
          "0x1dCc16ee772932D7bEeC2e6feBB9218cb00Adae4",
          "0xAF1Fa6fdf141C3fd05B816Ae717fFBB7975D81A3"):
    out[a]=shape(a)
json.dump(out, open(BASE+"run-2026-11-11-2034-triage.json","w"), indent=1)
seen_j=json.load(open(BASE+"hot-leg-seen.json"))
for addr,d in out.items():
    if d.get("verified"):
        if addr in seen_j:
            seen_j[addr]["note"]=f"S1={d.get('S1')} S2={d.get('S2')} mint={d.get('has_mint')} quote={d.get('has_quote')} free={d.get('free_views')} agent={d.get('agent_ref')} token={d.get('is_token')} (triage 20:34)"
            seen_j[addr]["status"]="sale-shape" if (d.get("S1") or d.get("S2")) else "checked-not-sale-shape"
        else:
            seen_j[addr]={"first_seen_wib":"2026-11-11T20:34:00+07:00",
                          "note":f"S1={d.get('S1')} S2={d.get('S2')} mint={d.get('has_mint')} quote={d.get('has_quote')} free={d.get('free_views')} agent={d.get('agent_ref')} token={d.get('is_token')} (triage 20:34)",
                          "source":"sourcify-feed-2034-triage",
                          "status":"sale-shape" if (d.get("S1") or d.get("S2")) else "checked-not-sale-shape"}
    else:
        if addr not in seen_j:
            seen_j[addr]={"first_seen_wib":"2026-11-11T20:34:00+07:00",
                          "note":f"shape-check FAILED: {d.get('error')} (triage 20:34)",
                          "source":"sourcify-feed-2034-triage","status":"shape-check-failed"}
json.dump(seen_j, open(BASE+"hot-leg-seen.json","w"), indent=1)
print("TRIAGE DONE", flush=True)
