import sys, time, json
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _post as _fr_post, batch as _batch
from Crypto.Hash import keccak
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
ADDR = "0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77"  # HIVE
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed.binance.org/", "https://bsc-dataseed3.bnbchain.org/"]
# 1) single eth_call via _fr_post
for ep in EPS:
    t=time.time()
    try:
        out = _fr_post(ep, {"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":ADDR,"data":sel("totalSupply()")},"latest"]}, timeout=8, retries=0)
        print(f"single _fr_post {ep} -> {out} ({time.time()-t:.1f}s)", flush=True)
    except Exception as e:
        print(f"single _fr_post {ep} FAIL {type(e).__name__}: {str(e)[:100]} ({time.time()-t:.1f}s)", flush=True)
# 2) batch of 9 via _fr_post (what reread does)
calls=[{"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":ADDR,"data":sel("totalSupply()")},"latest"]} for i in range(9)]
for ep in EPS[:2]:
    t=time.time()
    try:
        out = _fr_post(ep, calls, timeout=8, retries=0)
        print(f"batch9 _fr_post {ep} -> n={len(out) if isinstance(out,list) else type(out)} ({time.time()-t:.1f}s)", flush=True)
    except Exception as e:
        print(f"batch9 _fr_post {ep} FAIL {type(e).__name__}: {str(e)[:100]} ({time.time()-t:.1f}s)", flush=True)
# 3) fast_rpc.batch single call
for ep in EPS[:2]:
    t=time.time()
    try:
        out = _batch([("eth_call", [{"to":ADDR,"data":sel("totalSupply()")},"latest"])], endpoint=ep, timeout=10)
        print(f"fast_rpc.batch {ep} -> {out} ({time.time()-t:.1f}s)", flush=True)
    except Exception as e:
        print(f"fast_rpc.batch {ep} FAIL {type(e).__name__}: {str(e)[:100]} ({time.time()-t:.1f}s)", flush=True)
