import sys, time, json
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from ankr import ankr_post
from fast_rpc import batch as _batch
latest = int(_batch([("eth_blockNumber", [])], endpoint="https://bsc-dataseed.binance.org/", timeout=15)[0], 16)
print("head:", latest, flush=True)
t0=time.time()
body = ankr_post("ankr_getLogs", {"blockchain":"bsc","fromBlock":hex(latest-49),"toBlock":hex(latest),"pageSize":1000,"decodeLogs":False,"topics":["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef","0x"+"00"*32]}, timeout=30)
print("preflight OK in %.1fs, logs=%d" % (time.time()-t0, len(body.get("result",{}).get("logs",[]))), flush=True)
