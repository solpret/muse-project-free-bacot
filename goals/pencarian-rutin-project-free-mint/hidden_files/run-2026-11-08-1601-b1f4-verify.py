import sys, json, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _post as _fr_post
from Crypto.Hash import keccak
from ankr import ankr_post
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return '0x'+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,'0')
USER='0xeb237F6f9FB4e826739F0954e9768914F28b2c2E'
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed.binance.org/"]
A='0xB1f4f9c3Bb8533064fFec75dFab1Be88833b3a32'
def call(addr, data):
    for ep in EPS:
        try:
            out=_fr_post(ep, {'jsonrpc':'2.0','id':1,'method':'eth_call','params':[{'to':addr,'data':data},'latest']}, timeout=10, retries=0)
            if isinstance(out,dict) and 'result' in out: return out['result']
            if isinstance(out,dict) and 'error' in out: return 'ERR:'+str(out['error'])[:80]
        except Exception as e: continue
    return 'ERR:all-fail'
def dec_str(h):
    try:
        b=bytes.fromhex(h[2:])
        ln=int.from_bytes(b[64:96],'big')
        return b[96:96+ln].decode()
    except Exception as e: return 'DECODE-ERR:'+str(e)
def dec_int(h):
    try: return int(h,16)
    except Exception: return h
out={}
out['name']=dec_str(call(A, sel('name()')))
out['symbol']=dec_str(call(A, sel('symbol()')))
for v in ['AGENT_ID()','FREE_SUPPLY()','MAX_SUPPLY()','PAID_SUPPLY()','PAID_PER_WALLET()','PRICE_1()','PRICE_2()','STEP()','currentPrice()','freeMinted()','paidMinted()','totalSupply()','mintStart()','rarityLeft()','owner()']:
    r=call(A, sel(v))
    out[v]=r if isinstance(r,str) and r.startswith('ERR') else dec_int(r)
    print(v, '=', out[v], flush=True)
print('name =', out['name'], '| symbol =', out['symbol'], flush=True)
for v in ['claimedFree(address)','paidBy(address)','balanceOf(address)']:
    r=call(A, sel(v)+enc(USER))
    out[v+'_user']=r if isinstance(r,str) and r.startswith('ERR') else dec_int(r)
    print(v, '(user) =', out[v+'_user'], flush=True)
r=call(A, sel('quote(uint256)')+'0'*63+'1')
out['quote_1']=r if isinstance(r,str) and r.startswith('ERR') else dec_int(r)
print('quote(1) =', out['quote_1'], flush=True)
r=call(A, sel('tokenURI(uint256)')+'0'*63+'1')
out['tokenURI_1_raw']=r
print('tokenURI(1) raw =', (r or '')[:200], flush=True)
# stats()
r=call(A, sel('stats()'))
out['stats_raw']=r
print('stats() raw =', (r or '')[:300], flush=True)
# first mint via Ankr: Transfer from zero, address-filtered, walk back in 2000-block chunks from head
head=None
for ep in EPS:
    try:
        o=_fr_post(ep, {'jsonrpc':'2.0','id':1,'method':'eth_blockNumber','params':[]}, timeout=10, retries=0)
        head=int(o['result'],16); break
    except Exception: continue
print('HEAD', head, flush=True)
TRANSFER='0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
ZERO='0x'+'00'*32
first=None
to_block=head
for i in range(12):
    frm=max(0,to_block-1999)
    try:
        body=ankr_post('ankr_getLogs', {'blockchain':'bsc','fromBlock':hex(frm),'toBlock':hex(to_block),'pageSize':1000,'decodeLogs':False,'topics':[TRANSFER, ZERO],'address':A}, timeout=30)
        logs=(body.get('result') or {}).get('logs',[])
    except Exception as e:
        print('walkback chunk',frm,to_block,'ERR',str(e)[:100],flush=True); logs=[]
    print('walkback',frm,to_block,'logs',len(logs),flush=True)
    if logs:
        first=min(logs, key=lambda l: int(l['blockNumber'],16))
        print('EARLIEST in chunk block', int(first['blockNumber'],16), flush=True)
        break
    to_block=frm-1
    if to_block<=0: break
out['first_mint_log']=first
out['head']=head
json.dump(out, open('run-2026-11-08-1601-b1f4-verify.json','w'), indent=1)
print('DONE')
