#!/usr/bin/env python3
"""Preflight retry 3: head via curl (dataseed), Ankr getLogs via ankr module. Read-only."""
import sys, time, json, subprocess
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x0000000000000000000000000000000000000000000000000000000000000000"
def head():
    out = subprocess.run(["curl","-sL","--max-time","25","-X","POST","https://bsc-dataseed1.bnbchain.org/","-H","Content-Type: application/json","-d",'{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}'],capture_output=True,text=True,timeout=30).stdout
    return int(json.loads(out)["result"],16)
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
