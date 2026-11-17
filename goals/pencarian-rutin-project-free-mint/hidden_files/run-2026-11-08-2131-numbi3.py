import sys, json
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _post as fr_post
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed.binance.org/"]
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x"+"00"*32
def getlogs(addr,frm,to,topics):
    for ep in EPS:
        try:
            out=fr_post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_getLogs","params":[{"fromBlock":hex(frm),"toBlock":hex(to),"address":addr,"topics":topics}]},timeout=15,retries=0)
            return out.get("result",[])
        except Exception: continue
    return None
# control: BAHUANG2 should have many mints 132404126-132409469
logs=getlogs("0x57CC350b844484Eac0DE444526d295C90F9cCbB5",132404126,132409469,[TRANSFER,ZERO])
print("CONTROL BAHUANG2 mint logs in window:", None if logs is None else len(logs),flush=True)
# NUMBI wider: last 30000 blocks before 132409469, chunked 1000
ADDR="0xeEdd6F512Fec64AD5A4aa64722ef6C5689937B50"
frm=132409469-30000
tot=0; first=None
f=frm
while f<=132409469:
    t=min(f+999,132409469)
    logs=getlogs(ADDR,f,t,[TRANSFER,ZERO])
    n=0 if logs is None else len(logs)
    if n:
        print(f"NUMBI chunk {f}-{t}: {n} logs",flush=True)
        tot+=n
        if first is None: first=(f,logs[0])
    f=t+1
print("NUMBI total mint logs in last 30000 blocks:",tot,flush=True)
if first:
    print("first in window block:",first[0],"tx:",first[1]["transactionHash"],"blockNumber:",first[1]["blockNumber"],flush=True)
json.dump({"control_bahuang2":None if logs is None else len(logs),"numbi_30k":tot},open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-08-2131-numbi3.json","w"))
