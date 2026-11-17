import json, subprocess, datetime
ADDR="0xB7517e3B31107695F2f8837fAFC76999b956C871"
T0="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x0000000000000000000000000000000000000000000000000000000000000000"
def rpc(ep,payload,timeout=60):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+10).stdout
    return json.loads(out)
# 1) all Transfer events, last 3000 blocks (should be >0 if minting recently; if 0, method/endpoint issue)
p={"jsonrpc":"2.0","id":1,"method":"eth_getLogs","params":[{"address":ADDR,"fromBlock":hex(133482229),"toBlock":"latest","topics":[T0]}]}
r=rpc("https://bsc-dataseed.binance.org/",p)
print("recent all-Transfer:", "ERR "+str(r.get("error"))[:100] if "error" in r else f"{len(r.get('result',[]))} logs")
if isinstance(r,dict) and r.get("result"):
    l=r["result"][0]; print("  sample block",int(l["blockNumber"],16),"from",l["topics"][1][-40:])
# 2) retry errored range alone, first-mint filter
p={"jsonrpc":"2.0","id":1,"method":"eth_getLogs","params":[{"address":ADDR,"fromBlock":hex(133410000),"toBlock":hex(133414999),"topics":[T0,ZERO]}]}
r=rpc("https://bsc-dataseed.binance.org/",p)
print("range 133410000-133414999 first-mint:", "ERR "+str(r.get("error"))[:100] if "error" in r else f"{len(r.get('result',[]))} logs")
if isinstance(r,dict) and r.get("result"):
    l=r["result"][0]; blk=int(l["blockNumber"],16)
    b=rpc("https://bsc-dataseed.binance.org/",{"jsonrpc":"2.0","id":1,"method":"eth_getBlockByNumber","params":[hex(blk),False]})
    ts=int(b["result"]["timestamp"],16)
    print("  first mint block",blk,"time WIB:",datetime.datetime.utcfromtimestamp(ts+7*3600).isoformat())
# 3) publicnode endpoint: first-mint filter over wide range in one call
p={"jsonrpc":"2.0","id":1,"method":"eth_getLogs","params":[{"address":ADDR,"fromBlock":hex(133400000),"toBlock":"latest","topics":[T0,ZERO]}]}
r=rpc("https://bsc-rpc.publicnode.com/",p)
print("publicnode wide first-mint:", "ERR "+str(r.get("error"))[:120] if "error" in r else f"{len(r.get('result',[]))} logs")
if isinstance(r,dict) and r.get("result"):
    l=r["result"][0]; blk=int(l["blockNumber"],16)
    b=rpc("https://bsc-rpc.publicnode.com/",{"jsonrpc":"2.0","id":1,"method":"eth_getBlockByNumber","params":[hex(blk),False]})
    ts=int(b["result"]["timestamp"],16)
    print("  first mint block",blk,"time WIB:",datetime.datetime.utcfromtimestamp(ts+7*3600).isoformat(),"token",int(l["topics"][3],16))
