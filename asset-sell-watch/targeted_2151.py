import json, urllib.request
from eth_abi import encode, decode
from eth_utils import keccak

def sel(sig): return keccak(text=sig).hex()[:8]
def rpc(url, calls):
    batch=[{"jsonrpc":"2.0","id":i+1,"method":m,"params":p} for i,(m,p) in enumerate(calls)]
    req=urllib.request.Request(url,data=json.dumps(batch).encode(),headers={"Content-Type":"application/json"})
    try:
        return json.loads(urllib.request.urlopen(req,timeout=30).read())
    except Exception as e:
        return [{"error":str(e)} for _ in calls]

calls=[("eth_call",[{"to":"0xb34105002B19EF0ce43B59011fE848df5c8B174f","data":"0x"+sel("launched()")},"latest"])]
for url in ["https://bsc-dataseed.binance.org/","https://bsc-dataseed2.binance.org/","https://bsc-dataseed1.defibit.io/"]:
    res=rpc(url,calls)
    r=res[0]
    if isinstance(r,dict) and r.get("result"):
        try:
            print(json.dumps({"endpoint":url,"launched":decode(["bool"],bytes.fromhex(r["result"][2:]))[0],"raw":r["result"]}))
        except Exception as ex:
            print(json.dumps({"endpoint":url,"decode_error":str(ex),"raw":r["result"]}))
        break
    else:
        print(json.dumps({"endpoint":url,"failed":r}))
