import json, urllib.request, time, subprocess
REG="0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
d=json.load(open('run-2026-11-08-1831-feed.json'))
out={}
for it in d.get('results',[]):
    a=it['address']
    url=f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi"
    try:
        req=urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as r:
            j=json.load(r)
    except Exception as e:
        try:
            cp=subprocess.run(['curl','-s','--max-time','20',url],capture_output=True,text=True)
            j=json.loads(cp.stdout)
        except Exception as e2:
            out[a]={'error':str(e)[:120]}; print(a,'ERR',str(e)[:80],flush=True); continue
    abi=j.get('abi') or []
    fns=[f.get('name','') for f in abi if f.get('type')=='function']
    low=[f.lower() for f in fns]
    has_mint=any(n.startswith('mint') or n in ('freeMint','mintFree','claimFreeMiner') for n in fns)
    free_views=[n for n in fns if n.lower().startswith('free') or n in ('freeMinted','freeClaimed','freeLeft','freeSupply','FREE_SUPPLY','FREE_SLOTS','FREE_CAP','FREE_POOL')]
    has_quote=any(n.lower().startswith('quote') or n.lower() in ('cost','price','mintcost','getprice') for n in fns)
    reg_ref = REG.lower() in json.dumps(j).lower()
    out[a]={'verifiedAt':it.get('verifiedAt'),'match':it.get('match'),'nFns':len(fns),
            'hasMint':has_mint,'freeViews':free_views,'hasQuote':has_quote,'registryRef':reg_ref,
            'fns':fns}
    print(a, '| fns',len(fns),'| mint',has_mint,'| free',free_views,'| quote',has_quote,'| reg',reg_ref,flush=True)
    time.sleep(0.5)
json.dump(out, open('run-2026-11-08-1831-feed-shape.json','w'), indent=1)
print('DONE')
