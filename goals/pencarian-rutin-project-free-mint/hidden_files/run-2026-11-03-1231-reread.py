import json,sys,os
sys.path.insert(0,"/home/hatch/workspace/fast_exec")
from fast_rpc import race, call_many
from Crypto.Hash import keccak
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return k.hexdigest()[:8]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"; pad=USER[2:].rjust(64,'0')
H=os.path.expanduser('~/workspace/goals/pencarian-rutin-project-free-mint/hidden_files')
s=json.load(open(f'{H}/onchain-snapshot.json'))
targets=[]
for k,v in s['contracts'].items():
    if v.get('status','').startswith('early-lead-reported') and (v.get('freePctVerified') or 0)>=25:
        targets.append((k,v['address']))
for k in ('Mechfarm','Deepvane','Neuroveil'):
    if k in s['contracts']: targets.append((k,s['contracts'][k]['address']))
# dedupe preserve order
seen=set(); tg=[]
for k,a in targets:
    if a.lower() not in seen: seen.add(a.lower()); tg.append((k,a))
views=[("totalSupply()",""),("freeClaimed()",""),("FREE_SUPPLY()",""),("totalMinted()",""),("freeMinted()",""),("mintedBy(address)",pad),("freeUsed(address)",pad),("balanceOf(address)",pad)]
out={"block":None}
try: out["block"]=int(race("eth_blockNumber",[]),16)
except Exception as e: out["block_error"]=str(e)[:120]
for name,addr in tg:
    calls=[]
    for sig,args in views:
        calls.append((addr,"0x"+sel(sig)+args))
    try:
        res=call_many(calls)
    except Exception as e:
        res=[f"ERR:{type(e).__name__}"]*len(calls)
    d={}
    for (sig,_),r in zip(views,res):
        if isinstance(r,str) and r.startswith("0x") and len(r)>=66:
            try: d[sig]=int(r,16)
            except: d[sig]=None
        else: d[sig]=None
    out[name]={"address":addr, **d}
    print(name, d)
json.dump(out, open(f'{H}/run-2026-11-03-1231-reread.json','w'), indent=1)
print("DONE", len(tg), "block", out["block"])
