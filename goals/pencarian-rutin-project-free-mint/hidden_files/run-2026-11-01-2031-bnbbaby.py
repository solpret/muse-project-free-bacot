import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return "0x" + a[2:].lower().rjust(64, "0")
BABY="0xbb7ed59ca41ea03cf20084a8c9de94244b7b2637"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
names=["sharesMinted()","freeMinted()","paidShares()","totalShares()","MAX_SHARES()","deadline()"]
out={}
for name in names:
    val,err=None,None
    for ep in EPS:
        try: val=_single(ep,"eth_call",[{"to":BABY,"data":sel(name)},"latest"],8,retries=0); break
        except Exception as e: err=f"{type(e).__name__}: {str(e)[:100]}"
    try: iv=int(val,16) if val else None
    except Exception: iv=None
    out[name]={"raw":val,"int":iv,"error":err if val is None else None}
for name in ["freeMintedBy(address)","shares(address)","mintedBy(address)","hasClaimed(address)"]:
    data=sel(name)+enc_addr(USER)[2:]; val,err=None,None
    for ep in EPS:
        try: val=_single(ep,"eth_call",[{"to":BABY,"data":data},"latest"],8,retries=0); break
        except Exception as e: err=f"{type(e).__name__}: {str(e)[:100]}"
    try: iv=int(val,16) if val else None
    except Exception: iv=None
    out[name]={"raw":val,"int":iv,"error":err if val is None else None}
block=None
for ep in EPS:
    try: block=int(_single(ep,"eth_blockNumber",[],8,retries=0),16); break
    except Exception as e: block=f"error: {e}"
print(json.dumps({"block":block,"contract":BABY,"results":out},indent=1))
