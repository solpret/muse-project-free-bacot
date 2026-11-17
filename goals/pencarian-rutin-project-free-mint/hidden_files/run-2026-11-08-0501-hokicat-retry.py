import json, urllib.request
from Crypto.Hash import keccak
RPC="https://bsc.publicnode.com"
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def rpc(method,params):
    p=json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode()
    req=urllib.request.Request(RPC,data=p,headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=60) as r: return json.load(r)
H="0xdb51Dcc2D8cAf9942D9A975a2e68e023aB5E1fcA"
head=int(rpc("eth_blockNumber",[])["result"],16)
print("head",head)
out=json.load(open("run-2026-11-08-0501-hokicat-read.json"))
out["retry_rpc"]=RPC; out["retry_head"]=head
for f in ["FREE_CAP()","freeCount()","PRICE()","freeMinted()","totalMinted()"]:
    try:
        r=rpc("eth_call",[{"to":H,"data":sel(f)},"latest"])
        v=r.get("result")
        print(f, int(v,16) if v and v!="0x" else r)
        out["retry_"+f]=int(v,16) if v and v!="0x" else None
    except Exception as e:
        print(f,"ERR",str(e)[:100]); out["retry_"+f]="ERR:"+str(e)[:100]
topic0="0x"+keccak.new(digest_bits=256,data=b"Transfer(address,address,uint256)").hexdigest()
params={"fromBlock":hex(head-1000),"toBlock":hex(head),"address":H,"topics":[topic0,"0x0000000000000000000000000000000000000000000000000000000000000000"]}
try:
    lg=rpc("eth_getLogs",[params])
    logs=lg.get("result",[])
    print("mint logs last 1000 blocks:",len(logs))
    out["retry_mint_logs_1000"]=len(logs)
    if logs:
        print("first:",int(logs[0]["blockNumber"],16),logs[0]["transactionHash"])
        out["retry_first_mint_block"]=int(logs[0]["blockNumber"],16)
        out["retry_first_mint_tx"]=logs[0]["transactionHash"]
except Exception as e:
    print("getLogs ERR",str(e)[:120]); out["retry_mint_logs_1000"]="ERR:"+str(e)[:120]
json.dump(out,open("run-2026-11-08-0501-hokicat-read.json","w"),indent=2)
