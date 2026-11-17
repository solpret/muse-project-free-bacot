import json, urllib.request, pathlib
base=pathlib.Path.home()/"workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
triage=json.load(open(base/"run-2026-11-02-0701-scan-triage.json"))
todo=triage["erc20_todo"][:20]
FREE_VIEWS=["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeSharesMinted","freeShares","freeSupply","FREE_SUPPLY","FREE_SHARES"]
out=[]
for e in todo:
    a=e["address"]; rec={"address":a,"mint_count":e["mint_count"],"distinct_minters":e["distinct_minters"]}
    try:
        req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi", headers={"User-Agent":"Mozilla/5.0"})
        d=json.load(urllib.request.urlopen(req, timeout=20)); abi=d.get("abi") or []
        fns=[f["name"] for f in abi if f.get("type")=="function"]
        rec["fns"]=fns
        rec["has_mint"]=any("mint" in x.lower() for x in fns)
        rec["has_quote"]=any("quote" in x.lower() or "cost" in x.lower() for x in fns)
        rec["free_views"]=[x for x in fns if x in FREE_VIEWS or ("free" in x.lower() and not x.lower().startswith("freeze"))]
        rec["agent_ref"]=any("registry" in x.lower() or "agent" in x.lower() for x in fns)
        rec["is_token"]=all(x in fns for x in ["name","symbol","decimals","totalSupply"])
        rec["has_mintFree"]=any(x in ("mintFree","claimFree","freeMint") for x in fns)
        rec["S1"]=bool(rec["has_mint"] and rec["has_quote"] and rec["free_views"] and rec["agent_ref"])
        rec["S2"]=bool(rec["is_token"] and rec["has_mintFree"] and rec["free_views"] and rec["agent_ref"])
    except Exception as ex:
        rec["error"]=str(ex)[:200]
    out.append(rec); print(a, e["mint_count"], rec.get("S1"), rec.get("S2"), rec.get("error",""), (rec.get("fns") or [])[:12])
json.dump(out, open(base/"run-2026-11-02-0701-trackc-erc20-shape.json","w"), indent=1)
# update checked file
chk=json.load(open(base/"track-c-scan-checked.json"))
lst=chk.get("checked",[])
s=set(x.lower() for x in lst)
for e in todo: s.add(e["address"].lower())
chk["checked"]=sorted(s); chk["note"]=chk.get("note","")
json.dump(chk, open(base/"track-c-scan-checked.json","w"), indent=1)
print("checked total now", len(chk["checked"]))
