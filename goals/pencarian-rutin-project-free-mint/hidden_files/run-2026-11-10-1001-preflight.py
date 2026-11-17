import sys, time, json
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
import subprocess
# head via dataseed
out = subprocess.run(["curl","-sL","--max-time","25","-X","POST","https://bsc-dataseed1.bnbchain.org/","-H","Content-Type: application/json","-d",'{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'],capture_output=True,text=True).stdout
head = int(json.loads(out)["result"],16)
print("head", head)
t0=time.time()
try:
    body = ankr_post("ankr_getLogs", {"blockchain":"bsc","fromBlock":str(head-49),"toBlock":str(head),"topics":["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef","0x0000000000000000000000000000000000000000000000000000000000000000"],"pageSize":10}, timeout=30)
    print("preflight OK in %.1fs:"%(time.time()-t0), str(body)[:300])
except Exception as e:
    print("preflight FAIL in %.1fs: %s"%(time.time()-t0, e))
