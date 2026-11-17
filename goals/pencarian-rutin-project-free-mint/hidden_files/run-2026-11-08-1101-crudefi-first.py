import sys, json
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from ankr import ankr_post
from fast_rpc import batch as _batch
ADDR="0x60FBe0ddC05A4B4bae047B816d77f5E6B68306E2"
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x"+"00"*32
head=int(_batch([("eth_blockNumber",[])],endpoint="https://bsc-dataseed1.bnbchain.org/",timeout=15)[0],16)
# single address-filtered query over last 200k blocks (85 total mints max, pageSize 1000 is plenty)
frm=head-200000
body=ankr_post("ankr_getLogs",{"blockchain":"bsc","fromBlock":hex(frm),"toBlock":hex(head),"pageSize":1000,"decodeLogs":False,"address":ADDR,"topics":[TRANSFER,ZERO]},timeout=60)
logs=body.get("result",{}).get("logs",[])
print("head", head, "logs in last 200k blocks:", len(logs))
if logs:
    blks=sorted(int(l.get("blockNumber","0x0"),16) for l in logs)
    print("first mint block:", blks[0], "last:", blks[-1], "count:", len(blks))
    # block timestamp of first mint via dataseed eth_getBlockByNumber
    b=_batch([("eth_getBlockByNumber",[hex(blks[0]),False])],endpoint="https://bsc-dataseed1.bnbchain.org/",timeout=15)[0]
    print("first mint block ts:", b.get("timestamp"), "->", int(b["timestamp"],16))
    import datetime
    print("first mint WIB:", datetime.datetime.fromtimestamp(int(b["timestamp"],16), datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB"))
json.dump({"head":head,"n_logs":len(logs),"first_block":blks[0] if logs else None,"last_block":blks[-1] if logs else None}, open('run-2026-11-08-1101-crudefi-first.json','w'), indent=1)
