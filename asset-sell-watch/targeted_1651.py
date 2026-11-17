import json, urllib.request
from eth_abi import encode, decode
from eth_utils import keccak
W="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ROUTER="0x10ED43C718714eb63d5aA57B78B54704E256024E"
FACTORY="0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB="0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
BAY="0x397BF425926F521Ac5BEbe5062793BB224e3eF8f"   # 币安加油
KAGENT="0xb34105002B19EF0ce43B59011fE848df5c8B174f"
URLS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.defibit.io/","https://bsc-dataseed1.binance.org/","https://bsc-dataseed2.binance.org/"]
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
# 币安加油: balance + pair + reserves
for url in URLS:
    bal_h=call(url,BAY,"0x"+sel("balanceOf(address)")+encode(["address"],[W]).hex())
    if bal_h is not None:
        out["bay_balance_raw"]=str(u256(bal_h)); out["bay_balance_url"]=url
        pair_h=call(url,FACTORY,"0x"+sel("getPair(address,address)")+encode(["address","address"],[BAY,WBNB]).hex())
        pair=("0x"+pair_h[-40:]) if pair_h and u256(pair_h) else None
        out["bay_pair"]=pair; out["bay_pair_url"]=url
        if pair:
            res_h=call(url,pair,"0x"+sel("getReserves()"))
            if res_h:
                r0,r1,_=decode(["uint112","uint112","uint32"],bytes.fromhex(res_h[2:]))
                out["bay_reserves"]=[str(r0),str(r1)]
        break
# KAGENT: pair + reserves + quote + launched
for url in URLS:
    pair_h=call(url,FACTORY,"0x"+sel("getPair(address,address)")+encode(["address","address"],[KAGENT,WBNB]).hex())
    pair=("0x"+pair_h[-40:]) if pair_h and u256(pair_h) else None
    if pair:
        out["kagent_pair"]=pair; out["kagent_pair_url"]=url
        res_h=call(url,pair,"0x"+sel("getReserves()"))
        if res_h:
            r0,r1,_=decode(["uint112","uint112","uint32"],bytes.fromhex(res_h[2:]))
            out["kagent_reserves"]=[str(r0),str(r1)]
            if r0 and r1:
                q_h=call(url,ROUTER,"0x"+sel("getAmountsOut(uint256,address[])")+encode(["uint256","address[]"],[50000000000000000000000,[KAGENT,WBNB]]).hex())
                if q_h:
                    outs=decode(["uint256[]"],bytes.fromhex(q_h[2:]))[0]
                    out["kagent_quote_bnb"]=outs[1]/1e18
        lh=call(url,KAGENT,"0x"+sel("launched()"))
        if lh is not None:
            out["kagent_launched"]=decode(["bool"],bytes.fromhex(lh[2:]))[0]
            out["kagent_launched_url"]=url
        break
print(json.dumps(out,indent=1,ensure_ascii=False))
