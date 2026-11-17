#!/usr/bin/env python3
"""Triage run 2201: (a) retry Sourcify feed via curl (legs urllib hit
IncompleteRead on 6/10 new ABIs); (b) curl shape-check the 6 errored
new feed addresses. Read-only except run-2026-11-11-2201-triage.json
+ hot-leg-seen.json note updates. No preview/mint."""
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
        lnames={n.lower() for n in names}
        has_quote=bool(lnames & {"quote","cost","getquote","mintcost","price","getprice","mintprice"})
        free_views=sorted(names & set(FREE))
        src=json.dumps(meta.get("sources",{}))
        agent_ref=REG in src.lower() or bool(lnames & {"agentid","agentregistry","registry","getagentid","agentgate","agentidregistry"})
        is_token=bool(names & {"name","symbol","decimals","totalSupply"}) or "transfer" in names
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
# (a) feed retry via curl
try:
    feed=curl_json("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", timeout=30)
    json.dump(feed, open(BASE+"run-2026-11-11-2201-feed.json","w"), indent=1)
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
for pf in ("run-2026-11-11-2131-feed.json", "run-2026-11-11-2031-feed.json"):
    try:
        prev=json.load(open(BASE+pf))
        for it in prev.get("results",[]): seen.add(str(it.get("address","")).lower())
    except Exception: pass
new_addrs=[it.get("address") for it in items if str(it.get("address","")).lower() not in seen and it.get("address")]
out["feed_new"]=new_addrs
json.dump(new_addrs, open(BASE+"run-2026-11-11-2201-feed-new.json","w"), indent=1)
print("FEED NEW:", new_addrs, flush=True)
# (b) shape-check only the 6 addresses whose legs urllib ABI fetch errored
ERR=[]
try:
    _legs=json.load(open(BASE+"run-2026-11-11-2201-legs.json"))
    for _s in _legs.get("feed_shape",{}).get("shapes",[]):
        if _s.get("error"): ERR.append(_s.get("address"))
    for _a in _legs.get("feed_shape",{}).get("s1_pass",[])+_legs.get("feed_shape",{}).get("s2_pass",[])+_legs.get("feed_shape",{}).get("early_shape",[]):
        if _a not in ERR: ERR.append(_a)
except Exception as _e:
    print("ERR dynamic build fail", _e, flush=True)
print("TRIAGE ERR/SHAPE-LIST:", ERR, flush=True)
for a in ERR:
    out[a]=shape(a)
json.dump(out, open(BASE+"run-2026-11-11-2201-triage.json","w"), indent=1)
try:
    seen_j=json.load(open(BASE+"hot-leg-seen.json"))
    legs=json.load(open(BASE+"run-2026-11-11-2201-legs.json"))
    leg_shapes={s.get("address"):s for s in legs.get("feed_shape",{}).get("shapes",[]) if s.get("address")}
    for addr,d in out.items():
        if addr.startswith("0x") and d.get("verified"):
            note=(f"S1={d.get('S1')} S2={d.get('S2')} mint={d.get('has_mint')} quote={d.get('has_quote')} "
                  f"free={d.get('free_views')} agent={d.get('agent_ref')} token={d.get('is_token')} (triage-retry 22:01)")
            if addr in seen_j:
                seen_j[addr]["note"]=note
                seen_j[addr]["status"]="sale-shape" if (d.get("S1") or d.get("S2")) else "checked-not-sale-shape"
            else:
                seen_j[addr]={"first_seen_wib":"2026-11-11T22:01:00+07:00","note":note,
                              "source":"sourcify-feed-2201-triage",
                              "status":"sale-shape" if (d.get("S1") or d.get("S2")) else "checked-not-sale-shape"}
    # also record the 4 legs-checked addresses (no error) in seen
    for addr,s in leg_shapes.items():
        if addr not in seen_j and not s.get("error"):
            seen_j[addr]={"first_seen_wib":"2026-11-11T22:01:00+07:00",
                          "note":(f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('has_mint')} quote={s.get('has_quote')} "
                                 f"free={s.get('free_views')} agent={s.get('agent_ref')} token={s.get('is_token')} (legs 22:01)"),
                          "source":"sourcify-feed-2201-legs",
                          "status":"sale-shape" if (s.get("S1") or s.get("S2")) else "checked-not-sale-shape"}
    json.dump(seen_j, open(BASE+"hot-leg-seen.json","w"), indent=1)
    print("SEEN updated, total", len(seen_j), flush=True)
except Exception as e:
    print("SEEN update FAIL", e, flush=True)
print("TRIAGE DONE")
