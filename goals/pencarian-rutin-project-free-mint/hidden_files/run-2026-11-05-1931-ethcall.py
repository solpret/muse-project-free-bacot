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
print('BLOCK', blk, 'via', ep)
out={'block':blk}
def C(label, to, sig, args='', dec='u'):
    data=sel(sig)+args
    res, used = call(to, data)
    fn={'u':u,'addr':addr,'b':b,'s':s}[dec]
    val=fn(res) if res is not None else None
    print(f"{label}: {val} (via {used})")
    out[label]=val
    return val

print('--- 0x5b49B06a agent-shaped NFT (FREE_CAP/freeMint/canFreeMint/REGISTRY) ---')
A='0x5b49B06a2E25FcE0BCa865Be70F3C62b6319367a'
C('A.name',A,'name()',dec='s'); C('A.symbol',A,'symbol()',dec='s')
C('A.REGISTRY',A,'REGISTRY()',dec='addr')
C('A.FREE_CAP',A,'FREE_CAP()'); C('A.freeMinted',A,'freeMinted()')
C('A.claimedFree_user',A,'claimedFree(address)',enc_addr(USER))
C('A.canFreeMint_user',A,'canFreeMint(address)',enc_addr(USER),dec='b')
C('A.quote_user1',A,'quote(address,uint256)',enc_addr(USER)+enc_uint(1))
C('A.totalSupply',A,'totalSupply()'); C('A.maxSupply',A,'maxSupply()')
C('A.PRICE',A,'PRICE()'); C('A.paidMinted',A,'paidMinted()')
C('A.owner',A,'owner()',dec='addr')

print('--- 0xe460d44d NFT (mint+quote+AGENT_REGISTRY+spotsLeft) ---')
B='0xe460d44d4A5eb9BEF848C0815d689827f6890D59'
C('B.name',B,'name()',dec='s'); C('B.symbol',B,'symbol()',dec='s')
C('B.AGENT_REGISTRY',B,'AGENT_REGISTRY()',dec='addr')
C('B.totalSupply',B,'totalSupply()'); C('B.totalMinted',B,'totalMinted()')
C('B.MAX_SUPPLY',B,'MAX_SUPPLY()'); C('B.PRICE',B,'PRICE()')
C('B.spotsLeft',B,'spotsLeft()'); C('B.nextTokenId',B,'nextTokenId()')
C('B.mintedBy_user',B,'mintedBy(address)',enc_addr(USER))
C('B.quote_user1',B,'quote(address,uint256)',enc_addr(USER)+enc_uint(1))
C('B.OWNER',B,'OWNER()',dec='addr')

print('--- 0xeC8A897a ERC20 sale? (mint+quote+AGENT_REGISTRY+WEBSITE+TWITTER) ---')
C2='0xeC8A897a0De48a6fbfb83646f790581a2280aDB3'
C('C.name',C2,'name()',dec='s'); C('C.symbol',C2,'symbol()',dec='s')
C('C.decimals',C2,'decimals()'); C('C.totalSupply',C2,'totalSupply()')
C('C.AGENT_REGISTRY',C2,'AGENT_REGISTRY()',dec='addr')
C('C.CAP',C2,'CAP()'); C('C.MAX_SPOTS',C2,'MAX_SPOTS()')
C('C.PER_SPOT',C2,'PER_SPOT()'); C('C.PRICE',C2,'PRICE()')
C('C.spotsLeft',C2,'spotsLeft()'); C('C.totalSpotsMinted',C2,'totalSpotsMinted()')
C('C.mintedBy_user',C2,'mintedBy(address)',enc_addr(USER))
C('C.quote_user1',C2,'quote(address,uint256)',enc_addr(USER)+enc_uint(1))
C('C.WEBSITE',C2,'WEBSITE()',dec='s'); C('C.TWITTER',C2,'TWITTER()',dec='s')
C('C.poolBalance',C2,'poolBalance()'); C('C.OWNER',C2,'OWNER()',dec='addr')
C('C.TREASURY',C2,'TREASURY()',dec='addr')

print('--- ASOC 0x43ceef93 free-lane confirmation ---')
D='0x43cEef9313CB8c4ca3757bA841C44DF40A223205'
C('D.freeUsed',D,'freeUsed()'); C('D.freeClaimed_user',D,'freeClaimed(address)',enc_addr(USER))
C('D.saleEnded',D,'saleEnded()',dec='b'); C('D.totalSold',D,'totalSold()')
json.dump(out, open('run-2026-11-05-1931-ethcall.json','w'), indent=1)
print('saved run-2026-11-05-1931-ethcall.json')
