import sys, time, json
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
head=132409469
t1=time.time()
try:
    body=ankr_post("ankr_getLogs",{"blockchain":"bsc","fromBlock":hex(head-49),"toBlock":hex(head),"pageSize":1000,"decodeLogs":False,"topics":["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef","0x"+"00"*32]},timeout=30)
    logs=body.get("result",{}).get("logs",[])
    print(f"ANKR-PROBE OK: {head-49}-{head} -> {len(logs)} logs in {time.time()-t1:.1f}s",flush=True)
except Exception as e:
    print(f"ANKR-PROBE FAIL: {type(e).__name__}: {e} in {time.time()-t1:.1f}s",flush=True)
