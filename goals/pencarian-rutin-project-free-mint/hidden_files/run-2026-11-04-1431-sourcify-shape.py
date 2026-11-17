import json, urllib.request
feed=json.load(open('run-2026-11-04-1431-sourcify.json'))
items=feed if isinstance(feed,list) else feed.get('results',feed)
cutoff="2026-11-04T07:03:43Z"
new=[it for it in items if it.get('verifiedAt','')>cutoff]
print('new vs cutoff', len(new))
FREE=['freeClaimed','freeFor','freeLeft','freeUsed','freeMinted','freeAvailable','freeSharesRemaining','freeSharesClaimed','freeSharePoolExhausted','freeSupply','freeLeft','freeFor']
out={}
for it in new:
    a=it['address']; url=f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi"
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req,timeout=20) as r: d=json.load(r)
        abi=d.get('abi') or (d.get('stdJson') or {}).get('abi') or []
        names=[f.get('name','') for f in abi if isinstance(f,dict) and f.get('type')=='function']
        free=[n for n in names if any(f.lower() in n.lower() for f in ['freeClaimed','freeFor','freeLeft','freeUsed','freeMinted','freeAvailable','freeShares'])]
        mint=any('mint' in n.lower() or 'claim' in n.lower() for n in names)
        agent=any('agent' in n.lower() or 'registry' in n.lower() for n in names)
        out[a]={'verifiedAt':it.get('verifiedAt'),'nfuncs':len(names),'mint_or_claim':mint,'free_views':free,'agent_substr':agent,'names':names}
        print(a, it.get('verifiedAt'), 'mint',mint,'free',free,'agent',agent,'n',len(names), flush=True)
    except Exception as e:
        out[a]={'verifiedAt':it.get('verifiedAt'),'error':str(e)}
        print(a,'ERROR',e, flush=True)
json.dump(out,open('run-2026-11-04-1431-sourcify-shape.json','w'),indent=1)
print('DONE')
