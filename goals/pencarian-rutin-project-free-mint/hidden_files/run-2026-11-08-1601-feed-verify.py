import sys, json
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _post as _fr_post
from Crypto.Hash import keccak
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return '0x'+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,'0')
USER='0xeb237F6f9FB4e826739F0954e9768914F28b2c2E'
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed.binance.org/"]
def to_int(v):
    try:
        if v is None or v=='0x': return None
        return int(v,16)
    except Exception: return None
def batch(addr, views):
    calls=[]; keys=[]
    for i,sig in enumerate(views):
        base=sig.split('(')[0]
        if '(address)' in sig: data=sel(sig)+enc(USER); key=base+'_user'
        elif '(uint256)' in sig: data=sel(sig)+'0'*63+'1'; key=base+'_1'
        else: data=sel(sig); key=base
        calls.append({'jsonrpc':'2.0','id':i+1,'method':'eth_call','params':[{'to':addr,'data':data},'latest']})
        keys.append(key)
    for ep in EPS:
        try:
            out=_fr_post(ep, calls, timeout=10, retries=0)
            if not isinstance(out,list) or len(out)!=len(calls): continue
            res={}
            for item,key in zip(out,keys):
                if isinstance(item,dict) and 'error' in item: res[key]=None
                else: res[key]=to_int(item.get('result')) if isinstance(item,dict) else None
            return res
        except Exception: continue
    return None
def raw(addr, sig):
    # returns raw hex (for address-returning views)
    for ep in EPS:
        try:
            out=_fr_post(ep, {'jsonrpc':'2.0','id':1,'method':'eth_call','params':[{'to':addr,'data':sel(sig)},'latest']}, timeout=10, retries=0)
            if isinstance(out,dict) and 'result' in out: return out['result']
        except Exception: continue
    return None
VIEWS=["name()","symbol()","totalSupply()","totalMinted()","FREE_SUPPLY()","freeMinted()","freeClaimed()","MAX_SUPPLY()","mintOpen()","freeClaimed(address)","balanceOf(address)","quote(uint256)"]
d=json.load(open('run-2026-11-08-1601-feed-shape.json'))
out={}
for a,info in d.items():
    if not info.get('hasMint'): continue
    r=batch(a, VIEWS)
    reg={}
    for fn in ['agentRegistry()','AGENT_ID_REGISTRY()','AGENT_REGISTRY()','agentId()']:
        v=raw(a,fn)
        reg[fn]=('0x'+v[-40:]) if v and len(v)>=42 else v
    out[a]={'views':r,'registry':reg}
    print(a, json.dumps(r), json.dumps(reg), flush=True)
json.dump(out, open('run-2026-11-08-1601-feed-verify.json','w'), indent=1)
print('DONE')
