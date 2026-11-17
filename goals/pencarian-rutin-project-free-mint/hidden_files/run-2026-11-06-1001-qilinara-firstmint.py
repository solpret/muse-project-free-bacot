import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
addr="0x46d0eE06a3b919091B006D7818C3Ae405E0f3774"
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x"+"00"*32
logs=[]; errs=[]
# single wide call 131060000..131899999
try:
    b=ankr_post("ankr_getLogs",{"blockchain":"bsc","fromBlock":hex(131060000),"toBlock":hex(131899999),"pageSize":1000,"decodeLogs":False,"topics":[TRANSFER,ZERO],"address":addr.lower()},timeout=60)
    logs=b.get("result",{}).get("logs",[]) if isinstance(b,dict) else []
    print("wide single call logs:",len(logs),flush=True)
except Exception as e:
    errs.append(str(e)); print("single call FAILED",repr(e),flush=True)
    cur=131060000
    while cur<=131899999:
        to=min(cur+9999,131899999)
        try:
            b=ankr_post("ankr_getLogs",{"blockchain":"bsc","fromBlock":hex(cur),"toBlock":hex(to),"pageSize":1000,"decodeLogs":False,"topics":[TRANSFER,ZERO],"address":addr.lower()},timeout=30)
            logs+=b.get("result",{}).get("logs",[]) if isinstance(b,dict) else []
        except Exception as e2:
            errs.append(f"{cur}-{to}:{e2}")
        cur=to+1
    print("chunked total logs:",len(logs),flush=True)
if logs:
    first=min(int(l["blockNumber"],16) for l in logs)
    print("FIRST_MINT_BLOCK",first,"COUNT",len(logs),"ERRORS",errs)
    json.dump({"first_mint_block":first,"count":len(logs),"errors":errs},open(f"{BASE}/run-2026-11-06-1001-qilinara-firstmint.json","w"))
else:
    print("NO LOGS in range; errors:",errs)
