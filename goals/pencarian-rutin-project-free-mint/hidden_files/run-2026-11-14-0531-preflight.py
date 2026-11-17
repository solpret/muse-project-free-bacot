import sys, time, json
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
t0=time.time()
try:
    r = ankr_post("ankr_getLogs", {"blockchain":"bsc","fromBlock":133432900,"toBlock":133432949,
        "topics":["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
                  "0x0000000000000000000000000000000000000000000000000000000000000000"]}, timeout=55)
    print("PREFLIGHT OK", round(time.time()-t0,1), "s:", json.dumps(r)[:300])
except Exception as e:
    print("PREFLIGHT FAIL", round(time.time()-t0,1), "s:", str(e)[:300])
