import sys, json
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
ADDR="0x2b5c0d44878279501aa111e353a2b493e0823b57"
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x"+"00"*32
def logs(frm,to):
    out=[]; token=None
    for _ in range(10):
        p={"blockchain":"bsc","fromBlock":hex(frm),"toBlock":hex(to),"pageSize":1000,"decodeLogs":False,"address":ADDR,"topics":[TRANSFER,ZERO]}
        if token: p["pageToken"]=token
        body=ankr_post("ankr_getLogs",p,timeout=30)
        r=body.get("result",{}) if isinstance(body,dict) else {}
        out.extend(r.get("logs",[])); token=r.get("nextPageToken")
        if not token: break
    return out
# walk backwards from head in 20000-block steps: find first chunk with zero from-zero logs
import subprocess
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import race
head=int(race("eth_blockNumber",[]),16)
print("head",head,flush=True)
hi=head; found=None
while hi>0:
    lo=max(0,hi-20000)
    try:
        lg=logs(lo,hi)
    except Exception as e:
        print("ERR chunk",lo,hi,type(e).__name__,str(e)[:150],flush=True); break
    print("chunk",lo,hi,"from-zero logs",len(lg),flush=True)
    if len(lg)==0:
        print("EMPTY chunk -> first mint is above",lo,flush=True); break
    found=(lo,hi,lg)
    hi=lo-1
    if hi<131200000: 
        print("floor reached, stop",flush=True); break
if found:
    lo,hi,lg=found
    # earliest log in the oldest non-empty chunk: refine within that chunk in 2000-block steps
    print("oldest non-empty chunk",lo,hi,"count",len(lg),flush=True)
    # get block numbers, earliest
    blocks=sorted({int(x.get("blockNumber"),16) if isinstance(x.get("blockNumber"),str) else x.get("blockNumber") for x in lg})
    print("earliest block in chunk",blocks[0],"latest",blocks[-1],flush=True)
    json.dump({"head":head,"oldest_chunk":[lo,hi],"earliest_block_in_chunk":blocks[0],"count_in_chunk":len(lg)},open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-03-1431-kitsuneon-firstmint.json","w"),indent=1)
