import json, subprocess, re, sys
cands=json.load(open('trackc-134716240-candidates.json'))
out={}
for c in cands:
    a=c['address'].lower()
    url=f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi"
    try:
        r=subprocess.run(['curl','-s','--max-time','20',url],capture_output=True,text=True,timeout=25)
        body=r.stdout
        if 'not_verified' in body or len(body)<50:
            out[a]={'sourcify':'not_verified','mints':c['mint_count']}; print(a,'NOT_VERIFIED',c['mint_count']); continue
        d=json.loads(body)
        abi=d.get('abi') or []
        if isinstance(abi, dict): abi=abi.get('abi',[])
        names=[e['name'] for e in abi if isinstance(e,dict) and 'name' in e]
        s=' '.join(names)
        agent=bool(re.search(r'agentRegistry|AGENT_ID_REGISTRY|agentIdRegistry', s))
        has_mint=any(re.search(r'\bmint',n,re.I) for n in names)
        has_quote=any(re.search(r'quote|cost',n,re.I) for n in names)
        has_free=any(re.search(r'free',n,re.I) for n in names)
        has_token=any(n in names for n in ('name','symbol','decimals','totalSupply'))
        sale = (has_mint and has_quote and has_free and agent) or (has_mint and has_free and has_token and agent)
        out[a]={'sourcify':'verified','agent':agent,'mint':has_mint,'quote':has_quote,'free':has_free,'token':has_token,'sale_shape':sale,'fns':names,'mints':c['mint_count'],'minters':c.get('distinct_minters'),'first_block':c.get('first_block')}
        print(a,'agent=',agent,'mint=',has_mint,'quote=',has_quote,'free=',has_free,'SALE=' ,sale,'mints=',c['mint_count'])
    except Exception as e:
        out[a]={'sourcify':'error','err':str(e)}; print(a,'ERROR',e)
json.dump(out, open('trackc-check-134716240-results.json','w'), indent=1)
