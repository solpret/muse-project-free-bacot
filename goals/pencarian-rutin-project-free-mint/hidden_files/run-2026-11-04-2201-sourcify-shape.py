import json, urllib.request, time
feed=json.load(open('run-2026-11-04-2201-sourcify.json'))['results']
FREE=['freeSharesRemaining','freeClaimed','freeFor','freeLeft','freeUsed','freeAvailable','freeSharePoolExhausted','freeSharesClaimed','freeMinted','freeClaimedBy','freePlotsRemaining']
out=[]
for it in feed:
    a=it['address']
    try:
        req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi",headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req,timeout=20) as r: d=json.load(r)
        abi=d.get('abi') or (d.get('contract') or {}).get('abi') or []
        fns=sorted({e.get('name') for e in abi if e.get('type')=='function' and e.get('name')})
        low=[f.lower() for f in fns]
        mint=any('mint' in f for f in low)
        quote=any('quote' in f or 'cost' in f or f=='price' for f in low)
        fv=[f for f in fns if f in FREE or 'free' in f.lower()]
        agent=any('agent' in f.lower() or 'registry' in f.lower() for f in fns)
        out.append({"addr":a,"verified":True,"verifiedAt":it.get('verifiedAt'),"n_fn":len(fns),"mint":mint,"quote":quote,"free_views":fv,"agent_fn":agent,"fns":fns})
        print(a, "mint",mint,"quote",quote,"free",fv,"agent",agent,flush=True)
    except Exception as e:
        out.append({"addr":a,"verified":False,"error":str(e)[:120]})
        print(a,"ERR",str(e)[:120],flush=True)
    time.sleep(0.3)
json.dump(out,open('run-2026-11-04-2201-sourcify-shape.json','w'),indent=1)
print("DONE",len(out))
