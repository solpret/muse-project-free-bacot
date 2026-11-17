import json, subprocess, time
ADDR="0xBb9bA68C8E99651450F099C431eb530a71C712bE"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EP="https://bsc-dataseed.binance.org/"
def rpc(method, params, timeout=60):
    p=json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params})
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",EP,"-H","Content-Type: application/json","-d",p],capture_output=True,text=True,timeout=timeout+10).stdout
    return json.loads(out)
head=int(rpc("eth_blockNumber",[]).get("result","0x0"),16)
print("head",head,flush=True)
ZERO="0x"+"0"*64
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
# search backwards in 2000-block chunks for Transfer from zero to this contract, max 20000 blocks
found=[]
for start in range(head-2000, head-22000, -2000):
    end=start+1999
    try:
        r=rpc("eth_getLogs",[{"fromBlock":hex(start),"toBlock":hex(end),"address":ADDR,"topics":[TRANSFER,ZERO]}],timeout=60)
        logs=r.get("result") or []
        print(f"chunk {start}-{end}: {len(logs)} mint logs",flush=True)
        if logs:
            found.extend(logs)
            break
    except Exception as e:
        print(f"chunk {start}-{end} ERR {e}",flush=True)
if found:
    first=min(found,key=lambda l:int(l["blockNumber"],16))
    blk=int(first["blockNumber"],16)
    ts=int(rpc("eth_getBlockByNumber",[hex(blk),False]).get("result",{}).get("timestamp","0x0"),16)
    import datetime
    print("FIRST MINT block",blk,"ts",ts,datetime.datetime.fromtimestamp(ts,datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB"),"total mint logs in window:",len(found),flush=True)
    json.dump({"first_mint_block":blk,"first_mint_ts":ts,"logs_in_chunk":len(found)},open("run-2026-11-16-2231-woof-firstmint.json","w"))
else:
    print("NO mint logs in last 20000 blocks - first mint older or logs unavailable",flush=True)
