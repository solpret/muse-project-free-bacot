import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
H="0x83Ec9F10CEA61ED892B507dcE9E57fA8d4777C2e"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
for name in ["totalMinted()","mintedBy(address)","FREE_SUPPLY()","MAX_SUPPLY()","mintStart()","mintEnd()"]:
    data=sel(name)
    val,err=None,None
    for ep in EPS:
        try: val=_single(ep,"eth_call",[{"to":H,"data":data},"latest"],8,retries=0); break
        except Exception as e: err=f"{type(e).__name__}: {str(e)[:100]}"
    try: iv=int(val,16) if val else None
    except Exception: iv=None
    print(name, iv, val if iv is None else "", err or "")
