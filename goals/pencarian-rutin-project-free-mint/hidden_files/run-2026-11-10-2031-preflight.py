import sys, time, json
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
# head first via dataseed
import urllib.request
def rpc(ep, method, params, timeout=25):
    body=json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode()
    req=urllib.request.Request(ep, data=body, headers={"Content-Type":"application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=timeout).read())
head=None
for ep in ["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]:
    try:
        head=int(rpc(ep,"eth_blockNumber",[])["result"],16); break
    except Exception as e:
        print("head fail", ep, e, flush=True)
print("HEAD", head, flush=True)
t0=time.time()
try:
    res=ankr_post("ankr_getLogs", {"blockchain":"bsc","fromBlock":hex(head-49),"toBlock":hex(head),
        "topics":["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
                  "0x0000000000000000000000000000000000000000000000000000000000000000",
                  None,
                  "0x00000000000000000000000055d398326f99059ff775485246999027b3197955"]}, timeout=55)
    print("PREFLIGHT OK in %.1fs logs=%s" % (time.time()-t0, len(res.get("logs",[])) if isinstance(res,dict) else res), flush=True)
except Exception as e:
    print("PREFLIGHT FAIL in %.1fs: %s" % (time.time()-t0, e), flush=True)
