import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x"+"00"*32
ADDR="0x79720611065DF9Fc810399DC1eeE870b3A8AD3fC"
FB=131898146
def ankr_logs(frm,to):
    params={"blockchain":"bsc","fromBlock":hex(frm),"toBlock":hex(to),"pageSize":1000,"decodeLogs":False,"topics":[TRANSFER, ZERO],"address":ADDR}
    body=ankr_post("ankr_getLogs", params, timeout=30)
    return body.get("result",{}).get("logs",[]) if isinstance(body,dict) else []
earlier=0; failed=False; start=131890000
while start < FB:
    end=min(start+1999, FB-1)
    ok=False
    for attempt in range(3):
        try:
            logs=ankr_logs(start,end); earlier+=len(logs); ok=True; break
        except Exception as e:
            print("chunk",start,end,"attempt",attempt,"FAIL",repr(e),flush=True); time.sleep(3)
    if not ok:
        failed=True; break
    start=end+1
    time.sleep(0.5)
print("Unnamed-7972 earlier_mints=", None if failed else earlier, "verified=", (not failed) and earlier==0)
json.dump({"address":ADDR,"earlier_mints_before_first_block":None if failed else earlier,"first_mint_verified":(not failed) and earlier==0},
          open(f"{BASE}/run-2026-11-06-0731-early-verify-retry2.json","w"), indent=1)
