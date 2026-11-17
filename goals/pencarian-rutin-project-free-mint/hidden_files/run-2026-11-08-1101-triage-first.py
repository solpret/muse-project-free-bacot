import sys, json, subprocess
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch as _batch
from Crypto.Hash import keccak
REG_BYTES="60b9262456de011f7d15a54cdd8c48baaa8b022f"
def sel(s): return "0x"+keccak.new(digest_bits=256, data=s.encode()).hexdigest()[:8]
def ti(v):
    try: return int(v,16)
    except: return None
def call(addr, data, ep="https://bsc-dataseed1.bnbchain.org/"):
    try:
        return _batch([("eth_call",[{"to":addr,"data":data},"latest"])],endpoint=ep,timeout=15)[0]
    except Exception as e:
        return "ERR:"+str(e)[:80]
def code(addr, ep="https://bsc-dataseed1.bnbchain.org/"):
    try:
        return _batch([("eth_getCode",[addr,"latest"])],endpoint=ep,timeout=15)[0]
    except Exception as e:
        return "ERR:"+str(e)[:80]
first=json.load(open('run-2026-11-08-1101-firstseen.json'))
out=[]
for c in first:
    a=c['address']
    cd=code(a)
    reg = (REG_BYTES in cd[2:].lower()) if isinstance(cd,str) and cd.startswith("0x") else None
    d=dict(c)
    d['registry_bytes']=reg
    d['code_len']=len(cd) if isinstance(cd,str) else None
    d['totalSupply']=ti(call(a, sel("totalSupply()")))
    d['totalMinted']=ti(call(a, sel("totalMinted()")))
    d['name_call']=call(a, sel("name()"))
    # sourcify via curl
    r=subprocess.run(["curl","-sL","--max-time","20",f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi"],capture_output=True,text=True).stdout
    try:
        meta=json.loads(r); abi=meta.get("abi",[])
        fns=sorted({e["name"] for e in abi if e.get("type")=="function"})
        d['sourcify2']='verified' if abi else 'empty'
        d['fns']=fns
        d['free_fns']=[f for f in fns if 'free' in f.lower() and not f.lower().startswith('freeze')]
        d['mint_fns']=[f for f in fns if 'mint' in f.lower()]
        d['agent_fns']=[f for f in fns if f in ("agentId","agentRegistry","registry","REGISTRY","getAgentId","agentGate","AgentGate","AGENT_ID","AGENT_ID_REGISTRY","agentIdOf","AGENT_REGISTRY","hasAgentId")]
    except Exception as e:
        d['sourcify2']=f'error {type(e).__name__}'
    out.append(d)
    print(json.dumps(d, indent=1))
json.dump(out, open('run-2026-11-08-1101-triage-first.json','w'), indent=1)
# 5c selection
scan=json.load(open('onchain-scan-2026-11-08-1101.json'))
checked=json.load(open('track-c-scan-checked.json'))
checked_set={k.lower() for k in (checked if isinstance(checked,dict) else {})}
print('checked file type:', type(checked), 'n:', len(checked_set))
cands=[e for e in scan['erc20_mint_contracts_list'] if e['mint_count']>=10 and e['address'].lower() not in checked_set]
cands.sort(key=lambda e:-e['mint_count'])
print('5c candidates mint>=10 not checked:', len(cands), 'to check (cap 20):', len(cands[:20]))
for e in cands[:20]:
    print('  ', e['address'], 'mint_count=', e['mint_count'], 'minters=', e['distinct_minters'])
json.dump(cands[:20], open('run-2026-11-08-1101-5c.json','w'), indent=1)
