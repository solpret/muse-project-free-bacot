import sys, json
sys.path.insert(0,"/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
ADDR="0x38CB2dF1D6Fdac4115883E6EC7d2Ff39e20C1e61"
for frm,to in [(131200000,131384000)]:
    try:
        body=ankr_post("ankr_getLogs",{"blockchain":"bsc","fromBlock":hex(frm),"toBlock":hex(to),"address":ADDR,"pageSize":1000,"decodeLogs":False},timeout=60)
        logs=body.get("result",{}).get("logs",[])
        print("window",frm,to,"logs",len(logs), "pageToken?", bool(body.get("result",{}).get("nextPageToken")), flush=True)
        if logs:
            logs_sorted=sorted(logs,key=lambda l:int(l["blockNumber"],16))
            for l in logs_sorted[:3]: print("first:",int(l["blockNumber"],16),l.get("transactionHash"),l.get("topics",[]),flush=True)
            for l in logs_sorted[-3:]: print("last:",int(l["blockNumber"],16),l.get("transactionHash"),flush=True)
            print("distinct tx:", len({l.get("transactionHash") for l in logs}), flush=True)
    except Exception as e:
        print("ERR",type(e).__name__,str(e)[:300],flush=True)
