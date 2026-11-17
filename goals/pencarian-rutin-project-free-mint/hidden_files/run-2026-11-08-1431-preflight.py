import sys, time, json
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from ankr import ankr_post
from fast_rpc import _post
t0=time.time()
head=None
for ep in ['https://bsc-dataseed2.bnbchain.org/','https://bsc-dataseed.binance.org/','https://bsc-dataseed1.bnbchain.org/']:
    try:
        head=int(_post(ep, {'jsonrpc':'2.0','id':1,'method':'eth_blockNumber','params':[]}, timeout=8, retries=0)['result'],16)
        break
    except Exception as e:
        print("head fail", ep, e, flush=True)
if head is None:
    head=132351223
    print("head fallback to earlier read", head, flush=True)
frm=head-49
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
res=ankr_post("ankr_getLogs", {"blockchain":"bsc","fromBlock":hex(frm),"toBlock":hex(head),"topics":[TRANSFER],"pageSize":1000}, timeout=55)
logs=res.get("result",{}).get("logs",[]) if isinstance(res,dict) else []
print(json.dumps({"preflight":"OK","head":head,"from":frm,"to":head,"logs":len(logs),"elapsed":round(time.time()-t0,1)}))
