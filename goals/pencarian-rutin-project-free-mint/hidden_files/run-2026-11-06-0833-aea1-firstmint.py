import json, urllib.request
ADDR="0xAeA1433dBD9e7edE0914d996C2Dad692E6e01e09"
RPCS=["https://bsc-dataseed1.bnbchain.org","https://bsc.publicnode.com"]
TOPIC="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x0000000000000000000000000000000000000000000000000000000000000000"
def rpc(method,params):
    for url in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode()
            req=urllib.request.Request(url,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=15) as r: return json.load(r)
        except Exception as e:
            last=e; continue
    return {"error":str(last)}
# current block
cur=rpc("eth_blockNumber",[])
print("CUR",cur)
cur=int(cur["result"],16)
frm=cur-20000  # ~16.7h back
res=rpc("eth_getLogs",[{"fromBlock":hex(frm),"toBlock":"latest","address":ADDR,"topics":[TOPIC,ZERO]}])
print("LOGS-ERR" if "error" in res else f"LOGS n={len(res.get('result',[]))} fromBlock={frm}")
logs=res.get("result",[])
if logs:
    first=logs[0]
    print("FIRST mint log block",int(first["blockNumber"],16),"tx",first["transactionHash"],"idx",int(first["logIndex"],16))
    blk=rpc("eth_getBlockByNumber",[first["blockNumber"],False])
    ts=int(blk["result"]["timestamp"],16)
    import datetime
    print("FIRST mint time UTC",datetime.datetime.utcfromtimestamp(ts).isoformat(),"WIB",(datetime.datetime.utcfromtimestamp(ts)+datetime.timedelta(hours=7)).isoformat())
    print("TOTAL mint Transfer logs in window:",len(logs))
    json.dump({"fromBlock":frm,"count":len(logs),"first":first,"firstMintTs":ts},open("run-2026-11-06-0833-aea1-firstmint.json","w"),indent=1)
else:
    print("NO mint logs in window - contract may be older than window or no mints via Transfer")
