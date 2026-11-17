import json, sys
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import get_logs
ADDR="0xcaa6554463a98f9afc966175694cd81ac7c41b41"
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x0000000000000000000000000000000000000000000000000000000000000000"
out={}
try:
    res=get_logs(ADDR, 132000000, "latest", topics=[TRANSFER, ZERO])
    logs=res.get("result",{}).get("logs",[])
    out["window"]=[132000000,"latest"]
    out["n_mint_logs"]=len(logs)
    out["nextPageToken"]=res.get("result",{}).get("nextPageToken")
    if logs:
        blocks=sorted(int(l["blockNumber"],16) for l in logs)
        out["earliest_mint_block"]=blocks[0]
        out["latest_mint_block"]=blocks[-1]
        out["first5"]=blocks[:5]
    json.dump(res, open("hot-leg-2026-11-09-0044-caa6-mintlogs.json","w"))
except Exception as e:
    out["error"]=f"{type(e).__name__}: {e}"
print(json.dumps(out,indent=1))
