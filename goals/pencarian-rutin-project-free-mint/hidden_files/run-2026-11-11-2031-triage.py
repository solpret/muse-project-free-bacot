#!/usr/bin/env python3
"""Triage run 2031: (a) retry Sourcify feed via curl (legs urllib hit
IncompleteRead); (b) shape-check new Boltbook address 0xf21031e004904efb1f4bfb2b72aec23334ce1e50.
Read-only except run-2026-11-11-2031-triage.json + hot-leg-seen.json note updates.
No preview/mint."""
import json, subprocess, time
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
    return d
out={}
# (a) feed retry
try:
    feed=curl_json("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", timeout=30)
    json.dump(feed, open(BASE+"run-2026-11-11-2031-feed.json","w"), indent=1)
    items=feed.get("results",[])
    out["feed"]={"n":len(items),"newest_verifiedAt":items[0].get("verifiedAt") if items else None,
                 "oldest_verifiedAt":items[-1].get("verifiedAt") if items else None}
    print("FEED-RETRY", out["feed"], flush=True)
except Exception as e:
    out["feed"]={"error":f"{type(e).__name__}: {str(e)[:150]}"}
    items=[]
    print("FEED-RETRY FAIL", e, flush=True)
seen=set()
try:
    hl=json.load(open(BASE+"hot-leg-seen.json"))
    if isinstance(hl,dict): seen|={k.lower() for k in hl.keys()}
except Exception: pass
for pf in ("run-2026-11-11-2019-feed.json",):
    try:
        prev=json.load(open(BASE+pf))
        for it in prev.get("results",[]): seen.add(str(it.get("address","")).lower())
    except Exception: pass
new_addrs=[it.get("address") for it in items if str(it.get("address","")).lower() not in seen and it.get("address")]
out["feed_new"]=new_addrs
json.dump(new_addrs, open(BASE+"run-2026-11-11-2031-feed-new.json","w"), indent=1)
print("FEED NEW:", new_addrs, flush=True)
for a in new_addrs:
    out[a]=shape(a)
# (b) new Boltbook addresses (1, from 2031 legs)
for bb in ("0xd612a555d4e7a1f01012991af447f35a1fb91e3f",):
    out[bb]=shape(bb)
json.dump(out, open(BASE+"run-2026-11-11-2031-triage.json","w"), indent=1)
try:
    seen_j=json.load(open(BASE+"hot-leg-seen.json"))
    for addr,d in out.items():
        if addr.startswith("0x") and d.get("verified") and addr in seen_j:
            seen_j[addr]["note"]=f"S1={d.get('S1')} S2={d.get('S2')} mint={d.get('has_mint')} quote={d.get('has_quote')} free={d.get('free_views')} agent={d.get('agent_ref')} token={d.get('is_token')} (triage-retry 20:31)"
            seen_j[addr]["status"]="sale-shape" if (d.get("S1") or d.get("S2")) else "checked-not-sale-shape"
    for a in new_addrs:
        if a and a.lower() not in {k.lower() for k in seen_j}:
            d=out.get(a,{})
            seen_j[a]={"first_seen_wib":"2026-11-11T20:31:00+07:00",
                       "note":f"S1={d.get('S1')} S2={d.get('S2')} mint={d.get('has_mint')} quote={d.get('has_quote')} free={d.get('free_views')} agent={d.get('agent_ref')} token={d.get('is_token')} (triage-retry 20:31)",
                       "source":"sourcify-feed-2031-triage","status":"sale-shape" if (d.get("S1") or d.get("S2")) else "checked-not-sale-shape"}
    json.dump(seen_j, open(BASE+"hot-leg-seen.json","w"), indent=1)
    print("SEEN updated, total", len(seen_j), flush=True)
except Exception as e:
    print("SEEN update FAIL", e, flush=True)
print("TRIAGE DONE")
