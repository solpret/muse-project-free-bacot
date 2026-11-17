import sys, json
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _post as fr_post
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed.binance.org/"]
ADDR="0xeEdd6F512Fec64AD5A4aa64722ef6C5689937B50"
def getlogs(params,tag):
    for ep in EPS:
        try:
            out=fr_post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_getLogs","params":[params]},timeout=15,retries=0)
            r=out.get("result",[])
            print(tag, "->", len(r), "logs", flush=True)
            return r
        except Exception as e:
            print(tag,"err",ep,e,flush=True); continue
    return None
frm,to=132404126,132409469
# all Transfer (any from) for contract
logs=getlogs({"fromBlock":hex(frm),"toBlock":hex(to),"address":ADDR,"topics":["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"]},"all-Transfer")
if logs:
    for l in logs[:5]: print(" ",l["blockNumber"],l["topics"],l["transactionHash"],flush=True)
# TransferSingle any
logs2=getlogs({"fromBlock":hex(frm),"toBlock":hex(to),"address":ADDR,"topics":["0xc3d58168c5ae7397731d063d5bbf3d657854427343f4c083240f7aacaa2d0f62"]},"TransferSingle")
if logs2:
    for l in logs2[:5]: print(" ",l["blockNumber"],l["topics"],flush=True)
# any logs at all for address in range (no topics)
logs3=getlogs({"fromBlock":hex(frm),"toBlock":hex(to),"address":ADDR},"any-topic")
# name/symbol/totalSupply fresh
def call(data):
    for ep in EPS:
        try:
            out=fr_post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":ADDR,"data":data},"latest"]},timeout=8,retries=0)
            return out.get("result")
        except Exception: continue
    return None
print("totalSupply raw:",call("0x18160ddd"),flush=True)
print("code len:",len(call("0x") or "") if False else "(skip)",flush=True)
# eth_getCode via fr_post
for ep in EPS:
    try:
        out=fr_post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[ADDR,"latest"]},timeout=8,retries=0)
        print("code bytes:",(len(out["result"])-2)//2,flush=True); break
    except Exception as e: print("code err",e,flush=True)
