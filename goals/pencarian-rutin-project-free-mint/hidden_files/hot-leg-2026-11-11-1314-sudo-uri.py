import sys, json
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
ADDR="0x869d330bb48e7ab32da16745ef9a36a69d34f12f"
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
def call(data):
    for ep in EPS:
        try: return _single(ep,"eth_call",[{"to":ADDR,"data":data},"latest"],12,retries=0)
        except Exception as e: last=str(e)[:100]
    return {"error":last}
def dec_str(h):
    try:
        b=bytes.fromhex(h[2:])
        off=int.from_bytes(b[0:32],'big'); ln=int.from_bytes(b[off:off+32],'big')
        return b[off+32:off+32+ln].decode()
    except Exception as e: return f"err {e} raw={h[:120]}"
for label,sig,arg in [("name","name()",""),("symbol","symbol()",""),("contractURI","contractURI()",""),("tokenURI_1","tokenURI(uint256)",format(1,"064x"))]:
    r=call(sel(sig)+arg)
    print(label, dec_str(r) if isinstance(r,str) and r.startswith("0x") else r)
