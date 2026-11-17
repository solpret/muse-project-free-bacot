import json, sys
sys.path.insert(0, '.')
exec(open('shape-check-1201.py').read().split('def main')[0].replace('sys.path.insert(0, "/home/hatch/workspace/fast_exec")','sys.path.insert(0, "/home/hatch/workspace/fast_exec")'))
addrs = ["0x4EbB70fC9FD26e009f11fE176540C4C8aebB4732","0x5bc4fb61270c2628c93bf507c4ba125b868d34ff","0x61df6496d708ec11e7a9261005f788cf7cac818b","0x8269Ea1629644219a88dbB053D34E8e877596B00"]
results=[]
for addr in addrs:
    status, abi = sourcify_abi(addr)
    fns=[it for it in (abi or []) if isinstance(it,dict) and it.get('type')=='function']
    names=[f.get('name','') for f in fns]; lower=[n.lower() for n in names]
    has_mint=any('mint' in n for n in lower)
    has_quote=any(any(q in n for q in QUOTE_FNS) for n in lower)
    free_views=[n for n in names if n.lower() in FREE_SHARE_VIEWS]
    gate_names=[n for n in names if 'agentregistry' in n.lower() or 'agentgate' in n.lower() or 'agentid' in n.lower()]
    try:
        code=rpc_call('eth_getCode',[addr,'latest'])
        reg_bytes=REGISTRY_BYTES in code[2:].lower() if isinstance(code,str) and len(code)>2 else False
    except Exception as e:
        reg_bytes=f'error:{e}'
    registry_ref=bool(gate_names) or reg_bytes is True
    s1=has_mint and has_quote and bool(free_views) and registry_ref
    token_fns={'name','symbol','decimals','totalsupply'}
    has_token=token_fns <= set(lower)
    noarg=False
    for f in fns:
        if f.get('name','').lower() in ('mintfree','freemint','claimfree','mintfreeshare') and len(f.get('inputs',[]))==0:
            noarg=True
    s2=has_token and noarg and bool(free_views) and registry_ref
    r={'address':addr,'sourcify':status,'has_mint':has_mint,'has_quote':has_quote,'free_views':free_views,'gate_names':gate_names,'registry_bytes':reg_bytes,'S1':s1,'S2':s2,'has_token_fns':has_token,'noarg_free_mint':noarg,'fns':names[:40]}
    results.append(r)
    print(addr, 'sourcify=',status,'mint=',has_mint,'quote=',has_quote,'free=',free_views,'gate=',gate_names,'reg_bytes=',reg_bytes,'S1=',s1,'S2=',s2, flush=True)
json.dump(results, open('boltbook-1201-shape.json','w'), indent=1)
print('HITS:', [r['address'] for r in results if r['S1'] or r['S2']])
