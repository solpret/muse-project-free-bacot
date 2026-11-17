import json, urllib.request
from eth_abi import encode, decode
from eth_utils import keccak
W="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ROUTER="0x10ED43C718714eb63d5aA57B78B54704E256024E"
FACTORY="0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB="0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
YYDS="0xd23be069c3c3a7f631af52584a16a9e46bb41da1"
KAGENT_SALE="0xb34105002B19EF0ce43B59011fE848df5c8B174f"
def sel(s): return keccak(text=s).hex()[:8]
def call(url,to,data):
    req=urllib.request.Request(url,data=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode(),headers={"Content-Type":"application/json"})
    try:
        r=json.loads(urllib.request.urlopen(req,timeout=30).read())
        return r.get("result") if not r.get("error") else None
    except Exception as e:
        return None
def u256(h):
    try: return int(h,16) if h else 0
    except Exception: return 0
for url in ["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.defibit.io/","https://bsc-dataseed1.binance.org/"]:
    pair_h=call(url,FACTORY,"0x"+sel("getPair(address,address)")+encode(["address","address"],[YYDS,WBNB]).hex())
    pair=("0x"+pair_h[-40:]) if pair_h and u256(pair_h) else None
    print(url,"YYDS pair:",pair, "raw:", pair_h)
    if pair:
        res_h=call(url,pair,"0x"+sel("getReserves()"))
        print(" reserves raw:",res_h)
        if res_h:
            r0,r1,_=decode(["uint112","uint112","uint32"],bytes.fromhex(res_h[2:]))
            print(" reserves:",r0,r1)
            q_h=call(url,ROUTER,"0x"+sel("getAmountsOut(uint256,address[])")+encode(["uint256","address[]"],[177600000000000,[YYDS,WBNB]]).hex())
            print(" quote raw:",q_h)
            if q_h:
                outs=decode(["uint256[]"],bytes.fromhex(q_h[2:]))[0]
                print(" quote BNB:",outs[1]/1e18)
        break
for url in ["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.defibit.io/"]:
    lh=call(url,KAGENT_SALE,"0x"+sel("launched()"))
    print(url,"KAGENT launched raw:",lh)
    if lh is not None:
        print(" launched:",decode(["bool"],bytes.fromhex(lh[2:]))[0]); break
