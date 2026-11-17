import json, urllib.request
from eth_abi import encode, decode
from eth_utils import keccak
def sel(s): return keccak(text=s).hex()[:8]
ENDPOINTS=["https://bsc-dataseed1.binance.org/","https://bsc-dataseed3.binance.org/","https://bsc.publicnode.com","https://bsc-dataseed2.binance.org/"]
def rpc(url,method,params):
    p=json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode()
    req=urllib.request.Request(url,data=p,headers={"Content-Type":"application/json"})
    r=json.loads(urllib.request.urlopen(req,timeout=20).read())
    return r.get("result") if not r.get("error") else None
def call(to,sig):
    d="0x"+sel(sig)
    for u in ENDPOINTS:
        try:
            r=rpc(u,"eth_call",[{"to":to,"data":d},"latest"])
            if r is not None: return r
        except Exception: continue
    return None
def b(h):
    try: return decode(["bool"],bytes.fromhex(h[2:]))[0] if h else None
    except: return None
def u(h):
    try: return int(h,16) if h else None
    except: return None
C="0x00b4bdA5BBf83A72f1252CCEf361f107f5a728b2"
out={}
out["CHEEMSA_tradingOpen"]=b(call(C,"tradingOpen()"))
out["CHEEMSA_mintDeadline"]=u(call(C,"mintDeadline()"))
out["CHEEMSA_launched"]=b(call(C,"launched()"))
out["CHEEMSA_isOpen"]=b(call(C,"isOpen()"))
out["PACTURE_launched"]=b(call("0x95AF9fe16fE5c1741b5E3F1b3b045a8c2470eca9","launched()"))
out["LUCKY777_launched"]=b(call("0xc6D4ec8CB889aFBa9f251606001457644E260f7D","launched()"))
out["JINMA_launched"]=b(call("0xe4517E6718b24D5725956ac7A90686592a7b1539","launched()"))
out["POA_launched"]=b(call("0x74d9b5477e7fa818298f927966452f2eb9c5fa5e","launched()"))
print(json.dumps(out,indent=1))
