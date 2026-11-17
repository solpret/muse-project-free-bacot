import sys, json
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return '0x'+k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64,'0')
def enc_u(n): return format(n,'064x')
USER='0xeb237F6f9FB4e826739F0954e9768914F28b2c2E'
TARGETS={
 'Alchemister-0xCafEEDDF':'0xCafEEDDF3C15C5CD9A63D97021efDe845e1781Bc',
 '0x1a904Da7':'0x1a904Da7ebBE7708D79d52DB594A73EbB7d2875B',
 'Zigzoo':'0x09ada5a12293c30d75b97c56e34967e8a4326a3c',
 'Jinli Agents':'0x0f45b52f80a3a42e56e66Cd8CFd1A65895c34496',
 '0xbd4B4e71':'0xbd4B4e7189ae9356514664146b0eD683601200A9',
 'Undead NFTs':'0xC92bEc9160506065E515b225721a749Fad7664E9',
}
VIEWS=['totalSupply()','FREE_SUPPLY()','FREE_PER_WALLET()','MAX_SUPPLY()','freeClaimed()','freeMinted()','freeLeft()','freeFor()','freeSupply()','mintOpen()','PRICE()','owner()']
USERVIEWS=['freeUsed(address)','mintedBy(address)','freeClaimed(address)','balanceOf(address)']
out={}
for name,a in TARGETS.items():
    d={}
    for v in VIEWS:
        try:
            r=batch([('eth_call',[{'to':a,'data':sel(v)},'latest'])], endpoint='https://bsc-dataseed2.bnbchain.org/', timeout=10)[0]
            d[v]=int(r,16) if isinstance(r,str) and r.startswith('0x') and len(r)<=66 else r
        except Exception as e: d[v]='ERR'
    for v in USERVIEWS:
        try:
            r=batch([('eth_call',[{'to':a,'data':sel(v)+enc_addr(USER)},'latest'])], endpoint='https://bsc-dataseed2.bnbchain.org/', timeout=10)[0]
            d[v+'_user']=int(r,16) if isinstance(r,str) and r.startswith('0x') and len(r)<=66 else r
        except Exception as e: d[v+'_user']='ERR'
    try:
        r=batch([('eth_call',[{'to':a,'data':sel('quote(uint256)')+enc_u(1)},'latest'])], endpoint='https://bsc-dataseed2.bnbchain.org/', timeout=10)[0]
        d['quote_1']=int(r,16) if isinstance(r,str) and r.startswith('0x') and len(r)<=66 else r
    except Exception as e: d['quote_1']='ERR'
    out[name]=d
    fc=d.get('freeClaimed()'); fs=d.get('FREE_SUPPLY()')
    fp=(fc/fs*100) if isinstance(fc,int) and isinstance(fs,int) and fs else None
    print(name, 'totalSupply=',d.get('totalSupply()'),'FREE_SUPPLY=',fs,'freeClaimed=',fc,'free%=',round(fp,1) if fp is not None else None,'freeMinted=',d.get('freeMinted()'),'freeLeft=',d.get('freeLeft()'),'mintOpen=',d.get('mintOpen()'),'PRICE=',d.get('PRICE()'),'quote1=',d.get('quote_1'),'freeUsed_user=',d.get('freeUsed(address)_user'),'mintedBy_user=',d.get('mintedBy(address)_user'),'freeClaimed_user=',d.get('freeClaimed(address)_user'),'bal_user=',d.get('balanceOf(address)_user'),'owner=',d.get('owner()'), flush=True)
json.dump(out, open('run-2026-11-08-1431-promocheck.json','w'), indent=1)
