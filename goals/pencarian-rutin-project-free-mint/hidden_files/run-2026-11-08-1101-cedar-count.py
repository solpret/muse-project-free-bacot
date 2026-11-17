import sys, json
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from ankr import ankr_post
from fast_rpc import batch as _batch
COLL="0x7ac89Ff65D1e4aa9C2BBCdEE0bBafAaa092B02bE"
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x"+"00"*32
head=int(_batch([("eth_blockNumber",[])],endpoint="https://bsc-dataseed1.bnbchain.org/",timeout=15)[0],16)
total=0; last=None; first=None; chunks=0; errs=[]
frm=132321293
while frm<=head:
    to_b=min(frm+999, head)
    try:
        body=ankr_post("ankr_getLogs",{"blockchain":"bsc","fromBlock":hex(frm),"toBlock":hex(to_b),"pageSize":1000,"decodeLogs":False,"address":COLL,"topics":[TRANSFER,ZERO]},timeout=30)
        logs=body.get("result",{}).get("logs",[])
        total+=len(logs)
        for l in logs:
            b=int(l.get("blockNumber","0x0"),16)
            first=b if first is None else min(first,b)
            last=b if last is None else max(last,b)
    except Exception as e:
        errs.append(f"{frm}-{to_b}: {e}")
    chunks+=1
    frm=to_b+1
print(json.dumps({"head":head,"total_mints":total,"first_block":first,"last_block":last,"chunks":chunks,"errors":errs},indent=1))
json.dump({"head":head,"total_mints":total,"first_block":first,"last_block":last,"chunks":chunks,"errors":errs},open('run-2026-11-08-1101-cedar-count.json','w'),indent=1)
