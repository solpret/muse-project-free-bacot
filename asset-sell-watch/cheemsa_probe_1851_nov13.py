import json, urllib.request
from eth_utils import keccak
def sel(s): return keccak(text=s).hex()[:8]
ADDR="0x00b4bdA5BBf83A72f1252CCEf361f107f5a728b2"
sigs=["phase()","saleEnds()","mintEnd()","deadline()","endTime()","mintDeadline()","launched()","isOpen()","saleState()","status()","totalSharesSold()","freeSharesClaimed()","refundable()"]
ENDPOINTS=["https://bsc-dataseed1.binance.org/","https://bsc.publicnode.com","https://bsc-dataseed3.binance.org/"]
out={}
for sig in sigs:
    data="0x"+sel(sig)
    batch=[{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":ADDR,"data":data},"latest"]}]
    got=None
    for url in ENDPOINTS:
        try:
            req=urllib.request.Request(url,data=json.dumps(batch).encode(),headers={"Content-Type":"application/json"})
            r=json.loads(urllib.request.urlopen(req,timeout=10).read())
            if isinstance(r,list) and r and r[0].get("result"):
                got=r[0]["result"]; break
        except Exception as e:
            continue
    out[sig]=got
print(json.dumps(out,indent=1))
