import sys, json, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _post as fr_post
from datetime import datetime, timezone, timedelta
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed.binance.org/"]
ADDR="0xeEdd6F512Fec64AD5A4aa64722ef6C5689937B50"
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x"+"00"*32
def getlogs(frm,to):
    for ep in EPS:
        try:
            out=fr_post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_getLogs","params":[{"fromBlock":hex(frm),"toBlock":hex(to),"address":ADDR,"topics":[TRANSFER,ZERO]}]},timeout=15,retries=0)
            return out.get("result",[])
        except Exception as e:
            continue
    return None
def block_ts(blk):
    for ep in EPS:
        try:
            out=fr_post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_getBlockByNumber","params":[hex(blk),False]},timeout=8,retries=0)
            return int(out["result"]["timestamp"],16)
        except Exception:
            continue
    return None
frm,to=132404126,132409469
all_logs=[]
f=frm
while f<=to:
    t=min(f+999,to)
    logs=getlogs(f,t)
    print(f"chunk {f}-{t}: {None if logs is None else len(logs)} logs",flush=True)
    if logs: all_logs.extend(logs)
    f=t+1
print("total first-mint-candidate logs:",len(all_logs),flush=True)
res={"address":ADDR,"logs":len(all_logs)}
if all_logs:
    first=min(all_logs,key=lambda l:int(l["blockNumber"],16))
    blk=int(first["blockNumber"],16)
    ts=block_ts(blk)
    wib=datetime.fromtimestamp(ts,timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB") if ts else None
    minters=len(set(l["topics"][2] for l in all_logs))
    print("first mint block:",blk,"tx:",first["transactionHash"],"wib:",wib,"mints in range:",len(all_logs),"minters:",minters,flush=True)
    res.update({"first_block":blk,"first_tx":first["transactionHash"],"first_ts":ts,"first_wib":wib,"mints_in_range":len(all_logs),"minters":minters})
json.dump(res,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-08-2131-numbi.json","w"),indent=1)
