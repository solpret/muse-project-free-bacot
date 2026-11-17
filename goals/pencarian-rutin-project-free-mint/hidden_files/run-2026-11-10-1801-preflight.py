#!/usr/bin/env python3
"""Pre-flight Ankr run 1801: satu ankr_getLogs kecil (50 blok) <60 dtk."""
import sys, time, json
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
HEAD = 132765203
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
t0=time.time()
try:
    body = ankr_post("ankr_getLogs", {"blockchain":"bsc","fromBlock":hex(HEAD-49),"toBlock":hex(HEAD),
        "pageSize":100,"decodeLogs":False,"topics":[TRANSFER]}, timeout=30)
    print("PREFLIGHT OK %.1fs logs=%s" % (time.time()-t0, len(body.get("result",{}).get("logs",[])) if isinstance(body,dict) else "?"))
    print(json.dumps(body)[:400])
except Exception as e:
    print("PREFLIGHT FAIL %.1fs: %s" % (time.time()-t0, e))
