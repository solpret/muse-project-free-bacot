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
out={}
def C(label, to, sig, args='', dec='u'):
    data=sel(sig)+args
    res, used = call(to, data)
    fn={'u':u,'addr':addr,'b':b,'s':s}[dec]
    val=fn(res) if res is not None else None
    print(f"{label}: {val} (raw={res} via {used})")
    out[label]=val
    return val
NFT='0xe22763bBaa9aA11a88b47E6f604c5DED0510DDE6'
print('--- NFT 0xe22763bB ---')
C('nft.name',NFT,'name()',dec='s'); C('nft.symbol',NFT,'symbol()',dec='s')
C('nft.AGENT_REGISTRY',NFT,'AGENT_REGISTRY()',dec='addr')
C('nft.totalSupply',NFT,'totalSupply()'); C('nft.totalMinted',NFT,'totalMinted()')
C('nft.MAX_SUPPLY',NFT,'MAX_SUPPLY()'); C('nft.PRICE',NFT,'PRICE()')
C('nft.spotsLeft',NFT,'spotsLeft()'); C('nft.quote1',NFT,'quote(uint256)',enc_uint(1))
C('nft.mintedBy_user',NFT,'mintedBy(address)',enc_addr(USER))
NJAR='0x816458b734d17d59058762deaadd9b952bad6985'
print('--- NJAR sale ---')
C('njar.REGISTRY',NJAR,'REGISTRY()',dec='addr'); C('njar.token',NJAR,'token()',dec='addr')
C('njar.GIFT_SHARES',NJAR,'GIFT_SHARES()'); C('njar.GIFT_WINDOW',NJAR,'GIFT_WINDOW()')
C('njar.giftsClaimed',NJAR,'giftsClaimed()'); C('njar.openedAt',NJAR,'openedAt()')
C('njar.saleStart',NJAR,'saleStart()'); C('njar.live',NJAR,'live()',dec='b')
C('njar.poolOpen',NJAR,'poolOpen()',dec='b'); C('njar.TOKENS_PER_SHARE',NJAR,'TOKENS_PER_SHARE()')
C('njar.mintPrice',NJAR,'mintPrice()'); C('njar.quote1',NJAR,'quote(uint256)',enc_uint(1))
C('njar.paidSharesSold',NJAR,'paidSharesSold()'); C('njar.maxPerWallet',NJAR,'maxPerWallet()')
aid=C('njar.agentIdOf_user',NJAR,'agentIdOf(address)',enc_addr(USER))
print('agentIdOf raw tuple decode: need manual')
res,_=call(NJAR, sel('agentIdOf(address)')+enc_addr(USER))
print('agentIdOf raw:',res)
if res:
    h=res[2:]; print('  agentId=',int(h[0:64],16),' hasAgent=',int(h[64:128],16)!=0)
    aidv=int(h[0:64],16)
    C('njar.giftTaken_agentId',NJAR,'giftTaken(uint256)',enc_uint(aidv),dec='b')
MAO='0x29A4B2f50871a010064571AaF34B228e9f245EC8'
print('--- MAO sale ---')
C('mao.token',MAO,'token()',dec='addr'); C('mao.poolOpened',MAO,'poolOpened()',dec='b')
C('mao.startTime',MAO,'startTime()'); C('mao.POOL_TRIGGER',MAO,'POOL_TRIGGER()')
C('mao.currentGen',MAO,'currentGen()'); C('mao.saleFinished',MAO,'saleFinished()',dec='b')
json.dump({'block':blk,'out':out}, open('run-2026-11-05-1831-ethcall.json','w'), indent=1)
print('saved run-2026-11-05-1831-ethcall.json')
