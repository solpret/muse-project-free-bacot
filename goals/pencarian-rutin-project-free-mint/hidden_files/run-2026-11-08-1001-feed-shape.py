import json, urllib.request, urllib.error
ADDRS=["0x3db85889678c1cd9f191b602f275b04165d7b95c","0xe89fa17b9c94267d0bba284ee2cfb0ad5585fde1","0xa91c8a0ca40b8d2d1ebe3903bdc93bcea69622f0","0x7056dfe6cdc208f385f4867062ba2808d3836e30"]
REG="60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE=["freesharesremaining","freeclaimed","freefor","freeleft","freeused","freeavailable","freesharepoolexhausted","freesharesclaimed","freeminted","freesupply","free_slots","free_supply","freeslots"]
def get_abi(a):
    url=f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi"
    req=urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            d=json.load(r)
        return d.get("abi") or d.get("stdJson",{}).get("abi") or d
    except urllib.error.HTTPError as e:
        return {"_http": e.code}
    except Exception as e:
        return {"_err": str(e)}
out={}
for a in ADDRS:
    abi=get_abi(a)
    if not isinstance(abi,list):
        out[a]={"status":"sourcify_"+str(abi)}; print(a, out[a]); continue
    fns=[x.get("name","") for x in abi if x.get("type")=="function"]
    low=[f.lower() for f in fns]
    has_mint=any(f.startswith("mint") for f in low)
    has_quote=any("quote" in f or f.startswith("cost") for f in low)
    free=[f for f in low if any(k in f for k in FREE)]
    has_token=all(x in low for x in ["name","symbol","decimals","totalsupply"])
    # registry ref: check raw abi text for registry address bytes
    raw=json.dumps(abi).lower()
    reg = REG in raw or "agentregistry" in raw or "agent_id_registry" in raw or "agentidregistry" in raw
    s1 = has_mint and has_quote and bool(free) and reg
    noarg_free = any(f in ("mintfree","claimfree","freemint") for f in low)
    s2 = has_token and noarg_free and bool(free) and reg
    out[a]={"fns":len(fns),"mint":has_mint,"quote":has_quote,"free":free,"token":has_token,"registry":reg,"S1":s1,"S2":s2,"fn_sample":fns[:40]}
    print(a, "fns",len(fns),"mint",has_mint,"quote",has_quote,"free",free,"token",has_token,"reg",reg,"S1",s1,"S2",s2)
json.dump(out, open("run-2026-11-08-1001-feed-shape.json","w"), indent=1)
