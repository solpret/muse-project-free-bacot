#!/usr/bin/env python3
"""Shape-check 5 addresses for run 2131: 4 new Sourcify feed addrs (triage
feed-retry) + 1 new Boltbook addr. Lowercase shape-check (hot-leg 2114 fix).
Read-only except run-2026-11-11-2131-shape5.json + hot-leg-seen.json notes."""
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
        names=set(fns); lnames={n.lower() for n in names}
        has_mint=any(n.lower().startswith("mint") for n in names)
        has_quote=bool(lnames & {"quote","cost","getquote","mintcost","price","getprice","mintprice"})
        free_views=sorted(names & set(FREE))
        src=json.dumps(meta.get("sources",{}))
        agent_ref=REG in src.lower() or bool(lnames & {"agentid","agentregistry","registry","getagentid","agentgate","agentidregistry"})
        is_token=bool(names & {"name","symbol","decimals","totalSupply"})
        is_nft=bool(names & {"tokenURI","ownerOf","safeTransferFrom"}) or "uri" in names
        mintfree="mintFree" in names
        s1=has_mint and has_quote and bool(free_views) and agent_ref
        s2=is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
        early_shape=is_nft and (agent_ref or bool(names & {"freeMint","mintFree","claimFree"}) or any(n.lower().startswith("freemint") for n in names))
        d.update({"verified":True,"fn_count":len(names),"fns":sorted(names),"has_mint":has_mint,"has_quote":has_quote,
                  "free_views":free_views,"agent_ref":agent_ref,"is_token":is_token,"is_nft":is_nft,
                  "S1":s1,"S2":s2,"early_shape":early_shape,
                  "verifiedAt":meta.get("verifiedAt") or meta.get("match")})
    except Exception as e:
        d.update({"verified":None,"error":f"{type(e).__name__}: {str(e)[:120]}"})
    print(addr, {k:v for k,v in d.items() if k!="fns"}, flush=True)
    return d
ADDRS=["0xD2fb74f382b487E942dC5619581EF8BA8fDca446","0x09828DBC579fA803A975f50065c1254850d0b538",
       "0x35C426d21EF51162BDf5F5F49227107B58b91427","0x56ec4a9A0914570EA6F96E0a53d98f6f8854F040",
       "0x43621df3f0a215f507ebbe5ecf530714788bf29f"]
out={a: shape(a) for a in ADDRS}
json.dump(out, open(BASE+"run-2026-11-11-2131-shape5.json","w"), indent=1)
try:
    seen_j=json.load(open(BASE+"hot-leg-seen.json"))
    for addr,d in out.items():
        if d.get("verified"):
            note=(f"S1={d.get('S1')} S2={d.get('S2')} early={d.get('early_shape')} mint={d.get('has_mint')} quote={d.get('has_quote')} "
                  f"free={d.get('free_views')} agent={d.get('agent_ref')} token={d.get('is_token')} nft={d.get('is_nft')} (shape5 21:31)")
            if addr in seen_j:
                seen_j[addr]["note"]=note
                seen_j[addr]["status"]="sale-shape" if (d.get("S1") or d.get("S2")) else ("early-shape" if d.get("early_shape") else "checked-not-sale-shape")
            else:
                seen_j[addr]={"first_seen_wib":"2026-11-11T21:31:00+07:00","note":note,
                              "source":"sourcify-feed-2131-shape5" if addr!="0x43621df3f0a215f507ebbe5ecf530714788bf29f" else "boltbook-2131",
                              "status":"sale-shape" if (d.get("S1") or d.get("S2")) else ("early-shape" if d.get("early_shape") else "checked-not-sale-shape")}
    json.dump(seen_j, open(BASE+"hot-leg-seen.json","w"), indent=1)
    print("SEEN updated, total", len(seen_j), flush=True)
except Exception as e:
    print("SEEN update FAIL", e, flush=True)
print("SHAPE5 DONE")
