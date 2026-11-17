#!/usr/bin/env python3
"""PLNK first-mint via Ankr ankr_getLogs (address-filtered Transfer from zero),
walking backwards in 10000-block chunks from head. Read-only."""
import sys, json, time
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
ADDR="0xec266bdd979b19d8a2f1266ef0610b4791dbd24b"
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x"+"00"*32
head=int(ankr_post("eth_blockNumber", [], timeout=30)["result"],16) if isinstance(ankr_post("eth_blockNumber", [], timeout=30).get("result"),str) else None
if head is None:
    sys.path.insert(0,"/home/hatch/workspace/fast_exec")
    from fast_rpc import race
    head=int(race("eth_blockNumber", []),16)
print("head:", head, flush=True)
def chunk_logs(frm,to):
    body=ankr_post("ankr_getLogs", {"blockchain":"bsc","address":ADDR,"fromBlock":hex(frm),"toBlock":hex(to),"pageSize":1000,"decodeLogs":False,"topics":[TRANSFER,ZERO]}, timeout=60)
    return body.get("result",{}).get("logs",[])
# walk back 10000-block chunks, max 12 chunks (~20h)
hi=head; found=None
for i in range(12):
    lo=max(0,hi-9999)
    try:
        logs=chunk_logs(lo,hi)
    except Exception as e:
        print(f"chunk {lo}-{hi} FAIL {e}", flush=True); break
    print(f"chunk {lo}-{hi}: {len(logs)} mint logs", flush=True)
    if len(logs)==0:
        break
    found=(lo,hi,logs)
    hi=lo-1
    time.sleep(1)
if found:
    lo,hi,logs=found
    first=min(logs, key=lambda l: int(l["blockNumber"],16))
    print("EARLIEST mint in last non-empty chunk: block", int(first["blockNumber"],16), "tx", first.get("transactionHash"), flush=True)
    json.dump({"window":[lo,hi],"first_block":int(first["blockNumber"],16),"first_tx":first.get("transactionHash"),"logs_in_chunk":len(logs)}, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-07-1401-plnk-firstmint.json","w"), indent=1)
else:
    print("NO mint logs found in searched range", flush=True)
