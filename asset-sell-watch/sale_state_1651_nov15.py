import json, urllib.request
from eth_abi import encode, decode
from eth_utils import keccak
def sel(s): return keccak(text=s).hex()[:8]
def batch(calls):
    b=[{"jsonrpc":"2.0","id":i+1,"method":m,"params":p} for i,(m,p) in enumerate(calls)]
    for url in ["https://bsc-dataseed-public.bnbchain.org/","https://bsc-dataseed1.binance.org/","https://bsc-dataseed3.binance.org/","https://bsc-dataseed.binance.org/"]:
        try:
            req=urllib.request.Request(url,data=json.dumps(b).encode(),headers={"Content-Type":"application/json"})
            res=json.loads(urllib.request.urlopen(req,timeout=30).read())
            if isinstance(res,list) and any(isinstance(r,dict) and r.get("result") for r in res):
                return [r.get("result") if isinstance(r,dict) else None for r in res]
        except Exception:
            continue
    return [None]*len(calls)
def call(to,sig,args=(),types=()):
    d="0x"+sel(sig)+(encode(types,list(args)).hex() if args else "")
    r=batch([("eth_call",[{"to":to,"data":d},"latest"])])[0]
    return r
def u(h):
    try: return int(h,16) if h else None
    except: return None
def b(h):
    try: return decode(["bool"],bytes.fromhex(h[2:]))[0] if h else None
    except: return None
out={}
CHEEMSA="0x00b4bdA5BBf83A72f1252CCEf361f107f5a728b2"
out["CHEEMSA_tradingOpen"]=b(call(CHEEMSA,"tradingOpen()"))
out["CHEEMSA_mintDeadline"]=u(call(CHEEMSA,"mintDeadline()"))
out["CHEEMSA_launched"]=b(call(CHEEMSA,"launched()"))
out["CHEEMSA_isOpen"]=b(call(CHEEMSA,"isOpen()"))
out["PACTURE_launched"]=b(call("0x95AF9fe16fE5c1741b5E3F1b3b045a8c2470eca9","launched()"))
out["LUCKY777_launched"]=b(call("0xc6D4ec8CB889aFBa9f251606001457644E260f7D","launched()"))
out["JINMA_launched"]=b(call("0xe4517E6718b24D5725956ac7A90686592a7b1539","launched()"))
out["POA_launched"]=b(call("0x74d9b5477e7fa818298f927966452f2eb9c5fa5e","launched()"))
print(json.dumps(out,indent=1))
