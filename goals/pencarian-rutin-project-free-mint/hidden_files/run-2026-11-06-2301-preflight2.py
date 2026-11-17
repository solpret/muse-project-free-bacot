import sys, time, json
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
t0=time.time()
# Pre-flight per amendment 2026-11-06: ONE small ankr_getLogs call, must succeed <60s.
# Range anchored at last known head (hot-leg 2304 read block 132038070 via dataseed1).
END=132038070
body=ankr_post("ankr_getLogs",{"blockchain":"bsc","fromBlock":hex(END-49),"toBlock":hex(END),"pageSize":1000,"decodeLogs":False,"topics":["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef","0x"+"00"*32]},timeout=30)
n=len(body.get("result",{}).get("logs",[]))
print(f"PREFLIGHT2 OK end={END} logs50={n} total={time.time()-t0:.1f}s",flush=True)
json.dump({"end":END,"logs50":n,"elapsed":round(time.time()-t0,1)},open("run-2026-11-06-2301-preflight2.json","w"),indent=1)
