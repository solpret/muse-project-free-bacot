import sys, time, json
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
from Crypto.Hash import keccak
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
ADDR = "0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77"  # HIVE
t=time.time()
try:
    body = ankr_post("eth_call", [{"to": ADDR, "data": sel("totalSupply()")}, "latest"], timeout=30)
    print(f"ANKR eth_call totalSupply HIVE -> {body} ({time.time()-t:.1f}s)", flush=True)
    r = body.get("result")
    if r: print("totalSupply =", int(r,16), flush=True)
except Exception as e:
    print(f"ANKR eth_call FAIL {type(e).__name__}: {str(e)[:200]} ({time.time()-t:.1f}s)", flush=True)
t=time.time()
try:
    body = ankr_post("eth_blockNumber", [], timeout=30)
    print(f"ANKR eth_blockNumber -> {body} ({time.time()-t:.1f}s)", flush=True)
except Exception as e:
    print(f"ANKR eth_blockNumber FAIL {type(e).__name__}: {str(e)[:200]} ({time.time()-t:.1f}s)", flush=True)
