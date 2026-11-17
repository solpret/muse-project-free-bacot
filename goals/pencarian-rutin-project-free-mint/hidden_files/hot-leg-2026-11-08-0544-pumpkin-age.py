import sys, json
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
ADDR="0x77e38295603a06654a6ed3ed0849e6aa50749963"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
DATA=sel("totalSupply()")
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc.publicnode.com/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed.binance.org/"]
def ts_at(blk):
    for ep in EPS:
        try:
            r=batch([("eth_call",[{"to":ADDR,"data":DATA},hex(blk)])],endpoint=ep,timeout=10)
            v=r[0]
            if v is None: return (ep,"null")
            return (ep,int(v,16))
        except Exception as e:
            last=f"{type(e).__name__}:{str(e)[:80]}"
    return ("all","ERR:"+last)
head=int(batch([("eth_blockNumber",[])],endpoint=EPS[0],timeout=8)[0],16)
print("head",head)
for blk in [head, head-1000, head-10000, head-100000, head-200000, head-384000]:
    print(blk, ts_at(blk))
