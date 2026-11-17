import json, urllib.request
from Crypto.Hash import keccak
RPCS=['https://bsc-dataseed1.bnbchain.org','https://bsc.publicnode.com']
USER='0xeb237F6f9FB4e826739F0954e9768914F28b2c2E'
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return '0x'+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,'0')
def enc_uint(n): return format(n,'064x')
def raw(to,data):
    for rpc in RPCS:
        try:
            body=json.dumps({'jsonrpc':'2.0','id':1,'method':'eth_call','params':[{'to':to,'data':data},'latest']}).encode()
            req=urllib.request.Request(rpc,data=body,headers={'Content-Type':'application/json'})
            with urllib.request.urlopen(req,timeout=8) as r: out=json.load(r)
            if 'error' in out: return None
            v=out['result']
            if not v or v=='0x': return None
            try: return int(v,16)
            except Exception: return v
        except Exception: continue
    return None
def call(to,sig,args=''): return raw(to,sel(sig)+args)
def blk():
    for rpc in RPCS:
        try:
            body=json.dumps({'jsonrpc':'2.0','id':1,'method':'eth_blockNumber','params':[]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={'Content-Type':'application/json'})
            with urllib.request.urlopen(req,timeout=8) as r: return int(json.load(r)['result'],16)
        except Exception: continue
    return None
b=blk(); print('BLOCK',b)
AB='0x08393dad165d90e7258501fE1dfb5F3498644011'
GA='0xa388bba8e4ed07043bae8cc68a00e9aec42f72f4'
def name_sym(to):
    n=raw(to,sel('name()')); s=raw(to,sel('symbol()'))
    def dec(v):
        if isinstance(v,int): return v
        if isinstance(v,str) and v.startswith('0x'):
            try:
                bb=bytes.fromhex(v[2:])
                # string ABI: offset 32, len at 64
                ln=int.from_bytes(bb[32:64],'big')
                return bb[64:64+ln].decode('utf-8','replace')
            except Exception: return v
        return v
    return dec(n),dec(s)
out={'block':b}
for label,to in [('AgentBox',AB),('Galaxy',GA)]:
    d={'address':to}
    d['name'],d['symbol']=name_sym(to)
    d['totalSupply']=call(to,'totalSupply()')
    d['totalMinted']=call(to,'totalMinted()')
    d['MAX_SUPPLY']=call(to,'MAX_SUPPLY()')
    d['freeClaimed']=call(to,'freeClaimed()')
    d['freeMinted']=call(to,'freeMinted()')
    d['FREE_SUPPLY']=call(to,'FREE_SUPPLY()')
    d['balanceOf_user']=call(to,'balanceOf(address)',enc(USER))
    d['mintedBy_user']=call(to,'mintedBy(address)',enc(USER))
    d['freeUsed_user']=call(to,'freeUsed(address)',enc(USER))
    d['quote_user_1']=call(to,'quote(address,uint256)',enc(USER)+enc_uint(1))
    d['mintOpen']=call(to,'mintOpen()')
    d['owner']=call(to,'owner()')
    d['AGENT_ID']=call(to,'AGENT_ID()')
    d['registry']=call(to,'registry()')
    print(label,d,flush=True)
    out[label]=d
json.dump(out,open('run-2026-11-05-2031-agentbox-galaxy-probe.json','w'),indent=1)
print('DONE')
