import json, subprocess
from Crypto.Hash import keccak
ADDR="0xBb9bA68C8E99651450F099C431eb530a71C712bE"
EP="https://bsc-dataseed.binance.org/"
def rpc(method, params, timeout=60):
    p=json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params})
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",EP,"-H","Content-Type: application/json","-d",p],capture_output=True,text=True,timeout=timeout+10).stdout
    return json.loads(out)
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
head=int(rpc("eth_blockNumber",[]).get("result","0x0"),16)
print("head",head,flush=True)
data=sel("totalSupply()")
for blk in [head, head-2000, head-10000, head-20000, head-40000]:
    r=rpc("eth_call",[{"to":ADDR,"data":data},hex(blk)])
    res=r.get("result")
    print("totalSupply @",blk,"=",int(res,16) if res else r,flush=True)
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
r=rpc("eth_getLogs",[{"fromBlock":hex(head-2000),"toBlock":hex(head),"address":ADDR}],timeout=60)
logs=r.get("result")
print("all logs to contract last 2000 blocks:", len(logs) if isinstance(logs,list) else r,flush=True)
if isinstance(logs,list) and logs:
    for l in logs[:5]: print(" ",l.get("topics",[None])[0],"block",int(l["blockNumber"],16),flush=True)
