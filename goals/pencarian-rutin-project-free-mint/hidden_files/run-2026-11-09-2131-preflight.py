import sys, time, json
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x0000000000000000000000000000000000000000000000000000000000000000"
# current head via dataseed
import urllib.request
def head():
    body = json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}).encode()
    req = urllib.request.Request("https://bsc-dataseed1.bnbchain.org", data=body, headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return int(json.load(r)["result"], 16)
h = head()
print("HEAD", h, flush=True)
t0=time.time()
try:
    body = ankr_post("ankr_getLogs", {"blockchain":"bsc","fromBlock":str(h-50),"toBlock":str(h),"topics":[TRANSFER, ZERO_TOPIC],"pageSize":10}, timeout=55)
    print("PREFLIGHT OK in %.1fs" % (time.time()-t0), flush=True)
    logs = body.get("result", {}).get("logs", []) if isinstance(body, dict) else []
    print("logs:", len(logs), flush=True)
    print(json.dumps({"ok": True, "head": h, "elapsed": round(time.time()-t0,1), "logs": len(logs)}))
except Exception as e:
    print("PREFLIGHT FAIL in %.1fs: %r" % (time.time()-t0, e), flush=True)
    print(json.dumps({"ok": False, "head": h, "elapsed": round(time.time()-t0,1), "error": repr(e)}))
