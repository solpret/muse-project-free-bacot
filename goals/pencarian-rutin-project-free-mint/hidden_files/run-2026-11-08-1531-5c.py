import json, urllib.request
REG="60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE_VIEWS=["freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeSharesRemaining","freeMinted","freeMint","freeSupply","freeFor","free"]
def fetch(addr):
    url=f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    req=urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r: return json.load(r)
    except Exception as e: return {"_error": str(e)}
d=json.load(open('onchain-scan-2026-11-08-1531.json'))
lst=d.get('erc20_mint_contracts_list',[])
checked=json.load(open('track-c-scan-checked.json'))
seen=set()
if isinstance(checked, dict):
    seen |= {k.lower() for k in checked.keys() if k.startswith('0x')}
    sub=checked.get('checked')
    if isinstance(sub, dict): seen |= {k.lower() for k in sub.keys()}
print("already-checked total:", len(seen))
cands=[x for x in sorted(lst, key=lambda z: z.get('mint_count',0), reverse=True) if x.get('mint_count',0)>=10 and x['address'].lower() not in seen]
print("mint_count>=10 total:", sum(1 for x in lst if x.get('mint_count',0)>=10), "| new to check:", len(cands))
take=cands[:20]
out={}
for x in take:
    addr=x['address']
    dd=fetch(addr)
    abi=dd.get("abi") or (dd.get("stdJson",{}).get("output",{}).get("abi") if isinstance(dd.get("stdJson"),dict) else None)
    if dd.get("_error") or not isinstance(abi,list):
        out[addr]={"error": dd.get("_error","no-abi"), "mint_count": x.get('mint_count')}
        print(addr, "mint_count=",x.get('mint_count'), "ERROR/no-abi", flush=True); continue
    fns=[e.get("name","") for e in abi if e.get("type")=="function"]
    src=json.dumps(dd).lower()
    has_mint=any(n in fns for n in ["mint","mintFree","freeMint","mintAgent","claimFree"])
    has_quote=any(n in fns for n in ["quote","cost","price","priceForSerial","mintQuote","getQuote"])
    freeviews=[n for n in fns if any(fv.lower() in n.lower() for fv in FREE_VIEWS)]
    registry=REG in src
    is_token=all(n in fns for n in ["name","symbol","decimals","totalSupply"])
    noarg_free=any(n in fns for n in ["mintFree"])
    s1=has_mint and has_quote and bool(freeviews) and registry
    s2=is_token and noarg_free and bool(freeviews) and registry
    out[addr]={"mint_count":x.get('mint_count'),"fns":len(fns),"has_mint":has_mint,"has_quote":has_quote,"free_views":freeviews,"registry_bytes":registry,"is_token":is_token,"S1":s1,"S2":s2}
    print(addr, "mint_count=",x.get('mint_count'), "fns=",len(fns), "mint=",has_mint,"quote=",has_quote,"freeviews=",freeviews,"registry=",registry,"S1=",s1,"S2=",s2, flush=True)
json.dump(out, open('run-2026-11-08-1531-5c.json','w'), indent=1)
# record newly checked (top-level keys, per established file structure)
for addr in out:
    checked[addr]=out[addr]
json.dump(checked, open('track-c-scan-checked.json','w'), indent=1)
print("checked-file top-level now:", len([k for k in checked if k.startswith('0x')]))
print("dropped sampling-limit this window:", max(0, len(cands)-20))
