import sys, time, json
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch as _batch
from ankr import ankr_post
t0=time.time()
# head block via dataseed
head=None
for ep in ["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed.binance.org/"]:
    try:
        r=_batch([("eth_blockNumber",[])], endpoint=ep, timeout=15)[0]
        head=int(r,16); break
    except Exception as e:
        print("head fail", ep, e, flush=True)
print("HEAD", head, flush=True)
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
body=ankr_post("ankr_getLogs", {"blockchain":"bsc","fromBlock":hex(head-50),"toBlock":hex(head),"pageSize":1000,"decodeLogs":False,"topics":[TRANSFER]}, timeout=30)
logs=body.get("result",{}).get("logs",[])
print("PREFLIGHT OK logs=", len(logs), "elapsed=%.1fs"%(time.time()-t0), "head=", head, flush=True)
json.dump({"head":head,"logs":len(logs),"elapsed":time.time()-t0}, open("run-2026-11-09-0301-preflight.json","w"))
