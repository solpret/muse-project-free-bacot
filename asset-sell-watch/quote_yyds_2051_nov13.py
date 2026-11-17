#!/usr/bin/env python3
import json
from pending_check_2051_nov13 import rpc_batch, sel
from eth_abi import encode, decode
ROUTER="0x10ED43C718714eb63d5aA57B78B54704E256024E"
WBNB="0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
TOK="0xd23be069c3c3a7f631af52584a16a9e46bb41da1"
amt=177600000000000
calls=[("eth_call",[{"to":ROUTER,"data":"0x"+sel("getAmountsOut(uint256,address[])")+encode(["uint256","address[]"],[amt,[TOK,WBNB]]).hex()},"latest"])]
res,err=rpc_batch(calls,timeout=15)
out={"error":err}
if res[0]:
    try:
        outs=decode(["uint256[]"],bytes.fromhex(res[0][2:]))[0]
        out["quote_bnb"]=outs[1]/1e18
    except Exception as ex:
        out["quote_error"]=str(ex)
print(json.dumps(out))
