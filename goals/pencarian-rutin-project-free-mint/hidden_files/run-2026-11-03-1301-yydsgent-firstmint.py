import sys, json
sys.path.insert(0,"/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
sys.path.insert(0,"/home/hatch/workspace/fast_exec")
sys.path.insert(0,"/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from onchain_nft_scan import rpc_call
from ankr import ankr_post
ADDR="0x38CB2dF1D6Fdac4115883E6EC7d2Ff39e20C1e61"
def ts(block):
    r=rpc_call("eth_call",[{"to":ADDR,"data":"0x18160ddd"},hex(block)])
    return int(r,16) if isinstance(r,str) and len(r)==66 else None
head=int(rpc_call("eth_blockNumber",[]),16)
print("head",head,"current totalSupply",ts(head),flush=True)
lo,hi=131300000,head
# invariant: ts(lo)==0 assumed? check
print("ts(lo)",ts(lo),flush=True)
while lo+1<hi:
    mid=(lo+hi)//2
    v=ts(mid)
    if v and v>0: hi=mid
    else: lo=mid
print("first nonzero block approx",hi,"totalSupply",ts(hi),"prev",ts(hi-1),flush=True)
# block timestamp
blk=rpc_call("eth_getBlockByNumber",[hex(hi),False])
print("block timestamp", blk.get('timestamp'), int(blk['timestamp'],16) if blk else None, flush=True)
# Ankr address-filtered logs around first block
try:
    body=ankr_post("ankr_getLogs",{"blockchain":"bsc","fromBlock":hex(max(131300000,hi-2000)),"toBlock":hex(hi+50),"address":ADDR,"pageSize":1000,"decodeLogs":False},timeout=30)
    logs=body.get("result",{}).get("logs",[])
    print("ankr logs in window:",len(logs),flush=True)
    for l in logs[:5]: print(l.get("blockNumber"), l.get("transactionHash"), l.get("topics",[])[:2], flush=True)
    if logs:
        first=min(logs,key=lambda l:int(l["blockNumber"],16))
        print("earliest log block", int(first["blockNumber"],16), first.get("transactionHash"), flush=True)
except Exception as e:
    print("ankr ERR", type(e).__name__, str(e)[:200], flush=True)
