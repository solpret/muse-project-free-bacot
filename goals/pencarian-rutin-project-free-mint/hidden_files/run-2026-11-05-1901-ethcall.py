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
print('BLOCK', blk, 'via', ep)
out={'block':blk}
def C(label, to, sig, args='', dec='u'):
    data=sel(sig)+args
    res, used = call(to, data)
    fn={'u':u,'addr':addr,'b':b,'s':s}[dec]
    val=fn(res) if res is not None else None
    print(f"{label}: {val} (raw={res} via {used})")
    out[label]=val
    return val

A='0x3ef2A97Abf2E43182eACAe323B82d2CAC2132C6A'
print('--- FEED-A 0x3ef2A97A agent-shaped NFT ---')
C('A.name',A,'name()',dec='s'); C('A.symbol',A,'symbol()',dec='s')
C('A.AGENT_ID',A,'AGENT_ID()',dec='addr')
C('A.FREE_SUPPLY',A,'FREE_SUPPLY()'); C('A.freeClaimed',A,'freeClaimed()')
C('A.freeLeft',A,'freeLeft()'); C('A.freeFor_user',A,'freeFor(address)',enc_addr(USER))
C('A.freeUsed_user',A,'freeUsed(address)',enc_addr(USER))
C('A.totalSupply',A,'totalSupply()'); C('A.totalMinted',A,'totalMinted()')
C('A.MAX_SUPPLY',A,'MAX_SUPPLY()'); C('A.PRICE',A,'PRICE()')
C('A.quote1',A,'quote(uint256)',enc_uint(1)); C('A.mintOpen',A,'mintOpen()',dec='b')
C('A.mintedBy_user',A,'mintedBy(address)',enc_addr(USER))

B='0x5AD10026B4233aC004043DBB9291CFad19b1B3C3'
print('--- FEED-B 0x5AD10026 AGC-related sale ---')
C('B.AGENT_REGISTRY',B,'AGENT_REGISTRY()',dec='addr')
C('B.token',B,'token()',dec='addr'); C('B.saleStart',B,'saleStart()')
C('B.freeRemaining',B,'freeRemaining()'); C('B.freeClaimed',B,'freeClaimed()')
C('B.freeSharesClaimed',B,'freeSharesClaimed()'); C('B.isLive',B,'isLive()',dec='b')
C('B.pair',B,'pair()',dec='addr'); C('B.PRICE',B,'PRICE()')
C('B.totalPaidShares',B,'totalPaidShares()'); C('B.FREE_AMOUNT',B,'FREE_AMOUNT()')
C('B.TOKENS_PER_SHARE',B,'TOKENS_PER_SHARE()')

Ctok='0x942c19A87a77b062D94C452ED8FaC6162aff45aD'
print('--- FEED-C 0x942c19A8 token+saleContract ---')
C('C.name',Ctok,'name()',dec='s'); C('C.symbol',Ctok,'symbol()',dec='s')
C('C.totalSupply',Ctok,'totalSupply()'); C('C.saleContract',Ctok,'saleContract()',dec='addr')
C('C.pair',Ctok,'pair()',dec='addr')

D='0xaa890A3B658eCFa56f0d0486665F0D4e77f3Fa0F'
print('--- FEED-D 0xaa890A3B EXTERNAL_URL NFT ---')
C('D.EXTERNAL_URL',D,'EXTERNAL_URL()',dec='s')
C('D.name',D,'name()',dec='s'); C('D.symbol',D,'symbol()',dec='s')
C('D.minter',D,'minter()',dec='addr'); C('D.nextId',D,'nextId()')

FAT='0x3ea76cd5b86884eb5e3d23a4e2e58154d45a8996'
print('--- FAT AGENTIC free-pool confirm ---')
C('FAT.freeAllocation',FAT,'freeAllocation()'); C('FAT.freeMinted',FAT,'freeMinted()')
C('FAT.freeRemaining',FAT,'freeRemaining()'); C('FAT.mintPrice',FAT,'mintPrice()')
C('FAT.totalMinted',FAT,'totalMinted()'); C('FAT.mintOpen',FAT,'mintOpen()',dec='b')
C('FAT.paidMinted',FAT,'paidMinted()')

json.dump(out, open('run-2026-11-05-1901-ethcall.json','w'), indent=1)
print('saved run-2026-11-05-1901-ethcall.json')
