import json, subprocess
ADDR="0xB7517e3B31107695F2f8837fAFC76999b956C871"
EP="https://bsc-dataseed.binance.org/"
T0="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x0000000000000000000000000000000000000000000000000000000000000000"
start,end=133410000,133485229
step=5000
ranges=[]; s=start
while s<=end:
    ranges.append((s,min(s+step-1,end))); s+=step
calls=[{"jsonrpc":"2.0","id":i+1,"method":"eth_getLogs","params":[{"address":ADDR,"fromBlock":hex(a),"toBlock":hex(b),"topics":[T0,ZERO]}]} for i,(a,b) in enumerate(ranges)]
out=subprocess.run(["curl","-sL","--max-time","60","-X","POST",EP,"-H","Content-Type: application/json","-d",json.dumps(calls)],capture_output=True,text=True,timeout=70).stdout
r=json.loads(out)
first=None; total=0; errs=0
for it,(a,b) in zip(r,ranges):
    if "error" in it: errs+=1; print("range",a,b,"ERR",it["error"].get("message","")[:80]); continue
    logs=it.get("result",[]); total+=len(logs)
    if logs and first is None: first=logs[0]
print("ranges",len(ranges),"errs",errs,"first-mint transfers total",total)
if first:
    blk=int(first["blockNumber"],16); print("first mint block",blk,"tx",first["transactionHash"],"token",int(first["topics"][3],16))
    # block timestamp
    out2=subprocess.run(["curl","-sL","--max-time","30","-X","POST",EP,"-H","Content-Type: application/json","-d",json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_getBlockByNumber","params":[hex(blk),False]})],capture_output=True,text=True,timeout=40).stdout
    b2=json.loads(out2).get("result",{})
    import datetime
    ts=int(b2.get("timestamp","0x0"),16)
    print("first mint time UTC:",datetime.datetime.utcfromtimestamp(ts).isoformat(),"WIB:",datetime.datetime.utcfromtimestamp(ts+7*3600).isoformat())
