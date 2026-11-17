import sys, json
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from ankr import ankr_post
from fast_rpc import batch
CAB="0xa8543350e5accacc780c9613bfa2fb9b52d3858e"
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x0000000000000000000000000000000000000000000000000000000000000000"
head=int(batch([("eth_blockNumber",[])], endpoint="https://bsc-dataseed1.bnbchain.org/", timeout=10)[0],16)
print("head",head,flush=True)
def exists(fb,tb):
    body=ankr_post("ankr_getLogs",{"blockchain":"bsc","fromBlock":hex(fb),"toBlock":hex(tb),
        "address":CAB,"topics":[TRANSFER,ZERO,None]})
    logs=body.get("result",{}).get("logs",[]) if isinstance(body,dict) else []
    return len(logs)
# window: last 500k blocks (~62h) - covers 48h cutoff
lo=head-500000
n=exists(lo,head)
print(f"exists [{lo},{head}]: {n} logs (1000=truncated, presence only)",flush=True)
if n==0:
    print(json.dumps({"head":head,"verdict":"NO_MINT_IN_LAST_500K_BLOCKS_age_gt_62h"}))
    raise SystemExit
# binary search earliest mint block
a,b=lo,head
while a<b:
    mid=(a+b)//2
    c=exists(a,mid)
    print(f"  [{a},{mid}]: {c}",flush=True)
    if c>0: b=mid
    else: a=mid+1
print("earliest mint block:",a,flush=True)
# timestamp of that block via dataseed (NOT Ankr - fake timestamps)
blk=batch([("eth_getBlockByNumber",[hex(a),False])], endpoint="https://bsc-dataseed1.bnbchain.org/", timeout=10)[0]
ts=int(blk["timestamp"],16)
import datetime
wib=datetime.datetime.fromtimestamp(ts,datetime.timezone(datetime.timedelta(hours=7)))
print("block ts:",ts,"WIB:",wib.strftime("%Y-%m-%d %H:%M:%S"))
json.dump({"head":head,"first_mint_block":a,"first_mint_ts":ts,"first_mint_wib":wib.strftime("%Y-%m-%d %H:%M:%S WIB")},
          open("cabinette-0839-firstmint.json","w"),indent=1)
