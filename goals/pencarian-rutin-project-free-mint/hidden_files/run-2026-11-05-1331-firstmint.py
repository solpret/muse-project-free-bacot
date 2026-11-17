import json, urllib.request, sys, datetime
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
RPCS=["https://bsc-dataseed1.bnbchain.org","https://bsc-dataseed2.bnbchain.org"]
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x"+"00"*32
def block_ts(n):
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_getBlockByNumber","params":[hex(n),False]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=15) as r: out=json.load(r)
            return int(out["result"]["timestamp"],16)
        except Exception: continue
    return None
def first_mint(addr):
    lo, hi = 131755000, 131769375
    first=None
    while lo<=hi:
        end=min(lo+1999, hi)
        params={"blockchain":"bsc","fromBlock":hex(lo),"toBlock":hex(end),"pageSize":1000,"decodeLogs":False,"topics":[TRANSFER,ZERO],"address":addr}
        try:
            body=ankr_post("ankr_getLogs", params, timeout=30)
            result=body.get("result",{}) if isinstance(body,dict) else {}
            logs=result.get("logs",[])
            for lg in logs:
                if len(lg.get("topics",[]))==4:
                    b=int(lg["blockNumber"],16)
                    if first is None or b<first[0]: first=(b, lg.get("transactionHash"))
        except Exception as e:
            print("ERR",addr,lo,end,str(e)[:120]); return {"error":str(e)[:120]}
        if first is not None and first[0]<=end:
            # earliest in this chunk found; earlier chunks already scanned, so this is global earliest
            break
        lo=end+1
    if not first: return None
    ts=block_ts(first[0])
    wib=datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).isoformat() if ts else None
    return {"block":first[0],"tx":first[1],"ts":ts,"wib":wib}
res={}
for name,addr in [("Smeltbots","0xdC0004F3Efcc2aEA6052e138d3f1e680ca5D9b8e"),("Tumblebots","0x02f10432EAf9CbF72e1aC9b9208af601aADd6b17")]:
    fm=first_mint(addr); res[name]=fm; print(name,fm)
json.dump(res, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-05-1331-firstmint.json","w"), indent=1)
