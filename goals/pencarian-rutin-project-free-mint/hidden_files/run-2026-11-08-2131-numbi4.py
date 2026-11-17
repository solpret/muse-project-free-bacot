import sys, json, time
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
from datetime import datetime, timezone, timedelta
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x"+"00"*32
def ankr_logs_addr(addr,frm,to):
    body=ankr_post("ankr_getLogs",{"blockchain":"bsc","fromBlock":hex(frm),"toBlock":hex(to),"address":addr,"pageSize":1000,"decodeLogs":False,"topics":[TRANSFER,ZERO]},timeout=30)
    return body.get("result",{}).get("logs",[])
t0=time.time()
# control first
c=ankr_logs_addr("0x57CC350b844484Eac0DE444526d295C90F9cCbB5",132404126,132409469)
print(f"CONTROL BAHUANG2 via Ankr: {len(c)} mint logs in {time.time()-t0:.1f}s",flush=True)
n=ankr_logs_addr("0xeEdd6F512Fec64AD5A4aa64722ef6C5689937B50",132404126,132409469)
print(f"NUMBI via Ankr 132404126-132409469: {len(n)} mint logs",flush=True)
res={"control_bahuang2":len(c),"numbi_window":len(n)}
if n:
    first=min(n,key=lambda l:int(l["blockNumber"],16))
    print("NUMBI first in window:",first["blockNumber"],first["transactionHash"],flush=True)
    res["numbi_first_block"]=int(first["blockNumber"],16); res["numbi_first_tx"]=first["transactionHash"]
    # block timestamp via ankr? use eth_getBlockByNumber through ankr_post? try ankr raw? skip: use dataseed single call
    sys.path.insert(0,"/home/hatch/workspace/fast_exec")
    from fast_rpc import _post as fr_post
    for ep in ["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]:
        try:
            out=fr_post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_getBlockByNumber","params":[first["blockNumber"],False]},timeout=8,retries=0)
            ts=int(out["result"]["timestamp"],16)
            wib=datetime.fromtimestamp(ts,timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
            print("NUMBI first mint WIB:",wib,flush=True); res["numbi_first_wib"]=wib; res["numbi_first_ts"]=ts
            break
        except Exception as e:
            print("block ts fail",e,flush=True)
json.dump(res,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-08-2131-numbi4.json","w"),indent=1)
