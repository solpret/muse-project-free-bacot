import sys, json
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _post as _fr_post
from Crypto.Hash import keccak
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return '0x'+k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64,'0')
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
M='0x46cb1D3efd4307506Cda7EbBa5a51be64746739E'
T='0x209173F09aFbCA053C0de9e9763f503e9fb54a3c'
out={}
for v in ['launched()','failed()','isRefundPhase()','totalShares()','tokenClaimed(address)','claimable(address)']:
    data = sel(v)+enc_addr(USER) if '(address)' in v else sel(v)
    out[v]=single(M, data)
    print(f"mint {v} =", out[v])
print("token balanceOf(user) =", single(T, sel('balanceOf(address)')+enc_addr(USER)))
print("token totalSupply =", single(T, sel('totalSupply()')))
json.dump(out, open('run-2026-11-08-1531-binanceai.json','w'), indent=1)
