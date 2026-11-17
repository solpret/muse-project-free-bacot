import sys, time, json
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _post as fr_post
from ankr import ankr_post
t0=time.time()
head=None
for ep in ["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed.binance.org/"]:
    try:
        out=fr_post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]},timeout=8,retries=0)
        head=int(out["result"],16); print(f"head {head} via {ep} in {time.time()-t0:.1f}s",flush=True); break
    except Exception as e:
        print(f"head fail {ep}: {e}",flush=True)
if head is None:
    print("PREFLIGHT2 FAIL: no head"); sys.exit(2)
t1=time.time()
try:
    body=ankr_post("ankr_getLogs",{"blockchain":"bsc","fromBlock":hex(head-49),"toBlock":hex(head),"pageSize":1000,"decodeLogs":False,"topics":["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef","0x"+"00"*32]},timeout=30)
    logs=body.get("result",{}).get("logs",[])
    print(f"PREFLIGHT2 OK: ankr_getLogs {head-49}-{head} -> {len(logs)} logs in {time.time()-t1:.1f}s; total {time.time()-t0:.1f}s",flush=True)
    print(json.dumps({"head":head,"logs":len(logs),"seconds":round(time.time()-t0,1)}))
except Exception as e:
    print(f"PREFLIGHT2 FAIL ankr: {type(e).__name__}: {e}",flush=True); sys.exit(3)
