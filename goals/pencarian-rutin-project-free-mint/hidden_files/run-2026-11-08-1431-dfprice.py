import sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _post as _fr_post
from Crypto.Hash import keccak
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return '0x'+k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64,'0')
def enc_u(n): return format(n,'064x')
USER='0xeb237F6f9FB4e826739F0954e9768914F28b2c2E'
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed.binance.org/"]
def single(addr, data):
    for ep in EPS:
        try:
            out=_fr_post(ep, {"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]}, timeout=8, retries=0)
            if not isinstance(out,dict): continue
            if out.get("error"): return "ERR"
            r=out.get("result")
            if r is None: return None
            if r=="0x": return 0
            if r.startswith("0x") and len(r)<=66: return int(r,16)
            return r
        except Exception: continue
    return "ERR:all-fail"
D='0xd8de64acb25a87d98f1e170bf082a01427772511'
print("priceFor(user,636):", single(D, sel('priceFor(address,uint256)')+enc_addr(USER)+enc_u(636)))
print("priceFor(user,1):", single(D, sel('priceFor(address,uint256)')+enc_addr(USER)+enc_u(1)))
print("priceOf(666):", single(D, sel('priceOf(uint256)')+enc_u(666)))
print("priceOf(667):", single(D, sel('priceOf(uint256)')+enc_u(667)))
print("priceOf(635):", single(D, sel('priceOf(uint256)')+enc_u(635)))
print("TIER2_END_ID:", single(D, sel('TIER2_END_ID()')))
print("PRICE_TIER2:", single(D, sel('PRICE_TIER2()')))
print("PRICE_TIER3:", single(D, sel('PRICE_TIER3()')))
print("tierOf(1):", single(D, sel('tierOf(uint256)')+enc_u(1)))
print("tierOf(636):", single(D, sel('tierOf(uint256)')+enc_u(636)))
print("totalSupply:", single(D, sel('totalSupply()')))
print("isFreeEligible(user):", single(D, sel('isFreeEligible(address)')+enc_addr(USER)))
