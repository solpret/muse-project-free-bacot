import sys, time, json
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
import subprocess
# head via dataseed
head = None
for _ep in ["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed.binance.org/"]:
    try:
        _o = subprocess.run(["curl","-sL","--max-time","25","-X","POST",_ep,"-H","Content-Type: application/json","-d",'{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'],capture_output=True,text=True).stdout
        head = int(json.loads(_o)["result"],16); print("head via", _ep); break
    except Exception as e:
        print("head fail", _ep, e); continue
if head is None:
    print("preflight FAIL: no RPC head"); raise SystemExit(1)
print("head", head)
t0=time.time()
try:
    body = ankr_post("ankr_getLogs", {"blockchain":"bsc","fromBlock":str(head-49),"toBlock":str(head),"topics":["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef","0x0000000000000000000000000000000000000000000000000000000000000000"],"pageSize":10}, timeout=30)
    print("preflight OK in %.1fs:"%(time.time()-t0), str(body)[:300])
except Exception as e:
    print("preflight FAIL in %.1fs: %s"%(time.time()-t0, e))
