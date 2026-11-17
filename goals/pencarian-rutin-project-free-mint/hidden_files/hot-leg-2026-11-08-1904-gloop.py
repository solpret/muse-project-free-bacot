import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
GLOOP="0x183CBb52B3C7BCB2433d50dE0Add99B59f4DE4fE"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EP="https://bsc-dataseed1.bnbchain.org/"
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def single(sig, arg=None):
    data=sel(sig)
    if arg=="USER": data+=enc(USER)
    elif isinstance(arg,int): data+=format(arg,"064x")
    try:
        r=batch([("eth_call",[{"to":GLOOP,"data":data},"latest"])], endpoint=EP, timeout=20)
        return int(r[0],16)
    except Exception as e:
        return f"ERR {str(e)[:100]}"
out={}
for name,sig,arg in [("totalMinted","totalMinted()",None),("mintOpen","mintOpen()",None),
                     ("TOTAL_SUPPLY","TOTAL_SUPPLY()",None),("MINT_START","MINT_START()",None),
                     ("difficultyBits","difficultyBits()",None),
                     ("hasMinted_user","hasMinted(address)", "USER"),
                     ("balanceOf_user","balanceOf(address)","USER")]:
    out[name]=single(sig,arg)
for t in range(4):
    out[f"tierQuota_{t}"]=single("tierQuota(uint256)",t)
    out[f"tierMinted_{t}"]=single("tierMinted(uint256)",t)
try:
    out["block"]=int(batch([("eth_blockNumber",[])],endpoint=EP,timeout=20)[0],16)
except Exception as e:
    out["block"]=f"ERR {e}"
print(json.dumps(out,indent=1))
json.dump(out,open("hot-leg-2026-11-08-1904-gloop.json","w"),indent=1)
