import json, urllib.request
from eth_abi import encode, decode
from eth_utils import keccak
ROUTER="0x10ED43C718714eb63d5aA57B78B54704E256024E"
WBNB="0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
YYDS="0xd23be069c3c3a7f631af52584a16a9e46bb41da1"
PAIR="0xd15c928b7b777cac7d613fe840c6ec3de8e4edda"
def sel(s): return keccak(text=s).hex()[:8]
def call(url,to,data):
    req=urllib.request.Request(url,data=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode(),headers={"Content-Type":"application/json"})
    try:
        r=json.loads(urllib.request.urlopen(req,timeout=30).read())
        return r.get("result") if not r.get("error") else None
    except Exception:
        return None
for url in ["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.binance.org/","https://bsc-dataseed1.defibit.io/"]:
    res_h=call(url,PAIR,"0x"+sel("getReserves()"))
    print(url,"reserves raw:",res_h)
    if res_h:
        r0,r1,_=decode(["uint112","uint112","uint32"],bytes.fromhex(res_h[2:]))
        print(" reserves:",r0,r1)
        q_h=call(url,ROUTER,"0x"+sel("getAmountsOut(uint256,address[])")+encode(["uint256","address[]"],[177600000000000,[YYDS,WBNB]]).hex())
        print(" quote raw:",q_h)
        if q_h:
            outs=decode(["uint256[]"],bytes.fromhex(q_h[2:]))[0]
            print(" quote BNB:",outs[1]/1e18)
        break
