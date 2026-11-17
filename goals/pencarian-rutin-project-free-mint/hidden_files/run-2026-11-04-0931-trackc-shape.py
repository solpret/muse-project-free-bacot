import json, urllib.request, urllib.error
def sourcify_abi(a):
    url=f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi"
    req=urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r: return ("verified", json.loads(r.read().decode()).get("abi"))
    except urllib.error.HTTPError as e: return (f"http_{e.code}", None)
    except Exception as e: return (f"error:{type(e).__name__}", None)
FREE_VIEWS={"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeSupply"}
QUOTE={"quote","quoteMint","getQuote","cost","mintCost","mintPrice","price"}
todo=json.load(open('run-2026-11-04-0931-scan-analysis.json'))['todo5c']
out={}
for e in todo:
    a=e['address']; st,abi=sourcify_abi(a)
    if not isinstance(abi,list):
        out[a]={'verified':False,'status':st,'window_mint_count':e['mint_count']}; print(a,'NOT VERIFIED',st,flush=True); continue
    fns={x.get('name') for x in abi if x.get('type')=='function'}
    has_mint=any('mint' in f.lower() for f in fns)
    has_quote=bool(fns & QUOTE)
    fv=sorted(fns & FREE_VIEWS)
    reg=any('agent' in f.lower() or 'registry' in f.lower() for f in fns) or '0x60b9262456de011f7d15a54cdd8c48baa8b022f' in json.dumps(abi).lower()
    sale = has_mint and has_quote and bool(fv) and reg
    out[a]={'verified':True,'has_mint':has_mint,'has_quote':has_quote,'free_views':fv,'registry_ref':reg,'sale_shape':sale,'window_mint_count':e['mint_count']}
    print(a,'SALE' if sale else 'no-shape','mint',has_mint,'quote',has_quote,'free',fv,'reg',reg,flush=True)
json.dump(out,open('run-2026-11-04-0931-trackc-erc20-shape.json','w'),indent=1)
chk=json.load(open('track-c-scan-checked.json'))
if 'checked' not in chk: chk={'checked':chk}
for a in out: chk['checked'][a]={'source':'run-2026-11-04-0931-5c','sale_shape':out[a].get('sale_shape')}
json.dump(chk,open('track-c-scan-checked.json','w'),indent=1)
print('DONE', sum(1 for v in out.values() if v.get('sale_shape')))
