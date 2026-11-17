import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def ea(a): return "0x"+a[2:].lower().rjust(64,"0")
def eu(n): return "0x"+format(n,"064x")
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
C="0x538Bd9f178eEf2CFB564d2FAD1D5B0702d8B3818"; USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def call(data):
    for ep in EPS:
        try: return _single(ep,"eth_call",[{"to":C,"data":data},"latest"],8,retries=0)
        except Exception: pass
def iv(v): return int(v,16) if v else None
def words(v):
    if not v: return None
    b=bytes.fromhex(v[2:]); return [int.from_bytes(b[i:i+32],"big") for i in range(0,len(b),32)]
out={}
for fn in ["totalSupply()","totalClaimedShares()","freeSupply()","freeClaimedShares()","freeTaken()","remainingShares()","claimOpen()","paused()","paidPrice()","shareSize()","TOTAL_SHARES()","FREE_SHARES()"]:
    out[fn]=iv(call(sel(fn)))
out["quote_user_1"]=words(call(sel("quote(address,uint256)")+ea(USER)[2:]+eu(1)[2:]))
out["claimedBy_user"]=iv(call(sel("claimedBy(address)")+ea(USER)[2:]))
out["balance_user"]=iv(call(sel("balanceOf(address)")+ea(USER)[2:]))
out["REGISTRY"]=call(sel("REGISTRY()"))
print(json.dumps(out,indent=1))
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-02-0701-538b.json","w"), indent=1)
