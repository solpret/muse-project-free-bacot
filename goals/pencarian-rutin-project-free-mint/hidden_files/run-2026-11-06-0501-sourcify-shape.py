import json, urllib.request, time
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
items=json.load(open(f"{BASE}/run-2026-11-06-0501-sourcify-items.json"))
seen=json.load(open(f"{BASE}/hot-leg-seen.json"))
seen_addrs=set()
def collect(o):
    if isinstance(o,dict):
        for k,v in o.items():
            if isinstance(v,str) and v.startswith('0x') and len(v)==42: seen_addrs.add(v.lower())
            else: collect(v)
    elif isinstance(o,list):
        for v in o: collect(v)
collect(seen)
new=[it for it in items if it.get('address','').lower() not in seen_addrs]
print('feed:',len(items),'new vs hot-leg-seen:',len(new))
REG='60b9262456de011f7d15a54cdd8c48baaa8b022f'
FREE_VIEWS=['freesharesremaining','freeclaimed','freefor','freeleft','freeused','freeavailable','freesharepoolexhausted','freesharesclaimed','freeminted','free_supply','freeslots','freeamount']
def fetch_abi(addr):
    for base in [f"https://sourcify.dev/server/v2/contracts/56/{addr}", f"https://repo.sourcify.dev/contracts/56/{addr}"]:
        try:
            req=urllib.request.Request(base, headers={'User-Agent':'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=20) as r: return json.load(r)
        except Exception as e: continue
    return None
out=[]
for it in new:
    addr=it['address']
    meta=fetch_abi(addr)
    rec={'address':addr,'verifiedAt':it.get('verifiedAt')}
    if not meta:
        rec['error']='sourcify fetch failed'; out.append(rec); print(addr,'FETCH FAIL'); continue
    abi=meta.get('abi') or (meta.get('metadata',{}).get('output',{}).get('abi') if isinstance(meta.get('metadata'),dict) else None)
    src=json.dumps(meta).lower()
    names=[]
    if abi:
        for e in abi:
            if e.get('type')=='function': names.append(e.get('name','').lower())
    has_mint=any('mint' in n for n in names)
    has_quote=any('quote' in n or 'cost' in n for n in names)
    free=[n for n in names if any(f in n for f in FREE_VIEWS)]
    has_agent=(REG in src) or any('agent' in n and ('gate' in n or 'registry' in n) for n in names)
    is_token=any(n in names for n in ['name','symbol','decimals','totalsupply'])
    noarg_free=any(n in ('mintfree','freemint','claimfree') for n in names)
    s1=has_mint and has_quote and bool(free) and has_agent
    s2=is_token and noarg_free and bool(free) and has_agent
    rec.update({'functions':names,'has_mint':has_mint,'has_quote':has_quote,'free_views':free,'has_agent':has_agent,'is_token':is_token,'S1':s1,'S2':s2})
    out.append(rec)
    print(addr,'S1=',s1,'S2=',s2,'mint=',has_mint,'quote=',has_quote,'free=',free,'agent=',has_agent,'token=',is_token)
    time.sleep(0.5)
json.dump(out,open(f"{BASE}/run-2026-11-06-0501-sourcify-shape.json","w"),indent=1)
