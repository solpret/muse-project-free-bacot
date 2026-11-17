import json,os,subprocess
H=os.path.expanduser('~/workspace/goals/pencarian-rutin-project-free-mint/hidden_files')
scan=json.load(open(f'{H}/onchain-scan-2026-11-03-1301.json'))
checked=json.load(open(f'{H}/track-c-scan-checked.json'))
checked_map=checked.get('checked',{}) if isinstance(checked,dict) else {}
checked_set={k.lower() for k in checked_map.keys()}
erc=sorted(scan['erc20_mint_contracts_list'], key=lambda x:-x['mint_count'])
cands=[e for e in erc if e['mint_count']>=10 and e['address'].lower() not in checked_set]
print('erc20>=10:', sum(1 for e in erc if e['mint_count']>=10), 'unchecked:', len(cands))
FREE_VIEWS={'freeSharesRemaining','freeClaimed','freeFor','freeLeft','freeUsed','freeAvailable','freeSharePoolExhausted','freeSharesClaimed','freeMinted','freeCardsRemaining'}
AGENT={'agentId','agentRegistry','registry','getAgentId','agentGate','AgentGate','AGENT_ID','AGENT_ID_REGISTRY','agentIdOf','hasAgentId','AGENT_REGISTRY'}
out=[]
for e in cands[:20]:
    a=e['address']
    try:
        raw=subprocess.run(["curl","-sL","--max-time","20",f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi"],capture_output=True,text=True).stdout
        meta=json.loads(raw); abi=meta.get('abi',[])
        fns={}
        for fn in abi:
            if fn.get('type')=='function': fns.setdefault(fn['name'],[]).append(fn)
        names=set(fns)
        has_mint=any(n.lower().startswith('mint') for n in names)
        has_quote=bool(names & {'quote','cost','getQuote','mintCost','price','getPrice'})
        free_views=sorted(names & FREE_VIEWS)
        agent_ref=bool(names & AGENT)
        is_token=bool(names & {'name','symbol','decimals','totalSupply'})
        mintfree='mintFree' in fns and any(len(x.get('inputs',[]))==0 for x in fns['mintFree'])
        s1=has_mint and has_quote and bool(free_views) and agent_ref
        s2=is_token and mintfree and bool(names & {'freeClaimed','freeMinted'}) and bool(names & {'FREE_SLOTS','FREE_SUPPLY'}) and agent_ref
        status='PASS' if (s1 or s2) else 'not_verified' if not abi else 'fail-shape'
        print(a, 'mint_count', e['mint_count'], 'S1', s1, 'S2', s2, 'mint', has_mint, 'quote', has_quote, 'free', free_views, 'agent', agent_ref, 'token', is_token, flush=True)
        out.append({'address':a,'mint_count':e['mint_count'],'distinct_minters':e['distinct_minters'],'S1':s1,'S2':s2,'status':status,'functions':sorted(names) if abi else []})
        if abi: checked_map[a]=True
    except Exception as ex:
        print(a, 'FETCH-FAIL', type(ex).__name__, str(ex)[:120], flush=True)
        out.append({'address':a,'mint_count':e['mint_count'],'status':'fetch-fail','error':str(ex)[:120]})
json.dump(out, open(f'{H}/run-2026-11-03-1301-trackc-5c.json','w'), indent=1)
checked['checked']=checked_map
json.dump(checked, open(f'{H}/track-c-scan-checked.json','w'), indent=1)
print('checked total now:', len(checked_map))
