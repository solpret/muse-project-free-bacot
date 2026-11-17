import json, urllib.request
from eth_abi import encode, decode
from eth_utils import keccak
def sel(s): return keccak(text=s).hex()[:8]
def call(to, data):
    body=[{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}]
    req=urllib.request.Request("https://bsc-dataseed.binance.org/", data=json.dumps(body).encode(), headers={"Content-Type":"application/json"})
    r=json.loads(urllib.request.urlopen(req, timeout=30).read())
    return r[0].get("result") if isinstance(r, list) and r and isinstance(r[0], dict) else None
out={}
# 币安加油 pair reserves (retry, 3 attempts)
pair="0xc939e2b49eea548c4539e45b4e355c2b2aa464d6"
for i in range(3):
    h=call(pair,"0x"+sel("getReserves()"))
    if h:
        r0,r1,_=decode(["uint112","uint112","uint32"], bytes.fromhex(h[2:]))
        out["bianjiayou_reserves"]=[str(r0),str(r1)]; out["bianjiayou_attempt"]=i+1; break
    out["bianjiayou_attempt"]=i+1
# KAGENT launched()
for i in range(3):
    h=call("0xb34105002B19EF0ce43B59011fE848df5c8B174f","0x"+sel("launched()"))
    if h:
        out["kagent_launched"]=decode(["bool"], bytes.fromhex(h[2:]))[0]; out["kagent_attempt"]=i+1; break
    out["kagent_attempt"]=i+1
print(json.dumps(out, indent=1))
