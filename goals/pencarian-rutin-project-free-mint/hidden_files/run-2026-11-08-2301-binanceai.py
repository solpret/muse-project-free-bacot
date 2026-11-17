import sys, json, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _post as _fr_post
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed3.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def to_int(v):
    try:
        if v is None or v=="0x": return None
        return int(v,16)
    except Exception: return None
def call(addr, sig, arg=None, timeout=30):
    data=sel(sig)+(enc(arg) if arg else "")
    for ep in EPS:
        try:
            out=_fr_post(ep, {"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]}, timeout=timeout, retries=0)
            if isinstance(out,dict) and "error" in out: return None
            return to_int(out.get("result")) if isinstance(out,dict) else None
        except Exception: continue
    return None
MINT="0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"
TOKEN="0x209173F09aFbCA053C0de9e9763f503e9fb54a3c"
res={}
for name,addr,sig,arg in [
    ("launched",MINT,"launched()",None),("failed",MINT,"failed()",None),
    ("isRefundPhase",MINT,"isRefundPhase()",None),("totalShares",MINT,"totalShares()",None),
    ("tokenClaimed_user",MINT,"tokenClaimed(address)",USER),
    ("claimable_user",MINT,"claimable(address)",USER),
    ("tokenBalance_user",TOKEN,"balanceOf(address)",USER),
    ("token_totalSupply",TOKEN,"totalSupply()",None)]:
    t=time.time(); v=call(addr,sig,arg); res[name]=v
    print(f"{name} = {v} ({time.time()-t:.1f}s)", flush=True)
# slot verification: GLOOP + Pokechain balanceOf(user) fresh single calls
for name,addr in [("GLOOP","0x183CBb52B3C7BCB2433d50dE0Add99B59f4DE4fE"),
                  ("Pokechain","0x4EF929aF00cB93993c3D01834C4DA79200d31e32")]:
    v=call(addr,"balanceOf(address)",USER)
    print(f"VERIFY {name} balanceOf(user) = {v}", flush=True)
    res[name+"_balanceOf_user_verify"]=v
# Agentic Bull per-view check (artifact check)
AB="0x1Aa9797cC762b838388566Daa45A56b1709F4Bbe"
for sig in ["totalSupply()","totalMinted()","freeClaimed()"]:
    v=call(AB,sig)
    print(f"AgenticBull {sig} = {v}", flush=True)
    res["agenticbull_"+sig]=v
json.dump(res, open("run-2026-11-08-2301-binanceai.json","w"), indent=1)
print("written run-2026-11-08-2301-binanceai.json")
