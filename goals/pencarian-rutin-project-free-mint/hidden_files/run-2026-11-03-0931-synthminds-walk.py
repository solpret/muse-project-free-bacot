#!/usr/bin/env python3
import sys
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
A="0x36E655717BA3fB01268b6069a88Cc5D4a982EA15"
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x"+"00"*32
# walk back in 2000-block chunks from 131350347
end=131350347
for i in range(6):
    frm=end-2000+1; to=end-1
    # chunk convention: use [frm, to] with to = end-1 to avoid overlap; first chunk 131348348-131350346
    try:
        body=ankr_post("ankr_getLogs", {"blockchain":"bsc","fromBlock":hex(frm),"toBlock":hex(to),"address":A,"pageSize":1000,"decodeLogs":False,"topics":[TRANSFER,ZERO]}, timeout=30)
        res=body.get("result",body) if isinstance(body,dict) else body
        logs=res.get("logs",[]) if isinstance(res,dict) else []
        print(f"chunk {frm}-{to} mints {len(logs)}", flush=True)
        if logs:
            blks=sorted(int(l.get("blockNumber"),16) for l in logs if l.get("blockNumber"))
            print("  earliest block in chunk:", blks[0] if blks else None, "latest:", blks[-1] if blks else None, flush=True)
            break
    except Exception as e: print(f"chunk {frm}-{to} ERROR {str(e)[:160]}", flush=True); break
    end=frm
