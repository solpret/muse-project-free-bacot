import json, urllib.request
from Crypto.Hash import keccak
RPCS=["https://bsc-dataseed.binance.org","https://bsc-dataseed1.defibit.io","https://bsc.publicnode.com"]
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def call(rpc,to,data,block="latest"):
    p=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest" if block=="latest" else hex(block)]}).encode()
    req=urllib.request.Request(rpc,data=p,headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=30) as r: return json.load(r)
def getblock(rpc):
    p=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}).encode()
    req=urllib.request.Request(rpc,data=p,headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=30) as r: return int(json.load(r)["result"],16)
H="0xdb51Dcc2D8cAf9942D9A975a2e68e023aB5E1fcA"
fns=["totalMinted()","freeMinted()","FREE_CAP()","FREE_PER_WALLET()","mintOpen()","name()","symbol()","totalSupply()","freeCount()","MAX_SUPPLY()","PRICE()","paidMintedCount()"]
out={}
for rpc in RPCS[:1]:
    head=getblock(rpc); out["head"]=head
    print("head",head)
    for f in fns:
        try:
            r=call(rpc,H,sel(f))
            v=r.get("result")
            if v and v!="0x":
                try: val=int(v,16)
                except: val=v
                print(f,repr(val) if isinstance(val,int) else v[:120])
                out[f]=val if isinstance(val,int) else v[:120]
            else:
                print(f,"REVERT/empty",r.get("error"))
                out[f]=None
        except Exception as e:
            print(f,"ERR",e); out[f]="ERR:"+str(e)[:80]
# getLogs Transfer from 0x0, last 1000 blocks
topic0="0x"+keccak.new(digest_bits=256,data=b"Transfer(address,address,uint256)").hexdigest()
frm="0x"+"0"*24+"0"*40
params={"fromBlock":hex(head-1000),"toBlock":hex(head),"address":H,"topics":[topic0,"0x0000000000000000000000000000000000000000000000000000000000000000"]}
p=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_getLogs","params":[params]}).encode()
req=urllib.request.Request(RPCS[0],data=p,headers={"Content-Type":"application/json"})
try:
    with urllib.request.urlopen(req,timeout=60) as r: lg=json.load(r)
    logs=lg.get("result",[])
    print("transfer-from-zero logs in last 1000 blocks:",len(logs))
    out["mint_logs_1000"]=len(logs)
    if logs:
        print("first log block:",int(logs[0]["blockNumber"],16),"tx:",logs[0]["transactionHash"])
        out["first_mint_block"]=int(logs[0]["blockNumber"],16)
        out["first_mint_tx"]=logs[0]["transactionHash"]
    else:
        out["first_mint_block"]=None
except Exception as e:
    print("getLogs ERR",e); out["mint_logs_1000"]="ERR:"+str(e)[:100]
json.dump(out,open("run-2026-11-08-0501-hokicat-read.json","w"),indent=2)
