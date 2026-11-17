#!/usr/bin/env python3
import json, urllib.request
from eth_abi import encode, decode
from eth_utils import keccak
ROUTER = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
def sel(sig): return keccak(text=sig).hex()[:8]
def call(to, data, url):
    batch = [{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}]
    req = urllib.request.Request(url, data=json.dumps(batch).encode(), headers={"Content-Type":"application/json"})
    try:
        res = json.loads(urllib.request.urlopen(req, timeout=30).read())
    except Exception as e:
        return None, str(e)
    if isinstance(res, list): res = res[0] if res else {}
    if isinstance(res, dict) and (res.get("error") or not res.get("result")):
        return None, str(res.get("error"))
    return (res.get("result") if isinstance(res, dict) else None), None
tok2 = "0xd23be069c3c3a7f631af52584a16a9e46bb41da1"
tok3 = "0xb34105002B19EF0ce43B59011fE848df5c8B174f"
out = {}
for url in ["https://bsc-dataseed1.binance.org/", "https://bsc-dataseed1.defibit.io/"]:
    qh, err = call(ROUTER, "0x"+sel("getAmountsOut(uint256,address[])")+encode(["uint256","address[]"],[177600000000000,[tok2,WBNB]]).hex(), url)
    if qh:
        outs = decode(["uint256[]"], bytes.fromhex(qh[2:]))[0]
        out["yyds_quote_bnb"] = outs[1]/1e18; out["yyds_quote_via"] = url; break
    out["yyds_quote_err_"+url.split("/")[2]] = err
for url in ["https://bsc-dataseed1.binance.org/", "https://bsc-dataseed1.defibit.io/"]:
    lh, err = call(tok3, "0x"+sel("launched()"), url)
    if lh is not None:
        try: out["kagent_launched"] = decode(["bool"], bytes.fromhex(lh[2:]))[0]
        except Exception: out["kagent_launched"] = "decode_fail"
        out["kagent_launched_via"] = url; break
    out["kagent_launched_err_"+url.split("/")[2]] = err
print(json.dumps(out, indent=1))
