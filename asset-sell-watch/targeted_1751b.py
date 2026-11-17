import json, urllib.request
from eth_abi import encode, decode
from eth_utils import keccak
ROUTER="0x10ED43C718714eb63d5aA57B78B54704E256024E"
FACTORY="0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB="0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
BAY="0x397BF425926F521Ac5BEbe5062793BB224e3eF8f"
KAGENT="0xb34105002B19EF0ce43B59011fE848df5c8B174f"
URLS=["https://bsc-dataseed1.defibit.io/","https://bsc-dataseed2.binance.org/","https://bsc-dataseed3.binance.org/","https://bsc-dataseed1.binance.org/"]
def sel(s): return keccak(text=s).hex()[:8]
def call(url,to,data):
    req=urllib.request.Request(url,data=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode(),headers={"Content-Type":"application/json"})
    try:
        r=json.loads(urllib.request.urlopen(req,timeout=30).read())
        return r.get("result") if not r.get("error") else None
    except Exception:
        return None
def u256(h):
    try: return int(h,16) if h else 0
    except Exception: return 0
out={}
for label,tok in [("bay",BAY),("kagent",KAGENT)]:
    for url in URLS:
        pair_h=call(url,FACTORY,"0x"+sel("getPair(address,address)")+encode(["address","address"],[tok,WBNB]).hex())
        pair=("0x"+pair_h[-40:]) if pair_h and u256(pair_h) else None
        if pair:
            d={"pair":pair,"url":url}
            res_h=call(url,pair,"0x"+sel("getReserves()"))
            if res_h:
                r0,r1,_=decode(["uint112","uint112","uint32"],bytes.fromhex(res_h[2:]))
                d["reserves"]=[str(r0),str(r1)]
            out[label]=d; break
    else:
        out[label]={"status":"pair_not_returned_on_any_endpoint"}
print(json.dumps(out,indent=1,ensure_ascii=False))
