import json, urllib.request, sys
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
print("Dafeiyu freeAgentCount:", single(D, sel('freeAgentCount()')))
print("Dafeiyu isFreeEligible(user):", single(D, sel('isFreeEligible(address)')+enc_addr(USER)))
print("Dafeiyu isFreeAgent(user):", single(D, sel('isFreeAgent(address)')+enc_addr(USER)))
print("Dafeiyu priceFor(1):", single(D, sel('priceFor(uint256)')+enc_u(1)))
print("Dafeiyu poolOpened:", single(D, sel('poolOpened()')))
print("Dafeiyu remaining:", single(D, sel('remaining()')))
print("Dafeiyu openPool:", single(D, sel('openPool()')))
P='0x587C303982187Ec578dF309d27670327b13202F8'
print("PawGang TOTAL_SUPPLY:", single(P, sel('TOTAL_SUPPLY()')))
print("PawGang hasMinted(user):", single(P, sel('hasMinted(address)')+enc_addr(USER)))
print("PawGang totalMinted:", single(P, sel('totalMinted()')))
print("PawGang tierQuota(0):", single(P, sel('tierQuota(uint256)')+enc_u(0)))
print("PawGang tierMinted(0):", single(P, sel('tierMinted(uint256)')+enc_u(0)))
print("PawGang MINT_START:", single(P, sel('MINT_START()')))
print("PawGang mintOpen:", single(P, sel('mintOpen()')))
X='0x08b1a979dd997492eecc010fe986ea2e2925e620'
print("PassAgentX mintStart:", single(X, sel('mintStart()')))
print("PassAgentX mintEnd:", single(X, sel('mintEnd()')))
print("PassAgentX freeUsedByWallet(user):", single(X, sel('freeUsedByWallet(address)')+enc_addr(USER)))
print("PassAgentX claimableOf(user):", single(X, sel('claimableOf(address)')+enc_addr(USER)))
print("PassAgentX eligibility(user):", single(X, sel('eligibility(address)')+enc_addr(USER)))
print("PassAgentX claimOpen:", single(X, sel('claimOpen()')))
print("PassAgentX freeMinted:", single(X, sel('freeMinted()')))
print("PassAgentX mintTimeLeft:", single(X, sel('mintTimeLeft()')))
print("PassAgentX REGISTRY:", single(X, sel('REGISTRY()')))
E='0xEB71a7cbF97e091beBE2175C48E350D1993a04c9'
print("EB71 REGISTRY:", single(E, sel('REGISTRY()')))
print("EB71 MAX_FREE_SUPPLY:", single(E, sel('MAX_FREE_SUPPLY()')))
print("EB71 freeMinted:", single(E, sel('freeMinted()')))
print("EB71 freeRemaining:", single(E, sel('freeRemaining()')))
print("EB71 totalSupply:", single(E, sel('totalSupply()')))
print("EB71 MAX_SUPPLY:", single(E, sel('MAX_SUPPLY()')))
print("EB71 name:", single(E, sel('name()')))
# Sourcify ABI details for PawGang mint + Dafeiyu freeClaimed inputs
for label, addr in [("PawGang",P),("Dafeiyu",D)]:
    url=f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    req=urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
    try: d=json.load(urllib.request.urlopen(req, timeout=20))
    except Exception as e: print(label,"Sourcify ERROR",e); continue
    for e in d.get("abi",[]):
        if e.get("type")=="function" and e.get("name") in ("mint","freeClaimed","freeAgent","claim","freeMint","mintFree"):
            print(label,"ABI",e.get("name"),"inputs:",[(i.get("type"),i.get("name")) for i in e.get("inputs",[])],"mutability:",e.get("stateMutability"))
