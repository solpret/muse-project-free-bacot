#!/usr/bin/env python3
"""Triage2 run 2101: curl shape-check the 5 extra addresses that appeared
in the triage feed retry (verifiedAt 14:02:59Z-14:04:51Z), plus full ABI dump
of S1 hit 0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78. Read-only except
run-2026-11-11-2101-triage2.json + abi-2101-EEe3.json + hot-leg-seen notes."""
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
        is_token=bool(names & {"name","symbol","decimals","totalSupply"}) or "transfer" in names
        is_nft=bool(names & {"tokenURI","ownerOf","safeTransferFrom"}) or "uri" in names
        mintfree="mintFree" in names
        s1=has_mint and has_quote and bool(free_views) and agent_ref
        s2=is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
        d.update({"verified":True,"fn_count":len(names),"has_mint":has_mint,"has_quote":has_quote,
                  "free_views":free_views,"agent_ref":agent_ref,"is_token":is_token,"is_nft":is_nft,
                  "S1":s1,"S2":s2,"fn_names":sorted(names)})
    except Exception as e:
        d.update({"verified":None,"error":f"{type(e).__name__}: {str(e)[:120]}"})
    print(addr, {k:v for k,v in d.items() if k!="fn_names"}, flush=True)
    return d
out={}
EXTRA=["0x6F421584a067b511CEb441C2d5b8534B0C9cdDE7","0xdFabF87EE3A9A4cEdda43D3f8035C89E1C9438b7",
       "0x9De342bDFFB5da04D9865f4cd9846D22560D253a","0xE381c967c14b0c6ef82944E0e4b4272D24dd8957",
       "0x097753bD983973940167977980963Aeef87b25CB"]
for a in EXTRA:
    out[a]=shape(a)
# full dump of S1 hit
S1HIT="0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78"
try:
    meta=curl_json(f"https://sourcify.dev/server/v2/contract/56/{S1HIT}?fields=abi,sources,metadata")
    json.dump(meta, open(BASE+"abi-2101-EEe3.json","w"), indent=1)
    abi=meta.get("abi",[])
    fns=[(f.get("name"), f.get("type"), f.get("inputs"), f.get("outputs"), f.get("stateMutability")) for f in abi if isinstance(f,dict)]
    out["S1HIT_abi"]=fns
    out["S1HIT_sources_keys"]=list((meta.get("sources") or {}).keys())
    out["S1HIT_metadata"]=meta.get("metadata")
    print("S1HIT fn_count", len(fns), flush=True)
    for f in fns: print("  FN", f, flush=True)
except Exception as e:
    out["S1HIT_error"]=f"{type(e).__name__}: {str(e)[:150]}"
    print("S1HIT FAIL", e, flush=True)
json.dump(out, open(BASE+"run-2026-11-11-2101-triage2.json","w"), indent=1)
try:
    seen_j=json.load(open(BASE+"hot-leg-seen.json"))
    for addr,d in out.items():
        if addr.startswith("0x") and d.get("verified"):
            note=(f"S1={d.get('S1')} S2={d.get('S2')} mint={d.get('has_mint')} quote={d.get('has_quote')} "
                  f"free={d.get('free_views')} agent={d.get('agent_ref')} token={d.get('is_token')} (triage2 21:01)")
            if addr in seen_j:
                seen_j[addr]["note"]=note
                seen_j[addr]["status"]="sale-shape" if (d.get("S1") or d.get("S2")) else "checked-not-sale-shape"
            else:
                seen_j[addr]={"first_seen_wib":"2026-11-11T21:01:00+07:00","note":note,
                              "source":"sourcify-feed-2101-triage2",
                              "status":"sale-shape" if (d.get("S1") or d.get("S2")) else "checked-not-sale-shape"}
    json.dump(seen_j, open(BASE+"hot-leg-seen.json","w"), indent=1)
    print("SEEN updated", flush=True)
except Exception as e:
    print("SEEN update FAIL", e, flush=True)
print("TRIAGE2 DONE")
