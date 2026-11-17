#!/usr/bin/env python3
"""Binary-search Botkirin deploy block via eth_getCode, then first-mint via small-range getLogs."""
import json, urllib.request, datetime
ADDR="0xe43818c2c6080e9d2bef53db14092806b51711d2"
TOPIC0="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x0000000000000000000000000000000000000000000000000000000000000000"
RPC="https://bsc-dataseed1.bnbchain.org"
def post(method, params, timeout=15):
    body=json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode()
    req=urllib.request.Request(RPC,data=body,headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=timeout) as r: return json.load(r)
def has_code(blk):
    o=post("eth_getCode",[ADDR,hex(blk)])
    v=o.get("result","0x")
    return v and v!="0x"
lo,hi=131900000,132054301
# check lo first
if has_code(lo):
    print("code already at lo 131900000; deploy earlier - widening needed")
else:
    while hi-lo>1:
        mid=(lo+hi)//2
        if has_code(mid): hi=mid
        else: lo=mid
    print("deploy block:",hi)
    ts=post("eth_getBlockByNumber",[hex(hi),False])["result"]["timestamp"]
    ts=int(ts,16)
    wib=datetime.datetime.fromtimestamp(ts,datetime.timezone(datetime.timedelta(hours=7)))
    print("deploy ts:",ts,"wib:",wib.strftime("%Y-%m-%d %H:%M:%S"))
    # first mint: getLogs from deploy block, 2000-block chunks
    start=hi; found=None
    while start<=132054301 and not found:
        end=min(start+1999,132054301)
        try:
            o=post("eth_getLogs",[{"fromBlock":hex(start),"toBlock":hex(end),"address":ADDR,"topics":[TOPIC0,ZERO]}],timeout=20)
        except Exception as e:
            print("getLogs chunk",start,"-",end,"EXC",e); break
        if "error" in o:
            print("getLogs chunk",start,"-",end,"error:",o["error"]); break
        logs=o.get("result",[])
        if logs:
            f=logs[0]; blk=int(f["blockNumber"],16)
            ts2=int(post("eth_getBlockByNumber",[f["blockNumber"],False])["result"]["timestamp"],16)
            w2=datetime.datetime.fromtimestamp(ts2,datetime.timezone(datetime.timedelta(hours=7)))
            print("first mint block:",blk,"wib:",w2.strftime("%Y-%m-%d %H:%M:%S"),"tx:",f["transactionHash"],"tokenId:",int(f["topics"][3],16))
            found={"first_mint_block":blk,"ts":ts2,"wib":w2.strftime("%Y-%m-%d %H:%M:%S WIB"),"tx":f["transactionHash"],"tokenId":int(f["topics"][3],16)}
            break
        start=end+1
    if found:
        json.dump({"deploy_block":hi,"deploy_wib":wib.strftime("%Y-%m-%d %H:%M:%S WIB"),**found},open("hot-leg-2026-11-07-0104-firstmint.json","w"),indent=1)
    else:
        print("first mint NOT found in range (getLogs limit or no mints in scanned chunks)")
