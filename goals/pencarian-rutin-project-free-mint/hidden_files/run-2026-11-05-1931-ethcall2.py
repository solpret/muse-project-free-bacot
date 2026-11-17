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
            with urllib.request.urlopen(req, timeout=15) as r:
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
            with urllib.request.urlopen(req, timeout=15) as r:
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
def s(res):
    if res is None: return None
    try:
        h=res[2:]; off=int(h[64:128],16)*2; ln=int(h[off:off+64],16)
        return bytes.fromhex(h[off+64:off+64+ln*2]).decode('utf-8','replace')
    except Exception: return res
blk, ep = block()
print('BLOCK', blk, 'via', ep)
out={'block':blk}
def C(label, to, sig, args='', dec='u'):
    data=sel(sig)+args
    res, used = call(to, data)
    fn={'u':u,'addr':addr,'s':s}[dec]
    val=fn(res) if res is not None else None
    print(f"{label}: {val} (via {used})")
    out[label]=val
    return val

A='0x5b49B06a2E25FcE0BCa865Be70F3C62b6319367a'
print('--- Mossminds quote(1) retry ---')
C('A.quote_1',A,'quote(uint256)',enc_uint(1))
C('A.FREE_PCT',A,'FREE_PCT()')
C('A.tokenURI_1',A,'tokenURI(uint256)',enc_uint(1),dec='s')
C('A.ownerOf_1',A,'ownerOf(uint256)',enc_uint(1),dec='addr')
B='0xe460d44d4A5eb9BEF848C0815d689827f6890D59'
print('--- Aether Core quote(1) + supply holders ---')
C('B.quote_1',B,'quote(uint256)',enc_uint(1))
C('B.ownerOf_1',B,'ownerOf(uint256)',enc_uint(1),dec='addr')
C('B.balanceOf_owner',B,'balanceOf(address)',enc_addr('0xe9d9dec36ce804e44fdd5e19f09e2364cbf64ed5'))
C('B.balanceOf_treasury',B,'balanceOf(address)',enc_addr('0xe9d9dec36ce804e44fdd5e19f09e2364cbf64ed5'))
C('B.tokenURI_1',B,'tokenURI(uint256)',enc_uint(1),dec='s')
C2='0xeC8A897a0De48a6fbfb83646f790581a2280aDB3'
print('--- Ember Byte quote(1) ---')
C('C.quote_1',C2,'quote(uint256)',enc_uint(1))
C('C.balanceOf_pool',C2,'balanceOf(address)',enc_addr(C2))
json.dump(out, open('run-2026-11-05-1931-ethcall2.json','w'), indent=1)
print('saved run-2026-11-05-1931-ethcall2.json')
