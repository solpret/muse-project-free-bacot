import sys, time, json
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single
from ankr import ankr_post
t0=time.time()
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed3.bnbchain.org/"]
head=None
for ep in EPS:
    try:
        head=int(_single(ep,"eth_blockNumber",[],8,retries=0),16); break
    except Exception as e:
        print("dataseed fail",ep,e,flush=True)
print(f"head={head} t={time.time()-t0:.1f}s",flush=True)
if head is None: sys.exit(1)
body=ankr_post("ankr_getLogs",{"blockchain":"bsc","fromBlock":hex(head-49),"toBlock":hex(head),"pageSize":1000,"decodeLogs":False,"topics":["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef","0x"+"00"*32]},timeout=30)
n=len(body.get("result",{}).get("logs",[]))
print(f"PREFLIGHT OK head={head} logs50={n} total={time.time()-t0:.1f}s",flush=True)
