#!/usr/bin/env python3
"""Find Botkirin first mint block via eth_getLogs Transfer(from=0x0)."""
import json, urllib.request, datetime
ADDR="0xe43818c2c6080e9d2bef53db14092806b51711d2"
TOPIC0="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x0000000000000000000000000000000000000000000000000000000000000000"
RPCS=["https://rpc.ankr.com/bsc","https://bsc-dataseed1.bnbchain.org","https://bsc.publicnode.com"]
def post(rpc, method, params, timeout=20):
    body=json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode()
    req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=timeout) as r: return json.load(r)
def get_block_ts(rpc, blk_hex):
    o=post(rpc,"eth_getBlockByNumber",[blk_hex,False],timeout=10)
    b=o.get("result") or {}
    return int(b["timestamp"],16) if b.get("timestamp") else None
for rpc in RPCS:
    try:
        o=post(rpc,"eth_getLogs",[{"fromBlock":"0x7dd8a20","toBlock":"latest","address":ADDR,"topics":[TOPIC0,ZERO]}],timeout=30)
        if "error" in o:
            print(rpc,"error:",o["error"]); continue
        logs=o.get("result",[])
        print(rpc,"logs:",len(logs))
        if logs:
            first=logs[0]
            blk=int(first["blockNumber"],16)
            ts=get_block_ts(rpc, first["blockNumber"])
            wib=datetime.datetime.fromtimestamp(ts,datetime.timezone(datetime.timedelta(hours=7)))
            print("first mint block:",blk,"ts:",ts,"wib:",wib.strftime("%Y-%m-%d %H:%M:%S"),"tx:",first["transactionHash"],"tokenId:",int(first["topics"][3],16))
            json.dump({"first_mint_block":blk,"ts":ts,"wib":wib.strftime("%Y-%m-%d %H:%M:%S WIB"),"tx":first["transactionHash"],"tokenId":int(first["topics"][3],16),"logs_total":len(logs),"via":rpc},open("hot-leg-2026-11-07-0104-firstmint.json","w"),indent=1)
            break
        else:
            print("no logs in range - contract older than fromBlock 0x7dd8a20 (131900000)")
    except Exception as e:
        print(rpc,"EXC:",type(e).__name__,e)
