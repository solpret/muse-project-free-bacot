import sys, time, json, subprocess
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x0000000000000000000000000000000000000000000000000000000000000000"
def head():
    for ep in ["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed.binance.org/"]:
        try:
            out = subprocess.run(["curl","-sL","--max-time","20","-X","POST",ep,"-H","Content-Type: application/json",
                "-d", json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]})],
                capture_output=True, text=True, timeout=25).stdout
            return int(json.loads(out)["result"], 16)
        except Exception:
            continue
    return None
h = head()
print("HEAD", h, flush=True)
t0=time.time()
try:
    body = ankr_post("ankr_getLogs", {"blockchain":"bsc","fromBlock":str(h-50),"toBlock":str(h),"topics":[TRANSFER, ZERO_TOPIC],"pageSize":10}, timeout=55)
    logs = body.get("result", {}).get("logs", []) if isinstance(body, dict) else []
    print(json.dumps({"ok": True, "head": h, "elapsed": round(time.time()-t0,1), "logs": len(logs)}))
except Exception as e:
    print(json.dumps({"ok": False, "head": h, "elapsed": round(time.time()-t0,1), "error": repr(e)[:300]}))
