import json, urllib.request, time
new=json.load(open('run-2026-11-04-2001-trackc-new.json'))
FREE=['freeSharesRemaining','freeClaimed','freeFor','freeLeft','freeUsed','freeAvailable','freeSharePoolExhausted','freeSharesClaimed','freeMinted','freeClaimedBy','freePlotsRemaining','freeCap','freeSold']
out=[]
for e in new:
    a=e['address']
    try:
        req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi",headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req,timeout=20) as r: d=json.load(r)
        abi=d.get('abi') or []
        fns=sorted({x.get('name') for x in abi if x.get('type')=='function' and x.get('name')})
        low=[f.lower() for f in fns]
        mint=any(f=='mint' or f=='mintfree' or f=='claimfree' or f.startswith('mint') for f in low)
        quote=any('quote' in f or 'cost' in f for f in low)
        fv=[f for f in fns if f in FREE or 'free' in f.lower()]
        agent=any('agent' in f or 'registry' in f for f in low)
        token=any(f in low for f in ['name','symbol','decimals','totalsupply'])
        s1 = mint and quote and bool(fv) and agent
        s2 = token and any(f in low for f in ['mintfree','claimfree']) and bool(fv) and agent
        out.append({"addr":a,"mint_count":e['mint_count'],"verified":True,"mint":mint,"quote":quote,"free_views":fv,"agent":agent,"token":token,"S1":s1,"S2":s2,"n_fn":len(fns)})
        print(a, "S1",s1,"S2",s2,"mint",mint,"quote",quote,"free",fv,"agent",agent,flush=True)
    except Exception as ex:
        out.append({"addr":a,"mint_count":e['mint_count'],"verified":False,"error":str(ex)[:120]})
        print(a,"ERR",str(ex)[:120],flush=True)
    time.sleep(0.3)
json.dump(out,open('run-2026-11-04-2001-trackc-shape.json','w'),indent=1)
print("DONE")
