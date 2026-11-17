import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return "0x" + a[2:].lower().rjust(64, "0")
B="0xc205F8c74733D914776D66cBc4Cf10BF701D96Aa"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
tests=[("totalSupply()",""),("freeClaimed()",""),("FREE_SUPPLY()",""),("MAX_SUPPLY()",""),("mintOpen()",""),("mintedBy(address)",enc_addr(USER)[2:]),("freeFor(address)",enc_addr(USER)[2:]),("freeUsed(address)",enc_addr(USER)[2:]),("balanceOf(address)",enc_addr(USER)[2:])]
out={}
for name,arg in tests:
    data=sel(name)+arg; val,err=None,None
    for ep in EPS:
        try: val=_single(ep,"eth_call",[{"to":B,"data":data},"latest"],8,retries=0); break
        except Exception as e: err=f"{type(e).__name__}: {str(e)[:100]}"
    try: iv=int(val,16) if val else None
    except Exception: iv=None
    out[name]={"int":iv,"raw":val,"error":err if val is None else None}
    print(name, iv, err or "")
block=None
for ep in EPS:
    try: block=int(_single(ep,"eth_blockNumber",[],8,retries=0),16); break
    except Exception as e: block=f"error: {e}"
print("block",block)
json.dump({"block":block,"results":out},open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-01-2031-bubble.json","w"),indent=1)
