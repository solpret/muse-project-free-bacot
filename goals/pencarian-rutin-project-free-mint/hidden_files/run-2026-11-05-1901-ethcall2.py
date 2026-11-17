import json, urllib.request
from Crypto.Hash import keccak
USER='0xeb237F6f9FB4e826739F0954e9768914F28b2c2E'
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return '0x'+k.hexdigest()[:8]
def enc_addr(a): return '0'*24 + a[2:].lower()
def enc_uint(n): return '%064x' % n
def call(to, data):
    body=json.dumps({"jsonrpc":"2.0","method":"eth_call","params":[{"to":to,"data":data},"latest"],"id":1}).encode()
    last=None
    for ep in EPS:
        try:
            req=urllib.request.Request(ep, data=body, headers={"Content-Type":"application/json"}, method='POST')
            with urllib.request.urlopen(req, timeout=10) as r:
                j=json.load(r)
            if 'result' in j and j['result'] is not None: return j['result'], ep
            last=j
        except Exception as e:
            last=str(e)
    return None, str(last)
def block():
    body=json.dumps({"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}).encode()
    for ep in EPS:
        try:
            req=urllib.request.Request(ep, data=body, headers={"Content-Type":"application/json"}, method='POST')
            with urllib.request.urlopen(req, timeout=10) as r:
                return int(json.load(r)['result'],16), ep
        except Exception: pass
    return None, None
def u(res):
    if res is None: return None
    try: return int(res,16)
    except Exception: return res
def addr(res):
    if res is None: return None
    return '0x'+res[-40:]
def b(res):
    if res is None: return None
    return int(res,16)!=0
def s(res):
    if res is None: return None
    try:
        h=res[2:]; off=int(h[64:128],16)*2; ln=int(h[off:off+64],16)
        return bytes.fromhex(h[off+64:off+64+ln*2]).decode('utf-8','replace')
    except Exception: return res
blk, ep = block()
print('BLOCK', blk, 'via', ep, flush=True)
out={'block':blk}
def C(label, to, sig, args='', dec='u'):
    data=sel(sig)+args
    res, used = call(to, data)
    fn={'u':u,'addr':addr,'b':b,'s':s}[dec]
    val=fn(res) if res is not None else None
    print(f"{label}: {val}", flush=True)
    out[label]=val
    return val

A='0x3ef2A97Abf2E43182eACAe323B82d2CAC2132C6A'
print('--- FEED-A follow-up ---', flush=True)
C('A.quote_user1',A,'quote(address,uint256)',enc_addr(USER)+enc_uint(1))
C('A.freeLeft_user',A,'freeLeft(address)',enc_addr(USER))
C('A.freeFor_user1',A,'freeFor(address,uint256)',enc_addr(USER)+enc_uint(1))

B='0x5AD10026B4233aC004043DBB9291CFad19b1B3C3'
print('--- FEED-B user slot ---', flush=True)
C('B.freeClaimed_user',B,'freeClaimed(address)',enc_addr(USER),dec='b')

BA='0xa75526d63bd5E3b3e8A65a5f2efEF45072904d04'
print('--- Bound Agent ---', flush=True)
C('BA.name',BA,'name()',dec='s'); C('BA.symbol',BA,'symbol()',dec='s')
C('BA.REGISTRY',BA,'REGISTRY()',dec='addr'); C('BA.AGENT_ID',BA,'AGENT_ID()',dec='addr')
C('BA.totalSupply',BA,'totalSupply()'); C('BA.MAX_SUPPLY',BA,'MAX_SUPPLY()')
C('BA.quote_user1',BA,'quote(address,uint256)',enc_addr(USER)+enc_uint(1))
C('BA.mintOpen',BA,'mintOpen()',dec='b'); C('BA.mintedBy_user',BA,'mintedBy(address)',enc_addr(USER))

NS='0x427aed3f7427b48e45f5e648105aa1b77724cf14'
print('--- Night Shift ---', flush=True)
C('NS.name',NS,'name()',dec='s'); C('NS.symbol',NS,'symbol()',dec='s')
C('NS.AGENT_ID',NS,'AGENT_ID()',dec='addr')
C('NS.totalSupply',NS,'totalSupply()'); C('NS.MAX_SUPPLY',NS,'MAX_SUPPLY()')
C('NS.PRICE',NS,'PRICE()')
C('NS.quote_user1',NS,'quote(address,uint256)',enc_addr(USER)+enc_uint(1))
C('NS.mintOpen',NS,'mintOpen()',dec='b'); C('NS.mintedBy_user',NS,'mintedBy(address)',enc_addr(USER))

OTV='0xfab9c88d25e111edd68a2cca3e0f650863a5bf25'
print('--- OTV ---', flush=True)
C('OTV.name',OTV,'name()',dec='s'); C('OTV.symbol',OTV,'symbol()',dec='s')
C('OTV.totalSupply',OTV,'totalSupply()'); C('OTV.MAX_SUPPLY',OTV,'MAX_SUPPLY()')
C('OTV.FREE_MINT_CAP',OTV,'FREE_MINT_CAP()'); C('OTV.freeMintsClaimed_user',OTV,'freeMintsClaimed(address)',enc_addr(USER))
C('OTV.freeMintsLeft',OTV,'freeMintsLeft()'); C('OTV.freeMintsUsed',OTV,'freeMintsUsed()')
C('OTV.PRICE',OTV,'PRICE()')
C('OTV.quote_user1',OTV,'quote(address,uint256)',enc_addr(USER)+enc_uint(1))

json.dump(out, open('run-2026-11-05-1901-ethcall2.json','w'), indent=1)
print('saved run-2026-11-05-1901-ethcall2.json', flush=True)
